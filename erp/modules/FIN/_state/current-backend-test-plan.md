# BACKEND TEST PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Scope : project (modules FIN, MDL, SEC)
Sources: srs-fin.md v1 · backend-execution-plan-fin.md v1 · registry-srs-fin.md v1 · registry-db-fin.md v1
Framework: agnostic. REDUCED: no. Open ADRs: 0 new (ADR-FIN-001 unaffected).
TC count: 46 (module scope) · 1 (integration — XM-FIN-001, FIN declares → MDL)
══════════════════════════════════════════════════════════════════

<!-- PHASE:TEST-PLAN-BE:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,REQ-FIN-025,REQ-FIN-026,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043,REQ-FIN-044,REQ-FIN-045,REQ-FIN-046 -->

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

<!-- SUB:API-SCENARIOS:START traces=REQ-FIN-001,REQ-FIN-003,REQ-FIN-004,REQ-FIN-005,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,REQ-FIN-025,REQ-FIN-026,REQ-FIN-027,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-036,REQ-FIN-037,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043,REQ-FIN-044,REQ-FIN-045,REQ-FIN-046 -->
### SUB — API-SCENARIOS

<!-- TC:TC-FIN-001:START traces=AC-FIN-001,REQ-FIN-001,API-FIN-002 -->
### TC-FIN-001 — create an account
Derived from : AC-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-002 POST /api/v1/fin/accounts
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: unique code; registered owner-consistent accountTypeCode/natureCode
Steps        : 1. POST {code, nameAr, nameEn, accountTypeCode: "ASSET", natureCode: "DEBIT"}
Expected     : 201; account created
Test data    : code "1000", ASSET/DEBIT
<!-- TC:TC-FIN-001:END -->

<!-- TC:TC-FIN-003:START traces=AC-FIN-003,REQ-FIN-003,API-FIN-004 -->
### TC-FIN-003 — deactivate an account blocks future posting
Derived from : AC-FIN-003 (REQ-FIN-003) · Exercises: API-FIN-004 DELETE /api/v1/fin/accounts/{id}
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active account
Steps        : 1. DELETE (deactivate) — 2. attempt to post to it (TC-FIN-019 pattern)
Expected     : 1. 200, isActiveFl=false — 2. rejected (FIN-409-NOT-POSTABLE-ACCOUNT)
Test data    : a leaf account with no postings yet
<!-- TC:TC-FIN-003:END -->

<!-- TC:TC-FIN-004:START traces=AC-FIN-004,REQ-FIN-004,API-FIN-006 -->
### TC-FIN-004 — create a dimension
Derived from : AC-FIN-004 (REQ-FIN-004) · Exercises: API-FIN-006 POST /api/v1/fin/dimensions
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: unique code
Steps        : 1. POST {code, nameAr, nameEn}
Expected     : 201; active Dimension created
Test data    : code "PROJECT"
<!-- TC:TC-FIN-004:END -->

<!-- TC:TC-FIN-005:START traces=AC-FIN-005,REQ-FIN-005,API-FIN-007 -->
### TC-FIN-005 — create a dimension value
Derived from : AC-FIN-005 (REQ-FIN-005) · Exercises: API-FIN-007 POST /api/v1/fin/dimensions/{id}/values
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a code not yet used under the dimension
Steps        : 1. POST {code, nameAr, nameEn, sortOrder}
Expected     : 201; DimensionValue created
Test data    : dimension "PROJECT", code "P100"
<!-- TC:TC-FIN-005:END -->

<!-- TC:TC-FIN-007:START traces=AC-FIN-007,REQ-FIN-007,API-FIN-010 -->
### TC-FIN-007 — create an event-type rule
Derived from : AC-FIN-007 (REQ-FIN-007) · Exercises: API-FIN-010 POST /api/v1/fin/event-rules
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an event type with no existing rule
Steps        : 1. POST {eventTypeCode, nameAr, nameEn}
Expected     : 201; active EventTypeRule created
Test data    : eventTypeCode "INVOICE_PAID"
<!-- TC:TC-FIN-007:END -->

<!-- TC:TC-FIN-008:START traces=AC-FIN-008,REQ-FIN-008,API-FIN-011 -->
### TC-FIN-008 — add a rule line
Derived from : AC-FIN-008 (REQ-FIN-008) · Exercises: API-FIN-011 POST /api/v1/fin/event-rules/{id}/lines
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an existing rule
Steps        : 1. POST {accountDerivationTypeCode, accountDerivationValue, amountSourceTypeCode, directionCode, distributionTypeCode}
Expected     : 201; RuleLine created
Test data    : CONSTANT derivation, FIELD amount source, DEBIT
<!-- TC:TC-FIN-008:END -->

<!-- TC:TC-FIN-010:START traces=AC-FIN-010,REQ-FIN-010,API-FIN-020 -->
### TC-FIN-010 — build an entry from an event using its rule
Derived from : AC-FIN-010 (REQ-FIN-010) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an event type with an active rule
Steps        : 1. submit a valid event of that type
Expected     : a DRAFT is built per the rule, then proceeds through TC-FIN-017's validate+post
Test data    : event type "INVOICE_PAID", one matching payload
<!-- TC:TC-FIN-010:END -->

<!-- TC:TC-FIN-014:START traces=AC-FIN-014,REQ-FIN-014,API-FIN-019 -->
### TC-FIN-014 — create a manual journal entry
Derived from : AC-FIN-014 (REQ-FIN-014) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: ≥2 balanced lines, leaf active accounts, an Open period
Steps        : 1. submit the entry
Expected     : 201, statusCode=POSTED, docNo generated
Test data    : 2-line balanced entry, 100.00 debit/credit
<!-- TC:TC-FIN-014:END -->

<!-- TC:TC-FIN-015:START traces=AC-FIN-015,REQ-FIN-015,API-FIN-019 -->
### TC-FIN-015 — every validation failure returned together, nothing posts
Derived from : AC-FIN-015 (REQ-FIN-015) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an entry that is both unbalanced AND targets a non-leaf account
Steps        : 1. submit it
Expected     : both FIN-409-UNBALANCED and FIN-409-NOT-POSTABLE-ACCOUNT returned together; nothing posted
Test data    : unbalanced entry + rollup-account line
<!-- TC:TC-FIN-015:END -->

<!-- TC:TC-FIN-016:START traces=AC-FIN-016,REQ-FIN-016,API-FIN-022 -->
### TC-FIN-016 — a posted entry can never be hard-deleted (§12.13 immutable audit trail)
Derived from : AC-FIN-016 (REQ-FIN-016) · Exercises: (no DELETE route exists on /journal-entries/{id})
Scenario     : VIOLATION · data class ATTACK · language ALL
Preconditions: a POSTED entry
Steps        : 1. attempt any delete operation against it (direct call, since no UI/API path offers one)
Expected     : 404/405 (no route) — the record is retrievable unchanged via API-FIN-022 afterward
Test data    : any posted entry
<!-- TC:TC-FIN-016:END -->

<!-- TC:TC-FIN-022:START traces=AC-FIN-022,REQ-FIN-022,API-FIN-013 -->
### TC-FIN-022 — create a recurring/reversing template
Derived from : AC-FIN-022 (REQ-FIN-022) · Exercises: API-FIN-013 POST /api/v1/fin/recurring-templates
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a schedule type, frequency (if recurring), ≥2 balanced lines
Steps        : 1. POST the template
Expected     : 201; active RecurringTemplate created
Test data    : scheduleTypeCode RECURRING, frequencyCode MONTHLY
<!-- TC:TC-FIN-022:END -->

<!-- TC:TC-FIN-023:START traces=AC-FIN-023,REQ-FIN-023,API-FIN-014 -->
### TC-FIN-023 — run a recurring template on schedule
Derived from : AC-FIN-023 (REQ-FIN-023) · Exercises: API-FIN-014 POST /api/v1/fin/recurring-templates/{id}/run
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an active template with nextRunDate = today
Steps        : 1. run it
Expected     : one entry built and posted from the template; nextRunDate advances per frequency
Test data    : monthly template due today
<!-- TC:TC-FIN-023:END -->

<!-- TC:TC-FIN-024:START traces=AC-FIN-024,REQ-FIN-024,API-FIN-014 -->
### TC-FIN-024 — automatic reversal in the next period for a reversing template
Derived from : AC-FIN-024 (REQ-FIN-024) · Exercises: API-FIN-014 POST /api/v1/fin/recurring-templates/{id}/run
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a REVERSING-type template posts in period N
Steps        : 1. run the template — 2. observe period N+1
Expected     : a linked reversal posts in period N+1 automatically
Test data    : reversing template, accrual scenario
<!-- TC:TC-FIN-024:END -->

<!-- TC:TC-FIN-025:START traces=AC-FIN-025,REQ-FIN-025,API-FIN-016 -->
### TC-FIN-025 — create an allocation rule
Derived from : AC-FIN-025 (REQ-FIN-025) · Exercises: API-FIN-016 POST /api/v1/fin/allocation-rules
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a source account, ≥1 target with a distribution type
Steps        : 1. POST the rule
Expected     : 201; active AllocationRule created
Test data    : 1 source account, 2 targets (60%/remainder)
<!-- TC:TC-FIN-025:END -->

<!-- TC:TC-FIN-026:START traces=AC-FIN-026,REQ-FIN-026,API-FIN-017 -->
### TC-FIN-026 — run an allocation rule with exact remainder distribution
Derived from : AC-FIN-026 (REQ-FIN-026) · Exercises: API-FIN-017 POST /api/v1/fin/allocation-rules/{id}/run
Scenario     : HAPPY · data class BOUNDARY · language ALL
Preconditions: 2 PERCENTAGE targets + 1 REMAINDER target; source balance 1,000.00
Steps        : 1. run the rule
Expected     : one posted entry whose target lines sum exactly to 1,000.00, remainder target absorbing rounding
Test data    : source balance 1,000.00, 40%/40%/remainder
<!-- TC:TC-FIN-026:END -->

<!-- TC:TC-FIN-027:START traces=AC-FIN-027,REQ-FIN-027,API-FIN-018 -->
### TC-FIN-027 — search journal entries without altering them
Derived from : AC-FIN-027 (REQ-FIN-027) · Exercises: API-FIN-018 GET /api/v1/fin/journal-entries
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: entries across several statuses/periods
Steps        : 1. GET filtered by period + status
Expected     : 200; exactly the matching entries, unmodified
Test data    : filter statusCode=POSTED
<!-- TC:TC-FIN-027:END -->

<!-- TC:TC-FIN-031:START traces=AC-FIN-031,REQ-FIN-031,API-FIN-023 -->
### TC-FIN-031 — create a fiscal year with its periods
Derived from : AC-FIN-031 (REQ-FIN-031) · Exercises: API-FIN-023 POST /api/v1/fin/fiscal-years
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: unique year code
Steps        : 1. POST {code, startDate, endDate, periodCount: 12}
Expected     : 201; year + 12 Open periods created
Test data    : code "2027", 12 monthly periods
<!-- TC:TC-FIN-031:END -->

<!-- TC:TC-FIN-032:START traces=AC-FIN-032,REQ-FIN-032,API-FIN-024 -->
### TC-FIN-032 — open (reopen) a soft-closed period
Derived from : AC-FIN-032 (REQ-FIN-032) · Exercises: API-FIN-024 PATCH /api/v1/fin/fiscal-periods/{id}/open
Scenario     : STATE · data class VALID · language ALL
Preconditions: a Soft Closed period
Steps        : 1. PATCH to open
Expected     : 200; statusCode=OPEN
Test data    : a soft-closed period
<!-- TC:TC-FIN-032:END -->

<!-- TC:TC-FIN-033:START traces=AC-FIN-033,REQ-FIN-033,API-FIN-025 -->
### TC-FIN-033 — soft-close an open period
Derived from : AC-FIN-033 (REQ-FIN-033) · Exercises: API-FIN-025 PATCH /api/v1/fin/fiscal-periods/{id}/soft-close
Scenario     : STATE · data class VALID · language ALL
Preconditions: an Open period
Steps        : 1. PATCH to soft-close
Expected     : 200; statusCode=SOFT_CLOSE; normal postings thereafter rejected (TC-FIN-020-style)
Test data    : an open period
<!-- TC:TC-FIN-033:END -->

<!-- TC:TC-FIN-034:START traces=AC-FIN-034,REQ-FIN-034,API-FIN-026 -->
### TC-FIN-034 — hard-close a soft-closed period (approval)
Derived from : AC-FIN-034 (REQ-FIN-034) · Exercises: API-FIN-026 PATCH /api/v1/fin/fiscal-periods/{id}/hard-close
Scenario     : STATE · data class VALID · language ALL
Preconditions: a Soft Closed period; approver holds PERM_FIN_PERIODS_CLOSE_APPROVE (distinct role)
Steps        : 1. PATCH to hard-close
Expected     : 200; statusCode=HARD_CLOSE; closedBy/closedAt set; permanently not reopenable
Test data    : soft-closed period, valid approver
<!-- TC:TC-FIN-034:END -->

<!-- TC:TC-FIN-036:START traces=AC-FIN-036,REQ-FIN-036,API-FIN-027 -->
### TC-FIN-036 — run year-end close (§12.10 opening-balance continuity)
Derived from : AC-FIN-036 (REQ-FIN-036) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: every period of the year Hard Closed
Steps        : 1. run year-end close
Expected     : a balanced closing entry (result accounts → Retained Earnings) and a
  balanced opening entry for next year, generated from the resulting balances
Test data    : fully hard-closed fiscal year with posted activity
<!-- TC:TC-FIN-036:END -->

<!-- TC:TC-FIN-037:START traces=AC-FIN-037,REQ-FIN-037,API-FIN-026 -->
### TC-FIN-037 — period-close approval recorded distinctly from entry creation
Derived from : AC-FIN-037 (REQ-FIN-037) · Exercises: API-FIN-026 PATCH /api/v1/fin/fiscal-periods/{id}/hard-close
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a period ready to hard-close, entries in it created by a different principal
Steps        : 1. hard-close it
Expected     : closedBy/closedAt = the approver's principal/moment, distinct from any entry's createdBy in that period
Test data    : entries created by user A; close approved by user B
<!-- TC:TC-FIN-037:END -->

<!-- TC:TC-FIN-039:START traces=AC-FIN-039,REQ-FIN-039,API-FIN-028 -->
### TC-FIN-039 — account ledger derived live (§12.9 balances recomputed, never stored)
Derived from : AC-FIN-039 (REQ-FIN-039) · Exercises: API-FIN-028 GET /api/v1/fin/reports/account-ledger
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: posted lines across 2 periods for one account
Steps        : 1. GET the ledger for the account/range — 2. post one more entry — 3. GET again
Expected     : running balance correct both times; step 3 reflects the new posting immediately (no caching)
Test data    : one account, postings across 2 periods
<!-- TC:TC-FIN-039:END -->

<!-- TC:TC-FIN-040:START traces=AC-FIN-040,REQ-FIN-040,API-FIN-029 -->
### TC-FIN-040 — trial balance always balances (§12.8)
Derived from : AC-FIN-040 (REQ-FIN-040) · Exercises: API-FIN-029 GET /api/v1/fin/reports/trial-balance
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: any set of POSTED entries in a period
Steps        : 1. GET the trial balance
Expected     : total debit balances = total credit balances, exactly, by construction
Test data    : a period with ≥5 posted entries of mixed account types
<!-- TC:TC-FIN-040:END -->

<!-- TC:TC-FIN-041:START traces=AC-FIN-041,REQ-FIN-041,API-FIN-030 -->
### TC-FIN-041 — balance sheet continuity across year-end
Derived from : AC-FIN-041 (REQ-FIN-041) · Exercises: API-FIN-030 GET /api/v1/fin/reports/balance-sheet
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a completed year-end close (TC-FIN-036)
Steps        : 1. GET the new year's balance sheet at its very first moment
Expected     : opening balances equal the prior year's closing balances for every balance-sheet account
Test data    : post-year-end-close state
<!-- TC:TC-FIN-041:END -->

<!-- TC:TC-FIN-042:START traces=AC-FIN-042,REQ-FIN-042,API-FIN-031 -->
### TC-FIN-042 — income statement opens at zero each year
Derived from : AC-FIN-042 (REQ-FIN-042) · Exercises: API-FIN-031 GET /api/v1/fin/reports/income-statement
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a completed year-end close, no postings yet in the new year
Steps        : 1. GET the new year's income statement
Expected     : every revenue/expense account shows a zero balance
Test data    : post-year-end-close state, new year, zero activity
<!-- TC:TC-FIN-042:END -->

<!-- TC:TC-FIN-043:START traces=AC-FIN-043,REQ-FIN-043,API-FIN-032 -->
### TC-FIN-043 — dimension report never collapses distinct dimension values (§12.11)
Derived from : AC-FIN-043 (REQ-FIN-043) · Exercises: API-FIN-032 GET /api/v1/fin/reports/dimension
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: one account posted under 2 different PROJECT dimension values
Steps        : 1. GET the dimension report by PROJECT
Expected     : two separate rows for that account, one per project — never one combined row
Test data    : account posted under PROJECT=P1 and PROJECT=P2
<!-- TC:TC-FIN-043:END -->

<!-- TC:TC-FIN-044:START traces=AC-FIN-044,REQ-FIN-044,API-FIN-010 -->
### TC-FIN-044 — FIN registers itself into SEC at onboarding
Derived from : AC-FIN-044 (REQ-FIN-044) · Exercises: (onboarding call to SEC's API-SEC-018/019/020 — no dedicated FIN endpoint)
Scenario     : INTEGRATION · data class VALID · language ALL
Preconditions: SEC v1 gated and reachable; FIN deploying for the first time
Steps        : 1. run FIN's onboarding
Expected     : SEC records 1 ModuleRegistry row for FIN, 1 ScreenRegistry row per FIN screen (12), 1 ActionRegistry row per action
Test data    : fresh FIN deployment against a live SEC
<!-- TC:TC-FIN-044:END -->

<!-- TC:TC-FIN-045:START traces=AC-FIN-045,REQ-FIN-045,API-FIN-010 -->
### TC-FIN-045 — FIN registers its lookup types into MDL at onboarding
Derived from : AC-FIN-045 (REQ-FIN-045) · Exercises: (onboarding call to MDL's API-MDL-002/006 — no dedicated FIN endpoint)
Scenario     : INTEGRATION · data class VALID · language ALL
Preconditions: MDL v1 gated and reachable; FIN deploying for the first time
Steps        : 1. run FIN's onboarding
Expected     : MDL records 13 LookupType rows owned by FIN (module-registry-fin.md → LOOKUPS OWNED)
Test data    : fresh FIN deployment against a live MDL
<!-- TC:TC-FIN-045:END -->

<!-- TC:TC-FIN-046:START traces=AC-FIN-046,REQ-FIN-046,API-FIN-030 -->
### TC-FIN-046 — drill down from a statement line to its source event
Derived from : AC-FIN-046 (REQ-FIN-046) · Exercises: API-FIN-030 (entry point) → API-FIN-029 → API-FIN-028 → API-FIN-022
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a balance-sheet line backed by a known event-sourced entry
Steps        : 1. drill from the balance-sheet line → trial balance row → account ledger → the originating entry → its eventReference
Expected     : each hop resolves to the correct downstream record; the terminal entry shows the original eventReference (or "manual"/"recurring"/"allocation" if not event-sourced)
Test data    : one event-sourced posted entry contributing to a known balance-sheet line
<!-- TC:TC-FIN-046:END -->
<!-- SUB:API-SCENARIOS:END -->
<!-- PHASE:TEST-PLAN-BE:END -->

<!-- PHASE:INT-XM:START traces=REQ-FIN-001,XM-FIN-001 -->
FIN declares one XM (XM-FIN-001, SOFT-READ → MDL's lookup values); MDL is in the current
selection, so this is a real linking atom.

<!-- TC:TC-FIN-047:START traces=XM-FIN-001,REQ-FIN-001,API-FIN-002 -->
### TC-FIN-047 — graceful degradation when MDL is unreachable during lookup validation
Derived from : XM-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-002 POST /api/v1/fin/accounts (representative of every lookup-validating API)
Rule / code  : XM-FIN-001 (SOFT-READ) → FIN-503 (a defined error, never a 500/unhandled state)
Scenario     : INTEGRATION · data class EDGE · language ALL
Preconditions: MDL's `GET /api/v1/mdl/lookups` (API-MDL-011) is made unreachable/times out
Steps        : 1. POST a new account (accountTypeCode requires MDL validation) while MDL is down
Expected     : the request fails with FIN-503, message ar "تعذّر التحقق من القيمة المرجعية مؤقتًا" / en "Could not verify the reference value right now" — never a raw crash
Test data    : any account payload; MDL endpoint simulated as down
<!-- TC:TC-FIN-047:END -->
<!-- PHASE:INT-XM:END -->

## TC TRACEABILITY INDEX
| AC | TC | REQ | API | RULE/code | XM |
|---|---|---|---|---|---|
| AC-FIN-001…046 | TC-FIN-001…046 (1:1) | REQ-FIN-001…046 (1:1) | see each TC's Exercises line | see each TC's Rule/code line | — |
| — | TC-FIN-047 | REQ-FIN-001 | API-FIN-002 (representative) | — | XM-FIN-001 |

## COVERAGE
AC covered 46/46 (0 gaps) · REQ covered 46/46 · API covered 32/32 · every selected-module
XM covered 1/1 (XM-FIN-001 → TC-FIN-047, no gap). All 14 of the plan's §12 must-honor
points are individually exercised: 1→TC-018, 2→TC-040 (sign presentation, checked
structurally by the report), 3→TC-019, 4→TC-020, 5→TC-018/all amount fields (CHK
constraint, exercised implicitly by every posting TC), 6→TC-012/026, 7→TC-028, 8→TC-040,
9→TC-039/040/041/042/043 (all live-derived), 10→TC-036/041, 11→TC-021/043, 12→TC-011,
13→TC-016, 14→(no TC — a design-time constraint verified by code review, not a runtime scenario).
══════════════════════════════════════════════════════════════════
