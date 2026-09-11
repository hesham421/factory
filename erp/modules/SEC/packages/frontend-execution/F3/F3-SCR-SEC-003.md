<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-003 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-029, API-SEC-003, API-SEC-004, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-029, SCR-SEC-003 -->
<!-- SUB:F3-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F3 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

Validation timing for this form: **on submit**, per step.
### F3-FIELD — SCR-SEC-003 step 1
email · REQUIRED · LENGTH (maxLength 255) · PATTERN (valid email) · when submit
### F3-FIELD — SCR-SEC-003 step 2
token           · REQUIRED · LENGTH (maxLength 200) · when submit
newPassword     · REQUIRED · LENGTH (maxLength 200) · when submit
confirmPassword · REQUIRED · BUSINESS_RULE (equal to newPassword) · when submit — client-side
                  only, never sent; it is the SRS's "confirm password" field (B3)
Validation shape : step 1 one required email; step 2 a required token, a required new password
                   within the published maximum, and an equality check between the two password
                   fields. No password-complexity rule is asserted: the SRS refers to "the
                   platform's password rules" (AC-SEC-007) without stating them, and the server
                   is the only place they exist. Written with `zod` + `react-hook-form`.
### F3-VALIDATION — RULE-SEC-006      traces=REQ-SEC-008,AC-SEC-008
Statement : The system shall reject a password-reset submission whose token is expired or
            already used.
Message   : from the catalog code `SEC-409-RESET-TOKEN-INVALID` —
            ar: "رابط إعادة التعيين غير صالح أو منتهي" ·
            en: "This reset link is invalid or has expired"
Scope     : CREATE (the step-2 submission)
Field     : token · kind BUSINESS_RULE · when submit
Validation shape : **server-side only.** Expiry and single use are properties of a token the
            client cannot inspect — no published endpoint returns a token's `expiresAt` or
            `usedAt`. The form submits and routes the returned catalog code to a user message
            above the fields, leaving every field as the user left it (AC-SEC-008: "changes
            nothing"). The message is read from the catalog, never hard-coded.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-003:END -->
