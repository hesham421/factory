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

**Numbering**: `docNo` format is `JV-{fiscalYearCode}-{NNNNNN}` — literal prefix `JV-`, the
owning fiscal year's `code` (DBF-FIN-066, VARCHAR(10)), `-`, then a zero-padded 6-digit
counter starting at `000001`; e.g. `JV-2026-000123` (worst case 20 chars, inside
`doc_no VARCHAR(30)`). The counter is scoped per `fiscalYearId` and restarts at `000001`
for each new fiscal year — one counter for all journal types, never segmented by
`journalTypeCode`; `UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO (fiscal_year_id, doc_no)` backs the
uniqueness guarantee at the database level. Generated by a FIN-local generator in
`com.erp.fin`, deliberately NOT a shared `com.erp.common` component: no other module needs
document numbering today, so a general shared interface would be speculative — promote it
to `common` only if and when a second real consumer appears. This is a conscious, recorded
deviation from the profile's standing guidance that numbering "comes from the platform
numbering engine; never generated in a module" — that guidance presumes an engine which
does not exist in this repo, making literal compliance impossible. Assigned once on create,
immutable thereafter — excluded entirely from every create/update request DTO, present
only in responses.

**Workflow engine**: forbidden — every lifecycle below (JournalEntry, FiscalPeriod) is a
plain guarded transition, never a workflow definition.

**Languages**: every name field and catalog message present in ar + en.

**Cross-module contract placement**: XM-FIN-001 (SOFT-READ → MDL) is implemented in FIN's
service layer by injecting MDL's published cross-module interface
`com.erp.mdl.crossmodule.MdlLookupApi` directly — in-process Spring interface injection
within the single deployable, never a loopback HTTP call to API-MDL-011. FIN calls
`readActiveValuesByKey(String typeKey)` and consumes the narrow read-model record
`com.erp.mdl.crossmodule.LookupOptionView` (code, labelAr, labelEn, sortOrder) — never a
`LookupValue` entity or an MDL-internal DTO; a submitted code is validated by membership in
that returned list. Same pattern as the delivered `NotificationLookupService` and
`FileLookupService`. FIN's own dependency on SEC for identity/authorization uses the identical
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
FIELDS: DBF-FIN-001..013 + DBF-FIN-147 (`isRetainedEarningsFl`, REQ-FIN-036 — see API-FIN-027) — see DB Alignment Manifest; `accountTypeCode`/`natureCode` are
lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request excludes {accountPk, isActiveFl, audit}; update-request
excludes {accountPk, code, isActiveFl, audit} (code immutable, matching MDL's own `key`
precedent); response includes all.
LOOKUP FIELDS: `accountTypeCode`→`ACCOUNT_TYPE`, `natureCode`→`DEBIT_CREDIT`, both validated
in the service layer via injected `MdlLookupApi.readActiveValuesByKey(<key>)` (XM-FIN-001) —
stored as code, never a numeric FK.
DOMAIN RULES: **RULE-FIN-001** (full text: srs-fin.md §A5) — Scope ENT-FIN-001 · Trigger:
on update (`isLeafFl`) · DB enforcement: application layer (QR-FIN-006) · owner layer:
service.
STATE MACHINE: `isActiveFl` binary only — not applicable.
CROSS-MODULE: `accountTypeCode`/`natureCode` touch XM-FIN-001.
REPOSITORY OPS → QR-FIN-001, QR-FIN-002, QR-FIN-003, QR-FIN-004, QR-FIN-005, QR-FIN-006,
QR-FIN-045 (FIND_ONE the Retained Earnings account, DBF-FIN-147 — API-FIN-027).

#### ENT-FIN-007 — FiscalYear      kind: master
BINDINGS: table `FIN_FISCAL_YEAR` · PK `fiscalYearPk` (DBF-FIN-065) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-065..074 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request `{code, startDate, endDate, periodCount}` (periodCount is a
transient input driving REQ-FIN-031's period-generation, not a persisted column); response
includes all persisted fields plus the generated periods.
DOMAIN RULES: **a CLOSED year is never closed again** — the year-end close's own re-run
guard, scoped to `statusCode` alone and therefore owned by `FiscalYearDomain` (ALIGN-BE;
`FIN-409-INVALID-TRANSITION`, reusing the catalog's existing invalid-transition row). Amends
this block's earlier "none scoped alone": the rest of year-end close (REQ-FIN-036) is still
orchestrated at the API layer over both FiscalYear and FiscalPeriod — see API-FIN-027 — and
this remains the entity's ONLY Domain object (A.0.7).
STATE MACHINE: `statusCode` (FISCAL_YEAR_STATUS) — OPEN→CLOSED, set once by REQ-FIN-036 —
binary, not applicable for a diagram (SRS A7).
CROSS-MODULE: `statusCode` touches XM-FIN-001.
REPOSITORY OPS → QR-FIN-038 (SAVE, with periods), QR-FIN-041 (AGGREGATE, year-end),
QR-FIN-047 (EXISTS, code unique), QR-FIN-048 (FIND_ONE, next year by startDate).

#### ENT-FIN-008 — FiscalPeriod      kind: master
BINDINGS: table `FIN_FISCAL_PERIOD` · PK `fiscalPeriodPk` (DBF-FIN-075) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-075..088 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: no direct create (generated with the year, REQ-FIN-031); transition
endpoints only (open/soft-close/hard-close) take just `{id}`; response includes all.
DOMAIN RULES:
**RULE-FIN-008** (srs-fin.md §A5) — period-open-at-post-time, except the year-end closing and
opening entries, which the rule itself exempts (REQ-FIN-036 / API-FIN-027) — DB enforcement:
application layer (QR-FIN-031) · owner layer: service.
**RULE-FIN-014** (srs-fin.md §A5) — reject reopening a Hard Closed period — DB enforcement:
application layer (QR-FIN-040) · owner layer: service.
**RULE-FIN-015** (srs-fin.md §A5) — close-approval permission distinct from entry-creation
permission — DB enforcement: application layer (service, reading SEC role/grant data,
Phase 1 CORE) · owner layer: service.
STATE MACHINE: `statusCode` (PERIOD_STATE) per SRS A7 — OPEN⇄SOFT_CLOSE→HARD_CLOSE→YEAR_END_CLOSE.
CROSS-MODULE: `statusCode` touches XM-FIN-001; the SoD check (RULE-FIN-015) reads SEC role
data (not a formal XM row — platform-standard integration, ADR-FIN-001).
REPOSITORY OPS → QR-FIN-038 (SAVE, with year), QR-FIN-039 (UPDATE, transitions), QR-FIN-040 (EXISTS),
QR-FIN-049 (FIND_BY_CRITERIA, every period of one year).
<!-- SUB:DATA-DOM-MASTER:END -->

<!-- SUB:DATA-DOM-TRANSACTIONAL:START traces=REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028 -->
### SUB — DATA-DOM-TRANSACTIONAL

#### ENT-FIN-004 — JournalEntry      kind: transactional
BINDINGS: table `FIN_JOURNAL_ENTRY` · PK `journalEntryPk` (DBF-FIN-034) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: **docNo** · column `doc_no` (DBF-FIN-035) · format:
`JV-{fiscalYearCode}-{NNNNNN}` (e.g. `JV-2026-000123`), counter scoped per `fiscalYearId`
and restarting at `000001` each fiscal year, single counter across all journal types
(`UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO`) · generation source: a FIN-local generator in
`com.erp.fin` (not `com.erp.common` — see CORE Numbering), invoked at create, before the
first save — excluded from every create/update request body, always present in responses.
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
**RULE-FIN-008** — period open at post, except the year-end closing/opening entries the rule
itself exempts (REQ-FIN-036 / API-FIN-027) — QR-FIN-031 — service (POL-FIN-004).
**RULE-FIN-011** — reversal exact and linked — QR-FIN-034 — service (POL-FIN-007).
**RULE-FIN-012** — reversal posts to current period if original's closed — QR-FIN-036 — service.
**RULE-FIN-013** — reject reverse of non-POSTED, and reject reversing an entry that already
carries a reversal link (double-reversal) — QR-FIN-035 — service.
**RULE-FIN-016** — lock after posting — enforced by omission (no UPDATE/DELETE mapping on
a POSTED row in the repository layer at all) — service/repository.
**RULE-FIN-017** — the submitted fiscalYearId, periodId and docDate must describe one
accounting context (the period belongs to that year, DBF-FIN-076; the date falls inside the
period, DBF-FIN-080/081) — API-FIN-019 only, since every system-generated entry derives the
three from one another — `JournalEntryDomain.assertHeaderCoherent(...)` (ALIGN-BE;
`FIN-400-PERIOD-NOT-IN-YEAR`, `FIN-400-DOCDATE-OUTSIDE-PERIOD`).
**RULE-FIN-013's second half under concurrency** — the "already reversed" read-then-write is
made atomic by a PESSIMISTIC_WRITE load of the original's header before the guard runs
(ALIGN-BE); no FIN entity carries `@Version`, so without it two concurrent reversals both
post a mirror.
(Full text of every RULE above: srs-fin.md §A5 — not restated here per the single-source rule.)
STATE MACHINE: `statusCode` (JOURNAL_STATUS) per SRS A7 — DRAFT→POSTED (RULE-FIN-016 locks
immediately); POSTED is terminal. Classic reversal (RULE-FIN-011): reversing an entry leaves the
original POSTED and posts an equal, opposite mirror entry, the two linked through
`originalEntryId`/`reversalEntryId` (DBF-FIN-042/043) — net ledger effect zero. No path sets VOID.
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
RULES: none scoped alone. REPOSITORY OPS → QR-FIN-007, QR-FIN-008, QR-FIN-046 (EXISTS, code unique).

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
**RULE-FIN-003** (exactly one remainder line whenever the line set is a compound or
percentage distribution — any sibling PERCENTAGE-distributed, or any line already marked
remainder — plus marker agreement: `isRemainderFl` (DBF-FIN-103) is the SINGLE remainder
marker, the one both this guard and the API-FIN-020 builder read, and must agree with the
line's own REMAINDER type code, `FIN-422-REMAINDER-MARKER`) — QR-FIN-016 —
`EventTypeRuleDomain`. REPOSITORY OPS → QR-FIN-015, QR-FIN-016; read as part of QR-FIN-025/028 at
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
**RULE-FIN-003** (reused — exactly one remainder target whenever the target set is a
compound or percentage distribution, plus marker agreement between `isRemainderFl`
(DBF-FIN-141, the SINGLE marker the API-FIN-017 builder reads) and `distributionTypeCode`,
`FIN-422-REMAINDER-MARKER`) — QR-FIN-016 (reused) — `AllocationRuleDomain`. REPOSITORY OPS → written with QR-FIN-021; read by
QR-FIN-022 at run time.
<!-- SUB:DATA-DOM-LOOKUP:END -->
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-FIN-001,REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028,REQ-FIN-036 -->
## PHASE 3 — SVC-API

API count = 32 ≥ 8 → split by threshold, grouped CRUD / SEARCH / INT.

<!-- SUB:SVC-API-SEARCH:START traces=REQ-FIN-001,REQ-FIN-004,REQ-FIN-007,REQ-FIN-022,REQ-FIN-027,REQ-FIN-031,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043 -->
### SUB — SVC-API-SEARCH (read-only)

<!-- API:API-FIN-001:START traces=REQ-FIN-001,DBF-FIN-002,DBF-FIN-003,DBF-FIN-004,DBF-FIN-005 -->
### API-FIN-001 — search accounts
Endpoint: POST /api/v1/fin/accounts/search · Layers: `AccountController.search`→`AccountService.search`
Request: body `AccountSearchRequest` — `code`(LIKE), `nameAr/nameEn`(LIKE), `accountTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AccountResponse>` · `ApiResponse<...>`
Validations: none (read-only) · Errors: `FIN-500`
Orchestration: load (QR-FIN-001) → map → return · Repository: QR-FIN-001 · join NONE · READ_ONLY
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_VIEW` · Localization: nameAr/nameEn returned
<!-- API:API-FIN-001:END -->

<!-- API:API-FIN-005:START traces=REQ-FIN-004,DBF-FIN-015,DBF-FIN-016,DBF-FIN-017 -->
### API-FIN-005 — search dimensions
Endpoint: POST /api/v1/fin/dimensions/search · Layers: `DimensionController.search`→`DimensionService.search`
Request: body `DimensionSearchRequest` — `code`(LIKE), paging · Response: 200 · `Page<DimensionResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-007 → map → return · Repository: QR-FIN-007 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-005:END -->

<!-- API:API-FIN-008:START traces=REQ-FIN-005,DBF-FIN-024,DBF-FIN-025,DBF-FIN-026,DBF-FIN-027 -->
### API-FIN-008 — search dimension values
Endpoint: POST /api/v1/fin/dimensions/values/search · Layers: `DimensionController.searchDimensionValues`→`DimensionValueService.search`
Request: body `DimensionValueSearchRequest` — `dimensionId`(EXACT, required) carried in the body filters and read by the child parent-id extractor (never a path variable); `code`(LIKE), paging · Response: 200 · `Page<DimensionValueResponse>`
Validations: none · Errors: `FIN-404-DIMENSION`
Orchestration: QR-FIN-011 → map → return · Repository: QR-FIN-011 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-008:END -->

<!-- API:API-FIN-009:START traces=REQ-FIN-007,DBF-FIN-090,DBF-FIN-091,DBF-FIN-092 -->
### API-FIN-009 — search event-type rules
Endpoint: POST /api/v1/fin/event-rules/search · Layers: `EventTypeRuleController.search`→`EventTypeRuleService.search`
Request: body `EventTypeRuleSearchRequest` — `eventTypeCode`(EXACT), `isActiveFl`(EXACT), paging · Response: 200 · `Page<EventTypeRuleResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-012 → map → return · Repository: QR-FIN-012 · join NONE · READ_ONLY
Security: screen FIN_RULES · `PERM_FIN_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-009:END -->

<!-- API:API-FIN-012:START traces=REQ-FIN-022,DBF-FIN-110,DBF-FIN-111,DBF-FIN-112 -->
### API-FIN-012 — search templates
Endpoint: POST /api/v1/fin/recurring-templates/search · Layers: `RecurringTemplateController.search`→`RecurringTemplateService.search`
Request: body `RecurringTemplateSearchRequest` — `nameAr/nameEn`(LIKE), `scheduleTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<RecurringTemplateResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-017 → map → return · Repository: QR-FIN-017 · join NONE · READ_ONLY
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-012:END -->

<!-- API:API-FIN-015:START traces=REQ-FIN-025,DBF-FIN-131,DBF-FIN-132,DBF-FIN-133 -->
### API-FIN-015 — search allocation rules
Endpoint: POST /api/v1/fin/allocation-rules/search · Layers: `AllocationRuleController.search`→`AllocationRuleService.search`
Request: body `AllocationRuleSearchRequest` — `nameAr/nameEn`(LIKE), `sourceAccountId`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AllocationRuleResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-020 → map → return · Repository: QR-FIN-020 · join NONE · READ_ONLY
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-015:END -->

<!-- API:API-FIN-018:START traces=REQ-FIN-027,DBF-FIN-035,DBF-FIN-036,DBF-FIN-040 -->
### API-FIN-018 — search journal entries
Endpoint: POST /api/v1/fin/journal-entries/search · Layers: `JournalEntryController.search`→`JournalEntryService.search`
Request: body `JournalEntrySearchRequest` — `docNo`(LIKE), `docDate`(DATE_RANGE), `periodId`(EXACT), `statusCode`(EXACT), `journalTypeCode`(EXACT), paging
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
Validations: RULE-FIN-006 restated as a report-level guarantee (POL-FIN-008: the sums always match because every contributing entry individually balanced — no separate check needed, an invariant by construction). `periodId` is an OPTIONAL narrowing, validated ONLY when supplied: omitting it means "no period narrowing" and stays a 200 (AC-FIN-040's happy path) — it is NOT mandatory
Errors: `FIN-404-PERIOD` (supplied `periodId` does not resolve), `FIN-500`
Orchestration: QR-FIN-043 (POSTED lines only, live, grouped by account) → apply nature sign → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_TRIAL_BALANCE · `PERM_FIN_TRIAL_BALANCE_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-029:END -->

<!-- API:API-FIN-030:START traces=REQ-FIN-041,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-030 — balance sheet
Endpoint: GET /api/v1/fin/reports/balance-sheet · Layers: `ReportController.balanceSheet`→`ReportService.balanceSheet`
Request: `fiscalYearId`(EXACT), `asOfDate` · Response: 200 · grouped ASSET/LIABILITY/EQUITY balances
Validations: none (continuity itself is guaranteed by REQ-FIN-036's opening-entry generation, not re-validated at read time). The REQUIRED `fiscalYearId` is resolved FIRST, before any aggregation
Errors: `FIN-404-YEAR` (unknown `fiscalYearId` — previously a silent 200 carrying an all-zero statement), `FIN-500`
Orchestration: QR-FIN-043 (accountTypeCode IN ASSET,LIABILITY,EQUITY) → group → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_BALANCE_SHEET · `PERM_FIN_BALANCE_SHEET_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-030:END -->

<!-- API:API-FIN-031:START traces=REQ-FIN-042,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-031 — income statement
Endpoint: GET /api/v1/fin/reports/income-statement · Layers: `ReportController.incomeStatement`→`ReportService.incomeStatement`
Request: `fiscalYearId`(EXACT), period range · Response: 200 · grouped REVENUE/EXPENSE balances
Validations: none (zero-opening is guaranteed by REQ-FIN-036 closing result accounts to Retained Earnings, not re-validated at read time). The REQUIRED `fiscalYearId` is resolved FIRST; the two OPTIONAL period bounds `fromPeriodId`/`toPeriodId` are validated only when supplied, as they already were
Errors: `FIN-404-YEAR` (unknown `fiscalYearId`), `FIN-404-PERIOD` (supplied period bound does not resolve — unchanged), `FIN-500`
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

<!-- API:API-FIN-033:START traces=REQ-FIN-031,DBF-FIN-076,DBF-FIN-077,DBF-FIN-080,DBF-FIN-081,DBF-FIN-082 -->
### API-FIN-033 — search fiscal periods
Endpoint: POST /api/v1/fin/fiscal-periods/search · Layers: `FiscalPeriodController.search`→`FiscalPeriodService.search`
Request: body `FiscalPeriodSearchRequest` — `fiscalYearId`(EXACT, **OPTIONAL**, DBF-FIN-076) carried in the body filters and read by the child parent-id extractor (never a path variable); `statusCode`(EXACT, DBF-FIN-082), paging/sort · Response: 200 · `Page<FiscalPeriodResponse>`
Validations: none (read-only) · Errors: `FIN-400-INVALID-SORT`, `FIN-500`
Orchestration: build the generic specification from the remaining filters → AND in an explicit join predicate on `fiscalYear.fiscalYearPk` ONLY when `fiscalYearId` is present → page → map → return
Repository: `FiscalPeriodRepository` via `JpaSpecificationExecutor.findAll(Specification, Pageable)` — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join intra-module (period→year, only when the parent filter is supplied) · READ_ONLY
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_VIEW` · Localization: nameAr/nameEn per period
Parent id OPTIONAL — deliberate divergence from API-FIN-008, which rejects a missing `dimensionId` with `FIN-404-DIMENSION`. SCR-REQ-FIN-007 §B2 makes both filters EXACT but neither mandatory, and the endpoint exists precisely so a client that did NOT create the fiscal year in the same session can discover a period id: requiring the year id first would leave that client with no way in. Same shape API-FIN-018 already uses for its optional `periodId`.
Why it exists: `JournalEntryCreateRequest` requires `fiscalYearId` + `periodId` (API-FIN-019) and API-FIN-029/030/031 require a period or year id, yet before this endpoint no API returned a fiscal period except API-FIN-023's create response. `PERM_FIN_PERIODS_VIEW` was already a V24 registry row and already granted by V25/V27, so **no migration was needed** — only the matching `PermissionConstants` constant was added.
<!-- API:API-FIN-033:END -->

**404 on a keying id, as built (API-FIN-029/030/031).** FIN's house style already 404s on the id
that keys a report — API-FIN-028 answers `FIN-404-ACCOUNT`, API-FIN-032 answers
`FIN-404-DIMENSION`. API-FIN-030 and API-FIN-031 now do the same for their REQUIRED `fiscalYearId`
(`FIN-404-YEAR`), and API-FIN-029 for its `periodId` when — and only when — one is supplied
(`FIN-404-PERIOD`). API-FIN-031 was internally contradictory before: 404 on an unknown period bound
and 200 on an unknown year, in the same request. No new error code was introduced; both codes were
already registered in `FinErrorCodes` and both i18n bundles.
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
Endpoint: PUT /api/v1/fin/accounts/{id}/deactivate · Layers: `AccountController.deactivate`→`AccountService.deactivate`
Request: path `id`, no body · Response: 200 · `AccountResponse` (isActiveFl=false)
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
Endpoint: POST /api/v1/fin/dimensions/{id}/values · Layers: `DimensionController.createDimensionValue`→`DimensionValueService.create`
Request: path `id` (dimensionId); body `{code, nameAr, nameEn, sortOrder}`
Response: 201 · `DimensionValueResponse`
Validations: RULE-FIN-002 (full text: DATA-DOM §ENT-FIN-003) — code unique within the
dimension (QR-FIN-010)
Errors: `FIN-409-DIMVALUE-DUP`, `FIN-404-DIMENSION`
Orchestration: validate dimension exists → check RULE-FIN-002 (QR-FIN-010) → persist (QR-FIN-009) → return
Repository: QR-FIN-009, QR-FIN-010 · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-007:END -->

<!-- API:API-FIN-035:START traces=REQ-FIN-005,REQ-FIN-021,DBF-FIN-029 -->
### API-FIN-035 — deactivate dimension value
Endpoint: PUT /api/v1/fin/dimensions/values/{id}/deactivate · Layers: `DimensionController.deactivateDimensionValue`→`DimensionValueService.deactivate`
Request: path `id` (dimensionValuePk), no body · Response: 200 · `DimensionValueResponse` (isActiveFl=false)
Validations: none beyond existence · Errors: `FIN-404-DIMVALUE`
Orchestration: load → `DimensionValue.deactivate()` (the entity's own helper, never a direct field assignment) → persist → return. Effect: `DimensionValueDomain.checkUsableOnLine` reads exactly this flag (DBF-FIN-029), so every posting path citing the value afterwards answers `FIN-409-INVALID-DIMENSION` (RULE-FIN-009 / REQ-FIN-021, via API-FIN-019, 020, 014, 017)
Repository: `DimensionValueRepository.findById` + `save` — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_UPDATE` · Localization: n/a
New in this delivery: `FIN-404-DIMVALUE` (`FinErrorCodes.FIN_404_DIMVALUE`, added to BOTH i18n bundles) and `PERM_FIN_DIMENSIONS_UPDATE`. This is the first UPDATE-class endpoint on FIN_DIMENSIONS, so migration `V28__fin_dimensions_update_action.sql` registers the `FIN_DIMENSIONS / UPDATE` action row AND explicitly grants it to `SYS_ADMIN` — V25 grants by a `SELECT` over the registry and has already run, so a later row would otherwise be registered-but-ungrantable.
Why it exists: RULE-FIN-009 / REQ-FIN-021 reject a journal line citing an INACTIVE dimension value and `DimensionValueDomain` implements that check, but nothing could set the flag false, so the branch was unreachable and untestable. Deliberately NOT built (a decision, not a backlog item): a deactivate on the PARENT `Dimension` — no REQ/AC/RULE requires one and `Dimension.isActiveFl` (DBF-FIN-018) drives no behaviour. No `activate` counterpart either, matching the delivered `AccountService.deactivate` precedent.
<!-- API:API-FIN-035:END -->

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
Endpoint: POST /api/v1/fin/event-rules/{id}/lines · Layers: `EventTypeRuleController.createRuleLine`→`RuleLineService.create`
Request: path `id` (eventTypeRuleId); body `{accountDerivationTypeCode, accountDerivationValue,
amountSourceTypeCode, amountSourceValue?, directionCode, distributionTypeCode, isRemainderFl}`
Response: 201 · `RuleLineResponse`
Validations: RULE-FIN-003 (full text: DATA-DOM §ENT-FIN-010) — exactly one remainder line
once the line set is a compound or percentage distribution, i.e. any sibling line is
PERCENTAGE-distributed OR any line is already marked remainder (QR-FIN-016); and each line's
`isRemainderFl` marker (DBF-FIN-103) must agree with its own REMAINDER type code, since that
marker is the single one the API-FIN-020 builder reads; all four lookup codes validated via
XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-422-REMAINDER-MARKER`, `FIN-404-RULE`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookups → check RULE-FIN-003 across the rule's existing + new line
(QR-FIN-016) → persist (QR-FIN-015) → return
Repository: QR-FIN-015, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-011:END -->

<!-- API:API-FIN-034:START traces=REQ-FIN-007,DBF-FIN-093 -->
### API-FIN-034 — deactivate event-type rule
Endpoint: PUT /api/v1/fin/event-rules/{id}/deactivate · Layers: `EventTypeRuleController.deactivate`→`EventTypeRuleService.deactivate`
Request: path `id`, no body · Response: 200 · `EventTypeRuleResponse` (isActiveFl=false)
Validations: none beyond existence · Errors: `FIN-404-RULE`
Orchestration: load → clear the active flag (DBF-FIN-093) → persist → return
Repository: `EventTypeRuleRepository.findById` + `save` — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_UPDATE` (pre-existing — no new constant, no migration) · Localization: n/a
Why it exists: until this endpoint landed no rule could ever be retired, so `FIN-404-NO-ACTIVE-RULE` (RULE-FIN-005, API-FIN-020) was unreachable. **Stated limitation**, recorded in the service's own javadoc: deactivating does NOT free the event type for a replacement rule, because `EventTypeRuleService.create` guards uniqueness with `existsByEventTypeCode`, which is not scoped to the active flag. No `activate` counterpart, and no rule-line delete — ENT-FIN-010 carries no active-flag column and FIN publishes no `DELETE` endpoint on any screen (a deliberate v1 exclusion, see srs-fin.md SCR-REQ-FIN-003 §B4).
<!-- API:API-FIN-034:END -->

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

<!-- API:API-FIN-036:START traces=REQ-FIN-022,DBF-FIN-117 -->
### API-FIN-036 — deactivate template
Endpoint: PUT /api/v1/fin/recurring-templates/{id}/deactivate · Layers: `RecurringTemplateController.deactivate`→`RecurringTemplateService.deactivate`
Request: path `id`, no body · Response: 200 · `RecurringTemplateResponse` (isActiveFl=false)
Validations: none beyond existence · Errors: `FIN-404-TEMPLATE`
Orchestration: load → `RecurringTemplate.deactivate()` (the entity's own helper, never a direct field assignment) → persist → re-read the template's lines and hand them to the mapper → return. The line re-read is not decoration: `RecurringTemplateResponse.lineCount` is derived from the list the mapper is handed, so passing an empty list would misreport the aggregate as having no lines. It is orchestration (load → map), not a rule.
Repository: `RecurringTemplateRepository.findById` + `save`, plus `RecurringTemplateLineRepository.findByRecurringTemplatePk` for the response's lines — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_UPDATE` (pre-existing — V24 seeds the `FIN_RECURRING_TEMPLATES / UPDATE` action row and V25's blanket Tier-3 grant already covers it, so no new constant, no new error code and no migration) · Localization: n/a
**DEFECT CLOSED 2026-09-12 — deactivate now DOES stop the run.** This paragraph used to report an OPEN DEFECT: `RecurringTemplateService.run` (API-FIN-014) ignored `isActiveFl`, so a deactivated template still ran and still posted. That is no longer true. `RecurringTemplateDomain.assertCanRun()` — a NEW Domain companion for ENT-FIN-011 — is called by `RecurringTemplateService.run` immediately after the row is loaded and before anything else is resolved, and refuses a deactivated template with `FIN-409-NOT-ACTIVE` (`Status.CONFLICT` → HTTP 409; ar "هذا التعريف غير نشط ولا يمكن تشغيله", en "This definition is deactivated and cannot be run"). The screen's 404 was deliberately not reused: the template does exist. **This gate is a RECORDED HUMAN DECISION, not spec.** No RULE-FIN-* states it, and AC-FIN-023 is written "Given an active recurring template" without stating any outcome for an inactive one — a later reader must not mistake the gate for a requirement that was always there. What remains OPEN on this screen is only that a template cannot be UPDATED after creation (next paragraph). Recorded identically at srs-fin.md SCR-REQ-FIN-004 §B4 and §"Access summary".
Why it exists: srs-fin.md SCR-REQ-FIN-004 §B4 recorded the absence of a template deactivate as an OPEN DEFECT rather than a scope decision — `IS_ACTIVE_FL` is NOT NULL, the entity's `activate()`/`deactivate()` shipped with zero callers, B2 advertises an `isActiveFl(EXACT)` filter over a column nothing could set to FALSE, and AC-FIN-023 is written "Given an active recurring template", presupposing a state nothing could produce. Deliberately NOT built, and NOT taken by this endpoint: a template `update` — a correct update must decide the fate of the template's existing child lines, which is a design question no REQ, AC or RULE answers, so it remains the still-open half of the same gap. No `activate` counterpart either; FIN ships none for any entity.
<!-- API:API-FIN-036:END -->

<!-- API:API-FIN-016:START traces=REQ-FIN-025,DBF-FIN-133,DBF-FIN-142,DBF-FIN-144 -->
### API-FIN-016 — create allocation rule
Endpoint: POST /api/v1/fin/allocation-rules · Layers: `AllocationRuleController.create`→`AllocationRuleService.create`
Request: `{nameAr, nameEn, sourceAccountId, targets: [...]}`
Response: 201 · `AllocationRuleResponse`
Validations: RULE-FIN-003 (reused) — exactly one remainder target when any sibling is
PERCENTAGE or any target is already marked remainder (QR-FIN-016, reused), and each target's
`isRemainderFl` (DBF-FIN-141) must agree with its own `distributionTypeCode`;
distributionTypeCode validated via XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-422-REMAINDER-MARKER`, `FIN-404-ACCOUNT`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate → check RULE-FIN-003 across targets (QR-FIN-016) → persist rule+targets (QR-FIN-021) → return
Repository: QR-FIN-021, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-016:END -->

<!-- API:API-FIN-037:START traces=REQ-FIN-025,DBF-FIN-134 -->
### API-FIN-037 — deactivate allocation rule
Endpoint: PUT /api/v1/fin/allocation-rules/{id}/deactivate · Layers: `AllocationRuleController.deactivate`→`AllocationRuleService.deactivate`
Request: path `id`, no body · Response: 200 · `AllocationRuleResponse` (isActiveFl=false)
Validations: none beyond existence — RULE-FIN-003, the one rule `AllocationRuleDomain` owns, governs the remainder-target SET at create and run time and says nothing about the active flag · Errors: `FIN-404-ALLOCATION-RULE`
Orchestration: load → `AllocationRule.deactivate()` (the entity's own helper, never a direct field assignment) → persist → re-read the rule's targets and hand them to the mapper → return. The target re-read is not decoration: `AllocationRuleResponse.targetCount` is derived from the list the mapper is handed, so passing an empty list would misreport the aggregate as having no targets. It is orchestration (load → map), not a rule.
Repository: `AllocationRuleRepository.findById` + `save`, plus `AllocationTargetRepository.findByAllocationRulePk` for the response's targets — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_UPDATE` (pre-existing — V24 seeds the `FIN_ALLOCATION_RULES / UPDATE` action row and V25's blanket Tier-3 grant already covers it, so no new constant, no new error code and no migration) · Localization: n/a
**DEFECT CLOSED 2026-09-12 — deactivate now DOES stop the run.** This paragraph used to report an OPEN DEFECT: `AllocationRuleService.run` (API-FIN-017) ignored `isActiveFl`, so a deactivated rule still ran and still posted, and `AllocationRuleDomain.isActive()` had no caller. That is no longer true. `AllocationRuleDomain.assertCanRun()` is called by `AllocationRuleService.run` immediately after the row is loaded and before the target set is even fetched, and refuses a deactivated rule with `FIN-409-NOT-ACTIVE` (`Status.CONFLICT` → HTTP 409; ar "هذا التعريف غير نشط ولا يمكن تشغيله", en "This definition is deactivated and cannot be run"). The screen's 404 was deliberately not reused: the rule does exist. **This gate is a RECORDED HUMAN DECISION, not spec** — no RULE-FIN-* states it, and a later reader must not mistake it for a requirement that was always there. What remains OPEN on this screen is only that a rule cannot be UPDATED after creation (next paragraph). Recorded identically at srs-fin.md SCR-REQ-FIN-005 §B4 and §"Access summary".
Why it exists: srs-fin.md SCR-REQ-FIN-005 §B4 recorded the absence of a rule deactivate as an OPEN DEFECT rather than a scope decision — `IS_ACTIVE_FL` is NOT NULL, the entity's `activate()`/`deactivate()` shipped with zero callers, `AllocationRuleDomain.isActive()` was dead code, and B2 advertises an `isActiveFl(EXACT)` filter over a column nothing could set to FALSE. Deliberately NOT built, and NOT taken by this endpoint: a rule `update` — a correct update must decide the fate of the rule's existing targets (and therefore of RULE-FIN-003's remainder-target set), which is a design question no REQ, AC or RULE answers, so it remains the still-open half of the same gap. No `activate` counterpart either; FIN ships none for any entity.
<!-- API:API-FIN-037:END -->

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
QR-FIN-032) — every failure returned together (REQ-FIN-015), nothing posts if any fails.
RULE-FIN-017 (header coherence) runs FIRST and fail-fast: the submitted `periodId` must
belong to the submitted `fiscalYearId` (DBF-FIN-076) and `docDate` must fall inside that
period's [startDate, endDate] (DBF-FIN-080/081) — an incoherent triple makes RULE-FIN-008's
own period gate meaningless, lets the entry take a docNo from the wrong year's series, and
corrupts every period-scoped report and the year-end close. This is the only API that needs
it: every system-generated entry derives the three facts from one another
Errors: `FIN-400-PERIOD-NOT-IN-YEAR`, `FIN-400-DOCDATE-OUTSIDE-PERIOD`, `FIN-409-UNBALANCED`,
`FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`, `FIN-409-INVALID-DIMENSION`
Orchestration: resolve fiscal year UNDER A ROW LOCK (`SELECT ... FOR UPDATE` on
FIN_FISCAL_YEAR, the docNo series' allocation lock) → resolve period → check RULE-FIN-017 →
generate docNo (FIN-local generator, `JV-{fiscalYearCode}-{NNNNNN}`) → build DRAFT (QR-FIN-024) → validate
(QR-FIN-029..032) → on success: post (QR-FIN-033); on failure: discard the whole attempt
(one transaction, REQ-FIN-015) → return. The lock is what makes the per-fiscal-year counter
safe under concurrency: two simultaneous creates can no longer observe the same predecessor,
so `UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO` stays an unreachable backstop instead of surfacing as an
unlocalized data-integrity 409. A sequence was rejected (the counter restarts per year and the
schema declares none) and so was catch-and-retry (a service may not catch
DataIntegrityViolationException)
Repository: QR-FIN-024, QR-FIN-029, QR-FIN-030, QR-FIN-031, QR-FIN-032, QR-FIN-033 · join
NONE · READ_WRITE (one transaction, build-through-post)
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_CREATE` · Localization: descriptionAr/En
<!-- API:API-FIN-019:END -->
<!-- SUB:SVC-API-CRUD:END -->

<!-- SUB:SVC-API-INT:START traces=REQ-FIN-010,REQ-FIN-023,REQ-FIN-024,REQ-FIN-026,REQ-FIN-028,REQ-FIN-031,REQ-FIN-034,REQ-FIN-036,REQ-FIN-037 -->
### SUB — SVC-API-INT (posting-pipeline orchestration and period-control actions)

<!-- API:API-FIN-020:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,DBF-FIN-041,DBF-FIN-090,DBF-FIN-106,DBF-FIN-107 -->
### API-FIN-020 — build event entry (system)
Endpoint: POST /api/v1/fin/journal-entries/from-event · Layers: `JournalEntryController.buildFromEvent`→`EventEntryService.build`
Request: the canonical accounting event payload (opaque shape, out-of-scope Event consumer, POL-FIN-020)
Response: 201 · `JournalEntryResponse` (statusCode=POSTED) — or a rejection recorded for operator follow-up (REQ-FIN-013)
Validations: RULE-FIN-004 (duplicate eventReference, QR-FIN-026), RULE-FIN-005 (active
rule exists, QR-FIN-027), RULE-FIN-003 (the single-remainder guarantee RULE-FIN-010 depends
on, re-checked over the stored line set, QR-FIN-016), RULE-FIN-010 (PER-SIDE remainder
difference, QR-FIN-028), then the same RULE-FIN-006/007/008/009 checks as API-FIN-019
(QR-FIN-029..032)
Errors: `FIN-409-DUPLICATE-EVENT`, `FIN-404-NO-ACTIVE-RULE`, `FIN-409-REMAINDER-COUNT`,
`FIN-422-REMAINDER-MARKER`, `FIN-422-REMAINDER-NOT-POSITIVE`, `FIN-409-UNBALANCED`,
`FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`, `FIN-409-INVALID-DIMENSION`,
`FIN-422-MAPPING-UNSUPPORTED` (a rule line whose accountDerivationTypeCode is MAPPING — the
derivation fails loudly, since db-script-fin.md declares no mapping store; CONSTANT and
DIRECT are unaffected)
Orchestration: check RULE-FIN-004 (QR-FIN-026) → resolve active rule (QR-FIN-027) →
generate docNo (under the fiscal-year allocation lock, as API-FIN-019) → build lines from
the rule against the event's fields, computing the remainder line last as the difference
between the total already carried by the OPPOSING posting side and the total already carried
by the remainder line's own side (QR-FIN-028, QR-FIN-025) — a side-blind total would subtract
debit and credit lines alike from the base amount and produce a negative amount that dies on
CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE; a remainder that computes to zero or less is
`FIN-422-REMAINDER-NOT-POSITIVE`. Which line is the remainder is read from `isRemainderFl`
alone (DBF-FIN-103), the same marker RULE-FIN-003's guard counts → validate (QR-FIN-029..032)
→ post (QR-FIN-033) → return
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
Validations: the template must still be ACTIVE — `RecurringTemplateDomain.assertCanRun()`
(the NEW Domain companion for ENT-FIN-011) runs FIRST, immediately after the row is loaded and
before the period is resolved, and refuses a deactivated template with `FIN-409-NOT-ACTIVE`;
**no RULE-FIN-* states this gate — it rests on a recorded human decision of 2026-09-12, not on
stated requirement.** Then the same RULE-FIN-006/007/008/009 checks as API-FIN-019 (the
template's own lines were already balance-checked at API-FIN-013 create time, but re-validated
here since accounts/periods may have changed since)
Errors: same as API-FIN-019, plus `FIN-404-TEMPLATE` (unknown recurring template id) and
`FIN-409-NOT-ACTIVE` (the template exists but is deactivated)
Orchestration: load template (QR-FIN-019) → assert it is active → build entry from its lines (journalTypeCode=
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
Validations: the rule must still be ACTIVE — `AllocationRuleDomain.assertCanRun()` runs FIRST,
immediately after the row is loaded and before the target set is even fetched, and refuses a
deactivated rule with `FIN-409-NOT-ACTIVE`; **no RULE-FIN-* states this gate — it rests on a
recorded human decision of 2026-09-12, not on stated requirement.** Then RULE-FIN-003 (single
remainder marker over the stored targets, QR-FIN-016) and RULE-FIN-010 (per-side remainder
guarantee, QR-FIN-028, reused) then RULE-FIN-006/007/008/009
Errors: same family as API-FIN-019, plus `FIN-404-ALLOCATION-RULE`, `FIN-409-NOT-ACTIVE`,
`FIN-409-REMAINDER-COUNT`, `FIN-422-REMAINDER-MARKER`, `FIN-422-REMAINDER-NOT-POSITIVE`
Orchestration: load rule → assert it is active → load targets + current source-account balance (QR-FIN-022) →
distribute per target's distributionTypeCode, the target marked `isRemainderFl`
(DBF-FIN-141, the single marker — not `distributionTypeCode`) absorbing the rounding
difference between the source line's side and the targets' own side (QR-FIN-028) → build
entry (journalTypeCode=ALLOCATION) → validate + post (QR-FIN-029..033) → return
Repository: QR-FIN-022, QR-FIN-028, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-017:END -->

<!-- API:API-FIN-021:START traces=REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,DBF-FIN-042,DBF-FIN-043 -->
### API-FIN-021 — reverse entry
Endpoint: POST /api/v1/fin/journal-entries/{id}/reverse · Layers: `JournalEntryController.reverse`→`JournalEntryService.reverse`
Request: path `id` · Response: 201 · `JournalEntryResponse` (the new reversal entry)
Validations: RULE-FIN-013 (must be POSTED and not already reversed, QR-FIN-035); RULE-FIN-012
(period substitution if original's is closed, QR-FIN-036)
Errors: `FIN-409-NOT-POSTED`, `FIN-409-ALREADY-REVERSED`, `FIN-404-ENTRY`
Orchestration: load original UNDER A ROW LOCK (`SELECT ... FOR UPDATE` on the
FIN_JOURNAL_ENTRY header — no FIN entity carries `@Version`, so without it two concurrent
reversals both read reversalEntryId as null, both post a mirror, and the second save
overwrites the first link, leaving one orphaned mirror and a net effect of −(original)) →
check RULE-FIN-013 (QR-FIN-035) → resolve posting period
(original's if Open, else the current open period per RULE-FIN-012, QR-FIN-036) → build
mirrored lines with opposite directions, same amounts (RULE-FIN-011, QR-FIN-034) →
validate + post (QR-FIN-029..033, journalTypeCode=REVERSAL) → set originalEntryId/
reversalEntryId on both rows (bidirectional link) → return. Classic reversal: the original
STAYS POSTED — the only write back to it is the reversalEntryId link (DBF-FIN-043); its
statusCode is never modified, so both entries are seen by the POSTED-only report queries and
the pair nets to zero (SRS A7). Because the original stays POSTED, the double-reversal half of
RULE-FIN-013 is an explicit guard on the reversal link: a second reverse on the same entry is
rejected with `FIN-409-ALREADY-REVERSED` (AC-FIN-030), which would otherwise post a second
mirror and leave a net effect of −(original).
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
Period spans and names (governed, not implicit): when `periodCount` = 12 and
[startDate, endDate] spans one whole calendar year, each generated period IS a calendar
month — period N runs from the 1st to the last day of the Nth month of the span — and its
NAME_AR / NAME_EN (DBF-FIN-078/079, both NOT NULL) are that month's own name in Arabic and
English, taken from the platform's locale data (`java.time.Month` + CLDR), never a
hardcoded string table. For any other `periodCount`, or a span that is not a whole year,
the fallback is the even split: the days of [startDate, endDate] divided into periodCount
contiguous blocks, the first (totalDays mod periodCount) blocks one day longer, so the last
period always ends on the year's endDate and no day belongs to two periods; those periods
are named "الفترة N" / "Period N".
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
distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`. **That gate is the WHOLE of the rule**: the
`@PreAuthorize` on `FiscalPeriodService.hardClose`, enforced by SEC's own mechanism, exactly as
RULE-FIN-015 states it and AC-FIN-038 describes it. There is NO service-layer SoD read — the
one that existed was deleted on 2026-09-12 as an over-implementation (it refused the close for
every caller whenever any single user held both codes); see the Error Catalog's struck
`FIN-403-SOD-VIOLATION` row and retired XM-FIN-002
Errors: `FIN-409-NOT-REOPENABLE`(reused message context), `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040)
→ transition, set closedBy/closedAt to the approving principal (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` (custom — the distinct permission RULE-FIN-015 requires; since V30 it is also granted to SYS_ADMIN) · Localization: n/a
<!-- API:API-FIN-026:END -->

<!-- API:API-FIN-027:START traces=REQ-FIN-036,DBF-FIN-069,DBF-FIN-034 -->
### API-FIN-027 — run year-end close
Endpoint: POST /api/v1/fin/fiscal-years/{id}/year-end-close · Layers: `FiscalYearController.yearEndClose`→`FiscalYearService.yearEndClose`
Request: path `id` · Response: 201 · `{closingEntry: JournalEntryResponse, openingEntry: JournalEntryResponse}`
Validations, IN THIS ORDER (the order is part of the contract — a test asserting 409 on this
endpoint must not be defeated by a missing successor year or Retained Earnings
account): (1) the fiscal year's own statusCode must
still be OPEN — a re-run against an already-CLOSED year is rejected with
`FIN-409-INVALID-TRANSITION`, a stated rule on ENT-FIN-007's state machine rather than the
incidental `FIN-409-PERIODS-NOT-CLOSED` the first run's own YEAR_END_CLOSE transitions would
otherwise raise; (2) every period of the year must be HARD_CLOSE (§10.4 precondition), 409.
Only then are the successor year and the Retained Earnings account resolved.
RULE-FIN-015 is no longer a numbered step here: it is enforced entirely by this endpoint's
`@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate, which rejects before the method body
runs. The step that used to come first — a service-layer SoD read answering 403 — was deleted
on 2026-09-12 as an over-implementation; see the Error Catalog's struck `FIN-403-SOD-VIOLATION`
row. **A test written against the old contract and asserting 403 from inside this method will
now fail, and should be retargeted at the `@PreAuthorize` gate.**
Errors: `FIN-409-INVALID-TRANSITION` (year already closed), `FIN-409-PERIODS-NOT-CLOSED`, `FIN-404-YEAR` (unknown year id, or no adjacent successor year), `FIN-404-ACCOUNT` (no account marked as Retained Earnings)
Orchestration: verify the year is still OPEN → verify all periods Hard
Closed → resolve the successor year and the Retained Earnings account → compute closing
balances (QR-FIN-041) →
build + post a closing entry into the year's LAST period (result accounts → Retained
Earnings, journalTypeCode=CLOSING). The Retained Earnings account is DERIVED BY THE SYSTEM
from FIN_ACCOUNT.is_retained_earnings_fl (DBF-FIN-147, at most one row TRUE — partial unique
index UQ_FIN_ACCOUNT_RETAINED_EARNINGS) and is never supplied by the caller; no marked
account is `FIN-404-ACCOUNT`
→ build + post the next year's opening entry from the resulting balance-sheet balances
(journalTypeCode=OPENING, QR-FIN-041, POL-FIN-010) — CLOSING/OPENING are two values added
to the JOURNAL_TYPE lookup this stage (see Decisions Applied — a data-only, non-breaking
extension, not a new REQ/RULE) → mark FiscalYear statusCode=CLOSED, periods
statusCode=YEAR_END_CLOSE → return
Repository: QR-FIN-041, QR-FIN-029, QR-FIN-030, QR-FIN-032, QR-FIN-033 (both generated
entries go through the same validated posting pipeline) · QR-FIN-031 is deliberately NOT
applied to either of them: RULE-FIN-008 itself exempts the year-end closing and opening
entries, since this API's own all-periods-Hard-Closed precondition leaves no Open period for
the closing entry to post into. RULE-FIN-006/007/009 apply to both in full · the successor
fiscal year receiving the opening entry is resolved by DATE ADJACENCY (the year whose
startDate is the day after this year's endDate) — a DERIVED decision, recorded as such in
execution-state.json because ENT-FIN-007 declares no successor column; no such year is
`FIN-404-YEAR` · join intra-module · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` · Localization: n/a
DORMANT YEAR — a reviewed decision, not an accident. For a fiscal year in which no result account
carries a non-zero balance, `FiscalYearService.closingLines` contributes no line at all (each
result account with `net().signum() == 0` is skipped, and the Retained Earnings absorbing line is
added only when the running `resultTotal` is itself non-zero), and symmetrically
`openingLines` contributes none when no balance-sheet account carries a non-zero balance. The run
therefore posts a CLOSING (and OPENING) journal entry with an EMPTY line set, and that entry still
consumes a `docNo`: `JournalPostingService.buildValidateAndPost` allocates the number from the
locked fiscal-year series before it validates, and writes the entry unconditionally.
This was reviewed and deliberately KEPT. `JournalEntryDomain.checkBalanced` sums debits and
credits and returns empty when they compare equal, so 0 = 0 passes — a lineless entry literally
satisfies AC-FIN-036's "both entries individually balanced". Omitting the entry would make
AC-FIN-036's "posts a closing entry" false, and refusing the close outright would invent a rule no
artifact states.
Reachable only from here. `JournalEntryCreateRequest.lines` carries `@NotEmpty`, so API-FIN-019
rejects a lineless entry at the DTO boundary. This shape exists solely on the internal year-end
path, which builds its lines itself and never passes through that DTO.
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
A second row, XM-FIN-002 (READ → SEC), was assigned at ALIGN-BE — SEC-BE landed after this
phase was written and added what then looked like a second, genuinely distinct cross-module
consumption — and was RETIRED on 2026-09-12. Its block below is kept as a historical record,
struck; it must not be read as a live dependency.

<!-- XM:XM-FIN-001:START traces=REQ-FIN-001,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-018,REQ-FIN-022,REQ-FIN-025,REQ-FIN-031 -->
### XM-FIN-001 — validate/read lookup-backed codes against MDL
Target        : MDL · ENT-MDL-001/002 (LookupType/LookupValue) · classification SOFT-READ
Interface     : in-process Spring injection — FIN's service layer injects
`com.erp.mdl.crossmodule.MdlLookupApi` and calls `readActiveValuesByKey(typeKey)` for every
one of FIN's 13 owned keys, at the point each lookup-backed field is written or offered as a select-list
Contract      : data required = the submitted code exists as an active value under the
named type, checked by membership in the returned `List<LookupOptionView>` (code, labelAr,
labelEn, sortOrder); fallback if absent = reject with `FIN-400-INVALID-LOOKUP`; an unknown/
inactive `typeKey` raises MDL's `LocalizedException(NOT_FOUND, MDL_404_TYPE_KEY)`, which FIN
catches and translates to `FIN-400-INVALID-LOOKUP` (MDL's code never leaks out of FIN's API);
retry = none (same-process call, no network hop); idempotency
= read-only, naturally idempotent
Blocks        : none DEFERRED — MDL v1 is already gated (pass-1 APPROVE); ACTIVE from the
moment FIN v1 is created
<!-- XM:XM-FIN-001:END -->

<!-- XM:XM-FIN-002:START traces=REQ-FIN-037,REQ-FIN-038 -->
### ~~XM-FIN-002~~ — RETIRED 2026-09-12 (historical record, NOT a live dependency)
Status        : RETIRED. Kept so a reader reconstructing the decision can see what was
registered and why it went away. It binds nothing today and no code consumes it. The id is
burned, not reused.
What it was   : a READ of SEC's user→permission directory, classification READ, target SEC ·
ENT-SEC-001 (User) + SEC's role/permission grant tables. `FinSeparationOfDutiesService`
injected `com.erp.sec.crossmodule.SecUserDirectoryApi` and called
`findUserIdsHoldingPermission(permissionCode)` twice, for `PERM_FIN_PERIODS_CLOSE_APPROVE` and
`PERM_FIN_JOURNAL_ENTRIES_CREATE`, on every API-FIN-026 hard-close and API-FIN-027 year-end
close (never HTTP); it derived `closeApprovePermissionHeld` and `entryCreatePermissionShared`
and handed them to `FiscalPeriodDomain.assertCanHardClose`, which threw
`FIN-403-SOD-VIOLATION`.
Why it is gone: that check enforced GLOBAL user-set disjointness — if ANY single user in the
system held both permissions, the close was refused for EVERY caller, including a perfectly
clean approver — and no REQ, AC or RULE requires it. RULE-FIN-015 (srs-fin.md:1026-1033)
requires only that the close-approval action be gated by a permission DISTINCT from the
journal-entry-creation permission, "enforced through the Security module", and its `Data
source` line reads "DEFERRED — ... has no FIN-side field to read"; REQ-FIN-038
(srs-fin.md:781-788) and AC-FIN-038 (:789-792) say the same, the latter describing an ordinary
interceptor denial. By recorded human decision on 2026-09-12 the over-implementation was
removed: `FinSeparationOfDutiesService` and `FiscalPeriodDomain.assertCanHardClose(...)` were
deleted. RULE-FIN-015 still stands, enforced by the delivered
`@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on `FiscalPeriodService.hardClose` and
`FiscalYearService.yearEndClose`.
Consequence   : that service was FIN's ONLY consumer of `com.erp.sec.crossmodule`, so **FIN's
cross-module dependency on SEC is gone entirely**. The only remaining `com.erp.sec` mentions
under `src/main/java/com/erp/fin/` are `@PreAuthorize` SpEL string literals naming
`PermissionConstants`, plus two javadoc references — neither is a structural dependency.
`FIN-403-SOD-VIOLATION` is correspondingly struck as unreachable in the Error Catalog.
<!-- XM:XM-FIN-002:END -->

FIN's dependency on SEC for identity/authorization (the principal on every request, the
`@PreAuthorize` gate, and FIN's own self-registration of its module/screens/actions into SEC)
remains NOT a formal `XM` row — ADR-FIN-001 (carried from P2), unchanged — and since 2026-09-12
it is the ONLY relationship FIN has with SEC. XM-FIN-002 had been registered separately on the
grounds that it was a different thing: not the platform's ambient authorization of the caller
but FIN's own business logic reading SEC's data *about other users* — a named FIN service
calling a named SEC `crossmodule` interface method, whose returned rows were an input to a FIN
business rule (RULE-FIN-015) and whose absence had a defined, FIN-owned failure code. That
reasoning was sound for exactly as long as the consumption existed. It stopped applying when
the service making the call was deleted. Nothing about ADR-FIN-001 changed; what changed is
that there is no longer a second, non-ambient consumption for it to fail to cover.
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-FIN-001 -->
## PHASE 6 — INT-R (cross-module resolve)

| XM | Status | Workaround (if not READY/ACTIVE) |
|---|---|---|
| XM-FIN-001 | ACTIVE | not applicable — target already gated |
| ~~XM-FIN-002~~ | RETIRED 2026-09-12 | not applicable — the row is historical. `FinSeparationOfDutiesService`, its only consumer, was deleted with the SoD over-implementation (see INT-C); there is no read left to fail and so nothing to work around |

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
| FIN_ACCOUNTS | ✓ (API-FIN-001) | ✓ (API-FIN-002) | ✓ (API-FIN-003, and API-FIN-004 deactivate) | — | — |
| FIN_DIMENSIONS | ✓ (API-FIN-005,008) | ✓ (API-FIN-006,007) | ✓ (API-FIN-035, deactivate a dimension VALUE — `PERM_FIN_DIMENSIONS_UPDATE`, added by V28) | — | — |
| FIN_RULES | ✓ (API-FIN-009) | ✓ (API-FIN-010) | ✓ (API-FIN-011, add line; and API-FIN-034, deactivate rule) | — | — |
| FIN_RECURRING_TEMPLATES | ✓ (API-FIN-012) | ✓ (API-FIN-013) | ✓ (API-FIN-014, run; and API-FIN-036, deactivate template) | — | — |
| FIN_ALLOCATION_RULES | ✓ (API-FIN-015) | ✓ (API-FIN-016) | ✓ (API-FIN-017, run; and API-FIN-037, deactivate rule) | — | — |
| FIN_JOURNAL_ENTRIES | ✓ (API-FIN-018,022) | ✓ (API-FIN-019,020) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, API-FIN-021) |
| FIN_PERIODS | ✓ (API-FIN-033, search periods — and still the gateway, see below) | ✓ (API-FIN-023, year) | ✓ (API-FIN-024,025) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE`, API-FIN-026,027 — the distinct permission RULE-FIN-015 requires) |
| FIN_ACCOUNT_LEDGER | ✓ (API-FIN-028) | — | — | — | — |
| FIN_TRIAL_BALANCE | ✓ (API-FIN-029) | — | — | — | — |
| FIN_BALANCE_SHEET | ✓ (API-FIN-030) | — | — | — | — |
| FIN_INCOME_STATEMENT | ✓ (API-FIN-031) | — | — | — | — |
| FIN_DIMENSION_REPORTS | ✓ (API-FIN-032) | — | — | — | — |

**DELETE column — deliberately empty everywhere.** FIN exposes no `DELETE` endpoint at all.
Deactivation is `PUT /{id}/deactivate` gated by the screen's UPDATE permission (see
`AccountService.deactivate`, `@PreAuthorize` on `PERM_FIN_ACCOUNTS_UPDATE`), exactly as
MDL_LOOKUPS models it, and neither V24 nor V28 seeds a `PERM_FIN_*_DELETE` row for any FIN screen.
The FIN_ACCOUNTS row above read "✓ deactivate (API-FIN-004)" under DELETE until ALIGN-BE moved it
to UPDATE; inventing DELETE rows here would create permanently-unreferenced registry data. The two
later deactivates follow the same modelling: API-FIN-034 (event-type rule) under FIN_RULES/UPDATE,
API-FIN-035 (dimension value) under FIN_DIMENSIONS/UPDATE, API-FIN-036 (recurring template) under
FIN_RECURRING_TEMPLATES/UPDATE and API-FIN-037 (allocation rule) under FIN_ALLOCATION_RULES/UPDATE.
There are five deactivate endpoints in FIN and no `activate` anywhere — API-FIN-034, 035, 036 and
037 each deliberately omit a counterpart, following the delivered `AccountService.deactivate`
precedent.

**FIN_DIMENSIONS / UPDATE — the one cell V24 did not seed.** `PERM_FIN_DIMENSIONS_UPDATE` is
declared in `PermissionConstants` and registered by `V28__fin_dimensions_update_action.sql`, which
also grants it explicitly to `SYS_ADMIN`. The explicit grant is not optional: V25 grants SYS_ADMIN
its FIN actions with a `SELECT` over `SEC_ACTION_REG` and has already run everywhere, so Flyway
will never re-evaluate it against a row inserted later — registering without granting is exactly
the MDL failure V19/V21 had to repair. Tiers 1 and 2 need nothing new (V25 already grants SYS_ADMIN
the FIN module row and every FIN screen, FIN_DIMENSIONS included), and the RULE-SEC-007 gateway
holds because V24/V25 already registered and granted `PERM_FIN_DIMENSIONS_VIEW` on the same screen.
`FIN_CLOSE_APPROVER` (V27) deliberately gets nothing from V28 — its grants are scoped to
FIN_PERIODS and two permission codes.

**FIN_RULES / UPDATE — one permission, two endpoints.** API-FIN-034 reuses the pre-existing
`PERM_FIN_RULES_UPDATE` that V24 already seeds and V25 already granted, so it needed no new
constant, no new error code and no migration.

**FIN_RECURRING_TEMPLATES / UPDATE and FIN_ALLOCATION_RULES / UPDATE — the same shape, two
endpoints each.** API-FIN-036 reuses `PERM_FIN_RECURRING_TEMPLATES_UPDATE` and API-FIN-037 reuses
`PERM_FIN_ALLOCATION_RULES_UPDATE`; both action rows are seeded by V24 (`FIN_RECURRING_TEMPLATES /
UPDATE` and `FIN_ALLOCATION_RULES / UPDATE`) and both are already granted to SYS_ADMIN by V25's
Tier-3 statement, which grants every FIN action row except `PERM_FIN_PERIODS_CLOSE_APPROVE`. So
neither endpoint needed a new constant, a new error code or a migration — unlike API-FIN-035, whose
`FIN_DIMENSIONS / UPDATE` row did not exist and had to be both registered and explicitly granted by
V28. Each screen's UPDATE cell therefore now covers a run AND a deactivate.

**Deactivating now DOES stop the run — defect closed 2026-09-12, by decision rather than by rule.**
The permission gate above is still the whole of what API-FIN-036/037 themselves enforce, but the
two run endpoints are no longer indifferent to the flag. `RecurringTemplateService.run`
(API-FIN-014) and `AllocationRuleService.run` (API-FIN-017) each call `assertCanRun()` on the
loaded row's Domain companion — `RecurringTemplateDomain`, created for this, and
`AllocationRuleDomain` — and refuse a deactivated definition with `FIN-409-NOT-ACTIVE` (409).
**No RULE-FIN-* states this gate**; it rests on a recorded human decision, because closing the gap
required a new "exists but is inactive" error code that no requirement asks for. Do not cite it as
pre-existing spec. What remains open on those two screens is only that neither a template nor an
allocation rule can be UPDATED after creation. Recorded in full at srs-fin.md SCR-REQ-FIN-004 §B4,
SCR-REQ-FIN-005 §B4 and §"Access summary", and in SVC-API-CRUD's API-FIN-036/037 blocks.

**FIN_PERIODS / VIEW — a gateway that now also has an endpoint.** `PERM_FIN_PERIODS_VIEW` is a
real V24 action row and is load-bearing: `MenuService.effectiveAuthorityCodes()` keeps a granted
permission only if the same screen also carries a granted gateway (VIEW) action, so V27's
FIN_CLOSE_APPROVER role must hold it for `PERM_FIN_PERIODS_CLOSE_APPROVE` to survive into the
caller's authorities. That much is unchanged.

What HAS changed: the row is no longer constant-less and no longer endpoint-less. API-FIN-033
(`POST /api/v1/fin/fiscal-periods/search`, `FiscalPeriodService.search`) is gated on
`PERM_FIN_PERIODS_VIEW`, and the matching `PermissionConstants` constant was added with it. No
migration was needed — the action row was already registered by V24 and already granted by V25 and
V27. This section previously recorded the opposite state ("no `PermissionConstants` constant,
because FIN publishes no fiscal-period read endpoint … §B5 and the API registry define no search
API"); that was accurate before API-FIN-033 and is superseded now. srs-fin.md SCR-REQ-FIN-007 §B5
carries the endpoint row.

**Seed data** (REQ-FIN-044): 12 SEC_PAGES rows registered via SEC's screen-registration
endpoint at FIN onboarding; one action row per action above via SEC's action-registration
endpoint, following `PERM_<PAGE_CODE>_<ACTION>` — including the two custom actions
(`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, `PERM_FIN_PERIODS_CLOSE_APPROVE`). Delivered as migrations
V24 (registry) and V25 (SYS_ADMIN grants); V27 adds the dedicated `FIN_CLOSE_APPROVER` role; V28
adds the one later action row, `FIN_DIMENSIONS / UPDATE`, together with its own explicit SYS_ADMIN
grant; V30 grants `PERM_FIN_PERIODS_CLOSE_APPROVE` to `SYS_ADMIN`, the one row V25 had
deliberately withheld — see the SoD section below.

**SoD enforcement (RULE-FIN-015, POL-FIN-016) — SPECIFICATION REWRITTEN 2026-09-12.** What the
SRS actually requires, read at source: RULE-FIN-015 (srs-fin.md:1026-1033) requires the
period-close-approval action to be "gated by a permission distinct from the journal-entry-creation
permission, enforced through the Security module", and its `Data source` line reads "DEFERRED —
the permission matrix is the Security module's declaration surface; FIN declares no permission
entity in this version, so the separation is enforced there and has no FIN-side field to read".
REQ-FIN-038 (:781-788) states the same requirement, and AC-FIN-038 (:789-792) describes an
ordinary interceptor denial: "Given a role holding only the entry-creation permission / When that
role's user attempts the period-close-approval action / Then the system denies it (the CORE
interceptor, per SEC's own mechanism)."

That is the whole requirement, and it is satisfied in full by the delivered
`@PreAuthorize(PermissionConstants.PERM_FIN_PERIODS_CLOSE_APPROVE)` on
`FiscalPeriodService.hardClose` (API-FIN-026) and `FiscalYearService.yearEndClose`
(API-FIN-027). `PERM_FIN_PERIODS_CLOSE_APPROVE` is a different permission code from
`PERM_FIN_JOURNAL_ENTRIES_CREATE`, and SEC's own mechanism enforces it — `JwtAuthenticationFilter`
builds the caller's authorities from `MenuService`, which reads `SEC_ROLE_ACTION_GRANT`. Keeping
the two codes off the same role remains a sound administrative guideline, and `FIN_CLOSE_APPROVER`
(V27) is how a deployment expresses it; it is a guideline, not a constraint FIN code enforces.

**WHAT THIS SECTION USED TO SPECIFY, AND MUST NOT SPECIFY AGAIN.** Every earlier revision of this
paragraph said FIN's service layer "additionally checks at hard-close/year-end-close time that no
single *user* holds both, per role union". **That sentence is the origin of the defect** — it is a
GLOBAL user-set-disjointness rule, strictly stronger than anything the SRS states, and it was
implemented exactly as written: `FinSeparationOfDutiesService` read SEC's user directory and
`FiscalPeriodDomain.assertCanHardClose` threw `FIN-403-SOD-VIOLATION` whenever ANY single user in
the system held both codes, refusing the close for EVERY caller — including an approver who was
himself perfectly clean. Both classes were DELETED on 2026-09-12 by recorded human decision. This
section is rewritten rather than annotated precisely so that a future generation pass reading it
cannot regenerate the removed behaviour. **No FIN service reads SEC's user directory, and none may
be specified to here.** FIN has no cross-module dependency on SEC at all any more: XM-FIN-002 is
retired (INT-C), and `FIN-403-SOD-VIOLATION` is struck as unreachable in the Error Catalog.

**Who can actually close, as seeded.** V25 deliberately withheld `PERM_FIN_PERIODS_CLOSE_APPROVE`
from `SYS_ADMIN`, because granting it would have put the bootstrap `admin` user into both
permission sets and tripped the removed check on every close. With the check gone that exclusion
had no purpose, and `V30__fin_sys_admin_close_approve_grant.sql` reverses it by granting the single
withheld action row to `SYS_ADMIN`. So on a fresh database **the bootstrap `admin` user can now
hard-close a period and run a year-end close** — endpoints V25 had left answering 403 to every
principal. V27's `FIN_CLOSE_APPROVER` role (module FIN, screen FIN_PERIODS, exactly the
`PERM_FIN_PERIODS_VIEW` gateway plus `PERM_FIN_PERIODS_CLOSE_APPROVE`, and by construction no entry
creation) **remains valid** and is still the least-privilege way to give close approval to someone
who is not a system administrator. It is simply no longer REQUIRED for the close to work at all.

**V27's own "OPERATIONAL PRECONDITIONS" text is now factually wrong in BOTH numbered points, and
V27 is applied and immutable — this prose is the correction, because the source cannot be fixed.**
V27's header states (1) that a user assignment is still required, because
`FinSeparationOfDutiesService.resolveFacts()` reports `closeApprovePermissionHeld =
!approvers.isEmpty()` and `FiscalPeriodDomain.assertCanHardClose` throws when nobody holds
close-approval; and (2) that the assignee must not be a journal-entry creator and must NOT be the
bootstrap `admin`, or `FIN-403-SOD-VIOLATION` trips on every close. **Neither holds.** There is no
`resolveFacts()`, no `assertCanHardClose`, and no thrower of `FIN-403-SOD-VIOLATION` anywhere in
the codebase: "nobody holds close-approval" is no longer a failure mode, and assigning
`FIN_CLOSE_APPROVER` to a journal-entry creator — or to `admin`, who now holds the permission
directly via V30 — breaks nothing. Read V27's header as the history of a removed mechanism, never
as live operating instructions. (The same applies to V25's header, which explains its exclusion in
the same removed terms; V30's own header records the reversal in full.)

**Gateway**: every non-VIEW permission requires VIEW on the same screen first (platform
convention, SEC's own interceptor — not restated as a FIN-owned RULE).

**Forbidden responses**: both FIN 403 codes map through the `LocalizedException` envelope, each
carrying a registered FIN code and both ar/en messages — but only `FIN-403-FORBIDDEN` is still
reachable; see the next paragraph.

`FIN-403-SOD-VIOLATION` is STRUCK and no longer reachable, so it is not among them. It was never a
Spring Security `AccessDeniedException` — it was a business refusal thrown by hand as a
`LocalizedException`, so no advisor or handler for access denial was ever involved in it, and that
much is unchanged. What changed on 2026-09-12 is that BOTH of its throw sites were deleted with the
SoD over-implementation, so nothing raises it at all. The constant
`FinErrorCodes.FIN_403_SOD_VIOLATION` and both bundle entries were deliberately left in place by
the code session; they are dead text, not a live response.

`FIN-403-FORBIDDEN` now does too, and **this reverses what this section previously said**. It is a
real `FinErrorCodes.FIN_403_FORBIDDEN` constant and has entries in BOTH
`src/main/resources/i18n/messages.properties` and `messages_ar.properties`. A `@PreAuthorize`
denial on any `com.erp.fin.service.*` method is intercepted by
`com.erp.fin.security.FinForbiddenAdvisor`, which catches the `AccessDeniedException` and re-raises
it as `LocalizedException(Status.FORBIDDEN, FinErrorCodes.FIN_403_FORBIDDEN)`; `GlobalExceptionHandler`
then renders it like every other FIN error. The advisor is a `DefaultPointcutAdvisor` at
`Ordered.HIGHEST_PRECEDENCE`, declared once for the whole module — never per endpoint, and never as
a feature-module `@ControllerAdvice`, which `gov-enforce-backend-contract` CU.7 forbids. It mirrors
`com.erp.sec.security.SecForbiddenAdvisor`. So **FIN-403-FORBIDDEN does reach the wire**, and the
earlier claim that it is "the catalog's *name* for a platform response, not a FIN code" is
superseded.

Two boundaries bound that statement, and both were read in source rather than assumed:

1. **Filter-chain denials are still `SEC-403-FORBIDDEN`.** A denial raised before any FIN service is
   entered never reaches an AOP proxy or `GlobalExceptionHandler`; it is written directly by the
   chain's `accessDeniedHandler`. Today this is unreachable for FIN: `SecurityConfig` (`com.erp.main.config`)
   authorizes with `.anyRequest().authenticated()` and declares no FIN authority rule, so every FIN
   permission denial is in fact a `@PreAuthorize` denial on a FIN service and does pass through the
   advisor. Adding a URL-level authority rule for a FIN path would change that.
2. **`FIN-403-SOD-VIOLATION` is moot.** It never was an `AccessDeniedException`, so the advisor
   never saw it; and since 2026-09-12 it has no throw site at all. See the SoD section above.

What DID change, platform-wide: the 403 body is now localized. `handleAccessDenied` resolves its
message through the same `resolveMessage(...)` helper and `MessageSource` every other handler uses,
keyed on a new `CommonErrorCodes.ACCESS_DENIED` constant, and `ACCESS_DENIED` was added to BOTH
`messages.properties` and `messages_ar.properties`. The wire `code` is unchanged and the English
text is byte-identical to the string that was hardcoded before, so only Arabic callers observe any
difference. The earlier description of this response as carrying "a hardcoded English message,
bypassing `MessageSource`" is therefore no longer accurate; the separate point — that this is a
platform response and not a FIN code — still stands, as does the fact that routing it through
`LocalizedException` would change every module's 403 envelope and remains a platform decision.
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
MIRROR DIVERGENCE ⚠ STILL OPEN, PRE-EXISTING and outside this session's scope. The two supposedly-mirrored copies of the API-FIN-019 block are still NOT identical. Re-measured 2026-09-12 by extracting each block between its own `<!-- API:API-FIN-019:START ... -->` and `:END -->` markers and diffing: SVC-API-CRUD.md:180-222 is 43 lines, P3_1/backend-execution-plan-fin.md:979-1011 is 33 lines (the P3_1 range has MOVED — the previous revision cited :977-1009), and `diff` reports 12 changed lines, 11 on the CRUD side and 1 on the P3_1 side. The substance is unchanged: a 10-line `Numbering:` paragraph (docNo format, the VARCHAR(30) width argument, the per-fiscalYearId counter, UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO, and the explicit "no platform numbering engine exists in this repo") is present ONLY in SVC-API-CRUD.md at :199-208, and the Orchestration line differs correspondingly, the package copy reading "generate docNo (FIN-local generator)" where P3_1 inlines it as "generate docNo (FIN-local generator, `JV-{fiscalYearCode}-{NNNNNN}`)". No fact contradicts the other — P3_1 carries LESS detail, not different detail — so nothing downstream is wrong today; the risk is that a future session reading only P3_1 re-derives the numbering scheme, which is exactly the failure BINDING records. NOT FIXED HERE: this session's scope is this self-check block, execution-state.json and one project-artifacts report, and the divergence sits in the API blocks, outside all three. The fix is mechanical — copy the `Numbering:` paragraph into P3_1 and re-align the Orchestration line, then re-verify byte-equality — but it must be done by a session authorized to edit those blocks. Note this ALIGN block itself IS byte-identical across both files, verified by md5 before and after this revision.
V22 HEADER COUNT  ⚠ STILL OPEN, lowest severity here and deliberately left alone. V22__fin_schema.sql:4, opened and read at that line 2026-09-12, still reads verbatim: `-- Target: POSTGRESQL_16 | 14 tables, 14 sequences | 146 DBF-IDs | 1 XM (SOFT-READ -> MDL)`. "146 DBF-IDs" has been stale since V23__fin_account_retained_earnings_flag.sql added DBF-FIN-147; the current count is 147, re-counted today. It is a HEADER COMMENT in the migration file, not a `COMMENT ON` statement, so it was never written into the database and no live object misreports anything — which is precisely why V29 deliberately did NOT touch it: V29 corrects only the two statements that ARE in the live catalog, and a forward migration cannot rewrite an earlier file's header in any case. V22 is applied and immutable, so this can never be corrected at source; it is recorded here so no future session quotes "146 DBF-IDs" as the current count. === NOTE 2026-09-12, and it is a curiosity rather than a repair: the SAME header's "1 XM (SOFT-READ -> MDL)" has become ACCIDENTALLY CORRECT AGAIN. It was accurate when V22 was written, went stale when XM-FIN-002 was registered at ALIGN-BE, and is accurate once more now that XM-FIN-002 is retired and XM-FIN-001 is the whole live set. Nothing was fixed; the world moved back. The DBF half is still wrong, so this finding stays open — and no session may cite the XM half as evidence that the header is reliable. Separately re-confirmed today: 16 `^COMMENT ON COLUMN.*XM-FIN-001` lines in V22, unchanged.
SOD DEAD CODE     ⚠ NEW OPEN FINDING — FIN-403-SOD-VIOLATION is a live constant and a live pair of bundle rows with NO THROW SITE ANYWHERE. Measured 2026-09-12, three greps, all over src/main/java/ and src/main/resources/i18n/: the constant is declared at src/main/java/com/erp/fin/exception/FinErrorCodes.java:78 (`public static final String FIN_403_SOD_VIOLATION = "FIN-403-SOD-VIOLATION";`); the message keys are live in BOTH bundles, messages.properties:142 and messages_ar.properties:139; and `grep -rn 'FIN_403_SOD_VIOLATION' src/main/java/` returns exactly TWO hits, the declaration itself and a `{@link}` javadoc reference at FinErrorCodes.java:392 — NOT ONE `throw`. Its only former throw sites were FinSeparationOfDutiesService (deleted) and FiscalPeriodDomain.assertCanHardClose (deleted with it). The Error Catalog row was struck at _SECTIONS.md:407, following the FIN-503 precedent, BUT the constant and the two bundle entries were DELIBERATELY LEFT IN PLACE by the catalog session — that is the divergence recorded here, not an accusation of oversight. WHY IT IS A FINDING AND NOT NOISE: it makes the three-way 40/40/40 code count under API (R3) include one code no caller can ever receive, so any future session diffing constants against reachable behaviour will re-discover it; and a struck catalog row beside a live constant is exactly the shape that invites someone to "restore" the rule. WHAT MUST NOT HAPPEN: nobody may re-add a throw for it. RULE-FIN-015 is satisfied by the @PreAuthorize gate alone (see DECISIONS), and re-introducing a SoD check is the precise thing FiscalPeriodDomain.java:110-117's "DO NOT RESTORE THE PREVIOUS IMPLEMENTATION" note forbids. The open question for a human is only whether to retire the constant and the two bundle rows too, or keep them as the struck row's counterpart; this session invented no answer.
SEC DEAD CHAIN    ⚠ NEW OPEN FINDING, and it is OUTSIDE FIN — reported here because FIN's change caused it, and fixed here by nobody, because it is SEC's code. Deleting FinSeparationOfDutiesService removed the only PRODUCTION caller of a three-link chain in SEC. Traced 2026-09-12 with `grep -rn findUserIdsHoldingPermission src/`, every hit read: the JPQL query `RoleActionGrantRepository.findUserIdsHoldingPermission` (src/main/java/com/erp/sec/repository/RoleActionGrantRepository.java:124) is called only by `UserService.findUserIdsHoldingPermission` (:199-203), which is called only by `SecUserDirectoryApiImpl.findUserIdsHoldingPermission` (:26-27), which implements `SecUserDirectoryApi.findUserIdsHoldingPermission` (:25) — and the ONLY remaining callers of that interface method anywhere are four assertions in src/test/java/com/erp/sec/SecCoverageIntegrationTest.java (:438, :442, :447, :452). Zero production call sites. That is an A.2.9 dead-code condition of exactly the kind this block's own QRC line deleted four FIN repository methods for — with the difference that a test still exercises it, so it is not unreachable, merely unused. NOT ACTIONED, and deliberately: this is SEC's module record, not FIN's, and FIN's ALIGN block has no authority to delete SEC code or to decide that SEC's published crossmodule contract should shrink because its only consumer went away. Note also that RoleActionGrantRepository.java:115's javadoc still names `UserService.findUserIdsHoldingPermission` as its caller under "(A.2.9)", which is true one link up but no longer true end-to-end. For a human: either keep the method as published SEC API with no current consumer (legitimate — `SecUserDirectoryApi.findContact` is in the same position, with no production consumer outside SEC today), or retire both. FIN has no stake in the answer.
CATALOG GAP       ⚠ NEW OPEN FINDING — FIN-422-INVALID-PERCENTAGE-VALUE is a registered, thrown, fully-bundled error code with NO ERROR CATALOG ROW. Measured 2026-09-12 by extracting the 41 codes in the catalog table's first column (_SECTIONS.md:378-418) and `comm`-diffing them against the 40 `"FIN-*"` literals in FinErrorCodes.java: the constants-minus-catalog set is exactly one element, FIN-422-INVALID-PERCENTAGE-VALUE. It is not a phantom — the constant is at FinErrorCodes.java:357, it IS thrown, at EventTypeRuleDomain.java:267 inside `sourcedAmount(...)` when `new BigDecimal(amountSourceValue)` raises NumberFormatException for a PERCENTAGE-sourced rule line, and both bundles carry the key (messages.properties:170, messages_ar.properties:167). `grep -n 'INVALID-PERCENTAGE' _SECTIONS.md` and the same over P3_1 both return ZERO, so the row is missing from BOTH mirrors identically — this is an omission, not a divergence. The test plan already noticed and covered it: TC-FIN-109 was added 2026-09-12 expressly to close the coverage half. What remains uncovered is the catalog half. NOT FIXED HERE because the Error Catalog table lies outside this session's scope (this block, execution-state.json and one project-artifacts report); the fix is mechanical and must be applied to BOTH mirrors — add one row reading code FIN-422-INVALID-PERCENTAGE-VALUE, RULE-FIN-010 (build half), API-FIN-020 and API-FIN-011, HTTP 422, with the trigger and the ar+en text taken from the bundles rather than reworded. Until then the API (R3) line's "41 catalog rows / 40 constants" must be read as a 40-row overlap plus two catalog-only entries and one constant-only entry, not as a superset relation.
INPUT VALIDATION  ⚠ NEW OPEN FINDING — `RuleLineCreateRequest.amountSourceValue` accepts any string, which is the whole reason FIN-422-INVALID-PERCENTAGE-VALUE is reachable at all. Read in source 2026-09-12 at src/main/java/com/erp/fin/dto/RuleLineCreateRequest.java:41-42: the field is declared `private String amountSourceValue;` under a single `@Schema(description = "Amount source value - قيمة مصدر المبلغ", example = "netAmount")` and NOTHING ELSE — no @NotBlank, no @Size, no @Pattern, no format constraint of any kind, in contrast with the neighbouring amountSourceTypeCode which carries @Size(max = 20). THE CONSEQUENCE, traced end to end: API-FIN-011 (create rule line) persists whatever arrives, including a value that can never be parsed as a decimal, on a line whose amountSourceTypeCode is PERCENTAGE. Nothing rejects it at write time. The failure surfaces only much later, at API-FIN-020 (post from event), when EventTypeRuleDomain.sourcedAmount(...) reaches `new BigDecimal(amountSourceValue)` at EventTypeRuleDomain.java:265-268 and converts the NumberFormatException into FIN-422-INVALID-PERCENTAGE-VALUE. So a configuration error committed on one screen is reported as a posting failure on another, to a different user, possibly much later — and the stored rule stays broken, because there is no update endpoint for a rule line either (FIN publishes create-only on rule lines; see SCOPE vs SRS). This is a REAL INPUT-VALIDATION GAP, not a documentation defect. NOT FIXED HERE: adding a constraint changes the API contract for API-FIN-011 (a previously-accepted body would start returning 400 VALIDATION_ERROR), and the correct constraint is conditional — amountSourceValue means a field NAME for a FIELD-sourced line and a NUMBER for a PERCENTAGE-sourced one, so a flat @Pattern is wrong and a class-level cross-field validator is a design decision no RULE-FIN-* states. For a human: either add the conditional validation at API-FIN-011 and downgrade FIN-422-INVALID-PERCENTAGE-VALUE to a defence-in-depth path, or accept late failure and say so in the SRS. This session invented neither.
RESULT            PASSED WITH FINDINGS — 9 open, 0 blocking the phase, 0 unverified lines. THE COUNT ROSE FROM 6 TO 9 AND THAT IS NOT A REGRESSION: one finding CLOSED, four were ADDED by a sweep the previous revision had not run, and the remainder carried. Line by line, because this block's own standing rule requires every movement to be named. CLOSED (1): DEACTIVATE RUN — closed by FinErrorCodes.java:441 (FIN-409-NOT-ACTIVE) plus its two bundle keys, RecurringTemplateDomain.java:71-76 and AllocationRuleDomain.java:191-196 (the two assertCanRun() guards), their call sites at RecurringTemplateService.java:206 and AllocationRuleService.java:182, and the flipped TC-FIN-106/107; it rests on a RECORDED HUMAN DECISION and on no RULE-FIN-*, which the catalog row at _SECTIONS.md:393 states in its own RULE column. CARRIED, UNCHANGED IN SUBSTANCE (4): DOC QUOTATION (V24:52-53, applied and immutable, structurally uncloseable — its cited srs line numbers refreshed today); PLATFORM I18N (residue — the malformed-request-body handler at GlobalExceptionHandler.java:79-87, which cannot be localized without a wire-contract change); TEMPLATE/RULE UPD (neither aggregate can be corrected after creation; its workaround clause corrected, since deactivate now does stop the run); MIRROR DIVERGENCE (the `Numbering:` paragraph still present only in SVC-API-CRUD.md; P3_1 range refreshed to :979-1011); V22 HEADER COUNT (`146 DBF-IDs` still stale; its XM half became accidentally correct again, which repairs nothing). ADDED (4), each verified against the real artifact before being written: SOD DEAD CODE, SEC DEAD CHAIN, CATALOG GAP, INPUT VALIDATION. THE NINE OPEN ARE THEREFORE: DOC QUOTATION, PLATFORM I18N (residue), TEMPLATE/RULE UPD, MIRROR DIVERGENCE, V22 HEADER COUNT, SOD DEAD CODE, SEC DEAD CHAIN, CATALOG GAP, INPUT VALIDATION. Of those, INPUT VALIDATION is the only one that is a defect in shipped behaviour rather than a documentation, history or dead-code divergence; SEC DEAD CHAIN is the only one outside FIN entirely. MEASUREMENTS THAT MOVED THIS REVISION, each stated on its own line above and each the measurement winning over the inherited claim: error codes 38/38/38 → 40/40/40; Error Catalog rows 39 → 41; @PreAuthorize annotations 43 → 42; XM 2 → 1; Domain classes 7 → 8; test-case ids 108 → 109 (108 in force, TC-FIN-091 retired); and every srs-fin.md Operations line number, all six of which shifted. Re-measured and UNCHANGED: 37 endpoints, 147 DBF ids, 49 QR ids, 27 PERM_FIN_* constants against 27 registered action rows, 16 XM-FIN-001 COMMENT ON COLUMN lines in V22, 22 AuditableEntity subclasses split 16/6 on audit width. ONE CLAIM INHERITED FROM THE HAND-OFF WAS CHECKED AND FOUND FALSE, and is recorded so it is not re-asserted: FiscalPeriodService.java:135 was reported as a stale javadoc still naming FinSeparationOfDutiesService and XM-FIN-002. It is NOT stale. Read at :131-135 today, it is a deliberate past-tense removal note — "A previous implementation resolved facts from SEC's user directory here ... It was removed by an explicit human decision, together with FinSeparationOfDutiesService and FIN's XM-FIN-002 dependency on SEC" — under a "Do not add a SoD check back into this body" warning. FiscalYearService.java:156 and FiscalPeriodDomain.java:110-117 carry the same deliberate note. Nothing was changed there. STANDING RULE, STRENGTHENED AGAIN: this block must NEVER be returned to "PASSED ✓ — 0 findings" while any finding above still stands. The open count must never be lowered without naming, ON THAT FINDING'S OWN LINE, the specific artifact — file and line, migration, or commit — that closed it; DEACTIVATE RUN above is the worked example of what that looks like, and the bar it sets is the bar. "Re-verified and now fine" is not a closure. A closure that rests on a human decision rather than on a stated requirement MUST say so and MUST say that no RULE-FIN-* states it, as DEACTIVATE RUN does. A closure asserted against a migration that has not been applied MUST say so, as SCHEMA COMMENT does. ADDING a finding is always permitted and needs no authority; REMOVING one is not, and a finding may be struck only by a session that RE-MEASURED it from the artifact, never by one that inherited the claim. Every line number quoted in this block was opened today; where a previously-recorded line number had moved, the line says both the old and the new value rather than silently substituting — carry that habit forward, because three separate line-reference sets drifted in a single day.
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
