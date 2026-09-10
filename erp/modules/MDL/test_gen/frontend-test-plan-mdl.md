# FRONTEND TEST PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Scope : project (modules FIN, MDL, SEC)
Sources: srs-mdl.md v1 · frontend-execution-plan-mdl.md — **MISSING** (P3.2 has not run
  for MDL).
Framework: agnostic. REDUCED: **yes** — no frontend execution plan exists.
══════════════════════════════════════════════════════════════════

<!-- PHASE:TEST-PLAN-FE:START traces=REQ-MDL-001 -->
No TC blocks in this file. All 13 of MDL's acceptance criteria (plus the 1 integration
case) are already covered on the backend track (`backend-test-plan-mdl.md`). Neither of
MDL's 2 `SCR-REQ-*` (Generic Lookups, Type registry — srs-mdl.md Part B) has yet been
turned into a `SCR-*`/route by P3.2.
<!-- PHASE:TEST-PLAN-FE:END -->

No `INT-UXD` phase — no `UXD-*` exists anywhere in the platform yet.

## TC TRACEABILITY INDEX
| AC | TC | REQ | SCR | RULE/code | UXD |
|---|---|---|---|---|---|
| (all 13) | see backend-test-plan-mdl.md | (all 13) | none assigned yet | — | none |

## COVERAGE
AC covered: 13/13, entirely on the backend track — a REDUCED-mode limitation, not a gap.
SCR covered: not applicable (0 `SCR-*` exist for MDL). UXD covered: not applicable.

**Re-run once MDL's P3.2 (frontend-execution-plan-mdl.md) exists.**
══════════════════════════════════════════════════════════════════
