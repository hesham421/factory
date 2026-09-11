<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-002 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-003, API-SEC-002, REQ-SEC-003, SCR-SEC-002 -->
<!-- SUB:F1-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F1 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F1-MODEL — ENT-SEC-013 — طلب تسجيل معلّق / SignupRequest
Source DTO   : `SignupSubmitRequest` (request) · `SignupRequestResponse` (response)
  request  : email      : string · required · maxLength 255
             fullNameAr : string · required · maxLength 200
             fullNameEn : string · required · maxLength 200
  response : signupRequestPk : number · read-only (PK) · system-only
             email, fullNameAr, fullNameEn : string · read-only on the response
             submittedAt : date-time · read-only · system-only
             statusCode  : string · read-only · lookup — SIGNUP_STATUS code, held as a string
                           (no enum, no union of literals — ADR-SEC-006)
             reviewedBy  : string · read-only · system-only
             reviewedAt  : date-time · read-only · system-only
Read-only    : PK, submittedAt, statusCode, reviewedBy, reviewedAt — never form input
### F1-SCREEN — SCR-SEC-002
Search model : none — public single-purpose form
Form model   : email, fullNameAr, fullNameEn (all required)
               excluded system fields: signupRequestPk, submittedAt, statusCode, reviewedBy,
               reviewedAt
               read-only on edit: not applicable — the request is submitted once, never edited
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Both name properties are modelled separately per language (ar, en) as the DTO declares them;
neither is derived from the other.

<!-- SUB:F1-SCR-SEC-002:END -->
