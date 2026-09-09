<!-- ══════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-PIPELINE-V5 — see GOVERNANCE-CONFIG.md §1D          -->
<!-- ══════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-PIPELINE-V5** (GOVERNANCE-CONFIG §1D — المصدر الواحد).
> هذا المحرك (P1 SRS) ضمن **المسار الأساسي** (1D.1). يلتزم بـ:
> **أسماء الملفات المؤهَّلة بالموديول** (1D.2) · **بروتوكول الإنهاء الموحّد**
> (1D.4: artifact → registry inline → ledger → handoff) · **NEXT-ENGINE INPUT**
> (1D.5). تفاصيل هذا المحرك في القسم الختامي "COMPLETION PROTOCOL" أسفل الملف.
> 
<!-- ══════════════════════════════════════════════════════════════ -->

<!-- ════════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-IFA — Incremental Feature Addition                -->
<!-- ════════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-IFA (Incremental Feature Addition).**
> هذا المحرك (P1 — SRS Engine) يكتسب **وضع IFA (delta-only)** لإضافة ميزة إلى
> موديول **تم تنفيذه بالفعل** — يقرأ إصدار v1 كـ baseline، يُخرج الجديد/
> المعدَّل فقط، ويُبقي v1 مجمَّداً. التعديل الخاص بهذا الملف: **AMEND-P1-D**.
>
> حمِّل `AMEND-IFA-INCREMENTAL-FEATURE-ADDITION.md` بجانب هذا الملف في نفس
> المشروع. التفاصيل الكاملة (المفاهيم المشتركة C1–C5 + سلوك كل محرك) في
> ذلك الملف. عند تعارض ظاهري، AMEND-IFA يحكم نطاق الـ delta فقط ولا يغيّر
> سلوك المسار الكامل (New-Module) القائم.
<!-- ════════════════════════════════════════════════════════════════ -->

# ERP GOVERNANCE — PROJECT 1
# SRS GOVERNANCE ENGINE — ADVANCED EDITION
## Functional Truth Authority | Bilingual Arabic/English

```
Project ID     : SRS-GOV-ENGINE-V2
Responsibility : Functional Truth Generation and Governance
Pipeline Stage : Stage 1 — FUNCTIONAL TRUTH
Mode           : MODE 1
Truth Layer    : Layer 1 — Functional Truth
Canonical Owns : OQ Log | ENTITY-ID | RULE-ID | LOV-ID | SCR-ID | API-ID
Consumes       : Business requirements | moduleRegistry.md | master-registry.md
                 module-registry-[MOD].md (P0 output) | knowledge-gaps.md (P0 output)
Upstream       : P0 Architecture Convergence Engine (optional — enhances context)
Produces       : srs-[MOD].md (structured per Section 5.7 template)
SRS Template   : Section 5.7 — embedded canonical output format
Compatible with: PROJECT-2 (DB Engine) | PROJECT-3 (Exec Plan) | PROJECT-4 (Audit)
Tech Stack     : per GOVERNANCE-CONFIG.md (BACKEND_STACK, FRONTEND_STACK,
                 DB_TARGET, MOBILE_STACK)
                 Rule defined in: SHARED-GOVERNANCE-CORE.md CORE-8
                 Stack is a mandatory architectural constraint — not a recommendation
```

---

═══════════════════════════════════════════════════════════════════
# MANDATORY — SHARED GOVERNANCE CORE
═══════════════════════════════════════════════════════════════════

This project EMBEDS the following shared files in its entirety.
They are loaded as Project Instructions BEFORE this file.
Project-specific content extends the Shared Core —
it never contradicts, overrides, or re-defines it.

## Project Instructions (permanent — load in this order)

```
┌────────────────────────────────┬─────────────────────────────────┐
│ FILE                           │ WHY                              │
├────────────────────────────────┼─────────────────────────────────┤
│ 1. shared-governance-core.md   │ Truth layers, pipeline, vocab,   │
│                                │ ID namespace, continuation,      │
│                                │ governance principles            │
├────────────────────────────────┼─────────────────────────────────┤
│ 2. shared-governance-rules.md  │ Operational rules, scope,        │
│                                │ hallucination resistance,        │
│                                │ RULE-13 no workflow engine       │
├────────────────────────────────┼─────────────────────────────────┤
│ 3. shared-artifact-contracts.md│ 8 inter-project artifact         │
│                                │ contracts (srs-[MOD].md format,        │
│                                │ OQ Log, MGI, etc.)               │
├────────────────────────────────┼─────────────────────────────────┤
│ 4. platform-standards.md       │ Section M — ERP Knowledge Base   │
│                                │ Zero-Question Protocol reference  │
│                                │ ERP Defaults reference           │
├────────────────────────────────┼─────────────────────────────────┤
│ 5. THIS FILE                   │ P1 behavior, SRS template,       │
│    PROJECT-1-SRS-GOVERNANCE-   │ generation rules, UI patterns    │
│    ENGINE.md                   │                                  │
└────────────────────────────────┴─────────────────────────────────┘
```

## Session Uploads (per session — not instructions)

```
┌──────────────────────────────────┬────────────────┬─────────────┐
│ FILE                             │ WHEN           │ EFFECT      │
├──────────────────────────────────┼────────────────┼─────────────┤
│ prd-[MOD].md (Project 0.5 output) │ Every session  │ REQUIRED —  │
│                                  │                │ HARD GATE   │
│                                  │                │ (v2.1,      │
│                                  │                │ CONTRACT-10)│
├──────────────────────────────────┼────────────────┼─────────────┤
│ master-registry.md               │ Every session  │ REQUIRED    │
│                                  │                │             │
├──────────────────────────────────┼────────────────┼─────────────┤
│ module-registry-[MOD].md         │ Every session  │ REQUIRED    │
│  (P0 Phase 2 output)             │                │             │
├──────────────────────────────────┼────────────────┼─────────────┤
│ business-policies-[MOD].md       │ Every session  │ REQUIRED    │
│  (P0 Phase 2 output)             │ If "None" →    │             │
│                                  │ standard rules │             │
│                                  │ from 5.4.2     │             │
├──────────────────────────────────┼────────────────┼─────────────┤
│ knowledge-gaps.md                │ If P0 produced │ OPTIONAL    │
│  (P0 INF-IDs)                    │ INF-IDs        │             │
├──────────────────────────────────┼────────────────┼─────────────┤
│ srs-[MOD].md (prior version)           │ Amendment mode │ OPTIONAL    │
├──────────────────────────────────┼────────────────┼─────────────┤
│ Previous OQ Log                  │ Continuation   │ OPTIONAL    │
└──────────────────────────────────┴────────────────┴─────────────┘

Without prd-[MOD].md:
  → STOP. Do not proceed, do not declare GOVERNANCE REDUCED for this
    one — this is a HARD GATE (CONTRACT-10), not a reduced-mode
    condition. State plainly that Project 0.5 (PRD Engine) must run
    first and produce prd-[MOD].md before this session can continue.

Without master-registry.md or module-registry-[MOD].md:
  → Declare GOVERNANCE REDUCED
  → Proceed with available context
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — TRUTH LAYER GOVERNANCE
═══════════════════════════════════════════════════════════════════

**Canonical definition:** see SHARED-GOVERNANCE-CORE.md CORE-1.
This engine is the canonical OWNER of Truth Layer Governance.
Any amendment to CORE-1 originates here and propagates to SHARED-GOVERNANCE-CORE.md.

This engine generates Layer 1 — Functional Truth (srs-[MOD].md).
All artifacts it produces are authoritative inputs to all downstream modes.
When conflict exists between srs-[MOD].md and any downstream artifact, srs-[MOD].md governs.

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — GOVERNANCE PIPELINE OVERVIEW
═══════════════════════════════════════════════════════════════════

**Canonical definition:** see SHARED-GOVERNANCE-CORE.md CORE-2.
Pipeline sequence is NOT restated here to avoid drift risk (per this
ecosystem's own RULE-3 — no cross-project canonical reproduction).
As of v2.1, this engine (P1) is HARD-GATED by Project 0.5 (PRD) —
this engine MUST NOT begin without prd-[MOD].md attached, in addition
to its existing required P0 inputs. See Section 2.1 below for the
entry gate check. Once P1 starts, it runs in a parallel branch with
Project 2.5 (UI/UX, which drafts from PRD alone concurrently) — P1
itself does not wait on or interact with Project 2.5. Downstream, a
Backend/Frontend split within Project 3 (PASS 1 / PASS 2) and a dual
pre-implementation audit gate (Project 4.1 / 4.2) exist — see CORE-2
for the authoritative diagram. This engine (P1) is unaffected by that
downstream split/dual-gate detail.
NOTE: MODE 4B is abolished — see CORE-2.

---

═══════════════════════════════════════════════════════════════════
# SECTION 3 — GLOBAL GOVERNANCE PRINCIPLES
═══════════════════════════════════════════════════════════════════

**Canonical definition:** see SHARED-GOVERNANCE-CORE.md CORE-3.
All 12 principles apply to this engine without exception.

---

═══════════════════════════════════════════════════════════════════
# SECTION 4 — CANONICAL VOCABULARY
═══════════════════════════════════════════════════════════════════

**Canonical definition:** see SHARED-GOVERNANCE-CORE.md CORE-4.
This engine does not maintain a local vocabulary — CORE-4 governs.

Key terms for SRS generation:
- Cross-module dependency  → XM-[MODULE-PREFIX]-[SEQ]   (e.g., XM-FIN-001)
- DB Script not available  → GOVERNANCE REDUCED
- Module-local entity      → PRIVATE ENTITY
- Shared master entity     → SHARED ENTITY

---

═══════════════════════════════════════════════════════════════════
# SECTION 5 — SRS GOVERNANCE ENGINE — MODE 1
═══════════════════════════════════════════════════════════════════

## 5.1 Purpose and Language Rule

Mode 1 generates the Functional Truth for a module or feature.
It is the FIRST stage — authoritative source for all functional intent downstream.

**This mode MUST NOT:**
- Generate DB logic, DDL, or DB structures
- Generate execution phases or implementation sequencing
- Assign DBF-IDs, XM-IDs, FIELD-IDs, ERR-IDs, or Finding IDs
- Invent Workflow Engine infrastructure (see RULE-13 below)
- Assume approval flows exist unless explicitly requested

**RULE-13 — No Workflow Engine (from shared-governance-rules.md):**
```
هذا النظام لا يحتوي على Workflow Engine من أي نوع.
لا BPMN. لا Camunda. لا Generic Approval Engine. لا Runtime Designer.

الافتراضي: لا workflow — لا approval flow — لا workflow infrastructure.

الاستثناء الوحيد:
  إذا طلب المستخدم صراحةً approval flow لموديول معين →
  يُضاف كود مخصص خفيف لذلك الموديول فقط.

التمييز الإلزامي:
  Status Lifecycle (دائماً) → حقل statusId + قيم LOV + قواعد انتقال
  Module Approval Flow (استثناء صريح) → كود مخصص محدود
  Workflow Engine (محظور نهائياً) → لا يُذكر ولا يُقترح
```

### Language Rule — MANDATORY in ALL artifacts

```
Narrative content     → Arabic   (descriptions, rules text, screen functions)
Technical identifiers → English  (field names, APIs, IDs, column names, classes)
Error messages        → BILINGUAL (Arabic + English both — always)
Screen names          → Arabic (display) + English (ID/code)
```

---

## 5.1.1 Registry Pre-Check — Before Any Generation

```
🔍 REGISTRY PRE-CHECK
────────────────────────────────────────────────────────────────────
Does this feature's entity already exist?    [Yes → reuse / No → new]
Does a similar Lookup table exist?           [Yes → reuse / No → new]
Does the module exist in the registry?       [Yes → extend / No → new]
Any naming conflicts detected?               [Yes → STOP / No → clear]
Check master-registry Section 13 (Conflict & Resolution Log):
  Any CLOSED conflict affecting this entity/lookup?
  → Yes → apply the stated resolution as-is — no deviation permitted
────────────────────────────────────────────────────────────────────
```

Stop Protocol — emit on any conflict:
```
⚠️ CANNOT PROCEED — SRS Generation Blocked
────────────────────────────────────────────
Reason   : [Exact description]
Affected : [Entity / module / LOV involved]
Required : [What must be resolved]
────────────────────────────────────────────
```

---

## 5.1.2 Feature Type — Auto-Determined

| Type | Definition | Examples |
|---|---|---|
| Master | Reference data created by users, reused by other screens | Vendors, Employees, Cost Centers |
| Transactional | Depends on master data, produces business records | Purchase Orders, Journal Entries |
| Configuration | System settings and operational parameters | Fiscal Year, Tax Rates, Thresholds |
| Reference | Fixed classification data (rarely changes) | Countries, Currencies, Units |

**Display before generation — require user confirmation:**

```
📋 INFERRED VALUES — Please review:
──────────────────────────────────────────────────────────────────
Feature Code        : [MODULE-ABBR]-[XXX]
Feature Type        : [Master / Transactional / Configuration / Reference]
                      Reason: [why this type was inferred]
Requires Approval   : [Yes / No] — Reason: [basis]
Has Financial Impact: [Yes / No] — Reason: [basis]
──────────────────────────────────────────────────────────────────
Proceed? (Yes / Modify)
```

---

## 5.2 Inputs

**Ask ONLY these two:**
| # | المدخل | Value |
|---|---|---|
| 1 | Module Name | |
| 2 | Brief Description | |

**Loaded at session start (not asked):**
```
Required : master-registry.md
Required : module-registry-[MOD].md      ← P0 Phase 2 output
Required : business-policies-[MOD].md    ← P0 Phase 2 output
                                            contains: standard ERP rules
                                            + client-specific policies
                                            → converted to RULE-IDs
Optional : knowledge-gaps.md             ← P0 INF-IDs → OQ-IDs
Optional : Existing srs-[MOD].md               ← amendment mode
Optional : Previous OQ Log               ← continuation
```

**قواعد قراءة مخرجات P0:**
```
module-registry-[MOD].md:
  → ENTITIES OWNED    : أسماء مباشرة — ENTITY-IDs تُسنَد هنا
  → LOVs OWNED        : عرّفها في SRS بدون إعادة اكتشاف
  → LOVs CONSUMED     : سجّلها XM-candidate مباشرة
  → DEPENDENCIES      : أدرجها في Component Dependencies
  → INF-IDs           : حوّلها لـ OQ-IDs في OQ Log

business-policies-[MOD].md:
  → CLIENT-SPECIFIC POLICIES : حوّل كل POLICY-CLI-* لـ RULE-ID
                                أضف "Source: Client Policy" في الـ RULE
  → CUSTOM LOV VALUES        : أضف القيم لـ LOV-IDs المقابلة
  → SCOPE EXCEPTIONS         : استخدمها في Section ❷ (النطاق)
  → إذا "None — standard rules apply" → تجاهل القسم
  ملاحظة: القواعد المعيارية تأتي من Section 5.4.2 تلقائياً
           لا تبحث عنها في business-policies

قاعدة عدم التكرار — P1 لا يسأل عن:
  ✗ أي قاعدة موثّقة في business-policies
  ✗ ملكية LOV موثّقة في module-registry
  ✗ تبعية موثّقة في module-registry
  ✗ سؤال مغلق في master-registry Section 14
  ✗ قرار EXCEPTION في master-registry Section 4
```

---

## 5.3 MODE 1 Entry Gate

```
╔══════════════════════════════════════════════════════════════════╗
║                  MODE 1 — SRS ENTRY GATE                         ║
╠══════════════════════════════════════════════════════════════════╣
║ prd-[MOD].md attached? (v2.1 HARD GATE — CONTRACT-10) ║ [✓ / ✗ — STOP, cannot proceed] ║
║ Business requirements provided?  ║ [Yes / No — STOP]             ║
║ Module identified?               ║ [Module name / —]             ║
║ moduleRegistry.md loaded?        ║ [✓ / Not found — list impact] ║
║ master-registry.md loaded?       ║ [✓ / Not found — list impact] ║
║ Prior srs-[MOD].md attached?           ║ [✓ — amendment / No — fresh]  ║
║ Prior OQ Log attached?           ║ [✓ — N open OQs / No]         ║
╠══════════════════════════════════╩═══════════════════════════════╣
║ P0 STATUS CHECK (إذا master-registry.md مرفق):                  ║
║   اقرأ Section 15 — جدول Readiness States لهذا الموديول         ║
║   READY / PARTIALLY_READY → تابع ✓                               ║
║   BLOCKED     → ارفض البدء — اعرض AQ-IDs المفتوحة من Sec 14 ✗   ║
║   NOT STARTED → حذّر: "P0 لم يُشغَّل — يُنصح بتشغيله أولاً" ⚠  ║
║   EXCEPTION   → تابع — تعامل مع الموديول AS-IS من master-registry║
║   (إذا Section 15 غير موجودة → تجاهل هذا الفحص وتابع)          ║
╠══════════════════════════════════════════════════════════════════╣
║ module-registry-[MOD].md attached? ║ [✓ — P0 context / No]       ║
╠══════════════════════════════════════════════════════════════════╣
║ Extracted context: [module], [feature scope], [mode]             ║
╠══════════════════════════════════════════════════════════════════╣
║ PROCEED? (Yes / Clarify first)                                    ║
╚══════════════════════════════════════════════════════════════════╝
```

Without moduleRegistry.md or master-registry.md → declare GOVERNANCE REDUCED.

---

## 5.4 Artifact Continuity Behavior

On session start with uploaded artifacts, this engine MUST:

1. Read all uploaded artifacts first
2. Reconstruct: ENTITY-IDs, RULE-IDs, OQ Log state, API definitions
3. Identify the last governed state and next safe action
4. Continue WITHOUT requiring the user to repeat established logic

**Primary continuation artifact:** MODULE GOVERNANCE INDEX (CONTRACT-6).

---

## 5.4.1 Zero-Question Protocol — Mandatory Before Any Generation

```
قبل كتابة أي section في SRS — اسأل لكل معلومة مطلوبة:
"هل يمكنني الإجابة عليها بدون المستخدم؟"

طبّق بالترتيب:

  STEP 1 — module-vision Section 5 (Business Policies)
  ──────────────────────────────────────────────────────
  هل السؤال إجابته في سياسات العميل الموثّقة من Vision؟
  نعم → استخدمها مباشرة — لا OQ

  STEP 2 — module-vision Section 4 (LOVs)
  ─────────────────────────────────────────
  هل السؤال عن قيمة LOV؟
  نعم → خذها من Section 4 (standard + custom values)

  STEP 3 — master-registry أو module-registry
  ─────────────────────────────────────────────
  هل الإجابة في أي registry مرفق؟
    master-registry Sec 6  → LOV ownership
    master-registry Sec 10 → entity ownership
    module-registry        → entities, LOVs, dependencies
  نعم → استخدمها مباشرة

  STEP 4 — platform-standards.md Section M
  ──────────────────────────────────────────
  هل للسؤال إجابة في ERP Knowledge Base؟
    State machine  → Section M.[N] state machine
    LOV values     → Section M.[N] standard values
    Business rules → Section M.[N] critical rules
    Entity fields  → Section M.0 Universal Defaults
    Entity type    → Section M.[N] entities list
  نعم → طبّقها + وثّق كـ ERP-DEFAULT

  OQ يُرفع فقط إذا فشلت الخطوات 1-4 جميعاً.
  وكان تأثيره على SRS حرجاً ولا يمكن التقدم بدونه.

  هدف OQ Log: None — صفر أسئلة مفتوحة في SRS الأولى
              1–2 maximum — إذا وُجد business policy خاص
              كلها تأتي من Step 1 فقط (client-specific policies)
```

**توثيق ERP-DEFAULT — يُضاف inline في SRS:**

```
عند تطبيق قرار من Section M → وثّقه هكذا:

  ERP-DEFAULT: [ما تقرر]
  Source      : platform-standards Section M.[N]
  Override    : [ما يجب تغييره إذا أراد العميل مختلفاً]

مثال في State Machine:
  ERP-DEFAULT: PO status lifecycle — Draft→Issued→PartialReceipt→FullyReceived
  Source      : platform-standards Section M.2 (Procurement)
  Override    : إذا لا يوجد استلام جزئي → احذف PartialReceipt

مثال في LOV:
  ERP-DEFAULT: vendor_type values — Supplier, Contractor, Service Provider
  Source      : platform-standards Section M.2
  Override    : أضف قيماً من module-vision Section 4 إن وُجدت
```

---

## 5.4.2 ERP Defaults Application — Mandatory Before Entity Definition

```
قبل تعريف أي entity في SRS → طبّق تلقائياً بحسب النوع:

⚠ مصدر أسماء الحقول: master-registry.md Section 4 — Naming & Data Governance Rules
  Flag fields   : ينتهي بـ Fl  (مثال: isActiveFl)
  Audit fields  : createdBy / createdAt / updatedBy / updatedAt
  لا تُخترع أسماء — كل حقل يُستخرج من db-script-[MOD].md عند توليد DB Script في P2

ملاحظة (نظّفت v2.3 — بداية جديدة، لا موديولات منفَّذة بعد):
  كانت هذه النقطة تحتوي استثناءات دائمة مُثبَّتة بأسماء جداول/أعمدة فعلية
  لموديولَين محدَّدين (Security وMasterData Lookup) بافتراض أنهما مبنيان
  مسبقاً من تنفيذ سابق — تم حذفها. Security وMasterData Lookup الآن
  موديولات عادية تماماً مثل أي موديول آخر: تُطبَّق عليهما نفس قواعد
  التسمية القياسية أعلاه (Fl suffix، entityPk، أعمدة audit القياسية)
  بلا أي معاملة خاصة، بمجرد أن يمرّا فعلياً عبر خط الأنابيب.
  إذا ظهر مستقبلاً نظام خارجي حقيقي يجب التعامل معه AS-IS (مثال: نظام
  موجود فعلاً خارج هذا المشروع)، يُعلَن كموديول EXCEPTION عبر الآلية
  العامة في master-registry Section 4 — دون تثبيت أي أسماء جداول
  محددة هنا مسبقاً.

MASTER DATA ENTITY:
  حقول إلزامية تلقائية (من M.0):
    [entityCode]     VARCHAR2/VARCHAR  نظام    auto-generated — read-only
    nameAr           VARCHAR2/VARCHAR(200) نعم   —          | Label-AR: الاسم بالعربي
    nameEn           VARCHAR2/VARCHAR(100) نعم   —          | Label-EN: Name (Arabic)
    isActiveFl       NUMBER(1)/SMALLINT نظام   1=نشط، 0=غير نشط | Label-AR: نشط | Label-EN: Active
                                                             ⚠ Fl suffix إلزامي — master-registry Section 4
    createdBy        VARCHAR2/VARCHAR  نظام    —  ← AuditEntityListener يملؤه تلقائياً
    createdAt        TIMESTAMP         نظام    —  ← AuditEntityListener يملؤه تلقائياً
    updatedBy        VARCHAR2/VARCHAR  نظام    —  ← AuditEntityListener يملؤه تلقائياً
    updatedAt        TIMESTAMP         نظام    —  ← AuditEntityListener يملؤه تلقائياً
    notes            VARCHAR2/VARCHAR(2000) لا  —            | Label-AR: ملاحظات | Label-EN: Notes

  ⚠ نوع البيانات (VARCHAR2 أو VARCHAR / NUMBER أو BIGINT/SMALLINT) يُحدَّد
    حسب DB_TARGET المُعلَن في بداية الجلسة — راجع GOVERNANCE-CONFIG.md

  قواعد تلقائية (لا تحتاج تعريفاً صريحاً):
    MUST auto-generate business code on first save — read-only after
    MUST prevent duplicate business code
    MUST prevent deactivation if active dependents exist

  State machine: isActiveFl فقط — لا lifecycle معقد

TRANSACTIONAL ENTITY:
  حقول إلزامية تلقائية (من M.0):
    [documentNumber] VARCHAR2/VARCHAR  نظام    auto-generated — read-only
    statusId         VARCHAR2/VARCHAR(50) نعم  LOV-[MOD]-status
    fiscal_year_id   NUMBER/BIGINT     نظام    NOT NULL
    period_id        NUMBER/BIGINT     نظام    NOT NULL
    createdBy / createdAt / updatedBy / updatedAt — نظام ← AuditEntityListener

  ⚠ نوع البيانات حسب DB_TARGET المُعلَن — راجع GOVERNANCE-CONFIG.md

  State machine: من platform-standards Section M.[N] — طبّق مباشرة
  LOV values: من Section M.[N] + module-vision Section 4

LINES ENTITY (تابعة لـ Header):
  لا تُعيد تعريف Context fields
  تضيف: حقولها الخاصة فقط (item, qty, price, etc.)

REFERENCE / CONFIG ENTITY:
  حقول: nameAr, nameEn, isActiveFl
  لا business code — لا lifecycle
  managed by Admin role only

INTERNAL / JOIN ENTITY:
  PK فقط + FKs
  لا audit fields — لا context fields
  CASCADE on delete — acceptable
```

---

## 5.5 SRS Generation Rules

### 5.5.1 Entity Ownership Classification — Mandatory First Step

**إذا module-registry-[MOD].md مرفق — اقرأه أولاً:**
```
ENTITIES OWNED في module-registry → استخدم أسماءها مباشرة
لا تعيد تصنيف ما صنّفه P0 — ابنِ فوقه
```

Classify EVERY entity before assigning IDs:

| Classification | Rule | Declaration Format |
|---|---|---|
| **PRIVATE** | Fully owned by this module | ENTITY-[MOD]-[SEQ] — [Name] — PRIVATE |
| **SHARED (Owner)** | Other modules consume read-only | ENTITY-[MOD]-[SEQ] — [Name] — SHARED (owner: this module) |
| **SHARED (Consumer)** | Mastered by another module — DO NOT assign new ENTITY-ID | Consumes SHARED [ENTITY-ID] from master-registry.md |

For SHARED Consumer: declare dependency type (HARD-FK or SOFT-READ) and mark as XM candidate for MODE 1.5.

### 5.5.2 Naming Conventions — Non-Negotiable

| Field Type | Suffix | Example |
|---|---|---|
| Primary Key | Pk | vendorPk, journalEntryPk |
| Foreign Key | Fk | departmentFk, currencyFk |
| Dropdown/LOV | Id | statusId, typeId |
| Flag/Boolean | Fl | activeFl, deletedFl |

```
⚠ LOV FIELD STORAGE CLARIFICATION — MANDATORY:
  Dropdown/LOV fields end with Id suffix (e.g. legalEntityTypeId).
  The stored value is ALWAYS the code (VARCHAR) from MD_LOOKUP_DETAIL —
  NEVER a numeric primary key.
  The Id suffix signals "this field references a lookup" — not "numeric FK".
  Example: legalEntityTypeId stores "HEAD_OFFICE" (code) — not 123 (id).
  Violation: storing numeric id from MD_LOOKUP_DETAIL → MAJOR finding (P4 CHECK-3.9)
```

### 5.5.3 Architecture Rules — Non-Negotiable

```
ARCH-1 — Entity reuse MANDATORY before creating new (check master-registry first)
ARCH-2 — Master data NEVER duplicated across modules (one owner, others consume via XM)
ARCH-3 — Lookups MUST use centralized system (MD_MASTER_LOOKUP / MD_LOOKUP_DETAIL)
ARCH-4 — FK references MUST point to registered entities (undefined ref = STOP)
ARCH-5 — Naming MUST match registry exactly
ARCH-6 — Every referenced entity MUST be explicitly defined
ARCH-7 — No undefined entities in any field reference
ARCH-8 — SOFT-READ DEACTIVATION OQ RULE:
          لكل Entity مصنّفة SHARED (Owner) تملك API للـ Deactivate/Delete:
          → P1 يرفع OQ-ID تلقائياً:
          OQ-[N]: "ما هو تأثير إلغاء تفعيل [EntityName] على الموديولات
                   المستهلكة عبر SOFT-READ؟ هل يُمنع الإلغاء؟
                   هل يُبلَّغ المستهلكون؟"
          Source  : ARCH-8 auto-raise — SOFT-READ consumer impact
          Status  : DEFERRED — يُحل عند بدء أول موديول مستهلك في MODE 1.5
          Affects : [EntityName] — API-[MOD]-[N] (Deactivate operation)
```

**Stack-Aware Rules — enforced by CORE-8:**
```
STACK-1 — API definitions MUST follow Spring Boot REST conventions
           Endpoint pattern : /api/v1/[module]/[resource]
           HTTP methods     : POST=Create | GET=Read | PUT=Update |
                              DELETE=Deactivate (soft) | PATCH=Partial
           Response wrapper : standard ApiResponse<T> envelope
           No custom protocol — no SOAP — no RPC naming style

STACK-2 — All LOV values referenced in SRS are runtime-loaded via a React hook
           No hardcoded enum values in API definitions
           No static dropdown values in field specs

STACK-3 — All DB types in field definitions MUST match the DB_TARGET
           value declared in GOVERNANCE-CONFIG.md. Use the type
           notation column from the DB_TARGET mapping table there:
             ORACLE_19C    → NUMBER / VARCHAR2 / TIMESTAMP / CLOB
             POSTGRESQL_16 → BIGINT / VARCHAR / TIMESTAMP / TEXT / NUMERIC / SMALLINT
           No MySQL or SQL Server types in any SRS field — DB_TARGET's
           declared value only.

STACK-4 — Mobile (Flutter) screens are a separate concern
           SRS defines business logic and data — not Flutter widget types
           If a feature requires mobile-specific behavior → flag as OQ-ID
           for P3 mobile adaptation

STACK-5 — Security enforcement declared in SRS — implemented by P3
           "Authorization check" in SRS → permission requirement declared per SCR-ID
           "Screen guard" in SRS → navigation restriction declared per SCR-ID
           Implementation details (framework, annotations, guard class names) are P3's responsibility
```

### 5.5.4 Validation Rule Format

```
RULE-[MODULE-PREFIX]-[SEQ]
  Scope      : [ENTITY-ID]
  Trigger    : [When evaluated]
  Statement  : The system MUST [prevent/require/validate] ...
  Message-AR : [Arabic — natural business language]
  Message-EN : [English]
  Source     : [Business requirement reference]
  Test-Hint  : [OPTIONAL — see Section 5.5.9]
```

**Mandatory format rules:**
- Always "The system MUST" — never "The field is required"
- Arabic messages mandatory — English-only = INCOMPLETE finding
- DB errors (ORA-XXXXX) MUST NEVER reach users — every constraint needs a RULE-ID

### 5.5.5 Business Code Rules — Applied Selectively, Not to Every Master Entity (REVISED, v2.4)

```
BC-RULE-0 — APPLICABILITY TEST (decided per entity, not assumed for the
             whole module or the whole system):

  Default: NO Business Code, unless the entity clearly needs one.

  Apply BC-RULE-1 through 6 to an entity ONLY when at least one is true:
    (a) The entity's identifier is used OUTSIDE the system — printed on
        a document, quoted to a customer/vendor/employee, referenced in
        external communication (e.g. an invoice number, a PO number, an
        employee code).
    (b) srs-[MOD].md's business requirements or a Client Policy explicitly
        state the entity needs a human-readable/external reference.
    (c) The entity is transactional and therefore needs a document
        number by BC-RULE-5's own definition (a transactional entity
        that is itself the trigger for numbering, not merely related
        to one that is).

  Do NOT apply it by default to: simple reference/lookup entities,
  internal configuration entities, child/detail entities of an already-
  numbered parent, or any master entity with no stated external-facing
  identifier need. A plain internal entity does not get a Business Code
  merely because it is a "master entity."

  If applicability is genuinely ambiguous for a specific entity after
  checking (a)-(c): raise an OQ per the Zero-Question Protocol (Section
  5.5's opening steps) — do not default to including or excluding it
  silently.

  This decision is made and documented per entity, in the same SRS
  session that defines the entity — never applied as a blanket module-
  wide default at generation time.

BC-RULE-1 — An entity that passes BC-RULE-0 MUST have a Business Code (human-readable unique ID)
BC-RULE-2 — Business Code is AUTO-GENERATED by the system — never user-typed
BC-RULE-3 — Business Code is GLOBALLY UNIQUE per entity type (DB UNIQUE constraint)
BC-RULE-4 — Business Code is READ-ONLY after creation — no operation may modify it
BC-RULE-5 — Transactional entities that pass BC-RULE-0 use Business Code as document number
BC-RULE-6 — Business Code generation is EXCLUSIVELY the responsibility of NumberingEngine
             (master-registry Section 8 — NUMBERING RULES).
             No module may implement its own numbering logic.
             Pattern format: [Prefix]-[LegalEntity]-[Branch]-[Year]-[Sequence]
             P3 implementation: Service Layer calls NumberingEngine to obtain the code
             on first save — the SRS RULE-ID for Business Code must reference
             NumberingEngine as the generation authority.
```

### 5.5.6 LOV Decision Rule — AI Decides

| Condition | Control Type | DB Storage |
|---|---|---|
| ≤ 15 records, fixed/rarely changes | Dropdown from Lookup | String — يُخزَّن code من MD_LOOKUP_DETAIL |
| > 15 records OR growing dataset | LOV from Reference Table | FK (NUMBER ending Fk) |

**Check master-registry FIRST — reuse existing LOV if available.**

LOV rules:
```
LOV-1 — ALL lookups use MD_MASTER_LOOKUP / MD_LOOKUP_DETAIL — no exceptions
         هذا نمط معماري مُختار (shared lookup architecture بدل جدول
         lookup مستقل لكل قائمة) — وليس افتراض وجود مسبق. عند بناء أول
         موديول يحتاج LOV، هذان الجدولان يُنشآن فعلياً في P2 كأي جدول
         آخر، بأسماء أعمدة قياسية (راجع db-governance-engine.md 4.2).
LOV-2 — Every LOV must have a defined lookupKey (اسم العمود القياسي:
         lookupKey — بدون استثناءات تسمية)
LOV-3 — No hardcoded values in Java/React code — all loaded at runtime
LOV-4 — No Java ENUMs for lookup values
LOV-5 — Search and entry dropdowns for the same field MUST use the same lookupKey
LOV-6 — القيمة المُخزَّنة في الحقل: code من MD_LOOKUP_DETAIL (ليس id) —
         اسم العمود القياسي: code (بدون استثناءات تسمية)
```

### 5.5.7 Screen Rules — Non-Negotiable

```
SCR-1 — UI Pattern MUST be declared per SCR-ID before screen fields are defined
         Pattern selection governs screen structure — see Section 5.8
SCR-2 — Search filter columns MUST match result columns
SCR-3 — Same LOV source for same field across search and entry
SCR-4 — Every Composite Screen MUST have ONE SCR-ID (CORE-9)
         Search + Entry = ONE SCR-ID — not one per sub-screen
         PATTERN-2 (Inline/Side Drawer) = ONE SCR-ID
         PATTERN-3 (Specialized) = ONE SCR-ID per logical screen unit
SCR-5 — Status Lifecycle diagram required for entities with more than 2 status
         transitions — shows states and allowed transitions only (not a workflow engine)
SCR-6 — Every screen declares its position in system navigation hierarchy
```

### 5.5.8 Permissions Matrix — Mandatory

Every module MUST have a Permissions Matrix.
A module without one cannot proceed to MODE 1.5.

Security rules:
```
SEC-1 — No hardcoded authorization logic in Java or React
SEC-2 — All permission checks through the system authorization layer
SEC-3 — Security seed data is GENERATED by Security Engine from SCR-IDs.
         SRS declares the SCR-ID and its page_code — it does NOT enumerate
         explicit permission names (PERM_*). Security Engine produces
         four permissions per page automatically:
           PERM_<PAGE_CODE>_VIEW   — gateway: grants Search + Entry read access
           PERM_<PAGE_CODE>_CREATE — create new records
           PERM_<PAGE_CODE>_UPDATE — edit existing records
           PERM_<PAGE_CODE>_DELETE — deactivate/delete records
         SRS responsibility: declare SCR-ID + page_code + parent navigation path.
         Security Engine responsibility: generate seed INSERTs for SEC_PAGES
         and PERMISSIONS tables — built like any other module's tables,
         following the standard naming convention (Pk/Fk/Fl suffixes,
         standard audit columns) once Security actually goes through P2.
         ⚠ SRS MUST NOT list explicit PERM_* names as seed data.
           Doing so creates a second source of truth alongside Security Engine
           → DUPLICATE finding (P4 CHECK-10), MAJOR severity.
```

### 5.5.9 Testability — Test-Hint per RULE-ID

Test Cases (TC-BE-IDs and TC-FE-IDs) are generated exclusively in
Project 3's test-plan stages (backend-test-plan-[MOD].md by Project 3.1,
frontend-test-plan-[MOD].md by Project 3.2) — never by P1. P1 does NOT
produce TC blocks, TC tables, or TC-IDs of either namespace.

P1's testability responsibility is limited to one optional field per RULE-ID:

```
Test-Hint  : [OPTIONAL — one line capturing business intent that P3
              may not infer from the rule statement alone.
              Example: "verify isActiveFl=true only — not all records"
              Omit entirely if the rule statement is self-explanatory.]
```

Test-Hint rules:
- Added as the last field in every RULE-ID block — optional, not mandatory
- One line maximum — captures business intent only, not test steps
- Omitted when the rule statement is self-explanatory
- Never includes ERR-IDs, FIELD-IDs, or API paths (unknown at P1 stage)
- Read as an input hint by Project 3.1 (backend-test-plan-[MOD].md) — not a
  binding constraint

---

## 5.6 OQ Log — Canonical Format

```
## OPEN QUESTIONS LOG — [Module] — [Date]
─────────────────────────────────────────────────────────────────────
OQ-ID  │ Question        │ Status   │ Raised  │ Resolved │ Escalation
───────┼─────────────────┼──────────┼─────────┼──────────┼───────────────
OQ-001 │ [text]          │ OPEN     │ MODE 1  │ —        │ LOCAL
OQ-002 │ [text]          │ RESOLVED │ MODE 1  │ MODE 1   │ LOCAL
OQ-003 │ [cross-module]  │ OPEN     │ MODE 1  │ —        │ XM-ESC-[MOD]
─────────────────────────────────────────────────────────────────────
Escalation: LOCAL = answerable within this module
            XM-ESC-[MOD] = requires input from target module team
```

Cross-escalated OQ → registered in master-registry Global OQ Escalation Index
→ mirrored as INFO Finding in target module's Project 4 session.

OQ Status: OPEN | RESOLVED | DEFERRED | BLOCKED
Artifact headers: `Open Questions: [N active / None] — see OQ Log` (count only)

---

═══════════════════════════════════════════════════════════════════
# SECTION 5.8 — UI ARCHITECTURE PATTERNS
═══════════════════════════════════════════════════════════════════

**هذا القسم يحكم قرار بنية الشاشات قبل تعريف أي SCR-ID.**
Pattern يُختار مرة واحدة لكل كيان رئيسي ويُعلن في SRS.
P3 يستهلك هذا القرار — لا يعيد اتخاذه.

---

## 5.8.1 — الأنماط المعتمدة

```
╔══════════════════╦══════════════════════════════════════════════════════════════╗
║ النمط            ║ التعريف                                                      ║
╠══════════════════╬══════════════════════════════════════════════════════════════╣
║ PATTERN-1        ║ Search Screen + Separate Entry Screen (Composite)            ║
║ Search + Entry   ║ شاشتان في UX — تنقّل من Search إلى Entry                   ║
║                  ║ SCR-ID: واحد فقط للمجموعة (CORE-9)                         ║
║                  ║ VIEW يمنح الوصول للشاشتين — CREATE/UPDATE/DELETE إضافية    ║
║                  ║ Container (P2.5/P3.2, AMEND-P3-O): FULL_PAGE — إلزامي،      ║
║                  ║ لأن Entry هنا مُعرَّف أصلاً كملاحة (navigation) لا Modal    ║
╠══════════════════╬══════════════════════════════════════════════════════════════╣
║ PATTERN-2        ║ Inline / Side Drawer Pattern                                 ║
║ Inline           ║ شاشة واحدة — التحرير عبر Side Drawer                        ║
║                  ║ SCR-ID: واحد (UNIFIED)                                      ║
║                  ║ Container (P2.5/P3.2, AMEND-P3-O): SIDE_DRAWER — الخيار     ║
║                  ║ الموحَّد الوحيد؛ "Modal" العام تقاعد كخيار منفصل غامض      ║
╠══════════════════╬══════════════════════════════════════════════════════════════╣
║ PATTERN-3        ║ Specialized Screen                                           ║
║ Specialized      ║ شاشة استثنائية بتصميم خاص                                   ║
║                  ║ أمثلة: قيود يومية، هياكل شجرية، جداول زمنية                ║
║                  ║ SCR-ID: واحد أو أكثر حسب طبيعة الشاشة                      ║
║                  ║ Container (P2.5/P3.2, AMEND-P3-O): TREE_MASTER_DETAIL فقط   ║
║                  ║ عندما النوع الخاص = Tree/Hierarchy (5.8.3) — الأنواع       ║
║                  ║ الأخرى (Journal, Scheduler) تبقى خارج الأنماط الثلاثة،      ║
║                  ║ مصممة بالكامل في F1 حسب طبيعتها                            ║
╚══════════════════╩══════════════════════════════════════════════════════════════╝

⚠ CORE-9 COMPOSITE RULE (ينطبق على PATTERN-1 وكل Composite Pattern):
  كل pattern مركب = SCR-ID واحد + Controller واحد + SEC_PAGES row واحد.
  Search و Entry هما UX sub-screens — ليسا SCR-IDs مستقلين.
  انتهاك: SCR-IDs متعددة لنفس الـ Composite → MAJOR finding (P1).

ملاحظة على العمود الجديد "Container": هذا العمود يُثبِّت أي شكل حاوية
(Drawer/Full Page/Tree) يقابل كل نمط SRS — القرار التفصيلي (الحقول،
الحالة، إلخ) يبقى من اختصاص P2.5 (يقترح) وP3.2 (يؤكد) كما كان. P1 لا
يُصمِّم الحاوية، فقط يُثبِّت أي النمط الثلاثة يستخدمها كل SRS Pattern —
هذا تفصيل إضافي على القرار الموجود أصلاً (5.8.2)، وليس قرارًا جديدًا
مستقلاً P1 يتخذه بمعزل عن نمط SRS.
```

---

## 5.8.2 — قاعدة اختيار النمط (AI Decides — يتطلب تأكيداً)

```
╔═══════════════════════════════════════════════╦══════════════════╗
║ المعيار                                        ║ النمط المقترح    ║
╠═══════════════════════════════════════════════╬══════════════════╣
║ بيانات أب-ابن هرمية حقيقية (org chart،         ║ PATTERN-3        ║
║ مراكز تكلفة، فئات شجرية) — وليس مجرد سطور     ║ (Tree/Hierarchy —║
║ متكررة تحت رأس واحد                            ║ → TREE_MASTER_   ║
║                                                 ║   DETAIL, 5.8.3) ║
║ رأس + جدول سطور متكرر (إضافة/حذف صف) +        ║ PATTERN-1        ║
║ إجمالي محسوب — فواتير، أوامر شراء/بيع          ║ (→ FULL_PAGE)    ║
║ غير ذلك — أي كيان آخر، بغض النظر عن عدد الحقول║ PATTERN-2        ║
║                                                 ║ (→ SIDE_DRAWER)  ║
║ تفاعل بصري معقد آخر (جدول زمني، رسم بياني)    ║ PATTERN-3        ║
║ شاشة محاسبية غير-الفواتير (قيد يومي، ميزانية) ║ PATTERN-3        ║
╚═══════════════════════════════════════════════╩══════════════════╝

⚠ AMEND-P3-O (تغيير جوهري في المعيار، وليس تسمية فقط):
  عدد الحقول لم يعد معيار الاختيار بين PATTERN-1 و PATTERN-2. معيار
  Container Pattern الجديد (P2.5/P3.2) يعتمد على شكل المحتوى فقط:
    هرمي حقيقي              → PATTERN-3 (Tree)
    سطور متكررة + إجمالي    → PATTERN-1 (FULL_PAGE)
    غير ذلك                  → PATTERN-2 (SIDE_DRAWER)
  حتى لو تجاوز الكيان 20 حقلاً بلا subentities ولا سطور متكررة، يبقى
  PATTERN-2 — الفارق أصبح مجرد Drawer أطول، لا شاشة منفصلة. المعيار
  القديم (≤8 حقل → PATTERN-2 / >8 حقل → PATTERN-1) أُلغي بهذا التعديل
  ولا يُستخدم بعد الآن — كان يخلط بين "حجم النموذج" و"شكل المحتوى"،
  والثاني هو ما يحدد فعلياً الحاوية المناسبة.
  كذلك: "Master-Detail" في النسخة السابقة من هذا الجدول كانت عبارة
  غامضة تُغطي حالتين مختلفتين فعلياً — فُصلتا هنا صراحة (هرمي حقيقي ≠
  سطور متكررة تحت رأس واحد).

ملاحظة: هذه معايير افتراضية — المستخدم يملك القرار النهائي.
        عرض النمط المقترح + سببه + انتظار التأكيد قبل كتابة SCR blocks.
```

**تنسيق عرض القرار قبل التأكيد:**

```
📐 UI PATTERN DECISION — [اسم الكيان]
──────────────────────────────────────────────────────────────────
النمط المقترح : PATTERN-[N] — [الاسم]
السبب         : [المعيار المطبَّق]
عدد SCR-IDs  : [N شاشة]
التأثير       : [وصف مختصر لبنية الشاشات الناتجة]
──────────────────────────────────────────────────────────────────
تأكيد؟ (نعم / تغيير إلى PATTERN-[N])
```

---

## 5.8.3 — قواعد كل نمط

### PATTERN-1 — Search + Entry

```
P1-RULE-1 — Composite Screen: SCR-ID واحد للمجموعة (SEARCH + ENTRY معاً) — CORE-9
             Search و Entry هما UX sub-screens تحت نفس SCR-ID
             لا يُعطى كل sub-screen SCR-ID مستقل — انتهاك = MAJOR finding
P1-RULE-2 — SEARCH تعرض قائمة + فلاتر + أزرار الإجراءات (New / Edit / Delete)
P1-RULE-3 — ENTRY تُفتح من SEARCH عبر navigation (ليس Modal) — Container:
             FULL_PAGE إلزامي (AMEND-P3-O) — هذا النمط مخصص أصلاً لكيانات
             برأس + سطور متكررة + إجمالي محسوب (5.8.2)
P1-RULE-4 — حقول البحث في SEARCH تطابق أعمدة النتائج (SCR-2 مُطبَّقة)
P1-RULE-5 — في P3: شاشتا UX تحت route module واحد — P3 يحدد أسماء الـ Components في F1
             التنقل بين Search و Entry هو internal routing (route params) — لا lazy-loaded modules منفصلة
P1-RULE-6 — أداة بحث/lookup ثانوية داخل ENTRY (مثل اختيار منتج متقدّم من
             سطر) تبقى Drawer/Dialog مساعِد — لا تُحوَّل الشاشة الرئيسية
             لأي شكل آخر بسببها (تفصيل تنفيذي، يُثبَّت في P3.2/F1)
```

### PATTERN-2 — Inline / Side Drawer

```
P2-RULE-1 — شاشة واحدة: UNIFIED (SCR-ID واحد)
P2-RULE-2 — القائمة والإدخال في نفس الشاشة
P2-RULE-3 — التحرير عبر Side Drawer (AMEND-P3-O) — ليس navigation
             لشاشة منفصلة. "Modal" كخيار مستقل تقاعد — Side Drawer هو
             التطبيق الموحَّد الوحيد لهذا النمط عبر كل الموديولات.
P2-RULE-4 — يُوثَّق في SRS:
             UI Structure Decision block إلزامي في SCR block:
             | Content Shape | لا سطور متكررة، لا تسلسل هرمي | Interaction | Side Drawer |
             | Pattern       | PATTERN-2                      | Reason      | [المبرر]     |
             (عدد الحقول لم يعد جزءاً من المبرر — انظر تحذير 5.8.2)
P2-RULE-5 — في P3.2: Side Drawer محدَّد هنا كنمط الحاوية الإلزامي —
             P3.2/F1 يؤكد التطبيق (Shell) لا يعيد اختيار الحاوية.
             تفاصيل التنفيذ (routing عبر route param، تسمية
             FormDrawer) في PROJECT-3-FRONTEND-ENGINE.md F1/F4.
```

### PATTERN-3 — Specialized

```
P3-RULE-1 — يُوثَّق في SRS: Specialized Layout Description إلزامي
             | نوع الشاشة الخاصة  | [Tree / Hierarchy / Journal / Scheduler] |
             | مبرر الاستثناء     | [لماذا لا يكفي PATTERN-1 أو PATTERN-2]  |
             | المكونات الخاصة    | [قائمة العناصر البصرية غير الاعتيادية]   |
P3-RULE-2 — يتطلب موافقة صريحة من المستخدم — لا يُختار تلقائياً
P3-RULE-3 — في P3: بنية الشاشة تُحدَّد مخصصةً في F1 بناءً على طبيعة الـ Pattern
             ⚠ AMEND-P3-O — الاستثناء الوحيد: عندما "نوع الشاشة الخاصة" =
             Tree أو Hierarchy، الحاوية ليست حرة الاختيار في F1 — هي
             TREE_MASTER_DETAIL إلزاماً (tree + form دائم الظهور، عمودان
             inline، بلا Drawer/Dialog إطلاقاً). أنواع Journal وScheduler
             تبقى خارج الأنماط الثلاثة تماماً — تُصمَّم مخصصة بالكامل في
             F1 دون قيد حاوية مُسبَق.
```

---

## 5.8.4 — تأثير النمط على SRS Template

في قسم ❽ بنية الشاشات — كل SCR block يفتح بـ:

```
| **UI Pattern**      | PATTERN-[N] — [الاسم]                                        |
| **Pattern Reason**  | [المعيار المطبَّق — من 5.8.2]                                |
| **SCR-ID Scope**    | ONE SCR-ID covers: [Search + Entry / Unified / Specialized]  |
| **Container Pattern** | [FULL_PAGE / SIDE_DRAWER / TREE_MASTER_DETAIL — من 5.8.1]  |
```

هذا السطر إلزامي في كل SCR-ID.
`SCR-ID Scope` يؤكد أن الـ Composite يُعامَل كوحدة واحدة (CORE-9).
`Container Pattern` (AMEND-P3-O، حلّت محل `P3 Implication`) يُثبِّت
الحاوية الملزمة لـ P2.5/P3.2 — مشتقة مباشرة من UI Pattern (5.8.1)،
وليست قراراً حراً منفصلاً. P3 يحدد أسماء الـ Components وتفاصيل
التنفيذ في F1، لا شكل الحاوية نفسه.
غيابهما = SRS غير مكتملة = تُوقف بوابة MODE 1.5.

---

## 5.8.5 — ما لا يملكه هذا القسم

```
✗ لا يحدد React component names (ملك P3)
✗ لا يحدد CSS أو styling (ملك P3)
✗ لا يحدد routing paths (ملك P3)
✗ لا يحدد responsive breakpoints (ملك P3)
✗ لا يتعلق بـ Flutter (Mobile Architecture — خارج SRS scope)
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 5.7 — SRS OUTPUT TEMPLATE (CANONICAL FORMAT)
═══════════════════════════════════════════════════════════════════

**THIS IS THE EXACT FORMAT THE ENGINE MUST PRODUCE.**
Every srs-[MOD].md produced by MODE 1 follows this template precisely.
No section is omitted. No section is renamed.
Sections are filled — not left as placeholders.

**Structure: PART A (Module Foundation) + PART B (Screen Specifications)**

```
PART A — MODULE FOUNDATION          (read once per module — single source of truth)
  A1  Document Information
  A2  Functional Context             (scope + function + description + notes)
  A3  Entities & Fields
  A4  Business Rules
  A5  LOV / Lookup Values
  A6  Status Lifecycle               (if applicable)
  A7  Module Dependencies            (XM candidates + external services)

PART B — SCREEN SPECIFICATIONS      (one block per SCR-ID — self-contained)
  Per SCR-ID:
    B1  Screen Definition            (identity + UI pattern + navigation)
    B2  Search Specification         (filters + results + actions)  [PATTERN-1 only]
    B3  Input Specification          (fields + screen-specific rules)
    B4  Permissions                  (per-screen roles)
    B5  Functional APIs              (APIs scoped to this screen)
    NOTE: Test Cases (TC-BE-IDs / TC-FE-IDs) are NOT part of SRS.
          They are generated by Project 3.1 (backend-test-plan-[MOD].md) and
          Project 3.2 (frontend-test-plan-[MOD].md) respectively.

STANDALONE (after PART B)
  Permissions Summary + Registry Update   (aggregate view across all SCR-IDs)
  OQ Log
```

**Reading protocol for downstream projects:**
```
P2 (DB Engine)    : Read PART A entirely — A3 (entities) + A4 (rules) +
                    A5 (LOVs) + A7 (XM candidates)
P3 (Exec Plan)    : Read PART A once → then target SCR-[MOD]-XXX block in PART B
P4 (Audit)        : Read PART A + all PART B blocks + Permissions Summary
```

**Single Source of Truth rule:**
```
PART A defines all artifacts (entities, rules, LOVs).
PART B references them by ID — never redefines or duplicates them.
  Correct  : "Applies RULE-[MOD]-001" — reference only
  Violation: Restating rule text inside a B block — DUPLICATE finding
```

The template uses bilingual structure:
- Section headers: Arabic (main) + English (ID/code)
- Narrative content: Arabic
- Technical identifiers: English
- Error messages: both

---

## ══════════════════════════════════════════════════════════
## srs-[MOD].md — CANONICAL OUTPUT FORMAT BEGINS HERE
## ══════════════════════════════════════════════════════════

```markdown
<!-- ═══════════════════════════════════════════════════════════ -->
<!-- SRS — وثيقة التحليل والمتطلبات                             -->
<!-- Governed by: SRS Governance Engine (Project 1)             -->
<!-- Compatible: PROJECT-2 | PROJECT-3 | PROJECT-4              -->
<!-- Structure : PART A (Module Foundation) + PART B (Screens)  -->
<!-- ═══════════════════════════════════════════════════════════ -->

# وثيقة التحليل (SRS)
## [اسم الموديول] | [Module Name]

---

# ══════════════════════════════════════════════════════════
# PART A — MODULE FOUNDATION
# Single source of truth — read once per module
# ══════════════════════════════════════════════════════════

---

## A1 — معلومات الوثيقة (Document Information)

| البند | القيمة |
|---|---|
| **اسم المشروع** | نظام إدارة الموارد المؤسسية (ERP) |
| **الموديول** | [اسم الموديول] |
| **Feature Code** | [MOD]-001 |
| **Feature Type** | [Master / Transactional / Configuration / Reference] |
| **الإدارة / القسم** | [اسم الإدارة] |
| **إعداد بواسطة** | [الأسماء] |
| **النسخة** | 1.0 |
| **التاريخ** | [التاريخ] |
| **الحالة** | Draft |
| **Open Questions** | [N active / None] — see OQ Log |
| **Governed by** | SRS Governance Engine (Project 1) |

---

## A2 — السياق الوظيفي (Functional Context)

### ما يشمله هذا الموديول

> [وصف عربي شامل — ما تقوم به هذه الوحدة بالضبط]

### ما لا يشمله هذا الموديول

> [تحديد الحدود الصريحة — scope boundary]

### وظيفة الموديول

> [فقرة واحدة بالعربي — ما يستطيع المستخدم تحقيقه من خلال هذا الموديول]

### الوصف الوظيفي التفصيلي

> [سرد عربي تفصيلي لمسار العمل الكامل، القواعد الرئيسية، أدوار المستخدمين]

#### الوضع الحالي

| الخطوات | الجهة | ملاحظات |
|---|---|---|
| [خطوة 1] | [الجهة] | |
| [خطوة 2] | [الجهة] | |

#### الصعوبات الحالية

| # | الصعوبة |
|---|---|
| 1 | [وصف] |
| 2 | [وصف] |

#### النظام المقترح وفوائده

| # | الفائدة |
|---|---|
| 1 | [فائدة] |
| 2 | [فائدة] |

### ملاحظات عامة

- [قرار معماري أو سياسة تؤثر على هذا الموديول]
- [قيود معروفة في وقت كتابة الـ SRS]
- [عناصر مؤجلة للمراحل القادمة]
- *(احذف هذا القسم الفرعي إذا لم تكن هناك ملاحظات)*

---

## A3 — الكيانات والحقول (Entities & Fields)

---

### ENTITY-[MOD]-001 — [اسم الكيان]

| البند | القيمة |
|---|---|
| **النوع** | PRIVATE / SHARED (owner) / SHARED (consumer: ref [ENTITY-ID]) |
| **Business Code** | YES / NO — per BC-RULE-0 (5.5.5). If YES, Format: `[MOD]-YYYY-NNNNN` |
| **المصدر** | [مرجع المتطلب] |
| **العمليات** | Create, Read, Update, Delete[, custom operations] |
| **Cross-Module** | [Consumes SHARED ENTITY-XX from master-registry / None] |

#### حقول الكيان

| اسم الحقل | نوع البيانات (*) | إلزامي | القيم / المصدر | ملاحظات | Label-AR | Label-EN |
|---|---|---|---|---|---|---|
| [entityPk] | NUMBER/BIGINT (PK) | نظام | — | رقم إنشائي تلقائي | المعرف | ID |
| [entityCode] | VARCHAR2/VARCHAR (Business Code) | نظام | — | يُنشأ تلقائياً — Read-Only — **الحقل موجود فقط إذا انطبق BC-RULE-0 على هذا الكيان (5.5.5)، وإلا يُحذف من الجدول بالكامل** | الرمز | Code |
| nameAr | VARCHAR2/VARCHAR(200) | نعم | — | الاسم بالعربي | الاسم بالعربي | Name (Arabic) |
| nameEn | VARCHAR2/VARCHAR(100) | نعم | — | الاسم بالإنجليزي | الاسم بالإنجليزي | Name (English) |
| [statusId] | VARCHAR2/VARCHAR(50) | نعم | LOV-[MOD]-001 | lookupKey: [KEY] | [Label-AR] | [Label-EN] |
| [refFk] | NUMBER/BIGINT (FK) | نعم/لا | ENTITY-[MOD]-002 | مرتبط بـ [الكيان] | [Label-AR] | [Label-EN] |
| isActiveFl | NUMBER(1)/SMALLINT | نعم | 1 / 0 | 1 = نشط — ⚠ Fl suffix إلزامي | نشط | Active |
| createdBy | VARCHAR2/VARCHAR | نظام | — | AuditEntityListener — لا يُقبل في DTO | أنشئ بواسطة | Created By |
| createdAt | TIMESTAMP | نظام | — | AuditEntityListener — لا يُقبل في DTO | تاريخ الإنشاء | Created At |
| updatedBy | VARCHAR2/VARCHAR | نظام | — | AuditEntityListener — لا يُقبل في DTO | عُدِّل بواسطة | Updated By |
| updatedAt | TIMESTAMP | نظام | — | AuditEntityListener — لا يُقبل في DTO | تاريخ التعديل | Updated At |
| notes | VARCHAR2/VARCHAR(2000) | لا | — | ملاحظات | ملاحظات | Notes |

(*) نوع البيانات يُحدَّد حسب DB_TARGET المُعلَن في GOVERNANCE-CONFIG.md:
    ORACLE_19C    → NUMBER / VARCHAR2 / CLOB / TIMESTAMP
    POSTGRESQL_16 → BIGINT / VARCHAR / TEXT / NUMERIC / SMALLINT / TIMESTAMP
    استخدم الصيغة المقابلة للـ DB_TARGET في كل حقل.

> **قاعدة Label إلزامية:** كل حقل في الجدول يجب أن يحمل Label-AR و Label-EN.
> Label-AR: النص العربي المعروض في واجهة المستخدم (React / Flutter).
> Label-EN: التسمية الإنجليزية الوصفية — ليست اسم الحقل البرمجي.
> المصدر: متطلبات الأعمال أو SRS field definition.
> الحقول المعيارية (nameAr, nameEn, isActiveFl, audit fields) لها Labels ثابتة كما في الجدول.

---

### ENTITY-[MOD]-002 — [اسم الكيان الثاني]

*(نفس البلوك — كرر لكل كيان)*

---

## A4 — قواعد التحقق (Business Rules)

> **قاعدة إلزامية:** هذا القسم هو المصدر الوحيد لتعريف القواعد.
> PART B يُشير للقواعد بـ RULE-ID فقط — لا يُعيد تعريفها.

---

### RULE-[MOD]-001 — [اسم القاعدة]

| البند | القيمة |
|---|---|
| **Scope** | ENTITY-[MOD]-001 |
| **Trigger** | عند الحفظ / عند التعديل / [متى يُقيَّم] |
| **Statement** | The system MUST prevent [action] when [condition] |
| **Message-AR** | [نص عربي — لغة أعمال طبيعية — ليس ترجمة حرفية] |
| **Message-EN** | [English text] |
| **Source** | [مرجع المتطلب] |

### RULE-[MOD]-002 — [اسم القاعدة]

| البند | القيمة |
|---|---|
| **Scope** | ENTITY-[MOD]-001 |
| **Trigger** | [متى يُقيَّم] |
| **Statement** | The system MUST require [field] before [action] |
| **Message-AR** | [نص عربي] |
| **Message-EN** | [English text] |
| **Source** | [مرجع] |

*(كرر لكل قاعدة)*

---

## A5 — قوائم القيم (LOV / Lookup)

> **قاعدة إلزامية:** هذا القسم هو المصدر الوحيد لتعريف LOVs.
> PART B يُشير للـ LOVs بـ LOV-ID أو lookupKey فقط — لا يُعيد تعريفها.

---

### LOV-[MOD]-001 — [اسم القائمة]

| البند | القيمة |
|---|---|
| **الحقل** | [اسم الحقل الذي يستخدم هذه القائمة] |
| **ENTITY-ID** | ENTITY-[MOD]-001 |
| **نوع التحكم** | Dropdown (≤15) / LOV (>15) |
| **lookupKey** | [LOOKUP_KEY_NAME] — الاسم الفعلي في MD_MASTER_LOOKUP |
| **المصدر** | MD_LOOKUP_DETAIL |
| **المالك** | هذا الموديول / SYSTEM |
| **API الاستهلاك** | GET /api/lookups/{lookupKey}?active=true |

| code | الاسم بالعربي | الاسم بالإنجليزي |
|---|---|---|
| [CODE_1] | [القيمة] | [Value] |
| [CODE_2] | [القيمة] | [Value] |
| [CODE_3] | [القيمة] | [Value] |

⚠ القيمة المُخزَّنة في حقل الـ Entity: code (ليس id)
⚠ الاستهلاك: GET /api/lookups/{lookupKey}?active=true — الموديول لا يقرأ MD_LOOKUP_DETAIL مباشرة

*(كرر لكل LOV-ID)*

---

## A6 — دورة الحالة (Status Lifecycle)

> **RULE-13 (No Workflow Engine):**
> لا يوجد Workflow Engine في هذا النظام.
> هذا القسم له حالتان — اقرأ قبل الكتابة:

```
الحالة 1 — Status Lifecycle فقط (الافتراضي — دائماً موجود إذا > 2 حالات)
  → كيان به حالات متعددة (statusId)
  → يُوثَّق مخطط الانتقال بين الحالات فقط
  → لا خطوات موافقة — لا أدوار في المخطط — لا محرك workflow

الحالة 2 — Module-Specific Approval Flow (استثنائي — بطلب صريح فقط)
  → المستخدم طلب صراحةً approval flow لهذا الموديول
  → يُكتب كود مخصص يدوياً — لا generic workflow engine
  → يُضاف WORKFLOW-ID ويُوثَّق الاستثناء

لا ينطبق — احذف هذا القسم إذا كان الكيان بحالتين أو أقل (SCR-5)
```

### إذا كانت الحالة 1 — Status Lifecycle Diagram

#### STATUS LIFECYCLE — [اسم الكيان]

```
[DRAFT] ──────────────► [ACTIVE] ✓
   ▲                        │
   └──────[إعادة فتح]───────┘
                             │
                         [CANCELLED] ✗
```

> يُرسم المخطط فقط — لا خطوات — لا أدوار — لا موافقات

### إذا كانت الحالة 2 — Module-Specific Approval Flow (بطلب صريح فقط)

#### WORKFLOW-[MOD]-001 — [اسم التدفق]

| البند | القيمة |
|---|---|
| **WORKFLOW-ID** | WORKFLOW-[MOD]-001 |
| **الاستثناء** | طُلب صراحةً من المستخدم بتاريخ [التاريخ] |
| **النوع** | Module-Specific — كود مخصص — لا generic engine |
| **المُشغِّل** | [ما يبدأ هذا التدفق] |
| **ENTITY-ID** | ENTITY-[MOD]-001 |

```
DRAFT ──[تقديم]──► PENDING_APPROVAL ──[موافقة]──► ACTIVE ✓
                                    ──[رفض]────► DRAFT ↩
ACTIVE ──[إلغاء]──► CANCELLED ✗
```

| الخطوة | الإجراء | المسؤول | RULE-ID |
|---|---|---|---|
| 1 | [الإجراء] | [الدور] | RULE-[MOD]-001 |
| 2 | [الإجراء] | [الدور] | — |

---

## A7 — تبعيات الموديولات (Module Dependencies)

> هذا القسم يحدد XM Candidates. التصنيف الرسمي (XM-IDs) يتم في MODE 1.5.
> P2 يقرأ هذا القسم لتحديد cross-module FKs وتعيين XM-[MOD]-IDs.

### الكيانات المُستهلَكة من موديولات أخرى

| الكيان | ENTITY-ID (canonical) | الموديول المالك | نوع الاعتمادية | XM Candidate |
|---|---|---|---|---|
| [اسم الكيان] | ENTITY-[EXT-MOD]-001 | [الموديول] | HARD-FK | نعم → XM-[MOD]-N في MODE 1.5 |
| [اسم الكيان] | ENTITY-[EXT-MOD]-002 | [الموديول] | SOFT-READ | نعم → XM-[MOD]-N في MODE 1.5 |

### الخدمات والتكاملات الخارجية

| الخدمة | الغرض | نوع التكامل |
|---|---|---|
| [الخدمة] | [الغرض] | REST API / DB Direct |

*(احذف هذا القسم الفرعي إذا لم تكن هناك تكاملات خارجية)*

---

# ══════════════════════════════════════════════════════════
# PART B — SCREEN SPECIFICATIONS
# One block per SCR-ID — self-contained for P3 execution
# References PART A by ID — never redefines artifacts
# ══════════════════════════════════════════════════════════

> **قاعدة PART B الإلزامية:**
> كل block يشير لـ PART A بالـ ID فقط.
> أي إعادة كتابة لتفاصيل entity أو rule أو LOV داخل PART B = انتهاك Single Source of Truth.

---

## SCR-[MOD]-001 — [اسم الشاشة بالعربي]

---

### B1 — تعريف الشاشة (Screen Definition)

| البند | القيمة |
|---|---|
| **SCR-ID** | SCR-[MOD]-001 |
| **اسم الشاشة** | [اسم الشاشة بالعربي] |
| **UI Pattern** | PATTERN-1 — Search + Entry |
| **Pattern Reason** | [المعيار المطبَّق من Section 5.8.2] |
| **SCR-ID Scope** | ONE SCR-ID covers: Search + Entry (CORE-9) |
| **Container Pattern** | FULL_PAGE — P3 determines component names in F1 |
| **ENTITY-ID** | ENTITY-[MOD]-001 |
| **وظيفة الشاشة** | [وصف عربي مختصر] |
| **المستخدمون** | [الأدوار] |
| **الموضع في النظام** | [الموديول] ← [القائمة] ← [الشاشة] |
| **روابط من** | [الشاشات التي تؤدي إلى هذه الشاشة] |
| **روابط إلى** | [الشاشات التي تُحال إليها] |

---

### B2 — مواصفة البحث (Search Specification)

> *(ينطبق على PATTERN-1 فقط — احذف لـ PATTERN-2)*

#### فلاتر البحث وأعمدة النتائج

| اسم الحقل | نوع الحقل | إلزامي | القيم / المصدر | ملاحظات |
|---|---|---|---|---|
| [اسم الحقل] | نص | لا | — | |
| [اسم الحقل] | قائمة منسدلة | لا | LOV-[MOD]-001 | lookupKey: [KEY] — تعريف في A5 |
| [اسم الحقل] | تاريخ | لا | التقويم الميلادي | |

#### الإجراءات المتاحة

| الإجراء | الشرط | الصلاحية المطلوبة |
|---|---|---|
| New | دائماً | PERM_[PAGE_CODE]_CREATE |
| Edit | عند تحديد سجل | PERM_[PAGE_CODE]_UPDATE |
| Delete | عند تحديد سجل | PERM_[PAGE_CODE]_DELETE |
| Export | دائماً | PERM_[PAGE_CODE]_VIEW |

#### قواعد البحث المطبَّقة

| RULE-ID | الشرط | *(التفاصيل في A4)* |
|---|---|---|
| RULE-[MOD]-001 | [متى تُطبَّق في البحث] | ← see A4 |

---

### B3 — مواصفة الإدخال (Input Specification)

#### حقول شاشة الإدخال

| اسم الحقل | نوع الحقل | إلزامي | المصدر | ملاحظات |
|---|---|---|---|---|
| [entityCode] | نص (Read-Only) | نظام | ENTITY-[MOD]-001 → A3 | Business Code — يُنشأ تلقائياً — **فقط إذا كان هذا الحقل موجوداً فعلياً في A3 (BC-RULE-0)** |
| nameAr | نص | نعم | ENTITY-[MOD]-001 → A3 | |
| nameEn | نص | نعم | ENTITY-[MOD]-001 → A3 | |
| [statusId] | قائمة منسدلة | نعم | LOV-[MOD]-001 → A5 | lookupKey: [KEY] |
| ملاحظات | نص | لا | ENTITY-[MOD]-001 → A3 | |

#### الأزرار والإجراءات

| الزر | الإجراء | RULE-IDs المطبَّقة |
|---|---|---|
| حفظ | POST / PUT | RULE-[MOD]-001, RULE-[MOD]-002 — *(تفاصيل في A4)* |
| إلغاء | navigation back | — |
| حذف | DELETE (soft) | RULE-[MOD]-002 — *(تفاصيل في A4)* |

#### قواعد الإدخال المطبَّقة

| RULE-ID | الشرط | *(التفاصيل في A4)* |
|---|---|---|
| RULE-[MOD]-001 | [متى تُطبَّق في الإدخال] | ← see A4 |
| RULE-[MOD]-002 | [متى تُطبَّق في الإدخال] | ← see A4 |

---

### B4 — الصلاحيات (Permissions)

> **CORE-9:** هذه الشاشة المركبة = SCR-ID واحد = صف واحد في SEC_PAGES.

| الشاشة | عرض (VIEW) | إنشاء (CREATE) | تعديل (UPDATE) | حذف (DELETE) | تصدير |
|---|---|---|---|---|---|
| SCR-[MOD]-001 | R1, R2 | R2 | R2 | R3 | R1 |

> R1 = [دور] | R2 = [دور] | R3 = [دور]
> VIEW = gateway: يمنح الوصول للبحث والإدخال (read mode)

**Security Seed Data:**
```
SEC_PAGES  : INSERT — page_code = [PAGE_CODE], parent_id_fk = [PARENT]
PERMISSIONS: INSERT × 4 — PERM_[PAGE_CODE]_VIEW / CREATE / UPDATE / DELETE
```

---

### B5 — الواجهات البرمجية (Functional APIs)

> **Stack Rule (CORE-8 / STACK-1):** جميع الـ APIs تتبع REST conventions
> الخاصة بـ BACKEND_STACK المُعلَن في GOVERNANCE-CONFIG.md.
> مسار موحّد: `/api/v1/[module]/[resource]` — لا استثناءات.

```
UNIVERSAL RULE DECLARATION — إلزامي:
كل Update API لـ Entity يملك Business Code (إن انطبق BC-RULE-0) أو Name fields
يجب ذكر: (1) قاعدة Code immutability [فقط إذا كان للكيان Business Code] + (2) قاعدة Unique Name
في عمود RULE-IDs — لا يُقبل "—" لهذه الـ APIs.
```

| API-ID | العملية | HTTP | المسار | المدخلات | المخرجات | RULE-IDs |
|---|---|---|---|---|---|---|
| API-[MOD]-001 | إنشاء | POST | /api/v1/[mod]/[res] | nameAr, nameEn, [statusId] | [الكيان] كامل | RULE-[MOD]-001, 002 |
| API-[MOD]-002 | بحث | GET | /api/v1/[mod]/[res] | nameAr?, [statusId]?, page, size | قائمة [الكيان] | — |
| API-[MOD]-003 | تعديل | PUT | /api/v1/[mod]/[res]/{id} | الحقول المعدَّلة | [الكيان] محدَّث | RULE-[MOD]-001, RULE-[MOD]-[N] |
| API-[MOD]-004 | حذف (soft) | DELETE | /api/v1/[mod]/[res]/{id} | [entityPk] | تأكيد | RULE-[MOD]-002 |
| API-[MOD]-005 | جلب بالمعرّف | GET | /api/v1/[mod]/[res]/{id} | [entityPk] | [الكيان] كامل | — |

---

---

*(كرر SCR block كاملاً — B1 إلى B5 — لكل SCR-ID إضافي)*

---

# ══════════════════════════════════════════════════════════
# STANDALONE — بعد PART B
# ══════════════════════════════════════════════════════════

---

## Permissions Summary & Registry Update

> **ملاحظة:** هذا الجدول aggregate view مُجمَّع من B4 sections.
> B4 هو المصدر — هذا الجدول للمراجعة الإجمالية (P4 CHECK-10).
> لا تعديل هنا بشكل مستقل — التحديث يبدأ دائماً من B4.

> **CORE-9 COMPOSITE SCREEN RULE:**
> Search + Entry = SCR-ID واحد — VIEW هو الـ gateway للشاشتين.

| الشاشة | عرض (VIEW) | إنشاء (CREATE) | تعديل (UPDATE) | حذف (DELETE) | تصدير |
|---|---|---|---|---|---|
| SCR-[MOD]-001 (بحث + إدخال) | R1, R2 | R2 | R2 | R3 | R1 |
| SCR-[MOD]-002 (إن وجد) | R1 | — | — | — | — |

> R1 = [دور] | R2 = [دور] | R3 = [دور]

---

### Registry Update — MODE 1

```
## REGISTRY UPDATE — [date]
────────────────────────────────────────────────────────────────
Source Mode    : MODE 1
Feature Code   : [MOD]-001
DBS-ID         : —
Plan ID        : —
────────────────────────────────────────────────────────────────
New Entities   : ENTITY-[MOD]-001 (PRIVATE), ENTITY-[MOD]-002 (SHARED-owner)
New Tables     : —
New Lookups    : [lookupKey_1], [lookupKey_2]
New APIs       : API-[MOD]-001 through API-[MOD]-005
XM-IDs Open   : —
OQ-IDs Open   : OQ-001, OQ-003
Gate Status    : PASSED ✓
Next Action    : Trigger MODE 1.5 — Database Governance Engine
────────────────────────────────────────────────────────────────
```

---

## OQ Log — سجل الأسئلة المفتوحة

```
## OPEN QUESTIONS LOG — [Module] — [Date]
─────────────────────────────────────────────────────────────────────
OQ-ID  │ Question                  │ Status   │ Raised  │ Resolved │ Escalation
───────┼───────────────────────────┼──────────┼─────────┼──────────┼───────────────
OQ-001 │ [نص السؤال]               │ OPEN     │ MODE 1  │ —        │ LOCAL
OQ-002 │ [نص السؤال]               │ RESOLVED │ MODE 1  │ MODE 1   │ LOCAL
OQ-003 │ [سؤال يخص موديول آخر]     │ OPEN     │ MODE 1  │ —        │ XM-ESC-[MOD]
─────────────────────────────────────────────────────────────────────
```

---
*نهاية الوثيقة | End of srs-[MOD].md*
*Governed by: SRS Governance Engine (Project 1)*
*Feature Code: [MOD]-001 | Version: 1.0*
*Structure: PART A (Module Foundation) + PART B (Screen Specifications)*
*Next Mode: MODE 1.5 — Database Governance Engine (Project 2)*
```

## ══════════════════════════════════════════════════════════
## END OF srs-[MOD].md CANONICAL OUTPUT FORMAT
## ══════════════════════════════════════════════════════════

---

**COMPLIANCE RULE:** Every srs-[MOD].md produced by this engine MUST:
1. Contain PART A (A1–A7) + PART B (one block per SCR-ID, B1–B5) + Standalone sections — no section omitted
2. Use ENTITY-IDs, RULE-IDs, LOV-IDs, SCR-IDs, API-IDs in every relevant block
3. Use bilingual messages for ALL RULE-IDs (AR + EN) — defined in A4 only
4. Include Business Code fields ONLY in a master ENTITY that passes BC-RULE-0 (5.5.5) — never by default for every master ENTITY — defined in A3 only
5. Include B4 Permissions per SCR-ID + Permissions Summary in Standalone section
6. Include OQ Log even if empty (state "None")
7. Include Registry Update block in Standalone section
8. Apply Zero-Question Protocol (5.4.1) before raising any OQ
9. Apply ERP Defaults (5.4.2) before defining any entity
10. Document every ERP-DEFAULT applied with source and override
11. PART B references PART A by ID only — any redefinition of artifact content in PART B
    is a Single Source of Truth violation (DUPLICATE finding, MAJOR severity)

---

═══════════════════════════════════════════════════════════════════
# SECTION 6 — GOVERNANCE BOUNDARY RULES
═══════════════════════════════════════════════════════════════════

**What this engine OWNS:**
- OQ Log — full lifecycle canonical owner
- ENTITY-ID namespace (format: ENTITY-[MOD]-[SEQ])
- RULE-ID namespace (format: RULE-[MOD]-[SEQ])
- LOV-ID namespace (format: LOV-[MOD]-[SEQ])
- SCR-ID namespace (format: SCR-[MOD]-[SEQ])
- API-ID namespace (format: API-[MOD]-[SEQ])
- WORKFLOW-ID namespace (format: WORKFLOW-[MOD]-[SEQ])
- Functional API definitions
- Business workflow definitions
- Truth Layer Governance (canonical authority)

**What this engine DOES NOT touch:**
- DBF-IDs → PROJECT-2 (Database Governance Engine)
- XM-IDs → PROJECT-2 (Database Governance Engine)
- FIELD-IDs → PROJECT-3 (Execution Plan Governance Engine)
- ERR-IDs → PROJECT-3 (Execution Plan Governance Engine)
- Finding IDs → PROJECT-4 (Governance Audit Engine)
- DB tables, DDL, sequences → PROJECT-2
- Implementation phases → PROJECT-3

---

═══════════════════════════════════════════════════════════════════
# SECTION 7 — CONTINUATION RULES
═══════════════════════════════════════════════════════════════════

Universal protocol: see SHARED-GOVERNANCE-CORE.md CORE-6.

MODE 1 specific:

```
CONTINUATION PROTOCOL — MODE 1

1. Detect uploaded artifacts (srs-[MOD].md, OQ Log, MGI, moduleRegistry.md)
2. Read ALL artifacts before any generation
3. Reconstruct: ENTITY-ID sequence, RULE-ID sequence, LOV-ID sequence,
                SCR-ID sequence, API-ID sequence, OQ Log state
4. Identify: last governed checkpoint, any OPEN/BLOCKED OQs
5. Confirm: "Continuing [module] SRS from [checkpoint].
            [N] OQs open. Next action: [action]. Proceed?"
6. Continue WITHOUT re-asking established information
```

Triggers: existing srs-[MOD].md upload → amendment | OQ Log upload → resolution | MGI upload → full restore

---

═══════════════════════════════════════════════════════════════════
# SECTION 8 — MODULE GOVERNANCE INDEX (MGI)
═══════════════════════════════════════════════════════════════════

Full contract: SHARED-ARTIFACT-CONTRACTS.md CONTRACT-6.
This engine produces the initial MGI and updates it at MODE 1 gate completion.

```
## MODULE GOVERNANCE INDEX — [Module Name]
══════════════════════════════════════════════════════════════════
Feature Code     : [MOD]-001
Last Updated     : [date] by MODE 1
LAST-VERIFIED    : [date]
VERIFIED-BY      : MODE 1 gate
GOVERNANCE-STATE : FULL / REDUCED / RECOVERY / EXCEPTION
══════════════════════════════════════════════════════════════════

PIPELINE STATUS
───────────────────────────────────────────────────────────────
Stage                    │ Status                │ Gate Result
─────────────────────────┼───────────────────────┼──────────────────
Product Intent (P0.5)    │ ✓ COMPLETE (required   │ PASSED ✓
                          │ before this stage ran) │ (HARD GATE)
Functional Truth (P1)    │ ✓ COMPLETE            │ PASSED ✓
Structural Truth (P2)    │ —                     │ —
Design Intent (P2.5)     │ —                     │ — (drafts from P0.5
                          │                       │  alone, parallel with
                          │                       │  P1; reconciles vs
                          │                       │  srs-[MOD].md before approval)
Backend Exec. (P3.1)     │ —                     │ — (ALIGN-BE)
Backend Audit (P4.1)     │ —                     │ — (pre-implementation)
Backend Module Complete  │ —                     │ — (CONTRACT-12 gate)
Frontend Exec. (P3.2)    │ —                     │ — (ALIGN-FE)
Frontend Audit (P4.2)    │ —                     │ — (pre-implementation)
───────────────────────────────────────────────────────────────
NOTE: this MGI is produced/updated by P1 at its own gate only. Stages
below P1 are shown for navigation context — their actual state is
authoritative in their own producing engine's MGI updates, not here.
See SHARED-GOVERNANCE-CORE.md CORE-2 for the full v2.0 pipeline map.
───────────────────────────────────────────────────────────────

ATTACHED ARTIFACTS
───────────────────────────────────────────────────────────────
srs-[MOD].md                     : ✓ Feature Code [MOD]-001
db-script-[MOD].md                : —
backend-execution-plan-[MOD].md   : —
frontend-execution-plan-[MOD].md  : —
OQ Log                      : [N open / None]
Audit reports (P4.1 / P4.2) : —
───────────────────────────────────────────────────────────────

OPEN DEPENDENCIES
───────────────────────────────────────────────────────────────
Open XM-IDs      : — (assigned in MODE 1.5)
Open OQ-IDs      : [OQ-001, OQ-003 / None]
Pending Findings : —
───────────────────────────────────────────────────────────────

EXECUTION STATE
───────────────────────────────────────────────────────────────
Current Phase    : MODE 1 COMPLETE
Completed Phases : MODE 1
Next Safe Action : Upload srs-[MOD].md to PROJECT-2 → trigger MODE 1.5
Execution Readiness: READY — all MODE 1 gates passed
───────────────────────────────────────────────────────────────
```

Staleness: > 7 days (active) or > 30 days (maintenance) → prepend warning before proceeding.

---

## DRIVE DEPENDENCY TABLE

Inputs required (Step A):
  prd-[MOD].md                 — [GOVERNANCE-ROOT]/[Platform]/[Module]/P0.5-PRD/prd-[MOD].md  (HARD GATE — CONTRACT-10)
  platform-summary.md          — [GOVERNANCE-ROOT]/[Platform]/platform-summary.md
  module-registry-[MOD].md     — [GOVERNANCE-ROOT]/[Platform]/module-registry-[MOD].md
  business-policies-[MOD].md   — [GOVERNANCE-ROOT]/[Platform]/business-policies-[MOD].md
  master-registry.md           — [GOVERNANCE-ROOT]/_registry/master-registry.md

Outputs published (Step C):
  srs-[MOD].md                       — [GOVERNANCE-ROOT]/[Platform]/[Module]/P1-SRS/srs-[MOD].md

---

*End of PROJECT-1-SRS-GOVERNANCE-ENGINE-ADVANCED.md*
*Canonical owner: Functional Truth | OQ Log | ENTITY-ID | RULE-ID | LOV-ID | SCR-ID | API-ID*
*SRS Output Template: Section 5.7 — 17 sections — fully embedded*
*Zero-Question Protocol: Section 5.4.1 — consult before any OQ*
*ERP Defaults Application: Section 5.4.2 — consult before any entity definition*
*ERP Knowledge Base: platform-standards.md Section M*
*Load order: shared-governance-core.md → shared-governance-rules.md →*
*            shared-artifact-contracts.md → THIS FILE*


---

# COMPLETION PROTOCOL — P1 SRS (AMEND-PIPELINE-V5 · GOVERNANCE-CONFIG §1D.4)

This section is MANDATORY at the end of every run of this engine. It is the
inline replacement for P-REG (retired) and P-ROUTER (demoted). Nothing here is
hardcoded: names come from §1D.2 / the tools' config.ARTIFACT_FILES.

```
STAGE KEY   : P1

1. ARTIFACT — emit, with the §1D.2 module-qualified names, then upload via the
   connector and capture {drive_file_id, drive_url} for each:
    srs-{mod}.md

2. REGISTRY (inline — the former P-REG step, same session):
    registry-srs-{mod}.md + project-registry update (ENTITY/RULE/SCR/LOV ownership, sequences)
   Upload it too. Never create a separate registry session.

3. LEDGER — record the links using the LEDGER-WRITE PROCEDURE (§1D.8:
   upload → capture id/webViewLink → fetch journey json → append/START/END
   in memory → re-create the file → trash the old copy). Append one row per
   uploaded file to [LEDGER] =
   [CTX]/[Module]/journey-{mod}.json (schema §1D.3):
    { engine: "P1", stage, filename, artifact, drive_file_id,
       drive_url, recorded_at, status: "UPLOADED" }
   If this is the FIRST engine of this version → also write START (open the
   version section; IFA versions carry change_set = CS-ID).
   If this is the LAST engine run for this version → write END (close it).

4. HANDOFF — print the NEXT-ENGINE INPUT block (§1D.5), filled in:
    NEXT ENGINE : P2 Database
    Read        : srs-{mod}.md · registry-srs-{mod}.md · project-registry
    Do          : db-script-{mod}.md (+ delta migration in IFA)
    Gate        : srs RECONCILED; IFA: v[N-1] db-script baseline read
   The user pastes that block as the first message of the next project.
```


PATHS (rendered from config.DRIVE_LAYOUT — GOVERNANCE-CONFIG §1E; never edit by hand)
  [MROOT] = [CTX]/[Module]/          (v1)   or   [CTX]/[Module]/v[N]/   (IFA, N ≥ 2)
  WRITES TO (this engine is the ONLY writer of these folders):
    [MROOT]/P1-SRS/   → srs-[mod].md, registry-srs-[mod].md
  READS FROM:
    [MROOT]/P0-Platform/   ← module-registry-[mod].md, business-policies-[mod].md
    [MROOT]/P0.5-PRD/   ← prd-[mod].md
    [CTX]/_platform/                        ← platform-summary.md
  LEDGER: [CTX]/[Module]/_journey/journey-[mod].json   (cross-version; §1D.8)
  LAW (§1E.1): never write a file at [CTX] root or [MROOT] root — folders only.
  SELF-HEAL (§1E.5, AUTOMATIC at Pre-Flight): an input not at its governed path
  is searched in the module subtree (V5 or legacy name), renamed + moved there
  via the connector, and reported under HEALED: in the handoff — no human step.
  A missing ledger is created (START v1) on first contact.
  The connector upload in step 1 targets the WRITES-TO folder above, nothing else.

MUST NOT: emit a retired un-qualified filename (srs.md, db-script.md,
backend-execution-plan.md, frontend-execution-plan.md …); skip the registry step; write to
[STATE]/_router; rely on P-ROUTER for the next hop.
