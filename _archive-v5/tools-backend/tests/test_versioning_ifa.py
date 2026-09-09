"""
IFA / new-version scenario coverage (previously ZERO tests touched versioning).

Locks in the end-to-end contract that makes "add a feature to an already-
implemented module" work as a delta, v1 frozen:

  agent1 --new-version  → creates modules/[MOD]/v2/ + sets current_version=2
  agent2                → archives into v2 (reads current_version, never
                          blindly v1) — THIS was the broken link before the
                          config.py + agent2 version-awareness fix
  config path helpers   → get_stage_path / get_packages_path / get_module_path
                          all resolve to the current version, so nothing lands
                          in v1 once v2 is current
  v1                    → remains byte-identical (frozen) throughout
"""
import sys
from pathlib import Path

import pytest

import config
import agent1_create_structure as a1


def _run_a1(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    a1.main()


# ── config path helpers are version-aware (root cause of the agent2 break) ──

def test_path_helpers_follow_current_version(isolated_registry, monkeypatch):
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--auto-register",
                          "--description", "x"])
    # v1 is current → no suffix on any path helper
    assert config.get_module_path("ORG").name == "ORG"
    assert config.get_stage_path("ORG", "P3_1").parent.name == "ORG"
    assert config.get_packages_path("ORG", "backend-execution").parent.parent.name == "ORG"

    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--new-version"])
    # v2 is now current → every helper (no explicit version) must resolve to v2,
    # NOT to v1. This is exactly what let a delta land over v1 before the fix.
    assert config.get_module_path("ORG").name == "v2"
    assert config.get_stage_path("ORG", "P3_1").parent.name == "v2"
    assert config.get_packages_path("ORG", "backend-execution").parent.parent.name == "v2"

    # Explicit version=1 still addresses the frozen v1 tree.
    assert config.get_module_path("ORG", 1).name == "ORG"
    assert config.get_stage_path("ORG", "P3_1", 1).parent.name == "ORG"


def test_module_path_casing_consistent_across_versions(isolated_registry, monkeypatch):
    # get_module_path used to .upper() while get_module_version_path didn't —
    # a v1/v2 casing mismatch. Lower-case input must resolve identically now.
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--auto-register",
                          "--description", "x"])
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--new-version"])
    assert config.get_module_path("org") == config.get_module_path("ORG")
    assert config.get_stage_path("org", "P3_1") == config.get_stage_path("ORG", "P3_1")


# ── the registry bookkeeping agent1 --new-version performs ──────────────────

def test_new_version_registers_and_freezes_v1(isolated_registry, monkeypatch):
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--auto-register",
                          "--description", "x"])
    v1_root = config.get_module_path("ORG", 1)
    assert v1_root.exists() and v1_root.name == "ORG"

    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--new-version"])
    reg = config.load_modules_registry()["modules"]["ORG"]
    assert reg["current_version"] == 2
    assert sorted(reg["versions"]) == [1, 2]

    v2_root = config.get_module_path("ORG")
    assert v2_root.name == "v2" and v2_root.exists()
    # v1 tree still present and distinct from v2 — v2 is created ALONGSIDE, not over.
    assert v1_root.exists()
    assert v1_root != v2_root


# ── the core end-to-end: agent2 archives the delta into v2, v1 frozen ───────

def test_agent2_archives_delta_into_v2_leaving_v1_frozen(isolated_registry, monkeypatch):
    import agent2_archive as a2

    # 1) v1 built + a v1 artifact archived.
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--auto-register",
                          "--description", "x"])
    src = isolated_registry["repo"].parent / "src_v1"
    src.mkdir()
    (src / config.resolve_filename("srs-{mod}.md","ORG")).write_text("V1 SRS — original", encoding="utf-8")
    monkeypatch.setattr(sys, "argv",
                        ["agent2", "--module", "ORG", "--source", str(src)])
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    a2.main()

    v1_srs = config.get_stage_path("ORG", "P1", 1) / config.resolve_filename("srs-{mod}.md","ORG")
    assert v1_srs.exists(), "v1 archive should have landed under modules/ORG/"
    v1_bytes = v1_srs.read_bytes()

    # 2) new version, then archive a DELTA artifact.
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--new-version"])
    src2 = isolated_registry["repo"].parent / "src_v2"
    src2.mkdir()
    (src2 / config.resolve_filename("srs-{mod}.md","ORG")).write_text("V2 SRS — delta feature added", encoding="utf-8")
    monkeypatch.setattr(sys, "argv",
                        ["agent2", "--module", "ORG", "--source", str(src2)])
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    a2.main()

    # The delta must land in v2 …
    v2_srs = config.get_stage_path("ORG", "P1", 2) / config.resolve_filename("srs-{mod}.md","ORG")
    assert v2_srs.exists(), "delta archive must land under modules/ORG/v2/"
    assert "delta feature" in v2_srs.read_text(encoding="utf-8")

    # … and v1 must be byte-identical (frozen), never overwritten by the delta.
    assert v1_srs.read_bytes() == v1_bytes, "v1 artifact must remain frozen"
    assert v1_srs.read_text(encoding="utf-8").startswith("V1 SRS")
    assert v2_srs.resolve() != v1_srs.resolve()


# ── AMEND-PIPELINE-V5 §5: module-qualified names must NOT bypass semantics ──

def test_module_qualified_plan_is_classified_and_semantically_checked(tmp_path):
    """Regression guard for the silent bypass found in the V5 rename: the old
    classify_artifact matched a LITERAL filename, so a module-qualified plan
    classified as '' and every semantic check (canonical keys, SUB
    qualification) was skipped without any error. This pins that:
      (a) a qualified name classifies to its plan key,
      (b) a non-canonical PHASE key in it IS blocked."""
    import marker_parser as mp
    assert config.classify_artifact("backend-execution-plan-org.md") == "exec"
    assert config.classify_artifact("backend-test-plan-org.md") == "test"
    # the old un-qualified name is deliberately no longer a valid artifact
    assert config.classify_artifact("backend-execution-plan.md") == ""

    p = tmp_path / config.plan_label("exec", "org")
    p.write_text("<!-- PHASE:DATADOM:START -->\nx\n<!-- PHASE:DATADOM:END -->\n", encoding="utf-8")
    result = mp.parse_file(p)
    blocking, _adv = mp.validate_semantics(p, result)
    assert any("DATADOM" in e.message or "canonical" in e.message.lower() for e in blocking), \
        "a non-canonical phase key in a module-qualified plan must be BLOCKED"


def test_no_literal_plan_filename_in_agent3_source():
    """agent3 must locate plans only through config.plan_file / plan_label."""
    src = (Path(__file__).parent.parent / "agent3_splitter.py").read_text(encoding="utf-8")
    code_lines = [l for l in src.splitlines()
                  if not l.lstrip().startswith("#") and '"""' not in l]
    body = "\n".join(code_lines)
    assert '"backend-execution-plan.md"' not in body
    assert '"backend-test-plan.md"' not in body
