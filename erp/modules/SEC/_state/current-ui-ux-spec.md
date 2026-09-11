# UI / UX SPEC — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Stage : P3.2 (Part A — UX design)
Screens: 10 — SCR-SEC-001..010 · UXD : 0 (SEC is ROOT — SRS A8: no consumed entity)
Fields : copied from SRS A3 per owning ENT, reconciled against the published DTOs
ADRs   : ADR-SEC-003..010 (all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

كل كتلة أدناه تصف شاشة واحدة: حقولها وصلاحياتها منسوخة من SRS بلا إضافة ولا حذف، ونمط
الحاوية مقرَّر هنا وفق §A.4. «نيّة التصميم» اقتراح مُعلَّم بوضوح ولا يُقرأ كقاعدة.

Each block below is one screen. Fields and permissions are copied from the SRS; the
container pattern is decided here; `Design intent` is a clearly marked proposal, never a rule.

**Cross-module display dependencies (`UXD-*`): none.** SRS A8 records SEC as ROOT — it
consumes no entity owned by another module — so no screen in this module displays data whose
authoritative source is another module's API, and no `UXD-*` is minted. The one place a
foreign code appears (`SCR-SEC-006`'s registry tree, `SCR-SEC-010`'s menu) is not foreign
data: `ModuleRegistry`, `ScreenRegistry` and `ActionRegistry` are entities SEC itself owns
(ENT-SEC-004/005/006), holding rows that other modules registered. Reading a SEC-owned row
is not a cross-module display dependency.

**Error states** are stated generically per §A.3; the catalog codes and their routing belong
to Part B (`frontend-execution-plan-sec.md` → F2).

---

## SCR-SEC-001 — تسجيل الدخول / Login                 traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002
Traces            : REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002
UI pattern        : flat record — a credentials form (SRS SCR-REQ-SEC-001 B1 "flat record")
Container pattern : FULL_PAGE (no entry sub-view — ADR-SEC-007; public page with no host list)
Sub-views         : none — single screen, no search and no detail (SRS B2 "not applicable")
Fields shown      : username — اسم المستخدم / Username (required, editable) ·
                    password — كلمة المرور / Password (required, editable, write-only —
                    never echoed, never stored as entered [POL-SEC-004])
                    No other field of ENT-SEC-001 appears: the SRS B3 input list is exactly these two.
Permissions       : public (pre-authentication) — SRS Access summary row SEC_LOGIN: no role or
                    permission gates reaching this screen. No `PERM_*` applies.
Cross-module data : none
States            : empty (the default state of the form) · loading (while the credentials are
                    being verified — the submit affordance is busy, the form is not cleared) ·
                    error (rejected credentials return to this screen with the message and no
                    session; a transport failure shows the generic error) · offline — the SRS
                    does not state offline behaviour, so none is specified
Design intent     : PROPOSAL — one centred card; the two secondary paths ("Forgot password?" →
                    SCR-SEC-003, "Sign up" → SCR-SEC-002) sit below the submit affordance as
                    links, so the primary path stays single. The rejection message is shown
                    once, above the fields, and is identical for a wrong password and an
                    unknown or disabled username (AC-SEC-002 gives one message for all three).
Mockup            : not produced this run (optional per §A.7)

---

## SCR-SEC-002 — التسجيل الذاتي / Sign-up             traces=REQ-SEC-003,AC-SEC-003
Traces            : REQ-SEC-003,AC-SEC-003
UI pattern        : flat record (SRS SCR-REQ-SEC-002 B1)
Container pattern : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Sub-views         : none — single screen
Fields shown      : email — البريد الإلكتروني / Email (required, editable, valid email) ·
                    fullNameAr — الاسم الكامل (عربي) / Full name (Arabic) (required, editable) ·
                    fullNameEn — الاسم الكامل (إنجليزي) / Full name (English) (required, editable)
                    ENT-SEC-013's remaining fields — signupRequestPk, submittedAt, statusCode,
                    reviewedBy, reviewedAt — are system-set and are not shown on this screen
                    (SRS B3 lists three inputs).
Permissions       : public (pre-authentication) — SRS Access summary row SEC_SIGNUP
Cross-module data : none
States            : empty · loading (submission in flight) · error (validation returned per
                    field; a duplicate request is a server conflict shown as a message) ·
                    submitted — a confirmation state stating that the request is pending and
                    that no access exists yet (REQ-SEC-003: no account is created)
Design intent     : PROPOSAL — the same card shell as SCR-SEC-001 so the public pages read as
                    one surface; after submission the form is replaced by the confirmation
                    rather than cleared, so a second submission is a deliberate act.
Mockup            : not produced this run

---

## SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password   traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029
Traces            : REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029
UI pattern        : flat record, two steps (SRS SCR-REQ-SEC-003 B1 "Wizard (request step +
                    reset step) = ONE screen requirement")
Container pattern : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Sub-views         : Wizard — step 1 "request" and step 2 "reset", under this ONE SCR; the step
                    is addressed by a route param, never by local-only state
Fields shown      : step 1 — email — البريد الإلكتروني / Email (required, editable) ·
                    step 2 — token — رمز إعادة التعيين / Reset token (required, normally
                    carried by the link, editable only when absent) · newPassword — كلمة المرور
                    الجديدة / New password (required, editable, write-only) · confirm password
                    — تأكيد كلمة المرور / Confirm password (required, editable, write-only,
                    client-side confirmation of the field above — SRS B3 "confirm password")
                    ENT-SEC-012's tokenHash, requestedAt, expiresAt and usedAt are system-only
                    and never displayed.
Permissions       : public (pre-authentication) — SRS Access summary row SEC_PWD_RESET
Cross-module data : none
States            : empty · loading · error (an expired or already-used token returns to step 2
                    with the invalid-link message and changes nothing — AC-SEC-008) ·
                    confirmed (step 1 always ends in the same generic confirmation whether or
                    not the email is registered — SRS B5 "never reveals whether the email exists")
Design intent     : PROPOSAL — step 1 and step 2 never appear together; arriving with a token
                    in the URL opens step 2 directly, so the emailed link is a single click.
                    The optional notification (REQ-SEC-029) is entirely server-side and has no
                    representation here.
Mockup            : not produced this run

---

## SCR-SEC-004 — المستخدمون / Users                   traces=REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,REQ-SEC-004,REQ-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,AC-SEC-004,AC-SEC-005
Traces            : REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,REQ-SEC-004,REQ-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,AC-SEC-004,AC-SEC-005
UI pattern        : Search + Entry composite, plus a pending sign-ups sub-view (SRS
                    SCR-REQ-SEC-004 B1 "flat record (search list + entry form)")
Container pattern : SIDE_DRAWER (§A.4 rule 3 — bounded field count, no repeating rows with a
                    computed total; the roles multi-select is a selection, not a line-item grid)
Sub-views         : Search (the user list) · Entry (the drawer over it) · Pending sign-ups
                    (SRS B3 "a separate Pending sign-ups tab") — all under this ONE SCR
Fields shown      : from ENT-SEC-001 —
                    userPk — معرّف المستخدم / User id (read-only, system, not rendered as a field) ·
                    username — اسم المستخدم / Username (required; editable on create, read-only
                    on edit — the published `UserUpdateRequest` does not carry it) ·
                    email — البريد الإلكتروني / Email (required, editable) ·
                    fullNameAr — الاسم الكامل (عربي) / Full name (Arabic) (required, editable) ·
                    fullNameEn — الاسم الكامل (إنجليزي) / Full name (English) (required, editable) ·
                    password — كلمة المرور / Password (required on create only, write-only;
                    never shown, never returned — SRS B3 does not list it, but
                    `UserCreateRequest` requires it and ENT-SEC-001.passwordHash is its SRS
                    basis [POL-SEC-004]; ADR-SEC-010) ·
                    statusCode — الحالة / Status (read-only — SRS B3 lists it as an input, but
                    no published write DTO accepts it; it is changed by the activate /
                    deactivate affordances and by sign-up approval, along SRS A7's transitions,
                    never typed; ADR-SEC-010) ·
                    lastLoginAt — آخر دخول / Last login (read-only, informational) ·
                    isActiveFl — نشط / Active (read-only — mirrors statusCode) ·
                    createdBy, createdAt, updatedBy, updatedAt — audit fields (read-only)
                    from ENT-SEC-003 — roles — الأدوار / Roles (multi-select of active roles;
                    one assignment row per selected role — REQ-SEC-010)
                    from ENT-SEC-013, in the pending sign-ups sub-view only —
                    email, fullNameAr, fullNameEn, submittedAt — تاريخ التقديم / Submitted at,
                    statusCode, reviewedBy, reviewedAt (all read-only; the only inputs are the
                    Approve and Reject decisions)
                    `failedLoginCount24h` is documented in SRS A3 as a dashboard figure that is
                    not a stored column — it appears on SCR-SEC-007, never here.
Permissions       : SEC_USERS — VIEW (list, search, read), CREATE (new user), UPDATE (edit,
                    activate, deactivate, assign roles, approve/reject a sign-up). SRS Access
                    summary; every action beyond VIEW also requires VIEW on this screen
                    (RULE-SEC-007). Names as declared by the backend:
                    `PERM_SEC_USERS_VIEW`, `PERM_SEC_USERS_CREATE`, `PERM_SEC_USERS_UPDATE`.
                    Reference only — the enforcement is the server's.
Cross-module data : none
States            : empty (no user matches the filters — distinguished from an unfiltered empty
                    list) · loading (list and drawer load independently) · error (generic here;
                    catalog codes and their routing are Part B's) · offline — not specified by
                    the SRS
Design intent     : PROPOSAL — the drawer keeps the list visible so an administrator editing one
                    user keeps the population in view. Deactivate and Reactivate are one
                    affordance whose label follows the row's status, and both confirm before
                    acting: deactivation ends the user's live sessions (REQ-SEC-011) and that
                    consequence is named in the confirmation. Pending sign-ups is a tab beside
                    the list rather than a screen of its own, because it is the same permission
                    and the same administrator (SRS B4).
Mockup            : not produced this run

---

## SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions   traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030
Traces            : REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030
UI pattern        : Master (role list) + Detail (three-level grant tree) — SRS SCR-REQ-SEC-005
                    B1 "true hierarchy (parent/child) — module → screen → action tree per role"
Container pattern : TREE_MASTER_DETAIL (§A.4 rule 1 — hierarchical parent–child data; two-pane,
                    tree plus a permanently visible detail)
Sub-views         : Search (role master list) · Detail (the grant tree of the selected role) —
                    under this ONE SCR
Fields shown      : from ENT-SEC-002 —
                    rolePk — معرّف الدور / Role id (read-only, system) ·
                    code — رمز الدور / Role code (required, editable on create; read-only
                    afterwards — it is the stable machine reference) ·
                    nameAr — اسم الدور (عربي) / Role name (Arabic) (required, editable) ·
                    nameEn — اسم الدور (إنجليزي) / Role name (English) (required, editable) ·
                    descriptionAr — الوصف (عربي) / Description (Arabic) (optional, editable) ·
                    descriptionEn — الوصف (إنجليزي) / Description (English) (optional, editable) ·
                    isActiveFl — نشط / Active (read-only) ·
                    createdBy, createdAt, updatedBy, updatedAt (read-only)
                    grant tree nodes, read from the registry entities —
                    module: code — رمز الوحدة / Module code, nameAr / nameEn — اسم الوحدة /
                    Module name (ENT-SEC-004, read-only) ·
                    screen: pageCode — رمز الصفحة / Page code, nameAr / nameEn — اسم الشاشة /
                    Screen name (ENT-SEC-005, read-only) ·
                    action: actionCode — الإجراء / Action, permissionCode — رمز الصلاحية /
                    Permission code, nameAr / nameEn — اسم الإجراء / Action name (ENT-SEC-006,
                    read-only — the permission code is derived by the server, never entered)
                    The grant rows themselves (ENT-SEC-007/008/009) carry no user-entered field:
                    grantedBy and grantedAt are system-set and shown as node metadata only.
Permissions       : SEC_ROLES — VIEW, CREATE, UPDATE (the grant-tree edits run under UPDATE),
                    DELETE (deactivate a role). SRS Access summary; RULE-SEC-007 applies.
                    Names as declared by the backend: `PERM_SEC_ROLES_VIEW`,
                    `PERM_SEC_ROLES_CREATE`, `PERM_SEC_ROLES_UPDATE`. Reference only.
                    No endpoint is published for role edit, role deactivate, or an individual
                    screen/action revoke — those affordances are not drawn (ADR-SEC-008), so
                    the DELETE row of the SRS matrix has no surface on this screen in v1.
Cross-module data : none — the tree's module and screen nodes are rows of SEC's own registry
                    entities (ENT-SEC-004/005/006), not another module's data
States            : empty (no role matches; and a selected role with no grant yet, which is the
                    normal starting point) · loading (master and tree load independently) ·
                    error (a refused grant keeps the tree unchanged and states why) ·
                    offline — not specified by the SRS
Design intent     : PROPOSAL — the tree's own shape carries the hierarchy rule, so a refusal is
                    rare by construction: a screen node is reachable only under a granted
                    module, an action node only under a granted screen, and a non-VIEW action
                    only once VIEW is held on that screen (RULE-SEC-001/002/007). Revoking a
                    module confirms first and names the count it will cascade (RULE-SEC-003);
                    the confirmation is the only place the cascade is announced, because it is
                    the only place it happens. A conflicting-action pair (RULE-SEC-005) is
                    refused at the moment of the second grant with its own message.
Mockup            : not produced this run

---

## SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry   traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019
Traces            : REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019
UI pattern        : master-detail tree (SRS SCR-REQ-SEC-006 B1 "true hierarchy
                    (module → screen → action)")
Container pattern : TREE_MASTER_DETAIL (§A.4 rule 1)
Sub-views         : Search (filters over the tree) · Detail (the selected node's own fields) —
                    under this ONE SCR
Fields shown      : from ENT-SEC-004 — moduleRegistryPk (read-only, system) · code — رمز الوحدة /
                    Module code (read-only) · nameAr — اسم الوحدة (عربي) / Module name (Arabic)
                    (read-only) · nameEn — اسم الوحدة (إنجليزي) / Module name (English)
                    (read-only) · isActiveFl — نشط / Active (read-only) · audit fields (read-only)
                    from ENT-SEC-005 — screenRegistryPk (read-only, system) · pageCode — رمز
                    الصفحة / Page code (read-only) · moduleId — الوحدة / Module (read-only) ·
                    nameAr / nameEn — اسم الشاشة / Screen name (read-only) · isActiveFl
                    (read-only) · audit fields (read-only)
                    from ENT-SEC-006 — actionRegistryPk (read-only, system) · permissionCode —
                    رمز الصلاحية / Permission code (read-only — derived, never entered) ·
                    screenId — الشاشة / Screen (read-only) · actionCode — الإجراء / Action
                    (read-only) · nameAr / nameEn — اسم الإجراء / Action name (read-only) ·
                    isActiveFl (read-only) · audit fields (read-only)
                    Every field on this screen is read-only: registration happens through the
                    registering module's own call (SRS B3), and the one edit the SRS names —
                    deactivating a stale row — has no published endpoint (ADR-SEC-008).
Permissions       : SEC_MODULE_REGISTRY — VIEW, UPDATE (deactivate only, per the SRS matrix;
                    no surface in v1 — ADR-SEC-008). Names as declared by the backend:
                    `PERM_SEC_MODULE_REGISTRY_VIEW`, `PERM_SEC_MODULE_REGISTRY_UPDATE`.
                    Reference only.
Cross-module data : none — the rows describe other modules but are owned by SEC
                    (ENT-SEC-004/005/006 are SHARED with SEC as owner)
States            : empty (no module registered yet — the expected first state of a new
                    platform) · loading · error (generic) · offline — not specified
Design intent     : PROPOSAL — the tree is the same shape an administrator will meet again on
                    SCR-SEC-005, so onboarding review and granting read alike. The derived
                    permission code is shown on every action node, because it is the string a
                    consuming module's developer needs to check on their own side.
Mockup            : not produced this run

---

## SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard   traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023
Traces            : REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023
UI pattern        : other — a grid of independent widgets, not a record or a list
                    (SRS SCR-REQ-SEC-007 B1 "dashboard")
Container pattern : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Sub-views         : none — the widgets are not separate screens (SRS B1 "Composite: single screen")
Fields shown      : read-only throughout (SRS B3 "Read-only; no data entry") —
                    users overview — نظرة عامة على المستخدمين / Users overview: total, active,
                    disabled, pending sign-ups ·
                    failed logins (24h) — محاولات الدخول الفاشلة (٢٤س) / Failed logins (24h):
                    count (the figure SRS A3 documents as derived, never a stored column) ·
                    active sessions — الجلسات النشطة / Active sessions: count ·
                    recent activity — آخر الأحداث / Recent activity: the latest audit entries
                    (event type, actor, time, details ar/en) ·
                    roles & permissions summary — ملخص الأدوار والصلاحيات / Roles & permissions:
                    role count, privileged role count, users per role ·
                    onboarding funnel — مسار التسجيل / Onboarding funnel: pending sign-ups,
                    stalled count
Permissions       : SEC_DASHBOARD — VIEW; each widget additionally requires the VIEW permission
                    of the screen it summarizes (REQ-SEC-023) — e.g. the active-sessions widget
                    requires SEC_SESSIONS VIEW. Names as declared by the backend:
                    `PERM_SEC_DASHBOARD_VIEW`, and per widget the source screen's own VIEW.
                    Reference only — the server returns only the widgets the caller may see
                    (ADR-SEC-005).
Cross-module data : none
States            : empty (a widget whose figure is legitimately zero states the zero; a widget
                    the caller may not see is absent, not empty) · loading (per widget, so one
                    slow figure does not hold the page) · error (per widget, so one failure does
                    not blank the dashboard) · offline — not specified
Design intent     : PROPOSAL — every widget is a link to the screen it summarizes (recent
                    activity → SCR-SEC-008, active sessions → SCR-SEC-009, onboarding funnel →
                    SCR-SEC-004's pending tab), so the dashboard is a starting point rather than
                    a destination. No figure is cached or carried between visits: REQ-SEC-022
                    requires each one computed at the moment of opening, and showing a stale
                    number would contradict the requirement even if it were faster.
Mockup            : not produced this run

---

## SCR-SEC-008 — سجل التدقيق / Audit log              traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026
Traces            : REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026
UI pattern        : flat record — an append-only list with filters and an export
                    (SRS SCR-REQ-SEC-008 B1)
Container pattern : FULL_PAGE (no entry sub-view — ADR-SEC-007; SRS B3 "not applicable — no
                    create/update")
Sub-views         : Search only — no entry; audit rows are never hand-created
Fields shown      : from ENT-SEC-011, all read-only —
                    auditLogEntryPk — معرّف قيد التدقيق / Audit entry id (system) ·
                    eventTypeCode — نوع الحدث / Event type ·
                    actorUserId — المستخدم الفاعل / Actor user (absent for an unauthenticated
                    failed-login attempt) ·
                    occurredAt — وقت الحدث / Occurred at ·
                    targetRef — الهدف / Target ·
                    detailsAr — التفاصيل (عربي) / Details (Arabic) ·
                    detailsEn — التفاصيل (إنجليزي) / Details (English) ·
                    ipAddress — عنوان IP / IP address
                    Filters (SRS B2): event type, actor, date range — each one a result column.
                    This entity carries no createdBy/updatedBy: it is the audit record
                    (SRS A3 note), and it is never updated after insert [POL-SEC-009].
Permissions       : SEC_AUDIT_LOG — VIEW; export shares the same permission and is not a
                    separate mutation (SRS B4). Name as declared by the backend:
                    `PERM_SEC_AUDIT_LOG_VIEW`. Reference only.
Cross-module data : none
States            : empty (no entry matches the filters) · loading · error (generic) ·
                    offline — not specified
Design intent     : PROPOSAL — the filter set is the investigation, so it is mirrored into the
                    route's search params and the filtered view is shareable by URL
                    (ADR-SEC-003). Export acts on exactly the current filter, never on the
                    current page, so an investigator exports what they are looking at rather
                    than what happens to be on screen (AC-SEC-026).
Mockup            : not produced this run

---

## SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management   traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028
Traces            : REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028
UI pattern        : flat record — a live list with a per-row terminate action
                    (SRS SCR-REQ-SEC-009 B1)
Container pattern : FULL_PAGE (no entry sub-view — ADR-SEC-007; SRS B3 "no separate entry form")
Sub-views         : Search only — no entry
Fields shown      : from ENT-SEC-010, all read-only —
                    activeSessionPk — معرّف الجلسة / Session id (system) ·
                    userId — المستخدم / User (shown with the owner's login, which the published
                    response carries alongside the id) ·
                    startedAt — بدأت في / Started at ·
                    lastActivityAt — آخر نشاط / Last activity ·
                    ipAddress — عنوان IP / IP address
                    tokenRef — مرجع الرمز / Token reference is an opaque reference and is never
                    displayed; terminatedAt / terminatedBy — أُنهيت في / بواسطة — are null for
                    every row this screen lists (SRS B5 lists non-terminated sessions only) and
                    are therefore not columns.
                    Filters (SRS B2): user, IP address — each one a result column.
Permissions       : SEC_SESSIONS — VIEW, DELETE (terminate); RULE-SEC-007 applies. Names as
                    declared by the backend: `PERM_SEC_SESSIONS_VIEW`,
                    `PERM_SEC_SESSIONS_DELETE`. Reference only.
Cross-module data : none
States            : empty (no live session matches) · loading · error (a refused or
                    already-terminated session leaves the list unchanged and states why) ·
                    offline — not specified
Design intent     : PROPOSAL — terminate confirms first and names the user, because the
                    consequence lands on someone who is working at that moment (AC-SEC-028);
                    after success the row leaves the list rather than greying out, since the
                    screen's contract is "sessions that have not been terminated".
Mockup            : not produced this run

---

## SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu   traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033
Traces            : REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033
UI pattern        : other — a navigation component rendered on every authenticated page, not a
                    record or a list (SRS SCR-REQ-SEC-010 B1)
Container pattern : none — a global shell component with no route of its own (ADR-SEC-007)
Sub-views         : none
Fields shown      : derived, read-only (SRS B3 "not applicable — read-only, derived") —
                    module tier: code — رمز الوحدة / Module code, nameAr / nameEn — اسم الوحدة /
                    Module name (ENT-SEC-004) ·
                    screen tier: pageCode — رمز الصفحة / Page code, nameAr / nameEn — اسم
                    الشاشة / Screen name (ENT-SEC-005)
                    Exactly two tiers, and only entries the caller's effective grants hold
                    (ENT-SEC-007/008 decide membership; neither is displayed).
Permissions       : no page code of its own — this is not a securable destination (SRS B4). Its
                    content is filtered per user by the same module and screen grants each
                    target page enforces for itself; the published endpoint requires only an
                    authenticated caller. A module the caller does not hold is absent entirely
                    (REQ-SEC-032), and absence from the menu is not the enforcement: the server
                    checks the module gate on every request regardless (REQ-SEC-033).
Cross-module data : none — the entries are rows of SEC's own registry entities
States            : empty (an authenticated user with no grant at all sees a menu with no module
                    — the correct rendering of "only what is granted", not an error) ·
                    loading (the shell renders before the menu resolves; no entry is guessed) ·
                    error (the menu fails to load — the shell stays usable and states it, and no
                    screen becomes reachable as a result) · offline — not specified
Design intent     : PROPOSAL — the menu is the module's only client-side gate (ADR-SEC-005), so
                    it is read once per session and re-read whenever a grant this user holds is
                    changed from SCR-SEC-005; nothing in it is composed locally from a static
                    route table, because a local table would outlive a revoked grant.
Mockup            : not produced this run

══════════════════════════════════════════════════════════════════
