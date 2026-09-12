## TEST EXECUTION MANIFEST — FIN v1
══════════════════════════════════════════════════════════════════
Derived from: backend-test-plan-fin.md v1 (this run) · db-script-fin.md v1 (FK/XM) ·
srs-fin.md v1 (RULE messages). Extended with TC-FIN-049..091 after ALIGN-BE, then with
TC-FIN-092..103 for API-FIN-033/034/035, the report-404 change and RULE-FIN-009's wrong-dimension
branch (the previous revision of this line said 092..102 and omitted TC-FIN-103 — corrected here),
then with TC-FIN-104..108 for the API-FIN-036/037 deactivate delivery; no existing TC id was
renumbered. REVISED 2026-09-12: API-FIN-026 and API-FIN-027 are NO LONGER KNOWN-BLOCKED on a fresh
deployment. V30__fin_sys_admin_close_approve_grant.sql grants PERM_FIN_PERIODS_CLOSE_APPROVE to
SYS_ADMIN, so the bootstrap `admin` can run both directly, and the global separation-of-duties check
that used to refuse them (FinSeparationOfDutiesService + FiscalPeriodDomain.assertCanHardClose) was
deleted by a recorded human decision — see TC-FIN-059/060/061. API-FIN-027 still needs TC-FIN-086's
account marked `is_retained_earnings_fl`, settable only as data. TC-FIN-091 is RETIRED as of the
same date (XM-FIN-002 no longer exists); its id is kept, it covers nothing, and it is not a gap.
══════════════════════════════════════════════════════════════════

## DEPENDENCY ORDER (topological entity build order)
1. Dimension (no FK)
2. Account (self-FK parent only)
3. FiscalYear (no FK)
4. EventTypeRule (no FK)
5. RecurringTemplate (no FK)
6. DimensionValue (FK → Dimension)
7. AllocationRule (FK → Account)
8. FiscalPeriod (FK → FiscalYear)
9. RuleLine (FK → EventTypeRule)
10. JournalEntry (FK → FiscalYear, FiscalPeriod, self)
11. RecurringTemplateLine (FK → RecurringTemplate, Account, DimensionValue)
12. AllocationTarget (FK → AllocationRule, Account, DimensionValue)
13. JournalLine (FK → JournalEntry, Account)
14. JournalLineDimension (FK → JournalLine, Dimension, DimensionValue)

## RULE → CODE → TC
| RULE | Catalog code | TC | HTTP | API |
|---|---|---|---|---|
| RULE-FIN-001 | FIN-409-HAS-CHILDREN / FIN-409-PARENT-NOT-LEAF-ELIGIBLE | TC-FIN-002, TC-FIN-058 (violated) · TC-FIN-057 (satisfied) | 409 / 200 | API-FIN-002, API-FIN-003 |
| RULE-FIN-002 | FIN-409-DIMVALUE-DUP | TC-FIN-006 | 409 | API-FIN-007 |
| RULE-FIN-003 | FIN-409-REMAINDER-COUNT | TC-FIN-009, TC-FIN-053 | 409 | API-FIN-011, API-FIN-016 |
| RULE-FIN-003 | FIN-422-REMAINDER-MARKER | TC-FIN-052, TC-FIN-053 | 422 | API-FIN-011, API-FIN-016, API-FIN-017, API-FIN-020 |
| RULE-FIN-004 | FIN-409-DUPLICATE-EVENT | TC-FIN-011 | 409 | API-FIN-020 |
| RULE-FIN-005 | FIN-404-NO-ACTIVE-RULE | TC-FIN-013 (never configured), TC-FIN-092 (rule retired via API-FIN-034) | 404 | API-FIN-020 |
| RULE-FIN-006 | FIN-409-UNBALANCED | TC-FIN-018 · TC-FIN-102 (0 = 0 counts as balanced: the dormant year-end close) | 409 / 201 | API-FIN-019, 020, 014, 017, 027 |
| RULE-FIN-007 | FIN-409-NOT-POSTABLE-ACCOUNT | TC-FIN-019 | 409 | API-FIN-019, 020, 014, 017 |
| RULE-FIN-008 | FIN-409-PERIOD-NOT-OPEN | TC-FIN-020 | 409 | API-FIN-019, 020, 014, 017 |
| RULE-FIN-008 | — (year-end CLOSING/OPENING exemption) | TC-FIN-056 | 201 | API-FIN-027 |
| RULE-FIN-009 | FIN-409-INVALID-DIMENSION | TC-FIN-021 · TC-FIN-093 (inactive branch staged through API-FIN-035) · TC-FIN-103 (wrong-dimension branch) | 409 | API-FIN-019, 020, 014, 017 |
| RULE-FIN-010 | — (success-path computation, per side) | TC-FIN-012, TC-FIN-026, TC-FIN-054 | 200/201 | API-FIN-020, 014, 017 |
| RULE-FIN-010 | FIN-422-REMAINDER-NOT-POSITIVE | TC-FIN-055 | 422 | API-FIN-017, API-FIN-020 |
| RULE-FIN-011 | — (success-path) | TC-FIN-028 | 201 | API-FIN-021 |
| RULE-FIN-012 | — (success-path) | TC-FIN-029 | 201 | API-FIN-021 |
| RULE-FIN-013 | FIN-409-NOT-POSTED | TC-FIN-030 | 409 | API-FIN-021 |
| RULE-FIN-013 | FIN-409-ALREADY-REVERSED | TC-FIN-048 | 409 | API-FIN-021 |
| RULE-FIN-014 | FIN-409-NOT-REOPENABLE | TC-FIN-035 | 409 | API-FIN-024 |
| RULE-FIN-015 | FIN-403-FORBIDDEN — the distinct-permission `@PreAuthorize` IS the enforcement, re-raised by FinForbiddenAdvisor. FIN-403-SOD-VIOLATION has NO throw site left in `com.erp.fin` (constant and bundle rows survive; catalog row untouched here) | TC-FIN-038 (entry-creation-only role, API-FIN-026), TC-FIN-060 (the same denial on API-FIN-027) | 403 | API-FIN-026, API-FIN-027 |
| RULE-FIN-015 | — (satisfied path: ANY holder of PERM_FIN_PERIODS_CLOSE_APPROVE; overlap with the entry-creation permission is no longer consulted anywhere) | TC-FIN-059 (200, API-FIN-026, `admin` post-V30 or a FIN_CLOSE_APPROVER holder), TC-FIN-061 (201, API-FIN-027, caller holds BOTH codes) | 200 / 201 | API-FIN-026, API-FIN-027 |
| (platform gateway) | FIN-403-FORBIDDEN — the @PreAuthorize denial inside `com.erp.fin.service`, re-raised by FinForbiddenAdvisor and localized per Accept-Language; never the platform `ACCESS_DENIED` | TC-FIN-062, TC-FIN-095, TC-FIN-098, TC-FIN-104, TC-FIN-105 | 403 | API-FIN-026, API-FIN-033, API-FIN-035, API-FIN-036, API-FIN-037 |
| RULE-FIN-016 | — (enforced by omission, no route) | TC-FIN-016, TC-FIN-017 | 404/405 | API-FIN-022 |
| RULE-FIN-017 | FIN-400-PERIOD-NOT-IN-YEAR | TC-FIN-049 | 400 | API-FIN-019 |
| RULE-FIN-017 | FIN-400-DOCDATE-OUTSIDE-PERIOD | TC-FIN-050 | 400 | API-FIN-019 |
| RULE-FIN-017 | — (satisfied, inclusive period bounds) | TC-FIN-051 | 201 | API-FIN-019 |
| (no RULE — RECORDED HUMAN DECISION, added 2026-09-12) | FIN-409-NOT-ACTIVE — a deactivated recurring template or allocation rule is refused at run time by `RecurringTemplateDomain.assertCanRun()` / `AllocationRuleDomain.assertCanRun()`, before the period is resolved / before the target set is loaded, so nothing is built and nothing posts | TC-FIN-106, TC-FIN-107 | 409 | API-FIN-014, API-FIN-017 |

## ENTITY CRUD CHECKLIST
| ENT | create | read | search | update | deactivate (soft) | activate |
|---|---|---|---|---|---|---|
| ENT-FIN-001 Account | ✓ (API-FIN-002) | — | ✓ (API-FIN-001) | ✓ (API-FIN-003) | ✓ (API-FIN-004) | — |
| ENT-FIN-002 Dimension | ✓ (API-FIN-006) | — | ✓ (API-FIN-005) | — | — | — |
| ENT-FIN-003 DimensionValue | ✓ (API-FIN-007) | — | ✓ (API-FIN-008) | — | ✓ (API-FIN-035) | — (no `activate` anywhere in FIN) |
| ENT-FIN-004 JournalEntry | ✓ (API-FIN-019, 020) | ✓ (API-FIN-022) | ✓ (API-FIN-018) | — (locked, RULE-FIN-016) | — (no VOID path — classic reversal leaves the original POSTED, API-FIN-021) | — |
| ENT-FIN-005 JournalLine | ✓ (with header) | ✓ (with header) | — | — | — | — |
| ENT-FIN-006 JournalLineDimension | ✓ (with line) | ✓ (with line) | — | — | — | — |
| ENT-FIN-007 FiscalYear | ✓ (API-FIN-023) | — | — | — | ✓ (statusCode=CLOSED, API-FIN-027) | — |
| ENT-FIN-008 FiscalPeriod | ✓ (with year) | — | ✓ (API-FIN-033, parent id OPTIONAL) | ✓ (API-FIN-024/025/026, transitions) | — | ✓ (API-FIN-024, reopen) |
| ENT-FIN-009 EventTypeRule | ✓ (API-FIN-010) | — | ✓ (API-FIN-009) | — | ✓ (API-FIN-034 — does NOT free the event type, TC-FIN-097) | — (no `activate` anywhere in FIN) |
| ENT-FIN-010 RuleLine | ✓ (API-FIN-011) | — | — | — | — | — |
| ENT-FIN-011 RecurringTemplate | ✓ (API-FIN-013) | — | ✓ (API-FIN-012) | — | ✓ (API-FIN-036 — now GATES API-FIN-014's run with FIN-409-NOT-ACTIVE, TC-FIN-106) | — (no `activate` anywhere in FIN) |
| ENT-FIN-012 RecurringTemplateLine | ✓ (with template) | — | — | — | — | — |
| ENT-FIN-013 AllocationRule | ✓ (API-FIN-016) | — | ✓ (API-FIN-015) | — | ✓ (API-FIN-037 — now GATES API-FIN-017's run with FIN-409-NOT-ACTIVE, TC-FIN-107) | — (no `activate` anywhere in FIN) |
| ENT-FIN-014 AllocationTarget | ✓ (with rule) | — | — | — | — | — |

## CROSS-MODULE (this module's declared XM)
| XM | Target | TC | Status |
|---|---|---|---|
| XM-FIN-001 | MDL | TC-FIN-047, TC-FIN-090 | ACTIVE — covered. FIN's ONLY XM. XM coverage is 1/1 |
| XM-FIN-002 | SEC | — (TC-FIN-091 RETIRED 2026-09-12) | **REMOVED** — no longer declared or consumed. FinSeparationOfDutiesService, FIN's only caller of `SecUserDirectoryApi`, was deleted by a recorded human decision; nothing under `com.erp.fin` imports `com.erp.sec.crossmodule`. XM coverage therefore dropped 2/2 → 1/1. (The XM registration is still present in `P2/db-script-fin.md`, `P3_1/backend-execution-plan-fin.md` and `packages/backend-execution/` — stale, and out of this revision's scope to fix.) |
══════════════════════════════════════════════════════════════════

## ENDPOINTS ADDED AFTER THE ORIGINAL MANIFEST
| API | Endpoint | Permission | TC | Notes |
|---|---|---|---|---|
| API-FIN-033 | POST /api/v1/fin/fiscal-periods/search | PERM_FIN_PERIODS_VIEW (pre-existing registry row, already granted — no migration) | TC-FIN-094, TC-FIN-095 | `fiscalYearId` is OPTIONAL, unlike API-FIN-008's required `dimensionId`; allowed sort set is fiscalPeriodPk, periodNo, nameAr, nameEn, startDate, endDate, statusCode, createdAt |
| API-FIN-034 | PUT /api/v1/fin/event-rules/{id}/deactivate | PERM_FIN_RULES_UPDATE (pre-existing — no migration) | TC-FIN-096, TC-FIN-097, TC-FIN-092 | base path is `event-rules`, not `event-type-rules`; the only way to reach FIN-404-NO-ACTIVE-RULE from a previously working event type |
| API-FIN-035 | PUT /api/v1/fin/dimensions/values/{id}/deactivate | PERM_FIN_DIMENSIONS_UPDATE (NEW — registered and granted by V28__fin_dimensions_update_action.sql) | TC-FIN-098, TC-FIN-093 | raises the NEW FIN-404-DIMVALUE; makes RULE-FIN-009's inactive branch reachable without writing the flag as data |
| API-FIN-036 | PUT /api/v1/fin/recurring-templates/{id}/deactivate | PERM_FIN_RECURRING_TEMPLATES_UPDATE (pre-existing, seeded by V24__fin_security_seed.sql — no migration) | TC-FIN-104, TC-FIN-106, TC-FIN-108 | 404 is FIN-404-TEMPLATE; response reports the real lineCount because the service re-reads the lines before mapping. REVISED 2026-09-12 — the deactivate DOES now gate API-FIN-014: `RecurringTemplateService.run` calls `RecurringTemplateDomain.assertCanRun()`, so a retired template is refused 409 FIN-409-NOT-ACTIVE and posts nothing (TC-FIN-106). FIN-409-NOT-ACTIVE is a new catalog code, added by recorded human decision, not by any RULE-FIN-* |
| API-FIN-037 | PUT /api/v1/fin/allocation-rules/{id}/deactivate | PERM_FIN_ALLOCATION_RULES_UPDATE (pre-existing, seeded by V24__fin_security_seed.sql — no migration) | TC-FIN-105, TC-FIN-107, TC-FIN-108 | 404 is FIN-404-ALLOCATION-RULE; response reports the real targetCount. REVISED 2026-09-12 — the deactivate DOES now gate API-FIN-017: `AllocationRuleService.run` calls `AllocationRuleDomain.assertCanRun()` before the target set is loaded, so a retired rule is refused 409 FIN-409-NOT-ACTIVE and posts nothing (TC-FIN-107). Shares the FIN-409-NOT-ACTIVE code with API-FIN-036 |

Report keying ids, as built: API-FIN-030 and API-FIN-031 resolve their REQUIRED `fiscalYearId`
first and raise FIN-404-YEAR (TC-FIN-100, TC-FIN-101); API-FIN-029's `periodId` is OPTIONAL and
raises FIN-404-PERIOD only when supplied (TC-FIN-099). Ordering all three before any run: fiscal
year and periods must exist before any report call is exercised.
══════════════════════════════════════════════════════════════════
