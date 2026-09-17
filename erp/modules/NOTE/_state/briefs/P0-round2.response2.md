## Round 2 — final

Four of round 1's five proposals accepted; **one amended**. Files written directly to `erp/modules/NOTE/P0/`; the full round-2 record (with the three files reproduced) is in `erp/modules/NOTE/_state/briefs/P0-round2.response2.md`.

**PROPOSAL 2 — amended.** Round 1 wrote `DEPENDENCIES: None. ROOT: YES` and `SHARED ENTITIES CONSUMED: None`. That contradicts ground truth this stage must read: `project-registry.md` SHARED ENTITY DECLARATIONS says of SEC's Module/Screen/ActionRegistry "every future module registers one row of itself here", G3 makes an unregistered module's screen absent from the menu *and* from direct URL access, and both completed P0 registries declared a SEC row (MDL `SOFT`, FIN `HARD`). Round 1 made NOTE the only module in the platform claiming ROOT: YES.

Two claims had been conflated. Separated now:
- **kept** — no XM row, no foreign key (ADR-FIN-001 precedent), so INT-C/INT-R still come out empty-but-present;
- **fixed** — one `SEC | SOFT` dependency (self-registration + module gate), two SOFT-READ shared-entity rows, `ROOT: NO`, and no MDL dependency at all (NOTE owns and consumes no coded value list, so G4 has nothing to bite on).

`SOFT` over `HARD` follows MDL's precedent: the need is an application-level registration check, not referential integrity. Tier and number are untouched — a SOFT-READ dependency on a Tier-0 module does not change tiering, so NOTE stays L1 / 1.4. The vision's "zero cross-module dependencies" is restated throughout as **zero domain-data dependency**, which is preserved literally; visibility to the platform's one security system was never a dependency the module could decline.

Accepted as-is: `productivity` as a new bounded context (with its profile/registry consequence now recorded inside the summary as decision #6, not just in dialogue prose); entity kind `master`; bilingual exemption for note title/body fixed as POL-NOTE-005; no administrator override. Policies POL-NOTE-001…006 are unchanged in text and numbering — the amendment is structural only.

**Verification:** `gov.py analyze -m NOTE -v 1 --scope all` → no C3 finding (C3.1–C3.7 all pass, each examined something). `gov.py lint` → 0 critical · 0 major · 0 minor. Remaining findings are downstream stages not yet run, plus the pre-existing C2.2 CAT-10 gap in `project-registry.md` — the orchestrator's artifact, a genuine finding for the smoke run.

Two items fall outside this brief's three files and were not edited: one line in `profiles/erp.yaml → vocabulary.bounded_contexts`, and a qualifying clause in `erp-domain-standards.md §2 rule 1` (the KB states the bilingual rule as unconditional on `master`, so every master entity holding user-authored content will hit this same friction).

<!-- CONVERGED -->
` dependency (self-registration + module gate)
plus the two SOFT-READ shared-entity rows, `ROOT: NO`, and **no MDL dependency at all** (NOTE owns
and consumes no coded value list, so G4 has nothing to bite on). Tier and number are untouched —
MDL's own P0 already established that a SOFT-READ dependency on a Tier-0 module does not change
tiering, so NOTE stays L1 / 1.4 (number stability holds).
The vision's "zero cross-module dependencies" is preserved in its real sense and restated in the
artifacts as **zero domain-data dependency**: no XM, no FK, no MDL lookup, no foreign entity, no
external reader of a note. Being visible to the platform's one security system is not a dependency
the module could have declined.
`SEC | SOFT` (not HARD) is chosen on MDL's precedent — the need is an application-level
registration/existence check, not referential integrity; FIN wrote HARD at P0 but P2 reclassified
it, and the outcome is the precedent worth following, not the first wording.

**PROPOSAL 3 — entity kind `master`: ACCEPT (option A).**
Of the five kinds the profile permits, `master` is the only defensible one: [KB §2] defines
transactional as period-bound (`fiscalYearId`, `periodId`) *and* status-driven from a lookup, and a
note is neither; `transactional` would drag in fiscal fields and an MDL status lookup — a new
dependency and scope growth on a module budgeted at one entity. The `IF WRONG` line already spells
that consequence out, which is what keeps P1 from reclassifying quietly.

**PROPOSAL 4 — bilingual rule does not reach note title/body: ACCEPT (option B).**
G11 and [KB §2 rule 1] govern *named* platform artifacts — things a second person must read.
A personal note has one reader, its author. Fixing it as POL-NOTE-005 (rather than leaving it
implicit) is what stops P1 from re-applying `nameAr`/`nameEn` by reflex. Bilingualism stays fully in
force on the module, entity and screen names, and on the policy statements themselves.
Round 1's side observation stands and is worth carrying out of this stage: [KB §2 rule 1] states the
bilingual rule as unconditional on `master`, so *any* master entity holding user-authored content
meets this same friction — a qualifying clause in `erp-domain-standards.md §2 rule 1` would remove
the need for a per-module deviation. That is a knowledge-base edit, outside this brief's three files.

**PROPOSAL 5 — no administrator override: ACCEPT (option A).**
The vision says "own notes only" with no exception; an admin-wide view needs a second permission set,
which contradicts "one permission set on that screen". Recorded as a scope exception with an explicit
activation trigger rather than silently omitted, so a later version can switch it on deliberately.

## What changed in the files this round

- `platform-summary.md` — MODULES row 1.4 `Depends on` → `SEC (SOFT …)`; DEPENDENCY MAP's two NOTE
  lines rewritten (SOFT → SEC; zero domain-data dependency elsewhere); RESOLVED DECISION #3 rewritten
  as the amended answer; RESOLVED DECISION #6 added for the profile/registry consequence.
- `module-registry-note.md` — SHARED ENTITIES CONSUMED now has two SOFT-READ rows; DEPENDENCIES has
  `SEC | SOFT` and an explicit "MDL — nothing" row; `ROOT: NO` with the tiering rationale; a new
  AUTO-DECISION justifying SOFT over HARD with its `IF WRONG`; SCOPE line and RESOLVED DECISION #2
  restated as *domain-data* dependency.
- `business-policies-note.md` — the cross-module SCOPE EXCEPTION restated (SEC registration explicitly
  carved out as a platform invariant, not a module choice); RESOLVED DECISION #4 amended to match.
- Policies are untouched: POL-NOTE-001 … POL-NOTE-006, unchanged text, unchanged numbering — the
  amendment is structural, and no policy the user did not state was added (the module gate is a
  platform standard applied by later stages, not a client policy).

## Files (written directly; reproduced for the record)

<<<FILE: erp/modules/NOTE/P0/platform-summary.md>>>
# PLATFORM SUMMARY — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile : erp   Domain profile : v1   Registry : v1.3.0
══════════════════════════════════════════════════════════════════

## OVERVIEW
منصة ERP متعددة الوحدات، قائمة على مبدأ "كل ما يمكن أن يتغير = بيانات، لا شيفرة"، تُبنى
بـ Spring (خلفية) وReact (واجهة) على PostgreSQL. دفعة الوحدات الثلاث (SEC → MDL → FIN)
اكتملت بالكامل (pass-1 APPROVE لكل وحدة) [project-registry PIPELINE/PROGRESS STATUS].
هذه الجلسة تُضيف وحدة رابعة صغيرة ومستقلة تمامًا: **NOTE (الملاحظات / Notes)** — مستخدم
يكتب ملاحظة قصيرة ويقرأ ملاحظاته هو فقط. الوحدة مقصودة الصِّغَر: كيان واحد، أربع عمليات
(إنشاء · تعديل · تعطيل · بحث ضمن ملاحظات المستخدم نفسه)، شاشة واحدة، مجموعة صلاحيات
واحدة، وصفر اعتماديات بين الوحدات. حجمها هذا **قيد مُلزِم لكل مرحلة لاحقة**، لا نقطة
انطلاق قابلة للتوسيع.
The platform is a multi-module ERP built as data, not code. The three-module batch
(SEC → MDL → FIN) is complete; this run adds one small, fully self-contained module,
NOTE (Notes): a user writes a short note and reads their own notes back.

## MODULES
| #   | Code | Module (ar/en) | Bounded context | Layer | Type | Depends on | Status |
|-----|------|--------|-----------------|-------|------|------------|--------|
| 1.1 | ORG | الهيكل التنظيمي / Organization | organization | L1 | master data | ROOT | NEW (not this run) |
| 1.2 | SEC | الأمان / Security | organization | L1 | security engine | ROOT | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 1.3 | MDL | البيانات المرجعية / Master Data Lookup | organization | L1 | reference | SEC (SOFT-READ) | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 1.4 | NOTE | الملاحظات / Notes | productivity | L1 | master data | SEC (SOFT — تسجيل ذاتي وتفويض فقط / self-registration + authorization only) | NEW — this run |
| 2.1 | PRC | المشتريات / Procurement | supply | L3 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 2.2 | FIN | الحسابات العامة / Finance (GL) | finance | L3 | transactional/reporting | SEC (HARD), MDL (HARD) | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 2.3 | INV | المخزون / Inventory | supply | L3 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 3.1 | SLS | المبيعات / Sales | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 3.2 | CTR | العقود / Contracts | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 3.3 | HR | الموارد البشرية / Human Resources | people | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
Status: NEW (Phase 2 produces) · EXISTING (Phase 2 extends) · EXCEPTION (read as-is)
Numbering: [tier].[sequence within tier] — the user requests Phase 2 by this number.
أرقام 1.1–3.3 مُثبَّتة من دورات P0 السابقة ولم يتغير أي منها؛ NOTE أخذ الرقم التالي في
الطبقة الأولى (1.4) تطبيقًا لقاعدة ثبات الترقيم.
This run's Phase 2 request: **1.4 NOTE** (module convergence in module-registry-note.md).

## DEPENDENCY MAP
Build order: Tier 1 [ORG, SEC, MDL, NOTE] → Tier 2 [PRC, FIN, INV] → Tier 3 [SLS, CTR, HR] → Tier 4 (reporting, none yet)
Key dependencies (one line each):
  NOTE → SOFT → SEC : تسجيل الوحدة/الشاشة/الإجراء كبيانات + الهوية والتفويض عبر بوابة الوحدة (G2, G3) — قراءة ناعمة لا مفتاح أجنبي، ولا صف XM (سابقة ADR-FIN-001) / self-registration into SEC's Module/Screen/Action registries + identity & the module gate; SOFT-READ, no FK, no XM row
  NOTE → (none) → أي وحدة أخرى : صفر اعتمادية بيانات-مجال — لا lookup من MDL، ولا كيان أجنبي، ولا قارئ خارجي للملاحظة / zero domain-data dependency: no MDL lookup, no foreign entity, no external reader
  FIN → HARD → SEC : identity + grants + SoD (recorded in the completed batch, unchanged here)
  FIN → HARD → MDL : lookup-backed codes (recorded in the completed batch, unchanged here)
  (host business system) → EVENT → FIN : canonical accounting event only (unchanged here)

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
| ORG, PRC, HR, INV, SLS, CTR detailed analysis | out of the current scope; activate when a batch names them |
| Workflow engine | profile: `forbidden` |
| مشاركة الملاحظات بين المستخدمين / note sharing between users | خارج الرؤية صراحة: "reads their own notes back"؛ يُفعَّل فقط إذا طلب المستخدم مشاركة صريحة |
| تصنيف/وسوم/مرفقات الملاحظة / note categories, tags, attachments | ستجاوز حدّ "كيان واحد"؛ كل توسيع هنا مخالفة نطاق تُسجَّل كـ finding |
| ربط NOTE بأي وحدة أخرى (lookup أو FK) / any NOTE↔module link | الرؤية تنص على صفر اعتماديات؛ يُفعَّل بقرار صريح لاحق فقط |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | السياق المحدود لوحدة NOTE — لا ينتمي لأي سياق في الملف الشخصي / NOTE's bounded context | سياق جديد `productivity` يملك NOTE وحده، سطر واحد في `profiles/erp.yaml → vocabulary.bounded_contexts` | موصى به — ينتظر تأكيد المستخدم؛ الملف الشخصي نفسه يسمح: "a new module can join an existing context or start a new one" | profiles/erp.yaml vocabulary.bounded_contexts (تعليق); domain-profile §7.2 |
| 6 | أثر القرار 1 خارج هذه المرحلة / the registry consequence of decision 1 | سطر واحد `- {id: productivity, owns: [NOTE]}` في `profiles/erp.yaml → vocabulary.bounded_contexts`، وصفٌّ مقابل في CONVENTIONS & STEERING بـ`project-registry.md` — خطوة دمج يملكها المنسِّق (orchestrator §4)، لا ملف من ملفات P0 الثلاثة | موصى به | engines/P0 §4 registry step; profiles/erp.yaml (تعليق bounded_contexts) |
| 2 | الطبقة والترقيم / tier and number | Tier 1، الرقم 1.4 — الوحدة بلا اعتماديات فتصلح للبناء في أي وقت، ووضعها في طبقة أعلى يوحي باعتمادية غير موجودة | موصى به | [KB:erp-domain-standards §1]; engines/P0 §2.3 number stability |
| 3 | التعارض بين "كل وحدة عمل تعتمد HARD على SEC وMDL" (domain-profile §6) و"صفر اعتماديات" لـ NOTE | **مُعدَّل في الجولة 2** — يُفصل النوعان: (أ) اعتمادية SEC واقعة ولا خيار فيها، تُسجَّل SOFT: بلا تسجيل NOTE لنفسها في سجلات الوحدة/الشاشة/الإجراء تصبح شاشتها الوحيدة غائبة تمامًا (G2, G3)، وهو نفس ما سجّلته MDL وFIN في P0؛ (ب) "صفر اعتماديات" في الرؤية تعني صفر اعتمادية بيانات-مجال: لا MDL (لا قائمة قيم أصلًا فلا يسري G4)، ولا كيان أجنبي، ولا قارئ خارجي. ويبقى: لا صف XM ولا مفتاح أجنبي (سابقة ADR-FIN-001)، فتخرج INT-C وINT-R فارغتين لكن موجودتين | موصى به | domain-profile §6, G2/G3/G4; project-registry SHARED ENTITY DECLARATIONS + DECISION INDEX #9; erp/modules/MDL/P0/module-registry-mdl.md, erp/modules/FIN/P0/module-registry-fin.md; [KB:erp-domain-standards §5] |
| 4 | نوع الكيان: master أم transactional / entity kind | master — الملاحظة ليست مستندًا مرتبطًا بفترة محاسبية ولا مدفوعًا بحالة من lookup، وتُعطَّل تعطيلًا ناعمًا (isActiveFl)، وهو تعريف master في المعيار | موصى به | [KB:erp-domain-standards §2 rules 1–2, §6 soft delete] |
| 5 | ثنائية اللغة في محتوى الملاحظة / bilingual note content | الاصطلاح الثنائي (nameAr/nameEn) لا يسري على محتوى يكتبه المستخدم: العنوان والنص حقل حر واحد بلغة كاتبه — مُثبَّت كسياسة POL-NOTE-005؛ الاصطلاح يبقى ساريًا على أسماء الوحدة والكيان والشاشة | موصى به | [KB:erp-domain-standards §2 rule 1] (انحراف مُعلَن); domain-profile G11; profiles/erp.yaml languages |

## OPEN ITEMS
None — النطاق محدَّد بالكامل: كيان واحد، أربع عمليات، شاشة واحدة، صفر اعتماديات؛ القرارات
الخمس أعلاه تغلق كل نقطة أثارها هذا التحليل.

## NEXT STEP
Module 1.4 NOTE converges in module-registry-note.md and business-policies-note.md.
Requirements begin in P0.5 and later stages; these files are their input.
<<<END FILE>>>

<<<FILE: erp/modules/NOTE/P0/module-registry-note.md>>>
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
<<<END FILE>>>

<<<FILE: erp/modules/NOTE/P0/business-policies-note.md>>>
## BUSINESS POLICIES — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module   : NOTE     Source of truth : نص رؤية الوحدة + قرارات هذا الحوار / the module's vision text + this dialogue's resolutions
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)

POL-NOTE-001 — الملاحظة مرئية لمالكها فقط / A note is visible to its owner only
  Statement (ar) : يجب على النظام إتاحة قراءة الملاحظة لمستخدمها المالك دون سواه.
  Statement (en) : The system shall make a note readable only by the user who owns it.
  Pattern   : ubiquitous
  Trigger   : Search / Read
  Rationale : الرؤية تحصر القراءة في ملاحظات المستخدم نفسه — لا مشاركة ولا اطّلاع متبادل
  Source    : vision text — "A user writes a short note and reads their own notes back"; "search (own notes only)"
  Status    : CONFIRMED

POL-NOTE-002 — التعديل والتعطيل للمالك وحده / Owner-only update and deactivation
  Statement (ar) : إذا طلب مستخدم غير مالك الملاحظة تعديلها أو تعطيلها، فيجب على النظام رفض الطلب.
  Statement (en) : If a user who does not own a note requests its update or deactivation, then the system shall reject the request.
  Pattern   : unwanted
  Trigger   : Update / Deactivate
  Rationale : الملكية شرط كتابة كما هي شرط قراءة؛ بغير ذلك تُخترق حدود المالك من جهة الكتابة
  Source    : vision text — "four operations: create · update · deactivate · search (own notes only)"; resolved dialogue decision (module-registry-note.md #1 scope)
  Status    : CONFIRMED

POL-NOTE-003 — التقاعد بالتعطيل لا بالحذف / Retirement by deactivation, never by deletion
  Statement (ar) : يجب على النظام إخراج الملاحظة من الخدمة بالتعطيل وحده.
  Statement (en) : The system shall retire a note by deactivation alone.
  Pattern   : ubiquitous
  Trigger   : Deactivate
  Rationale : الحذف النهائي يُفقد أثر التدقيق؛ العملية الرابعة في الرؤية اسمها "تعطيل" لا "حذف"
  Source    : vision text — "four operations: … deactivate …"; [KB:erp-domain-standards §6 soft delete]
  Status    : CONFIRMED

POL-NOTE-004 — الملاحظة المعطَّلة خارج البحث الافتراضي / A deactivated note stays out of the default search
  Statement (ar) : أثناء كون الملاحظة معطَّلة، يجب على النظام استبعادها من البحث الافتراضي لمالكها.
  Statement (en) : While a note is deactivated, the system shall exclude it from its owner's default search.
  Pattern   : state
  Trigger   : Search
  Rationale : التعطيل يجب أن يُحدث أثرًا ملموسًا للمستخدم، وإلا صار علمًا بلا معنى
  Source    : vision text — "deactivate"; [KB:erp-domain-standards §6]
  Status    : CONFIRMED

POL-NOTE-005 — محتوى الملاحظة بلغة كاتبها / Note content is in its author's own language
  Statement (ar) : يجب على النظام حفظ عنوان الملاحظة ونصها كحقلين حرّين بلغة كاتبهما.
  Statement (en) : The system shall store a note's title and body as free-text fields in their author's own language.
  Pattern   : ubiquitous
  Trigger   : Create / Update
  Rationale : المحتوى الذي يكتبه المستخدم ليس بيانات مرجعية؛ فرض زوج ثنائي اللغة عليه يُلزم
              المستخدم بترجمة ملاحظته الشخصية. تبقى ثنائية اللغة سارية كاملةً على أسماء الوحدة
              والكيان والشاشة (domain-profile G11).
  Source    : resolved dialogue decision (platform-summary RESOLVED DECISIONS #5) — انحراف مُعلَن عن [KB:erp-domain-standards §2 rule 1]
  Status    : CONFIRMED

POL-NOTE-006 — مجموعة صلاحيات واحدة تحكم العمليات الأربع / One permission set governs all four operations
  Statement (ar) : يجب على النظام ضبط عمليات الملاحظة الأربع جميعها بمجموعة صلاحيات واحدة على شاشة الملاحظات الوحيدة.
  Statement (en) : The system shall govern all four note operations through a single permission set on the one Notes screen.
  Pattern   : ubiquitous
  Trigger   : Any authorization check
  Rationale : حجم الوحدة مقصود: شاشة واحدة، مجموعة صلاحيات واحدة — أي مجموعة ثانية تعني شاشة ثانية
  Source    : vision text — "one screen … one permission set on that screen"; [KB:erp-domain-standards §4]
  Status    : CONFIRMED

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
None — لا تملك الوحدة ولا تستهلك أي قائمة قيم مُرمَّزة / the module owns and consumes no coded value list.

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| مشاركة الملاحظة / note sharing | لا مسار لمشاركة ملاحظة مع مستخدم آخر ولا اطّلاع إداري شامل عليها في هذه النسخة / no sharing path and no administrative all-notes view in this version | طلب صريح من المستخدم لمشاركة أو لإشراف إداري | vision text — "reads their own notes back" |
| اعتماديات بيانات-مجال بين الوحدات / cross-module domain-data dependencies | لا صف XM ولا مفتاح أجنبي ولا قائمة قيم من MDL ولا كيان أجنبي / no XM row, no FK, no MDL lookup, no foreign entity. التسجيل الذاتي في سجلات SEC وبوابة الوحدة خارج هذا الاستثناء — invariant منصّي لا تملك أي وحدة الإعفاء منه (G2, G3) | قرار صريح لاحق يربط NOTE ببيانات وحدة أخرى | vision text — "zero cross-module dependencies"; domain-profile G2/G3; round-2 resolution #4 |
| توسيع النموذج / model growth | لا كيان ثانٍ ولا شاشة ثانية (وسوم، تصنيفات، مرفقات، تذكيرات) / no second entity or screen (tags, categories, attachments, reminders) | نسخة لاحقة تُعيد تحديد النطاق صراحة | vision text — "one entity … one screen" |
| ثنائية اللغة لمحتوى المستخدم / bilingual user content | العنوان والنص خارج اصطلاح nameAr/nameEn — انظر POL-NOTE-005 | طلب صريح بمحتوى ثنائي اللغة | [KB:erp-domain-standards §2 rule 1]; domain-profile G11 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | هل يرى مسؤول النظام كل الملاحظات؟ / Does an administrator see every note? | لا — لا استثناء لأي دور في هذه النسخة؛ الملكية هي الحدّ الوحيد (POL-NOTE-001) | موصى به — ينتظر تأكيد المستخدم | vision text — "own notes only"; [KB:erp-domain-standards §4] |
| 2 | ماذا يحدث للملاحظة المعطَّلة؟ / What becomes of a deactivated note? | تبقى محفوظة وتخرج من البحث الافتراضي لمالكها (POL-NOTE-003, POL-NOTE-004) | موصى به | [KB:erp-domain-standards §6] |
| 3 | هل يلزم أن يكون محتوى الملاحظة ثنائي اللغة؟ / Must note content be bilingual? | لا — حقل حر بلغة كاتبه (POL-NOTE-005)، مع بقاء ثنائية اللغة على الأسماء | موصى به | domain-profile G11; [KB:erp-domain-standards §2 rule 1] |
| 4 | هل تُسجَّل NOTE اعتمادية على SEC أو MDL؟ / Does NOTE record a SEC or MDL dependency? | **مُعدَّل في الجولة 2** — SEC: نعم، صف SOFT واحد (تسجيل ذاتي + بوابة الوحدة)، بلا صف XM وبلا مفتاح أجنبي؛ MDL: لا — لا قائمة قيم أصلًا | موصى به | project-registry SHARED ENTITY DECLARATIONS + DECISION INDEX #9; domain-profile §6, G2/G3; erp/modules/MDL/P0/module-registry-mdl.md |
══════════════════════════════════════════════════════════════════
<<<END FILE>>>

Nothing material remains open: every point raised in either round carries a recommended answer
written into a RESOLVED DECISIONS row of the artifact it affects (C3.5 no-questions passes), and the
two items that fall outside these three files — the `profiles/erp.yaml` bounded-context line and the
`erp-domain-standards.md §2 rule 1` qualifying clause — are named above for the orchestrator and the
knowledge base respectively.

<!-- CONVERGED -->
