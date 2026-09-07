# UI/UX SPEC — الملاحظات الشخصية (Personal Notes) — DEMO
══════════════════════════════════════════════════════════════════
Module   : DEMO
Date     : 2026-09-07
Status   : DRAFT (design intent — human approval pending, per
           CONTRACT-11/12; not yet confirmed against a real UI Shell)
══════════════════════════════════════════════════════════════════

## ui-ux-spec-demo.md — SCR-DEMO-001 — canonical format
──────────────────────────────────────────────────────────────────
Screen           : SCR-DEMO-001 — My Notes (ملاحظاتي)
UI Pattern       : PATTERN-2 — Inline / Side Drawer (from srs-demo.md
                   B1 — unchanged)
Create/Edit Container Pattern : SIDE_DRAWER
  Decision (AMEND-P3-O order): not hierarchical (rule 1 N/A); not a
  header + repeating line-items with a computed total (rule 2 N/A);
  bounded field count (title, content), no repeating child rows
  (rule 3 applies) → SIDE_DRAWER. Confirms srs-demo.md B1's Container
  Pattern — no change.

Fields shown:
  List view (from srs-demo.md B1 "List View" note):
    - title       — primary row label
    - updatedAt   — secondary/trailing text, most-recent-first sort
  Entry/Drawer fields (from srs-demo.md B3 — every field, no
  additions/omissions):
    - title       — single-line text input, required
    - content     — multi-line text area, optional

Permissions : R1 (OWNER) only — VIEW/CREATE/UPDATE/DELETE, from
              srs-demo.md B4 (reference only, not redefined here).

Empty state : "لا توجد ملاحظات بعد" (No notes yet) — centered message
              + a prominent "ملاحظة جديدة / New Note" button that opens
              the same Side Drawer used for New from the list toolbar.

Loading state : Skeleton placeholder rows (3-4) while the list request
              (API-DEMO-002) is in flight; the Drawer shows a disabled/
              spinner state on its Save button while a create/update/
              delete request is in flight.

Error state : Generic inline error banner at the top of the list (list
              load failure) or inside the Drawer (save/delete failure)
              with a retry action. ERR-ID → message mapping is Project
              3.2's job (F3), not decided here.

Design intent note: PROPOSAL, not final. A simple two-pane feel within
  one screen: a scrollable list of note cards/rows on the left/main
  area, with the Side Drawer sliding in from the right for New/Edit.
  Minimal chrome — no filters, no tags, no bulk actions, consistent
  with the module's deliberately small scope (business-policies-
  demo.md SCOPE EXCEPTIONS). Delete is offered inside the open Drawer
  for an existing note (not a separate icon in the list row), to keep
  the list itself as simple as possible.
──────────────────────────────────────────────────────────────────

## STAGE C — visual-mockups/

Not produced in this factory pass. Per governance-tools/tracks/backend/
config.py (P2_5 ARTIFACT_FILES comment), `visual-mockups/` is a
directory that lives in the FRONTEND repo, not this factory — this
factory's P2.5 output is the two text artifacts (flow-diagram-demo.md,
this file) only. Claude Design mockup generation is out of scope for
this analysis-only factory.

══════════════════════════════════════════════════════════════════
*End of ui-ux-spec-demo.md*
*Next: Project 3.1 (Backend Execution Plan) — pass 1 continues.*
*Note: this file + flow-diagram-demo.md remain DRAFT until a human*
*approves them (CONTRACT-11/12) — that approval happens outside this*
*automated factory run; P3.1 may proceed per analyze-pass1.md's normal*
*sequencing (P2.5 does not gate P3.1/P3.5 — only P3.2, pass 2, needs*
*human-approved P2.5 output, per CONTRACT-12).*
══════════════════════════════════════════════════════════════════
