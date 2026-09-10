## BUSINESS POLICIES — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module   : SEC     Source of truth : new project/security-module-plan-en.md
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)

POL-SEC-001 — أسبقية بوابة الوحدة / Module-gate precedence
  Statement (ar) : يجب على النظام تقييم منح الوحدة للدور قبل تقييم أي منح شاشة أو إجراء ضمن تلك الوحدة.
  Statement (en) : The system shall evaluate a role's module grant before evaluating any screen or action grant within that module.
  Pattern   : ubiquitous
  Trigger   : Any authorization check
  Rationale : الوصول الخشن (coarse) يُرفض ابتداءً، لا أن يُخفى فقط
  Source    : security-module-plan-en.md §4.2
  Status    : CONFIRMED

POL-SEC-002 — منع منح الشاشة/الإجراء اليتيم / No orphaned screen/action grant
  Statement (ar) : إذا لم يملك الدور منح وحدة الطلب، فيجب على النظام رفض أي منح شاشة أو إجراء ضمن تلك الوحدة لذلك الدور.
  Statement (en) : If a role does not hold the module grant of a requested screen or action, then the system shall reject that screen or action grant for the role.
  Pattern   : unwanted
  Trigger   : Grant assignment (Role editor)
  Rationale : سلامة بنيوية — استحالة وجود منح يتيم بالبناء
  Source    : security-module-plan-en.md §4.2
  Status    : CONFIRMED

POL-SEC-003 — المستخدم المعلّق بلا صلاحيات / Pending sign-up holds no permission
  Statement (ar) : أثناء انتظار تفعيل تسجيل مستخدم ذاتي، يجب على النظام ألا يمنح ذلك المستخدم أي صلاحية.
  Statement (en) : While a self-registered user's sign-up is pending activation, the system shall grant that user no permission.
  Pattern   : state
  Trigger   : Sign-up submitted
  Rationale : المستخدم المعلّق لا يملك صلاحيات حتى المنح الصريح
  Source    : security-module-plan-en.md §3
  Status    : CONFIRMED

POL-SEC-004 — عدم إرسال تجزئة كلمة المرور للعميل / Password hash never reaches the client
  Statement (ar) : يجب على النظام ألا يرسل تجزئة (hash) كلمة المرور إلى العميل مطلقًا.
  Statement (en) : The system shall never transmit a password hash to the client.
  Pattern   : ubiquitous
  Trigger   : Any authentication-related response
  Rationale : تخزين آمن لكلمة المرور
  Source    : security-module-plan-en.md §3
  Status    : CONFIRMED

POL-SEC-005 — دعم فصل المهام للمستهلكين / Segregation of duties support for consumers
  Statement (ar) : حيثما تُعلن وحدة مستهلكة إجراءين متعارضين، يجب على النظام دعم اشتراط أن يُسنَدا لدورين/مستخدمين متمايزين.
  Statement (en) : Where a consumer module declares two conflicting actions, the system shall support requiring those actions be held by distinct roles or users.
  Pattern   : optional
  Trigger   : Consumer module registration (e.g. FIN's entry-creator vs period-close-approver)
  Rationale : فصل المهام عند المُستهلِك يُنفَّذ عبر RBAC المشترك
  Source    : security-module-plan-en.md §4.4; general-accounting-system-plan-en.md §8.2/§10.3
  Status    : CONFIRMED

POL-SEC-006 — القائمة من المنح الفعلية فقط / Menu built from effective grants only
  Statement (ar) : يجب على النظام بناء قائمة كل مستخدم من منحه الفعلية للوحدات والشاشات فقط.
  Statement (en) : The system shall build each user's menu from only that user's effective module and screen grants.
  Pattern   : ubiquitous
  Trigger   : Menu render
  Rationale : قائمة ديناميكية بمستويين مبنية بيانيًا
  Source    : security-module-plan-en.md §6
  Status    : CONFIRMED

POL-SEC-007 — إخفاء الوحدة غير الممنوحة كليًا / Absent module entirely hidden
  Statement (ar) : إذا كانت أدوار المستخدم لا تمنح وحدة ما، فيجب على النظام حذف تلك الوحدة كليًا من قائمته ومنع الوصول إليها بالرابط المباشر.
  Statement (en) : If a user's roles do not grant a module, then the system shall omit that module entirely from the user's menu and block direct URL access to it.
  Pattern   : unwanted
  Trigger   : Menu render; direct navigation attempt
  Rationale : غياب الوحدة = غياب تام، لا إخفاء بصري فقط
  Source    : security-module-plan-en.md §4.2, §6
  Status    : CONFIRMED

POL-SEC-008 — الصلاحية الفعلية = اتحاد الأدوار / Effective permission = union across roles
  Statement (ar) : يجب على النظام حساب الصلاحيات الفعلية للمستخدم كاتحاد منح كل الأدوار المسندة إليه.
  Statement (en) : The system shall compute a user's effective permissions as the union of the grants of all roles assigned to that user.
  Pattern   : ubiquitous
  Trigger   : Any authorization check
  Rationale : مستخدم قد يحمل أكثر من دور
  Source    : security-module-plan-en.md §4.4
  Status    : CONFIRMED

POL-SEC-009 — سجل تدقيق غير قابل للتعديل / Immutable audit trail
  Statement (ar) : يجب على النظام الاحتفاظ بكل قيد في سجل التدقيق (دخول، دخول فاشل، إعادة تعيين كلمة مرور، تغيير دور/صلاحية) دون تعديل أو حذف.
  Statement (en) : The system shall retain every audit-log entry (login, failed login, password reset, role/permission change) without modification or deletion.
  Pattern   : ubiquitous
  Trigger   : Any security-relevant event
  Rationale : الأثر التدقيقي متطلب أمني لا رفاهية
  Source    : security-module-plan-en.md §5.2-§5.3
  Status    : CONFIRMED

POL-SEC-010 — أرقام لوحة التحكم مُشتقة دائمًا / Dashboard figures are always derived
  Statement (ar) : يجب على النظام حساب كل رقم في لوحة تحكم الأمان وقت الاستعلام من بيانات حية، لا من عدّاد مُخزَّن.
  Statement (en) : The system shall compute every admin-dashboard figure at query time from live data, never from a stored counter.
  Pattern   : ubiquitous
  Trigger   : Dashboard render
  Rationale : انضباط مصدر الحقيقة الواحد المُتَّبع عبر المنصة
  Source    : security-module-plan-en.md §5.2
  Status    : CONFIRMED

POL-SEC-011 — كل زر/شاشة تحكمها الصلاحية / Every widget/screen permission-gated
  Statement (ar) : يجب على النظام إظهار عنصر لوحة تحكم الأمان للمستخدم فقط إذا كان دوره يمنحه صلاحيته.
  Statement (en) : The system shall show an admin-dashboard widget to a user only if that user's role grants the widget's underlying permission.
  Pattern   : ubiquitous
  Trigger   : Dashboard render
  Rationale : كل عنصر محكوم بالصلاحية، بما فيها بوابة الوحدة
  Source    : security-module-plan-en.md §5.1
  Status    : CONFIRMED

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
| Lookup key | Added values | Source |
|---|---|---|
None named directly by the user; AUTO-added initial value sets are recorded in
module-registry-sec.md → AUTO-DECISIONS (USER_STATUS, AUDIT_EVENT_TYPE), not here —
they are not user-stated custom values.

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| Multi-factor authentication | Not mentioned by the plan; not built this batch | explicit future request | security-module-plan-en.md §3 (lists only login/sign-up/reset) |
| SSO / external identity providers | Not mentioned by the plan; not built this batch | explicit future request | security-module-plan-en.md §3 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
None — no open question was raised for SEC; the plan is fully prescriptive for this stage's scope.
══════════════════════════════════════════════════════════════════
