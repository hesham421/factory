"""
Pytest suite for the FRONTEND governance splitting toolset.
Run: pytest -q   (from governance-tools/)

Covers the AMEND-FE-01 maturity pass:
  - frontend-only marker vocabulary (PHASE/SUB/TC; no API/XM)
  - single-source ALLOWED_PARENTS (config == marker_parser)
  - foreign-marker rejection (backend API/XM/MARK leak → structural error)
  - self-describing package files + Stage 5 round-trip integrity
  - --fix-safe unqualified SUB repair (reversible)
  - --strict-thresholds advisory/blocking
  - global SUB-id uniqueness (AMEND-P3-N)
"""

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent.parent
sys.path.insert(0, str(HERE))

import config
import marker_parser as mp
import agent3_splitter as a3


# ── fixtures ────────────────────────────────────────────────────────────────

def write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


EXEC_OK = """# Frontend Execution Plan — ORG

<!-- PHASE:F1:START -->
## F1 — Model Confirmation
Phase strategy table.
<!-- SUB:F1-SCR-ORG-001:START -->
### F1 — SCR-ORG-001
Model confirmation content. API-ORG-001 referenced as text only.
<!-- SUB:F1-SCR-ORG-001:END -->
<!-- SUB:F1-SCR-ORG-002:START -->
### F1 — SCR-ORG-002
Second screen.
<!-- SUB:F1-SCR-ORG-002:END -->
<!-- PHASE:F1:END -->

<!-- PHASE:SEC-FE:START -->
## SEC-FE — Security
Single block, never splits.
<!-- PHASE:SEC-FE:END -->
"""

TEST_OK = """# Frontend Test Plan — ORG

<!-- PHASE:TEST-PLAN-FE:START -->
Mandatory scenarios preamble.
<!-- SUB:UI-FLOWS:START -->
<!-- TC:TC-FE-ORG-001:START -->
Happy path flow.
<!-- TC:TC-FE-ORG-001:END -->
<!-- SUB:UI-FLOWS:END -->
<!-- SUB:INT-FLOW:START -->
<!-- TC:TC-FE-ORG-002:START -->
Integration flow.
<!-- TC:TC-FE-ORG-002:END -->
<!-- SUB:INT-FLOW:END -->
<!-- PHASE:TEST-PLAN-FE:END -->
"""


# ── vocabulary / dedup ──────────────────────────────────────────────────────

def test_marker_vocabulary_is_frontend_only():
    assert set(config.MARKERS.keys()) == {"phase", "sub", "tc"}
    assert "api" not in config.MARKERS and "xm" not in config.MARKERS

def test_allowed_parents_single_source():
    # marker_parser must not keep its own copy — it imports config's.
    assert mp.ALLOWED_PARENTS is config.ALLOWED_PARENTS
    assert config.ALLOWED_PARENTS["tc"] == ["phase", "sub"]

def test_phase_folder_map_derived_from_config():
    assert a3.EXEC_PHASES == set(config.PACKAGES_STRUCTURE["frontend-execution"])


# ── parsing ─────────────────────────────────────────────────────────────────

def test_clean_exec_parses_without_error(tmp_path):
    r = mp.parse_file(write(tmp_path, "e.md", EXEC_OK))
    assert r.errors == []
    assert [p.marker_id for p in mp.find_by_kind(r.root_blocks, "phase")] == ["F1", "SEC-FE"]
    assert [s.marker_id for s in mp.find_by_kind(r.root_blocks, "sub")] == \
        ["F1-SCR-ORG-001", "F1-SCR-ORG-002"]

def test_clean_test_parses_with_tcs(tmp_path):
    r = mp.parse_file(write(tmp_path, "t.md", TEST_OK))
    assert r.errors == []
    assert len(mp.find_by_kind(r.root_blocks, "tc")) == 2


# ── foreign-marker rejection (separation guard) ─────────────────────────────

@pytest.mark.parametrize("foreign", [
    "<!-- API:API-ORG-001:START -->\nx\n<!-- API:API-ORG-001:END -->",
    "<!-- XM:XM-ORG-001:START -->\nx\n<!-- XM:XM-ORG-001:END -->",
    "<!-- MARK:JUNIT:START -->\nx\n<!-- MARK:JUNIT:END -->",
])
def test_foreign_markers_rejected(tmp_path, foreign):
    doc = f"<!-- PHASE:F1:START -->\n{foreign}\n<!-- PHASE:F1:END -->\n"
    r = mp.parse_file(write(tmp_path, "f.md", doc))
    assert any("Unrecognized marker kind" in e.message for e in r.errors)

def test_source_header_comment_not_flagged(tmp_path):
    # The 'Source:'/'Context:' header comments Stage 2 writes must NOT trip
    # the foreign-marker guard (they don't end in :START/:END).
    doc = ("<!-- Source: PHASE:F1 / SUB:F1-SCR-ORG-001 -->\n"
           "<!-- PHASE:F1:START -->\n<!-- SUB:F1-SCR-ORG-001:START -->\nx\n"
           "<!-- SUB:F1-SCR-ORG-001:END -->\n<!-- PHASE:F1:END -->\n")
    r = mp.parse_file(write(tmp_path, "s.md", doc))
    assert r.errors == []


# ── global uniqueness (AMEND-P3-N) ──────────────────────────────────────────

def test_unqualified_sub_repeated_across_phases_is_duplicate(tmp_path):
    doc = ("<!-- PHASE:F1:START -->\n<!-- SUB:SCR-ORG-001:START -->\na\n"
           "<!-- SUB:SCR-ORG-001:END -->\n<!-- PHASE:F1:END -->\n"
           "<!-- PHASE:F2:START -->\n<!-- SUB:SCR-ORG-001:START -->\nb\n"
           "<!-- SUB:SCR-ORG-001:END -->\n<!-- PHASE:F2:END -->\n")
    r = mp.parse_file(write(tmp_path, "d.md", doc))
    assert any("Duplicate SUB:SCR-ORG-001" in e.message for e in r.errors)


# ── self-describing package files + Stage 5 round trip ──────────────────────

def _split_and_verify(tmp_path, exec_text, test_text):
    """Run stages 2/3 then stage5 against an isolated module base."""
    base = tmp_path / "MOD"
    (base / "P3_2").mkdir(parents=True)
    (base / "P3_5_FE").mkdir(parents=True)
    (config.plan_file(base, "MOD", "exec")).write_text(exec_text, encoding="utf-8")
    (config.plan_file(base, "MOD", "test")).write_text(test_text, encoding="utf-8")

    # Stage 2/3 write plans directly (bypass interactive confirm()).
    state = {"stages_completed": [], "stages": {}}
    import builtins
    orig_input = builtins.input
    builtins.input = lambda *a, **k: "y"
    try:
        assert a3.stage2_split_execution("MOD", state, None, base=base) is True
        assert a3.stage3_split_test("MOD", state, None, base=base) is True
        ok = a3.stage5_verify("MOD", state, base=base)
    finally:
        builtins.input = orig_input
    return ok, base

def test_stage5_round_trip_passes(tmp_path):
    ok, base = _split_and_verify(tmp_path, EXEC_OK, TEST_OK)
    assert ok is True
    # Package files are self-describing: SUB marker present in its file.
    scr = base / "packages" / "frontend-execution" / "F1" / "F1-SCR-ORG-001.md"
    assert "<!-- SUB:F1-SCR-ORG-001:START -->" in scr.read_text(encoding="utf-8")
    # No-SUB phase written whole.
    sec = base / "packages" / "frontend-execution" / "SEC-FE" / "SEC-FE.md"
    assert "<!-- PHASE:SEC-FE:START -->" in sec.read_text(encoding="utf-8")

def test_stage5_detects_tampering(tmp_path):
    ok, base = _split_and_verify(tmp_path, EXEC_OK, TEST_OK)
    assert ok is True
    tc = base / "packages" / "frontend-test" / "UI-FLOWS.md"
    txt = tc.read_text(encoding="utf-8").replace("Happy path flow.", "TAMPERED CONTENT.")
    tc.write_text(txt, encoding="utf-8")
    state = {"stages_completed": [], "stages": {}}
    assert a3.stage5_verify("MOD", state, base=base) is False


# ── --fix-safe ──────────────────────────────────────────────────────────────

def test_fix_safe_plans_unqualified_sub(tmp_path):
    doc = ("<!-- PHASE:F1:START -->\n<!-- SUB:SCR-ORG-001:START -->\na\n"
           "<!-- SUB:SCR-ORG-001:END -->\n<!-- PHASE:F1:END -->\n")
    r = mp.parse_file(write(tmp_path, "u.md", doc))
    fixes = a3._plan_sub_qualification_fixes(r)
    assert len(fixes) == 1
    assert fixes[0]["new_label"] == "F1-SCR-ORG-001"

def test_fix_safe_skips_already_qualified(tmp_path):
    r = mp.parse_file(write(tmp_path, "q.md", EXEC_OK))
    assert a3._plan_sub_qualification_fixes(r) == []

def test_fix_safe_applies_and_revalidates(tmp_path):
    base = tmp_path / "MOD"
    (base / "P3_2").mkdir(parents=True)
    bad = ("<!-- PHASE:F1:START -->\n<!-- SUB:SCR-ORG-001:START -->\na\n"
           "<!-- SUB:SCR-ORG-001:END -->\n<!-- PHASE:F1:END -->\n"
           "<!-- PHASE:F2:START -->\n<!-- SUB:SCR-ORG-001:START -->\nb\n"
           "<!-- SUB:SCR-ORG-001:END -->\n<!-- PHASE:F2:END -->\n")
    (config.plan_file(base, "MOD", "exec")).write_text(bad, encoding="utf-8")
    import builtins
    orig_input = builtins.input
    builtins.input = lambda *a, **k: "y"
    try:
        ok = a3.run_fix_safe("MOD", base=base, dry_run=False)
    finally:
        builtins.input = orig_input
    assert ok is True
    fixed = (config.plan_file(base, "MOD", "exec")).read_text(encoding="utf-8")
    assert "SUB:F1-SCR-ORG-001" in fixed and "SUB:F2-SCR-ORG-001" in fixed
    assert (config.plan_file(base, "MOD", "exec").with_name(config.plan_label("exec","MOD")+".orig")).exists()
    # Post-fix the document validates clean (duplicate resolved).
    assert mp.parse_file(config.plan_file(base, "MOD", "exec")).errors == []


# ── thresholds ──────────────────────────────────────────────────────────────

def test_threshold_advisory_when_many_tcs_no_sub(tmp_path):
    tcs = "".join(
        f"<!-- TC:TC-FE-ORG-{i:03d}:START -->\nx\n<!-- TC:TC-FE-ORG-{i:03d}:END -->\n"
        for i in range(1, 11))  # 10 TCs > threshold 8
    doc = f"<!-- PHASE:TEST-PLAN-FE:START -->\n{tcs}<!-- PHASE:TEST-PLAN-FE:END -->\n"
    r = mp.parse_file(write(tmp_path, "many.md", doc))
    assert r.errors == []
    adv = a3.check_thresholds(None, r)
    assert len(adv) == 1 and "TEST-PLAN-FE" in adv[0]

def test_no_threshold_advisory_when_below(tmp_path):
    r = mp.parse_file(write(tmp_path, "few.md", TEST_OK))  # 2 TCs
    assert a3.check_thresholds(None, r) == []
