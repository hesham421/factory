<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-012 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-043, API-FIN-032, REQ-FIN-043, SCR-FIN-012, UXD-FIN-002 -->
<!-- SUB:F1-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F1 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F1-MODEL — DimensionReportResponse — تقرير الأبعاد / Dimension report
Source DTO   : `DimensionReportResponse` (read only)
  dimensionId, dimensionValueId, periodId : number · read-only — echoed from the request
  rows[] : DimensionReportRowResponse —
    accountId, accountCode : number, string · read-only
    accountNameAr, accountNameEn : string · read-only
    natureCode : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    dimensionId, dimensionValueId : number · read-only
    dimensionValueCode : string · read-only
    dimensionValueNameAr, dimensionValueNameEn : string · read-only
    debitTotal, creditTotal, signedBalance : number · read-only
### F1-SCREEN — SCR-FIN-012
Search model : query params — dimensionId : number · EXACT · **required** ·
               dimensionValueId : number · EXACT · optional · periodId : number · EXACT ·
               optional. All three in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
The row is keyed by account **and** dimension value together — that pair is the model's unit,
which is how REQ-FIN-043's "never by the base account alone" is expressed in the type rather
than only in the rendering. The dimension value's names come from the row itself, so this
screen needs no dimension-value lookup hook.

<!-- SUB:F1-SCR-FIN-012:END -->
