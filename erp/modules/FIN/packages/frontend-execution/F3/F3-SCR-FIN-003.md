<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-003 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-007, AC-FIN-008, AC-FIN-009, API-FIN-009, API-FIN-010, API-FIN-011, API-FIN-034, REQ-FIN-007, REQ-FIN-008, REQ-FIN-009, SCR-FIN-003, UXD-FIN-002, UXD-FIN-007, UXD-FIN-008, UXD-FIN-009, UXD-FIN-010 -->
<!-- SUB:F3-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F3 · SCR-FIN-003 — قواعد المحرك / Engine rules

Validation timing for this form: **on submit** for the rule header and for each line
(declared once for the whole page). The remainder marker is judged across the line set, so it
has nothing to validate until a line is submitted.
### F3-FIELD — SCR-FIN-003 (rule header, create)
eventTypeCode  · REQUIRED · LOOKUP_VALID (`ACCOUNTING_EVENT_TYPE`, UXD-FIN-007) ·
                 LENGTH (maxLength 50) · UNIQUE_CHECK · when submit
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-FIN-003 (rule line)
accountDerivationTypeCode · REQUIRED · LOOKUP_VALID (`ACCOUNT_DERIVATION_TYPE`, UXD-FIN-008) ·
                            LENGTH (20) · when submit
accountDerivationValue    · REQUIRED · when submit
amountSourceTypeCode      · REQUIRED · LOOKUP_VALID (`AMOUNT_SOURCE_TYPE`, UXD-FIN-009) ·
                            LENGTH (20) · when submit
amountSourceValue         · BUSINESS_RULE (required unless the amount source type is
                            REMAINDER — SRS ENT-FIN-010) · when submit
directionCode             · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) ·
                            LENGTH (10) · when submit
distributionTypeCode      · REQUIRED · LOOKUP_VALID (`DISTRIBUTION_TYPE`, UXD-FIN-010) ·
                            LENGTH (15) · when submit
isRemainderFl             · BUSINESS_RULE (RULE-FIN-003) · when submit
UNIQUE_CHECK : async on `eventTypeCode` via `API-FIN-009` with an EQUALS filter. The check is
               **not** narrowed to active rules, because the server's own uniqueness guard is
               not either — a deactivated rule still holds its event type (SRS §B4). The
               authority remains `FIN-409-RULE-DUP`.
### F3-VALIDATION — RULE-FIN-003      traces=REQ-FIN-009,AC-FIN-009
Statement : The system shall require exactly one line marked as the remainder whenever the set
            forms a compound or percentage distribution.
Message   : from the catalog code `FIN-409-REMAINDER-COUNT` —
            ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" ·
            en: "Exactly one remainder line is required when any percentage distribution is
            present"
Scope     : CREATE and UPDATE of the line set
Field     : isRemainderFl, across the line grid · kind BUSINESS_RULE · when submit
Validation shape : the marker is a single exclusive choice across the grid rather than a free
            checkbox per row, so "exactly one" is expressible before the server says it; and
            the rule's second half — a marker that disagrees with its own REMAINDER
            distribution or amount-source type — is surfaced as the catalog's
            `FIN-422-REMAINDER-MARKER` on the offending row. The count is judged by the server
            over the whole persisted set, which is the only place the whole set exists.
Business-code fields: none — this screen mints no business code.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-003:END -->
