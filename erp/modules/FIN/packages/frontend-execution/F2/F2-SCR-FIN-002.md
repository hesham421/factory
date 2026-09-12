<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-002 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-004, AC-FIN-005, AC-FIN-006, API-FIN-005, API-FIN-006, API-FIN-007, API-FIN-008, API-FIN-035, REQ-FIN-004, REQ-FIN-005, REQ-FIN-006, SCR-FIN-002 -->
<!-- SUB:F2-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F2 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F2-QUERY — API-FIN-005            traces=API-FIN-005,REQ-FIN-004
POST `/api/v1/fin/dimensions/search` · request `DimensionSearchRequest` { filters[], sortField,
sortDirection, page, size } · response `Page<DimensionResponse>` · kind **read query**
Cache key    : `[dimensions, filters]` — code, sort **and page, size**, all inside the one object
Errors       : `FIN-400-INVALID-SORT` (400) → inline on the sort control ·
               `FIN-403-FORBIDDEN` (403) → forbidden message · server error → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-006
### F2-QUERY — API-FIN-006            traces=API-FIN-006,REQ-FIN-004
POST `/api/v1/fin/dimensions` · request `DimensionCreateRequest` { code, nameAr, nameEn } ·
response `DimensionResponse` · kind **mutation**
Errors       : `FIN-409-DIMENSION-DUP` (409) → inline on `code` · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[dimensions, *]`
### F2-QUERY — API-FIN-008            traces=API-FIN-008,REQ-FIN-005
POST `/api/v1/fin/dimensions/values/search` · request `DimensionValueSearchRequest`
{ filters[] including `dimensionId`, sortField, sortDirection, page, size } ·
response `Page<DimensionValueResponse>` · kind **read query**
Cache key    : `[dimension-values, filters]` — dimensionId, code, sort **and page, size**.
               The parent id is part of the key, so selecting another dimension is a different
               cache entry rather than a refetch of the same one.
Errors       : `FIN-404-DIMENSION` (404) → user message · `FIN-400-INVALID-SORT` (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-007 and API-FIN-035
### F2-QUERY — API-FIN-007            traces=API-FIN-007,REQ-FIN-005,REQ-FIN-006
POST `/api/v1/fin/dimensions/{id}/values` · request `DimensionValueCreateRequest`
{ code, nameAr, nameEn, sortOrder } · response `DimensionValueResponse` · kind **mutation**
Errors       : `FIN-409-DIMVALUE-DUP` (409) → user message for RULE-FIN-002, routed inline to
               `code`, ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" ·
               en: "This code is already used within this dimension" ·
               `FIN-404-DIMENSION` (404) → user message · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[dimension-values, *]`
### F2-QUERY — API-FIN-035            traces=API-FIN-035,REQ-FIN-005
PUT `/api/v1/fin/dimensions/values/{id}/deactivate` · no request body ·
response `DimensionValueResponse` (isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-DIMVALUE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[dimension-values, *]`
### F2-SCREEN-INIT — SCR-FIN-002
Permission read : `FIN_DIMENSIONS` present in the caller's effective menu → VIEW (ADR-FIN-005)
Lookups used    : none — this screen writes the data other screens' dimension selects read
Entity by id    : none published for either resource; both panes hydrate from their own search
                  caches (ADR-FIN-006)
### F2-FACADE — SCR-FIN-002
Composes     : API-FIN-005, API-FIN-008 (lists) · API-FIN-006, API-FIN-007, API-FIN-035
               (mutations)
State it owns: the dimension list and the selected dimension's value list, both derived from
               their queries' data; the selected dimension id (from the route param); two
               filter objects, each carrying its own page and size; a derived loading flag
Operations   : createDimension · createValue (under the selected dimension) ·
               deactivateValue (confirmation naming that the value will be refused on any
               later journal line — REQ-FIN-021)
There is no deactivateDimension operation: no endpoint exists for it (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-002:END -->
