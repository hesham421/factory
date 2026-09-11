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


# ════════════════════════════════════════════════════════════════════════════
# F2 — a verdict is invalidated when its inputs or its rules change
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def toy_analyzable(toy_policy):
    """A toy module with one artifact and a toy CONTRACT DOCUMENT of its own, so a
    real report (real rules digests, real input digests) can be written and then
    invalidated. Nothing about the ERP contract set is involved."""
    import analyze as an
    import render
    toy_policy(TOY_SEVERITIES[:2])
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    ensure_structure(mod, 1)
    stage = next(s for s in CFG.stages if any(a.artifact == "prd" for a in s.produces))
    art = CFG.artifact_path(mod, stage.id, "prd", 1)
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_text("# toy prd\nbody\n", encoding="utf-8")
    doc = render.contracts_path(CFG)
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("---\n" + yaml.safe_dump({"contracts": [
        {"id": "T1", "title": "toy", "owner": stage.id, "consumer": stage.id, "artifacts": ["prd"],
         "clauses": [{"id": "T1.1", "check": "exists", "args": {"artifact": "prd"}, "severity": "HALT"}]},
    ]}, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    return mod, art, an


def test_toy_report_records_what_produced_it(toy_analyzable):
    mod, art, an = toy_analyzable
    rep = an.run(mod, 1, scope="all")
    prov = rep.provenance
    assert set(prov["rules"]) == {"contracts", "checker", "policy"}
    assert all(prov["rules"].values()), "every rule digest resolves"
    assert "prd" in prov["inputs"], "the artifact list is derived from what the run READ"
    data = yaml.safe_load(an.report_json_path(mod, 1, "all").read_text(encoding="utf-8"))
    assert data["provenance"]["rules"] == prov["rules"]
    assert data["blocking"] == ["HALT", "WARN"] and "skipped" in data, "skipped survives into the JSON"
    assert an.stale_reason(mod, 1, "all") is None, "a report just written is current"


def test_toy_verdict_is_refused_when_an_input_changes(toy_analyzable):
    mod, art, an = toy_analyzable
    an.run(mod, 1, scope="all")
    art.write_text("# toy prd\nbody, edited\n", encoding="utf-8")
    assert "has changed" in (an.stale_reason(mod, 1, "all") or ""), "a source edit is caught before the digests"
    import state as st
    st.build_state(mod, 1)
    reason = an.stale_reason(mod, 1, "all")
    assert reason and "inputs changed" in reason and "prd" in reason, reason
    rep, refused = an.verdict(mod, 1, "all", write=False)
    assert refused == reason, "verdict() re-runs rather than trusting it"


def test_toy_verdict_is_refused_when_the_policy_changes(toy_analyzable, toy_policy):
    """Strengthening the rules must invalidate every prior PASS — the whole point:
    all three modules held verdicts from a contract set that no longer existed."""
    mod, art, an = toy_analyzable
    an.run(mod, 1, scope="all")
    assert an.stale_reason(mod, 1, "all") is None
    toy_policy(TOY_SEVERITIES)                    # widen `blocking`; nothing else moves
    reason = an.stale_reason(mod, 1, "all")
    assert reason and "policy" in reason, reason


def test_toy_contract_document_change_invalidates_every_verdict(toy_analyzable):
    """The exact failure this fix exists for: the contract set grew from 73 checks
    to 80 and not one stored PASS was invalidated."""
    mod, art, an = toy_analyzable
    import render
    an.run(mod, 1, scope="all")
    assert an.stale_reason(mod, 1, "all") is None
    doc = render.contracts_path(CFG)
    doc.write_text(doc.read_text(encoding="utf-8") + "\nan added clause would live here\n", encoding="utf-8")
    reason = an.stale_reason(mod, 1, "all")
    assert reason and "contracts" in reason, reason


def test_toy_verdict_is_refused_when_an_unseen_artifact_appears(toy_analyzable):
    mod, art, an = toy_analyzable
    an.run(mod, 1, scope="all")
    stage = next(s for s in CFG.stages if any(a.artifact == "srs" for a in s.produces))
    p = CFG.artifact_path(mod, stage.id, "srs", 1)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# toy srs\n", encoding="utf-8")
    import state as st
    st.build_state(mod, 1)
    reason = an.stale_reason(mod, 1, "all")
    assert reason and "never saw" in reason, reason


def test_toy_sweep_takes_its_module_list_from_state(toy_analyzable):
    """`analyze --all-modules` reads the filesystem, never a list of names."""
    mod, art, an = toy_analyzable
    import gov
    assert CFG.modules() == [mod], "only modules that actually exist"
    assert gov.cmd_analyze_all("all") == gov.OK
    assert an.stale_reason(mod, 1, "all") is None, "the sweep clears the backlog"


# ════════════════════════════════════════════════════════════════════════════
# F3 — the authored verdict is reconciled with (and generated from) the machine
# ----------------------------------------------------------------------------
# The toy clinic names its self-check block, its verdict label and its wording
# nothing like the ERP profile does. The checker and the stamper know none of
# those words: they arrive through `profile.self_check` and the clause's `spec`.
# ════════════════════════════════════════════════════════════════════════════

TOY_SELF_CHECK = {"block": "SIGNOFF", "verdict_label": "OUTCOME",
                  "pass_token": "CLEAR", "fail_token": "HELD", "findings_noun": "issues"}


@pytest.fixture
def toy_self_check(toy_analyzable):
    """The toy profile declares its own self-check, and its contract carries a
    `verdict-agrees` clause pointing at the profile address that holds it."""
    import render
    mod, art, an = toy_analyzable
    prof = CFG.profiles_dir() / "toy.yaml"
    data = yaml.safe_load(prof.read_text(encoding="utf-8"))
    data["self_check"] = dict(TOY_SELF_CHECK)
    prof.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    stage = spec["contracts"][0]["owner"]
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.2", "check": "verdict-agrees",
         "args": {"artifact": ["prd"], "spec": "self_check", "when": "profile.self_check"}, "severity": "HALT"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an, stage


def _plan(verdict_line: str) -> str:
    return ("# toy prd\n\n## Sign-off (SIGNOFF) — v1\n\n```\n"
            "ROWS      everything checked\n" + verdict_line + "\n```\n")


def test_toy_self_check_vocabulary_is_live(toy_self_check):
    mod, art, an, stage = toy_self_check
    assert CFG.profile.self_check == TOY_SELF_CHECK
    assert an.render_verdict(TOY_SELF_CHECK, 0) == "CLEAR — 0 issues"
    assert an.render_verdict(TOY_SELF_CHECK, 3) == "HELD — 3 issues"
    # the block is found by its token anywhere on a line; the label must open its line
    found = an._verdict_line(_plan("OUTCOME  CLEAR — 0 issues"), TOY_SELF_CHECK)
    assert found and found[1].strip() == "OUTCOME  CLEAR — 0 issues"
    assert an.claimed_findings("OUTCOME  CLEAR — 0 issues", TOY_SELF_CHECK) == 0
    assert an.claimed_findings("OUTCOME  CLEAR", TOY_SELF_CHECK) == 0
    assert an.claimed_findings("OUTCOME  HELD — 4 issues", TOY_SELF_CHECK) == 4
    assert an.claimed_findings("OUTCOME  pending", TOY_SELF_CHECK) is None


def test_toy_verdict_that_understates_its_findings_is_a_finding(toy_self_check, monkeypatch):
    """The shipped defect, reproduced under a profile whose words are all different:
    an artifact claiming zero over findings the machine produced for it."""
    import analyze as an
    mod, art, an, stage = toy_self_check
    art.write_text(_plan("OUTCOME  CLEAR — 0 issues"), encoding="utf-8")
    # one real finding against the same artifact, injected through the check registry
    monkeypatch.setitem(an.CHECKS, "exists",
                        lambda ctx, c, sev: [an.Finding(sev, "", "exists", "toy defect", "prd", 2)])
    rep = an.run(mod, 1, scope="all", write=False)
    bad = [f for f in rep.findings if f.check == "verdict-agrees"]
    assert bad and bad[0].severity == "HALT", [str(f) for f in rep.findings]
    assert "claims 0 issues" in bad[0].message and "produced 1" in bad[0].message
    assert "HELD — 1 issues" in bad[0].message, "the message names the correct line"


def test_toy_verdict_stating_the_truth_passes(toy_self_check, monkeypatch):
    import analyze as an
    mod, art, an, stage = toy_self_check
    art.write_text(_plan("OUTCOME  HELD — 1 issues"), encoding="utf-8")
    monkeypatch.setitem(an.CHECKS, "exists",
                        lambda ctx, c, sev: [an.Finding(sev, "", "exists", "toy defect", "prd", 2)])
    rep = an.run(mod, 1, scope="all", write=False)
    assert [f for f in rep.findings if f.check == "verdict-agrees"] == []


def test_toy_orchestrator_generates_the_verdict_from_the_report(toy_self_check, monkeypatch):
    """The preferred half: the line is WRITTEN from the report, so it cannot drift.
    Nothing in gov.py knows the words SIGNOFF, OUTCOME, CLEAR or HELD."""
    import gov
    import analyze as an
    mod, art, an, stage = toy_self_check
    art.write_text(_plan("OUTCOME  CLEAR — 0 issues"), encoding="utf-8")
    rep = an.AnalyzeReport(mod, 1, "all")
    rep.findings = [an.Finding("HALT", "T1.1", "exists", "toy defect", "prd", 2),
                    an.Finding("WARN", "T1.1", "exists", "another", "prd", 3)]
    changed = gov._stamp_verdict(CFG.stage(stage), mod, 1, rep)
    assert changed == [art]
    assert "OUTCOME  HELD — 2 issues" in art.read_text(encoding="utf-8")
    assert gov._stamp_verdict(CFG.stage(stage), mod, 1, rep) == [], "stamping is idempotent"
    # and a clean report writes the pass wording back
    rep.findings = []
    gov._stamp_verdict(CFG.stage(stage), mod, 1, rep)
    assert "OUTCOME  CLEAR — 0 issues" in art.read_text(encoding="utf-8")


def test_a_profile_with_no_self_check_is_served_unchanged(toy_analyzable):
    """No self-check declared → the clause never runs and nothing is stamped."""
    import gov
    mod, art, an = toy_analyzable
    assert CFG.profile.self_check is None
    assert an._c_verdict_agrees(an.Ctx(mod, 1), {"artifact": ["prd"], "spec": "self_check"}, "HALT") == []
    stage = next(s for s in CFG.stages if any(a.artifact == "prd" for a in s.produces))
    assert gov._stamp_verdict(stage, mod, 1, an.AnalyzeReport(mod, 1, "all")) == []
