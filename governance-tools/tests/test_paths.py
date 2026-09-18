"""Two roots. Tool paths resolve against the factory checkout; every key in
`paths.external.keys` — the profiles, the analysis, the decisions, the
overview — resolves against the PROJECT checkout named by
`GOV_PROJECT_CHECKOUT`. Which is which is declared in factory.yaml and read by
`config.dir()`; nothing here pins a name to either root. Switching projects is
one variable.
"""
from __future__ import annotations

import pathlib
import shutil

import yaml

from config import CFG
from conftest import FIXTURE_PROJECT, git_init
from test_agnostic import TOY


def test_project_paths_resolve_on_the_project_checkout(factory_root, project_root, mod):
    for key in CFG.external["keys"]:
        assert CFG.dir(key) == project_root / CFG.paths[key], key
        assert not CFG.dir(key).is_relative_to(CFG.root)
    assert CFG.modules_root() == project_root / CFG.paths["modules"]
    assert CFG.module_root(mod) == CFG.modules_root() / mod.upper()
    assert CFG.decisions_dir(mod) == project_root / CFG.paths["decisions"] / mod.upper()
    assert CFG.profiles_dir() == project_root / CFG.paths["profiles"]
    # tool paths stay in the tool
    for key in ("engines", "shared", "reviewers", "commands", "tools", "templates", "schema"):
        assert CFG.dir(key) == CFG.root / CFG.paths[key]
    # no unresolved template token leaked through
    assert all("{" not in v for v in CFG.paths.values() if isinstance(v, str))


def test_switching_the_project_is_one_variable(factory_root, tmp_path, monkeypatch):
    """The same tool checkout drives another project repo when the variable
    points at it: a different profile, a different content root, nothing in
    the tool changed."""
    first = CFG.project_checkout()
    first_id = CFG.profile_id
    other = tmp_path / "other-project"
    shutil.copytree(FIXTURE_PROJECT, other)
    (other / CFG.paths["profiles"] / "toy.yaml").write_text(yaml.safe_dump(TOY, sort_keys=False), encoding="utf-8")
    pj = other / CFG.project["file"]
    pj.write_text(pj.read_text(encoding="utf-8").replace(f"profile: {first_id}", "profile: toy"), encoding="utf-8")
    git_init(other)

    monkeypatch.setenv(CFG.project["checkout_env"], str(other))
    cfg = CFG.reload()
    assert cfg.project_checkout() == other.resolve() and cfg.project_checkout() != first
    assert cfg.profile_id == "toy" and cfg.profile.id == "toy"
    assert cfg.dir("modules") == other.resolve() / cfg.paths["modules"]
    assert cfg.root == factory_root.resolve()          # the tool did not move
    monkeypatch.setenv(CFG.project["checkout_env"], str(first))
    assert CFG.reload().profile_id == first_id


def test_generated_content_actually_lands_in_the_project_repo(factory_root, project_root, mod):
    """Not just path arithmetic — files written through the real helpers land
    in the project checkout, and nothing spills into the tool tree."""
    (CFG.dir("domain")).mkdir(parents=True, exist_ok=True)
    (CFG.dir("domain") / "domain-profile.md").write_text("stub\n", encoding="utf-8")
    CFG.decisions_dir(mod).mkdir(parents=True, exist_ok=True)
    (CFG.decisions_dir(mod) / "ADR-X-001.md").write_text("Status: OPEN\n", encoding="utf-8")
    CFG.module_root(mod).mkdir(parents=True, exist_ok=True)
    assert (project_root / CFG.paths["domain"] / "domain-profile.md").exists()
    assert (project_root / CFG.paths["decisions"] / mod.upper() / "ADR-X-001.md").exists()
    assert (project_root / CFG.paths["modules"] / mod.upper()).is_dir()
    for key in CFG.external["keys"]:
        if key != "profiles":                          # the tool keeps the SCHEMA under the same folder name
            assert not (CFG.root / CFG.paths[key]).exists(), key
    assert not (CFG.root / "analysis").exists()


def test_the_project_file_names_the_profile_and_the_env_overrides_it(factory_root, monkeypatch):
    assert CFG.profile_id == CFG.project_data["profile"]
    (CFG.profiles_dir() / "toy.yaml").write_text(yaml.safe_dump(TOY, sort_keys=False), encoding="utf-8")
    monkeypatch.setenv("GOV_PROFILE", "toy")
    assert CFG.reload().profile_id == "toy"
    monkeypatch.delenv("GOV_PROFILE")
    assert CFG.reload().profile_id == CFG.project_data["profile"]


def test_a_project_without_a_profile_says_so(factory_root, tmp_path, monkeypatch):
    import pytest
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv(CFG.project["checkout_env"], str(empty))
    cfg = CFG.reload()
    assert cfg.project_data == {}
    with pytest.raises(FileNotFoundError, match="no active profile"):
        _ = cfg.profile_id
    # paths that need no profile still resolve — a project can be scaffolded there
    assert cfg.dir("modules") == empty.resolve() / cfg.paths["modules"]


# ── which repository owns a path (paths.external) ────────────────────────────

def test_dir_routes_an_external_key_to_the_project_and_the_rest_here(factory_root):
    """`paths.external.keys` is the ONE statement of the tool/project boundary."""
    fac = factory_root / "factory.yaml"
    data = yaml.safe_load(fac.read_text(encoding="utf-8"))
    data["paths"]["external"] = {"keys": ["modules", "profiles"]}
    fac.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    cfg = CFG.reload()
    assert cfg.dir("modules") == cfg.project_checkout() / cfg.paths["modules"]
    assert cfg.dir("engines") == cfg.root / cfg.paths["engines"]
    assert cfg.dir("decisions") == cfg.root / cfg.paths["decisions"]      # moved back by the declaration alone
    assert cfg.modules_root() == cfg.project_checkout() / cfg.paths["modules"]
    CFG.reload()


# ── factory.yaml's own cross-table invariants (F-12) ─────────────────────────

def test_a_track_naming_an_undeclared_repo_is_a_finding(factory_root):
    """A track's repo is a key of the PROJECT's repos — named, checked, never
    assumed to equal the track's own key."""
    import lint
    cfg = CFG.reload()
    assert lint.scan_config(cfg) == []
    cfg.data["tracks"][next(iter(cfg.tracks))]["repo"] = "no-such-repo"
    found = lint.scan_config(cfg)
    assert len(found) == 1
    assert "no-such-repo" in found[0].message
    assert all(r in found[0].message for r in cfg.repos)   # names the project's table
    CFG.reload()


def test_a_track_or_input_naming_an_undeclared_partition_is_a_finding(factory_root):
    import lint
    cfg = CFG.reload()
    track = next(iter(cfg.tracks))
    cfg.data["tracks"][track]["delivery"] = "nowhere"
    assert any("nowhere" in f.message for f in lint.scan_config(cfg))
    cfg = CFG.reload()
    cfg.data["inputs"][next(iter(cfg.inputs))]["partition"] = "nowhere"
    assert any("nowhere" in f.message for f in lint.scan_config(cfg))
    cfg = CFG.reload()
    # a delivery partition a track writes is a contradiction: split writes there
    cfg.data["tracks"][track]["delivery"] = cfg.tracks[track]["partition"]
    assert any("delivery" in f.path for f in lint.scan_config(cfg))
    CFG.reload()


def test_an_external_key_that_is_not_a_path_is_a_finding(factory_root):
    import lint
    cfg = CFG.reload()
    cfg.data["paths"]["external"] = {"keys": ["module"]}
    found = lint.scan_config(cfg)
    assert len(found) == 1 and "not a path" in found[0].message
    cfg.data["paths"]["external"]["keys"] = ["not-a-key-at-all"]
    found = lint.scan_config(cfg)
    assert len(found) == 1 and "not a declared path key" in found[0].message
    CFG.reload()


# ── partitions of the project repo ───────────────────────────────────────────

def test_a_partition_is_per_module_by_its_template_not_its_name(factory_root):
    import gov
    parts = gov._partitions()
    assert parts, "the project declares no partitions"
    for name, template in parts.items():
        assert gov._per_module(name) == ("{MOD}" in template)
    for name in parts:
        p = gov._shared_dir(name, "ORG" if gov._per_module(name) else None)
        assert "{" not in str(p), f"{name} resolved to {p}"
        assert p.is_relative_to(CFG.project_checkout())


def test_the_project_checkout_is_never_named_in_code(factory_root):
    """Where the project lives is `project.checkout_env`/`checkout_default` and
    nothing else, so any project repo is driven by the same tool."""
    import gov, dispatch, config
    for m in (gov, dispatch, config):
        src = pathlib.Path(m.__file__).read_text(encoding="utf-8")
        assert CFG.project["checkout_default"].strip("./") not in src, f"the project checkout is typed in {m.__name__}"


def test_a_partition_declares_who_writes_it(factory_root):
    """The ownership table is read, not merely documented: `writer` is what stops
    a factory regeneration from clearing a path a track wrote — and the DEEPEST
    partition decides, so a delivery partition nested in a track's is the factory's."""
    for part in CFG.partitions():
        w = CFG.partition_writer(part)
        assert w == CFG.FACTORY_WRITER or w in CFG.tracks, \
            f"{part} names writer '{w}', which is neither this factory nor a track"
    foreign = set(CFG.foreign_partitions("SEC"))
    assert foreign, "no partition is protected from the factory — the table says nothing"
    for part in CFG.partitions():
        d = CFG.partition_dir(part, "SEC" if CFG.partition_is_per_module(part) else None)
        assert (d in foreign) == (CFG.partition_writer(part) != CFG.FACTORY_WRITER and CFG.partition_is_per_module(part)), part
    for track in CFG.tracks:
        delivery = CFG.partition_dir(CFG.track_delivery(track), "SEC")
        own = CFG.partition_dir(CFG.track_partition(track), "SEC")
        assert CFG.partition_of(delivery / "x.md", "SEC") == CFG.track_delivery(track)
        assert CFG.partition_of(own / "execution-state.json", "SEC") == CFG.track_partition(track)
    assert CFG.partition_of(CFG.root / "engines" / "x.md", "SEC") is None


def test_packages_are_delivered_into_the_track_partition(factory_root, mod):
    """The split writes where the consumer reads: the track's delivery
    partition, versioned like the module (v1 = the partition, vN = its version
    folder) — never a copy in the consumer's own tree."""
    for track in CFG.tracks:
        for plan, pkg in CFG.tracks[track]["packages"].items():
            base = CFG.partition_dir(CFG.track_delivery(track), mod)
            assert CFG.packages_dir(mod, track, plan, 1) == base / pkg
            assert CFG.packages_dir(mod, track, plan, 2) == base / CFG.fmt(CFG.naming["version_folder"], version=2) / pkg


# ── who may SEE what (sparse checkout) ───────────────────────────────────────

def test_a_track_sees_its_own_partition_and_not_the_others(factory_root):
    """`CODEOWNERS` decides who may write; a submodule hands every consumer the
    whole repository, so sparse-checkout is the only lever on the read. The
    patterns are derived from the same declarations as everything else."""
    import gov
    per_track = {t: set(gov._sparse_patterns(t)) for t in CFG.tracks}
    for part in CFG.partitions():
        if not CFG.partition_is_per_module(part):
            continue
        pat = CFG.fmt(CFG.partitions()[part], mod="*") + "/**"
        for track in CFG.tracks:
            allowed = CFG.partition_is_readable_by(part, track)
            assert (pat in per_track[track]) == allowed, \
                f"{track} {'cannot see' if allowed else 'can see'} {part}"


def test_a_stage_that_names_a_track_is_hidden_from_the_other(factory_root):
    import gov
    per_track = {t: set(gov._sparse_patterns(t)) for t in CFG.tracks}
    tracked = [s for s in CFG.all_stages() if s.track]
    assert tracked, "no stage names a track — nothing is being separated"
    for s in tracked:
        pat = f"{CFG.paths['modules']}/*/{s.folder}/**"
        assert pat in per_track[s.track]
        for other in CFG.tracks:
            if other != s.track:
                assert pat not in per_track[other], f"{other} can see {s.id}"
    # and the analysis partition as a whole is not handed to anyone: it is read stage by stage
    whole = CFG.fmt(CFG.partitions()["analysis"], mod="*") + "/**"
    assert all(whole not in p for p in per_track.values())


def test_shared_analysis_stays_visible_to_everyone(factory_root):
    """P0…P2 name no track: they are the analysis both sides implement against.
    Narrowing must not hide the thing the plan is derived from."""
    import gov
    per_track = {t: set(gov._sparse_patterns(t)) for t in CFG.tracks}
    for s in CFG.all_stages():
        if s.track is None:
            pat = f"{CFG.paths['modules']}/*/{s.folder}/**"
            assert all(pat in p for p in per_track.values()), f"{s.id} hidden from someone"
    assert all(CFG.project["file"] in p for p in per_track.values())
