<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-007 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-031, AC-FIN-032, AC-FIN-033, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-037, AC-FIN-038, AC-FIN-045, API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026, API-FIN-027, API-FIN-033, REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038, REQ-FIN-045, SCR-FIN-007, UXD-FIN-003, UXD-FIN-004 -->
<!-- SUB:F2-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F2-QUERY — API-FIN-033            traces=API-FIN-033,REQ-FIN-031
POST `/api/v1/fin/fiscal-periods/search` · request `FiscalPeriodSearchRequest` { filters[]
optionally carrying `fiscalYearId` and `statusCode`, sortField, sortDirection, page, size } ·
response `Page<FiscalPeriodResponse>` · kind **read query**
Cache key    : `[fiscal-periods, filters]` — fiscalYearId, statusCode, sort **and page, size**.
               Omitting the year is a legitimate "all periods" request and is its own key.
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026 and API-FIN-027
This query is also the shared source of the period select on SCR-FIN-006's entry form and of
the period filters on SCR-FIN-009 and SCR-FIN-011 — one hook, one key, no duplicate call.
### F2-QUERY — API-FIN-023            traces=API-FIN-023,REQ-FIN-031
POST `/api/v1/fin/fiscal-years` · request `FiscalYearCreateRequest` { code, startDate, endDate,
periodCount } · response `FiscalYearResponse` with its generated `periods[]` · kind **mutation**
Errors       : `FIN-409-YEAR-DUP` (409) → inline on `code` · validation (400) → inline per
               field · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[fiscal-periods, *]` — the new year's periods must appear in every period list
### F2-QUERY — API-FIN-024            traces=API-FIN-024,REQ-FIN-032,REQ-FIN-035
PATCH `/api/v1/fin/fiscal-periods/{id}/open` · no request body · response
`FiscalPeriodResponse` · kind **mutation**
Errors       : `FIN-409-NOT-REOPENABLE` (409) [RULE-FIN-014] → user message,
               ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" ·
               en: "The period is hard-closed and cannot be reopened" ·
               `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-025            traces=API-FIN-025,REQ-FIN-033
PATCH `/api/v1/fin/fiscal-periods/{id}/soft-close` · no request body · response
`FiscalPeriodResponse` · kind **mutation**
Errors       : `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-026            traces=API-FIN-026,REQ-FIN-034,REQ-FIN-037,REQ-FIN-038
PATCH `/api/v1/fin/fiscal-periods/{id}/hard-close` · no request body · response
`FiscalPeriodResponse` (with `closedBy` and `closedAt` set) · kind **mutation**
Errors       : `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message — this is the
               refusal a caller without `PERM_FIN_PERIODS_CLOSE_APPROVE` receives, and it is
               the visible half of RULE-FIN-015
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-027            traces=API-FIN-027,REQ-FIN-036
POST `/api/v1/fin/fiscal-years/{id}/year-end-close` · no request body ·
response `YearEndCloseResponse` { closingEntry, openingEntry } · kind **mutation**
Errors       : `FIN-409-PERIODS-NOT-CLOSED` (409) → user message (not every period of the year
               is hard-closed) · `FIN-404-YEAR` / `FIN-404-PERIOD` / `FIN-404-ACCOUNT` (404) →
               user message (the last covers a ledger with no account marked as retained
               earnings) · `FIN-409-UNBALANCED`, `FIN-409-NOT-POSTABLE-ACCOUNT`,
               `FIN-409-INVALID-DIMENSION` (409) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : GLOBAL — the only GLOBAL indicator in this plan. The call computes every
               balance-sheet balance of the year and posts two entries; the SRS describes it
               as the year's terminal act (REQ-FIN-036), and a screen-local spinner would
               leave the rest of the application looking usable while the ledger's year is
               being closed underneath it
Invalidation : `[fiscal-periods, *]`, `[journal-entries, *]` and `[reports, *]`
### F2-LOOKUP — PERIOD_STATE · FISCAL_YEAR_STATUS
Keys `PERIOD_STATE` (UXD-FIN-003) · `FISCAL_YEAR_STATUS` (UXD-FIN-004) — one shared hook per
key, `{ code, labelAr, labelEn }`, long-lived cache. The labels come from the lookup; which
transitions a row offers comes from SRS §A7, not from the lookup's value list.
### F2-SCREEN-INIT — SCR-FIN-007
Permission read : `FIN_PERIODS` present in the caller's effective menu → VIEW (ADR-FIN-005).
                  `PERM_FIN_PERIODS_CLOSE_APPROVE` is not readable from any published
                  endpoint, so the hard-close and year-end-close affordances render and the
                  server's 403 is the authority (ADR-FIN-005).
Lookups used    : PERIOD_STATE (row status + filter), FISCAL_YEAR_STATUS (year header)
Entity by id    : none published for either resource — the period rows come from API-FIN-033
                  and the year from the API-FIN-023 response and from the rows' `fiscalYearId`
                  (ADR-FIN-006)
### F2-FACADE — SCR-FIN-007
Composes     : API-FIN-033 (period list) · API-FIN-023, API-FIN-024, API-FIN-025,
               API-FIN-026, API-FIN-027 (mutations) · the two lookup hooks
State it owns: the period list from the query's data, the year list derived from those rows'
               `fiscalYearId`, the selected year id (route param), the filter object including
               page and size, the create-year draft, and a derived loading flag
Operations   : createYear · openPeriod · softClosePeriod · hardClosePeriod (confirmation using
               the word permanent — RULE-FIN-014) · runYearEndClose (confirmation; on success
               the two returned entries are offered on SCR-FIN-006)

<!-- SUB:F2-SCR-FIN-007:END -->
