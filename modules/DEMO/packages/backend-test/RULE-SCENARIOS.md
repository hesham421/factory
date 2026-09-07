<!-- Source: PHASE:TEST-PLAN-BE / SUB:RULE-SCENARIOS -->


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

