<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-006 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-010, AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-014, AC-FIN-015, AC-FIN-016, AC-FIN-017, AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-027, AC-FIN-028, AC-FIN-029, AC-FIN-030, AC-FIN-045, API-FIN-018, API-FIN-019, API-FIN-020, API-FIN-021, API-FIN-022, REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-045, SCR-FIN-006, UXD-FIN-002, UXD-FIN-005, UXD-FIN-006 -->
<!-- SUB:F2-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-006 — قيود اليومية / Journal entries

### F2-QUERY — API-FIN-018            traces=API-FIN-018,REQ-FIN-027
POST `/api/v1/fin/journal-entries/search` · request `JournalEntrySearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<JournalEntryResponse>` ·
kind **read query**
Cache key    : `[journal-entries, filters]` — docNo, docDate range, periodId, statusCode,
               journalTypeCode, sort **and page, size**, all inside the one filter object
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-019 and API-FIN-021, and by the two run endpoints of
               SCR-FIN-004 and SCR-FIN-005 and the year-end close of SCR-FIN-007
### F2-QUERY — API-FIN-022            traces=API-FIN-022,REQ-FIN-016,REQ-FIN-027
GET `/api/v1/fin/journal-entries/{id}` · response `JournalEntryResponse` with its `lines[]`
and each line's `dimensions[]` · kind **read query**
Cache key    : `[journal-entry, id]`
Errors       : `FIN-404-ENTRY` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults — a POSTED entry is immutable (RULE-FIN-016), so a cached one cannot
               go stale except through its own reversal link, which API-FIN-021 invalidates
Invalidation : n/a (a read); invalidated by API-FIN-021 for the reversed original
This is the one by-id read in the module, and it exists because the search result is not where
REQ-FIN-016 and REQ-FIN-027 read an entry's lines from.
### F2-QUERY — API-FIN-019            traces=API-FIN-019,REQ-FIN-014,REQ-FIN-015,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021
POST `/api/v1/fin/journal-entries` · request `JournalEntryCreateRequest` { docDate,
fiscalYearId, periodId, journalTypeCode, descriptionAr?, descriptionEn?, lines[] { accountId,
amount, directionCode, descriptionAr?, descriptionEn?, dimensions[] { dimensionId,
dimensionValueId } } } · response `JournalEntryResponse` (POSTED) · kind **mutation**
Errors       : every automatic check REQ-FIN-015 asks to be shown, each routed to the line or
               field it names and all shown together rather than one at a time —
               `FIN-409-UNBALANCED` (409) [RULE-FIN-006],
               ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" ·
               en: "The entry is unbalanced — total debits do not equal total credits" ·
               `FIN-409-NOT-POSTABLE-ACCOUNT` (409) [RULE-FIN-007],
               ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" ·
               en: "The target account does not accept direct posting" — routed to the line ·
               `FIN-409-PERIOD-NOT-OPEN` (409) [RULE-FIN-008],
               ar: "الفترة المستهدفة غير مفتوحة" · en: "The target period is not open" ·
               `FIN-409-INVALID-DIMENSION` (409) [RULE-FIN-009],
               ar: "قيمة البُعد غير صالحة" · en: "The dimension value is invalid" ·
               `FIN-400-PERIOD-NOT-IN-YEAR` (400) and `FIN-400-DOCDATE-OUTSIDE-PERIOD` (400)
               [RULE-FIN-017] → inline on the period and the document date ·
               `FIN-404-ACCOUNT` / `FIN-404-PERIOD` / `FIN-404-YEAR` (404) → inline on the
               offending selection · validation (400) → inline per field ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL — the submit affordance is busy; the entry is not cleared
Invalidation : `[journal-entries, *]` and `[reports, *]`
### F2-QUERY — API-FIN-020            traces=API-FIN-020,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013
POST `/api/v1/fin/journal-entries/from-event` · request `EventEntryBuildRequest`
{ eventReference, eventTypeCode, docDate, baseAmount, amounts?, fields?, descriptionAr?,
descriptionEn? } · response `JournalEntryResponse` · kind **mutation**
**Bound, and called by no screen** (ADR-FIN-007): the caller is a host system over the
platform's in-process module interface, not a user with a form. It is stated here so the
published surface is completely accounted for.
Errors       : `FIN-404-NO-ACTIVE-RULE` (404) [RULE-FIN-005] · `FIN-409-DUPLICATE-EVENT` (409)
               [RULE-FIN-004] · `FIN-422-MAPPING-UNSUPPORTED` (422) · the same posting
               refusals as API-FIN-019 — all answered to the calling system, never rendered
               by a FIN screen
Invalidation : n/a — no client of this plan calls it
### F2-QUERY — API-FIN-021            traces=API-FIN-021,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030
POST `/api/v1/fin/journal-entries/{id}/reverse` · no request body ·
response `JournalEntryResponse` (the new reversal entry) · kind **mutation**
Errors       : `FIN-409-NOT-POSTED` (409) [RULE-FIN-013] → user message,
               ar: "لا يمكن عكس قيد غير مُرحَّل" · en: "A non-posted entry cannot be reversed" ·
               `FIN-409-ALREADY-REVERSED` (409) → user message (the entry already carries a
               reversal link) · `FIN-409-PERIOD-NOT-OPEN` (409) → user message, raised when no
               open period can receive the reversal [RULE-FIN-012] ·
               `FIN-404-ENTRY` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[journal-entries, *]`, `[journal-entry, id]` (the original now carries its
               `reversalEntryId`) and `[reports, *]`
### F2-LOOKUP — JOURNAL_TYPE · JOURNAL_STATUS · DEBIT_CREDIT
Keys `JOURNAL_TYPE` (UXD-FIN-005) · `JOURNAL_STATUS` (UXD-FIN-006) · `DEBIT_CREDIT`
(UXD-FIN-002) — one shared hook per key, `{ code, labelAr, labelEn }`, long-lived cache. The
first two serve the search filters and the read-only display; on the entry form the journal
type is the fixed value `MANUAL` and no select is rendered (ADR-FIN-008).
### F2-SCREEN-INIT — SCR-FIN-006
Permission read : `FIN_JOURNAL_ENTRIES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). CREATE and the custom reverse action are not readable; their
                  affordances render and the server's 403 is the authority.
Lookups used    : JOURNAL_TYPE (filter + display), JOURNAL_STATUS (filter + display),
                  DEBIT_CREDIT (line grid)
Entity by id    : API-FIN-022 — the entry page reads by id rather than from the list cache,
                  because the lines and their dimensions are what the page renders
Period + year   : the period and year selects of the entry form are served by the SCR-FIN-007
                  fiscal-period query (API-FIN-033) through its own shared hook, keyed the
                  same way; this screen declares the dependency and does not duplicate the call
### F2-FACADE — SCR-FIN-006
Composes     : API-FIN-018 (list) · API-FIN-022 (entry) · API-FIN-019, API-FIN-021
               (mutations) · the three lookup hooks and the fiscal-period hook
State it owns: the list derived from the query's data, the selected entry id (route param),
               the filter object including page and size, the draft entry with its draft lines
               and their dimensions, the live debit and credit totals derived from those draft
               lines, and a derived loading flag
Operations   : postManualEntry (the draft is submitted whole; every returned refusal is
               displayed at once — REQ-FIN-015 — and nothing is cleared) ·
               reverseEntry (confirmation naming the period the reversal will land in)
The live totals are derived state over the draft lines and are never sent: the balance
judgement is RULE-FIN-006's, evaluated by the server.

<!-- SUB:F2-SCR-FIN-006:END -->
