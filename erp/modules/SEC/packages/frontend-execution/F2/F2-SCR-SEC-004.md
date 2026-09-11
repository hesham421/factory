<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-004 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-004, AC-SEC-005, AC-SEC-009, AC-SEC-010, AC-SEC-011, AC-SEC-031, API-SEC-005, API-SEC-006, API-SEC-007, API-SEC-008, API-SEC-009, API-SEC-010, API-SEC-011, REQ-SEC-004, REQ-SEC-005, REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-031, SCR-SEC-004 -->
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
