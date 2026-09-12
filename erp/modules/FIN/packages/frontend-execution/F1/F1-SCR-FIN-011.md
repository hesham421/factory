<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-011 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-042, AC-FIN-046, API-FIN-031, REQ-FIN-042, REQ-FIN-046, SCR-FIN-011, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F1-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F1 · SCR-FIN-011 — قائمة الدخل / Income statement

### F1-MODEL — IncomeStatementResponse — قائمة الدخل / Income statement
Source DTO   : `IncomeStatementResponse` (read only)
  fiscalYearId             : number · read-only — echoed from the request
  fromPeriodId, toPeriodId : number · read-only — echoed from the request
  fromDate, toDate         : date · read-only — derived by the server from those two periods
  netResult                : number · read-only
  groups[]                 : AccountBalanceGroupResponse — accountTypeCode (lookup,
                             UXD-FIN-001) · groupTotal · rows[] (AccountBalanceRowResponse,
                             natureCode lookup UXD-FIN-002)
### F1-SCREEN — SCR-FIN-011
Search model : query params — fiscalYearId : number · EXACT · **required** ·
               fromPeriodId, toPeriodId : number · EXACT · optional. All three in the route's
               search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`fromDate`/`toDate` are modelled as read-only server output, not as inputs: the request takes
period ids and the server translates them into the date bounds those periods span. A statement
of zeros for a freshly closed year is a correct result (REQ-FIN-042), and nothing in this model
treats it as an absence of data.

<!-- SUB:F1-SCR-FIN-011:END -->
