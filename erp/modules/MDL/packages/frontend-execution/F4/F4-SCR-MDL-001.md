<!-- source: PHASE:F4 / SUB:F4-SCR-MDL-001 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, SCR-MDL-001, UXD-MDL-001 -->
<!-- SUB:F4-SCR-MDL-001:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001 -->
### F4 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F4-SCREEN — SCR-MDL-001            traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001
Routes       : base slug `lookups`, under the module segment `/reference-data` —
               `/reference-data/lookups` (the type list, registered **before** any `:id` route
               so a type id is never matched as the list itself) ·
               `/reference-data/lookups/new` (create a type — a **static** segment registered
               BEFORE the `:id` routes) ·
               `/reference-data/lookups/:typeId` (that type's values beside the list) ·
               `/reference-data/lookups/:typeId/edit` (edit the type) ·
               `/reference-data/lookups/:typeId/values/new` (create a value under it) ·
               `/reference-data/lookups/:typeId/values/:valueId/edit` (edit a value)
Chunk        : one lazy chunk for this composite screen — both panes and both forms share it;
               neither form is a second chunk
Guard        : every route element guarded by `PERM_MDL_LOOKUPS_VIEW`, evaluated as
               "`MDL_LOOKUPS` is present in the caller's effective menu". CREATE, UPDATE and
               DELETE are not readable from any published endpoint, so `/new`, `/edit` and the
               value routes carry the same VIEW guard and the server's 403 is the authority on
               the write itself.
Components   : `LookupsPage` (route-level, TREE_MASTER_DETAIL — hosts the type list and the
               value detail) · `LookupTypeList`, `LookupTypeFilters`, `LookupTypeForm`,
               `LookupValueTable`, `LookupValueFilters`, `LookupValueForm`,
               `ValueReorderHandle`, `DeactivateConfirm` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` and
               `/values/new` → CREATE, `/edit` → EDIT, `/:typeId` → VIEW — never from a parent
               prop
Facade       : the SCR-MDL-001 facade of F2; the page never calls a query directly
Shared UI    : split pane, data table, filter bar, text field, number field, select (the owner
               module), drag handle, confirmation dialog, inline field errors, localized
               message banner
Cross-module : UXD-MDL-001 (the owner module) — the one field on this screen whose
               authoritative source is another module
The selected type is a route param, so a type's value list is a linkable address and the
browser's back gesture returns to the list. Both levels show Deactivate and neither shows an
Activate: no endpoint exists for the second half (ADR-MDL-005). The drag handle submits the
whole ordered set through API-MDL-009 rather than writing one row's `sortOrder`.
<!-- SUB:F4-SCR-MDL-001:END -->
