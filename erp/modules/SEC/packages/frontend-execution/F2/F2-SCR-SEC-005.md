<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-005 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-020, AC-SEC-030, API-SEC-012, API-SEC-013, API-SEC-014, API-SEC-015, API-SEC-016, API-SEC-017, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-020, REQ-SEC-030, SCR-SEC-005 -->
<!-- SUB:F2-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F2 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F2-QUERY — API-SEC-012            traces=API-SEC-012,REQ-SEC-012
POST `/api/v1/sec/roles/search` · request `RoleSearchRequest` { filters[], sortField,
sortDirection, page, size, name } · response `Page<RoleResponse>` · kind **read query**
(ADR-SEC-003)
Cache key    : `[roles, filters]` — code/name, isActiveFl, sort **and page, size**, all inside
               the one filter object
Errors       : `ACCESS_DENIED` → forbidden message · `SEC-400-INVALID-SORT` → inline on sort ·
               `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-SEC-013 and by the grant mutations below
### F2-QUERY — API-SEC-013            traces=API-SEC-013,REQ-SEC-012
POST `/api/v1/sec/roles` · request `RoleCreateRequest` { code, nameAr, nameEn, descriptionAr,
descriptionEn } · response `RoleResponse` · kind **mutation**
Errors       : `SEC-409-ROLE-DUP` (409) → inline on `code` · `VALIDATION_ERROR` → inline ·
               `ACCESS_DENIED` → forbidden
Invalidation : `[roles, *]`
### F2-QUERY — API-SEC-014            traces=API-SEC-014,REQ-SEC-012
POST `/api/v1/sec/roles/{id}/modules` · request `RoleModuleGrantRequest` { moduleId } ·
response `RoleModuleGrantResponse` · kind **mutation**
Errors       : `SEC-404-ROLE` / `SEC-404-MODULE` (404) → user message ·
               `SEC-409-GRANT-DUP` (409) → user message · `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]` — a grant changes what some user's menu
               resolves to (REQ-SEC-021)
### F2-QUERY — API-SEC-015            traces=API-SEC-015,REQ-SEC-015
DELETE `/api/v1/sec/roles/{id}/modules/{moduleId}` · response `ModuleGrantRevokeResponse`
{ revokedScreenGrants, revokedActionGrants } · kind **mutation**
Errors       : `SEC-404-GRANT` (404) → user message · `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]` — the cascade (RULE-SEC-003) removes screen
               and action grants the client must not keep showing. The returned counts are
               displayed as the outcome, never used to patch the tree locally.
### F2-QUERY — API-SEC-016            traces=API-SEC-016,REQ-SEC-013
POST `/api/v1/sec/roles/{id}/screens` · request `RoleScreenGrantRequest` { screenId } ·
response `RoleScreenGrantResponse` · kind **mutation**
Errors       : `SEC-409-NO-MODULE-GRANT` (409) → user message for RULE-SEC-001,
               ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" ·
               en: "Cannot grant a screen without first granting its module" (AC-SEC-013) ·
               `SEC-404-SCREEN` (404) → user message · `SEC-409-GRANT-DUP` → user message ·
               `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]`
### F2-QUERY — API-SEC-017            traces=API-SEC-017,REQ-SEC-014,REQ-SEC-020,REQ-SEC-030
POST `/api/v1/sec/roles/{id}/actions` · request `RoleActionGrantRequest` { actionId } ·
response `RoleActionGrantResponse` · kind **mutation**
Errors       : `SEC-409-NO-SCREEN-GRANT` (409) → user message for RULE-SEC-002,
               ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" ·
               en: "Cannot grant an action without first granting its screen" (AC-SEC-014) ·
               `SEC-409-NO-VIEW-GRANT` (409) → user message for RULE-SEC-007,
               ar: "يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة" ·
               en: "The VIEW action must be granted on this screen first" (AC-SEC-030) ·
               `SEC-409-SOD-CONFLICT` (409) → user message for RULE-SEC-005 (AC-SEC-020) ·
               `SEC-404-ACTION` (404) · `SEC-409-GRANT-DUP` (409) → user message ·
               `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]`
### F2-QUERY — API-SEC-021 (grant tree source)   traces=API-SEC-021,REQ-SEC-012
POST `/api/v1/sec/registry/search` · response `Page<RegistryRowResponse>` · kind **read query**
Cache key    : `[registry, filters]` — module code, pageCode, sort **and page, size**, in the
               one filter object: byte-for-byte the key SCR-SEC-006 builds, so the registry is
               fetched once and both screens read one cache entry. A key that differed in page
               or size here would silently double the fetch.
Errors       : `ACCESS_DENIED` → forbidden message · `INTERNAL_ERROR` → generic
Cache policy : defaults; the registry changes only when a module onboards, so this entry is a
               natural candidate for a longer stale window — left at defaults, since deviating
               would need an ADR and nothing in the SRS asks for it
Invalidation : none from this screen — it registers nothing
### F2-SCREEN-INIT — SCR-SEC-005
Permission read : `SEC_ROLES` present in the API-SEC-027 menu response → VIEW (ADR-SEC-005).
                  CREATE / UPDATE affordances render; the server's 403 is the authority.
Lookups used    : none — every node label comes from the registry response itself
Entity by id    : none published; the master row already held by `[roles, filters]` hydrates
                  the detail pane (ADR-SEC-008)
### F2-FACADE — SCR-SEC-005
Composes     : API-SEC-012 (master list) · API-SEC-021 (the grantable tree) · the role-grant
               mutations API-SEC-013, 014, 015, 016, 017
State it owns: the role list derived from the query's data, the selected role id (route param),
               the filter object including page and size, the tree's expansion state, and a
               derived loading flag
Operations   : createRole · grantModule · grantScreen · grantModuleRevoke (usage check first —
               the confirmation names the cascade before it runs) · grantAction
               No role edit, no role deactivate and no individual screen/action revoke: no
               endpoint is published for them (ADR-SEC-008).

<!-- SUB:F2-SCR-SEC-005:END -->
