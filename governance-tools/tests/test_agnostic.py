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
    # G6 — the toy states the OPPOSITE access mechanism to the ERP profile, so an
    # engine still carrying an answer of its own emits the wrong one here.
    "conventions": {"module_interface": "rest"},
    "stack": {
        # F5a — the toy states the OPPOSITE answer to the ERP profile for every
        # stated choice. An engine that still carried a default of its own would
        # emit the ERP answer here and the assertions below would catch it.
        "db": {"dialects": ["sqlite3", "duckdb"], "target_dialect": "duckdb",
               "pk_generation": "identity", "delete_semantics": "hard"},
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
    """No self-check declared → the clause does not run, nothing is stamped, and the
    skip is STATED: a check that never ran must not read as a clean pass."""
    import gov
    mod, art, an = toy_analyzable
    assert CFG.profile.self_check is None
    with pytest.raises(an.ClauseSkipped) as e:
        an._c_verdict_agrees(an.Ctx(mod, 1), {"artifact": ["prd"], "spec": "self_check"}, "HALT")
    assert e.value.address == "self_check"
    stage = next(s for s in CFG.stages if any(a.artifact == "prd" for a in s.produces))
    assert gov._stamp_verdict(stage, mod, 1, an.AnalyzeReport(mod, 1, "all")) == []


# ════════════════════════════════════════════════════════════════════════════
# F5a — a dialect default never silently becomes a project decision
# ════════════════════════════════════════════════════════════════════════════

# every key the schema marks as a stated choice — the addresses, not their answers
STATED_CHOICES = ["stack.db.target_dialect", "stack.db.pk_generation", "stack.db.delete_semantics"]


def test_a_profile_that_omits_a_stated_choice_is_a_lint_finding(toy):
    """Not a silent default — a finding. Each of these has a real alternative and
    is restated in a generated artifact, so an unstated one reaches the implementer
    as indistinguishable from a decision that was made."""
    for address in STATED_CHOICES:
        data = yaml.safe_load(yaml.safe_dump(TOY))
        node, leaf = data, address.split(".")
        for part in leaf[:-1]:
            node = node[part]
        node.pop(leaf[-1])
        path = toy.root / CFG.paths["profiles"] / "omitted.yaml"
        data["identity"]["id"] = "omitted"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        fs = lint.validate_profile(toy, toy.load_profile("omitted"))
        assert any(address.split(".")[-1] in f.path and "required" in f.message for f in fs), \
            f"omitting {address} must be a finding, not a default"


def test_a_target_dialect_outside_the_declared_list_is_a_finding(toy):
    data = yaml.safe_load(yaml.safe_dump(TOY))
    data["identity"]["id"] = "wrongtarget"
    data["stack"]["db"]["target_dialect"] = "a-dialect-nobody-kept-rows-for"
    (toy.root / CFG.paths["profiles"] / "wrongtarget.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    fs = lint.validate_profile(toy, toy.load_profile("wrongtarget"))
    assert any("target_dialect" in f.path for f in fs)


def test_the_engines_emit_the_toy_answer_not_a_default(toy):
    """The decisive one: the engine carries no answer of its own. Under the toy
    profile every stated choice renders the TOY's value — the opposite of the ERP
    profile's in all three cases — and no ERP value appears in the brief at all."""
    import shutil
    import dispatch as dp
    from conftest import REAL_ROOT
    shutil.copytree(REAL_ROOT / "engines", toy.root / "engines")
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    for sid in ("P2", "P3.1"):
        out = dp.render_engine(CFG.stage(sid), mod, 1)
        assert "{{" not in out and "{%" not in out, "the brief still holds unrendered template syntax"
        assert TOY["stack"]["db"]["target_dialect"] in out, f"{sid} does not emit the toy's target dialect"
        # no dialect of the OTHER profile on disk may appear — read from it, never typed
        other = toy.load_profile(toy.data["factory"]["active_profile"])
        for d in other.get("stack.db.dialects") or []:
            assert d not in out, f"{sid} leaks a dialect belonging to profile {other.id}"
        pkgen = TOY["stack"]["db"]["pk_generation"]
        assert f"pk_generation = `{pkgen}`" in out or f"strategy `{pkgen}`" in out, \
            f"{sid} does not emit the toy's pk_generation"
    sem = TOY["stack"]["db"]["delete_semantics"]
    assert f"`{sem}` per profile.stack.db.delete_semantics" in dp.render_engine(CFG.stage("P3.1"), mod, 1)


# ════════════════════════════════════════════════════════════════════════════
# F5b — a config fact is rendered, never restated by an author
# ════════════════════════════════════════════════════════════════════════════

def test_no_engine_brief_restates_a_config_value_it_could_render(toy):
    """Every engine brief, rendered under the TOY profile, must contain no value
    belonging to the OTHER profile on disk. A sentence an author maintains by hand
    drifts from the value it describes — that is the whole of C7.11's existence."""
    import shutil
    import dispatch as dp
    from conftest import REAL_ROOT
    for d in ("engines", "standalone"):
        shutil.copytree(REAL_ROOT / d, toy.root / d)
    other = toy.load_profile(toy.data["factory"]["active_profile"])
    # the other profile's distinctive stack values — read from it, never typed here
    foreign = set()
    def collect(v):
        if isinstance(v, str):
            tok = v.split()[0]
            if len(tok) >= 6 and (any(c.isdigit() for c in tok) or "-" in tok or "_" in tok
                                  or (any(c.isupper() for c in tok) and any(c.islower() for c in tok))):
                foreign.add(tok.strip("(),`"))
        elif isinstance(v, list):
            for x in v: collect(x)
        elif isinstance(v, dict):
            for x in v.values(): collect(x)
    collect(other.get("stack"))
    collect(other.get("conventions"))
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    leaks = []
    for stage in list(CFG.stages) + list(CFG.standalone):
        if not (toy.root / ("standalone" if stage.standalone else "engines") / stage.id / "references" / "ENGINE.md").exists():
            continue
        out = dp.render_engine(stage, mod, 1)
        assert "{{" not in out and "{%" not in out, f"{stage.id}: unrendered template syntax survives"
        leaks += [(stage.id, f) for f in foreign if f in out]
    assert leaks == [], f"engine briefs leak values of profile {other.id}: {sorted(set(leaks))}"


def test_atom_lists_in_briefs_follow_the_id_grammar(toy):
    """The P1 count line and the test-gen source list are rendered from
    factory.ids, so a factory that adds or renames an atom needs no engine edit."""
    import shutil
    import dispatch as dp
    from conftest import REAL_ROOT
    shutil.copytree(REAL_ROOT / "engines", toy.root / "engines")
    shutil.copytree(REAL_ROOT / "standalone", toy.root / "standalone")
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    p1 = next(s for s in CFG.stages if "REQ" in s.owns_ids)
    line = next(l for l in dp.render_engine(p1, mod, 1).splitlines() if l.startswith("Counts :"))
    assert all(f"{x} [N]" in line for x in p1.owns_ids), line
    tg = next(s for s in CFG.standalone if "TC" in s.owns_ids)
    out = dp.render_engine(tg, mod, 1)
    sources = CFG.id_atoms()["TC"]["traces_to"]
    assert "/".join(sources) in out, f"the TC source list is not rendered from ids.atoms.TC.traces_to"


# ════════════════════════════════════════════════════════════════════════════
# F6a — an artifact may not state as fact what it cannot verify at its own stage
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def toy_forward(toy_analyzable):
    """The toy declares a forward-referencing column of its own — a different
    artifact, a different header, a different resolving artifact, and its own
    proposed token in the toy factory.yaml."""
    import render
    mod, art, an = toy_analyzable
    fac = toy_analyzable[2].CFG.root / "factory.yaml"
    data = yaml.safe_load(fac.read_text(encoding="utf-8"))
    data["forward_reference"] = {"proposed_token": "<<TBD>>"}
    fac.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["forward_columns"] = [{"artifact": "prd", "column": "Handler class", "resolved_from": "srs"}]
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.3", "check": "forward-refs",
         "args": {"spec": "forward_columns", "when": "profile.forward_columns"}, "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _table(*handlers: str) -> str:
    rows = "\n".join(f"| A-{i} | {h} | v1 |" for i, h in enumerate(handlers, 1))
    return "# toy prd\n\n| Endpoint | Handler class | Stability |\n|---|---|---|\n" + rows + "\n"


def _srs(text: str) -> None:
    stage = next(s for s in CFG.stages if any(a.artifact == "srs" for a in s.produces))
    p = CFG.artifact_path(next(iter(CFG.profile.vocabulary["module_prefixes"])), stage.id, "srs", 1)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_toy_forward_column_stated_as_fact_before_it_can_resolve(toy_forward):
    """The shipped defect, in a profile whose column, artifact and token are all
    different words: names invented for something that does not exist yet."""
    import state as st
    mod, art, an = toy_forward
    art.write_text(_table("LoginHandler", "SignupHandler"), encoding="utf-8")
    st.build_state(mod, 1)
    fs = [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "forward-refs"]
    assert len(fs) == 1, "one finding per unresolvable column, not one per row"
    assert "Handler class" in fs[0].message and "2 value(s)" in fs[0].message
    assert "<<TBD>>" in fs[0].message, "the message names the toy factory's own token"
    assert fs[0].severity == "WARN"


def test_toy_forward_column_marked_proposed_is_honest(toy_forward):
    import state as st
    mod, art, an = toy_forward
    art.write_text(_table("LoginHandler <<TBD>>", "<<TBD>>"), encoding="utf-8")
    st.build_state(mod, 1)
    assert [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "forward-refs"] == []


def test_toy_forward_column_resolves_once_the_later_artifact_exists(toy_forward):
    """The later stage that CAN resolve it: a value the resolving artifact defines
    is a fact, and one it does not is a disagreement — reported per row."""
    import state as st
    mod, art, an = toy_forward
    art.write_text(_table("LoginHandler", "GhostHandler"), encoding="utf-8")
    _srs("# toy srs\nDefines LoginHandler.\n")
    st.build_state(mod, 1)
    fs = [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "forward-refs"]
    assert len(fs) == 1 and "GhostHandler" in fs[0].message and "LoginHandler" not in fs[0].message


def test_a_profile_with_no_forward_columns_is_served_unchanged(toy_analyzable):
    mod, art, an = toy_analyzable
    assert CFG.profile.get("forward_columns") is None
    with pytest.raises(an.ClauseSkipped):
        an._c_forward_refs(an.Ctx(mod, 1), {"spec": "forward_columns"}, "WARN")


# ════════════════════════════════════════════════════════════════════════════
# F6b — a reference resolves where it is CONSUMED, not only where it is written
# ════════════════════════════════════════════════════════════════════════════

def test_toy_locator_regex_is_built_from_the_profile_template(toy):
    """The check reads the address template out of the profile; it knows no path
    shape of its own. The toy's template looks nothing like the ERP one."""
    import analyze as an
    mods = set(CFG.profile.vocabulary["module_prefixes"])
    rx = an._locator_rx(CFG.profile.get("stack.backend.api.base_path"), mods)
    m = rx.search("call GET /v1/apt/slots for the calendar")
    assert m is None or m.groupdict().get("module") is None, "the toy template has no {module} slot"
    rx2 = an._locator_rx("/svc/{module}/{resource}", mods)
    assert rx2.search("see /svc/BIL/invoices").group("module") == "BIL"
    assert rx2.search("see /svc/bil/invoices").group("module") == "bil", "matched case-insensitively"
    assert rx2.search("see /svc/nope/invoices") is None, "an undeclared module is not a locator"


@pytest.fixture
def toy_surface(toy_analyzable):
    """The toy declares its own surface template and a plan that consumes another
    toy module through it."""
    import render
    mod, art, an = toy_analyzable
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["stack"]["backend"]["api"]["base_path"] = "/svc/{module}/{resource}"
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.4", "check": "xref-surface",
         "args": {"artifact": ["prd"], "locator": "stack.backend.api.base_path", "kinds": ["API"]},
         "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _surface_findings(mod, an):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "xref-surface"]


def _seed_other(other: str, *api_ids: str) -> None:
    """Give the target module real artifacts defining the given surface ids, so the
    resolution is across the module SET rather than against an empty module."""
    ensure_structure(other, 1)
    stage = next(s for s in CFG.stages if any(a.artifact == "backend-execution-plan" for a in s.produces))
    p = CFG.artifact_path(other, stage.id, "backend-execution-plan", 1)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(f"<!-- API:{i}:START -->\nan endpoint\n<!-- API:{i}:END -->\n" for i in api_ids)
                 or "# no surface\n", encoding="utf-8")


def test_toy_prose_dependency_with_no_id_is_a_finding(toy_surface):
    """The evidence case: a plan describing data obtained through another module's
    read API, where the target defines no such endpoint. Both modules passed before,
    because each validated only itself."""
    mod, art, an = toy_surface
    other = [m for m in CFG.profile.vocabulary["module_prefixes"] if m != mod][0]
    _seed_other(other, CFG.make_id("API", other, 1))
    art.write_text(f"# toy prd\n\nReads the roster through /svc/{other.lower()}/roster once it exists.\n",
                   encoding="utf-8")
    fs = _surface_findings(mod, an)
    assert len(fs) == 1 and other in fs[0].message and "resolves nowhere" in fs[0].message
    assert fs[0].severity == "WARN" and fs[0].line == 3

    # and a target module with no artifacts at all is its own, distinct finding
    import shutil
    shutil.rmtree(CFG.module_root(other))
    fs = _surface_findings(mod, an)
    assert len(fs) == 1 and "has no artifacts yet" in fs[0].message


def test_toy_narrative_mention_of_another_module_is_not_a_finding(toy_surface):
    """Naming another module in prose is not consuming its surface — only a line
    carrying the profile's own address template is."""
    mod, art, an = toy_surface
    other = [m for m in CFG.profile.vocabulary["module_prefixes"] if m != mod][0]
    art.write_text(f"# toy prd\n\nThe next module to be generated is {other}, then the rest.\n", encoding="utf-8")
    assert _surface_findings(mod, an) == []


def test_toy_surface_reference_resolves_when_the_target_defines_it(toy_surface):
    """Run across the module SET: the id is looked up in the other module's own
    artifacts, not in this one's."""
    mod, art, an = toy_surface
    other = [m for m in CFG.profile.vocabulary["module_prefixes"] if m != mod][0]
    api, ghost = CFG.make_id("API", other, 1), CFG.make_id("API", other, 9)
    # the target exists and defines api, but the plan cites an id it does not define
    _seed_other(other, api)
    art.write_text(f"# toy prd\n\nReads the roster through /svc/{other.lower()}/roster ({ghost}).\n", encoding="utf-8")
    fs = _surface_findings(mod, an)
    assert len(fs) == 1 and "does not define" in fs[0].message, [str(f) for f in fs]

    art.write_text(f"# toy prd\n\nReads the roster through /svc/{other.lower()}/roster ({api}).\n", encoding="utf-8")
    assert _surface_findings(mod, an) == [], "the target module defines the cited surface"


def test_toy_surface_citation_may_wrap_to_the_next_line(toy_surface):
    """Prose wraps. A sentence naming another module's endpoint often carries the
    id on the next line, so a citation anywhere in the same paragraph counts."""
    mod, art, an = toy_surface
    other = [m for m in CFG.profile.vocabulary["module_prefixes"] if m != mod][0]
    api = CFG.make_id("API", other, 1)
    _seed_other(other, api)
    art.write_text(f"# toy prd\n\nReads the roster through /svc/{other.lower()}/roster,\n"
                   f"the endpoint {api} publishes for consumers.\n", encoding="utf-8")
    assert _surface_findings(mod, an) == []


def test_toy_surface_citation_does_not_leak_across_table_rows(toy_surface):
    """A table row is its own statement: an id in a neighbouring row says nothing
    about this one, so the paragraph rule stops at the table."""
    mod, art, an = toy_surface
    other = [m for m in CFG.profile.vocabulary["module_prefixes"] if m != mod][0]
    api = CFG.make_id("API", other, 1)
    _seed_other(other, api)
    art.write_text(f"# toy prd\n\n| Source | Note |\n|---|---|\n"
                   f"| {api} | the roster endpoint |\n"
                   f"| /svc/{other.lower()}/roster | read here |\n", encoding="utf-8")
    fs = _surface_findings(mod, an)
    assert len(fs) == 1 and "cites no API" in fs[0].message


# ════════════════════════════════════════════════════════════════════════════
# G1 — a declared total must equal the rows beneath it
# ----------------------------------------------------------------------------
# The first COMPLETENESS clause. The toy names its total something no ERP reader
# would guess, keys it to a different atom and resolves its rows in a different
# artifact — the checker knows none of the three.
# ════════════════════════════════════════════════════════════════════════════

TOY_TOTALS = [{"artifact": "prd", "label": "CHARTS FILED", "kind": "REQ", "rows_in": "srs"}]


@pytest.fixture
def toy_totals(toy_analyzable):
    import render
    mod, art, an = toy_analyzable
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["declared_totals"] = [dict(r) for r in TOY_TOTALS]
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.5", "check": "count-agrees",
         "args": {"spec": "declared_totals", "when": "profile.declared_totals"}, "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _rows(mod: str, n: int) -> None:
    """`n` rows in the toy's resolving artifact, each keyed by its own id."""
    _srs("# toy srs\n\n" + "\n".join(
        f"### {CFG.make_id('REQ', mod, i)} — the clinic shall record it" for i in range(1, n + 1)) + "\n")


def _count_findings(mod, an):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "count-agrees"]


def test_toy_wrong_total_is_a_finding_that_names_both_numbers(toy_totals):
    mod, art, an = toy_totals
    _rows(mod, 3)
    art.write_text("# toy prd\n\nCHARTS FILED   4\n", encoding="utf-8")
    fs = _count_findings(mod, an)
    assert len(fs) == 1 and fs[0].severity == "WARN", [str(f) for f in fs]
    assert "declares 4" in fs[0].message and "carries 3" in fs[0].message, fs[0].message
    assert "CHARTS FILED" in fs[0].message and "srs" in fs[0].message


def test_toy_right_total_passes(toy_totals):
    mod, art, an = toy_totals
    _rows(mod, 3)
    art.write_text("# toy prd\n\nCHARTS FILED   3\n", encoding="utf-8")
    assert _count_findings(mod, an) == []


def test_toy_two_statements_of_one_total_must_agree_with_each_other(toy_totals):
    """Both are compared against the same row set, so a pair that disagrees is
    two findings — the shipped shape was '147' on one line and '146' on another."""
    mod, art, an = toy_totals
    _rows(mod, 3)
    art.write_text("# toy prd\n\nCHARTS FILED   4\n\nlater: CHARTS FILED 5 in total\n", encoding="utf-8")
    fs = _count_findings(mod, an)
    assert len(fs) == 2 and {f.line for f in fs} == {3, 5}, [str(f) for f in fs]


def test_a_profile_with_no_declared_totals_is_served_unchanged(toy_analyzable):
    mod, art, an = toy_analyzable
    assert CFG.profile.get("declared_totals") is None
    with pytest.raises(an.ClauseSkipped):
        an._c_count_agrees(an.Ctx(mod, 1), {"spec": "declared_totals"}, "WARN")


# ════════════════════════════════════════════════════════════════════════════
# G2 — a declared HTTP status must be one the platform can produce
# ----------------------------------------------------------------------------
# `error_code_format` declares a code's SHAPE, and `FIN-503` obeyed it perfectly
# on a platform whose status enum has no 503. The toy declares a status set of
# its own and its own code format; the checker knows neither.
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def toy_codes(toy_analyzable):
    import render
    mod, art, an = toy_analyzable
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["stack"]["backend"]["api"]["error_code_format"] = "{MOD}-{http}[-{SLUG}]"
    pdata["stack"]["backend"]["api"]["http_statuses"] = [200, 404, 418]
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.6", "check": "code-format",
         "args": {"artifact": ["prd"], "format": "stack.backend.api.error_code_format",
                  "statuses": "stack.backend.api.http_statuses", "require_declaration": False},
         "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _code_findings(mod, an):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "code-format"]


def test_toy_status_outside_the_declared_set_is_a_finding(toy_codes):
    mod, art, an = toy_codes
    art.write_text(f"# toy prd\n\n| {mod}-503-NO-SLOT | the clinic is busy |\n", encoding="utf-8")
    fs = _code_findings(mod, an)
    assert len(fs) == 1 and "503" in fs[0].message and "cannot emit it" in fs[0].message, [str(f) for f in fs]
    assert "418" in fs[0].message, "the message names the declared set, which is the toy's own"


def test_toy_status_inside_the_declared_set_passes(toy_codes):
    mod, art, an = toy_codes
    art.write_text(f"# toy prd\n\n| {mod}-418-NO-COFFEE | the clinic is a teapot |\n", encoding="utf-8")
    assert _code_findings(mod, an) == []


def test_a_profile_that_declares_no_status_set_checks_only_the_shape(toy_codes):
    """The membership half is an optional convention (C5) — remove the set and a
    row the shape accepts passes again, with no clause change."""
    mod, art, an = toy_codes
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["stack"]["backend"]["api"].pop("http_statuses")
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    CFG.reload(profile_id="toy")
    art.write_text(f"# toy prd\n\n| {mod}-503-NO-SLOT | the clinic is busy |\n", encoding="utf-8")
    assert _code_findings(mod, an) == []
    # …and the shape half still holds
    art.write_text(f"# toy prd\n\n| {mod}-9 | not a status at all |\n", encoding="utf-8")
    assert [f for f in _code_findings(mod, an) if "not an instance" in f.message]


# ════════════════════════════════════════════════════════════════════════════
# G3 — required data must have a writer
# ----------------------------------------------------------------------------
# The toy's structural artifact, its required marker, its writing labels and its
# exclusion tokens are all its own words, and the exempt platform-filled fields
# come from the toy profile's own naming block.
# ════════════════════════════════════════════════════════════════════════════

TOY_WRITER_ARGS = {
    "kind": "DBF", "declared_in": "db-script", "required_marker": "stack.db.required_marker",
    "writer_kind": "API", "writer_in": "backend-execution-plan",
    "writer_labels": ["Intake", "Follow-up"],
    "exempt_names": "stack.db.naming.audit_fields",
    "exempt_pattern": "stack.db.naming.pk_pattern",
    "exclusions": ["filled-by-the-clinic"],
}


@pytest.fixture
def toy_writer(toy_analyzable):
    import render
    mod, art, an = toy_analyzable
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["stack"]["db"]["required_marker"] = "MANDATORY"
    pdata["stack"]["db"]["naming"] = {"audit_fields": ["loggedBy"], "pk_pattern": "{record}Ref"}
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.7", "check": "required-writer", "args": dict(TOY_WRITER_ARGS), "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _write_art(mod: str, artifact: str, text: str) -> None:
    stage = next(s for s in CFG.stages if any(a.artifact == artifact for a in s.produces))
    p = CFG.artifact_path(mod, stage.id, artifact, 1)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _columns(mod: str, *rows: str) -> str:
    return "# toy db\n\n" + "\n".join(rows) + "\n"


def _endpoint(mod: str, *lines: str) -> str:
    api = CFG.make_id("API", mod, 1)
    return f"# toy plan\n\n### {api} — book a visit\n" + "\n".join(lines) + "\n"


def _writer_findings(mod, an):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "required-writer"]


def test_toy_required_column_with_no_writer_is_a_finding(toy_writer):
    mod, art, an = toy_writer
    col = CFG.make_id("DBF", mod, 1)
    _write_art(mod, "db-script", _columns(mod, f"| {col} | visit_reason | MANDATORY |"))
    _write_art(mod, "backend-execution-plan", _endpoint(mod, "Intake : nothing much"))
    fs = _writer_findings(mod, an)
    assert len(fs) == 1 and col in fs[0].message, [str(f) for f in fs]
    assert "MANDATORY" in fs[0].message and "Intake" in fs[0].message


def test_toy_required_column_written_by_an_endpoint_passes(toy_writer):
    mod, art, an = toy_writer
    col = CFG.make_id("DBF", mod, 1)
    _write_art(mod, "db-script", _columns(mod, f"| {col} | visit_reason | MANDATORY |"))
    _write_art(mod, "backend-execution-plan", _endpoint(mod, f"Intake : body carries {col}"))
    assert _writer_findings(mod, an) == []
    # …and a column the endpoint sets itself rather than accepting counts too
    _write_art(mod, "backend-execution-plan", _endpoint(mod, "Intake : —", f"Follow-up : flips {col}"))
    assert _writer_findings(mod, an) == []


def test_toy_platform_filled_and_key_columns_are_exempt_by_profile(toy_writer):
    """The exemptions are profile ADDRESSES, and they match across spellings: the
    toy declares `loggedBy` and the database holds `logged_by`."""
    mod, art, an = toy_writer
    audit, pk = CFG.make_id("DBF", mod, 1), CFG.make_id("DBF", mod, 2)
    _write_art(mod, "db-script", _columns(mod, f"| {audit} | logged_by | MANDATORY |",
                                          f"| {pk} | visit_ref | MANDATORY |"))
    _write_art(mod, "backend-execution-plan", _endpoint(mod, "Intake : nothing"))
    assert _writer_findings(mod, an) == []


def test_toy_stated_exclusion_is_not_a_finding_but_silence_is(toy_writer):
    mod, art, an = toy_writer
    col = CFG.make_id("DBF", mod, 1)
    _write_art(mod, "db-script", _columns(mod, f"| {col} | visit_reason | MANDATORY | filled-by-the-clinic |"))
    _write_art(mod, "backend-execution-plan", _endpoint(mod, "Intake : nothing"))
    assert _writer_findings(mod, an) == []
    # the same reason stated on the PLAN's row for that column counts too
    _write_art(mod, "db-script", _columns(mod, f"| {col} | visit_reason | MANDATORY |"))
    _write_art(mod, "backend-execution-plan",
               _endpoint(mod, "Intake : nothing") + f"\n| {col} | filled-by-the-clinic |\n")
    assert _writer_findings(mod, an) == []


# ════════════════════════════════════════════════════════════════════════════
# G4 — a declared operation must resolve to an endpoint (both directions)
# ----------------------------------------------------------------------------
# The toy's operation vocabulary, its permission template and its present-token
# are all its own; the checker knows none of them.
# ════════════════════════════════════════════════════════════════════════════

TOY_ACTIONS = ["BOOK", "CANCEL", "REBOOK"]
TOY_PERM = "CAN_<AREA>_<ACTION>"


@pytest.fixture
def toy_ops(toy_analyzable):
    import render
    mod, art, an = toy_analyzable
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["conventions"] = {"security_model": {
        "page_registry": "CLINIC_VIEWS", "permission_pattern": TOY_PERM,
        "actions": list(TOY_ACTIONS), "gateway_action": "BOOK"}}
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.8", "check": "operation-resolves",
         "args": {"artifact": "prd", "resolves_to": "API",
                  "actions": "conventions.security_model.actions",
                  "declared": {"kind": "ENT", "label": "OFFERS"},
                  "matrix": {"present": "yes", "permission": "conventions.security_model.permission_pattern"}},
         "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _op_findings(mod, an):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "operation-resolves"]


def test_toy_declared_operation_with_no_endpoint_is_a_finding(toy_ops):
    mod, art, an = toy_ops
    ent, api = CFG.make_id("ENT", mod, 1), CFG.make_id("API", mod, 1)
    art.write_text(f"# toy prd\n\n### {ent} — Visit\nOFFERS : BOOK, CANCEL\n\n"
                   f"### {api} — BOOK a visit for {ent}\nbody\n", encoding="utf-8")
    fs = _op_findings(mod, an)
    assert len(fs) == 1 and "CANCEL" in fs[0].message and ent in fs[0].message, [str(f) for f in fs]
    assert "specified and never built" in fs[0].message


def test_toy_every_declared_operation_built_passes(toy_ops):
    mod, art, an = toy_ops
    ent = CFG.make_id("ENT", mod, 1)
    a1, a2 = CFG.make_id("API", mod, 1), CFG.make_id("API", mod, 2)
    art.write_text(f"# toy prd\n\n### {ent} — Visit\nOFFERS : BOOK, CANCEL\n\n"
                   f"### {a1} — BOOK a visit for {ent}\nbody\n\n"
                   f"### {a2} — CANCEL a visit for {ent}\nbody\n", encoding="utf-8")
    assert _op_findings(mod, an) == []


def _matrix(mod: str, api_cell: str, perm_cell: str) -> str:
    return ("# toy prd\n\n| Screen | Served by | BOOK | CANCEL |\n|---|---|---|---|\n"
            f"| Calendar | {api_cell} | yes {perm_cell} | |\n")


def test_toy_marked_matrix_cell_with_nothing_behind_it_is_a_finding(toy_ops):
    mod, art, an = toy_ops
    api = CFG.make_id("API", mod, 1)
    art.write_text(_matrix(mod, "—", ""), encoding="utf-8")
    fs = _op_findings(mod, an)
    assert len(fs) == 1 and "no `API` id" in fs[0].message and TOY_PERM in fs[0].message, [str(f) for f in fs]

    # an endpoint but no permission — still a finding, and only the missing half named
    art.write_text(_matrix(mod, api, ""), encoding="utf-8")
    fs = _op_findings(mod, an)
    assert len(fs) == 1 and "no `API` id" not in fs[0].message and TOY_PERM in fs[0].message

    # a permission for the WRONG action does not satisfy the cell
    art.write_text(_matrix(mod, api, "CAN_CALENDAR_CANCEL"), encoding="utf-8")
    fs = _op_findings(mod, an)
    assert len(fs) == 1 and "for `BOOK`" in fs[0].message, [str(f) for f in fs]


def test_toy_matrix_cell_with_endpoint_and_the_right_permission_passes(toy_ops):
    mod, art, an = toy_ops
    art.write_text(_matrix(mod, CFG.make_id("API", mod, 1), "CAN_CALENDAR_BOOK"), encoding="utf-8")
    assert _op_findings(mod, an) == []


def test_a_profile_with_no_operation_vocabulary_is_served_unchanged(toy_analyzable):
    mod, art, an = toy_analyzable
    assert CFG.profile.get("conventions.security_model.actions") is None
    assert an._c_operation_resolves(an.Ctx(mod, 1), {
        "artifact": "prd", "resolves_to": "API", "actions": "conventions.security_model.actions"}, "WARN") == []


# ════════════════════════════════════════════════════════════════════════════
# G5 — plan the bootstrap data, then check it exists
# ----------------------------------------------------------------------------
# The toy's section token, its item labels, its source words and its grant
# vocabulary are all its own. One item enumerates by a table column, the other by
# the toy's own permission template — the checker knows neither mechanism's words.
# ════════════════════════════════════════════════════════════════════════════

TOY_BOOTSTRAP = {
    "section": "OPENING STOCK",
    "items": [
        {"label": "roster code", "column": "Roster code", "declared_in": "prd", "source_label": "filled from"},
        {"label": "clearance", "names": "conventions.security_model.permission_pattern",
         "declared_in": "prd", "source_label": "handed to"},
    ],
}


@pytest.fixture
def toy_bootstrap(toy_ops):
    import render
    mod, art, an = toy_ops
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["conventions"]["security_model"]["grant_target"] = "duty rota"
    pdata["bootstrap_data"] = yaml.safe_load(yaml.safe_dump(TOY_BOOTSTRAP))
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"] = [cl for cl in spec["contracts"][0]["clauses"] if cl["id"] != "T1.8"]
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.9", "check": "bootstrap-complete",
         "args": {"artifact": "prd", "spec": "bootstrap_data", "when": "profile.bootstrap_data"},
         "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _boot_findings(mod, an):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "bootstrap-complete"]


_DECLARES = ("# toy prd\n\n| Roster code | Used by |\n|---|---|\n| NIGHT_SHIFT | the ward |\n\n"
             "The calendar screen needs CAN_CALENDAR_BOOK.\n")


def test_toy_lookup_key_with_no_seed_source_is_a_finding(toy_bootstrap):
    mod, art, an = toy_bootstrap
    art.write_text(_DECLARES + "\n## OPENING STOCK\n\nCLEARANCE  CAN_CALENDAR_BOOK │ handed to: the ward rota\n",
                   encoding="utf-8")
    fs = _boot_findings(mod, an)
    assert len(fs) == 1 and "NIGHT_SHIFT" in fs[0].message and "roster code" in fs[0].message, [str(f) for f in fs]
    assert "fails on a fresh deployment" in fs[0].message


def test_toy_row_that_names_no_source_creates_nothing(toy_bootstrap):
    mod, art, an = toy_bootstrap
    art.write_text(_DECLARES + "\n## OPENING STOCK\n\nROSTER CODE  NIGHT_SHIFT\n"
                                "CLEARANCE  CAN_CALENDAR_BOOK │ handed to: the ward rota\n", encoding="utf-8")
    fs = _boot_findings(mod, an)
    assert len(fs) == 1 and "names no `filled from`" in fs[0].message, [str(f) for f in fs]


def test_toy_bootstrap_that_covers_everything_passes(toy_bootstrap):
    mod, art, an = toy_bootstrap
    art.write_text(_DECLARES + "\n## OPENING STOCK\n\nROSTER CODE  NIGHT_SHIFT │ filled from: the ward seed script\n"
                                "CLEARANCE  CAN_CALENDAR_BOOK │ handed to: the ward rota\n", encoding="utf-8")
    assert _boot_findings(mod, an) == []


def test_toy_missing_bootstrap_section_is_one_finding_per_item(toy_bootstrap):
    """The shipped shape: the plan carries structure and behaviour and nothing at
    all about the data either depends on."""
    mod, art, an = toy_bootstrap
    art.write_text(_DECLARES, encoding="utf-8")
    fs = _boot_findings(mod, an)
    assert len(fs) == 2 and all("carries no `OPENING STOCK` section" in f.message for f in fs), [str(f) for f in fs]


def test_the_toy_grant_target_is_the_toys_own_word(toy_bootstrap):
    """`grant_target` is the thing a permission is granted TO, and it is the
    project's word — the schema and the engines never spell it."""
    assert CFG.profile.get("conventions.security_model.grant_target") == "duty rota"


def test_a_profile_with_no_bootstrap_data_is_served_unchanged(toy_analyzable):
    mod, art, an = toy_analyzable
    assert CFG.profile.get("bootstrap_data") is None
    with pytest.raises(an.ClauseSkipped):
        an._c_bootstrap_complete(an.Ctx(mod, 1), {"artifact": "prd", "spec": "bootstrap_data"}, "WARN")


# ════════════════════════════════════════════════════════════════════════════
# G6 — the last free choice in a template, removed
# ----------------------------------------------------------------------------
# A template that offers the author "A | B" gets an answer that contradicts the
# platform's own architecture, and no check knows what the right answer was.
# ════════════════════════════════════════════════════════════════════════════

def _exec_brief(toy, stage_id: str) -> str:
    import shutil
    import dispatch as dp
    from conftest import REAL_ROOT
    if not (toy.root / "engines").exists():
        shutil.copytree(REAL_ROOT / "engines", toy.root / "engines")
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    return dp.render_engine(CFG.stage(stage_id), mod, 1)


def test_the_cross_module_interface_is_rendered_not_offered(toy):
    """The rendered line states the profile's declared mechanism and offers the
    author no menu. The toy declares the opposite value to the profile on disk."""
    out = _exec_brief(toy, "P3.1")
    assert "{{" not in out and "{%" not in out
    mine = TOY["conventions"]["module_interface"]
    assert f"profile.conventions.module_interface: {mine}" in out, "the toy's own answer is not rendered"
    other = toy.load_profile(toy.data["factory"]["active_profile"]).get("conventions.module_interface")
    assert other and other != mine
    assert f"module_interface: {other}" not in out, "the brief carries the OTHER profile's answer"
    assert "DB foreign key | REST call" not in out, "the author is still offered a menu"


def test_a_profile_declaring_no_interface_still_gets_a_sensible_instruction(toy):
    """The else-branch: no declaration → an instruction, never a silent default
    and never a choice."""
    import yaml as _y
    prof = CFG.profiles_dir() / "toy.yaml"
    data = _y.safe_load(prof.read_text(encoding="utf-8"))
    data["conventions"].pop("module_interface")
    prof.write_text(_y.safe_dump(data, sort_keys=False), encoding="utf-8")
    CFG.reload(profile_id="toy")
    out = _exec_brief(toy, "P3.1")
    assert "the single access mechanism" in out and "profile.conventions.module_interface" in out
    assert "DB foreign key | REST call" not in out


# ════════════════════════════════════════════════════════════════════════════
# G7 — every catalogued query must be referenced
# ----------------------------------------------------------------------------
# No new check: `orphans` is exactly this question, asked in the direction the
# QRC's own four assertions never ran.
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def toy_catalog(toy_analyzable):
    import render
    mod, art, an = toy_analyzable
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.10", "check": "orphans",
         "args": {"kind": "QR", "referenced_by": ["API"], "min": 1}, "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _orphan_findings(mod, an):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.check == "orphans"]


def test_toy_catalogued_query_nobody_runs_is_a_finding(toy_catalog):
    mod, art, an = toy_catalog
    qr, dead, api = CFG.make_id("QR", mod, 1), CFG.make_id("QR", mod, 2), CFG.make_id("API", mod, 1)
    art.write_text(f"# toy prd\n\n### {qr} — find the visit\n\n### {dead} — nobody runs this\n\n"
                   f"### {api} — book a visit\nRepository : {qr}\n", encoding="utf-8")
    fs = _orphan_findings(mod, an)
    assert len(fs) == 1 and dead in fs[0].message and "API" in fs[0].message, [str(f) for f in fs]


def test_toy_catalog_reached_in_both_directions_passes(toy_catalog):
    mod, art, an = toy_catalog
    qr, api = CFG.make_id("QR", mod, 1), CFG.make_id("API", mod, 1)
    art.write_text(f"# toy prd\n\n### {qr} — find the visit\n\n"
                   f"### {api} — book a visit\nRepository : {qr}\n", encoding="utf-8")
    assert _orphan_findings(mod, an) == []


# ════════════════════════════════════════════════════════════════════════════
# G8 — a later stage may mint a cross-module row, and must back-register it
# ----------------------------------------------------------------------------
# Equality made the right answer illegal: the dependency is introduced AFTER the
# register is frozen, so the row was simply left out and nothing tracked it.
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def toy_xm(toy_analyzable):
    """Two `registry-agree` clauses over one atom, in the two directions: the
    register ⊆ the plan (placement), and the plan ⊆ the register (back-registration)."""
    import render
    mod, art, an = toy_analyzable
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"] += [
        {"id": "T1.11", "check": "registry-agree",
         "args": {"artifact": "prd", "registry": "registry-db", "kinds": ["XM"],
                  "direction": "registry→artifact"}, "severity": "WARN"},
        {"id": "T1.12", "check": "registry-agree",
         "args": {"artifact": "prd", "registry": "registry-db", "kinds": ["XM"],
                  "direction": "artifact→registry"}, "severity": "WARN"},
    ]
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _xm_findings(mod, an, clause):
    import state as st
    st.build_state(mod, 1)
    return [f for f in an.run(mod, 1, scope="all", write=False).findings if f.clause == clause]


def test_toy_minted_cross_module_row_passes_placement_and_fails_back_registration(toy_xm):
    mod, art, an = toy_xm
    declared, minted = CFG.make_id("XM", mod, 1), CFG.make_id("XM", mod, 2)
    _write_art(mod, "registry-db", f"# toy register\n\n- {declared}\n")
    art.write_text(f"# toy prd\n\n### {declared} — the frozen one\n\n### {minted} — found by a later role\n",
                   encoding="utf-8")
    assert _xm_findings(mod, an, "T1.11") == [], "placement: every registered row IS placed"
    fs = _xm_findings(mod, an, "T1.12")
    assert len(fs) == 1 and minted in fs[0].message and "absent from" in fs[0].message, [str(f) for f in fs]


def test_toy_minted_row_that_is_back_registered_passes_both(toy_xm):
    mod, art, an = toy_xm
    declared, minted = CFG.make_id("XM", mod, 1), CFG.make_id("XM", mod, 2)
    _write_art(mod, "registry-db", f"# toy register\n\n- {declared}\n- {minted}\n")
    art.write_text(f"# toy prd\n\n### {declared} — the frozen one\n\n### {minted} — found by a later role\n",
                   encoding="utf-8")
    assert _xm_findings(mod, an, "T1.11") == [] and _xm_findings(mod, an, "T1.12") == []


def test_toy_registered_row_the_plan_never_places_is_still_a_finding(toy_xm):
    """Relaxing to a superset must not relax the direction that was doing work."""
    mod, art, an = toy_xm
    declared = CFG.make_id("XM", mod, 1)
    _write_art(mod, "registry-db", f"# toy register\n\n- {declared}\n")
    art.write_text("# toy prd\n\nnothing placed here\n", encoding="utf-8")
    fs = _xm_findings(mod, an, "T1.11")
    assert len(fs) == 1 and declared in fs[0].message, [str(f) for f in fs]


# ════════════════════════════════════════════════════════════════════════════
# G10 — concurrency is asked once, per mutating endpoint
# ----------------------------------------------------------------------------
# Not mechanically checkable, and no check pretends to verify it: the template
# asks the question and the reviewer has a row for it.
# ════════════════════════════════════════════════════════════════════════════

def test_the_endpoint_and_query_templates_ask_the_concurrency_question(toy):
    out = _exec_brief(toy, "P3.1")
    assert "Concurrency  :" in out, "the endpoint block does not ask about two simultaneous requests"
    assert "Locking      :" in out, "the query catalog entry does not ask what stops a repeated read"
    assert "both validate, both pass, both write" in out, "the template accepts 'validated first' as an answer"


def test_the_reviewer_carries_a_concurrency_row(toy):
    from conftest import REAL_ROOT
    text = (REAL_ROOT / CFG.paths["reviewers"] / "pass-review.md").read_text(encoding="utf-8")
    row = next((l for l in text.splitlines() if l.startswith("| concurrency:")), None)
    assert row and "two simultaneous requests" in row, "the gate brief has no concurrency row"
    assert "nothing mechanical can check this" in row, "the row must say it is the reviewer's, not a check's"


# ════════════════════════════════════════════════════════════════════════════
# G11 — a channel for findings that belong to no module
# ----------------------------------------------------------------------------
# The category list is a FACTORY fact read from the shared schema, not a literal
# in Python, so a factory that adds one needs no checker change: `registry-agree
# categories: all` demands it of whatever registry the project declares.
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def toy_categories(toy_analyzable):
    """The toy factory gets the real shared schema and a contract clause that
    demands every category of it be mapped in the toy's own registry."""
    import shutil
    import render
    from conftest import REAL_ROOT
    mod, art, an = toy_analyzable
    # only the category schema — the toy's own contract document already lives here
    schema = "REGISTRY-SCHEMA.md"
    dest = CFG.dir("shared")
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REAL_ROOT / CFG.paths["shared"] / schema, dest / schema)
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.13", "check": "registry-agree",
         "args": {"registry": "project-registry", "categories": "all"}, "severity": "WARN"})
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def _platform_category(an) -> str:
    """The category the schema declares for findings that belong to no module —
    found by its meaning in the schema, never by a number typed here."""
    doc = (CFG.dir("shared") / "REGISTRY-SCHEMA.md").read_text(encoding="utf-8")
    import re
    row = next(l for l in doc.splitlines() if "platform findings" in l.lower() and l.startswith("|"))
    # whole-token, longest-first: `CAT-1` is a substring of `CAT-10`, and picking the
    # short one would have the test remove a category the text still contains
    return max((c for c in an._categories() if re.search(re.escape(c) + r"(?!\d)", row)), key=len)


def test_a_registry_that_maps_no_platform_findings_category_is_a_finding(toy_categories):
    import state as st
    mod, art, an = toy_categories
    cats = an._categories()
    platform = _platform_category(an)
    assert platform in cats, "the shared schema declares no category for platform findings"

    _write_art(mod, "project-registry", "# toy registry\n\n" + "\n".join(f"- {c} → §1" for c in sorted(cats - {platform})))
    st.build_state(mod, 1)
    fs = [f for f in an.run(mod, 1, scope="all", write=False).findings if f.clause == "T1.13"]
    assert len(fs) == 1 and platform in fs[0].message, [str(f) for f in fs]

    _write_art(mod, "project-registry", "# toy registry\n\n" + "\n".join(f"- {c} → §1" for c in sorted(cats)))
    st.build_state(mod, 1)
    assert [f for f in an.run(mod, 1, scope="all", write=False).findings if f.clause == "T1.13"] == []


def test_a_category_is_matched_as_a_whole_token(toy_categories):
    """A plain substring test passed any category whose name is a prefix of
    another's — the moment the schema reached two digits, a registry that mapped
    the tenth satisfied the first as well."""
    import state as st
    mod, art, an = toy_categories
    cats = an._categories()
    longest = max(cats, key=len)
    prefixes = [c for c in cats if c != longest and longest.startswith(c)]
    assert prefixes, "no category name is a prefix of another — nothing to guard"
    _write_art(mod, "project-registry", "# toy registry\n\n- " + longest + " → §1\n")
    st.build_state(mod, 1)
    fs = [f for f in an.run(mod, 1, scope="all", write=False).findings if f.clause == "T1.13"]
    assert len(fs) == 1 and all(c in fs[0].message for c in prefixes), [str(f) for f in fs]


def test_the_schema_says_a_module_scoped_stage_records_and_never_fixes(toy_categories):
    doc = (CFG.dir("shared") / "REGISTRY-SCHEMA.md").read_text(encoding="utf-8")
    assert "records** a platform finding; it never fixes one" in doc
    assert "is **not** a module gap" in doc, "nothing stops it being read as a module gap"


# ════════════════════════════════════════════════════════════════════════════
# G12 — a quotation carries its source
# ----------------------------------------------------------------------------
# A standing rule, not a check: a generated artifact quoted text as one module's
# requirement that exists only in another module's file, and by the time it was
# found the artifact was immutable, so the false attribution is permanent.
# ════════════════════════════════════════════════════════════════════════════

def test_the_shared_rules_require_a_quotation_to_carry_its_source(toy):
    from conftest import REAL_ROOT
    doc = (REAL_ROOT / CFG.paths["shared"] / "GOVERNANCE-CORE.md").read_text(encoding="utf-8")
    assert "A quotation carries its source" in doc
    assert "paraphrase" in doc, "the rule offers no alternative to quoting with a source"


def test_every_engine_brief_loads_the_shared_rules_that_carry_it(toy):
    """The rule is only binding where it is read: every engine brief loads the
    core rules document, under the toy profile as under any other."""
    import shutil
    import dispatch as dp
    from conftest import REAL_ROOT
    for d in ("engines", "standalone"):
        if not (toy.root / d).exists():
            shutil.copytree(REAL_ROOT / d, toy.root / d)
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    for stage in CFG.stages:          # the governed line: every artifact that can quote another
        if not (toy.root / "engines" / stage.id / "references" / "ENGINE.md").exists():
            continue
        assert "GOVERNANCE-CORE.md" in dp.render_engine(stage, mod, 1), stage.id


# ════════════════════════════════════════════════════════════════════════════
# G13 — every self-check row names the check that backs it
# ----------------------------------------------------------------------------
# A row nothing can falsify manufactures confidence: four rows of the shipped
# block were false and the verdict beneath them said PASSED.
# ════════════════════════════════════════════════════════════════════════════

def _self_check_rows(brief: str, block_token: str) -> list[str]:
    """The rows of the rendered self-check block: the fenced section headed by the
    profile's own block token, minus its header and its verdict line."""
    lines = brief.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith(block_token + " —"))
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("```"))
    return [l for l in lines[start + 1:end] if l.strip() and not l.startswith("row ")]


def test_every_self_check_row_names_a_check_that_analyze_implements(toy):
    """The decisive one. Every row of every rendered self-check block names a check
    from `analyze.CHECKS`, or is the explicitly-marked report row. A row backed by
    nothing is not softened — it is not there."""
    import analyze as an
    import yaml as _y
    prof = CFG.profiles_dir() / "toy.yaml"
    data = _y.safe_load(prof.read_text(encoding="utf-8"))
    data["self_check"] = dict(TOY_SELF_CHECK)
    prof.write_text(_y.safe_dump(data, sort_keys=False), encoding="utf-8")
    CFG.reload(profile_id="toy")
    block, label = TOY_SELF_CHECK["block"], TOY_SELF_CHECK["verdict_label"]
    for sid in (s.id for s in CFG.stages if s.track):
        rows = _self_check_rows(_exec_brief(toy, sid), block)
        assert rows, f"{sid}: no self-check rows rendered"
        for row in rows:
            if row.startswith(label):
                continue
            named = [c for c in an.CHECKS if c in row]
            assert named or "(the report)" in row, f"{sid}: row backed by nothing — {row!r}"


def test_no_self_check_row_asserts_a_dimension_no_check_examines(toy):
    """The rows deleted in this round, by name: each described something real and
    nothing could falsify any of them."""
    for sid in (s.id for s in CFG.stages if s.track):
        out = _exec_brief(toy, sid)
        for gone in ("no placeholder table/column", 'no "see SRS"',
                     "layers declared │ domain placement declared",
                     "no BLOCKED ADR left unsurfaced", "tree routes before :id",
                     "no hard-coded message", "no enum models"):
            assert gone not in out, f"{sid}: an unfalsifiable self-check row survives — {gone!r}"


def test_a_profile_that_states_no_required_marker_skips_the_writer_clause(toy_writer):
    """The notation for "this column is required" is a PROJECT fact: the contract
    set is shared across every profile, so a marker spelled there would be one
    stack's notation imposed on all of them. Undeclared → the clause does not run."""
    mod, art, an = toy_writer
    col = CFG.make_id("DBF", mod, 1)
    _write_art(mod, "db-script", _columns(mod, f"| {col} | visit_reason | MANDATORY |"))
    _write_art(mod, "backend-execution-plan", _endpoint(mod, "Intake : nothing"))
    assert len(_writer_findings(mod, an)) == 1
    prof = CFG.profiles_dir() / "toy.yaml"
    pdata = yaml.safe_load(prof.read_text(encoding="utf-8"))
    pdata["stack"]["db"].pop("required_marker")
    prof.write_text(yaml.safe_dump(pdata, sort_keys=False), encoding="utf-8")
    CFG.reload(profile_id="toy")
    assert _writer_findings(mod, an) == []


# ════════════════════════════════════════════════════════════════════════════
# A clause that could not run is never silent
# ----------------------------------------------------------------------------
# Every check whose vocabulary comes from the profile used to return "no
# findings" when the address resolved to nothing. A check that never ran and a
# check that looked and found nothing printed the same line — and a MISTYPED
# address printed the same line as a deliberate omission. Both read as a pass.
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def toy_typo(toy_analyzable):
    """A clause naming an address this profile does not declare — exactly what a
    typo in a contract looks like from the outside."""
    import render
    mod, art, an = toy_analyzable
    doc = render.contracts_path(CFG)
    spec = yaml.safe_load(doc.read_text(encoding="utf-8").split("---")[1])
    spec["contracts"][0]["clauses"].append(
        {"id": "T1.14", "check": "count-agrees",
         "args": {"spec": "declared_totalz"}, "severity": "HALT"})      # note the typo
    doc.write_text("---\n" + yaml.safe_dump(spec, sort_keys=False) + "---\n\n# toy contracts\n", encoding="utf-8")
    CFG.reload(profile_id="toy")
    return mod, art, an


def test_a_clause_whose_address_resolves_to_nothing_says_so(toy_typo):
    mod, art, an = toy_typo
    rep = an.run(mod, 1, scope="all", write=False)
    assert [f for f in rep.findings if f.clause == "T1.14"] == [], "a missing convention is not a finding"
    skipped = [s for s in rep.skipped if s.startswith("T1.14")]
    assert len(skipped) == 1, rep.skipped
    assert "declared_totalz" in skipped[0] and "enforced nothing" in skipped[0], skipped[0]
    assert rep.coverage.get("T1.14") == 0 and "T1.14" in rep.vacuous(), rep.coverage


def test_the_skip_survives_into_the_report_a_gate_reads(toy_typo):
    """The report is what a pipeline gates on; a skip that reached only the
    terminal is a skip nobody acts on."""
    import json
    mod, art, an = toy_typo
    an.run(mod, 1, scope="all")
    data = json.loads(an.report_json_path(mod, 1, "all").read_text(encoding="utf-8"))
    assert any("declared_totalz" in s for s in data["skipped"])
    assert "T1.14" in data["vacuous"]


def test_a_deliberate_omission_is_still_free_and_visible_as_such(toy_totals):
    """Declaring the convention makes the clause run; `when:` is how a contract
    suppresses one on purpose, and that is visible in the contract itself."""
    mod, art, an = toy_totals
    rep = an.run(mod, 1, scope="all", write=False)
    assert not [s for s in rep.skipped if "declared_totals" in s]
