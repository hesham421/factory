<!-- source: PHASE:TEST-PLAN-BE / SUB:RULE-SCENARIOS -->
<!-- traces: AC-FIN-002, AC-FIN-006, AC-FIN-009, AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-017, AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-028, AC-FIN-029, AC-FIN-030, AC-FIN-035, AC-FIN-038, API-FIN-003, API-FIN-007, API-FIN-011, API-FIN-019, API-FIN-020, API-FIN-021, API-FIN-024, API-FIN-026, REQ-FIN-002, REQ-FIN-006, REQ-FIN-009, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-035, REQ-FIN-038 -->
<!-- SUB:RULE-SCENARIOS:START traces=REQ-FIN-002,REQ-FIN-006,REQ-FIN-009,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,REQ-FIN-035,REQ-FIN-038 -->
### SUB — RULE-SCENARIOS (the 14 §12 must-honor points + SoD)

<!-- TC:TC-FIN-002:START traces=AC-FIN-002,REQ-FIN-002,API-FIN-003 -->
### TC-FIN-002 — reject direct-posting on an account with children
Derived from : AC-FIN-002 (REQ-FIN-002) · Exercises: API-FIN-003 PUT /api/v1/fin/accounts/{id}
Rule / code  : RULE-FIN-001 → FIN-409-HAS-CHILDREN
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an account with ≥1 child account
Steps        : 1. PUT {isLeafFl: true} on the parent
Expected     : 409 FIN-409-HAS-CHILDREN; isLeafFl unchanged
Test data    : parent account with 1 child
<!-- TC:TC-FIN-002:END -->

<!-- TC:TC-FIN-006:START traces=AC-FIN-006,REQ-FIN-006,API-FIN-007 -->
### TC-FIN-006 — reject a duplicate code within a dimension
Derived from : AC-FIN-006 (REQ-FIN-006) · Exercises: API-FIN-007 POST /api/v1/fin/dimensions/{id}/values
Rule / code  : RULE-FIN-002 → FIN-409-DIMVALUE-DUP
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a dimension already holding value code "NORTH"
Steps        : 1. POST a second value with code "NORTH" under the same dimension
Expected     : 409 FIN-409-DIMVALUE-DUP; no second row
Test data    : dimension "REGION", code "NORTH"
<!-- TC:TC-FIN-006:END -->

<!-- TC:TC-FIN-009:START traces=AC-FIN-009,REQ-FIN-009,API-FIN-011 -->
### TC-FIN-009 — reject an incorrect remainder-line count
Derived from : AC-FIN-009 (REQ-FIN-009) · Exercises: API-FIN-011 POST /api/v1/fin/event-rules/{id}/lines
Rule / code  : RULE-FIN-003 → FIN-409-REMAINDER-COUNT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a rule with 2 PERCENTAGE lines and 0 lines marked remainder
Steps        : 1. attempt to save the rule as-is
Expected     : 409 FIN-409-REMAINDER-COUNT until exactly one line is marked remainder
Test data    : 2 PERCENTAGE lines (30%, 70%), 0 remainder lines
<!-- TC:TC-FIN-009:END -->

<!-- TC:TC-FIN-011:START traces=AC-FIN-011,REQ-FIN-011,API-FIN-020 -->
### TC-FIN-011 — reject a duplicate event reference (§12.12 idempotency)
Derived from : AC-FIN-011 (REQ-FIN-011) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
Rule / code  : RULE-FIN-004 → FIN-409-DUPLICATE-EVENT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a POSTED entry already exists with eventReference "EVT-1001"
Steps        : 1. submit another event with reference "EVT-1001"
Expected     : 409 FIN-409-DUPLICATE-EVENT; no second entry posted
Test data    : eventReference "EVT-1001" (already used)
<!-- TC:TC-FIN-011:END -->

<!-- TC:TC-FIN-012:START traces=AC-FIN-012,REQ-FIN-012,API-FIN-020 -->
### TC-FIN-012 — remainder line absorbs the rounding difference exactly (§12.6)
Derived from : AC-FIN-012 (REQ-FIN-012) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
Rule / code  : RULE-FIN-010 → (success-path computation, no error code)
Scenario     : HAPPY · data class BOUNDARY · language ALL
Preconditions: a rule distributing 100.00 as 33% + 33% + remainder
Steps        : 1. submit the triggering event with amount=100.00
Expected     : the two percentage lines total 66.00 (each rounded to the smallest currency
  unit); the remainder line is exactly 34.00; total debits = total credits = 100.00 exactly
Test data    : amount 100.00, split 33%/33%/remainder
<!-- TC:TC-FIN-012:END -->

<!-- TC:TC-FIN-013:START traces=AC-FIN-013,REQ-FIN-013,API-FIN-020 -->
### TC-FIN-013 — reject an event with no active rule
Derived from : AC-FIN-013 (REQ-FIN-013) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
Rule / code  : RULE-FIN-005 → FIN-404-NO-ACTIVE-RULE
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an event type with no active EventTypeRule
Steps        : 1. submit an event of that type
Expected     : 404 FIN-404-NO-ACTIVE-RULE; the failure is recorded for operator follow-up; no entry created
Test data    : eventType "NEVER_CONFIGURED"
<!-- TC:TC-FIN-013:END -->

<!-- TC:TC-FIN-017:START traces=AC-FIN-017,REQ-FIN-017,API-FIN-019 -->
### TC-FIN-017 — unified validation + direct posting, no separate approval (§8.1, §12 no per-entry approval)
Derived from : AC-FIN-017 (REQ-FIN-017) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-016 → (success-path; entry locks immediately on post)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a balanced DRAFT that passes every check (RULE-FIN-006..009)
Steps        : 1. submit the entry — 2. immediately attempt to edit or delete it (no approval step exists between build and post)
Expected     : 1. statusCode=POSTED, postedAt set, in the same call/transaction as validation — 2. step 2 is rejected (no UPDATE/DELETE route on a POSTED row)
Test data    : a fully valid 2-line balanced manual entry
<!-- TC:TC-FIN-017:END -->

<!-- TC:TC-FIN-018:START traces=AC-FIN-018,REQ-FIN-018,API-FIN-019 -->
### TC-FIN-018 — reject an unbalanced entry (§12.1 debit=credit invariant)
Derived from : AC-FIN-018 (REQ-FIN-018) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-006 → FIN-409-UNBALANCED
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: lines totaling debit 100.00, credit 99.99
Steps        : 1. submit the entry
Expected     : 409 FIN-409-UNBALANCED, imbalance amount shown; nothing posted (also re-run via API-FIN-020/014/017 — same RULE, same code, per Exercises union)
Test data    : debit 100.00 / credit 99.99
<!-- TC:TC-FIN-018:END -->

<!-- TC:TC-FIN-019:START traces=AC-FIN-019,REQ-FIN-019,API-FIN-019 -->
### TC-FIN-019 — reject a non-postable account (§12.3 leaf/active only)
Derived from : AC-FIN-019 (REQ-FIN-019) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-007 → FIN-409-NOT-POSTABLE-ACCOUNT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a line targeting a non-leaf (rollup) account
Steps        : 1. submit the entry
Expected     : 409 FIN-409-NOT-POSTABLE-ACCOUNT, offending line named; nothing posted
Test data    : a rollup account with isLeafFl=false
<!-- TC:TC-FIN-019:END -->

<!-- TC:TC-FIN-020:START traces=AC-FIN-020,REQ-FIN-020,API-FIN-019 -->
### TC-FIN-020 — reject a closed period at post time (§12.4 period gate at post, not build)
Derived from : AC-FIN-020 (REQ-FIN-020) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-008 → FIN-409-PERIOD-NOT-OPEN
Scenario     : VIOLATION · data class EDGE · language ALL
Preconditions: an entry built while its period was Open, then the period is Hard Closed before posting completes
Steps        : 1. build the entry (period Open) — 2. hard-close the period — 3. complete posting
Expected     : 409 FIN-409-PERIOD-NOT-OPEN at step 3, citing the period's current state
Test data    : period transitioned OPEN→HARD_CLOSE between build and post
<!-- TC:TC-FIN-020:END -->

<!-- TC:TC-FIN-021:START traces=AC-FIN-021,REQ-FIN-021,API-FIN-019 -->
### TC-FIN-021 — reject an invalid dimension value (§12.11 dimensions as posting identity)
Derived from : AC-FIN-021 (REQ-FIN-021) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-009 → FIN-409-INVALID-DIMENSION
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a line citing an inactive DimensionValue
Steps        : 1. submit the entry
Expected     : 409 FIN-409-INVALID-DIMENSION, offending line + dimension named
Test data    : an inactive dimension value
<!-- TC:TC-FIN-021:END -->

<!-- TC:TC-FIN-028:START traces=AC-FIN-028,REQ-FIN-028,API-FIN-021 -->
### TC-FIN-028 — reversal is exact and bidirectionally linked (§12.7)
Derived from : AC-FIN-028 (REQ-FIN-028) · Exercises: API-FIN-021 POST /api/v1/fin/journal-entries/{id}/reverse
Rule / code  : RULE-FIN-011 → (success-path)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a POSTED entry with 3 lines
Steps        : 1. reverse it
Expected     : a new POSTED entry with the same 3 lines' amounts and opposite directions;
  original.reversalEntryId = new.id and new.originalEntryId = original.id
Test data    : 3-line posted entry
<!-- TC:TC-FIN-028:END -->

<!-- TC:TC-FIN-029:START traces=AC-FIN-029,REQ-FIN-029,API-FIN-021 -->
### TC-FIN-029 — reversal posts to the current period when the original's is closed
Derived from : AC-FIN-029 (REQ-FIN-029) · Exercises: API-FIN-021 POST /api/v1/fin/journal-entries/{id}/reverse
Rule / code  : RULE-FIN-012 → (success-path, period substitution)
Scenario     : STATE · data class EDGE · language ALL
Preconditions: a POSTED entry whose period is now Hard Closed
Steps        : 1. reverse it
Expected     : the reversal posts into the current open period, not the closed one
Test data    : entry in a now-hard-closed period
<!-- TC:TC-FIN-029:END -->

<!-- TC:TC-FIN-030:START traces=AC-FIN-030,REQ-FIN-030,API-FIN-021 -->
### TC-FIN-030 — reject reversing an already-reversed (non-POSTED) entry
Derived from : AC-FIN-030 (REQ-FIN-030) · Exercises: API-FIN-021 POST /api/v1/fin/journal-entries/{id}/reverse
Rule / code  : RULE-FIN-013 → FIN-409-NOT-POSTED
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an entry already reversed once (its own statusCode is now VOID)
Steps        : 1. attempt to reverse it again
Expected     : 409 FIN-409-NOT-POSTED
Test data    : an already-reversed entry
<!-- TC:TC-FIN-030:END -->

<!-- TC:TC-FIN-035:START traces=AC-FIN-035,REQ-FIN-035,API-FIN-024 -->
### TC-FIN-035 — reject reopening a hard-closed period
Derived from : AC-FIN-035 (REQ-FIN-035) · Exercises: API-FIN-024 PATCH /api/v1/fin/fiscal-periods/{id}/open
Rule / code  : RULE-FIN-014 → FIN-409-NOT-REOPENABLE
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a Hard Closed period
Steps        : 1. attempt to reopen it
Expected     : 409 FIN-409-NOT-REOPENABLE
Test data    : a hard-closed period
<!-- TC:TC-FIN-035:END -->

<!-- TC:TC-FIN-038:START traces=AC-FIN-038,REQ-FIN-038,API-FIN-026 -->
### TC-FIN-038 — close-approval permission distinct from entry-creation permission (SoD)
Derived from : AC-FIN-038 (REQ-FIN-038) · Exercises: API-FIN-026 PATCH /api/v1/fin/fiscal-periods/{id}/hard-close
Rule / code  : RULE-FIN-015 → FIN-403-SOD-VIOLATION
Scenario     : PERMISSION · data class ATTACK · language ALL
Preconditions: a role holding only `PERM_FIN_JOURNAL_ENTRIES_CREATE` (no close-approve permission)
Steps        : 1. that role's user attempts hard-close
Expected     : 403 FIN-403-SOD-VIOLATION (or 403 FIN-403-FORBIDDEN if the permission itself is entirely absent — both paths tested)
Test data    : role with entry-creation only
<!-- TC:TC-FIN-038:END -->
<!-- SUB:RULE-SCENARIOS:END -->
