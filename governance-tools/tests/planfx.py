"""
Profile-driven fixture builders — small but structurally faithful plans.

Nothing here spells a phase key, ID prefix or label: every name comes from
the active profile (via `toolkit.markers.Grammar`) and factory.yaml (`CFG`),
so the SAME builders produce a valid plan for any track / plan / profile.
Marker syntax follows factory.yaml → markers (html-comment).
"""
from __future__ import annotations

import itertools

from config import CFG
from toolkit.markers import Grammar

START, END = "START", "END"


def marker(kind: str, mid: str, action: str, indent: str = "", attrs: str = "") -> str:
    return f"{indent}<!-- {kind}:{mid}:{action}{(' ' + attrs) if attrs else ''} -->\n"


def atom(kind: str, aid: str, body: str, indent: str = "    ", traces: list[str] | None = None) -> str:
    attrs = f"traces={','.join(traces)}" if traces else ""
    return marker(kind, aid, START, indent, attrs) + f"{indent}{body}\n" + marker(kind, aid, END, indent)


def grammar(track: str, plan: str) -> Grammar:
    return Grammar(track, plan)


def trace_id(g: Grammar, atom_kind: str, mod: str, seq: int = 1) -> str:
    """An id of the first atom the marker kind `traces_to` (else any core atom)."""
    atoms = CFG.id_atoms()
    prefix = g.atom_kinds[atom_kind]
    targets = atoms.get(prefix, {}).get("traces_to") or [p for p in atoms if p not in g.atom_kinds.values()]
    return CFG.make_id(targets[0], mod, seq)


def countable_kind(g: Grammar, phase) -> str | None:
    """The marker kind a phase's split_threshold counts — if it IS a marker
    kind allowed in this (track, plan); otherwise None (not marker-countable)."""
    thr = phase.split_threshold
    if thr and thr.get("kind") in g.atom_kinds and not g.foreign(thr["kind"]):
        return thr["kind"]
    return None


def threshold_phase(g: Grammar):
    """First phase with a marker-countable split threshold (or None)."""
    return next((p for p in g.phases if countable_kind(g, p)), None)


def never_split_phase(g: Grammar):
    return next((p for p in g.phases if p.never_split), None)


def exec_plan(mod: str, track: str = "backend", plan: str = "exec", trailing: bool = True) -> str:
    """A well-formed exec plan for (track, plan) built ONLY from the profile:
      • never_split phases → one whole-phase block
      • phases with a marker-countable threshold → two phase-qualified SUBs,
        each holding one atom of the counted kind (with a traces= attribute)
      • sub_bearing phases → two phase-qualified SUBs of plain content
      • anything else → a plain phase block
      • optionally a trailing un-marked section (must be preserved, C4)
    """
    g = grammar(track, plan)
    P, S = g.phase_kind, g.sub_kind
    seq = itertools.count(1)
    out: list[str] = []
    for ph in g.phases:
        out.append(marker(P, ph.key, START))
        out.append(f"## {ph.display}\nPhase-level strategy for {ph.key}.\n")
        kind = countable_kind(g, ph)
        if kind:
            for label in (list(ph.sub_labels)[:2] or ["A", "B"]):
                sid = f"{ph.key}-{label}"
                out.append(marker(S, sid, START, "  "))
                out.append(f"  ### {label} group\n")
                aid = CFG.make_id(g.atom_kinds[kind], mod, next(seq))
                out.append(atom(kind, aid, f"Body of {aid}.", traces=[trace_id(g, kind, mod)]))
                out.append(marker(S, sid, END, "  "))
        elif ph.sub_bearing:
            for i in (1, 2):
                sid = f"{ph.key}-UNIT-{i:03d}"
                out.append(marker(S, sid, START, "  ") + f"  Unit {i} of {ph.key}.\n" + marker(S, sid, END, "  "))
        out.append(marker(P, ph.key, END))
        out.append("\n")
    if trailing:
        out.append("## Handoff Summary\nThis trailing section has no phase marker and must still be packaged.\n")
    return "".join(out)


def test_plan(mod: str, track: str = "backend", plan: str = "test", over: bool = True) -> str:
    """A test plan: `over=True` → atoms above the phase threshold, split into
    the profile's bare sub_labels; `over=False` → a few atoms flat under the phase."""
    g = grammar(track, plan)
    ph = g.phases[0]
    kind = countable_kind(g, ph)
    assert kind, "test plan phase must declare a marker-countable threshold"
    n = int(ph.split_threshold["count"]) + 1 if over else 3
    tcs = [atom(kind, CFG.make_id(g.atom_kinds[kind], mod, i), f"Given/When/Then {i}", traces=[trace_id(g, kind, mod, i)])
           for i in range(1, n + 1)]
    out = [marker(g.phase_kind, ph.key, START), f"## {ph.display}\n"]
    if over:
        labels = list(ph.sub_labels)[:2] or ["A", "B"]
        half = len(tcs) // 2
        for label, chunk in zip(labels, (tcs[:half], tcs[half:])):
            out.append(marker(g.sub_kind, label, START, "  ") + "".join(chunk) + marker(g.sub_kind, label, END, "  "))
    else:
        out += [t.replace("    ", "  ") for t in tcs]
    out.append(marker(g.phase_kind, ph.key, END))
    return "".join(out)


def over_threshold_no_sub(mod: str, track: str = "backend", plan: str = "exec") -> tuple[str, object]:
    """A threshold phase at its trigger count with NO SUB → advisory case."""
    g = grammar(track, plan)
    ph = threshold_phase(g)
    kind = countable_kind(g, ph)
    thr = ph.split_threshold
    n = int(thr["count"]) + (1 if thr.get("op") == ">" else 0)
    body = "".join(atom(kind, CFG.make_id(g.atom_kinds[kind], mod, i), f"x{i}", indent="  ") for i in range(1, n + 1))
    return marker(g.phase_kind, ph.key, START) + body + marker(g.phase_kind, ph.key, END), ph


def below_threshold_no_sub(mod: str, track: str = "backend", plan: str = "exec") -> str:
    g = grammar(track, plan)
    ph = threshold_phase(g)
    kind = countable_kind(g, ph)
    thr = ph.split_threshold
    n = int(thr["count"]) - (0 if thr.get("op") == ">" else 1)     # exactly one below the trigger
    body = "".join(atom(kind, CFG.make_id(g.atom_kinds[kind], mod, i), f"x{i}", indent="  ") for i in range(1, n + 1))
    return marker(g.phase_kind, ph.key, START) + body + marker(g.phase_kind, ph.key, END)


def never_split_with_sub(track: str = "backend", plan: str = "exec") -> str:
    g = grammar(track, plan)
    ph = never_split_phase(g)
    sid = f"{ph.key}-A"
    return (marker(g.phase_kind, ph.key, START) + marker(g.sub_kind, sid, START, "  ") + "  x\n"
            + marker(g.sub_kind, sid, END, "  ") + marker(g.phase_kind, ph.key, END))
