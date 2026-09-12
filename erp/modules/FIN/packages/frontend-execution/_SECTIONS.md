<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
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
| 1 | F1 — Models & Types | always — one SUB per screen | 12 SUB |
| 2 | F2 — Data Hooks | always — one SUB per screen | 12 SUB |
| 3 | F3 — Forms & Validators | always — one SUB per screen | 12 SUB |
| 4 | F4 — Screens & Routes | always — one SUB per screen | 12 SUB |
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

Twelve screens, and every `sub_bearing` phase splits per screen — one `SUB` per `SCR-*`, at
any screen count — so
every SUB id is phase-qualified — `SUB:F1-SCR-FIN-006` and `SUB:F2-SCR-FIN-006` are distinct
blocks for the same screen under different phases.













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
