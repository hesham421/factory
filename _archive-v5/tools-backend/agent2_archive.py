"""
ERP Governance Tools — Agent 2: Backend Artifact Archiver
============================================================
Copies generated artifacts from their source location into the
canonical backend governance structure.

Usage:
    python agent2_archive.py --module MODCODE --source /path/to/generated-files
    python agent2_archive.py --module MODCODE --source /path/to/generated-files --dry-run

Filenames scanned for are EXACT matches to what the real governance
engines produce (verified against PRD-ENGINE.md,
PROJECT-1-SRS-GOVERNANCE-ENGINE.md, PROJECT-2-DATABASE-GOVERNANCE-
ENGINE.md, UI-UX-DESIGN-ENGINE.md, PROJECT-3-BACKEND-ENGINE.md) — see
config.py's ARTIFACT_FILES.

Flexibility: this tool does NOT require agent1_create_structure.py to
have run first. If the module's folder structure doesn't exist yet,
this tool creates it automatically (via config.ensure_module_structure)
before archiving — there is no hard pipeline dependency between the
two agents. Running agent1 first is still fine and remains idempotent
(it will simply find the structure already exists).

This tool has no representation of "frontend" anywhere, and no
--track flag — it does exactly one job: backend.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    REPO_BASE_PATH,
    ARTIFACT_FILES,
    SHARED_FILES,
    get_module_path,
    get_stage_path,
    validate_module,
    resolve_filename,
    ensure_module_structure,
    build_manifest,
    set_current_version,
    load_modules_registry,
)


def scan_source(mod: str, source_path: Path) -> list[dict]:
    """Scan source folder for known artifact files (exact names only)."""
    operations = []

    for stage, templates in ARTIFACT_FILES.items():
        dest_dir = get_stage_path(mod, stage)
        for template in templates:
            filename = resolve_filename(template, mod)
            src = source_path / filename
            dst = dest_dir / filename
            operations.append({
                "stage":    stage,
                "filename": filename,
                "src":      src,
                "dst":      dst,
                "found":    src.exists(),
                "exists":   dst.exists(),
                "shared":   False,
            })

    for filename in SHARED_FILES:
        src = source_path / filename
        dst = REPO_BASE_PATH / filename
        operations.append({
            "stage":    "SHARED",
            "filename": filename,
            "src":      src,
            "dst":      dst,
            "found":    src.exists(),
            "exists":   dst.exists(),
            "shared":   True,
        })

    return operations


def print_plan(mod: str, source_path: Path, operations: list[dict], dry_run: bool,
                structure_created: list[Path], structure_missing: bool = False,
                force: bool = False):
    found     = [o for o in operations if o["found"]]
    missing   = [o for o in operations if not o["found"]]
    overwrite = [o for o in found if o["exists"]]

    print()
    print("═" * 65)
    print(f"  AGENT 2 — Backend Artifact Archiver")
    print(f"  Module  : {mod}")
    print(f"  Source  : {source_path}")
    print(f"  Repo    : {REPO_BASE_PATH}")
    print(f"  Mode    : {'DRY RUN (no changes)' if dry_run else 'LIVE'}")
    print("═" * 65)

    if structure_created:
        print()
        print(f"  ⓘ Module structure did not exist — {len(structure_created)} "
              f"folders were created automatically (agent1 was not required "
              f"to run first).")
    elif structure_missing and dry_run:
        print()
        print(f"  ⓘ Module structure does not exist yet — a LIVE run would "
              f"auto-create it first (agent1 is not required), then archive "
              f"into it. Nothing created during this dry run.")
    print()

    stages = {}
    for op in operations:
        stages.setdefault(op["stage"], []).append(op)

    for stage, ops in stages.items():
        print(f"  [{stage}]")
        for op in ops:
            if not op["found"]:
                status = "NOT FOUND  ✗ skip"
            elif op["exists"]:
                status = "OVERWRITE  ⚠" if force else "KEEP       ⚠ exists"
            else:
                status = "COPY       ✓"
            try:
                rel_dst = op["dst"].relative_to(REPO_BASE_PATH)
            except ValueError:
                rel_dst = op["dst"]
            print(f"    {status:<18} {op['filename']:<35} → {rel_dst}")
        print()

    print("─" * 65)
    print(f"  To copy    : {len(found)}")
    print(f"  To skip    : {len(missing)} (not found in source)")
    print(f"  Overwrites : {len(overwrite)}")
    if missing:
        print()
        print("  Missing files (will be skipped):")
        for op in missing:
            print(f"    ✗ {op['filename']}")
    print()


def execute_archive(mod: str, operations: list[dict], dry_run: bool, force: bool = False):
    if dry_run:
        print("  DRY RUN — no files copied.")
        return

    copied, skipped, skipped_exists, errors = [], [], [], []

    for op in operations:
        if not op["found"]:
            skipped.append(op["filename"])
            continue
        # An existing destination is preserved unless --force is given. This is
        # what the closing note has always promised; previously copy2 overwrote
        # unconditionally, contradicting that note (M4).
        if op["dst"].exists() and not force:
            skipped_exists.append(op["filename"])
            continue
        try:
            op["dst"].parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(op["src"], op["dst"])
            copied.append(op["filename"])
        except Exception as e:
            errors.append(f"{op['filename']}: {e}")

    manifest_path = get_module_path(mod) / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        manifest.setdefault("status", {})["archived"] = True
        manifest["archived_at"] = datetime.now().isoformat()
        manifest["archived_files"] = copied
        manifest["skipped_files"] = skipped
        manifest["skipped_existing_files"] = skipped_exists
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)

    print("─" * 65)
    print(f"  ✓ Copied        : {len(copied)} files")
    print(f"  ⚠ Skipped (n/f) : {len(skipped)} files (not found in source)")
    print(f"  ⚠ Skipped (kept): {len(skipped_exists)} files (already present — use --force to overwrite)")
    if errors:
        print(f"  ✗ Errors   : {len(errors)}")
        for err in errors:
            print(f"    {err}")
    print(f"  ✓ Manifest : updated (archived: true)")
    print("─" * 65)
    print()

    if skipped:
        print("  NOTE: Missing files can be added later by re-running")
        print(f"  agent2_archive.py --module {mod} --source <path>")
        print()
    if skipped_exists:
        print(f"  NOTE: {len(skipped_exists)} file(s) already existed and were kept as-is.")
        print(f"  Re-run with --force to overwrite them.")
        print()

    if not errors:
        print(f"  Archive complete for module [{mod}].")
        print(f"  Next step : python agent3_splitter.py --module {mod}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Archive generated backend artifacts into the governance repo.")
    parser.add_argument("--module", "-m", required=True, help="Module code (module code).")
    parser.add_argument("--source", "-s", required=True, help="Folder containing the generated artifact files.")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without copying anything.")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing files without asking.")

    args = parser.parse_args()

    try:
        mod = validate_module(args.module)
    except ValueError as e:
        print(f"\n  ERROR: {e}\n")
        sys.exit(1)

    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists():
        print(f"\n  ERROR: Source folder not found: {source_path}\n")
        sys.exit(1)

    # Version resolution (IFA-aware): archive into whatever version agent1
    # set as current — v1 for a first pass, v2/v3… when agent1 --new-version
    # ran first. Reading current_version (never hardcoding 1) is what lets an
    # incremental-feature delta land in modules/[MOD]/v2/ instead of over v1.
    registry = load_modules_registry()
    entry = registry.get("modules", {}).get(mod)
    version = (entry.get("current_version") if entry else None) or 1

    # Flexibility: auto-create structure if missing — no hard dependency on agent1
    module_path = get_module_path(mod, version)
    structure_created = []
    structure_missing = not module_path.exists()

    if structure_missing and not args.dry_run:
        structure_created = ensure_module_structure(mod, version)
        # Keep manifest.json / registry tracking consistent even though
        # agent1 never ran — same manifest shape agent1 would have written.
        manifest_path_new = module_path / "manifest.json"
        if not manifest_path_new.exists():
            manifest = build_manifest(mod, version)
            manifest["created_at"] = datetime.now().isoformat()
            manifest["created_by"] = "agent2_archive.py (auto-created — agent1 was not run first)"
            with open(manifest_path_new, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, indent=2, ensure_ascii=False)
            set_current_version(mod, version)

    manifest_path = module_path / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        if manifest.get("status", {}).get("archived") and not args.force:
            print(f"\n  WARNING: Module [{mod}] was already archived.")
            print(f"  Use --force to overwrite existing files.")
            confirm = input("  Continue anyway? [y/N]: ").strip().lower()
            if confirm != "y":
                print("\n  Cancelled — no changes made.\n")
                sys.exit(0)
            print()

    operations = scan_source(mod, source_path)
    print_plan(mod, source_path, operations, args.dry_run, structure_created, structure_missing, force=args.force)

    if not args.dry_run:
        confirm = input("  Proceed? [y/N]: ").strip().lower()
        if confirm != "y":
            print("\n  Cancelled — no changes made.\n")
            sys.exit(0)
        print()

    execute_archive(mod, operations, args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
