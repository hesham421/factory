# SRS — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-10)
Counts : ENT 2 · REQ 13 · AC 13 · RULE 4 · SCR-REQ 2 · ADR 0
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |
|---|---|
| Module | MDL — البيانات المرجعية / Master Data Lookup |
| Feature code | MDL |
| Version | v1 |
| Date | 2026-09-10 |
| Status | DRAFT (P1) |
| Prepared by | governance-factory (analysis lane) |
| Decisions applied count | 0 |

## A2 — Functional context

**In scope:** نوع اللوكب (Master) وقيمه (Detail)، شاشة عامة واحدة لإدارة كل القوائم، تسجيل
نوع جديد كبيانات من أي وحدة مستهلكة، قراءة القيم النشطة بالمفتاح لأي وحدة مستهلكة، سجل
الأنواع مجمّعًا حسب المالك، التحقق من صحة الوحدة المالكة عبر SEC.

**Out of scope:** تسلسل هرمي لقيم اللوكب (شجرة)، صلاحيات دقيقة لكل نوع لوكب على حدة (تبقى
الصلاحية على مستوى الشاشة فقط)؛ غير مذكورة في `lookup-module-plan-en.md`
[business-policies-mdl.md → SCOPE EXCEPTIONS].

**Module function (one paragraph):** MDL هو المركز الموحّد الوحيد لكل قوائم القيم
المُرمَّزة في المنصة؛ لا وحدة أخرى — بما فيها SEC وFIN لاحقًا — تحتفظ بجدول قيم مرجعية
خاص بها؛ كل وحدة تسجّل أنواعها هنا كبيانات وتقرأ قيمها من هنا وقت التشغيل.

**Detailed description (workflow narrative, roles):** وحدة مستهلكة (مثل FIN لاحقًا) تُسجّل
نوع لوكب جديد كبيانات، مسمّية نفسها مالكًا → MDL يتحقق من أن رمز الوحدة مسجَّل فعليًا في
SEC (قراءة فقط، بلا مفتاح خارجي فعلي) → مسؤول مخوَّل يدير قيم ذلك النوع عبر الشاشة العامة
الواحدة (رئيسي-تفصيلي) → أي وحدة تقرأ القيم النشطة بالمفتاح وقت التشغيل، مرتبة حسب الترتيب.

**Current situation:** لا يوجد نظام سابق ضمن هذه الدفعة؛ SEC هي الوحدة الوحيدة المكتملة
حتى الآن ولا تملك آلية قوائم مرجعية مركزية — قيمها الثلاث (USER_STATUS, SIGNUP_STATUS,
AUDIT_EVENT_TYPE) مُقيَّدة بـ CHECK محليًا (ADR-SEC-001)، على أن تُهاجَر لاحقًا إلى هنا.

**Current difficulties:** بلا مركزية، كل وحدة تخترع قوائمها الخاصة فتتضارب القيم — بالضبط
المشكلة التي يحلّها MDL (KB:erp-domain-standards §2 rule 3).

**Proposed system and benefits:** مركز واحد موثوق يمنع الازدواج والتضارب، ويجعل إضافة قائمة
أو قيمة جديدة عملية بيانات بحتة، لا تغييرًا في الشيفرة.

**General notes (constraints, deferred items):** لا محرك سير عمل؛ هجرة قوائم SEC الثلاث
إلى هذا المركز مؤجّلة لإصدار v2 من SEC (خارج نطاق هذه الدفعة، موثّقة في ADR-SEC-001).

## A3 — Entities and fields

Standard fields per kind (profile.conventions.entity_defaults):
master → nameAr, nameEn, code, isActiveFl, createdBy, createdAt, updatedBy, updatedAt;
lookup → code, nameAr, nameEn, sortOrder, isActiveFl.

### ENT-MDL-001 — نوع اللوكب / LookupType
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | SHARED (owner) — every consuming module registers and reads its own types here | No — `key` is a client-chosen stable string, not a platform-numbered sequence [§3.3 test] | create, read, search, update (name only), deactivate | consumed (registered into) by every future module | lookup-module-plan-en.md §2-§3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| lookupTypePk | number | yes (system) | — | primary key | معرّف نوع اللوكب | LookupType id |
| key | text | yes | unique, immutable after create [RULE-MDL-003] | the string every consumer cites (e.g. `USER_STATUS`) | المفتاح | Key |
| ownerModuleCode | text | yes | must exist in SEC's ModuleRegistry [RULE-MDL-001] | namespacing | رمز الوحدة المالكة | Owner module code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-MDL-002 — قيمة اللوكب / LookupValue
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| lookup | SHARED (owner) — every consuming module reads/manages its own values here | No | create, read, search, update, deactivate, reorder | consumed (read) by every future module | lookup-module-plan-en.md §3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| lookupValuePk | number | yes (system) | — | primary key | معرّف قيمة اللوكب | LookupValue id |
| lookupTypeId | reference | yes | ENT-MDL-001 | — | نوع اللوكب | Lookup type |
| code | text | yes | unique within its lookupTypeId [RULE-MDL-002] | the value a consumer stores | الرمز | Code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| sortOrder | number | yes | — | display order | ترتيب العرض | Sort order |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-MDL-001 — إنشاء نوع لوكب / Create a lookup type
Pattern    : event
Statement  : When an administrator creates a lookup type naming its owner module, the system shall record it as an active lookup type.
Traces     : US-MDL-001, US-MDL-004
Entities   : ENT-MDL-001
Rationale  : registration as data, per module's own integration
Source     : lookup-module-plan-en.md §2-§3
Priority   : HIGH
#### AC-MDL-001 — [REQ-MDL-001]
Given a unique key and a registered owner module code
When an administrator submits the lookup type form
Then the system creates an active LookupType

### REQ-MDL-002 — رفض نوع لوحدة غير مسجّلة / Reject a type for an unregistered module
Pattern    : unwanted
Statement  : If a lookup type registration names a module that is not registered in the Security module, then the system shall reject the registration.
Traces     : US-MDL-001, US-MDL-004
Entities   : ENT-MDL-001
Rationale  : RULE-MDL-001; POL-MDL-003
Source     : lookup-module-plan-en.md §3
Priority   : HIGH
#### AC-MDL-002 — [REQ-MDL-002]
Given an owner module code with no ModuleRegistry row in SEC
When a lookup type registration names that code
Then the system rejects it and creates no LookupType

### REQ-MDL-003 — تعديل اسم نوع اللوكب / Edit a lookup type's name
Pattern    : event
Statement  : When an administrator edits a lookup type's name, the system shall update it without changing its key.
Traces     : US-MDL-001
Entities   : ENT-MDL-001
Rationale  : RULE-MDL-003 — key immutability
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-003 — [REQ-MDL-003]
Given an existing LookupType
When an administrator updates its nameAr/nameEn
Then the system saves the new names and leaves the key unchanged

### REQ-MDL-004 — تعطيل نوع لوكب / Deactivate a lookup type
Pattern    : event
Statement  : When an administrator deactivates a lookup type, the system shall exclude its values from every future consumer read.
Traces     : US-MDL-001
Entities   : ENT-MDL-001
Rationale  : RULE-MDL-004
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-004 — [REQ-MDL-004]
Given an active LookupType
When an administrator deactivates it
Then the system sets isActiveFl=false and REQ-MDL-011 no longer returns its values

### REQ-MDL-005 — اختيار النوع وعرض قيمه / Select a type and list its values
Pattern    : event
Statement  : When a user selects a lookup type in the master, the system shall list its values in the detail.
Traces     : US-MDL-002
Entities   : ENT-MDL-001, ENT-MDL-002
Rationale  : the generic master-detail mechanism, POL-MDL-004
Source     : lookup-module-plan-en.md §3
Priority   : HIGH
#### AC-MDL-005 — [REQ-MDL-005]
Given a lookup type with three values
When a user selects it in the master list
Then the system lists exactly those three values in the detail, ordered by sortOrder

### REQ-MDL-006 — إنشاء قيمة لوكب / Create a lookup value
Pattern    : event
Statement  : When an authorized user creates a value under a selected lookup type, the system shall record its code, bilingual labels, sort order and active flag.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : POL-MDL-005
Source     : lookup-module-plan-en.md §3
Priority   : HIGH
#### AC-MDL-006 — [REQ-MDL-006]
Given a selected lookup type and a code not yet used within it
When the user submits the value form
Then the system creates an active LookupValue under that type

### REQ-MDL-007 — رفض تكرار الرمز ضمن النوع / Reject a duplicate code within a type
Pattern    : unwanted
Statement  : If two lookup values under the same lookup type share the same code, then the system shall reject the second.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : RULE-MDL-002; POL-MDL-006
Source     : lookup-module-plan-en.md §6
Priority   : HIGH
#### AC-MDL-007 — [REQ-MDL-007]
Given a lookup type already holding a value with code "ACTIVE"
When a user attempts to create another value with code "ACTIVE" under the same type
Then the system rejects it and creates no second row

### REQ-MDL-008 — تعديل قيمة لوكب / Edit a lookup value
Pattern    : event
Statement  : When an authorized user edits a lookup value's labels or sort order, the system shall update it.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : POL-MDL-005
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-008 — [REQ-MDL-008]
Given an existing LookupValue
When the user updates its nameAr/nameEn/sortOrder
Then the system saves the new values (code and lookupTypeId remain unchanged)

### REQ-MDL-009 — تعطيل قيمة لوكب / Deactivate a lookup value
Pattern    : event
Statement  : When an authorized user deactivates a lookup value, the system shall exclude it from future consumer reads.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : POL-MDL-005
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-009 — [REQ-MDL-009]
Given an active LookupValue
When the user deactivates it
Then the system sets isActiveFl=false and REQ-MDL-011 no longer returns it

### REQ-MDL-010 — إعادة ترتيب قيم اللوكب / Reorder lookup values
Pattern    : event
Statement  : When an authorized user reorders the values of a lookup type, the system shall persist the new sort order for each affected value.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : sortOrder is a stored, consumer-facing field (A3)
Source     : lookup-module-plan-en.md §3
Priority   : LOW
#### AC-MDL-010 — [REQ-MDL-010]
Given three values with sortOrder 1,2,3
When the user reorders them to 3,1,2
Then the system persists sortOrder=3,1,2 respectively and REQ-MDL-011 returns them in that order

### REQ-MDL-011 — قراءة القيم النشطة بالمفتاح / Read active values by key
Pattern    : event
Statement  : When a consuming module requests the active values of a lookup type by key, the system shall return them ordered by sort order.
Traces     : US-MDL-003
Entities   : ENT-MDL-001, ENT-MDL-002
Rationale  : POL-MDL-001 — the module's entire reason to exist
Source     : lookup-module-plan-en.md §2, §4
Priority   : HIGH
#### AC-MDL-011 — [REQ-MDL-011]
Given a lookup type "PAYMENT_METHOD" with two active and one inactive value
When a consuming module requests its values by key
Then the system returns exactly the two active values, ordered by sortOrder

### REQ-MDL-012 — رفض مفتاح نوع غير موجود / Reject an unknown type key
Pattern    : unwanted
Statement  : If a consuming module requests values for a lookup type key that does not exist, then the system shall return a not-found error.
Traces     : US-MDL-003
Entities   : ENT-MDL-001
Rationale  : distinguishes "type exists, zero values" (success, empty) from "type never registered" (integration defect)
Source     : lookup-module-plan-en.md §4
Priority   : MEDIUM
#### AC-MDL-012 — [REQ-MDL-012]
Given no LookupType with key "NOT_A_REAL_KEY"
When a consuming module requests its values
Then the system returns a not-found error, not an empty success

### REQ-MDL-013 — تصفّح سجل الأنواع حسب المالك / Browse the type registry by owner
Pattern    : event
Statement  : When an administrator browses the lookup-type registry, the system shall group active lookup types by their owner module.
Traces     : US-MDL-005
Entities   : ENT-MDL-001
Rationale  : POL-MDL-002
Source     : lookup-module-plan-en.md §7
Priority   : MEDIUM
#### AC-MDL-013 — [REQ-MDL-013]
Given lookup types owned by SEC and by MDL... (example: two types owned by SEC, one by MDL's own future host)
When an administrator opens the registry screen
Then the system shows the types grouped under their respective owner module headings

## A5 — Business rules

### RULE-MDL-001 — رفض نوع لوحدة غير مسجّلة / Reject a type for an unregistered owner module
Scope      : ENT-MDL-001
Trigger    : on create (lookup type)
Statement  : The system shall reject a lookup type registration whose owner module code has no ModuleRegistry row in SEC.
Data source: ENT-MDL-001.ownerModuleCode — validated against SEC's module registry through XM-MDL-001 (SOFT-READ, application layer)
Message    : ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" · en: "The owning module is not registered in the Security module"
Traces     : REQ-MDL-002
Source     : lookup-module-plan-en.md §3

### RULE-MDL-002 — رفض رمز مكرر ضمن النوع / Reject a duplicate code within a type
Scope      : ENT-MDL-002
Trigger    : on create (lookup value)
Statement  : The system shall reject a lookup value whose code already exists under the same lookup type.
Data source: ENT-MDL-002.code, ENT-MDL-002.lookupTypeId
Message    : ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" · en: "This code is already used within this type"
Traces     : REQ-MDL-007
Source     : lookup-module-plan-en.md §6

### RULE-MDL-003 — عدم تغيير مفتاح النوع بعد إنشائه / Key immutability after creation
Scope      : ENT-MDL-001
Trigger    : on update (lookup type)
Statement  : The system shall prevent editing a lookup type's key after creation.
Data source: ENT-MDL-001.key
Message    : ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" · en: "A lookup type's key cannot be changed after creation"
Traces     : REQ-MDL-003
Source     : lookup-module-plan-en.md §3 (the key is what every consumer already cites)

### RULE-MDL-004 — استبعاد قيم النوع المعطّل / Exclude an inactive type's values from reads
Scope      : ENT-MDL-001
Trigger    : on evaluate (consumer read, REQ-MDL-011)
Statement  : While a lookup type is inactive, the system shall exclude its values from consumer reads.
Data source: ENT-MDL-001.isActiveFl
Message    : ar: "هذا النوع معطّل حاليًا" · en: "This lookup type is currently inactive"
Traces     : REQ-MDL-004, REQ-MDL-011
Source     : lookup-module-plan-en.md §3

## A6 — Lookups
None — MDL introduces no domain-specific coded list of its own (it is the generic
mechanism every other module's lookup types run on top of; see module-registry-mdl.md →
LOOKUPS OWNED).

## A7 — Status lifecycle
`LookupType.isActiveFl` and `LookupValue.isActiveFl` are each a plain binary active flag
(≤2 states) — not applicable for a diagram.

## A8 — Module dependencies
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate (assigned by P2) |
|---|---|---|---|---|
| ModuleRegistry | ENT-SEC-004 | SEC | SOFT-READ | assigned by P2 (this module) |

| External service | Purpose | Integration kind |
|---|---|---|
None — lookup-module-plan-en.md §5 names Notifications/File Service as available but MDL's
PRD (US-MDL-001..005) states no need that would use either; not built this v1.

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-MDL-001 — اللوكبات العامة / Generic Lookups (master-detail, all lists)
### B1 — Definition
Purpose      : إدارة كل قوائم القيم المُرمَّزة عبر شاشة واحدة.
Entities     : ENT-MDL-001, ENT-MDL-002
Operations   : search, create, read, update, deactivate (type); create, read, search, update, deactivate, reorder (value)
Users        : مسؤول مخوَّل بصلاحية الشاشة (أي وحدة، حسب منحها من SEC)
Navigation   : MDL → Reference data → Generic Lookups
Content shape: header + repeating lines with totals — رئيسي (أنواع) + تفصيلي (قيم) قابل لإعادة الترتيب
Traces       : REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010
Composite    : Master (types) + Detail (values) = ONE screen requirement
### B2 — Search / list
Master filters: key(LIKE), ownerModuleCode(EXACT), isActiveFl(EXACT) — correspond to result columns.
Detail filters: code(LIKE) — corresponds to result column.
### B3 — Input
Master fields: key, ownerModuleCode, nameAr, nameEn (ENT-MDL-001). Detail fields: code,
nameAr, nameEn, sortOrder (drag-to-reorder), isActiveFl (ENT-MDL-002). Buttons: activate/
deactivate per row at both levels.
### B4 — Access
Page code: MDL_LOOKUPS. Actions: VIEW, CREATE, UPDATE, DELETE (deactivate), per §7.1
(gateway VIEW).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search types | POST | /api/v1/mdl/lookup-types/search | filters, paging | Page\<LookupType\> | — | REQ-MDL-001 |
| create type | POST | /api/v1/mdl/lookup-types | key, ownerModuleCode, nameAr, nameEn | LookupType | RULE-MDL-001 | REQ-MDL-001, REQ-MDL-002 |
| update type | PUT | /api/v1/mdl/lookup-types/{id} | nameAr, nameEn | LookupType | RULE-MDL-003 | REQ-MDL-003 |
| deactivate type | DELETE | /api/v1/mdl/lookup-types/{id} | id | confirmation | — | REQ-MDL-004 |
| search values | POST | /api/v1/mdl/lookup-types/values/search | filters, paging (parent lookupTypeId in filters) | Page\<LookupValue\> | — | REQ-MDL-005 |
| create value | POST | /api/v1/mdl/lookup-types/{id}/values | code, nameAr, nameEn, sortOrder | LookupValue | RULE-MDL-002 | REQ-MDL-006, REQ-MDL-007 |
| update value | PUT | /api/v1/mdl/lookup-values/{id} | nameAr, nameEn, sortOrder | LookupValue | — | REQ-MDL-008 |
| deactivate value | DELETE | /api/v1/mdl/lookup-values/{id} | id | confirmation | — | REQ-MDL-009 |
| reorder values | PATCH | /api/v1/mdl/lookup-types/{id}/values/reorder | ordered list of value ids | Page\<LookupValue\> | — | REQ-MDL-010 |

## SCR-REQ-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner
### B1 — Definition
Purpose      : تصفّح أنواع اللوكب مجمّعة حسب الوحدة المالكة.
Entities     : ENT-MDL-001
Operations   : search, read
Users        : مسؤول مخوَّل
Navigation   : MDL → Reference data → Type registry; from: SCR-REQ-MDL-001
Content shape: true hierarchy (parent/child) — وحدة مالكة → أنواعها
Traces       : REQ-MDL-013
Composite    : single screen (grouped list) = ONE screen requirement
### B2 — Search / list
Filters: ownerModuleCode(EXACT), key(LIKE) — correspond to result columns.
### B3 — Input
Read-only browse; no create/update here (management happens on SCR-REQ-MDL-001).
### B4 — Access
Page code: MDL_TYPE_REGISTRY. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| browse registry | POST | /api/v1/mdl/lookup-types/by-owner/search | filters | grouped List\<OwnerGroupResponse\> | — | REQ-MDL-013 |
| read values by key (consumer API) | GET | /api/v1/mdl/lookups | type=key | List\<LookupValue\> (active only) | RULE-MDL-004 | REQ-MDL-011, REQ-MDL-012 |

# STANDALONE

## Traceability matrix
| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-MDL-001 | REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004 | AC-MDL-001…004 | RULE-MDL-001, RULE-MDL-003, RULE-MDL-004 | ENT-MDL-001 | SCR-REQ-MDL-001 |
| US-MDL-002 | REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010 | AC-MDL-005…010 | RULE-MDL-002 | ENT-MDL-001, ENT-MDL-002 | SCR-REQ-MDL-001 |
| US-MDL-003 | REQ-MDL-011, REQ-MDL-012 | AC-MDL-011, AC-MDL-012 | RULE-MDL-004 | ENT-MDL-001, ENT-MDL-002 | SCR-REQ-MDL-002 |
| US-MDL-004 | REQ-MDL-001, REQ-MDL-002 | AC-MDL-001, AC-MDL-002 | RULE-MDL-001 | ENT-MDL-001 | SCR-REQ-MDL-001 |
| US-MDL-005 | REQ-MDL-013 | AC-MDL-013 | — | ENT-MDL-001 | SCR-REQ-MDL-002 |

Every story traces to ≥1 REQ; every REQ traces to ≥1 AC; every RULE traces to a REQ; every
SCR-REQ traces to ≥1 REQ. No orphan, no dangling id.

## Decisions applied
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
No ADR was raised — no ambiguity reached the breaking/non-breaking fork of §9; the MDL→SEC
SOFT-READ classification was settled at P0 (module-registry-mdl.md → AUTO-DECISIONS), not
here, and every other point was settled by the plan directly.

## Access summary
| Page code | Screen | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|---|
| MDL_LOOKUPS | Generic Lookups | role-granted | role-granted | role-granted | role-granted (deactivate) |
| MDL_TYPE_REGISTRY | Type registry by owner | role-granted | — | — | — |
Every action beyond VIEW additionally requires VIEW on the same screen (platform gateway
convention, `profiles/erp.yaml → conventions.security_model.gateway_action`, applied the
same way SEC's own RULE-SEC-007 documents it — not restated as an MDL-owned RULE since it
is a platform-wide convention, not an MDL-specific constraint).
══════════════════════════════════════════════════════════════════
