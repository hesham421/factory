"""
toolkit.common — small helpers shared by markers / structure / archive / splitter
=================================================================================
Everything here is derived from `CFG` (factory.yaml + the active profile).
No stage id, phase key, ID prefix, plan name or package name is spelled in
this package (Constitution C1/C2) — the lint rule `scan_code_literals`
enforces it.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import CFG, Stage

# ── severity policy — factory.yaml → analyze (the ONE source) ────────────────
# The severity vocabulary and the set that blocks are factory facts. They used
# to be a tuple here, a dict in analyze.py and a comparison in gov.py: three
# literals, one policy, and no way for an operator to see or change it. Every
# reader below goes through these helpers, so `analyze`'s stage/gate verdict and
# `lint`'s verdict are the same question asked twice and cannot disagree.
# Rank 0 is the most severe declared level.


def severities() -> tuple[str, ...]:
    return tuple(CFG.analyze["severities"])


def sev(rank: int) -> str:
    """The severity at `rank` in the configured order (0 = most severe), clamped
    so a factory that declares fewer levels than a caller asks for still resolves."""
    s = severities()
    return s[min(max(rank, 0), len(s) - 1)]


def severity_rank(severity: str) -> int:
    """Sort key. A severity the vocabulary does not declare sorts after every one
    that it does — it is a defect in the contract, not a level in the scale."""
    s = severities()
    return s.index(severity) if severity in s else len(s)


def known_severity(severity: str) -> bool:
    return severity in severities()


def blocking_severities() -> frozenset[str]:
    return frozenset(CFG.analyze["blocking"])


def blocks(findings) -> bool:
    """THE predicate: does this set of findings close the stage, gate or run it
    belongs to? Every caller asks it here; nobody re-spells the comparison."""
    blocking = blocking_severities()
    return any(getattr(f, "severity", None) in blocking for f in findings)


def counts_line(counts: dict) -> str:
    """A counts mapping → "1 critical · 4 major" — the operator-facing
    tally, written from the configured vocabulary rather than from three names
    spelled in a format string."""
    return " · ".join(f"{n} {name.lower()}" for name, n in counts.items())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    """Path relative to the factory root; absolute string when the path lives
    outside the root (tests, --output overrides)."""
    try:
        return str(Path(path).resolve().relative_to(CFG.root))
    except ValueError:
        return str(path)


def rel_to(path: Path, base: Path) -> str:
    """Path relative to `base` — the form a generated index must emit.

    An index that spells its own repo-relative prefix ("<project>/modules/<MOD>/…")
    resolves only in the repository that produced it: the same tree delivered into a
    consumer repo sits under a different prefix and every path in it dangles. Relative
    to the index's own directory, the same string resolves in both.
    """
    p, b = Path(path).resolve(), Path(base).resolve()
    if p == b:
        return "."
    return os.path.relpath(p, b).replace(os.sep, "/")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def module_stages() -> list[Stage]:
    """Stages (pipeline + standalone) that write at least one artifact INTO the
    module version folder — i.e. an artifact without a platform-level `dir`."""
    return [s for s in CFG.all_stages() if any(a.dir is None for a in s.produces)]


def track_plans() -> list[tuple[str, str]]:
    """Every (track, plan) that BOTH factory.yaml (tracks.<t>.packages) and the
    active profile (tracks.<t>.plans) declare, in factory order."""
    out: list[tuple[str, str]] = []
    for track, spec in CFG.tracks.items():
        declared = CFG.profile.plans(track) if track in CFG.profile.tracks else []
        for plan in spec.get("packages", {}):
            if plan in declared:
                out.append((track, plan))
    return out


def plan_key(track: str, plan: str) -> str:
    """Manifest / report key for a (track, plan) pair."""
    return f"{track}/{plan}"


def flat_plan(plan: str) -> bool:
    """A plan whose SUB labels are bare (markers.rules.sub_unqualified_exempt_plans)
    is a single-phase plan: its package is a FLAT container with no per-phase
    sub-folders. Every other plan gets one folder per phase."""
    rules = CFG.markers.get("rules", {}) or {}
    return plan in (rules.get("sub_unqualified_exempt_plans") or [])


def generated_marker() -> str:
    return CFG.data["lint"]["generated_marker"]


def markers_schema_version() -> int:
    return int(CFG.markers.get("schema_version", 0))


def plan_path_or_none(mod: str, track: str, plan: str, version: int | None) -> Path | None:
    try:
        return CFG.plan_path(mod, track, plan, version)
    except KeyError:
        return None
