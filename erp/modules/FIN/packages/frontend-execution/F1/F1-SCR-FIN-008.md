<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-008 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-039, AC-FIN-046, API-FIN-028, REQ-FIN-039, REQ-FIN-046, SCR-FIN-008, UXD-FIN-001, UXD-FIN-002, UXD-FIN-005 -->
<!-- SUB:F1-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F1 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F1-MODEL — AccountLedgerResponse — دفتر الحساب / Account ledger
Source DTO   : `AccountLedgerResponse` (read only — this screen writes nothing)
  accountId, accountCode        : number, string · read-only
  accountNameAr, accountNameEn  : string · read-only
  accountTypeCode               : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001)
  natureCode                    : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
  fromDate, toDate              : date · read-only — echoed from the request
  dimensionId, dimensionValueId : number · read-only — echoed from the request
  debitTotal, creditTotal       : number · read-only
  closingBalance                : number · read-only
  rows[]                        : AccountLedgerRowResponse —
    journalEntryId : number · read-only — the link target on SCR-FIN-006
    docNo          : string · read-only
    docDate        : date · read-only
    journalTypeCode: string · read-only · lookup — `JOURNAL_TYPE` (UXD-FIN-005)
    eventReference : string · read-only — the end of the REQ-FIN-046 chain
    journalLineId, lineNo : number · read-only
    amount         : number · read-only
    directionCode  : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    signedAmount   : number · read-only
    runningBalance : number · read-only — computed by the server, never accumulated on the client
    descriptionAr, descriptionEn : string · read-only
### F1-SCREEN — SCR-FIN-008
Search model : query params — accountId : number · required · fromDate, toDate : date ·
               DATE_RANGE · dimensionId, dimensionValueId : number · EXACT — all five on the
               query string of a GET, so the report's address IS its filter
Form model   : none — a read-only report (SRS B3 "not applicable")
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`runningBalance` is modelled as a server field and is never recomputed client-side: the plan's
own accumulation could disagree with the ledger, which is exactly the class of defect
POL-FIN-009 exists to remove. This report is not paged — the endpoint returns the rows of the
requested range, and no `Page<T>` envelope appears in its response.

<!-- SUB:F1-SCR-FIN-008:END -->
