"""Project-specific generated content (`domain-profile.md`, `project-registry.md`,
`modules/`, `decisions/`) consolidates under ONE top-level folder named after the
active profile's own identity (`profile.identity.id`) — never a fixed literal like
`project/`. `factory.yaml -> paths.*` carries this as a `{profile_id}` token,
resolved at runtime by `FactoryConfig.paths` (config.py); nothing here pins a name
to either profile — both are read back from `CFG.profile.id`.
"""
from __future__ import annotations

import yaml

from config import CFG

from test_agnostic import TOY


def test_project_paths_nest_under_the_active_profile_id(factory_root, mod):
    root = CFG.dir("domain")
    assert root == CFG.root / CFG.profile.id
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
