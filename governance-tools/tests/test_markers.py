"""Marker parser — tokeniser, structure, uniqueness, semantics, traces (a–i)."""
from __future__ import annotations

import pytest

from config import CFG
from toolkit.common import track_plans
from toolkit.markers import parse

import planfx as fx
from planfx import START, END, marker, atom


def _rules(res, rule):
    return [f for f in res.findings if f.rule == rule]


def _first_countable(track="backend", plan="exec"):
    g = fx.grammar(track, plan)
    ph = fx.threshold_phase(g)
    return g, ph, fx.countable_kind(g, ph)


# ── (a) tokeniser: several markers on one line ──────────────────────────────

def test_multiple_markers_per_line_all_tokenised(mod):
    g, ph, kind = _first_countable()
    a1, a2 = (CFG.make_id(g.atom_kinds[kind], mod, i) for i in (1, 2))
    s1, s2 = f"{ph.key}-A", f"{ph.key}-B"
    text = (marker(g.phase_kind, ph.key, START)
            + marker(g.sub_kind, s1, START, "  ")
            + f"    <!-- {kind}:{a1}:START -->inline body<!-- {kind}:{a1}:END -->\n"
            + f"  <!-- {g.sub_kind}:{s1}:END --><!-- {g.sub_kind}:{s2}:START -->\n"
            + atom(kind, a2, "y")
            + marker(g.sub_kind, s2, END, "  ")
            + marker(g.phase_kind, ph.key, END))
    res = parse(text, "backend", "exec")
    assert res.findings == []
    ids = {(b.kind, b.id) for b in res.blocks()}
    assert ids == {(g.phase_kind, ph.key), (g.sub_kind, s1), (g.sub_kind, s2), (kind, a1), (kind, a2)}
    inline = next(b for b in res.blocks() if b.id == a1)
    assert inline.content == "inline body"


def test_comment_that_is_not_a_marker_is_ignored(mod):
    g = fx.grammar("backend", "exec")
    ph = g.phases[0]
    text = "<!-- source: some header comment -->\n" + marker(g.phase_kind, ph.key, START) + "x\n" + marker(g.phase_kind, ph.key, END)
    res = parse(text, "backend", "exec")
    assert res.findings == [] and len(res.blocks()) == 1


# ── (b) nesting / unmatched / mismatched / unclosed ─────────────────────────

def test_atom_at_document_root_is_illegal_nesting(mod):
    g, _ph, kind = _first_countable()
    text = atom(kind, CFG.make_id(g.atom_kinds[kind], mod, 1), "x", indent="")
    res = parse(text, "backend", "exec")
    assert any(f.severity == "CRITICAL" for f in _rules(res, "marker-nesting"))


def test_unmatched_end_is_critical():
    g = fx.grammar("backend", "exec")
    res = parse("text\n" + marker(g.phase_kind, g.phases[0].key, END), "backend", "exec")
    assert [f.severity for f in _rules(res, "marker-unmatched-end")] == ["CRITICAL"]


def test_mismatched_end_is_critical():
    g = fx.grammar("backend", "exec")
    a, b = g.phases[0].key, g.phases[1].key
    res = parse(marker(g.phase_kind, a, START) + "x\n" + marker(g.phase_kind, b, END), "backend", "exec")
    assert _rules(res, "marker-mismatched-end") and _rules(res, "marker-unclosed")
    assert all(f.severity == "CRITICAL" for f in res.findings)


def test_unclosed_marker_is_critical():
    g = fx.grammar("backend", "exec")
    res = parse(marker(g.phase_kind, g.phases[0].key, START) + "content\n", "backend", "exec")
    assert [f.severity for f in _rules(res, "marker-unclosed")] == ["CRITICAL"]


# ── (c) uniqueness ───────────────────────────────────────────────────────────

def test_duplicate_id_within_kind_is_critical(mod):
    g, ph, kind = _first_countable()
    aid = CFG.make_id(g.atom_kinds[kind], mod, 1)
    text = marker(g.phase_kind, ph.key, START) + atom(kind, aid, "a") + atom(kind, aid, "b") + marker(g.phase_kind, ph.key, END)
    res = parse(text, "backend", "exec")
    dup = _rules(res, "marker-duplicate")
    assert len(dup) == 1 and dup[0].severity == "CRITICAL" and aid in dup[0].message


def test_same_label_under_two_phases_is_duplicate_in_exempt_plan(mod):
    """Bare SUB labels (exempt plan) still must be unique across the file."""
    g = fx.grammar("backend", "test")
    ph = g.phases[0]
    label = ph.sub_labels[0]
    text = (marker(g.phase_kind, ph.key, START)
            + marker(g.sub_kind, label, START, "  ") + "  a\n" + marker(g.sub_kind, label, END, "  ")
            + marker(g.sub_kind, label, START, "  ") + "  b\n" + marker(g.sub_kind, label, END, "  ")
            + marker(g.phase_kind, ph.key, END))
    assert _rules(parse(text, "backend", "test"), "marker-duplicate")


# ── (d) unknown phase refused (exec and test plans) ─────────────────────────

@pytest.mark.parametrize("track,plan", [("backend", "exec"), ("frontend", "exec"), ("backend", "test"), ("frontend", "test")])
def test_unknown_phase_is_refused(track, plan):
    g = fx.grammar(track, plan)
    bogus = "NOT-A-" + g.phases[0].key
    res = parse(marker(g.phase_kind, bogus, START) + "x\n" + marker(g.phase_kind, bogus, END), track, plan)
    f = _rules(res, "phase-unknown")
    assert f and f[0].severity == "CRITICAL" and bogus in f[0].message
    assert res.blocking()


def test_typo_separator_in_phase_key_is_refused_not_skipped():
    g = fx.grammar("backend", "exec")
    key = next(p.key for p in g.phases if "-" in p.key)
    typo = key.replace("-", "+", 1)
    res = parse(marker(g.phase_kind, typo, START) + "x\n" + marker(g.phase_kind, typo, END), "backend", "exec")
    assert _rules(res, "phase-unknown")


# ── (e) foreign / unknown kinds ─────────────────────────────────────────────

def test_track_restricted_kind_in_other_track_is_foreign(mod):
    """A kind restricted to one track (markers.kinds.<K>.tracks) is CRITICAL in another."""
    kinds = CFG.markers["kinds"]
    kind = next(k for k, v in kinds.items() if v.get("tracks"))
    other = next(t for t in CFG.tracks if t not in kinds[kind]["tracks"])
    g = fx.grammar(other, "exec")
    ph = g.phases[0]
    text = marker(g.phase_kind, ph.key, START) + atom(kind, CFG.make_id(kinds[kind]["atom"], mod, 1), "x") + marker(g.phase_kind, ph.key, END)
    res = parse(text, other, "exec")
    f = _rules(res, "marker-foreign-kind")
    assert f and f[0].severity == "CRITICAL"
    assert not any(b.kind == kind for b in res.blocks()), "a foreign block must not enter the tree"


def test_plan_restricted_kind_in_other_plan_is_foreign(mod):
    kinds = CFG.markers["kinds"]
    kind = next(k for k, v in kinds.items() if v.get("plans"))
    plan = next(p for _t, p in track_plans() if p not in kinds[kind]["plans"])
    g = fx.grammar("backend", plan)
    ph = g.phases[0]
    text = marker(g.phase_kind, ph.key, START) + atom(kind, CFG.make_id(kinds[kind]["atom"], mod, 1), "x") + marker(g.phase_kind, ph.key, END)
    assert _rules(parse(text, "backend", plan), "marker-foreign-kind")


def test_unknown_kind_is_critical():
    g = fx.grammar("backend", "exec")
    ph = g.phases[0]
    text = marker(g.phase_kind, ph.key, START) + "  <!-- BOGUS:X-1:START -->\n  x\n  <!-- BOGUS:X-1:END -->\n" + marker(g.phase_kind, ph.key, END)
    f = _rules(parse(text, "backend", "exec"), "marker-unknown-kind")
    assert f and f[0].severity == "CRITICAL" and "BOGUS" in f[0].message


def test_malformed_atom_id_is_critical():
    g, ph, kind = _first_countable()
    text = marker(g.phase_kind, ph.key, START) + atom(kind, "not-an-id", "x") + marker(g.phase_kind, ph.key, END)
    assert [f.severity for f in _rules(parse(text, "backend", "exec"), "atom-id")] == ["CRITICAL"]


# ── (f) SUB qualification + exemption ───────────────────────────────────────

def test_bare_sub_in_exec_plan_is_rejected(mod):
    g, ph, kind = _first_countable()
    text = (marker(g.phase_kind, ph.key, START) + marker(g.sub_kind, "BARE", START, "  ")
            + atom(kind, CFG.make_id(g.atom_kinds[kind], mod, 1), "x") + marker(g.sub_kind, "BARE", END, "  ")
            + marker(g.phase_kind, ph.key, END))
    f = _rules(parse(text, "backend", "exec"), "sub-unqualified")
    assert f and f[0].severity == "CRITICAL" and ph.key in f[0].message


def test_bare_sub_allowed_in_exempt_test_plan(mod):
    res = parse(fx.test_plan(mod, over=True), "backend", "test")
    assert res.findings == []


def test_qualified_subs_pass_in_exec_plan(mod):
    res = parse(fx.exec_plan(mod), "backend", "exec")
    assert res.findings == []


# ── orphan atoms ─────────────────────────────────────────────────────────────

def test_orphan_atom_next_to_subs_is_major(mod):
    g, ph, kind = _first_countable()
    a1, a2 = (CFG.make_id(g.atom_kinds[kind], mod, i) for i in (1, 2))
    sid = f"{ph.key}-A"
    text = (marker(g.phase_kind, ph.key, START) + marker(g.sub_kind, sid, START, "  ") + atom(kind, a1, "a")
            + marker(g.sub_kind, sid, END, "  ") + atom(kind, a2, "orphan", indent="  ") + marker(g.phase_kind, ph.key, END))
    f = _rules(parse(text, "backend", "exec"), "atom-orphan")
    assert f and f[0].severity == "MAJOR" and a2 in f[0].message


def test_atoms_under_phase_without_subs_are_not_orphans(mod):
    res = parse(fx.test_plan(mod, over=False), "backend", "test")
    assert res.findings == []


# ── (g) thresholds: advisory vs strict ──────────────────────────────────────

def test_over_threshold_without_sub_is_minor_advisory(mod):
    text, ph = fx.over_threshold_no_sub(mod)
    res = parse(text, "backend", "exec")
    f = _rules(res, "split-threshold")
    assert f and f[0].severity == "MINOR" and ph.key in f[0].message
    assert res.blocking() == [] and res.blocking(strict=True) == []


def test_over_threshold_is_major_and_blocking_under_strict(mod):
    text, _ph = fx.over_threshold_no_sub(mod)
    res = parse(text, "backend", "exec", strict=True)
    assert [f.severity for f in _rules(res, "split-threshold")] == ["MAJOR"]
    assert res.blocking(strict=True)


def test_below_threshold_no_advisory(mod):
    res = parse(fx.below_threshold_no_sub(mod), "backend", "exec")
    assert _rules(res, "split-threshold") == []


def test_threshold_boundary_respects_op(mod):
    """`op: >` triggers only ABOVE count; `op: >=` triggers AT count."""
    for track, plan in (("backend", "test"), ("backend", "exec")):
        g = fx.grammar(track, plan)
        ph = fx.threshold_phase(g)
        kind, thr = fx.countable_kind(g, ph), ph.split_threshold
        n = int(thr["count"])
        body = "".join(atom(kind, CFG.make_id(g.atom_kinds[kind], mod, i), "x", indent="  ") for i in range(1, n + 1))
        res = parse(marker(g.phase_kind, ph.key, START) + body + marker(g.phase_kind, ph.key, END), track, plan)
        assert bool(_rules(res, "split-threshold")) == (thr.get("op") != ">")


def test_threshold_of_non_marker_kind_is_not_counted(mod):
    """A threshold whose kind is not a marker kind (e.g. screens) is skipped, never guessed."""
    g = fx.grammar("frontend", "exec")
    ph = next(p for p in g.phases if p.split_threshold and p.split_threshold["kind"] not in g.atom_kinds)
    res = parse(marker(g.phase_kind, ph.key, START) + "x\n" + marker(g.phase_kind, ph.key, END), "frontend", "exec")
    assert res.findings == []


# ── (h) never_split ──────────────────────────────────────────────────────────

def test_never_split_phase_with_sub_is_major():
    res = parse(fx.never_split_with_sub(), "backend", "exec")
    f = _rules(res, "never-split")
    assert f and f[0].severity == "MAJOR"
    assert res.blocking() == [] and res.blocking(strict=True)


# ── (i) traces attribute ─────────────────────────────────────────────────────

def test_traces_attribute_parsed_and_aggregated(mod):
    g, ph, kind = _first_countable()
    aid = CFG.make_id(g.atom_kinds[kind], mod, 1)
    t1, t2 = fx.trace_id(g, kind, mod, 1), fx.trace_id(g, kind, mod, 2)
    sid = f"{ph.key}-A"
    text = (marker(g.phase_kind, ph.key, START) + marker(g.sub_kind, sid, START, "  ")
            + atom(kind, aid, "x", traces=[t1, t2]) + marker(g.sub_kind, sid, END, "  ") + marker(g.phase_kind, ph.key, END))
    res = parse(text, "backend", "exec")
    assert res.findings == []
    a = next(b for b in res.blocks() if b.id == aid)
    assert a.traces == [t1, t2]
    sub = next(b for b in res.blocks() if b.id == sid)
    assert sub.traces == [] and sub.all_traces() == sorted([t1, t2])
    assert res.phases()[0].all_traces() == sorted([t1, t2])


def test_invalid_trace_id_and_unknown_attribute_are_major(mod):
    g, ph, kind = _first_countable()
    aid = CFG.make_id(g.atom_kinds[kind], mod, 1)
    attr = CFG.markers["attributes"][0]
    text = (marker(g.phase_kind, ph.key, START)
            + f"  <!-- {kind}:{aid}:START {attr}=bogus-id,{fx.trace_id(g, kind, mod)} colour=red -->\n  x\n  <!-- {kind}:{aid}:END -->\n"
            + marker(g.phase_kind, ph.key, END))
    res = parse(text, "backend", "exec")
    assert [f.severity for f in _rules(res, "marker-trace-id")] == ["MAJOR"]
    assert [f.severity for f in _rules(res, "marker-attribute")] == ["MAJOR"]
    assert res.blocking() == []


# ── content extraction ──────────────────────────────────────────────────────

def test_outside_phase_content_and_preamble_extracted(mod):
    res = parse(fx.exec_plan(mod, trailing=True), "backend", "exec")
    assert "Handoff Summary" in res.outside_phases()
    g = res.grammar
    ph = next(p for p in res.phases() if res.subs_of(p))
    assert res.preamble(ph).startswith("## ")
    assert g.sub_kind not in res.preamble(ph)


def test_rewrap_is_byte_identical_to_source(mod):
    text = fx.exec_plan(mod)
    res = parse(text, "backend", "exec")
    for b in res.blocks():
        assert text[b.open_off:b.end_off] == b.rewrap()
