<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-005 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-025, AC-FIN-026, AC-FIN-045, API-FIN-015, API-FIN-016, API-FIN-017, API-FIN-037, REQ-FIN-025, REQ-FIN-026, REQ-FIN-045, SCR-FIN-005, UXD-FIN-010 -->
<!-- SUB:F2-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F2-QUERY — API-FIN-015            traces=API-FIN-015,REQ-FIN-025
POST `/api/v1/fin/allocation-rules/search` · request `AllocationRuleSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<AllocationRuleResponse>` (each row
carries its full `targets[]`) · kind **read query**
Cache key    : `[allocation-rules, filters]` — nameAr/nameEn, sourceAccountId, isActiveFl,
               sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-016            traces=API-FIN-016,REQ-FIN-025
POST `/api/v1/fin/allocation-rules` · request `AllocationRuleCreateRequest` { nameAr, nameEn,
sourceAccountId, targets[] { targetAccountId, dimensionValueId?, distributionTypeCode,
distributionValue?, isRemainderFl? } } · response `AllocationRuleResponse` · kind **mutation**
Errors       : `FIN-409-REMAINDER-COUNT` (409) → user message for RULE-FIN-003, the same ar/en
               pair the rule declares, shown on the target grid ·
               `FIN-422-REMAINDER-MARKER` (422) → user message on the remainder marker ·
               `FIN-422-INVALID-PERCENTAGE-VALUE` (422) → inline on the offending
               `distributionValue` · `FIN-404-ACCOUNT` (404) → inline on the offending account ·
               `FIN-409-INVALID-DIMENSION` (409) → inline on the offending dimension value ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`
### F2-QUERY — API-FIN-017            traces=API-FIN-017,REQ-FIN-026
POST `/api/v1/fin/allocation-rules/{id}/run` · no request body ·
response `JournalEntryResponse` (the posted distribution entry) · kind **mutation**
Errors       : `FIN-409-NOT-ACTIVE` (409) → user message, the same ar/en pair as the template
               run · `FIN-404-ALLOCATION-RULE` (404) → user message ·
               `FIN-409-REMAINDER-COUNT` (409) [RULE-FIN-003, re-checked at run time] ·
               `FIN-422-REMAINDER-NOT-POSITIVE` (422) → user message for RULE-FIN-010,
               ar: "سطر الباقي يُحسب كفرق، لا كنسبة" ·
               en: "The remainder line is computed as a difference, never as a percentage" ·
               the posting pipeline's refusals — `FIN-409-UNBALANCED`,
               `FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`,
               `FIN-409-INVALID-DIMENSION` (409) · `FIN-404-PERIOD` / `FIN-404-YEAR` (404) ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`, `[journal-entries, *]` and `[reports, *]`
### F2-QUERY — API-FIN-037            traces=API-FIN-037,REQ-FIN-025
PUT `/api/v1/fin/allocation-rules/{id}/deactivate` · no request body ·
response `AllocationRuleResponse` (isActiveFl=false, targets included) · kind **mutation**
Errors       : `FIN-404-ALLOCATION-RULE` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`
### F2-LOOKUP — DISTRIBUTION_TYPE
Key `DISTRIBUTION_TYPE` · the same shared hook SCR-FIN-003 uses, resolved through UXD-FIN-010 ·
options { code, labelAr, labelEn } · long-lived cache · one hook for the whole application
### F2-SCREEN-INIT — SCR-FIN-005
Permission read : `FIN_ALLOCATION_RULES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005)
Lookups used    : DISTRIBUTION_TYPE (target grid)
Entity by id    : none published — the search row carries the full aggregate, targets included
                  (ADR-FIN-006)
### F2-FACADE — SCR-FIN-005
Composes     : API-FIN-015 (list) · API-FIN-016, API-FIN-017, API-FIN-037 (mutations) · the
               DISTRIBUTION_TYPE hook
State it owns: the rule list from the query's data, the selected rule id (route param), the
               filter object including page and size, the draft rule and its draft targets,
               and a derived loading flag
Operations   : createRule (header and targets in one submission) · runRule (confirmation
               first; on success the returned entry is offered on SCR-FIN-006) ·
               deactivateRule (confirmation stating that the rule will no longer run)
No updateRule operation exists: no endpoint is published (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-005:END -->
