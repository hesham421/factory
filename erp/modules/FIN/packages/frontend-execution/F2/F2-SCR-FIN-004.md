<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-004 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-022, AC-FIN-023, AC-FIN-024, AC-FIN-045, API-FIN-012, API-FIN-013, API-FIN-014, API-FIN-036, REQ-FIN-022, REQ-FIN-023, REQ-FIN-024, REQ-FIN-045, SCR-FIN-004, UXD-FIN-002, UXD-FIN-011, UXD-FIN-012 -->
<!-- SUB:F2-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F2-QUERY — API-FIN-012            traces=API-FIN-012,REQ-FIN-022
POST `/api/v1/fin/recurring-templates/search` · request `RecurringTemplateSearchRequest`
{ filters[], sortField, sortDirection, page, size } · response
`Page<RecurringTemplateResponse>` (each row carries its full `lines[]`) · kind **read query**
Cache key    : `[recurring-templates, filters]` — nameAr/nameEn, scheduleTypeCode, isActiveFl,
               sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-013            traces=API-FIN-013,REQ-FIN-022
POST `/api/v1/fin/recurring-templates` · request `RecurringTemplateCreateRequest` { nameAr,
nameEn, scheduleTypeCode, frequencyCode?, startDate, endDate?, lines[] { accountId, amount,
directionCode, dimensionValueId? } } · response `RecurringTemplateResponse` · kind **mutation**
Errors       : `FIN-400-MISSING-FREQUENCY` (400) → inline on `frequencyCode` when the schedule
               type is RECURRING · `FIN-404-ACCOUNT` (404) → inline on the offending line's
               account · `FIN-409-INVALID-DIMENSION` (409) → inline on the offending line's
               dimension value · `FIN-400-INVALID-LOOKUP` (400) → inline on the offending code ·
               validation (400) → inline per field · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[recurring-templates, *]`
### F2-QUERY — API-FIN-014            traces=API-FIN-014,REQ-FIN-023,REQ-FIN-024
POST `/api/v1/fin/recurring-templates/{id}/run` · no request body ·
response `JournalEntryResponse` (the posted entry) · kind **mutation**
Errors       : `FIN-409-NOT-ACTIVE` (409) → user message,
               ar: "هذا التعريف غير نشط ولا يمكن تشغيله" ·
               en: "This definition is deactivated and cannot be run" ·
               `FIN-404-TEMPLATE` (404) → user message ·
               the posting pipeline's refusals, each as its own user message —
               `FIN-409-UNBALANCED` (409) [RULE-FIN-006] ·
               `FIN-409-NOT-POSTABLE-ACCOUNT` (409) [RULE-FIN-007] ·
               `FIN-409-PERIOD-NOT-OPEN` (409) [RULE-FIN-008] ·
               `FIN-409-INVALID-DIMENSION` (409) [RULE-FIN-009] ·
               `FIN-404-PERIOD` / `FIN-404-YEAR` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[recurring-templates, *]` (the template's `nextRunDate` advanced) and
               `[journal-entries, *]` (a new entry exists) and `[reports, *]` (every live
               report over posted lines is now stale)
### F2-QUERY — API-FIN-036            traces=API-FIN-036,REQ-FIN-022
PUT `/api/v1/fin/recurring-templates/{id}/deactivate` · no request body ·
response `RecurringTemplateResponse` (isActiveFl=false, lines included) · kind **mutation**
Errors       : `FIN-404-TEMPLATE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[recurring-templates, *]`
### F2-LOOKUP — RECURRING_SCHEDULE_TYPE · RECURRING_FREQUENCY · DEBIT_CREDIT
Keys `RECURRING_SCHEDULE_TYPE` (UXD-FIN-011) · `RECURRING_FREQUENCY` (UXD-FIN-012) ·
`DEBIT_CREDIT` (UXD-FIN-002) — one shared hook per key, `{ code, labelAr, labelEn }`,
long-lived cache, the DEBIT_CREDIT hook shared with every other screen that shows a direction.
### F2-SCREEN-INIT — SCR-FIN-004
Permission read : `FIN_RECURRING_TEMPLATES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005)
Lookups used    : RECURRING_SCHEDULE_TYPE (header + filter), RECURRING_FREQUENCY (header),
                  DEBIT_CREDIT (line grid)
Entity by id    : none published — the search row already carries the full aggregate, lines
                  included, so the page hydrates from the `[recurring-templates, filters]`
                  cache (ADR-FIN-006)
### F2-FACADE — SCR-FIN-004
Composes     : API-FIN-012 (list) · API-FIN-013, API-FIN-014, API-FIN-036 (mutations) · the
               three lookup hooks above
State it owns: the template list from the query's data, the selected template id (route
               param), the filter object including page and size, the draft template and its
               draft lines, and a derived loading flag
Operations   : createTemplate (header and lines in one submission) · runTemplate (confirmation
               first; on success the returned entry is offered on SCR-FIN-006) ·
               deactivateTemplate (confirmation stating that the template will no longer run)
No updateTemplate operation exists: no endpoint is published (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-004:END -->
