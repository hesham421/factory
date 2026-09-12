<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-011 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-042, AC-FIN-045, AC-FIN-046, API-FIN-031, REQ-FIN-042, REQ-FIN-045, REQ-FIN-046, SCR-FIN-011, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F2-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-011 — قائمة الدخل / Income statement

### F2-QUERY — API-FIN-031            traces=API-FIN-031,REQ-FIN-042,REQ-FIN-046
GET `/api/v1/fin/reports/income-statement` · query params `fiscalYearId` (**required**),
`fromPeriodId` (optional), `toPeriodId` (optional) · response `IncomeStatementResponse` with
its `groups[]` · kind **read query**
Cache key    : `[reports, income-statement, filters]` — all three params
Enabled      : only once a fiscal year is chosen, as on SCR-FIN-010
Errors       : `FIN-404-YEAR` (404) → user message (the required keying id) ·
               `FIN-404-PERIOD` (404) → user message, raised only when a period id is supplied
               and does not resolve · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
The same two shared hooks (UXD-FIN-001, UXD-FIN-002).
### F2-SCREEN-INIT — SCR-FIN-011
Permission read : `FIN_INCOME_STATEMENT` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (section headings), DEBIT_CREDIT (row nature)
Entity by id    : none
Year + periods  : both selects served by the shared fiscal-period query (API-FIN-033); the
                  period selects are narrowed to the chosen year by the same filter object
### F2-FACADE — SCR-FIN-011
Composes     : API-FIN-031 · the fiscal-period hook · the two lookup hooks
State it owns: the filter object (fiscal year, from period, to period) mirrored from the
               route's search params, and a derived loading flag. `fromDate`, `toDate` and
               `netResult` are read from the response, never computed here
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-011:END -->
