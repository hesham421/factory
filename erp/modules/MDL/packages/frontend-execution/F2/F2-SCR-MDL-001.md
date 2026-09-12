<!-- source: PHASE:F2 / SUB:F2-SCR-MDL-001 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, SCR-MDL-001, UXD-MDL-001 -->
<!-- SUB:F2-SCR-MDL-001:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001 -->
### F2 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F2-QUERY — API-MDL-001            traces=API-MDL-001,REQ-MDL-001
POST `/api/v1/mdl/lookup-types/search` · request `LookupTypeSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<LookupTypeResponse>` ·
kind **read query** (a POST that mutates nothing — ADR-MDL-002)
Cache key    : `[lookup-types, filters]` where `filters` is the whole request object — key,
               ownerModuleCode, isActiveFl, sortField, sortDirection **and page, size**
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `VALIDATION_ERROR` (400) → inline on the offending filter ·
               `INTERNAL_ERROR` (500) → generic message
Loading      : LOCAL — the SRS states nothing about this call being slow, so no GLOBAL indicator
Cache policy : defaults
Invalidation : refreshed by API-MDL-002, API-MDL-003 and API-MDL-004
### F2-QUERY — API-MDL-002            traces=API-MDL-002,REQ-MDL-001,REQ-MDL-002
POST `/api/v1/mdl/lookup-types` · request `LookupTypeCreateRequest` { key, ownerModuleCode,
nameAr, nameEn } · response `LookupTypeResponse` · kind **mutation**
Errors       : `MDL-409-MODULE-NOT-REGISTERED` (409) → user message for RULE-MDL-001, routed to
               the owner-module field, ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" ·
               en: "The owning module is not registered in the Security module" ·
               `MDL-409-TYPE-DUP` (409) → inline on `key` ·
               `VALIDATION_ERROR` (400) → inline per `error.fieldErrors[].field` ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-types, *]`
### F2-QUERY — API-MDL-003            traces=API-MDL-003,REQ-MDL-003
PUT `/api/v1/mdl/lookup-types/{id}` · request `LookupTypeUpdateRequest` { nameAr, nameEn } ·
response `LookupTypeResponse` · kind **mutation**
Errors       : `MDL-404-TYPE` (404) → user message · `VALIDATION_ERROR` (400) → inline ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-types, *]`
The request carries the two names and nothing else, which is RULE-MDL-003 expressed in the
surface: there is no key field to send and none is sent.
### F2-QUERY — API-MDL-004            traces=API-MDL-004,REQ-MDL-004
DELETE `/api/v1/mdl/lookup-types/{id}` · no request body · response `LookupTypeResponse`
(isActiveFl=false) · kind **mutation**
Errors       : `MDL-404-TYPE` (404) → user message · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-types, *]` and `[lookup-values, *]` — RULE-MDL-004 makes an inactive
               type's values invisible to consumers, so any cached value list of that type is
               stale in meaning even though its rows have not changed
### F2-QUERY — API-MDL-005            traces=API-MDL-005,REQ-MDL-005
POST `/api/v1/mdl/lookup-types/values/search` · request `LookupValueSearchRequest`
{ filters[] including `lookupTypeId`, sortField, sortDirection, page, size } ·
response `Page<LookupValueResponse>` · kind **read query** (ADR-MDL-002)
Cache key    : `[lookup-values, filters]` — lookupTypeId, code, sort **and page, size**. The
               parent id is part of the key, so selecting another type is a different cache
               entry rather than a refetch of the same one.
Errors       : `ACCESS_DENIED` (403) → forbidden message · `VALIDATION_ERROR` (400) → inline ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-MDL-006, API-MDL-007, API-MDL-008 and API-MDL-009
This read returns inactive values as well as active ones — it is the manager's view, not the
consumer's, and the screen shows what API-MDL-011 would hide.
### F2-QUERY — API-MDL-006            traces=API-MDL-006,REQ-MDL-006,REQ-MDL-007
POST `/api/v1/mdl/lookup-types/{id}/values` · request `LookupValueCreateRequest` { code,
nameAr, nameEn, sortOrder } · response `LookupValueResponse` · kind **mutation**
Errors       : `MDL-409-VALUE-DUP` (409) → user message for RULE-MDL-002, routed inline to
               `code`, ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" ·
               en: "This code is already used within this type" ·
               `MDL-404-TYPE` (404) → user message (the parent type is gone) ·
               `VALIDATION_ERROR` (400) → inline · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]`
### F2-QUERY — API-MDL-007            traces=API-MDL-007,REQ-MDL-008
PUT `/api/v1/mdl/lookup-values/{id}` · request `LookupValueUpdateRequest` { nameAr, nameEn,
sortOrder } · response `LookupValueResponse` · kind **mutation**
Errors       : `MDL-404-VALUE` (404) → user message · `VALIDATION_ERROR` (400) → inline ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]` — the sort order may have moved the row
### F2-QUERY — API-MDL-008            traces=API-MDL-008,REQ-MDL-009
DELETE `/api/v1/mdl/lookup-values/{id}` · no request body · response `LookupValueResponse`
(isActiveFl=false) · kind **mutation**
Errors       : `MDL-404-VALUE` (404) → user message · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]`
### F2-QUERY — API-MDL-009            traces=API-MDL-009,REQ-MDL-010
PATCH `/api/v1/mdl/lookup-types/{id}/values/reorder` · request `LookupValueReorderRequest`
{ orderedValueIds[] } · response **a bare array** of `LookupValueResponse` in the persisted
order — not a `Page<T>` · kind **mutation**
Errors       : `MDL-400-REORDER-MISMATCH` (400) → user message on the value list (the submitted
               set is not exactly that type's values) · `MDL-404-TYPE` (404) → user message ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]` — every row's `sortOrder` may have changed, and the
               response's order is the persisted one, so the list re-renders from it
The whole ordered set is submitted, never one row's new position: the endpoint takes
`orderedValueIds[]` and the mismatch error exists precisely because a partial set is wrong.
### F2-SCREEN-INIT — SCR-MDL-001
Permission read : `MDL_LOOKUPS` present in the caller's effective menu → VIEW. CREATE, UPDATE
                  and DELETE are not readable from any published endpoint; their affordances
                  render and the server's `ACCESS_DENIED` is the authority (see SEC-FE).
Lookups used    : none — MDL has no lookup of its own (SRS §A6)
Foreign data    : the owner-module select and filter resolve through UXD-MDL-001; ONE shared
                  hook, long-lived cache, shared with SCR-MDL-002
Entity by id    : none published for either level — both forms hydrate from the row their own
                  search query already holds (ADR-MDL-005), so opening an edit performs no
                  second read and an invalidation re-reads through the same key
### F2-FACADE — SCR-MDL-001
Composes     : API-MDL-001, API-MDL-005 (lists) · API-MDL-002, API-MDL-003, API-MDL-004,
               API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009 (mutations) · the
               UXD-MDL-001 hook
State it owns: the type list and the selected type's value list, both derived from their
               queries' data (never a copy); the selected type id (from the route param); two
               filter objects, each carrying its own page and size; the pending drag order
               while a reorder is in flight; and a derived loading flag over the calls in flight
Operations   : createType · updateType · deactivateType (confirmation naming that consumer
               reads will stop returning its values — RULE-MDL-004) · createValue ·
               updateValue · deactivateValue (confirmation) · reorderValues (the whole ordered
               list, submitted once)
There is no activateType and no activateValue operation: no endpoint exists for either
(ADR-MDL-005). Components use the facade only; the facade uses the declared queries only.
<!-- SUB:F2-SCR-MDL-001:END -->
