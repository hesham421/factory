<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-007 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-022, AC-SEC-023, API-SEC-022, REQ-SEC-022, REQ-SEC-023, SCR-SEC-007 -->
<!-- SUB:F3-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F3 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

This screen has **no form and no input of any kind** (SRS B3: "Read-only; no data entry"),
so it declares no validation timing and carries no field block.
No `RULE-*` is enforced here. The one behavioural requirement that could look like a validation
— REQ-SEC-023, hiding a widget the caller's role does not grant — is not a client-side rule at
all: the server returns only the widgets the caller may see, and the screen renders exactly
what it received (ADR-SEC-005). A client-side permission test would be a second, weaker copy of
a decision the server already made.
Number and date formatting follow the active locale (session → browser → `ar`); no figure is
rounded, aggregated or recomputed on the client, because REQ-SEC-022 requires every figure to
be the server's live computation.
Permission-driven behaviour: none beyond the above — there is no field to make read-only.

<!-- SUB:F3-SCR-SEC-007:END -->
