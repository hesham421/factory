<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-008 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-039, AC-FIN-045, AC-FIN-046, API-FIN-028, REQ-FIN-039, REQ-FIN-045, REQ-FIN-046, SCR-FIN-008, UXD-FIN-001, UXD-FIN-002, UXD-FIN-005 -->
<!-- SUB:F2-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F2-QUERY — API-FIN-028            traces=API-FIN-028,REQ-FIN-039,REQ-FIN-046
GET `/api/v1/fin/reports/account-ledger` · query params `accountId` (required), `fromDate`,
`toDate`, `dimensionId`, `dimensionValueId` · response `AccountLedgerResponse` with its
`rows[]` · kind **read query**
Cache key    : `[reports, account-ledger, filters]` where `filters` carries all five params.
               Every parameter that changes the response is in the key; this report is not
               paged, so no page or size belongs in it.
Errors       : `FIN-404-ACCOUNT` (404) → user message (the keying id did not resolve) ·
               validation (400) → inline on the offending parameter ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message
Loading      : LOCAL
Cache policy : defaults, and the key is in the `[reports, *]` family every posting mutation
               invalidates — a ledger computed live from posted lines is stale the moment
               anything posts [POL-FIN-009]
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT · JOURNAL_TYPE
Keys `ACCOUNT_TYPE` (UXD-FIN-001) · `DEBIT_CREDIT` (UXD-FIN-002) · `JOURNAL_TYPE`
(UXD-FIN-005) — the same shared hooks the entry screens use; this screen adds no hook of its own.
### F2-SCREEN-INIT — SCR-FIN-008
Permission read : `FIN_ACCOUNT_LEDGER` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). This screen has no other action.
Lookups used    : ACCOUNT_TYPE, DEBIT_CREDIT, JOURNAL_TYPE (all display-only)
Entity by id    : none — the report's own response carries the account's identity
Account select  : served by the SCR-FIN-001 account search (API-FIN-001) through its shared
                  key; this screen declares the dependency and duplicates no call
### F2-FACADE — SCR-FIN-008
Composes     : API-FIN-028 · the account search for its account picker · the three lookup hooks
State it owns: the filter object (account, date range, dimension, dimension value) mirrored
               from the route's search params, and a derived loading flag. No running balance
               and no total is owned here: all three come from the response
Operations   : none — this screen writes nothing. Navigation to SCR-FIN-006 for a row's entry
               is a route change, not an operation

<!-- SUB:F2-SCR-FIN-008:END -->
