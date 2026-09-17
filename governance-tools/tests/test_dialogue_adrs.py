"""What a dialogue settled is kept: every DECISION block of a converged
dialogue lane becomes an ADR in the decisions partition (naming.adr_file,
status factory.dialogue.adr_status), continuing the module's ADR stream, and
never twice for the same settled point."""
from __future__ import annotations

from config import CFG
import dispatch as dp
import gov
import orchfx as fx
from test_orchestrator import orch_root  # noqa: F401 (fixture reuse)


def _fake_for(mod, decisions_round2: list[str]):
    def fake(brief, impl, effort, round_no):
        out = []
        if round_no >= 2:
            for a in CFG.stage("P0").produces:
                p = CFG.artifact_path(mod, "P0", a.artifact, 1)
                body = {"platform-summary": fx.platform_summary(mod), "module-registry": fx.module_registry(mod),
                        "business-policies": fx.business_policies(mod)}[a.artifact]
                out.append(f"<<<FILE: {p}>>>\n{body}\n<<<END FILE>>>")
            out += decisions_round2
            out.append(dp.CONVERGED)
        else:
            out.append(f"{CFG.dialogue['proposal_token']} tiering — two tiers or three?")
        return "\n".join(out)
    return fake


def test_dialogue_decisions_become_adrs(orch_root, mod, monkeypatch):
    monkeypatch.setenv("GOV_RUNNER", "fake")
    fx.write_stage("domain-profile", mod); fx.write_stage("P-1", mod)
    tok = CFG.dialogue["decision_token"]
    pol = fx.mid("POL", mod, 1)
    # one ADR already in the stream — the dialogue's continue after it
    d = CFG.decisions_dir(mod); d.mkdir(parents=True, exist_ok=True)
    (d / CFG.fmt(CFG.naming["adr_file"], mod=mod, seq=1)).write_text("# earlier\nStatus      : ACCEPTED\n", encoding="utf-8")
    dp.set_fake(_fake_for(mod, [
        f"{tok} two tiers, not three",
        f"Accepted: the platform profile names two tiers; three would split {pol} across owners.",
        "",
        f"- {tok} lookup values are runtime-loaded",
        "Amended with reason: no hardcoded enum — the lookup module owns the values.",
    ]))
    try:
        assert gov.run_stage("P0", mod, 1, complete=False, no_commit=True) == gov.OK
    finally:
        dp.set_fake(None)

    files = sorted(p.name for p in d.glob("*.md"))
    assert files == [CFG.fmt(CFG.naming["adr_file"], mod=mod, seq=i) for i in (1, 2, 3)]
    two = (d / files[1]).read_text(encoding="utf-8")
    assert f"Status      : {CFG.dialogue['adr_status']}" in two
    assert "two tiers, not three" in two and pol in two and "Version: v1" in two
    assert f"Stage       : P0" in two and CFG.stage("P0").lane in two
    three = (d / files[2]).read_text(encoding="utf-8")
    assert "runtime-loaded" in three and "Amended with reason" in three
    # not a BLOCKED ADR — the stage was not stopped by its own record of a settled point
    assert dp.blocked_adrs(mod, 1) == []


def test_re_running_the_stage_does_not_mint_the_same_decision_twice(orch_root, mod, monkeypatch):
    monkeypatch.setenv("GOV_RUNNER", "fake")
    fx.write_stage("domain-profile", mod); fx.write_stage("P-1", mod)
    tok = CFG.dialogue["decision_token"]
    dp.set_fake(_fake_for(mod, [f"{tok} two tiers, not three", "settled."]))
    try:
        assert gov.run_stage("P0", mod, 1, complete=False, no_commit=True) == gov.OK
        first = sorted(p.name for p in CFG.decisions_dir(mod).glob("*.md"))
        assert gov.run_stage("P0", mod, 1, complete=False, no_commit=True) == gov.OK
    finally:
        dp.set_fake(None)
    assert sorted(p.name for p in CFG.decisions_dir(mod).glob("*.md")) == first == [CFG.fmt(CFG.naming["adr_file"], mod=mod, seq=1)]


def test_decisions_in_reads_title_and_body_and_stops_at_the_marker():
    tok = CFG.dialogue["decision_token"]
    text = f"prose\n{tok} one\nline a\nline b\n\n{tok} two\n{dp.CONVERGED}\n"
    assert dp.decisions_in(text) == [("one", "line a\nline b"), ("two", "")]
