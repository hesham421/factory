<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-007 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-022, AC-SEC-023, API-SEC-022, REQ-SEC-022, REQ-SEC-023, SCR-SEC-007 -->
<!-- SUB:F4-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F4 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F4-SCREEN — SCR-SEC-007            traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022
Routes       : `/security/dashboard` — a single route; no `new`, no `:id`, no `:id/edit`
               (there is no record to address)
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_DASHBOARD_VIEW`, evaluated as `SEC_DASHBOARD` present in
               the menu response (ADR-SEC-005). Per-widget permission is **not** guarded on the
               client: the server returns only the widgets the caller may see (REQ-SEC-023).
Components   : `SecurityDashboardPage` (route-level) · `UsersOverviewWidget`,
               `FailedLoginsWidget`, `ActiveSessionsWidget`, `RecentActivityWidget`,
               `RolesPermissionsWidget`, `OnboardingFunnelWidget` (presentational)
Mode         : VIEW only — read-only screen, no mode to resolve
Facade       : the SCR-SEC-007 facade of F2
Shared UI    : widget card, stat figure, compact table, skeleton, empty state, error state,
               localized message banner
Cross-module : none
Each widget renders only when its property is present in `DashboardResponse`, and each links to
the screen it summarizes — recent activity → `/security/audit-log`, active sessions →
`/security/sessions`, onboarding funnel → `/security/users/pending`. Those links are rendered
whether or not the caller holds the target screen; a caller who does not is stopped by that
screen's own guard rather than by a second, weaker check here.

<!-- SUB:F4-SCR-SEC-007:END -->
