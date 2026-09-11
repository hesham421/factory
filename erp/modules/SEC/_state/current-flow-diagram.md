# FLOW DIAGRAM — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Stage : P3.2 (Part A — UX design)
Inputs : srs (v1), prd (v1, APPROVED), api-docs (v1), registry-srs (v1), registry-exec-be (v1)
Screens: 10 — SCR-SEC-001..010 (one per SRS Part B screen requirement)
Flows  : 11 · ADRs open : 6 — ADR-SEC-003..008 (all non-breaking)
══════════════════════════════════════════════════════════════════

يصف هذا المستند مسارات التنقّل فقط: كل مسار يبدأ من شاشة معرّفة في متطلبات الشاشات
(SRS Part B) وينتهي عند مخرج واضح. لا يُنشئ هذا المستند شاشة ولا قاعدة عمل ولا صلاحية؛
كل شاشة هنا لها مقابل واحد في `ui-ux-spec-sec.md`.

This document describes navigation paths only. Every flow starts at a screen the SRS
declares, cites the `US-*` that asks for it, and ends at a stated exit. No flow invents a
screen, a rule or a permission.

## SCREEN INDEX — SRS screen requirement → SCR

| SCR | Name (ar / en) | SRS screen req | Page code |
|---|---|---|---|
| SCR-SEC-001 | تسجيل الدخول / Login | SCR-REQ-SEC-001 | SEC_LOGIN |
| SCR-SEC-002 | التسجيل الذاتي / Sign-up | SCR-REQ-SEC-002 | SEC_SIGNUP |
| SCR-SEC-003 | نسيت / إعادة تعيين كلمة المرور / Forgot / reset password | SCR-REQ-SEC-003 | SEC_PWD_RESET |
| SCR-SEC-004 | المستخدمون / Users | SCR-REQ-SEC-004 | SEC_USERS |
| SCR-SEC-005 | الأدوار والصلاحيات / Roles & permissions | SCR-REQ-SEC-005 | SEC_ROLES |
| SCR-SEC-006 | سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry | SCR-REQ-SEC-006 | SEC_MODULE_REGISTRY |
| SCR-SEC-007 | لوحة تحكم الأمان / Admin dashboard | SCR-REQ-SEC-007 | SEC_DASHBOARD |
| SCR-SEC-008 | سجل التدقيق / Audit log | SCR-REQ-SEC-008 | SEC_AUDIT_LOG |
| SCR-SEC-009 | إدارة الجلسات النشطة / Active sessions | SCR-REQ-SEC-009 | SEC_SESSIONS |
| SCR-SEC-010 | القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu | SCR-REQ-SEC-010 | (none — global component) |

Ten SRS screen requirements, ten `SCR-*` — B4 of the reconciliation holds by construction.

## FLOWS

```
FLOW — Sign in                                  traces=US-SEC-001,REQ-SEC-001,REQ-SEC-002,SCR-SEC-001
Screens   : SCR-SEC-001, SCR-SEC-010, SCR-SEC-007
Sequence  : (public entry) → SCR-SEC-001 Login → [credentials accepted] → SCR-SEC-010 menu renders
            → the caller's own landing screen (SCR-SEC-007 when the dashboard is in the menu)
            → [credentials rejected] → SCR-SEC-001 with the invalid-credentials message, no session
Trigger   : تشغيل المنصة دون جلسة صالحة / opening the platform without a valid session
Priority  : HIGH (PRD US-SEC-001 — the entry point of the whole module)
```
تسجيل الدخول هو نقطة الدخول الوحيدة؛ لا تُعرض أي شاشة داخلية قبل نجاحه.
The rejected path is part of this flow, not a separate one: REQ-SEC-002 returns the user to
the same screen, and the failed attempt is recorded by the server (audit), not by the UI.

```
FLOW — Self-registration                        traces=US-SEC-002,REQ-SEC-003,SCR-SEC-002
Screens   : SCR-SEC-002, SCR-SEC-001
Sequence  : SCR-SEC-001 "Sign up" → SCR-SEC-002 Sign-up → [submitted] → confirmation state
            → SCR-SEC-001 (no session, no account yet — the request is PENDING)
Trigger   : زائر غير مصادَق يطلب حسابًا / a prospective user asking for an account
Priority  : MEDIUM (PRD US-SEC-002)
```
لا يُمنح أي وصول عند التقديم؛ المسار ينتهي بطلب معلّق ينتظر مراجعة مسؤول الأمان
(يُستكمل في «Sign-up review»).

```
FLOW — Password reset                           traces=US-SEC-003,US-SEC-012,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,SCR-SEC-003
Screens   : SCR-SEC-003, SCR-SEC-001
Sequence  : SCR-SEC-001 "Forgot password?" → SCR-SEC-003 step 1 (email) → generic confirmation
            → [user follows the emailed link] → SCR-SEC-003 step 2 (token + new password)
            → [accepted] → SCR-SEC-001 → [token expired or used] → SCR-SEC-003 step 2 with the
              invalid-link message, nothing changed
Trigger   : فقدان كلمة المرور / a user who cannot sign in
Priority  : MEDIUM (PRD US-SEC-003)
```
الخطوتان شاشة واحدة (Wizard) بمعرّف `SCR-SEC-003` واحد، والخطوة معرّفة في المسار لا في حالة
محلية. رسالة الخطوة الأولى عامة دائمًا ولا تكشف ما إذا كان البريد مسجّلًا. الإشعار الاختياري
(REQ-SEC-029) خادمي بالكامل ولا يظهر في هذا المسار.

```
FLOW — User administration                      traces=US-SEC-004,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,SCR-SEC-004
Screens   : SCR-SEC-004, SCR-SEC-005
Sequence  : SCR-SEC-010 menu → SCR-SEC-004 Users (search) → [New] or [row selected] → the entry
            drawer over the same list → save → back to the list, refreshed
            → [Assign roles] → role multi-select in the same drawer (references SCR-SEC-005's roles)
            → [Deactivate] / [Reactivate] → confirmation → the list row's status changes
Trigger   : مسؤول أمان يضبط من يملك وصولًا الآن / an administrator adjusting who has access
Priority  : HIGH (PRD US-SEC-004)
```
الشاشة مركّبة (بحث + إدخال) بمعرّف واحد؛ الإدخال يُفتح فوق القائمة عبر وسيط مسار، لا عبر
حالة محلية. تعطيل المستخدم يُنهي جلساته خادميًا (REQ-SEC-011)، ويُرى أثره في
«Session response» دون أن يقوم هذا المسار بذلك بنفسه.

```
FLOW — Sign-up review                           traces=US-SEC-002,REQ-SEC-004,REQ-SEC-005,SCR-SEC-004
Screens   : SCR-SEC-004
Sequence  : SCR-SEC-004 → "Pending sign-ups" sub-view → [row] → Approve → a user is created
            ACTIVE and appears in the users list │ Reject → the request is marked REJECTED and
            no user is created
Trigger   : وجود طلبات تسجيل معلّقة (تُبرزه لوحة التحكم عبر onboarding funnel)
Priority  : MEDIUM (PRD US-SEC-002)
```
مراجعة الطلبات تعيش داخل `SCR-SEC-004` كعرض فرعي، لا كشاشة مستقلة: هي نفس صلاحية
إدارة المستخدمين ونفس المستخدم المسؤول (SRS B3 / Access summary).

```
FLOW — Role and grant administration            traces=US-SEC-005,US-SEC-007,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,SCR-SEC-005
Screens   : SCR-SEC-005
Sequence  : SCR-SEC-010 menu → SCR-SEC-005 (role master list) → [role selected] → the 3-level
            grant tree beside it → grant a module → grant a screen inside that module
            → grant an action on that screen → [revoke the module] → confirmation naming the
            cascade → the tree collapses that module's screens and actions
Trigger   : تغيير ما يستطيع دور فعله / changing what a role can do
Priority  : HIGH — PRD US-SEC-005 names this "the core improvement"
```
الترتيب الهرمي هو المسار نفسه: لا يمكن الوصول إلى عقدة شاشة قبل منح وحدتها، ولا إلى عقدة
إجراء قبل منح شاشتها، ولا إلى إجراء غير العرض قبل منح VIEW على تلك الشاشة. المحاولة المرفوضة
تبقى في نفس الشاشة برسالتها. السحب الفردي لمنح شاشة أو إجراء غير متاح — ADR-SEC-008.

```
FLOW — Module onboarding review                 traces=US-SEC-006,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,SCR-SEC-006
Screens   : SCR-SEC-006, SCR-SEC-005
Sequence  : SCR-SEC-010 menu → SCR-SEC-006 (module tree) → [module node] → its screens
            → [screen node] → its actions and their derived permission codes
            → the reviewer moves to SCR-SEC-005 to grant what the tree showed
Trigger   : وحدة مستهلكة سجّلت نفسها وتحتاج تأكيدًا بصريًا قبل المنح
Priority  : HIGH — foundational to every other module's onboarding (PRD US-SEC-006)
```
التسجيل نفسه يقع عبر نداء الوحدة المستهلكة لا عبر هذه الشاشة؛ المسار هنا للقراءة والمراجعة
ثم الانتقال إلى المنح. الشاشة للقراءة فقط — ADR-SEC-008.

```
FLOW — Security monitoring                      traces=US-SEC-009,REQ-SEC-022,REQ-SEC-023,SCR-SEC-007
Screens   : SCR-SEC-007, SCR-SEC-008, SCR-SEC-009
Sequence  : SCR-SEC-010 menu → SCR-SEC-007 dashboard (every figure computed live)
            → [recent activity widget] → SCR-SEC-008 Audit log
            → [active sessions widget] → SCR-SEC-009 Active sessions
            → [onboarding funnel] → SCR-SEC-004 pending sign-ups sub-view
Trigger   : بداية يوم مسؤول الأمان / an administrator looking for risk at a glance
Priority  : MEDIUM — PRD US-SEC-009 calls the dashboard a "recommended baseline"
```
لوحة التحكم هي نقطة الانطلاق لا الوجهة؛ كل عنصر فيها يفتح الشاشة المصدر. العنصر الذي لا
يملك المستخدم صلاحيته لا يُعاد من الخادم أصلًا، فلا يظهر ولا يُفتح مساره (ADR-SEC-005).

```
FLOW — Audit investigation                      traces=US-SEC-010,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,SCR-SEC-008
Screens   : SCR-SEC-008
Sequence  : SCR-SEC-007 or the menu → SCR-SEC-008 → filter by event type, actor, date range
            → the filtered list → [Export] → a CSV of exactly the filtered entries
Trigger   : حادثة أمنية أو مراجعة دورية / an incident or a periodic review
Priority  : MEDIUM (PRD US-SEC-010)
```
لا يوجد مسار إنشاء أو تعديل: القيود تُلحَق من الخادم فقط ولا تُعدَّل بعد كتابتها. التصفية
تُعكس في وسائط المسار حتى يكون العرض المفلتر قابلًا للمشاركة (ADR-SEC-003).

```
FLOW — Session response                         traces=US-SEC-011,REQ-SEC-027,REQ-SEC-028,SCR-SEC-009
Screens   : SCR-SEC-009
Sequence  : SCR-SEC-007 or the menu → SCR-SEC-009 (non-terminated sessions only)
            → [row → Terminate] → confirmation → the row leaves the list and the affected
              user must sign in again
Trigger   : جلسة مشبوهة أو مهجورة / a compromised or abandoned session
Priority  : MEDIUM (PRD US-SEC-011)
```
الإنهاء هو التغيير الوحيد في هذه الشاشة؛ لا نموذج إدخال ولا إنشاء.

```
FLOW — Navigation                               traces=US-SEC-008,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,SCR-SEC-010
Screens   : SCR-SEC-010 (host of every authenticated screen above)
Sequence  : [session established] → SCR-SEC-010 renders modules → screens from the caller's
            effective grants → [screen entry chosen] → that screen's route
            → [a route reached directly without its grant] → the unauthorized destination
Trigger   : كل تحميل صفحة بعد المصادقة / every authenticated page load
Priority  : HIGH (PRD US-SEC-008)
```
القائمة مشتقّة بالكامل ولا تُدخَل يدويًا: ما لا يُمنح لا يظهر (REQ-SEC-032)، وما لا يظهر لا
يُبلَغ حتى بالعنوان المباشر — والفحص خادمي في الحالتين (REQ-SEC-033). هذه الشاشة هي المصدر
الوحيد لبوابة العرض في الواجهة (ADR-SEC-005).

## RECONCILIATION — SEC v1

```
RECONCILIATION — SEC v1
B1 every US-* used in a flow has an SRS counterpart (REQ/AC/screen)
   → US-SEC-001..012 all cited; each resolves to ≥1 REQ and ≥1 SCR-REQ (SRS traceability
     matrix). No flow was excluded and no screen was invented.
B2 no RULE-* contradicts a flow/spec outcome
   → RULE-SEC-001/002/007 shape the grant tree's reachability (they are the flow, not a
     contradiction of it); RULE-SEC-003 is the cascade the revoke step announces;
     RULE-SEC-005 blocks the second conflicting action inside the same step;
     RULE-SEC-004 blocks a screen registration server-side (SCR-SEC-006 is read-only);
     RULE-SEC-006 is the rejected branch of "Password reset". No contradiction found.
B3 every field/permission on a screen exists in the SRS
   → fields copied from SRS A3 per owning ENT and reconciled against the api-docs DTOs in
     ui-ux-spec-sec.md; permission names taken from the api-docs (backend-declared), never
     minted here. Extra removed: none. Missing added: none.
B4 every screen entry of the SRS has exactly one SCR-* block
   → 10 SRS screen requirements ↔ SCR-SEC-001..010, 1:1 (SCREEN INDEX above).
RESULT  reconciled 10 · reworked 0 · ADRs ADR-SEC-003, ADR-SEC-004, ADR-SEC-005,
        ADR-SEC-006, ADR-SEC-007, ADR-SEC-008 (all non-breaking, raised in Part B's
        binding to the published api-docs and recorded here for completeness)
```
══════════════════════════════════════════════════════════════════
