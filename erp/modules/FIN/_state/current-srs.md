# SRS — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-10)
Counts : ENT 14 · REQ 46 · AC 46 · RULE 16 · SCR-REQ 12 · ADR 0
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |
|---|---|
| Module | FIN — الحسابات العامة / Finance (General Ledger) |
| Feature code | FIN |
| Version | v1 |
| Date | 2026-09-10 |
| Status | DRAFT (P1) |
| Prepared by | governance-factory (analysis lane) |
| Decisions applied count | 0 |

## A2 — Functional context

**In scope:** شجرة حسابات هرمية بأبعاد كبيانات، محرك قواعد يبني القيد من الحدث المحاسبي
القياسي، مصادر يومية أربعة (حدث/يدوي/متكرر-عكسي/توزيع) بدورة حياة موحدة (بناء → تحقق آلي →
ترحيل مباشر، لا اعتماد لكل قيد)، تصحيح بالعكس فقط، دورة حياة فترة محاسبية داخلية بالكامل
مع بوابة اعتماد واحدة عند الإغلاق، تقارير مالية مُشتقة حيًا مع تتبع نازل، تسجيل FIN في SEC
وMDL كبيانات.

**Out of scope:** تعدد العملات، تعدد الدفاتر/الكيانات والقيود البينية، الحسابات الإحصائية،
التقويم متعدد الأنماط، المرفقات — استبعاد صريح [business-policies-fin.md → SCOPE
EXCEPTIONS]؛ الوحدة التجارية، مستهلك الأحداث، طبقة النقل — خارج النطاق تمامًا
[general-accounting-system-plan-en.md §15].

**Module function (one paragraph):** FIN دفتر أستاذ عام قابل للتوصيل بأي نظام مضيف: يستقبل
حدثًا محاسبيًا قياسيًا فقط (لا قراءة ولا كتابة مباشرة لجداول المضيف)، يبني منه قيدًا متوازنًا
عبر قاعدة مُعرَّفة كبيانات، يرحّله مباشرة بعد تحقق آلي، ويشتق كل رصيد وتقرير من القيود
المُرحَّلة فقط — لا عمود رصيد مُخزَّن في أي مكان.

**Detailed description (workflow narrative, roles):** حدث محاسبي يصل → المحرك يحدد قاعدته
عبر نوع الحدث → يبني سطور القيد (اشتقاق حساب + مصدر مبلغ + اتجاه لكل سطر، مع سطر باقٍ ضامن
عند التوزيع النسبي) → تحقق آلي (توازن، أوراق نشطة قابلة للترحيل، أبعاد صالحة، فترة مفتوحة)
→ ترحيل مباشر. محاسب يُدخل قيودًا يدوية بنفس المسار. مراقب مالي (منفصل عن منشئ القيود) يعتمد
إغلاق الفترة فقط — نقطة التحكم البشري الوحيدة. كل التقارير تُشتق حيًا من القيود المُرحَّلة.

**Current situation:** لا نظام محاسبي سابق ضمن هذه الدفعة؛ FIN أول وحدة أعمال حقيقية تُبنى،
تستهلك SEC وMDL المكتملتين بالفعل.

**Current difficulties:** الأنظمة القديمة المشابهة (المصدر الملهم لهذا التصميم) تعتمد على
أعمدة رصيد مُخزَّنة تفقد تزامنها — بالضبط ما يحله POL-FIN-009.

**Proposed system and benefits:** محرك قواعد بيانات-محور يفصل منطق الحساب عن مصدر المبلغ،
دورة حياة قيد موحدة بلا اعتماد فردي يُسرّع التشغيل مع نقل الرقابة لمستوى الفترة، وأرصدة
مُشتقة دائمًا تضمن التطابق التام مع القيود الفعلية.

**General notes (constraints, deferred items):** لا محرك سير عمل؛ لا رقم حساب داخل حمولة
الحدث؛ الالتزام بحدود idempotency عند الحد الخارجي مفترض لا مُعاد تنفيذه [§12.12].

## A3 — Entities and fields

Standard fields per kind (profile.conventions.entity_defaults): master → nameAr, nameEn,
code, isActiveFl, createdBy, createdAt, updatedBy, updatedAt; transactional → docNo,
docDate, statusCode, fiscalYearId, periodId, createdBy, createdAt, updatedBy, updatedAt;
lookup → code, nameAr, nameEn, sortOrder, isActiveFl; config → key, valueAr, valueEn,
isActiveFl (adapted per entity below where the plan's own vocabulary differs, e.g. `code`
in place of a generic `key`, cited per field).

### ENT-FIN-001 — الحساب / Account
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | No — `code` is a client-defined chart-of-accounts code, not a platform-numbered sequence [§3.3 test] | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| accountPk | number | yes (system) | — | primary key | معرّف الحساب | Account id |
| code | text | yes | unique | chart-of-accounts code | رمز الحساب | Account code |
| nameAr | text | yes | — | — | اسم الحساب (عربي) | Account name (Arabic) |
| nameEn | text | yes | — | — | اسم الحساب (إنجليزي) | Account name (English) |
| accountTypeCode | lookup | yes | lookup key `ACCOUNT_TYPE` (A6) | asset/liability/equity/revenue/expense | نوع الحساب | Account type |
| natureCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | normal balance side [POL-FIN-002] | الطبيعة | Nature |
| parentAccountId | reference | no | ENT-FIN-001 (self) | null = root | الحساب الأب | Parent account |
| isLeafFl | flag | yes | — | accepts direct posting only when true [RULE-FIN-001, POL-FIN-003] | ورقة (يقبل ترحيلاً مباشرًا) | Leaf (accepts direct posting) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-002 — البُعد / Dimension
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, deactivate | none | general-accounting-system-plan-en.md §4.2 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| dimensionPk | number | yes (system) | — | primary key | معرّف البُعد | Dimension id |
| code | text | yes | unique | e.g. `PROJECT`, `INVESTOR` | رمز البُعد | Dimension code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-003 — قيمة البُعد / DimensionValue
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| lookup | PRIVATE | No | create, read, search, deactivate | none | general-accounting-system-plan-en.md §4.2 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| dimensionValuePk | number | yes (system) | — | primary key | معرّف قيمة البُعد | Dimension value id |
| dimensionId | reference | yes | ENT-FIN-002 | — | البُعد | Dimension |
| code | text | yes | unique within dimensionId [RULE-FIN-002] | — | الرمز | Code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| sortOrder | number | yes | — | — | ترتيب العرض | Sort order |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-004 — رأس قيد اليومية / JournalEntry
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | **Yes** — `docNo` is exactly the numbered transactional document case [§3.3 test (c)]: system-generated on first save, read-only after, unique per fiscal year. Format `JV-{fiscalYearCode}-{NNNNNN}` (e.g. `JV-2026-000123`), counter scoped per `fiscalYearId` and restarting at `000001` each year, one counter across all journal types, produced by a FIN-local generator in `com.erp.fin` — NOT a "platform numbering engine", which does not exist in this platform and never did | create (4 sources), read, search, reverse | none | general-accounting-system-plan-en.md §7, §8, §9 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalEntryPk | number | yes (system) | — | primary key | معرّف القيد | Journal entry id |
| docNo | text | yes (system) | FIN-local generator (`com.erp.fin`), format `JV-{fiscalYearCode}-{NNNNNN}`; unique per fiscalYearId (UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO) | read-only after create | رقم المستند | Document number |
| docDate | date | yes | — | — | تاريخ المستند | Document date |
| fiscalYearId | reference | yes | ENT-FIN-007 | — | السنة المالية | Fiscal year |
| periodId | reference | yes | ENT-FIN-008; must be Open at post [RULE-FIN-008] | — | الفترة | Period |
| journalTypeCode | lookup | yes | lookup key `JOURNAL_TYPE` (A6) | classifies the source | نوع اليومية | Journal type |
| statusCode | lookup | yes | lookup key `JOURNAL_STATUS` (A6) | drives A7 lifecycle | الحالة | Status |
| eventReference | text | no | unique when not null [RULE-FIN-004] | idempotency key for event-sourced entries [POL-FIN-012] | مرجع الحدث | Event reference |
| originalEntryId | reference | no | ENT-FIN-004 (self) | set on a reversal entry [POL-FIN-007] | القيد الأصلي | Original entry |
| reversalEntryId | reference | no | ENT-FIN-004 (self) | set on the original once reversed (bidirectional link) | قيد العكس | Reversal entry |
| descriptionAr | text | no | — | — | الوصف (عربي) | Description (Arabic) |
| descriptionEn | text | no | — | — | الوصف (إنجليزي) | Description (English) |
| postedAt | date-time | no (system) | set at post time | — | تاريخ الترحيل | Posted at |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields; immutable after posting [POL-FIN-013] | — | — |

### ENT-FIN-005 — سطر قيد اليومية / JournalLine
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | No | create (with header), read | none | general-accounting-system-plan-en.md §6, §8 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalLinePk | number | yes (system) | — | primary key | معرّف السطر | Line id |
| journalEntryId | reference | yes | ENT-FIN-004 | — | القيد | Journal entry |
| lineNo | number | yes | — | display/build order | رقم السطر | Line number |
| accountId | reference | yes | ENT-FIN-001; must be leaf+active [RULE-FIN-007] | — | الحساب | Account |
| amount | decimal | yes | always positive [RULE-FIN-006, POL-FIN-005] | `NUMERIC(18,4)` per [KB:erp-domain-standards §6] | المبلغ | Amount |
| directionCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | carries the sign, never the amount [POL-FIN-005] | الاتجاه | Direction |
| isRemainderFl | flag | yes | default false | marks the POL-FIN-006 guarantor line, at most one true per compound distribution [RULE-FIN-010] | سطر الباقي | Remainder line |
| descriptionAr | text | no | — | — | الوصف (عربي) | Description (Arabic) |
| descriptionEn | text | no | — | — | الوصف (إنجليزي) | Description (English) |
| createdAt | system | yes | — | lines are written atomically with the header, never edited independently | — | — |

### ENT-FIN-006 — بُعد سطر القيد / JournalLineDimension
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | No | create (with line), read | none | general-accounting-system-plan-en.md §4.3, §12.11 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalLineDimensionPk | number | yes (system) | — | primary key | معرّف بُعد السطر | Line dimension id |
| journalLineId | reference | yes | ENT-FIN-005 | — | سطر القيد | Journal line |
| dimensionId | reference | yes | ENT-FIN-002 | — | البُعد | Dimension |
| dimensionValueId | reference | yes | ENT-FIN-003; must belong to dimensionId and be active [RULE-FIN-009] | — | قيمة البُعد | Dimension value |

### ENT-FIN-007 — السنة المالية / FiscalYear
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | No | create, read, search | none | general-accounting-system-plan-en.md §10 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| fiscalYearPk | number | yes (system) | — | primary key | معرّف السنة المالية | Fiscal year id |
| code | text | yes | unique, e.g. `2026` | — | رمز السنة | Year code |
| startDate | date | yes | — | — | تاريخ البداية | Start date |
| endDate | date | yes | — | — | تاريخ النهاية | End date |
| statusCode | lookup | yes | lookup key `FISCAL_YEAR_STATUS` (A6) | — | الحالة | Status |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-008 — الفترة المحاسبية / FiscalPeriod
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | No | create, read, search, open, soft-close, hard-close | none | general-accounting-system-plan-en.md §10 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| fiscalPeriodPk | number | yes (system) | — | primary key | معرّف الفترة | Period id |
| fiscalYearId | reference | yes | ENT-FIN-007 | — | السنة المالية | Fiscal year |
| periodNo | number | yes | — | 1..N within the year | رقم الفترة | Period number |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| startDate | date | yes | — | — | تاريخ البداية | Start date |
| endDate | date | yes | — | — | تاريخ النهاية | End date |
| statusCode | lookup | yes | lookup key `PERIOD_STATE` (A6) | drives A7 lifecycle | الحالة | Status |
| closedBy | text | no | — | set at hard-close, by the approver [POL-FIN-016] | أُغلقت بواسطة | Closed by |
| closedAt | date-time | no | — | — | تاريخ الإغلاق | Closed at |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-009 — قاعدة نوع الحدث / EventTypeRule
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §6 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| eventTypeRuleId | number | yes (system) | — | primary key | معرّف قاعدة الحدث | Event type rule id |
| eventTypeCode | lookup | yes | lookup key `ACCOUNTING_EVENT_TYPE` (A6); unique | one rule per event type [§6.4] | نوع الحدث | Event type |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-010 — سطر القاعدة / RuleLine
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create (with rule), read, update, delete | none | general-accounting-system-plan-en.md §6.2, §6.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| ruleLineId | number | yes (system) | — | primary key | معرّف سطر القاعدة | Rule line id |
| eventTypeRuleId | reference | yes | ENT-FIN-009 | — | قاعدة الحدث | Event type rule |
| lineNo | number | yes | — | — | رقم السطر | Line number |
| accountDerivationTypeCode | lookup | yes | lookup key `ACCOUNT_DERIVATION_TYPE` (A6) | constant / direct / mapping [§6.2(a)] | نوع اشتقاق الحساب | Account derivation type |
| accountDerivationValue | text | yes | interpreted per accountDerivationTypeCode | constant account code, event field name, or mapping-set key | قيمة الاشتقاق | Derivation value |
| amountSourceTypeCode | lookup | yes | lookup key `AMOUNT_SOURCE_TYPE` (A6) | field / percentage / remainder [§6.2(b)] | نوع مصدر المبلغ | Amount source type |
| amountSourceValue | text | no | event field name or percentage figure | required unless amountSourceTypeCode=REMAINDER | قيمة مصدر المبلغ | Amount source value |
| directionCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | — | الاتجاه | Direction |
| distributionTypeCode | lookup | yes | lookup key `DISTRIBUTION_TYPE` (A6) | fixed / percentage / remainder [§6.3] | نوع التوزيع | Distribution type |
| isRemainderFl | flag | yes | default false | exactly one true per rule when any line is PERCENTAGE [RULE-FIN-003] | سطر الباقي | Remainder line |
| createdAt | system | yes | — | — | — | — |

### ENT-FIN-011 — قالب متكرر/عكسي / RecurringTemplate
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §7.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| recurringTemplateId | number | yes (system) | — | primary key | معرّف القالب | Template id |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| scheduleTypeCode | lookup | yes | lookup key `RECURRING_SCHEDULE_TYPE` (A6) | recurring / reversing | نوع الجدولة | Schedule type |
| frequencyCode | lookup | yes (when scheduleTypeCode=RECURRING) | lookup key `RECURRING_FREQUENCY` (A6) | not applicable to a pure reversing template | التكرار | Frequency |
| startDate | date | yes | — | — | تاريخ البدء | Start date |
| nextRunDate | date | yes (system-maintained) | — | advances after each run | تاريخ التشغيل القادم | Next run date |
| endDate | date | no | — | — | تاريخ الانتهاء | End date |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-012 — سطر القالب المتكرر / RecurringTemplateLine
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create (with template), read, update, delete | none | general-accounting-system-plan-en.md §7.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| recurringTemplateLineId | number | yes (system) | — | primary key | معرّف سطر القالب | Template line id |
| recurringTemplateId | reference | yes | ENT-FIN-011 | — | القالب | Template |
| lineNo | number | yes | — | — | رقم السطر | Line number |
| accountId | reference | yes | ENT-FIN-001; must be leaf+active at run time [RULE-FIN-007, reused] | — | الحساب | Account |
| amount | decimal | yes | positive [RULE-FIN-006, reused] | — | المبلغ | Amount |
| directionCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | — | الاتجاه | Direction |
| dimensionValueId | reference | no | ENT-FIN-003 | single optional dimension per line — a simplification vs the header's multi-dimension model (§9.3.3, AUTO-DECISION) | قيمة البُعد | Dimension value |
| createdAt | system | yes | — | — | — | — |

### ENT-FIN-013 — قاعدة توزيع / AllocationRule
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §7.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| allocationRuleId | number | yes (system) | — | primary key | معرّف قاعدة التوزيع | Allocation rule id |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| sourceAccountId | reference | yes | ENT-FIN-001 | the balance being distributed | الحساب المصدر | Source account |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-014 — هدف التوزيع / AllocationTarget
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create (with rule), read, update, delete | none | general-accounting-system-plan-en.md §7.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| allocationTargetId | number | yes (system) | — | primary key | معرّف هدف التوزيع | Allocation target id |
| allocationRuleId | reference | yes | ENT-FIN-013 | — | قاعدة التوزيع | Allocation rule |
| lineNo | number | yes | — | — | رقم السطر | Line number |
| targetAccountId | reference | yes | ENT-FIN-001 | — | الحساب الهدف | Target account |
| dimensionValueId | reference | no | ENT-FIN-003 | single optional dimension (same simplification as ENT-FIN-012) | قيمة البُعد | Dimension value |
| distributionTypeCode | lookup | yes | lookup key `DISTRIBUTION_TYPE` (A6) | fixed / percentage / remainder [§6.3, reused for allocations §7.4] | نوع التوزيع | Distribution type |
| distributionValue | decimal | no | required unless distributionTypeCode=REMAINDER | — | قيمة التوزيع | Distribution value |
| isRemainderFl | flag | yes | default false | exactly one true per rule when any target is PERCENTAGE [RULE-FIN-003, reused] | هدف الباقي | Remainder target |

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-FIN-001 — إنشاء حساب / Create an account
Pattern    : event
Statement  : When a finance administrator creates an account, the system shall record its code, bilingual name, type and nature within the chart hierarchy.
Traces     : US-FIN-001
Entities   : ENT-FIN-001
Rationale  : the reference structure that determines where values are recorded
Source     : general-accounting-system-plan-en.md §4.1-§4.2
Priority   : HIGH
#### AC-FIN-001 — [REQ-FIN-001]
Given a unique code, bilingual name, account type and nature, optionally a parent account
When a finance administrator submits the account form
Then the system creates the account

### REQ-FIN-002 — رفض ترحيل مباشر لحساب له أبناء / Reject direct-posting on an account with children
Pattern    : unwanted
Statement  : If an account has any child account, then the system shall prevent it from being marked as accepting direct posting.
Traces     : US-FIN-001
Entities   : ENT-FIN-001
Rationale  : RULE-FIN-001; POL-FIN-003 — only leaves accept postings
Source     : general-accounting-system-plan-en.md §4.2
Priority   : HIGH
#### AC-FIN-002 — [REQ-FIN-002]
Given an account with at least one child account
When an administrator attempts to mark it as accepting direct posting (isLeafFl=true)
Then the system rejects the change

### REQ-FIN-003 — تعطيل حساب / Deactivate an account
Pattern    : event
Statement  : When a finance administrator deactivates an account, the system shall block any future posting to it.
Traces     : US-FIN-001
Entities   : ENT-FIN-001
Rationale  : POL-FIN-003
Source     : general-accounting-system-plan-en.md §4.2
Priority   : MEDIUM
#### AC-FIN-003 — [REQ-FIN-003]
Given an active account
When an administrator deactivates it
Then the system sets isActiveFl=false and REQ-FIN-019 subsequently rejects any posting to it

### REQ-FIN-004 — إنشاء بُعد / Create a dimension
Pattern    : event
Statement  : When a finance administrator creates a dimension, the system shall record it as an active dimension available for account combinations.
Traces     : US-FIN-002
Entities   : ENT-FIN-002
Rationale  : dimensions defined as data, a governing design constraint
Source     : general-accounting-system-plan-en.md §4.2-§4.3
Priority   : HIGH
#### AC-FIN-004 — [REQ-FIN-004]
Given a unique code and bilingual name
When an administrator submits the dimension form
Then the system creates an active Dimension

### REQ-FIN-005 — إنشاء قيمة بُعد / Create a dimension value
Pattern    : event
Statement  : When a finance administrator creates a value under a dimension, the system shall record its code, bilingual name and sort order.
Traces     : US-FIN-002
Entities   : ENT-FIN-003
Rationale  : §4.2
Source     : general-accounting-system-plan-en.md §4.2
Priority   : HIGH
#### AC-FIN-005 — [REQ-FIN-005]
Given a selected dimension and a code not yet used under it
When an administrator submits the value form
Then the system creates the DimensionValue

### REQ-FIN-006 — رفض رمز مكرر ضمن البُعد / Reject a duplicate code within a dimension
Pattern    : unwanted
Statement  : If two dimension values under the same dimension share the same code, then the system shall reject the second.
Traces     : US-FIN-002
Entities   : ENT-FIN-003
Rationale  : RULE-FIN-002
Source     : general-accounting-system-plan-en.md §4.2
Priority   : MEDIUM
#### AC-FIN-006 — [REQ-FIN-006]
Given a dimension already holding a value with code "NORTH"
When a second value with code "NORTH" is created under the same dimension
Then the system rejects it

### REQ-FIN-007 — إنشاء قاعدة نوع حدث / Create an event-type rule
Pattern    : event
Statement  : When a finance administrator creates a rule for an event type, the system shall record it as the single active rule for that type.
Traces     : US-FIN-003
Entities   : ENT-FIN-009
Rationale  : §6.4 — one rule per event type
Source     : general-accounting-system-plan-en.md §6.1, §6.4
Priority   : HIGH
#### AC-FIN-007 — [REQ-FIN-007]
Given an event type registered in MDL with no existing rule
When an administrator creates a rule for it
Then the system creates an active EventTypeRule

### REQ-FIN-008 — إضافة سطر قاعدة / Add a rule line
Pattern    : event
Statement  : When a finance administrator adds a line to an event-type rule, the system shall record its account derivation, amount source and direction as three separate references.
Traces     : US-FIN-003
Entities   : ENT-FIN-010
Rationale  : POL-FIN-014; §6.2 separation of (a) and (b) is deliberate
Source     : general-accounting-system-plan-en.md §6.2
Priority   : HIGH
#### AC-FIN-008 — [REQ-FIN-008]
Given an event-type rule
When an administrator adds a line with an account-derivation spec, an amount-source spec and a direction
Then the system creates the RuleLine

### REQ-FIN-009 — رفض عدد غير صحيح من سطور الباقي / Reject an incorrect remainder-line count
Pattern    : unwanted
Statement  : If an event-type rule's lines include any percentage-distribution line, then the system shall require exactly one line marked as the remainder.
Traces     : US-FIN-003
Entities   : ENT-FIN-010
Rationale  : RULE-FIN-003; POL-FIN-006
Source     : general-accounting-system-plan-en.md §6.3, §12.6
Priority   : HIGH
#### AC-FIN-009 — [REQ-FIN-009]
Given a rule with two PERCENTAGE-distribution lines and zero lines marked remainder
When an administrator attempts to save the rule
Then the system rejects it until exactly one line is marked remainder

### REQ-FIN-010 — بناء قيد من حدث / Build an entry from an event
Pattern    : event
Statement  : When a canonical accounting event arrives, the system shall build a journal entry from it using its event type's active rule.
Traces     : US-FIN-004
Entities   : ENT-FIN-004, ENT-FIN-005, ENT-FIN-009, ENT-FIN-010
Rationale  : POL-FIN-014, POL-FIN-020 — no host-specific logic, only rule + event data
Source     : general-accounting-system-plan-en.md §7.1
Priority   : HIGH
#### AC-FIN-010 — [REQ-FIN-010]
Given a canonical event with a type that has an active rule
When the event arrives
Then the system builds a DRAFT journal entry whose lines follow the rule, then proceeds to REQ-FIN-017 (validate + post)

### REQ-FIN-011 — رفض مرجع حدث مكرر / Reject a duplicate event reference
Pattern    : unwanted
Statement  : If a canonical event's reference has already produced a posted entry, then the system shall reject a second entry for the same reference.
Traces     : US-FIN-004
Entities   : ENT-FIN-004
Rationale  : RULE-FIN-004; POL-FIN-012 — boundary idempotency is assumed, a repeat is a defect
Source     : general-accounting-system-plan-en.md §12.12
Priority   : HIGH
#### AC-FIN-011 — [REQ-FIN-011]
Given a POSTED entry with eventReference "EVT-1001"
When another event with reference "EVT-1001" arrives
Then the system rejects building a second entry for it

### REQ-FIN-012 — امتصاص فرق التقريب عبر سطر الباقي / Absorb the rounding difference via the remainder line
Pattern    : event
Statement  : When a rule's lines produce a compound or percentage distribution, the system shall compute the remainder line's amount as the original amount minus the sum of every other line, after each percentage line is rounded to the smallest currency unit.
Traces     : US-FIN-004
Entities   : ENT-FIN-005, ENT-FIN-010
Rationale  : RULE-FIN-010; POL-FIN-006
Source     : general-accounting-system-plan-en.md §6.3
Priority   : HIGH
#### AC-FIN-012 — [REQ-FIN-012]
Given a rule distributing 100.00 as 33% + 33% + remainder
When the entry is built
Then the two percentage lines total 66.00 (each rounded to the smallest currency unit) and the remainder line is exactly 34.00, so the entry balances exactly

### REQ-FIN-013 — رفض حدث بلا قاعدة نشطة / Reject an event with no active rule
Pattern    : unwanted
Statement  : If an event's type has no active event-type rule, then the system shall reject building an entry for it.
Traces     : US-FIN-004
Entities   : ENT-FIN-009
Rationale  : the engine applies rules, it never guesses
Source     : general-accounting-system-plan-en.md §6.1
Priority   : MEDIUM
#### AC-FIN-013 — [REQ-FIN-013]
Given an event type with no active EventTypeRule
When an event of that type arrives
Then the system rejects building an entry and records the failure for operator follow-up

### REQ-FIN-014 — إدخال يدوي / Create a manual journal entry
Pattern    : event
Statement  : When an accountant creates a manual journal entry with its lines, the system shall build it exactly as any other source, then proceed through the same validation and posting path.
Traces     : US-FIN-005
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : POL-FIN-001, POL-FIN-018 — one unified rule for every source
Source     : general-accounting-system-plan-en.md §7.2
Priority   : HIGH
#### AC-FIN-014 — [REQ-FIN-014]
Given a fiscal period, at least two balanced lines with leaf active accounts
When an accountant submits the manual entry form
Then the system builds a DRAFT entry and proceeds to REQ-FIN-017

### REQ-FIN-015 — عرض تفاصيل الفشل قبل الترحيل / Show validation failures before posting
Pattern    : event
Statement  : When a manual entry fails automatic validation, the system shall return every failing check to the accountant without posting anything.
Traces     : US-FIN-005
Entities   : ENT-FIN-004
Rationale  : usable error feedback for the one path with a live human editor
Source     : general-accounting-system-plan-en.md §8.1
Priority   : MEDIUM
#### AC-FIN-015 — [REQ-FIN-015]
Given a manual entry with two failing validations
When the accountant submits it
Then the system returns both failures and posts nothing

### REQ-FIN-016 — إبقاء السجل دون حذف فعلي / Retain records without hard deletion
Pattern    : ubiquitous
Statement  : The system shall retain every posted journal entry's record permanently, never hard-deleting it.
Traces     : US-FIN-008
Entities   : ENT-FIN-004
Rationale  : POL-FIN-013
Source     : general-accounting-system-plan-en.md §12.13
Priority   : HIGH
#### AC-FIN-016 — [REQ-FIN-016]
Given a POSTED journal entry
When any attempt is made to delete it
Then the system rejects the delete — the only path that changes its effect is a reversal (REQ-FIN-028)

### REQ-FIN-017 — تحقق آلي وترحيل مباشر موحّد / Unified automatic validation and direct posting
Pattern    : event
Statement  : When any journal entry, regardless of source, passes automatic validation, the system shall post it directly with no separate human approval step.
Traces     : US-FIN-004, US-FIN-005, US-FIN-006, US-FIN-007, US-FIN-009
Entities   : ENT-FIN-004
Rationale  : POL-FIN-001, POL-FIN-003, POL-FIN-004, POL-FIN-018 — the single unified rule
Source     : general-accounting-system-plan-en.md §8.1
Priority   : HIGH
#### AC-FIN-017 — [REQ-FIN-017]
Given a DRAFT entry that passes every check in REQ-FIN-018..021
When validation completes
Then the system sets statusCode=POSTED, postedAt=now(), and the entry becomes fully locked (no edit, no delete — REQ-FIN-034-equivalent lock, POL-FIN-013)

### REQ-FIN-018 — رفض عدم توازن القيد / Reject an unbalanced entry
Pattern    : unwanted
Statement  : If a journal entry's total debits do not equal its total credits, then the system shall reject posting.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : RULE-FIN-006; POL-FIN-001
Source     : general-accounting-system-plan-en.md §12.1
Priority   : HIGH
#### AC-FIN-018 — [REQ-FIN-018]
Given a DRAFT entry with debit lines totaling 100.00 and credit lines totaling 99.99
When the system validates it
Then it rejects posting with the imbalance amount shown

### REQ-FIN-019 — رفض حساب غير مؤهَّل للترحيل / Reject a non-postable account
Pattern    : unwanted
Statement  : If a journal line targets an account that is not a leaf, not active, or not marked as accepting direct posting, then the system shall reject posting.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-001, ENT-FIN-005
Rationale  : RULE-FIN-007; POL-FIN-003
Source     : general-accounting-system-plan-en.md §12.3
Priority   : HIGH
#### AC-FIN-019 — [REQ-FIN-019]
Given a DRAFT entry with a line targeting a non-leaf (rollup) account
When the system validates it
Then it rejects posting, naming the offending line

### REQ-FIN-020 — رفض فترة مغلقة عند الترحيل / Reject a closed period at post time
Pattern    : unwanted
Statement  : If a journal entry's period is not Open at the moment of posting, then the system shall reject posting, even if it was Open when the entry was built.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-004, ENT-FIN-008
Rationale  : RULE-FIN-008; POL-FIN-004 — checked at post time, not build time
Source     : general-accounting-system-plan-en.md §12.4
Priority   : HIGH
#### AC-FIN-020 — [REQ-FIN-020]
Given a DRAFT entry whose period was Open when built but is now Hard Closed
When the system attempts to post it
Then it rejects posting citing the period's current state

### REQ-FIN-021 — رفض قيمة بُعد غير صالحة / Reject an invalid dimension value
Pattern    : unwanted
Statement  : If a journal line cites a dimension value that does not belong to its stated dimension or is inactive, then the system shall reject posting.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-006
Rationale  : RULE-FIN-009
Source     : general-accounting-system-plan-en.md §8.1 ("dimension valid")
Priority   : MEDIUM
#### AC-FIN-021 — [REQ-FIN-021]
Given a DRAFT entry line citing an inactive DimensionValue
When the system validates it
Then it rejects posting, naming the offending line and dimension

### REQ-FIN-022 — إنشاء قالب متكرر/عكسي / Create a recurring or reversing template
Pattern    : event
Statement  : When an accountant creates a recurring or reversing template with its lines, the system shall record its schedule and store it for future runs.
Traces     : US-FIN-006
Entities   : ENT-FIN-011, ENT-FIN-012
Rationale  : §7.3 — templates defined once as data
Source     : general-accounting-system-plan-en.md §7.3
Priority   : MEDIUM
#### AC-FIN-022 — [REQ-FIN-022]
Given a schedule type, a frequency (for recurring) and at least two balanced lines
When an accountant submits the template form
Then the system creates the active RecurringTemplate

### REQ-FIN-023 — تشغيل قالب متكرر / Run a recurring template on schedule
Pattern    : event
Statement  : When a recurring template's next run date arrives, the system shall generate and post a journal entry from it exactly as REQ-FIN-017 describes.
Traces     : US-FIN-006
Entities   : ENT-FIN-004, ENT-FIN-011
Rationale  : §7.3
Source     : general-accounting-system-plan-en.md §7.3
Priority   : MEDIUM
#### AC-FIN-023 — [REQ-FIN-023]
Given an active recurring template whose nextRunDate is today
When the scheduled run executes
Then the system builds and posts one entry from the template and advances nextRunDate per its frequency

### REQ-FIN-024 — عكس تلقائي في الفترة التالية / Automatic reversal in the next period
Pattern    : event
Statement  : When a reversing template's entry posts, the system shall automatically build and post its exact reversal in the next period.
Traces     : US-FIN-006
Entities   : ENT-FIN-004
Rationale  : §7.3; POL-FIN-007
Source     : general-accounting-system-plan-en.md §7.3
Priority   : MEDIUM
#### AC-FIN-024 — [REQ-FIN-024]
Given a reversing-type template entry posted in period N
When period N+1 opens (or immediately, per the template's own trigger)
Then the system posts a linked reversal entry in period N+1

### REQ-FIN-025 — إنشاء قاعدة توزيع / Create an allocation rule
Pattern    : event
Statement  : When an accountant creates an allocation rule with its targets, the system shall record how the source account's balance distributes across them.
Traces     : US-FIN-007
Entities   : ENT-FIN-013, ENT-FIN-014
Rationale  : §7.4
Source     : general-accounting-system-plan-en.md §7.4
Priority   : MEDIUM
#### AC-FIN-025 — [REQ-FIN-025]
Given a source account and at least one target with a distribution type
When an accountant submits the allocation rule form
Then the system creates the active AllocationRule

### REQ-FIN-026 — تشغيل قاعدة توزيع / Run an allocation rule
Pattern    : event
Statement  : When an allocation rule runs, the system shall distribute the source account's current balance across its targets per their distribution type, applying the same remainder guarantee as any compound distribution.
Traces     : US-FIN-007
Entities   : ENT-FIN-004, ENT-FIN-013, ENT-FIN-014
Rationale  : §7.4; RULE-FIN-010 reused
Source     : general-accounting-system-plan-en.md §7.4, §6.3
Priority   : MEDIUM
#### AC-FIN-026 — [REQ-FIN-026]
Given an allocation rule with two PERCENTAGE targets and one REMAINDER target, and a source balance of 1,000.00
When an accountant runs it
Then the system builds and posts one entry whose target lines sum exactly to 1,000.00, the remainder target absorbing the rounding difference

### REQ-FIN-027 — عرض/بحث قيود اليومية / Search and view journal entries
Pattern    : event
Statement  : When an accountant searches journal entries, the system shall return matching entries with their full status detail, unmodified.
Traces     : US-FIN-008
Entities   : ENT-FIN-004
Rationale  : POL-FIN-013
Source     : general-accounting-system-plan-en.md §8.4
Priority   : HIGH
#### AC-FIN-027 — [REQ-FIN-027]
Given entries across several statuses and periods
When an accountant filters by period and status
Then the system returns exactly the matching entries, unmodified

### REQ-FIN-028 — عكس قيد / Reverse a posted entry
Pattern    : event
Statement  : When an accountant reverses a posted entry, the system shall build and post a new entry mirroring it line-for-line with opposite directions and equal amounts, linked bidirectionally to the original.
Traces     : US-FIN-009
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : RULE-FIN-011; POL-FIN-007
Source     : general-accounting-system-plan-en.md §9
Priority   : HIGH
#### AC-FIN-028 — [REQ-FIN-028]
Given a POSTED entry with three lines
When an accountant reverses it
Then the system posts a new entry with the same three lines' amounts and opposite directions, and both entries reference each other (originalEntryId/reversalEntryId)

### REQ-FIN-029 — ترحيل العكس في الفترة الحالية عند إغلاق الأصل / Post the reversal in the current period when the original's period is closed
Pattern    : event
Statement  : When the original entry's period is closed, the system shall post its reversal into the current open period instead.
Traces     : US-FIN-009
Entities   : ENT-FIN-004, ENT-FIN-008
Rationale  : RULE-FIN-012
Source     : general-accounting-system-plan-en.md §9
Priority   : MEDIUM
#### AC-FIN-029 — [REQ-FIN-029]
Given a POSTED entry whose period is now Hard Closed
When an accountant reverses it
Then the system posts the reversal into the current open period, not the closed one

### REQ-FIN-030 — رفض عكس قيد غير مُرحَّل / Reject reversing a non-posted entry
Pattern    : unwanted
Statement  : If an entry is not POSTED, then the system shall reject a reverse action on it.
Traces     : US-FIN-009
Entities   : ENT-FIN-004
Rationale  : RULE-FIN-013 — prevents double-reversal (an entry that already carries a reversal link) or reversing a DRAFT row
Source     : general-accounting-system-plan-en.md §9
Priority   : MEDIUM
#### AC-FIN-030 — [REQ-FIN-030]
Given an entry already reversed once (it stays POSTED and carries a reversalEntryId link to its reversal)
When an accountant attempts to reverse it again
Then the system rejects the action

### REQ-FIN-031 — إنشاء سنة مالية وفتراتها / Create a fiscal year with its periods
Pattern    : event
Statement  : When a finance administrator creates a fiscal year, the system shall generate its periods in the Open state per the chosen calendar. As built: a `periodCount` of twelve over a whole year generates the twelve calendar months, named from the JDK's CLDR month names in Arabic and English; any other count falls back to an even day split named "الفترة N" / "Period N".
Traces     : US-FIN-010
Entities   : ENT-FIN-007, ENT-FIN-008
Rationale  : §10.1-§10.2
Source     : general-accounting-system-plan-en.md §10.1, §10.4
Priority   : HIGH
#### AC-FIN-031 — [REQ-FIN-031]
Given a start date, end date and period count
When an administrator creates the fiscal year
Then the system creates the year and its periods, each initially Open

### REQ-FIN-032 — فتح فترة / Open a period
Pattern    : event
Statement  : When a finance administrator opens a period, the system shall allow normal posting into it.
Traces     : US-FIN-010
Entities   : ENT-FIN-008
Rationale  : §10.2
Source     : general-accounting-system-plan-en.md §10.2
Priority   : MEDIUM
#### AC-FIN-032 — [REQ-FIN-032]
Given a period not currently Open
When an administrator reopens it (soft-closed only, per §10.2 "re-openable")
Then the system sets statusCode=OPEN

### REQ-FIN-033 — إغلاق ناعم لفترة / Soft-close a period
Pattern    : event
Statement  : When a finance administrator soft-closes a period, the system shall block normal posting into it while still allowing authorized adjustments.
Traces     : US-FIN-010
Entities   : ENT-FIN-008
Rationale  : §10.2
Source     : general-accounting-system-plan-en.md §10.2
Priority   : MEDIUM
#### AC-FIN-033 — [REQ-FIN-033]
Given an Open period
When an administrator soft-closes it
Then the system sets statusCode=SOFT_CLOSE and REQ-FIN-020 rejects normal (non-adjustment) postings to it thereafter

### REQ-FIN-034 — إغلاق صارم لفترة / Hard-close a period
Pattern    : event
Statement  : When an authorized approver hard-closes a period, the system shall permanently block any posting into it.
Traces     : US-FIN-010, US-FIN-011
Entities   : ENT-FIN-008
Rationale  : §10.2-§10.3
Source     : general-accounting-system-plan-en.md §10.2, §10.3
Priority   : HIGH
#### AC-FIN-034 — [REQ-FIN-034]
Given a Soft Closed period
When an authorized approver hard-closes it
Then the system sets statusCode=HARD_CLOSE, closedBy and closedAt, and the period becomes permanently not re-openable

### REQ-FIN-035 — رفض إعادة فتح فترة مغلقة صارمًا / Reject reopening a hard-closed period
Pattern    : unwanted
Statement  : If a period is Hard Closed, then the system shall reject any attempt to reopen it.
Traces     : US-FIN-010
Entities   : ENT-FIN-008
Rationale  : RULE-FIN-014 — "not re-openable" per §10.2
Source     : general-accounting-system-plan-en.md §10.2
Priority   : MEDIUM
#### AC-FIN-035 — [REQ-FIN-035]
Given a Hard Closed period
When an administrator attempts to reopen it
Then the system rejects the action

### REQ-FIN-036 — تشغيل إقفال نهاية السنة / Run year-end close
Pattern    : event
Statement  : When an authorized approver runs year-end close for a fiscal year whose periods are all Hard Closed, the system shall generate a balanced closing entry and a balanced opening entry for the next year.
Traces     : US-FIN-010
Entities   : ENT-FIN-004, ENT-FIN-007
Rationale  : POL-FIN-010
Source     : general-accounting-system-plan-en.md §10.4
Priority   : HIGH
#### AC-FIN-036 — [REQ-FIN-036]
Given a fiscal year with every period Hard Closed
When an approver runs year-end close
Then the system posts a closing entry (result accounts → Retained Earnings) and generates the next year's opening entry from the resulting balance-sheet balances, both entries individually balanced

### REQ-FIN-037 — تسجيل اعتماد إغلاق الفترة / Record period-close approval distinctly
Pattern    : event
Statement  : When an authorized approver closes a period, the system shall record that approval as a distinct act from any entry creation in that period.
Traces     : US-FIN-011
Entities   : ENT-FIN-008
Rationale  : §8.2, §10.3 — the single human control point
Source     : general-accounting-system-plan-en.md §8.2, §10.3
Priority   : HIGH
#### AC-FIN-037 — [REQ-FIN-037]
Given a period ready to hard-close
When the approval is recorded
Then closedBy and closedAt are set to the approving principal and moment, distinct from any entry's createdBy in that period

### REQ-FIN-038 — فصل صلاحية الاعتماد عن صلاحية الإنشاء / Separate the approval permission from the creation permission
Pattern    : ubiquitous
Statement  : The system shall gate the period-close-approval action behind a permission distinct from the journal-entry-creation permission, enforced by the Security module.
Traces     : US-FIN-011
Entities   : ENT-FIN-008
Rationale  : POL-FIN-016; RULE-FIN-015
Source     : general-accounting-system-plan-en.md §2.2, §8.2, §10.3
Priority   : HIGH
#### AC-FIN-038 — [REQ-FIN-038]
Given a role holding only the entry-creation permission
When that role's user attempts the period-close-approval action
Then the system denies it (the CORE interceptor, per SEC's own mechanism)

### REQ-FIN-039 — دفتر الحساب المُشتق حيًا / Live-derived account ledger
Pattern    : event
Statement  : When an accountant opens the account ledger for an account and period range, the system shall compute it from POSTED lines at that moment.
Traces     : US-FIN-012
Entities   : ENT-FIN-005
Rationale  : POL-FIN-009, POL-FIN-011
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-039 — [REQ-FIN-039]
Given an account with posted lines across two periods
When the ledger is opened for that range
Then the system computes the running balance live from those lines, never from a stored column

### REQ-FIN-040 — ميزان مراجعة مُشتق حيًا ومتوازن دائمًا / Live-derived, always-balanced trial balance
Pattern    : event
Statement  : When a financial controller opens the trial balance for a period, the system shall compute it from POSTED lines such that total debit balances equal total credit balances.
Traces     : US-FIN-013
Entities   : ENT-FIN-005
Rationale  : POL-FIN-008, POL-FIN-009
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-040 — [REQ-FIN-040]
Given any set of POSTED entries in a period
When the trial balance is generated
Then its total debit balances equal its total credit balances exactly

### REQ-FIN-041 — ميزانية عمومية مع استمرارية / Balance sheet with continuity
Pattern    : event
Statement  : When a financial controller opens the balance sheet, the system shall compute balance-sheet account balances from POSTED lines, consistent with the prior year's closing balances as this year's opening balances.
Traces     : US-FIN-014
Entities   : ENT-FIN-005
Rationale  : POL-FIN-002, POL-FIN-009, POL-FIN-010
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-041 — [REQ-FIN-041]
Given a completed year-end close (REQ-FIN-036)
When the new year's balance sheet is opened
Then its opening balances equal the prior year's closing balances for every balance-sheet account

### REQ-FIN-042 — قائمة دخل تُفتح بصفر / Income statement opening at zero
Pattern    : event
Statement  : When a financial controller opens the income statement for a new fiscal year, the system shall compute result-account balances starting from zero for that year.
Traces     : US-FIN-015
Entities   : ENT-FIN-005
Rationale  : POL-FIN-002, POL-FIN-010
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-042 — [REQ-FIN-042]
Given a completed year-end close
When the new year's income statement is opened before any posting
Then every revenue/expense account shows a zero balance

### REQ-FIN-043 — تقارير أبعاد دون تكرار الحسابات / Dimension reports without duplicating accounts
Pattern    : event
Statement  : When a financial controller opens a dimension report, the system shall aggregate POSTED lines by the full account-and-dimension combination, never by the base account alone when a dimension is in play.
Traces     : US-FIN-016
Entities   : ENT-FIN-005, ENT-FIN-006
Rationale  : POL-FIN-011
Source     : general-accounting-system-plan-en.md §11, §12.11
Priority   : MEDIUM
#### AC-FIN-043 — [REQ-FIN-043]
Given postings to one account under two different PROJECT dimension values
When the dimension report is generated by PROJECT
Then the system shows two separate rows for that account, one per project, not one combined row

### REQ-FIN-044 — تسجيل FIN في وحدة الأمان / Register FIN into the Security module
Pattern    : event
Statement  : When FIN is deployed, the system shall register its module, screens and every action as data into the Security module.
Traces     : US-FIN-017
Entities   : ENT-FIN-004
Rationale  : POL-FIN-015
Source     : general-accounting-system-plan-en.md §2.2, §2.4
Priority   : HIGH
#### AC-FIN-044 — [REQ-FIN-044]
Given SEC v1 is gated and reachable
When FIN's onboarding runs
Then SEC records one ModuleRegistry row for FIN, one ScreenRegistry row per FIN screen, and one ActionRegistry row per action

### REQ-FIN-045 — تسجيل قوائم FIN في MDL / Register FIN's lookup types into the Lookup module
Pattern    : event
Statement  : When FIN is deployed, the system shall register its 13 lookup types as data into the Lookup module, naming FIN as owner.
Traces     : US-FIN-018
Entities   : ENT-FIN-001, ENT-FIN-004, ENT-FIN-007, ENT-FIN-008, ENT-FIN-009, ENT-FIN-010, ENT-FIN-011, ENT-FIN-013
Rationale  : POL-FIN-017
Source     : general-accounting-system-plan-en.md §5.2-§5.3
Priority   : HIGH
#### AC-FIN-045 — [REQ-FIN-045]
Given MDL v1 is gated and reachable
When FIN's onboarding runs
Then MDL records 13 LookupType rows owned by FIN (module-registry-fin.md → LOOKUPS OWNED)

### REQ-FIN-046 — تتبع نازل من التقرير إلى الحدث / Drill down from a report to its source event
Pattern    : event
Statement  : When a financial controller drills down from a financial-statement line, the system shall lead through the trial balance to the account ledger, to the original entry, to its source event reference.
Traces     : US-FIN-019
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : POL-FIN-013
Source     : general-accounting-system-plan-en.md §11
Priority   : MEDIUM
#### AC-FIN-046 — [REQ-FIN-046]
Given a balance-sheet line
When a controller drills into it
Then the system navigates statement line → trial balance row → account ledger → the originating entry → its eventReference (or "manual", "recurring", "allocation" if not event-sourced)

## A5 — Business rules

### RULE-FIN-001 — منع ترحيل مباشر لحساب له أبناء / No direct posting on an account with children
Scope      : ENT-FIN-001
Trigger    : on update (isLeafFl)
Statement  : The system shall prevent an account with any child account from being marked as accepting direct posting.
Data source: ENT-FIN-001.parentAccountId, ENT-FIN-001.isLeafFl
Message    : ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" · en: "An account with sub-accounts cannot accept direct posting"
Traces     : REQ-FIN-002
Source     : general-accounting-system-plan-en.md §4.2

### RULE-FIN-002 — رفض رمز مكرر ضمن البُعد / Reject a duplicate code within a dimension
Scope      : ENT-FIN-003
Trigger    : on create (dimension value)
Statement  : The system shall reject a dimension value whose code already exists under the same dimension.
Data source: ENT-FIN-003.code, ENT-FIN-003.dimensionId
Message    : ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" · en: "This code is already used within this dimension"
Traces     : REQ-FIN-006
Source     : general-accounting-system-plan-en.md §4.2

### RULE-FIN-003 — سطر/هدف باقٍ واحد بالضبط عند التوزيع النسبي / Exactly one remainder line/target under percentage distribution
Scope      : ENT-FIN-010, ENT-FIN-014
Trigger    : on create/update (rule line or allocation target set)
Statement  : The system shall require exactly one line or target marked as the remainder whenever the set forms a compound or percentage distribution — that is, whenever any sibling line or target uses percentage distribution, or any line or target is already marked as the remainder (POL-FIN-006). The marker is `isRemainderFl`; a line or target whose marker disagrees with its own REMAINDER distribution/amount-source type code is rejected, since which line is the remainder decides every other line's amount under RULE-FIN-010.
Data source: ENT-FIN-010.isRemainderFl, ENT-FIN-010.distributionTypeCode, ENT-FIN-014.isRemainderFl, ENT-FIN-014.distributionTypeCode
Message    : ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" · en: "Exactly one remainder line is required when any percentage distribution is present"
Traces     : REQ-FIN-009
Source     : general-accounting-system-plan-en.md §6.3, §12.6

### RULE-FIN-004 — رفض مرجع حدث مكرر / Reject a duplicate event reference
Scope      : ENT-FIN-004
Trigger    : on create (event-sourced entry)
Statement  : The system shall reject building an entry for an event reference that has already produced a posted entry.
Data source: ENT-FIN-004.eventReference, ENT-FIN-004.statusCode
Message    : ar: "تم بالفعل ترحيل قيد لهذا المرجع" · en: "An entry for this event reference has already been posted"
Traces     : REQ-FIN-011
Source     : general-accounting-system-plan-en.md §12.12

### RULE-FIN-005 — رفض حدث بلا قاعدة نشطة / Reject an event with no active rule
Scope      : ENT-FIN-009
Trigger    : on create (event-sourced entry)
Statement  : The system shall reject building an entry for an event whose type has no active rule.
Data source: ENT-FIN-009.eventTypeCode, ENT-FIN-009.isActiveFl
Message    : ar: "لا توجد قاعدة نشطة لهذا النوع من الأحداث" · en: "No active rule exists for this event type"
Traces     : REQ-FIN-013
Source     : general-accounting-system-plan-en.md §6.1

### RULE-FIN-006 — ثبات تساوي المدين والدائن / Debit=Credit invariant
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on post (any source)
Statement  : The system shall reject posting an entry whose total debits do not equal its total credits to the smallest currency unit.
Data source: ENT-FIN-005.amount, ENT-FIN-005.directionCode
Message    : ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" · en: "The entry is unbalanced — total debits do not equal total credits"
Traces     : REQ-FIN-018
Source     : general-accounting-system-plan-en.md §12.1

### RULE-FIN-007 — الترحيل للأوراق النشطة فقط / Posting only to leaf, active accounts
Scope      : ENT-FIN-001, ENT-FIN-005
Trigger    : on post (any source)
Statement  : The system shall reject posting a line targeting an account that is not a leaf, not active, or not marked as accepting direct posting.
Data source: ENT-FIN-001.isLeafFl, ENT-FIN-001.isActiveFl, ENT-FIN-005.accountId
Message    : ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" · en: "The target account does not accept direct posting"
Traces     : REQ-FIN-019
Source     : general-accounting-system-plan-en.md §12.3

### RULE-FIN-008 — بوابة الفترة عند الترحيل / Period gate at post time
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on post (any source)
Statement  : The system shall reject posting an entry whose period is not Open at that moment, except the year-end closing and opening entries generated by the year-end close (REQ-FIN-036, API-FIN-027), which are exempt from this gate: that close may only run once every period of the year is Hard Closed, so no Open period exists for its own entries by construction. The exemption is part of this rule and applies to no other entry and to no other rule — RULE-FIN-006, RULE-FIN-007 and RULE-FIN-009 apply to both generated entries in full.
Data source: ENT-FIN-004.periodId, ENT-FIN-008.statusCode
Message    : ar: "الفترة المستهدفة غير مفتوحة" · en: "The target period is not open"
Traces     : REQ-FIN-020
Source     : general-accounting-system-plan-en.md §12.4

### RULE-FIN-009 — صحة قيمة البُعد / Dimension value validity
Scope      : ENT-FIN-006
Trigger    : on post (any source)
Statement  : The system shall reject posting a line whose cited dimension value does not belong to its stated dimension or is inactive.
Data source: ENT-FIN-006.dimensionId, ENT-FIN-006.dimensionValueId, ENT-FIN-003.dimensionId, ENT-FIN-003.isActiveFl
Message    : ar: "قيمة البُعد غير صالحة" · en: "The dimension value is invalid"
Traces     : REQ-FIN-021
Source     : general-accounting-system-plan-en.md §8.1

### RULE-FIN-010 — سطر الباقي يمتص فرق التقريب / The remainder line absorbs the rounding difference
Scope      : ENT-FIN-005, ENT-FIN-010, ENT-FIN-014
Trigger    : on build (compound/percentage distribution — rule engine or allocation)
Statement  : The system shall compute the remainder line's amount per posting side — the total already carried by the opposing side minus the sum of every other line on the remainder line's own side — after every percentage line rounds to the smallest currency unit. The remainder line is never itself computed as a percentage, and its computed amount must be positive (POL-FIN-005): a distribution whose other lines already equal or exceed the opposing side leaves no residue to absorb and is rejected.
Data source: ENT-FIN-005.amount, ENT-FIN-005.isRemainderFl, ENT-FIN-010.distributionTypeCode, ENT-FIN-014.distributionValue
Message    : ar: "سطر الباقي يُحسب كفرق، لا كنسبة" · en: "The remainder line is computed as a difference, never as a percentage"
Traces     : REQ-FIN-012, REQ-FIN-026
Source     : general-accounting-system-plan-en.md §6.3, §12.6

### RULE-FIN-011 — العكس تام ومرتبط / Reversal is exact and linked
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on reverse
Statement  : The system shall build the reversal entry with the same lines as the original, each with the opposite direction and the same amount, and link both entries to each other.
Data source: ENT-FIN-005.amount, ENT-FIN-005.directionCode, ENT-FIN-004.originalEntryId, ENT-FIN-004.reversalEntryId
Message    : ar: "قيد العكس يطابق الأصل بعكس الاتجاه" · en: "The reversal entry mirrors the original with opposite direction"
Traces     : REQ-FIN-028
Source     : general-accounting-system-plan-en.md §12.7, §9

### RULE-FIN-012 — ترحيل العكس بالفترة الحالية عند إغلاق الأصل / Reversal posts to the current period when the original's is closed
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on reverse
Statement  : The system shall post the reversal into the current open period when the original entry's own period is no longer Open.
Data source: ENT-FIN-004.periodId, ENT-FIN-008.statusCode
Message    : ar: "سيُرحَّل قيد العكس في الفترة المفتوحة الحالية" · en: "The reversal will post into the current open period"
Traces     : REQ-FIN-029
Source     : general-accounting-system-plan-en.md §9

### RULE-FIN-013 — رفض عكس قيد غير مُرحَّل / Reject reversing a non-posted entry
Scope      : ENT-FIN-004
Trigger    : on reverse
Statement  : The system shall reject a reverse action on an entry that is not POSTED.
Data source: ENT-FIN-004.statusCode
Message    : ar: "لا يمكن عكس قيد غير مُرحَّل" · en: "A non-posted entry cannot be reversed"
Traces     : REQ-FIN-030
Source     : general-accounting-system-plan-en.md §9

### RULE-FIN-014 — رفض إعادة فتح فترة مغلقة صارمًا / Reject reopening a hard-closed period
Scope      : ENT-FIN-008
Trigger    : on update (period status)
Statement  : The system shall reject any attempt to reopen a Hard Closed period.
Data source: ENT-FIN-008.statusCode
Message    : ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" · en: "The period is hard-closed and cannot be reopened"
Traces     : REQ-FIN-035
Source     : general-accounting-system-plan-en.md §10.2

### RULE-FIN-015 — فصل صلاحية الاعتماد عن صلاحية الإنشاء / Separate the approval permission from the creation permission
Scope      : ENT-FIN-008
Trigger    : on evaluate (period-close-approval action)
Statement  : The system shall require the period-close-approval action to be gated by a permission distinct from the journal-entry-creation permission, enforced through the Security module.
Data source: DEFERRED — the permission matrix is the Security module's declaration surface; FIN declares no permission entity in this version, so the separation is enforced there and has no FIN-side field to read
Message    : ar: "صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود" · en: "The close-approval permission is separate from the entry-creation permission"
Traces     : REQ-FIN-038
Source     : general-accounting-system-plan-en.md §2.2, §8.2, §10.3
Enforcement note (2026-09-12, does not change the Statement above): satisfied in full by the
             `@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on `FiscalPeriodService.hardClose`
             (API-FIN-026) and `FiscalYearService.yearEndClose` (API-FIN-027) — a permission code
             distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`, enforced by SEC, exactly as the
             Statement and AC-FIN-038 describe. A STRICTER check once existed in FIN code and was
             removed by recorded human decision: `FinSeparationOfDutiesService` +
             `FiscalPeriodDomain.assertCanHardClose(...)` refused the close for EVERY caller
             whenever ANY single user in the system held both permissions — global user-set
             disjointness, which this rule does not ask for and which the `Data source` line above
             explicitly rules out by stating there is no FIN-side fact to read. `FIN-403-SOD-VIOLATION`
             is struck as unreachable; do not re-derive the removed behaviour from this rule.

### RULE-FIN-016 — قفل القيد بعد الترحيل / Lock an entry after posting
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on evaluate (any edit/delete attempt)
Statement  : The system shall reject any edit or delete attempt on a POSTED entry or its lines; correction is only through a reversal (REQ-FIN-028).
Data source: ENT-FIN-004.statusCode, ENT-FIN-005.journalEntryId
Message    : ar: "القيد المُرحَّل مقفل؛ التصحيح فقط عبر العكس" · en: "A posted entry is locked; correction is only through a reversal"
Traces     : REQ-FIN-016, REQ-FIN-017
Source     : general-accounting-system-plan-en.md §8.3, §12.13

### RULE-FIN-017 — تماسك السنة والفترة وتاريخ المستند / Fiscal year, period and document date must cohere
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on create (an entry whose fiscalYearId, periodId and docDate are all submitted)
Statement  : The system shall reject an entry whose submitted period does not belong to its submitted fiscal year, or whose document date falls outside that period's start/end dates. Entries the system itself generates derive the three from one another and are coherent by construction.
Data source: ENT-FIN-004.fiscalYearId, ENT-FIN-004.periodId, ENT-FIN-004.docDate, ENT-FIN-008.fiscalYearId, ENT-FIN-008.startDate, ENT-FIN-008.endDate
Message    : ar: "الفترة المحددة لا تتبع السنة المالية المحددة، أو تاريخ المستند خارج نطاقها" · en: "The selected period does not belong to the selected fiscal year, or the document date falls outside it"
Traces     : REQ-FIN-014, REQ-FIN-017
Source     : general-accounting-system-plan-en.md §8.1, §10.1

## A6 — Lookups

All 13 lookup types below are owned by FIN and registered into MDL (module-registry-fin.md
→ LOOKUPS OWNED carries the full source citation per key; only the values are repeated here).

| Key | Values |
|---|---|
| ACCOUNT_TYPE | ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| DEBIT_CREDIT | DEBIT, CREDIT |
| PERIOD_STATE | OPEN, SOFT_CLOSE, HARD_CLOSE, YEAR_END_CLOSE |
| FISCAL_YEAR_STATUS | OPEN, CLOSED |
| JOURNAL_TYPE | EVENT_GENERATED, MANUAL, RECURRING, ALLOCATION, REVERSAL |
| JOURNAL_STATUS | DRAFT, POSTED, VOID (VOID is seeded in MDL by V26 and declared as `JournalEntry.STATUS_VOID`, but is now UNREACHABLE: classic reversal leaves the original POSTED and no code path writes VOID — see §A7) |
| ACCOUNTING_EVENT_TYPE | none seeded — host-specific, added as data [§3, §6.4] |
| PAYMENT_METHOD | none seeded — host-specific |
| ACCOUNT_DERIVATION_TYPE | CONSTANT, DIRECT, MAPPING |
| AMOUNT_SOURCE_TYPE | FIELD, PERCENTAGE, REMAINDER |
| DISTRIBUTION_TYPE | FIXED, PERCENTAGE, REMAINDER |
| RECURRING_SCHEDULE_TYPE | RECURRING, REVERSING |
| RECURRING_FREQUENCY | MONTHLY, QUARTERLY, ANNUALLY, WEEKLY |

Consumed lookups: none — FIN owns every coded value list it uses.

## A7 — Status lifecycle

**ENT-FIN-004 JournalEntry.statusCode (JOURNAL_STATUS, 3 states)**
```
DRAFT  --(REQ-FIN-017, automatic validation passes)--> POSTED   (terminal)
POSTED --(REQ-FIN-028, reverse action)----------------> POSTED  (no transition — classic reversal: the original STAYS POSTED; its reversal is itself a new POSTED entry, and the two are linked through originalEntryId/reversalEntryId)
```
Classic reversal is the convention FIN follows: reversing an entry posts an equal, opposite
mirror entry and leaves the original POSTED and untouched, so the net effect on every account
balance is zero and both entries stay visible in the ledger and its audit trail. VOIDing the
original instead would remove it from the POSTED-only reports while the mirror remained,
netting to −(original). It also means RULE-FIN-016 (a POSTED row is never modified) holds
without exception — the reverse action's only write back to the original is the
reversalEntryId link.

DRAFT is transient (build → validate happens in one orchestration, RULE-FIN-016 locks
POSTED immediately); a DRAFT that fails validation is never saved (REQ-FIN-015/018-021
reject before any row is written) — not a stored intermediate state a user can browse.

**ENT-FIN-008 FiscalPeriod.statusCode (PERIOD_STATE, 4 states)**
```
OPEN        --(REQ-FIN-033, soft-close)--------> SOFT_CLOSE
SOFT_CLOSE  --(REQ-FIN-032, reopen)------------> OPEN
SOFT_CLOSE  --(REQ-FIN-034, hard-close)--------> HARD_CLOSE
HARD_CLOSE  --(REQ-FIN-036, year-end close, all periods of the year)--> YEAR_END_CLOSE
```
HARD_CLOSE and YEAR_END_CLOSE are terminal (RULE-FIN-014 — never reopened).

**ENT-FIN-007 FiscalYear.statusCode (FISCAL_YEAR_STATUS, 2 states)** — binary
(OPEN/CLOSED, set by REQ-FIN-036) — not applicable for a diagram.

All other statuses in this module (isActiveFl flags) are binary — not applicable.

## A8 — Module dependencies

| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate (assigned by P2) |
|---|---|---|---|---|
| User (identity, principal string on audit columns) | ENT-SEC-001 | SEC | HARD-FK (per SEC's own precedent: principal string, not numeric FK — see AUTO-DECISIONS) | assigned by P2 |
| ModuleRegistry, ScreenRegistry, ActionRegistry | ENT-SEC-004, ENT-SEC-005, ENT-SEC-006 | SEC | HARD-FK (registration as data) | assigned by P2 |
| LookupType, LookupValue | ENT-MDL-001, ENT-MDL-002 | MDL | HARD-FK (registration + runtime read) | assigned by P2 |

| External service | Purpose | Integration kind |
|---|---|---|
| Notifications (ready, external) | period-close-awaiting notice | SOFT / optional, per general-accounting-system-plan-en.md §2.3 |
| File Service (ready, external) | statement export | SOFT / optional, per general-accounting-system-plan-en.md §2.3 |

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-FIN-001 — شجرة الحسابات / Chart of accounts
### B1 — Definition
Purpose      : إدارة شجرة الحسابات الهرمية.
Entities     : ENT-FIN-001
Operations   : search, create, update, deactivate. No by-id read — deliberate v1 exclusion, see
               the note under B5
Users        : مسؤول مالي
Navigation   : FIN → Setup → Chart of accounts
Content shape: true hierarchy (parent/child)
Traces       : REQ-FIN-001, REQ-FIN-002, REQ-FIN-003
Composite    : Search + Entry = ONE screen requirement
### B2 — Search / list
Filters: code(LIKE), nameAr/nameEn(LIKE), accountTypeCode(EXACT), isActiveFl(EXACT) — correspond to result columns.
### B3 — Input
Fields: code, nameAr, nameEn, accountTypeCode, natureCode, parentAccountId, isLeafFl (ENT-FIN-001; RULE-FIN-001 blocks isLeafFl=true on a parent). Button: Deactivate.
### B4 — Access
Page code: FIN_ACCOUNTS. Actions: VIEW, CREATE, UPDATE (covers deactivate — there is no DELETE
endpoint and no `PERM_FIN_ACCOUNTS_DELETE`; deactivate is `PUT /{id}/deactivate` gated by
`PERM_FIN_ACCOUNTS_UPDATE`).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search accounts | POST | /api/v1/fin/accounts/search | filters, paging (request body) | Page\<Account\> | — | REQ-FIN-001 |
| create account | POST | /api/v1/fin/accounts | account fields | Account | RULE-FIN-001 | REQ-FIN-001, REQ-FIN-002 |
| update account | PUT | /api/v1/fin/accounts/{id} | account fields | Account | RULE-FIN-001 | REQ-FIN-002 |
| deactivate account | PUT | /api/v1/fin/accounts/{id}/deactivate | id | Account | — | REQ-FIN-003 |

**No by-id read, and why.** `AccountController` publishes exactly these four endpoints — create,
update, deactivate and search (`AccountController.java:45, 52, 60, 66`) — and no `GET /{id}`. The
`read` this section's B1 Operations line used to name was never in B5 either, so the B1 line was
its only claim; it is narrowed here rather than deleted so the decision stays legible. A by-id read
is a deliberate v1 exclusion, not a pending endpoint: no REQ or AC asks for one (REQ-FIN-001/002/003
and AC-FIN-001…003 cover create, the leaf-flag rejection and deactivate), this is a Composite
"Search + Entry = ONE screen" requirement whose Entry form is populated from the search-result row,
and API-FIN-001 already returns the complete `Account` record, not a trimmed projection. Contrast
SCR-REQ-FIN-006, where a by-id read WAS built (API-FIN-022) because REQ-FIN-016/REQ-FIN-027 need
the entry's lines, which its search result does not carry.

## SCR-REQ-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values
### B1 — Definition
Purpose      : إدارة الأبعاد وقيمها.
Entities     : ENT-FIN-002, ENT-FIN-003
Operations   : search, create (dimension — no deactivate, deliberate; see B4); search, create,
               deactivate (value — API-FIN-035)
Users        : مسؤول مالي
Navigation   : FIN → Setup → Dimensions
Content shape: header + repeating lines (master dimensions + detail values)
Traces       : REQ-FIN-004, REQ-FIN-005, REQ-FIN-006
Composite    : Master (dimensions) + Detail (values) = ONE screen requirement
### B2 — Search / list
Dimension filters: code(LIKE). Value filters: code(LIKE) — correspond to result columns.
### B3 — Input
Dimension fields: code, nameAr, nameEn. Value fields: code, nameAr, nameEn, sortOrder (ENT-FIN-002/003).
### B4 — Access
Page code: FIN_DIMENSIONS. Actions: VIEW, CREATE, UPDATE.

**UPDATE — the dimension-VALUE deactivate, and only that.** UPDATE covers exactly one endpoint:
API-FIN-035, `PUT /api/v1/fin/dimensions/values/{id}/deactivate`, published on
`DimensionController` (child endpoints live on the parent's controller) and delegating to
`DimensionValueService.deactivate`, gated by `PERM_FIN_DIMENSIONS_UPDATE`. That permission is
declared in `PermissionConstants` and is both registered and granted to `SYS_ADMIN` by migration
`V28__fin_dimensions_update_action.sql` — V24 had seeded VIEW and CREATE only, and V25's grant
statement (a `SELECT` over the registry) had already run, so V28 carries its own explicit grant
rather than relying on it. Deactivate is modelled as UPDATE and not DELETE, exactly as
FIN_ACCOUNTS models API-FIN-004. An unknown dimension-value id answers `FIN-404-DIMVALUE`, a new
code registered in `FinErrorCodes` and in both i18n bundles.

**The PARENT dimension deliberately has no deactivate.** No REQ, AC or RULE asks for one and
`Dimension.isActiveFl` (DBF-FIN-018) drives no behaviour, so that column stays unflippable through
the API by decision, not by oversight. The value-level flag (DBF-FIN-029) is the one RULE-FIN-009 /
REQ-FIN-021 read when rejecting a journal line that cites an INACTIVE dimension value —
`DimensionValueDomain.checkUsableOnLine` returns `FIN-409-INVALID-DIMENSION` off exactly this flag
— so before API-FIN-035 that branch was unreachable and untestable, and closing that gap is the
whole reason this half, and only this half, was built. No `activate` counterpart was added either,
matching the delivered `AccountService.deactivate` precedent.

**Previously recorded here, now superseded**: this section stated that FIN publishes no dimension
or dimension-value update/deactivate endpoint at all and that V24 seeds no
`PERM_FIN_DIMENSIONS_UPDATE`. That was an accurate description of the as-built state before
API-FIN-035 and V28; it is no longer true for the value half, and remains true for the parent half.

No DELETE: FIN publishes no `DELETE` endpoint on any screen, and neither V24 nor V28 seeds a
`PERM_FIN_DIMENSIONS_DELETE` row.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search dimensions | POST | /api/v1/fin/dimensions/search | filters, paging (request body) | Page\<Dimension\> | — | REQ-FIN-004 |
| create dimension | POST | /api/v1/fin/dimensions | code, nameAr, nameEn | Dimension | — | REQ-FIN-004 |
| create dimension value | POST | /api/v1/fin/dimensions/{id}/values | code, nameAr, nameEn, sortOrder | DimensionValue | RULE-FIN-002 | REQ-FIN-005, REQ-FIN-006 |
| search dimension values | POST | /api/v1/fin/dimensions/values/search | filters (incl. dimensionId), paging (request body) | Page\<DimensionValue\> | — | REQ-FIN-005 |
| deactivate dimension value | PUT | /api/v1/fin/dimensions/values/{id}/deactivate | id | DimensionValue (isActiveFl=false) | — | REQ-FIN-005 |

API-FIN-035 (the last row) is the endpoint that makes REQ-FIN-021 / RULE-FIN-009 reachable at all:
it is the only way to set `DimensionValue.isActiveFl` to false. There is no parent-dimension
counterpart and no `activate` — see B4.

## SCR-REQ-FIN-003 — قواعد المحرك / Engine rules
### B1 — Definition
Purpose      : إدارة قواعد ربط أنواع الأحداث بسطور القيد.
Entities     : ENT-FIN-009, ENT-FIN-010
Operations   : search, create, deactivate (rule — API-FIN-034); create (line). As built there is
               no update and no by-id read on either, and no line delete — see B4
Users        : مسؤول مالي
Navigation   : FIN → Setup → Engine rules
Content shape: header + repeating lines (rule header + its lines)
Traces       : REQ-FIN-007, REQ-FIN-008, REQ-FIN-009
Composite    : Master (rules) + Detail (lines) = ONE screen requirement
### B2 — Search / list
Filters: eventTypeCode(EXACT), isActiveFl(EXACT) — correspond to result columns.
### B3 — Input
Rule fields: eventTypeCode, nameAr, nameEn (ENT-FIN-009). Line fields: accountDerivationTypeCode,
accountDerivationValue, amountSourceTypeCode, amountSourceValue, directionCode, distributionTypeCode,
isRemainderFl (ENT-FIN-010; RULE-FIN-003 blocks saving until exactly one remainder line exists
when a percentage line is present).
### B4 — Access
Page code: FIN_RULES. Actions: VIEW, CREATE, UPDATE.

**UPDATE covers two endpoints**, both gated by the single `PERM_FIN_RULES_UPDATE` that V24 already
seeds — no new permission constant and no migration were needed: API-FIN-011 (add a rule line) and
API-FIN-034, `PUT /api/v1/fin/event-rules/{id}/deactivate` (note the base path is
`/api/v1/fin/event-rules`, not `event-type-rules`). An unknown rule id answers the pre-existing
`FIN-404-RULE`. API-FIN-034 exists because until it landed no rule could ever be retired, which
left `FIN-404-NO-ACTIVE-RULE` (RULE-FIN-005, raised by API-FIN-020) unreachable. **Stated
limitation**, recorded in `EventTypeRuleService`'s own javadoc: deactivating a rule does NOT free
its event type for a replacement rule, because `EventTypeRuleService.create` guards uniqueness with
`existsByEventTypeCode`, which is not scoped to the active flag. No `activate` counterpart was
added, matching the delivered `AccountService.deactivate` precedent.

**Not built, and why.** `EventTypeRuleService` publishes exactly `create`, `deactivate` and
`search`; `RuleLineService` publishes `create` alone. So the rule has no update and no by-id read
endpoint, and the line has none of update, by-id read or delete. The rule-line *delete* named under
B1 Operations is a deliberate v1 exclusion rather than an oversight: ENT-FIN-010 carries no active
flag to soft-delete against, and FIN publishes no `DELETE` endpoint on any screen — V24 seeds no
`PERM_FIN_RULES_DELETE` row for this or any other FIN screen.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search rules | POST | /api/v1/fin/event-rules/search | filters, paging (request body) | Page\<EventTypeRule\> | — | REQ-FIN-007 |
| create rule | POST | /api/v1/fin/event-rules | eventTypeCode, nameAr, nameEn | EventTypeRule | — | REQ-FIN-007 |
| add rule line | POST | /api/v1/fin/event-rules/{id}/lines | line fields | RuleLine | RULE-FIN-003 | REQ-FIN-008, REQ-FIN-009 |
| deactivate rule | PUT | /api/v1/fin/event-rules/{id}/deactivate | id | EventTypeRule (isActiveFl=false) | — | REQ-FIN-007 |

## SCR-REQ-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates
### B1 — Definition
Purpose      : إدارة القوالب المتكررة والعكسية.
Entities     : ENT-FIN-011, ENT-FIN-012
Operations   : search, create (template with its lines in one request), run, deactivate —
               API-FIN-012/013/014/036, which is everything `RecurringTemplateController`
               publishes. **`deactivate` (template) is DELIVERED as API-FIN-036 and, since
               2026-09-12, it DOES stop the template from running — that defect is CLOSED, see
               B4.** **`update` (template) is still NOT built and is now the ONLY open half of
               the original gap — also B4.** No by-id read and no line-level read/update/delete:
               deliberate v1 exclusions, also B4
Users        : محاسب
Navigation   : FIN → Setup → Recurring/reversing templates
Content shape: header + repeating lines
Traces       : REQ-FIN-022, REQ-FIN-023, REQ-FIN-024
Composite    : Master (templates) + Detail (lines) = ONE screen requirement
### B2 — Search / list
Filters: nameAr/nameEn(LIKE), scheduleTypeCode(EXACT), isActiveFl(EXACT).
### B3 — Input
Template fields: nameAr, nameEn, scheduleTypeCode, frequencyCode, startDate, endDate (ENT-FIN-011).
Line fields: accountId, amount, directionCode, dimensionValueId (ENT-FIN-012).
### B4 — Access
Page code: FIN_RECURRING_TEMPLATES. Actions: VIEW, CREATE, UPDATE (covers BOTH "run" —
API-FIN-014 — and "deactivate" — API-FIN-036; one permission, `PERM_FIN_RECURRING_TEMPLATES_UPDATE`,
already seeded by V24 and already granted by V25's blanket Tier-3 grant, so API-FIN-036 needed no
new constant, no new error code and no migration). No DELETE endpoint and no
`PERM_FIN_RECURRING_TEMPLATES_DELETE`.

**As built.** `RecurringTemplateController` publishes exactly four endpoints, each at its mapping
annotation: `POST` create (API-FIN-013, `RecurringTemplateController.java:51`), `POST /{id}/run`
(API-FIN-014, `:62`), `PUT /{id}/deactivate` (API-FIN-036, `:68`) and `POST /search` (API-FIN-012,
`:76`). The B1 Operations line originally promised `read, update, deactivate` on the template and
`create, read, update, delete` on the line; `deactivate` has since been built, but `read` and
`update` on the template and everything but `create` on the line have not.

**Deliberate v1 exclusions.** *By-id read*: API-FIN-012's search already returns the FULL aggregate
— `RecurringTemplateService.search` batch-loads each page's lines and maps them into
`RecurringTemplateResponse.lines` (`RecurringTemplateService.java:405-411`) — so a `GET /{id}`
would return nothing the search does not, and no REQ or AC asks for one. *Line delete*: FIN
publishes no `DELETE` endpoint on any screen and V24 seeds no `PERM_FIN_*_DELETE` row, the same
already-taken decision recorded at SCR-REQ-FIN-003 §B4. *No `activate` counterpart to API-FIN-036*:
FIN ships none for any entity, following the delivered `AccountService.deactivate` precedent.

**`deactivate` (template) — DELIVERED as API-FIN-036.** The half of the defect this section used
to report — that no endpoint could ever set `IS_ACTIVE_FL` to FALSE — is closed.
`RecurringTemplateService.deactivate` loads the template, calls the entity's own `deactivate()`
helper (`RecurringTemplate.java:99`, which until now had zero callers), persists, then re-reads the
template's lines and hands them to the mapper before returning — the re-read is required because
`RecurringTemplateResponse.lineCount` is derived from the list the mapper is given, so an empty
list would misreport the aggregate as having no lines. Unknown id answers the pre-existing
`FIN-404-TEMPLATE`. It is gated on the pre-existing `PERM_FIN_RECURRING_TEMPLATES_UPDATE`, the same
permission API-FIN-014's run uses. No migration, no new constant, no new error code.

**DEFECT CLOSED 2026-09-12 — deactivate now stops the run.** This paragraph used to report an OPEN
DEFECT: `RecurringTemplateService.run` (API-FIN-014) did not read `isActiveFl`, so a deactivated
template still ran and still posted, and setting the flag changed no behaviour whatever. It is now
closed. `RecurringTemplateDomain.assertCanRun()` — a NEW Domain companion for ENT-FIN-011, created
for this — is called by `RecurringTemplateService.run` immediately after the template is loaded and
before the run date, period or lines are resolved, and refuses a deactivated template with a new
`FIN-409-NOT-ACTIVE` (HTTP 409; ar "هذا التعريف غير نشط ولا يمكن تشغيله", en "This definition is
deactivated and cannot be run"). `FIN-404-TEMPLATE` was deliberately NOT reused, because the
template does exist. AC-FIN-023, written "Given an **active** recurring template", is now fully
satisfied: the inactive state is reachable AND behaves differently. The flag's other observable
effect is unchanged — B2's advertised `isActiveFl(EXACT)` filter discriminates
(`RecurringTemplateService`'s sort/filter whitelist honours it).

**READ THIS BEFORE CITING THE GATE AS A REQUIREMENT.** No RULE-FIN-* states it. It was closed on a
**recorded human decision**, because closing it required inventing an "exists but is inactive"
error code, its HTTP status, its ar+en messages and its Error Catalog row — none of which any REQ,
AC or RULE asks for. A later session must not cite `FIN-409-NOT-ACTIVE` as pre-existing spec, and
must not infer from it that other unstated gates may be added the same way without a fresh
decision.

**OPEN DEFECT — `update` (template) is still missing.** This is now the ONLY open half of the
original gap: with deactivate but no update, a template created with a wrong account or amount
cannot be corrected — it can only be retired. Since 2026-09-12 retiring it does at least stop it
(above), so the wrong entries stop arriving; entries already posted before the retirement remain
recoverable only by reversing them one by one. It was not built because a correct update must decide the fate of the template's existing child
lines (replace wholesale? merge? reject if any line changed?), which is a design question no REQ,
AC or RULE answers. It is recorded here as a known gap, not as a reasoned exclusion.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search templates | POST | /api/v1/fin/recurring-templates/search | filters, paging (request body) | Page\<RecurringTemplate\> | — | REQ-FIN-022 |
| create template | POST | /api/v1/fin/recurring-templates | template + lines | RecurringTemplate | RULE-FIN-006 (reused, balance check applied at run time not save time) | REQ-FIN-022 |
| run template (system/scheduled) | POST | /api/v1/fin/recurring-templates/{id}/run | — | JournalEntry | RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009, RULE-FIN-011 | REQ-FIN-023, REQ-FIN-024 |
| deactivate template (API-FIN-036) | PUT | /api/v1/fin/recurring-templates/{id}/deactivate | path `id`, no body | RecurringTemplate (isActiveFl=false, lines included) | — (none beyond existence; since 2026-09-12 it DOES gate the run — a subsequent API-FIN-014 answers `FIN-409-NOT-ACTIVE`, by decision not by RULE — see B4) | REQ-FIN-022 |

## SCR-REQ-FIN-005 — قواعد التوزيع / Allocation rules
### B1 — Definition
Purpose      : إدارة قواعد توزيع رصيد حساب مصدر على أهدافه.
Entities     : ENT-FIN-013, ENT-FIN-014
Operations   : search, create (rule with its targets in one request), run, deactivate —
               API-FIN-015/016/017/037, which is everything `AllocationRuleController` publishes.
               **`deactivate` (rule) is DELIVERED as API-FIN-037 and, since 2026-09-12, it DOES
               stop the rule from running — that defect is CLOSED, see B4.** **`update` (rule) is
               still NOT built and is now the ONLY open half of the original gap — also B4.** No
               by-id read and no target-level read/update/delete: deliberate v1 exclusions, also B4
Users        : محاسب
Navigation   : FIN → Setup → Allocation rules
Content shape: header + repeating lines
Traces       : REQ-FIN-025, REQ-FIN-026
Composite    : Master (rules) + Detail (targets) = ONE screen requirement
### B2 — Search / list
Filters: nameAr/nameEn(LIKE), sourceAccountId(EXACT), isActiveFl(EXACT).
### B3 — Input
Rule fields: nameAr, nameEn, sourceAccountId (ENT-FIN-013). Target fields: targetAccountId,
dimensionValueId, distributionTypeCode, distributionValue, isRemainderFl (ENT-FIN-014;
RULE-FIN-003 applies).
### B4 — Access
Page code: FIN_ALLOCATION_RULES. Actions: VIEW, CREATE, UPDATE (covers BOTH "run" — API-FIN-017 —
and "deactivate" — API-FIN-037; one permission, `PERM_FIN_ALLOCATION_RULES_UPDATE`, already seeded
by V24 and already granted by V25's blanket Tier-3 grant, so API-FIN-037 needed no new constant, no
new error code and no migration). No DELETE endpoint and no `PERM_FIN_ALLOCATION_RULES_DELETE`.

**As built.** `AllocationRuleController` publishes exactly four endpoints, each at its mapping
annotation: `POST` create (API-FIN-016, `AllocationRuleController.java:52`), `POST /{id}/run`
(API-FIN-017, `:63`), `PUT /{id}/deactivate` (API-FIN-037, `:69`) and `POST /search` (API-FIN-015,
`:76`). The B1 Operations line originally promised `read, update, deactivate` on the rule and
`create, read, update, delete` on the target; `deactivate` has since been built, but `read` and
`update` on the rule and everything but `create` on the target have not.

**Deliberate v1 exclusions.** *By-id read*: API-FIN-015's search returns the FULL aggregate,
targets included (`AllocationRuleResponse.targets`), so a `GET /{id}` would add nothing and no REQ
or AC asks for one — the same reasoning as SCR-REQ-FIN-004 §B4. *Target delete*: FIN publishes no
`DELETE` endpoint on any screen and V24 seeds no `PERM_FIN_*_DELETE` row. *No `activate`
counterpart to API-FIN-037*: FIN ships none for any entity, following the delivered
`AccountService.deactivate` precedent.

**`deactivate` (rule) — DELIVERED as API-FIN-037.** The half of the defect this section used to
report — that no endpoint could ever set `IS_ACTIVE_FL` to FALSE — is closed.
`AllocationRuleService.deactivate` loads the rule, calls the entity's own `deactivate()` helper
(`AllocationRule.java:91`, which until now had zero callers), persists, then re-reads the rule's
targets and hands them to the mapper before returning — the re-read is required because
`AllocationRuleResponse.targetCount` is derived from the list the mapper is given, so an empty list
would misreport the aggregate as having no targets. Unknown id answers the pre-existing
`FIN-404-ALLOCATION-RULE`. It is gated on the pre-existing `PERM_FIN_ALLOCATION_RULES_UPDATE`, the
same permission API-FIN-017's run uses. No migration, no new constant, no new error code. Nothing
is delegated to `AllocationRuleDomain` before the mutation: RULE-FIN-003, the one rule that Domain
owns, governs the remainder-target SET at create and run time and says nothing about the active
flag.

**DEFECT CLOSED 2026-09-12 — deactivate now stops the run.** This paragraph used to report an OPEN
DEFECT: `AllocationRuleService.run` (API-FIN-017) did not read `isActiveFl`, so a deactivated
allocation rule still ran and still posted, and the Domain accessor built for the flag was dead
code. It is now closed. `AllocationRuleDomain.assertCanRun()` is called by
`AllocationRuleService.run` immediately after the rule is loaded and before its targets are even
fetched, and refuses a deactivated rule with a new `FIN-409-NOT-ACTIVE` (HTTP 409; ar "هذا التعريف
غير نشط ولا يمكن تشغيله", en "This definition is deactivated and cannot be run").
`FIN-404-ALLOCATION-RULE` was deliberately NOT reused, because the rule does exist. B2's advertised
`isActiveFl(EXACT)` filter still discriminates as before.

**READ THIS BEFORE CITING THE GATE AS A REQUIREMENT.** No RULE-FIN-* states it — RULE-FIN-003, the
one rule `AllocationRuleDomain` owns, governs the remainder-target set and says nothing about the
active flag. The gate was added on a **recorded human decision**, since closing the gap required
inventing an error code, status and messages no REQ, AC or RULE asks for. Do not cite
`FIN-409-NOT-ACTIVE` as pre-existing spec. It closed on the same decision as SCR-REQ-FIN-004's.

**OPEN DEFECT — `update` (rule) is still missing.** This is now the ONLY open half of the original
gap: with deactivate but no update, a rule created with the wrong source account or target split
cannot be corrected — it can only be retired. Since 2026-09-12 retiring it does at least stop it
(above), so the wrong distributions stop arriving. It was not built because a correct update must decide the fate
of the rule's existing targets, and therefore of RULE-FIN-003's remainder-target set (replace
wholesale? merge? re-validate the remainder marker across the new set?), which is a design question
no REQ, AC or RULE answers. It is recorded here as a known gap, not as a reasoned exclusion.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search allocation rules | POST | /api/v1/fin/allocation-rules/search | filters, paging (request body) | Page\<AllocationRule\> | — | REQ-FIN-025 |
| create allocation rule | POST | /api/v1/fin/allocation-rules | rule + targets | AllocationRule | RULE-FIN-003 | REQ-FIN-025 |
| run allocation rule | POST | /api/v1/fin/allocation-rules/{id}/run | — | JournalEntry | RULE-FIN-006..011 | REQ-FIN-026 |
| deactivate allocation rule (API-FIN-037) | PUT | /api/v1/fin/allocation-rules/{id}/deactivate | path `id`, no body | AllocationRule (isActiveFl=false, targets included) | — (none beyond existence; since 2026-09-12 it DOES gate the run — a subsequent API-FIN-017 answers `FIN-409-NOT-ACTIVE`, by decision not by RULE — see B4) | REQ-FIN-025 |

## SCR-REQ-FIN-006 — قيود اليومية / Journal entries (view + manual entry + reverse)
### B1 — Definition
Purpose      : عرض قيود اليومية بكل مصادرها، إدخال يدوي، وعكس قيد مُرحَّل.
Entities     : ENT-FIN-004, ENT-FIN-005, ENT-FIN-006
Operations   : search, create (manual), read, reverse
Users        : محاسب
Navigation   : FIN → Operations → Journal entries
Content shape: header + repeating lines with totals (debit/credit totals shown live while entering)
Traces       : REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030
Composite    : Search + Entry (with a "Reverse" action on a posted entry) = ONE screen requirement
### B2 — Search / list
Filters: docNo(LIKE), docDate(DATE_RANGE), periodId(EXACT), statusCode(EXACT), journalTypeCode(EXACT) — correspond to result columns.
### B3 — Input
Header fields: docDate, periodId, descriptionAr, descriptionEn (ENT-FIN-004; docNo/statusCode/
journalTypeCode system-set). Line fields (repeating): accountId, amount, directionCode,
dimension value(s) per JournalLineDimension, descriptionAr, descriptionEn (ENT-FIN-005/006).
Buttons: "Post" → REQ-FIN-017 (validates REQ-FIN-018..021 first, REQ-FIN-015 shows failures);
"Reverse" (on a POSTED row) → REQ-FIN-028/029/030.
### B4 — Access
Page code: FIN_JOURNAL_ENTRIES. Actions: VIEW, CREATE (incl. Post), UPDATE (Reverse, modeled
as an update-class action per §7.1 custom-action convention — `PERM_FIN_JOURNAL_ENTRIES_REVERSE`).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search entries | POST | /api/v1/fin/journal-entries/search | filters, paging (request body) | Page\<JournalEntry\> | — | REQ-FIN-027 |
| create manual entry | POST | /api/v1/fin/journal-entries | header + lines | JournalEntry (DRAFT then POSTED) | RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009, RULE-FIN-017 | REQ-FIN-014, REQ-FIN-015, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021 |
| build event entry (system) | POST | /api/v1/fin/journal-entries/from-event | canonical event payload | JournalEntry | RULE-FIN-004, RULE-FIN-005, RULE-FIN-006..009, RULE-FIN-010 | REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-017..021 |
| reverse entry | POST | /api/v1/fin/journal-entries/{id}/reverse | id | JournalEntry (the new reversal) | RULE-FIN-011, RULE-FIN-012, RULE-FIN-013 | REQ-FIN-028, REQ-FIN-029, REQ-FIN-030 |
| read entry | GET | /api/v1/fin/journal-entries/{id} | id | JournalEntry with lines | — | REQ-FIN-016, REQ-FIN-027 |

## SCR-REQ-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years + close approval + year-end close
### B1 — Definition
Purpose      : إدارة السنوات والفترات المالية، اعتماد الإغلاق، وتشغيل إقفال نهاية السنة.
Entities     : ENT-FIN-007, ENT-FIN-008
Operations   : create (year); search — PERIODS only (API-FIN-033); open, soft-close, hard-close
               (period); run year-end close. There is NO fiscal-YEAR search and no by-id read of
               either a year or a period — see the note under B5
Users        : مسؤول مالي (إدارة) / مراقب مالي (اعتماد الإغلاق — دور منفصل، POL-FIN-016)
Navigation   : FIN → Control → Fiscal periods & years
Content shape: header + repeating lines (year + its periods)
Traces       : REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038
Composite    : Master (years) + Detail (periods) = ONE screen requirement
### B2 — Search / list
Filters: fiscalYearId(EXACT), statusCode(EXACT) — both OPTIONAL. As delivered by API-FIN-033 these
are exactly the two filters implemented (`FiscalPeriodSearchRequest`), plus paging and sort.
`fiscalYearId` travels inside the body's `filters` list and narrows to one year's periods when
supplied; omitting it is a legitimate "all periods" request, deliberately unlike the dimension-value
child search (API-FIN-008), which rejects a missing parent id. The divergence is the point of the
endpoint: a client that did not create the fiscal year in the same session must still be able to
discover a period id.
### B3 — Input
Year fields: code, startDate, endDate, periodCount (ENT-FIN-007). Period actions per row:
Open, Soft-close, Hard-close (approval-gated). Year action: "Run year-end close" (enabled
only once every period is Hard Closed).
### B4 — Access
Page code: FIN_PERIODS. Actions: VIEW (`PERM_FIN_PERIODS_VIEW` — the screen's gateway, and since
API-FIN-033 also the permission behind a real read endpoint), CREATE (year), UPDATE
(open/soft-close, and a distinct custom action `PERM_FIN_PERIODS_CLOSE_APPROVE` for
hard-close/year-end-close — RULE-FIN-015).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search fiscal periods | POST | /api/v1/fin/fiscal-periods/search | filters (fiscalYearId?, statusCode?), paging (request body) | Page\<FiscalPeriod\> | — | REQ-FIN-031 |
| create fiscal year | POST | /api/v1/fin/fiscal-years | code, startDate, endDate, periodCount | FiscalYear + FiscalPeriod[] | — | REQ-FIN-031 |
| open period | PATCH | /api/v1/fin/fiscal-periods/{id}/open | id | FiscalPeriod | — | REQ-FIN-032 |
| soft-close period | PATCH | /api/v1/fin/fiscal-periods/{id}/soft-close | id | FiscalPeriod | — | REQ-FIN-033 |
| hard-close period (approval) | PATCH | /api/v1/fin/fiscal-periods/{id}/hard-close | id | FiscalPeriod | RULE-FIN-014, RULE-FIN-015 | REQ-FIN-034, REQ-FIN-035, REQ-FIN-037, REQ-FIN-038 |
| run year-end close | POST | /api/v1/fin/fiscal-years/{id}/year-end-close | id | closing + opening JournalEntry | RULE-FIN-006, RULE-FIN-007, RULE-FIN-009, RULE-FIN-015 (RULE-FIN-008 does NOT apply — the year-end CLOSING/OPENING entries are exempt from the period gate by RULE-FIN-008's own carve-out; they are precisely the entries a hard-closed period must still accept) | REQ-FIN-036 |

**A fiscal-period search API now exists: API-FIN-033**, `POST /api/v1/fin/fiscal-periods/search`
(`FiscalPeriodController.search` → `FiscalPeriodService.search`), serving the B2 filters directly
and gated by `PERM_FIN_PERIODS_VIEW` — which was already a registered V24 action row and already
granted by V25/V27, so no migration was needed; the endpoint only added the matching
`PermissionConstants` constant. Until it landed, the B2 filters were served solely by API-FIN-023's
response (the year with its generated periods), which is what this paragraph previously recorded,
and `PERM_FIN_PERIODS_VIEW` was a gateway row with no endpoint behind it. That is no longer the
case.

Why it was built: `JournalEntryCreateRequest` requires both `fiscalYearId` and `periodId`
(API-FIN-019, RULE-FIN-017), and API-FIN-029/030/031 require a period or year id of their own, yet
no API returned a fiscal period except the API-FIN-023 create response. A client that had not
created the year in the same session therefore could not post an entry or run a report at all.

**What API-FIN-033 is NOT, and what B1 no longer claims.** The B1 Operations line used to read
`create (year), search, read`. Measured against the controllers: `FiscalYearController` publishes
exactly two endpoints, `POST` create (API-FIN-023, `FiscalYearController.java:39`) and
`POST /{id}/year-end-close` (API-FIN-027, `:47`); `FiscalPeriodController` publishes the three
PATCH transitions plus `POST /search` (`FiscalPeriodController.java:49, 55, 61, 68`). So the
`search` B1 named is API-FIN-033 over fiscal PERIODS — **there is no fiscal-year search**, and
API-FIN-033 must not be read as one — and the `read` B1 named exists for neither resource: no
`GET /{id}` is published on a year or on a period.

*By-id read* is a deliberate v1 exclusion: API-FIN-023 returns the year together with its generated
periods, and API-FIN-033 returns the full `FiscalPeriodResponse` row, so neither a year nor a
period has a field a by-id read would newly expose. *Fiscal-year search* is recorded as a KNOWN GAP
rather than a reasoned exclusion — no REQ or AC asks for one (REQ-FIN-031 asks only that creating a
year generate its periods), and it is not blocking, because `FiscalPeriodResponse` carries
`fiscalYearId` (`FiscalPeriodResponse.java:31`), so an unfiltered API-FIN-033 call discovers year
ids indirectly. It is a gap and not a defect for that reason alone: the discovery path is awkward
(read a year id off any period row) but it exists, and nothing in the ledger can be corrupted by
its absence.

## SCR-REQ-FIN-008 — دفتر الحساب / Account ledger
### B1 — Definition
Purpose      : عرض دفتر حساب مُشتق حيًا مع تتبع نازل.
Entities     : ENT-FIN-005
Operations   : read
Users        : محاسب / مراقب مالي
Navigation   : FIN → Reports → Account ledger; to: SCR-REQ-FIN-006 (drill-down to entry)
Content shape: flat record (running balance list)
Traces       : REQ-FIN-039, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: accountId(EXACT), periodId or date range(DATE_RANGE), dimension value(s)(EXACT).
### B3 — Input
Not applicable — read-only report.
### B4 — Access
Page code: FIN_ACCOUNT_LEDGER. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| account ledger | GET | /api/v1/fin/reports/account-ledger | accountId, date range, dimension filters | running-balance list, each row linking to its JournalEntry | — | REQ-FIN-039, REQ-FIN-046 |

## SCR-REQ-FIN-009 — ميزان المراجعة / Trial balance
### B1 — Definition
Purpose      : عرض ميزان مراجعة مُشتق حيًا ومتوازن دائمًا.
Entities     : ENT-FIN-005
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Trial balance; to: SCR-REQ-FIN-008 (drill-down per account)
Content shape: flat record (one row per account)
Traces       : REQ-FIN-040, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: periodId(EXACT), accountTypeCode(EXACT) — both OPTIONAL query parameters as built.
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_TRIAL_BALANCE. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| trial balance | GET | /api/v1/fin/reports/trial-balance | periodId?, accountTypeCode? | one row per account (debit/credit balance) | — | REQ-FIN-040, REQ-FIN-046 |

**404 on an unknown keying id, as built.** `periodId` stays an OPTIONAL narrowing: omitting it
means "no period narrowing" and remains a 200 (AC-FIN-040's happy path). When it IS supplied it
must resolve — an unknown id now answers the pre-existing `FIN-404-PERIOD` rather than a silent 200
carrying an all-zero report. This aligns the screen with FIN's existing house style, where a
keying entity id 404s (API-FIN-028 → `FIN-404-ACCOUNT`, API-FIN-032 → `FIN-404-DIMENSION`).

## SCR-REQ-FIN-010 — الميزانية العمومية / Balance sheet
### B1 — Definition
Purpose      : عرض ميزانية عمومية مُشتقة حيًا مع استمرارية الأرصدة الافتتاحية.
Entities     : ENT-FIN-005
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Balance sheet; to: SCR-REQ-FIN-009 (drill-down)
Content shape: header + repeating lines with totals (assets / liabilities / equity sections)
Traces       : REQ-FIN-041, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: fiscalYearId(EXACT, REQUIRED), asOfDate (optional cut-off).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_BALANCE_SHEET. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| balance sheet | GET | /api/v1/fin/reports/balance-sheet | fiscalYearId (required), asOfDate? | grouped balance-sheet accounts with balances | — | REQ-FIN-041, REQ-FIN-046 |

**404 on an unknown fiscal year, as built.** `fiscalYearId` is the REQUIRED keying identifier and
is resolved first: an unknown id answers the pre-existing `FIN-404-YEAR`. Previously it returned a
200 carrying an all-zero statement that a caller could not tell apart from a genuinely dormant
year.

## SCR-REQ-FIN-011 — قائمة الدخل / Income statement
### B1 — Definition
Purpose      : عرض قائمة دخل مُشتقة حيًا تُفتح بصفر كل سنة.
Entities     : ENT-FIN-005
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Income statement; to: SCR-REQ-FIN-009 (drill-down)
Content shape: header + repeating lines with totals (revenue / expense sections)
Traces       : REQ-FIN-042, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: fiscalYearId(EXACT, REQUIRED); the period range is expressed as built by two optional
period ids, `fromPeriodId` and `toPeriodId`, translated into the `docDate` bounds those periods
span (DBF-FIN-080 / DBF-FIN-081).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_INCOME_STATEMENT. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| income statement | GET | /api/v1/fin/reports/income-statement | fiscalYearId (required), fromPeriodId?, toPeriodId? | grouped revenue/expense accounts with balances | — | REQ-FIN-042, REQ-FIN-046 |

**404 on an unknown keying id, as built.** `fiscalYearId` is resolved first and raises the
pre-existing `FIN-404-YEAR` when it does not exist; `fromPeriodId` / `toPeriodId` stay OPTIONAL
narrowings and already raised `FIN-404-PERIOD` when supplied and unknown — that half is unchanged.
The year check closes an internal contradiction: the same request used to answer 404 on an unknown
period and 200 on an unknown year.

## SCR-REQ-FIN-012 — تقارير الأبعاد / Dimension reports
### B1 — Definition
Purpose      : عرض تقارير مجمّعة حسب البُعد دون تكرار الحسابات.
Entities     : ENT-FIN-005, ENT-FIN-006
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Dimension reports
Content shape: flat record (account × dimension-value rows)
Traces       : REQ-FIN-043
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: dimensionId(EXACT), dimensionValueId(EXACT), periodId(EXACT).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_DIMENSION_REPORTS. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| dimension report | GET | /api/v1/fin/reports/dimension | dimensionId, filters | one row per account+dimension-value combination | — | REQ-FIN-043 |

# STANDALONE

## Traceability matrix
| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-FIN-001 | REQ-FIN-001, REQ-FIN-002, REQ-FIN-003 | AC-FIN-001…003 | RULE-FIN-001 | ENT-FIN-001 | SCR-REQ-FIN-001 |
| US-FIN-002 | REQ-FIN-004, REQ-FIN-005, REQ-FIN-006 | AC-FIN-004…006 | RULE-FIN-002 | ENT-FIN-002, ENT-FIN-003 | SCR-REQ-FIN-002 |
| US-FIN-003 | REQ-FIN-007, REQ-FIN-008, REQ-FIN-009 | AC-FIN-007…009 | RULE-FIN-003 | ENT-FIN-009, ENT-FIN-010 | SCR-REQ-FIN-003 |
| US-FIN-004 | REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013 | AC-FIN-010…013 | RULE-FIN-004, RULE-FIN-005, RULE-FIN-010 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-009, ENT-FIN-010 | SCR-REQ-FIN-006 |
| US-FIN-005 | REQ-FIN-014, REQ-FIN-015 | AC-FIN-014, AC-FIN-015 | — | ENT-FIN-004, ENT-FIN-005 | SCR-REQ-FIN-006 |
| US-FIN-006 | REQ-FIN-022, REQ-FIN-023, REQ-FIN-024 | AC-FIN-022…024 | — | ENT-FIN-011, ENT-FIN-012 | SCR-REQ-FIN-004 |
| US-FIN-007 | REQ-FIN-025, REQ-FIN-026 | AC-FIN-025, AC-FIN-026 | RULE-FIN-010 | ENT-FIN-013, ENT-FIN-014 | SCR-REQ-FIN-005 |
| US-FIN-008 | REQ-FIN-016, REQ-FIN-027 | AC-FIN-016, AC-FIN-027 | RULE-FIN-016 | ENT-FIN-004 | SCR-REQ-FIN-006 |
| US-FIN-009 | REQ-FIN-028, REQ-FIN-029, REQ-FIN-030 | AC-FIN-028…030 | RULE-FIN-011, RULE-FIN-012, RULE-FIN-013 | ENT-FIN-004, ENT-FIN-005 | SCR-REQ-FIN-006 |
| US-FIN-010 | REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036 | AC-FIN-031…036 | RULE-FIN-014 | ENT-FIN-007, ENT-FIN-008 | SCR-REQ-FIN-007 |
| US-FIN-011 | REQ-FIN-037, REQ-FIN-038 | AC-FIN-037, AC-FIN-038 | RULE-FIN-015 | ENT-FIN-008 | SCR-REQ-FIN-007 |
| US-FIN-012 | REQ-FIN-039 | AC-FIN-039 | — | ENT-FIN-005 | SCR-REQ-FIN-008 |
| US-FIN-013 | REQ-FIN-040 | AC-FIN-040 | RULE-FIN-006 | ENT-FIN-005 | SCR-REQ-FIN-009 |
| US-FIN-014 | REQ-FIN-041 | AC-FIN-041 | — | ENT-FIN-005 | SCR-REQ-FIN-010 |
| US-FIN-015 | REQ-FIN-042 | AC-FIN-042 | — | ENT-FIN-005 | SCR-REQ-FIN-011 |
| US-FIN-016 | REQ-FIN-043 | AC-FIN-043 | — | ENT-FIN-005, ENT-FIN-006 | SCR-REQ-FIN-012 |
| US-FIN-017 | REQ-FIN-044 | AC-FIN-044 | — | ENT-FIN-004 | — (onboarding, no screen) |
| US-FIN-018 | REQ-FIN-045 | AC-FIN-045 | — | ENT-FIN-001, ENT-FIN-004, ENT-FIN-007, ENT-FIN-008, ENT-FIN-009, ENT-FIN-010, ENT-FIN-011, ENT-FIN-013 | — (onboarding, no screen) |
| US-FIN-019 | REQ-FIN-046 | AC-FIN-046 | — | ENT-FIN-004, ENT-FIN-005 | SCR-REQ-FIN-008, SCR-REQ-FIN-009, SCR-REQ-FIN-010 |

Plus REQ-FIN-017 through REQ-FIN-021 (unified validation, traced to US-FIN-004/005/006/007/009
collectively — see each REQ's own Traces line) and RULE-FIN-006 through RULE-FIN-009 (the four
post-time checks) — every REQ traces to ≥1 story, every AC to ≥1 REQ, every RULE to ≥1 REQ,
every SCR-REQ to ≥1 REQ. No orphan, no dangling id.

## Decisions applied
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| DEFAULT | `amount` type `NUMERIC(18,4)` | [KB:erp-domain-standards §6] platform default for money | non-breaking |
| DEFAULT | RecurringTemplateLine/AllocationTarget carry a single optional dimension value, not the header's full multi-dimension model | this stage, applying §9.3.3 "as data" philosophy pragmatically — the plan does not detail multi-dimension templates/allocations explicitly | non-breaking; extend to a full JournalLineDimension-style child table if multi-dimension templates are needed later |
No ADR was raised — no ambiguity reached the breaking/non-breaking fork of §9; every point
was settled by business policies, PRD stories, the registries, the knowledge source, or
documented above as a plain DEFAULT.

## Access summary
| Page code | Screen | VIEW | CREATE | UPDATE | DELETE | Custom |
|---|---|---|---|---|---|---|
| FIN_ACCOUNTS | Chart of accounts | role-granted | role-granted | role-granted (incl. deactivate) | — | — |
| FIN_DIMENSIONS | Dimensions | role-granted | role-granted | role-granted (dimension-VALUE deactivate only — API-FIN-035; `PERM_FIN_DIMENSIONS_UPDATE`, registered and granted by V28) | — | — |
| FIN_RULES | Engine rules | role-granted | role-granted | role-granted (add line — API-FIN-011; and deactivate rule — API-FIN-034; one permission, `PERM_FIN_RULES_UPDATE`) | — | — |
| FIN_RECURRING_TEMPLATES | Recurring/reversing templates | role-granted | role-granted | role-granted (run — API-FIN-014; and deactivate template — API-FIN-036; one permission, `PERM_FIN_RECURRING_TEMPLATES_UPDATE`) | — | — |
| FIN_ALLOCATION_RULES | Allocation rules | role-granted | role-granted | role-granted (run — API-FIN-017; and deactivate rule — API-FIN-037; one permission, `PERM_FIN_ALLOCATION_RULES_UPDATE`) | — | — |
| FIN_JOURNAL_ENTRIES | Journal entries | role-granted | role-granted (incl. Post) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`) |
| FIN_PERIODS | Fiscal periods & years | role-granted (gateway, and now also the read endpoint API-FIN-033) | role-granted (year) | role-granted (open/soft-close) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE` — the distinct permission RULE-FIN-015 requires. Since V30 it is granted to `SYS_ADMIN`, so the bootstrap `admin` can close; V27's dedicated `FIN_CLOSE_APPROVER` role remains valid as a least-privilege alternative but is no longer required — see the SoD note below) |
| FIN_ACCOUNT_LEDGER | Account ledger | role-granted | — | — | — | — |
| FIN_TRIAL_BALANCE | Trial balance | role-granted | — | — | — | — |
| FIN_BALANCE_SHEET | Balance sheet | role-granted | — | — | — | — |
| FIN_INCOME_STATEMENT | Income statement | role-granted | — | — | — | — |
| FIN_DIMENSION_REPORTS | Dimension reports | role-granted | — | — | — | — |
Every action beyond VIEW additionally requires VIEW on the same screen (platform gateway
convention, `profiles/erp.yaml → conventions.security_model.gateway_action`, enforced by
SEC's own mechanism — not restated as a FIN-owned RULE).

**DELETE column, as built**: empty for every FIN screen. FIN publishes no `DELETE` endpoint;
deactivation, where it exists, is `PUT /{id}/deactivate` gated by the screen's UPDATE permission,
and V24 seeds no `PERM_FIN_*_DELETE` row (nor does V28, which adds only
`PERM_FIN_DIMENSIONS_UPDATE`). The DELETE ✓ marks above were pre-implementation and were corrected
at ALIGN-BE.

**Deactivate endpoints, as built**: five — API-FIN-004 (account), API-FIN-034 (event-type rule),
API-FIN-035 (dimension value), API-FIN-036 (recurring/reversing template) and API-FIN-037
(allocation rule). None has an `activate` counterpart, following the delivered
`AccountService.deactivate` precedent. Each is `PUT /{id}/deactivate` gated by its screen's UPDATE
permission; API-FIN-036 and API-FIN-037 reuse `PERM_FIN_RECURRING_TEMPLATES_UPDATE` and
`PERM_FIN_ALLOCATION_RULES_UPDATE`, both already seeded by V24 and already granted by V25's blanket
Tier-3 grant, so neither needed a new permission, a new error code or a migration. Deliberately NOT
built, and not pending: a deactivate on the parent `Dimension` (no REQ/AC/RULE requires it and
`Dimension.isActiveFl` drives no behaviour) and a rule-line delete (ENT-FIN-010 has no active-flag
column and FIN publishes no `DELETE` endpoint on any screen) — see SCR-REQ-FIN-002 §B4 and
SCR-REQ-FIN-003 §B4.

**DEFECT CLOSED 2026-09-12 — on those two screens, deactivating now DOES stop the run.** This
supersedes the entry that used to stand here reporting the run as ungated. `RecurringTemplateDomain
.assertCanRun()` (a new Domain companion) and `AllocationRuleDomain.assertCanRun()` are each called
first thing in their service's `run`, so a deactivated template or allocation rule is refused with
`FIN-409-NOT-ACTIVE` (409) and posts nothing. The UPDATE cells above cover run AND deactivate for
these two screens, and "deactivate" there now means a real gate, not only a record-keeping state.
**The gate is a recorded human decision, not stated requirement: no RULE-FIN-* asks for it**, and
closing the gap required inventing an error code, status and ar+en messages that no REQ, AC or RULE
provides — do not read `FIN-409-NOT-ACTIVE` back out of these tables as pre-existing spec. See
SCR-REQ-FIN-004 §B4 and SCR-REQ-FIN-005 §B4.

**SoD on FIN_PERIODS — what was removed, and what still holds (2026-09-12).** RULE-FIN-015 stands
and is enforced by the `PERM_FIN_PERIODS_CLOSE_APPROVE` gate alone, which is exactly what the rule
asks for. A stricter, unrequested check — FIN service code that refused the close for every caller
whenever any single user in the system held both that permission and
`PERM_FIN_JOURNAL_ENTRIES_CREATE` — was deleted by recorded human decision, together with the SEC
user-directory read behind it; `FIN-403-SOD-VIOLATION` is struck as unreachable. Migration V30 then
granted `PERM_FIN_PERIODS_CLOSE_APPROVE` to `SYS_ADMIN`, which V25 had deliberately withheld, so
the bootstrap `admin` can now close. Note that V27's header, being applied and immutable, still
describes the removed mechanism as live in both its numbered "OPERATIONAL PRECONDITIONS" — both are
now false; see the SEC-BE phase document for the correction in full.

**OPEN DEFECT — `update` is still missing on the same two screens.** This is now the only open half
of the original gap: a template or allocation rule created with wrong content can be retired — and,
since 2026-09-12, retiring it does stop it running — but it still cannot be corrected. Neither update was built because a
correct one must decide the fate of the aggregate's children — a template's existing lines, a
rule's existing targets and hence RULE-FIN-003's remainder-target set — which is a design question
no REQ, AC or RULE answers. Recorded as a known gap, not a reasoned exclusion. See SCR-REQ-FIN-004
§B4 and SCR-REQ-FIN-005 §B4.
══════════════════════════════════════════════════════════════════
