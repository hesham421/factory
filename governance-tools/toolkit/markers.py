"""
toolkit.markers — the ONE marker parser, validator and safe auto-fixer
=======================================================================
Grammar    : factory.yaml → `markers` (syntax, kinds, allowed_parents,
             attributes, rules, autofix, schema_version)
Vocabulary : the active profile → `tracks.<track>.plans.<plan>.phases`
ID grammar : factory.yaml → `ids` (+ profile `ids.atoms`) via `CFG.id_regex()`

Marker syntax (markers.syntax = html-comment):
    <!-- KIND:ID:START [key=value …] -->  …  <!-- KIND:ID:END -->
A line may carry several markers; every one is tokenised, ordered by column.

Hierarchy (from `kinds.*.allowed_parents`): the kind with `keys_from` is the
PHASE level, the kind with `qualified_by_phase` is the SUB level, kinds with
`atom` are atoms. Nothing in this module spells a kind, key or prefix (C1/C2).

Public API
----------
    parse(text, track, plan, *, strict=False)  -> ParseResult
    validate(path, track, plan, *, strict=False) -> ParseResult
    safe_autofix(path, track, plan)             -> AutofixReport
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from config import CFG, Phase

from .common import CRITICAL, MAJOR, MINOR

_ACTION_START, _ACTION_END = "START", "END"
_SYNTAX_HTML_COMMENT = "html-comment"
_MAX_AUTOFIX_PASSES = 50


# ── data types ───────────────────────────────────────────────────────────────

@dataclass
class Finding:
    severity: str          # CRITICAL | MAJOR | MINOR
    rule: str
    message: str
    line: int = 0

    def __str__(self) -> str:
        return f"[{self.severity}] {self.rule} line {self.line} — {self.message}"


@dataclass
class Block:
    """One START…END pair. `content` is EXACTLY the text between the two
    markers (so a block can be re-emitted byte-identically)."""
    kind: str
    id: str
    start_line: int
    end_line: int = 0
    content: str = ""
    attrs: dict[str, list[str]] = field(default_factory=dict)
    children: list["Block"] = field(default_factory=list)
    parent: "Block | None" = field(default=None, repr=False, compare=False)
    open_off: int = 0          # offset of the START marker
    content_off: int = 0       # offset just after the START marker
    close_off: int = 0         # offset of the END marker
    end_off: int = 0           # offset just after the END marker
    open_text: str = ""        # the START marker verbatim
    close_text: str = ""       # the END marker verbatim

    @property
    def traces(self) -> list[str]:
        """IDs this block traces to (union of every declared attribute)."""
        out: list[str] = []
        for vals in self.attrs.values():
            out.extend(v for v in vals if v not in out)
        return out

    def all_traces(self) -> list[str]:
        seen: list[str] = []
        for b in self.walk():
            seen.extend(t for t in b.traces if t not in seen)
        return sorted(seen)

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def sha256(self) -> str:
        return hashlib.sha256(self.content.strip().encode("utf-8")).hexdigest()

    def rewrap(self) -> str:
        """The block re-emitted with its own markers — byte-identical source."""
        return self.open_text + self.content + self.close_text


@dataclass
class ParseResult:
    text: str
    track: str
    plan: str
    grammar: "Grammar"
    roots: list[Block] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def blocks(self) -> list[Block]:
        return [b for r in self.roots for b in r.walk()]

    def by_kind(self, kind: str) -> list[Block]:
        return [b for b in self.blocks() if b.kind == kind]

    def phases(self) -> list[Block]:
        return [b for b in self.roots if self.grammar.is_phase(b.kind)]

    def atoms(self) -> list[Block]:
        return [b for b in self.blocks() if self.grammar.is_atom(b.kind)]

    def subs_of(self, phase: Block) -> list[Block]:
        return [c for c in phase.children if self.grammar.is_sub(c.kind)]

    def blocking(self, strict: bool = False) -> list[Finding]:
        """CRITICAL findings block always; MAJOR ones block under --strict."""
        levels = {CRITICAL, MAJOR} if strict else {CRITICAL}
        return [f for f in self.findings if f.severity in levels]

    def outside_phases(self) -> str:
        """Every character that lies outside all top-level blocks — leading,
        between-phase and trailing sections that carry no marker (kept, C4)."""
        parts, pos = [], 0
        for r in sorted(self.roots, key=lambda b: b.open_off):
            parts.append(self.text[pos:r.open_off])
            pos = max(pos, r.end_off)
        parts.append(self.text[pos:])
        return "".join(parts).strip()

    def preamble(self, phase: Block) -> str:
        """Phase content before its first SUB (the phase-level header)."""
        subs = self.subs_of(phase)
        if not subs:
            return ""
        return self.text[phase.content_off:subs[0].open_off].strip()


@dataclass
class AutofixReport:
    path: Path
    changed: bool = False
    backup: Path | None = None
    phase_key_fixes: list[dict] = field(default_factory=list)
    sub_qualification_fixes: list[dict] = field(default_factory=list)
    remaining: list[Finding] = field(default_factory=list)


# ── grammar (built from CFG on every call — never cached across reloads) ─────

class Grammar:
    def __init__(self, track: str, plan: str):
        m = CFG.markers
        if m.get("syntax") != _SYNTAX_HTML_COMMENT:
            raise NotImplementedError(f"markers.syntax {m.get('syntax')!r} is not supported")
        self.track, self.plan = track, plan
        self.kinds: dict[str, dict] = dict(m["kinds"])
        self.rules: dict = m.get("rules") or {}
        self.autofix: dict = m.get("autofix") or {}
        self.attributes: list[str] = list(m.get("attributes") or [])
        self.phase_kind = next(k for k, v in self.kinds.items() if "keys_from" in v)
        self.sub_kind = next((k for k, v in self.kinds.items() if v.get("qualified_by_phase")), None)
        self.atom_kinds: dict[str, str] = {k: v["atom"] for k, v in self.kinds.items() if v.get("atom")}
        self.allowed_parents = {k: set(v.get("allowed_parents") or []) for k, v in self.kinds.items()}
        self.phases: list[Phase] = CFG.profile.phases(track, plan)
        self.phase_by_key = {p.key: p for p in self.phases}
        self.sub_exempt = plan in (self.rules.get("sub_unqualified_exempt_plans") or [])
        self.id_rx = CFG.id_regex()
        self.atom_rx = {k: CFG.id_regex(a) for k, a in self.atom_kinds.items()}
        self.marker_rx = re.compile(
            r"<!--\s*(?P<kind>[A-Za-z][\w-]*):(?P<id>[^:<>]+?):(?P<action>"
            + _ACTION_START + "|" + _ACTION_END + r")(?P<attrs>(?:\s+[^\s>]+)*)\s*-->")

    def is_phase(self, kind: str) -> bool: return kind == self.phase_kind
    def is_sub(self, kind: str) -> bool:   return kind == self.sub_kind
    def is_atom(self, kind: str) -> bool:  return kind in self.atom_kinds

    def foreign(self, kind: str) -> str | None:
        """Why this kind may not appear in this (track, plan), or None."""
        spec = self.kinds[kind]
        if "tracks" in spec and self.track not in spec["tracks"]:
            return f"kind {kind} is restricted to tracks {spec['tracks']}"
        if "plans" in spec and self.plan not in spec["plans"]:
            return f"kind {kind} is restricted to plans {spec['plans']}"
        return None

    def normalise_key(self, key: str) -> str:
        n = re.sub(r"[+_\s]", "-", key.strip()).upper()
        return re.sub(r"-{2,}", "-", n).strip("-")

    def canonical_for(self, key: str) -> str | None:
        """The ONE canonical phase key `key` normalises to, else None."""
        hits = [p.key for p in self.phases if self.normalise_key(p.key) == self.normalise_key(key)]
        return hits[0] if len(hits) == 1 else None


# ── tokeniser + tree ─────────────────────────────────────────────────────────

@dataclass
class _Token:
    kind: str
    id: str
    action: str
    attrs: str
    line: int
    start: int
    end: int


def _tokenize(text: str, g: Grammar) -> list[_Token]:
    tokens, off = [], 0
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        hits = [(m.start(), m) for m in g.marker_rx.finditer(line)]
        for col, m in sorted(hits, key=lambda h: h[0]):
            tokens.append(_Token(m.group("kind"), m.group("id").strip(), m.group("action"),
                                 m.group("attrs").strip(), n, off + col, off + m.end()))
        off += len(line)
    return tokens


def _parse_attrs(tok: _Token, g: Grammar, out: list[Finding]) -> dict[str, list[str]]:
    attrs: dict[str, list[str]] = {}
    for item in tok.attrs.split():
        key, _, value = item.partition("=")
        if key not in g.attributes:
            out.append(Finding(MAJOR, "marker-attribute", f"unknown attribute {key!r} on {tok.kind}:{tok.id} (allowed: {g.attributes})", tok.line))
            continue
        ids = [v for v in value.split(",") if v]
        for v in ids:
            if not g.id_rx.fullmatch(v):
                out.append(Finding(MAJOR, "marker-trace-id", f"{tok.kind}:{tok.id} {key}= carries an invalid id {v!r}", tok.line))
        attrs.setdefault(key, []).extend(ids)
    return attrs


def _build_tree(text: str, tokens: list[_Token], g: Grammar, check_nesting: bool = True) -> tuple[list[Block], list[Finding]]:
    """Single pass: START opens a block under the current parent, END closes
    the innermost open block. Unknown / foreign kinds never enter the tree."""
    findings: list[Finding] = []
    stack: list[Block] = []
    roots: list[Block] = []
    for t in tokens:
        if t.kind not in g.kinds:
            findings.append(Finding(CRITICAL, "marker-unknown-kind", f"unknown marker kind {t.kind!r} ({t.kind}:{t.id}:{t.action})", t.line))
            continue
        why = g.foreign(t.kind)
        if why:
            findings.append(Finding(CRITICAL, "marker-foreign-kind", f"{t.kind}:{t.id} does not belong in a {g.track}/{g.plan} plan — {why}", t.line))
            continue
        if t.action == _ACTION_START:
            parent = stack[-1] if stack else None
            if check_nesting and (parent.kind if parent else None) not in (g.allowed_parents[t.kind] or {None}):
                findings.append(Finding(CRITICAL, "marker-nesting", f"{t.kind}:{t.id} may not open inside {parent.kind + ':' + parent.id if parent else 'the document root'} (allowed parents: {sorted(g.allowed_parents[t.kind]) or 'root'})", t.line))
            if g.is_atom(t.kind) and not g.atom_rx[t.kind].fullmatch(t.id):
                findings.append(Finding(CRITICAL, "atom-id", f"{t.kind}:{t.id} is not a well-formed {g.atom_kinds[t.kind]} id ({CFG.ids['pattern']})", t.line))
            b = Block(kind=t.kind, id=t.id, start_line=t.line, attrs=_parse_attrs(t, g, findings),
                      open_off=t.start, content_off=t.end, open_text=text[t.start:t.end], parent=parent)
            (parent.children if parent else roots).append(b)
            stack.append(b)
            continue
        if not stack:
            findings.append(Finding(CRITICAL, "marker-unmatched-end", f"{t.kind}:{t.id}:{_ACTION_END} has no open {_ACTION_START}", t.line))
            continue
        top = stack[-1]
        if (top.kind, top.id) != (t.kind, t.id):
            findings.append(Finding(CRITICAL, "marker-mismatched-end", f"expected {top.kind}:{top.id}:{_ACTION_END} (opened line {top.start_line}) but found {t.kind}:{t.id}:{_ACTION_END}", t.line))
            continue
        top.end_line, top.close_off, top.end_off = t.line, t.start, t.end
        top.content, top.close_text = text[top.content_off:t.start], text[t.start:t.end]
        stack.pop()
    for b in stack:
        findings.append(Finding(CRITICAL, "marker-unclosed", f"{b.kind}:{b.id}:{_ACTION_START} (line {b.start_line}) has no {_ACTION_END}", b.start_line))
    return roots, findings


def _check_uniqueness(roots: list[Block]) -> list[Finding]:
    seen: dict[tuple[str, str], list[Block]] = {}
    for r in roots:
        for b in r.walk():
            seen.setdefault((b.kind, b.id), []).append(b)
    return [Finding(CRITICAL, "marker-duplicate", f"{k}:{i} appears {len(bs)} times (lines {', '.join(str(b.start_line) for b in bs)})", bs[0].start_line)
            for (k, i), bs in seen.items() if len(bs) > 1]


# ── semantic checks (profile-driven) ─────────────────────────────────────────

def _check_semantics(res: ParseResult, strict: bool) -> list[Finding]:
    g, out = res.grammar, []
    adv = MAJOR if strict else MINOR
    for ph in res.phases():
        spec = g.phase_by_key.get(ph.id)
        if spec is None:
            out.append(Finding(CRITICAL, "phase-unknown", f"{ph.kind}:{ph.id} is not a phase of {g.track}/{g.plan} (canonical: {', '.join(g.phase_by_key)}) — refusing (rules.unknown_phase)", ph.start_line))
            continue
        subs = res.subs_of(ph)
        if not g.sub_exempt:
            for s in subs:
                if not s.id.startswith(ph.id + "-"):
                    out.append(Finding(CRITICAL, "sub-unqualified", f"{s.kind}:{s.id} must be phase-qualified as {ph.id}-<LABEL>", s.start_line))
        if subs:
            for c in ph.children:
                if g.is_atom(c.kind):
                    out.append(Finding(MAJOR, "atom-orphan", f"{c.kind}:{c.id} sits directly under {ph.kind}:{ph.id} which also has {g.sub_kind} blocks — it would reach no package file", c.start_line))
        if spec.never_split and subs:
            out.append(Finding(MAJOR, "never-split", f"{ph.kind}:{ph.id} is never_split but carries {len(subs)} {g.sub_kind} block(s)", ph.start_line))
        thr = spec.split_threshold
        if thr and not subs and thr.get("kind") in g.kinds:
            count = sum(1 for b in ph.walk() if b.kind == thr["kind"])
            over = count > int(thr["count"]) if thr.get("op") == ">" else count >= int(thr["count"])
            if over:
                out.append(Finding(adv, "split-threshold", f"{ph.kind}:{ph.id} has {count} {thr['kind']} block(s) ({thr.get('op', '>=')} {thr['count']}) but no {g.sub_kind} blocks — expected split{(' by ' + str(thr['grouping'])) if thr.get('grouping') else ''}", ph.start_line))
    return out


# ── public API ───────────────────────────────────────────────────────────────

def parse(text: str, track: str, plan: str, *, strict: bool = False) -> ParseResult:
    """Tokenise → tree → uniqueness → semantics. Never raises on bad input;
    everything is a Finding. `strict` escalates threshold advisories to MAJOR."""
    g = Grammar(track, plan)
    roots, findings = _build_tree(text, _tokenize(text, g), g)
    res = ParseResult(text=text, track=track, plan=plan, grammar=g, roots=roots, findings=findings)
    res.findings += _check_uniqueness(roots)
    res.findings += _check_semantics(res, strict)
    return res


def parse_structure(text: str, track: str, plan: str) -> ParseResult:
    """Tree only, no nesting/semantic rules — used to look blocks up inside
    package files, where a SUB or PHASE legitimately sits at the root."""
    g = Grammar(track, plan)
    roots, findings = _build_tree(text, _tokenize(text, g), g, check_nesting=False)
    return ParseResult(text=text, track=track, plan=plan, grammar=g, roots=roots, findings=findings)


def validate(path: Path, track: str, plan: str, *, strict: bool = False) -> ParseResult:
    return parse(Path(path).read_text(encoding="utf-8"), track, plan, strict=strict)


def _rename_marker(lines: list[str], block: Block, new_id: str) -> None:
    for ln in (block.start_line, block.end_line):
        if ln:
            lines[ln - 1] = lines[ln - 1].replace(f"{block.kind}:{block.id}:", f"{block.kind}:{new_id}:", 1)


def _one_safe_fix(res: ParseResult, lines: list[str], rep: AutofixReport) -> bool:
    """Apply at most ONE mechanical fix; True when something changed."""
    g = res.grammar
    if g.autofix.get("phase_key_normalise"):
        for ph in res.phases():
            canon = g.canonical_for(ph.id) if ph.id not in g.phase_by_key else None
            if canon:
                _rename_marker(lines, ph, canon)
                rep.phase_key_fixes.append({"from": ph.id, "to": canon, "line": ph.start_line})
                return True
    if g.autofix.get("qualify_bare_sub") and not g.sub_exempt:
        for ph in res.phases():
            if ph.id not in g.phase_by_key:
                continue
            for s in res.subs_of(ph):
                if not s.id.startswith(ph.id + "-"):
                    _rename_marker(lines, s, f"{ph.id}-{s.id}")
                    rep.sub_qualification_fixes.append({"from": s.id, "to": f"{ph.id}-{s.id}", "line": s.start_line})
                    return True
    return False


def safe_autofix(path: Path, track: str, plan: str) -> AutofixReport:
    """Deterministic, reversible repairs only (markers.autofix):
    phase-key normalisation when it maps to exactly ONE canonical key, and
    bare SUB → phase-qualified SUB (unless the plan is exempt). Never touches
    content, never guesses. Original kept as <file>.orig on first change."""
    path = Path(path)
    rep = AutofixReport(path=path)
    original = path.read_bytes()
    for _ in range(_MAX_AUTOFIX_PASSES):
        res = validate(path, track, plan)
        lines = res.text.splitlines(keepends=True)
        if not _one_safe_fix(res, lines, rep):
            break
        path.write_text("".join(lines), encoding="utf-8")
    if rep.phase_key_fixes or rep.sub_qualification_fixes:
        rep.changed = True
        rep.backup = path.with_name(path.name + ".orig")
        if not rep.backup.exists():
            rep.backup.write_bytes(original)
    rep.remaining = validate(path, track, plan).findings
    return rep
