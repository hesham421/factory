## MODULE REGISTRY — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module Code    : SEC   (profile.vocabulary.module_prefixes)
Bounded context: organization
Layer / Type   : L1 / security engine     Execution tier : 1.2
Source         : NEW
Knowledge      : new project/security-module-plan-en.md; profiles/erp/knowledge/erp-domain-standards.md §4
Readiness      : READY
══════════════════════════════════════════════════════════════════

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar/en) | Kind | PRIVATE / SHARED | Source |
|---|---|---|---|
| المستخدم / User | security | SHARED — every module's audit fields (createdBy/updatedBy) FK to it | security-module-plan-en.md §3, §4.4; profiles/erp.yaml conventions.entity_defaults |
| الدور / Role | security | PRIVATE | security-module-plan-en.md §4.4 |
| ربط المستخدم بالدور / UserRoleAssignment | security | PRIVATE | security-module-plan-en.md §4.4 |
| سجل الوحدات / ModuleRegistry | security | SHARED — every consuming module registers itself here | security-module-plan-en.md §4.3, §7 |
| سجل الشاشات / ScreenRegistry (SEC_PAGES) | security | SHARED — every consuming module registers its screens here | security-module-plan-en.md §4.3, §4.5; profiles/erp.yaml conventions.security_model.page_registry |
| سجل الإجراءات / ActionRegistry (permission catalog, PERM_*) | security | SHARED — every consuming module registers its actions here | security-module-plan-en.md §4.1, §4.3; profiles/erp.yaml conventions.security_model.permission_pattern |
| منح الوحدة للدور / RoleModuleGrant | security | PRIVATE | security-module-plan-en.md §4.1-§4.2 |
| منح الشاشة للدور / RoleScreenGrant | security | PRIVATE | security-module-plan-en.md §4.1-§4.2 |
| منح الإجراء للدور / RoleActionGrant | security | PRIVATE | security-module-plan-en.md §4.1-§4.2 |
| الجلسة النشطة / ActiveSession | security | PRIVATE | security-module-plan-en.md §5.1, §5.3 |
| سجل التدقيق / AuditLogEntry | security | PRIVATE | security-module-plan-en.md §5.2-§5.3 |
| رمز إعادة تعيين كلمة المرور / PasswordResetToken | security | PRIVATE | security-module-plan-en.md §3 |
| طلب تسجيل معلّق / SignupRequest | security | PRIVATE | security-module-plan-en.md §3 |

LOOKUPS OWNED    (value lists this module masters — registered into MDL, not stored locally)
| Lookup key | Description | Initial values (only those the user named) | Source |
|---|---|---|---|
| USER_STATUS | حالة حساب المستخدم / user account status | None — no specific values named by the user | AUTO (see AUTO-DECISIONS) |
| AUDIT_EVENT_TYPE | نوع حدث التدقيق / audit-log event type | None — no specific values named by the user | AUTO (see AUTO-DECISIONS) |
Rule (profile): all LOV values runtime-loaded from the lookup module; no hardcoded enums in APIs or field specs

LOOKUPS CONSUMED (from other modules)
| Lookup key | Owner code | READ-ONLY |
None — SEC is a Tier-0 foundation module; it consumes no other in-scope module's lookups this batch.

SHARED ENTITIES CONSUMED
| Entity | Owner code | HARD-FK / SOFT-READ | Why |
None — SEC is ROOT; it depends on no other in-scope module.

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
None (within the platform's module registry).
External (not a registry module): Notifications (ready, SOFT, optional — e.g. password-reset email) [security-module-plan-en.md §8].
ROOT: YES

AUTO-DECISIONS
AUTO: registered USER_STATUS and AUDIT_EVENT_TYPE as SEC-owned lookup types (values: USER_STATUS = PENDING/ACTIVE/DISABLED/LOCKED; AUDIT_EVENT_TYPE = LOGIN_SUCCESS/LOGIN_FAILED/LOGOUT/PASSWORD_RESET_REQUESTED/PASSWORD_RESET_COMPLETED/ROLE_ASSIGNED/ROLE_REVOKED/MODULE_GRANTED/MODULE_REVOKED/SCREEN_GRANTED/SCREEN_REVOKED/ACTION_GRANTED/ACTION_REVOKED/SESSION_TERMINATED — these initial values are AUTO, not user-named, so they are listed here rather than in the Lookups Owned "Initial values" column)
  FROM: profiles/erp.yaml conventions.lookups ("no hardcoded enums in APIs or field specs") + lookup-module-plan-en.md §3
  IF WRONG: fold these states into a plain internal enum on the User/AuditLogEntry entities instead of a shared lookup type — revise this module registry and business-policies-sec.md's CUSTOM LOOKUP VALUES accordingly.
AUTO: classified User as SHARED
  FROM: profiles/erp.yaml conventions.entity_defaults (every entity carries createdBy/updatedBy, which must reference a real User row)
  IF WRONG: none recommended — dropping this would break audit traceability platform-wide.
AUTO: tier/numbering 1.2 (Foundation, Tier 0)
  FROM: [KB:erp-domain-standards §1]
  IF WRONG: renumber if the platform later reprioritizes; number stability rule applies once confirmed.
AUTO: Session and AuditLogEntry kept PRIVATE, not SHARED
  FROM: security-module-plan-en.md §5 scopes the audit feed to SEC's own security events (logins, resets, role/permission changes) only, not other modules' business events
  IF WRONG: promote to SHARED if a later module needs to append platform-wide audit events through SEC — would need its own ADR at that time.

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
None — security-module-plan-en.md fully settles this module's P0 scope; no point required dialogue.
══════════════════════════════════════════════════════════════════
