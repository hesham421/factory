<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-011 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-042, AC-FIN-046, API-FIN-031, REQ-FIN-042, REQ-FIN-046, SCR-FIN-011, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F4-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F4 · SCR-FIN-011 — قائمة الدخل / Income statement

### F4-SCREEN — SCR-FIN-011            traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `income-statement`, under `/finance` —
               `/finance/income-statement` — the only route; the fiscal year and the two
               period ids live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_INCOME_STATEMENT_VIEW`, evaluated as
               "`FIN_INCOME_STATEMENT` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `IncomeStatementPage` (route-level, FULL_PAGE) · `StatementFilters`,
               `StatementSection`, `AccountBalanceTable`, `NetResultFooter` (presentational —
               the first three shared with SCR-FIN-010)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-011 facade of F2
Shared UI    : filter bar, select, data table, section headings, localized message banner
Cross-module : UXD-FIN-001 (account type — the section heading), UXD-FIN-002 (nature)
The period range is two selects narrowed to the chosen year, and the dates the server derived
from them are shown read-only beside the filters. An all-zero statement for a freshly closed
year is labelled as the correct result of REQ-FIN-042, not as an empty list. Each row links to
`/finance/trial-balance` for that account type.

<!-- SUB:F4-SCR-FIN-011:END -->
