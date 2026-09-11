<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-002 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-003, API-SEC-002, REQ-SEC-003, SCR-SEC-002 -->
<!-- SUB:F4-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F4 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F4-SCREEN — SCR-SEC-002            traces=REQ-SEC-003,AC-SEC-003,API-SEC-002
Routes       : `/sign-up` — the only route
Chunk        : one lazy chunk for this composite screen
Guard        : **none — public** (SRS Access summary: SEC_SIGNUP). A caller holding a session
               is sent to their landing screen instead, as on SCR-SEC-001.
Components   : `SignUpPage` (route-level) · `SignUpForm` · `SignUpSubmittedNotice`
               (presentational)
Mode         : not applicable — CREATE is the screen's only purpose and is not resolved from a
               route match
Facade       : the SCR-SEC-002 facade of F2
Shared UI    : card shell, text fields, primary button, inline field errors, notice block
Cross-module : none
After a successful submission the page renders `SignUpSubmittedNotice` in place of the form, so
a second submission is a deliberate navigation rather than a second click on a cleared form
(REQ-SEC-003 creates a pending request, not an account).

<!-- SUB:F4-SCR-SEC-002:END -->
