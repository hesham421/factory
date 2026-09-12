<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-001 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-001, AC-FIN-002, AC-FIN-003, API-FIN-001, API-FIN-002, API-FIN-003, API-FIN-004, REQ-FIN-001, REQ-FIN-002, REQ-FIN-003, SCR-FIN-001, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F4-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F4 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F4-SCREEN — SCR-FIN-001            traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `accounts`, under the module segment `/finance` —
               `/finance/accounts` (the tree, registered **before** any `:id` route so a node
               id is never matched as the tree itself) ·
               `/finance/accounts/new` (create, the form beside the tree) ·
               `/finance/accounts/:id` (view) ·
               `/finance/accounts/:id/edit` (edit)
Chunk        : one lazy chunk for this composite screen — tree and form share it; the form is
               never a second chunk
Guard        : every route element guarded by `PERM_FIN_ACCOUNTS_VIEW`, evaluated as
               "`FIN_ACCOUNTS` is present in the caller's effective menu" (ADR-FIN-005).
               CREATE and UPDATE are not readable from any published endpoint, so `/new` and
               `/:id/edit` carry the same VIEW guard and the server's 403 is the authority on
               the write itself.
Components   : `AccountsTreePage` (route-level, TREE_MASTER_DETAIL — hosts the tree and the
               detail form) · `AccountTree`, `AccountFilters`, `AccountForm`,
               `AccountDeactivateConfirm` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` → CREATE,
               `/:id/edit` → EDIT, `/:id` → VIEW — never from a parent prop
Facade       : the SCR-FIN-001 facade of F2; the page never calls a query directly
Shared UI    : tree, filter bar, text field, select, checkbox, confirmation dialog, inline
               field errors, localized message banner
Cross-module : UXD-FIN-001 (account type) and UXD-FIN-002 (nature) — both fields display a
               value whose authoritative source is the lookup module
The selected node is a route param, so an account being edited is linkable and the browser's
back gesture returns to the tree. Creating a child from a selected node pre-fills the parent
and the tree scrolls to the new row on success.

<!-- SUB:F4-SCR-FIN-001:END -->
