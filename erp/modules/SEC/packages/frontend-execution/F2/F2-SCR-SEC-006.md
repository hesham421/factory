<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-006 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-016, AC-SEC-017, AC-SEC-018, AC-SEC-019, API-SEC-018, API-SEC-019, API-SEC-020, API-SEC-021, REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019, SCR-SEC-006 -->
<!-- SUB:F2-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F2 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

### F2-QUERY — API-SEC-021            traces=API-SEC-021,REQ-SEC-016,REQ-SEC-017,REQ-SEC-019
POST `/api/v1/sec/registry/search` · request `RegistrySearchRequest` { filters[], sortField,
sortDirection, page, size, pageCode } · response `Page<RegistryRowResponse>` (module → screens
→ actions, nested) · kind **read query** (ADR-SEC-003)
Cache key    : `[registry, filters]` — module code, pageCode, sort **and page, size**, in the
               one filter object. This is the same key SCR-SEC-005's grant tree reads, so the
               registry is fetched once for both screens.
Errors       : `ACCESS_DENIED` → forbidden message · `SEC-400-INVALID-SORT` → inline on sort ·
               `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : nothing this frontend does invalidates it — registration happens through the
               registering module's own call (ADR-SEC-009), so the tree is refreshed by an
               explicit refresh affordance rather than by a local mutation
### F2-QUERY — API-SEC-018            traces=API-SEC-018,REQ-SEC-016
POST `/api/v1/sec/registry/modules` · request `ModuleRegistryCreateRequest` { code, nameAr,
nameEn } · response `ModuleRegistryResponse` · kind **mutation — not called by this frontend**
Documented, bound and left uncalled (ADR-SEC-009): a module registers itself from its own
onboarding path (SRS SCR-REQ-SEC-006 B3). The block exists so the shape is on record for the
integrator reading this plan, and so a later pass adding an operator-driven registration has
its contract already reconciled. Errors when it is called: `SEC-409-MODULE-DUP` (409),
`VALIDATION_ERROR` (400), `ACCESS_DENIED` (403).
### F2-QUERY — API-SEC-019            traces=API-SEC-019,REQ-SEC-017,REQ-SEC-018
POST `/api/v1/sec/registry/screens` · request `ScreenRegistryCreateRequest` { moduleCode,
pageCode, nameAr, nameEn } · response `ScreenRegistryResponse` · kind **mutation — not called
by this frontend** (ADR-SEC-009). Errors when it is called:
`SEC-409-MODULE-NOT-REGISTERED` (409) — RULE-SEC-004, ar: "الوحدة غير مسجّلة" ·
en: "Module is not registered" (AC-SEC-018) · `SEC-409-SCREEN-DUP` (409) ·
`VALIDATION_ERROR` (400) · `ACCESS_DENIED` (403).
### F2-QUERY — API-SEC-020            traces=API-SEC-020,REQ-SEC-019
POST `/api/v1/sec/registry/actions` · request `ActionRegistryCreateRequest` { pageCode,
actionCode, nameAr, nameEn } · response `ActionRegistryResponse` · kind **mutation — not called
by this frontend** (ADR-SEC-009). The response's `permissionCode` is derived server-side as
`PERM_<PAGE_CODE>_<ACTION>` and is displayed, never composed here. Errors when it is called:
`SEC-409-SCREEN-NOT-REGISTERED` (409) · `SEC-409-ACTION-DUP` (409) · `VALIDATION_ERROR` (400) ·
`ACCESS_DENIED` (403).
### F2-SCREEN-INIT — SCR-SEC-006
Permission read : `SEC_MODULE_REGISTRY` present in the API-SEC-027 menu response → VIEW
                  (ADR-SEC-005). No UPDATE affordance is drawn at all (ADR-SEC-008), so none
                  is read.
Lookups used    : none
Entity by id    : none — the nested search response carries every level the detail pane shows
### F2-FACADE — SCR-SEC-006
Composes     : API-SEC-021 only
State it owns: the tree derived from the query's data, the selected node (route param), the
               filter object including page and size, the expansion state, and a derived
               loading flag
Operations   : none — this screen is read-only (SRS B3, ADR-SEC-008)

<!-- SUB:F2-SCR-SEC-006:END -->
