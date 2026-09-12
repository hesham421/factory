<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-009 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-040, AC-FIN-046, API-FIN-029, REQ-FIN-040, REQ-FIN-046, SCR-FIN-009, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F1-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F1 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F1-MODEL — TrialBalanceResponse — ميزان المراجعة / Trial balance
Source DTO   : `TrialBalanceResponse` (read only)
  periodId            : number · read-only — echoed from the request
  accountTypeCode     : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001)
  totalDebitBalance   : number · read-only
  totalCreditBalance  : number · read-only
  balanced            : boolean · read-only — the property REQ-FIN-040 asserts
  rows[]              : AccountBalanceRowResponse —
    accountId, accountCode : number, string · read-only
    accountNameAr, accountNameEn : string · read-only
    accountTypeCode : string · read-only · lookup (UXD-FIN-001)
    natureCode      : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    debitTotal, creditTotal, debitBalance, creditBalance, signedBalance : number · read-only
### F1-SCREEN — SCR-FIN-009
Search model : query params — periodId : number · EXACT · optional · accountTypeCode : string ·
               EXACT · optional. Both live in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`balanced` is the server's assertion and is modelled as such; the screen renders it and never
derives it by comparing the two totals itself. `AccountBalanceRowResponse` is shared with
SCR-FIN-010 and SCR-FIN-011 and is modelled once.

<!-- SUB:F1-SCR-FIN-009:END -->
