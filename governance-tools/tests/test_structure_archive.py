"""Structure (m), archive (n) and versions (o) — all through CFG path helpers."""
from __future__ import annotations

import json

from config import CFG
from toolkit import archive, build_manifest, ensure_structure, load_manifest, planned_folders
from toolkit.common import flat_plan, module_stages, plan_key, track_plans


def _has_stage_folder(root):
    return any((root / s.folder).is_dir() for s in CFG.all_stages())


# ── (m) structure ────────────────────────────────────────────────────────────

def test_structure_creates_stage_and_package_folders(factory_root, mod):
    created = ensure_structure(mod, 1)
    root = CFG.version_root(mod, 1)
    assert root == CFG.module_root(mod)                       # v1 = base folder
    module_level = {s.id for s in module_stages()}
    for st in CFG.all_stages():
        expected = st.id in module_level
        assert (root / st.folder).is_dir() == expected, st.id
        if expected:
            assert (root / st.folder / ".gitkeep").exists()
    assert any(a.dir for s in CFG.all_stages() for a in s.produces), "fixture: some stage writes platform-level"
    assert CFG.state_dir(mod, 1).is_dir() and CFG.inputs_dir(mod, 1).is_dir() and CFG.decisions_dir(mod).is_dir()
    assert set(created) == set(planned_folders(mod, 1))


def test_structure_phase_folders_only_for_per_phase_plans(factory_root, mod):
    ensure_structure(mod, 1)
    for track, plan in track_plans():
        container = CFG.packages_dir(mod, track, plan, 1)
        assert container.is_dir()
        subdirs = {p.name for p in container.iterdir() if p.is_dir()}
        if flat_plan(plan):
            assert subdirs == set(), f"{track}/{plan}: flat container must have no pre-created sub-folders"
        else:
            assert subdirs == {p.folder for p in CFG.profile.phases(track, plan)}


def test_structure_is_idempotent_and_manifest_stable(factory_root, mod):
    ensure_structure(mod, 1)
    m1 = load_manifest(mod, 1)
    assert ensure_structure(mod, 1) == []
    assert load_manifest(mod, 1) == m1


def test_manifest_contents(factory_root, mod):
    ensure_structure(mod, 1)
    m = load_manifest(mod, 1)
    assert m["module"] == mod and m["version"] == 1
    assert m["profile"] == CFG.profile_id
    assert m["markers_schema_version"] == CFG.markers["schema_version"]
    assert set(m["stages"]) == {s.id for s in module_stages()}
    keys = {plan_key(t, p) for t, p in track_plans()}
    assert set(m["packages"]) == keys and set(m["plans"]) == keys
    assert m["status"] == {"archived": False, "split": {k: False for k in keys}}
    for v in list(m["stages"].values()) + list(m["packages"].values()) + list(m["plans"].values()):
        assert not v.startswith("/"), "manifest paths are repo-relative"
        assert (factory_root / v).exists() or v.endswith(".md")


def test_structure_dry_run_creates_nothing(factory_root, mod):
    planned = ensure_structure(mod, 1, dry_run=True)
    assert planned and not CFG.module_root(mod).exists()


# ── (o) versions: v1 = base folder, vN = subfolder ──────────────────────────

def test_versions_v1_base_and_v2_subfolder(factory_root, mod):
    assert CFG.module_versions(mod) == [] and CFG.next_version(mod) == 1
    ensure_structure(mod, 1)
    assert CFG.module_versions(mod) == [1] and CFG.current_version(mod) == 1
    ensure_structure(mod, 2)
    v2 = CFG.version_root(mod, 2)
    assert v2 == CFG.module_root(mod) / CFG.fmt(CFG.naming["version_folder"], version=2)
    assert v2.is_dir() and _has_stage_folder(v2)
    assert CFG.module_versions(mod) == [1, 2] and CFG.current_version(mod) == 2
    assert load_manifest(mod, 2)["version"] == 2 and load_manifest(mod, 1)["version"] == 1
    # helpers without an explicit version follow the CURRENT version
    assert CFG.version_root(mod) == v2
    for track, plan in track_plans():
        assert CFG.packages_dir(mod, track, plan).is_relative_to(v2)
        assert CFG.packages_dir(mod, track, plan, 1).is_relative_to(CFG.module_root(mod))
        assert not CFG.packages_dir(mod, track, plan, 1).is_relative_to(v2)


def test_module_code_case_insensitive(factory_root, mod):
    ensure_structure(mod.lower(), 1)
    assert CFG.module_root(mod).is_dir()
    assert build_manifest(mod.lower(), 1)["module"] == mod.upper()


# ── (n) archive ──────────────────────────────────────────────────────────────

def _source(tmp_path, mod, stage_ids=None, body="v1"):
    src = tmp_path / "generated"
    src.mkdir(parents=True, exist_ok=True)
    written = {}
    for st in module_stages():
        if stage_ids and st.id not in stage_ids:
            continue
        for a in st.produces:
            if a.dir is None:
                (src / a.filename(mod)).write_text(f"{body} {a.artifact}", encoding="utf-8")
                written[(st.id, a.artifact)] = a.filename(mod)
    return src, written


def test_archive_copies_every_module_artifact_and_marks_manifest(factory_root, tmp_path, mod):
    src, written = _source(tmp_path, mod)
    rep = archive(mod, 1, src)
    assert rep.ok and set(rep.copied) == set(written.values())
    assert rep.skipped_missing == [] and rep.kept_existing == []
    for (sid, art), name in written.items():
        p = CFG.artifact_path(mod, sid, art, 1)
        assert p.exists() and p.name == name and p.parent == CFG.stage_dir(mod, sid, 1)
    m = load_manifest(mod, 1)
    assert m["status"]["archived"] is True and set(m["status"]["archived_files"]) == set(written.values())


def test_archive_skips_missing_with_warning_and_optional_silently(factory_root, tmp_path, mod):
    first = module_stages()[0]
    src, written = _source(tmp_path, mod, stage_ids={first.id})
    rep = archive(mod, 1, src)
    assert rep.ok and set(rep.copied) == set(written.values())
    optional = {a.filename(mod) for s in module_stages() for a in s.produces if a.optional and a.dir is None}
    assert set(rep.skipped_optional) == optional
    assert rep.skipped_missing and not (set(rep.skipped_missing) & optional)
    assert len(rep.warnings) == len(rep.skipped_missing)


def test_archive_refuses_overwrite_unless_force(factory_root, tmp_path, mod):
    first = module_stages()[0]
    src, written = _source(tmp_path, mod, stage_ids={first.id}, body="OLD")
    archive(mod, 1, src)
    src2, _ = _source(tmp_path, mod, stage_ids={first.id}, body="NEW")
    rep = archive(mod, 1, src2)
    assert rep.ok and rep.copied == [] and set(rep.kept_existing) == set(written.values())
    (sid, art), name = next(iter(written.items()))
    assert CFG.artifact_path(mod, sid, art, 1).read_text(encoding="utf-8").startswith("OLD")
    rep = archive(mod, 1, src2, force=True)
    assert set(rep.overwritten) == set(written.values())
    assert CFG.artifact_path(mod, sid, art, 1).read_text(encoding="utf-8").startswith("NEW")


def test_archive_dry_run_writes_nothing(factory_root, tmp_path, mod):
    src, written = _source(tmp_path, mod)
    rep = archive(mod, 1, src, dry_run=True)
    assert rep.dry_run and set(rep.copied) == set(written.values())
    assert not CFG.module_root(mod).exists()


def test_archive_missing_source_is_an_error(factory_root, tmp_path, mod):
    rep = archive(mod, 1, tmp_path / "nope")
    assert not rep.ok and rep.errors


def test_archive_delta_into_v2_leaves_v1_frozen(factory_root, tmp_path, mod):
    """Port of the old versioning scenario: v2 archives land under vN, v1 stays byte-identical."""
    first = module_stages()[0]
    src1, written = _source(tmp_path, mod, stage_ids={first.id}, body="V1")
    archive(mod, 1, src1)
    (sid, art), _ = next(iter(written.items()))
    v1_file = CFG.artifact_path(mod, sid, art, 1)
    v1_bytes = v1_file.read_bytes()
    ensure_structure(mod, 2)
    src2, _ = _source(tmp_path / "two", mod, stage_ids={first.id}, body="V2 delta")
    rep = archive(mod, None, src2)                         # None → current version = 2
    assert rep.version == 2 and rep.copied
    v2_file = CFG.artifact_path(mod, sid, art, 2)
    assert v2_file.exists() and v2_file != v1_file and "delta" in v2_file.read_text(encoding="utf-8")
    assert v1_file.read_bytes() == v1_bytes
    assert json.loads((CFG.version_root(mod, 2) / CFG.paths["module"]["manifest_file"]).read_text())["status"]["archived"] is True
