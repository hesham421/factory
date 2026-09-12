<!-- source: PHASE:F2 / SUB:F2-SCR-MDL-002 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-010, API-MDL-011, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, SCR-MDL-002, UXD-MDL-001 -->
<!-- SUB:F2-SCR-MDL-002:START traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001,SCR-MDL-002 -->
### F2 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F2-QUERY — API-MDL-010            traces=API-MDL-010,REQ-MDL-013
POST `/api/v1/mdl/lookup-types/by-owner/search` · request `LookupTypeByOwnerSearchRequest`
{ filters[] } — **no sortField, no sortDirection, no page, no size** · response **a bare
array** of `OwnerGroupResponse` { ownerModuleCode, types[] } · kind **read query**
(ADR-MDL-002)
Cache key    : `[lookup-types-by-owner, filters]` — ownerModuleCode and key, and nothing more.
               No page or size belongs in this key because the endpoint accepts neither; adding
               them would key a variation the server cannot produce.
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `VALIDATION_ERROR` (400) → inline on the offending filter ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : n/a (a read). It is refreshed by SCR-MDL-001's type mutations through the shared
               `[lookup-types, *]` family, since a type created or deactivated there changes
               what this registry shows.
### F2-QUERY — API-MDL-011            traces=API-MDL-011,REQ-MDL-011,REQ-MDL-012
GET `/api/v1/mdl/lookups` · query param `type` = the lookup type's key · response **a bare
array** of `LookupValueResponse` — active values only, ordered by `sortOrder` · kind
**read query**
**Bound, and called by no screen** (ADR-MDL-007): the caller is a consuming module's backend
over the platform's in-process module interface, not a user with a screen. It is stated here so
the published surface is completely accounted for.
Errors       : `MDL-404-TYPE-KEY` (404) [REQ-MDL-012] → answered to the calling module — an
               unknown key is a not-found, never an empty success ·
               `ACCESS_DENIED` (403) → answered to the calling module
Cache key    : n/a — no client of this plan calls it
Invalidation : n/a. What a user can observe of this endpoint is indirect: deactivating a value
               or its type on SCR-MDL-001 is what makes it stop being returned (RULE-MDL-004).
### F2-SCREEN-INIT — SCR-MDL-002
Permission read : `MDL_TYPE_REGISTRY` present in the caller's effective menu → VIEW. This
                  screen has no other action.
Lookups used    : none
Foreign data    : the owner-module filter and the group headings resolve through UXD-MDL-001 —
                  the same shared hook SCR-MDL-001 uses, not a second call
Entity by id    : none — the groups carry their full type rows
### F2-FACADE — SCR-MDL-002
Composes     : API-MDL-010 · the UXD-MDL-001 hook
State it owns: the groups derived from the query's data, and the filter object (owner module,
               key) mirrored from the route's search params. No grouping and no count is
               composed here — both arrive in the response
Operations   : none — this screen writes nothing. Navigation to SCR-MDL-001 with a type
               selected is a route change, not an operation
<!-- SUB:F2-SCR-MDL-002:END -->
