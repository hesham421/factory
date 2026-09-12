## REGISTRY — P3.1 — FIN v1
══════════════════════════════════════════════════════════════════

ID RANGES
API-FIN-001 .. API-FIN-037 · QR-FIN-001 .. QR-FIN-049

API ids: API-FIN-001, API-FIN-002, API-FIN-003, API-FIN-004, API-FIN-005, API-FIN-006,
API-FIN-007, API-FIN-008, API-FIN-009, API-FIN-010, API-FIN-011, API-FIN-012, API-FIN-013,
API-FIN-014, API-FIN-015, API-FIN-016, API-FIN-017, API-FIN-018, API-FIN-019, API-FIN-020,
API-FIN-021, API-FIN-022, API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026, API-FIN-027,
API-FIN-028, API-FIN-029, API-FIN-030, API-FIN-031, API-FIN-032, API-FIN-033,
API-FIN-034, API-FIN-035, API-FIN-036, API-FIN-037

QR ids: QR-FIN-001, QR-FIN-002, QR-FIN-003, QR-FIN-004, QR-FIN-005, QR-FIN-006, QR-FIN-007,
QR-FIN-008, QR-FIN-009, QR-FIN-010, QR-FIN-011, QR-FIN-012, QR-FIN-013, QR-FIN-014,
QR-FIN-015, QR-FIN-016, QR-FIN-017, QR-FIN-018, QR-FIN-019, QR-FIN-020, QR-FIN-021,
QR-FIN-022, QR-FIN-023, QR-FIN-024, QR-FIN-025, QR-FIN-026, QR-FIN-027, QR-FIN-028,
QR-FIN-029, QR-FIN-030, QR-FIN-031, QR-FIN-032, QR-FIN-033, QR-FIN-034, QR-FIN-035,
QR-FIN-036, QR-FIN-037, QR-FIN-038, QR-FIN-039, QR-FIN-040, QR-FIN-041, QR-FIN-042,
QR-FIN-043, QR-FIN-044, QR-FIN-045, QR-FIN-046, QR-FIN-047, QR-FIN-048,
QR-FIN-049

EXTENDED 2026-09-12 — the five endpoints and five queries delivered after this registry was
last written are now registered, which is what this section is for. API-FIN-033 (fiscal-period
search), API-FIN-034 (deactivate event-type rule), API-FIN-035 (deactivate dimension value),
API-FIN-036 (deactivate recurring template) and API-FIN-037 (deactivate allocation rule) were
all defined in `backend-execution-plan-fin.md`, published in `_inputs/api-docs-fin.md` and
bound by its API ID BINDING annex, but never carried into the ID RANGES line here; the same is
true of QR-FIN-045..049 beneath them. `gov.py analyze` reported the gap as ten C7.4
`registry-agree` findings against the plan — the plan defined ten ids this registry did not
know. Nothing is renumbered and nothing new is minted: every id above already existed in the
plan, and this section is catching up to it. Recorded from the other side in
`erp/decisions/FIN/ADR-FIN-002.md`, which raised the gap at P3.2 and named this line as where
the fix belonged.

ENTITIES / TABLES bound
All 14 ENT-FIN-001..014 bound to their db-script tables; lookups: 13 FIN-owned keys
registered into MDL (2 additional values, CLOSING/OPENING, added to JOURNAL_TYPE this
stage — data-only, non-breaking).

XM STATUS
open: none · deferred: none · active: XM-FIN-001 (SOFT-READ → MDL, target already gated).

CATALOG
31 error-catalog rows (29 module-specific/PLATFORM-STD + FIN-403-FORBIDDEN +
FIN-400-INVALID-SORT + FIN-500 generic set). Rules without a message: none — every
RULE-FIN-001..016 that produces a user-facing message has a full ar/en pair.

ALIGN
PASSED ✓ · 0 findings — including the explicit 14-point §12 coverage check (see
backend-execution-plan-fin.md → Alignment self-check → "ACCOUNTING §12" row).

ADRs
erp/decisions/FIN/ADR-FIN-001.md (ACCEPTED, carried from P2; no new ADR this stage).

TRACEABILITY
REQ covered by ≥1 API/DBF: 46/46 (every REQ-FIN-001..046 appears in ≥1 API block's
traces= or ≥1 DBF record's traces in db-script-fin.md). Orphan REQ: none.

Event
"P3.1 completed: FIN v1 — 32 API, 44 QR, ALIGN PASSED (14-point §12 coverage confirmed), 0 new ADRs"
══════════════════════════════════════════════════════════════════
