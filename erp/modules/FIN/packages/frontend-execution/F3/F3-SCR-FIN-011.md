<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-011 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-042, AC-FIN-046, API-FIN-031, REQ-FIN-042, REQ-FIN-046, SCR-FIN-011, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F3-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F3 · SCR-FIN-011 — قائمة الدخل / Income statement

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-011 (filters, not a form)
fiscalYearId             · REQUIRED (the endpoint's required query param)
fromPeriodId, toPeriodId · optional · both selects narrowed to the chosen year, and
                           `toPeriodId` not before `fromPeriodId`
Validation shape : filter validation only, over the route's search params. The date bounds are
                   NOT validated here: the server derives `fromDate`/`toDate` from the chosen
                   periods and returns them, so the client has nothing of its own to check.
No RULE-* is enforced on this screen. REQ-FIN-042's "opens at zero" is the server's result for
a freshly closed year, and the screen labels an all-zero statement as such rather than treating
it as an absence of data.
`FIN-404-YEAR` and `FIN-404-PERIOD` are shown as user messages when an id in the address does
not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-011:END -->
