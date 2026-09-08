"""(p) Agnosticism: a NON-ERP toy profile (outpatient clinic), written into the
tmp root and validated against profiles/_schema.yaml, drives the SAME toolkit
— different phase keys, different module prefixes, one language."""
from __future__ import annotations

import pytest
import yaml

import lint
from config import CFG
from toolkit import ensure_structure, load_manifest, split
from toolkit.common import flat_plan, plan_key, track_plans
from toolkit.markers import parse

import planfx as fx

TOY = {
    "schema_version": 6,
    "identity": {"id": "toy", "display": "Clinic Suite", "description": "Outpatient clinic scheduling and billing."},
    "languages": {"all": ["en"], "primary": "en", "require_all": False},
    "vocabulary": {
        "module_prefixes": {"PAT": "Patients", "APT": "Appointments", "BIL": "Billing"},
        "entity_kinds": ["record", "event"],
        "glossary": {"Visit": "One patient encounter."},
    },
    "tracks": {
        "backend": {"plans": {
            "exec": {"phases": [
                {"key": "FOUNDATION", "never_split": True},
                {"key": "RECORDS", "display": "Records & Charts", "folder": "records", "sub_labels": ["CLINICAL", "ADMIN"]},
                {"key": "ENDPOINTS", "split_threshold": {"kind": "API", "count": 3, "op": ">="}, "sub_labels": ["READ", "WRITE"]},
                {"key": "LINKS", "split_threshold": {"kind": "XM", "count": 2, "op": ">=", "grouping": "per partner system"}},
                {"key": "WRAP-UP", "never_split": True},
            ]},
            "test": {"phases": [
                {"key": "CLINIC-TESTS", "split_threshold": {"kind": "TC", "count": 4, "op": ">"}, "sub_labels": ["FLOWS", "EDGES"]},
            ]},
        }},
        "frontend": {"plans": {
            "exec": {"phases": [
                {"key": "VIEWS", "sub_bearing": True},
                {"key": "CLOSE", "never_split": True},
            ]},
        }},
    },
    "stack": {
        "db": {"dialects": ["sqlite3"]},
        "backend": {"framework": "fastapi-python", "api": {"base_path": "/v1/{resource}", "verbs": {"GET": "read", "POST": "create"}}},
        "frontend": {"framework": "vue-ts"},
        "testing": {"manifest": False},
    },
}


@pytest.fixture
def toy(factory_root):
    (factory_root / CFG.paths["profiles"] / "toy.yaml").write_text(yaml.safe_dump(TOY, sort_keys=False), encoding="utf-8")
    cfg = CFG.reload(profile_id="toy")
    assert cfg.profile_id == "toy"
    yield cfg
    CFG.reload()


def test_toy_profile_validates_against_schema(toy):
    findings = lint.validate_profile(toy, toy.load_profile("toy"))
    assert [f for f in findings if f.severity in ("CRITICAL", "MAJOR")] == [], [str(f) for f in findings]


def test_toy_vocabulary_is_live_in_cfg(toy):
    assert list(CFG.profile.vocabulary["module_prefixes"]) == ["PAT", "APT", "BIL"]
    assert CFG.profile.phase_keys("backend", "exec") == ["FOUNDATION", "RECORDS", "ENDPOINTS", "LINKS", "WRAP-UP"]
    assert CFG.profile.languages["all"] == ["en"]
    assert set(track_plans()) == {("backend", "exec"), ("backend", "test"), ("frontend", "exec")}


def test_toy_parser_uses_toy_phases(toy):
    mod = "PAT"
    res = parse(fx.exec_plan(mod), "backend", "exec")
    assert res.findings == [] and [p.id for p in res.phases()] == CFG.profile.phase_keys("backend", "exec")
    # an ERP-looking phase key is unknown here
    bad = parse("<!-- PHASE:CORE:START -->\nx\n<!-- PHASE:CORE:END -->\n", "backend", "exec")
    assert any(f.rule == "phase-unknown" for f in bad.findings)
    # toy module prefix accepted by the ID grammar, foreign prefix not
    g = res.grammar
    kind = fx.countable_kind(g, fx.threshold_phase(g))
    assert g.atom_rx[kind].fullmatch(CFG.make_id(g.atom_kinds[kind], "APT", 7))


def test_toy_split_exec_and_test_plans(toy):
    mod = "APT"
    ensure_structure(mod, 1)
    for track, plan, text in (("backend", "exec", fx.exec_plan(mod)), ("backend", "test", fx.test_plan(mod)),
                              ("frontend", "exec", fx.exec_plan(mod, "frontend", "exec"))):
        CFG.plan_path(mod, track, plan, 1).write_text(text, encoding="utf-8")
        rep = split(mod, track, plan, 1)
        assert rep.ok, (track, plan, rep.findings, rep.verification)
        container = CFG.packages_dir(mod, track, plan, 1)
        dirs = {p.name for p in container.iterdir() if p.is_dir()}
        if flat_plan(plan):
            assert dirs == set()
            assert {"FLOWS.md", "EDGES.md", "CLINIC-TESTS-HEADER.md"} <= {f.name for f in container.glob("*.md")}
        else:
            assert dirs == {p.folder for p in CFG.profile.phases(track, plan)}
    exec_dir = CFG.packages_dir(mod, "backend", "exec", 1)
    assert (exec_dir / "records" / "RECORDS.md").exists(), "custom folder name honoured"
    assert (exec_dir / "ENDPOINTS" / "ENDPOINTS-READ.md").exists() and (exec_dir / "ENDPOINTS" / "ENDPOINTS-WRITE.md").exists()
    assert (exec_dir / "FOUNDATION" / "FOUNDATION.md").exists()
    m = load_manifest(mod, 1)
    assert m["profile"] == "toy" and all(m["status"]["split"][plan_key(t, p)] for t, p in track_plans())


def test_toy_thresholds_and_never_split_follow_the_profile(toy):
    mod = "BIL"
    text, ph = fx.over_threshold_no_sub(mod)
    assert ph.key == "ENDPOINTS"
    res = parse(text, "backend", "exec")
    assert [f.rule for f in res.findings] == ["split-threshold"] and "3" in res.findings[0].message
    ns = parse(fx.never_split_with_sub(), "backend", "exec")
    assert [f.rule for f in ns.findings] == ["never-split"] and "FOUNDATION" in ns.findings[0].message
