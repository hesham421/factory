<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-006 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-016, AC-SEC-017, AC-SEC-018, AC-SEC-019, API-SEC-018, API-SEC-019, API-SEC-020, API-SEC-021, REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019, SCR-SEC-006 -->
<!-- SUB:F4-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F4 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

### F4-SCREEN — SCR-SEC-006            traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021
Routes       : base slug `registry`, under the module segment —
               `/security/registry` (the module tree) ·
               `/security/registry/:moduleId` (module node — the tree route, registered BEFORE
               any deeper id route) ·
               `/security/registry/:moduleId/screens/:screenId` (screen node, with its actions
               in the detail pane)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_SEC_MODULE_REGISTRY_VIEW`, evaluated as
               `SEC_MODULE_REGISTRY` present in the menu response (ADR-SEC-005). No UPDATE
               affordance is drawn at all (ADR-SEC-008), so none is guarded.
Components   : `RegistryTreePage` (route-level, `TREE_MASTER_DETAIL`) · `RegistryTree`,
               `RegistryNodeDetail`, `PermissionCodeBadge` (presentational)
Mode         : VIEW only — resolved from the route match; there is no CREATE and no EDIT route,
               because this frontend calls none of the three register endpoints (ADR-SEC-009)
Facade       : the SCR-SEC-006 facade of F2
Shared UI    : two-pane tree layout, tree node, detail panel, filter bar, badge, empty state
Cross-module : none — the rows describe other modules but are owned by SEC (ENT-SEC-004/005/006
               are SHARED with SEC as owner), so no `UXD-*` is cited
Tree routes are registered before the `:id` routes at both levels. `PermissionCodeBadge`
displays the server-derived `permissionCode` verbatim — it is the string a consuming module's
developer checks on their own side, and composing it locally would invent a second derivation
of `PERM_<PAGE_CODE>_<ACTION>`.

<!-- SUB:F4-SCR-SEC-006:END -->
