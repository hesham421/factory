"""Structural + semantic validation tests for marker_parser."""
from pathlib import Path

import config

import marker_parser as mp
import fixtures


def _write(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


# ── structural ────────────────────────────────────────────────────────────

def test_valid_execution_plan_parses_clean(tmp_path):
    p = _write(tmp_path, config.plan_label("exec","tst"), fixtures.valid_execution_plan())
    result = mp.parse_file(p)
    assert result.errors == []
    phases = mp.find_by_kind(result.root_blocks, "phase")
    assert {b.marker_id for b in phases} == {"CORE", "SVC-API", "INT-C", "ALIGN-BE"}
    apis = mp.find_by_kind(result.root_blocks, "api")
    assert {a.marker_id for a in apis} == {"API-ORG-001", "API-ORG-002"}


def test_unclosed_marker_is_critical(tmp_path):
    body = "<!-- PHASE:CORE:START -->\ncontent\n"  # no END
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    assert any(e.severity == "CRITICAL" and "Unclosed" in e.message for e in result.errors)


def test_unmatched_end_is_critical(tmp_path):
    body = "content\n<!-- PHASE:CORE:END -->\n"  # END with no START
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    assert any("Unmatched END" in e.message for e in result.errors)


def test_illegal_nesting_is_critical(tmp_path):
    body = (
        "<!-- API:API-ORG-001:START -->\n"  # API at document root — illegal
        "x\n"
        "<!-- API:API-ORG-001:END -->\n"
    )
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    assert any("Illegal nesting" in e.message for e in result.errors)


def test_duplicate_id_is_critical(tmp_path):
    body = (
        "<!-- PHASE:CORE:START -->\n"
        "  <!-- SUB:CORE-A:START -->\n"
        "    <!-- API:API-ORG-001:START -->\n    a\n    <!-- API:API-ORG-001:END -->\n"
        "    <!-- API:API-ORG-001:START -->\n    b\n    <!-- API:API-ORG-001:END -->\n"
        "  <!-- SUB:CORE-A:END -->\n"
        "<!-- PHASE:CORE:END -->\n"
    )
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    assert any("Duplicate API:API-ORG-001" in e.message for e in result.errors)


# ── semantic: canonical phase keys ────────────────────────────────────────

def test_non_canonical_phase_key_rejected(tmp_path):
    body = (
        "<!-- PHASE:DATADOM:START -->\n"  # missing hyphen → valid id, not canonical
        "x\n"
        "<!-- PHASE:DATADOM:END -->\n"
    )
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    blocking, _adv = mp.validate_semantics(p, result)
    assert any("Non-canonical PHASE key 'DATADOM'" in e.message for e in blocking)


def test_canonical_phase_keys_pass(tmp_path):
    p = _write(tmp_path, config.plan_label("exec","tst"), fixtures.valid_execution_plan())
    result = mp.parse_file(p)
    blocking, advisories = mp.validate_semantics(p, result)
    assert blocking == [] and advisories == []


# ── semantic: SUB phase-qualification (AMEND-P3-N) ────────────────────────

def test_unqualified_sub_rejected_in_execution_plan(tmp_path):
    body = (
        "<!-- PHASE:SVC-API:START -->\n"
        "  <!-- SUB:CRUD:START -->\n"          # bare label — not phase-qualified
        "    <!-- API:API-ORG-001:START -->\n    a\n    <!-- API:API-ORG-001:END -->\n"
        "  <!-- SUB:CRUD:END -->\n"
        "<!-- PHASE:SVC-API:END -->\n"
    )
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    blocking, _adv = mp.validate_semantics(p, result)
    assert any("SUB 'CRUD'" in e.message and "phase-qualified" in e.message for e in blocking)


def test_bare_sub_allowed_in_test_plan(tmp_path):
    # test-plans are EXEMPT — RULE-SCENARIOS / API-SCENARIOS are bare by design.
    p = _write(tmp_path, config.plan_label("test","tst"), fixtures.valid_test_plan())
    result = mp.parse_file(p)
    assert result.errors == []
    blocking, _adv = mp.validate_semantics(p, result)
    assert blocking == []


# ── semantic: orphan atomics ──────────────────────────────────────────────

def test_orphan_atomic_rejected(tmp_path):
    body = (
        "<!-- PHASE:SVC-API:START -->\n"
        "  <!-- SUB:SVC-API-CRUD:START -->\n"
        "    <!-- API:API-ORG-001:START -->\n    a\n    <!-- API:API-ORG-001:END -->\n"
        "  <!-- SUB:SVC-API-CRUD:END -->\n"
        "  <!-- API:API-ORG-002:START -->\n  orphan\n  <!-- API:API-ORG-002:END -->\n"  # outside SUB
        "<!-- PHASE:SVC-API:END -->\n"
    )
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    blocking, _adv = mp.validate_semantics(p, result)
    assert any("Orphan API:API-ORG-002" in e.message for e in blocking)


def test_no_sub_phase_atomics_not_orphaned(tmp_path):
    # Below-threshold test plan: TCs directly under PHASE, no SUB → valid.
    p = _write(tmp_path, config.plan_label("test","tst"), fixtures.valid_test_plan_below_threshold())
    result = mp.parse_file(p)
    assert result.errors == []
    blocking, advisories = mp.validate_semantics(p, result)
    assert blocking == [] and advisories == []


def test_allowed_parents_single_source():
    # config is the single source of truth; parser must reference the same object.
    import config
    assert mp.ALLOWED_PARENTS is config.ALLOWED_PARENTS


# ── split thresholds (auto + flexible) ────────────────────────────────────

def test_over_threshold_no_sub_is_advisory_not_blocking(tmp_path):
    p = _write(tmp_path, config.plan_label("exec","tst"), fixtures.svc_api_over_threshold_no_sub())
    result = mp.parse_file(p)
    blocking, advisories = mp.validate_semantics(p, result)  # default: non-strict
    assert blocking == [], "an unsplit over-threshold phase must NOT block by default"
    assert any("over the split threshold" in e.message for e in advisories)
    assert all(e.severity == "MINOR" for e in advisories)


def test_over_threshold_blocks_under_strict(tmp_path):
    p = _write(tmp_path, config.plan_label("exec","tst"), fixtures.svc_api_over_threshold_no_sub())
    result = mp.parse_file(p)
    blocking, advisories = mp.validate_semantics(p, result, strict_thresholds=True)
    assert any(e.severity == "MAJOR" and "over the split threshold" in e.message for e in advisories)


def test_below_threshold_no_advisory(tmp_path):
    # 7 APIs, no SUB → below the ≥8 trigger → no advisory.
    apis = "".join(
        f"  <!-- API:API-ORG-{i:03d}:START -->\n  x\n  <!-- API:API-ORG-{i:03d}:END -->\n"
        for i in range(1, 8)
    )
    body = "<!-- PHASE:SVC-API:START -->\n" + apis + "<!-- PHASE:SVC-API:END -->\n"
    p = _write(tmp_path, config.plan_label("exec","tst"), body)
    result = mp.parse_file(p)
    _blocking, advisories = mp.validate_semantics(p, result)
    assert advisories == []


def test_test_plan_boundary_is_strict_greater_than(tmp_path):
    # TEST-PLAN-BE trigger is TCs > 12; exactly 12 must NOT advise.
    tcs = "".join(
        f"  <!-- TC:TC-BE-ORG-{i:03d}:START -->\n  x\n  <!-- TC:TC-BE-ORG-{i:03d}:END -->\n"
        for i in range(1, 13)  # 12 TCs
    )
    body = "<!-- PHASE:TEST-PLAN-BE:START -->\n" + tcs + "<!-- PHASE:TEST-PLAN-BE:END -->\n"
    p = _write(tmp_path, config.plan_label("test","tst"), body)
    result = mp.parse_file(p)
    _blocking, advisories = mp.validate_semantics(p, result)
    assert advisories == [], "12 TCs is not > 12 — no advisory"


def test_never_split_phase_with_sub_is_advisory(tmp_path):
    p = _write(tmp_path, config.plan_label("exec","tst"), fixtures.core_with_sub())
    result = mp.parse_file(p)
    blocking, advisories = mp.validate_semantics(p, result)
    assert blocking == []
    assert any("never-split phase" in e.message for e in advisories)
