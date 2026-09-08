"""Safe auto-fix (j): deterministic, reversible repairs only; <file>.orig kept."""
from __future__ import annotations

from config import CFG
from toolkit.markers import safe_autofix, validate

import planfx as fx
from planfx import START, END, marker, atom


def _w(tmp_path, body, name="plan.md"):
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_separator_typo_and_bare_sub_are_fixed_with_backup(tmp_path, mod):
    g = fx.grammar("backend", "exec")
    ph = fx.threshold_phase(g)
    kind = fx.countable_kind(g, ph)
    typo = ph.key.replace("-", "_")
    assert typo != ph.key
    body = (marker(g.phase_kind, typo, START) + marker(g.sub_kind, "BARE", START, "  ")
            + atom(kind, CFG.make_id(g.atom_kinds[kind], mod, 1), "x") + marker(g.sub_kind, "BARE", END, "  ")
            + marker(g.phase_kind, typo, END))
    p = _w(tmp_path, body)
    rep = safe_autofix(p, "backend", "exec")
    assert rep.changed and rep.remaining == []
    assert rep.phase_key_fixes == [{"from": typo, "to": ph.key, "line": 1}]
    assert [f["to"] for f in rep.sub_qualification_fixes] == [f"{ph.key}-BARE"]
    text = p.read_text(encoding="utf-8")
    assert f"{g.phase_kind}:{ph.key}:START" in text and f"{g.phase_kind}:{ph.key}:END" in text
    assert f"{g.sub_kind}:{ph.key}-BARE:START" in text and f"{g.sub_kind}:{ph.key}-BARE:END" in text
    assert typo not in text
    assert rep.backup == tmp_path / "plan.md.orig" and rep.backup.read_text(encoding="utf-8") == body
    assert validate(p, "backend", "exec").findings == []


def test_plus_and_space_separators_normalise(tmp_path):
    g = fx.grammar("backend", "exec")
    key = next(p.key for p in g.phases if "-" in p.key)
    for variant in (key.replace("-", "+"), key.replace("-", " "), key.replace("-", "--"), key.lower()):
        p = _w(tmp_path, marker(g.phase_kind, variant, START) + "x\n" + marker(g.phase_kind, variant, END), f"{abs(hash(variant))}.md")
        rep = safe_autofix(p, "backend", "exec")
        assert rep.phase_key_fixes and rep.phase_key_fixes[0]["to"] == key, variant
        assert rep.remaining == []


def test_exempt_plan_subs_are_left_bare(tmp_path, mod):
    p = _w(tmp_path, fx.test_plan(mod, over=True))
    before = p.read_text(encoding="utf-8")
    rep = safe_autofix(p, "backend", "test")
    assert rep.sub_qualification_fixes == [] and not rep.changed
    assert p.read_text(encoding="utf-8") == before and rep.backup is None


def test_unfixable_is_reported_and_untouched(tmp_path):
    g = fx.grammar("backend", "exec")
    p = _w(tmp_path, marker(g.phase_kind, g.phases[0].key, START) + "x\n")     # unclosed → needs a human
    rep = safe_autofix(p, "backend", "exec")
    assert not rep.changed and rep.backup is None
    assert any(f.rule == "marker-unclosed" for f in rep.remaining)
    assert not (tmp_path / "plan.md.orig").exists()


def test_already_valid_file_is_noop(tmp_path, mod):
    p = _w(tmp_path, fx.exec_plan(mod))
    before = p.read_bytes()
    rep = safe_autofix(p, "backend", "exec")
    assert not rep.changed and rep.phase_key_fixes == [] and rep.sub_qualification_fixes == [] and rep.remaining == []
    assert p.read_bytes() == before


def test_ambiguous_key_is_left_for_a_human(tmp_path):
    g = fx.grammar("backend", "exec")
    key = next(p.key for p in g.phases if "-" in p.key)
    squashed = key.replace("-", "")                     # cannot be restored unambiguously
    p = _w(tmp_path, marker(g.phase_kind, squashed, START) + "x\n" + marker(g.phase_kind, squashed, END))
    rep = safe_autofix(p, "backend", "exec")
    assert rep.phase_key_fixes == [] and not rep.changed
    assert any(f.rule == "phase-unknown" and squashed in f.message for f in rep.remaining)
