"""
toolkit.structure — canonical module-version layout + manifest.json
====================================================================
    ensure_structure(mod, version)      -> list[Path]   (created paths; idempotent)
    build_manifest(mod, version)        -> dict
    write_manifest(mod, version, ...)   -> Path
    load_manifest(mod, version)         -> dict | None
    set_status(mod, version, key, value, sub=None)

Layout (every name from factory.yaml / the profile — nothing spelled here):
    <version root>/<stage folder>/            one per stage that writes into the module
    <version root>/<packages_dir>/<package>/  one per (track, plan) the profile declares
        └── <phase.folder>/                   only for plans that split per phase
    <version root>/<state_dir>/  <inputs_dir>/
    <decisions>/<MOD>/

Plans listed in `markers.rules.sub_unqualified_exempt_plans` (single-phase
plans) get a FLAT container — no pre-created sub-folders (the old toolsets
pre-created folders the splitter never wrote into: dead folders).

CLI:  python -m toolkit.structure --module ORG [--version N] [--dry-run]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from config import CFG

from .common import (flat_plan, markers_schema_version, module_stages, now_iso,
                     plan_key, plan_path_or_none, read_json, rel, rel_to, track_plans,
                     write_json)


def _manifest_path(mod: str, version: int | None) -> Path:
    return CFG.version_root(mod, version) / CFG.paths["module"]["manifest_file"]


def planned_folders(mod: str, version: int | None = None) -> list[Path]:
    """Every folder the layout requires for this module version (in order)."""
    root = CFG.version_root(mod, version)
    out: list[Path] = [root]
    out += [root / s.folder for s in module_stages()]
    for track, plan in track_plans():
        container = CFG.packages_dir(mod, track, plan, version)
        out.append(container)
        if not flat_plan(plan):
            out += [container / p.folder for p in CFG.profile.phases(track, plan)]
    out += [CFG.state_dir(mod, version), CFG.inputs_dir(mod, version), CFG.decisions_dir(mod)]
    return out


def ensure_structure(mod: str, version: int | None = None, dry_run: bool = False) -> list[Path]:
    """Create every missing folder (+ .gitkeep) and refresh manifest.json.
    Returns the paths that were newly created (empty on a second run)."""
    mod = mod.upper()
    created: list[Path] = []
    for p in planned_folders(mod, version):
        if p.exists():
            continue
        created.append(p)
        if not dry_run:
            p.mkdir(parents=True, exist_ok=True)
            (p / ".gitkeep").touch()
    if not dry_run:
        write_manifest(mod, version)
    return created


def build_manifest(mod: str, version: int | None = None, base: Path | None = None) -> dict:
    """The module version's index.

    Every path is written relative to `base` — the directory the manifest itself
    lives in (the version root by default). A manifest that spells its own
    repo-relative prefix resolves only in the repository that produced it; the same
    tree delivered into a consumer repo sits under a different prefix and every path
    in it dangles. `deliver` passes the delivered root as `base` for the same reason.

    A plan file that has not been written yet is OMITTED rather than emitted as a
    path to nothing: `status.split` already says which plans exist.
    """
    mod = mod.upper()
    version = CFG.current_version(mod) if version is None else int(version)
    root = CFG.version_root(mod, version)
    base = root if base is None else base
    plans, packages, split = {}, {}, {}
    for track, plan in track_plans():
        key = plan_key(track, plan)
        p = plan_path_or_none(mod, track, plan, version)
        if p is not None and p.exists():
            plans[key] = rel_to(p, base)
        packages[key] = rel_to(CFG.packages_dir(mod, track, plan, version), base)
        split[key] = False
    return {
        "module": mod,
        "version": version,
        "profile": CFG.profile_id,
        "markers_schema_version": markers_schema_version(),
        "paths_relative_to": "the directory holding this file",
        "root": rel_to(root, base),
        "stages": {s.id: rel_to(root / s.folder, base) for s in module_stages()},
        "plans": plans,
        "packages": packages,
        "state_dir": rel_to(CFG.state_dir(mod, version), base),
        "inputs_dir": rel_to(CFG.inputs_dir(mod, version), base),
        "decisions_dir": rel_to(CFG.decisions_dir(mod), base),
        "status": {"archived": False, "split": split},
    }


def load_manifest(mod: str, version: int | None = None) -> dict | None:
    return read_json(_manifest_path(mod.upper(), version))


def write_manifest(mod: str, version: int | None = None) -> Path:
    """Write a fresh manifest, preserving `status` and `created_at` of an
    existing one (the layout is regenerated, the history is kept)."""
    path = _manifest_path(mod.upper(), version)
    fresh = build_manifest(mod, version)
    old = read_json(path) or {}
    if old.get("status"):
        status = fresh["status"]
        status["archived"] = bool(old["status"].get("archived", False))
        for key, done in (old["status"].get("split") or {}).items():
            if key in status["split"]:
                status["split"][key] = bool(done)
        for extra in ("archived_at", "archived_files"):
            if extra in old["status"]:
                status[extra] = old["status"][extra]
    fresh["created_at"] = old.get("created_at") or now_iso()
    write_json(path, fresh)
    return path


def set_status(mod: str, version: int | None, key: str, value, sub: str | None = None) -> dict:
    """manifest.status[key] = value  (or status[key][sub] = value); creates the
    manifest when missing so archive/split can run without structure first."""
    path = _manifest_path(mod.upper(), version)
    if not path.exists():
        write_manifest(mod, version)
    data = read_json(path)
    status = data.setdefault("status", {})
    if sub is None:
        status[key] = value
    else:
        status.setdefault(key, {})[sub] = value
    write_json(path, data)
    return data


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Create the canonical module-version layout (idempotent).")
    ap.add_argument("--module", "-m", required=True)
    ap.add_argument("--version", "-v", type=int, default=None, help="default: current version (filesystem)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    mod = a.module.upper()
    version = CFG.current_version(mod) if a.version is None else a.version
    planned = planned_folders(mod, version)
    created = ensure_structure(mod, version, dry_run=a.dry_run)
    print(f"structure [{mod}] v{version} → {rel(CFG.version_root(mod, version))}  ({'DRY RUN' if a.dry_run else 'LIVE'})")
    for p in planned:
        print(f"  {'CREATE' if p in created else 'exists'}  {rel(p)}")
    print(f"  {len(created)} created, {len(planned) - len(created)} already present"
          + ("" if a.dry_run else f"; manifest: {rel(_manifest_path(mod, version))}"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
