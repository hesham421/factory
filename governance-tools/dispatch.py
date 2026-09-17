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
import contracts as contracts_mod
from toolkit.common import rel
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
    # shallow copy so `factory.paths.*` in ENGINE.md resolves {profile_id}, same as render.py._ctx
    factory_data = dict(CFG.data, paths=CFG.paths)
    ctx = dict(profile=CFG.profile.data, factory=factory_data, stage=stage, mod=mod.upper(), version=version, **extra)
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
    cs = contracts_mod.contracts_from_doc(CFG)
    return [c for c in cs if stage.id in (c["owner"] if isinstance(c["owner"], list) else [c["owner"]]) or c["consumer"] == stage.id]


def build_brief(stage: Stage, mod: str, version: int, *, round_no: int = 1, implementer: Implementer | None = None,
                previous: Path | None = None) -> Path:
    lane = CFG.lane(stage.lane)
    dialogue = lane.get("dialogue") if stage.dialogue else None
    outputs = []
    for a in stage.produces:
        p = CFG.artifact_path(mod, stage.id, a.artifact, version)
        outputs.append(f"- `{rel(p)}`{' (registry)' if a.registry else ''}{' (optional)' if a.optional else ''}")
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
            head += ["", f"## Previous round", f"(see `{rel(previous)}` — appended below)"]
    contracts = _contracts_for(stage)
    if contracts:
        head += ["", "## Contracts checked by `gov.py analyze` after this stage"]
        for c in contracts:
            head += [f"- **{c['id']}** {c['title']}: " + "; ".join(f"{cl['id']} {cl['check']} {cl.get('args', {})} [{contracts_mod.clause_severity(CFG, cl)}]" for cl in c.get("clauses", []))]
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


# ── multi-module / project briefs (additive — single-module build_brief() is
#    untouched, so a plain `--module MOD` run stays byte-identical) ───────────

def build_brief_scoped(stage: Stage, mods: list[str], versions: dict[str, int], scope: str) -> Path:
    """One combined brief for a `--modules A,B,...` or `--scope project` test-gen
    run: the ENGINE.md body is rendered ONCE with `scope`/`mods` context, inputs
    are bundled per selected module, and every module's own output files are
    listed (plus the platform-level `system-test-index` at `scope: project`)."""
    lane = CFG.lane(stage.lane)
    outputs = []
    for m in mods:
        for a in stage.produces:
            if a.artifact == "system-test-index":
                continue
            p = CFG.artifact_path(m, stage.id, a.artifact, versions[m])
            outputs.append(f"- `{rel(p)}`{' (optional)' if a.optional else ''}")
    if scope == "project":
        p = CFG.artifact_path(mods[0], stage.id, "system-test-index", versions[mods[0]])
        outputs.append(f"- `{rel(p)}` (platform-level, optional)")
    head = [
        f"# BRIEF — stage `{stage.id}` ({stage.title}) · scope `{scope}` · modules {', '.join(mods)} · profile `{CFG.profile_id}`",
        "",
        f"Lane `{stage.lane}` · implementers {lane.get('implementers')} · effort {lane.get('effort')}",
        "",
        "## Rules that bind this run",
        f"- Questions: **{stage.questions}**. A `[QUESTION]` block is refused. Ambiguity → ADR per affected module in "
        f"`{CFG.paths['decisions']}/<MOD>/` (`{CFG.naming['adr_file']}`): non-breaking → continue; breaking → status BLOCKED and stop.",
        f"- Owns IDs: {', '.join(stage.owns_ids)} — ID grammar `{CFG.ids['pattern']}` (seq width {CFG.ids['seq_width']}); never re-number, never restart a "
        f"sequence; an integration TC is owned by the DECLARING module (XM) or the DISPLAYING module (UXD), never the target/owner module.",
        f"- Read only what this brief contains (generated current state, EACH module below); never open version folders yourself.",
        f"- Write exactly these files (complete files):",
        *outputs,
        "- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; "
        "when running as the operator, write the files directly.",
    ]
    body = render_engine(stage, mods[0], versions[mods[0]], scope=scope, mods=mods)
    parts = ["\n".join(head), "", "---", "# ENGINE", body]
    for m in mods:
        parts += ["", "---", f"# INPUTS — module {m} (generated current state)"]
        for label, text in _state_bundle(stage, m, versions[m]):
            parts += [f"\n<<<INPUT: {label} ({m})>>>", text, "<<<END INPUT>>>"]
    kn = _knowledge(stage)
    if kn:
        parts += ["", "---", "# KNOWLEDGE (profile primary sources — cite as [KB:<file> §n])"]
        for label, text in kn:
            parts += [f"\n<<<KB: {label}>>>", text, "<<<END KB>>>"]
    bdir = CFG.state_dir(mods[0], versions[mods[0]]) / "briefs"
    bdir.mkdir(parents=True, exist_ok=True)
    tag = "project" if scope == "project" else "-".join(mods)
    path = bdir / f"{stage.id}-{tag}.md"
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return path


def dispatch_scoped(stage: Stage, mods: list[str], versions: dict[str, int], scope: str) -> DispatchResult:
    """Dispatch a scoped (multi-module / project) test-gen brief. Manual runner
    only for now — a `cmd`/`fake` runner may be wired the same way build_brief()
    already is, once a delegate needs it; the orchestrator's contract (AWAITING
    until the brief is executed) is identical either way."""
    lane = CFG.lane(stage.lane)
    brief = build_brief_scoped(stage, mods, versions, scope)
    res = DispatchResult(stage.id, stage.lane, brief)
    if runner_kind() == "manual" or not lane.get("implementers"):
        res.awaiting = True
        return res
    impl = Implementer.parse(lane["implementers"][0])
    resp = run_round(brief, impl, lane.get("effort", "high"), 1, lane_id=stage.lane, read_only=bool(lane.get("read_only")))
    res.rounds = 1
    if resp is not None:
        res.responses.append(resp)
        res.converged = True
        res.written = ingest(resp)
    return res


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
        # {lane} is the factory.yaml lane id (e.g. "analysis", "review-per-engine") — the same
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


def write_roots() -> list[Path]:
    """Where a response may write: this repo, and the checkout that owns the
    external path keys (`paths.external`) — the content root.

    The content root used to be assumed to sit INSIDE this repo (the submodule
    layout), so a relative block path was joined to `CFG.root` and the escape
    check knew one root. Point `GOV_SHARED_CHECKOUT` anywhere else and every
    automated stage write failed: the brief carried absolute paths (`rel()`
    falls back to them outside the root) and the check refused each one."""
    roots = [CFG.root.resolve()]
    ext = CFG.external
    if ext.get("keys"):
        shared = CFG.repo_checkout(ext["repo"]).resolve()
        if shared not in roots:
            roots.append(shared)
    return roots


def _content_prefixes() -> list[str]:
    """The first path segment of every external key's declared path — how a
    relative block path says which root it means."""
    out = []
    for key in (CFG.external.get("keys") or ()):
        v = CFG.paths.get(key)
        if isinstance(v, str) and v:
            out.append(Path(v).parts[0])
    return out


def resolve_target(rel: str) -> Path:
    """A `<<<FILE:>>>` path → the file it names, inside one of `write_roots()`.

    Absolute paths are taken as given. A relative path resolves against this
    repo, unless its first segment is one of the content root's declared
    top-level folders (`paths.<external key>`) and the content root is not
    nested here — then it resolves against the content root. Anything that
    lands outside every allowed root is refused."""
    p = Path(rel)
    roots = write_roots()
    if p.is_absolute():
        target = p.resolve()
    else:
        target = (roots[0] / p).resolve()
        if len(roots) > 1 and p.parts and p.parts[0] in _content_prefixes() and not (roots[0] / p).exists():
            target = (roots[1] / p).resolve()
    if not any(target == r or r in target.parents for r in roots):
        raise ValueError(f"response tries to write outside the factory and the content root: {rel}")
    return target


def ingest(response: Path) -> list[Path]:
    """Write every <<<FILE: path>>> block of a response into the repo that owns
    the path (`resolve_target`: this repo or the content root, never elsewhere).

    A block NEVER overwrites a file written after the response that carries it.
    The runner contract asks for file blocks, but the runners actually dispatched
    to are agents holding write tools, and one of them may save the artifact
    itself — this run's P0.5 said so in as many words ("written to …/prd-note.md
    (as operator, not a file block)"). Replaying an older round's block over that
    would substitute a superseded draft for the delivered artifact, silently.
    A response cannot supersede a write that happened after it.
    """
    written = []
    text = response.read_text(encoding="utf-8")
    cutoff = response.stat().st_mtime
    for m in _FILE_BLOCK.finditer(text):
        rel = m.group("path").strip()
        target = resolve_target(rel)
        body = m.group("body").rstrip("\n") + "\n"
        if target.exists() and target.stat().st_mtime > cutoff and target.read_text(encoding="utf-8") != body:
            continue                      # written out of band, after this response
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
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
    # Dialogue stages (domain-profile, P0, P0.5) name the plain `analysis` lane, not a
    # distinct "analysis-dialogue" id: the real delegate setup this dispatches to has no
    # such lane. `impls` therefore usually has one entry, so every round below re-dispatches
    # the same lane/implementer — the rounds differ by the brief's framing (draft → self-
    # review, see build_brief()'s "Dialogue protocol" section), not by which model answers.
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
    # Ingest EVERY round, oldest first, so a later round overwrites a file it
    # re-emits and a file emitted once survives the rounds that do not mention
    # it. Only `previous` used to be ingested, which silently discarded every
    # earlier round's blocks — and the shape that triggers it is the NORMAL one
    # for a dialogue stage: the last round is a self-review that argues about
    # the artifact instead of re-emitting it. P0.5 of this run did exactly that
    # (round 1 carried the PRD, round 2 carried only `<!-- CONVERGED -->`), and
    # the artifact survived solely because the runner happened to be an agent
    # with write access that had saved it itself — which the documented runner
    # contract does not promise.
    for resp in res.responses:
        for path in ingest(resp):
            if path not in res.written:
                res.written.append(path)
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
                out.append((rel(p), ln))
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
