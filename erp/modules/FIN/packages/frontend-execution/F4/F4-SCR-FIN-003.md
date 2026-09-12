<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-003 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-007, AC-FIN-008, AC-FIN-009, API-FIN-009, API-FIN-010, API-FIN-011, API-FIN-034, REQ-FIN-007, REQ-FIN-008, REQ-FIN-009, SCR-FIN-003, UXD-FIN-002, UXD-FIN-007, UXD-FIN-008, UXD-FIN-009, UXD-FIN-010 -->
<!-- SUB:F4-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F4 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F4-SCREEN — SCR-FIN-003            traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010
Routes       : base slug `engine-rules`, under `/finance` —
               `/finance/engine-rules` (search) ·
               `/finance/engine-rules/new` (create the rule header — a static segment before
               the `:id` routes) ·
               `/finance/engine-rules/:id` (the rule page with its line grid) ·
               `/finance/engine-rules/:id/lines/new` (add a line)
Chunk        : one lazy chunk for this composite screen — search page and rule page share it
Guard        : every route element guarded by `PERM_FIN_RULES_VIEW`, evaluated as
               "`FIN_RULES` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `EngineRulesSearchPage` (route-level, FULL_PAGE) · `EngineRulePage`
               (route-level, FULL_PAGE — the header and its lines) · `RuleFilters`,
               `RuleResultTable`, `RuleHeaderForm`, `RuleLineGrid`, `RuleLineForm`,
               `RuleDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match; there is no EDIT mode — neither
               the rule nor the line has an update endpoint (ADR-FIN-006)
Facade       : the SCR-FIN-003 facade of F2
Shared UI    : data table, filter bar, text field, select, exclusive-choice control (the
               remainder marker across the grid), confirmation dialog, inline errors,
               localized message banner
Cross-module : UXD-FIN-007 (event type), UXD-FIN-008 (account derivation type), UXD-FIN-009
               (amount source type), UXD-FIN-010 (distribution type), UXD-FIN-002 (direction)
Search and the rule page are separate components under ONE `SCR-*` sharing ONE chunk, linked
by the `:id` route param. The line grid's three references stay three columns and are never
collapsed into one control.

<!-- SUB:F4-SCR-FIN-003:END -->
