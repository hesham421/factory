# FRONTEND TEST PLAN — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Scope : project (modules FIN, MDL, SEC)
Sources: srs-sec.md v1 · frontend-execution-plan-sec.md — **MISSING** (P3.2 has not run
  for SEC; no version of this artifact exists in `_state/`)
Framework: agnostic (profile.stack.testing.frontend).
REDUCED: **yes** — no frontend execution plan exists (no `SCR-*`/route/F-block source),
  so no screen-bound TC can be derived per engine §1 ("A missing optional plan → the
  corresponding test plan is written in REDUCED mode ... no endpoint/screen binding").
══════════════════════════════════════════════════════════════════

<!-- PHASE:TEST-PLAN-FE:START traces=REQ-SEC-001 -->
No TC blocks in this file. Every one of SEC's 33 acceptance criteria is already covered
on the backend track (`backend-test-plan-sec.md`) via its bound `API-*`; per the engine's
own TC-ownership rule ("both plans share it, so no TC id repeats" — engine §6), a TC is
defined once, in whichever plan can bind it to a real endpoint or screen. None of SEC's
`SCR-REQ-*` (10 screen requirements, srs-fin.md Part B) has yet been turned into a
`SCR-*`/route by P3.2, so there is nothing to bind a frontend-specific TC to today.
<!-- PHASE:TEST-PLAN-FE:END -->

No `INT-UXD` phase — no `UXD-*` exists anywhere in the platform yet (no P3.2 has run for
any module); not an empty block, simply absent, per §2/§5 of the engine.

## TC TRACEABILITY INDEX
| AC | TC | REQ | SCR | RULE/code | UXD |
|---|---|---|---|---|---|
| (all 33) | see backend-test-plan-sec.md | (all 33) | none assigned yet | — | none |

## COVERAGE
AC covered: 33/33, but entirely on the backend track (see backend-test-plan-sec.md) — not
a frontend gap, a REDUCED-mode limitation stated per engine §1. REQ covered: same. SCR
covered: not applicable (0 `SCR-*` exist for SEC). Every selected-module UXD covered: not
applicable (0 `UXD-*` exist anywhere).

**Re-run this file once SEC's P3.2 (frontend-execution-plan-sec.md) exists** — at that
point the engine will bind screen-level flows (form validation, composite-screen
search↔entry, permission-hidden affordance) to real `SCR-*` ids and this file gains real
content; nothing here needs to change to make that happen.
══════════════════════════════════════════════════════════════════
