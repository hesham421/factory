<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-005 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-020, AC-SEC-030, API-SEC-012, API-SEC-013, API-SEC-014, API-SEC-015, API-SEC-016, API-SEC-017, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-020, REQ-SEC-030, SCR-SEC-005 -->
<!-- SUB:F4-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F4 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F4-SCREEN — SCR-SEC-005            traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017
Routes       : base slug `roles`, under the module segment —
               `/security/roles` (master list) ·
               `/security/roles/new` (create form — a **static** segment registered BEFORE the
               id routes) ·
               `/security/roles/:roleId` (the role's grant tree — the tree route, registered
               before any deeper id route) ·
               `/security/roles/:roleId/modules/:moduleId` (a module node selected inside the
               tree — the node route param)
Chunk        : one lazy chunk for this composite screen — master list, create form and grant
               tree share it
Guard        : every route element guarded by `PERM_SEC_ROLES_VIEW`, evaluated as `SEC_ROLES`
               present in the menu response (ADR-SEC-005). CREATE and UPDATE render their
               affordances; the server's 403 is the authority.
Components   : `RolesTreePage` (route-level, `TREE_MASTER_DETAIL` — hosts the role master list,
               the grant tree and the permanently visible detail) · `RoleCreatePage`
               (route-level) · `RoleMasterList`, `GrantTree`, `GrantNodeDetail`,
               `ModuleRevokeConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new` → CREATE, `/:roleId` → VIEW
               with the tree editable in place. There is no EDIT mode: no role-update endpoint
               is published (ADR-SEC-008).
Facade       : the SCR-SEC-005 facade of F2
Shared UI    : two-pane tree layout, tree node with a checkbox affordance, data table, filter
               bar, text field, textarea, confirmation dialog, inline errors, message banner
Cross-module : none — the tree's nodes are rows of SEC's own registry entities
               (ENT-SEC-004/005/006), not another module's data, so no `UXD-*` is cited
The tree route is registered before the node route, so a role id is never matched as a module
id. Un-checking a screen or action node is not offered — only the module-level revoke exists
(API-SEC-015, ADR-SEC-008) — and the tree states this where a reader would expect otherwise.

<!-- SUB:F4-SCR-SEC-005:END -->
