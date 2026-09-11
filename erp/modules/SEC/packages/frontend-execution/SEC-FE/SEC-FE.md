<!-- source: PHASE:SEC-FE -->
<!-- traces: AC-SEC-001, AC-SEC-002, AC-SEC-003, AC-SEC-004, AC-SEC-005, AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-009, AC-SEC-010, AC-SEC-011, AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-016, AC-SEC-017, AC-SEC-018, AC-SEC-019, AC-SEC-020, AC-SEC-021, AC-SEC-022, AC-SEC-023, AC-SEC-024, AC-SEC-025, AC-SEC-026, AC-SEC-027, AC-SEC-028, AC-SEC-029, AC-SEC-030, AC-SEC-031, AC-SEC-032, AC-SEC-033, API-SEC-001, API-SEC-002, API-SEC-003, API-SEC-004, API-SEC-005, API-SEC-006, API-SEC-007, API-SEC-008, API-SEC-009, API-SEC-010, API-SEC-011, API-SEC-012, API-SEC-013, API-SEC-014, API-SEC-015, API-SEC-016, API-SEC-017, API-SEC-018, API-SEC-019, API-SEC-020, API-SEC-021, API-SEC-022, API-SEC-023, API-SEC-024, API-SEC-025, API-SEC-026, API-SEC-027, REQ-SEC-001, REQ-SEC-002, REQ-SEC-003, REQ-SEC-004, REQ-SEC-005, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019, REQ-SEC-020, REQ-SEC-021, REQ-SEC-022, REQ-SEC-023, REQ-SEC-024, REQ-SEC-025, REQ-SEC-026, REQ-SEC-027, REQ-SEC-028, REQ-SEC-029, REQ-SEC-030, REQ-SEC-031, REQ-SEC-032, REQ-SEC-033, SCR-SEC-001, SCR-SEC-002, SCR-SEC-003, SCR-SEC-004, SCR-SEC-005, SCR-SEC-006, SCR-SEC-007, SCR-SEC-008, SCR-SEC-009, SCR-SEC-010 -->
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
