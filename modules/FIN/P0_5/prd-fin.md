<!-- P0.5 stage output — governed by factory.yaml stages[P0.5]; see shared/GOVERNANCE-CORE.md -->
# PRD — Finance / المحاسبة والمالية (FIN)
══════════════════════════════════════════════════════════════════
Module          : FIN     Version : v1
Source artifacts: platform-summary, module-registry-fin, business-policies-fin
Stories         : 17   Policies covered : 10/10   Deferred : 0
Status          : DRAFT — awaiting prd-approval
══════════════════════════════════════════════════════════════════

## EXTRACTION REPORT
══════════════════════════════════════════════════════════════════
PRD EXTRACTION REPORT — FIN — 2026-09-10
══════════════════════════════════════════════════════════════════
STORIES DRAFTED
  + US-FIN-001 — Chart of accounts management — Traces: POL-FIN-001, POL-FIN-003 — Source: plan §1
  + US-FIN-002 — Dimension definition as data — Traces: POL-FIN-001 — Source: plan §1.2, §1.3
  + US-FIN-003 — Reference-data (Lookups) management — Traces: POL-FIN-003 — Source: plan §2
  + US-FIN-004 — Rules-engine configuration — Traces: POL-FIN-002 — Source: plan §3
  + US-FIN-005 — Automatic posting from events — Traces: POL-FIN-002, POL-FIN-004 — Source: plan §4.1
  + US-FIN-006 — Direct manual entries — Traces: POL-FIN-004 — Source: plan §4.2
  + US-FIN-007 — Recurring / reversing templates — Traces: POL-FIN-004 — Source: plan §4.3
  + US-FIN-008 — Allocation entries — Traces: POL-FIN-004 — Source: plan §4.4
  + US-FIN-009 — Immediate posting, no per-entry approval — Traces: POL-FIN-004 — Source: plan §5.1, §5.2
  + US-FIN-010 — Period-close approval with SoD — Traces: POL-FIN-005, POL-FIN-006 — Source: plan §5.2, §7.3, §8.2
  + US-FIN-011 — Reverse a posted entry — Traces: POL-FIN-007 — Source: plan §6
  + US-FIN-012 — Independent accounting-only login and roles — Traces: POL-FIN-008 — Source: plan §8
  + US-FIN-013 — Fiscal period/year lifecycle management — Traces: POL-FIN-005, POL-FIN-010 — Source: plan §7.1–§7.3
  + US-FIN-014 — Automatic year-end carryforward — Traces: POL-FIN-010 — Source: plan §7.4
  + US-FIN-015 — Ledger, trial balance and financial statements — Traces: POL-FIN-009 — Source: plan §9.1, §9.2
  + US-FIN-016 — Dimension-based reporting — Traces: POL-FIN-001, POL-FIN-009 — Source: plan §9.2
  + US-FIN-017 — Drill-down audit trail — Traces: — (scope only) — Source: plan §9.3
STORIES SKIPPED (no traceable source)
  — "Account balance maintenance screen" — considered, rejected: POL-FIN-009 explicitly forbids a manually accumulated balance column; balances are read-only/derived, so no such story exists.
QUESTIONS RAISED → RESOLVED IN DIALOGUE
  — None raised at this stage. The one structural open point (FIN's total isolation from ORG/SEC/MDL) was already raised and resolved in dialogue at P0 (platform-summary Resolved Decision #1); P0.5 does not reopen it, per §5 "never re-open a P0 STEERING/resolved decision" — it is only carried forward below for the user's explicit confirmation at this gate.
POLICIES WITHOUT A STORY (must be empty)
  — (none)
══════════════════════════════════════════════════════════════════

## USER STORIES

US-FIN-001
  Title          : شجرة الحسابات / Chart of accounts management
  Story          : As an Accounting Configuration Administrator (مسؤول إعداد النظام المحاسبي), I need to manage a hierarchical chart of accounts where the account combination is base account + dimensions, so that postings can always be directed to the correct account/dimension combination.
  Priority       : HIGH — the reference structure everything else posts against
  Success metric : —
  Traces         : POL-FIN-001, POL-FIN-003
  Source         : plan §1
  Status         : DRAFT

US-FIN-002
  Title          : تعريف الأبعاد / Dimension definition as data
  Story          : As an Accounting Configuration Administrator, I need to add, remove or change an account dimension (e.g. investor, project, cost center) as configuration, so that the module fits a new host system without a code change.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-001
  Source         : plan §1.2, §1.3
  Status         : DRAFT

US-FIN-003
  Title          : البيانات المرجعية / Reference-data (Lookups) management
  Story          : As an Accounting Configuration Administrator, I need one generic screen to manage every accounting reference list (payment methods, event types, account types, period states, journal types), so that FIN never depends on another module's reference tables.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-003
  Source         : plan §2
  Status         : DRAFT

US-FIN-004
  Title          : إعداد محرك القواعد / Rules-engine configuration
  Story          : As an Accounting Configuration Administrator, I need to define, per event type, how it becomes a journal entry (account derivation, amount source, direction, distribution), so that onboarding a new event type or a new host system is a data change, not code.
  Priority       : HIGH — the core of the module
  Success metric : —
  Traces         : POL-FIN-002
  Source         : plan §3
  Status         : DRAFT

US-FIN-005
  Title          : الترحيل التلقائي من الأحداث / Automatic posting from events
  Story          : As an Accountant (محاسب), I need an incoming canonical accounting event to become a validated, balanced journal entry automatically, so that routine transactions never need re-keying.
  Priority       : HIGH — the primary journal source
  Success metric : —
  Traces         : POL-FIN-002, POL-FIN-004
  Source         : plan §4.1
  Status         : DRAFT

US-FIN-006
  Title          : القيد اليدوي المباشر / Direct manual entries
  Story          : As an Accountant, I need to enter an adjustment or opening entry directly, so that transactions with no source event are still captured, through the same validation as any other entry.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-004
  Source         : plan §4.2
  Status         : DRAFT

US-FIN-007
  Title          : القيود المتكررة / العكسية / Recurring / reversing templates
  Story          : As an Accountant, I need to define an entry template that recurs on a schedule or auto-reverses next period, so that routine or accrual entries don't need to be rebuilt every period.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-004
  Source         : plan §4.3
  Status         : DRAFT

US-FIN-008
  Title          : قيود التوزيع / Allocation entries
  Story          : As an Accountant, I need to distribute an accumulated balance across several accounts/dimensions by data-defined rules, so that shared costs or revenues are apportioned consistently.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-004
  Source         : plan §4.4
  Status         : DRAFT

US-FIN-009
  Title          : الترحيل الفوري دون موافقة لكل قيد / Immediate posting, no per-entry approval
  Story          : As an Accountant, I need a validated entry (from any source) to post immediately, so that my work is never held up waiting for individual sign-off.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-004
  Source         : plan §5.1, §5.2
  Status         : DRAFT

US-FIN-010
  Title          : اعتماد إقفال الفترة مع فصل المهام / Period-close approval with SoD
  Story          : As a Financial Controller (المراقب المالي), I need to review and approve the close of a fiscal period myself — never as the same person who created its entries — so that the period's content is checked by someone independent before it becomes final.
  Priority       : HIGH — the platform's one human control point
  Success metric : —
  Traces         : POL-FIN-005, POL-FIN-006
  Source         : plan §5.2, §7.3, §8.2
  Status         : DRAFT

US-FIN-011
  Title          : عكس قيد مرحّل / Reverse a posted entry
  Story          : As an Accountant, I need to reverse a posted entry with one action that creates a linked, traceable correction, so that mistakes are fixed without ever editing or deleting history.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-007
  Source         : plan §6
  Status         : DRAFT

US-FIN-012
  Title          : دخول وصلاحيات محاسبية مستقلة / Independent accounting-only login and roles
  Story          : As an Accounting System Administrator (مسؤول أمان النظام المحاسبي), I need to manage FIN's own users, roles and permissions independently of any other module, so that accounting access is controlled entirely within accounting.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-008
  Source         : plan §8
  Status         : DRAFT

US-FIN-013
  Title          : دورة حياة الفترة والسنة المالية / Fiscal period/year lifecycle management
  Story          : As a Financial Controller, I need to open, soft-close, hard-close and year-end-close fiscal periods and years, so that posting is always confined to the correct, controlled window.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-005, POL-FIN-010
  Source         : plan §7.1–§7.3
  Status         : DRAFT

US-FIN-014
  Title          : الترحيل التلقائي لأول المدة / Automatic year-end carryforward
  Story          : As a Financial Controller, I need the new year's opening entry generated automatically from the prior year's closing balances, so that year-end close never requires manual re-entry of opening balances.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-010
  Source         : plan §7.4
  Status         : DRAFT

US-FIN-015
  Title          : كشف الحساب وميزان المراجعة والقوائم المالية / Ledger, trial balance and financial statements
  Story          : As an Accountant or Financial Controller, I need the account ledger, trial balance, balance sheet and income statement all derived from posted entries only, so that reporting can never disagree with the ledger.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-009
  Source         : plan §9.1, §9.2
  Status         : DRAFT

US-FIN-016
  Title          : التقارير حسب البُعد / Dimension-based reporting
  Story          : As a Financial Controller, I need a statement per dimension value (e.g. per investor) without duplicating accounts, so that dimension-level results are visible without account-tree bloat.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-001, POL-FIN-009
  Source         : plan §9.2
  Status         : DRAFT

US-FIN-017
  Title          : مسار التدقيق التفصيلي / Drill-down audit trail
  Story          : As an Auditor (مدقق), I need to go from a financial-statement line down to the trial balance, the account ledger, the original entry and its source-event reference, so that every reported number can be traced back to its origin.
  Priority       : MEDIUM
  Success metric : —
  Traces         : — (scope only — plan §9.3, module-registry entity list)
  Source         : plan §9.3
  Status         : DRAFT

## TRACEABILITY — story → policy
| US | Traces (POL) | Source |
|---|---|---|
| US-FIN-001 | POL-FIN-001, POL-FIN-003 | plan §1 |
| US-FIN-002 | POL-FIN-001 | plan §1.2, §1.3 |
| US-FIN-003 | POL-FIN-003 | plan §2 |
| US-FIN-004 | POL-FIN-002 | plan §3 |
| US-FIN-005 | POL-FIN-002, POL-FIN-004 | plan §4.1 |
| US-FIN-006 | POL-FIN-004 | plan §4.2 |
| US-FIN-007 | POL-FIN-004 | plan §4.3 |
| US-FIN-008 | POL-FIN-004 | plan §4.4 |
| US-FIN-009 | POL-FIN-004 | plan §5.1, §5.2 |
| US-FIN-010 | POL-FIN-005, POL-FIN-006 | plan §5.2, §7.3, §8.2 |
| US-FIN-011 | POL-FIN-007 | plan §6 |
| US-FIN-012 | POL-FIN-008 | plan §8 |
| US-FIN-013 | POL-FIN-005, POL-FIN-010 | plan §7.1–§7.3 |
| US-FIN-014 | POL-FIN-010 | plan §7.4 |
| US-FIN-015 | POL-FIN-009 | plan §9.1, §9.2 |
| US-FIN-016 | POL-FIN-001, POL-FIN-009 | plan §9.2 |
| US-FIN-017 | — (scope only) | plan §9.3 |

Every policy (POL-FIN-001 … POL-FIN-010) appears in at least one row above.

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Carried from P0: should FIN stay fully isolated from `ORG`/`SEC`/`MDL` (dedicated lookups + independent RBAC, US-FIN-003 and US-FIN-012), or fall back to the platform-shared default? | Keep the isolated design — it is what the vision document explicitly and repeatedly specifies, and it is now the basis of two user stories | **Requires explicit confirmation at this gate** — approving this PRD as written accepts the isolated design; reject or amend to fall back to the shared platform default instead | platform-summary Resolved Decision #1; module-registry-fin Resolved Decision #1; plan §2.1, §8.1 |

## DEFERRED
| US | Reason | Activation trigger |
|---|---|---|
| (none) | All scope exclusions (multi-currency, multi-ledger/entity, intercompany, statistical accounts, multi-pattern calendar, attachments) are recorded as SCOPE EXCEPTIONS in `business-policies-fin.md`, not as deferred stories — no user story was drafted for them to defer. | — |

## APPROVAL
Approved by : —   Date : —
Once approved, no stage may raise a question; P1 onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════
