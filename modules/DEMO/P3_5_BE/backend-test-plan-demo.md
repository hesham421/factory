backend-test-plan-demo.md — DEMO — PLAN-ID: PLAN-DEMO-001
══════════════════════════════════════════════════════════════════
Source artifacts:
  backend-execution-plan-demo.md : PLAN-DEMO-001 — Gate ALIGN-BE ✓ confirmed (8747295)
  srs-demo.md                    : DEMO SRS reference
  db-script-demo.md              : DEMO DB reference
Open Questions: None — see OQ Log (srs-demo.md)
══════════════════════════════════════════════════════════════════

ENTRY GATE
─────────────────────────────────────────────────────────────────
backend-execution-plan-demo.md uploaded?  ✓
Gate ALIGN-BE ✓ confirmed?                ✓ (PASSED ✓, review(P3.1) APPROVED)
srs-demo.md uploaded?                     ✓
db-script-demo.md uploaded?               ✓
─────────────────────────────────────────────────────────────────

[TP-SEC-1]  RULE-ID SCENARIOS — per RULE-ID: Happy path + Main violation.
            Boundary added ONLY where the RULE-ID's srs-demo.md A4
            Test-Hint describes a genuine numeric threshold
            (RULE-DEMO-001, RULE-DEMO-002). RULE-DEMO-003/004/005 have
            explicit Test-Hints too, but those describe specific
            behavioral scenarios, not numeric boundaries — folded into
            each rule's Violation TC instead of a separate Boundary TC
            (avoids a meaningless "boundary" on a non-numeric condition).

[TP-SEC-2]  API-ID SCENARIOS — per API-ID: Happy path only.

Mandatory scenarios (16.4) — applicability assessed against this
module's actual shape (single entity, no Business Code, no client-facing
LOV, no cross-entity usage check):
  MANDATORY-J-1 (Business Code auto-generation)   : N/A — ENTITY-DEMO-001
    has no Business Code (backend-execution-plan-demo.md DRV-DEMO-003).
  MANDATORY-J-2 (Business Code immutability)       : N/A — same reason.
  MANDATORY-J-3 (Arabic error message, API level)  : APPLIED → TC-BE-DEMO-018
  MANDATORY-J-4 (LOV invalid value rejected)       : N/A — statusId
    (the only LOV field) is server-managed and never accepted from
    client input (CreateNoteRequest/UpdateNoteRequest both exclude it) —
    there is no client-supplied LOV value to reject.
  MANDATORY-J-5 (Permission enforcement)           : ADAPTED → TC-BE-DEMO-019.
    This domain has no role matrix (DRV-DEMO-008 — every authenticated
    user holds all 4 DEMO_NOTES permissions); "user without CREATE
    permission" does not exist among authenticated users. Adapted to the
    domain's real boundary: an unauthenticated request is rejected.
  MANDATORY-J-6 (Soft deactivation with usage check): N/A — no other
    entity references Note (srs-demo.md A7: None); DELETE is an
    unconditional soft delete, not a canDelete/canDeactivate usage
    check (backend-execution-plan-demo.md ALIGN-BE table, same N/A).
  MANDATORY-J-7 (Empty search returns 200 not 404)  : APPLIED → TC-BE-DEMO-020
  MANDATORY-J-8 (SQL injection resistance)          : APPLIED → TC-BE-DEMO-021

TARGET TC COUNT (small, single-entity module — proportionate to
business-policies-demo.md SCOPE EXCEPTIONS, not Level 2 ERP mid-
complexity): baseline (RULE-IDs × 2) + (API-IDs × 1) = (5×2)+(5×1) = 15,
+2 boundary (RULE-DEMO-001, RULE-DEMO-002) +4 applicable/adapted
mandatory scenarios = 21 TC. Within the 15–25 target band; well under
the 40-TC over-engineering ceiling.
══════════════════════════════════════════════════════════════════

<!-- PHASE:TEST-PLAN-BE:START -->

<!-- SUB:RULE-SCENARIOS:START -->

<!-- TC:TC-BE-DEMO-001:START -->
TC-BE-DEMO-001 — Create note with a valid title (RULE-DEMO-001 happy path)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : RULE-DEMO-001
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : an authenticated user, no prior notes required
When          : POST /api/v1/demo/notes with title = "Groceries" (9 chars), content omitted
Then          : HTTP 201; response NoteResponse.title = "Groceries"; statusId = "ACTIVE"
ERR-ID        : —
Language      : BOTH
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-001:END -->

<!-- TC:TC-BE-DEMO-002:START -->
TC-BE-DEMO-002 — Create note with a blank title (RULE-DEMO-001 violation)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : RULE-DEMO-001
ERR-ID       : ERR-0001
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Validation failure
Data class    : INVALID
Given         : an authenticated user
When          : POST /api/v1/demo/notes with title = "   " (whitespace-only)
Then          : HTTP 400; ERR-0001 returned; no row persisted
ERR-ID        : ERR-0001
Language      : BOTH
Test-Hint     : srs-demo.md RULE-DEMO-001 Test-Hint — "blank/whitespace-only (INVALID)"
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-002:END -->

<!-- TC:TC-BE-DEMO-003:START -->
TC-BE-DEMO-003 — Title length boundary (RULE-DEMO-001 boundary)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : RULE-DEMO-001
ERR-ID       : ERR-0001
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Boundary
Data class    : BOUNDARY
Given         : an authenticated user
When          : (a) POST with title at exactly 200 chars; (b) POST with title at exactly 201 chars
Then          : (a) HTTP 201, note created; (b) HTTP 400, ERR-0001
ERR-ID        : ERR-0001 (case b only)
Language      : BOTH
Test-Hint     : srs-demo.md RULE-DEMO-001 Test-Hint — "title at exactly 200 chars (VALID), 201 chars (INVALID)"
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-003:END -->

<!-- TC:TC-BE-DEMO-004:START -->
TC-BE-DEMO-004 — Create note with content within limit (RULE-DEMO-002 happy path)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : RULE-DEMO-002
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : an authenticated user
When          : POST /api/v1/demo/notes with title = "Note", content = a 5,000-char string
Then          : HTTP 201; response content matches the submitted string exactly
ERR-ID        : —
Language      : BOTH
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-004:END -->

<!-- TC:TC-BE-DEMO-005:START -->
TC-BE-DEMO-005 — Create note with over-limit content (RULE-DEMO-002 violation)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : RULE-DEMO-002
ERR-ID       : ERR-0002
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Validation failure
Data class    : INVALID
Given         : an authenticated user
When          : POST /api/v1/demo/notes with title = "Note", content = a 20,001-char string
Then          : HTTP 400; ERR-0002 returned; no row persisted
ERR-ID        : ERR-0002
Language      : BOTH
Test-Hint     : srs-demo.md RULE-DEMO-002 Test-Hint — "content at exactly 20,001 chars (INVALID)"
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-005:END -->

<!-- TC:TC-BE-DEMO-006:START -->
TC-BE-DEMO-006 — Content length boundary + omission (RULE-DEMO-002 boundary)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : RULE-DEMO-002
ERR-ID       : ERR-0002
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Boundary
Data class    : BOUNDARY
Given         : an authenticated user
When          : (a) POST with content at exactly 20,000 chars; (b) POST with content at
                exactly 20,001 chars; (c) POST with content omitted entirely
Then          : (a) HTTP 201; (b) HTTP 400, ERR-0002; (c) HTTP 201, content is null/absent
ERR-ID        : ERR-0002 (case b only)
Language      : BOTH
Test-Hint     : srs-demo.md RULE-DEMO-002 Test-Hint — "content at exactly 20,000 chars
                (VALID), 20,001 chars (INVALID), empty string / omitted (VALID)"
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-006:END -->

<!-- TC:TC-BE-DEMO-007:START -->
TC-BE-DEMO-007 — Owner reads their own note (RULE-DEMO-003 happy path)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-003
RULE-ID      : RULE-DEMO-003
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : User A owns note N (ACTIVE)
When          : User A calls GET /api/v1/demo/notes/{N.noteId}
Then          : HTTP 200; response body matches note N
ERR-ID        : —
Language      : BOTH
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-007:END -->

<!-- TC:TC-BE-DEMO-008:START -->
TC-BE-DEMO-008 — Non-owner requests another user's note by direct id (RULE-DEMO-003 violation)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-003
RULE-ID      : RULE-DEMO-003
ERR-ID       : ERR-0003
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Permission
Data class    : ATTACK
Given         : User A owns note N (ACTIVE); User B is a different authenticated user
When          : User B calls GET /api/v1/demo/notes/{N.noteId} directly (not via User B's own list)
Then          : HTTP 403; ERR-0003 returned — request is explicitly rejected, not merely
                absent from User B's list results
ERR-ID        : ERR-0003
Language      : BOTH
Test-Hint     : srs-demo.md RULE-DEMO-003 Test-Hint — "User B requesting User A's noteId by
                direct ID → rejected, not merely filtered from the list"
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-008:END -->

<!-- TC:TC-BE-DEMO-009:START -->
TC-BE-DEMO-009 — Owner soft-deletes their own note (RULE-DEMO-004 happy path)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-005
RULE-ID      : RULE-DEMO-004
ERR-ID       : —
LOV-ID       : LOV-DEMO-001
─────────────────────────────────────────────────────────────────
Scenario type : State transition
Data class    : VALID
Given         : User A owns note N (ACTIVE)
When          : User A calls DELETE /api/v1/demo/notes/{N.noteId}
Then          : HTTP 200; response statusId = "DELETED"; row is NOT physically removed
                (still queryable at the DB layer with statusId = 'DELETED')
ERR-ID        : —
Language      : BOTH
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-009:END -->

<!-- TC:TC-BE-DEMO-010:START -->
TC-BE-DEMO-010 — Deleted note excluded from list and get-by-id (RULE-DEMO-004 exclusion behavior)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-002, API-DEMO-003
RULE-ID      : RULE-DEMO-004
ERR-ID       : ERR-0004
LOV-ID       : LOV-DEMO-001
─────────────────────────────────────────────────────────────────
Scenario type : State transition
Data class    : VALID
Given         : User A owns note N, previously soft-deleted (statusId = DELETED)
When          : (a) User A calls GET /api/v1/demo/notes (list); (b) User A calls
                GET /api/v1/demo/notes/{N.noteId}
Then          : (a) note N does NOT appear in the returned page; (b) HTTP 404, ERR-0004
                (not the deleted record)
ERR-ID        : ERR-0004
Language      : BOTH
Test-Hint     : srs-demo.md RULE-DEMO-004 Test-Hint — "After delete, GET list excludes it;
                GET by id returns 404 (not the deleted record)"
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-010:END -->

<!-- TC:TC-BE-DEMO-011:START -->
TC-BE-DEMO-011 — Update an ACTIVE note (RULE-DEMO-005 happy path)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-004
RULE-ID      : RULE-DEMO-005
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : User A owns note N (ACTIVE)
When          : User A calls PUT /api/v1/demo/notes/{N.noteId} with a new title
Then          : HTTP 200; title updated — same underlying scenario as TC-BE-DEMO-016
                (API-DEMO-004 happy path); listed separately here only to satisfy the
                per-RULE-ID derivation rule (TP-SEC-1) — no independent assertion beyond it
ERR-ID        : —
Language      : BOTH
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-011:END -->

<!-- TC:TC-BE-DEMO-012:START -->
TC-BE-DEMO-012 — Update a DELETED note is rejected (RULE-DEMO-005 violation)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-004
RULE-ID      : RULE-DEMO-005
ERR-ID       : ERR-0005
LOV-ID       : LOV-DEMO-001
─────────────────────────────────────────────────────────────────
Scenario type : Validation failure
Data class    : INVALID
Given         : User A owns note N, previously soft-deleted (statusId = DELETED)
When          : User A calls PUT /api/v1/demo/notes/{N.noteId} with a new title
Then          : HTTP 409; ERR-0005 returned; note remains unchanged (still DELETED, old title)
ERR-ID        : ERR-0005
Language      : BOTH
Test-Hint     : srs-demo.md RULE-DEMO-005 Test-Hint — "Update on a DELETED note's id must be
                rejected (exact ERR-ID / HTTP status is P3.1's decision)" — resolved as
                ERR-0005 / HTTP 409 in backend-execution-plan-demo.md DRV-DEMO-007
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-012:END -->

<!-- SUB:RULE-SCENARIOS:END -->

<!-- SUB:API-SCENARIOS:START -->

<!-- TC:TC-BE-DEMO-013:START -->
TC-BE-DEMO-013 — API-DEMO-001 happy path (Create)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : an authenticated user
When          : POST /api/v1/demo/notes with title = "Trip ideas", content = "Beach or mountains?"
Then          : HTTP 201; NoteResponse contains noteId, title, content, statusId = "ACTIVE",
                ownerUserId = the caller's id, createdAt/createdBy populated
ERR-ID        : —
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-013:END -->

<!-- TC:TC-BE-DEMO-014:START -->
TC-BE-DEMO-014 — API-DEMO-002 happy path (List)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-002
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : User A owns 3 ACTIVE notes and 1 DELETED note; User B owns 1 ACTIVE note
When          : User A calls GET /api/v1/demo/notes?page=0&size=10
Then          : HTTP 200; page contains exactly User A's 3 ACTIVE notes, sorted by
                updatedAt DESC; User B's note and User A's DELETED note are absent
ERR-ID        : —
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-014:END -->

<!-- TC:TC-BE-DEMO-015:START -->
TC-BE-DEMO-015 — API-DEMO-003 happy path (Get by id)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-003
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : User A owns note N (ACTIVE)
When          : User A calls GET /api/v1/demo/notes/{N.noteId}
Then          : HTTP 200; full NoteResponse for note N returned
ERR-ID        : —
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-015:END -->

<!-- TC:TC-BE-DEMO-016:START -->
TC-BE-DEMO-016 — API-DEMO-004 happy path (Update)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-004
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : User A owns note N (ACTIVE, title = "Old title")
When          : User A calls PUT /api/v1/demo/notes/{N.noteId} with title = "New title",
                content omitted
Then          : HTTP 200; response title = "New title"; content unchanged from before
                (DRV-DEMO-009 — omitted field left as-is); updatedAt refreshed
ERR-ID        : —
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-016:END -->

<!-- TC:TC-BE-DEMO-017:START -->
TC-BE-DEMO-017 — API-DEMO-005 happy path (Delete)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-005
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Happy path
Data class    : VALID
Given         : User A owns note N (ACTIVE)
When          : User A calls DELETE /api/v1/demo/notes/{N.noteId}
Then          : HTTP 200; response statusId = "DELETED" (confirmation body per
                srs-demo.md B5 API-DEMO-005)
ERR-ID        : —
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-017:END -->

<!-- TC:TC-BE-DEMO-018:START -->
TC-BE-DEMO-018 — Arabic + English error message present (MANDATORY-J-3, applied)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : RULE-DEMO-001
ERR-ID       : ERR-0001
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Arabic message
Data class    : INVALID
Given         : an authenticated user
When          : POST /api/v1/demo/notes with a blank title
Then          : HTTP 400; response body messageAr = "يجب إدخال عنوان للملاحظة (200 حرف
                كحد أقصى)." exact match; messageEn = "A note title is required (max 200
                characters)." also present
ERR-ID        : ERR-0001
Language      : BOTH
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-018:END -->

<!-- TC:TC-BE-DEMO-019:START -->
TC-BE-DEMO-019 — Unauthenticated request rejected (MANDATORY-J-5, adapted)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Permission
Data class    : ATTACK
Given         : no authenticated session (no/invalid token)
When          : POST /api/v1/demo/notes with an otherwise-valid body
Then          : HTTP 401; no row persisted
ERR-ID        : — (platform-level auth error, outside this module's Error Catalog —
                see backend-execution-plan-demo.md, N/A note on MANDATORY-J-4/J-5)
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-019:END -->

<!-- TC:TC-BE-DEMO-020:START -->
TC-BE-DEMO-020 — Empty list returns 200, not 404 (MANDATORY-J-7, applied)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-002
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Edge case
Data class    : EDGE_CASE
Given         : User C is authenticated and owns zero notes
When          : User C calls GET /api/v1/demo/notes
Then          : HTTP 200; page content = empty list — NEVER HTTP 404
ERR-ID        : —
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-020:END -->

<!-- TC:TC-BE-DEMO-021:START -->
TC-BE-DEMO-021 — SQL injection resistance on title (MANDATORY-J-8, applied)
─────────────────────────────────────────────────────────────────
API-ID       : API-DEMO-001
RULE-ID      : —
ERR-ID       : —
LOV-ID       : —
─────────────────────────────────────────────────────────────────
Scenario type : Security attack
Data class    : ATTACK
Given         : an authenticated user
When          : POST /api/v1/demo/notes with title = "test' OR '1'='1"
Then          : HTTP 201 with the value stored and returned as a literal string
                (title = "test' OR '1'='1" verbatim) — DB is not affected, no other
                user's data is leaked or altered
ERR-ID        : —
Language      : —
Test-Hint     : —
XM-impact     : —
─────────────────────────────────────────────────────────────────
<!-- TC:TC-BE-DEMO-021:END -->

<!-- SUB:API-SCENARIOS:END -->

<!-- PHASE:TEST-PLAN-BE:END -->

---

## TC TRACEABILITY INDEX (BACKEND) — DEMO
══════════════════════════════════════════════════════════════════
RULE-ID → TC-IDs:
RULE-DEMO-001  → TC-BE-DEMO-001 (happy) | TC-BE-DEMO-002 (violation) | TC-BE-DEMO-003 (boundary) | TC-BE-DEMO-018 (Arabic message)
RULE-DEMO-002  → TC-BE-DEMO-004 (happy) | TC-BE-DEMO-005 (violation) | TC-BE-DEMO-006 (boundary)
RULE-DEMO-003  → TC-BE-DEMO-007 (happy) | TC-BE-DEMO-008 (violation)
RULE-DEMO-004  → TC-BE-DEMO-009 (happy) | TC-BE-DEMO-010 (exclusion behavior)
RULE-DEMO-005  → TC-BE-DEMO-011 (happy) | TC-BE-DEMO-012 (violation)

API-ID → TC-IDs:
API-DEMO-001   → TC-BE-DEMO-001, TC-BE-DEMO-002, TC-BE-DEMO-003, TC-BE-DEMO-004,
                 TC-BE-DEMO-005, TC-BE-DEMO-006, TC-BE-DEMO-013, TC-BE-DEMO-018,
                 TC-BE-DEMO-019, TC-BE-DEMO-021
API-DEMO-002   → TC-BE-DEMO-010, TC-BE-DEMO-014, TC-BE-DEMO-020
API-DEMO-003   → TC-BE-DEMO-007, TC-BE-DEMO-008, TC-BE-DEMO-010, TC-BE-DEMO-015
API-DEMO-004   → TC-BE-DEMO-011, TC-BE-DEMO-012, TC-BE-DEMO-016
API-DEMO-005   → TC-BE-DEMO-009, TC-BE-DEMO-017

ERR-ID → TC-IDs:
ERR-0001       → TC-BE-DEMO-002, TC-BE-DEMO-003, TC-BE-DEMO-018
ERR-0002       → TC-BE-DEMO-005, TC-BE-DEMO-006
ERR-0003       → TC-BE-DEMO-008
ERR-0004       → TC-BE-DEMO-010
ERR-0005       → TC-BE-DEMO-012
══════════════════════════════════════════════════════════════════
Coverage summary:
  RULE-IDs covered  : 5 / 5
  API-IDs covered   : 5 / 5
  ERR-IDs covered   : 5 / 5
  Total backend TCs : 21 — within target 15–25
══════════════════════════════════════════════════════════════════

---

## TC COVERAGE MATRIX SUMMARY (BACKEND) — DEMO
══════════════════════════════════════════════════════════════════
RULE-ID COVERAGE:
RULE-ID          │ Happy path TC     │ Violation TC      │ Status
─────────────────┼───────────────────┼───────────────────┼──────────────
RULE-DEMO-001    │ TC-BE-DEMO-001    │ TC-BE-DEMO-002    │ COVERED ✓
RULE-DEMO-002    │ TC-BE-DEMO-004    │ TC-BE-DEMO-005    │ COVERED ✓
RULE-DEMO-003    │ TC-BE-DEMO-007    │ TC-BE-DEMO-008    │ COVERED ✓
RULE-DEMO-004    │ TC-BE-DEMO-009    │ TC-BE-DEMO-010    │ COVERED ✓
RULE-DEMO-005    │ TC-BE-DEMO-011    │ TC-BE-DEMO-012    │ COVERED ✓
──────────────────────────────────────────────────────────────────
API-ID COVERAGE:
API-DEMO-001     │ TC-BE-DEMO-013    │ COVERED ✓
API-DEMO-002     │ TC-BE-DEMO-014    │ COVERED ✓
API-DEMO-003     │ TC-BE-DEMO-015    │ COVERED ✓
API-DEMO-004     │ TC-BE-DEMO-016    │ COVERED ✓
API-DEMO-005     │ TC-BE-DEMO-017    │ COVERED ✓
──────────────────────────────────────────────────────────────────
Gate rule (self-check only):
  COVERED ✓ = happy-path + violation TC both declared (or, for API-ID
  rows, the happy-path TC declared). No PARTIAL or GAP rows — every
  RULE-ID and API-ID reached full coverage without a DEFERRED entry.
══════════════════════════════════════════════════════════════════

══════════════════════════════════════════════════════════════════
*End of backend-test-plan-demo.md*
*Produced by: standalone Test Generation Engine (outside the core pipeline)*
*PLAN-ID: PLAN-DEMO-001 | Total TCs: 21*
*test-execution-manifest.md: NOT generated for this factory instance —
 not in governance-tools/tracks/backend/config.py ARTIFACT_FILES["P3_5_BE"]
 for this factory build; P5 (api-verify) is out of scope for this pass.*
══════════════════════════════════════════════════════════════════
