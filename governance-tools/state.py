"""
gov.py state — generated current state (shared/VERSIONING.md §4)
=================================================================
Folds the base version and every delta, in version order, into ONE current
file per artifact at `paths.module.state_dir` (`naming.current_state_file`),
plus `traceability.md` (matrix) and `state.json` (freshness). Engines read
`_state/` only.

Delta folding (VERSIONING.md §3): a version > 1 re-emits only changed
artifacts; inside such an artifact, blocks/records listed as UNCHANGED in the
change manifest may be omitted. Folding = the delta file, with every baseline
record/block that the delta neither re-defines nor lists as REMOVED carried
over (marker blocks into their phase; records appended under a carried-over
section). Nothing is ever silently dropped.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from config import CFG, Artifact, Stage
import idmodel
from toolkit.common import now_iso
from toolkit import markers as mk

_CARRIED = "<!-- carried from baseline v{v} by gov.py state — not re-emitted in this delta -->"


@dataclass
class StateReport:
    mod: str
    version: int
    files: dict[str, Path] = field(default_factory=dict)      # artifact → state file
    sources: dict[str, list[int]] = field(default_factory=dict)  # artifact → versions folded
    missing: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ── change manifest ─────────────────────────────────────────────────────────

_MAN_ART = re.compile(r"^(?P<art>[a-z0-9-]+)\s*:\s*$")
_MAN_ROW = re.compile(r"^\s+(?P<kind>ADDED|MODIFIED|REMOVED|UNCHANGED)\s*:\s*(?P<ids>.*)$")
_MAN_TYPE = re.compile(r"^Change type\s*:\s*(ADDITIVE|BREAKING)", re.I)


def read_change_manifest(mod: str, version: int) -> dict:
    """{'type': ADDITIVE|BREAKING|None, 'artifacts': {artifact: {ADDED:[..], MODIFIED:[..], REMOVED:[..], UNCHANGED:[..]}}}"""
    path = CFG.version_root(mod, version) / CFG.paths["module"]["change_manifest"]
    out = {"path": path, "type": None, "artifacts": {}, "cs": None}
    if not path.exists():
        return out
    cur = None
    for ln in path.read_text(encoding="utf-8").splitlines():
        mt = _MAN_TYPE.match(ln.strip())
        if mt:
            out["type"] = mt.group(1).upper()
        ma = _MAN_ART.match(ln)
        if ma:
            cur = ma.group("art")
            out["artifacts"].setdefault(cur, {"ADDED": [], "MODIFIED": [], "REMOVED": [], "UNCHANGED": []})
            continue
        mr = _MAN_ROW.match(ln)
        if mr and cur:
            ids = idmodel.find_ids(mr.group("ids"))
            extra = [x.strip() for x in mr.group("ids").split(",") if x.strip().lower() == "all"]
            out["artifacts"][cur][mr.group("kind")] += ids + extra
    cs = [x for x in idmodel.find_ids(path.read_text(encoding="utf-8")) if idmodel.split_id(x) and idmodel.split_id(x)[0] == _cs_prefix()]
    out["cs"] = cs[0] if cs else None
    return out


def _cs_prefix() -> str:
    for k, v in CFG.id_atoms().items():
        if v.get("owner") == "versioning":
            return k
    return ""


# ── folding ─────────────────────────────────────────────────────────────────

def _artifact_file(mod: str, stage: Stage, a: Artifact, version: int) -> Path:
    return CFG.artifact_path(mod, stage.id, a.artifact, version)


def _fold_markers(base: str, delta: str, removed: set[str], a: Artifact, base_v: int) -> str:
    """Carry baseline blocks the delta omits into the delta text (by phase)."""
    rb = mk.parse_structure(base, a.track, a.plan)
    rd = mk.parse_structure(delta, a.track, a.plan)
    d_ids = {(b.kind, b.id) for b in rd.blocks()}
    out = delta
    carried_phases = []
    for phase in rb.phases():
        if (phase.kind, phase.id) in d_ids:
            # phase present in delta: carry its missing children (SUB/atoms) before its END
            dphase = next(b for b in rd.phases() if b.id == phase.id)
            missing = [c for c in phase.children if (c.kind, c.id) not in d_ids and c.id not in removed]
            if missing:
                ins = "\n".join([_CARRIED.format(v=base_v)] + [c.rewrap() for c in missing]) + "\n"
                out = out[:dphase.close_off] + ins + out[dphase.close_off:]
                rd = mk.parse_structure(out, a.track, a.plan)   # offsets moved
                d_ids = {(b.kind, b.id) for b in rd.blocks()}
        elif phase.id not in removed:
            carried_phases.append(phase.rewrap())
    if carried_phases:
        out = out.rstrip("\n") + "\n\n" + _CARRIED.format(v=base_v) + "\n" + "\n".join(carried_phases) + "\n"
    return out


def _fold_records(base: str, delta: str, removed: set[str], base_v: int) -> str:
    d_ids = idmodel.defined_ids(delta)
    carried = [r.text for r in idmodel.records(base) if r.id not in d_ids and r.id not in removed]
    if not carried:
        return delta
    return delta.rstrip("\n") + "\n\n" + _CARRIED.format(v=base_v) + "\n" + "\n\n".join(carried) + "\n"


def current_artifact(mod: str, stage: Stage, a: Artifact, version: int) -> tuple[str | None, list[int]]:
    """Fold v1..version for one artifact. Returns (text, versions folded)."""
    present = [v for v in range(1, version + 1) if _artifact_file(mod, stage, a, v).exists()]
    if not present:
        return None, []
    text = _artifact_file(mod, stage, a, present[0]).read_text(encoding="utf-8")
    for v in present[1:]:
        delta = _artifact_file(mod, stage, a, v).read_text(encoding="utf-8")
        man = read_change_manifest(mod, v)["artifacts"].get(a.artifact, {})
        removed = set(man.get("REMOVED", []))
        if a.plan and a.track:
            text = _fold_markers(text, delta, removed, a, present[present.index(v) - 1])
        else:
            text = _fold_records(text, delta, removed, present[present.index(v) - 1])
    return text, present


def _state_name(a: Artifact, mod: str) -> str:
    ext = Path(a.filename(mod)).suffix
    return CFG.fmt(CFG.naming["current_state_file"], artifact=a.artifact) + ext


def traceability_matrix(texts: dict[str, str]) -> str:
    """Markdown matrix: every defined ID → the IDs it traces to → the IDs that reference it."""
    recs: dict[str, idmodel.Record] = {}
    where: dict[str, str] = {}
    for art, t in texts.items():
        for r in idmodel.records(t):
            recs.setdefault(r.id, r)
            where.setdefault(r.id, art)
    refs: dict[str, set[str]] = {i: set() for i in recs}
    for art, t in texts.items():
        for r in idmodel.records(t):
            for tr in r.traces:
                if tr in refs:
                    refs[tr].add(r.id)
    rows = ["| ID | Defined in | Traces to | Referenced by |", "|---|---|---|---|"]
    for rid in sorted(recs, key=lambda x: (idmodel.split_id(x)[0], idmodel.split_id(x)[2])):
        r = recs[rid]
        rows.append(f"| `{rid}` | {where[rid]} | {', '.join(r.traces) or '—'} | {', '.join(sorted(refs[rid])) or '—'} |")
    return "\n".join(rows) + "\n"


def build_state(mod: str, version: int | None = None, write: bool = True) -> StateReport:
    version = CFG.current_version(mod) if version is None else int(version)
    rep = StateReport(mod.upper(), version)
    sdir = CFG.state_dir(mod, version)
    texts: dict[str, str] = {}
    for st in CFG.all_stages():
        for a in st.produces:
            if a.dir:               # platform-level artifacts are already single files
                p = CFG.artifact_path(mod, st.id, a.artifact)
                if p.exists():
                    texts[a.artifact] = p.read_text(encoding="utf-8")
                    rep.files[a.artifact] = p
                elif not a.optional:
                    rep.missing.append(a.artifact)
                continue
            text, folded = current_artifact(mod, st, a, version)
            if text is None:
                if not a.optional:
                    rep.missing.append(a.artifact)
                continue
            texts[a.artifact] = text
            rep.sources[a.artifact] = folded
            target = sdir / _state_name(a, mod)
            rep.files[a.artifact] = target
            if write:
                sdir.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
    if write:
        sdir.mkdir(parents=True, exist_ok=True)
        (sdir / "traceability.md").write_text(
            CFG.data["lint"]["generated_marker"] + "\n# Traceability matrix\n\n" + traceability_matrix(texts), encoding="utf-8")
        (sdir / "state.json").write_text(json.dumps({
            "module": rep.mod, "version": version, "profile": CFG.profile_id, "generated_at": now_iso(),
            "sources": rep.sources, "missing": rep.missing,
            "inputs_mtime": _latest_mtime(mod, version),
        }, indent=2), encoding="utf-8")
    return rep


def _latest_mtime(mod: str, version: int) -> float:
    latest = 0.0
    for v in range(1, version + 1):
        root = CFG.version_root(mod, v)
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file() and CFG.paths["module"]["state_dir"] not in p.parts and CFG.paths["module"]["packages_dir"] not in p.parts:
                latest = max(latest, p.stat().st_mtime)
    return latest


def is_fresh(mod: str, version: int | None = None) -> bool:
    version = CFG.current_version(mod) if version is None else int(version)
    sj = CFG.state_dir(mod, version) / "state.json"
    if not sj.exists():
        return False
    data = json.loads(sj.read_text(encoding="utf-8"))
    return float(data.get("inputs_mtime", 0)) >= _latest_mtime(mod, version) - 1e-6


def state_text(mod: str, version: int, artifact: str) -> str | None:
    """Read one artifact from _state/ (what engines and analyze read)."""
    for st in CFG.all_stages():
        for a in st.produces:
            if a.artifact != artifact:
                continue
            if a.dir:
                p = CFG.artifact_path(mod, st.id, a.artifact)
            else:
                p = CFG.state_dir(mod, version) / _state_name(a, mod)
            return p.read_text(encoding="utf-8") if p.exists() else None
    return None
