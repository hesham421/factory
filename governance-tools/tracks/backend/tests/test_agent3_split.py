"""Integration tests for agent3_splitter — run the real stage functions
against a tmp module base, with prompts auto-approved."""
from pathlib import Path

import pytest
import config

import agent3_splitter as a3
import fixtures


@pytest.fixture
def module_base(tmp_path, monkeypatch):
    """Build modules/TST/{P3_1,P3_5_BE}/ with valid artifacts and auto-approve
    every Agent 3 confirmation prompt."""
    base = tmp_path / "modules" / "TST"
    (base / "P3_1").mkdir(parents=True)
    (base / "P3_5_BE").mkdir(parents=True)
    (config.plan_file(base, "TST", "exec")).write_text(
        fixtures.valid_execution_plan(), encoding="utf-8")
    (config.plan_file(base, "TST", "test")).write_text(
        fixtures.valid_test_plan(), encoding="utf-8")
    monkeypatch.setattr(a3, "confirm", lambda *a, **k: True)
    return base


def _run_all(base):
    state = {"stages_completed": [], "stages": {}}
    plan = a3.stage1_parse_and_plan("TST", 1, state, base)
    assert plan is not None, "Stage 1 should approve a clean plan"
    assert a3.stage2_split_execution("TST", 1, state, plan, base) is True
    assert a3.stage3_split_test("TST", 1, state, plan, base) is True
    assert a3.stage4_generate_index("TST", 1, state, base) is True
    assert a3.stage5_verify("TST", 1, state, base) is True
    return state


def test_full_split_pipeline(module_base):
    state = _run_all(module_base)
    assert state["stages_completed"] == [1, 2, 3, 4, 5]


def test_sub_filenames_not_double_prefixed(module_base):
    _run_all(module_base)
    svc = module_base / "packages" / "backend-execution" / "SVC-API"
    names = {f.name for f in svc.glob("*.md")}
    # C1: filename is the (already phase-qualified) SUB label — NOT re-prefixed.
    assert "SVC-API-CRUD.md" in names
    assert "SVC-API-SEARCH.md" in names
    assert "SVC-API-SVC-API-CRUD.md" not in names  # the old double-prefix bug


def test_unmarked_trailing_section_captured(module_base):
    _run_all(module_base)
    sections = module_base / "packages" / "backend-execution" / "_SECTIONS.md"
    assert sections.exists(), "trailing un-marked content must be captured (C4)"
    assert "Agent Handoff Summary" in sections.read_text(encoding="utf-8")


def test_test_plan_files_flat_in_container(module_base):
    _run_all(module_base)
    bt = module_base / "packages" / "backend-test"
    names = {f.name for f in bt.glob("*.md")}
    # FINDING-19: flat files directly in the container, no per-label subfolders.
    assert "RULE-SCENARIOS.md" in names
    assert "API-SCENARIOS.md" in names
    assert not (bt / "RULE-SCENARIOS").is_dir()


def test_stage1_blocks_on_non_canonical_key(tmp_path, monkeypatch):
    base = tmp_path / "modules" / "BAD"
    (base / "P3_1").mkdir(parents=True)
    (config.plan_file(base, "BAD", "exec")).write_text(
        "<!-- PHASE:DATADOM:START -->\nx\n<!-- PHASE:DATADOM:END -->\n", encoding="utf-8")
    monkeypatch.setattr(a3, "confirm", lambda *a, **k: True)
    state = {"stages_completed": [], "stages": {}}
    plan = a3.stage1_parse_and_plan("BAD", 1, state, base)
    assert plan is None, "Stage 1 must block a non-canonical phase key"


def _write_over_threshold(tmp_path):
    base = tmp_path / "modules" / "THR"
    (base / "P3_1").mkdir(parents=True)
    (config.plan_file(base, "THR", "exec")).write_text(
        fixtures.svc_api_over_threshold_no_sub(), encoding="utf-8")
    return base


def test_stage1_over_threshold_is_non_blocking_by_default(tmp_path, monkeypatch):
    base = _write_over_threshold(tmp_path)
    monkeypatch.setattr(a3, "confirm", lambda *a, **k: True)
    state = {"stages_completed": [], "stages": {}}
    plan = a3.stage1_parse_and_plan("THR", 1, state, base)  # non-strict
    assert plan is not None, "an over-threshold-but-unsplit phase must not block by default"


def test_stage1_over_threshold_blocks_when_strict(tmp_path, monkeypatch):
    base = _write_over_threshold(tmp_path)
    monkeypatch.setattr(a3, "confirm", lambda *a, **k: True)
    state = {"stages_completed": [], "stages": {}}
    plan = a3.stage1_parse_and_plan("THR", 1, state, base, strict_thresholds=True)
    assert plan is None, "--strict-thresholds must block the same case"
