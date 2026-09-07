<!-- Source: PHASE:CORE -->

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
