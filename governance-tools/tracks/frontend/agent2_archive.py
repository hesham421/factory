"""
ERP Governance Tools — Agent 2: Frontend Artifact Archiver
=============================================================
Copies generated artifacts from their source location into the
canonical frontend governance structure.

Usage:
    python agent2_archive.py --module MODCODE --source /path/to/generated-files
    python agent2_archive.py --module MODCODE --source /path/to/generated-files --dry-run

Filenames scanned for are EXACT matches to what the real governance
engine produces (verified against PROJECT-3-FRONTEND-ENGINE.md) — see
config.py's ARTIFACT_FILES.

Flexibility: this tool does NOT require agent1_create_structure.py to
have run first. If the module's folder structure doesn't exist yet,
this tool creates it automatically (via config.ensure_module_structure)
before archiving.

This is a pure mechanical file-copy tool — it does not check any
readiness gate (backend completeness, UI Shell status, etc.). Those
are decisions made earlier, before the source files it archives even
existed; by the time an artifact is sitting in a source folder ready
to archive, the questions this tool answers are only "does the file
exist" and "where does it go" — nothing else.

This tool has no representation of "backend" anywhere except the one
sanctioned module-identity check (via config.validate_module, which
itself reads backend's registry) and no --track flag.
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
    get_module_path,
    get_stage_path,
    validate_module,
    resolve_filename,
    ensure_module_structure,
    build_manifest,
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
            })

    return operations


def print_plan(mod: str, source_path: Path, operations: list[dict], dry_run: bool,
                structure_created: list[Path], structure_missing: bool = False):
    found     = [o for o in operations if o["found"]]
    missing   = [o for o in operations if not o["found"]]
    overwrite = [o for o in found if o["exists"]]

    print()
    print("═" * 65)
    print(f"  AGENT 2 — Frontend Artifact Archiver")
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
              f"auto-create it first, then archive. Nothing created during "
              f"this dry run.")
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
                status = "OVERWRITE  ⚠"
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


def execute_archive(mod: str, operations: list[dict], dry_run: bool):
    if dry_run:
        print("  DRY RUN — no files copied.")
        return

    copied, skipped, errors = [], [], []

    for op in operations:
        if not op["found"]:
            skipped.append(op["filename"])
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
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)

    print("─" * 65)
    print(f"  ✓ Copied   : {len(copied)} files")
    print(f"  ⚠ Skipped  : {len(skipped)} files (not found)")
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
        print("  Any file present in the source is copied over its destination")
        print("  once you approve the plan — overwrites are shown as OVERWRITE ⚠")
        print("  in the plan above. --force only skips the extra 're-archive'")
        print("  confirmation asked when the module was already archived once.")
        print()

    if not errors:
        print(f"  Archive complete for module [{mod}].")
        print(f"  Next step : python agent3_splitter.py --module {mod}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Archive generated frontend artifacts into the governance repo.")
    parser.add_argument("--module", "-m", required=True, help="Module code — must already be registered in backend.")
    parser.add_argument("--source", "-s", required=True, help="Folder containing the generated artifact files.")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without copying anything.")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Skip the 're-archive' confirmation when the module was already "
                             "archived once. (Per-file overwrites always happen after the plan "
                             "is approved; this flag does not gate them.)")

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

    module_path = get_module_path(mod)
    structure_created = []
    structure_missing = not module_path.exists()

    if structure_missing and not args.dry_run:
        structure_created = ensure_module_structure(mod)
        manifest_path_new = module_path / "manifest.json"
        if not manifest_path_new.exists():
            manifest = build_manifest(mod)
            manifest["created_at"] = datetime.now().isoformat()
            manifest["created_by"] = "agent2_archive.py (auto-created — agent1 was not run first)"
            with open(manifest_path_new, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, indent=2, ensure_ascii=False)

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
    print_plan(mod, source_path, operations, args.dry_run, structure_created, structure_missing)

    if not args.dry_run:
        confirm = input("  Proceed? [y/N]: ").strip().lower()
        if confirm != "y":
            print("\n  Cancelled — no changes made.\n")
            sys.exit(0)
        print()

    execute_archive(mod, operations, args.dry_run)


if __name__ == "__main__":
    main()
