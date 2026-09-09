"""
ERP Governance Tools — Journey Loader (AMEND-PIPELINE-V5 §2)
=============================================================
Turns a module's JOURNEY LEDGER (journey-{mod}.json — one file per module,
all versions) into an actionable download plan for ONE module+version, and
verifies the result. Built to sit in front of process-project-files.md
(both tracks) so a whole module version is loaded once, in one pass.

Transfer is done by the Drive CONNECTOR (the orchestrating agent), not by
this script: it has no Drive credentials and needs none. The split is
deterministic-vs-transfer:
    this script  → which files, which version, expected names, verification
    connector    → the actual bytes (download_file_content per drive_file_id)

Usage:
    journey_loader.py --ledger journey-org.json --module ORG --version 2 --plan
        → prints a JSON download plan: [{drive_file_id, drive_url, filename,
          dest}] for the connector to execute into --dest (default ./).
    journey_loader.py --ledger ... --module ORG --version latest --plan
    journey_loader.py --ledger ... --module ORG --version 2 --dest <dir> --verify
        → exit 0 if every UPLOADED artifact of that version is present in
          --dest under its exact ledger filename; exit 1 listing what's missing.
    journey_loader.py --ledger ... --module ORG --version 2 --append row.json
        → appends one artifact row (validated against config.LEDGER_ROW_KEYS)
          — used by Stage-2 tooling for package receipts.
    journey_loader.py --ledger ... --module ORG --version 2 --open  [--engine P1] [--change-set CS-ORG-001]
    journey_loader.py --ledger ... --module ORG --version 2 --close
        → START / END markers for a version.

No filename is spelled here: names come from the ledger rows, which the
engines wrote from config.ARTIFACT_FILES. No hardcoded paths.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (  # noqa: E402
    new_ledger, open_ledger_version, close_ledger_version,
    validate_ledger_row, ledger_filename, legacy_name_map,
)


def load_ledger(path: Path, mod: str) -> dict:
    if not path.exists():
        return new_ledger(mod)
    with open(path, "r", encoding="utf-8") as fh:
        ledger = json.load(fh)
    if ledger.get("module", "").upper() != mod.upper():
        raise SystemExit(f"  ERROR: ledger is for module {ledger.get('module')!r}, not {mod!r}.")
    return ledger


def save_ledger(path: Path, ledger: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=2, ensure_ascii=False)


def resolve_version(ledger: dict, version: str) -> int:
    versions = sorted(int(v) for v in ledger.get("versions", {}))
    if version == "latest":
        if not versions:
            raise SystemExit("  ERROR: ledger has no versions yet.")
        return versions[-1]
    v = int(version)
    if v not in versions:
        raise SystemExit(f"  ERROR: version v{v} not in ledger (has: {versions or 'none'}).")
    return v


def current_rows(section: dict) -> list[dict]:
    """Latest UPLOADED row per filename (a re-upload SUPERSEDES the earlier one)."""
    latest: dict[str, dict] = {}
    for row in section.get("artifacts", []):
        if row.get("status") == "UPLOADED":
            latest[row["filename"]] = row
    return list(latest.values())


def build_plan(ledger: dict, version: int, dest: Path) -> list[dict]:
    section = ledger["versions"][str(version)]
    return [
        {
            "drive_file_id": r.get("drive_file_id"),
            "drive_url": r.get("drive_url"),
            "repo_path": r.get("repo_path"),
            "transfer": "connector" if r.get("drive_file_id") else "already-in-repo",
            "filename": r["filename"],
            "engine": r.get("engine"),
            "stage": r.get("stage"),
            "dest": str(dest / r["filename"]),
        }
        for r in current_rows(section)
    ]


def verify(ledger: dict, version: int, dest: Path) -> tuple[list[str], list[str]]:
    present, missing = [], []
    for r in current_rows(ledger["versions"][str(version)]):
        target = Path(r["repo_path"]) if r.get("repo_path") else dest / r["filename"]
        (present if target.exists() else missing).append(r["filename"])
    return present, missing


def main():
    ap = argparse.ArgumentParser(description="Journey ledger → download plan / verify / append.")
    ap.add_argument("--ledger", required=True, help="Path to journey-{mod}.json (downloaded via the connector).")
    ap.add_argument("--module", "-m", required=True)
    ap.add_argument("--version", "-v", default="latest", help="Version number or 'latest'.")
    ap.add_argument("--dest", "-d", default=".", help="Folder the connector downloads into / to verify.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true", help="Print the JSON download plan.")
    g.add_argument("--verify", action="store_true", help="Check every artifact landed in --dest.")
    g.add_argument("--append", metavar="ROW_JSON", help="Append one artifact row (JSON file or inline JSON).")
    g.add_argument("--append-receipts", metavar="RECEIPT_JSON",
                   help="Append every row in a Stage-2 split receipt (written by agent3 stage 5).")
    g.add_argument("--open", action="store_true", help="START module vN (create the version section).")
    g.add_argument("--backfill", metavar="LISTING_JSON",
                   help="DRIVE MIGRATION: build the v[--version] ledger for a PRE-V5 module from a "
                        "connector listing of its existing Drive files, and print the rename plan "
                        "(old un-qualified name → V5 name) for the connector to apply.")
    g.add_argument("--close", action="store_true", help="END module vN (freeze the version section).")
    ap.add_argument("--engine", default="tooling", help="With --open/--append: the recording engine.")
    ap.add_argument("--change-set", default=None, help="With --open: CS-ID for an IFA version.")
    args = ap.parse_args()

    mod = args.module.upper()
    ledger_path = Path(args.ledger).expanduser().resolve()
    ledger = load_ledger(ledger_path, mod)
    now = datetime.now().isoformat(timespec="seconds")

    if args.backfill:
        listing = json.loads(Path(args.backfill).read_text(encoding="utf-8"))
        files = listing["files"] if isinstance(listing, dict) else listing
        v = int(args.version) if args.version != "latest" else 1
        legacy = legacy_name_map(mod)
        section = open_ledger_version(ledger, v, "backfill", started_at=now)
        renames, rows = [], []
        for f in files:                       # {id, name, webViewLink, stage?}
            name = f["name"]
            new_name = legacy.get(name, name) # already-qualified names pass through
            if new_name != name:
                renames.append({"drive_file_id": f["id"], "from": name, "to": new_name})
            row = {"engine": f.get("engine", "backfill"), "stage": f.get("stage", ""),
                   "filename": new_name, "artifact": new_name.rsplit("-", 1)[0],
                   "drive_file_id": f["id"], "drive_url": f.get("webViewLink"),
                   "recorded_at": now, "status": "UPLOADED"}
            problems = validate_ledger_row(row)
            if problems:
                raise SystemExit(f"  ERROR: {name}: " + "; ".join(problems))
            rows.append(row)
        section["artifacts"].extend(rows)
        section["status"] = "CLOSED"; section["ended_at"] = now   # a built module is a closed v1
        save_ledger(ledger_path, ledger)
        print(json.dumps({"module": mod, "version": v, "ledger": str(ledger_path),
                          "rows": len(rows), "renames": renames}, indent=2, ensure_ascii=False))
        return

    if args.open:
        v = int(args.version) if args.version != "latest" else (
            max((int(k) for k in ledger["versions"]), default=0) + 1)
        open_ledger_version(ledger, v, args.engine, args.change_set, started_at=now)
        save_ledger(ledger_path, ledger)
        print(f"  START module {mod} v{v}  → {ledger_filename(mod)}")
        return

    version = resolve_version(ledger, args.version)
    section = ledger["versions"][str(version)]

    if args.close:
        close_ledger_version(ledger, version, ended_at=now)
        save_ledger(ledger_path, ledger)
        print(f"  END module {mod} v{version}  ({len(current_rows(section))} artifacts)")
        return

    if args.append_receipts:
        rows = json.loads(Path(args.append_receipts).read_text(encoding="utf-8"))["rows"]
        added = 0
        for row in rows:
            row.setdefault("recorded_at", now); row.setdefault("status", "UPLOADED")
            problems = validate_ledger_row(row)
            if problems:
                raise SystemExit(f"  ERROR: invalid receipt row {row.get('filename')!r} — " + "; ".join(problems))
            for prev in section["artifacts"]:
                if prev["filename"] == row["filename"] and prev["status"] == "UPLOADED":
                    prev["status"] = "SUPERSEDED"
            section["artifacts"].append(row); added += 1
        save_ledger(ledger_path, ledger)
        print(f"  + {added} package rows from receipt → v{version}")
        return

    if args.append:
        raw = args.append
        row = json.loads(Path(raw).read_text(encoding="utf-8")) if Path(raw).exists() else json.loads(raw)
        row.setdefault("engine", args.engine)
        row.setdefault("recorded_at", now)
        row.setdefault("status", "UPLOADED")
        problems = validate_ledger_row(row)
        if problems:
            raise SystemExit("  ERROR: invalid row — " + "; ".join(problems))
        for prev in section["artifacts"]:
            if prev["filename"] == row["filename"] and prev["status"] == "UPLOADED":
                prev["status"] = "SUPERSEDED"
        section["artifacts"].append(row)
        save_ledger(ledger_path, ledger)
        print(f"  + {row['filename']}  ({row['engine']})  → v{version}")
        return

    dest = Path(args.dest).expanduser().resolve()

    if args.plan:
        if section["status"] != "CLOSED":
            print(f"  ⚠ v{version} is still OPEN (journey not ended) — plan may be partial.", file=sys.stderr)
        plan = build_plan(ledger, version, dest)
        print(json.dumps({"module": mod, "version": version, "dest": str(dest),
                          "count": len(plan), "files": plan}, indent=2, ensure_ascii=False))
        return

    if args.verify:
        present, missing = verify(ledger, version, dest)
        print(f"  VERIFY {mod} v{version} in {dest}")
        print(f"  present : {len(present)}")
        for f in present:
            print(f"    ✓ {f}")
        if missing:
            print(f"  missing : {len(missing)}")
            for f in missing:
                print(f"    ✗ {f}")
            sys.exit(1)
        print("  all artifacts present ✓")


if __name__ == "__main__":
    main()
