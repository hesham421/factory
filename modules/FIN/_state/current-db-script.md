<!-- P2 stage output — governed by factory.yaml stages[P2]; see shared/GOVERNANCE-CORE.md -->
# DATABASE — Finance / المحاسبة والمالية (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Dialect : postgresql16
Schema prefix : none (bare identifiers)
Identifier transformation : SRS camelCase field name → snake_case column name
  (e.g. `accountPk` → `account_pk`); table name = `fin_` + entity abbreviation
  (lower snake_case); one deterministic transformation, applied everywhere,
  never two spellings of one field.
Date : 2026-09-10
Counts : 24 tables · 190 DBF · 0 XM (FIN is fully isolated — SRS A8)
══════════════════════════════════════════════════════════════════

## 1 — DB FIELD TRACEABILITY MATRIX

Assignment rules applied: sequence continuous across the module (not per
table); per table, PK first, then the entity's own columns in SRS order, then
FK columns, then standard/audit columns last. Every column traces to an
ENT.field of `srs-fin.md` and to ≥ 1 REQ. No column lacks an SRS origin
(NO-COLUMN-INVENTION).

### Table `fin_account` — ENT-FIN-001 (شجرة الحسابات / Chart of Account)

DBF-FIN-001 — fin_account.account_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-001.accountPk, REQ-FIN-001

DBF-FIN-002 — fin_account.parent_account_id : BIGINT : NULL (FK→fin_account.account_pk)
  Traces: ENT-FIN-001.parentAccountId, REQ-FIN-001

DBF-FIN-003 — fin_account.code : VARCHAR(40) : NOT NULL, UNIQUE
  Traces: ENT-FIN-001.code, REQ-FIN-001

DBF-FIN-004 — fin_account.name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-001.nameAr, REQ-FIN-001

DBF-FIN-005 — fin_account.name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-001.nameEn, REQ-FIN-001

DBF-FIN-006 — fin_account.account_type : VARCHAR(30) : NOT NULL (lookup code, key=account-types, §4.2 — stored as code, not FK)
  Traces: ENT-FIN-001.accountType, REQ-FIN-003

DBF-FIN-007 — fin_account.nature_code : VARCHAR(10) : NOT NULL, CHECK IN (DEBIT,CREDIT)
  Traces: ENT-FIN-001.natureCode, REQ-FIN-003

DBF-FIN-008 — fin_account.accepts_direct_posting_fl : BOOLEAN : NOT NULL, DEFAULT FALSE
  Traces: ENT-FIN-001.acceptsDirectPostingFl, REQ-FIN-002

DBF-FIN-009 — fin_account.is_retained_earnings_account_fl : BOOLEAN : NOT NULL, DEFAULT FALSE
  Traces: ENT-FIN-001.isRetainedEarningsAccountFl, REQ-FIN-031

DBF-FIN-010 — fin_account.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE (profile: entity_defaults.master)
  Traces: ENT-FIN-001.isActiveFl, REQ-FIN-003

DBF-FIN-011 — fin_account.created_by : VARCHAR(100) : NOT NULL (profile: entity_defaults.master)
  Traces: ENT-FIN-001.createdBy, REQ-FIN-003

DBF-FIN-012 — fin_account.created_at : TIMESTAMPTZ : NOT NULL (profile: entity_defaults.master)
  Traces: ENT-FIN-001.createdAt, REQ-FIN-003

DBF-FIN-013 — fin_account.updated_by : VARCHAR(100) : NOT NULL (profile: entity_defaults.master)
  Traces: ENT-FIN-001.updatedBy, REQ-FIN-003

DBF-FIN-014 — fin_account.updated_at : TIMESTAMPTZ : NOT NULL (profile: entity_defaults.master)
  Traces: ENT-FIN-001.updatedAt, REQ-FIN-003

### Table `fin_dimension` — ENT-FIN-002 (بُعد الحساب — definition)

DBF-FIN-015 — fin_dimension.dimension_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-002.dimensionKey, REQ-FIN-004

DBF-FIN-016 — fin_dimension.dimension_key : VARCHAR(40) : NOT NULL, UNIQUE
  Traces: ENT-FIN-002.dimensionKey, REQ-FIN-004

DBF-FIN-017 — fin_dimension.name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-002.nameAr, REQ-FIN-004

DBF-FIN-018 — fin_dimension.name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-002.nameEn, REQ-FIN-004

DBF-FIN-019 — fin_dimension.control_type : VARCHAR(20) : NOT NULL, CHECK IN (FIXED_LIST,REFERENCE_ENTITY)
  Traces: ENT-FIN-002.controlType, REQ-FIN-004

DBF-FIN-020 — fin_dimension.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-002.isActiveFl, REQ-FIN-004

### Table `fin_dimension_value` — ENT-FIN-002 (بُعد الحساب — values)

DBF-FIN-021 — fin_dimension_value.dimension_value_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-002.valueCode, REQ-FIN-004

DBF-FIN-022 — fin_dimension_value.dimension_id : BIGINT : NOT NULL (FK→fin_dimension.dimension_pk)
  Traces: ENT-FIN-002.dimensionKey, REQ-FIN-005

DBF-FIN-023 — fin_dimension_value.value_code : VARCHAR(40) : NOT NULL, UNIQUE(dimension_id, value_code)
  Traces: ENT-FIN-002.valueCode, REQ-FIN-004

DBF-FIN-024 — fin_dimension_value.value_name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-002.valueNameAr, REQ-FIN-004

DBF-FIN-025 — fin_dimension_value.value_name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-002.valueNameEn, REQ-FIN-004

DBF-FIN-026 — fin_dimension_value.sort_order : INTEGER : NULL
  Traces: ENT-FIN-002.sortOrder, REQ-FIN-004

DBF-FIN-027 — fin_dimension_value.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-002.isActiveFl, REQ-FIN-005

### Table `fin_lookup_type` — ENT-FIN-003 (البيانات المرجعية المحاسبية — type)

DBF-FIN-028 — fin_lookup_type.lookup_type_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-003.lookupKey, REQ-FIN-006

DBF-FIN-029 — fin_lookup_type.lookup_key : VARCHAR(40) : NOT NULL, UNIQUE
  Traces: ENT-FIN-003.lookupKey, REQ-FIN-006

DBF-FIN-030 — fin_lookup_type.name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-003.nameAr, REQ-FIN-006

DBF-FIN-031 — fin_lookup_type.name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-003.nameEn, REQ-FIN-006

DBF-FIN-032 — fin_lookup_type.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-003.isActiveFl, REQ-FIN-006

### Table `fin_lookup_value` — ENT-FIN-003 (البيانات المرجعية المحاسبية — values)

DBF-FIN-033 — fin_lookup_value.lookup_value_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-003.valueCode, REQ-FIN-006

DBF-FIN-034 — fin_lookup_value.lookup_type_id : BIGINT : NOT NULL (FK→fin_lookup_type.lookup_type_pk)
  Traces: ENT-FIN-003.lookupKey, REQ-FIN-007

DBF-FIN-035 — fin_lookup_value.value_code : VARCHAR(40) : NOT NULL, UNIQUE(lookup_type_id, value_code)
  Traces: ENT-FIN-003.valueCode, REQ-FIN-006

DBF-FIN-036 — fin_lookup_value.label_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-003.labelAr, REQ-FIN-006

DBF-FIN-037 — fin_lookup_value.label_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-003.labelEn, REQ-FIN-006

DBF-FIN-038 — fin_lookup_value.sort_order : INTEGER : NULL
  Traces: ENT-FIN-003.sortOrder, REQ-FIN-006

DBF-FIN-039 — fin_lookup_value.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-003.isActiveFl, REQ-FIN-007

### Table `fin_event_rule` — ENT-FIN-004 (قاعدة نوع الحدث)

DBF-FIN-040 — fin_event_rule.event_rule_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-004.eventTypeCode, REQ-FIN-008

DBF-FIN-041 — fin_event_rule.event_type_code : VARCHAR(40) : NOT NULL, UNIQUE (lookup code, key=accounting-event-types, §4.2)
  Traces: ENT-FIN-004.eventTypeCode, REQ-FIN-008

DBF-FIN-042 — fin_event_rule.name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-004.nameAr, REQ-FIN-008

DBF-FIN-043 — fin_event_rule.name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-004.nameEn, REQ-FIN-008

DBF-FIN-044 — fin_event_rule.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-004.isActiveFl, REQ-FIN-008

DBF-FIN-045 — fin_event_rule.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-004.createdBy, REQ-FIN-008

DBF-FIN-046 — fin_event_rule.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-004.createdAt, REQ-FIN-008

DBF-FIN-047 — fin_event_rule.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-004.updatedBy, REQ-FIN-008

DBF-FIN-048 — fin_event_rule.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-004.updatedAt, REQ-FIN-008

### Table `fin_rule_line` — ENT-FIN-005 (سطر القاعدة)

DBF-FIN-049 — fin_rule_line.rule_line_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-005.lineNo, REQ-FIN-009

DBF-FIN-050 — fin_rule_line.event_rule_id : BIGINT : NOT NULL (FK→fin_event_rule.event_rule_pk)
  Traces: ENT-FIN-005.eventTypeRuleId, REQ-FIN-008

DBF-FIN-051 — fin_rule_line.line_no : INTEGER : NOT NULL
  Traces: ENT-FIN-005.lineNo, REQ-FIN-009

DBF-FIN-052 — fin_rule_line.account_derivation_type : VARCHAR(20) : NOT NULL, CHECK IN (CONSTANT,EVENT_FIELD,MAPPING_SET)
  Traces: ENT-FIN-005.accountDerivationType, REQ-FIN-010

DBF-FIN-053 — fin_rule_line.constant_account_id : BIGINT : NULL (FK→fin_account.account_pk)
  Traces: ENT-FIN-005.constantAccountId, REQ-FIN-010

DBF-FIN-054 — fin_rule_line.event_field_name : VARCHAR(100) : NULL
  Traces: ENT-FIN-005.eventFieldName, REQ-FIN-010

DBF-FIN-055 — fin_rule_line.amount_source_field : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-005.amountSourceField, REQ-FIN-011

DBF-FIN-056 — fin_rule_line.amount_source_operation : VARCHAR(20) : NOT NULL, CHECK IN (DIRECT,PERCENTAGE,REMAINDER)
  Traces: ENT-FIN-005.amountSourceOperation, REQ-FIN-011

DBF-FIN-057 — fin_rule_line.amount_operation_value : NUMERIC(9,4) : NULL (DEFAULT precision — percentage value; domain best practice, KB §6 covers money only)
  Traces: ENT-FIN-005.amountOperationValue, REQ-FIN-011

DBF-FIN-058 — fin_rule_line.direction_code : VARCHAR(10) : NOT NULL, CHECK IN (DEBIT,CREDIT)
  Traces: ENT-FIN-005.directionCode, REQ-FIN-009

DBF-FIN-059 — fin_rule_line.distribution_type : VARCHAR(20) : NOT NULL, CHECK IN (FIXED,PERCENTAGE,REMAINDER)
  Traces: ENT-FIN-005.distributionType, REQ-FIN-012

DBF-FIN-060 — fin_rule_line.distribution_value : NUMERIC(18,4) : NULL (KB §6 money precision)
  Traces: ENT-FIN-005.distributionValue, REQ-FIN-012

DBF-FIN-061 — fin_rule_line.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-005.isActiveFl, REQ-FIN-009

### Table `fin_rule_line_mapping` — ENT-FIN-005 (ADR-FIN-002 — mapping entries)

DBF-FIN-062 — fin_rule_line_mapping.rule_line_mapping_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-005.mappingEntries, REQ-FIN-010

DBF-FIN-063 — fin_rule_line_mapping.rule_line_id : BIGINT : NOT NULL (FK→fin_rule_line.rule_line_pk)
  Traces: ENT-FIN-005.mappingEntries, REQ-FIN-010

DBF-FIN-064 — fin_rule_line_mapping.event_attribute_name : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-005.mappingEntries.eventAttributeName, REQ-FIN-010

DBF-FIN-065 — fin_rule_line_mapping.event_attribute_value : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-005.mappingEntries.eventAttributeValue, REQ-FIN-010

DBF-FIN-066 — fin_rule_line_mapping.resulting_dimension_value_id : BIGINT : NOT NULL (FK→fin_dimension_value.dimension_value_pk)
  Traces: ENT-FIN-005.mappingEntries.resultingDimensionValue, REQ-FIN-010

### Table `fin_journal_entry` — ENT-FIN-006 (القيد المحاسبي)

DBF-FIN-067 — fin_journal_entry.journal_entry_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-006.entryNo, REQ-FIN-018

DBF-FIN-068 — fin_journal_entry.entry_no : VARCHAR(30) : NOT NULL, UNIQUE (NUMBERING rule — platform numbering engine, system-generated, read-only after)
  Traces: ENT-FIN-006.entryNo, REQ-FIN-018

DBF-FIN-069 — fin_journal_entry.entry_date : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-006.entryDate, REQ-FIN-018

DBF-FIN-070 — fin_journal_entry.source_type_code : VARCHAR(20) : NOT NULL (lookup code, key=journal-types, §4.2)
  Traces: ENT-FIN-006.sourceTypeCode, REQ-FIN-014

DBF-FIN-071 — fin_journal_entry.status_code : VARCHAR(10) : NOT NULL, CHECK IN (DRAFT,POSTED)
  Traces: ENT-FIN-006.statusCode, REQ-FIN-018

DBF-FIN-072 — fin_journal_entry.fiscal_year_id : BIGINT : NOT NULL (FK→fin_fiscal_year.fiscal_year_pk)
  Traces: ENT-FIN-006.fiscalYearId, REQ-FIN-027

DBF-FIN-073 — fin_journal_entry.period_id : BIGINT : NOT NULL (FK→fin_fiscal_period.fiscal_period_pk)
  Traces: ENT-FIN-006.periodId, REQ-FIN-028

DBF-FIN-074 — fin_journal_entry.source_event_reference : VARCHAR(100) : NULL
  Traces: ENT-FIN-006.sourceEventReference, REQ-FIN-034

DBF-FIN-075 — fin_journal_entry.template_id : BIGINT : NULL (FK→fin_recurring_template.recurring_template_pk)
  Traces: ENT-FIN-006.templateId, REQ-FIN-016

DBF-FIN-076 — fin_journal_entry.allocation_rule_id : BIGINT : NULL (FK→fin_allocation_rule.allocation_rule_pk)
  Traces: ENT-FIN-006.allocationRuleId, REQ-FIN-017

DBF-FIN-077 — fin_journal_entry.reversal_of_entry_id : BIGINT : NULL (FK→fin_journal_entry.journal_entry_pk)
  Traces: ENT-FIN-006.reversalOfEntryId, REQ-FIN-023

DBF-FIN-078 — fin_journal_entry.reversed_by_entry_id : BIGINT : NULL (FK→fin_journal_entry.journal_entry_pk)
  Traces: ENT-FIN-006.reversedByEntryId, REQ-FIN-023

DBF-FIN-079 — fin_journal_entry.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-006.createdBy, REQ-FIN-018

DBF-FIN-080 — fin_journal_entry.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-006.createdAt, REQ-FIN-018

DBF-FIN-081 — fin_journal_entry.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-006.updatedBy, REQ-FIN-018

DBF-FIN-082 — fin_journal_entry.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-006.updatedAt, REQ-FIN-018

### Table `fin_journal_entry_line` — ENT-FIN-007 (سطر القيد)

DBF-FIN-083 — fin_journal_entry_line.journal_entry_line_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-007.lineNo, REQ-FIN-005

DBF-FIN-084 — fin_journal_entry_line.journal_entry_id : BIGINT : NOT NULL (FK→fin_journal_entry.journal_entry_pk)
  Traces: ENT-FIN-007.journalEntryId, REQ-FIN-018

DBF-FIN-085 — fin_journal_entry_line.line_no : INTEGER : NOT NULL
  Traces: ENT-FIN-007.lineNo, REQ-FIN-005

DBF-FIN-086 — fin_journal_entry_line.account_id : BIGINT : NOT NULL (FK→fin_account.account_pk)
  Traces: ENT-FIN-007.accountId, REQ-FIN-002

DBF-FIN-087 — fin_journal_entry_line.direction_code : VARCHAR(10) : NOT NULL, CHECK IN (DEBIT,CREDIT)
  Traces: ENT-FIN-007.directionCode, REQ-FIN-018

DBF-FIN-088 — fin_journal_entry_line.amount : NUMERIC(18,4) : NOT NULL, CHECK (amount > 0) (KB §6 money precision)
  Traces: ENT-FIN-007.amount, REQ-FIN-019

DBF-FIN-089 — fin_journal_entry_line.description_ar : VARCHAR(500) : NULL
  Traces: ENT-FIN-007.descriptionAr, REQ-FIN-005

DBF-FIN-090 — fin_journal_entry_line.description_en : VARCHAR(500) : NULL
  Traces: ENT-FIN-007.descriptionEn, REQ-FIN-005

### Table `fin_journal_entry_line_dim` — ENT-FIN-007 (dimension segments, junction)

DBF-FIN-091 — fin_journal_entry_line_dim.journal_entry_line_dim_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-007.dimensionValues, REQ-FIN-005

DBF-FIN-092 — fin_journal_entry_line_dim.journal_entry_line_id : BIGINT : NOT NULL (FK→fin_journal_entry_line.journal_entry_line_pk)
  Traces: ENT-FIN-007.dimensionValues, REQ-FIN-005

DBF-FIN-093 — fin_journal_entry_line_dim.dimension_value_id : BIGINT : NOT NULL (FK→fin_dimension_value.dimension_value_pk), UNIQUE(journal_entry_line_id, dimension_value_id)
  Traces: ENT-FIN-007.dimensionValues, REQ-FIN-005

### Table `fin_recurring_template` — ENT-FIN-008 (قالب القيد المتكرر / العكسي)

DBF-FIN-094 — fin_recurring_template.recurring_template_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-008.templateNameAr, REQ-FIN-016

DBF-FIN-095 — fin_recurring_template.template_name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-008.templateNameAr, REQ-FIN-016

DBF-FIN-096 — fin_recurring_template.template_name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-008.templateNameEn, REQ-FIN-016

DBF-FIN-097 — fin_recurring_template.template_type_code : VARCHAR(20) : NOT NULL, CHECK IN (RECURRING,REVERSING)
  Traces: ENT-FIN-008.templateTypeCode, REQ-FIN-016

DBF-FIN-098 — fin_recurring_template.schedule_rule : TEXT : NOT NULL (ADR-FIN-001 — data-defined recurrence definition)
  Traces: ENT-FIN-008.scheduleRule, REQ-FIN-016

DBF-FIN-099 — fin_recurring_template.next_run_date : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-008.nextRunDate, REQ-FIN-016

DBF-FIN-100 — fin_recurring_template.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-008.isActiveFl, REQ-FIN-016

DBF-FIN-101 — fin_recurring_template.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-008.createdBy, REQ-FIN-016

DBF-FIN-102 — fin_recurring_template.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-008.createdAt, REQ-FIN-016

DBF-FIN-103 — fin_recurring_template.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-008.updatedBy, REQ-FIN-016

DBF-FIN-104 — fin_recurring_template.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-008.updatedAt, REQ-FIN-016

### Table `fin_recurring_template_line` — ENT-FIN-008 (templateLines)

DBF-FIN-105 — fin_recurring_template_line.recurring_template_line_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-008.templateLines, REQ-FIN-016

DBF-FIN-106 — fin_recurring_template_line.recurring_template_id : BIGINT : NOT NULL (FK→fin_recurring_template.recurring_template_pk)
  Traces: ENT-FIN-008.templateLines, REQ-FIN-016

DBF-FIN-107 — fin_recurring_template_line.line_no : INTEGER : NOT NULL
  Traces: ENT-FIN-008.templateLines, REQ-FIN-016

DBF-FIN-108 — fin_recurring_template_line.account_id : BIGINT : NOT NULL (FK→fin_account.account_pk)
  Traces: ENT-FIN-008.templateLines.accountId, REQ-FIN-016

DBF-FIN-109 — fin_recurring_template_line.amount_source_value : NUMERIC(18,4) : NULL (KB §6 money precision — fixed-amount case)
  Traces: ENT-FIN-008.templateLines.amountSource, REQ-FIN-016

DBF-FIN-110 — fin_recurring_template_line.amount_source_formula : VARCHAR(200) : NULL (formula-reference case, RULE-FIN-013)
  Traces: ENT-FIN-008.templateLines.amountSource, REQ-FIN-016

DBF-FIN-111 — fin_recurring_template_line.direction_code : VARCHAR(10) : NOT NULL, CHECK IN (DEBIT,CREDIT)
  Traces: ENT-FIN-008.templateLines.directionCode, REQ-FIN-016

### Table `fin_recurring_template_line_dim` — ENT-FIN-008 (junction)

DBF-FIN-112 — fin_recurring_template_line_dim.recurring_template_line_dim_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-008.templateLines.dimensionValues, REQ-FIN-016

DBF-FIN-113 — fin_recurring_template_line_dim.recurring_template_line_id : BIGINT : NOT NULL (FK→fin_recurring_template_line.recurring_template_line_pk)
  Traces: ENT-FIN-008.templateLines.dimensionValues, REQ-FIN-016

DBF-FIN-114 — fin_recurring_template_line_dim.dimension_value_id : BIGINT : NOT NULL (FK→fin_dimension_value.dimension_value_pk), UNIQUE(recurring_template_line_id, dimension_value_id)
  Traces: ENT-FIN-008.templateLines.dimensionValues, REQ-FIN-016

### Table `fin_allocation_rule` — ENT-FIN-009 (قاعدة التوزيع)

DBF-FIN-115 — fin_allocation_rule.allocation_rule_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-009.ruleNameAr, REQ-FIN-017

DBF-FIN-116 — fin_allocation_rule.rule_name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-009.ruleNameAr, REQ-FIN-017

DBF-FIN-117 — fin_allocation_rule.rule_name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-009.ruleNameEn, REQ-FIN-017

DBF-FIN-118 — fin_allocation_rule.source_account_id : BIGINT : NOT NULL (FK→fin_account.account_pk)
  Traces: ENT-FIN-009.sourceAccountId, REQ-FIN-017

DBF-FIN-119 — fin_allocation_rule.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-009.isActiveFl, REQ-FIN-017

DBF-FIN-120 — fin_allocation_rule.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-009.createdBy, REQ-FIN-017

DBF-FIN-121 — fin_allocation_rule.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-009.createdAt, REQ-FIN-017

DBF-FIN-122 — fin_allocation_rule.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-009.updatedBy, REQ-FIN-017

DBF-FIN-123 — fin_allocation_rule.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-009.updatedAt, REQ-FIN-017

### Table `fin_allocation_rule_dim` — ENT-FIN-009 (sourceDimensionValues, junction)

DBF-FIN-124 — fin_allocation_rule_dim.allocation_rule_dim_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-009.sourceDimensionValues, REQ-FIN-017

DBF-FIN-125 — fin_allocation_rule_dim.allocation_rule_id : BIGINT : NOT NULL (FK→fin_allocation_rule.allocation_rule_pk)
  Traces: ENT-FIN-009.sourceDimensionValues, REQ-FIN-017

DBF-FIN-126 — fin_allocation_rule_dim.dimension_value_id : BIGINT : NOT NULL (FK→fin_dimension_value.dimension_value_pk), UNIQUE(allocation_rule_id, dimension_value_id)
  Traces: ENT-FIN-009.sourceDimensionValues, REQ-FIN-017

### Table `fin_allocation_rule_line` — ENT-FIN-009 (allocationLines)

DBF-FIN-127 — fin_allocation_rule_line.allocation_rule_line_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-009.allocationLines, REQ-FIN-017

DBF-FIN-128 — fin_allocation_rule_line.allocation_rule_id : BIGINT : NOT NULL (FK→fin_allocation_rule.allocation_rule_pk)
  Traces: ENT-FIN-009.allocationLines, REQ-FIN-017

DBF-FIN-129 — fin_allocation_rule_line.line_no : INTEGER : NOT NULL
  Traces: ENT-FIN-009.allocationLines, REQ-FIN-017

DBF-FIN-130 — fin_allocation_rule_line.target_account_id : BIGINT : NOT NULL (FK→fin_account.account_pk)
  Traces: ENT-FIN-009.allocationLines.targetAccountId, REQ-FIN-017

DBF-FIN-131 — fin_allocation_rule_line.distribution_type : VARCHAR(20) : NOT NULL, CHECK IN (FIXED,PERCENTAGE,REMAINDER)
  Traces: ENT-FIN-009.allocationLines.distributionType, REQ-FIN-017

DBF-FIN-132 — fin_allocation_rule_line.distribution_value : NUMERIC(18,4) : NULL (KB §6 money precision)
  Traces: ENT-FIN-009.allocationLines.distributionValue, REQ-FIN-017

### Table `fin_allocation_rule_line_dim` — ENT-FIN-009 (targetDimensionValues, junction)

DBF-FIN-133 — fin_allocation_rule_line_dim.allocation_rule_line_dim_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-009.allocationLines.targetDimensionValues, REQ-FIN-017

DBF-FIN-134 — fin_allocation_rule_line_dim.allocation_rule_line_id : BIGINT : NOT NULL (FK→fin_allocation_rule_line.allocation_rule_line_pk)
  Traces: ENT-FIN-009.allocationLines.targetDimensionValues, REQ-FIN-017

DBF-FIN-135 — fin_allocation_rule_line_dim.dimension_value_id : BIGINT : NOT NULL (FK→fin_dimension_value.dimension_value_pk), UNIQUE(allocation_rule_line_id, dimension_value_id)
  Traces: ENT-FIN-009.allocationLines.targetDimensionValues, REQ-FIN-017

### Table `fin_fiscal_year` — ENT-FIN-010 (السنة المالية)

DBF-FIN-136 — fin_fiscal_year.fiscal_year_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-010.yearCode, REQ-FIN-027

DBF-FIN-137 — fin_fiscal_year.year_code : VARCHAR(10) : NOT NULL, UNIQUE
  Traces: ENT-FIN-010.yearCode, REQ-FIN-027

DBF-FIN-138 — fin_fiscal_year.name_ar : VARCHAR(200) : NULL
  Traces: ENT-FIN-010.nameAr, REQ-FIN-027

DBF-FIN-139 — fin_fiscal_year.name_en : VARCHAR(200) : NULL
  Traces: ENT-FIN-010.nameEn, REQ-FIN-027

DBF-FIN-140 — fin_fiscal_year.start_date : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-010.startDate, REQ-FIN-027

DBF-FIN-141 — fin_fiscal_year.end_date : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-010.endDate, REQ-FIN-027

DBF-FIN-142 — fin_fiscal_year.status_code : VARCHAR(20) : NOT NULL, CHECK IN (OPEN,YEAR_END_CLOSED)
  Traces: ENT-FIN-010.statusCode, REQ-FIN-027

DBF-FIN-143 — fin_fiscal_year.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-010.isActiveFl, REQ-FIN-027

DBF-FIN-144 — fin_fiscal_year.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-010.createdBy, REQ-FIN-027

DBF-FIN-145 — fin_fiscal_year.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-010.createdAt, REQ-FIN-027

DBF-FIN-146 — fin_fiscal_year.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-010.updatedBy, REQ-FIN-027

DBF-FIN-147 — fin_fiscal_year.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-010.updatedAt, REQ-FIN-027

### Table `fin_fiscal_period` — ENT-FIN-011 (الفترة المالية)

DBF-FIN-148 — fin_fiscal_period.fiscal_period_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-011.periodCode, REQ-FIN-027

DBF-FIN-149 — fin_fiscal_period.fiscal_year_id : BIGINT : NOT NULL (FK→fin_fiscal_year.fiscal_year_pk)
  Traces: ENT-FIN-011.fiscalYearId, REQ-FIN-027

DBF-FIN-150 — fin_fiscal_period.period_code : VARCHAR(10) : NOT NULL, UNIQUE(fiscal_year_id, period_code)
  Traces: ENT-FIN-011.periodCode, REQ-FIN-027

DBF-FIN-151 — fin_fiscal_period.name_ar : VARCHAR(200) : NULL
  Traces: ENT-FIN-011.nameAr, REQ-FIN-027

DBF-FIN-152 — fin_fiscal_period.name_en : VARCHAR(200) : NULL
  Traces: ENT-FIN-011.nameEn, REQ-FIN-027

DBF-FIN-153 — fin_fiscal_period.sequence_no : INTEGER : NOT NULL
  Traces: ENT-FIN-011.sequenceNo, REQ-FIN-027

DBF-FIN-154 — fin_fiscal_period.start_date : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-011.startDate, REQ-FIN-027

DBF-FIN-155 — fin_fiscal_period.end_date : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-011.endDate, REQ-FIN-027

DBF-FIN-156 — fin_fiscal_period.status_code : VARCHAR(20) : NOT NULL, CHECK IN (OPEN,SOFT_CLOSE,HARD_CLOSE)
  Traces: ENT-FIN-011.statusCode, REQ-FIN-028

DBF-FIN-157 — fin_fiscal_period.close_approved_by : BIGINT : NULL (FK→fin_user.user_pk)
  Traces: ENT-FIN-011.closeApprovedBy, REQ-FIN-021

DBF-FIN-158 — fin_fiscal_period.close_approved_at : TIMESTAMPTZ : NULL
  Traces: ENT-FIN-011.closeApprovedAt, REQ-FIN-021

DBF-FIN-159 — fin_fiscal_period.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-011.isActiveFl, REQ-FIN-027

DBF-FIN-160 — fin_fiscal_period.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-011.createdBy, REQ-FIN-027

DBF-FIN-161 — fin_fiscal_period.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-011.createdAt, REQ-FIN-027

DBF-FIN-162 — fin_fiscal_period.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-011.updatedBy, REQ-FIN-027

DBF-FIN-163 — fin_fiscal_period.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-011.updatedAt, REQ-FIN-027

### Table `fin_user` — ENT-FIN-012 (مستخدم المحاسبة)

DBF-FIN-164 — fin_user.user_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-012.username, REQ-FIN-025

DBF-FIN-165 — fin_user.username : VARCHAR(60) : NOT NULL, UNIQUE
  Traces: ENT-FIN-012.username, REQ-FIN-025

DBF-FIN-166 — fin_user.name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-012.nameAr, REQ-FIN-025

DBF-FIN-167 — fin_user.name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-012.nameEn, REQ-FIN-025

DBF-FIN-168 — fin_user.password_hash : VARCHAR(255) : NOT NULL
  Traces: ENT-FIN-012.passwordHash, REQ-FIN-025

DBF-FIN-169 — fin_user.last_login_at : TIMESTAMPTZ : NULL
  Traces: ENT-FIN-012.lastLoginAt, REQ-FIN-025

DBF-FIN-170 — fin_user.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-012.isActiveFl, REQ-FIN-025

DBF-FIN-171 — fin_user.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-012.createdBy, REQ-FIN-025

DBF-FIN-172 — fin_user.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-012.createdAt, REQ-FIN-025

DBF-FIN-173 — fin_user.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-012.updatedBy, REQ-FIN-025

DBF-FIN-174 — fin_user.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-012.updatedAt, REQ-FIN-025

### Table `fin_role` — ENT-FIN-013 (الدور والصلاحية — role)

DBF-FIN-175 — fin_role.role_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-013.roleCode, REQ-FIN-025

DBF-FIN-176 — fin_role.role_code : VARCHAR(40) : NOT NULL, UNIQUE
  Traces: ENT-FIN-013.roleCode, REQ-FIN-025

DBF-FIN-177 — fin_role.role_name_ar : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-013.roleNameAr, REQ-FIN-025

DBF-FIN-178 — fin_role.role_name_en : VARCHAR(200) : NOT NULL
  Traces: ENT-FIN-013.roleNameEn, REQ-FIN-025

DBF-FIN-179 — fin_role.is_active_fl : BOOLEAN : NOT NULL, DEFAULT TRUE
  Traces: ENT-FIN-013.isActiveFl, REQ-FIN-025

DBF-FIN-180 — fin_role.created_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-013.createdBy, REQ-FIN-025

DBF-FIN-181 — fin_role.created_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-013.createdAt, REQ-FIN-025

DBF-FIN-182 — fin_role.updated_by : VARCHAR(100) : NOT NULL
  Traces: ENT-FIN-013.updatedBy, REQ-FIN-025

DBF-FIN-183 — fin_role.updated_at : TIMESTAMPTZ : NOT NULL
  Traces: ENT-FIN-013.updatedAt, REQ-FIN-025

### Table `fin_role_permission` — ENT-FIN-013 (permissionAssignments)

DBF-FIN-184 — fin_role_permission.role_permission_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-013.permissionAssignments, REQ-FIN-026

DBF-FIN-185 — fin_role_permission.role_id : BIGINT : NOT NULL (FK→fin_role.role_pk)
  Traces: ENT-FIN-013.permissionAssignments, REQ-FIN-026

DBF-FIN-186 — fin_role_permission.page_code : VARCHAR(40) : NOT NULL, UNIQUE(role_id, page_code, action_code) (SEC_PAGES row per SRS §7.1 — this module's own copy, POL-FIN-008)
  Traces: ENT-FIN-013.permissionAssignments.pageCode, REQ-FIN-026

DBF-FIN-187 — fin_role_permission.action_code : VARCHAR(10) : NOT NULL, CHECK IN (VIEW,CREATE,UPDATE,DELETE)
  Traces: ENT-FIN-013.permissionAssignments.actionCode, REQ-FIN-026

### Table `fin_user_role` — ENT-FIN-013 (userAssignments, junction)

DBF-FIN-188 — fin_user_role.user_role_pk : GENERATED ALWAYS AS IDENTITY : NOT NULL
  Traces: ENT-FIN-013.userAssignments, REQ-FIN-026

DBF-FIN-189 — fin_user_role.user_id : BIGINT : NOT NULL (FK→fin_user.user_pk)
  Traces: ENT-FIN-013.userAssignments, REQ-FIN-026

DBF-FIN-190 — fin_user_role.role_id : BIGINT : NOT NULL (FK→fin_role.role_pk), UNIQUE(user_id, role_id)
  Traces: ENT-FIN-013.userAssignments, REQ-FIN-026

Total: 190 DBF ids across 24 tables.

## 2 — XM REGISTER

None. FIN consumes no other module's entity and exposes none for consumption —
confirmed total isolation (`DEPENDENCIES: NONE`, `ROOT: YES`, SRS A8,
module-registry-fin.md, prd-approval gate approved 2026-09-10). No HARD-FK,
SOFT-READ or deferred-FK record exists in this script; BLOCK 11 is empty.

## 3 — FULL_DATABASE_SCRIPT (postgresql16 — copy-and-run against a clean schema)

```sql
-- ════════════════════════════════════════════════════════════════════════
-- FIN v1 — General Ledger — postgresql16 — schema prefix: none
-- Identifier transformation: SRS camelCase field -> snake_case column;
-- table = fin_<entity abbreviation>. Generated by P2 (Database) — FIN v1.
-- ════════════════════════════════════════════════════════════════════════

-- BLOCK 1 — SEQUENCES
-- none: every PK uses GENERATED ALWAYS AS IDENTITY (postgresql16 syntax_map.identity)

-- BLOCK 2 — PARENT TABLES (no FK dependencies)

CREATE TABLE fin_fiscal_year (
    fiscal_year_pk      BIGINT GENERATED ALWAYS AS IDENTITY,
    year_code           VARCHAR(10)   NOT NULL,
    name_ar             VARCHAR(200),
    name_en             VARCHAR(200),
    start_date          TIMESTAMPTZ   NOT NULL,
    end_date            TIMESTAMPTZ   NOT NULL,
    status_code         VARCHAR(20)   NOT NULL,
    is_active_fl        BOOLEAN       NOT NULL DEFAULT TRUE,
    created_by          VARCHAR(100)  NOT NULL,
    created_at          TIMESTAMPTZ   NOT NULL,
    updated_by          VARCHAR(100)  NOT NULL,
    updated_at          TIMESTAMPTZ   NOT NULL
);

CREATE TABLE fin_user (
    user_pk              BIGINT GENERATED ALWAYS AS IDENTITY,
    username              VARCHAR(60)   NOT NULL,
    name_ar               VARCHAR(200)  NOT NULL,
    name_en               VARCHAR(200)  NOT NULL,
    password_hash         VARCHAR(255)  NOT NULL,
    last_login_at         TIMESTAMPTZ,
    is_active_fl          BOOLEAN       NOT NULL DEFAULT TRUE,
    created_by            VARCHAR(100)  NOT NULL,
    created_at            TIMESTAMPTZ   NOT NULL,
    updated_by            VARCHAR(100)  NOT NULL,
    updated_at            TIMESTAMPTZ   NOT NULL
);

CREATE TABLE fin_role (
    role_pk              BIGINT GENERATED ALWAYS AS IDENTITY,
    role_code             VARCHAR(40)   NOT NULL,
    role_name_ar          VARCHAR(200)  NOT NULL,
    role_name_en          VARCHAR(200)  NOT NULL,
    is_active_fl          BOOLEAN       NOT NULL DEFAULT TRUE,
    created_by            VARCHAR(100)  NOT NULL,
    created_at            TIMESTAMPTZ   NOT NULL,
    updated_by            VARCHAR(100)  NOT NULL,
    updated_at            TIMESTAMPTZ   NOT NULL
);

CREATE TABLE fin_dimension (
    dimension_pk          BIGINT GENERATED ALWAYS AS IDENTITY,
    dimension_key          VARCHAR(40)   NOT NULL,
    name_ar                VARCHAR(200)  NOT NULL,
    name_en                VARCHAR(200)  NOT NULL,
    control_type           VARCHAR(20)   NOT NULL,
    is_active_fl           BOOLEAN       NOT NULL DEFAULT TRUE
);

CREATE TABLE fin_lookup_type (
    lookup_type_pk         BIGINT GENERATED ALWAYS AS IDENTITY,
    lookup_key              VARCHAR(40)   NOT NULL,
    name_ar                 VARCHAR(200)  NOT NULL,
    name_en                 VARCHAR(200)  NOT NULL,
    is_active_fl             BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE fin_account (
    account_pk              BIGINT GENERATED ALWAYS AS IDENTITY,
    parent_account_id        BIGINT,
    code                      VARCHAR(40)   NOT NULL,
    name_ar                   VARCHAR(200)  NOT NULL,
    name_en                   VARCHAR(200)  NOT NULL,
    account_type              VARCHAR(30)   NOT NULL,
    nature_code                VARCHAR(10)  NOT NULL,
    accepts_direct_posting_fl  BOOLEAN      NOT NULL DEFAULT FALSE,
    is_retained_earnings_account_fl BOOLEAN NOT NULL DEFAULT FALSE,
    is_active_fl                BOOLEAN     NOT NULL DEFAULT TRUE,
    created_by                   VARCHAR(100) NOT NULL,
    created_at                    TIMESTAMPTZ NOT NULL,
    updated_by                     VARCHAR(100) NOT NULL,
    updated_at                      TIMESTAMPTZ NOT NULL
);

-- BLOCK 3 — CHILD TABLES (parents already created; chain A -> B -> C)

CREATE TABLE fin_dimension_value (
    dimension_value_pk    BIGINT GENERATED ALWAYS AS IDENTITY,
    dimension_id            BIGINT        NOT NULL,
    value_code               VARCHAR(40)  NOT NULL,
    value_name_ar             VARCHAR(200) NOT NULL,
    value_name_en              VARCHAR(200) NOT NULL,
    sort_order                  INTEGER,
    is_active_fl                  BOOLEAN  NOT NULL DEFAULT TRUE
);

CREATE TABLE fin_lookup_value (
    lookup_value_pk       BIGINT GENERATED ALWAYS AS IDENTITY,
    lookup_type_id          BIGINT        NOT NULL,
    value_code                VARCHAR(40) NOT NULL,
    label_ar                   VARCHAR(200) NOT NULL,
    label_en                    VARCHAR(200) NOT NULL,
    sort_order                    INTEGER,
    is_active_fl                    BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE fin_event_rule (
    event_rule_pk         BIGINT GENERATED ALWAYS AS IDENTITY,
    event_type_code         VARCHAR(40)   NOT NULL,
    name_ar                  VARCHAR(200) NOT NULL,
    name_en                   VARCHAR(200) NOT NULL,
    is_active_fl                BOOLEAN    NOT NULL DEFAULT TRUE,
    created_by                   VARCHAR(100) NOT NULL,
    created_at                    TIMESTAMPTZ NOT NULL,
    updated_by                     VARCHAR(100) NOT NULL,
    updated_at                      TIMESTAMPTZ NOT NULL
);

CREATE TABLE fin_rule_line (
    rule_line_pk           BIGINT GENERATED ALWAYS AS IDENTITY,
    event_rule_id            BIGINT       NOT NULL,
    line_no                    INTEGER    NOT NULL,
    account_derivation_type      VARCHAR(20) NOT NULL,
    constant_account_id            BIGINT,
    event_field_name                 VARCHAR(100),
    amount_source_field                VARCHAR(100) NOT NULL,
    amount_source_operation              VARCHAR(20)  NOT NULL,
    amount_operation_value                 NUMERIC(9,4),
    direction_code                           VARCHAR(10) NOT NULL,
    distribution_type                          VARCHAR(20) NOT NULL,
    distribution_value                           NUMERIC(18,4),
    is_active_fl                                   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE fin_rule_line_mapping (
    rule_line_mapping_pk   BIGINT GENERATED ALWAYS AS IDENTITY,
    rule_line_id              BIGINT       NOT NULL,
    event_attribute_name        VARCHAR(100) NOT NULL,
    event_attribute_value         VARCHAR(200) NOT NULL,
    resulting_dimension_value_id    BIGINT     NOT NULL
);

CREATE TABLE fin_recurring_template (
    recurring_template_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
    template_name_ar          VARCHAR(200) NOT NULL,
    template_name_en           VARCHAR(200) NOT NULL,
    template_type_code           VARCHAR(20)  NOT NULL,
    schedule_rule                  TEXT       NOT NULL,
    next_run_date                    TIMESTAMPTZ NOT NULL,
    is_active_fl                       BOOLEAN   NOT NULL DEFAULT TRUE,
    created_by                           VARCHAR(100) NOT NULL,
    created_at                             TIMESTAMPTZ NOT NULL,
    updated_by                               VARCHAR(100) NOT NULL,
    updated_at                                 TIMESTAMPTZ NOT NULL
);

CREATE TABLE fin_recurring_template_line (
    recurring_template_line_pk BIGINT GENERATED ALWAYS AS IDENTITY,
    recurring_template_id         BIGINT      NOT NULL,
    line_no                         INTEGER   NOT NULL,
    account_id                        BIGINT  NOT NULL,
    amount_source_value                 NUMERIC(18,4),
    amount_source_formula                 VARCHAR(200),
    direction_code                          VARCHAR(10) NOT NULL
);

CREATE TABLE fin_recurring_template_line_dim (
    recurring_template_line_dim_pk BIGINT GENERATED ALWAYS AS IDENTITY,
    recurring_template_line_id        BIGINT NOT NULL,
    dimension_value_id                  BIGINT NOT NULL
);

CREATE TABLE fin_allocation_rule (
    allocation_rule_pk     BIGINT GENERATED ALWAYS AS IDENTITY,
    rule_name_ar              VARCHAR(200) NOT NULL,
    rule_name_en                VARCHAR(200) NOT NULL,
    source_account_id             BIGINT     NOT NULL,
    is_active_fl                    BOOLEAN  NOT NULL DEFAULT TRUE,
    created_by                        VARCHAR(100) NOT NULL,
    created_at                          TIMESTAMPTZ NOT NULL,
    updated_by                            VARCHAR(100) NOT NULL,
    updated_at                              TIMESTAMPTZ NOT NULL
);

CREATE TABLE fin_allocation_rule_dim (
    allocation_rule_dim_pk BIGINT GENERATED ALWAYS AS IDENTITY,
    allocation_rule_id        BIGINT NOT NULL,
    dimension_value_id          BIGINT NOT NULL
);

CREATE TABLE fin_allocation_rule_line (
    allocation_rule_line_pk BIGINT GENERATED ALWAYS AS IDENTITY,
    allocation_rule_id         BIGINT      NOT NULL,
    line_no                      INTEGER   NOT NULL,
    target_account_id              BIGINT  NOT NULL,
    distribution_type                VARCHAR(20) NOT NULL,
    distribution_value                 NUMERIC(18,4)
);

CREATE TABLE fin_allocation_rule_line_dim (
    allocation_rule_line_dim_pk BIGINT GENERATED ALWAYS AS IDENTITY,
    allocation_rule_line_id        BIGINT NOT NULL,
    dimension_value_id               BIGINT NOT NULL
);

CREATE TABLE fin_fiscal_period (
    fiscal_period_pk        BIGINT GENERATED ALWAYS AS IDENTITY,
    fiscal_year_id             BIGINT       NOT NULL,
    period_code                  VARCHAR(10) NOT NULL,
    name_ar                        VARCHAR(200),
    name_en                          VARCHAR(200),
    sequence_no                        INTEGER NOT NULL,
    start_date                           TIMESTAMPTZ NOT NULL,
    end_date                               TIMESTAMPTZ NOT NULL,
    status_code                              VARCHAR(20) NOT NULL,
    close_approved_by                          BIGINT,
    close_approved_at                            TIMESTAMPTZ,
    is_active_fl                                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_by                                       VARCHAR(100) NOT NULL,
    created_at                                         TIMESTAMPTZ NOT NULL,
    updated_by                                           VARCHAR(100) NOT NULL,
    updated_at                                             TIMESTAMPTZ NOT NULL
);

CREATE TABLE fin_journal_entry (
    journal_entry_pk         BIGINT GENERATED ALWAYS AS IDENTITY,
    entry_no                    VARCHAR(30)  NOT NULL,
    entry_date                    TIMESTAMPTZ NOT NULL,
    source_type_code                VARCHAR(20) NOT NULL,
    status_code                       VARCHAR(10) NOT NULL,
    fiscal_year_id                      BIGINT    NOT NULL,
    period_id                             BIGINT  NOT NULL,
    source_event_reference                  VARCHAR(100),
    template_id                               BIGINT,
    allocation_rule_id                          BIGINT,
    reversal_of_entry_id                          BIGINT,
    reversed_by_entry_id                            BIGINT,
    created_by                                        VARCHAR(100) NOT NULL,
    created_at                                          TIMESTAMPTZ NOT NULL,
    updated_by                                            VARCHAR(100) NOT NULL,
    updated_at                                              TIMESTAMPTZ NOT NULL
);

CREATE TABLE fin_journal_entry_line (
    journal_entry_line_pk    BIGINT GENERATED ALWAYS AS IDENTITY,
    journal_entry_id             BIGINT      NOT NULL,
    line_no                        INTEGER   NOT NULL,
    account_id                       BIGINT  NOT NULL,
    direction_code                     VARCHAR(10) NOT NULL,
    amount                                NUMERIC(18,4) NOT NULL,
    description_ar                         VARCHAR(500),
    description_en                           VARCHAR(500)
);

CREATE TABLE fin_journal_entry_line_dim (
    journal_entry_line_dim_pk BIGINT GENERATED ALWAYS AS IDENTITY,
    journal_entry_line_id        BIGINT NOT NULL,
    dimension_value_id             BIGINT NOT NULL
);

CREATE TABLE fin_role_permission (
    role_permission_pk       BIGINT GENERATED ALWAYS AS IDENTITY,
    role_id                     BIGINT      NOT NULL,
    page_code                     VARCHAR(40) NOT NULL,
    action_code                     VARCHAR(10) NOT NULL
);

CREATE TABLE fin_user_role (
    user_role_pk              BIGINT GENERATED ALWAYS AS IDENTITY,
    user_id                      BIGINT     NOT NULL,
    role_id                        BIGINT   NOT NULL
);

-- BLOCK 4 — COMMENTS (table + every column; each column comment cites its DBF id)

COMMENT ON TABLE fin_account IS 'ENT-FIN-001 — Chart of Account';
COMMENT ON COLUMN fin_account.account_pk IS 'DBF-FIN-001';
COMMENT ON COLUMN fin_account.parent_account_id IS 'DBF-FIN-002';
COMMENT ON COLUMN fin_account.code IS 'DBF-FIN-003';
COMMENT ON COLUMN fin_account.name_ar IS 'DBF-FIN-004';
COMMENT ON COLUMN fin_account.name_en IS 'DBF-FIN-005';
COMMENT ON COLUMN fin_account.account_type IS 'DBF-FIN-006';
COMMENT ON COLUMN fin_account.nature_code IS 'DBF-FIN-007';
COMMENT ON COLUMN fin_account.accepts_direct_posting_fl IS 'DBF-FIN-008';
COMMENT ON COLUMN fin_account.is_retained_earnings_account_fl IS 'DBF-FIN-009';
COMMENT ON COLUMN fin_account.is_active_fl IS 'DBF-FIN-010';
COMMENT ON COLUMN fin_account.created_by IS 'DBF-FIN-011';
COMMENT ON COLUMN fin_account.created_at IS 'DBF-FIN-012';
COMMENT ON COLUMN fin_account.updated_by IS 'DBF-FIN-013';
COMMENT ON COLUMN fin_account.updated_at IS 'DBF-FIN-014';

COMMENT ON TABLE fin_dimension IS 'ENT-FIN-002 — Account Dimension (definition)';
COMMENT ON COLUMN fin_dimension.dimension_pk IS 'DBF-FIN-015';
COMMENT ON COLUMN fin_dimension.dimension_key IS 'DBF-FIN-016';
COMMENT ON COLUMN fin_dimension.name_ar IS 'DBF-FIN-017';
COMMENT ON COLUMN fin_dimension.name_en IS 'DBF-FIN-018';
COMMENT ON COLUMN fin_dimension.control_type IS 'DBF-FIN-019';
COMMENT ON COLUMN fin_dimension.is_active_fl IS 'DBF-FIN-020';

COMMENT ON TABLE fin_dimension_value IS 'ENT-FIN-002 — Account Dimension (values)';
COMMENT ON COLUMN fin_dimension_value.dimension_value_pk IS 'DBF-FIN-021';
COMMENT ON COLUMN fin_dimension_value.dimension_id IS 'DBF-FIN-022';
COMMENT ON COLUMN fin_dimension_value.value_code IS 'DBF-FIN-023';
COMMENT ON COLUMN fin_dimension_value.value_name_ar IS 'DBF-FIN-024';
COMMENT ON COLUMN fin_dimension_value.value_name_en IS 'DBF-FIN-025';
COMMENT ON COLUMN fin_dimension_value.sort_order IS 'DBF-FIN-026';
COMMENT ON COLUMN fin_dimension_value.is_active_fl IS 'DBF-FIN-027';

COMMENT ON TABLE fin_lookup_type IS 'ENT-FIN-003 — Accounting Reference List (type)';
COMMENT ON COLUMN fin_lookup_type.lookup_type_pk IS 'DBF-FIN-028';
COMMENT ON COLUMN fin_lookup_type.lookup_key IS 'DBF-FIN-029';
COMMENT ON COLUMN fin_lookup_type.name_ar IS 'DBF-FIN-030';
COMMENT ON COLUMN fin_lookup_type.name_en IS 'DBF-FIN-031';
COMMENT ON COLUMN fin_lookup_type.is_active_fl IS 'DBF-FIN-032';

COMMENT ON TABLE fin_lookup_value IS 'ENT-FIN-003 — Accounting Reference List (values)';
COMMENT ON COLUMN fin_lookup_value.lookup_value_pk IS 'DBF-FIN-033';
COMMENT ON COLUMN fin_lookup_value.lookup_type_id IS 'DBF-FIN-034';
COMMENT ON COLUMN fin_lookup_value.value_code IS 'DBF-FIN-035';
COMMENT ON COLUMN fin_lookup_value.label_ar IS 'DBF-FIN-036';
COMMENT ON COLUMN fin_lookup_value.label_en IS 'DBF-FIN-037';
COMMENT ON COLUMN fin_lookup_value.sort_order IS 'DBF-FIN-038';
COMMENT ON COLUMN fin_lookup_value.is_active_fl IS 'DBF-FIN-039';

COMMENT ON TABLE fin_event_rule IS 'ENT-FIN-004 — Event-Type Rule';
COMMENT ON COLUMN fin_event_rule.event_rule_pk IS 'DBF-FIN-040';
COMMENT ON COLUMN fin_event_rule.event_type_code IS 'DBF-FIN-041';
COMMENT ON COLUMN fin_event_rule.name_ar IS 'DBF-FIN-042';
COMMENT ON COLUMN fin_event_rule.name_en IS 'DBF-FIN-043';
COMMENT ON COLUMN fin_event_rule.is_active_fl IS 'DBF-FIN-044';
COMMENT ON COLUMN fin_event_rule.created_by IS 'DBF-FIN-045';
COMMENT ON COLUMN fin_event_rule.created_at IS 'DBF-FIN-046';
COMMENT ON COLUMN fin_event_rule.updated_by IS 'DBF-FIN-047';
COMMENT ON COLUMN fin_event_rule.updated_at IS 'DBF-FIN-048';

COMMENT ON TABLE fin_rule_line IS 'ENT-FIN-005 — Rule Line';
COMMENT ON COLUMN fin_rule_line.rule_line_pk IS 'DBF-FIN-049';
COMMENT ON COLUMN fin_rule_line.event_rule_id IS 'DBF-FIN-050';
COMMENT ON COLUMN fin_rule_line.line_no IS 'DBF-FIN-051';
COMMENT ON COLUMN fin_rule_line.account_derivation_type IS 'DBF-FIN-052';
COMMENT ON COLUMN fin_rule_line.constant_account_id IS 'DBF-FIN-053';
COMMENT ON COLUMN fin_rule_line.event_field_name IS 'DBF-FIN-054';
COMMENT ON COLUMN fin_rule_line.amount_source_field IS 'DBF-FIN-055';
COMMENT ON COLUMN fin_rule_line.amount_source_operation IS 'DBF-FIN-056';
COMMENT ON COLUMN fin_rule_line.amount_operation_value IS 'DBF-FIN-057';
COMMENT ON COLUMN fin_rule_line.direction_code IS 'DBF-FIN-058';
COMMENT ON COLUMN fin_rule_line.distribution_type IS 'DBF-FIN-059';
COMMENT ON COLUMN fin_rule_line.distribution_value IS 'DBF-FIN-060';
COMMENT ON COLUMN fin_rule_line.is_active_fl IS 'DBF-FIN-061';

COMMENT ON TABLE fin_rule_line_mapping IS 'ENT-FIN-005 — Rule Line mapping entries (ADR-FIN-002)';
COMMENT ON COLUMN fin_rule_line_mapping.rule_line_mapping_pk IS 'DBF-FIN-062';
COMMENT ON COLUMN fin_rule_line_mapping.rule_line_id IS 'DBF-FIN-063';
COMMENT ON COLUMN fin_rule_line_mapping.event_attribute_name IS 'DBF-FIN-064';
COMMENT ON COLUMN fin_rule_line_mapping.event_attribute_value IS 'DBF-FIN-065';
COMMENT ON COLUMN fin_rule_line_mapping.resulting_dimension_value_id IS 'DBF-FIN-066';

COMMENT ON TABLE fin_journal_entry IS 'ENT-FIN-006 — Journal Entry';
COMMENT ON COLUMN fin_journal_entry.journal_entry_pk IS 'DBF-FIN-067';
COMMENT ON COLUMN fin_journal_entry.entry_no IS 'DBF-FIN-068';
COMMENT ON COLUMN fin_journal_entry.entry_date IS 'DBF-FIN-069';
COMMENT ON COLUMN fin_journal_entry.source_type_code IS 'DBF-FIN-070';
COMMENT ON COLUMN fin_journal_entry.status_code IS 'DBF-FIN-071';
COMMENT ON COLUMN fin_journal_entry.fiscal_year_id IS 'DBF-FIN-072';
COMMENT ON COLUMN fin_journal_entry.period_id IS 'DBF-FIN-073';
COMMENT ON COLUMN fin_journal_entry.source_event_reference IS 'DBF-FIN-074';
COMMENT ON COLUMN fin_journal_entry.template_id IS 'DBF-FIN-075';
COMMENT ON COLUMN fin_journal_entry.allocation_rule_id IS 'DBF-FIN-076';
COMMENT ON COLUMN fin_journal_entry.reversal_of_entry_id IS 'DBF-FIN-077';
COMMENT ON COLUMN fin_journal_entry.reversed_by_entry_id IS 'DBF-FIN-078';
COMMENT ON COLUMN fin_journal_entry.created_by IS 'DBF-FIN-079';
COMMENT ON COLUMN fin_journal_entry.created_at IS 'DBF-FIN-080';
COMMENT ON COLUMN fin_journal_entry.updated_by IS 'DBF-FIN-081';
COMMENT ON COLUMN fin_journal_entry.updated_at IS 'DBF-FIN-082';

COMMENT ON TABLE fin_journal_entry_line IS 'ENT-FIN-007 — Journal Entry Line';
COMMENT ON COLUMN fin_journal_entry_line.journal_entry_line_pk IS 'DBF-FIN-083';
COMMENT ON COLUMN fin_journal_entry_line.journal_entry_id IS 'DBF-FIN-084';
COMMENT ON COLUMN fin_journal_entry_line.line_no IS 'DBF-FIN-085';
COMMENT ON COLUMN fin_journal_entry_line.account_id IS 'DBF-FIN-086';
COMMENT ON COLUMN fin_journal_entry_line.direction_code IS 'DBF-FIN-087';
COMMENT ON COLUMN fin_journal_entry_line.amount IS 'DBF-FIN-088';
COMMENT ON COLUMN fin_journal_entry_line.description_ar IS 'DBF-FIN-089';
COMMENT ON COLUMN fin_journal_entry_line.description_en IS 'DBF-FIN-090';

COMMENT ON TABLE fin_journal_entry_line_dim IS 'ENT-FIN-007 — Journal Entry Line dimension segments';
COMMENT ON COLUMN fin_journal_entry_line_dim.journal_entry_line_dim_pk IS 'DBF-FIN-091';
COMMENT ON COLUMN fin_journal_entry_line_dim.journal_entry_line_id IS 'DBF-FIN-092';
COMMENT ON COLUMN fin_journal_entry_line_dim.dimension_value_id IS 'DBF-FIN-093';

COMMENT ON TABLE fin_recurring_template IS 'ENT-FIN-008 — Recurring-Reversing Entry Template';
COMMENT ON COLUMN fin_recurring_template.recurring_template_pk IS 'DBF-FIN-094';
COMMENT ON COLUMN fin_recurring_template.template_name_ar IS 'DBF-FIN-095';
COMMENT ON COLUMN fin_recurring_template.template_name_en IS 'DBF-FIN-096';
COMMENT ON COLUMN fin_recurring_template.template_type_code IS 'DBF-FIN-097';
COMMENT ON COLUMN fin_recurring_template.schedule_rule IS 'DBF-FIN-098';
COMMENT ON COLUMN fin_recurring_template.next_run_date IS 'DBF-FIN-099';
COMMENT ON COLUMN fin_recurring_template.is_active_fl IS 'DBF-FIN-100';
COMMENT ON COLUMN fin_recurring_template.created_by IS 'DBF-FIN-101';
COMMENT ON COLUMN fin_recurring_template.created_at IS 'DBF-FIN-102';
COMMENT ON COLUMN fin_recurring_template.updated_by IS 'DBF-FIN-103';
COMMENT ON COLUMN fin_recurring_template.updated_at IS 'DBF-FIN-104';

COMMENT ON TABLE fin_recurring_template_line IS 'ENT-FIN-008 — Recurring-Reversing Entry Template lines';
COMMENT ON COLUMN fin_recurring_template_line.recurring_template_line_pk IS 'DBF-FIN-105';
COMMENT ON COLUMN fin_recurring_template_line.recurring_template_id IS 'DBF-FIN-106';
COMMENT ON COLUMN fin_recurring_template_line.line_no IS 'DBF-FIN-107';
COMMENT ON COLUMN fin_recurring_template_line.account_id IS 'DBF-FIN-108';
COMMENT ON COLUMN fin_recurring_template_line.amount_source_value IS 'DBF-FIN-109';
COMMENT ON COLUMN fin_recurring_template_line.amount_source_formula IS 'DBF-FIN-110';
COMMENT ON COLUMN fin_recurring_template_line.direction_code IS 'DBF-FIN-111';

COMMENT ON TABLE fin_recurring_template_line_dim IS 'ENT-FIN-008 — Recurring-Reversing Entry Template line dimension segments';
COMMENT ON COLUMN fin_recurring_template_line_dim.recurring_template_line_dim_pk IS 'DBF-FIN-112';
COMMENT ON COLUMN fin_recurring_template_line_dim.recurring_template_line_id IS 'DBF-FIN-113';
COMMENT ON COLUMN fin_recurring_template_line_dim.dimension_value_id IS 'DBF-FIN-114';

COMMENT ON TABLE fin_allocation_rule IS 'ENT-FIN-009 — Allocation Rule';
COMMENT ON COLUMN fin_allocation_rule.allocation_rule_pk IS 'DBF-FIN-115';
COMMENT ON COLUMN fin_allocation_rule.rule_name_ar IS 'DBF-FIN-116';
COMMENT ON COLUMN fin_allocation_rule.rule_name_en IS 'DBF-FIN-117';
COMMENT ON COLUMN fin_allocation_rule.source_account_id IS 'DBF-FIN-118';
COMMENT ON COLUMN fin_allocation_rule.is_active_fl IS 'DBF-FIN-119';
COMMENT ON COLUMN fin_allocation_rule.created_by IS 'DBF-FIN-120';
COMMENT ON COLUMN fin_allocation_rule.created_at IS 'DBF-FIN-121';
COMMENT ON COLUMN fin_allocation_rule.updated_by IS 'DBF-FIN-122';
COMMENT ON COLUMN fin_allocation_rule.updated_at IS 'DBF-FIN-123';

COMMENT ON TABLE fin_allocation_rule_dim IS 'ENT-FIN-009 — Allocation Rule source dimension values';
COMMENT ON COLUMN fin_allocation_rule_dim.allocation_rule_dim_pk IS 'DBF-FIN-124';
COMMENT ON COLUMN fin_allocation_rule_dim.allocation_rule_id IS 'DBF-FIN-125';
COMMENT ON COLUMN fin_allocation_rule_dim.dimension_value_id IS 'DBF-FIN-126';

COMMENT ON TABLE fin_allocation_rule_line IS 'ENT-FIN-009 — Allocation Rule lines';
COMMENT ON COLUMN fin_allocation_rule_line.allocation_rule_line_pk IS 'DBF-FIN-127';
COMMENT ON COLUMN fin_allocation_rule_line.allocation_rule_id IS 'DBF-FIN-128';
COMMENT ON COLUMN fin_allocation_rule_line.line_no IS 'DBF-FIN-129';
COMMENT ON COLUMN fin_allocation_rule_line.target_account_id IS 'DBF-FIN-130';
COMMENT ON COLUMN fin_allocation_rule_line.distribution_type IS 'DBF-FIN-131';
COMMENT ON COLUMN fin_allocation_rule_line.distribution_value IS 'DBF-FIN-132';

COMMENT ON TABLE fin_allocation_rule_line_dim IS 'ENT-FIN-009 — Allocation Rule line target dimension values';
COMMENT ON COLUMN fin_allocation_rule_line_dim.allocation_rule_line_dim_pk IS 'DBF-FIN-133';
COMMENT ON COLUMN fin_allocation_rule_line_dim.allocation_rule_line_id IS 'DBF-FIN-134';
COMMENT ON COLUMN fin_allocation_rule_line_dim.dimension_value_id IS 'DBF-FIN-135';

COMMENT ON TABLE fin_fiscal_year IS 'ENT-FIN-010 — Fiscal Year';
COMMENT ON COLUMN fin_fiscal_year.fiscal_year_pk IS 'DBF-FIN-136';
COMMENT ON COLUMN fin_fiscal_year.year_code IS 'DBF-FIN-137';
COMMENT ON COLUMN fin_fiscal_year.name_ar IS 'DBF-FIN-138';
COMMENT ON COLUMN fin_fiscal_year.name_en IS 'DBF-FIN-139';
COMMENT ON COLUMN fin_fiscal_year.start_date IS 'DBF-FIN-140';
COMMENT ON COLUMN fin_fiscal_year.end_date IS 'DBF-FIN-141';
COMMENT ON COLUMN fin_fiscal_year.status_code IS 'DBF-FIN-142';
COMMENT ON COLUMN fin_fiscal_year.is_active_fl IS 'DBF-FIN-143';
COMMENT ON COLUMN fin_fiscal_year.created_by IS 'DBF-FIN-144';
COMMENT ON COLUMN fin_fiscal_year.created_at IS 'DBF-FIN-145';
COMMENT ON COLUMN fin_fiscal_year.updated_by IS 'DBF-FIN-146';
COMMENT ON COLUMN fin_fiscal_year.updated_at IS 'DBF-FIN-147';

COMMENT ON TABLE fin_fiscal_period IS 'ENT-FIN-011 — Fiscal Period';
COMMENT ON COLUMN fin_fiscal_period.fiscal_period_pk IS 'DBF-FIN-148';
COMMENT ON COLUMN fin_fiscal_period.fiscal_year_id IS 'DBF-FIN-149';
COMMENT ON COLUMN fin_fiscal_period.period_code IS 'DBF-FIN-150';
COMMENT ON COLUMN fin_fiscal_period.name_ar IS 'DBF-FIN-151';
COMMENT ON COLUMN fin_fiscal_period.name_en IS 'DBF-FIN-152';
COMMENT ON COLUMN fin_fiscal_period.sequence_no IS 'DBF-FIN-153';
COMMENT ON COLUMN fin_fiscal_period.start_date IS 'DBF-FIN-154';
COMMENT ON COLUMN fin_fiscal_period.end_date IS 'DBF-FIN-155';
COMMENT ON COLUMN fin_fiscal_period.status_code IS 'DBF-FIN-156';
COMMENT ON COLUMN fin_fiscal_period.close_approved_by IS 'DBF-FIN-157';
COMMENT ON COLUMN fin_fiscal_period.close_approved_at IS 'DBF-FIN-158';
COMMENT ON COLUMN fin_fiscal_period.is_active_fl IS 'DBF-FIN-159';
COMMENT ON COLUMN fin_fiscal_period.created_by IS 'DBF-FIN-160';
COMMENT ON COLUMN fin_fiscal_period.created_at IS 'DBF-FIN-161';
COMMENT ON COLUMN fin_fiscal_period.updated_by IS 'DBF-FIN-162';
COMMENT ON COLUMN fin_fiscal_period.updated_at IS 'DBF-FIN-163';

COMMENT ON TABLE fin_user IS 'ENT-FIN-012 — Accounting User';
COMMENT ON COLUMN fin_user.user_pk IS 'DBF-FIN-164';
COMMENT ON COLUMN fin_user.username IS 'DBF-FIN-165';
COMMENT ON COLUMN fin_user.name_ar IS 'DBF-FIN-166';
COMMENT ON COLUMN fin_user.name_en IS 'DBF-FIN-167';
COMMENT ON COLUMN fin_user.password_hash IS 'DBF-FIN-168';
COMMENT ON COLUMN fin_user.last_login_at IS 'DBF-FIN-169';
COMMENT ON COLUMN fin_user.is_active_fl IS 'DBF-FIN-170';
COMMENT ON COLUMN fin_user.created_by IS 'DBF-FIN-171';
COMMENT ON COLUMN fin_user.created_at IS 'DBF-FIN-172';
COMMENT ON COLUMN fin_user.updated_by IS 'DBF-FIN-173';
COMMENT ON COLUMN fin_user.updated_at IS 'DBF-FIN-174';

COMMENT ON TABLE fin_role IS 'ENT-FIN-013 — Role & Permission (role)';
COMMENT ON COLUMN fin_role.role_pk IS 'DBF-FIN-175';
COMMENT ON COLUMN fin_role.role_code IS 'DBF-FIN-176';
COMMENT ON COLUMN fin_role.role_name_ar IS 'DBF-FIN-177';
COMMENT ON COLUMN fin_role.role_name_en IS 'DBF-FIN-178';
COMMENT ON COLUMN fin_role.is_active_fl IS 'DBF-FIN-179';
COMMENT ON COLUMN fin_role.created_by IS 'DBF-FIN-180';
COMMENT ON COLUMN fin_role.created_at IS 'DBF-FIN-181';
COMMENT ON COLUMN fin_role.updated_by IS 'DBF-FIN-182';
COMMENT ON COLUMN fin_role.updated_at IS 'DBF-FIN-183';

COMMENT ON TABLE fin_role_permission IS 'ENT-FIN-013 — Role & Permission (permission assignments)';
COMMENT ON COLUMN fin_role_permission.role_permission_pk IS 'DBF-FIN-184';
COMMENT ON COLUMN fin_role_permission.role_id IS 'DBF-FIN-185';
COMMENT ON COLUMN fin_role_permission.page_code IS 'DBF-FIN-186';
COMMENT ON COLUMN fin_role_permission.action_code IS 'DBF-FIN-187';

COMMENT ON TABLE fin_user_role IS 'ENT-FIN-013 — Role & Permission (user assignments)';
COMMENT ON COLUMN fin_user_role.user_role_pk IS 'DBF-FIN-188';
COMMENT ON COLUMN fin_user_role.user_id IS 'DBF-FIN-189';
COMMENT ON COLUMN fin_user_role.role_id IS 'DBF-FIN-190';

-- BLOCK 5 — CONSTRAINTS

-- 5a PRIMARY KEYS
ALTER TABLE fin_account ADD CONSTRAINT PK_FIN_ACCOUNT PRIMARY KEY (account_pk);
ALTER TABLE fin_dimension ADD CONSTRAINT PK_FIN_DIMENSION PRIMARY KEY (dimension_pk);
ALTER TABLE fin_dimension_value ADD CONSTRAINT PK_FIN_DIMENSION_VALUE PRIMARY KEY (dimension_value_pk);
ALTER TABLE fin_lookup_type ADD CONSTRAINT PK_FIN_LOOKUP_TYPE PRIMARY KEY (lookup_type_pk);
ALTER TABLE fin_lookup_value ADD CONSTRAINT PK_FIN_LOOKUP_VALUE PRIMARY KEY (lookup_value_pk);
ALTER TABLE fin_event_rule ADD CONSTRAINT PK_FIN_EVENT_RULE PRIMARY KEY (event_rule_pk);
ALTER TABLE fin_rule_line ADD CONSTRAINT PK_FIN_RULE_LINE PRIMARY KEY (rule_line_pk);
ALTER TABLE fin_rule_line_mapping ADD CONSTRAINT PK_FIN_RULE_LINE_MAPPING PRIMARY KEY (rule_line_mapping_pk);
ALTER TABLE fin_journal_entry ADD CONSTRAINT PK_FIN_JOURNAL_ENTRY PRIMARY KEY (journal_entry_pk);
ALTER TABLE fin_journal_entry_line ADD CONSTRAINT PK_FIN_JOURNAL_ENTRY_LINE PRIMARY KEY (journal_entry_line_pk);
ALTER TABLE fin_journal_entry_line_dim ADD CONSTRAINT PK_FIN_JOURNAL_ENTRY_LINE_DIM PRIMARY KEY (journal_entry_line_dim_pk);
ALTER TABLE fin_recurring_template ADD CONSTRAINT PK_FIN_RECURRING_TEMPLATE PRIMARY KEY (recurring_template_pk);
ALTER TABLE fin_recurring_template_line ADD CONSTRAINT PK_FIN_RECURRING_TEMPLATE_LINE PRIMARY KEY (recurring_template_line_pk);
ALTER TABLE fin_recurring_template_line_dim ADD CONSTRAINT PK_FIN_RECURRING_TEMPLATE_LINE_DIM PRIMARY KEY (recurring_template_line_dim_pk);
ALTER TABLE fin_allocation_rule ADD CONSTRAINT PK_FIN_ALLOCATION_RULE PRIMARY KEY (allocation_rule_pk);
ALTER TABLE fin_allocation_rule_dim ADD CONSTRAINT PK_FIN_ALLOCATION_RULE_DIM PRIMARY KEY (allocation_rule_dim_pk);
ALTER TABLE fin_allocation_rule_line ADD CONSTRAINT PK_FIN_ALLOCATION_RULE_LINE PRIMARY KEY (allocation_rule_line_pk);
ALTER TABLE fin_allocation_rule_line_dim ADD CONSTRAINT PK_FIN_ALLOCATION_RULE_LINE_DIM PRIMARY KEY (allocation_rule_line_dim_pk);
ALTER TABLE fin_fiscal_year ADD CONSTRAINT PK_FIN_FISCAL_YEAR PRIMARY KEY (fiscal_year_pk);
ALTER TABLE fin_fiscal_period ADD CONSTRAINT PK_FIN_FISCAL_PERIOD PRIMARY KEY (fiscal_period_pk);
ALTER TABLE fin_user ADD CONSTRAINT PK_FIN_USER PRIMARY KEY (user_pk);
ALTER TABLE fin_role ADD CONSTRAINT PK_FIN_ROLE PRIMARY KEY (role_pk);
ALTER TABLE fin_role_permission ADD CONSTRAINT PK_FIN_ROLE_PERMISSION PRIMARY KEY (role_permission_pk);
ALTER TABLE fin_user_role ADD CONSTRAINT PK_FIN_USER_ROLE PRIMARY KEY (user_role_pk);

-- 5b UNIQUE
ALTER TABLE fin_account ADD CONSTRAINT UQ_FIN_ACCOUNT_CODE UNIQUE (code);
ALTER TABLE fin_dimension ADD CONSTRAINT UQ_FIN_DIMENSION_KEY UNIQUE (dimension_key);
ALTER TABLE fin_dimension_value ADD CONSTRAINT UQ_FIN_DIMENSION_VALUE_CODE UNIQUE (dimension_id, value_code);
ALTER TABLE fin_lookup_type ADD CONSTRAINT UQ_FIN_LOOKUP_TYPE_KEY UNIQUE (lookup_key);
ALTER TABLE fin_lookup_value ADD CONSTRAINT UQ_FIN_LOOKUP_VALUE_CODE UNIQUE (lookup_type_id, value_code);
ALTER TABLE fin_event_rule ADD CONSTRAINT UQ_FIN_EVENT_RULE_TYPE UNIQUE (event_type_code);
ALTER TABLE fin_journal_entry ADD CONSTRAINT UQ_FIN_JOURNAL_ENTRY_NO UNIQUE (entry_no);
ALTER TABLE fin_journal_entry_line_dim ADD CONSTRAINT UQ_FIN_JEL_DIM UNIQUE (journal_entry_line_id, dimension_value_id);
ALTER TABLE fin_recurring_template_line_dim ADD CONSTRAINT UQ_FIN_RTL_DIM UNIQUE (recurring_template_line_id, dimension_value_id);
ALTER TABLE fin_allocation_rule_dim ADD CONSTRAINT UQ_FIN_AR_DIM UNIQUE (allocation_rule_id, dimension_value_id);
ALTER TABLE fin_allocation_rule_line_dim ADD CONSTRAINT UQ_FIN_ARL_DIM UNIQUE (allocation_rule_line_id, dimension_value_id);
ALTER TABLE fin_fiscal_year ADD CONSTRAINT UQ_FIN_FISCAL_YEAR_CODE UNIQUE (year_code);
ALTER TABLE fin_fiscal_period ADD CONSTRAINT UQ_FIN_FISCAL_PERIOD_CODE UNIQUE (fiscal_year_id, period_code);
ALTER TABLE fin_user ADD CONSTRAINT UQ_FIN_USER_USERNAME UNIQUE (username);
ALTER TABLE fin_role ADD CONSTRAINT UQ_FIN_ROLE_CODE UNIQUE (role_code);
ALTER TABLE fin_role_permission ADD CONSTRAINT UQ_FIN_ROLE_PERM UNIQUE (role_id, page_code, action_code);
ALTER TABLE fin_user_role ADD CONSTRAINT UQ_FIN_USER_ROLE UNIQUE (user_id, role_id);

-- 5c CHECK  (RULE-FIN-* backed constraints and closed vocabularies — SRS A6/§4.2)
ALTER TABLE fin_account ADD CONSTRAINT CHK_FIN_ACCOUNT_NATURE CHECK (nature_code IN ('DEBIT','CREDIT'));
ALTER TABLE fin_dimension ADD CONSTRAINT CHK_FIN_DIMENSION_CONTROL CHECK (control_type IN ('FIXED_LIST','REFERENCE_ENTITY'));
ALTER TABLE fin_rule_line ADD CONSTRAINT CHK_FIN_RULE_LINE_DERIVATION CHECK (account_derivation_type IN ('CONSTANT','EVENT_FIELD','MAPPING_SET'));
ALTER TABLE fin_rule_line ADD CONSTRAINT CHK_FIN_RULE_LINE_OPERATION CHECK (amount_source_operation IN ('DIRECT','PERCENTAGE','REMAINDER'));
ALTER TABLE fin_rule_line ADD CONSTRAINT CHK_FIN_RULE_LINE_DIRECTION CHECK (direction_code IN ('DEBIT','CREDIT'));
ALTER TABLE fin_rule_line ADD CONSTRAINT CHK_FIN_RULE_LINE_DISTRIBUTION CHECK (distribution_type IN ('FIXED','PERCENTAGE','REMAINDER'));  -- RULE-FIN-005
ALTER TABLE fin_journal_entry ADD CONSTRAINT CHK_FIN_JE_STATUS CHECK (status_code IN ('DRAFT','POSTED'));  -- A7
ALTER TABLE fin_journal_entry_line ADD CONSTRAINT CHK_FIN_JEL_DIRECTION CHECK (direction_code IN ('DEBIT','CREDIT'));
ALTER TABLE fin_journal_entry_line ADD CONSTRAINT CHK_FIN_JEL_AMOUNT CHECK (amount > 0);  -- RULE-FIN-002 (header-level balance enforced in application/trigger, §6 BLOCK 6)
ALTER TABLE fin_recurring_template ADD CONSTRAINT CHK_FIN_RT_TYPE CHECK (template_type_code IN ('RECURRING','REVERSING'));
ALTER TABLE fin_recurring_template_line ADD CONSTRAINT CHK_FIN_RTL_DIRECTION CHECK (direction_code IN ('DEBIT','CREDIT'));
ALTER TABLE fin_allocation_rule_line ADD CONSTRAINT CHK_FIN_ARL_DISTRIBUTION CHECK (distribution_type IN ('FIXED','PERCENTAGE','REMAINDER'));  -- RULE-FIN-014
ALTER TABLE fin_fiscal_year ADD CONSTRAINT CHK_FIN_FY_STATUS CHECK (status_code IN ('OPEN','YEAR_END_CLOSED'));  -- A7
ALTER TABLE fin_fiscal_period ADD CONSTRAINT CHK_FIN_FP_STATUS CHECK (status_code IN ('OPEN','SOFT_CLOSE','HARD_CLOSE'));  -- A7
ALTER TABLE fin_role_permission ADD CONSTRAINT CHK_FIN_ROLE_PERM_ACTION CHECK (action_code IN ('VIEW','CREATE','UPDATE','DELETE'));

-- 5d INTRA-MODULE FK (parent PK first; all FKs are intra-module — FIN has no XM)
ALTER TABLE fin_account ADD CONSTRAINT FK_FIN_ACCOUNT_PARENT FOREIGN KEY (parent_account_id) REFERENCES fin_account (account_pk);
ALTER TABLE fin_dimension_value ADD CONSTRAINT FK_FIN_DIMVAL_DIMENSION FOREIGN KEY (dimension_id) REFERENCES fin_dimension (dimension_pk);
ALTER TABLE fin_lookup_value ADD CONSTRAINT FK_FIN_LKPVAL_TYPE FOREIGN KEY (lookup_type_id) REFERENCES fin_lookup_type (lookup_type_pk);
ALTER TABLE fin_rule_line ADD CONSTRAINT FK_FIN_RULELINE_RULE FOREIGN KEY (event_rule_id) REFERENCES fin_event_rule (event_rule_pk);
ALTER TABLE fin_rule_line ADD CONSTRAINT FK_FIN_RULELINE_ACCOUNT FOREIGN KEY (constant_account_id) REFERENCES fin_account (account_pk);
ALTER TABLE fin_rule_line_mapping ADD CONSTRAINT FK_FIN_RLM_RULELINE FOREIGN KEY (rule_line_id) REFERENCES fin_rule_line (rule_line_pk);
ALTER TABLE fin_rule_line_mapping ADD CONSTRAINT FK_FIN_RLM_DIMVAL FOREIGN KEY (resulting_dimension_value_id) REFERENCES fin_dimension_value (dimension_value_pk);
ALTER TABLE fin_journal_entry ADD CONSTRAINT FK_FIN_JE_FISCALYEAR FOREIGN KEY (fiscal_year_id) REFERENCES fin_fiscal_year (fiscal_year_pk);
ALTER TABLE fin_journal_entry ADD CONSTRAINT FK_FIN_JE_PERIOD FOREIGN KEY (period_id) REFERENCES fin_fiscal_period (fiscal_period_pk);
ALTER TABLE fin_journal_entry ADD CONSTRAINT FK_FIN_JE_TEMPLATE FOREIGN KEY (template_id) REFERENCES fin_recurring_template (recurring_template_pk);
ALTER TABLE fin_journal_entry ADD CONSTRAINT FK_FIN_JE_ALLOCRULE FOREIGN KEY (allocation_rule_id) REFERENCES fin_allocation_rule (allocation_rule_pk);
ALTER TABLE fin_journal_entry ADD CONSTRAINT FK_FIN_JE_REVERSALOF FOREIGN KEY (reversal_of_entry_id) REFERENCES fin_journal_entry (journal_entry_pk);
ALTER TABLE fin_journal_entry ADD CONSTRAINT FK_FIN_JE_REVERSEDBY FOREIGN KEY (reversed_by_entry_id) REFERENCES fin_journal_entry (journal_entry_pk);
ALTER TABLE fin_journal_entry_line ADD CONSTRAINT FK_FIN_JEL_ENTRY FOREIGN KEY (journal_entry_id) REFERENCES fin_journal_entry (journal_entry_pk);
ALTER TABLE fin_journal_entry_line ADD CONSTRAINT FK_FIN_JEL_ACCOUNT FOREIGN KEY (account_id) REFERENCES fin_account (account_pk);
ALTER TABLE fin_journal_entry_line_dim ADD CONSTRAINT FK_FIN_JELDIM_LINE FOREIGN KEY (journal_entry_line_id) REFERENCES fin_journal_entry_line (journal_entry_line_pk);
ALTER TABLE fin_journal_entry_line_dim ADD CONSTRAINT FK_FIN_JELDIM_DIMVAL FOREIGN KEY (dimension_value_id) REFERENCES fin_dimension_value (dimension_value_pk);
ALTER TABLE fin_recurring_template_line ADD CONSTRAINT FK_FIN_RTL_TEMPLATE FOREIGN KEY (recurring_template_id) REFERENCES fin_recurring_template (recurring_template_pk);
ALTER TABLE fin_recurring_template_line ADD CONSTRAINT FK_FIN_RTL_ACCOUNT FOREIGN KEY (account_id) REFERENCES fin_account (account_pk);
ALTER TABLE fin_recurring_template_line_dim ADD CONSTRAINT FK_FIN_RTLDIM_LINE FOREIGN KEY (recurring_template_line_id) REFERENCES fin_recurring_template_line (recurring_template_line_pk);
ALTER TABLE fin_recurring_template_line_dim ADD CONSTRAINT FK_FIN_RTLDIM_DIMVAL FOREIGN KEY (dimension_value_id) REFERENCES fin_dimension_value (dimension_value_pk);
ALTER TABLE fin_allocation_rule ADD CONSTRAINT FK_FIN_AR_ACCOUNT FOREIGN KEY (source_account_id) REFERENCES fin_account (account_pk);
ALTER TABLE fin_allocation_rule_dim ADD CONSTRAINT FK_FIN_ARDIM_RULE FOREIGN KEY (allocation_rule_id) REFERENCES fin_allocation_rule (allocation_rule_pk);
ALTER TABLE fin_allocation_rule_dim ADD CONSTRAINT FK_FIN_ARDIM_DIMVAL FOREIGN KEY (dimension_value_id) REFERENCES fin_dimension_value (dimension_value_pk);
ALTER TABLE fin_allocation_rule_line ADD CONSTRAINT FK_FIN_ARL_RULE FOREIGN KEY (allocation_rule_id) REFERENCES fin_allocation_rule (allocation_rule_pk);
ALTER TABLE fin_allocation_rule_line ADD CONSTRAINT FK_FIN_ARL_ACCOUNT FOREIGN KEY (target_account_id) REFERENCES fin_account (account_pk);
ALTER TABLE fin_allocation_rule_line_dim ADD CONSTRAINT FK_FIN_ARLDIM_LINE FOREIGN KEY (allocation_rule_line_id) REFERENCES fin_allocation_rule_line (allocation_rule_line_pk);
ALTER TABLE fin_allocation_rule_line_dim ADD CONSTRAINT FK_FIN_ARLDIM_DIMVAL FOREIGN KEY (dimension_value_id) REFERENCES fin_dimension_value (dimension_value_pk);
ALTER TABLE fin_fiscal_period ADD CONSTRAINT FK_FIN_FP_FISCALYEAR FOREIGN KEY (fiscal_year_id) REFERENCES fin_fiscal_year (fiscal_year_pk);
ALTER TABLE fin_fiscal_period ADD CONSTRAINT FK_FIN_FP_APPROVEDBY FOREIGN KEY (close_approved_by) REFERENCES fin_user (user_pk);
ALTER TABLE fin_role_permission ADD CONSTRAINT FK_FIN_ROLEPERM_ROLE FOREIGN KEY (role_id) REFERENCES fin_role (role_pk);
ALTER TABLE fin_user_role ADD CONSTRAINT FK_FIN_USERROLE_USER FOREIGN KEY (user_id) REFERENCES fin_user (user_pk);
ALTER TABLE fin_user_role ADD CONSTRAINT FK_FIN_USERROLE_ROLE FOREIGN KEY (role_id) REFERENCES fin_role (role_pk);

-- BLOCK 6 — TRIGGERS (only where an SRS RULE requires them; never for PK population)

-- RULE-FIN-002: debits must equal credits at the journal-entry header level. A
-- CHECK constraint cannot aggregate sibling rows, so this is enforced by an
-- AFTER INSERT/UPDATE/DELETE trigger on fin_journal_entry_line, validated only
-- when the parent header transitions to POSTED (application-orchestrated); the
-- trigger itself raises an exception if invoked while the header is POSTED and
-- the balance would no longer hold, protecting RULE-FIN-006 (posted immutability).
CREATE OR REPLACE FUNCTION fin_fn_check_entry_balance() RETURNS TRIGGER AS $$
DECLARE
    v_status VARCHAR(10);
    v_debit  NUMERIC(18,4);
    v_credit NUMERIC(18,4);
    v_entry_id BIGINT := COALESCE(NEW.journal_entry_id, OLD.journal_entry_id);
BEGIN
    SELECT status_code INTO v_status FROM fin_journal_entry WHERE journal_entry_pk = v_entry_id;
    IF v_status = 'POSTED' THEN
        SELECT COALESCE(SUM(CASE WHEN direction_code = 'DEBIT' THEN amount ELSE 0 END), 0),
               COALESCE(SUM(CASE WHEN direction_code = 'CREDIT' THEN amount ELSE 0 END), 0)
          INTO v_debit, v_credit
          FROM fin_journal_entry_line WHERE journal_entry_id = v_entry_id;
        IF v_debit <> v_credit THEN
            RAISE EXCEPTION 'RULE-FIN-002: debit total (%%) does not equal credit total (%%) for journal_entry_pk %%', v_debit, v_credit, v_entry_id;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER trg_fin_jel_balance
    AFTER INSERT OR UPDATE OR DELETE ON fin_journal_entry_line
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION fin_fn_check_entry_balance();

-- RULE-FIN-006: a POSTED journal entry (and its lines) is immutable.
CREATE OR REPLACE FUNCTION fin_fn_block_posted_entry_edit() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status_code = 'POSTED' THEN
        RAISE EXCEPTION 'RULE-FIN-006: a posted entry is locked and cannot be edited or deleted (journal_entry_pk %%)', OLD.journal_entry_pk;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_fin_je_no_edit_when_posted
    BEFORE UPDATE OR DELETE ON fin_journal_entry
    FOR EACH ROW EXECUTE FUNCTION fin_fn_block_posted_entry_edit();

-- BLOCK 7 — INDEXES (non-PK; every FK column; every SRS PART B search/list filter; every UNIQUE business key already indexed by its UNIQUE constraint)

CREATE INDEX IDX_FIN_ACCOUNT_PARENT ON fin_account (parent_account_id);
CREATE INDEX IDX_FIN_ACCOUNT_TYPE ON fin_account (account_type);
CREATE INDEX IDX_FIN_ACCOUNT_NAME_AR ON fin_account (name_ar);
CREATE INDEX IDX_FIN_ACCOUNT_NAME_EN ON fin_account (name_en);
CREATE INDEX IDX_FIN_ACCOUNT_ACTIVE ON fin_account (is_active_fl);
CREATE INDEX IDX_FIN_DIMVAL_DIMENSION ON fin_dimension_value (dimension_id);
CREATE INDEX IDX_FIN_LKPVAL_TYPE ON fin_lookup_value (lookup_type_id);
CREATE INDEX IDX_FIN_EVENTRULE_TYPE ON fin_event_rule (event_type_code);
CREATE INDEX IDX_FIN_RULELINE_RULE ON fin_rule_line (event_rule_id);
CREATE INDEX IDX_FIN_RULELINE_ACCOUNT ON fin_rule_line (constant_account_id);
CREATE INDEX IDX_FIN_RLM_RULELINE ON fin_rule_line_mapping (rule_line_id);
CREATE INDEX IDX_FIN_RLM_DIMVAL ON fin_rule_line_mapping (resulting_dimension_value_id);
CREATE INDEX IDX_FIN_JE_NO ON fin_journal_entry (entry_no);
CREATE INDEX IDX_FIN_JE_DATE ON fin_journal_entry (entry_date);
CREATE INDEX IDX_FIN_JE_SOURCE ON fin_journal_entry (source_type_code);
CREATE INDEX IDX_FIN_JE_STATUS ON fin_journal_entry (status_code);
CREATE INDEX IDX_FIN_JE_PERIOD ON fin_journal_entry (period_id);
CREATE INDEX IDX_FIN_JE_FISCALYEAR ON fin_journal_entry (fiscal_year_id);
CREATE INDEX IDX_FIN_JE_REVERSALOF ON fin_journal_entry (reversal_of_entry_id);
CREATE INDEX IDX_FIN_JE_TEMPLATE ON fin_journal_entry (template_id);
CREATE INDEX IDX_FIN_JE_ALLOCRULE ON fin_journal_entry (allocation_rule_id);
CREATE INDEX IDX_FIN_JEL_ENTRY ON fin_journal_entry_line (journal_entry_id);
CREATE INDEX IDX_FIN_JEL_ACCOUNT ON fin_journal_entry_line (account_id);
CREATE INDEX IDX_FIN_JELDIM_LINE ON fin_journal_entry_line_dim (journal_entry_line_id);
CREATE INDEX IDX_FIN_JELDIM_DIMVAL ON fin_journal_entry_line_dim (dimension_value_id);
CREATE INDEX IDX_FIN_RT_NEXTRUN ON fin_recurring_template (next_run_date);
CREATE INDEX IDX_FIN_RTL_TEMPLATE ON fin_recurring_template_line (recurring_template_id);
CREATE INDEX IDX_FIN_RTL_ACCOUNT ON fin_recurring_template_line (account_id);
CREATE INDEX IDX_FIN_RTLDIM_LINE ON fin_recurring_template_line_dim (recurring_template_line_id);
CREATE INDEX IDX_FIN_ARULE_ACCOUNT ON fin_allocation_rule (source_account_id);
CREATE INDEX IDX_FIN_ARDIM_RULE ON fin_allocation_rule_dim (allocation_rule_id);
CREATE INDEX IDX_FIN_ARL_RULE ON fin_allocation_rule_line (allocation_rule_id);
CREATE INDEX IDX_FIN_ARL_ACCOUNT ON fin_allocation_rule_line (target_account_id);
CREATE INDEX IDX_FIN_ARLDIM_LINE ON fin_allocation_rule_line_dim (allocation_rule_line_id);
CREATE INDEX IDX_FIN_FP_FISCALYEAR ON fin_fiscal_period (fiscal_year_id);
CREATE INDEX IDX_FIN_FP_STATUS ON fin_fiscal_period (status_code);
CREATE INDEX IDX_FIN_FP_APPROVEDBY ON fin_fiscal_period (close_approved_by);
CREATE INDEX IDX_FIN_USER_USERNAME ON fin_user (username);
CREATE INDEX IDX_FIN_ROLEPERM_ROLE ON fin_role_permission (role_id);
CREATE INDEX IDX_FIN_ROLEPERM_PAGE ON fin_role_permission (page_code);
CREATE INDEX IDX_FIN_USERROLE_USER ON fin_user_role (user_id);
CREATE INDEX IDX_FIN_USERROLE_ROLE ON fin_user_role (role_id);

-- BLOCK 8 — LOOKUP SEED DATA (module-registry-fin.md "LOOKUPS OWNED"; business-policies-fin.md custom values)

INSERT INTO fin_lookup_type (lookup_key, name_ar, name_en, is_active_fl) VALUES
    ('payment-methods', 'طرق السداد', 'Payment methods', TRUE),
    ('accounting-event-types', 'أنواع الأحداث المحاسبية', 'Accounting event types', TRUE),
    ('account-types', 'أنواع الحسابات', 'Account types', TRUE),
    ('period-states', 'حالات الفترة', 'Period states', TRUE),
    ('journal-types', 'أنواع القيود', 'Journal types', TRUE);

INSERT INTO fin_lookup_value (lookup_type_id, value_code, label_ar, label_en, sort_order, is_active_fl)
SELECT lt.lookup_type_pk, v.value_code, v.label_ar, v.label_en, v.sort_order, TRUE
FROM fin_lookup_type lt
JOIN (VALUES
    ('account-types', 'asset',     'أصول',     'Asset',     1),
    ('account-types', 'liability', 'خصوم',     'Liability', 2),
    ('account-types', 'equity',    'حقوق ملكية','Equity',    3),
    ('account-types', 'revenue',   'إيرادات',  'Revenue',   4),
    ('account-types', 'expense',   'مصروفات',  'Expense',   5),
    ('period-states', 'OPEN',        'مفتوحة',        'Open',            1),
    ('period-states', 'SOFT_CLOSE',  'إقفال مبدئي',   'Soft Close',      2),
    ('period-states', 'HARD_CLOSE',  'إقفال نهائي',   'Hard Close',      3),
    ('journal-types', 'EVENT',       'من حدث',        'Event-generated', 1),
    ('journal-types', 'MANUAL',      'يدوي',          'Manual',          2),
    ('journal-types', 'RECURRING',   'متكرر/عكسي',    'Recurring/Reversing', 3),
    ('journal-types', 'ALLOCATION',  'توزيع',         'Allocation',      4),
    ('journal-types', 'VOID_CORRECTION', 'إلغاء/تصحيح','Void/Correction', 5)
) AS v(lookup_key, value_code, label_ar, label_en, sort_order) ON v.lookup_key = lt.lookup_key;

COMMIT;

-- BLOCK 9 — VIEWS
-- none required by the SRS at v1; reports (SCR-REQ-FIN-009..013) read the base
-- tables directly through the backend's query layer, per POL-FIN-009 (derived
-- from POSTED entries only, no materialized balance column).

-- BLOCK 10 — FUNCTIONS / PROCEDURES
-- fin_fn_check_entry_balance and fin_fn_block_posted_entry_edit are declared in BLOCK 6
-- (co-located with their triggers per this script's authoring convention; no other
-- function is required by the SRS at v1).

-- BLOCK 11 — DEFERRED FK PATCH BLOCKS
-- none: FIN declares zero XM records (fully isolated — SRS A8).
```

## 4 — DECISIONS APPLIED

| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| DEFAULT | Lookup-backed fields (`account_type`, `event_type_code`, `source_type_code`) store the lookup CODE as VARCHAR, never a numeric FK | brief §4.2 (profile rule: LOV runtime-loaded, no hardcoded enums) | fixed convention — no override |
| DEFAULT | Money/amount columns `NUMERIC(18,4)`; TIMESTAMPTZ for all dates, UTC | KB §6 | client-specific precision would be a new ADR |
| DEFAULT | Percentage-shaped values (`amount_operation_value`) `NUMERIC(9,4)` | domain best practice (KB §6 covers money only, not percentages) | — |
| DEFAULT | Small closed vocabularies intrinsic to this SRS's own design (nature, derivation type, direction, distribution type, statuses, permission action) implemented as `VARCHAR` + `CHECK`, not as `fin_lookup_value` rows | SRS A6 (already marked "fixed, not ENT-FIN-003 rows") | — |
| ADR-FIN-001 (carried from P1) | Recurring template `schedule_rule` is `TEXT`, data-defined, not an enumerated frequency | `decisions/FIN/ADR-FIN-001.md` | non-breaking — ACCEPTED |
| ADR-FIN-002 (carried from P1) | Rule-line mapping entries become their own child table `fin_rule_line_mapping`, still tracing to ENT-FIN-005, not a new ENT | `decisions/FIN/ADR-FIN-002.md` | non-breaking — ACCEPTED |
| ADR-FIN-003 (carried from P1) | Year-end close prerequisite (all periods Hard Closed) enforced at the application layer per RULE-FIN-010; no DB-level cross-period CHECK exists in postgresql16, so this is not a DDL constraint | `decisions/FIN/ADR-FIN-003.md` | non-breaking — ACCEPTED |
| ADR-FIN-004 (new, this stage) | Header-level debit=credit balance (RULE-FIN-002) enforced via a deferred constraint trigger, not a CHECK constraint (postgresql16 CHECK cannot aggregate sibling rows) | `decisions/FIN/ADR-FIN-004.md` | non-breaking — ACCEPTED |
| ADR-FIN-005 (new, this stage) | Posted-entry immutability (RULE-FIN-006) enforced via a `BEFORE UPDATE OR DELETE` trigger on `fin_journal_entry`, not application-only, closing the gap between "the API refuses it" and "the database refuses it" | `decisions/FIN/ADR-FIN-005.md` | non-breaking — ACCEPTED |

## 5 — REGISTRY CONTENT

See `registry-db-fin.md` for the structured registry ledger merged into
`project-registry.md` (CAT-5 structural registry, CAT-6 dependency index).
══════════════════════════════════════════════════════════════════
