# BACKEND EXECUTION PLAN — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module : NOTE   Version : v1   Profile : erp   Dialect : postgresql16
Framework : spring-boot-java (profile.stack.backend.framework)
Inputs : srs (v1, PRD-approved) · db-script (v1) · registry-srs (v1) · registry-db (v1)
Governance : FULL — the db-script exists and binds every entity of the SRS; no entity is `PENDING DB`.
Open ADRs : 0 (2 new ADRs raised and ACCEPTED this stage — see DECISIONS APPLIED)
══════════════════════════════════════════════════════════════════

## PRE-GENERATION EXTRACTION — NOTE v1 (working set; not part of the plan proper)

```
── FROM srs ──────────────────────────────────────────────────────────────
ENTITIES      1 — ENT-NOTE-001 الملاحظة / Note, kind master, PRIVATE
REQUIREMENTS  18 — REQ-NOTE-001..018, 24 AC-NOTE-001..024
RULES         7 — RULE-NOTE-001..007, all scoped to ENT-NOTE-001, all with ar+en messages
SCREENS       1 — SCR-REQ-NOTE-001 شاشة الملاحظات / Notes, composite (search + entry = ONE screen)
PERMISSIONS   page code NOTE_NOTES · actions VIEW (gateway) · CREATE · UPDATE · DELETE
              · one role: مستخدم شاشة الملاحظات / Notes-screen user
LOOKUPS       none — SRS A6 states the module owns no lookup key and consumes none
BUSINESS CODE none — the note is not a numbered document (SRS A3, §3.3 NUMBERING)
── FROM db-script ────────────────────────────────────────────────────────
TABLES        1 — NOTE_NOTE (ENT-NOTE-001)
PK GENERATION strategy `sequence` — SEQ_NOTE_NOTE (db-script BLOCK 1), one per table;
              note_pk is a plain BIGINT NOT NULL with no identity clause and no default
COLUMNS       9 — DBF-NOTE-001..009
CONSTRAINTS   PK_NOTE_NOTE · CHK_NOTE_NOTE_NOTE_TITLE · CHK_NOTE_NOTE_NOTE_BODY ·
              CHK_NOTE_NOTE_OWNER_USER_REF · no UNIQUE · no FK
INDEXES       IDX_NOTE_NOTE_OWN_ACT · IDX_NOTE_NOTE_OWN_UPD · IDX_NOTE_NOTE_OWN_CRT
XM            none — 0 rows in the db-script XM register
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   ENT-SEC-001 (identity as a principal string, no FK, no XM row),
                           ENT-SEC-004 / ENT-SEC-005 / ENT-SEC-006 (deployment-time
                           registration as data — precedent ADR-FIN-001, no XM row)
EXISTING LOOKUP KEYS       none to reuse — none exists for this module
ID RANGES already used     API: none · QR: none — both sequences start at 001 here
──────────────────────────────────────────────────────────────────────────
No row needed §2A.3 extraction-failure handling: every value below is bound.
```

## EXECUTION PLAN INDEX — NOTE v1 — backend-execution-plan-note.md
Profile: erp · dialect: postgresql16 · framework: spring-boot-java
Open ADRs: 0 — erp/decisions/NOTE/

**ENTITY REGISTRY**
| ENT | Name (ar / en) | Table | Business code | Operations |
|---|---|---|---|---|
| ENT-NOTE-001 | الملاحظة / Note | NOTE_NOTE | none | VIEW · CREATE · UPDATE · DELETE |

**FIELD REGISTRY**
| DBF | Property | Read-only | ENT |
|---|---|---|---|
| DBF-NOTE-001 | notePk | Yes (platform-assigned from the sequence) | ENT-NOTE-001 |
| DBF-NOTE-002 | noteTitle | No | ENT-NOTE-001 |
| DBF-NOTE-003 | noteBody | No | ENT-NOTE-001 |
| DBF-NOTE-004 | ownerUserRef | Yes (set at creation from the authenticated principal) | ENT-NOTE-001 |
| DBF-NOTE-005 | isActiveFl | Yes (flipped by the deactivate endpoint only) | ENT-NOTE-001 |
| DBF-NOTE-006 | createdBy | Yes (audit) | ENT-NOTE-001 |
| DBF-NOTE-007 | createdAt | Yes (audit) | ENT-NOTE-001 |
| DBF-NOTE-008 | updatedBy | Yes (audit) | ENT-NOTE-001 |
| DBF-NOTE-009 | updatedAt | Yes (audit) | ENT-NOTE-001 |

**API REGISTRY**
| API | Operation | Verb | Path | Traces (REQ · DBF) |
|---|---|---|---|---|
| API-NOTE-001 | create note | POST | /api/v1/note/notes | REQ-NOTE-001, REQ-NOTE-002, REQ-NOTE-003, REQ-NOTE-004 · DBF-NOTE-002, DBF-NOTE-003, DBF-NOTE-004, DBF-NOTE-005 |
| API-NOTE-002 | search notes | GET | /api/v1/note/notes | REQ-NOTE-009, REQ-NOTE-010, REQ-NOTE-011, REQ-NOTE-012, REQ-NOTE-013 · DBF-NOTE-002, DBF-NOTE-003, DBF-NOTE-004, DBF-NOTE-005 |
| API-NOTE-003 | read note | GET | /api/v1/note/notes/{id} | REQ-NOTE-006, REQ-NOTE-014 · DBF-NOTE-001, DBF-NOTE-002, DBF-NOTE-003, DBF-NOTE-005 |
| API-NOTE-004 | update note | PUT | /api/v1/note/notes/{id} | REQ-NOTE-005, REQ-NOTE-006 · DBF-NOTE-002, DBF-NOTE-003, DBF-NOTE-008, DBF-NOTE-009 |
| API-NOTE-005 | deactivate note | DELETE | /api/v1/note/notes/{id} | REQ-NOTE-007, REQ-NOTE-008 · DBF-NOTE-005, DBF-NOTE-008, DBF-NOTE-009 |

**RULE REGISTRY**
| RULE | Name (en) | Scope | ENT | Message ar/en |
|---|---|---|---|---|
| RULE-NOTE-001 | A note title is required | on create / on update | ENT-NOTE-001 | ✓ |
| RULE-NOTE-002 | A note body is required | on create / on update | ENT-NOTE-001 | ✓ |
| RULE-NOTE-003 | Title and body length limits | on create / on update | ENT-NOTE-001 | ✓ |
| RULE-NOTE-004 | Ownership is immutable after creation | on update | ENT-NOTE-001 | ✓ |
| RULE-NOTE-005 | No operation on a note the requester does not own | on read / update / deactivate / search | ENT-NOTE-001 | ✓ |
| RULE-NOTE-006 | No editing of a deactivated note | on update | ENT-NOTE-001 | ✓ |
| RULE-NOTE-007 | No repeated deactivation | on deactivate | ENT-NOTE-001 | ✓ |

**SCREEN REGISTRY**
| Screen | Type | ENT | Permission names |
|---|---|---|---|
| NOTE_NOTES | composite (search + entry) | ENT-NOTE-001 | PERM_NOTE_NOTES_VIEW, PERM_NOTE_NOTES_CREATE, PERM_NOTE_NOTES_UPDATE, PERM_NOTE_NOTES_DELETE |

**LOOKUP REGISTRY** — the module owns no lookup key and consumes none (SRS A6); the table
is written empty rather than omitted, so the absence is a stated fact and not a gap.

| Lookup key | Used in field (`DBF-*`) | `ENT-*` | Table owner module |
|---|---|---|---|
| — | — | — | — |

**QRC SUMMARY**
| QR | Operation | Phase | ENT |
|---|---|---|---|
| QR-NOTE-001 | NATIVE (sequence allocation) | SVC-API | ENT-NOTE-001 |
| QR-NOTE-002 | SAVE | SVC-API | ENT-NOTE-001 |
| QR-NOTE-003 | FIND_BY_CRITERIA | SVC-API | ENT-NOTE-001 |
| QR-NOTE-004 | FIND_ONE | SVC-API | ENT-NOTE-001 |
| QR-NOTE-005 | UPDATE | SVC-API | ENT-NOTE-001 |
| QR-NOTE-006 | UPDATE (deactivate) | SVC-API | ENT-NOTE-001 |

**DB ALIGNMENT** — see the manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 0 deferred; the cross-module phases (INT-C, INT-R) are present and empty by construction
**SECURITY** — 1 screen × 1 role
**DBF ROWS** — 9
**XM ROWS** — 0
**API ROWS** — 5
**QR ROWS** — 6

## DB Alignment Manifest — NOTE v1

Column names, DB types and SRS references are sourced by lookup from the db-script and are
not reproduced here.

| DBF | ENT | plan property | plan type | XM | status |
|---|---|---|---|---|---|
| DBF-NOTE-001 | ENT-NOTE-001 | notePk | Long | — | ✓ · system-generated (platform-assigned, `{entity}Pk`) |
| DBF-NOTE-002 | ENT-NOTE-001 | noteTitle | String | — | ✓ |
| DBF-NOTE-003 | ENT-NOTE-001 | noteBody | String | — | ✓ |
| DBF-NOTE-004 | ENT-NOTE-001 | ownerUserRef | String | — | ✓ |
| DBF-NOTE-005 | ENT-NOTE-001 | isActiveFl | Boolean | — | ✓ |
| DBF-NOTE-006 | ENT-NOTE-001 | createdBy | String | — | ✓ · system-generated (audit) |
| DBF-NOTE-007 | ENT-NOTE-001 | createdAt | Instant | — | ✓ · system-generated (audit) |
| DBF-NOTE-008 | ENT-NOTE-001 | updatedBy | String | — | ✓ · system-generated (audit) |
| DBF-NOTE-009 | ENT-NOTE-001 | updatedAt | Instant | — | ✓ · system-generated (audit) |

Legend ✓ aligned · ✗ type mismatch (finding) · ⏸ deferred XM.
No derived / computed property exists in this module: every plan property is a column of
NOTE_NOTE, so no row carries `— (derived)`.

## Query Reference Catalog (QR-NOTE-*)

> Logical specification only, never executable code: the implementer rewrites every entry
> with the real entity class, mapped property names and the project's query strategy.

#### QR-NOTE-001 — allocate the note primary key
Phase        : SVC-API
API          : API-NOTE-001
Entity       : ENT-NOTE-001
Operation    : NATIVE
Intent       : draw the next primary-key value for a new note from the object the db-script declares
Logical spec : SELECT nextval FROM SEQUENCE SEQ_NOTE_NOTE
Join         : NONE
Transaction  : READ_WRITE (participates in the caller's create transaction)
Locking      : NONE — the sequence allocates atomically, so two simultaneous creates cannot
               receive the same key. This is the reason the key is never computed as MAX+1.
Pagination   : NO
Filters      : —
Result shape : count (one BIGINT value)
Null handling: never null

#### QR-NOTE-002 — persist a new note
Phase        : SVC-API
API          : API-NOTE-001
Entity       : ENT-NOTE-001
Operation    : SAVE
Intent       : store a new note with its owner, its content and its active flag
Logical spec : INSERT INTO NOTE_NOTE (note_pk, note_title, note_body, owner_user_ref, is_active_fl, created_by, created_at) VALUES (…)
Join         : NONE
Transaction  : READ_WRITE
Locking      : NONE — the row does not exist yet and no unique business value is allocated
               here (the note carries no business code); the only allocated value is the key,
               and QR-NOTE-001 allocates it atomically
Pagination   : NO
Filters      : —
Result shape : full entity
Null handling: updated_by / updated_at stay null until the first update

#### QR-NOTE-003 — search the requester's notes
Phase        : SVC-API
API          : API-NOTE-002
Entity       : ENT-NOTE-001
Operation    : FIND_BY_CRITERIA
Intent       : the page of notes the requester owns, in the requested state, optionally
               narrowed by a text filter — RULE-NOTE-005 bounds every row it can return
Logical spec : SELECT … FROM NOTE_NOTE WHERE owner_user_ref = :principal AND is_active_fl = :state
               [AND (note_title CONTAINS :text OR note_body CONTAINS :text)]
               ORDER BY updated_at DESC NULLS LAST, created_at DESC — page/size
Join         : NONE
Transaction  : READ_ONLY
Locking      : NONE — nothing is decided on and written back
Pagination   : YES (Page<T>) — default size 20, maximum 200 (REQ-NOTE-012)
Filters      : text: LIKE (contains, title or body) · state: EXACT (boolean, default true) ·
               owner: EXACT (never a caller-supplied filter — always the principal)
Result shape : projection (notePk, noteTitle, body excerpt, isActiveFl, updatedAt, createdAt)
Null handling: updatedAt null on a never-updated note — ordering falls back to createdAt
Notes        : an empty result is success with empty content, never "not found"

#### QR-NOTE-004 — read one note the requester owns
Phase        : SVC-API
API          : API-NOTE-003, API-NOTE-004, API-NOTE-005 — the load step of the update and
               deactivate endpoints reaches this same query; API-NOTE-003 is the head of the chain
Entity       : ENT-NOTE-001
Operation    : FIND_ONE
Intent       : resolve a note by key **and** owner in one predicate, so a note owned by
               someone else is indistinguishable from one that does not exist (ADR-NOTE-003)
Logical spec : SELECT … FROM NOTE_NOTE WHERE note_pk = :id AND owner_user_ref = :principal
Join         : NONE
Transaction  : READ_ONLY (as the entry of API-NOTE-003) · READ_WRITE when it opens the
               update or deactivate transaction
Locking      : NONE on the read path. On the write paths the read is NOT the guard: neither
               API-NOTE-004 nor API-NOTE-005 decides on `is_active_fl` from this result and
               then writes — each carries the state predicate into its own conditional
               UPDATE (QR-NOTE-005 / QR-NOTE-006), which is what makes a second concurrent
               caller lose rather than pass the same check
Pagination   : NO
Filters      : notePk: EXACT · ownerUserRef: EXACT
Result shape : full entity
Null handling: empty result → the catalog row for "not found" (NOTE-404-NOTE-NOT-FOUND)

#### QR-NOTE-005 — update an owned, active note
Phase        : SVC-API
API          : API-NOTE-004
Entity       : ENT-NOTE-001
Operation    : UPDATE
Intent       : replace the stored title and body of a note the requester owns while it is active
Logical spec : UPDATE NOTE_NOTE SET note_title = :title, note_body = :body, updated_by = :principal,
               updated_at = :now WHERE note_pk = :id AND owner_user_ref = :principal AND is_active_fl = TRUE
Join         : NONE
Transaction  : READ_WRITE
Locking      : the conditional predicate IS the guard. Two simultaneous requests — an update
               and a deactivation of the same note — must not both succeed; the update names
               `is_active_fl = TRUE` in its own WHERE clause, so exactly one of the two
               statements affects a row and the loser sees 0 rows affected and raises
               RULE-NOTE-006. A validate-then-write with the flag read beforehand would let
               both pass validation
Pagination   : NO
Filters      : notePk: EXACT · ownerUserRef: EXACT · isActiveFl: EXACT
Result shape : count (rows affected) → 0 distinguishes "not owned / absent" (RULE-NOTE-005,
               already separated by QR-NOTE-004) from "inactive" (RULE-NOTE-006)
Null handling: —

#### QR-NOTE-006 — deactivate an owned note
Phase        : SVC-API
API          : API-NOTE-005
Entity       : ENT-NOTE-001
Operation    : UPDATE
Intent       : flip a note the requester owns out of service without removing its row
Logical spec : UPDATE NOTE_NOTE SET is_active_fl = FALSE, updated_by = :principal, updated_at = :now
               WHERE note_pk = :id AND owner_user_ref = :principal AND is_active_fl = TRUE
Join         : NONE
Transaction  : READ_WRITE
Locking      : the conditional predicate IS the guard. Two simultaneous deactivations of the
               same note must not both report success: only one statement affects a row, and
               the other sees 0 rows affected and raises RULE-NOTE-007. Nothing is deleted —
               REQ-NOTE-008 forbids any statement that removes the row
Pagination   : NO
Filters      : notePk: EXACT · ownerUserRef: EXACT · isActiveFl: EXACT
Result shape : count (rows affected)
Null handling: —

**Standard operation defaults** apply as the engine states them (FIND_ONE by PK → read-only,
not found → the catalog row; FIND_BY_CRITERIA → read-only, empty result is success; SAVE →
PK and audit fields system-set; UPDATE → PK, owner and audit excluded from the request;
deactivate → `soft` per profile.stack.db.delete_semantics, the active flag flipped; EXISTS →
uniqueness check) except where an entry above overrides them.

**No usage check precedes deactivation**: the can-delete question is whether another record
depends on the row, and ENT-NOTE-001 is PRIVATE with no inbound reference anywhere in the
platform (registry-db → Cascade). The only precondition is RULE-NOTE-007, enforced in the
statement itself.

**Join governance**: every query above is single-table. The module has one entity, no lookup
field whose label would have to be resolved, and no cross-entity filter — so no join exists
and no ADR for one is required. No native query beyond the sequence allocation (QR-NOTE-001),
which is native because a sequence is not addressable as an entity.

## ERROR CATALOG — NOTE v1

Envelope `LocalizedException → {code, messageAr, messageEn}`; the runtime code format is
declared once in PHASE 1 — CORE and every row below is an instance of it. Downstream
consumers cite the **code** and never reproduce the message text.

| code | RULE | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| NOTE-400-TITLE-REQUIRED | RULE-NOTE-001 | API-NOTE-001, API-NOTE-004 | 400 | the submitted title is missing or blank (a title of spaces only counts as blank) | عنوان الملاحظة مطلوب. | A note title is required. |
| NOTE-400-BODY-REQUIRED | RULE-NOTE-002 | API-NOTE-001, API-NOTE-004 | 400 | the submitted body is missing or blank | نصّ الملاحظة مطلوب. | A note body is required. |
| NOTE-400-LENGTH-EXCEEDED | RULE-NOTE-003 | API-NOTE-001, API-NOTE-004 | 400 | the title exceeds 200 characters or the body exceeds 4000 characters | العنوان لا يتجاوز 200 حرف والنصّ لا يتجاوز 4000 حرف. | A title may not exceed 200 characters and a body may not exceed 4000 characters. |
| NOTE-404-NOTE-NOT-FOUND | RULE-NOTE-005 | API-NOTE-003, API-NOTE-004, API-NOTE-005 | 404 | the id resolves to no note owned by the authenticated requester — the same answer for an absent note and for one owned by somebody else (ADR-NOTE-003) | الملاحظة غير موجودة. | The note was not found. |
| NOTE-409-NOTE-INACTIVE | RULE-NOTE-006 | API-NOTE-004 | 409 | the update statement affected no row because the note is inactive | لا يمكن تعديل ملاحظة معطَّلة. | A deactivated note cannot be edited. |
| NOTE-409-ALREADY-DEACTIVATED | RULE-NOTE-007 | API-NOTE-005 | 409 | the deactivation statement affected no row because the note is already inactive | الملاحظة معطَّلة أصلًا. | The note is already deactivated. |
| NOTE-401 | PLATFORM-STD — ADR-NOTE-005 | API-NOTE-001, API-NOTE-002, API-NOTE-003, API-NOTE-004, API-NOTE-005 | 401 | no authenticated principal on the request; the module never derives an owner without one | الرجاء تسجيل الدخول. | Please sign in. |
| NOTE-403-SCREEN-FORBIDDEN | PLATFORM-STD — ADR-NOTE-005 | API-NOTE-001, API-NOTE-002, API-NOTE-003, API-NOTE-004, API-NOTE-005 | 403 | the requester's roles do not hold the module grant or PERM_NOTE_NOTES_VIEW, the gateway action (REQ-NOTE-016) | لا تملك صلاحية الوصول إلى هذه الشاشة. | You are not authorised to access this screen. |
| NOTE-403-ACTION-FORBIDDEN | PLATFORM-STD — ADR-NOTE-005 | API-NOTE-001, API-NOTE-004, API-NOTE-005 | 403 | the requester holds the gateway action but not the action this endpoint carries (REQ-NOTE-018) | لا تملك صلاحية تنفيذ هذا الإجراء. | You are not authorised to perform this action. |
| NOTE-400-INVALID-SORT | PLATFORM-STD — ADR-NOTE-005 | API-NOTE-002 | 400 | the request asks to sort on a field the screen does not offer (the allowed set is declared in PHASE 1 — CORE) | حقل الترتيب غير مسموح به. | The requested sort field is not allowed. |
| NOTE-500 | PLATFORM-STD — ADR-NOTE-005 | API-NOTE-001, API-NOTE-002, API-NOTE-003, API-NOTE-004, API-NOTE-005 | 500 | an unexpected server-side failure; the database error itself never reaches the user (REQ-NOTE-004 rationale) | حدث خطأ غير متوقع. | An unexpected error occurred. |

**RULE-NOTE-004 carries no catalog row, deliberately** (ADR-NOTE-006). Ownership is immutable
because `ownerUserRef` is absent from both request DTOs and is never mapped from a request:
a client-supplied owner is ignored, not rejected (AC-NOTE-003). A row here would be raisable
by no code path — the defect class this catalog exists to keep out.

---

<!-- PHASE:CORE:START traces=REQ-NOTE-004,REQ-NOTE-012,REQ-NOTE-018 -->
## PHASE 1 — CORE

**Layers** — controller → service → mapper → domain → repository
(`profile.stack.backend.layers`). Domain-behaviour placement: `domain_classes` — the
single-entity invariants of ENT-NOTE-001 (activation state, content replacement) are
methods on the domain class; the service layer owns the owner predicate, the transaction
boundary and the mapping between request and domain.

**Type mapping — postgresql16 → Java** (from `profile.stack.db.syntax_map`; column types
only — the PK-generation clause is not a type):

| postgresql16 | Java |
|---|---|
| BIGINT (pk) | Long |
| VARCHAR(n) | String |
| BOOLEAN | Boolean |
| TIMESTAMPTZ | Instant |

A deviation from this table needs an ADR; none is taken in this module.

**Primary keys** — strategy `sequence`. The application draws every `NOTE_NOTE` key from
`SEQ_NOTE_NOTE` (QR-NOTE-001) before the insert. No identity clause and no sequence default
exists in the script, so a JPA identity or table generator would contradict the delivered
schema.

**Runtime error-code format** — `NOTE-{http}[-{SLUG}]`
(`profile.stack.backend.api.error_code_format`; `{http}` is the row's HTTP status, `{SLUG}`
is SCREAMING-KEBAB and the bracketed half is optional). Every ERROR CATALOG row above is an
instance of this one string, and every status it carries is one
`profile.stack.backend.api.http_statuses` declares.

**Error signalling** — `LocalizedException → {code, messageAr, messageEn}`; responses are
wrapped in `ApiResponse<T>`, pages in `Page<T>`.

**Transaction scope** — `READ_ONLY` for every FIND_* query; `READ_WRITE` for every SAVE and
UPDATE. No endpoint of this module needs `REQUIRES_NEW`.

**Search contract** — the sort fields this module offers are exactly the ones
SCR-REQ-NOTE-001 §B2 names as list columns: `updatedAt` and `createdAt`, default
`updatedAt DESC` falling back to `createdAt DESC`. The set is not widened here; a request
for any other sort field is refused with NOTE-400-INVALID-SORT. Paging is server-side,
`Page<T>`, default size 20 and maximum 200 (REQ-NOTE-012); an empty result is success.

**Lookup values** — all LOV values are runtime-loaded from the lookup module and no enum is
hardcoded in an API or a field spec. The rule is satisfied vacuously here: SRS A6 declares
no lookup key owned or consumed. `isActiveFl` is a platform boolean, and the state filter of
the search is that boolean's two faces — not a coded value list.

**Numbering** — document numbers come from the platform numbering engine and are never
generated in a module. Not applicable here: the note is not a numbered document and
ENT-NOTE-001 carries no business code.

**Workflow engine** — forbidden (`profile.conventions.workflow_engine`); the two-state flag
of ENT-NOTE-001 is not a workflow and no engine is introduced for it.

**Audit fields** — `createdBy`, `createdAt`, `updatedBy`, `updatedAt` are filled by the
platform and never appear in a request DTO (AC-NOTE-002).

**Identity** — the authenticated principal identifier is delivered by the standard platform
interceptor as a string (ENT-SEC-001 consumed as a value, no foreign key). Every endpoint
reads it from the security context; no endpoint accepts it as input.

**Authorization** — evaluated by the platform authorisation layer on the page code and the
action the operation carries (REQ-NOTE-018); no role name is written into any service of
this module. `VIEW` is the gateway: without it no other permission applies.

**Languages** — every message in this plan is present in ar and en, and every field of
ENT-NOTE-001 carries an ar and an en label (PHASE 2). The note's own content is monolingual
by POL-NOTE-005 and ADR-NOTE-001 — that is the user's text, not a platform name.
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=REQ-NOTE-001,REQ-NOTE-002,REQ-NOTE-003,REQ-NOTE-005,REQ-NOTE-007,REQ-NOTE-008 -->
## PHASE 2 — DATA-DOM

Entity count is 1 — far below the split self-check, so no SUB is opened and the single
entity block is written flat.

#### ENT-NOTE-001 — الملاحظة / Note      kind: master
BINDINGS   table `NOTE_NOTE` · PK `note_pk` (DBF-NOTE-001) · PK generation `sequence` →
sequence `SEQ_NOTE_NOTE` (db-script BLOCK 1) · db-script version v1
BUSINESS CODE  none — the note is not a numbered document (SRS A3, §3.3 NUMBERING); no
property, no column, no uniqueness constraint and no generation source exists for one, and
none is invented here.
DEFAULT FIELDS (profile.conventions.entity_defaults.master: nameAr, nameEn, code,
isActiveFl, createdBy, createdAt, updatedBy, updatedAt) — narrowed by ADR-NOTE-001: this
entity carries `isActiveFl` and the four audit fields, and carries no `nameAr`, `nameEn` or
`code`. The db-script creates no such columns, so the plan may not name them.
FIELDS
| DBF | property | column | type (postgresql16) | null | read-only | constraint | label ar / en |
|---|---|---|---|---|---|---|---|
| DBF-NOTE-001 | notePk | note_pk | BIGINT | NOT NULL | Yes | PK_NOTE_NOTE | المعرّف / Identifier |
| DBF-NOTE-002 | noteTitle | note_title | VARCHAR(200) | NOT NULL | No | CHK_NOTE_NOTE_NOTE_TITLE | العنوان / Title |
| DBF-NOTE-003 | noteBody | note_body | VARCHAR(4000) | NOT NULL | No | CHK_NOTE_NOTE_NOTE_BODY | النص / Body |
| DBF-NOTE-004 | ownerUserRef | owner_user_ref | VARCHAR(100) | NOT NULL | Yes | CHK_NOTE_NOTE_OWNER_USER_REF | المالك / Owner |
| DBF-NOTE-005 | isActiveFl | is_active_fl | BOOLEAN | NOT NULL | Yes | — (DEFAULT TRUE) | فعّالة / Active |
| DBF-NOTE-006 | createdBy | created_by | VARCHAR(100) | NOT NULL | Yes | — | أنشأها / Created by |
| DBF-NOTE-007 | createdAt | created_at | TIMESTAMPTZ | NOT NULL | Yes | — (DEFAULT now()) | تاريخ الإنشاء / Created at |
| DBF-NOTE-008 | updatedBy | updated_by | VARCHAR(100) | NULL | Yes | — | عدّلها / Updated by |
| DBF-NOTE-009 | updatedAt | updated_at | TIMESTAMPTZ | NULL | Yes | — | تاريخ التعديل / Updated at |

DTO MEMBERSHIP
- create-request `{noteTitle, noteBody}` — excludes the PK, the owner, the active flag and
  the four audit fields; a supplied owner is ignored, never mapped (AC-NOTE-003).
- update-request `{noteTitle, noteBody}` — excludes the PK (it is a path parameter), the
  owner (RULE-NOTE-004), the active flag (only the deactivate endpoint changes it) and the
  audit fields.
- response includes `{notePk, noteTitle, noteBody, isActiveFl, createdBy, createdAt,
  updatedBy, updatedAt}`; there is no business code to include. The owner is not returned —
  every response a requester can obtain is already their own row, so echoing the principal
  adds nothing the caller does not have.

LOOKUP FIELDS  none — no property of this entity stores a lookup code (SRS A6).

DOMAIN RULES
- **RULE-NOTE-001** — عنوان الملاحظة إلزامي / A note title is required · scope CREATE|UPDATE ·
  trigger: on create / on update · statement: "The system shall prevent saving a note when
  its title is missing or blank." · message ar: «عنوان الملاحظة مطلوب.» · en: "A note title
  is required." · DB enforcement: `CHK_NOTE_NOTE_NOTE_TITLE` + NOT NULL is the structural
  floor; the user-facing check is application-level (a title of spaces only is blank) ·
  owner layer: domain class, invoked by the service before persistence.
- **RULE-NOTE-002** — نصّ الملاحظة إلزامي / A note body is required · scope CREATE|UPDATE ·
  trigger: on create / on update · statement: "The system shall prevent saving a note when
  its body is missing or blank." · message ar: «نصّ الملاحظة مطلوب.» · en: "A note body is
  required." · DB enforcement: `CHK_NOTE_NOTE_NOTE_BODY` + NOT NULL · owner layer: domain class.
- **RULE-NOTE-003** — حدود طول العنوان والنص / Title and body length limits · scope
  CREATE|UPDATE · trigger: on create / on update · statement: "The system shall prevent
  saving a note when its title exceeds 200 characters or its body exceeds 4000 characters."
  · message ar: «العنوان لا يتجاوز 200 حرف والنصّ لا يتجاوز 4000 حرف.» · en: "A title may
  not exceed 200 characters and a body may not exceed 4000 characters." · DB enforcement:
  the column widths `VARCHAR(200)` / `VARCHAR(4000)` are the floor; the message is produced
  by the application · owner layer: domain class.
- **RULE-NOTE-004** — الملكية لا تتغيّر بعد الإنشاء / Ownership is immutable after creation ·
  scope UPDATE · trigger: on update · statement: "The system shall prevent any change to a
  note's owner after the note is created." · message ar: «لا يمكن تغيير مالك الملاحظة.» ·
  en: "A note's owner cannot be changed." · DB enforcement: application-level, and enforced
  structurally: the owner is absent from every request DTO and no mapper writes it after
  creation · owner layer: controller/service (DTO shape). No error-catalog row and no
  enforcing branch — ADR-NOTE-006.
- **RULE-NOTE-005** — لا عملية على ملاحظة لا يملكها الطالب / No operation on a note the
  requester does not own · scope ALL · trigger: on read / on update / on deactivate / on
  search · statement: "The system shall prevent any read, update or deactivation of a note
  whose owner differs from the authenticated requester." · message ar: «الملاحظة غير
  موجودة.» · en: "The note was not found." · DB enforcement: application-level — the owner
  predicate is part of every query (QR-NOTE-003, QR-NOTE-004, QR-NOTE-005, QR-NOTE-006), not
  a branch after the read; structurally supported by `IDX_NOTE_NOTE_OWN_ACT` · owner layer:
  repository predicate + service.
- **RULE-NOTE-006** — لا تعديل لملاحظة معطَّلة / No editing of a deactivated note · scope
  UPDATE · trigger: on update · statement: "The system shall prevent updating a note while
  the note is inactive." · message ar: «لا يمكن تعديل ملاحظة معطَّلة.» · en: "A deactivated
  note cannot be edited." · DB enforcement: application-level, carried in the UPDATE
  predicate (QR-NOTE-005) · owner layer: domain class + repository predicate.
- **RULE-NOTE-007** — لا تعطيل مكرَّر / No repeated deactivation · scope DELETE · trigger: on
  deactivate · statement: "The system shall prevent deactivating a note that is already
  inactive." · message ar: «الملاحظة معطَّلة أصلًا.» · en: "The note is already
  deactivated." · DB enforcement: application-level, carried in the UPDATE predicate
  (QR-NOTE-006) · owner layer: domain class + repository predicate.

STATE MACHINE  state column `is_active_fl` (DBF-NOTE-005) · values TRUE (فعّالة / active),
FALSE (معطَّلة / deactivated) · initial TRUE at creation (REQ-NOTE-003) · transition
TRUE → FALSE, trigger `deactivate`, actor the note's owner · terminal FALSE — there is no
reverse transition in v1 (reactivation is out of scope, SRS A2) · invalid transition
FALSE → FALSE is refused by RULE-NOTE-007. The row itself is never removed (REQ-NOTE-008),
and no endpoint of this plan issues a DELETE statement.

CROSS-MODULE  none — the db-script XM register carries 0 rows for this module. The
authenticated principal reaches `owner_user_ref` and the audit columns as a string handed
over by the platform interceptor, which is a value, not a dependency on another module's
table (SRS A8, precedent ADR-FIN-001).

OPERATIONS  VIEW · CREATE · UPDATE · DELETE — the four actions SCR-REQ-NOTE-001 §B4 grants
on the page code `NOTE_NOTES`, where `DELETE` is the soft deactivation of REQ-NOTE-007.
Every one of them is answered by an `API-*` block in PHASE 3 that names this entity.

REPOSITORY OPS → QR-NOTE-001 (NATIVE, key allocation) · QR-NOTE-002 (SAVE) · QR-NOTE-003 (FIND_BY_CRITERIA) · QR-NOTE-004 (FIND_ONE) · QR-NOTE-005 (UPDATE) · QR-NOTE-006 (UPDATE, deactivate).
No EXISTS query: the entity has no unique business value
to check, because it has no business code and no RULE demands uniqueness of any column.
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-NOTE-001,REQ-NOTE-002,REQ-NOTE-003,REQ-NOTE-004,REQ-NOTE-005,REQ-NOTE-006,REQ-NOTE-007,REQ-NOTE-008,REQ-NOTE-009,REQ-NOTE-010,REQ-NOTE-011,REQ-NOTE-012,REQ-NOTE-013,REQ-NOTE-014 -->
## PHASE 3 — SVC-API

API count is 5, below the split threshold of 8, so no SUB is opened and the five atom
blocks sit directly under this phase. The five are exactly the operations SRS §B5 names —
no endpoint is added beyond them and none of them is dropped.

<!-- API:API-NOTE-001:START traces=REQ-NOTE-001,REQ-NOTE-002,REQ-NOTE-003,REQ-NOTE-004,REQ-NOTE-015,REQ-NOTE-016,REQ-NOTE-017,REQ-NOTE-018,DBF-NOTE-002,DBF-NOTE-003,DBF-NOTE-004,DBF-NOTE-005 -->
### API-NOTE-001 — create note
Entity       : ENT-NOTE-001 · operation CREATE
Endpoint     : POST /api/v1/note/notes   verb: POST
Layers       : controller → `NoteController.create` ; service → `NoteService.create`
Request      : body `NoteCreateRequest` — noteTitle (DBF-NOTE-002, String, required, max 200, CHK_NOTE_NOTE_NOTE_TITLE) · noteBody (DBF-NOTE-003, String, required, max 4000, CHK_NOTE_NOTE_NOTE_BODY) · no path param, no query param. Excluded system fields: the key, the owner, the active flag and the four audit fields — a value supplied for any of them is ignored.
Response     : 201 · `NoteResponse` {notePk, noteTitle, noteBody, isActiveFl, createdBy, createdAt, updatedBy, updatedAt} · not paginated · envelope `ApiResponse<T>`
Validations  : RULE-NOTE-001 "The system shall prevent saving a note when its title is missing or blank." (trigger: on create · ar: «عنوان الملاحظة مطلوب.» · en: "A note title is required.") · RULE-NOTE-002 "The system shall prevent saving a note when its body is missing or blank." (trigger: on create · ar: «نصّ الملاحظة مطلوب.» · en: "A note body is required.") · RULE-NOTE-003 "The system shall prevent saving a note when its title exceeds 200 characters or its body exceeds 4000 characters." (trigger: on create · ar: «العنوان لا يتجاوز 200 حرف والنصّ لا يتجاوز 4000 حرف.» · en: "A title may not exceed 200 characters and a body may not exceed 4000 characters.")
Errors       : NOTE-400-TITLE-REQUIRED (400, RULE-NOTE-001) · NOTE-400-BODY-REQUIRED (400, RULE-NOTE-002) · NOTE-400-LENGTH-EXCEEDED (400, RULE-NOTE-003) · NOTE-401 (401, PLATFORM-STD) · NOTE-403-SCREEN-FORBIDDEN (403, PLATFORM-STD) · NOTE-403-ACTION-FORBIDDEN (403, PLATFORM-STD) · NOTE-500 (500, PLATFORM-STD)
Orchestration : authorise → validate (RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003) → integrate (none — no XM row exists) → set the fields the request does not carry: the owner DBF-NOTE-004 from the authenticated principal (REQ-NOTE-002), the active flag DBF-NOTE-005 to TRUE (REQ-NOTE-003), the audit columns DBF-NOTE-006 and DBF-NOTE-007 from the principal and the clock (AC-NOTE-002) → allocate the key DBF-NOTE-001 (QR-NOTE-001, from SEQ_NOTE_NOTE) → persist (QR-NOTE-002, table NOTE_NOTE)
Repository   : QR-NOTE-001, QR-NOTE-002 · join NONE · transaction READ_WRITE
Concurrency  : the only allocated value is the primary key, and QR-NOTE-001 allocates it atomically from the sequence — two simultaneous creates cannot receive the same key, and nothing here is read and then decided on. The note carries no business code and no unique column, so there is no second value two callers could race for.
Security     : screen NOTE_NOTES · permission `PERM_NOTE_NOTES_CREATE`, gated by `PERM_NOTE_NOTES_VIEW` — both verified before the method body runs
Localization : messages in ar + en (see Validations and the ERROR CATALOG); the note's own content stays in its author's language (POL-NOTE-005)
<!-- API:API-NOTE-001:END -->

<!-- API:API-NOTE-002:START traces=REQ-NOTE-009,REQ-NOTE-010,REQ-NOTE-011,REQ-NOTE-012,REQ-NOTE-013,REQ-NOTE-015,REQ-NOTE-016,REQ-NOTE-017,REQ-NOTE-018,DBF-NOTE-002,DBF-NOTE-003,DBF-NOTE-004,DBF-NOTE-005 -->
### API-NOTE-002 — search notes
Entity       : ENT-NOTE-001 · operation VIEW
Endpoint     : GET /api/v1/note/notes   verb: GET
Layers       : controller → `NoteController.search` ; service → `NoteService.search`
Request      : query params `text` (optional, matched against DBF-NOTE-002 and DBF-NOTE-003, contains) · `active` (optional boolean over DBF-NOTE-005; absent = TRUE, REQ-NOTE-010; `false` is the deliberate path to the deactivated list, REQ-NOTE-013) · `page`, `size` (default 20, capped at 200) · `sort` (updatedAt | createdAt). No body. Excluded system fields: the owner DBF-NOTE-004 is never a parameter — it is always the authenticated principal (REQ-NOTE-009).
Response     : 200 · `Page<NoteListItemResponse>` {notePk, noteTitle, body excerpt, isActiveFl, updatedAt, createdAt} · paginated (`Page<T>`) · envelope `ApiResponse<T>`
Validations  : RULE-NOTE-005 "The system shall prevent any read, update or deactivation of a note whose owner differs from the authenticated requester." (trigger: on search · ar: «الملاحظة غير موجودة.» · en: "The note was not found.") — on this endpoint the rule never produces a message: it is a predicate of the query, so a foreign note is not refused, it is not a row of the result at all (AC-NOTE-014). The requested sort field is checked against the set PHASE 1 — CORE declares.
Errors       : NOTE-400-INVALID-SORT (400, PLATFORM-STD) · NOTE-401 (401, PLATFORM-STD) · NOTE-403-SCREEN-FORBIDDEN (403, PLATFORM-STD) · NOTE-500 (500, PLATFORM-STD). An empty page is success, never NOTE-404-NOTE-NOT-FOUND.
Orchestration : authorise → bind the owner predicate to the authenticated principal → validate the sort field → load (QR-NOTE-003, table NOTE_NOTE) → map into the page envelope. This endpoint writes no column of any kind.
Repository   : QR-NOTE-003 · join NONE · transaction READ_ONLY
Concurrency  : NONE — this endpoint neither allocates a unique value nor reads-then-writes.
Security     : screen NOTE_NOTES · permission `PERM_NOTE_NOTES_VIEW` (the gateway action) — verified before processing
Localization : messages in ar + en; list content is the author's own text
<!-- API:API-NOTE-002:END -->

<!-- API:API-NOTE-003:START traces=REQ-NOTE-006,REQ-NOTE-014,REQ-NOTE-015,REQ-NOTE-016,REQ-NOTE-017,REQ-NOTE-018,DBF-NOTE-001,DBF-NOTE-002,DBF-NOTE-003,DBF-NOTE-005 -->
### API-NOTE-003 — read note
Entity       : ENT-NOTE-001 · operation VIEW
Endpoint     : GET /api/v1/note/notes/{id}   verb: GET
Layers       : controller → `NoteController.read` ; service → `NoteService.read`
Request      : path param `{id}` → DBF-NOTE-001 (Long, required). No query params and no body.
Response     : 200 · `NoteResponse` {notePk, noteTitle, noteBody, isActiveFl, createdBy, createdAt, updatedBy, updatedAt} · not paginated · envelope `ApiResponse<T>`. A deactivated note returns its stored content unchanged (REQ-NOTE-008, REQ-NOTE-014); the response carries `isActiveFl` so the screen renders it read-only and offers no save action.
Validations  : RULE-NOTE-005 "The system shall prevent any read, update or deactivation of a note whose owner differs from the authenticated requester." (trigger: on read · ar: «الملاحظة غير موجودة.» · en: "The note was not found.") — a note owned by somebody else and a note that does not exist produce the identical answer, and the response body discloses nothing of either (AC-NOTE-010, ADR-NOTE-003).
Errors       : NOTE-404-NOTE-NOT-FOUND (404, RULE-NOTE-005) · NOTE-401 (401, PLATFORM-STD) · NOTE-403-SCREEN-FORBIDDEN (403, PLATFORM-STD) · NOTE-500 (500, PLATFORM-STD)
Orchestration : authorise → load by key and owner in one predicate (QR-NOTE-004, table NOTE_NOTE) → an empty result raises NOTE-404-NOTE-NOT-FOUND → map. This endpoint writes no column of any kind.
Repository   : QR-NOTE-004 · join NONE · transaction READ_ONLY
Concurrency  : NONE — this endpoint neither allocates a unique value nor reads-then-writes.
Security     : screen NOTE_NOTES · permission `PERM_NOTE_NOTES_VIEW` (the gateway action) — verified before processing
Localization : messages in ar + en
<!-- API:API-NOTE-003:END -->

<!-- API:API-NOTE-004:START traces=REQ-NOTE-005,REQ-NOTE-006,REQ-NOTE-015,REQ-NOTE-016,REQ-NOTE-017,REQ-NOTE-018,DBF-NOTE-002,DBF-NOTE-003,DBF-NOTE-008,DBF-NOTE-009 -->
### API-NOTE-004 — update note
Entity       : ENT-NOTE-001 · operation UPDATE
Endpoint     : PUT /api/v1/note/notes/{id}   verb: PUT
Layers       : controller → `NoteController.update` ; service → `NoteService.update`
Request      : path param `{id}` → DBF-NOTE-001 (Long, required) · body `NoteUpdateRequest` — noteTitle (DBF-NOTE-002, String, required, max 200, CHK_NOTE_NOTE_NOTE_TITLE) · noteBody (DBF-NOTE-003, String, required, max 4000, CHK_NOTE_NOTE_NOTE_BODY). Excluded system fields: the owner (RULE-NOTE-004), the active flag, the key and the four audit fields.
Response     : 200 · `NoteResponse` {notePk, noteTitle, noteBody, isActiveFl, createdBy, createdAt, updatedBy, updatedAt} · not paginated · envelope `ApiResponse<T>`
Validations  : RULE-NOTE-001 "The system shall prevent saving a note when its title is missing or blank." (ar: «عنوان الملاحظة مطلوب.» · en: "A note title is required.") · RULE-NOTE-002 "The system shall prevent saving a note when its body is missing or blank." (ar: «نصّ الملاحظة مطلوب.» · en: "A note body is required.") · RULE-NOTE-003 "The system shall prevent saving a note when its title exceeds 200 characters or its body exceeds 4000 characters." (ar: «العنوان لا يتجاوز 200 حرف والنصّ لا يتجاوز 4000 حرف.» · en: "A title may not exceed 200 characters and a body may not exceed 4000 characters.") · RULE-NOTE-004 "The system shall prevent any change to a note's owner after the note is created." (ar: «لا يمكن تغيير مالك الملاحظة.» · en: "A note's owner cannot be changed.") — enforced by DTO shape, with no branch and no catalog row (ADR-NOTE-006) · RULE-NOTE-005 "The system shall prevent any read, update or deactivation of a note whose owner differs from the authenticated requester." (ar: «الملاحظة غير موجودة.» · en: "The note was not found.") · RULE-NOTE-006 "The system shall prevent updating a note while the note is inactive." (ar: «لا يمكن تعديل ملاحظة معطَّلة.» · en: "A deactivated note cannot be edited.")
Errors       : NOTE-400-TITLE-REQUIRED (400, RULE-NOTE-001) · NOTE-400-BODY-REQUIRED (400, RULE-NOTE-002) · NOTE-400-LENGTH-EXCEEDED (400, RULE-NOTE-003) · NOTE-404-NOTE-NOT-FOUND (404, RULE-NOTE-005) · NOTE-409-NOTE-INACTIVE (409, RULE-NOTE-006) · NOTE-401 (401, PLATFORM-STD) · NOTE-403-SCREEN-FORBIDDEN (403, PLATFORM-STD) · NOTE-403-ACTION-FORBIDDEN (403, PLATFORM-STD) · NOTE-500 (500, PLATFORM-STD)
Orchestration : authorise → load by key and owner (QR-NOTE-004) → an empty result raises NOTE-404-NOTE-NOT-FOUND → validate the content rules → persist with the state predicate carried into the statement itself (QR-NOTE-005, table NOTE_NOTE), writing the columns the request does not carry: the audit columns DBF-NOTE-008 and DBF-NOTE-009 from the principal and the clock → 0 rows affected raises NOTE-409-NOTE-INACTIVE. The owner DBF-NOTE-004 and the flag DBF-NOTE-005 are read as predicates and never written here.
Repository   : QR-NOTE-004, QR-NOTE-005 · join NONE · transaction READ_WRITE
Concurrency  : an update and a deactivation of the same note must not both succeed. The guard is the conditional statement: QR-NOTE-005 carries `is_active_fl = TRUE` in its own WHERE clause, so the database decides which of two concurrent writers affects the row, and the other sees 0 rows affected and answers NOTE-409-NOTE-INACTIVE. The state read by QR-NOTE-004 is never what the decision rests on — two requests would both pass such a check.
Security     : screen NOTE_NOTES · permission `PERM_NOTE_NOTES_UPDATE`, gated by `PERM_NOTE_NOTES_VIEW` — both verified before processing. A granted UPDATE still does not reach another user's note: ownership is a data predicate above authorisation, not a substitute for it (SRS §B4).
Localization : messages in ar + en
<!-- API:API-NOTE-004:END -->

<!-- API:API-NOTE-005:START traces=REQ-NOTE-007,REQ-NOTE-008,REQ-NOTE-015,REQ-NOTE-016,REQ-NOTE-017,REQ-NOTE-018,DBF-NOTE-005,DBF-NOTE-008,DBF-NOTE-009 -->
### API-NOTE-005 — deactivate note
Entity       : ENT-NOTE-001 · operation DELETE
Endpoint     : DELETE /api/v1/note/notes/{id}   verb: DELETE
Layers       : controller → `NoteController.deactivate` ; service → `NoteService.deactivate`
Request      : path param `{id}` → DBF-NOTE-001 (Long, required). No query params and no body.
Response     : 200 · `NoteResponse` {notePk, noteTitle, noteBody, isActiveFl, createdBy, createdAt, updatedBy, updatedAt} · not paginated · envelope `ApiResponse<T>`
Validations  : RULE-NOTE-005 "The system shall prevent any read, update or deactivation of a note whose owner differs from the authenticated requester." (trigger: on deactivate · ar: «الملاحظة غير موجودة.» · en: "The note was not found.") · RULE-NOTE-007 "The system shall prevent deactivating a note that is already inactive." (trigger: on deactivate · ar: «الملاحظة معطَّلة أصلًا.» · en: "The note is already deactivated.")
Errors       : NOTE-404-NOTE-NOT-FOUND (404, RULE-NOTE-005) · NOTE-409-ALREADY-DEACTIVATED (409, RULE-NOTE-007) · NOTE-401 (401, PLATFORM-STD) · NOTE-403-SCREEN-FORBIDDEN (403, PLATFORM-STD) · NOTE-403-ACTION-FORBIDDEN (403, PLATFORM-STD) · NOTE-500 (500, PLATFORM-STD)
Orchestration : authorise → load by key and owner (QR-NOTE-004) → an empty result raises NOTE-404-NOTE-NOT-FOUND → flip the flag the request does not carry: the active flag DBF-NOTE-005 to FALSE, with the audit columns DBF-NOTE-008 and DBF-NOTE-009 written from the principal and the clock, in one conditional statement (QR-NOTE-006, table NOTE_NOTE) → 0 rows affected raises NOTE-409-ALREADY-DEACTIVATED. The verb is DELETE and the effect is `soft` (profile.stack.db.delete_semantics): no row is ever removed (REQ-NOTE-008).
Repository   : QR-NOTE-004, QR-NOTE-006 · join NONE · transaction READ_WRITE
Concurrency  : two simultaneous deactivations of the same note must not both report success. The guard is the conditional statement: QR-NOTE-006 carries `is_active_fl = TRUE` in its own WHERE clause, so exactly one writer affects the row and the second answers NOTE-409-ALREADY-DEACTIVATED. Validating the flag first would let both requests through.
Security     : screen NOTE_NOTES · permission `PERM_NOTE_NOTES_DELETE`, gated by `PERM_NOTE_NOTES_VIEW` — both verified before processing
Localization : messages in ar + en
<!-- API:API-NOTE-005:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-NOTE-015 -->
## PHASE 4 — DOC

The implementer publishes `backend/modules/NOTE/api-docs` from the surface it actually
builds: the five endpoints of PHASE 3 with their verbs, paths, request and response types,
their HTTP statuses and the error codes of the ERROR CATALOG. That published file — not this
plan's contract draft — is what the frontend stage and `api-verify` read.

What the api-docs must carry for this module: the base path `/api/v1/note/notes`; the
`ApiResponse<T>` and `Page<T>` envelopes; the paging defaults (20, maximum 200); the sort
fields the search accepts (`updatedAt`, `createdAt`); and the status → code table for the
eleven catalog rows. Nothing in this module is documented that PHASE 3 does not specify, and
no endpoint of PHASE 3 is left out of it.

No other document is produced by this stage: the module has no report, no export and no
printable output in v1.
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=REQ-NOTE-002,REQ-NOTE-017 -->
## PHASE 5 — INT-C

**Empty by construction, present by requirement.** The db-script XM register carries 0 rows
for NOTE, and this stage mints none: nothing in the plan above is the first reader of
another module's data.

| XM | classification | target | interface | the thing the target publishes | status |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

Why each consumed SEC entity is still not an XM row — the classification is the SRS's (A8)
and the precedent is ADR-FIN-001, and nothing this stage wrote changes either:

- ENT-SEC-001 (User) — `ownerUserRef` and the audit columns hold the principal **string**
  the standard platform interceptor hands to every request. This module reads no row of
  SEC's own table, holds no foreign key to it and calls no operation on it, so there is no
  dependency to track. A principal that arrives as a value is not an integration.
- ENT-SEC-004 (ModuleRegistry), ENT-SEC-005 (ScreenRegistry), ENT-SEC-006 (ActionRegistry) —
  registration is deployment-time data (REQ-NOTE-017), written as seed rows, not read at
  runtime by any endpoint above. The rows themselves are listed in the deployment-seed section of PHASE 7,
  where their producer is named.

Inbound dependencies: none. ENT-NOTE-001 is PRIVATE (POL-NOTE-001) and no module consumes
it, so no `XM-INBOUND-STUB-<n>` row exists either. Because the platform is ONE deployable
(`profile.conventions.module_interface: in_process`), there is no HTTP client, no base path
to another module, no timeout and no network error path anywhere in this plan — and
therefore no ERROR CATALOG row describing a network failure that cannot occur.
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-NOTE-002,REQ-NOTE-017 -->
## PHASE 6 — INT-R

**Empty by construction, present by requirement.** There is no XM row to activate, so there
is no status row, no mock, no simulation and no workaround to describe.

| XM | status | workaround / mock strategy |
|---|---|---|
| — | — | — |

Nothing in this module is blocked on another module's delivery: every endpoint of PHASE 3
can be built, deployed and called with SEC's standard interceptor in place and nothing else.
The one deployment-time prerequisite is data, not code, and it is stated in the
deployment-seed section of PHASE 7.
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=REQ-NOTE-015,REQ-NOTE-016,REQ-NOTE-017,REQ-NOTE-018 -->
## PHASE 7 — SEC-BE

**One screen, one permission set.** SCR-REQ-NOTE-001 (شاشة الملاحظات / Notes) is composite —
search and entry are one screen — so the module registers exactly one page code,
`NOTE_NOTES`, and mints exactly four permission names from it. A second permission set would
be a second screen and a growth in scope (REQ-NOTE-015, POL-NOTE-006).

Every endpoint of PHASE 3 verifies its permission through the platform authorisation layer
before any processing, on the page code and the action the operation carries (REQ-NOTE-018).
No role name is compared anywhere in this module's code: services see permissions, never
roles. `VIEW` is the gateway — a requester without it reaches no endpoint of this module,
whatever else they hold (REQ-NOTE-016).

**Registration rows** (REQ-NOTE-017) — written at deployment into the platform registries,
with the column names taken from SEC's own script, never from here:
- one module row with the code `NOTE` (ENT-SEC-004);
- one page row in `SEC_PAGES` with the page code `NOTE_NOTES`, its ar/en name
  (شاشة الملاحظات / Notes) and its menu parent (ENT-SEC-005);
- four action rows on that page — VIEW, CREATE, UPDATE, DELETE (ENT-SEC-006).

Without these rows the module gate fails closed and the screen is absent from the menu even
for a granted user (AC-NOTE-022, AC-NOTE-023) — which is why they are bootstrap data below
and not a runtime concern.

**Forbidden responses** map through `LocalizedException → {code, messageAr, messageEn}` with
a catalog row: NOTE-403-SCREEN-FORBIDDEN for the gate and NOTE-403-ACTION-FORBIDDEN for an
ungranted action (AC-NOTE-022, AC-NOTE-024).

**Permission matrix** — one row per composite screen. A cell is marked only where the row
also names the endpoint that serves it and the permission for that action:

| Screen | ENT-* | API-* serving it | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|---|---|
| NOTE_NOTES | ENT-NOTE-001 | API-NOTE-001, API-NOTE-002, API-NOTE-003, API-NOTE-004, API-NOTE-005 | ✓ PERM_NOTE_NOTES_VIEW | ✓ PERM_NOTE_NOTES_CREATE | ✓ PERM_NOTE_NOTES_UPDATE | ✓ PERM_NOTE_NOTES_DELETE |

Ownership is a data constraint **above** authorisation, never a replacement for it: holding
`PERM_NOTE_NOTES_UPDATE` does not let a user edit another user's note, because RULE-NOTE-005
is a predicate of every query (SRS §B4, AC-NOTE-009).

### BOOTSTRAP DATA — NOTE v1

The rows that must exist before any endpoint of this module can succeed. Every row names who
produces it, not only that it is needed.

| item | value | producer |
|---|---|---|
| LOOKUP KEY | none — SRS A6: the module owns no lookup key and consumes none, so no value of any module's lookup table is read by any endpoint above | seed source: not applicable — there is no key to seed, in this module's tables or in another module's |
| PERMISSION | PERM_NOTE_NOTES_VIEW | grant target: role `مستخدم شاشة الملاحظات / Notes-screen user` — the SEC role seed grants it, and the module grant row for `NOTE` is granted to the same role; without the grant the name exists and authorises nobody |
| PERMISSION | PERM_NOTE_NOTES_CREATE | grant target: role `مستخدم شاشة الملاحظات / Notes-screen user`, granted in the same SEC role seed |
| PERMISSION | PERM_NOTE_NOTES_UPDATE | grant target: role `مستخدم شاشة الملاحظات / Notes-screen user`, granted in the same SEC role seed |
| PERMISSION | PERM_NOTE_NOTES_DELETE | grant target: role `مستخدم شاشة الملاحظات / Notes-screen user`, granted in the same SEC role seed |
| REGISTRATION | module row `NOTE`, page row `NOTE_NOTES`, four action rows | seed source: this module's deployment seed, written into the platform registries (ENT-SEC-004, ENT-SEC-005, ENT-SEC-006) — REQ-NOTE-017 |

No required column of `NOTE_NOTE` is seeded: every one of them is written by an endpoint of
PHASE 3 or by the platform (the key from the sequence, the audit columns by the interceptor),
so this section carries no data row for the module's own table — the table starts empty and
the first create call fills it.

The frontend stage references these permission names and never redeclares them.
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-NOTE-015 -->
## PHASE 8 — ALIGN-BE

Every row below names the mechanical check that backs it, and there are no other rows. Each
mark is the analyze report's result for that check, copied — not an independent judgement.

```
ALIGN — NOTE v1
row               backing check        mark                assertion
TRACEABILITY      traces               ✓                   every PHASE/SUB/atom block carries traces=, and every API traces to its REQ and its DBF
COVERED           orphans              ✓                   every REQ is covered by ≥1 API or DBF
BINDING (§2A)     value-agreement      ✓                   every DBF names the same physical column here as the db-script declares for it
MANIFEST (§4)     count-agrees         ✓                   every total this plan states equals the rows it heads
WRITERS           required-writer      ✓                   every required column is written by an endpoint, or the row states why not
QRC (§5)          orphans              ✓                   every catalogued query is reached by ≥1 API
API (R3)          code-format          ✓                   every catalog code is an instance of the declared format and carries a status the platform can emit
RULE INPUTS       data-source          ✓                   every RULE enforced at runtime names where the data it READS comes from, or is deferred
CROSS-MODULE      registry-agree       — examined nothing   every registered XM is placed here, and every XM minted here is back-registered
FOREIGN IDS       xref-resolve         ✓                   every id of another module cited here is defined in that module's own registry
BOOTSTRAP DATA    bootstrap-complete   ✓                   every lookup key and every permission has a row naming who produces it
SECURITY (R7)     operation-resolves   ✓                   every declared entity operation resolves to an API, and every marked matrix cell names its API and its permission
DEMAND (SRS)      operation-resolves   — examined nothing   every operation an SRS screen names is built by an API, or the plan states why it is not
DECISIONS         refs-exist           ✓                   every ADR this plan cites exists on disk in erp/decisions/NOTE/
PATHS             paths-resolve        ✓                   every path the generated manifest and execution state emit resolves to something that exists
COVERAGE          (the report)         C7.23, C7.5, C7.5b — the three clauses the analyze report lists as having examined nothing
RESULT PASSED ✓ — 0 findings
```

**What the two empty clauses mean, stated rather than passed over.** A row nothing examined is
not a row that passed:

- `C7.5` / `C7.5b` (`registry-agree`, XM) had no rows to compare in either direction: the
  db-script register carries 0 XM and this stage minted none. The agreement is vacuous, and
  the plan's claim of no cross-module dependency rests on SRS A8 and PHASE 5, not on this check.
- `C7.23` (`operation-resolves`, the SRS demand) read SCR-REQ-NOTE-001's `Operations` line and
  parsed no operation word from it: the SRS separates that list with `·`, and the clause splits
  on `,` `;` `/`. So the machine did not verify that each operation the screen offers is built.
  The manual reading is recorded here instead, and it is exact — `search` and `list` are
  API-NOTE-002, `create` is API-NOTE-001, `read` is API-NOTE-003, `update` is API-NOTE-004 and
  `deactivate` is API-NOTE-005; every one of those blocks names ENT-NOTE-001, the entity the
  screen's `Entities` line declares. No operation of the screen is unbuilt and none is excluded.
  Nothing in this plan can make that clause run — the separator is the upstream artifact's, and
  P3.1 does not edit the SRS — so it is a factory finding, not a module one (smoke-findings).
<!-- PHASE:ALIGN-BE:END -->

## Coverage tables

**ENT / DBF → phases → QR → XM**

| ENT | DBF | phases | QR | XM |
|---|---|---|---|---|
| ENT-NOTE-001 | DBF-NOTE-001 | DATA-DOM, SVC-API | QR-NOTE-001, QR-NOTE-002, QR-NOTE-004, QR-NOTE-005, QR-NOTE-006 | none |
| ENT-NOTE-001 | DBF-NOTE-002 | DATA-DOM, SVC-API | QR-NOTE-002, QR-NOTE-003, QR-NOTE-004, QR-NOTE-005 | none |
| ENT-NOTE-001 | DBF-NOTE-003 | DATA-DOM, SVC-API | QR-NOTE-002, QR-NOTE-003, QR-NOTE-004, QR-NOTE-005 | none |
| ENT-NOTE-001 | DBF-NOTE-004 | DATA-DOM, SVC-API | QR-NOTE-002, QR-NOTE-003, QR-NOTE-004, QR-NOTE-005, QR-NOTE-006 | none |
| ENT-NOTE-001 | DBF-NOTE-005 | DATA-DOM, SVC-API | QR-NOTE-002, QR-NOTE-003, QR-NOTE-005, QR-NOTE-006 | none |
| ENT-NOTE-001 | DBF-NOTE-006 | DATA-DOM, SVC-API | QR-NOTE-002 | none |
| ENT-NOTE-001 | DBF-NOTE-007 | DATA-DOM, SVC-API | QR-NOTE-002, QR-NOTE-003 | none |
| ENT-NOTE-001 | DBF-NOTE-008 | DATA-DOM, SVC-API | QR-NOTE-005, QR-NOTE-006 | none |
| ENT-NOTE-001 | DBF-NOTE-009 | DATA-DOM, SVC-API | QR-NOTE-003, QR-NOTE-005, QR-NOTE-006 | none |

**RULE → API → catalog code**

| RULE | API | catalog code |
|---|---|---|
| RULE-NOTE-001 | API-NOTE-001, API-NOTE-004 | NOTE-400-TITLE-REQUIRED |
| RULE-NOTE-002 | API-NOTE-001, API-NOTE-004 | NOTE-400-BODY-REQUIRED |
| RULE-NOTE-003 | API-NOTE-001, API-NOTE-004 | NOTE-400-LENGTH-EXCEEDED |
| RULE-NOTE-004 | API-NOTE-004 | none — enforced by DTO shape, ADR-NOTE-006 |
| RULE-NOTE-005 | API-NOTE-002, API-NOTE-003, API-NOTE-004, API-NOTE-005 | NOTE-404-NOTE-NOT-FOUND |
| RULE-NOTE-006 | API-NOTE-004 | NOTE-409-NOTE-INACTIVE |
| RULE-NOTE-007 | API-NOTE-005 | NOTE-409-ALREADY-DEACTIVATED |

**XM → status → blocks → workaround** — no row: the module declares no cross-module
dependency, so nothing is blocked and no workaround exists.

## Decisions applied

| ADR | What | Status |
|---|---|---|
| ADR-NOTE-005 | The infrastructure rows of the ERROR CATALOG (401, both 403s, the invalid-sort 400 and 500) carry RULE = PLATFORM-STD: they are platform behaviours, not business rules of this module | ACCEPTED (non-breaking) — erp/decisions/NOTE/ADR-NOTE-005.md |
| ADR-NOTE-006 | RULE-NOTE-004 is enforced by DTO shape and carries no catalog row and no branch — a client-supplied owner is ignored (AC-NOTE-003), never rejected | ACCEPTED (non-breaking) — erp/decisions/NOTE/ADR-NOTE-006.md |
| ADR-NOTE-001 (P1) | The narrowed `master` defaults — no `nameAr`, `nameEn` or `code` on ENT-NOTE-001 | ACCEPTED (non-breaking), applied here |
| ADR-NOTE-002 (P1) | The 200 / 4000-character limits RULE-NOTE-003 states | ACCEPTED (non-breaking), applied here |
| ADR-NOTE-003 (P1) | A non-owner's request is answered "not found", never "forbidden" | ACCEPTED (non-breaking), applied here |
| ADR-NOTE-004 (P2) | No index on the substring-filtered title/body columns | ACCEPTED (non-breaking), applied here |

No BLOCKED ADR — the pass was not stopped. No question was raised.
══════════════════════════════════════════════════════════════════
