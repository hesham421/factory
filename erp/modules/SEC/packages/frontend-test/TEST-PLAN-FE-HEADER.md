<!-- source: PHASE:TEST-PLAN-FE — preamble before the first SUB -->
<!-- traces: AC-SEC-001, AC-SEC-002, AC-SEC-003, AC-SEC-004, AC-SEC-005, AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-009, AC-SEC-010, AC-SEC-011, AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-016, AC-SEC-017, AC-SEC-019, AC-SEC-020, AC-SEC-021, AC-SEC-022, AC-SEC-023, AC-SEC-025, AC-SEC-026, AC-SEC-027, AC-SEC-028, AC-SEC-030, AC-SEC-031, AC-SEC-032, AC-SEC-033, REQ-SEC-001, REQ-SEC-002, REQ-SEC-003, REQ-SEC-004, REQ-SEC-005, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-016, REQ-SEC-017, REQ-SEC-019, REQ-SEC-020, REQ-SEC-021, REQ-SEC-022, REQ-SEC-023, REQ-SEC-025, REQ-SEC-026, REQ-SEC-027, REQ-SEC-028, REQ-SEC-030, REQ-SEC-031, REQ-SEC-032, REQ-SEC-033 -->
## TEST-PLAN-FE — SEC v1

Thirty test cases, so the phase splits (threshold: TC count > 8) into the two labels the
profile names: `UI-FLOWS` for the per-screen flows, and `INT-FLOW` for the flows that cross
screens — the dynamic menu, which every other screen's guard reads, and the dashboard widget
whose absence and whose target route are two separate mechanisms. Every case derives from
exactly one `AC-*`, cites the `SCR-*` and route it exercises, and asserts the catalog message
in both languages wherever a `RULE-*` fires.
