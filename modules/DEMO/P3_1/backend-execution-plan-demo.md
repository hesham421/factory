# BACKEND EXECUTION PLAN — الملاحظات الشخصية (Personal Notes) — DEMO
══════════════════════════════════════════════════════════════════

## EXECUTION PLAN INDEX — DEMO — PLAN-ID: PLAN-DEMO-001
══════════════════════════════════════════════════════════════════
Feature Code   : DEMO-001
DBS-ID         : DBS-DEMO-01
Governed by    : Execution Plan Governance Engine (Project 3) v3 (light) — PASS 1 (Backend)
Output Mode    : SINGLE-FILE — Agent-Ready Specification
Open Questions : None — see OQ Log (srs-demo.md)
══════════════════════════════════════════════════════════════════

ENTITY REGISTRY (this plan)
───────────────────────────────────────────────────────────────
ENTITY-ID          │ Entity Name │ DB Table    │ Business Code │ Operations
───────────────────┼─────────────┼─────────────┼───────────────┼──────────────
ENTITY-DEMO-001    │ Note        │ DEMO_NOTE   │ NOT APPLIED (BC-RULE-0 — see DRV-DEMO-003) │ CRUD (soft delete)

FIELD REGISTRY (this plan)
───────────────────────────────────────────────────────────────
FIELD-ID  │ Field Name    │ DBF-ID   │ Type              │ Read-Only
──────────┼───────────────┼──────────┼───────────────────┼──────────────
FIELD-0001│ noteId        │ DBF-0001 │ Long              │ System (PK)
FIELD-0002│ title         │ DBF-0002 │ String(200)       │ No
FIELD-0003│ content       │ DBF-0003 │ String (TEXT/Lob) │ No
FIELD-0004│ statusId      │ DBF-0004 │ String (code)     │ System (server-managed lifecycle)
FIELD-0005│ ownerUserId   │ DBF-0005 │ Long              │ System (from auth context)
FIELD-0006│ createdBy     │ DBF-0006 │ String            │ System (AuditEntityListener)
FIELD-0007│ createdAt     │ DBF-0007 │ LocalDateTime     │ System (AuditEntityListener)
FIELD-0008│ updatedBy     │ DBF-0008 │ String            │ System (AuditEntityListener)
FIELD-0009│ updatedAt     │ DBF-0009 │ LocalDateTime     │ System (AuditEntityListener)
Note: no Business Code field exists on this entity (DRV-DEMO-003) — the
"Business Code fields are always Read-Only" rule is N/A here.

API REGISTRY (this plan)
───────────────────────────────────────────────────────────────
API-ID        │ Operation      │ HTTP Method │ Endpoint
──────────────┼────────────────┼─────────────┼──────────────────────────
API-DEMO-001  │ Create         │ POST        │ /api/v1/demo/notes
API-DEMO-002  │ List (search)  │ GET         │ /api/v1/demo/notes
API-DEMO-003  │ Get by id      │ GET         │ /api/v1/demo/notes/{id}
API-DEMO-004  │ Update         │ PUT         │ /api/v1/demo/notes/{id}
API-DEMO-005  │ Delete (soft)  │ DELETE      │ /api/v1/demo/notes/{id}

RULE REGISTRY (this plan)
───────────────────────────────────────────────────────────────
RULE-ID          │ Rule Name                    │ Scope  │ ENTITY-ID       │ Message-AR defined
──────────────────┼──────────────────────────────┼────────┼─────────────────┼───────────────────
RULE-DEMO-001    │ العنوان إلزامي (title required)│ CREATE/UPDATE │ ENTITY-DEMO-001 │ YES
RULE-DEMO-002    │ حد أقصى لطول المحتوى           │ CREATE/UPDATE │ ENTITY-DEMO-001 │ YES
RULE-DEMO-003    │ الوصول يقتصر على المالك        │ READ/UPDATE/DELETE │ ENTITY-DEMO-001 │ YES
RULE-DEMO-004    │ الحذف ناعم (soft delete)       │ DELETE │ ENTITY-DEMO-001 │ YES (success message, not an error — see Error Catalog note)
RULE-DEMO-005    │ لا تعديل على ملاحظة محذوفة     │ UPDATE │ ENTITY-DEMO-001 │ YES

SCREEN REGISTRY (this plan)
───────────────────────────────────────────────────────────────
SCR-ID          │ Screen Name        │ Type      │ ENTITY-ID
─────────────────┼────────────────────┼───────────┼──────────────
SCR-DEMO-001    │ ملاحظاتي (My Notes)│ COMPOSITE (Search + Entry via Side Drawer) │ ENTITY-DEMO-001

LOV REGISTRY (this plan)
───────────────────────────────────────────────────────────────
LOV-ID          │ LOOKUP_CODE   │ Used In Field │ ENTITY-ID
─────────────────┼───────────────┼───────────────┼──────────────
LOV-DEMO-001    │ NOTE_STATUS (fixed, static — DB CHECK constraint, no dynamic lookup service — see srs-demo.md/db-script-demo.md) │ statusId │ ENTITY-DEMO-001
No LOV endpoint is generated for LOV-DEMO-001 — its two values (ACTIVE,
DELETED) are embedded directly in the API contracts below, per its
already-documented deviation from the dynamic MD_LOOKUP_DETAIL pattern.

QUERY REFERENCE CATALOG SUMMARY
───────────────────────────────────────────────────────────────
QR-ID          │ Operation           │ Phase     │ Entity
─────────────────┼─────────────────────┼───────────┼──────────────
QR-DEMO-0001   │ FIND_BY_CRITERIA (list, owner+ACTIVE) │ SVC+API │ ENTITY-DEMO-001
QR-DEMO-0002   │ FIND_ONE (by pk, owner-checked)       │ SVC+API │ ENTITY-DEMO-001
QR-DEMO-0003   │ SAVE (create)                          │ SVC+API │ ENTITY-DEMO-001
QR-DEMO-0004   │ UPDATE (title/content)                 │ SVC+API │ ENTITY-DEMO-001
QR-DEMO-0005   │ UPDATE (soft delete — statusId=DELETED)│ SVC+API │ ENTITY-DEMO-001
⚠ ALL entries above are AGENT REFERENCE only — see Section 11.
  The agent MUST rewrite every query during implementation using the
  actual project structure, entity names, and field names.

DB ALIGNMENT     : see DB Alignment Manifest below — status: ALIGNED ✓
XM STATUS        : None — DEMO has no cross-module dependency (srs-demo.md A7, db-script-demo.md Section 2)
CONTRACT GATE    : DOC ✓ | INT-C ✓ (vacuous — no XM-IDs)
SECURITY         : Permissions matrix: 1 screen × owner-only access (no role matrix — see SEC-BE, DRV-DEMO-008)
══════════════════════════════════════════════════════════════════

## DB ALIGNMENT MANIFEST — DEMO — PLAN-ID: PLAN-DEMO-001 / DBS-ID: DBS-DEMO-01
══════════════════════════════════════════════════════════════════
FIELD-ID  │ DBF-ID   │ Plan Type      │ FK/XM-ID │ Match Status
──────────┼──────────┼────────────────┼──────────┼─────────────
FIELD-0001│ DBF-0001 │ Long           │ —        │ ✓
FIELD-0002│ DBF-0002 │ String(200)    │ —        │ ✓
FIELD-0003│ DBF-0003 │ String (@Lob)  │ —        │ ✓
FIELD-0004│ DBF-0004 │ String(20)     │ —        │ ✓
FIELD-0005│ DBF-0005 │ Long           │ —        │ ✓ (not a DB FK — see db-script-demo.md notes; not an XM-ID either, per srs-demo.md A7)
FIELD-0006│ DBF-0006 │ String(255)    │ —        │ ✓
FIELD-0007│ DBF-0007 │ LocalDateTime  │ —        │ ✓
FIELD-0008│ DBF-0008 │ String(255)    │ —        │ ✓
FIELD-0009│ DBF-0009 │ LocalDateTime  │ —        │ ✓
══════════════════════════════════════════════════════════════════
Legend: ✓ = aligned | ✗ = type mismatch (finding) | ⏸ = XM deferred
No ✗ / ⏸ entries — DEMO has no cross-module dependency (see INT-C below).

## OPEN QUESTIONS LOG — CONTINUATION
Open Questions: None active — see srs-demo.md OQ Log (canonical, owned by
Project 1). No new OQ was raised during PASS 1 generation.

## DERIVATION LOG — DEMO — PLAN-ID: PLAN-DEMO-001
══════════════════════════════════════════════════════════════════
DRV-ID        │ Element                                          │ Criterion │ Source
──────────────┼───────────────────────────────────────────────────┼───────────┼──────────────────────
DRV-DEMO-001  │ Entity base: lean audit fields only, no orgUnitId  │ N/A (platform-standard) │ platform-standards.md ENTITY/DB CONVENTIONS; domain/domain-profile.md (GENERAL — no multi-tenant model)
DRV-DEMO-002  │ No nameAr/nameEn bilingual name-field pair on Note │ N/A (platform-standard) │ domain/domain-profile.md (GENERAL, ERP localization pattern not adopted); srs-demo.md A3 (title already carries its own Label-AR/Label-EN)
DRV-DEMO-003  │ Business Code omitted entirely for ENTITY-DEMO-001 │ N/A (SRS-stated)        │ srs-demo.md A3 — "Business Code: NO — لا ينطبق BC-RULE-0"
DRV-DEMO-004  │ statusId (not isActiveFl) is the sole lifecycle/soft-delete column │ N/A (SRS-stated) │ srs-demo.md A2 General Notes (documented at P1, carried forward unchanged)
DRV-DEMO-005  │ ERR-0004 (404 Note Not Found) registered as platform-standard (RULE-ID = PLATFORM-STD) │ N/A (platform-standard, RULE-PLATFORM-ERR) │ PROJECT-3-BACKEND-ENGINE.md §8.3 RULE-PLATFORM-ERR
DRV-DEMO-006  │ RULE-DEMO-003 violation → HTTP 403 Forbidden (not 404) │ Criterion 2 (explicit "The system MUST...reject" + access-denial message text, not an existence-concealment framing) │ srs-demo.md RULE-DEMO-003 Message-AR/EN; RULE-DEMO-005 Test-Hint (explicitly defers this exact decision to P3.1/CONTRACT-4)
DRV-DEMO-007  │ RULE-DEMO-005 violation → HTTP 409 Conflict          │ Criterion 2 (rule states a state-conflict: cannot modify an already-deleted resource) │ srs-demo.md RULE-DEMO-005 Statement
DRV-DEMO-008  │ SEC-BE permission rows assigned to ALL AUTHENTICATED USERS, not a role matrix — record-level ownership (RULE-DEMO-003) is the real authorization boundary │ N/A (domain-stated) │ domain/domain-profile.md — "owner-based access, not role-based"
DRV-DEMO-009  │ UpdateNoteRequest fields (title, content) are optional-if-unchanged (partial-update semantics on PUT) — RULE-DEMO-001/002 apply only to a field that IS sent │ Criterion 2 (reconciles srs-demo.md B5 API-DEMO-004 row "title?, content?" with RULE-DEMO-001/002's "on Update" trigger) │ srs-demo.md B5 API-DEMO-004; RULE-DEMO-001, RULE-DEMO-002
══════════════════════════════════════════════════════════════════

---

<!-- PHASE:CORE:START -->
## PHASE CORE — Architectural Policies
─────────────────────────────────────────────────────────────────
Gate Status: PASSED ✓

CANONICAL ARCHITECTURE (project-standard — applies to this module like
every other; see PROJECT-3-BACKEND-ENGINE.md §8.1 for the full,
unabridged text — not reproduced here in full to keep this small
single-entity plan proportionate; every rule below is binding):

  controller/ → REST endpoint only (no business/validation logic)
  service/    → orchestration: load, validate (delegates to domain),
                integrate, persist, manage transactions
  mapper/     → Entity ↔ DTO only — no logic, no audit-field assignment
  domain/     → business rules owner (see "Domain behavior placement" below)
  repository/ → data access only, no business logic
  entity/     → JPA entity (Note) + domain behavior
  dto/        → CreateNoteRequest, UpdateNoteRequest, NoteResponse
  exception/  → DEMO module error codes (ErrorCodes.DEMO_*)

Domain behavior placement : embedded in Entity methods (Note.validateForSave()
  covers RULE-DEMO-001/002; Note.assertNotDeleted() covers RULE-DEMO-005).
  Justification: single entity, 5 rules, no cross-entity orchestration —
  a separate domain/ package would be unused ceremony for this module's
  size (proportionate to business-policies-demo.md SCOPE EXCEPTIONS).
  RULE-DEMO-003 (owner scoping) is NOT an entity domain rule — it is
  enforced at the repository/service boundary on every read/write query
  (every QR-ID below filters by ownerUserId — see Section 11), because it
  is an authorization concern, not a data-validity concern.

Entity inheritance : Note extends a lean audit base (createdBy, createdAt,
  updatedBy, updatedAt via AuditEntityListener) — NOT the full ERP
  AuditableEntity/TenantAuditableEntity lineage (no orgUnitId anywhere in
  this domain — DRV-DEMO-001). ✗ orgUnitId never appears in any DTO.

Error signaling  : service layer signals LocalizedException — NotFoundException BANNED.
Audit fields     : filled by AuditEntityListener — never appear in
                   CreateNoteRequest/UpdateNoteRequest DTOs, never set
                   manually in Mapper or Service.
Search contract  : NoteSearchRequest extends BaseSearchContractRequest.
                   ALLOWED_SORT_FIELDS = { updatedAt, createdAt, title }.
                   Default sort: updatedAt DESC (srs-demo.md B1 "الأحدث أولاً").
Transaction scope: READ_ONLY for all GET operations; READ_WRITE for
                   POST/PUT/DELETE(soft). No REQUIRES_NEW anywhere
                   (single-table module, no nested orchestration).

TYPE MAPPING (DB_TARGET = POSTGRESQL_16 — project-standard, no DRV-ID):
  BIGINT        → Java Long        (noteId, ownerUserId)
  VARCHAR(N)    → Java String      (title, statusId, createdBy, updatedBy)
  TEXT          → Java String + @Lob (content)
  TIMESTAMP     → Java LocalDateTime (createdAt, updatedAt)
  No SMALLINT/_FL flag column on this entity — statusId (not isActiveFl)
  is the lifecycle field (DRV-DEMO-004); the standard _FL→Boolean mapping
  row is N/A here.

ARCHITECTURAL POLICIES:
  - LOV values (statusId's two codes) are embedded directly in this plan's
    API contracts — never hardcoded as a Java enum with business meaning
    beyond a simple String comparison (see DOC phase LOV note).
  - Business Code: N/A — not generated, not accepted, not displayed
    (DRV-DEMO-003).
  - No nameAr/nameEn pair on this entity (DRV-DEMO-002) — title's own
    Label-AR/Label-EN (see Plan Index / DATA+DOM) cover the UI-label need.
  - No Workflow Engine (RULE-13, WORKFLOW-ENGINE-TIER = OFF) — N/A, not
    requested for DEMO.
─────────────────────────────────────────────────────────────────
<!-- PHASE:CORE:END -->

---

<!-- PHASE:DATA-DOM:START -->
## PHASE DATA+DOM — Entity & Domain Specifications

### ENTITY-DEMO-001 — Note (الملاحظة)
────────────────────────────────────────────────────────────────────────
SOURCE BINDINGS (from artifact extraction):
  DB Table       : DEMO_NOTE                     ← db-script-demo.md
  PK Column      : ID                            ← DBF-0001
  PK Sequence    : SEQ_DEMO_NOTE                  ← db-script-demo.md Block 1
  PK Trigger     : none — PK populated by the framework from the sequence
                   at insert time (db-script-demo.md Block 6 note: no DB
                   trigger governed for this module)
  DBS-ID ref     : DBS-DEMO-01

BUSINESS CODE: NOT APPLIED — see DRV-DEMO-003 (srs-demo.md A3 "Business Code: NO").

SOFT DEACTIVATION / LIFECYCLE:
  Governed by RULE-DEMO-004 (soft delete), not the CORE Deactivation
  Policy's isActiveFl pattern — DRV-DEMO-004. Column: STATUS_ID — DBF-0004.
  Values: ACTIVE (default on INSERT) | DELETED (set by DELETE, never
  physically removed). No "reactivate" operation exists in srs-demo.md.

AUDIT COLUMNS (sourced from db-script-demo.md — AuditEntityListener fills automatically):
  CREATED_BY     : DBF-0006  String   ← filled by AuditEntityListener — NEVER set manually
  CREATED_AT     : DBF-0007  TIMESTAMP← filled by AuditEntityListener — NEVER set manually
  UPDATED_BY     : DBF-0008  String   ← filled by AuditEntityListener — NEVER set manually
  UPDATED_AT     : DBF-0009  TIMESTAMP← filled by AuditEntityListener — NEVER set manually
  ⚠ Agent: these fields MUST NOT appear in CreateNoteRequest or UpdateNoteRequest.

────────────────────────────────────────────────────────────────────────
FIELDS (DB Field Traceability Matrix binding):
────────────────────────────────────────────────────────────────────────
FIELD-ID  │ Java Property │ DB Column (exact) │ DBF-ID   │ DB Type       │ Null │ Read-Only              │ Constraint                        │ Label-AR │ Label-EN
──────────┼───────────────┼────────────────────┼──────────┼───────────────┼──────┼────────────────────────┼────────────────────────────────────┼──────────┼──────────
FIELD-0001│ noteId        │ ID                 │ DBF-0001 │ BIGINT        │ No   │ System                 │ PK — SEQ_DEMO_NOTE                 │ المعرف   │ ID
FIELD-0002│ title         │ TITLE              │ DBF-0002 │ VARCHAR(200)  │ No   │ No                     │ NOT NULL, non-blank (RULE-DEMO-001)│ العنوان  │ Title
FIELD-0003│ content       │ CONTENT            │ DBF-0003 │ TEXT          │ Yes  │ No                     │ ≤20000 chars (RULE-DEMO-002)       │ المحتوى  │ Content
FIELD-0004│ statusId      │ STATUS_ID          │ DBF-0004 │ VARCHAR(20)   │ No   │ System                 │ CHECK IN ('ACTIVE','DELETED')      │ الحالة   │ Status
FIELD-0005│ ownerUserId   │ OWNER_USER_ID      │ DBF-0005 │ BIGINT        │ No   │ System (from auth ctx) │ not a DB FK — see db-script notes  │ مالك الملاحظة │ Owner
FIELD-0006│ createdBy     │ CREATED_BY         │ DBF-0006 │ VARCHAR(255)  │ Yes  │ System                 │ AuditEntityListener                │ أنشئ بواسطة │ Created By
FIELD-0007│ createdAt     │ CREATED_AT         │ DBF-0007 │ TIMESTAMP     │ Yes  │ System                 │ AuditEntityListener                │ تاريخ الإنشاء │ Created At
FIELD-0008│ updatedBy     │ UPDATED_BY         │ DBF-0008 │ VARCHAR(255)  │ Yes  │ System                 │ AuditEntityListener                │ عُدِّل بواسطة │ Updated By
FIELD-0009│ updatedAt     │ UPDATED_AT         │ DBF-0009 │ TIMESTAMP     │ Yes  │ System                 │ AuditEntityListener                │ تاريخ التعديل │ Updated At
────────────────────────────────────────────────────────────────────────
⚠ EVERY column name above is sourced from db-script-demo.md DBF-ID lookup
  (NO-COLUMN-INVENTION RULE, Section 2A.0).

DTO MEMBERSHIP RULES:
  CreateNoteRequest : title (REQUIRED), content (OPTIONAL). Excludes:
                      noteId, statusId, ownerUserId, createdBy, createdAt,
                      updatedBy, updatedAt (all system-managed).
  UpdateNoteRequest : title (OPTIONAL — if sent, RULE-DEMO-001 applies;
                      if omitted, unchanged — DRV-DEMO-009), content
                      (OPTIONAL — same pattern, RULE-DEMO-002). Same
                      exclusions as CreateNoteRequest.
  NoteResponse      : includes ALL fields — noteId, title, content,
                      statusId, ownerUserId, createdBy, createdAt,
                      updatedBy, updatedAt.
  ⚠ Agent: map Java property → DB column via @Column(name="[EXACT_DB_COLUMN]")
    per the FIELDS table above — never invent a column name.

────────────────────────────────────────────────────────────────────────
LOV FIELDS (LOOKUP_CODE binding):
────────────────────────────────────────────────────────────────────────
FIELD-ID  │ Java Property │ DB Column │ DBF-ID   │ LOV-ID       │ LOOKUP_CODE   │ Endpoint                     │ Label-AR │ Label-EN
──────────┼───────────────┼───────────┼──────────┼──────────────┼───────────────┼──────────────────────────────┼──────────┼──────────
FIELD-0004│ statusId      │ STATUS_ID │ DBF-0004 │ LOV-DEMO-001 │ NOTE_STATUS   │ NONE — fixed values embedded directly in API contracts (see DOC phase) — no GET /api/v1/sys/lookups/NOTE_STATUS endpoint exists │ الحالة │ Status
────────────────────────────────────────────────────────────────────────
Values: ACTIVE (نشطة/Active), DELETED (محذوفة/Deleted) — see
srs-demo.md LOV-DEMO-001 and db-script-demo.md CHK_DEMO_NOTE_STATUS_ID.
Column stores the code (ACTIVE/DELETED) directly — String, not an ENUM
per project standard, and not a numeric FK to a lookup table.

────────────────────────────────────────────────────────────────────────
DOMAIN RULES (full text — extracted from srs-demo.md A4):
────────────────────────────────────────────────────────────────────────
RULE-DEMO-001 — العنوان إلزامي (Title required):
  Trigger    : عند الحفظ (Create) / عند التعديل (Update)
  Statement  : The system MUST require a non-blank title, maximum 200
               characters, before saving a note.
  Message-AR : يجب إدخال عنوان للملاحظة (200 حرف كحد أقصى).
  Message-EN : A note title is required (max 200 characters).
  Scope      : CREATE, UPDATE (when title is present in the request — DRV-DEMO-009)
  DB Enforce : CHECK constraint CHK_DEMO_NOTE_TITLE_NOT_BLANK (defense-in-depth
               only; app-level validation is authoritative)
  ERR-ID     : ERR-0001 (see Error Catalog)
  Owned by   : domain layer — Note.validateForSave() (embedded, per PHASE CORE)

RULE-DEMO-002 — حد أقصى لطول المحتوى (Content max length):
  Trigger    : عند الحفظ (Create) / عند التعديل (Update)
  Statement  : The system MUST limit content to at most 20,000 characters;
               content MAY be blank or absent.
  Message-AR : محتوى الملاحظة يتجاوز الحد المسموح (20000 حرف).
  Message-EN : Note content exceeds the allowed limit (20,000 characters).
  Scope      : CREATE, UPDATE (when content is present in the request — DRV-DEMO-009)
  DB Enforce : CHECK constraint CHK_DEMO_NOTE_CONTENT_LEN (defense-in-depth
               only; app-level validation is authoritative)
  ERR-ID     : ERR-0002 (see Error Catalog)
  Owned by   : domain layer — Note.validateForSave() (embedded, per PHASE CORE)

RULE-DEMO-003 — الوصول يقتصر على المالك (Owner-only access):
  Trigger    : عند القراءة (Read/List) / التعديل (Update) / الحذف (Delete)
  Statement  : The system MUST only allow a user to read, update, or
               delete a note whose ownerUserId equals the acting
               authenticated user's id; any other user's request for
               that note MUST be rejected.
  Message-AR : لا تملك صلاحية الوصول لهذه الملاحظة.
  Message-EN : You do not have access to this note.
  Scope      : READ (single), UPDATE, DELETE — enforced as a WHERE-clause
               filter for LIST (RULE-DEMO-003 note below)
  DB Enforce : app-level only — no DB row-level policy (domain-profile.md:
               "no row-level DB policy by default")
  ERR-ID     : ERR-0003 (see Error Catalog) — HTTP 403, DRV-DEMO-006
  Owned by   : repository/service boundary (NOT domain layer — see PHASE CORE)
  Enforcement note: for LIST (API-DEMO-002) this rule manifests as a
  mandatory ownerUserId filter in QR-DEMO-0001 (never a client-supplied
  parameter). For GET/UPDATE/DELETE by id (API-DEMO-003/004/005) it
  manifests as an explicit ownership check after FIND_ONE — a lookup that
  finds a row owned by a different user MUST be rejected the same as if
  the row did not belong to this user's result set, never merely "filtered
  from a list" (srs-demo.md RULE-DEMO-003 Test-Hint).

RULE-DEMO-004 — الحذف ناعم (Soft delete):
  Trigger    : عند الحذف (Delete)
  Statement  : The system MUST perform delete as a soft delete: set
               statusId = DELETED rather than physically removing the
               row. Notes with statusId = DELETED MUST be excluded from
               the default list and from get-by-id retrieval.
  Message-AR : تم حذف الملاحظة. (success confirmation — NOT an error;
               no ERR-ID owns this text, see Error Catalog note)
  Message-EN : Note deleted.
  Scope      : DELETE
  DB Enforce : app-level UPDATE statusId=DELETED (QR-DEMO-0005); no DB
               trigger (db-script-demo.md Block 6)
  ERR-ID     : — (this rule's own text is a SUCCESS message; the
               resulting "not found" behavior for a deleted note is
               ERR-0004, platform-standard — DRV-DEMO-005)
  Owned by   : domain layer — Note.markDeleted() (embedded, per PHASE CORE)

RULE-DEMO-005 — لا تعديل على ملاحظة محذوفة (No update on a deleted note):
  Trigger    : عند التعديل (Update)
  Statement  : The system MUST reject an update attempt on a note whose
               statusId = DELETED.
  Message-AR : لا يمكن تعديل ملاحظة محذوفة.
  Message-EN : A deleted note cannot be updated.
  Scope      : UPDATE
  DB Enforce : app-level only
  ERR-ID     : ERR-0005 (see Error Catalog) — HTTP 409, DRV-DEMO-007
  Owned by   : domain layer — Note.assertNotDeleted() (embedded, per PHASE CORE)

────────────────────────────────────────────────────────────────────────
STATE MACHINE: N/A — srs-demo.md A6 explicitly omits a formal lifecycle
diagram (≤2 states threshold not met). The single ACTIVE→DELETED
transition is fully specified above (RULE-DEMO-004) and in API-DEMO-005
below — no separate diagram is generated here either, consistent with
the upstream decision.

────────────────────────────────────────────────────────────────────────
CROSS-MODULE DEPENDENCIES: None — srs-demo.md A7 and db-script-demo.md
Section 2 (XM Register) both confirm no HARD-FK or SOFT-READ dependency
for ENTITY-DEMO-001.

REPOSITORY OPERATIONS REQUIRED:
  → QR-DEMO-0001 : FIND_BY_CRITERIA (list, owner+ACTIVE only)
  → QR-DEMO-0002 : FIND_ONE by PK (owner-checked)
  → QR-DEMO-0003 : SAVE (create)
  → QR-DEMO-0004 : UPDATE (title/content)
  → QR-DEMO-0005 : UPDATE (soft delete — statusId=DELETED)
  → QRC entries generated in Section 11.
────────────────────────────────────────────────────────────────────────
<!-- PHASE:DATA-DOM:END -->

---

<!-- PHASE:SVC-API:START -->
## PHASE SVC+API — Service & API Contract Specifications

<!-- API:API-DEMO-001:START -->
### API-DEMO-001 — Create Note
─────────────────────────────────────────────────────────────────
Endpoint         : POST /api/v1/demo/notes
Controller       : DemoNoteController → method: createNote
Service          : DemoNoteService → method: createNote
─────────────────────────────────────────────────────────────────
REQUEST:
  Content-Type   : application/json
  Request Body   : CreateNoteRequest
    Fields:
      title      : String   REQUIRED   max 200 chars, non-blank
      content    : String   OPTIONAL   max 20,000 chars
    Excluded fields: noteId, statusId, ownerUserId, createdBy, createdAt,
                     updatedBy, updatedAt — all system-managed.

RESPONSE:
  Success code   : 201
  Response DTO   : NoteResponse
    Fields: noteId (Long), title (String), content (String, nullable),
      statusId (String — "ACTIVE" on create), ownerUserId (Long),
      createdBy, createdAt, updatedBy, updatedAt.
  Paginated      : NO

VALIDATIONS:
  1. RULE-DEMO-001 — Title required:
       Statement  : The system MUST require a non-blank title, maximum
                    200 characters, before saving a note.
       Trigger    : عند الحفظ (Create)
       Message-AR : يجب إدخال عنوان للملاحظة (200 حرف كحد أقصى).
       Message-EN : A note title is required (max 200 characters).
  2. RULE-DEMO-002 — Content max length:
       Statement  : The system MUST limit content to at most 20,000
                    characters; content MAY be blank or absent.
       Trigger    : عند الحفظ (Create)
       Message-AR : محتوى الملاحظة يتجاوز الحد المسموح (20000 حرف).
       Message-EN : Note content exceeds the allowed limit (20,000 characters).

ERRORS:
  ERR-0001 → RULE-DEMO-001 triggered → HTTP 400 (see SECTION A Error Catalog for message text)
  ERR-0002 → RULE-DEMO-002 triggered → HTTP 400 (see SECTION A Error Catalog for message text)

SERVICE ORCHESTRATION:
  1. [validate] — RULE-DEMO-001, RULE-DEMO-002 evaluated against the request body
  2. [derive]   — ownerUserId set from the authenticated session (never from request body)
  3. [persist]  — new DEMO_NOTE row inserted, statusId defaulted to ACTIVE,
                  PK from SEQ_DEMO_NOTE, audit fields via AuditEntityListener
  Note: No business logic in controller.

REPOSITORY OPERATION:
  QR-ID      : QR-DEMO-0003 — see Section 11
  Table      : DEMO_NOTE
  Operation  : SAVE
  Join       : NONE
  Transaction: READ_WRITE
  Fetch strategy: N/A (insert)
  Bulk operation: NO
  Sequence   : SEQ_DEMO_NOTE

SECURITY:
  Screen     : SCR-DEMO-001 — ملاحظاتي (My Notes)
  Permission : CREATE
  ⚠ Agent: enforce via permission check before processing request.

LOCALIZATION:
  Error responses: messageAr AND messageEn (exact texts above).
─────────────────────────────────────────────────────────────────
<!-- API:API-DEMO-001:END -->

<!-- API:API-DEMO-002:START -->
### API-DEMO-002 — List Notes (search)
─────────────────────────────────────────────────────────────────
Endpoint         : GET /api/v1/demo/notes
Controller       : DemoNoteController → method: listNotes
Service          : DemoNoteService → method: listNotes
─────────────────────────────────────────────────────────────────
REQUEST:
  Content-Type   : N/A (GET)
  Query Params   : page (int, default 0), size (int, default per project
                   standard), sortBy/sortDir (optional — ALLOWED_SORT_FIELDS
                   only; default updatedAt DESC per PHASE CORE)
  No client-supplied filter on owner or status — both are fixed server-side
  (RULE-DEMO-003, RULE-DEMO-004).

RESPONSE:
  Success code   : 200
  Response DTO   : Page<NoteResponse>
  Paginated      : YES — JPA Page<T>, project's existing framework.

VALIDATIONS: None beyond ALLOWED_SORT_FIELDS validation (project-standard —
  no DRV-ID, see PHASE CORE / DOC phase).

ERRORS: None specific to this endpoint. Empty result → HTTP 200 with
  empty content — NEVER HTTP 404 (project-standard, PHASE DOC).

SERVICE ORCHESTRATION:
  1. [derive]  — ownerUserId from authenticated session
  2. [load]    — page of DEMO_NOTE rows WHERE owner_user_id = :ownerUserId
                 AND status_id = 'ACTIVE'
  Note: No business logic in controller.

REPOSITORY OPERATION:
  QR-ID      : QR-DEMO-0001 — see Section 11
  Table      : DEMO_NOTE
  Operation  : FIND_BY_CRITERIA
  Join       : NONE
  Transaction: READ_ONLY
  Fetch strategy: LAZY (default — no related entities to fetch)
  Bulk operation: NO

SECURITY:
  Screen     : SCR-DEMO-001
  Permission : VIEW
─────────────────────────────────────────────────────────────────
<!-- API:API-DEMO-002:END -->

<!-- API:API-DEMO-003:START -->
### API-DEMO-003 — Get Note by id
─────────────────────────────────────────────────────────────────
Endpoint         : GET /api/v1/demo/notes/{id}
Controller       : DemoNoteController → method: getNote
Service          : DemoNoteService → method: getNote
─────────────────────────────────────────────────────────────────
REQUEST:
  Path Params    : id: Long (noteId)

RESPONSE:
  Success code   : 200
  Response DTO   : NoteResponse
  Paginated      : NO

VALIDATIONS: None (read-only) — RULE-DEMO-003/004 are enforced as
  lookup-and-authorize logic below, not input validation.

ERRORS:
  ERR-0004 → note not found OR statusId = DELETED → HTTP 404 (see SECTION A Error Catalog for message text)
  ERR-0003 → row exists, ACTIVE, but ownerUserId ≠ requester → HTTP 403 (see SECTION A Error Catalog for message text)

SERVICE ORCHESTRATION:
  1. [load]     — FIND_ONE by PK, excluding statusId = DELETED (RULE-DEMO-004)
                  → not found or DELETED → ERR-0004 (404)
  2. [validate] — RULE-DEMO-003: loaded row's ownerUserId must equal the
                  authenticated user's id → mismatch → ERR-0003 (403)
  Note: the ownership check happens AFTER existence/delete-state check —
  order matches API-DEMO-004/005 below for consistency.

REPOSITORY OPERATION:
  QR-ID      : QR-DEMO-0002 — see Section 11
  Table      : DEMO_NOTE
  Operation  : FIND_ONE
  Join       : NONE
  Transaction: READ_ONLY
  Fetch strategy: LAZY
  Bulk operation: NO

SECURITY:
  Screen     : SCR-DEMO-001
  Permission : VIEW
─────────────────────────────────────────────────────────────────
<!-- API:API-DEMO-003:END -->

<!-- API:API-DEMO-004:START -->
### API-DEMO-004 — Update Note
─────────────────────────────────────────────────────────────────
Endpoint         : PUT /api/v1/demo/notes/{id}
Controller       : DemoNoteController → method: updateNote
Service          : DemoNoteService → method: updateNote
─────────────────────────────────────────────────────────────────
REQUEST:
  Content-Type   : application/json
  Path Params    : id: Long (noteId)
  Request Body   : UpdateNoteRequest
    Fields:
      title      : String   OPTIONAL — if present, RULE-DEMO-001 applies;
                   if absent, existing title is unchanged (DRV-DEMO-009)
      content    : String   OPTIONAL — if present, RULE-DEMO-002 applies;
                   if absent, existing content is unchanged (DRV-DEMO-009)
    Excluded fields: noteId, statusId, ownerUserId, createdBy, createdAt,
                     updatedBy, updatedAt — all system-managed.

RESPONSE:
  Success code   : 200
  Response DTO   : NoteResponse (updated state)
  Paginated      : NO

VALIDATIONS:
  1. RULE-DEMO-001 — Title required (only when title is present in the request body)
  2. RULE-DEMO-002 — Content max length (only when content is present in the request body)
  3. RULE-DEMO-003 — Owner-only access
  4. RULE-DEMO-005 — No update on a deleted note

ERRORS (see SECTION A Error Catalog for message text):
  ERR-0004 → note not found → HTTP 404
  ERR-0003 → not the owner → HTTP 403
  ERR-0005 → RULE-DEMO-005 (row exists, owned, but statusId = DELETED) → HTTP 409
  ERR-0001 → RULE-DEMO-001 triggered (title sent, invalid) → HTTP 400
  ERR-0002 → RULE-DEMO-002 triggered (content sent, invalid) → HTTP 400

SERVICE ORCHESTRATION:
  1. [load]     — FIND_ONE by PK → not found → ERR-0004 (404)
  2. [validate] — RULE-DEMO-003 ownership → mismatch → ERR-0003 (403)
  3. [validate] — RULE-DEMO-005: loaded row's statusId = DELETED → ERR-0005 (409)
  4. [validate] — RULE-DEMO-001 (if title present), RULE-DEMO-002 (if content present)
  5. [persist]  — UPDATE title/content as present; updatedBy/updatedAt via
                  AuditEntityListener

REPOSITORY OPERATION:
  QR-ID      : QR-DEMO-0002 (load) then QR-DEMO-0004 (update) — see Section 11
  Table      : DEMO_NOTE
  Operation  : FIND_ONE then UPDATE
  Join       : NONE
  Transaction: READ_WRITE
  Fetch strategy: LAZY
  Bulk operation: NO

SECURITY:
  Screen     : SCR-DEMO-001
  Permission : UPDATE
─────────────────────────────────────────────────────────────────
<!-- API:API-DEMO-004:END -->

<!-- API:API-DEMO-005:START -->
### API-DEMO-005 — Delete Note (soft)
─────────────────────────────────────────────────────────────────
Endpoint         : DELETE /api/v1/demo/notes/{id}
Controller       : DemoNoteController → method: deleteNote
Service          : DemoNoteService → method: deleteNote
─────────────────────────────────────────────────────────────────
REQUEST:
  Path Params    : id: Long (noteId)

RESPONSE:
  Success code   : 200
  Response DTO   : NoteResponse (statusId = "DELETED") — serves as the
                   confirmation srs-demo.md B5 API-DEMO-005 requires
                   ("تأكيد").
  Paginated      : NO

VALIDATIONS:
  1. RULE-DEMO-003 — Owner-only access
  Note: RULE-DEMO-004 (soft delete) is NOT listed here — it is the
  operation itself (see SERVICE ORCHESTRATION step 3), not a rejection
  check, so it carries no ERR-ID and is deliberately excluded from
  VALIDATIONS (RULE-ERR-CARRY applies only to rejection-triggering rules).

ERRORS (see SECTION A Error Catalog for message text):
  ERR-0004 → note not found or already DELETED → HTTP 404 (deleting an
             already-deleted note is indistinguishable from deleting a
             nonexistent one, per RULE-DEMO-004's exclusion rule)
  ERR-0003 → not the owner → HTTP 403

SERVICE ORCHESTRATION:
  1. [load]     — FIND_ONE by PK, excluding statusId = DELETED → not
                  found/already deleted → ERR-0004 (404)
  2. [validate] — RULE-DEMO-003 ownership → mismatch → ERR-0003 (403)
  3. [persist]  — UPDATE statusId = 'DELETED'; updatedBy/updatedAt via
                  AuditEntityListener (RULE-DEMO-004 — soft delete, no
                  physical row removal)

REPOSITORY OPERATION:
  QR-ID      : QR-DEMO-0002 (load) then QR-DEMO-0005 (soft delete) — see Section 11
  Table      : DEMO_NOTE
  Operation  : FIND_ONE then UPDATE
  Join       : NONE
  Transaction: READ_WRITE
  Fetch strategy: LAZY
  Bulk operation: NO

SECURITY:
  Screen     : SCR-DEMO-001
  Permission : DELETE
─────────────────────────────────────────────────────────────────
<!-- API:API-DEMO-005:END -->

**API Governance Rules applied:** BC-B2-RULE-1/2/3 are N/A (no Business
Code on this entity — DRV-DEMO-003). LOC-B2-RULE-1/2 applied (every
ERR-ID's messageAr + messageEn is defined once, canonically, in SECTION A
Error Catalog — every API block above references it by ERR-ID + HTTP
status only, never reproducing the text, per the Error Catalog Canonical
Location Rule, Option A). SEC-B2-RULE-1 applied (every controller method
has a declared Permission). RULE-ERR-CARRY verified: every RULE-ID
appearing in a Validations list has a matching ERR-ID in that API's
Errors field — RULE-DEMO-004 is deliberately excluded from API-DEMO-005's
Validations list (see that block's note) because it is the operation
itself, not a rejection check, so RULE-ERR-CARRY does not apply to it.
RULE-PLATFORM-ERR applied to ERR-0004 (RULE-ID = PLATFORM-STD, DRV-DEMO-005).
RULE-REPO-DRV: no deviation from defaults (READ_ONLY reads, LAZY fetch,
NONE join) anywhere in this plan — no additional DRV-ID required beyond
DRV-DEMO-001..009 already logged.
<!-- PHASE:SVC-API:END -->

---

<!-- PHASE:DOC:START -->
## PHASE DOC — Contract Stabilization

### DOC-1: API Contract Summary
─────────────────────────────────────────────────────────────────
API-ID       │ Endpoint                     │ Method │ Request DTO        │ Response DTO  │ Stability
─────────────┼───────────────────────────────┼────────┼─────────────────────┼───────────────┼──────────
API-DEMO-001 │ /api/v1/demo/notes            │ POST   │ CreateNoteRequest   │ NoteResponse  │ STABLE
API-DEMO-002 │ /api/v1/demo/notes            │ GET    │ page, size, sortBy, sortDir │ Page<NoteResponse> │ STABLE
API-DEMO-003 │ /api/v1/demo/notes/{id}       │ GET    │ — (path param only) │ NoteResponse  │ STABLE
API-DEMO-004 │ /api/v1/demo/notes/{id}       │ PUT    │ UpdateNoteRequest   │ NoteResponse  │ STABLE
API-DEMO-005 │ /api/v1/demo/notes/{id}       │ DELETE │ — (path param only) │ NoteResponse  │ STABLE
─────────────────────────────────────────────────────────────────
Unstable APIs: None.
Frontend-governed contracts: None.

### DOC-2: DTO Typing Rules (constraints — DTOs fully defined in PHASE SVC+API)
LOV field typing (statusId): String (stores the fixed code ACTIVE/DELETED
  directly — never an ENUM, per project standard).
Business Code: N/A on this entity — never appears in any DTO.

### DOC-3: Pagination & Filter Standards (project-standard — see PHASE CORE)
Backend strategy : JPA Page<T> — used directly, no custom wrapper.
Request contract : NoteSearchRequest extends BaseSearchContractRequest →
                    page (0-based), size, sortBy, sortDir.
                    ALLOWED_SORT_FIELDS = { updatedAt, createdAt, title }.
Empty result rule : HTTP 200 with empty content — NEVER HTTP 404.
Filter types      : None client-supplied for this module (owner + ACTIVE
                    status are server-fixed, not filters — see API-DEMO-002).

**DOC GATE CHECK (auto-evaluated):**
[ ✓ ] All API-IDs from SVC+API appear in API Contract Summary
[ ✓ ] Error Catalog complete with Arabic + English messages
[ ✓ ] All APIs marked STABLE
[ ✓ ] Pagination standard declared
DOC Gate: PASSED ✓

**v2.0 STATUS NOTE (CONTRACT-12):** DOC-1 above is an internal,
backend-only self-consistency artifact. It does NOT gate P3.2 — that
gate is GATE: BACKEND MODULE COMPLETE (real, post-implementation API
Docs + human-approved P2.5 outputs), evaluated independently and out of
scope for this factory pass.
<!-- PHASE:DOC:END -->

---

<!-- PHASE:INT-C:START -->
## PHASE INT-C — Integration Contract Specifications

None — db-script-demo.md's XM Register (Section 2) is empty: DEMO has no
HARD-FK or SOFT-READ dependency on any other module (srs-demo.md A7
confirms the same; this platform currently has no other module). No
XM-ID exists to contract, and none is invented here (P3 never assigns
XM-IDs).

**INT-C GATE CHECK (auto-evaluated):**
[ ✓ ] All XM-IDs from DB Script XM Register accounted for (0 of 0)
[ ✓ ] N/A — no XM-ID to classify
[ ✓ ] N/A — no DEFERRED item
[ ✓ ] No new XM-IDs invented
[ ✓ ] N/A — no OPEN RXE targets this module
[ ✓ ] N/A — no inbound XM stub; DEMO is not currently a source for any
      other module (this platform has only one module so far)
INT-C Gate: PASSED ✓ (vacuously — no cross-module dependency exists)
<!-- PHASE:INT-C:END -->

---

<!-- PHASE:INT-R:START -->
## PHASE INT-R — Runtime Activation Status

None — no XM-ID exists for this module (see PHASE INT-C). No runtime
activation table is applicable.
<!-- PHASE:INT-R:END -->

---

<!-- PHASE:SEC-BE:START -->
## PHASE SEC-BE — Backend Security Specifications

### SEC-BE — SCR-DEMO-001 — ملاحظاتي (My Notes)
─────────────────────────────────────────────────────────────────
API-level enforcement:
  Every API-ID serving this screen (API-DEMO-001..005) requires
  permission verification before the request is processed — see the
  SECURITY block in each API contract in PHASE SVC+API. The substantive
  gate is record-level ownership (RULE-DEMO-003), not a role check — see
  DRV-DEMO-008.

EXCEPTION module scope: N/A — no EXCEPTION module referenced.
─────────────────────────────────────────────────────────────────

SECURITY SEED DATA REQUIREMENTS:
  Screen registration (table: SEC_PAGES, standard naming — column names
  per db-script-demo.md convention once Security itself goes through P2):
    page_code  : DEMO_NOTES
    page_name  : ملاحظاتي (My Notes) / My Notes
    parent_id_fk: DEMO_ROOT (per srs-demo.md B4 Security Seed Data note)
  Permission rows (table: PERMISSIONS):
    ────────────────────────────────────────────────────────
    Permission Name              │ Roles Assigned
    ─────────────────────────────┼──────────────────────────
    PERM_DEMO_NOTES_VIEW         │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    PERM_DEMO_NOTES_CREATE       │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    PERM_DEMO_NOTES_UPDATE       │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    PERM_DEMO_NOTES_DELETE       │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    ────────────────────────────────────────────────────────
  Note (DRV-DEMO-008): this domain has no role matrix (domain-profile.md
  — "owner-based access, not role-based"). Every authenticated user holds
  all 4 permission rows; the actual authorization boundary per request is
  RULE-DEMO-003 (record-level ownership), enforced in PHASE SVC+API — the
  permission rows above gate "is this feature reachable at all by an
  authenticated user," not "which user's records."

SEC-BE Governance Rules:
  SEC-IMPL-RULE-1 — SCR-DEMO-001 has permission verification enforced at
                    the API level (no exceptions) — see PHASE SVC+API.
  SEC-IMPL-RULE-3 — HTTP 403 responses mapped via LocalizedException,
                    carrying ERR-0003.
  SEC-IMPL-RULE-4 — SCR-DEMO-001 verified in SEC_PAGES before launch.

Note: UI-level show/hide, navigation guards (SEC-FE) belong to Project
3.2 (frontend pass, out of scope for this backend-only plan) — consumes
the SAME PERMISSIONS seed data declared above.
<!-- PHASE:SEC-BE:END -->

---

<!-- PHASE:ALIGN-BE:START -->
## ALIGN-BE GATE — DEMO — PLAN-ID: PLAN-DEMO-001
═══════════════════════════════════════════════════════════════════════════

TRACEABILITY CHECKS                                        │ Status
───────────────────────────────────────────────────────────┼──────────────
All FIELD-IDs used in phases appear in Plan Index          │ ✓
All API-IDs used in phases appear in Plan Index            │ ✓
All RULE-IDs used in phases appear in Plan Index           │ ✓
All ERR-IDs used in Error Catalog appear correctly         │ ✓
All QR-IDs in QRC appear in Plan Index QRC Summary         │ ✓
Derivation Log complete — no undocumented inferences       │ ✓ (DRV-DEMO-001..009)
DB Structural Alignment confirms field coverage            │ ✓ (see DB Alignment Manifest)
───────────────────────────────────────────────────────────┼──────────────
BUSINESS CODE CHECKS (backend half)                        │ Status
───────────────────────────────────────────────────────────┼──────────────
Business Code excluded from POST/PUT request bodies        │ ✓ N/A — no Business Code on this entity (DRV-DEMO-003)
Business Code always present in GET/response DTOs          │ ✓ N/A — same reason
───────────────────────────────────────────────────────────┼──────────────
LOCALIZATION CHECKS (backend half)                         │ Status
───────────────────────────────────────────────────────────┼──────────────
All RULE-IDs have Message-AR defined                       │ ✓
All API error responses: messageAr + messageEn             │ ✓
───────────────────────────────────────────────────────────┼──────────────
SECURITY CHECKS (backend half)                              │ Status
───────────────────────────────────────────────────────────┼──────────────
Every API-ID serving a screen has permission declared      │ ✓
Every SCR-ID has SEC-BE block                               │ ✓
───────────────────────────────────────────────────────────┼──────────────
QUERY REFERENCE CATALOG CHECKS                              │ Status
───────────────────────────────────────────────────────────┼──────────────
Every API-ID with DB operation has QR-ID in QRC              │ ✓
Every QR-ID has agent-reference warning label                 │ ✓
No QR entry references ENUM for LOV fields                    │ ✓
No QR entry joins to lookups table                             │ ✓
Every QR-ID states exact sequence name (not placeholder)      │ ✓
───────────────────────────────────────────────────────────┼──────────────
CROSS-MODULE DEPENDENCY CHECKS                               │ Status
───────────────────────────────────────────────────────────┼──────────────
All DEFERRED items (⏸) have XM-DEMO-[N] + workarounds        │ ✓ N/A — none exist
All OQ references point to valid OQ-IDs in OQ Log             │ ✓ N/A — no OQ raised
Inbound XM stubs use INBOUND-STUB notation (not TODO)         │ ✓ N/A — no inbound stub
───────────────────────────────────────────────────────────┼──────────────
ARTIFACT BINDING CHECKS (Section 2A compliance)               │ Status
───────────────────────────────────────────────────────────┼──────────────
No placeholder [TABLE_NAME] in any phase                      │ ✓
No placeholder [LOOKUP_CODE] in any phase                     │ ✓
No placeholder [SEQ_NAME] — all sequences are exact            │ ✓
No RULE block shows "see SRS" — all text is inline             │ ✓
Every LOV-ID has exact LOOKUP_CODE bound from SRS               │ ✓
Every sequence name matches SEQ_[TABLE] from db-script          │ ✓
Every column name traces to a DBF-ID in DB Traceability        │ ✓
Every Message-AR is exact text — not paraphrase or summary     │ ✓
Business Code format stated explicitly (not "auto-gen")        │ ✓ N/A — not applied
DB Alignment Manifest: 5 columns only — no Column Name, DB Type,│ ✓
  or SRS Source (CONTRACT-1 compliance)                        │
───────────────────────────────────────────────────────────┼──────────────
PLAN COMPLETENESS CHECKS (backend)                            │ Status
───────────────────────────────────────────────────────────┼──────────────
Canonical architecture declared in PHASE CORE                  │ ✓
Domain behavior placement declared in PHASE CORE               │ ✓
Entity inheritance declared per module type                    │ ✓
No orgUnitId in any DTO described in the plan                  │ ✓
No audit fields in any CreateRequest/UpdateRequest              │ ✓
Error signaling strategy declared (LocalizedException)          │ ✓
All ERR-IDs have 4-registration points declared                │ ✓ (see PHASE CORE "Error catalog: every ERR-ID registered in 4 places")
All search operations declare ALLOWED_SORT_FIELDS               │ ✓
Empty search result → HTTP 200 declared (not HTTP 404)          │ ✓
Pre-deactivation usage check declared per deactivate op          │ ✓ N/A — this module has no deactivate-with-usage-check op (DELETE is unconditional soft delete, not a "canDelete" usage check per srs-demo.md — no other entity references a Note)
Inbound XM stubs use INBOUND-STUB notation (not TODO)            │ ✓ N/A
═══════════════════════════════════════════════════════════════════════════
ALIGN-BE GATE RESULT: PASSED ✓
Auto-correction applied: None
═══════════════════════════════════════════════════════════════════════════

**Table 1 — Entity & Field Coverage:**
```
ENTITY-ID / FIELD-ID │ DATA+DOM │ SVC+API │ QR-ID        │ XM-ID │ Status
─────────────────────┼──────────┼─────────┼──────────────┼───────┼───────
ENTITY-DEMO-001      │ ✓        │ ✓       │ QR-DEMO-0001..0005 │ —  │ ✓
FIELD-0001..0009     │ ✓        │ ✓       │ —            │ —     │ ✓
```

**Table 2 — Validations Coverage:**
```
RULE-ID        │ SVC+API │ ERR-ID   │ Status
────────────────┼─────────┼──────────┼───────
RULE-DEMO-001  │ ✓       │ ERR-0001 │ ✓
RULE-DEMO-002  │ ✓       │ ERR-0002 │ ✓
RULE-DEMO-003  │ ✓       │ ERR-0003 │ ✓
RULE-DEMO-004  │ ✓       │ — (success message, not an error) │ ✓
RULE-DEMO-005  │ ✓       │ ERR-0005 │ ✓
```

**Table 3 — XM Dependency Gate:** N/A — no XM-ID exists for this module.
<!-- PHASE:ALIGN-BE:END -->

---

## SECTION A — ERROR CATALOG (CANONICAL)
══════════════════════════════════════════════════════════════════════════════════
ERR-ID   │ RULE-ID       │ API-ID(s)                    │ HTTP │ Trigger                          │ Message-AR                        │ Message-EN
─────────┼────────────────┼───────────────────────────────┼──────┼───────────────────────────────────┼────────────────────────────────────┼─────────────────────────────────────
ERR-0001 │ RULE-DEMO-001 │ API-DEMO-001, API-DEMO-004   │ 400  │ title missing/blank or >200 chars │ يجب إدخال عنوان للملاحظة (200 حرف كحد أقصى). │ A note title is required (max 200 characters).
ERR-0002 │ RULE-DEMO-002 │ API-DEMO-001, API-DEMO-004   │ 400  │ content >20,000 chars              │ محتوى الملاحظة يتجاوز الحد المسموح (20000 حرف). │ Note content exceeds the allowed limit (20,000 characters).
ERR-0003 │ RULE-DEMO-003 │ API-DEMO-003, API-DEMO-004, API-DEMO-005 │ 403 │ requester is not the note's owner │ لا تملك صلاحية الوصول لهذه الملاحظة. │ You do not have access to this note.
ERR-0004 │ PLATFORM-STD (DRV-DEMO-005) │ API-DEMO-003, API-DEMO-004, API-DEMO-005 │ 404 │ note does not exist or statusId = DELETED │ الملاحظة غير موجودة. │ Note not found.
ERR-0005 │ RULE-DEMO-005 │ API-DEMO-004                  │ 409  │ update attempted on a DELETED note │ لا يمكن تعديل ملاحظة محذوفة.        │ A deleted note cannot be updated.
══════════════════════════════════════════════════════════════════════════════════
Total Errors: 5

Registration (project-standard, 4 points — PHASE CORE): every ERR-ID
above is registered in ErrorCodes (constants), messages.properties
(Message-EN), the i18n JSON (Message-AR), and ErpErrorMapperService
(HTTP status mapping).

Error Catalog canonical location: THIS SECTION (Option A per
PROJECT-3-BACKEND-ENGINE.md §Section 10) — PHASE SVC+API references it
by ERR-ID only, no duplicate table.

---

## SECTION 11 — QUERY REFERENCE CATALOG (FULL — AGENT REFERENCE)
```
╔══════════════════════════════════════════════════════════════════╗
║        QUERY REFERENCE CATALOG — DEMO — PLAN-ID: PLAN-DEMO-001   ║
╠══════════════════════════════════════════════════════════════════╣
║  ⚠ AGENT REFERENCE ONLY — ALL ENTRIES MUST BE REWRITTEN         ║
║  Use actual JPA entity class names, mapped field property names, ║
║  the project's query strategy (JPQL/Criteria/QueryDSL), and its  ║
║  pagination framework. Never copy-paste these entries.           ║
╚══════════════════════════════════════════════════════════════════╝
```

QR-DEMO-0001 — List active notes for owner
──────────────────────────────────────────────────────────────────
Phase        : SVC+API
API-ID       : API-DEMO-002
Entity       : ENTITY-DEMO-001
Operation    : FIND_BY_CRITERIA
──────────────────────────────────────────────────────────────────
Intent: return a page of the requesting user's own ACTIVE notes,
  most-recently-updated first.
Logical Specification (pseudo-SQL — agent reference only):
  SELECT *
  FROM   DEMO_NOTE
  WHERE  OWNER_USER_ID = :ownerUserId
  AND    STATUS_ID = 'ACTIVE'
  ORDER  BY UPDATED_AT DESC
  LIMIT/OFFSET (or Pageable equivalent)
Join Justification  : NONE required
Transaction         : READ_ONLY
Pagination          : YES — page + size params
Filter fields       : none client-supplied (owner + status fixed server-side)
Result shape        : full entity (mapped to NoteResponse)
Null handling       : N/A
──────────────────────────────────────────────────────────────────
⚠ Agent: rewrite using actual entity class/field names.
──────────────────────────────────────────────────────────────────

QR-DEMO-0002 — Find one note by id (pre-authorization load)
──────────────────────────────────────────────────────────────────
Phase        : SVC+API
API-ID       : API-DEMO-003, API-DEMO-004, API-DEMO-005
Entity       : ENTITY-DEMO-001
Operation    : FIND_ONE
──────────────────────────────────────────────────────────────────
Intent: load one note by PK, excluding soft-deleted rows, before the
  caller applies the RULE-DEMO-003 ownership check.
Logical Specification (pseudo-SQL — agent reference only):
  SELECT *
  FROM   DEMO_NOTE
  WHERE  ID = :noteId
  AND    STATUS_ID != 'DELETED'
Join Justification  : NONE required
Transaction         : READ_ONLY
Pagination          : NO
Filter fields       : id (EXACT)
Result shape        : full entity or throw LocalizedException(NOT_FOUND, ErrorCodes.DEMO_NOTE_NOT_FOUND) → ERR-0004
Null handling       : absent/DELETED row → ERR-0004
──────────────────────────────────────────────────────────────────
⚠ Agent: rewrite using actual entity class/field names. The ownership
  check (RULE-DEMO-003 → ERR-0003) happens in the calling service method
  AFTER this query returns a row — not inside this query.
──────────────────────────────────────────────────────────────────

QR-DEMO-0003 — Save (create) a note
──────────────────────────────────────────────────────────────────
Phase        : SVC+API
API-ID       : API-DEMO-001
Entity       : ENTITY-DEMO-001
Operation    : SAVE
──────────────────────────────────────────────────────────────────
Intent: insert a new note owned by the authenticated user.
Logical Specification (pseudo-SQL — agent reference only):
  INSERT INTO DEMO_NOTE (ID, TITLE, CONTENT, STATUS_ID, OWNER_USER_ID,
    CREATED_BY, CREATED_AT, UPDATED_BY, UPDATED_AT)
  VALUES (SEQ_DEMO_NOTE.NEXTVAL, :title, :content, 'ACTIVE',
    :ownerUserId, :auditUser, :now, :auditUser, :now)
Join Justification  : NONE required
Transaction         : READ_WRITE
Pagination          : NO
Result shape        : full entity (mapped to NoteResponse)
──────────────────────────────────────────────────────────────────
⚠ Agent: PK generation and audit fields are handled by the framework
  (@SequenceGenerator(sequenceName = "SEQ_DEMO_NOTE") + AuditEntityListener)
  — do not set them manually in code that mirrors this pseudo-SQL.
──────────────────────────────────────────────────────────────────

QR-DEMO-0004 — Update a note's title/content
──────────────────────────────────────────────────────────────────
Phase        : SVC+API
API-ID       : API-DEMO-004
Entity       : ENTITY-DEMO-001
Operation    : UPDATE
──────────────────────────────────────────────────────────────────
Intent: apply title and/or content changes to an already-loaded,
  already-authorized, non-deleted note (see QR-DEMO-0002).
Logical Specification (pseudo-SQL — agent reference only):
  UPDATE DEMO_NOTE
  SET    TITLE = COALESCE(:title, TITLE),
         CONTENT = COALESCE(:content, CONTENT),
         UPDATED_BY = :auditUser, UPDATED_AT = :now
  WHERE  ID = :noteId
Join Justification  : NONE required
Transaction         : READ_WRITE
Pagination          : NO
Result shape        : full entity (mapped to NoteResponse)
──────────────────────────────────────────────────────────────────
⚠ Agent: the COALESCE pattern above expresses DRV-DEMO-009's
  "optional-if-unchanged" semantics — rewrite with the project's actual
  partial-update idiom (e.g. only setting fields present on the mapped
  entity before save, not a raw SQL COALESCE).
──────────────────────────────────────────────────────────────────

QR-DEMO-0005 — Soft delete a note
──────────────────────────────────────────────────────────────────
Phase        : SVC+API
API-ID       : API-DEMO-005
Entity       : ENTITY-DEMO-001
Operation    : UPDATE
──────────────────────────────────────────────────────────────────
Intent: mark an already-loaded, already-authorized note as DELETED
  (RULE-DEMO-004) — never a physical row removal.
Logical Specification (pseudo-SQL — agent reference only):
  UPDATE DEMO_NOTE
  SET    STATUS_ID = 'DELETED', UPDATED_BY = :auditUser, UPDATED_AT = :now
  WHERE  ID = :noteId
Join Justification  : NONE required
Transaction         : READ_WRITE
Pagination          : NO
Result shape        : full entity (mapped to NoteResponse, statusId = "DELETED")
──────────────────────────────────────────────────────────────────
⚠ Agent: rewrite using actual entity class/field names. No hard DELETE
  statement is ever issued for this entity.
──────────────────────────────────────────────────────────────────

---

## SECTION 12 — REGISTRY UPDATE SCHEMA

See `registry-exec-be-demo.md` (companion file, same commit) for the
inline REGISTRY step output (AMEND-PIPELINE-V5 §1D.4).

---

## SECTION 13 — PASS 1 COMPLETION BLOCK
```
╔══════════════════════════════════════════════════════════════════╗
║           BACKEND EXECUTION PLAN — PASS 1 COMPLETE ✓              ║
╠═══════════════════════╦══════════════════════════════════════════╣
║ Plan Name             ║ New Feature — My Notes — Personal Notes (DEMO) — BE ║
║ Plan ID               ║ PLAN-DEMO-001                            ║
║ Output                ║ backend-execution-plan-demo.md — Agent-Ready ║
║ Phases Complete       ║ CORE✓ DATA+DOM✓ SVC+API✓ DOC✓ INT-C✓    ║
║                       ║ INT-R✓ SEC-BE✓ ALIGN-BE✓                ║
║ Open Questions        ║ None                                     ║
║ XM DEFERRED           ║ None — no cross-module dependency        ║
║ Blocked Elements      ║ None                                     ║
║ QR-IDs Generated      ║ 5 — see Section 11                       ║
║ Next Stage            ║ review(P3.1) → P3.5 (backend test plan)  ║
║                       ║ → holistic review → split → deliver       ║
╠═══════════════════════╩══════════════════════════════════════════╣
║  ⚠ AGENT INSTRUCTIONS                                            ║
║  This plan is ready for implementation by an agent.               ║
║  Agent MUST:                                                      ║
║    1. Read the full plan before writing any code                 ║
║    2. Rewrite ALL Query Reference Catalog entries from scratch    ║
║    3. Follow the architectural policies declared in PHASE CORE   ║
║    4. Apply all Business Rules declared in PHASE DATA+DOM         ║
║    5. Never copy-paste QRC entries — treat as logic reference     ║
║    6. Implement security checks per PHASE SEC-BE                  ║
║    7. After implementation, run api-doc-generator — required      ║
║       before PASS 2 (frontend) can start                          ║
║  Tests are NOT part of this plan (P3 light). backend-test-plan-   ║
║  demo.md is produced separately (P3.5, same factory pass).        ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## SECTION 15 — AGENT HANDOFF SUMMARY (BACKEND)

### 15.1 What the Agent Receives
```
✓ backend-execution-plan-demo.md — this file
✓ srs-demo.md — functional requirements
✓ db-script-demo.md — database DDL (actual table/column names)
✓ OQ Log (srs-demo.md) — none open
```

### 15.2 Agent Reading Order
1. PLAN INDEX — full scope (1 entity, 5 APIs, 5 rules, 0 XM-IDs)
2. DB ALIGNMENT MANIFEST — FIELD-ID → DBF-ID mapping
3. PHASE CORE — architectural patterns, domain behavior placement, DRV log
4. PHASE DATA+DOM — entity structure and domain rules
5. PHASE SVC+API — API contracts and orchestration
6. PHASE SEC-BE — security and permission requirements
7. SECTION 11 QUERY REFERENCE CATALOG — query intent per operation
8. SECTION A ERROR CATALOG — use ERR-IDs in all error handling code
9. AFTER implementation: run api-doc-generator for real API Docs (PASS 2 gate)

### 15.3 Implementation Rules — Quick Reference
```
QRC — NEVER copy-paste QRC entries as production code.
DEFERRED XM — N/A, no XM-ID exists for this module.
OPEN QUESTIONS — N/A, none open.
```

### 15.4 Backend Plan Completeness Self-Check
```
[✓] PHASE CORE: canonical architecture declared
[✓] PHASE CORE: domain behavior placement declared
[✓] PHASE CORE: entity inheritance declared
[✓] PHASE CORE: error signaling strategy declared
[✓] PHASE CORE: transaction scope declared
[✓] ENTITY-DEMO-001 has complete field table with DBF-ID bindings
[✓] Every RULE-ID has full text + "Owned by" declared
[✓] Every API-ID: Errors field covers all RULE-IDs in Validations
[✓] ERR-0004 (platform-standard): RULE-ID = PLATFORM-STD + DRV-DEMO-005
[✓] No repository deviation from defaults — no additional DRV-ID needed
[✓] No orgUnitId in any DTO shape described
[✓] No audit fields in any CreateNoteRequest/UpdateNoteRequest shape
[✓] All ERR-IDs registered in 4 places declared
[✓] All inbound XM references: N/A, none exist
[✓] Derivation Log entries present for every non-obvious inference (DRV-DEMO-001..009)
[✓] ALIGN-BE gate passed ✓
[✓] Every phase has exactly one PHASE:{key}:START/END, key is one of the
    eight canonical keys (Section 8.0)
[✓] Every API-ID has exactly one dedicated marker pair
```

══════════════════════════════════════════════════════════════════
*End of backend-execution-plan-demo.md*
*Governed by: Execution Plan Governance Engine (Project 3.1)*
*PLAN-ID: PLAN-DEMO-001 | DBS-ID: DBS-DEMO-01*
*Next: review(P3.1) → P3.5 (backend-test-plan-demo.md, same factory pass)*
══════════════════════════════════════════════════════════════════
