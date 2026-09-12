# BACKEND TEST PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Scope : project (modules FIN, MDL, SEC)
Sources: srs-fin.md v1 · backend-execution-plan-fin.md v1 · registry-srs-fin.md v1 · registry-db-fin.md v1
Framework: agnostic. REDUCED: no. Open ADRs: 0 new (ADR-FIN-001 unaffected).
TC count: 109 ids — 107 (module scope, phase TEST-PLAN-BE) · 2 (phase INT-XM). 108 are IN FORCE;
TC-FIN-091 is RETIRED (see below). TC-FIN-109 was ADDED 2026-09-12 (API-SCENARIOS) to close the
FIN-422-INVALID-PERCENTAGE-VALUE coverage gap this revision found; it is the highest id. FIN declares exactly ONE XM: XM-FIN-001, FIN → MDL. XM-FIN-002
(FIN → SEC) no longer exists.
Extended after ALIGN-BE with TC-FIN-049..091, then with TC-FIN-092..103 for the API-FIN-033/034/035
delivery, the report-404 change and RULE-FIN-009's previously uncovered wrong-dimension branch, then
with TC-FIN-104..108 for the API-FIN-036/037 deactivate delivery.
REVISED 2026-09-12 for two recorded human decisions already delivered in code. No id was renumbered
and no TC was added or removed; every change is a rewrite in place:
  (1) THE SEPARATION-OF-DUTIES CHECK WAS DELETED. FinSeparationOfDutiesService and
      FiscalPeriodDomain.assertCanHardClose(boolean, boolean) are gone, and
      V30__fin_sys_admin_close_approve_grant.sql grants PERM_FIN_PERIODS_CLOSE_APPROVE to SYS_ADMIN,
      so the bootstrap `admin` can hard-close and year-end-close directly. FIN-403-SOD-VIOLATION now
      has NO throw site. TC-FIN-038 re-pointed at FIN-403-FORBIDDEN; TC-FIN-059 lost its
      KNOWN-BLOCKED premise; TC-FIN-060 rewritten as AC-FIN-038's denial on API-FIN-027 (previously
      uncovered); TC-FIN-061 INVERTED into the success case; TC-FIN-091 RETIRED outright.
  (2) THE RUN PATHS ARE NOW GATED ON THE ACTIVE FLAG. RecurringTemplateDomain.assertCanRun() and
      AllocationRuleDomain.assertCanRun() answer FIN-409-NOT-ACTIVE (Status.CONFLICT → 409), so
      TC-FIN-106 and TC-FIN-107 were FLIPPED from "still runs and still posts" to the refusal. No
      RULE-FIN-* states that gate — it is a recorded human decision, not a requirement that was
      always there, and the scenarios say so.
(TC-FIN-062's Expected was rewritten in place earlier for the now-localized 403 body, then again once
FinForbiddenAdvisor made that body carry FIN-403-FORBIDDEN instead of the platform ACCESS_DENIED.)
══════════════════════════════════════════════════════════════════

<!-- PHASE:TEST-PLAN-BE:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,REQ-FIN-025,REQ-FIN-026,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043,REQ-FIN-044,REQ-FIN-045,REQ-FIN-046 -->

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

<!-- SUB:API-SCENARIOS:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,REQ-FIN-004,REQ-FIN-005,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,REQ-FIN-025,REQ-FIN-026,REQ-FIN-027,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-036,REQ-FIN-037,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043,REQ-FIN-044,REQ-FIN-045,REQ-FIN-046 -->
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
Derived from : AC-FIN-003 (REQ-FIN-003) · Exercises: API-FIN-004 PUT /api/v1/fin/accounts/{id}/deactivate
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active account
Steps        : 1. PUT /{id}/deactivate (no body) — 2. attempt to post to it (TC-FIN-019 pattern)
Expected     : 1. 200 `AccountResponse`, isActiveFl=false — 2. rejected (FIN-409-NOT-POSTABLE-ACCOUNT)
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
Expected     : a linked reversal posts in period N+1 automatically; the period-N entry
  stays POSTED (classic reversal), so the accrual and its reversal net to zero across N/N+1
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
Derived from : AC-FIN-027 (REQ-FIN-027) · Exercises: API-FIN-018 POST /api/v1/fin/journal-entries/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: entries across several statuses/periods
Steps        : 1. POST /search with `JournalEntrySearchRequest` filtering period + status
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

<!-- TC:TC-FIN-063:START traces=AC-FIN-001,REQ-FIN-001,API-FIN-001 -->
### TC-FIN-063 — search accounts
Derived from : AC-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-001 POST /api/v1/fin/accounts/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: several accounts of mixed accountTypeCode and isActiveFl
Steps        : 1. POST `AccountSearchRequest` {code LIKE "10", accountTypeCode "ASSET", isActiveFl true, paging}
Expected     : 200 `Page<AccountResponse>` containing exactly the matching rows, nameAr/nameEn returned, nothing modified
Test data    : accounts 1000/1001 ASSET active, 4000 REVENUE active, 1002 ASSET inactive
<!-- TC:TC-FIN-063:END -->

<!-- TC:TC-FIN-064:START traces=AC-FIN-001,REQ-FIN-001,API-FIN-001 -->
### TC-FIN-064 — an unrecognized sort field is rejected on every search endpoint
Derived from : AC-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-001 (representative of API-FIN-005, 008, 009, 012, 015, 018 — the same shared search builder)
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: none beyond an authenticated caller holding the screen's VIEW permission
Steps        : 1. POST a search whose paging sort names a field not on the request's allowed list
Expected     : 400 FIN-400-INVALID-SORT, ar "حقل الترتيب غير معروف" / en "Unrecognized sort field"; no page returned
Test data    : sort "dropTable"
<!-- TC:TC-FIN-064:END -->

<!-- TC:TC-FIN-065:START traces=AC-FIN-004,REQ-FIN-004,API-FIN-005 -->
### TC-FIN-065 — search dimensions
Derived from : AC-FIN-004 (REQ-FIN-004) · Exercises: API-FIN-005 POST /api/v1/fin/dimensions/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: ≥2 dimensions
Steps        : 1. POST `DimensionSearchRequest` {code LIKE "PRO", paging}
Expected     : 200 `Page<DimensionResponse>`, only the matching dimensions
Test data    : dimensions "PROJECT", "REGION"
<!-- TC:TC-FIN-065:END -->

<!-- TC:TC-FIN-066:START traces=AC-FIN-005,REQ-FIN-005,API-FIN-008 -->
### TC-FIN-066 — search dimension values, and reject an unknown parent dimension
Derived from : AC-FIN-005 (REQ-FIN-005) · Exercises: API-FIN-008 POST /api/v1/fin/dimensions/values/search
Scenario     : HAPPY + VIOLATION · data class VALID/INVALID · language ALL
Preconditions: dimension "PROJECT" with ≥2 values; dimensionId is carried in the body filters, never as a path variable
Steps        : 1. POST {dimensionId = PROJECT, code LIKE "P1", paging} — 2. POST the same with a dimensionId that does not exist
Expected     : 1. 200 `Page<DimensionValueResponse>`, only that dimension's matching values —
  2. 404 FIN-404-DIMENSION, ar "البُعد غير موجود" / en "Dimension not found"
Test data    : PROJECT values P100/P200; unknown dimensionId 999999
<!-- TC:TC-FIN-066:END -->

<!-- TC:TC-FIN-067:START traces=AC-FIN-007,REQ-FIN-007,API-FIN-009 -->
### TC-FIN-067 — search event-type rules
Derived from : AC-FIN-007 (REQ-FIN-007) · Exercises: API-FIN-009 POST /api/v1/fin/event-rules/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: ≥1 active and ≥1 inactive rule
Steps        : 1. POST {eventTypeCode EXACT, isActiveFl true, paging}
Expected     : 200 `Page<EventTypeRuleResponse>` with only the active rule for that event type
Test data    : eventTypeCode "INVOICE_PAID"
<!-- TC:TC-FIN-067:END -->

<!-- TC:TC-FIN-068:START traces=AC-FIN-022,REQ-FIN-022,API-FIN-012 -->
### TC-FIN-068 — search recurring templates
Derived from : AC-FIN-022 (REQ-FIN-022) · Exercises: API-FIN-012 POST /api/v1/fin/recurring-templates/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: one RECURRING and one REVERSING template
Steps        : 1. POST {scheduleTypeCode "REVERSING", isActiveFl true, paging}
Expected     : 200 `Page<RecurringTemplateResponse>` with only the reversing template
Test data    : two templates as above
<!-- TC:TC-FIN-068:END -->

<!-- TC:TC-FIN-069:START traces=AC-FIN-025,REQ-FIN-025,API-FIN-015 -->
### TC-FIN-069 — search allocation rules
Derived from : AC-FIN-025 (REQ-FIN-025) · Exercises: API-FIN-015 POST /api/v1/fin/allocation-rules/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: ≥2 allocation rules with different source accounts
Steps        : 1. POST {sourceAccountId EXACT, isActiveFl true, paging}
Expected     : 200 `Page<AllocationRuleResponse>` with only that source account's rules
Test data    : two rules, one per source account
<!-- TC:TC-FIN-069:END -->

<!-- TC:TC-FIN-070:START traces=AC-FIN-001,REQ-FIN-001,API-FIN-002 -->
### TC-FIN-070 — reject a duplicate account code
Derived from : AC-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-002 POST /api/v1/fin/accounts
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: account code "1000" already exists
Steps        : 1. POST a second account with code "1000"
Expected     : 409 FIN-409-ACCOUNT-DUP, ar "رمز الحساب مستخدم بالفعل" / en "Account code already in use"; no second row
Test data    : code "1000"
<!-- TC:TC-FIN-070:END -->

<!-- TC:TC-FIN-071:START traces=AC-FIN-002,REQ-FIN-002,REQ-FIN-003,API-FIN-003 -->
### TC-FIN-071 — unknown account id on update, deactivate and ledger
Derived from : AC-FIN-002 (REQ-FIN-002, REQ-FIN-003) · Exercises: API-FIN-003 PUT /api/v1/fin/accounts/{id}, API-FIN-004 PUT /{id}/deactivate, API-FIN-028 GET /reports/account-ledger
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an id that matches no account row
Steps        : 1. PUT the update — 2. PUT the deactivate — 3. GET the account ledger for it
Expected     : all three 404 FIN-404-ACCOUNT, ar "الحساب غير موجود" / en "Account not found"
Test data    : accountId 999999
<!-- TC:TC-FIN-071:END -->

<!-- TC:TC-FIN-072:START traces=AC-FIN-004,REQ-FIN-004,API-FIN-006 -->
### TC-FIN-072 — reject a duplicate dimension code
Derived from : AC-FIN-004 (REQ-FIN-004) · Exercises: API-FIN-006 POST /api/v1/fin/dimensions
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: dimension "PROJECT" exists
Steps        : 1. POST a second dimension with code "PROJECT"
Expected     : 409 FIN-409-DIMENSION-DUP, ar "رمز البُعد مستخدم بالفعل" / en "Dimension code already in use"; no second row
Test data    : code "PROJECT"
<!-- TC:TC-FIN-072:END -->

<!-- TC:TC-FIN-073:START traces=AC-FIN-007,REQ-FIN-007,API-FIN-010 -->
### TC-FIN-073 — reject a second active rule for the same event type
Derived from : AC-FIN-007 (REQ-FIN-007) · Exercises: API-FIN-010 POST /api/v1/fin/event-rules
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an active rule already exists for eventTypeCode "INVOICE_PAID" (whose value must
  first be added to MDL's ACCOUNTING_EVENT_TYPE — see TC-FIN-090)
Steps        : 1. POST another rule for the same event type
Expected     : 409 FIN-409-RULE-DUP, ar "يوجد بالفعل قاعدة نشطة لهذا النوع" / en "An active rule already exists for this event type"
Test data    : eventTypeCode "INVOICE_PAID"
<!-- TC:TC-FIN-073:END -->

<!-- TC:TC-FIN-074:START traces=AC-FIN-008,REQ-FIN-008,API-FIN-011 -->
### TC-FIN-074 — unknown event-type rule id when adding a line
Derived from : AC-FIN-008 (REQ-FIN-008) · Exercises: API-FIN-011 POST /api/v1/fin/event-rules/{id}/lines
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an id that matches no EventTypeRule row
Steps        : 1. POST a valid line payload under that id
Expected     : 404 FIN-404-RULE, ar "القاعدة غير موجودة" / en "Rule not found" — never FIN-404-TEMPLATE
Test data    : ruleId 999999
<!-- TC:TC-FIN-074:END -->

<!-- TC:TC-FIN-075:START traces=AC-FIN-022,REQ-FIN-022,API-FIN-013 -->
### TC-FIN-075 — a recurring template without a frequency is rejected
Derived from : AC-FIN-022 (REQ-FIN-022) · Exercises: API-FIN-013 POST /api/v1/fin/recurring-templates
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: none
Steps        : 1. POST a template with scheduleTypeCode=RECURRING and no frequencyCode —
  2. POST the same with scheduleTypeCode=REVERSING and no frequencyCode
Expected     : 1. 400 FIN-400-MISSING-FREQUENCY, ar "يلزم تحديد التكرار للقالب المتكرر" /
  en "A frequency is required for a recurring template" — 2. 201, a reversing template needs none
Test data    : the two payloads above
<!-- TC:TC-FIN-075:END -->

<!-- TC:TC-FIN-076:START traces=AC-FIN-023,REQ-FIN-023,API-FIN-014 -->
### TC-FIN-076 — unknown recurring template id on run
Derived from : AC-FIN-023 (REQ-FIN-023) · Exercises: API-FIN-014 POST /api/v1/fin/recurring-templates/{id}/run
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an id that matches no RecurringTemplate row
Steps        : 1. run it
Expected     : 404 FIN-404-TEMPLATE, ar "القالب المتكرر غير موجود" / en "Recurring template not found" —
  the entity named is the template, never FIN-404-RULE
Test data    : templateId 999999
<!-- TC:TC-FIN-076:END -->

<!-- TC:TC-FIN-077:START traces=AC-FIN-026,REQ-FIN-026,API-FIN-017 -->
### TC-FIN-077 — unknown allocation rule id on run
Derived from : AC-FIN-026 (REQ-FIN-026) · Exercises: API-FIN-017 POST /api/v1/fin/allocation-rules/{id}/run
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an id that matches no AllocationRule row
Steps        : 1. run it
Expected     : 404 FIN-404-ALLOCATION-RULE, ar "قاعدة التوزيع غير موجودة" / en "Allocation rule not found"
Test data    : allocationRuleId 999999
<!-- TC:TC-FIN-077:END -->

<!-- TC:TC-FIN-078:START traces=AC-FIN-010,REQ-FIN-010,API-FIN-020 -->
### TC-FIN-078 — MAPPING account derivation fails loudly
Derived from : AC-FIN-010 (REQ-FIN-010) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an active rule holding one line with accountDerivationTypeCode=MAPPING (a stored
  configuration; db-script-fin.md declares no mapping store)
Steps        : 1. submit a triggering event of that type — 2. repeat with the line switched to
  CONSTANT, and again with DIRECT
Expected     : 1. 422 FIN-422-MAPPING-UNSUPPORTED, ar "يستخدم هذا السطر اشتقاق الحساب عبر جدول المطابقة وهو غير متاح حاليًا" /
  en "This rule line uses mapping-based account derivation, which is not available yet"; nothing
  posted and no account silently resolved — 2. both CONSTANT and DIRECT still build and post normally
Test data    : one MAPPING line, then the CONSTANT/DIRECT variants
<!-- TC:TC-FIN-078:END -->

<!-- TC:TC-FIN-079:START traces=AC-FIN-016,REQ-FIN-016,REQ-FIN-027,API-FIN-022 -->
### TC-FIN-079 — read one entry with its lines, and reject an unknown entry id
Derived from : AC-FIN-016 (REQ-FIN-016, REQ-FIN-027) · Exercises: API-FIN-022 GET /api/v1/fin/journal-entries/{id}
Scenario     : HAPPY + VIOLATION · data class VALID/INVALID · language ALL
Preconditions: a POSTED entry with 2 lines, one carrying a dimension tag
Steps        : 1. GET it — 2. GET an id that matches no entry — 3. GET the same unknown id on
  API-FIN-021 reverse
Expected     : 1. 200 `JournalEntryResponse` with docNo, statusCode=POSTED, nested lines and their
  dimensions — 2 and 3. 404 FIN-404-ENTRY, ar "القيد غير موجود" / en "Entry not found"
Test data    : a posted 2-line entry; entryId 999999
<!-- TC:TC-FIN-079:END -->

<!-- TC:TC-FIN-080:START traces=AC-FIN-031,REQ-FIN-031,API-FIN-023 -->
### TC-FIN-080 — reject a duplicate fiscal year code
Derived from : AC-FIN-031 (REQ-FIN-031) · Exercises: API-FIN-023 POST /api/v1/fin/fiscal-years
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: fiscal year code "2027" exists
Steps        : 1. POST a second year with code "2027"
Expected     : 409 FIN-409-YEAR-DUP, ar "رمز السنة المالية مستخدم بالفعل" / en "Fiscal year code already in use";
  no year and no periods generated
Test data    : code "2027"
<!-- TC:TC-FIN-080:END -->

<!-- TC:TC-FIN-081:START traces=AC-FIN-031,REQ-FIN-031,API-FIN-023 -->
### TC-FIN-081 — twelve periods are calendar months; any other count falls back to an even day split
Derived from : AC-FIN-031 (REQ-FIN-031) · Exercises: API-FIN-023 POST /api/v1/fin/fiscal-years
Scenario     : HAPPY · data class BOUNDARY · language ALL
Preconditions: none
Steps        : 1. POST {code "2027", startDate 2027-01-01, endDate 2027-12-31, periodCount 12} —
  2. POST {code "2028Q", startDate 2028-01-01, endDate 2028-12-31, periodCount 4} —
  3. POST a 12-period year whose span does not start on the first of a month
Expected     : 1. 201 with 12 OPEN periods, period N spanning the 1st to the LAST day of the Nth
  calendar month (period 2 = 2027-02-01..2027-02-28, not a 31-day block), nameAr/nameEn = that
  month's own Arabic/English name from the platform's locale data — 2 and 3. the even-day-split
  fallback: contiguous blocks, the first (totalDays mod periodCount) one day longer, the last
  period ending exactly on the year's endDate, named "الفترة N" / "Period N"; no day belongs to two periods
Test data    : the three payloads above
<!-- TC:TC-FIN-081:END -->

<!-- TC:TC-FIN-082:START traces=AC-FIN-032,REQ-FIN-032,API-FIN-024 -->
### TC-FIN-082 — unknown period id on every period transition
Derived from : AC-FIN-032 (REQ-FIN-032) · Exercises: API-FIN-024 open, API-FIN-025 soft-close, API-FIN-026 hard-close
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an id that matches no FiscalPeriod row
Steps        : 1. PATCH /{id}/open — 2. PATCH /{id}/soft-close — 3. PATCH /{id}/hard-close
Expected     : all three 404 FIN-404-PERIOD, ar "الفترة غير موجودة" / en "Period not found"
Test data    : periodId 999999
<!-- TC:TC-FIN-082:END -->

<!-- TC:TC-FIN-083:START traces=AC-FIN-033,REQ-FIN-033,API-FIN-025 -->
### TC-FIN-083 — reject soft-closing a period that is not Open
Derived from : AC-FIN-033 (REQ-FIN-033) · Exercises: API-FIN-025 PATCH /api/v1/fin/fiscal-periods/{id}/soft-close
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a period already in SOFT_CLOSE, and another in HARD_CLOSE
Steps        : 1. soft-close the SOFT_CLOSE one — 2. soft-close the HARD_CLOSE one
Expected     : both 409 FIN-409-INVALID-TRANSITION, ar "لا يمكن تنفيذ هذا الانتقال من الحالة الحالية" /
  en "This transition is not allowed from the current status"; neither period's statusCode changes
Test data    : one soft-closed and one hard-closed period
<!-- TC:TC-FIN-083:END -->

<!-- TC:TC-FIN-084:START traces=AC-FIN-036,REQ-FIN-036,API-FIN-027 -->
### TC-FIN-084 — year-end close refused while any period is not Hard Closed
Derived from : AC-FIN-036 (REQ-FIN-036) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: TC-FIN-059's close-approver setup (otherwise the call stops at 403 first); an OPEN
  fiscal year with 11 HARD_CLOSE periods and 1 still SOFT_CLOSE
Steps        : 1. run year-end close
Expected     : 409 FIN-409-PERIODS-NOT-CLOSED, ar "يجب إغلاق كل الفترات إغلاقًا صارمًا أولًا" /
  en "Every period must be hard-closed first"; nothing posted, the year stays OPEN
Test data    : one period left soft-closed
<!-- TC:TC-FIN-084:END -->

<!-- TC:TC-FIN-085:START traces=AC-FIN-036,REQ-FIN-036,API-FIN-027 -->
### TC-FIN-085 — year-end close is not re-runnable, and needs a real year and successor
Derived from : AC-FIN-036 (REQ-FIN-036) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
Scenario     : STATE · data class EDGE · language ALL
Preconditions: TC-FIN-059's close-approver setup; a year already closed by TC-FIN-056
Steps        : 1. run year-end close again on that CLOSED year — 2. run it on an id matching no
  fiscal year — 3. run it on an eligible year for which NO year exists whose startDate =
  this year's endDate + 1 day
Expected     : 1. 409 FIN-409-INVALID-TRANSITION (the year's own status guard, never the misleading
  FIN-409-PERIODS-NOT-CLOSED the first run's YEAR_END_CLOSE transitions would otherwise raise) —
  2 and 3. 404 FIN-404-YEAR, ar "السنة المالية غير موجودة" / en "Fiscal year not found"; the
  successor is resolved by date adjacency only (a DERIVED decision — no successor column exists)
Test data    : a CLOSED year; yearId 999999; an eligible year with no adjacent successor
<!-- TC:TC-FIN-085:END -->

<!-- TC:TC-FIN-086:START traces=AC-FIN-036,REQ-FIN-036,API-FIN-027 -->
### TC-FIN-086 — Retained Earnings is resolved from the marker, and its absence is reported
Derived from : AC-FIN-036 (REQ-FIN-036) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
Scenario     : STATE · data class EDGE · language ALL
Preconditions: TC-FIN-059's close-approver setup; an eligible year with a successor. The marker
  FIN_ACCOUNT.is_retained_earnings_fl (DBF-FIN-147) is READ-ONLY on every endpoint — API-FIN-002/003
  cannot set it — so it must be set as data directly, and the partial unique index
  UQ_FIN_ACCOUNT_RETAINED_EARNINGS caps it at one marked account
Steps        : 1. run year-end close with NO account marked — 2. mark one EQUITY account and re-run —
  3. attempt to set a second account's marker directly in the database
Expected     : 1. 404 FIN-404-ACCOUNT (no invented code) and nothing posted — 2. 201; every
  result account's balance closes into the marked account, which is the only one credited/debited
  by the CLOSING entry, and the result accounts stand at zero afterwards — 3. the index rejects the
  second marked row, so the account can never be ambiguous
Test data    : EQUITY account "3900" marked as Retained Earnings
<!-- TC:TC-FIN-086:END -->

<!-- TC:TC-FIN-087:START traces=AC-FIN-014,REQ-FIN-014,API-FIN-019 -->
### TC-FIN-087 — docNo format, per-fiscal-year counter and immutability
Derived from : AC-FIN-014 (REQ-FIN-014) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries, read back through API-FIN-022
Scenario     : HAPPY · data class BOUNDARY · language ALL
Preconditions: two fiscal years, codes "2026" and "2027", both with OPEN periods
Steps        : 1. post the first entry of FY2026 — 2. post two more in FY2026, one of them through
  API-FIN-020 (event) and one through API-FIN-021 (a reversal) — 3. post the first entry of FY2027 —
  4. attempt to submit docNo in a create payload
Expected     : 1. docNo = "JV-2026-000001" — 2. "JV-2026-000002" and "JV-2026-000003": ONE counter
  per fiscal year across every journal type, never segmented by journalTypeCode — 3. "JV-2027-000001",
  the counter restarts per year — 4. the field is not part of any create/update request contract, so
  a submitted docNo is ignored and the generated value is returned; the value never changes on any
  later read
Test data    : years "2026"/"2027"
<!-- TC:TC-FIN-087:END -->

<!-- TC:TC-FIN-088:START traces=AC-FIN-014,REQ-FIN-014,API-FIN-019 -->
### TC-FIN-088 — concurrent creates in one fiscal year never collide on docNo
Derived from : AC-FIN-014 (REQ-FIN-014) · Exercises: API-FIN-019 POST /api/v1/fin/journal-entries
Scenario     : HAPPY · data class EDGE · language ALL
Preconditions: one fiscal year with an OPEN period; docNo allocation is serialized by a
  PESSIMISTIC_WRITE lock on the owning FIN_FISCAL_YEAR row, held to commit
Steps        : 1. issue N concurrent valid create requests against the same fiscal year (N ≥ 10)
Expected     : all N succeed with 201 and N DISTINCT sequential docNos; no request answers an
  opaque 409 DATA_INTEGRITY_VIOLATION from UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO, which stays an
  unreachable backstop
Test data    : 10 identical balanced 2-line payloads fired in parallel
<!-- TC:TC-FIN-088:END -->

<!-- TC:TC-FIN-089:START traces=AC-FIN-043,REQ-FIN-043,API-FIN-032 -->
### TC-FIN-089 — dimension report rejects an unknown dimension
Derived from : AC-FIN-043 (REQ-FIN-043) · Exercises: API-FIN-032 GET /api/v1/fin/reports/dimension
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an id that matches no Dimension row
Steps        : 1. GET the dimension report for it
Expected     : 404 FIN-404-DIMENSION, ar "البُعد غير موجود" / en "Dimension not found"; no rows returned
Test data    : dimensionId 999999
<!-- TC:TC-FIN-089:END -->

<!-- TC:TC-FIN-090:START traces=AC-FIN-045,REQ-FIN-045,API-FIN-010,XM-FIN-001 -->
### TC-FIN-090 — the lookup seed: 13 FIN-owned types, 36 values, two types deliberately empty
Derived from : AC-FIN-045 (REQ-FIN-045) · Exercises: API-FIN-010 POST /api/v1/fin/event-rules (the
  one create blocked by an empty type) and API-FIN-002 (the representative validated create)
Scenario     : INTEGRATION · data class EDGE · language ALL
Preconditions: a fresh database with the FIN lookup seed applied; FIN's module row exists in SEC
Steps        : 1. read MDL's lookup types owned by FIN — 2. POST an event-type rule with any
  eventTypeCode — 3. add one ACCOUNTING_EVENT_TYPE value through MDL's lookup administration and
  repeat step 2 — 4. POST an account with accountTypeCode "ASSET"
Expected     : 1. exactly 13 FIN-owned types and 36 active values; ACCOUNTING_EVENT_TYPE and
  PAYMENT_METHOD exist as TYPES with ZERO values on purpose (no artifact enumerates any), so they
  return an empty active-value list rather than MDL's type-not-found — 2. 400 FIN-400-INVALID-LOOKUP,
  because no active value exists yet: adding the host's own event types is a documented deployment
  step, not a defect — 3. 201 — 4. 201, every other lookup-backed create works out of the box
Test data    : the seeded 13 keys; one host-supplied ACCOUNTING_EVENT_TYPE value
<!-- TC:TC-FIN-090:END -->

<!-- TC:TC-FIN-094:START traces=AC-FIN-031,REQ-FIN-031,API-FIN-033 -->
### TC-FIN-094 — search fiscal periods, with and without the OPTIONAL fiscalYearId
Derived from : AC-FIN-031 (REQ-FIN-031) · Exercises: API-FIN-033 POST /api/v1/fin/fiscal-periods/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: two fiscal years, each with its 12 generated periods (API-FIN-023, TC-FIN-081), at
  least one OPEN in each; a caller holding PERM_FIN_PERIODS_VIEW. fiscalYearId travels inside the
  body's filters list and is read by the child parent-id extractor, never as a path variable
Steps        : 1. POST {filters: [fiscalYearId = year A], paging} — 2. POST {filters: [statusCode =
  "OPEN"], paging} with NO fiscalYearId — 3. POST {filters: [fiscalYearId = year A, statusCode =
  "OPEN"], sort periodNo asc}
Expected     : 1. 200 `Page<FiscalPeriodResponse>` holding only year A's 12 periods, nameAr/nameEn
  returned — 2. 200 listing the OPEN periods of BOTH years: omitting the parent id is a legitimate
  "all periods" request, NOT the 404 its sibling child search answers. API-FIN-033 diverges from
  API-FIN-008 (TC-FIN-066, which 404s FIN-404-DIMENSION on a missing dimensionId) on purpose,
  because this endpoint is the only way a client that did not create the year in the same session
  can discover a period id at all — 3. 200, both filters ANDed, ordered by periodNo. Nothing is
  modified by any of the three
Test data    : years "2026"/"2027", 12 periods each; statusCode "OPEN"
<!-- TC:TC-FIN-094:END -->

<!-- TC:TC-FIN-095:START traces=AC-FIN-031,REQ-FIN-031,API-FIN-033 -->
### TC-FIN-095 — fiscal-period search rejects an unrecognized sort field and an ungranted caller
Derived from : AC-FIN-031 (REQ-FIN-031) · Exercises: API-FIN-033 POST /api/v1/fin/fiscal-periods/search
Scenario     : VIOLATION + PERMISSION · data class INVALID/ATTACK · language ALL
Preconditions: periods exist; one caller holds PERM_FIN_PERIODS_VIEW and one holds no FIN_PERIODS
  action grant at all. The endpoint's allowed sort/filter set is fiscalPeriodPk, periodNo, nameAr,
  nameEn, startDate, endDate, statusCode, createdAt — fiscalYearId is deliberately NOT on it (it is
  the `fiscalYear` association, ANDed in as an explicit join, not a flat path), and neither are
  closedBy/closedAt
Steps        : 1. POST a search sorted by "closedAt" — 2. POST a search sorted by "fiscalYearId" —
  3. POST a valid search as the ungranted caller
Expected     : 1 and 2. 400 FIN-400-INVALID-SORT, ar "حقل الترتيب غير معروف" / en "Unrecognized sort
  field"; no page returned — the whitelist check runs BEFORE the shared pageable builder, which
  would otherwise drop the field silently and return a differently ordered page with nothing saying
  so — 3. 403 carrying {code: "FIN-403-FORBIDDEN"} — FIN's own catalog code, never the platform
  `ACCESS_DENIED`: FiscalPeriodService.search's @PreAuthorize on PERM_FIN_PERIODS_VIEW denies inside
  com.erp.fin.service, so FinForbiddenAdvisor translates it — with the message localized per
  Accept-Language: ar "لا تملك صلاحية المالية المطلوبة لهذه العملية" /
  en "You do not hold the Finance permission required for this operation"
Test data    : sort fields "closedAt" and "fiscalYearId"; a user with no FIN_PERIODS action grant
<!-- TC:TC-FIN-095:END -->

<!-- TC:TC-FIN-096:START traces=AC-FIN-007,REQ-FIN-007,API-FIN-034 -->
### TC-FIN-096 — deactivate an event-type rule, and reject an unknown rule id
Derived from : AC-FIN-007 (REQ-FIN-007) · Exercises: API-FIN-034 PUT /api/v1/fin/event-rules/{id}/deactivate
Scenario     : HAPPY + VIOLATION · data class VALID/INVALID · language ALL
Preconditions: an active EventTypeRule; a caller holding PERM_FIN_RULES_UPDATE — pre-existing, the
  same permission API-FIN-011 uses, so this endpoint needed no migration. The base path is
  /api/v1/fin/event-rules, NOT /event-type-rules
Steps        : 1. PUT /{id}/deactivate with no body — 2. PUT /{id}/deactivate again on the same id —
  3. PUT /{id}/deactivate on an id matching no EventTypeRule row
Expected     : 1. 200 `EventTypeRuleResponse` with isActiveFl=false; the row is not deleted and is
  still returned by API-FIN-009 — 2. 200 again, still isActiveFl=false: no rule guards the
  transition and the catalog registers no code for re-deactivating, so the endpoint is idempotent —
  3. 404 FIN-404-RULE, ar "القاعدة غير موجودة" / en "Rule not found", never FIN-404-TEMPLATE.
  No `activate` counterpart exists on this or any FIN entity, so step 1 is not reversible through
  the API
Test data    : an active rule for "INVOICE_PAID"; ruleId 999999
<!-- TC:TC-FIN-096:END -->

<!-- TC:TC-FIN-097:START traces=AC-FIN-007,REQ-FIN-007,API-FIN-034,API-FIN-010 -->
### TC-FIN-097 — deactivating a rule does NOT free its event type for a replacement
Derived from : AC-FIN-007 (REQ-FIN-007) · Exercises: API-FIN-034 PUT /api/v1/fin/event-rules/{id}/deactivate, then API-FIN-010 POST /api/v1/fin/event-rules
Scenario     : STATE · data class EDGE · language ALL
Preconditions: exactly one rule, active, for eventTypeCode "INVOICE_PAID". Asserted as a KNOWN
  LIMITATION, not as desired behaviour: the create path guards uniqueness with
  `existsByEventTypeCode`, which is NOT scoped to the active flag, so the deactivated row still
  satisfies the one-rule-per-event-type check
Steps        : 1. PUT /{id}/deactivate — 2. POST a NEW rule for "INVOICE_PAID"
Expected     : 1. 200, isActiveFl=false — 2. 409 FIN-409-RULE-DUP, ar "يوجد بالفعل قاعدة نشطة لهذا
  النوع" / en "An active rule already exists for this event type" — the message says "active" while
  the blocking row is inactive, which is exactly the limitation this TC pins. The event type is
  therefore left with no usable rule and no API route to configure a replacement, and
  TC-FIN-092's FIN-404-NO-ACTIVE-RULE becomes its permanent answer. If the uniqueness check is
  later narrowed to active rows, this TC must flip to expecting 201 — the current 409 is recorded
  as as-built behaviour, not endorsed as the contract
Test data    : eventTypeCode "INVOICE_PAID"; one deactivated rule, one replacement payload
<!-- TC:TC-FIN-097:END -->

<!-- TC:TC-FIN-098:START traces=AC-FIN-005,REQ-FIN-005,API-FIN-035 -->
### TC-FIN-098 — deactivate a dimension value, and reject an unknown dimension-value id
Derived from : AC-FIN-005 (REQ-FIN-005) · Exercises: API-FIN-035 PUT /api/v1/fin/dimensions/values/{id}/deactivate
Scenario     : HAPPY + VIOLATION · data class VALID/INVALID · language ALL
Preconditions: dimension "REGION" with active value "NORTH"; a caller holding
  PERM_FIN_DIMENSIONS_UPDATE — the FIRST UPDATE-class permission on screen FIN_DIMENSIONS,
  registered AND granted to SYS_ADMIN by V28__fin_dimensions_update_action.sql (the earlier grant
  migration grants by a SELECT over the registry and has already run, so registration alone would
  have left the endpoint ungrantable)
Steps        : 1. PUT /api/v1/fin/dimensions/values/{id}/deactivate with no body — 2. POST
  /api/v1/fin/dimensions/values/search for that dimension — 3. PUT the same path with an id
  matching no DimensionValue row — 4. repeat step 1 as a caller holding only the screen's VIEW and
  CREATE grants
Expected     : 1. 200 `DimensionValueResponse` with isActiveFl=false; the row is not deleted — 2.
  200, the value is still returned by the search with only its flag changed — 3. 404
  FIN-404-DIMVALUE, ar "قيمة البُعد غير موجودة" / en "Dimension value not found" — its own row,
  never the parent's FIN-404-DIMENSION, which would say the DIMENSION was missing when the VALUE
  was — 4. 403 {code: "FIN-403-FORBIDDEN"} — DimensionValueService.deactivate's @PreAuthorize on
  PERM_FIN_DIMENSIONS_UPDATE denies inside com.erp.fin.service and FinForbiddenAdvisor translates
  it, so the body carries FIN's own code, never the platform `ACCESS_DENIED`:
  ar "لا تملك صلاحية المالية المطلوبة لهذه العملية" /
  en "You do not hold the Finance permission required for this operation".
  There is deliberately no deactivate on the PARENT Dimension
  and no `activate` counterpart; neither is a gap
Test data    : dimension "REGION", value "NORTH"; dimensionValueId 999999
<!-- TC:TC-FIN-098:END -->

<!-- TC:TC-FIN-099:START traces=AC-FIN-040,REQ-FIN-040,API-FIN-029 -->
### TC-FIN-099 — trial balance 404s on a SUPPLIED unknown periodId, and still serves an omitted one
Derived from : AC-FIN-040 (REQ-FIN-040) · Exercises: API-FIN-029 GET /api/v1/fin/reports/trial-balance
Scenario     : VIOLATION + HAPPY · data class INVALID/VALID · language ALL
Preconditions: posted entries across ≥2 periods; a caller holding PERM_FIN_TRIAL_BALANCE_VIEW.
  periodId is an OPTIONAL narrowing on this report — unlike API-FIN-030/031's REQUIRED fiscalYearId
Steps        : 1. GET ?periodId=999999 — 2. GET with no periodId at all — 3. GET ?periodId=<a real
  period id>
Expected     : 1. 404 FIN-404-PERIOD, ar "الفترة غير موجودة" / en "Period not found"; no report
  body — the id is resolved only BECAUSE it was supplied — 2. 200, the trial balance across ALL
  periods, still balancing (TC-FIN-040): omitting the parameter is a valid request and must NEVER
  answer 404 — a scenario asserting 404 on an omitted periodId would be wrong — 3. 200, narrowed to
  that period
Test data    : periodId 999999; one real period id
<!-- TC:TC-FIN-099:END -->

<!-- TC:TC-FIN-100:START traces=AC-FIN-041,REQ-FIN-041,API-FIN-030 -->
### TC-FIN-100 — balance sheet 404s on an unknown fiscalYearId instead of an all-zero report
Derived from : AC-FIN-041 (REQ-FIN-041) · Exercises: API-FIN-030 GET /api/v1/fin/reports/balance-sheet
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a caller holding PERM_FIN_BALANCE_SHEET_VIEW. fiscalYearId is REQUIRED on this
  report and is resolved BEFORE any aggregation runs
Steps        : 1. GET ?fiscalYearId=999999 — 2. GET ?fiscalYearId=999999&asOfDate=2026-06-30
Expected     : both 404 FIN-404-YEAR, ar "السنة المالية غير موجودة" / en "Fiscal year not found";
  no report body. Specifically NOT a 200 carrying an all-zero balance sheet: an unknown year and a
  real year with no activity used to be indistinguishable to the caller, and keeping them apart is
  the whole point of this TC. The optional asOfDate does not change the answer — the year is
  resolved first
Test data    : fiscalYearId 999999
<!-- TC:TC-FIN-100:END -->

<!-- TC:TC-FIN-101:START traces=AC-FIN-042,REQ-FIN-042,API-FIN-031 -->
### TC-FIN-101 — income statement 404s on an unknown fiscal year and on an unknown period bound
Derived from : AC-FIN-042 (REQ-FIN-042) · Exercises: API-FIN-031 GET /api/v1/fin/reports/income-statement
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: one real fiscal year with periods; a caller holding PERM_FIN_INCOME_STATEMENT_VIEW.
  fiscalYearId is REQUIRED; fromPeriodId/toPeriodId are OPTIONAL narrowings that already raised
  their own 404 before this change
Steps        : 1. GET ?fiscalYearId=999999 — 2. GET ?fiscalYearId=<real>&fromPeriodId=999999 —
  3. GET ?fiscalYearId=<real>&toPeriodId=999999 — 4. GET ?fiscalYearId=<real> with neither bound
Expected     : 1. 404 FIN-404-YEAR, ar "السنة المالية غير موجودة" / en "Fiscal year not found",
  raised before any aggregation and never a 200 all-zero report — 2 and 3. 404 FIN-404-PERIOD,
  ar "الفترة غير موجودة" / en "Period not found"; the year is resolved FIRST, so a request wrong in
  both answers FIN-404-YEAR — 4. 200, the whole year: omitting both bounds is valid
Test data    : fiscalYearId 999999; fromPeriodId/toPeriodId 999999; one real year
<!-- TC:TC-FIN-101:END -->

<!-- TC:TC-FIN-102:START traces=AC-FIN-036,REQ-FIN-036,API-FIN-027,API-FIN-019 -->
### TC-FIN-102 — a dormant fiscal year still closes, posting two EMPTY entries (reviewed and kept)
Derived from : AC-FIN-036 (REQ-FIN-036) · Exercises: API-FIN-027 POST /api/v1/fin/fiscal-years/{id}/year-end-close
Scenario     : STATE · data class EDGE · language ALL
Preconditions: TC-FIN-056's full setup (a caller holding PERM_FIN_PERIODS_CLOSE_APPROVE — no
  longer required to be free of the entry-creation permission, see TC-FIN-061 — an account marked
  is_retained_earnings_fl, every period HARD_CLOSE, an adjacent successor year) — but over a fiscal
  year with NO posted lines at all, so neither a result account nor a balance-sheet account carries
  a non-zero net
Steps        : 1. run year-end close on that dormant year — 2. read both returned entries
  (API-FIN-022) — 3. POST a manual entry with lines: [] (API-FIN-019)
Expected     : 1. 201 `YearEndCloseResponse` carrying BOTH a CLOSING and an OPENING entry, each
  with an EMPTY line set and each consuming a docNo from its own fiscal year's sequence; the year
  becomes CLOSED and every period YEAR_END_CLOSE — 2. both read back POSTED with zero lines. This
  is a reviewed and deliberately kept outcome, not a defect: the closing and opening line builders
  skip every zero-net account, and RULE-FIN-006 treats 0 = 0 as balanced, so the run satisfies
  AC-FIN-036 literally — 3. 400 {code: "VALIDATION_ERROR"} with a fieldErrors entry for `lines`
  (the request contract's own @NotEmpty), which is what makes the empty-entry shape reachable ONLY
  through the internal year-end path and never from a caller
Test data    : a fully hard-closed fiscal year with zero posted entries; an adjacent successor year
<!-- TC:TC-FIN-102:END -->

<!-- TC:TC-FIN-104:START traces=AC-FIN-022,REQ-FIN-022,API-FIN-036 -->
### TC-FIN-104 — deactivate a recurring template, and reject an unknown template id
Derived from : AC-FIN-022 (REQ-FIN-022) · Exercises: API-FIN-036 PUT /api/v1/fin/recurring-templates/{id}/deactivate
Scenario     : HAPPY + VIOLATION + PERMISSION · data class VALID/INVALID/ATTACK · language ALL
Preconditions: an active RecurringTemplate created through API-FIN-013 with THREE lines; a caller
  holding PERM_FIN_RECURRING_TEMPLATES_UPDATE — pre-existing, seeded by V24__fin_security_seed.sql
  as the FIN_RECURRING_TEMPLATES/UPDATE action and already the gate on API-FIN-014, so this
  endpoint needed no migration and registers no new error code; and a second caller holding no
  FIN_RECURRING_TEMPLATES action grant at all. The base path is /api/v1/fin/recurring-templates and
  the verb is PUT, matching API-FIN-034/035
Steps        : 1. PUT /{id}/deactivate with no body — 2. PUT /{id}/deactivate again on the same id —
  3. PUT /{id}/deactivate on an id matching no FIN_RECURRING_TEMPLATE row — 4. PUT /{id}/deactivate
  as the ungranted caller
Expected     : 1. 200 `RecurringTemplateResponse` with isActiveFl=false AND lineCount=3, all three
  entries present in `lines` — the service re-reads the template's children before mapping, so the
  aggregate is never misreported as having none; the row is not deleted and is still returned by
  API-FIN-012 — 2. 200 again, still isActiveFl=false: no rule guards the transition and the catalog
  registers no code for re-deactivating, so the endpoint is idempotent — 3. 404 FIN-404-TEMPLATE,
  ar "القالب المتكرر غير موجود" / en "Recurring template not found", never FIN-404-RULE — 4. 403
  carrying {code: "FIN-403-FORBIDDEN"} — FIN's own catalog code, never the platform `ACCESS_DENIED`:
  RecurringTemplateService.deactivate's @PreAuthorize denies inside com.erp.fin.service, so
  FinForbiddenAdvisor translates it — with the message localized per Accept-Language:
  ar "لا تملك صلاحية المالية المطلوبة لهذه العملية" /
  en "You do not hold the Finance permission required for this operation".
  No `activate` counterpart exists on this or any FIN entity, so step 1 is NOT reversible through
  the API — ENT-FIN-011's own activate() helper still has zero callers
Test data    : a MONTHLY RECURRING template with 3 lines; templateId 999999; a user with no
  FIN_RECURRING_TEMPLATES action grant
<!-- TC:TC-FIN-104:END -->

<!-- TC:TC-FIN-105:START traces=AC-FIN-025,REQ-FIN-025,API-FIN-037 -->
### TC-FIN-105 — deactivate an allocation rule, and reject an unknown rule id
Derived from : AC-FIN-025 (REQ-FIN-025) · Exercises: API-FIN-037 PUT /api/v1/fin/allocation-rules/{id}/deactivate
Scenario     : HAPPY + VIOLATION + PERMISSION · data class VALID/INVALID/ATTACK · language ALL
Preconditions: an active AllocationRule created through API-FIN-016 with THREE targets (two
  PERCENTAGE plus one remainder); a caller holding PERM_FIN_ALLOCATION_RULES_UPDATE — pre-existing,
  seeded by V24__fin_security_seed.sql as the FIN_ALLOCATION_RULES/UPDATE action and already the
  gate on API-FIN-017, so this endpoint needed no migration and registers no new error code; and a
  second caller holding no FIN_ALLOCATION_RULES action grant at all
Steps        : 1. PUT /{id}/deactivate with no body — 2. PUT /{id}/deactivate again on the same id —
  3. PUT /{id}/deactivate on an id matching no FIN_ALLOCATION_RULE row — 4. PUT /{id}/deactivate as
  the ungranted caller
Expected     : 1. 200 `AllocationRuleResponse` with isActiveFl=false AND targetCount=3, all three
  entries present in `targets` — the service re-reads the rule's children before mapping, the same
  point API-FIN-036 makes for lineCount; the row is not deleted and is still returned by
  API-FIN-015 — 2. 200 again, still isActiveFl=false: idempotent for the same reason as
  API-FIN-036, and RULE-FIN-003 is NOT consulted here, so a rule whose remainder-target set would
  fail at run time can still be retired — 3. 404 FIN-404-ALLOCATION-RULE, ar "قاعدة التوزيع غير موجودة" /
  en "Allocation rule not found" — 4. 403 carrying {code: "FIN-403-FORBIDDEN"}, localized per
  Accept-Language exactly as in TC-FIN-104; AllocationRuleService.deactivate's @PreAuthorize denies
  inside com.erp.fin.service and FinForbiddenAdvisor translates it.
  No `activate` counterpart exists, so step 1 is NOT reversible through the API
Test data    : an allocation rule with 3 targets; allocationRuleId 999999; a user with no
  FIN_ALLOCATION_RULES action grant
<!-- TC:TC-FIN-105:END -->

<!-- TC:TC-FIN-106:START traces=AC-FIN-023,REQ-FIN-023,API-FIN-036,API-FIN-014 -->
### TC-FIN-106 — a deactivated recurring template is REFUSED at run time (FIN-409-NOT-ACTIVE)
Derived from : AC-FIN-023 (REQ-FIN-023) · Exercises: API-FIN-036 PUT /api/v1/fin/recurring-templates/{id}/deactivate then API-FIN-014 POST /api/v1/fin/recurring-templates/{id}/run
Rule / code  : RECORDED HUMAN DECISION, not a RULE-FIN-* → FIN-409-NOT-ACTIVE (Status.CONFLICT → 409)
Scenario     : STATE · data class EDGE · language ALL
Preconditions: TC-FIN-104's template, whose nextRunDate falls inside a period that exists and is
  OPEN and whose lines reference postable accounts, so the run has no unrelated reason to fail — the
  409 must be provably the active-flag gate and nothing else. ONE caller performs both calls:
  API-FIN-036 and API-FIN-014 are both gated on PERM_FIN_RECURRING_TEMPLATES_UPDATE, so whoever may
  retire a template may still attempt to run it
Steps        : 1. PUT /{id}/deactivate — 2. POST /{id}/run on that same, now inactive template —
  3. re-read the template (API-FIN-012) and search the period's journal entries (API-FIN-018)
Expected     : 1. 200, isActiveFl=false — 2. 409 {code: "FIN-409-NOT-ACTIVE"},
  ar "هذا التعريف غير نشط ولا يمكن تشغيله" /
  en "This definition is deactivated and cannot be run"; NO journal entry is posted and nextRunDate
  is NOT advanced. RecurringTemplateService.run locks the row (repository.lockForRun), then calls
  RecurringTemplateDomain.from(template).assertCanRun() BEFORE the period is resolved, before any
  line is built and before JournalPostingService.buildValidateAndPost — so the refusal precedes
  RULE-FIN-006/007/008/009 and the answer is 409 FIN-409-NOT-ACTIVE, never FIN-409-PERIOD-NOT-OPEN
  or FIN-409-UNBALANCED. The gate applies to any internal or scheduled trigger too, since both enter
  through the same run(Long) — 3. the template is still isActiveFl=false and still carries its
  ORIGINAL nextRunDate, and the period gained no RECURRING entry.
  REVISED 2026-09-12 — FLIPPED. Until this revision this scenario asserted the opposite ("201, NOT
  an error … a deactivated template still runs and still posts") and was labelled a KNOWN OPEN ITEM
  awaiting a human decision. That decision has been taken and delivered: RecurringTemplateDomain
  .assertCanRun() and the FIN-409-NOT-ACTIVE catalog row both now exist in source. State plainly
  what the decision is NOT — no RULE-FIN-* states this gate (RULE-FIN-001..017 were each read and
  none constrains running a retired template) and AC-FIN-023 is still written "Given an active
  recurring template", stating no outcome for an inactive one. This is a recorded human decision,
  not a requirement that was always there, and no scenario may imply otherwise
Test data    : the deactivated MONTHLY RECURRING template from TC-FIN-104; an OPEN period covering
  its nextRunDate
<!-- TC:TC-FIN-106:END -->

<!-- TC:TC-FIN-107:START traces=AC-FIN-026,REQ-FIN-026,API-FIN-037,API-FIN-017 -->
### TC-FIN-107 — a deactivated allocation rule is REFUSED at run time (FIN-409-NOT-ACTIVE)
Derived from : AC-FIN-026 (REQ-FIN-026) · Exercises: API-FIN-037 PUT /api/v1/fin/allocation-rules/{id}/deactivate then API-FIN-017 POST /api/v1/fin/allocation-rules/{id}/run
Rule / code  : RECORDED HUMAN DECISION, not a RULE-FIN-* → FIN-409-NOT-ACTIVE (Status.CONFLICT → 409)
Scenario     : STATE · data class EDGE · language ALL
Preconditions: TC-FIN-105's rule, with a non-zero source-account balance and a valid remainder-target
  set, and today's date inside a period that exists and is OPEN — API-FIN-017 posts at
  LocalDate.now(), not at a caller-supplied date. ONE caller performs both calls: API-FIN-037 and
  API-FIN-017 are both gated on PERM_FIN_ALLOCATION_RULES_UPDATE
Steps        : 1. PUT /{id}/deactivate — 2. POST /{id}/run on that same, now inactive rule —
  3. re-read the rule (API-FIN-015) and search the period's journal entries (API-FIN-018)
Expected     : 1. 200, isActiveFl=false — 2. 409 {code: "FIN-409-NOT-ACTIVE"}, the same bundle row
  as TC-FIN-106: ar "هذا التعريف غير نشط ولا يمكن تشغيله" /
  en "This definition is deactivated and cannot be run"; NO ALLOCATION entry is posted and the
  source account's balance is untouched. AllocationRuleService.run locks the row
  (repository.lockForRun), builds the domain and calls assertCanRun() BEFORE the target set is
  loaded and before assertRemainderTargetSetValid evaluates RULE-FIN-003 — so a retired rule is
  refused for being retired and never for its remainder-target set: the answer is
  409 FIN-409-NOT-ACTIVE, never FIN-409-REMAINDER-COUNT or FIN-422-REMAINDER-NOT-POSITIVE — 3. the
  rule is still isActiveFl=false and the period gained no ALLOCATION entry.
  REVISED 2026-09-12 — FLIPPED, together with TC-FIN-106. It previously asserted "201, NOT an error
  … AllocationRuleDomain.isActive() remains uncalled anywhere in the module" and was labelled a
  KNOWN OPEN ITEM. assertCanRun() now reads exactly that `active` fact, so the flag finally has a
  reader on the run path. As with TC-FIN-106, no RULE-FIN-* states this gate — RULE-FIN-003, the
  rule AllocationRuleDomain otherwise owns, governs the remainder-target SET and says nothing about
  the active flag — so it rests on a recorded human decision, not on a requirement that was always
  there
Test data    : the deactivated 3-target rule from TC-FIN-105; a source account with a non-zero
  POSTED balance; an OPEN period covering today
<!-- TC:TC-FIN-107:END -->

<!-- TC:TC-FIN-108:START traces=AC-FIN-022,REQ-FIN-022,API-FIN-012,API-FIN-015,API-FIN-036,API-FIN-037 -->
### TC-FIN-108 — the isActiveFl search filter finally discriminates on both screens
Derived from : AC-FIN-022 (REQ-FIN-022) · Exercises: API-FIN-012 POST /api/v1/fin/recurring-templates/search · API-FIN-015 POST /api/v1/fin/allocation-rules/search
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: two recurring templates and two allocation rules, exactly one of each deactivated
  through API-FIN-036 / API-FIN-037; callers holding PERM_FIN_RECURRING_TEMPLATES_VIEW and
  PERM_FIN_ALLOCATION_RULES_VIEW. `isActiveFl` is on both services' allowed field sets, so it is
  both filterable and sortable. It travels in the body's `filters` list as the plan's EXACT
  comparison — operator EQUALS — and its `value` must be a JSON boolean, because the shared
  converter passes the raw value straight through to cb.equal against a Boolean attribute
Steps        : 1. POST recurring-templates/search {filters: [isActiveFl EQUALS false]} — 2. POST
  the same with true — 3. POST allocation-rules/search {filters: [isActiveFl EQUALS false]} —
  4. POST the same with true — 5. POST recurring-templates/search with NO isActiveFl filter
Expected     : 1. 200 returning ONLY the deactivated template, with its real lineCount — 2. 200
  returning ONLY the still-active one — 3 and 4. the same split over allocation rules, each row
  carrying its real targetCount — 5. 200 returning BOTH.
  This is the one behaviour the two new endpoints genuinely CHANGE. Before API-FIN-036 and
  API-FIN-037 existed, FIN_RECURRING_TEMPLATE.IS_ACTIVE_FL and FIN_ALLOCATION_RULE.IS_ACTIVE_FL
  were NOT NULL, defaulted TRUE and had no writer reachable from the API, so an isActiveFl=false
  search could only ever return an empty page and an isActiveFl=true search was indistinguishable
  from no filter at all — the filter was advertised on both screens but could not discriminate.
  Steps 1 and 3 are therefore the assertions that would have failed before this delivery
Test data    : 2 templates and 2 allocation rules, one of each deactivated; filter values JSON
  `false` and `true`
<!-- TC:TC-FIN-108:END -->

<!-- TC:TC-FIN-109:START traces=AC-FIN-010,REQ-FIN-010,API-FIN-020,API-FIN-011 -->
### TC-FIN-109 — a PERCENTAGE rule line whose amountSourceValue is not a number fails loudly
Derived from : AC-FIN-010 (REQ-FIN-010) · Exercises: API-FIN-020 POST /api/v1/fin/journal-entries/from-event
  (the only caller of the throw site); staged through API-FIN-011 POST /api/v1/fin/event-rules/{id}/lines
Rule / code  : RULE-FIN-010 (build half) → FIN-422-INVALID-PERCENTAGE-VALUE
  (Status.BUSINESS_RULE_VIOLATION → HTTP 422). A malformed-stored-configuration guard, NOT a rule
  violation: no RULE-FIN-* requires amountSourceValue to parse, and the code's own javadoc calls it
  a "code review fix"
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an ACTIVE EventTypeRule holding one line created through API-FIN-011 with
  amountSourceTypeCode=PERCENTAGE and amountSourceValue="abc" — a value that is NOT a well-formed
  decimal. This is storable through the API: RuleLineService.create validates the four CODE fields
  against MDL (ACCOUNT_DERIVATION_TYPE, AMOUNT_SOURCE_TYPE, DEBIT_CREDIT, DISTRIBUTION_TYPE) and
  runs RULE-FIN-003's remainder-set guard, but amountSourceValue itself carries NO format
  constraint — RuleLineCreateRequest declares it as a bare String with only an @Schema annotation,
  no @Pattern, @Digits or @NotNull — so the bad value persists and only surfaces at build time.
  The line must NOT be marked isRemainderFl: buildLines sets remainder lines aside BEFORE calling
  sourcedAmount, so a remainder-marked line never reaches the parse (and PERCENTAGE + remainder is
  already rejected by TC-FIN-052 anyway). Also required: no prior entry for this eventReference,
  and a docDate inside an OPEN period, so nothing earlier in the path can account for the failure
Steps        : 1. POST /from-event with a triggering event of that type, a fresh eventReference and
  a non-zero baseAmount — 2. re-read by eventReference (API-FIN-018) — 3. repeat step 1 with the
  same line's amountSourceValue corrected to "60" through a fresh rule/line fixture
Expected     : 1. 422 {code: "FIN-422-INVALID-PERCENTAGE-VALUE"},
  ar "قيمة مصدر المبلغ لهذا السطر ليست نسبة مئوية صالحة" /
  en "This rule line's amount source value is not a valid percentage number"; NOTHING is posted —
  the whole build runs in ONE transaction and the throw happens while the lines are still being
  assembled, before JournalPostingService.buildValidateAndPost is entered. The validation ORDER is
  part of this assertion: EventEntryService.build runs the RULE-FIN-004 duplicate check →
  FIN-404-NO-ACTIVE-RULE → EventTypeRuleDomain.assertRemainderLineSetValid (RULE-FIN-003) →
  resolvePeriodContaining → buildLines, and only then posts. So the answer is 422
  FIN-422-INVALID-PERCENTAGE-VALUE and never the posting pipeline's aggregated
  FIN-409-UNBALANCED / FIN-409-NOT-POSTABLE-ACCOUNT / FIN-409-PERIOD-NOT-OPEN, and never the
  sibling FIN-422-REMAINDER-MARKER, which the same method raises on its FIRST branch for a
  REMAINDER-sourced line (TC-FIN-052) — 2. no entry exists for that eventReference, so the event
  can be resubmitted once the rule is fixed; the 422 consumed no docNo — 3. 201, the percentage
  line computes normally, proving the refusal was the unparseable value and nothing else.
  ADDED 2026-09-12 to close a real coverage gap: FIN-422-INVALID-PERCENTAGE-VALUE was a registered
  constant with a live throw site and both bundle rows, and NO scenario exercised it. It is not a
  code this revision's work introduced
Test data    : an active rule with one non-remainder PERCENTAGE line, amountSourceValue "abc";
  baseAmount 1000.00; a fresh eventReference; then the same fixture with "60"
<!-- TC:TC-FIN-109:END -->
<!-- SUB:API-SCENARIOS:END -->
<!-- PHASE:TEST-PLAN-BE:END -->

<!-- PHASE:INT-XM:START traces=REQ-FIN-001,REQ-FIN-037,REQ-FIN-038,XM-FIN-001 -->
FIN declares exactly ONE XM: XM-FIN-001 (SOFT-READ → MDL's lookup values), consumed by
FinLookupValidationService through the injected MdlLookupApi. MDL is in the current selection, so it
is a real linking atom.
XM-FIN-002 (READ → SEC's user→permission directory, registered at ALIGN-BE for the RULE-FIN-015
fact) NO LONGER EXISTS — REVISED 2026-09-12. Its only consumer, FinSeparationOfDutiesService, was
deleted by a recorded human decision, and nothing under com.erp.fin imports com.erp.sec.crossmodule
any more. XM coverage for this module is therefore 1/1, down from 2/2. TC-FIN-091, which existed
solely to exercise that call, is RETIRED below rather than deleted, so no id renumbers.

<!-- TC:TC-FIN-047:START traces=XM-FIN-001,REQ-FIN-001,API-FIN-002 -->
### TC-FIN-047 — MDL lookup-type not-found is translated into a FIN error code
Derived from : XM-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-002 POST /api/v1/fin/accounts (representative of every lookup-validating API)
Rule / code  : XM-FIN-001 (SOFT-READ) → FIN-400-INVALID-LOOKUP (a defined error, never a 500/unhandled state, never MDL's raw code)
Scenario     : INTEGRATION · data class EDGE · language ALL
Preconditions: MDL's `ACCOUNT_TYPE` LookupType is absent or deactivated, so the injected `MdlLookupApi.readActiveValuesByKey("ACCOUNT_TYPE")` throws `LocalizedException(NOT_FOUND, MDL_404_TYPE_KEY)`. (XM-FIN-001 is in-process Spring injection inside the single deployable — there is no network hop, so the former "MDL unreachable / times out" precondition is not reachable and has been replaced by the real in-process failure mode.)
Steps        : 1. POST a new account (accountTypeCode requires MDL validation) while that lookup type is unavailable
Expected     : the request fails with FIN-400-INVALID-LOOKUP, message ar "القيمة المُدخلة غير صالحة" / en "The submitted value is not valid" — never a raw crash, and MDL's `MDL_404_TYPE_KEY` never surfaces to the caller
Test data    : any account payload; MDL's ACCOUNT_TYPE lookup type deactivated (or the MdlLookupApi test double configured to throw MDL_404_TYPE_KEY)
<!-- TC:TC-FIN-047:END -->

<!-- TC:TC-FIN-091:START traces=AC-FIN-038,REQ-FIN-037,REQ-FIN-038,API-FIN-026 -->
### TC-FIN-091 — RETIRED 2026-09-12 — asserts nothing; the SEC directory read it exercised no longer exists
Derived from : AC-FIN-038 (REQ-FIN-038), through the now-deleted XM-FIN-002 ·
  Exercised: API-FIN-026 PATCH /api/v1/fin/fiscal-periods/{id}/hard-close
Rule / code  : none — this TC is RETIRED and contributes NO coverage
Scenario     : RETIRED — do not implement, do not count as a gap
Status       : RETIRED 2026-09-12. The id is deliberately kept, never deleted and never renumbered,
  because it is referenced from the TC TRACEABILITY INDEX, test-execution-manifest-fin.md and
  packages/backend-test/state.json. Any runner that enumerates TCs must SKIP it and must NOT report
  it as a coverage gap.
Why retired  : it existed only to drive XM-FIN-002 — a test double for
  `SecUserDirectoryApi.findUserIdsHoldingPermission` throwing on the first call — and to assert that
  an unverified separation-of-duties fact answers 403 FIN-403-SOD-VIOLATION rather than approving the
  close. FIN makes no such call any more. FinSeparationOfDutiesService, FIN's only consumer of
  SecUserDirectoryApi, and FiscalPeriodDomain.assertCanHardClose(boolean, boolean) with it, were
  deleted by a recorded human decision; nothing under com.erp.fin imports com.erp.sec.crossmodule,
  and FIN-403-SOD-VIOLATION has no throw site anywhere in the module. There is no mock to install,
  no call to fail and no code to answer — so there is nothing real left to assert, which is why this
  was RETIRED rather than rewritten (unlike TC-FIN-059/060/061, each of which still had a true
  assertion available).
Coverage moved: REQ-FIN-037 is covered by TC-FIN-037 (closedBy/closedAt recorded as a distinct act)
  and now also by TC-FIN-059's Expected. REQ-FIN-038 is covered by TC-FIN-038 and TC-FIN-060 (the
  denial, on API-FIN-026 and API-FIN-027), TC-FIN-061 (the satisfied direction) and TC-FIN-062 (the
  gateway resolution). Neither REQ loses coverage. XM coverage DOES drop, 2/2 → 1/1
Traces note  : the `traces=` of this block names AC-FIN-038, the acceptance criterion whose
  denial direction this case asserted before XM-FIN-002 was deleted. The trace records where the
  case CAME FROM; it does not restore coverage — AC-FIN-038 is covered by TC-FIN-038, TC-FIN-060
  and TC-FIN-062, and this block still contributes none. It was added because `traces=` had been
  left with REQ and API ids only when XM-FIN-002 went, which left a defined TC with no
  AC/XM/UXD source at all (analyze C10.1, CRITICAL) — a retired case must still say what it was
  derived from. The id is still never enumerated by a runner.
Test data    : none
<!-- TC:TC-FIN-091:END -->
<!-- PHASE:INT-XM:END -->

## TC TRACEABILITY INDEX
| AC | TC | REQ | API | RULE/code | XM |
|---|---|---|---|---|---|
| AC-FIN-001…046 | TC-FIN-001…046 (1:1) | REQ-FIN-001…046 (1:1) | see each TC's Exercises line | see each TC's Rule/code line | — |
| — | TC-FIN-047 | REQ-FIN-001 | API-FIN-002 (representative) | — | XM-FIN-001 |
| AC-FIN-030 | TC-FIN-048 | REQ-FIN-030 | API-FIN-021 | RULE-FIN-013 / FIN-409-ALREADY-REVERSED | — |
| AC-FIN-014 | TC-FIN-049, 050, 051 | REQ-FIN-014, REQ-FIN-017 | API-FIN-019 | RULE-FIN-017 / FIN-400-PERIOD-NOT-IN-YEAR, FIN-400-DOCDATE-OUTSIDE-PERIOD | — |
| AC-FIN-009 | TC-FIN-052 | REQ-FIN-009 | API-FIN-011 | RULE-FIN-003 / FIN-422-REMAINDER-MARKER | — |
| AC-FIN-025 | TC-FIN-053, 069 | REQ-FIN-025 | API-FIN-015, API-FIN-016 | RULE-FIN-003 / FIN-409-REMAINDER-COUNT, FIN-422-REMAINDER-MARKER | — |
| AC-FIN-012 | TC-FIN-054, 055 | REQ-FIN-012 | API-FIN-020 | RULE-FIN-010 / FIN-422-REMAINDER-NOT-POSITIVE | — |
| AC-FIN-036 | TC-FIN-056, 084, 085, 086 | REQ-FIN-036 | API-FIN-027 | RULE-FIN-008 year-end exemption / FIN-409-PERIODS-NOT-CLOSED, FIN-409-INVALID-TRANSITION, FIN-404-YEAR, FIN-404-ACCOUNT | — |
| AC-FIN-002 | TC-FIN-057, 058, 071 | REQ-FIN-002, REQ-FIN-003 | API-FIN-002, 003, 004, 028 | RULE-FIN-001 / FIN-409-PARENT-NOT-LEAF-ELIGIBLE, FIN-404-ACCOUNT | — |
| AC-FIN-034 | TC-FIN-059 | REQ-FIN-034, REQ-FIN-038 | API-FIN-026 | RULE-FIN-015 (satisfied path — the distinct-permission @PreAuthorize gate is the whole enforcement) | — |
| AC-FIN-038 | TC-FIN-038, 060, 062 (denial) · TC-FIN-061 (REQ-FIN-038 satisfied) | REQ-FIN-038 | API-FIN-026, 027 | RULE-FIN-015 / FIN-403-FORBIDDEN — FIN-403-SOD-VIOLATION has no throw site and is asserted by nothing | — |
| AC-FIN-001 | TC-FIN-063, 064, 070 | REQ-FIN-001 | API-FIN-001, 002 | FIN-400-INVALID-SORT, FIN-409-ACCOUNT-DUP | — |
| AC-FIN-004 | TC-FIN-065, 072 | REQ-FIN-004 | API-FIN-005, 006 | FIN-409-DIMENSION-DUP | — |
| AC-FIN-005 | TC-FIN-066 | REQ-FIN-005 | API-FIN-008 | FIN-404-DIMENSION | — |
| AC-FIN-007 | TC-FIN-067, 073 | REQ-FIN-007 | API-FIN-009, 010 | FIN-409-RULE-DUP | — |
| AC-FIN-022 | TC-FIN-068, 075 | REQ-FIN-022 | API-FIN-012, 013 | FIN-400-MISSING-FREQUENCY | — |
| AC-FIN-008 | TC-FIN-074 | REQ-FIN-008 | API-FIN-011 | FIN-404-RULE | — |
| AC-FIN-023 | TC-FIN-076 | REQ-FIN-023 | API-FIN-014 | FIN-404-TEMPLATE | — |
| AC-FIN-026 | TC-FIN-077 | REQ-FIN-026 | API-FIN-017 | FIN-404-ALLOCATION-RULE | — |
| AC-FIN-010 | TC-FIN-078 | REQ-FIN-010 | API-FIN-020 | FIN-422-MAPPING-UNSUPPORTED | — |
| AC-FIN-016 | TC-FIN-079 | REQ-FIN-016, REQ-FIN-027 | API-FIN-021, 022 | FIN-404-ENTRY | — |
| AC-FIN-031 | TC-FIN-080, 081 | REQ-FIN-031 | API-FIN-023 | FIN-409-YEAR-DUP; calendar-month period generation | — |
| AC-FIN-032 | TC-FIN-082 | REQ-FIN-032 | API-FIN-024, 025, 026 | FIN-404-PERIOD | — |
| AC-FIN-033 | TC-FIN-083 | REQ-FIN-033 | API-FIN-025 | FIN-409-INVALID-TRANSITION | — |
| AC-FIN-014 | TC-FIN-087, 088 | REQ-FIN-014 | API-FIN-019, 022 | docNo `JV-{fiscalYearCode}-{NNNNNN}` (business code, no error row) | — |
| AC-FIN-043 | TC-FIN-089 | REQ-FIN-043 | API-FIN-032 | FIN-404-DIMENSION | — |
| AC-FIN-045 | TC-FIN-090 | REQ-FIN-045 | API-FIN-010, 002 | FIN-400-INVALID-LOOKUP | XM-FIN-001 |
| — | TC-FIN-091 — **RETIRED 2026-09-12**, covers nothing | REQ-FIN-037 → TC-FIN-037/059 · REQ-FIN-038 → TC-FIN-038/060/061/062 | API-FIN-026 | none — XM-FIN-002 and FIN-403-SOD-VIOLATION are both unreachable | — |
| AC-FIN-013 | TC-FIN-092 | REQ-FIN-013, REQ-FIN-007 | API-FIN-034, API-FIN-020 | RULE-FIN-005 / FIN-404-NO-ACTIVE-RULE (reachable via deactivation) | — |
| AC-FIN-021 | TC-FIN-093 | REQ-FIN-021, REQ-FIN-005 | API-FIN-035, API-FIN-019 | RULE-FIN-009 / FIN-409-INVALID-DIMENSION (inactive-value branch) | — |
| AC-FIN-031 | TC-FIN-094, 095 | REQ-FIN-031 | API-FIN-033 | FIN-400-INVALID-SORT; FIN-403-FORBIDDEN | — |
| AC-FIN-007 | TC-FIN-096, 097 | REQ-FIN-007 | API-FIN-034, API-FIN-010 | FIN-404-RULE; FIN-409-RULE-DUP (deactivate does not free the event type) | — |
| AC-FIN-005 | TC-FIN-098 | REQ-FIN-005 | API-FIN-035 | FIN-404-DIMVALUE | — |
| AC-FIN-040 | TC-FIN-099 | REQ-FIN-040 | API-FIN-029 | FIN-404-PERIOD (only when periodId is supplied) | — |
| AC-FIN-041 | TC-FIN-100 | REQ-FIN-041 | API-FIN-030 | FIN-404-YEAR | — |
| AC-FIN-042 | TC-FIN-101 | REQ-FIN-042 | API-FIN-031 | FIN-404-YEAR, FIN-404-PERIOD | — |
| AC-FIN-036 | TC-FIN-102 | REQ-FIN-036 | API-FIN-027, API-FIN-019 | dormant close: empty line sets, RULE-FIN-006 reads 0 = 0 as balanced; VALIDATION_ERROR on `lines: []` | — |
| AC-FIN-021 | TC-FIN-103 | REQ-FIN-021 | API-FIN-019 | RULE-FIN-009 / FIN-409-INVALID-DIMENSION (wrong-dimension branch) | — |
| AC-FIN-022 | TC-FIN-104 | REQ-FIN-022 | API-FIN-036 | FIN-404-TEMPLATE; FIN-403-FORBIDDEN (no SRS rule guards a deactivate) | — |
| AC-FIN-025 | TC-FIN-105 | REQ-FIN-025 | API-FIN-037 | FIN-404-ALLOCATION-RULE; FIN-403-FORBIDDEN (no SRS rule guards a deactivate) | — |
| AC-FIN-023 | TC-FIN-106 | REQ-FIN-023 | API-FIN-036, API-FIN-014 | FIN-409-NOT-ACTIVE (409) via RecurringTemplateDomain.assertCanRun() — recorded human decision, no RULE-FIN-* states it | — |
| AC-FIN-026 | TC-FIN-107 | REQ-FIN-026 | API-FIN-037, API-FIN-017 | FIN-409-NOT-ACTIVE (409) via AllocationRuleDomain.assertCanRun() — recorded human decision, no RULE-FIN-* states it | — |
| AC-FIN-022 | TC-FIN-108 | REQ-FIN-022 | API-FIN-012, API-FIN-015 | isActiveFl(EXACT) filter now discriminates (no error row) | — |
| AC-FIN-010 | TC-FIN-109 | REQ-FIN-010 | API-FIN-020, API-FIN-011 | RULE-FIN-010 (build half) / FIN-422-INVALID-PERCENTAGE-VALUE — malformed stored config, not a rule violation | — |

## COVERAGE
RE-MEASURED 2026-09-12. TC ids 109 (TC-FIN-109 added, nothing renumbered) · TCs IN FORCE 108
(TC-FIN-091 RETIRED — it is not a gap and must not be counted as one) · AC covered 46/46 (0 gaps) ·
REQ covered 46/46 · XM covered 1/1, DOWN from 2/2 · 40 FIN error-code constants, of which 39 are
exercised.
AC-FIN-038 keeps THREE denial TCs (TC-FIN-038, TC-FIN-060, TC-FIN-062) plus TC-FIN-061 for
REQ-FIN-038's satisfied direction, so neither AC-FIN-038 nor REQ-FIN-038 loses coverage when
TC-FIN-091 retires; REQ-FIN-037 keeps TC-FIN-037 and gains TC-FIN-059's closedBy/closedAt assertion.
API covered 37/37, each with a happy path AND its
principal failure — 37 re-counted against the delivered controllers, which carry API-FIN-001…037
with no gap (API-FIN-028…032 are ReportController's five). The TWO endpoints added since the
previous count are API-FIN-036 (deactivate recurring template — TC-FIN-104: happy with a correct
lineCount, FIN-404-TEMPLATE and FIN-403-FORBIDDEN) and API-FIN-037 (deactivate allocation rule —
TC-FIN-105: the same three, with a correct targetCount). Both reuse an existing permission
(FIN_RECURRING_TEMPLATES/UPDATE and FIN_ALLOCATION_RULES/UPDATE, seeded by
V24__fin_security_seed.sql), so neither needed a migration and neither added an error code. The
three endpoints added in the count before that are API-FIN-033 (period
search — TC-FIN-094 happy, TC-FIN-095 FIN-400-INVALID-SORT and the 403), API-FIN-034 (deactivate
event-type rule — TC-FIN-096 happy and FIN-404-RULE, TC-FIN-097 the duplicate-code limitation) and
API-FIN-035 (deactivate dimension value — TC-FIN-098 happy and FIN-404-DIMVALUE).
CLOSED 2026-09-12 — the KNOWN OPEN ITEM this section used to carry is resolved in code, and the two
scenarios that pinned it are flipped. API-FIN-036 and API-FIN-037 now GATE both run paths:
RecurringTemplateDomain.assertCanRun() and AllocationRuleDomain.assertCanRun() throw
LocalizedException(Status.CONFLICT, FIN_409_NOT_ACTIVE), so API-FIN-014 and API-FIN-017 answer
409 FIN-409-NOT-ACTIVE on a deactivated definition and post nothing. Each guard runs FIRST, before
the period is resolved / before the target set is loaded, so the refusal precedes RULE-FIN-006/007/
008/009 and RULE-FIN-003 respectively. TC-FIN-106 and TC-FIN-107 assert that; they previously
asserted "201, still runs and still posts", which would now FAIL.
State plainly what this gate is NOT: no REQ, AC or RULE-FIN-* requires it. RULE-FIN-001..017 were
each read and none constrains running a retired template or rule; AC-FIN-023 and AC-FIN-026 state
outcomes only for the ACTIVE case. FIN-409-NOT-ACTIVE and both assertCanRun() methods rest on a
RECORDED HUMAN DECISION, not on a requirement that was always there — no scenario may imply
otherwise.
Deactivation itself is still UNGUARDED on the way in — nothing is delegated before the mutation, and
re-deactivating stays idempotent — which is exactly what TC-FIN-104 and TC-FIN-105 assert and which
the gate does not change. The other thing the two endpoints change is that the isActiveFl(EXACT)
filter advertised on API-FIN-012 and API-FIN-015 finally discriminates — before them the column was
NOT NULL, defaulted TRUE and had no writer reachable from the API — and that is TC-FIN-108, also
unaffected.
SUPERSEDED, and stated plainly because this file previously claimed the opposite: API-FIN-029/030/031
no longer "declare no reachable failure of their own, so none was invented". The report service now
resolves the keying id first, so API-FIN-030 and API-FIN-031 answer FIN-404-YEAR on an unknown
REQUIRED fiscalYearId (TC-FIN-100, TC-FIN-101) instead of a silent 200 all-zero report, and
API-FIN-029 answers FIN-404-PERIOD on an unknown periodId ONLY when one is supplied — omitting it
stays a valid 200 across all periods (TC-FIN-099), so a scenario asserting 404 on an omitted
periodId would be wrong · every selected-module
(AC-FIN-030 carries two TCs — TC-FIN-030 for the non-POSTED half of RULE-FIN-013 and
TC-FIN-048 for its double-reversal half; the 1:1 row above is otherwise unchanged.)
XM covered 1/1 (XM-FIN-001 → TC-FIN-047 and TC-FIN-090). DOWN FROM 2/2, said plainly rather than
quietly re-based: XM-FIN-002 (FIN → SEC's user→permission directory) NO LONGER EXISTS.
FinSeparationOfDutiesService, FIN's only consumer of SecUserDirectoryApi, was deleted by a recorded
human decision, and nothing under com.erp.fin imports com.erp.sec.crossmodule any more — FIN's sole
crossmodule import today is com.erp.mdl.crossmodule.MdlLookupApi, in FinLookupValidationService.
TC-FIN-091 existed only to exercise that SEC call and is RETIRED — its id is kept so nothing
renumbers, it contributes no coverage, and a runner must skip it rather than report it as a gap.
Note for the governance owner, NOT fixed here (out of this session's scope): XM-FIN-002 is still
declared in P2/db-script-fin.md, P3_1/backend-execution-plan-fin.md and several
packages/backend-execution/ files. Those declarations are now stale.
RULE covered 17/17, each with both paths, except where the rule has no violated path by
construction: RULE-FIN-011 and RULE-FIN-012 are success-path only (TC-FIN-028/029) and
RULE-FIN-016 is enforced by omission — there is no route to violate, which TC-FIN-016/017
assert. RULE-FIN-017 is covered by TC-FIN-049/050 (violated) and TC-FIN-051 (satisfied, at both
inclusive period bounds); RULE-FIN-008's year-end exemption by TC-FIN-056; RULE-FIN-010's
per-side computation by TC-FIN-054 and its non-positive residue by TC-FIN-055; RULE-FIN-015 by
TC-FIN-059 (satisfied, API-FIN-026) and TC-FIN-061 (satisfied, API-FIN-027, by a caller holding BOTH
permission codes) against TC-FIN-038 and TC-FIN-060 (violated: a role without
PERM_FIN_PERIODS_CLOSE_APPROVE is denied, on API-FIN-026 and API-FIN-027 respectively). REVISED
2026-09-12 — the previous reading of this rule ("violated: creator-only, nobody holding
close-approval, one user holding both") is FALSE. The rule is satisfied by the DISTINCT PERMISSION
alone, enforced by SEC's own mechanism, exactly as RULE-FIN-015's Data source line and AC-FIN-038
state; it was never a requirement that the two permissions' USER SETS be disjoint. The deleted
FinSeparationOfDutiesService enforced that stricter reading and refused the close for everyone
whenever any one user held both codes. RULE-FIN-005's violated path is now covered twice, from two
different starting states: TC-FIN-013 from an event type that never had a rule, and TC-FIN-092 from
one whose rule was retired through API-FIN-034 — a transition nothing could stage through the API
before that endpoint existed. RULE-FIN-009 is now covered on BOTH of its
conditions, which it was not before: the inactive branch by TC-FIN-021 (stated) and TC-FIN-093
(arranged end to end through API-FIN-035, rather than by writing FIN_DIMENSION_VALUE.IS_ACTIVE_FL
as data), and the wrong-dimension branch by TC-FIN-103 — a real hole until now, since the guard is
a single `if` over both conditions and nothing exercised the second one. Both branches answer the
same FIN-409-INVALID-DIMENSION by design, so the pair is distinguished by its fixture, never by the
response.
ERROR CODES, re-measured in source for this revision and not carried over: 40 `FinErrorCodes`
constants, 40 `^FIN-` keys in messages.properties and 40 in messages_ar.properties — all three sets
identical, compared key by key. Up from the 38 this file last recorded; the three added since are
FIN-403-FORBIDDEN, FIN-409-NOT-ACTIVE and FIN-422-INVALID-PERCENTAGE-VALUE (FIN-403-SOD-VIOLATION
was not removed from either the constants or the bundles — see below).
Of those 40, 39 are exercised by at least one scenario. The ONE that is not, stated rather than
hidden:
  · FIN-403-SOD-VIOLATION — the constant (FinErrorCodes) and both bundle rows still exist, but the
    code has NO throw site anywhere in com.erp.fin: FinSeparationOfDutiesService and
    FiscalPeriodDomain.assertCanHardClose(boolean, boolean) were deleted by a recorded human
    decision, and FiscalPeriodDomain now carries an explicit "there is deliberately NO
    assertCanHardClose(...) method here" comment in its place. No scenario can produce it and none
    claims to any more. Whether the Error Catalog row itself is struck is a separate edit to the
    catalog, deliberately NOT made here.
CLOSED 2026-09-12: FIN-422-INVALID-PERCENTAGE-VALUE was the second such row when this revision
began — a registered constant with both bundle rows and a live throw site
(EventTypeRuleDomain.sourcedAmount, the PERCENTAGE branch's NumberFormatException catch) that NO
scenario exercised. It is reachable: RuleLineCreateRequest puts no format constraint on
amountSourceValue, so API-FIN-011 stores an unparseable one and API-FIN-020 — the throw site's only
caller — raises 422 while building the lines. TC-FIN-109 now covers it. That code was NOT introduced
by this revision's work; the gap predated it.
FIN-409-NOT-ACTIVE is the code the run-gate decision added and is covered by TC-FIN-106 and
TC-FIN-107. FIN-403-FORBIDDEN is covered by TC-FIN-038 and TC-FIN-060 (both re-pointed at it this
revision) plus TC-FIN-062, TC-FIN-095, TC-FIN-098, TC-FIN-104 and TC-FIN-105; FIN-404-DIMVALUE by
TC-FIN-098, never conflated with the parent's FIN-404-DIMENSION. FIN-404-TEMPLATE has a second
producer (TC-FIN-104 alongside TC-FIN-076) and FIN-404-ALLOCATION-RULE likewise (TC-FIN-105
alongside TC-FIN-077).
SEPARATELY from those two unexercised CONSTANTS, TWO Error Catalog rows are deliberately NOT given
a scenario and are not constants at all: FIN-503 is struck
(XM-FIN-001 is in-process injection, so no 503 producer exists) and FIN-500 is the infrastructure
fallthrough with no sanctioned way to provoke it from the API surface. FIN-403-FORBIDDEN was a third
such row until FinForbiddenAdvisor landed, and this file previously claimed it "never reaches the
wire as a FIN code" — that is now FALSE. The advisor intercepts every AccessDeniedException raised
inside `com.erp.fin.service` and re-raises it as LocalizedException(FORBIDDEN, FIN_403_FORBIDDEN),
so a @PreAuthorize denial on any FIN service answers FIN's own code with a bundle-resolved message:
ar "لا تملك صلاحية المالية المطلوبة لهذه العملية" /
en "You do not hold the Finance permission required for this operation".
All 42 @PreAuthorize annotations in FIN sit on `com.erp.fin.service` methods (none on a controller,
none anywhere else under com.erp.fin; 42 re-counted in source for this revision — this file
previously recorded 43, measured before FinSeparationOfDutiesService was deleted, and "44" before
that; the two deactivate methods are part of the current 42)
and SecurityConfig adds no URL-level authority rule for FIN, so in practice every FIN permission
denial takes that path. Two boundaries stay true and no scenario may claim otherwise: a denial raised
by the Spring Security filter chain BEFORE any FIN service is entered is written by
SecSecurityErrorHandler and still answers SEC-403-FORBIDDEN (unreachable for FIN today —
SecurityConfig authorizes FIN paths with `.anyRequest().authenticated()` only — but it exists); and
FIN-403-SOD-VIOLATION is moot rather than "unaffected". This file previously said the advisor never
sees it, "which is exactly what TC-FIN-059/060/061/091 assert" — FALSE on both halves as of
2026-09-12: the code has no throw site at all, and not one of those four scenarios asserts it any
more (TC-FIN-059 and TC-FIN-061 are success paths, TC-FIN-060 asserts FIN-403-FORBIDDEN, TC-FIN-091
is RETIRED).
PLATFORM I18N, residual: `INTERNAL_ERROR`, `DATA_INTEGRITY_VIOLATION`, `VALIDATION_ERROR` and
`ACCESS_DENIED` now all resolve through MessageSource. One half stays open and is stated here rather
than hidden: GlobalExceptionHandler.handleMalformedRequestBody emits hardcoded English
("The request body is malformed or does not match the expected structure") because it shares the
`VALIDATION_ERROR` wire code with the bean-validation handler but needs different text, and one
bundle key cannot carry two messages — so an Arabic caller sending a malformed body still gets
English. No TC asserts a localized message for that response. All 14 of the plan's §12 must-honor
points are individually exercised: 1→TC-018, 2→TC-040 (sign presentation, checked
structurally by the report), 3→TC-019, 4→TC-020, 5→TC-018/all amount fields (CHK
constraint, exercised implicitly by every posting TC), 6→TC-012/026, 7→TC-028, 8→TC-040,
9→TC-039/040/041/042/043 (all live-derived), 10→TC-036/041, 11→TC-021/043, 12→TC-011,
13→TC-016, 14→(no TC — a design-time constraint verified by code review, not a runtime scenario).
══════════════════════════════════════════════════════════════════
