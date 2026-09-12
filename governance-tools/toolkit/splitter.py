"""
toolkit.splitter — split a marked plan into addressable package files
======================================================================
    split(mod, track, plan, version=None, *, yes=True, dry_run=False,
          strict=False, fix_safe=False)                    -> SplitReport
    verify(mod, track, plan, version=None)                 -> dict

Source  : CFG.plan_path(mod, track, plan, version)
Target  : CFG.packages_dir(mod, track, plan, version)   (the "container")

Stages (all non-interactive; `yes=False` or `dry_run=True` = plan only):
  1. parse + validate  — block on the most severe level (and on the next under `strict`);
                         `fix_safe` runs the safe auto-fixer first
  2. split             — per phase: with SUBs → one `<SUB-ID>.md` per SUB plus
                         `<PHASE>-HEADER.md` for the preamble; without → `<PHASE>.md`.
                         Per-phase plans write into `<container>/<phase.folder>/`;
                         single-phase plans (markers.rules.sub_unqualified_exempt_plans)
                         write flat files into the container. Content outside every
                         phase → `_SECTIONS.md`. An unknown phase is refused.
  3. index.md          — per folder, generated-marker line at the top
  4. verification.json — `markers.rules.verify` digest of EVERY atom and every
                         split unit, source vs package file
  5. state.json + manifest.status.split[<track>/<plan>]

Every unit file starts with `<!-- source: … -->` and `<!-- traces: … -->`
(the block's own + descendants' `traces=`), then the block re-emitted with
its own markers byte-identically — packages leave already traced and
independently parseable. Re-running removes what the previous run wrote and
produces identical files.

CLI:  python -m toolkit.splitter --module ORG --track backend --plan exec
        [--version N] [--dry-run] [--strict] [--fix-safe] [--validate-only FILE]
"""
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from config import CFG

from .common import (flat_plan, generated_marker, markers_schema_version, now_iso,
                     plan_key, plan_path_or_none, read_json, rel, write_json)
from .markers import AutofixReport, Block, Finding, ParseResult, parse_structure, safe_autofix, validate
from .structure import MarkerSchemaError, require_supported_marker_schema, set_status

INDEX_FILE = "index.md"
STATE_FILE = "state.json"
VERIFICATION_FILE = "verification.json"
SECTIONS_FILE = "_SECTIONS.md"
HEADER_SUFFIX = "-HEADER"


@dataclass
class SplitReport:
    module: str
    track: str
    plan: str
    version: int
    source: Path | None = None
    dry_run: bool = False
    strict: bool = False
    findings: list[Finding] = field(default_factory=list)
    blocked: bool = False
    errors: list[str] = field(default_factory=list)
    autofix: AutofixReport | None = None
    written: list[Path] = field(default_factory=list)      # unit/header/section files (planned when dry_run)
    indexes: list[Path] = field(default_factory=list)
    verification: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        if self.errors or self.blocked:
            return False
        return self.dry_run or bool(self.verification.get("ok"))

    def summary(self) -> str:
        head = f"split [{self.module}] v{self.version} {plan_key(self.track, self.plan)}"
        if self.errors:
            return f"{head}: ERROR — " + "; ".join(self.errors)
        if self.blocked:
            return f"{head}: BLOCKED — {len(self.findings)} finding(s)"
        v = self.verification
        tail = "dry run" if self.dry_run else f"verified {v.get('checked', 0)} block(s), ok={v.get('ok')}"
        return f"{head}: {len(self.written)} file(s), {tail}"


# ── helpers ──────────────────────────────────────────────────────────────────

def _digest(block: Block) -> str:
    algo = (CFG.markers.get("rules") or {}).get("verify") or "sha256"
    return hashlib.new(algo, block.content.strip().encode("utf-8")).hexdigest()


def _fname(marker_id: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_.") else "-" for c in marker_id.strip()) + ".md"


def _traces_line(ids: list[str]) -> str:
    return f"<!-- traces: {', '.join(ids) if ids else 'none'} -->"


def _unit_body(phase: Block, unit: Block, header_name: str | None) -> str:
    lines = [f"<!-- source: {phase.kind}:{phase.id}" + (f" / {unit.kind}:{unit.id}" if unit is not phase else "") + " -->"]
    if header_name:
        lines.append(f"<!-- context: {header_name} — phase-level preamble -->")
    lines.append(_traces_line(unit.all_traces()))
    return "\n".join(lines) + "\n" + unit.rewrap().strip("\n") + "\n"


def build_write_plan(res: ParseResult, container: Path) -> list[dict]:
    """[{dest, body, kind, unit}] — pure; refuses an unknown phase (C3)."""
    g, rows = res.grammar, []
    flat = flat_plan(res.plan)
    for ph in res.phases():
        spec = g.phase_by_key.get(ph.id)
        if spec is None:
            raise ValueError(f"{ph.kind}:{ph.id} is not a phase of {res.track}/{res.plan} — refusing to split")
        folder = container if flat else container / spec.folder
        subs = res.subs_of(ph)
        if not subs:
            rows.append({"dest": folder / _fname(ph.id), "body": _unit_body(ph, ph, None), "kind": "unit", "unit": ph})
            continue
        preamble = res.preamble(ph)
        header_name = _fname(ph.id + HEADER_SUFFIX) if preamble else None
        if preamble:
            body = f"<!-- source: {ph.kind}:{ph.id} — preamble before the first {g.sub_kind} -->\n{_traces_line(ph.traces)}\n{preamble}\n"
            rows.append({"dest": folder / header_name, "body": body, "kind": "header", "unit": None})
        for s in subs:
            rows.append({"dest": folder / _fname(s.id), "body": _unit_body(ph, s, header_name), "kind": "unit", "unit": s})
    outside = res.outside_phases()
    if outside:
        body = f"<!-- source: content outside every {g.phase_kind} block (leading / between / trailing sections) -->\n{outside}\n"
        rows.append({"dest": container / SECTIONS_FILE, "body": body, "kind": "sections", "unit": None})
    return rows


def _clean_previous(container: Path) -> None:
    """Remove what an earlier run wrote (from state.json) so re-runs never
    leave stale files behind; never touches anything outside the container."""
    state = read_json(container / STATE_FILE) or {}
    for f in state.get("files", []):
        p = (CFG.root / f).resolve()
        if p.is_file() and container.resolve() in p.parents:
            p.unlink()
    for idx in container.rglob(INDEX_FILE):
        idx.unlink()
    for name in (VERIFICATION_FILE, STATE_FILE):
        if (container / name).exists():
            (container / name).unlink()


def write_indexes(container: Path) -> list[Path]:
    out = []
    for folder in sorted({container, *[p for p in container.rglob("*") if p.is_dir()]}):
        files = sorted(f for f in folder.glob("*.md") if f.name != INDEX_FILE)
        if not files:
            continue
        title = rel(folder) if folder == container else str(folder.relative_to(container))
        lines = [generated_marker(), f"# Index — {title}", ""] + [f"- [{f.stem}]({f.name})" for f in files]
        idx = folder / INDEX_FILE
        idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
        out.append(idx)
    return out


def _package_blocks(container: Path, track: str, plan: str) -> dict[tuple[str, str], tuple[Block, Path]]:
    found: dict[tuple[str, str], tuple[Block, Path]] = {}
    for f in sorted(container.rglob("*.md")):
        if f.name == INDEX_FILE:
            continue
        res = parse_structure(f.read_text(encoding="utf-8"), track, plan)
        for b in res.blocks():
            found.setdefault((b.kind, b.id), (b, f))
    return found


def verify(mod: str, track: str, plan: str, version: int | None = None) -> dict:
    """Digest-compare every atom and every split unit of the source plan with
    its copy inside the package files. Pure read; returns the verification dict.

    Re-runnable on purpose. This comparison used to happen ONCE, at split time,
    and every hand edit to a package after that drifted silently — the packages
    the implementer reads stopped being the plan the gate approved and nothing
    said so. `gov.py verify-split` runs it on demand, and `gov.py
    verify-delivery` runs it where a consumer reconciles."""
    mod = mod.upper()
    version = CFG.current_version(mod) if version is None else int(version)
    src = plan_path_or_none(mod, track, plan, version)
    container = CFG.packages_dir(mod, track, plan, version)
    algo = (CFG.markers.get("rules") or {}).get("verify") or "sha256"
    out = {"module": mod, "track": track, "plan": plan, "version": version, "verify": algo,
           "source": rel(src) if src else None, "checked": 0, "missing": [], "mismatched": [], "ok": False, "at": now_iso()}
    if not src or not src.exists() or not container.exists():
        out["missing"].append("source plan or package container not found")
        return out
    res = validate(src, track, plan)
    expected: list[Block] = list(res.atoms())
    for ph in res.phases():
        expected += res.subs_of(ph) or [ph]
    found = _package_blocks(container, track, plan)
    for b in expected:
        out["checked"] += 1
        hit = found.get((b.kind, b.id))
        if hit is None:
            out["missing"].append(f"{b.kind}:{b.id}")
        elif _digest(hit[0]) != _digest(b):
            out["mismatched"].append(f"{b.kind}:{b.id} in {rel(hit[1])}")
    # A verification that checked NOTHING is not a pass. Without this, a plan
    # carrying no split units verifies "ok" over an empty set and the caller
    # records a successful split of nothing.
    if out["checked"] == 0:
        out["missing"].append(
            "no split unit found in the source plan — nothing was verified, "
            "so this is a failure, not a clean verification")
    out["ok"] = not out["missing"] and not out["mismatched"]
    return out


# ── the public entry point ───────────────────────────────────────────────────

def split(mod: str, track: str, plan: str, version: int | None = None, *, yes: bool = True,
          dry_run: bool = False, strict: bool = False, fix_safe: bool = False) -> SplitReport:
    mod = mod.upper()
    version = CFG.current_version(mod) if version is None else int(version)
    rep = SplitReport(module=mod, track=track, plan=plan, version=version, dry_run=dry_run or not yes, strict=strict)
    src = plan_path_or_none(mod, track, plan, version)
    if src is None:
        rep.errors.append(f"no stage produces a {plan} plan for track {track}")
        return rep
    rep.source = src
    if not src.exists():
        rep.errors.append(f"plan not found: {rel(src)} (archive it first)")
        return rep
    # Grammar-version precondition, BEFORE any parsing (see structure.py).
    try:
        require_supported_marker_schema(mod, version)
    except MarkerSchemaError as e:
        rep.errors.append(str(e))
        return rep
    if fix_safe and not rep.dry_run:
        rep.autofix = safe_autofix(src, track, plan)
    res = validate(src, track, plan, strict=strict)
    rep.findings = res.findings
    if res.blocking(strict):
        rep.blocked = True
        return rep
    # A plan with no phase block has nothing to split. It must NOT fall through
    # to the write plan, where the whole unsplit file would be emitted as one
    # sections file and recorded as a successful split of zero units.
    if not res.phases():
        g = res.grammar
        rep.errors.append(
            f"no {g.phase_kind} block found in {rel(src)} — the plan was not "
            f"marker-annotated by the engine that owns {track}/{plan}, so there is "
            f"nothing to split. Expected one of: {', '.join(g.phase_by_key) or '(none declared)'}. "
            f"Fix at the source by regenerating the plan through that engine; this "
            f"tool detects and reports marker drift and never injects markers.")
        return rep
    container = CFG.packages_dir(mod, track, plan, version)
    try:
        rows = build_write_plan(res, container)
    except ValueError as e:                     # unknown phase — defensive, validation already refused it
        rep.errors.append(str(e))
        return rep
    rep.written = [r["dest"] for r in rows]
    if rep.dry_run:
        return rep
    _clean_previous(container)
    for r in rows:
        r["dest"].parent.mkdir(parents=True, exist_ok=True)
        r["dest"].write_text(r["body"], encoding="utf-8")
    rep.indexes = write_indexes(container)
    rep.verification = verify(mod, track, plan, version)
    write_json(container / VERIFICATION_FILE, rep.verification)
    write_json(container / STATE_FILE, {
        "module": mod, "track": track, "plan": plan, "version": version,
        "profile": CFG.profile_id, "markers_schema_version": markers_schema_version(),
        "source": rel(src), "split_at": now_iso(), "strict": strict,
        "files": [rel(p) for p in rep.written], "indexes": [rel(p) for p in rep.indexes],
        "units": [r["unit"].kind + ":" + r["unit"].id for r in rows if r["unit"] is not None],
        "atoms": [b.kind + ":" + b.id for b in res.atoms()],
        "verification": rel(container / VERIFICATION_FILE), "verified": rep.verification["ok"],
    })
    set_status(mod, version, "split", bool(rep.verification["ok"]), sub=plan_key(track, plan))
    return rep


# ── CLI ──────────────────────────────────────────────────────────────────────

def _print_findings(findings: list[Finding]) -> None:
    for f in findings:
        print(f"  {f}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Split a marked plan into package files (non-interactive).")
    ap.add_argument("--module", "-m", help="module code (not needed with --validate-only)")
    ap.add_argument("--track", required=True, choices=list(CFG.tracks))
    ap.add_argument("--plan", required=True, help="plan key as declared by the profile (e.g. one of the packages keys)")
    ap.add_argument("--version", "-v", type=int, default=None, help="default: current version (filesystem)")
    ap.add_argument("--dry-run", action="store_true", help="show the write plan; write nothing")
    ap.add_argument("--strict", action="store_true", help="second-rank findings (thresholds, orphans …) block too")
    ap.add_argument("--fix-safe", action="store_true", help="run the safe auto-fixer on the source first (<file>.orig kept)")
    ap.add_argument("--validate-only", metavar="FILE", help="validate this file for --track/--plan and exit")
    a = ap.parse_args(argv)

    if a.validate_only:
        path = Path(a.validate_only)
        if not path.is_file():
            print(f"  ERROR file not found: {path}")
            return 1
        if a.fix_safe:
            fix = safe_autofix(path, a.track, a.plan)
            for f in fix.phase_key_fixes + fix.sub_qualification_fixes:
                print(f"  fixed line {f['line']}: {f['from']} → {f['to']}")
        res = validate(path, a.track, a.plan, strict=a.strict)
        _print_findings(res.findings)
        blocking = res.blocking(a.strict)
        print(f"  {path.name}: {len(res.phases())} phase(s), {len(res.atoms())} atom(s), "
              f"{len(res.findings)} finding(s), {len(blocking)} blocking")
        # Validating a file in which nothing was found is a failure to validate,
        # not a clean bill of health — the single most misreadable "pass" there is.
        if not res.phases():
            g = res.grammar
            print(f"  ERROR no {g.phase_kind} block found in {path} — this file is not "
                  f"marker-annotated for {a.track}/{a.plan}. Expected one of: "
                  f"{', '.join(g.phase_by_key) or '(none declared)'}. Regenerate it through "
                  f"the engine that owns the plan; this tool never injects markers.")
            return 1
        return 1 if blocking else 0

    if not a.module:
        ap.error("--module is required (unless --validate-only)")
    rep = split(a.module, a.track, a.plan, a.version, dry_run=a.dry_run, strict=a.strict, fix_safe=a.fix_safe)
    if rep.autofix and rep.autofix.changed:
        print(f"  auto-fixed {len(rep.autofix.phase_key_fixes) + len(rep.autofix.sub_qualification_fixes)} marker(s); original: {rep.autofix.backup}")
    _print_findings(rep.findings)
    for p in rep.written:
        print(f"  {'plan ' if rep.dry_run else 'wrote'} {rel(p)}")
    v = rep.verification
    for m in v.get("missing", []) + v.get("mismatched", []):
        print(f"  VERIFY FAILED {m}")
    print(rep.summary())
    return 0 if rep.ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
