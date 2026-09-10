"""`gov.py new-domain` — reset stale project content, then start the new domain.

Exercises the full flow against an isolated git-backed root (reusing
`orch_root` from test_orchestrator.py, the same fixture the end-to-end
orchestrator dry run uses): a populated project (profiles, modules,
decisions, generated project docs, a dirtied `repos:` block) is reset down
to exactly the scoped set, `factory.yaml` instance values are restored, a
fresh profile is scaffolded, and the pipeline's first stage is dispatched —
all in one call. Nothing here pins today's stage/profile names: the target
stage is read from `CFG.stages[0]` and the module code from the `mod`
fixture / a derived code, per the active profile.
"""
from __future__ import annotations

import re

import pytest

from config import CFG
import gov
from test_orchestrator import orch_root, _git  # noqa: F401 (fixture + helper reuse)

OK, BLOCKED, AWAITING = gov.OK, gov.BLOCKED, gov.AWAITING


def _dirty_repos_block(root) -> None:
    """Simulate a previously-linked repo (via /link-repos) so the reset has something real to undo."""
    p = root / "factory.yaml"
    text = p.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^(    url:\s*)"[^"]*"', r'\1"git@example.com:org/backend.git"', text, count=1)
    text = re.sub(r'(?m)^(    checkout_default:\s*)"[^"]*"', r'\1"/abs/custom/backend"', text, count=1)
    p.write_text(text, encoding="utf-8")


def _populate(root, mod: str) -> None:
    """A populated project: modules, decisions, generated project docs, a static project doc."""
    (CFG.module_root(mod)).mkdir(parents=True, exist_ok=True)
    (CFG.module_root(mod) / "stray.txt").write_text("x\n", encoding="utf-8")
    (CFG.dir("decisions") / mod).mkdir(parents=True, exist_ok=True)
    (CFG.dir("decisions") / mod / "ADR-X-001.md").write_text("Status: OPEN\n", encoding="utf-8")
    (CFG.dir("domain")).mkdir(parents=True, exist_ok=True)
    (CFG.dir("domain") / "domain-profile.md").write_text("stub domain profile\n", encoding="utf-8")
    (CFG.dir("platform") / "project-registry.md").write_text("stub project registry\n", encoding="utf-8")
    (CFG.dir("domain") / "README.md").write_text("static project readme — never generated\n", encoding="utf-8")
    (root / "_archive-v5").mkdir(parents=True, exist_ok=True)
    (root / "_archive-v5" / "marker.txt").write_text("keep\n", encoding="utf-8")
    (root / "history").mkdir(parents=True, exist_ok=True)
    (root / "history" / "marker.txt").write_text("keep\n", encoding="utf-8")


def test_new_domain_refuses_over_uncommitted_changes(orch_root, mod):
    _populate(orch_root, mod)   # left uncommitted on purpose — never even `git add`ed
    before = sorted(p.name for p in CFG.profiles_dir().glob("*.yaml"))

    rc = gov.cmd_new_domain("shouldnot-run", yes=True)

    assert rc == BLOCKED
    assert sorted(p.name for p in CFG.profiles_dir().glob("*.yaml")) == before
    assert not (CFG.profiles_dir() / "shouldnot-run.yaml").exists()
    assert CFG.module_root(mod).exists()
    assert (CFG.dir("decisions") / mod).exists()
    assert (CFG.dir("domain") / "domain-profile.md").exists()


def test_new_domain_resets_exact_scope_and_starts_first_stage(orch_root, mod, monkeypatch):
    _dirty_repos_block(orch_root)
    _populate(orch_root, mod)
    CFG.reload()
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=orch_root)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "populated project state", cwd=orch_root)

    tools_marker = CFG.dir("tools") / "templates" / "README.md.j2"
    project_readme = CFG.dir("domain") / "README.md"
    assert tools_marker.exists() and project_readme.exists()

    rc = gov.cmd_new_domain("notes", yes=True, module="NOTES")

    assert rc == AWAITING   # manual runner: brief written, awaiting the operator

    # deleted — exactly the scoped set
    assert not (CFG.profiles_dir() / "erp.yaml").exists()
    assert not (CFG.profiles_dir() / "erp").exists()
    assert not CFG.module_root(mod).exists()
    assert not (CFG.dir("decisions") / mod).exists()
    assert not (CFG.dir("domain") / "domain-profile.md").exists()
    assert not (CFG.dir("platform") / "project-registry.md").exists()

    # kept — untouched by construction (different subtrees, never in the computed scope)
    assert tools_marker.exists()
    assert project_readme.exists() and "static project readme" in project_readme.read_text(encoding="utf-8")
    assert (orch_root / "_archive-v5" / "marker.txt").exists()
    assert (orch_root / "history" / "marker.txt").exists()

    # scaffolded + factory.yaml instance values reset
    assert (CFG.profiles_dir() / "notes.yaml").exists()
    factory_text = (orch_root / "factory.yaml").read_text(encoding="utf-8")
    assert re.search(r"(?m)^  active_profile:\s*notes\b", factory_text)
    assert 'url: ""' in factory_text
    assert 'checkout_default: "../backend"' in factory_text
    # factory.yaml's own mechanism (paths/lanes/commands/stages) untouched
    assert "checkout_env: GOV_BACKEND_CHECKOUT" in factory_text

    # continued straight into the pipeline's first stage for the given module
    stage = gov.CFG.stages[0]
    brief = CFG.state_dir("NOTES", 1) / "briefs" / f"{stage.id}.md"
    assert brief.exists() and "# ENGINE" in brief.read_text(encoding="utf-8")


def test_sanitize_mod_derives_a_valid_module_code():
    assert gov._sanitize_mod("acme-shop") == "ACMESHOP"
    assert gov._sanitize_mod("notes") == "NOTES"
    assert gov._sanitize_mod("123x") == "M123X"
