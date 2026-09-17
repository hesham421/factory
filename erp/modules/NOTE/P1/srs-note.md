# SRS — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module : NOTE   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-17 — gate `prd-approval`)
Counts : REQ 18 · AC 24 · ENT 1 · RULE 7 · SCR-REQ 1 · ADR 3
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information

| Item | Value |
|---|---|
| الوحدة / Module | الملاحظات / Notes |
| رمز الوحدة / Module code | NOTE |
| السياق المحدود / Bounded context | productivity |
| النسخة / Version | v1 |
| التاريخ / Date | 2026-09-17 |
| الحالة / Status | COMPLETE — pass P1, round 1 |
| أعدّها / Prepared by | P1 (SRS engine), lane `analysis` |
| القرارات المطبَّقة / Decisions applied | 3 ADR + 4 DEFAULT (see STANDALONE) |
| المدخلات / Inputs | prd-note.md (APPROVED), domain-profile.md v1, project-registry.md v1.3.0, module-registry-note.md, business-policies-note.md |

## A2 — Functional context

**داخل النطاق / In scope**
كيان واحد (الملاحظة) · أربع عمليات (إنشاء · تعديل · تعطيل · بحث ضمن ملاحظات المستخدم نفسه)
· شاشة مركّبة واحدة (قائمة + نموذج إنشاء/تعديل) · مجموعة صلاحيات واحدة على تلك الشاشة ·
تسجيل ذاتي للوحدة وشاشتها وإجراءاتها في سجلات SEC. هذا الحجم قيدٌ مُلزِم من
`module-registry-note.md → SCOPE`، لا نقطة انطلاق.

**خارج النطاق / Out of scope**
مشاركة الملاحظة مع مستخدم آخر · اطّلاع إداري شامل على ملاحظات الآخرين · الوسوم والتصنيفات
والمرفقات والتذكيرات · كيان ثانٍ أو شاشة ثانية · محتوى ثنائي اللغة يكتبه المستخدم ·
أي قائمة قيم مُرمَّزة تُملك أو تُستهلَك · أي مفتاح أجنبي أو صف XM بين NOTE وأي وحدة أخرى ·
**إعادة تفعيل ملاحظة معطَّلة** — لا قصة معتمدة تطلبها، والعمليات أربع لا خمس.

**وظيفة الوحدة / Module function**
تُتيح الوحدة لمستخدمٍ ممنوحٍ شاشةَ الملاحظات أن يدوّن ملاحظة قصيرة بعنوان ونصّ بلغته هو،
ثم يُنقّحها، ويُخرجها من الخدمة بالتعطيل حين لا يعود يريدها، ويبحث في ملاحظاته هو دون سواها.
الملكية هي الحدّ الوحيد للرؤية في هذه النسخة: ما كتبه المستخدم يراه هو وحده، ولا يرى غيرَ ما كتب.

**الوصف التفصيلي / Detailed description**
المستخدم يدخل شاشة الملاحظات بعد أن تُجيزه بوابة الوحدة ثم منح الشاشة (domain-profile G3).
تُعرض له قائمة ملاحظاته الفعّالة ابتداءً، مُرتّبة بالأحدث. يفتح نموذج الإنشاء فيكتب عنوانًا
ونصًّا ويحفظ؛ يصير مالكَ الملاحظة لحظةَ الحفظ ولا يُؤخذ المالك من الطلب إطلاقًا. يفتح ملاحظة
قائمة فيُعدّل عنوانها أو نصّها. يُعطّل ملاحظة فتخرج من قائمته الافتراضية ويبقى صفّها محفوظًا،
ويصل إليها متى شاء عبر مسار حالة مقصود داخل الشاشة نفسها. الأدوار في هذه النسخة اثنان فقط:
"مستخدم شاشة الملاحظات" (الممنوح مجموعة الصلاحيات) و"مالك الملاحظة" (الوجه الذي تخصّه الملكية)،
ودور "مُكامِل الوحدة" الذي يخصّ التسجيل في سجلات SEC (prd RESOLVED DECISION #3).

**الوضع الحالي / Current situation**
| الخطوة | الجهة | ملاحظة |
|---|---|---|
| تدوين الملاحظة | المستخدم نفسه | خارج المنصة — ورق أو ملف شخصي أو أداة غير مُدارة |
| الرجوع إليها | المستخدم نفسه | لا بحث ولا ترتيب ولا ضمان بقاء |
| التخلّص منها | المستخدم نفسه | محو نهائي بلا أثر |

**الصعوبات الحالية / Current difficulties**
ما يُدوَّن خارج المنصة يضيع، ولا يخضع لأي ضبط صلاحيات، والتخلّص منه محوٌ لا رجعة فيه.

**النظام المقترح ومنافعه / Proposed system and benefits**
موضع واحد داخل المنصة للملاحظة، محكومٌ بمجموعة صلاحيات واحدة، بملكية صارمة، وبتعطيل ناعم
يُبقي ما كُتب قائمًا (POL-NOTE-003) — فتنظيف القائمة لا يكلّف فقدان السجل.

**ملاحظات عامة / General notes**
لا محرك سير عمل (domain-profile G12) · لا ترقيم مستندات لأن الملاحظة ليست مستندًا مُرقَّمًا
(§3.3 NUMBERING) · لا قائمة قيم مُرمَّزة فلا شيء يُسجَّل في MDL · المحتوى الذي يكتبه المستخدم
أحادي اللغة بنصّ POL-NOTE-005، بينما تبقى ثنائية اللغة سارية كاملةً على كل تسمية وشاشة ورسالة.

## A3 — Entities and fields

**الحقول القياسية لكل نوع كيان (من الملف الشخصي) / Standard fields per entity kind**

| Kind | Default fields |
|---|---|
| master | nameAr, nameEn, code, isActiveFl, createdBy, createdAt, updatedBy, updatedAt |
| transactional | docNo, docDate, statusCode, fiscalYearId, periodId, createdBy, createdAt, updatedBy, updatedAt |
| lookup | code, nameAr, nameEn, sortOrder, isActiveFl |
| config | key, valueAr, valueEn, isActiveFl |

تُكتب مرة واحدة هنا ولا تُعاد لكل كيان. المفتاح الأساسي `{entity}Pk`؛ حقول العلم تنتهي بـ `Fl`؛
حقول التدقيق `createdBy, createdAt, updatedBy, updatedAt` يملؤها النظام ولا تُقبل من العميل أبدًا.
الأنواع هنا منطقية فقط — الأنواع الفيزيائية من إنتاج P2.

### ENT-NOTE-001 — الملاحظة / Note

| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE — لا وحدة أخرى تقرأها (POL-NOTE-001) | **لا / no** — معرّف الملاحظة لا يُستخدم خارج النظام، ولا سياسة ولا قصة تطلب مرجعًا مقروءًا، وليست مستندًا مُرقَّمًا (§3.3 NUMBERING) | create · read · update · deactivate · search | `ownerUserRef` وحقول التدقيق تحمل معرّف الأصل المُصادَق الصادر عن SEC (SOFT-READ إلى ENT-SEC-001، بلا مفتاح أجنبي) | module-registry-note.md ENTITIES OWNED; POL-NOTE-001…005 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| notePk | reference | yes | مولَّد من النظام / system-generated | المفتاح الأساسي، غير معروض للمستخدم كمرجع عمل | المعرّف | Identifier |
| noteTitle | text | yes | نص حرّ بلغة كاتبه / free text in its author's language (POL-NOTE-005) | RULE-NOTE-001, RULE-NOTE-003 | العنوان | Title |
| noteBody | text | yes | نص حرّ بلغة كاتبه / free text in its author's language (POL-NOTE-005) | RULE-NOTE-002, RULE-NOTE-003 | النص | Body |
| ownerUserRef | text | yes | معرّف الأصل المُصادَق / the authenticated principal (ENT-SEC-001, SOFT-READ, no FK) | يملؤه النظام، لا يُقبل من العميل — RULE-NOTE-004 | المالك | Owner |
| isActiveFl | flag | yes | `true` عند الإنشاء / `true` on creation | التعطيل الناعم — RULE-NOTE-006, RULE-NOTE-007 | فعّالة | Active |
| createdBy | text | yes | نظام / system | معرّف الأصل المنشئ | أنشأها | Created by |
| createdAt | date-time | yes | نظام / system | UTC مخزَّنة، تُعرض بتوقيت المستأجر [KB:erp-domain-standards §6] | تاريخ الإنشاء | Created at |
| updatedBy | text | no | نظام / system | يُملأ عند أول تعديل | عدّلها | Updated by |
| updatedAt | date-time | no | نظام / system | يُملأ عند أول تعديل | تاريخ التعديل | Updated at |

**انحراف مُعلَن عن حقول `master` القياسية / declared deviation** — الكيان لا يحمل `nameAr`/`nameEn`/`code`:
محتوى المستخدم أحادي اللغة بنصّ POL-NOTE-005، ولا كود عمل للملاحظة (§3.3 NUMBERING). القرار في
ADR-NOTE-001؛ باقي حقول `master` (`isActiveFl` + حقول التدقيق الأربعة) محمولة كاملةً أعلاه.

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-NOTE-001 — إنشاء ملاحظة / Create a note
  Pattern    : event
  Statement  : When a Notes-screen user submits a new note with a title and a body, the system shall store the note and return it to its author.
  بالعربية   : عند إرسال مستخدم شاشة الملاحظات ملاحظةً جديدة بعنوان ونصّ، يحفظ النظام الملاحظة ويُعيدها إلى كاتبها.
  Traces     : US-NOTE-001
  Entities   : ENT-NOTE-001
  Rationale  : العملية الأولى من العمليات الأربع في نطاق الوحدة
  Source     : US-NOTE-001; POL-NOTE-005
  Priority   : HIGH

#### AC-NOTE-001 — المسار السعيد للإنشاء / create happy path
  Traces : REQ-NOTE-001
  Given  : مستخدم ممنوح شاشة الملاحظات وإجراء CREATE عليها
  When   : يُرسل ملاحظة بعنوان "اجتماع الاثنين" ونصّ غير فارغ
  Then   : تُحفظ الملاحظة وتُعاد بمعرّفها، وتظهر رسالة النجاح — ar: «تم حفظ الملاحظة.» · en: "The note has been saved."

#### AC-NOTE-002 — ختم التدقيق عند الإنشاء / audit stamp on creation
  Traces : REQ-NOTE-001
  Given  : مستخدم ممنوح إجراء CREATE على شاشة الملاحظات
  When   : يحفظ ملاحظة جديدة
  Then   : تحمل الملاحظة `createdBy` بمعرّف الأصل المُصادَق و`createdAt` بلحظة الحفظ، ولا يُقبل أيٌّ منهما من الطلب

### REQ-NOTE-002 — اشتقاق المالك من الأصل المُصادَق / Owner derived from the authenticated principal
  Pattern    : ubiquitous
  Statement  : The system shall derive every note's owner from the authenticated principal that created it, disregarding any owner value supplied by a client.
  بالعربية   : يشتقّ النظام مالكَ كل ملاحظة من الأصل المُصادَق الذي أنشأها، ولا يلتفت إلى أي قيمة مالك يُرسلها العميل.
  Traces     : US-NOTE-001
  Entities   : ENT-NOTE-001
  Rationale  : الملكية تنشأ بالكتابة (POL-NOTE-001) — ولو قُبلت من الطلب لسقط الحدّ كلّه
  Source     : US-NOTE-001; POL-NOTE-001
  Priority   : HIGH

#### AC-NOTE-003 — تجاهل مالك مُرسَل من العميل / client-supplied owner ignored
  Traces : REQ-NOTE-002
  Given  : المستخدم «أ» مُصادَق عليه وممنوح إجراء CREATE
  When   : يُرسل ملاحظة تحمل قيمة مالك تشير إلى المستخدم «ب»
  Then   : تُحفظ الملاحظة بمالكها «أ»، ولا تظهر للمستخدم «ب» في أي بحث

### REQ-NOTE-003 — الملاحظة فعّالة عند إنشائها / A new note starts active
  Pattern    : event
  Statement  : When a note is created, the system shall mark it active.
  بالعربية   : عند إنشاء الملاحظة، يجعلها النظام فعّالة.
  Traces     : US-NOTE-001
  Entities   : ENT-NOTE-001
  Rationale  : البحث الافتراضي يُظهر الفعّالة وحدها؛ لو وُلدت معطَّلة لغابت عن كاتبها فور كتابتها
  Source     : US-NOTE-001; POL-NOTE-004; [KB:erp-domain-standards §6]
  Priority   : HIGH

#### AC-NOTE-004 — الملاحظة الجديدة تظهر في البحث الافتراضي / new note appears in the default search
  Traces : REQ-NOTE-003
  Given  : مستخدم لتوّه حفظ ملاحظة جديدة
  When   : يفتح قائمة ملاحظاته دون تحديد أي حالة
  Then   : تظهر الملاحظة في القائمة بحالة فعّالة

### REQ-NOTE-004 — رفض ملاحظة ناقصة / Reject an incomplete note
  Pattern    : unwanted
  Statement  : If a note is submitted with a required field missing, blank or longer than its declared maximum, then the system shall reject the save and return the message of the rule that failed.
  بالعربية   : إذا أُرسلت ملاحظة بحقل إلزامي مفقود أو فارغ أو أطول من حدّه المعلَن، فيرفض النظام الحفظ ويُعيد رسالة القاعدة التي أخفقت.
  Traces     : US-NOTE-001
  Entities   : ENT-NOTE-001
  Rationale  : أخطاء قاعدة البيانات لا تصل المستخدم؛ كل قيد يُخفق له رسالة عمل
  Source     : US-NOTE-001; POL-NOTE-005; engine §5
  Priority   : HIGH

#### AC-NOTE-005 — عنوان فارغ / empty title
  Traces : REQ-NOTE-004
  Given  : مستخدم في نموذج إنشاء ملاحظة
  When   : يحفظ ونصّ الملاحظة مكتوب والعنوان فارغ
  Then   : يُرفض الحفظ وتظهر رسالة RULE-NOTE-001 — ar: «عنوان الملاحظة مطلوب.» · en: "A note title is required."

#### AC-NOTE-006 — نصّ فارغ / empty body
  Traces : REQ-NOTE-004
  Given  : مستخدم في نموذج إنشاء ملاحظة
  When   : يحفظ والعنوان مكتوب والنص فارغ
  Then   : يُرفض الحفظ وتظهر رسالة RULE-NOTE-002 — ar: «نصّ الملاحظة مطلوب.» · en: "A note body is required."

### REQ-NOTE-005 — تعديل ملاحظة مملوكة / Update an owned note
  Pattern    : event
  Statement  : When a note's owner submits a revised title or body for a note they own, the system shall replace the stored values with the submitted ones.
  بالعربية   : عند إرسال مالك الملاحظة عنوانًا أو نصًّا مُنقّحًا لملاحظة يملكها، يستبدل النظام القيم المحفوظة بالمُرسَلة.
  Traces     : US-NOTE-002
  Entities   : ENT-NOTE-001
  Rationale  : العملية الثانية من العمليات الأربع
  Source     : US-NOTE-002; POL-NOTE-002
  Priority   : HIGH

#### AC-NOTE-007 — المسار السعيد للتعديل / update happy path
  Traces : REQ-NOTE-005
  Given  : ملاحظة فعّالة يملكها المستخدم «أ»
  When   : يُرسل «أ» عنوانًا جديدًا ونصًّا جديدًا لها
  Then   : تُحفظ القيم الجديدة، ويُملأ `updatedBy`/`updatedAt`، وتظهر رسالة النجاح — ar: «تم حفظ التعديل.» · en: "The change has been saved."

#### AC-NOTE-008 — تعديل ملاحظة معطَّلة / update of a deactivated note
  Traces : REQ-NOTE-005
  Given  : ملاحظة معطَّلة يملكها المستخدم «أ»
  When   : يُرسل «أ» عنوانًا مُنقّحًا لها
  Then   : يُرفض التعديل وتظهر رسالة RULE-NOTE-006 — ar: «لا يمكن تعديل ملاحظة معطَّلة.» · en: "A deactivated note cannot be edited."

### REQ-NOTE-006 — رفض أي عملية لغير المالك / Refuse any operation for a non-owner
  Pattern    : unwanted
  Statement  : If a user requests a read, update or deactivation of a note they do not own, then the system shall refuse the operation and report the note as not found.
  بالعربية   : إذا طلب مستخدم قراءة ملاحظة لا يملكها أو تعديلها أو تعطيلها، فيرفض النظام العملية ويُبلّغ بأن الملاحظة غير موجودة.
  Traces     : US-NOTE-002, US-NOTE-004
  Entities   : ENT-NOTE-001
  Rationale  : الملكية حدّ قراءة وكتابة معًا (POL-NOTE-001, POL-NOTE-002)؛ و"غير موجودة" لا تكشف وجود ملاحظة لغيره (ADR-NOTE-003)
  Source     : US-NOTE-002; US-NOTE-004; POL-NOTE-001; POL-NOTE-002; ADR-NOTE-003
  Priority   : HIGH

#### AC-NOTE-009 — تعديل من غير المالك / update by a non-owner
  Traces : REQ-NOTE-006
  Given  : ملاحظة يملكها المستخدم «ب»، والمستخدم «أ» ممنوح شاشة الملاحظات وإجراء UPDATE
  When   : يطلب «أ» تعديل تلك الملاحظة بمعرّفها
  Then   : تُرفض العملية وتظهر رسالة RULE-NOTE-005 — ar: «الملاحظة غير موجودة.» · en: "The note was not found." ولا يتغيّر أي حقل فيها

#### AC-NOTE-010 — قراءة من غير المالك / read by a non-owner
  Traces : REQ-NOTE-006
  Given  : ملاحظة يملكها المستخدم «ب»
  When   : يطلب المستخدم «أ» قراءتها بمعرّفها مباشرة
  Then   : تُرفض القراءة بالرسالة نفسها — ar: «الملاحظة غير موجودة.» · en: "The note was not found." ولا يُفصح الردّ عن أي من محتواها

### REQ-NOTE-007 — تعطيل ملاحظة مملوكة / Deactivate an owned note
  Pattern    : event
  Statement  : When a note's owner deactivates a note they own, the system shall mark the note inactive.
  بالعربية   : عند تعطيل مالك الملاحظة ملاحظةً يملكها، يجعلها النظام غير فعّالة.
  Traces     : US-NOTE-003
  Entities   : ENT-NOTE-001
  Rationale  : العملية الرابعة في نطاق الوحدة، واسمها "تعطيل" لا "حذف" (POL-NOTE-003)
  Source     : US-NOTE-003; POL-NOTE-003
  Priority   : HIGH

#### AC-NOTE-011 — المسار السعيد للتعطيل / deactivate happy path
  Traces : REQ-NOTE-007
  Given  : ملاحظة فعّالة يملكها المستخدم «أ»
  When   : يُعطّلها «أ»
  Then   : تصير غير فعّالة، وتختفي من بحثه الافتراضي، وتظهر رسالة — ar: «تم تعطيل الملاحظة.» · en: "The note has been deactivated."

#### AC-NOTE-012 — تعطيل ملاحظة معطَّلة / deactivating an already deactivated note
  Traces : REQ-NOTE-007
  Given  : ملاحظة معطَّلة يملكها المستخدم «أ»
  When   : يطلب «أ» تعطيلها ثانية
  Then   : يُرفض الطلب وتظهر رسالة RULE-NOTE-007 — ar: «الملاحظة معطَّلة أصلًا.» · en: "The note is already deactivated."

### REQ-NOTE-008 — لا محو نهائي لأي ملاحظة / No permanent removal of a note
  Pattern    : ubiquitous
  Statement  : The system shall retain a deactivated note's stored content and shall expose no operation that permanently removes a note record.
  بالعربية   : يُبقي النظام محتوى الملاحظة المعطَّلة محفوظًا ولا يُتيح أي عملية تمحو صفّ الملاحظة نهائيًا.
  Traces     : US-NOTE-003
  Entities   : ENT-NOTE-001
  Rationale  : التعطيل تنحيةٌ لا محو — بغير هذا القيد يفقد التعطيل معناه ويسقط أثر التدقيق
  Source     : US-NOTE-003; POL-NOTE-003; [KB:erp-domain-standards §6]
  Priority   : HIGH

#### AC-NOTE-013 — المحتوى باقٍ بعد التعطيل / content survives deactivation
  Traces : REQ-NOTE-008
  Given  : ملاحظة عُطِّلت قبل قليل ويملكها المستخدم «أ»
  When   : يفتحها «أ» من مسار الحالة المعطَّلة
  Then   : يُعرض عنوانها ونصّها كما كانا قبل التعطيل، ولا تُتاح في الشاشة أي عملية محو نهائي

### REQ-NOTE-009 — البحث محصور بملاحظات الطالب / Search is confined to the requester's notes
  Pattern    : event
  Statement  : When a user searches notes, the system shall return only notes whose owner is that user.
  بالعربية   : عند بحث المستخدم في الملاحظات، يُعيد النظام ملاحظاته هو دون سواها.
  Traces     : US-NOTE-004
  Entities   : ENT-NOTE-001
  Rationale  : الملكية هي الحدّ الوحيد للرؤية في هذه النسخة (POL-NOTE-001)
  Source     : US-NOTE-004; POL-NOTE-001
  Priority   : HIGH

#### AC-NOTE-014 — ملاحظات الآخرين لا تظهر / other users' notes never appear
  Traces : REQ-NOTE-009
  Given  : المستخدم «أ» يملك ملاحظتين والمستخدم «ب» يملك ثلاثًا
  When   : يبحث «أ» بلا أي مُرشِّح
  Then   : تُعاد ملاحظتا «أ» وحدهما، ولا ملاحظة من ملاحظات «ب» في النتيجة ولا في عدّادها

### REQ-NOTE-010 — الفعّالة وحدها في البحث الافتراضي / Active notes only by default
  Pattern    : state
  Statement  : While a search request carries no state filter, the system shall return only the requester's active notes.
  بالعربية   : أثناء خلوّ طلب البحث من مُرشِّح حالة، يُعيد النظام ملاحظات الطالب الفعّالة وحدها.
  Traces     : US-NOTE-004
  Entities   : ENT-NOTE-001
  Rationale  : POL-NOTE-004 — التعطيل يجب أن يُحدث أثرًا ملموسًا في القائمة
  Source     : US-NOTE-004; POL-NOTE-004
  Priority   : HIGH

#### AC-NOTE-015 — المعطَّلة خارج القائمة الافتراضية / deactivated notes are out of the default list
  Traces : REQ-NOTE-010
  Given  : المستخدم «أ» يملك ملاحظتين فعّالتين وواحدة معطَّلة
  When   : يفتح قائمته دون تحديد حالة
  Then   : تُعاد الفعّالتان فقط، والمعطَّلة غائبة عن النتيجة

### REQ-NOTE-011 — التصفية النصية / Text filtering
  Pattern    : optional
  Statement  : Where the requester supplies a text filter, the system shall return only those of their notes whose title or body contains the supplied text.
  بالعربية   : حيثما قدّم الطالب مُرشِّحًا نصيًّا، يُعيد النظام من ملاحظاته ما يحتوي عنوانه أو نصّه ذلك النص.
  Traces     : US-NOTE-004
  Entities   : ENT-NOTE-001
  Rationale  : البحث ضمن ملاحظات المستخدم نفسه هو العملية الرابعة في نطاق الوحدة
  Source     : US-NOTE-004; [KB:erp-domain-standards §6 search]
  Priority   : HIGH

#### AC-NOTE-016 — التطابق في العنوان / match in the title
  Traces : REQ-NOTE-011
  Given  : المستخدم «أ» يملك ملاحظة عنوانها "اجتماع الاثنين" وأخرى عنوانها "قائمة الشراء"
  When   : يبحث بالنص "اجتماع"
  Then   : تُعاد ملاحظة "اجتماع الاثنين" وحدها

#### AC-NOTE-017 — التطابق في النص / match in the body
  Traces : REQ-NOTE-011
  Given  : المستخدم «أ» يملك ملاحظة نصّها يحتوي كلمة "الميزانية" وعنوانها لا يحتويها
  When   : يبحث بالنص "الميزانية"
  Then   : تُعاد تلك الملاحظة

### REQ-NOTE-012 — ترقيم صفحات النتائج / Server-side paging of results
  Pattern    : ubiquitous
  Statement  : The system shall return note search results in server-side pages of 20 records by default and 200 at most.
  بالعربية   : يُعيد النظام نتائج بحث الملاحظات مُقسَّمة على الخادم بحجم صفحة 20 افتراضًا و200 حدًّا أقصى.
  Traces     : US-NOTE-004
  Entities   : ENT-NOTE-001
  Rationale  : DEFAULT منصّي للبحث؛ بغير حدّ أعلى يصير الطلب الواحد قادرًا على سحب القائمة كلها
  Source     : US-NOTE-004; DEFAULT [KB:erp-domain-standards §6 paging]
  Priority   : MEDIUM

#### AC-NOTE-018 — حجم الصفحة الافتراضي والحدّ الأقصى / default and maximum page size
  Traces : REQ-NOTE-012
  Given  : المستخدم «أ» يملك 45 ملاحظة فعّالة
  When   : يبحث دون تحديد حجم صفحة، ثم يبحث طالبًا حجم صفحة 500
  Then   : يُعاد في الأولى 20 سجلًا مع العدد الكلي 45، وفي الثانية 200 سجلًا كحدّ أقصى لا أكثر

### REQ-NOTE-013 — مسار مقصود للملاحظات المعطَّلة / A deliberate path to deactivated notes
  Pattern    : optional
  Statement  : Where the requester explicitly asks for the deactivated state, the system shall return only that requester's inactive notes.
  بالعربية   : حيثما طلب الطالب الحالة المعطَّلة صراحةً، يُعيد النظام ملاحظاته غير الفعّالة وحدها.
  Traces     : US-NOTE-005
  Entities   : ENT-NOTE-001
  Rationale  : كلمة "الافتراضي" في POL-NOTE-004 لا معنى لها بغير مسار غير افتراضي
  Source     : US-NOTE-005; POL-NOTE-004; prd RESOLVED DECISION #2
  Priority   : MEDIUM

#### AC-NOTE-019 — قائمة المعطَّلة / the deactivated list
  Traces : REQ-NOTE-013
  Given  : المستخدم «أ» يملك ملاحظتين فعّالتين وواحدة معطَّلة، وللمستخدم «ب» ملاحظة معطَّلة
  When   : يطلب «أ» الحالة المعطَّلة صراحةً
  Then   : تُعاد ملاحظته المعطَّلة وحدها — لا الفعّالتان ولا ملاحظة «ب»

### REQ-NOTE-014 — فتح ملاحظة معطَّلة للقراءة / Open a deactivated note read-only
  Pattern    : event
  Statement  : When a note's owner opens a deactivated note they own, the system shall display its stored content in read-only form.
  بالعربية   : عند فتح مالك الملاحظة ملاحظةً معطَّلة يملكها، يعرض النظام محتواها المحفوظ للقراءة فقط.
  Traces     : US-NOTE-005
  Entities   : ENT-NOTE-001
  Rationale  : التعطيل تنحيةٌ لا محو؛ والقراءة دون تعديل تُبقي القرار مفهومًا ولا تفتح عملية خامسة
  Source     : US-NOTE-005; POL-NOTE-003; POL-NOTE-002
  Priority   : MEDIUM

#### AC-NOTE-020 — العرض للقراءة فقط / read-only display
  Traces : REQ-NOTE-014
  Given  : ملاحظة معطَّلة يملكها المستخدم «أ»
  When   : يفتحها «أ» من قائمة المعطَّلة
  Then   : يُعرض عنوانها ونصّها، وتكون حقول الإدخال غير قابلة للتحرير، ولا يُتاح إجراء حفظ

### REQ-NOTE-015 — شاشة مركّبة واحدة بمجموعة صلاحيات واحدة / One composite screen under one permission set
  Pattern    : ubiquitous
  Statement  : The system shall expose all four note operations through one composite screen governed by the single page code `NOTE_NOTES`.
  بالعربية   : يُتيح النظام عمليات الملاحظة الأربع كلَّها عبر شاشة مركّبة واحدة يحكمها رمز الصفحة الواحد `NOTE_NOTES`.
  Traces     : US-NOTE-006
  Entities   : ENT-NOTE-001
  Rationale  : أي مجموعة صلاحيات ثانية تعني شاشة ثانية — أي نموًّا في النطاق (POL-NOTE-006)
  Source     : US-NOTE-006; POL-NOTE-006; [KB:erp-domain-standards §4]
  Priority   : HIGH

#### AC-NOTE-021 — العمليات الأربع خلف رمز صفحة واحد / four operations behind one page code
  Traces : REQ-NOTE-015
  Given  : مستخدم ممنوح شاشة الملاحظات بإجراءاتها الأربعة
  When   : ينتقل بين القائمة ونموذج الإنشاء/التعديل ويُنفّذ العمليات الأربع
  Then   : تُفحص كلها على رمز الصفحة `NOTE_NOTES` وحده، ولا يوجد رمز صفحة ثانٍ للوحدة

### REQ-NOTE-016 — بوابة الوحدة قبل كل شيء / The module gate comes first
  Pattern    : unwanted
  Statement  : If the requester's roles do not hold the NOTE module grant, then the system shall omit the Notes screen from the menu and refuse direct access to it.
  بالعربية   : إذا لم تحمل أدوار الطالب منح وحدة NOTE، فيُسقط النظام شاشة الملاحظات من القائمة ويرفض الوصول المباشر إليها.
  Traces     : US-NOTE-006, US-NOTE-007
  Entities   : ENT-NOTE-001
  Rationale  : بوابة الوحدة تُفحص أولاً وغيابها غياب تام (domain-profile G3)
  Source     : US-NOTE-006; US-NOTE-007; POL-NOTE-006; domain-profile G3
  Priority   : HIGH

#### AC-NOTE-022 — غياب تام بلا منح الوحدة / total absence without the module grant
  Traces : REQ-NOTE-016
  Given  : مستخدم مُصادَق عليه لا تحمل أدواره منح وحدة NOTE
  When   : يفتح القائمة ثم يقصد رابط شاشة الملاحظات مباشرة
  Then   : لا تظهر الوحدة ولا شاشتها في القائمة، ويُرفض الوصول المباشر برسالة — ar: «لا تملك صلاحية الوصول إلى هذه الشاشة.» · en: "You are not authorised to access this screen."

### REQ-NOTE-017 — التسجيل الذاتي في سجلات SEC / Self-registration in the SEC registries
  Pattern    : ubiquitous
  Statement  : The system shall register the NOTE module, its single screen and its four actions as rows of the platform module, screen and action registries.
  بالعربية   : يُسجّل النظام وحدة NOTE وشاشتها الوحيدة وإجراءاتها الأربعة كصفوف في سجلات الوحدات والشاشات والإجراءات في المنصة.
  Traces     : US-NOTE-007
  Entities   : ENT-NOTE-001
  Rationale  : بغير هذه الصفوف تسقط بوابة الوحدة فلا يصل إليها مَن مُنحت له
  Source     : US-NOTE-007; POL-NOTE-006; module-registry-note.md SHARED ENTITIES CONSUMED; domain-profile G2/G3
  Priority   : HIGH

#### AC-NOTE-023 — صفوف التسجيل موجودة / the registration rows exist
  Traces : REQ-NOTE-017
  Given  : منصّة مُهيّأة تحتوي سجلات الوحدات والشاشات والإجراءات (ENT-SEC-004, ENT-SEC-005, ENT-SEC-006)
  When   : تُنشر وحدة NOTE
  Then   : يوجد صف وحدة واحد بالرمز `NOTE`، وصف شاشة واحد بالرمز `NOTE_NOTES`، وأربعة صفوف إجراءات (VIEW · CREATE · UPDATE · DELETE) على تلك الشاشة

### REQ-NOTE-018 — التفويض عبر الطبقة المنصّية / Authorisation through the platform layer
  Pattern    : ubiquitous
  Statement  : The system shall evaluate every note operation against the platform authorisation layer using the screen's page code and the action the operation carries.
  بالعربية   : يفحص النظام كل عملية على الملاحظات عبر طبقة التفويض المنصّية برمز صفحة الشاشة وإجراء العملية.
  Traces     : US-NOTE-006
  Entities   : ENT-NOTE-001
  Rationale  : لا منطق تفويض مكتوب داخل الوحدة (domain-profile G2)؛ VIEW بوابة لا يُغني عنها إجراء آخر
  Source     : US-NOTE-006; POL-NOTE-006; profiles/erp.yaml conventions.security_model
  Priority   : HIGH

#### AC-NOTE-024 — إجراء غير ممنوح يُرفض / an ungranted action is refused
  Traces : REQ-NOTE-018
  Given  : مستخدم يحمل منح الوحدة ومنح الشاشة وإجراء VIEW وحده
  When   : يحاول إنشاء ملاحظة
  Then   : تُرفض العملية برسالة — ar: «لا تملك صلاحية تنفيذ هذا الإجراء.» · en: "You are not authorised to perform this action." وتبقى القراءة متاحة له

## A5 — Business rules

### RULE-NOTE-001 — عنوان الملاحظة إلزامي / A note title is required
  Scope      : ENT-NOTE-001
  Trigger    : on create / on update
  Statement  : The system shall prevent saving a note when its title is missing or blank.
  Message    : ar: «عنوان الملاحظة مطلوب.» · en: "A note title is required."
  Traces     : REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005
  Data source: ENT-NOTE-001.noteTitle
  Source     : POL-NOTE-005; US-NOTE-001
  Test-Hint  : العنوان المكوَّن من مسافات فقط يُعامَل كفارغ

### RULE-NOTE-002 — نصّ الملاحظة إلزامي / A note body is required
  Scope      : ENT-NOTE-001
  Trigger    : on create / on update
  Statement  : The system shall prevent saving a note when its body is missing or blank.
  Message    : ar: «نصّ الملاحظة مطلوب.» · en: "A note body is required."
  Traces     : REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005
  Data source: ENT-NOTE-001.noteBody
  Source     : POL-NOTE-005; US-NOTE-001

### RULE-NOTE-003 — حدود طول العنوان والنص / Title and body length limits
  Scope      : ENT-NOTE-001
  Trigger    : on create / on update
  Statement  : The system shall prevent saving a note when its title exceeds 200 characters or its body exceeds 4000 characters.
  Message    : ar: «العنوان لا يتجاوز 200 حرف والنصّ لا يتجاوز 4000 حرف.» · en: "A title may not exceed 200 characters and a body may not exceed 4000 characters."
  Traces     : REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005
  Data source: ENT-NOTE-001.noteTitle, ENT-NOTE-001.noteBody
  Source     : ADR-NOTE-002 (الملاحظة "قصيرة" بنصّ US-NOTE-001، ولا مدخل يُسمّي رقمًا)

### RULE-NOTE-004 — الملكية لا تتغيّر بعد الإنشاء / Ownership is immutable after creation
  Scope      : ENT-NOTE-001
  Trigger    : on update
  Statement  : The system shall prevent any change to a note's owner after the note is created.
  Message    : ar: «لا يمكن تغيير مالك الملاحظة.» · en: "A note's owner cannot be changed."
  Traces     : REQ-NOTE-002
  Data source: ENT-NOTE-001.ownerUserRef
  Source     : POL-NOTE-001; US-NOTE-001

### RULE-NOTE-005 — لا عملية على ملاحظة لا يملكها الطالب / No operation on a note the requester does not own
  Scope      : ENT-NOTE-001
  Trigger    : on read / on update / on deactivate / on search
  Statement  : The system shall prevent any read, update or deactivation of a note whose owner differs from the authenticated requester.
  Message    : ar: «الملاحظة غير موجودة.» · en: "The note was not found."
  Traces     : REQ-NOTE-006, REQ-NOTE-009, REQ-NOTE-013
  Data source: ENT-NOTE-001.ownerUserRef
  Source     : POL-NOTE-001; POL-NOTE-002; ADR-NOTE-003
  Test-Hint  : الرسالة لا تُفرّق بين معرّف غير موجود ومعرّف يملكه غيره

### RULE-NOTE-006 — لا تعديل لملاحظة معطَّلة / No editing of a deactivated note
  Scope      : ENT-NOTE-001
  Trigger    : on update
  Statement  : The system shall prevent updating a note while the note is inactive.
  Message    : ar: «لا يمكن تعديل ملاحظة معطَّلة.» · en: "A deactivated note cannot be edited."
  Traces     : REQ-NOTE-005, REQ-NOTE-014
  Data source: ENT-NOTE-001.isActiveFl
  Source     : POL-NOTE-003; US-NOTE-005

### RULE-NOTE-007 — لا تعطيل مكرَّر / No repeated deactivation
  Scope      : ENT-NOTE-001
  Trigger    : on deactivate
  Statement  : The system shall prevent deactivating a note that is already inactive.
  Message    : ar: «الملاحظة معطَّلة أصلًا.» · en: "The note is already deactivated."
  Traces     : REQ-NOTE-007
  Data source: ENT-NOTE-001.isActiveFl
  Source     : POL-NOTE-003; [KB:erp-domain-standards §6]

**ARCH-5** — لا ينطبق: ENT-NOTE-001 كيان PRIVATE لا يقرأه مستهلك خارجي، فلا أثر لتعطيله خارج الوحدة.

## A6 — Lookups

لا تملك الوحدة أي مفتاح قائمة قيم ولا تستهلك أيًّا منه في هذه النسخة: علم النشاط `isActiveFl`
قيمة منطقية باصطلاح المنصة لا نوع lookup، وحقلا العنوان والنص نصّان حرّان بلغة كاتبهما
(POL-NOTE-005)، ومُرشِّح الحالة في البحث وجهان لعلم منطقي لا قائمة قيم.
No lookup key is owned or consumed by NOTE in v1; the profile rule "all LOV values are
runtime-loaded from the lookup module" is satisfied vacuously — there is no value list.

## A7 — Status lifecycle

لا ينطبق / not applicable — للملاحظة حالتان فقط (فعّالة / معطَّلة) وانتقال واحد لا رجعة فيه
في هذه النسخة، وهو أقل من عتبة الثلاث حالات التي تستوجب مخطّطًا (§6):

```
فعّالة (isActiveFl = true)  ──(تعطيل / deactivate — RULE-NOTE-007)──▶  معطَّلة (isActiveFl = false)
```
لا انتقال عكسي: إعادة التفعيل خارج النطاق (A2) — لا قصة معتمدة تطلبها.

## A8 — Module dependencies

| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate (assigned by P2) |
|---|---|---|---|---|
| ModuleRegistry | ENT-SEC-004 | SEC | SOFT-READ (تسجيل كبيانات / registration as data) | لا شيء — سابقة ADR-FIN-001: التسجيل الذاتي ليس صف XM ولا مفتاحًا أجنبيًا |
| ScreenRegistry | ENT-SEC-005 | SEC | SOFT-READ | لا شيء — نفس السابقة |
| ActionRegistry | ENT-SEC-006 | SEC | SOFT-READ | لا شيء — نفس السابقة |
| User (الهوية كسلسلة أصل / identity as a principal string) | ENT-SEC-001 | SEC | SOFT-READ (بلا مفتاح أجنبي) | لا شيء — `ownerUserRef` وحقول التدقيق تحمل المعرّف الذي يسلّمه المعترِض القياسي |

| External service | Purpose | Integration kind |
|---|---|---|
| — | لا خدمة خارجية: لا إشعارات ولا خدمة ملفات ولا أي قائمة قيم من MDL | — |

يُتوقَّع أن تكون مرحلتا INT-C وINT-R في خطة التنفيذ **فارغتين لكن موجودتين**، لا محذوفتين
(module-registry-note.md DEPENDENCIES).

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-NOTE-001 — شاشة الملاحظات / Notes

### B1 — Definition
  Purpose      : أن يدوّن المستخدم ملاحظاته ويُنقّحها ويُعطّلها ويبحث فيها من موضع واحد
  Entities     : ENT-NOTE-001
  Operations   : search · list · create · read · update · deactivate
  Users        : مستخدم شاشة الملاحظات (الممنوح مجموعة صلاحيات الشاشة) — وهو مالك ما يكتب
  Navigation   : الملاحظات / Notes → الملاحظات / Notes → شاشة الملاحظات / Notes ; from: القائمة الرئيسية / main menu ; to: — (لا شاشة ثانية في الوحدة)
  Content shape: flat record (قائمة + نموذج سجل مسطّح) — تلميح لا تصميم
  Traces       : REQ-NOTE-001, REQ-NOTE-002, REQ-NOTE-003, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-006, REQ-NOTE-007, REQ-NOTE-008, REQ-NOTE-009, REQ-NOTE-010, REQ-NOTE-011, REQ-NOTE-012, REQ-NOTE-013, REQ-NOTE-014, REQ-NOTE-015, REQ-NOTE-016, REQ-NOTE-018
  Composite    : بحث + إدخال = متطلَّب شاشة واحد (profile.conventions.composite_screen)

### B2 — Search / list
| Filter | Field (ENT) | Result column | Notes |
|---|---|---|---|
| نص البحث / Text | ENT-NOTE-001.noteTitle, ENT-NOTE-001.noteBody | العنوان / Title · مقتطف النص / Body excerpt | يطبّق REQ-NOTE-011 |
| الحالة / State | ENT-NOTE-001.isActiveFl | الحالة / State | الافتراضي «الفعّالة» (REQ-NOTE-010)؛ الخيار الصريح «المعطَّلة» (REQ-NOTE-013) — علم منطقي لا مفتاح قائمة قيم |
| — | ENT-NOTE-001.updatedAt, ENT-NOTE-001.createdAt | آخر تحديث / Last updated | الترتيب الافتراضي بالأحدث |
Applies: RULE-NOTE-005. Paging per REQ-NOTE-012.
المالك ليس مُرشِّحًا معروضًا: البحث محصور بالطالب دائمًا (REQ-NOTE-009).

### B3 — Input
| Field (ENT) | Editable | Notes |
|---|---|---|
| ENT-NOTE-001.noteTitle | yes | applies RULE-NOTE-001, RULE-NOTE-003 |
| ENT-NOTE-001.noteBody | yes | applies RULE-NOTE-002, RULE-NOTE-003 |
| ENT-NOTE-001.ownerUserRef | no | يملؤه النظام — applies RULE-NOTE-004 |
| ENT-NOTE-001.isActiveFl | no | يتغيّر بإجراء التعطيل وحده |
| ENT-NOTE-001.createdBy, ENT-NOTE-001.createdAt, ENT-NOTE-001.updatedBy, ENT-NOTE-001.updatedAt | no | حقول تدقيق يملؤها النظام |

| Action (ar / en) | Operation | REQ | RULEs |
|---|---|---|---|
| حفظ / Save (جديدة) | create | REQ-NOTE-001, REQ-NOTE-002, REQ-NOTE-003, REQ-NOTE-004 | RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003 |
| حفظ التعديل / Save changes | update | REQ-NOTE-005, REQ-NOTE-006 | RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003, RULE-NOTE-004, RULE-NOTE-005, RULE-NOTE-006 |
| تعطيل / Deactivate | deactivate | REQ-NOTE-007, REQ-NOTE-008 | RULE-NOTE-005, RULE-NOTE-007 |
| فتح / Open | read | REQ-NOTE-006, REQ-NOTE-014 | RULE-NOTE-005 |
الملاحظة المعطَّلة تُفتح للقراءة فقط (REQ-NOTE-014)، ولا إجراء محو نهائي في الشاشة (REQ-NOTE-008).

### B4 — Access
| Page code | Action | Roles |
|---|---|---|
| NOTE_NOTES | VIEW (بوابة / gateway) | مستخدم شاشة الملاحظات / Notes-screen user |
| NOTE_NOTES | CREATE | مستخدم شاشة الملاحظات / Notes-screen user |
| NOTE_NOTES | UPDATE | مستخدم شاشة الملاحظات / Notes-screen user |
| NOTE_NOTES | DELETE (تعطيل ناعم / soft deactivate) | مستخدم شاشة الملاحظات / Notes-screen user |
صف واحد في SEC_PAGES ومجموعة صلاحيات واحدة (REQ-NOTE-015, POL-NOTE-006). أسماء الصلاحيات
تشتقّها وحدة الأمان من رمز الصفحة ولا تُعدَّد هنا. الملكية قيد بيانات فوق التفويض، لا بديل عنه:
منح UPDATE لا يُتيح تعديل ملاحظة الغير (RULE-NOTE-005).

### B5 — API expectations
Base path : `/api/v1/note/notes` — Response `ApiResponse<T>` · Paging `Page<T>` ·
Errors `LocalizedException → {code, messageAr, messageEn}`

| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| create note | POST | `/api/v1/note/notes` | noteTitle, noteBody | the created note | RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003 | REQ-NOTE-001, REQ-NOTE-002, REQ-NOTE-003, REQ-NOTE-004 |
| search notes | GET | `/api/v1/note/notes` | text filter, state filter, paging | page of notes | RULE-NOTE-005 | REQ-NOTE-009, REQ-NOTE-010, REQ-NOTE-011, REQ-NOTE-012, REQ-NOTE-013 |
| read note | GET | `/api/v1/note/notes/{id}` | id | the note | RULE-NOTE-005 | REQ-NOTE-006, REQ-NOTE-014 |
| update note | PUT | `/api/v1/note/notes/{id}` | id, noteTitle, noteBody | the updated note | RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003, RULE-NOTE-004, RULE-NOTE-005, RULE-NOTE-006 | REQ-NOTE-005, REQ-NOTE-006 |
| deactivate note | DELETE | `/api/v1/note/notes/{id}` | id | confirmation | RULE-NOTE-005, RULE-NOTE-007 | REQ-NOTE-007, REQ-NOTE-008 |
لا قيمة قائمة مُرمَّزة في أي من هذه العمليات. المالك لا يُقبل مُدخلًا في أيٍّ منها (REQ-NOTE-002).

# STANDALONE

## Traceability matrix

| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-NOTE-001 | REQ-NOTE-001, REQ-NOTE-002, REQ-NOTE-003, REQ-NOTE-004 | AC-NOTE-001, AC-NOTE-002, AC-NOTE-003, AC-NOTE-004, AC-NOTE-005, AC-NOTE-006 | RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003, RULE-NOTE-004 | ENT-NOTE-001 | SCR-REQ-NOTE-001 |
| US-NOTE-002 | REQ-NOTE-005, REQ-NOTE-006 | AC-NOTE-007, AC-NOTE-008, AC-NOTE-009, AC-NOTE-010 | RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003, RULE-NOTE-005, RULE-NOTE-006 | ENT-NOTE-001 | SCR-REQ-NOTE-001 |
| US-NOTE-003 | REQ-NOTE-007, REQ-NOTE-008 | AC-NOTE-011, AC-NOTE-012, AC-NOTE-013 | RULE-NOTE-005, RULE-NOTE-007 | ENT-NOTE-001 | SCR-REQ-NOTE-001 |
| US-NOTE-004 | REQ-NOTE-009, REQ-NOTE-010, REQ-NOTE-011, REQ-NOTE-012 | AC-NOTE-014, AC-NOTE-015, AC-NOTE-016, AC-NOTE-017, AC-NOTE-018 | RULE-NOTE-005 | ENT-NOTE-001 | SCR-REQ-NOTE-001 |
| US-NOTE-005 | REQ-NOTE-013, REQ-NOTE-014 | AC-NOTE-019, AC-NOTE-020 | RULE-NOTE-005, RULE-NOTE-006 | ENT-NOTE-001 | SCR-REQ-NOTE-001 |
| US-NOTE-006 | REQ-NOTE-015, REQ-NOTE-016, REQ-NOTE-018 | AC-NOTE-021, AC-NOTE-022, AC-NOTE-024 | — | ENT-NOTE-001 | SCR-REQ-NOTE-001 |
| US-NOTE-007 | REQ-NOTE-016, REQ-NOTE-017 | AC-NOTE-022, AC-NOTE-023 | — | ENT-NOTE-001 | SCR-REQ-NOTE-001 |

كل قصة مغطّاة بمتطلَّب واحد على الأقل، وكل متطلَّب يتتبّع قصة واحدة على الأقل وله معيار قبول
واحد على الأقل، وكل قاعدة تتتبّع متطلَّبًا، ومتطلَّب الشاشة يتتبّع سبعة عشر متطلَّبًا. لا يتيم ولا
مرجع معلّق. (REQ-NOTE-017 لا تحكمه قاعدة عمل: التسجيل فعلٌ منصّي لا قيدُ بيانات داخل الوحدة.)

## Decisions applied

| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| ADR-NOTE-001 | ENT-NOTE-001 يبقى `master` بلا `nameAr`/`nameEn`/`code` — انحراف مُعلَن عن حقول النوع القياسية | POL-NOTE-005; module-registry-note.md AUTO; [KB:erp-domain-standards §2 rule 1] | ACCEPTED (non-breaking) — يُلغى بطلب صريح لمحتوى ثنائي اللغة |
| ADR-NOTE-002 | حدّا الطول: العنوان 200 حرف، النص 4000 حرف | US-NOTE-001 ("ملاحظة قصيرة")؛ ممارسة المجال | ACCEPTED (non-breaking) — يُغيَّر الرقمان بطلب العميل دون أثر على أي متطلَّب |
| ADR-NOTE-003 | طلب غير المالك يُردّ بـ«غير موجودة» لا بـ«ممنوع» | POL-NOTE-001; POL-NOTE-002 | ACCEPTED (non-breaking) — يُقلب إلى ردّ «ممنوع» إن طلب العميل تمييز الحالتين |
| DEFAULT | التعطيل ناعم عبر `isActiveFl`، ولا حذف نهائي | [KB:erp-domain-standards §6]; POL-NOTE-003 | Override: لا يُغيَّر إلا بقرار يُلغي POL-NOTE-003 |
| DEFAULT | ترقيم الصفحات على الخادم: 20 افتراضًا، 200 حدًّا أقصى | [KB:erp-domain-standards §6 paging] | Override: رقمان قابلان للضبط دون أثر على أي متطلَّب آخر |
| DEFAULT | البحث النصي على العنوان والنص معًا | [KB:erp-domain-standards §6 search] | Override: حصره بالعنوان وحده إن طلب العميل |
| DEFAULT | التواريخ تُخزَّن UTC وتُعرض بتوقيت المستأجر | [KB:erp-domain-standards §6 dates] | Override: قرار منصّي لا قرار وحدة |

## Access summary

| Page code | Screen (ar / en) | Actions | Roles |
|---|---|---|---|
| NOTE_NOTES | شاشة الملاحظات / Notes | VIEW (بوابة) · CREATE · UPDATE · DELETE | مستخدم شاشة الملاحظات / Notes-screen user |
صف واحد في SEC_PAGES، ومجموعة صلاحيات واحدة، ولا دور ثانٍ في هذه النسخة: لا اطّلاع إداري شامل
(POL-NOTE-001، business-policies SCOPE EXCEPTIONS). المصدر هو B4.
══════════════════════════════════════════════════════════════════
