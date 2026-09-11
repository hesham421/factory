<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-004 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-004, AC-SEC-005, AC-SEC-009, AC-SEC-010, AC-SEC-011, AC-SEC-031, API-SEC-005, API-SEC-006, API-SEC-007, API-SEC-008, API-SEC-009, API-SEC-010, API-SEC-011, REQ-SEC-004, REQ-SEC-005, REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-031, SCR-SEC-004 -->
<!-- SUB:F4-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F4 · SCR-SEC-004 — المستخدمون / Users

### F4-SCREEN — SCR-SEC-004            traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011
Routes       : base slug `users`, under the flat module segment `/security` — SRS Part B's
               `SEC → Authorization → Users` grouping is not rendered, because the two-tier
               menu of REQ-SEC-021 and `ModuleMenuResponse` cannot carry it (ADR-SEC-011);
               a route segment the menu cannot produce would disagree with the menu —
               `/security/users` (search) ·
               `/security/users/pending` (the pending sign-ups sub-view — a **static** segment,
               registered BEFORE the `:id` routes so it is never matched as an id) ·
               `/security/users/new` (drawer, create) ·
               `/security/users/:id` (drawer, view) ·
               `/security/users/:id/edit` (drawer, edit)
Chunk        : one lazy chunk for this composite screen — search, drawer and pending sub-view
               share it; the drawer is never a second chunk
Guard        : every route element guarded by `PERM_SEC_USERS_VIEW`, evaluated as
               "`SEC_USERS` is present in the menu response" (ADR-SEC-005). CREATE and UPDATE
               are not readable from any published endpoint, so `/new` and `/:id/edit` carry
               the same VIEW guard and the server's 403 is the authority on the write itself.
Components   : `UsersSearchPage` (route-level) · `UserFormDrawer` (route-level, `SIDE_DRAWER`) ·
               `PendingSignupsPage` (route-level) · `UserFilters`, `UserResultTable`,
               `UserRolesSelect`, `SignupDecisionRow` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` → CREATE,
               `/:id/edit` → EDIT, `/:id` → VIEW — never from a parent prop
Facade       : the SCR-SEC-004 facade of F2; pages never call queries directly
Shared UI    : side drawer, data table, filter bar, text field, select, multi-select,
               confirmation dialog, inline errors, localized message banner
Cross-module : none — no `UXD-*` is cited; every field is SEC's own (ENT-SEC-001/003/013)
The drawer is toggled by the route param, never by local-only state, so an edit is linkable and
the browser's back gesture closes it. Deactivate and reactivate are one affordance whose label
follows the row's status, and its confirmation names the session termination REQ-SEC-011
performs server-side.

<!-- SUB:F4-SCR-SEC-004:END -->
