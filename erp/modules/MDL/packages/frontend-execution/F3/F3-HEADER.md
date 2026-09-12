<!-- source: PHASE:F3 — preamble before the first SUB -->
<!-- traces: REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, UXD-MDL-001, SCR-MDL-001, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-010, API-MDL-011, SCR-MDL-002 -->
## PHASE 3 — F3 — Forms & Validators

One block per `RULE-*` enforced on a form, plus the field constraints the published DTOs state.
No frontend-only validation the SRS does not state; every message is read from its catalog
code, never hard-coded; the locale resolves session → browser → `ar`; and a caller without the
write permission is answered by the server rather than by a pre-emptively disabled field.
Schemas are written with `zod` + `react-hook-form`.

**No `LOOKUP_VALID` validator exists anywhere in this module.** MDL owns no coded list (SRS
§A6), so no field binds to an option set of lookup values. The one field with a constrained set
is `ownerModuleCode`, whose set is another module's registry — its validator is named in the
SCR-MDL-001 block below and binds to the runtime-loaded list of UXD-MDL-001, never to a static
list of module codes.
