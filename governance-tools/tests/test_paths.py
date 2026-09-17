"""Project-specific generated content (`domain-profile.md`, `project-registry.md`,
`modules/`, `decisions/`) consolidates under ONE folder named after the active
profile's own identity (`profile.identity.id`) — never a fixed literal like
`project/`. `factory.yaml -> paths.*` carries this as a `{profile_id}` token,
resolved at runtime by `FactoryConfig.paths` (config.py); nothing here pins a name
to either profile — both are read back from `CFG.profile.id`.

That folder lives in the SHARED repo, not this one: governance is read by every
repo that builds from it, so it is written where all of them can read it instead
of copied to each. Which path keys move is declared in `paths.external` and
resolved by `config.dir()` — so these tests assert against the root that owns
the key, never against `CFG.root` directly.
"""
from __future__ import annotations

import yaml

from config import CFG

from test_agnostic import TOY


def test_project_paths_nest_under_the_active_profile_id(factory_root, mod):
    root = CFG.dir("domain")
    assert root == CFG.repo_checkout(CFG.external["repo"]) / CFG.profile.id
    assert root.name == CFG.profile.id          # the folder is named by the profile
    assert CFG.root not in (root, *root.parents) or root.is_relative_to(CFG.root)
    # platform shares the same root as domain (both are the entry-gate + bootstrap
    # artifacts of ONE project instance)
    assert CFG.dir("platform") == root
    # modules/ and decisions/ nest inside it, not beside it
    assert CFG.dir("modules") == root / "modules"
    assert CFG.dir("decisions") == root / "decisions"
    assert CFG.modules_root() == root / "modules"
    assert CFG.module_root(mod) == root / "modules" / mod.upper()
    assert CFG.decisions_dir(mod) == root / "decisions" / mod.upper()
    # no unresolved template token leaked through
    assert all("{profile_id}" not in v for v in CFG.paths.values() if isinstance(v, str))


def test_a_differently_identified_profile_gets_a_differently_named_root(factory_root):
    erp_root = CFG.dir("domain")
    assert erp_root.name == "erp"

    (factory_root / CFG.paths["profiles"] / "toy.yaml").write_text(yaml.safe_dump(TOY, sort_keys=False), encoding="utf-8")
    CFG.reload(profile_id="toy")
    toy_root = CFG.dir("domain")

    assert toy_root.name == "toy"
    assert toy_root != erp_root
    assert CFG.dir("modules") == toy_root / "modules"
    assert CFG.dir("decisions") == toy_root / "decisions"
    CFG.reload()


def test_generated_content_actually_lands_under_the_named_root(factory_root, mod):
    """Not just path arithmetic — files written through the real artifact/module
    helpers land on disk under the profile-named folder, for whichever profile
    is active."""
    root = CFG.dir("domain")
    root.mkdir(parents=True, exist_ok=True)
    (root / "domain-profile.md").write_text("stub\n", encoding="utf-8")
    CFG.decisions_dir(mod).mkdir(parents=True, exist_ok=True)
    (CFG.decisions_dir(mod) / "ADR-X-001.md").write_text("Status: OPEN\n", encoding="utf-8")
    CFG.module_root(mod).mkdir(parents=True, exist_ok=True)

    assert (root / "domain-profile.md").exists()
    assert (root / "decisions" / mod.upper() / "ADR-X-001.md").exists()
    assert (root / "modules" / mod.upper()).is_dir()
    # nothing spilled back out to the old fixed top-level names
    assert not (CFG.root / "project").exists()
    assert not (CFG.root / "modules").exists()
    assert not (CFG.root / "decisions").exists()
    # nor back into this repo under the profile's own name: the factory writes
    # governance, it does not keep a copy of it
    assert not (CFG.root / CFG.profile.id).exists()


# ── which repository owns a path (paths.external) ────────────────────────────

def test_dir_routes_an_external_key_to_the_owning_repo(factory_root):
    """`paths.external` is the ONE statement of the factory/shared boundary:
    a key listed there resolves against the shared checkout, every other key
    against this repo. Neither root is decided in code."""
    import yaml
    fac = factory_root / "factory.yaml"
    data = yaml.safe_load(fac.read_text(encoding="utf-8"))
    data["paths"]["external"] = {"repo": "shared", "keys": ["modules"]}
    fac.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    cfg = CFG.reload()

    shared = cfg.repo_checkout("shared")
    assert cfg.dir("modules") == shared / cfg.paths["modules"]
    assert cfg.dir("engines") == cfg.root / cfg.paths["engines"]
    # everything built on modules_root follows, with no further wiring
    assert cfg.modules_root() == shared / cfg.paths["modules"]
    assert cfg.module_root("ORG").parent == shared / cfg.paths["modules"]
    CFG.reload()


def test_an_empty_external_list_leaves_every_path_here(factory_root):
    import yaml
    fac = factory_root / "factory.yaml"
    data = yaml.safe_load(fac.read_text(encoding="utf-8"))
    data["paths"]["external"] = {"repo": "shared", "keys": []}
    fac.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    cfg = CFG.reload()
    for key, rel in cfg.paths.items():
        if isinstance(rel, str):
            assert cfg.dir(key) == cfg.root / rel
    CFG.reload()


# ── factory.yaml's own cross-table invariants (F-12) ─────────────────────────

def test_a_track_naming_an_undeclared_repo_is_a_finding(factory_root):
    """`tracks` and `repos` are different tables — `repos.shared` is in one and
    not the other. A track's repo is therefore named, and the name is checked,
    instead of the two keys being assumed identical and failing as a KeyError."""
    import lint
    cfg = CFG.reload()
    assert lint.scan_config(cfg) == []

    cfg.data["tracks"][next(iter(cfg.tracks))]["repo"] = "no-such-repo"
    found = lint.scan_config(cfg)
    assert len(found) == 1
    assert "no-such-repo" in found[0].message
    assert all(r in found[0].message for r in cfg.repos)   # names both tables
    CFG.reload()


def test_an_external_key_that_is_not_a_path_is_a_finding(factory_root):
    import lint
    cfg = CFG.reload()
    cfg.data["paths"]["external"] = {"repo": "shared", "keys": ["module"]}
    found = lint.scan_config(cfg)
    assert len(found) == 1 and "not a path" in found[0].message

    cfg.data["paths"]["external"]["keys"] = ["not-a-key-at-all"]
    found = lint.scan_config(cfg)
    assert len(found) == 1 and "not a declared path key" in found[0].message

    cfg.data["paths"]["external"] = {"repo": "not-a-repo", "keys": []}
    found = lint.scan_config(cfg)
    assert len(found) == 1 and "not-a-repo" in found[0].message
    CFG.reload()
