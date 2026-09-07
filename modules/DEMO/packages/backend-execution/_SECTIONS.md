<!-- Source: content OUTSIDE all PHASE markers (trailing / between-phase sections — e.g. Plan Index, DB Alignment Manifest, Error Catalog, Agent Handoff Summary) -->

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


---


---


---


---


---


---


---


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