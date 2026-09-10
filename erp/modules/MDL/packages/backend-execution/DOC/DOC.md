<!-- source: PHASE:DOC -->
<!-- traces: REQ-MDL-011 -->
<!-- PHASE:DOC:START traces=REQ-MDL-011 -->
## PHASE 4 — DOC

**API contract summary** (backend self-check only; the frontend stage binds to the real
`api-docs-mdl.md` published after implementation):

| API | Path | Verb | Request DTO | Response DTO | Stability |
|---|---|---|---|---|---|
| API-MDL-001 | /lookup-types | GET | (query params) | Page\<LookupTypeResponse\> | v1 |
| API-MDL-002 | /lookup-types | POST | LookupTypeCreateRequest | LookupTypeResponse | v1 |
| API-MDL-003 | /lookup-types/{id} | PUT | LookupTypeUpdateRequest | LookupTypeResponse | v1 |
| API-MDL-004 | /lookup-types/{id} | DELETE | — | DeactivateConfirmation | v1 |
| API-MDL-005 | /lookup-types/{id}/values | GET | (query params) | Page\<LookupValueResponse\> | v1 |
| API-MDL-006 | /lookup-types/{id}/values | POST | LookupValueCreateRequest | LookupValueResponse | v1 |
| API-MDL-007 | /lookup-values/{id} | PUT | LookupValueUpdateRequest | LookupValueResponse | v1 |
| API-MDL-008 | /lookup-values/{id} | DELETE | — | DeactivateConfirmation | v1 |
| API-MDL-009 | /lookup-types/{id}/values/reorder | PATCH | ReorderRequest | List\<LookupValueResponse\> | v1 |
| API-MDL-010 | /lookup-types/by-owner | GET | (query params) | List\<OwnerGroupResponse\> | v1 |
| API-MDL-011 | /lookups | GET | (query param `type`) | List\<LookupValueResponse\> | v1 |
(paths relative to `/api/v1/mdl`)

**DTO typing constraints**: `ownerModuleCode` is `String` (the platform module code, not
an enum); no business code field exists.

**Pagination + filter standard**: same as every module (Phase 1 CORE).
<!-- PHASE:DOC:END -->
