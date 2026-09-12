<!-- source: PHASE:F1 — preamble before the first SUB -->
<!-- traces: REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, UXD-MDL-001, SCR-MDL-001, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-010, API-MDL-011, SCR-MDL-002 -->
## PHASE 1 — F1 — Models & Types

Per `ENT-*` (from the response DTOs of the api-docs) and per `SCR-*`: the source DTO with each
property's type and read-only / system-only status, then the screen's search model, form model
and container. Both names are carried per language (ar, en). No internal or tenant identifier
is modelled, and nothing is modelled that the api-docs do not return. **No lookup field and no
enum appears anywhere in this phase** — MDL owns no coded list of its own (SRS §A6).
