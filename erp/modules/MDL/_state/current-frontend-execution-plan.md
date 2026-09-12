# FRONTEND EXECUTION PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Track : frontend
Framework : react-ts-vite (profile.stack.frontend.framework) · routing react-router ·
            server-state tanstack-query · forms react-hook-form · validation zod ·
            state useState/useReducer + Context (no global store by default)
Inputs : srs (v1, PRD-approved), prd (v1), api-docs (v1, published by the backend repo),
         registry-srs (v1), registry-exec-be (v1)
Screens : 2 — SCR-MDL-001..002 · UXD : 1 — UXD-MDL-001 · API bound : 11 / 11
Open ADRs : 7 — erp/decisions/MDL/ (ADR-MDL-001..007, all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

## API SURFACE — MDL v1   (source: `_inputs/api-docs-mdl.md` — the ONLY endpoint source)

```
ENDPOINTS   11 — API-MDL-001..011, bound to the published surface by the API ID BINDING annex
            of the api-docs (ADR-MDL-001). Envelope: every response is wrapped in
            ApiResponse<T> { success, data, error { code, message, fieldErrors[] }, timestamp }.
            Paging constraints (PageableBuilder): default page 0 · default size 20 · maximum
            size 200. THREE response shapes, and the difference matters to every F2 block:
              · Page<T> — API-MDL-001 and API-MDL-005 alone
              · a bare array — API-MDL-009 (the reordered values), API-MDL-010
                (OwnerGroupResponse[]) and API-MDL-011 (LookupValueResponse[]); none of these
                carries a paging envelope and none may be read as one
              · a single object — API-MDL-002, 003, 004, 006, 007, 008
            Two reads and one browse are POST `…/search` with a `filters[] {field, operator,
            value}` envelope rather than GET with query params (operators EQUALS, NOT_EQUALS,
            LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN) —
            which is what the SRS B5 tables state too; only the backend plan's contract table
            still predicts GET (ADR-MDL-002). API-MDL-010's request carries `filters` alone,
            with no sort and no paging.
ERRORS      business codes, each already carrying its ar/en text in the module's catalog:
            MDL-400-REORDER-MISMATCH (400) · MDL-404-TYPE · MDL-404-VALUE · MDL-404-TYPE-KEY
            (404) · MDL-409-MODULE-NOT-REGISTERED [RULE-MDL-001] · MDL-409-TYPE-DUP ·
            MDL-409-VALUE-DUP [RULE-MDL-002] (409) · framework codes VALIDATION_ERROR (400) ·
            DATA_INTEGRITY_VIOLATION (409) · ACCESS_DENIED (403) · INTERNAL_ERROR (500).
            Routing is uniform across every F2 block: field validation → inline · business
            rule → user message · unauthenticated → login · forbidden → the localized
            forbidden message · server → generic.
LOOKUPS     **none.** SRS §A6 records that MDL introduces no coded list of its own — it is the
            mechanism every other module's lists run on. No field on either screen is a
            lookup-backed code, no lookup hook exists anywhere in this plan, and no enum is
            modelled. The one cross-module dependency, UXD-MDL-001, is the owner-module field,
            whose valid set the security module owns (ADR-MDL-004) — not lookup data, and not
            read through API-MDL-011.
PERMISSIONS declared by the backend and read from the SRS Access summary and the backend
            registry, never redeclared here: PERM_MDL_LOOKUPS_VIEW / _CREATE / _UPDATE /
            _DELETE · PERM_MDL_TYPE_REGISTRY_VIEW.
            No MDL endpoint publishes the caller's own permission set: the screen gate is the
            security module's effective menu (SEC-FE below), and no `PERM_*` name is composed
            at runtime.
```

### Reconciliation against the SRS — run once, before any F-content

- **Every REQ that needs an endpoint has one.** REQ-MDL-001..013 map onto API-MDL-001..011
  with no gap; the mapping is the traces of the F2 blocks below.
- **Every documented endpoint maps to a REQ.** All 11 are bound; none is unknown and none is
  used without a REQ behind it.
- **Naming and shape differences** — three reads are POST `…/search` where the backend plan's
  contract table predicted GET. The api-docs and the SRS B5 tables agree with each other; the
  backend plan is the one artifact that lags, and `gov.py analyze` reports it there as C8.4.
  The frontend binds to the published shape (ADR-MDL-002).
- **Operations the SRS names with no published endpoint** — `activate` at either level, and
  the by-id reads of a type and of a value. None is required by a `REQ-*`, so none is
  breaking; each is omitted rather than faked (ADR-MDL-005).
- **Endpoints published but not called by this frontend** — API-MDL-011 alone, the consumer
  read another module's backend performs over the platform's in-process module interface
  (ADR-MDL-007). It is bound and blocked out in F2 below.
- **One screen's form differs from its SRS Part B input list** — SCR-MDL-001 renders
  `isActiveFl` read-only at both levels although B3 lists it among the detail inputs; no
  published write DTO accepts it and the deactivate endpoints are what change it
  (ADR-MDL-006).
- **Nothing is invented.** No value absent from the api-docs appears in this plan, and no
  permission name, route or component is derived from anything but the SRS, the api-docs and
  the profile's own stack.

## EXECUTION PLAN INDEX — MDL v1 — frontend-execution-plan-mdl.md

| # | Phase | Split | Blocks |
|---|---|---|---|
| 1 | F1 — Models & Types | always — one SUB per screen | 2 SUB |
| 2 | F2 — Data Hooks | always — one SUB per screen | 2 SUB |
| 3 | F3 — Forms & Validators | always — one SUB per screen | 2 SUB |
| 4 | F4 — Screens & Routes | always — one SUB per screen | 2 SUB |
| 5 | SEC-FE | never split | level-1 only |
| 6 | ALIGN-FE | never split | level-1 only |

**SCREEN REGISTRY**

| SCR | Name (ar / en) | Page code | Container pattern | Owning ENT |
|---|---|---|---|---|
| SCR-MDL-001 | اللوكبات العامة / Generic Lookups | MDL_LOOKUPS | TREE_MASTER_DETAIL | ENT-MDL-001 نوع اللوكب / LookupType (+ ENT-MDL-002 قيمة اللوكب / LookupValue) |
| SCR-MDL-002 | سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner | MDL_TYPE_REGISTRY | FULL_PAGE (no entry sub-view — ADR-MDL-003) | ENT-MDL-001 نوع اللوكب / LookupType |

Two screens, and every `sub_bearing` phase still splits per screen — one `SUB` per `SCR-*`,
at any screen count. The four phases below therefore carry two SUB blocks each, and every SUB
id is phase-qualified: `SUB:F1-SCR-MDL-001` and `SUB:F2-SCR-MDL-001` are distinct blocks for
the same screen under different phases.

These phases carried a `split_threshold` of `SCR >= 5` until 2026-09-12, which would have left
this module — and every small module after it — with a package whose folder tree differed from
a large module's for no reason a reader could act on. The gate was removed at its source in
`profiles/erp.yaml`, not worked around here; `shared/MARKER-PROTOCOL.md` now renders these four
rows as `per screen`.

<!-- PHASE:F1:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 1 — F1 — Models & Types

Per `ENT-*` (from the response DTOs of the api-docs) and per `SCR-*`: the source DTO with each
property's type and read-only / system-only status, then the screen's search model, form model
and container. Both names are carried per language (ar, en). No internal or tenant identifier
is modelled, and nothing is modelled that the api-docs do not return. **No lookup field and no
enum appears anywhere in this phase** — MDL owns no coded list of its own (SRS §A6).

<!-- SUB:F1-SCR-MDL-001:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001 -->
### F1 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F1-MODEL — ENT-MDL-001 — نوع اللوكب / LookupType
Source DTO   : `LookupTypeResponse` (read) · `LookupTypeCreateRequest` · `LookupTypeUpdateRequest`
  lookupTypePk    : number · read-only (PK) · system-only
  key             : string · maxLength 80 · required on create, **read-only on edit** —
                    RULE-MDL-003, and `LookupTypeUpdateRequest` does not carry it
  ownerModuleCode : string · maxLength 10 · required on create, **read-only on edit** — not in
                    the update request; its valid set is the security module's registry
                    (UXD-MDL-001), and it is held as a plain string, never an enum
  nameAr          : string · required · maxLength 150
  nameEn          : string · required · maxLength 150
  isActiveFl      : boolean · read-only — flipped only by API-MDL-004 (ADR-MDL-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — ENT-MDL-002 — قيمة اللوكب / LookupValue
Source DTO   : `LookupValueResponse` (read) · `LookupValueCreateRequest` ·
               `LookupValueUpdateRequest` · `LookupValueReorderRequest`
  lookupValuePk : number · read-only (PK) · system-only
  lookupTypeId  : number · read-only — the path id of API-MDL-006, taken from the selected
                  parent, never typed
  code          : string · maxLength 50 · required on create, **read-only on edit** — the
                  update request does not carry it; unique within its type (RULE-MDL-002)
  nameAr        : string · required · maxLength 150
  nameEn        : string · required · maxLength 150
  sortOrder     : number · required on create **and** on update — and the same field the
                  reorder writes, through `LookupValueReorderRequest { orderedValueIds[] }`
  isActiveFl    : boolean · read-only — flipped only by API-MDL-008 (ADR-MDL-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-SCREEN — SCR-MDL-001
Search model : master filters — key : string · LIKE · ownerModuleCode : string · EXACT (from
               the UXD-MDL-001 hook) · isActiveFl : boolean · EXACT
               detail filters — code : string · LIKE · lookupTypeId : number · EXACT (set from
               the selected parent, not typed)
               paging + sort — page, size, sortField, sortDirection, inside each of
               `LookupTypeSearchRequest` and `LookupValueSearchRequest` per `Page<T>`
Form model   : type, create — key, ownerModuleCode, nameAr, nameEn (all required)
               type, edit   — nameAr, nameEn (required); key and ownerModuleCode read-only
               value, create — code, nameAr, nameEn, sortOrder (all required)
               value, edit   — nameAr, nameEn, sortOrder (required); code read-only
               reorder       — the ordered list of value ids, not a per-row edit
               excluded system fields: both PKs, lookupTypeId, both isActiveFl, the audit fields
Container    : TREE_MASTER_DETAIL
`isActiveFl` is modelled read-only at both levels: it is in the response and in no write
request, so a form that offered it would be offering a field the server ignores (ADR-MDL-006).
<!-- SUB:F1-SCR-MDL-001:END -->

<!-- SUB:F1-SCR-MDL-002:START traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001,SCR-MDL-002 -->
### F1 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F1-MODEL — OwnerGroupResponse — المجموعة حسب المالك / Owner group
Source DTO   : `OwnerGroupResponse[]` (read only — this screen writes nothing)
  ownerModuleCode : string · read-only — the group key (UXD-MDL-001)
  types[]         : LookupTypeResponse — the same type model as SCR-MDL-001 above, every
                    property read-only here: lookupTypePk, key, ownerModuleCode, nameAr,
                    nameEn, isActiveFl, and the four audit fields
### F1-SCREEN — SCR-MDL-002
Search model : filters — ownerModuleCode : string · EXACT · key : string · LIKE.
               **No paging and no sort**: `LookupTypeByOwnerSearchRequest` carries `filters`
               alone, so no page or size is modelled and none belongs in this screen's cache key
Form model   : none — a read-only browse (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-MDL-003)
The response is a bare array of groups, not a `Page<T>`, and is modelled as one: reading it
through a paging envelope would invent fields the endpoint does not send.
<!-- SUB:F1-SCR-MDL-002:END -->

<!-- PHASE:F1:END -->

<!-- PHASE:F2:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 2 — F2 — Data Hooks

What each screen needs from the API — not hook code. Every read query's cache key carries
**every** filter that changes the response, page and size included **where the endpoint is
paged**; page and page size live inside the filter object and are never independent state.
Every mutation declares its invalidation. Components use the facade only; the facade uses the
declared queries only (server-state library: `tanstack-query`).

Only two of the eleven endpoints return `Page<T>` — API-MDL-001 and API-MDL-005. API-MDL-009,
API-MDL-010 and API-MDL-011 return bare arrays, so their keys carry no page or size and their
blocks say so rather than leaving a reader to assume the usual envelope.

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

<!-- SUB:F2-SCR-MDL-002:START traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001,SCR-MDL-002 -->
### F2 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F2-QUERY — API-MDL-010            traces=API-MDL-010,REQ-MDL-013
POST `/api/v1/mdl/lookup-types/by-owner/search` · request `LookupTypeByOwnerSearchRequest`
{ filters[] } — **no sortField, no sortDirection, no page, no size** · response **a bare
array** of `OwnerGroupResponse` { ownerModuleCode, types[] } · kind **read query**
(ADR-MDL-002)
Cache key    : `[lookup-types-by-owner, filters]` — ownerModuleCode and key, and nothing more.
               No page or size belongs in this key because the endpoint accepts neither; adding
               them would key a variation the server cannot produce.
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `VALIDATION_ERROR` (400) → inline on the offending filter ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : n/a (a read). It is refreshed by SCR-MDL-001's type mutations through the shared
               `[lookup-types, *]` family, since a type created or deactivated there changes
               what this registry shows.
### F2-QUERY — API-MDL-011            traces=API-MDL-011,REQ-MDL-011,REQ-MDL-012
GET `/api/v1/mdl/lookups` · query param `type` = the lookup type's key · response **a bare
array** of `LookupValueResponse` — active values only, ordered by `sortOrder` · kind
**read query**
**Bound, and called by no screen** (ADR-MDL-007): the caller is a consuming module's backend
over the platform's in-process module interface, not a user with a screen. It is stated here so
the published surface is completely accounted for.
Errors       : `MDL-404-TYPE-KEY` (404) [REQ-MDL-012] → answered to the calling module — an
               unknown key is a not-found, never an empty success ·
               `ACCESS_DENIED` (403) → answered to the calling module
Cache key    : n/a — no client of this plan calls it
Invalidation : n/a. What a user can observe of this endpoint is indirect: deactivating a value
               or its type on SCR-MDL-001 is what makes it stop being returned (RULE-MDL-004).
### F2-SCREEN-INIT — SCR-MDL-002
Permission read : `MDL_TYPE_REGISTRY` present in the caller's effective menu → VIEW. This
                  screen has no other action.
Lookups used    : none
Foreign data    : the owner-module filter and the group headings resolve through UXD-MDL-001 —
                  the same shared hook SCR-MDL-001 uses, not a second call
Entity by id    : none — the groups carry their full type rows
### F2-FACADE — SCR-MDL-002
Composes     : API-MDL-010 · the UXD-MDL-001 hook
State it owns: the groups derived from the query's data, and the filter object (owner module,
               key) mirrored from the route's search params. No grouping and no count is
               composed here — both arrive in the response
Operations   : none — this screen writes nothing. Navigation to SCR-MDL-001 with a type
               selected is a route change, not an operation
<!-- SUB:F2-SCR-MDL-002:END -->

<!-- PHASE:F2:END -->

<!-- PHASE:F3:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 3 — F3 — Forms & Validators

One block per `RULE-*` enforced on a form, plus the field constraints the published DTOs state.
No frontend-only validation the SRS does not state; every message is read from its catalog
code, never hard-coded; the locale resolves session → browser → `ar`; and a caller without the
write permission is answered by the server rather than by a pre-emptively disabled field.
Schemas are written with `zod` + `react-hook-form`.

**No `LOOKUP_VALID` validator exists anywhere in this module.** MDL owns no coded list (SRS
§A6), so no field binds to an option set of lookup values. The one field with a constrained set
is `ownerModuleCode`, whose set is another module's registry — its validator is named in the
SCR-MDL-001 block below and binds to the runtime-loaded list of UXD-MDL-001, never to a static
list of module codes.

<!-- SUB:F3-SCR-MDL-001:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001 -->
### F3 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

Validation timing for this screen: **on blur for the unique key and code, on submit for the
rest** — declared once, and it holds for both the type form and the value form.
### F3-FIELD — SCR-MDL-001 (type, create)
key             · REQUIRED · LENGTH (maxLength 80, from `LookupTypeCreateRequest`) ·
                  UNIQUE_CHECK · when blur
ownerModuleCode · REQUIRED · LENGTH (maxLength 10) · BUSINESS_RULE (RULE-MDL-001) · when submit
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-MDL-001 (type, edit)
key, ownerModuleCode · read-only — not inputs at all; `LookupTypeUpdateRequest` carries neither
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-MDL-001 (value, create)
code            · REQUIRED · LENGTH (maxLength 50) · UNIQUE_CHECK (within the selected type —
                  RULE-MDL-002) · when blur
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder       · REQUIRED · when submit
### F3-FIELD — SCR-MDL-001 (value, edit)
code            · read-only — `LookupValueUpdateRequest` does not carry it
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder       · REQUIRED · when submit
UNIQUE_CHECK    : async, on blur — the type's `key` via `API-MDL-001` with an EQUALS filter;
                  the value's `code` via `API-MDL-005` with EQUALS filters on **both**
                  `lookupTypeId` and `code`, so the check's scope is the rule's scope. Neither
                  blocks submit on its own: the server's `MDL-409-TYPE-DUP` and
                  `MDL-409-VALUE-DUP` are the authority, routed inline to the same field. On
                  edit neither field is an input, so neither check runs.
### F3-VALIDATION — RULE-MDL-001      traces=REQ-MDL-002,AC-MDL-002
Statement : The system shall reject a lookup type registration whose owner module code has no
            ModuleRegistry row in the Security module.
Message   : from the catalog code `MDL-409-MODULE-NOT-REGISTERED` —
            ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" ·
            en: "The owning module is not registered in the Security module"
Scope     : CREATE
Field     : ownerModuleCode · kind BUSINESS_RULE · when submit
Validation shape : the control is a **select over the registered module codes** loaded through
            UXD-MDL-001, so the common case cannot be typed wrong at all; the validator asserts
            that the submitted value is one the runtime-loaded list contains, never that it is
            one of a static set. The server remains the authority — a module deregistered
            between load and submit is caught there — and the catalog message routes to this
            field. The rule's `Data source` is another module's registry, read SOFT at the
            application layer, so the client cannot decide it alone and does not try.
### F3-VALIDATION — RULE-MDL-002      traces=REQ-MDL-007,AC-MDL-007
Statement : The system shall reject a lookup value whose code already exists under the same
            lookup type.
Message   : from the catalog code `MDL-409-VALUE-DUP` —
            ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" ·
            en: "This code is already used within this type"
Scope     : CREATE
Field     : code (of the value) · kind UNIQUE_CHECK · when blur, and again on submit by the server
Validation shape : uniqueness is scoped to the parent type, never globally — the same code
            under another type is legitimate, and a global check would reject a value the
            server accepts. The async check is bound to the selected parent id.
### F3-VALIDATION — RULE-MDL-003      traces=REQ-MDL-003,AC-MDL-003
Statement : The system shall prevent editing a lookup type's key after creation.
Message   : the rule's own text — ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" ·
            en: "A lookup type's key cannot be changed after creation"
Scope     : UPDATE
Field     : key · kind BUSINESS_RULE · not a form check at all
Validation shape : there is **nothing to validate**: `key` is not an input on edit, because
            `LookupTypeUpdateRequest` does not carry it. The rule is expressed by the absence
            of the field rather than by a message on a control that would refuse. The form
            still *states* the rule beside the read-only key, so an editor learns why it cannot
            be changed instead of discovering a disabled control with no explanation.
### F3-VALIDATION — RULE-MDL-004      traces=REQ-MDL-004,AC-MDL-004
Statement : While a lookup type is inactive, the system shall exclude its values from consumer
            reads.
Message   : the rule's own text — ar: "هذا النوع معطّل حاليًا" ·
            en: "This lookup type is currently inactive"
Scope     : the deactivate action (API-MDL-004)
Field     : none — a row action · kind BUSINESS_RULE · when submit
Validation shape : **not a validation this form performs at all** — it is a consequence the
            deactivate confirmation names before the act: every consuming module stops
            receiving this type's values. The rule's text is shown as the state label on an
            inactive type row, so the same words explain the row and the warning. Nothing on
            this screen is hidden by it: the manager's value list (API-MDL-005) still shows the
            values, which is the difference between this screen and a consumer.
Business-code fields: `key` and `code` are both client-chosen strings, not platform-numbered,
and both are read-only after create (per the two update DTOs). Neither is generated or
predicted on the client.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE, UPDATE or DELETE receives `ACCESS_DENIED`
on submit and the form shows the localized forbidden message; fields are not pre-emptively
disabled, because no published endpoint tells the screen which actions the caller holds.
<!-- SUB:F3-SCR-MDL-001:END -->

<!-- SUB:F3-SCR-MDL-002:START traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001,SCR-MDL-002 -->
### F3 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

This screen has **no form**: SRS SCR-REQ-MDL-002 §B3 reads "read-only browse; no create/update
here", and every field of `OwnerGroupResponse` is read-only.
### F3-FIELD — SCR-MDL-002 (filters, not a form)
ownerModuleCode · optional · the select is the UXD-MDL-001 hook's list, so it offers only
                  registered module codes
key             · optional · LENGTH (maxLength 80) · a LIKE filter
Validation shape : filter validation only, written with `zod` over the route's search params so
                  that an address someone shared is validated the same way a typed filter is.
                  No business rule is enforced here, because nothing is written.
No RULE-* is enforced on this screen. RULE-MDL-004's effect is visible — a deactivated type
leaves this registry's active set — but the rule fires on the consumer read, not here.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen — the navigation
guard of SEC-FE stops the route.
<!-- SUB:F3-SCR-MDL-002:END -->

<!-- PHASE:F3:END -->

<!-- PHASE:F4:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 4 — F4 — Screens & Routes

One block per `SCR-*`: routes, chunk, guard, components, mode, facade, shared UI and
cross-module citations. Routes are named by the container pattern — `TREE_MASTER_DETAIL` → a
TreePage hosting the master list and its detail, with the list route registered **before** any
`:id` route; `FULL_PAGE` with no entry sub-view → a single Page and no entry route. One lazy
chunk per composite screen. Every `PERM_*` name below is the backend's, never invented here,
and every route sits under the module segment `/reference-data`.

<!-- SUB:F4-SCR-MDL-001:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001 -->
### F4 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F4-SCREEN — SCR-MDL-001            traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001
Routes       : base slug `lookups`, under the module segment `/reference-data` —
               `/reference-data/lookups` (the type list, registered **before** any `:id` route
               so a type id is never matched as the list itself) ·
               `/reference-data/lookups/new` (create a type — a **static** segment registered
               BEFORE the `:id` routes) ·
               `/reference-data/lookups/:typeId` (that type's values beside the list) ·
               `/reference-data/lookups/:typeId/edit` (edit the type) ·
               `/reference-data/lookups/:typeId/values/new` (create a value under it) ·
               `/reference-data/lookups/:typeId/values/:valueId/edit` (edit a value)
Chunk        : one lazy chunk for this composite screen — both panes and both forms share it;
               neither form is a second chunk
Guard        : every route element guarded by `PERM_MDL_LOOKUPS_VIEW`, evaluated as
               "`MDL_LOOKUPS` is present in the caller's effective menu". CREATE, UPDATE and
               DELETE are not readable from any published endpoint, so `/new`, `/edit` and the
               value routes carry the same VIEW guard and the server's 403 is the authority on
               the write itself.
Components   : `LookupsPage` (route-level, TREE_MASTER_DETAIL — hosts the type list and the
               value detail) · `LookupTypeList`, `LookupTypeFilters`, `LookupTypeForm`,
               `LookupValueTable`, `LookupValueFilters`, `LookupValueForm`,
               `ValueReorderHandle`, `DeactivateConfirm` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` and
               `/values/new` → CREATE, `/edit` → EDIT, `/:typeId` → VIEW — never from a parent
               prop
Facade       : the SCR-MDL-001 facade of F2; the page never calls a query directly
Shared UI    : split pane, data table, filter bar, text field, number field, select (the owner
               module), drag handle, confirmation dialog, inline field errors, localized
               message banner
Cross-module : UXD-MDL-001 (the owner module) — the one field on this screen whose
               authoritative source is another module
The selected type is a route param, so a type's value list is a linkable address and the
browser's back gesture returns to the list. Both levels show Deactivate and neither shows an
Activate: no endpoint exists for the second half (ADR-MDL-005). The drag handle submits the
whole ordered set through API-MDL-009 rather than writing one row's `sortOrder`.
<!-- SUB:F4-SCR-MDL-001:END -->

<!-- SUB:F4-SCR-MDL-002:START traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001,SCR-MDL-002 -->
### F4 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F4-SCREEN — SCR-MDL-002            traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001
Routes       : base slug `type-registry`, under `/reference-data` —
               `/reference-data/type-registry` — the only route; no `new`, no `:id`, no
               `:id/edit`, because this screen addresses no record it could edit. The owner
               module and the key filter live in the route's search params, so the browse IS
               its address
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_MDL_TYPE_REGISTRY_VIEW`, evaluated as
               "`MDL_TYPE_REGISTRY` is present in the caller's effective menu"
Components   : `TypeRegistryPage` (route-level, FULL_PAGE) · `RegistryFilters`,
               `OwnerGroupSection`, `RegistryTypeTable` (presentational)
Mode         : not applicable — no CREATE, EDIT or VIEW mode exists to resolve; this screen
               writes nothing
Facade       : the SCR-MDL-002 facade of F2
Shared UI    : filter bar, select (the owner module), section headings, data table, localized
               message banner
Cross-module : UXD-MDL-001 — here it is the grouping itself, not a field of a form
Each type row links to `/reference-data/lookups/:typeId`, which is SCR-MDL-001's own route and
carries its own guard — reviewing and managing are two steps of one task, and this screen does
neither half of the second. API-MDL-011 has no component and no route here (ADR-MDL-007).
<!-- SUB:F4-SCR-MDL-002:END -->

<!-- PHASE:F4:END -->

<!-- PHASE:SEC-FE:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 5 — SEC-FE

The frontend half of the security model, per `SCR-*`: the navigation guard and the per-action
UI behaviour. Permission names are the backend registry's and the SRS Access summary's, never
redeclared. One mechanism gates both screens — the **menu gate**: the screen's page code is
present in the effective menu the security module serves for this caller. Action-level
permissions are not readable from any published MDL endpoint, so an action's affordance renders
for a caller who holds the screen and the server's `ACCESS_DENIED` is the authority, shown as
its localized message. Never split — level-1 only.

### SEC-FE · SCR-MDL-001 — اللوكبات العامة / Generic Lookups
Permissions      : `PERM_MDL_LOOKUPS_VIEW`, `PERM_MDL_LOOKUPS_CREATE`,
`PERM_MDL_LOOKUPS_UPDATE`, `PERM_MDL_LOOKUPS_DELETE`
Navigation guard : `MDL_LOOKUPS` must be present in the caller's effective menu; a caller
without it is sent to the unauthorized destination, and every route of this screen — the list,
`new`, `:typeId`, `:typeId/edit` and both value routes — carries the same guard.
Per action       : VIEW → the gate above, exact, and it covers both panes: a caller who holds
the screen sees types and values alike. CREATE (a type, and a value under it), UPDATE (edit at
either level, and the reorder) and DELETE (deactivate at either level) → the affordances render
and `ACCESS_DENIED` from the server is shown as the localized forbidden message. DELETE here
means deactivate and nothing else: no hard delete exists at either level, which is why the SRS
Access summary's DELETE column reads "role-granted (deactivate)".
The screen-level grant is the whole granularity. Per-lookup-type permissions — letting a role
manage `USER_STATUS` but not `PAYMENT_METHOD` — are an explicit SRS scope exception
(§A2 Out of scope), so no per-type gate is drawn, attempted, or hinted at in the UI.

### SEC-FE · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner
Permissions      : `PERM_MDL_TYPE_REGISTRY_VIEW`
Navigation guard : `MDL_TYPE_REGISTRY` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE: the SRS Access
summary gives this screen VIEW alone, and the screen writes nothing. Its links into
SCR-MDL-001 are rendered unconditionally; the target route's own guard stops a caller who does
not hold that screen, so a reviewer who may browse but not manage sees the registry and is
refused at the door of the editor rather than shown a dead link.

**Across both screens.** A forbidden response is shown as its localized catalog message, never
as a silent no-op and never as a generic failure. An unauthenticated response returns the
caller to the platform's sign-in destination and discards the server-state cache, so no data of
the previous identity survives into the next. No screen composes a permission name, and no
screen holds a local copy of the caller's grants: the menu response is the single source, and a
failure to load it renders no MDL entry and grants no MDL route — access narrows, never widens.

<!-- PHASE:SEC-FE:END -->

<!-- PHASE:ALIGN-FE:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 6 — ALIGN-FE

The alignment self-check is this phase's content, and its `RESULT` row is written by the
orchestrator from the analyze report. Never split — level-1 only.

```
ALIGN-FE — MDL v1
row           backing check   assertion
SCREENS       orphans         both SCR-MDL-001 and SCR-MDL-002 are referenced by a plan block —
                              each has a block in F1, F2, F3 and F4 and an RF5 block in SEC-FE.
                              Every sub_bearing phase splits per screen — 8 SUB blocks, two
                              per phase — at a screen count of 2, because the count gate was
                              removed from the profile
UXD           orphans         UXD-MDL-001 is cited by a plan block — by both screens' F2
                              SCREEN-INIT blocks, by SCR-MDL-001's F3 validator for
                              RULE-MDL-001, and by both F4 Cross-module lines
TRACES        traces          every PHASE carries traces=; UXD-MDL-001 traces to its REQ and
                              its AC; every SCR traces to its REQ and to its UXD
API           traces          every API-MDL-* this plan cites is defined in the fetched
                              api-docs — through the API ID BINDING annex of ADR-MDL-001, and
                              never in the backend plan's contract table, which is the artifact
                              the three shape diffs belong to. No foreign module's API id is
                              cited here at all; the one cross-module endpoint this frontend
                              depends on is named in ui-ux-spec-mdl.md, where UXD-MDL-001 is
                              defined
FOREIGN       xref-surface    every reference to another module's surface resolves in that
                              module's own artifacts
REGISTRY      registry-agree  the UXD and both SCR defined here are in registry-exec-fe-mdl.md,
                              and nothing else is
LANGUAGES     languages       labels and messages in ar + en
MARKERS       markers         the parser reports no structural or semantic error for the
                              frontend track's exec plan
DECISIONS     refs-exist      every ADR this plan cites exists on disk in erp/decisions/MDL/ —
                              ADR-MDL-001 … ADR-MDL-007
COVERAGE      (the report)    C7.16, C7.18 and C7.20 — all three are P3.1
                              clauses over backend artifacts this stage does not write. No
                              C8.* or C9.* clause reported having examined nothing
RESULT        PASSED ✓ — 0 findings
```

### Operations coverage

| Operation | API | SCR action | Route | Status |
|---|---|---|---|---|
| search lookup types | API-MDL-001 | SCR-MDL-001 search | /reference-data/lookups | ✓ |
| create lookup type | API-MDL-002 | SCR-MDL-001 create type | /reference-data/lookups/new | ✓ |
| update lookup type | API-MDL-003 | SCR-MDL-001 edit type | /reference-data/lookups/:typeId/edit | ✓ |
| deactivate lookup type | API-MDL-004 | SCR-MDL-001 deactivate type | /reference-data/lookups/:typeId | ✓ |
| search lookup values of a type | API-MDL-005 | SCR-MDL-001 value list | /reference-data/lookups/:typeId | ✓ |
| create lookup value | API-MDL-006 | SCR-MDL-001 create value | /reference-data/lookups/:typeId/values/new | ✓ |
| update lookup value | API-MDL-007 | SCR-MDL-001 edit value | /reference-data/lookups/:typeId/values/:valueId/edit | ✓ |
| deactivate lookup value | API-MDL-008 | SCR-MDL-001 deactivate value | /reference-data/lookups/:typeId | ✓ |
| reorder lookup values | API-MDL-009 | SCR-MDL-001 drag to reorder | /reference-data/lookups/:typeId | ✓ |
| browse the registry by owner | API-MDL-010 | SCR-MDL-002 render | /reference-data/type-registry | ✓ |
| read values by key (consumer API) | API-MDL-011 | — a consuming module's backend call | — (ADR-MDL-007) | ✗ |
| activate a lookup type | — none published | SCR-MDL-001 — not drawn | — (ADR-MDL-005) | ✗ |
| activate a lookup value | — none published | SCR-MDL-001 — not drawn | — (ADR-MDL-005) | ✗ |
| read one type / one value by id | — none published | hydrated from the search cache | — (ADR-MDL-005) | ✗ |

Eleven rows carry a published endpoint; ten of those carry a route and a ✓. Four rows carry a
✗ with the ADR that explains it — one endpoint published for a caller that is not this frontend
(ADR-MDL-007), and three operations with no endpoint at all (ADR-MDL-005). No row is a ✗ for
want of a decision.

<!-- PHASE:ALIGN-FE:END -->

---

## Hand-off

The implementer reads the phases in profile order — F1 models, F2 hooks, F3 forms, F4 screens
and routes, SEC-FE guards — takes design intent from `ui-ux-spec-mdl.md`, and takes every
request and response shape from `_inputs/api-docs-mdl.md`. No route, component, permission or
field that is not traceable to an F-block above is invented: a gap is an ADR in
`erp/decisions/MDL/`, never an invention. Three response shapes travel in this module and the
difference is load-bearing — two paged reads, five bare arrays or single objects, and the rest
single objects — so no block may be read through an envelope another block declares. The plan
and its registry are split by the toolkit into `packages/frontend-execution/` and delivered on
the frontend delivery branch after the `gate:pass-2` verdict, then tagged.

══════════════════════════════════════════════════════════════════
