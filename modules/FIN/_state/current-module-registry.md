<!-- P0 stage output — governed by factory.yaml stages[P0]; see shared/GOVERNANCE-CORE.md -->
## MODULE REGISTRY — Finance / المحاسبة والمالية (FIN)
══════════════════════════════════════════════════════════════════
Module Code    : FIN   (profile.vocabulary.module_prefixes)
Bounded context: finance
Layer / Type   : L2 / engine          Execution tier : 2.2
Source         : NEW
Knowledge      : `profiles/erp/knowledge/erp-domain-standards.md` §1, §3, §5 ·
                  FIN vision document `general-accounting-system-plan-en.md` (all sections)
Readiness      : READY
══════════════════════════════════════════════════════════════════

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar / en) | Kind | PRIVATE / SHARED | Source |
|---|---|---|---|
| شجرة الحسابات / Chart of Account | master | PRIVATE | plan §1 |
| بُعد الحساب / Account Dimension (definition + values) | config | PRIVATE | plan §1.2, §1.3 |
| البيانات المرجعية المحاسبية / Accounting Reference List (lookup type + values) | lookup | PRIVATE | plan §2 |
| قاعدة نوع الحدث / Event-Type Rule | config | PRIVATE | plan §3 |
| سطر القاعدة / Rule Line (account / amount / direction / distribution derivation) | config | PRIVATE | plan §3.2, §3.3 |
| القيد المحاسبي / Journal Entry | transactional | PRIVATE | plan §4, §5 |
| سطر القيد / Journal Entry Line | transactional | PRIVATE | plan §4, §5 |
| قالب القيد المتكرر / العكسي / Recurring-Reversing Entry Template | config | PRIVATE | plan §4.3 |
| قاعدة التوزيع / Allocation Rule | config | PRIVATE | plan §4.4 |
| السنة المالية / Fiscal Year | master | PRIVATE | plan §7 |
| الفترة المالية / Fiscal Period | master | PRIVATE | plan §7 |
| مستخدم المحاسبة / Accounting User | security | PRIVATE | plan §8 |
| الدور والصلاحية / Role & Permission | security | PRIVATE | plan §8 |

LOOKUPS OWNED    (value lists this module masters, via its own generic Lookups screen — plan §2)
| Lookup key | Description | Initial values (only those the user named) | Source |
|---|---|---|---|
| payment-methods | طرق السداد / Payment methods | None named — categories only | plan §2.2 |
| accounting-event-types | أنواع الأحداث المحاسبية / Accounting event types | None named — categories only | plan §2.2, §3.4 |
| account-types | أنواع الحسابات / Account types | asset, liability, equity, revenue, expense (plan §1.2) | plan §1.2, §2.2 |
| period-states | حالات الفترة / Period states | Open, Soft Close, Hard Close, Year-End Close (plan §7.2) | plan §2.2, §7.2 |
| journal-types | أنواع القيود / Journal types | Event-generated, Manual, Recurring/Reversing, Allocation, Void/Correction (plan §4, §6.2) | plan §2.2, §4, §6.2 |

LOOKUPS CONSUMED (from other modules)
None. FIN's reference data is deliberately isolated in tables it owns exclusively —
no link to or dependency on any other module's (including `MDL`'s) generic reference
tables (plan §2.1; platform-summary Resolved Decision #1).

SHARED ENTITIES CONSUMED
None. Total separation from the host platform's business entities and tables — FIN
neither reads from nor writes to any other module's tables (plan §0, §10.4).

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
|---|---|---|
| — | — | NONE |
ROOT: YES

FIN's only inbound integration is the canonical accounting event, produced by the
out-of-scope Event consumer (plan §0) — not a platform module dependency, so no XM
record is declared here. `PRC`, `SLS`, `HR` each declare, on their own side, the
obligation to emit that event (project-registry CAT-6 XM-CAND-003/004/005).

AUTO-DECISIONS
AUTO: Type = "engine" (not plain "transactional"), reflecting FIN's core Rules Engine architecture.  FROM: FIN vision document §3 ("Rules Engine — the core").  IF WRONG: reclassify to "transactional" — cosmetic only, no structural impact.
AUTO: FIN excluded from the platform's shared `MDL` lookup pattern and `SEC` security model; it owns dedicated lookup tables and an independent RBAC instead.  FROM: FIN vision document §2.1, §8.1 (stated twice, explicitly).  IF WRONG: revert to the platform-shared default (adds `ORG`/`SEC`/`MDL` SOFT-READ dependencies back, per XM-CAND-007) — see platform-summary Resolved Decision #1 for the trade-off.
AUTO: Multi-currency, multi-ledger/multi-entity, intercompany entries, statistical accounts, multi-pattern fiscal calendar, attachments excluded from v1.  FROM: FIN vision document §12 (explicit exclusion list).  IF WRONG: scope into a FIN v2.

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | FIN's dependency posture — platform-shared (ORG/SEC/MDL) vs. fully isolated | Fully isolated: `DEPENDENCIES: NONE`, `ROOT: YES`, own lookups, own RBAC | Recommended and adopted for this draft — confirm or reject at `prd-approval` gate | FIN vision document §0, §2.1, §8.1, §10 |
══════════════════════════════════════════════════════════════════
