<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-007 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-031, AC-FIN-032, AC-FIN-033, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-037, AC-FIN-038, API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026, API-FIN-027, API-FIN-033, REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038, SCR-FIN-007, UXD-FIN-003, UXD-FIN-004 -->
<!-- SUB:F4-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F4 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F4-SCREEN — SCR-FIN-007            traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004
Routes       : base slug `fiscal-periods`, under `/finance` —
               `/finance/fiscal-periods` (the year list beside the period list, registered
               **before** any `:id` route) ·
               `/finance/fiscal-periods/new-year` (create a fiscal year — a static segment
               before the `:id` routes) ·
               `/finance/fiscal-periods/:yearId` (that year's periods)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_PERIODS_VIEW`, evaluated as
               "`FIN_PERIODS` is present in the caller's effective menu" (ADR-FIN-005).
               `PERM_FIN_PERIODS_CLOSE_APPROVE` is not readable, so the hard-close and
               year-end-close affordances render under the same VIEW guard and the server's
               403 is the authority — which is exactly what RULE-FIN-015 asks for.
Components   : `FiscalCalendarPage` (route-level, TREE_MASTER_DETAIL — years beside their
               periods) · `FiscalYearList`, `FiscalYearForm`, `FiscalPeriodTable`,
               `PeriodFilters`, `PeriodTransitionConfirm`, `YearEndCloseConfirm`
               (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new-year` → CREATE,
               `/:yearId` → VIEW. Neither resource has an EDIT mode (ADR-FIN-006).
Facade       : the SCR-FIN-007 facade of F2
Shared UI    : split pane, data table, text field, date field, number field, confirmation
               dialog, global busy indicator (the year-end close alone), inline errors,
               localized message banner
Cross-module : UXD-FIN-003 (period state), UXD-FIN-004 (fiscal year status)
The year list is derived from the period rows' `fiscalYearId` (ADR-FIN-006) and is presented
as an ordinary list; the indirection is not exposed to the user. Each period row renders only
the transitions §A7 allows from its current state, so a hard-closed row has no Open affordance
at all. On a successful year-end close the two returned entries are offered on SCR-FIN-006's
route.

<!-- SUB:F4-SCR-FIN-007:END -->
