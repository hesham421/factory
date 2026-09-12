# ADR-FIN-006 — operations the SRS names for which no endpoint is published are omitted, not faked

Module  : FIN     Version : v1     Stage raised : P3.2 (Frontend — UX Design + Execution Plan)
Status  : ACCEPTED (non-breaking)

## Context
`srs-fin.md` Part B names several operations that `_inputs/api-docs-fin.md` publishes no
endpoint for. The SRS itself records each one and why, at the §B4 of the screen that owns it;
this ADR is the frontend's single place of record for the set:

| Operation | Screen | SRS record |
|---|---|---|
| update a recurring/reversing template | SCR-FIN-004 | §B4 "OPEN DEFECT — `update` (template) is still missing" |
| update an allocation rule | SCR-FIN-005 | §B4 "OPEN DEFECT — `update` (rule) is still missing" |
| search fiscal years | SCR-FIN-007 | §B5 "KNOWN GAP … there is no fiscal-year search" |
| read one account / template / allocation rule / fiscal year / fiscal period by id | SCR-FIN-001, 004, 005, 007 | §B4/§B5 "deliberate v1 exclusion" — the search result already carries the full record |
| delete a rule line, a template line, an allocation target | SCR-FIN-003, 004, 005 | §B4 "FIN publishes no `DELETE` endpoint on any screen" |
| deactivate the parent Dimension | SCR-FIN-002 | §B4 "deliberately has no deactivate" |

Two of these are recorded by the SRS as real gaps (template update, allocation-rule update);
the rest are reasoned v1 exclusions. Either way the frontend faces the same question.

## Decision
No affordance is drawn for an operation with no published endpoint. A screen shows what it
can really do: a template or an allocation rule created with wrong content can be retired
(API-FIN-036, API-FIN-037) and not corrected, and the screen says so in its empty-state and
row affordances rather than offering an Edit that would have nowhere to go.

Where a by-id read is absent, the entry hydrates from the row the search query already holds
in cache — the search responses of API-FIN-001, API-FIN-012 and API-FIN-015 carry the full
record, lines and targets included, so no second read is needed and an invalidation re-reads
through the same key. SCR-FIN-006 is the exception and reads by id (API-FIN-022), because a
journal entry's lines are what REQ-FIN-016 and REQ-FIN-027 need and the search result is the
place they would otherwise have to come from.

Fiscal-year ids are discovered from `fiscalYearId` on the fiscal-period rows API-FIN-033
returns, which is the path the SRS §B5 names; no year-search call is invented.

## Consequences
- The operations coverage table in the plan's ALIGN-FE section carries a `✗` row with this
  ADR for each omitted operation — a `✗` for a missing endpoint, never for a missing decision.
- If a template-update or rule-update endpoint is later published, the screen gains an Edit
  affordance and this ADR is superseded for that row; no other part of the plan changes.
- No `REQ-*` is unmet by the omission: none of the six operations is required by a `REQ-*`
  (the SRS states this per screen), which is why each is non-breaking.
