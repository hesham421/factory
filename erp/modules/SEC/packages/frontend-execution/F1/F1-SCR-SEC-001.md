<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-001 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-001, AC-SEC-002, API-SEC-001, REQ-SEC-001, REQ-SEC-002, SCR-SEC-001 -->
<!-- SUB:F1-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F1 · SCR-SEC-001 — تسجيل الدخول / Login

### F1-MODEL — ENT-SEC-001 — المستخدم / User (credentials projection only)
Source DTO   : `LoginRequest` (request) · `LoginResponse` (response)
  request  : username : string · required · maxLength 100 — the login identity
             password : string · required · maxLength 200 · write-only — never held after submit
  response : accessToken : string · read-only · system-only — the signed token
             tokenType   : string · read-only · system-only
             expiresIn   : number (seconds) · read-only · system-only
Read-only    : every response property — the session is issued, never edited
### F1-SCREEN — SCR-SEC-001
Search model : none — this screen has no list (SRS B2 not applicable)
Form model   : username (required) · password (required, write-only)
               excluded system fields: every other ENT-SEC-001 property — the published
               `LoginRequest` carries two fields and the form models exactly those two
               read-only on edit: not applicable — this form has no edit mode
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Nothing is modelled that the api-docs do not return: `userPk`, `statusCode` and the user's
own profile are absent from `LoginResponse` and are therefore absent from this model. The
caller's identity for the rest of the session comes from the menu (API-SEC-027), not from a
user object this endpoint does not send.

<!-- SUB:F1-SCR-SEC-001:END -->
