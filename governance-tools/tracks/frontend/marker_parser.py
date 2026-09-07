"""
ERP Governance Tools — Marker Parser Engine (Frontend)
========================================================
Shared parsing engine used by Agent 3.
Reads HTML comment markers (PROJECT-3-REGISTRY-2.md Section 5.7) and
builds a structured tree representing the artifact's addressable
elements.

This module does NOT modify any content — it only reads and indexes.

Frontend hierarchy: PHASE → [SUB] → [TC]
  frontend-execution-plan.md : PHASE + SUB only — no atomic markers at
    all (API-ID / XM-ID are backend-owned and referenced here as plain
    text, never re-marked; no TC markers appear in the execution plan).
    The addressable unit is the SUB (one screen per phase, e.g.
    SUB:F1-SCR-ORG-001) or, for a phase that never splits (SEC-FE /
    ALIGN-FE), the PHASE block itself.
  frontend-test-plan.md      : PHASE:TEST-PLAN-FE + optional
    SUB:UI-FLOWS / SUB:INT-FLOW + TC blocks. It is Playwright-only by
    construction, so the file itself is the tool boundary — there is no
    MARK level. TC blocks nest directly under PHASE or SUB.

The nesting hierarchy (ALLOWED_PARENTS) and the recognized marker
vocabulary (MARKERS) both live in config.py as the single source of
truth; this module imports them rather than keeping its own copy.

Foreign markers: any marker-shaped comment whose kind is NOT one of the
recognized frontend kinds (a backend-owned API/XM/MARK comment leaked
from a copied backend pattern, or a typo) is flagged as a structural
error — see _check_foreign_markers — rather than silently absorbed into
a block's content. This enforces the frontend/backend separation at the
parser level, generically, with no hardcoded backend marker names.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field

import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import MARKERS, ALLOWED_PARENTS, GENERIC_MARKER


@dataclass
class MarkerBlock:
    kind: str            # "phase" | "sub" | "tc"
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


def _tokenize(lines: list[str]) -> list[dict]:
    """Scan every line for recognized marker patterns, return ordered token list."""
    tokens = []
    for i, line in enumerate(lines, start=1):
        for kind, pattern in MARKERS.items():
            m = pattern.search(line)
            if m:
                marker_id, action = m.group(1), m.group(2)
                tokens.append({"kind": kind, "marker_id": marker_id, "type": action, "line": i})
    return tokens


def _check_foreign_markers(lines: list[str]) -> list[ParseError]:
    """
    Flag any marker-shaped comment whose KIND is not a recognized
    frontend marker kind. This catches an API / XM / MARK comment (or a
    misspelled kind) leaked from a backend pattern — a structural error
    in a frontend artifact — without this parser needing to know any
    specific backend marker name. Generic by construction: the allowed
    set is exactly MARKERS.keys().
    """
    recognized = set(MARKERS.keys())
    errors: list[ParseError] = []
    for i, line in enumerate(lines, start=1):
        for m in GENERIC_MARKER.finditer(line):
            kind = m.group(1).lower()
            if kind not in recognized:
                errors.append(ParseError(
                    severity="MAJOR",
                    message=(
                        f"Unrecognized marker kind '{m.group(1)}' at line {i}: "
                        f"<{m.group(1)}:{m.group(2)}:{m.group(3)}>. This frontend "
                        f"toolset recognizes only {sorted(recognized)} — API/XM/MARK "
                        f"are backend-owned and must never appear in a frontend "
                        f"artifact (referenced as plain text only). Fix the source."
                    ),
                    line=i,
                ))
    return errors


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
                        f"not permitted by PROJECT-3-REGISTRY-2.md Section 5.7.6 Rule 2."
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
                        f"(lines {lines}). Every marker_id must be unique within its kind. "
                        f"For F1-F4 SUB blocks this is almost always a missing phase-key "
                        f"prefix (SUB:SCR-X repeated across phases) — see agent3 --fix-safe.",
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
    errors += _check_foreign_markers(lines)

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
