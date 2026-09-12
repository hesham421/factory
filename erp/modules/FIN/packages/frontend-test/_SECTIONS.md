<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
# FRONTEND TEST PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Scope : module (FIN)
Sources: srs-fin.md v1 · frontend-execution-plan-fin.md v1 · registry-srs-fin.md v1 ·
         registry-exec-fe-fin.md v1
Framework: agnostic (profile.stack.testing.frontend). REDUCED: **no** — P3.2 has run for FIN,
so every test case below binds to a real `SCR-*` and its route.
TC count: 39 — TC-FIN-110 … TC-FIN-148, continuing the module's one TC sequence after the
backend plan's highest id (TC-FIN-109). No id is renumbered and no backend TC is touched.
Open ADRs: 0 new. The plan cites ADR-FIN-003, ADR-FIN-006, ADR-FIN-007 and ADR-FIN-008 where a
screen's behaviour follows one of them.
SUPERSEDES the REDUCED stub this file previously held, which recorded that P3.2 had not run and
asked to be re-run once it had ("None of FIN's 12 `SCR-REQ-*` has yet been turned into a
`SCR-*`/route by P3.2"). That is no longer true: SCR-FIN-001..012 and UXD-FIN-001..012 exist.
══════════════════════════════════════════════════════════════════

Scope is `module`, so this run derives from FIN's own `AC-*` only. The integration phase
`INT-UXD` is **absent by rule**, not empty and not a gap: `UXD-FIN-001..012` all name the
lookup module as the owner of the displayed data, and that module is not in this selection —
§2 rule 1 and §5 of the engine. An `INT-UXD` phase appears the first time this stage runs at
`--modules FIN,MDL` or `--scope project`.



## TC TRACEABILITY INDEX

| AC | TC | REQ | SCR | RULE / code |
|---|---|---|---|---|
| AC-FIN-001 | TC-FIN-110 | REQ-FIN-001 | SCR-FIN-001 | — |
| AC-FIN-002 | TC-FIN-111 | REQ-FIN-002 | SCR-FIN-001 | RULE-FIN-001 → FIN-409-PARENT-NOT-LEAF-ELIGIBLE / FIN-409-HAS-CHILDREN |
| AC-FIN-003 | TC-FIN-112 | REQ-FIN-003 | SCR-FIN-001 | — |
| AC-FIN-004 | TC-FIN-113 | REQ-FIN-004 | SCR-FIN-002 | — |
| AC-FIN-005 | TC-FIN-114 | REQ-FIN-005 | SCR-FIN-002 | — |
| AC-FIN-006 | TC-FIN-115 | REQ-FIN-006 | SCR-FIN-002 | RULE-FIN-002 → FIN-409-DIMVALUE-DUP |
| AC-FIN-007 | TC-FIN-116 | REQ-FIN-007 | SCR-FIN-003 | — |
| AC-FIN-008 | TC-FIN-117 | REQ-FIN-008 | SCR-FIN-003 | — |
| AC-FIN-009 | TC-FIN-118 | REQ-FIN-009 | SCR-FIN-003 | RULE-FIN-003 → FIN-409-REMAINDER-COUNT |
| AC-FIN-014 | TC-FIN-119 | REQ-FIN-014 | SCR-FIN-006 | — |
| AC-FIN-015 | TC-FIN-120 | REQ-FIN-015 | SCR-FIN-006 | RULE-FIN-006, RULE-FIN-007 → FIN-409-UNBALANCED, FIN-409-NOT-POSTABLE-ACCOUNT |
| AC-FIN-016 | TC-FIN-121 | REQ-FIN-016 | SCR-FIN-006 | RULE-FIN-016 |
| AC-FIN-017 | TC-FIN-122 | REQ-FIN-017 | SCR-FIN-006 | — |
| AC-FIN-018 | TC-FIN-123 | REQ-FIN-018 | SCR-FIN-006 | RULE-FIN-006 → FIN-409-UNBALANCED |
| AC-FIN-019 | TC-FIN-124 | REQ-FIN-019 | SCR-FIN-006 | RULE-FIN-007 → FIN-409-NOT-POSTABLE-ACCOUNT |
| AC-FIN-020 | TC-FIN-125 | REQ-FIN-020 | SCR-FIN-006 | RULE-FIN-008 → FIN-409-PERIOD-NOT-OPEN |
| AC-FIN-021 | TC-FIN-126 | REQ-FIN-021 | SCR-FIN-006 | RULE-FIN-009 → FIN-409-INVALID-DIMENSION |
| AC-FIN-027 | TC-FIN-127 | REQ-FIN-027 | SCR-FIN-006 | — |
| AC-FIN-028 | TC-FIN-128 | REQ-FIN-028 | SCR-FIN-006 | RULE-FIN-011 |
| AC-FIN-029 | TC-FIN-129 | REQ-FIN-029 | SCR-FIN-006 | RULE-FIN-012 |
| AC-FIN-030 | TC-FIN-130 | REQ-FIN-030 | SCR-FIN-006 | RULE-FIN-013 → FIN-409-ALREADY-REVERSED |
| AC-FIN-022 | TC-FIN-131 | REQ-FIN-022 | SCR-FIN-004 | — |
| AC-FIN-023 | TC-FIN-132 | REQ-FIN-023 | SCR-FIN-004, SCR-FIN-006 | — |
| AC-FIN-025 | TC-FIN-133 | REQ-FIN-025 | SCR-FIN-005 | RULE-FIN-003 |
| AC-FIN-026 | TC-FIN-134 | REQ-FIN-026 | SCR-FIN-005, SCR-FIN-006 | RULE-FIN-010 |
| AC-FIN-031 | TC-FIN-135 | REQ-FIN-031 | SCR-FIN-007 | — |
| AC-FIN-032 | TC-FIN-136 | REQ-FIN-032 | SCR-FIN-007 | — |
| AC-FIN-033 | TC-FIN-137 | REQ-FIN-033 | SCR-FIN-007 | — |
| AC-FIN-034 | TC-FIN-138 | REQ-FIN-034 | SCR-FIN-007 | — |
| AC-FIN-035 | TC-FIN-139 | REQ-FIN-035 | SCR-FIN-007 | RULE-FIN-014 → FIN-409-NOT-REOPENABLE |
| AC-FIN-036 | TC-FIN-140 | REQ-FIN-036 | SCR-FIN-007, SCR-FIN-006 | — |
| AC-FIN-037 | TC-FIN-141 | REQ-FIN-037 | SCR-FIN-007 | — |
| AC-FIN-038 | TC-FIN-142 | REQ-FIN-038 | SCR-FIN-007 | RULE-FIN-015 → FIN-403-FORBIDDEN |
| AC-FIN-039 | TC-FIN-143 | REQ-FIN-039 | SCR-FIN-008 | — |
| AC-FIN-040 | TC-FIN-144 | REQ-FIN-040 | SCR-FIN-009 | — |
| AC-FIN-041 | TC-FIN-145 | REQ-FIN-041 | SCR-FIN-010 | — |
| AC-FIN-042 | TC-FIN-146 | REQ-FIN-042 | SCR-FIN-011 | — |
| AC-FIN-043 | TC-FIN-147 | REQ-FIN-043 | SCR-FIN-012 | — |
| AC-FIN-046 | TC-FIN-148 | REQ-FIN-046 | SCR-FIN-010, SCR-FIN-009, SCR-FIN-008, SCR-FIN-006 | — |

### AC covered on the backend track only — not a gap on this track

These acceptance criteria have no screen to exercise them: each is either a server-to-server
path or a deployment act, and the SRS traceability matrix maps the last two to
"— (onboarding, no screen)". Each is covered by its 1:1 test case in
`backend-test-plan-fin.md`.

| AC | REQ | Why no frontend case |
|---|---|---|
| AC-FIN-010 | REQ-FIN-010 | the engine builds the entry from an arriving event — API-FIN-020 is a host system's call and is drawn on no screen (ADR-FIN-007) |
| AC-FIN-011 | REQ-FIN-011 | duplicate event reference — refused to the calling system, not to a screen |
| AC-FIN-012 | REQ-FIN-012 | the remainder line's rounding arithmetic — computed server-side during the build |
| AC-FIN-013 | REQ-FIN-013 | an event type with no active rule — answered to the calling system; the SRS declares no failure-queue entity for a screen to show |
| AC-FIN-024 | REQ-FIN-024 | the automatic next-period reversal of a reversing template — posted server-side, with no user action to exercise |
| AC-FIN-044 | REQ-FIN-044 | onboarding: FIN registers its module, screens and actions into the security module (no screen — SRS traceability matrix) |
| AC-FIN-045 | REQ-FIN-045 | onboarding: FIN registers its 13 lookup types into the lookup module (no screen — SRS traceability matrix) |

## COVERAGE

AC covered on this track: 39/46 — the seven above are backend-only by construction, and
46/46 across the module when both plans are read together (`backend-test-plan-fin.md` carries
one TC per AC for all 46).
REQ covered on this track: 39/46 — the same seven REQ ids, for the same reason.
SCR covered: 12/12 — every `SCR-FIN-001..012` is exercised by at least one case:
SCR-FIN-001 (3), SCR-FIN-002 (3), SCR-FIN-003 (3), SCR-FIN-004 (2), SCR-FIN-005 (2),
SCR-FIN-006 (12), SCR-FIN-007 (8), SCR-FIN-008 (2), SCR-FIN-009 (2), SCR-FIN-010 (2),
SCR-FIN-011 (2), SCR-FIN-012 (1) — the drill-down case counts on four of them.
UXD covered: not derived in this run — `INT-UXD` is an integration phase and this run is
`--module FIN`; the twelve `UXD-FIN-*` all name an owner module outside the selection.
TC count check (§3 over-engineering guard): 39 cases against 46 ACs is well under 2×, and no
case is a fabricated variant — every one derives from a distinct AC.
Scenario mix: HAPPY 20 · VIOLATION 9 · STATE 9 · PERMISSION 1 · BOUNDARY 0 (no AC or RULE in
FIN's set states a numeric limit, so §3 rule 3 adds none).

## NOTES

- Every message asserted above is copied character-perfect from `srs-fin.md` §A5 in both
  languages; no message is reworded and none is composed by a test.
- No test data is invented beyond the values the ACs themselves name (100.00 / 99.99,
  1,000.00 with 33% + 33% + remainder, the "NORTH" duplicate code).
- Three screen behaviours asserted here follow a recorded decision rather than a `RULE-*`, and
  each case says so where it matters: the report screens' single route (ADR-FIN-003), the
  absent Edit affordance on templates and allocation rules (ADR-FIN-006), and the fixed
  `MANUAL` journal type on the entry form (ADR-FIN-008).
- `test-execution-manifest-fin.md` is a derived view of the **backend** plan and its API set.
  Neither changed in this run, so it is current and is not rewritten.
══════════════════════════════════════════════════════════════════
