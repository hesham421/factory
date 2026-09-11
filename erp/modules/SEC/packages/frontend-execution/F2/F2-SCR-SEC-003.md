<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-003 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-029, API-SEC-003, API-SEC-004, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-029, SCR-SEC-003 -->
<!-- SUB:F2-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F2 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F2-QUERY — API-SEC-003            traces=API-SEC-003,REQ-SEC-006,REQ-SEC-029
POST `/api/v1/sec/auth/password-reset/request` · request `PasswordResetRequest` { email } ·
response `ConfirmationResponse` { messageAr, messageEn } · kind **mutation**
Cache key    : none
Errors       : `VALIDATION_ERROR` (400) → inline. There is deliberately no not-found path: the
               endpoint answers identically whether or not the email is registered, and the
               client must not infer one from a timing or a status difference.
Loading      : LOCAL
Cache policy : defaults
Invalidation : none
### F2-QUERY — API-SEC-004            traces=API-SEC-004,REQ-SEC-007,REQ-SEC-008
POST `/api/v1/sec/auth/password-reset/complete` · request `PasswordResetCompleteRequest`
{ token, newPassword } · response `ConfirmationResponse` · kind **mutation**
Cache key    : none
Errors       : `SEC-409-RESET-TOKEN-INVALID` (409) → user message for RULE-SEC-006,
               ar: "رابط إعادة التعيين غير صالح أو منتهي" ·
               en: "This reset link is invalid or has expired" (AC-SEC-008) ·
               `VALIDATION_ERROR` (400) → inline · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : none — the caller is unauthenticated and holds no cached entity
### F2-SCREEN-INIT — SCR-SEC-003
Permission read : none — public screen (SRS Access summary: SEC_PWD_RESET)
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-003
Composes     : the two mutations above
State it owns: the wizard step (mirrored from the route param, not owned independently), the
               confirmation text returned by whichever step ran, and the last rejection
Operations   : requestReset(email) → always ends in the same generic confirmation ·
               completeReset(token, newPassword) → on success route to SCR-SEC-001; on
               `SEC-409-RESET-TOKEN-INVALID` stay on step 2 with the message and change nothing
The optional notification of REQ-SEC-029 is dispatched entirely server-side when a token is
issued; no client call, state or affordance represents it.

<!-- SUB:F2-SCR-SEC-003:END -->
