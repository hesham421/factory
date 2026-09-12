# FRONTEND TEST PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Scope : module (FIN)
Sources: srs-fin.md v1 · frontend-execution-plan-fin.md v1 · registry-srs-fin.md v1 ·
         registry-exec-fe-fin.md v1
Framework: agnostic (profile.stack.testing.frontend). REDUCED: **no** — P3.2 has run for FIN,
so every test case below binds to a real `SCR-*` and its route.
TC count: 39 — TC-FIN-110 … TC-FIN-148, continuing the module's one TC sequence after the
backend plan's highest id (TC-FIN-109). No id is renumbered and no backend TC is touched.
Open ADRs: 0 new. The plan cites ADR-FIN-003, ADR-FIN-006, ADR-FIN-007 and ADR-FIN-008 where a
screen's behaviour follows one of them.
SUPERSEDES the REDUCED stub this file previously held, which recorded that P3.2 had not run and
asked to be re-run once it had ("None of FIN's 12 `SCR-REQ-*` has yet been turned into a
`SCR-*`/route by P3.2"). That is no longer true: SCR-FIN-001..012 and UXD-FIN-001..012 exist.
══════════════════════════════════════════════════════════════════

Scope is `module`, so this run derives from FIN's own `AC-*` only. The integration phase
`INT-UXD` is **absent by rule**, not empty and not a gap: `UXD-FIN-001..012` all name the
lookup module as the owner of the displayed data, and that module is not in this selection —
§2 rule 1 and §5 of the engine. An `INT-UXD` phase appears the first time this stage runs at
`--modules FIN,MDL` or `--scope project`.

<!-- PHASE:TEST-PLAN-FE:START traces=AC-FIN-001,AC-FIN-002,AC-FIN-003,AC-FIN-004,AC-FIN-005,AC-FIN-006,AC-FIN-007,AC-FIN-008,AC-FIN-009,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-022,AC-FIN-023,AC-FIN-025,AC-FIN-026,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,AC-FIN-039,AC-FIN-040,AC-FIN-041,AC-FIN-042,AC-FIN-043,AC-FIN-046,REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-022,REQ-FIN-023,REQ-FIN-025,REQ-FIN-026,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043,REQ-FIN-046 -->
## TEST-PLAN-FE — FIN v1

Thirty-nine test cases, so the phase splits (threshold: TC count > 8) into the two labels the
profile names: `UI-FLOWS` for the per-screen flows, and `INT-FLOW` for the one flow that
crosses screens. Every case derives from exactly one `AC-*`, cites the `SCR-*` and route it
exercises, and asserts the catalog message in both languages wherever a `RULE-*` fires.

<!-- SUB:UI-FLOWS:START traces=AC-FIN-001,REQ-FIN-001,SCR-FIN-001,API-FIN-002,AC-FIN-002,REQ-FIN-002,API-FIN-003,AC-FIN-003,REQ-FIN-003,API-FIN-004,API-FIN-001,AC-FIN-004,REQ-FIN-004,SCR-FIN-002,API-FIN-006,AC-FIN-005,REQ-FIN-005,API-FIN-007,AC-FIN-006,REQ-FIN-006,AC-FIN-007,REQ-FIN-007,SCR-FIN-003,API-FIN-010,AC-FIN-008,REQ-FIN-008,API-FIN-011,AC-FIN-009,REQ-FIN-009,AC-FIN-014,REQ-FIN-014,SCR-FIN-006,API-FIN-019,AC-FIN-015,REQ-FIN-015,AC-FIN-016,REQ-FIN-016,API-FIN-022,AC-FIN-017,REQ-FIN-017,AC-FIN-018,REQ-FIN-018,AC-FIN-019,REQ-FIN-019,AC-FIN-020,REQ-FIN-020,AC-FIN-021,REQ-FIN-021,AC-FIN-027,REQ-FIN-027,API-FIN-018,AC-FIN-028,REQ-FIN-028,API-FIN-021,AC-FIN-029,REQ-FIN-029,AC-FIN-030,REQ-FIN-030,AC-FIN-022,REQ-FIN-022,SCR-FIN-004,API-FIN-013,AC-FIN-023,REQ-FIN-023,API-FIN-014,AC-FIN-025,REQ-FIN-025,SCR-FIN-005,API-FIN-016,AC-FIN-026,REQ-FIN-026,API-FIN-017,AC-FIN-031,REQ-FIN-031,SCR-FIN-007,API-FIN-023,AC-FIN-032,REQ-FIN-032,API-FIN-024,AC-FIN-033,REQ-FIN-033,API-FIN-025,AC-FIN-034,REQ-FIN-034,API-FIN-026,AC-FIN-035,REQ-FIN-035,AC-FIN-036,REQ-FIN-036,API-FIN-027,AC-FIN-037,REQ-FIN-037,AC-FIN-038,REQ-FIN-038,AC-FIN-039,REQ-FIN-039,SCR-FIN-008,API-FIN-028,AC-FIN-040,REQ-FIN-040,SCR-FIN-009,API-FIN-029,AC-FIN-041,REQ-FIN-041,SCR-FIN-010,API-FIN-030,AC-FIN-042,REQ-FIN-042,SCR-FIN-011,API-FIN-031,AC-FIN-043,REQ-FIN-043,SCR-FIN-012,API-FIN-032 -->
### SUB — UI-FLOWS

Per-screen flows: search, create and edit, the violation as the screen shows it, the state transition, and the permission denial.

<!-- TC:TC-FIN-110:START traces=AC-FIN-001,REQ-FIN-001,SCR-FIN-001,API-FIN-002 -->
### TC-FIN-110 — create an account from the chart tree
Derived from : AC-FIN-001 (REQ-FIN-001) · Exercises: SCR-FIN-001 /finance/accounts/new · API-FIN-002
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: signed in holding FIN_ACCOUNTS VIEW and CREATE; the ACCOUNT_TYPE and DEBIT_CREDIT option lists are loaded; a code not yet used
Steps        : 1. open /finance/accounts 2. select a parent node and choose New 3. fill code, nameAr, nameEn, account type, nature; leave 'accepts direct posting' set 4. submit
Expected     : the account is created and appears in the tree under the selected parent; the form switches to its saved state with `code` read-only
Test data    : code "1000", nameAr "الأصول", nameEn "Assets", accountTypeCode ASSET, natureCode DEBIT
<!-- TC:TC-FIN-110:END -->

<!-- TC:TC-FIN-111:START traces=AC-FIN-002,REQ-FIN-002,SCR-FIN-001,API-FIN-003 -->
### TC-FIN-111 — marking a parent account as accepting direct posting is refused on screen
Derived from : AC-FIN-002 (REQ-FIN-002) · Exercises: SCR-FIN-001 /finance/accounts/:id/edit · API-FIN-003
Rule / code  : RULE-FIN-001 → FIN-409-PARENT-NOT-LEAF-ELIGIBLE / FIN-409-HAS-CHILDREN
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an account that has at least one child account, open in the detail form
Steps        : 1. open /finance/accounts/:id/edit on the parent node 2. set 'accepts direct posting' (isLeafFl) to true 3. submit
Expected     : nothing is saved, the form stays open with its values, and the catalog message is shown — ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" · en: "An account with sub-accounts cannot accept direct posting"
Test data    : a parent account with ≥1 child
<!-- TC:TC-FIN-111:END -->

<!-- TC:TC-FIN-112:START traces=AC-FIN-003,REQ-FIN-003,SCR-FIN-001,API-FIN-004,API-FIN-001 -->
### TC-FIN-112 — deactivating an account leaves it in the tree and out of the active filter
Derived from : AC-FIN-003 (REQ-FIN-003) · Exercises: SCR-FIN-001 /finance/accounts/:id · API-FIN-004, API-FIN-001
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active account, signed in holding FIN_ACCOUNTS VIEW and UPDATE
Steps        : 1. open /finance/accounts and select the account 2. choose Deactivate and confirm 3. set the 'active' filter to true and search again
Expected     : the row's active state becomes false and the node stays in the tree (history is retained); the row is absent from the active-only result set
Test data    : an account with no posted line
<!-- TC:TC-FIN-112:END -->

<!-- TC:TC-FIN-113:START traces=AC-FIN-004,REQ-FIN-004,SCR-FIN-002,API-FIN-006 -->
### TC-FIN-113 — create a dimension
Derived from : AC-FIN-004 (REQ-FIN-004) · Exercises: SCR-FIN-002 /finance/dimensions/new · API-FIN-006
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: signed in holding FIN_DIMENSIONS VIEW and CREATE; the code is not yet used
Steps        : 1. open /finance/dimensions 2. choose New 3. fill code, nameAr, nameEn 4. submit
Expected     : the dimension is created active and appears in the dimension list; its (empty) value pane opens
Test data    : code "PROJECT", nameAr "مشروع", nameEn "Project"
<!-- TC:TC-FIN-113:END -->

<!-- TC:TC-FIN-114:START traces=AC-FIN-005,REQ-FIN-005,SCR-FIN-002,API-FIN-007 -->
### TC-FIN-114 — create a value under a dimension
Derived from : AC-FIN-005 (REQ-FIN-005) · Exercises: SCR-FIN-002 /finance/dimensions/:id/values/new · API-FIN-007
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a dimension is selected; the code is not yet used under it
Steps        : 1. open /finance/dimensions/:id 2. choose New value 3. fill code, nameAr, nameEn, sort order 4. submit
Expected     : the value is created active under that dimension and appears in the value list, ordered by its sort order; the parent id was never typed
Test data    : code "NORTH", nameAr "الشمال", nameEn "North", sortOrder 1
<!-- TC:TC-FIN-114:END -->

<!-- TC:TC-FIN-115:START traces=AC-FIN-006,REQ-FIN-006,SCR-FIN-002,API-FIN-007 -->
### TC-FIN-115 — a duplicate value code under the same dimension is refused on screen
Derived from : AC-FIN-006 (REQ-FIN-006) · Exercises: SCR-FIN-002 /finance/dimensions/:id/values/new · API-FIN-007
Rule / code  : RULE-FIN-002 → FIN-409-DIMVALUE-DUP
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a dimension already holding a value with code "NORTH"
Steps        : 1. open the value form under that same dimension 2. enter code "NORTH" 3. leave the field (blur) 4. submit
Expected     : the value is not created and the message is shown inline on `code` — ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" · en: "This code is already used within this dimension"
Test data    : code "NORTH" under the dimension that already holds it
<!-- TC:TC-FIN-115:END -->

<!-- TC:TC-FIN-116:START traces=AC-FIN-007,REQ-FIN-007,SCR-FIN-003,API-FIN-010 -->
### TC-FIN-116 — create an event-type rule
Derived from : AC-FIN-007 (REQ-FIN-007) · Exercises: SCR-FIN-003 /finance/engine-rules/new · API-FIN-010
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an event type registered in the lookup module with no existing rule; the ACCOUNTING_EVENT_TYPE option list is loaded and non-empty
Steps        : 1. open /finance/engine-rules 2. choose New 3. pick the event type, fill nameAr and nameEn 4. submit
Expected     : the rule is created active and its (empty) line grid opens; the event-type select offered only values the lookup module served
Test data    : an event type with no rule yet
<!-- TC:TC-FIN-116:END -->

<!-- TC:TC-FIN-117:START traces=AC-FIN-008,REQ-FIN-008,SCR-FIN-003,API-FIN-011 -->
### TC-FIN-117 — add a rule line with its three separate references
Derived from : AC-FIN-008 (REQ-FIN-008) · Exercises: SCR-FIN-003 /finance/engine-rules/:id/lines/new · API-FIN-011
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an event-type rule exists and is open
Steps        : 1. open the rule page 2. choose Add line 3. set account derivation type and value, amount source type and value, direction, distribution type 4. submit
Expected     : the line is created and appears in the grid with a server-assigned line number; account derivation, amount source and direction are three separate columns, never one control
Test data    : derivation CONSTANT/"1000", amount source FIELD/"amount", direction DEBIT, distribution FIXED
<!-- TC:TC-FIN-117:END -->

<!-- TC:TC-FIN-118:START traces=AC-FIN-009,REQ-FIN-009,SCR-FIN-003,API-FIN-011 -->
### TC-FIN-118 — percentage lines with no remainder line are refused on screen
Derived from : AC-FIN-009 (REQ-FIN-009) · Exercises: SCR-FIN-003 /finance/engine-rules/:id · API-FIN-011
Rule / code  : RULE-FIN-003 → FIN-409-REMAINDER-COUNT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a rule whose line set holds two PERCENTAGE-distribution lines and no line marked as the remainder
Steps        : 1. open the rule page 2. submit the line set with no remainder marker set
Expected     : nothing is saved and the message is shown on the line grid — ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" · en: "Exactly one remainder line is required when any percentage distribution is present"; the marker is an exclusive choice across the grid, so two markers cannot be set at once
Test data    : two PERCENTAGE lines, zero remainder markers
<!-- TC:TC-FIN-118:END -->

<!-- TC:TC-FIN-119:START traces=AC-FIN-014,REQ-FIN-014,SCR-FIN-006,API-FIN-019 -->
### TC-FIN-119 — post a balanced manual journal entry
Derived from : AC-FIN-014 (REQ-FIN-014) · Exercises: SCR-FIN-006 /finance/journal-entries/new · API-FIN-019
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an open fiscal period inside its fiscal year; at least two leaf, active accounts; signed in holding FIN_JOURNAL_ENTRIES VIEW and CREATE
Steps        : 1. open /finance/journal-entries/new 2. pick the fiscal year, then the period (narrowed to that year), set the document date 3. add two balanced lines with leaf active accounts 4. choose Post
Expected     : the entry posts, opens read-only with its generated document number and posted status, and the journal type submitted was the fixed value MANUAL (no select was offered)
Test data    : two lines, 100.00 DEBIT and 100.00 CREDIT
<!-- TC:TC-FIN-119:END -->

<!-- TC:TC-FIN-120:START traces=AC-FIN-015,REQ-FIN-015,SCR-FIN-006,API-FIN-019 -->
### TC-FIN-120 — every failing check is shown together, and nothing posts
Derived from : AC-FIN-015 (REQ-FIN-015) · Exercises: SCR-FIN-006 /finance/journal-entries/new · API-FIN-019
Rule / code  : RULE-FIN-006, RULE-FIN-007 → FIN-409-UNBALANCED, FIN-409-NOT-POSTABLE-ACCOUNT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a manual entry draft that is both unbalanced and targets a non-leaf account
Steps        : 1. fill the entry so two checks will fail 2. choose Post
Expected     : nothing posts; both refusals are listed together above the entry and each is also routed to the line or field it names; every value the user typed is still in the form
Test data    : debit 100.00 vs credit 99.99, and one line on a rollup account
<!-- TC:TC-FIN-120:END -->

<!-- TC:TC-FIN-121:START traces=AC-FIN-016,REQ-FIN-016,SCR-FIN-006,API-FIN-022 -->
### TC-FIN-121 — a posted entry offers no edit and no delete path
Derived from : AC-FIN-016 (REQ-FIN-016) · Exercises: SCR-FIN-006 /finance/journal-entries/:id · API-FIN-022
Rule / code  : RULE-FIN-016
Scenario     : STATE · data class VALID · language ALL
Preconditions: a POSTED journal entry
Steps        : 1. open /finance/journal-entries/:id 2. look for an edit or delete affordance 3. request /finance/journal-entries/:id/edit directly
Expected     : the entry renders read-only with its lines and their dimensions; no edit and no delete affordance exists anywhere on it, and the edit address matches no route — Reverse is the only action offered
Test data    : a POSTED entry with three lines
<!-- TC:TC-FIN-121:END -->

<!-- TC:TC-FIN-122:START traces=AC-FIN-017,REQ-FIN-017,SCR-FIN-006,API-FIN-019 -->
### TC-FIN-122 — a validated entry shows as posted with its document number
Derived from : AC-FIN-017 (REQ-FIN-017) · Exercises: SCR-FIN-006 /finance/journal-entries/new · API-FIN-019
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a manual entry draft that passes every automatic check
Steps        : 1. choose Post 2. read the header of the returned entry
Expected     : the status shows POSTED (label from the lookup, in the active language), the posted-at timestamp and the document number are populated and read-only; there was no separate approval step between submitting and posting
Test data    : a balanced two-line entry in an open period
<!-- TC:TC-FIN-122:END -->

<!-- TC:TC-FIN-123:START traces=AC-FIN-018,REQ-FIN-018,SCR-FIN-006,API-FIN-019 -->
### TC-FIN-123 — an unbalanced entry is refused with the imbalance visible
Derived from : AC-FIN-018 (REQ-FIN-018) · Exercises: SCR-FIN-006 /finance/journal-entries/new · API-FIN-019
Rule / code  : RULE-FIN-006 → FIN-409-UNBALANCED
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a draft whose debit lines total 100.00 and credit lines 99.99
Steps        : 1. watch the totals bar while typing the second line 2. choose Post
Expected     : the totals bar shows the difference while typing, the Post affordance stays enabled, and the entry is refused — ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" · en: "The entry is unbalanced — total debits do not equal total credits"
Test data    : debit 100.00, credit 99.99
<!-- TC:TC-FIN-123:END -->

<!-- TC:TC-FIN-124:START traces=AC-FIN-019,REQ-FIN-019,SCR-FIN-006,API-FIN-019 -->
### TC-FIN-124 — a line on a non-leaf account is refused and the line is named
Derived from : AC-FIN-019 (REQ-FIN-019) · Exercises: SCR-FIN-006 /finance/journal-entries/new · API-FIN-019
Rule / code  : RULE-FIN-007 → FIN-409-NOT-POSTABLE-ACCOUNT
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a draft with one line targeting a rollup (non-leaf) account; the account picker's leaf+active filter has been bypassed by an account that changed state after the picker loaded
Steps        : 1. submit the entry with that line 2. read where the message lands
Expected     : the entry is refused, the offending line is named, and the message is shown — ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" · en: "The target account does not accept direct posting"
Test data    : one line on a rollup account
<!-- TC:TC-FIN-124:END -->

<!-- TC:TC-FIN-125:START traces=AC-FIN-020,REQ-FIN-020,SCR-FIN-006,API-FIN-019 -->
### TC-FIN-125 — an entry whose period closed while it was being typed is refused
Derived from : AC-FIN-020 (REQ-FIN-020) · Exercises: SCR-FIN-006 /finance/journal-entries/new · API-FIN-019
Rule / code  : RULE-FIN-008 → FIN-409-PERIOD-NOT-OPEN
Scenario     : VIOLATION · data class STATE · language ALL
Preconditions: a period that was Open when the entry form loaded and is Hard Closed by the time Post is pressed
Steps        : 1. build a balanced entry against that period 2. choose Post after the period is closed
Expected     : the entry is refused and the message is routed to the period field — ar: "الفترة المستهدفة غير مفتوحة" · en: "The target period is not open"; the check is at post time, not at build time, so the earlier open state does not save it
Test data    : a period closed between load and submit
<!-- TC:TC-FIN-125:END -->

<!-- TC:TC-FIN-126:START traces=AC-FIN-021,REQ-FIN-021,SCR-FIN-006,API-FIN-019 -->
### TC-FIN-126 — a line citing an inactive dimension value is refused
Derived from : AC-FIN-021 (REQ-FIN-021) · Exercises: SCR-FIN-006 /finance/journal-entries/new · API-FIN-019
Rule / code  : RULE-FIN-009 → FIN-409-INVALID-DIMENSION
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a dimension value that was active when the select loaded and was deactivated before Post
Steps        : 1. add a line and set its dimension and value 2. choose Post after the value is deactivated
Expected     : the entry is refused, the offending line and dimension are named, and the message is shown — ar: "قيمة البُعد غير صالحة" · en: "The dimension value is invalid"
Test data    : one line carrying a since-deactivated dimension value
<!-- TC:TC-FIN-126:END -->

<!-- TC:TC-FIN-127:START traces=AC-FIN-027,REQ-FIN-027,SCR-FIN-006,API-FIN-018 -->
### TC-FIN-127 — search returns exactly the matching entries, unmodified
Derived from : AC-FIN-027 (REQ-FIN-027) · Exercises: SCR-FIN-006 /finance/journal-entries · API-FIN-018
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: entries across several statuses and periods
Steps        : 1. open /finance/journal-entries 2. set the period filter and the status filter 3. page forward once
Expected     : exactly the matching entries are listed and none is altered; the page and page size travel inside the same filter object, so paging forward is a different cache entry of the same key, not independent state
Test data    : entries in two periods across DRAFT-free POSTED statuses
<!-- TC:TC-FIN-127:END -->

<!-- TC:TC-FIN-128:START traces=AC-FIN-028,REQ-FIN-028,SCR-FIN-006,API-FIN-021 -->
### TC-FIN-128 — reverse a posted entry and see both entries linked
Derived from : AC-FIN-028 (REQ-FIN-028) · Exercises: SCR-FIN-006 /finance/journal-entries/:id · API-FIN-021
Rule / code  : RULE-FIN-011
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a POSTED entry with three lines, in an open period; signed in holding the reverse action
Steps        : 1. open the entry 2. choose Reverse 3. confirm the period named in the dialog
Expected     : a new entry opens with the same three amounts and the opposite directions; the original carries a link to the reversal and the reversal a link to the original, and the original is still POSTED
Test data    : a POSTED entry with three lines
<!-- TC:TC-FIN-128:END -->

<!-- TC:TC-FIN-129:START traces=AC-FIN-029,REQ-FIN-029,SCR-FIN-006,API-FIN-021 -->
### TC-FIN-129 — reversing an entry whose period is closed names the current open period first
Derived from : AC-FIN-029 (REQ-FIN-029) · Exercises: SCR-FIN-006 /finance/journal-entries/:id · API-FIN-021
Rule / code  : RULE-FIN-012
Scenario     : STATE · data class VALID · language ALL
Preconditions: a POSTED entry whose own period is now Hard Closed, and a current open period
Steps        : 1. open the entry 2. choose Reverse 3. read the confirmation before accepting 4. confirm
Expected     : the confirmation names the period the reversal will land in before the user commits, and the reversal posts into the current open period, not the closed one
Test data    : an entry in a hard-closed period
<!-- TC:TC-FIN-129:END -->

<!-- TC:TC-FIN-130:START traces=AC-FIN-030,REQ-FIN-030,SCR-FIN-006,API-FIN-021 -->
### TC-FIN-130 — reversing an already-reversed entry is refused
Derived from : AC-FIN-030 (REQ-FIN-030) · Exercises: SCR-FIN-006 /finance/journal-entries/:id · API-FIN-021
Rule / code  : RULE-FIN-013 → FIN-409-ALREADY-REVERSED
Scenario     : VIOLATION · data class STATE · language ALL
Preconditions: an entry already reversed once — it is still POSTED and carries a reversal link
Steps        : 1. open that entry 2. look for the Reverse affordance 3. issue the reverse against a stale row that still shows it
Expected     : the affordance is not drawn on a row that already carries a reversal link; when the row is stale and the action is issued anyway the server refuses and the catalog message is shown; nothing is posted
Test data    : an entry with a reversal link already set
<!-- TC:TC-FIN-130:END -->

<!-- TC:TC-FIN-131:START traces=AC-FIN-022,REQ-FIN-022,SCR-FIN-004,API-FIN-013 -->
### TC-FIN-131 — create a recurring template with its lines in one submission
Derived from : AC-FIN-022 (REQ-FIN-022) · Exercises: SCR-FIN-004 /finance/recurring-templates/new · API-FIN-013
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: signed in holding FIN_RECURRING_TEMPLATES VIEW and CREATE; the schedule-type and frequency option lists are loaded
Steps        : 1. open /finance/recurring-templates/new 2. set schedule type RECURRING — the frequency field appears — and pick a frequency 3. set the start date and add two balanced lines 4. submit
Expected     : the template is created active with its lines in the one submission; the next run date is populated read-only; switching schedule type to REVERSING hides the frequency field rather than disabling it
Test data    : schedule RECURRING, frequency MONTHLY, two lines 50.00 DEBIT / 50.00 CREDIT
<!-- TC:TC-FIN-131:END -->

<!-- TC:TC-FIN-132:START traces=AC-FIN-023,REQ-FIN-023,SCR-FIN-004,API-FIN-014,SCR-FIN-006 -->
### TC-FIN-132 — run a template and reach the entry it posted
Derived from : AC-FIN-023 (REQ-FIN-023) · Exercises: SCR-FIN-004 /finance/recurring-templates/:id · API-FIN-014
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an active recurring template whose next run date is today, and an open period covering it
Steps        : 1. open the template 2. choose Run and confirm 3. follow the offered link to the posted entry
Expected     : one entry is posted from the template, the template's next run date advances per its frequency, and the link opens that entry on SCR-FIN-006 — this screen never renders an entry itself
Test data    : an active template with nextRunDate = today
<!-- TC:TC-FIN-132:END -->

<!-- TC:TC-FIN-133:START traces=AC-FIN-025,REQ-FIN-025,SCR-FIN-005,API-FIN-016 -->
### TC-FIN-133 — create an allocation rule with its targets in one submission
Derived from : AC-FIN-025 (REQ-FIN-025) · Exercises: SCR-FIN-005 /finance/allocation-rules/new · API-FIN-016
Rule / code  : RULE-FIN-003
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a source account; signed in holding FIN_ALLOCATION_RULES VIEW and CREATE
Steps        : 1. open /finance/allocation-rules/new 2. set the names and the source account 3. add two PERCENTAGE targets and one REMAINDER target, marking exactly one remainder 4. submit
Expected     : the rule is created active with its targets; the target grid showed the percentage targets' running sum, and the remainder target's amount cell showed the word remainder rather than a predicted figure
Test data    : two targets at 33%, one remainder target
<!-- TC:TC-FIN-133:END -->

<!-- TC:TC-FIN-134:START traces=AC-FIN-026,REQ-FIN-026,SCR-FIN-005,API-FIN-017,SCR-FIN-006 -->
### TC-FIN-134 — run an allocation rule and reach the distribution entry
Derived from : AC-FIN-026 (REQ-FIN-026) · Exercises: SCR-FIN-005 /finance/allocation-rules/:id · API-FIN-017
Rule / code  : RULE-FIN-010
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an active allocation rule with two PERCENTAGE targets and one REMAINDER target, and a source balance of 1,000.00
Steps        : 1. open the rule 2. choose Run and confirm 3. follow the offered link to the posted entry
Expected     : one entry is posted whose target lines sum exactly to the source balance, the remainder target absorbing the rounding difference; no figure was predicted on screen before the run
Test data    : source balance 1,000.00; targets 33% + 33% + remainder
<!-- TC:TC-FIN-134:END -->

<!-- TC:TC-FIN-135:START traces=AC-FIN-031,REQ-FIN-031,SCR-FIN-007,API-FIN-023 -->
### TC-FIN-135 — create a fiscal year and see its periods generated Open
Derived from : AC-FIN-031 (REQ-FIN-031) · Exercises: SCR-FIN-007 /finance/fiscal-periods/new-year · API-FIN-023
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: signed in holding FIN_PERIODS VIEW and CREATE; the year code is not yet used
Steps        : 1. open /finance/fiscal-periods/new-year 2. fill code, start date, end date and period count 3. submit
Expected     : the year and its periods are created, every period Open, and the periods appear beside the year; the period names and dates are the server's generated values and are read-only
Test data    : code "2026", a whole year, periodCount 12
<!-- TC:TC-FIN-135:END -->

<!-- TC:TC-FIN-136:START traces=AC-FIN-032,REQ-FIN-032,SCR-FIN-007,API-FIN-024 -->
### TC-FIN-136 — reopen a soft-closed period
Derived from : AC-FIN-032 (REQ-FIN-032) · Exercises: SCR-FIN-007 /finance/fiscal-periods/:yearId · API-FIN-024
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a soft-closed period; signed in holding FIN_PERIODS VIEW and UPDATE
Steps        : 1. open the year's period list 2. choose Open on the soft-closed row 3. confirm
Expected     : the row's state becomes Open (label from the lookup, in the active language) and the row now offers Soft-close again
Test data    : a SOFT_CLOSE period
<!-- TC:TC-FIN-136:END -->

<!-- TC:TC-FIN-137:START traces=AC-FIN-033,REQ-FIN-033,SCR-FIN-007,API-FIN-025 -->
### TC-FIN-137 — soft-close a period
Derived from : AC-FIN-033 (REQ-FIN-033) · Exercises: SCR-FIN-007 /finance/fiscal-periods/:yearId · API-FIN-025
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: an Open period; signed in holding FIN_PERIODS VIEW and UPDATE
Steps        : 1. open the year's period list 2. choose Soft-close on the Open row 3. confirm
Expected     : the row's state becomes soft-closed and the row now offers both Open and Hard-close, which are exactly the transitions the lifecycle allows from that state
Test data    : an OPEN period
<!-- TC:TC-FIN-137:END -->

<!-- TC:TC-FIN-138:START traces=AC-FIN-034,REQ-FIN-034,SCR-FIN-007,API-FIN-026 -->
### TC-FIN-138 — hard-close a period, confirming a permanent act
Derived from : AC-FIN-034 (REQ-FIN-034) · Exercises: SCR-FIN-007 /finance/fiscal-periods/:yearId · API-FIN-026
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a soft-closed period; signed in as a caller holding the close-approval action
Steps        : 1. choose Hard-close on the soft-closed row 2. read the confirmation 3. confirm
Expected     : the confirmation states that the close is permanent; the row becomes hard-closed, shows who closed it and when, and offers no Open affordance afterwards
Test data    : a SOFT_CLOSE period
<!-- TC:TC-FIN-138:END -->

<!-- TC:TC-FIN-139:START traces=AC-FIN-035,REQ-FIN-035,SCR-FIN-007,API-FIN-024 -->
### TC-FIN-139 — a hard-closed period offers no reopen path
Derived from : AC-FIN-035 (REQ-FIN-035) · Exercises: SCR-FIN-007 /finance/fiscal-periods/:yearId · API-FIN-024
Rule / code  : RULE-FIN-014 → FIN-409-NOT-REOPENABLE
Scenario     : VIOLATION · data class STATE · language ALL
Preconditions: a Hard Closed period
Steps        : 1. open the year's period list 2. look for an Open affordance on that row 3. issue the open against a stale row that still shows one
Expected     : no Open affordance is drawn on a hard-closed row; when the row is stale and the action is issued anyway the refusal is shown — ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" · en: "The period is hard-closed and cannot be reopened"
Test data    : a HARD_CLOSE period
<!-- TC:TC-FIN-139:END -->

<!-- TC:TC-FIN-140:START traces=AC-FIN-036,REQ-FIN-036,SCR-FIN-007,API-FIN-027,SCR-FIN-006 -->
### TC-FIN-140 — run year-end close and reach both generated entries
Derived from : AC-FIN-036 (REQ-FIN-036) · Exercises: SCR-FIN-007 /finance/fiscal-periods/:yearId · API-FIN-027
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a fiscal year with every period Hard Closed; signed in as a caller holding the close-approval action
Steps        : 1. open the year 2. read the count of periods not yet hard-closed beside the affordance 3. choose Run year-end close and confirm 4. follow the offered links to each returned entry
Expected     : the count reads zero; a global busy indicator is shown while the close runs; a closing entry and the next year's opening entry are returned, each individually balanced, and each opens read-only on SCR-FIN-006
Test data    : a year with 12 hard-closed periods
<!-- TC:TC-FIN-140:END -->

<!-- TC:TC-FIN-141:START traces=AC-FIN-037,REQ-FIN-037,SCR-FIN-007,API-FIN-026 -->
### TC-FIN-141 — the approval is recorded on the row as a distinct act
Derived from : AC-FIN-037 (REQ-FIN-037) · Exercises: SCR-FIN-007 /finance/fiscal-periods/:yearId · API-FIN-026
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a period ready to hard-close, and entries in that period created by a different principal
Steps        : 1. hard-close the period as the approver 2. read the row's closed-by and closed-at
Expected     : the row shows the approving principal and the moment of approval, and that principal is distinct from the creator shown on the entries of the same period
Test data    : an approver distinct from the entry creator
<!-- TC:TC-FIN-141:END -->

<!-- TC:TC-FIN-142:START traces=AC-FIN-038,REQ-FIN-038,SCR-FIN-007,API-FIN-026 -->
### TC-FIN-142 — a caller without the close-approval permission is refused on screen
Derived from : AC-FIN-038 (REQ-FIN-038) · Exercises: SCR-FIN-007 /finance/fiscal-periods/:yearId · API-FIN-026
Rule / code  : RULE-FIN-015 → FIN-403-FORBIDDEN
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: signed in holding only FIN_JOURNAL_ENTRIES create and FIN_PERIODS view — not the close-approval action
Steps        : 1. open the year's period list 2. choose Hard-close on a soft-closed row 3. confirm
Expected     : the affordance renders (the permission is not readable from any published endpoint) and the server denies the act; the localized forbidden message is shown and the row is unchanged — the denial is never a silent no-op
Test data    : a role holding entry-creation but not close-approval
<!-- TC:TC-FIN-142:END -->

<!-- TC:TC-FIN-143:START traces=AC-FIN-039,REQ-FIN-039,SCR-FIN-008,API-FIN-028 -->
### TC-FIN-143 — the account ledger shows a running balance computed live
Derived from : AC-FIN-039 (REQ-FIN-039) · Exercises: SCR-FIN-008 /finance/account-ledger · API-FIN-028
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an account with posted lines across two periods
Steps        : 1. open /finance/account-ledger 2. pick the account and the date range covering both periods 3. read the running balance column and the header totals
Expected     : each row carries the running balance the server computed and the header restates the debit total, credit total and closing balance; the account and range are in the address, so the view is shareable
Test data    : one account, posted lines in two periods
<!-- TC:TC-FIN-143:END -->

<!-- TC:TC-FIN-144:START traces=AC-FIN-040,REQ-FIN-040,SCR-FIN-009,API-FIN-029 -->
### TC-FIN-144 — the trial balance states that it balances
Derived from : AC-FIN-040 (REQ-FIN-040) · Exercises: SCR-FIN-009 /finance/trial-balance · API-FIN-029
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: any set of posted entries in a period
Steps        : 1. open /finance/trial-balance 2. select the period 3. read the banner and the totals
Expected     : total debit balances equal total credit balances exactly, and the banner renders the server's own balanced assertion rather than a comparison the client performed
Test data    : posted entries in one period
<!-- TC:TC-FIN-144:END -->

<!-- TC:TC-FIN-145:START traces=AC-FIN-041,REQ-FIN-041,SCR-FIN-010,API-FIN-030 -->
### TC-FIN-145 — the new year's balance sheet opens on the prior year's closing balances
Derived from : AC-FIN-041 (REQ-FIN-041) · Exercises: SCR-FIN-010 /finance/balance-sheet · API-FIN-030
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a completed year-end close
Steps        : 1. open /finance/balance-sheet 2. select the new fiscal year 3. compare each balance-sheet account against the prior year's closing figure
Expected     : every balance-sheet account's opening balance equals the prior year's closing balance; the sections are the server's account-type groups with their own totals, not a client grouping
Test data    : the year after a completed close
<!-- TC:TC-FIN-145:END -->

<!-- TC:TC-FIN-146:START traces=AC-FIN-042,REQ-FIN-042,SCR-FIN-011,API-FIN-031 -->
### TC-FIN-146 — the new year's income statement opens at zero
Derived from : AC-FIN-042 (REQ-FIN-042) · Exercises: SCR-FIN-011 /finance/income-statement · API-FIN-031
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a completed year-end close and no posting yet in the new year
Steps        : 1. open /finance/income-statement 2. select the new fiscal year 3. read every revenue and expense row
Expected     : every result account shows a zero balance and the screen labels the statement as the correct result for a freshly closed year, not as an empty list
Test data    : the new year before any posting
<!-- TC:TC-FIN-146:END -->

<!-- TC:TC-FIN-147:START traces=AC-FIN-043,REQ-FIN-043,SCR-FIN-012,API-FIN-032 -->
### TC-FIN-147 — a dimension report shows one row per account and dimension value
Derived from : AC-FIN-043 (REQ-FIN-043) · Exercises: SCR-FIN-012 /finance/dimension-reports · API-FIN-032
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: postings to one account under two different values of the same dimension
Steps        : 1. open /finance/dimension-reports 2. select that dimension 3. read the rows for that account
Expected     : two separate rows appear for that account, one per dimension value, never one combined row; the account and the dimension value are two columns of the same row
Test data    : one account, two values of the PROJECT dimension
<!-- TC:TC-FIN-147:END -->

<!-- SUB:UI-FLOWS:END -->

<!-- SUB:INT-FLOW:START traces=AC-FIN-046,REQ-FIN-046,SCR-FIN-010,SCR-FIN-009,SCR-FIN-008,SCR-FIN-006,API-FIN-030,API-FIN-029,API-FIN-028,API-FIN-022 -->
### SUB — INT-FLOW

The one flow that crosses screens: REQ-FIN-046's drill-down chain, which is a property of four screens' links and of no single screen.

<!-- TC:TC-FIN-148:START traces=AC-FIN-046,REQ-FIN-046,SCR-FIN-010,SCR-FIN-009,SCR-FIN-008,SCR-FIN-006,API-FIN-030,API-FIN-029,API-FIN-028,API-FIN-022 -->
### TC-FIN-148 — drill down from a statement line to the originating entry and its source
Derived from : AC-FIN-046 (REQ-FIN-046) · Exercises: SCR-FIN-010 → SCR-FIN-009 → SCR-FIN-008 → SCR-FIN-006 · API-FIN-030, 029, 028, 022
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a balance-sheet line with posted activity behind it, reachable by a caller holding all four screens
Steps        : 1. open /finance/balance-sheet for a fiscal year and choose a statement line 2. follow it to /finance/trial-balance narrowed to that account type 3. follow a row to /finance/account-ledger for that account and range 4. follow a ledger row to /finance/journal-entries/:id 5. read the entry's source
Expected     : each hop lands on the next screen with its filters already in the address, so every step is shareable; the chain ends on the entry's event reference, or on its journal type (manual, recurring, allocation) when the entry is not event-sourced
Test data    : a balance-sheet line whose activity traces to an event-sourced entry
<!-- TC:TC-FIN-148:END -->

<!-- SUB:INT-FLOW:END -->

<!-- PHASE:TEST-PLAN-FE:END -->

## TC TRACEABILITY INDEX

| AC | TC | REQ | SCR | RULE / code |
|---|---|---|---|---|
| AC-FIN-001 | TC-FIN-110 | REQ-FIN-001 | SCR-FIN-001 | — |
| AC-FIN-002 | TC-FIN-111 | REQ-FIN-002 | SCR-FIN-001 | RULE-FIN-001 → FIN-409-PARENT-NOT-LEAF-ELIGIBLE / FIN-409-HAS-CHILDREN |
| AC-FIN-003 | TC-FIN-112 | REQ-FIN-003 | SCR-FIN-001 | — |
| AC-FIN-004 | TC-FIN-113 | REQ-FIN-004 | SCR-FIN-002 | — |
| AC-FIN-005 | TC-FIN-114 | REQ-FIN-005 | SCR-FIN-002 | — |
| AC-FIN-006 | TC-FIN-115 | REQ-FIN-006 | SCR-FIN-002 | RULE-FIN-002 → FIN-409-DIMVALUE-DUP |
| AC-FIN-007 | TC-FIN-116 | REQ-FIN-007 | SCR-FIN-003 | — |
| AC-FIN-008 | TC-FIN-117 | REQ-FIN-008 | SCR-FIN-003 | — |
| AC-FIN-009 | TC-FIN-118 | REQ-FIN-009 | SCR-FIN-003 | RULE-FIN-003 → FIN-409-REMAINDER-COUNT |
| AC-FIN-014 | TC-FIN-119 | REQ-FIN-014 | SCR-FIN-006 | — |
| AC-FIN-015 | TC-FIN-120 | REQ-FIN-015 | SCR-FIN-006 | RULE-FIN-006, RULE-FIN-007 → FIN-409-UNBALANCED, FIN-409-NOT-POSTABLE-ACCOUNT |
| AC-FIN-016 | TC-FIN-121 | REQ-FIN-016 | SCR-FIN-006 | RULE-FIN-016 |
| AC-FIN-017 | TC-FIN-122 | REQ-FIN-017 | SCR-FIN-006 | — |
| AC-FIN-018 | TC-FIN-123 | REQ-FIN-018 | SCR-FIN-006 | RULE-FIN-006 → FIN-409-UNBALANCED |
| AC-FIN-019 | TC-FIN-124 | REQ-FIN-019 | SCR-FIN-006 | RULE-FIN-007 → FIN-409-NOT-POSTABLE-ACCOUNT |
| AC-FIN-020 | TC-FIN-125 | REQ-FIN-020 | SCR-FIN-006 | RULE-FIN-008 → FIN-409-PERIOD-NOT-OPEN |
| AC-FIN-021 | TC-FIN-126 | REQ-FIN-021 | SCR-FIN-006 | RULE-FIN-009 → FIN-409-INVALID-DIMENSION |
| AC-FIN-027 | TC-FIN-127 | REQ-FIN-027 | SCR-FIN-006 | — |
| AC-FIN-028 | TC-FIN-128 | REQ-FIN-028 | SCR-FIN-006 | RULE-FIN-011 |
| AC-FIN-029 | TC-FIN-129 | REQ-FIN-029 | SCR-FIN-006 | RULE-FIN-012 |
| AC-FIN-030 | TC-FIN-130 | REQ-FIN-030 | SCR-FIN-006 | RULE-FIN-013 → FIN-409-ALREADY-REVERSED |
| AC-FIN-022 | TC-FIN-131 | REQ-FIN-022 | SCR-FIN-004 | — |
| AC-FIN-023 | TC-FIN-132 | REQ-FIN-023 | SCR-FIN-004, SCR-FIN-006 | — |
| AC-FIN-025 | TC-FIN-133 | REQ-FIN-025 | SCR-FIN-005 | RULE-FIN-003 |
| AC-FIN-026 | TC-FIN-134 | REQ-FIN-026 | SCR-FIN-005, SCR-FIN-006 | RULE-FIN-010 |
| AC-FIN-031 | TC-FIN-135 | REQ-FIN-031 | SCR-FIN-007 | — |
| AC-FIN-032 | TC-FIN-136 | REQ-FIN-032 | SCR-FIN-007 | — |
| AC-FIN-033 | TC-FIN-137 | REQ-FIN-033 | SCR-FIN-007 | — |
| AC-FIN-034 | TC-FIN-138 | REQ-FIN-034 | SCR-FIN-007 | — |
| AC-FIN-035 | TC-FIN-139 | REQ-FIN-035 | SCR-FIN-007 | RULE-FIN-014 → FIN-409-NOT-REOPENABLE |
| AC-FIN-036 | TC-FIN-140 | REQ-FIN-036 | SCR-FIN-007, SCR-FIN-006 | — |
| AC-FIN-037 | TC-FIN-141 | REQ-FIN-037 | SCR-FIN-007 | — |
| AC-FIN-038 | TC-FIN-142 | REQ-FIN-038 | SCR-FIN-007 | RULE-FIN-015 → FIN-403-FORBIDDEN |
| AC-FIN-039 | TC-FIN-143 | REQ-FIN-039 | SCR-FIN-008 | — |
| AC-FIN-040 | TC-FIN-144 | REQ-FIN-040 | SCR-FIN-009 | — |
| AC-FIN-041 | TC-FIN-145 | REQ-FIN-041 | SCR-FIN-010 | — |
| AC-FIN-042 | TC-FIN-146 | REQ-FIN-042 | SCR-FIN-011 | — |
| AC-FIN-043 | TC-FIN-147 | REQ-FIN-043 | SCR-FIN-012 | — |
| AC-FIN-046 | TC-FIN-148 | REQ-FIN-046 | SCR-FIN-010, SCR-FIN-009, SCR-FIN-008, SCR-FIN-006 | — |

### AC covered on the backend track only — not a gap on this track

These acceptance criteria have no screen to exercise them: each is either a server-to-server
path or a deployment act, and the SRS traceability matrix maps the last two to
"— (onboarding, no screen)". Each is covered by its 1:1 test case in
`backend-test-plan-fin.md`.

| AC | REQ | Why no frontend case |
|---|---|---|
| AC-FIN-010 | REQ-FIN-010 | the engine builds the entry from an arriving event — API-FIN-020 is a host system's call and is drawn on no screen (ADR-FIN-007) |
| AC-FIN-011 | REQ-FIN-011 | duplicate event reference — refused to the calling system, not to a screen |
| AC-FIN-012 | REQ-FIN-012 | the remainder line's rounding arithmetic — computed server-side during the build |
| AC-FIN-013 | REQ-FIN-013 | an event type with no active rule — answered to the calling system; the SRS declares no failure-queue entity for a screen to show |
| AC-FIN-024 | REQ-FIN-024 | the automatic next-period reversal of a reversing template — posted server-side, with no user action to exercise |
| AC-FIN-044 | REQ-FIN-044 | onboarding: FIN registers its module, screens and actions into the security module (no screen — SRS traceability matrix) |
| AC-FIN-045 | REQ-FIN-045 | onboarding: FIN registers its 13 lookup types into the lookup module (no screen — SRS traceability matrix) |

## COVERAGE

AC covered on this track: 39/46 — the seven above are backend-only by construction, and
46/46 across the module when both plans are read together (`backend-test-plan-fin.md` carries
one TC per AC for all 46).
REQ covered on this track: 39/46 — the same seven REQ ids, for the same reason.
SCR covered: 12/12 — every `SCR-FIN-001..012` is exercised by at least one case:
SCR-FIN-001 (3), SCR-FIN-002 (3), SCR-FIN-003 (3), SCR-FIN-004 (2), SCR-FIN-005 (2),
SCR-FIN-006 (12), SCR-FIN-007 (8), SCR-FIN-008 (2), SCR-FIN-009 (2), SCR-FIN-010 (2),
SCR-FIN-011 (2), SCR-FIN-012 (1) — the drill-down case counts on four of them.
UXD covered: not derived in this run — `INT-UXD` is an integration phase and this run is
`--module FIN`; the twelve `UXD-FIN-*` all name an owner module outside the selection.
TC count check (§3 over-engineering guard): 39 cases against 46 ACs is well under 2×, and no
case is a fabricated variant — every one derives from a distinct AC.
Scenario mix: HAPPY 20 · VIOLATION 9 · STATE 9 · PERMISSION 1 · BOUNDARY 0 (no AC or RULE in
FIN's set states a numeric limit, so §3 rule 3 adds none).

## NOTES

- Every message asserted above is copied character-perfect from `srs-fin.md` §A5 in both
  languages; no message is reworded and none is composed by a test.
- No test data is invented beyond the values the ACs themselves name (100.00 / 99.99,
  1,000.00 with 33% + 33% + remainder, the "NORTH" duplicate code).
- Three screen behaviours asserted here follow a recorded decision rather than a `RULE-*`, and
  each case says so where it matters: the report screens' single route (ADR-FIN-003), the
  absent Edit affordance on templates and allocation rules (ADR-FIN-006), and the fixed
  `MANUAL` journal type on the entry form (ADR-FIN-008).
- `test-execution-manifest-fin.md` is a derived view of the **backend** plan and its API set.
  Neither changed in this run, so it is current and is not rewritten.
══════════════════════════════════════════════════════════════════
