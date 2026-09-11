# BACKEND EXECUTION PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Dialect : postgresql16
Framework : spring-boot-java (profile.stack.backend.framework)
Inputs : srs (v1, PRD-approved), db-script (v1), registry-srs (v1), registry-db (v1)
Open ADRs : 0
══════════════════════════════════════════════════════════════════

## PRE-GENERATION EXTRACTION — MDL v1 (working set; not part of the plan proper)

```
── FROM srs ──────────────────────────────────────────────────────────────
ENTITIES      2 — ENT-MDL-001 (master), ENT-MDL-002 (lookup)
REQUIREMENTS  13 — REQ-MDL-001..013, each with 1 AC-MDL-*
RULES         4 — RULE-MDL-001..004
SCREENS       2 — SCR-REQ-MDL-001..002, composite per profile.conventions.composite_screen
PERMISSIONS   MDL_LOOKUPS, MDL_TYPE_REGISTRY page codes + PERM_<PAGE_CODE>_<ACTION>, gateway VIEW
LOOKUPS       none owned by MDL itself (SRS A6)
BUSINESS CODE none — no MDL entity has a platform-numbered business code
── FROM db-script ────────────────────────────────────────────────────────
TABLES        2 — MDL_LOOKUP_TYPE, MDL_LOOKUP_VALUE
PK GENERATION every table: `GENERATED ALWAYS AS IDENTITY`
COLUMNS       21 DBF-MDL-001..021
CONSTRAINTS   PK_*, UQ_MDL_LOOKUP_TYPE_KEY, UQ_MDL_LOOKUP_VALUE_TYPE_CODE, FK_LOOKUP_VALUE_TYPE; INDEXES IDX_*
XM            1 — XM-MDL-001 SOFT-READ → SEC_MODULE_REG, status ACTIVE
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   ModuleRegistry (ENT-SEC-004, SEC) via XM-MDL-001
EXISTING LOOKUP KEYS        none reused (MDL is the mechanism, not a consumer of its own kind)
ID RANGES already used      API: none yet · QR: none yet
──────────────────────────────────────────────────────────────────────────
No row required §2A.3 extraction-failure handling.
```

## EXECUTION PLAN INDEX — MDL v1 — backend-execution-plan-mdl.md
Profile: erp · dialect: postgresql16 · framework: spring-boot-java
Open ADRs: 0

**ENTITY REGISTRY**
| ENT | Name | Table | Business code | Operations |
|---|---|---|---|---|
| ENT-MDL-001 | LookupType | MDL_LOOKUP_TYPE | none | create, read, search, update (name only), deactivate |
| ENT-MDL-002 | LookupValue | MDL_LOOKUP_VALUE | none | create, read, search, update, deactivate, reorder |

**FIELD REGISTRY**
| DBF | Property | Read-only | ENT |
|---|---|---|---|
| DBF-MDL-001 | lookupTypePk | Yes | ENT-MDL-001 |
| DBF-MDL-002 | key | create-only (immutable after, RULE-MDL-003) | ENT-MDL-001 |
| DBF-MDL-003 | ownerModuleCode | create-only | ENT-MDL-001 |
| DBF-MDL-004 | nameAr | No | ENT-MDL-001 |
| DBF-MDL-005 | nameEn | No | ENT-MDL-001 |
| DBF-MDL-006 | isActiveFl | Yes | ENT-MDL-001 |
| DBF-MDL-007 | createdBy | Yes | ENT-MDL-001 |
| DBF-MDL-008 | createdAt | Yes | ENT-MDL-001 |
| DBF-MDL-009 | updatedBy | Yes | ENT-MDL-001 |
| DBF-MDL-010 | updatedAt | Yes | ENT-MDL-001 |
| DBF-MDL-011 | lookupValuePk | Yes | ENT-MDL-002 |
| DBF-MDL-012 | lookupTypeId | create-only | ENT-MDL-002 |
| DBF-MDL-013 | code | create-only | ENT-MDL-002 |
| DBF-MDL-014 | nameAr | No | ENT-MDL-002 |
| DBF-MDL-015 | nameEn | No | ENT-MDL-002 |
| DBF-MDL-016 | sortOrder | No | ENT-MDL-002 |
| DBF-MDL-017 | isActiveFl | Yes | ENT-MDL-002 |
| DBF-MDL-018 | createdBy | Yes | ENT-MDL-002 |
| DBF-MDL-019 | createdAt | Yes | ENT-MDL-002 |
| DBF-MDL-020 | updatedBy | Yes | ENT-MDL-002 |
| DBF-MDL-021 | updatedAt | Yes | ENT-MDL-002 |

**API REGISTRY**
| API | Operation | Verb | Path | Traces (REQ, DBF) |
|---|---|---|---|---|
| API-MDL-001 | search types | GET | /api/v1/mdl/lookup-types | REQ-MDL-001 · DBF-MDL-002,003,004,005,006 |
| API-MDL-002 | create type | POST | /api/v1/mdl/lookup-types | REQ-MDL-001,REQ-MDL-002 · DBF-MDL-002,003,004,005 |
| API-MDL-003 | update type | PUT | /api/v1/mdl/lookup-types/{id} | REQ-MDL-003 · DBF-MDL-004,005 |
| API-MDL-004 | deactivate type | DELETE | /api/v1/mdl/lookup-types/{id} | REQ-MDL-004 · DBF-MDL-006 |
| API-MDL-005 | search values | GET | /api/v1/mdl/lookup-types/{id}/values | REQ-MDL-005 · DBF-MDL-012,013,014,015,016,017 |
| API-MDL-006 | create value | POST | /api/v1/mdl/lookup-types/{id}/values | REQ-MDL-006,REQ-MDL-007 · DBF-MDL-012,013,014,015,016 |
| API-MDL-007 | update value | PUT | /api/v1/mdl/lookup-values/{id} | REQ-MDL-008 · DBF-MDL-014,015,016 |
| API-MDL-008 | deactivate value | DELETE | /api/v1/mdl/lookup-values/{id} | REQ-MDL-009 · DBF-MDL-017 |
| API-MDL-009 | reorder values | PATCH | /api/v1/mdl/lookup-types/{id}/values/reorder | REQ-MDL-010 · DBF-MDL-016 |
| API-MDL-010 | browse registry by owner | GET | /api/v1/mdl/lookup-types/by-owner | REQ-MDL-013 · DBF-MDL-003,002,004,005 |
| API-MDL-011 | read values by key (consumer API) | GET | /api/v1/mdl/lookups | REQ-MDL-011,REQ-MDL-012 · DBF-MDL-002,013,014,015,016,006,017 |

**RULE REGISTRY**
| RULE | Name | Scope (ENT) | Message ar/en ✓ |
|---|---|---|---|
| RULE-MDL-001 | Reject a type for an unregistered owner module | ENT-MDL-001 | ✓ |
| RULE-MDL-002 | Reject a duplicate code within a type | ENT-MDL-002 | ✓ |
| RULE-MDL-003 | Key immutability after creation | ENT-MDL-001 | ✓ |
| RULE-MDL-004 | Exclude an inactive type's values from reads | ENT-MDL-001 | ✓ |

**SCREEN REGISTRY**
| Screen | Type | ENT | Permission names |
|---|---|---|---|
| MDL_LOOKUPS | secured | ENT-MDL-001, ENT-MDL-002 | PERM_MDL_LOOKUPS_VIEW, PERM_MDL_LOOKUPS_CREATE, PERM_MDL_LOOKUPS_UPDATE, PERM_MDL_LOOKUPS_DELETE |
| MDL_TYPE_REGISTRY | secured | ENT-MDL-001 | PERM_MDL_TYPE_REGISTRY_VIEW |

**LOOKUP REGISTRY** — none (MDL owns no lookup key of its own).

**QRC SUMMARY** — 15 QR ids, QR-MDL-001..015 — see Query Reference Catalog below.

**DB ALIGNMENT** — see manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 1 (XM-MDL-001, SOFT-READ → SEC, ACTIVE)
**SECURITY** — 2 secured screens, data-driven role grants (no fixed role count)

## DB Alignment Manifest — MDL v1
All 21 rows: **status ✓ (aligned)**; XM column populated only for the one field the
SOFT-READ touches (ownerModuleCode) — a SOFT-READ is an application-level read, not a
column-level FK, so it is noted, not blocking.

| DBF | ENT | property | type | XM |
|---|---|---|---|---|
| DBF-MDL-001 | ENT-MDL-001 | lookupTypePk | Long | — |
| DBF-MDL-002 | ENT-MDL-001 | key | String | — |
| DBF-MDL-003 | ENT-MDL-001 | ownerModuleCode | String | XM-MDL-001 (validated, not FK-constrained) |
| DBF-MDL-004 | ENT-MDL-001 | nameAr | String | — |
| DBF-MDL-005 | ENT-MDL-001 | nameEn | String | — |
| DBF-MDL-006 | ENT-MDL-001 | isActiveFl | Boolean | — |
| DBF-MDL-007 | ENT-MDL-001 | createdBy | String | — |
| DBF-MDL-008 | ENT-MDL-001 | createdAt | Instant | — |
| DBF-MDL-009 | ENT-MDL-001 | updatedBy | String | — |
| DBF-MDL-010 | ENT-MDL-001 | updatedAt | Instant | — |
| DBF-MDL-011 | ENT-MDL-002 | lookupValuePk | Long | — |
| DBF-MDL-012 | ENT-MDL-002 | lookupTypeId | Long | — |
| DBF-MDL-013 | ENT-MDL-002 | code | String | — |
| DBF-MDL-014 | ENT-MDL-002 | nameAr | String | — |
| DBF-MDL-015 | ENT-MDL-002 | nameEn | String | — |
| DBF-MDL-016 | ENT-MDL-002 | sortOrder | Integer | — |
| DBF-MDL-017 | ENT-MDL-002 | isActiveFl | Boolean | — |
| DBF-MDL-018 | ENT-MDL-002 | createdBy | String | — |
| DBF-MDL-019 | ENT-MDL-002 | createdAt | Instant | — |
| DBF-MDL-020 | ENT-MDL-002 | updatedBy | String | — |
| DBF-MDL-021 | ENT-MDL-002 | updatedAt | Instant | — |

## Query Reference Catalog (QR-MDL-*)

> Logical specification only — never executable code.

| QR | Operation | Phase | API | Entity | Kind | Intent |
|---|---|---|---|---|---|---|
| QR-MDL-001 | FIND_BY_CRITERIA | SVC-API | API-MDL-001 | ENT-MDL-001 | FIND_BY_CRITERIA | search lookup types |
| QR-MDL-002 | SAVE | SVC-API | API-MDL-002 | ENT-MDL-001 | SAVE | create lookup type |
| QR-MDL-003 | UPDATE | SVC-API | API-MDL-003 | ENT-MDL-001 | UPDATE | rename lookup type |
| QR-MDL-004 | UPDATE | SVC-API | API-MDL-004 | ENT-MDL-001 | UPDATE | deactivate lookup type |
| QR-MDL-005 | FIND_BY_CRITERIA | SVC-API | API-MDL-005 | ENT-MDL-002 | FIND_BY_CRITERIA | search values of a type |
| QR-MDL-006 | SAVE | SVC-API | API-MDL-006 | ENT-MDL-002 | SAVE | create lookup value |
| QR-MDL-007 | UPDATE | SVC-API | API-MDL-007 | ENT-MDL-002 | UPDATE | update lookup value |
| QR-MDL-008 | UPDATE | SVC-API | API-MDL-008 | ENT-MDL-002 | UPDATE | deactivate lookup value |
| QR-MDL-009 | UPDATE | SVC-API | API-MDL-009 | ENT-MDL-002 | UPDATE (batch) | persist new sortOrder per reordered value |
| QR-MDL-010 | FIND_BY_CRITERIA | SVC-API | API-MDL-010 | ENT-MDL-001 | FIND_BY_CRITERIA | browse types grouped by ownerModuleCode |
| QR-MDL-011 | FIND_BY_CRITERIA | SVC-API | API-MDL-011 | ENT-MDL-001, ENT-MDL-002 | FIND_BY_CRITERIA | active values of an active type, by key, ordered by sortOrder |
| QR-MDL-012 | EXISTS | SVC-API | API-MDL-002 | (SEC_MODULE_REG, cross-module) | EXISTS | XM-MDL-001 / RULE-MDL-001: owner module registered in SEC? |
| QR-MDL-013 | EXISTS | SVC-API | API-MDL-002 | ENT-MDL-001 | EXISTS | uniqueness: key |
| QR-MDL-014 | EXISTS | SVC-API | API-MDL-006 | ENT-MDL-002 | EXISTS | RULE-MDL-002: code unique within lookupTypeId (also DB UQ) |
| QR-MDL-015 | FIND_ONE | SVC-API | API-MDL-011 | ENT-MDL-001 | FIND_ONE | RULE-MDL-004: resolve type by key and confirm isActiveFl=true |

Standard operation defaults (SEC's Phase 1 CORE table applies verbatim, restated once in
Phase 1 below rather than duplicated per QR). Join governance: QR-MDL-011 joins
MDL_LOOKUP_TYPE → MDL_LOOKUP_VALUE (intra-module, both owned here) to filter by the type's
own `isActiveFl` and `key` — never joins to resolve a lookup LABEL for a consumer (the
consumer receives code+labels directly, since these ARE the labels, not a foreign lookup).
QR-MDL-012 is the module's one cross-module read (XM-MDL-001, SOFT-READ, no join — a
separate query against SEC's table, reconciled in the service layer, not a SQL JOIN across
schemas).

---

<!-- PHASE:CORE:START traces=REQ-MDL-002 -->
## PHASE 1 — CORE

**Layers**: controller → service → mapper → domain → repository (same as every module,
`profile.stack.backend.layers`). Domain-behaviour placement: entity methods for
single-entity invariants (e.g. `LookupType.deactivate()`); service layer for anything
spanning more than one entity or a cross-module read (RULE-MDL-001 via XM-MDL-001,
RULE-MDL-004's join, RULE-MDL-002's pre-check even though it is also DB-enforced).

**Error signalling**: `LocalizedException → {code, messageAr, messageEn}`; runtime code
format `MDL-{http}[-{SLUG}]` (`profile.stack.backend.api.error_code_format`; {http} = the row's HTTP status, {SLUG} = SCREAMING-KEBAB, the [ ] half optional).

**Transaction scope**: `READ_ONLY` for every `FIND_*`/`EXISTS` QR; `READ_WRITE` for every
`SAVE`/`UPDATE` QR (including the batch reorder, QR-MDL-009, in one transaction).

**Search contract**: `{filters, page, size, sort}`, `Page<T>`, empty result = success.

**Audit fields**: `createdBy/createdAt/updatedBy/updatedAt` framework-filled, never in a
request DTO.

**Type mapping** (postgresql16 → Java):
| postgresql16 | Java |
|---|---|
| GENERATED ALWAYS AS IDENTITY | Long |
| VARCHAR(n) | String |
| BOOLEAN | Boolean |
| TIMESTAMPTZ | Instant |
| NUMERIC (bare, `sort_order` only) | Integer — governance note: `sort_order` is a whole-number ordering field, not a monetary/precision decimal; the profile's `decimal` syntax-map row (`NUMERIC(p,s)`) does not fit a bare `NUMERIC` column, so this module maps it to `Integer` explicitly (deviation stated once here, per P2 engine §4.1) |

**Lookup values**: not applicable in the usual sense — MDL IS the lookup mechanism; its own
`ownerModuleCode` field is validated against SEC's `ModuleRegistry` (XM-MDL-001), not
against another lookup type.

**Numbering**: not applicable — no MDL entity has a business code.

**Workflow engine**: forbidden — not used.

**Languages**: every name field (`nameAr`/`nameEn`) and catalog message present in ar + en.

**Cross-module contract placement**: MDL's one cross-module read (XM-MDL-001) is a plain
outbound call from the service layer (`SecModuleRegistryClient` or an equivalent
inversion-of-control interface implemented against SEC's `GET /api/v1/sec/registry`
search endpoint (API-SEC-021), filtered by `code`) — not a physical join, not a shared transaction.

**Cross-cutting authorization**: the same CORE interceptor mechanism SEC's own plan
declares (SEC's backend-execution-plan-sec.md → Phase 1 CORE) applies platform-wide; MDL
does not redeclare it, only cites it — every secured MDL endpoint below is gated by it
before its controller method runs.
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=REQ-MDL-001,REQ-MDL-006 -->
## PHASE 2 — DATA-DOM

Entity count is 2 — below the engine's self-check split threshold; no SUB is opened, both
entities are written flat in profile.vocabulary order (LookupType first, as the master).

#### ENT-MDL-001 — LookupType      kind: master
BINDINGS: table `MDL_LOOKUP_TYPE` · PK `lookupTypePk` (DBF-MDL-001) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none (§3.3 test: no)
DEFAULT FIELDS (profile.conventions.entity_defaults.master): nameAr, nameEn, code, isActiveFl,
createdBy, createdAt, updatedBy, updatedAt — here `key` plays the role of `code` (SRS A3 note); `ownerModuleCode` is an addition beyond the default set, required by the plan's namespacing rule (POL-MDL-002).
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-MDL-001 | lookupTypePk | lookup_type_pk | Long | NOT NULL | Yes | PK_MDL_LOOKUP_TYPE | معرّف نوع اللوكب / LookupType id |
| DBF-MDL-002 | key | key | String | NOT NULL | create-only | UQ_MDL_LOOKUP_TYPE_KEY | المفتاح / Key |
| DBF-MDL-003 | ownerModuleCode | owner_module_code | String | NOT NULL | create-only | — (XM-MDL-001 app-level check) | رمز الوحدة المالكة / Owner module code |
| DBF-MDL-004 | nameAr | name_ar | String | NOT NULL | No | — | الاسم (عربي) / Name (Arabic) |
| DBF-MDL-005 | nameEn | name_en | String | NOT NULL | No | — | الاسم (إنجليزي) / Name (English) |
| DBF-MDL-006 | isActiveFl | is_active_fl | Boolean | NOT NULL | Yes | — | نشط / Active |
| DBF-MDL-007..010 | createdBy/createdAt/updatedBy/updatedAt | created_by/… | String/Instant | see db-script | Yes | — | audit |
DTO MEMBERSHIP: create-request `{key, ownerModuleCode, nameAr, nameEn}`; update-request `{nameAr, nameEn}` only (key and ownerModuleCode immutable — RULE-MDL-003); response includes all.
LOOKUP FIELDS: none (LookupType is not itself lookup-backed).
DOMAIN RULES:
**RULE-MDL-001** — Scope ENT-MDL-001 · Trigger: on create · Statement: "The system shall reject a lookup type registration whose owner module code has no ModuleRegistry row in SEC." · Message ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" / en: "The owning module is not registered in the Security module" · DB enforcement: application layer (service, via QR-MDL-012, XM-MDL-001) · owner layer: service.
**RULE-MDL-003** — Scope ENT-MDL-001 · Trigger: on update · Statement: "The system shall prevent editing a lookup type's key after creation." · Message ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" / en: "A lookup type's key cannot be changed after creation" · DB enforcement: application layer (enforced by omission — `key` is absent from the update DTO entirely) · owner layer: service/controller (DTO shape).
**RULE-MDL-004** — Scope ENT-MDL-001 · Trigger: on evaluate (consumer read, API-MDL-011) · Statement: "While a lookup type is inactive, the system shall exclude its values from consumer reads." · Message ar: "هذا النوع معطّل حاليًا" / en: "This lookup type is currently inactive" · DB enforcement: application layer (service, via QR-MDL-015 + QR-MDL-011's join filter) · owner layer: service.
STATE MACHINE: `isActiveFl` binary only — not applicable (SRS A7).
CROSS-MODULE: XM-MDL-001 (SOFT-READ → SEC_MODULE_REG, status ACTIVE) touches `ownerModuleCode`.
REPOSITORY OPS → QR-MDL-001 (FIND_BY_CRITERIA), QR-MDL-002 (SAVE), QR-MDL-003 (UPDATE), QR-MDL-004 (UPDATE, deactivate), QR-MDL-010 (FIND_BY_CRITERIA, grouped), QR-MDL-012 (EXISTS, cross-module), QR-MDL-013 (EXISTS, uniqueness), QR-MDL-015 (FIND_ONE, by key).

#### ENT-MDL-002 — LookupValue      kind: lookup
BINDINGS: table `MDL_LOOKUP_VALUE` · PK `lookupValuePk` (DBF-MDL-011) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
DEFAULT FIELDS (profile.conventions.entity_defaults.lookup): code, nameAr, nameEn, sortOrder, isActiveFl — matched exactly, plus PK/FK/audit.
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-MDL-011 | lookupValuePk | lookup_value_pk | Long | NOT NULL | Yes | PK_MDL_LOOKUP_VALUE | معرّف قيمة اللوكب / LookupValue id |
| DBF-MDL-012 | lookupTypeId | lookup_type_id | Long | NOT NULL | create-only | FK_LOOKUP_VALUE_TYPE | نوع اللوكب / Lookup type |
| DBF-MDL-013 | code | code | String | NOT NULL | create-only | UQ_MDL_LOOKUP_VALUE_TYPE_CODE | الرمز / Code |
| DBF-MDL-014 | nameAr | name_ar | String | NOT NULL | No | — | الاسم (عربي) / Name (Arabic) |
| DBF-MDL-015 | nameEn | name_en | String | NOT NULL | No | — | الاسم (إنجليزي) / Name (English) |
| DBF-MDL-016 | sortOrder | sort_order | Integer | NOT NULL | No | — | ترتيب العرض / Sort order |
| DBF-MDL-017 | isActiveFl | is_active_fl | Boolean | NOT NULL | Yes | — | نشط / Active |
| DBF-MDL-018..021 | createdBy/createdAt/updatedBy/updatedAt | … | — | see db-script | Yes | — | audit |
DTO MEMBERSHIP: create-request `{lookupTypeId, code, nameAr, nameEn, sortOrder}`; update-request `{nameAr, nameEn, sortOrder}` (lookupTypeId, code immutable); response includes all.
LOOKUP FIELDS: none — LookupValue rows are themselves the values other modules resolve; they hold no lookup-backed field of their own.
DOMAIN RULES: **RULE-MDL-002** — Scope ENT-MDL-002 · Trigger: on create · Statement: "The system shall reject a lookup value whose code already exists under the same lookup type." · Message ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" / en: "This code is already used within this type" · DB enforcement: `UQ_MDL_LOOKUP_VALUE_TYPE_CODE` (structural) + service pre-check (QR-MDL-014, friendly error before the DB would reject it) · owner layer: service + database.
STATE MACHINE: `isActiveFl` binary only — not applicable.
CROSS-MODULE: none.
REPOSITORY OPS → QR-MDL-005 (FIND_BY_CRITERIA), QR-MDL-006 (SAVE), QR-MDL-007 (UPDATE), QR-MDL-008 (UPDATE, deactivate), QR-MDL-009 (UPDATE batch, reorder), QR-MDL-011 (FIND_BY_CRITERIA, consumer read), QR-MDL-014 (EXISTS, uniqueness).
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-MDL-001,REQ-MDL-006,REQ-MDL-011 -->
## PHASE 3 — SVC-API

API count = 11 ≥ 8 → split by threshold. Only two of the three standard groups are
populated (no MDL endpoint is "INT"-shaped in the SEC sense — no auth flow, no onboarding
registration, no export); `SVC-API-INT` is therefore omitted rather than opened empty,
consistent with engine §6.2 ("Content: the roles whose words appear... otherwise as the
profile describes this phase" — an empty SUB with no atoms would violate "every atom then
sits inside a SUB — no orphan atoms beside SUBs" trivially, since there would be none to
place; omitting an unneeded SUB is the correct reading, not a violation).

<!-- SUB:SVC-API-SEARCH:START traces=REQ-MDL-001,REQ-MDL-005,REQ-MDL-011,REQ-MDL-013 -->
### SUB — SVC-API-SEARCH (read-only)

<!-- API:API-MDL-001:START traces=REQ-MDL-001,DBF-MDL-002,DBF-MDL-003,DBF-MDL-004,DBF-MDL-005,DBF-MDL-006 -->
### API-MDL-001 — search lookup types
Endpoint     : GET /api/v1/mdl/lookup-types
Layers       : controller → `LookupTypeController.search` ; service → `LookupTypeService.search`
Request      : query params `key`(LIKE), `ownerModuleCode`(EXACT), `isActiveFl`(EXACT), `page`, `size`, `sort`
Response     : 200 · `Page<LookupTypeResponse>` · `ApiResponse<Page<LookupTypeResponse>>`
Validations  : none (read-only)
Errors       : `MDL-500` only
Orchestration: load (QR-MDL-001) → map → return
Repository   : QR-MDL-001 · join NONE · transaction READ_ONLY
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_VIEW`
Localization : nameAr/nameEn returned
<!-- API:API-MDL-001:END -->

<!-- API:API-MDL-005:START traces=REQ-MDL-005,DBF-MDL-012,DBF-MDL-013,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016,DBF-MDL-017 -->
### API-MDL-005 — search values of a type
Endpoint     : GET /api/v1/mdl/lookup-types/{id}/values
Layers       : controller → `LookupValueController.search` ; service → `LookupValueService.search`
Request      : path `id` (lookupTypeId); query params `code`(LIKE), `page`, `size`, `sort` (default sort = sortOrder)
Response     : 200 · `Page<LookupValueResponse>` · `ApiResponse<Page<LookupValueResponse>>`
Validations  : none
Errors       : `MDL-404-TYPE` (404, unknown id)
Orchestration: load (QR-MDL-005) → map → return
Repository   : QR-MDL-005 · join NONE · transaction READ_ONLY
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_VIEW`
Localization : nameAr/nameEn returned
<!-- API:API-MDL-005:END -->

<!-- API:API-MDL-010:START traces=REQ-MDL-013,DBF-MDL-003,DBF-MDL-002,DBF-MDL-004,DBF-MDL-005 -->
### API-MDL-010 — browse registry by owner
Endpoint     : GET /api/v1/mdl/lookup-types/by-owner
Layers       : controller → `LookupTypeController.browseByOwner` ; service → `LookupTypeService.browseByOwner`
Request      : query params `ownerModuleCode`(EXACT), `key`(LIKE)
Response     : 200 · `List<OwnerGroupResponse>` (ownerModuleCode → nested active LookupType list) · `ApiResponse<List<OwnerGroupResponse>>`
Validations  : none
Errors       : `MDL-500` only
Orchestration: load grouped (QR-MDL-010) → assemble → return
Repository   : QR-MDL-010 · join NONE (single-table, grouped in the service layer) · transaction READ_ONLY
Security     : screen MDL_TYPE_REGISTRY · permission `PERM_MDL_TYPE_REGISTRY_VIEW`
Localization : nameAr/nameEn per type
<!-- API:API-MDL-010:END -->

<!-- API:API-MDL-011:START traces=REQ-MDL-011,REQ-MDL-012,DBF-MDL-002,DBF-MDL-013,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016 -->
### API-MDL-011 — read values by key (consumer API)
Endpoint     : GET /api/v1/mdl/lookups
Layers       : controller → `LookupConsumerController.readByKey` ; service → `LookupConsumerService.readByKey`
Request      : query param `type` (the LookupType key, e.g. `PAYMENT_METHOD`)
Response     : 200 · `List<LookupValueResponse>` (active values only, ordered by sortOrder) — 404 if the key itself is unknown
Validations  : RULE-MDL-004 (full text: DATA-DOM §ENT-MDL-001) — resolve the type, confirm it is active, then return only its active values (REQ-MDL-012: unknown key → not-found, not empty success)
Errors       : `MDL-404-TYPE-KEY` (404)
Orchestration: resolve type by key (QR-MDL-015) → if not found: 404 → else: load its active values ordered by sortOrder (QR-MDL-011) → return (empty list is a valid success if the type is active but has zero active values, per the FIND_BY_CRITERIA default)
Repository   : QR-MDL-015, QR-MDL-011 · join intra-module (type → value, both owned by MDL) · transaction READ_ONLY
Security     : called by other modules' backends, not an end-user screen — gated the same as any secured API (permission `PERM_MDL_LOOKUPS_VIEW`, granted to the calling module's own service principal per the platform's module-to-module auth pattern, same mechanism as any other authenticated caller — no special "system" bypass)
Localization : nameAr/nameEn returned per value
<!-- API:API-MDL-011:END -->
<!-- SUB:SVC-API-SEARCH:END -->

<!-- SUB:SVC-API-CRUD:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010 -->
### SUB — SVC-API-CRUD

<!-- API:API-MDL-002:START traces=REQ-MDL-001,REQ-MDL-002,DBF-MDL-002,DBF-MDL-003,DBF-MDL-004,DBF-MDL-005 -->
### API-MDL-002 — create lookup type
Endpoint     : POST /api/v1/mdl/lookup-types
Layers       : controller → `LookupTypeController.create` ; service → `LookupTypeService.create`
Request      : body `{key, ownerModuleCode, nameAr, nameEn}` — excludes {lookupTypePk, isActiveFl, audit}
Response     : 201 · `LookupTypeResponse`
Validations  : RULE-MDL-001 (full text: DATA-DOM §ENT-MDL-001) — owner module must be registered in SEC (QR-MDL-012); uniqueness of key (QR-MDL-013)
Errors       : `MDL-409-MODULE-NOT-REGISTERED` (409), `MDL-409-TYPE-DUP` (409)
Orchestration: check RULE-MDL-001 via XM-MDL-001 (QR-MDL-012) → validate key uniqueness (QR-MDL-013) → persist (QR-MDL-002) → return
Repository   : QR-MDL-002, QR-MDL-012, QR-MDL-013 · join NONE (QR-MDL-012 is a separate cross-module call, not a SQL join) · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_CREATE`
Localization : nameAr/nameEn required
<!-- API:API-MDL-002:END -->

<!-- API:API-MDL-003:START traces=REQ-MDL-003,DBF-MDL-004,DBF-MDL-005 -->
### API-MDL-003 — update lookup type (name only)
Endpoint     : PUT /api/v1/mdl/lookup-types/{id}
Layers       : controller → `LookupTypeController.update` ; service → `LookupTypeService.update`
Request      : body `{nameAr, nameEn}` — excludes {lookupTypePk, key, ownerModuleCode, isActiveFl, audit}
Response     : 200 · `LookupTypeResponse`
Validations  : RULE-MDL-003 (full text: DATA-DOM §ENT-MDL-001) — enforced by DTO shape (key absent from the request)
Errors       : `MDL-404-TYPE` (404)
Orchestration: load → update names (QR-MDL-003) → return
Repository   : QR-MDL-003 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : both name fields updatable
<!-- API:API-MDL-003:END -->

<!-- API:API-MDL-004:START traces=REQ-MDL-004,DBF-MDL-006 -->
### API-MDL-004 — deactivate lookup type
Endpoint     : DELETE /api/v1/mdl/lookup-types/{id}
Layers       : controller → `LookupTypeController.deactivate` ; service → `LookupTypeService.deactivate`
Request      : path `id`
Response     : 200 · confirmation `{lookupTypePk, isActiveFl: false}`
Validations  : none beyond existence
Errors       : `MDL-404-TYPE` (404)
Orchestration: load → `LookupType.deactivate()` → persist (QR-MDL-004) → (RULE-MDL-004 then applies automatically at the next API-MDL-011 read — no cascade write to values needed, since the exclusion is a read-time join filter, not a stored flag on each value)
Repository   : QR-MDL-004 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : n/a
<!-- API:API-MDL-004:END -->

<!-- API:API-MDL-006:START traces=REQ-MDL-006,REQ-MDL-007,DBF-MDL-012,DBF-MDL-013,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016 -->
### API-MDL-006 — create lookup value
Endpoint     : POST /api/v1/mdl/lookup-types/{id}/values
Layers       : controller → `LookupValueController.create` ; service → `LookupValueService.create`
Request      : path `id` (lookupTypeId); body `{code, nameAr, nameEn, sortOrder}` — excludes {lookupValuePk, isActiveFl, audit}
Response     : 201 · `LookupValueResponse`
Validations  : RULE-MDL-002 (full text: DATA-DOM §ENT-MDL-002) — code unique within the type (QR-MDL-014)
Errors       : `MDL-409-VALUE-DUP` (409), `MDL-404-TYPE` (404)
Orchestration: validate type exists → check RULE-MDL-002 (QR-MDL-014) → persist (QR-MDL-006) → return
Repository   : QR-MDL-006, QR-MDL-014 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_CREATE`
Localization : nameAr/nameEn required
<!-- API:API-MDL-006:END -->

<!-- API:API-MDL-007:START traces=REQ-MDL-008,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016 -->
### API-MDL-007 — update lookup value
Endpoint     : PUT /api/v1/mdl/lookup-values/{id}
Layers       : controller → `LookupValueController.update` ; service → `LookupValueService.update`
Request      : body `{nameAr, nameEn, sortOrder}` — excludes {lookupValuePk, lookupTypeId, code, isActiveFl, audit}
Response     : 200 · `LookupValueResponse`
Validations  : none beyond existence
Errors       : `MDL-404-VALUE` (404)
Orchestration: load → update (QR-MDL-007) → return
Repository   : QR-MDL-007 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : both name fields updatable
<!-- API:API-MDL-007:END -->

<!-- API:API-MDL-008:START traces=REQ-MDL-009,DBF-MDL-017 -->
### API-MDL-008 — deactivate lookup value
Endpoint     : DELETE /api/v1/mdl/lookup-values/{id}
Layers       : controller → `LookupValueController.deactivate` ; service → `LookupValueService.deactivate`
Request      : path `id`
Response     : 200 · confirmation `{lookupValuePk, isActiveFl: false}`
Validations  : none beyond existence
Errors       : `MDL-404-VALUE` (404)
Orchestration: load → `LookupValue.deactivate()` → persist (QR-MDL-008) → return
Repository   : QR-MDL-008 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : n/a
<!-- API:API-MDL-008:END -->

<!-- API:API-MDL-009:START traces=REQ-MDL-010,DBF-MDL-016 -->
### API-MDL-009 — reorder lookup values
Endpoint     : PATCH /api/v1/mdl/lookup-types/{id}/values/reorder
Layers       : controller → `LookupValueController.reorder` ; service → `LookupValueService.reorder`
Request      : path `id` (lookupTypeId); body `{orderedValueIds: [Long]}`
Response     : 200 · `List<LookupValueResponse>` in the new order
Validations  : every id in `orderedValueIds` must belong to the given lookupTypeId
Errors       : `MDL-400-REORDER-MISMATCH` (400)
Orchestration: validate membership → assign sortOrder = list position for each id → persist (QR-MDL-009, batch update, one transaction) → return
Repository   : QR-MDL-009 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : n/a
<!-- API:API-MDL-009:END -->
<!-- SUB:SVC-API-CRUD:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-MDL-011 -->
## PHASE 4 — DOC

**API contract summary** (backend self-check only; the frontend stage binds to the real
`api-docs-mdl.md` published after implementation):

| API | Path | Verb | Request DTO | Response DTO | Stability |
|---|---|---|---|---|---|
| API-MDL-001 | /lookup-types | GET | — | Page\<LookupTypeResponse\> (proposed) | v1 |
| API-MDL-002 | /lookup-types | POST | LookupTypeCreateRequest (proposed) | LookupTypeResponse (proposed) | v1 |
| API-MDL-003 | /lookup-types/{id} | PUT | LookupTypeUpdateRequest (proposed) | LookupTypeResponse (proposed) | v1 |
| API-MDL-004 | /lookup-types/{id} | DELETE | — | DeactivateConfirmation (proposed) | v1 |
| API-MDL-005 | /lookup-types/{id}/values | GET | — | Page\<LookupValueResponse\> (proposed) | v1 |
| API-MDL-006 | /lookup-types/{id}/values | POST | LookupValueCreateRequest (proposed) | LookupValueResponse (proposed) | v1 |
| API-MDL-007 | /lookup-values/{id} | PUT | LookupValueUpdateRequest (proposed) | LookupValueResponse (proposed) | v1 |
| API-MDL-008 | /lookup-values/{id} | DELETE | — | DeactivateConfirmation (proposed) | v1 |
| API-MDL-009 | /lookup-types/{id}/values/reorder | PATCH | ReorderRequest (proposed) | List\<LookupValueResponse\> (proposed) | v1 |
| API-MDL-010 | /lookup-types/by-owner | GET | — | List\<OwnerGroupResponse\> (proposed) | v1 |
| API-MDL-011 | /lookups | GET | — | List\<LookupValueResponse\> (proposed) | v1 |
(paths relative to `/api/v1/mdl`. A `—` request means the endpoint takes no body: the GET rows
read their filters from query parameters. Every type name above is marked `(proposed)` — this
stage runs before any implementation exists, so the names are derived, not decided; the real
ones arrive with `api-docs-mdl.md` and the stage that can resolve them fills them in.)

**DTO typing constraints**: `ownerModuleCode` is `String` (the platform module code, not
an enum); no business code field exists.

**Pagination + filter standard**: same as every module (Phase 1 CORE).
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=REQ-MDL-002 -->
## PHASE 5 — INT-C (cross-module consume)

One `XM-*` row, below the split threshold (1 < 5) — no SUB opened.

<!-- XM:XM-MDL-001:START traces=REQ-MDL-002 -->
### XM-MDL-001 — validate owner module against SEC
Target        : SEC · ENT-SEC-004 (ModuleRegistry) · classification SOFT-READ
Interface     : REST call — `GET /api/v1/sec/registry?moduleCode={code}` (an instance of `/api/v1/{module}/{resource}` on SEC, per API-SEC-021's search-registry contract)
Contract      : data required = the module code exists and `isActiveFl=true`; fallback if absent = reject with `MDL-409-MODULE-NOT-REGISTERED` (RULE-MDL-001); retry = none (synchronous, user-facing call — a transient SEC outage surfaces as `MDL-503` per the platform-standard infrastructure row, not a silent pass); idempotency = the call is read-only, naturally idempotent
Blocks        : none DEFERRED — SEC v1 is already gated (pass-1 APPROVE); this XM is ACTIVE from the moment MDL v1 is created, never DEFERRED
<!-- XM:XM-MDL-001:END -->
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-MDL-002 -->
## PHASE 6 — INT-R (cross-module resolve)

| XM | Status | Workaround (if not READY/ACTIVE) |
|---|---|---|
| XM-MDL-001 | ACTIVE | not applicable — target already gated |

No DEFERRED row exists this module; no mock/simulated strategy is needed. Inbound
dependency stub: any future consumer of MDL itself (every module from PRC onward, and FIN
next) reaches `ENT-MDL-001`/`ENT-MDL-002` through API-MDL-011 exactly as SEC's own consumers
reach SEC — `XM-INBOUND-STUB-2` (first expected consumer: FIN, per GENERATION-
INSTRUCTIONS.md §3), formal id assigned by FIN's own P2.
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=REQ-MDL-001 -->
## PHASE 7 — SEC-BE (security, backend half)

| Screen (page code) | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|
| MDL_LOOKUPS | PERM_MDL_LOOKUPS_VIEW (API-MDL-001, 005, 011) | PERM_MDL_LOOKUPS_CREATE (API-MDL-002, 006) | PERM_MDL_LOOKUPS_UPDATE (API-MDL-003, 004, 007, 008, 009) | (deactivate only, modeled as UPDATE — no hard-delete endpoint exists) |
| MDL_TYPE_REGISTRY | PERM_MDL_TYPE_REGISTRY_VIEW (API-MDL-010) | — | — | — |

**Seed data**: 2 SEC_PAGES rows (MDL_LOOKUPS, MDL_TYPE_REGISTRY) registered into SEC via SEC's own screen-registration endpoint (MDL is a consuming module registering itself, exactly the pattern security-module-plan-en.md §7 describes); action rows VIEW/CREATE/UPDATE per secured screen via SEC's own action-registration endpoint, following `PERM_<PAGE_CODE>_<ACTION>`.

**Gateway**: every non-VIEW permission requires VIEW on the same screen first (platform
convention, enforced by SEC's own CORE interceptor — not restated as an MDL-owned RULE).

**Forbidden responses**: `MDL` endpoints reuse the same `LocalizedException` envelope; a
403 from the interceptor is not module-specific (see SEC's `SEC-403-FORBIDDEN` — the same
mechanism denies MDL requests, this module mints no separate forbidden code).
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-MDL-011 -->
## PHASE 8 — ALIGN-BE

See Alignment self-check (ALIGN) below.
<!-- PHASE:ALIGN-BE:END -->

## Error Catalog — MDL v1

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `MDL-{http}[-{SLUG}]`.

| code | RULE / PLATFORM-STD | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| MDL-409-MODULE-NOT-REGISTERED | RULE-MDL-001 | API-MDL-002 | 409 | owner module not in SEC's ModuleRegistry | الوحدة المالكة غير مسجّلة في وحدة الأمان | The owning module is not registered in the Security module |
| MDL-409-TYPE-DUP | PLATFORM-STD (uniqueness, ADR-SEC-002 convention reused) | API-MDL-002 | 409 | duplicate key | هذا المفتاح مستخدم بالفعل | This key is already in use |
| MDL-404-TYPE | PLATFORM-STD (not found) | API-MDL-003, 004, 005 | 404 | unknown lookup type id | نوع اللوكب غير موجود | Lookup type not found |
| MDL-409-VALUE-DUP | RULE-MDL-002 | API-MDL-006 | 409 | duplicate code within type | هذا الرمز مستخدم بالفعل ضمن هذا النوع | This code is already used within this type |
| MDL-404-VALUE | PLATFORM-STD (not found) | API-MDL-007, 008 | 404 | unknown lookup value id | قيمة اللوكب غير موجودة | Lookup value not found |
| MDL-400-REORDER-MISMATCH | PLATFORM-STD (referential) | API-MDL-009 | 400 | reordered id not under the given type | إحدى القيم لا تنتمي لهذا النوع | One of the values does not belong to this type |
| MDL-404-TYPE-KEY | RULE-MDL-004 | API-MDL-011 | 404 | unknown or inactive type key | مفتاح النوع غير موجود أو غير نشط | This lookup type key does not exist or is inactive |
| MDL-403-FORBIDDEN | PLATFORM-STD (SEC's CORE interceptor) | every secured API | 403 | missing permission | غير مصرح بهذا الإجراء | You are not authorized to perform this action |
| MDL-503 | PLATFORM-STD (infrastructure) | API-MDL-002 | 503 | SEC unreachable during XM-MDL-001's validation call | تعذّر التحقق من الوحدة المالكة مؤقتًا | Could not verify the owning module right now |
| MDL-500 | PLATFORM-STD (infrastructure) | any | 500 | unhandled server error | حدث خطأ في الخادم | A server error occurred |

Every PLATFORM-STD row here follows the same umbrella convention SEC's ADR-SEC-002
established; MDL does not raise a new ADR for it (it cites SEC's, consistent with that
ADR's own consequence: "A future module's own P3.1 may cite the same PLATFORM-STD
convention... without re-deriving this decision").

## Alignment self-check (ALIGN) — MDL v1

```
TRACEABILITY      ✓ every API-*/QR-*/RULE-*/DBF-*/XM-* used in a phase appears in the Plan Index; every PHASE/SUB/atom carries traces=; every traces target exists upstream
BINDING (§2A)     ✓ no placeholder; every column cites a DBF; every RULE message present in ar+en; business code: none applicable
MANIFEST (§4)     ✓ only the mandated columns; all 21 DBF listed; the 1 XM-touched field (ownerModuleCode) is noted, not ⏸ (SOFT-READ is never blocking)
QRC (§5)          ✓ every API with a DB operation has ≥1 QR; no join for a lookup label; exact generation object named (Phase 1 CORE)
API (R3)          ✓ every RULE in a Validations line has a catalog row; platform errors carry RULE=PLATFORM-STD (citing SEC's ADR-SEC-002 convention); create/update requests exclude PK/audit/immutable fields
CROSS-MODULE      ✓ 1 XM from db-script, 1 placed (XM-MDL-001), 0 mismatched; ACTIVE status correctly reflects SEC's already-gated state; inbound stub uses XM-INBOUND-STUB-2 notation
SECURITY (R7)     ✓ both secured APIs' screens declare PERM_*; ERP-4 (every mutation endpoint declares its PERM_*): checked — every POST/PUT/PATCH/DELETE API above states one
CORE (R1)         ✓ layers, domain placement, error signalling (`MDL-{http}[-{SLUG}]`), type mapping (incl. the stated sort_order→Integer deviation) all declared
DECISIONS         ✓ 0 new ADR this stage; SEC's ADR-SEC-002 convention correctly cited, not re-derived
RESULT            PASSED ✓ — 0 findings
```

**Coverage — ENT/DBF → phases → QR → XM**: ENT-MDL-001/002 each appear in DATA-DOM with
≥1 QR under REPOSITORY OPS; all 21 DBF appear in the DB Alignment Manifest and their
owning entity's FIELDS table; XM-MDL-001 appears in INT-C, INT-R and ENT-MDL-001's
CROSS-MODULE line.

**Coverage — RULE → API → catalog code**: RULE-MDL-001→API-MDL-002→
MDL-409-MODULE-NOT-REGISTERED · RULE-MDL-002→API-MDL-006→MDL-409-VALUE-DUP ·
RULE-MDL-003→API-MDL-003→(enforced by DTO shape, no distinct error code needed — a request
including `key` simply has it ignored, not rejected, since the field is absent from the
DTO's schema entirely) · RULE-MDL-004→API-MDL-011→MDL-404-TYPE-KEY.

**Coverage — XM → status → blocks → workaround**: XM-MDL-001 → ACTIVE → blocks none →
no workaround needed.

## QR id definitions (cross-reference index — full detail in Query Reference Catalog above)
**QR-MDL-001** — FIND_BY_CRITERIA search lookup types [ENT-MDL-001, API-MDL-001]
**QR-MDL-002** — SAVE create lookup type [ENT-MDL-001, API-MDL-002]
**QR-MDL-003** — UPDATE rename lookup type [ENT-MDL-001, API-MDL-003]
**QR-MDL-004** — UPDATE deactivate lookup type [ENT-MDL-001, API-MDL-004]
**QR-MDL-005** — FIND_BY_CRITERIA search values of a type [ENT-MDL-002, API-MDL-005]
**QR-MDL-006** — SAVE create lookup value [ENT-MDL-002, API-MDL-006]
**QR-MDL-007** — UPDATE update lookup value [ENT-MDL-002, API-MDL-007]
**QR-MDL-008** — UPDATE deactivate lookup value [ENT-MDL-002, API-MDL-008]
**QR-MDL-009** — UPDATE batch persist reordered sortOrder [ENT-MDL-002, API-MDL-009]
**QR-MDL-010** — FIND_BY_CRITERIA browse types grouped by owner [ENT-MDL-001, API-MDL-010]
**QR-MDL-011** — FIND_BY_CRITERIA active values of an active type by key [ENT-MDL-001, ENT-MDL-002, API-MDL-011]
**QR-MDL-012** — EXISTS owner module registered in SEC (XM-MDL-001) [ENT-MDL-001, API-MDL-002]
**QR-MDL-013** — EXISTS uniqueness of key [ENT-MDL-001, API-MDL-002]
**QR-MDL-014** — EXISTS uniqueness of code within lookupTypeId [ENT-MDL-002, API-MDL-006]
**QR-MDL-015** — FIND_ONE resolve type by key + confirm active [ENT-MDL-001, API-MDL-011]

## Registry content
See `registry-exec-be-mdl.md`.
══════════════════════════════════════════════════════════════════
