<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
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

















## REGISTRY — P3.1 — DEMO v1
See `registry-exec-be-demo.md`.
══════════════════════════════════════════════════════════════════
