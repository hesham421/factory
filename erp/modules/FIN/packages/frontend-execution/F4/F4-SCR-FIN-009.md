<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-009 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-040, AC-FIN-046, API-FIN-029, REQ-FIN-040, REQ-FIN-046, SCR-FIN-009, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F4-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F4 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F4-SCREEN — SCR-FIN-009            traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `trial-balance`, under `/finance` —
               `/finance/trial-balance` — the only route; both filters live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_TRIAL_BALANCE_VIEW`, evaluated as
               "`FIN_TRIAL_BALANCE` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `TrialBalancePage` (route-level, FULL_PAGE) · `TrialBalanceFilters`,
               `BalancedBanner`, `AccountBalanceTable` (presentational)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-009 facade of F2
Shared UI    : filter bar, select, data table, status banner, localized message banner
Cross-module : UXD-FIN-001 (account type), UXD-FIN-002 (nature)
`BalancedBanner` renders the server's `balanced` value and nothing derived: REQ-FIN-040 makes
the equality the report's property, and a client that recomputed it could contradict the
report it is displaying. Each row's account links to `/finance/account-ledger` carrying the
account and the period's range — the second hop of the drill-down chain. This screen is itself
the target of SCR-FIN-010's and SCR-FIN-011's statement lines.

<!-- SUB:F4-SCR-FIN-009:END -->
