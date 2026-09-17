# PRD — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module          : NOTE     Version : v1
Source artifacts: platform-summary, module-registry, business-policies
Stories         : 7   Policies covered : 6/6   Deferred : 0
Status          : DRAFT — awaiting prd-approval
══════════════════════════════════════════════════════════════════

## النطاق المُلزِم / binding scope
هذه الوثيقة تُعيد صياغة ما أقرّته مرحلة P0 عن وحدة الملاحظات كحاجات مستخدم قابلة للتتبّع،
لا كقواعد. حجم الوحدة قيدٌ مُلزِم لا نقطة انطلاق: كيان واحد (الملاحظة)، أربع عمليات
(إنشاء · تعديل · تعطيل · بحث ضمن ملاحظات المستخدم نفسه)، شاشة مركّبة واحدة، مجموعة صلاحيات
واحدة، وصفر اعتمادية بيانات-مجال بين الوحدات. القصص السبع أدناه تغطّي هذا الحجم بالضبط؛
كل قصة إضافية في مرحلة لاحقة مخالفة نطاق لا تحسين.

الملكية هي الحدّ الوحيد للرؤية في هذه النسخة: لا مشاركة بين المستخدمين ولا اطّلاع إداري
شامل (business-policies SCOPE EXCEPTIONS). ولا تنصّ أي قصة على آلية — الحقول والقيود
والصلاحيات التفصيلية وأشكال الواجهات كلها من إنتاج P1. كل قصة هنا حالتها `DRAFT`؛ إقرار
المستخدم لهذه الوثيقة عند بوابة `prd-approval` هو ما ينقلها جميعًا إلى `APPROVED` دفعةً
واحدة، ولا تُعدَّل قصة بعد ذلك في مكانها.

This PRD restates the NOTE module as seven traceable needs. Ownership is the only
visibility boundary in v1; no story states a mechanism; every story is DRAFT until the
single approval act at the `prd-approval` gate.

## USER STORIES

US-NOTE-001
  Title          : كتابة ملاحظة بلغة كاتبها / Capture a note in the author's own words
  Story          : As a Notes-screen user, I need to write a short note with a title and a body in whichever language I am writing in, and to have it be mine from the moment I write it, so that capturing a thought costs me nothing beyond typing it.
  القصة          : بصفتي مستخدمًا لشاشة الملاحظات، أحتاج أن أكتب ملاحظة قصيرة بعنوان ونصّ باللغة التي أكتب بها، وأن تكون ملكي منذ لحظة كتابتها، لكي لا يكلّفني تدوين الفكرة أكثر من كتابتها.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-NOTE-005, POL-NOTE-001
  Source         : platform-summary OVERVIEW — "أربع عمليات (إنشاء …)" / "four operations: create"; POL-NOTE-005; POL-NOTE-001 (الملكية تنشأ بالكتابة / ownership originates at creation)
  Status         : DRAFT

US-NOTE-002
  Title          : تعديل ملاحظتي / Correct a note I own
  Story          : As a note's owner, I need to revise the title and body of a note I wrote, so that a note stays accurate without my having to write it again.
  القصة          : بصفتي مالك الملاحظة، أحتاج أن أُنقّح عنوان ملاحظتي ونصّها، لكي تبقى دقيقة دون أن أُعيد كتابتها من جديد.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-NOTE-002, POL-NOTE-005
  Source         : platform-summary OVERVIEW — "… تعديل …" / "four operations: update"; POL-NOTE-002
  Status         : DRAFT

US-NOTE-003
  Title          : تعطيل ملاحظة دون فقدها / Retire a note without losing it
  Story          : As a note's owner, I need to take a note I no longer want out of use while knowing it is not destroyed, so that clearing my list never costs me the record of what I wrote.
  القصة          : بصفتي مالك الملاحظة، أحتاج أن أُخرج ملاحظة لم أعد أريدها من الخدمة وأنا مطمئن أنها لم تُمحَ، لكي لا يكلّفني تنظيف قائمتي فقدانَ ما كتبت.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-NOTE-002, POL-NOTE-003
  Source         : platform-summary OVERVIEW — "… تعطيل …" / "four operations: deactivate"; POL-NOTE-003
  Status         : DRAFT

US-NOTE-004
  Title          : البحث في ملاحظاتي الفعّالة / Search my own live notes
  Story          : As a note's owner, I need to look through my own notes and see the live ones to begin with, confident that nobody else's notes appear and mine appear to nobody else, so that the list I work from is exactly mine and exactly current.
  القصة          : بصفتي مالك الملاحظة، أحتاج أن أبحث في ملاحظاتي أنا فلا يظهر لي غيرها ولا تظهر هي لسواي، وأن تكون الفعّالة وحدَها ما أراه ابتداءً، لكي تكون القائمة التي أعمل عليها ملكي تمامًا وحاضرةً تمامًا.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-NOTE-001, POL-NOTE-004
  Source         : platform-summary OVERVIEW — "بحث ضمن ملاحظات المستخدم نفسه" / "search (own notes only)"; POL-NOTE-001, POL-NOTE-004
  Status         : DRAFT

US-NOTE-005
  Title          : الوصول إلى ملاحظاتي المعطَّلة عن قصد / Reach my deactivated notes deliberately
  Story          : As a note's owner, I need a deliberate way to see the notes I deactivated, so that deactivation reads as setting aside rather than as deletion.
  القصة          : بصفتي مالك الملاحظة، أحتاج مسارًا مقصودًا أرى به ملاحظاتي المعطَّلة، لكي يكون التعطيل تنحيةً لا محوًا.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-NOTE-003, POL-NOTE-004, POL-NOTE-001
  Source         : POL-NOTE-004 — "استبعادها من البحث **الافتراضي**" / "excluded from its owner's **default** search"; business-policies RESOLVED DECISION #2 ("تبقى محفوظة")
  Status         : DRAFT

US-NOTE-006
  Title          : شاشة واحدة بمجموعة صلاحيات واحدة / One screen under one permission set
  Story          : As a Notes-screen user, I need my whole relationship with notes — listing them and creating or editing one — to live behind the single grant I was given, so that being allowed into Notes is one decision rather than four.
  القصة          : بصفتي مستخدمًا لشاشة الملاحظات، أحتاج أن تكون علاقتي بالملاحظات كلُّها — عرضُها وإنشاؤها وتعديلها — خلف المنح الواحد الذي أُعطيته، لكي يكون السماح لي بالملاحظات قرارًا واحدًا لا أربعة.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-NOTE-006
  Source         : module-registry SCOPE — "شاشة مركّبة واحدة (قائمة + نموذج) · مجموعة صلاحيات واحدة"; POL-NOTE-006; [KB:erp-domain-standards §4]
  Status         : DRAFT

US-NOTE-007
  Title          : حضور الوحدة وشاشتها كبيانات / The module and its screen present as data
  Story          : As the module's integrator, I need NOTE and its one screen to be known to the platform's module, screen and action registries, so that the people granted Notes can actually reach it instead of meeting a module gate that has never heard of it.
  القصة          : بصفتي مُكامِل الوحدة، أحتاج أن تكون NOTE وشاشتها الوحيدة معروفةً لسجلات الوحدات والشاشات والإجراءات في المنصة، لكي يصل إليها فعلًا مَن مُنح صلاحيتَها بدل أن يصطدم ببوابة وحدة لا تعرفها.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-NOTE-006
  Source         : module-registry SHARED ENTITIES CONSUMED — "NOTE تُسجِّل نفسها وشاشتها الوحيدة وإجراءاتها الأربعة في سجلات SEC؛ بدون ذلك تسقط بوابة الوحدة (G3)"; platform-summary DEPENDENCY MAP (NOTE → SOFT → SEC)
  Status         : DRAFT

## TRACEABILITY — story → policy
| US | Traces (POL) | Source |
|---|---|---|
| US-NOTE-001 | POL-NOTE-005, POL-NOTE-001 | platform-summary OVERVIEW ("create"); POL-NOTE-005 |
| US-NOTE-002 | POL-NOTE-002, POL-NOTE-005 | platform-summary OVERVIEW ("update"); POL-NOTE-002 |
| US-NOTE-003 | POL-NOTE-002, POL-NOTE-003 | platform-summary OVERVIEW ("deactivate"); POL-NOTE-003 |
| US-NOTE-004 | POL-NOTE-001, POL-NOTE-004 | platform-summary OVERVIEW ("search own notes"); POL-NOTE-001/004 |
| US-NOTE-005 | POL-NOTE-003, POL-NOTE-004, POL-NOTE-001 | POL-NOTE-004 ("default search"); business-policies RESOLVED DECISION #2 |
| US-NOTE-006 | POL-NOTE-006 | module-registry SCOPE; [KB:erp-domain-standards §4] |
| US-NOTE-007 | POL-NOTE-006 | module-registry SHARED ENTITIES CONSUMED; platform-summary DEPENDENCY MAP |
كل سياسة من POL-NOTE-001 إلى POL-NOTE-006 تظهر في صفٍّ واحد على الأقل أعلاه؛ لا سياسة بلا قصة.
Coverage: POL-NOTE-001 → US-001/004/005 · POL-NOTE-002 → US-002/003 · POL-NOTE-003 → US-003/005 ·
POL-NOTE-004 → US-004/005 · POL-NOTE-005 → US-001/002 · POL-NOTE-006 → US-006/007.

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | لا أولوية منصوص عليها في أي مدخل / no priority is stated in any input | الأولوية HIGH للعمليات الأربع في نص الرؤية ولشاشتها الوحيدة (US-001…004, US-006) **ولقصة حضور الوحدة (US-007)**: القصص الخمس الأولى كلها تتوقف على تسجيل الوحدة وشاشتها، فوضعُه دونها انقلابٌ في الأولوية — إن تأخّر لم يُسلَّم شيء. وتبقى US-005 وحدها MEDIUM لأنها وجهٌ ثانٍ من عملية البحث لا عملية خامسة. ومقياس النجاح "—" في الجميع لانعدام أي نص يذكره | يؤكّده المستخدم بإقرار هذه الوثيقة عند بوابة `prd-approval` | platform-summary OVERVIEW; module-registry SCOPE + DEPENDENCIES; domain-profile G3; [KB:erp-domain-standards §4]; engines/P0.5 §2 ("only if stated or clearly implied") |
| 2 | هل يصل المالك إلى ملاحظته بعد تعطيلها، وهل تُدمج الحاجة في قصة البحث؟ / can the owner still reach a deactivated note — and should the need fold into the search story? | نعم يصل، وتبقى **قصة قائمة بذاتها** (US-NOTE-005) على مستوى النية لا الآلية: كلمة "الافتراضي" في POL-NOTE-004 لا معنى لها بغير مسار غير افتراضي، والتعطيل الناعم يُبقي الصف قائمًا. والدمج في US-NOTE-004 مرفوض لسببين: يُلبس الحاجتين أولويةً واحدة (HIGH) فيُضخّم ما هو ثانوي، ويُخفي عن P1 أن أمامه قرار آلية مستقلًّا. ولا شاشة ثانية: القيد شاشة واحدة، وP1 يقرر الآلية داخلها | يؤكّده المستخدم بإقرار هذه الوثيقة عند بوابة `prd-approval` | POL-NOTE-003, POL-NOTE-004; business-policies RESOLVED DECISION #2; module-registry SCOPE; [KB:erp-domain-standards §6] |
| 3 | أي دور تحمله القصص؟ / which role do the stories carry? | دوران فقط: "مستخدم شاشة الملاحظات" (الممنوح مجموعة الصلاحيات) و"مالك الملاحظة" حيث تكون الملكية هي الموضوع؛ ودور "مُكامِل الوحدة" في US-NOTE-007 وحدها. لا دور تنظيمي (موظف/مدير) لأن المدخلات لا تسمّي أيًّا منه | يؤكّده المستخدم بإقرار هذه الوثيقة عند بوابة `prd-approval` | profiles/erp.yaml conventions.security_model; POL-NOTE-001, POL-NOTE-002, POL-NOTE-006; سابقة US-MDL-004 |
| 4 | هل يستحق التسجيل الذاتي في سجلات SEC قصة؟ / does SEC self-registration deserve a story? | نعم — قصة واحدة (US-NOTE-007) تتتبّع POL-NOTE-006، مصوغة كحاجة "أن تكون الشاشة قابلة للوصول" لا كآلية تسجيل؛ ولا تفتح صف XM ولا مفتاحًا أجنبيًا (سابقة ADR-FIN-001)، فتبقى INT-C وINT-R فارغتين لكن موجودتين. صياغة "Traces: — (scope only)" مرفوضة هنا لأن كل قصة في هذا الملف الشخصي تلزمها سياسة واحدة على الأقل (C4.4) | يؤكّده المستخدم بإقرار هذه الوثيقة عند بوابة `prd-approval` | module-registry SHARED ENTITIES CONSUMED + DEPENDENCIES; domain-profile G2/G3; project-registry DECISION INDEX #9 (ADR-FIN-001) |
لا نقطة مفتوحة بعد هذا الجدول: كل سؤال أثاره هذا التحليل مُغلَق أعلاه، ولا قصة مؤجَّلة.

## DEFERRED
| US | Reason | Activation trigger |
|---|---|---|
| — | لا قصة مؤجَّلة: كل ما تسمّيه المدخلات داخل النطاق مكتوب أعلاه، وكل ما هو خارجه (مشاركة الملاحظة، اطّلاع إداري شامل، وسوم/تصنيفات/مرفقات/تذكيرات، كيان أو شاشة ثانية، ثنائية لغة لمحتوى المستخدم، أي ربط ببيانات وحدة أخرى) مستبعَد نصًّا في platform-summary DEFERRED وbusiness-policies SCOPE EXCEPTIONS، فلا يُكتب قصةً ولو مؤجَّلة | نسخة لاحقة تُعيد تحديد النطاق صراحةً بطلب المستخدم — عندها تُضاف قصص جديدة بأرقام تالية (US-NOTE-008 فصاعدًا)، ولا تُعدَّل قصة معتمدة في مكانها |

## APPROVAL
Approved by : PENDING   Date : PENDING
Once approved, no stage may raise a question; P1 onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════
