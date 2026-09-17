## REGISTRY — P2 — NOTE v1
══════════════════════════════════════════════════════════════════
Module : NOTE (الملاحظات / Notes)   Version : v1   Profile : erp
Source : erp/modules/NOTE/P2/db-script-note.md   Dialect : postgresql16
══════════════════════════════════════════════════════════════════

Tables
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| NOTE_NOTE | ENT-NOTE-001 | master | DBF-NOTE-001 … DBF-NOTE-009 |

DBF ids (full detail in db-script-note.md → §1):
DBF-NOTE-001, DBF-NOTE-002, DBF-NOTE-003, DBF-NOTE-004, DBF-NOTE-005, DBF-NOTE-006,
DBF-NOTE-007, DBF-NOTE-008, DBF-NOTE-009

XM index
none — 0 XM rows (→ dependency index: no row for this module). SRS A8 classifies all four
consumed SEC entities as neither HARD-FK nor SOFT-READ candidates: the identity is
consumed as a principal string with no FK, and the module/screen/action registration is
data written at deployment, not a runtime dependency (precedent ADR-FIN-001,
project-registry DECISION INDEX #9). INT-C and INT-R stay empty but present in the
execution plan.

Lookups
| Key | Seeded values count | Owner |
|---|---|---|
| — | 0 | — — NOTE owns no lookup key and consumes none (SRS A6); no seed block anywhere in this script, and no other module's lookup table is touched |

Sequences
Last DBF: DBF-NOTE-009 · Last XM: none assigned (0 rows)
Database sequence objects: SEQ_NOTE_NOTE (1 sequence, 1 table — pk_generation `sequence`)

Decisions
| ADR id | Subject | Status |
|---|---|---|
| ADR-NOTE-004 | No index on the substring-filtered title/body columns; the owner-scoped composite index bounds the search instead | ACCEPTED (non-breaking) — erp/decisions/NOTE/ADR-NOTE-004.md |
ADR-NOTE-001 / ADR-NOTE-002 (assigned by P1) are applied by this script but not
re-assigned here. No BLOCKED ADR — the pass completed. No question was raised.

Event
"P2 completed: NOTE v1 — 1 table, 9 DBF, 0 XM"

Cascade
No registry XM row anywhere in the platform targets NOTE with status DEFERRED —
ENT-NOTE-001 is PRIVATE (POL-NOTE-001) and no module consumes it. Nothing to resolve
under shared/XM-PROTOCOL.md.
══════════════════════════════════════════════════════════════════
