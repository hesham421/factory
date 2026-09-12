<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-004 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-022, AC-FIN-023, AC-FIN-024, API-FIN-012, API-FIN-013, API-FIN-014, API-FIN-036, REQ-FIN-022, REQ-FIN-023, REQ-FIN-024, SCR-FIN-004, UXD-FIN-002, UXD-FIN-011, UXD-FIN-012 -->
<!-- SUB:F3-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F3 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

Validation timing for this form: **on submit** (declared once for the whole page) —
there is no unique field on this screen to check on blur.
### F3-FIELD — SCR-FIN-004 (template header, create)
nameAr, nameEn   · REQUIRED · LENGTH (maxLength 150) · when submit
scheduleTypeCode · REQUIRED · LOOKUP_VALID (`RECURRING_SCHEDULE_TYPE`, UXD-FIN-011) ·
                   LENGTH (15) · when submit
frequencyCode    · BUSINESS_RULE (required when the schedule type is RECURRING; not applicable
                   to REVERSING — SRS ENT-FIN-011) · LOOKUP_VALID (`RECURRING_FREQUENCY`,
                   UXD-FIN-012) · LENGTH (15) · when submit
startDate        · REQUIRED · when submit
endDate          · optional · DATE_RANGE (not before `startDate`) · when submit
### F3-FIELD — SCR-FIN-004 (template line)
accountId        · REQUIRED · when submit
amount           · REQUIRED · BUSINESS_RULE (positive — RULE-FIN-006/POL-FIN-005: the amount
                   carries no sign, the direction does) · when submit
directionCode    · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
dimensionValueId · optional · when submit
### F3-VALIDATION — RULE-FIN-006 (applied at run time, not at save)   traces=REQ-FIN-018,AC-FIN-018
Statement : The system shall reject posting an entry whose total debits do not equal its total
            credits to the smallest currency unit.
Message   : from the catalog code `FIN-409-UNBALANCED` —
            ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" ·
            en: "The entry is unbalanced — total debits do not equal total credits"
Scope     : the RUN of the template (API-FIN-014), not its creation — the SRS §B5 is explicit
            that the balance check is applied at run time, not at save time
Field     : the line grid · kind BUSINESS_RULE · when submit (of the run)
Validation shape : the grid shows a running debit and credit total while the template is
            drafted, as a display; it does **not** block the save, because an unbalanced
            template is a legal row the server accepts and refuses only when run. On the run,
            the catalog message is shown as a user message beside the template.
`FIN-400-MISSING-FREQUENCY` is the server's answer to the frequency rule above and is routed
inline to `frequencyCode`; the field is hidden, not disabled, when the schedule type is
REVERSING, because the SRS calls it "not applicable" rather than empty.
Business-code fields: none.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit or on run and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-004:END -->
