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
    """A project with one module on disk, and every consumer repo checked out
    somewhere else — so a copy landing in a consumer's tree would be visible."""
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
    """Where the publication lands — the project repo, when it declares a home.
    Derived, never listed: the home is a config decision this suite follows."""
    p = CFG.project_receives(pub)
    return {"project": p} if p else {}


def test_publishes_into_the_project_repo_and_nowhere_else(linked):
    gov, mod, checkouts = linked
    for pub in CFG.publications:
        targets = _receivers(pub)
        assert targets, f"nothing receives {pub} — the publication has no reader"
        assert gov.cmd_publish(pub) == 0
        target = targets["project"]
        assert target.exists(), f"the project never received {pub}"
        assert CFG.project_checkout() in target.parents         # inside the one repo every consumer mounts
        for repo, checkout in checkouts.items():
            assert not list(checkout.rglob(target.name)), f"a copy of {pub} appeared in {repo}'s own tree"
    assert mod in _read(_receivers("modules-registry")["project"])["modules"]


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


# ── profile-summary: the factory facts a consumer must not retype ────────────

def test_the_summary_carries_what_a_consumer_would_otherwise_type(linked):
    """Both consumer generators restated the profile id and each track's ordered
    phase list — the id in 29 places, the phase list twice per generator, one of
    them `gated_by_phases`, which decides what must be COMPLETE before a test
    phase runs (F-14). Everything they restated has to be in here, or they go
    back to typing it."""
    gov, mod, checkouts = linked
    assert gov.cmd_publish("profile-summary") == 0
    summary = _read(next(iter(_receivers("profile-summary").values())))

    assert summary["profile"] == CFG.profile.id
    for key in CFG.external["keys"]:
        assert summary["paths"][key] == CFG.paths[key]
    for track in CFG.tracks:
        row = summary["tracks"][track]
        assert row["repo"] == CFG.track_repo(track)
        for plan in CFG.profile.plans(track):
            keys = [ph["key"] for ph in row["plans"][plan]["phases"]]
            assert keys == CFG.profile.phase_keys(track, plan), "order is the point"
            assert row["plans"][plan]["package"] == CFG.tracks[track]["packages"][plan]
    # attributes that drive behaviour travel with the key, not as prose
    fe = summary["tracks"]["frontend"]["plans"]["exec"]["phases"]
    assert any(ph["binds_api"] for ph in fe), "no phase declares it binds the API surface"


def test_the_summary_is_deterministic(linked):
    """Same profile, same bytes. A derived file that changes on every publish
    makes `unchanged` meaningless and every diff noise."""
    gov, _, checkouts = linked
    target = next(iter(_receivers("profile-summary").values()))
    assert gov.cmd_publish("profile-summary") == 0
    first = target.read_text(encoding="utf-8")
    assert gov.cmd_publish("profile-summary") == 0
    assert target.read_text(encoding="utf-8") == first


def test_a_publication_whose_builder_is_not_registered_is_a_lint_finding(factory_root):
    import lint
    cfg = CFG.reload()
    assert lint.scan_config(cfg) == []
    cfg.data["publications"]["modules-registry"]["builder"] = "nonesuch"
    found = lint.scan_config(cfg)
    assert len(found) == 1 and "not registered" in found[0].message
    CFG.reload()


# ── feedback: what a consumer records for the factory to answer ──────────────

def _write_state(track, mod, items):
    import gov, json as _j
    d = gov._shared_dir(CFG.track_partition(track), mod)
    d.mkdir(parents=True, exist_ok=True)
    (d / CFG.feedback["file"]).write_text(_j.dumps({"module": mod, **items}), encoding="utf-8")


def test_an_unknown_resolution_word_is_reported_not_bucketed(linked, capsys):
    """`resolution` is prose an implementer types, and it was already written
    eleven ways. A word in none of the declared lists must come back
    UNRECOGNISED: a gap silently filed as closed is worse than one filed
    nowhere."""
    gov, mod, _ = linked
    track = next(iter(CFG.tracks))
    _write_state(track, mod, {"api_doc_gaps": [
        {"type": "ABSENT", "phase": "P", "endpoint": "e1", "resolution": "OPEN"},
        {"type": "ABSENT", "phase": "P", "endpoint": "e2", "resolution": "Resolved."},
        {"type": "ABSENT", "phase": "P", "endpoint": "e3", "resolution": "ABSENT"},
        {"type": "ABSENT", "phase": "P", "endpoint": "e4", "resolution": ""},
    ]})
    rows = {r["id"]: r["status"] for r in gov._feedback_rows(mod)}
    assert rows["e1"] == "OPEN"
    assert rows["e2"] == "CLOSED", "punctuation and case must not change the bucket"
    assert rows["e3"] == "UNRECOGNISED"
    assert rows["e4"] == "UNRECOGNISED", "an empty resolution is not a closed one"

    assert gov.cmd_feedback(mod) == 0
    out = capsys.readouterr().out
    assert "UNRECOGNISED" in out and "not a declared status" in out
    assert "3 item(s) the factory has not answered" in out


def test_feedback_reads_every_declared_channel(linked):
    gov, mod, _ = linked
    track = next(iter(CFG.tracks))
    _write_state(track, mod, {ch: [{"id": f"{ch}-1", "endpoint": f"{ch}-1", "resolution": "OPEN"}]
                              for ch in CFG.feedback["channels"]})
    got = {r["channel"] for r in gov._feedback_rows(mod)}
    assert got == set(CFG.feedback["channels"]), "a declared channel nothing reads is a channel that does not exist"


def test_feedback_says_so_when_it_examined_nothing(linked, capsys):
    gov, mod, _ = linked
    assert gov.cmd_feedback(mod) == 0
    assert "nothing recorded" in capsys.readouterr().out


# ── the gate will not open over a gap the factory has not answered ───────────

def _gate_with_feedback():
    return next(g for g in CFG.gates if g.get("requires_feedback") == "answered")


def test_a_waiver_is_pinned_to_the_items_it_saw(linked):
    """A waiver that says only "feedback waived" covers whatever appears next,
    which is the opposite of a decision. It names its items, the same way
    `approve` binds an approval to `artifact_sha`."""
    import json as _j
    gov, mod, _ = linked
    track = next(iter(CFG.tracks))
    g = _gate_with_feedback()
    pass_no = CFG.gate(g["id"])["after"]
    _write_state(track, mod, {"api_doc_gaps": [
        {"type": "ABSENT", "phase": "P", "endpoint": "old-1", "resolution": "OPEN"},
        {"type": "ABSENT", "phase": "P", "endpoint": "old-2", "resolution": "HUMAN"},
    ]})
    blockers, waiver = gov._feedback_blockers(mod, 1, pass_no)
    assert len(blockers) == 2 and not waiver

    assert gov.cmd_waive_feedback(mod, 1, pass_no, by="t", why="decided") == 0
    blockers, waiver = gov._feedback_blockers(mod, 1, pass_no)
    assert blockers == [] and waiver["by"] == "t" and len(waiver["waived"]) == 2

    # a gap recorded AFTER the waiver is not covered by it
    _write_state(track, mod, {"api_doc_gaps": [
        {"type": "ABSENT", "phase": "P", "endpoint": "old-1", "resolution": "OPEN"},
        {"type": "ABSENT", "phase": "P", "endpoint": "old-2", "resolution": "HUMAN"},
        {"type": "ABSENT", "phase": "P", "endpoint": "new-1", "resolution": "OPEN"},
    ]})
    blockers, _ = gov._feedback_blockers(mod, 1, pass_no)
    assert [b["id"] for b in blockers] == ["new-1"], "a standing waiver swallowed a new gap"


def test_a_closed_item_never_blocks(linked):
    gov, mod, _ = linked
    track = next(iter(CFG.tracks))
    pass_no = CFG.gate(_gate_with_feedback()["id"])["after"]
    _write_state(track, mod, {"api_doc_gaps": [
        {"type": "ABSENT", "phase": "P", "endpoint": "done", "resolution": "RESOLVED"},
    ]})
    assert gov._feedback_blockers(mod, 1, pass_no)[0] == []


def test_waiving_nothing_writes_nothing(linked):
    """A waiver file with an empty list would read as a decision that was never
    taken, and would then cover the first gap recorded after it."""
    gov, mod, _ = linked
    pass_no = CFG.gate(_gate_with_feedback()["id"])["after"]
    assert gov.cmd_waive_feedback(mod, 1, pass_no, by="t", why="nothing here") == 0
    assert not gov._waiver_path(mod, 1, pass_no).exists()
