"""
Cross-repo publications — `gov.py publish`.

A published file is DERIVED, and a derived file that overwrites a consumer's
tree can destroy facts it never authored. Two invariants carry that risk, and
both are asserted here against an isolated factory root and fake checkouts:

  * additive — a module only the consumer knows about survives a publish
  * preserve — fields the factory does not own (description, registered_at)
    are carried over rather than regenerated

Plus the property the whole move exists for: a copy lands INSIDE the repo that
declares it under `receives`, and NOWHERE else. A repo that declares no
`receives` gets nothing — it mounts the shared repo and reads the one copy
there, which is why a publication has one receiver now and not three.
"""
from __future__ import annotations

import json

import pytest

from config import CFG


@pytest.fixture
def linked(factory_root, mod, monkeypatch):
    """A factory with one module on disk and every consumer repo checked out.

    The checkouts are pointed at BEFORE the module is created: modules live in
    the shared repo now (`paths.external`), so `CFG.module_root()` has no
    answer until that checkout is settled."""
    import gov

    checkouts = {}
    for repo in CFG.repos:
        c = factory_root.parent / repo
        c.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv(CFG.repos[repo]["checkout_env"], str(c))
        checkouts[repo] = c
    stage = next(iter(CFG.all_stages())).folder
    (CFG.module_root(mod) / stage).mkdir(parents=True)          # v1 by the filesystem authority
    return gov, mod, checkouts


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _receivers(pub):
    """The repos that declare a home for this publication. Derived, never listed:
    which repos receive is a config decision, and this suite must follow it."""
    return {r: CFG.repo_receives(r, pub) for r in CFG.repos if CFG.repo_receives(r, pub)}


def test_publishes_into_the_repos_that_declare_a_home_and_no_others(linked):
    gov, mod, checkouts = linked
    for pub in CFG.publications:
        targets = _receivers(pub)
        assert targets, f"nothing receives {pub} — the publication has no reader"
        assert gov.cmd_publish(pub) == 0
        for repo, target in targets.items():
            assert target.exists(), f"{repo} never received {pub}"
            # the whole point of the move: no path above the repo root
            assert checkouts[repo] in target.parents
        bodies = {t.read_text(encoding="utf-8") for t in targets.values()}
        assert len(bodies) == 1, "consumer copies diverged"
        # a repo that declares no home gets no copy: it reads the shared one
        for repo, checkout in checkouts.items():
            if repo in targets:
                continue
            assert not list(checkout.rglob(next(iter(targets.values())).name)), \
                f"{repo} declares no `receives` for {pub} yet a copy appeared in it"
    assert mod in _read(next(iter(_receivers("modules-registry").values())))["modules"]


def test_keeps_a_module_the_factory_does_not_know(linked):
    gov, mod, checkouts = linked
    target = next(iter(_receivers("modules-registry").values()))
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
    target = next(iter(_receivers("modules-registry").values()))
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
    for target in _receivers("modules-registry").values():
        assert not target.exists()
