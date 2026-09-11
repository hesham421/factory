## REGISTRY — P3.2 — SEC v1
══════════════════════════════════════════════════════════════════

ID RANGES
UXD-SEC — none minted (see UXD INDEX) · SCR-SEC-001 .. SCR-SEC-010

SCR ids: SCR-SEC-001, SCR-SEC-002, SCR-SEC-003, SCR-SEC-004, SCR-SEC-005, SCR-SEC-006,
SCR-SEC-007, SCR-SEC-008, SCR-SEC-009, SCR-SEC-010

UXD ids: none — SEC is ROOT (SRS A8: no consumed entity, no external module read), so no
screen owned by this module displays data whose authoritative source is another module.
Last sequence per atom: SCR: 010 · UXD: 000 (sequence not opened)

SCREENS
| SCR | Name (ar / en) | Container pattern | Owning ENT | Permissions |
|---|---|---|---|---|
| SCR-SEC-001 | تسجيل الدخول / Login | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001, ENT-SEC-010 | public (SEC_LOGIN) |
| SCR-SEC-002 | التسجيل الذاتي / Sign-up | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-013 | public (SEC_SIGNUP) |
| SCR-SEC-003 | نسيت / إعادة تعيين كلمة المرور / Forgot / reset password | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-012, ENT-SEC-001 | public (SEC_PWD_RESET) |
| SCR-SEC-004 | المستخدمون / Users | SIDE_DRAWER | ENT-SEC-001 (+ ENT-SEC-003, ENT-SEC-013) | PERM_SEC_USERS_VIEW, PERM_SEC_USERS_CREATE, PERM_SEC_USERS_UPDATE |
| SCR-SEC-005 | الأدوار والصلاحيات / Roles & permissions | TREE_MASTER_DETAIL | ENT-SEC-002 (+ ENT-SEC-004..009) | PERM_SEC_ROLES_VIEW, PERM_SEC_ROLES_CREATE, PERM_SEC_ROLES_UPDATE |
| SCR-SEC-006 | سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry | TREE_MASTER_DETAIL | ENT-SEC-004, ENT-SEC-005, ENT-SEC-006 | PERM_SEC_MODULE_REGISTRY_VIEW, PERM_SEC_MODULE_REGISTRY_UPDATE (no surface — ADR-SEC-008) |
| SCR-SEC-007 | لوحة تحكم الأمان / Admin dashboard | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001, ENT-SEC-002, ENT-SEC-010, ENT-SEC-011 | PERM_SEC_DASHBOARD_VIEW (+ each widget's source-screen VIEW, server-side) |
| SCR-SEC-008 | سجل التدقيق / Audit log | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-011 | PERM_SEC_AUDIT_LOG_VIEW (export shares it) |
| SCR-SEC-009 | إدارة الجلسات النشطة / Active sessions management | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-010 | PERM_SEC_SESSIONS_VIEW, PERM_SEC_SESSIONS_DELETE |
| SCR-SEC-010 | القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu | none — global shell component (ADR-SEC-007) | ENT-SEC-004, ENT-SEC-005 | none of its own — authenticated caller (SRS B4) |

UXD INDEX
| UXD | Screen | Field | Owner module · API used |
|---|---|---|---|
| — | — | — | none. SEC consumes no entity owned by another module (SRS A8, registry-srs "Consumed: none"), so no cross-module display dependency exists to mint. The registry rows of ENT-SEC-004/005/006 describe other modules but are owned by SEC, and reading a SEC-owned row is not a foreign-data field. |

API COVERAGE
| Status | Count | API ids |
|---|---|---|
| used by this frontend | 24 | API-SEC-001..017, API-SEC-021..027 |
| documented, deliberately uncalled | 3 | API-SEC-018, API-SEC-019, API-SEC-020 — the registration calls a consuming module makes for itself (SRS SCR-REQ-SEC-006 B3), bound and blocked out in F2 — ADR-SEC-009 |
| used but undocumented | 0 | — no endpoint is called that the api-docs lack |
| documented but unbound | 0 | all 27 registered API-SEC ids are bound by the API ID BINDING annex — ADR-SEC-004 |

Five of the bound reads carry a verb/path shape diff against the SRS B5 and the backend plan
(API-SEC-005, 012, 021, 023, 025 — GET planned, POST `…/search` published): ADR-SEC-003.

OPERATIONS WITHOUT AN ENDPOINT
role update · role deactivate · individual screen/action grant revoke · registry-row
deactivate · read-one-user-by-id · logout — named by SRS Part B or by an audit event type, but
required by no `REQ-*`; omitted from the frontend rather than faked (ADR-SEC-008).

LOOKUPS
| Key | Owner | Hook | Endpoint |
|---|---|---|---|
| USER_STATUS | SEC (SRS A6) | one shared hook | PENDING ADR-SEC-006 |
| SIGNUP_STATUS | SEC (SRS A6) | one shared hook | PENDING ADR-SEC-006 |
| AUDIT_EVENT_TYPE | SEC (SRS A6) | one shared hook | PENDING ADR-SEC-006 |
No lookup endpoint is published for any of the three; every lookup field stays a string holding
the code and no enum is modelled anywhere in the plan.

ALIGN-FE
PASSED ✓ · findings fixed: 0 (the verdict row inside the plan's ALIGN-FE block is written by
the orchestrator from the analyze report)

ADRs
erp/decisions/SEC/ADR-SEC-003.md (ACCEPTED, non-breaking — search endpoint shape) ·
erp/decisions/SEC/ADR-SEC-004.md (ACCEPTED, non-breaking — API id binding annex) ·
erp/decisions/SEC/ADR-SEC-005.md (ACCEPTED, non-breaking — no action-level permission endpoint) ·
erp/decisions/SEC/ADR-SEC-006.md (ACCEPTED, non-breaking — no lookup endpoint) ·
erp/decisions/SEC/ADR-SEC-007.md (ACCEPTED, non-breaking — container pattern for screens with no entry sub-view) ·
erp/decisions/SEC/ADR-SEC-008.md (ACCEPTED, non-breaking — operations with no published endpoint) ·
erp/decisions/SEC/ADR-SEC-009.md (ACCEPTED, non-breaking — documented endpoints this frontend does not call) ·
erp/decisions/SEC/ADR-SEC-010.md (ACCEPTED, non-breaking — SCR-SEC-004's form vs SRS B3's input list)
Carried from earlier stages: ADR-SEC-001 (P2), ADR-SEC-002 (P3.1). No BLOCKED ADR.

TRACEABILITY
REQ covered by ≥1 SCR/F-block: 33/33 — REQ-SEC-001..033 each appear in the `traces=` of at
least one SUB block of every sub-bearing phase that owns its screen.
Orphan REQ: none.
AC covered: 33/33 (each AC accompanies its REQ in the same SUB traces).
SCR covered: 10/10 — every `SCR-*` carries a block in F1, F2, F3 and F4 (40 SUB blocks) and an
RF5 block in SEC-FE.
UXD cited by an F-block: 0 of 0 — none minted, none dangling.

Event
"P3.2 completed: SEC v1 — 10 screens, 0 UXD, 27/27 API bound (24 called), 4 sub-bearing phases
× 10 SUB blocks, ALIGN-FE PASSED, 8 ADRs"
══════════════════════════════════════════════════════════════════
