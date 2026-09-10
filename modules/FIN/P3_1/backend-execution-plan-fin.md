<!-- P3.1 stage output — governed by factory.yaml stages[P3.1]; see shared/GOVERNANCE-CORE.md -->
# BACKEND EXECUTION PLAN — Finance / المحاسبة والمالية (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Dialect : postgresql16
Framework : spring-boot-java (profile.stack.backend.framework)
Date : 2026-09-10
══════════════════════════════════════════════════════════════════

## EXECUTION PLAN INDEX — FIN v1 — backend-execution-plan-fin.md
Profile: erp · dialect: postgresql16 · framework: spring-boot-java
Open ADRs: 0 (all 5 prior ADRs ACCEPTED; none opened at this stage)

ENTITY REGISTRY: 13 entities, ENT-FIN-001…013 → 24 tables (§ PHASE:DATA-DOM). No entity carries a business (document) number except ENT-FIN-006 Journal Entry (`entryNo`, platform numbering engine).

FIELD REGISTRY: 190 DBF-FIN-001…190 (db-script-fin.md) → all bound in the DB Alignment Manifest below.

API REGISTRY: 58 endpoints, API-FIN-001…058 (§ PHASE:SVC-API).

RULE REGISTRY: 14 RULE-FIN-001…014, all with ar+en messages ✓ (srs-fin.md A5) — every one cited in ≥1 API's Validations.

SCREEN REGISTRY: 16 screens, SCR-REQ-FIN-001…016 → 16 page codes in SEC_PAGES (§ PHASE:SEC-BE).

LOOKUP REGISTRY: payment-methods, accounting-event-types, account-types, period-states, journal-types — all FIN-owned (fin_lookup_type/fin_lookup_value); reused verbatim from db-script-fin.md, none re-created.

QRC SUMMARY: 58 QR-FIN-001…058, one per API (agent reference only — full catalog trailing this plan).

DB ALIGNMENT: see manifest below — ALIGNED ✓ (190/190), issues: 0.

XM STATUS: 0 — FIN declares zero cross-module dependencies (fully isolated, SRS A8; db-script-fin.md §2).

SECURITY: 16 screens × 5 roles (Accounting Configuration Administrator, Accountant, Financial Controller, Accounting System Administrator, Auditor).

## DB ALIGNMENT MANIFEST — FIN v1
Columns are sourced by lookup from `db-script-fin.md` only (column name, DB type, SRS reference are never reproduced here). Legend: ✓ aligned · ✗ type mismatch · ⏸ deferred XM. No ⏸ rows exist (0 XM).

| DBF-* | ENT-* | plan property | plan type (Java) | XM-* | status |
|---|---|---|---|---|---|
| DBF-FIN-001 | ENT-FIN-001 | accountPk | Long | — | ✓ |
| DBF-FIN-002 | ENT-FIN-001 | parentAccountId | Long | — | ✓ |
| DBF-FIN-003 | ENT-FIN-001 | code | String | — | ✓ |
| DBF-FIN-004 | ENT-FIN-001 | nameAr | String | — | ✓ |
| DBF-FIN-005 | ENT-FIN-001 | nameEn | String | — | ✓ |
| DBF-FIN-006 | ENT-FIN-001 | accountType | String | — | ✓ |
| DBF-FIN-007 | ENT-FIN-001 | natureCode | String | — | ✓ |
| DBF-FIN-008 | ENT-FIN-001 | acceptsDirectPostingFl | Boolean | — | ✓ |
| DBF-FIN-009 | ENT-FIN-001 | isRetainedEarningsAccountFl | Boolean | — | ✓ |
| DBF-FIN-010 | ENT-FIN-001 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-011 | ENT-FIN-001 | createdBy | String | — | ✓ |
| DBF-FIN-012 | ENT-FIN-001 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-013 | ENT-FIN-001 | updatedBy | String | — | ✓ |
| DBF-FIN-014 | ENT-FIN-001 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-015 | ENT-FIN-002 | dimensionPk | Long | — | ✓ |
| DBF-FIN-016 | ENT-FIN-002 | dimensionKey | String | — | ✓ |
| DBF-FIN-017 | ENT-FIN-002 | nameAr | String | — | ✓ |
| DBF-FIN-018 | ENT-FIN-002 | nameEn | String | — | ✓ |
| DBF-FIN-019 | ENT-FIN-002 | controlType | String | — | ✓ |
| DBF-FIN-020 | ENT-FIN-002 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-021 | ENT-FIN-002 | dimensionValuePk | Long | — | ✓ |
| DBF-FIN-022 | ENT-FIN-002 | dimensionId | Long | — | ✓ |
| DBF-FIN-023 | ENT-FIN-002 | valueCode | String | — | ✓ |
| DBF-FIN-024 | ENT-FIN-002 | valueNameAr | String | — | ✓ |
| DBF-FIN-025 | ENT-FIN-002 | valueNameEn | String | — | ✓ |
| DBF-FIN-026 | ENT-FIN-002 | sortOrder | Integer | — | ✓ |
| DBF-FIN-027 | ENT-FIN-002 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-028 | ENT-FIN-003 | lookupTypePk | Long | — | ✓ |
| DBF-FIN-029 | ENT-FIN-003 | lookupKey | String | — | ✓ |
| DBF-FIN-030 | ENT-FIN-003 | nameAr | String | — | ✓ |
| DBF-FIN-031 | ENT-FIN-003 | nameEn | String | — | ✓ |
| DBF-FIN-032 | ENT-FIN-003 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-033 | ENT-FIN-003 | lookupValuePk | Long | — | ✓ |
| DBF-FIN-034 | ENT-FIN-003 | lookupTypeId | Long | — | ✓ |
| DBF-FIN-035 | ENT-FIN-003 | valueCode | String | — | ✓ |
| DBF-FIN-036 | ENT-FIN-003 | labelAr | String | — | ✓ |
| DBF-FIN-037 | ENT-FIN-003 | labelEn | String | — | ✓ |
| DBF-FIN-038 | ENT-FIN-003 | sortOrder | Integer | — | ✓ |
| DBF-FIN-039 | ENT-FIN-003 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-040 | ENT-FIN-004 | eventRulePk | Long | — | ✓ |
| DBF-FIN-041 | ENT-FIN-004 | eventTypeCode | String | — | ✓ |
| DBF-FIN-042 | ENT-FIN-004 | nameAr | String | — | ✓ |
| DBF-FIN-043 | ENT-FIN-004 | nameEn | String | — | ✓ |
| DBF-FIN-044 | ENT-FIN-004 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-045 | ENT-FIN-004 | createdBy | String | — | ✓ |
| DBF-FIN-046 | ENT-FIN-004 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-047 | ENT-FIN-004 | updatedBy | String | — | ✓ |
| DBF-FIN-048 | ENT-FIN-004 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-049 | ENT-FIN-005 | ruleLinePk | Long | — | ✓ |
| DBF-FIN-050 | ENT-FIN-005 | eventRuleId | Long | — | ✓ |
| DBF-FIN-051 | ENT-FIN-005 | lineNo | Integer | — | ✓ |
| DBF-FIN-052 | ENT-FIN-005 | accountDerivationType | String | — | ✓ |
| DBF-FIN-053 | ENT-FIN-005 | constantAccountId | Long | — | ✓ |
| DBF-FIN-054 | ENT-FIN-005 | eventFieldName | String | — | ✓ |
| DBF-FIN-055 | ENT-FIN-005 | amountSourceField | String | — | ✓ |
| DBF-FIN-056 | ENT-FIN-005 | amountSourceOperation | String | — | ✓ |
| DBF-FIN-057 | ENT-FIN-005 | amountOperationValue | BigDecimal | — | ✓ |
| DBF-FIN-058 | ENT-FIN-005 | directionCode | String | — | ✓ |
| DBF-FIN-059 | ENT-FIN-005 | distributionType | String | — | ✓ |
| DBF-FIN-060 | ENT-FIN-005 | distributionValue | BigDecimal | — | ✓ |
| DBF-FIN-061 | ENT-FIN-005 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-062 | ENT-FIN-005 | ruleLineMappingPk | Long | — | ✓ |
| DBF-FIN-063 | ENT-FIN-005 | ruleLineId | Long | — | ✓ |
| DBF-FIN-064 | ENT-FIN-005 | eventAttributeName | String | — | ✓ |
| DBF-FIN-065 | ENT-FIN-005 | eventAttributeValue | String | — | ✓ |
| DBF-FIN-066 | ENT-FIN-005 | resultingDimensionValueId | Long | — | ✓ |
| DBF-FIN-067 | ENT-FIN-006 | journalEntryPk | Long | — | ✓ |
| DBF-FIN-068 | ENT-FIN-006 | entryNo | String | — | ✓ |
| DBF-FIN-069 | ENT-FIN-006 | entryDate | OffsetDateTime | — | ✓ |
| DBF-FIN-070 | ENT-FIN-006 | sourceTypeCode | String | — | ✓ |
| DBF-FIN-071 | ENT-FIN-006 | statusCode | String | — | ✓ |
| DBF-FIN-072 | ENT-FIN-006 | fiscalYearId | Long | — | ✓ |
| DBF-FIN-073 | ENT-FIN-006 | periodId | Long | — | ✓ |
| DBF-FIN-074 | ENT-FIN-006 | sourceEventReference | String | — | ✓ |
| DBF-FIN-075 | ENT-FIN-006 | templateId | Long | — | ✓ |
| DBF-FIN-076 | ENT-FIN-006 | allocationRuleId | Long | — | ✓ |
| DBF-FIN-077 | ENT-FIN-006 | reversalOfEntryId | Long | — | ✓ |
| DBF-FIN-078 | ENT-FIN-006 | reversedByEntryId | Long | — | ✓ |
| DBF-FIN-079 | ENT-FIN-006 | createdBy | String | — | ✓ |
| DBF-FIN-080 | ENT-FIN-006 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-081 | ENT-FIN-006 | updatedBy | String | — | ✓ |
| DBF-FIN-082 | ENT-FIN-006 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-083 | ENT-FIN-007 | journalEntryLinePk | Long | — | ✓ |
| DBF-FIN-084 | ENT-FIN-007 | journalEntryId | Long | — | ✓ |
| DBF-FIN-085 | ENT-FIN-007 | lineNo | Integer | — | ✓ |
| DBF-FIN-086 | ENT-FIN-007 | accountId | Long | — | ✓ |
| DBF-FIN-087 | ENT-FIN-007 | directionCode | String | — | ✓ |
| DBF-FIN-088 | ENT-FIN-007 | amount | BigDecimal | — | ✓ |
| DBF-FIN-089 | ENT-FIN-007 | descriptionAr | String | — | ✓ |
| DBF-FIN-090 | ENT-FIN-007 | descriptionEn | String | — | ✓ |
| DBF-FIN-091 | ENT-FIN-007 | journalEntryLineDimPk | Long | — | ✓ |
| DBF-FIN-092 | ENT-FIN-007 | journalEntryLineId | Long | — | ✓ |
| DBF-FIN-093 | ENT-FIN-007 | dimensionValueId | Long | — | ✓ |
| DBF-FIN-094 | ENT-FIN-008 | recurringTemplatePk | Long | — | ✓ |
| DBF-FIN-095 | ENT-FIN-008 | templateNameAr | String | — | ✓ |
| DBF-FIN-096 | ENT-FIN-008 | templateNameEn | String | — | ✓ |
| DBF-FIN-097 | ENT-FIN-008 | templateTypeCode | String | — | ✓ |
| DBF-FIN-098 | ENT-FIN-008 | scheduleRule | String | — | ✓ |
| DBF-FIN-099 | ENT-FIN-008 | nextRunDate | OffsetDateTime | — | ✓ |
| DBF-FIN-100 | ENT-FIN-008 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-101 | ENT-FIN-008 | createdBy | String | — | ✓ |
| DBF-FIN-102 | ENT-FIN-008 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-103 | ENT-FIN-008 | updatedBy | String | — | ✓ |
| DBF-FIN-104 | ENT-FIN-008 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-105 | ENT-FIN-008 | recurringTemplateLinePk | Long | — | ✓ |
| DBF-FIN-106 | ENT-FIN-008 | recurringTemplateId | Long | — | ✓ |
| DBF-FIN-107 | ENT-FIN-008 | lineNo | Integer | — | ✓ |
| DBF-FIN-108 | ENT-FIN-008 | accountId | Long | — | ✓ |
| DBF-FIN-109 | ENT-FIN-008 | amountSourceValue | BigDecimal | — | ✓ |
| DBF-FIN-110 | ENT-FIN-008 | amountSourceFormula | String | — | ✓ |
| DBF-FIN-111 | ENT-FIN-008 | directionCode | String | — | ✓ |
| DBF-FIN-112 | ENT-FIN-008 | recurringTemplateLineDimPk | Long | — | ✓ |
| DBF-FIN-113 | ENT-FIN-008 | recurringTemplateLineId | Long | — | ✓ |
| DBF-FIN-114 | ENT-FIN-008 | dimensionValueId | Long | — | ✓ |
| DBF-FIN-115 | ENT-FIN-009 | allocationRulePk | Long | — | ✓ |
| DBF-FIN-116 | ENT-FIN-009 | ruleNameAr | String | — | ✓ |
| DBF-FIN-117 | ENT-FIN-009 | ruleNameEn | String | — | ✓ |
| DBF-FIN-118 | ENT-FIN-009 | sourceAccountId | Long | — | ✓ |
| DBF-FIN-119 | ENT-FIN-009 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-120 | ENT-FIN-009 | createdBy | String | — | ✓ |
| DBF-FIN-121 | ENT-FIN-009 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-122 | ENT-FIN-009 | updatedBy | String | — | ✓ |
| DBF-FIN-123 | ENT-FIN-009 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-124 | ENT-FIN-009 | allocationRuleDimPk | Long | — | ✓ |
| DBF-FIN-125 | ENT-FIN-009 | allocationRuleId | Long | — | ✓ |
| DBF-FIN-126 | ENT-FIN-009 | dimensionValueId | Long | — | ✓ |
| DBF-FIN-127 | ENT-FIN-009 | allocationRuleLinePk | Long | — | ✓ |
| DBF-FIN-128 | ENT-FIN-009 | allocationRuleId | Long | — | ✓ |
| DBF-FIN-129 | ENT-FIN-009 | lineNo | Integer | — | ✓ |
| DBF-FIN-130 | ENT-FIN-009 | targetAccountId | Long | — | ✓ |
| DBF-FIN-131 | ENT-FIN-009 | distributionType | String | — | ✓ |
| DBF-FIN-132 | ENT-FIN-009 | distributionValue | BigDecimal | — | ✓ |
| DBF-FIN-133 | ENT-FIN-009 | allocationRuleLineDimPk | Long | — | ✓ |
| DBF-FIN-134 | ENT-FIN-009 | allocationRuleLineId | Long | — | ✓ |
| DBF-FIN-135 | ENT-FIN-009 | dimensionValueId | Long | — | ✓ |
| DBF-FIN-136 | ENT-FIN-010 | fiscalYearPk | Long | — | ✓ |
| DBF-FIN-137 | ENT-FIN-010 | yearCode | String | — | ✓ |
| DBF-FIN-138 | ENT-FIN-010 | nameAr | String | — | ✓ |
| DBF-FIN-139 | ENT-FIN-010 | nameEn | String | — | ✓ |
| DBF-FIN-140 | ENT-FIN-010 | startDate | OffsetDateTime | — | ✓ |
| DBF-FIN-141 | ENT-FIN-010 | endDate | OffsetDateTime | — | ✓ |
| DBF-FIN-142 | ENT-FIN-010 | statusCode | String | — | ✓ |
| DBF-FIN-143 | ENT-FIN-010 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-144 | ENT-FIN-010 | createdBy | String | — | ✓ |
| DBF-FIN-145 | ENT-FIN-010 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-146 | ENT-FIN-010 | updatedBy | String | — | ✓ |
| DBF-FIN-147 | ENT-FIN-010 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-148 | ENT-FIN-011 | fiscalPeriodPk | Long | — | ✓ |
| DBF-FIN-149 | ENT-FIN-011 | fiscalYearId | Long | — | ✓ |
| DBF-FIN-150 | ENT-FIN-011 | periodCode | String | — | ✓ |
| DBF-FIN-151 | ENT-FIN-011 | nameAr | String | — | ✓ |
| DBF-FIN-152 | ENT-FIN-011 | nameEn | String | — | ✓ |
| DBF-FIN-153 | ENT-FIN-011 | sequenceNo | Integer | — | ✓ |
| DBF-FIN-154 | ENT-FIN-011 | startDate | OffsetDateTime | — | ✓ |
| DBF-FIN-155 | ENT-FIN-011 | endDate | OffsetDateTime | — | ✓ |
| DBF-FIN-156 | ENT-FIN-011 | statusCode | String | — | ✓ |
| DBF-FIN-157 | ENT-FIN-011 | closeApprovedBy | Long | — | ✓ |
| DBF-FIN-158 | ENT-FIN-011 | closeApprovedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-159 | ENT-FIN-011 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-160 | ENT-FIN-011 | createdBy | String | — | ✓ |
| DBF-FIN-161 | ENT-FIN-011 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-162 | ENT-FIN-011 | updatedBy | String | — | ✓ |
| DBF-FIN-163 | ENT-FIN-011 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-164 | ENT-FIN-012 | userPk | Long | — | ✓ |
| DBF-FIN-165 | ENT-FIN-012 | username | String | — | ✓ |
| DBF-FIN-166 | ENT-FIN-012 | nameAr | String | — | ✓ |
| DBF-FIN-167 | ENT-FIN-012 | nameEn | String | — | ✓ |
| DBF-FIN-168 | ENT-FIN-012 | passwordHash | String | — | ✓ |
| DBF-FIN-169 | ENT-FIN-012 | lastLoginAt | OffsetDateTime | — | ✓ |
| DBF-FIN-170 | ENT-FIN-012 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-171 | ENT-FIN-012 | createdBy | String | — | ✓ |
| DBF-FIN-172 | ENT-FIN-012 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-173 | ENT-FIN-012 | updatedBy | String | — | ✓ |
| DBF-FIN-174 | ENT-FIN-012 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-175 | ENT-FIN-013 | rolePk | Long | — | ✓ |
| DBF-FIN-176 | ENT-FIN-013 | roleCode | String | — | ✓ |
| DBF-FIN-177 | ENT-FIN-013 | roleNameAr | String | — | ✓ |
| DBF-FIN-178 | ENT-FIN-013 | roleNameEn | String | — | ✓ |
| DBF-FIN-179 | ENT-FIN-013 | isActiveFl | Boolean | — | ✓ |
| DBF-FIN-180 | ENT-FIN-013 | createdBy | String | — | ✓ |
| DBF-FIN-181 | ENT-FIN-013 | createdAt | OffsetDateTime | — | ✓ |
| DBF-FIN-182 | ENT-FIN-013 | updatedBy | String | — | ✓ |
| DBF-FIN-183 | ENT-FIN-013 | updatedAt | OffsetDateTime | — | ✓ |
| DBF-FIN-184 | ENT-FIN-013 | rolePermissionPk | Long | — | ✓ |
| DBF-FIN-185 | ENT-FIN-013 | roleId | Long | — | ✓ |
| DBF-FIN-186 | ENT-FIN-013 | pageCode | String | — | ✓ |
| DBF-FIN-187 | ENT-FIN-013 | actionCode | String | — | ✓ |
| DBF-FIN-188 | ENT-FIN-013 | userRolePk | Long | — | ✓ |
| DBF-FIN-189 | ENT-FIN-013 | userId | Long | — | ✓ |
| DBF-FIN-190 | ENT-FIN-013 | roleId | Long | — | ✓ |

Total: 190/190 bound, 0 mismatches, 0 deferred.

<!-- PHASE:CORE:START traces=REQ-FIN-001,REQ-FIN-018,REQ-FIN-025 -->
## PHASE 1 — CORE (architecture policies, declared once)

**Layers**: `controller → service → mapper → domain → repository` (profile.stack.backend.layers).
Controller: HTTP binding, DTO validation annotations, permission gate only — never business logic.
Service: orchestration (load → validate RULE-* → integrate → persist), transaction boundary owner.
Mapper: DTO ↔ domain, one mapper per aggregate root (Account, Dimension, LookupType, EventRule, JournalEntry, RecurringTemplate, AllocationRule, FiscalYear, FiscalPeriod, User, Role).
Domain: RULE-* enforcement lives in domain methods on the aggregate root (e.g. `JournalEntry.post()` runs RULE-FIN-001…004 before flipping `statusCode`), never in the controller.
Repository: one Spring Data repository per table; QR-FIN-* entries are the logical spec every repository method implements.

**Error signalling**: `LocalizedException → {code, messageAr, messageEn}` (profile.stack.backend.api.error_envelope). Runtime `code` format: `FIN-<RULE-seq|PLATFORM>-<3-digit>`, e.g. `FIN-RULE-002` for RULE-FIN-002, `FIN-PLATFORM-404` for a not-found. Every thrown exception carries this triple; the HTTP layer maps it to the catalog's HTTP status (§ Error Catalog, trailing this plan).

**Transaction defaults**: `READ_ONLY` on every GET/search/read method; `READ_WRITE` on every mutation; a multi-table write (e.g. build entry header + lines, then post) is one `@Transactional` boundary at the service method so the deferred balance trigger (ADR-FIN-004) evaluates once at commit.

**Search contract**: request = `{filters: {field: value}, sort: [{field, direction}], page, size}`; allowed sort fields = the columns listed as filters in each SRS PART B §B2; paging wraps in `Page<T>` (profile.stack.backend.api.paging); default page size 20, max 200 (KB §6).

**Audit fields**: `createdBy, createdAt, updatedBy, updatedAt` are framework-filled (Spring Data auditing) on every table that carries them (db-script-fin.md) — never present in a create/update request DTO, never set by a mapper or service method.

**Type mapping** (`profile.stack.db.syntax_map`, postgresql16 → Java):
| postgresql16 | Java |
|---|---|
| GENERATED ALWAYS AS IDENTITY | Long |
| VARCHAR(n) / TEXT | String |
| BOOLEAN | Boolean |
| TIMESTAMPTZ | OffsetDateTime |
| NUMERIC(p,s) | BigDecimal |

**Lookup values**: every lookup-backed property (`accountType`, `eventTypeCode`, `sourceTypeCode`, and every `*Code` field backed by a fixed vocabulary in db-script-fin.md §5c) is a `String` holding the stored code; the frontend resolves the display label — no hardcoded enum in a request/response DTO, no hardcoded enum in an API definition (profile.conventions.lookups).

**Numbering**: `entryNo` (ENT-FIN-006, DBF-FIN-068) is issued by the platform numbering engine at first save, read-only after (profile.conventions.numbering) — FIN's own code never generates it.

**Workflow engine**: forbidden (profile.conventions.workflow_engine) — status lifecycles (A7) are plain `statusCode` fields with domain-method-enforced transitions, never a BPM/workflow library.

**Languages**: every `nameAr/nameEn`, `labelAr/labelEn`, `descriptionAr/descriptionEn` pair is present in every create/update/response DTO; a response missing either language for a bilingual field is a review finding.

**Cross-module contract placement**: not applicable — FIN declares zero XM (PHASE:INT-C / PHASE:INT-R below are empty by design).

**Inbound event entry point (non-REST)**: the canonical accounting event (plan §0) arrives through the out-of-scope Event consumer, not as a FIN REST endpoint — no `API-FIN-*` marker applies. It is a service-layer listener (`AccountingEventListener`, package `fin.service.event`) that: (1) resolves the event's `eventType` to `ENT-FIN-004` via `eventTypeCode` (QR-FIN-016 FIND_ONE), (2) builds a `JournalEntry` (`sourceTypeCode='EVENT'`) from the matched rule's lines (REQ-FIN-014), (3) calls the same `JournalEntry.post()` domain method every other source uses (REQ-FIN-018, REQ-FIN-020) — one posting path for all four sources, never a source-specific shortcut.
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=REQ-FIN-001,REQ-FIN-004,REQ-FIN-006,REQ-FIN-008,REQ-FIN-009,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-027,REQ-FIN-025 -->
## PHASE 2 — DATA-DOM (data + domain, one block per ENT-*)

### ENT-FIN-001 — Chart of Account      kind: master
BINDINGS   table `fin_account` · PK `account_pk` (DBF-FIN-001) · PK generation `GENERATED ALWAYS AS IDENTITY` · db-script-fin.md v1
BUSINESS CODE   none — `code` (DBF-FIN-003) is an internal unique key, not an external-reference business number (SRS A3 §3.3 test fails a/b/c)
DEFAULT FIELDS (master)   nameAr, nameEn, code, isActiveFl, createdBy, createdAt, updatedBy, updatedAt — all present (DBF-FIN-003,004,005,010,011,012,013,014)
FIELDS     DBF-FIN-001 accountPk/Long/NOT NULL/read-only/PK; DBF-FIN-002 parentAccountId/Long/nullable/writable/FK self; DBF-FIN-003 code/String/NOT NULL/writable/UQ_FIN_ACCOUNT_CODE (ar/en: رمز الحساب/Account code); DBF-FIN-004/005 nameAr/nameEn/String/NOT NULL/writable (اسم الحساب/Account name); DBF-FIN-006 accountType/String/NOT NULL/writable/lookup key `account-types` (نوع الحساب/Account type); DBF-FIN-007 natureCode/String/NOT NULL/writable/CHK_FIN_ACCOUNT_NATURE (طبيعة الحساب/Account nature); DBF-FIN-008 acceptsDirectPostingFl/Boolean/NOT NULL/writable (يقبل الترحيل المباشر/Accepts direct posting); DBF-FIN-009 isRetainedEarningsAccountFl/Boolean/NOT NULL/writable/RULE-FIN-011 (حساب الأرباح المحتجزة/Retained-earnings account); DBF-FIN-010 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-011…014 audit/read-only
DTO MEMBERSHIP   create-request excludes: accountPk, createdBy/At, updatedBy/At · update-request excludes: accountPk, code (immutable after create — business key), createdBy/At, updatedBy/At · response includes: all fields
LOOKUP FIELDS   accountType │ DBF-FIN-006 │ key `account-types` │ GET /api/v1/fin/lookups?lookupKey=account-types
DOMAIN RULES   RULE-FIN-001 "Prevent posting to an account when it is inactive or does not accept direct posting" · trigger: on post · message ar: لا يمكن الترحيل إلى حساب غير نشط أو غير قابل للترحيل المباشر · en: Cannot post to an inactive or non-postable account · scope: journal-entry-line creation (ALL) · DB enforcement: app-level (validated in `JournalEntry.post()`, no DB constraint spans two tables) · owner layer: domain. RULE-FIN-011 "Require exactly one active account flagged isRetainedEarningsAccountFl at year-end close time" · trigger: on account save / year-end close · message ar: يجب تحديد حساب واحد فقط للأرباح المحتجزة · en: Exactly one Retained Earnings account must be designated · scope: CREATE|UPDATE (this entity) + year-end close (ALL) · DB enforcement: app-level (a partial unique index cannot express "at most one TRUE" portably across postgresql16/oracle19c — deviation noted, no ADR needed: standard app-level uniqueness-of-flag pattern) · owner layer: domain
STATE MACHINE   not applicable — no status field on Account
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-001 SAVE, QR-FIN-002 FIND_BY_CRITERIA, QR-FIN-003 FIND_ONE, QR-FIN-004 UPDATE, QR-FIN-005 UPDATE (deactivate)

### ENT-FIN-002 — Account Dimension (definition + values)      kind: config
BINDINGS   tables `fin_dimension` (definition, PK `dimension_pk`/DBF-FIN-015) + `fin_dimension_value` (values, PK `dimension_value_pk`/DBF-FIN-021) · PK generation `GENERATED ALWAYS AS IDENTITY` (both) · db-script-fin.md v1
BUSINESS CODE   none
DEFAULT FIELDS (config)   key→dimensionKey, valueAr→nameAr, valueEn→nameEn, isActiveFl — present (DBF-FIN-016,017,018,020)
FIELDS     DBF-FIN-015 dimensionPk/Long/read-only/PK; DBF-FIN-016 dimensionKey/String/NOT NULL/writable/UQ_FIN_DIMENSION_KEY (مفتاح البُعد/Dimension key); DBF-FIN-017/018 nameAr/nameEn/String/NOT NULL/writable; DBF-FIN-019 controlType/String/NOT NULL/writable/CHK_FIN_DIMENSION_CONTROL (نوع الضبط/Control type); DBF-FIN-020 isActiveFl/Boolean/NOT NULL/writable — value sub-shape: DBF-FIN-021 dimensionValuePk/Long/read-only/PK; DBF-FIN-022 dimensionId/Long/NOT NULL/writable/FK; DBF-FIN-023 valueCode/String/NOT NULL/writable/UQ per dimension; DBF-FIN-024/025 valueNameAr/valueNameEn/String/NOT NULL/writable; DBF-FIN-026 sortOrder/Integer/nullable/writable; DBF-FIN-027 isActiveFl/Boolean/NOT NULL/writable
DTO MEMBERSHIP   create/update-request: dimensionKey (create-only), nameAr, nameEn, controlType, values[] (nested: valueCode, valueNameAr, valueNameEn, sortOrder) · response includes all + values[] with dimensionValuePk
LOOKUP FIELDS   none (Dimension is its own reference system, not a `fin_lookup_*` consumer — SRS A6)
DOMAIN RULES   RULE-FIN-003 "Prevent posting a line whose dimension value is inactive or does not belong to the dimension configured for that segment" · trigger: on post · message ar: قيمة البُعد غير صالحة أو غير نشطة · en: Dimension value is invalid or inactive · scope: journal-entry-line creation (ALL) · DB enforcement: app-level (join validated in `JournalEntry.post()`) · owner layer: domain
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-006 SAVE, QR-FIN-007 FIND_BY_CRITERIA, QR-FIN-008 FIND_ONE, QR-FIN-009 UPDATE, QR-FIN-010 UPDATE (deactivate)

### ENT-FIN-003 — Accounting Reference List (lookup type + values)      kind: lookup
BINDINGS   tables `fin_lookup_type` (PK `lookup_type_pk`/DBF-FIN-028) + `fin_lookup_value` (PK `lookup_value_pk`/DBF-FIN-033) · identity PKs · db-script-fin.md v1
BUSINESS CODE   none
DEFAULT FIELDS (lookup)   code→lookupKey/valueCode, nameAr/nameEn or labelAr/labelEn, sortOrder, isActiveFl — present
FIELDS     DBF-FIN-028 lookupTypePk/Long/read-only/PK; DBF-FIN-029 lookupKey/String/NOT NULL/writable/UQ_FIN_LOOKUP_TYPE_KEY; DBF-FIN-030/031 nameAr/nameEn/String/NOT NULL/writable — value sub-shape: DBF-FIN-033 lookupValuePk/Long/read-only/PK; DBF-FIN-034 lookupTypeId/Long/NOT NULL/writable/FK; DBF-FIN-035 valueCode/String/NOT NULL/writable/UQ per type; DBF-FIN-036/037 labelAr/labelEn/String/NOT NULL/writable; DBF-FIN-038 sortOrder/Integer/nullable/writable; DBF-FIN-032,039 isActiveFl/Boolean/NOT NULL/writable
DTO MEMBERSHIP   create/update-request: lookupKey (create-only), nameAr, nameEn, values[] (nested: valueCode, labelAr, labelEn, sortOrder) · response includes all + values[]
LOOKUP FIELDS   this IS the lookup system that other entities' lookup-backed fields point to by key (SRS A6) — not itself a consumer
DOMAIN RULES   none SRS-declared beyond standard uniqueness (UQ constraints, no RULE-* id)
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-011 SAVE, QR-FIN-012 FIND_BY_CRITERIA, QR-FIN-013 FIND_ONE, QR-FIN-014 UPDATE, QR-FIN-015 UPDATE (deactivate)

### ENT-FIN-004 — Event-Type Rule      kind: config
BINDINGS   table `fin_event_rule` · PK `event_rule_pk` (DBF-FIN-040) · identity · db-script-fin.md v1
BUSINESS CODE   none
FIELDS     DBF-FIN-040 eventRulePk/Long/read-only/PK; DBF-FIN-041 eventTypeCode/String/NOT NULL/writable/UQ_FIN_EVENT_RULE_TYPE (lookup key `accounting-event-types`) (نوع الحدث/Event type); DBF-FIN-042/043 nameAr/nameEn/String/NOT NULL/writable; DBF-FIN-044 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-045…048 audit/read-only
DTO MEMBERSHIP   create-request excludes eventRulePk, audit · update-request excludes eventRulePk, eventTypeCode (immutable), audit · response includes all + lines[]
LOOKUP FIELDS   eventTypeCode │ DBF-FIN-041 │ key `accounting-event-types` │ GET /api/v1/fin/lookups?lookupKey=accounting-event-types
DOMAIN RULES   RULE-FIN-012 "Prevent activating a second rule for an event type that already has an active rule" · trigger: on rule save · message ar: يوجد بالفعل قاعدة نشطة لهذا النوع من الأحداث · en: An active rule already exists for this event type · scope: CREATE|UPDATE (this entity) · DB enforcement: UQ_FIN_EVENT_RULE_TYPE (constraint, not conditional on isActiveFl — app-level check refines to "active" specifically) · owner layer: domain
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-016 FIND_ONE (by eventTypeCode, used by the event listener too), QR-FIN-017 FIND_BY_CRITERIA, QR-FIN-018 FIND_ONE (by PK), QR-FIN-019 UPDATE, QR-FIN-020 UPDATE (deactivate)

### ENT-FIN-005 — Rule Line      kind: config
BINDINGS   tables `fin_rule_line` (PK `rule_line_pk`/DBF-FIN-049) + `fin_rule_line_mapping` (PK `rule_line_mapping_pk`/DBF-FIN-062, ADR-FIN-002) · identity PKs · db-script-fin.md v1
BUSINESS CODE   none
FIELDS     DBF-FIN-049 ruleLinePk/Long/read-only/PK; DBF-FIN-050 eventRuleId/Long/NOT NULL/writable/FK; DBF-FIN-051 lineNo/Integer/NOT NULL/writable; DBF-FIN-052 accountDerivationType/String/NOT NULL/writable/CHK (CONSTANT|EVENT_FIELD|MAPPING_SET); DBF-FIN-053 constantAccountId/Long/nullable/writable/FK; DBF-FIN-054 eventFieldName/String/nullable/writable; DBF-FIN-055 amountSourceField/String/NOT NULL/writable; DBF-FIN-056 amountSourceOperation/String/NOT NULL/writable/CHK (DIRECT|PERCENTAGE|REMAINDER); DBF-FIN-057 amountOperationValue/BigDecimal/nullable/writable; DBF-FIN-058 directionCode/String/NOT NULL/writable/CHK (DEBIT|CREDIT); DBF-FIN-059 distributionType/String/NOT NULL/writable/CHK (FIXED|PERCENTAGE|REMAINDER); DBF-FIN-060 distributionValue/BigDecimal/nullable/writable; DBF-FIN-061 isActiveFl/Boolean/NOT NULL/writable — mapping sub-shape: DBF-FIN-062 ruleLineMappingPk/Long/read-only/PK; DBF-FIN-063 ruleLineId/Long/NOT NULL/writable/FK; DBF-FIN-064 eventAttributeName/String/NOT NULL/writable; DBF-FIN-065 eventAttributeValue/String/NOT NULL/writable; DBF-FIN-066 resultingDimensionValueId/Long/NOT NULL/writable/FK
DTO MEMBERSHIP   nested in Event-Type Rule's create/update request (no standalone Rule Line endpoint — aggregate root pattern, R1) · response nested under the rule response
LOOKUP FIELDS   none directly (accountType/direction/derivation-type are fixed CHECK vocabularies per db-script-fin.md §Decisions Applied, not `fin_lookup_value` rows)
DOMAIN RULES   RULE-FIN-005 "Apply fixed-amount lines first, then percentage lines against the remaining amount rounded to the smallest currency unit, then assign the exact difference to the single remainder line" · trigger: on entry build / allocation run · message ar: يجب وجود سطر متبقي واحد فقط لاستيعاب فرق التقريب · en: Exactly one remainder line is required to absorb the rounding difference · scope: rule-line save (CREATE|UPDATE) + entry-build time (ALL) · DB enforcement: app-level (aggregate arithmetic, no single-row CHECK possible) · owner layer: domain
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   folded into QR-FIN-016…020 (Event-Type Rule aggregate save/update persists its lines and mapping entries in the same transaction)

### ENT-FIN-006 — Journal Entry      kind: transactional
BINDINGS   table `fin_journal_entry` · PK `journal_entry_pk` (DBF-FIN-067) · identity · db-script-fin.md v1
BUSINESS CODE   property `entryNo` · column `entry_no` (DBF-FIN-068) · format: platform numbering engine format (profile-level, not FIN-specific) · uniqueness constraint `UQ_FIN_JOURNAL_ENTRY_NO` · generation source: platform numbering engine, called from the service layer on first save, never the database and never FIN's own code (profile.conventions.numbering)
DEFAULT FIELDS (transactional)   docNo→entryNo, docDate→entryDate, statusCode, fiscalYearId, periodId, createdBy, createdAt, updatedBy, updatedAt — all present (DBF-FIN-068,069,071,072,073,079,080,081,082)
FIELDS     DBF-FIN-067 journalEntryPk/Long/read-only/PK; DBF-FIN-068 entryNo/String/NOT NULL/read-only-after-create; DBF-FIN-069 entryDate/OffsetDateTime/NOT NULL/writable; DBF-FIN-070 sourceTypeCode/String/NOT NULL/read-only (system-set from the creating operation, lookup key `journal-types`); DBF-FIN-071 statusCode/String/NOT NULL/read-only (system-set by `post()`, never client-set — A7); DBF-FIN-072/073 fiscalYearId/periodId/Long/NOT NULL/writable(create only); DBF-FIN-074 sourceEventReference/String/nullable/read-only; DBF-FIN-075 templateId/Long/nullable/read-only; DBF-FIN-076 allocationRuleId/Long/nullable/read-only; DBF-FIN-077 reversalOfEntryId/Long/nullable/read-only; DBF-FIN-078 reversedByEntryId/Long/nullable/read-only (system-set when reversed); DBF-FIN-079…082 audit/read-only
DTO MEMBERSHIP   create-request (manual only, API-FIN-032): entryDate, periodId, lines[] · excludes: journalEntryPk, entryNo, sourceTypeCode (system='MANUAL'), statusCode, reversal fields, audit · response includes all + lines[]
LOOKUP FIELDS   sourceTypeCode │ DBF-FIN-070 │ key `journal-types` │ GET /api/v1/fin/lookups?lookupKey=journal-types
DOMAIN RULES   RULE-FIN-002 (debits=credits, ADR-FIN-004 deferred trigger) · RULE-FIN-004 "Prevent posting a normal entry to a period that is not Open" trigger: on post · ar: الفترة غير مفتوحة للترحيل · en: Period is not open for posting · scope: post (ALL) · DB enforcement: app-level (reads `fin_fiscal_period.status_code`) · owner layer: domain · RULE-FIN-006 (posted immutable, ADR-FIN-005 DB trigger) · RULE-FIN-007 "Require every Void/Correction entry to carry a reversalOfEntryId pointing to the entry it corrects" trigger: on reversal creation · ar: يجب ربط قيد العكس بالقيد الأصلي · en: A reversing entry must reference the original entry · scope: reversal create (CREATE) · DB enforcement: app-level (FK is nullable — only enforced NOT NULL when sourceTypeCode='VOID_CORRECTION', a conditional constraint expressed in the domain layer, not DDL) · owner layer: domain
STATE MACHINE   status column DBF-FIN-071 (`statusCode`) · values DRAFT, POSTED · initial DRAFT · transitions: DRAFT→POSTED (trigger: automatic validation passes, actor: system, RULE-FIN-001…004) · terminal: POSTED · invalid-transition RULE: RULE-FIN-006 (no transition out of POSTED)
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-032 SAVE (manual create), QR-FIN-033 FIND_BY_CRITERIA, QR-FIN-034 FIND_ONE, QR-FIN-035 SAVE (reversal, creates a linked new row)

### ENT-FIN-007 — Journal Entry Line      kind: transactional
BINDINGS   tables `fin_journal_entry_line` (PK `journal_entry_line_pk`/DBF-FIN-083) + `fin_journal_entry_line_dim` (PK `journal_entry_line_dim_pk`/DBF-FIN-091) · identity PKs · db-script-fin.md v1
BUSINESS CODE   none (child of a numbered document)
FIELDS     DBF-FIN-083 journalEntryLinePk/Long/read-only/PK; DBF-FIN-084 journalEntryId/Long/NOT NULL/read-only(set from parent); DBF-FIN-085 lineNo/Integer/NOT NULL/writable; DBF-FIN-086 accountId/Long/NOT NULL/writable/FK; DBF-FIN-087 directionCode/String/NOT NULL/writable/CHK; DBF-FIN-088 amount/BigDecimal/NOT NULL/writable/CHK(amount>0); DBF-FIN-089/090 descriptionAr/descriptionEn/String/nullable/writable — dim sub-shape: DBF-FIN-091 journalEntryLineDimPk/Long/read-only/PK; DBF-FIN-092 journalEntryLineId/Long/NOT NULL/writable/FK; DBF-FIN-093 dimensionValueId/Long/NOT NULL/writable/FK, UQ per line
DTO MEMBERSHIP   nested in Journal Entry's create request (`lines[]`): accountId, dimensionValueIds[], directionCode, amount, descriptionAr, descriptionEn · excludes journalEntryLinePk, journalEntryId · response nested under the entry response
LOOKUP FIELDS   none directly (directionCode is a fixed CHECK vocabulary)
DOMAIN RULES   RULE-FIN-001 (leaf/active posting, see ENT-FIN-001) · RULE-FIN-003 (dimension validity, see ENT-FIN-002)
STATE MACHINE   not applicable (inherits the header's statusCode; RULE-FIN-006 blocks direct edit once POSTED)
CROSS-MODULE   none
REPOSITORY OPS   folded into QR-FIN-032/035 (lines persist in the same transaction as their header)

### ENT-FIN-008 — Recurring-Reversing Entry Template      kind: config
BINDINGS   tables `fin_recurring_template` (PK `recurring_template_pk`/DBF-FIN-094) + `fin_recurring_template_line` (PK `recurring_template_line_pk`/DBF-FIN-105) + `fin_recurring_template_line_dim` (PK `recurring_template_line_dim_pk`/DBF-FIN-112) · identity PKs · db-script-fin.md v1
BUSINESS CODE   none
FIELDS     DBF-FIN-094 recurringTemplatePk/Long/read-only/PK; DBF-FIN-095/096 templateNameAr/templateNameEn/String/NOT NULL/writable; DBF-FIN-097 templateTypeCode/String/NOT NULL/writable/CHK (RECURRING|REVERSING); DBF-FIN-098 scheduleRule/String/NOT NULL/writable (ADR-FIN-001, data-defined); DBF-FIN-099 nextRunDate/OffsetDateTime/NOT NULL/read-only(system-advanced after each run); DBF-FIN-100 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-101…104 audit/read-only — line sub-shape: DBF-FIN-105 recurringTemplateLinePk/Long/read-only/PK; DBF-FIN-106 recurringTemplateId/Long/NOT NULL/writable/FK; DBF-FIN-107 lineNo/Integer/NOT NULL/writable; DBF-FIN-108 accountId/Long/NOT NULL/writable/FK; DBF-FIN-109 amountSourceValue/BigDecimal/nullable/writable; DBF-FIN-110 amountSourceFormula/String/nullable/writable; DBF-FIN-111 directionCode/String/NOT NULL/writable/CHK — dim sub-shape: DBF-FIN-112…114, same shape as ENT-FIN-007's line-dim
DTO MEMBERSHIP   create/update-request: templateNameAr/En, templateTypeCode, scheduleRule, lines[] (accountId, dimensionValueIds[], amountSourceValue|amountSourceFormula, directionCode) · excludes recurringTemplatePk, nextRunDate (system), audit · response includes all + lines[]
LOOKUP FIELDS   none directly
DOMAIN RULES   RULE-FIN-013 "Skip generating an entry from a template whose target account is inactive at run time, and flag it for review" · trigger: on scheduled run · message ar: تم تخطي القالب — الحساب غير نشط · en: Template skipped — account is inactive · scope: scheduled run (ALL) · DB enforcement: app-level (the scheduler job) · owner layer: domain (scheduler service, package `fin.service.scheduler`)
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-021 SAVE, QR-FIN-022 FIND_BY_CRITERIA, QR-FIN-023 FIND_ONE, QR-FIN-024 UPDATE, QR-FIN-025 UPDATE (deactivate); scheduler additionally uses QR-FIN-022-shaped query filtered by `next_run_date <= now()` (same QR, different filter values — no new id)

### ENT-FIN-009 — Allocation Rule      kind: config
BINDINGS   tables `fin_allocation_rule` (PK `allocation_rule_pk`/DBF-FIN-115) + `fin_allocation_rule_dim` (PK `allocation_rule_dim_pk`/DBF-FIN-124) + `fin_allocation_rule_line` (PK `allocation_rule_line_pk`/DBF-FIN-127) + `fin_allocation_rule_line_dim` (PK `allocation_rule_line_dim_pk`/DBF-FIN-133) · identity PKs · db-script-fin.md v1
BUSINESS CODE   none
FIELDS     DBF-FIN-115 allocationRulePk/Long/read-only/PK; DBF-FIN-116/117 ruleNameAr/ruleNameEn/String/NOT NULL/writable; DBF-FIN-118 sourceAccountId/Long/NOT NULL/writable/FK; DBF-FIN-119 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-120…123 audit/read-only — source-dim sub-shape DBF-FIN-124…126; line sub-shape: DBF-FIN-127 allocationRuleLinePk/Long/read-only/PK; DBF-FIN-128 allocationRuleId/Long/NOT NULL/writable/FK; DBF-FIN-129 lineNo/Integer/NOT NULL/writable; DBF-FIN-130 targetAccountId/Long/NOT NULL/writable/FK; DBF-FIN-131 distributionType/String/NOT NULL/writable/CHK; DBF-FIN-132 distributionValue/BigDecimal/nullable/writable — line-dim sub-shape DBF-FIN-133…135
DTO MEMBERSHIP   create/update-request: ruleNameAr/En, sourceAccountId, sourceDimensionValueIds[], lines[] (targetAccountId, targetDimensionValueIds[], distributionType, distributionValue) · excludes allocationRulePk, audit · response includes all + lines[]
LOOKUP FIELDS   none directly
DOMAIN RULES   RULE-FIN-014 "Require an allocation rule's lines, applying the same fixed→percentage→remainder order as RULE-FIN-005, to total exactly the source balance being distributed" · trigger: on allocation run · message ar: يجب أن يساوي مجموع سطور التوزيع رصيد المصدر بالكامل · en: Allocation lines must total exactly the source balance · scope: run (ALL) · DB enforcement: app-level · owner layer: domain
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-026 SAVE, QR-FIN-027 FIND_BY_CRITERIA, QR-FIN-028 FIND_ONE, QR-FIN-029 UPDATE, QR-FIN-030 UPDATE (deactivate), QR-FIN-031 SAVE (run → generates a Journal Entry via QR-FIN-032's persistence path)

### ENT-FIN-010 — Fiscal Year      kind: master
BINDINGS   table `fin_fiscal_year` · PK `fiscal_year_pk` (DBF-FIN-136) · identity · db-script-fin.md v1
BUSINESS CODE   none
DEFAULT FIELDS (master)   nameAr, nameEn, code→yearCode, isActiveFl, createdBy, createdAt, updatedBy, updatedAt — present
FIELDS     DBF-FIN-136 fiscalYearPk/Long/read-only/PK; DBF-FIN-137 yearCode/String/NOT NULL/writable(create-only)/UQ; DBF-FIN-138/139 nameAr/nameEn/String/nullable/writable; DBF-FIN-140/141 startDate/endDate/OffsetDateTime/NOT NULL/writable(create-only); DBF-FIN-142 statusCode/String/NOT NULL/read-only(system-set by close actions — A7); DBF-FIN-143 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-144…147 audit/read-only
DTO MEMBERSHIP   create-request: yearCode, nameAr, nameEn, startDate, endDate, periods[] (nested, generates fiscal_period rows) · excludes fiscalYearPk, statusCode, audit · response includes all + periods[]
LOOKUP FIELDS   none
DOMAIN RULES   RULE-FIN-010 "Prevent year-end close of a fiscal year until every one of its periods is Hard Closed" (ADR-FIN-003) · trigger: on year-end close attempt · ar: يجب إقفال جميع فترات السنة إقفالاً نهائياً أولاً · en: All periods of the year must be Hard Closed first · scope: year-end-close (ALL) · DB enforcement: app-level (cross-row check across `fin_fiscal_period`) · owner layer: domain
STATE MACHINE   status column DBF-FIN-142 · values OPEN, YEAR_END_CLOSED · initial OPEN · transitions: OPEN→YEAR_END_CLOSED (trigger: year-end close, actor: Financial Controller, RULE-FIN-010, RULE-FIN-011) · terminal: YEAR_END_CLOSED · invalid-transition RULE: RULE-FIN-010
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-036 SAVE, QR-FIN-037 FIND_BY_CRITERIA, QR-FIN-038 FIND_ONE, QR-FIN-040 UPDATE (year-end close, plus generates the carryforward entry via QR-FIN-032's persistence path)

### ENT-FIN-011 — Fiscal Period      kind: master
BINDINGS   table `fin_fiscal_period` · PK `fiscal_period_pk` (DBF-FIN-148) · identity · db-script-fin.md v1
BUSINESS CODE   none
DEFAULT FIELDS (master)   nameAr, nameEn, code→periodCode, isActiveFl, createdBy, createdAt, updatedBy, updatedAt — present
FIELDS     DBF-FIN-148 fiscalPeriodPk/Long/read-only/PK; DBF-FIN-149 fiscalYearId/Long/NOT NULL/writable(create-only)/FK; DBF-FIN-150 periodCode/String/NOT NULL/writable(create-only)/UQ per year; DBF-FIN-151/152 nameAr/nameEn/String/nullable/writable; DBF-FIN-153 sequenceNo/Integer/NOT NULL/writable(create-only); DBF-FIN-154/155 startDate/endDate/OffsetDateTime/NOT NULL/writable(create-only); DBF-FIN-156 statusCode/String/NOT NULL/read-only(system-set by close actions); DBF-FIN-157 closeApprovedBy/Long/nullable/read-only(system-set); DBF-FIN-158 closeApprovedAt/OffsetDateTime/nullable/read-only(system-set); DBF-FIN-159 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-160…163 audit/read-only
DTO MEMBERSHIP   create-request (nested under Fiscal Year, or standalone API-FIN-041): periodCode, nameAr, nameEn, sequenceNo, startDate, endDate · excludes fiscalPeriodPk, statusCode, closeApprovedBy/At, audit · response includes all
LOOKUP FIELDS   statusCode │ DBF-FIN-156 │ key `period-states` │ GET /api/v1/fin/lookups?lookupKey=period-states
DOMAIN RULES   RULE-FIN-004 (period Open for posting, see ENT-FIN-006) · RULE-FIN-008 "Prevent a user from approving a period's close if that user created any entry posted within the period" · trigger: on period-close approval · ar: لا يمكن لمنشئ القيد اعتماد إقفال الفترة · en: The entry's creator cannot approve the period close · scope: approve-close (ALL) · DB enforcement: app-level (join `fin_journal_entry.created_by` against the approving principal) · owner layer: domain · RULE-FIN-009 "Permanently refuse any reopen or posting attempt against a Hard Closed period" · trigger: on reopen / post attempt · ar: الفترة مقفلة إقفالاً نهائياً · en: Period is permanently closed · scope: approve-close, post (ALL) · DB enforcement: app-level · owner layer: domain
STATE MACHINE   status column DBF-FIN-156 · values OPEN, SOFT_CLOSE, HARD_CLOSE · initial OPEN · transitions: OPEN→SOFT_CLOSE (approve-close, Financial Controller, RULE-FIN-008), SOFT_CLOSE→OPEN (reopen, Financial Controller), SOFT_CLOSE→HARD_CLOSE (approve-close, Financial Controller, RULE-FIN-008) · terminal: HARD_CLOSE · invalid-transition RULE: RULE-FIN-009 (nothing out of HARD_CLOSE, including back to OPEN)
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-041 SAVE, part of QR-FIN-037/038 (search/read via parent year), QR-FIN-039 UPDATE (approve-close)

### ENT-FIN-012 — Accounting User      kind: security
BINDINGS   table `fin_user` · PK `user_pk` (DBF-FIN-164) · identity · db-script-fin.md v1
BUSINESS CODE   none
FIELDS     DBF-FIN-164 userPk/Long/read-only/PK; DBF-FIN-165 username/String/NOT NULL/writable(create-only)/UQ; DBF-FIN-166/167 nameAr/nameEn/String/NOT NULL/writable; DBF-FIN-168 passwordHash/String/NOT NULL/write-only(never in response, BCrypt-hashed server-side from a plaintext `password` request field); DBF-FIN-169 lastLoginAt/OffsetDateTime/nullable/read-only(system-set on login); DBF-FIN-170 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-171…174 audit/read-only
DTO MEMBERSHIP   create-request: username, nameAr, nameEn, password (plaintext, write-only, mapped to passwordHash) · update-request excludes username, password (a separate change-password flow, out of v1 scope per plan §12 — not in any user story) · response excludes passwordHash entirely
LOOKUP FIELDS   none
DOMAIN RULES   none SRS-declared beyond standard uniqueness
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-016-shaped FIND_ONE by username (auth, see API-FIN-047), QR-FIN-048 SAVE, QR-FIN-049 FIND_BY_CRITERIA, QR-FIN-050 FIND_ONE, QR-FIN-051 UPDATE, QR-FIN-052 UPDATE (deactivate)

### ENT-FIN-013 — Role & Permission      kind: security
BINDINGS   tables `fin_role` (PK `role_pk`/DBF-FIN-175) + `fin_role_permission` (PK `role_permission_pk`/DBF-FIN-184) + `fin_user_role` (PK `user_role_pk`/DBF-FIN-188) · identity PKs · db-script-fin.md v1
BUSINESS CODE   none
FIELDS     DBF-FIN-175 rolePk/Long/read-only/PK; DBF-FIN-176 roleCode/String/NOT NULL/writable(create-only)/UQ; DBF-FIN-177/178 roleNameAr/roleNameEn/String/NOT NULL/writable; DBF-FIN-179 isActiveFl/Boolean/NOT NULL/writable; DBF-FIN-180…183 audit/read-only — permission sub-shape: DBF-FIN-184 rolePermissionPk/Long/read-only/PK; DBF-FIN-185 roleId/Long/NOT NULL/writable/FK; DBF-FIN-186 pageCode/String/NOT NULL/writable (SEC_PAGES row, PHASE:SEC-BE); DBF-FIN-187 actionCode/String/NOT NULL/writable/CHK (VIEW|CREATE|UPDATE|DELETE) — user-assignment sub-shape: DBF-FIN-188…190
DTO MEMBERSHIP   create/update-request: roleCode (create-only), roleNameAr/En, permissions[] (pageCode, actionCode) · assign-request (API-FIN-058): userIds[] · response includes all + permissions[] + assignedUsers[]
LOOKUP FIELDS   none (pageCode is not `fin_lookup_value` — it is this module's own `SEC_PAGES` seed, PHASE:SEC-BE)
DOMAIN RULES   none SRS-declared beyond the VIEW-gateway rule (enforced in PHASE:SEC-BE, R7) and RULE-FIN-008's role-separation pattern (SRS §7.1 — enabled here, enforced at approve-close, ENT-FIN-011)
STATE MACHINE   not applicable
CROSS-MODULE   none
REPOSITORY OPS   QR-FIN-053 SAVE, QR-FIN-054 FIND_BY_CRITERIA, QR-FIN-055 FIND_ONE, QR-FIN-056 UPDATE, QR-FIN-057 UPDATE (deactivate), QR-FIN-058 SAVE (assign — inserts fin_user_role rows)
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-FIN-001,REQ-FIN-004,REQ-FIN-006,REQ-FIN-008,REQ-FIN-013,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,REQ-FIN-025,REQ-FIN-026,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034 -->
## PHASE 3 — SVC-API (service + API; 58 endpoints, split at ≥8 per §6.0)

<!-- SUB:SVC-API-CRUD:START traces=REQ-FIN-001,REQ-FIN-008,REQ-FIN-015,REQ-FIN-018,REQ-FIN-021,REQ-FIN-023,REQ-FIN-025 -->
### SUB SVC-API-CRUD — 33 mutation endpoints (POST/PUT/DELETE)

<!-- API:API-FIN-001:START traces=REQ-FIN-001,REQ-FIN-003,DBF-FIN-001 -->
#### API-FIN-001 — create account
Endpoint     : POST /api/v1/fin/accounts
Layers       : AccountController.create → AccountService.create → AccountRepository (R1 standard flow)
Request      : body: code, nameAr, nameEn, parentAccountId?, accountType, natureCode, acceptsDirectPostingFl, isRetainedEarningsAccountFl — excludes accountPk, audit
Response     : 201, AccountResponse (all fields), not paginated, ApiResponse<AccountResponse>
Validations  : RULE-FIN-011 "Require exactly one active account flagged isRetainedEarningsAccountFl at year-end close time" (ar: يجب تحديد حساب واحد فقط للأرباح المحتجزة · en: Exactly one Retained Earnings account must be designated) — checked only if isRetainedEarningsAccountFl=true
Errors       : FIN-RULE-011 (409, RULE-FIN-011); FIN-PLATFORM-400 (400, validation)
Orchestration: validate DTO → check RULE-FIN-011 if flag set → QR-FIN-001 SAVE into fin_account (PK account_pk, identity)
Repository   : QR-FIN-001 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-001 · PERM_FIN_COA_CREATE
Localization : nameAr/nameEn both required in request and response
<!-- API:API-FIN-001:END -->

<!-- API:API-FIN-004:START traces=REQ-FIN-001,REQ-FIN-003,DBF-FIN-001 -->
#### API-FIN-004 — update account
Endpoint     : PUT /api/v1/fin/accounts/{id}
Layers       : AccountController.update → AccountService.update → AccountRepository
Request      : path: id · body: nameAr, nameEn, parentAccountId?, accountType, natureCode, acceptsDirectPostingFl, isRetainedEarningsAccountFl — excludes accountPk, code, audit
Response     : 200, AccountResponse, ApiResponse<AccountResponse>
Validations  : RULE-FIN-011 (same as API-FIN-001)
Errors       : FIN-RULE-011 (409); FIN-PLATFORM-404 (404, not found)
Orchestration: load by id (QR-FIN-003) → validate → check RULE-FIN-011 → QR-FIN-004 UPDATE
Repository   : QR-FIN-004 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-001 · PERM_FIN_COA_UPDATE
Localization : nameAr/nameEn both required
<!-- API:API-FIN-004:END -->

<!-- API:API-FIN-005:START traces=REQ-FIN-001,DBF-FIN-010 -->
#### API-FIN-005 — deactivate account
Endpoint     : DELETE /api/v1/fin/accounts/{id}
Layers       : AccountController.deactivate → AccountService.deactivate → AccountRepository
Request      : path: id
Response     : 204, no body
Validations  : usage check — an account referenced by an active RULE-FIN-005 rule line or a POSTED journal-entry-line is not blocked from deactivation (soft delete never removes history), but a deactivated account can no longer be RULE-FIN-001 posting target
Errors       : FIN-PLATFORM-404 (404, not found)
Orchestration: load by id → QR-FIN-005 UPDATE (isActiveFl=false)
Repository   : QR-FIN-005 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-001 · PERM_FIN_COA_DELETE
Localization : not applicable (no body)
<!-- API:API-FIN-005:END -->

<!-- API:API-FIN-006:START traces=REQ-FIN-004,DBF-FIN-015 -->
#### API-FIN-006 — create dimension
Endpoint     : POST /api/v1/fin/dimensions
Layers       : DimensionController.create → DimensionService.create → DimensionRepository
Request      : body: dimensionKey, nameAr, nameEn, controlType, values[]? (valueCode, valueNameAr, valueNameEn, sortOrder)
Response     : 201, DimensionResponse (+ values[]), ApiResponse<DimensionResponse>
Validations  : none beyond DTO validation + UQ_FIN_DIMENSION_KEY
Errors       : FIN-PLATFORM-409 (409, duplicate key)
Orchestration: validate → QR-FIN-006 SAVE dimension + nested values
Repository   : QR-FIN-006 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-002 · PERM_FIN_DIM_CREATE
Localization : nameAr/nameEn + valueNameAr/valueNameEn required
<!-- API:API-FIN-006:END -->

<!-- API:API-FIN-009:START traces=REQ-FIN-004,REQ-FIN-005,DBF-FIN-015 -->
#### API-FIN-009 — update dimension
Endpoint     : PUT /api/v1/fin/dimensions/{id}
Layers       : DimensionController.update → DimensionService.update → DimensionRepository
Request      : path: id · body: nameAr, nameEn, controlType, values[]
Response     : 200, DimensionResponse, ApiResponse<DimensionResponse>
Validations  : none beyond DTO validation
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load (QR-FIN-008) → validate → QR-FIN-009 UPDATE
Repository   : QR-FIN-009 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-002 · PERM_FIN_DIM_UPDATE
Localization : nameAr/nameEn required
<!-- API:API-FIN-009:END -->

<!-- API:API-FIN-010:START traces=REQ-FIN-004,DBF-FIN-020 -->
#### API-FIN-010 — deactivate dimension
Endpoint     : DELETE /api/v1/fin/dimensions/{id}
Layers       : DimensionController.deactivate → DimensionService.deactivate → DimensionRepository
Request      : path: id
Response     : 204, no body
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load → QR-FIN-010 UPDATE (isActiveFl=false)
Repository   : QR-FIN-010 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-002 · PERM_FIN_DIM_DELETE
Localization : not applicable
<!-- API:API-FIN-010:END -->

<!-- API:API-FIN-011:START traces=REQ-FIN-006,REQ-FIN-007,DBF-FIN-028 -->
#### API-FIN-011 — create lookup type
Endpoint     : POST /api/v1/fin/lookups
Layers       : LookupController.create → LookupService.create → LookupRepository
Request      : body: lookupKey, nameAr, nameEn, values[]? (valueCode, labelAr, labelEn, sortOrder)
Response     : 201, LookupResponse (+ values[]), ApiResponse<LookupResponse>
Validations  : UQ_FIN_LOOKUP_TYPE_KEY
Errors       : FIN-PLATFORM-409 (409, duplicate key)
Orchestration: validate → QR-FIN-011 SAVE
Repository   : QR-FIN-011 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-003 · PERM_FIN_LKP_CREATE
Localization : nameAr/nameEn + labelAr/labelEn required
<!-- API:API-FIN-011:END -->

<!-- API:API-FIN-014:START traces=REQ-FIN-006,DBF-FIN-028 -->
#### API-FIN-014 — update lookup
Endpoint     : PUT /api/v1/fin/lookups/{id}
Layers       : LookupController.update → LookupService.update → LookupRepository
Request      : path: id · body: nameAr, nameEn, values[]
Response     : 200, LookupResponse, ApiResponse<LookupResponse>
Validations  : none beyond DTO validation
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load (QR-FIN-013) → validate → QR-FIN-014 UPDATE
Repository   : QR-FIN-014 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-003 · PERM_FIN_LKP_UPDATE
Localization : nameAr/nameEn + labelAr/labelEn required
<!-- API:API-FIN-014:END -->

<!-- API:API-FIN-015:START traces=REQ-FIN-006,DBF-FIN-032 -->
#### API-FIN-015 — deactivate lookup value
Endpoint     : DELETE /api/v1/fin/lookups/{id}
Layers       : LookupController.deactivate → LookupService.deactivate → LookupRepository
Request      : path: id
Response     : 204, no body
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load → QR-FIN-015 UPDATE (isActiveFl=false)
Repository   : QR-FIN-015 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-003 · PERM_FIN_LKP_DELETE
Localization : not applicable
<!-- API:API-FIN-015:END -->

<!-- API:API-FIN-016:START traces=REQ-FIN-008,REQ-FIN-013,DBF-FIN-040 -->
#### API-FIN-016 — create event-type rule
Endpoint     : POST /api/v1/fin/rules
Layers       : EventRuleController.create → EventRuleService.create → EventRuleRepository
Request      : body: eventTypeCode, nameAr, nameEn, lines[] (lineNo, accountDerivationType, constantAccountId?, eventFieldName?, mappingEntries[]?, amountSourceField, amountSourceOperation, amountOperationValue?, directionCode, distributionType, distributionValue?)
Response     : 201, EventRuleResponse (+ lines[]), ApiResponse<EventRuleResponse>
Validations  : RULE-FIN-012 "Prevent activating a second rule for an event type that already has an active rule" (ar: يوجد بالفعل قاعدة نشطة لهذا النوع من الأحداث · en: An active rule already exists for this event type); RULE-FIN-005 (distribution order) validated per line group
Errors       : FIN-RULE-012 (409); FIN-RULE-005 (400, malformed distribution)
Orchestration: validate → check RULE-FIN-012 → validate RULE-FIN-005 per distribution group → QR-FIN-016-shaped existence check → SAVE rule + lines + mapping entries
Repository   : QR-FIN-016 (existence check) then rule persisted via the aggregate save (folded into the rule create, R2 REPOSITORY OPS) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-004 · PERM_FIN_RULE_CREATE
Localization : nameAr/nameEn required
<!-- API:API-FIN-016:END -->

<!-- API:API-FIN-019:START traces=REQ-FIN-009,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,DBF-FIN-049 -->
#### API-FIN-019 — update event-type rule
Endpoint     : PUT /api/v1/fin/rules/{id}
Layers       : EventRuleController.update → EventRuleService.update → EventRuleRepository
Request      : path: id · body: nameAr, nameEn, lines[] (full replace) — excludes eventTypeCode (immutable)
Response     : 200, EventRuleResponse, ApiResponse<EventRuleResponse>
Validations  : RULE-FIN-005 per distribution group
Errors       : FIN-RULE-005 (400); FIN-PLATFORM-404 (404)
Orchestration: load (QR-FIN-018) → validate → QR-FIN-019 UPDATE (replace lines + mapping entries)
Repository   : QR-FIN-019 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-004 · PERM_FIN_RULE_UPDATE
Localization : nameAr/nameEn required
<!-- API:API-FIN-019:END -->

<!-- API:API-FIN-020:START traces=REQ-FIN-008,DBF-FIN-044 -->
#### API-FIN-020 — deactivate event-type rule
Endpoint     : DELETE /api/v1/fin/rules/{id}
Layers       : EventRuleController.deactivate → EventRuleService.deactivate → EventRuleRepository
Request      : path: id
Response     : 204, no body
Validations  : none — deactivating a rule stops future event matching (REQ-FIN-008); does not touch entries already posted
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load → QR-FIN-020 UPDATE (isActiveFl=false)
Repository   : QR-FIN-020 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-004 · PERM_FIN_RULE_DELETE
Localization : not applicable
<!-- API:API-FIN-020:END -->

<!-- API:API-FIN-021:START traces=REQ-FIN-016,DBF-FIN-094 -->
#### API-FIN-021 — create recurring/reversing template
Endpoint     : POST /api/v1/fin/recurring-templates
Layers       : RecurringTemplateController.create → RecurringTemplateService.create → RecurringTemplateRepository
Request      : body: templateNameAr, templateNameEn, templateTypeCode, scheduleRule, lines[] (accountId, dimensionValueIds[], amountSourceValue|amountSourceFormula, directionCode)
Response     : 201, RecurringTemplateResponse (+ lines[], nextRunDate computed from scheduleRule), ApiResponse<RecurringTemplateResponse>
Validations  : none SRS-declared at create time (RULE-FIN-013 fires only at scheduled-run time)
Errors       : FIN-PLATFORM-400 (400, malformed scheduleRule)
Orchestration: validate → compute initial nextRunDate from scheduleRule → QR-FIN-021 SAVE
Repository   : QR-FIN-021 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-005 · PERM_FIN_TMPL_CREATE
Localization : templateNameAr/En required
<!-- API:API-FIN-021:END -->

<!-- API:API-FIN-024:START traces=REQ-FIN-016,DBF-FIN-094 -->
#### API-FIN-024 — update recurring/reversing template
Endpoint     : PUT /api/v1/fin/recurring-templates/{id}
Layers       : RecurringTemplateController.update → RecurringTemplateService.update → RecurringTemplateRepository
Request      : path: id · body: templateNameAr, templateNameEn, scheduleRule, lines[] — excludes templateTypeCode (immutable), nextRunDate (system)
Response     : 200, RecurringTemplateResponse, ApiResponse<RecurringTemplateResponse>
Validations  : none beyond DTO validation
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load (QR-FIN-023) → validate → QR-FIN-024 UPDATE
Repository   : QR-FIN-024 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-005 · PERM_FIN_TMPL_UPDATE
Localization : templateNameAr/En required
<!-- API:API-FIN-024:END -->

<!-- API:API-FIN-025:START traces=REQ-FIN-016,DBF-FIN-100 -->
#### API-FIN-025 — deactivate recurring/reversing template
Endpoint     : DELETE /api/v1/fin/recurring-templates/{id}
Layers       : RecurringTemplateController.deactivate → RecurringTemplateService.deactivate → RecurringTemplateRepository
Request      : path: id
Response     : 204, no body
Validations  : none — deactivation stops future scheduled runs
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load → QR-FIN-025 UPDATE (isActiveFl=false)
Repository   : QR-FIN-025 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-005 · PERM_FIN_TMPL_DELETE
Localization : not applicable
<!-- API:API-FIN-025:END -->

<!-- API:API-FIN-026:START traces=REQ-FIN-017,DBF-FIN-115 -->
#### API-FIN-026 — create allocation rule
Endpoint     : POST /api/v1/fin/allocation-rules
Layers       : AllocationRuleController.create → AllocationRuleService.create → AllocationRuleRepository
Request      : body: ruleNameAr, ruleNameEn, sourceAccountId, sourceDimensionValueIds[]?, lines[] (targetAccountId, targetDimensionValueIds[]?, distributionType, distributionValue?)
Response     : 201, AllocationRuleResponse (+ lines[]), ApiResponse<AllocationRuleResponse>
Validations  : RULE-FIN-014 structural shape (exactly one REMAINDER line if any FIXED/PERCENTAGE line present) validated at save time; full-balance check deferred to run time (RULE-FIN-014)
Errors       : FIN-RULE-014 (400, malformed distribution shape)
Orchestration: validate → QR-FIN-026 SAVE
Repository   : QR-FIN-026 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-006 · PERM_FIN_ALLOC_CREATE
Localization : ruleNameAr/En required
<!-- API:API-FIN-026:END -->

<!-- API:API-FIN-029:START traces=REQ-FIN-017,DBF-FIN-115 -->
#### API-FIN-029 — update allocation rule
Endpoint     : PUT /api/v1/fin/allocation-rules/{id}
Layers       : AllocationRuleController.update → AllocationRuleService.update → AllocationRuleRepository
Request      : path: id · body: ruleNameAr, ruleNameEn, sourceAccountId, sourceDimensionValueIds[], lines[]
Response     : 200, AllocationRuleResponse, ApiResponse<AllocationRuleResponse>
Validations  : RULE-FIN-014 structural shape (as API-FIN-026)
Errors       : FIN-RULE-014 (400); FIN-PLATFORM-404 (404)
Orchestration: load (QR-FIN-028) → validate → QR-FIN-029 UPDATE
Repository   : QR-FIN-029 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-006 · PERM_FIN_ALLOC_UPDATE
Localization : ruleNameAr/En required
<!-- API:API-FIN-029:END -->

<!-- API:API-FIN-030:START traces=REQ-FIN-017,DBF-FIN-119 -->
#### API-FIN-030 — deactivate allocation rule
Endpoint     : DELETE /api/v1/fin/allocation-rules/{id}
Layers       : AllocationRuleController.deactivate → AllocationRuleService.deactivate → AllocationRuleRepository
Request      : path: id
Response     : 204, no body
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load → QR-FIN-030 UPDATE (isActiveFl=false)
Repository   : QR-FIN-030 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-006 · PERM_FIN_ALLOC_DELETE
Localization : not applicable
<!-- API:API-FIN-030:END -->

<!-- API:API-FIN-031:START traces=REQ-FIN-017,DBF-FIN-118 -->
#### API-FIN-031 — run allocation
Endpoint     : POST /api/v1/fin/allocation-rules/{id}/run
Layers       : AllocationRuleController.run → AllocationRuleService.run → JournalEntryRepository (writes the generated entry)
Request      : path: id
Response     : 201, JournalEntryResponse (the generated, posted entry), ApiResponse<JournalEntryResponse>
Validations  : RULE-FIN-014 "Require an allocation rule's lines... to total exactly the source balance being distributed" (ar: يجب أن يساوي مجموع سطور التوزيع رصيد المصدر بالكامل · en: Allocation lines must total exactly the source balance); RULE-FIN-001…004 (the generated entry's own posting validation)
Errors       : FIN-RULE-014 (409); FIN-RULE-001..004 (409, posting validation)
Orchestration: load rule (QR-FIN-028) → compute source balance (QR-FIN-032-shaped aggregate over fin_journal_entry_line) → apply RULE-FIN-005 distribution order → build entry (sourceTypeCode=ALLOCATION, allocationRuleId=id) → post via `JournalEntry.post()` (RULE-FIN-001…004) → QR-FIN-031 SAVE
Repository   : QR-FIN-031 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-006 · PERM_FIN_ALLOC_UPDATE
Localization : not applicable (no user-facing name fields on the run action itself)
<!-- API:API-FIN-031:END -->

<!-- API:API-FIN-032:START traces=REQ-FIN-015,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-028,DBF-FIN-067 -->
#### API-FIN-032 — create manual journal entry
Endpoint     : POST /api/v1/fin/journal-entries
Layers       : JournalEntryController.create → JournalEntryService.createManual → JournalEntryRepository
Request      : body: entryDate, periodId, lines[] (accountId, dimensionValueIds[], directionCode, amount, descriptionAr?, descriptionEn?) — excludes journalEntryPk, entryNo, sourceTypeCode (system='MANUAL'), statusCode
Response     : 201, JournalEntryResponse (statusCode=POSTED on success), ApiResponse<JournalEntryResponse>
Validations  : RULE-FIN-001 (leaf/active account, ar: لا يمكن الترحيل إلى حساب غير نشط أو غير قابل للترحيل المباشر · en: Cannot post to an inactive or non-postable account) · RULE-FIN-002 (debits=credits, ADR-FIN-004, ar: مجموع المدين لا يساوي مجموع الدائن · en: Debit total does not equal credit total) · RULE-FIN-003 (dimension validity, ar: قيمة البُعد غير صالحة أو غير نشطة · en: Dimension value is invalid or inactive) · RULE-FIN-004 (period Open, ar: الفترة غير مفتوحة للترحيل · en: Period is not open for posting)
Errors       : FIN-RULE-001 (409); FIN-RULE-002 (409); FIN-RULE-003 (409); FIN-RULE-004 (409)
Orchestration: platform numbering engine issues entryNo → build DRAFT entry+lines → `JournalEntry.post()` runs RULE-FIN-001…004 in one transaction → on success statusCode=POSTED (REQ-FIN-018); no per-entry approval step exists anywhere in this flow (REQ-FIN-020) → QR-FIN-032 SAVE
Repository   : QR-FIN-032 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-007 · PERM_FIN_JE_CREATE
Localization : descriptionAr/descriptionEn optional but paired
<!-- API:API-FIN-032:END -->

<!-- API:API-FIN-035:START traces=REQ-FIN-023,REQ-FIN-024,DBF-FIN-077 -->
#### API-FIN-035 — reverse journal entry
Endpoint     : POST /api/v1/fin/journal-entries/{id}/reverse
Layers       : JournalEntryController.reverse → JournalEntryService.reverse → JournalEntryRepository
Request      : path: id
Response     : 201, JournalEntryResponse (the new VOID/CORRECTION entry), ApiResponse<JournalEntryResponse>
Validations  : RULE-FIN-006 "prevent any edit or delete on an entry once its statusCode is POSTED" — reversal creates a NEW row, never edits the original (ar: القيد المرحّل مقفل ولا يمكن تعديله أو حذفه · en: A posted entry is locked and cannot be edited or deleted) · RULE-FIN-007 "Require every Void/Correction entry to carry a reversalOfEntryId" (ar: يجب ربط قيد العكس بالقيد الأصلي · en: A reversing entry must reference the original entry)
Errors       : FIN-PLATFORM-404 (404, original not found); FIN-RULE-007 (500, internal — should never occur, defensive)
Orchestration: load original (QR-FIN-034) → determine posting period: original's period if Open, else the current Open period (REQ-FIN-024) → build mirrored lines (debit↔credit swapped) → `JournalEntry.post()` (RULE-FIN-001…004) → set original.reversedByEntryId → QR-FIN-035 SAVE
Repository   : QR-FIN-035 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-007 · PERM_FIN_JE_UPDATE
Localization : not applicable
<!-- API:API-FIN-035:END -->

<!-- API:API-FIN-036:START traces=REQ-FIN-027,DBF-FIN-136 -->
#### API-FIN-036 — create fiscal year
Endpoint     : POST /api/v1/fin/fiscal-years
Layers       : FiscalYearController.create → FiscalYearService.create → FiscalYearRepository
Request      : body: yearCode, nameAr?, nameEn?, startDate, endDate, periods[] (periodCode, sequenceNo, startDate, endDate) — excludes fiscalYearPk, statusCode
Response     : 201, FiscalYearResponse (statusCode=OPEN, + periods[] each statusCode=OPEN), ApiResponse<FiscalYearResponse>
Validations  : UQ_FIN_FISCAL_YEAR_CODE; UQ_FIN_FISCAL_PERIOD_CODE per year
Errors       : FIN-PLATFORM-409 (409, duplicate code)
Orchestration: validate → QR-FIN-036 SAVE year + nested periods (each statusCode=OPEN)
Repository   : QR-FIN-036 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-008 · PERM_FIN_PERIOD_CREATE
Localization : nameAr/nameEn optional but paired
<!-- API:API-FIN-036:END -->

<!-- API:API-FIN-039:START traces=REQ-FIN-021,REQ-FIN-022,REQ-FIN-029,DBF-FIN-157 -->
#### API-FIN-039 — approve period close
Endpoint     : POST /api/v1/fin/fiscal-years/{yearId}/periods/{periodId}/approve-close
Layers       : FiscalYearController.approveClose → FiscalPeriodService.approveClose → FiscalPeriodRepository
Request      : path: yearId, periodId · body: targetStatus (SOFT_CLOSE | HARD_CLOSE)
Response     : 200, FiscalPeriodResponse (statusCode updated, closeApprovedBy/At set), ApiResponse<FiscalPeriodResponse>
Validations  : RULE-FIN-008 "Prevent a user from approving a period's close if that user created any entry posted within the period" (ar: لا يمكن لمنشئ القيد اعتماد إقفال الفترة · en: The entry's creator cannot approve the period close) · RULE-FIN-009 "Permanently refuse any reopen or posting attempt against a Hard Closed period" (ar: الفترة مقفلة إقفالاً نهائياً · en: Period is permanently closed) — blocks approve-close on an already HARD_CLOSE period
Errors       : FIN-RULE-008 (403); FIN-RULE-009 (409, already Hard Closed)
Orchestration: load period (QR-FIN-039-shaped read) → SoD check (RULE-FIN-008, join fin_journal_entry.created_by against the current principal for entries in this period) → HARD_CLOSE-immutability check (RULE-FIN-009) → set statusCode, closeApprovedBy=current principal, closeApprovedAt=now() → QR-FIN-039 UPDATE
Repository   : QR-FIN-039 · UPDATE · join required (fin_journal_entry) — ADR-FIN-006 (below) · transaction READ_WRITE
Security     : SCR-REQ-FIN-008 · PERM_FIN_PERIOD_UPDATE
Localization : not applicable
<!-- API:API-FIN-039:END -->

<!-- API:API-FIN-040:START traces=REQ-FIN-030,REQ-FIN-031,DBF-FIN-142 -->
#### API-FIN-040 — year-end close
Endpoint     : POST /api/v1/fin/fiscal-years/{id}/year-end-close
Layers       : FiscalYearController.yearEndClose → FiscalYearService.yearEndClose → FiscalYearRepository, JournalEntryRepository
Request      : path: id
Response     : 200, FiscalYearResponse (statusCode=YEAR_END_CLOSED) + the generated opening JournalEntryResponse, ApiResponse<FiscalYearYearEndCloseResponse>
Validations  : RULE-FIN-010 "Prevent year-end close of a fiscal year until every one of its periods is Hard Closed" (ADR-FIN-003; ar: يجب إقفال جميع فترات السنة إقفالاً نهائياً أولاً · en: All periods of the year must be Hard Closed first) · RULE-FIN-011 "Require exactly one active account flagged isRetainedEarningsAccountFl" (ar: يجب تحديد حساب واحد فقط للأرباح المحتجزة · en: Exactly one Retained Earnings account must be designated)
Errors       : FIN-RULE-010 (409); FIN-RULE-011 (409, no/multiple RE account)
Orchestration: check every period Hard Closed (RULE-FIN-010) → compute closing balances per account from POSTED entries (QR-FIN-043-shaped aggregate) → close revenue/expense net to the RE account (RULE-FIN-011) → generate + post the new year's opening entry from balance-sheet closing balances (REQ-FIN-030, via `JournalEntry.post()`) → set statusCode=YEAR_END_CLOSED
Repository   : QR-FIN-040 · SAVE+UPDATE · join NONE (self-contained aggregate over fin_journal_entry_line) · transaction READ_WRITE
Security     : SCR-REQ-FIN-008 · PERM_FIN_PERIOD_UPDATE
Localization : not applicable
<!-- API:API-FIN-040:END -->

<!-- API:API-FIN-041:START traces=REQ-FIN-027,DBF-FIN-148 -->
#### API-FIN-041 — create fiscal period
Endpoint     : POST /api/v1/fin/fiscal-years/{yearId}/periods
Layers       : FiscalYearController.createPeriod → FiscalPeriodService.create → FiscalPeriodRepository
Request      : path: yearId · body: periodCode, nameAr?, nameEn?, sequenceNo, startDate, endDate
Response     : 201, FiscalPeriodResponse (statusCode=OPEN), ApiResponse<FiscalPeriodResponse>
Validations  : UQ_FIN_FISCAL_PERIOD_CODE per year
Errors       : FIN-PLATFORM-409 (409, duplicate code); FIN-PLATFORM-404 (404, year not found)
Orchestration: load year (QR-FIN-038) → validate → QR-FIN-041 SAVE
Repository   : QR-FIN-041 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-008 · PERM_FIN_PERIOD_CREATE
Localization : nameAr/nameEn optional but paired
<!-- API:API-FIN-041:END -->

<!-- API:API-FIN-047:START traces=REQ-FIN-025,DBF-FIN-164 -->
#### API-FIN-047 — login (authenticate)
Endpoint     : POST /api/v1/fin/auth/login
Layers       : AuthController.login → AuthService.authenticate → UserRepository
Request      : body: username, password
Response     : 200, AuthTokenResponse (token, expiresAt), ApiResponse<AuthTokenResponse>
Validations  : credentials match a `fin_user` row with isActiveFl=true; independent of any other module's login (POL-FIN-008)
Errors       : FIN-PLATFORM-401 (401, invalid credentials); FIN-PLATFORM-403 (403, inactive user)
Orchestration: QR-FIN-016-shaped FIND_ONE by username → verify BCrypt password → set lastLoginAt=now() → issue token (platform auth layer, FIN-scoped)
Repository   : QR-FIN-016-shaped · FIND_ONE · join NONE · transaction READ_WRITE (lastLoginAt update)
Security     : SCR-REQ-FIN-014 · no gateway permission required (pre-authentication)
Localization : not applicable
<!-- API:API-FIN-047:END -->

<!-- API:API-FIN-048:START traces=REQ-FIN-025,DBF-FIN-164 -->
#### API-FIN-048 — create user
Endpoint     : POST /api/v1/fin/users
Layers       : UserController.create → UserService.create → UserRepository
Request      : body: username, nameAr, nameEn, password — excludes userPk, passwordHash, audit
Response     : 201, UserResponse (excludes passwordHash), ApiResponse<UserResponse>
Validations  : UQ_FIN_USER_USERNAME
Errors       : FIN-PLATFORM-409 (409, duplicate username)
Orchestration: validate → BCrypt-hash password → QR-FIN-048 SAVE
Repository   : QR-FIN-048 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-015 · PERM_FIN_USER_CREATE
Localization : nameAr/nameEn required
<!-- API:API-FIN-048:END -->

<!-- API:API-FIN-051:START traces=REQ-FIN-025,DBF-FIN-166 -->
#### API-FIN-051 — update user
Endpoint     : PUT /api/v1/fin/users/{id}
Layers       : UserController.update → UserService.update → UserRepository
Request      : path: id · body: nameAr, nameEn — excludes username, password (separate flow, out of v1 scope)
Response     : 200, UserResponse, ApiResponse<UserResponse>
Validations  : none beyond DTO validation
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load (QR-FIN-050) → validate → QR-FIN-051 UPDATE
Repository   : QR-FIN-051 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-015 · PERM_FIN_USER_UPDATE
Localization : nameAr/nameEn required
<!-- API:API-FIN-051:END -->

<!-- API:API-FIN-052:START traces=REQ-FIN-025,DBF-FIN-170 -->
#### API-FIN-052 — deactivate user
Endpoint     : DELETE /api/v1/fin/users/{id}
Layers       : UserController.deactivate → UserService.deactivate → UserRepository
Request      : path: id
Response     : 204, no body
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load → QR-FIN-052 UPDATE (isActiveFl=false)
Repository   : QR-FIN-052 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-015 · PERM_FIN_USER_DELETE
Localization : not applicable
<!-- API:API-FIN-052:END -->

<!-- API:API-FIN-053:START traces=REQ-FIN-025,REQ-FIN-026,DBF-FIN-175 -->
#### API-FIN-053 — create role
Endpoint     : POST /api/v1/fin/roles
Layers       : RoleController.create → RoleService.create → RoleRepository
Request      : body: roleCode, roleNameAr, roleNameEn, permissions[] (pageCode, actionCode)
Response     : 201, RoleResponse (+ permissions[]), ApiResponse<RoleResponse>
Validations  : UQ_FIN_ROLE_CODE; every pageCode exists in SEC_PAGES (PHASE:SEC-BE); VIEW-gateway rule (§7.1) — a non-VIEW action for a page requires VIEW also present
Errors       : FIN-PLATFORM-409 (409, duplicate role code); FIN-PLATFORM-400 (400, unknown page code or missing VIEW gateway)
Orchestration: validate → check gateway rule → QR-FIN-053 SAVE
Repository   : QR-FIN-053 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-016 · PERM_FIN_ROLE_CREATE
Localization : roleNameAr/En required
<!-- API:API-FIN-053:END -->

<!-- API:API-FIN-056:START traces=REQ-FIN-026,DBF-FIN-175 -->
#### API-FIN-056 — update role
Endpoint     : PUT /api/v1/fin/roles/{id}
Layers       : RoleController.update → RoleService.update → RoleRepository
Request      : path: id · body: roleNameAr, roleNameEn, permissions[] — excludes roleCode (immutable)
Response     : 200, RoleResponse, ApiResponse<RoleResponse>
Validations  : VIEW-gateway rule (as API-FIN-053)
Errors       : FIN-PLATFORM-400 (400, missing VIEW gateway); FIN-PLATFORM-404 (404)
Orchestration: load (QR-FIN-055) → validate → QR-FIN-056 UPDATE
Repository   : QR-FIN-056 · UPDATE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-016 · PERM_FIN_ROLE_UPDATE
Localization : roleNameAr/En required
<!-- API:API-FIN-056:END -->

<!-- API:API-FIN-057:START traces=REQ-FIN-025,DBF-FIN-179 -->
#### API-FIN-057 — deactivate role
Endpoint     : DELETE /api/v1/fin/roles/{id}
Layers       : RoleController.deactivate → RoleService.deactivate → RoleRepository
Request      : path: id
Response     : 204, no body
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: load → QR-FIN-057 UPDATE (isActiveFl=false)
Repository   : QR-FIN-057 · UPDATE (flag) · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-016 · PERM_FIN_ROLE_DELETE
Localization : not applicable
<!-- API:API-FIN-057:END -->

<!-- API:API-FIN-058:START traces=REQ-FIN-026,DBF-FIN-188 -->
#### API-FIN-058 — assign users to role
Endpoint     : POST /api/v1/fin/roles/{id}/assign
Layers       : RoleController.assign → RoleService.assignUsers → UserRoleRepository
Request      : path: id · body: userIds[]
Response     : 200, RoleResponse (+ assignedUsers[]), ApiResponse<RoleResponse>
Validations  : every userId exists and isActiveFl=true
Errors       : FIN-PLATFORM-404 (404, unknown user)
Orchestration: load role → validate user ids → QR-FIN-058 SAVE (insert fin_user_role rows, idempotent on UQ_FIN_USER_ROLE)
Repository   : QR-FIN-058 · SAVE · join NONE · transaction READ_WRITE
Security     : SCR-REQ-FIN-016 · PERM_FIN_ROLE_UPDATE
Localization : not applicable
<!-- API:API-FIN-058:END -->
<!-- SUB:SVC-API-CRUD:END -->

<!-- SUB:SVC-API-SEARCH:START traces=REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-002 -->
### SUB SVC-API-SEARCH — 25 read endpoints (GET)

<!-- API:API-FIN-002:START traces=REQ-FIN-001,DBF-FIN-001 -->
#### API-FIN-002 — search accounts
Endpoint     : GET /api/v1/fin/accounts
Layers       : AccountController.search → AccountService.search → AccountRepository
Request      : query: code?, nameAr?, nameEn?, accountType?, isActiveFl?, page, size
Response     : 200, Page<AccountResponse>, ApiResponse<Page<AccountResponse>>
Validations  : none (read-only)
Errors       : none beyond platform standard
Orchestration: QR-FIN-002 FIND_BY_CRITERIA
Repository   : QR-FIN-002 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-001 · PERM_FIN_COA_VIEW
Localization : not applicable
<!-- API:API-FIN-002:END -->

<!-- API:API-FIN-003:START traces=REQ-FIN-001,DBF-FIN-001 -->
#### API-FIN-003 — read account
Endpoint     : GET /api/v1/fin/accounts/{id}
Layers       : AccountController.read → AccountService.read → AccountRepository
Request      : path: id
Response     : 200, AccountResponse, ApiResponse<AccountResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-003 FIND_ONE
Repository   : QR-FIN-003 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-001 · PERM_FIN_COA_VIEW
Localization : not applicable
<!-- API:API-FIN-003:END -->

<!-- API:API-FIN-007:START traces=REQ-FIN-004,DBF-FIN-015 -->
#### API-FIN-007 — search dimensions
Endpoint     : GET /api/v1/fin/dimensions
Layers       : DimensionController.search → DimensionService.search → DimensionRepository
Request      : query: dimensionKey?, nameAr?, nameEn?, isActiveFl?, page, size
Response     : 200, Page<DimensionResponse>, ApiResponse<Page<DimensionResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-007 FIND_BY_CRITERIA
Repository   : QR-FIN-007 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-002 · PERM_FIN_DIM_VIEW
Localization : not applicable
<!-- API:API-FIN-007:END -->

<!-- API:API-FIN-008:START traces=REQ-FIN-004,DBF-FIN-015 -->
#### API-FIN-008 — read dimension
Endpoint     : GET /api/v1/fin/dimensions/{id}
Layers       : DimensionController.read → DimensionService.read → DimensionRepository
Request      : path: id
Response     : 200, DimensionResponse (+ values[]), ApiResponse<DimensionResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-008 FIND_ONE
Repository   : QR-FIN-008 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-002 · PERM_FIN_DIM_VIEW
Localization : not applicable
<!-- API:API-FIN-008:END -->

<!-- API:API-FIN-012:START traces=REQ-FIN-006,DBF-FIN-028 -->
#### API-FIN-012 — search lookups
Endpoint     : GET /api/v1/fin/lookups
Layers       : LookupController.search → LookupService.search → LookupRepository
Request      : query: lookupKey?, nameAr?, nameEn?, page, size
Response     : 200, Page<LookupResponse>, ApiResponse<Page<LookupResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-012 FIND_BY_CRITERIA
Repository   : QR-FIN-012 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-003 · PERM_FIN_LKP_VIEW
Localization : not applicable
<!-- API:API-FIN-012:END -->

<!-- API:API-FIN-013:START traces=REQ-FIN-006,DBF-FIN-028 -->
#### API-FIN-013 — read lookup
Endpoint     : GET /api/v1/fin/lookups/{id}
Layers       : LookupController.read → LookupService.read → LookupRepository
Request      : path: id
Response     : 200, LookupResponse (+ values[]), ApiResponse<LookupResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-013 FIND_ONE
Repository   : QR-FIN-013 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-003 · PERM_FIN_LKP_VIEW
Localization : not applicable
<!-- API:API-FIN-013:END -->

<!-- API:API-FIN-017:START traces=REQ-FIN-008,DBF-FIN-040 -->
#### API-FIN-017 — search event-type rules
Endpoint     : GET /api/v1/fin/rules
Layers       : EventRuleController.search → EventRuleService.search → EventRuleRepository
Request      : query: eventTypeCode?, isActiveFl?, page, size
Response     : 200, Page<EventRuleResponse>, ApiResponse<Page<EventRuleResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-017 FIND_BY_CRITERIA
Repository   : QR-FIN-017 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-004 · PERM_FIN_RULE_VIEW
Localization : not applicable
<!-- API:API-FIN-017:END -->

<!-- API:API-FIN-018:START traces=REQ-FIN-008,DBF-FIN-040 -->
#### API-FIN-018 — read event-type rule
Endpoint     : GET /api/v1/fin/rules/{id}
Layers       : EventRuleController.read → EventRuleService.read → EventRuleRepository
Request      : path: id
Response     : 200, EventRuleResponse (+ lines[]), ApiResponse<EventRuleResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-018 FIND_ONE
Repository   : QR-FIN-018 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-004 · PERM_FIN_RULE_VIEW
Localization : not applicable
<!-- API:API-FIN-018:END -->

<!-- API:API-FIN-022:START traces=REQ-FIN-016,DBF-FIN-094 -->
#### API-FIN-022 — search recurring templates
Endpoint     : GET /api/v1/fin/recurring-templates
Layers       : RecurringTemplateController.search → RecurringTemplateService.search → RecurringTemplateRepository
Request      : query: templateNameAr?, templateNameEn?, templateTypeCode?, isActiveFl?, page, size
Response     : 200, Page<RecurringTemplateResponse>, ApiResponse<Page<RecurringTemplateResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-022 FIND_BY_CRITERIA
Repository   : QR-FIN-022 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-005 · PERM_FIN_TMPL_VIEW
Localization : not applicable
<!-- API:API-FIN-022:END -->

<!-- API:API-FIN-023:START traces=REQ-FIN-016,DBF-FIN-094 -->
#### API-FIN-023 — read recurring template
Endpoint     : GET /api/v1/fin/recurring-templates/{id}
Layers       : RecurringTemplateController.read → RecurringTemplateService.read → RecurringTemplateRepository
Request      : path: id
Response     : 200, RecurringTemplateResponse (+ lines[]), ApiResponse<RecurringTemplateResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-023 FIND_ONE
Repository   : QR-FIN-023 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-005 · PERM_FIN_TMPL_VIEW
Localization : not applicable
<!-- API:API-FIN-023:END -->

<!-- API:API-FIN-027:START traces=REQ-FIN-017,DBF-FIN-115 -->
#### API-FIN-027 — search allocation rules
Endpoint     : GET /api/v1/fin/allocation-rules
Layers       : AllocationRuleController.search → AllocationRuleService.search → AllocationRuleRepository
Request      : query: ruleNameAr?, ruleNameEn?, sourceAccountId?, isActiveFl?, page, size
Response     : 200, Page<AllocationRuleResponse>, ApiResponse<Page<AllocationRuleResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-027 FIND_BY_CRITERIA
Repository   : QR-FIN-027 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-006 · PERM_FIN_ALLOC_VIEW
Localization : not applicable
<!-- API:API-FIN-027:END -->

<!-- API:API-FIN-028:START traces=REQ-FIN-017,DBF-FIN-115 -->
#### API-FIN-028 — read allocation rule
Endpoint     : GET /api/v1/fin/allocation-rules/{id}
Layers       : AllocationRuleController.read → AllocationRuleService.read → AllocationRuleRepository
Request      : path: id
Response     : 200, AllocationRuleResponse (+ lines[]), ApiResponse<AllocationRuleResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-028 FIND_ONE
Repository   : QR-FIN-028 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-006 · PERM_FIN_ALLOC_VIEW
Localization : not applicable
<!-- API:API-FIN-028:END -->

<!-- API:API-FIN-033:START traces=REQ-FIN-018,DBF-FIN-067 -->
#### API-FIN-033 — search journal entries
Endpoint     : GET /api/v1/fin/journal-entries
Layers       : JournalEntryController.search → JournalEntryService.search → JournalEntryRepository
Request      : query: entryNo?, entryDateFrom?, entryDateTo?, sourceTypeCode?, statusCode?, periodId?, accountId?, page, size
Response     : 200, Page<JournalEntryResponse>, ApiResponse<Page<JournalEntryResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-033 FIND_BY_CRITERIA
Repository   : QR-FIN-033 · FIND_BY_CRITERIA · join required (fin_journal_entry_line when filtering by accountId) — ADR-FIN-006 · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-007 · PERM_FIN_JE_VIEW
Localization : not applicable
<!-- API:API-FIN-033:END -->

<!-- API:API-FIN-034:START traces=REQ-FIN-018,REQ-FIN-034,DBF-FIN-067 -->
#### API-FIN-034 — read journal entry
Endpoint     : GET /api/v1/fin/journal-entries/{id}
Layers       : JournalEntryController.read → JournalEntryService.read → JournalEntryRepository
Request      : path: id
Response     : 200, JournalEntryResponse (+ lines[], sourceEventReference when EVENT-sourced — REQ-FIN-034 drill-down), ApiResponse<JournalEntryResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-034 FIND_ONE
Repository   : QR-FIN-034 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-007 · PERM_FIN_JE_VIEW
Localization : not applicable
<!-- API:API-FIN-034:END -->

<!-- API:API-FIN-037:START traces=REQ-FIN-027,DBF-FIN-136 -->
#### API-FIN-037 — search fiscal years
Endpoint     : GET /api/v1/fin/fiscal-years
Layers       : FiscalYearController.search → FiscalYearService.search → FiscalYearRepository
Request      : query: yearCode?, statusCode?, page, size
Response     : 200, Page<FiscalYearResponse>, ApiResponse<Page<FiscalYearResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-037 FIND_BY_CRITERIA
Repository   : QR-FIN-037 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-008 · PERM_FIN_PERIOD_VIEW
Localization : not applicable
<!-- API:API-FIN-037:END -->

<!-- API:API-FIN-038:START traces=REQ-FIN-027,DBF-FIN-136 -->
#### API-FIN-038 — read fiscal year
Endpoint     : GET /api/v1/fin/fiscal-years/{id}
Layers       : FiscalYearController.read → FiscalYearService.read → FiscalYearRepository
Request      : path: id
Response     : 200, FiscalYearResponse (+ periods[]), ApiResponse<FiscalYearResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-038 FIND_ONE
Repository   : QR-FIN-038 · FIND_ONE · join NONE (fin_fiscal_period fetched as an owned collection) · transaction READ_ONLY
Security     : SCR-REQ-FIN-008 · PERM_FIN_PERIOD_VIEW
Localization : not applicable
<!-- API:API-FIN-038:END -->

<!-- API:API-FIN-042:START traces=REQ-FIN-032,REQ-FIN-034,DBF-FIN-086 -->
#### API-FIN-042 — account ledger report
Endpoint     : GET /api/v1/fin/reports/account-ledger
Layers       : ReportController.accountLedger → ReportService.accountLedger → JournalEntryLineRepository
Request      : query: accountId, dimensionValueIds[]?, periodId? | dateFrom?/dateTo?, page, size
Response     : 200, Page<AccountLedgerLineResponse> (entryNo, entryDate, directionCode, amount, runningBalance), ApiResponse<Page<AccountLedgerLineResponse>>
Validations  : POL-FIN-009 / RULE derivation — reads POSTED lines only (statusCode='POSTED' filter, never a materialized balance column)
Errors       : none beyond platform standard
Orchestration: QR-FIN-042 FIND_BY_CRITERIA (filter statusCode='POSTED') → compute running balance in the service layer (no stored balance column, REQ-FIN-032)
Repository   : QR-FIN-042 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-009 · PERM_FIN_LEDGER_VIEW
Localization : not applicable
<!-- API:API-FIN-042:END -->

<!-- API:API-FIN-043:START traces=REQ-FIN-032,REQ-FIN-034,DBF-FIN-086 -->
#### API-FIN-043 — trial balance report
Endpoint     : GET /api/v1/fin/reports/trial-balance
Layers       : ReportController.trialBalance → ReportService.trialBalance → JournalEntryLineRepository
Request      : query: periodId? | dateFrom?/dateTo?, accountType?
Response     : 200, List<TrialBalanceRowResponse> (account, debitTotal, creditTotal), ApiResponse<List<TrialBalanceRowResponse>>
Validations  : POSTED-only (REQ-FIN-032)
Errors       : none
Orchestration: QR-FIN-043 AGGREGATE (SUM debit/credit GROUP BY account, statusCode='POSTED')
Repository   : QR-FIN-043 · AGGREGATE · join NONE · transaction READ_ONLY · Pagination NO
Security     : SCR-REQ-FIN-010 · PERM_FIN_TB_VIEW
Localization : not applicable
<!-- API:API-FIN-043:END -->

<!-- API:API-FIN-044:START traces=REQ-FIN-032,REQ-FIN-034,DBF-FIN-086 -->
#### API-FIN-044 — balance sheet report
Endpoint     : GET /api/v1/fin/reports/balance-sheet
Layers       : ReportController.balanceSheet → ReportService.balanceSheet → JournalEntryLineRepository
Request      : query: asOfDate, fiscalYearId
Response     : 200, BalanceSheetResponse (grouped by accountType: asset, liability, equity), ApiResponse<BalanceSheetResponse>
Validations  : POSTED-only (REQ-FIN-032)
Errors       : none
Orchestration: QR-FIN-044 AGGREGATE (SUM balances GROUP BY accountType WHERE accountType IN (asset,liability,equity), statusCode='POSTED', entryDate<=asOfDate)
Repository   : QR-FIN-044 · AGGREGATE · join NONE · transaction READ_ONLY · Pagination NO
Security     : SCR-REQ-FIN-011 · PERM_FIN_BS_VIEW
Localization : not applicable
<!-- API:API-FIN-044:END -->

<!-- API:API-FIN-045:START traces=REQ-FIN-032,REQ-FIN-034,DBF-FIN-086 -->
#### API-FIN-045 — income statement report
Endpoint     : GET /api/v1/fin/reports/income-statement
Layers       : ReportController.incomeStatement → ReportService.incomeStatement → JournalEntryLineRepository
Request      : query: periodFrom, periodTo, fiscalYearId
Response     : 200, IncomeStatementResponse (grouped by accountType: revenue, expense), ApiResponse<IncomeStatementResponse>
Validations  : POSTED-only (REQ-FIN-032)
Errors       : none
Orchestration: QR-FIN-045 AGGREGATE (SUM balances GROUP BY accountType IN (revenue,expense), statusCode='POSTED', period range)
Repository   : QR-FIN-045 · AGGREGATE · join NONE · transaction READ_ONLY · Pagination NO
Security     : SCR-REQ-FIN-012 · PERM_FIN_IS_VIEW
Localization : not applicable
<!-- API:API-FIN-045:END -->

<!-- API:API-FIN-046:START traces=REQ-FIN-033,REQ-FIN-034,DBF-FIN-093 -->
#### API-FIN-046 — dimension report
Endpoint     : GET /api/v1/fin/reports/dimension-reports
Layers       : ReportController.dimensionReport → ReportService.dimensionReport → JournalEntryLineDimRepository
Request      : query: dimensionKey, dimensionValueId, periodFrom?, periodTo?
Response     : 200, List<DimensionReportRowResponse> (account, dimensionValue, balance), ApiResponse<List<DimensionReportRowResponse>>
Validations  : POSTED-only (REQ-FIN-032); no account duplication per dimension value (REQ-FIN-033 — the same account row is reused, filtered by dimension)
Errors       : none
Orchestration: QR-FIN-046 AGGREGATE (join fin_journal_entry_line_dim → fin_journal_entry_line, GROUP BY account/dimension value, statusCode='POSTED')
Repository   : QR-FIN-046 · AGGREGATE · join required (fin_journal_entry_line_dim ↔ fin_journal_entry_line) — intra-module, no ADR needed (both tables owned by this module, REQ-FIN-033 explicitly requires the join to avoid account duplication) · transaction READ_ONLY · Pagination NO
Security     : SCR-REQ-FIN-013 · PERM_FIN_DIMRPT_VIEW
Localization : not applicable
<!-- API:API-FIN-046:END -->

<!-- API:API-FIN-049:START traces=REQ-FIN-025,DBF-FIN-164 -->
#### API-FIN-049 — search users
Endpoint     : GET /api/v1/fin/users
Layers       : UserController.search → UserService.search → UserRepository
Request      : query: username?, nameAr?, nameEn?, isActiveFl?, page, size
Response     : 200, Page<UserResponse>, ApiResponse<Page<UserResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-049 FIND_BY_CRITERIA
Repository   : QR-FIN-049 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-015 · PERM_FIN_USER_VIEW
Localization : not applicable
<!-- API:API-FIN-049:END -->

<!-- API:API-FIN-050:START traces=REQ-FIN-025,DBF-FIN-164 -->
#### API-FIN-050 — read user
Endpoint     : GET /api/v1/fin/users/{id}
Layers       : UserController.read → UserService.read → UserRepository
Request      : path: id
Response     : 200, UserResponse (excludes passwordHash), ApiResponse<UserResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-050 FIND_ONE
Repository   : QR-FIN-050 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : SCR-REQ-FIN-015 · PERM_FIN_USER_VIEW
Localization : not applicable
<!-- API:API-FIN-050:END -->

<!-- API:API-FIN-054:START traces=REQ-FIN-025,DBF-FIN-175 -->
#### API-FIN-054 — search roles
Endpoint     : GET /api/v1/fin/roles
Layers       : RoleController.search → RoleService.search → RoleRepository
Request      : query: roleCode?, roleNameAr?, roleNameEn?, isActiveFl?, page, size
Response     : 200, Page<RoleResponse>, ApiResponse<Page<RoleResponse>>
Validations  : none
Errors       : none
Orchestration: QR-FIN-054 FIND_BY_CRITERIA
Repository   : QR-FIN-054 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY · Pagination YES
Security     : SCR-REQ-FIN-016 · PERM_FIN_ROLE_VIEW
Localization : not applicable
<!-- API:API-FIN-054:END -->

<!-- API:API-FIN-055:START traces=REQ-FIN-025,REQ-FIN-026,DBF-FIN-175 -->
#### API-FIN-055 — read role
Endpoint     : GET /api/v1/fin/roles/{id}
Layers       : RoleController.read → RoleService.read → RoleRepository
Request      : path: id
Response     : 200, RoleResponse (+ permissions[], assignedUsers[]), ApiResponse<RoleResponse>
Validations  : none
Errors       : FIN-PLATFORM-404 (404)
Orchestration: QR-FIN-055 FIND_ONE
Repository   : QR-FIN-055 · FIND_ONE · join NONE (owned collections) · transaction READ_ONLY
Security     : SCR-REQ-FIN-016 · PERM_FIN_ROLE_VIEW
Localization : not applicable
<!-- API:API-FIN-055:END -->
<!-- SUB:SVC-API-SEARCH:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-FIN-018,REQ-FIN-025 -->
## PHASE 4 — DOC (contract documentation, backend self-check only)

This section is **not** the published contract — after implementation the backend repo
publishes `governance/api-docs/api-docs-fin.md`, which is the only file the frontend
stage (`P3.2`) reads. This summary exists so `gov.py analyze`'s C7 contracts have a
self-contained artifact to check before that publication happens.

**API contract summary** (58 endpoints — full detail in PHASE:SVC-API):
| Group | Count | Verbs | Stability |
|---|---|---|---|
| Chart of Accounts (API-FIN-001…005) | 5 | POST,GET,GET,PUT,DELETE | stable |
| Dimensions (API-FIN-006…010) | 5 | POST,GET,GET,PUT,DELETE | stable |
| Lookups (API-FIN-011…015) | 5 | POST,GET,GET,PUT,DELETE | stable |
| Engine Rules (API-FIN-016…020) | 5 | POST,GET,GET,PUT,DELETE | stable |
| Recurring Templates (API-FIN-021…025) | 5 | POST,GET,GET,PUT,DELETE | stable |
| Allocation Rules (API-FIN-026…031) | 6 | POST,GET,GET,PUT,DELETE,POST(run) | stable |
| Journal Entries (API-FIN-032…035) | 4 | POST,GET,GET,POST(reverse) | stable |
| Fiscal Years/Periods (API-FIN-036…041) | 6 | POST,GET,GET,POST(approve),POST(year-end),POST(period) | stable |
| Reports (API-FIN-042…046) | 5 | GET × 5 | stable |
| Auth (API-FIN-047) | 1 | POST | stable |
| Users (API-FIN-048…052) | 5 | POST,GET,GET,PUT,DELETE | stable |
| Roles (API-FIN-053…058) | 6 | POST,GET,GET,PUT,DELETE,POST(assign) | stable |

**DTO typing constraints**: every lookup-backed property is `String` holding the code (never an enum, never the display label — CORE); business code (`entryNo`) never appears in a create/update request body, always in every response that includes a Journal Entry (R3 rule).

**Pagination + filter standard**: request shape `{filters, sort, page, size}`; allowed sort fields = the query parameters listed per endpoint above; empty result set = 200 with empty `content[]`, never a "not found" error (CORE search contract).
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=REQ-FIN-001 -->
## PHASE 5 — INT-C (cross-module consume)

No content. FIN declares zero cross-module dependencies — `DEPENDENCIES: NONE`,
`ROOT: YES` (module-registry-fin.md; SRS A8; db-script-fin.md §2, 0 XM). This phase's
marker pair is emitted for structural completeness per §6.0 (every profile phase key
gets exactly one PHASE START/END pair); it is traced to REQ-FIN-001 (the module's
foundational requirement) only because the marker grammar requires ≥1 trace id on
every PHASE block — there is no cross-module consume content to trace to anything
more specific.
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-FIN-001 -->
## PHASE 6 — INT-R (cross-module resolve)

No content, for the same reason as PHASE:INT-C above — 0 XM records exist in
db-script-fin.md for FIN to resolve or activate at runtime. No inbound consumer has
registered an `XM-INBOUND-STUB` against FIN in `project-registry.md` CAT-6 as of this
version.
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=REQ-FIN-025,REQ-FIN-026,REQ-FIN-021,REQ-FIN-022 -->
## PHASE 7 — SEC-BE (security, backend half)

Enforced per `profile.conventions.security_model`: page registry `SEC_PAGES`,
permission pattern `PERM_<PAGE_CODE>_<ACTION>`, actions `VIEW/CREATE/UPDATE/DELETE`,
gateway action `VIEW` (without VIEW no other permission applies). FIN's `SEC_PAGES`
and permission rows are FIN's own — independent of the platform's shared security
module (POL-FIN-008), stored in `fin_role_permission.page_code` (DBF-FIN-186), never
shared with `SEC`.

**SEC_PAGES seed** (one row per composite screen, `srs-fin.md` PART B):
| Page code | Screen (SCR-REQ) | Gateway (VIEW) mutation permissions declared |
|---|---|---|
| FIN_COA | SCR-REQ-FIN-001 | PERM_FIN_COA_VIEW, _CREATE, _UPDATE, _DELETE |
| FIN_DIM | SCR-REQ-FIN-002 | PERM_FIN_DIM_VIEW, _CREATE, _UPDATE, _DELETE |
| FIN_LKP | SCR-REQ-FIN-003 | PERM_FIN_LKP_VIEW, _CREATE, _UPDATE, _DELETE |
| FIN_RULE | SCR-REQ-FIN-004 | PERM_FIN_RULE_VIEW, _CREATE, _UPDATE, _DELETE |
| FIN_TMPL | SCR-REQ-FIN-005 | PERM_FIN_TMPL_VIEW, _CREATE, _UPDATE, _DELETE |
| FIN_ALLOC | SCR-REQ-FIN-006 | PERM_FIN_ALLOC_VIEW, _CREATE, _UPDATE, _DELETE |
| FIN_JE | SCR-REQ-FIN-007 | PERM_FIN_JE_VIEW, _CREATE, _UPDATE |
| FIN_PERIOD | SCR-REQ-FIN-008 | PERM_FIN_PERIOD_VIEW, _CREATE, _UPDATE |
| FIN_LEDGER | SCR-REQ-FIN-009 | PERM_FIN_LEDGER_VIEW |
| FIN_TB | SCR-REQ-FIN-010 | PERM_FIN_TB_VIEW |
| FIN_BS | SCR-REQ-FIN-011 | PERM_FIN_BS_VIEW |
| FIN_IS | SCR-REQ-FIN-012 | PERM_FIN_IS_VIEW |
| FIN_DIMRPT | SCR-REQ-FIN-013 | PERM_FIN_DIMRPT_VIEW |
| FIN_LOGIN | SCR-REQ-FIN-014 | none (pre-authentication, no gateway required) |
| FIN_USER | SCR-REQ-FIN-015 | PERM_FIN_USER_VIEW, _CREATE, _UPDATE, _DELETE |
| FIN_ROLE | SCR-REQ-FIN-016 | PERM_FIN_ROLE_VIEW, _CREATE, _UPDATE, _DELETE |

Every permission name above matches `srs-fin.md` PART B §B4 (Access) exactly — no
permission appears in this plan that is absent from the SRS access matrix
(`ERP-4`, MAJOR — every mutation endpoint above declares its `PERM_*` requirement,
see the Security row on each API-FIN-* block).

Role → default permission grants (from `srs-fin.md` STANDALONE Access summary):
Accounting Configuration Administrator → FIN_COA/FIN_DIM/FIN_LKP/FIN_RULE full;
Accountant → FIN_TMPL/FIN_ALLOC/FIN_JE full (create/update, no delete on FIN_JE per
RULE-FIN-006), FIN_COA/FIN_DIM/FIN_LKP/FIN_RULE/FIN_LEDGER/FIN_TB/FIN_BS/FIN_IS view;
Financial Controller → FIN_PERIOD full, FIN_LEDGER/FIN_TB/FIN_BS/FIN_IS/FIN_DIMRPT
view, FIN_TMPL/FIN_ALLOC/FIN_JE view (RULE-FIN-008 SoD keeps this role out of
FIN_JE create); Accounting System Administrator → FIN_USER/FIN_ROLE full; Auditor →
FIN_LEDGER/FIN_TB/FIN_BS/FIN_IS/FIN_DIMRPT/FIN_JE view (all read-only).

Forbidden responses (permission denied, gateway missing) map to `FIN-PLATFORM-403`
via `LocalizedException → {code, messageAr, messageEn}` (Error Catalog, trailing).
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-FIN-001,REQ-FIN-018,REQ-FIN-025,REQ-FIN-032 -->
## PHASE 8 — ALIGN-BE (self-check)

```
ALIGN — FIN v1
TRACEABILITY      ✓ every API-*/QR-*/RULE-*/DBF-* used in a phase appears in the Plan Index │ ✓ every PHASE/SUB/API/XM block carries traces= │ ✓ every traces target exists upstream (srs-fin.md, db-script-fin.md)
BINDING (§2A)     ✓ no placeholder table/column/key/generation object │ ✓ no "see SRS" anywhere — every RULE cited in an API block carries its full statement + ar/en message │ ✓ every column cites a DBF (DB Alignment Manifest) │ ✓ business code format explicit (entryNo — CORE + ENT-FIN-006 block)
MANIFEST (§4)     ✓ only the 6 mandated columns │ ✓ all 190/190 DBF listed │ ✓ 0 ⏸ rows (0 XM, nothing deferred)
QRC (§5)          ✓ every API with a DB operation has a QR (58/58) │ ✓ every QR carries the agent-reference warning (QRC header, trailing) │ ✓ no join for lookup labels (CORE: lookup fields return code only) │ ✓ exact generation object named (GENERATED ALWAYS AS IDENTITY, per table)
API (R3)          ✓ every RULE in Validations has a catalog row (Error Catalog, trailing) │ ✓ platform errors use RULE=PLATFORM-STD equivalent (FIN-PLATFORM-*) │ ✓ create/update DTOs exclude system fields (PK, audit, business code) │ ✓ business code present in every Journal Entry response
CROSS-MODULE      ✓ 0 XM from db-script-fin.md — nothing to place │ n/a DEFERRED strategy (none exist) │ n/a inbound stubs (none registered)
SECURITY (R7)     ✓ every API serving a screen declares its PERM_* (58/58) │ ✓ every screen has a SEC_PAGES seed row (16/16) │ ✓ no permission outside the SRS access matrix
CORE (R1)         ✓ layers declared │ ✓ domain placement declared (RULE-* in aggregate root methods) │ ✓ error signalling declared (LocalizedException triple) │ ✓ type mapping declared (postgresql16 → Java table)
DECISIONS         ✓ ADR-FIN-001…003 carried (P1) │ ✓ ADR-FIN-004…005 carried (P2) │ ✓ ADR-FIN-006 (this stage, join governance) │ 0 BLOCKED
RESULT            PASSED ✓ — 0 findings
```

**Coverage — ENT/DBF → phases → QR → XM**: every one of the 13 ENT-FIN-* blocks
(PHASE:DATA-DOM) names its table(s), every DBF-FIN-* (190) is bound in the DB
Alignment Manifest, every ENT's "REPOSITORY OPS" line names its QR-FIN-* id(s); XM
column is empty throughout (0 XM).

**Coverage — RULE → API → catalog code**: all 14 RULE-FIN-* ids appear in at least
one API-FIN-* block's Validations field (RULE-FIN-001: API-FIN-032; RULE-FIN-002:
API-FIN-032, ADR-FIN-004; RULE-FIN-003: API-FIN-032; RULE-FIN-004: API-FIN-032;
RULE-FIN-005: API-FIN-016, 019, 026, 029, 031; RULE-FIN-006: API-FIN-035, ADR-FIN-005;
RULE-FIN-007: API-FIN-035; RULE-FIN-008: API-FIN-039; RULE-FIN-009: API-FIN-039;
RULE-FIN-010: API-FIN-040; RULE-FIN-011: API-FIN-001, 004, 040; RULE-FIN-012:
API-FIN-016; RULE-FIN-013: PHASE:DATA-DOM ENT-FIN-008 (scheduler, not a REST API);
RULE-FIN-014: API-FIN-026, 029, 031) — every one has an Error Catalog row (trailing).

**Coverage — XM → status → blocks → workaround**: not applicable, 0 XM.

**Coverage — REQ orphan check**: all 34 REQ-FIN-* ids are referenced by ≥1 API-FIN-*
or DBF-FIN-* trace across db-script-fin.md and this plan (REQ-FIN-013, 015, 020, 022,
024, 028, 029, 030, 032, 033 — the ids not covered by a DBF anchor trace in
db-script-fin.md — are each covered here: 013→API-FIN-016, 015→API-FIN-032,
020→API-FIN-032, 022→API-FIN-039, 024→API-FIN-035, 028→API-FIN-032, 029→API-FIN-039,
030→API-FIN-040, 032→API-FIN-042…046, 033→API-FIN-046).
<!-- PHASE:ALIGN-BE:END -->

## ERROR CATALOG — FIN v1

| code | RULE-* | API-* | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| FIN-RULE-001 | RULE-FIN-001 | API-FIN-032, API-FIN-035 | 409 | posting to a non-postable/inactive account | لا يمكن الترحيل إلى حساب غير نشط أو غير قابل للترحيل المباشر | Cannot post to an inactive or non-postable account |
| FIN-RULE-002 | RULE-FIN-002 | API-FIN-032, API-FIN-035 | 409 | debit total ≠ credit total | مجموع المدين لا يساوي مجموع الدائن | Debit total does not equal credit total |
| FIN-RULE-003 | RULE-FIN-003 | API-FIN-032, API-FIN-035 | 409 | invalid/inactive dimension value on a line | قيمة البُعد غير صالحة أو غير نشطة | Dimension value is invalid or inactive |
| FIN-RULE-004 | RULE-FIN-004 | API-FIN-032, API-FIN-035, API-FIN-031 | 409 | posting to a non-Open period | الفترة غير مفتوحة للترحيل | Period is not open for posting |
| FIN-RULE-005 | RULE-FIN-005 | API-FIN-016, API-FIN-019, API-FIN-026, API-FIN-029, API-FIN-031 | 400 | distribution shape missing/malformed remainder line | يجب وجود سطر متبقي واحد فقط لاستيعاب فرق التقريب | Exactly one remainder line is required to absorb the rounding difference |
| FIN-RULE-006 | RULE-FIN-006 | (internal — DB trigger, ADR-FIN-005) | 409 | edit/delete attempted on a POSTED entry | القيد المرحّل مقفل ولا يمكن تعديله أو حذفه | A posted entry is locked and cannot be edited or deleted |
| FIN-RULE-007 | RULE-FIN-007 | API-FIN-035 | 500 | a reversal entry missing reversalOfEntryId (defensive — should never occur) | يجب ربط قيد العكس بالقيد الأصلي | A reversing entry must reference the original entry |
| FIN-RULE-008 | RULE-FIN-008 | API-FIN-039 | 403 | entry creator attempts to approve their own period's close | لا يمكن لمنشئ القيد اعتماد إقفال الفترة | The entry's creator cannot approve the period close |
| FIN-RULE-009 | RULE-FIN-009 | API-FIN-039 | 409 | reopen/post attempted on a Hard Closed period | الفترة مقفلة إقفالاً نهائياً | Period is permanently closed |
| FIN-RULE-010 | RULE-FIN-010 | API-FIN-040 | 409 | year-end close attempted with a period not Hard Closed | يجب إقفال جميع فترات السنة إقفالاً نهائياً أولاً | All periods of the year must be Hard Closed first |
| FIN-RULE-011 | RULE-FIN-011 | API-FIN-001, API-FIN-004, API-FIN-040 | 409 | zero or multiple active Retained-Earnings accounts | يجب تحديد حساب واحد فقط للأرباح المحتجزة | Exactly one Retained Earnings account must be designated |
| FIN-RULE-012 | RULE-FIN-012 | API-FIN-016 | 409 | a second active rule for one event type | يوجد بالفعل قاعدة نشطة لهذا النوع من الأحداث | An active rule already exists for this event type |
| FIN-RULE-013 | RULE-FIN-013 | (internal — scheduler, PHASE:DATA-DOM ENT-FIN-008) | n/a (no HTTP — background job log entry) | scheduled run hits an inactive template account | تم تخطي القالب — الحساب غير نشط | Template skipped — account is inactive |
| FIN-RULE-014 | RULE-FIN-014 | API-FIN-026, API-FIN-029, API-FIN-031 | 400/409 | allocation lines don't total the source balance | يجب أن يساوي مجموع سطور التوزيع رصيد المصدر بالكامل | Allocation lines must total exactly the source balance |
| FIN-PLATFORM-400 | PLATFORM-STD | multiple (DTO validation) | 400 | request DTO fails bean validation | طلب غير صالح | Invalid request |
| FIN-PLATFORM-401 | PLATFORM-STD | API-FIN-047 | 401 | invalid login credentials | بيانات الدخول غير صحيحة | Invalid credentials |
| FIN-PLATFORM-403 | PLATFORM-STD | multiple (PHASE:SEC-BE) | 403 | permission or gateway VIEW missing; inactive user login | غير مصرح بهذا الإجراء | Not authorized for this action |
| FIN-PLATFORM-404 | PLATFORM-STD | multiple | 404 | resource not found by id | العنصر غير موجود | Resource not found |
| FIN-PLATFORM-409 | PLATFORM-STD | multiple (UNIQUE constraint) | 409 | a UQ_FIN_* constraint violated | القيمة مستخدمة بالفعل | Value already in use |

Runtime code format (stated once, per §7): `FIN-<RULE-seq|PLATFORM>-<3-digit-or-status>` —
e.g. `FIN-RULE-002`, `FIN-PLATFORM-404` — serialised verbatim in `LocalizedException.code`,
asserted on by the standalone `api-verify` stage.

## QUERY REFERENCE CATALOG (QR-*) — FIN v1

> Agent reference only — pseudo-SQL logical specification. The implementer rewrites
> every entry with real entity classes, mapped property names and the project's query
> strategy (Spring Data / JPQL / criteria API). Copy-pasting a QR entry into production
> code is a governance violation (§5).

QR-FIN-001 — create account
Phase        : PHASE:SVC-API (SUB:SVC-API-CRUD)
API          : API-FIN-001
Entity       : ENT-FIN-001
Operation    : SAVE
Intent       : persist a new chart-of-accounts row
Logical spec : INSERT INTO fin_account (parent_account_id, code, name_ar, name_en, account_type, nature_code, accepts_direct_posting_fl, is_retained_earnings_account_fl, is_active_fl, created_by, created_at, updated_by, updated_at) VALUES (…)
Join         : NONE
Transaction  : READ_WRITE
Pagination   : NO
Filters      : n/a
Result shape : full entity
Null handling: parent_account_id NULL when root account

QR-FIN-002 — search accounts
Phase        : PHASE:SVC-API (SUB:SVC-API-SEARCH)
API          : API-FIN-002
Entity       : ENT-FIN-001
Operation    : FIND_BY_CRITERIA
Intent       : filtered, paged account list
Logical spec : SELECT * FROM fin_account WHERE (code LIKE :code OR :code IS NULL) AND (name_ar LIKE :nameAr OR :nameAr IS NULL) AND (name_en LIKE :nameEn OR :nameEn IS NULL) AND (account_type = :accountType OR :accountType IS NULL) AND (is_active_fl = :isActiveFl OR :isActiveFl IS NULL) ORDER BY code
Join         : NONE
Transaction  : READ_ONLY
Pagination   : YES (Page<T>)
Filters      : code: LIKE · nameAr/nameEn: LIKE · accountType: EXACT · isActiveFl: EXACT
Result shape : full entity
Null handling: empty result = success, empty content[]

QR-FIN-003 — read account
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-003 · Entity: ENT-FIN-001 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_account WHERE account_pk = :id
Join: NONE · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full entity · Null handling: not found → FIN-PLATFORM-404

QR-FIN-004 — update account
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-004 · Entity: ENT-FIN-001 · Operation: UPDATE
Logical spec : UPDATE fin_account SET parent_account_id=:parentAccountId, name_ar=:nameAr, name_en=:nameEn, account_type=:accountType, nature_code=:natureCode, accepts_direct_posting_fl=:acceptsDirectPostingFl, is_retained_earnings_account_fl=:isRetainedEarningsAccountFl, updated_by=:principal, updated_at=now() WHERE account_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full entity · Null handling: code excluded (immutable)

QR-FIN-005 — deactivate account
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-005 · Entity: ENT-FIN-001 · Operation: UPDATE
Logical spec : UPDATE fin_account SET is_active_fl=false, updated_by=:principal, updated_at=now() WHERE account_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none (204) · Null handling: not found → FIN-PLATFORM-404

QR-FIN-006 — create dimension (+ nested values)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-006 · Entity: ENT-FIN-002 · Operation: SAVE
Logical spec : INSERT INTO fin_dimension (…) VALUES (…); INSERT INTO fin_dimension_value (dimension_id, value_code, value_name_ar, value_name_en, sort_order, is_active_fl) VALUES (…) [per value row]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate · Null handling: values[] optional at create

QR-FIN-007 — search dimensions
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-007 · Entity: ENT-FIN-002 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_dimension WHERE (dimension_key LIKE :key OR :key IS NULL) AND (name_ar LIKE :nameAr OR :nameAr IS NULL) AND (is_active_fl=:isActiveFl OR :isActiveFl IS NULL)
Join: NONE · Transaction: READ_ONLY · Pagination: YES · Filters: dimensionKey/nameAr/nameEn LIKE, isActiveFl EXACT · Result shape: full entity (values excluded from list rows) · Null handling: empty = success

QR-FIN-008 — read dimension (+ values)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-008 · Entity: ENT-FIN-002 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_dimension WHERE dimension_pk=:id; SELECT * FROM fin_dimension_value WHERE dimension_id=:id ORDER BY sort_order
Join: NONE (two queries, owned collection) · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-009 — update dimension
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-009 · Entity: ENT-FIN-002 · Operation: UPDATE
Logical spec : UPDATE fin_dimension SET name_ar, name_en, control_type WHERE dimension_pk=:id; replace fin_dimension_value rows for :id per values[]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: n/a

QR-FIN-010 — deactivate dimension
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-010 · Entity: ENT-FIN-002 · Operation: UPDATE
Logical spec : UPDATE fin_dimension SET is_active_fl=false WHERE dimension_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none · Null handling: not found → 404

QR-FIN-011 — create lookup type (+ nested values)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-011 · Entity: ENT-FIN-003 · Operation: SAVE
Logical spec : INSERT INTO fin_lookup_type (…); INSERT INTO fin_lookup_value (lookup_type_id, value_code, label_ar, label_en, sort_order, is_active_fl) VALUES (…) [per value]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate · Null handling: values[] optional

QR-FIN-012 — search lookups
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-012 · Entity: ENT-FIN-003 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_lookup_type WHERE (lookup_key LIKE :key OR :key IS NULL) AND (name_ar LIKE :nameAr OR :nameAr IS NULL)
Join: NONE · Transaction: READ_ONLY · Pagination: YES · Filters: lookupKey/nameAr/nameEn LIKE · Result shape: full entity · Null handling: empty = success

QR-FIN-013 — read lookup (+ values)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-013 · Entity: ENT-FIN-003 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_lookup_type WHERE lookup_type_pk=:id; SELECT * FROM fin_lookup_value WHERE lookup_type_id=:id ORDER BY sort_order
Join: NONE · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-014 — update lookup
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-014 · Entity: ENT-FIN-003 · Operation: UPDATE
Logical spec : UPDATE fin_lookup_type SET name_ar, name_en WHERE lookup_type_pk=:id; replace fin_lookup_value rows per values[]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: n/a

QR-FIN-015 — deactivate lookup value
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-015 · Entity: ENT-FIN-003 · Operation: UPDATE
Logical spec : UPDATE fin_lookup_value SET is_active_fl=false WHERE lookup_value_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none · Null handling: not found → 404

QR-FIN-016 — find event rule by event type code (also used by auth-independent user lookup pattern reused for username, see API-FIN-047)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD, invoked from the event listener and from PHASE:CORE's inbound handler) · API: API-FIN-016 (existence check), API-FIN-047 (shaped identically for username) · Entity: ENT-FIN-004 (rule) / ENT-FIN-012 (user) · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_event_rule WHERE event_type_code=:code AND is_active_fl=true — [user variant] SELECT * FROM fin_user WHERE username=:username AND is_active_fl=true
Join: NONE · Transaction: READ_ONLY · Pagination: NO · Filters: code/username EXACT · Result shape: full entity · Null handling: not found → RULE-FIN-012 context / FIN-PLATFORM-401

QR-FIN-017 — search event rules
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-017 · Entity: ENT-FIN-004 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_event_rule WHERE (event_type_code=:code OR :code IS NULL) AND (is_active_fl=:isActiveFl OR :isActiveFl IS NULL)
Join: NONE · Transaction: READ_ONLY · Pagination: YES · Filters: eventTypeCode EXACT, isActiveFl EXACT · Result shape: full entity · Null handling: empty = success

QR-FIN-018 — read event rule (+ lines + mapping entries)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-018 · Entity: ENT-FIN-004 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_event_rule WHERE event_rule_pk=:id; SELECT * FROM fin_rule_line WHERE event_rule_id=:id ORDER BY line_no; SELECT * FROM fin_rule_line_mapping WHERE rule_line_id IN (…)
Join: NONE (owned collections, 3 queries) · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-019 — update event rule (replace lines)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-019 · Entity: ENT-FIN-004 · Operation: UPDATE
Logical spec : UPDATE fin_event_rule SET name_ar, name_en WHERE event_rule_pk=:id; DELETE FROM fin_rule_line WHERE event_rule_id=:id (cascades to fin_rule_line_mapping); re-INSERT lines + mapping entries per lines[]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: full replace, not a diff

QR-FIN-020 — deactivate event rule
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-020 · Entity: ENT-FIN-004 · Operation: UPDATE
Logical spec : UPDATE fin_event_rule SET is_active_fl=false WHERE event_rule_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none · Null handling: not found → 404

QR-FIN-021 — create recurring template (+ lines)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-021 · Entity: ENT-FIN-008 · Operation: SAVE
Logical spec : INSERT INTO fin_recurring_template (…, next_run_date=:computedFromScheduleRule); INSERT INTO fin_recurring_template_line (…) [per line]; INSERT INTO fin_recurring_template_line_dim (…) [per dimension value]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate · Null handling: n/a

QR-FIN-022 — search recurring templates (also used by the scheduler filtered on next_run_date)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-022 · Entity: ENT-FIN-008 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_recurring_template WHERE (template_name_ar LIKE :nameAr OR :nameAr IS NULL) AND (template_type_code=:type OR :type IS NULL) AND (is_active_fl=:isActiveFl OR :isActiveFl IS NULL) — [scheduler variant] AND next_run_date <= :now AND is_active_fl=true
Join: NONE · Transaction: READ_ONLY · Pagination: YES (user-facing) / NO (scheduler batch) · Filters: as listed · Result shape: full entity · Null handling: empty = success / no due templates

QR-FIN-023 — read recurring template (+ lines)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-023 · Entity: ENT-FIN-008 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_recurring_template WHERE recurring_template_pk=:id; SELECT * FROM fin_recurring_template_line WHERE recurring_template_id=:id ORDER BY line_no
Join: NONE · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-024 — update recurring template
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-024 · Entity: ENT-FIN-008 · Operation: UPDATE
Logical spec : UPDATE fin_recurring_template SET template_name_ar, template_name_en, schedule_rule WHERE recurring_template_pk=:id; replace lines per lines[]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: n/a

QR-FIN-025 — deactivate recurring template
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-025 · Entity: ENT-FIN-008 · Operation: UPDATE
Logical spec : UPDATE fin_recurring_template SET is_active_fl=false WHERE recurring_template_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none · Null handling: not found → 404

QR-FIN-026 — create allocation rule (+ lines)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-026 · Entity: ENT-FIN-009 · Operation: SAVE
Logical spec : INSERT INTO fin_allocation_rule (…); INSERT INTO fin_allocation_rule_dim (…) [per source dim value]; INSERT INTO fin_allocation_rule_line (…) [per line]; INSERT INTO fin_allocation_rule_line_dim (…) [per target dim value]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate · Null handling: n/a

QR-FIN-027 — search allocation rules
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-027 · Entity: ENT-FIN-009 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_allocation_rule WHERE (rule_name_ar LIKE :nameAr OR :nameAr IS NULL) AND (source_account_id=:accId OR :accId IS NULL) AND (is_active_fl=:isActiveFl OR :isActiveFl IS NULL)
Join: NONE · Transaction: READ_ONLY · Pagination: YES · Filters: as listed · Result shape: full entity · Null handling: empty = success

QR-FIN-028 — read allocation rule (+ lines)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-028 · Entity: ENT-FIN-009 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_allocation_rule WHERE allocation_rule_pk=:id; SELECT * FROM fin_allocation_rule_line WHERE allocation_rule_id=:id ORDER BY line_no
Join: NONE · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-029 — update allocation rule
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-029 · Entity: ENT-FIN-009 · Operation: UPDATE
Logical spec : UPDATE fin_allocation_rule SET rule_name_ar, rule_name_en, source_account_id WHERE allocation_rule_pk=:id; replace source dims + lines
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: n/a

QR-FIN-030 — deactivate allocation rule
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-030 · Entity: ENT-FIN-009 · Operation: UPDATE
Logical spec : UPDATE fin_allocation_rule SET is_active_fl=false WHERE allocation_rule_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none · Null handling: not found → 404

QR-FIN-031 — run allocation (generates a journal entry)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-031 · Entity: ENT-FIN-009, ENT-FIN-006 · Operation: SAVE
Logical spec : SELECT SUM(amount) FROM fin_journal_entry_line jel JOIN fin_journal_entry je ON je.journal_entry_pk=jel.journal_entry_id WHERE jel.account_id=:sourceAccountId AND je.status_code='POSTED' [+ dimension filter] — then INSERT INTO fin_journal_entry/fin_journal_entry_line per RULE-FIN-005 distribution order
Join: required (fin_journal_entry_line ↔ fin_journal_entry) — ADR-FIN-006 · Transaction: READ_WRITE · Pagination: NO · Filters: sourceAccountId EXACT, dimension EXACT · Result shape: computed aggregate → new entity · Null handling: zero balance → FIN-RULE-014

QR-FIN-032 — create manual journal entry (+ lines)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-032 · Entity: ENT-FIN-006, ENT-FIN-007 · Operation: SAVE
Logical spec : INSERT INTO fin_journal_entry (entry_no=:issuedByNumberingEngine, entry_date, source_type_code='MANUAL', status_code='DRAFT'→'POSTED', fiscal_year_id, period_id, created_by, created_at, updated_by, updated_at) VALUES (…); INSERT INTO fin_journal_entry_line (…) [per line]; INSERT INTO fin_journal_entry_line_dim (…) [per dimension value]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate · Null handling: validation failure → entry stays DRAFT, error returned (REQ-FIN-019)

QR-FIN-033 — search journal entries
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-033 · Entity: ENT-FIN-006 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT DISTINCT je.* FROM fin_journal_entry je [LEFT JOIN fin_journal_entry_line jel ON jel.journal_entry_id=je.journal_entry_pk WHEN :accountId IS NOT NULL] WHERE (je.entry_no LIKE :entryNo OR :entryNo IS NULL) AND (je.entry_date BETWEEN :from AND :to OR :from IS NULL) AND (je.source_type_code=:sourceType OR :sourceType IS NULL) AND (je.status_code=:status OR :status IS NULL) AND (je.period_id=:periodId OR :periodId IS NULL) AND (jel.account_id=:accountId OR :accountId IS NULL)
Join: required (fin_journal_entry_line, only when accountId filter present) — ADR-FIN-006 · Transaction: READ_ONLY · Pagination: YES · Filters: as listed · Result shape: full entity (headers only, lines fetched on read) · Null handling: empty = success

QR-FIN-034 — read journal entry (+ lines)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-034 · Entity: ENT-FIN-006 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_journal_entry WHERE journal_entry_pk=:id; SELECT * FROM fin_journal_entry_line WHERE journal_entry_id=:id ORDER BY line_no; SELECT * FROM fin_journal_entry_line_dim WHERE journal_entry_line_id IN (…)
Join: NONE (owned collections) · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-035 — reverse journal entry (creates a linked new entry)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-035 · Entity: ENT-FIN-006, ENT-FIN-007 · Operation: SAVE
Logical spec : (read original via QR-FIN-034) → INSERT INTO fin_journal_entry (…, source_type_code='VOID_CORRECTION', reversal_of_entry_id=:originalId, period_id=:currentOpenOrOriginal); INSERT INTO fin_journal_entry_line (direction flipped) […]; UPDATE fin_journal_entry SET reversed_by_entry_id=:newId WHERE journal_entry_pk=:originalId
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: new full aggregate · Null handling: original not found → 404

QR-FIN-036 — create fiscal year (+ periods)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-036 · Entity: ENT-FIN-010, ENT-FIN-011 · Operation: SAVE
Logical spec : INSERT INTO fin_fiscal_year (…, status_code='OPEN'); INSERT INTO fin_fiscal_period (…, status_code='OPEN') [per period]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate · Null handling: n/a

QR-FIN-037 — search fiscal years
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-037 · Entity: ENT-FIN-010 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_fiscal_year WHERE (year_code LIKE :code OR :code IS NULL) AND (status_code=:status OR :status IS NULL)
Join: NONE · Transaction: READ_ONLY · Pagination: YES · Filters: yearCode LIKE, statusCode EXACT · Result shape: full entity · Null handling: empty = success

QR-FIN-038 — read fiscal year (+ periods)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-038 · Entity: ENT-FIN-010 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_fiscal_year WHERE fiscal_year_pk=:id; SELECT * FROM fin_fiscal_period WHERE fiscal_year_id=:id ORDER BY sequence_no
Join: NONE (owned collection) · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-039 — approve period close
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-039 · Entity: ENT-FIN-011, ENT-FIN-006 · Operation: UPDATE
Logical spec : SELECT DISTINCT created_by FROM fin_journal_entry WHERE period_id=:periodId AND status_code='POSTED' [RULE-FIN-008 check against :principal] → UPDATE fin_fiscal_period SET status_code=:targetStatus, close_approved_by=:principal, close_approved_at=now() WHERE fiscal_period_pk=:periodId
Join: required (fin_journal_entry, for the SoD check) — ADR-FIN-006 · Transaction: READ_WRITE · Pagination: NO · Filters: periodId EXACT · Result shape: full entity · Null handling: principal found in creator set → FIN-RULE-008

QR-FIN-040 — year-end close
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-040 · Entity: ENT-FIN-010, ENT-FIN-006, ENT-FIN-001 · Operation: SAVE, UPDATE
Logical spec : SELECT COUNT(*) FROM fin_fiscal_period WHERE fiscal_year_id=:yearId AND status_code<>'HARD_CLOSE' [RULE-FIN-010, must be 0] → SELECT account_pk, SUM(signed amount) FROM fin_journal_entry_line jel JOIN fin_journal_entry je ON … WHERE je.status_code='POSTED' AND je.fiscal_year_id=:yearId GROUP BY account_pk, account_type → build + INSERT the opening entry (balance-sheet accounts) and the closing entry (revenue/expense net → Retained Earnings account, RULE-FIN-011) → UPDATE fin_fiscal_year SET status_code='YEAR_END_CLOSED' WHERE fiscal_year_pk=:yearId
Join: NONE beyond the standard header/line join already used by QR-FIN-033 pattern · Transaction: READ_WRITE · Pagination: NO · Filters: yearId EXACT · Result shape: full aggregate + generated entry · Null handling: any period not Hard Closed → FIN-RULE-010

QR-FIN-041 — create fiscal period
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-041 · Entity: ENT-FIN-011 · Operation: SAVE
Logical spec : INSERT INTO fin_fiscal_period (fiscal_year_id, period_code, name_ar, name_en, sequence_no, start_date, end_date, status_code='OPEN', is_active_fl, created_by, created_at, updated_by, updated_at) VALUES (…)
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full entity · Null handling: duplicate code → FIN-PLATFORM-409

QR-FIN-042 — account ledger
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-042 · Entity: ENT-FIN-007 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT je.entry_no, je.entry_date, jel.direction_code, jel.amount FROM fin_journal_entry_line jel JOIN fin_journal_entry je ON je.journal_entry_pk=jel.journal_entry_id WHERE jel.account_id=:accountId AND je.status_code='POSTED' [AND period/date range] [AND EXISTS dimension filter via fin_journal_entry_line_dim] ORDER BY je.entry_date
Join: required (fin_journal_entry_line ↔ fin_journal_entry) — ADR-FIN-006 · Transaction: READ_ONLY · Pagination: YES · Filters: accountId EXACT, dimensionValueIds SET, period/date RANGE · Result shape: projection (running balance computed in service) · Null handling: empty = success

QR-FIN-043 — trial balance
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-043 · Entity: ENT-FIN-001, ENT-FIN-007 · Operation: AGGREGATE
Logical spec : SELECT a.account_pk, a.code, a.name_ar, a.name_en, SUM(CASE WHEN jel.direction_code='DEBIT' THEN jel.amount ELSE 0 END) debit_total, SUM(CASE WHEN jel.direction_code='CREDIT' THEN jel.amount ELSE 0 END) credit_total FROM fin_account a JOIN fin_journal_entry_line jel ON jel.account_id=a.account_pk JOIN fin_journal_entry je ON je.journal_entry_pk=jel.journal_entry_id WHERE je.status_code='POSTED' [AND period/date range] GROUP BY a.account_pk, a.code, a.name_ar, a.name_en
Join: required (account ↔ line ↔ entry) — ADR-FIN-006 · Transaction: READ_ONLY · Pagination: NO · Filters: period/date RANGE, accountType EXACT · Result shape: projection · Null handling: no POSTED activity → account omitted, not an error

QR-FIN-044 — balance sheet
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-044 · Entity: ENT-FIN-001, ENT-FIN-007 · Operation: AGGREGATE
Logical spec : same shape as QR-FIN-043, filtered to account_type IN ('asset','liability','equity'), grouped additionally by account_type, entry_date <= :asOfDate
Join: required — ADR-FIN-006 · Transaction: READ_ONLY · Pagination: NO · Filters: asOfDate, fiscalYearId · Result shape: projection grouped by accountType · Null handling: n/a

QR-FIN-045 — income statement
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-045 · Entity: ENT-FIN-001, ENT-FIN-007 · Operation: AGGREGATE
Logical spec : same shape as QR-FIN-043, filtered to account_type IN ('revenue','expense'), period range :from/:to
Join: required — ADR-FIN-006 · Transaction: READ_ONLY · Pagination: NO · Filters: periodFrom, periodTo, fiscalYearId · Result shape: projection grouped by accountType · Null handling: n/a

QR-FIN-046 — dimension report
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-046 · Entity: ENT-FIN-002, ENT-FIN-007 · Operation: AGGREGATE
Logical spec : SELECT a.account_pk, dv.value_code, SUM(signed jel.amount) balance FROM fin_journal_entry_line_dim jeld JOIN fin_journal_entry_line jel ON jel.journal_entry_line_pk=jeld.journal_entry_line_id JOIN fin_journal_entry je ON je.journal_entry_pk=jel.journal_entry_id JOIN fin_account a ON a.account_pk=jel.account_id JOIN fin_dimension_value dv ON dv.dimension_value_pk=jeld.dimension_value_id WHERE dv.dimension_id=:dimensionId AND jeld.dimension_value_id=:dimensionValueId AND je.status_code='POSTED' [period range] GROUP BY a.account_pk, dv.value_code
Join: required (line-dim ↔ line ↔ entry ↔ account ↔ dimension value) — ADR-FIN-006 · Transaction: READ_ONLY · Pagination: NO · Filters: dimensionKey, dimensionValueId, period RANGE · Result shape: projection · Null handling: no activity for the value = empty, not an error

QR-FIN-047 — n/a (API-FIN-047 uses QR-FIN-016's user-shaped variant, see above)

QR-FIN-048 — create user
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-048 · Entity: ENT-FIN-012 · Operation: SAVE
Logical spec : INSERT INTO fin_user (username, name_ar, name_en, password_hash=:bcryptHash(password), is_active_fl=true, created_by, created_at, updated_by, updated_at) VALUES (…)
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full entity (excludes passwordHash) · Null handling: duplicate username → FIN-PLATFORM-409

QR-FIN-049 — search users
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-049 · Entity: ENT-FIN-012 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_user WHERE (username LIKE :username OR :username IS NULL) AND (name_ar LIKE :nameAr OR :nameAr IS NULL) AND (is_active_fl=:isActiveFl OR :isActiveFl IS NULL)
Join: NONE · Transaction: READ_ONLY · Pagination: YES · Filters: as listed · Result shape: projection (excludes passwordHash) · Null handling: empty = success

QR-FIN-050 — read user
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-050 · Entity: ENT-FIN-012 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_user WHERE user_pk=:id
Join: NONE · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full entity minus passwordHash · Null handling: not found → 404

QR-FIN-051 — update user
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-051 · Entity: ENT-FIN-012 · Operation: UPDATE
Logical spec : UPDATE fin_user SET name_ar=:nameAr, name_en=:nameEn, updated_by=:principal, updated_at=now() WHERE user_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full entity minus passwordHash · Null handling: username/password excluded (immutable via this endpoint)

QR-FIN-052 — deactivate user
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-052 · Entity: ENT-FIN-012 · Operation: UPDATE
Logical spec : UPDATE fin_user SET is_active_fl=false WHERE user_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none · Null handling: not found → 404

QR-FIN-053 — create role (+ permissions)
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-053 · Entity: ENT-FIN-013 · Operation: SAVE
Logical spec : INSERT INTO fin_role (role_code, role_name_ar, role_name_en, is_active_fl=true, created_by, created_at, updated_by, updated_at) VALUES (…); INSERT INTO fin_role_permission (role_id, page_code, action_code) [per permission]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate · Null handling: duplicate role_code → FIN-PLATFORM-409

QR-FIN-054 — search roles
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-054 · Entity: ENT-FIN-013 · Operation: FIND_BY_CRITERIA
Logical spec : SELECT * FROM fin_role WHERE (role_code LIKE :code OR :code IS NULL) AND (role_name_ar LIKE :nameAr OR :nameAr IS NULL) AND (is_active_fl=:isActiveFl OR :isActiveFl IS NULL)
Join: NONE · Transaction: READ_ONLY · Pagination: YES · Filters: as listed · Result shape: full entity · Null handling: empty = success

QR-FIN-055 — read role (+ permissions + assigned users)
Phase: PHASE:SVC-API (SUB:SVC-API-SEARCH) · API: API-FIN-055 · Entity: ENT-FIN-013 · Operation: FIND_ONE
Logical spec : SELECT * FROM fin_role WHERE role_pk=:id; SELECT * FROM fin_role_permission WHERE role_id=:id; SELECT u.* FROM fin_user u JOIN fin_user_role ur ON ur.user_id=u.user_pk WHERE ur.role_id=:id
Join: NONE (owned collections, 3 queries) · Transaction: READ_ONLY · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: not found → 404

QR-FIN-056 — update role
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-056 · Entity: ENT-FIN-013 · Operation: UPDATE
Logical spec : UPDATE fin_role SET role_name_ar, role_name_en WHERE role_pk=:id; replace fin_role_permission rows per permissions[]
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: full aggregate · Null handling: role_code excluded (immutable)

QR-FIN-057 — deactivate role
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-057 · Entity: ENT-FIN-013 · Operation: UPDATE
Logical spec : UPDATE fin_role SET is_active_fl=false WHERE role_pk=:id
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: id EXACT · Result shape: none · Null handling: not found → 404

QR-FIN-058 — assign users to role
Phase: PHASE:SVC-API (SUB:SVC-API-CRUD) · API: API-FIN-058 · Entity: ENT-FIN-013, ENT-FIN-012 · Operation: SAVE
Logical spec : INSERT INTO fin_user_role (user_id, role_id) VALUES (…) [per userId] ON CONFLICT (user_id, role_id) DO NOTHING (idempotent on UQ_FIN_USER_ROLE)
Join: NONE · Transaction: READ_WRITE · Pagination: NO · Filters: n/a · Result shape: full aggregate (role + assignedUsers[]) · Null handling: unknown userId → FIN-PLATFORM-404

## REGISTRY UPDATE

See `registry-exec-be-fin.md` for the structured registry ledger merged into
`project-registry.md` (CAT-5 structural registry, CAT-6 dependency index, CAT-8
pipeline status).
══════════════════════════════════════════════════════════════════

