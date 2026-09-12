<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
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
RULES         17 — RULE-FIN-001..017 (RULE-FIN-017, fiscal-year/period/docDate coherence,
              added during SVC-API and carried back into srs-fin.md §A5), all 14 §12
              must-honor points covered (see ALIGN)
SCREENS       12 — SCR-REQ-FIN-001..012
PERMISSIONS   12 secured page codes + PERM_<PAGE_CODE>_<ACTION>, gateway VIEW, plus the
              custom `PERM_FIN_PERIODS_CLOSE_APPROVE` (RULE-FIN-015 SoD)
LOOKUPS       13 keys, all FIN-owned, registered into MDL (SRS A6) — none CHECK-constrained
              locally (unlike SEC's ADR-SEC-001; MDL is already gated)
BUSINESS CODE JournalEntry.docNo — system-generated `JV-{fiscalYearCode}-{NNNNNN}`
              (e.g. JV-2026-000123) by a FIN-local generator in com.erp.fin; counter
              scoped per fiscalYearId, restarts at 000001 each fiscal year, single
              counter across all journal types; unique per fiscalYearId
              (UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO), read-only after create
── FROM db-script ────────────────────────────────────────────────────────
TABLES        14 tables, FIN_ACCOUNT … FIN_ALLOCATION_TARGET
PK GENERATION every table: an explicit `SEQ_<TABLE>` sequence (V22 BLOCK 1) — a deliberate,
              documented deviation from db-script's `GENERATED ALWAYS AS IDENTITY`, required by
              build-create-entity A.1.3/A.1.4 and matching SEC/MDL/CU/NOTIF/FILE
COLUMNS       147 DBF-FIN-001..147
CONSTRAINTS   PK_*, UQ_*, CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE (POL-FIN-005), FK_*; INDEXES IDX_*
XM            1 — XM-FIN-001 SOFT-READ → MDL_LOOKUP_VALUE, status ACTIVE. XM-FIN-002
              (READ → SEC user directory, SecUserDirectoryApi) was assigned at ALIGN-BE and
              RETIRED 2026-09-12 with the deletion of FinSeparationOfDutiesService — INT-C
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   LookupType/LookupValue (MDL) via XM-FIN-001; SEC's identity/
                           authorization for every request, and FIN's self-registration into
                           SEC, consumed as platform-standard integration, not an XM row
                           (ADR-FIN-001 — unchanged). SEC's user→permission read model
                           (SecUserDirectoryApi) was consumed via XM-FIN-002 until
                           2026-09-12 and is not consumed any more
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
| ENT-FIN-004 | JournalEntry | FIN_JOURNAL_ENTRY | **docNo** (`JV-{fiscalYearCode}-{NNNNNN}`, FIN-local generator) | create (4 sources), read, search, reverse |
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

**FIELD REGISTRY** — see DB Alignment Manifest below (147 rows; property = camelCase of the
db-script column, per the same 1:1 transformation used for SEC/MDL — not restated as a
separate lighter table here given the row count, per this stage's own economy: the
Manifest already carries property/type/status, and read-only is uniformly: **Yes** for
every PK, every audit column, every system-timestamp column (postedAt, closedAt/closedBy,
createdAt-only child rows); **No** for every business-input field named in each entity's
SRS A3 "Required" column. The DB Alignment Manifest is the single canonical binding.

**API REGISTRY**
| API | Operation | Verb | Path | Traces (REQ) |
|---|---|---|---|---|
| API-FIN-001 | search accounts | POST | /api/v1/fin/accounts/search | REQ-FIN-001 |
| API-FIN-002 | create account | POST | /api/v1/fin/accounts | REQ-FIN-001, REQ-FIN-002 |
| API-FIN-003 | update account | PUT | /api/v1/fin/accounts/{id} | REQ-FIN-002 |
| API-FIN-004 | deactivate account | PUT | /api/v1/fin/accounts/{id}/deactivate | REQ-FIN-003 |
| API-FIN-005 | search dimensions | POST | /api/v1/fin/dimensions/search | REQ-FIN-004 |
| API-FIN-006 | create dimension | POST | /api/v1/fin/dimensions | REQ-FIN-004 |
| API-FIN-007 | create dimension value | POST | /api/v1/fin/dimensions/{id}/values | REQ-FIN-005, REQ-FIN-006 |
| API-FIN-008 | search dimension values | POST | /api/v1/fin/dimensions/values/search | REQ-FIN-005 |
| API-FIN-009 | search event-type rules | POST | /api/v1/fin/event-rules/search | REQ-FIN-007 |
| API-FIN-010 | create event-type rule | POST | /api/v1/fin/event-rules | REQ-FIN-007 |
| API-FIN-011 | add rule line | POST | /api/v1/fin/event-rules/{id}/lines | REQ-FIN-008, REQ-FIN-009 |
| API-FIN-012 | search templates | POST | /api/v1/fin/recurring-templates/search | REQ-FIN-022 |
| API-FIN-013 | create template | POST | /api/v1/fin/recurring-templates | REQ-FIN-022 |
| API-FIN-014 | run template | POST | /api/v1/fin/recurring-templates/{id}/run | REQ-FIN-023, REQ-FIN-024 |
| API-FIN-015 | search allocation rules | POST | /api/v1/fin/allocation-rules/search | REQ-FIN-025 |
| API-FIN-016 | create allocation rule | POST | /api/v1/fin/allocation-rules | REQ-FIN-025 |
| API-FIN-017 | run allocation rule | POST | /api/v1/fin/allocation-rules/{id}/run | REQ-FIN-026 |
| API-FIN-018 | search journal entries | POST | /api/v1/fin/journal-entries/search | REQ-FIN-027 |
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

**QRC SUMMARY** — 49 QR ids, QR-FIN-001..049 (045-049 assigned at ALIGN-BE to queries that
were implemented but uncatalogued) — see Query Reference Catalog below.

**DB ALIGNMENT** — see manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 1 live (XM-FIN-001, SOFT-READ → MDL, ACTIVE); XM-FIN-002 (READ → SEC) RETIRED 2026-09-12
**SECURITY** — 12 secured screens, data-driven role grants + 1 custom permission (close-approve, `PERM_FIN_PERIODS_CLOSE_APPROVE` — the distinct permission RULE-FIN-015 requires; the service-layer SoD check that once sat behind it was removed 2026-09-12, see SEC-BE)

## DB Alignment Manifest — FIN v1
All 147 rows: **status ✓ (aligned)**; XM populated only on lookup-backed columns (16
columns across 10 tables touch XM-FIN-001, noted individually below — a SOFT-READ, never
blocking; the count read 12/8 until ALIGN-BE recounted it against V22's 16 XM-FIN-001
`COMMENT ON COLUMN` lines). XM-FIN-002 bound no column — it was a service-to-service read of
SEC's user directory, not a lookup-backed value — so it carries no row in this manifest and
never did; it was retired on 2026-09-12 in any case.

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
| DBF-FIN-098 | ENT-FIN-010 | ruleLinePk | Long | — |
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
| DBF-FIN-109 | ENT-FIN-011 | recurringTemplatePk | Long | — |
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
| DBF-FIN-122 | ENT-FIN-012 | recurringTemplateLinePk | Long | — |
| DBF-FIN-123 | ENT-FIN-012 | recurringTemplateId | Long | — |
| DBF-FIN-124 | ENT-FIN-012 | lineNo | Integer | — |
| DBF-FIN-125 | ENT-FIN-012 | accountId | Long | — |
| DBF-FIN-126 | ENT-FIN-012 | amount | BigDecimal | — |
| DBF-FIN-127 | ENT-FIN-012 | directionCode | String | XM-FIN-001 |
| DBF-FIN-128 | ENT-FIN-012 | dimensionValueId | Long | — |
| DBF-FIN-129 | ENT-FIN-012 | createdAt | Instant | — |
| DBF-FIN-130 | ENT-FIN-013 | allocationRulePk | Long | — |
| DBF-FIN-131 | ENT-FIN-013 | nameAr | String | — |
| DBF-FIN-132 | ENT-FIN-013 | nameEn | String | — |
| DBF-FIN-133 | ENT-FIN-013 | sourceAccountId | Long | — |
| DBF-FIN-134 | ENT-FIN-013 | isActiveFl | Boolean | — |
| DBF-FIN-135 | ENT-FIN-013 | createdBy | String | — |
| DBF-FIN-136 | ENT-FIN-013 | createdAt | Instant | — |
| DBF-FIN-137 | ENT-FIN-013 | updatedBy | String | — |
| DBF-FIN-138 | ENT-FIN-013 | updatedAt | Instant | — |
| DBF-FIN-139 | ENT-FIN-014 | allocationTargetPk | Long | — |
| DBF-FIN-140 | ENT-FIN-014 | allocationRuleId | Long | — |
| DBF-FIN-141 | ENT-FIN-014 | lineNo | Integer | — |
| DBF-FIN-142 | ENT-FIN-014 | targetAccountId | Long | — |
| DBF-FIN-143 | ENT-FIN-014 | dimensionValueId | Long | — |
| DBF-FIN-144 | ENT-FIN-014 | distributionTypeCode | String | XM-FIN-001 |
| DBF-FIN-145 | ENT-FIN-014 | distributionValue | BigDecimal | — |
| DBF-FIN-146 | ENT-FIN-014 | isRemainderFl | Boolean | — |
| DBF-FIN-147 | ENT-FIN-001 | isRetainedEarningsFl | Boolean | — |

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
| QR-FIN-016 | EXISTS | API-FIN-011, API-FIN-016 | ENT-FIN-010, ENT-FIN-014 | RULE-FIN-003 | exactly one remainder line/target when a percentage distribution exists (scope widened here to match the id definition below and the code) |
| QR-FIN-017 | FIND_BY_CRITERIA | API-FIN-012 | ENT-FIN-011 | search | search templates |
| QR-FIN-018 | SAVE | API-FIN-013 | ENT-FIN-011, ENT-FIN-012 | create | create template with lines |
| QR-FIN-019 | FIND_ONE | API-FIN-014 | ENT-FIN-011 | run | load the template to run, by id (inherited `findById`; no due-date selection query exists — FIN exposes no scheduler endpoint) |
| QR-FIN-020 | FIND_BY_CRITERIA | API-FIN-015 | ENT-FIN-013 | search | search allocation rules |
| QR-FIN-021 | SAVE | API-FIN-016 | ENT-FIN-013, ENT-FIN-014 | create | create allocation rule with targets |
| QR-FIN-022 | FIND_ONE | API-FIN-017 | ENT-FIN-013 | run | load allocation rule + current source balance (via QR-FIN-043 — the shared balance aggregation; the earlier citation of QR-FIN-040, the hard-closed-period check, was wrong) |
| QR-FIN-023 | FIND_BY_CRITERIA | API-FIN-018 | ENT-FIN-004 | search | search journal entries |
| QR-FIN-024 | SAVE | API-FIN-019 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build manual entry (DRAFT) |
| QR-FIN-025 | SAVE | API-FIN-020 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build event entry (DRAFT) from rule |
| QR-FIN-026 | EXISTS | API-FIN-020 | ENT-FIN-004 | RULE-FIN-004 | duplicate eventReference |
| QR-FIN-027 | EXISTS | API-FIN-020 | ENT-FIN-009 | RULE-FIN-005 | active rule exists for event type |
| QR-FIN-028 | AGGREGATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-010 | compute remainder-line amount for a compound/percentage distribution |
| QR-FIN-029 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-006 | debits = credits |
| QR-FIN-030 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-001 | RULE-FIN-007 | every line's account is leaf + active |
| QR-FIN-031 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-008 | RULE-FIN-008 | entry's period is Open at post time (not applied to API-FIN-027's CLOSING/OPENING entries — exempted by RULE-FIN-008 itself) |
| QR-FIN-032 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-006 | RULE-FIN-009 | every dimension value valid + active |
| QR-FIN-033 | UPDATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-004 | post | flip DRAFT → POSTED, set postedAt (RULE-FIN-016 lock takes effect) |
| QR-FIN-034 | SAVE | API-FIN-021 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build reversal entry (RULE-FIN-011) |
| QR-FIN-035 | EXISTS | API-FIN-021, 014 | ENT-FIN-004 | RULE-FIN-013 | original entry is POSTED and not already reversed |
| QR-FIN-036 | FIND_ONE | API-FIN-021 | ENT-FIN-008 | RULE-FIN-012 | current open period, if original's is closed |
| QR-FIN-037 | FIND_ONE | API-FIN-022 | ENT-FIN-004 | read | read one entry with lines |
| QR-FIN-038 | SAVE | API-FIN-023 | ENT-FIN-007, ENT-FIN-008 | create | create fiscal year + periods |
| QR-FIN-039 | UPDATE | API-FIN-024, API-FIN-025, API-FIN-026 | ENT-FIN-008 | transition | open / soft-close / hard-close a period |
| QR-FIN-040 | EXISTS | API-FIN-026 | ENT-FIN-008 | RULE-FIN-014 | period not already Hard Closed before reopen attempts |
| QR-FIN-041 | AGGREGATE | API-FIN-027 | ENT-FIN-004, ENT-FIN-005 | year-end | compute closing balances, build closing + opening entries |
| QR-FIN-042 | FIND_BY_CRITERIA | API-FIN-028 | ENT-FIN-005 | report | account ledger — POSTED lines for one account, oldest first; the running balance is accumulated by the service, deliberately not returned by the query |
| QR-FIN-043 | AGGREGATE | API-FIN-029, API-FIN-030, API-FIN-031 | ENT-FIN-005 | report | trial balance / balance sheet / income statement account balances (shared aggregation, filtered per report by accountTypeCode) |
| QR-FIN-044 | AGGREGATE | API-FIN-032 | ENT-FIN-005, ENT-FIN-006 | report | dimension report (account × dimension value) |
| QR-FIN-045 | FIND_ONE | API-FIN-027 | ENT-FIN-001 | year-end | the single Retained Earnings account (DBF-FIN-147), lowest pk first |
| QR-FIN-046 | EXISTS | API-FIN-006 | ENT-FIN-002 | uniqueness | dimension code unique |
| QR-FIN-047 | EXISTS | API-FIN-023 | ENT-FIN-007 | uniqueness | fiscal year code unique |
| QR-FIN-048 | FIND_ONE | API-FIN-027 | ENT-FIN-007 | year-end | the next fiscal year, found by its startDate = this year's endDate + 1 day (the opening entry's target) |
| QR-FIN-049 | FIND_BY_CRITERIA | API-FIN-023, API-FIN-027, API-FIN-014 | ENT-FIN-008 | read | every period of one fiscal year, JOIN FETCH on the year, ordered by periodNo |

Join governance: every posting-pipeline QR (024, 025, 028-033) is intra-module only
(FIN_JOURNAL_ENTRY/LINE/LINE_DIM/ACCOUNT/FISCAL_PERIOD, all owned here); the one
cross-module read (QR for lookup-code validation, folded into QR-FIN-002/013/015/024/025/
etc.'s "Validations" step, per XM-FIN-001) is a separate in-process `MdlLookupApi` call,
never a SQL join. No
QR joins to resolve a lookup label — every lookup-backed column returns its code; the
frontend resolves the display label via MDL.

---

















## Error Catalog — FIN v1

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `FIN-{http}[-{SLUG}]`.

| code | RULE / PLATFORM-STD | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| FIN-409-ACCOUNT-DUP | PLATFORM-STD | API-FIN-002 | 409 | duplicate account code | رمز الحساب مستخدم بالفعل | Account code already in use |
| FIN-409-PARENT-NOT-LEAF-ELIGIBLE | RULE-FIN-001 | API-FIN-002 | 409 | parent account cannot remain a leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-400-INVALID-LOOKUP | PLATFORM-STD (XM-FIN-001) | many | 400 | submitted code not found in MDL | القيمة المُدخلة غير صالحة | The submitted value is not valid |
| FIN-409-HAS-CHILDREN | RULE-FIN-001 | API-FIN-003 | 409 | marking a parent as leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-404-ACCOUNT | PLATFORM-STD | API-FIN-002, 003, 004, 013, 016, 019, 020, 027, 028 | 404 | unknown account id — every path that resolves an account FK raises it, not only the three originally listed: API-FIN-002's `parentAccountId` (AccountService.java:168, reached only from `create`), a template line's `accountId` (API-FIN-013, RecurringTemplateService.java:304), an allocation rule's source and target accounts (API-FIN-016, AllocationRuleService.java:278), a manual entry line's `accountId` (API-FIN-019, JournalEntryService.java:349), the account code an event rule derives (API-FIN-020, EventEntryService.java:193) and API-FIN-027's Retained Earnings account, where the reachable failure is "none marked" rather than an unknown id (FiscalYearService.java:347) | الحساب غير موجود | Account not found |
| FIN-409-DIMENSION-DUP | PLATFORM-STD | API-FIN-006 | 409 | duplicate dimension code | رمز البُعد مستخدم بالفعل | Dimension code already in use |
| FIN-409-DIMVALUE-DUP | RULE-FIN-002 | API-FIN-007 | 409 | duplicate code within dimension | هذا الرمز مستخدم بالفعل ضمن هذا البُعد | This code is already used within this dimension |
| FIN-404-DIMENSION | PLATFORM-STD | API-FIN-007, 008, 032 | 404 | unknown dimension id | البُعد غير موجود | Dimension not found |
| FIN-404-DIMVALUE | PLATFORM-STD | API-FIN-035 | 404 | unknown dimension-value id | قيمة البُعد غير موجودة | Dimension value not found |
| FIN-409-RULE-DUP | PLATFORM-STD (§6.4) | API-FIN-010 | 409 | event type already has an active rule | يوجد بالفعل قاعدة نشطة لهذا النوع | An active rule already exists for this event type |
| FIN-409-REMAINDER-COUNT | RULE-FIN-003 | API-FIN-011, 016, 017, 020 | 409 | wrong remainder-line/target count — both guards are re-run on the consuming path, not only at create: the rule-line set is re-validated when an event entry is built (API-FIN-020, EventEntryService.java:104 → EventTypeRuleDomain.java:177) and the target set when an allocation rule is run (API-FIN-017, AllocationRuleService.java:179 → AllocationRuleDomain.java:122) | يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي | Exactly one remainder line is required when any percentage distribution is present |
| FIN-404-RULE | PLATFORM-STD | API-FIN-011, 034 | 404 | unknown event-type rule id | القاعدة غير موجودة | Rule not found |
| FIN-400-MISSING-FREQUENCY | PLATFORM-STD | API-FIN-013 | 400 | recurring template with no frequency | يلزم تحديد التكرار للقالب المتكرر | A frequency is required for a recurring template |
| FIN-404-TEMPLATE | PLATFORM-STD | API-FIN-014, 036 | 404 | unknown recurring template id — raised by `RecurringTemplateService.run` (API-FIN-014) and, since the template deactivate landed, by `RecurringTemplateService.deactivate` (API-FIN-036) resolving the same path id. API-FIN-036 raises it ONLY for an id that does not exist; deactivating an already-inactive template is not an error, and there is deliberately no "exists but is inactive" code — see the API-FIN-036 block in SVC-API-CRUD | القالب المتكرر غير موجود | Recurring template not found |
| FIN-404-ALLOCATION-RULE | PLATFORM-STD | API-FIN-017, 037 | 404 | unknown allocation rule id — raised by `AllocationRuleService.run` (API-FIN-017) and, since the rule deactivate landed, by `AllocationRuleService.deactivate` (API-FIN-037) resolving the same path id. API-FIN-037 raises it ONLY for an id that does not exist; deactivating an already-inactive rule is not an error, and there is deliberately no "exists but is inactive" code — see the API-FIN-037 block in SVC-API-CRUD | قاعدة التوزيع غير موجودة | Allocation rule not found |
| FIN-409-NOT-ACTIVE | (no RULE — recorded human decision, 2026-09-12) | API-FIN-014, 017 | 409 | running a DEACTIVATED recurring template (API-FIN-014) or a deactivated allocation rule (API-FIN-017). Thrown by `RecurringTemplateDomain.assertCanRun()` (a NEW Domain companion for ENT-FIN-011) and `AllocationRuleDomain.assertCanRun()`, each the first thing its service's `run` does after loading the row and before any period, line or target is resolved, so a retired definition posts nothing at all. `Status.CONFLICT` → HTTP 409, consistent with every other FIN refusal whose cause is the target row's own state (FIN-409-NOT-POSTED, FIN-409-NOT-REOPENABLE, FIN-409-PERIOD-NOT-OPEN, FIN-409-INVALID-TRANSITION); the screen's own 404 was NOT reused because the row does exist. **NO RULE-FIN-* STATES THIS GATE.** It closes the "deactivate does not stop the run" OPEN DEFECT by decision, not by implementing a requirement that was always there — do not cite it as pre-existing spec | هذا التعريف غير نشط ولا يمكن تشغيله | This definition is deactivated and cannot be run |
| FIN-409-UNBALANCED | RULE-FIN-006 | API-FIN-019, 020, 014, 017, 021, 027 | 409 | debits ≠ credits — checked once in JournalEntryService.createManual (API-FIN-019) and once in JournalPostingService.buildValidateAndPost (JournalPostingService.java:163), which is the single posting pipeline for API-FIN-014, 017, 020 AND for API-FIN-021's reversal and API-FIN-027's closing/opening pair; the last two were missing from this row | القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن | The entry is unbalanced — total debits do not equal total credits |
| FIN-409-NOT-POSTABLE-ACCOUNT | RULE-FIN-007 | API-FIN-019, 020, 014, 017, 021, 027 | 409 | non-leaf/inactive account — AccountDomain.checkPostable runs per line in JournalEntryService.createManual (API-FIN-019, :350) and in JournalPostingService.buildValidateAndPost (:141), so it also covers API-FIN-021's reversal and API-FIN-027's closing/opening pair | الحساب المستهدف لا يقبل ترحيلاً مباشرًا | The target account does not accept direct posting |
| FIN-409-PERIOD-NOT-OPEN | RULE-FIN-008 | API-FIN-019, 020, 014, 017, 021 | 409 | period not Open at post — API-FIN-021 raises it twice over: from the shared gate in JournalPostingService.buildValidateAndPost (:164) and, before that, when the original's period is closed and the ledger has no open period to receive the reversal (JournalEntryDomain.java:329). API-FIN-027 is deliberately NOT listed: RULE-FIN-008 exempts the year-end CLOSING/OPENING types (JournalEntryDomain.checkTargetPeriodOpenForGeneratedEntry, :236) | الفترة المستهدفة غير مفتوحة | The target period is not open |
| FIN-409-INVALID-DIMENSION | RULE-FIN-009 | API-FIN-013, 014, 016, 017, 019, 020, 021, 027 | 409 | invalid/inactive dimension value — RULE-FIN-009 (DimensionValueDomain.checkUsableOnLine) runs in JournalEntryService.createManual (API-FIN-019, :376) and in JournalPostingService.buildValidateAndPost (:144), so it also covers API-FIN-021 and API-FIN-027. API-FIN-013 and API-FIN-016 raise the SAME code for a different reason — plain FK resolution of a submitted `dimensionValueId` that does not exist (RecurringTemplateService.java:318, AllocationRuleService.java:291) — which is why they belong in this row even though no rule is evaluated there | قيمة البُعد غير صالحة | The dimension value is invalid |
| FIN-409-DUPLICATE-EVENT | RULE-FIN-004 | API-FIN-020 | 409 | repeated eventReference | تم بالفعل ترحيل قيد لهذا المرجع | An entry for this event reference has already been posted |
| FIN-404-NO-ACTIVE-RULE | RULE-FIN-005 | API-FIN-020 | 404 | no active rule for event type | لا توجد قاعدة نشطة لهذا النوع من الأحداث | No active rule exists for this event type |
| FIN-422-MAPPING-UNSUPPORTED | PLATFORM-STD | API-FIN-020 | 422 | rule line with accountDerivationTypeCode=MAPPING, for which no mapping store is declared in db-script-fin.md | يستخدم هذا السطر اشتقاق الحساب عبر جدول المطابقة وهو غير متاح حاليًا | This rule line uses mapping-based account derivation, which is not available yet |
| FIN-409-NOT-POSTED | RULE-FIN-013 | API-FIN-021, 014 | 409 | reversing a non-posted entry — raised by the same JournalEntryDomain.assertCanReverse guard as FIN-409-ALREADY-REVERSED (JournalEntryDomain.java:284), so a REVERSING template run reaches it too (API-FIN-014, RecurringTemplateService.java:249) | لا يمكن عكس قيد غير مُرحَّل | A non-posted entry cannot be reversed |
| FIN-409-ALREADY-REVERSED | RULE-FIN-013 | API-FIN-021, 014 | 409 | reversing an entry that already carries a reversal link | تم عكس هذا القيد بالفعل ولا يمكن عكسه مرة أخرى | This entry has already been reversed and cannot be reversed again |
| FIN-404-ENTRY | PLATFORM-STD | API-FIN-021, 022 | 404 | unknown entry id | القيد غير موجود | Entry not found |
| FIN-409-YEAR-DUP | PLATFORM-STD | API-FIN-023 | 409 | duplicate fiscal year code | رمز السنة المالية مستخدم بالفعل | Fiscal year code already in use |
| FIN-409-NOT-REOPENABLE | RULE-FIN-014 | API-FIN-024, 026 | 409 | period Hard Closed | الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها | The period is hard-closed and cannot be reopened |
| FIN-409-INVALID-TRANSITION | PLATFORM-STD | API-FIN-025, 027 | 409 | period not in the expected state; fiscal year already CLOSED when year-end close is re-run | لا يمكن تنفيذ هذا الانتقال من الحالة الحالية | This transition is not allowed from the current status |
| ~~FIN-403-SOD-VIOLATION~~ STRUCK | RULE-FIN-015 | — | — | UNREACHABLE since 2026-09-12 — both throw sites are gone. It was raised when the close-approver's permission set was not globally disjoint from the entry-creation permission's: `FinSeparationOfDutiesService` read SEC's user directory (XM-FIN-002, now retired) and `FiscalPeriodDomain.assertCanHardClose(...)` threw. Both were DELETED by recorded human decision as an OVER-IMPLEMENTATION: they refused the close for EVERY caller whenever ANY single user in the system held both `PERM_FIN_PERIODS_CLOSE_APPROVE` and `PERM_FIN_JOURNAL_ENTRIES_CREATE`, and no REQ, AC or RULE states that. RULE-FIN-015 (srs-fin.md:1026-1033) asks only for a DISTINCT permission "enforced through the Security module" and its `Data source` line reads DEFERRED — no FIN-side fact to read — so the rule is satisfied in full by the delivered `@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on API-FIN-026 and API-FIN-027, which is untouched. STRUCK RATHER THAN DELETED, following the `FIN-503` row's precedent in this same table (an unreachable code is struck, kept visible, and given no API/HTTP cells). ONE HONEST DIFFERENCE FROM THAT PRECEDENT: FIN-503 never existed in code, whereas the constant `FinErrorCodes.FIN_403_SOD_VIOLATION` and BOTH bundle entries (`messages.properties`, `messages_ar.properties`) were deliberately left in place by the code session, so the string is still in the build with no thrower — the message columns below are therefore the real, still-present bundle text, not a historical quotation. A session that removes the constant and the two bundle keys should delete this row's message cells with them | صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود | The close-approval permission is separate from the entry-creation permission |
| FIN-404-PERIOD | PLATFORM-STD | API-FIN-014, 017, 019, 020, 024, 025, 026, 027, 029, 031 | 404 | unknown period id — on API-FIN-029 only when the OPTIONAL `periodId` is actually supplied (omitting it stays a 200); API-FIN-031's `fromPeriodId`/`toPeriodId` already raised it before the report-404 change and are unchanged. The six ids added here were verified in source and are NOT all "unknown id" failures: API-FIN-024/025/026 resolve the path id (FiscalPeriodService.java:204); API-FIN-019 resolves the submitted `periodId` (JournalEntryService.java:174); API-FIN-014, 017 and 020 carry no period id at all and raise it when NO period's `[startDate, endDate]` covers the run/document date (JournalPostingService.java:208); API-FIN-014 additionally raises it when a REVERSING template's period has no successor inside the same fiscal year (RecurringTemplateService.java:284); API-FIN-027 raises it when the closing year has no last period or the successor year no first period (FiscalYearService.java:314, :322) | الفترة غير موجودة | Period not found |
| FIN-409-PERIODS-NOT-CLOSED | PLATFORM-STD (§10.4 precondition) | API-FIN-027 | 409 | not every period Hard Closed | يجب إغلاق كل الفترات إغلاقًا صارمًا أولًا | Every period must be hard-closed first |
| FIN-404-YEAR | PLATFORM-STD | API-FIN-014, 017, 019, 020, 021, 027, 030, 031 | 404 | unknown fiscal year id — on API-FIN-030 and API-FIN-031 the REQUIRED `fiscalYearId` is resolved first and raises this instead of the silent all-zero 200 those reports previously returned. The five ids added here were verified in source: API-FIN-019 resolves the submitted `fiscalYearId` under the docNo row lock (JournalEntryService.java:171), and every system-generated posting re-resolves the year under that same lock inside JournalPostingService.buildValidateAndPost (:152) — the single pipeline behind API-FIN-014, 017, 020, 021 and 027. API-FIN-027 raises it from two further sites of its own: an absent adjacent successor year (FiscalYearService.java:364) and an unknown path id (:371). API-FIN-023 does NOT raise it — FiscalYearService.create resolves no year | السنة المالية غير موجودة | Fiscal year not found |
| FIN-422-REMAINDER-MARKER | RULE-FIN-003, RULE-FIN-010 | API-FIN-011, 016, 017, 020 | 422 | `isRemainderFl` (DBF-FIN-103/141) disagrees with the line's/target's own REMAINDER type code, so which line is the remainder is ambiguous | علامة سطر الباقي لا تتفق مع نوع التوزيع أو مصدر المبلغ لنفس السطر | The remainder marker disagrees with the line's own distribution or amount-source type |
| FIN-422-REMAINDER-NOT-POSITIVE | RULE-FIN-010 | API-FIN-017, 020 | 422 | the remainder line's per-side difference is zero or negative — the other lines on its side already equal or exceed the opposing side (POL-FIN-005) | سطر الباقي يُحسب كفرق ويجب أن يكون موجبًا؛ السطور الأخرى تستهلك المبلغ بالكامل | The remainder line is computed as a difference and must be positive; the other lines already consume the full amount |
| FIN-400-PERIOD-NOT-IN-YEAR | RULE-FIN-017 | API-FIN-019 | 400 | submitted `periodId` belongs to a different fiscal year than the submitted `fiscalYearId` (DBF-FIN-076) | الفترة المحددة لا تتبع السنة المالية المحددة | The selected period does not belong to the selected fiscal year |
| FIN-400-DOCDATE-OUTSIDE-PERIOD | RULE-FIN-017 | API-FIN-019 | 400 | submitted `docDate` falls outside the submitted period's `[startDate, endDate]` span (DBF-FIN-080/081) | تاريخ المستند خارج نطاق الفترة المحددة | The document date falls outside the selected period |
| FIN-403-FORBIDDEN | PLATFORM-STD | every secured API (i.e. every `@PreAuthorize` on a `com.erp.fin.service.*` method — API-FIN-036 and API-FIN-037 included) | 403 | missing module/screen/action grant — **this code now REACHES THE WIRE as itself.** `com.erp.fin.security.FinForbiddenAdvisor` catches the `AccessDeniedException` raised by `@PreAuthorize` on any `com.erp.fin.service.*` method and re-raises it as `LocalizedException(Status.FORBIDDEN, FinErrorCodes.FIN_403_FORBIDDEN)`, which `GlobalExceptionHandler` renders like every other FIN error. It IS a `FinErrorCodes` constant (`FIN_403_FORBIDDEN`) and it IS in BOTH i18n bundles (`messages.properties`, `messages_ar.properties`). **Every earlier revision of this row said the opposite** — that FIN's 403 was rendered as the platform `ACCESS_DENIED` envelope, that this row was merely the catalog's *name* for that response, that the code was in no `FinErrorCodes` constant and in neither bundle, and that FIN had no `FIN-403-FORBIDDEN` on the wire. All of that is superseded and none of it is true any more. TWO BOUNDARIES, each read in source: (1) a denial raised by the Spring Security **filter chain**, before any FIN service is entered, never reaches an AOP proxy or `GlobalExceptionHandler` — it is written by the chain's `accessDeniedHandler` and still answers `SEC-403-FORBIDDEN`. That path is currently UNREACHABLE for FIN, because `SecurityConfig` (`com.erp.main.config`) authorizes with `.anyRequest().authenticated()` and declares no FIN authority rule, so every FIN permission denial is a `@PreAuthorize` denial on a FIN service and does pass through the advisor; adding a URL-level authority rule for a FIN path would change that. (2) `FIN-403-SOD-VIOLATION` is unaffected — it is a RULE-FIN-015 business failure thrown by hand as a `LocalizedException`, never an `AccessDeniedException`, so the advisor never sees it. Also note `CommonErrorCodes.ACCESS_DENIED` still exists and is still what `GlobalExceptionHandler.handleAccessDenied` emits for modules that have no forbidden advisor of their own; FIN is simply no longer one of them | لا تملك صلاحية المالية المطلوبة لهذه العملية | You do not hold the Finance permission required for this operation |
| FIN-400-INVALID-SORT | PLATFORM-STD | every search API | 400 | unrecognized sort field | حقل الترتيب غير معروف | Unrecognized sort field |
| ~~FIN-503~~ STRUCK | PLATFORM-STD (MDL unreachable) | — | — | unreachable: XM-FIN-001 is in-process `MdlLookupApi` injection, so there is no network hop to fail (and `Status` has no SERVICE_UNAVAILABLE); an invalid code raises `FIN-400-INVALID-LOOKUP`, anything else falls through to `FIN-500` | — | — |
| FIN-500 | PLATFORM-STD (infrastructure) | any | 500 | unhandled server error | حدث خطأ في الخادم | A server error occurred |

Every PLATFORM-STD row follows SEC's ADR-SEC-002 umbrella convention, cited (not re-derived).

## Alignment self-check (ALIGN) — FIN v1

```
RE-RUN AT ALIGN-BE, against the delivered code — every line below states what was actually
verified after implementation, not what was intended before it. The pre-implementation form of
this block read "PASSED ✓ — 0 findings"; that was false and is superseded here. REVISED AGAIN
2026-09-12 (final governance-state pass, after the separation-of-duties removal, the
FIN-409-NOT-ACTIVE run gate, and V30): EVERY COUNT BELOW WAS RE-MEASURED FROM THE REAL ARTIFACT
BY THAT SESSION, none carried from the previous revision, and each line names how it was taken.

TRACEABILITY      ✓ re-verified. REQ-FIN-001..046 and DBF-FIN-001..147 all defined upstream; every PHASE/SUB/atom carries traces=. Re-counted 2026-09-12: 147 unique DBF-FIN ids and 49 unique QR-FIN ids in this document (`grep -oE 'DBF-FIN-[0-9]{3}'` / `'QR-FIN-[0-9]{3}'`, sorted unique), contiguous in both cases; no id was ever renumbered. Two id sets that grew after this block was first written are still reflected everywhere: RULE-FIN-017 (srs §A5) and QR-FIN-045..049 (ALIGN-BE, for queries already implemented). === CORRECTED 2026-09-12: XM-FIN-002 IS NO LONGER A LIVE ID and must not be listed as one. It was registered at ALIGN-BE for FIN's read of SEC's SecUserDirectoryApi; that read was deleted together with FinSeparationOfDutiesService by a recorded human decision, so XM-FIN-002 is RETIRED — the id is kept, never reused and never renumbered, and survives only as a struck historical block in INT-C and INT-R. The live XM set is XM-FIN-001 alone; see CROSS-MODULE.
BINDING (§2A)     ✓ re-verified. No placeholder; every column cites a DBF; every RULE message present in ar+en. docNo is `JV-{fiscalYearCode}-{NNNNNN}`, counter per fiscalYearId, generated by a FIN-local generator in com.erp.fin (the "platform numbering engine" the pre-implementation text named does not exist and never did). The one place that phrase survived in the LIVE DATABASE — V22__fin_schema.sql:278's `COMMENT ON COLUMN FIN_JOURNAL_ENTRY.doc_no` — is corrected forward by V29__fin_comment_corrections.sql, whose replacement statement names `com.erp.fin.numbering.JournalDocNoGenerator` and the `JV-{fiscalYearCode}-{NNNNNN}` format explicitly (both of V29's two statements re-read in full today). V29 is WRITTEN BUT NOT YET APPLIED to any database — `git status --short src/main/resources/db/migration/` returns it as untracked (`??`) today — so until it runs the live comment still says "platform numbering engine". === CORRECTED 2026-09-12: V29 is NO LONGER the highest-numbered migration. `ls src/main/resources/db/migration/ | grep -oE '^V[0-9]+' | sort -t V -k2 -n | tail -1` now returns V30 (V30__fin_sys_admin_close_approve_grant.sql), also untracked and also not yet applied. The previous revision's "highest-numbered file" parenthetical is superseded; V29's unapplied status is unchanged.
MANIFEST (§4)     ✓ after correction. All 147 DBF listed, only the mandated columns. Corrected earlier and still standing: the XM count read "12 columns across 8 tables" and is 16 across 10 — re-measured today as 16 lines matching `^COMMENT ON COLUMN.*XM-FIN-001` in V22__fin_schema.sql, spanning FIN_ACCOUNT, FIN_JOURNAL_ENTRY, FIN_JOURNAL_LINE, FIN_FISCAL_YEAR, FIN_FISCAL_PERIOD, FIN_EVENT_TYPE_RULE, FIN_RULE_LINE, FIN_RECURRING_TEMPLATE, FIN_RECURRING_TEMPLATE_LINE and FIN_ALLOCATION_TARGET (a bare `grep -c XM-FIN-001` over V22 returns 18 and OVER-COUNTS — two of the hits are prose, at V22:6 and V22:482); five rows named a `_pk` column `...Id` (DBF-FIN-098/109/122/130/139) — one of them, DBF-FIN-130, colliding with DBF-FIN-140's real FK of the same name — and now match the entity. RESIDUAL, not corrected: db-script-fin.md's 14 matrix rows still describe `GENERATED ALWAYS AS IDENTITY` PKs where V22 deliberately built SEQUENCE PKs (deviation justified at V22:15-22 and noted in this plan's extraction block); 20 FK rows are modelled as scalar Long where the entity uses @ManyToOne. The (d) half — V22:240's FIN_ACCOUNT table comment omitting DBF-FIN-147 — is CLOSED by V29 (written, not applied; see SCHEMA COMMENT). The audit-width half is HALF-CLOSED and was re-measured from scratch today: AuditableEntity.createdBy/updatedBy are `length = 100` (AuditableEntity.java:26 and :32, both re-read), while the PHYSICAL schema is still split — `grep -rhoiE '(created_by|updated_by) +VARCHAR\([0-9]+\)' src/main/resources/db/migration/` returns 16 CREATED_BY + 16 UPDATED_BY at VARCHAR(100) (V16 SEC 5 · V18 MDL 2 · V22 FIN 9) and 14 + 14 at VARCHAR(255) (V1 · V2 · V6 · V8); discarding the eight V2 tables that V14__drop_legacy_security_schema.sql drops leaves 6 LIVE at 255 (CU_APP_CONFIGURATION, NOTIF_TEMPLATE, NOTIF_CHANNEL_CONFIG, NOTIF_LOG, FILE_CATEGORY, FILE_DOCUMENT), so 16 + 6 = 22 live tables — exactly the 22 classes `grep -rl "extends AuditableEntity" src/main/java/com/erp/` returns, re-counted today. Platform-wide, so still not FIN's to settle — written up in governance/project-artifacts/platform-audit-widths-and-error-localization.md.
QRC (§5)          ✓ after correction. Both directions re-run. Forward: all 49 QR ids have a real implementation; no join resolves a lookup label (zero MDL joins in any FIN @Query). Backward: four repository methods had ZERO call sites (contract rule A.2.9) and were DELETED at ALIGN-BE — FiscalPeriodRepository.existsByFiscalPeriodPkAndStatusCode, JournalEntryRepository.existsByJournalEntryPkAndStatusCode, JournalLineRepository.countByJournalEntryPk, RecurringTemplateRepository.findByIsActiveFlAndNextRunDateLessThanEqual; the first two claimed to be the "cheap pre-check" for QR-FIN-040/035, which are in fact decided by FiscalPeriodDomain.assertCanReopen and JournalEntryDomain.assertCanReverse on the loaded entity, with no query at all. Five real, called queries had no QR id and now carry QR-FIN-045..049. Three catalog cross-references corrected (QR-FIN-022 cited QR-FIN-040 for a balance, now QR-FIN-043; QR-FIN-016's table scope now matches its id definition and the code; QR-FIN-042 no longer claims to return a running balance). Re-counted 2026-09-12: 49 unique QR-FIN ids, contiguous QR-FIN-001..049. NOTE for the A.2.9 sweep: the SoD removal created a NEW dead chain, but it is in SEC, not FIN — carried below as SEC DEAD CHAIN.
API (R3)          ✓ re-measured against the controllers 2026-09-12, nothing carried over. 37 endpoints — counted by listing every `@GetMapping/@PostMapping/@PutMapping/@PatchMapping/@DeleteMapping` in each of the nine files under src/main/java/com/erp/fin/controller/ and summing: Account 4, AllocationRule 4, Dimension 5, EventTypeRule 4, FiscalPeriod 4, FiscalYear 2, JournalEntry 5, RecurringTemplate 4, Report 5 — covering exactly API-FIN-001..037. Unchanged from the previous revision's re-measurement; the run-gate and SoD changes added no endpoint and removed none. Shapes unchanged: every search is POST /<resource>/search, every deactivate is a PUT on the resource's own id path (`/{id}/deactivate`, or `/values/{id}/deactivate` for the dimension-value child), the three period transitions are PATCH, child endpoints sit on the parent's controller, and there is still NO @DeleteMapping and no activate anywhere in FIN (grep returns zero of each; re-run today). Create/update requests exclude PK/audit/system fields (docNo, statusCode, postedAt); docNo appears only in responses. === RE-COUNTED 2026-09-12, and the previous revision's figures are SUPERSEDED: 40 error codes, measured three ways and diffed pairwise with zero orphans in any direction — 40 `"FIN-*"` string literals in FinErrorCodes.java, 40 keys matching `^FIN-` in messages.properties, 40 in messages_ar.properties — 40/40/40, where the previous revision said 38/38/38. The two added since are FIN-409-NOT-ACTIVE (the run gate; FinErrorCodes.java:441) and FIN-422-INVALID-PERCENTAGE-VALUE (FinErrorCodes.java:357). THREE line references on the previous revision's text have MOVED because of those inserts and are corrected here: FIN_403_FORBIDDEN is now FinErrorCodes.java:400 (was :384), messages.properties:173 (was :172), messages_ar.properties:170 (was :169). The Error Catalog holds 41 code rows, not 39 — counted as _SECTIONS.md:378-418 inclusive and cross-checked as 41 unique codes in the first table column. Of those 41, exactly TWO are deliberately not constants: FIN-500, the infrastructure fallthrough (:418), and ~~FIN-503~~, struck (:417). ~~FIN-403-SOD-VIOLATION~~ is ALSO struck (:407) but, unlike those two, IS still a live constant and a live pair of bundle rows — that mismatch is a finding in its own right, carried below as SOD DEAD CODE. And the diff does not close in the other direction either: ONE constant has no catalog row at all — FIN-422-INVALID-PERCENTAGE-VALUE — carried below as CATALOG GAP. The previous revision's sentence "The Error Catalog holds 39 code rows, so exactly TWO are deliberately not constants" is therefore wrong twice over and is superseded by this measurement.
CROSS-MODULE      ✓ after correction, and the correction runs the OTHER WAY from the previous revision's. EXACTLY 1 XM, 1 placed, 0 mismatched, ACTIVE: XM-FIN-001 (SOFT-READ → MDL_LOOKUP_VALUE). The previous revision read "2 XM, 2 placed ... both ACTIVE" and listed XM-FIN-002 (READ → SEC's SecUserDirectoryApi); that stopped being true on 2026-09-12, when FinSeparationOfDutiesService — FIN's ONLY consumer of SecUserDirectoryApi — was deleted by a recorded human decision, together with FiscalPeriodDomain.assertCanHardClose(...). Re-measured today, not inferred: `ls src/main/java/com/erp/fin/service/FinSeparationOfDutiesService.java` returns "No such file or directory"; `grep -rn SecUserDirectoryApi src/main/java/com/erp/fin/` returns ZERO hits; and the complete set of non-com.erp.fin, non-com.erp.common imports anywhere under src/main/java/com/erp/fin/ is now exactly two lines — `import com.erp.mdl.crossmodule.LookupOptionView;` and `import com.erp.mdl.crossmodule.MdlLookupApi;`. XM-FIN-002 is RETIRED, not deleted: its id is kept and never reused, it survives as a struck historical block in INT-C and INT-R, and it binds no manifest row (it never did — it was a service-to-service read, not a column). Consumption of XM-FIN-001 is in-process Spring interface injection, never HTTP; CrossModuleBoundaryArchTest passes. Inbound stub XM-INBOUND-STUB-3 notation unchanged.
SECURITY (R7)     ✓ ORIGINAL FINDING CLOSED, fully re-measured 2026-09-12 from the files, nothing carried. 27 PERM_FIN_* constants — `grep -oE 'String (PERM_FIN_[A-Z_]+) *=' PermissionConstants.java`, sorted unique (a plain `PERM_FIN_` grep over-counts: comments mention PERM_FIN_ACCOUNTS_DELETE, which is NOT declared) — against 27 registered action rows: 26 in V24__fin_security_seed.sql's SEC_ACTION_REG VALUES block (counted per screen: FIN_ACCOUNTS 3, FIN_DIMENSIONS 2, FIN_RULES 3, FIN_RECURRING_TEMPLATES 3, FIN_ALLOCATION_RULES 3, FIN_JOURNAL_ENTRIES 3, FIN_PERIODS 4, five report screens 1 each) plus the one FIN_DIMENSIONS/UPDATE row added by V28__fin_dimensions_update_action.sql. Synthesising `PERM_<page_code>_<action_code>` from those 27 rows and `diff`ing the sorted set against the sorted constant list gives an EXACT 27/27 match with no orphan in either direction, and every one of the 27 is referenced from at least one file under src/main/java/com/erp/fin/ (checked individually today, zero unreferenced). V30 ADDS NO ACTION ROW: it is a grant only — a single INSERT INTO SEC_ROLE_ACTION_GRANT selecting SYS_ADMIN against `a.PERMISSION_CODE = 'PERM_FIN_PERIODS_CLOSE_APPROVE'` — so the 27/27 figure is unaffected by it. What V30 DOES change is reachability: V25__fin_role_grants.sql:111 deliberately excluded that one permission from SYS_ADMIN (`AND a.PERMISSION_CODE <> 'PERM_FIN_PERIODS_CLOSE_APPROVE'`) precisely because the deleted SoD service would have refused every close if one user held both codes; with that service gone the exclusion protects nothing and locks the bootstrap `admin` out of API-FIN-026/027, so V30 reverses it forward. Also corrected earlier and still standing: PERM_FIN_PERIODS_VIEW is declared (PermissionConstants.java:248) and consumed by FiscalPeriodService.java:176's @PreAuthorize behind API-FIN-033; PERM_FIN_DIMENSIONS_UPDATE (DimensionValueService.java:100) is the genuinely new one V28 both registers and grants; the FIN_ACCOUNTS ✓ sits on UPDATE, not DELETE. === @PreAuthorize RE-COUNTED 2026-09-12 AND THE PREVIOUS FIGURE CORRECTED: 42 annotations, not 43. Counted as lines matching `^[[:space:]]*@PreAuthorize\(` under src/main/java/com/erp/fin/ — AccountService 4, AllocationRuleService 4, DimensionService 2, DimensionValueService 3, EventEntryService 1, EventTypeRuleService 3, FinLookupValidationService 2, FiscalPeriodService 4, FiscalYearService 2, JournalEntryService 4, JournalPostingService 3, RecurringTemplateService 4, ReportService 5, RuleLineService 1 — 14 files, all under service/. TWO looser greps over-count and both are named so the next session does not repeat them: the bare word `@PreAuthorize` returns 58, and `@PreAuthorize(` (unanchored) returns 47, the extra 5 being javadoc `{@code @PreAuthorize(...)}` references in FiscalPeriod.java:38 and :158, FinLookupValidationService.java:44, JournalPostingService.java:73 and FiscalPeriodDomain.java:106. The previous revision's file list is also stale: it named FinSeparationOfDutiesService, which no longer exists, and the drop from 43 to 42 is exactly that file's single annotation leaving the tree.
CORE (R1)         ✓ re-verified. Layers, domain placement, error signalling (`FIN-{http}[-{SLUG}]`) and type mapping all as declared; services delegate every rule decision to a Domain companion. === RE-COUNTED 2026-09-12: 8 Domain classes, not 7 — `ls src/main/java/com/erp/fin/domain/*.java` returns AccountDomain, AllocationRuleDomain, DimensionValueDomain, EventTypeRuleDomain, FiscalPeriodDomain, FiscalYearDomain, JournalEntryDomain and RecurringTemplateDomain. RecurringTemplateDomain is NEW (untracked in the working tree today), added as the companion for the run gate; its only rule method is assertCanRun() at RecurringTemplateDomain.java:71. AllocationRuleDomain gained the matching assertCanRun() at :191. The count moved 7 → 8 for that reason and no other; FiscalPeriodDomain LOST a method in the same pass (assertCanHardClose) without losing the class.
DECISIONS         ✓ ADR-FIN-001 (carried from P2) cited and still correct as written. DEFAULTs landed since: JOURNAL_TYPE gains CLOSING/OPENING (data-only); docNo format and FIN-local generator ownership; classic reversal (the original stays POSTED and is linked to its reversal; a second reversal is rejected; nothing writes VOID); RULE-FIN-008 exempts API-FIN-027's year-end CLOSING/OPENING entries; MAPPING account derivation is rejected with FIN-422-MAPPING-UNSUPPORTED; a twelve-period fiscal year generates calendar months. No BLOCKED ADR. === ADDED 2026-09-12 — TWO RECORDED HUMAN DECISIONS, both of which change delivered behaviour and neither of which derives from any RULE-FIN-*, so both are named here rather than left implicit in the code: (1) SEPARATION OF DUTIES IS THE PERMISSION GATE AND NOTHING MORE. RULE-FIN-015 (srs-fin.md:1026-1033, re-read at those lines) requires only that the close-approval action be "gated by a permission distinct from the journal-entry-creation permission, enforced through the Security module", and its Data source line records that FIN has no field to read for it; REQ-FIN-038/AC-FIN-038 say the same. The delivered `@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` on FiscalPeriodService.hardClose and FiscalYearService.yearEndClose IS that enforcement. The previous implementation went further and enforced GLOBAL USER-SET DISJOINTNESS — it asked SEC which users held each permission and refused the close for EVERY caller whenever any single user in the system held both — which the SRS never asks for and which denied clean approvers. It was deleted. ADR-FIN-001 is unaffected by this: it excludes AMBIENT platform integration with SEC from the XM register, and the thing removed was FIN business logic reading SEC data about other users, which is why it had correctly been an XM row while it existed. (2) A DEACTIVATED TEMPLATE OR RULE MAY NOT RUN — see DEACTIVATE RUN below; likewise a decision, not a derived requirement.
ACCOUNTING §12    ✓ all 14 must-honor points still traced and re-verified: (1) RULE-FIN-006 · (2) POL-FIN-002/API-FIN-029 sign presentation · (3) RULE-FIN-007 · (4) RULE-FIN-008, now with its explicit carve-out for API-FIN-027's year-end CLOSING/OPENING entries · (5) CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE + directionCode · (6) RULE-FIN-003/010, plus FIN-422-REMAINDER-MARKER and FIN-422-REMAINDER-NOT-POSITIVE · (7) RULE-FIN-011, now CLASSIC reversal: the original stays POSTED, reversalEntryId/originalEntryId link the pair, a second reversal is rejected with FIN-409-ALREADY-REVERSED, net ledger effect zero, and no path writes VOID · (8) API-FIN-029 (balances by construction) · (9) every report QR reads POSTED lines live, no stored balance column anywhere in db-script-fin.md · (10) REQ-FIN-036/RULE for continuity · (11) RULE-FIN-009 + QR-FIN-044 dimension grouping · (12) RULE-FIN-004 · (13) RULE-FIN-016 lock + no DELETE mapping anywhere (FIN publishes no DELETE endpoint at all) · (14) POL-FIN-014, no host-specific branch anywhere in this plan
TEST PLAN         ✓ re-counted 2026-09-12, for the record only — THE TEST PHASE HAS NOT RUN and nothing below asserts that it has. governance/modules/FIN/test_gen/backend-test-plan-fin.md now carries 109 test-case ids, not 108: counted as 109 `<!-- TC:TC-FIN-nnn:START` markers and confirmed as 109 unique TC-FIN ids, contiguous TC-FIN-001..109. 108 of the 109 are IN FORCE. The arithmetic, from the plan's own header at its lines 6-9: 107 module-scope (phase TEST-PLAN-BE) + 2 integration (phase INT-XM) = 109 ids, less TC-FIN-091, RETIRED 2026-09-12 — its id deliberately kept rather than deleted so nothing renumbers, and it must NOT be counted as a coverage gap. TWO CHANGES SINCE THE PREVIOUS REVISION, both verified in the file: (a) TC-FIN-091 existed only to exercise the SEC user-directory read and was retired when that read was deleted; (b) TC-FIN-106 and TC-FIN-107 NO LONGER PIN AN OPEN DEFECT — they were FLIPPED (the plan says so at its line 24 and at :1502) and now read "a deactivated recurring template is REFUSED at run time (FIN-409-NOT-ACTIVE)" (:1449) and the same for an allocation rule (:1483), asserting the 409 rather than the old "still runs and still posts". The previous revision of this line said those two TCs "deliberately PIN THE OPEN DEFECT"; that is superseded. (c) TC-FIN-109 is new, added to cover FIN-422-INVALID-PERCENTAGE-VALUE, which had been a registered code with no test — a real gap the test session found and closed. execution-state.json's TEST-PLAN-BE and INT-XM remain PENDING and are not touched by this block.
ERROR ENVELOPE    ✓ CLOSED — by src/main/java/com/erp/fin/security/FinForbiddenAdvisor.java, re-read in full 2026-09-12. It is a `DefaultPointcutAdvisor` at `Ordered.HIGHEST_PRECEDENCE` (:57) whose pointcut matches any target class whose name starts with `com.erp.fin.service.` (:40); its interceptor catches `AccessDeniedException` from `invocation.proceed()` and re-throws `new LocalizedException(Status.FORBIDDEN, FinErrorCodes.FIN_403_FORBIDDEN)` (:54), which GlobalExceptionHandler's LocalizedException handler (:32-52) then renders through MessageSource. FIN-403-FORBIDDEN is therefore reachable on the wire, and is backed by a constant and by both bundles — all three re-grepped today AT THEIR CURRENT LINES, which have moved since the previous revision wrote them: FinErrorCodes.java:400 (was :384), messages.properties:173 (was :172), messages_ar.properties:170 (was :169). It is declared once for the module, never per endpoint and never as a feature-module @ControllerAdvice, mirroring com.erp.sec.security.SecForbiddenAdvisor. THE BOUNDARY, NAMED RATHER THAN GLOSSED, because the closure is real but not total: (1) only a denial raised INSIDE com.erp.fin.service.* is translated — a Spring Security FILTER-CHAIN denial never reaches an AOP proxy or GlobalExceptionHandler at all, being written directly by SecSecurityErrorHandler, which SecurityConfig.java:59 wires as `.accessDeniedHandler(securityErrorHandler)` and which answers SEC-403-FORBIDDEN (SecSecurityErrorHandler.java:42) — all three lines re-read today. That path is UNREACHABLE for FIN today: SecurityConfig.java:56 authorizes with `.anyRequest().authenticated()` and declares no FIN authority rule, so every FIN permission denial is in fact a @PreAuthorize denial on a FIN service. Add one URL-level authority rule for a FIN path and that stops being true. (2) Platform-wide, the shared handler's AccessDeniedException path still answers CommonErrorCodes.ACCESS_DENIED for any module without its own advisor — unchanged, and not a FIN finding. === CORRECTED 2026-09-12: the previous revision's clause (2), that "FIN-403-SOD-VIOLATION is UNAFFECTED ... raised as a LocalizedException directly (FinSeparationOfDutiesService.java:109, FiscalPeriodDomain.java:112)", is NO LONGER TRUE IN ANY PART — that file is gone, that method is gone, and `grep -rn 'FIN_403_SOD_VIOLATION' src/main/java/` returns no throw site at all. The code is unreachable; see SOD DEAD CODE.
SCHEMA COMMENT    ✓ CLOSED — by src/main/resources/db/migration/V29__fin_comment_corrections.sql, named here because this line's own prior text demanded that any closure point at the migration that closed it. Re-read in full 2026-09-12: V29 issues exactly two statements and changes no structure and no data — `COMMENT ON TABLE FIN_ACCOUNT IS 'ENT-FIN-001 Account — PRIVATE; [DBF-FIN-001..013, DBF-FIN-147]';` and a replacement `COMMENT ON COLUMN FIN_JOURNAL_ENTRY.doc_no` naming com.erp.fin.numbering.JournalDocNoGenerator and the JV format (see BINDING). The first is byte-for-byte the text db-script-fin.md:447 states, against V22__fin_schema.sql:240's `[DBF-FIN-001..013]`. V22 stays untouched and immutable, as required; the defect is corrected FORWARD, which is the only legal repair. STATED HONESTLY AND RE-CONFIRMED TODAY: V29 is WRITTEN BUT NOT YET APPLIED to any database — still untracked (`??`) in `git status --short`. This line is closed against the repository, not against a running database; if V29 is ever reverted or renumbered, reopen it. V30 has the same unapplied status but corrects no comment and does not bear on this line.
SCOPE vs SRS      ✓ ORIGINAL FINDING CLOSED — by a SPLIT decision, half built and half deliberately excluded, both recorded in srs-fin.md. BUILT: API-FIN-035, `PUT /api/v1/fin/dimensions/values/{id}/deactivate` (DimensionController.java:80), gated on the new PERM_FIN_DIMENSIONS_UPDATE (DimensionValueService.java:100), raising the new FIN-404-DIMVALUE, registered and granted by V28; and API-FIN-034, `PUT /api/v1/fin/event-rules/{id}/deactivate` (EventTypeRuleController.java:66), on the PRE-EXISTING PERM_FIN_RULES_UPDATE (EventTypeRuleService.java:100) and the PRE-EXISTING FIN-404-RULE — so it needed no migration and no new code. NOT BUILT, deliberately, and now v1 DECISIONS rather than gaps: a deactivate on the PARENT Dimension (srs-fin.md:1177, and the reasoning under B4 — no REQ, AC or RULE asks for one) and a rule-line DELETE (srs-fin.md:1235 and B4 — ENT-FIN-010 carries no active-flag column and FIN publishes no DELETE endpoint on any screen). The requirement text was narrowed WITH its reason attached, not silently deleted. A DIFFERENT, newly-surfaced SRS/code divergence is recorded below as SRS OPERATIONS — it is not this finding returning.
DOC QUOTATION     ⚠ STILL OPEN — re-verified 2026-09-12, unchanged, and structurally uncloseable. V24__fin_security_seed.sql:52-53, re-read at those exact lines today, still asserts that srs-fin.md's B4 "Actions:" lines for FIN_DIMENSIONS, FIN_RULES, FIN_RECURRING_TEMPLATES and FIN_ALLOCATION_RULES `say "DELETE (deactivate ..., modeled as UPDATE)"`. Re-measured today: `grep -c 'DELETE (deactivate' governance/modules/FIN/P1/srs-fin.md` returns 0 and `grep -c 'modeled as UPDATE' governance/modules/FIN/P1/srs-fin.md` returns 0 — the string occurs nowhere in srs-fin.md, in any spelling, and the further SRS narrowing done since has not introduced it either. V24 is applied and Flyway-checksummed, so it can NEVER be corrected at source, and a forward migration cannot amend a comment inside an earlier file; this self-check block and execution-state.json are the only mutable record. Any future session that meets V24:52-53 must treat that string as NOT srs text and re-read the real Operations/Actions lines — whose CURRENT line numbers are srs-fin.md:1177, :1235, :1281 and :1369, NOT the :1166/:1224/:1270/:1354 the previous revision of this line cited; every one of them moved when the SRS was renarrowed, which is itself the reason a quotation must never be carried by line number without re-opening the file. The CONCLUSION V24 draws from the false quotation — seed no PERM_FIN_*_DELETE rows — remains independently correct and is not in dispute; only its cited evidence is fabricated.
ERROR CAT COVER   ✓ CLOSED for the two rows it named, and re-verified against the code 2026-09-12 rather than accepted as done. FIN-404-YEAR's API column (_SECTIONS.md:410 and its P3_1 mirror) reads API-FIN-014, 017, 019, 020, 021, 027, 030, 031, and FIN-404-PERIOD's (:408 and mirror) reads API-FIN-014, 017, 019, 020, 024, 025, 026, 027, 029, 031 — note both row line numbers shifted by the FIN-409-NOT-ACTIVE row inserted at :393, and are restated here at their current values. Checked by re-grepping both constants across src/main/java/com/erp/fin/ and reading every hit: FIN_404_YEAR is thrown at ReportService.java:329, FiscalYearService.java:364 (successorOf) and :371 (findOrThrow — whose only caller is FiscalYearService.java:168, the year-end close, i.e. API-FIN-027 and NOT API-FIN-023), JournalEntryService.java:171 and JournalPostingService.java:152; FIN_404_PERIOD at RecurringTemplateService.java:284, ReportService.java:337, FiscalYearService.java:314 and :322, JournalEntryService.java:174, FiscalPeriodService.java:204 and JournalPostingService.java:208. Both columns cover every one of those paths. Report 404 behaviour re-read and correct: ReportService.assertFiscalYearExists resolves the REQUIRED fiscalYearId first on API-FIN-030/031, and trialBalance validates API-FIN-029's OPTIONAL periodId only `if (periodId != null)`. THIS LINE STAYS CLOSED ON ITS OWN TERMS — it was scoped to those two rows — but the same full-catalog sweep that re-verified it turned up a DIFFERENT coverage hole in the opposite direction, a constant with no catalog row at all; that is NOT this finding reopening and is carried separately as CATALOG GAP.
SRS OPERATIONS    ✓ CLOSED — every B1 Operations line named by the earlier revision is narrowed to what is built, each with its reason attached inline rather than silently deleted; all six re-opened and re-read 2026-09-12 AT THEIR CURRENT LINE NUMBERS, every one of which has MOVED since the previous revision recorded them (1128→1139, 1166→1177, 1224→1235, 1270→1281, 1354→1369, 1467→1484): srs-fin.md:1139 (SCR-REQ-FIN-001) reads "search, create, update, deactivate. No by-id read — deliberate v1 exclusion, see the note under B5". :1177 (SCR-REQ-FIN-002) reads "search, create (dimension — no deactivate, deliberate; see B4); search, create, deactivate (value — API-FIN-035)". :1235 (SCR-REQ-FIN-003) reads "search, create, deactivate (rule — API-FIN-034); create (line). As built there is no update and no by-id read on either, and no line delete — see B4". :1281 (SCR-REQ-FIN-004) and :1369 (SCR-REQ-FIN-005) name exactly API-FIN-012/013/014/036 and API-FIN-015/016/017/037 — everything their controllers publish. :1484 (SCR-REQ-FIN-007) reads "create (year); search — PERIODS only (API-FIN-033); open, soft-close, hard-close (period); run year-end close. There is NO fiscal-YEAR search and no by-id read of either a year or a period". SCR-REQ-FIN-006 and -008 were never affected. === UPDATED 2026-09-12: the previous revision said :1270/:1354 carry "two explicit bold caveats, that deactivate is delivered but does NOT stop the run, and that update is still not built". Re-read today, ONE of those two caveats has been REWRITTEN, not merely moved: both lines now say deactivate "is DELIVERED ... and, since 2026-09-12, it DOES stop the template/rule from running — that defect is CLOSED, see B4", while the update caveat survives as "the ONLY open half of the original gap". That matches DEACTIVATE RUN below being closed and TEMPLATE/RULE UPD below staying open, which is why this line can still close honestly.
PLATFORM I18N     ⚠ PARTIALLY CLOSED — 5 of 6 handlers localized, 1 RESIDUE STILL OPEN; unchanged in substance since the previous revision and re-read at GlobalExceptionHandler.java today (127 lines total). RESOLVING THROUGH MessageSource: handleLocalizedException (:32-52), handleValidation (:54-68), handleDataIntegrity (:89-97), handleAccessDenied (:99-106) and handleUnexpected (:108-116), all via the private resolveMessage(String, Object[]) at :118-126. The keys they need exist in BOTH bundles, re-grepped today: INTERNAL_ERROR (messages.properties:15 / messages_ar.properties:12), ACCESS_DENIED (:16 / :13), VALIDATION_ERROR (:17 / :14), DATA_INTEGRITY_VIOLATION (:18 / :15). CommonErrorCodes carries all four constants (:9 VALIDATION_ERROR, :10 INTERNAL_ERROR, :11 ACCESS_DENIED, :12 DATA_INTEGRITY_VIOLATION) and the handlers use the constants, not string literals. The INTERNAL_ERROR wording conflict WAS decided, in favour of the BUNDLE text: the wire returns messages.properties:15 "An unexpected error occurred. Please try again later." instead of the handler's former "An unexpected error occurred", so English 500 bodies did move — stated plainly rather than glossed as a no-op. OPEN RESIDUE, re-confirmed today: handleMalformedRequestBody (:79-87) still hardcodes English at :84, `.message("The request body is malformed or does not match the expected structure")`, and its own javadoc says why — it emits the SAME wire code as handleValidation (VALIDATION_ERROR, :83) but a DIFFERENT sentence, and one bundle key cannot carry two messages. So an Arabic caller still receives English for a malformed request body, and only for that. Closing it is a CONTRACT change, not a localization change: either give this response its own wire code (e.g. MALFORMED_REQUEST_BODY) with its own pair of keys, or collapse the two messages into one. Platform-wide — SEC, MDL, FIN, CU, NOTIF and FILE alike — so still not FIN's to settle. Written up in governance/project-artifacts/platform-audit-widths-and-error-localization.md.
DEACTIVATE RUN    ✓ CLOSED 2026-09-12 — by FIN-409-NOT-ACTIVE plus the two `assertCanRun()` guards, each read in source before this line was written. The defect was that a template or allocation rule deactivated through API-FIN-036/037 still ran and still posted. IT NO LONGER DOES. THE ARTIFACTS THAT CLOSED IT, named individually because this block's own standing rule requires it: (a) the new error code, `public static final String FIN_409_NOT_ACTIVE = "FIN-409-NOT-ACTIVE";` at src/main/java/com/erp/fin/exception/FinErrorCodes.java:441, with its two bundle entries (messages.properties and messages_ar.properties both carry the `FIN-409-NOT-ACTIVE` key — verified by the 40/40/40 three-way set diff under API (R3)); (b) `RecurringTemplateDomain.assertCanRun()` at src/main/java/com/erp/fin/domain/RecurringTemplateDomain.java:71-76, which throws `new LocalizedException(Status.CONFLICT, FinErrorCodes.FIN_409_NOT_ACTIVE, recurringTemplatePk)` when `!active` — RecurringTemplateDomain is itself NEW, FIN's 8th Domain class; (c) `AllocationRuleDomain.assertCanRun()` at src/main/java/com/erp/fin/domain/AllocationRuleDomain.java:191-196, the same shape with allocationRulePk; (d) the two call sites that make them live, RecurringTemplateService.java:206 (`RecurringTemplateDomain.from(template).assertCanRun();`, API-FIN-014) and AllocationRuleService.java:182 (`domain.assertCanRun();`, API-FIN-017) — both re-read today; and (e) TC-FIN-106 and TC-FIN-107, FLIPPED in backend-test-plan-fin.md to assert the 409 rather than pin the defect (:1449, :1483). Status.CONFLICT maps to HTTP 409. TWO THINGS THIS CLOSURE MUST NOT BE READ AS: first, NO RULE-FIN-* STATES THIS GATE and none was invented to pretend otherwise — RULE-FIN-006/007/008/009 govern the CONTENT of what is posted, not a template's or rule's own lifecycle, and no REQ-FIN-* or AC-FIN-* specifies it either; the catalog row at _SECTIONS.md:393 says so in its own RULE column, which reads "(no RULE — recorded human decision, 2026-09-12)", and the test plan's traceability rows for TC-FIN-106/107 repeat it. This gate therefore rests ENTIRELY on a recorded human decision, which is exactly the authority the previous revision of this line said was required, and it was obtained rather than assumed. Second, the third alternative that entry offered — removing isActiveFl from the search allow-list — was NOT taken and was not part of the decision; the flag remains searchable.
TEMPLATE/RULE UPD ⚠ STILL OPEN — a recurring template and an allocation rule CANNOT BE CORRECTED after creation. Re-measured 2026-09-12 by listing every mapping in both controllers: RecurringTemplateController publishes exactly four (POST create, POST /{id}/run, PUT /{id}/deactivate, POST /search) and AllocationRuleController exactly four (the same shape). There is no PUT /{id}, no line- or target-level endpoint of any kind (lines and targets travel inside the create body only), and the matching services expose no update method. THE PRACTICAL CONSEQUENCE HAS CHANGED FOR THE BETTER BUT THE GAP HAS NOT CLOSED: the previous revision said a typo could only be worked around by creating a replacement and deactivating the original, "which, per DEACTIVATE RUN above, does not actually stop the original from running". That second clause is now FALSE — deactivate does stop the run — so the workaround is at last sound. The gap itself is untouched: there is still no way to CORRECT a template or rule in place, only to replace it. Recorded as a KNOWN GAP WITH NO DERIVABLE REQUIREMENT: srs-fin.md:1281 and :1369 say outright that update "is still NOT built and is now the ONLY open half of the original gap", and no REQ-FIN-*, AC-FIN-* or RULE-FIN-* specifies update semantics for either aggregate (what happens to an in-flight schedule, whether past runs are re-derived, whether a target set may shrink), so no session can derive one. Needs a human to either write the requirement or record the exclusion the way the dimension and rule-line exclusions were recorded.
MIRROR DIVERGENCE ⚠ STILL OPEN, PRE-EXISTING and outside this session's scope. The two supposedly-mirrored copies of the API-FIN-019 block are still NOT identical. Re-measured 2026-09-12 by extracting each block between its own `API:API-FIN-019:START` and `API:API-FIN-019:END` markers and diffing (written here WITHOUT their `<!--`/`-->` delimiters on purpose: a quoted marker inside prose is a real marker to the parser, and this line used to make `gov.py analyze` report API-FIN-019 as duplicated, unclosed and illegally nested at the document root — three CRITICALs and a MAJOR raised by a sentence that only described a marker): SVC-API-CRUD.md:180-222 is 43 lines, P3_1/backend-execution-plan-fin.md:979-1011 is 33 lines (the P3_1 range has MOVED — the previous revision cited :977-1009), and `diff` reports 12 changed lines, 11 on the CRUD side and 1 on the P3_1 side. The substance is unchanged: a 10-line `Numbering:` paragraph (docNo format, the VARCHAR(30) width argument, the per-fiscalYearId counter, UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO, and the explicit "no platform numbering engine exists in this repo") is present ONLY in SVC-API-CRUD.md at :199-208, and the Orchestration line differs correspondingly, the package copy reading "generate docNo (FIN-local generator)" where P3_1 inlines it as "generate docNo (FIN-local generator, `JV-{fiscalYearCode}-{NNNNNN}`)". No fact contradicts the other — P3_1 carries LESS detail, not different detail — so nothing downstream is wrong today; the risk is that a future session reading only P3_1 re-derives the numbering scheme, which is exactly the failure BINDING records. NOT FIXED HERE: this session's scope is this self-check block, execution-state.json and one project-artifacts report, and the divergence sits in the API blocks, outside all three. The fix is mechanical — copy the `Numbering:` paragraph into P3_1 and re-align the Orchestration line, then re-verify byte-equality — but it must be done by a session authorized to edit those blocks. Note this ALIGN block itself IS byte-identical across both files, verified by md5 before and after this revision.
V22 HEADER COUNT  ⚠ STILL OPEN, lowest severity here and deliberately left alone. V22__fin_schema.sql:4, opened and read at that line 2026-09-12, still reads verbatim: `-- Target: POSTGRESQL_16 | 14 tables, 14 sequences | 146 DBF-IDs | 1 XM (SOFT-READ -> MDL)`. "146 DBF-IDs" has been stale since V23__fin_account_retained_earnings_flag.sql added DBF-FIN-147; the current count is 147, re-counted today. It is a HEADER COMMENT in the migration file, not a `COMMENT ON` statement, so it was never written into the database and no live object misreports anything — which is precisely why V29 deliberately did NOT touch it: V29 corrects only the two statements that ARE in the live catalog, and a forward migration cannot rewrite an earlier file's header in any case. V22 is applied and immutable, so this can never be corrected at source; it is recorded here so no future session quotes "146 DBF-IDs" as the current count. === NOTE 2026-09-12, and it is a curiosity rather than a repair: the SAME header's "1 XM (SOFT-READ -> MDL)" has become ACCIDENTALLY CORRECT AGAIN. It was accurate when V22 was written, went stale when XM-FIN-002 was registered at ALIGN-BE, and is accurate once more now that XM-FIN-002 is retired and XM-FIN-001 is the whole live set. Nothing was fixed; the world moved back. The DBF half is still wrong, so this finding stays open — and no session may cite the XM half as evidence that the header is reliable. Separately re-confirmed today: 16 `^COMMENT ON COLUMN.*XM-FIN-001` lines in V22, unchanged.
SOD DEAD CODE     ⚠ NEW OPEN FINDING — FIN-403-SOD-VIOLATION is a live constant and a live pair of bundle rows with NO THROW SITE ANYWHERE. Measured 2026-09-12, three greps, all over src/main/java/ and src/main/resources/i18n/: the constant is declared at src/main/java/com/erp/fin/exception/FinErrorCodes.java:78 (`public static final String FIN_403_SOD_VIOLATION = "FIN-403-SOD-VIOLATION";`); the message keys are live in BOTH bundles, messages.properties:142 and messages_ar.properties:139; and `grep -rn 'FIN_403_SOD_VIOLATION' src/main/java/` returns exactly TWO hits, the declaration itself and a `{@link}` javadoc reference at FinErrorCodes.java:392 — NOT ONE `throw`. Its only former throw sites were FinSeparationOfDutiesService (deleted) and FiscalPeriodDomain.assertCanHardClose (deleted with it). The Error Catalog row was struck at _SECTIONS.md:407, following the FIN-503 precedent, BUT the constant and the two bundle entries were DELIBERATELY LEFT IN PLACE by the catalog session — that is the divergence recorded here, not an accusation of oversight. WHY IT IS A FINDING AND NOT NOISE: it makes the three-way 40/40/40 code count under API (R3) include one code no caller can ever receive, so any future session diffing constants against reachable behaviour will re-discover it; and a struck catalog row beside a live constant is exactly the shape that invites someone to "restore" the rule. WHAT MUST NOT HAPPEN: nobody may re-add a throw for it. RULE-FIN-015 is satisfied by the @PreAuthorize gate alone (see DECISIONS), and re-introducing a SoD check is the precise thing FiscalPeriodDomain.java:110-117's "DO NOT RESTORE THE PREVIOUS IMPLEMENTATION" note forbids. The open question for a human is only whether to retire the constant and the two bundle rows too, or keep them as the struck row's counterpart; this session invented no answer.
SEC DEAD CHAIN    ⚠ NEW OPEN FINDING, and it is OUTSIDE FIN — reported here because FIN's change caused it, and fixed here by nobody, because it is SEC's code. Deleting FinSeparationOfDutiesService removed the only PRODUCTION caller of a three-link chain in SEC. Traced 2026-09-12 with `grep -rn findUserIdsHoldingPermission src/`, every hit read: the JPQL query `RoleActionGrantRepository.findUserIdsHoldingPermission` (src/main/java/com/erp/sec/repository/RoleActionGrantRepository.java:124) is called only by `UserService.findUserIdsHoldingPermission` (:199-203), which is called only by `SecUserDirectoryApiImpl.findUserIdsHoldingPermission` (:26-27), which implements `SecUserDirectoryApi.findUserIdsHoldingPermission` (:25) — and the ONLY remaining callers of that interface method anywhere are four assertions in src/test/java/com/erp/sec/SecCoverageIntegrationTest.java (:438, :442, :447, :452). Zero production call sites. That is an A.2.9 dead-code condition of exactly the kind this block's own QRC line deleted four FIN repository methods for — with the difference that a test still exercises it, so it is not unreachable, merely unused. NOT ACTIONED, and deliberately: this is SEC's module record, not FIN's, and FIN's ALIGN block has no authority to delete SEC code or to decide that SEC's published crossmodule contract should shrink because its only consumer went away. Note also that RoleActionGrantRepository.java:115's javadoc still names `UserService.findUserIdsHoldingPermission` as its caller under "(A.2.9)", which is true one link up but no longer true end-to-end. For a human: either keep the method as published SEC API with no current consumer (legitimate — `SecUserDirectoryApi.findContact` is in the same position, with no production consumer outside SEC today), or retire both. FIN has no stake in the answer.
CATALOG GAP       ⚠ NEW OPEN FINDING — FIN-422-INVALID-PERCENTAGE-VALUE is a registered, thrown, fully-bundled error code with NO ERROR CATALOG ROW. Measured 2026-09-12 by extracting the 41 codes in the catalog table's first column (_SECTIONS.md:378-418) and `comm`-diffing them against the 40 `"FIN-*"` literals in FinErrorCodes.java: the constants-minus-catalog set is exactly one element, FIN-422-INVALID-PERCENTAGE-VALUE. It is not a phantom — the constant is at FinErrorCodes.java:357, it IS thrown, at EventTypeRuleDomain.java:267 inside `sourcedAmount(...)` when `new BigDecimal(amountSourceValue)` raises NumberFormatException for a PERCENTAGE-sourced rule line, and both bundles carry the key (messages.properties:170, messages_ar.properties:167). `grep -n 'INVALID-PERCENTAGE' _SECTIONS.md` and the same over P3_1 both return ZERO, so the row is missing from BOTH mirrors identically — this is an omission, not a divergence. The test plan already noticed and covered it: TC-FIN-109 was added 2026-09-12 expressly to close the coverage half. What remains uncovered is the catalog half. NOT FIXED HERE because the Error Catalog table lies outside this session's scope (this block, execution-state.json and one project-artifacts report); the fix is mechanical and must be applied to BOTH mirrors — add one row reading code FIN-422-INVALID-PERCENTAGE-VALUE, RULE-FIN-010 (build half), API-FIN-020 and API-FIN-011, HTTP 422, with the trigger and the ar+en text taken from the bundles rather than reworded. Until then the API (R3) line's "41 catalog rows / 40 constants" must be read as a 40-row overlap plus two catalog-only entries and one constant-only entry, not as a superset relation.
INPUT VALIDATION  ⚠ NEW OPEN FINDING — `RuleLineCreateRequest.amountSourceValue` accepts any string, which is the whole reason FIN-422-INVALID-PERCENTAGE-VALUE is reachable at all. Read in source 2026-09-12 at src/main/java/com/erp/fin/dto/RuleLineCreateRequest.java:41-42: the field is declared `private String amountSourceValue;` under a single `@Schema(description = "Amount source value - قيمة مصدر المبلغ", example = "netAmount")` and NOTHING ELSE — no @NotBlank, no @Size, no @Pattern, no format constraint of any kind, in contrast with the neighbouring amountSourceTypeCode which carries @Size(max = 20). THE CONSEQUENCE, traced end to end: API-FIN-011 (create rule line) persists whatever arrives, including a value that can never be parsed as a decimal, on a line whose amountSourceTypeCode is PERCENTAGE. Nothing rejects it at write time. The failure surfaces only much later, at API-FIN-020 (post from event), when EventTypeRuleDomain.sourcedAmount(...) reaches `new BigDecimal(amountSourceValue)` at EventTypeRuleDomain.java:265-268 and converts the NumberFormatException into FIN-422-INVALID-PERCENTAGE-VALUE. So a configuration error committed on one screen is reported as a posting failure on another, to a different user, possibly much later — and the stored rule stays broken, because there is no update endpoint for a rule line either (FIN publishes create-only on rule lines; see SCOPE vs SRS). This is a REAL INPUT-VALIDATION GAP, not a documentation defect. NOT FIXED HERE: adding a constraint changes the API contract for API-FIN-011 (a previously-accepted body would start returning 400 VALIDATION_ERROR), and the correct constraint is conditional — amountSourceValue means a field NAME for a FIELD-sourced line and a NUMBER for a PERCENTAGE-sourced one, so a flat @Pattern is wrong and a class-level cross-field validator is a design decision no RULE-FIN-* states. For a human: either add the conditional validation at API-FIN-011 and downgrade FIN-422-INVALID-PERCENTAGE-VALUE to a defence-in-depth path, or accept late failure and say so in the SRS. This session invented neither.
RESULT            BLOCKED ✗ — 30 findings
SELF-CHECK        PASSED WITH FINDINGS — 9 open, 0 blocking the phase, 0 unverified lines. THE COUNT ROSE FROM 6 TO 9 AND THAT IS NOT A REGRESSION: one finding CLOSED, four were ADDED by a sweep the previous revision had not run, and the remainder carried. Line by line, because this block's own standing rule requires every movement to be named. CLOSED (1): DEACTIVATE RUN — closed by FinErrorCodes.java:441 (FIN-409-NOT-ACTIVE) plus its two bundle keys, RecurringTemplateDomain.java:71-76 and AllocationRuleDomain.java:191-196 (the two assertCanRun() guards), their call sites at RecurringTemplateService.java:206 and AllocationRuleService.java:182, and the flipped TC-FIN-106/107; it rests on a RECORDED HUMAN DECISION and on no RULE-FIN-*, which the catalog row at _SECTIONS.md:393 states in its own RULE column. CARRIED, UNCHANGED IN SUBSTANCE (4): DOC QUOTATION (V24:52-53, applied and immutable, structurally uncloseable — its cited srs line numbers refreshed today); PLATFORM I18N (residue — the malformed-request-body handler at GlobalExceptionHandler.java:79-87, which cannot be localized without a wire-contract change); TEMPLATE/RULE UPD (neither aggregate can be corrected after creation; its workaround clause corrected, since deactivate now does stop the run); MIRROR DIVERGENCE (the `Numbering:` paragraph still present only in SVC-API-CRUD.md; P3_1 range refreshed to :979-1011); V22 HEADER COUNT (`146 DBF-IDs` still stale; its XM half became accidentally correct again, which repairs nothing). ADDED (4), each verified against the real artifact before being written: SOD DEAD CODE, SEC DEAD CHAIN, CATALOG GAP, INPUT VALIDATION. THE NINE OPEN ARE THEREFORE: DOC QUOTATION, PLATFORM I18N (residue), TEMPLATE/RULE UPD, MIRROR DIVERGENCE, V22 HEADER COUNT, SOD DEAD CODE, SEC DEAD CHAIN, CATALOG GAP, INPUT VALIDATION. Of those, INPUT VALIDATION is the only one that is a defect in shipped behaviour rather than a documentation, history or dead-code divergence; SEC DEAD CHAIN is the only one outside FIN entirely. MEASUREMENTS THAT MOVED THIS REVISION, each stated on its own line above and each the measurement winning over the inherited claim: error codes 38/38/38 → 40/40/40; Error Catalog rows 39 → 41; @PreAuthorize annotations 43 → 42; XM 2 → 1; Domain classes 7 → 8; test-case ids 108 → 109 (108 in force, TC-FIN-091 retired); and every srs-fin.md Operations line number, all six of which shifted. Re-measured and UNCHANGED: 37 endpoints, 147 DBF ids, 49 QR ids, 27 PERM_FIN_* constants against 27 registered action rows, 16 XM-FIN-001 COMMENT ON COLUMN lines in V22, 22 AuditableEntity subclasses split 16/6 on audit width. ONE CLAIM INHERITED FROM THE HAND-OFF WAS CHECKED AND FOUND FALSE, and is recorded so it is not re-asserted: FiscalPeriodService.java:135 was reported as a stale javadoc still naming FinSeparationOfDutiesService and XM-FIN-002. It is NOT stale. Read at :131-135 today, it is a deliberate past-tense removal note — "A previous implementation resolved facts from SEC's user directory here ... It was removed by an explicit human decision, together with FinSeparationOfDutiesService and FIN's XM-FIN-002 dependency on SEC" — under a "Do not add a SoD check back into this body" warning. FiscalYearService.java:156 and FiscalPeriodDomain.java:110-117 carry the same deliberate note. Nothing was changed there. STANDING RULE, STRENGTHENED AGAIN: this block must NEVER be returned to "PASSED ✓ — 0 findings" while any finding above still stands. The open count must never be lowered without naming, ON THAT FINDING'S OWN LINE, the specific artifact — file and line, migration, or commit — that closed it; DEACTIVATE RUN above is the worked example of what that looks like, and the bar it sets is the bar. "Re-verified and now fine" is not a closure. A closure that rests on a human decision rather than on a stated requirement MUST say so and MUST say that no RULE-FIN-* states it, as DEACTIVATE RUN does. A closure asserted against a migration that has not been applied MUST say so, as SCHEMA COMMENT does. ADDING a finding is always permitted and needs no authority; REMOVING one is not, and a finding may be struck only by a session that RE-MEASURED it from the artifact, never by one that inherited the claim. Every line number quoted in this block was opened today; where a previously-recorded line number had moved, the line says both the old and the new value rather than silently substituting — carry that habit forward, because three separate line-reference sets drifted in a single day. === STRUCTURAL NOTE 2026-09-12: this narrative used to BE the `RESULT` line, and that made the artifact fail `verdict-agrees` (C7.15, CRITICAL) for a reason that had nothing to do with its content. The check reads the first number after the label and compares it with what `gov.py analyze` produced FOR THIS ARTIFACT; it read the “9 open” of this block’s own self-check and compared it against the machine’s 30, and 9 < 30 is a claim of fewer findings than the evidence. THE TWO NUMBERS COUNT DIFFERENT THINGS AND NEITHER IS WRONG: the machine’s count is contract clauses failing over this file (C7.19 required-writer dominates it), while the 9 here are the substantive findings this block tracks by name. So the machine verdict now has the `RESULT` label to itself, one short line the orchestrator can rewrite from the report at every `run-stage --complete` without touching a word of this narrative, and the narrative keeps its own label. DO NOT merge them back: restoring the paragraph to the `RESULT` line would both re-raise the CRITICAL and put this entire record one `_stamp_verdict()` call away from being overwritten by a single generated sentence.
```

**Coverage — ENT/DBF → phases → QR → XM**: every ENT-FIN-001..014 appears in exactly one
DATA-DOM entity block with ≥1 QR cited under REPOSITORY OPS; every DBF-FIN-001..147
appears in the DB Alignment Manifest and its owning entity's block; XM-FIN-001 appears in
INT-C, INT-R and every lookup-backed field's manifest row, and is the whole live XM set.
XM-FIN-002 survives only as a struck historical block in INT-C and INT-R (RETIRED 2026-09-12)
and binds no manifest row — no column ever carried it.

**Coverage — RULE → API → catalog code**: RULE-FIN-001→API-FIN-002/003→
FIN-409-PARENT-NOT-LEAF-ELIGIBLE/FIN-409-HAS-CHILDREN · RULE-FIN-002→API-FIN-007→
FIN-409-DIMVALUE-DUP · RULE-FIN-003→API-FIN-011/016→FIN-409-REMAINDER-COUNT, FIN-422-REMAINDER-MARKER ·
RULE-FIN-004→API-FIN-020→FIN-409-DUPLICATE-EVENT · RULE-FIN-005→API-FIN-020→
FIN-404-NO-ACTIVE-RULE · RULE-FIN-006→API-FIN-019/020/014/017→FIN-409-UNBALANCED ·
RULE-FIN-007→(same APIs)→FIN-409-NOT-POSTABLE-ACCOUNT · RULE-FIN-008→(same)→
FIN-409-PERIOD-NOT-OPEN · RULE-FIN-009→(same)→FIN-409-INVALID-DIMENSION ·
RULE-FIN-010→API-FIN-020/014/017→FIN-422-REMAINDER-NOT-POSITIVE, FIN-422-REMAINDER-MARKER (the per-side computation itself is success-path; these two reject a distribution that leaves no positive residue, and a line whose remainder marker is ambiguous) ·
RULE-FIN-011→API-FIN-021→(no distinct code — success-path build) ·
RULE-FIN-012→API-FIN-021→(no distinct code — success-path period substitution) ·
RULE-FIN-013→API-FIN-021/014→FIN-409-NOT-POSTED, FIN-409-ALREADY-REVERSED ·
RULE-FIN-014→API-FIN-024/026→
FIN-409-NOT-REOPENABLE · RULE-FIN-015→API-FIN-026/027→(no code — satisfied by the distinct
`PERM_FIN_PERIODS_CLOSE_APPROVE` gate, exactly as the rule states it; FIN-403-SOD-VIOLATION
struck 2026-09-12 with the service-layer check that threw it) ·
RULE-FIN-016→(every posted-entry endpoint)→(enforced by omission, no code needed — no
UPDATE/DELETE mapping exists on a POSTED row) ·
RULE-FIN-017→API-FIN-019→FIN-400-PERIOD-NOT-IN-YEAR, FIN-400-DOCDATE-OUTSIDE-PERIOD.
One catalog code deliberately appears in NO line above: `FIN-409-NOT-ACTIVE` (API-FIN-014,
API-FIN-017) has no RULE-FIN-* behind it. The active gate it enforces rests on a recorded
human decision of 2026-09-12, not on stated requirement — see its Error Catalog row and
SVC-API-CRUD's API-FIN-036/037 blocks, and do not read it as pre-existing spec.

**Coverage — XM → status → blocks → workaround**: XM-FIN-001 → ACTIVE → blocks none → no
workaround needed. That is the whole live set. XM-FIN-002 → RETIRED 2026-09-12 → blocks none →
no workaround needed: `FinSeparationOfDutiesService`, the only caller, was deleted with the SoD
over-implementation, so there is no directory read left to fail.

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
**QR-FIN-019** — FIND_ONE load the template to run, by id [ENT-FIN-011, API-FIN-014]
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
**QR-FIN-035** — EXISTS original entry is POSTED and not already reversed (RULE-FIN-013) [ENT-FIN-004, API-FIN-021, API-FIN-014]
**QR-FIN-036** — FIND_ONE current open period for reversal (RULE-FIN-012) [ENT-FIN-008, API-FIN-021]
**QR-FIN-037** — FIND_ONE read one entry with lines [ENT-FIN-004, API-FIN-022]
**QR-FIN-038** — SAVE create fiscal year + periods [ENT-FIN-007, ENT-FIN-008, API-FIN-023]
**QR-FIN-039** — UPDATE open/soft-close/hard-close period [ENT-FIN-008, API-FIN-024, API-FIN-025, API-FIN-026]
**QR-FIN-040** — EXISTS period not already Hard Closed (RULE-FIN-014) [ENT-FIN-008, API-FIN-024, API-FIN-026]
**QR-FIN-041** — AGGREGATE year-end closing/opening balances [ENT-FIN-004, ENT-FIN-005, API-FIN-027]
**QR-FIN-042** — FIND_BY_CRITERIA account ledger POSTED lines; running balance accumulated in the service [ENT-FIN-005, API-FIN-028]
**QR-FIN-043** — AGGREGATE trial balance / balance sheet / income statement account balances [ENT-FIN-005, API-FIN-029, API-FIN-030, API-FIN-031]
**QR-FIN-044** — AGGREGATE dimension report [ENT-FIN-005, ENT-FIN-006, API-FIN-032]
**QR-FIN-045** — FIND_ONE the Retained Earnings account (DBF-FIN-147) [ENT-FIN-001, API-FIN-027]
**QR-FIN-046** — EXISTS dimension code unique [ENT-FIN-002, API-FIN-006]
**QR-FIN-047** — EXISTS fiscal year code unique [ENT-FIN-007, API-FIN-023]
**QR-FIN-048** — FIND_ONE next fiscal year by startDate [ENT-FIN-007, API-FIN-027]
**QR-FIN-049** — FIND_BY_CRITERIA every period of one fiscal year [ENT-FIN-008, API-FIN-023, API-FIN-027, API-FIN-014]

## XM id definitions
**XM-FIN-001** — SOFT-READ every FIN lookup-backed column → MDL_LOOKUP_VALUE [REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031]
**~~XM-FIN-002~~** — RETIRED 2026-09-12, id burned and not reused. Was: READ SEC's user→permission directory (`SecUserDirectoryApi.findUserIdsHoldingPermission`) for a global user-set-disjointness check that RULE-FIN-015 does not require; retired when `FinSeparationOfDutiesService` was deleted [REQ-FIN-037, REQ-FIN-038]

## Registry content
See `registry-exec-be-fin.md`.
══════════════════════════════════════════════════════════════════
