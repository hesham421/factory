## MODULE REGISTRY — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module Code    : FIN   (profile.vocabulary.module_prefixes)
Bounded context: finance
Layer / Type   : L3 / transactional + reporting     Execution tier : 2.2
Source         : NEW
Knowledge      : new project/general-accounting-system-plan-en.md (incl. §12 "details the
                  analysis agent MUST honor"); profiles/erp/knowledge/erp-domain-standards.md
Readiness      : READY
══════════════════════════════════════════════════════════════════

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar/en) | Kind | PRIVATE / SHARED | Source |
|---|---|---|---|
| الحساب / Account | master | PRIVATE | general-accounting-system-plan-en.md §4 |
| البُعد / Dimension | config | PRIVATE | §4.2 |
| قيمة البُعد / DimensionValue | lookup | PRIVATE | §4.2 |
| رأس قيد اليومية / JournalEntry | transactional | PRIVATE | §7, §8 |
| سطر قيد اليومية / JournalLine | transactional | PRIVATE | §7, §8 |
| بُعد سطر القيد / JournalLineDimension | transactional | PRIVATE | §4.3 (posting combination) |
| السنة المالية / FiscalYear | master | PRIVATE | §10 |
| الفترة المحاسبية / FiscalPeriod | master | PRIVATE | §10 |
| قاعدة نوع الحدث / EventTypeRule | config | PRIVATE | §6 |
| سطر القاعدة / RuleLine | config | PRIVATE | §6.2 |
| قالب متكرر/عكسي / RecurringTemplate | config | PRIVATE | §7.3 |
| سطر القالب المتكرر / RecurringTemplateLine | config | PRIVATE | §7.3 |
| قاعدة توزيع / AllocationRule | config | PRIVATE | §7.4 |
| هدف التوزيع / AllocationTarget | config | PRIVATE | §7.4 |

LOOKUPS OWNED    (value lists this module masters — registered into MDL, not stored locally)
| Lookup key | Description | Initial values (only those the user named) | Source |
|---|---|---|---|
| ACCOUNT_TYPE | نوع الحساب / account type | ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE — named by the plan | general-accounting-system-plan-en.md §4.2 |
| DEBIT_CREDIT | طبيعة/اتجاه / nature & posting direction | DEBIT, CREDIT — named by the plan | §4.2, §6.2(c) |
| PERIOD_STATE | حالة الفترة / period state | OPEN, SOFT_CLOSE, HARD_CLOSE, YEAR_END_CLOSE — named by the plan | §10.2 |
| ACCOUNTING_EVENT_TYPE | نوع الحدث المحاسبي / accounting event type | None named — host-specific, added as data per host [§3, §6.4] | §5.2, §6.4 |
| PAYMENT_METHOD | طريقة الدفع / payment method | None named | §5.2 |
| JOURNAL_TYPE | نوع اليومية / journal type | EVENT_GENERATED, MANUAL, RECURRING, ALLOCATION, REVERSAL — named by the plan §7 (journal sources) + §9 (reversal) | §5.2, §7 |
| FISCAL_YEAR_STATUS | حالة السنة المالية / fiscal year status | OPEN, CLOSED | AUTO (see AUTO-DECISIONS) |
| JOURNAL_STATUS | حالة القيد / journal entry status | DRAFT, POSTED, VOID | AUTO — §8.1 lifecycle |
| ACCOUNT_DERIVATION_TYPE | نوع اشتقاق الحساب / account derivation type | CONSTANT, DIRECT, MAPPING | AUTO — §6.2(a) |
| AMOUNT_SOURCE_TYPE | نوع مصدر المبلغ / amount source type | FIELD, PERCENTAGE, REMAINDER | AUTO — §6.2(b) |
| DISTRIBUTION_TYPE | نوع التوزيع / distribution type | FIXED, PERCENTAGE, REMAINDER | AUTO — §6.3, reused by AllocationRule (§7.4) |
| RECURRING_SCHEDULE_TYPE | نوع الجدولة / recurring schedule type | RECURRING, REVERSING | AUTO — §7.3 |
| RECURRING_FREQUENCY | تكرار الجدولة / recurring frequency | MONTHLY, QUARTERLY, ANNUALLY, WEEKLY | AUTO — §7.3 |
Rule (profile): all LOV values runtime-loaded from the lookup module; no hardcoded enums in APIs or field specs

LOOKUPS CONSUMED (from other modules)
| Lookup key | Owner code | READ-ONLY |
None beyond FIN's own (FIN owns and reads all lookup keys named above; it consumes no
other module's domain-specific list).

SHARED ENTITIES CONSUMED
| Entity | Owner code | HARD-FK / SOFT-READ | Why |
|---|---|---|---|
| User (identity) | SEC | HARD-FK (createdBy/updatedBy principal reference — same non-FK "principal string" pattern SEC itself uses; see AUTO-DECISIONS) | audit trail |
| ModuleRegistry, ScreenRegistry, ActionRegistry | SEC | HARD-FK (registration as data) | FIN registers itself, its screens and actions into SEC |
| LookupType, LookupValue | MDL | HARD-FK (registration + read) | FIN registers all 13 lookup keys above into MDL and reads their values at runtime |

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
|---|---|---|
| SEC | HARD | identity, module/screen/action grants, SoD (entry-creator ≠ period-close approver) |
| MDL | HARD | all 13 lookup keys above (registration + runtime read) |
External (not registry modules): Notifications (ready, SOFT, optional — period-close-awaiting
notice); File Service (ready, SOFT, optional — statement export) [general-accounting-system-plan-en.md §2.3].
ROOT: NO

AUTO-DECISIONS
AUTO: audit columns (createdBy/updatedBy) store a principal string, not a numeric FK to SEC's User table
  FROM: SEC's own db-script §3 AUDIT COLUMNS rule ("user columns hold a principal string, not a numeric FK"), applied identically here for consistency across every module
  IF WRONG: none recommended — matches the platform-wide convention already set by the first module through this pipeline.
AUTO: added FISCAL_YEAR_STATUS, JOURNAL_STATUS, ACCOUNT_DERIVATION_TYPE, AMOUNT_SOURCE_TYPE, DISTRIBUTION_TYPE, RECURRING_SCHEDULE_TYPE, RECURRING_FREQUENCY as FIN-owned lookup types beyond the plan's explicitly named five (ACCOUNT_TYPE, DEBIT_CREDIT, PERIOD_STATE, ACCOUNTING_EVENT_TYPE, PAYMENT_METHOD, JOURNAL_TYPE)
  FROM: profiles/erp.yaml conventions.lookups ("no hardcoded enums") applied to the structural mechanisms §6.2/§6.3/§7.3/§8.1 explicitly describe — every closed value set the plan text names, even informally, becomes a real lookup, never an in-code enum
  IF WRONG: fold a narrow-scope one (e.g. RECURRING_FREQUENCY) into a plain CHECK constraint if the client considers it too granular for central governance — non-breaking, revise this module registry.
AUTO: Dimension/DimensionValue modeled as FIN-owned entities (config/lookup kind), not as MDL lookup types
  FROM: general-accounting-system-plan-en.md §4.3 gives dimensions their own dedicated screen ("Dimension definition & values screen") distinct from the generic Lookups screen, and dimensions are posting-identity structure (§12 point 11), not a simple coded reference list — a categorical difference from an ordinary lookup
  IF WRONG: migrate to MDL as lookup types if the client wants dimensions managed through the same generic screen as everything else — would need its own ADR (changes the posting-identity architecture, likely breaking).
AUTO: reversal modeled as a self-referencing link on JournalEntry (originalEntryId / reversalEntryId), not a separate entity
  FROM: general-accounting-system-plan-en.md §9 — "a new VOID/CORRECTION entry... linked by reference to the original" describes a link, not a distinct record type
  IF WRONG: none recommended — a separate entity would only duplicate JournalEntry's own shape.

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
None — general-accounting-system-plan-en.md fully settles this module's P0 scope; no point
required dialogue.

POLICIES OWNED (full text in business-policies-fin.md)
POL-FIN-001, POL-FIN-002, POL-FIN-003, POL-FIN-004, POL-FIN-005, POL-FIN-006, POL-FIN-007,
POL-FIN-008, POL-FIN-009, POL-FIN-010, POL-FIN-011, POL-FIN-012, POL-FIN-013, POL-FIN-014,
POL-FIN-015, POL-FIN-016, POL-FIN-017, POL-FIN-018, POL-FIN-019, POL-FIN-020
══════════════════════════════════════════════════════════════════
