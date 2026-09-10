<!-- source: PHASE:INT-R -->
<!-- traces: REQ-SEC-016 -->
<!-- PHASE:INT-R:START traces=REQ-SEC-016 -->
## PHASE 6 — INT-R (cross-module resolve)

No `XM-*` row to resolve — same basis as Phase 5. No SUB opened (0 < 5).

Inbound dependency stub (future consumers, not `TODO`): `XM-INBOUND-STUB-1` — any future
module (first expected: MDL, then FIN per GENERATION-INSTRUCTIONS.md §3) will register
itself via API-SEC-018/019/020 and consume identity/authorization via API-SEC-001/027 and
the CORE interceptor; the entity it reaches is `ENT-SEC-004` (ModuleRegistry) /
`ENT-SEC-005` (ScreenRegistry) / `ENT-SEC-006` (ActionRegistry); formal `XM-*` ids for that
direction are assigned by the *consuming* module's own P2, not by SEC.
<!-- PHASE:INT-R:END -->
