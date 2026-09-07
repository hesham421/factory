# AMEND-PIPELINE-V5 — حزمة الاستبدال (المشاريع + الأدوات + الأوامر)

**المرجع الحاكم:** `projects/GOVERNANCE-CONFIG.md` §1D (المصدر الواحد). كل ما عداه يشير إليه.
**الدليل:** الباك 51 اختبار ✓ · الفرونت 22 اختبار ✓ (`PYTEST-EVIDENCE-*.txt`).

## خريطة الاستبدال — مشاريع Claude (`projects/`)
| المشروع | الملف | نوع التغيير |
|---|---|---|
| **كل المشاريع** | `GOVERNANCE-CONFIG.md` | **§1D + §1E جديدان** — §1E (حوكمة ترتيب Drive) **مولَّد آلياً من `config.DRIVE_LAYOUT`** (استبدل في الجميع) |
| P(-1) Master Registry Builder | `MASTER-REGISTRY-BUILDER-instructions.md` | bootstrap فقط + بروتوكول إنهاء |
| P0 | `PROJECT-0-PLATFORM-INCEPTION-ENGINE-v2.md` | banner + بروتوكول إنهاء |
| P0.5 PRD | `PRD-ENGINE.md` | banner + بروتوكول إنهاء |
| P1 SRS | `PROJECT-1-SRS-GOVERNANCE-ENGINE.md` | banner + بروتوكول إنهاء (registry-srs inline) |
| P2 DB | `PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md` | banner + بروتوكول إنهاء (registry-db inline) |
| P2.5 UI/UX | `UI-UX-DESIGN-ENGINE.md` | banner + بروتوكول إنهاء |
| P3.1 Backend | `PROJECT-3-BACKEND-ENGINE.md` | banner + بروتوكول إنهاء (registry-exec-be inline) |
| P3.2 Frontend | `PROJECT-3-FRONTEND-ENGINE.md` | banner + بروتوكول إنهاء + END للـ ledger |
| P3.5 Test Gen (اختياري) | `PROJECT-TEST-GENERATION-ENGINE.md` | نطاق مبسّط: TC specs → TestSprite |
| P4.1 / P4.2 Audit (اختياري) | `PROJECT-4-BACKEND-AUDIT.md` / `PROJECT-4-FRONTEND-AUDIT.md` | الناتج = fix-prompts مجمّعة حسب المشروع |
| P-REG | `PROJECT-REG-STATE-REGISTRY-EXTRACTOR.md` | **متقاعد** — استبدل الملف بالـ stub |
| P-ROUTER | (بلا ملف) | مُخفَّض لقارئ حالة اختياري؛ لا يُعتمد عليه |

> ملاحظة: ملفات المحركات = **المحتوى الأصلي + banner + قسم COMPLETION PROTOCOL** مع **pass إعادة تسمية مضبوط** للأسماء القديمة داخل النص (`srs.md`→`srs-[MOD].md`…). لم يُعَد كتابة منطق أي محرك؛ الأمندمنت + §1D هما الحاكمان. `PROJECT-3-REGISTRY.md` (backbone) لم يُعدَّل هنا — يبقى كما في حزمة AMEND-IFA.

## الأدوات (`tools-backend/` → `backend/governance/governance-tools/`)
| ملف | التغيير |
|---|---|
| `config.py` | أسماء مؤهَّلة بالموديول مُعرَّفة **مرة واحدة** (`EXEC_PLAN_FILE`/`TEST_PLAN_FILE` → `ARTIFACT_FILES`/`PLAN_ARTIFACTS`) + `plan_file()`/`plan_label()` + `classify_artifact()` قالبي (أصلح تجاوزاً صامتاً للفحوصات الدلالية) + **schema وhelpers الـ ledger** (§1D.3) |
| `agent3_splitter.py` | **صفر أسماء حرفية** + يكتب **split receipt** بعد Stage 5 (روابط الحزم للـ ledger تلقائياً) |
| `agent2_archive.py` | (من AMEND-IFA) version-aware |
| `drive_layout.py` | **جديد** — `--tree` (شجرة المجلدات المتوقعة لكل موديول/إصدار) و`--audit` (يكشف الملفات الشاردة/في المكان الخطأ ويُخرج خطة نقل/إعادة تسمية/إنشاء مجلدات للـ connector) — كله من `config.DRIVE_LAYOUT` |
| `journey_loader.py` | **جديد** — ledger → plan / verify / append / **append-receipts** / open / close / **backfill** (ترحيل Drive) |
| `tests/` | 5 ملفات محدَّثة/جديدة (منها `test_journey_loader.py` + حراس no-literal + حارس التصنيف) |

غير مُعدَّل: `agent1_create_structure.py`, `marker_parser.py`.

## الأدوات (`tools-frontend/` → `frontend/governance/governance-tools/`)
| ملف | التغيير |
|---|---|
| `config.py` | نفس نمط الباك (أسماء مرة واحدة + `plan_file`/`plan_label`) + إصدارات مشتقّة من الملفات (AMEND-IFA) |
| `agent3_splitter.py` | **صفر أسماء حرفية** + split receipt بعد Stage 5 |
| `agent1_create_structure.py` | (من AMEND-IFA) `--new-version` |
| `tests/` | محدَّثة config-driven + حارس no-literal |

غير مُعدَّل: `agent2_archive.py`, `marker_parser.py` (يتبعان config تلقائياً).

## الأوامر
`commands-backend/` → `backend/.claude/commands/` (و launcher حيث يعيش):
`process-project-files.md` (**STEP 0 Loader** + STEP 3.5 IFA + فحوصات config-resolved) · `generate-module-setup.md` · `orchestrate-module.md` · `governance-tools-launcher.md` (نص الأسماء → config).
`commands-frontend/` → `frontend/.claude/commands/`:
`process-project-files.md` (dual-track: **STEP 0 Loader** + STEP 3.5 لكل مسار) · `generate-frontend-module-setup.md` · `orchestrate-module.md`.

## مراجع UI Shell + API Docs المحوكمة (§1F) — الجديد
- مجلدان مرجعيان لكل إصدار موديول: `_ref/ui-shell` و`_ref/api-docs` (ضمن `config.DRIVE_LAYOUT`، مصدر واحد).
- **P3.2:** أول إرفاق → رفع نسخة دائمة مرة واحدة؛ إرفاق أحدث → **استبدال في المكان** (نسخة حية واحدة لكل إصدار، القديمة تُحذف وتُعلَّم SUPERSEDED)؛ بلا إرفاق → يقرأ النسخة المحوكمة → **أي محادثة تُفتح لاحقاً على الموديول ترث الاثنين تلقائياً**.
- **إصدار جديد (IFA):** إرفاق جديد يُدمَج في vN، وإلا **carry-forward** من vN-1؛ vN-1 يبقى مجمّداً.

## حوكمة ترتيب Drive (§1E)
- **القانون:** لا ملف خارج مجلد مرحلته؛ جذر `[CTX]` وجذر الموديول = مجلدات فقط؛ شجرة واحدة لكل موديول (الباك والفرونت معاً)؛ الإصدارات تحت `/vN/`؛ الـ ledger في `_journey/`؛ ملفات المنصّة في `_platform/`؛ كاتب واحد لكل مجلد.
- **كل محرك** فيه الآن كتلة **PATHS** (يكتب أين / يقرأ من أين) مولَّدة من نفس المصدر — واختبار يثبت تطابق النص مع الكود.
- **STEP 0.0** في المنسّقين يفحص الترتيب **ويطبّق الإصلاح بنفسه** (mkdir/rename/move + backfill للـ ledger)، يتوقف فقط أمام ملفات مجهولة.
- **§1E.5 Self-Heal:** كل محرك يعالج مدخلاته تلقائياً في الـ Pre-Flight (يبحث بالاسم الجديد/القديم، ينقل ويعيد التسمية عبر الـ connector، ينشئ ledger ناقصاً) — **لا خطوة يدوية للترحيل**. `DRIVE-MIGRATION-V5.md` صار مساراً اختيارياً للترحيل الجماعي فقط.

## ملفات إضافية
- `DRIVE-MIGRATION-V5.md` — إجراء ترحيل محتوى Drive الحالي (إعادة تسمية + بناء ledger لكل موديول موجود) عبر الـ connector.
- `GOVERNANCE-CONFIG.md` §1D.8 — الإجراء الدقيق لتسجيل الروابط من داخل المحرك (لأن `update_file` لا يحدّث المحتوى).

## الترحيل
1. طبّق الأدوات أولاً (تتوقع الأسماء الجديدة وترفض القديمة عمداً).
2. رحّل Drive لكل موديول موجود حسب `DRIVE-MIGRATION-V5.md` (إعادة تسمية + backfill للـ ledger).
3. استبدل ملفات المشاريع + ارفع `GOVERNANCE-CONFIG.md` في الجميع.
4. أوقف فتح جلسات P-REG؛ لا تعتمد على P-ROUTER.
