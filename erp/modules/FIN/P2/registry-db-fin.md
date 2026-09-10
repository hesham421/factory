## REGISTRY — P2 — FIN v1
══════════════════════════════════════════════════════════════════

Tables
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| FIN_ACCOUNT | ENT-FIN-001 | master | DBF-FIN-001 … DBF-FIN-013 |
| FIN_DIMENSION | ENT-FIN-002 | config | DBF-FIN-014 … DBF-FIN-022 |
| FIN_DIMENSION_VALUE | ENT-FIN-003 | lookup | DBF-FIN-023 … DBF-FIN-033 |
| FIN_JOURNAL_ENTRY | ENT-FIN-004 | transactional | DBF-FIN-034 … DBF-FIN-050 |
| FIN_JOURNAL_LINE | ENT-FIN-005 | transactional | DBF-FIN-051 … DBF-FIN-060 |
| FIN_JOURNAL_LINE_DIM | ENT-FIN-006 | transactional | DBF-FIN-061 … DBF-FIN-064 |
| FIN_FISCAL_YEAR | ENT-FIN-007 | master | DBF-FIN-065 … DBF-FIN-074 |
| FIN_FISCAL_PERIOD | ENT-FIN-008 | master | DBF-FIN-075 … DBF-FIN-088 |
| FIN_EVENT_TYPE_RULE | ENT-FIN-009 | config | DBF-FIN-089 … DBF-FIN-097 |
| FIN_RULE_LINE | ENT-FIN-010 | config | DBF-FIN-098 … DBF-FIN-108 |
| FIN_RECURRING_TEMPLATE | ENT-FIN-011 | config | DBF-FIN-109 … DBF-FIN-121 |
| FIN_RECURRING_TEMPLATE_LINE | ENT-FIN-012 | config | DBF-FIN-122 … DBF-FIN-129 |
| FIN_ALLOCATION_RULE | ENT-FIN-013 | config | DBF-FIN-130 … DBF-FIN-138 |
| FIN_ALLOCATION_TARGET | ENT-FIN-014 | config | DBF-FIN-139 … DBF-FIN-146 |

DBF ids (full detail in db-script-fin.md → §1): DBF-FIN-001 … DBF-FIN-146, full literal
list in db-script-fin.md → §6 (DBF id definitions) — cross-referenced there, not repeated
twice in this registry to keep it navigable; every id from that section is REGISTERED.

XM index
| XM id | Type | From | To | Status |
|---|---|---|---|---|
| XM-FIN-001 | SOFT-READ | FIN | MDL | ACTIVE |

Lookups
| Key | Seeded values count | Owner |
|---|---|---|
| ACCOUNT_TYPE | 5 | FIN |
| DEBIT_CREDIT | 2 | FIN |
| PERIOD_STATE | 4 | FIN |
| FISCAL_YEAR_STATUS | 2 | FIN |
| JOURNAL_TYPE | 5 | FIN |
| JOURNAL_STATUS | 3 | FIN |
| ACCOUNTING_EVENT_TYPE | 0 (host-defined) | FIN |
| PAYMENT_METHOD | 0 (host-defined) | FIN |
| ACCOUNT_DERIVATION_TYPE | 3 | FIN |
| AMOUNT_SOURCE_TYPE | 3 | FIN |
| DISTRIBUTION_TYPE | 3 | FIN |
| RECURRING_SCHEDULE_TYPE | 2 | FIN |
| RECURRING_FREQUENCY | 4 | FIN |
All seeded via MDL's API at onboarding time (BLOCK 8 note), not local INSERTs.

Sequences
Last DBF: DBF-FIN-146 · Last XM: XM-FIN-001

Decisions
ADR-FIN-001 (ACCEPTED, non-breaking) — see erp/decisions/FIN/ADR-FIN-001.md

Event
"P2 completed: FIN v1 — 14 tables, 146 DBF, 1 XM"

Cascade
No registry XM row anywhere in the platform currently targets FIN with status DEFERRED
(FIN is the last module of this batch) — nothing to resolve. XM-FIN-001 resolves
immediately to ACTIVE since MDL v1 is already gated.
══════════════════════════════════════════════════════════════════
