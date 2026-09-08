"""
gov.py render — every generated file comes from factory.yaml + the profile (C1)
===============================================================================
Generates (whole files, carrying the generated marker):
    engines/<id>/SKILL.md            standalone/<id>/SKILL.md
    .claude/commands/<id>.md         README.md            shared/START-HERE.md
Fills RENDER blocks inside hand-written docs:
    <!-- RENDER:<name> --> … <!-- /RENDER:<name> -->
Block names: stages · standalone · gates · lanes · ids · ears · markers ·
phases:<track>:<plan> · commands · review-rubric · profile-summary · contracts-index

`check_fresh(cfg)` renders to memory and compares with disk — lint uses it.
"""
from __future__ import annotations

import re
from pathlib import Path

import jinja2
import yaml

from config import CFG, FactoryConfig, Stage

_TEMPLATES = ("SKILL.md.j2", "command.md.j2", "README.md.j2", "START-HERE.md.j2")
_RENDER_RX = re.compile(r"(<!-- RENDER:([A-Za-z0-9_:-]+) -->)(.*?)(<!-- /RENDER:\2 -->)", re.S)
_FRONTMATTER_RX = re.compile(r"^---\n(.*?)\n---\n", re.S)


def _env(cfg: FactoryConfig) -> jinja2.Environment:
    loader = jinja2.FileSystemLoader(str(cfg.root / cfg.paths["templates"]))
    env = jinja2.Environment(loader=loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    env.filters["join_ids"] = lambda xs: ", ".join(f"`{x}`" for x in xs) if xs else "—"
    return env


def _ctx(cfg: FactoryConfig, **extra) -> dict:
    return dict(
        factory=cfg.data, profile=cfg.profile.data, cfg=cfg,
        stages=cfg.stages, standalone=cfg.standalone, marker=cfg.data["lint"]["generated_marker"],
        **extra,
    )


# ═══════════════════════════════════════════════════════════════════════════
# RENDER blocks
# ═══════════════════════════════════════════════════════════════════════════

def _t(rows: list[list[str]], header: list[str]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def _ids_list(xs) -> str:
    return ", ".join(f"`{x}`" for x in xs) if xs else "—"


def _stage_row(s: Stage, cfg: FactoryConfig) -> list[str]:
    gate = cfg.gate_after(s.id)
    return [f"`{s.id}`", s.title, s.pass_, s.questions + (" (dialogue)" if s.dialogue else ""),
            f"`{s.lane}`", _ids_list(s.inputs), ", ".join(f"`{a.file}`" for a in s.produces),
            _ids_list(s.owns_ids), f"gate `{gate['id']}`" if gate else (s.next or "—")]


def block_stages(cfg): return _t([_stage_row(s, cfg) for s in cfg.stages],
                                 ["Stage", "Title", "Pass", "Questions", "Lane", "Inputs", "Produces", "Owns IDs", "Then"])


def block_standalone(cfg): return _t([_stage_row(s, cfg)[:8] for s in cfg.standalone],
                                     ["Stage", "Title", "Pass", "Questions", "Lane", "Inputs", "Produces", "Owns IDs"])


def block_gates(cfg):
    rows = []
    for g in cfg.gates:
        rows.append([f"`{g['id']}`", f"after `{g['after']}`", g["type"], f"`{g.get('lane','—')}`",
                     g.get("requires_analyze", "—"), f"`{g.get('on_revise','—')}`"])
    return _t(rows, ["Gate", "When", "Type", "Lane", "Requires analyze", "On REVISE"])


def block_lanes(cfg):
    rows = []
    for k, v in cfg.lanes.items():
        d = v.get("dialogue")
        rows.append([f"`{k}`", ", ".join(f"`{i}`" for i in v.get("implementers", [])) or "tools only",
                     v.get("effort", "—"), "read-only" if v.get("read_only") else "—",
                     f"max {d['max_rounds']} rounds, converge on *{d['converge_on']}*" if d else "—"])
    return _t(rows, ["Lane", "Implementers", "Effort", "Mode", "Dialogue"])


def block_ids(cfg):
    rows = []
    for k, v in cfg.id_atoms().items():
        rows.append([f"`{k}`", v.get("title", ""), f"`{v.get('owner','')}`", _ids_list(v.get("traces_to", [])), _ids_list(v.get("requires", []))])
    return (f"Pattern `{cfg.ids['pattern']}`, sequence width {cfg.ids['seq_width']}.\n\n"
            + _t(rows, ["Atom", "Meaning", "Owner", "Traces to", "Requires"]))


def block_ears(cfg):
    return _t([[k, f"`{v}`"] for k, v in cfg.ids["ears"]["patterns"].items()], ["Pattern", "Statement regex"])


def block_markers(cfg):
    m = cfg.markers
    rows = []
    for k, v in m["kinds"].items():
        scope = []
        if v.get("tracks"): scope.append("tracks: " + "/".join(v["tracks"]))
        if v.get("plans"): scope.append("plans: " + "/".join(v["plans"]))
        rows.append([f"`{k}`", v["level"], _ids_list(v.get("allowed_parents", [])) if v.get("allowed_parents") else "top level",
                     f"atom `{v['atom']}`" if v.get("atom") else ("keys from profile" if v.get("keys_from") else "phase-qualified label"),
                     ", ".join(scope) or "all"])
    head = (f"Schema version **{m['schema_version']}**, syntax `{m['syntax']}`, attributes {_ids_list(m['attributes'])}.\n\n")
    return head + _t(rows, ["Kind", "Level", "Allowed parents", "Identity", "Scope"])


def block_phases(cfg, track: str, plan: str):
    prof = cfg.profile
    if track not in prof.tracks or plan not in prof.plans(track):
        return f"_(profile `{prof.id}` declares no `{plan}` plan for track `{track}`)_"
    rows = []
    for p in prof.phases(track, plan):
        thr = p.split_threshold
        rows.append([f"`{p.key}`", p.display, f"`{p.folder}`",
                     "never" if p.never_split else (f"{thr['kind']} {thr['op']} {thr['count']}" + (f" ({thr.get('grouping')})" if thr and thr.get("grouping") else "")) if thr else ("per screen" if p.sub_bearing else "—"),
                     _ids_list(p.sub_labels)])
    return _t(rows, ["Key", "Display", "Folder", "Split when", "SUB labels"])


def block_commands(cfg):
    return _t([[f"`/{c['id']} {c.get('args','')}`".strip(), f"`gov.py {c['runs']}`"] for c in cfg.commands], ["Command", "Runs"])


def block_review_rubric(cfg):
    r = cfg.review
    return (f"Scale {r['scale']['min']}–{r['scale']['max']}; every attribute must score ≥ {r['pass_threshold']} to APPROVE; "
            f"verdicts {_ids_list(r['verdicts'])}; at most {r['revise_max']} REVISE per finding before ESCALATE.\n\n"
            + "\n".join(f"- `{a}`" for a in r["rubric"]))


def block_profile_summary(cfg):
    p = cfg.profile
    langs = p.languages
    return _t([
        ["Profile", f"`{p.id}` — {p.data['identity']['display']}"],
        ["Languages", ", ".join(langs["all"]) + (f" (all required, primary {langs['primary']})" if langs.get("require_all") else f" (primary {langs['primary']})")],
        ["Modules", ", ".join(f"`{k}`" for k in p.vocabulary["module_prefixes"])],
        ["Entity kinds", ", ".join(p.vocabulary["entity_kinds"])],
        ["Backend plans", ", ".join(p.plans("backend"))], ["Frontend plans", ", ".join(p.plans("frontend"))],
        ["Knowledge", ", ".join(f"`{f}`" for f in p.knowledge_files) or "—"],
    ], ["Fact", "Value"])


def contracts_from_doc(cfg: FactoryConfig) -> list[dict]:
    path = cfg.dir("shared") / "ARTIFACT-CONTRACTS.md"
    if not path.exists():
        return []
    m = _FRONTMATTER_RX.match(path.read_text(encoding="utf-8"))
    return (yaml.safe_load(m.group(1)) or {}).get("contracts", []) if m else []


def block_contracts_index(cfg):
    rows = []
    for c in contracts_from_doc(cfg):
        owner = c["owner"] if isinstance(c["owner"], str) else "+".join(c["owner"])
        rows.append([f"`{c['id']}`", c["title"], f"`{owner}`", f"`{c['consumer']}`", _ids_list(c.get("artifacts", [])), len(c.get("clauses", []))])
    return _t(rows, ["Contract", "Interface", "Owner", "Consumer", "Artifacts", "Clauses"])


def render_block(cfg: FactoryConfig, name: str) -> str:
    if name.startswith("phases:"):
        _, track, plan = name.split(":")
        return block_phases(cfg, track, plan)
    fn = {
        "stages": block_stages, "standalone": block_standalone, "gates": block_gates, "lanes": block_lanes,
        "ids": block_ids, "ears": block_ears, "markers": block_markers, "commands": block_commands,
        "review-rubric": block_review_rubric, "profile-summary": block_profile_summary,
        "contracts-index": block_contracts_index,
    }.get(name)
    if fn is None:
        raise KeyError(f"unknown RENDER block '{name}'")
    return fn(cfg)


def fill_blocks(cfg: FactoryConfig, text: str) -> str:
    def repl(m: re.Match) -> str:
        body = render_block(cfg, m.group(2))
        return f"{m.group(1)}\n{body}\n{m.group(4)}"
    return _RENDER_RX.sub(repl, text)


# ═══════════════════════════════════════════════════════════════════════════
# Whole generated files
# ═══════════════════════════════════════════════════════════════════════════

def _shared_docs(cfg: FactoryConfig) -> list[str]:
    return sorted(p.name for p in cfg.dir("shared").glob("*.md") if p.name != "START-HERE.md")


def generated_files(cfg: FactoryConfig) -> dict[Path, str]:
    """path → content for every whole-file generation target."""
    env = _env(cfg)
    out: dict[Path, str] = {}
    skill = env.get_template("SKILL.md.j2")
    for s in cfg.stages:
        out[cfg.dir("engines") / s.id / "SKILL.md"] = skill.render(_ctx(cfg, stage=s, kind="engine", shared_docs=_shared_docs(cfg)))
    for s in cfg.standalone:
        out[cfg.dir("standalone") / s.id / "SKILL.md"] = skill.render(_ctx(cfg, stage=s, kind="standalone", shared_docs=_shared_docs(cfg)))
    cmd = env.get_template("command.md.j2")
    for c in cfg.commands:
        out[cfg.dir("commands") / f"{c['id']}.md"] = cmd.render(_ctx(cfg, command=c))
    out[cfg.root / "README.md"] = env.get_template("README.md.j2").render(_ctx(cfg, shared_docs=_shared_docs(cfg)))
    out[cfg.dir("shared") / "START-HERE.md"] = env.get_template("START-HERE.md.j2").render(_ctx(cfg))
    return {p: fill_blocks(cfg, c) for p, c in out.items()}   # generated files may embed RENDER blocks too


def block_files(cfg: FactoryConfig) -> dict[Path, str]:
    """path → filled content for every hand-written file that contains RENDER blocks."""
    out: dict[Path, str] = {}
    for d in (cfg.dir("shared"), cfg.dir("reviewers"), cfg.dir("engines"), cfg.dir("standalone"), cfg.dir("profiles")):
        if not d.exists():
            continue
        for f in d.rglob("*.md"):
            text = f.read_text(encoding="utf-8")
            if "<!-- RENDER:" in text:
                out[f] = fill_blocks(cfg, text)
    return out


def render_all(cfg: FactoryConfig | None = None, write: bool = True) -> list[Path]:
    cfg = cfg or CFG.reload()
    changed: list[Path] = []
    targets = {**generated_files(cfg), **block_files(cfg)}
    # stale generated files (a stage removed from factory.yaml) are reported, never deleted silently
    for path, content in targets.items():
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        changed.append(path)
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if write:
        for extra in cfg.dir("commands").glob("*.md"):
            if extra not in targets:
                extra.unlink()          # commands are fully owned by factory.yaml → commands
                changed.append(extra)
    return changed


def check_fresh(cfg: FactoryConfig):
    from lint import Finding  # local import: lint imports render lazily too
    findings = []
    for path in render_all(cfg, write=False):
        rel = str(path.relative_to(cfg.root)) if path.is_relative_to(cfg.root) else str(path)
        findings.append(Finding("MAJOR", "C1-stale-render", rel, 0, "differs from `gov.py render` output (or missing)"))
    return findings


if __name__ == "__main__":  # pragma: no cover
    for p in render_all():
        print("rendered", p)
