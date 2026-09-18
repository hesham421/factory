"""End to end with no operator step (the nightly job runs exactly this):
GOV_RUNNER=fake drives a NON-ERP toy profile through pass 1 → gate
(auto-verdict through the review dialogue) → split → fetch-inputs (the shared
commit recorded) → pass 2 → gate → tag. Every command returns; nothing is left
AWAITING. The one human act is the PRD approval, which factory.yaml declares
as a human decision point (`gates: prd-approval`) — the test performs it, as
the human would, and `gov.py next` names it as the step in between.
"""
from __future__ import annotations

import json
import re

import pytest
import yaml

from config import CFG
import analyze as an
import dispatch as dp
import gov
import orchfx as fx
from test_orchestrator import orch_root, _consumer, _git  # noqa: F401 (fixture reuse)
from test_agnostic import TOY

OK, BLOCKED, AWAITING = gov.OK, gov.BLOCKED, gov.AWAITING


def _init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "-q", cwd=path)
    (path / ".gitkeep").write_text("", encoding="utf-8")
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=path)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init", cwd=path)
    return path


@pytest.fixture
def auto(orch_root, tmp_path, monkeypatch):
    """A project repo scaffolded on the fly (`gov.py new-project`) carrying the
    toy profile, the fake runner, both consumer checkouts present."""
    monkeypatch.setenv(CFG.runner["env"], "fake")
    project = tmp_path / "toy-governance"
    assert gov.cmd_new_project(project, "toy", "Clinic Suite", None) == OK
    (project / CFG.paths["profiles"] / "toy.yaml").write_text(yaml.safe_dump(TOY, sort_keys=False), encoding="utf-8")
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "the toy profile", cwd=project)
    monkeypatch.setenv(CFG.project["checkout_env"], str(project))
    monkeypatch.delenv("GOV_PROFILE", raising=False)
    CFG.reload()
    _consumer(tmp_path, monkeypatch, "backend")
    _consumer(tmp_path, monkeypatch, "frontend")
    mod = next(iter(CFG.profile.vocabulary["module_prefixes"]))
    log: list[tuple[str, str, int]] = []
    yield orch_root, project.resolve(), mod, log
    dp.set_fake(None)


def _card(mod: str, verdict: str) -> dict:
    r = CFG.review
    findings = [] if verdict == "APPROVE" else [
        {"id": "G1", "severity": "MAJOR", "artifact": "srs", "line": None, "clause": r["rubric"][0],
         "problem": "one statement two implementers would build differently", "fix": "state the measure", "adr": False}]
    return {"module": mod, "version": 1, "scores": {k: r["scale"]["max"] for k in r["rubric"]},
            "extra_checks": [], "analyze_confirmed": [], "findings": findings, "adrs_reviewed": [], "verdict": verdict}


def make_fake(mod: str, log: list, gate_verdicts: list[str]):
    """A runner that answers every brief the orchestrator can send: a stage
    (dialogue or not) with the fixture artifacts as file blocks, a gate with a
    scorecard (round 1 scores, round 2 merges and converges), a revise with a
    rewrite of the artifact the finding names."""
    state = {"gates": 0, "last": None}
    tok = CFG.dialogue

    def fake(brief, impl, effort, round_no):
        text = brief.read_text(encoding="utf-8").lstrip()     # the gate template opens with a Jinja comment → blank lines
        log.append((brief.name, str(impl), round_no))
        if text.startswith("# GATE BRIEF"):
            if round_no == 1:
                state["last"] = gate_verdicts[min(state["gates"], len(gate_verdicts) - 1)]
                state["gates"] += 1
                return "Round one scores the pass.\n```json\n" + json.dumps(_card(mod, state["last"])) + "\n```\n"
            return (f"{tok['decision_token']} the merged scorecard stands\nboth reviewers agree on every row.\n\n"
                    "```json\n" + json.dumps(_card(mod, state["last"])) + "\n```\n" + dp.CONVERGED)
        if text.startswith("# REVISE BRIEF"):
            srs = CFG.artifact_path(mod, "P1", "srs", 1)
            return f"<<<FILE: {srs}>>>\n{fx.srs(mod)}\n<<<END FILE>>>\n"
        stage = CFG.stage(re.search(r"stage `([^`]+)`", text).group(1))
        if stage.dialogue and round_no == 1:
            return f"{tok['proposal_token']} two tiers or three? recommend two."
        out = [f"<<<FILE: {p}>>>\n{p.read_text(encoding='utf-8')}\n<<<END FILE>>>" for p in fx.write_stage(stage.id, mod)]
        if stage.dialogue:
            out += [f"{tok['decision_token']} two tiers, not three\nsettled: the profile names two.\n", dp.CONVERGED]
        return "\n".join(out)
    return fake


def _gate_record(mod: str, pass_no: str) -> dict:
    p = CFG.version_root(mod, 1) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": pass_no})
    return json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))


def _through_pass_1(mod: str) -> None:
    assert gov.next_step(mod, 1)[1][:2] == ["run-stage", CFG.stages[0].id]
    assert gov.run_stage(CFG.stages[0].id, mod, 1, complete=False, no_commit=False) == OK
    assert gov.run_stage(CFG.stages[1].id, mod, 1, complete=False, no_commit=False) == OK
    # pass 1 advances stage by stage and stops only at the human decision point
    assert gov.run_pass("1", mod, 1, new=False, complete=False, no_commit=False) == BLOCKED
    what, argv = gov.next_step(mod, 1)
    assert argv[0] == "approve" and "human approval" in what
    assert gov.approve(argv[1], mod, 1, "e2e", no_commit=False) == OK
    assert gov.run_pass("1", mod, 1, new=False, complete=False, no_commit=False) == OK
    assert gov.next_step(mod, 1)[1][:2] == ["gate", "1"]


def test_full_pipeline_runs_with_no_operator(auto):
    root, shared, mod, log = auto
    dp.set_fake(make_fake(mod, log, ["APPROVE"]))
    _through_pass_1(mod)

    # gate 1: the review lane's two implementers argue one brief; the verdict is recorded, no AWAITING
    assert gov.gate("1", mod, 1, complete=False, result=None, no_commit=False) == OK
    rec = _gate_record(mod, "1")
    assert rec["verdict"] == "APPROVE"
    assert [m["id"] for m in rec["coverage"]] == [m["id"] for m in CFG.analyze["coverage"]]
    assert (CFG.state_dir(mod, 1) / "briefs" / "gate-pass-1.result.json").exists()
    lane = CFG.lane(CFG.gate_after(CFG.passes["1"]["stages"][-1])["lane"])
    review = [e for e in log if e[0].startswith("gate-pass-1")]
    assert [e[1] for e in review] == lane["implementers"][:2] and [e[2] for e in review] == [1, 2]

    # split — `next --run` executes it
    assert gov.next_step(mod, 1)[1][:3] == ["split", "--track", CFG.passes["1"]["track"]]
    assert gov.cmd_next(mod, 1, run=True) == OK
    assert gov.next_step(mod, 1)[1][0] == "fetch-inputs"
    assert gov.run_pass("2", mod, 1, new=False, complete=False, no_commit=False) == BLOCKED

    # the backend publishes api-docs into the shared partition and commits there; fetch records that commit
    name, spec = next(iter(CFG.inputs.items()))
    pub = CFG.partition_dir(spec["partition"], mod)
    pub.mkdir(parents=True, exist_ok=True)
    (pub / "index.md").write_text(fx.api_docs(mod), encoding="utf-8")
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=shared)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "backend: publish api-docs", cwd=shared)
    head = _git("rev-parse", "HEAD", cwd=shared).stdout.strip()
    assert gov.cmd_fetch_inputs(mod, 1, pull=False) == OK
    dst = CFG.inputs_dir(mod, 1) / CFG.fmt(spec["file"], mod=mod)
    meta = json.loads(dst.with_name(CFG.fmt(CFG.paths["module"]["input_meta"], file=dst.name)).read_text(encoding="utf-8"))
    assert meta["commit"] == head

    # pass 2 → gate 2 → split → tag, still no operator
    assert gov.run_pass("2", mod, 1, new=False, complete=False, no_commit=False) == OK
    assert gov.gate("2", mod, 1, complete=False, result=None, no_commit=False) == OK
    assert _gate_record(mod, "2")["verdict"] == "APPROVE"
    assert gov.main(["split", "--track", CFG.passes["2"]["track"], "-m", mod, "-v", "1"]) == OK
    assert gov.next_step(mod, 1)[1][0] == "tag"
    assert gov.cmd_tag(mod, 1) == OK
    assert CFG.tag_name(mod, 1) in _git("tag", "-l", cwd=shared).stdout       # on the project repo
    assert CFG.tag_name(mod, 1) not in _git("tag", "-l", cwd=root).stdout    # never on the tool
    assert gov.next_step(mod, 1)[1] is None

    # what the dialogues settled is in the decisions partition, and the whole module analyzes clean
    adrs = sorted(CFG.decisions_dir(mod).glob("*.md"))
    assert adrs and all(CFG.dialogue["adr_status"] in p.read_text(encoding="utf-8") for p in adrs)
    assert an.run(mod, 1, scope="all").clean
    # every artifact and every record landed in the shared repo, none in the tool tree
    assert (shared / CFG.paths["modules"] / mod).is_dir()
    assert not (root / CFG.paths["modules"]).exists()
    assert "AWAITING" not in " ".join(e[0] for e in log)
    state = json.loads((CFG.module_root(mod) / CFG.paths["module"]["manifest_file"]).read_text(encoding="utf-8"))
    assert state["status"]["inputs"][name]["commit"] == head and "coverage" in state["status"]


def test_a_revise_is_applied_re_analyzed_and_re_gated_once(auto):
    root, shared, mod, log = auto
    dp.set_fake(make_fake(mod, log, ["REVISE", "APPROVE"]))
    _through_pass_1(mod)
    assert gov.gate("1", mod, 1, complete=False, result=None, no_commit=False) == OK
    assert _gate_record(mod, "1")["verdict"] == "APPROVE"
    g = CFG.gate_after(CFG.passes["1"]["stages"][-1])
    revise = [e for e in log if e[0].startswith("revise-pass-1")]
    assert len(revise) == 1 and revise[0][1] == CFG.lane(g["on_revise"])["implementers"][0]
    assert (CFG.state_dir(mod, 1) / "briefs" / "revise-pass-1.md").exists()
    history = _git("log", "--format=%s", cwd=shared).stdout
    assert CFG.commit_msg("gate", **{"pass": "1"}, mod=mod, version=1, verdict="REVISE") in history
    assert CFG.commit_msg("gate", **{"pass": "1"}, mod=mod, version=1, verdict="APPROVE") in history
    assert sum(1 for e in log if e[0].startswith("gate-pass-1") and e[2] == 1) == 2, "the gate was re-run exactly once"


def test_a_second_revise_escalates_to_the_human(auto):
    root, shared, mod, log = auto
    dp.set_fake(make_fake(mod, log, ["REVISE", "REVISE"]))
    _through_pass_1(mod)
    assert gov.gate("1", mod, 1, complete=False, result=None, no_commit=False) == BLOCKED
    assert _gate_record(mod, "1")["verdict"] == "ESCALATE"
    assert sum(1 for e in log if e[0].startswith("revise-pass-1")) == int(CFG.review["revise_max"])
    what, argv = gov.next_step(mod, 1)
    assert argv[:2] == ["gate", "1"] and "ESCALATE" in what


def test_manual_mode_is_unchanged(auto, monkeypatch):
    root, shared, mod, log = auto
    dp.set_fake(make_fake(mod, log, ["APPROVE"]))
    _through_pass_1(mod)
    monkeypatch.setenv(CFG.runner["env"], "manual")
    assert gov.gate("1", mod, 1, complete=False, result=None, no_commit=False) == AWAITING
    assert not [e for e in log if e[0].startswith("gate-pass-1")]


def test_the_cmd_template_must_pass_the_model(factory_root, tmp_path, monkeypatch):
    """A dialogue lane alternates implementers; a template that does not pass
    {model} would hand every round to the lane's one configured model."""
    monkeypatch.setenv(CFG.runner["env"], "cmd")
    brief = tmp_path / "b.md"
    brief.write_text("x", encoding="utf-8")
    impl = dp.Implementer.parse("claude:opus")
    monkeypatch.setenv(CFG.runner["cmd_env"], "printf '%s' {lane} > {out}")
    with pytest.raises(RuntimeError, match="model"):
        dp.run_round(brief, impl, "high", 1, lane_id="analysis")
    monkeypatch.setenv(CFG.runner["cmd_env"], "printf '%s' {model}:{lane}:{read_only_flag} > {out}")
    out = dp.run_round(brief, impl, "high", 1, lane_id="analysis", read_only=True)
    assert out.read_text(encoding="utf-8") == "opus:analysis:--read-only"
