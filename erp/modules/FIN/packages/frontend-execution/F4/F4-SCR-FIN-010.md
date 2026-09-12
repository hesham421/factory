<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-010 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-041, AC-FIN-046, API-FIN-030, REQ-FIN-041, REQ-FIN-046, SCR-FIN-010, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F4-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F4 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F4-SCREEN — SCR-FIN-010            traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `balance-sheet`, under `/finance` —
               `/finance/balance-sheet` — the only route; the fiscal year and as-of date live
               in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_BALANCE_SHEET_VIEW`, evaluated as
               "`FIN_BALANCE_SHEET` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `BalanceSheetPage` (route-level, FULL_PAGE) · `StatementFilters`,
               `StatementSection`, `AccountBalanceTable` (presentational — the table is the
               same component SCR-FIN-009 uses, since the row shape is the same)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-010 facade of F2
Shared UI    : filter bar, select, date field, data table, section headings, localized message
               banner
Cross-module : UXD-FIN-001 (account type — the section heading), UXD-FIN-002 (nature)
The required fiscal year gates the call, so the page shows a choose-a-year state rather than a
blank statement. Each row links to `/finance/trial-balance` narrowed to that account type —
the first hop of REQ-FIN-046's chain.

<!-- SUB:F4-SCR-FIN-010:END -->
