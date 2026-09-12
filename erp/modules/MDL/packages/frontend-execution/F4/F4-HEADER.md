<!-- source: PHASE:F4 — preamble before the first SUB -->
<!-- traces: REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, UXD-MDL-001, SCR-MDL-001, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-010, API-MDL-011, SCR-MDL-002 -->
## PHASE 4 — F4 — Screens & Routes

One block per `SCR-*`: routes, chunk, guard, components, mode, facade, shared UI and
cross-module citations. Routes are named by the container pattern — `TREE_MASTER_DETAIL` → a
TreePage hosting the master list and its detail, with the list route registered **before** any
`:id` route; `FULL_PAGE` with no entry sub-view → a single Page and no entry route. One lazy
chunk per composite screen. Every `PERM_*` name below is the backend's, never invented here,
and every route sits under the module segment `/reference-data`.
