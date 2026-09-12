<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-010 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-041, AC-FIN-046, API-FIN-030, REQ-FIN-041, REQ-FIN-046, SCR-FIN-010, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F1-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F1 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F1-MODEL — BalanceSheetResponse — الميزانية العمومية / Balance sheet
Source DTO   : `BalanceSheetResponse` (read only)
  fiscalYearId : number · read-only — echoed from the request
  asOfDate     : date · read-only — echoed from the request
  groups[]     : AccountBalanceGroupResponse —
    accountTypeCode : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001); the section
    groupTotal      : number · read-only
    rows[]          : AccountBalanceRowResponse — the same row model as SCR-FIN-009, including
                      natureCode · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
### F1-SCREEN — SCR-FIN-010
Search model : query params — fiscalYearId : number · EXACT · **required** ·
               asOfDate : date · optional cut-off. Both in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
The grouping is the server's: `groups[]` arrives already keyed by account type with its total,
and no client-side grouping or subtotal is modelled. The continuity REQ-FIN-041 asserts is a
property of the posted data, not of this model — the opening balances are ordinary posted
lines of the year-end close entries.

<!-- SUB:F1-SCR-FIN-010:END -->
