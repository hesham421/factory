<!-- ═══════════════════════════════════════════════════════════ -->
<!-- SRS — وثيقة التحليل والمتطلبات                             -->
<!-- Governed by: SRS Governance Engine (Project 1)             -->
<!-- Compatible: PROJECT-2 | PROJECT-3 | PROJECT-4              -->
<!-- Structure : PART A (Module Foundation) + PART B (Screens)  -->
<!-- ═══════════════════════════════════════════════════════════ -->

# وثيقة التحليل (SRS)
## الملاحظات الشخصية | Personal Notes (DEMO)

---

# ══════════════════════════════════════════════════════════
# PART A — MODULE FOUNDATION
# Single source of truth — read once per module
# ══════════════════════════════════════════════════════════

---

## A1 — معلومات الوثيقة (Document Information)

| البند | القيمة |
|---|---|
| **اسم المشروع** | مصنع الحوكمة — منصة أدوات شخصية (General / Personal Productivity — ليست ERP، انظر domain/domain-profile.md) |
| **الموديول** | الملاحظات الشخصية (Personal Notes) |
| **Feature Code** | DEMO-001 |
| **Feature Type** | Transactional |
| **الإدارة / القسم** | لا ينطبق — أداة شخصية للمستخدم الفردي (single-owner utility) |
| **إعداد بواسطة** | مصنع الحوكمة (P1 — SRS Governance Engine) |
| **النسخة** | 1.0 |
| **التاريخ** | 2026-09-07 |
| **الحالة** | Draft |
| **Open Questions** | None — see OQ Log |
| **Governed by** | SRS Governance Engine (Project 1) |

---

## A2 — السياق الوظيفي (Functional Context)

### ما يشمله هذا الموديول

> إدارة كاملة (CRUD) للملاحظات الشخصية: إنشاء ملاحظة بعنوان ومحتوى،
> عرض قائمة الملاحظات الخاصة بالمستخدم، فتح ملاحظة واحدة لقراءتها
> كاملة، تعديل عنوان/محتوى ملاحظة موجودة، وحذف ملاحظة (حذف ناعم —
> soft delete). كل ملاحظة مملوكة حصرياً للمستخدم الذي أنشأها.

### ما لا يشمله هذا الموديول

> لا مشاركة الملاحظات بين المستخدمين، لا مجلدات أو وسوم (tags)، لا
> مرفقات، لا نص منسّق (rich text) — المحتوى نص عادي فقط، لا سجل
> إصدارات لمحتوى الملاحظة، لا بحث متقدم بخلاف قائمة بسيطة. هذه حدود
> صريحة مستمدة من الطلب الأصلي ("موديول بسيط ... CRUD كامل") ومن
> business-policies-demo.md SCOPE EXCEPTIONS.

### وظيفة الموديول

> يمكّن هذا الموديول المستخدم من الاحتفاظ بملاحظاته الشخصية النصية
> وإدارتها بالكامل (إنشاء، قراءة، تعديل، حذف) دون أي تعقيد إضافي.

### الوصف الوظيفي التفصيلي

> المستخدم المصادَق عليه (authenticated) يرى فقط ملاحظاته الخاصة.
> عند الإنشاء يُدخل عنواناً (إلزامي) ومحتوى (اختياري). القائمة تعرض
> الملاحظات النشطة (ACTIVE) افتراضياً؛ الحذف لا يزيل السجل فعلياً بل
> يضع حالته DELETED فيُستبعد من القائمة والعرض الافتراضي. لا توجد
> أدوار متعددة — كل مستخدم "مالك" (owner) لملاحظاته فقط، ولا يوجد دور
> إداري يرى ملاحظات الآخرين في نطاق هذا الموديول.

#### الوضع الحالي

> لا ينطبق — هذه أداة جديدة بالكامل (net-new)، وليست استبدالاً لنظام
> يدوي أو سابق. *(القسم الفرعي "الصعوبات الحالية" يُحذف لنفس السبب.)*

#### النظام المقترح وفوائده

| # | الفائدة |
|---|---|
| 1 | مكان واحد بسيط ومحكوم (governed) لتدوين الملاحظات الشخصية بدلاً من أدوات مبعثرة. |
| 2 | حذف ناعم يمنع فقدان البيانات عرضياً مع إبقاء تجربة "حذف" كاملة للمستخدم. |

### ملاحظات عامة

- النمط المعتمد للشاشة هو PATTERN-2 (Inline / Side Drawer) — انظر B1 —
  لأن الكيان لا يحتوي سطوراً متكررة ولا تسلسلاً هرمياً (معيار 5.8.2).
- لا يوجد Workflow Engine (RULE-13 — WORKFLOW-ENGINE-TIER = OFF)، ولا
  Business Code لهذا الكيان (BC-RULE-0 لا ينطبق — كيان بسيط بدون حاجة
  لرمز عمل).
- الحقل المعياري `isActiveFl` استُبدل بحقل `statusId` (LOV-DEMO-001 —
  NOTE_STATUS: ACTIVE/DELETED) ليكون هو المصدر الوحيد لحالة الحذف
  الناعم — تجنباً لازدواج حقلين يؤديان نفس الغرض على كيان بسيط بحقل
  حالة واحد فقط.

---

## A3 — الكيانات والحقول (Entities & Fields)

---

### ENTITY-DEMO-001 — الملاحظة (Note)

| البند | القيمة |
|---|---|
| **النوع** | PRIVATE |
| **Business Code** | NO — لا ينطبق BC-RULE-0 (كيان بسيط بحقلي عنوان/محتوى، لا حاجة عمل لرمز مرجعي) |
| **المصدر** | الطلب: "موديول بسيط لإدارة ملاحظات شخصية: عنوان + محتوى + CRUD كامل"؛ module-registry-demo.md ENTITIES OWNED |
| **العمليات** | Create, Read, Update, Delete (soft) |
| **Cross-Module** | None |

#### حقول الكيان

| اسم الحقل | نوع البيانات (*) | إلزامي | القيم / المصدر | ملاحظات | Label-AR | Label-EN |
|---|---|---|---|---|---|---|
| noteId | BIGINT (PK) | نظام | — | رقم إنشائي تلقائي (SEQUENCE — GOVERNANCE-CONFIG.md §3) | المعرف | ID |
| title | VARCHAR(200) | نعم | — | RULE-DEMO-001 | العنوان | Title |
| content | TEXT | لا | — | RULE-DEMO-002 — قد يكون فارغاً | المحتوى | Content |
| statusId | VARCHAR(50) | نعم | LOV-DEMO-001 | lookupKey: NOTE_STATUS — الحقل الوحيد لدورة الحياة/الحذف الناعم (يحل محل isActiveFl لهذا الكيان — انظر A2 ملاحظات عامة) | الحالة | Status |
| ownerUserId | BIGINT | نظام | — | مرجع للمستخدم المصادَق عليه من سياق المنصة — يُضبط تلقائياً من الجلسة، ليس حقلاً يُدخله المستخدم؛ ليس FK لكيان محكوم في هذه المنصة (module-registry-demo.md AUTO-DECISIONS) | مالك الملاحظة | Owner |
| createdBy | VARCHAR | نظام | — | AuditEntityListener — لا يُقبل في DTO | أنشئ بواسطة | Created By |
| createdAt | TIMESTAMP | نظام | — | AuditEntityListener — لا يُقبل في DTO | تاريخ الإنشاء | Created At |
| updatedBy | VARCHAR | نظام | — | AuditEntityListener — لا يُقبل في DTO | عُدِّل بواسطة | Updated By |
| updatedAt | TIMESTAMP | نظام | — | AuditEntityListener — لا يُقبل في DTO | تاريخ التعديل | Updated At |

(*) نوع البيانات حسب DB_TARGET = POSTGRESQL_16 (GOVERNANCE-CONFIG.md §3):
    BIGINT (PK/FK) / VARCHAR(n) / TEXT / TIMESTAMP — لا NUMBER/VARCHAR2/CLOB
    (تلك لـ ORACLE_19C فقط) ولا SERIAL/IDENTITY (تُستخدم SEQUENCE صراحة).

> **قاعدة Label إلزامية:** كل حقل يحمل Label-AR و Label-EN كما هو مثبت أعلاه.

---

## A4 — قواعد التحقق (Business Rules)

> **قاعدة إلزامية:** هذا القسم هو المصدر الوحيد لتعريف القواعد.
> PART B يُشير للقواعد بـ RULE-ID فقط — لا يُعيد تعريفها.

---

### RULE-DEMO-001 — العنوان إلزامي

| البند | القيمة |
|---|---|
| **Scope** | ENTITY-DEMO-001 |
| **Trigger** | عند الحفظ (Create) / عند التعديل (Update) |
| **Statement** | The system MUST require a non-blank `title`, maximum 200 characters, before saving a note. |
| **Message-AR** | يجب إدخال عنوان للملاحظة (200 حرف كحد أقصى). |
| **Message-EN** | A note title is required (max 200 characters). |
| **Source** | الطلب: "عنوان" — module-registry-demo.md |
| **Test-Hint** | Boundary: title at exactly 200 chars (VALID), 201 chars (INVALID), blank/whitespace-only (INVALID). |

### RULE-DEMO-002 — حد أقصى لطول المحتوى

| البند | القيمة |
|---|---|
| **Scope** | ENTITY-DEMO-001 |
| **Trigger** | عند الحفظ (Create) / عند التعديل (Update) |
| **Statement** | The system MUST limit `content` to at most 20,000 characters; `content` MAY be blank or absent. |
| **Message-AR** | محتوى الملاحظة يتجاوز الحد المسموح (20000 حرف). |
| **Message-EN** | Note content exceeds the allowed limit (20,000 characters). |
| **Source** | الطلب: "محتوى" — module-registry-demo.md؛ الحد الأقصى قرار تناسبي من المحلّل (proportionate default لأداة "بسيطة") |
| **Test-Hint** | Boundary: content at exactly 20,000 chars (VALID), 20,001 chars (INVALID), empty string / omitted (VALID). |

### RULE-DEMO-003 — الوصول يقتصر على المالك

| البند | القيمة |
|---|---|
| **Scope** | ENTITY-DEMO-001 |
| **Trigger** | عند القراءة (Read/List) / التعديل (Update) / الحذف (Delete) |
| **Statement** | The system MUST only allow a user to read, update, or delete a note whose `ownerUserId` equals the acting authenticated user's id; any other user's request for that note MUST be rejected. |
| **Message-AR** | لا تملك صلاحية الوصول لهذه الملاحظة. |
| **Message-EN** | You do not have access to this note. |
| **Source** | domain/domain-profile.md — Governing Rules ("Owner-based access, not role-based") |
| **Test-Hint** | User B requesting User A's noteId by direct ID → rejected, not merely filtered from the list. |

### RULE-DEMO-004 — الحذف ناعم (Soft Delete)

| البند | القيمة |
|---|---|
| **Scope** | ENTITY-DEMO-001 |
| **Trigger** | عند الحذف (Delete) |
| **Statement** | The system MUST perform delete as a soft delete: set `statusId = DELETED` rather than physically removing the row. Notes with `statusId = DELETED` MUST be excluded from the default list and from get-by-id retrieval. |
| **Message-AR** | تم حذف الملاحظة. |
| **Message-EN** | Note deleted. |
| **Source** | module-registry-demo.md AUTO-DECISIONS (soft-delete default) |
| **Test-Hint** | After delete, GET list excludes it; GET by id returns 404 (not the deleted record). |

### RULE-DEMO-005 — لا تعديل على ملاحظة محذوفة

| البند | القيمة |
|---|---|
| **Scope** | ENTITY-DEMO-001 |
| **Trigger** | عند التعديل (Update) |
| **Statement** | The system MUST reject an update attempt on a note whose `statusId = DELETED`. |
| **Message-AR** | لا يمكن تعديل ملاحظة محذوفة. |
| **Message-EN** | A deleted note cannot be updated. |
| **Source** | مشتقة (analyst-derived) للحفاظ على اتساق RULE-DEMO-004 |
| **Test-Hint** | Update on a DELETED note's id → rejected (same status family as "not found" per RULE-DEMO-004, see Error Catalog owned by P3.1). |

---

## A5 — قوائم القيم (LOV / Lookup)

> **قاعدة إلزامية:** هذا القسم هو المصدر الوحيد لتعريف LOVs.
> PART B يُشير للـ LOVs بـ LOV-ID أو lookupKey فقط — لا يُعيد تعريفها.

---

### LOV-DEMO-001 — حالة الملاحظة (Note Status)

| البند | القيمة |
|---|---|
| **الحقل** | statusId |
| **ENTITY-ID** | ENTITY-DEMO-001 |
| **نوع التحكم** | Dropdown (≤15 — القيم هنا 2 فقط) |
| **lookupKey** | NOTE_STATUS |
| **المصدر** | MD_LOOKUP_DETAIL |
| **المالك** | هذا الموديول (DEMO) |
| **API الاستهلاك** | GET /api/lookups/NOTE_STATUS?active=true |

| code | الاسم بالعربي | الاسم بالإنجليزي |
|---|---|---|
| ACTIVE | نشطة | Active |
| DELETED | محذوفة | Deleted |

⚠ القيمة المُخزَّنة في حقل statusId: code (ACTIVE / DELETED) — ليس id.

---

## A6 — دورة الحالة (Status Lifecycle)

لا ينطبق — ENTITY-DEMO-001 بحالتين فقط (ACTIVE, DELETED)، وهذا القسم
يُحذف عند حالتين أو أقل (SRS §A6 threshold: > 2 لعرض مخطط الانتقال).
الانتقال الوحيد (ACTIVE → DELETED عبر RULE-DEMO-004) موثّق بالكامل
في A4 دون الحاجة لمخطط منفصل.

---

## A7 — تبعيات الموديولات (Module Dependencies)

None — لا كيانات مُستهلَكة من موديولات أخرى (لا يوجد موديول آخر في
هذه المنصة بعد)، ولا تكاملات خارجية. لا XM Candidates لهذا الموديول.

---

# ══════════════════════════════════════════════════════════
# PART B — SCREEN SPECIFICATIONS
# One block per SCR-ID — self-contained for P3 execution
# References PART A by ID — never redefines artifacts
# ══════════════════════════════════════════════════════════

> **قاعدة PART B الإلزامية:** كل block يشير لـ PART A بالـ ID فقط.

---

## SCR-DEMO-001 — ملاحظاتي (My Notes)

---

### B1 — تعريف الشاشة (Screen Definition)

| البند | القيمة |
|---|---|
| **SCR-ID** | SCR-DEMO-001 |
| **اسم الشاشة** | ملاحظاتي (My Notes) |
| **UI Pattern** | PATTERN-2 — Inline / Side Drawer |
| **Pattern Reason** | Content Shape = لا سطور متكررة (line-items) ولا تسلسل هرمي — المعيار الافتراضي "غير ذلك" في 5.8.2 يعيّن PATTERN-2 |
| **SCR-ID Scope** | ONE SCR-ID covers: Unified (list + inline create/edit via Side Drawer) |
| **Container Pattern** | SIDE_DRAWER — P3 يحدد أسماء المكوّنات في F1 |
| **ENTITY-ID** | ENTITY-DEMO-001 |
| **وظيفة الشاشة** | عرض قائمة ملاحظات المستخدم النشطة + إنشاء/تعديل/حذف عبر Side Drawer |
| **المستخدمون** | المستخدم المصادَق عليه (owner) فقط — لا أدوار أخرى |
| **الموضع في النظام** | DEMO ← ملاحظاتي |
| **روابط من** | نقطة الدخول الرئيسية للموديول (لا شاشة سابقة) |
| **روابط إلى** | لا شاشات إضافية — كل التفاعل داخل هذه الشاشة الموحّدة |

**UI Structure Decision block (P2-RULE-4, PATTERN-2):**

| Content Shape | Interaction | Pattern | Reason |
|---|---|---|---|
| لا سطور متكررة، لا تسلسل هرمي | Side Drawer | PATTERN-2 | كيان بسيط (عنوان + محتوى) — لا رأس/سطور ولا هرمية تستدعي PATTERN-1 أو PATTERN-3 |

**List View (جزء من B1 لهذا النمط — B2 لا ينطبق على PATTERN-2، محذوف):**

| اسم الحقل المعروض | المصدر | ملاحظات |
|---|---|---|
| title | ENTITY-DEMO-001 → A3 | عمود العنوان الرئيسي في القائمة |
| updatedAt | ENTITY-DEMO-001 → A3 | لعرض آخر تعديل، الأحدث أولاً افتراضياً |

القائمة تعرض افتراضياً الملاحظات المملوكة للمستخدم الحالي حيث
`statusId = ACTIVE` فقط (RULE-DEMO-004)؛ لا فلاتر بحث إضافية — أداة
بسيطة، انظر business-policies-demo.md SCOPE EXCEPTIONS.

---

### B3 — مواصفة الإدخال (Input Specification)

#### حقول شاشة الإدخال (Side Drawer)

| اسم الحقل | نوع الحقل | إلزامي | المصدر | ملاحظات |
|---|---|---|---|---|
| title | نص | نعم | ENTITY-DEMO-001 → A3 | RULE-DEMO-001 |
| content | نص متعدد الأسطر | لا | ENTITY-DEMO-001 → A3 | RULE-DEMO-002 |

statusId, ownerUserId, والحقول التدقيقية (audit fields) غير معروضة في
الإدخال — تُدار من الخادم (server-managed)، ليست جزءاً من DTO الإدخال.

#### الأزرار والإجراءات

| الزر | الإجراء | RULE-IDs المطبَّقة |
|---|---|---|
| حفظ (New) | POST | RULE-DEMO-001, RULE-DEMO-002 |
| حفظ (Edit) | PUT | RULE-DEMO-001, RULE-DEMO-002, RULE-DEMO-003, RULE-DEMO-005 |
| إلغاء | إغلاق الـ Drawer — بدون حفظ | — |
| حذف | DELETE (soft) | RULE-DEMO-003, RULE-DEMO-004 |

#### قواعد الإدخال المطبَّقة

| RULE-ID | الشرط | *(التفاصيل في A4)* |
|---|---|---|
| RULE-DEMO-001 | عند كل حفظ (إنشاء/تعديل) | ← see A4 |
| RULE-DEMO-002 | عند كل حفظ (إنشاء/تعديل) | ← see A4 |
| RULE-DEMO-003 | عند القراءة/التعديل/الحذف | ← see A4 |
| RULE-DEMO-005 | عند التعديل | ← see A4 |

---

### B4 — الصلاحيات (Permissions)

| الشاشة | عرض (VIEW) | إنشاء (CREATE) | تعديل (UPDATE) | حذف (DELETE) |
|---|---|---|---|---|
| SCR-DEMO-001 | R1 | R1 | R1 | R1 |

> R1 = OWNER (المستخدم المصادَق عليه، على ملاحظاته الخاصة فقط —
> RULE-DEMO-003). لا يوجد دور إداري/ثانٍ في نطاق هذا الموديول
> (module-registry-demo.md: لا أدوار متعددة مذكورة في الطلب).
> VIEW = gateway: يمنح الوصول للقائمة وفتح الـ Drawer (read mode).
> لا عمود "تصدير" — لا ميزة تصدير مطلوبة في الطلب.

**Security Seed Data:**
```
SEC_PAGES  : INSERT — page_code = DEMO_NOTES, parent_id_fk = DEMO_ROOT
PERMISSIONS: INSERT × 4 — PERM_DEMO_NOTES_VIEW / CREATE / UPDATE / DELETE
```

---

### B5 — الواجهات البرمجية (Functional APIs)

> **Stack Rule (CORE-8 / STACK-1):** REST conventions لـ
> BACKEND_STACK = SPRING_BOOT_JAVA. مسار موحّد:
> `/api/v1/demo/notes` (platform-standards.md API CONVENTIONS).

| API-ID | العملية | HTTP | المسار | المدخلات | المخرجات | RULE-IDs |
|---|---|---|---|---|---|---|
| API-DEMO-001 | إنشاء | POST | /api/v1/demo/notes | title, content? | الملاحظة كاملة | RULE-DEMO-001, RULE-DEMO-002 |
| API-DEMO-002 | قائمة (بحث) | GET | /api/v1/demo/notes | page, size | قائمة ملاحظات المالك (ACTIVE فقط) | RULE-DEMO-003, RULE-DEMO-004 |
| API-DEMO-003 | جلب بالمعرّف | GET | /api/v1/demo/notes/{id} | noteId | الملاحظة كاملة | RULE-DEMO-003, RULE-DEMO-004 |
| API-DEMO-004 | تعديل | PUT | /api/v1/demo/notes/{id} | title?, content? | الملاحظة محدَّثة | RULE-DEMO-001, RULE-DEMO-002, RULE-DEMO-003, RULE-DEMO-005 |
| API-DEMO-005 | حذف (soft) | DELETE | /api/v1/demo/notes/{id} | noteId | تأكيد | RULE-DEMO-003, RULE-DEMO-004 |

---

*(SCR block واحد فقط لهذا الموديول — لا شاشات إضافية.)*

---

# ══════════════════════════════════════════════════════════
# STANDALONE — بعد PART B
# ══════════════════════════════════════════════════════════

---

## Permissions Summary & Registry Update

| الشاشة | عرض (VIEW) | إنشاء (CREATE) | تعديل (UPDATE) | حذف (DELETE) |
|---|---|---|---|---|
| SCR-DEMO-001 (ملاحظاتي — Unified) | R1 | R1 | R1 | R1 |

> R1 = OWNER — انظر B4.

---

### Registry Update — MODE 1

```
## REGISTRY UPDATE — 2026-09-07
────────────────────────────────────────────────────────────────
Source Mode    : MODE 1 (P1 — SRS)
Feature Code   : DEMO-001
DBS-ID         : —  (assigned by P2)
Plan ID        : —  (assigned by P3.1)
────────────────────────────────────────────────────────────────
New Entities   : ENTITY-DEMO-001 (PRIVATE)
New Tables     : —  (P2's decision)
New Lookups    : NOTE_STATUS
New Screens    : SCR-DEMO-001
New APIs       : API-DEMO-001 through API-DEMO-005
New Rules      : RULE-DEMO-001 through RULE-DEMO-005
XM-IDs Open    : —  (none — no cross-module dependencies)
OQ-IDs Open    : None
Gate Status    : PASSED ✓
Next Action    : Trigger MODE 1.5 — Database Governance Engine (P2)
────────────────────────────────────────────────────────────────
```

---

## OQ Log — سجل الأسئلة المفتوحة

```
## OPEN QUESTIONS LOG — DEMO — 2026-09-07
─────────────────────────────────────────────────────────────────────
OQ-ID  │ Question                  │ Status   │ Raised  │ Resolved │ Escalation
───────┼───────────────────────────┼──────────┼─────────┼──────────┼───────────────
(none) │ —                         │ —        │ —       │ —        │ —
─────────────────────────────────────────────────────────────────────
None — the brief was unambiguous at every field/rule/screen decision
above (Zero-Question Protocol, §5.4.1); every judgment call made
without a stated answer is instead recorded as an AUTO-DECISION in
module-registry-demo.md or inline in this file, not left as an OQ.
```

---
*نهاية الوثيقة | End of srs-demo.md*
*Governed by: SRS Governance Engine (Project 1)*
*Feature Code: DEMO-001 | Version: 1.0*
*Structure: PART A (Module Foundation) + PART B (Screen Specifications)*
*Next Mode: MODE 1.5 — Database Governance Engine (Project 2)*
