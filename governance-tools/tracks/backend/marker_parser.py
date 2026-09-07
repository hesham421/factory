"""
ERP Governance Tools — Marker Parser Engine
=============================================
Shared parsing engine used by Agent 3.
Reads HTML comment markers (PROJECT-3-REGISTRY.md Section 5.7) and
builds a structured tree representing the artifact's addressable
elements.

This module does NOT modify any content — it only reads and indexes.

Hierarchy: PHASE → [SUB] → ATOM (API/XM/TC) — the same shape for every
artifact type (backend-execution-plan.md, frontend-execution-plan.md,
backend-test-plan.md, frontend-test-plan.md). There is no MARK level —
each test-plan file is single-tool by construction (backend-test-plan.md
is JUnit-only, frontend-test-plan.md is Playwright-only), so the file
itself is the tool boundary; TC blocks nest directly under PHASE or SUB.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field

import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    MARKERS,
    ALLOWED_PARENTS,          # single source of truth — no local copy here
    CANONICAL_PHASE_KEYS,
    SUB_QUALIFICATION_EXEMPT,
    PHASE_SPLIT_THRESHOLDS,
    NEVER_SPLIT_PHASES,
    classify_artifact,
)


@dataclass
class MarkerBlock:
    kind: str            # "phase" | "sub" | "api" | "xm" | "tc"
    marker_id: str
    start_line: int       # 1-indexed line number of the START marker
    end_line: int = 0     # 1-indexed line number of the END marker
    content: str = ""     # raw text between START and END (exclusive of marker lines)
    children: list = field(default_factory=list)
    parent: "MarkerBlock" = None


@dataclass
class ParseError:
    severity: str          # "CRITICAL" | "MAJOR" | "MINOR"
    message: str
    line: int = 0


@dataclass
class ParseResult:
    root_blocks: list[MarkerBlock]
    errors: list[ParseError]
    raw_lines: list[str]
    total_lines: int


# Nesting hierarchy (PROJECT-3-REGISTRY.md Section 5.7.2/5.7.6) is imported
# from config.ALLOWED_PARENTS above — kept in ONE place so the parser and any
# other consumer can never drift apart. (Previously this file held a second,
# independent copy — a latent drift hazard removed under this amendment.)


def _tokenize(lines: list[str]) -> list[dict]:
    """Scan every line for marker patterns, return ordered token list.

    A single line may legitimately contain more than one marker (e.g. a
    compact inline atomic block `<!-- TC:..:START -->...<!-- TC:..:END -->`,
    or a SUB:END immediately followed by the next SUB:START). Every marker on
    the line is captured, ordered by column position, so none is silently
    missed. (The previous version used pattern.search and kept only the FIRST
    match per pattern per line — a latent bug that dropped any second marker on
    a shared line.)
    """
    tokens = []
    for i, line in enumerate(lines, start=1):
        line_hits = []
        for kind, pattern in MARKERS.items():
            for m in pattern.finditer(line):
                line_hits.append((m.start(), kind, m.group(1), m.group(2)))
        line_hits.sort(key=lambda h: h[0])  # preserve left-to-right order
        for _col, kind, marker_id, action in line_hits:
            tokens.append({"kind": kind, "marker_id": marker_id, "type": action, "line": i})
    return tokens


def _build_tree(tokens: list[dict], lines: list[str]) -> tuple[list[MarkerBlock], list[ParseError]]:
    """
    Single-pass tree builder.
    Opens a block at START (attaches to current parent immediately),
    fills in content + end_line at matching END.
    """
    errors: list[ParseError] = []
    stack: list[MarkerBlock] = []   # currently open blocks
    roots: list[MarkerBlock] = []

    for tok in tokens:
        kind, marker_id, action, line = tok["kind"], tok["marker_id"], tok["type"], tok["line"]

        if action == "START":
            parent_kind = stack[-1].kind if stack else None
            allowed = ALLOWED_PARENTS.get(kind, [])
            if parent_kind not in allowed:
                errors.append(ParseError(
                    severity="CRITICAL",
                    message=(
                        f"Illegal nesting: <{kind.upper()}:{marker_id}:START> at line {line} "
                        f"found inside '{parent_kind or 'document root'}' — "
                        f"not permitted by PROJECT-3-REGISTRY.md Section 5.7.6 Rule 2."
                    ),
                    line=line,
                ))

            block = MarkerBlock(kind=kind, marker_id=marker_id, start_line=line)
            if stack:
                stack[-1].children.append(block)
                block.parent = stack[-1]
            else:
                roots.append(block)
            stack.append(block)

        elif action == "END":
            if not stack:
                errors.append(ParseError(
                    severity="CRITICAL",
                    message=f"Unmatched END marker: <{kind.upper()}:{marker_id}:END> at line {line} "
                            f"— no corresponding START marker is open.",
                    line=line,
                ))
                continue

            open_block = stack[-1]
            if open_block.kind != kind or open_block.marker_id != marker_id:
                errors.append(ParseError(
                    severity="CRITICAL",
                    message=(
                        f"Mismatched END marker at line {line}: expected "
                        f"</{open_block.kind.upper()}:{open_block.marker_id}> but found "
                        f"</{kind.upper()}:{marker_id}>."
                    ),
                    line=line,
                ))
                continue

            open_block.end_line = line
            content_lines = lines[open_block.start_line: line - 1]
            open_block.content = "".join(content_lines)
            stack.pop()

    for unclosed in stack:
        errors.append(ParseError(
            severity="CRITICAL",
            message=f"Unclosed marker: <{unclosed.kind.upper()}:{unclosed.marker_id}:START> "
                    f"at line {unclosed.start_line} — no matching END marker found.",
            line=unclosed.start_line,
        ))

    return roots, errors


def _check_uniqueness(roots: list[MarkerBlock]) -> list[ParseError]:
    """Every marker_id within the same kind must be unique across the whole document."""
    errors = []
    seen: dict[str, list[MarkerBlock]] = {}

    def _walk(block: MarkerBlock):
        key = f"{block.kind}:{block.marker_id}"
        seen.setdefault(key, []).append(block)
        for child in block.children:
            _walk(child)

    for root in roots:
        _walk(root)

    for key, blocks in seen.items():
        if len(blocks) > 1:
            kind, marker_id = key.split(":", 1)
            lines = ", ".join(str(b.start_line) for b in blocks)
            errors.append(ParseError(
                severity="CRITICAL",
                message=f"Duplicate {kind.upper()}:{marker_id} — appears {len(blocks)} times "
                        f"(lines {lines}). Every marker_id must be unique within its kind.",
                line=blocks[0].start_line,
            ))

    return errors


def parse_file(filepath: Path) -> ParseResult:
    """
    Parse a markdown artifact file and return its marker tree.
    Does not raise on structural errors — collects them in result.errors.
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    tokens = _tokenize(lines)
    roots, errors = _build_tree(tokens, lines)
    errors += _check_uniqueness(roots)

    return ParseResult(
        root_blocks=roots,
        errors=errors,
        raw_lines=lines,
        total_lines=len(lines),
    )


def flatten(blocks: list[MarkerBlock]) -> list[MarkerBlock]:
    """Return every block in the tree (depth-first), including nested children."""
    result = []
    for b in blocks:
        result.append(b)
        result.extend(flatten(b.children))
    return result


def find_by_kind(blocks: list[MarkerBlock], kind: str) -> list[MarkerBlock]:
    """Return every block of a given kind, anywhere in the tree."""
    return [b for b in flatten(blocks) if b.kind == kind]


# ─────────────────────────────────────────────────────────────────────────────
# SEMANTIC VALIDATION — layered ON TOP of structural parsing.
#
# parse_file() already catches STRUCTURAL faults (unmatched/unclosed markers,
# illegal nesting, duplicate IDs). The checks below catch SEMANTIC faults that
# are structurally legal but violate the governance contract and would
# otherwise cause SILENT DATA LOSS during splitting:
#
#   • a non-canonical PHASE key (e.g. "SVC+API" instead of "SVC-API") — would
#     be silently skipped by Agent 3 Stage 2, dropping a whole phase.
#   • a SUB label that is not phase-qualified (AMEND-P3-N) — collides across
#     phases and/or produces mis-named package files.
#   • an atomic marker (API/XM/TC) sitting directly under a PHASE that also
#     has SUB children ("orphan") — Agent 3 writes SUBs only, so the orphan
#     would never reach any package file.
#
# All are returned as ParseError so callers can treat them exactly like
# structural errors: blocking, with a line number and a clear message.
# ─────────────────────────────────────────────────────────────────────────────

def check_canonical_phase_keys(roots: list[MarkerBlock], allowed_keys: list[str]) -> list[ParseError]:
    """Every top-level PHASE marker_id must be one of allowed_keys."""
    errors: list[ParseError] = []
    allowed = set(allowed_keys)
    for block in roots:
        if block.kind != "phase":
            continue
        if block.marker_id not in allowed:
            errors.append(ParseError(
                severity="CRITICAL",
                message=(
                    f"Non-canonical PHASE key '{block.marker_id}' at line {block.start_line} "
                    f"— not one of the canonical keys for this file "
                    f"({', '.join(sorted(allowed))}). A typo here (e.g. '+' instead of '-') "
                    f"would be silently skipped by the splitter, dropping the whole phase."
                ),
                line=block.start_line,
            ))
    return errors


def check_sub_qualification(roots: list[MarkerBlock], exempt: bool) -> list[ParseError]:
    """Every SUB label must be phase-qualified as {PARENT-PHASE-KEY}-{LABEL}
    (AMEND-P3-N), unless the file is exempt (test-plans — single phase)."""
    if exempt:
        return []
    errors: list[ParseError] = []
    for phase in roots:
        if phase.kind != "phase":
            continue
        prefix = f"{phase.marker_id}-"
        for child in phase.children:
            if child.kind != "sub":
                continue
            if not child.marker_id.startswith(prefix):
                errors.append(ParseError(
                    severity="CRITICAL",
                    message=(
                        f"SUB '{child.marker_id}' at line {child.start_line} is not "
                        f"phase-qualified — it must start with '{prefix}' "
                        f"(SUB:{phase.marker_id}-{{LABEL}}), per PROJECT-3-REGISTRY.md "
                        f"Section 5.7.4 (AMEND-P3-N). Bare SUB labels collide across "
                        f"phases and mis-name package files."
                    ),
                    line=child.start_line,
                ))
    return errors


def check_orphan_atomics(roots: list[MarkerBlock]) -> list[ParseError]:
    """An atomic (api/xm/tc) that is a DIRECT child of a PHASE which also has
    SUB children is an orphan: Agent 3 writes SUB blocks (or the whole phase
    when there are no SUBs), so a mixed phase would drop its direct atomics."""
    errors: list[ParseError] = []
    for phase in roots:
        if phase.kind != "phase":
            continue
        has_sub = any(c.kind == "sub" for c in phase.children)
        if not has_sub:
            continue  # no-SUB phase: atomics directly under PHASE are valid
        for child in phase.children:
            if child.kind in ("api", "xm", "tc"):
                errors.append(ParseError(
                    severity="MAJOR",
                    message=(
                        f"Orphan {child.kind.upper()}:{child.marker_id} at line "
                        f"{child.start_line} — sits directly under PHASE:{phase.marker_id} "
                        f"which also has SUB blocks. When a phase is split into SUBs, "
                        f"every atomic must live inside a SUB, or it will not be written "
                        f"to any package file."
                    ),
                    line=child.start_line,
                ))
    return errors


def check_split_thresholds(roots: list[MarkerBlock], strict: bool = False) -> list[ParseError]:
    """AUTO-verify the split thresholds (config.PHASE_SPLIT_THRESHOLDS) that are
    countable from markers.

    Flexible by design:
      • A phase at/above its trigger count with NO SUB blocks is reported.
      • A NEVER_SPLIT phase that DOES carry SUB blocks is reported.
      • Severity is MINOR (advisory — callers treat it as a non-blocking
        warning) unless strict=True, which escalates to MAJOR (blocking).

    Only markers can be counted, so phases whose trigger is not a marker kind
    (e.g. DATA-DOM entities) are simply not in PHASE_SPLIT_THRESHOLDS and are
    skipped here — never guessed at.
    """
    sev = "MAJOR" if strict else "MINOR"
    errors: list[ParseError] = []
    for phase in roots:
        if phase.kind != "phase":
            continue
        has_sub = any(c.kind == "sub" for c in phase.children)

        rule = PHASE_SPLIT_THRESHOLDS.get(phase.marker_id)
        if rule and not has_sub:
            count = len([b for b in flatten([phase]) if b.kind == rule["kind"]])
            triggered = count > rule["count"] if rule["op"] == ">" else count >= rule["count"]
            if triggered:
                errors.append(ParseError(
                    severity=sev,
                    message=(
                        f"PHASE:{phase.marker_id} has {count} {rule['kind'].upper()} "
                        f"block(s) ({rule['op']} {rule['count']} → over the split "
                        f"threshold) but no SUB blocks. Section 5.7.4 expects it split "
                        f"into {rule['grouping']}. "
                        + ("Blocking (--strict-thresholds)." if strict else
                           "Advisory — verify this was an intentional semantic choice.")
                    ),
                    line=phase.start_line,
                ))

        if phase.marker_id in NEVER_SPLIT_PHASES and has_sub:
            errors.append(ParseError(
                severity=sev,
                message=(
                    f"PHASE:{phase.marker_id} carries SUB blocks but is a "
                    f"never-split phase (Section 5.7.4). "
                    + ("Blocking (--strict-thresholds)." if strict else
                       "Advisory — verify this was intentional.")
                ),
                line=phase.start_line,
            ))
    return errors


def validate_semantics(filepath, result: ParseResult, strict_thresholds: bool = False):
    """Run all semantic checks appropriate to the file's identity.

    Returns a tuple (blocking, advisories):
      • blocking    — always-blocking semantic errors (non-canonical phase key,
                      un-qualified SUB, orphan atomic).
      • advisories  — split-threshold findings. These are NON-blocking warnings
                      by default; when strict_thresholds=True they are emitted at
                      MAJOR severity and the caller should treat them as blocking.

    File identity is inferred from the basename. If unrecognised, the
    file-specific checks are skipped but the file-agnostic ones still run.
    """
    artifact = classify_artifact(str(filepath))
    blocking: list[ParseError] = []
    if artifact:
        blocking += check_canonical_phase_keys(result.root_blocks, CANONICAL_PHASE_KEYS[artifact])
        blocking += check_sub_qualification(result.root_blocks, exempt=artifact in SUB_QUALIFICATION_EXEMPT)
    blocking += check_orphan_atomics(result.root_blocks)

    advisories = check_split_thresholds(result.root_blocks, strict=strict_thresholds)
    return blocking, advisories
