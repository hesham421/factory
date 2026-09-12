# FRONTEND EXECUTION PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Track : frontend
Framework : react-ts-vite (profile.stack.frontend.framework) · routing react-router ·
            server-state tanstack-query · forms react-hook-form · validation zod ·
            state useState/useReducer + Context (no global store by default)
Inputs : srs (v1, PRD-approved), prd (v1), api-docs (v1, published by the backend repo),
         registry-srs (v1), registry-exec-be (v1)
Screens : 12 — SCR-FIN-001..012 · UXD : 12 — UXD-FIN-001..012 · API bound : 37 / 37
Open ADRs : 7 — erp/decisions/FIN/ (ADR-FIN-002..008, all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

## API SURFACE — FIN v1   (source: `_inputs/api-docs-fin.md` — the ONLY endpoint source)

```
ENDPOINTS   37 — API-FIN-001..037, bound to the published surface by the API ID BINDING
            annex of the api-docs (ADR-FIN-002), matched on verb + path with no shape diff.
            Envelope: every response is wrapped in ApiResponse<T> { success, data,
            error { code, message, fieldErrors[] }, timestamp }; every paged read returns
            Page<T> { totalPages, totalElements, first, last, numberOfElements, pageable,
            sort, size, number, empty }. Paging constraints (PageableBuilder): default page 0 ·
            default size 20 · maximum size 200.
            Ten reads are POST `…/search` with a `filters[] {field, operator, value}` body
            (operators EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL,
            LESS_THAN, LESS_THAN_OR_EQUAL, IN) plus sortField, sortDirection, page, size;
            the five report reads are GET with query params and are NOT paged. Per-endpoint
            request and response shapes are stated in each F2 block rather than duplicated here.
ERRORS      business codes, each already carrying its ar/en text in the module's catalog:
            FIN-400-INVALID-LOOKUP · FIN-400-INVALID-SORT · FIN-400-MISSING-FREQUENCY ·
            FIN-400-PERIOD-NOT-IN-YEAR · FIN-400-DOCDATE-OUTSIDE-PERIOD (400) ·
            FIN-403-FORBIDDEN (403) · FIN-404-ACCOUNT / -DIMENSION / -DIMVALUE / -RULE /
            -NO-ACTIVE-RULE / -TEMPLATE / -ALLOCATION-RULE / -ENTRY / -YEAR / -PERIOD (404) ·
            FIN-409-ACCOUNT-DUP / -DIMENSION-DUP / -DIMVALUE-DUP / -RULE-DUP / -YEAR-DUP (409,
            ALREADY_EXISTS) · FIN-409-HAS-CHILDREN · FIN-409-PARENT-NOT-LEAF-ELIGIBLE
            [RULE-FIN-001] · FIN-409-REMAINDER-COUNT [RULE-FIN-003] · FIN-409-DUPLICATE-EVENT
            [RULE-FIN-004] · FIN-409-UNBALANCED [RULE-FIN-006] · FIN-409-NOT-POSTABLE-ACCOUNT
            [RULE-FIN-007] · FIN-409-PERIOD-NOT-OPEN [RULE-FIN-008] · FIN-409-INVALID-DIMENSION
            [RULE-FIN-009] · FIN-409-NOT-POSTED [RULE-FIN-013] · FIN-409-ALREADY-REVERSED ·
            FIN-409-NOT-REOPENABLE [RULE-FIN-014] · FIN-409-INVALID-TRANSITION ·
            FIN-409-PERIODS-NOT-CLOSED · FIN-409-NOT-ACTIVE (409) ·
            FIN-422-MAPPING-UNSUPPORTED · FIN-422-REMAINDER-MARKER ·
            FIN-422-REMAINDER-NOT-POSITIVE [RULE-FIN-010] · FIN-422-INVALID-PERCENTAGE-VALUE
            (422) · framework codes VALIDATION_ERROR (400) and INTERNAL_ERROR (500).
            `FIN-403-SOD-VIOLATION` is struck in the module's own catalog as unreachable and
            is routed by nothing here.
            Routing is uniform across every F2 block: field validation → inline ·
            business rule → user message · unauthenticated → login · forbidden → the localized
            forbidden message · server → generic.
LOOKUPS     12 keys displayed on a FIN screen — ACCOUNT_TYPE, DEBIT_CREDIT, PERIOD_STATE,
            FISCAL_YEAR_STATUS, JOURNAL_TYPE, JOURNAL_STATUS, ACCOUNTING_EVENT_TYPE,
            ACCOUNT_DERIVATION_TYPE, AMOUNT_SOURCE_TYPE, DISTRIBUTION_TYPE,
            RECURRING_SCHEDULE_TYPE, RECURRING_FREQUENCY. FIN owns all thirteen keys and
            registers them into the lookup module (REQ-FIN-045), but **no FIN endpoint serves
            their values**: every value is runtime-loaded from the lookup module through the
            cross-module dependency each key mints — UXD-FIN-001..012, defined in
            `ui-ux-spec-fin.md` with the foreign endpoint named there (ADR-FIN-004). ONE hook
            per key, shared across every screen that shows it, long-lived cache. Every lookup
            field is a string holding the code; no enum and no union of literals is modelled
            anywhere below. PAYMENT_METHOD is registered but displayed by no FIN field in this
            version and mints nothing.
PERMISSIONS declared by the backend and read from the SRS Access summary and the backend
            registry, never redeclared here: PERM_FIN_ACCOUNTS_VIEW / _CREATE / _UPDATE ·
            PERM_FIN_DIMENSIONS_VIEW / _CREATE / _UPDATE · PERM_FIN_RULES_VIEW / _CREATE /
            _UPDATE · PERM_FIN_RECURRING_TEMPLATES_VIEW / _CREATE / _UPDATE ·
            PERM_FIN_ALLOCATION_RULES_VIEW / _CREATE / _UPDATE ·
            PERM_FIN_JOURNAL_ENTRIES_VIEW / _CREATE / _REVERSE · PERM_FIN_PERIODS_VIEW /
            _CREATE / _UPDATE / _CLOSE_APPROVE · PERM_FIN_ACCOUNT_LEDGER_VIEW ·
            PERM_FIN_TRIAL_BALANCE_VIEW · PERM_FIN_BALANCE_SHEET_VIEW ·
            PERM_FIN_INCOME_STATEMENT_VIEW · PERM_FIN_DIMENSION_REPORTS_VIEW.
            No FIN endpoint publishes the caller's own permission set: the screen gate is the
            security module's effective menu (ADR-FIN-005), and no `PERM_*` name is composed
            at runtime.
```

### Reconciliation against the SRS — run once, before any F-content

- **Every REQ that needs an endpoint has one.** REQ-FIN-001..043 map onto API-FIN-001..037
  with no gap; the mapping is the traces of the F2 blocks below. REQ-FIN-044 and REQ-FIN-045
  are onboarding acts with no screen in the SRS traceability matrix — the first is what makes
  the menu gate of SEC-FE resolve at all, the second is what makes the lookup hooks of F2
  return anything, and both are cited where they are depended on rather than given a screen
  they do not have. REQ-FIN-046 is covered by the drill-down links of SCR-FIN-008/009/010/011.
- **Every documented endpoint maps to a REQ.** All 37 are bound; none is unknown and none is
  used without a REQ behind it.
- **Naming and shape differences** — none. Every planned verb and path is the published verb
  and path (ADR-FIN-002's annex). What the registry lags by five ids is a registry gap, not a
  surface difference.
- **Operations the SRS names with no published endpoint** — template update, allocation-rule
  update, fiscal-year search, the by-id reads of account / template / allocation rule / year /
  period, the rule-line and target deletes, and the parent-dimension deactivate. None is
  required by a `REQ-*`, so none is breaking; each is omitted rather than faked (ADR-FIN-006).
- **Endpoints published but not called by this frontend** — API-FIN-020 alone, the
  event-sourced build a host system calls over the platform's in-process module interface
  (ADR-FIN-007). It is bound and blocked out in F2, and its entries are seen on SCR-FIN-006.
- **One screen's form differs from its SRS Part B input list** — SCR-FIN-006 takes
  `fiscalYearId` as an input (B3 lists neither it nor its absence; the request requires it and
  RULE-FIN-017 reads it) and holds `journalTypeCode` in the form model as the fixed value
  `MANUAL` (B3 marks it system-set; the request requires it). Both resolve against SRS A3 and
  RULE-FIN-017 rather than against B3's prose — ADR-FIN-008. The other eleven screens match
  their B3 list exactly.
- **Nothing is invented.** No value absent from the api-docs appears in this plan, and no
  lookup value, permission name, route or component is derived from anything but the SRS, the
  api-docs and the profile's own stack.

## EXECUTION PLAN INDEX — FIN v1 — frontend-execution-plan-fin.md

| # | Phase | Split | Blocks |
|---|---|---|---|
| 1 | F1 — Models & Types | per screen (12 SCR ≥ 5) | 12 SUB |
| 2 | F2 — Data Hooks | per screen | 12 SUB |
| 3 | F3 — Forms & Validators | per screen | 12 SUB |
| 4 | F4 — Screens & Routes | per screen | 12 SUB |
| 5 | SEC-FE | never split | level-1 only |
| 6 | ALIGN-FE | never split | level-1 only |

**SCREEN REGISTRY**

| SCR | Name (ar / en) | Page code | Container pattern | Owning ENT |
|---|---|---|---|---|
| SCR-FIN-001 | شجرة الحسابات / Chart of accounts | FIN_ACCOUNTS | TREE_MASTER_DETAIL | ENT-FIN-001 الحساب / Account |
| SCR-FIN-002 | تعريف الأبعاد وقيمها / Dimension definition & values | FIN_DIMENSIONS | TREE_MASTER_DETAIL | ENT-FIN-002 البُعد / Dimension (+ ENT-FIN-003 قيمة البُعد / DimensionValue) |
| SCR-FIN-003 | قواعد المحرك / Engine rules | FIN_RULES | FULL_PAGE | ENT-FIN-009 قاعدة نوع الحدث / EventTypeRule (+ ENT-FIN-010 سطر القاعدة / RuleLine) |
| SCR-FIN-004 | قوالب متكررة/عكسية / Recurring / reversing templates | FIN_RECURRING_TEMPLATES | FULL_PAGE | ENT-FIN-011 قالب متكرر/عكسي / RecurringTemplate (+ ENT-FIN-012 سطر القالب / TemplateLine) |
| SCR-FIN-005 | قواعد التوزيع / Allocation rules | FIN_ALLOCATION_RULES | FULL_PAGE | ENT-FIN-013 قاعدة توزيع / AllocationRule (+ ENT-FIN-014 هدف التوزيع / AllocationTarget) |
| SCR-FIN-006 | قيود اليومية / Journal entries | FIN_JOURNAL_ENTRIES | FULL_PAGE | ENT-FIN-004 رأس قيد اليومية / JournalEntry (+ ENT-FIN-005, ENT-FIN-006) |
| SCR-FIN-007 | الفترات والسنوات المالية / Fiscal periods & years | FIN_PERIODS | TREE_MASTER_DETAIL | ENT-FIN-007 السنة المالية / FiscalYear (+ ENT-FIN-008 الفترة المحاسبية / FiscalPeriod) |
| SCR-FIN-008 | دفتر الحساب / Account ledger | FIN_ACCOUNT_LEDGER | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-009 | ميزان المراجعة / Trial balance | FIN_TRIAL_BALANCE | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-010 | الميزانية العمومية / Balance sheet | FIN_BALANCE_SHEET | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-011 | قائمة الدخل / Income statement | FIN_INCOME_STATEMENT | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-012 | تقارير الأبعاد / Dimension reports | FIN_DIMENSION_REPORTS | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005, ENT-FIN-006 (live-derived) |

Twelve screens, so every `sub_bearing` phase splits per screen (threshold: SCR count ≥ 5), and
every SUB id is phase-qualified — `SUB:F1-SCR-FIN-006` and `SUB:F2-SCR-FIN-006` are distinct
blocks for the same screen under different phases.

<!-- PHASE:F1:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 1 — F1 — Models & Types

Per `ENT-*` (from the response DTOs of the api-docs) and per `SCR-*`: the source DTO with each
property's type and read-only / system-only / lookup status, then the screen's search model,
form model and container. Lookup fields are strings holding the code — all LOV values are
runtime-loaded from the lookup module (`profile.conventions.lookups`, ADR-FIN-004) — and no
enum is modelled anywhere below. Both names are carried per language (ar, en). No internal or
tenant identifier is modelled, and nothing is modelled that the api-docs do not return.

<!-- SUB:F1-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F1 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F1-MODEL — ENT-FIN-001 — الحساب / Account
Source DTO   : `AccountResponse` (read) · `AccountCreateRequest` · `AccountUpdateRequest` (write)
  accountPk            : number · read-only (PK) · system-only
  code                 : string · maxLength 30 · required on create, **read-only on edit**
                         (`AccountUpdateRequest` does not carry it — the chart code is immutable)
  nameAr               : string · required · maxLength 200
  nameEn               : string · required · maxLength 200
  accountTypeCode      : string · required on create · maxLength 20 · lookup — `ACCOUNT_TYPE`
                         code held as a string (UXD-FIN-001); **read-only on edit**, absent
                         from the update request
  natureCode           : string · required on create · maxLength 10 · lookup — `DEBIT_CREDIT`
                         code held as a string (UXD-FIN-002); **read-only on edit**
  parentAccountId      : number · optional on create (omitted for a root) · **read-only on edit**
  isLeafFl             : boolean · optional on create, required on update — the only field the
                         update request carries besides the two names
  isActiveFl           : boolean · read-only — flipped only by API-FIN-004
  isRetainedEarningsFl : boolean · read-only · system-only — the published DTO states it is
                         never settable through the account APIs
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-SCREEN — SCR-FIN-001
Search model : filters — code : string · LIKE · nameAr/nameEn : string · LIKE ·
               accountTypeCode : string · EXACT (the code, from the shared UXD-FIN-001 hook) ·
               isActiveFl : boolean · EXACT
               paging + sort — page, size, sortField, sortDirection, all inside the one
               `AccountSearchRequest` object per `Page<T>`
Form model   : create — code, nameAr, nameEn, accountTypeCode, natureCode (required),
                        parentAccountId, isLeafFl (optional)
               edit   — nameAr, nameEn, isLeafFl (required); every other field read-only
               excluded system fields: accountPk, isActiveFl, isRetainedEarningsFl, audit fields
Container    : TREE_MASTER_DETAIL
The tree is built on the client from `parentAccountId` over the rows the search returns; no
endpoint returns a nested tree and none is invented. Nothing is modelled that the api-docs do
not return, and no lookup is modelled as an enum — both code fields are plain strings.

<!-- SUB:F1-SCR-FIN-001:END -->

<!-- SUB:F1-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F1 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F1-MODEL — ENT-FIN-002 — البُعد / Dimension
Source DTO   : `DimensionResponse` (read) · `DimensionCreateRequest` (write)
  dimensionPk : number · read-only (PK) · system-only
  code        : string · required on create · maxLength 30
  nameAr      : string · required on create · maxLength 150
  nameEn      : string · required on create · maxLength 150
  isActiveFl  : boolean · read-only — and never written at all: no endpoint sets it on the
                parent dimension (SRS §B4, ADR-FIN-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-003 — قيمة البُعد / DimensionValue
Source DTO   : `DimensionValueResponse` (read) · `DimensionValueCreateRequest` (write)
  dimensionValuePk : number · read-only (PK) · system-only
  dimensionId      : number · read-only on the form — it is the path id of API-FIN-007, taken
                     from the selected parent, never typed
  code             : string · required on create · maxLength 30 — unique within the dimension
  nameAr           : string · required on create · maxLength 150
  nameEn           : string · required on create · maxLength 150
  sortOrder        : number · required on create
  isActiveFl       : boolean · read-only — flipped only by API-FIN-035
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-SCREEN — SCR-FIN-002
Search model : dimension filters — code : string · LIKE
               value filters — code : string · LIKE · dimensionId : number · EXACT (set from
               the selected parent, not typed)
               paging + sort inside each of `DimensionSearchRequest` and
               `DimensionValueSearchRequest`
Form model   : dimension — code, nameAr, nameEn (all required, create only)
               value — code, nameAr, nameEn, sortOrder (all required, create only)
               excluded system fields: both PKs, both isActiveFl, the audit fields
               read-only on edit: not applicable — neither resource has an update endpoint
Container    : TREE_MASTER_DETAIL
No enum is modelled: this screen defines the values other screens' dimension selects read, and
holds no lookup code of its own.

<!-- SUB:F1-SCR-FIN-002:END -->

<!-- SUB:F1-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F1 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F1-MODEL — ENT-FIN-009 — قاعدة نوع الحدث / EventTypeRule
Source DTO   : `EventTypeRuleResponse` (read) · `EventTypeRuleCreateRequest` (write)
  eventTypeRulePk : number · read-only (PK) · system-only
  eventTypeCode   : string · required on create · maxLength 50 · lookup —
                    `ACCOUNTING_EVENT_TYPE` code held as a string (UXD-FIN-007)
  nameAr, nameEn  : string · required on create · maxLength 150
  isActiveFl      : boolean · read-only — flipped only by API-FIN-034
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-010 — سطر القاعدة / RuleLine
Source DTO   : `RuleLineResponse` (read) · `RuleLineCreateRequest` (write)
  ruleLinePk                : number · read-only (PK) · system-only
  eventTypeRuleId           : number · read-only — the path id of API-FIN-011
  lineNo                    : number · read-only · system-assigned
  accountDerivationTypeCode : string · required · maxLength 20 · lookup —
                              `ACCOUNT_DERIVATION_TYPE` (UXD-FIN-008)
  accountDerivationValue    : string · required — read per the derivation type: a constant
                              account code, an event field name, or a mapping-set key
  amountSourceTypeCode      : string · required · maxLength 20 · lookup — `AMOUNT_SOURCE_TYPE`
                              (UXD-FIN-009)
  amountSourceValue         : string · optional in the DTO; required unless the amount source
                              type is REMAINDER (SRS ENT-FIN-010)
  directionCode             : string · required · maxLength 10 · lookup — `DEBIT_CREDIT`
                              (UXD-FIN-002)
  distributionTypeCode      : string · required · maxLength 15 · lookup — `DISTRIBUTION_TYPE`
                              (UXD-FIN-010)
  isRemainderFl             : boolean · optional in the DTO, governed by RULE-FIN-003
  createdAt                 : date-time · read-only · system-only
### F1-SCREEN — SCR-FIN-003
Search model : filters — eventTypeCode : string · EXACT (from the UXD-FIN-007 hook) ·
               isActiveFl : boolean · EXACT
               paging + sort inside `EventTypeRuleSearchRequest`
Form model   : rule — eventTypeCode, nameAr, nameEn (required, create only)
               line — accountDerivationTypeCode, accountDerivationValue, amountSourceTypeCode,
                      directionCode, distributionTypeCode (required); amountSourceValue
                      (required unless REMAINDER); isRemainderFl (boolean)
               excluded system fields: both PKs, eventTypeRuleId, lineNo, isActiveFl, createdAt
               read-only on edit: not applicable — neither the rule nor the line has an update
               endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The rule's lines are NOT part of the create request: `EventTypeRuleCreateRequest` carries the
header alone and each line is a separate API-FIN-011 call. The form model reflects that — a
rule is created first and its lines added to it — rather than promising a single submission
the surface does not accept. Five lookup fields, five strings, no enum.

<!-- SUB:F1-SCR-FIN-003:END -->

<!-- SUB:F1-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F1 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F1-MODEL — ENT-FIN-011 — قالب متكرر/عكسي / RecurringTemplate
Source DTO   : `RecurringTemplateResponse` (read) · `RecurringTemplateCreateRequest` (write)
  recurringTemplatePk : number · read-only (PK) · system-only
  nameAr, nameEn      : string · required on create · maxLength 150
  scheduleTypeCode    : string · required on create · maxLength 15 · lookup —
                        `RECURRING_SCHEDULE_TYPE` (UXD-FIN-011)
  frequencyCode       : string · optional in the DTO · maxLength 15 · lookup —
                        `RECURRING_FREQUENCY` (UXD-FIN-012); required when the schedule type
                        is RECURRING (SRS ENT-FIN-011), which the server answers with
                        `FIN-400-MISSING-FREQUENCY`
  startDate           : date · required on create
  nextRunDate         : date · read-only · system-maintained — it advances after each run
  endDate             : date · optional on create
  isActiveFl          : boolean · read-only — flipped only by API-FIN-036
  lineCount           : number · read-only · derived by the server from the lines it returns
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-012 — سطر القالب المتكرر / RecurringTemplateLine
Source DTO   : `RecurringTemplateLineResponse` (read) · `RecurringTemplateLineCreateRequest`
  recurringTemplateLinePk : number · read-only (PK) · system-only
  recurringTemplateId     : number · read-only · system-only
  lineNo                  : number · read-only · system-assigned
  accountId               : number · required
  amount                  : number · required — always positive; the direction carries the sign
  directionCode           : string · required · maxLength 10 · lookup — `DEBIT_CREDIT`
                            (UXD-FIN-002)
  dimensionValueId        : number · optional — ONE per line, the §9.3.3 simplification
  createdAt               : date-time · read-only · system-only
### F1-SCREEN — SCR-FIN-004
Search model : filters — nameAr/nameEn : string · LIKE · scheduleTypeCode : string · EXACT ·
               isActiveFl : boolean · EXACT
               paging + sort inside `RecurringTemplateSearchRequest`
Form model   : create — nameAr, nameEn, scheduleTypeCode, startDate, lines[] (required);
                        frequencyCode (required when RECURRING), endDate (optional)
               lines[] — accountId, amount, directionCode (required); dimensionValueId (optional)
               excluded system fields: every PK, recurringTemplateId, lineNo, nextRunDate,
               isActiveFl, lineCount, createdAt, audit fields
               read-only on edit: not applicable — no update endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The template and its lines are ONE submission — `RecurringTemplateCreateRequest` carries
`lines[]` — unlike SCR-FIN-003, whose lines are separate calls. `lineCount` is modelled as
read-only and never computed on the client, because the server derives it from the list it
returns.

<!-- SUB:F1-SCR-FIN-004:END -->

<!-- SUB:F1-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F1 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F1-MODEL — ENT-FIN-013 — قاعدة توزيع / AllocationRule
Source DTO   : `AllocationRuleResponse` (read) · `AllocationRuleCreateRequest` (write)
  allocationRulePk : number · read-only (PK) · system-only
  nameAr, nameEn   : string · required on create · maxLength 150
  sourceAccountId  : number · required on create — the balance being distributed
  isActiveFl       : boolean · read-only — flipped only by API-FIN-037
  targetCount      : number · read-only · derived by the server from the targets it returns
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-014 — هدف التوزيع / AllocationTarget
Source DTO   : `AllocationTargetResponse` (read) · `AllocationTargetCreateRequest` (write)
  allocationTargetPk   : number · read-only (PK) · system-only
  allocationRuleId     : number · read-only · system-only
  lineNo               : number · read-only · system-assigned
  targetAccountId      : number · required
  dimensionValueId     : number · optional — ONE per target
  distributionTypeCode : string · required · maxLength 15 · lookup — `DISTRIBUTION_TYPE`
                         (UXD-FIN-010)
  distributionValue    : number · optional in the DTO; required unless the distribution type
                         is REMAINDER (SRS ENT-FIN-014)
  isRemainderFl        : boolean · optional in the DTO, governed by RULE-FIN-003
### F1-SCREEN — SCR-FIN-005
Search model : filters — nameAr/nameEn : string · LIKE · sourceAccountId : number · EXACT ·
               isActiveFl : boolean · EXACT
               paging + sort inside `AllocationRuleSearchRequest`
Form model   : create — nameAr, nameEn, sourceAccountId, targets[] (required)
               targets[] — targetAccountId, distributionTypeCode (required); dimensionValueId,
                           distributionValue, isRemainderFl (optional per the DTO, constrained
                           by RULE-FIN-003 and by the distribution type)
               excluded system fields: every PK, allocationRuleId, lineNo, isActiveFl,
               targetCount, audit fields
               read-only on edit: not applicable — no update endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The rule and its targets are ONE submission. No model holds a computed allocation amount: the
distribution is produced by the server at run time from the source account's balance at that
moment, and the remainder target's amount is a difference RULE-FIN-010 computes, never a
percentage the client could anticipate.

<!-- SUB:F1-SCR-FIN-005:END -->

<!-- SUB:F1-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F1 · SCR-FIN-006 — قيود اليومية / Journal entries

### F1-MODEL — ENT-FIN-004 — رأس قيد اليومية / JournalEntry
Source DTO   : `JournalEntryResponse` (read) · `JournalEntryCreateRequest` (write)
  journalEntryPk  : number · read-only (PK) · system-only
  docNo           : string · read-only · system-only — generated on first save, immutable after
  docDate         : date · required on create
  fiscalYearId    : number · required on create — B3 lists it as neither an input nor a system
                    field; the published request requires it and RULE-FIN-017 reads it
                    (ADR-FIN-008)
  periodId        : number · required on create
  journalTypeCode : string · required on create · maxLength 20 · lookup — `JOURNAL_TYPE`
                    (UXD-FIN-005). On this form it is the fixed value `MANUAL`, held in the
                    model and rendered read-only (ADR-FIN-008)
  statusCode      : string · read-only · lookup — `JOURNAL_STATUS` (UXD-FIN-006); set by the
                    posting pipeline, never by a form
  eventReference  : string · read-only — present only on an event-sourced entry
  originalEntryId : number · read-only — set on a reversal
  reversalEntryId : number · read-only — set on the original once reversed
  descriptionAr, descriptionEn : string · optional on create
  postedAt        : date-time · read-only · system-only
  lineCount       : number · read-only · derived
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-005 — سطر قيد اليومية / JournalLine
Source DTO   : `JournalLineResponse` (read) · `JournalLineCreateRequest` (write)
  journalLinePk  : number · read-only (PK) · system-only
  journalEntryId : number · read-only · system-only
  lineNo         : number · read-only · system-assigned
  accountId      : number · required
  amount         : number · required — always positive
  directionCode  : string · required · maxLength 10 · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
  isRemainderFl  : boolean · read-only on this screen — the engine sets it on a built entry;
                   `JournalLineCreateRequest` does not carry it
  descriptionAr, descriptionEn : string · optional
  createdAt      : date-time · read-only · system-only
### F1-MODEL — ENT-FIN-006 — بُعد سطر القيد / JournalLineDimension
Source DTO   : `JournalLineDimensionResponse` (read) · `JournalLineDimensionCreateRequest`
  journalLineDimensionPk, journalLineId : number · read-only · system-only
  dimensionId      : number · required when a dimension is used
  dimensionValueId : number · required with it
### F1-SCREEN — SCR-FIN-006
Search model : filters — docNo : string · LIKE · docDate : DATE_RANGE · periodId : number ·
               EXACT · statusCode : string · EXACT · journalTypeCode : string · EXACT
               paging + sort inside `JournalEntrySearchRequest`; page and size are part of the
               same object and never independent state
Form model   : create — docDate, fiscalYearId, periodId, journalTypeCode (fixed `MANUAL`,
                        read-only), lines[] (required); descriptionAr, descriptionEn (optional)
               lines[] — accountId, amount, directionCode (required); descriptionAr,
                         descriptionEn, dimensions[] (optional)
               dimensions[] — dimensionId, dimensionValueId (both required together)
               excluded system fields: every PK, docNo, statusCode, eventReference,
               originalEntryId, reversalEntryId, postedAt, lineCount, isRemainderFl, audit fields
               read-only on edit: the whole entry — a POSTED entry is locked (RULE-FIN-016) and
               this screen has no edit mode at all
Container    : FULL_PAGE
No DRAFT is modelled as a stored state a user can return to: SRS §A7 makes DRAFT transient and
a failed build is never written. `isRemainderFl` is read on a built entry and never written by
this form.

<!-- SUB:F1-SCR-FIN-006:END -->

<!-- SUB:F1-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F1 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F1-MODEL — ENT-FIN-007 — السنة المالية / FiscalYear
Source DTO   : `FiscalYearResponse` (read) · `FiscalYearCreateRequest` (write)
  fiscalYearPk : number · read-only (PK) · system-only
  code         : string · required on create · maxLength 10
  startDate    : date · required on create
  endDate      : date · required on create
  periodCount  : number · required on create — an input to generation, returned on the response
  statusCode   : string · read-only · lookup — `FISCAL_YEAR_STATUS` (UXD-FIN-004)
  isActiveFl   : boolean · read-only
  periods      : FiscalPeriodResponse[] · read-only — the generated periods, returned with the
                 year by API-FIN-023
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-008 — الفترة المحاسبية / FiscalPeriod
Source DTO   : `FiscalPeriodResponse` (read) — no write DTO: a period is generated, never typed
  fiscalPeriodPk : number · read-only (PK) · system-only
  fiscalYearId   : number · read-only — also the field year ids are discovered from, since no
                   fiscal-year search is published (ADR-FIN-006)
  periodNo       : number · read-only · generated
  nameAr, nameEn : string · read-only · generated (month names for a twelve-period year,
                   "الفترة N" / "Period N" otherwise)
  startDate, endDate : date · read-only · generated
  statusCode     : string · read-only · lookup — `PERIOD_STATE` (UXD-FIN-003); changed only by
                   API-FIN-024, API-FIN-025, API-FIN-026
  closedBy       : string · read-only — the approving principal, set at hard-close
  closedAt       : date-time · read-only — set at hard-close
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — YearEndCloseResponse (the year-end close result)
  closingEntry : JournalEntryResponse · read-only — the closing entry, modelled by the
                 SCR-FIN-006 entry model above and rendered through the same components
  openingEntry : JournalEntryResponse · read-only — the next year's opening entry
### F1-SCREEN — SCR-FIN-007
Search model : filters — fiscalYearId : number · EXACT · statusCode : string · EXACT — both
               OPTIONAL; omitting the year is a legitimate "all periods" request
               paging + sort inside `FiscalPeriodSearchRequest`
Form model   : create year — code, startDate, endDate, periodCount (all required)
               period actions — no form: open, soft-close and hard-close are path-id calls
               with no body
               excluded system fields: every PK, both statusCode, isActiveFl, periodNo, the
               generated names and dates, closedBy, closedAt, audit fields
               read-only on edit: not applicable — neither resource has an update endpoint
Container    : TREE_MASTER_DETAIL
The year list is derived from the distinct `fiscalYearId` of the period rows plus the year
API-FIN-023 returns on creation; no year-list model is invented on top of an endpoint that
does not exist.

<!-- SUB:F1-SCR-FIN-007:END -->

<!-- SUB:F1-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F1 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F1-MODEL — AccountLedgerResponse — دفتر الحساب / Account ledger
Source DTO   : `AccountLedgerResponse` (read only — this screen writes nothing)
  accountId, accountCode        : number, string · read-only
  accountNameAr, accountNameEn  : string · read-only
  accountTypeCode               : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001)
  natureCode                    : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
  fromDate, toDate              : date · read-only — echoed from the request
  dimensionId, dimensionValueId : number · read-only — echoed from the request
  debitTotal, creditTotal       : number · read-only
  closingBalance                : number · read-only
  rows[]                        : AccountLedgerRowResponse —
    journalEntryId : number · read-only — the link target on SCR-FIN-006
    docNo          : string · read-only
    docDate        : date · read-only
    journalTypeCode: string · read-only · lookup — `JOURNAL_TYPE` (UXD-FIN-005)
    eventReference : string · read-only — the end of the REQ-FIN-046 chain
    journalLineId, lineNo : number · read-only
    amount         : number · read-only
    directionCode  : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    signedAmount   : number · read-only
    runningBalance : number · read-only — computed by the server, never accumulated on the client
    descriptionAr, descriptionEn : string · read-only
### F1-SCREEN — SCR-FIN-008
Search model : query params — accountId : number · required · fromDate, toDate : date ·
               DATE_RANGE · dimensionId, dimensionValueId : number · EXACT — all five on the
               query string of a GET, so the report's address IS its filter
Form model   : none — a read-only report (SRS B3 "not applicable")
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`runningBalance` is modelled as a server field and is never recomputed client-side: the plan's
own accumulation could disagree with the ledger, which is exactly the class of defect
POL-FIN-009 exists to remove. This report is not paged — the endpoint returns the rows of the
requested range, and no `Page<T>` envelope appears in its response.

<!-- SUB:F1-SCR-FIN-008:END -->

<!-- SUB:F1-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F1 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F1-MODEL — TrialBalanceResponse — ميزان المراجعة / Trial balance
Source DTO   : `TrialBalanceResponse` (read only)
  periodId            : number · read-only — echoed from the request
  accountTypeCode     : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001)
  totalDebitBalance   : number · read-only
  totalCreditBalance  : number · read-only
  balanced            : boolean · read-only — the property REQ-FIN-040 asserts
  rows[]              : AccountBalanceRowResponse —
    accountId, accountCode : number, string · read-only
    accountNameAr, accountNameEn : string · read-only
    accountTypeCode : string · read-only · lookup (UXD-FIN-001)
    natureCode      : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    debitTotal, creditTotal, debitBalance, creditBalance, signedBalance : number · read-only
### F1-SCREEN — SCR-FIN-009
Search model : query params — periodId : number · EXACT · optional · accountTypeCode : string ·
               EXACT · optional. Both live in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`balanced` is the server's assertion and is modelled as such; the screen renders it and never
derives it by comparing the two totals itself. `AccountBalanceRowResponse` is shared with
SCR-FIN-010 and SCR-FIN-011 and is modelled once.

<!-- SUB:F1-SCR-FIN-009:END -->

<!-- SUB:F1-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F1 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F1-MODEL — BalanceSheetResponse — الميزانية العمومية / Balance sheet
Source DTO   : `BalanceSheetResponse` (read only)
  fiscalYearId : number · read-only — echoed from the request
  asOfDate     : date · read-only — echoed from the request
  groups[]     : AccountBalanceGroupResponse —
    accountTypeCode : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001); the section
    groupTotal      : number · read-only
    rows[]          : AccountBalanceRowResponse — the same row model as SCR-FIN-009, including
                      natureCode · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
### F1-SCREEN — SCR-FIN-010
Search model : query params — fiscalYearId : number · EXACT · **required** ·
               asOfDate : date · optional cut-off. Both in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
The grouping is the server's: `groups[]` arrives already keyed by account type with its total,
and no client-side grouping or subtotal is modelled. The continuity REQ-FIN-041 asserts is a
property of the posted data, not of this model — the opening balances are ordinary posted
lines of the year-end close entries.

<!-- SUB:F1-SCR-FIN-010:END -->

<!-- SUB:F1-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F1 · SCR-FIN-011 — قائمة الدخل / Income statement

### F1-MODEL — IncomeStatementResponse — قائمة الدخل / Income statement
Source DTO   : `IncomeStatementResponse` (read only)
  fiscalYearId             : number · read-only — echoed from the request
  fromPeriodId, toPeriodId : number · read-only — echoed from the request
  fromDate, toDate         : date · read-only — derived by the server from those two periods
  netResult                : number · read-only
  groups[]                 : AccountBalanceGroupResponse — accountTypeCode (lookup,
                             UXD-FIN-001) · groupTotal · rows[] (AccountBalanceRowResponse,
                             natureCode lookup UXD-FIN-002)
### F1-SCREEN — SCR-FIN-011
Search model : query params — fiscalYearId : number · EXACT · **required** ·
               fromPeriodId, toPeriodId : number · EXACT · optional. All three in the route's
               search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`fromDate`/`toDate` are modelled as read-only server output, not as inputs: the request takes
period ids and the server translates them into the date bounds those periods span. A statement
of zeros for a freshly closed year is a correct result (REQ-FIN-042), and nothing in this model
treats it as an absence of data.

<!-- SUB:F1-SCR-FIN-011:END -->

<!-- SUB:F1-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F1 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F1-MODEL — DimensionReportResponse — تقرير الأبعاد / Dimension report
Source DTO   : `DimensionReportResponse` (read only)
  dimensionId, dimensionValueId, periodId : number · read-only — echoed from the request
  rows[] : DimensionReportRowResponse —
    accountId, accountCode : number, string · read-only
    accountNameAr, accountNameEn : string · read-only
    natureCode : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    dimensionId, dimensionValueId : number · read-only
    dimensionValueCode : string · read-only
    dimensionValueNameAr, dimensionValueNameEn : string · read-only
    debitTotal, creditTotal, signedBalance : number · read-only
### F1-SCREEN — SCR-FIN-012
Search model : query params — dimensionId : number · EXACT · **required** ·
               dimensionValueId : number · EXACT · optional · periodId : number · EXACT ·
               optional. All three in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
The row is keyed by account **and** dimension value together — that pair is the model's unit,
which is how REQ-FIN-043's "never by the base account alone" is expressed in the type rather
than only in the rendering. The dimension value's names come from the row itself, so this
screen needs no dimension-value lookup hook.

<!-- SUB:F1-SCR-FIN-012:END -->

<!-- PHASE:F1:END -->

<!-- PHASE:F2:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-045,AC-FIN-045,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 2 — F2 — Data Hooks

What each screen needs from the API — not hook code. Every read query's cache key carries
**every** filter that changes the response, page and size included; page and page size live
inside the filter object and are never independent state. Every mutation declares its
invalidation. Components use the facade only; the facade uses the declared queries only
(server-state library: `tanstack-query`).

Two invalidation families are shared across screens and are declared once here. `[reports, *]`
covers the five live-derived reports of SCR-FIN-008..012: every one is computed from posted
lines at request time [POL-FIN-009], so every endpoint that posts — API-FIN-019, API-FIN-021,
API-FIN-014, API-FIN-017 and API-FIN-027 — invalidates it. `[fiscal-periods, *]` is one key
shared by SCR-FIN-007's list, SCR-FIN-006's period select and the period filters of SCR-FIN-009
and SCR-FIN-011, so a period that closes is stale everywhere at once rather than on one screen.

Every `F2-LOOKUP` block below names a key whose values come from the lookup module through the
`UXD-*` of `ui-ux-spec-fin.md`; the hooks are shared by key, not duplicated per screen, and
REQ-FIN-045 is what registers those keys in the first place.

<!-- SUB:F2-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F2-QUERY — API-FIN-001            traces=API-FIN-001,REQ-FIN-001
POST `/api/v1/fin/accounts/search` · request `AccountSearchRequest` { filters[], sortField,
sortDirection, page, size } · response `Page<AccountResponse>` · kind **read query**
(a POST that mutates nothing)
Cache key    : `[accounts, filters]` where `filters` is the whole request object — code,
               nameAr/nameEn, accountTypeCode, isActiveFl, sortField, sortDirection **and
               page, size**. Page and page size live inside the filter object; they are never
               independent state.
Errors       : `FIN-400-INVALID-SORT` (400) → inline on the sort control ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message ·
               server error (500) → generic message
Loading      : LOCAL — the SRS states nothing about this call being slow, so no GLOBAL indicator
Cache policy : defaults
Invalidation : this key is refreshed by every mutation below
### F2-QUERY — API-FIN-002            traces=API-FIN-002,REQ-FIN-001,REQ-FIN-002
POST `/api/v1/fin/accounts` · request `AccountCreateRequest` { code, nameAr, nameEn,
accountTypeCode, natureCode, parentAccountId?, isLeafFl? } · response `AccountResponse` ·
kind **mutation**
Errors       : `FIN-409-ACCOUNT-DUP` (409) → inline on `code` ·
               `FIN-409-PARENT-NOT-LEAF-ELIGIBLE` (409) → user message for RULE-FIN-001,
               ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" ·
               en: "An account with sub-accounts cannot accept direct posting" ·
               `FIN-404-ACCOUNT` (404) → inline on `parentAccountId` ·
               `FIN-400-INVALID-LOOKUP` (400) → inline on the offending code field ·
               validation (400) → inline per `error.fieldErrors[].field` ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[accounts, *]`
### F2-QUERY — API-FIN-003            traces=API-FIN-003,REQ-FIN-002
PUT `/api/v1/fin/accounts/{id}` · request `AccountUpdateRequest` { nameAr, nameEn, isLeafFl } ·
response `AccountResponse` · kind **mutation**
Errors       : `FIN-409-HAS-CHILDREN` (409) → user message for RULE-FIN-001, the same ar/en
               pair as above, shown on the `isLeafFl` control ·
               `FIN-404-ACCOUNT` (404) → user message · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[accounts, *]`
### F2-QUERY — API-FIN-004            traces=API-FIN-004,REQ-FIN-003
PUT `/api/v1/fin/accounts/{id}/deactivate` · no request body · response `AccountResponse`
(isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-ACCOUNT` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[accounts, *]`
### F2-LOOKUP — ACCOUNT_TYPE
Key `ACCOUNT_TYPE` · one shared hook, resolved through UXD-FIN-001 · options shape
{ code, labelAr, labelEn } · long-lived cache (the values change only when the lookup module's
data does) · shared with SCR-FIN-009, SCR-FIN-010 and SCR-FIN-011, never duplicated per screen
### F2-LOOKUP — DEBIT_CREDIT
Key `DEBIT_CREDIT` · one shared hook, resolved through UXD-FIN-002 · options shape
{ code, labelAr, labelEn } · long-lived cache · shared with every screen that shows a direction
or a nature
### F2-SCREEN-INIT — SCR-FIN-001
Permission read : `FIN_ACCOUNTS` present in the caller's effective menu → VIEW (ADR-FIN-005).
                  CREATE and UPDATE are not readable from any published endpoint; their
                  affordances render and the server's 403 is the authority.
Lookups used    : ACCOUNT_TYPE (form + filter), DEBIT_CREDIT (form)
Entity by id    : none published — the form hydrates from the row the `[accounts, filters]`
                  query already holds (ADR-FIN-006), so opening an account performs no second
                  read and an invalidation re-reads through the same key
### F2-FACADE — SCR-FIN-001
Composes     : API-FIN-001 (list) · API-FIN-002, API-FIN-003, API-FIN-004 (mutations) · the
               ACCOUNT_TYPE and DEBIT_CREDIT hooks
State it owns: the tree derived from the query's rows (never a copy of them), the selected
               account id (from the route param), the filter object including page and size,
               and a derived loading flag over the calls in flight
Operations   : createAccount · updateAccount · deactivateAccount (confirmation first, naming
               that history is retained)
Components use the facade only; the facade uses the declared queries only.

<!-- SUB:F2-SCR-FIN-001:END -->

<!-- SUB:F2-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F2 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F2-QUERY — API-FIN-005            traces=API-FIN-005,REQ-FIN-004
POST `/api/v1/fin/dimensions/search` · request `DimensionSearchRequest` { filters[], sortField,
sortDirection, page, size } · response `Page<DimensionResponse>` · kind **read query**
Cache key    : `[dimensions, filters]` — code, sort **and page, size**, all inside the one object
Errors       : `FIN-400-INVALID-SORT` (400) → inline on the sort control ·
               `FIN-403-FORBIDDEN` (403) → forbidden message · server error → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-006
### F2-QUERY — API-FIN-006            traces=API-FIN-006,REQ-FIN-004
POST `/api/v1/fin/dimensions` · request `DimensionCreateRequest` { code, nameAr, nameEn } ·
response `DimensionResponse` · kind **mutation**
Errors       : `FIN-409-DIMENSION-DUP` (409) → inline on `code` · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[dimensions, *]`
### F2-QUERY — API-FIN-008            traces=API-FIN-008,REQ-FIN-005
POST `/api/v1/fin/dimensions/values/search` · request `DimensionValueSearchRequest`
{ filters[] including `dimensionId`, sortField, sortDirection, page, size } ·
response `Page<DimensionValueResponse>` · kind **read query**
Cache key    : `[dimension-values, filters]` — dimensionId, code, sort **and page, size**.
               The parent id is part of the key, so selecting another dimension is a different
               cache entry rather than a refetch of the same one.
Errors       : `FIN-404-DIMENSION` (404) → user message · `FIN-400-INVALID-SORT` (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-007 and API-FIN-035
### F2-QUERY — API-FIN-007            traces=API-FIN-007,REQ-FIN-005,REQ-FIN-006
POST `/api/v1/fin/dimensions/{id}/values` · request `DimensionValueCreateRequest`
{ code, nameAr, nameEn, sortOrder } · response `DimensionValueResponse` · kind **mutation**
Errors       : `FIN-409-DIMVALUE-DUP` (409) → user message for RULE-FIN-002, routed inline to
               `code`, ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" ·
               en: "This code is already used within this dimension" ·
               `FIN-404-DIMENSION` (404) → user message · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[dimension-values, *]`
### F2-QUERY — API-FIN-035            traces=API-FIN-035,REQ-FIN-005
PUT `/api/v1/fin/dimensions/values/{id}/deactivate` · no request body ·
response `DimensionValueResponse` (isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-DIMVALUE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[dimension-values, *]`
### F2-SCREEN-INIT — SCR-FIN-002
Permission read : `FIN_DIMENSIONS` present in the caller's effective menu → VIEW (ADR-FIN-005)
Lookups used    : none — this screen writes the data other screens' dimension selects read
Entity by id    : none published for either resource; both panes hydrate from their own search
                  caches (ADR-FIN-006)
### F2-FACADE — SCR-FIN-002
Composes     : API-FIN-005, API-FIN-008 (lists) · API-FIN-006, API-FIN-007, API-FIN-035
               (mutations)
State it owns: the dimension list and the selected dimension's value list, both derived from
               their queries' data; the selected dimension id (from the route param); two
               filter objects, each carrying its own page and size; a derived loading flag
Operations   : createDimension · createValue (under the selected dimension) ·
               deactivateValue (confirmation naming that the value will be refused on any
               later journal line — REQ-FIN-021)
There is no deactivateDimension operation: no endpoint exists for it (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-002:END -->

<!-- SUB:F2-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F2-QUERY — API-FIN-009            traces=API-FIN-009,REQ-FIN-007
POST `/api/v1/fin/event-rules/search` · request `EventTypeRuleSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<EventTypeRuleResponse>` ·
kind **read query**
Cache key    : `[event-rules, filters]` — eventTypeCode, isActiveFl, sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-010            traces=API-FIN-010,REQ-FIN-007
POST `/api/v1/fin/event-rules` · request `EventTypeRuleCreateRequest` { eventTypeCode, nameAr,
nameEn } · response `EventTypeRuleResponse` · kind **mutation**
Errors       : `FIN-409-RULE-DUP` (409) → inline on `eventTypeCode` (one rule per event type;
               note that a deactivated rule still holds its type — SRS §B4) ·
               `FIN-400-INVALID-LOOKUP` (400) → inline on `eventTypeCode` ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[event-rules, *]`
### F2-QUERY — API-FIN-011            traces=API-FIN-011,REQ-FIN-008,REQ-FIN-009
POST `/api/v1/fin/event-rules/{id}/lines` · request `RuleLineCreateRequest`
{ accountDerivationTypeCode, accountDerivationValue, amountSourceTypeCode, amountSourceValue?,
directionCode, distributionTypeCode, isRemainderFl? } · response `RuleLineResponse` ·
kind **mutation**
Errors       : `FIN-409-REMAINDER-COUNT` (409) → user message for RULE-FIN-003,
               ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" ·
               en: "Exactly one remainder line is required when any percentage distribution
               is present" ·
               `FIN-422-REMAINDER-MARKER` (422) → user message on the remainder marker ·
               `FIN-422-INVALID-PERCENTAGE-VALUE` (422) → inline on `amountSourceValue` ·
               `FIN-404-RULE` (404) → user message · `FIN-400-INVALID-LOOKUP` (400) → inline
               on the offending code field · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[event-rules, *]` — the rule's line set is part of what the list shows
### F2-QUERY — API-FIN-034            traces=API-FIN-034,REQ-FIN-007
PUT `/api/v1/fin/event-rules/{id}/deactivate` · no request body ·
response `EventTypeRuleResponse` (isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-RULE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[event-rules, *]`
### F2-LOOKUP — ACCOUNTING_EVENT_TYPE
Key `ACCOUNTING_EVENT_TYPE` · one shared hook, resolved through UXD-FIN-007 · options
{ code, labelAr, labelEn } · long-lived cache. The list is legitimately empty until a host
registers event types; an empty list disables the create affordance with an explanatory
empty-state and is never replaced by a free-text field.
### F2-LOOKUP — ACCOUNT_DERIVATION_TYPE · AMOUNT_SOURCE_TYPE · DISTRIBUTION_TYPE · DEBIT_CREDIT
Keys `ACCOUNT_DERIVATION_TYPE` (UXD-FIN-008) · `AMOUNT_SOURCE_TYPE` (UXD-FIN-009) ·
`DISTRIBUTION_TYPE` (UXD-FIN-010) · `DEBIT_CREDIT` (UXD-FIN-002) — one shared hook per key,
each `{ code, labelAr, labelEn }`, each long-lived, and each shared with the other screens that
use the same key rather than re-fetched here.
### F2-SCREEN-INIT — SCR-FIN-003
Permission read : `FIN_RULES` present in the caller's effective menu → VIEW (ADR-FIN-005)
Lookups used    : ACCOUNTING_EVENT_TYPE (header + filter), ACCOUNT_DERIVATION_TYPE,
                  AMOUNT_SOURCE_TYPE, DISTRIBUTION_TYPE, DEBIT_CREDIT (line grid)
Entity by id    : none published — the rule page hydrates from the `[event-rules, filters]`
                  cache (ADR-FIN-006)
### F2-FACADE — SCR-FIN-003
Composes     : API-FIN-009 (list) · API-FIN-010, API-FIN-011, API-FIN-034 (mutations) · the
               five lookup hooks above
State it owns: the rule list from the query's data, the selected rule id (route param), the
               filter object including page and size, the draft line being added, and a
               derived loading flag
Operations   : createRule · addRuleLine · deactivateRule (confirmation stating that the event
               type is not freed for a replacement rule — the limitation SRS §B4 records)
There is no updateRule and no deleteRuleLine operation: neither endpoint exists (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-003:END -->

<!-- SUB:F2-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F2-QUERY — API-FIN-012            traces=API-FIN-012,REQ-FIN-022
POST `/api/v1/fin/recurring-templates/search` · request `RecurringTemplateSearchRequest`
{ filters[], sortField, sortDirection, page, size } · response
`Page<RecurringTemplateResponse>` (each row carries its full `lines[]`) · kind **read query**
Cache key    : `[recurring-templates, filters]` — nameAr/nameEn, scheduleTypeCode, isActiveFl,
               sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-013            traces=API-FIN-013,REQ-FIN-022
POST `/api/v1/fin/recurring-templates` · request `RecurringTemplateCreateRequest` { nameAr,
nameEn, scheduleTypeCode, frequencyCode?, startDate, endDate?, lines[] { accountId, amount,
directionCode, dimensionValueId? } } · response `RecurringTemplateResponse` · kind **mutation**
Errors       : `FIN-400-MISSING-FREQUENCY` (400) → inline on `frequencyCode` when the schedule
               type is RECURRING · `FIN-404-ACCOUNT` (404) → inline on the offending line's
               account · `FIN-409-INVALID-DIMENSION` (409) → inline on the offending line's
               dimension value · `FIN-400-INVALID-LOOKUP` (400) → inline on the offending code ·
               validation (400) → inline per field · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[recurring-templates, *]`
### F2-QUERY — API-FIN-014            traces=API-FIN-014,REQ-FIN-023,REQ-FIN-024
POST `/api/v1/fin/recurring-templates/{id}/run` · no request body ·
response `JournalEntryResponse` (the posted entry) · kind **mutation**
Errors       : `FIN-409-NOT-ACTIVE` (409) → user message,
               ar: "هذا التعريف غير نشط ولا يمكن تشغيله" ·
               en: "This definition is deactivated and cannot be run" ·
               `FIN-404-TEMPLATE` (404) → user message ·
               the posting pipeline's refusals, each as its own user message —
               `FIN-409-UNBALANCED` (409) [RULE-FIN-006] ·
               `FIN-409-NOT-POSTABLE-ACCOUNT` (409) [RULE-FIN-007] ·
               `FIN-409-PERIOD-NOT-OPEN` (409) [RULE-FIN-008] ·
               `FIN-409-INVALID-DIMENSION` (409) [RULE-FIN-009] ·
               `FIN-404-PERIOD` / `FIN-404-YEAR` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[recurring-templates, *]` (the template's `nextRunDate` advanced) and
               `[journal-entries, *]` (a new entry exists) and `[reports, *]` (every live
               report over posted lines is now stale)
### F2-QUERY — API-FIN-036            traces=API-FIN-036,REQ-FIN-022
PUT `/api/v1/fin/recurring-templates/{id}/deactivate` · no request body ·
response `RecurringTemplateResponse` (isActiveFl=false, lines included) · kind **mutation**
Errors       : `FIN-404-TEMPLATE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[recurring-templates, *]`
### F2-LOOKUP — RECURRING_SCHEDULE_TYPE · RECURRING_FREQUENCY · DEBIT_CREDIT
Keys `RECURRING_SCHEDULE_TYPE` (UXD-FIN-011) · `RECURRING_FREQUENCY` (UXD-FIN-012) ·
`DEBIT_CREDIT` (UXD-FIN-002) — one shared hook per key, `{ code, labelAr, labelEn }`,
long-lived cache, the DEBIT_CREDIT hook shared with every other screen that shows a direction.
### F2-SCREEN-INIT — SCR-FIN-004
Permission read : `FIN_RECURRING_TEMPLATES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005)
Lookups used    : RECURRING_SCHEDULE_TYPE (header + filter), RECURRING_FREQUENCY (header),
                  DEBIT_CREDIT (line grid)
Entity by id    : none published — the search row already carries the full aggregate, lines
                  included, so the page hydrates from the `[recurring-templates, filters]`
                  cache (ADR-FIN-006)
### F2-FACADE — SCR-FIN-004
Composes     : API-FIN-012 (list) · API-FIN-013, API-FIN-014, API-FIN-036 (mutations) · the
               three lookup hooks above
State it owns: the template list from the query's data, the selected template id (route
               param), the filter object including page and size, the draft template and its
               draft lines, and a derived loading flag
Operations   : createTemplate (header and lines in one submission) · runTemplate (confirmation
               first; on success the returned entry is offered on SCR-FIN-006) ·
               deactivateTemplate (confirmation stating that the template will no longer run)
No updateTemplate operation exists: no endpoint is published (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-004:END -->

<!-- SUB:F2-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F2-QUERY — API-FIN-015            traces=API-FIN-015,REQ-FIN-025
POST `/api/v1/fin/allocation-rules/search` · request `AllocationRuleSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<AllocationRuleResponse>` (each row
carries its full `targets[]`) · kind **read query**
Cache key    : `[allocation-rules, filters]` — nameAr/nameEn, sourceAccountId, isActiveFl,
               sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-016            traces=API-FIN-016,REQ-FIN-025
POST `/api/v1/fin/allocation-rules` · request `AllocationRuleCreateRequest` { nameAr, nameEn,
sourceAccountId, targets[] { targetAccountId, dimensionValueId?, distributionTypeCode,
distributionValue?, isRemainderFl? } } · response `AllocationRuleResponse` · kind **mutation**
Errors       : `FIN-409-REMAINDER-COUNT` (409) → user message for RULE-FIN-003, the same ar/en
               pair the rule declares, shown on the target grid ·
               `FIN-422-REMAINDER-MARKER` (422) → user message on the remainder marker ·
               `FIN-422-INVALID-PERCENTAGE-VALUE` (422) → inline on the offending
               `distributionValue` · `FIN-404-ACCOUNT` (404) → inline on the offending account ·
               `FIN-409-INVALID-DIMENSION` (409) → inline on the offending dimension value ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`
### F2-QUERY — API-FIN-017            traces=API-FIN-017,REQ-FIN-026
POST `/api/v1/fin/allocation-rules/{id}/run` · no request body ·
response `JournalEntryResponse` (the posted distribution entry) · kind **mutation**
Errors       : `FIN-409-NOT-ACTIVE` (409) → user message, the same ar/en pair as the template
               run · `FIN-404-ALLOCATION-RULE` (404) → user message ·
               `FIN-409-REMAINDER-COUNT` (409) [RULE-FIN-003, re-checked at run time] ·
               `FIN-422-REMAINDER-NOT-POSITIVE` (422) → user message for RULE-FIN-010,
               ar: "سطر الباقي يُحسب كفرق، لا كنسبة" ·
               en: "The remainder line is computed as a difference, never as a percentage" ·
               the posting pipeline's refusals — `FIN-409-UNBALANCED`,
               `FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`,
               `FIN-409-INVALID-DIMENSION` (409) · `FIN-404-PERIOD` / `FIN-404-YEAR` (404) ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`, `[journal-entries, *]` and `[reports, *]`
### F2-QUERY — API-FIN-037            traces=API-FIN-037,REQ-FIN-025
PUT `/api/v1/fin/allocation-rules/{id}/deactivate` · no request body ·
response `AllocationRuleResponse` (isActiveFl=false, targets included) · kind **mutation**
Errors       : `FIN-404-ALLOCATION-RULE` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`
### F2-LOOKUP — DISTRIBUTION_TYPE
Key `DISTRIBUTION_TYPE` · the same shared hook SCR-FIN-003 uses, resolved through UXD-FIN-010 ·
options { code, labelAr, labelEn } · long-lived cache · one hook for the whole application
### F2-SCREEN-INIT — SCR-FIN-005
Permission read : `FIN_ALLOCATION_RULES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005)
Lookups used    : DISTRIBUTION_TYPE (target grid)
Entity by id    : none published — the search row carries the full aggregate, targets included
                  (ADR-FIN-006)
### F2-FACADE — SCR-FIN-005
Composes     : API-FIN-015 (list) · API-FIN-016, API-FIN-017, API-FIN-037 (mutations) · the
               DISTRIBUTION_TYPE hook
State it owns: the rule list from the query's data, the selected rule id (route param), the
               filter object including page and size, the draft rule and its draft targets,
               and a derived loading flag
Operations   : createRule (header and targets in one submission) · runRule (confirmation
               first; on success the returned entry is offered on SCR-FIN-006) ·
               deactivateRule (confirmation stating that the rule will no longer run)
No updateRule operation exists: no endpoint is published (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-005:END -->

<!-- SUB:F2-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-006 — قيود اليومية / Journal entries

### F2-QUERY — API-FIN-018            traces=API-FIN-018,REQ-FIN-027
POST `/api/v1/fin/journal-entries/search` · request `JournalEntrySearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<JournalEntryResponse>` ·
kind **read query**
Cache key    : `[journal-entries, filters]` — docNo, docDate range, periodId, statusCode,
               journalTypeCode, sort **and page, size**, all inside the one filter object
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-019 and API-FIN-021, and by the two run endpoints of
               SCR-FIN-004 and SCR-FIN-005 and the year-end close of SCR-FIN-007
### F2-QUERY — API-FIN-022            traces=API-FIN-022,REQ-FIN-016,REQ-FIN-027
GET `/api/v1/fin/journal-entries/{id}` · response `JournalEntryResponse` with its `lines[]`
and each line's `dimensions[]` · kind **read query**
Cache key    : `[journal-entry, id]`
Errors       : `FIN-404-ENTRY` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults — a POSTED entry is immutable (RULE-FIN-016), so a cached one cannot
               go stale except through its own reversal link, which API-FIN-021 invalidates
Invalidation : n/a (a read); invalidated by API-FIN-021 for the reversed original
This is the one by-id read in the module, and it exists because the search result is not where
REQ-FIN-016 and REQ-FIN-027 read an entry's lines from.
### F2-QUERY — API-FIN-019            traces=API-FIN-019,REQ-FIN-014,REQ-FIN-015,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021
POST `/api/v1/fin/journal-entries` · request `JournalEntryCreateRequest` { docDate,
fiscalYearId, periodId, journalTypeCode, descriptionAr?, descriptionEn?, lines[] { accountId,
amount, directionCode, descriptionAr?, descriptionEn?, dimensions[] { dimensionId,
dimensionValueId } } } · response `JournalEntryResponse` (POSTED) · kind **mutation**
Errors       : every automatic check REQ-FIN-015 asks to be shown, each routed to the line or
               field it names and all shown together rather than one at a time —
               `FIN-409-UNBALANCED` (409) [RULE-FIN-006],
               ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" ·
               en: "The entry is unbalanced — total debits do not equal total credits" ·
               `FIN-409-NOT-POSTABLE-ACCOUNT` (409) [RULE-FIN-007],
               ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" ·
               en: "The target account does not accept direct posting" — routed to the line ·
               `FIN-409-PERIOD-NOT-OPEN` (409) [RULE-FIN-008],
               ar: "الفترة المستهدفة غير مفتوحة" · en: "The target period is not open" ·
               `FIN-409-INVALID-DIMENSION` (409) [RULE-FIN-009],
               ar: "قيمة البُعد غير صالحة" · en: "The dimension value is invalid" ·
               `FIN-400-PERIOD-NOT-IN-YEAR` (400) and `FIN-400-DOCDATE-OUTSIDE-PERIOD` (400)
               [RULE-FIN-017] → inline on the period and the document date ·
               `FIN-404-ACCOUNT` / `FIN-404-PERIOD` / `FIN-404-YEAR` (404) → inline on the
               offending selection · validation (400) → inline per field ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL — the submit affordance is busy; the entry is not cleared
Invalidation : `[journal-entries, *]` and `[reports, *]`
### F2-QUERY — API-FIN-020            traces=API-FIN-020,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013
POST `/api/v1/fin/journal-entries/from-event` · request `EventEntryBuildRequest`
{ eventReference, eventTypeCode, docDate, baseAmount, amounts?, fields?, descriptionAr?,
descriptionEn? } · response `JournalEntryResponse` · kind **mutation**
**Bound, and called by no screen** (ADR-FIN-007): the caller is a host system over the
platform's in-process module interface, not a user with a form. It is stated here so the
published surface is completely accounted for.
Errors       : `FIN-404-NO-ACTIVE-RULE` (404) [RULE-FIN-005] · `FIN-409-DUPLICATE-EVENT` (409)
               [RULE-FIN-004] · `FIN-422-MAPPING-UNSUPPORTED` (422) · the same posting
               refusals as API-FIN-019 — all answered to the calling system, never rendered
               by a FIN screen
Invalidation : n/a — no client of this plan calls it
### F2-QUERY — API-FIN-021            traces=API-FIN-021,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030
POST `/api/v1/fin/journal-entries/{id}/reverse` · no request body ·
response `JournalEntryResponse` (the new reversal entry) · kind **mutation**
Errors       : `FIN-409-NOT-POSTED` (409) [RULE-FIN-013] → user message,
               ar: "لا يمكن عكس قيد غير مُرحَّل" · en: "A non-posted entry cannot be reversed" ·
               `FIN-409-ALREADY-REVERSED` (409) → user message (the entry already carries a
               reversal link) · `FIN-409-PERIOD-NOT-OPEN` (409) → user message, raised when no
               open period can receive the reversal [RULE-FIN-012] ·
               `FIN-404-ENTRY` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[journal-entries, *]`, `[journal-entry, id]` (the original now carries its
               `reversalEntryId`) and `[reports, *]`
### F2-LOOKUP — JOURNAL_TYPE · JOURNAL_STATUS · DEBIT_CREDIT
Keys `JOURNAL_TYPE` (UXD-FIN-005) · `JOURNAL_STATUS` (UXD-FIN-006) · `DEBIT_CREDIT`
(UXD-FIN-002) — one shared hook per key, `{ code, labelAr, labelEn }`, long-lived cache. The
first two serve the search filters and the read-only display; on the entry form the journal
type is the fixed value `MANUAL` and no select is rendered (ADR-FIN-008).
### F2-SCREEN-INIT — SCR-FIN-006
Permission read : `FIN_JOURNAL_ENTRIES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). CREATE and the custom reverse action are not readable; their
                  affordances render and the server's 403 is the authority.
Lookups used    : JOURNAL_TYPE (filter + display), JOURNAL_STATUS (filter + display),
                  DEBIT_CREDIT (line grid)
Entity by id    : API-FIN-022 — the entry page reads by id rather than from the list cache,
                  because the lines and their dimensions are what the page renders
Period + year   : the period and year selects of the entry form are served by the SCR-FIN-007
                  fiscal-period query (API-FIN-033) through its own shared hook, keyed the
                  same way; this screen declares the dependency and does not duplicate the call
### F2-FACADE — SCR-FIN-006
Composes     : API-FIN-018 (list) · API-FIN-022 (entry) · API-FIN-019, API-FIN-021
               (mutations) · the three lookup hooks and the fiscal-period hook
State it owns: the list derived from the query's data, the selected entry id (route param),
               the filter object including page and size, the draft entry with its draft lines
               and their dimensions, the live debit and credit totals derived from those draft
               lines, and a derived loading flag
Operations   : postManualEntry (the draft is submitted whole; every returned refusal is
               displayed at once — REQ-FIN-015 — and nothing is cleared) ·
               reverseEntry (confirmation naming the period the reversal will land in)
The live totals are derived state over the draft lines and are never sent: the balance
judgement is RULE-FIN-006's, evaluated by the server.

<!-- SUB:F2-SCR-FIN-006:END -->

<!-- SUB:F2-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F2-QUERY — API-FIN-033            traces=API-FIN-033,REQ-FIN-031
POST `/api/v1/fin/fiscal-periods/search` · request `FiscalPeriodSearchRequest` { filters[]
optionally carrying `fiscalYearId` and `statusCode`, sortField, sortDirection, page, size } ·
response `Page<FiscalPeriodResponse>` · kind **read query**
Cache key    : `[fiscal-periods, filters]` — fiscalYearId, statusCode, sort **and page, size**.
               Omitting the year is a legitimate "all periods" request and is its own key.
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026 and API-FIN-027
This query is also the shared source of the period select on SCR-FIN-006's entry form and of
the period filters on SCR-FIN-009 and SCR-FIN-011 — one hook, one key, no duplicate call.
### F2-QUERY — API-FIN-023            traces=API-FIN-023,REQ-FIN-031
POST `/api/v1/fin/fiscal-years` · request `FiscalYearCreateRequest` { code, startDate, endDate,
periodCount } · response `FiscalYearResponse` with its generated `periods[]` · kind **mutation**
Errors       : `FIN-409-YEAR-DUP` (409) → inline on `code` · validation (400) → inline per
               field · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[fiscal-periods, *]` — the new year's periods must appear in every period list
### F2-QUERY — API-FIN-024            traces=API-FIN-024,REQ-FIN-032,REQ-FIN-035
PATCH `/api/v1/fin/fiscal-periods/{id}/open` · no request body · response
`FiscalPeriodResponse` · kind **mutation**
Errors       : `FIN-409-NOT-REOPENABLE` (409) [RULE-FIN-014] → user message,
               ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" ·
               en: "The period is hard-closed and cannot be reopened" ·
               `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-025            traces=API-FIN-025,REQ-FIN-033
PATCH `/api/v1/fin/fiscal-periods/{id}/soft-close` · no request body · response
`FiscalPeriodResponse` · kind **mutation**
Errors       : `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-026            traces=API-FIN-026,REQ-FIN-034,REQ-FIN-037,REQ-FIN-038
PATCH `/api/v1/fin/fiscal-periods/{id}/hard-close` · no request body · response
`FiscalPeriodResponse` (with `closedBy` and `closedAt` set) · kind **mutation**
Errors       : `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message — this is the
               refusal a caller without `PERM_FIN_PERIODS_CLOSE_APPROVE` receives, and it is
               the visible half of RULE-FIN-015
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-027            traces=API-FIN-027,REQ-FIN-036
POST `/api/v1/fin/fiscal-years/{id}/year-end-close` · no request body ·
response `YearEndCloseResponse` { closingEntry, openingEntry } · kind **mutation**
Errors       : `FIN-409-PERIODS-NOT-CLOSED` (409) → user message (not every period of the year
               is hard-closed) · `FIN-404-YEAR` / `FIN-404-PERIOD` / `FIN-404-ACCOUNT` (404) →
               user message (the last covers a ledger with no account marked as retained
               earnings) · `FIN-409-UNBALANCED`, `FIN-409-NOT-POSTABLE-ACCOUNT`,
               `FIN-409-INVALID-DIMENSION` (409) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : GLOBAL — the only GLOBAL indicator in this plan. The call computes every
               balance-sheet balance of the year and posts two entries; the SRS describes it
               as the year's terminal act (REQ-FIN-036), and a screen-local spinner would
               leave the rest of the application looking usable while the ledger's year is
               being closed underneath it
Invalidation : `[fiscal-periods, *]`, `[journal-entries, *]` and `[reports, *]`
### F2-LOOKUP — PERIOD_STATE · FISCAL_YEAR_STATUS
Keys `PERIOD_STATE` (UXD-FIN-003) · `FISCAL_YEAR_STATUS` (UXD-FIN-004) — one shared hook per
key, `{ code, labelAr, labelEn }`, long-lived cache. The labels come from the lookup; which
transitions a row offers comes from SRS §A7, not from the lookup's value list.
### F2-SCREEN-INIT — SCR-FIN-007
Permission read : `FIN_PERIODS` present in the caller's effective menu → VIEW (ADR-FIN-005).
                  `PERM_FIN_PERIODS_CLOSE_APPROVE` is not readable from any published
                  endpoint, so the hard-close and year-end-close affordances render and the
                  server's 403 is the authority (ADR-FIN-005).
Lookups used    : PERIOD_STATE (row status + filter), FISCAL_YEAR_STATUS (year header)
Entity by id    : none published for either resource — the period rows come from API-FIN-033
                  and the year from the API-FIN-023 response and from the rows' `fiscalYearId`
                  (ADR-FIN-006)
### F2-FACADE — SCR-FIN-007
Composes     : API-FIN-033 (period list) · API-FIN-023, API-FIN-024, API-FIN-025,
               API-FIN-026, API-FIN-027 (mutations) · the two lookup hooks
State it owns: the period list from the query's data, the year list derived from those rows'
               `fiscalYearId`, the selected year id (route param), the filter object including
               page and size, the create-year draft, and a derived loading flag
Operations   : createYear · openPeriod · softClosePeriod · hardClosePeriod (confirmation using
               the word permanent — RULE-FIN-014) · runYearEndClose (confirmation; on success
               the two returned entries are offered on SCR-FIN-006)

<!-- SUB:F2-SCR-FIN-007:END -->

<!-- SUB:F2-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F2-QUERY — API-FIN-028            traces=API-FIN-028,REQ-FIN-039,REQ-FIN-046
GET `/api/v1/fin/reports/account-ledger` · query params `accountId` (required), `fromDate`,
`toDate`, `dimensionId`, `dimensionValueId` · response `AccountLedgerResponse` with its
`rows[]` · kind **read query**
Cache key    : `[reports, account-ledger, filters]` where `filters` carries all five params.
               Every parameter that changes the response is in the key; this report is not
               paged, so no page or size belongs in it.
Errors       : `FIN-404-ACCOUNT` (404) → user message (the keying id did not resolve) ·
               validation (400) → inline on the offending parameter ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message
Loading      : LOCAL
Cache policy : defaults, and the key is in the `[reports, *]` family every posting mutation
               invalidates — a ledger computed live from posted lines is stale the moment
               anything posts [POL-FIN-009]
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT · JOURNAL_TYPE
Keys `ACCOUNT_TYPE` (UXD-FIN-001) · `DEBIT_CREDIT` (UXD-FIN-002) · `JOURNAL_TYPE`
(UXD-FIN-005) — the same shared hooks the entry screens use; this screen adds no hook of its own.
### F2-SCREEN-INIT — SCR-FIN-008
Permission read : `FIN_ACCOUNT_LEDGER` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). This screen has no other action.
Lookups used    : ACCOUNT_TYPE, DEBIT_CREDIT, JOURNAL_TYPE (all display-only)
Entity by id    : none — the report's own response carries the account's identity
Account select  : served by the SCR-FIN-001 account search (API-FIN-001) through its shared
                  key; this screen declares the dependency and duplicates no call
### F2-FACADE — SCR-FIN-008
Composes     : API-FIN-028 · the account search for its account picker · the three lookup hooks
State it owns: the filter object (account, date range, dimension, dimension value) mirrored
               from the route's search params, and a derived loading flag. No running balance
               and no total is owned here: all three come from the response
Operations   : none — this screen writes nothing. Navigation to SCR-FIN-006 for a row's entry
               is a route change, not an operation

<!-- SUB:F2-SCR-FIN-008:END -->

<!-- SUB:F2-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F2-QUERY — API-FIN-029            traces=API-FIN-029,REQ-FIN-040,REQ-FIN-046
GET `/api/v1/fin/reports/trial-balance` · query params `periodId` (optional),
`accountTypeCode` (optional) · response `TrialBalanceResponse` with its `rows[]` ·
kind **read query**
Cache key    : `[reports, trial-balance, filters]` — both params, and the unfiltered request is
               its own key rather than a variant of a filtered one
Errors       : `FIN-404-PERIOD` (404) → user message, raised only when `periodId` is supplied
               and does not resolve; omitting it stays a valid whole-ledger request ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
Keys `ACCOUNT_TYPE` (UXD-FIN-001, also the filter's option list) · `DEBIT_CREDIT`
(UXD-FIN-002) — the same shared hooks; no new hook here.
### F2-SCREEN-INIT — SCR-FIN-009
Permission read : `FIN_TRIAL_BALANCE` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (filter + display), DEBIT_CREDIT (display)
Entity by id    : none
Period select   : served by the shared fiscal-period query (API-FIN-033) of SCR-FIN-007
### F2-FACADE — SCR-FIN-009
Composes     : API-FIN-029 · the fiscal-period hook for its period select · the two lookup hooks
State it owns: the filter object (period, account type) mirrored from the route's search
               params, and a derived loading flag. `balanced` and both totals are read from the
               response and never derived here
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-009:END -->

<!-- SUB:F2-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F2-QUERY — API-FIN-030            traces=API-FIN-030,REQ-FIN-041,REQ-FIN-046
GET `/api/v1/fin/reports/balance-sheet` · query params `fiscalYearId` (**required**),
`asOfDate` (optional) · response `BalanceSheetResponse` with its `groups[]` ·
kind **read query**
Cache key    : `[reports, balance-sheet, filters]` — both params
Enabled      : only once a fiscal year is chosen — the query does not run with an absent
               required parameter, and the screen shows its choose-a-year state instead of a
               failed request
Errors       : `FIN-404-YEAR` (404) → user message (the required keying id did not resolve) ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
The same two shared hooks (UXD-FIN-001, UXD-FIN-002); the account type labels the section
headings the response groups by.
### F2-SCREEN-INIT — SCR-FIN-010
Permission read : `FIN_BALANCE_SHEET` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (section headings), DEBIT_CREDIT (row nature)
Entity by id    : none
Year select     : derived from the `fiscalYearId` of the shared fiscal-period query's rows
                  (API-FIN-033), since no fiscal-year search is published (ADR-FIN-006)
### F2-FACADE — SCR-FIN-010
Composes     : API-FIN-030 · the fiscal-period hook for its year select · the two lookup hooks
State it owns: the filter object (fiscal year, as-of date) mirrored from the route's search
               params, and a derived loading flag. No group total and no section is composed
               here — both arrive in the response
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-010:END -->

<!-- SUB:F2-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-011 — قائمة الدخل / Income statement

### F2-QUERY — API-FIN-031            traces=API-FIN-031,REQ-FIN-042,REQ-FIN-046
GET `/api/v1/fin/reports/income-statement` · query params `fiscalYearId` (**required**),
`fromPeriodId` (optional), `toPeriodId` (optional) · response `IncomeStatementResponse` with
its `groups[]` · kind **read query**
Cache key    : `[reports, income-statement, filters]` — all three params
Enabled      : only once a fiscal year is chosen, as on SCR-FIN-010
Errors       : `FIN-404-YEAR` (404) → user message (the required keying id) ·
               `FIN-404-PERIOD` (404) → user message, raised only when a period id is supplied
               and does not resolve · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
The same two shared hooks (UXD-FIN-001, UXD-FIN-002).
### F2-SCREEN-INIT — SCR-FIN-011
Permission read : `FIN_INCOME_STATEMENT` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (section headings), DEBIT_CREDIT (row nature)
Entity by id    : none
Year + periods  : both selects served by the shared fiscal-period query (API-FIN-033); the
                  period selects are narrowed to the chosen year by the same filter object
### F2-FACADE — SCR-FIN-011
Composes     : API-FIN-031 · the fiscal-period hook · the two lookup hooks
State it owns: the filter object (fiscal year, from period, to period) mirrored from the
               route's search params, and a derived loading flag. `fromDate`, `toDate` and
               `netResult` are read from the response, never computed here
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-011:END -->

<!-- SUB:F2-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F2-QUERY — API-FIN-032            traces=API-FIN-032,REQ-FIN-043
GET `/api/v1/fin/reports/dimension` · query params `dimensionId` (**required**),
`dimensionValueId` (optional), `periodId` (optional) · response `DimensionReportResponse`
with its `rows[]` · kind **read query**
Cache key    : `[reports, dimension, filters]` — all three params
Enabled      : only once a dimension is chosen — the required parameter gates the call, and
               the screen shows its choose-a-dimension state until then
Errors       : `FIN-404-DIMENSION` (404) → user message (the required keying id) ·
               `FIN-404-PERIOD` (404) → user message when a supplied period does not resolve ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — DEBIT_CREDIT
Key `DEBIT_CREDIT` (UXD-FIN-002) — the shared hook, for the row's nature. The dimension and
dimension-value selects are NOT lookups: they read FIN's own API-FIN-005 and API-FIN-008
through the SCR-FIN-002 keys, and the row's dimension-value names come from the report itself.
### F2-SCREEN-INIT — SCR-FIN-012
Permission read : `FIN_DIMENSION_REPORTS` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : DEBIT_CREDIT (row nature)
Entity by id    : none
Dimension select: served by the SCR-FIN-002 dimension and dimension-value searches through
                  their shared keys; no call is duplicated here
### F2-FACADE — SCR-FIN-012
Composes     : API-FIN-032 · the dimension and dimension-value searches for its selects · the
               DEBIT_CREDIT hook
State it owns: the filter object (dimension, dimension value, period) mirrored from the
               route's search params, and a derived loading flag. No aggregation is performed
               here — the account × dimension-value rows arrive as they are
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-012:END -->

<!-- PHASE:F2:END -->

<!-- PHASE:F3:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 3 — F3 — Forms & Validators

One block per `RULE-*` enforced on a form, plus the field constraints the published DTOs state.
No frontend-only validation the SRS does not state; every message is read from its catalog
code, never hard-coded; the locale resolves session → browser → `ar`; and a caller without the
write permission is answered by the server rather than by a pre-emptively disabled field
(ADR-FIN-005). Schemas are written with `zod` + `react-hook-form`.

Five of the twelve screens carry no form at all: SCR-FIN-008..012 are read-only reports whose
SRS §B3 reads "not applicable". Their blocks state the filter validation and say plainly that
no `RULE-*` is enforced, rather than inventing one to fill the section.

<!-- SUB:F3-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F3 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

Validation timing for this form: **on blur for the unique code, on submit for the rest**
(declared once for the whole form).
### F3-FIELD — SCR-FIN-001 (create)
code            · REQUIRED · LENGTH (maxLength 30, from `AccountCreateRequest`) ·
                  UNIQUE_CHECK · when blur
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 200) · when submit
accountTypeCode · REQUIRED · LOOKUP_VALID (`ACCOUNT_TYPE`, UXD-FIN-001) · LENGTH (20) · when submit
natureCode      · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
parentAccountId · optional · when submit
isLeafFl        · optional · BUSINESS_RULE (RULE-FIN-001) · when submit
### F3-FIELD — SCR-FIN-001 (edit)
code, accountTypeCode, natureCode, parentAccountId · read-only — not inputs at all;
                  `AccountUpdateRequest` does not carry them
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 200) · when submit
isLeafFl        · REQUIRED · BUSINESS_RULE (RULE-FIN-001) · when submit
UNIQUE_CHECK    : async, on blur, via `API-FIN-001` with an EQUALS filter on `code`; on edit
                  the field is read-only so the check does not run at all. A failure never
                  blocks submit on its own — the authority is the server's
                  `FIN-409-ACCOUNT-DUP`, routed inline to the same field.
LOOKUP_VALID    : the value must be one the runtime-loaded option list contains; no static
                  list is written anywhere, and an empty option list leaves the field
                  unsatisfiable rather than falling back to a hardcoded set (ADR-FIN-004).
### F3-VALIDATION — RULE-FIN-001      traces=REQ-FIN-002,AC-FIN-002
Statement : The system shall prevent an account with any child account from being marked as
            accepting direct posting.
Message   : from the catalog codes `FIN-409-PARENT-NOT-LEAF-ELIGIBLE` (on create) and
            `FIN-409-HAS-CHILDREN` (on update) —
            ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" ·
            en: "An account with sub-accounts cannot accept direct posting"
Scope     : CREATE and UPDATE
Field     : isLeafFl · kind BUSINESS_RULE · when submit
Validation shape : the client knows, from the tree it already renders, whether the selected
            node has children, and uses that to explain the constraint beside the control
            before submit. It does **not** decide the outcome: the tree is a page of search
            results and may not hold every child, so the submission goes through and the
            catalog message is what the user is shown on refusal. The message is read from the
            catalog, never composed here.
Business-code fields: `code` is the chart-of-accounts code and is displayed read-only after
create; it is never regenerated or re-derived on the client.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `FIN-403-FORBIDDEN` on submit
and the form shows the localized forbidden message; fields are not pre-emptively disabled,
because the permission is not readable (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-001:END -->

<!-- SUB:F3-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F3 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

Validation timing for this form: **on blur for the unique codes, on submit for the rest**.
### F3-FIELD — SCR-FIN-002 (dimension, create)
code           · REQUIRED · LENGTH (maxLength 30) · UNIQUE_CHECK · when blur
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-FIN-002 (dimension value, create)
code           · REQUIRED · LENGTH (maxLength 30) · UNIQUE_CHECK (within the selected
                 dimension — RULE-FIN-002) · when blur
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder      · REQUIRED · when submit
UNIQUE_CHECK   : async, on blur — the dimension via `API-FIN-005` with an EQUALS filter on
                 `code`; the value via `API-FIN-008` with EQUALS filters on both `dimensionId`
                 and `code`, so the scope of the check is the same scope the rule has. Neither
                 blocks submit on its own: the server's `FIN-409-DIMENSION-DUP` and
                 `FIN-409-DIMVALUE-DUP` are the authority, routed inline to `code`.
### F3-VALIDATION — RULE-FIN-002      traces=REQ-FIN-006,AC-FIN-006
Statement : The system shall reject a dimension value whose code already exists under the same
            dimension.
Message   : from the catalog code `FIN-409-DIMVALUE-DUP` —
            ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" ·
            en: "This code is already used within this dimension"
Scope     : CREATE
Field     : code (of the value) · kind UNIQUE_CHECK · when blur, and again on submit by the server
Validation shape : uniqueness is scoped to the parent dimension, never globally — a code used
            under one dimension is legitimate under another, and a global check would reject a
            value the server accepts. Written with `zod` + `react-hook-form`, with the async
            check bound to the selected parent id.
Business-code fields: none of these codes is platform-numbered; both are client-defined and
are read-only after create because neither resource has an update endpoint.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit and the form shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-002:END -->

<!-- SUB:F3-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F3 · SCR-FIN-003 — قواعد المحرك / Engine rules

Validation timing for this form: **on submit** for the rule header and for each line
(declared once for the whole page). The remainder marker is judged across the line set, so it
has nothing to validate until a line is submitted.
### F3-FIELD — SCR-FIN-003 (rule header, create)
eventTypeCode  · REQUIRED · LOOKUP_VALID (`ACCOUNTING_EVENT_TYPE`, UXD-FIN-007) ·
                 LENGTH (maxLength 50) · UNIQUE_CHECK · when submit
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-FIN-003 (rule line)
accountDerivationTypeCode · REQUIRED · LOOKUP_VALID (`ACCOUNT_DERIVATION_TYPE`, UXD-FIN-008) ·
                            LENGTH (20) · when submit
accountDerivationValue    · REQUIRED · when submit
amountSourceTypeCode      · REQUIRED · LOOKUP_VALID (`AMOUNT_SOURCE_TYPE`, UXD-FIN-009) ·
                            LENGTH (20) · when submit
amountSourceValue         · BUSINESS_RULE (required unless the amount source type is
                            REMAINDER — SRS ENT-FIN-010) · when submit
directionCode             · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) ·
                            LENGTH (10) · when submit
distributionTypeCode      · REQUIRED · LOOKUP_VALID (`DISTRIBUTION_TYPE`, UXD-FIN-010) ·
                            LENGTH (15) · when submit
isRemainderFl             · BUSINESS_RULE (RULE-FIN-003) · when submit
UNIQUE_CHECK : async on `eventTypeCode` via `API-FIN-009` with an EQUALS filter. The check is
               **not** narrowed to active rules, because the server's own uniqueness guard is
               not either — a deactivated rule still holds its event type (SRS §B4). The
               authority remains `FIN-409-RULE-DUP`.
### F3-VALIDATION — RULE-FIN-003      traces=REQ-FIN-009,AC-FIN-009
Statement : The system shall require exactly one line marked as the remainder whenever the set
            forms a compound or percentage distribution.
Message   : from the catalog code `FIN-409-REMAINDER-COUNT` —
            ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" ·
            en: "Exactly one remainder line is required when any percentage distribution is
            present"
Scope     : CREATE and UPDATE of the line set
Field     : isRemainderFl, across the line grid · kind BUSINESS_RULE · when submit
Validation shape : the marker is a single exclusive choice across the grid rather than a free
            checkbox per row, so "exactly one" is expressible before the server says it; and
            the rule's second half — a marker that disagrees with its own REMAINDER
            distribution or amount-source type — is surfaced as the catalog's
            `FIN-422-REMAINDER-MARKER` on the offending row. The count is judged by the server
            over the whole persisted set, which is the only place the whole set exists.
Business-code fields: none — this screen mints no business code.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-003:END -->

<!-- SUB:F3-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F3 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

Validation timing for this form: **on submit** (declared once for the whole page) —
there is no unique field on this screen to check on blur.
### F3-FIELD — SCR-FIN-004 (template header, create)
nameAr, nameEn   · REQUIRED · LENGTH (maxLength 150) · when submit
scheduleTypeCode · REQUIRED · LOOKUP_VALID (`RECURRING_SCHEDULE_TYPE`, UXD-FIN-011) ·
                   LENGTH (15) · when submit
frequencyCode    · BUSINESS_RULE (required when the schedule type is RECURRING; not applicable
                   to REVERSING — SRS ENT-FIN-011) · LOOKUP_VALID (`RECURRING_FREQUENCY`,
                   UXD-FIN-012) · LENGTH (15) · when submit
startDate        · REQUIRED · when submit
endDate          · optional · DATE_RANGE (not before `startDate`) · when submit
### F3-FIELD — SCR-FIN-004 (template line)
accountId        · REQUIRED · when submit
amount           · REQUIRED · BUSINESS_RULE (positive — RULE-FIN-006/POL-FIN-005: the amount
                   carries no sign, the direction does) · when submit
directionCode    · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
dimensionValueId · optional · when submit
### F3-VALIDATION — RULE-FIN-006 (applied at run time, not at save)   traces=REQ-FIN-018,AC-FIN-018
Statement : The system shall reject posting an entry whose total debits do not equal its total
            credits to the smallest currency unit.
Message   : from the catalog code `FIN-409-UNBALANCED` —
            ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" ·
            en: "The entry is unbalanced — total debits do not equal total credits"
Scope     : the RUN of the template (API-FIN-014), not its creation — the SRS §B5 is explicit
            that the balance check is applied at run time, not at save time
Field     : the line grid · kind BUSINESS_RULE · when submit (of the run)
Validation shape : the grid shows a running debit and credit total while the template is
            drafted, as a display; it does **not** block the save, because an unbalanced
            template is a legal row the server accepts and refuses only when run. On the run,
            the catalog message is shown as a user message beside the template.
`FIN-400-MISSING-FREQUENCY` is the server's answer to the frequency rule above and is routed
inline to `frequencyCode`; the field is hidden, not disabled, when the schedule type is
REVERSING, because the SRS calls it "not applicable" rather than empty.
Business-code fields: none.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit or on run and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-004:END -->

<!-- SUB:F3-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F3 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

Validation timing for this form: **on submit** (declared once for the whole page).
### F3-FIELD — SCR-FIN-005 (rule header, create)
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sourceAccountId · REQUIRED · when submit
### F3-FIELD — SCR-FIN-005 (allocation target)
targetAccountId      · REQUIRED · when submit
dimensionValueId     · optional · when submit
distributionTypeCode · REQUIRED · LOOKUP_VALID (`DISTRIBUTION_TYPE`, UXD-FIN-010) ·
                       LENGTH (15) · when submit
distributionValue    · BUSINESS_RULE (required unless the distribution type is REMAINDER —
                       SRS ENT-FIN-014) · when submit
isRemainderFl        · BUSINESS_RULE (RULE-FIN-003) · when submit
### F3-VALIDATION — RULE-FIN-003      traces=REQ-FIN-025,AC-FIN-025
Statement : The system shall require exactly one target marked as the remainder whenever the
            set forms a compound or percentage distribution.
Message   : from the catalog code `FIN-409-REMAINDER-COUNT` — the same ar/en pair the rule
            declares, shown on the target grid; a marker disagreeing with its own type is the
            catalog's `FIN-422-REMAINDER-MARKER` on the offending row
Scope     : CREATE of the target set, and again at RUN — the server re-validates the set when
            the rule runs, not only when it is created
Field     : isRemainderFl, across the target grid · kind BUSINESS_RULE · when submit
Validation shape : one exclusive marker across the grid, as on SCR-FIN-003. The grid also
            shows the percentage targets' running sum as a display.
### F3-VALIDATION — RULE-FIN-010      traces=REQ-FIN-026,AC-FIN-026
Statement : The system shall compute the remainder line's amount as a difference after every
            percentage line rounds to the smallest currency unit, and that amount must be
            positive.
Message   : from the catalog codes `FIN-422-REMAINDER-NOT-POSITIVE` and the rule's own text —
            ar: "سطر الباقي يُحسب كفرق، لا كنسبة" ·
            en: "The remainder line is computed as a difference, never as a percentage"
Scope     : the RUN of the rule (API-FIN-017)
Field     : the remainder target · kind BUSINESS_RULE · when submit (of the run)
Validation shape : **server-side only, and deliberately not previewed.** The remainder depends
            on the source account's balance at the moment of the run, which no published
            endpoint gives this screen; the remainder cell therefore shows the word
            "الباقي / remainder" instead of a figure. Showing a predicted number would invite
            trust in a value the server has not produced, and the rule's own message says the
            remainder is a difference and never a percentage.
Business-code fields: none.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit or on run and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-005:END -->

<!-- SUB:F3-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F3 · SCR-FIN-006 — قيود اليومية / Journal entries

Validation timing for this form: **on submit** (declared once for the whole entry page).
REQ-FIN-015 requires every failing check to come back together, so the submission is the point
at which the entry is judged; nothing pre-empts it.
### F3-FIELD — SCR-FIN-006 (entry header, create)
docDate         · REQUIRED · DATE_RANGE (inside the selected period — RULE-FIN-017) · when submit
fiscalYearId    · REQUIRED · when submit
periodId        · REQUIRED · BUSINESS_RULE (must belong to the selected year — RULE-FIN-017) ·
                  when submit
journalTypeCode · REQUIRED, fixed to `MANUAL`, read-only — in the model because the request
                  requires it, not an input (ADR-FIN-008)
descriptionAr, descriptionEn · optional · when submit
### F3-FIELD — SCR-FIN-006 (entry line, repeating)
accountId       · REQUIRED · BUSINESS_RULE (a leaf, active account — RULE-FIN-007) · when submit
amount          · REQUIRED · BUSINESS_RULE (positive — POL-FIN-005) · when submit
directionCode   · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
descriptionAr, descriptionEn · optional
dimensions[].dimensionId, dimensions[].dimensionValueId · REQUIRED together when a dimension
                  is used · BUSINESS_RULE (the value must belong to the dimension and be
                  active — RULE-FIN-009) · when submit
### F3-VALIDATION — RULE-FIN-006      traces=REQ-FIN-018,AC-FIN-018
Statement : total debits must equal total credits to the smallest currency unit.
Message   : `FIN-409-UNBALANCED` — ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي
            الدائن" · en: "The entry is unbalanced — total debits do not equal total credits"
Scope     : CREATE
Field     : the line grid · kind BUSINESS_RULE · when submit
Validation shape : the live totals at the foot of the grid show the difference as the user
            types, and the Post affordance stays enabled regardless. Disabling it would hide
            the other failing checks REQ-FIN-015 asks to be shown together.
### F3-VALIDATION — RULE-FIN-007      traces=REQ-FIN-019,AC-FIN-019
Statement : a line may not target an account that is not a leaf, not active, or not marked as
            accepting direct posting.
Message   : `FIN-409-NOT-POSTABLE-ACCOUNT` — ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" ·
            en: "The target account does not accept direct posting"
Scope     : CREATE · Field : accountId per line · kind BUSINESS_RULE · when submit
Validation shape : the account picker filters to `isLeafFl = true` and `isActiveFl = true`
            through API-FIN-001's own filters, so the common case never reaches the server as
            a failure; the server's refusal is still routed to the offending line, because the
            account's state may have changed since the picker loaded.
### F3-VALIDATION — RULE-FIN-008      traces=REQ-FIN-020,AC-FIN-020
Statement : the entry's period must be Open at the moment of posting.
Message   : `FIN-409-PERIOD-NOT-OPEN` — ar: "الفترة المستهدفة غير مفتوحة" ·
            en: "The target period is not open"
Scope     : CREATE · Field : periodId · kind BUSINESS_RULE · when submit
Validation shape : **server-side only at the moment that matters.** The period select shows
            each period's state and defaults to an Open one, but the check is at post time, not
            build time (RULE-FIN-008's own words), so a period that closed while the entry was
            being typed is caught by the server and its message routed to the period field.
### F3-VALIDATION — RULE-FIN-009      traces=REQ-FIN-021,AC-FIN-021
Statement : a cited dimension value must belong to its stated dimension and be active.
Message   : `FIN-409-INVALID-DIMENSION` — ar: "قيمة البُعد غير صالحة" ·
            en: "The dimension value is invalid"
Scope     : CREATE · Field : the line's dimension pair · kind LOOKUP_VALID + BUSINESS_RULE ·
            when submit
Validation shape : the value select is loaded from API-FIN-008 filtered by the chosen
            dimension and by `isActiveFl`, so it cannot offer a value of another dimension;
            activity can still change under it, and the server's refusal names the line.
### F3-VALIDATION — RULE-FIN-017      traces=REQ-FIN-014,AC-FIN-014
Statement : the submitted period must belong to the submitted fiscal year, and the document
            date must fall inside that period.
Message   : from the catalog codes `FIN-400-PERIOD-NOT-IN-YEAR` and
            `FIN-400-DOCDATE-OUTSIDE-PERIOD` —
            ar: "الفترة المحددة لا تتبع السنة المالية المحددة، أو تاريخ المستند خارج نطاقها" ·
            en: "The selected period does not belong to the selected fiscal year, or the
            document date falls outside it"
Scope     : CREATE · Field : fiscalYearId, periodId, docDate · kind DATE_RANGE +
            BUSINESS_RULE · when submit
Validation shape : the period select is narrowed to the chosen year and the date picker is
            bounded by the selected period's own `startDate` and `endDate`, both of which the
            period row already carries — so the pairing is expressible client-side and the two
            catalog codes are routed inline to the fields they name.
### F3-VALIDATION — RULE-FIN-016      traces=REQ-FIN-016,AC-FIN-016
Statement : a POSTED entry may not be edited or deleted; correction is only through a reversal.
Message   : the rule's own text — ar: "القيد المُرحَّل مقفل؛ التصحيح فقط عبر العكس" ·
            en: "A posted entry is locked; correction is only through a reversal"
Scope     : ALL · Field : the whole entry · kind BUSINESS_RULE · not a form check at all
Validation shape : there is **no form to validate**: a posted entry opens read-only with no
            edit and no delete affordance anywhere on it, and the rule is expressed by the
            absence of the path rather than by a message on a control that would refuse.
### F3-VALIDATION — RULE-FIN-013      traces=REQ-FIN-030,AC-FIN-030
Statement : a reverse action is rejected on an entry that is not POSTED.
Message   : `FIN-409-NOT-POSTED` — ar: "لا يمكن عكس قيد غير مُرحَّل" ·
            en: "A non-posted entry cannot be reversed" — and `FIN-409-ALREADY-REVERSED` for
            an entry that already carries a reversal link
Scope     : the reverse action · Field : none (a row action) · kind BUSINESS_RULE · when submit
Validation shape : the affordance is drawn only on an entry whose `statusCode` is POSTED and
            whose `reversalEntryId` is absent, both of which the response carries; the server's
            refusal is still shown, because the row may be stale.
Business-code fields: `docNo` is system-generated and displayed read-only; the form never
composes or predicts it.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE, or without the reverse action, receives
`FIN-403-FORBIDDEN` on submit and the page shows the localized forbidden message; no field is
pre-emptively disabled, because neither permission is readable (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-006:END -->

<!-- SUB:F3-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F3 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

Validation timing for this form: **on blur for the year code, on submit for the rest**.
The period transitions carry no form at all — each is a path-id call with no body.
### F3-FIELD — SCR-FIN-007 (fiscal year, create)
code        · REQUIRED · LENGTH (maxLength 10) · UNIQUE_CHECK · when blur
startDate   · REQUIRED · when submit
endDate     · REQUIRED · DATE_RANGE (after `startDate`) · when submit
periodCount · REQUIRED · when submit
UNIQUE_CHECK : the year code has no published search to check against — no fiscal-year search
               exists (ADR-FIN-006) — so the check is **not** written as an async pre-check.
               `FIN-409-YEAR-DUP` from the server is the only authority, routed inline to
               `code`. A pre-check over the period rows would test a proxy, not the code.
### F3-VALIDATION — RULE-FIN-014      traces=REQ-FIN-035,AC-FIN-035
Statement : The system shall reject any attempt to reopen a Hard Closed period.
Message   : from the catalog code `FIN-409-NOT-REOPENABLE` —
            ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" ·
            en: "The period is hard-closed and cannot be reopened"
Scope     : the open action (API-FIN-024)
Field     : none — a row action · kind BUSINESS_RULE · when submit
Validation shape : the row offers only the transitions SRS §A7 allows from its current state,
            so a hard-closed row shows no Open affordance at all; the catalog message is still
            routed to a user message, because a row may be stale when the action is taken.
### F3-VALIDATION — RULE-FIN-015      traces=REQ-FIN-038,AC-FIN-038
Statement : The system shall gate the period-close-approval action behind a permission
            distinct from the journal-entry-creation permission, enforced by the Security
            module.
Message   : the rule's own text — ar: "صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود" ·
            en: "The close-approval permission is separate from the entry-creation permission"
            — and, on refusal, the catalog's `FIN-403-FORBIDDEN`
Scope     : the hard-close and year-end-close actions
Field     : none — a row and a header action · kind BUSINESS_RULE · when submit
Validation shape : **server-side only, and by design.** The rule's own `Data source` line
            reads DEFERRED — there is no FIN-side fact to read — and no published endpoint
            tells this screen whether the caller holds `PERM_FIN_PERIODS_CLOSE_APPROVE`. The
            affordance therefore renders for anyone holding the screen and the server's 403 is
            the answer (ADR-FIN-005). Hiding the button would be a weaker copy of a check that
            already exists where the rule puts it.
The year-end close additionally answers `FIN-409-PERIODS-NOT-CLOSED` when a period of the year
is not hard-closed; the header shows that count as context beside the affordance, not as a gate.
Business-code fields: the year `code` is client-defined, not platform-numbered, and is
read-only after create because no update endpoint exists.
Locale       : session → browser → `ar`.
Permission-driven behaviour: as above — the forbidden message is the localized catalog text,
never a silent no-op.

<!-- SUB:F3-SCR-FIN-007:END -->

<!-- SUB:F3-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F3 · SCR-FIN-008 — دفتر الحساب / Account ledger

This screen has **no form**: SRS SCR-REQ-FIN-008 §B3 reads "not applicable — read-only
report", and every field of `AccountLedgerResponse` is read-only.
### F3-FIELD — SCR-FIN-008 (filters, not a form)
accountId        · REQUIRED (the endpoint's required query param) — the report does not run
                   without it, and the screen shows its choose-an-account state instead
fromDate, toDate · optional · DATE_RANGE (`toDate` not before `fromDate`)
dimensionId, dimensionValueId · optional · the value select is loaded from API-FIN-008
                   filtered by the chosen dimension, so it cannot offer a foreign value
Validation shape : filter validation only, written with `zod` over the route's search params
                   so that an address someone shared is validated the same way a typed filter
                   is. No business rule is enforced here, because nothing is written.
No RULE-* is enforced on this screen. `FIN-404-ACCOUNT` from the server is shown as a user
message when the account id in the address does not resolve — which is the case a shared link
to a since-deleted account produces.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen — the navigation
guard of SEC-FE stops the route (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-008:END -->

<!-- SUB:F3-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F3 · SCR-FIN-009 — ميزان المراجعة / Trial balance

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-009 (filters, not a form)
periodId        · optional · the select is served by the shared fiscal-period query
accountTypeCode · optional · LOOKUP_VALID (`ACCOUNT_TYPE`, UXD-FIN-001) — the option list is
                  runtime-loaded, never a static list
Validation shape : filter validation only, over the route's search params. Both filters are
                  optional and the unfiltered request is valid, so there is no required-field
                  state to enforce.
No RULE-* is enforced on this screen. REQ-FIN-040's balance property is asserted by the server
and rendered from `balanced`; the client does not re-derive it, and there is no client-side
condition under which the screen would contradict the report.
`FIN-404-PERIOD` is shown as a user message when a supplied period id does not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-009:END -->

<!-- SUB:F3-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F3 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-010 (filters, not a form)
fiscalYearId · REQUIRED (the endpoint's required query param) — the report does not run until
               it is chosen, and the screen shows its choose-a-year state instead of a blank
               statement
asOfDate     · optional cut-off
Validation shape : filter validation only, over the route's search params.
No RULE-* is enforced on this screen. REQ-FIN-041's continuity is a property of the posted
data — the prior year's closing balances are the opening entry's posted lines — and nothing
here asserts or recomputes it.
`FIN-404-YEAR` is shown as a user message when the year in the address does not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-010:END -->

<!-- SUB:F3-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F3 · SCR-FIN-011 — قائمة الدخل / Income statement

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-011 (filters, not a form)
fiscalYearId             · REQUIRED (the endpoint's required query param)
fromPeriodId, toPeriodId · optional · both selects narrowed to the chosen year, and
                           `toPeriodId` not before `fromPeriodId`
Validation shape : filter validation only, over the route's search params. The date bounds are
                   NOT validated here: the server derives `fromDate`/`toDate` from the chosen
                   periods and returns them, so the client has nothing of its own to check.
No RULE-* is enforced on this screen. REQ-FIN-042's "opens at zero" is the server's result for
a freshly closed year, and the screen labels an all-zero statement as such rather than treating
it as an absence of data.
`FIN-404-YEAR` and `FIN-404-PERIOD` are shown as user messages when an id in the address does
not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-011:END -->

<!-- SUB:F3-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F3 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-012 (filters, not a form)
dimensionId      · REQUIRED (the endpoint's required query param) — the report does not run
                   until a dimension is chosen
dimensionValueId · optional · the select is loaded from API-FIN-008 filtered by the chosen
                   dimension, so it cannot offer a value of another dimension
periodId         · optional · served by the shared fiscal-period query
Validation shape : filter validation only, over the route's search params.
No RULE-* is enforced on this screen. REQ-FIN-043's "never by the base account alone" is a
property of the rows the server returns — one per account-and-dimension-value pair — and the
screen neither merges nor re-aggregates them.
`FIN-404-DIMENSION` and `FIN-404-PERIOD` are shown as user messages when an id in the address
does not resolve.
Business-code fields: `accountCode` and `dimensionValueCode` are displayed read-only, from the
response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-012:END -->

<!-- PHASE:F3:END -->

<!-- PHASE:F4:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 4 — F4 — Screens & Routes

One block per `SCR-*`: routes, chunk, guard, components, mode, facade, shared UI and
cross-module citations. Routes are named by the container pattern — `TREE_MASTER_DETAIL` → a
TreePage hosting the tree and its detail, with the tree route registered **before** any `:id`
route; `FULL_PAGE` with an entry → SearchPage + EntryPage on separate routes; `FULL_PAGE` with
no entry sub-view → a single Page and no entry route. One lazy chunk per composite screen:
search and entry are separate components under ONE `SCR-*` sharing ONE chunk, never a second
chunk for a sub-view. Every `PERM_*` name below is the backend's, never invented here, and
every route sits under the module segment `/finance`.

<!-- SUB:F4-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F4 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F4-SCREEN — SCR-FIN-001            traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `accounts`, under the module segment `/finance` —
               `/finance/accounts` (the tree, registered **before** any `:id` route so a node
               id is never matched as the tree itself) ·
               `/finance/accounts/new` (create, the form beside the tree) ·
               `/finance/accounts/:id` (view) ·
               `/finance/accounts/:id/edit` (edit)
Chunk        : one lazy chunk for this composite screen — tree and form share it; the form is
               never a second chunk
Guard        : every route element guarded by `PERM_FIN_ACCOUNTS_VIEW`, evaluated as
               "`FIN_ACCOUNTS` is present in the caller's effective menu" (ADR-FIN-005).
               CREATE and UPDATE are not readable from any published endpoint, so `/new` and
               `/:id/edit` carry the same VIEW guard and the server's 403 is the authority on
               the write itself.
Components   : `AccountsTreePage` (route-level, TREE_MASTER_DETAIL — hosts the tree and the
               detail form) · `AccountTree`, `AccountFilters`, `AccountForm`,
               `AccountDeactivateConfirm` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` → CREATE,
               `/:id/edit` → EDIT, `/:id` → VIEW — never from a parent prop
Facade       : the SCR-FIN-001 facade of F2; the page never calls a query directly
Shared UI    : tree, filter bar, text field, select, checkbox, confirmation dialog, inline
               field errors, localized message banner
Cross-module : UXD-FIN-001 (account type) and UXD-FIN-002 (nature) — both fields display a
               value whose authoritative source is the lookup module
The selected node is a route param, so an account being edited is linkable and the browser's
back gesture returns to the tree. Creating a child from a selected node pre-fills the parent
and the tree scrolls to the new row on success.

<!-- SUB:F4-SCR-FIN-001:END -->

<!-- SUB:F4-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F4 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F4-SCREEN — SCR-FIN-002            traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035
Routes       : base slug `dimensions`, under `/finance` —
               `/finance/dimensions` (the dimension list) ·
               `/finance/dimensions/new` (create a dimension — a **static** segment registered
               BEFORE the `:id` routes) ·
               `/finance/dimensions/:id` (the dimension with its values) ·
               `/finance/dimensions/:id/values/new` (create a value under it)
Chunk        : one lazy chunk for this composite screen — both panes and both forms share it
Guard        : every route element guarded by `PERM_FIN_DIMENSIONS_VIEW`, evaluated as
               "`FIN_DIMENSIONS` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `DimensionsPage` (route-level, TREE_MASTER_DETAIL) · `DimensionList`,
               `DimensionForm`, `DimensionValueTable`, `DimensionValueForm`,
               `DimensionValueDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match — there is no EDIT mode on either
               resource, because neither has an update endpoint (ADR-FIN-006)
Facade       : the SCR-FIN-002 facade of F2
Shared UI    : split pane, data table, text field, number field, confirmation dialog, inline
               errors, localized message banner
Cross-module : none — every field on this screen is FIN's own (ENT-FIN-002, ENT-FIN-003), and
               no `UXD-*` is cited
The selected dimension is a route param, so a dimension's value list is a shareable address.
No deactivate affordance is drawn on the dimension itself: no endpoint exists (ADR-FIN-006).

<!-- SUB:F4-SCR-FIN-002:END -->

<!-- SUB:F4-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F4 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F4-SCREEN — SCR-FIN-003            traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010
Routes       : base slug `engine-rules`, under `/finance` —
               `/finance/engine-rules` (search) ·
               `/finance/engine-rules/new` (create the rule header — a static segment before
               the `:id` routes) ·
               `/finance/engine-rules/:id` (the rule page with its line grid) ·
               `/finance/engine-rules/:id/lines/new` (add a line)
Chunk        : one lazy chunk for this composite screen — search page and rule page share it
Guard        : every route element guarded by `PERM_FIN_RULES_VIEW`, evaluated as
               "`FIN_RULES` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `EngineRulesSearchPage` (route-level, FULL_PAGE) · `EngineRulePage`
               (route-level, FULL_PAGE — the header and its lines) · `RuleFilters`,
               `RuleResultTable`, `RuleHeaderForm`, `RuleLineGrid`, `RuleLineForm`,
               `RuleDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match; there is no EDIT mode — neither
               the rule nor the line has an update endpoint (ADR-FIN-006)
Facade       : the SCR-FIN-003 facade of F2
Shared UI    : data table, filter bar, text field, select, exclusive-choice control (the
               remainder marker across the grid), confirmation dialog, inline errors,
               localized message banner
Cross-module : UXD-FIN-007 (event type), UXD-FIN-008 (account derivation type), UXD-FIN-009
               (amount source type), UXD-FIN-010 (distribution type), UXD-FIN-002 (direction)
Search and the rule page are separate components under ONE `SCR-*` sharing ONE chunk, linked
by the `:id` route param. The line grid's three references stay three columns and are never
collapsed into one control.

<!-- SUB:F4-SCR-FIN-003:END -->

<!-- SUB:F4-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F4 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F4-SCREEN — SCR-FIN-004            traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012
Routes       : base slug `recurring-templates`, under `/finance` —
               `/finance/recurring-templates` (search) ·
               `/finance/recurring-templates/new` (create — a static segment registered BEFORE
               the `:id` route) ·
               `/finance/recurring-templates/:id` (the template page, read-only)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_RECURRING_TEMPLATES_VIEW`, evaluated
               as "`FIN_RECURRING_TEMPLATES` is present in the caller's effective menu"
               (ADR-FIN-005)
Components   : `RecurringTemplatesSearchPage` (route-level, FULL_PAGE) ·
               `RecurringTemplatePage` (route-level, FULL_PAGE — header and line grid) ·
               `TemplateFilters`, `TemplateResultTable`, `TemplateHeaderForm`,
               `TemplateLineGrid`, `TemplateRunConfirm`, `TemplateDeactivateConfirm`
               (presentational)
Mode         : CREATE | VIEW resolved from the route match; no EDIT mode exists (ADR-FIN-006)
Facade       : the SCR-FIN-004 facade of F2
Shared UI    : data table, filter bar, text field, select, date field, number field,
               confirmation dialog, inline errors, localized message banner
Cross-module : UXD-FIN-011 (schedule type), UXD-FIN-012 (frequency), UXD-FIN-002 (direction)
The header and its lines are one submission, so the create route is a single page rather than
a wizard. On a successful run the returned entry's id is used to offer navigation to
`/finance/journal-entries/:id`, which is SCR-FIN-006's own route and guard — this screen never
renders an entry itself.

<!-- SUB:F4-SCR-FIN-004:END -->

<!-- SUB:F4-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F4 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F4-SCREEN — SCR-FIN-005            traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010
Routes       : base slug `allocation-rules`, under `/finance` —
               `/finance/allocation-rules` (search) ·
               `/finance/allocation-rules/new` (create — a static segment before the `:id`
               route) ·
               `/finance/allocation-rules/:id` (the rule page, read-only)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_ALLOCATION_RULES_VIEW`, evaluated as
               "`FIN_ALLOCATION_RULES` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `AllocationRulesSearchPage` (route-level, FULL_PAGE) · `AllocationRulePage`
               (route-level, FULL_PAGE — header and target grid) · `AllocationRuleFilters`,
               `AllocationRuleResultTable`, `AllocationRuleHeaderForm`, `AllocationTargetGrid`,
               `AllocationRunConfirm`, `AllocationDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match; no EDIT mode exists (ADR-FIN-006)
Facade       : the SCR-FIN-005 facade of F2
Shared UI    : data table, filter bar, text field, select, number field, exclusive-choice
               control (the remainder target), confirmation dialog, inline errors, localized
               message banner
Cross-module : UXD-FIN-010 (distribution type)
The remainder target's amount cell renders the word "الباقي / remainder" rather than a figure,
which is the routing decision of F3's RULE-FIN-010 block expressed as a component. On a
successful run the returned entry is offered on SCR-FIN-006's route, never rendered here.

<!-- SUB:F4-SCR-FIN-005:END -->

<!-- SUB:F4-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F4 · SCR-FIN-006 — قيود اليومية / Journal entries

### F4-SCREEN — SCR-FIN-006            traces=REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-027,AC-FIN-028,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006
Routes       : base slug `journal-entries`, under `/finance` —
               `/finance/journal-entries` (search) ·
               `/finance/journal-entries/new` (the manual entry page — a static segment
               registered BEFORE the `:id` route) ·
               `/finance/journal-entries/:id` (the entry, read-only, with the Reverse action)
               There is no `:id/edit` route at all: a POSTED entry is locked (RULE-FIN-016),
               and the absence of the route is how that is expressed in the router.
Chunk        : one lazy chunk for this composite screen — search, entry page and the read-only
               entry share it
Guard        : every route element guarded by `PERM_FIN_JOURNAL_ENTRIES_VIEW`, evaluated as
               "`FIN_JOURNAL_ENTRIES` is present in the caller's effective menu"
               (ADR-FIN-005). CREATE and the custom reverse action are not readable, so `/new`
               carries the same VIEW guard and the server's 403 is the authority on the write.
Components   : `JournalEntriesSearchPage` (route-level, FULL_PAGE) · `JournalEntryPage`
               (route-level, FULL_PAGE — create mode, or read-only on a posted entry) ·
               `EntryFilters`, `EntryResultTable`, `EntryHeaderForm`, `EntryLineGrid`,
               `EntryLineDimensions`, `EntryTotalsBar`, `ReverseConfirm`,
               `ValidationFailureList` (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new` → CREATE, `/:id` → VIEW.
               There is no EDIT mode to resolve.
Facade       : the SCR-FIN-006 facade of F2; pages never call queries directly
Shared UI    : data table, filter bar, date field, date-range filter, select, number field,
               editable line grid, totals bar, confirmation dialog, inline errors, localized
               message banner
Cross-module : UXD-FIN-005 (journal type), UXD-FIN-006 (status), UXD-FIN-002 (direction)
`ValidationFailureList` exists because REQ-FIN-015 asks for every failing check at once: the
refusals of one submission are listed together above the entry, each also routed inline to the
line or field it names, and nothing the user typed is cleared. API-FIN-020 has no component
and no route on this screen (ADR-FIN-007); its entries appear in the list like any other.

<!-- SUB:F4-SCR-FIN-006:END -->

<!-- SUB:F4-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F4 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F4-SCREEN — SCR-FIN-007            traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004
Routes       : base slug `fiscal-periods`, under `/finance` —
               `/finance/fiscal-periods` (the year list beside the period list, registered
               **before** any `:id` route) ·
               `/finance/fiscal-periods/new-year` (create a fiscal year — a static segment
               before the `:id` routes) ·
               `/finance/fiscal-periods/:yearId` (that year's periods)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_PERIODS_VIEW`, evaluated as
               "`FIN_PERIODS` is present in the caller's effective menu" (ADR-FIN-005).
               `PERM_FIN_PERIODS_CLOSE_APPROVE` is not readable, so the hard-close and
               year-end-close affordances render under the same VIEW guard and the server's
               403 is the authority — which is exactly what RULE-FIN-015 asks for.
Components   : `FiscalCalendarPage` (route-level, TREE_MASTER_DETAIL — years beside their
               periods) · `FiscalYearList`, `FiscalYearForm`, `FiscalPeriodTable`,
               `PeriodFilters`, `PeriodTransitionConfirm`, `YearEndCloseConfirm`
               (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new-year` → CREATE,
               `/:yearId` → VIEW. Neither resource has an EDIT mode (ADR-FIN-006).
Facade       : the SCR-FIN-007 facade of F2
Shared UI    : split pane, data table, text field, date field, number field, confirmation
               dialog, global busy indicator (the year-end close alone), inline errors,
               localized message banner
Cross-module : UXD-FIN-003 (period state), UXD-FIN-004 (fiscal year status)
The year list is derived from the period rows' `fiscalYearId` (ADR-FIN-006) and is presented
as an ordinary list; the indirection is not exposed to the user. Each period row renders only
the transitions §A7 allows from its current state, so a hard-closed row has no Open affordance
at all. On a successful year-end close the two returned entries are offered on SCR-FIN-006's
route.

<!-- SUB:F4-SCR-FIN-007:END -->

<!-- SUB:F4-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F4 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F4-SCREEN — SCR-FIN-008            traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005
Routes       : base slug `account-ledger`, under `/finance` —
               `/finance/account-ledger` — the only route; no `new`, no `:id`, no `:id/edit`,
               because this screen addresses no record it could edit. The account, date range
               and dimension live in the route's search params, so the report IS its address
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_ACCOUNT_LEDGER_VIEW`, evaluated as
               "`FIN_ACCOUNT_LEDGER` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `AccountLedgerPage` (route-level, FULL_PAGE) · `LedgerFilters`,
               `LedgerSummaryHeader`, `LedgerRowTable` (presentational)
Mode         : not applicable — no CREATE, EDIT or VIEW mode exists to resolve; this screen
               writes nothing
Facade       : the SCR-FIN-008 facade of F2
Shared UI    : filter bar, account picker, date-range filter, select, data table, localized
               message banner
Cross-module : UXD-FIN-001 (account type), UXD-FIN-002 (nature and direction), UXD-FIN-005
               (journal type on each row)
Each row's document number links to `/finance/journal-entries/:id`, which is SCR-FIN-006's own
route and carries its own guard — the third hop of REQ-FIN-046's chain. This screen is the
drill-down target of SCR-FIN-009 and SCR-FIN-012, and arrives with its filters already in the
address.

<!-- SUB:F4-SCR-FIN-008:END -->

<!-- SUB:F4-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F4 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F4-SCREEN — SCR-FIN-009            traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `trial-balance`, under `/finance` —
               `/finance/trial-balance` — the only route; both filters live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_TRIAL_BALANCE_VIEW`, evaluated as
               "`FIN_TRIAL_BALANCE` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `TrialBalancePage` (route-level, FULL_PAGE) · `TrialBalanceFilters`,
               `BalancedBanner`, `AccountBalanceTable` (presentational)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-009 facade of F2
Shared UI    : filter bar, select, data table, status banner, localized message banner
Cross-module : UXD-FIN-001 (account type), UXD-FIN-002 (nature)
`BalancedBanner` renders the server's `balanced` value and nothing derived: REQ-FIN-040 makes
the equality the report's property, and a client that recomputed it could contradict the
report it is displaying. Each row's account links to `/finance/account-ledger` carrying the
account and the period's range — the second hop of the drill-down chain. This screen is itself
the target of SCR-FIN-010's and SCR-FIN-011's statement lines.

<!-- SUB:F4-SCR-FIN-009:END -->

<!-- SUB:F4-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F4 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F4-SCREEN — SCR-FIN-010            traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `balance-sheet`, under `/finance` —
               `/finance/balance-sheet` — the only route; the fiscal year and as-of date live
               in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_BALANCE_SHEET_VIEW`, evaluated as
               "`FIN_BALANCE_SHEET` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `BalanceSheetPage` (route-level, FULL_PAGE) · `StatementFilters`,
               `StatementSection`, `AccountBalanceTable` (presentational — the table is the
               same component SCR-FIN-009 uses, since the row shape is the same)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-010 facade of F2
Shared UI    : filter bar, select, date field, data table, section headings, localized message
               banner
Cross-module : UXD-FIN-001 (account type — the section heading), UXD-FIN-002 (nature)
The required fiscal year gates the call, so the page shows a choose-a-year state rather than a
blank statement. Each row links to `/finance/trial-balance` narrowed to that account type —
the first hop of REQ-FIN-046's chain.

<!-- SUB:F4-SCR-FIN-010:END -->

<!-- SUB:F4-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F4 · SCR-FIN-011 — قائمة الدخل / Income statement

### F4-SCREEN — SCR-FIN-011            traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `income-statement`, under `/finance` —
               `/finance/income-statement` — the only route; the fiscal year and the two
               period ids live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_INCOME_STATEMENT_VIEW`, evaluated as
               "`FIN_INCOME_STATEMENT` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `IncomeStatementPage` (route-level, FULL_PAGE) · `StatementFilters`,
               `StatementSection`, `AccountBalanceTable`, `NetResultFooter` (presentational —
               the first three shared with SCR-FIN-010)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-011 facade of F2
Shared UI    : filter bar, select, data table, section headings, localized message banner
Cross-module : UXD-FIN-001 (account type — the section heading), UXD-FIN-002 (nature)
The period range is two selects narrowed to the chosen year, and the dates the server derived
from them are shown read-only beside the filters. An all-zero statement for a freshly closed
year is labelled as the correct result of REQ-FIN-042, not as an empty list. Each row links to
`/finance/trial-balance` for that account type.

<!-- SUB:F4-SCR-FIN-011:END -->

<!-- SUB:F4-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F4 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F4-SCREEN — SCR-FIN-012            traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002
Routes       : base slug `dimension-reports`, under `/finance` —
               `/finance/dimension-reports` — the only route; the dimension, its value and the
               period live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_DIMENSION_REPORTS_VIEW`, evaluated as
               "`FIN_DIMENSION_REPORTS` is present in the caller's effective menu"
               (ADR-FIN-005)
Components   : `DimensionReportPage` (route-level, FULL_PAGE) · `DimensionReportFilters`,
               `DimensionReportTable` (presentational)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-012 facade of F2
Shared UI    : filter bar, select, data table, localized message banner
Cross-module : UXD-FIN-002 (nature). The dimension and its values are FIN's own entities, read
               through this module's own endpoints, so they cite no `UXD-*`
The table renders the account and the dimension value as two columns of the same row and never
merges them, which is REQ-FIN-043 expressed in the component. Each row links to
`/finance/account-ledger` carrying the account **and** the dimension pair, so the ledger behind
the figure shows the same slice.

<!-- SUB:F4-SCR-FIN-012:END -->

<!-- PHASE:F4:END -->

<!-- PHASE:SEC-FE:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012,REQ-FIN-044,AC-FIN-044 -->
## PHASE 5 — SEC-FE

The frontend half of the security model, per `SCR-*`: the navigation guard and the per-action
UI behaviour. Permission names are the backend registry's and the SRS Access summary's, never
redeclared. One mechanism gates every screen — the **menu gate**: the screen's page code is
present in the effective menu the security module serves for this caller, which exists because
REQ-FIN-044 registers FIN's module, screens and actions there as data. Action-level
permissions are not readable from any published endpoint, so an action's affordance renders for
a caller who holds the screen and the server's `FIN-403-FORBIDDEN` is the authority, shown as
its localized catalog message (ADR-FIN-005). Never split — level-1 only.

### SEC-FE · SCR-FIN-001 — شجرة الحسابات / Chart of accounts
Permissions      : `PERM_FIN_ACCOUNTS_VIEW`, `PERM_FIN_ACCOUNTS_CREATE`,
`PERM_FIN_ACCOUNTS_UPDATE`
Navigation guard : `FIN_ACCOUNTS` must be present in the caller's effective menu; a caller
without it is sent to the unauthorized destination, and every route of this screen — the tree,
`new`, `:id`, `:id/edit` — carries the same guard.
Per action       : VIEW → the gate above, exact. CREATE (new account) and UPDATE (edit, and
deactivate) → the affordances render for a caller who holds the screen, and `FIN-403-FORBIDDEN`
from the server is shown as the localized forbidden message (ADR-FIN-005). DELETE → no delete
action exists: deactivation is an UPDATE (API-FIN-004), and the SRS Access summary leaves this
screen's DELETE column empty.

### SEC-FE · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values
Permissions      : `PERM_FIN_DIMENSIONS_VIEW`, `PERM_FIN_DIMENSIONS_CREATE`,
`PERM_FIN_DIMENSIONS_UPDATE`
Navigation guard : `FIN_DIMENSIONS` must be present in the caller's effective menu; every route
of this screen carries it.
Per action       : VIEW → the gate above. CREATE (a dimension, or a value under it) → the
affordances render and the server's 403 is the authority. UPDATE → it covers exactly one
operation, deactivating a dimension **value** (API-FIN-035); the parent dimension has no
deactivate affordance because no endpoint exists for it (ADR-FIN-006), so nothing is gated
there. DELETE → no delete action exists on this screen.

### SEC-FE · SCR-FIN-003 — قواعد المحرك / Engine rules
Permissions      : `PERM_FIN_RULES_VIEW`, `PERM_FIN_RULES_CREATE`, `PERM_FIN_RULES_UPDATE`
Navigation guard : `FIN_RULES` must be present in the caller's effective menu; every route of
this screen carries it.
Per action       : VIEW → the gate above. CREATE (a rule header) and UPDATE (adding a line,
API-FIN-011; deactivating the rule, API-FIN-034 — both under the one `PERM_FIN_RULES_UPDATE`)
→ the affordances render and the server's 403 is the authority. DELETE → no delete action
exists: there is no rule-line delete endpoint and V24 seeds no `PERM_FIN_RULES_DELETE`
(ADR-FIN-006).

### SEC-FE · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates
Permissions      : `PERM_FIN_RECURRING_TEMPLATES_VIEW`,
`PERM_FIN_RECURRING_TEMPLATES_CREATE`, `PERM_FIN_RECURRING_TEMPLATES_UPDATE`
Navigation guard : `FIN_RECURRING_TEMPLATES` must be present in the caller's effective menu;
every route of this screen carries it.
Per action       : VIEW → the gate above. CREATE (a template with its lines) and UPDATE (run,
API-FIN-014; deactivate, API-FIN-036 — both under the one
`PERM_FIN_RECURRING_TEMPLATES_UPDATE`) → the affordances render and the server's 403 is the
authority. DELETE → no delete action exists. No Edit affordance is drawn at all, since no
update endpoint is published (ADR-FIN-006) — an absent affordance, not a gated one.

### SEC-FE · SCR-FIN-005 — قواعد التوزيع / Allocation rules
Permissions      : `PERM_FIN_ALLOCATION_RULES_VIEW`, `PERM_FIN_ALLOCATION_RULES_CREATE`,
`PERM_FIN_ALLOCATION_RULES_UPDATE`
Navigation guard : `FIN_ALLOCATION_RULES` must be present in the caller's effective menu; every
route of this screen carries it.
Per action       : VIEW → the gate above. CREATE (a rule with its targets) and UPDATE (run,
API-FIN-017; deactivate, API-FIN-037 — both under the one `PERM_FIN_ALLOCATION_RULES_UPDATE`)
→ the affordances render and the server's 403 is the authority. DELETE → no delete action
exists. No Edit affordance is drawn (ADR-FIN-006).

### SEC-FE · SCR-FIN-006 — قيود اليومية / Journal entries
Permissions      : `PERM_FIN_JOURNAL_ENTRIES_VIEW`, `PERM_FIN_JOURNAL_ENTRIES_CREATE`,
and the custom action `PERM_FIN_JOURNAL_ENTRIES_REVERSE`
Navigation guard : `FIN_JOURNAL_ENTRIES` must be present in the caller's effective menu; the
search, `new` and `:id` routes all carry it.
Per action       : VIEW → the gate above. CREATE (the manual entry, posting included) and the
custom reverse action → the affordances render for a caller who holds the screen, and
`FIN-403-FORBIDDEN` is shown as the localized forbidden message (ADR-FIN-005). UPDATE and
DELETE → **neither exists on this screen at all**, and their absence is RULE-FIN-016 rather
than a permission decision: a posted entry is locked, there is no edit route to guard, and the
SRS Access summary leaves both columns empty.

### SEC-FE · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years
Permissions      : `PERM_FIN_PERIODS_VIEW`, `PERM_FIN_PERIODS_CREATE`,
`PERM_FIN_PERIODS_UPDATE`, and the distinct custom action `PERM_FIN_PERIODS_CLOSE_APPROVE`
Navigation guard : `FIN_PERIODS` must be present in the caller's effective menu; every route of
this screen carries it.
Per action       : VIEW → the gate above, and since API-FIN-033 it is also the permission
behind a real read. CREATE (a fiscal year) and UPDATE (open, soft-close) → the affordances
render and the server's 403 is the authority. The close-approval action (hard-close,
API-FIN-026; year-end close, API-FIN-027) is gated by its **own** permission, distinct from
`PERM_FIN_JOURNAL_ENTRIES_CREATE` — which is exactly what RULE-FIN-015 requires — and it is
**not readable from any published endpoint**, so its affordances render under the screen's
VIEW gate and a caller who does not hold it receives the server's localized forbidden message
(ADR-FIN-005). Hiding the affordance would be a weaker copy of a check the Security module
already performs. DELETE → no delete action exists on this screen.

### SEC-FE · SCR-FIN-008 — دفتر الحساب / Account ledger
Permissions      : `PERM_FIN_ACCOUNT_LEDGER_VIEW`
Navigation guard : `FIN_ACCOUNT_LEDGER` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE: the SRS Access
summary gives this screen VIEW alone, and the screen writes nothing. The links it draws to
SCR-FIN-006 are rendered unconditionally; the target route's own guard stops a caller who does
not hold it.

### SEC-FE · SCR-FIN-009 — ميزان المراجعة / Trial balance
Permissions      : `PERM_FIN_TRIAL_BALANCE_VIEW`
Navigation guard : `FIN_TRIAL_BALANCE` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-008 are rendered unconditionally and the target's guard is what decides.

### SEC-FE · SCR-FIN-010 — الميزانية العمومية / Balance sheet
Permissions      : `PERM_FIN_BALANCE_SHEET_VIEW`
Navigation guard : `FIN_BALANCE_SHEET` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-009 are rendered unconditionally and the target's guard is what decides.

### SEC-FE · SCR-FIN-011 — قائمة الدخل / Income statement
Permissions      : `PERM_FIN_INCOME_STATEMENT_VIEW`
Navigation guard : `FIN_INCOME_STATEMENT` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-009 are rendered unconditionally and the target's guard is what decides.

### SEC-FE · SCR-FIN-012 — تقارير الأبعاد / Dimension reports
Permissions      : `PERM_FIN_DIMENSION_REPORTS_VIEW`
Navigation guard : `FIN_DIMENSION_REPORTS` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-008 are rendered unconditionally and the target's guard is what decides.

**Across every screen.** A forbidden response is shown as its localized catalog message,
never as a silent no-op and never as a generic failure. An unauthenticated response returns the
caller to the platform's sign-in destination and discards the server-state cache, so no data of
the previous identity survives into the next. No screen composes a permission name, and no
screen holds a local copy of the caller's grants: the menu response is the single source, and a
failure to load it renders no FIN entry and grants no FIN route — access narrows, never widens.

<!-- PHASE:SEC-FE:END -->

<!-- PHASE:ALIGN-FE:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 6 — ALIGN-FE

The alignment self-check is this phase's content: see the section of the same name below, whose
`RESULT` row is written by the orchestrator from the analyze report. Never split — level-1 only.

```
ALIGN-FE — FIN v1
row           backing check   assertion
SCREENS       orphans         every SCR-FIN-001..012 is referenced by a plan block — each has
                              one SUB in F1, F2, F3 and F4 (48 SUB blocks) and one RF5 block
                              in SEC-FE
UXD           orphans         every UXD-FIN-001..012 is cited by a plan block — each is named
                              by the F2-LOOKUP of the screens that display its key and by the
                              Cross-module line of those screens' F4 blocks
TRACES        traces          every PHASE and every SUB carries traces=; every UXD traces to
                              its REQ and its AC; every SCR traces to its REQ and, where it
                              displays foreign data, its UXD
API           traces          every API-FIN-* this plan cites is defined in the fetched
                              api-docs — through the API ID BINDING annex of ADR-FIN-002, and
                              never in the backend plan's contract draft. No foreign module's
                              API id is cited here at all; the one cross-module endpoint this
                              frontend depends on is named in ui-ux-spec-fin.md, where its
                              UXD-* are defined
FOREIGN       xref-surface    every reference to another module's surface resolves in that
                              module's own artifacts
REGISTRY      registry-agree  every UXD and SCR defined here is in registry-exec-fe-fin.md,
                              and nothing else is
LANGUAGES     languages       labels and messages in ar + en
MARKERS       markers         the parser reports no structural or semantic error for the
                              frontend track's exec plan
DECISIONS     refs-exist      every ADR this plan cites exists on disk in erp/decisions/FIN/ —
                              ADR-FIN-002, ADR-FIN-003, ADR-FIN-004, ADR-FIN-005, ADR-FIN-006,
                              ADR-FIN-007, ADR-FIN-008
COVERAGE      (the report)    C7.16 and C7.18 — both P3.1 clauses, over backend
                              artifacts this stage does not write. No C8.* or C9.* clause
                              reported having examined nothing
RESULT        PASSED ✓ — 0 findings
```

### Operations coverage

| Operation | API | SCR action | Route | Status |
|---|---|---|---|---|
| search accounts | API-FIN-001 | SCR-FIN-001 search | /finance/accounts | ✓ |
| create account | API-FIN-002 | SCR-FIN-001 create | /finance/accounts/new | ✓ |
| update account | API-FIN-003 | SCR-FIN-001 edit | /finance/accounts/:id/edit | ✓ |
| deactivate account | API-FIN-004 | SCR-FIN-001 deactivate | /finance/accounts/:id | ✓ |
| search dimensions | API-FIN-005 | SCR-FIN-002 search | /finance/dimensions | ✓ |
| create dimension | API-FIN-006 | SCR-FIN-002 create | /finance/dimensions/new | ✓ |
| create dimension value | API-FIN-007 | SCR-FIN-002 create value | /finance/dimensions/:id/values/new | ✓ |
| search dimension values | API-FIN-008 | SCR-FIN-002 value list | /finance/dimensions/:id | ✓ |
| deactivate dimension value | API-FIN-035 | SCR-FIN-002 deactivate value | /finance/dimensions/:id | ✓ |
| search event-type rules | API-FIN-009 | SCR-FIN-003 search | /finance/engine-rules | ✓ |
| create event-type rule | API-FIN-010 | SCR-FIN-003 create | /finance/engine-rules/new | ✓ |
| add rule line | API-FIN-011 | SCR-FIN-003 add line | /finance/engine-rules/:id/lines/new | ✓ |
| deactivate event-type rule | API-FIN-034 | SCR-FIN-003 deactivate | /finance/engine-rules/:id | ✓ |
| search recurring templates | API-FIN-012 | SCR-FIN-004 search | /finance/recurring-templates | ✓ |
| create recurring template | API-FIN-013 | SCR-FIN-004 create | /finance/recurring-templates/new | ✓ |
| run recurring template | API-FIN-014 | SCR-FIN-004 run | /finance/recurring-templates/:id | ✓ |
| deactivate recurring template | API-FIN-036 | SCR-FIN-004 deactivate | /finance/recurring-templates/:id | ✓ |
| search allocation rules | API-FIN-015 | SCR-FIN-005 search | /finance/allocation-rules | ✓ |
| create allocation rule | API-FIN-016 | SCR-FIN-005 create | /finance/allocation-rules/new | ✓ |
| run allocation rule | API-FIN-017 | SCR-FIN-005 run | /finance/allocation-rules/:id | ✓ |
| deactivate allocation rule | API-FIN-037 | SCR-FIN-005 deactivate | /finance/allocation-rules/:id | ✓ |
| search journal entries | API-FIN-018 | SCR-FIN-006 search | /finance/journal-entries | ✓ |
| create manual entry (post) | API-FIN-019 | SCR-FIN-006 post | /finance/journal-entries/new | ✓ |
| build entry from an event | API-FIN-020 | — a host system's call | — (ADR-FIN-007) | ✗ |
| reverse a posted entry | API-FIN-021 | SCR-FIN-006 reverse | /finance/journal-entries/:id | ✓ |
| read an entry with its lines | API-FIN-022 | SCR-FIN-006 read | /finance/journal-entries/:id | ✓ |
| search fiscal periods | API-FIN-033 | SCR-FIN-007 search | /finance/fiscal-periods | ✓ |
| create fiscal year | API-FIN-023 | SCR-FIN-007 create year | /finance/fiscal-periods/new-year | ✓ |
| open a period | API-FIN-024 | SCR-FIN-007 open | /finance/fiscal-periods/:yearId | ✓ |
| soft-close a period | API-FIN-025 | SCR-FIN-007 soft-close | /finance/fiscal-periods/:yearId | ✓ |
| hard-close a period (approval) | API-FIN-026 | SCR-FIN-007 hard-close | /finance/fiscal-periods/:yearId | ✓ |
| run year-end close | API-FIN-027 | SCR-FIN-007 year-end close | /finance/fiscal-periods/:yearId | ✓ |
| account ledger | API-FIN-028 | SCR-FIN-008 render | /finance/account-ledger | ✓ |
| trial balance | API-FIN-029 | SCR-FIN-009 render | /finance/trial-balance | ✓ |
| balance sheet | API-FIN-030 | SCR-FIN-010 render | /finance/balance-sheet | ✓ |
| income statement | API-FIN-031 | SCR-FIN-011 render | /finance/income-statement | ✓ |
| dimension report | API-FIN-032 | SCR-FIN-012 render | /finance/dimension-reports | ✓ |
| update a recurring template | — none published | SCR-FIN-004 — not drawn | — (ADR-FIN-006) | ✗ |
| update an allocation rule | — none published | SCR-FIN-005 — not drawn | — (ADR-FIN-006) | ✗ |
| search fiscal years | — none published | SCR-FIN-007 — derived from period rows | — (ADR-FIN-006) | ✗ |
| read account / template / rule / year / period by id | — none published | hydrated from the search cache | — (ADR-FIN-006) | ✗ |
| delete a rule line / template line / target | — none published | not drawn on any screen | — (ADR-FIN-006) | ✗ |
| deactivate the parent dimension | — none published | SCR-FIN-002 — not drawn | — (ADR-FIN-006) | ✗ |

Thirty-seven rows carry a published endpoint; thirty-six of those carry a route and a ✓. Six
rows carry a ✗ with the ADR that explains it — one endpoint published for a caller that is not
this frontend (ADR-FIN-007), and five operations with no endpoint at all (ADR-FIN-006). No row
is a ✗ for want of a decision.

<!-- PHASE:ALIGN-FE:END -->

---

## Hand-off

The implementer reads the phases in profile order — F1 models, F2 hooks, F3 forms, F4 screens
and routes, SEC-FE guards — takes design intent from `ui-ux-spec-fin.md`, and takes every
request and response shape from `_inputs/api-docs-fin.md`. No route, component, permission or
field that is not traceable to an F-block above is invented: a gap is an ADR in
`erp/decisions/FIN/`, never an invention. The plan and its registry are split by the toolkit
into `packages/frontend-execution/` and delivered on the frontend delivery branch after the
`gate:pass-2` verdict, then tagged.

══════════════════════════════════════════════════════════════════
