<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-012 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-043, API-FIN-032, REQ-FIN-043, SCR-FIN-012, UXD-FIN-002 -->
<!-- SUB:F4-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F4 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F4-SCREEN — SCR-FIN-012            traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002
Routes       : base slug `dimension-reports`, under `/finance` —
               `/finance/dimension-reports` — the only route; the dimension, its value and the
               period live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_DIMENSION_REPORTS_VIEW`, evaluated as
               "`FIN_DIMENSION_REPORTS` is present in the caller's effective menu"
               (ADR-FIN-005)
Components   : `DimensionReportPage` (route-level, FULL_PAGE) · `DimensionReportFilters`,
               `DimensionReportTable` (presentational)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-012 facade of F2
Shared UI    : filter bar, select, data table, localized message banner
Cross-module : UXD-FIN-002 (nature). The dimension and its values are FIN's own entities, read
               through this module's own endpoints, so they cite no `UXD-*`
The table renders the account and the dimension value as two columns of the same row and never
merges them, which is REQ-FIN-043 expressed in the component. Each row links to
`/finance/account-ledger` carrying the account **and** the dimension pair, so the ledger behind
the figure shows the same slice.

<!-- SUB:F4-SCR-FIN-012:END -->
