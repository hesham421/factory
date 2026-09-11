<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-004 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-004, AC-SEC-005, AC-SEC-009, AC-SEC-010, AC-SEC-011, AC-SEC-031, API-SEC-005, API-SEC-006, API-SEC-007, API-SEC-008, API-SEC-009, API-SEC-010, API-SEC-011, REQ-SEC-004, REQ-SEC-005, REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-031, SCR-SEC-004 -->
<!-- SUB:F3-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F3 · SCR-SEC-004 — المستخدمون / Users

Validation timing for this form: **on blur for the unique fields, on submit for the rest**
(declared once for the whole drawer).
### F3-FIELD — SCR-SEC-004 (create)
username   · REQUIRED · LENGTH (maxLength 100) · UNIQUE_CHECK · when blur
email      · REQUIRED · LENGTH (maxLength 255) · PATTERN (valid email) · UNIQUE_CHECK · when blur
fullNameAr · REQUIRED · LENGTH (maxLength 200) · when submit
fullNameEn · REQUIRED · LENGTH (maxLength 200) · when submit
password   · REQUIRED · LENGTH (maxLength 200) · when submit — create only
### F3-FIELD — SCR-SEC-004 (edit)
username   · read-only — not an input at all; `UserUpdateRequest` does not carry it
email      · REQUIRED · LENGTH · PATTERN · UNIQUE_CHECK (current record excluded) · when blur
fullNameAr, fullNameEn · REQUIRED · LENGTH · when submit
UNIQUE_CHECK : async, on blur, via `API-SEC-005` with an EQUALS filter on the field; the
               current record is excluded on edit by comparing the returned `userPk`. A
               failure of the check never blocks submit on its own — the authority is the
               server's `SEC-409-USER-DUP`, routed inline to the same field.
### F3-VALIDATION — RULE-SEC-005      traces=REQ-SEC-020,AC-SEC-020
Statement : The system shall prevent assigning a user, by any combination of roles, both
            actions of a module-declared conflicting pair.
Message   : from the catalog code `SEC-409-SOD-CONFLICT` —
            ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" ·
            en: "This user already holds a conflicting action"
Scope     : CREATE and UPDATE of the role assignment (API-SEC-008)
Field     : roles (the multi-select) · kind BUSINESS_RULE · when submit
Validation shape : **server-side only.** Conflicting pairs are declared by the owning consumer
            module and no published endpoint exposes them, so the client cannot know which
            selection conflicts before it is sent. The returned catalog code routes to a user
            message on the roles field and the selection is left exactly as the administrator
            made it, so the offending choice is visible rather than silently reverted.
Business-code fields: none — no SEC entity carries a platform-numbered business code
(SRS §3.3 NUMBERING test: all "No"), so there is no read-only code display on this form.
LOOKUP_VALID : `statusCode` is never an input on this screen (it is changed by API-SEC-009 /
            010 / 011), so no lookup validator exists to bind — which is also why ADR-SEC-006's
            missing lookup endpoint costs this form nothing.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `ACCESS_DENIED` on submit and
the form shows the localized forbidden message; the fields are not pre-emptively disabled,
because the permission is not readable (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-004:END -->
