"""
ERP Governance Tools — Agent 1: Frontend Structure Creator
=============================================================
Creates the canonical frontend folder structure for a module.

Usage:
    python agent1_create_structure.py --module MODCODE
    python agent1_create_structure.py --module MODCODE --dry-run
    python agent1_create_structure.py --list-modules

This tool has no representation of "backend" anywhere except the one
sanctioned read of backend's modules-registry.json (to validate module
identity — see config.py). There is no auto-register here: this repo
never registers a module, only backend does. There is no
--frontend-only flag (unnecessary — this tool only ever does one
thing), no --track flag, and no module-name denylist of any kind.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    REPO_BASE_PATH,
    MODULE_STRUCTURE,
    PACKAGES_STRUCTURE,
    FRONTEND_STAGES,
    get_module_path,
    validate_module,
    build_manifest,
    load_backend_registry,
    get_current_version,
    get_next_version,
)


def plan_structure(mod: str, version: int) -> list[dict]:
    base = get_module_path(mod, version)
    folders = []

    for stage in FRONTEND_STAGES:
        p = base / MODULE_STRUCTURE[stage]
        folders.append({"path": p, "label": stage})

    for artifact, subs in PACKAGES_STRUCTURE.items():
        for sub in subs:
            p = base / "packages" / artifact / sub
            folders.append({"path": p, "label": f"packages/{artifact}/{sub}"})

    for f in folders:
        f["exists"] = f["path"].exists()

    return folders


def print_plan(mod: str, version: int, folders: list[dict], dry_run: bool):
    base = get_module_path(mod, version)
    new_count  = sum(1 for f in folders if not f["exists"])
    skip_count = sum(1 for f in folders if f["exists"])

    print()
    print("═" * 62)
    print(f"  AGENT 1 — Frontend Structure Creator")
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

    base = get_module_path(mod, version)
    manifest_path = base / "manifest.json"
    manifest = build_manifest(mod, version)
    manifest["created_at"] = datetime.now().isoformat()
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    print("─" * 62)
    print(f"  ✓ Created  : {len(created)} folders")
    print(f"  ⚠ Skipped  : {len(skipped)} (already exist)")
    print(f"  ✓ Manifest : {manifest_path.relative_to(REPO_BASE_PATH)}")
    print("─" * 62)
    print()
    print(f"  Structure ready: [{mod}] v{version}")
    print(f"  Next step : python agent2_archive.py --module {mod}")
    print()


def list_modules():
    registry = load_backend_registry()
    mods = sorted(registry.get("modules", {}).keys())

    print()
    print("═" * 62)
    print("  MODULES (from backend's registry — read-only)")
    print("═" * 62)
    if not mods:
        print("  (none registered in backend yet)")
    for mod in mods:
        print(f"  {mod}")
    print("═" * 62)
    print()


def main():
    parser = argparse.ArgumentParser(description="Create frontend governance folder structure for a module.")
    parser.add_argument("--module", "-m", help="Module code (module code) — must already be registered in backend.")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without creating anything.")
    parser.add_argument("--new-version", action="store_true",
                        help="Create the NEXT frontend version for an existing module "
                             "(modules/[MOD]/v2, v3, …) alongside the frozen prior one. "
                             "The version is derived from THIS repo's own folders — the "
                             "frontend never writes the backend-owned registry.")
    parser.add_argument("--list-modules", action="store_true", help="List modules known to backend and exit.")

    args = parser.parse_args()

    if args.list_modules:
        list_modules()
        sys.exit(0)

    if not args.module:
        print("\n  ERROR: --module is required (or use --list-modules).\n")
        sys.exit(1)

    try:
        mod = validate_module(args.module)
    except ValueError as e:
        print(f"\n  ERROR: {e}\n")
        sys.exit(1)

    # Version resolution (self-contained — filesystem-derived, no registry write):
    #   --new-version → the next local version (v1→v2→v3…), prior version frozen.
    #   otherwise     → the current local version (v1 for a brand-new module).
    version = get_next_version(mod) if args.new_version else get_current_version(mod)

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
