"""
Cross-repo publications — `gov.py publish`.

A published file is DERIVED, and a derived file that overwrites a consumer's
tree can destroy facts it never authored. Two invariants carry that risk, and
both are asserted here against an isolated factory root and fake checkouts:

  * additive — a module only the consumer knows about survives a publish
  * preserve — fields the factory does not own (description, registered_at)
    are carried over rather than regenerated

Plus the property the whole move exists for: every copy lands INSIDE its own
repo, at the path that repo declares under `receives`.
"""
from __future__ import annotations

import json

import pytest

from config import CFG


@pytest.fixture
def linked(factory_root, mod, monkeypatch):
    """A factory with one module on disk and every consumer repo checked out."""
    import gov

    stage = next(iter(CFG.all_stages())).folder
    (CFG.module_root(mod) / stage).mkdir(parents=True)          # v1 by the filesystem authority
    checkouts = {}
    for repo in CFG.repos:
        c = factory_root.parent / repo
        c.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv(CFG.repos[repo]["checkout_env"], str(c))
        checkouts[repo] = c
    return gov, mod, checkouts


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_publishes_into_every_repo_at_its_declared_path(linked):
    gov, mod, checkouts = linked
    for pub in CFG.publications:
        assert gov.cmd_publish(pub) == 0
        for repo, checkout in checkouts.items():
            target = CFG.repo_receives(repo, pub)
            assert target is not None
            assert target.exists(), f"{repo} never received {pub}"
            # the whole point of the move: no path above the repo root
            assert checkout in target.parents
        bodies = {CFG.repo_receives(r, pub).read_text(encoding="utf-8") for r in checkouts}
        assert len(bodies) == 1, "consumer copies diverged"
    assert mod in _read(CFG.repo_receives(next(iter(checkouts)), "modules-registry"))["modules"]


def test_keeps_a_module_the_factory_does_not_know(linked):
    gov, mod, checkouts = linked
    repo = next(iter(checkouts))
    target = CFG.repo_receives(repo, "modules-registry")
    target.parent.mkdir(parents=True, exist_ok=True)
    stranger = {"code": "ZZZ", "description": "built by an older toolchain",
                "registered_at": "2020-01-01T00:00:00", "versions": [2], "current_version": 2}
    target.write_text(json.dumps({"modules": {"ZZZ": stranger}}), encoding="utf-8")

    assert gov.cmd_publish("modules-registry") == 0
    after = _read(target)["modules"]
    assert after["ZZZ"] == stranger, "a module the factory never saw was rewritten or dropped"
    assert mod in after


def test_preserves_the_fields_the_factory_does_not_own(linked):
    gov, mod, checkouts = linked
    target = CFG.repo_receives(next(iter(checkouts)), "modules-registry")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"modules": {mod: {
        "code": mod, "description": "written by a human", "registered_at": "2020-01-01T00:00:00",
        "versions": [], "current_version": None}}}), encoding="utf-8")

    assert gov.cmd_publish("modules-registry") == 0
    row = _read(target)["modules"][mod]
    for field in CFG.publications["modules-registry"]["preserve"]:
        assert row[field] == {"description": "written by a human",
                              "registered_at": "2020-01-01T00:00:00"}[field]
    assert row["versions"] == [1] and row["current_version"] == 1   # derived fields DO refresh


def test_dry_run_writes_nothing(linked):
    gov, _, checkouts = linked
    gov.cmd_publish("modules-registry", dry_run=True)
    for repo in checkouts:
        assert not CFG.repo_receives(repo, "modules-registry").exists()
