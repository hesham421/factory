<!-- Source: PHASE:SVC-API -->

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
