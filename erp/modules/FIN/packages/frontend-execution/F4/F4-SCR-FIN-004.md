<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-004 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-022, AC-FIN-023, AC-FIN-024, API-FIN-012, API-FIN-013, API-FIN-014, API-FIN-036, REQ-FIN-022, REQ-FIN-023, REQ-FIN-024, SCR-FIN-004, UXD-FIN-002, UXD-FIN-011, UXD-FIN-012 -->
<!-- SUB:F4-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F4 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F4-SCREEN — SCR-FIN-004            traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012
Routes       : base slug `recurring-templates`, under `/finance` —
               `/finance/recurring-templates` (search) ·
               `/finance/recurring-templates/new` (create — a static segment registered BEFORE
               the `:id` route) ·
               `/finance/recurring-templates/:id` (the template page, read-only)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_RECURRING_TEMPLATES_VIEW`, evaluated
               as "`FIN_RECURRING_TEMPLATES` is present in the caller's effective menu"
               (ADR-FIN-005)
Components   : `RecurringTemplatesSearchPage` (route-level, FULL_PAGE) ·
               `RecurringTemplatePage` (route-level, FULL_PAGE — header and line grid) ·
               `TemplateFilters`, `TemplateResultTable`, `TemplateHeaderForm`,
               `TemplateLineGrid`, `TemplateRunConfirm`, `TemplateDeactivateConfirm`
               (presentational)
Mode         : CREATE | VIEW resolved from the route match; no EDIT mode exists (ADR-FIN-006)
Facade       : the SCR-FIN-004 facade of F2
Shared UI    : data table, filter bar, text field, select, date field, number field,
               confirmation dialog, inline errors, localized message banner
Cross-module : UXD-FIN-011 (schedule type), UXD-FIN-012 (frequency), UXD-FIN-002 (direction)
The header and its lines are one submission, so the create route is a single page rather than
a wizard. On a successful run the returned entry's id is used to offer navigation to
`/finance/journal-entries/:id`, which is SCR-FIN-006's own route and guard — this screen never
renders an entry itself.

<!-- SUB:F4-SCR-FIN-004:END -->
