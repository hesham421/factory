# FRONTEND TEST PLAN — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Scope : module (SEC)
Sources: srs-sec.md v1 · frontend-execution-plan-sec.md v1 · registry-srs-sec.md v1 ·
         registry-exec-fe-sec.md v1
Framework: agnostic (profile.stack.testing.frontend). REDUCED: **no** — P3.2 has run for SEC,
so every test case below binds to a real `SCR-*` and its route.
TC count: 30 — TC-SEC-034 … TC-SEC-063, continuing the module's one TC sequence after the
backend plan's highest id (TC-SEC-033). No id is renumbered and no backend TC is touched.
Open ADRs: 0 new. The plan cites ADR-SEC-005, ADR-SEC-008 and ADR-SEC-009 where a screen's
behaviour follows one of them.
SUPERSEDES the REDUCED stub this file previously held, which recorded that P3.2 had not run
for SEC and that no version of the frontend execution plan existed. That is no longer true:
SCR-SEC-001..010 exist and the plan binds all 27 API ids.
══════════════════════════════════════════════════════════════════

Scope is `module`, so this run derives from SEC's own `AC-*` only. The integration phase
`INT-UXD` is **absent by rule**, and for SEC it could never be otherwise: the module mints no
`UXD-*` at all, because SRS §A8 records it as ROOT — it consumes no entity owned by another
module, so no screen of its displays foreign data.

<!-- PHASE:TEST-PLAN-FE:START traces=AC-SEC-001,AC-SEC-002,AC-SEC-003,AC-SEC-004,AC-SEC-005,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-016,AC-SEC-017,AC-SEC-019,AC-SEC-020,AC-SEC-021,AC-SEC-022,AC-SEC-023,AC-SEC-025,AC-SEC-026,AC-SEC-027,AC-SEC-028,AC-SEC-030,AC-SEC-031,AC-SEC-032,AC-SEC-033,REQ-SEC-001,REQ-SEC-002,REQ-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-016,REQ-SEC-017,REQ-SEC-019,REQ-SEC-020,REQ-SEC-021,REQ-SEC-022,REQ-SEC-023,REQ-SEC-025,REQ-SEC-026,REQ-SEC-027,REQ-SEC-028,REQ-SEC-030,REQ-SEC-031,REQ-SEC-032,REQ-SEC-033 -->
## TEST-PLAN-FE — SEC v1

Thirty test cases, so the phase splits (threshold: TC count > 8) into the two labels the
profile names: `UI-FLOWS` for the per-screen flows, and `INT-FLOW` for the flows that cross
screens — the dynamic menu, which every other screen's guard reads, and the dashboard widget
whose absence and whose target route are two separate mechanisms. Every case derives from
exactly one `AC-*`, cites the `SCR-*` and route it exercises, and asserts the catalog message
in both languages wherever a `RULE-*` fires.

<!-- SUB:UI-FLOWS:START traces=AC-SEC-001,REQ-SEC-001,SCR-SEC-001,API-SEC-001,AC-SEC-002,REQ-SEC-002,AC-SEC-003,REQ-SEC-003,SCR-SEC-002,API-SEC-002,AC-SEC-006,REQ-SEC-006,SCR-SEC-003,API-SEC-003,AC-SEC-007,REQ-SEC-007,API-SEC-004,AC-SEC-008,REQ-SEC-008,AC-SEC-004,REQ-SEC-004,SCR-SEC-004,API-SEC-011,AC-SEC-005,REQ-SEC-005,AC-SEC-009,REQ-SEC-009,API-SEC-006,AC-SEC-010,REQ-SEC-010,API-SEC-008,AC-SEC-011,REQ-SEC-011,API-SEC-009,AC-SEC-031,REQ-SEC-031,API-SEC-010,AC-SEC-012,REQ-SEC-012,SCR-SEC-005,API-SEC-014,AC-SEC-013,REQ-SEC-013,API-SEC-016,AC-SEC-014,REQ-SEC-014,API-SEC-017,AC-SEC-015,REQ-SEC-015,API-SEC-015,AC-SEC-020,REQ-SEC-020,AC-SEC-030,REQ-SEC-030,AC-SEC-016,REQ-SEC-016,SCR-SEC-006,API-SEC-021,AC-SEC-017,REQ-SEC-017,AC-SEC-019,REQ-SEC-019,AC-SEC-022,REQ-SEC-022,SCR-SEC-007,API-SEC-022,AC-SEC-025,REQ-SEC-025,SCR-SEC-008,API-SEC-023,AC-SEC-026,REQ-SEC-026,API-SEC-024,AC-SEC-027,REQ-SEC-027,SCR-SEC-009,API-SEC-025,AC-SEC-028,REQ-SEC-028,API-SEC-026 -->
### SUB — UI-FLOWS

Per-screen flows: the public pages, user and role administration, the read-only registry, the dashboard, the audit log and the sessions screen.

<!-- TC:TC-SEC-034:START traces=AC-SEC-001,REQ-SEC-001,SCR-SEC-001,API-SEC-001 -->
### TC-SEC-034 — sign in with correct credentials
Derived from : AC-SEC-001 (REQ-SEC-001) · Exercises: SCR-SEC-001 /login · API-SEC-001
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an active user with a known username and password; no session held
Steps        : 1. open /login 2. enter the username and password 3. submit
Expected     : a session is created and the caller lands on the screen their own grants resolve to — the menu is fetched before navigating, so the landing screen is theirs and not a fixed default
Test data    : an ACTIVE user
<!-- TC:TC-SEC-034:END -->

<!-- TC:TC-SEC-035:START traces=AC-SEC-002,REQ-SEC-002,SCR-SEC-001,API-SEC-001 -->
### TC-SEC-035 — rejected credentials return to the form with one message for all three causes
Derived from : AC-SEC-002 (REQ-SEC-002) · Exercises: SCR-SEC-001 /login · API-SEC-001
Rule / code  : SEC-401-INVALID-CREDENTIALS
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a wrong password, an unknown username, and a disabled username — three attempts
Steps        : 1. submit a wrong password 2. submit an unknown username 3. submit a disabled username
Expected     : all three return to /login with the identical message — ar: "بيانات الدخول غير صحيحة" · en: "Invalid credentials" — no session is issued, and the screen reveals nothing about which of the three occurred. The `LOGIN_FAILED` audit entry is the server's; the client neither writes nor counts it
Test data    : three rejected attempts
<!-- TC:TC-SEC-035:END -->

<!-- TC:TC-SEC-036:START traces=AC-SEC-003,REQ-SEC-003,SCR-SEC-002,API-SEC-002 -->
### TC-SEC-036 — submitting the sign-up form creates a pending request and no account
Derived from : AC-SEC-003 (REQ-SEC-003) · Exercises: SCR-SEC-002 /sign-up · API-SEC-002
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a valid, not-already-registered email
Steps        : 1. open /sign-up 2. fill email and both name labels 3. submit
Expected     : the form is replaced by a confirmation stating the request is pending and that no access exists yet — not cleared, so a second submission is a deliberate navigation; no session is created
Test data    : a new email address
<!-- TC:TC-SEC-036:END -->

<!-- TC:TC-SEC-037:START traces=AC-SEC-006,REQ-SEC-006,SCR-SEC-003,API-SEC-003 -->
### TC-SEC-037 — requesting a password reset always ends in the same generic confirmation
Derived from : AC-SEC-006 (REQ-SEC-006) · Exercises: SCR-SEC-003 /password-reset · API-SEC-003
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: one registered email and one that is not registered
Steps        : 1. open /password-reset 2. submit the registered email 3. repeat with the unregistered one
Expected     : both submissions end in the identical confirmation; the screen does not reveal whether the email is registered, and no password has changed in either case
Test data    : two email addresses
<!-- TC:TC-SEC-037:END -->

<!-- TC:TC-SEC-038:START traces=AC-SEC-007,REQ-SEC-007,SCR-SEC-003,API-SEC-004 -->
### TC-SEC-038 — completing a reset with a valid token changes the password
Derived from : AC-SEC-007 (REQ-SEC-007) · Exercises: SCR-SEC-003 /password-reset/complete · API-SEC-004
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an unexpired, unused token carried by the emailed link, and a new password
Steps        : 1. follow the emailed link to /password-reset/complete 2. read the pre-filled token field 3. enter the new password and its confirmation 4. submit
Expected     : the token arrives pre-filled from the link so the step is a single click; the password is changed and the caller is routed to /login. The confirm-password field is client-side only and is never sent
Test data    : a fresh token
<!-- TC:TC-SEC-038:END -->

<!-- TC:TC-SEC-039:START traces=AC-SEC-008,REQ-SEC-008,SCR-SEC-003,API-SEC-004 -->
### TC-SEC-039 — an expired or used reset token is refused and changes nothing
Derived from : AC-SEC-008 (REQ-SEC-008) · Exercises: SCR-SEC-003 /password-reset/complete · API-SEC-004
Rule / code  : RULE-SEC-006 → SEC-409-RESET-TOKEN-INVALID
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a token that is expired, and one already used
Steps        : 1. submit the expired token with a new password 2. submit the already-used token
Expected     : both stay on step 2 with the message — ar: "رابط إعادة التعيين غير صالح أو منتهي" · en: "This reset link is invalid or has expired" — every field is left as the user left it and nothing is changed; the screen does not distinguish expired from used, because the catalog gives one message for both
Test data    : two invalid tokens
<!-- TC:TC-SEC-039:END -->

<!-- TC:TC-SEC-040:START traces=AC-SEC-004,REQ-SEC-004,SCR-SEC-004,API-SEC-011 -->
### TC-SEC-040 — approving a pending sign-up creates an active user
Derived from : AC-SEC-004 (REQ-SEC-004) · Exercises: SCR-SEC-004 /security/users/pending · API-SEC-011
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a PENDING SignupRequest; signed in holding SEC_USERS view and update
Steps        : 1. open /security/users/pending 2. approve the request 3. return to the users list
Expected     : a user is created ACTIVE from the request's email and names, the request leaves the pending sub-view, and the new user appears in the users list — the pending view is a tab beside the list, not a screen of its own
Test data    : a PENDING request
<!-- TC:TC-SEC-040:END -->

<!-- TC:TC-SEC-041:START traces=AC-SEC-005,REQ-SEC-005,SCR-SEC-004,API-SEC-011 -->
### TC-SEC-041 — rejecting a pending sign-up creates no user
Derived from : AC-SEC-005 (REQ-SEC-005) · Exercises: SCR-SEC-004 /security/users/pending · API-SEC-011
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a PENDING SignupRequest
Steps        : 1. open the pending sub-view 2. reject the request 3. search the users list for its email
Expected     : the request is marked rejected, leaves the pending view, and no user with that email exists
Test data    : a PENDING request
<!-- TC:TC-SEC-041:END -->

<!-- TC:TC-SEC-042:START traces=AC-SEC-009,REQ-SEC-009,SCR-SEC-004,API-SEC-006 -->
### TC-SEC-042 — create a user from the drawer
Derived from : AC-SEC-009 (REQ-SEC-009) · Exercises: SCR-SEC-004 /security/users/new · API-SEC-006
Rule / code  : SEC-409-USER-DUP
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a unique username and email; signed in holding SEC_USERS view and create
Steps        : 1. open /security/users and choose New 2. fill username, email, both names and the password 3. leave the unique fields (blur) 4. submit
Expected     : the drawer opens over the list so the population stays visible; the user is created and appears in the list. The password is write-only and is never echoed or returned. A duplicate would be answered by the server and routed inline to the field it names
Test data    : a unique username and email
<!-- TC:TC-SEC-042:END -->

<!-- TC:TC-SEC-043:START traces=AC-SEC-010,REQ-SEC-010,SCR-SEC-004,API-SEC-008 -->
### TC-SEC-043 — assign roles to a user
Derived from : AC-SEC-010 (REQ-SEC-010) · Exercises: SCR-SEC-004 /security/users/:id/edit · API-SEC-008
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an existing user and two active roles
Steps        : 1. open the user's drawer 2. select both roles in the multi-select 3. save
Expected     : one assignment exists per selected role; the roles multi-select is written through its own call, not as a property of the user create or update body
Test data    : two active roles
<!-- TC:TC-SEC-043:END -->

<!-- TC:TC-SEC-044:START traces=AC-SEC-011,REQ-SEC-011,SCR-SEC-004,API-SEC-009 -->
### TC-SEC-044 — deactivating a user ends their sessions, and the confirmation says so
Derived from : AC-SEC-011 (REQ-SEC-011) · Exercises: SCR-SEC-004 /security/users/:id · API-SEC-009
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active user holding one active session
Steps        : 1. choose Deactivate on that user's row 2. read the confirmation 3. confirm 4. open /security/sessions
Expected     : the confirmation names the consequence — the user's live sessions will end — before the act; the user's status becomes disabled and the sessions list no longer shows their session, because deactivation invalidates the sessions cache as well as the users cache
Test data    : a user with one live session
<!-- TC:TC-SEC-044:END -->

<!-- TC:TC-SEC-045:START traces=AC-SEC-031,REQ-SEC-031,SCR-SEC-004,API-SEC-010 -->
### TC-SEC-045 — reactivating a user restores access
Derived from : AC-SEC-031 (REQ-SEC-031) · Exercises: SCR-SEC-004 /security/users/:id · API-SEC-010
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a user with status DISABLED
Steps        : 1. choose Reactivate on that row — the same affordance, its label following the row's status 2. confirm
Expected     : the status becomes active and the row returns to the active-only result set; Deactivate and Reactivate are one affordance whose label follows the row, never two competing buttons
Test data    : a DISABLED user
<!-- TC:TC-SEC-045:END -->

<!-- TC:TC-SEC-046:START traces=AC-SEC-012,REQ-SEC-012,SCR-SEC-005,API-SEC-014 -->
### TC-SEC-046 — grant a module to a role
Derived from : AC-SEC-012 (REQ-SEC-012) · Exercises: SCR-SEC-005 /security/roles/:roleId · API-SEC-014
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an active role and an active registered module
Steps        : 1. open /security/roles and select the role 2. grant the module in the tree
Expected     : one module grant exists and the module's screens become reachable nodes in the tree beside the role — the tree and the detail are two panes of one screen, not two screens
Test data    : one active module
<!-- TC:TC-SEC-046:END -->

<!-- TC:TC-SEC-047:START traces=AC-SEC-013,REQ-SEC-013,SCR-SEC-005,API-SEC-016 -->
### TC-SEC-047 — granting a screen before its module is refused in the tree
Derived from : AC-SEC-013 (REQ-SEC-013) · Exercises: SCR-SEC-005 /security/roles/:roleId · API-SEC-016
Rule / code  : RULE-SEC-001 → SEC-409-NO-MODULE-GRANT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a role with no module grant for FIN
Steps        : 1. select the role 2. attempt to grant a FIN screen
Expected     : no screen grant is created and the message is shown beside the node — ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" · en: "Cannot grant a screen without first granting its module". It is rendered as its own rule message, never as the generic forbidden message: this is an authorization outcome the administrator is editing, not an authorization failure of the administrator
Test data    : a role without the FIN module grant
<!-- TC:TC-SEC-047:END -->

<!-- TC:TC-SEC-048:START traces=AC-SEC-014,REQ-SEC-014,SCR-SEC-005,API-SEC-017 -->
### TC-SEC-048 — granting an action before its screen is refused in the tree
Derived from : AC-SEC-014 (REQ-SEC-014) · Exercises: SCR-SEC-005 /security/roles/:roleId · API-SEC-017
Rule / code  : RULE-SEC-002 → SEC-409-NO-SCREEN-GRANT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a role with no screen grant for a given screen
Steps        : 1. select the role 2. attempt to grant an action on that screen
Expected     : no action grant is created and the message is shown beside the node — ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" · en: "Cannot grant an action without first granting its screen"
Test data    : a role without that screen's grant
<!-- TC:TC-SEC-048:END -->

<!-- TC:TC-SEC-049:START traces=AC-SEC-015,REQ-SEC-015,SCR-SEC-005,API-SEC-015 -->
### TC-SEC-049 — revoking a module cascades, and the confirmation names what it will take
Derived from : AC-SEC-015 (REQ-SEC-015) · Exercises: SCR-SEC-005 /security/roles/:roleId · API-SEC-015
Rule / code  : RULE-SEC-003
Scenario     : STATE · data class VALID · language ALL
Preconditions: a role holding one module grant plus two screen grants and three action grants under it
Steps        : 1. select the role 2. revoke the module grant 3. read the confirmation naming the cascade 4. confirm 5. re-read the tree
Expected     : the confirmation names the cascade before the act; afterwards the module grant and every screen and action grant it covered are gone, and the tree collapses that module's nodes — none is left behind. There is no individual screen- or action-grant revoke affordance, because no endpoint publishes one (ADR-SEC-008)
Test data    : 1 module + 2 screen + 3 action grants
<!-- TC:TC-SEC-049:END -->

<!-- TC:TC-SEC-050:START traces=AC-SEC-020,REQ-SEC-020,SCR-SEC-005,API-SEC-008 -->
### TC-SEC-050 — a conflicting action assignment is refused on the roles field
Derived from : AC-SEC-020 (REQ-SEC-020) · Exercises: SCR-SEC-004 /security/users/:id/edit and SCR-SEC-005 · API-SEC-008
Rule / code  : RULE-SEC-005 → SEC-409-SOD-CONFLICT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: two actions declared conflicting by their owning module, and a user already holding one of them through some role
Steps        : 1. open that user's drawer 2. select a role that would give them the other conflicting action 3. submit
Expected     : the assignment is refused and the message is shown on the roles field — ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" · en: "This user already holds a conflicting action" — and the selection is left exactly as the administrator made it, so the offending choice stays visible rather than being silently reverted. The check is server-side only: no endpoint exposes the conflicting pairs
Test data    : a conflicting action pair
<!-- TC:TC-SEC-050:END -->

<!-- TC:TC-SEC-051:START traces=AC-SEC-030,REQ-SEC-030,SCR-SEC-005,API-SEC-017 -->
### TC-SEC-051 — an action without VIEW on the same screen is denied
Derived from : AC-SEC-030 (REQ-SEC-030) · Exercises: SCR-SEC-005 /security/roles/:roleId · API-SEC-017
Rule / code  : RULE-SEC-007 → SEC-409-NO-VIEW-GRANT
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: a role holding CREATE on a screen but not VIEW on that same screen
Steps        : 1. sign in as that role's user 2. attempt the CREATE action on that screen
Expected     : the action is denied until VIEW is granted on the same screen — the gateway convention, enforced by the server; the administrator editing the grant tree sees the rule message beside the node, and the acting user sees the localized forbidden message
Test data    : CREATE granted, VIEW not
<!-- TC:TC-SEC-051:END -->

<!-- TC:TC-SEC-052:START traces=AC-SEC-016,REQ-SEC-016,SCR-SEC-006,API-SEC-021 -->
### TC-SEC-052 — the registry tree shows a registered module
Derived from : AC-SEC-016 (REQ-SEC-016) · Exercises: SCR-SEC-006 /security/registry · API-SEC-021
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a module that has registered itself with its bilingual name — the registration is the consuming module's own call and is drawn on no screen (ADR-SEC-009)
Steps        : 1. open /security/registry 2. find the module node
Expected     : one active module node appears with both names; the screen is read-only for every caller who reaches it and offers no register affordance
Test data    : a registered module
<!-- TC:TC-SEC-052:END -->

<!-- TC:TC-SEC-053:START traces=AC-SEC-017,REQ-SEC-017,SCR-SEC-006,API-SEC-021 -->
### TC-SEC-053 — the registry tree shows a module's screens
Derived from : AC-SEC-017 (REQ-SEC-017) · Exercises: SCR-SEC-006 /security/registry · API-SEC-021
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a registered, active module that has registered a screen with a unique page code
Steps        : 1. open /security/registry 2. expand the module node
Expected     : one active screen node appears under that module with its page code and both names, and the tree route is registered before any :id route so a node id is never matched as the tree itself
Test data    : one registered screen
<!-- TC:TC-SEC-053:END -->

<!-- TC:TC-SEC-054:START traces=AC-SEC-019,REQ-SEC-019,SCR-SEC-006,API-SEC-021 -->
### TC-SEC-054 — the registry tree shows each action's derived permission code
Derived from : AC-SEC-019 (REQ-SEC-019) · Exercises: SCR-SEC-006 /security/registry · API-SEC-021
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a registered, active screen that has registered an action code
Steps        : 1. expand the screen node 2. read the action row's permission code
Expected     : the action appears with the permission code `PERM_<pageCode>_<actionCode>` as the server derived it — the screen displays the code and never composes one of its own, which is what lets a reviewer move from here to the grant tree and grant exactly what is shown
Test data    : one registered action
<!-- TC:TC-SEC-054:END -->

<!-- TC:TC-SEC-055:START traces=AC-SEC-022,REQ-SEC-022,SCR-SEC-007,API-SEC-022 -->
### TC-SEC-055 — every dashboard figure is computed live
Derived from : AC-SEC-022 (REQ-SEC-022) · Exercises: SCR-SEC-007 /security/dashboard · API-SEC-022
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a caller holding the dashboard
Steps        : 1. open /security/dashboard 2. read every widget 3. change the underlying data and reload
Expected     : each widget — users overview, failed logins in 24h, active sessions, recent activity, roles/permissions summary, onboarding funnel — reflects current data; no figure is read from a stored counter, and the reloaded values move with the data
Test data    : six widgets
<!-- TC:TC-SEC-055:END -->

<!-- TC:TC-SEC-056:START traces=AC-SEC-025,REQ-SEC-025,SCR-SEC-008,API-SEC-023 -->
### TC-SEC-056 — filtering the audit log returns exactly the matching entries
Derived from : AC-SEC-025 (REQ-SEC-025) · Exercises: SCR-SEC-008 /security/audit-log · API-SEC-023
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: audit entries across several event types and dates
Steps        : 1. open /security/audit-log 2. filter by event type and date range
Expected     : exactly the matching entries are returned and none is altered; the filter is mirrored into the route's search params so an investigation is shareable as a link
Test data    : entries across three event types
<!-- TC:TC-SEC-056:END -->

<!-- TC:TC-SEC-057:START traces=AC-SEC-026,REQ-SEC-026,SCR-SEC-008,API-SEC-024 -->
### TC-SEC-057 — exporting the audit log exports exactly the filtered entries
Derived from : AC-SEC-026 (REQ-SEC-026) · Exercises: SCR-SEC-008 /security/audit-log · API-SEC-024
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a filtered audit-log view
Steps        : 1. filter the list 2. choose Export 3. open the produced file
Expected     : the CSV contains exactly the filtered entries' fields — the export builds its parameters from the same filter object the list uses, so the two cannot diverge. Export shares the screen's VIEW permission and is not separately gated
Test data    : a filtered view
<!-- TC:TC-SEC-057:END -->

<!-- TC:TC-SEC-058:START traces=AC-SEC-027,REQ-SEC-027,SCR-SEC-009,API-SEC-025 -->
### TC-SEC-058 — only non-terminated sessions are listed
Derived from : AC-SEC-027 (REQ-SEC-027) · Exercises: SCR-SEC-009 /security/sessions · API-SEC-025
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: several sessions, some terminated and some not
Steps        : 1. open /security/sessions 2. read the list
Expected     : only the non-terminated sessions appear, each with its user and last-activity time; the terminated ones are absent rather than shown greyed out
Test data    : a mix of terminated and live sessions
<!-- TC:TC-SEC-058:END -->

<!-- TC:TC-SEC-059:START traces=AC-SEC-028,REQ-SEC-028,SCR-SEC-009,API-SEC-026 -->
### TC-SEC-059 — terminating a session ends it for the affected user
Derived from : AC-SEC-028 (REQ-SEC-028) · Exercises: SCR-SEC-009 /security/sessions · API-SEC-026
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active session; signed in as a caller holding the session-delete action
Steps        : 1. choose Terminate on the row 2. confirm 3. read the list again
Expected     : the row leaves the list and the affected user's token is no longer accepted, so their next request sends them back to sign in; termination is the only change this screen makes — there is no create and no edit on it
Test data    : one live session
<!-- TC:TC-SEC-059:END -->

<!-- SUB:UI-FLOWS:END -->

<!-- SUB:INT-FLOW:START traces=AC-SEC-021,REQ-SEC-021,SCR-SEC-010,API-SEC-027,AC-SEC-032,REQ-SEC-032,AC-SEC-033,REQ-SEC-033,AC-SEC-023,REQ-SEC-023,SCR-SEC-007,SCR-SEC-009,API-SEC-022 -->
### SUB — INT-FLOW

The flows that span screens: the two-tier menu that is itself the guard source for every route above, and the dashboard widget whose gating is the server's.

<!-- TC:TC-SEC-060:START traces=AC-SEC-021,REQ-SEC-021,SCR-SEC-010,API-SEC-027 -->
### TC-SEC-060 — the menu shows exactly the modules and screens the caller's grants union to
Derived from : AC-SEC-021 (REQ-SEC-021) · Exercises: SCR-SEC-010 (shell) · API-SEC-027
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a user whose roles union to exactly module FIN with the screens "Journal Entries" and "Trial Balance"
Steps        : 1. sign in as that user 2. read the two-tier menu
Expected     : FIN is the only top-level entry and exactly those two screens sit beneath it; the menu is derived entirely from the response and is never authored in the client, which is why it is also the source every route guard evaluates
Test data    : one module, two screens
<!-- TC:TC-SEC-060:END -->

<!-- TC:TC-SEC-061:START traces=AC-SEC-032,REQ-SEC-032,SCR-SEC-010,API-SEC-027 -->
### TC-SEC-061 — a module the caller does not hold is absent from the menu entirely
Derived from : AC-SEC-032 (REQ-SEC-032) · Exercises: SCR-SEC-010 (shell) · API-SEC-027
Rule / code  : —
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: a user whose roles hold no grant for module FIN
Steps        : 1. sign in as that user 2. search the menu for FIN
Expected     : FIN appears nowhere — not greyed out, not disabled, absent. What is not granted is not rendered
Test data    : a user without the FIN grant
<!-- TC:TC-SEC-061:END -->

<!-- TC:TC-SEC-062:START traces=AC-SEC-033,REQ-SEC-033,SCR-SEC-010,API-SEC-027 -->
### TC-SEC-062 — a route reached directly without its grant is refused
Derived from : AC-SEC-033 (REQ-SEC-033) · Exercises: SCR-SEC-010 (the guard source) · API-SEC-027
Rule / code  : —
Scenario     : PERMISSION · data class ATTACK · language ALL
Preconditions: the same user, and a FIN screen URL typed directly
Steps        : 1. sign in as that user 2. navigate straight to the FIN screen URL 3. call the FIN endpoint directly
Expected     : the route guard sends the caller to the unauthorized destination, and the server denies the direct endpoint call independently — the menu's omission is not the enforcement, the server's check is, and the test asserts both halves rather than only the one the UI performs
Test data    : a direct URL and a direct endpoint call
<!-- TC:TC-SEC-062:END -->

<!-- TC:TC-SEC-063:START traces=AC-SEC-023,REQ-SEC-023,SCR-SEC-007,SCR-SEC-009,API-SEC-022 -->
### TC-SEC-063 — a widget the caller may not see is absent, and its source screen still guards itself
Derived from : AC-SEC-023 (REQ-SEC-023) · Exercises: SCR-SEC-007 /security/dashboard → SCR-SEC-009 · API-SEC-022
Rule / code  : —
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: an administrator role without the "active sessions" widget's permission
Steps        : 1. sign in as that role's user 2. open /security/dashboard 3. look for the active-sessions widget 4. navigate directly to /security/sessions
Expected     : the widget is absent from the response and therefore from the screen — the server returns only the widgets the caller may see, and the client performs no second permission test of its own; the sessions route is then refused by its own guard, so the absence and the refusal are two independent mechanisms and neither is standing in for the other
Test data    : a role without the sessions permission
<!-- TC:TC-SEC-063:END -->

<!-- SUB:INT-FLOW:END -->

<!-- PHASE:TEST-PLAN-FE:END -->

## TC TRACEABILITY INDEX

| AC | TC | REQ | SCR | RULE / code |
|---|---|---|---|---|
| AC-SEC-001 | TC-SEC-034 | REQ-SEC-001 | SCR-SEC-001 | — |
| AC-SEC-002 | TC-SEC-035 | REQ-SEC-002 | SCR-SEC-001 | SEC-401-INVALID-CREDENTIALS |
| AC-SEC-003 | TC-SEC-036 | REQ-SEC-003 | SCR-SEC-002 | — |
| AC-SEC-006 | TC-SEC-037 | REQ-SEC-006 | SCR-SEC-003 | — |
| AC-SEC-007 | TC-SEC-038 | REQ-SEC-007 | SCR-SEC-003 | — |
| AC-SEC-008 | TC-SEC-039 | REQ-SEC-008 | SCR-SEC-003 | RULE-SEC-006 → SEC-409-RESET-TOKEN-INVALID |
| AC-SEC-004 | TC-SEC-040 | REQ-SEC-004 | SCR-SEC-004 | — |
| AC-SEC-005 | TC-SEC-041 | REQ-SEC-005 | SCR-SEC-004 | — |
| AC-SEC-009 | TC-SEC-042 | REQ-SEC-009 | SCR-SEC-004 | SEC-409-USER-DUP |
| AC-SEC-010 | TC-SEC-043 | REQ-SEC-010 | SCR-SEC-004 | — |
| AC-SEC-011 | TC-SEC-044 | REQ-SEC-011 | SCR-SEC-004 | — |
| AC-SEC-031 | TC-SEC-045 | REQ-SEC-031 | SCR-SEC-004 | — |
| AC-SEC-012 | TC-SEC-046 | REQ-SEC-012 | SCR-SEC-005 | — |
| AC-SEC-013 | TC-SEC-047 | REQ-SEC-013 | SCR-SEC-005 | RULE-SEC-001 → SEC-409-NO-MODULE-GRANT |
| AC-SEC-014 | TC-SEC-048 | REQ-SEC-014 | SCR-SEC-005 | RULE-SEC-002 → SEC-409-NO-SCREEN-GRANT |
| AC-SEC-015 | TC-SEC-049 | REQ-SEC-015 | SCR-SEC-005 | RULE-SEC-003 |
| AC-SEC-020 | TC-SEC-050 | REQ-SEC-020 | SCR-SEC-005 | RULE-SEC-005 → SEC-409-SOD-CONFLICT |
| AC-SEC-030 | TC-SEC-051 | REQ-SEC-030 | SCR-SEC-005 | RULE-SEC-007 → SEC-409-NO-VIEW-GRANT |
| AC-SEC-016 | TC-SEC-052 | REQ-SEC-016 | SCR-SEC-006 | — |
| AC-SEC-017 | TC-SEC-053 | REQ-SEC-017 | SCR-SEC-006 | — |
| AC-SEC-019 | TC-SEC-054 | REQ-SEC-019 | SCR-SEC-006 | — |
| AC-SEC-022 | TC-SEC-055 | REQ-SEC-022 | SCR-SEC-007 | — |
| AC-SEC-025 | TC-SEC-056 | REQ-SEC-025 | SCR-SEC-008 | — |
| AC-SEC-026 | TC-SEC-057 | REQ-SEC-026 | SCR-SEC-008 | — |
| AC-SEC-027 | TC-SEC-058 | REQ-SEC-027 | SCR-SEC-009 | — |
| AC-SEC-028 | TC-SEC-059 | REQ-SEC-028 | SCR-SEC-009 | — |
| AC-SEC-021 | TC-SEC-060 | REQ-SEC-021 | SCR-SEC-010 | — |
| AC-SEC-032 | TC-SEC-061 | REQ-SEC-032 | SCR-SEC-010 | — |
| AC-SEC-033 | TC-SEC-062 | REQ-SEC-033 | SCR-SEC-010 | — |
| AC-SEC-023 | TC-SEC-063 | REQ-SEC-023 | SCR-SEC-007, SCR-SEC-009 | — |

### AC covered on the backend track only — not a gap on this track

| AC | REQ | Why no frontend case |
|---|---|---|
| AC-SEC-018 | REQ-SEC-018 | a screen registration naming an unregistered module is refused — the refusal is answered to the registering module's own call, which no screen makes (ADR-SEC-009); SCR-SEC-006 is read-only |
| AC-SEC-024 | REQ-SEC-024 | the audit entry is appended by the server when an event completes; no client call or affordance writes one, and the frontend's assertable half is the filtered read (TC-SEC-056) |
| AC-SEC-029 | REQ-SEC-029 | the password-reset notification is dispatched entirely server-side when a token is issued — SEC's own F2 block records that no client call, state or affordance represents it |

## COVERAGE

AC covered on this track: 30/33 — the three above are backend-only by construction, and 33/33
across the module when both plans are read together (`backend-test-plan-sec.md` carries one TC
per AC for all 33).
REQ covered on this track: 30/33 — the same three REQ ids, for the same reason.
SCR covered: 10/10 — SCR-SEC-001 (2), SCR-SEC-002 (1), SCR-SEC-003 (3), SCR-SEC-004 (6),
SCR-SEC-005 (6), SCR-SEC-006 (3), SCR-SEC-007 (2), SCR-SEC-008 (2), SCR-SEC-009 (3),
SCR-SEC-010 (3) — the conflicting-assignment and dashboard-widget cases each touch two screens.
UXD covered: not applicable — SEC mints no `UXD-*` (SRS §A8: ROOT, no consumed entity), so
there is nothing for an integration phase to derive even at project scope.
TC count check (§3 over-engineering guard): 30 cases against 33 ACs is well under 2×, and no
case is a fabricated variant — every one derives from a distinct AC.
Scenario mix: HAPPY 13 · VIOLATION 5 · STATE 8 · PERMISSION 4 · BOUNDARY 0 (no AC or RULE in
SEC's set states a numeric limit, so §3 rule 3 adds none).

## NOTES

- Every message asserted above is copied character-perfect from `srs-sec.md` in both languages;
  no message is reworded and none is composed by a test.
- TC-SEC-035 is one case with three attempts on purpose: AC-SEC-002 gives ONE message for a
  wrong password, an unknown username and a disabled one, and a test that checked only the
  first would pass against a screen that leaked the difference in the other two.
- TC-SEC-062 asserts both halves of REQ-SEC-033 — the route guard AND the server's independent
  denial — because the menu's omission is not the enforcement, and a test that checked only the
  guard would pass against a client-only gate.
- TC-SEC-047, TC-SEC-048 and TC-SEC-051 assert that a grant refusal renders as its own rule
  message rather than the generic forbidden message: these are authorization outcomes the
  administrator is editing, not authorization failures of the administrator.
- `test-execution-manifest-sec.md` is a derived view of the **backend** plan and its API set.
  Neither changed in this run, so it is current and is not rewritten.
══════════════════════════════════════════════════════════════════
