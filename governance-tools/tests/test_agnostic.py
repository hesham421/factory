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


# ════════════════════════════════════════════════════════════════════════════
# F1 — the blocking policy is a config fact
# ----------------------------------------------------------------------------
# The severity vocabulary a factory declares is exercised with names no reader
# of this repository would guess (HALT / WARN / NOTE). Any literal left behind
# in analyze, gov, lint or the toolkit fails these: they cannot resolve a name
# that only the toy factory.yaml knows.
# ════════════════════════════════════════════════════════════════════════════

TOY_SEVERITIES = ["HALT", "WARN", "NOTE"]


@pytest.fixture
def toy_policy(toy):
    """The toy factory declares its own severity scale, blocking the top two."""
    def policy(blocking):
        path = toy.root / "factory.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["analyze"] = {"severities": list(TOY_SEVERITIES), "blocking": list(blocking)}
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return CFG.reload(profile_id="toy")
    return policy


def test_toy_severity_vocabulary_is_live(toy_policy):
    from toolkit.common import severities, sev, severity_rank, known_severity, counts_line
    toy_policy(TOY_SEVERITIES[:2])
    assert list(severities()) == TOY_SEVERITIES
    assert sev(0) == "HALT" and sev(1) == "WARN" and sev(2) == "NOTE"
    assert sev(9) == "NOTE", "rank past the end clamps to the least severe declared level"
    assert severity_rank("HALT") < severity_rank("NOTE")
    assert severity_rank("CRITICAL") == len(TOY_SEVERITIES), "a name this factory never declared sorts last"
    assert not known_severity("CRITICAL") and known_severity("WARN")
    assert counts_line({"HALT": 2, "WARN": 0}) == "2 halt · 0 warn"


def test_toy_blocking_set_decides_the_verdict(toy_policy):
    """`clean` is 'no finding at a blocking severity', read from config — the
    defect this fix exists for is a second-rank finding that blocked nothing."""
    import analyze as an
    from toolkit.common import blocks

    def report(*sevs):
        r = an.AnalyzeReport("PAT", 1, "all")
        r.findings = [an.Finding(s, "T1.1", "exists", "toy") for s in sevs]
        return r

    toy_policy(["HALT", "WARN"])
    assert report().clean and report("NOTE").clean
    assert not report("WARN").clean and not report("HALT").clean
    assert blocks(report("WARN").findings)
    assert report("HALT", "WARN", "NOTE").counts() == {"HALT": 1, "WARN": 1, "NOTE": 1}

    toy_policy(["HALT"])                                  # narrow the policy, nothing else
    assert report("WARN").clean, "the verdict follows factory.yaml, not a literal"
    assert not blocks(report("WARN").findings)


def test_toy_unknown_clause_severity_is_itself_a_finding(toy_policy, monkeypatch):
    """A clause charged at a severity the vocabulary does not declare can never
    reach `blocking`, so it enforces nothing — the same defensive shape `run()`
    already uses for a check nobody implements."""
    import analyze as an
    import render
    toy_policy(["HALT", "WARN"])
    ensure_structure("PAT", 1)
    monkeypatch.setattr(render, "contracts_from_doc", lambda cfg: [
        {"id": "T1", "title": "toy", "owner": "P0", "consumer": "P0.5", "artifacts": [], "clauses": [
            {"id": "T1.1", "check": "exists", "args": {"artifact": "prd"}, "severity": "SEVERE"},
        ]},
    ])
    rep = an.run("PAT", 1, scope="all", write=False)
    bad = [f for f in rep.findings if "never block" in f.message]
    assert bad and bad[0].severity == "HALT", [str(f) for f in rep.findings]
    assert any("SEVERE" in s for s in rep.skipped)
    assert not rep.clean
