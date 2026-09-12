# BACKEND EXECUTION PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Dialect : postgresql16
Framework : spring-boot-java (profile.stack.backend.framework)
Inputs : srs (v1, PRD-approved), db-script (v1), registry-srs (v1), registry-db (v1)
Open ADRs : 1 — erp/decisions/FIN/ (ADR-FIN-001, carried from P2; no new ADR this stage)
══════════════════════════════════════════════════════════════════

## PRE-GENERATION EXTRACTION — FIN v1 (working set; not part of the plan proper)

```
── FROM srs ──────────────────────────────────────────────────────────────
ENTITIES      14 — ENT-FIN-001..014 (master/config/lookup/transactional per SRS A3)
REQUIREMENTS  46 — REQ-FIN-001..046, each with 1 AC-FIN-*
RULES         16 — RULE-FIN-001..016, all 14 §12 must-honor points covered (see ALIGN)
SCREENS       12 — SCR-REQ-FIN-001..012
PERMISSIONS   12 secured page codes + PERM_<PAGE_CODE>_<ACTION>, gateway VIEW, plus the
              custom `PERM_FIN_PERIODS_CLOSE_APPROVE` (RULE-FIN-015 SoD)
LOOKUPS       13 keys, all FIN-owned, registered into MDL (SRS A6) — none CHECK-constrained
              locally (unlike SEC's ADR-SEC-001; MDL is already gated)
BUSINESS CODE JournalEntry.docNo — system-generated (platform numbering engine), unique
              per fiscalYearId, read-only after create
── FROM db-script ────────────────────────────────────────────────────────
TABLES        14 tables, FIN_ACCOUNT … FIN_ALLOCATION_TARGET
PK GENERATION every table: `GENERATED ALWAYS AS IDENTITY`
COLUMNS       146 DBF-FIN-001..146
CONSTRAINTS   PK_*, UQ_*, CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE (POL-FIN-005), FK_*; INDEXES IDX_*
XM            1 — XM-FIN-001 SOFT-READ → MDL_LOOKUP_VALUE, status ACTIVE
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   LookupType/LookupValue (MDL) via XM-FIN-001; SEC's identity/
                           authorization consumed as platform-standard integration, not
                           an XM row (ADR-FIN-001)
EXISTING LOOKUP KEYS        none reused — all 13 are new, FIN-owned
ID RANGES already used      API: none yet · QR: none yet
──────────────────────────────────────────────────────────────────────────
No row required §2A.3 extraction-failure handling.
```

## EXECUTION PLAN INDEX — FIN v1 — backend-execution-plan-fin.md
Profile: erp · dialect: postgresql16 · framework: spring-boot-java
Open ADRs: 1 — decisions/FIN/ (ADR-FIN-001, non-breaking, carried from P2)

**ENTITY REGISTRY**
| ENT | Name | Table | Business code | Operations |
|---|---|---|---|---|
| ENT-FIN-001 | Account | FIN_ACCOUNT | none | create, read, search, update, deactivate |
| ENT-FIN-002 | Dimension | FIN_DIMENSION | none | create, read, search, deactivate |
| ENT-FIN-003 | DimensionValue | FIN_DIMENSION_VALUE | none | create, read, search, deactivate |
| ENT-FIN-004 | JournalEntry | FIN_JOURNAL_ENTRY | **docNo** (numbering engine) | create (4 sources), read, search, reverse |
| ENT-FIN-005 | JournalLine | FIN_JOURNAL_LINE | none | create (with header), read |
| ENT-FIN-006 | JournalLineDimension | FIN_JOURNAL_LINE_DIM | none | create (with line), read |
| ENT-FIN-007 | FiscalYear | FIN_FISCAL_YEAR | none | create, read, search |
| ENT-FIN-008 | FiscalPeriod | FIN_FISCAL_PERIOD | none | create, read, search, open, soft-close, hard-close |
| ENT-FIN-009 | EventTypeRule | FIN_EVENT_TYPE_RULE | none | create, read, search, update, deactivate |
| ENT-FIN-010 | RuleLine | FIN_RULE_LINE | none | create, read, update, delete |
| ENT-FIN-011 | RecurringTemplate | FIN_RECURRING_TEMPLATE | none | create, read, search, update, deactivate |
| ENT-FIN-012 | RecurringTemplateLine | FIN_RECURRING_TEMPLATE_LINE | none | create, read, update, delete |
| ENT-FIN-013 | AllocationRule | FIN_ALLOCATION_RULE | none | create, read, search, update, deactivate |
| ENT-FIN-014 | AllocationTarget | FIN_ALLOCATION_TARGET | none | create, read, update, delete |

**FIELD REGISTRY** — see DB Alignment Manifest below (146 rows; property = camelCase of the
db-script column, per the same 1:1 transformation used for SEC/MDL — not restated as a
separate lighter table here given the row count, per this stage's own economy: the
Manifest already carries property/type/status, and read-only is uniformly: **Yes** for
every PK, every audit column, every system-timestamp column (postedAt, closedAt/closedBy,
createdAt-only child rows); **No** for every business-input field named in each entity's
SRS A3 "Required" column. The DB Alignment Manifest is the single canonical binding.

**API REGISTRY**
| API | Operation | Verb | Path | Traces (REQ) |
|---|---|---|---|---|
| API-FIN-001 | search accounts | GET | /api/v1/fin/accounts | REQ-FIN-001 |
| API-FIN-002 | create account | POST | /api/v1/fin/accounts | REQ-FIN-001, REQ-FIN-002 |
| API-FIN-003 | update account | PUT | /api/v1/fin/accounts/{id} | REQ-FIN-002 |
| API-FIN-004 | deactivate account | DELETE | /api/v1/fin/accounts/{id} | REQ-FIN-003 |
| API-FIN-005 | search dimensions | GET | /api/v1/fin/dimensions | REQ-FIN-004 |
| API-FIN-006 | create dimension | POST | /api/v1/fin/dimensions | REQ-FIN-004 |
| API-FIN-007 | create dimension value | POST | /api/v1/fin/dimensions/{id}/values | REQ-FIN-005, REQ-FIN-006 |
| API-FIN-008 | search dimension values | GET | /api/v1/fin/dimensions/{id}/values | REQ-FIN-005 |
| API-FIN-009 | search event-type rules | GET | /api/v1/fin/event-rules | REQ-FIN-007 |
| API-FIN-010 | create event-type rule | POST | /api/v1/fin/event-rules | REQ-FIN-007 |
| API-FIN-011 | add rule line | POST | /api/v1/fin/event-rules/{id}/lines | REQ-FIN-008, REQ-FIN-009 |
| API-FIN-012 | search templates | GET | /api/v1/fin/recurring-templates | REQ-FIN-022 |
| API-FIN-013 | create template | POST | /api/v1/fin/recurring-templates | REQ-FIN-022 |
| API-FIN-014 | run template | POST | /api/v1/fin/recurring-templates/{id}/run | REQ-FIN-023, REQ-FIN-024 |
| API-FIN-015 | search allocation rules | GET | /api/v1/fin/allocation-rules | REQ-FIN-025 |
| API-FIN-016 | create allocation rule | POST | /api/v1/fin/allocation-rules | REQ-FIN-025 |
| API-FIN-017 | run allocation rule | POST | /api/v1/fin/allocation-rules/{id}/run | REQ-FIN-026 |
| API-FIN-018 | search journal entries | GET | /api/v1/fin/journal-entries | REQ-FIN-027 |
| API-FIN-019 | create manual entry | POST | /api/v1/fin/journal-entries | REQ-FIN-014, REQ-FIN-015, REQ-FIN-017, REQ-FIN-018..021 |
| API-FIN-020 | build event entry (system) | POST | /api/v1/fin/journal-entries/from-event | REQ-FIN-010..013, REQ-FIN-017..021 |
| API-FIN-021 | reverse entry | POST | /api/v1/fin/journal-entries/{id}/reverse | REQ-FIN-028, REQ-FIN-029, REQ-FIN-030 |
| API-FIN-022 | read entry | GET | /api/v1/fin/journal-entries/{id} | REQ-FIN-016, REQ-FIN-027 |
| API-FIN-023 | create fiscal year | POST | /api/v1/fin/fiscal-years | REQ-FIN-031 |
| API-FIN-024 | open period | PATCH | /api/v1/fin/fiscal-periods/{id}/open | REQ-FIN-032 |
| API-FIN-025 | soft-close period | PATCH | /api/v1/fin/fiscal-periods/{id}/soft-close | REQ-FIN-033 |
| API-FIN-026 | hard-close period (approval) | PATCH | /api/v1/fin/fiscal-periods/{id}/hard-close | REQ-FIN-034, REQ-FIN-035, REQ-FIN-037, REQ-FIN-038 |
| API-FIN-027 | run year-end close | POST | /api/v1/fin/fiscal-years/{id}/year-end-close | REQ-FIN-036 |
| API-FIN-028 | account ledger | GET | /api/v1/fin/reports/account-ledger | REQ-FIN-039, REQ-FIN-046 |
| API-FIN-029 | trial balance | GET | /api/v1/fin/reports/trial-balance | REQ-FIN-040, REQ-FIN-046 |
| API-FIN-030 | balance sheet | GET | /api/v1/fin/reports/balance-sheet | REQ-FIN-041, REQ-FIN-046 |
| API-FIN-031 | income statement | GET | /api/v1/fin/reports/income-statement | REQ-FIN-042, REQ-FIN-046 |
| API-FIN-032 | dimension report | GET | /api/v1/fin/reports/dimension | REQ-FIN-043 |

**RULE REGISTRY** — all 16 SRS rules; full text: srs-fin.md §A5, cited by id in each API's
Validations line below (never restated in full here — single-source rule).

**SCREEN REGISTRY** — 12 secured screens; see SEC-BE (Phase 7) below.

**LOOKUP REGISTRY** — 13 keys; see SRS A6 (not restated).

**QRC SUMMARY** — 44 QR ids, QR-FIN-001..044 — see Query Reference Catalog below.

**DB ALIGNMENT** — see manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 1 (XM-FIN-001, SOFT-READ → MDL, ACTIVE)
**SECURITY** — 12 secured screens, data-driven role grants + 1 custom SoD-gated permission

## DB Alignment Manifest — FIN v1
All 146 rows: **status ✓ (aligned)**; XM populated only on lookup-backed columns (12
columns across 8 tables touch XM-FIN-001, noted individually below — a SOFT-READ, never
blocking).

| DBF | ENT | property | type | XM |
|---|---|---|---|---|
| DBF-FIN-001 | ENT-FIN-001 | accountPk | Long | — |
| DBF-FIN-002 | ENT-FIN-001 | code | String | — |
| DBF-FIN-003 | ENT-FIN-001 | nameAr | String | — |
| DBF-FIN-004 | ENT-FIN-001 | nameEn | String | — |
| DBF-FIN-005 | ENT-FIN-001 | accountTypeCode | String | XM-FIN-001 |
| DBF-FIN-006 | ENT-FIN-001 | natureCode | String | XM-FIN-001 |
| DBF-FIN-007 | ENT-FIN-001 | parentAccountId | Long | — |
| DBF-FIN-008 | ENT-FIN-001 | isLeafFl | Boolean | — |
| DBF-FIN-009 | ENT-FIN-001 | isActiveFl | Boolean | — |
| DBF-FIN-010 | ENT-FIN-001 | createdBy | String | — |
| DBF-FIN-011 | ENT-FIN-001 | createdAt | Instant | — |
| DBF-FIN-012 | ENT-FIN-001 | updatedBy | String | — |
| DBF-FIN-013 | ENT-FIN-001 | updatedAt | Instant | — |
| DBF-FIN-014 | ENT-FIN-002 | dimensionPk | Long | — |
| DBF-FIN-015 | ENT-FIN-002 | code | String | — |
| DBF-FIN-016 | ENT-FIN-002 | nameAr | String | — |
| DBF-FIN-017 | ENT-FIN-002 | nameEn | String | — |
| DBF-FIN-018 | ENT-FIN-002 | isActiveFl | Boolean | — |
| DBF-FIN-019 | ENT-FIN-002 | createdBy | String | — |
| DBF-FIN-020 | ENT-FIN-002 | createdAt | Instant | — |
| DBF-FIN-021 | ENT-FIN-002 | updatedBy | String | — |
| DBF-FIN-022 | ENT-FIN-002 | updatedAt | Instant | — |
| DBF-FIN-023 | ENT-FIN-003 | dimensionValuePk | Long | — |
| DBF-FIN-024 | ENT-FIN-003 | dimensionId | Long | — |
| DBF-FIN-025 | ENT-FIN-003 | code | String | — |
| DBF-FIN-026 | ENT-FIN-003 | nameAr | String | — |
| DBF-FIN-027 | ENT-FIN-003 | nameEn | String | — |
| DBF-FIN-028 | ENT-FIN-003 | sortOrder | Integer | — |
| DBF-FIN-029 | ENT-FIN-003 | isActiveFl | Boolean | — |
| DBF-FIN-030 | ENT-FIN-003 | createdBy | String | — |
| DBF-FIN-031 | ENT-FIN-003 | createdAt | Instant | — |
| DBF-FIN-032 | ENT-FIN-003 | updatedBy | String | — |
| DBF-FIN-033 | ENT-FIN-003 | updatedAt | Instant | — |
| DBF-FIN-034 | ENT-FIN-004 | journalEntryPk | Long | — |
| DBF-FIN-035 | ENT-FIN-004 | docNo | String | — |
| DBF-FIN-036 | ENT-FIN-004 | docDate | LocalDate | — |
| DBF-FIN-037 | ENT-FIN-004 | fiscalYearId | Long | — |
| DBF-FIN-038 | ENT-FIN-004 | periodId | Long | — |
| DBF-FIN-039 | ENT-FIN-004 | journalTypeCode | String | XM-FIN-001 |
| DBF-FIN-040 | ENT-FIN-004 | statusCode | String | XM-FIN-001 |
| DBF-FIN-041 | ENT-FIN-004 | eventReference | String | — |
| DBF-FIN-042 | ENT-FIN-004 | originalEntryId | Long | — |
| DBF-FIN-043 | ENT-FIN-004 | reversalEntryId | Long | — |
| DBF-FIN-044 | ENT-FIN-004 | descriptionAr | String | — |
| DBF-FIN-045 | ENT-FIN-004 | descriptionEn | String | — |
| DBF-FIN-046 | ENT-FIN-004 | postedAt | Instant | — |
| DBF-FIN-047 | ENT-FIN-004 | createdBy | String | — |
| DBF-FIN-048 | ENT-FIN-004 | createdAt | Instant | — |
| DBF-FIN-049 | ENT-FIN-004 | updatedBy | String | — |
| DBF-FIN-050 | ENT-FIN-004 | updatedAt | Instant | — |
| DBF-FIN-051 | ENT-FIN-005 | journalLinePk | Long | — |
| DBF-FIN-052 | ENT-FIN-005 | journalEntryId | Long | — |
| DBF-FIN-053 | ENT-FIN-005 | lineNo | Integer | — |
| DBF-FIN-054 | ENT-FIN-005 | accountId | Long | — |
| DBF-FIN-055 | ENT-FIN-005 | amount | BigDecimal | — |
| DBF-FIN-056 | ENT-FIN-005 | directionCode | String | XM-FIN-001 |
| DBF-FIN-057 | ENT-FIN-005 | isRemainderFl | Boolean | — |
| DBF-FIN-058 | ENT-FIN-005 | descriptionAr | String | — |
| DBF-FIN-059 | ENT-FIN-005 | descriptionEn | String | — |
| DBF-FIN-060 | ENT-FIN-005 | createdAt | Instant | — |
| DBF-FIN-061 | ENT-FIN-006 | journalLineDimensionPk | Long | — |
| DBF-FIN-062 | ENT-FIN-006 | journalLineId | Long | — |
| DBF-FIN-063 | ENT-FIN-006 | dimensionId | Long | — |
| DBF-FIN-064 | ENT-FIN-006 | dimensionValueId | Long | — |
| DBF-FIN-065 | ENT-FIN-007 | fiscalYearPk | Long | — |
| DBF-FIN-066 | ENT-FIN-007 | code | String | — |
| DBF-FIN-067 | ENT-FIN-007 | startDate | LocalDate | — |
| DBF-FIN-068 | ENT-FIN-007 | endDate | LocalDate | — |
| DBF-FIN-069 | ENT-FIN-007 | statusCode | String | XM-FIN-001 |
| DBF-FIN-070 | ENT-FIN-007 | isActiveFl | Boolean | — |
| DBF-FIN-071 | ENT-FIN-007 | createdBy | String | — |
| DBF-FIN-072 | ENT-FIN-007 | createdAt | Instant | — |
| DBF-FIN-073 | ENT-FIN-007 | updatedBy | String | — |
| DBF-FIN-074 | ENT-FIN-007 | updatedAt | Instant | — |
| DBF-FIN-075 | ENT-FIN-008 | fiscalPeriodPk | Long | — |
| DBF-FIN-076 | ENT-FIN-008 | fiscalYearId | Long | — |
| DBF-FIN-077 | ENT-FIN-008 | periodNo | Integer | — |
| DBF-FIN-078 | ENT-FIN-008 | nameAr | String | — |
| DBF-FIN-079 | ENT-FIN-008 | nameEn | String | — |
| DBF-FIN-080 | ENT-FIN-008 | startDate | LocalDate | — |
| DBF-FIN-081 | ENT-FIN-008 | endDate | LocalDate | — |
| DBF-FIN-082 | ENT-FIN-008 | statusCode | String | XM-FIN-001 |
| DBF-FIN-083 | ENT-FIN-008 | closedBy | String | — |
| DBF-FIN-084 | ENT-FIN-008 | closedAt | Instant | — |
| DBF-FIN-085 | ENT-FIN-008 | createdBy | String | — |
| DBF-FIN-086 | ENT-FIN-008 | createdAt | Instant | — |
| DBF-FIN-087 | ENT-FIN-008 | updatedBy | String | — |
| DBF-FIN-088 | ENT-FIN-008 | updatedAt | Instant | — |
| DBF-FIN-089 | ENT-FIN-009 | eventTypeRulePk | Long | — |
| DBF-FIN-090 | ENT-FIN-009 | eventTypeCode | String | XM-FIN-001 |
| DBF-FIN-091 | ENT-FIN-009 | nameAr | String | — |
| DBF-FIN-092 | ENT-FIN-009 | nameEn | String | — |
| DBF-FIN-093 | ENT-FIN-009 | isActiveFl | Boolean | — |
| DBF-FIN-094 | ENT-FIN-009 | createdBy | String | — |
| DBF-FIN-095 | ENT-FIN-009 | createdAt | Instant | — |
| DBF-FIN-096 | ENT-FIN-009 | updatedBy | String | — |
| DBF-FIN-097 | ENT-FIN-009 | updatedAt | Instant | — |
| DBF-FIN-098 | ENT-FIN-010 | ruleLineId | Long | — |
| DBF-FIN-099 | ENT-FIN-010 | eventTypeRuleId | Long | — |
| DBF-FIN-100 | ENT-FIN-010 | lineNo | Integer | — |
| DBF-FIN-101 | ENT-FIN-010 | accountDerivationTypeCode | String | XM-FIN-001 |
| DBF-FIN-102 | ENT-FIN-010 | accountDerivationValue | String | — |
| DBF-FIN-103 | ENT-FIN-010 | amountSourceTypeCode | String | XM-FIN-001 |
| DBF-FIN-104 | ENT-FIN-010 | amountSourceValue | String | — |
| DBF-FIN-105 | ENT-FIN-010 | directionCode | String | XM-FIN-001 |
| DBF-FIN-106 | ENT-FIN-010 | distributionTypeCode | String | XM-FIN-001 |
| DBF-FIN-107 | ENT-FIN-010 | isRemainderFl | Boolean | — |
| DBF-FIN-108 | ENT-FIN-010 | createdAt | Instant | — |
| DBF-FIN-109 | ENT-FIN-011 | recurringTemplateId | Long | — |
| DBF-FIN-110 | ENT-FIN-011 | nameAr | String | — |
| DBF-FIN-111 | ENT-FIN-011 | nameEn | String | — |
| DBF-FIN-112 | ENT-FIN-011 | scheduleTypeCode | String | XM-FIN-001 |
| DBF-FIN-113 | ENT-FIN-011 | frequencyCode | String | XM-FIN-001 |
| DBF-FIN-114 | ENT-FIN-011 | startDate | LocalDate | — |
| DBF-FIN-115 | ENT-FIN-011 | nextRunDate | LocalDate | — |
| DBF-FIN-116 | ENT-FIN-011 | endDate | LocalDate | — |
| DBF-FIN-117 | ENT-FIN-011 | isActiveFl | Boolean | — |
| DBF-FIN-118 | ENT-FIN-011 | createdBy | String | — |
| DBF-FIN-119 | ENT-FIN-011 | createdAt | Instant | — |
| DBF-FIN-120 | ENT-FIN-011 | updatedBy | String | — |
| DBF-FIN-121 | ENT-FIN-011 | updatedAt | Instant | — |
| DBF-FIN-122 | ENT-FIN-012 | recurringTemplateLineId | Long | — |
| DBF-FIN-123 | ENT-FIN-012 | recurringTemplateId | Long | — |
| DBF-FIN-124 | ENT-FIN-012 | lineNo | Integer | — |
| DBF-FIN-125 | ENT-FIN-012 | accountId | Long | — |
| DBF-FIN-126 | ENT-FIN-012 | amount | BigDecimal | — |
| DBF-FIN-127 | ENT-FIN-012 | directionCode | String | XM-FIN-001 |
| DBF-FIN-128 | ENT-FIN-012 | dimensionValueId | Long | — |
| DBF-FIN-129 | ENT-FIN-012 | createdAt | Instant | — |
| DBF-FIN-130 | ENT-FIN-013 | allocationRuleId | Long | — |
| DBF-FIN-131 | ENT-FIN-013 | nameAr | String | — |
| DBF-FIN-132 | ENT-FIN-013 | nameEn | String | — |
| DBF-FIN-133 | ENT-FIN-013 | sourceAccountId | Long | — |
| DBF-FIN-134 | ENT-FIN-013 | isActiveFl | Boolean | — |
| DBF-FIN-135 | ENT-FIN-013 | createdBy | String | — |
| DBF-FIN-136 | ENT-FIN-013 | createdAt | Instant | — |
| DBF-FIN-137 | ENT-FIN-013 | updatedBy | String | — |
| DBF-FIN-138 | ENT-FIN-013 | updatedAt | Instant | — |
| DBF-FIN-139 | ENT-FIN-014 | allocationTargetId | Long | — |
| DBF-FIN-140 | ENT-FIN-014 | allocationRuleId | Long | — |
| DBF-FIN-141 | ENT-FIN-014 | lineNo | Integer | — |
| DBF-FIN-142 | ENT-FIN-014 | targetAccountId | Long | — |
| DBF-FIN-143 | ENT-FIN-014 | dimensionValueId | Long | — |
| DBF-FIN-144 | ENT-FIN-014 | distributionTypeCode | String | XM-FIN-001 |
| DBF-FIN-145 | ENT-FIN-014 | distributionValue | BigDecimal | — |
| DBF-FIN-146 | ENT-FIN-014 | isRemainderFl | Boolean | — |

## Query Reference Catalog (QR-FIN-*)

> Logical specification only — never executable code.

| QR | Operation | API | Entity | Kind | Intent |
|---|---|---|---|---|---|
| QR-FIN-001 | FIND_BY_CRITERIA | API-FIN-001 | ENT-FIN-001 | search | search accounts |
| QR-FIN-002 | SAVE | API-FIN-002 | ENT-FIN-001 | create | create account |
| QR-FIN-003 | UPDATE | API-FIN-003 | ENT-FIN-001 | update | update account |
| QR-FIN-004 | UPDATE | API-FIN-004 | ENT-FIN-001 | deactivate | deactivate account |
| QR-FIN-005 | EXISTS | API-FIN-002 | ENT-FIN-001 | uniqueness | account code unique |
| QR-FIN-006 | EXISTS | API-FIN-002, API-FIN-003 | ENT-FIN-001 | RULE-FIN-001 | account has no children before marking leaf |
| QR-FIN-007 | FIND_BY_CRITERIA | API-FIN-005 | ENT-FIN-002 | search | search dimensions |
| QR-FIN-008 | SAVE | API-FIN-006 | ENT-FIN-002 | create | create dimension |
| QR-FIN-009 | SAVE | API-FIN-007 | ENT-FIN-003 | create | create dimension value |
| QR-FIN-010 | EXISTS | API-FIN-007 | ENT-FIN-003 | RULE-FIN-002 | dimension value code unique within dimension |
| QR-FIN-011 | FIND_BY_CRITERIA | API-FIN-008 | ENT-FIN-003 | search | search dimension values |
| QR-FIN-012 | FIND_BY_CRITERIA | API-FIN-009 | ENT-FIN-009 | search | search event-type rules |
| QR-FIN-013 | SAVE | API-FIN-010 | ENT-FIN-009 | create | create event-type rule |
| QR-FIN-014 | EXISTS | API-FIN-010 | ENT-FIN-009 | uniqueness | one active rule per event type |
| QR-FIN-015 | SAVE | API-FIN-011 | ENT-FIN-010 | create | add rule line |
| QR-FIN-016 | EXISTS | API-FIN-011 | ENT-FIN-010 | RULE-FIN-003 | exactly one remainder line when a percentage line exists |
| QR-FIN-017 | FIND_BY_CRITERIA | API-FIN-012 | ENT-FIN-011 | search | search templates |
| QR-FIN-018 | SAVE | API-FIN-013 | ENT-FIN-011, ENT-FIN-012 | create | create template with lines |
| QR-FIN-019 | FIND_ONE | API-FIN-014 | ENT-FIN-011 | run | load template due to run |
| QR-FIN-020 | FIND_BY_CRITERIA | API-FIN-015 | ENT-FIN-013 | search | search allocation rules |
| QR-FIN-021 | SAVE | API-FIN-016 | ENT-FIN-013, ENT-FIN-014 | create | create allocation rule with targets |
| QR-FIN-022 | FIND_ONE | API-FIN-017 | ENT-FIN-013 | run | load allocation rule + current source balance (via QR-FIN-040) |
| QR-FIN-023 | FIND_BY_CRITERIA | API-FIN-018 | ENT-FIN-004 | search | search journal entries |
| QR-FIN-024 | SAVE | API-FIN-019 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build manual entry (DRAFT) |
| QR-FIN-025 | SAVE | API-FIN-020 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build event entry (DRAFT) from rule |
| QR-FIN-026 | EXISTS | API-FIN-020 | ENT-FIN-004 | RULE-FIN-004 | duplicate eventReference |
| QR-FIN-027 | EXISTS | API-FIN-020 | ENT-FIN-009 | RULE-FIN-005 | active rule exists for event type |
| QR-FIN-028 | AGGREGATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-010 | compute remainder-line amount for a compound/percentage distribution |
| QR-FIN-029 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-006 | debits = credits |
| QR-FIN-030 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-001 | RULE-FIN-007 | every line's account is leaf + active |
| QR-FIN-031 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-008 | RULE-FIN-008 | entry's period is Open at post time |
| QR-FIN-032 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-006 | RULE-FIN-009 | every dimension value valid + active |
| QR-FIN-033 | UPDATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-004 | post | flip DRAFT → POSTED, set postedAt (RULE-FIN-016 lock takes effect) |
| QR-FIN-034 | SAVE | API-FIN-021 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build reversal entry (RULE-FIN-011) |
| QR-FIN-035 | EXISTS | API-FIN-021 | ENT-FIN-004 | RULE-FIN-013 | original entry is POSTED |
| QR-FIN-036 | FIND_ONE | API-FIN-021 | ENT-FIN-008 | RULE-FIN-012 | current open period, if original's is closed |
| QR-FIN-037 | FIND_ONE | API-FIN-022 | ENT-FIN-004 | read | read one entry with lines |
| QR-FIN-038 | SAVE | API-FIN-023 | ENT-FIN-007, ENT-FIN-008 | create | create fiscal year + periods |
| QR-FIN-039 | UPDATE | API-FIN-024, API-FIN-025, API-FIN-026 | ENT-FIN-008 | transition | open / soft-close / hard-close a period |
| QR-FIN-040 | EXISTS | API-FIN-026 | ENT-FIN-008 | RULE-FIN-014 | period not already Hard Closed before reopen attempts |
| QR-FIN-041 | AGGREGATE | API-FIN-027 | ENT-FIN-004, ENT-FIN-005 | year-end | compute closing balances, build closing + opening entries |
| QR-FIN-042 | FIND_BY_CRITERIA | API-FIN-028 | ENT-FIN-005 | report | account ledger (running balance) |
| QR-FIN-043 | AGGREGATE | API-FIN-029, API-FIN-030, API-FIN-031 | ENT-FIN-005 | report | trial balance / balance sheet / income statement account balances (shared aggregation, filtered per report by accountTypeCode) |
| QR-FIN-044 | AGGREGATE | API-FIN-032 | ENT-FIN-005, ENT-FIN-006 | report | dimension report (account × dimension value) |

Join governance: every posting-pipeline QR (024, 025, 028-033) is intra-module only
(FIN_JOURNAL_ENTRY/LINE/LINE_DIM/ACCOUNT/FISCAL_PERIOD, all owned here); the one
cross-module read (QR for lookup-code validation, folded into QR-FIN-002/013/015/024/025/
etc.'s "Validations" step, per XM-FIN-001) is a separate REST call, never a SQL join. No
QR joins to resolve a lookup label — every lookup-backed column returns its code; the
frontend resolves the display label via MDL.

---

<!-- PHASE:CORE:START traces=REQ-FIN-017 -->
## PHASE 1 — CORE

**Layers**: controller → service → mapper → domain → repository (`profile.stack.backend.layers`).
Domain-behaviour placement: **domain classes** — one dedicated `<Entity>Domain` per entity —
for every rule that answers "is this operation allowed?"
(`profile.conventions.domain_behaviour_placement: domain_classes`). The service layer is
never a placement: it orchestrates only (load → delegate → persist → return) and holds no
business-rule conditional of its own. How many entities or tables a rule reads is NOT a
placement criterion — the service fetches those facts and passes them into the domain class
as plain arguments, so a multi-entity rule sits in exactly the same place as a single-entity
one. The decision moves to the domain class while the entity keeps the plain state mutation:
`JournalEntryDomain.assertCanPost(...)` then `JournalEntry.post()`;
`FiscalPeriodDomain.assertCanHardClose(...)` then `FiscalPeriod.hardClose()`. FIN domain
classes: `AccountDomain` (RULE-FIN-001, 007), `DimensionValueDomain` (RULE-FIN-002, 009),
`EventTypeRuleDomain` (RULE-FIN-003, 005, 010), `JournalEntryDomain` (RULE-FIN-004, 006,
008, 011, 012, 013, 016), `FiscalPeriodDomain` (RULE-FIN-014, 015), `AllocationRuleDomain`
(RULE-FIN-003, 010 as they apply to allocation targets).

**Error signalling**: `LocalizedException → {code, messageAr, messageEn}`; runtime code
format `FIN-{http}[-{SLUG}]`.

**Transaction scope**: `READ_ONLY` for every `FIND_*`/`EXISTS`/`AGGREGATE` QR; `READ_WRITE`
for every `SAVE`/`UPDATE` QR. The build→validate→post sequence (QR-FIN-024/025 through
QR-FIN-033) runs in ONE transaction per entry — either the whole entry posts, or nothing is
written (no partially-built DRAFT survives a failed validation, per REQ-FIN-015/018-021).

**Search contract**: `{filters, page, size, sort}`, `Page<T>`, empty result = success.

**Audit fields**: `createdBy/createdAt/updatedBy/updatedAt` framework-filled; on
FIN_JOURNAL_ENTRY, `createdBy` records the entry-creator principal used by RULE-FIN-015's
distinct-permission check; `closedBy` on FIN_FISCAL_PERIOD records the period-close
approver principal, from a different principal-permission pair by construction.

**Type mapping** (postgresql16 → Java): identical table to SEC's/MDL's own Phase 1 CORE
(`GENERATED ALWAYS AS IDENTITY`→Long, `VARCHAR(n)`→String, `BOOLEAN`→Boolean,
`TIMESTAMPTZ`→Instant, `TEXT`→String, `DATE`→LocalDate, `NUMERIC(18,4)`→BigDecimal,
bare `NUMERIC` (line/period numbers, sort orders)→Integer, per the same governance note
MDL's plan already stated for its own `sort_order`).

**Lookup values**: all 13 FIN-owned lookup-backed columns are plain `String` holding the
code; validated at the service layer against MDL (XM-FIN-001) before any write — an
invalid code is rejected with a catalog error before it reaches the database.

**Numbering**: `docNo` is generated by the platform numbering engine on `JournalEntry`
create, scoped per `fiscalYearId`, immutable thereafter — excluded entirely from every
create/update request DTO.

**Workflow engine**: forbidden — every lifecycle below (JournalEntry, FiscalPeriod) is a
plain guarded transition, never a workflow definition.

**Languages**: every name field and catalog message present in ar + en.

**Cross-module contract placement**: XM-FIN-001 (SOFT-READ → MDL) is implemented as a
service-layer client (`MdlLookupClient`) calling MDL's `GET /api/v1/mdl/lookups?type=<key>`
(API-MDL-011); FIN's own dependency on SEC for identity/authorization uses the identical
CORE-interceptor mechanism SEC's and MDL's own plans already declare — not redeclared here,
only cited (ADR-FIN-001).

**Cross-cutting authorization**: every secured API below is gated by the platform's CORE
interceptor (module/screen/action grant check) before its controller method runs, exactly
as SEC's own Phase 1 CORE describes; `PERM_FIN_PERIODS_CLOSE_APPROVE` (API-FIN-026/027) is
additionally required to be held by a role distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`
(RULE-FIN-015) — this distinctness check itself runs in FIN's own service layer by reading
the two roles' user sets through SEC's role/grant read APIs, since SEC's interceptor alone
only proves "this caller holds permission X," not "no user holding X also holds Y."
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=REQ-FIN-001,REQ-FIN-010,REQ-FIN-014,REQ-FIN-031 -->
## PHASE 2 — DATA-DOM

Entity count is 14 (≥ threshold) — grouped below under `SUB:DATA-DOM-MASTER` (Account,
FiscalYear, FiscalPeriod — master-like reference data), `SUB:DATA-DOM-TRANSACTIONAL`
(JournalEntry, JournalLine, JournalLineDimension — the posting core), and
`SUB:DATA-DOM-LOOKUP` (Dimension, DimensionValue, EventTypeRule, RuleLine,
RecurringTemplate, RecurringTemplateLine, AllocationRule, AllocationTarget — FIN's own
config/lookup-kind structural data, grouped together here since the engine's three-way
split is by role, not literally the `lookup` kind alone).

<!-- SUB:DATA-DOM-MASTER:START traces=REQ-FIN-001,REQ-FIN-031 -->
### SUB — DATA-DOM-MASTER

#### ENT-FIN-001 — Account      kind: master
BINDINGS: table `FIN_ACCOUNT` · PK `accountPk` (DBF-FIN-001) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none (§3.3 test: no — `code` is client-chosen, not numbering-engine-generated)
FIELDS: DBF-FIN-001..013 — see DB Alignment Manifest; `accountTypeCode`/`natureCode` are
lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request excludes {accountPk, isActiveFl, audit}; update-request
excludes {accountPk, code, isActiveFl, audit} (code immutable, matching MDL's own `key`
precedent); response includes all.
LOOKUP FIELDS: `accountTypeCode`→`ACCOUNT_TYPE`, `natureCode`→`DEBIT_CREDIT`, both via
`GET /api/v1/mdl/lookups?type=<key>` (XM-FIN-001) — stored as code, never a numeric FK.
DOMAIN RULES: **RULE-FIN-001** (full text: srs-fin.md §A5) — Scope ENT-FIN-001 · Trigger:
on update (`isLeafFl`) · DB enforcement: application layer (QR-FIN-006) · owner layer:
service.
STATE MACHINE: `isActiveFl` binary only — not applicable.
CROSS-MODULE: `accountTypeCode`/`natureCode` touch XM-FIN-001.
REPOSITORY OPS → QR-FIN-001, QR-FIN-002, QR-FIN-003, QR-FIN-004, QR-FIN-005, QR-FIN-006.

#### ENT-FIN-007 — FiscalYear      kind: master
BINDINGS: table `FIN_FISCAL_YEAR` · PK `fiscalYearPk` (DBF-FIN-065) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-065..074 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request `{code, startDate, endDate, periodCount}` (periodCount is a
transient input driving REQ-FIN-031's period-generation, not a persisted column); response
includes all persisted fields plus the generated periods.
DOMAIN RULES: none scoped alone (year-end close, REQ-FIN-036, is orchestrated at the API
layer over both FiscalYear and FiscalPeriod — see API-FIN-027).
STATE MACHINE: `statusCode` (FISCAL_YEAR_STATUS) — OPEN→CLOSED, set once by REQ-FIN-036 —
binary, not applicable for a diagram (SRS A7).
CROSS-MODULE: `statusCode` touches XM-FIN-001.
REPOSITORY OPS → QR-FIN-038 (SAVE, with periods), QR-FIN-041 (AGGREGATE, year-end).

#### ENT-FIN-008 — FiscalPeriod      kind: master
BINDINGS: table `FIN_FISCAL_PERIOD` · PK `fiscalPeriodPk` (DBF-FIN-075) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-075..088 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: no direct create (generated with the year, REQ-FIN-031); transition
endpoints only (open/soft-close/hard-close) take just `{id}`; response includes all.
DOMAIN RULES:
**RULE-FIN-008** (srs-fin.md §A5) — period-open-at-post-time — DB enforcement: application
layer (QR-FIN-031) · owner layer: service.
**RULE-FIN-014** (srs-fin.md §A5) — reject reopening a Hard Closed period — DB enforcement:
application layer (QR-FIN-040) · owner layer: service.
**RULE-FIN-015** (srs-fin.md §A5) — close-approval permission distinct from entry-creation
permission — DB enforcement: application layer (service, reading SEC role/grant data,
Phase 1 CORE) · owner layer: service.
STATE MACHINE: `statusCode` (PERIOD_STATE) per SRS A7 — OPEN⇄SOFT_CLOSE→HARD_CLOSE→YEAR_END_CLOSE.
CROSS-MODULE: `statusCode` touches XM-FIN-001; the SoD check (RULE-FIN-015) reads SEC role
data (not a formal XM row — platform-standard integration, ADR-FIN-001).
REPOSITORY OPS → QR-FIN-038 (SAVE, with year), QR-FIN-039 (UPDATE, transitions), QR-FIN-040 (EXISTS).
<!-- SUB:DATA-DOM-MASTER:END -->

<!-- SUB:DATA-DOM-TRANSACTIONAL:START traces=REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028 -->
### SUB — DATA-DOM-TRANSACTIONAL

#### ENT-FIN-004 — JournalEntry      kind: transactional
BINDINGS: table `FIN_JOURNAL_ENTRY` · PK `journalEntryPk` (DBF-FIN-034) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: **docNo** · column `doc_no` (DBF-FIN-035) · format: platform numbering
engine, scoped per `fiscalYearId` (`UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO`) · generation source:
the numbering engine, invoked at create, before the first save — excluded from every
create/update request body, always present in responses.
FIELDS: DBF-FIN-034..050 — see DB Alignment Manifest; `journalTypeCode`/`statusCode`
lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: manual-create request `{docDate, fiscalYearId, periodId, descriptionAr,
descriptionEn, lines: [...]}`; event-build request = the canonical event payload (opaque
to this DTO description — shape owned by the out-of-scope Event consumer, POL-FIN-020);
no update endpoint exists once POSTED (RULE-FIN-016); response includes all fields
including nested lines.
LOOKUP FIELDS: `journalTypeCode`→`JOURNAL_TYPE`, `statusCode`→`JOURNAL_STATUS`, both via
XM-FIN-001.
DOMAIN RULES:
**RULE-FIN-004** — duplicate eventReference rejected — QR-FIN-026 — service.
**RULE-FIN-005** — no active rule for event type — QR-FIN-027 — service.
**RULE-FIN-006** — debit=credit invariant — QR-FIN-029 — service (POL-FIN-001).
**RULE-FIN-008** — period open at post — QR-FIN-031 — service (POL-FIN-004).
**RULE-FIN-011** — reversal exact and linked — QR-FIN-034 — service (POL-FIN-007).
**RULE-FIN-012** — reversal posts to current period if original's closed — QR-FIN-036 — service.
**RULE-FIN-013** — reject reverse of non-POSTED — QR-FIN-035 — service.
**RULE-FIN-016** — lock after posting — enforced by omission (no UPDATE/DELETE mapping on
a POSTED row in the repository layer at all) — service/repository.
(Full text of every RULE above: srs-fin.md §A5 — not restated here per the single-source rule.)
STATE MACHINE: `statusCode` (JOURNAL_STATUS) per SRS A7 — DRAFT→POSTED (RULE-FIN-016 locks
immediately)→VOID (via reversal, RULE-FIN-011).
CROSS-MODULE: `journalTypeCode`/`statusCode` touch XM-FIN-001.
REPOSITORY OPS → QR-FIN-023 through QR-FIN-037 (the full posting pipeline + reversal + read).

#### ENT-FIN-005 — JournalLine      kind: transactional
BINDINGS: table `FIN_JOURNAL_LINE` · PK `journalLinePk` (DBF-FIN-051) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-051..060 — see DB Alignment Manifest; `directionCode` lookup-backed
(XM-FIN-001); `amount` DB-CHECK'd positive (`CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE`, POL-FIN-005).
DTO MEMBERSHIP: written only as a nested array inside the entry create/build request; no
standalone line endpoint; never independently updated (locked with its header).
DOMAIN RULES: **RULE-FIN-007** (leaf/active account) — QR-FIN-030 — service;
**RULE-FIN-010** (remainder-line rounding) — QR-FIN-028 — service.
CROSS-MODULE: `directionCode` touches XM-FIN-001.
REPOSITORY OPS → written as part of QR-FIN-024/025/034 (SAVE, header+lines in one
transaction); read via QR-FIN-037, QR-FIN-042 (ledger), QR-FIN-043 (statements).

#### ENT-FIN-006 — JournalLineDimension      kind: transactional
BINDINGS: table `FIN_JOURNAL_LINE_DIM` · PK `journalLineDimensionPk` (DBF-FIN-061) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-061..064 — see DB Alignment Manifest.
DTO MEMBERSHIP: nested under each line in the entry create/build request (0..N per line).
DOMAIN RULES: **RULE-FIN-009** (dimension value validity) — QR-FIN-032 — service.
CROSS-MODULE: none.
REPOSITORY OPS → written as part of QR-FIN-024/025/034; read via QR-FIN-044 (dimension report).
<!-- SUB:DATA-DOM-TRANSACTIONAL:END -->

<!-- SUB:DATA-DOM-LOOKUP:START traces=REQ-FIN-004,REQ-FIN-007,REQ-FIN-022,REQ-FIN-025 -->
### SUB — DATA-DOM-LOOKUP (FIN's own config/lookup-kind structural data)

#### ENT-FIN-002 — Dimension      kind: config
BINDINGS: table `FIN_DIMENSION` · PK `dimensionPk` (DBF-FIN-014) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-014..022. DTO: create `{code, nameAr, nameEn}`; no update endpoint (name
edits go through a future v2 if needed — not named in the plan, so not built). DOMAIN
RULES: none scoped alone. REPOSITORY OPS → QR-FIN-007, QR-FIN-008.

#### ENT-FIN-003 — DimensionValue      kind: lookup
BINDINGS: table `FIN_DIMENSION_VALUE` · PK `dimensionValuePk` (DBF-FIN-023) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-023..033 — matches `profile.conventions.entity_defaults.lookup` exactly
(code, nameAr, nameEn, sortOrder, isActiveFl) plus PK/FK/audit. DOMAIN RULES:
**RULE-FIN-002** (duplicate code within dimension) — QR-FIN-010 — service + DB
(`UQ_FIN_DIMENSION_VALUE_DIM_CODE`). REPOSITORY OPS → QR-FIN-009, QR-FIN-010, QR-FIN-011.

#### ENT-FIN-009 — EventTypeRule      kind: config
BINDINGS: table `FIN_EVENT_TYPE_RULE` · PK `eventTypeRulePk` (DBF-FIN-089) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-089..097; `eventTypeCode` lookup-backed (XM-FIN-001). DOMAIN RULES: one
active rule per event type — DB (`UQ_FIN_EVENT_TYPE_RULE_CODE`) + QR-FIN-014. REPOSITORY
OPS → QR-FIN-012, QR-FIN-013, QR-FIN-014, QR-FIN-027 (reused at post time).

#### ENT-FIN-010 — RuleLine      kind: config
BINDINGS: table `FIN_RULE_LINE` · PK `ruleLinePk` (DBF-FIN-098) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-098..108; `accountDerivationTypeCode`/`amountSourceTypeCode`/
`directionCode`/`distributionTypeCode` all lookup-backed (XM-FIN-001). DOMAIN RULES:
**RULE-FIN-003** (exactly one remainder line under percentage distribution) — QR-FIN-016 —
service. REPOSITORY OPS → QR-FIN-015, QR-FIN-016; read as part of QR-FIN-025/028 at
event-entry build time.

#### ENT-FIN-011 — RecurringTemplate      kind: config
BINDINGS: table `FIN_RECURRING_TEMPLATE` · PK `recurringTemplatePk` (DBF-FIN-109) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-109..121; `scheduleTypeCode`/`frequencyCode` lookup-backed (XM-FIN-001).
DOMAIN RULES: none scoped alone (its run posts through the same shared pipeline as any
entry — RULE-FIN-006 through RULE-FIN-010, cited on API-FIN-014). REPOSITORY OPS →
QR-FIN-017, QR-FIN-018, QR-FIN-019.

#### ENT-FIN-012 — RecurringTemplateLine      kind: config
BINDINGS: table `FIN_RECURRING_TEMPLATE_LINE` · PK `recurringTemplateLinePk` (DBF-FIN-122) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-122..129; `directionCode` lookup-backed (XM-FIN-001); `amount` DB-CHECK'd
positive. DOMAIN RULES: none scoped alone. REPOSITORY OPS → written with QR-FIN-018; read
by QR-FIN-019 at run time.

#### ENT-FIN-013 — AllocationRule      kind: config
BINDINGS: table `FIN_ALLOCATION_RULE` · PK `allocationRulePk` (DBF-FIN-130) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-130..138. DOMAIN RULES: none scoped alone. REPOSITORY OPS → QR-FIN-020,
QR-FIN-021, QR-FIN-022.

#### ENT-FIN-014 — AllocationTarget      kind: config
BINDINGS: table `FIN_ALLOCATION_TARGET` · PK `allocationTargetPk` (DBF-FIN-139) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-139..146; `distributionTypeCode` lookup-backed (XM-FIN-001). DOMAIN RULES:
**RULE-FIN-003** (reused — exactly one remainder target under percentage distribution) —
QR-FIN-016 (reused) — service. REPOSITORY OPS → written with QR-FIN-021; read by
QR-FIN-022 at run time.
<!-- SUB:DATA-DOM-LOOKUP:END -->
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-FIN-001,REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028,REQ-FIN-036 -->
## PHASE 3 — SVC-API

API count = 32 ≥ 8 → split by threshold, grouped CRUD / SEARCH / INT.

<!-- SUB:SVC-API-SEARCH:START traces=REQ-FIN-001,REQ-FIN-004,REQ-FIN-007,REQ-FIN-022,REQ-FIN-027,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043 -->
### SUB — SVC-API-SEARCH (read-only)

<!-- API:API-FIN-001:START traces=REQ-FIN-001,DBF-FIN-002,DBF-FIN-003,DBF-FIN-004,DBF-FIN-005 -->
### API-FIN-001 — search accounts
Endpoint: GET /api/v1/fin/accounts · Layers: `AccountController.search`→`AccountService.search`
Request: `code`(LIKE), `nameAr/nameEn`(LIKE), `accountTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AccountResponse>` · `ApiResponse<...>`
Validations: none (read-only) · Errors: `FIN-500`
Orchestration: load (QR-FIN-001) → map → return · Repository: QR-FIN-001 · join NONE · READ_ONLY
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_VIEW` · Localization: nameAr/nameEn returned
<!-- API:API-FIN-001:END -->

<!-- API:API-FIN-005:START traces=REQ-FIN-004,DBF-FIN-015,DBF-FIN-016,DBF-FIN-017 -->
### API-FIN-005 — search dimensions
Endpoint: GET /api/v1/fin/dimensions · Layers: `DimensionController.search`→`DimensionService.search`
Request: `code`(LIKE), paging · Response: 200 · `Page<DimensionResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-007 → map → return · Repository: QR-FIN-007 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-005:END -->

<!-- API:API-FIN-008:START traces=REQ-FIN-005,DBF-FIN-024,DBF-FIN-025,DBF-FIN-026,DBF-FIN-027 -->
### API-FIN-008 — search dimension values
Endpoint: GET /api/v1/fin/dimensions/{id}/values · Layers: `DimensionValueController.search`→`DimensionValueService.search`
Request: path `id`; `code`(LIKE), paging · Response: 200 · `Page<DimensionValueResponse>`
Validations: none · Errors: `FIN-404-DIMENSION`
Orchestration: QR-FIN-011 → map → return · Repository: QR-FIN-011 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-008:END -->

<!-- API:API-FIN-009:START traces=REQ-FIN-007,DBF-FIN-090,DBF-FIN-091,DBF-FIN-092 -->
### API-FIN-009 — search event-type rules
Endpoint: GET /api/v1/fin/event-rules · Layers: `EventTypeRuleController.search`→`EventTypeRuleService.search`
Request: `eventTypeCode`(EXACT), `isActiveFl`(EXACT), paging · Response: 200 · `Page<EventTypeRuleResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-012 → map → return · Repository: QR-FIN-012 · join NONE · READ_ONLY
Security: screen FIN_RULES · `PERM_FIN_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-009:END -->

<!-- API:API-FIN-012:START traces=REQ-FIN-022,DBF-FIN-110,DBF-FIN-111,DBF-FIN-112 -->
### API-FIN-012 — search templates
Endpoint: GET /api/v1/fin/recurring-templates · Layers: `RecurringTemplateController.search`→`RecurringTemplateService.search`
Request: `nameAr/nameEn`(LIKE), `scheduleTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<RecurringTemplateResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-017 → map → return · Repository: QR-FIN-017 · join NONE · READ_ONLY
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-012:END -->

<!-- API:API-FIN-015:START traces=REQ-FIN-025,DBF-FIN-131,DBF-FIN-132,DBF-FIN-133 -->
### API-FIN-015 — search allocation rules
Endpoint: GET /api/v1/fin/allocation-rules · Layers: `AllocationRuleController.search`→`AllocationRuleService.search`
Request: `nameAr/nameEn`(LIKE), `sourceAccountId`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AllocationRuleResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-020 → map → return · Repository: QR-FIN-020 · join NONE · READ_ONLY
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-015:END -->

<!-- API:API-FIN-018:START traces=REQ-FIN-027,DBF-FIN-035,DBF-FIN-036,DBF-FIN-040 -->
### API-FIN-018 — search journal entries
Endpoint: GET /api/v1/fin/journal-entries · Layers: `JournalEntryController.search`→`JournalEntryService.search`
Request: `docNo`(LIKE), `docDate`(DATE_RANGE), `periodId`(EXACT), `statusCode`(EXACT), `journalTypeCode`(EXACT), paging
Response: 200 · `Page<JournalEntryResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-023 → map → return (REQ-FIN-027: unmodified) · Repository: QR-FIN-023 · join NONE · READ_ONLY
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_VIEW` · Localization: descriptionAr/En
<!-- API:API-FIN-018:END -->

<!-- API:API-FIN-022:START traces=REQ-FIN-016,REQ-FIN-027,DBF-FIN-034,DBF-FIN-041 -->
### API-FIN-022 — read entry
Endpoint: GET /api/v1/fin/journal-entries/{id} · Layers: `JournalEntryController.read`→`JournalEntryService.read`
Request: path `id` · Response: 200 · `JournalEntryResponse` with nested lines and their dimensions
Validations: none · Errors: `FIN-404-ENTRY`
Orchestration: QR-FIN-037 → map → return · Repository: QR-FIN-037 · join intra-module (entry→line→line-dim) · READ_ONLY
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_VIEW` · Localization: descriptionAr/En
<!-- API:API-FIN-022:END -->

<!-- API:API-FIN-028:START traces=REQ-FIN-039,REQ-FIN-046,DBF-FIN-054,DBF-FIN-055,DBF-FIN-056 -->
### API-FIN-028 — account ledger
Endpoint: GET /api/v1/fin/reports/account-ledger · Layers: `ReportController.accountLedger`→`ReportService.accountLedger`
Request: `accountId`(EXACT), date range, dimension filters · Response: 200 · running-balance list, each row linking journalEntryId
Validations: none · Errors: `FIN-404-ACCOUNT`
Orchestration: QR-FIN-042 (POSTED lines only, live) → compute running balance → return (POL-FIN-009)
Repository: QR-FIN-042 · join intra-module (line→entry for docDate/status) · READ_ONLY
Security: screen FIN_ACCOUNT_LEDGER · `PERM_FIN_ACCOUNT_LEDGER_VIEW` · Localization: n/a
<!-- API:API-FIN-028:END -->

<!-- API:API-FIN-029:START traces=REQ-FIN-040,REQ-FIN-046,DBF-FIN-005,DBF-FIN-006,DBF-FIN-055 -->
### API-FIN-029 — trial balance
Endpoint: GET /api/v1/fin/reports/trial-balance · Layers: `ReportController.trialBalance`→`ReportService.trialBalance`
Request: `periodId`(EXACT), `accountTypeCode`(EXACT) · Response: 200 · one row per account (debit/credit balance, sign per natureCode — POL-FIN-002)
Validations: RULE-FIN-006 restated as a report-level guarantee (POL-FIN-008: the sums always match because every contributing entry individually balanced — no separate check needed, an invariant by construction)
Errors: `FIN-500`
Orchestration: QR-FIN-043 (POSTED lines only, live, grouped by account) → apply nature sign → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_TRIAL_BALANCE · `PERM_FIN_TRIAL_BALANCE_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-029:END -->

<!-- API:API-FIN-030:START traces=REQ-FIN-041,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-030 — balance sheet
Endpoint: GET /api/v1/fin/reports/balance-sheet · Layers: `ReportController.balanceSheet`→`ReportService.balanceSheet`
Request: `fiscalYearId`(EXACT), `asOfDate` · Response: 200 · grouped ASSET/LIABILITY/EQUITY balances
Validations: none (continuity itself is guaranteed by REQ-FIN-036's opening-entry generation, not re-validated at read time)
Errors: `FIN-500`
Orchestration: QR-FIN-043 (accountTypeCode IN ASSET,LIABILITY,EQUITY) → group → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_BALANCE_SHEET · `PERM_FIN_BALANCE_SHEET_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-030:END -->

<!-- API:API-FIN-031:START traces=REQ-FIN-042,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-031 — income statement
Endpoint: GET /api/v1/fin/reports/income-statement · Layers: `ReportController.incomeStatement`→`ReportService.incomeStatement`
Request: `fiscalYearId`(EXACT), period range · Response: 200 · grouped REVENUE/EXPENSE balances
Validations: none (zero-opening is guaranteed by REQ-FIN-036 closing result accounts to Retained Earnings, not re-validated at read time)
Errors: `FIN-500`
Orchestration: QR-FIN-043 (accountTypeCode IN REVENUE,EXPENSE, scoped to the year/period range) → group → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_INCOME_STATEMENT · `PERM_FIN_INCOME_STATEMENT_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-031:END -->

<!-- API:API-FIN-032:START traces=REQ-FIN-043,DBF-FIN-063,DBF-FIN-064,DBF-FIN-055 -->
### API-FIN-032 — dimension report
Endpoint: GET /api/v1/fin/reports/dimension · Layers: `ReportController.dimensionReport`→`ReportService.dimensionReport`
Request: `dimensionId`(EXACT), `dimensionValueId`(EXACT), `periodId`(EXACT) · Response: 200 · one row per account+dimension-value combination (POL-FIN-011)
Validations: none · Errors: `FIN-404-DIMENSION`
Orchestration: QR-FIN-044 (group by account + dimension value, never base account alone) → return
Repository: QR-FIN-044 · join intra-module (line→line-dim→dimension-value) · READ_ONLY
Security: screen FIN_DIMENSION_REPORTS · `PERM_FIN_DIMENSION_REPORTS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-032:END -->
<!-- SUB:SVC-API-SEARCH:END -->

<!-- SUB:SVC-API-CRUD:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,REQ-FIN-014,REQ-FIN-022,REQ-FIN-025 -->
### SUB — SVC-API-CRUD

<!-- API:API-FIN-002:START traces=REQ-FIN-001,REQ-FIN-002,DBF-FIN-002,DBF-FIN-005,DBF-FIN-006,DBF-FIN-007,DBF-FIN-008 -->
### API-FIN-002 — create account
Endpoint: POST /api/v1/fin/accounts · Layers: `AccountController.create`→`AccountService.create`
Request: `{code, nameAr, nameEn, accountTypeCode, natureCode, parentAccountId?, isLeafFl}`
Response: 201 · `AccountResponse`
Validations: RULE-FIN-001 (leaf requires no children — only relevant if `parentAccountId`
is later given children; at create this only matters when the same call sets a parent
that itself must remain non-leaf — QR-FIN-006 checks the *parent*, not the new row);
uniqueness of code (QR-FIN-005); accountTypeCode/natureCode validated via XM-FIN-001
Errors: `FIN-409-ACCOUNT-DUP`, `FIN-409-PARENT-NOT-LEAF-ELIGIBLE`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookups (XM-FIN-001) → validate uniqueness (QR-FIN-005) → if
parentAccountId given, flip the parent's isLeafFl to false via RULE-FIN-001's inverse
effect (a parent gaining its first child can no longer itself be a leaf) → persist (QR-FIN-002) → return
Repository: QR-FIN-002, QR-FIN-005, QR-FIN-006 · join NONE · READ_WRITE
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-002:END -->

<!-- API:API-FIN-003:START traces=REQ-FIN-002,DBF-FIN-003,DBF-FIN-004,DBF-FIN-008 -->
### API-FIN-003 — update account
Endpoint: PUT /api/v1/fin/accounts/{id} · Layers: `AccountController.update`→`AccountService.update`
Request: `{nameAr, nameEn, isLeafFl}` — excludes {accountPk, code, accountTypeCode, natureCode, isActiveFl, audit}
Response: 200 · `AccountResponse`
Validations: RULE-FIN-002-equivalent — RULE-FIN-001 (full text: DATA-DOM §ENT-FIN-001) —
`isLeafFl=true` rejected if the account has any child (QR-FIN-006)
Errors: `FIN-409-HAS-CHILDREN`, `FIN-404-ACCOUNT`
Orchestration: load → check RULE-FIN-001 if isLeafFl changing to true (QR-FIN-006) → update (QR-FIN-003) → return
Repository: QR-FIN-003, QR-FIN-006 · join NONE · READ_WRITE
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_UPDATE` · Localization: both name fields updatable
<!-- API:API-FIN-003:END -->

<!-- API:API-FIN-004:START traces=REQ-FIN-003,DBF-FIN-009 -->
### API-FIN-004 — deactivate account
Endpoint: DELETE /api/v1/fin/accounts/{id} · Layers: `AccountController.deactivate`→`AccountService.deactivate`
Request: path `id` · Response: 200 · confirmation `{accountPk, isActiveFl: false}`
Validations: none beyond existence · Errors: `FIN-404-ACCOUNT`
Orchestration: load → `Account.deactivate()` → persist (QR-FIN-004) → return (REQ-FIN-019
subsequently rejects any posting to it)
Repository: QR-FIN-004 · join NONE · READ_WRITE
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_UPDATE` · Localization: n/a
<!-- API:API-FIN-004:END -->

<!-- API:API-FIN-006:START traces=REQ-FIN-004,DBF-FIN-015,DBF-FIN-016,DBF-FIN-017 -->
### API-FIN-006 — create dimension
Endpoint: POST /api/v1/fin/dimensions · Layers: `DimensionController.create`→`DimensionService.create`
Request: `{code, nameAr, nameEn}` · Response: 201 · `DimensionResponse`
Validations: uniqueness of code (DB `UQ_FIN_DIMENSION_CODE`, checked friendly at service layer)
Errors: `FIN-409-DIMENSION-DUP`
Orchestration: validate → persist (QR-FIN-008) → return · Repository: QR-FIN-008 · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-006:END -->

<!-- API:API-FIN-007:START traces=REQ-FIN-005,REQ-FIN-006,DBF-FIN-024,DBF-FIN-025,DBF-FIN-028 -->
### API-FIN-007 — create dimension value
Endpoint: POST /api/v1/fin/dimensions/{id}/values · Layers: `DimensionValueController.create`→`DimensionValueService.create`
Request: path `id` (dimensionId); body `{code, nameAr, nameEn, sortOrder}`
Response: 201 · `DimensionValueResponse`
Validations: RULE-FIN-002 (full text: DATA-DOM §ENT-FIN-003) — code unique within the
dimension (QR-FIN-010)
Errors: `FIN-409-DIMVALUE-DUP`, `FIN-404-DIMENSION`
Orchestration: validate dimension exists → check RULE-FIN-002 (QR-FIN-010) → persist (QR-FIN-009) → return
Repository: QR-FIN-009, QR-FIN-010 · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-007:END -->

<!-- API:API-FIN-010:START traces=REQ-FIN-007,REQ-FIN-044,REQ-FIN-045,DBF-FIN-090,DBF-FIN-091,DBF-FIN-092 -->
### API-FIN-010 — create event-type rule
Endpoint: POST /api/v1/fin/event-rules · Layers: `EventTypeRuleController.create`→`EventTypeRuleService.create`
Request: `{eventTypeCode, nameAr, nameEn}` · Response: 201 · `EventTypeRuleResponse`
Validations: eventTypeCode validated via XM-FIN-001; uniqueness of one-active-rule-per-type (QR-FIN-014)
Errors: `FIN-409-RULE-DUP`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookup → check uniqueness (QR-FIN-014) → persist (QR-FIN-013) → return
Repository: QR-FIN-013, QR-FIN-014 · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_CREATE` · Localization: nameAr/nameEn required
Precondition: this endpoint is only reachable once FIN's onboarding has completed —
FIN registered as a module with its screens/actions into SEC (REQ-FIN-044) and FIN's 13
lookup types, including ACCOUNTING_EVENT_TYPE, registered into MDL (REQ-FIN-045); both run
once at deployment, not per request.
<!-- API:API-FIN-010:END -->

<!-- API:API-FIN-011:START traces=REQ-FIN-008,REQ-FIN-009,DBF-FIN-101,DBF-FIN-103,DBF-FIN-105,DBF-FIN-106,DBF-FIN-107 -->
### API-FIN-011 — add rule line
Endpoint: POST /api/v1/fin/event-rules/{id}/lines · Layers: `RuleLineController.create`→`RuleLineService.create`
Request: path `id` (eventTypeRuleId); body `{accountDerivationTypeCode, accountDerivationValue,
amountSourceTypeCode, amountSourceValue?, directionCode, distributionTypeCode, isRemainderFl}`
Response: 201 · `RuleLineResponse`
Validations: RULE-FIN-003 (full text: DATA-DOM §ENT-FIN-010) — exactly one remainder line
once any sibling line is PERCENTAGE-distributed (QR-FIN-016); all four lookup codes
validated via XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-404-RULE`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookups → check RULE-FIN-003 across the rule's existing + new line
(QR-FIN-016) → persist (QR-FIN-015) → return
Repository: QR-FIN-015, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-011:END -->

<!-- API:API-FIN-013:START traces=REQ-FIN-022,DBF-FIN-112,DBF-FIN-113,DBF-FIN-114,DBF-FIN-115 -->
### API-FIN-013 — create template
Endpoint: POST /api/v1/fin/recurring-templates · Layers: `RecurringTemplateController.create`→`RecurringTemplateService.create`
Request: `{nameAr, nameEn, scheduleTypeCode, frequencyCode?, startDate, endDate?, lines: [...]}`
Response: 201 · `RecurringTemplateResponse`
Validations: scheduleTypeCode/frequencyCode/line directionCode validated via XM-FIN-001;
frequencyCode required unless scheduleTypeCode=REVERSING
Errors: `FIN-400-MISSING-FREQUENCY`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate → set nextRunDate=startDate → persist template+lines (QR-FIN-018) → return
Repository: QR-FIN-018 · join NONE · READ_WRITE
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-013:END -->

<!-- API:API-FIN-016:START traces=REQ-FIN-025,DBF-FIN-133,DBF-FIN-142,DBF-FIN-144 -->
### API-FIN-016 — create allocation rule
Endpoint: POST /api/v1/fin/allocation-rules · Layers: `AllocationRuleController.create`→`AllocationRuleService.create`
Request: `{nameAr, nameEn, sourceAccountId, targets: [...]}`
Response: 201 · `AllocationRuleResponse`
Validations: RULE-FIN-003 (reused) — exactly one remainder target when any sibling is
PERCENTAGE (QR-FIN-016, reused); distributionTypeCode validated via XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-404-ACCOUNT`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate → check RULE-FIN-003 across targets (QR-FIN-016) → persist rule+targets (QR-FIN-021) → return
Repository: QR-FIN-021, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-016:END -->

<!-- API:API-FIN-019:START traces=REQ-FIN-014,REQ-FIN-015,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,DBF-FIN-036,DBF-FIN-037,DBF-FIN-038,DBF-FIN-044 -->
### API-FIN-019 — create manual entry
Endpoint: POST /api/v1/fin/journal-entries · Layers: `JournalEntryController.createManual`→`JournalEntryService.createManual`
Request: `{docDate, fiscalYearId, periodId, journalTypeCode="MANUAL", descriptionAr,
descriptionEn, lines: [{accountId, amount, directionCode, descriptionAr?, descriptionEn?,
dimensions: [{dimensionId, dimensionValueId}]}]}` — excludes {journalEntryPk, docNo,
statusCode, postedAt, audit}
Response: 201 · `JournalEntryResponse` (statusCode=POSTED on success)
Validations: RULE-FIN-006 (debit=credit, QR-FIN-029), RULE-FIN-007 (leaf/active accounts,
QR-FIN-030), RULE-FIN-008 (period open, QR-FIN-031), RULE-FIN-009 (dimension valid,
QR-FIN-032) — every failure returned together (REQ-FIN-015), nothing posts if any fails
Errors: `FIN-409-UNBALANCED`, `FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`,
`FIN-409-INVALID-DIMENSION`
Orchestration: generate docNo (numbering engine) → build DRAFT (QR-FIN-024) → validate
(QR-FIN-029..032) → on success: post (QR-FIN-033); on failure: discard the whole attempt
(one transaction, REQ-FIN-015) → return
Repository: QR-FIN-024, QR-FIN-029, QR-FIN-030, QR-FIN-031, QR-FIN-032, QR-FIN-033 · join
NONE · READ_WRITE (one transaction, build-through-post)
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_CREATE` · Localization: descriptionAr/En
<!-- API:API-FIN-019:END -->
<!-- SUB:SVC-API-CRUD:END -->

<!-- SUB:SVC-API-INT:START traces=REQ-FIN-010,REQ-FIN-023,REQ-FIN-024,REQ-FIN-026,REQ-FIN-028,REQ-FIN-031,REQ-FIN-034,REQ-FIN-036,REQ-FIN-037 -->
### SUB — SVC-API-INT (posting-pipeline orchestration and period-control actions)

<!-- API:API-FIN-020:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,DBF-FIN-041,DBF-FIN-090,DBF-FIN-106,DBF-FIN-107 -->
### API-FIN-020 — build event entry (system)
Endpoint: POST /api/v1/fin/journal-entries/from-event · Layers: `EventEntryController.build`→`EventEntryService.build`
Request: the canonical accounting event payload (opaque shape, out-of-scope Event consumer, POL-FIN-020)
Response: 201 · `JournalEntryResponse` (statusCode=POSTED) — or a rejection recorded for operator follow-up (REQ-FIN-013)
Validations: RULE-FIN-004 (duplicate eventReference, QR-FIN-026), RULE-FIN-005 (active
rule exists, QR-FIN-027), RULE-FIN-010 (remainder-line rounding, QR-FIN-028), then the
same RULE-FIN-006/007/008/009 checks as API-FIN-019 (QR-FIN-029..032)
Errors: `FIN-409-DUPLICATE-EVENT`, `FIN-404-NO-ACTIVE-RULE`, `FIN-409-UNBALANCED`,
`FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`, `FIN-409-INVALID-DIMENSION`
Orchestration: check RULE-FIN-004 (QR-FIN-026) → resolve active rule (QR-FIN-027) →
generate docNo → build lines from the rule against the event's fields, computing the
remainder line last (QR-FIN-028, QR-FIN-025) → validate (QR-FIN-029..032) → post (QR-FIN-033) → return
Repository: QR-FIN-025, QR-FIN-026, QR-FIN-027, QR-FIN-028, QR-FIN-029..033 · join NONE ·
READ_WRITE (one transaction, build-through-post)
Security: system-to-system call (the Event consumer's own service principal), gated by
the same interceptor as any authenticated caller · `PERM_FIN_JOURNAL_ENTRIES_CREATE`
Localization: n/a (no free-text description supplied by an event)
<!-- API:API-FIN-020:END -->

<!-- API:API-FIN-014:START traces=REQ-FIN-023,REQ-FIN-024,DBF-FIN-115,DBF-FIN-112 -->
### API-FIN-014 — run template
Endpoint: POST /api/v1/fin/recurring-templates/{id}/run · Layers: `RecurringTemplateController.run`→`RecurringTemplateService.run`
Request: path `id` (or invoked by an internal scheduler with no path — the endpoint is the
same either way) · Response: 201 · `JournalEntryResponse`
Validations: same RULE-FIN-006/007/008/009 checks as API-FIN-019 (the template's own lines
were already balance-checked at API-FIN-013 create time, but re-validated here since
accounts/periods may have changed since)
Errors: same as API-FIN-019
Orchestration: load template (QR-FIN-019) → build entry from its lines (journalTypeCode=
RECURRING) → validate + post (QR-FIN-029..033) → advance nextRunDate per frequencyCode →
if scheduleTypeCode=REVERSING: also build and post the linked reversal in the next period
(REQ-FIN-024, reusing RULE-FIN-011/012 via QR-FIN-034/036) → return
Repository: QR-FIN-019, QR-FIN-024(-style build), QR-FIN-029..033, QR-FIN-034, QR-FIN-036
· join NONE · READ_WRITE
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_UPDATE` (running
a template is modeled as an update-class custom action) · Localization: n/a
<!-- API:API-FIN-014:END -->

<!-- API:API-FIN-017:START traces=REQ-FIN-026,DBF-FIN-133,DBF-FIN-145,DBF-FIN-146 -->
### API-FIN-017 — run allocation rule
Endpoint: POST /api/v1/fin/allocation-rules/{id}/run · Layers: `AllocationRuleController.run`→`AllocationRuleService.run`
Request: path `id` · Response: 201 · `JournalEntryResponse`
Validations: RULE-FIN-010 (remainder guarantee, QR-FIN-028, reused) then RULE-FIN-006/007/008/009
Errors: same family as API-FIN-019, plus `FIN-404-ALLOCATION-RULE`
Orchestration: load rule + targets + current source-account balance (QR-FIN-022) →
distribute per target's distributionTypeCode, remainder target absorbing rounding
(QR-FIN-028) → build entry (journalTypeCode=ALLOCATION) → validate + post (QR-FIN-029..033) → return
Repository: QR-FIN-022, QR-FIN-028, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-017:END -->

<!-- API:API-FIN-021:START traces=REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,DBF-FIN-042,DBF-FIN-043 -->
### API-FIN-021 — reverse entry
Endpoint: POST /api/v1/fin/journal-entries/{id}/reverse · Layers: `JournalEntryController.reverse`→`JournalEntryService.reverse`
Request: path `id` · Response: 201 · `JournalEntryResponse` (the new reversal entry)
Validations: RULE-FIN-013 (must be POSTED, QR-FIN-035); RULE-FIN-012 (period substitution
if original's is closed, QR-FIN-036)
Errors: `FIN-409-NOT-POSTED`, `FIN-404-ENTRY`
Orchestration: load original → check RULE-FIN-013 (QR-FIN-035) → resolve posting period
(original's if Open, else the current open period per RULE-FIN-012, QR-FIN-036) → build
mirrored lines with opposite directions, same amounts (RULE-FIN-011, QR-FIN-034) →
validate + post (QR-FIN-029..033, journalTypeCode=REVERSAL) → set originalEntryId/
reversalEntryId on both rows (bidirectional link) → return
Repository: QR-FIN-034, QR-FIN-035, QR-FIN-036, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_REVERSE` (custom action) · Localization: n/a
<!-- API:API-FIN-021:END -->

<!-- API:API-FIN-023:START traces=REQ-FIN-031,DBF-FIN-066,DBF-FIN-067,DBF-FIN-068,DBF-FIN-077 -->
### API-FIN-023 — create fiscal year
Endpoint: POST /api/v1/fin/fiscal-years · Layers: `FiscalYearController.create`→`FiscalYearService.create`
Request: `{code, startDate, endDate, periodCount}` · Response: 201 · `FiscalYearResponse` with its generated periods
Validations: uniqueness of code
Errors: `FIN-409-YEAR-DUP`
Orchestration: validate → persist year (statusCode=OPEN) + generate periodCount periods,
each statusCode=OPEN (QR-FIN-038) → return
Repository: QR-FIN-038 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CREATE` · Localization: n/a
<!-- API:API-FIN-023:END -->

<!-- API:API-FIN-024:START traces=REQ-FIN-032,DBF-FIN-082 -->
### API-FIN-024 — open period
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/open · Layers: `FiscalPeriodController.open`→`FiscalPeriodService.open`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: current state must be SOFT_CLOSE (§10.2 "re-openable" — Hard Closed is not, RULE-FIN-014)
Errors: `FIN-409-NOT-REOPENABLE`, `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040) → transition (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_UPDATE` · Localization: n/a
<!-- API:API-FIN-024:END -->

<!-- API:API-FIN-025:START traces=REQ-FIN-033,DBF-FIN-082 -->
### API-FIN-025 — soft-close period
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/soft-close · Layers: `FiscalPeriodController.softClose`→`FiscalPeriodService.softClose`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: current state must be OPEN · Errors: `FIN-409-INVALID-TRANSITION`, `FIN-404-PERIOD`
Orchestration: load → transition (QR-FIN-039) → return · Repository: QR-FIN-039 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_UPDATE` · Localization: n/a
<!-- API:API-FIN-025:END -->

<!-- API:API-FIN-026:START traces=REQ-FIN-034,REQ-FIN-035,REQ-FIN-037,REQ-FIN-038,DBF-FIN-082,DBF-FIN-083,DBF-FIN-084 -->
### API-FIN-026 — hard-close period (approval)
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/hard-close · Layers: `FiscalPeriodController.hardClose`→`FiscalPeriodService.hardClose`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: RULE-FIN-014 (not already Hard Closed, QR-FIN-040); RULE-FIN-015 (full text:
DATA-DOM §ENT-FIN-008) — caller must hold `PERM_FIN_PERIODS_CLOSE_APPROVE`, a permission
distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE` (checked by the CORE interceptor plus the
service-layer distinctness read, Phase 1 CORE)
Errors: `FIN-409-NOT-REOPENABLE`(reused message context), `FIN-403-SOD-VIOLATION`, `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040) → check RULE-FIN-015 (SEC role read)
→ transition, set closedBy/closedAt to the approving principal (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` (custom, SoD-gated) · Localization: n/a
<!-- API:API-FIN-026:END -->

<!-- API:API-FIN-027:START traces=REQ-FIN-036,DBF-FIN-069,DBF-FIN-034 -->
### API-FIN-027 — run year-end close
Endpoint: POST /api/v1/fin/fiscal-years/{id}/year-end-close · Layers: `FiscalYearController.yearEndClose`→`FiscalYearService.yearEndClose`
Request: path `id` · Response: 201 · `{closingEntry: JournalEntryResponse, openingEntry: JournalEntryResponse}`
Validations: every period of the year must be HARD_CLOSE (precondition) — `PERM_FIN_PERIODS_CLOSE_APPROVE` required (same SoD gate as API-FIN-026)
Errors: `FIN-409-PERIODS-NOT-CLOSED`, `FIN-404-YEAR`
Orchestration: verify all periods Hard Closed → compute closing balances (QR-FIN-041) →
build + post a closing entry (result accounts → Retained Earnings, journalTypeCode=CLOSING)
→ build + post the next year's opening entry from the resulting balance-sheet balances
(journalTypeCode=OPENING, QR-FIN-041, POL-FIN-010) — CLOSING/OPENING are two values added
to the JOURNAL_TYPE lookup this stage (see Decisions Applied — a data-only, non-breaking
extension, not a new REQ/RULE) → mark FiscalYear statusCode=CLOSED, periods
statusCode=YEAR_END_CLOSE → return
Repository: QR-FIN-041, QR-FIN-029..033 (both generated entries go through the same
validated posting pipeline) · join intra-module · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` · Localization: n/a
<!-- API:API-FIN-027:END -->
<!-- SUB:SVC-API-INT:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-FIN-017 -->
## PHASE 4 — DOC

**API contract summary** (backend self-check only; the frontend stage binds to the real
`api-docs-fin.md` published after implementation): 32 endpoints under `/api/v1/fin`, one
row per API-FIN-001..032 (path/verb/request/response per the API Registry table in the
Plan Index above — not restated a third time here, single-source rule).

**DTO typing constraints**: every lookup-backed field (`accountTypeCode`, `natureCode`,
`directionCode`, `journalTypeCode`, `statusCode`, `eventTypeCode`,
`accountDerivationTypeCode`, `amountSourceTypeCode`, `distributionTypeCode`,
`scheduleTypeCode`, `frequencyCode`) is `String`, never a Java enum; `docNo` never appears
in any create/update request body, always in every response.

**Pagination + filter standard**: identical to SEC's/MDL's own Phase 1 CORE.
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=REQ-FIN-001 -->
## PHASE 5 — INT-C (cross-module consume)

One `XM-*` row (XM-FIN-001), below the split threshold (1 < 5) — no SUB opened.

<!-- XM:XM-FIN-001:START traces=REQ-FIN-001,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-018,REQ-FIN-022,REQ-FIN-025,REQ-FIN-031 -->
### XM-FIN-001 — validate/read lookup-backed codes against MDL
Target        : MDL · ENT-MDL-001/002 (LookupType/LookupValue) · classification SOFT-READ
Interface     : REST call — `GET /api/v1/mdl/lookups?type={key}` (API-MDL-011) for every
one of FIN's 13 owned keys, called at the point each lookup-backed field is written or offered as a select-list
Contract      : data required = the submitted code exists as an active value under the
named type; fallback if absent = reject with `FIN-400-INVALID-LOOKUP`; retry = none
(synchronous, user-facing call — a transient MDL outage surfaces as `FIN-503`); idempotency
= read-only, naturally idempotent
Blocks        : none DEFERRED — MDL v1 is already gated (pass-1 APPROVE); ACTIVE from the
moment FIN v1 is created
<!-- XM:XM-FIN-001:END -->

FIN's dependency on SEC (identity/authorization for every request, and FIN's own
self-registration into SEC) is not a formal `XM` row — ADR-FIN-001 (carried from P2).
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-FIN-001 -->
## PHASE 6 — INT-R (cross-module resolve)

| XM | Status | Workaround (if not READY/ACTIVE) |
|---|---|---|
| XM-FIN-001 | ACTIVE | not applicable — target already gated |

No DEFERRED row exists. FIN is the third and last module of this batch
(GENERATION-INSTRUCTIONS.md §3); the next module to consume FIN (first candidate: PRC or
any future Tier-2/3 module needing accounting integration) is out of this batch's scope —
`XM-INBOUND-STUB-3` names FIN as the eventual target, formal id assigned by that module's
own P2 when it exists.
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=REQ-FIN-038,REQ-FIN-044 -->
## PHASE 7 — SEC-BE (security, backend half)

| Screen (page code) | VIEW | CREATE | UPDATE | DELETE | Custom |
|---|---|---|---|---|---|
| FIN_ACCOUNTS | ✓ (API-FIN-001) | ✓ (API-FIN-002) | ✓ (API-FIN-003) | ✓ deactivate (API-FIN-004) | — |
| FIN_DIMENSIONS | ✓ (API-FIN-005,008) | ✓ (API-FIN-006,007) | — | — | — |
| FIN_RULES | ✓ (API-FIN-009) | ✓ (API-FIN-010) | ✓ (API-FIN-011, add line) | — | — |
| FIN_RECURRING_TEMPLATES | ✓ (API-FIN-012) | ✓ (API-FIN-013) | ✓ (API-FIN-014, run) | — | — |
| FIN_ALLOCATION_RULES | ✓ (API-FIN-015) | ✓ (API-FIN-016) | ✓ (API-FIN-017, run) | — | — |
| FIN_JOURNAL_ENTRIES | ✓ (API-FIN-018,022) | ✓ (API-FIN-019,020) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, API-FIN-021) |
| FIN_PERIODS | ✓ | ✓ (API-FIN-023, year) | ✓ (API-FIN-024,025) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE`, API-FIN-026,027 — RULE-FIN-015 SoD) |
| FIN_ACCOUNT_LEDGER | ✓ (API-FIN-028) | — | — | — | — |
| FIN_TRIAL_BALANCE | ✓ (API-FIN-029) | — | — | — | — |
| FIN_BALANCE_SHEET | ✓ (API-FIN-030) | — | — | — | — |
| FIN_INCOME_STATEMENT | ✓ (API-FIN-031) | — | — | — | — |
| FIN_DIMENSION_REPORTS | ✓ (API-FIN-032) | — | — | — | — |

**Seed data** (REQ-FIN-044): 12 SEC_PAGES rows registered via SEC's screen-registration
endpoint at FIN onboarding; one action row per action above via SEC's action-registration
endpoint, following `PERM_<PAGE_CODE>_<ACTION>` — including the two custom actions
(`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, `PERM_FIN_PERIODS_CLOSE_APPROVE`).

**SoD enforcement (RULE-FIN-015, POL-FIN-016)**: `PERM_FIN_PERIODS_CLOSE_APPROVE` and
`PERM_FIN_JOURNAL_ENTRIES_CREATE` must never be held by the same role by platform
convention (an administrative guideline enforced by role design, not a database
constraint — SEC's RBAC model grants permissions per role, and FIN's service layer
additionally checks at hard-close/year-end-close time that no single *user* holds both,
per role union, Phase 1 CORE).

**Gateway**: every non-VIEW permission requires VIEW on the same screen first (platform
convention, SEC's own interceptor — not restated as a FIN-owned RULE).

**Forbidden responses**: `FIN-403-FORBIDDEN` / `FIN-403-SOD-VIOLATION` map through the
same `LocalizedException` envelope as every other module.
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-FIN-017 -->
## PHASE 8 — ALIGN-BE

See Alignment self-check (ALIGN) below.
<!-- PHASE:ALIGN-BE:END -->

## Error Catalog — FIN v1

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `FIN-{http}[-{SLUG}]`.

| code | RULE / PLATFORM-STD | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| FIN-409-ACCOUNT-DUP | PLATFORM-STD | API-FIN-002 | 409 | duplicate account code | رمز الحساب مستخدم بالفعل | Account code already in use |
| FIN-409-PARENT-NOT-LEAF-ELIGIBLE | RULE-FIN-001 | API-FIN-002 | 409 | parent account cannot remain a leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-400-INVALID-LOOKUP | PLATFORM-STD (XM-FIN-001) | many | 400 | submitted code not found in MDL | القيمة المُدخلة غير صالحة | The submitted value is not valid |
| FIN-409-HAS-CHILDREN | RULE-FIN-001 | API-FIN-003 | 409 | marking a parent as leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-404-ACCOUNT | PLATFORM-STD | API-FIN-003, 004, 028 | 404 | unknown account id | الحساب غير موجود | Account not found |
| FIN-409-DIMENSION-DUP | PLATFORM-STD | API-FIN-006 | 409 | duplicate dimension code | رمز البُعد مستخدم بالفعل | Dimension code already in use |
| FIN-409-DIMVALUE-DUP | RULE-FIN-002 | API-FIN-007 | 409 | duplicate code within dimension | هذا الرمز مستخدم بالفعل ضمن هذا البُعد | This code is already used within this dimension |
| FIN-404-DIMENSION | PLATFORM-STD | API-FIN-007, 008, 032 | 404 | unknown dimension id | البُعد غير موجود | Dimension not found |
| FIN-409-RULE-DUP | PLATFORM-STD (§6.4) | API-FIN-010 | 409 | event type already has an active rule | يوجد بالفعل قاعدة نشطة لهذا النوع | An active rule already exists for this event type |
| FIN-409-REMAINDER-COUNT | RULE-FIN-003 | API-FIN-011, 016 | 409 | wrong remainder-line/target count | يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي | Exactly one remainder line is required when any percentage distribution is present |
| FIN-404-RULE | PLATFORM-STD | API-FIN-011 | 404 | unknown event-type rule id | القاعدة غير موجودة | Rule not found |
| FIN-400-MISSING-FREQUENCY | PLATFORM-STD | API-FIN-013 | 400 | recurring template with no frequency | يلزم تحديد التكرار للقالب المتكرر | A frequency is required for a recurring template |
| FIN-404-ALLOCATION-RULE | PLATFORM-STD | API-FIN-017 | 404 | unknown allocation rule id | قاعدة التوزيع غير موجودة | Allocation rule not found |
| FIN-409-UNBALANCED | RULE-FIN-006 | API-FIN-019, 020, 014, 017 | 409 | debits ≠ credits | القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن | The entry is unbalanced — total debits do not equal total credits |
| FIN-409-NOT-POSTABLE-ACCOUNT | RULE-FIN-007 | API-FIN-019, 020, 014, 017 | 409 | non-leaf/inactive account | الحساب المستهدف لا يقبل ترحيلاً مباشرًا | The target account does not accept direct posting |
| FIN-409-PERIOD-NOT-OPEN | RULE-FIN-008 | API-FIN-019, 020, 014, 017 | 409 | period not Open at post | الفترة المستهدفة غير مفتوحة | The target period is not open |
| FIN-409-INVALID-DIMENSION | RULE-FIN-009 | API-FIN-019, 020, 014, 017 | 409 | invalid/inactive dimension value | قيمة البُعد غير صالحة | The dimension value is invalid |
| FIN-409-DUPLICATE-EVENT | RULE-FIN-004 | API-FIN-020 | 409 | repeated eventReference | تم بالفعل ترحيل قيد لهذا المرجع | An entry for this event reference has already been posted |
| FIN-404-NO-ACTIVE-RULE | RULE-FIN-005 | API-FIN-020 | 404 | no active rule for event type | لا توجد قاعدة نشطة لهذا النوع من الأحداث | No active rule exists for this event type |
| FIN-409-NOT-POSTED | RULE-FIN-013 | API-FIN-021 | 409 | reversing a non-posted entry | لا يمكن عكس قيد غير مُرحَّل | A non-posted entry cannot be reversed |
| FIN-404-ENTRY | PLATFORM-STD | API-FIN-021, 022 | 404 | unknown entry id | القيد غير موجود | Entry not found |
| FIN-409-YEAR-DUP | PLATFORM-STD | API-FIN-023 | 409 | duplicate fiscal year code | رمز السنة المالية مستخدم بالفعل | Fiscal year code already in use |
| FIN-409-NOT-REOPENABLE | RULE-FIN-014 | API-FIN-024, 026 | 409 | period Hard Closed | الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها | The period is hard-closed and cannot be reopened |
| FIN-409-INVALID-TRANSITION | PLATFORM-STD | API-FIN-025 | 409 | period not in the expected state | لا يمكن تنفيذ هذا الانتقال من الحالة الحالية | This transition is not allowed from the current status |
| FIN-403-SOD-VIOLATION | RULE-FIN-015 | API-FIN-026, 027 | 403 | close-approver also holds entry-creation permission | صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود | The close-approval permission is separate from the entry-creation permission |
| FIN-404-PERIOD | PLATFORM-STD | API-FIN-024, 025, 026 | 404 | unknown period id | الفترة غير موجودة | Period not found |
| FIN-409-PERIODS-NOT-CLOSED | PLATFORM-STD (§10.4 precondition) | API-FIN-027 | 409 | not every period Hard Closed | يجب إغلاق كل الفترات إغلاقًا صارمًا أولًا | Every period must be hard-closed first |
| FIN-404-YEAR | PLATFORM-STD | API-FIN-027 | 404 | unknown fiscal year id | السنة المالية غير موجودة | Fiscal year not found |
| FIN-403-FORBIDDEN | PLATFORM-STD (CORE interceptor) | every secured API | 403 | missing module/screen/action grant | غير مصرح بهذا الإجراء | You are not authorized to perform this action |
| FIN-400-INVALID-SORT | PLATFORM-STD | every search API | 400 | unrecognized sort field | حقل الترتيب غير معروف | Unrecognized sort field |
| FIN-503 | PLATFORM-STD (MDL unreachable) | any lookup-validating API | 503 | XM-FIN-001 call failed | تعذّر التحقق من القيمة المرجعية مؤقتًا | Could not verify the reference value right now |
| FIN-500 | PLATFORM-STD (infrastructure) | any | 500 | unhandled server error | حدث خطأ في الخادم | A server error occurred |

Every PLATFORM-STD row follows SEC's ADR-SEC-002 umbrella convention, cited (not re-derived).

## Alignment self-check (ALIGN) — FIN v1

```
TRACEABILITY      ✓ every API-*/QR-*/RULE-*/DBF-*/XM-* used in a phase appears in the Plan Index; every PHASE/SUB/atom carries traces=; every traces target exists upstream (REQ-FIN-001..046, DBF-FIN-001..146 all defined in srs/db-script)
BINDING (§2A)     ✓ no placeholder; every column cites a DBF; every RULE message present in ar+en; business code (docNo) format explicit with generation source
MANIFEST (§4)     ✓ only the mandated columns; all 146 DBF listed; 12 columns note XM-FIN-001 (SOFT-READ, never ⏸/blocking)
QRC (§5)          ✓ every API with a DB operation has ≥1 QR; no join for a lookup label; exact generation object named (Phase 1 CORE)
API (R3)          ✓ every RULE in a Validations line has a catalog row; platform errors carry RULE=PLATFORM-STD (SEC's ADR-SEC-002 convention); create/update requests exclude PK/audit/system fields (docNo, statusCode, postedAt); business code (docNo) always in responses, never in create/update bodies
CROSS-MODULE      ✓ 1 XM from db-script, 1 placed (XM-FIN-001), 0 mismatched; ACTIVE status correct; inbound stub XM-INBOUND-STUB-3 notation
SECURITY (R7)     ✓ every secured API declares its PERM_*; ERP-4 (every mutation endpoint declares its PERM_*): checked — every POST/PUT/PATCH/DELETE API above states one, including the two custom SoD-relevant actions
CORE (R1)         ✓ layers, domain placement, error signalling (`FIN-{http}[-{SLUG}]`), type mapping (incl. the NUMERIC→Integer governance note) all declared
DECISIONS         ✓ ADR-FIN-001 (carried from P2) cited; one new DEFAULT this stage (JOURNAL_TYPE gains CLOSING/OPENING, data-only, non-breaking); no BLOCKED ADR
ACCOUNTING §12    ✓ all 14 must-honor points traced: (1) RULE-FIN-006 · (2) POL-FIN-002/API-FIN-029 sign presentation · (3) RULE-FIN-007 · (4) RULE-FIN-008 · (5) CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE + directionCode · (6) RULE-FIN-003/010 · (7) RULE-FIN-011 · (8) API-FIN-029 (balances by construction) · (9) every report QR reads POSTED lines live, no stored balance column anywhere in db-script-fin.md · (10) REQ-FIN-036/RULE for continuity · (11) RULE-FIN-009 + QR-FIN-044 dimension grouping · (12) RULE-FIN-004 · (13) RULE-FIN-016 lock + no DELETE mapping anywhere · (14) POL-FIN-014, no host-specific branch anywhere in this plan
RESULT            PASSED ✓ — 0 findings
```

**Coverage — ENT/DBF → phases → QR → XM**: every ENT-FIN-001..014 appears in exactly one
DATA-DOM entity block with ≥1 QR cited under REPOSITORY OPS; every DBF-FIN-001..146
appears in the DB Alignment Manifest and its owning entity's block; XM-FIN-001 appears in
INT-C, INT-R and every lookup-backed field's manifest row.

**Coverage — RULE → API → catalog code**: RULE-FIN-001→API-FIN-002/003→
FIN-409-PARENT-NOT-LEAF-ELIGIBLE/FIN-409-HAS-CHILDREN · RULE-FIN-002→API-FIN-007→
FIN-409-DIMVALUE-DUP · RULE-FIN-003→API-FIN-011/016→FIN-409-REMAINDER-COUNT ·
RULE-FIN-004→API-FIN-020→FIN-409-DUPLICATE-EVENT · RULE-FIN-005→API-FIN-020→
FIN-404-NO-ACTIVE-RULE · RULE-FIN-006→API-FIN-019/020/014/017→FIN-409-UNBALANCED ·
RULE-FIN-007→(same APIs)→FIN-409-NOT-POSTABLE-ACCOUNT · RULE-FIN-008→(same)→
FIN-409-PERIOD-NOT-OPEN · RULE-FIN-009→(same)→FIN-409-INVALID-DIMENSION ·
RULE-FIN-010→API-FIN-020/014/017→(no distinct code — success-path computation) ·
RULE-FIN-011→API-FIN-021→(no distinct code — success-path build) ·
RULE-FIN-012→API-FIN-021→(no distinct code — success-path period substitution) ·
RULE-FIN-013→API-FIN-021→FIN-409-NOT-POSTED · RULE-FIN-014→API-FIN-024/026→
FIN-409-NOT-REOPENABLE · RULE-FIN-015→API-FIN-026/027→FIN-403-SOD-VIOLATION ·
RULE-FIN-016→(every posted-entry endpoint)→(enforced by omission, no code needed — no
UPDATE/DELETE mapping exists on a POSTED row).

**Coverage — XM → status → blocks → workaround**: XM-FIN-001 → ACTIVE → blocks none → no
workaround needed.

## QR id definitions (cross-reference index — full detail in Query Reference Catalog above)
**QR-FIN-001** — FIND_BY_CRITERIA search accounts [ENT-FIN-001, API-FIN-001]
**QR-FIN-002** — SAVE create account [ENT-FIN-001, API-FIN-002]
**QR-FIN-003** — UPDATE update account [ENT-FIN-001, API-FIN-003]
**QR-FIN-004** — UPDATE deactivate account [ENT-FIN-001, API-FIN-004]
**QR-FIN-005** — EXISTS account code unique [ENT-FIN-001, API-FIN-002]
**QR-FIN-006** — EXISTS account has no children (RULE-FIN-001) [ENT-FIN-001, API-FIN-002, API-FIN-003]
**QR-FIN-007** — FIND_BY_CRITERIA search dimensions [ENT-FIN-002, API-FIN-005]
**QR-FIN-008** — SAVE create dimension [ENT-FIN-002, API-FIN-006]
**QR-FIN-009** — SAVE create dimension value [ENT-FIN-003, API-FIN-007]
**QR-FIN-010** — EXISTS dimension value code unique within dimension (RULE-FIN-002) [ENT-FIN-003, API-FIN-007]
**QR-FIN-011** — FIND_BY_CRITERIA search dimension values [ENT-FIN-003, API-FIN-008]
**QR-FIN-012** — FIND_BY_CRITERIA search event-type rules [ENT-FIN-009, API-FIN-009]
**QR-FIN-013** — SAVE create event-type rule [ENT-FIN-009, API-FIN-010]
**QR-FIN-014** — EXISTS one active rule per event type [ENT-FIN-009, API-FIN-010]
**QR-FIN-015** — SAVE add rule line [ENT-FIN-010, API-FIN-011]
**QR-FIN-016** — EXISTS remainder-line/target count (RULE-FIN-003) [ENT-FIN-010, ENT-FIN-014, API-FIN-011, API-FIN-016]
**QR-FIN-017** — FIND_BY_CRITERIA search templates [ENT-FIN-011, API-FIN-012]
**QR-FIN-018** — SAVE create template with lines [ENT-FIN-011, ENT-FIN-012, API-FIN-013]
**QR-FIN-019** — FIND_ONE load template due to run [ENT-FIN-011, API-FIN-014]
**QR-FIN-020** — FIND_BY_CRITERIA search allocation rules [ENT-FIN-013, API-FIN-015]
**QR-FIN-021** — SAVE create allocation rule with targets [ENT-FIN-013, ENT-FIN-014, API-FIN-016]
**QR-FIN-022** — FIND_ONE load allocation rule + source balance [ENT-FIN-013, API-FIN-017]
**QR-FIN-023** — FIND_BY_CRITERIA search journal entries [ENT-FIN-004, API-FIN-018]
**QR-FIN-024** — SAVE build manual entry (DRAFT) [ENT-FIN-004, ENT-FIN-005, ENT-FIN-006, API-FIN-019]
**QR-FIN-025** — SAVE build event entry (DRAFT) [ENT-FIN-004, ENT-FIN-005, ENT-FIN-006, API-FIN-020]
**QR-FIN-026** — EXISTS duplicate eventReference (RULE-FIN-004) [ENT-FIN-004, API-FIN-020]
**QR-FIN-027** — EXISTS active rule for event type (RULE-FIN-005) [ENT-FIN-009, API-FIN-020]
**QR-FIN-028** — AGGREGATE compute remainder-line amount (RULE-FIN-010) [ENT-FIN-005, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-029** — EXISTS debits=credits (RULE-FIN-006) [ENT-FIN-005, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-030** — EXISTS every line account leaf+active (RULE-FIN-007) [ENT-FIN-001, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-031** — EXISTS period open at post (RULE-FIN-008) [ENT-FIN-008, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-032** — EXISTS every dimension value valid+active (RULE-FIN-009) [ENT-FIN-006, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-033** — UPDATE post entry DRAFT→POSTED [ENT-FIN-004, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-034** — SAVE build reversal entry (RULE-FIN-011) [ENT-FIN-004, ENT-FIN-005, ENT-FIN-006, API-FIN-021]
**QR-FIN-035** — EXISTS original entry is POSTED (RULE-FIN-013) [ENT-FIN-004, API-FIN-021]
**QR-FIN-036** — FIND_ONE current open period for reversal (RULE-FIN-012) [ENT-FIN-008, API-FIN-021]
**QR-FIN-037** — FIND_ONE read one entry with lines [ENT-FIN-004, API-FIN-022]
**QR-FIN-038** — SAVE create fiscal year + periods [ENT-FIN-007, ENT-FIN-008, API-FIN-023]
**QR-FIN-039** — UPDATE open/soft-close/hard-close period [ENT-FIN-008, API-FIN-024, API-FIN-025, API-FIN-026]
**QR-FIN-040** — EXISTS period not already Hard Closed (RULE-FIN-014) [ENT-FIN-008, API-FIN-024, API-FIN-026]
**QR-FIN-041** — AGGREGATE year-end closing/opening balances [ENT-FIN-004, ENT-FIN-005, API-FIN-027]
**QR-FIN-042** — FIND_BY_CRITERIA account ledger running balance [ENT-FIN-005, API-FIN-028]
**QR-FIN-043** — AGGREGATE trial balance / balance sheet / income statement account balances [ENT-FIN-005, API-FIN-029, API-FIN-030, API-FIN-031]
**QR-FIN-044** — AGGREGATE dimension report [ENT-FIN-005, ENT-FIN-006, API-FIN-032]

## XM id definitions
**XM-FIN-001** — SOFT-READ every FIN lookup-backed column → MDL_LOOKUP_VALUE [REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031]

## Registry content
See `registry-exec-be-fin.md`.
══════════════════════════════════════════════════════════════════
