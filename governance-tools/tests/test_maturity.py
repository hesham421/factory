"""Maturity clauses — the machine sees what the reviewer used to be the only one
to see: an ambiguous word, an unfalsifiable Then, an entity nothing deletes, a
feature with no unwanted path, a screen with no empty state, a glossary term
spelled three ways. Every one fires at `factory.yaml → analyze.maturity_severity`
(MINOR by default: recorded, never closing a gate), and the one knob re-tunes
them all. Plus the coverage ratios: in the report, the gate record and the
module's execution state — one number, three readers.
"""
from __future__ import annotations

import json

from config import CFG
import analyze as an
import orchfx as fx
from test_orchestrator import orch_root, _run_pass1, _consumer  # noqa: F401 (fixture reuse)


def _p1(mod):
    for s in ("domain-profile", "P-1", "P0", "P0.5"):
        fx.write_stage(s, mod)
    return fx.write_stage("P1", mod)


def _srs(mod):
    return CFG.artifact_path(mod, "P1", "srs", 1)


def _by_check(rep, check):
    return [f for f in rep.findings if f.check == check]


def test_the_seeded_fixture_is_clean_and_every_maturity_finding_is_at_the_knob(orch_root, mod):
    _p1(mod)
    rep = an.run(mod, 1, scope="stage:P1")
    knob = CFG.analyze["maturity_severity"]
    maturity = {"ambiguity", "ac-measurable", "crud-covered", "feature-unwanted", "glossary"}
    assert rep.clean, [str(f) for f in rep.findings]
    assert all(f.severity == knob for f in rep.findings if f.check in maturity)
    assert knob not in CFG.analyze["blocking"], "the default knob must not close a gate"


def test_ambiguity_lexicon_fires_on_a_requirement_statement(orch_root, mod):
    _p1(mod)
    srs = _srs(mod)
    word = next(w for w in CFG.analyze["maturity"]["ambiguity_lexicon"]["en"] if " " not in w)
    srs.write_text(srs.read_text(encoding="utf-8").replace(
        "the system shall validate and store the record.", f"the system shall validate and store the record {word}.", 1), encoding="utf-8")
    rep = an.run(mod, 1, scope="stage:P1")
    hits = _by_check(rep, "ambiguity")
    assert len(hits) == 1 and word in hits[0].message and hits[0].severity == CFG.analyze["maturity_severity"]
    assert rep.clean


def test_a_profile_extends_the_lexicon_and_a_rationale_line_is_not_read(orch_root, mod):
    _p1(mod)
    srs = _srs(mod)
    CFG.profile.data.setdefault("review", {})["ambiguity_lexicon"] = {"en": ["promptly"]}
    text = srs.read_text(encoding="utf-8")
    text = text.replace("  Pattern    : event\n", "  Pattern    : event\n  Rationale  : usually wanted promptly\n", 1)
    srs.write_text(text, encoding="utf-8")
    assert not _by_check(an.run(mod, 1, scope="stage:P1"), "ambiguity"), "a rationale may say 'usually'; only the statement is read"
    srs.write_text(text.replace("validate and store the record.", "validate and store the record promptly.", 1), encoding="utf-8")
    assert any("promptly" in f.message for f in _by_check(an.run(mod, 1, scope="stage:P1"), "ambiguity"))


def test_an_unmeasurable_then_is_a_finding(orch_root, mod):
    _p1(mod)
    srs = _srs(mod)
    srs.write_text(srs.read_text(encoding="utf-8").replace("  Then   : the record is stored", "  Then   : the system behaves correctly", 1), encoding="utf-8")
    hits = _by_check(an.run(mod, 1, scope="stage:P1"), "ac-measurable")
    assert len(hits) == 1 and fx.mid("AC", mod, 1) in hits[0].message
    # a number, an id or a name=value each make it measurable
    for outcome in ("within 2 seconds the page changes", f"{fx.mid('ENT', mod, 1)} is written", "archivedFlag=false afterwards"):
        srs.write_text(srs.read_text(encoding="utf-8").replace("the system behaves correctly", outcome, 1), encoding="utf-8")
        assert not _by_check(an.run(mod, 1, scope="stage:P1"), "ac-measurable"), outcome
        srs.write_text(srs.read_text(encoding="utf-8").replace(outcome, "the system behaves correctly", 1), encoding="utf-8")


def test_an_entity_whose_requirements_cover_no_lifecycle_group_is_a_finding(orch_root, mod):
    _p1(mod)
    hits = _by_check(an.run(mod, 1, scope="stage:P1"), "crud-covered")
    # the fixture's two requirements only ever store (create) the entity
    assert len(hits) == 1 and fx.mid("ENT", mod, 1) in hits[0].message and "read" in hits[0].message
    srs = _srs(mod)
    text = srs.read_text(encoding="utf-8").replace(
        "When a user submits form 2, the system shall validate and store the record.",
        "When a user submits form 2, the system shall list, update and deactivate the record.", 1)
    srs.write_text(text, encoding="utf-8")
    assert not _by_check(an.run(mod, 1, scope="stage:P1"), "crud-covered")


def test_a_feature_group_with_no_unwanted_path_is_a_finding(orch_root, mod):
    _p1(mod)
    hits = _by_check(an.run(mod, 1, scope="stage:P1"), "feature-unwanted")
    assert {fx.mid("US", mod, 1), fx.mid("US", mod, 2)} == {f.message.split("`")[1] for f in hits}
    srs = _srs(mod)
    srs.write_text(srs.read_text(encoding="utf-8").replace(
        "When a user submits form 2, the system shall validate and store the record.",
        "If the form is incomplete, then the system shall reject it with the missing fields.", 1), encoding="utf-8")
    rep = an.run(mod, 1, scope="stage:P1")
    assert [f.message.split("`")[1] for f in _by_check(rep, "feature-unwanted")] == [fx.mid("US", mod, 1)]


def test_glossary_variants_and_synonyms_are_findings(orch_root, mod):
    _p1(mod)
    glossary = CFG.profile.vocabulary["glossary"]
    # a separator variant exists for a multi-word term, a case variant for an acronym;
    # an ordinary single word is left alone (prose lowercases it legitimately)
    term = next((t for t in glossary if " " in t or (t.isupper() and len(t) >= 2)), next(iter(glossary)))
    CFG.profile.data["vocabulary"]["glossary_synonyms"] = {term: ["thingamajig"]}
    srs = _srs(mod)
    variant = term.replace(" ", "-") if " " in term else (term.lower() if term.isupper() else term)
    srs.write_text(srs.read_text(encoding="utf-8") + f"\nNote: the {variant} and the thingamajig are the same {term}.\n", encoding="utf-8")
    hits = _by_check(an.run(mod, 1, scope="stage:P1"), "glossary")
    variants = {f.message.split("`")[1] for f in hits}
    assert "thingamajig" in variants
    if variant != term:
        assert variant in variants
    assert all(f.artifact == "srs" for f in hits)


def test_a_screen_without_its_states_is_a_finding_and_the_engine_line_clears_it(orch_root, mod, tmp_path, monkeypatch):
    _consumer(tmp_path, monkeypatch, "backend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    fx.write_input("api-docs", mod)
    fx.write_stage("P3.2", mod)
    hits = _by_check(an.run(mod, 1, scope="stage:P3.2"), "screen-states")
    assert len(hits) == 1 and fx.mid("SCR", mod, 1) in hits[0].message
    spec = CFG.analyze["maturity"]["screen_states"]
    ux = CFG.artifact_path(mod, "P3.2", "ui-ux-spec", 1)
    ux.write_text(ux.read_text(encoding="utf-8").replace(
        f"### {fx.mid('SCR', mod, 1)} — main screen",
        f"### {fx.mid('SCR', mod, 1)} — main screen\n  {spec['label']}   : {' · '.join(spec['required'])}", 1), encoding="utf-8")
    assert not _by_check(an.run(mod, 1, scope="stage:P3.2"), "screen-states")


def test_a_screen_that_never_says_where_its_secondary_detail_sits_is_a_finding(
        orch_root, mod, tmp_path, monkeypatch):
    """C9.17. A screen opened to edit ONE record grows a second job inline — a
    picker, a repeating child-row editor — and a second save beside the first,
    and the user who presses the first leaves without the second. The spec had no
    line on which that could be said; now a screen without one is a finding, and
    a screen with one that commits to no placement is a finding too."""
    _consumer(tmp_path, monkeypatch, "backend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    fx.write_input("api-docs", mod)
    fx.write_stage("P3.2", mod)
    scr, spec = fx.mid("SCR", mod, 1), CFG.analyze["maturity"]["screen_composition"]
    hits = _by_check(an.run(mod, 1, scope="stage:P3.2"), "screen-composition")
    assert len(hits) == 1 and scr in hits[0].message

    ux = CFG.artifact_path(mod, "P3.2", "ui-ux-spec", 1)
    heading = f"### {scr} — main screen"
    def _line(body):
        ux.write_text(ux.read_text(encoding="utf-8").replace(
            heading, f"{heading}\n  {spec['label']}   : {body}", 1), encoding="utf-8")
        return _by_check(an.run(mod, 1, scope="stage:P3.2"), "screen-composition")
    original = ux.read_text(encoding="utf-8")

    # the line is there and names the required word, but commits to no placement
    hits = _line(f"{spec['required'][0]}: one")
    assert len(hits) == 1 and "chooses none of" in hits[0].message

    # a placement with no submit count is the other half of the same silence
    ux.write_text(original, encoding="utf-8")
    hits = _line(str(spec["one_of"][1]))
    assert len(hits) == 1 and spec["required"][0] in hits[0].message

    # both, and the screen has committed
    ux.write_text(original, encoding="utf-8")
    assert not _line(f"secondary detail → {spec['one_of'][1]} · {spec['required'][0]}: one")


def test_a_profile_that_does_not_declare_the_convention_is_not_charged_for_it(
        orch_root, mod, tmp_path, monkeypatch):
    """`when:` — the clause is the project's to adopt. A profile without
    `conventions.screen_composition` gets no finding and no rendered line, so the
    toolkit stays agnostic (the same guarantee `composite_screen` already has)."""
    _consumer(tmp_path, monkeypatch, "backend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    fx.write_input("api-docs", mod)
    fx.write_stage("P3.2", mod)
    monkeypatch.delitem(CFG.profile.data["conventions"], "screen_composition")
    assert not _by_check(an.run(mod, 1, scope="stage:P3.2"), "screen-composition")


def test_the_one_knob_retunes_every_maturity_clause(orch_root, mod):
    _p1(mod)
    top = CFG.analyze["severities"][0]
    CFG.data["analyze"]["maturity_severity"] = top
    rep = an.run(mod, 1, scope="stage:P1")
    hits = [f for f in rep.findings if f.check in ("crud-covered", "feature-unwanted")]
    assert hits and all(f.severity == top for f in hits)
    assert not rep.clean, "raised to a blocking severity, the same findings close the stage"


def test_coverage_ratios_reach_the_report_the_gate_record_and_the_execution_state(orch_root, mod, tmp_path, monkeypatch):
    _consumer(tmp_path, monkeypatch, "backend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    rep = an.run(mod, 1, scope="all")
    ids = [m["id"] for m in CFG.analyze["coverage"]]
    assert [m["id"] for m in rep.metrics] == ids
    by = {m["id"]: m for m in rep.metrics}
    assert by["us-req"]["pct"] == 100.0 and by["req-ac"]["pct"] == 100.0 and by["req-api"]["pct"] == 100.0
    assert by["req-ux"]["pct"] == 0.0, "no design stage has run yet"
    md = an.report_json_path(mod, 1, "all").with_suffix(".md").read_text(encoding="utf-8")
    assert "traceability ratios" in md and "us-req" in md
    rec = json.loads((CFG.version_root(mod, 1) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": "1"})).with_suffix(".json").read_text(encoding="utf-8"))
    assert [m["id"] for m in rec["coverage"]] == ids
    state = json.loads((CFG.module_root(mod) / CFG.paths["module"]["manifest_file"]).read_text(encoding="utf-8"))
    assert state["status"]["coverage"]["us-req"] == 100.0
