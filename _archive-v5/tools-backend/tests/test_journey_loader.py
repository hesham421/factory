"""journey_loader.py — START/append/END, latest-wins, plan, verify."""
import json, subprocess, sys
from pathlib import Path

import config

HERE = Path(__file__).parent.parent
LOADER = HERE / "journey_loader.py"


def run(*args):
    return subprocess.run([sys.executable, str(LOADER), *args],
                          capture_output=True, text=True)


def _row(fname, fid, engine="P1"):
    return json.dumps({"engine": engine, "stage": "P1", "filename": fname,
                       "artifact": "srs", "drive_file_id": fid,
                       "drive_url": f"https://drive/{fid}"})


def test_full_journey_start_append_end_plan_verify(tmp_path):
    ledger = tmp_path / config.ledger_filename("ORG")
    srs = config.resolve_filename("srs-{mod}.md", "ORG")

    assert run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--open", "--engine", "P1").returncode == 0
    assert run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--append", _row(srs, "id-A")).returncode == 0
    # re-upload → the earlier row is SUPERSEDED, plan must carry only the latest id
    assert run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--append", _row(srs, "id-B")).returncode == 0
    assert run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--close").returncode == 0

    data = json.loads(ledger.read_text(encoding="utf-8"))
    sec = data["versions"]["1"]
    assert sec["status"] == "CLOSED" and sec["started_by_engine"] == "P1"
    assert [r["status"] for r in sec["artifacts"]] == ["SUPERSEDED", "UPLOADED"]

    dest = tmp_path / "drop"; dest.mkdir()
    p = run("--ledger", str(ledger), "-m", "ORG", "-v", "latest", "-d", str(dest), "--plan")
    assert p.returncode == 0
    plan = json.loads(p.stdout)
    assert plan["version"] == 1 and plan["count"] == 1
    assert plan["files"][0]["drive_file_id"] == "id-B"
    assert plan["files"][0]["dest"].endswith(srs)

    # verify fails before the connector downloads, passes after
    v = run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "-d", str(dest), "--verify")
    assert v.returncode == 1 and srs in v.stdout
    (dest / srs).write_text("x", encoding="utf-8")
    v = run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "-d", str(dest), "--verify")
    assert v.returncode == 0


def test_versions_are_isolated_in_one_file(tmp_path):
    ledger = tmp_path / config.ledger_filename("ORG")
    srs = config.resolve_filename("srs-{mod}.md", "ORG")
    run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--open")
    run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--append", _row(srs, "v1-id"))
    run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--close")
    # IFA: v2 opens with a change set; v1 stays frozen in the same file
    run("--ledger", str(ledger), "-m", "ORG", "-v", "2", "--open", "--change-set", "CS-ORG-001")
    run("--ledger", str(ledger), "-m", "ORG", "-v", "2", "--append", _row(srs, "v2-id"))
    data = json.loads(ledger.read_text(encoding="utf-8"))
    assert set(data["versions"]) == {"1", "2"}
    assert data["versions"]["2"]["change_set"] == "CS-ORG-001"
    p1 = json.loads(run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--plan").stdout)
    p2 = json.loads(run("--ledger", str(ledger), "-m", "ORG", "-v", "2", "--plan").stdout)
    assert p1["files"][0]["drive_file_id"] == "v1-id"
    assert p2["files"][0]["drive_file_id"] == "v2-id"


def test_invalid_row_rejected(tmp_path):
    ledger = tmp_path / config.ledger_filename("ORG")
    run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--open")
    bad = json.dumps({"filename": "srs-org.md"})     # missing required keys
    r = run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--append", bad)
    assert r.returncode != 0 and "invalid row" in (r.stdout + r.stderr)


def test_stage5_receipt_flows_into_ledger(tmp_path, monkeypatch):
    """Gap-2 closure: a verified split writes a receipt of every package file
    (repo_path rows), and --append-receipts lands them in the module ledger,
    so package links are recorded automatically — no hand bookkeeping."""
    import agent3_splitter as a3
    import fixtures
    base = tmp_path / "modules" / "TST"
    (base / "P3_1").mkdir(parents=True); (base / "P3_5_BE").mkdir(parents=True)
    config.plan_file(base, "TST", "exec").write_text(fixtures.valid_execution_plan(), encoding="utf-8")
    config.plan_file(base, "TST", "test").write_text(fixtures.valid_test_plan(), encoding="utf-8")
    monkeypatch.setattr(a3, "confirm", lambda *a, **k: True)
    state = {"stages_completed": [], "stages": {}}
    plan = a3.stage1_parse_and_plan("TST", 1, state, base)
    assert plan is not None
    assert a3.stage2_split_execution("TST", 1, state, plan, base)
    assert a3.stage3_split_test("TST", 1, state, plan, base)
    assert a3.stage4_generate_index("TST", 1, state, base)
    assert a3.stage5_verify("TST", 1, state, base)

    receipt = base / "receipts" / config.receipt_filename("TST", 1)
    assert receipt.exists()
    rows = json.loads(receipt.read_text(encoding="utf-8"))["rows"]
    assert rows and all(r.get("repo_path") and not r.get("drive_file_id") for r in rows)

    ledger = tmp_path / config.ledger_filename("TST")
    run("--ledger", str(ledger), "-m", "TST", "-v", "1", "--open")
    r = run("--ledger", str(ledger), "-m", "TST", "-v", "1", "--append-receipts", str(receipt))
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(ledger.read_text(encoding="utf-8"))
    assert len(data["versions"]["1"]["artifacts"]) == len(rows)
    # plan marks repo rows as needing no connector transfer
    p = json.loads(run("--ledger", str(ledger), "-m", "TST", "-v", "1", "--plan").stdout)
    assert all(f["transfer"] == "already-in-repo" for f in p["files"])


def test_backfill_builds_ledger_and_rename_plan_for_legacy_module(tmp_path):
    """Drive migration: a pre-V5 module (un-qualified names, no ledger) gets a
    CLOSED v1 ledger built from a connector listing, plus the exact renames the
    connector must apply — derived from ARTIFACT_FILES, nothing hand-listed."""
    listing = tmp_path / "listing.json"
    listing.write_text(json.dumps({"files": [
        {"id": "f1", "name": "srs.md", "webViewLink": "https://d/f1", "stage": "P1"},
        {"id": "f2", "name": "db-script.md", "webViewLink": "https://d/f2", "stage": "P2"},
        {"id": "f3", "name": "registry-srs-org.md", "webViewLink": "https://d/f3", "stage": "P1"},
    ]}), encoding="utf-8")
    ledger = tmp_path / config.ledger_filename("ORG")
    r = run("--ledger", str(ledger), "-m", "ORG", "-v", "1", "--backfill", str(listing))
    assert r.returncode == 0, r.stdout + r.stderr
    out = json.loads(r.stdout)
    assert {(x["from"], x["to"]) for x in out["renames"]} == {
        ("srs.md", "srs-org.md"), ("db-script.md", "db-script-org.md")}
    data = json.loads(ledger.read_text(encoding="utf-8"))
    sec = data["versions"]["1"]
    assert sec["status"] == "CLOSED"
    names = {row["filename"] for row in sec["artifacts"]}
    assert names == {"srs-org.md", "db-script-org.md", "registry-srs-org.md"}
    # legacy map is derived from config, never hand-written
    assert config.legacy_name_map("ORG")["backend-execution-plan.md"] == "backend-execution-plan-org.md"
