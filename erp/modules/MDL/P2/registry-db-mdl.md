## REGISTRY — P2 — MDL v1
══════════════════════════════════════════════════════════════════

Tables
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| MDL_LOOKUP_TYPE | ENT-MDL-001 | master | DBF-MDL-001 … DBF-MDL-010 |
| MDL_LOOKUP_VALUE | ENT-MDL-002 | lookup | DBF-MDL-011 … DBF-MDL-021 |

DBF ids (full detail in db-script-mdl.md → §1): DBF-MDL-001, DBF-MDL-002, DBF-MDL-003,
DBF-MDL-004, DBF-MDL-005, DBF-MDL-006, DBF-MDL-007, DBF-MDL-008, DBF-MDL-009, DBF-MDL-010,
DBF-MDL-011, DBF-MDL-012, DBF-MDL-013, DBF-MDL-014, DBF-MDL-015, DBF-MDL-016, DBF-MDL-017,
DBF-MDL-018, DBF-MDL-019, DBF-MDL-020, DBF-MDL-021

XM index
| XM id | Type | From | To | Status |
|---|---|---|---|---|
| XM-MDL-001 | SOFT-READ | MDL | SEC | ACTIVE |

Lookups
| Key | Seeded values count | Owner |
|---|---|---|
None — MDL owns the mechanism, not a domain-specific coded list of its own.

Sequences
Last DBF: DBF-MDL-021 · Last XM: XM-MDL-001

Decisions
None (no ADR this stage).

Event
"P2 completed: MDL v1 — 2 tables, 21 DBF, 1 XM"

Cascade
No registry XM row anywhere in the platform currently targets MDL with status DEFERRED —
nothing to resolve. XM-MDL-001 itself (MDL → SEC) resolves immediately to ACTIVE since SEC
v1 is already gated (pass-1 APPROVE, see project-registry.md PIPELINE/PROGRESS STATUS).
══════════════════════════════════════════════════════════════════
