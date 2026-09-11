<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-003 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-029, API-SEC-003, API-SEC-004, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-029, SCR-SEC-003 -->
<!-- SUB:F1-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F1 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F1-MODEL — ENT-SEC-012 — رمز إعادة تعيين كلمة المرور / PasswordResetToken
Source DTO   : `PasswordResetRequest` · `PasswordResetCompleteRequest` · `ConfirmationResponse`
  step 1 request : email : string · required · maxLength 255
  step 2 request : token       : string · required · maxLength 200 · write-only
                   newPassword : string · required · maxLength 200 · write-only
  response       : messageAr : string · read-only — the confirmation text, Arabic
                   messageEn : string · read-only — the confirmation text, English
Read-only    : both message properties; `tokenHash`, `requestedAt`, `expiresAt` and `usedAt`
               are never returned by any published endpoint and are therefore not modelled
### F1-SCREEN — SCR-SEC-003
Search model : none
Form model   : step 1 — email (required)
               step 2 — token (required; pre-filled from the route when the link carries it),
                        newPassword (required), confirmPassword (required, client-side only —
                        it is a confirmation of the field above and is never sent)
               excluded system fields: every ENT-SEC-012 property above
               read-only on edit: not applicable
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007); the wizard step is a route param
The response carries the localized text itself, so the screen renders `messageAr`/`messageEn`
by the active locale rather than composing a message of its own.

<!-- SUB:F1-SCR-SEC-003:END -->
