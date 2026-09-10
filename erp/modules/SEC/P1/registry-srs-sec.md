## REGISTRY — P1 — SEC v1
══════════════════════════════════════════════════════════════════

Entities
| ENT id | Name (ar/en) | Kind | PRIVATE/SHARED | Status |
|---|---|---|---|---|
| ENT-SEC-001 | المستخدم / User | security | SHARED (owner) | REGISTERED |
| ENT-SEC-002 | الدور / Role | security | PRIVATE | REGISTERED |
| ENT-SEC-003 | ربط المستخدم بالدور / UserRoleAssignment | security | PRIVATE | REGISTERED |
| ENT-SEC-004 | سجل الوحدات / ModuleRegistry | security | SHARED (owner) | REGISTERED |
| ENT-SEC-005 | سجل الشاشات / ScreenRegistry | security | SHARED (owner) | REGISTERED |
| ENT-SEC-006 | سجل الإجراءات / ActionRegistry | security | SHARED (owner) | REGISTERED |
| ENT-SEC-007 | منح الوحدة للدور / RoleModuleGrant | security | PRIVATE | REGISTERED |
| ENT-SEC-008 | منح الشاشة للدور / RoleScreenGrant | security | PRIVATE | REGISTERED |
| ENT-SEC-009 | منح الإجراء للدور / RoleActionGrant | security | PRIVATE | REGISTERED |
| ENT-SEC-010 | الجلسة النشطة / ActiveSession | security | PRIVATE | REGISTERED |
| ENT-SEC-011 | سجل التدقيق / AuditLogEntry | security | PRIVATE | REGISTERED |
| ENT-SEC-012 | رمز إعادة تعيين كلمة المرور / PasswordResetToken | security | PRIVATE | REGISTERED |
| ENT-SEC-013 | طلب تسجيل معلّق / SignupRequest | security | PRIVATE | REGISTERED |

Consumed
none — SEC is ROOT (→ dependency index: no row this module).

Lookups owned
| Key | ENT | Values count |
|---|---|---|
| USER_STATUS | ENT-SEC-001 | 3 |
| SIGNUP_STATUS | ENT-SEC-013 | 3 |
| AUDIT_EVENT_TYPE | ENT-SEC-011 | 14 |

Lookups consumed
none.

Screens
| SCR-REQ id | Name (ar/en) | Page code |
|---|---|---|
| SCR-REQ-SEC-001 | تسجيل الدخول / Login | SEC_LOGIN |
| SCR-REQ-SEC-002 | التسجيل الذاتي / Sign-up | SEC_SIGNUP |
| SCR-REQ-SEC-003 | نسيت/إعادة تعيين كلمة المرور / Forgot/reset password | SEC_PWD_RESET |
| SCR-REQ-SEC-004 | المستخدمون / Users | SEC_USERS |
| SCR-REQ-SEC-005 | الأدوار والصلاحيات / Roles & permissions | SEC_ROLES |
| SCR-REQ-SEC-006 | سجل الوحدة/الشاشة/الإجراء / Module/screen/action registry | SEC_MODULE_REGISTRY |
| SCR-REQ-SEC-007 | لوحة تحكم الأمان / Admin dashboard | SEC_DASHBOARD |
| SCR-REQ-SEC-008 | سجل التدقيق / Audit log | SEC_AUDIT_LOG |
| SCR-REQ-SEC-009 | إدارة الجلسات النشطة / Active sessions management | SEC_SESSIONS |
| SCR-REQ-SEC-010 | القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu | (no page code — global component) |

Requirements
REQ count: 33 · AC count: 33 · RULE count: 7 · ENT count: 13 · SCR-REQ count: 10
Last sequence per atom: REQ: 033 · AC: 033 · ENT: 013 · RULE: 007 · SCR-REQ: 010

REQ ids (full text in srs-sec.md → A4): REQ-SEC-001, REQ-SEC-002, REQ-SEC-003,
REQ-SEC-004, REQ-SEC-005, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-009,
REQ-SEC-010, REQ-SEC-011, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015,
REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019, REQ-SEC-020, REQ-SEC-021,
REQ-SEC-022, REQ-SEC-023, REQ-SEC-024, REQ-SEC-025, REQ-SEC-026, REQ-SEC-027,
REQ-SEC-028, REQ-SEC-029, REQ-SEC-030, REQ-SEC-031, REQ-SEC-032, REQ-SEC-033

AC ids (full text in srs-sec.md → A4, one per REQ above): AC-SEC-001, AC-SEC-002,
AC-SEC-003, AC-SEC-004, AC-SEC-005, AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-009,
AC-SEC-010, AC-SEC-011, AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-016,
AC-SEC-017, AC-SEC-018, AC-SEC-019, AC-SEC-020, AC-SEC-021, AC-SEC-022, AC-SEC-023,
AC-SEC-024, AC-SEC-025, AC-SEC-026, AC-SEC-027, AC-SEC-028, AC-SEC-029, AC-SEC-030,
AC-SEC-031, AC-SEC-032, AC-SEC-033

RULE ids (full text in srs-sec.md → A5): RULE-SEC-001, RULE-SEC-002, RULE-SEC-003,
RULE-SEC-004, RULE-SEC-005, RULE-SEC-006, RULE-SEC-007

Decisions
ADR ids: none (no ADR raised — §9 ambiguity fork was never reached this stage).

Event
"P1 completed: SEC v1 — 13 entities, 33 requirements, 33 acceptance criteria, 7 rules, 10 screen requirements, 0 ADRs"
══════════════════════════════════════════════════════════════════
