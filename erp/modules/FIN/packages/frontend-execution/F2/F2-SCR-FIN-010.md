<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-010 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-041, AC-FIN-045, AC-FIN-046, API-FIN-030, REQ-FIN-041, REQ-FIN-045, REQ-FIN-046, SCR-FIN-010, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F2-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F2-QUERY — API-FIN-030            traces=API-FIN-030,REQ-FIN-041,REQ-FIN-046
GET `/api/v1/fin/reports/balance-sheet` · query params `fiscalYearId` (**required**),
`asOfDate` (optional) · response `BalanceSheetResponse` with its `groups[]` ·
kind **read query**
Cache key    : `[reports, balance-sheet, filters]` — both params
Enabled      : only once a fiscal year is chosen — the query does not run with an absent
               required parameter, and the screen shows its choose-a-year state instead of a
               failed request
Errors       : `FIN-404-YEAR` (404) → user message (the required keying id did not resolve) ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
The same two shared hooks (UXD-FIN-001, UXD-FIN-002); the account type labels the section
headings the response groups by.
### F2-SCREEN-INIT — SCR-FIN-010
Permission read : `FIN_BALANCE_SHEET` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (section headings), DEBIT_CREDIT (row nature)
Entity by id    : none
Year select     : derived from the `fiscalYearId` of the shared fiscal-period query's rows
                  (API-FIN-033), since no fiscal-year search is published (ADR-FIN-006)
### F2-FACADE — SCR-FIN-010
Composes     : API-FIN-030 · the fiscal-period hook for its year select · the two lookup hooks
State it owns: the filter object (fiscal year, as-of date) mirrored from the route's search
               params, and a derived loading flag. No group total and no section is composed
               here — both arrive in the response
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-010:END -->
