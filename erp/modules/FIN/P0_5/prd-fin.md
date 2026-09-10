# PRD — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module          : FIN     Version : v1
Source artifacts: platform-summary, module-registry, business-policies
Stories         : 19   Policies covered : 20/20   Deferred : 0
Status          : DRAFT — awaiting prd-approval
══════════════════════════════════════════════════════════════════

## USER STORIES

US-FIN-001
  Title          : شجرة الحسابات / Chart of accounts
  Story          : As a finance administrator, I need a hierarchical chart of accounts where only leaf accounts accept direct posting, so that the account structure enforces its own integrity.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-002, POL-FIN-003
  Source         : general-accounting-system-plan-en.md §4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-002
  Title          : تعريف الأبعاد وقيمها / Define dimensions and their values
  Story          : As a finance administrator, I need to define dimensions and their values as data, so that account combinations can carry any segment (project, department, investor, ...) without code changes.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-011
  Source         : general-accounting-system-plan-en.md §4.2-§4.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-003
  Title          : إعداد محرك القواعد / Configure the rules engine
  Story          : As a finance administrator, I need to map each event type to a set of lines (account derivation, amount source, direction), so that new event types are added as data, never as code.
  Priority       : HIGH — plan names this "the core" (§6.1)
  Success metric : —
  Traces         : POL-FIN-005, POL-FIN-006, POL-FIN-014
  Source         : general-accounting-system-plan-en.md §6
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-004
  Title          : إنشاء قيد من حدث محاسبي / Build an entry from an accounting event
  Story          : As the accounting engine, I need to build a balanced entry from an incoming canonical event using its rule, so that event-sourced postings need no manual entry.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-001, POL-FIN-012, POL-FIN-014, POL-FIN-020
  Source         : general-accounting-system-plan-en.md §7.1
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-005
  Title          : إدخال يدوي / Manual journal entry
  Story          : As an accountant, I need to create a manual journal entry (adjustments, opening entries), so that postings with no source event follow the same validation and posting path.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-001, POL-FIN-018
  Source         : general-accounting-system-plan-en.md §7.2
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-006
  Title          : قوالب متكررة/عكسية / Recurring / reversing templates
  Story          : As an accountant, I need a template that recurs on a schedule or auto-reverses next period, so that I don't rebuild the same accrual entry by hand every period.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-018
  Source         : general-accounting-system-plan-en.md §7.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-007
  Title          : قواعد التوزيع / Allocation rules
  Story          : As an accountant, I need to distribute an accumulated account balance across several accounts or dimensions by data-defined rules, so that periodic allocations don't require manual, error-prone entries.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-006
  Source         : general-accounting-system-plan-en.md §7.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-008
  Title          : عرض قيود اليومية / View journal entries
  Story          : As an accountant, I need to view and search journal entries with their full status detail, so that I can review what has posted without altering it.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-013
  Source         : general-accounting-system-plan-en.md §8.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-009
  Title          : عكس/تصحيح قيد / Reverse / correct an entry
  Story          : As an accountant, I need to reverse a posted entry with one action, so that a mistake is corrected without ever editing or deleting the original.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-007
  Source         : general-accounting-system-plan-en.md §9
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-010
  Title          : إدارة السنوات والفترات المالية / Manage fiscal years and periods
  Story          : As a finance administrator, I need to open, soft-close and hard-close periods and run year-end close, so that the accounting calendar is fully under this module's own control.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-004, POL-FIN-010
  Source         : general-accounting-system-plan-en.md §10
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-011
  Title          : اعتماد إغلاق الفترة / Approve period close
  Story          : As a financial controller (distinct from any entry creator), I need to be the one who approves closing a period, so that the single human control point in the whole posting lifecycle is genuinely independent.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-016, POL-FIN-019
  Source         : general-accounting-system-plan-en.md §8.2, §10.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-012
  Title          : دفتر الحساب / Account ledger
  Story          : As an accountant, I need an account ledger derived live from posted lines, so that I always see a figure that matches reality, never a stale cached one.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-009, POL-FIN-011
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-013
  Title          : ميزان المراجعة / Trial balance
  Story          : As a financial controller, I need a trial balance that always balances by construction, so that I trust it as a control report, not just a listing.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-008, POL-FIN-009
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-014
  Title          : الميزانية العمومية / Balance sheet
  Story          : As a financial controller, I need a balance sheet derived from posted balances with correct opening-balance continuity, so that year-over-year figures are trustworthy.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-002, POL-FIN-010
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-015
  Title          : قائمة الدخل / Income statement
  Story          : As a financial controller, I need an income statement derived from posted balances that opens at zero every new year, so that period results are never contaminated by a prior year.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-002, POL-FIN-010
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-016
  Title          : تقارير الأبعاد / Dimension reports
  Story          : As a financial controller, I need reports broken down by dimension without duplicating accounts, so that I can analyze results per project/department/investor without a parallel chart of accounts.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-011
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-017
  Title          : تسجيل FIN في وحدة الأمان / Register FIN into the Security module
  Story          : As FIN's own integrator, I need to register FIN's module, screens and actions into the Security module as data, so that FIN owns no security of its own.
  Priority       : HIGH — foundational, blocks every secured screen below
  Success metric : —
  Traces         : POL-FIN-015
  Source         : general-accounting-system-plan-en.md §2.2, §2.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-018
  Title          : تسجيل قوائم FIN المرجعية في MDL / Register FIN's lookup types into the Lookup module
  Story          : As FIN's own integrator, I need to register FIN's lookup types (payment methods, event types, account types, period states, journal types, ...) into the Lookup module as data, so that FIN keeps no lookup table of its own.
  Priority       : HIGH — foundational, blocks account/period/entry creation which cite these codes
  Success metric : —
  Traces         : POL-FIN-017
  Source         : general-accounting-system-plan-en.md §5.2, §5.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-019
  Title          : التتبع النازل من التقرير إلى الحدث / Drill-down from statement to source event
  Story          : As a financial controller, I need to drill down from a financial-statement line through the trial balance and account ledger to the original entry and its source event, so that any figure is explainable to its root cause.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-013
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

## TRACEABILITY — story → policy
| US | Traces (POL) | Source |
|---|---|---|
| US-FIN-001 | POL-FIN-002, POL-FIN-003 | §4 |
| US-FIN-002 | POL-FIN-011 | §4.2-§4.3 |
| US-FIN-003 | POL-FIN-005, POL-FIN-006, POL-FIN-014 | §6 |
| US-FIN-004 | POL-FIN-001, POL-FIN-012, POL-FIN-014, POL-FIN-020 | §7.1 |
| US-FIN-005 | POL-FIN-001, POL-FIN-018 | §7.2 |
| US-FIN-006 | POL-FIN-018 | §7.3 |
| US-FIN-007 | POL-FIN-006 | §7.4 |
| US-FIN-008 | POL-FIN-013 | §8.4 |
| US-FIN-009 | POL-FIN-007 | §9 |
| US-FIN-010 | POL-FIN-004, POL-FIN-010 | §10 |
| US-FIN-011 | POL-FIN-016, POL-FIN-019 | §8.2, §10.3 |
| US-FIN-012 | POL-FIN-009, POL-FIN-011 | §11 |
| US-FIN-013 | POL-FIN-008, POL-FIN-009 | §11 |
| US-FIN-014 | POL-FIN-002, POL-FIN-010 | §11 |
| US-FIN-015 | POL-FIN-002, POL-FIN-010 | §11 |
| US-FIN-016 | POL-FIN-011 | §11 |
| US-FIN-017 | POL-FIN-015 | §2.2, §2.4 |
| US-FIN-018 | POL-FIN-017 | §5.2-§5.3 |
| US-FIN-019 | POL-FIN-013 | §11 |
Every policy POL-FIN-001 … POL-FIN-020 appears in at least one row above.

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |
None — general-accounting-system-plan-en.md left no story's scope, priority or role
genuinely ambiguous; no dialogue question was required.

## DEFERRED
| US | Reason | Activation trigger |
None — every capability named in general-accounting-system-plan-en.md's in-scope sections
is represented by a story in this v1 PRD; the explicit exclusions (§15) are recorded as
SCOPE EXCEPTIONS in business-policies-fin.md, not as deferred stories.

## APPROVAL
Approved by : PENDING   Date : PENDING
Once approved, no stage may raise a question; P1 onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════
