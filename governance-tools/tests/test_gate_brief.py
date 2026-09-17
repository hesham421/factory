"""The gate brief renders from `reviewers/pass-review.md` with zero Jinja
errors and carries §3.5, the adversarial reading — the four probes the
reviewer works where `gov.py analyze` stopped."""
from __future__ import annotations

from config import CFG
from test_orchestrator import orch_root, _run_pass1, _consumer  # noqa: F401 (fixture reuse)


def test_gate_brief_renders_the_adversarial_reading(orch_root, mod, tmp_path, monkeypatch):
    _consumer(tmp_path, monkeypatch, "backend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    text = (CFG.state_dir(mod, 1) / "briefs" / "gate-pass-1.md").read_text(encoding="utf-8")
    assert "{{" not in text and "{%" not in text, "an unrendered Jinja expression survived"
    assert "## 3.5 Adversarial reading" in text
    for probe in ("**P1 — Invert every check.**", "**P2 — Closure questions per record.**",
                  "**P3 — Read the seams.**", "**P4 — Error vs pattern.**"):
        assert probe in text
    # P3 names the pass's own stage chain, from factory.yaml
    assert " → ".join(CFG.passes["1"]["stages"]) in text
    # numbering of §4–§8 and the §8 schema untouched
    for h in ("## 4. Scorecard", "## 5. Traceability", "## 6. Profile extra checks", "## 7. Decisions", "## 8. Output"):
        assert h in text
    assert '"verdict": "' + "|".join(CFG.review["verdicts"]) + '"' in text
    # the gate names one lane, and it is the read-only dialogue lane
    g = CFG.gate_after(CFG.passes["1"]["stages"][-1])
    lane = CFG.lane(g["lane"])
    assert lane.get("read_only") and len(lane["implementers"]) == 2 and lane["dialogue"]["converge_on"] == "merged-scorecard"
    assert f"`{g['lane']}` lane" in text
