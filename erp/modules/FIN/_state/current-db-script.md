# DATABASE — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Dialect : postgresql16   Schema prefix : none
Identifier transformation : SRS logical field name (camelCase) → physical column
  name (snake_case). Applied to every identifier; no other spelling exists.
Date : 2026-09-10
Counts : 14 tables · 147 DBF · 1 XM (XM-FIN-001 SOFT-READ → MDL). XM-FIN-002 (READ → SEC)
  was registered at ALIGN-BE and RETIRED on 2026-09-12 — see §2
══════════════════════════════════════════════════════════════════

## 1. DB FIELD TRACEABILITY MATRIX — FIN v1

### Table FIN_ACCOUNT (ENT-FIN-001)
| DBF id | Column | Type (postgresql16) | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-001 | account_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-001 (PK) | REQ-FIN-001 | NOT NULL | identity |
| DBF-FIN-002 | code | VARCHAR(30) | ENT-FIN-001.code | REQ-FIN-001 | NOT NULL | — |
| DBF-FIN-003 | name_ar | VARCHAR(200) | ENT-FIN-001.nameAr | REQ-FIN-001 | NOT NULL | — |
| DBF-FIN-004 | name_en | VARCHAR(200) | ENT-FIN-001.nameEn | REQ-FIN-001 | NOT NULL | — |
| DBF-FIN-005 | account_type_code | VARCHAR(20) | ENT-FIN-001.accountTypeCode (A6 ACCOUNT_TYPE) | REQ-FIN-001 | NOT NULL | — |
| DBF-FIN-006 | nature_code | VARCHAR(10) | ENT-FIN-001.natureCode (A6 DEBIT_CREDIT) | REQ-FIN-001 | NOT NULL | — |
| DBF-FIN-007 | parent_account_id | BIGINT | ENT-FIN-001.parentAccountId (self) | REQ-FIN-001, REQ-FIN-002 | NULL | — |
| DBF-FIN-008 | is_leaf_fl | BOOLEAN | ENT-FIN-001.isLeafFl | REQ-FIN-002, REQ-FIN-019 | NOT NULL | TRUE |
| DBF-FIN-009 | is_active_fl | BOOLEAN | ENT-FIN-001.isActiveFl | REQ-FIN-003, REQ-FIN-019 | NOT NULL | TRUE |
| DBF-FIN-147 | is_retained_earnings_fl | BOOLEAN | ENT-FIN-001.isRetainedEarningsFl | REQ-FIN-036 | NOT NULL | FALSE |
| DBF-FIN-010 | created_by | VARCHAR(100) | profile: entity_defaults.master (audit) | REQ-FIN-001 | NOT NULL | — |
| DBF-FIN-011 | created_at | TIMESTAMPTZ | profile: entity_defaults.master (audit) | REQ-FIN-001 | NOT NULL | now() |
| DBF-FIN-012 | updated_by | VARCHAR(100) | profile: entity_defaults.master (audit) | REQ-FIN-001 | NULL | — |
| DBF-FIN-013 | updated_at | TIMESTAMPTZ | profile: entity_defaults.master (audit) | REQ-FIN-001 | NULL | — |

### Table FIN_DIMENSION (ENT-FIN-002)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-014 | dimension_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-002 (PK) | REQ-FIN-004 | NOT NULL | identity |
| DBF-FIN-015 | code | VARCHAR(30) | ENT-FIN-002.code | REQ-FIN-004 | NOT NULL | — |
| DBF-FIN-016 | name_ar | VARCHAR(150) | ENT-FIN-002.nameAr | REQ-FIN-004 | NOT NULL | — |
| DBF-FIN-017 | name_en | VARCHAR(150) | ENT-FIN-002.nameEn | REQ-FIN-004 | NOT NULL | — |
| DBF-FIN-018 | is_active_fl | BOOLEAN | ENT-FIN-002.isActiveFl | REQ-FIN-004 | NOT NULL | TRUE |
| DBF-FIN-019..022 | created_by/created_at/updated_by/updated_at | String/Instant | profile: entity_defaults.config (audit) | REQ-FIN-004 | see db-script | Yes-equivalent | — |

### Table FIN_DIMENSION_VALUE (ENT-FIN-003)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-023 | dimension_value_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-003 (PK) | REQ-FIN-005 | NOT NULL | identity |
| DBF-FIN-024 | dimension_id | BIGINT | ENT-FIN-003.dimensionId → FK ENT-FIN-002 | REQ-FIN-005 | NOT NULL | — |
| DBF-FIN-025 | code | VARCHAR(30) | ENT-FIN-003.code | REQ-FIN-005, REQ-FIN-006 | NOT NULL | — |
| DBF-FIN-026 | name_ar | VARCHAR(150) | ENT-FIN-003.nameAr | REQ-FIN-005 | NOT NULL | — |
| DBF-FIN-027 | name_en | VARCHAR(150) | ENT-FIN-003.nameEn | REQ-FIN-005 | NOT NULL | — |
| DBF-FIN-028 | sort_order | NUMERIC | ENT-FIN-003.sortOrder | REQ-FIN-005 | NOT NULL | 0 |
| DBF-FIN-029 | is_active_fl | BOOLEAN | ENT-FIN-003.isActiveFl | REQ-FIN-021 | NOT NULL | TRUE |
| DBF-FIN-030..033 | created_by/created_at/updated_by/updated_at | String/Instant | profile: entity_defaults.lookup (audit) | REQ-FIN-005 | see db-script | — | — |

### Table FIN_JOURNAL_ENTRY (ENT-FIN-004)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-034 | journal_entry_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-004 (PK) | REQ-FIN-010, REQ-FIN-014 | NOT NULL | identity |
| DBF-FIN-035 | doc_no | VARCHAR(30) | ENT-FIN-004.docNo | REQ-FIN-010, REQ-FIN-014 | NOT NULL | numbering engine |
| DBF-FIN-036 | doc_date | DATE | ENT-FIN-004.docDate | REQ-FIN-010, REQ-FIN-014 | NOT NULL | — |
| DBF-FIN-037 | fiscal_year_id | BIGINT | ENT-FIN-004.fiscalYearId → FK ENT-FIN-007 | REQ-FIN-010, REQ-FIN-014 | NOT NULL | — |
| DBF-FIN-038 | period_id | BIGINT | ENT-FIN-004.periodId → FK ENT-FIN-008 | REQ-FIN-020 | NOT NULL | — |
| DBF-FIN-039 | journal_type_code | VARCHAR(20) | ENT-FIN-004.journalTypeCode (A6 JOURNAL_TYPE) | REQ-FIN-010, REQ-FIN-014 | NOT NULL | — |
| DBF-FIN-040 | status_code | VARCHAR(10) | ENT-FIN-004.statusCode (A6 JOURNAL_STATUS) | REQ-FIN-017 | NOT NULL | 'DRAFT' |
| DBF-FIN-041 | event_reference | VARCHAR(100) | ENT-FIN-004.eventReference | REQ-FIN-010, REQ-FIN-011 | NULL | — |
| DBF-FIN-042 | original_entry_id | BIGINT | ENT-FIN-004.originalEntryId (self) | REQ-FIN-028 | NULL | — |
| DBF-FIN-043 | reversal_entry_id | BIGINT | ENT-FIN-004.reversalEntryId (self) | REQ-FIN-028 | NULL | — |
| DBF-FIN-044 | description_ar | TEXT | ENT-FIN-004.descriptionAr | REQ-FIN-014 | NULL | — |
| DBF-FIN-045 | description_en | TEXT | ENT-FIN-004.descriptionEn | REQ-FIN-014 | NULL | — |
| DBF-FIN-046 | posted_at | TIMESTAMPTZ | ENT-FIN-004.postedAt | REQ-FIN-017 | NULL | — |
| DBF-FIN-047 | created_by | VARCHAR(100) | profile: entity_defaults.transactional (audit) | REQ-FIN-010, REQ-FIN-014 | NOT NULL | — |
| DBF-FIN-048 | created_at | TIMESTAMPTZ | profile: entity_defaults.transactional (audit) | REQ-FIN-010, REQ-FIN-014 | NOT NULL | now() |
| DBF-FIN-049 | updated_by | VARCHAR(100) | profile: entity_defaults.transactional (audit) | REQ-FIN-016 | NULL | — |
| DBF-FIN-050 | updated_at | TIMESTAMPTZ | profile: entity_defaults.transactional (audit) | REQ-FIN-016 | NULL | — |

### Table FIN_JOURNAL_LINE (ENT-FIN-005)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-051 | journal_line_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-005 (PK) | REQ-FIN-014 | NOT NULL | identity |
| DBF-FIN-052 | journal_entry_id | BIGINT | ENT-FIN-005.journalEntryId → FK ENT-FIN-004 | REQ-FIN-014 | NOT NULL | — |
| DBF-FIN-053 | line_no | NUMERIC | ENT-FIN-005.lineNo | REQ-FIN-014 | NOT NULL | — |
| DBF-FIN-054 | account_id | BIGINT | ENT-FIN-005.accountId → FK ENT-FIN-001 | REQ-FIN-019 | NOT NULL | — |
| DBF-FIN-055 | amount | NUMERIC(18,4) | ENT-FIN-005.amount | REQ-FIN-012, REQ-FIN-018 | NOT NULL | — |
| DBF-FIN-056 | direction_code | VARCHAR(10) | ENT-FIN-005.directionCode (A6 DEBIT_CREDIT) | REQ-FIN-018 | NOT NULL | — |
| DBF-FIN-057 | is_remainder_fl | BOOLEAN | ENT-FIN-005.isRemainderFl | REQ-FIN-012 | NOT NULL | FALSE |
| DBF-FIN-058 | description_ar | TEXT | ENT-FIN-005.descriptionAr | REQ-FIN-014 | NULL | — |
| DBF-FIN-059 | description_en | TEXT | ENT-FIN-005.descriptionEn | REQ-FIN-014 | NULL | — |
| DBF-FIN-060 | created_at | TIMESTAMPTZ | ENT-FIN-005 (audit) | REQ-FIN-014 | NOT NULL | now() |

### Table FIN_JOURNAL_LINE_DIM (ENT-FIN-006)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-061 | journal_line_dim_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-006 (PK) | REQ-FIN-021 | NOT NULL | identity |
| DBF-FIN-062 | journal_line_id | BIGINT | ENT-FIN-006.journalLineId → FK ENT-FIN-005 | REQ-FIN-021 | NOT NULL | — |
| DBF-FIN-063 | dimension_id | BIGINT | ENT-FIN-006.dimensionId → FK ENT-FIN-002 | REQ-FIN-021 | NOT NULL | — |
| DBF-FIN-064 | dimension_value_id | BIGINT | ENT-FIN-006.dimensionValueId → FK ENT-FIN-003 | REQ-FIN-021, REQ-FIN-043 | NOT NULL | — |

### Table FIN_FISCAL_YEAR (ENT-FIN-007)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-065 | fiscal_year_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-007 (PK) | REQ-FIN-031 | NOT NULL | identity |
| DBF-FIN-066 | code | VARCHAR(10) | ENT-FIN-007.code | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-067 | start_date | DATE | ENT-FIN-007.startDate | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-068 | end_date | DATE | ENT-FIN-007.endDate | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-069 | status_code | VARCHAR(10) | ENT-FIN-007.statusCode (A6 FISCAL_YEAR_STATUS) | REQ-FIN-036 | NOT NULL | 'OPEN' |
| DBF-FIN-070 | is_active_fl | BOOLEAN | ENT-FIN-007.isActiveFl | REQ-FIN-031 | NOT NULL | TRUE |
| DBF-FIN-071..074 | created_by/created_at/updated_by/updated_at | String/Instant | profile: entity_defaults.master (audit) | REQ-FIN-031 | see db-script | — | — |

### Table FIN_FISCAL_PERIOD (ENT-FIN-008)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-075 | fiscal_period_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-008 (PK) | REQ-FIN-031 | NOT NULL | identity |
| DBF-FIN-076 | fiscal_year_id | BIGINT | ENT-FIN-008.fiscalYearId → FK ENT-FIN-007 | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-077 | period_no | NUMERIC | ENT-FIN-008.periodNo | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-078 | name_ar | VARCHAR(100) | ENT-FIN-008.nameAr | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-079 | name_en | VARCHAR(100) | ENT-FIN-008.nameEn | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-080 | start_date | DATE | ENT-FIN-008.startDate | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-081 | end_date | DATE | ENT-FIN-008.endDate | REQ-FIN-031 | NOT NULL | — |
| DBF-FIN-082 | status_code | VARCHAR(15) | ENT-FIN-008.statusCode (A6 PERIOD_STATE) | REQ-FIN-020, REQ-FIN-032..035 | NOT NULL | 'OPEN' |
| DBF-FIN-083 | closed_by | VARCHAR(100) | ENT-FIN-008.closedBy | REQ-FIN-037 | NULL | — |
| DBF-FIN-084 | closed_at | TIMESTAMPTZ | ENT-FIN-008.closedAt | REQ-FIN-037 | NULL | — |
| DBF-FIN-085..088 | created_by/created_at/updated_by/updated_at | String/Instant | profile: entity_defaults.master (audit) | REQ-FIN-031 | see db-script | — | — |

### Table FIN_EVENT_TYPE_RULE (ENT-FIN-009)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-089 | event_type_rule_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-009 (PK) | REQ-FIN-007 | NOT NULL | identity |
| DBF-FIN-090 | event_type_code | VARCHAR(50) | ENT-FIN-009.eventTypeCode (A6 ACCOUNTING_EVENT_TYPE) | REQ-FIN-007, REQ-FIN-013 | NOT NULL | — |
| DBF-FIN-091 | name_ar | VARCHAR(150) | ENT-FIN-009.nameAr | REQ-FIN-007 | NOT NULL | — |
| DBF-FIN-092 | name_en | VARCHAR(150) | ENT-FIN-009.nameEn | REQ-FIN-007 | NOT NULL | — |
| DBF-FIN-093 | is_active_fl | BOOLEAN | ENT-FIN-009.isActiveFl | REQ-FIN-013 | NOT NULL | TRUE |
| DBF-FIN-094..097 | created_by/created_at/updated_by/updated_at | String/Instant | profile: entity_defaults.config (audit) | REQ-FIN-007 | see db-script | — | — |

### Table FIN_RULE_LINE (ENT-FIN-010)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-098 | rule_line_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-010 (PK) | REQ-FIN-008 | NOT NULL | identity |
| DBF-FIN-099 | event_type_rule_id | BIGINT | ENT-FIN-010.eventTypeRuleId → FK ENT-FIN-009 | REQ-FIN-008 | NOT NULL | — |
| DBF-FIN-100 | line_no | NUMERIC | ENT-FIN-010.lineNo | REQ-FIN-008 | NOT NULL | — |
| DBF-FIN-101 | account_derivation_type_code | VARCHAR(20) | ENT-FIN-010.accountDerivationTypeCode (A6 ACCOUNT_DERIVATION_TYPE) | REQ-FIN-008 | NOT NULL | — |
| DBF-FIN-102 | account_derivation_value | TEXT | ENT-FIN-010.accountDerivationValue | REQ-FIN-008 | NOT NULL | — |
| DBF-FIN-103 | amount_source_type_code | VARCHAR(20) | ENT-FIN-010.amountSourceTypeCode (A6 AMOUNT_SOURCE_TYPE) | REQ-FIN-008 | NOT NULL | — |
| DBF-FIN-104 | amount_source_value | TEXT | ENT-FIN-010.amountSourceValue | REQ-FIN-008 | NULL | — |
| DBF-FIN-105 | direction_code | VARCHAR(10) | ENT-FIN-010.directionCode (A6 DEBIT_CREDIT) | REQ-FIN-008 | NOT NULL | — |
| DBF-FIN-106 | distribution_type_code | VARCHAR(15) | ENT-FIN-010.distributionTypeCode (A6 DISTRIBUTION_TYPE) | REQ-FIN-009, REQ-FIN-012 | NOT NULL | — |
| DBF-FIN-107 | is_remainder_fl | BOOLEAN | ENT-FIN-010.isRemainderFl | REQ-FIN-009, REQ-FIN-012 | NOT NULL | FALSE |
| DBF-FIN-108 | created_at | TIMESTAMPTZ | ENT-FIN-010 (audit) | REQ-FIN-008 | NOT NULL | now() |

### Table FIN_RECURRING_TEMPLATE (ENT-FIN-011)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-109 | recurring_template_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-011 (PK) | REQ-FIN-022 | NOT NULL | identity |
| DBF-FIN-110 | name_ar | VARCHAR(150) | ENT-FIN-011.nameAr | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-111 | name_en | VARCHAR(150) | ENT-FIN-011.nameEn | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-112 | schedule_type_code | VARCHAR(15) | ENT-FIN-011.scheduleTypeCode (A6 RECURRING_SCHEDULE_TYPE) | REQ-FIN-022, REQ-FIN-024 | NOT NULL | — |
| DBF-FIN-113 | frequency_code | VARCHAR(15) | ENT-FIN-011.frequencyCode (A6 RECURRING_FREQUENCY) | REQ-FIN-023 | NULL | — |
| DBF-FIN-114 | start_date | DATE | ENT-FIN-011.startDate | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-115 | next_run_date | DATE | ENT-FIN-011.nextRunDate | REQ-FIN-023 | NOT NULL | — |
| DBF-FIN-116 | end_date | DATE | ENT-FIN-011.endDate | REQ-FIN-022 | NULL | — |
| DBF-FIN-117 | is_active_fl | BOOLEAN | ENT-FIN-011.isActiveFl | REQ-FIN-022 | NOT NULL | TRUE |
| DBF-FIN-118..121 | created_by/created_at/updated_by/updated_at | String/Instant | profile: entity_defaults.config (audit) | REQ-FIN-022 | see db-script | — | — |

### Table FIN_RECURRING_TEMPLATE_LINE (ENT-FIN-012)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-122 | recurring_template_line_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-012 (PK) | REQ-FIN-022 | NOT NULL | identity |
| DBF-FIN-123 | recurring_template_id | BIGINT | ENT-FIN-012.recurringTemplateId → FK ENT-FIN-011 | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-124 | line_no | NUMERIC | ENT-FIN-012.lineNo | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-125 | account_id | BIGINT | ENT-FIN-012.accountId → FK ENT-FIN-001 | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-126 | amount | NUMERIC(18,4) | ENT-FIN-012.amount | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-127 | direction_code | VARCHAR(10) | ENT-FIN-012.directionCode (A6 DEBIT_CREDIT) | REQ-FIN-022 | NOT NULL | — |
| DBF-FIN-128 | dimension_value_id | BIGINT | ENT-FIN-012.dimensionValueId → FK ENT-FIN-003 | REQ-FIN-022 | NULL | — |
| DBF-FIN-129 | created_at | TIMESTAMPTZ | ENT-FIN-012 (audit) | REQ-FIN-022 | NOT NULL | now() |

### Table FIN_ALLOCATION_RULE (ENT-FIN-013)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-130 | allocation_rule_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-013 (PK) | REQ-FIN-025 | NOT NULL | identity |
| DBF-FIN-131 | name_ar | VARCHAR(150) | ENT-FIN-013.nameAr | REQ-FIN-025 | NOT NULL | — |
| DBF-FIN-132 | name_en | VARCHAR(150) | ENT-FIN-013.nameEn | REQ-FIN-025 | NOT NULL | — |
| DBF-FIN-133 | source_account_id | BIGINT | ENT-FIN-013.sourceAccountId → FK ENT-FIN-001 | REQ-FIN-025, REQ-FIN-026 | NOT NULL | — |
| DBF-FIN-134 | is_active_fl | BOOLEAN | ENT-FIN-013.isActiveFl | REQ-FIN-025 | NOT NULL | TRUE |
| DBF-FIN-135..138 | created_by/created_at/updated_by/updated_at | String/Instant | profile: entity_defaults.config (audit) | REQ-FIN-025 | see db-script | — | — |

### Table FIN_ALLOCATION_TARGET (ENT-FIN-014)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-FIN-139 | allocation_target_pk | GENERATED ALWAYS AS IDENTITY | ENT-FIN-014 (PK) | REQ-FIN-025 | NOT NULL | identity |
| DBF-FIN-140 | allocation_rule_id | BIGINT | ENT-FIN-014.allocationRuleId → FK ENT-FIN-013 | REQ-FIN-025 | NOT NULL | — |
| DBF-FIN-141 | line_no | NUMERIC | ENT-FIN-014.lineNo | REQ-FIN-025 | NOT NULL | — |
| DBF-FIN-142 | target_account_id | BIGINT | ENT-FIN-014.targetAccountId → FK ENT-FIN-001 | REQ-FIN-025 | NOT NULL | — |
| DBF-FIN-143 | dimension_value_id | BIGINT | ENT-FIN-014.dimensionValueId → FK ENT-FIN-003 | REQ-FIN-025 | NULL | — |
| DBF-FIN-144 | distribution_type_code | VARCHAR(15) | ENT-FIN-014.distributionTypeCode (A6 DISTRIBUTION_TYPE) | REQ-FIN-009, REQ-FIN-026 | NOT NULL | — |
| DBF-FIN-145 | distribution_value | NUMERIC(18,4) | ENT-FIN-014.distributionValue | REQ-FIN-026 | NULL | — |
| DBF-FIN-146 | is_remainder_fl | BOOLEAN | ENT-FIN-014.isRemainderFl | REQ-FIN-009, REQ-FIN-026 | NOT NULL | FALSE |

Total: 147 DBF ids across 14 tables (the figure read 146 until ALIGN-BE; it was never bumped
when DBF-FIN-147, FIN_ACCOUNT.is_retained_earnings_fl, was inserted by migration V23 and added
to the matrix above — the header's "147 DBF" was the correct half of the contradiction).

PK generation, as built: the matrix rows above describe every PK as
`GENERATED ALWAYS AS IDENTITY`; migration V22 deliberately built plain `BIGINT NOT NULL` PKs fed
by explicit `SEQ_<TABLE>` sequences instead (V22 BLOCK 1, justified in that file's header), because
this repo's entity contract mandates `GenerationType.SEQUENCE` and every other module here does
the same. The entities match V22. Left as written rather than rewriting 14 applied rows; the
deviation is recorded here and in the backend execution plan's extraction block.

## 2. XM REGISTER — FIN v1

| XM id | Type | This table | Column / access | Target table | Target module | Traces (REQ) | Status |
|---|---|---|---|---|---|---|---|
| XM-FIN-001 | SOFT-READ | FIN_ACCOUNT, FIN_JOURNAL_ENTRY, FIN_JOURNAL_LINE, FIN_FISCAL_YEAR, FIN_FISCAL_PERIOD, FIN_EVENT_TYPE_RULE, FIN_RULE_LINE, FIN_RECURRING_TEMPLATE, FIN_ALLOCATION_TARGET | application-level validation of every lookup-backed code column (account_type_code, nature_code, direction_code, journal_type_code, status_code, event_type_code, account_derivation_type_code, amount_source_type_code, distribution_type_code, schedule_type_code, frequency_code) against `MDL_LOOKUP_VALUE` | MDL_LOOKUP_VALUE | MDL | REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031 | ACTIVE (target MDL v1 gated, pass-1 APPROVE) |
| ~~XM-FIN-002~~ | READ | (no table — service-to-service) | HISTORICAL, kept so the decision can be reconstructed. `FinSeparationOfDutiesService` injected `com.erp.sec.crossmodule.SecUserDirectoryApi` and called `findUserIdsHoldingPermission` for `PERM_FIN_PERIODS_CLOSE_APPROVE` and `PERM_FIN_JOURNAL_ENTRIES_CREATE`, to resolve a global user-set-disjointness fact behind API-FIN-026 / API-FIN-027; in-process Spring injection, never HTTP. That service was DELETED on 2026-09-12 together with `FiscalPeriodDomain.assertCanHardClose(...)` — see the note below | SEC's user/role/permission grant tables (via the crossmodule interface only) | SEC | REQ-FIN-037, REQ-FIN-038 | RETIRED 2026-09-12 — nothing consumes it |

XM-FIN-002 bound no FIN column and created no physical FK. It was assigned at ALIGN-BE, after
the SEC-BE phase introduced the read (the P2 pass legitimately saw only one XM), on the grounds
that it was a named FIN service consuming a named SEC `crossmodule` interface whose result fed a
FIN business rule.

**RETIRED 2026-09-12 — do not resurrect it.** The rule it fed was an over-implementation:
`FinSeparationOfDutiesService` reported whether the user sets holding
`PERM_FIN_PERIODS_CLOSE_APPROVE` and `PERM_FIN_JOURNAL_ENTRIES_CREATE` were disjoint, and
`FiscalPeriodDomain.assertCanHardClose` refused the close whenever ANY single user in the system
held both — for EVERY caller, including a perfectly clean approver. RULE-FIN-015 does not ask for
that. Read at `governance/modules/FIN/P1/srs-fin.md:1026-1033`, it requires only that the
close-approval action be gated by a permission DISTINCT from the journal-entry-creation
permission, "enforced through the Security module", and its `Data source` line reads
"DEFERRED — ... has no FIN-side field to read". REQ-FIN-038 (`srs-fin.md:781-788`) and
AC-FIN-038 (`:789-792`) say the same. By recorded human decision both classes were deleted;
RULE-FIN-015 stands and is enforced by the delivered
`@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on `FiscalPeriodService.hardClose` and
`FiscalYearService.yearEndClose`. That service was FIN's ONLY consumer of
`com.erp.sec.crossmodule`, so **FIN now has no cross-module dependency on SEC at all**; the only
remaining `com.erp.sec` mentions under `src/main/java/com/erp/fin/` are `@PreAuthorize` SpEL
string literals naming `PermissionConstants`, plus two javadoc references. The id XM-FIN-002 is
retired, not reused.

See `erp/decisions/FIN/ADR-FIN-001.md` for why FIN's *identity/authorization* dependency on SEC,
and its own self-registration into SEC, are still NOT an XM row (they follow the exact precedent
SEC's and MDL's own P2/P3.1 already set: platform-standard integration narrated in the backend
execution plan, not a `SHARED ENTITIES CONSUMED` → `XM` row — no physical cross-module FK exists
anywhere in this pipeline). ADR-FIN-001 is unchanged and, with XM-FIN-002 retired, it once again
covers the whole of FIN's relationship with SEC.

### 2.1 SOFT-READ handling
```
-- XM-FIN-001 SOFT-READ — every FIN lookup-backed column above reads MDL_LOOKUP_VALUE
-- (joined by lookup_type_key = the FIN-owned key, e.g. 'ACCOUNT_TYPE', and code = the
-- stored column value) from MDL without a physical FK, since these columns store plain
-- VARCHAR codes validated at the application layer, per ADR-FIN-001.
-- Rationale: centralization per lookup-module-plan-en.md §2; FIN owns no lookup table.
-- Risk: a value deactivated in MDL after a FIN row already cites it is not retro-
-- invalidated here — an accepted impact per XM-PROTOCOL.md (no cascading revoke across
-- modules), same acceptance already recorded by XM-MDL-001.
```

No DEFERRED FK — SOFT-READ never gets a live constraint (§6), and MDL is already gated
regardless.

## 3. FULL_DATABASE_SCRIPT

```sql
-- ════════════════════════════════════════════════════════════════
-- FIN v1 — General Ledger module — PostgreSQL 16
-- Identifier transformation: camelCase (SRS) -> snake_case (DB)
-- ════════════════════════════════════════════════════════════════

-- BLOCK 1 — SEQUENCES
-- none: every PK uses GENERATED ALWAYS AS IDENTITY.

-- BLOCK 2 — PARENT TABLES (no FK dependencies)

CREATE TABLE FIN_DIMENSION (
  dimension_pk   BIGINT GENERATED ALWAYS AS IDENTITY,
  code           VARCHAR(30)   NOT NULL,
  name_ar        VARCHAR(150)  NOT NULL,
  name_en        VARCHAR(150)  NOT NULL,
  is_active_fl   BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by     VARCHAR(100)  NOT NULL,
  created_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by     VARCHAR(100),
  updated_at     TIMESTAMPTZ
);

CREATE TABLE FIN_ACCOUNT (
  account_pk        BIGINT GENERATED ALWAYS AS IDENTITY,
  code               VARCHAR(30)   NOT NULL,
  name_ar            VARCHAR(200)  NOT NULL,
  name_en            VARCHAR(200)  NOT NULL,
  account_type_code  VARCHAR(20)   NOT NULL,
  nature_code        VARCHAR(10)   NOT NULL,
  parent_account_id  BIGINT,
  is_leaf_fl         BOOLEAN       NOT NULL DEFAULT TRUE,
  is_active_fl       BOOLEAN       NOT NULL DEFAULT TRUE,
  is_retained_earnings_fl BOOLEAN  NOT NULL DEFAULT FALSE,
  created_by         VARCHAR(100)  NOT NULL,
  created_at         TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by         VARCHAR(100),
  updated_at         TIMESTAMPTZ
);

CREATE TABLE FIN_FISCAL_YEAR (
  fiscal_year_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  code            VARCHAR(10)   NOT NULL,
  start_date      DATE          NOT NULL,
  end_date        DATE          NOT NULL,
  status_code     VARCHAR(10)   NOT NULL DEFAULT 'OPEN',
  is_active_fl    BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by      VARCHAR(100)  NOT NULL,
  created_at      TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by      VARCHAR(100),
  updated_at      TIMESTAMPTZ
);

CREATE TABLE FIN_EVENT_TYPE_RULE (
  event_type_rule_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  event_type_code     VARCHAR(50)   NOT NULL,
  name_ar             VARCHAR(150)  NOT NULL,
  name_en             VARCHAR(150)  NOT NULL,
  is_active_fl        BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by          VARCHAR(100)  NOT NULL,
  created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by          VARCHAR(100),
  updated_at          TIMESTAMPTZ
);

CREATE TABLE FIN_RECURRING_TEMPLATE (
  recurring_template_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  name_ar                VARCHAR(150)  NOT NULL,
  name_en                VARCHAR(150)  NOT NULL,
  schedule_type_code     VARCHAR(15)   NOT NULL,
  frequency_code         VARCHAR(15),
  start_date             DATE          NOT NULL,
  next_run_date          DATE          NOT NULL,
  end_date               DATE,
  is_active_fl           BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by             VARCHAR(100)  NOT NULL,
  created_at             TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by             VARCHAR(100),
  updated_at             TIMESTAMPTZ
);

CREATE TABLE FIN_ALLOCATION_RULE (
  allocation_rule_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  name_ar             VARCHAR(150)  NOT NULL,
  name_en             VARCHAR(150)  NOT NULL,
  source_account_id   BIGINT        NOT NULL,
  is_active_fl        BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by          VARCHAR(100)  NOT NULL,
  created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by           VARCHAR(100),
  updated_at           TIMESTAMPTZ
);

-- BLOCK 3 — CHILD TABLES (parents already created above; chain respected)

CREATE TABLE FIN_DIMENSION_VALUE (
  dimension_value_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  dimension_id        BIGINT        NOT NULL,
  code                VARCHAR(30)   NOT NULL,
  name_ar             VARCHAR(150)  NOT NULL,
  name_en             VARCHAR(150)  NOT NULL,
  sort_order          NUMERIC       NOT NULL DEFAULT 0,
  is_active_fl        BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by          VARCHAR(100)  NOT NULL,
  created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by          VARCHAR(100),
  updated_at          TIMESTAMPTZ
);

CREATE TABLE FIN_FISCAL_PERIOD (
  fiscal_period_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  fiscal_year_id    BIGINT        NOT NULL,
  period_no         NUMERIC       NOT NULL,
  name_ar           VARCHAR(100)  NOT NULL,
  name_en           VARCHAR(100)  NOT NULL,
  start_date        DATE          NOT NULL,
  end_date          DATE          NOT NULL,
  status_code       VARCHAR(15)   NOT NULL DEFAULT 'OPEN',
  closed_by         VARCHAR(100),
  closed_at         TIMESTAMPTZ,
  created_by        VARCHAR(100)  NOT NULL,
  created_at        TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by        VARCHAR(100),
  updated_at        TIMESTAMPTZ
);

CREATE TABLE FIN_JOURNAL_ENTRY (
  journal_entry_pk   BIGINT GENERATED ALWAYS AS IDENTITY,
  doc_no             VARCHAR(30)   NOT NULL,
  doc_date           DATE          NOT NULL,
  fiscal_year_id     BIGINT        NOT NULL,
  period_id          BIGINT        NOT NULL,
  journal_type_code  VARCHAR(20)   NOT NULL,
  status_code        VARCHAR(10)   NOT NULL DEFAULT 'DRAFT',
  event_reference    VARCHAR(100),
  original_entry_id  BIGINT,
  reversal_entry_id  BIGINT,
  description_ar     TEXT,
  description_en     TEXT,
  posted_at          TIMESTAMPTZ,
  created_by         VARCHAR(100)  NOT NULL,
  created_at         TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by         VARCHAR(100),
  updated_at         TIMESTAMPTZ
);

CREATE TABLE FIN_RULE_LINE (
  rule_line_pk                    BIGINT GENERATED ALWAYS AS IDENTITY,
  event_type_rule_id              BIGINT        NOT NULL,
  line_no                         NUMERIC       NOT NULL,
  account_derivation_type_code    VARCHAR(20)   NOT NULL,
  account_derivation_value        TEXT          NOT NULL,
  amount_source_type_code         VARCHAR(20)   NOT NULL,
  amount_source_value             TEXT,
  direction_code                  VARCHAR(10)   NOT NULL,
  distribution_type_code          VARCHAR(15)   NOT NULL,
  is_remainder_fl                 BOOLEAN       NOT NULL DEFAULT FALSE,
  created_at                      TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE FIN_RECURRING_TEMPLATE_LINE (
  recurring_template_line_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  recurring_template_id       BIGINT        NOT NULL,
  line_no                     NUMERIC       NOT NULL,
  account_id                  BIGINT        NOT NULL,
  amount                      NUMERIC(18,4) NOT NULL,
  direction_code              VARCHAR(10)   NOT NULL,
  dimension_value_id          BIGINT,
  created_at                  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE FIN_ALLOCATION_TARGET (
  allocation_target_pk    BIGINT GENERATED ALWAYS AS IDENTITY,
  allocation_rule_id      BIGINT        NOT NULL,
  line_no                 NUMERIC       NOT NULL,
  target_account_id       BIGINT        NOT NULL,
  dimension_value_id      BIGINT,
  distribution_type_code  VARCHAR(15)   NOT NULL,
  distribution_value      NUMERIC(18,4),
  is_remainder_fl         BOOLEAN       NOT NULL DEFAULT FALSE
);

CREATE TABLE FIN_JOURNAL_LINE (
  journal_line_pk   BIGINT GENERATED ALWAYS AS IDENTITY,
  journal_entry_id  BIGINT        NOT NULL,
  line_no           NUMERIC       NOT NULL,
  account_id        BIGINT        NOT NULL,
  amount            NUMERIC(18,4) NOT NULL,
  direction_code    VARCHAR(10)   NOT NULL,
  is_remainder_fl   BOOLEAN       NOT NULL DEFAULT FALSE,
  description_ar    TEXT,
  description_en    TEXT,
  created_at        TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE FIN_JOURNAL_LINE_DIM (
  journal_line_dim_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  journal_line_id      BIGINT  NOT NULL,
  dimension_id          BIGINT  NOT NULL,
  dimension_value_id    BIGINT  NOT NULL
);

-- BLOCK 4 — COMMENTS (table + every column; each column comment cites its DBF id)

COMMENT ON TABLE FIN_ACCOUNT IS 'ENT-FIN-001 Account — PRIVATE; [DBF-FIN-001..013, DBF-FIN-147]';
-- NOTE (ALIGN-BE): the LIVE database does not carry this text. V22 applied
-- '[DBF-FIN-001..013]' and V23, which added is_retained_earnings_fl, added the column comment
-- but no replacement table comment. V22 is applied and must never be edited, so the live
-- FIN_ACCOUNT table comment permanently omits DBF-FIN-147 unless a forward migration is written
-- for it. Open decision — recorded in execution-state.json, not silently reconciled.
COMMENT ON COLUMN FIN_ACCOUNT.account_pk IS 'DBF-FIN-001';
COMMENT ON COLUMN FIN_ACCOUNT.code IS 'DBF-FIN-002';
COMMENT ON COLUMN FIN_ACCOUNT.name_ar IS 'DBF-FIN-003';
COMMENT ON COLUMN FIN_ACCOUNT.name_en IS 'DBF-FIN-004';
COMMENT ON COLUMN FIN_ACCOUNT.account_type_code IS 'DBF-FIN-005 — lookup ACCOUNT_TYPE (XM-FIN-001)';
COMMENT ON COLUMN FIN_ACCOUNT.nature_code IS 'DBF-FIN-006 — lookup DEBIT_CREDIT (XM-FIN-001)';
COMMENT ON COLUMN FIN_ACCOUNT.parent_account_id IS 'DBF-FIN-007';
COMMENT ON COLUMN FIN_ACCOUNT.is_leaf_fl IS 'DBF-FIN-008 — RULE-FIN-001 enforced at application layer';
COMMENT ON COLUMN FIN_ACCOUNT.is_active_fl IS 'DBF-FIN-009';
COMMENT ON COLUMN FIN_ACCOUNT.is_retained_earnings_fl IS 'DBF-FIN-147 — REQ-FIN-036 / POL-FIN-010; at most one row TRUE (UQ_FIN_ACCOUNT_RETAINED_EARNINGS, partial unique index)';
COMMENT ON COLUMN FIN_ACCOUNT.created_by IS 'DBF-FIN-010';
COMMENT ON COLUMN FIN_ACCOUNT.created_at IS 'DBF-FIN-011';
COMMENT ON COLUMN FIN_ACCOUNT.updated_by IS 'DBF-FIN-012';
COMMENT ON COLUMN FIN_ACCOUNT.updated_at IS 'DBF-FIN-013';

COMMENT ON TABLE FIN_DIMENSION IS 'ENT-FIN-002 Dimension — PRIVATE; [DBF-FIN-014..022]';
COMMENT ON COLUMN FIN_DIMENSION.dimension_pk IS 'DBF-FIN-014';
COMMENT ON COLUMN FIN_DIMENSION.code IS 'DBF-FIN-015';
COMMENT ON COLUMN FIN_DIMENSION.name_ar IS 'DBF-FIN-016';
COMMENT ON COLUMN FIN_DIMENSION.name_en IS 'DBF-FIN-017';
COMMENT ON COLUMN FIN_DIMENSION.is_active_fl IS 'DBF-FIN-018';
COMMENT ON COLUMN FIN_DIMENSION.created_by IS 'DBF-FIN-019';
COMMENT ON COLUMN FIN_DIMENSION.created_at IS 'DBF-FIN-020';
COMMENT ON COLUMN FIN_DIMENSION.updated_by IS 'DBF-FIN-021';
COMMENT ON COLUMN FIN_DIMENSION.updated_at IS 'DBF-FIN-022';

COMMENT ON TABLE FIN_DIMENSION_VALUE IS 'ENT-FIN-003 DimensionValue — PRIVATE; [DBF-FIN-023..033]';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.dimension_value_pk IS 'DBF-FIN-023';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.dimension_id IS 'DBF-FIN-024';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.code IS 'DBF-FIN-025 — RULE-FIN-002 (UQ_FIN_DIMENSION_VALUE_DIM_CODE)';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.name_ar IS 'DBF-FIN-026';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.name_en IS 'DBF-FIN-027';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.sort_order IS 'DBF-FIN-028';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.is_active_fl IS 'DBF-FIN-029';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.created_by IS 'DBF-FIN-030';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.created_at IS 'DBF-FIN-031';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.updated_by IS 'DBF-FIN-032';
COMMENT ON COLUMN FIN_DIMENSION_VALUE.updated_at IS 'DBF-FIN-033';

COMMENT ON TABLE FIN_JOURNAL_ENTRY IS 'ENT-FIN-004 JournalEntry — PRIVATE, immutable after POSTED (POL-FIN-013); [DBF-FIN-034..050]';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.journal_entry_pk IS 'DBF-FIN-034';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.doc_no IS 'DBF-FIN-035 — platform numbering engine, unique per fiscal_year_id';
-- NOTE (ALIGN-BE): "platform numbering engine" is a fiction — no such component exists in this
-- repo. doc_no is `JV-{fiscal_year.code}-{NNNNNN}`, counter per fiscal_year_id, produced by a
-- FIN-local generator in com.erp.fin. V22 applied this comment text verbatim and must never be
-- edited, so the live column comment keeps the wrong phrase; corrected here and in srs-fin.md.
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.doc_date IS 'DBF-FIN-036';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.fiscal_year_id IS 'DBF-FIN-037';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.period_id IS 'DBF-FIN-038 — RULE-FIN-008 period-open-at-post-time, application layer';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.journal_type_code IS 'DBF-FIN-039 — lookup JOURNAL_TYPE (XM-FIN-001)';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.status_code IS 'DBF-FIN-040 — lookup JOURNAL_STATUS (XM-FIN-001)';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.event_reference IS 'DBF-FIN-041 — RULE-FIN-004 idempotency (UQ_FIN_JOURNAL_ENTRY_EVENT_REF)';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.original_entry_id IS 'DBF-FIN-042 — RULE-FIN-011 reversal link';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.reversal_entry_id IS 'DBF-FIN-043 — RULE-FIN-011 reversal link';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.description_ar IS 'DBF-FIN-044';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.description_en IS 'DBF-FIN-045';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.posted_at IS 'DBF-FIN-046';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.created_by IS 'DBF-FIN-047';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.created_at IS 'DBF-FIN-048';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.updated_by IS 'DBF-FIN-049';
COMMENT ON COLUMN FIN_JOURNAL_ENTRY.updated_at IS 'DBF-FIN-050';

COMMENT ON TABLE FIN_JOURNAL_LINE IS 'ENT-FIN-005 JournalLine — PRIVATE; [DBF-FIN-051..060]';
COMMENT ON COLUMN FIN_JOURNAL_LINE.journal_line_pk IS 'DBF-FIN-051';
COMMENT ON COLUMN FIN_JOURNAL_LINE.journal_entry_id IS 'DBF-FIN-052';
COMMENT ON COLUMN FIN_JOURNAL_LINE.line_no IS 'DBF-FIN-053';
COMMENT ON COLUMN FIN_JOURNAL_LINE.account_id IS 'DBF-FIN-054 — RULE-FIN-007 leaf/active check, application layer';
COMMENT ON COLUMN FIN_JOURNAL_LINE.amount IS 'DBF-FIN-055 — POL-FIN-005 always positive (CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE)';
COMMENT ON COLUMN FIN_JOURNAL_LINE.direction_code IS 'DBF-FIN-056 — lookup DEBIT_CREDIT (XM-FIN-001)';
COMMENT ON COLUMN FIN_JOURNAL_LINE.is_remainder_fl IS 'DBF-FIN-057 — RULE-FIN-010';
COMMENT ON COLUMN FIN_JOURNAL_LINE.description_ar IS 'DBF-FIN-058';
COMMENT ON COLUMN FIN_JOURNAL_LINE.description_en IS 'DBF-FIN-059';
COMMENT ON COLUMN FIN_JOURNAL_LINE.created_at IS 'DBF-FIN-060';

COMMENT ON TABLE FIN_JOURNAL_LINE_DIM IS 'ENT-FIN-006 JournalLineDimension — PRIVATE; [DBF-FIN-061..064]';
COMMENT ON COLUMN FIN_JOURNAL_LINE_DIM.journal_line_dim_pk IS 'DBF-FIN-061';
COMMENT ON COLUMN FIN_JOURNAL_LINE_DIM.journal_line_id IS 'DBF-FIN-062';
COMMENT ON COLUMN FIN_JOURNAL_LINE_DIM.dimension_id IS 'DBF-FIN-063';
COMMENT ON COLUMN FIN_JOURNAL_LINE_DIM.dimension_value_id IS 'DBF-FIN-064 — RULE-FIN-009, application layer';

COMMENT ON TABLE FIN_FISCAL_YEAR IS 'ENT-FIN-007 FiscalYear — PRIVATE; [DBF-FIN-065..074]';
COMMENT ON COLUMN FIN_FISCAL_YEAR.fiscal_year_pk IS 'DBF-FIN-065';
COMMENT ON COLUMN FIN_FISCAL_YEAR.code IS 'DBF-FIN-066';
COMMENT ON COLUMN FIN_FISCAL_YEAR.start_date IS 'DBF-FIN-067';
COMMENT ON COLUMN FIN_FISCAL_YEAR.end_date IS 'DBF-FIN-068';
COMMENT ON COLUMN FIN_FISCAL_YEAR.status_code IS 'DBF-FIN-069 — lookup FISCAL_YEAR_STATUS (XM-FIN-001)';
COMMENT ON COLUMN FIN_FISCAL_YEAR.is_active_fl IS 'DBF-FIN-070';
COMMENT ON COLUMN FIN_FISCAL_YEAR.created_by IS 'DBF-FIN-071';
COMMENT ON COLUMN FIN_FISCAL_YEAR.created_at IS 'DBF-FIN-072';
COMMENT ON COLUMN FIN_FISCAL_YEAR.updated_by IS 'DBF-FIN-073';
COMMENT ON COLUMN FIN_FISCAL_YEAR.updated_at IS 'DBF-FIN-074';

COMMENT ON TABLE FIN_FISCAL_PERIOD IS 'ENT-FIN-008 FiscalPeriod — PRIVATE; [DBF-FIN-075..088]';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.fiscal_period_pk IS 'DBF-FIN-075';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.fiscal_year_id IS 'DBF-FIN-076';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.period_no IS 'DBF-FIN-077';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.name_ar IS 'DBF-FIN-078';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.name_en IS 'DBF-FIN-079';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.start_date IS 'DBF-FIN-080';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.end_date IS 'DBF-FIN-081';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.status_code IS 'DBF-FIN-082 — lookup PERIOD_STATE (XM-FIN-001); RULE-FIN-008, RULE-FIN-014 application layer';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.closed_by IS 'DBF-FIN-083 — RULE-FIN-015 SoD, application layer via SEC';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.closed_at IS 'DBF-FIN-084';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.created_by IS 'DBF-FIN-085';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.created_at IS 'DBF-FIN-086';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.updated_by IS 'DBF-FIN-087';
COMMENT ON COLUMN FIN_FISCAL_PERIOD.updated_at IS 'DBF-FIN-088';

COMMENT ON TABLE FIN_EVENT_TYPE_RULE IS 'ENT-FIN-009 EventTypeRule — PRIVATE; [DBF-FIN-089..097]';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.event_type_rule_pk IS 'DBF-FIN-089';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.event_type_code IS 'DBF-FIN-090 — lookup ACCOUNTING_EVENT_TYPE (XM-FIN-001); RULE-FIN-005 (UQ_FIN_EVENT_TYPE_RULE_CODE)';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.name_ar IS 'DBF-FIN-091';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.name_en IS 'DBF-FIN-092';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.is_active_fl IS 'DBF-FIN-093';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.created_by IS 'DBF-FIN-094';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.created_at IS 'DBF-FIN-095';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.updated_by IS 'DBF-FIN-096';
COMMENT ON COLUMN FIN_EVENT_TYPE_RULE.updated_at IS 'DBF-FIN-097';

COMMENT ON TABLE FIN_RULE_LINE IS 'ENT-FIN-010 RuleLine — PRIVATE; [DBF-FIN-098..108]';
COMMENT ON COLUMN FIN_RULE_LINE.rule_line_pk IS 'DBF-FIN-098';
COMMENT ON COLUMN FIN_RULE_LINE.event_type_rule_id IS 'DBF-FIN-099';
COMMENT ON COLUMN FIN_RULE_LINE.line_no IS 'DBF-FIN-100';
COMMENT ON COLUMN FIN_RULE_LINE.account_derivation_type_code IS 'DBF-FIN-101 — lookup ACCOUNT_DERIVATION_TYPE (XM-FIN-001)';
COMMENT ON COLUMN FIN_RULE_LINE.account_derivation_value IS 'DBF-FIN-102';
COMMENT ON COLUMN FIN_RULE_LINE.amount_source_type_code IS 'DBF-FIN-103 — lookup AMOUNT_SOURCE_TYPE (XM-FIN-001)';
COMMENT ON COLUMN FIN_RULE_LINE.amount_source_value IS 'DBF-FIN-104';
COMMENT ON COLUMN FIN_RULE_LINE.direction_code IS 'DBF-FIN-105 — lookup DEBIT_CREDIT (XM-FIN-001)';
COMMENT ON COLUMN FIN_RULE_LINE.distribution_type_code IS 'DBF-FIN-106 — lookup DISTRIBUTION_TYPE (XM-FIN-001); RULE-FIN-003 application layer';
COMMENT ON COLUMN FIN_RULE_LINE.is_remainder_fl IS 'DBF-FIN-107 — RULE-FIN-003, RULE-FIN-010';
COMMENT ON COLUMN FIN_RULE_LINE.created_at IS 'DBF-FIN-108';

COMMENT ON TABLE FIN_RECURRING_TEMPLATE IS 'ENT-FIN-011 RecurringTemplate — PRIVATE; [DBF-FIN-109..121]';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.recurring_template_pk IS 'DBF-FIN-109';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.name_ar IS 'DBF-FIN-110';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.name_en IS 'DBF-FIN-111';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.schedule_type_code IS 'DBF-FIN-112 — lookup RECURRING_SCHEDULE_TYPE (XM-FIN-001)';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.frequency_code IS 'DBF-FIN-113 — lookup RECURRING_FREQUENCY (XM-FIN-001)';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.start_date IS 'DBF-FIN-114';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.next_run_date IS 'DBF-FIN-115';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.end_date IS 'DBF-FIN-116';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.is_active_fl IS 'DBF-FIN-117';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.created_by IS 'DBF-FIN-118';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.created_at IS 'DBF-FIN-119';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.updated_by IS 'DBF-FIN-120';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE.updated_at IS 'DBF-FIN-121';

COMMENT ON TABLE FIN_RECURRING_TEMPLATE_LINE IS 'ENT-FIN-012 RecurringTemplateLine — PRIVATE; [DBF-FIN-122..129]';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.recurring_template_line_pk IS 'DBF-FIN-122';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.recurring_template_id IS 'DBF-FIN-123';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.line_no IS 'DBF-FIN-124';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.account_id IS 'DBF-FIN-125';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.amount IS 'DBF-FIN-126 — CHK positive, reuses RULE-FIN-006 spirit';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.direction_code IS 'DBF-FIN-127 — lookup DEBIT_CREDIT (XM-FIN-001)';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.dimension_value_id IS 'DBF-FIN-128';
COMMENT ON COLUMN FIN_RECURRING_TEMPLATE_LINE.created_at IS 'DBF-FIN-129';

COMMENT ON TABLE FIN_ALLOCATION_RULE IS 'ENT-FIN-013 AllocationRule — PRIVATE; [DBF-FIN-130..138]';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.allocation_rule_pk IS 'DBF-FIN-130';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.name_ar IS 'DBF-FIN-131';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.name_en IS 'DBF-FIN-132';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.source_account_id IS 'DBF-FIN-133';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.is_active_fl IS 'DBF-FIN-134';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.created_by IS 'DBF-FIN-135';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.created_at IS 'DBF-FIN-136';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.updated_by IS 'DBF-FIN-137';
COMMENT ON COLUMN FIN_ALLOCATION_RULE.updated_at IS 'DBF-FIN-138';

COMMENT ON TABLE FIN_ALLOCATION_TARGET IS 'ENT-FIN-014 AllocationTarget — PRIVATE; [DBF-FIN-139..146]';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.allocation_target_pk IS 'DBF-FIN-139';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.allocation_rule_id IS 'DBF-FIN-140';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.line_no IS 'DBF-FIN-141';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.target_account_id IS 'DBF-FIN-142';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.dimension_value_id IS 'DBF-FIN-143';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.distribution_type_code IS 'DBF-FIN-144 — lookup DISTRIBUTION_TYPE (XM-FIN-001)';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.distribution_value IS 'DBF-FIN-145';
COMMENT ON COLUMN FIN_ALLOCATION_TARGET.is_remainder_fl IS 'DBF-FIN-146 — RULE-FIN-003, RULE-FIN-010';

-- BLOCK 5 — CONSTRAINTS

-- 5a PK
ALTER TABLE FIN_ACCOUNT                  ADD CONSTRAINT PK_FIN_ACCOUNT                  PRIMARY KEY (account_pk);
ALTER TABLE FIN_DIMENSION                ADD CONSTRAINT PK_FIN_DIMENSION                PRIMARY KEY (dimension_pk);
ALTER TABLE FIN_DIMENSION_VALUE          ADD CONSTRAINT PK_FIN_DIMENSION_VALUE          PRIMARY KEY (dimension_value_pk);
ALTER TABLE FIN_JOURNAL_ENTRY            ADD CONSTRAINT PK_FIN_JOURNAL_ENTRY            PRIMARY KEY (journal_entry_pk);
ALTER TABLE FIN_JOURNAL_LINE             ADD CONSTRAINT PK_FIN_JOURNAL_LINE             PRIMARY KEY (journal_line_pk);
ALTER TABLE FIN_JOURNAL_LINE_DIM         ADD CONSTRAINT PK_FIN_JOURNAL_LINE_DIM         PRIMARY KEY (journal_line_dim_pk);
ALTER TABLE FIN_FISCAL_YEAR              ADD CONSTRAINT PK_FIN_FISCAL_YEAR              PRIMARY KEY (fiscal_year_pk);
ALTER TABLE FIN_FISCAL_PERIOD            ADD CONSTRAINT PK_FIN_FISCAL_PERIOD            PRIMARY KEY (fiscal_period_pk);
ALTER TABLE FIN_EVENT_TYPE_RULE          ADD CONSTRAINT PK_FIN_EVENT_TYPE_RULE          PRIMARY KEY (event_type_rule_pk);
ALTER TABLE FIN_RULE_LINE                ADD CONSTRAINT PK_FIN_RULE_LINE                PRIMARY KEY (rule_line_pk);
ALTER TABLE FIN_RECURRING_TEMPLATE       ADD CONSTRAINT PK_FIN_RECURRING_TEMPLATE       PRIMARY KEY (recurring_template_pk);
ALTER TABLE FIN_RECURRING_TEMPLATE_LINE  ADD CONSTRAINT PK_FIN_RECURRING_TEMPLATE_LINE  PRIMARY KEY (recurring_template_line_pk);
ALTER TABLE FIN_ALLOCATION_RULE          ADD CONSTRAINT PK_FIN_ALLOCATION_RULE          PRIMARY KEY (allocation_rule_pk);
ALTER TABLE FIN_ALLOCATION_TARGET        ADD CONSTRAINT PK_FIN_ALLOCATION_TARGET        PRIMARY KEY (allocation_target_pk);

-- 5b UNIQUE
ALTER TABLE FIN_ACCOUNT           ADD CONSTRAINT UQ_FIN_ACCOUNT_CODE                UNIQUE (code);
ALTER TABLE FIN_DIMENSION         ADD CONSTRAINT UQ_FIN_DIMENSION_CODE              UNIQUE (code);
ALTER TABLE FIN_DIMENSION_VALUE   ADD CONSTRAINT UQ_FIN_DIMENSION_VALUE_DIM_CODE    UNIQUE (dimension_id, code);   -- RULE-FIN-002
ALTER TABLE FIN_JOURNAL_ENTRY     ADD CONSTRAINT UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO    UNIQUE (fiscal_year_id, doc_no);
ALTER TABLE FIN_JOURNAL_ENTRY     ADD CONSTRAINT UQ_FIN_JOURNAL_ENTRY_EVENT_REF     UNIQUE (event_reference);      -- RULE-FIN-004 (NULLs never conflict)
ALTER TABLE FIN_FISCAL_YEAR       ADD CONSTRAINT UQ_FIN_FISCAL_YEAR_CODE            UNIQUE (code);
ALTER TABLE FIN_EVENT_TYPE_RULE   ADD CONSTRAINT UQ_FIN_EVENT_TYPE_RULE_CODE        UNIQUE (event_type_code);      -- RULE-FIN-005, §6.4 one rule per type

-- 5c CHECK
ALTER TABLE FIN_JOURNAL_LINE            ADD CONSTRAINT CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE   CHECK (amount > 0);   -- POL-FIN-005
ALTER TABLE FIN_RECURRING_TEMPLATE_LINE ADD CONSTRAINT CHK_FIN_RECURRING_TPL_LINE_AMOUNT_POS  CHECK (amount > 0);
-- No CHECK enumerates any lookup-backed column's value set: FIN registers all 13 keys into
-- MDL (XM-FIN-001); the closed sets live in MDL_LOOKUP_VALUE, not as local CHECK constraints
-- (unlike SEC's ADR-SEC-001, which applied only because MDL did not yet exist at SEC's time).

-- 5d intra-module FK (parent PK first)
ALTER TABLE FIN_ACCOUNT                 ADD CONSTRAINT FK_ACCOUNT_PARENT             FOREIGN KEY (parent_account_id) REFERENCES FIN_ACCOUNT (account_pk);
ALTER TABLE FIN_DIMENSION_VALUE         ADD CONSTRAINT FK_DIMENSION_VALUE_DIMENSION  FOREIGN KEY (dimension_id) REFERENCES FIN_DIMENSION (dimension_pk);
ALTER TABLE FIN_FISCAL_PERIOD           ADD CONSTRAINT FK_FISCAL_PERIOD_YEAR         FOREIGN KEY (fiscal_year_id) REFERENCES FIN_FISCAL_YEAR (fiscal_year_pk);
ALTER TABLE FIN_JOURNAL_ENTRY           ADD CONSTRAINT FK_JOURNAL_ENTRY_YEAR         FOREIGN KEY (fiscal_year_id) REFERENCES FIN_FISCAL_YEAR (fiscal_year_pk);
ALTER TABLE FIN_JOURNAL_ENTRY           ADD CONSTRAINT FK_JOURNAL_ENTRY_PERIOD       FOREIGN KEY (period_id) REFERENCES FIN_FISCAL_PERIOD (fiscal_period_pk);
ALTER TABLE FIN_JOURNAL_ENTRY           ADD CONSTRAINT FK_JOURNAL_ENTRY_ORIGINAL     FOREIGN KEY (original_entry_id) REFERENCES FIN_JOURNAL_ENTRY (journal_entry_pk);
ALTER TABLE FIN_JOURNAL_ENTRY           ADD CONSTRAINT FK_JOURNAL_ENTRY_REVERSAL     FOREIGN KEY (reversal_entry_id) REFERENCES FIN_JOURNAL_ENTRY (journal_entry_pk);
ALTER TABLE FIN_JOURNAL_LINE            ADD CONSTRAINT FK_JOURNAL_LINE_ENTRY         FOREIGN KEY (journal_entry_id) REFERENCES FIN_JOURNAL_ENTRY (journal_entry_pk);
ALTER TABLE FIN_JOURNAL_LINE            ADD CONSTRAINT FK_JOURNAL_LINE_ACCOUNT       FOREIGN KEY (account_id) REFERENCES FIN_ACCOUNT (account_pk);
ALTER TABLE FIN_JOURNAL_LINE_DIM        ADD CONSTRAINT FK_JOURNAL_LINE_DIM_LINE      FOREIGN KEY (journal_line_id) REFERENCES FIN_JOURNAL_LINE (journal_line_pk);
ALTER TABLE FIN_JOURNAL_LINE_DIM        ADD CONSTRAINT FK_JOURNAL_LINE_DIM_DIMENSION FOREIGN KEY (dimension_id) REFERENCES FIN_DIMENSION (dimension_pk);
ALTER TABLE FIN_JOURNAL_LINE_DIM        ADD CONSTRAINT FK_JOURNAL_LINE_DIM_VALUE     FOREIGN KEY (dimension_value_id) REFERENCES FIN_DIMENSION_VALUE (dimension_value_pk);
ALTER TABLE FIN_RULE_LINE               ADD CONSTRAINT FK_RULE_LINE_RULE             FOREIGN KEY (event_type_rule_id) REFERENCES FIN_EVENT_TYPE_RULE (event_type_rule_pk);
ALTER TABLE FIN_RECURRING_TEMPLATE_LINE ADD CONSTRAINT FK_RECURRING_TPL_LINE_TPL     FOREIGN KEY (recurring_template_id) REFERENCES FIN_RECURRING_TEMPLATE (recurring_template_pk);
ALTER TABLE FIN_RECURRING_TEMPLATE_LINE ADD CONSTRAINT FK_RECURRING_TPL_LINE_ACCOUNT FOREIGN KEY (account_id) REFERENCES FIN_ACCOUNT (account_pk);
ALTER TABLE FIN_RECURRING_TEMPLATE_LINE ADD CONSTRAINT FK_RECURRING_TPL_LINE_DIMVAL  FOREIGN KEY (dimension_value_id) REFERENCES FIN_DIMENSION_VALUE (dimension_value_pk);
ALTER TABLE FIN_ALLOCATION_RULE         ADD CONSTRAINT FK_ALLOCATION_RULE_SRC_ACCT   FOREIGN KEY (source_account_id) REFERENCES FIN_ACCOUNT (account_pk);
ALTER TABLE FIN_ALLOCATION_TARGET       ADD CONSTRAINT FK_ALLOCATION_TARGET_RULE     FOREIGN KEY (allocation_rule_id) REFERENCES FIN_ALLOCATION_RULE (allocation_rule_pk);
ALTER TABLE FIN_ALLOCATION_TARGET       ADD CONSTRAINT FK_ALLOCATION_TARGET_ACCOUNT  FOREIGN KEY (target_account_id) REFERENCES FIN_ACCOUNT (account_pk);
ALTER TABLE FIN_ALLOCATION_TARGET       ADD CONSTRAINT FK_ALLOCATION_TARGET_DIMVAL   FOREIGN KEY (dimension_value_id) REFERENCES FIN_DIMENSION_VALUE (dimension_value_pk);

-- BLOCK 6 — TRIGGERS
-- none: every SRS RULE is enforced at the application layer (multi-row / cross-module /
-- time-based logic) or already covered structurally by a constraint above (RULE-FIN-002,
-- POL-FIN-005 amount positivity, RULE-FIN-004/005 uniqueness). No PK-population trigger.

-- BLOCK 7 — INDEXES (non-PK; every FK column + every SRS search/list filter column)
CREATE UNIQUE INDEX UQ_FIN_ACCOUNT_RETAINED_EARNINGS ON FIN_ACCOUNT (is_retained_earnings_fl) WHERE is_retained_earnings_fl;
CREATE INDEX IDX_FIN_ACCOUNT_PARENT              ON FIN_ACCOUNT (parent_account_id);
CREATE INDEX IDX_FIN_ACCOUNT_TYPE                ON FIN_ACCOUNT (account_type_code);
CREATE INDEX IDX_FIN_DIMENSION_VALUE_DIMENSION   ON FIN_DIMENSION_VALUE (dimension_id);
CREATE INDEX IDX_FIN_JOURNAL_ENTRY_YEAR          ON FIN_JOURNAL_ENTRY (fiscal_year_id);
CREATE INDEX IDX_FIN_JOURNAL_ENTRY_PERIOD        ON FIN_JOURNAL_ENTRY (period_id);
CREATE INDEX IDX_FIN_JOURNAL_ENTRY_STATUS        ON FIN_JOURNAL_ENTRY (status_code);
CREATE INDEX IDX_FIN_JOURNAL_ENTRY_DOCDATE       ON FIN_JOURNAL_ENTRY (doc_date);
CREATE INDEX IDX_FIN_JOURNAL_LINE_ENTRY          ON FIN_JOURNAL_LINE (journal_entry_id);
CREATE INDEX IDX_FIN_JOURNAL_LINE_ACCOUNT        ON FIN_JOURNAL_LINE (account_id);
CREATE INDEX IDX_FIN_JOURNAL_LINE_DIM_LINE       ON FIN_JOURNAL_LINE_DIM (journal_line_id);
CREATE INDEX IDX_FIN_JOURNAL_LINE_DIM_VALUE      ON FIN_JOURNAL_LINE_DIM (dimension_value_id);
CREATE INDEX IDX_FIN_FISCAL_PERIOD_YEAR          ON FIN_FISCAL_PERIOD (fiscal_year_id);
CREATE INDEX IDX_FIN_FISCAL_PERIOD_STATUS        ON FIN_FISCAL_PERIOD (status_code);
CREATE INDEX IDX_FIN_RULE_LINE_RULE              ON FIN_RULE_LINE (event_type_rule_id);
CREATE INDEX IDX_FIN_RECURRING_TPL_LINE_TPL      ON FIN_RECURRING_TEMPLATE_LINE (recurring_template_id);
CREATE INDEX IDX_FIN_RECURRING_TPL_LINE_ACCOUNT  ON FIN_RECURRING_TEMPLATE_LINE (account_id);
CREATE INDEX IDX_FIN_ALLOCATION_RULE_SRC_ACCT    ON FIN_ALLOCATION_RULE (source_account_id);
CREATE INDEX IDX_FIN_ALLOCATION_TARGET_RULE      ON FIN_ALLOCATION_TARGET (allocation_rule_id);
CREATE INDEX IDX_FIN_ALLOCATION_TARGET_ACCOUNT   ON FIN_ALLOCATION_TARGET (target_account_id);

-- BLOCK 8 — LOOKUP SEED DATA
-- none in this script: all 13 FIN-owned lookup types are registered and seeded through
-- MDL's own API (API-MDL-002/API-MDL-006, per FIN's onboarding — REQ-FIN-045), not via
-- local INSERTs; the values live in MDL_LOOKUP_TYPE/MDL_LOOKUP_VALUE, per XM-FIN-001.
COMMIT;

-- BLOCK 9 — VIEWS
-- none required by this SRS (reports are computed queries at the API layer, per
-- POL-FIN-009 — never a materialized/stored view standing in for a live balance).

-- BLOCK 10 — FUNCTIONS / PROCEDURES
-- none required by this SRS.

-- BLOCK 11 — DEFERRED FK PATCH BLOCKS
-- none: FIN's one cross-module dependency (XM-FIN-001) is SOFT-READ, never a deferred
-- HARD-FK, and MDL is already gated regardless.
```

## 4. DECISIONS APPLIED

| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| ADR-FIN-001 | Only one formal XM row (XM-FIN-001, SOFT-READ → MDL) is assigned at THIS stage; FIN's identity/authorization dependency on SEC and its own self-registration into SEC follow the exact precedent SEC's and MDL's own P2/P3.1 already set — platform-standard integration narrated in the backend plan, not an `XM` row, since no physical cross-module FK exists anywhere in this pipeline | erp/decisions/FIN/ADR-FIN-001.md | ACCEPTED (non-breaking). Still correct as written. It did NOT cover XM-FIN-002, added at ALIGN-BE for FIN's read of SEC's user directory; that row was RETIRED on 2026-09-12 when `FinSeparationOfDutiesService` was deleted, so the ADR again covers the whole of FIN↔SEC — see §2 |
| DEFAULT | All 13 FIN-owned lookup-backed columns are plain VARCHAR, validated against MDL at the application layer (XM-FIN-001), never CHECK-constrained locally — unlike SEC's ADR-SEC-001, which applied only because MDL did not exist yet at SEC's build time | this stage, MDL v1 already gated | non-breaking |
| DEFAULT | `amount` columns use `NUMERIC(18,4)` | [KB:erp-domain-standards §6] | non-breaking |

No BLOCKED ADR — the pass was not stopped.

## 5. REGISTRY CONTENT
See `registry-db-fin.md`.

## 6. DBF id definitions (cross-reference index — full detail in §1; `[traces]` = ENT + REQ)
**DBF-FIN-001** — FIN_ACCOUNT.account_pk [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-002** — FIN_ACCOUNT.code [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-003** — FIN_ACCOUNT.name_ar [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-004** — FIN_ACCOUNT.name_en [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-005** — FIN_ACCOUNT.account_type_code [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-006** — FIN_ACCOUNT.nature_code [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-007** — FIN_ACCOUNT.parent_account_id [ENT-FIN-001, REQ-FIN-001, REQ-FIN-002]
**DBF-FIN-008** — FIN_ACCOUNT.is_leaf_fl [ENT-FIN-001, REQ-FIN-002, REQ-FIN-019]
**DBF-FIN-009** — FIN_ACCOUNT.is_active_fl [ENT-FIN-001, REQ-FIN-003, REQ-FIN-019]
**DBF-FIN-147** — FIN_ACCOUNT.is_retained_earnings_fl [ENT-FIN-001, REQ-FIN-036]
**DBF-FIN-010** — FIN_ACCOUNT.created_by [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-011** — FIN_ACCOUNT.created_at [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-012** — FIN_ACCOUNT.updated_by [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-013** — FIN_ACCOUNT.updated_at [ENT-FIN-001, REQ-FIN-001]
**DBF-FIN-014** — FIN_DIMENSION.dimension_pk [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-015** — FIN_DIMENSION.code [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-016** — FIN_DIMENSION.name_ar [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-017** — FIN_DIMENSION.name_en [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-018** — FIN_DIMENSION.is_active_fl [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-019** — FIN_DIMENSION.created_by [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-020** — FIN_DIMENSION.created_at [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-021** — FIN_DIMENSION.updated_by [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-022** — FIN_DIMENSION.updated_at [ENT-FIN-002, REQ-FIN-004]
**DBF-FIN-023** — FIN_DIMENSION_VALUE.dimension_value_pk [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-024** — FIN_DIMENSION_VALUE.dimension_id [ENT-FIN-003, ENT-FIN-002, REQ-FIN-005]
**DBF-FIN-025** — FIN_DIMENSION_VALUE.code [ENT-FIN-003, REQ-FIN-005, REQ-FIN-006]
**DBF-FIN-026** — FIN_DIMENSION_VALUE.name_ar [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-027** — FIN_DIMENSION_VALUE.name_en [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-028** — FIN_DIMENSION_VALUE.sort_order [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-029** — FIN_DIMENSION_VALUE.is_active_fl [ENT-FIN-003, REQ-FIN-021]
**DBF-FIN-030** — FIN_DIMENSION_VALUE.created_by [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-031** — FIN_DIMENSION_VALUE.created_at [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-032** — FIN_DIMENSION_VALUE.updated_by [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-033** — FIN_DIMENSION_VALUE.updated_at [ENT-FIN-003, REQ-FIN-005]
**DBF-FIN-034** — FIN_JOURNAL_ENTRY.journal_entry_pk [ENT-FIN-004, REQ-FIN-010, REQ-FIN-014]
**DBF-FIN-035** — FIN_JOURNAL_ENTRY.doc_no [ENT-FIN-004, REQ-FIN-010, REQ-FIN-014]
**DBF-FIN-036** — FIN_JOURNAL_ENTRY.doc_date [ENT-FIN-004, REQ-FIN-010, REQ-FIN-014]
**DBF-FIN-037** — FIN_JOURNAL_ENTRY.fiscal_year_id [ENT-FIN-004, ENT-FIN-007, REQ-FIN-010, REQ-FIN-014]
**DBF-FIN-038** — FIN_JOURNAL_ENTRY.period_id [ENT-FIN-004, ENT-FIN-008, REQ-FIN-020]
**DBF-FIN-039** — FIN_JOURNAL_ENTRY.journal_type_code [ENT-FIN-004, REQ-FIN-010, REQ-FIN-014]
**DBF-FIN-040** — FIN_JOURNAL_ENTRY.status_code [ENT-FIN-004, REQ-FIN-017]
**DBF-FIN-041** — FIN_JOURNAL_ENTRY.event_reference [ENT-FIN-004, REQ-FIN-010, REQ-FIN-011]
**DBF-FIN-042** — FIN_JOURNAL_ENTRY.original_entry_id [ENT-FIN-004, REQ-FIN-028]
**DBF-FIN-043** — FIN_JOURNAL_ENTRY.reversal_entry_id [ENT-FIN-004, REQ-FIN-028]
**DBF-FIN-044** — FIN_JOURNAL_ENTRY.description_ar [ENT-FIN-004, REQ-FIN-014]
**DBF-FIN-045** — FIN_JOURNAL_ENTRY.description_en [ENT-FIN-004, REQ-FIN-014]
**DBF-FIN-046** — FIN_JOURNAL_ENTRY.posted_at [ENT-FIN-004, REQ-FIN-017]
**DBF-FIN-047** — FIN_JOURNAL_ENTRY.created_by [ENT-FIN-004, REQ-FIN-010, REQ-FIN-014]
**DBF-FIN-048** — FIN_JOURNAL_ENTRY.created_at [ENT-FIN-004, REQ-FIN-010, REQ-FIN-014]
**DBF-FIN-049** — FIN_JOURNAL_ENTRY.updated_by [ENT-FIN-004, REQ-FIN-016]
**DBF-FIN-050** — FIN_JOURNAL_ENTRY.updated_at [ENT-FIN-004, REQ-FIN-016]
**DBF-FIN-051** — FIN_JOURNAL_LINE.journal_line_pk [ENT-FIN-005, REQ-FIN-014]
**DBF-FIN-052** — FIN_JOURNAL_LINE.journal_entry_id [ENT-FIN-005, ENT-FIN-004, REQ-FIN-014]
**DBF-FIN-053** — FIN_JOURNAL_LINE.line_no [ENT-FIN-005, REQ-FIN-014]
**DBF-FIN-054** — FIN_JOURNAL_LINE.account_id [ENT-FIN-005, ENT-FIN-001, REQ-FIN-019]
**DBF-FIN-055** — FIN_JOURNAL_LINE.amount [ENT-FIN-005, REQ-FIN-012, REQ-FIN-018]
**DBF-FIN-056** — FIN_JOURNAL_LINE.direction_code [ENT-FIN-005, REQ-FIN-018]
**DBF-FIN-057** — FIN_JOURNAL_LINE.is_remainder_fl [ENT-FIN-005, REQ-FIN-012]
**DBF-FIN-058** — FIN_JOURNAL_LINE.description_ar [ENT-FIN-005, REQ-FIN-014]
**DBF-FIN-059** — FIN_JOURNAL_LINE.description_en [ENT-FIN-005, REQ-FIN-014]
**DBF-FIN-060** — FIN_JOURNAL_LINE.created_at [ENT-FIN-005, REQ-FIN-014]
**DBF-FIN-061** — FIN_JOURNAL_LINE_DIM.journal_line_dim_pk [ENT-FIN-006, REQ-FIN-021]
**DBF-FIN-062** — FIN_JOURNAL_LINE_DIM.journal_line_id [ENT-FIN-006, ENT-FIN-005, REQ-FIN-021]
**DBF-FIN-063** — FIN_JOURNAL_LINE_DIM.dimension_id [ENT-FIN-006, ENT-FIN-002, REQ-FIN-021]
**DBF-FIN-064** — FIN_JOURNAL_LINE_DIM.dimension_value_id [ENT-FIN-006, ENT-FIN-003, REQ-FIN-021, REQ-FIN-043]
**DBF-FIN-065** — FIN_FISCAL_YEAR.fiscal_year_pk [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-066** — FIN_FISCAL_YEAR.code [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-067** — FIN_FISCAL_YEAR.start_date [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-068** — FIN_FISCAL_YEAR.end_date [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-069** — FIN_FISCAL_YEAR.status_code [ENT-FIN-007, REQ-FIN-036]
**DBF-FIN-070** — FIN_FISCAL_YEAR.is_active_fl [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-071** — FIN_FISCAL_YEAR.created_by [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-072** — FIN_FISCAL_YEAR.created_at [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-073** — FIN_FISCAL_YEAR.updated_by [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-074** — FIN_FISCAL_YEAR.updated_at [ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-075** — FIN_FISCAL_PERIOD.fiscal_period_pk [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-076** — FIN_FISCAL_PERIOD.fiscal_year_id [ENT-FIN-008, ENT-FIN-007, REQ-FIN-031]
**DBF-FIN-077** — FIN_FISCAL_PERIOD.period_no [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-078** — FIN_FISCAL_PERIOD.name_ar [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-079** — FIN_FISCAL_PERIOD.name_en [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-080** — FIN_FISCAL_PERIOD.start_date [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-081** — FIN_FISCAL_PERIOD.end_date [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-082** — FIN_FISCAL_PERIOD.status_code [ENT-FIN-008, REQ-FIN-020, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035]
**DBF-FIN-083** — FIN_FISCAL_PERIOD.closed_by [ENT-FIN-008, REQ-FIN-037]
**DBF-FIN-084** — FIN_FISCAL_PERIOD.closed_at [ENT-FIN-008, REQ-FIN-037]
**DBF-FIN-085** — FIN_FISCAL_PERIOD.created_by [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-086** — FIN_FISCAL_PERIOD.created_at [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-087** — FIN_FISCAL_PERIOD.updated_by [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-088** — FIN_FISCAL_PERIOD.updated_at [ENT-FIN-008, REQ-FIN-031]
**DBF-FIN-089** — FIN_EVENT_TYPE_RULE.event_type_rule_pk [ENT-FIN-009, REQ-FIN-007]
**DBF-FIN-090** — FIN_EVENT_TYPE_RULE.event_type_code [ENT-FIN-009, REQ-FIN-007, REQ-FIN-013]
**DBF-FIN-091** — FIN_EVENT_TYPE_RULE.name_ar [ENT-FIN-009, REQ-FIN-007]
**DBF-FIN-092** — FIN_EVENT_TYPE_RULE.name_en [ENT-FIN-009, REQ-FIN-007]
**DBF-FIN-093** — FIN_EVENT_TYPE_RULE.is_active_fl [ENT-FIN-009, REQ-FIN-013]
**DBF-FIN-094** — FIN_EVENT_TYPE_RULE.created_by [ENT-FIN-009, REQ-FIN-007]
**DBF-FIN-095** — FIN_EVENT_TYPE_RULE.created_at [ENT-FIN-009, REQ-FIN-007]
**DBF-FIN-096** — FIN_EVENT_TYPE_RULE.updated_by [ENT-FIN-009, REQ-FIN-007]
**DBF-FIN-097** — FIN_EVENT_TYPE_RULE.updated_at [ENT-FIN-009, REQ-FIN-007]
**DBF-FIN-098** — FIN_RULE_LINE.rule_line_pk [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-099** — FIN_RULE_LINE.event_type_rule_id [ENT-FIN-010, ENT-FIN-009, REQ-FIN-008]
**DBF-FIN-100** — FIN_RULE_LINE.line_no [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-101** — FIN_RULE_LINE.account_derivation_type_code [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-102** — FIN_RULE_LINE.account_derivation_value [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-103** — FIN_RULE_LINE.amount_source_type_code [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-104** — FIN_RULE_LINE.amount_source_value [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-105** — FIN_RULE_LINE.direction_code [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-106** — FIN_RULE_LINE.distribution_type_code [ENT-FIN-010, REQ-FIN-009, REQ-FIN-012]
**DBF-FIN-107** — FIN_RULE_LINE.is_remainder_fl [ENT-FIN-010, REQ-FIN-009, REQ-FIN-012]
**DBF-FIN-108** — FIN_RULE_LINE.created_at [ENT-FIN-010, REQ-FIN-008]
**DBF-FIN-109** — FIN_RECURRING_TEMPLATE.recurring_template_pk [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-110** — FIN_RECURRING_TEMPLATE.name_ar [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-111** — FIN_RECURRING_TEMPLATE.name_en [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-112** — FIN_RECURRING_TEMPLATE.schedule_type_code [ENT-FIN-011, REQ-FIN-022, REQ-FIN-024]
**DBF-FIN-113** — FIN_RECURRING_TEMPLATE.frequency_code [ENT-FIN-011, REQ-FIN-023]
**DBF-FIN-114** — FIN_RECURRING_TEMPLATE.start_date [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-115** — FIN_RECURRING_TEMPLATE.next_run_date [ENT-FIN-011, REQ-FIN-023]
**DBF-FIN-116** — FIN_RECURRING_TEMPLATE.end_date [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-117** — FIN_RECURRING_TEMPLATE.is_active_fl [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-118** — FIN_RECURRING_TEMPLATE.created_by [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-119** — FIN_RECURRING_TEMPLATE.created_at [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-120** — FIN_RECURRING_TEMPLATE.updated_by [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-121** — FIN_RECURRING_TEMPLATE.updated_at [ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-122** — FIN_RECURRING_TEMPLATE_LINE.recurring_template_line_pk [ENT-FIN-012, REQ-FIN-022]
**DBF-FIN-123** — FIN_RECURRING_TEMPLATE_LINE.recurring_template_id [ENT-FIN-012, ENT-FIN-011, REQ-FIN-022]
**DBF-FIN-124** — FIN_RECURRING_TEMPLATE_LINE.line_no [ENT-FIN-012, REQ-FIN-022]
**DBF-FIN-125** — FIN_RECURRING_TEMPLATE_LINE.account_id [ENT-FIN-012, ENT-FIN-001, REQ-FIN-022]
**DBF-FIN-126** — FIN_RECURRING_TEMPLATE_LINE.amount [ENT-FIN-012, REQ-FIN-022]
**DBF-FIN-127** — FIN_RECURRING_TEMPLATE_LINE.direction_code [ENT-FIN-012, REQ-FIN-022]
**DBF-FIN-128** — FIN_RECURRING_TEMPLATE_LINE.dimension_value_id [ENT-FIN-012, ENT-FIN-003, REQ-FIN-022]
**DBF-FIN-129** — FIN_RECURRING_TEMPLATE_LINE.created_at [ENT-FIN-012, REQ-FIN-022]
**DBF-FIN-130** — FIN_ALLOCATION_RULE.allocation_rule_pk [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-131** — FIN_ALLOCATION_RULE.name_ar [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-132** — FIN_ALLOCATION_RULE.name_en [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-133** — FIN_ALLOCATION_RULE.source_account_id [ENT-FIN-013, ENT-FIN-001, REQ-FIN-025, REQ-FIN-026]
**DBF-FIN-134** — FIN_ALLOCATION_RULE.is_active_fl [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-135** — FIN_ALLOCATION_RULE.created_by [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-136** — FIN_ALLOCATION_RULE.created_at [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-137** — FIN_ALLOCATION_RULE.updated_by [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-138** — FIN_ALLOCATION_RULE.updated_at [ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-139** — FIN_ALLOCATION_TARGET.allocation_target_pk [ENT-FIN-014, REQ-FIN-025]
**DBF-FIN-140** — FIN_ALLOCATION_TARGET.allocation_rule_id [ENT-FIN-014, ENT-FIN-013, REQ-FIN-025]
**DBF-FIN-141** — FIN_ALLOCATION_TARGET.line_no [ENT-FIN-014, REQ-FIN-025]
**DBF-FIN-142** — FIN_ALLOCATION_TARGET.target_account_id [ENT-FIN-014, ENT-FIN-001, REQ-FIN-025]
**DBF-FIN-143** — FIN_ALLOCATION_TARGET.dimension_value_id [ENT-FIN-014, ENT-FIN-003, REQ-FIN-025]
**DBF-FIN-144** — FIN_ALLOCATION_TARGET.distribution_type_code [ENT-FIN-014, REQ-FIN-009, REQ-FIN-026]
**DBF-FIN-145** — FIN_ALLOCATION_TARGET.distribution_value [ENT-FIN-014, REQ-FIN-026]
**DBF-FIN-146** — FIN_ALLOCATION_TARGET.is_remainder_fl [ENT-FIN-014, REQ-FIN-009, REQ-FIN-026]

## 7. XM id definitions
**XM-FIN-001** — SOFT-READ every FIN lookup-backed column → MDL_LOOKUP_VALUE [REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031]
**XM-FIN-002** — READ SEC's user→permission directory (`SecUserDirectoryApi.findUserIdsHoldingPermission`) for the RULE-FIN-015 separation-of-duties fact [REQ-FIN-037, REQ-FIN-038]
══════════════════════════════════════════════════════════════════
