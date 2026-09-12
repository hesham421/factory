<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-012 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-043, API-FIN-032, REQ-FIN-043, SCR-FIN-012, UXD-FIN-002 -->
<!-- SUB:F3-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F3 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-012 (filters, not a form)
dimensionId      · REQUIRED (the endpoint's required query param) — the report does not run
                   until a dimension is chosen
dimensionValueId · optional · the select is loaded from API-FIN-008 filtered by the chosen
                   dimension, so it cannot offer a value of another dimension
periodId         · optional · served by the shared fiscal-period query
Validation shape : filter validation only, over the route's search params.
No RULE-* is enforced on this screen. REQ-FIN-043's "never by the base account alone" is a
property of the rows the server returns — one per account-and-dimension-value pair — and the
screen neither merges nor re-aggregates them.
`FIN-404-DIMENSION` and `FIN-404-PERIOD` are shown as user messages when an id in the address
does not resolve.
Business-code fields: `accountCode` and `dimensionValueCode` are displayed read-only, from the
response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-012:END -->
