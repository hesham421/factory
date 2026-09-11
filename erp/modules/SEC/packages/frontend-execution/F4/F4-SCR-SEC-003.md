<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-003 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-029, API-SEC-003, API-SEC-004, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-029, SCR-SEC-003 -->
<!-- SUB:F4-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F4 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F4-SCREEN — SCR-SEC-003            traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004
Routes       : `/password-reset` (step 1 — request) · `/password-reset/complete` (step 2 —
               token and new password; the emailed link points here and carries the token as a
               search param). The step is addressed by the route, never by local-only state.
Chunk        : **one** lazy chunk for both steps — they are one composite screen under one
               `SCR-*`, and a second chunk for a sub-view would break the composite invariant
Guard        : **none — public** (SRS Access summary: SEC_PWD_RESET)
Components   : `PasswordResetPage` (route-level, hosts both steps) · `ResetRequestForm` ·
               `ResetCompleteForm` · `ResetConfirmationNotice` (presentational)
Mode         : not applicable — the wizard step, not a CREATE/EDIT/VIEW mode, is what the route
               match resolves
Facade       : the SCR-SEC-003 facade of F2
Shared UI    : card shell, text field, password field, primary button, inline errors, notice
Cross-module : none
Arriving at `/password-reset/complete` with a token in the search params opens step 2 directly
with the field pre-filled, so the emailed link is a single click; arriving without one leaves
the token field editable rather than blocking the route.

<!-- SUB:F4-SCR-SEC-003:END -->
