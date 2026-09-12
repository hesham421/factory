<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-005 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-025, AC-FIN-026, API-FIN-015, API-FIN-016, API-FIN-017, API-FIN-037, REQ-FIN-025, REQ-FIN-026, SCR-FIN-005, UXD-FIN-010 -->
<!-- SUB:F3-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F3 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

Validation timing for this form: **on submit** (declared once for the whole page).
### F3-FIELD — SCR-FIN-005 (rule header, create)
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sourceAccountId · REQUIRED · when submit
### F3-FIELD — SCR-FIN-005 (allocation target)
targetAccountId      · REQUIRED · when submit
dimensionValueId     · optional · when submit
distributionTypeCode · REQUIRED · LOOKUP_VALID (`DISTRIBUTION_TYPE`, UXD-FIN-010) ·
                       LENGTH (15) · when submit
distributionValue    · BUSINESS_RULE (required unless the distribution type is REMAINDER —
                       SRS ENT-FIN-014) · when submit
isRemainderFl        · BUSINESS_RULE (RULE-FIN-003) · when submit
### F3-VALIDATION — RULE-FIN-003      traces=REQ-FIN-025,AC-FIN-025
Statement : The system shall require exactly one target marked as the remainder whenever the
            set forms a compound or percentage distribution.
Message   : from the catalog code `FIN-409-REMAINDER-COUNT` — the same ar/en pair the rule
            declares, shown on the target grid; a marker disagreeing with its own type is the
            catalog's `FIN-422-REMAINDER-MARKER` on the offending row
Scope     : CREATE of the target set, and again at RUN — the server re-validates the set when
            the rule runs, not only when it is created
Field     : isRemainderFl, across the target grid · kind BUSINESS_RULE · when submit
Validation shape : one exclusive marker across the grid, as on SCR-FIN-003. The grid also
            shows the percentage targets' running sum as a display.
### F3-VALIDATION — RULE-FIN-010      traces=REQ-FIN-026,AC-FIN-026
Statement : The system shall compute the remainder line's amount as a difference after every
            percentage line rounds to the smallest currency unit, and that amount must be
            positive.
Message   : from the catalog codes `FIN-422-REMAINDER-NOT-POSITIVE` and the rule's own text —
            ar: "سطر الباقي يُحسب كفرق، لا كنسبة" ·
            en: "The remainder line is computed as a difference, never as a percentage"
Scope     : the RUN of the rule (API-FIN-017)
Field     : the remainder target · kind BUSINESS_RULE · when submit (of the run)
Validation shape : **server-side only, and deliberately not previewed.** The remainder depends
            on the source account's balance at the moment of the run, which no published
            endpoint gives this screen; the remainder cell therefore shows the word
            "الباقي / remainder" instead of a figure. Showing a predicted number would invite
            trust in a value the server has not produced, and the rule's own message says the
            remainder is a difference and never a percentage.
Business-code fields: none.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit or on run and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-005:END -->
