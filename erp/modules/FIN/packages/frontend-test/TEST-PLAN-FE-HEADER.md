<!-- source: PHASE:TEST-PLAN-FE — preamble before the first SUB -->
<!-- traces: AC-FIN-001, AC-FIN-002, AC-FIN-003, AC-FIN-004, AC-FIN-005, AC-FIN-006, AC-FIN-007, AC-FIN-008, AC-FIN-009, AC-FIN-014, AC-FIN-015, AC-FIN-016, AC-FIN-017, AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-022, AC-FIN-023, AC-FIN-025, AC-FIN-026, AC-FIN-027, AC-FIN-028, AC-FIN-029, AC-FIN-030, AC-FIN-031, AC-FIN-032, AC-FIN-033, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-037, AC-FIN-038, AC-FIN-039, AC-FIN-040, AC-FIN-041, AC-FIN-042, AC-FIN-043, AC-FIN-046, REQ-FIN-001, REQ-FIN-002, REQ-FIN-003, REQ-FIN-004, REQ-FIN-005, REQ-FIN-006, REQ-FIN-007, REQ-FIN-008, REQ-FIN-009, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-022, REQ-FIN-023, REQ-FIN-025, REQ-FIN-026, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038, REQ-FIN-039, REQ-FIN-040, REQ-FIN-041, REQ-FIN-042, REQ-FIN-043, REQ-FIN-046 -->
## TEST-PLAN-FE — FIN v1

Thirty-nine test cases, so the phase splits (threshold: TC count > 8) into the two labels the
profile names: `UI-FLOWS` for the per-screen flows, and `INT-FLOW` for the one flow that
crosses screens. Every case derives from exactly one `AC-*`, cites the `SCR-*` and route it
exercises, and asserts the catalog message in both languages wherever a `RULE-*` fires.
