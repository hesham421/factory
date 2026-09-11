"""
The main issue behind every "silent success" this repo has had to patch one at a
time: a check that reports no finding over ZERO subjects prints the same line as
one reporting no finding over five hundred.

Each instance was fixed on its own as it was found — `verify` calling an empty
digest compare ok; a plan with no phase block splitting "successfully"; a DTO
column resolving four wrong names by substring; a screen-to-UXD clause that stops
enforcing the moment a module mints no UXD. The instances share one shape, and the
shape was invisible in every output the tool produced.

These tests pin the general answer: a clause records how many subjects it examined,
and a clause that examined none is named — in the CLI line, in the markdown report
and in the JSON. Zero is not declared a defect; a ROOT module really does own no
cross-module id. It is declared VISIBLE.
"""
from __future__ import annotations

import json

import pytest

import analyze as an


def test_a_clause_that_examined_nothing_is_listed():
    rep = an.AnalyzeReport(mod="SEC", version=1, scope="all")
    rep.coverage = {"C9.6": 0, "C9.7": 10, "C6.3": 0}
    assert rep.vacuous() == ["C6.3", "C9.6"]


def test_a_clause_with_subjects_is_not_listed():
    rep = an.AnalyzeReport(mod="SEC", version=1, scope="all")
    rep.coverage = {"C5.3": 33, "C7.3": 27}
    assert rep.vacuous() == []


def test_a_check_reporting_no_count_is_absent_rather_than_zero():
    """Absent from coverage and having counted zero are different facts. Only
    checks that opt in via `counts_subjects` are tracked, so the vacuous list
    never fills with checks that simply do not count."""
    rep = an.AnalyzeReport(mod="SEC", version=1, scope="all")
    assert rep.coverage == {}
    assert rep.vacuous() == []


def test_the_counting_checks_declare_themselves():
    """Every check that iterates a subject set reports its size — otherwise it can
    verify nothing and still print clean, which is the defect this file is about."""
    counting = {k for k, v in an.CHECKS.items() if getattr(v, "counts_subjects", False)}
    assert {"traces", "orphans", "registry-agree", "forward-refs", "endpoint-agrees"} <= counting


# ── the instrumentation actually fires ──────────────────────────────────────

def test_orphans_counts_the_targets_it_iterates(monkeypatch):
    """`orphans` over zero targets is the exact shape that let a screens-to-UXD
    clause stop enforcing silently when a module minted no UXD."""
    class _Ctx:
        mod = "SEC"
        def __init__(self):
            self._examined = 0
        def saw(self, n):
            self._examined += n
        def records_of(self, kind):
            return []
        def artifact(self, name):
            return None
        def text(self, name):
            return ""
    ctx = _Ctx()
    out = an._c_orphans(ctx, {"kind": "UXD", "referenced_by": ["frontend-execution-plan"], "min": 1}, "MAJOR")
    assert out == [], "no targets means no findings — that part was always true"
    assert ctx._examined == 0, "and now the run can SAY it checked nothing"


def test_evaluate_records_coverage_per_clause():
    class _Ctx:
        def __init__(self):
            self._examined = 0
        def saw(self, n):
            self._examined += n

    def fake(ctx, args, sev):
        ctx.saw(7)
        return []
    fake.counts_subjects = True

    rep = an.AnalyzeReport(mod="SEC", version=1, scope="all")
    ctx = _Ctx()
    an._evaluate(ctx, fake, {"id": "C9.9", "check": "traces", "severity": "MAJOR"}, {}, rep)
    assert rep.coverage == {"C9.9": 7}
    assert rep.clause_checks == {"C9.9": "traces"}


def test_coverage_resets_between_clauses():
    """A clause must not inherit the previous clause's count — that would hide a
    vacuous clause behind a busy one."""
    class _Ctx:
        def __init__(self):
            self._examined = 0
        def saw(self, n):
            self._examined += n

    def busy(ctx, args, sev):
        ctx.saw(50)
        return []
    def idle(ctx, args, sev):
        return []
    busy.counts_subjects = idle.counts_subjects = True

    rep = an.AnalyzeReport(mod="SEC", version=1, scope="all")
    ctx = _Ctx()
    an._evaluate(ctx, busy, {"id": "A", "check": "traces", "severity": "MAJOR"}, {}, rep)
    an._evaluate(ctx, idle, {"id": "B", "check": "orphans", "severity": "MAJOR"}, {}, rep)
    assert rep.coverage == {"A": 50, "B": 0}
    assert rep.vacuous() == ["B"]


def test_a_raising_clause_does_not_record_coverage():
    """A clause that blew up examined nothing, but it already reports itself as a
    finding; recording it as vacuous too would double-count one defect."""
    def boom(ctx, args, sev):
        raise ValueError("nope")
    boom.counts_subjects = True

    class _Ctx:
        def __init__(self):
            self._examined = 0
    rep = an.AnalyzeReport(mod="SEC", version=1, scope="all")
    out = an._evaluate(_Ctx(), boom, {"id": "C1.1", "check": "traces", "severity": "MAJOR"}, {}, rep)
    assert len(out) == 1 and "could not be evaluated" in out[0].message
    assert rep.coverage == {}


def test_a_reloaded_verdict_still_knows_what_it_did_not_examine(tmp_path):
    """A cache hit is exactly where a silent pass would hide best: the run that
    found nothing is not re-run, so if the reload drops the signal it is gone for
    every consumer after the first."""
    import json as _json
    p = tmp_path / "analyze-all.json"
    p.write_text(_json.dumps({
        "module": "SEC", "version": 1, "scope": "all", "contracts": ["C9"],
        "skipped": [], "findings": [], "provenance": {},
        "coverage": {"C9.6": 0, "C9.7": 10}, "vacuous": ["C9.6"],
    }), encoding="utf-8")
    rep = an.load_report(p)
    assert rep.coverage == {"C9.6": 0, "C9.7": 10}
    assert rep.vacuous() == ["C9.6"], "the signal must survive the cache, not just the first run"
