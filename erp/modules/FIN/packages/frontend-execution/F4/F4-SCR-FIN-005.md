<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-005 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-025, AC-FIN-026, API-FIN-015, API-FIN-016, API-FIN-017, API-FIN-037, REQ-FIN-025, REQ-FIN-026, SCR-FIN-005, UXD-FIN-010 -->
<!-- SUB:F4-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F4 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F4-SCREEN — SCR-FIN-005            traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010
Routes       : base slug `allocation-rules`, under `/finance` —
               `/finance/allocation-rules` (search) ·
               `/finance/allocation-rules/new` (create — a static segment before the `:id`
               route) ·
               `/finance/allocation-rules/:id` (the rule page, read-only)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_ALLOCATION_RULES_VIEW`, evaluated as
               "`FIN_ALLOCATION_RULES` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `AllocationRulesSearchPage` (route-level, FULL_PAGE) · `AllocationRulePage`
               (route-level, FULL_PAGE — header and target grid) · `AllocationRuleFilters`,
               `AllocationRuleResultTable`, `AllocationRuleHeaderForm`, `AllocationTargetGrid`,
               `AllocationRunConfirm`, `AllocationDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match; no EDIT mode exists (ADR-FIN-006)
Facade       : the SCR-FIN-005 facade of F2
Shared UI    : data table, filter bar, text field, select, number field, exclusive-choice
               control (the remainder target), confirmation dialog, inline errors, localized
               message banner
Cross-module : UXD-FIN-010 (distribution type)
The remainder target's amount cell renders the word "الباقي / remainder" rather than a figure,
which is the routing decision of F3's RULE-FIN-010 block expressed as a component. On a
successful run the returned entry is offered on SCR-FIN-006's route, never rendered here.

<!-- SUB:F4-SCR-FIN-005:END -->
