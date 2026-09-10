# ADR-FIN-001 — FIN's SEC/MDL dependencies are not modeled as XM rows except one SOFT-READ

Module  : FIN     Version : v1     Stage raised : P2 (Database)
Status  : ACCEPTED (non-breaking)

## Context
`srs-fin.md` §A8 carried forward, from `module-registry-fin.md` (P0), three "HARD-FK"
rows against SEC (User; ModuleRegistry/ScreenRegistry/ActionRegistry) and one "HARD-FK"
row against MDL (LookupType/LookupValue). At P2, assigning the actual `XM-*` register
from these candidates surfaces a discrepancy: `shared/XM-PROTOCOL.md` and this factory's
own knowledge base (`erp-domain-standards.md §5`) define `HARD-FK` as "a physical foreign
key to another module's table." No such physical, cross-module foreign key exists
anywhere in this pipeline — not in SEC's own script (its own audit columns are a
"principal string, not a numeric FK" by its own explicit db-script rule), not in MDL's
(its one cross-module dependency, XM-MDL-001, is SOFT-READ, and its own self-registration
into SEC was never modeled as an XM at all).

## Decision
P2 assigns exactly one XM row, `XM-FIN-001` (SOFT-READ → MDL_LOOKUP_VALUE), covering
every FIN column backed by one of FIN's 13 owned-but-MDL-hosted lookup keys. FIN's
dependency on SEC for identity and authorization (every request, via the same CORE
interceptor pattern SEC's and MDL's own P3.1 plans already describe) and FIN's own
self-registration into SEC (module/screens/actions, via SEC's REST onboarding endpoints)
are **not** given `XM` rows — they are narrated as platform-standard integration in
FIN's own P3.1 backend execution plan (Phase 1 CORE and Phase 7 SEC-BE), exactly
mirroring how SEC's and MDL's own P3.1 plans already handled the identical pattern.

## Consequences
- No SRS content changes — `srs-fin.md` §A8's three SEC rows remain readable as the
  *functional* dependency statement they always were (FIN cannot operate without SEC);
  this ADR only corrects which of them becomes a formal, P2-owned `XM-*` record.
- `db-script-fin.md` carries no cross-module physical FK anywhere, consistent with every
  other module built so far.
- A future reviewer comparing `srs-fin.md` §A8 ("HARD-FK") against `db-script-fin.md` §2
  (one SOFT-READ XM, the SEC rows absent) should read this ADR as the reconciling record,
  not a defect.

## Traces
ENT-FIN-001, ENT-FIN-004, ENT-FIN-007, ENT-FIN-008, ENT-FIN-009, ENT-FIN-010,
ENT-FIN-011, ENT-FIN-013 · REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010,
REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031, REQ-FIN-044,
REQ-FIN-045 · XM-FIN-001
