# `governance-shared` — التصميم المعماري

> ريبو رابع، مقسَّم داخلياً، الكتابة فيه **مباشرة**، الباك معزول عن الفرونت،
> والمصنع يرى الطرفين.
>
> الحالة: **تصميم — لم يُنفَّذ.**
> يُقرأ بعد [SHARED-GOVERNANCE-PLAN.md](SHARED-GOVERNANCE-PLAN.md) §٧.

---

## ١ · المبدأ المعماري الحاكم

الخطأ الشائع في «مجلد مشترك» أنه يخلط ثلاثة أسئلة مختلفة:

| السؤال | الإجابة المعمارية |
|---|---|
| **مَن يملك الحقيقة؟** | مُنتِج واحد لكل مسار — لا استثناء |
| **مَن يحقّ له الكتابة؟** | المالك فقط، ويُفرَض آلياً |
| **مَن يحقّ له القراءة؟** | الجميع — القراءة ليست خطراً |

الريبو المشترك يحلّ سؤال **المكان**، ولا يحلّ سؤالَي الملكية والكتابة.
فيجب أن يفرضهما التصميم صراحةً، وإلا صار «مكاناً يكتب فيه الجميع» — وهو
أسوأ من النسخ اليدوي، لأن الانحراف يصبح غير مرئي.

### القاعدة الأولى: اتجاه واحد لكل مسار

```
                    ┌──────────────────────────┐
   الباك يكتب  ───► │                          │ ───►  الفرونت يقرأ
   (api-docs)       │    governance-shared     │       (api-docs)
                    │                          │
   المصنع يكتب ───► │   مقسَّم · مالك واحد      │ ───►  الباك يقرأ
   (packages,       │      لكل مسار             │       (packages/backend)
    rules,          │                          │ ───►  الفرونت يقرأ
    registry)       └──────────────────────────┘       (packages/frontend)
                                │
                                └──►  المصنع يقرأ الطرفين
```

**لا سهم مرتدّ.** الفرونت لا يكتب api-docs أبداً — هي مشتقّة من الكود الشغّال،
وأي تعديل يدوي يُمحى عند أول `generate-api-docs`. الخطأ فيها **عيب في الكود**.

---

## ٢ · التقسيم الداخلي

```
governance-shared/
│
├── platform/                    ◄── المصنع يكتب · الجميع يقرأ
│   ├── rules/                       قواعد الحوكمة، تعريفات الذرّات، العقود
│   ├── modules-registry.json        سجل الموديولات (مشتقّ من نظام الملفات)
│   └── profile-summary.md           ملخّص البروفايل الفعّال
│
├── backend/                     ◄── منطقة الباك — معزولة
│   └── modules/{MOD}/
│       ├── api-docs/                ✍ الباك يكتب (مولَّد من /v3/api-docs)
│       │   ├── index.md
│       │   └── endpoints/*.md
│       ├── packages/                ✍ المصنع يكتب (backend-execution, backend-test)
│       └── execution-state.json     ✍ المصنع يكتب
│
├── frontend/                    ◄── منطقة الفرونت — معزولة
│   └── modules/{MOD}/
│       ├── packages/                ✍ المصنع يكتب (frontend-execution, frontend-test)
│       └── execution-state.json     ✍ المصنع يكتب
│
└── CODEOWNERS                   ◄── يفرض الملكية آلياً
```

### لماذا `backend/` و `frontend/` منفصلان تماماً؟

**العزل ليس تنظيماً — بل ضمانة.** الفرونت لا يملك مساراً واحداً تحت
`backend/`، والعكس. فأي محاولة كتابة عابرة للحدّ تُرفَض في مرحلة المراجعة،
لا تُكتشف بعد أسبوع في diff.

### أين تُقرأ الـ api-docs من الفرونت؟

`frontend/` لا يحوي `api-docs/`. الفرونت يقرأ من `backend/modules/{MOD}/api-docs/`
**بالقراءة فقط**. هذا مقصود:

- مصدر واحد لا نسختان → **لا انحراف ممكن بنيوياً** (لا مجرّد مكشوف)
- الفرونت يظلّ ممنوعاً من الكتابة (CODEOWNERS)
- يحلّ مشكلة CU · FILE · NOTIF الموجودة في الباك دون الفرونت

> هذا يخالف حرفية قاعدة العزل، ويوافق روحها: العزل يمنع **الكتابة** المتبادلة
> لا القراءة. والبديل (نسختان) هو بالضبط ما نحاول إلغاءه.

---

## ٣ · جدول الملكية (المرجع الوحيد)

| المسار | الكاتب الوحيد | القرّاء | الأداة المنتِجة |
|---|---|---|---|
| `platform/rules/` | **المصنع** | الجميع | `gov.py publish` |
| `platform/modules-registry.json` | **المصنع** | الجميع | `gov.py publish` |
| `backend/modules/*/api-docs/` | **الباك** | المصنع · الفرونت | `generate-api-docs` |
| `backend/modules/*/packages/` | **المصنع** | الباك | `gov.py deliver --track backend` |
| `frontend/modules/*/packages/` | **المصنع** | الفرونت | `gov.py deliver --track frontend` |
| `*/execution-state.json` | **المصنع** | مالك المسار | `gov.py deliver` |

### `CODEOWNERS`

```
/platform/                @factory-maintainers
/backend/*/api-docs/      @backend-maintainers
/backend/                 @factory-maintainers
/frontend/                @factory-maintainers
```

الأخصّ يفوز: الباك يملك `api-docs/` فقط، والمصنع يملك ما عداه داخل `backend/`.

---

## ٤ · آلية الوصل: submodule مثبَّت

### لماذا submodule لا clone مجاور

`clone` مجاور يكسر الاكتفاء الذاتي المنصوص عليه في `factory.yaml`:

> *"A consumer repo must be self-sufficient: everything it reads lives inside
> its own checkout, never at a path above it."*

الـ submodule **داخل** الـ checkout، فالقاعدة محفوظة، و CI يعمل بـ `--recursive`.

### نقطة الوصل في كل مستودع

| المستودع | المسار | ما يراه |
|---|---|---|
| `factory/` | `shared/` | **كل شيء** (يكتب ويقرأ الطرفين) |
| `backend/` | `governance/shared/` | `platform/` + `backend/` + api-docs |
| `frontend/` | `governance/shared/` | `platform/` + `frontend/` + api-docs (قراءة) |

> **«كلٌّ يرى ما يخصّه» لا يُفرَض في git** — الـ submodule يعطي الجميع كل شيء.
> التقسيم + `CODEOWNERS` يفرضان **الكتابة** لا الرؤية. هذه حدود الأداة،
> ويجب الإقرار بها لا تجاهلها.

### المؤشّر المثبَّت — أهم قرار في التصميم

الـ submodule يشير إلى **commit محدّد**، لا إلى فرع متحرّك. هذا ليس قيداً بل ميزة:

```
backend @ abc123  ──►  shared @ def456    ← نسخة v1 المجمّدة
frontend @ xyz789 ──►  shared @ def456    ← نفس النسخة بالضبط
```

- نسخة v1 المسلَّمة **لا تتغيّر تحت قدميها** عند تحديث الـ shared
- ترقية المؤشّر **فعل واعٍ** يظهر في الـ diff ويمرّ بمراجعة
- يمكن إثبات أيّ نسخة api-docs بُني عليها أيّ إصدار — تدقيق كامل

هذا يحلّ مشكلة لا يحلّها المجلد المشترك إطلاقاً: **التجميد**.

---

## ٥ · دورة المزامنة

### ٥-١ الباك ينشر api-docs

```
1. generate-api-docs يكتب مباشرة في:
   backend/governance/shared/backend/modules/{MOD}/api-docs/
2. commit + push داخل الـ submodule          → shared@new
3. bump المؤشّر في backend + commit          → الباك يعلن ما بنى عليه
```

### ٥-٢ المصنع يسحب

```
4. git submodule update --remote  في factory
5. gov.py fetch-inputs -m {MOD}
   → يقرأ من shared/backend/modules/{MOD}/api-docs/
   → يدمج index.md + endpoints/*.md → _inputs/api-docs-{mod}.md
```

### ٥-٣ المصنع يسلّم

```
6. gov.py deliver --track backend   → shared/backend/modules/{MOD}/packages/
   gov.py deliver --track frontend  → shared/frontend/modules/{MOD}/packages/
   gov.py publish                   → shared/platform/
7. commit + push داخل الـ submodule → shared@newer
```

### ٥-٤ المستهلك يرقّي بوعي

```
8. git submodule update --remote  في backend/frontend
9. bump المؤشّر + commit
```

### ٥-٥ الأمر الواحد الذي يخفي هذا كله

```
gov.py sync                 # يقرأ shared، يبلّغ عن التأخّر
gov.py sync --push          # يكتب ويدفع ويرقّي المؤشّر
gov.py sync --dry-run       # إجباري قبل أي دفع
```

**مبرّر وجوده:** بدونه تصبح كل مزامنة ٣ commits + ٣ ترقيات يدوية — وهو
ما قِسناه في §٧-٣ من الخطة وكان **أثقل** من النسخ اليدوي الحالي.
`gov.py sync` هو ما يجعل التصميم مكسباً لا خسارة.

---

## ٦ · وعي المصنع بالطرفين

المصنع اليوم يعرف `repos.backend` و `repos.frontend`. يضاف ثالث:

```yaml
repos:
  shared:
    url: "https://github.com/hesham421/governance-shared.git"
    checkout_env: GOV_SHARED_CHECKOUT
    checkout_default: "shared"          # submodule داخل المصنع
    partitions:                          # ← جديد: وعي المصنع بالتقسيم
      platform: "platform/"
      backend:  "backend/modules/{MOD}/"
      frontend: "frontend/modules/{MOD}/"

  backend:
    publishes:
      api-docs: "backend/modules/{MOD}/api-docs/"   # داخل shared الآن
    reads_from: shared
  frontend:
    reads_from: shared
```

**المصنع هو الوحيد الذي يقرأ القسمين.** وهذا صحيح معمارياً: هو الوحيد الذي
يوفّق بين الـ SRS والـ api-docs وخطط الطرفين — وظيفته بالتعريف.

### فحوص جديدة يتيحها الوعي بالطرفين

| الفحص | يمنع |
|---|---|
| `shared-pointer-fresh` | مستهلك يبني على `shared` متأخّر عن المُسلَّم |
| `partition-writer` | كتابة خارج المسار المملوك |
| `api-docs-reachable` | خطة فرونت تستشهد بـ endpoint غير منشور |

الثالث هو نفسه `C7.23` الذي بنيناه — لكن على **المصدر المنشور** لا على خطة الباك.

---

## ٧ · الأدوات المتأثرة

### تتغيّر

| الأداة | التغيير | الخطورة |
|---|---|---|
| `backend/…/generate-api-docs.md` | يكتب في `governance/shared/backend/…` | **متوسطة** — تغيير وجهة |
| `factory/factory.yaml` | `repos.shared` · `partitions` · `publishes` | منخفضة |
| `factory/…/gov.py` | `fetch-inputs` (دمج مجلد) · `deliver` (وجهة) · `sync` جديد | **عالية** |
| `factory/…/config.py` | `repo_checkout` يفهم `partitions` | منخفضة |
| CI في الثلاثة | `clone --recursive` + فحص تأخّر المؤشّر | متوسطة |

### لا تتغيّر

| الأداة | السبب |
|---|---|
| `generate-module-setup.md` (الباك) | ينشئ هيكلاً محلياً |
| `generate-frontend-module-setup.md` | نفس السبب |
| `orchestrate-module.md` (الطرفان) | يقرأ عبر مسار — يُعاد توجيهه بمتغيّر واحد |
| `generate.py` · `api-verify` · `test-gen` · `analyze` | لا علاقة لها بالمكان |

---

## ٨ · ما يكسر هذا التصميم (يجب الإقرار به)

| الخطر | الأثر | التخفيف |
|---|---|---|
| **`clone` بلا `--recursive`** | مستودع صامت الكسر — `shared/` فارغ | فحص في CI + `gov.py sync` يرفض |
| **HEAD منفصل في submodule** | commit يضيع بلا أثر | `submodule.<name>.branch` + `sync --push` يتولّاه |
| **كاتبان على ريبو واحد** | تعارض دمج | العزل بالمسار يجعله نادراً — لا مسار مشترك |
| **مؤشّر متأخّر** | البناء على api-docs قديمة بلا علم | `shared-pointer-fresh` (CRITICAL) |
| **الفرونت يعدّل api-docs** | كذبة تُمحى | `CODEOWNERS` + الفحص |
| **تاريخ ثقيل** | `shared` يتضخّم بالمسلَّمات | `shallow=true` في `.gitmodules` |

### الخطر الأكبر: الطقوس

قِسنا في الخطة §٧-٣: **~٣ مزامنات أسبوعياً**. بلا `gov.py sync` يصبح ذلك
**٩ commits أسبوعياً** من الطقوس الخالصة — أثقل من النسخ اليدوي الحالي.

> **`gov.py sync` ليس رفاهية — هو شرط جدوى التصميم كله.**
> لو نُفِّذ الريبو بلا الأمر، النتيجة تراجع لا تقدّم.

---

## ٩ · الترتيب المقترح

| # | الخطوة | يُفتح بها |
|---|---|---|
| **٠** | **المرحلة أ** (تصحيح المسار + دمج المجلد) | **شرط لازم** — لا يُغني عنه الريبو |
| ١ | إنشاء `governance-shared` + التقسيم + `CODEOWNERS` | الهيكل |
| ٢ | نقل api-docs الحالية (٦ موديولات) بالتاريخ | مصدر واحد |
| ٣ | ربط submodule في الثلاثة | الوصل |
| ٤ | `gov.py sync` + `--dry-run` | **الجدوى** |
| ٥ | إعادة توجيه `generate-api-docs` | الكتابة المباشرة |
| ٦ | فحوص §٦ + CI | منع التراجع |

### لماذا المرحلة أ أولاً رغم الريبو

العطل المُكتشَف بنيوي لا مكانيّ:

```
المُعلَن : governance/api-docs/api-docs-{mod}.md   ← ملف، غير موجود
الواقع  : {MOD}/api-docs/index.md + endpoints/*   ← مجلد
```

`fetch-inputs` سيظلّ عاجزاً عن قراءة مجلد **أينما وُضع**. ونقل ملفات معطوبة
الربط إلى ريبو جديد ينقل العطل معها ويضيف إليه طبقة.

---

## ١٠ · الحكم المعماري

### ما يكسبه التصميم

✅ مصدر واحد للـ api-docs — **الانحراف مستحيل بنيوياً** لا مكشوف فقط
✅ تجميد قابل للإثبات — أي إصدار يعرف ما بُني عليه
✅ ملكية مفروضة آلياً لا بالعُرف
✅ عزل حقيقي بين الباك والفرونت
✅ الاكتفاء الذاتي محفوظ (submodule داخل الـ checkout)

### ما يكلّفه

⚠️ طبقة git إضافية يجب أن يتعلّمها كل مساهم
⚠️ `gov.py sync` شرط وجودي — بدونه التصميم تراجع
⚠️ نقل تاريخي لستة موديولات
⚠️ CI في ثلاثة مستودعات

### متى يستحقّ

| الحالة | الحكم |
|---|---|
| مطوّر واحد · ٣ مزامنات/أسبوع | **المرحلة أ + ب تكفي** — الريبو مبالغة |
| فريق · مزامنة يومية · CI | **الريبو يستحقّ** |
| موديولات جديدة كثيرة قادمة | **الريبو يستحقّ** — التجميد وحده يبرّره |

**توصيتي:** نفّذ **المرحلة أ الآن** (رخيصة، تكشف إن كان الباقي ضرورياً)،
ثم الريبو حين يتحقّق أحد شرطَي الاستحقاق.

---

## ١١ · جرد الأدوات والأوامر (المسح الكامل)

> §٧ كان جدولاً موجزاً. هذا الجرد الفعلي بالمسح: **٣١ ملفاً** يذكر `api-docs`،
> مصنَّفة بما يلزمها.

### ١١-١ الفئة أ — تتغيّر فعلياً (٤ ملفات فقط)

| # | الملف | التغيير | لماذا |
|---|---|---|---|
| ١ | `backend/…/api-doc-generator/discovery.py` | `default_output_dir()` | `GOVERNANCE_ROOT/modules/{M}/api-docs` ← يصبح `GOVERNANCE_ROOT/shared/backend/modules/{M}/api-docs` |
| ٢ | `backend/.claude/commands/generate-api-docs.md` | سطر `Writes to` + تعليمات الـ commit | الوجهة تغيّرت، ويحتاج commit داخل submodule |
| ٣ | `backend/.claude/commands/generate-module-setup.md` | قالب المسار (موضعان) | **مولِّد** — يصلح كل أوامر الباك |
| ٤ | `frontend/…/generate-frontend-module-setup.md` | قالب المسار (موضعان) | **مولِّد** — يصلح كل أوامر الفرونت |

**اكتشاف يقلّص العمل كثيراً:** أوامر كل موديول **مولَّدة** لا مكتوبة يدوياً.

```
generate-module-setup.md  →  .claude/commands/{MOD}/execute-backend.md
                             .claude/commands/{MOD}/execute-backend-test.md
```

فالملفات الستّة التالية **لا تُحرَّر يدوياً** — يُصلَح المولِّد ثم يُعاد توليدها:

```
backend/.claude/commands/{SEC,FIN,MDL}/execute-backend-test.md
frontend/.claude/commands/{SEC,FIN,MDL}/execute-frontend.md
```

وكذلك `discovery.py` يشتقّ جذره من موقعه (`GENERATOR_ROOT.parent.parent`) —
فالتغيير **دالة واحدة**، لا مسارات متناثرة.

### ١١-٢ الفئة ب — إعدادات فقط (لا كود)

| الملف | التغيير |
|---|---|
| `factory/factory.yaml` | `repos.shared` · `partitions` · `publishes.api-docs` · `receives` |
| `.gitmodules` × ٣ | نقطة الوصل + `branch` + `shallow` |

**السبب أنها إعدادات فقط:** تحقّقت أن محرّكات المصنع **لا تحوي مساراً حرفياً
واحداً**. كلها ترندر من الإعدادات:

```jinja
{%- set api_docs = factory.inputs['api-docs'].file.replace('{mod}', MOD|lower) -%}
`{{ inputs_dir }}/{{ api_docs }}` (published at `{{ factory.repos.backend.publishes['api-docs'] }}`)
```

فهذه **لا تتغيّر رغم أنها تذكر api-docs**:

```
factory/engines/P3.1/references/ENGINE.md
factory/engines/P3.2/references/ENGINE.md · SKILL.md
factory/standalone/api-verify/{SKILL.md, references/ENGINE.md}
factory/standalone/test-gen/references/ENGINE.md
factory/shared/{ARTIFACT-CONTRACTS,GOVERNANCE-CORE,QUALITY-RUBRIC}.md
```

> هذا ثمرة قاعدة C1 (لا حرفيات في الكود). لولاها لكان الجرد ١٢ ملفاً إضافياً.

### ١١-٣ الفئة ج — منطق أدوات المصنع

| الدالة | التغيير | الخطورة |
|---|---|---|
| `gov.py::cmd_fetch_inputs` | `copy2` ملف ← دمج مجلد (المرحلة أ) | **متوسطة** |
| `gov.py::cmd_deliver` | الوجهة ← قسم الـ shared | متوسطة |
| `gov.py::cmd_publish` | يكتب `platform/` | منخفضة |
| `gov.py::cmd_sync` | **جديد** | **عالية** |
| `config.py::repo_checkout` | يفهم `partitions` | منخفضة |

### ١١-٤ الفئة د — مهارات التحقّق

| الملف | التغيير |
|---|---|
| `backend/.claude/skills/api-verify/SKILL.md` | مسار واحد (`governance/modules/<MOD>/api-docs/`) |
| `frontend/.claude/skills/api-verify/SKILL.md` | نفسه |

سطر واحد في كلٍّ — تقرأ ولا تكتب، فلا تحتاج منطق submodule.

### ١١-٥ الفئة هـ — الاختبارات (تفشل إن أُهملت)

```
factory/governance-tools/tests/test_resolution.py
factory/governance-tools/tests/test_endpoint_agreement.py
factory/governance-tools/tests/test_orchestrator.py
```

تبني مستودعات لعبة وتضع api-docs في المسار القديم. **ستفشل فوراً** عند تغيير
الإعدادات — وهذا مطلوب: هي الشبكة التي تمسك الخطأ.

> سابقة من هذه الجلسة: ثلاثة اختبارات حارسة أمسكت أخطاءً حقيقية أثناء `C7.23`.
> تعديلها جزء من العمل لا عبء إضافي.

### ١١-٦ لا تتغيّر إطلاقاً

| الملف | السبب |
|---|---|
| `backend/…/orchestrate-module.md` | يقرأ `governance/modules/{MOD}/` — الـ packages تبقى مرئية هناك عبر الـ submodule |
| `frontend/…/orchestrate-module.md` | نفسه · وقاعدته *"api-docs is ground truth"* يدعمها التصميم |
| `generate.py` · `contract_extractor.py` · `openapi_extractor.py` | تقرأ من التطبيق الشغّال، لا من القرص |
| `api-doc-generator/README.md` | توثيق — يُحدَّث لا يُعدَّل منطقياً |
| `test-gen` · `analyze` · `api-verify` (المصنع) | ترندر من الإعدادات |

---

## ١٢ · خلاصة الجرد

| الفئة | العدد | الطبيعة |
|---|---|---|
| أ — تغيير فعلي | **٤** | منها **٢ مولِّدان** يصلحان ٦ ملفات تلقائياً |
| ب — إعدادات | **٤** | `factory.yaml` + ٣ `.gitmodules` |
| ج — منطق المصنع | **٥ دوال** | `cmd_sync` وحده جديد |
| د — مهارات | **٢** | سطر واحد لكلٍّ |
| هـ — اختبارات | **٣** | تفشل عمداً ثم تُحدَّث |
| **لا تتغيّر** | **١٨** | بفضل C1 والتوليد |

### الاستنتاج المعماري

**الجرد أصغر مما يبدو، لسببين بنيويين:**

1. **قاعدة C1** — لا حرفيات في محرّكات المصنع ⟵ ١٢ ملفاً ينجو
2. **أوامر الموديولات مولَّدة** ⟵ ٦ ملفات تنجو

> **هذا اختبار للمعمار نفسه:** نظام يحتاج تحرير ٣١ ملفاً لنقل مجلد واحد
> هو نظام مكسور. أن يحتاج ٤ + إعدادات — دليل أن الطبقات سليمة.

⚠️ **لكن التحذير قائم:** الجرد الصغير يقيس تكلفة **النقل** لا تكلفة **التشغيل**.
كلفة التشغيل هي `gov.py sync` و ٣ مؤشّرات submodule — وهي التي تقرّر
الجدوى، لا هذا الجرد.
