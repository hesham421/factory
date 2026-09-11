<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-001 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-001, AC-SEC-002, API-SEC-001, REQ-SEC-001, REQ-SEC-002, SCR-SEC-001 -->
<!-- SUB:F3-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F3 · SCR-SEC-001 — تسجيل الدخول / Login

Validation timing for this form: **on submit** (declared once for the whole form). A login
form that validates while the user types leaks nothing useful and only interrupts them.
### F3-FIELD — SCR-SEC-001
username · REQUIRED · LENGTH (maxLength 100, from `LoginRequest`) · when submit
password · REQUIRED · LENGTH (maxLength 200, from `LoginRequest`) · when submit
Validation shape : both fields non-empty and within their published maximum; nothing more.
                   No pattern, no minimum length and no complexity rule is asserted here —
                   the SRS states none for the login form, and inventing one would reject a
                   credential the server would have accepted. Written with `zod` +
                   `react-hook-form`.
No RULE-* is enforced on this form. REQ-SEC-002's rejection is a server decision
(`SEC-401-INVALID-CREDENTIALS`), surfaced as the user message of the F2 block above, with the
catalog's own text and never a message composed on the client.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-001:END -->
