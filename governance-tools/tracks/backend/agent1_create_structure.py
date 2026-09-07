"""
ERP Governance Tools — Agent 1: Backend Structure Creator
============================================================
Creates the canonical backend folder structure for a module.

Usage:
    python agent1_create_structure.py --module MODCODE
    python agent1_create_structure.py --module MODCODE --dry-run
    python agent1_create_structure.py --module NEW --auto-register --description "New Module"
    python agent1_create_structure.py --module MODCODE --new-version
    python agent1_create_structure.py --list-modules

This tool has no representation of "frontend" anywhere. It creates
exactly one thing: the backend stage folders (P0, P0_5, P1, P2, P2_5,
P3_1, P3_5_BE) and their packages/ subfolders. There is no
--frontend-only flag, no --track flag — this tool does one job.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    REPO_BASE_PATH,
    KNOWN_MODULES,
    MODULE_STRUCTURE,
    PACKAGES_STRUCTURE,
    BACKEND_STAGES,
    get_module_version_path,
    validate_module,
    build_manifest,
    get_next_version,
    set_current_version,
    load_modules_registry,
)


def plan_structure(mod: str, version: int) -> list[dict]:
    """Build a plan of all folders to create for a module version."""
    base = get_module_version_path(mod, version)
    folders = []

    for stage in BACKEND_STAGES:
        p = base / MODULE_STRUCTURE[stage]
        folders.append({"path": p, "label": stage})

    for artifact, subs in PACKAGES_STRUCTURE.items():
        # Always plan the container itself (backend-test has no pre-created
        # subs — Agent 3 writes flat files straight into the container).
        folders.append({"path": base / "packages" / artifact, "label": f"packages/{artifact}"})
        for sub in subs:
            p = base / "packages" / artifact / sub
            folders.append({"path": p, "label": f"packages/{artifact}/{sub}"})

    for f in folders:
        f["exists"] = f["path"].exists()

    return folders


def print_plan(mod: str, version: int, folders: list[dict], dry_run: bool):
    base = get_module_version_path(mod, version)
    new_count  = sum(1 for f in folders if not f["exists"])
    skip_count = sum(1 for f in folders if f["exists"])

    print()
    print("═" * 62)
    print(f"  AGENT 1 — Backend Structure Creator")
    print(f"  Module  : {mod}")
    print(f"  Version : v{version}")
    try:
        print(f"  Path    : {base.relative_to(REPO_BASE_PATH)}")
    except ValueError:
        print(f"  Path    : {base}")
    print(f"  Mode    : {'DRY RUN (no changes)' if dry_run else 'LIVE'}")
    print("═" * 62)
    print()

    for f in folders:
        status = "EXISTS  ⚠ skip" if f["exists"] else "CREATE  ✓"
        try:
            rel = f["path"].relative_to(REPO_BASE_PATH)
        except ValueError:
            rel = f["path"]
        print(f"  [{status}]  {rel}")

    print()
    print(f"  Summary: {new_count} to create, {skip_count} already exist")
    print()


def create_structure(mod: str, version: int, folders: list[dict], dry_run: bool):
    if dry_run:
        print("  DRY RUN — no folders created.")
        return

    created, skipped = [], []
    for f in folders:
        if f["exists"]:
            skipped.append(f["path"])
        else:
            f["path"].mkdir(parents=True, exist_ok=True)
            (f["path"] / ".gitkeep").touch()
            created.append(f["path"])

    base = get_module_version_path(mod, version)
    manifest_path = base / "manifest.json"
    manifest = build_manifest(mod, version)
    manifest["created_at"] = datetime.now().isoformat()
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    set_current_version(mod, version)

    try:
        manifest_rel = manifest_path.relative_to(REPO_BASE_PATH)
    except ValueError:
        manifest_rel = manifest_path

    print("─" * 62)
    print(f"  ✓ Created  : {len(created)} folders")
    print(f"  ⚠ Skipped  : {len(skipped)} (already exist)")
    print(f"  ✓ Manifest : {manifest_rel}")
    print(f"  ✓ Registry : modules-registry.json updated (v{version})")
    print("─" * 62)
    print()
    print(f"  Structure ready: [{mod}] v{version}")
    print(f"  Next step : python agent2_archive.py --module {mod}")
    print()


def list_modules():
    registry = load_modules_registry()
    all_mods = set(KNOWN_MODULES) | set(registry.get("modules", {}).keys())

    print()
    print("═" * 62)
    print("  KNOWN MODULES")
    print("═" * 62)
    if not all_mods:
        print("  (none registered yet)")
    for mod in sorted(all_mods):
        entry = registry.get("modules", {}).get(mod, {})
        version = entry.get("current_version", "—")
        desc = entry.get("description", "")
        static_tag = " [static]" if mod in KNOWN_MODULES else ""
        print(f"  {mod:<12} v{version}{static_tag}  {desc}")
    print("═" * 62)
    print()


def main():
    parser = argparse.ArgumentParser(description="Create backend governance folder structure for a module.")
    parser.add_argument("--module", "-m", help="Module code (module code).")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without creating anything.")
    parser.add_argument("--auto-register", action="store_true", help="Automatically register an unknown module.")
    parser.add_argument("--description", default="", help="Description for --auto-register.")
    parser.add_argument("--new-version", action="store_true", help="Create the next version for an existing module.")
    parser.add_argument("--list-modules", action="store_true", help="List all known modules and exit.")

    args = parser.parse_args()

    if args.list_modules:
        list_modules()
        sys.exit(0)

    if not args.module:
        print("\n  ERROR: --module is required (or use --list-modules).\n")
        sys.exit(1)

    # FINDING-22a — a dry run must be strictly read-only. validate_module with
    # auto_register=True WRITES modules-registry.json (and publishes the shared
    # copy). So under --dry-run we never register: we validate read-only, and if
    # the module is unknown but --auto-register was requested, we only NORMALISE
    # the code and note that a live run would register it — no disk write.
    if args.dry_run:
        try:
            mod = validate_module(args.module, auto_register=False, description=args.description)
        except ValueError as e:
            if args.auto_register:
                mod = args.module.upper().strip()
                print(f"\n  ⓘ DRY RUN: module '{mod}' is not registered yet — a LIVE run "
                      f"with --auto-register would register it now. (Nothing written.)")
            else:
                print(f"\n  ERROR: {e}\n")
                sys.exit(1)
    else:
        try:
            mod = validate_module(args.module, auto_register=args.auto_register, description=args.description)
        except ValueError as e:
            print(f"\n  ERROR: {e}\n")
            sys.exit(1)

    if args.new_version:
        version = get_next_version(mod)
    else:
        registry = load_modules_registry()
        entry = registry.get("modules", {}).get(mod)
        version = (entry.get("current_version") if entry else None) or 1

    folders = plan_structure(mod, version)
    print_plan(mod, version, folders, args.dry_run)

    if not args.dry_run:
        confirm = input("  Proceed? [y/N]: ").strip().lower()
        if confirm != "y":
            print("\n  Cancelled — no changes made.\n")
            sys.exit(0)
        print()

    create_structure(mod, version, folders, args.dry_run)


if __name__ == "__main__":
    main()
