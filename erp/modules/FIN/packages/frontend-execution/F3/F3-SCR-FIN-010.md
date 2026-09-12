<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-010 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-041, AC-FIN-046, API-FIN-030, REQ-FIN-041, REQ-FIN-046, SCR-FIN-010, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F3-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F3 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-010 (filters, not a form)
fiscalYearId · REQUIRED (the endpoint's required query param) — the report does not run until
               it is chosen, and the screen shows its choose-a-year state instead of a blank
               statement
asOfDate     · optional cut-off
Validation shape : filter validation only, over the route's search params.
No RULE-* is enforced on this screen. REQ-FIN-041's continuity is a property of the posted
data — the prior year's closing balances are the opening entry's posted lines — and nothing
here asserts or recomputes it.
`FIN-404-YEAR` is shown as a user message when the year in the address does not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-010:END -->
