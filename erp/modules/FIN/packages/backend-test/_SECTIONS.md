<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
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
