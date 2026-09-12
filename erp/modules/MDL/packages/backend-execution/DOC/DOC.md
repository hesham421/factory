<!-- source: PHASE:DOC -->
<!-- traces: REQ-MDL-011 -->
<!-- PHASE:DOC:START traces=REQ-MDL-011 -->
## PHASE 4 — DOC

**API contract summary** (backend self-check only; the frontend stage binds to the real
`api-docs-mdl.md` published after implementation):

| API | Path | Verb | Request DTO | Response DTO | Stability |
|---|---|---|---|---|---|
| API-MDL-001 | /lookup-types/search | POST | LookupTypeSearchRequest | paginated list of LookupTypeResponse | v1 |
| API-MDL-002 | /lookup-types | POST | LookupTypeCreateRequest | LookupTypeResponse | v1 |
| API-MDL-003 | /lookup-types/{id} | PUT | LookupTypeUpdateRequest | LookupTypeResponse | v1 |
| API-MDL-004 | /lookup-types/{id} | DELETE | — | LookupTypeResponse | v1 |
| API-MDL-005 | /lookup-types/values/search | POST | LookupValueSearchRequest | paginated list of LookupValueResponse | v1 |
| API-MDL-006 | /lookup-types/{id}/values | POST | LookupValueCreateRequest | LookupValueResponse | v1 |
| API-MDL-007 | /lookup-values/{id} | PUT | LookupValueUpdateRequest | LookupValueResponse | v1 |
| API-MDL-008 | /lookup-values/{id} | DELETE | — | LookupValueResponse | v1 |
| API-MDL-009 | /lookup-types/{id}/values/reorder | PATCH | LookupValueReorderRequest | array of LookupValueResponse | v1 |
| API-MDL-010 | /lookup-types/by-owner/search | POST | LookupTypeByOwnerSearchRequest | array of OwnerGroupResponse | v1 |
| API-MDL-011 | /lookups | GET | — | array of LookupValueResponse | v1 |
(paths relative to `/api/v1/mdl`. A `—` request means the endpoint takes no body: API-MDL-004
and API-MDL-008 carry their id in the path, and API-MDL-011 reads its `type` key from a query
parameter. RESOLVED 2026-09-12 against the published `_inputs/api-docs-mdl.md`: every type name
above was previously marked `(proposed)` — derived before any implementation existed — and each
is now the name the surface really publishes, so the `(proposed)` marks are gone rather than
carried beside real names. THREE ROWS ALSO CHANGED VERB AND PATH, and that is the substantive
correction: API-MDL-001, API-MDL-005 and API-MDL-010 were written here as `GET` with query
parameters and are published as `POST …/search` taking a `filters[]` envelope. The `Endpoint :`
lines of their own API blocks above already said `POST …/search`, and so did `srs-mdl.md`
§B5 — this table was the only artifact in the module still predicting the GET form, which is
why `gov.py analyze` raised it here as three C8.4 `endpoint-agrees` findings and nowhere else.
The Response DTO cells are written in the api-docs' own words — `paginated list of X` where the
response carries a `Page<T>` envelope and `array of X` where it does not — rather than in a
`Page<X>` / `List<X>` notation the published document never uses; only two of the eleven are
paged, and the notation now shows which. Two response types also moved: API-MDL-004 and
API-MDL-008 were predicted to return a
`DeactivateConfirmation`, and each really returns its own entity response with
`isActiveFl=false`. The frontend was bound to the published shape throughout —
`erp/decisions/MDL/ADR-MDL-002.md` records the divergence and names this table as where the fix
belonged.)

**DTO typing constraints**: `ownerModuleCode` is `String` (the platform module code, not
an enum); no business code field exists.

**Pagination + filter standard**: same as every module (Phase 1 CORE).
<!-- PHASE:DOC:END -->
