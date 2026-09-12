<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-009 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-040, AC-FIN-046, API-FIN-029, REQ-FIN-040, REQ-FIN-046, SCR-FIN-009, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F3-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F3 · SCR-FIN-009 — ميزان المراجعة / Trial balance

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-009 (filters, not a form)
periodId        · optional · the select is served by the shared fiscal-period query
accountTypeCode · optional · LOOKUP_VALID (`ACCOUNT_TYPE`, UXD-FIN-001) — the option list is
                  runtime-loaded, never a static list
Validation shape : filter validation only, over the route's search params. Both filters are
                  optional and the unfiltered request is valid, so there is no required-field
                  state to enforce.
No RULE-* is enforced on this screen. REQ-FIN-040's balance property is asserted by the server
and rendered from `balanced`; the client does not re-derive it, and there is no client-side
condition under which the screen would contradict the report.
`FIN-404-PERIOD` is shown as a user message when a supplied period id does not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-009:END -->
