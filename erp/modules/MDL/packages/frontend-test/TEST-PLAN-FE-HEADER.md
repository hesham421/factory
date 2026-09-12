<!-- source: PHASE:TEST-PLAN-FE — preamble before the first SUB -->
<!-- traces: AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, AC-MDL-013, REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, REQ-MDL-013 -->
## TEST-PLAN-FE — MDL v1

Eleven test cases, so the phase splits (threshold: TC count > 8) into the two labels the
profile names: `UI-FLOWS` for the per-screen flows, and `INT-FLOW` for the one flow that
crosses screens. Every case derives from exactly one `AC-*`, cites the `SCR-*` and route it
exercises, and asserts the catalog message in both languages wherever a `RULE-*` fires.
