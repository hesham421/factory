<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
# FRONTEND TEST PLAN — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Scope : module (SEC)
Sources: srs-sec.md v1 · frontend-execution-plan-sec.md v1 · registry-srs-sec.md v1 ·
         registry-exec-fe-sec.md v1
Framework: agnostic (profile.stack.testing.frontend). REDUCED: **no** — P3.2 has run for SEC,
so every test case below binds to a real `SCR-*` and its route.
TC count: 30 — TC-SEC-034 … TC-SEC-063, continuing the module's one TC sequence after the
backend plan's highest id (TC-SEC-033). No id is renumbered and no backend TC is touched.
Open ADRs: 0 new. The plan cites ADR-SEC-005, ADR-SEC-008 and ADR-SEC-009 where a screen's
behaviour follows one of them.
SUPERSEDES the REDUCED stub this file previously held, which recorded that P3.2 had not run
for SEC and that no version of the frontend execution plan existed. That is no longer true:
SCR-SEC-001..010 exist and the plan binds all 27 API ids.
══════════════════════════════════════════════════════════════════

Scope is `module`, so this run derives from SEC's own `AC-*` only. The integration phase
`INT-UXD` is **absent by rule**, and for SEC it could never be otherwise: the module mints no
`UXD-*` at all, because SRS §A8 records it as ROOT — it consumes no entity owned by another
module, so no screen of its displays foreign data.



## TC TRACEABILITY INDEX

| AC | TC | REQ | SCR | RULE / code |
|---|---|---|---|---|
| AC-SEC-001 | TC-SEC-034 | REQ-SEC-001 | SCR-SEC-001 | — |
| AC-SEC-002 | TC-SEC-035 | REQ-SEC-002 | SCR-SEC-001 | SEC-401-INVALID-CREDENTIALS |
| AC-SEC-003 | TC-SEC-036 | REQ-SEC-003 | SCR-SEC-002 | — |
| AC-SEC-006 | TC-SEC-037 | REQ-SEC-006 | SCR-SEC-003 | — |
| AC-SEC-007 | TC-SEC-038 | REQ-SEC-007 | SCR-SEC-003 | — |
| AC-SEC-008 | TC-SEC-039 | REQ-SEC-008 | SCR-SEC-003 | RULE-SEC-006 → SEC-409-RESET-TOKEN-INVALID |
| AC-SEC-004 | TC-SEC-040 | REQ-SEC-004 | SCR-SEC-004 | — |
| AC-SEC-005 | TC-SEC-041 | REQ-SEC-005 | SCR-SEC-004 | — |
| AC-SEC-009 | TC-SEC-042 | REQ-SEC-009 | SCR-SEC-004 | SEC-409-USER-DUP |
| AC-SEC-010 | TC-SEC-043 | REQ-SEC-010 | SCR-SEC-004 | — |
| AC-SEC-011 | TC-SEC-044 | REQ-SEC-011 | SCR-SEC-004 | — |
| AC-SEC-031 | TC-SEC-045 | REQ-SEC-031 | SCR-SEC-004 | — |
| AC-SEC-012 | TC-SEC-046 | REQ-SEC-012 | SCR-SEC-005 | — |
| AC-SEC-013 | TC-SEC-047 | REQ-SEC-013 | SCR-SEC-005 | RULE-SEC-001 → SEC-409-NO-MODULE-GRANT |
| AC-SEC-014 | TC-SEC-048 | REQ-SEC-014 | SCR-SEC-005 | RULE-SEC-002 → SEC-409-NO-SCREEN-GRANT |
| AC-SEC-015 | TC-SEC-049 | REQ-SEC-015 | SCR-SEC-005 | RULE-SEC-003 |
| AC-SEC-020 | TC-SEC-050 | REQ-SEC-020 | SCR-SEC-005 | RULE-SEC-005 → SEC-409-SOD-CONFLICT |
| AC-SEC-030 | TC-SEC-051 | REQ-SEC-030 | SCR-SEC-005 | RULE-SEC-007 → SEC-409-NO-VIEW-GRANT |
| AC-SEC-016 | TC-SEC-052 | REQ-SEC-016 | SCR-SEC-006 | — |
| AC-SEC-017 | TC-SEC-053 | REQ-SEC-017 | SCR-SEC-006 | — |
| AC-SEC-019 | TC-SEC-054 | REQ-SEC-019 | SCR-SEC-006 | — |
| AC-SEC-022 | TC-SEC-055 | REQ-SEC-022 | SCR-SEC-007 | — |
| AC-SEC-025 | TC-SEC-056 | REQ-SEC-025 | SCR-SEC-008 | — |
| AC-SEC-026 | TC-SEC-057 | REQ-SEC-026 | SCR-SEC-008 | — |
| AC-SEC-027 | TC-SEC-058 | REQ-SEC-027 | SCR-SEC-009 | — |
| AC-SEC-028 | TC-SEC-059 | REQ-SEC-028 | SCR-SEC-009 | — |
| AC-SEC-021 | TC-SEC-060 | REQ-SEC-021 | SCR-SEC-010 | — |
| AC-SEC-032 | TC-SEC-061 | REQ-SEC-032 | SCR-SEC-010 | — |
| AC-SEC-033 | TC-SEC-062 | REQ-SEC-033 | SCR-SEC-010 | — |
| AC-SEC-023 | TC-SEC-063 | REQ-SEC-023 | SCR-SEC-007, SCR-SEC-009 | — |

### AC covered on the backend track only — not a gap on this track

| AC | REQ | Why no frontend case |
|---|---|---|
| AC-SEC-018 | REQ-SEC-018 | a screen registration naming an unregistered module is refused — the refusal is answered to the registering module's own call, which no screen makes (ADR-SEC-009); SCR-SEC-006 is read-only |
| AC-SEC-024 | REQ-SEC-024 | the audit entry is appended by the server when an event completes; no client call or affordance writes one, and the frontend's assertable half is the filtered read (TC-SEC-056) |
| AC-SEC-029 | REQ-SEC-029 | the password-reset notification is dispatched entirely server-side when a token is issued — SEC's own F2 block records that no client call, state or affordance represents it |

## COVERAGE

AC covered on this track: 30/33 — the three above are backend-only by construction, and 33/33
across the module when both plans are read together (`backend-test-plan-sec.md` carries one TC
per AC for all 33).
REQ covered on this track: 30/33 — the same three REQ ids, for the same reason.
SCR covered: 10/10 — SCR-SEC-001 (2), SCR-SEC-002 (1), SCR-SEC-003 (3), SCR-SEC-004 (6),
SCR-SEC-005 (6), SCR-SEC-006 (3), SCR-SEC-007 (2), SCR-SEC-008 (2), SCR-SEC-009 (3),
SCR-SEC-010 (3) — the conflicting-assignment and dashboard-widget cases each touch two screens.
UXD covered: not applicable — SEC mints no `UXD-*` (SRS §A8: ROOT, no consumed entity), so
there is nothing for an integration phase to derive even at project scope.
TC count check (§3 over-engineering guard): 30 cases against 33 ACs is well under 2×, and no
case is a fabricated variant — every one derives from a distinct AC.
Scenario mix: HAPPY 13 · VIOLATION 5 · STATE 8 · PERMISSION 4 · BOUNDARY 0 (no AC or RULE in
SEC's set states a numeric limit, so §3 rule 3 adds none).

## NOTES

- Every message asserted above is copied character-perfect from `srs-sec.md` in both languages;
  no message is reworded and none is composed by a test.
- TC-SEC-035 is one case with three attempts on purpose: AC-SEC-002 gives ONE message for a
  wrong password, an unknown username and a disabled one, and a test that checked only the
  first would pass against a screen that leaked the difference in the other two.
- TC-SEC-062 asserts both halves of REQ-SEC-033 — the route guard AND the server's independent
  denial — because the menu's omission is not the enforcement, and a test that checked only the
  guard would pass against a client-only gate.
- TC-SEC-047, TC-SEC-048 and TC-SEC-051 assert that a grant refusal renders as its own rule
  message rather than the generic forbidden message: these are authorization outcomes the
  administrator is editing, not authorization failures of the administrator.
- `test-execution-manifest-sec.md` is a derived view of the **backend** plan and its API set.
  Neither changed in this run, so it is current and is not rewritten.
══════════════════════════════════════════════════════════════════
