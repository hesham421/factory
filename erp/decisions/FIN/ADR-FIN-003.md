# ADR-FIN-003 — container pattern for the five report screens, which have no entry sub-view

Module  : FIN     Version : v1     Stage raised : P3.2 (Frontend — UX Design + Execution Plan)
Status  : ACCEPTED (non-breaking)

## Context
§A.4's container-pattern decision order is written for entry screens: it chooses between
`TREE_MASTER_DETAIL`, `FULL_PAGE` and `SIDE_DRAWER` by the shape of the data a user edits.
Five FIN screens edit nothing at all — SCR-FIN-008 (account ledger), SCR-FIN-009 (trial
balance), SCR-FIN-010 (balance sheet), SCR-FIN-011 (income statement) and SCR-FIN-012
(dimension reports). Each is a read-only report: the SRS marks their B3 "not applicable" and
their B1 "single screen (report; no entry)", and each is served by exactly one `GET` endpoint
(API-FIN-028, API-FIN-029, API-FIN-030, API-FIN-031, API-FIN-032). Running the decision order
over them asks which pattern hosts a form that does not exist.

## Decision
A screen with no entry sub-view carries `FULL_PAGE`, stated as
`FULL_PAGE (no entry sub-view — ADR-FIN-003)`, and no fourth pattern is invented. The three
`SIDE_DRAWER` / `TREE_MASTER_DETAIL` / `FULL_PAGE` values stay exactly as §A.4 defines them
for the seven screens that do have an entry.

## Consequences
- The five report screens each get one route and one lazy chunk, with no `new`, `:id` or
  `:id/edit` route and no drawer.
- Their filter state is mirrored into the route's search params so a filtered report is
  linkable — the drill-down chain REQ-FIN-046 asks for (statement line → trial balance →
  account ledger → entry) is navigation between screens, and each hop must be addressable.
- Nothing about the entry screens' patterns changes, and no `REQ-*` is affected.
