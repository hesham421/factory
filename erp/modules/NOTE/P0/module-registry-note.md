## MODULE REGISTRY — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module Code    : NOTE   (profile.vocabulary.module_prefixes → `NOTE: Notes`)
Bounded context: productivity   (سياق جديد يملك NOTE وحده — platform-summary RESOLVED DECISION #1)
Layer / Type   : L1 / master data     Execution tier : 1.4
Source         : NEW
Knowledge      : profiles/erp/knowledge/erp-domain-standards.md §1, §2, §4, §6; erp/domain-profile.md §7
Readiness      : READY
══════════════════════════════════════════════════════════════════

SCOPE (قيد مُلزِم — binding constraint on every later stage)
كيان واحد · أربع عمليات (إنشاء · تعديل · تعطيل · بحث ضمن ملاحظات المستخدم نفسه) · شاشة
مركّبة واحدة (قائمة + نموذج إنشاء/تعديل) · مجموعة صلاحيات واحدة على تلك الشاشة · صفر
اعتماديات بيانات-مجال بين الوحدات (التسجيل الذاتي في SEC استثناء منصّي لا خيار فيه — انظر DEPENDENCIES).
One entity · four operations (create · update · deactivate · search own notes) · one
composite screen (list + create/edit form) · one permission set · zero cross-module
dependencies. أي توسيع لهذا الحجم في مرحلة لاحقة هو مخالفة نطاق، لا تحسين.

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar/en) | Kind | PRIVATE / SHARED | Source |
|---|---|---|---|
| الملاحظة / Note | master | PRIVATE — لا وحدة أخرى تقرأها؛ الملاحظة مرئية لمالكها فقط (POL-NOTE-001) | رؤية الوحدة: "one entity: note (id, title, body, owner, audit fields, active flag)"; [KB:erp-domain-standards §2] |

LOOKUPS OWNED    (value lists this module masters)
None — الوحدة لا تملك أي قائمة قيم مُرمَّزة. علم النشاط (`isActiveFl`) قيمة منطقية باصطلاح
المنصة، لا نوع lookup [KB:erp-domain-standards §6 soft delete]، فلا شيء يُسجَّل في MDL.
Rule (profile): all LOV values runtime-loaded from the lookup module; no hardcoded enums
in APIs or field specs — تبقى سارية، وهي مُحقَّقة هنا بانعدام أي قائمة قيم أصلًا.

LOOKUPS CONSUMED (from other modules)
| Lookup key | Owner code | READ-ONLY |
None — لا قيمة مُرمَّزة تُقرأ من MDL ولا من غيرها.

SHARED ENTITIES CONSUMED
| Entity | Owner code | HARD-FK / SOFT-READ | Why |
|---|---|---|---|
| ModuleRegistry (ENT-SEC-004), ScreenRegistry (ENT-SEC-005), ActionRegistry (ENT-SEC-006) | SEC | SOFT-READ (تسجيل كبيانات / registration as data) | NOTE تُسجِّل نفسها وشاشتها الوحيدة وإجراءاتها الأربعة في سجلات SEC؛ بدون ذلك تسقط بوابة الوحدة (G3) وتغيب الشاشة كليًا عن القائمة وعن الوصول المباشر بالرابط |
| User (ENT-SEC-001) — الهوية كسلسلة أصل / identity as a principal string | SEC | SOFT-READ (لا مفتاح أجنبي / no FK) | مالك الملاحظة وحقول التدقيق (createdBy/updatedBy) تحمل معرِّف الأصل الذي يسلّمه المعترِض القياسي — نفس نمط SEC db-script §3 AUDIT COLUMNS المطبَّق في الوحدات الثلاث المكتملة |
لا مفتاح أجنبي فيزيائي في أي من الصفين، ولا كيان من كيانات NOTE يُقرأ من خارجها.

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
|---|---|---|
| SEC | SOFT | تسجيل الوحدة/الشاشة/الإجراء كبيانات + الهوية والتفويض عبر بوابة الوحدة / self-registration + identity & the module gate |
| MDL | — | لا شيء: NOTE لا تملك ولا تستهلك أي قائمة قيم مُرمَّزة، فلا موضوع لـ G4 هنا / nothing — NOTE owns and consumes no coded value list |
ROOT: NO — اعتمادية ناعمة واحدة على وحدة Tier 0؛ لا تُغيِّر الطبقة ولا الترتيب 1.4 (نفس منطق
MDL في P0: "a SOFT-READ foundation dependency on another Tier-0 module does not change tiering").
"صفر اعتماديات" في نص الرؤية تعني صفر اعتمادية **بيانات-مجال** — وهي محقَّقة حرفيًا هنا — لا
إعفاءً من بوابة الوحدة، فلا وحدة في هذه المنصة تملك أمانها الخاص (G2).
ولا يُفتح صف XM: سابقة ADR-FIN-001 (project-registry DECISION INDEX #9) تنص أن اعتماد
الهوية/التفويض والتسجيل الذاتي ليس صف XM وأن لا مفتاح أجنبي بين الوحدات في هذا الخط. لذلك
يُتوقَّع أن تكون مرحلتا INT-C وINT-R في خطة التنفيذ **فارغتين لكن موجودتين**، لا محذوفتين.

AUTO-DECISIONS
AUTO: الكيان الوحيد مصنَّف master لا transactional
  FROM: [KB:erp-domain-standards §2] — المستند transactional مرتبط بفترة (fiscalYearId/periodId)
        ومدفوع بحالة من lookup، وليس للملاحظة أي من الاثنين؛ بينما التعطيل الناعم (isActiveFl)
        هو بالضبط اصطلاح master نفسه [KB:erp-domain-standards §2 rule 1, §6]
  IF WRONG: أعد تصنيفه transactional في P1 — يستدعي عندئذٍ حقول الفترة وحالة من MDL، أي
        اعتمادية XM جديدة ونموًّا في النطاق؛ لا يُفعَل إلا بقرار صريح.
AUTO: الشاشة المركّبة واحدة (قائمة + نموذج) بمعرّف SCR واحد
  FROM: [KB:erp-domain-standards §4] — Search + Entry = ONE SCR, ONE SEC_PAGES row;
        ومطابق لنص الرؤية "one screen: a list with a create/edit form"
  IF WRONG: فصلها إلى شاشتين يخالف المعيار والرؤية معًا — لا يُوصى به.
AUTO: مجموعة صلاحيات واحدة على تلك الشاشة تحكم العمليات الأربع
  FROM: رؤية الوحدة ("one permission set on that screen") + profiles/erp.yaml
        conventions.security_model (VIEW/CREATE/UPDATE/DELETE على شاشة ممنوحة)
  IF WRONG: إضافة مجموعة ثانية تتطلب شاشة ثانية — أي نموًّا في النطاق.
AUTO: التعطيل ناعم دائمًا، ولا حذف نهائي في أي عملية
  FROM: [KB:erp-domain-standards §6] (soft delete هو الافتراضي) + العملية الرابعة في الرؤية
        اسمها "deactivate" لا "delete"
  IF WRONG: الحذف النهائي يُلغي أثر التدقيق؛ لا يُوصى به.
AUTO: اعتمادية SEC مصنَّفة SOFT لا HARD
  FROM: [KB:erp-domain-standards §5] (SOFT-READ = قراءة بالكود، مسموحة في أي اتجاه) + سابقة
        erp/modules/MDL/P0/module-registry-mdl.md التي صنَّفت اعتماد MDL على SEC بـ SOFT للسبب
        نفسه: الحاجة فحصُ وجود/تسجيل على مستوى التطبيق، لا تكامل مرجعي فيزيائي. (FIN كتبت HARD،
        لكن P2 أعادت تصنيفها إلى غير-XM في ADR-FIN-001 — تُتَّبع النتيجة لا الصياغة الأولى.)
  IF WRONG: ترقيتها إلى HARD تتطلب مفتاحًا أجنبيًا بين الوحدات، وهو ممنوع في هذا الخط بموجب
        ADR-FIN-001 — يلزمها ADR جديد يَنسخ تلك السابقة.
AUTO: الطبقة L1 والتِّرتيب 1.4، وROOT: NO
  FROM: [KB:erp-domain-standards §1] + انعدام أي اعتمادية؛ engines/P0 §2.3 number stability
  IF WRONG: أعد الترقيم فقط إذا أعيد ترتيب الطبقات منصّيًا؛ الرقم لا ينزاح بعد تثبيته.

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | السياق المحدود / bounded context | `productivity` — سياق جديد يملك NOTE وحده | موصى به — ينتظر تأكيد المستخدم | profiles/erp.yaml vocabulary.bounded_contexts; platform-summary decision #1 |
| 2 | صفر XM مقابل domain-profile §6 | **مُعدَّل في الجولة 2** — اعتمادية SEC تُسجَّل SOFT (تسجيل ذاتي + بوابة الوحدة) كما فعلت MDL وFIN في P0؛ ويبقى: لا صف XM ولا مفتاح أجنبي (سابقة ADR-FIN-001). لا اعتمادية على MDL إطلاقًا | موصى به | project-registry SHARED ENTITY DECLARATIONS + DECISION INDEX #9; erp/modules/MDL/P0/module-registry-mdl.md; [KB:erp-domain-standards §5] |
| 3 | نوع الكيان / entity kind | master | موصى به | [KB:erp-domain-standards §2] |
| 4 | ثنائية اللغة في محتوى المستخدم | لا تسري على العنوان/النص؛ تسري على أسماء الوحدة والكيان والشاشة — POL-NOTE-005 | موصى به | domain-profile G11; [KB:erp-domain-standards §2 rule 1] |

POLICIES OWNED (full text in business-policies-note.md)
POL-NOTE-001, POL-NOTE-002, POL-NOTE-003, POL-NOTE-004, POL-NOTE-005, POL-NOTE-006
══════════════════════════════════════════════════════════════════
