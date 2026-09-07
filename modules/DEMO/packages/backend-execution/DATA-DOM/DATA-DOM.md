<!-- Source: PHASE:DATA-DOM -->

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
