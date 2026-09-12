<!-- source: PHASE:SEC-FE -->
<!-- traces: AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, API-MDL-010, API-MDL-011, REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, SCR-MDL-001, SCR-MDL-002, UXD-MDL-001 -->
<!-- PHASE:SEC-FE:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 5 — SEC-FE

The frontend half of the security model, per `SCR-*`: the navigation guard and the per-action
UI behaviour. Permission names are the backend registry's and the SRS Access summary's, never
redeclared. One mechanism gates both screens — the **menu gate**: the screen's page code is
present in the effective menu the security module serves for this caller. Action-level
permissions are not readable from any published MDL endpoint, so an action's affordance renders
for a caller who holds the screen and the server's `ACCESS_DENIED` is the authority, shown as
its localized message. Never split — level-1 only.

### SEC-FE · SCR-MDL-001 — اللوكبات العامة / Generic Lookups
Permissions      : `PERM_MDL_LOOKUPS_VIEW`, `PERM_MDL_LOOKUPS_CREATE`,
`PERM_MDL_LOOKUPS_UPDATE`, `PERM_MDL_LOOKUPS_DELETE`
Navigation guard : `MDL_LOOKUPS` must be present in the caller's effective menu; a caller
without it is sent to the unauthorized destination, and every route of this screen — the list,
`new`, `:typeId`, `:typeId/edit` and both value routes — carries the same guard.
Per action       : VIEW → the gate above, exact, and it covers both panes: a caller who holds
the screen sees types and values alike. CREATE (a type, and a value under it), UPDATE (edit at
either level, and the reorder) and DELETE (deactivate at either level) → the affordances render
and `ACCESS_DENIED` from the server is shown as the localized forbidden message. DELETE here
means deactivate and nothing else: no hard delete exists at either level, which is why the SRS
Access summary's DELETE column reads "role-granted (deactivate)".
The screen-level grant is the whole granularity. Per-lookup-type permissions — letting a role
manage `USER_STATUS` but not `PAYMENT_METHOD` — are an explicit SRS scope exception
(§A2 Out of scope), so no per-type gate is drawn, attempted, or hinted at in the UI.

### SEC-FE · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner
Permissions      : `PERM_MDL_TYPE_REGISTRY_VIEW`
Navigation guard : `MDL_TYPE_REGISTRY` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE: the SRS Access
summary gives this screen VIEW alone, and the screen writes nothing. Its links into
SCR-MDL-001 are rendered unconditionally; the target route's own guard stops a caller who does
not hold that screen, so a reviewer who may browse but not manage sees the registry and is
refused at the door of the editor rather than shown a dead link.

**Across both screens.** A forbidden response is shown as its localized catalog message, never
as a silent no-op and never as a generic failure. An unauthenticated response returns the
caller to the platform's sign-in destination and discards the server-state cache, so no data of
the previous identity survives into the next. No screen composes a permission name, and no
screen holds a local copy of the caller's grants: the menu response is the single source, and a
failure to load it renders no MDL entry and grants no MDL route — access narrows, never widens.

<!-- PHASE:SEC-FE:END -->
