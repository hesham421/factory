"""drive_layout.py — the 'no loose files' law, multi-version addressing, move/rename plan."""
import json, subprocess, sys
from pathlib import Path

import config

TOOL = Path(__file__).parent.parent / "drive_layout.py"


def run(*a):
    return subprocess.run([sys.executable, str(TOOL), *a], capture_output=True, text=True)


def test_tree_has_folders_only_and_versions_nest(tmp_path):
    t1 = run("--tree", "--ctx", "[CTX]", "-m", "ORG", "-v", "1").stdout.split()
    t2 = run("--tree", "--ctx", "[CTX]", "-m", "ORG", "-v", "2").stdout.split()
    assert "[CTX]/ORG/P1-SRS" in t1 and "[CTX]/ORG/v2/P1-SRS" in t2
    # cross-version + platform folders are the same for both versions
    assert "[CTX]/ORG/_journey" in t1 and "[CTX]/ORG/_journey" in t2
    assert "[CTX]/_platform" in t1
    # every file-bearing location is a folder; no file paths in the tree
    assert not any(p.endswith(".md") or p.endswith(".json") for p in t1)


def test_audit_flags_loose_legacy_and_misplaced_and_passes_when_clean(tmp_path):
    listing = {
        "folders": ["_platform", "ORG/_journey", "ORG/P1-SRS", "ORG/P2-DB"],
        "files": [
            {"id": "a", "name": "srs-org.md",        "path": "ORG/P1-SRS"},   # ok
            {"id": "b", "name": "db-script.md",      "path": "ORG/P2-DB"},    # legacy name
            {"id": "c", "name": "business-policies-org.md", "path": ""},     # LOOSE at CTX root
            {"id": "d", "name": "journey-org.json",  "path": "ORG"},          # loose at module root
            {"id": "e", "name": "notes.txt",         "path": "ORG"},          # unknown
            {"id": "f", "name": "frontend-execution-plan-org.md", "path": "ORG/P1-SRS"},  # wrong folder
        ]}
    p = tmp_path / "l.json"; p.write_text(json.dumps(listing), encoding="utf-8")
    r = run("--audit", str(p), "-m", "ORG", "-v", "1")
    assert r.returncode == 1
    plan = json.loads(r.stdout)
    assert set(plan["ok"]) == {"srs-org.md", "db-script-org.md"}   # b: renamed, but already in the right folder
    assert {x["drive_file_id"] for x in plan["rename"]} == {"b"}
    moves = {x["drive_file_id"]: x["to"] for x in plan["move"]}
    assert moves["c"] == "ORG/P0-Platform"
    assert moves["d"] == "ORG/_journey"
    assert moves["f"] == "ORG/P3.2-Frontend-Exec"
    assert plan["unknown"][0]["name"] == "notes.txt"
    assert "ORG/P3.2-Frontend-Exec" in plan["missing_folders"]

    # after applying the plan the layout is clean → exit 0
    clean = {"folders": [f.strip("/") for f in config.drive_expected_tree("", "ORG", 1)],
             "files": [{"id": "a", "name": "srs-org.md", "path": "ORG/P1-SRS"},
                       {"id": "b", "name": "db-script-org.md", "path": "ORG/P2-DB"},
                       {"id": "c", "name": "business-policies-org.md", "path": "ORG/P0-Platform"},
                       {"id": "d", "name": "journey-org.json", "path": "ORG/_journey"}]}
    p.write_text(json.dumps(clean), encoding="utf-8")
    r = run("--audit", str(p), "-m", "ORG", "-v", "1")
    assert r.returncode == 0, r.stdout


def test_v2_files_must_sit_under_v2(tmp_path):
    listing = {"folders": [f.strip("/") for f in config.drive_expected_tree("", "ORG", 2)],
               "files": [{"id": "x", "name": "srs-org.md", "path": "ORG/P1-SRS"}]}  # v1 folder, but auditing v2
    p = tmp_path / "l.json"; p.write_text(json.dumps(listing), encoding="utf-8")
    plan = json.loads(run("--audit", str(p), "-m", "ORG", "-v", "2").stdout)
    assert plan["move"][0]["to"] == "ORG/v2/P1-SRS"


def test_no_literal_names_in_drive_layout_tool():
    body = "\n".join(l for l in TOOL.read_text(encoding="utf-8").splitlines()
                     if not l.lstrip().startswith("#") and '"""' not in l)
    for lit in ('"P1-SRS"', '"srs-', '"_journey"', '"_platform"', '"platform-summary'):
        assert lit not in body


def test_governance_config_1E_and_engine_paths_match_config(monkeypatch):
    """Prose is RENDERED from config: every canonical folder in DRIVE_LAYOUT
    must appear in GOVERNANCE-CONFIG §1E and in each engine's PATHS block,
    and no engine may claim a WRITES-TO folder it does not own."""
    import os
    proj = Path(os.environ.get("V5_PROJECTS", "/tmp/v5/projects"))
    if not proj.exists():
        import pytest; pytest.skip("rendered project files not present")
    cfg = (proj / "GOVERNANCE-CONFIG.md").read_text(encoding="utf-8")
    sec = cfg[cfg.index("## 1E."):]
    for _k, (folder, _w, _r) in config.all_drive_stages().items():
        assert folder in sec, f"§1E missing folder {folder}"
    assert config.DRIVE_JOURNEY_FOLDER in sec and config.DRIVE_PLATFORM_FOLDER in sec
    owners = {w: f for _k, (f, w, _r) in config.all_drive_stages().items()}
    engine_files = {"P1": "PROJECT-1-SRS-GOVERNANCE-ENGINE.md", "P2": "PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md",
                    "P3.1": "PROJECT-3-BACKEND-ENGINE.md", "P3.2": "PROJECT-3-FRONTEND-ENGINE.md"}
    for eng, fn in engine_files.items():
        body = (proj / fn).read_text(encoding="utf-8")
        blk = body[body.index("WRITES TO"):body.index("READS FROM")]
        assert f"/{owners[eng]}/" in blk, f"{eng} must write to {owners[eng]}"
        for other_eng, other_folder in owners.items():
            if other_eng != eng and other_folder != owners[eng]:
                assert f"/{other_folder}/" not in blk, f"{eng} claims {other_folder} which belongs to {other_eng}"


def test_reference_folders_governed_per_version_and_audited(tmp_path):
    """UI Shell + API Docs are governed reference files under _ref/, per version,
    and drive_layout audits a misplaced/loose reference like any artifact."""
    assert config.drive_folder_for_file("ui-shell-manifest-org.md", "ORG") == "_ref/ui-shell"
    assert config.drive_folder_for_file("api-docs-org.md", "ORG") == "_ref/api-docs"
    # v2 references live under /v2/_ref, leaving v1 frozen
    t2 = config.reference_targets("ORG", 2, "[CTX]")
    assert t2["REF_SHELL"][0] == "[CTX]/ORG/v2/_ref/ui-shell"
    assert "[CTX]/ORG/_ref/api-docs" in config.drive_expected_tree("[CTX]", "ORG", 1)

    listing = {"folders": [f.strip("/") for f in config.drive_expected_tree("", "ORG", 1)],
               "files": [{"id": "s", "name": "ui-shell-manifest-org.md", "path": "ORG"},          # loose → _ref
                         {"id": "a", "name": "api-docs-org.md", "path": "ORG/_ref/api-docs"}]}     # correct
    p = tmp_path / "l.json"; p.write_text(json.dumps(listing), encoding="utf-8")
    plan = json.loads(run("--audit", str(p), "-m", "ORG", "-v", "1").stdout)
    assert {x["drive_file_id"]: x["to"] for x in plan["move"]}["s"] == "ORG/_ref/ui-shell"
    assert "api-docs-org.md" in plan["ok"]
