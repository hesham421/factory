# PRD — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module          : SEC     Version : v1
Source artifacts: platform-summary, module-registry, business-policies
Stories         : 12   Policies covered : 11/11   Deferred : 0
Status          : DRAFT — awaiting prd-approval
══════════════════════════════════════════════════════════════════

## USER STORIES

US-SEC-001
  Title          : تسجيل الدخول / Login
  Story          : As a registered platform user, I need to sign in securely, so that I receive an identity/session every consuming module trusts.
  Priority       : HIGH — implied ("secure sign-in issuing a session/token consuming modules trust", the entry point of the whole module)
  Success metric : —
  Traces         : POL-SEC-004
  Source         : security-module-plan-en.md §3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-002
  Title          : التسجيل الذاتي / Sign-up
  Story          : As a prospective user, I need to self-register, so that an administrator can later grant me access without creating my account manually.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-SEC-003
  Source         : security-module-plan-en.md §3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-003
  Title          : نسيت / إعادة تعيين كلمة المرور / Forgot / reset password
  Story          : As a user who lost access to my password, I need a secure self-service reset, so that I can regain access without exposing my credentials.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-SEC-004
  Source         : security-module-plan-en.md §3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-004
  Title          : إدارة المستخدمين / Manage users
  Story          : As a security administrator, I need to add, edit, activate, deactivate a user and assign one or more roles, so that access reflects who currently should have it.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-SEC-008
  Source         : security-module-plan-en.md §4.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-005
  Title          : إدارة الأدوار والمنح الثلاثية / Manage roles and the three-level grant editor
  Story          : As a security administrator, I need to create/edit/deactivate roles and grant them modules, then screens within a granted module, then actions on a granted screen, so that access always follows the module-first hierarchy.
  Priority       : HIGH — plan names this "the core improvement" (§4.1)
  Success metric : —
  Traces         : POL-SEC-001, POL-SEC-002
  Source         : security-module-plan-en.md §4.1, §4.2, §4.4, §4.5
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-006
  Title          : سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry
  Story          : As a consuming module's integrator, I need to register my module, its screens and its actions as data, so that my module can be granted to roles without any change to security code.
  Priority       : HIGH — foundational to every other module's onboarding
  Success metric : —
  Traces         : — (scope only)
  Source         : security-module-plan-en.md §4.3, §4.5, §7; module-registry-sec.md → ENTITIES OWNED (ModuleRegistry, ScreenRegistry, ActionRegistry)
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-007
  Title          : فصل المهام للمستهلكين / Segregation of duties for consumers
  Story          : As a consuming module (e.g. Accounting), I need to require two conflicting actions be held by distinct roles/users, so that no single user can both perform and approve a sensitive transition.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-SEC-005
  Source         : security-module-plan-en.md §4.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-008
  Title          : القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu
  Story          : As a signed-in user, I need my menu to show only the modules and screens my roles actually grant, so that I never see or reach something I am not authorized for.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-SEC-006, POL-SEC-007
  Source         : security-module-plan-en.md §6
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-009
  Title          : لوحة تحكم الأمان / Admin dashboard
  Story          : As a security administrator, I need a landing dashboard (users overview, failed logins, active sessions, recent activity, roles/permissions summary, onboarding funnel), so that I can spot risk and over-privileged accounts at a glance.
  Priority       : MEDIUM — plan names this a "recommended baseline" (§5)
  Success metric : —
  Traces         : POL-SEC-010, POL-SEC-011
  Source         : security-module-plan-en.md §5.1, §5.2
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-010
  Title          : سجل التدقيق / Audit log
  Story          : As a security administrator, I need a searchable, filterable, exportable (CSV) audit log of logins, failed logins, resets and role/permission changes, so that I have a complete and trustworthy record of every security-relevant event.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-SEC-009
  Source         : security-module-plan-en.md §5.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-011
  Title          : إدارة الجلسات النشطة / Active sessions management
  Story          : As a security administrator, I need to see currently signed-in users and force-terminate a session when authorized, so that I can respond to a compromised or abandoned session.
  Priority       : MEDIUM
  Success metric : —
  Traces         : — (scope only)
  Source         : security-module-plan-en.md §5.1, §5.3; module-registry-sec.md → ENTITIES OWNED (ActiveSession)
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-SEC-012
  Title          : إشعار اختياري عبر خدمة الإشعارات / Optional notification on password reset
  Story          : As a user requesting a password reset, I need to optionally receive that reset through the platform's ready Notifications service, so that I am not blocked if this integration is skipped.
  Priority       : LOW — explicitly "only on real need", never a hard dependency
  Success metric : —
  Traces         : — (scope only)
  Source         : security-module-plan-en.md §8; new project/integration-notifications-fileservice.md §1
  Status         : DRAFT → APPROVED (by the PRD approval gate)

## TRACEABILITY — story → policy
| US | Traces (POL) | Source |
|---|---|---|
| US-SEC-001 | POL-SEC-004 | security-module-plan-en.md §3 |
| US-SEC-002 | POL-SEC-003 | security-module-plan-en.md §3 |
| US-SEC-003 | POL-SEC-004 | security-module-plan-en.md §3 |
| US-SEC-004 | POL-SEC-008 | security-module-plan-en.md §4.4 |
| US-SEC-005 | POL-SEC-001, POL-SEC-002 | security-module-plan-en.md §4.1-§4.2 |
| US-SEC-006 | — (scope only) | security-module-plan-en.md §4.3, §7 |
| US-SEC-007 | POL-SEC-005 | security-module-plan-en.md §4.4 |
| US-SEC-008 | POL-SEC-006, POL-SEC-007 | security-module-plan-en.md §6 |
| US-SEC-009 | POL-SEC-010, POL-SEC-011 | security-module-plan-en.md §5.1-§5.2 |
| US-SEC-010 | POL-SEC-009 | security-module-plan-en.md §5.3 |
| US-SEC-011 | — (scope only) | security-module-plan-en.md §5.1, §5.3 |
| US-SEC-012 | — (scope only) | security-module-plan-en.md §8 |
Every policy POL-SEC-001 … POL-SEC-011 appears in at least one row above (001,002 →
US-005; 003 → US-002; 004 → US-001/US-003; 005 → US-007; 006,007 → US-008;
008 → US-004; 009 → US-010; 010,011 → US-009).

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
None — security-module-plan-en.md and business-policies-sec.md left no story's scope,
priority or role genuinely ambiguous; no dialogue question was required.

## DEFERRED
| US | Reason | Activation trigger |
None — every capability named in security-module-plan-en.md is represented by a story
in this v1 PRD; nothing was pushed out.

## APPROVAL
Approved by : PENDING   Date : PENDING
Once approved, no stage may raise a question; P1 onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════
