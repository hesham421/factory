<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-002 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-003, API-SEC-002, REQ-SEC-003, SCR-SEC-002 -->
<!-- SUB:F3-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F3 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

Validation timing for this form: **on blur for the email, on submit for the rest**.
### F3-FIELD — SCR-SEC-002
email      · REQUIRED · LENGTH (maxLength 255) · PATTERN (a valid email address —
             SRS ENT-SEC-013 states "valid email") · when blur
fullNameAr · REQUIRED · LENGTH (maxLength 200) · when submit
fullNameEn · REQUIRED · LENGTH (maxLength 200) · when submit
Validation shape : three required strings within their published maxima, the first also
                   matching an email shape. Written with `zod` + `react-hook-form`.
No UNIQUE_CHECK runs on this form: the only endpoint that could answer "is this email already
registered" is `API-SEC-005`, which requires `PERM_SEC_USERS_VIEW`, and the submitter here is
unauthenticated. A duplicate is answered by the server as `SEC-409-SIGNUP-DUP` after submit —
the same answer, without exposing the user directory to an anonymous caller.
No RULE-* is enforced on this form.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-002:END -->
