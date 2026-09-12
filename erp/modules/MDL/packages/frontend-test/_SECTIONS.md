<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
# FRONTEND TEST PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Scope : module (MDL)
Sources: srs-mdl.md v1 · frontend-execution-plan-mdl.md v1 · registry-srs-mdl.md v1 ·
         registry-exec-fe-mdl.md v1
Framework: agnostic (profile.stack.testing.frontend). REDUCED: **no** — P3.2 has run for MDL,
so every test case below binds to a real `SCR-*` and its route.
TC count: 11 — TC-MDL-015 … TC-MDL-025, continuing the module's one TC sequence after the
backend plan's highest id (TC-MDL-014). No id is renumbered and no backend TC is touched.
Open ADRs: 0 new. The plan cites ADR-MDL-005 and ADR-MDL-007 where a screen's behaviour
follows one of them.
SUPERSEDES the REDUCED stub this file previously held, which recorded that P3.2 had not run
for MDL and that no `SCR-*` existed. That is no longer true: SCR-MDL-001, SCR-MDL-002 and
UXD-MDL-001 exist.
══════════════════════════════════════════════════════════════════

Scope is `module`, so this run derives from MDL's own `AC-*` only. The integration phase
`INT-UXD` is **absent by rule**, not empty and not a gap: UXD-MDL-001 names the security
module as the owner of the displayed data, and that module is not in this selection — §2 rule
1 and §5 of the engine. An `INT-UXD` phase appears the first time this stage runs at
`--modules MDL,SEC` or `--scope project`.



## TC TRACEABILITY INDEX

| AC | TC | REQ | SCR | RULE / code |
|---|---|---|---|---|
| AC-MDL-001 | TC-MDL-015 | REQ-MDL-001 | SCR-MDL-001 | — |
| AC-MDL-002 | TC-MDL-016 | REQ-MDL-002 | SCR-MDL-001 | RULE-MDL-001 → MDL-409-MODULE-NOT-REGISTERED |
| AC-MDL-003 | TC-MDL-017 | REQ-MDL-003 | SCR-MDL-001 | RULE-MDL-003 |
| AC-MDL-004 | TC-MDL-018 | REQ-MDL-004 | SCR-MDL-001 | RULE-MDL-004 |
| AC-MDL-005 | TC-MDL-019 | REQ-MDL-005 | SCR-MDL-001 | — |
| AC-MDL-006 | TC-MDL-020 | REQ-MDL-006 | SCR-MDL-001 | — |
| AC-MDL-007 | TC-MDL-021 | REQ-MDL-007 | SCR-MDL-001 | RULE-MDL-002 → MDL-409-VALUE-DUP |
| AC-MDL-008 | TC-MDL-022 | REQ-MDL-008 | SCR-MDL-001 | — |
| AC-MDL-009 | TC-MDL-023 | REQ-MDL-009 | SCR-MDL-001 | — |
| AC-MDL-010 | TC-MDL-024 | REQ-MDL-010 | SCR-MDL-001 | MDL-400-REORDER-MISMATCH (on a partial set) |
| AC-MDL-013 | TC-MDL-025 | REQ-MDL-013 | SCR-MDL-002, SCR-MDL-001 | — |

### AC covered on the backend track only — not a gap on this track

| AC | REQ | Why no frontend case |
|---|---|---|
| AC-MDL-011 | REQ-MDL-011 | the consumer read by key — API-MDL-011's caller is a consuming module's backend over the platform's in-process module interface, and no MDL screen calls it (ADR-MDL-007) |
| AC-MDL-012 | REQ-MDL-012 | the not-found answer for an unknown key — answered to that same calling module; no screen requests a key that was never registered |

## COVERAGE

AC covered on this track: 11/13 — the two above are backend-only by construction, and 13/13
across the module when both plans are read together (`backend-test-plan-mdl.md` carries one TC
per AC for all 13).
REQ covered on this track: 11/13 — the same two REQ ids, for the same reason.
SCR covered: 2/2 — SCR-MDL-001 by ten cases, SCR-MDL-002 by the drill-across case, which
touches both.
UXD covered: not derived in this run — `INT-UXD` is an integration phase and this run is
`--module MDL`; UXD-MDL-001's owner module is outside the selection.
TC count check (§3 over-engineering guard): 11 cases against 13 ACs is well under 2×, and no
case is a fabricated variant — every one derives from a distinct AC.
Scenario mix: HAPPY 6 · VIOLATION 2 · STATE 3 · PERMISSION 0 (no MDL AC states a permission
outcome — the SRS Access summary grants MDL_LOOKUPS four actions and MDL_TYPE_REGISTRY one,
and no AC asserts a denial) · BOUNDARY 0 (no AC or RULE states a numeric limit).

## NOTES

- Every message asserted above is copied character-perfect from `srs-mdl.md` §A5 in both
  languages; no message is reworded and none is composed by a test.
- Two cases assert an **absence** deliberately: TC-MDL-018 and TC-MDL-023 check that no
  Activate affordance is drawn, because no endpoint exists for one (ADR-MDL-005) and a
  half-working toggle would be the likeliest thing for an implementer to add.
- TC-MDL-021 is one case with two submissions on purpose: AC-MDL-007's rule is scoped to the
  parent type, and a test that only checked the refusal would pass against a wrongly global
  uniqueness check.
- `test-execution-manifest-mdl.md` is a derived view of the **backend** plan and its API set.
  Neither changed in this run, so it is current and is not rewritten.
══════════════════════════════════════════════════════════════════
