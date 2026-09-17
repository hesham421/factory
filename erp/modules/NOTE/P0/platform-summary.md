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
