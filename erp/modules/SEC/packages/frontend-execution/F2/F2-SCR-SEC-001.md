<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-001 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-001, AC-SEC-002, API-SEC-001, REQ-SEC-001, REQ-SEC-002, SCR-SEC-001 -->
<!-- SUB:F2-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F2 · SCR-SEC-001 — تسجيل الدخول / Login

### F2-QUERY — API-SEC-001            traces=API-SEC-001,REQ-SEC-001,REQ-SEC-002
POST `/api/v1/sec/auth/login` · request `LoginRequest` { username, password } ·
response `LoginResponse` { accessToken, tokenType, expiresIn } · kind **mutation**
Cache key    : none — a mutation holds no cache entry
Errors       : `SEC-401-INVALID-CREDENTIALS` (401) → user message, shown above the form,
               ar: "بيانات الدخول غير صحيحة" · en: "Invalid credentials" (AC-SEC-002) ·
               `VALIDATION_ERROR` (400) → inline, per `error.fieldErrors[].field` ·
               `INTERNAL_ERROR` (500) → generic message
Loading      : LOCAL — the submit affordance is busy; the SRS states nothing about this call
               being slow, so no GLOBAL indicator (a GLOBAL one would need an ADR)
Cache policy : defaults
Invalidation : the entire server-state cache is discarded and API-SEC-027 (menu) is fetched
               fresh on success — a new session must not read another identity's cached data
### F2-SCREEN-INIT — SCR-SEC-001
Permission read : none — this screen is public (SRS Access summary: SEC_LOGIN is public), so
                  no VIEW is read and no guard runs before it
Lookups used    : none
Entity by id    : none — this screen has no edit mode
### F2-FACADE — SCR-SEC-001
Composes     : the API-SEC-001 mutation only
State it owns: the form's submitted/failed state and the last rejection message; no list, no
               selection, no filters
Operations   : signIn(credentials) → on success, store the token through the session
               transport and navigate to the caller's own landing screen resolved from the
               freshly fetched menu; on `SEC-401-INVALID-CREDENTIALS`, stay and show the
               message — never a partial session
The rejected path records a `LOGIN_FAILED` audit entry server-side (REQ-SEC-002); the client
neither writes nor counts it.

<!-- SUB:F2-SCR-SEC-001:END -->
