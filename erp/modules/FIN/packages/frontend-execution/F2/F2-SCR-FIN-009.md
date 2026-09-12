<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-009 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-040, AC-FIN-045, AC-FIN-046, API-FIN-029, REQ-FIN-040, REQ-FIN-045, REQ-FIN-046, SCR-FIN-009, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F2-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F2-QUERY — API-FIN-029            traces=API-FIN-029,REQ-FIN-040,REQ-FIN-046
GET `/api/v1/fin/reports/trial-balance` · query params `periodId` (optional),
`accountTypeCode` (optional) · response `TrialBalanceResponse` with its `rows[]` ·
kind **read query**
Cache key    : `[reports, trial-balance, filters]` — both params, and the unfiltered request is
               its own key rather than a variant of a filtered one
Errors       : `FIN-404-PERIOD` (404) → user message, raised only when `periodId` is supplied
               and does not resolve; omitting it stays a valid whole-ledger request ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
Keys `ACCOUNT_TYPE` (UXD-FIN-001, also the filter's option list) · `DEBIT_CREDIT`
(UXD-FIN-002) — the same shared hooks; no new hook here.
### F2-SCREEN-INIT — SCR-FIN-009
Permission read : `FIN_TRIAL_BALANCE` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (filter + display), DEBIT_CREDIT (display)
Entity by id    : none
Period select   : served by the shared fiscal-period query (API-FIN-033) of SCR-FIN-007
### F2-FACADE — SCR-FIN-009
Composes     : API-FIN-029 · the fiscal-period hook for its period select · the two lookup hooks
State it owns: the filter object (period, account type) mirrored from the route's search
               params, and a derived loading flag. `balanced` and both totals are read from the
               response and never derived here
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-009:END -->
