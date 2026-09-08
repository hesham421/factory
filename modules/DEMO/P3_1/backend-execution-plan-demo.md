# BACKEND EXECUTION PLAN — Daily Notes / Demo (DEMO) v1
══════════════════════════════════════════════════════════════════
Profile: erp · dialect: postgresql16 · framework: profile.stack.backend.framework
Open ADRs: 2 — decisions/DEMO/ADR-DEMO-001.md, decisions/DEMO/ADR-DEMO-002.md
══════════════════════════════════════════════════════════════════

## EXECUTION PLAN INDEX — DEMO v1

ENTITY REGISTRY
| ENT | Name | Table | Business code | Operations |
|---|---|---|---|---|
| ENT-DEMO-001 | Note | demo_note | none (§3.3 test — no) | create, search, read, update, deactivate |

FIELD REGISTRY
| DBF | Property | Read-only? | ENT |
|---|---|---|---|
| DBF-DEMO-001 | id | yes (system) | ENT-DEMO-001 |
| DBF-DEMO-002 | title | no | ENT-DEMO-001 |
| DBF-DEMO-003 | content | no | ENT-DEMO-001 |
| DBF-DEMO-004 | activeFl | no (system-flipped on deactivate only) | ENT-DEMO-001 |
| DBF-DEMO-005 | createdBy | yes (system) | ENT-DEMO-001 |
| DBF-DEMO-006 | createdAt | yes (system) | ENT-DEMO-001 |
| DBF-DEMO-007 | updatedBy | yes (system) | ENT-DEMO-001 |
| DBF-DEMO-008 | updatedAt | yes (system) | ENT-DEMO-001 |

API REGISTRY
| API | Operation | Verb | Path | Traces (REQ, DBF) |
|---|---|---|---|---|
| API-DEMO-001 | create note | POST | /api/v1/demo/notes | REQ-DEMO-001; DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003 |
| API-DEMO-002 | search notes | GET | /api/v1/demo/notes | REQ-DEMO-002; DBF-DEMO-002,DBF-DEMO-008 |
| API-DEMO-003 | read note | GET | /api/v1/demo/notes/{id} | REQ-DEMO-003; DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003 |
| API-DEMO-004 | update note | PUT | /api/v1/demo/notes/{id} | REQ-DEMO-004; DBF-DEMO-002,DBF-DEMO-003,DBF-DEMO-008 |
| API-DEMO-005 | deactivate note | DELETE | /api/v1/demo/notes/{id} | REQ-DEMO-005; DBF-DEMO-004 |

RULE REGISTRY
| RULE | Name | Scope | ENT | Message ar/en |
|---|---|---|---|---|
| RULE-DEMO-001 | title required | create/update | ENT-DEMO-001 | ✓ |
| RULE-DEMO-002 | content max length (4000) | create/update | ENT-DEMO-001 | ✓ |

SCREEN REGISTRY
| Screen | Type | ENT | Permission names |
|---|---|---|---|
| SCR-REQ-DEMO-001 (Daily Notes) | composite Search+Entry | ENT-DEMO-001 | PERM_PAGE_DEMO_NOTES_VIEW, PERM_PAGE_DEMO_NOTES_CREATE, PERM_PAGE_DEMO_NOTES_UPDATE, PERM_PAGE_DEMO_NOTES_DELETE |

LOOKUP REGISTRY
None — DEMO owns no lookup (SRS A6: none).

QRC SUMMARY
| QR | Operation | Phase | ENT |
|---|---|---|---|
| QR-DEMO-001 | SAVE | SVC-API | ENT-DEMO-001 |
| QR-DEMO-002 | FIND_BY_CRITERIA | SVC-API | ENT-DEMO-001 |
| QR-DEMO-003 | FIND_ONE | SVC-API | ENT-DEMO-001 |
| QR-DEMO-004 | UPDATE | SVC-API | ENT-DEMO-001 |
| QR-DEMO-005 | UPDATE (flag flip) | SVC-API | ENT-DEMO-001 |

DB ALIGNMENT
See manifest below — ALIGNED ✓, issues: 0

XM STATUS
0 — DEMO declares no cross-module dependency in v1 (db-script XM REGISTER: none).

SECURITY
1 screen × 1 role (USER)

## DB ALIGNMENT MANIFEST — DEMO v1
| DBF-* | ENT-* | plan property | plan type | XM-* | status |
|---|---|---|---|---|---|
| DBF-DEMO-001 | ENT-DEMO-001 | id | Long | — | ✓ |
| DBF-DEMO-002 | ENT-DEMO-001 | title | String | — | ✓ |
| DBF-DEMO-003 | ENT-DEMO-001 | content | String | — | ✓ |
| DBF-DEMO-004 | ENT-DEMO-001 | activeFl | boolean | — | ✓ |
| DBF-DEMO-005 | ENT-DEMO-001 | createdBy | String | — | ✓ |
| DBF-DEMO-006 | ENT-DEMO-001 | createdAt | Instant | — | ✓ |
| DBF-DEMO-007 | ENT-DEMO-001 | updatedBy | String | — | ✓ |
| DBF-DEMO-008 | ENT-DEMO-001 | updatedAt | Instant | — | ✓ |

Legend  ✓ aligned · ✗ type mismatch (finding) · ⏸ deferred XM. No derived/computed properties in this module.

## Query Reference Catalog (QR-*)

### QR-DEMO-001 — create note
Phase        : SVC-API
API          : API-DEMO-001
Entity       : ENT-DEMO-001
Operation    : SAVE
Intent       : persist a new note owned by the current user, system-filling PK and audit fields.
Logical spec : INSERT INTO demo_note (title, content, is_active_fl, created_by, created_at, updated_by, updated_at) VALUES (:title, :content, TRUE, :currentUser, now(), :currentUser, now())
Join         : NONE
Transaction  : READ_WRITE
Pagination   : NO
Filters      : none
Result shape : full entity
Null handling: not applicable (title/content required, RULE-DEMO-001/002 validated before persist)

### QR-DEMO-002 — search notes
Phase        : SVC-API
API          : API-DEMO-002
Entity       : ENT-DEMO-001
Operation    : FIND_BY_CRITERIA
Intent       : list the current user's active notes, optionally filtered by title, newest-updated first.
Logical spec : SELECT * FROM demo_note WHERE created_by = :currentUser AND is_active_fl = TRUE [AND title LIKE :titleFilter] ORDER BY updated_at DESC [page/size]
Join         : NONE
Transaction  : READ_ONLY
Pagination   : YES (Page<T>)
Filters      : title: LIKE
Result shape : full entity (paged)
Null handling: titleFilter absent → no title predicate; empty result → success with empty content (never "not found")

### QR-DEMO-003 — read note
Phase        : SVC-API
API          : API-DEMO-003
Entity       : ENT-DEMO-001
Operation    : FIND_ONE
Intent       : return one active note's full title and content.
Logical spec : SELECT * FROM demo_note WHERE note_pk = :id AND created_by = :currentUser AND is_active_fl = TRUE
Join         : NONE
Transaction  : READ_ONLY
Pagination   : NO
Filters      : id: EXACT
Result shape : full entity
Null handling: not found or inactive → DEMO_NOTE_NOT_FOUND (ADR-DEMO-002)

### QR-DEMO-004 — update note
Phase        : SVC-API
API          : API-DEMO-004
Entity       : ENT-DEMO-001
Operation    : UPDATE
Intent       : save changed title/content on an existing active note; bump updated_by/updated_at.
Logical spec : UPDATE demo_note SET title = :title, content = :content, updated_by = :currentUser, updated_at = now() WHERE note_pk = :id AND created_by = :currentUser AND is_active_fl = TRUE
Join         : NONE
Transaction  : READ_WRITE
Pagination   : NO
Filters      : id: EXACT
Result shape : full entity
Null handling: not found or inactive → DEMO_NOTE_NOT_FOUND (ADR-DEMO-002); PK/created_by/created_at excluded from the request

### QR-DEMO-005 — deactivate note
Phase        : SVC-API
API          : API-DEMO-005
Entity       : ENT-DEMO-001
Operation    : UPDATE (flag flip)
Intent       : soft-delete an active note by flipping its active flag.
Logical spec : UPDATE demo_note SET is_active_fl = FALSE, updated_by = :currentUser, updated_at = now() WHERE note_pk = :id AND created_by = :currentUser AND is_active_fl = TRUE
Join         : NONE
Transaction  : READ_WRITE
Pagination   : NO
Filters      : id: EXACT
Result shape : confirmation
Null handling: not found or already inactive → DEMO_NOTE_NOT_FOUND (ADR-DEMO-002)

<!-- PHASE:CORE:START traces=REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: CORE — architecture policies

**Layers.** controller → service → mapper → domain (entity) → repository.
- Controller: HTTP binding, DTO validation annotations, permission gateway check only — no business logic.
- Service: orchestrates load → validate (RULE-*) → integrate (none — no XM) → persist (QR-*); the only layer allowed to throw `LocalizedException`.
- Mapper: entity ↔ DTO conversion only; never applies a RULE.
- Domain (entity): `Note` carries no behaviour beyond getters/setters for this module (simple kind) — domain-behaviour placement: entity methods only where a RULE is a pure invariant (title non-empty, content length); everything else lives in the service.
- Repository: QR-* implementations only; no business logic.

**Error signalling.** `LocalizedException → {code, messageAr, messageEn}`; runtime code format: the exact string in the Error Catalog (§7), serialized as the `code` field of the framework's standard error envelope.

**Transaction defaults.** READ_ONLY for FIND_*; READ_WRITE for SAVE/UPDATE (per QRC, §5 above).

**Search contract.** Request shape: `{titleFilter?: string, page: number, size: number}`; allowed sort field: `updatedAt` (default, DESC); paging via `Page<T>`.

**Audit fields.** `createdBy, createdAt, updatedBy, updatedAt` are framework-filled on every write; never accepted in create/update request DTOs, never set by mappers or services.

**Type mapping (postgresql16 → framework types).**
| postgresql16 | Framework type |
|---|---|
| GENERATED ALWAYS AS IDENTITY | Long |
| VARCHAR(n) | String |
| TEXT | String |
| BOOLEAN | boolean |
| TIMESTAMPTZ | Instant |

**Lookup values.** Not applicable — DEMO owns no lookup.

**Numbering.** Not applicable — Note has no business/document number (§3.3 test, all "no").

**Workflow engine.** Forbidden (profile) — not used; DEMO has no status lifecycle beyond the `activeFl` flag.

**Languages.** Every user-facing message carries `ar` and `en` (Error Catalog, §7); `Note.title`/`Note.content` are free-text user content, not per-language reference data (domain-profile §5) — no `titleAr`/`titleEn` split.

**Cross-module contract placement.** Not applicable — DEMO exposes and consumes no cross-module interface in v1.
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=ENT-DEMO-001,REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: DATA-DOM — data + domain

No SUB split (single entity, well under any split threshold).

### ENT-DEMO-001 — Note      kind: simple (DEMO-only exception, see domain-profile §5)
BINDINGS   table demo_note · PK note_pk (DBF-DEMO-001) · PK generation `GENERATED ALWAYS AS IDENTITY` · db-script v1
BUSINESS CODE none — not applicable (§3.3 test, all "no"; db-script has no business-code column)
DEFAULT FIELDS  simple-kind exception fields only (domain-profile §5, module-registry-demo.md AUTO-DECISIONS): audit fields + `is_active_fl`; no `nameAr`/`nameEn`, no `docNo`/`statusCode`/fiscal fields — this entity is neither `master` nor `transactional`.
FIELDS
| DBF | property | column | type (postgresql16) | null | read-only | constraint | label ar/en |
|---|---|---|---|---|---|---|---|
| DBF-DEMO-001 | id | note_pk | GENERATED ALWAYS AS IDENTITY | NOT NULL | yes | PK_DEMO_NOTE | معرّف الملاحظة / Note ID |
| DBF-DEMO-002 | title | title | VARCHAR(200) | NOT NULL | no | CHK_DEMO_NOTE_TITLE | عنوان الملاحظة / Title |
| DBF-DEMO-003 | content | content | TEXT | NOT NULL | no | CHK_DEMO_NOTE_CONTENT_LEN | محتوى الملاحظة / Content |
| DBF-DEMO-004 | activeFl | is_active_fl | BOOLEAN | NOT NULL | no (system-flipped only) | — | نشِط / Active |
| DBF-DEMO-005 | createdBy | created_by | VARCHAR(100) | NOT NULL | yes | — | أنشئ بواسطة / Created by |
| DBF-DEMO-006 | createdAt | created_at | TIMESTAMPTZ | NOT NULL | yes | — | تاريخ الإنشاء / Created at |
| DBF-DEMO-007 | updatedBy | updated_by | VARCHAR(100) | NOT NULL | yes | — | عُدّل بواسطة / Updated by |
| DBF-DEMO-008 | updatedAt | updated_at | TIMESTAMPTZ | NOT NULL | yes | — | تاريخ التعديل / Updated at |

DTO MEMBERSHIP  create-request: title, content (excludes id, activeFl, audit fields) · update-request: title, content (excludes id, activeFl, audit fields) · response: id, title, content, activeFl, createdAt, updatedAt (audit "By" fields excluded from response DTO — internal only)
LOOKUP FIELDS  none
DOMAIN RULES
  RULE-DEMO-001 — trigger: on create/update — statement: "The system shall reject a save when the note's title is empty." — message ar: "عنوان الملاحظة مطلوب" · en: "Note title is required" — scope: CREATE|UPDATE — DB enforcement: CHK_DEMO_NOTE_TITLE — owner layer: domain entity (pure invariant) + DB constraint as backstop
  RULE-DEMO-002 — trigger: on create/update — statement: "The system shall reject a save when the note's content exceeds 4000 characters." — message ar: "محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف)" · en: "Note content exceeds the maximum allowed length (4000 characters)" — scope: CREATE|UPDATE — DB enforcement: CHK_DEMO_NOTE_CONTENT_LEN — owner layer: domain entity (pure invariant) + DB constraint as backstop
STATE MACHINE  not applicable — `activeFl` is a 2-state flag, not a status lifecycle (SRS A7).
CROSS-MODULE   none.
REPOSITORY OPS → QR-DEMO-001 (SAVE), QR-DEMO-002 (FIND_BY_CRITERIA), QR-DEMO-003 (FIND_ONE), QR-DEMO-004 (UPDATE), QR-DEMO-005 (UPDATE flag flip)
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005,DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003,DBF-DEMO-004,DBF-DEMO-008 -->
### PHASE: SVC-API — service + API

No SUB split (5 API atoms, under the 8-endpoint threshold).

<!-- API:API-DEMO-001:START traces=REQ-DEMO-001,DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003 -->
### API-DEMO-001 — create note
Endpoint     : /api/v1/demo/notes   verb: POST
Layers       : controller.createNote → service.createNote
Request      : body DTO `CreateNoteRequest {title: string, content: string}`; excluded system fields: id, activeFl, createdBy, createdAt, updatedBy, updatedAt
Response     : status 201; DTO `NoteResponse {id, title, content, activeFl, createdAt, updatedAt}`; paginated? no; envelope ApiResponse<NoteResponse>
Validations  : RULE-DEMO-001 (title required — ar: "عنوان الملاحظة مطلوب" / en: "Note title is required"); RULE-DEMO-002 (content ≤ 4000 chars — ar: "محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف)" / en: "Note content exceeds the maximum allowed length (4000 characters)")
Errors       : DEMO_NOTE_TITLE_REQUIRED (400, RULE-DEMO-001); DEMO_NOTE_CONTENT_TOO_LONG (400, RULE-DEMO-002)
Orchestration: load — (none, new record) → validate (RULE-DEMO-001, RULE-DEMO-002) → integrate — (none, no XM) → persist (QR-DEMO-001, demo_note, GENERATED ALWAYS AS IDENTITY)
Repository   : QR-DEMO-001 · SAVE · join NONE · transaction READ_WRITE
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_CREATE — enforced before processing
Localization : messages ar+en above; no name field beyond user-entered title (free text, not per-language)
<!-- API:API-DEMO-001:END -->

<!-- API:API-DEMO-002:START traces=REQ-DEMO-002,DBF-DEMO-002,DBF-DEMO-008 -->
### API-DEMO-002 — search notes
Endpoint     : /api/v1/demo/notes   verb: GET
Layers       : controller.searchNotes → service.searchNotes
Request      : query params `titleFilter?: string, page: number = 0, size: number = 20 (max 200)`
Response     : status 200; DTO `Page<NoteResponse>`; paginated? yes (Page<T>); envelope ApiResponse<Page<NoteResponse>>
Validations  : none (search has no RULE)
Errors       : none beyond platform-standard (malformed paging params — framework-level, not module-specific)
Orchestration: load (QR-DEMO-002, filtered by current user + activeFl=TRUE) → validate — (none) → integrate — (none) → persist — (none, read-only)
Repository   : QR-DEMO-002 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_VIEW — enforced before processing
Localization : empty-state message ar: "لا توجد ملاحظات بعد" · en: "No notes yet" (AC-DEMO-005) — rendered by the caller on empty content, not a server error
<!-- API:API-DEMO-002:END -->

<!-- API:API-DEMO-003:START traces=REQ-DEMO-003,DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003 -->
### API-DEMO-003 — read note
Endpoint     : /api/v1/demo/notes/{id}   verb: GET
Layers       : controller.getNote → service.getNote
Request      : path param `id: Long`
Response     : status 200; DTO `NoteResponse`; paginated? no; envelope ApiResponse<NoteResponse>
Validations  : none beyond existence (RULE = PLATFORM-STD, ADR-DEMO-002)
Errors       : DEMO_NOTE_NOT_FOUND (404, PLATFORM-STD, ADR-DEMO-002)
Orchestration: load (QR-DEMO-003) → validate (existence, ADR-DEMO-002) → integrate — (none) → persist — (none, read-only)
Repository   : QR-DEMO-003 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_VIEW — enforced before processing
Localization : not-found message ar/en in the catalog row (§7)
<!-- API:API-DEMO-003:END -->

<!-- API:API-DEMO-004:START traces=REQ-DEMO-004,DBF-DEMO-002,DBF-DEMO-003,DBF-DEMO-008 -->
### API-DEMO-004 — update note
Endpoint     : /api/v1/demo/notes/{id}   verb: PUT
Layers       : controller.updateNote → service.updateNote
Request      : path param `id: Long`; body DTO `UpdateNoteRequest {title: string, content: string}`; excluded system fields: id, activeFl, createdBy, createdAt, updatedBy, updatedAt
Response     : status 200; DTO `NoteResponse`; paginated? no; envelope ApiResponse<NoteResponse>
Validations  : RULE-DEMO-001; RULE-DEMO-002; existence (RULE = PLATFORM-STD, ADR-DEMO-002)
Errors       : DEMO_NOTE_TITLE_REQUIRED (400, RULE-DEMO-001); DEMO_NOTE_CONTENT_TOO_LONG (400, RULE-DEMO-002); DEMO_NOTE_NOT_FOUND (404, PLATFORM-STD, ADR-DEMO-002)
Orchestration: load (QR-DEMO-003, verify ownership + active) → validate (RULE-DEMO-001, RULE-DEMO-002) → integrate — (none) → persist (QR-DEMO-004)
Repository   : QR-DEMO-004 · UPDATE · join NONE · transaction READ_WRITE
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_UPDATE — enforced before processing
Localization : messages ar+en above
<!-- API:API-DEMO-004:END -->

<!-- API:API-DEMO-005:START traces=REQ-DEMO-005,DBF-DEMO-004 -->
### API-DEMO-005 — deactivate note
Endpoint     : /api/v1/demo/notes/{id}   verb: DELETE
Layers       : controller.deactivateNote → service.deactivateNote
Request      : path param `id: Long`
Response     : status 200; confirmation body `{deactivated: true}`; paginated? no; envelope ApiResponse<Confirmation>
Validations  : existence (RULE = PLATFORM-STD, ADR-DEMO-002)
Errors       : DEMO_NOTE_NOT_FOUND (404, PLATFORM-STD, ADR-DEMO-002)
Orchestration: load (QR-DEMO-003, verify ownership + active) → validate (existence) → integrate — (none) → persist (QR-DEMO-005, flip is_active_fl)
Repository   : QR-DEMO-005 · UPDATE (flag flip) · join NONE · transaction READ_WRITE
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_DELETE — enforced before processing
Localization : confirmation message ar: "تم حذف الملاحظة" · en: "Note deleted" (AC-DEMO-010)
<!-- API:API-DEMO-005:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: DOC — contract documentation (internal, backend self-check only)

**API contract summary**
| API | Path | Verb | Request DTO | Response DTO | Stability |
|---|---|---|---|---|---|
| API-DEMO-001 | /api/v1/demo/notes | POST | CreateNoteRequest | NoteResponse | DRAFT — this summary is superseded by the published `api-docs-demo.md` after implementation |
| API-DEMO-002 | /api/v1/demo/notes | GET | (query params) | Page\<NoteResponse\> | DRAFT |
| API-DEMO-003 | /api/v1/demo/notes/{id} | GET | (path param) | NoteResponse | DRAFT |
| API-DEMO-004 | /api/v1/demo/notes/{id} | PUT | UpdateNoteRequest | NoteResponse | DRAFT |
| API-DEMO-005 | /api/v1/demo/notes/{id} | DELETE | (path param) | Confirmation | DRAFT |

**DTO typing constraints.** No lookup-backed fields in this module (none to constrain). Note has no business code, so none is ever present in create/update bodies (there is none to exclude/include).

**Pagination + filter standard.** Request shape `{titleFilter?, page, size}`; allowed sort field `updatedAt` (DESC default); an empty result is success with empty content, never "not found" (applies to API-DEMO-002 only).

This section is a backend self-check only; the frontend stage binds to the real `api-docs-demo.md` published after implementation (factory.passes.2.required_inputs), never to this summary.
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=ENT-DEMO-001 -->
### PHASE: INT-C — cross-module consume (contracts)

None — the db-script XM REGISTER is empty; DEMO consumes no other module's data in v1 (domain-profile §6, §8 decision 3; project-registry Cross-module dependency index: "None yet"). No inbound stub is declared either — no other module has requested to consume `Note` (it is PRIVATE, project-registry SHARED ENTITY DECLARATIONS: none).
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=ENT-DEMO-001 -->
### PHASE: INT-R — cross-module resolve (runtime activation)

None — no XM rows exist for DEMO to resolve or activate (see PHASE:INT-C).
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=SCR-REQ-DEMO-001,REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: SEC-BE — security (backend half)

**Per-screen enforcement.** SCR-REQ-DEMO-001 (Daily Notes): every serving API (API-DEMO-001..005) verifies its permission before processing (VIEW is the gateway — without it no other action applies, per `profile.conventions.security_model`).

**SEC_PAGES seed data**
| Page code | Name (ar/en) | Parent |
|---|---|---|
| PAGE_DEMO_NOTES | الملاحظات اليومية / Daily Notes | — (top-level under DEMO menu) |

**Permission seed data**
| Permission | Action | API(s) |
|---|---|---|
| PERM_PAGE_DEMO_NOTES_VIEW | VIEW (gateway) | API-DEMO-002, API-DEMO-003 |
| PERM_PAGE_DEMO_NOTES_CREATE | CREATE | API-DEMO-001 |
| PERM_PAGE_DEMO_NOTES_UPDATE | UPDATE | API-DEMO-004 |
| PERM_PAGE_DEMO_NOTES_DELETE | DELETE | API-DEMO-005 |

Role USER holds all four (SRS B4 Access — single-role module, no sharing). No permission name appears here that is absent from the SRS permission matrix (SRS B4).

**Forbidden responses.** Map through `LocalizedException → {code: FORBIDDEN, messageAr, messageEn}` — a catalog row, same envelope as every other error (§7).
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=ENT-DEMO-001,REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: ALIGN-BE — alignment self-check

## Error Catalog — DEMO v1
| code | RULE-* (or PLATFORM-STD + ADR) | API-* | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| DEMO_NOTE_TITLE_REQUIRED | RULE-DEMO-001 | API-DEMO-001, API-DEMO-004 | 400 | empty title on save | عنوان الملاحظة مطلوب | Note title is required |
| DEMO_NOTE_CONTENT_TOO_LONG | RULE-DEMO-002 | API-DEMO-001, API-DEMO-004 | 400 | content > 4000 chars on save | محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف) | Note content exceeds the maximum allowed length (4000 characters) |
| DEMO_NOTE_NOT_FOUND | PLATFORM-STD (ADR-DEMO-002) | API-DEMO-003, API-DEMO-004, API-DEMO-005 | 404 | id does not resolve to an active note owned by the caller | الملاحظة غير موجودة | Note not found |

Runtime code format: the `code` field of the framework's standard `ApiResponse` error envelope carries the string exactly as in the `code` column above (stated once here for api-verify).

## Security
Covered by PHASE:SEC-BE above. Review check `ERP-4` (MAJOR — every mutation endpoint declares its PERM_* requirement): API-DEMO-001 → PERM_PAGE_DEMO_NOTES_CREATE ✓; API-DEMO-004 → PERM_PAGE_DEMO_NOTES_UPDATE ✓; API-DEMO-005 → PERM_PAGE_DEMO_NOTES_DELETE ✓.

## ALIGN — DEMO v1
```
TRACEABILITY      every API-*/QR-*/RULE-*/DBF-* used in a phase appears in the Plan Index ✓ · every block carries traces= ✓ · every traces target exists upstream ✓
BINDING (§2A)     no placeholder table/column/key/generation object ✓ · no "see SRS" ✓ · every column cites a DBF ✓ · every message present in ar + en ✓ · business code format explicit (none applicable — Note has no business code) ✓
MANIFEST (§4)     only the manifest's columns ✓ · every DBF of demo_note listed ✓ · no ⏸ rows (no XM) ✓
QRC (§5)          every API with a DB operation has a QR ✓ (5/5) · every QR carries the agent-reference warning (this plan §5 header) ✓ · no join for lookup labels (no lookups) ✓ · exact generation object named (GENERATED ALWAYS AS IDENTITY) ✓
API (R3)          every RULE in Validations has a catalog row ✓ · platform errors have RULE = PLATFORM-STD + ADR ✓ (ADR-DEMO-002) · create/update exclude system fields ✓ · business code in responses — not applicable (none) ✓
CROSS-MODULE      no XM from the db-script to place ✓ · no DEFERRED row ✓ · no inbound stub requested ✓
SECURITY (R7)     every API serving SCR-REQ-DEMO-001 declares its permission ✓ · SCR_PAGES seed row present ✓ · no permission outside the SRS matrix ✓
CORE (R1)         layers declared ✓ · domain placement declared ✓ · error signalling declared ✓ · type mapping declared ✓
DECISIONS         ADR-DEMO-001 (content length), ADR-DEMO-002 (not-found handling) — both ACCEPTED, non-breaking · no BLOCKED ADR
RESULT            PASSED ✓
```

**Coverage tables**
| ENT/DBF | Phases | QR | XM |
|---|---|---|---|
| ENT-DEMO-001 / DBF-DEMO-001..008 | DATA-DOM, SVC-API, SEC-BE, ALIGN-BE | QR-DEMO-001..005 | none |

| RULE | API | Catalog code |
|---|---|---|
| RULE-DEMO-001 | API-DEMO-001, API-DEMO-004 | DEMO_NOTE_TITLE_REQUIRED |
| RULE-DEMO-002 | API-DEMO-001, API-DEMO-004 | DEMO_NOTE_CONTENT_TOO_LONG |

| XM | Status | Blocks | Workaround |
|---|---|---|---|
| none | — | — | — |
<!-- PHASE:ALIGN-BE:END -->

## REGISTRY — P3.1 — DEMO v1
See `registry-exec-be-demo.md`.
══════════════════════════════════════════════════════════════════
