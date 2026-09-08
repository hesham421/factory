"""
idmodel — one reading of IDs, records and traces shared by state / analyze / dispatch
=====================================================================================
Text conventions (shared/GOVERNANCE-CORE.md §3, MARKER-PROTOCOL.md):
  • an ID is DEFINED where it opens a line: optional heading marks / list bullet /
    bold, then the ID, then end-of-line, " —", " -", ":" or " (" ;
    or as a marker START (`<!-- KIND:ID:START … -->`).
  • a RECORD is the definition line plus every following line up to the next
    definition or a markdown heading of the same or higher level.
  • a record's TRACES are every ID on its `Traces`/`traces` line(s), every ID inside
    [brackets] on the definition line, and `traces=` marker attributes.
  • every other ID occurrence is a REFERENCE.
  • a QUESTION is a line containing `[QUESTION]` or an unresolved dialogue marker
    `<!-- OPEN -->`.
Everything about prefixes comes from CFG.id_atoms(); nothing is typed here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from config import CFG

_HEAD = re.compile(r"^(?P<lead>\s*(?:#{1,6}\s+)?(?:\*\*)?)(?P<id>ID)(?:\*\*)?(?P<rest>\s*(?:—|-|:|\(|$).*)$")   # a bullet `- ID` is a LISTING, never a definition
_TRACE_LINE = re.compile(r"^\s*[-*]?\s*\**traces?\**\s*:", re.I)
_QUESTION = re.compile(r"\[QUESTION\]|<!--\s*OPEN\s*-->")
_MARKER_START = re.compile(r"<!--\s*([A-Za-z][\w-]*):([\w-]+):START([^>]*)-->")
_ATTR = re.compile(r"(\w+)=([^\s]+)")
_HEADING = re.compile(r"^(#{1,6})\s")


@dataclass
class Record:
    id: str
    prefix: str
    mod: str
    seq: int
    line: int
    text: str = ""
    traces: list[str] = field(default_factory=list)
    level: int = 0                 # heading level of the definition (0 = not a heading)
    via_marker: bool = False       # defined by a marker START (an atom block) rather than a heading


def id_rx() -> re.Pattern:
    return CFG.id_regex()


def _def_rx() -> re.Pattern:
    core = id_rx().pattern
    return re.compile(_HEAD.pattern.replace("ID", core))


def split_id(s: str) -> tuple[str, str, int] | None:
    m = id_rx().fullmatch(s)
    if not m:
        return None
    return m.group("prefix"), m.group("mod"), int(m.group("seq"))


def find_ids(text: str) -> list[str]:
    return [m.group(0) for m in id_rx().finditer(text)]


def records(text: str) -> list[Record]:
    """Every ID definition in a text with its record body and traces."""
    lines = text.splitlines()
    drx = _def_rx()
    defs: list[tuple[int, str, int, bool]] = []       # (line index, id, heading level, via marker)
    for i, ln in enumerate(lines):
        m = drx.match(ln)
        if m:
            hm = _HEADING.match(ln)
            defs.append((i, m.group("id"), len(hm.group(1)) if hm else 0, False))
            continue
        for mm in _MARKER_START.finditer(ln):
            if id_rx().fullmatch(mm.group(2)):
                defs.append((i, mm.group(2), 0, True))
    out: list[Record] = []
    for n, (i, rid, level, via) in enumerate(defs):
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if any(d[0] == j for d in defs):
                end = j
                break
            hm = _HEADING.match(lines[j])
            if hm and level and len(hm.group(1)) <= level:
                end = j
                break
        body = "\n".join(lines[i:end])
        parts = split_id(rid)
        if not parts:
            continue
        pfx, mod, seq = parts
        rec = Record(rid, pfx, mod, seq, i + 1, body, [], level, via)
        # traces: Traces lines, bracket refs on the definition line, marker attrs
        for ln in body.splitlines():
            if _TRACE_LINE.match(ln):
                rec.traces += [x for x in find_ids(ln) if x != rid]
        for br in re.findall(r"\[([^\]]+)\]", lines[i]):
            rec.traces += [x for x in find_ids(br) if x != rid]
        for mm in _MARKER_START.finditer(lines[i]):
            for am in _ATTR.finditer(mm.group(3) or ""):
                rec.traces += [x for x in am.group(2).split(",") if id_rx().fullmatch(x)]
        rec.traces = list(dict.fromkeys(rec.traces))
        out.append(rec)
    return out


def defined_ids(text: str) -> set[str]:
    return {r.id for r in records(text)}


def marker_ids(text: str) -> set[str]:
    """IDs addressed by a marker START (atom blocks) — definitions OR references depending on ownership."""
    return {m.group(2) for m in _MARKER_START.finditer(text) if id_rx().fullmatch(m.group(2))}


def referenced_ids(text: str) -> set[str]:
    return set(find_ids(text))


def questions(text: str) -> list[int]:
    return [i + 1 for i, ln in enumerate(text.splitlines()) if _QUESTION.search(ln)]


def by_prefix(recs: list[Record], prefix: str) -> list[Record]:
    return [r for r in recs if r.prefix == prefix]
