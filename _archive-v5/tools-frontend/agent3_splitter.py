"""
ERP Governance Tools — Agent 3: Frontend Artifact Splitter
============================================================
Reads the Marker Protocol (PROJECT-3-REGISTRY-2.md Section 5.7) from
frontend-execution-plan.md and frontend-test-plan.md, then splits them
into addressable package files.

Usage:
    python agent3_splitter.py --module MODCODE
    python agent3_splitter.py --module MODCODE --stage 1
    python agent3_splitter.py --module MODCODE --resume
    python agent3_splitter.py --module MODCODE --status
    python agent3_splitter.py --module MODCODE --strict-thresholds
    python agent3_splitter.py --module MODCODE --fix-safe [--dry-run]
    python agent3_splitter.py --validate-markers --file PATH

This tool has no representation of "backend" anywhere, and no
--track flag — it does exactly one job: split frontend-execution-plan.md
and frontend-test-plan.md. There is no P4/audit concept anywhere.

Frontend element model (differs from backend by design):
    frontend-execution-plan.md carries NO atomic (API/XM/TC) markers —
    its addressable unit is the SUB (one screen, e.g. SUB:F1-SCR-ORG-001)
    or, for a phase that never splits (SEC-FE / ALIGN-FE), the PHASE
    block itself. frontend-test-plan.md carries TC markers (optionally
    grouped under SUB:UI-FLOWS / SUB:INT-FLOW). Stage 5 verifies exactly
    these units — not backend API/XM atoms.

Self-describing package files: every block written by Stage 2/3 is
wrapped back in its own START/END marker, so each package file is an
independently parseable artifact and Stage 5 can content-hash it back
against the source by marker lookup. (The preamble/HEADER file is not a
marker block and is written as-is.)

Stages:
    1. Parse & Plan          — read markers, validate structure, show plan
    2. Split execution-plan  — write one file per SUB (or per no-SUB PHASE)
    3. Split test-plan        — write PHASE/SUB/TC package files (no MARK
                                level — this file is Playwright-only)
    4. Generate Index Files  — index.md per package folder
    5. Verify Completeness   — content-hash cross-check of every SUB /
                                no-SUB PHASE (exec) and every TC (test)
                                against the archived source artifact
"""

import argparse
import re
import json
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    plan_file,
    plan_label,
    receipt_filename,
    REPO_BASE_PATH as _REPO_ROOT,
    REPO_BASE_PATH,
    PACKAGES_STRUCTURE,
    SUB_BEARING_EXEC_PHASES,
    TEST_PLAN_PHASE_KEY,
    TEST_PLAN_SUB_THRESHOLD,
    get_module_path,
    validate_module,
)
from marker_parser import parse_file, flatten, find_by_kind, MarkerBlock, ParseResult

STAGE_NAMES = {
    1: "Parse & Plan",
    2: "Split frontend-execution-plan.md",
    3: "Split frontend-test-plan.md",
    4: "Generate Index Files",
    5: "Verify Completeness",
}

# Derived from config's single source of truth — no second hardcoded map.
# The frontend execution phase names ARE their own folder names.
EXEC_PHASES = set(PACKAGES_STRUCTURE["frontend-execution"])


# ─────────────────────────────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────────────────────────────

def _state_path(mod: str, base: Path = None) -> Path:
    if base is None:
        base = get_module_path(mod)
    return base / "packages" / "_agent3-state.json"


def load_state(mod: str, base: Path = None) -> dict:
    p = _state_path(mod, base)
    if p.exists():
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"stages_completed": [], "stages": {}}


def save_state(mod: str, state: dict, base: Path = None):
    p = _state_path(mod, base)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)


def mark_stage_complete(state: dict, stage: int):
    if stage not in state["stages_completed"]:
        state["stages_completed"].append(stage)
    state["stages"][str(stage)] = {"completed_at": datetime.now().isoformat()}


def print_status(mod: str, base: Path = None):
    state = load_state(mod, base)
    print()
    print("═" * 62)
    print(f"  AGENT 3 — Status")
    print(f"  Module  : {mod}")
    print("═" * 62)
    for stage_num, name in STAGE_NAMES.items():
        done = stage_num in state.get("stages_completed", [])
        status = "✓ DONE" if done else "— pending"
        print(f"  Stage {stage_num} — {name:<32} {status}")
    if state.get("stages", {}).get("5"):
        print()
        print(f"  Last run: {state['stages']['5']['completed_at']}")
    print()


def confirm(prompt: str = "  Proceed?") -> bool:
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer == "y"


# ─────────────────────────────────────────────────────────────────────────────
# WRITE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _wrap_block(block: "MarkerBlock") -> str:
    """
    Re-wrap a block's content in its OWN START/END marker so the package
    file is an independently parseable artifact (and Stage 5 can find it
    by marker lookup). Nested markers inside block.content (e.g. TC
    blocks inside a UI-FLOWS SUB) are preserved verbatim.
    """
    kind = block.kind.upper()
    content = block.content
    if content and not content.endswith("\n"):
        content += "\n"
    return f"<!-- {kind}:{block.marker_id}:START -->\n{content}<!-- {kind}:{block.marker_id}:END -->\n"


def _write_block(path: Path, block: "MarkerBlock", header: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (header + "\n\n") if header else ""
    text += _wrap_block(block)
    path.write_text(text, encoding="utf-8")


def _write_content(path: Path, content: str, header: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (header + "\n\n") if header else ""
    text += content
    path.write_text(text, encoding="utf-8")


def _execute_write_plan(write_plan: list[dict]):
    for w in write_plan:
        if "block" in w:
            _write_block(w["dest"], w["block"], w.get("header", ""))
        else:
            _write_content(w["dest"], w["content"], w.get("header", ""))


def _safe_filename(marker_id: str) -> str:
    return marker_id.strip().replace(" ", "-") + ".md"


def _preamble_content(block: "MarkerBlock", raw_lines: list[str]) -> str:
    """
    Extract content between a container's START marker and its first
    child SUB — the 'preamble' that belongs to the container but is
    outside any SUB. Returns empty string if no preamble exists.
    """
    children_with_sub = [c for c in block.children if c.kind == "sub"]
    if not children_with_sub:
        return ""
    first_child_start = children_with_sub[0].start_line
    preamble_lines = raw_lines[block.start_line: first_child_start - 1]
    return "".join(preamble_lines).strip()


# ─────────────────────────────────────────────────────────────────────────────
# THRESHOLDS — advisory by default, blocking with --strict-thresholds.
# Covers only marker-countable frontend cases (PROJECT-3-REGISTRY-2.md):
# the frontend test plan should carry UI-FLOWS / INT-FLOW SUBs when it
# has more than TEST_PLAN_SUB_THRESHOLD TCs.
# ─────────────────────────────────────────────────────────────────────────────

def check_thresholds(exec_result, test_result) -> list[str]:
    """Return a list of human-readable threshold advisories (empty = none)."""
    advisories = []
    if test_result:
        phases_t = find_by_kind(test_result.root_blocks, "phase")
        for p in phases_t:
            tc_count = len([t for t in flatten([p]) if t.kind == "tc"])
            sub_count = len([s for s in p.children if s.kind == "sub"])
            if tc_count > TEST_PLAN_SUB_THRESHOLD and sub_count == 0:
                advisories.append(
                    f"PHASE:{p.marker_id} has {tc_count} TCs (> {TEST_PLAN_SUB_THRESHOLD}) "
                    f"but no SUB grouping — the registry expects SUB:UI-FLOWS / "
                    f"SUB:INT-FLOW above this threshold."
                )
    return advisories


# ─────────────────────────────────────────────────────────────────────────────
# SAFE AUTOFIX — deterministic, reversible. Repairs the single most
# common frontend structural error: an unqualified SUB label in
# frontend-execution-plan.md (bare SUB:SCR-X inside PHASE:F1-F4 instead
# of SUB:F1-SCR-X). Writes a .orig backup and re-validates; restores on
# any regression. The test plan is deliberately untouched — its
# UI-FLOWS / INT-FLOW SUB labels are intentionally NOT phase-qualified.
# ─────────────────────────────────────────────────────────────────────────────

def _plan_sub_qualification_fixes(result: "ParseResult") -> list[dict]:
    """
    Identify bare (unqualified) SUB labels under F1-F4 phases that can be
    safely auto-prefixed with their enclosing phase key. A SUB whose
    label already starts with ANY known phase prefix is left alone (a
    cross-phase mismatch is a human decision, not an autofix).
    """
    known_prefixes = tuple(f"{ph}-" for ph in SUB_BEARING_EXEC_PHASES)
    fixes = []
    for phase in find_by_kind(result.root_blocks, "phase"):
        if phase.marker_id not in SUB_BEARING_EXEC_PHASES:
            continue
        for sub in [c for c in phase.children if c.kind == "sub"]:
            label = sub.marker_id
            if label.startswith(known_prefixes):
                continue  # already qualified (correctly or mismatched — leave mismatched to a human)
            new_label = f"{phase.marker_id}-{label}"
            fixes.append({
                "phase": phase.marker_id,
                "old_label": label,
                "new_label": new_label,
                "start_line": sub.start_line,
                "end_line": sub.end_line,
            })
    return fixes


def run_fix_safe(mod: str, base: Path = None, dry_run: bool = False) -> bool:
    if base is None:
        base = get_module_path(mod)
    src_path = plan_file(base, mod, "exec")

    print()
    print("═" * 70)
    print(f"  SAFE AUTOFIX — unqualified SUB labels ({plan_label('exec', mod)})")
    print(f"  Module : {mod}")
    print("═" * 70)
    print()

    if not src_path.exists():
        print(f"  — {plan_label('exec', mod)} not found at {src_path}. Nothing to fix.\n")
        return True

    result = parse_file(src_path)
    fixes = _plan_sub_qualification_fixes(result)

    if not fixes:
        print("  ✓ No unqualified F1-F4 SUB labels found — nothing to repair.\n")
        return True

    print(f"  Repairable unqualified SUB labels: {len(fixes)}")
    for f in fixes:
        print(f"    line {f['start_line']:>4}: PHASE:{f['phase']}  SUB:{f['old_label']}  →  SUB:{f['new_label']}")
    print()

    if dry_run:
        print("  — DRY RUN: no file changed, no backup written.\n")
        return True

    if not confirm("  Apply these reversible fixes (writes a .orig backup)?"):
        print("\n  Cancelled — no changes made.\n")
        return False

    lines = list(result.raw_lines)
    # Replace the label on both the START and END marker lines of each SUB.
    for f in fixes:
        old_tag_frag = f"SUB:{f['old_label']}:"
        new_tag_frag = f"SUB:{f['new_label']}:"
        for ln in (f["start_line"], f["end_line"]):
            if 1 <= ln <= len(lines):
                lines[ln - 1] = lines[ln - 1].replace(old_tag_frag, new_tag_frag)

    backup = src_path.with_suffix(src_path.suffix + ".orig")
    backup.write_text("".join(result.raw_lines), encoding="utf-8")
    src_path.write_text("".join(lines), encoding="utf-8")

    # Re-validate; restore if the fix introduced any new structural error.
    reparsed = parse_file(src_path)
    if reparsed.errors:
        src_path.write_text("".join(result.raw_lines), encoding="utf-8")
        backup.unlink(missing_ok=True)
        print("  ✗ Re-validation failed after autofix — original restored, backup removed.")
        for e in reparsed.errors[:10]:
            print(f"    [{e.severity}] line {e.line}: {e.message}")
        print()
        return False

    print(f"\n  ✓ {len(fixes)} SUB label(s) qualified. Backup: {backup.relative_to(base)}")
    print("  ✓ Re-validated clean. Re-run Stage 1 to split.\n")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1 — Parse & Plan
# ─────────────────────────────────────────────────────────────────────────────

def stage1_parse_and_plan(mod: str, state: dict, base: Path = None,
                           strict_thresholds: bool = False) -> dict | None:
    """
    Parses frontend-execution-plan.md + frontend-test-plan.md, validates
    marker structure, and shows a generation plan before anything is written.
    """
    if base is None:
        base = get_module_path(mod)

    exec_path = plan_file(base, mod, "exec")
    test_path = plan_file(base, mod, "test")

    print()
    print("═" * 70)
    print(f"  STAGE 1 — Parse & Plan")
    print(f"  Module : {mod}")
    print("═" * 70)
    print()

    exec_result: ParseResult | None = None
    test_result: ParseResult | None = None

    if exec_path.exists():
        exec_result = parse_file(exec_path)
        print(f"  ✓ Read {plan_label('exec', mod)}  ({exec_result.total_lines} lines)")
    else:
        print(f"  ⚠ {plan_label('exec', mod)} not found at {exec_path}")
        print(f"    Run agent2_archive.py first.")

    if test_path.exists():
        test_result = parse_file(test_path)
        print(f"  ✓ Read {plan_label('test', mod)}      ({test_result.total_lines} lines)")
    else:
        print(f"  — {plan_label('test', mod)} not found — will skip Stage 3 (acceptable if not generated yet)")

    if not exec_result and not test_result:
        print()
        print(f"  ERROR: Neither {plan_label('exec', mod)} nor {plan_label('test', mod)} found. Nothing to split.")
        return None

    all_errors = []
    if exec_result:
        all_errors += [(plan_label("exec", mod), e) for e in exec_result.errors]
    if test_result:
        all_errors += [(plan_label("test", mod), e) for e in test_result.errors]

    if all_errors:
        print()
        print("  ✗ STRUCTURAL ERRORS FOUND — splitting blocked until fixed:")
        print()
        for fname, err in all_errors:
            print(f"    [{err.severity}] {fname} line {err.line}: {err.message}")
        print()
        # Offer the autofix hint only when it would actually apply.
        if exec_result and _plan_sub_qualification_fixes(exec_result):
            print("  ⓘ Some of these look like unqualified F1-F4 SUB labels — try:")
            print(f"      python3 agent3_splitter.py --module {mod} --fix-safe --dry-run")
            print()
        print("  Fix the marker structure in the source artifact and re-run Stage 1.")
        return None

    print()
    print("  ✓ No structural errors — marker hierarchy is valid.")

    # Threshold advisories (advisory by default; blocking with --strict-thresholds).
    advisories = check_thresholds(exec_result, test_result)
    if advisories:
        print()
        label = "✗ THRESHOLD (strict — blocking)" if strict_thresholds else "⚠ THRESHOLD (advisory)"
        print(f"  {label}:")
        for a in advisories:
            print(f"    - {a}")
        if strict_thresholds:
            print()
            print("  --strict-thresholds is set — resolve the above and re-run, or drop the flag to proceed.")
            return None
        print()

    def _rel_to_repo(p: Path) -> str:
        # --output may point outside REPO_BASE_PATH (advanced/testing use);
        # fall back to the absolute path rather than crashing.
        try:
            return str(p.relative_to(REPO_BASE_PATH))
        except ValueError:
            return str(p)

    plan = {
        # Relative to REPO_BASE_PATH when possible, never crashing — see
        # config.py's build_manifest() note; this persists into _agent3-state.json.
        "exec_path": _rel_to_repo(exec_path) if exec_result else None,
        "test_path": _rel_to_repo(test_path) if test_result else None,
        "exec_summary": {},
        "test_summary": {},
    }

    if exec_result:
        phases = find_by_kind(exec_result.root_blocks, "phase")
        subs = find_by_kind(exec_result.root_blocks, "sub")

        print()
        print(f"  ── {plan_label('exec', mod)} plan ──────────────────────")
        print(f"    PHASE blocks : {len(phases)}")
        for p in phases:
            sub_count = len([s for s in p.children if s.kind == "sub"])
            if sub_count:
                print(f"      - PHASE:{p.marker_id:<10} → {sub_count} screen file(s) (SUB) + header")
            else:
                print(f"      - PHASE:{p.marker_id:<10} → 1 file (no SUB — never splits)")
        print(f"    Total SUB (screen) files : {len(subs)}")

        plan["exec_summary"] = {"phases": len(phases), "subs": len(subs)}

    if test_result:
        tcs = find_by_kind(test_result.root_blocks, "tc")
        subs_t = find_by_kind(test_result.root_blocks, "sub")
        phases_t = find_by_kind(test_result.root_blocks, "phase")

        print()
        print(f"  ── {plan_label('test', mod)} plan ───────────────────────────")
        for p in phases_t:
            sub_count = len([s for s in p.children if s.kind == "sub"])
            tc_count = len([t for t in flatten([p]) if t.kind == "tc"])
            extra = f", {sub_count} sub-section(s)" if sub_count else " (no SUB — below threshold)"
            print(f"      - PHASE:{p.marker_id:<12} → {tc_count} TC(s){extra}")
        print(f"    Total TC atomic files : {len(tcs)}")

        orphan_warnings = []
        for p in phases_t:
            sub_blocks = [c for c in p.children if c.kind == "sub"]
            if not sub_blocks:
                continue
            tcs_in_subs = {t.marker_id for sub in sub_blocks for t in flatten([sub]) if t.kind == "tc"}
            all_tcs_in_phase = [t for t in flatten([p]) if t.kind == "tc"]
            orphans = [t for t in all_tcs_in_phase if t.marker_id not in tcs_in_subs]
            if orphans:
                orphan_warnings.append((p.marker_id, orphans))

        if orphan_warnings:
            print()
            print("  ⚠ WARNING — Orphan TCs (inside PHASE but outside any SUB block):")
            print("    Stage 3 will NOT write these TCs to any package file.")
            for phase_id, orphans in orphan_warnings:
                ids = ", ".join(t.marker_id for t in orphans)
                print(f"    PHASE:{phase_id} → {len(orphans)} orphan TC(s): {ids}")
            print()

        plan["test_summary"] = {"phases": len(phases_t), "tcs": len(tcs), "subs": len(subs_t)}

    total_files = (
        plan["exec_summary"].get("subs", 0) + plan["exec_summary"].get("phases", 0)
        + plan["test_summary"].get("tcs", 0) + plan["test_summary"].get("phases", 0)
    )
    print()
    print(f"  Estimated package files to generate: ~{total_files}")
    print()

    if not confirm("  Approve Stage 1 plan and proceed?"):
        print("\n  Stage 1 cancelled — no files written.\n")
        return None

    state["exec_plan_path"] = plan["exec_path"]
    state["test_plan_path"] = plan["test_path"]
    mark_stage_complete(state, 1)
    save_state(mod, state, base)

    print("  ✓ Stage 1 complete.\n")
    return plan


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2 — Split frontend-execution-plan.md
# ─────────────────────────────────────────────────────────────────────────────

def stage2_split_execution(mod: str, state: dict, plan: dict | None,
                             base: Path = None, dry_run: bool = False) -> bool:
    if base is None:
        base = get_module_path(mod)

    src_path = plan_file(base, mod, "exec")
    pkg_root = base / "packages" / "frontend-execution"

    print()
    print("═" * 70)
    print(f"  STAGE 2 — Split {plan_label('exec', mod)}")
    print(f"  Module : {mod}")
    print("═" * 70)
    print()

    if not src_path.exists():
        print(f"  — {plan_label('exec', mod)} not found at {src_path}. Skipping Stage 2.\n")
        if not dry_run:
            mark_stage_complete(state, 2)
            save_state(mod, state, base)
        return True

    result = parse_file(src_path)
    if result.errors:
        print("  ✗ Structural errors present:")
        for e in result.errors[:10]:
            print(f"    [{e.severity}] line {e.line}: {e.message}")
        print()
        return False

    phases = find_by_kind(result.root_blocks, "phase")
    write_plan = []

    for phase in phases:
        if phase.marker_id not in EXEC_PHASES:
            print(f"  ⚠ PHASE:{phase.marker_id} is not a known frontend execution phase "
                  f"({sorted(EXEC_PHASES)}) — skipped.")
            continue
        folder = pkg_root / phase.marker_id

        sub_blocks = [c for c in phase.children if c.kind == "sub"]

        if sub_blocks:
            preamble = _preamble_content(phase, result.raw_lines)
            header_filename = _safe_filename(f"{phase.marker_id}-HEADER") if preamble else None

            if preamble:
                write_plan.append({
                    "dest": folder / header_filename,
                    "content": preamble,
                    "header": f"<!-- Source: PHASE:{phase.marker_id} / PREAMBLE (before first SUB) -->",
                    "note": "phase-level content (tables, strategy, intro)",
                })

            for sub in sub_blocks:
                fname = _safe_filename(sub.marker_id)
                context_ref = (
                    f"<!-- Context: see {header_filename} for phase-level strategy, registry table, and intro -->"
                    if header_filename else ""
                )
                header_line = f"<!-- Source: PHASE:{phase.marker_id} / SUB:{sub.marker_id} -->"
                if context_ref:
                    header_line += f"\n{context_ref}"
                write_plan.append({
                    "dest": folder / fname,
                    "block": sub,
                    "header": header_line,
                    "note": "screen block",
                })
        else:
            fname = _safe_filename(phase.marker_id)
            write_plan.append({
                "dest": folder / fname,
                "block": phase,
                "header": f"<!-- Source: PHASE:{phase.marker_id} -->",
                "note": "whole-phase block (never splits)",
            })

    print(f"  Files to write: {len(write_plan)}")
    for w in write_plan[:15]:
        extra = f"  ({w['note']})" if w.get("note") else ""
        print(f"    {w['dest'].relative_to(base)}{extra}")
    if len(write_plan) > 15:
        print(f"    ... and {len(write_plan) - 15} more")
    print()

    if dry_run:
        print("  — DRY RUN: no files written, no state changed.\n")
        return True

    if not confirm("  Approve Stage 2 — write these files?"):
        print("\n  Stage 2 cancelled — no files written.\n")
        return False

    _execute_write_plan(write_plan)

    print(f"\n  ✓ {len(write_plan)} files written to packages/frontend-execution/")
    mark_stage_complete(state, 2)
    save_state(mod, state, base)
    print("  ✓ Stage 2 complete.\n")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 3 — Split frontend-test-plan.md
# ─────────────────────────────────────────────────────────────────────────────

def stage3_split_test(mod: str, state: dict, plan: dict | None,
                        base: Path = None, dry_run: bool = False) -> bool:
    if base is None:
        base = get_module_path(mod)

    src_path = plan_file(base, mod, "test")
    pkg_root = base / "packages" / "frontend-test"
    expected_phase_key = TEST_PLAN_PHASE_KEY

    print()
    print("═" * 70)
    print(f"  STAGE 3 — Split {plan_label('test', mod)}")
    print(f"  Module : {mod}")
    print("═" * 70)
    print()

    if not src_path.exists():
        print(f"  — {plan_label('test', mod)} not found at {src_path}. Skipping Stage 3.\n")
        if not dry_run:
            mark_stage_complete(state, 3)
            save_state(mod, state, base)
        return True

    result = parse_file(src_path)
    if result.errors:
        print("  ✗ Structural errors present:")
        for e in result.errors[:10]:
            print(f"    [{e.severity}] line {e.line}: {e.message}")
        print()
        return False

    phases = find_by_kind(result.root_blocks, "phase")
    write_plan = []

    for phase in phases:
        if phase.marker_id != expected_phase_key:
            print(f"  ⚠ PHASE:{phase.marker_id} does not match the expected "
                  f"'{expected_phase_key}' — processing anyway, but this may "
                  f"indicate a generation-time naming issue.")
        folder = pkg_root

        sub_blocks = [c for c in phase.children if c.kind == "sub"]

        if sub_blocks:
            preamble = _preamble_content(phase, result.raw_lines)
            header_filename = _safe_filename(f"{phase.marker_id}-HEADER") if preamble else None

            if preamble:
                write_plan.append({
                    "dest": folder / header_filename,
                    "content": preamble,
                    "header": f"<!-- Source: PHASE:{phase.marker_id} / PREAMBLE (before first SUB) -->",
                    "note": "phase-level content (mandatory scenarios, intro)",
                })

            for sub in sub_blocks:
                # Test-plan SUB labels (UI-FLOWS / INT-FLOW) are deliberately
                # NOT phase-qualified — one phase per file, no collision.
                fname = _safe_filename(sub.marker_id)
                sub_tc_count = len([t for t in flatten([sub]) if t.kind == "tc"])
                context_ref = (
                    f"<!-- Context: see {header_filename} for phase-level intro and mandatory scenarios -->"
                    if header_filename else ""
                )
                header_line = f"<!-- Source: PHASE:{phase.marker_id} / SUB:{sub.marker_id} -->"
                if context_ref:
                    header_line += f"\n{context_ref}"
                write_plan.append({
                    "dest": folder / fname,
                    "block": sub,
                    "header": header_line,
                    "note": f"{sub_tc_count} TC(s) embedded",
                })
        else:
            fname = _safe_filename(phase.marker_id)
            tc_count = len([t for t in flatten([phase]) if t.kind == "tc"])
            write_plan.append({
                "dest": folder / fname,
                "block": phase,
                "header": f"<!-- Source: PHASE:{phase.marker_id} -->",
                "note": f"{tc_count} TC(s) embedded",
            })

    print(f"  Files to write: {len(write_plan)}")
    for w in write_plan[:15]:
        extra = f"  ({w['note']})" if w.get("note") else ""
        print(f"    {w['dest'].relative_to(base)}{extra}")
    if len(write_plan) > 15:
        print(f"    ... and {len(write_plan) - 15} more")
    print()

    if dry_run:
        print("  — DRY RUN: no files written, no state changed.\n")
        return True

    if not confirm("  Approve Stage 3 — write these files?"):
        print("\n  Stage 3 cancelled — no files written.\n")
        return False

    _execute_write_plan(write_plan)

    print(f"\n  ✓ {len(write_plan)} files written to packages/frontend-test/")
    mark_stage_complete(state, 3)
    save_state(mod, state, base)
    print("  ✓ Stage 3 complete.\n")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 4 — Generate Index Files
# ─────────────────────────────────────────────────────────────────────────────

def stage4_generate_index(mod: str, state: dict, base: Path = None, dry_run: bool = False) -> bool:
    if base is None:
        base = get_module_path(mod)

    pkg_root = base / "packages"

    print()
    print("═" * 70)
    print(f"  STAGE 4 — Generate Index Files")
    print(f"  Module : {mod}")
    print("═" * 70)
    print()

    if not pkg_root.exists():
        print("  — No packages/ folder found. Run Stage 2/3 first.\n")
        return False

    index_targets = []
    for folder in sorted(pkg_root.rglob("*")):
        if not folder.is_dir():
            continue
        md_files = sorted([f for f in folder.glob("*.md") if f.name != "index.md"])
        if md_files:
            index_targets.append((folder, md_files))

    print(f"  Folders to index: {len(index_targets)}")
    for folder, files in index_targets:
        print(f"    {folder.relative_to(base)}  ({len(files)} file(s))")
    print()

    if dry_run:
        print("  — DRY RUN: no files written, no state changed.\n")
        return True

    if not confirm("  Approve Stage 4 — write index.md files?"):
        print("\n  Stage 4 cancelled — no index files written.\n")
        return False

    for folder, files in index_targets:
        lines = [f"# Index — {folder.relative_to(pkg_root)}", ""]
        for f in files:
            lines.append(f"- [{f.stem}]({f.name})")
        (folder / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n  ✓ {len(index_targets)} index.md files written.")
    mark_stage_complete(state, 4)
    save_state(mod, state, base)
    print("  ✓ Stage 4 complete.\n")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 5 — Verify Completeness
# Verifies the FRONTEND element model: every SUB (screen) block and every
# no-SUB PHASE block from frontend-execution-plan.md, and every TC from
# frontend-test-plan.md, is embedded in a package file with byte-identical
# (hash-identical) content. There are NO API/XM atoms to verify — the
# frontend carries none.
# ─────────────────────────────────────────────────────────────────────────────

def _content_hash(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()



def write_split_receipt(mod: str, version: int, base: Path, artifacts: dict) -> Path:
    """AMEND-PIPELINE-V5 §1D.8 — record every package file as a ledger row
    (repo_path) in base/receipts/; the orchestrator appends it to the module
    ledger. Rows are whatever Stage 2/3 actually wrote — nothing is spelled."""
    from datetime import datetime
    rows = []
    for stage, subdir in artifacts.items():
        root = base / "packages" / subdir
        if not root.exists():
            continue
        for f in sorted(root.rglob("*.md")):
            try:
                rel = str(f.relative_to(_REPO_ROOT))
            except ValueError:
                rel = str(f)
            rows.append({"engine": "agent3_splitter", "stage": stage, "filename": f.name,
                         "artifact": f"package/{subdir}", "repo_path": rel,
                         "recorded_at": datetime.now().isoformat(timespec="seconds"),
                         "status": "UPLOADED"})
    out = base / "receipts" / receipt_filename(mod, version)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"module": mod, "version": version, "rows": rows},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def stage5_verify(mod: str, state: dict, base: Path = None) -> bool:
    if base is None:
        base = get_module_path(mod)

    exec_path = plan_file(base, mod, "exec")
    test_path = plan_file(base, mod, "test")
    pkg_root = base / "packages"

    print()
    print("═" * 70)
    print(f"  STAGE 5 — Verify Completeness & Integrity")
    print(f"  Module : {mod}")
    print("═" * 70)
    print()

    missing_issues = []
    hash_issues = []
    checked_count = 0

    def _find_marker_in_files(kind: str, marker_id: str, pkg_subroot: Path):
        pattern_start = f"<!-- {kind.upper()}:{marker_id}:START -->"
        if not pkg_subroot.exists():
            return None, None
        for f in pkg_subroot.rglob("*.md"):
            if f.name == "index.md":
                continue
            text = f.read_text(encoding="utf-8")
            if pattern_start in text:
                sub_result = parse_file(f)
                matches = [b for b in flatten(sub_result.root_blocks)
                           if b.kind == kind and b.marker_id == marker_id]
                if matches:
                    return f, matches[0]
        return None, None

    def _verify_blocks(blocks, file_label, pkg_subroot):
        nonlocal checked_count
        for block in blocks:
            checked_count += 1
            pkg_file, pkg_block = _find_marker_in_files(block.kind, block.marker_id, pkg_subroot)

            if pkg_file is None:
                missing_issues.append(
                    f"{block.kind.upper()}:{block.marker_id} ({file_label}) — "
                    f"found in source but not embedded in any package file"
                )
                continue

            if _content_hash(block.content) != _content_hash(pkg_block.content):
                hash_issues.append(
                    f"{block.kind.upper()}:{block.marker_id} ({file_label}) — "
                    f"content MISMATCH inside {pkg_file.relative_to(base)}"
                )

    if exec_path.exists():
        result = parse_file(exec_path)
        phases = find_by_kind(result.root_blocks, "phase")
        subs = find_by_kind(result.root_blocks, "sub")
        no_sub_phases = [p for p in phases if not any(c.kind == "sub" for c in p.children)]
        pkg_exec = pkg_root / "frontend-execution"
        _verify_blocks(subs, plan_label("exec", mod), pkg_exec)
        _verify_blocks(no_sub_phases, plan_label("exec", mod), pkg_exec)
        print(f"  {plan_label('exec', mod)} : {len(subs)} SUB screen(s) + "
              f"{len(no_sub_phases)} no-SUB PHASE(s) checked")

    if test_path.exists():
        result = parse_file(test_path)
        tcs = find_by_kind(result.root_blocks, "tc")
        _verify_blocks(tcs, plan_label("test", mod), pkg_root / "frontend-test")
        print(f"  {plan_label('test', mod)}       : {len(tcs)} TC(s) checked")

    print(f"  Total addressable elements checked : {checked_count}")
    print()

    if missing_issues or hash_issues:
        if missing_issues:
            print(f"  ✗ {len(missing_issues)} MISSING file issue(s):")
            for i in missing_issues:
                print(f"    - {i}")
            print()
        if hash_issues:
            print(f"  ✗ {len(hash_issues)} CONTENT MISMATCH issue(s):")
            for i in hash_issues:
                print(f"    - {i}")
            print()
        print("  Re-run Stage 2/3 to regenerate, then Stage 5 again.")
        return False

    if checked_count == 0:
        print("  ⚠ Nothing to verify — no SUB/PHASE/TC elements found in the source artifacts.")
        return False

    print("  ✓ Every SUB / no-SUB PHASE (exec) and TC (test) has a matching package file.")
    print("  ✓ Content hash verified for every element — zero drift from archived source.")
    mark_stage_complete(state, 5)
    save_state(mod, state, base)
    print()
    # FE resolves its version from its own folder tree (AMEND-IFA); when
    # stage 5 runs against an isolated --output/test base, fall back to v1.
    _m = re.fullmatch(r"v(\d+)", base.name)
    _version = int(_m.group(1)) if _m else 1
    receipt = write_split_receipt(mod, _version, base,
                                  {"P3_2": "frontend-execution", "P3_5_FE": "frontend-test"})
    print(f"  ✓ Split receipt written → {receipt.name}  (append: journey_loader.py --append-receipts {receipt})")
    print(f"  ✓ Stage 5 complete — frontend splitting verified.")
    print(f"  Module [{mod}] fully packaged.")
    print()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATION
# ─────────────────────────────────────────────────────────────────────────────

def run_stage(stage: int, mod: str, state: dict, plan: dict | None,
              base: Path = None, dry_run: bool = False,
              strict_thresholds: bool = False) -> tuple[bool, dict | None]:
    if stage == 1:
        result_plan = stage1_parse_and_plan(mod, state, base, strict_thresholds=strict_thresholds)
        return (result_plan is not None), result_plan
    elif stage == 2:
        ok = stage2_split_execution(mod, state, plan, base, dry_run=dry_run)
        return ok, plan
    elif stage == 3:
        ok = stage3_split_test(mod, state, plan, base, dry_run=dry_run)
        return ok, plan
    elif stage == 4:
        ok = stage4_generate_index(mod, state, base, dry_run=dry_run)
        return ok, plan
    elif stage == 5:
        ok = stage5_verify(mod, state, base)
        return ok, plan
    else:
        print(f"  Unknown stage: {stage}")
        return False, plan


def _validate_and_report(label: str, path: Path) -> int:
    """Parse one file, print a one-line summary or its errors. Returns exit code."""
    result = parse_file(path)
    if result.errors:
        print(f"\n  ✗ STRUCTURAL ERRORS in {label}:")
        for e in result.errors:
            print(f"    [{e.severity}] line {e.line}: {e.message}")
        return 1
    phases = find_by_kind(result.root_blocks, "phase")
    subs = find_by_kind(result.root_blocks, "sub")
    tcs = find_by_kind(result.root_blocks, "tc")
    print(f"\n  ✓ {label}: marker structure valid — "
          f"{len(phases)} PHASE, {len(subs)} SUB, {len(tcs)} TC block(s).")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Split frontend-execution-plan.md/frontend-test-plan.md into package files.")
    parser.add_argument("--module", "-m", help="Module code (module code).")
    parser.add_argument("--stage", "-s", type=int, choices=[1, 2, 3, 4, 5], help="Run a single stage only.")
    parser.add_argument("--resume", "-r", action="store_true", help="Resume from the next incomplete stage.")
    parser.add_argument("--status", action="store_true", help="Show stage completion status and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be written without writing anything.")
    parser.add_argument("--strict-thresholds", action="store_true",
                         help="Treat threshold advisories (e.g. test plan TCs > 8 without SUB) as blocking.")
    parser.add_argument("--fix-safe", action="store_true",
                         help="Deterministically repair unqualified F1-F4 SUB labels in "
                              "frontend-execution-plan.md (writes a .orig backup, re-validates). "
                              "Combine with --dry-run to preview.")
    parser.add_argument("--output", "-o", help="Override the module's base path (advanced/testing use).")
    parser.add_argument("--validate-markers", action="store_true",
                         help="Parse and validate marker structure only — no writes, no state changes, "
                              "no module registration required if used with --file.")
    parser.add_argument("--file", help="With --validate-markers: validate this specific file directly "
                                        "(e.g. before it has been archived for any module).")

    args = parser.parse_args()

    if args.validate_markers and args.file:
        target = Path(args.file)
        if not target.exists():
            print(f"\n  ERROR: file not found: {target}\n")
            sys.exit(1)
        code = _validate_and_report(target.name, target)
        print()
        sys.exit(code)

    if not args.module:
        print("\n  ERROR: --module is required (unless using --validate-markers --file).\n")
        sys.exit(1)

    try:
        mod = validate_module(args.module)
    except ValueError as e:
        print(f"\n  ERROR: {e}\n")
        sys.exit(1)

    base = Path(args.output) if args.output else get_module_path(mod)

    if args.fix_safe:
        ok = run_fix_safe(mod, base, dry_run=args.dry_run)
        sys.exit(0 if ok else 1)

    if args.validate_markers:
        targets = [
            (plan_label("exec", mod), plan_file(base, mod, "exec")),
            (plan_label("test", mod), plan_file(base, mod, "test")),
        ]
        checked = 0
        exit_code = 0
        for label, p in targets:
            if not p.exists():
                continue
            checked += 1
            exit_code = max(exit_code, _validate_and_report(label, p))
        if checked == 0:
            print(f"\n  Nothing to validate — neither file found for module {mod}.")
        print()
        sys.exit(exit_code)

    if args.status:
        print_status(mod, base)
        sys.exit(0)

    state = load_state(mod, base)

    if args.stage:
        plan = None
        if args.stage > 1 and (args.stage - 1) not in state.get("stages_completed", []):
            ok, plan = run_stage(1, mod, state, None, base, strict_thresholds=args.strict_thresholds)
            if not ok:
                sys.exit(1)
        ok, _ = run_stage(args.stage, mod, state, plan, base, dry_run=args.dry_run,
                          strict_thresholds=args.strict_thresholds)
        sys.exit(0 if ok else 1)

    if args.resume:
        stages_to_run = [s for s in range(1, 6) if s not in state.get("stages_completed", [])]
        if not stages_to_run:
            print("\n  All stages already complete. Nothing to resume.\n")
            sys.exit(0)
    else:
        stages_to_run = list(range(1, 6))

    plan = None
    for stage in stages_to_run:
        ok, plan = run_stage(stage, mod, state, plan, base, dry_run=args.dry_run,
                             strict_thresholds=args.strict_thresholds)
        if not ok:
            print(f"\n  Stopped at Stage {stage}. Fix the issue and re-run with --resume.\n")
            sys.exit(1)

    print("\n  ✓ All 5 stages complete.\n")


if __name__ == "__main__":
    main()
