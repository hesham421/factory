<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-002 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-003, API-SEC-002, REQ-SEC-003, SCR-SEC-002 -->
<!-- SUB:F2-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F2 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F2-QUERY — API-SEC-002            traces=API-SEC-002,REQ-SEC-003
POST `/api/v1/sec/auth/signup` · request `SignupSubmitRequest` { email, fullNameAr,
fullNameEn } · response `SignupRequestResponse` · kind **mutation**
Cache key    : none
Errors       : `SEC-409-SIGNUP-DUP` (409) → user message (a request for that email already
               exists) · `VALIDATION_ERROR` (400) → inline per field · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : none for this caller — the submitter is unauthenticated and holds no cached
               list. An administrator's pending-sign-ups list (API-SEC-005 on SCR-SEC-004) is a
               different session and refreshes on its own key.
### F2-SCREEN-INIT — SCR-SEC-002
Permission read : none — public screen (SRS Access summary: SEC_SIGNUP)
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-002
Composes     : the API-SEC-002 mutation only
State it owns: submitted / not submitted, and the returned request's status for the
               confirmation text
Operations   : submitSignup(form) → on success switch to the confirmation state, which states
               that the request is PENDING and that no account exists yet (REQ-SEC-003)

<!-- SUB:F2-SCR-SEC-002:END -->
