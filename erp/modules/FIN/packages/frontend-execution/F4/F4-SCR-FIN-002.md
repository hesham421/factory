<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-002 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-004, AC-FIN-005, AC-FIN-006, API-FIN-005, API-FIN-006, API-FIN-007, API-FIN-008, API-FIN-035, REQ-FIN-004, REQ-FIN-005, REQ-FIN-006, SCR-FIN-002 -->
<!-- SUB:F4-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F4 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F4-SCREEN — SCR-FIN-002            traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035
Routes       : base slug `dimensions`, under `/finance` —
               `/finance/dimensions` (the dimension list) ·
               `/finance/dimensions/new` (create a dimension — a **static** segment registered
               BEFORE the `:id` routes) ·
               `/finance/dimensions/:id` (the dimension with its values) ·
               `/finance/dimensions/:id/values/new` (create a value under it)
Chunk        : one lazy chunk for this composite screen — both panes and both forms share it
Guard        : every route element guarded by `PERM_FIN_DIMENSIONS_VIEW`, evaluated as
               "`FIN_DIMENSIONS` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `DimensionsPage` (route-level, TREE_MASTER_DETAIL) · `DimensionList`,
               `DimensionForm`, `DimensionValueTable`, `DimensionValueForm`,
               `DimensionValueDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match — there is no EDIT mode on either
               resource, because neither has an update endpoint (ADR-FIN-006)
Facade       : the SCR-FIN-002 facade of F2
Shared UI    : split pane, data table, text field, number field, confirmation dialog, inline
               errors, localized message banner
Cross-module : none — every field on this screen is FIN's own (ENT-FIN-002, ENT-FIN-003), and
               no `UXD-*` is cited
The selected dimension is a route param, so a dimension's value list is a shareable address.
No deactivate affordance is drawn on the dimension itself: no endpoint exists (ADR-FIN-006).

<!-- SUB:F4-SCR-FIN-002:END -->
