<!-- P1 stage output — governed by factory.yaml stages[P1]; see shared/GOVERNANCE-CORE.md -->
# SRS — Finance / المحاسبة والمالية (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-10)
Counts : ENT 13 · REQ 34 · AC 37 · RULE 14 · SCR-REQ 16 · ADR 3
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |
|---|---|
| Module | FIN — Finance / المحاسبة والمالية |
| Feature code | FIN |
| Version | v1 |
| Date | 2026-09-10 |
| Status | DRAFT |
| Prepared by | P1 engine (lane `analysis`) |
| Decisions applied | 3 ADR + 6 DEFAULT (see STANDALONE §Decisions applied) |

## A2 — Functional context

**In scope** — a complete, standalone General Ledger module, generic and pluggable
into any host system: chart of accounts with data-defined dimensions, a single
generic reference-data (lookups) screen, a data-driven rules engine turning
canonical accounting events into journal entries, four journal sources (event,
manual, recurring/reversing, allocation), direct posting after automatic
validation with period-close as the sole human control point, reversal-only
correction, fiscal period/year lifecycle with automatic year-end carryforward,
a fully independent RBAC, and reporting derived exclusively from posted entries
with drill-down to source. (plan §0–§11)

**Out of scope** — the Business Module and any business-world entity; the Event
consumer and the AQ/RabbitMQ transport layer; any read/write from or to a host
system's tables; account numbers inside the event payload; multi-currency,
multi-ledger/multi-entity, intercompany entries, statistical accounts,
multi-pattern fiscal calendar, attachments; any workflow/BPM engine (plan §12;
`profiles/erp.yaml → conventions.workflow_engine`).

**Module function** — FIN receives a canonical accounting event at its single
entry point, resolves it to a balanced journal entry through data-defined rules,
posts it after automatic validation, and reports on it once posted — all
dimensions, event types, and rules are configuration, never code, so the same
module fits any host system (plan §0).

**Detailed description (workflow narrative, roles)** — An Accounting
Configuration Administrator sets up the chart of accounts, dimensions, lookups
and event-type rules once per host system. An Accountant works the daily flow:
events post automatically; the Accountant enters manual, recurring or
allocation entries when no event applies, and reverses a posted entry when a
correction is needed. A Financial Controller is the sole human checkpoint,
reviewing and approving the close of each fiscal period and year — never the
same person who created the entries being closed. An Accounting System
Administrator manages FIN's own users, roles and permissions, independent of
any other module. An Auditor consumes ledger, trial balance and statement
reports and drills down from any reported figure to its originating entry and
source event (plan §0–§9).

**Current situation** — none; FIN is a new module (module-registry-fin.md:
Source = NEW).

**Current difficulties** — not applicable (greenfield module).

**Proposed system and benefits** — a rules-as-data engine and fully isolated
reference data let the same FIN build be pointed at a different host system by
changing configuration only, never code (plan §0, governing rule "Everything
that can change = defined data, not code").

**General notes (constraints, deferred items)** — FIN is a ROOT module with
`DEPENDENCIES: NONE` — a deliberate deviation from the platform's shared
`ORG`/`SEC`/`MDL` pattern, confirmed by the user at the `prd-approval` gate
(see STANDALONE §Decisions applied, Decision 1). Deferred scope items are
recorded as SCOPE EXCEPTIONS in `business-policies-fin.md`, not as open items
here.

## A3 — Entities and fields

Standard fields per kind (`profiles/erp.yaml → conventions.entity_defaults`,
applied once here, not repeated per entity):
| Kind | Default fields |
|---|---|
| master | nameAr, nameEn, code, isActiveFl, createdBy, createdAt, updatedBy, updatedAt |
| transactional | docNo, docDate, statusCode, fiscalYearId, periodId, createdBy, createdAt, updatedBy, updatedAt |
| lookup | code, nameAr, nameEn, sortOrder, isActiveFl |
| config | key, valueAr, valueEn, isActiveFl |

All 13 entities are **PRIVATE** to FIN — no SHARED (owner) and no SHARED
(consumer) entity exists, per FIN's confirmed total-isolation design (A8).
Names below match `modules/FIN/P0/module-registry-fin.md` exactly (ARCH-4).

### ENT-FIN-001 — شجرة الحسابات / Chart of Account
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | no (internal code only, not a numbered document — §3.3 test fails a, b, c) | search, create, read, update, deactivate | none | plan §1 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| accountPk | number | yes (system) | — | primary key | معرّف الحساب | Account ID |
| parentAccountId | reference→ENT-FIN-001 | no | self | null for a root/top account | الحساب الأب | Parent account |
| code | text | yes | — | unique per tree | رمز الحساب | Account code |
| nameAr / nameEn | text | yes | — | master default | اسم الحساب | Account name |
| accountType | lookup→account-types | yes | asset / liability / equity / revenue / expense (business-policies-fin.md custom values) | RULE-011 | نوع الحساب | Account type |
| natureCode | lookup→account-nature | yes | debit / credit | DEFAULT: a fixed 2-value nature list, not a growing lookup — Source: plan §1.2 ("its nature (debit/credit)"); Override: none needed, the set is closed by accounting convention | طبيعة الحساب | Account nature |
| acceptsDirectPostingFl | flag | yes | default false | true only on leaf accounts (RULE-001) | يقبل الترحيل المباشر | Accepts direct posting |
| isRetainedEarningsAccountFl | flag | yes | default false | exactly one active account may hold true (RULE-011) | حساب الأرباح المحتجزة | Retained-earnings account |
| isActiveFl / createdBy / createdAt / updatedBy / updatedAt | master defaults | yes (system-filled for audit) | — | — | — | — |

### ENT-FIN-002 — بُعد الحساب / Account Dimension (definition + values)
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | no | search, create, read, update, deactivate (definition and values) | none | plan §1.2, §1.3 |

**Dimension definition fields**
| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| dimensionKey | text | yes | — | unique code, e.g. `INVESTOR` | مفتاح البُعد | Dimension key |
| nameAr / nameEn | text | yes | — | — | اسم البُعد | Dimension name |
| controlType | lookup→dimension-control-type | yes | FIXED_LIST / REFERENCE_ENTITY | DEFAULT: a value set below the profile's "growing/large set → reference entity" threshold (§3.3 LOOKUPS rule) uses FIXED_LIST; a large or externally-sourced set (e.g. investors) uses REFERENCE_ENTITY — Source: SRS §3.3 rule, applied per-dimension by the administrator, not hardcoded | نوع الضبط | Control type |
| isActiveFl | flag | yes | default true | — | نشط | Active |

**Dimension value fields** (one dimension value row per `dimensionKey`)
| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| dimensionKey | reference→ dimension definition (this ENT) | yes | — | — | البُعد | Dimension |
| valueCode | text | yes | — | e.g. an investor code | رمز القيمة | Value code |
| valueNameAr / valueNameEn | text | yes | — | — | اسم القيمة | Value name |
| sortOrder | number | no | — | — | ترتيب العرض | Sort order |
| isActiveFl | flag | yes | default true | — | نشط | Active |

### ENT-FIN-003 — البيانات المرجعية المحاسبية / Accounting Reference List (lookup type + values)
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| lookup | PRIVATE | no | search, create, read, update, deactivate (type and values, one generic screen) | none | plan §2 |

**Lookup type fields**
| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| lookupKey | text | yes | payment-methods / accounting-event-types / account-types / period-states / journal-types (module-registry-fin.md "LOOKUPS OWNED") | unique | مفتاح القائمة | Lookup key |
| nameAr / nameEn | text | yes | — | — | اسم القائمة | Lookup name |
| isActiveFl | flag | yes | default true | — | نشط | Active |

**Lookup value fields** (one row per `lookupKey`)
| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| lookupKey | reference→ lookup type (this ENT) | yes | — | — | القائمة | Lookup |
| valueCode | text | yes | — | unique per key | رمز القيمة | Value code |
| labelAr / labelEn | text | yes | — | — | التسمية | Label |
| sortOrder | number | no | — | — | ترتيب العرض | Sort order |
| isActiveFl | flag | yes | default true | — | نشط | Active |

### ENT-FIN-004 — قاعدة نوع الحدث / Event-Type Rule
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | no | search, create, read, update, deactivate | none | plan §3.1, §3.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| eventTypeCode | reference→ accounting-event-types lookup value (ENT-FIN-003) | yes | — | exactly one active rule per event type (RULE-012) | نوع الحدث | Event type |
| nameAr / nameEn | text | yes | — | — | اسم القاعدة | Rule name |
| isActiveFl / createdBy / createdAt / updatedBy / updatedAt | config defaults | yes | — | — | — | — |

### ENT-FIN-005 — سطر القاعدة / Rule Line (account / amount / direction / distribution derivation)
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | no | create, read, update, delete (as a child of its Event-Type Rule) | none | plan §3.2, §3.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| eventTypeRuleId | reference→ENT-FIN-004 | yes | — | — | القاعدة | Rule |
| lineNo | number | yes | — | order within the entry | رقم السطر | Line no |
| accountDerivationType | lookup→account-derivation-type | yes | CONSTANT / EVENT_FIELD / MAPPING_SET (plan §3.2 a) | — | نوع اشتقاق الحساب | Account derivation type |
| constantAccountId | reference→ENT-FIN-001 | when accountDerivationType=CONSTANT | — | — | الحساب الثابت | Constant account |
| eventFieldName | text | when accountDerivationType=EVENT_FIELD | — | the event's dimension attribute placed directly into the segment | حقل الحدث | Event field |
| mappingEntries (repeating) | — | when accountDerivationType=MAPPING_SET | — | see below | خريطة الاشتقاق | Mapping entries |
| ↳ eventAttributeName | text | yes (in the group) | — | — | اسم الخاصية | Event attribute name |
| ↳ eventAttributeValue | text | yes (in the group) | — | — | قيمة الخاصية | Event attribute value |
| ↳ resultingDimensionValue | reference→ ENT-FIN-002 value | yes (in the group) | — | segment value produced by this combination | القيمة الناتجة | Resulting value |
| amountSourceField | text | yes | — | event field the amount is read from (plan §3.2 b) | حقل المبلغ | Amount source field |
| amountSourceOperation | lookup→amount-source-operation | yes | DIRECT / PERCENTAGE / REMAINDER | — | عملية المبلغ | Amount operation |
| amountOperationValue | decimal | when amountSourceOperation=PERCENTAGE | — | the percentage | قيمة العملية | Operation value |
| directionCode | lookup→debit-credit | yes | DEBIT / CREDIT | plan §3.2 c | الاتجاه | Direction |
| distributionType | lookup→distribution-type | yes | FIXED / PERCENTAGE / REMAINDER (plan §3.3) | RULE-005 | نوع التوزيع | Distribution type |
| distributionValue | decimal | when distributionType∈{FIXED,PERCENTAGE} | — | — | قيمة التوزيع | Distribution value |
| isActiveFl | flag | yes | default true | — | نشط | Active |

### ENT-FIN-006 — القيد المحاسبي / Journal Entry
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | **yes** — the numbered transactional document itself (§3.3 test c) | search, create (manual source only), read, reverse (action) | none | plan §4, §5, §6 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| entryNo | text | yes | system-generated on first save, read-only after, unique per entity type | NUMBERING rule (§3.3) — via the platform numbering engine, never generated in-module | رقم القيد | Entry no |
| entryDate | date-time | yes | — | — | تاريخ القيد | Entry date |
| sourceTypeCode | lookup→journal-types | yes | Event-generated / Manual / Recurring-Reversing / Allocation / Void-Correction | plan §4, §6.2 | مصدر القيد | Source type |
| statusCode | lookup→journal-entry-status | yes | DRAFT / POSTED | A7 | حالة القيد | Status |
| fiscalYearId | reference→ENT-FIN-010 | yes | transactional default | — | السنة المالية | Fiscal year |
| periodId | reference→ENT-FIN-011 | yes | transactional default | must be Open (RULE-004) | الفترة المالية | Period |
| sourceEventReference | text | when sourceTypeCode=Event-generated | the canonical event's own reference, never an account number (plan §12 "Passing account numbers within the event payload... excluded") | used for drill-down (REQ-034) | مرجع الحدث المصدر | Source event reference |
| templateId | reference→ENT-FIN-008 | when sourceTypeCode=Recurring-Reversing | — | — | القالب | Template |
| allocationRuleId | reference→ENT-FIN-009 | when sourceTypeCode=Allocation | — | — | قاعدة التوزيع | Allocation rule |
| reversalOfEntryId | reference→ENT-FIN-006 (self) | when sourceTypeCode=Void-Correction | RULE-007 | يربط القيد بأصله | القيد الأصلي المعكوس | Reverses entry |
| reversedByEntryId | reference→ENT-FIN-006 (self) | system-set when this entry is later reversed | read-only, never client-set | القيد العاكس | Reversed by entry |
| createdBy / createdAt / updatedBy / updatedAt | transactional defaults | yes (system-filled) | — | — | — | — |

### ENT-FIN-007 — سطر القيد / Journal Entry Line
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | no (child of a numbered document) | create, read (as a child of its Journal Entry; immutable once the header is POSTED — RULE-006) | none | plan §4, §5 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalEntryId | reference→ENT-FIN-006 | yes | — | — | القيد | Journal entry |
| lineNo | number | yes | — | — | رقم السطر | Line no |
| accountId | reference→ENT-FIN-001 | yes | must accept direct posting (RULE-001) | — | الحساب | Account |
| dimensionValues (repeating) | reference→ ENT-FIN-002 value | no (per configured dimension) | one per active dimension applicable to the posting | RULE-003 | قيم الأبعاد | Dimension values |
| directionCode | lookup→debit-credit | yes | DEBIT / CREDIT | — | الاتجاه | Direction |
| amount | decimal | yes | > 0 | RULE-002 (header balance) | المبلغ | Amount |
| descriptionAr / descriptionEn | text | no | — | — | الوصف | Description |

### ENT-FIN-008 — قالب القيد المتكرر / العكسي / Recurring-Reversing Entry Template
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | no | search, create, read, update, deactivate | none | plan §4.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| templateNameAr / templateNameEn | text | yes | — | — | اسم القالب | Template name |
| templateTypeCode | lookup→template-type | yes | RECURRING / REVERSING (plan §4.3) | — | نوع القالب | Template type |
| scheduleRule | text | yes | a data-defined recurrence definition | ADR-FIN-001 | قاعدة الجدولة | Schedule rule |
| nextRunDate | date-time | yes (system-maintained) | computed from scheduleRule after each run | — | تاريخ التشغيل التالي | Next run date |
| templateLines (repeating) | — | yes, ≥ 1 | — | mirrors Journal Entry Line's shape | سطور القالب | Template lines |
| ↳ accountId | reference→ENT-FIN-001 | yes (in the group) | — | — | الحساب | Account |
| ↳ dimensionValues | reference→ENT-FIN-002 value | no (in the group) | — | — | قيم الأبعاد | Dimension values |
| ↳ amountSource | decimal or text (formula) | yes (in the group) | fixed amount or a formula reference | RULE-013 | مصدر المبلغ | Amount source |
| ↳ directionCode | lookup→debit-credit | yes (in the group) | DEBIT / CREDIT | — | الاتجاه | Direction |
| isActiveFl / createdBy / createdAt / updatedBy / updatedAt | config defaults | yes | — | — | — | — |

### ENT-FIN-009 — قاعدة التوزيع / Allocation Rule
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | no | search, create, read, update, deactivate | none | plan §4.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| ruleNameAr / ruleNameEn | text | yes | — | — | اسم القاعدة | Rule name |
| sourceAccountId | reference→ENT-FIN-001 | yes | — | balance being distributed | حساب المصدر | Source account |
| sourceDimensionValues (repeating) | reference→ENT-FIN-002 value | no | — | scopes the balance to distribute | قيم أبعاد المصدر | Source dimension values |
| allocationLines (repeating) | — | yes, ≥ 1 | — | RULE-014 | سطور التوزيع | Allocation lines |
| ↳ targetAccountId | reference→ENT-FIN-001 | yes (in the group) | — | — | حساب الهدف | Target account |
| ↳ targetDimensionValues | reference→ENT-FIN-002 value | no (in the group) | — | — | قيم أبعاد الهدف | Target dimension values |
| ↳ distributionType | lookup→distribution-type | yes (in the group) | FIXED / PERCENTAGE / REMAINDER | RULE-014 | نوع التوزيع | Distribution type |
| ↳ distributionValue | decimal | when distributionType∈{FIXED,PERCENTAGE} | — | — | قيمة التوزيع | Distribution value |
| isActiveFl / createdBy / createdAt / updatedBy / updatedAt | config defaults | yes | — | — | — | — |

### ENT-FIN-010 — السنة المالية / Fiscal Year
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | no (a code, not an external reference document) | search, create, read, update (status transitions only) | none | plan §7 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| yearCode | text | yes | — | unique | رمز السنة | Year code |
| startDate / endDate | date-time | yes | — | — | تاريخ البداية / النهاية | Start / end date |
| statusCode | lookup→fiscal-year-status | yes | OPEN / YEAR_END_CLOSED | A7 | حالة السنة | Status |
| isActiveFl / nameAr / nameEn / createdBy / createdAt / updatedBy / updatedAt | master defaults | yes | — | — | — | — |

### ENT-FIN-011 — الفترة المالية / Fiscal Period
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | no | search, create, read, update (status transitions), approve-close (action) | none | plan §7 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| fiscalYearId | reference→ENT-FIN-010 | yes | — | — | السنة المالية | Fiscal year |
| periodCode | text | yes | — | unique within the year | رمز الفترة | Period code |
| sequenceNo | number | yes | — | ordering within the year | الترتيب | Sequence no |
| startDate / endDate | date-time | yes | — | — | تاريخ البداية / النهاية | Start / end date |
| statusCode | lookup→period-states | yes | Open / Soft Close / Hard Close (business-policies-fin.md custom values) | A7 | حالة الفترة | Status |
| closeApprovedBy | reference→ENT-FIN-012 | when statusCode∈{Soft Close,Hard Close} | must differ from every entry's creator in this period (RULE-008) | معتمد الإقفال | Close approved by |
| closeApprovedAt | date-time | when statusCode∈{Soft Close,Hard Close} | — | — | تاريخ الاعتماد | Close approved at |
| isActiveFl / nameAr / nameEn / createdBy / createdAt / updatedBy / updatedAt | master defaults | yes | — | — | — | — |

### ENT-FIN-012 — مستخدم المحاسبة / Accounting User
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | no | search, create, read, update, deactivate | none | plan §8 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| username | text | yes | — | unique | اسم المستخدم | Username |
| nameAr / nameEn | text | yes | — | — | الاسم | Name |
| passwordHash | text | yes (system-managed) | — | never returned to a client | — | Password hash |
| lastLoginAt | date-time | no | — | — | آخر دخول | Last login |
| isActiveFl / createdBy / createdAt / updatedBy / updatedAt | security defaults | yes | — | — | — | — |

### ENT-FIN-013 — الدور والصلاحية / Role & Permission
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | no | search, create, read, update, deactivate (role), assign (permission, user) | none | plan §8 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| roleCode | text | yes | ACC-CFG-ADMIN / ACCOUNTANT / FIN-CONTROLLER / ACC-SYS-ADMIN / AUDITOR (§7.1) | unique | رمز الدور | Role code |
| roleNameAr / roleNameEn | text | yes | — | — | اسم الدور | Role name |
| permissionAssignments (repeating) | — | yes | — | §7.1 | الصلاحيات | Permissions |
| ↳ pageCode | reference→ SEC_PAGES row (this module's own copy, per POL-FIN-008 isolation) | yes (in the group) | one row per SCR-REQ (§7.1) | — | رمز الصفحة | Page code |
| ↳ actionCode | lookup→permission-action | yes (in the group) | VIEW / CREATE / UPDATE / DELETE | VIEW is the gateway (§7.1) | الإجراء | Action |
| userAssignments (repeating) | reference→ENT-FIN-012 | no | many users per role | — | المستخدمون | Assigned users |
| isActiveFl / createdBy / createdAt / updatedBy / updatedAt | security defaults | yes | — | — | — | — |

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-FIN-001 — Hierarchical chart of accounts with leaf-only posting
  Pattern    : ubiquitous
  Statement  : The system shall organize accounts in a hierarchical structure where only a leaf account may accept direct posting.
  Traces     : US-FIN-001
  Entities   : ENT-FIN-001
  Rationale  : Rollup accounts are for display/reporting only (plan §1.2).
  Source     : plan §1.2
  Priority   : HIGH

#### AC-FIN-001 — [REQ-FIN-001]
  Given  : a chart-of-accounts tree with a parent account "Assets" and a leaf child "Cash"
  When   : the Accounting Configuration Administrator marks "Cash" as accepting direct posting
  Then   : the system saves the flag and "Cash" becomes a valid posting target; "Assets" remains display/reporting-only (ar: "الحساب الأب مخصص للعرض فقط" · en: "Parent account is display-only")

### REQ-FIN-002 — Reject posting to a non-leaf account
  Pattern    : unwanted
  Statement  : If a journal entry line targets an account that does not accept direct posting, then the system shall reject the entry.
  Traces     : US-FIN-001
  Entities   : ENT-FIN-001, ENT-FIN-007
  Rationale  : Enforces the leaf-only posting rule at the point of entry (plan §1.2).
  Source     : plan §1.2
  Priority   : HIGH

#### AC-FIN-002 — [REQ-FIN-002]
  Given  : "Assets" is a rollup account with acceptsDirectPostingFl = false
  When   : a journal entry line is built against "Assets"
  Then   : the system rejects the entry with RULE-001's message (ar: "لا يمكن الترحيل إلى حساب غير قابل للترحيل المباشر" · en: "Cannot post to a non-postable account")

### REQ-FIN-003 — Account attributes
  Pattern    : ubiquitous
  Statement  : The system shall record, for every account, its type, its debit/credit nature, an active flag and whether it accepts direct posting.
  Traces     : US-FIN-001
  Entities   : ENT-FIN-001
  Rationale  : The attributes the chart of accounts must carry (plan §1.2).
  Source     : plan §1.2
  Priority   : HIGH

#### AC-FIN-003 — [REQ-FIN-003]
  Given  : the Accounting Configuration Administrator creates a new account
  When   : they save it with accountType = "asset", natureCode = "debit", acceptsDirectPostingFl = true
  Then   : the system persists all four attributes and displays them on the account's detail view

### REQ-FIN-004 — Dimensions defined and maintained as data
  Pattern    : ubiquitous
  Statement  : The system shall support one or more account dimensions that are defined and maintained as configuration data.
  Traces     : US-FIN-002
  Entities   : ENT-FIN-002
  Rationale  : POL-FIN-001 — no code change to add, remove or change a dimension (plan §0, §1.2).
  Source     : plan §0, §1.2; POL-FIN-001
  Priority   : HIGH

#### AC-FIN-004 — [REQ-FIN-004]
  Given  : no "PROJECT" dimension exists yet
  When   : the Accounting Configuration Administrator defines dimension key "PROJECT" with control type REFERENCE_ENTITY and adds three values
  Then   : "PROJECT" becomes immediately available as a segment choice on account combinations and rule lines, with no deployment step

### REQ-FIN-005 — Account combination = base account + dimension values
  Pattern    : ubiquitous
  Statement  : The system shall compose an account combination from a base account plus zero or more configured, active dimension values.
  Traces     : US-FIN-001, US-FIN-002
  Entities   : ENT-FIN-001, ENT-FIN-002, ENT-FIN-007
  Rationale  : Avoids duplicating the account per dimension value (plan §1.2).
  Source     : plan §1.2
  Priority   : HIGH

#### AC-FIN-005 — [REQ-FIN-005]
  Given  : account "Revenue - Rent" and an active "INVESTOR" dimension value "INV-007"
  When   : a journal entry line is built on that account with dimension value "INV-007"
  Then   : the line's combination is stored as base account + INV-007, without creating a separate "Revenue - Rent - INV-007" account

### REQ-FIN-006 — Single generic screen for all accounting reference data
  Pattern    : ubiquitous
  Statement  : The system shall manage every accounting reference list through one generic master-detail screen (list types in the master, values in the detail).
  Traces     : US-FIN-003
  Entities   : ENT-FIN-003
  Rationale  : POL-FIN-003 — no screen per list (plan §2.1, §2.3).
  Source     : plan §2.1, §2.3; POL-FIN-003
  Priority   : HIGH

#### AC-FIN-006 — [REQ-FIN-006]
  Given  : the generic Lookups screen
  When   : the Accounting Configuration Administrator selects lookup type "payment-methods" in the master panel
  Then   : the detail panel lists and lets them add/edit/deactivate its values, using the same screen used for every other lookup type

### REQ-FIN-007 — Reference data isolated from other modules
  Pattern    : ubiquitous
  Statement  : The system shall store all accounting reference data in tables owned exclusively by FIN.
  Traces     : US-FIN-003
  Entities   : ENT-FIN-003
  Rationale  : POL-FIN-003; total-isolation decision (A8 Decision 1) (plan §2.1).
  Source     : plan §2.1; POL-FIN-003
  Priority   : HIGH

#### AC-FIN-007 — [REQ-FIN-007]
  Given  : FIN's Lookups screen is in use
  When   : a lookup value is created
  Then   : it is written only to FIN's own `ENT-FIN-003` tables, never to the platform's shared `MDL` tables

### REQ-FIN-008 — One rule per event type, mapped to lines
  Pattern    : ubiquitous
  Statement  : The system shall map each accounting event type to exactly one rule composed of one or more lines.
  Traces     : US-FIN-004
  Entities   : ENT-FIN-004, ENT-FIN-005
  Rationale  : POL-FIN-002 (plan §3.1, §3.2).
  Source     : plan §3.1, §3.2; POL-FIN-002
  Priority   : HIGH

#### AC-FIN-008 — [REQ-FIN-008]
  Given  : event type "INVOICE_ISSUED" has no rule
  When   : the Accounting Configuration Administrator creates a rule for it with two lines
  Then   : the system links both lines to that one rule and rejects a second active rule for the same event type (RULE-012)

### REQ-FIN-009 — Rule line separates account derivation from amount source
  Pattern    : ubiquitous
  Statement  : The system shall keep a rule line's account-derivation logic and its amount-source logic as fully separate, independently configurable fields.
  Traces     : US-FIN-004
  Entities   : ENT-FIN-005
  Rationale  : Changing the account source never touches the amount logic, and vice versa (plan §3.2).
  Source     : plan §3.2
  Priority   : MEDIUM

#### AC-FIN-009 — [REQ-FIN-009]
  Given  : a rule line with accountDerivationType = EVENT_FIELD
  When   : the administrator changes only amountSourceOperation from DIRECT to PERCENTAGE
  Then   : the account-derivation configuration is unchanged and unaffected

### REQ-FIN-010 — Account derivation methods
  Pattern    : ubiquitous
  Statement  : The system shall derive a rule line's account segment from a constant value, a direct event field, or a mapping set of event attributes to a lookup segment value.
  Traces     : US-FIN-004
  Entities   : ENT-FIN-005
  Rationale  : plan §3.2 (a).
  Source     : plan §3.2
  Priority   : HIGH

#### AC-FIN-010 — [REQ-FIN-010]
  Given  : a rule line with accountDerivationType = MAPPING_SET and one mapping entry (eventAttributeName = "region", eventAttributeValue = "EAST" → resultingDimensionValue = "DIM-EAST")
  When   : an event with region = "EAST" is processed
  Then   : the segment resolves to dimension value "DIM-EAST"

### REQ-FIN-011 — Amount source
  Pattern    : ubiquitous
  Statement  : The system shall derive a rule line's amount from a specific event field, directly or through a percentage/remainder operation on that field.
  Traces     : US-FIN-004
  Entities   : ENT-FIN-005
  Rationale  : Never a written number (plan §3.2 (b)).
  Source     : plan §3.2
  Priority   : HIGH

#### AC-FIN-011 — [REQ-FIN-011]
  Given  : a rule line with amountSourceField = "grossAmount", amountSourceOperation = PERCENTAGE, amountOperationValue = 5
  When   : an event with grossAmount = 1000 is processed
  Then   : the line's amount resolves to 50

### REQ-FIN-012 — Distribution across compound-entry lines
  Pattern    : complex
  Statement  : When a rule distributes an amount across several lines, the system shall apply fixed lines first, then percentage lines from the remaining amount, then assign the true remainder to the single remainder line.
  Traces     : US-FIN-004
  Entities   : ENT-FIN-005
  Rationale  : Guarantees exact balance and absorbs rounding difference (plan §3.3); RULE-005.
  Source     : plan §3.3
  Priority   : HIGH

#### AC-FIN-012 — [REQ-FIN-012]
  Given  : a rule with a fixed line of 100, a percentage line of 30% and a remainder line, applied to an event amount of 1000
  When   : the entry is built
  Then   : the fixed line posts 100, the percentage line posts 270 (30% of the 900 remaining, rounded to the smallest currency unit), and the remainder line posts exactly 630 so debits equal credits

#### AC-FIN-013 — [REQ-FIN-012]
  Given  : a rounding difference of 0.01 remains after fixed and percentage lines
  When   : the remainder line is computed
  Then   : it absorbs the full 0.01 difference so the entry balances exactly (ar: "الفرق مرحّل بالكامل لسطر المتبقي" · en: "The difference is fully absorbed by the remainder line")

### REQ-FIN-013 — Adding an event type is a data change
  Pattern    : event
  Statement  : When a new event type is introduced, the system shall accept a new rule for it as configuration data, without a code change.
  Traces     : US-FIN-004
  Entities   : ENT-FIN-004
  Rationale  : Adapting to a new host system is a data change (plan §3.4).
  Source     : plan §3.4; POL-FIN-002
  Priority   : MEDIUM

#### AC-FIN-014 — [REQ-FIN-013]
  Given  : event type "REFUND_ISSUED" does not yet exist as a lookup value
  When   : the administrator adds it to the accounting-event-types lookup and configures a rule for it
  Then   : the system processes future "REFUND_ISSUED" events with that rule, with no deployment

### REQ-FIN-014 — Automatic posting from events
  Pattern    : event
  Statement  : When a canonical accounting event arrives, the system shall build a journal entry from it using the event type's rule.
  Traces     : US-FIN-005
  Entities   : ENT-FIN-004, ENT-FIN-005, ENT-FIN-006, ENT-FIN-007
  Rationale  : The primary journal source (plan §4.1).
  Source     : plan §4.1
  Priority   : HIGH

#### AC-FIN-015 — [REQ-FIN-014]
  Given  : event type "INVOICE_ISSUED" has an active, balanced rule
  When   : a canonical "INVOICE_ISSUED" event is received
  Then   : the system builds a journal entry with sourceTypeCode = Event-generated and sourceEventReference set from the event, then applies REQ-FIN-018

### REQ-FIN-015 — Direct manual entries
  Pattern    : ubiquitous
  Statement  : The system shall accept a manual journal entry, subject to the same automatic validation as any other entry.
  Traces     : US-FIN-006
  Entities   : ENT-FIN-006, ENT-FIN-007
  Rationale  : Adjustments and opening entries have no source event (plan §4.2).
  Source     : plan §4.2
  Priority   : MEDIUM

#### AC-FIN-016 — [REQ-FIN-015]
  Given  : the Accountant opens the manual entry form
  When   : they enter a balanced set of lines and submit
  Then   : the system runs the same validation as an event-generated entry (RULE-002, RULE-003, RULE-004) before posting

### REQ-FIN-016 — Recurring / reversing templates
  Pattern    : ubiquitous
  Statement  : The system shall generate journal entries automatically, on a defined schedule or as an auto-reversal in the next period, from a template defined once as data.
  Traces     : US-FIN-007
  Entities   : ENT-FIN-008, ENT-FIN-006
  Rationale  : Routine or accrual entries don't need rebuilding every period (plan §4.3).
  Source     : plan §4.3
  Priority   : MEDIUM

#### AC-FIN-017 — [REQ-FIN-016]
  Given  : a RECURRING template scheduled monthly with two lines
  When   : nextRunDate is reached
  Then   : the system generates a journal entry with sourceTypeCode = Recurring-Reversing, links templateId, and advances nextRunDate to the following month

### REQ-FIN-017 — Allocation entries
  Pattern    : ubiquitous
  Statement  : The system shall distribute an accumulated account balance across several target accounts or dimensions according to a data-defined allocation rule.
  Traces     : US-FIN-008
  Entities   : ENT-FIN-009, ENT-FIN-006
  Rationale  : Apportions shared costs/revenues consistently (plan §4.4).
  Source     : plan §4.4
  Priority   : MEDIUM

#### AC-FIN-018 — [REQ-FIN-017]
  Given  : an allocation rule distributing the "Shared Overhead" account balance across three departments by percentage, with one remainder line
  When   : the Accountant runs the allocation
  Then   : the system generates a balanced journal entry with sourceTypeCode = Allocation, following RULE-014's distribution order

### REQ-FIN-018 — Direct posting after automatic validation, no per-entry approval
  Pattern    : event
  Statement  : When a journal entry from any source passes automatic validation, the system shall post it directly with no per-entry human approval.
  Traces     : US-FIN-009
  Entities   : ENT-FIN-006, ENT-FIN-007
  Rationale  : POL-FIN-004 (plan §5.1, §5.2).
  Source     : plan §5.1, §5.2; POL-FIN-004
  Priority   : HIGH

#### AC-FIN-019 — [REQ-FIN-018]
  Given  : a balanced draft entry on leaf, active accounts, valid dimensions, in an Open period
  When   : validation runs
  Then   : the system sets statusCode = POSTED immediately, with no approval step, and the entry affects balances from that instant

#### AC-FIN-020 — [REQ-FIN-018]
  Given  : an event-generated entry that fails validation
  When   : validation runs
  Then   : the system keeps the entry in DRAFT and does not post it (see REQ-FIN-020)

### REQ-FIN-019 — Reject an invalid entry with reasons
  Pattern    : unwanted
  Statement  : If a journal entry fails automatic validation, then the system shall keep it in DRAFT and report every failed check.
  Traces     : US-FIN-009
  Entities   : ENT-FIN-006, ENT-FIN-007
  Rationale  : Database errors never reach users unexplained; every failing constraint carries a RULE message (SRS §5).
  Source     : plan §5.1; RULE-001…RULE-004
  Priority   : HIGH

#### AC-FIN-021 — [REQ-FIN-019]
  Given  : an entry where debits (500) ≠ credits (480)
  When   : validation runs
  Then   : the system rejects posting and returns RULE-002's message (ar: "مجموع المدين لا يساوي مجموع الدائن" · en: "Debit total does not equal credit total")

### REQ-FIN-020 — Automatic posting requires no per-entry approval (event-generated path)
  Pattern    : ubiquitous
  Statement  : The system shall never present a per-entry approval step to any user, for any journal entry source.
  Traces     : US-FIN-009, US-FIN-005
  Entities   : ENT-FIN-006
  Rationale  : POL-FIN-004; the sole human control point is period close, not the entry (plan §5.2).
  Source     : plan §5.2; POL-FIN-004
  Priority   : HIGH

#### AC-FIN-022 — [REQ-FIN-020]
  Given  : any of the four journal sources
  When   : an entry from that source passes validation
  Then   : the system posts it without ever routing it to a human approval queue

### REQ-FIN-021 — Human approval required to close a period
  Pattern    : ubiquitous
  Statement  : The system shall require a human approval before a fiscal period can be soft-closed or hard-closed.
  Traces     : US-FIN-010
  Entities   : ENT-FIN-011
  Rationale  : POL-FIN-005 — the platform's one human control point (plan §5.2, §7.3).
  Source     : plan §5.2, §7.3; POL-FIN-005
  Priority   : HIGH

#### AC-FIN-023 — [REQ-FIN-021]
  Given  : an Open period with posted entries
  When   : the Financial Controller reviews and approves its close
  Then   : the system records closeApprovedBy, closeApprovedAt and transitions the period per A7

### REQ-FIN-022 — Segregation of duties at period close
  Pattern    : unwanted
  Statement  : If the user attempting to approve a period's close created any journal entry posted within that period, then the system shall prevent that user from approving the close.
  Traces     : US-FIN-010
  Entities   : ENT-FIN-011, ENT-FIN-006, ENT-FIN-012
  Rationale  : POL-FIN-006 — SoD enforced via RBAC (plan §5.2, §8.2).
  Source     : plan §5.2, §8.2; POL-FIN-006
  Priority   : HIGH

#### AC-FIN-024 — [REQ-FIN-022]
  Given  : Accountant "Sara" created 3 entries in period "2026-08"
  When   : "Sara" attempts to approve the close of period "2026-08"
  Then   : the system blocks the approval with RULE-008's message (ar: "لا يمكن لمنشئ القيد اعتماد إقفال الفترة" · en: "The entry's creator cannot approve the period close")

### REQ-FIN-023 — Reverse a posted entry
  Pattern    : event
  Statement  : When a user reverses a posted entry, the system shall create a new, linked VOID/CORRECTION entry that zeroes its effect, posted directly after automatic validation.
  Traces     : US-FIN-011
  Entities   : ENT-FIN-006, ENT-FIN-007
  Rationale  : POL-FIN-007 — never edit or delete a posted entry (plan §6.1, §6.2).
  Source     : plan §6.1, §6.2; POL-FIN-007
  Priority   : HIGH

#### AC-FIN-025 — [REQ-FIN-023]
  Given  : a POSTED entry "JE-000102"
  When   : the Accountant chooses "Reverse" on it
  Then   : the system creates a new entry with sourceTypeCode = Void-Correction, reversalOfEntryId = "JE-000102", mirrored debit/credit lines, posts it directly, and sets "JE-000102".reversedByEntryId to the new entry's id

### REQ-FIN-024 — Reversal in a closed original period posts to the current open period
  Pattern    : unwanted
  Statement  : If the original entry's period is closed, then the system shall post its reversal in the current open period instead.
  Traces     : US-FIN-011
  Entities   : ENT-FIN-006
  Rationale  : plan §6.2.
  Source     : plan §6.2
  Priority   : MEDIUM

#### AC-FIN-026 — [REQ-FIN-024]
  Given  : "JE-000102" belongs to Hard-Closed period "2026-07"
  When   : it is reversed
  Then   : the system posts the reversal in the currently Open period, not "2026-07"

### REQ-FIN-025 — Independent accounting-only login, users, roles and permissions
  Pattern    : ubiquitous
  Statement  : The system shall authenticate and authorize FIN users through a role-based security model fully independent of any other module.
  Traces     : US-FIN-012
  Entities   : ENT-FIN-012, ENT-FIN-013
  Rationale  : POL-FIN-008 (plan §8.1, §8.2).
  Source     : plan §8.1, §8.2; POL-FIN-008
  Priority   : HIGH

#### AC-FIN-027 — [REQ-FIN-025]
  Given  : a FIN user with no account in any other module
  When   : they log in to FIN
  Then   : the system authenticates them using only FIN's own ENT-FIN-012/013 tables

### REQ-FIN-026 — Screen/action permissions with SoD-capable role assignment
  Pattern    : ubiquitous
  Statement  : The system shall assign permissions per screen and action to roles, and shall support assigning the entry-creator and period-close-approver roles to different users.
  Traces     : US-FIN-012, US-FIN-010
  Entities   : ENT-FIN-013
  Rationale  : plan §8.2; enables POL-FIN-006 to be enforced (RULE-008).
  Source     : plan §8.2; POL-FIN-008
  Priority   : HIGH

#### AC-FIN-028 — [REQ-FIN-026]
  Given  : roles ACCOUNTANT and FIN-CONTROLLER
  When   : the Accounting System Administrator assigns "Sara" to ACCOUNTANT only and "Omar" to FIN-CONTROLLER only
  Then   : the system enforces that "Sara" cannot hold period-close-approve permission and "Omar" cannot hold journal-entry-create permission unless separately, deliberately assigned

### REQ-FIN-027 — Fiscal period/year states
  Pattern    : ubiquitous
  Statement  : The system shall support fiscal year states Open and Year-End Closed, and fiscal period states Open, Soft Close and Hard Close.
  Traces     : US-FIN-013
  Entities   : ENT-FIN-010, ENT-FIN-011
  Rationale  : plan §7.1, §7.2.
  Source     : plan §7.1, §7.2
  Priority   : HIGH

#### AC-FIN-029 — [REQ-FIN-027]
  Given  : fiscal year "2026" with periods "2026-01" … "2026-12"
  When   : the Financial Controller views the fiscal periods screen
  Then   : each period shows its current state per A7 and the year shows Open

### REQ-FIN-028 — Posting blocked outside Open state
  Pattern    : state
  Statement  : While a fiscal period is not Open, the system shall block normal posting to it.
  Traces     : US-FIN-013
  Entities   : ENT-FIN-011, ENT-FIN-006
  Rationale  : Soft Close blocks normal posting while allowing authorized review/adjustment; Hard Close blocks all posting (plan §7.2).
  Source     : plan §7.2
  Priority   : HIGH

#### AC-FIN-030 — [REQ-FIN-028]
  Given  : period "2026-07" is Soft Closed
  When   : a normal (non-adjustment) entry targets it
  Then   : the system rejects it with RULE-004's message (ar: "الفترة غير مفتوحة للترحيل" · en: "Period is not open for posting")

### REQ-FIN-029 — Hard Close is permanent
  Pattern    : unwanted
  Statement  : If a period is Hard Closed, then the system shall never allow posting to it again and shall not permit it to be re-opened.
  Traces     : US-FIN-013
  Entities   : ENT-FIN-011
  Rationale  : plan §7.2 ("Hard Close: no posting after it ever; not re-openable").
  Source     : plan §7.2
  Priority   : HIGH

#### AC-FIN-031 — [REQ-FIN-029]
  Given  : period "2026-06" is Hard Closed
  When   : any user, including an administrator, attempts to reopen it or post to it
  Then   : the system refuses the action unconditionally (RULE-009)

### REQ-FIN-030 — Automatic year-end carryforward
  Pattern    : event
  Statement  : When a fiscal year is closed, the system shall automatically generate the new year's opening journal entry from the prior year's closing balances.
  Traces     : US-FIN-014
  Entities   : ENT-FIN-006, ENT-FIN-010
  Rationale  : POL-FIN-010; no manual re-entry (plan §7.4).
  Source     : plan §7.4; POL-FIN-010
  Priority   : MEDIUM

#### AC-FIN-032 — [REQ-FIN-030]
  Given  : fiscal year "2026" with all periods Hard Closed (ADR-FIN-003) and balance-sheet closing balances computed
  When   : the Financial Controller performs year-end close
  Then   : the system generates and posts the "2027" opening entry carrying forward every balance-sheet account's closing balance, and sets year "2026" to Year-End Closed

### REQ-FIN-031 — Result accounts close to Retained Earnings
  Pattern    : event
  Statement  : When a fiscal year is closed, the system shall close the net of every revenue and expense account to the designated Retained Earnings account, and the new year shall start those accounts from zero.
  Traces     : US-FIN-014
  Entities   : ENT-FIN-001, ENT-FIN-006, ENT-FIN-010
  Rationale  : plan §7.4.
  Source     : plan §7.4; POL-FIN-010
  Priority   : MEDIUM

#### AC-FIN-033 — [REQ-FIN-031]
  Given  : revenue and expense accounts with a combined net credit balance of 50,000 at year-end
  When   : year-end close runs
  Then   : the system posts a closing entry crediting 50,000 to the single account flagged isRetainedEarningsAccountFl = true (RULE-011), and every revenue/expense account opens "2027" at zero

### REQ-FIN-032 — Reporting derived from posted entries only
  Pattern    : ubiquitous
  Statement  : The system shall derive the account ledger, trial balance, balance sheet and income statement solely from POSTED journal entries.
  Traces     : US-FIN-015
  Entities   : ENT-FIN-001, ENT-FIN-006, ENT-FIN-007
  Rationale  : POL-FIN-009 — no manually accumulated balance column (plan §9.1, §9.2).
  Source     : plan §9.1, §9.2; POL-FIN-009
  Priority   : HIGH

#### AC-FIN-034 — [REQ-FIN-032]
  Given  : one DRAFT entry and three POSTED entries on account "Cash"
  When   : the trial balance is generated
  Then   : it reflects only the three POSTED entries; the DRAFT entry contributes nothing

### REQ-FIN-033 — Dimension-based reporting without account duplication
  Pattern    : ubiquitous
  Statement  : The system shall produce a statement filtered or grouped by any configured, active dimension value, without duplicating accounts per value.
  Traces     : US-FIN-016
  Entities   : ENT-FIN-001, ENT-FIN-002, ENT-FIN-007
  Rationale  : plan §9.2.
  Source     : plan §9.2
  Priority   : MEDIUM

#### AC-FIN-035 — [REQ-FIN-033]
  Given  : posted lines on "Revenue - Rent" carrying dimension values "INV-007" and "INV-011"
  When   : the Financial Controller requests a statement for "INV-007"
  Then   : the system shows only "INV-007"'s share of "Revenue - Rent", using the same account, not a duplicate

### REQ-FIN-034 — Drill-down audit trail
  Pattern    : ubiquitous
  Statement  : The system shall let a user navigate from any financial-statement line to its trial balance figure, to its account-ledger entries, to the originating journal entry, and to that entry's source-event reference.
  Traces     : US-FIN-017
  Entities   : ENT-FIN-001, ENT-FIN-006, ENT-FIN-007
  Rationale  : Standard audit element (plan §9.3).
  Source     : plan §9.3
  Priority   : MEDIUM

#### AC-FIN-036 — [REQ-FIN-034]
  Given  : an Income Statement line for "Revenue - Rent" showing 1,200
  When   : the Auditor drills down through trial balance → account ledger → the originating entry
  Then   : the system shows entry "JE-000045" and, since it was event-generated, its sourceEventReference

#### AC-FIN-037 — [REQ-FIN-034]
  Given  : the same drill-down chain reaches a manually-entered journal entry
  When   : the Auditor inspects it
  Then   : the system shows no sourceEventReference field populated (ar: "قيد يدوي — لا يوجد مرجع حدث" · en: "Manual entry — no source event reference") and the chain still resolves fully to that entry

## A5 — Business rules

### RULE-FIN-001 — Leaf/active posting only
  Scope      : ENT-FIN-001, ENT-FIN-007
  Trigger    : on post
  Statement  : The system shall prevent posting to an account when it is inactive or does not accept direct posting.
  Message    : ar: لا يمكن الترحيل إلى حساب غير نشط أو غير قابل للترحيل المباشر · en: Cannot post to an inactive or non-postable account
  Traces     : REQ-FIN-002, REQ-FIN-018
  Source     : plan §1.2
  Test-Hint  : cover both "inactive" and "rollup" rejection paths

### RULE-FIN-002 — Debits equal credits
  Scope      : ENT-FIN-006, ENT-FIN-007
  Trigger    : on post
  Statement  : The system shall prevent posting an entry whose debit lines do not sum to the same total as its credit lines.
  Message    : ar: مجموع المدين لا يساوي مجموع الدائن · en: Debit total does not equal credit total
  Traces     : REQ-FIN-019, REQ-FIN-018
  Source     : plan §5.1

### RULE-FIN-003 — Dimension value must belong to its dimension and be active
  Scope      : ENT-FIN-002, ENT-FIN-007
  Trigger    : on post
  Statement  : The system shall prevent posting a line whose dimension value is inactive or does not belong to the dimension configured for that segment.
  Message    : ar: قيمة البُعد غير صالحة أو غير نشطة · en: Dimension value is invalid or inactive
  Traces     : REQ-FIN-005, REQ-FIN-018
  Source     : plan §1.2, §5.1

### RULE-FIN-004 — Period must be Open for posting
  Scope      : ENT-FIN-011, ENT-FIN-006
  Trigger    : on post
  Statement  : The system shall prevent posting a normal entry to a period that is not Open.
  Message    : ar: الفترة غير مفتوحة للترحيل · en: Period is not open for posting
  Traces     : REQ-FIN-018, REQ-FIN-028
  Source     : plan §5.1, §7.2

### RULE-FIN-005 — Distribution order: fixed → percentage → remainder
  Scope      : ENT-FIN-005, ENT-FIN-009
  Trigger    : on entry build / allocation run
  Statement  : The system shall apply fixed-amount lines first, then percentage lines against the remaining amount rounded to the smallest currency unit, then assign the exact difference to the single remainder line.
  Message    : ar: يجب وجود سطر متبقي واحد فقط لاستيعاب فرق التقريب · en: Exactly one remainder line is required to absorb the rounding difference
  Traces     : REQ-FIN-012
  Source     : plan §3.3

### RULE-FIN-006 — Posted entry is immutable
  Scope      : ENT-FIN-006, ENT-FIN-007
  Trigger    : on edit / delete attempt
  Statement  : The system shall prevent any edit or delete on an entry once its statusCode is POSTED.
  Message    : ar: القيد المرحّل مقفل ولا يمكن تعديله أو حذفه · en: A posted entry is locked and cannot be edited or deleted
  Traces     : REQ-FIN-018, REQ-FIN-023
  Source     : plan §5.3, §6.1

### RULE-FIN-007 — Reversal must reference its original entry
  Scope      : ENT-FIN-006
  Trigger    : on reversal creation
  Statement  : The system shall require every Void/Correction entry to carry a reversalOfEntryId pointing to the entry it corrects.
  Message    : ar: يجب ربط قيد العكس بالقيد الأصلي · en: A reversing entry must reference the original entry
  Traces     : REQ-FIN-023
  Source     : plan §6.2

### RULE-FIN-008 — SoD: entry creator ≠ period-close approver
  Scope      : ENT-FIN-011, ENT-FIN-006, ENT-FIN-012
  Trigger    : on period-close approval
  Statement  : The system shall prevent a user from approving a period's close if that user created any entry posted within the period.
  Message    : ar: لا يمكن لمنشئ القيد اعتماد إقفال الفترة · en: The entry's creator cannot approve the period close
  Traces     : REQ-FIN-022
  Source     : plan §5.2, §8.2

### RULE-FIN-009 — Hard-closed period never reopens
  Scope      : ENT-FIN-011
  Trigger    : on reopen / post attempt against a Hard Closed period
  Statement  : The system shall permanently refuse any reopen or posting attempt against a Hard Closed period.
  Message    : ar: الفترة مقفلة إقفالاً نهائياً · en: Period is permanently closed
  Traces     : REQ-FIN-029
  Source     : plan §7.2

### RULE-FIN-010 — Year-end close requires every period of the year Hard Closed
  Scope      : ENT-FIN-010, ENT-FIN-011
  Trigger    : on year-end close attempt
  Statement  : The system shall prevent year-end close of a fiscal year until every one of its periods is Hard Closed.
  Message    : ar: يجب إقفال جميع فترات السنة إقفالاً نهائياً أولاً · en: All periods of the year must be Hard Closed first
  Traces     : REQ-FIN-030
  Source     : ADR-FIN-003 (domain best practice — plan does not state the exact gating condition)

### RULE-FIN-011 — Exactly one active Retained Earnings account
  Scope      : ENT-FIN-001
  Trigger    : on account save / year-end close
  Statement  : The system shall require exactly one active account flagged isRetainedEarningsAccountFl at year-end close time.
  Message    : ar: يجب تحديد حساب واحد فقط للأرباح المحتجزة · en: Exactly one Retained Earnings account must be designated
  Traces     : REQ-FIN-003, REQ-FIN-031
  Source     : plan §7.4

### RULE-FIN-012 — Exactly one active rule per event type
  Scope      : ENT-FIN-004
  Trigger    : on rule save
  Statement  : The system shall prevent activating a second rule for an event type that already has an active rule.
  Message    : ar: يوجد بالفعل قاعدة نشطة لهذا النوع من الأحداث · en: An active rule already exists for this event type
  Traces     : REQ-FIN-008
  Source     : plan §3.1

### RULE-FIN-013 — Recurring template skipped on invalid target at run time
  Scope      : ENT-FIN-008, ENT-FIN-001
  Trigger    : on scheduled run
  Statement  : The system shall skip generating an entry from a template whose target account is inactive at run time, and shall flag it for review.
  Message    : ar: تم تخطي القالب — الحساب غير نشط · en: Template skipped — account is inactive
  Traces     : REQ-FIN-016
  Source     : domain best practice (protects RULE-001 at scheduled-run time)

### RULE-FIN-014 — Allocation lines must total the source balance
  Scope      : ENT-FIN-009
  Trigger    : on allocation run
  Statement  : The system shall require an allocation rule's lines, applying the same fixed→percentage→remainder order as RULE-005, to total exactly the source balance being distributed.
  Message    : ar: يجب أن يساوي مجموع سطور التوزيع رصيد المصدر بالكامل · en: Allocation lines must total exactly the source balance
  Traces     : REQ-FIN-017
  Source     : plan §3.3 (referenced by §4.4), §4.4

## A6 — Lookups

| Key | Used by field(s) | ENT | Control type | Owner | Values | Source |
|---|---|---|---|---|---|---|
| payment-methods | (reserved for future journal-source use) | ENT-FIN-003 | lookup | this module | none named yet — configured post-delivery | plan §2.2, §2.3 |
| accounting-event-types | ENT-FIN-004.eventTypeCode, ENT-FIN-005.mappingEntries.eventAttributeName | ENT-FIN-003 | lookup | this module | none named yet — configured post-delivery | plan §2.2, §3.4 |
| account-types | ENT-FIN-001.accountType | ENT-FIN-003 | lookup | this module | asset, liability, equity, revenue, expense | plan §1.2, §2.2; business-policies-fin.md |
| period-states | ENT-FIN-011.statusCode | ENT-FIN-003 | lookup | this module | Open, Soft Close, Hard Close | plan §7.2, §2.2; business-policies-fin.md |
| journal-types | ENT-FIN-006.sourceTypeCode | ENT-FIN-003 | lookup | this module | Event-generated, Manual, Recurring/Reversing, Allocation, Void/Correction | plan §4, §6.2, §2.2 |
| account-nature | ENT-FIN-001.natureCode | fixed (not a growing ENT-FIN-003 lookup — DEFAULT, see A3) | fixed 2-value list | this module | debit, credit | plan §1.2 |
| dimension-control-type | ENT-FIN-002.controlType | fixed | fixed 2-value list | this module | FIXED_LIST, REFERENCE_ENTITY | SRS §3.3 rule |
| account-derivation-type | ENT-FIN-005.accountDerivationType | fixed | fixed 3-value list | this module | CONSTANT, EVENT_FIELD, MAPPING_SET | plan §3.2 |
| amount-source-operation | ENT-FIN-005.amountSourceOperation | fixed | fixed 3-value list | this module | DIRECT, PERCENTAGE, REMAINDER | plan §3.2 |
| debit-credit | ENT-FIN-005.directionCode, ENT-FIN-007.directionCode, ENT-FIN-008 lines.directionCode | fixed | fixed 2-value list | this module | DEBIT, CREDIT | plan §3.2 |
| distribution-type | ENT-FIN-005.distributionType, ENT-FIN-009 lines.distributionType | fixed | fixed 3-value list | this module | FIXED, PERCENTAGE, REMAINDER | plan §3.3 |
| template-type | ENT-FIN-008.templateTypeCode | fixed | fixed 2-value list | this module | RECURRING, REVERSING | plan §4.3 |
| journal-entry-status | ENT-FIN-006.statusCode | fixed | fixed 2-value list | this module | DRAFT, POSTED | plan §5.1 |
| fiscal-year-status | ENT-FIN-010.statusCode | fixed | fixed 2-value list | this module | OPEN, YEAR_END_CLOSED | plan §7.2 |
| permission-action | ENT-FIN-013.permissionAssignments.actionCode | fixed | fixed 4-value list | this module | VIEW, CREATE, UPDATE, DELETE | domain-profile §5 (security_model) |

The five module-registered keys (`payment-methods`, `accounting-event-types`,
`account-types`, `period-states`, `journal-types`) are managed through the
generic Lookups screen (SCR-REQ-FIN-003, ENT-FIN-003) per POL-FIN-003. The
remaining keys above are small, closed, structural vocabularies intrinsic to
this SRS's own design (not client-configurable reference data) and are fixed
value sets, not ENT-FIN-003 rows.

## A7 — Status lifecycle

**Journal Entry (`ENT-FIN-006.statusCode`)**
```
DRAFT --(automatic validation passes, RULE-001..004)--> POSTED
```
POSTED is terminal — no further transition on the same entry (RULE-006).
A correction is always a new entry (REQ-FIN-023), never a transition back to DRAFT.

**Fiscal Period (`ENT-FIN-011.statusCode`)**
```
Open <--(re-open, human decision, only from Soft Close)-- Soft Close
Open --(human approval, RULE-008)--> Soft Close
Soft Close --(human approval, RULE-008)--> Hard Close
Hard Close --(terminal — RULE-009, no transition out)
```
Soft Close blocks normal posting but allows authorized review/adjustment and is
re-openable; Hard Close blocks all posting forever and is not re-openable
(plan §7.2).

**Fiscal Year (`ENT-FIN-010.statusCode`)**
```
OPEN --(year-end close, requires all periods Hard Closed — RULE-010)--> YEAR_END_CLOSED
```
YEAR_END_CLOSED is terminal.

## A8 — Module dependencies

| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate |
|---|---|---|---|---|
| none | — | — | — | — |

FIN consumes no entity from any other module and exposes none for consumption —
confirmed total isolation (`DEPENDENCIES: NONE`, `ROOT: YES`,
module-registry-fin.md; prd-approval gate, approved 2026-09-10). This is a
deliberate deviation from the platform default in which every business module
reads `ORG`/`SEC`/`MDL` (domain-profile §6, project-registry XM-CAND-007) —
recorded, not silently applied (STANDALONE §Decisions applied, Decision 1).

| External service | Purpose | Integration kind |
|---|---|---|
| Event consumer (out of scope) | Delivers the canonical accounting event that triggers REQ-FIN-014 | inbound event, not a platform module dependency (plan §0) |

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-FIN-001 — شجرة الحسابات / Chart of Accounts
### B1 — Definition
  Purpose      : Maintain the hierarchical chart of accounts.
  Entities     : ENT-FIN-001
  Operations   : search, list, create, read, update, deactivate
  Users        : Accounting Configuration Administrator
  Navigation   : FIN → Setup → Chart of Accounts; from: FIN home; to: SCR-REQ-FIN-002 (dimension values referenced on an account combination)
  Content shape: true hierarchy (parent/child)
  Traces       : REQ-FIN-001, REQ-FIN-002, REQ-FIN-003
### B2 — Search / list
  Filters: code, name (ar/en), accountType (lookup account-types), isActiveFl. Result columns match the filters plus natureCode, acceptsDirectPostingFl, rendered as a tree.
### B3 — Input
  Fields: code, nameAr, nameEn, parentAccountId (tree picker), accountType (lookup), natureCode (lookup), acceptsDirectPostingFl, isRetainedEarningsAccountFl. Save applies RULE-011 (single active Retained-Earnings account) and RULE-001 (leaf-only posting flag consistency).
### B4 — Access
  Page code SEC_PAGES.FIN_COA. Accounting Configuration Administrator: VIEW, CREATE, UPDATE, DELETE. Accountant, Financial Controller, Auditor: VIEW.
### B5 — API expectations
  create/search/update/deactivate/read account, scoped to ENT-FIN-001, per §8 table; RULEs RULE-001, RULE-011; Traces REQ-FIN-001…003.

## SCR-REQ-FIN-002 — تعريف الأبعاد وقيمها / Dimension Definition & Values
### B1 — Definition
  Purpose      : Define account dimensions and manage their values.
  Entities     : ENT-FIN-002
  Operations   : search, list, create, read, update, deactivate (definition and values)
  Users        : Accounting Configuration Administrator
  Navigation   : FIN → Setup → Dimensions; from: FIN home; to: SCR-REQ-FIN-001 (dimension used on accounts)
  Content shape: master + detail (definitions in master, values in detail)
  Traces       : REQ-FIN-004, REQ-FIN-005
### B2 — Search / list
  Filters: dimensionKey, name (ar/en), isActiveFl on the master; valueCode, name (ar/en), isActiveFl on the detail. Result columns mirror the filters.
### B3 — Input
  Master fields: dimensionKey, nameAr, nameEn, controlType (lookup). Detail fields (per selected dimension): valueCode, valueNameAr, valueNameEn, sortOrder, isActiveFl.
### B4 — Access
  Page code SEC_PAGES.FIN_DIM. Accounting Configuration Administrator: VIEW, CREATE, UPDATE, DELETE. All other FIN roles: VIEW.
### B5 — API expectations
  create/search/update/deactivate/read on both definition and value, scoped to ENT-FIN-002; Traces REQ-FIN-004, REQ-FIN-005.

## SCR-REQ-FIN-003 — البيانات المرجعية المحاسبية / Accounting Reference Lists (Lookups)
### B1 — Definition
  Purpose      : Manage every accounting lookup type and its values in one generic screen.
  Entities     : ENT-FIN-003
  Operations   : search, list, create, read, update, deactivate (type and values)
  Users        : Accounting Configuration Administrator
  Navigation   : FIN → Setup → Lookups; from: FIN home; to: none (terminal setup screen)
  Content shape: master + detail (list types in master, values in detail)
  Traces       : REQ-FIN-006, REQ-FIN-007
### B2 — Search / list
  Filters: lookupKey, name (ar/en) on the master; valueCode, label (ar/en), isActiveFl on the detail. Result columns mirror the filters.
### B3 — Input
  Master fields: lookupKey, nameAr, nameEn. Detail fields: valueCode, labelAr, labelEn, sortOrder, isActiveFl.
### B4 — Access
  Page code SEC_PAGES.FIN_LKP. Accounting Configuration Administrator: VIEW, CREATE, UPDATE, DELETE. All other FIN roles: VIEW.
### B5 — API expectations
  create/search/update/deactivate/read on both type and value, scoped to ENT-FIN-003; Traces REQ-FIN-006, REQ-FIN-007.

## SCR-REQ-FIN-004 — قواعد المحرك / Engine Rules
### B1 — Definition
  Purpose      : Configure, per event type, how it becomes a journal entry.
  Entities     : ENT-FIN-004, ENT-FIN-005
  Operations   : search, list, create, read, update, deactivate (rule and its lines)
  Users        : Accounting Configuration Administrator
  Navigation   : FIN → Setup → Engine Rules; from: FIN home; to: SCR-REQ-FIN-001 (constant account picker), SCR-REQ-FIN-002 (mapping-set target values)
  Content shape: master + detail (rule in master, lines in detail)
  Traces       : REQ-FIN-008, REQ-FIN-009, REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013
### B2 — Search / list
  Filters: eventTypeCode, isActiveFl on the master. Result columns: eventTypeCode, name, line count, isActiveFl.
### B3 — Input
  Master fields: eventTypeCode, nameAr, nameEn. Line fields: lineNo, accountDerivationType, (constantAccountId | eventFieldName | mappingEntries), amountSourceField, amountSourceOperation, amountOperationValue, directionCode, distributionType, distributionValue. Save applies RULE-005 (distribution order) and RULE-012 (one active rule per event type).
### B4 — Access
  Page code SEC_PAGES.FIN_RULE. Accounting Configuration Administrator: VIEW, CREATE, UPDATE, DELETE. Accountant, Financial Controller, Auditor: VIEW.
### B5 — API expectations
  create/search/update/deactivate/read rule and its lines, scoped to ENT-FIN-004/005; RULEs RULE-005, RULE-012; Traces REQ-FIN-008…013.

## SCR-REQ-FIN-005 — قوالب القيود المتكررة والعكسية / Recurring / Reversing Templates
### B1 — Definition
  Purpose      : Define templates that generate entries on a schedule or auto-reverse.
  Entities     : ENT-FIN-008
  Operations   : search, list, create, read, update, deactivate
  Users        : Accountant
  Navigation   : FIN → Operations → Recurring Templates; from: FIN home; to: SCR-REQ-FIN-007 (generated entries)
  Content shape: header + repeating lines with totals
  Traces       : REQ-FIN-016
### B2 — Search / list
  Filters: templateNameAr/En, templateTypeCode, isActiveFl. Result columns: name, type, nextRunDate, isActiveFl.
### B3 — Input
  Header fields: templateNameAr, templateNameEn, templateTypeCode, scheduleRule. Line fields: accountId, dimensionValues, amountSource, directionCode. Save applies RULE-001 (leaf/active account) and RULE-002 (balance) at generation time.
### B4 — Access
  Page code SEC_PAGES.FIN_TMPL. Accountant: VIEW, CREATE, UPDATE, DELETE. Financial Controller, Auditor: VIEW.
### B5 — API expectations
  create/search/update/deactivate/read template; RULEs RULE-001, RULE-002, RULE-013; Traces REQ-FIN-016.

## SCR-REQ-FIN-006 — قواعد التوزيع / Allocation Rules
### B1 — Definition
  Purpose      : Define rules that distribute an accumulated balance across targets.
  Entities     : ENT-FIN-009
  Operations   : search, list, create, read, update, deactivate, run (action)
  Users        : Accountant
  Navigation   : FIN → Operations → Allocation Rules; from: FIN home; to: SCR-REQ-FIN-007 (generated entries)
  Content shape: header + repeating lines with totals
  Traces       : REQ-FIN-017
### B2 — Search / list
  Filters: ruleNameAr/En, sourceAccountId, isActiveFl. Result columns: name, source account, line count, isActiveFl.
### B3 — Input
  Header fields: ruleNameAr, ruleNameEn, sourceAccountId, sourceDimensionValues. Line fields: targetAccountId, targetDimensionValues, distributionType, distributionValue. Save/run applies RULE-014 (distribution order and total).
### B4 — Access
  Page code SEC_PAGES.FIN_ALLOC. Accountant: VIEW, CREATE, UPDATE, DELETE. Financial Controller, Auditor: VIEW.
### B5 — API expectations
  create/search/update/deactivate/read rule; run (action); RULE-014; Traces REQ-FIN-017.

## SCR-REQ-FIN-007 — القيود المحاسبية / Journal Entries
### B1 — Definition
  Purpose      : View all journal entries and create/reverse manual entries.
  Entities     : ENT-FIN-006, ENT-FIN-007
  Operations   : search, list, create (manual), read, reverse (action)
  Users        : Accountant (create, reverse, view), Financial Controller (view), Auditor (view)
  Navigation   : FIN → Operations → Journal Entries; from: FIN home, SCR-REQ-FIN-005, SCR-REQ-FIN-006 (generated-entry links); to: SCR-REQ-FIN-009 (account ledger drill-down)
  Content shape: header + repeating lines with totals
  Traces       : REQ-FIN-014, REQ-FIN-015, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-023, REQ-FIN-024
### B2 — Search / list
  Filters: entryNo, entryDate range, sourceTypeCode, statusCode, periodId, accountId. Result columns mirror the filters plus fiscalYearId.
### B3 — Input
  Header fields (manual create only): entryDate, periodId. Line fields: accountId, dimensionValues, directionCode, amount, descriptionAr/En. "Reverse" action: no input beyond confirmation; the system builds the linked entry per REQ-FIN-023. Save applies RULE-001, RULE-002, RULE-003, RULE-004, RULE-006, RULE-007.
### B4 — Access
  Page code SEC_PAGES.FIN_JE. Accountant: VIEW, CREATE, UPDATE (draft only, blocked by RULE-006 once posted). Financial Controller, Auditor: VIEW.
### B5 — API expectations
  create (manual), search, read, reverse (action) journal entry; RULEs RULE-001…004, RULE-006, RULE-007; Traces REQ-FIN-014, 015, 018, 019, 020, 023, 024.

## SCR-REQ-FIN-008 — الفترات والسنوات المالية / Fiscal Periods & Years
### B1 — Definition
  Purpose      : Manage fiscal years/periods and approve period/year close.
  Entities     : ENT-FIN-010, ENT-FIN-011
  Operations   : search, list, create, read, update (state transitions), approve-close (action), year-end-close (action)
  Users        : Financial Controller
  Navigation   : FIN → Control → Fiscal Periods & Years; from: FIN home; to: SCR-REQ-FIN-007 (period's entries), SCR-REQ-FIN-009 (year-end closing/opening entries)
  Content shape: true hierarchy (year → periods)
  Traces       : REQ-FIN-021, REQ-FIN-022, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-031
### B2 — Search / list
  Filters: yearCode, periodCode, statusCode. Result columns mirror the filters plus startDate/endDate.
### B3 — Input
  Year fields: yearCode, startDate, endDate. Period fields: periodCode, sequenceNo, startDate, endDate. Actions: "Approve close" (soft/hard) applies RULE-008, RULE-009; "Year-end close" applies RULE-010, RULE-011 and triggers REQ-FIN-030/031.
### B4 — Access
  Page code SEC_PAGES.FIN_PERIOD. Financial Controller: VIEW, CREATE, UPDATE, DELETE (state transitions and close actions). Accountant, Auditor: VIEW.
### B5 — API expectations
  create/search/update/read year & period; approve-close (action); year-end-close (action); RULEs RULE-008, 009, 010, 011; Traces REQ-FIN-021, 022, 027…031.

## SCR-REQ-FIN-009 — كشف الحساب / Account Ledger
### B1 — Definition
  Purpose      : Show POSTED movements and running balance for an account/dimension over a period.
  Entities     : (derived — reads ENT-FIN-001, ENT-FIN-006, ENT-FIN-007; no new entity)
  Operations   : search, generate, drill-down
  Users        : Accountant, Financial Controller, Auditor
  Navigation   : FIN → Reports → Account Ledger; from: SCR-REQ-FIN-010, SCR-REQ-FIN-011, SCR-REQ-FIN-012 (drill-down); to: SCR-REQ-FIN-007 (originating entry)
  Content shape: flat record with totals
  Traces       : REQ-FIN-032, REQ-FIN-034
### B2 — Search / list
  Filters: accountId, dimensionValues, periodId/date range. Result columns: entryNo, entryDate, direction, amount, running balance.
### B3 — Input
  Read-only report — no create/update.
### B4 — Access
  Page code SEC_PAGES.FIN_LEDGER. Accountant, Financial Controller, Auditor: VIEW.
### B5 — API expectations
  search/generate ledger (read); RULE: none (derived, read-only per POL-FIN-009); Traces REQ-FIN-032, 034.

## SCR-REQ-FIN-010 — ميزان المراجعة / Trial Balance
### B1 — Definition
  Purpose      : Show every account's POSTED debit/credit totals for a period.
  Entities     : (derived — reads ENT-FIN-001, ENT-FIN-006, ENT-FIN-007; no new entity)
  Operations   : search, generate, drill-down
  Users        : Accountant, Financial Controller, Auditor
  Navigation   : FIN → Reports → Trial Balance; from: FIN home; to: SCR-REQ-FIN-009 (drill-down)
  Content shape: flat record with totals
  Traces       : REQ-FIN-032, REQ-FIN-034
### B2 — Search / list
  Filters: periodId/date range, accountType. Result columns: account, debit total, credit total.
### B3 — Input
  Read-only report — no create/update.
### B4 — Access
  Page code SEC_PAGES.FIN_TB. Accountant, Financial Controller, Auditor: VIEW.
### B5 — API expectations
  search/generate trial balance (read); Traces REQ-FIN-032, 034.

## SCR-REQ-FIN-011 — الميزانية العمومية / Balance Sheet
### B1 — Definition
  Purpose      : Present asset/liability/equity balances as of a date, over posted entries.
  Entities     : (derived — reads ENT-FIN-001, ENT-FIN-006, ENT-FIN-007; no new entity)
  Operations   : search, generate, drill-down
  Users        : Accountant, Financial Controller, Auditor
  Navigation   : FIN → Reports → Balance Sheet; from: FIN home; to: SCR-REQ-FIN-010 (drill-down)
  Content shape: other (statement presentation layer)
  Traces       : REQ-FIN-032, REQ-FIN-034
### B2 — Search / list
  Filters: as-of date, fiscalYearId. Result columns: account group, balance.
### B3 — Input
  Read-only report — no create/update.
### B4 — Access
  Page code SEC_PAGES.FIN_BS. Accountant, Financial Controller, Auditor: VIEW.
### B5 — API expectations
  search/generate balance sheet (read); Traces REQ-FIN-032, 034.

## SCR-REQ-FIN-012 — قائمة الدخل / Income Statement
### B1 — Definition
  Purpose      : Present revenue/expense results over a period, over posted entries.
  Entities     : (derived — reads ENT-FIN-001, ENT-FIN-006, ENT-FIN-007; no new entity)
  Operations   : search, generate, drill-down
  Users        : Accountant, Financial Controller, Auditor
  Navigation   : FIN → Reports → Income Statement; from: FIN home; to: SCR-REQ-FIN-010 (drill-down)
  Content shape: other (statement presentation layer)
  Traces       : REQ-FIN-032, REQ-FIN-034
### B2 — Search / list
  Filters: period range, fiscalYearId. Result columns: account group, amount.
### B3 — Input
  Read-only report — no create/update.
### B4 — Access
  Page code SEC_PAGES.FIN_IS. Accountant, Financial Controller, Auditor: VIEW.
### B5 — API expectations
  search/generate income statement (read); Traces REQ-FIN-032, 034.

## SCR-REQ-FIN-013 — تقارير الأبعاد / Dimension Reports
### B1 — Definition
  Purpose      : Present a statement filtered/grouped by dimension value.
  Entities     : (derived — reads ENT-FIN-001, ENT-FIN-002, ENT-FIN-007; no new entity)
  Operations   : search, generate, drill-down
  Users        : Financial Controller, Auditor
  Navigation   : FIN → Reports → Dimension Reports; from: FIN home; to: SCR-REQ-FIN-009 (drill-down)
  Content shape: flat record with totals
  Traces       : REQ-FIN-033, REQ-FIN-034
### B2 — Search / list
  Filters: dimensionKey, dimensionValue, period range. Result columns: account, dimension value, balance.
### B3 — Input
  Read-only report — no create/update.
### B4 — Access
  Page code SEC_PAGES.FIN_DIMRPT. Financial Controller, Auditor: VIEW.
### B5 — API expectations
  search/generate dimension report (read); Traces REQ-FIN-033, 034.

## SCR-REQ-FIN-014 — تسجيل الدخول / Login
### B1 — Definition
  Purpose      : Authenticate a FIN user.
  Entities     : ENT-FIN-012
  Operations   : custom (authenticate)
  Users        : every FIN role
  Navigation   : entry point; from: none; to: FIN home
  Content shape: other (auth form)
  Traces       : REQ-FIN-025
### B2 — Search / list
  Not applicable — no search on a login screen.
### B3 — Input
  Fields: username, password. Action: authenticate, against ENT-FIN-012 only.
### B4 — Access
  Page code SEC_PAGES.FIN_LOGIN. No gateway VIEW required (pre-authentication); every FIN role reaches it.
### B5 — API expectations
  authenticate (custom verb, not the standard CRUD set); Traces REQ-FIN-025.

## SCR-REQ-FIN-015 — المستخدمون / Users
### B1 — Definition
  Purpose      : Manage FIN's own user accounts.
  Entities     : ENT-FIN-012
  Operations   : search, list, create, read, update, deactivate
  Users        : Accounting System Administrator
  Navigation   : FIN → Security → Users; from: FIN home; to: SCR-REQ-FIN-016 (role assignment)
  Content shape: flat record
  Traces       : REQ-FIN-025
### B2 — Search / list
  Filters: username, nameAr/En, isActiveFl. Result columns mirror the filters plus lastLoginAt.
### B3 — Input
  Fields: username, nameAr, nameEn, password (write-only). Save never accepts passwordHash directly from a client.
### B4 — Access
  Page code SEC_PAGES.FIN_USER. Accounting System Administrator: VIEW, CREATE, UPDATE, DELETE.
### B5 — API expectations
  create/search/update/deactivate/read user; Traces REQ-FIN-025.

## SCR-REQ-FIN-016 — الأدوار والصلاحيات / Roles & Permissions
### B1 — Definition
  Purpose      : Manage FIN roles, their screen/action permissions, and user assignment.
  Entities     : ENT-FIN-013
  Operations   : search, list, create, read, update, deactivate, assign (permission, user)
  Users        : Accounting System Administrator
  Navigation   : FIN → Security → Roles & Permissions; from: SCR-REQ-FIN-015; to: none
  Content shape: master + detail (role in master, permission/user assignment in detail)
  Traces       : REQ-FIN-025, REQ-FIN-026
### B2 — Search / list
  Filters: roleCode, roleNameAr/En, isActiveFl. Result columns mirror the filters plus assigned user count.
### B3 — Input
  Master fields: roleCode, roleNameAr, roleNameEn. Detail: permissionAssignments (pageCode, actionCode), userAssignments. Save enforces the VIEW-gateway rule (§7.1) and supports RULE-008's distinct-role pattern.
### B4 — Access
  Page code SEC_PAGES.FIN_ROLE. Accounting System Administrator: VIEW, CREATE, UPDATE, DELETE.
### B5 — API expectations
  create/search/update/deactivate/read role; assign permission/user (action); Traces REQ-FIN-025, 026.

# STANDALONE

## Traceability matrix

| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-FIN-001 | REQ-FIN-001, 002, 003, 005 | AC-FIN-001, 002, 003, 005 | RULE-001 | ENT-FIN-001 | SCR-REQ-FIN-001 |
| US-FIN-002 | REQ-FIN-004, 005 | AC-FIN-004, 005 | RULE-003 | ENT-FIN-002 | SCR-REQ-FIN-002 |
| US-FIN-003 | REQ-FIN-006, 007 | AC-FIN-006, 007 | — | ENT-FIN-003 | SCR-REQ-FIN-003 |
| US-FIN-004 | REQ-FIN-008…013 | AC-FIN-008…014 | RULE-005, 012 | ENT-FIN-004, ENT-FIN-005 | SCR-REQ-FIN-004 |
| US-FIN-005 | REQ-FIN-014, 020 | AC-FIN-015, 022 | — | ENT-FIN-006, ENT-FIN-007 | SCR-REQ-FIN-007 |
| US-FIN-006 | REQ-FIN-015 | AC-FIN-016 | — | ENT-FIN-006, ENT-FIN-007 | SCR-REQ-FIN-007 |
| US-FIN-007 | REQ-FIN-016 | AC-FIN-017 | RULE-013 | ENT-FIN-008 | SCR-REQ-FIN-005 |
| US-FIN-008 | REQ-FIN-017 | AC-FIN-018 | RULE-014 | ENT-FIN-009 | SCR-REQ-FIN-006 |
| US-FIN-009 | REQ-FIN-018, 019, 020 | AC-FIN-019, 020, 021, 022 | RULE-001, 002, 003, 004, 006 | ENT-FIN-006, ENT-FIN-007 | SCR-REQ-FIN-007 |
| US-FIN-010 | REQ-FIN-021, 022 | AC-FIN-023, 024 | RULE-008 | ENT-FIN-011, ENT-FIN-006, ENT-FIN-012 | SCR-REQ-FIN-008 |
| US-FIN-011 | REQ-FIN-023, 024 | AC-FIN-025, 026 | RULE-006, 007 | ENT-FIN-006, ENT-FIN-007 | SCR-REQ-FIN-007 |
| US-FIN-012 | REQ-FIN-025, 026 | AC-FIN-027, 028 | — | ENT-FIN-012, ENT-FIN-013 | SCR-REQ-FIN-014, 015, 016 |
| US-FIN-013 | REQ-FIN-027, 028, 029 | AC-FIN-029, 030, 031 | RULE-004, 009 | ENT-FIN-010, ENT-FIN-011 | SCR-REQ-FIN-008 |
| US-FIN-014 | REQ-FIN-030, 031 | AC-FIN-032, 033 | RULE-010, 011 | ENT-FIN-006, ENT-FIN-010, ENT-FIN-001 | SCR-REQ-FIN-008 |
| US-FIN-015 | REQ-FIN-032 | AC-FIN-034 | — | ENT-FIN-001, ENT-FIN-006, ENT-FIN-007 | SCR-REQ-FIN-009, 010, 011, 012 |
| US-FIN-016 | REQ-FIN-033 | AC-FIN-035 | — | ENT-FIN-001, ENT-FIN-002, ENT-FIN-007 | SCR-REQ-FIN-013 |
| US-FIN-017 | REQ-FIN-034 | AC-FIN-036, 037 | — | ENT-FIN-001, ENT-FIN-006, ENT-FIN-007 | SCR-REQ-FIN-009…013 |

Every story maps to ≥ 1 REQ; every REQ maps to ≥ 1 AC; every RULE traces to ≥ 1
REQ; every SCR-REQ traces to ≥ 1 REQ. No orphan.

## Decisions applied

| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| Decision 1 (carried, confirmed) | FIN is fully isolated — own lookups (ENT-FIN-003), own RBAC (ENT-FIN-012/013), `DEPENDENCIES: NONE` | plan §2.1, §8.1; prd-approval gate, approved 2026-09-10 | CONFIRMED — do not revisit |
| DEFAULT (A3, ENT-FIN-001) | `account-nature` is a fixed 2-value list, not a growing ENT-FIN-003 lookup | plan §1.2 | closed set by accounting convention — no override expected |
| DEFAULT (A3, ENT-FIN-002) | Dimension `controlType` decided per-dimension (FIXED_LIST vs REFERENCE_ENTITY) using the SRS §3.3 growing-set rule | SRS §3.3 (LOOKUPS rule) | administrator chooses per dimension at setup |
| ADR-FIN-001 | Recurring/reversing template schedule represented as a data-defined `scheduleRule` (not a fixed enumerated frequency) | `decisions/FIN/ADR-FIN-001.md` | non-breaking — CONTINUE |
| ADR-FIN-002 | Mapping-set account derivation modeled as repeating entries embedded in ENT-FIN-005 (Rule Line), not a separate top-level entity, to match the entity list already registered at P0 | `decisions/FIN/ADR-FIN-002.md` | non-breaking — CONTINUE |
| ADR-FIN-003 | Year-end close requires every period of the year Hard Closed first (RULE-010) | `decisions/FIN/ADR-FIN-003.md` | non-breaking — CONTINUE |

## Access summary

| SCR-REQ | Page code | Accounting Config Admin | Accountant | Financial Controller | Accounting Sys Admin | Auditor |
|---|---|---|---|---|---|---|
| SCR-REQ-FIN-001 Chart of Accounts | FIN_COA | VIEW,CREATE,UPDATE,DELETE | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-002 Dimensions | FIN_DIM | VIEW,CREATE,UPDATE,DELETE | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-003 Lookups | FIN_LKP | VIEW,CREATE,UPDATE,DELETE | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-004 Engine Rules | FIN_RULE | VIEW,CREATE,UPDATE,DELETE | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-005 Recurring Templates | FIN_TMPL | — | VIEW,CREATE,UPDATE,DELETE | VIEW | — | VIEW |
| SCR-REQ-FIN-006 Allocation Rules | FIN_ALLOC | — | VIEW,CREATE,UPDATE,DELETE | VIEW | — | VIEW |
| SCR-REQ-FIN-007 Journal Entries | FIN_JE | — | VIEW,CREATE,UPDATE | VIEW | — | VIEW |
| SCR-REQ-FIN-008 Fiscal Periods & Years | FIN_PERIOD | — | VIEW | VIEW,CREATE,UPDATE,DELETE | — | VIEW |
| SCR-REQ-FIN-009 Account Ledger | FIN_LEDGER | — | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-010 Trial Balance | FIN_TB | — | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-011 Balance Sheet | FIN_BS | — | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-012 Income Statement | FIN_IS | — | VIEW | VIEW | — | VIEW |
| SCR-REQ-FIN-013 Dimension Reports | FIN_DIMRPT | — | — | VIEW | — | VIEW |
| SCR-REQ-FIN-014 Login | FIN_LOGIN | (pre-auth, all roles) | (pre-auth, all roles) | (pre-auth, all roles) | (pre-auth, all roles) | (pre-auth, all roles) |
| SCR-REQ-FIN-015 Users | FIN_USER | — | — | — | VIEW,CREATE,UPDATE,DELETE | — |
| SCR-REQ-FIN-016 Roles & Permissions | FIN_ROLE | — | — | — | VIEW,CREATE,UPDATE,DELETE | — |
══════════════════════════════════════════════════════════════════
