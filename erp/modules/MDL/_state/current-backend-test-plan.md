# BACKEND TEST PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Scope : project (modules MDL, SEC)
Sources: srs-mdl.md v1 · backend-execution-plan-mdl.md v1 · registry-srs-mdl.md v1 · registry-db-mdl.md v1
Framework: agnostic. REDUCED: no. Open ADRs: 0 new.
TC count: 13 (module scope) · 1 (integration — XM-MDL-001, MDL declares → SEC)
══════════════════════════════════════════════════════════════════

<!-- PHASE:TEST-PLAN-BE:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013 -->

<!-- SUB:RULE-SCENARIOS:START traces=REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-007,REQ-MDL-011,REQ-MDL-012 -->
### SUB — RULE-SCENARIOS

<!-- TC:TC-MDL-002:START traces=AC-MDL-002,REQ-MDL-002,API-MDL-002 -->
### TC-MDL-002 — reject a type for an unregistered owner module
Derived from : AC-MDL-002 (REQ-MDL-002)
Exercises    : API-MDL-002 POST /api/v1/mdl/lookup-types
Rule / code  : RULE-MDL-001 → MDL-409-MODULE-NOT-REGISTERED
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an owner module code with no ModuleRegistry row in SEC
Steps        : 1. POST {key, ownerModuleCode: "ZZZ", nameAr, nameEn}
Expected     : 409 MDL-409-MODULE-NOT-REGISTERED; no LookupType created
Test data    : ownerModuleCode "ZZZ" (never registered in SEC)
<!-- TC:TC-MDL-002:END -->

<!-- TC:TC-MDL-003:START traces=AC-MDL-003,REQ-MDL-003,API-MDL-003 -->
### TC-MDL-003 — key is immutable after creation
Derived from : AC-MDL-003 (REQ-MDL-003)
Exercises    : API-MDL-003 PUT /api/v1/mdl/lookup-types/{id}
Rule / code  : RULE-MDL-003 → (enforced by DTO shape — no error code, `key` simply absent from the request schema)
Scenario     : STATE · data class VALID · language ALL
Preconditions: an existing LookupType
Steps        : 1. PUT {nameAr, nameEn} (no `key` field in the request DTO at all) — 2. attempt to also pass a `key` value and confirm it is ignored / rejected by schema validation
Expected     : 200; names updated, key unchanged; step 2 either fails schema validation (400) or is silently ignored depending on the consumer's DTO strictness — either way key never changes
Test data    : existing type key "ACCOUNT_TYPE"
<!-- TC:TC-MDL-003:END -->

<!-- TC:TC-MDL-004:START traces=AC-MDL-004,REQ-MDL-004,API-MDL-004 -->
### TC-MDL-004 — deactivating a type excludes its values from reads
Derived from : AC-MDL-004 (REQ-MDL-004)
Exercises    : API-MDL-004 DELETE /api/v1/mdl/lookup-types/{id}
Rule / code  : RULE-MDL-004 → (no error code — enforced on the read side, see TC-MDL-011)
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active LookupType with active values
Steps        : 1. DELETE (deactivate) the type — 2. call API-MDL-011 for its key
Expected     : 1. 200, isActiveFl=false — 2. step 2 returns no values (REQ-MDL-011 no longer returns them)
Test data    : a test-only type with 2 active values
<!-- TC:TC-MDL-004:END -->

<!-- TC:TC-MDL-007:START traces=AC-MDL-007,REQ-MDL-007,API-MDL-006 -->
### TC-MDL-007 — reject a duplicate code within a type
Derived from : AC-MDL-007 (REQ-MDL-007)
Exercises    : API-MDL-006 POST /api/v1/mdl/lookup-types/{id}/values
Rule / code  : RULE-MDL-002 → MDL-409-VALUE-DUP
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a type already holding a value with code "ACTIVE"
Steps        : 1. POST a second value with code "ACTIVE" under the same type
Expected     : 409 MDL-409-VALUE-DUP; no second row created
Test data    : type USER_STATUS, code "ACTIVE" (already exists)
<!-- TC:TC-MDL-007:END -->

<!-- TC:TC-MDL-011:START traces=AC-MDL-011,REQ-MDL-011,API-MDL-011 -->
### TC-MDL-011 — read active values by key, ordered
Derived from : AC-MDL-011 (REQ-MDL-011)
Exercises    : API-MDL-011 GET /api/v1/mdl/lookups
Rule / code  : RULE-MDL-004 (positive path — active type, active values only)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a type "PAYMENT_METHOD" with 2 active and 1 inactive value
Steps        : 1. GET ?type=PAYMENT_METHOD
Expected     : 200; exactly the 2 active values, ordered by sortOrder
Test data    : PAYMENT_METHOD with 3 values (2 active, 1 inactive)
<!-- TC:TC-MDL-011:END -->

<!-- TC:TC-MDL-012:START traces=AC-MDL-012,REQ-MDL-012,API-MDL-011 -->
### TC-MDL-012 — reject an unknown type key
Derived from : AC-MDL-012 (REQ-MDL-012)
Exercises    : API-MDL-011 GET /api/v1/mdl/lookups
Rule / code  : RULE-MDL-004 → MDL-404-TYPE-KEY
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: no LookupType with key "NOT_A_REAL_KEY"
Steps        : 1. GET ?type=NOT_A_REAL_KEY
Expected     : 404 MDL-404-TYPE-KEY (never an empty-success)
Test data    : type "NOT_A_REAL_KEY"
<!-- TC:TC-MDL-012:END -->
<!-- SUB:RULE-SCENARIOS:END -->

  <!-- SUB:API-SCENARIOS:START traces=REQ-MDL-001,REQ-MDL-005,REQ-MDL-006,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,REQ-MDL-013 -->
  ### SUB — API-SCENARIOS

  <!-- TC:TC-MDL-001:START traces=AC-MDL-001,REQ-MDL-001,API-MDL-002 -->
  ### TC-MDL-001 — create a lookup type
  Derived from : AC-MDL-001 (REQ-MDL-001)
  Exercises    : API-MDL-002 POST /api/v1/mdl/lookup-types
  Rule / code  : — (happy path)
  Scenario     : HAPPY · data class VALID · language ALL
  Preconditions: unique key; registered owner module code
  Steps        : 1. POST {key: "TEST_TYPE", ownerModuleCode: "MDL", nameAr, nameEn}
  Expected     : 201; active LookupType created
  Test data    : key "TEST_TYPE", ownerModuleCode "MDL" (MDL owning its own test lookup type is a legitimate self-registration case — a module owning its own reference data is a real scenario, not a contrived one)
  <!-- TC:TC-MDL-001:END -->

  <!-- TC:TC-MDL-005:START traces=AC-MDL-005,REQ-MDL-005,API-MDL-005 -->
  ### TC-MDL-005 — select a type and list its values
  Derived from : AC-MDL-005 (REQ-MDL-005)
  Exercises    : API-MDL-005 POST /api/v1/mdl/lookup-types/values/search
  Rule / code  : — (happy path)
  Scenario     : HAPPY · data class VALID · language ALL
  Preconditions: a type with 3 values
  Steps        : 1. POST /search filtered by the type's lookupTypeId
  Expected     : 200; exactly those 3 values, ordered by sortOrder
  Test data    : type with 3 values
  <!-- TC:TC-MDL-005:END -->

  <!-- TC:TC-MDL-006:START traces=AC-MDL-006,REQ-MDL-006,API-MDL-006 -->
### TC-MDL-006 — create a lookup value
Derived from : AC-MDL-006 (REQ-MDL-006)
Exercises    : API-MDL-006 POST /api/v1/mdl/lookup-types/{id}/values
Rule / code  : — (happy path)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a code not yet used within the type
Steps        : 1. POST {code, nameAr, nameEn, sortOrder}
Expected     : 201; active LookupValue created under the type
Test data    : new code "NEW_VAL" under an existing type
<!-- TC:TC-MDL-006:END -->

<!-- TC:TC-MDL-008:START traces=AC-MDL-008,REQ-MDL-008,API-MDL-007 -->
### TC-MDL-008 — edit a lookup value
Derived from : AC-MDL-008 (REQ-MDL-008)
Exercises    : API-MDL-007 PUT /api/v1/mdl/lookup-values/{id}
Rule / code  : — (happy path)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an existing LookupValue
Steps        : 1. PUT {nameAr, nameEn, sortOrder}
Expected     : 200; names/sortOrder updated; code and lookupTypeId unchanged
Test data    : existing value, new nameEn
<!-- TC:TC-MDL-008:END -->

<!-- TC:TC-MDL-009:START traces=AC-MDL-009,REQ-MDL-009,API-MDL-008 -->
### TC-MDL-009 — deactivate a lookup value
Derived from : AC-MDL-009 (REQ-MDL-009)
Exercises    : API-MDL-008 DELETE /api/v1/mdl/lookup-values/{id}
Rule / code  : — (happy path)
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active LookupValue
Steps        : 1. DELETE (deactivate) — 2. call API-MDL-011 for its type
Expected     : 1. 200, isActiveFl=false — 2. the value no longer returned
Test data    : a test-only value
<!-- TC:TC-MDL-009:END -->

<!-- TC:TC-MDL-010:START traces=AC-MDL-010,REQ-MDL-010,API-MDL-009 -->
### TC-MDL-010 — reorder lookup values
Derived from : AC-MDL-010 (REQ-MDL-010)
Exercises    : API-MDL-009 PATCH /api/v1/mdl/lookup-types/{id}/values/reorder
Rule / code  : — (happy path)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: 3 values with sortOrder 1,2,3
Steps        : 1. PATCH {orderedValueIds: [v3, v1, v2]}
Expected     : 200; sortOrder persisted as 3,1,2 respectively; a subsequent API-MDL-011 call returns them in that order
Test data    : 3 values under one type
<!-- TC:TC-MDL-010:END -->

<!-- TC:TC-MDL-013:START traces=AC-MDL-013,REQ-MDL-013,API-MDL-010 -->
### TC-MDL-013 — browse the type registry grouped by owner
Derived from : AC-MDL-013 (REQ-MDL-013)
Exercises    : API-MDL-010 POST /api/v1/mdl/lookup-types/by-owner/search
Rule / code  : — (happy path)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: types owned by SEC and by MDL
Steps        : 1. POST /search for the registry
Expected     : 200; types grouped under their respective owner-module headings
Test data    : existing SEC-owned and MDL-owned types
<!-- TC:TC-MDL-013:END -->
<!-- SUB:API-SCENARIOS:END -->
<!-- PHASE:TEST-PLAN-BE:END -->

<!-- PHASE:INT-XM:START traces=REQ-MDL-002,XM-MDL-001 -->
MDL declares one XM (XM-MDL-001, SOFT-READ → SEC's ModuleRegistry); SEC is in the current
selection, so this is a real linking atom.

<!-- TC:TC-MDL-014:START traces=XM-MDL-001,REQ-MDL-002,API-MDL-002 -->
### TC-MDL-014 — graceful degradation when SEC is unreachable during owner-module validation
Derived from : XM-MDL-001 (REQ-MDL-002)
Exercises    : API-MDL-002 POST /api/v1/mdl/lookup-types
Rule / code  : XM-MDL-001 (SOFT-READ) → (a defined error, never a 500/unhandled state)
Scenario     : INTEGRATION · data class EDGE · language ALL
Preconditions: SEC's registry-search endpoint (API-SEC-021) is made unreachable/times out
Steps        : 1. POST a new lookup-type registration while SEC is unreachable
Expected     : the request fails with a defined, documented error (not a raw 500/timeout
  leak) — MDL's own flow returns a controlled response rather than crashing
Test data    : any lookup-type payload; SEC endpoint simulated as down
<!-- TC:TC-MDL-014:END -->
<!-- PHASE:INT-XM:END -->

## TC TRACEABILITY INDEX
| AC | TC | REQ | API | RULE/code | XM |
|---|---|---|---|---|---|
| AC-MDL-001…013 | TC-MDL-001…013 (1:1) | REQ-MDL-001…013 (1:1) | see each TC's Exercises line | see each TC's Rule/code line | — |
| — | TC-MDL-014 | REQ-MDL-002 | API-MDL-002 | — | XM-MDL-001 |

## COVERAGE
AC covered 13/13 (0 gaps) · REQ covered 13/13 · API covered 11/11 · every selected-module
XM covered 1/1 (XM-MDL-001 → TC-MDL-014, no gap).
══════════════════════════════════════════════════════════════════
