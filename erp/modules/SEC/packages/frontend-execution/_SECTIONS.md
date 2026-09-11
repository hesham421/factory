<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
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
