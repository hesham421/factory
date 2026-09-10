## REGISTRY — P1 — MDL v1
══════════════════════════════════════════════════════════════════

Entities
| ENT id | Name (ar/en) | Kind | PRIVATE/SHARED | Status |
|---|---|---|---|---|
| ENT-MDL-001 | نوع اللوكب / LookupType | master | SHARED (owner) | REGISTERED |
| ENT-MDL-002 | قيمة اللوكب / LookupValue | lookup | SHARED (owner) | REGISTERED |

Consumed
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ |
|---|---|---|---|
| ModuleRegistry | ENT-SEC-004 | SEC | SOFT-READ |

Lookups owned
None (see SRS A6).

Lookups consumed
None.

Screens
| SCR-REQ id | Name (ar/en) | Page code |
|---|---|---|
| SCR-REQ-MDL-001 | اللوكبات العامة / Generic Lookups | MDL_LOOKUPS |
| SCR-REQ-MDL-002 | سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner | MDL_TYPE_REGISTRY |

Requirements
REQ count: 13 · AC count: 13 · RULE count: 4 · ENT count: 2 · SCR-REQ count: 2
Last sequence per atom: REQ: 013 · AC: 013 · ENT: 002 · RULE: 004 · SCR-REQ: 002

REQ ids (full text in srs-mdl.md → A4): REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004,
REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, REQ-MDL-011,
REQ-MDL-012, REQ-MDL-013

AC ids (full text in srs-mdl.md → A4, one per REQ above): AC-MDL-001, AC-MDL-002,
AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009,
AC-MDL-010, AC-MDL-011, AC-MDL-012, AC-MDL-013

RULE ids (full text in srs-mdl.md → A5): RULE-MDL-001, RULE-MDL-002, RULE-MDL-003,
RULE-MDL-004

Decisions
ADR ids: none.

Event
"P1 completed: MDL v1 — 2 entities, 13 requirements, 13 acceptance criteria, 4 rules, 2 screen requirements, 0 ADRs"
══════════════════════════════════════════════════════════════════
