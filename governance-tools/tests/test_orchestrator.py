"""
End-to-end dry run of the orchestrator (blueprint §12 step 6): a sample module
moves through every stage, both gates, split, delivery to a consumer repo,
tag, then a delta version — under the active (ERP) profile. Everything is
generated from CFG, so the same run proves the pipeline for any profile.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from config import CFG
import analyze as an
import dispatch as dp
import gov
import state as st
import orchfx as fx
from conftest import REAL_ROOT

OK, BLOCKED, AWAITING = gov.OK, gov.BLOCKED, gov.AWAITING


def _git(*a, cwd):
    return subprocess.run(["git", *a], cwd=str(cwd), check=True, capture_output=True, text=True)


@pytest.fixture
def orch_root(factory_root, monkeypatch):
    """Isolated root with everything the orchestrator reads: shared/, engines/, standalone/, reviewers/ + git."""
    for d in ("shared", "engines", "standalone", "reviewers"):
        shutil.copytree(REAL_ROOT / d, factory_root / d)
    shutil.copytree(REAL_ROOT / "governance-tools" / "templates", factory_root / "governance-tools" / "templates")
    _git("init", "-q", cwd=factory_root)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=factory_root)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base", cwd=factory_root)
    monkeypatch.setenv("GOV_RUNNER", "manual")
    CFG.reload()
    return factory_root


def _consumer(tmp_path: Path, monkeypatch, name: str) -> Path:
    repo = tmp_path / name
    repo.mkdir()
    _git("init", "-q", cwd=repo)
    (repo / "README.md").write_text("consumer\n")
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=repo)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init", cwd=repo)
    monkeypatch.setenv(CFG.repos[name]["checkout_env"], str(repo))
    return repo


def _approve_result(tmp_path: Path) -> Path:
    r = CFG.review
    p = tmp_path / "review.json"
    p.write_text(json.dumps({"verdict": "APPROVE", "scores": {k: r["scale"]["max"] for k in r["rubric"]}, "findings": []}))
    return p


# ── stages ──────────────────────────────────────────────────────────────────

def test_stage_awaits_operator_then_completes(orch_root, mod):
    """manual runner: run-stage writes a brief and returns AWAITING; --complete analyzes + commits."""
    fx.write_stage("domain-profile", mod)
    rc = gov.run_stage("P-1", mod, 1, complete=False, no_commit=False)
    assert rc == AWAITING
    brief = CFG.state_dir(mod, 1) / "briefs" / "P-1.md"
    assert brief.exists() and "# ENGINE" in brief.read_text() and "<<<INPUT: domain-profile>>>" in brief.read_text()
    fx.write_stage("P-1", mod)
    assert gov.run_stage("P-1", mod, 1, complete=True, no_commit=False) == OK
    log = _git("log", "--oneline", cwd=orch_root).stdout
    assert CFG.commit_msg("stage", stage="P-1", mod=mod, version=1, summary="Registry & Steering Builder") in log


def test_missing_input_blocks(orch_root, mod):
    assert gov.run_stage("P0", mod, 1, complete=False, no_commit=True) == BLOCKED   # no domain-profile / registry yet


def test_prd_approval_gate_blocks_p1(orch_root, mod):
    for s in ("domain-profile", "P-1", "P0", "P0.5"):
        fx.write_stage(s, mod)
    assert gov.run_stage("P1", mod, 1, complete=False, no_commit=True) == BLOCKED
    assert gov.approve("prd-approval", mod, 1, "tester", no_commit=True) == OK
    assert gov.run_stage("P1", mod, 1, complete=False, no_commit=True) == AWAITING


def test_forbidden_question_is_refused(orch_root, mod):
    for s in ("domain-profile", "P-1", "P0", "P0.5"):
        fx.write_stage(s, mod)
    gov.approve("prd-approval", mod, 1, "tester", no_commit=True)
    paths = fx.write_stage("P1", mod)
    srs = next(p for p in paths if "registry" not in p.name)
    srs.write_text(srs.read_text() + "\n[QUESTION] which currency?\n")
    assert gov.run_stage("P1", mod, 1, complete=True, no_commit=True) == BLOCKED


def test_blocked_adr_stops_the_pass(orch_root, mod):
    for s in ("domain-profile", "P-1", "P0", "P0.5"):
        fx.write_stage(s, mod)
    gov.approve("prd-approval", mod, 1, "tester", no_commit=True)
    fx.write_stage("P1", mod)
    d = CFG.decisions_dir(mod); d.mkdir(parents=True, exist_ok=True)
    (d / CFG.fmt(CFG.naming["adr_file"], mod=mod, seq=1)).write_text(
        f"# {fx.mid('ADR', mod, 1)} — breaking\nStatus      : BLOCKED\nStage       : P1        Module: {mod}        Version: v1\ntraces      : {fx.mid('REQ', mod, 1)}\n")
    assert gov.run_stage("P1", mod, 1, complete=True, no_commit=True) == BLOCKED


# ── the full dry run ────────────────────────────────────────────────────────

def _run_pass1(orch_root, mod, tmp_path, monkeypatch):
    for s in ("domain-profile", "P-1"):
        fx.write_stage(s, mod)
    assert gov.run_stage("P-1", mod, 1, complete=True, no_commit=False) == OK
    assert gov.run_pass("1", mod, 1, new=False, complete=False, no_commit=False) == AWAITING
    assert (CFG.state_dir(mod, 1) / "briefs" / "pass-1.md").exists()
    for s in ("P0", "P0.5"):
        fx.write_stage(s, mod)
        assert gov.run_stage(s, mod, 1, complete=True, no_commit=False) == OK
    assert gov.approve("prd-approval", mod, 1, "tester", no_commit=False) == OK
    for s in ("P1", "P2", "P3.1"):
        fx.write_stage(s, mod)
        assert gov.run_stage(s, mod, 1, complete=True, no_commit=False) == OK, s
    # gate: awaiting the reviewer, then APPROVE
    assert gov.gate("1", mod, 1, complete=False, result=None, no_commit=False) == AWAITING
    assert (CFG.state_dir(mod, 1) / "briefs" / "gate-pass-1.md").exists()
    assert gov.gate("1", mod, 1, complete=True, result=_approve_result(tmp_path), no_commit=False) == OK
    rec = CFG.version_root(mod, 1) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": "1"})
    assert rec.exists() and "APPROVE" in rec.read_text()


def test_full_dry_run_both_passes_split_deliver_tag(orch_root, mod, tmp_path, monkeypatch):
    backend = _consumer(tmp_path, monkeypatch, "backend")
    frontend = _consumer(tmp_path, monkeypatch, "frontend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    # split + deliver backend
    assert gov.main(["split", "--track", "backend", "-m", mod, "-v", "1"]) == OK
    pkg = CFG.packages_dir(mod, "backend", "exec", 1)
    assert (pkg / "index.md").exists() and any(pkg.rglob("*.md"))
    assert gov.cmd_deliver("backend", mod, 1, push=False) == OK
    dest = backend / CFG.fmt(CFG.repos["backend"]["deliver_to"], mod=mod)
    es = json.loads((dest / CFG.delivery["execution_state"]["file"]).read_text())
    assert es["module"] == mod and es["track"] == "backend" and es["gate"]["verdict"] == "APPROVE" and es["phases"]
    assert _git("branch", "--show-current", cwd=backend).stdout.strip() == CFG.delivery_branch(mod, 1, "backend")
    # pass 2 needs the api-docs input back from the backend repo
    assert gov.run_pass("2", mod, 1, new=False, complete=False, no_commit=False) == BLOCKED
    pub = backend / CFG.fmt(CFG.repos["backend"]["publishes"]["api-docs"], mod=mod)
    pub.parent.mkdir(parents=True, exist_ok=True); pub.write_text(fx.api_docs(mod))
    assert gov.cmd_fetch_inputs(mod, 1, pull=False) == OK
    assert gov.run_pass("2", mod, 1, new=False, complete=False, no_commit=False) == AWAITING
    fx.write_stage("P3.2", mod)
    assert gov.run_stage("P3.2", mod, 1, complete=True, no_commit=False) == OK
    assert gov.gate("2", mod, 1, complete=True, result=_approve_result(tmp_path), no_commit=False) == OK
    assert gov.main(["split", "--track", "frontend", "-m", mod, "-v", "1"]) == OK
    assert gov.cmd_deliver("frontend", mod, 1, push=False) == OK
    assert gov.cmd_tag(mod, 1) == OK
    assert CFG.tag_name(mod, 1) in _git("tag", "-l", cwd=orch_root).stdout
    # whole-module analyze is clean
    rep = an.run(mod, 1, scope="all")
    assert rep.clean, [str(f) for f in rep.findings]
    assert gov.cmd_status(mod) == OK
    # standalone test-gen: outside the line, derives TC from AC, split with plan `test`
    assert gov.run_stage("test-gen", mod, 1, complete=False, no_commit=False) == AWAITING
    fx.write_stage("test-gen", mod)
    assert gov.run_stage("test-gen", mod, 1, complete=True, no_commit=False) == OK
    assert gov.main(["split", "--track", "backend", "--plan", "test", "-m", mod, "-v", "1"]) == OK
    assert any(CFG.packages_dir(mod, "backend", "test", 1).glob("*.md"))
    rep = an.run(mod, 1, scope="all")
    assert rep.clean, [str(f) for f in rep.findings]


def test_analyze_catches_contract_violations(orch_root, mod):
    for s in ("domain-profile", "P-1", "P0", "P0.5"):
        fx.write_stage(s, mod)
    fx.write_stage("P1", mod)
    srs = CFG.artifact_path(mod, "P1", "srs", 1)
    text = srs.read_text().replace("When a user submits form 1, the system shall validate and store the record.",
                                   "Users can submit forms.")   # not EARS
    text = text.replace(f"  Traces     : {fx.mid('US', mod, 1)}\n", "", 1)              # REQ without trace
    srs.write_text(text)
    rep = an.run(mod, 1, scope="stage:P1")
    checks = {f.check for f in rep.findings}
    assert "ears" in checks and "traces" in checks and not rep.clean


def test_delta_version_state_folding_and_continuity(orch_root, mod, tmp_path, monkeypatch):
    for s in ("domain-profile", "P-1", "P0", "P0.5", "P1"):
        fx.write_stage(s, mod)
    st.build_state(mod, 1)
    assert gov.cmd_version(mod, True, quiet=True) == 2
    # v2: srs adds REQ 3 (continues the sequence), omits unchanged blocks; registry re-emitted whole
    cm = CFG.version_root(mod, 2) / CFG.paths["module"]["change_manifest"]
    cm.write_text(f"# CHANGE MANIFEST — {fx.mid('CS', mod, 1)}\nModule: {mod}  Version: v2  Baseline: v1\nChange type  : ADDITIVE\nSummary      : add req 3\n\n## Per artifact\nsrs:\n  ADDED    : {fx.mid('REQ', mod, 3)}, {fx.mid('AC', mod, 3)}\n  MODIFIED : {fx.mid('SCR-REQ', mod, 1)}\n  UNCHANGED: {fx.mid('REQ', mod, 1)}, {fx.mid('REQ', mod, 2)}\nregistry-srs:\n  MODIFIED : all\n")
    fx.write(CFG.artifact_path(mod, "P1", "srs", 2), fx.srs(mod, n_req=1, start=3))
    fx.write(CFG.artifact_path(mod, "P1", "registry-srs", 2), fx.registry_srs(mod, end=3))
    rep = st.build_state(mod, 2)
    cur = st.state_text(mod, 2, "srs")
    assert all(fx.mid("REQ", mod, i) in cur for i in (1, 2, 3)) and "carried from baseline v1" in cur
    a = an.run(mod, 2, scope="stage:P1")
    assert not [f for f in a.findings if f.check == "ids-continue"], [str(f) for f in a.findings]
    # re-minting an existing ID with different content (not listed MODIFIED) is CRITICAL
    fx.write(CFG.artifact_path(mod, "P1", "srs", 2), fx.srs(mod, n_req=1, start=1).replace("validate and store", "silently drop"))
    a2 = an.run(mod, 2, scope="stage:P1")
    assert any(f.check == "ids-continue" and f.severity == "CRITICAL" for f in a2.findings)


def test_fake_runner_dialogue_converges_and_ingests_files(orch_root, mod, monkeypatch):
    """cmd/fake runners: a dialogue lane alternates implementers until CONVERGED; file blocks are written."""
    monkeypatch.setenv("GOV_RUNNER", "fake")
    fx.write_stage("domain-profile", mod); fx.write_stage("P-1", mod)
    seen = []

    def fake(brief, impl, effort, round_no):
        seen.append((str(impl), round_no))
        out = []
        if round_no >= 2:
            for a in CFG.stage("P0").produces:
                rel = CFG.artifact_path(mod, "P0", a.artifact, 1).relative_to(CFG.root)
                body = {"platform-summary": fx.platform_summary(mod), "module-registry": fx.module_registry(mod),
                        "business-policies": fx.business_policies(mod)}[a.artifact]
                out.append(f"<<<FILE: {rel}>>>\n{body}\n<<<END FILE>>>")
            out.append(dp.CONVERGED)
        else:
            out.append("PROPOSAL: tiering — recommend two tiers.")
        return "\n".join(out)

    dp.set_fake(fake)
    try:
        assert gov.run_stage("P0", mod, 1, complete=False, no_commit=True) == OK
    finally:
        dp.set_fake(None)
    impls = CFG.lane(CFG.stage("P0").lane)["implementers"]
    assert seen[0][0] == impls[0] and seen[1][0] == impls[1 % len(impls)] and len(seen) == 2
    assert CFG.artifact_path(mod, "P0", "prd" if False else "platform-summary", 1).exists()


def test_render_and_lint_are_clean_in_the_real_repo():
    """The real repo must be lint-clean and fully rendered (C1)."""
    import subprocess, sys
    r = subprocess.run([sys.executable, str(REAL_ROOT / "governance-tools" / "gov.py"), "lint"], capture_output=True, text=True, cwd=str(REAL_ROOT))
    assert r.returncode == 0, r.stdout[-2000:]
    assert "0 critical · 0 major" in r.stdout


# ── agnosticism at pipeline level: the same orchestrator under a NON-ERP profile ──

def test_toy_profile_runs_the_whole_line(orch_root, tmp_path, monkeypatch):
    """Clinic profile (different prefixes, phases, one language, other stack): the orchestrator, analyze,
    split and delivery all follow the profile — no ERP assumption survives."""
    import yaml
    from test_agnostic import TOY
    (orch_root / CFG.paths["profiles"] / "toy.yaml").write_text(yaml.safe_dump(TOY, sort_keys=False), encoding="utf-8")
    monkeypatch.setenv("GOV_PROFILE", "toy")
    CFG.reload(profile_id="toy")
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    assert mod not in ("ORG",) and CFG.profile.languages["all"] == ["en"]
    backend = _consumer(tmp_path, monkeypatch, "backend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    assert gov.main(["split", "--track", "backend", "-m", mod, "-v", "1"]) == OK
    folders = {p.name for p in CFG.packages_dir(mod, "backend", "exec", 1).iterdir() if p.is_dir()}
    assert {ph.folder for ph in CFG.profile.phases("backend", "exec")} <= folders     # toy phase folders, e.g. "records"
    assert gov.cmd_deliver("backend", mod, 1, push=False) == OK
    es = json.loads((backend / CFG.fmt(CFG.repos["backend"]["deliver_to"], mod=mod) / CFG.delivery["execution_state"]["file"]).read_text())
    assert es["profile"] == "toy" and {p["key"] for p in es["phases"]} == set(CFG.profile.phase_keys("backend", "exec"))
    # rendered docs follow the profile too
    import render
    txt = render.block_phases(CFG.reload(profile_id="toy"), "backend", "exec")
    assert "RECORDS" in txt and "SVC-API" not in txt


def test_new_domain_scaffold_then_lint_reports_todos(orch_root):
    assert gov.cmd_new_domain("shop") == OK
    p = CFG.profiles_dir() / "shop.yaml"
    text = p.read_text()
    assert "id: shop" in text and "TODO" in text
    import lint
    fs = lint.validate_profile(CFG, CFG.load_profile("shop"))
    assert any(f.severity in ("CRITICAL", "MAJOR") for f in fs)     # an unfilled scaffold does not pass
