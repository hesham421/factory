# FRONTEND EXECUTION PLAN — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Track : frontend
Framework : react-ts-vite (profile.stack.frontend.framework) · routing react-router ·
            server-state tanstack-query · forms react-hook-form · validation zod ·
            state useState/useReducer + Context (no global store by default)
Inputs : srs (v1, PRD-approved), prd (v1), api-docs (v1, published by the backend repo),
         registry-srs (v1), registry-exec-be (v1)
Screens : 10 — SCR-SEC-001..010 · UXD : 0 (SEC is ROOT — SRS A8) · API bound : 27 / 27
Open ADRs : 8 — erp/decisions/SEC/ (ADR-SEC-003..010, all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

## API SURFACE — SEC v1   (source: `_inputs/api-docs-sec.md` — the ONLY endpoint source)

```
ENDPOINTS   27 — API-SEC-001..027, bound to the published surface by the API ID BINDING
            annex of the api-docs (ADR-SEC-004). Envelope: every response is wrapped in
            ApiResponse<T> { success, data, error { code, message, fieldErrors[] },
            timestamp }; every collection read returns Page<T> { totalPages, totalElements,
            first, last, numberOfElements, pageable, sort, size, number, empty } — except
            API-SEC-027, which returns a bare array and must not be read as a page.
            Paging constraints (PageableBuilder): default page 0 · default size 20 ·
            maximum size 200.
            Five reads are POST `…/search` with a filters[] body, not GET with query
            params — ADR-SEC-003. Per-endpoint request and response shapes are stated in
            each F2 block below rather than duplicated here.
ERRORS      business codes, each already carrying its ar/en text in the module's catalog:
            SEC-401-INVALID-CREDENTIALS (401) · SEC-403-FORBIDDEN (403) ·
            SEC-404-USER / -ROLE / -MODULE / -SCREEN / -ACTION / -GRANT / -SIGNUP /
            -SESSION (404) · SEC-409-USER-DUP / -ROLE-DUP / -MODULE-DUP / -SCREEN-DUP /
            -ACTION-DUP / -GRANT-DUP / -SIGNUP-DUP (409) · SEC-409-NO-MODULE-GRANT
            [RULE-SEC-001] · SEC-409-NO-SCREEN-GRANT [RULE-SEC-002] · SEC-409-NO-VIEW-GRANT
            [RULE-SEC-007] · SEC-409-SOD-CONFLICT [RULE-SEC-005] ·
            SEC-409-RESET-TOKEN-INVALID [RULE-SEC-006] · SEC-409-MODULE-NOT-REGISTERED
            [RULE-SEC-004] · SEC-409-SCREEN-NOT-REGISTERED · SEC-409-INVALID-TRANSITION ·
            SEC-409-ALREADY-TERMINATED (409) · SEC-400-INVALID-SORT (400)
            framework codes: VALIDATION_ERROR (400) · DATA_INTEGRITY_VIOLATION (409) ·
            ACCESS_DENIED (403) · INTERNAL_ERROR (500)
            Routing is uniform across every F2 block: field validation → inline ·
            business rule → user message · unauthenticated → login · forbidden →
            unauthorized / localized forbidden message · server → generic.
LOOKUPS     USER_STATUS · SIGNUP_STATUS · AUDIT_EVENT_TYPE — owned by SEC (SRS A6), and
            **no endpoint is published for any of them**. One shared hook per key, each
            PENDING ADR-SEC-006; every lookup field stays a string holding the code, and no
            enum is modelled anywhere in this plan.
PERMISSIONS declared by the backend and read from the api-docs, never redeclared here:
            PERM_SEC_USERS_VIEW / _CREATE / _UPDATE · PERM_SEC_ROLES_VIEW / _CREATE /
            _UPDATE · PERM_SEC_MODULE_REGISTRY_VIEW / _UPDATE · PERM_SEC_DASHBOARD_VIEW ·
            PERM_SEC_AUDIT_LOG_VIEW · PERM_SEC_SESSIONS_VIEW / _DELETE ·
            API-SEC-027 requires an authenticated caller only. No endpoint publishes the
            caller's own action-level permissions — ADR-SEC-005.
```

### Reconciliation against the SRS — run once, before any F-content

- **Every REQ that needs an endpoint has one.** REQ-SEC-001..033 map onto API-SEC-001..027
  with no gap; the mapping is the traces of the F2 blocks below.
- **Every documented endpoint maps to a REQ.** All 27 are bound; none is unknown and none is
  used without a REQ behind it.
- **Naming and shape differences** — five reads moved from GET to POST `…/search`
  (ADR-SEC-003), and the audit-entry PK is published as `auditLogPk` where the SRS calls it
  `auditLogEntryPk`. Both continue under an ADR; neither is a missing operation.
- **Operations the SRS names with no published endpoint** — role update, role deactivate,
  individual screen/action grant revoke, registry-row deactivate, read-one-user-by-id and
  logout. None is required by a `REQ-*`, so none is breaking; each is omitted rather than
  faked (ADR-SEC-008).
- **Endpoints published but not called by this frontend** — API-SEC-018, API-SEC-019,
  API-SEC-020, the three registration calls a consuming module makes for itself
  (SRS SCR-REQ-SEC-006 B3). Bound, blocked out in F2 and left uncalled (ADR-SEC-009).
- **One screen's form differs from its SRS Part B input list** — SCR-SEC-004 takes `password`
  on create (B3 omits it; `UserCreateRequest` requires it) and renders `statusCode` read-only
  (B3 lists it as an input; no write DTO accepts it). Both resolve against SRS A3 and A7
  rather than against B3's prose — ADR-SEC-010. The other nine screens match their B3 list.
- **Nothing is invented.** No value absent from the api-docs appears in this plan except as
  an explicit `PENDING ADR-…` marker.

## EXECUTION PLAN INDEX — SEC v1 — frontend-execution-plan-sec.md

| # | Phase | Split | Blocks |
|---|---|---|---|
| 1 | F1 — Models & Types | per screen (10 SCR ≥ 5) | 10 SUB |
| 2 | F2 — Data Hooks | per screen | 10 SUB |
| 3 | F3 — Forms & Validators | per screen | 10 SUB |
| 4 | F4 — Screens & Routes | per screen | 10 SUB |
| 5 | SEC-FE | never split | level-1 only |
| 6 | ALIGN-FE | never split | level-1 only |

**SCREEN REGISTRY**

| SCR | Name (ar / en) | Page code | Container pattern | Owning ENT |
|---|---|---|---|---|
| SCR-SEC-001 | تسجيل الدخول / Login | SEC_LOGIN | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001 المستخدم / User |
| SCR-SEC-002 | التسجيل الذاتي / Sign-up | SEC_SIGNUP | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-013 طلب تسجيل معلّق / SignupRequest |
| SCR-SEC-003 | نسيت / إعادة تعيين كلمة المرور / Forgot / reset password | SEC_PWD_RESET | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-012 رمز إعادة التعيين / PasswordResetToken |
| SCR-SEC-004 | المستخدمون / Users | SEC_USERS | SIDE_DRAWER | ENT-SEC-001 المستخدم / User (+ ENT-SEC-003 |
| SCR-SEC-005 | الأدوار والصلاحيات / Roles & permissions | SEC_ROLES | TREE_MASTER_DETAIL | ENT-SEC-002 الدور / Role (+ ENT-SEC-004..009 as tree nodes and grant rows) |
| SCR-SEC-006 | سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry | SEC_MODULE_REGISTRY | TREE_MASTER_DETAIL | ENT-SEC-004 ModuleRegistry |
| SCR-SEC-007 | لوحة تحكم الأمان / Admin dashboard | SEC_DASHBOARD | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001 |
| SCR-SEC-008 | سجل التدقيق / Audit log | SEC_AUDIT_LOG | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-011 سجل التدقيق / AuditLogEntry |
| SCR-SEC-009 | إدارة الجلسات النشطة / Active sessions management | SEC_SESSIONS | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-010 الجلسة النشطة / ActiveSession |
| SCR-SEC-010 | القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu | (none — global component) | none — global shell component (ADR-SEC-007) | ENT-SEC-004 ModuleRegistry |

Ten screens, so every `sub_bearing` phase splits per screen (threshold: SCR count ≥ 5), and
every SUB id is phase-qualified — `SUB:F1-SCR-SEC-004` and `SUB:F2-SCR-SEC-004` are distinct
blocks for the same screen under different phases.

<!-- PHASE:F1:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 1 — F1 — Models & Types

Per `ENT-*` (from the response DTOs of the api-docs) and per `SCR-*`: the source DTO with
each property's type and read-only / system-only / lookup status, then the screen's search
model, form model and container. Lookup fields are strings holding the code — all LOV values
are runtime-loaded (`profile.conventions.lookups`), and no enum is modelled anywhere below.
Both names are carried per language (ar, en). No internal or tenant identifier is modelled,
and nothing is modelled that the api-docs do not return.

<!-- SUB:F1-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F1 · SCR-SEC-001 — تسجيل الدخول / Login

### F1-MODEL — ENT-SEC-001 — المستخدم / User (credentials projection only)
Source DTO   : `LoginRequest` (request) · `LoginResponse` (response)
  request  : username : string · required · maxLength 100 — the login identity
             password : string · required · maxLength 200 · write-only — never held after submit
  response : accessToken : string · read-only · system-only — the signed token
             tokenType   : string · read-only · system-only
             expiresIn   : number (seconds) · read-only · system-only
Read-only    : every response property — the session is issued, never edited
### F1-SCREEN — SCR-SEC-001
Search model : none — this screen has no list (SRS B2 not applicable)
Form model   : username (required) · password (required, write-only)
               excluded system fields: every other ENT-SEC-001 property — the published
               `LoginRequest` carries two fields and the form models exactly those two
               read-only on edit: not applicable — this form has no edit mode
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Nothing is modelled that the api-docs do not return: `userPk`, `statusCode` and the user's
own profile are absent from `LoginResponse` and are therefore absent from this model. The
caller's identity for the rest of the session comes from the menu (API-SEC-027), not from a
user object this endpoint does not send.

<!-- SUB:F1-SCR-SEC-001:END -->

<!-- SUB:F1-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F1 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F1-MODEL — ENT-SEC-013 — طلب تسجيل معلّق / SignupRequest
Source DTO   : `SignupSubmitRequest` (request) · `SignupRequestResponse` (response)
  request  : email      : string · required · maxLength 255
             fullNameAr : string · required · maxLength 200
             fullNameEn : string · required · maxLength 200
  response : signupRequestPk : number · read-only (PK) · system-only
             email, fullNameAr, fullNameEn : string · read-only on the response
             submittedAt : date-time · read-only · system-only
             statusCode  : string · read-only · lookup — SIGNUP_STATUS code, held as a string
                           (no enum, no union of literals — ADR-SEC-006)
             reviewedBy  : string · read-only · system-only
             reviewedAt  : date-time · read-only · system-only
Read-only    : PK, submittedAt, statusCode, reviewedBy, reviewedAt — never form input
### F1-SCREEN — SCR-SEC-002
Search model : none — public single-purpose form
Form model   : email, fullNameAr, fullNameEn (all required)
               excluded system fields: signupRequestPk, submittedAt, statusCode, reviewedBy,
               reviewedAt
               read-only on edit: not applicable — the request is submitted once, never edited
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Both name properties are modelled separately per language (ar, en) as the DTO declares them;
neither is derived from the other.

<!-- SUB:F1-SCR-SEC-002:END -->

<!-- SUB:F1-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F1 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F1-MODEL — ENT-SEC-012 — رمز إعادة تعيين كلمة المرور / PasswordResetToken
Source DTO   : `PasswordResetRequest` · `PasswordResetCompleteRequest` · `ConfirmationResponse`
  step 1 request : email : string · required · maxLength 255
  step 2 request : token       : string · required · maxLength 200 · write-only
                   newPassword : string · required · maxLength 200 · write-only
  response       : messageAr : string · read-only — the confirmation text, Arabic
                   messageEn : string · read-only — the confirmation text, English
Read-only    : both message properties; `tokenHash`, `requestedAt`, `expiresAt` and `usedAt`
               are never returned by any published endpoint and are therefore not modelled
### F1-SCREEN — SCR-SEC-003
Search model : none
Form model   : step 1 — email (required)
               step 2 — token (required; pre-filled from the route when the link carries it),
                        newPassword (required), confirmPassword (required, client-side only —
                        it is a confirmation of the field above and is never sent)
               excluded system fields: every ENT-SEC-012 property above
               read-only on edit: not applicable
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007); the wizard step is a route param
The response carries the localized text itself, so the screen renders `messageAr`/`messageEn`
by the active locale rather than composing a message of its own.

<!-- SUB:F1-SCR-SEC-003:END -->

<!-- SUB:F1-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F1 · SCR-SEC-004 — المستخدمون / Users

### F1-MODEL — ENT-SEC-001 — المستخدم / User
Source DTO   : `UserResponse` (read) · `UserCreateRequest` · `UserUpdateRequest` (write)
  userPk     : number · read-only (PK) · system-only
  username   : string · maxLength 100 — required on create, **read-only on edit**
               (`UserUpdateRequest` does not carry it — the identity is immutable after create)
  email      : string · required · maxLength 255
  fullNameAr : string · required · maxLength 200
  fullNameEn : string · required · maxLength 200
  password   : string · required on create only · maxLength 200 · write-only — never returned
  statusCode : string · read-only · lookup — USER_STATUS code held as a string (ADR-SEC-006);
               changed only by API-SEC-009 / API-SEC-010 / API-SEC-011, never by a form
  lastLoginAt: date-time · read-only · system-only
  isActiveFl : boolean · read-only — mirrors statusCode
  roles      : RoleSummaryResponse[] · read-only on this DTO — { roleId, code, nameAr, nameEn };
               written only through API-SEC-008
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — ENT-SEC-013 — طلب تسجيل معلّق / SignupRequest (pending sub-view)
Source DTO   : `SignupRequestResponse` — every property read-only here; the only input is the
               decision value APPROVE | REJECT of `SignupDecisionRequest` (pattern-constrained)
### F1-SCREEN — SCR-SEC-004
Search model : filters — username/email : string · LIKE · fullName : string · LIKE ·
               statusCode : string · EXACT (the code, from the shared lookup hook — ADR-SEC-006)
               paging + sort — page, size, sortField, sortDirection, carried inside the filter
               object per `UserSearchRequest`
Form model   : create — username, email, fullNameAr, fullNameEn, password (all required)
               edit   — email, fullNameAr, fullNameEn (required); username read-only
               excluded system fields: userPk, statusCode, lastLoginAt, isActiveFl, roles,
               audit fields
               roles are a separate model written through API-SEC-008, not a property of the
               create or update body
Container    : SIDE_DRAWER
No internal or tenant identifier is modelled; `passwordHash` is never returned by any
published endpoint and is absent here, as SRS A3 requires [POL-SEC-004].

<!-- SUB:F1-SCR-SEC-004:END -->

<!-- SUB:F1-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F1 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F1-MODEL — ENT-SEC-002 — الدور / Role
Source DTO   : `RoleResponse` (read) · `RoleCreateRequest` (write)
  rolePk        : number · read-only (PK) · system-only
  code          : string · required on create · maxLength 50 — the stable machine reference;
                  read-only once created
  nameAr        : string · required · maxLength 150
  nameEn        : string · required · maxLength 150
  descriptionAr : string · optional · maxLength 500
  descriptionEn : string · optional · maxLength 500
  isActiveFl    : boolean · read-only
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — grant tree nodes (read-only projections of ENT-SEC-004/005/006)
Source DTO   : `RegistryRowResponse` — module { moduleRegPk, code, nameAr, nameEn, isActiveFl,
               screens[] }, screen { screenRegPk, pageCode, moduleId, moduleCode, nameAr,
               nameEn, isActiveFl, actions[] }, action { actionRegPk, permissionCode, screenId,
               pageCode, actionCode, nameAr, nameEn, isActiveFl }
               every property read-only — the tree displays the registry, it does not edit it
### F1-MODEL — grant rows (ENT-SEC-007/008/009)
Source DTO   : `RoleModuleGrantResponse` { roleModuleGrantPk, roleId, moduleId, grantedBy,
               grantedAt } · `RoleScreenGrantResponse` { roleScreenGrantPk, roleId, screenId,
               grantedBy, grantedAt } · `RoleActionGrantResponse` { roleActionGrantPk, roleId,
               actionId, grantedBy, grantedAt } · `ModuleGrantRevokeResponse`
               { revokedScreenGrants, revokedActionGrants }
               every property read-only — a grant is created or revoked by identifier, never
               edited field by field
### F1-SCREEN — SCR-SEC-005
Search model : filters — code/name : string · LIKE (the published `RoleSearchRequest` carries a
               `name` field beside the generic `filters[]`) · isActiveFl : boolean · EXACT
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : create — code, nameAr, nameEn (required); descriptionAr, descriptionEn (optional)
               edit   — not modelled: no role-update endpoint is published (ADR-SEC-008)
               excluded system fields: rolePk, isActiveFl, audit fields
Container    : TREE_MASTER_DETAIL
The tree holds selection state only. Which nodes are granted is derived from the grant rows the
server returns, never from a local mirror that could outlive a revoke.

<!-- SUB:F1-SCR-SEC-005:END -->

<!-- SUB:F1-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F1 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

### F1-MODEL — ENT-SEC-004 / ENT-SEC-005 / ENT-SEC-006 — registry tree
Source DTO   : `RegistryRowResponse` (the nested module → screens → actions shape returned by
               API-SEC-021), plus `ModuleRegistryResponse`, `ScreenRegistryResponse` and
               `ActionRegistryResponse` for the single-row shapes
  module  : moduleRegPk : number · read-only (PK) · code : string · read-only ·
            nameAr, nameEn : string · read-only · isActiveFl : boolean · read-only ·
            screens : ScreenRegistryResponse[] · audit fields read-only
  screen  : screenRegPk : number · read-only (PK) · pageCode : string · read-only ·
            moduleId : number · read-only · moduleCode : string · read-only ·
            nameAr, nameEn : string · read-only · isActiveFl : boolean · read-only ·
            actions : ActionRegistryResponse[] · audit fields read-only
  action  : actionRegPk : number · read-only (PK) ·
            permissionCode : string · read-only · system-only — derived server-side as
            `PERM_<PAGE_CODE>_<ACTION>`, never composed on the client ·
            screenId : number · read-only · pageCode : string · read-only ·
            actionCode : string · read-only · nameAr, nameEn : string · read-only ·
            isActiveFl : boolean · read-only · audit fields read-only
Read-only    : every property of all three levels — this screen writes nothing (SRS B3)
### F1-SCREEN — SCR-SEC-006
Search model : filters — module code : string · LIKE · pageCode : string · EXACT (the published
               `RegistrySearchRequest` carries `pageCode` beside the generic `filters[]`)
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : none — no create, no update and no deactivate affordance is drawn (ADR-SEC-008)
Container    : TREE_MASTER_DETAIL
The three register DTOs (`ModuleRegistryCreateRequest`, `ScreenRegistryCreateRequest`,
`ActionRegistryCreateRequest`) are modelled as read-only reference shapes so a consuming
module's integrator can see what their own onboarding call must send; this frontend never
builds one (ADR-SEC-009).

<!-- SUB:F1-SCR-SEC-006:END -->

<!-- SUB:F1-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F1 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F1-MODEL — dashboard aggregates (no entity is edited)
Source DTO   : `DashboardResponse` — every property read-only, every property optional
  usersOverview : { total, active, disabled, pendingSignups } : number · read-only
  failedLogins24h : { count } : number · read-only — the derived figure SRS A3 documents as
                    computed from the audit log, never a stored column on ENT-SEC-001
  activeSessions : { count } : number · read-only
  recentActivity : AuditLogEntryResponse[] · read-only — { auditLogPk, eventTypeCode,
                   actorUserId, occurredAt, targetRef, detailsAr, detailsEn, ipAddress }
  rolesPermissionsSummary : { roleCount, privilegedRoleCount,
                   usersPerRole : { roleId, code, nameAr, nameEn, userCount }[] } · read-only
  onboardingFunnel : { pendingSignups, stalledCount } : number · read-only
Read-only    : all of the above — the dashboard has no input of any kind (SRS B3)
### F1-SCREEN — SCR-SEC-007
Search model : none — aggregate widgets, not a browsable list (SRS B2)
Form model   : none
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Every widget property is optional in the published DTO, and that is the permission mechanism:
a widget the caller may not see is absent from the response, so the model treats absence as
"not permitted", never as zero (REQ-SEC-023, ADR-SEC-005). No figure is stored, carried
between visits or recomputed on the client — REQ-SEC-022 requires each one computed live by
the server at the moment of opening.

<!-- SUB:F1-SCR-SEC-007:END -->

<!-- SUB:F1-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F1 · SCR-SEC-008 — سجل التدقيق / Audit log

### F1-MODEL — ENT-SEC-011 — سجل التدقيق / AuditLogEntry
Source DTO   : `AuditLogEntryResponse` — every property read-only (append-only entity)
  auditLogPk     : number · read-only (PK) · system-only
                   (the published property name for the SRS field `auditLogEntryPk`)
  eventTypeCode  : string · read-only · lookup — AUDIT_EVENT_TYPE code held as a string
                   (no enum — ADR-SEC-006)
  actorUserId    : number · read-only · optional — absent for an unauthenticated failed login
  occurredAt     : date-time · read-only · system-only
  targetRef      : string · read-only · optional
  detailsAr      : string · read-only · optional
  detailsEn      : string · read-only · optional
  ipAddress      : string · read-only · optional
Read-only    : every property — no form ever writes this entity [POL-SEC-009]
### F1-SCREEN — SCR-SEC-008
Search model : filters — eventTypeCode : string · EXACT (from the shared lookup hook) ·
               actorUserId : number · EXACT · occurredFrom/occurredTo : date · DATE_RANGE
               paging + sort — page, size, sortField, sortDirection inside the filter object
               export model — the same filter object rendered as the four query parameters
               `eventTypeCode, actorUserId, occurredFrom, occurredTo` that API-SEC-024 accepts
               (one filter object, two shapes — ADR-SEC-003)
Form model   : none — rows are system-appended only (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
This entity carries no `createdBy`/`updatedBy`: it is the audit record, and `actorUserId` +
`occurredAt` serve that purpose (SRS A3 note).

<!-- SUB:F1-SCR-SEC-008:END -->

<!-- SUB:F1-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F1 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F1-MODEL — ENT-SEC-010 — الجلسة النشطة / ActiveSession
Source DTO   : `ActiveSessionResponse` (read) · `SessionTerminationResponse` (terminate result)
  activeSessionPk : number · read-only (PK) · system-only
  userId          : number · read-only
  username        : string · read-only — the owner's login, returned beside the id so the list
                    needs no second call to name the user
  startedAt       : date-time · read-only · system-only
  lastActivityAt  : date-time · read-only · system-only
  ipAddress       : string · read-only · optional
  terminatedAt    : date-time · read-only — returned only by `SessionTerminationResponse`
Read-only    : every property — the only mutation is terminate, by identifier
               `tokenRef` is never returned by any published endpoint and is not modelled; the
               SRS marks it an opaque reference that is never exposed
### F1-SCREEN — SCR-SEC-009
Search model : filters — userId or username : string · LIKE · ipAddress : string · LIKE
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : none — no create and no update (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
`terminatedAt` / `terminatedBy` are null for every row this screen lists — API-SEC-025 returns
non-terminated sessions only — so neither is modelled as a column.

<!-- SUB:F1-SCR-SEC-009:END -->

<!-- SUB:F1-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F1 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F1-MODEL — effective menu (read-only projection of ENT-SEC-004 / ENT-SEC-005)
Source DTO   : `ModuleMenuResponse[]` — a bare array, **not** a `Page<T>` (this endpoint does
               not page, and the model must not assume the pagination envelope)
  moduleRegPk : number · read-only (PK) · system-only
  code        : string · read-only — the module code
  nameAr      : string · read-only
  nameEn      : string · read-only
  screens     : ScreenMenuResponse[] · read-only —
                { screenRegPk : number, pageCode : string, nameAr : string, nameEn : string }
Read-only    : every property — the menu is derived from the caller's effective grants and is
               never composed, extended or reordered on the client
### F1-SCREEN — SCR-SEC-010
Search model : none
Form model   : none
Container    : none — a global shell component with no route of its own (ADR-SEC-007)
Exactly two tiers are modelled, because the endpoint returns exactly two (REQ-SEC-021). The
`pageCode` set of this response is also the module's screen-level permission model: it is what
every route guard reads (ADR-SEC-005), so it is modelled once here and consumed by F4, never
duplicated as a static route table.

<!-- SUB:F1-SCR-SEC-010:END -->

<!-- PHASE:F1:END -->

<!-- PHASE:F2:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 2 — F2 — Data Hooks

What each screen needs from the API — not hook code. Every read query's cache key carries
**every** filter that changes the response, page and size included; page and page size live
inside the filter object and are never independent state. Every mutation declares its
invalidation. Components use the facade only; the facade uses the declared queries only
(server-state library: `tanstack-query`).

<!-- SUB:F2-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F2 · SCR-SEC-001 — تسجيل الدخول / Login

### F2-QUERY — API-SEC-001            traces=API-SEC-001,REQ-SEC-001,REQ-SEC-002
POST `/api/v1/sec/auth/login` · request `LoginRequest` { username, password } ·
response `LoginResponse` { accessToken, tokenType, expiresIn } · kind **mutation**
Cache key    : none — a mutation holds no cache entry
Errors       : `SEC-401-INVALID-CREDENTIALS` (401) → user message, shown above the form,
               ar: "بيانات الدخول غير صحيحة" · en: "Invalid credentials" (AC-SEC-002) ·
               `VALIDATION_ERROR` (400) → inline, per `error.fieldErrors[].field` ·
               `INTERNAL_ERROR` (500) → generic message
Loading      : LOCAL — the submit affordance is busy; the SRS states nothing about this call
               being slow, so no GLOBAL indicator (a GLOBAL one would need an ADR)
Cache policy : defaults
Invalidation : the entire server-state cache is discarded and API-SEC-027 (menu) is fetched
               fresh on success — a new session must not read another identity's cached data
### F2-SCREEN-INIT — SCR-SEC-001
Permission read : none — this screen is public (SRS Access summary: SEC_LOGIN is public), so
                  no VIEW is read and no guard runs before it
Lookups used    : none
Entity by id    : none — this screen has no edit mode
### F2-FACADE — SCR-SEC-001
Composes     : the API-SEC-001 mutation only
State it owns: the form's submitted/failed state and the last rejection message; no list, no
               selection, no filters
Operations   : signIn(credentials) → on success, store the token through the session
               transport and navigate to the caller's own landing screen resolved from the
               freshly fetched menu; on `SEC-401-INVALID-CREDENTIALS`, stay and show the
               message — never a partial session
The rejected path records a `LOGIN_FAILED` audit entry server-side (REQ-SEC-002); the client
neither writes nor counts it.

<!-- SUB:F2-SCR-SEC-001:END -->

<!-- SUB:F2-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F2 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F2-QUERY — API-SEC-002            traces=API-SEC-002,REQ-SEC-003
POST `/api/v1/sec/auth/signup` · request `SignupSubmitRequest` { email, fullNameAr,
fullNameEn } · response `SignupRequestResponse` · kind **mutation**
Cache key    : none
Errors       : `SEC-409-SIGNUP-DUP` (409) → user message (a request for that email already
               exists) · `VALIDATION_ERROR` (400) → inline per field · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : none for this caller — the submitter is unauthenticated and holds no cached
               list. An administrator's pending-sign-ups list (API-SEC-005 on SCR-SEC-004) is a
               different session and refreshes on its own key.
### F2-SCREEN-INIT — SCR-SEC-002
Permission read : none — public screen (SRS Access summary: SEC_SIGNUP)
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-002
Composes     : the API-SEC-002 mutation only
State it owns: submitted / not submitted, and the returned request's status for the
               confirmation text
Operations   : submitSignup(form) → on success switch to the confirmation state, which states
               that the request is PENDING and that no account exists yet (REQ-SEC-003)

<!-- SUB:F2-SCR-SEC-002:END -->

<!-- SUB:F2-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F2 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F2-QUERY — API-SEC-003            traces=API-SEC-003,REQ-SEC-006,REQ-SEC-029
POST `/api/v1/sec/auth/password-reset/request` · request `PasswordResetRequest` { email } ·
response `ConfirmationResponse` { messageAr, messageEn } · kind **mutation**
Cache key    : none
Errors       : `VALIDATION_ERROR` (400) → inline. There is deliberately no not-found path: the
               endpoint answers identically whether or not the email is registered, and the
               client must not infer one from a timing or a status difference.
Loading      : LOCAL
Cache policy : defaults
Invalidation : none
### F2-QUERY — API-SEC-004            traces=API-SEC-004,REQ-SEC-007,REQ-SEC-008
POST `/api/v1/sec/auth/password-reset/complete` · request `PasswordResetCompleteRequest`
{ token, newPassword } · response `ConfirmationResponse` · kind **mutation**
Cache key    : none
Errors       : `SEC-409-RESET-TOKEN-INVALID` (409) → user message for RULE-SEC-006,
               ar: "رابط إعادة التعيين غير صالح أو منتهي" ·
               en: "This reset link is invalid or has expired" (AC-SEC-008) ·
               `VALIDATION_ERROR` (400) → inline · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : none — the caller is unauthenticated and holds no cached entity
### F2-SCREEN-INIT — SCR-SEC-003
Permission read : none — public screen (SRS Access summary: SEC_PWD_RESET)
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-003
Composes     : the two mutations above
State it owns: the wizard step (mirrored from the route param, not owned independently), the
               confirmation text returned by whichever step ran, and the last rejection
Operations   : requestReset(email) → always ends in the same generic confirmation ·
               completeReset(token, newPassword) → on success route to SCR-SEC-001; on
               `SEC-409-RESET-TOKEN-INVALID` stay on step 2 with the message and change nothing
The optional notification of REQ-SEC-029 is dispatched entirely server-side when a token is
issued; no client call, state or affordance represents it.

<!-- SUB:F2-SCR-SEC-003:END -->

<!-- SUB:F2-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F2 · SCR-SEC-004 — المستخدمون / Users

### F2-QUERY — API-SEC-005            traces=API-SEC-005,REQ-SEC-009
POST `/api/v1/sec/users/search` · request `UserSearchRequest` { filters[], sortField,
sortDirection, page, size, fullName } · response `Page<UserResponse>` · kind **read query**
(a POST that mutates nothing — ADR-SEC-003)
Cache key    : `[users, filters]` where `filters` is the whole request object — username/email,
               fullName, statusCode, sortField, sortDirection **and page, size**. Page and page
               size live inside the filter object; they are never independent state.
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on the sort control · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : this key is refreshed by every mutation below
### F2-QUERY — API-SEC-006            traces=API-SEC-006,REQ-SEC-009
POST `/api/v1/sec/users` · request `UserCreateRequest` { username, email, fullNameAr,
fullNameEn, password } · response `UserResponse` · kind **mutation**
Errors       : `SEC-409-USER-DUP` (409) → user message, routed to the duplicated field
               (username or email) where the response names it · `VALIDATION_ERROR` → inline ·
               `ACCESS_DENIED` → forbidden message
Invalidation : `[users, *]`
### F2-QUERY — API-SEC-007            traces=API-SEC-007,REQ-SEC-009
PUT `/api/v1/sec/users/{id}` · request `UserUpdateRequest` { email, fullNameAr, fullNameEn } ·
response `UserResponse` · kind **mutation**
Errors       : `SEC-404-USER` (404) → user message · `SEC-409-USER-DUP` (409) → inline on email ·
               `VALIDATION_ERROR` → inline · `ACCESS_DENIED` → forbidden message
Invalidation : `[users, *]`
### F2-QUERY — API-SEC-008            traces=API-SEC-008,REQ-SEC-010,REQ-SEC-020
PUT `/api/v1/sec/users/{id}/roles` · request `UserRoleAssignmentRequest` { roleIds[] } ·
response `UserResponse` · kind **mutation**
Errors       : `SEC-409-SOD-CONFLICT` (409) → user message for RULE-SEC-005,
               ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" ·
               en: "This user already holds a conflicting action" (AC-SEC-020) ·
               `SEC-404-ROLE` / `SEC-404-USER` (404) → user message · `ACCESS_DENIED` → forbidden
Invalidation : `[users, *]` and `[roles, *]` (the roles-per-user figure the role summary shows)
### F2-QUERY — API-SEC-009            traces=API-SEC-009,REQ-SEC-011
DELETE `/api/v1/sec/users/{id}` · response `UserStatusResponse` { userPk, statusCode } ·
kind **mutation**
Errors       : `SEC-404-USER` → user message · `SEC-409-INVALID-TRANSITION` (409) → user
               message · `ACCESS_DENIED` → forbidden
Invalidation : `[users, *]` and `[sessions, *]` — deactivation ends that user's live sessions
               server-side (REQ-SEC-011), so SCR-SEC-009's list is stale the moment it succeeds
### F2-QUERY — API-SEC-010            traces=API-SEC-010,REQ-SEC-031
PATCH `/api/v1/sec/users/{id}` · response `UserStatusResponse` · kind **mutation**
Errors       : `SEC-404-USER` · `SEC-409-INVALID-TRANSITION` · `ACCESS_DENIED` — as above
Invalidation : `[users, *]`
### F2-QUERY — API-SEC-011            traces=API-SEC-011,REQ-SEC-004,REQ-SEC-005
PATCH `/api/v1/sec/signup-requests/{id}` · request `SignupDecisionRequest`
{ decision: APPROVE | REJECT } · kind **mutation**
Errors       : `SEC-404-SIGNUP` (404) → user message · `SEC-409-INVALID-TRANSITION` (409) →
               user message (the request is no longer PENDING) · `SEC-409-USER-DUP` (409) →
               user message (approval would duplicate an existing login) ·
               `VALIDATION_ERROR` → inline · `ACCESS_DENIED` → forbidden
Invalidation : `[users, *]` — an approval creates a user (REQ-SEC-004) and both decisions move
               the request out of the pending sub-view's list
### F2-LOOKUP — USER_STATUS
Endpoint `PENDING ADR-SEC-006` · key `USER_STATUS` · options shape { code, labelAr, labelEn } ·
ONE hook per key, shared by the status filter here and by any other screen needing it ·
long-lived cache. Until the lookup endpoint is published the hook resolves labels through the
single seeded resolver of ADR-SEC-006; it never returns a value list a validator could bind to.
### F2-SCREEN-INIT — SCR-SEC-004
Permission read : `SEC_USERS` present in the API-SEC-027 menu response → VIEW (ADR-SEC-005).
                  CREATE / UPDATE are not readable from any published endpoint; their
                  affordances render and the server's 403 is the authority.
Lookups used    : USER_STATUS (filter), SIGNUP_STATUS (pending sub-view display)
Entity by id    : none published — the drawer hydrates from the row already held by the
                  `[users, filters]` query's cache (ADR-SEC-008), so opening an edit performs
                  no second read and an invalidation re-reads through the same key
### F2-FACADE — SCR-SEC-004
Composes     : API-SEC-005 (list) · API-SEC-006, API-SEC-007, API-SEC-008, API-SEC-009,
               API-SEC-010, API-SEC-011 (mutations) · the USER_STATUS and SIGNUP_STATUS hooks
State it owns: the list derived from the query's data (never a copy of it), the selected user
               id (from the route param), the filter object including page and size, the active
               sub-view (list | pending), and a derived loading flag over the calls in flight
Operations   : createUser · updateUser · assignRoles · deactivateUser (usage check first: the
               confirmation names that live sessions will end) · reactivateUser ·
               decideSignup(APPROVE | REJECT)
Components use the facade only; the facade uses the declared queries only.

<!-- SUB:F2-SCR-SEC-004:END -->

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

<!-- SUB:F2-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F2 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F2-QUERY — API-SEC-022            traces=API-SEC-022,REQ-SEC-022,REQ-SEC-023
GET `/api/v1/sec/dashboard` · no request body · response `DashboardResponse` ·
kind **read query**
Cache key    : `[dashboard]` — no filter exists, so the key carries none
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message, shown in place of the
               grid · `INTERNAL_ERROR` (500) → generic. A widget the caller may not see is not
               an error: it is simply absent from the response (ADR-SEC-005).
Loading      : LOCAL, per widget — one slow figure must not hold the page. The SRS does not
               state that this call is slow, so no GLOBAL indicator.
Cache policy : **no caching of the figures across visits** — REQ-SEC-022 requires every figure
               computed from live data at the moment the dashboard is opened, so this entry is
               always considered stale and refetched on mount. This is a deliberate deviation
               from the defaults, required by the requirement itself rather than chosen; it is
               recorded here rather than in an ADR because the requirement states it outright.
Invalidation : not applicable — the screen writes nothing
### F2-SCREEN-INIT — SCR-SEC-007
Permission read : `SEC_DASHBOARD` present in the API-SEC-027 menu response → VIEW. Per-widget
                  permission is not read at all: the server returns only the widgets the caller
                  may see, so presence in the response **is** the permission (REQ-SEC-023,
                  ADR-SEC-005).
Lookups used    : AUDIT_EVENT_TYPE — the recent-activity widget shows event type codes and
                  resolves their labels through the shared hook (ADR-SEC-006)
Entity by id    : none
### F2-FACADE — SCR-SEC-007
Composes     : the API-SEC-022 query and the AUDIT_EVENT_TYPE lookup hook
State it owns: which widgets the response actually carried (the render list), and a derived
               per-widget loading flag; no figure is held beyond the render
Operations   : none — read-only (SRS B3). Each widget's navigation target is a route, not an
               operation: recent activity → SCR-SEC-008, active sessions → SCR-SEC-009,
               onboarding funnel → SCR-SEC-004's pending sub-view.

<!-- SUB:F2-SCR-SEC-007:END -->

<!-- SUB:F2-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F2 · SCR-SEC-008 — سجل التدقيق / Audit log

### F2-QUERY — API-SEC-023            traces=API-SEC-023,REQ-SEC-024,REQ-SEC-025
POST `/api/v1/sec/audit-log/search` · request `AuditLogEntrySearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<AuditLogEntryResponse>` ·
kind **read query** (ADR-SEC-003)
Cache key    : `[audit-log, filters]` — eventTypeCode, actorUserId, the occurredFrom/occurredTo
               range, sort **and page, size**, all inside the one filter object
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on the sort control ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults — audit entries are append-only, so a returned page never changes
Invalidation : none — this screen writes nothing; new entries arrive through a refetch, not an
               invalidation (REQ-SEC-024 appends server-side, never from here)
### F2-QUERY — API-SEC-024            traces=API-SEC-024,REQ-SEC-026
GET `/api/v1/sec/audit-log/export` · query parameters `eventTypeCode`, `actorUserId`,
`occurredFrom`, `occurredTo` · response CSV · kind **read query (file)**
Cache key    : none — an export is requested, never cached
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL — the export affordance is busy while the file is produced
Cache policy : not applicable
Invalidation : none
The export's four parameters are rendered from **the same filter object** the search key holds,
so an export always matches what the screen is showing — and never the current page, since
`page` and `size` are not among the export's parameters (AC-SEC-026, ADR-SEC-003).
### F2-LOOKUP — AUDIT_EVENT_TYPE
Endpoint `PENDING ADR-SEC-006` · key `AUDIT_EVENT_TYPE` · options shape { code, labelAr,
labelEn } · ONE hook per key, shared with SCR-SEC-007's recent-activity widget · long-lived
cache. Labels resolve through the single seeded resolver until the lookup endpoint exists; the
hook exposes no value list a validator could bind to.
### F2-SCREEN-INIT — SCR-SEC-008
Permission read : `SEC_AUDIT_LOG` present in the API-SEC-027 menu response → VIEW. Export
                  shares that same permission (SRS B4), so no second read exists to make.
Lookups used    : AUDIT_EVENT_TYPE (the event-type filter and the result column)
Entity by id    : none — an audit entry is never opened on its own
### F2-FACADE — SCR-SEC-008
Composes     : API-SEC-023 (search) · API-SEC-024 (export) · the AUDIT_EVENT_TYPE hook
State it owns: the entry list derived from the query's data, the filter object including page
               and size (mirrored to the route's search params so the filtered view is
               shareable — ADR-SEC-003), and a derived loading flag
Operations   : exportCurrentFilter() — builds the four query parameters from the same filter
               object the list is reading; there is no create, update or delete

<!-- SUB:F2-SCR-SEC-008:END -->

<!-- SUB:F2-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F2 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F2-QUERY — API-SEC-025            traces=API-SEC-025,REQ-SEC-027
POST `/api/v1/sec/sessions/search` · request `ActiveSessionSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<ActiveSessionResponse>` ·
kind **read query** (ADR-SEC-003)
Cache key    : `[sessions, filters]` — user/username, ipAddress, sort **and page, size**, in
               the one filter object
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on sort · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-SEC-026 below, and by API-SEC-009 on SCR-SEC-004 — deactivating
               a user ends that user's sessions server-side (REQ-SEC-011)
### F2-QUERY — API-SEC-026            traces=API-SEC-026,REQ-SEC-028
DELETE `/api/v1/sec/sessions/{id}` · response `SessionTerminationResponse` { activeSessionPk,
terminatedAt } · kind **mutation**
Errors       : `SEC-404-SESSION` (404) → user message · `SEC-409-ALREADY-TERMINATED` (409) →
               user message (the session ended between the render and the click; the list is
               refreshed rather than the row patched) · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[sessions, *]` and `[dashboard]` — the active-sessions figure changes with it
### F2-SCREEN-INIT — SCR-SEC-009
Permission read : `SEC_SESSIONS` present in the API-SEC-027 menu response → VIEW. The DELETE
                  (terminate) permission is not readable from any published endpoint; the
                  affordance renders and the server's 403 is the authority (ADR-SEC-005).
Lookups used    : none
Entity by id    : none — the list row carries `username` beside `userId`, so naming the session
                  owner needs no second call
### F2-FACADE — SCR-SEC-009
Composes     : API-SEC-025 (list) · API-SEC-026 (terminate)
State it owns: the session list derived from the query's data, the filter object including page
               and size, the row awaiting confirmation, and a derived loading flag
Operations   : terminateSession(id) — usage check first: the confirmation names the affected
               user, because the consequence lands on someone working at that moment

<!-- SUB:F2-SCR-SEC-009:END -->

<!-- SUB:F2-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F2 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F2-QUERY — API-SEC-027            traces=API-SEC-027,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033
GET `/api/v1/sec/menu` · no request body · response `array of ModuleMenuResponse` — a bare
array, **not** `Page<T>` · kind **read query**
Cache key    : `[menu]` — the response is per-caller and carries no filter, so the key carries
               none; it is discarded with the rest of the cache when the session changes
Errors       : `ACCESS_DENIED` (403) → the shell stays usable, states that navigation could not
               be loaded, and **no screen becomes reachable as a result** — a failed menu never
               widens access · `INTERNAL_ERROR` (500) → generic, same rule
Loading      : LOCAL — the shell renders before the menu resolves and shows no entry it has not
               received; nothing is guessed from a static route table
Cache policy : long-lived within a session — the effective grants change only when an
               administrator changes them
Invalidation : `[menu]` is invalidated by every grant mutation of SCR-SEC-005 (API-SEC-014,
               015, 016, 017) and refetched fresh after API-SEC-001, so a revoked grant cannot
               outlive its revoke in this client
### F2-SCREEN-INIT — SCR-SEC-010
Permission read : none of its own — the published endpoint requires only an authenticated
                  caller, and this screen is not a securable destination (SRS B4). This query
                  **is** the permission source every other screen's guard reads (ADR-SEC-005).
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-010
Composes     : the API-SEC-027 query only
State it owns: the module → screen tree derived from the query's data and the expanded module;
               it owns no list of its own and composes no entry locally
Operations   : none — read-only and fully derived (SRS B3)
This facade exposes one derived predicate, `holdsScreen(pageCode)`, computed from the response
it already holds. Every route guard in F4 and every RF5 block reads that predicate, so the
screen-level gate has exactly one source and one call site.

<!-- SUB:F2-SCR-SEC-010:END -->

<!-- PHASE:F2:END -->

<!-- PHASE:F3:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 3 — F3 — Forms & Validators

One block per `RULE-*` enforced on a form, plus the field constraints the published DTOs
state. No frontend-only validation the SRS does not state; every message is read from its
catalog code, never hard-coded; the locale resolves session → browser → `ar`; and a caller
without the write permission is answered by the server rather than by a pre-emptively
disabled field (ADR-SEC-005). Schemas are written with `zod` + `react-hook-form`.

<!-- SUB:F3-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F3 · SCR-SEC-001 — تسجيل الدخول / Login

Validation timing for this form: **on submit** (declared once for the whole form). A login
form that validates while the user types leaks nothing useful and only interrupts them.
### F3-FIELD — SCR-SEC-001
username · REQUIRED · LENGTH (maxLength 100, from `LoginRequest`) · when submit
password · REQUIRED · LENGTH (maxLength 200, from `LoginRequest`) · when submit
Validation shape : both fields non-empty and within their published maximum; nothing more.
                   No pattern, no minimum length and no complexity rule is asserted here —
                   the SRS states none for the login form, and inventing one would reject a
                   credential the server would have accepted. Written with `zod` +
                   `react-hook-form`.
No RULE-* is enforced on this form. REQ-SEC-002's rejection is a server decision
(`SEC-401-INVALID-CREDENTIALS`), surfaced as the user message of the F2 block above, with the
catalog's own text and never a message composed on the client.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-001:END -->

<!-- SUB:F3-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F3 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

Validation timing for this form: **on blur for the email, on submit for the rest**.
### F3-FIELD — SCR-SEC-002
email      · REQUIRED · LENGTH (maxLength 255) · PATTERN (a valid email address —
             SRS ENT-SEC-013 states "valid email") · when blur
fullNameAr · REQUIRED · LENGTH (maxLength 200) · when submit
fullNameEn · REQUIRED · LENGTH (maxLength 200) · when submit
Validation shape : three required strings within their published maxima, the first also
                   matching an email shape. Written with `zod` + `react-hook-form`.
No UNIQUE_CHECK runs on this form: the only endpoint that could answer "is this email already
registered" is `API-SEC-005`, which requires `PERM_SEC_USERS_VIEW`, and the submitter here is
unauthenticated. A duplicate is answered by the server as `SEC-409-SIGNUP-DUP` after submit —
the same answer, without exposing the user directory to an anonymous caller.
No RULE-* is enforced on this form.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-002:END -->

<!-- SUB:F3-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F3 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

Validation timing for this form: **on submit**, per step.
### F3-FIELD — SCR-SEC-003 step 1
email · REQUIRED · LENGTH (maxLength 255) · PATTERN (valid email) · when submit
### F3-FIELD — SCR-SEC-003 step 2
token           · REQUIRED · LENGTH (maxLength 200) · when submit
newPassword     · REQUIRED · LENGTH (maxLength 200) · when submit
confirmPassword · REQUIRED · BUSINESS_RULE (equal to newPassword) · when submit — client-side
                  only, never sent; it is the SRS's "confirm password" field (B3)
Validation shape : step 1 one required email; step 2 a required token, a required new password
                   within the published maximum, and an equality check between the two password
                   fields. No password-complexity rule is asserted: the SRS refers to "the
                   platform's password rules" (AC-SEC-007) without stating them, and the server
                   is the only place they exist. Written with `zod` + `react-hook-form`.
### F3-VALIDATION — RULE-SEC-006      traces=REQ-SEC-008,AC-SEC-008
Statement : The system shall reject a password-reset submission whose token is expired or
            already used.
Message   : from the catalog code `SEC-409-RESET-TOKEN-INVALID` —
            ar: "رابط إعادة التعيين غير صالح أو منتهي" ·
            en: "This reset link is invalid or has expired"
Scope     : CREATE (the step-2 submission)
Field     : token · kind BUSINESS_RULE · when submit
Validation shape : **server-side only.** Expiry and single use are properties of a token the
            client cannot inspect — no published endpoint returns a token's `expiresAt` or
            `usedAt`. The form submits and routes the returned catalog code to a user message
            above the fields, leaving every field as the user left it (AC-SEC-008: "changes
            nothing"). The message is read from the catalog, never hard-coded.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-003:END -->

<!-- SUB:F3-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F3 · SCR-SEC-004 — المستخدمون / Users

Validation timing for this form: **on blur for the unique fields, on submit for the rest**
(declared once for the whole drawer).
### F3-FIELD — SCR-SEC-004 (create)
username   · REQUIRED · LENGTH (maxLength 100) · UNIQUE_CHECK · when blur
email      · REQUIRED · LENGTH (maxLength 255) · PATTERN (valid email) · UNIQUE_CHECK · when blur
fullNameAr · REQUIRED · LENGTH (maxLength 200) · when submit
fullNameEn · REQUIRED · LENGTH (maxLength 200) · when submit
password   · REQUIRED · LENGTH (maxLength 200) · when submit — create only
### F3-FIELD — SCR-SEC-004 (edit)
username   · read-only — not an input at all; `UserUpdateRequest` does not carry it
email      · REQUIRED · LENGTH · PATTERN · UNIQUE_CHECK (current record excluded) · when blur
fullNameAr, fullNameEn · REQUIRED · LENGTH · when submit
UNIQUE_CHECK : async, on blur, via `API-SEC-005` with an EQUALS filter on the field; the
               current record is excluded on edit by comparing the returned `userPk`. A
               failure of the check never blocks submit on its own — the authority is the
               server's `SEC-409-USER-DUP`, routed inline to the same field.
### F3-VALIDATION — RULE-SEC-005      traces=REQ-SEC-020,AC-SEC-020
Statement : The system shall prevent assigning a user, by any combination of roles, both
            actions of a module-declared conflicting pair.
Message   : from the catalog code `SEC-409-SOD-CONFLICT` —
            ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" ·
            en: "This user already holds a conflicting action"
Scope     : CREATE and UPDATE of the role assignment (API-SEC-008)
Field     : roles (the multi-select) · kind BUSINESS_RULE · when submit
Validation shape : **server-side only.** Conflicting pairs are declared by the owning consumer
            module and no published endpoint exposes them, so the client cannot know which
            selection conflicts before it is sent. The returned catalog code routes to a user
            message on the roles field and the selection is left exactly as the administrator
            made it, so the offending choice is visible rather than silently reverted.
Business-code fields: none — no SEC entity carries a platform-numbered business code
(SRS §3.3 NUMBERING test: all "No"), so there is no read-only code display on this form.
LOOKUP_VALID : `statusCode` is never an input on this screen (it is changed by API-SEC-009 /
            010 / 011), so no lookup validator exists to bind — which is also why ADR-SEC-006's
            missing lookup endpoint costs this form nothing.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `ACCESS_DENIED` on submit and
the form shows the localized forbidden message; the fields are not pre-emptively disabled,
because the permission is not readable (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-004:END -->

<!-- SUB:F3-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F3 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

Validation timing for this form: **on blur for the role code, on submit for the rest**.
### F3-FIELD — SCR-SEC-005 (create role)
code          · REQUIRED · LENGTH (maxLength 50) · UNIQUE_CHECK · when blur
nameAr        · REQUIRED · LENGTH (maxLength 150) · when submit
nameEn        · REQUIRED · LENGTH (maxLength 150) · when submit
descriptionAr · optional · LENGTH (maxLength 500) · when submit
descriptionEn · optional · LENGTH (maxLength 500) · when submit
UNIQUE_CHECK  : async, on blur, via `API-SEC-012` with an EQUALS filter on `code`; no edit mode
                exists on this screen, so there is no current record to exclude. The authority
                remains the server's `SEC-409-ROLE-DUP`, routed inline to `code`.
The role code is displayed read-only everywhere after creation — it is the stable machine
reference (SRS ENT-SEC-002) and is never an input a second time.
### F3-VALIDATION — RULE-SEC-001      traces=REQ-SEC-013,AC-SEC-013
Statement : The system shall prevent a screen grant for a role that does not hold the screen's
            module grant.
Message   : from the catalog code `SEC-409-NO-MODULE-GRANT` —
            ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" ·
            en: "Cannot grant a screen without first granting its module"
Scope     : CREATE (a screen grant, API-SEC-016)
Field     : the screen node of the grant tree · kind BUSINESS_RULE · when submit
Validation shape : the tree's own reachability expresses the rule — a screen node is offered
            only beneath a module the role already holds, so the refusal is rare by
            construction. It is never relied on as the enforcement: the server's catalog code
            is routed to a user message beside the node and the tree is re-read, never patched.
### F3-VALIDATION — RULE-SEC-002      traces=REQ-SEC-014,AC-SEC-014
Statement : The system shall prevent an action grant for a role that does not hold the action's
            screen grant.
Message   : from the catalog code `SEC-409-NO-SCREEN-GRANT` —
            ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" ·
            en: "Cannot grant an action without first granting its screen"
Scope     : CREATE (an action grant, API-SEC-017)
Field     : the action node of the grant tree · kind BUSINESS_RULE · when submit
Validation shape : as RULE-SEC-001, one level down — an action node is offered only beneath a
            granted screen; the server's code is the authority.
### F3-VALIDATION — RULE-SEC-007      traces=REQ-SEC-030,AC-SEC-030
Statement : The system shall require a role to hold the VIEW action grant on a screen before
            any other action grant on that screen takes effect for it.
Message   : from the catalog code `SEC-409-NO-VIEW-GRANT` —
            ar: "يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة" ·
            en: "The VIEW action must be granted on this screen first"
Scope     : CREATE (an action grant other than VIEW, API-SEC-017)
Field     : the action node · kind BUSINESS_RULE · when submit
Validation shape : the tree presents VIEW as the first action of every screen and marks the
            others unreachable until it is held; the server's code is the authority.
### F3-VALIDATION — RULE-SEC-003      traces=REQ-SEC-015,AC-SEC-015
Statement : The system shall delete every screen grant and action grant that module covered for
            that role when its module grant is revoked.
Message   : ar: "سيتم سحب كل منح الشاشات والإجراءات ضمن هذه الوحدة لهذا الدور" ·
            en: "Every screen and action grant under this module for this role will be revoked"
            (SRS A5 — this is a confirmation, not a rejection: the rule always succeeds)
Scope     : ALL (the module-revoke step, API-SEC-015)
Field     : the module node · kind BUSINESS_RULE · when submit
Validation shape : a blocking confirmation before the call, carrying the message above; after
            the call the returned `revokedScreenGrants` / `revokedActionGrants` counts are
            shown as the outcome and the tree is re-read from the server.
### F3-VALIDATION — RULE-SEC-005      traces=REQ-SEC-020,AC-SEC-020
Statement : The system shall prevent assigning a user, by any combination of roles, both
            actions of a module-declared conflicting pair.
Message   : from the catalog code `SEC-409-SOD-CONFLICT` — ar / en as on SCR-SEC-004
Scope     : CREATE (an action grant, API-SEC-017)
Field     : the action node · kind BUSINESS_RULE · when submit
Validation shape : server-side only — the conflicting pairs are the owning module's
            declaration and no endpoint publishes them (as on SCR-SEC-004).
LOOKUP_VALID : none — every selectable value on this screen is a registry node the server
            returned, so there is no static list to validate against.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `ACCESS_DENIED` on a grant and
the tree shows the localized forbidden message, unchanged (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-005:END -->

<!-- SUB:F3-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F3 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

This screen has **no form**: every field is read-only, registration happens through the
registering module's own onboarding call, and the one edit the SRS names — deactivating a stale
row — has no published endpoint (ADR-SEC-008, ADR-SEC-009). There is therefore no validation
timing to declare and no field block to write.
### F3-VALIDATION — RULE-SEC-004      traces=REQ-SEC-018,AC-SEC-018
Statement : The system shall reject a screen registration whose module code has no
            ModuleRegistry row.
Message   : from the catalog code `SEC-409-MODULE-NOT-REGISTERED` —
            ar: "الوحدة غير مسجّلة" · en: "Module is not registered"
Scope     : CREATE (a screen registration, API-SEC-019)
Field     : `moduleCode` of `ScreenRegistryCreateRequest` · kind BUSINESS_RULE · when submit
Validation shape : **not enforced on any form in this frontend.** The rule binds
            `API-SEC-019`, which this frontend does not call (ADR-SEC-009); it is recorded here
            so the block that will enforce it — in the registering module's own screen — has a
            reconciled contract to inherit, message and catalog code included. No client-side
            pre-check is written, because a registry lookup before the call would be a second
            source of truth for a rule the server already owns.
Only the search filters accept input, and they are filters rather than a form: `module code`
(LIKE) and `pageCode` (EXACT), both plain strings with no published constraint to assert.
Locale       : session → browser → `ar`.
Permission-driven behaviour: the screen is read-only for every caller, so no permission
changes a field's behaviour here.

<!-- SUB:F3-SCR-SEC-006:END -->

<!-- SUB:F3-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F3 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

This screen has **no form and no input of any kind** (SRS B3: "Read-only; no data entry"),
so it declares no validation timing and carries no field block.
No `RULE-*` is enforced here. The one behavioural requirement that could look like a validation
— REQ-SEC-023, hiding a widget the caller's role does not grant — is not a client-side rule at
all: the server returns only the widgets the caller may see, and the screen renders exactly
what it received (ADR-SEC-005). A client-side permission test would be a second, weaker copy of
a decision the server already made.
Number and date formatting follow the active locale (session → browser → `ar`); no figure is
rounded, aggregated or recomputed on the client, because REQ-SEC-022 requires every figure to
be the server's live computation.
Permission-driven behaviour: none beyond the above — there is no field to make read-only.

<!-- SUB:F3-SCR-SEC-007:END -->

<!-- SUB:F3-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F3 · SCR-SEC-008 — سجل التدقيق / Audit log

This screen has **no entry form**: audit rows are system-appended and never hand-created
(SRS B3). Only the filter set accepts input, and its validation timing is **on change** for the
selects and **on blur** for the date range.
### F3-FIELD — SCR-SEC-008 (filters)
eventTypeCode · optional · LOOKUP_VALID · when change
actorUserId   · optional · when change
occurredFrom / occurredTo · optional · DATE_RANGE (from ≤ to) · when blur
Validation shape : an optional code, an optional actor, and a date range whose start is not
                   after its end — the only constraint asserted, and it is a property of the
                   pair rather than a business rule. Written with `zod` + `react-hook-form`.
LOOKUP_VALID  : the event-type filter's value must be one of the runtime-loaded options of the
                `AUDIT_EVENT_TYPE` hook — **never a static list**. That hook is
                `PENDING ADR-SEC-006`: until the lookup endpoint is published the validator is
                not written at all, because the only list available would be a hardcoded enum,
                which `profile.conventions.lookups` forbids. An unrecognised code is answered
                by the server as an empty result, which is the correct answer to a filter
                matching nothing.
No `RULE-*` is enforced on this screen: REQ-SEC-024's append and the entries' immutability
[POL-SEC-009] are server properties with no client surface.
Locale        : session → browser → `ar`; `detailsAr` / `detailsEn` are rendered by the active
                locale, and the export carries both as the server writes them.
Permission-driven behaviour: a caller without VIEW never reaches this screen (F4 guard); export
shares that same permission, so no affordance on it is separately gated.

<!-- SUB:F3-SCR-SEC-008:END -->

<!-- SUB:F3-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F3 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

This screen has **no entry form** (SRS B3: no create, no update). Only the filter set
accepts input, with timing **on change**.
### F3-FIELD — SCR-SEC-009 (filters)
user / username · optional · LENGTH (no published maximum — none asserted) · when change
ipAddress       · optional · when change
Validation shape : two optional free-text filters; no pattern is asserted on the IP filter,
                   because a partial address is a legitimate LIKE search and a strict pattern
                   would reject it. Written with `zod` + `react-hook-form`.
No `RULE-*` is enforced on this screen. REQ-SEC-028's termination is a server operation whose
only client surface is the confirmation described in F2, and `SEC-409-ALREADY-TERMINATED` is
routed to a user message followed by a re-read of the list — never a local removal of the row.
No LOOKUP_VALID and no UNIQUE_CHECK apply: nothing on this screen is a lookup field and nothing
is created.
Locale        : session → browser → `ar`; `startedAt` and `lastActivityAt` are rendered in the
                tenant timezone by the active locale.
Permission-driven behaviour: a caller without VIEW never reaches this screen (F4 guard); the
terminate affordance renders for anyone who does, and `ACCESS_DENIED` is shown as the localized
forbidden message (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-009:END -->

<!-- SUB:F3-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F3 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

This component has **no form and no input** (SRS B3: "read-only, derived"), so it
declares no validation timing and carries no field block.
No `RULE-*` is enforced here, and none could be: the menu asserts nothing — it renders what the
caller's effective grants already are (REQ-SEC-021) and omits what they are not (REQ-SEC-032).
The one rule that matters at this boundary, REQ-SEC-033, is explicitly **not** a client-side
validation: the server verifies the module grant on every request regardless of what the menu
shows, and this component's absence of an entry is a usability consequence, never the
enforcement (ADR-SEC-005).
Nothing is composed locally: no static route table is merged into the response, no entry is
sorted into existence, and no module the response omitted is added back from a cached earlier
menu. A menu that fails to load renders no entry rather than a remembered one.
Locale       : session → browser → `ar`; `nameAr` / `nameEn` are rendered by the active locale
               at both tiers.
Permission-driven behaviour: the whole component **is** the permission-driven behaviour of this
module's frontend — it is the single source every route guard reads (F4, RF5).

<!-- SUB:F3-SCR-SEC-010:END -->

<!-- PHASE:F3:END -->

<!-- PHASE:F4:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 4 — F4 — Screens & Routes

One block per `SCR-*`: routes, chunk, guard, components, mode, facade, shared UI and
cross-module citations. Routes are named by the container pattern — `SIDE_DRAWER` →
SearchPage + FormDrawer toggled by a route param; `TREE_MASTER_DETAIL` → TreePage with the
tree route registered **before** any `:id` route; `FULL_PAGE` with no entry sub-view → a
single Page and no entry route. One lazy chunk per composite screen: Search and Entry are
separate components under ONE `SCR-*` sharing ONE chunk, never a second chunk for a
sub-view. Every `PERM_*` name below is the backend's, never invented here.

<!-- SUB:F4-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F4 · SCR-SEC-001 — تسجيل الدخول / Login

### F4-SCREEN — SCR-SEC-001            traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001
Routes       : `/login` — the only route; no `new`, no `:id`, no `:id/edit` (this screen has no
               record to address)
Chunk        : one lazy chunk for this composite screen (`react-router`); the three public
               screens are separate chunks, since a signed-in user loads none of them
Guard        : **none — public.** SRS Access summary marks SEC_LOGIN public, so no
               `PERM_*` gates it. The inverse guard applies instead: a caller who already holds
               a session is sent to their own landing screen rather than shown this form again.
Components   : `LoginPage` (route-level) · `CredentialsForm` (presentational)
Mode         : not applicable — no CREATE / EDIT / VIEW mode exists; there is no route match to
               resolve one from
Facade       : the SCR-SEC-001 facade of F2; the page never calls the mutation directly
Shared UI    : the card shell, text field, password field, primary button and inline message of
               the design system — nothing else is rendered
Cross-module : none — no `UXD-*` is cited, because no field on this screen displays another
               module's data
On success the menu (API-SEC-027) is fetched before navigating, so the landing screen is
resolved from the caller's real grants rather than from a default route that may not be theirs.

<!-- SUB:F4-SCR-SEC-001:END -->

<!-- SUB:F4-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F4 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F4-SCREEN — SCR-SEC-002            traces=REQ-SEC-003,AC-SEC-003,API-SEC-002
Routes       : `/sign-up` — the only route
Chunk        : one lazy chunk for this composite screen
Guard        : **none — public** (SRS Access summary: SEC_SIGNUP). A caller holding a session
               is sent to their landing screen instead, as on SCR-SEC-001.
Components   : `SignUpPage` (route-level) · `SignUpForm` · `SignUpSubmittedNotice`
               (presentational)
Mode         : not applicable — CREATE is the screen's only purpose and is not resolved from a
               route match
Facade       : the SCR-SEC-002 facade of F2
Shared UI    : card shell, text fields, primary button, inline field errors, notice block
Cross-module : none
After a successful submission the page renders `SignUpSubmittedNotice` in place of the form, so
a second submission is a deliberate navigation rather than a second click on a cleared form
(REQ-SEC-003 creates a pending request, not an account).

<!-- SUB:F4-SCR-SEC-002:END -->

<!-- SUB:F4-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F4 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F4-SCREEN — SCR-SEC-003            traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004
Routes       : `/password-reset` (step 1 — request) · `/password-reset/complete` (step 2 —
               token and new password; the emailed link points here and carries the token as a
               search param). The step is addressed by the route, never by local-only state.
Chunk        : **one** lazy chunk for both steps — they are one composite screen under one
               `SCR-*`, and a second chunk for a sub-view would break the composite invariant
Guard        : **none — public** (SRS Access summary: SEC_PWD_RESET)
Components   : `PasswordResetPage` (route-level, hosts both steps) · `ResetRequestForm` ·
               `ResetCompleteForm` · `ResetConfirmationNotice` (presentational)
Mode         : not applicable — the wizard step, not a CREATE/EDIT/VIEW mode, is what the route
               match resolves
Facade       : the SCR-SEC-003 facade of F2
Shared UI    : card shell, text field, password field, primary button, inline errors, notice
Cross-module : none
Arriving at `/password-reset/complete` with a token in the search params opens step 2 directly
with the field pre-filled, so the emailed link is a single click; arriving without one leaves
the token field editable rather than blocking the route.

<!-- SUB:F4-SCR-SEC-003:END -->

<!-- SUB:F4-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F4 · SCR-SEC-004 — المستخدمون / Users

### F4-SCREEN — SCR-SEC-004            traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011
Routes       : base slug `users`, under the module segment —
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

<!-- SUB:F4-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F4 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F4-SCREEN — SCR-SEC-005            traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017
Routes       : base slug `roles`, under the module segment —
               `/security/roles` (master list) ·
               `/security/roles/new` (create form — a **static** segment registered BEFORE the
               id routes) ·
               `/security/roles/:roleId` (the role's grant tree — the tree route, registered
               before any deeper id route) ·
               `/security/roles/:roleId/modules/:moduleId` (a module node selected inside the
               tree — the node route param)
Chunk        : one lazy chunk for this composite screen — master list, create form and grant
               tree share it
Guard        : every route element guarded by `PERM_SEC_ROLES_VIEW`, evaluated as `SEC_ROLES`
               present in the menu response (ADR-SEC-005). CREATE and UPDATE render their
               affordances; the server's 403 is the authority.
Components   : `RolesTreePage` (route-level, `TREE_MASTER_DETAIL` — hosts the role master list,
               the grant tree and the permanently visible detail) · `RoleCreatePage`
               (route-level) · `RoleMasterList`, `GrantTree`, `GrantNodeDetail`,
               `ModuleRevokeConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new` → CREATE, `/:roleId` → VIEW
               with the tree editable in place. There is no EDIT mode: no role-update endpoint
               is published (ADR-SEC-008).
Facade       : the SCR-SEC-005 facade of F2
Shared UI    : two-pane tree layout, tree node with a checkbox affordance, data table, filter
               bar, text field, textarea, confirmation dialog, inline errors, message banner
Cross-module : none — the tree's nodes are rows of SEC's own registry entities
               (ENT-SEC-004/005/006), not another module's data, so no `UXD-*` is cited
The tree route is registered before the node route, so a role id is never matched as a module
id. Un-checking a screen or action node is not offered — only the module-level revoke exists
(API-SEC-015, ADR-SEC-008) — and the tree states this where a reader would expect otherwise.

<!-- SUB:F4-SCR-SEC-005:END -->

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

<!-- SUB:F4-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F4 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F4-SCREEN — SCR-SEC-007            traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022
Routes       : `/security/dashboard` — a single route; no `new`, no `:id`, no `:id/edit`
               (there is no record to address)
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_DASHBOARD_VIEW`, evaluated as `SEC_DASHBOARD` present in
               the menu response (ADR-SEC-005). Per-widget permission is **not** guarded on the
               client: the server returns only the widgets the caller may see (REQ-SEC-023).
Components   : `SecurityDashboardPage` (route-level) · `UsersOverviewWidget`,
               `FailedLoginsWidget`, `ActiveSessionsWidget`, `RecentActivityWidget`,
               `RolesPermissionsWidget`, `OnboardingFunnelWidget` (presentational)
Mode         : VIEW only — read-only screen, no mode to resolve
Facade       : the SCR-SEC-007 facade of F2
Shared UI    : widget card, stat figure, compact table, skeleton, empty state, error state,
               localized message banner
Cross-module : none
Each widget renders only when its property is present in `DashboardResponse`, and each links to
the screen it summarizes — recent activity → `/security/audit-log`, active sessions →
`/security/sessions`, onboarding funnel → `/security/users/pending`. Those links are rendered
whether or not the caller holds the target screen; a caller who does not is stopped by that
screen's own guard rather than by a second, weaker check here.

<!-- SUB:F4-SCR-SEC-007:END -->

<!-- SUB:F4-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F4 · SCR-SEC-008 — سجل التدقيق / Audit log

### F4-SCREEN — SCR-SEC-008            traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024
Routes       : base slug `audit-log`, under the module segment — `/security/audit-log` (search)
               only. No `new`, no `:id`, no `:id/edit`: audit rows are never created and never
               opened alone (SRS B3).
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_AUDIT_LOG_VIEW`, evaluated as `SEC_AUDIT_LOG` present in
               the menu response (ADR-SEC-005). Export shares that permission (SRS B4), so its
               affordance carries no separate guard.
Components   : `AuditLogPage` (route-level) · `AuditFilters`, `AuditResultTable`,
               `ExportButton` (presentational)
Mode         : VIEW only — read-only screen
Facade       : the SCR-SEC-008 facade of F2
Shared UI    : data table, filter bar, select, date-range field, secondary button, skeleton,
               empty state, localized message banner
Cross-module : none
The filter set is mirrored into the route's search params, so a filtered investigation is
shareable by URL even though the search itself is a POST (ADR-SEC-003). Export builds its four
query parameters from that same filter object and deliberately omits `page` and `size`, so it
exports the investigation rather than the visible page (AC-SEC-026).

<!-- SUB:F4-SCR-SEC-008:END -->

<!-- SUB:F4-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F4 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F4-SCREEN — SCR-SEC-009            traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026
Routes       : base slug `sessions`, under the module segment — `/security/sessions` (search)
               only. No `new` and no `:id/edit`: there is no entry form (SRS B3), and the sole
               mutation is a per-row terminate that needs no route of its own.
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_SESSIONS_VIEW`, evaluated as `SEC_SESSIONS` present in the
               menu response (ADR-SEC-005). `PERM_SEC_SESSIONS_DELETE` is not readable from any
               published endpoint, so the terminate affordance renders and the server's 403 is
               the authority.
Components   : `ActiveSessionsPage` (route-level) · `SessionFilters`, `SessionResultTable`,
               `TerminateSessionConfirm` (presentational)
Mode         : VIEW only — read-only list with one action
Facade       : the SCR-SEC-009 facade of F2
Shared UI    : data table, filter bar, text field, destructive button, confirmation dialog,
               skeleton, empty state, localized message banner
Cross-module : none
Terminating confirms first and names the affected user (AC-SEC-028); on success the row leaves
the list through a re-read rather than a local removal, because the screen's contract is
"sessions that have not been terminated" and the server decides which those are.

<!-- SUB:F4-SCR-SEC-009:END -->

<!-- SUB:F4-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F4 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F4-SCREEN — SCR-SEC-010            traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027
Routes       : **none of its own** — this is the application shell's navigation component,
               rendered inside every authenticated route rather than matched by one. It is not
               a securable destination and has no page code (SRS B4).
Chunk        : none — it belongs to the shell bundle, not to a lazy chunk. A menu loaded lazily
               would leave the shell without navigation on first paint.
Guard        : the component itself requires only an authenticated caller, as its endpoint
               does. It **is** the guard source for every other screen: each route element in
               F4 above tests `holdsScreen(pageCode)` against this component's facade
               (ADR-SEC-005).
Components   : `AppShellNav` (shell-level) · `ModuleMenuGroup`, `ScreenMenuItem`
               (presentational). No "Page" suffix appears here, because none of these is a
               route-level page.
Mode         : not applicable — no route match, so no mode
Facade       : the SCR-SEC-010 facade of F2, which exposes the derived `holdsScreen(pageCode)`
               predicate the guards read
Shared UI    : navigation list, disclosure group, active-item indicator, skeleton, empty state
Cross-module : none — the entries are rows of SEC's own registry entities
A module the response omits is absent from the menu entirely (REQ-SEC-032) and its routes are
refused by their own guards (REQ-SEC-033); neither behaviour is the enforcement, which is the
server's on every request. When the menu fails to load the shell renders no entry and no route
becomes reachable — a failure narrows access, never widens it.

<!-- SUB:F4-SCR-SEC-010:END -->

<!-- PHASE:F4:END -->

<!-- PHASE:SEC-FE:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 5 — SEC-FE

The frontend half of the security model, per `SCR-*`: the navigation guard and the per-action
UI behaviour. Permission names are the backend registry's, read from the api-docs and never
redeclared. Two mechanisms exist in this module and each block states which one gates it:
the **menu gate** (`SEC_<PAGE>` present in the API-SEC-027 response) and the **server's 403**,
surfaced as the localized catalog message — the consequence of no endpoint publishing the
caller's action-level permissions (ADR-SEC-005). Never split — level-1 only.

### SEC-FE · SCR-SEC-001 — تسجيل الدخول / Login
Permissions      : public — no permission gates this screen (SRS Access summary: SEC_LOGIN)
Navigation guard : none. The inverse guard applies: a caller who already holds a session
is routed to their own landing screen rather than shown the form again.
Per action       : no `PERM_*` action exists for this screen. The rejected-credentials path is
a server decision (`SEC-401-INVALID-CREDENTIALS`) shown as the localized catalog message —
identical for a wrong password, an unknown username and a disabled one (AC-SEC-002), so the
screen reveals nothing about which of the three occurred.

### SEC-FE · SCR-SEC-002 — التسجيل الذاتي / Sign-up
Permissions      : public — no permission gates this screen (SRS Access summary: SEC_SIGNUP)
Navigation guard : none, as on SCR-SEC-001.
Per action       : no `PERM_*` action exists. A duplicate request is answered by the server as
`SEC-409-SIGNUP-DUP` after submit rather than by a client pre-check, so an anonymous caller
cannot probe the user directory (see F3).

### SEC-FE · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password
Permissions      : public — no permission gates this screen (SRS Access summary: SEC_PWD_RESET)
Navigation guard : none.
Per action       : no `PERM_*` action exists. Step 1 answers identically whether or not the
email is registered, and step 2's `SEC-409-RESET-TOKEN-INVALID` is shown as the localized
catalog message without distinguishing an expired token from an already-used one — both are
"invalid or expired" (AC-SEC-008).

### SEC-FE · SCR-SEC-004 — المستخدمون / Users
Permissions      : `PERM_SEC_USERS_VIEW`, `PERM_SEC_USERS_CREATE`, `PERM_SEC_USERS_UPDATE`
Navigation guard : `SEC_USERS` must be present in the API-SEC-027 menu response; a caller
without it is sent to the unauthorized destination, and every route of this screen — search,
pending, new, `:id`, `:id/edit` — carries the same guard.
Per action       : VIEW → the gate above, exact. CREATE (new user) and UPDATE (edit, assign
roles, activate, deactivate, approve/reject a sign-up) → the affordances render for a caller
who holds the screen, and `ACCESS_DENIED` from the server is shown as the localized forbidden
message (ADR-SEC-005). DELETE → no delete action exists on this screen: deactivation is an
UPDATE (REQ-SEC-011), and the SRS Access summary leaves SEC_USERS' DELETE column empty.
Permission names are the backend registry's, read from the api-docs, never redeclared here.

### SEC-FE · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions
Permissions      : `PERM_SEC_ROLES_VIEW`, `PERM_SEC_ROLES_CREATE`, `PERM_SEC_ROLES_UPDATE`
Navigation guard : `SEC_ROLES` must be present in the menu response; every route of this
screen carries it.
Per action       : VIEW → the gate above. CREATE (new role) and UPDATE (every grant-tree edit,
including the module revoke) → the affordances render and the server's `ACCESS_DENIED` is the
authority. DELETE → the SRS grants SEC_ROLES a DELETE for deactivating a role, but no endpoint
is published for it, so no affordance is drawn and nothing is gated (ADR-SEC-008).
The three grant refusals of this screen — `SEC-409-NO-MODULE-GRANT`, `SEC-409-NO-SCREEN-GRANT`,
`SEC-409-NO-VIEW-GRANT` — are authorization outcomes the administrator is *editing*, not
authorization failures of the administrator: they are shown as their own localized rule
messages beside the node (F3), never as the generic forbidden message.

### SEC-FE · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry
Permissions      : `PERM_SEC_MODULE_REGISTRY_VIEW`, `PERM_SEC_MODULE_REGISTRY_UPDATE`
Navigation guard : `SEC_MODULE_REGISTRY` must be present in the menu response; every
route of this screen carries it.
Per action       : VIEW → the gate above. UPDATE → the SRS grants it for deactivating a stale
row, but no endpoint is published, so no affordance is drawn and nothing is gated
(ADR-SEC-008). CREATE → registration is the registering module's own call, not an affordance of
this screen (ADR-SEC-009). DELETE → no such action on this screen.
The screen is read-only for every caller who reaches it.

### SEC-FE · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard
Permissions      : `PERM_SEC_DASHBOARD_VIEW`, plus the VIEW of each summarized screen
Navigation guard : `SEC_DASHBOARD` must be present in the menu response.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE on this screen.
Per widget → **not gated on the client at all**: the server returns only the widgets the caller
may see, so a widget's absence from `DashboardResponse` is the permission decision
(REQ-SEC-023, ADR-SEC-005). The screen never tests a widget permission itself, because a
second test would be a weaker copy of the server's.
A widget's link to its source screen is rendered unconditionally; the target screen's own guard
stops a caller who does not hold it.

### SEC-FE · SCR-SEC-008 — سجل التدقيق / Audit log
Permissions      : `PERM_SEC_AUDIT_LOG_VIEW`
Navigation guard : `SEC_AUDIT_LOG` must be present in the menu response.
Per action       : VIEW → the gate above. Export shares the same permission and is not a
separate mutation (SRS B4), so its affordance is not separately gated and `ACCESS_DENIED` on it
would be the same denial as on the list. There is no CREATE, UPDATE or DELETE: audit entries
are append-only and immutable [POL-SEC-009].

### SEC-FE · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management
Permissions      : `PERM_SEC_SESSIONS_VIEW`, `PERM_SEC_SESSIONS_DELETE`
Navigation guard : `SEC_SESSIONS` must be present in the menu response.
Per action       : VIEW → the gate above. DELETE (terminate) → the affordance renders for a
caller who holds the screen and `ACCESS_DENIED` is shown as the localized forbidden message
(ADR-SEC-005). There is no CREATE and no UPDATE on this screen.

### SEC-FE · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu
Permissions      : none of its own — the endpoint requires an authenticated caller only
Navigation guard : none — this component is not a destination (SRS B4). It is the guard
**source**: `holdsScreen(pageCode)`, derived from the API-SEC-027 response, is what every route
element above evaluates.
Per action       : no action exists on this component. A module the caller does not hold is
absent from the menu entirely (REQ-SEC-032), and a route reached directly without its grant is
refused by that route's guard here and by the server on every request (REQ-SEC-033) — the
server's check is the enforcement, the menu's omission is not.
A failure to load the menu renders no entry and grants no route; access narrows, never widens.

**Across every screen.** A forbidden response is shown as its localized catalog message, never
as a silent no-op and never as a generic failure. An unauthenticated response returns the
caller to `/login` and discards the server-state cache, so no data of the previous identity
survives into the next. No screen composes a permission name, and no screen holds a local copy
of the caller's grants beyond the menu response the SCR-SEC-010 facade already owns.

<!-- PHASE:SEC-FE:END -->

<!-- PHASE:ALIGN-FE:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 6 — ALIGN-FE

The alignment self-check is this phase's content: see the section of the same name below,
whose verdict row is written by the orchestrator from the analyze report. Never split —
level-1 only.

<!-- PHASE:ALIGN-FE:END -->

---

## Alignment self-check (ALIGN-FE) — SEC v1

```
ALIGN-FE — SEC v1
SCREENS      10 SRS screen entries ↔ 10 SCR (1:1) │ every SCR has a block in F1, F2, F3 and
             F4 (40 SUB blocks) │ composite separation declared on every composite screen │
             container pattern set for all three entry screens (SCR-SEC-004 SIDE_DRAWER,
             SCR-SEC-005 and SCR-SEC-006 TREE_MASTER_DETAIL); the six screens with no entry
             sub-view carry FULL_PAGE and SCR-SEC-010 none, per ADR-SEC-007
API          27 of 27 documented endpoints have an RF2 block │ no endpoint is used that the
             api-docs lack │ every mutation declares its invalidation │ page and size sit
             inside the cache key's filter object on all five paged reads │ three documented
             endpoints (API-SEC-018/019/020) are bound but deliberately uncalled —
             ADR-SEC-009
LOOKUPS      3 keys, 3 shared hooks (USER_STATUS, SIGNUP_STATUS, AUDIT_EVENT_TYPE), each
             PENDING ADR-SEC-006 │ no enum is modelled anywhere │ no lookup validator binds
             a static list — the one LOOKUP_VALID (SCR-SEC-008's event-type filter) is left
             unwritten rather than hardcoded
VALIDATION   7 of 7 RULE-* accounted for: RULE-SEC-001/002/003/005/007 on SCR-SEC-005,
             RULE-SEC-005 also on SCR-SEC-004, RULE-SEC-006 on SCR-SEC-003, RULE-SEC-004
             recorded on SCR-SEC-006 as bound to an endpoint this frontend does not call │
             every message cites its catalog code │ no hard-coded message │ no
             frontend-only rule
ROUTES       every authenticated route guarded; the three public screens are guarded by
             nothing because the SRS marks them public │ tree routes registered before :id
             routes on SCR-SEC-005 and SCR-SEC-006, and the static `pending` / `new`
             segments before :id on SCR-SEC-004 │ pages use the facade, never a query │
             component naming matches the container pattern on every screen
UXD          0 minted and 0 cited — SEC is ROOT (SRS A8: no consumed entity), so no screen
             displays another module's data and no foreign-data field exists to need one
SECURITY     every SCR has an RF5 block in SEC-FE │ every permission name used
             (PERM_SEC_USERS_*, PERM_SEC_ROLES_*, PERM_SEC_MODULE_REGISTRY_*,
             PERM_SEC_DASHBOARD_VIEW, PERM_SEC_AUDIT_LOG_VIEW, PERM_SEC_SESSIONS_*) is one
             the api-docs attribute to a published endpoint
LANGUAGES    every label and every rule message carries ar + en; the audit details and the
             reset confirmations are rendered from the server's own ar/en pair
TRACES       every PHASE and every SUB carries traces= │ every target exists: REQ-SEC-001..
             033, their AC counterparts, API-SEC-001..027 and SCR-SEC-001..010
DECISIONS    ADR-SEC-003 (search shape) · ADR-SEC-004 (API id binding) · ADR-SEC-005
             (no action-level permission endpoint) · ADR-SEC-006 (no lookup endpoint) ·
             ADR-SEC-007 (container pattern for screens with no entry sub-view) ·
             ADR-SEC-008 (operations with no endpoint) · ADR-SEC-009 (documented endpoints
             this frontend does not call) · ADR-SEC-010 (SCR-SEC-004's form vs SRS B3's input
             list) — all ACCEPTED, all non-breaking
RESULT       PASSED ✓ — 0 findings
```

### Operations coverage

| Operation | API | SCR action | Route | Status |
|---|---|---|---|---|
| login | API-SEC-001 | SCR-SEC-001 sign in | /login | ✓ |
| submit sign-up | API-SEC-002 | SCR-SEC-002 submit | /sign-up | ✓ |
| request password reset | API-SEC-003 | SCR-SEC-003 step 1 | /password-reset | ✓ |
| complete password reset | API-SEC-004 | SCR-SEC-003 step 2 | /password-reset/complete | ✓ |
| search users | API-SEC-005 | SCR-SEC-004 search | /security/users | ✓ |
| create user | API-SEC-006 | SCR-SEC-004 create | /security/users/new | ✓ |
| update user | API-SEC-007 | SCR-SEC-004 edit | /security/users/:id/edit | ✓ |
| assign roles | API-SEC-008 | SCR-SEC-004 assign roles | /security/users/:id/edit | ✓ |
| deactivate user | API-SEC-009 | SCR-SEC-004 deactivate | /security/users | ✓ |
| reactivate user | API-SEC-010 | SCR-SEC-004 reactivate | /security/users | ✓ |
| approve / reject sign-up | API-SEC-011 | SCR-SEC-004 decide | /security/users/pending | ✓ |
| search roles | API-SEC-012 | SCR-SEC-005 search | /security/roles | ✓ |
| create role | API-SEC-013 | SCR-SEC-005 create | /security/roles/new | ✓ |
| grant module | API-SEC-014 | SCR-SEC-005 grant module | /security/roles/:roleId | ✓ |
| revoke module (cascade) | API-SEC-015 | SCR-SEC-005 revoke module | /security/roles/:roleId | ✓ |
| grant screen | API-SEC-016 | SCR-SEC-005 grant screen | /security/roles/:roleId | ✓ |
| grant action | API-SEC-017 | SCR-SEC-005 grant action | /security/roles/:roleId | ✓ |
| register module | API-SEC-018 | — consuming module's own call | — (ADR-SEC-009) | ✗ |
| register screen | API-SEC-019 | — consuming module's own call | — (ADR-SEC-009) | ✗ |
| register action | API-SEC-020 | — consuming module's own call | — (ADR-SEC-009) | ✗ |
| search registry | API-SEC-021 | SCR-SEC-006 search; SCR-SEC-005 grant tree | /security/registry | ✓ |
| dashboard summary | API-SEC-022 | SCR-SEC-007 render | /security/dashboard | ✓ |
| search audit log | API-SEC-023 | SCR-SEC-008 search | /security/audit-log | ✓ |
| export audit log | API-SEC-024 | SCR-SEC-008 export | /security/audit-log | ✓ |
| list active sessions | API-SEC-025 | SCR-SEC-009 search | /security/sessions | ✓ |
| terminate session | API-SEC-026 | SCR-SEC-009 terminate | /security/sessions | ✓ |
| effective menu | API-SEC-027 | SCR-SEC-010 render + every guard | — (shell component) | ✓ |
| update role | — none published | SCR-SEC-005 — not drawn | — (ADR-SEC-008) | ✗ |
| deactivate role | — none published | SCR-SEC-005 — not drawn | — (ADR-SEC-008) | ✗ |
| revoke screen / action grant | — none published | SCR-SEC-005 — not drawn | — (ADR-SEC-008) | ✗ |
| deactivate registry row | — none published | SCR-SEC-006 — not drawn | — (ADR-SEC-008) | ✗ |
| read one user by id | — none published | SCR-SEC-004 — hydrated from cache | — (ADR-SEC-008) | ✗ |
| logout | — none published | — not drawn | — (ADR-SEC-008) | ✗ |

Twenty-four rows carry a route and a ✓; nine carry a ✗ with the ADR that explains it — three
endpoints published for a caller that is not this frontend, and six operations with no
endpoint at all. No row is a ✗ for want of a decision.

## Hand-off

The implementer reads the phases in profile order — F1 models, F2 hooks, F3 forms, F4 screens
and routes, SEC-FE guards — takes design intent from `ui-ux-spec-sec.md`, and takes every
request and response shape from `_inputs/api-docs-sec.md`. No route, component, permission or
field that is not traceable to an F-block above is invented: a gap is an ADR in
`erp/decisions/SEC/`, never an invention. The plan and its registry are split by the toolkit
into `packages/frontend-execution/` and delivered on the frontend delivery branch after the
`gate:pass-2` verdict, then tagged.

══════════════════════════════════════════════════════════════════
