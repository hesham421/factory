"""
toolkit.archive — copy generated artifacts into their stage folders
====================================================================
    archive(mod, version, source_dir, force=False, dry_run=False) -> ArchiveReport

For every artifact that ANY stage (pipeline or standalone) writes into the
module version — names resolved from factory.yaml with the module code —
copy `<source_dir>/<file>` to `CFG.artifact_path(mod, stage, artifact, version)`.
  • missing in source        → skipped with a warning (silently when `optional`)
  • destination exists       → kept, unless `force` (never overwrites by default)
  • structure missing        → created first (no dependency on `structure`)
Non-interactive. Updates manifest.status.archived.

CLI:  python -m toolkit.archive --module ORG --source DIR [--version N] [--dry-run] [--force]
"""
from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from config import CFG

from .common import module_stages, now_iso, rel
from .structure import ensure_structure, set_status


@dataclass
class ArchiveReport:
    module: str
    version: int
    source_dir: Path
    dry_run: bool = False
    copied: list[str] = field(default_factory=list)
    overwritten: list[str] = field(default_factory=list)
    kept_existing: list[str] = field(default_factory=list)
    skipped_missing: list[str] = field(default_factory=list)
    skipped_optional: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def plan_operations(mod: str, version: int, source_dir: Path) -> list[dict]:
    """One row per module-level artifact: src, dst, found, exists, optional."""
    ops = []
    for st in module_stages():
        for a in st.produces:
            if a.dir:
                continue
            name = a.filename(mod)
            src, dst = Path(source_dir) / name, CFG.artifact_path(mod, st.id, a.artifact, version)
            ops.append({"stage": st.id, "artifact": a.artifact, "file": name, "src": src, "dst": dst,
                        "found": src.is_file(), "exists": dst.exists(), "optional": a.optional})
    return ops


def archive(mod: str, version: int | None, source_dir: Path, force: bool = False, dry_run: bool = False) -> ArchiveReport:
    mod = mod.upper()
    version = CFG.current_version(mod) if version is None else int(version)
    source_dir = Path(source_dir)
    rep = ArchiveReport(module=mod, version=version, source_dir=source_dir, dry_run=dry_run)
    if not source_dir.is_dir():
        rep.errors.append(f"source folder not found: {source_dir}")
        return rep
    if not dry_run:
        ensure_structure(mod, version)
    for op in plan_operations(mod, version, source_dir):
        if not op["found"]:
            (rep.skipped_optional if op["optional"] else rep.skipped_missing).append(op["file"])
            if not op["optional"]:
                rep.warnings.append(f"{op['file']} not found in {source_dir} — skipped ({op['stage']})")
            continue
        if op["exists"] and not force:
            rep.kept_existing.append(op["file"])
            rep.warnings.append(f"{op['file']} already archived at {rel(op['dst'])} — kept (use force to overwrite)")
            continue
        (rep.overwritten if op["exists"] else rep.copied).append(op["file"])
        if dry_run:
            continue
        try:
            op["dst"].parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(op["src"], op["dst"])
        except OSError as e:
            rep.errors.append(f"{op['file']}: {e}")
    if not dry_run and rep.ok:
        set_status(mod, version, "archived", True)
        set_status(mod, version, "archived_at", now_iso())
        set_status(mod, version, "archived_files", sorted(rep.copied + rep.overwritten))
    return rep


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Archive generated artifacts into the module version (non-interactive).")
    ap.add_argument("--module", "-m", required=True)
    ap.add_argument("--source", "-s", required=True, help="folder holding the generated artifact files")
    ap.add_argument("--version", "-v", type=int, default=None, help="default: current version (filesystem)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", "-f", action="store_true", help="overwrite files already archived")
    a = ap.parse_args(argv)
    rep = archive(a.module, a.version, Path(a.source).expanduser().resolve(), force=a.force, dry_run=a.dry_run)
    print(f"archive [{rep.module}] v{rep.version} ← {rep.source_dir}  ({'DRY RUN' if rep.dry_run else 'LIVE'})")
    for label, rows in (("copied", rep.copied), ("overwritten", rep.overwritten), ("kept (exists)", rep.kept_existing),
                        ("missing", rep.skipped_missing), ("optional, absent", rep.skipped_optional)):
        if rows:
            print(f"  {label:<17}: {', '.join(rows)}")
    for w in rep.warnings:
        print(f"  WARN {w}")
    for e in rep.errors:
        print(f"  ERROR {e}")
    return 0 if rep.ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
