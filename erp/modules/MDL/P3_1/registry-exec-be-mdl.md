## REGISTRY — P3.1 — MDL v1
══════════════════════════════════════════════════════════════════

ID RANGES
API-MDL-001 .. API-MDL-011 · QR-MDL-001 .. QR-MDL-015

API ids: API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006,
API-MDL-007, API-MDL-008, API-MDL-009, API-MDL-010, API-MDL-011

QR ids: QR-MDL-001, QR-MDL-002, QR-MDL-003, QR-MDL-004, QR-MDL-005, QR-MDL-006, QR-MDL-007,
QR-MDL-008, QR-MDL-009, QR-MDL-010, QR-MDL-011, QR-MDL-012, QR-MDL-013, QR-MDL-014,
QR-MDL-015

ENTITIES / TABLES bound
ENT-MDL-001 → MDL_LOOKUP_TYPE, ENT-MDL-002 → MDL_LOOKUP_VALUE; lookups owned: none (MDL
is the mechanism, not a consumer of its own kind).

XM STATUS
open: none · deferred: none · active: XM-MDL-001 (SOFT-READ → SEC, target already gated).

CATALOG
10 error-catalog rows (9 module-specific/PLATFORM-STD + the shared 403 convention).
Rules without a message: none — every RULE-MDL-001..004 has a full ar/en message pair.

ALIGN
PASSED ✓ · 0 findings.

ADRs
none this stage (0 new; SEC's ADR-SEC-002 convention cited, not re-derived).

TRACEABILITY
REQ covered by ≥1 API/DBF: 13/13 (every REQ-MDL-001..013 appears in ≥1 API block's traces=
or ≥1 DBF record's traces in db-script-mdl.md). Orphan REQ: none.

Event
"P3.1 completed: MDL v1 — 11 API, 15 QR, ALIGN PASSED, 0 new ADRs"
══════════════════════════════════════════════════════════════════
