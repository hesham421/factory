<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-003 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-007, AC-FIN-008, AC-FIN-009, AC-FIN-045, API-FIN-009, API-FIN-010, API-FIN-011, API-FIN-034, REQ-FIN-007, REQ-FIN-008, REQ-FIN-009, REQ-FIN-045, SCR-FIN-003, UXD-FIN-002, UXD-FIN-007, UXD-FIN-008, UXD-FIN-009, UXD-FIN-010 -->
<!-- SUB:F2-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F2-QUERY — API-FIN-009            traces=API-FIN-009,REQ-FIN-007
POST `/api/v1/fin/event-rules/search` · request `EventTypeRuleSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<EventTypeRuleResponse>` ·
kind **read query**
Cache key    : `[event-rules, filters]` — eventTypeCode, isActiveFl, sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-010            traces=API-FIN-010,REQ-FIN-007
POST `/api/v1/fin/event-rules` · request `EventTypeRuleCreateRequest` { eventTypeCode, nameAr,
nameEn } · response `EventTypeRuleResponse` · kind **mutation**
Errors       : `FIN-409-RULE-DUP` (409) → inline on `eventTypeCode` (one rule per event type;
               note that a deactivated rule still holds its type — SRS §B4) ·
               `FIN-400-INVALID-LOOKUP` (400) → inline on `eventTypeCode` ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[event-rules, *]`
### F2-QUERY — API-FIN-011            traces=API-FIN-011,REQ-FIN-008,REQ-FIN-009
POST `/api/v1/fin/event-rules/{id}/lines` · request `RuleLineCreateRequest`
{ accountDerivationTypeCode, accountDerivationValue, amountSourceTypeCode, amountSourceValue?,
directionCode, distributionTypeCode, isRemainderFl? } · response `RuleLineResponse` ·
kind **mutation**
Errors       : `FIN-409-REMAINDER-COUNT` (409) → user message for RULE-FIN-003,
               ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" ·
               en: "Exactly one remainder line is required when any percentage distribution
               is present" ·
               `FIN-422-REMAINDER-MARKER` (422) → user message on the remainder marker ·
               `FIN-422-INVALID-PERCENTAGE-VALUE` (422) → inline on `amountSourceValue` ·
               `FIN-404-RULE` (404) → user message · `FIN-400-INVALID-LOOKUP` (400) → inline
               on the offending code field · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[event-rules, *]` — the rule's line set is part of what the list shows
### F2-QUERY — API-FIN-034            traces=API-FIN-034,REQ-FIN-007
PUT `/api/v1/fin/event-rules/{id}/deactivate` · no request body ·
response `EventTypeRuleResponse` (isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-RULE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[event-rules, *]`
### F2-LOOKUP — ACCOUNTING_EVENT_TYPE
Key `ACCOUNTING_EVENT_TYPE` · one shared hook, resolved through UXD-FIN-007 · options
{ code, labelAr, labelEn } · long-lived cache. The list is legitimately empty until a host
registers event types; an empty list disables the create affordance with an explanatory
empty-state and is never replaced by a free-text field.
### F2-LOOKUP — ACCOUNT_DERIVATION_TYPE · AMOUNT_SOURCE_TYPE · DISTRIBUTION_TYPE · DEBIT_CREDIT
Keys `ACCOUNT_DERIVATION_TYPE` (UXD-FIN-008) · `AMOUNT_SOURCE_TYPE` (UXD-FIN-009) ·
`DISTRIBUTION_TYPE` (UXD-FIN-010) · `DEBIT_CREDIT` (UXD-FIN-002) — one shared hook per key,
each `{ code, labelAr, labelEn }`, each long-lived, and each shared with the other screens that
use the same key rather than re-fetched here.
### F2-SCREEN-INIT — SCR-FIN-003
Permission read : `FIN_RULES` present in the caller's effective menu → VIEW (ADR-FIN-005)
Lookups used    : ACCOUNTING_EVENT_TYPE (header + filter), ACCOUNT_DERIVATION_TYPE,
                  AMOUNT_SOURCE_TYPE, DISTRIBUTION_TYPE, DEBIT_CREDIT (line grid)
Entity by id    : none published — the rule page hydrates from the `[event-rules, filters]`
                  cache (ADR-FIN-006)
### F2-FACADE — SCR-FIN-003
Composes     : API-FIN-009 (list) · API-FIN-010, API-FIN-011, API-FIN-034 (mutations) · the
               five lookup hooks above
State it owns: the rule list from the query's data, the selected rule id (route param), the
               filter object including page and size, the draft line being added, and a
               derived loading flag
Operations   : createRule · addRuleLine · deactivateRule (confirmation stating that the event
               type is not freed for a replacement rule — the limitation SRS §B4 records)
There is no updateRule and no deleteRuleLine operation: neither endpoint exists (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-003:END -->
