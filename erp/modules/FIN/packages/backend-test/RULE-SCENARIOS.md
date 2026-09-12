<!-- source: PHASE:TEST-PLAN-BE / SUB:RULE-SCENARIOS -->
<!-- traces: AC-FIN-002, AC-FIN-006, AC-FIN-009, AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-014, AC-FIN-017, AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-025, AC-FIN-028, AC-FIN-029, AC-FIN-030, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-038, API-FIN-002, API-FIN-003, API-FIN-007, API-FIN-011, API-FIN-016, API-FIN-019, API-FIN-020, API-FIN-021, API-FIN-024, API-FIN-026, API-FIN-027, API-FIN-034, API-FIN-035, REQ-FIN-002, REQ-FIN-005, REQ-FIN-006, REQ-FIN-007, REQ-FIN-009, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-025, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-038 -->
<!-- SUB:RULE-SCENARIOS:START traces=REQ-FIN-002,REQ-FIN-005,REQ-FIN-006,REQ-FIN-007,REQ-FIN-009,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-025,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-038 -->
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
  the ORIGINAL STAYS POSTED (classic reversal — its statusCode is unchanged, never VOID);
  original.reversalEntryId = new.id and new.originalEntryId = original.id;
  every affected account's net balance across the two entries is zero
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
### TC-FIN-030 — reject reversing a non-POSTED (DRAFT) entry
Derived from : AC-FIN-030 (REQ-FIN-030) · Exercises: API-FIN-021 POST /api/v1/fin/journal-entries/{id}/reverse
Rule / code  : RULE-FIN-013 → FIN-409-NOT-POSTED
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an entry that is not POSTED — a DRAFT entry. NOT REACHABLE THROUGH ANY API:
  build, validate and post happen in one transaction and only the POSTED row is ever written
  (the entry is posted before the single save), so no endpoint leaves a DRAFT row behind; the
  row must be seeded directly into FIN_JOURNAL_ENTRY with statusCode=DRAFT for this case to
  exist. (Under classic reversal an already-reversed entry stays POSTED, so it is no longer a
  non-POSTED case; that half of RULE-FIN-013 is now its own guard and its own case, TC-FIN-048.)
Steps        : 1. attempt to reverse it
Expected     : 409 FIN-409-NOT-POSTED
Test data    : a DRAFT (unposted) entry
<!-- TC:TC-FIN-030:END -->

<!-- TC:TC-FIN-048:START traces=AC-FIN-030,REQ-FIN-030,API-FIN-021 -->
### TC-FIN-048 — reject reversing an entry that has already been reversed (double-reversal)
Derived from : AC-FIN-030 (REQ-FIN-030) · Exercises: API-FIN-021 POST /api/v1/fin/journal-entries/{id}/reverse
Rule / code  : RULE-FIN-013 -> FIN-409-ALREADY-REVERSED
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a POSTED entry that has already been reversed once — under classic reversal it
  STAYS POSTED and carries reversalEntryId pointing at its reversal (the linked-entry
  precondition that replaces the old, now unreachable statusCode=VOID one)
Steps        : 1. attempt to reverse the same original entry a second time
Expected     : 409 FIN-409-ALREADY-REVERSED; no second reversal entry is created, and every
  affected account's net balance across the original and its single reversal stays zero
  (a second mirror would leave a net effect of -(original))
Test data    : a posted entry already reversed once, with its reversal link set
<!-- TC:TC-FIN-048:END -->

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
Rule / code  : RULE-FIN-015 → the distinct-permission @PreAuthorize gate → FIN-403-FORBIDDEN
Scenario     : PERMISSION · data class ATTACK · language ALL
Preconditions: a role holding only `PERM_FIN_JOURNAL_ENTRIES_CREATE` (no close-approve permission)
Steps        : 1. that role's user attempts hard-close
Expected     : 403 {code: "FIN-403-FORBIDDEN"}, ar "لا تملك صلاحية المالية المطلوبة لهذه العملية" /
  en "You do not hold the Finance permission required for this operation"; the period is unchanged.
  This is AC-FIN-038 verbatim ("Given a role holding only the entry-creation permission / When that
  role's user attempts the period-close-approval action / Then the system denies it") and the denial
  comes from the ONLY enforcement that exists: FiscalPeriodService.hardClose's
  @PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE) — a permission distinct from
  PERM_FIN_JOURNAL_ENTRIES_CREATE — whose AccessDeniedException is raised inside com.erp.fin.service
  and re-raised by FinForbiddenAdvisor as LocalizedException(FORBIDDEN, FIN_403_FORBIDDEN).
  REVISED 2026-09-12: this Expected previously named FIN-403-SOD-VIOLATION as the primary outcome,
  with FIN-403-FORBIDDEN allowed only as a parenthetical second path. FinSeparationOfDutiesService
  and FiscalPeriodDomain.assertCanHardClose(boolean, boolean) were both deleted by a recorded human
  decision, so FIN-403-SOD-VIOLATION has NO throw site left anywhere in com.erp.fin and can never be
  the answer. AC-FIN-038 itself is untouched and still holds — only the code that answers it moved
Test data    : role with entry-creation only
<!-- TC:TC-FIN-038:END -->

<!-- TC:TC-FIN-049:START traces=AC-FIN-014,REQ-FIN-014,REQ-FIN-017,API-FIN-019 -->
### TC-FIN-049 — reject a period that does not belong to the submitted fiscal year
Derived from : AC-FIN-014 (REQ-FIN-014, REQ-FIN-017) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-017 → FIN-400-PERIOD-NOT-IN-YEAR
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: two fiscal years, FY-A and FY-B, each with its own OPEN periods; an otherwise
  valid balanced 2-line manual payload
Steps        : 1. POST the entry with fiscalYearId = FY-B and periodId = an OPEN period of FY-A
Expected     : 400 FIN-400-PERIOD-NOT-IN-YEAR, ar "الفترة المحددة لا تتبع السنة المالية المحددة" /
  en "The selected period does not belong to the selected fiscal year"; fail-fast, so
  RULE-FIN-006/007/008/009 are never collected; nothing posted and no docNo consumed from either
  year's series
Test data    : fiscalYearId FY-B, periodId = FY-A period 1, docDate inside that period
<!-- TC:TC-FIN-049:END -->

<!-- TC:TC-FIN-050:START traces=AC-FIN-014,REQ-FIN-014,REQ-FIN-017,API-FIN-019 -->
### TC-FIN-050 — reject a document date outside the submitted period's span
Derived from : AC-FIN-014 (REQ-FIN-014, REQ-FIN-017) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-017 → FIN-400-DOCDATE-OUTSIDE-PERIOD
Scenario     : VIOLATION · data class BOUNDARY · language ALL
Preconditions: an OPEN period spanning [startDate, endDate] inside its own fiscal year
Steps        : 1. POST the entry with docDate = endDate + 1 day — 2. repeat with docDate = startDate − 1 day
Expected     : both attempts 400 FIN-400-DOCDATE-OUTSIDE-PERIOD, ar "تاريخ المستند خارج نطاق الفترة المحددة" /
  en "The document date falls outside the selected period"; nothing posted
Test data    : period 2026-02-01..2026-02-28; docDate 2026-03-01, then 2026-01-31
<!-- TC:TC-FIN-050:END -->

<!-- TC:TC-FIN-051:START traces=AC-FIN-014,REQ-FIN-014,REQ-FIN-017,API-FIN-019 -->
### TC-FIN-051 — coherent header accepted at both period boundaries (RULE-FIN-017 satisfied)
Derived from : AC-FIN-014 (REQ-FIN-014, REQ-FIN-017) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-017 → (success path, no error code)
Scenario     : HAPPY · data class BOUNDARY · language ALL
Preconditions: an OPEN period belonging to the submitted fiscal year, spanning [startDate, endDate]
Steps        : 1. POST a balanced entry with docDate = startDate — 2. POST a second one with docDate = endDate
Expected     : both 201, statusCode=POSTED; the inclusive bounds are accepted (the rule rejects
  only dates strictly outside the span)
Test data    : period 2026-02-01..2026-02-28; docDate 2026-02-01, then 2026-02-28
<!-- TC:TC-FIN-051:END -->

<!-- TC:TC-FIN-052:START traces=AC-FIN-009,REQ-FIN-009,API-FIN-011 -->
### TC-FIN-052 — reject a rule line whose remainder marker disagrees with its own type code
Derived from : AC-FIN-009 (REQ-FIN-009) · Exercises: API-FIN-011 POST /api/v1/fin/event-rules/{id}/lines
Rule / code  : RULE-FIN-003 → FIN-422-REMAINDER-MARKER
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an existing event-type rule; `isRemainderFl` (DBF-FIN-103) is the single marker the
  API-FIN-020 builder reads
Steps        : 1. POST a line with amountSourceTypeCode=REMAINDER and isRemainderFl=false —
  2. POST a line with isRemainderFl=true and distributionTypeCode=FIXED, amountSourceTypeCode=FIELD
Expected     : both attempts 422 FIN-422-REMAINDER-MARKER, ar "علامة سطر الباقي لا تتفق مع نوع التوزيع أو مصدر المبلغ لنفس السطر" /
  en "The remainder marker disagrees with the line's own distribution or amount-source type";
  no line stored, so the ambiguity can never reach the builder
Test data    : the two disagreeing line payloads above
<!-- TC:TC-FIN-052:END -->

<!-- TC:TC-FIN-053:START traces=AC-FIN-025,REQ-FIN-025,API-FIN-016 -->
### TC-FIN-053 — reject an allocation target set with the wrong remainder-target count
Derived from : AC-FIN-025 (REQ-FIN-025) · Exercises: API-FIN-016 POST /api/v1/fin/allocation-rules
Rule / code  : RULE-FIN-003 (target half, QR-FIN-016) → FIN-409-REMAINDER-COUNT; a marker/type
  disagreement on a target → FIN-422-REMAINDER-MARKER
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a source account; the rule is submitted with its targets in one call
Steps        : 1. POST a rule with 2 PERCENTAGE targets (40%/40%) and 0 targets marked remainder —
  2. POST a rule with 2 targets both marked isRemainderFl=true —
  3. POST a rule with one target isRemainderFl=true but distributionTypeCode=FIXED
Expected     : 1 and 2 → 409 FIN-409-REMAINDER-COUNT; 3 → 422 FIN-422-REMAINDER-MARKER; no rule
  and no target row persisted in any of the three
Test data    : source account 5000; targets as above
<!-- TC:TC-FIN-053:END -->

<!-- TC:TC-FIN-054:START traces=AC-FIN-012,REQ-FIN-012,API-FIN-020 -->
### TC-FIN-054 — the remainder is computed PER SIDE, never against every line
Derived from : AC-FIN-012 (REQ-FIN-012) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
Rule / code  : RULE-FIN-010 → (success-path computation; a side-blind total would produce a
  negative amount and die on CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE)
Scenario     : HAPPY · data class BOUNDARY · language ALL
Preconditions: an active rule with three lines — DEBIT/FIELD from the event's base amount,
  CREDIT/PERCENTAGE 60%, CREDIT/REMAINDER (isRemainderFl=true)
Steps        : 1. submit the triggering event with baseAmount = 1000.00
Expected     : 201, statusCode=POSTED; the credit percentage line is 600.0000 and the remainder
  line is 400.0000 — the difference between the OPPOSING side's total (debit 1000) and the
  remainder line's own side so far (credit 600), not 1000 − (1000 + 600); the entry balances
  D 1000.00 = C 600.00 + 400.00
Test data    : baseAmount 1000.00; lines DEBIT/FIELD, CREDIT/PERCENTAGE 60%, CREDIT/REMAINDER
<!-- TC:TC-FIN-054:END -->

<!-- TC:TC-FIN-055:START traces=AC-FIN-012,REQ-FIN-012,API-FIN-020 -->
### TC-FIN-055 — reject a distribution whose remainder computes to zero or less
Derived from : AC-FIN-012 (REQ-FIN-012) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
  (same code on API-FIN-017 POST /api/v1/fin/allocation-rules/{id}/run)
Rule / code  : RULE-FIN-010 → FIN-422-REMAINDER-NOT-POSITIVE
Scenario     : VIOLATION · data class BOUNDARY · language ALL
Preconditions: an active rule whose non-remainder lines on the remainder's own side already
  equal the opposing side's total — DEBIT/FIELD 1000, CREDIT/PERCENTAGE 100%, CREDIT/REMAINDER
Steps        : 1. submit the triggering event with baseAmount = 1000.00
Expected     : 422 FIN-422-REMAINDER-NOT-POSITIVE, ar "سطر الباقي يُحسب كفرق ويجب أن يكون موجبًا؛ السطور الأخرى تستهلك المبلغ بالكامل" /
  en "The remainder line is computed as a difference and must be positive; the other lines
  already consume the full amount" — never the generic DATA_INTEGRITY_VIOLATION from
  CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE; nothing posted
Test data    : baseAmount 1000.00; CREDIT/PERCENTAGE 100% + CREDIT/REMAINDER
<!-- TC:TC-FIN-055:END -->

<!-- TC:TC-FIN-056:START traces=AC-FIN-036,REQ-FIN-036,API-FIN-027 -->
### TC-FIN-056 — RULE-FIN-008's year-end exemption: CLOSING/OPENING post into non-Open periods
Derived from : AC-FIN-036 (REQ-FIN-036) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
Rule / code  : RULE-FIN-008 (year-end carve-out) → (success path); RULE-FIN-006/007/009 still
  apply to both generated entries in full
Scenario     : STATE · data class EDGE · language ALL
Preconditions: a caller holding PERM_FIN_PERIODS_CLOSE_APPROVE — post-V30 the bootstrap `admin`
  qualifies (see TC-FIN-059), and the caller may also hold PERM_FIN_JOURNAL_ENTRIES_CREATE, which is
  no longer disqualifying (see TC-FIN-061); an account with is_retained_earnings_fl = TRUE (set as
  data — no endpoint sets it), every period of the year HARD_CLOSE, and an adjacent successor year
  whose startDate = this year's endDate + 1. REVISED 2026-09-12: this block previously read
  "KNOWN-BLOCKED ENDPOINT … a user holding FIN_CLOSE_APPROVER and no role carrying
  PERM_FIN_JOURNAL_ENTRIES_CREATE" — the endpoint is no longer blocked and the exclusion is no
  longer required
Steps        : 1. run year-end close as that approver
Expected     : 201; the CLOSING entry posts into the year's LAST period even though that period is
  HARD_CLOSE, and the OPENING entry posts into the successor year's first period — neither is
  rejected with FIN-409-PERIOD-NOT-OPEN; a manual entry (API-FIN-019) carrying
  journalTypeCode="CLOSING" into the same period is still rejected 409 FIN-409-PERIOD-NOT-OPEN,
  so the exemption cannot be bought by a caller-supplied journal type
Test data    : a fully hard-closed year with posted result-account activity
<!-- TC:TC-FIN-056:END -->

<!-- TC:TC-FIN-057:START traces=AC-FIN-002,REQ-FIN-002,API-FIN-003 -->
### TC-FIN-057 — marking a childless account as a leaf is accepted (RULE-FIN-001 satisfied)
Derived from : AC-FIN-002 (REQ-FIN-002) · Exercises: API-FIN-003 PUT /api/v1/fin/accounts/{id}
Rule / code  : RULE-FIN-001 → (success path, no error code)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an account with zero child accounts and isLeafFl=false
Steps        : 1. PUT {nameAr, nameEn, isLeafFl: true}
Expected     : 200 `AccountResponse` with isLeafFl=true; the account then accepts a posting
  (the mirror of TC-FIN-019)
Test data    : a childless rollup account
<!-- TC:TC-FIN-057:END -->

<!-- TC:TC-FIN-058:START traces=AC-FIN-002,REQ-FIN-002,API-FIN-002 -->
### TC-FIN-058 — reject a child under a parent that is still marked as accepting direct posting
Derived from : AC-FIN-002 (REQ-FIN-002) · Exercises: API-FIN-002 POST /api/v1/fin/accounts
Rule / code  : RULE-FIN-001 (create trigger, QR-FIN-006) → FIN-409-PARENT-NOT-LEAF-ELIGIBLE
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an existing account with isLeafFl=true and no children
Steps        : 1. POST a new account naming it as parentAccountId — 2. demote the parent through
  API-FIN-003 (isLeafFl=false) — 3. repeat step 1
Expected     : 1. 409 FIN-409-PARENT-NOT-LEAF-ELIGIBLE and no child row created — the parent's
  isLeafFl is NEVER flipped automatically — 3. 201, the child is created once the parent has been
  demoted explicitly
Test data    : parent "1000" isLeafFl=true; child "1001"
<!-- TC:TC-FIN-058:END -->

<!-- TC:TC-FIN-059:START traces=AC-FIN-034,REQ-FIN-034,REQ-FIN-038,API-FIN-026 -->
### TC-FIN-059 — hard-close succeeds for any holder of the close-approval permission (RULE-FIN-015 satisfied)
Derived from : AC-FIN-034 (REQ-FIN-034, REQ-FIN-038) · Exercises: API-FIN-026 PATCH /api/v1/fin/fiscal-periods/{id}/hard-close
Rule / code  : RULE-FIN-015 → (success path); the distinct-permission @PreAuthorize gate is the whole enforcement
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: a SOFT_CLOSE period, and a caller holding PERM_FIN_PERIODS_CLOSE_APPROVE. On a fresh
  database that is now satisfied out of the box: V30__fin_sys_admin_close_approve_grant.sql grants
  that action to SYS_ADMIN — reversing V25's deliberate exclusion — and the bootstrap `admin` holds
  SYS_ADMIN, so `admin` can run this directly. The V27 role FIN_CLOSE_APPROVER (module FIN, screen
  FIN_PERIODS, exactly PERM_FIN_PERIODS_VIEW + PERM_FIN_PERIODS_CLOSE_APPROVE) still exists and a
  user assigned it passes identically — run the scenario as EITHER principal, the outcome is the
  same. Nothing on this path reads who else holds PERM_FIN_JOURNAL_ENTRIES_CREATE, so the caller may
  hold it too (that is TC-FIN-061)
Steps        : 1. hard-close the period
Expected     : 200, statusCode=HARD_CLOSE, closedBy = the calling principal
  (SecurityContextHelper.getCurrentUsername()) and closedAt set; the period is thereafter not
  reopenable (FiscalPeriodDomain.assertCanReopen). Never 403.
  REVISED 2026-09-12: this scenario previously opened "KNOWN-BLOCKED ENDPOINT — this cannot succeed
  on a fresh deployment", required a SECOND SEC user whose role union excluded
  PERM_FIN_JOURNAL_ENTRIES_CREATE, and pointed at TC-FIN-060 for a fresh-deployment
  403 FIN-403-SOD-VIOLATION. All three premises are void: the global user-set disjointness check
  (FinSeparationOfDutiesService + FiscalPeriodDomain.assertCanHardClose) was deleted by a recorded
  human decision, V30 grants the permission to SYS_ADMIN, and the endpoint is no longer blocked on a
  fresh deployment. TC-FIN-056, TC-FIN-084, TC-FIN-085, TC-FIN-086 and TC-FIN-102 all reference
  "TC-FIN-059's setup" — it is now simply "a caller holding PERM_FIN_PERIODS_CLOSE_APPROVE"
Test data    : the bootstrap `admin` (SYS_ADMIN, post-V30) or a user holding FIN_CLOSE_APPROVER; a soft-closed period
<!-- TC:TC-FIN-059:END -->

<!-- TC:TC-FIN-060:START traces=AC-FIN-038,REQ-FIN-038,API-FIN-027 -->
### TC-FIN-060 — the same AC-FIN-038 denial on year-end close, the second gated endpoint
Derived from : AC-FIN-038 (REQ-FIN-038) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
  (TC-FIN-038 is the identical assertion on API-FIN-026)
Rule / code  : RULE-FIN-015 → the distinct-permission @PreAuthorize gate → FIN-403-FORBIDDEN
Scenario     : PERMISSION · data class ATTACK · language ALL
Preconditions: a role holding PERM_FIN_JOURNAL_ENTRIES_CREATE but NOT
  PERM_FIN_PERIODS_CLOSE_APPROVE; an otherwise fully eligible fiscal year (every period HARD_CLOSE,
  an account marked is_retained_earnings_fl, an adjacent successor year) so that nothing but the
  permission can account for the refusal
Steps        : 1. that role's user runs year-end close
Expected     : 403 {code: "FIN-403-FORBIDDEN"}, ar "لا تملك صلاحية المالية المطلوبة لهذه العملية" /
  en "You do not hold the Finance permission required for this operation"; nothing is posted, the
  year stays OPEN and every period keeps its status. The denial is raised by
  FiscalYearService.yearEndClose's @PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE) — the same distinct
  permission FiscalPeriodService.hardClose carries — and reaches the wire as FIN's own catalog code
  because FinForbiddenAdvisor intercepts AccessDeniedException raised inside com.erp.fin.service.
  Because @PreAuthorize fires before the method body, the answer is 403 and never FIN-404-YEAR,
  FIN-409-INVALID-TRANSITION, FIN-409-PERIODS-NOT-CLOSED or FIN-404-ACCOUNT.
  REWRITTEN 2026-09-12. This id previously asserted "close fails when NOBODY holds close-approval",
  expecting 403 FIN-403-SOD-VIOLATION from an EMPTY approver set. That scenario is now impossible
  twice over: V30__fin_sys_admin_close_approve_grant.sql grants the permission to SYS_ADMIN so the
  set is not empty, and the code that inspected user sets at all
  (FinSeparationOfDutiesService + FiscalPeriodDomain.assertCanHardClose) was deleted by a recorded
  human decision. The id is kept — never renumbered — and re-pointed at the one real, previously
  UNCOVERED assertion in the same area: AC-FIN-038's denial on API-FIN-027, which no other TC made
Test data    : a role with entry-creation only; a fully eligible fiscal year
<!-- TC:TC-FIN-060:END -->

<!-- TC:TC-FIN-061:START traces=AC-FIN-038,REQ-FIN-038,API-FIN-027 -->
### TC-FIN-061 — a user holding BOTH permissions CAN close: RULE-FIN-015 is satisfied by the distinct permission, not by disjoint user sets
Derived from : REQ-FIN-038, satisfied direction (AC-FIN-038's denial direction is TC-FIN-038 on
  API-FIN-026 and TC-FIN-060 on API-FIN-027) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
  (the same permission gates API-FIN-026)
Rule / code  : RULE-FIN-015 → (success path). No separation-of-duties fact is read anywhere;
  FIN-403-SOD-VIOLATION has no throw site
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: the bootstrap `admin`, who holds SYS_ADMIN and therefore BOTH
  PERM_FIN_JOURNAL_ENTRIES_CREATE (granted by V25) and PERM_FIN_PERIODS_CLOSE_APPROVE (granted by
  V30) — the two permissions' holders deliberately overlap in ONE user, which is the exact state
  that used to be refused. Plus TC-FIN-056's year-end fixture: every period HARD_CLOSE, one account
  marked is_retained_earnings_fl, an adjacent successor year
Steps        : 1. run year-end close as `admin`
Expected     : 201 `YearEndCloseResponse` carrying a CLOSING and an OPENING entry; the year becomes
  CLOSED and every period YEAR_END_CLOSE. Assert EXPLICITLY that the response is not a 403 and
  carries no FIN-403-SOD-VIOLATION. FiscalYearService.yearEndClose runs findOrThrow →
  FiscalYearDomain.assertCanYearEndClose → FiscalPeriodDomain.assertHardClosedForYearEnd per period
  → successor year → Retained Earnings account → post; there is no separation-of-duties step
  anywhere in that sequence, and FiscalPeriodDomain carries an explicit "there is deliberately NO
  assertCanHardClose(...) method here" comment in its place.
  REVISED 2026-09-12 — EXACTLY INVERTED, and kept rather than retired because the inverted assertion
  is the regression guard for the change. This scenario previously asserted
  403 FIN-403-SOD-VIOLATION "raised BEFORE the year's status, the all-periods check, the successor
  year and the Retained Earnings lookup". That check enforced GLOBAL user-set disjointness — if any
  single user in the system held both codes, the close was refused for EVERY caller — which no REQ,
  AC or RULE asks for: RULE-FIN-015's own Data source line records that FIN has no field to read for
  it, and AC-FIN-038 names SEC's own mechanism. It was deleted by a recorded human decision and V30
  then deliberately put both codes on SYS_ADMIN, so the old assertion would fail today
Test data    : `admin` holding SYS_ADMIN (both permission codes, post-V30); a fully hard-closed year with an adjacent successor
<!-- TC:TC-FIN-061:END -->

<!-- TC:TC-FIN-062:START traces=AC-FIN-038,REQ-FIN-038,API-FIN-026 -->
### TC-FIN-062 — the gateway rule resolves the two-word action CLOSE_APPROVE
Derived from : AC-FIN-038 (REQ-FIN-038) · Exercises: API-FIN-026 PATCH /api/v1/fin/fiscal-periods/{id}/hard-close
Rule / code  : platform gateway convention (every non-VIEW permission needs a granted VIEW on the
  SAME SCREEN) → the resulting @PreAuthorize denial inside com.erp.fin.service is re-raised by
  FinForbiddenAdvisor as the catalog's FIN-403-FORBIDDEN row
Scenario     : PERMISSION · data class ATTACK · language ALL
Preconditions: a role granted PERM_FIN_PERIODS_CLOSE_APPROVE on screen FIN_PERIODS but WITHOUT the
  screen's PERM_FIN_PERIODS_VIEW gateway row; and, for the passing half, FIN_CLOSE_APPROVER, which
  holds both
Steps        : 1. call hard-close as the gateway-less role's user — 2. call it as a FIN_CLOSE_APPROVER
  holder (TC-FIN-059's setup)
Expected     : 1. the authority is stripped during resolution and the call answers 403 with
  {code: "FIN-403-FORBIDDEN"} — assert the FIN catalog code, NOT the platform `ACCESS_DENIED`:
  FiscalPeriodService.hardClose's @PreAuthorize denial is an AccessDeniedException raised inside
  com.erp.fin.service, which FinForbiddenAdvisor intercepts and re-raises as
  LocalizedException(FORBIDDEN, FIN_403_FORBIDDEN) before GlobalExceptionHandler sees it. The
  message resolves through the shared MessageSource, so it is localized per Accept-Language:
  ar "لا تملك صلاحية المالية المطلوبة لهذه العملية" /
  en "You do not hold the Finance permission required for this operation" — 2. the authority survives and
  the call reaches the RULE-FIN-015 check, proving the gateway is matched against the screen's own
  registry rows and not by splitting the code at its last underscore (which would demand a
  non-existent PERM_FIN_PERIODS_CLOSE_VIEW)
Test data    : one role with CLOSE_APPROVE only; FIN_CLOSE_APPROVER for the contrast
<!-- TC:TC-FIN-062:END -->

<!-- TC:TC-FIN-092:START traces=AC-FIN-013,REQ-FIN-013,REQ-FIN-007,API-FIN-034,API-FIN-020 -->
### TC-FIN-092 — deactivating a rule makes RULE-FIN-005's failure reachable for the first time
Derived from : AC-FIN-013 (REQ-FIN-013, REQ-FIN-007) · Exercises: API-FIN-034 PUT /api/v1/fin/event-rules/{id}/deactivate, then API-FIN-020 POST /api/v1/fin/journal-entries/from-event
Rule / code  : RULE-FIN-005 → FIN-404-NO-ACTIVE-RULE
Scenario     : STATE · data class EDGE · language ALL
Preconditions: one ACTIVE EventTypeRule for eventTypeCode "INVOICE_PAID" (TC-FIN-073's setup, which
  needs TC-FIN-090's host-supplied ACCOUNTING_EVENT_TYPE value first) and a caller holding
  PERM_FIN_RULES_UPDATE. Until API-FIN-034 landed nothing could clear
  FIN_EVENT_TYPE_RULE.IS_ACTIVE_FL (DBF-FIN-093), so THIS transition — an event type that HAD a
  working rule and no longer has an active one — could not be staged through the API at all;
  TC-FIN-013 reaches the same code only from an event type that never had a rule
Steps        : 1. POST an event of type "INVOICE_PAID" — 2. PUT /api/v1/fin/event-rules/{id}/deactivate
  on that rule — 3. POST a second event of the same type, with a fresh eventReference
Expected     : 1. 201, the entry is built from the rule — 2. 200 `EventTypeRuleResponse` with
  isActiveFl=false — 3. 404 FIN-404-NO-ACTIVE-RULE, ar "لا توجد قاعدة نشطة لهذا النوع من الأحداث" /
  en "No active rule exists for this event type"; no entry created and the step-1 entry untouched.
  The deactivated row still exists and is still returned by API-FIN-009, so the miss comes from the
  flag and not from a deleted row — the resolution is
  `findByEventTypeCodeAndIsActiveFl(code, TRUE)`, fail-fast before any other check
Test data    : eventTypeCode "INVOICE_PAID"; two distinct eventReferences
<!-- TC:TC-FIN-092:END -->

<!-- TC:TC-FIN-093:START traces=AC-FIN-021,REQ-FIN-021,REQ-FIN-005,API-FIN-035,API-FIN-019 -->
### TC-FIN-093 — RULE-FIN-009's inactive-value branch, now reachable end to end
Derived from : AC-FIN-021 (REQ-FIN-021, REQ-FIN-005) · Exercises: API-FIN-035 PUT /api/v1/fin/dimensions/values/{id}/deactivate, then API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-009 → FIN-409-INVALID-DIMENSION
Scenario     : STATE · data class EDGE · language ALL
Preconditions: dimension "REGION" with an ACTIVE value "NORTH"; an OPEN period; a caller holding
  PERM_FIN_DIMENSIONS_UPDATE (registered AND granted to SYS_ADMIN by V28). TC-FIN-021 already
  states the inactive half of RULE-FIN-009, but before API-FIN-035 no endpoint could clear
  FIN_DIMENSION_VALUE.IS_ACTIVE_FL (DBF-FIN-029), so its precondition could only be staged by
  writing the flag as data — this TC is the API-only route to the same branch
Steps        : 1. POST a balanced entry whose line cites REGION/NORTH — 2. PUT
  /api/v1/fin/dimensions/values/{id}/deactivate on NORTH — 3. POST an otherwise identical entry
  citing REGION/NORTH again
Expected     : 1. 201 — 2. 200 `DimensionValueResponse` with isActiveFl=false — 3. 409
  FIN-409-INVALID-DIMENSION, ar "قيمة البُعد غير صالحة" / en "The dimension value is invalid",
  the offending line and dimension named; nothing posted. Deactivation is forward-only in effect:
  it blocks NEW lines and never retracts the step-1 entry, which still reads back POSTED
Test data    : dimension "REGION", value "NORTH"; one 2-line balanced payload submitted twice
<!-- TC:TC-FIN-093:END -->

<!-- TC:TC-FIN-103:START traces=AC-FIN-021,REQ-FIN-021,API-FIN-019 -->
### TC-FIN-103 — reject a value belonging to a DIFFERENT dimension (§12.11, RULE-FIN-009's other half)
Derived from : AC-FIN-021 (REQ-FIN-021) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Rule / code  : RULE-FIN-009 → FIN-409-INVALID-DIMENSION
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: two dimensions — "REGION" holding value "NORTH", "PROJECT" holding value "P100" —
  with BOTH values ACTIVE, so the inactive condition cannot be what fires. Read as the sibling of
  TC-FIN-021: that TC drives RULE-FIN-009's inactive branch, this one drives its wrong-dimension
  branch, and only the two together cover the guard on both of its conditions
Steps        : 1. submit a balanced entry whose line carries a dimension tag stating dimensionId =
  REGION with dimensionValueId = P100 — an active value owned by PROJECT, not by REGION
Expected     : 409 FIN-409-INVALID-DIMENSION, ar "قيمة البُعد غير صالحة" / en "The dimension value
  is invalid"; nothing posted. ASSERT THE CODE, NOT THE BRANCH — the two conditions are ONE guard
  returning ONE code: `checkUsableOnLine` tests `!active || dimensionPk == null ||
  !dimensionPk.equals(statedDimensionPk)` and answers FIN-409-INVALID-DIMENSION either way, with
  the value's own `code` as the message argument and a registered message text that carries no
  placeholder, so the rendered ar/en strings are identical too. The branches are indistinguishable
  on the wire BY DESIGN, not by accident; do not write an assertion that tries to tell them apart,
  and do not read a pass here as proof the wrong-dimension path was the one taken unless the
  fixture really does leave both values active — which is why that is a stated precondition.
  Both ids are resolved independently BEFORE the pairing check and each answers this same
  FIN-409-INVALID-DIMENSION (not a 404) when the id itself is unknown, so the fixture must cite two
  REAL ids or it proves nothing about this branch
Test data    : dimensions "REGION"/"PROJECT"; active values "NORTH" (REGION) and "P100" (PROJECT);
  the tag pairs REGION with P100
<!-- TC:TC-FIN-103:END -->
<!-- SUB:RULE-SCENARIOS:END -->
