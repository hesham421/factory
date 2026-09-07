<!-- Source: PHASE:TEST-PLAN-BE / SUB:API-SCENARIOS -->


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

