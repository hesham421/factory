"""
dispatch — briefs, lanes, implementers, dialogue (GOVERNANCE-CORE.md §6–§7)
==========================================================================
A stage never runs "by hand": the orchestrator builds a self-contained BRIEF
(the stage's ENGINE.md template rendered with profile + factory + stage +
the `_state/` files) and hands it to the stage's LANE (`factory.lanes`): a
list of implementers `provider:model`, an effort, and — for dialogue lanes —
a converging protocol between the implementers.

Runners (how a brief reaches a model) are pluggable and chosen by env:
  GOV_RUNNER=cmd      (default) run GOV_RUNNER_CMD once per round with
                      placeholders {brief} {implementer} {provider} {model}
                      {effort} {out} {lane} {read_only_flag}; the response may
                      carry file blocks (see ingest()). {lane} is the
                      factory.yaml lane id — a lane-name-matching delegate CLI
                      (e.g. `claude-delegate --lane {lane} {read_only_flag}`)
                      needs nothing else: its own config maps that same lane
                      id to a Claude model/effort/readonly, so GOV_RUNNER_CMD
                      can be one line with no per-implementer model mapping to
                      keep in sync. Example:
                        GOV_RUNNER_CMD='node claude-delegate/relay.mjs
                        --lane {lane} {read_only_flag} --brief {brief}
                        --out {out}'
  GOV_RUNNER=manual   write the brief, stop with exit code 2 and an ACTION
                      block; the operator (Claude Code + delegate skills)
                      executes it and calls the command again with
                      --complete once the artifacts exist.
  GOV_RUNNER=fake     tests: a python callable registered via set_fake().
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import jinja2

from config import CFG, Stage
import idmodel
import render
import state as st_mod

CONVERGED = "<!-- CONVERGED -->"
_FILE_BLOCK = re.compile(r"<<<FILE:\s*(?P<path>[^>]+?)\s*>>>\n(?P<body>.*?)\n<<<END FILE>>>", re.S)


@dataclass
class Implementer:
    provider: str
    model: str

    @classmethod
    def parse(cls, s: str) -> "Implementer":
        p, _, m = s.partition(":")
        return cls(p, m or "default")

    def __str__(self) -> str:
        return f"{self.provider}:{self.model}"


@dataclass
class DispatchResult:
    stage: str
    lane: str
    brief: Path
    rounds: int = 0
    converged: bool = False
    responses: list[Path] = field(default_factory=list)
    written: list[Path] = field(default_factory=list)
    awaiting: bool = False        # manual runner: operator must act


# ── brief ───────────────────────────────────────────────────────────────────

def _engine_template(stage: Stage) -> Path:
    base = CFG.dir("standalone") if stage.standalone else CFG.dir("engines")
    return base / stage.id / "references" / "ENGINE.md"


def render_engine(stage: Stage, mod: str, version: int, **extra) -> str:
    tpl = _engine_template(stage)
    env = jinja2.Environment(undefined=jinja2.ChainableUndefined, keep_trailing_newline=True)
    ctx = dict(profile=CFG.profile.data, factory=CFG.data, stage=stage, mod=mod.upper(), version=version, **extra)
    return env.from_string(tpl.read_text(encoding="utf-8")).render(**ctx)


def _state_bundle(stage: Stage, mod: str, version: int) -> list[tuple[str, str]]:
    """(label, content) for every input the stage names, read from _state/ or _inputs/."""
    out = []
    for inp in stage.inputs:
        name = inp.rstrip("?")
        optional = inp.endswith("?")
        text = None
        if name in CFG.inputs:
            spec = CFG.inputs[name]
            p = CFG.inputs_dir(mod, version) / CFG.fmt(spec["file"], mod=mod)
            text = p.read_text(encoding="utf-8") if p.exists() else None
        else:
            text = st_mod.state_text(mod, version, name)
        if text is None:
            if not optional:
                out.append((name, "(MISSING — the orchestrator refuses to run this stage until it exists)"))
            continue
        out.append((name, text))
    return out


def _knowledge(stage: Stage) -> list[tuple[str, str]]:
    out = []
    for f in CFG.profile.knowledge_files:
        p = CFG.root / f
        if p.exists():
            out.append((f, p.read_text(encoding="utf-8")))
    return out


def _contracts_for(stage: Stage) -> list[dict]:
    cs = render.contracts_from_doc(CFG)
    return [c for c in cs if stage.id in (c["owner"] if isinstance(c["owner"], list) else [c["owner"]]) or c["consumer"] == stage.id]


def build_brief(stage: Stage, mod: str, version: int, *, round_no: int = 1, implementer: Implementer | None = None,
                previous: Path | None = None) -> Path:
    lane = CFG.lane(stage.lane)
    dialogue = lane.get("dialogue") if stage.dialogue else None
    outputs = []
    for a in stage.produces:
        p = CFG.artifact_path(mod, stage.id, a.artifact, version)
        outputs.append(f"- `{p.relative_to(CFG.root)}`{' (registry)' if a.registry else ''}{' (optional)' if a.optional else ''}")
    head = [
        f"# BRIEF — stage `{stage.id}` ({stage.title}) · module {mod.upper()} · v{version} · profile `{CFG.profile_id}`",
        "",
        f"Lane `{stage.lane}` · implementer {implementer or lane.get('implementers')} · effort {lane.get('effort')} · round {round_no}",
        "",
        "## Rules that bind this run",
        f"- Questions: **{stage.questions}**." + (
            " Close every open point inside this dialogue with a researched, recommended answer; never write an external open-questions file."
            if stage.questions == "allowed" else
            f" A `[QUESTION]` block is refused. Ambiguity → ADR in `{CFG.paths['decisions']}/{mod.upper()}/` "
            f"(`{CFG.naming['adr_file']}`): non-breaking → continue; breaking → status BLOCKED and stop."),
        f"- Owns IDs: {', '.join(stage.owns_ids) or 'none'} — ID grammar `{CFG.ids['pattern']}` (seq width {CFG.ids['seq_width']}); never re-number, never restart a sequence.",
        f"- Read only what this brief contains (generated current state); never open version folders yourself.",
        f"- Write exactly these files (complete files; in a delta version only what changed, plus `{CFG.paths['module']['change_manifest']}`):",
        *outputs,
        "- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; when running as the operator, write the files directly.",
    ]
    if dialogue:
        impls = ", ".join(lane.get("implementers", []))
        head += [
            "",
            "## Dialogue protocol (converging, in-brief)",
            f"Implementers {impls} alternate for at most {dialogue['max_rounds']} rounds; converge on **{dialogue['converge_on']}**.",
            "Round 1 drafts the artifacts and, for every open point, a `PROPOSAL:` block (options, researched recommendation, sources).",
            "Each later round answers every open PROPOSAL (accept / amend with reason), refines the artifacts, and appends "
            f"`{CONVERGED}` at the end of the response when nothing material remains open. The last response is final.",
        ]
        if previous is not None:
            head += ["", f"## Previous round", f"(see `{previous.relative_to(CFG.root)}` — appended below)"]
    contracts = _contracts_for(stage)
    if contracts:
        head += ["", "## Contracts checked by `gov.py analyze` after this stage"]
        for c in contracts:
            head += [f"- **{c['id']}** {c['title']}: " + "; ".join(f"{cl['id']} {cl['check']} {cl.get('args', {})} [{cl['severity']}]" for cl in c.get("clauses", []))]
    body = render_engine(stage, mod, version)
    parts = ["\n".join(head), "", "---", "# ENGINE", body, "", "---", "# INPUTS (generated current state)"]
    for label, text in _state_bundle(stage, mod, version):
        parts += [f"\n<<<INPUT: {label}>>>", text, "<<<END INPUT>>>"]
    kn = _knowledge(stage)
    if kn:
        parts += ["", "---", "# KNOWLEDGE (profile primary sources — cite as [KB:<file> §n])"]
        for label, text in kn:
            parts += [f"\n<<<KB: {label}>>>", text, "<<<END KB>>>"]
    if previous is not None:
        parts += ["", "---", "# PREVIOUS ROUND", previous.read_text(encoding="utf-8")]
    bdir = CFG.state_dir(mod, version) / "briefs"
    bdir.mkdir(parents=True, exist_ok=True)
    path = bdir / (f"{stage.id}.md" if round_no == 1 else f"{stage.id}-round{round_no}.md")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return path


# ── runners ─────────────────────────────────────────────────────────────────

_FAKE: Callable[[Path, Implementer, str, int], str] | None = None


def set_fake(fn: Callable[[Path, Implementer, str, int], str] | None) -> None:
    global _FAKE
    _FAKE = fn


def runner_kind() -> str:
    return os.environ.get("GOV_RUNNER", "cmd")


def run_round(brief: Path, impl: Implementer, effort: str, round_no: int, *,
              lane_id: str = "", read_only: bool = False) -> Path | None:
    kind = runner_kind()
    out = brief.with_name(brief.stem + f".response{round_no}.md")
    if kind == "fake":
        if _FAKE is None:
            raise RuntimeError("GOV_RUNNER=fake but no fake runner registered")
        out.write_text(_FAKE(brief, impl, effort, round_no), encoding="utf-8")
        return out
    if kind == "cmd":
        tpl = os.environ.get("GOV_RUNNER_CMD")
        if not tpl:
            raise RuntimeError("GOV_RUNNER=cmd requires GOV_RUNNER_CMD")
        # {lane} is the factory.yaml lane id (e.g. "analysis", "review-pass") — the same
        # string a lane-name-matching delegate tool (e.g. `claude-delegate --lane <id>`)
        # keys its own model/effort/readonly config by, so no model/effort mapping needs
        # to be duplicated here. {read_only_flag} is "--read-only" when the lane sets
        # `read_only: true`, else "" — safe to reference or ignore in the template.
        cmd = tpl.format(brief=shlex.quote(str(brief)), implementer=impl, provider=impl.provider, model=impl.model,
                         effort=effort, out=shlex.quote(str(out)), lane=lane_id,
                         read_only_flag=("--read-only" if read_only else ""))
        subprocess.run(cmd, shell=True, check=True)
        return out if out.exists() else None
    return None   # manual


def ingest(response: Path) -> list[Path]:
    """Write every <<<FILE: path>>> block of a response into the repo (path must stay inside the repo)."""
    written = []
    text = response.read_text(encoding="utf-8")
    for m in _FILE_BLOCK.finditer(text):
        rel = m.group("path").strip()
        target = (CFG.root / rel).resolve()
        if CFG.root not in target.parents and target != CFG.root:
            raise ValueError(f"response tries to write outside the repo: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(m.group("body").rstrip("\n") + "\n", encoding="utf-8")
        written.append(target)
    return written


def dispatch(stage: Stage, mod: str, version: int) -> DispatchResult:
    lane = CFG.lane(stage.lane)
    impls = [Implementer.parse(s) for s in lane.get("implementers", [])]
    res = DispatchResult(stage.id, stage.lane, build_brief(stage, mod, version, implementer=impls[0] if impls else None))
    if runner_kind() == "manual" or not impls:
        res.awaiting = True
        return res
    max_rounds = int(lane["dialogue"]["max_rounds"]) if (stage.dialogue and lane.get("dialogue")) else 1
    previous: Path | None = None
    for r in range(1, max_rounds + 1):
        impl = impls[(r - 1) % len(impls)]
        brief = res.brief if r == 1 else build_brief(stage, mod, version, round_no=r, implementer=impl, previous=previous)
        resp = run_round(brief, impl, lane.get("effort", "high"), r,
                         lane_id=stage.lane, read_only=bool(lane.get("read_only")))
        res.rounds = r
        if resp is None:
            break
        res.responses.append(resp)
        previous = resp
        if max_rounds == 1 or CONVERGED in resp.read_text(encoding="utf-8"):
            res.converged = True
            break
    if previous is not None:
        res.written = ingest(previous)
    return res


# ── question policy ─────────────────────────────────────────────────────────

def refused_questions(stage: Stage, mod: str, version: int) -> list[tuple[str, int]]:
    """[QUESTION] blocks found in a questions-forbidden stage's outputs."""
    if stage.questions != "forbidden":
        return []
    out = []
    for a in stage.produces:
        p = CFG.artifact_path(mod, stage.id, a.artifact, version)
        if p.exists():
            for ln in idmodel.questions(p.read_text(encoding="utf-8")):
                out.append((str(p.relative_to(CFG.root)), ln))
    return out


def blocked_adrs(mod: str, version: int) -> list[Path]:
    d = CFG.decisions_dir(mod)
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.md")):
        t = p.read_text(encoding="utf-8")
        if re.search(r"^\s*Status\s*:\s*BLOCKED", t, re.M) and re.search(rf"Version\s*:\s*v{version}\b", t):
            out.append(p)
    return out
