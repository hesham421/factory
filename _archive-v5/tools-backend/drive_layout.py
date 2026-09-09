"""
ERP Governance Tools — Drive Layout (AMEND-PIPELINE-V5 §1E)
============================================================
Governs WHERE files live on Drive, from the single machine-readable source
config.DRIVE_LAYOUT. Two jobs, both deterministic (the connector moves the
bytes/metadata):

  --tree  --ctx "[CTX]" --module ORG --version N
      → every folder that must exist for that module version (mkdir plan).

  --audit LISTING.json --ctx "[CTX]" --module ORG [--version N]
      → compare a connector listing of the module's Drive tree against the
        layout and print a PLAN:
          misplaced : file is in the wrong folder / loose at a root → move
          legacy    : un-qualified pre-V5 name → rename (then place)
          unknown   : not an artifact of this ecosystem → report only
          missing   : expected folders that do not exist → create
        Exit 1 if anything is misplaced/legacy/missing (so process-project-
        files can gate on a clean layout), else 0.

Listing format (from the connector): {"files":[{"id","name","path"}], "folders":["path", …]}
  "path" = folder path RELATIVE to [CTX] with '/' separators, e.g. "ORG/P1-SRS"
  or "ORG" (module root, i.e. LOOSE) or "" ([CTX] root, LOOSE).

No filename, folder name, or path is spelled in this file.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (  # noqa: E402
    all_drive_stages, drive_folder_for_file, drive_expected_tree, drive_module_root,
    legacy_name_map, DRIVE_JOURNEY_FOLDER, DRIVE_PLATFORM_FOLDER,
)


def expected_folder_rel(mod: str, version: int, folder: str) -> str:
    """Folder path relative to [CTX] for a canonical folder name."""
    if folder == DRIVE_PLATFORM_FOLDER:
        return DRIVE_PLATFORM_FOLDER
    if folder == DRIVE_JOURNEY_FOLDER:
        return f"{mod.upper()}/{DRIVE_JOURNEY_FOLDER}"
    root = mod.upper() if version == 1 else f"{mod.upper()}/v{version}"
    return f"{root}/{folder}"


def audit(listing: dict, mod: str, version: int) -> dict:
    mod = mod.upper()
    legacy = legacy_name_map(mod)
    plan = {"module": mod, "version": version, "move": [], "rename": [],
            "unknown": [], "missing_folders": [], "ok": []}

    for f in listing.get("files", []):
        name, path = f["name"], f.get("path", "").strip("/")
        target_name = legacy.get(name, name)
        if target_name != name:
            plan["rename"].append({"drive_file_id": f["id"], "from": name, "to": target_name})
        folder = drive_folder_for_file(target_name, mod)
        if folder is None:
            plan["unknown"].append({"drive_file_id": f["id"], "name": name, "path": path})
            continue
        want = expected_folder_rel(mod, version, folder)
        if path != want:
            plan["move"].append({"drive_file_id": f["id"], "name": target_name,
                                 "from": path or "<CTX root — LOOSE>", "to": want})
        else:
            plan["ok"].append(target_name)

    have = set(p.strip("/") for p in listing.get("folders", []))
    for full in drive_expected_tree("", mod, version):
        rel = full.strip("/")
        if rel not in have:
            plan["missing_folders"].append(rel)
    return plan


def main():
    ap = argparse.ArgumentParser(description="Drive layout — expected tree / audit + move plan.")
    ap.add_argument("--ctx", default="[CTX]", help="Context root path or token (display only).")
    ap.add_argument("--module", "-m", required=True)
    ap.add_argument("--version", "-v", type=int, default=1)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tree", action="store_true")
    g.add_argument("--audit", metavar="LISTING_JSON")
    args = ap.parse_args()

    if args.tree:
        for folder in drive_expected_tree(args.ctx, args.module, args.version):
            print(folder)
        return

    listing = json.loads(Path(args.audit).read_text(encoding="utf-8"))
    plan = audit(listing, args.module, args.version)
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    dirty = plan["move"] or plan["rename"] or plan["missing_folders"]
    sys.exit(1 if dirty else 0)


if __name__ == "__main__":
    main()
