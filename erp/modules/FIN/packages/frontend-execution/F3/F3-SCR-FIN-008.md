<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-008 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-039, AC-FIN-046, API-FIN-028, REQ-FIN-039, REQ-FIN-046, SCR-FIN-008, UXD-FIN-001, UXD-FIN-002, UXD-FIN-005 -->
<!-- SUB:F3-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F3 · SCR-FIN-008 — دفتر الحساب / Account ledger

This screen has **no form**: SRS SCR-REQ-FIN-008 §B3 reads "not applicable — read-only
report", and every field of `AccountLedgerResponse` is read-only.
### F3-FIELD — SCR-FIN-008 (filters, not a form)
accountId        · REQUIRED (the endpoint's required query param) — the report does not run
                   without it, and the screen shows its choose-an-account state instead
fromDate, toDate · optional · DATE_RANGE (`toDate` not before `fromDate`)
dimensionId, dimensionValueId · optional · the value select is loaded from API-FIN-008
                   filtered by the chosen dimension, so it cannot offer a foreign value
Validation shape : filter validation only, written with `zod` over the route's search params
                   so that an address someone shared is validated the same way a typed filter
                   is. No business rule is enforced here, because nothing is written.
No RULE-* is enforced on this screen. `FIN-404-ACCOUNT` from the server is shown as a user
message when the account id in the address does not resolve — which is the case a shared link
to a since-deleted account produces.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen — the navigation
guard of SEC-FE stops the route (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-008:END -->
