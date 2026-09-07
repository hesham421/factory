"""Tests for agent3_splitter.safe_autofix_file — deterministic marker repairs."""
from pathlib import Path

import config

import agent3_splitter as a3
import marker_parser as mp


def _w(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_fixes_separator_typo_and_qualifies_sub(tmp_path):
    body = (
        "<!-- PHASE:SVC_API:START -->\n"          # '_' separator typo → SVC-API
        "  <!-- SUB:CRUD:START -->\n"             # bare label → SVC-API-CRUD
        "    <!-- API:API-ORG-001:START -->\n    x\n    <!-- API:API-ORG-001:END -->\n"
        "  <!-- SUB:CRUD:END -->\n"
        "<!-- PHASE:SVC_API:END -->\n"
    )
    p = _w(tmp_path, config.plan_label("exec","tst"), body)
    rep = a3.safe_autofix_file(p)
    assert rep["changed"] is True
    assert rep["remaining_blocking"] == []
    text = p.read_text(encoding="utf-8")
    assert "PHASE:SVC-API:START" in text and "PHASE:SVC-API:END" in text
    assert "SUB:SVC-API-CRUD:START" in text and "SUB:SVC-API-CRUD:END" in text
    assert "SVC_API" not in text
    # original preserved
    assert (tmp_path / (config.plan_label("exec","tst") + ".orig")).exists()
    # and it now passes semantic validation
    result = mp.parse_file(p)
    blocking, _adv = mp.validate_semantics(p, result)
    assert result.errors == [] and blocking == []


def test_test_plan_subs_are_left_bare(tmp_path):
    # test-plan SUBs are exempt from qualification — must NOT be rewritten.
    body = (
        "<!-- PHASE:TEST-PLAN-BE:START -->\n"
        "  <!-- SUB:RULE-SCENARIOS:START -->\n"
        "    <!-- TC:TC-BE-ORG-001:START -->\n    x\n    <!-- TC:TC-BE-ORG-001:END -->\n"
        "  <!-- SUB:RULE-SCENARIOS:END -->\n"
        "<!-- PHASE:TEST-PLAN-BE:END -->\n"
    )
    p = _w(tmp_path, config.plan_label("test","tst"), body)
    rep = a3.safe_autofix_file(p)
    assert rep["sub_qualification_fixes"] == []
    assert "SUB:RULE-SCENARIOS:START" in p.read_text(encoding="utf-8")


def test_unfixable_is_reported_not_touched(tmp_path):
    body = "<!-- PHASE:CORE:START -->\nx\n"  # unclosed — needs a human
    p = _w(tmp_path, config.plan_label("exec","tst"), body)
    rep = a3.safe_autofix_file(p)
    assert rep["changed"] is False
    assert any("Unclosed" in e for e in rep["remaining_blocking"])
    assert not (tmp_path / (config.plan_label("exec","tst") + ".orig")).exists()


def test_already_valid_file_is_noop(tmp_path):
    import fixtures
    p = _w(tmp_path, config.plan_label("exec","tst"), fixtures.valid_execution_plan())
    rep = a3.safe_autofix_file(p)
    assert rep["changed"] is False
    assert rep["phase_key_fixes"] == [] and rep["sub_qualification_fixes"] == []
    assert rep["remaining_blocking"] == []
    assert not (tmp_path / (config.plan_label("exec","tst") + ".orig")).exists()


def test_ambiguous_key_left_for_human(tmp_path):
    # DATADOM (hyphen missing entirely) cannot be unambiguously restored → left.
    body = "<!-- PHASE:DATADOM:START -->\nx\n<!-- PHASE:DATADOM:END -->\n"
    p = _w(tmp_path, config.plan_label("exec","tst"), body)
    rep = a3.safe_autofix_file(p)
    assert rep["phase_key_fixes"] == []
    assert any("Non-canonical PHASE key 'DATADOM'" in e for e in rep["remaining_blocking"])
