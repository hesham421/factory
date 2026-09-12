<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-006 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-010, AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-014, AC-FIN-015, AC-FIN-016, AC-FIN-017, AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-027, AC-FIN-028, AC-FIN-029, AC-FIN-030, API-FIN-018, API-FIN-019, API-FIN-020, API-FIN-021, API-FIN-022, REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, SCR-FIN-006, UXD-FIN-002, UXD-FIN-005, UXD-FIN-006 -->
<!-- SUB:F3-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F3 · SCR-FIN-006 — قيود اليومية / Journal entries

Validation timing for this form: **on submit** (declared once for the whole entry page).
REQ-FIN-015 requires every failing check to come back together, so the submission is the point
at which the entry is judged; nothing pre-empts it.
### F3-FIELD — SCR-FIN-006 (entry header, create)
docDate         · REQUIRED · DATE_RANGE (inside the selected period — RULE-FIN-017) · when submit
fiscalYearId    · REQUIRED · when submit
periodId        · REQUIRED · BUSINESS_RULE (must belong to the selected year — RULE-FIN-017) ·
                  when submit
journalTypeCode · REQUIRED, fixed to `MANUAL`, read-only — in the model because the request
                  requires it, not an input (ADR-FIN-008)
descriptionAr, descriptionEn · optional · when submit
### F3-FIELD — SCR-FIN-006 (entry line, repeating)
accountId       · REQUIRED · BUSINESS_RULE (a leaf, active account — RULE-FIN-007) · when submit
amount          · REQUIRED · BUSINESS_RULE (positive — POL-FIN-005) · when submit
directionCode   · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
descriptionAr, descriptionEn · optional
dimensions[].dimensionId, dimensions[].dimensionValueId · REQUIRED together when a dimension
                  is used · BUSINESS_RULE (the value must belong to the dimension and be
                  active — RULE-FIN-009) · when submit
### F3-VALIDATION — RULE-FIN-006      traces=REQ-FIN-018,AC-FIN-018
Statement : total debits must equal total credits to the smallest currency unit.
Message   : `FIN-409-UNBALANCED` — ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي
            الدائن" · en: "The entry is unbalanced — total debits do not equal total credits"
Scope     : CREATE
Field     : the line grid · kind BUSINESS_RULE · when submit
Validation shape : the live totals at the foot of the grid show the difference as the user
            types, and the Post affordance stays enabled regardless. Disabling it would hide
            the other failing checks REQ-FIN-015 asks to be shown together.
### F3-VALIDATION — RULE-FIN-007      traces=REQ-FIN-019,AC-FIN-019
Statement : a line may not target an account that is not a leaf, not active, or not marked as
            accepting direct posting.
Message   : `FIN-409-NOT-POSTABLE-ACCOUNT` — ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" ·
            en: "The target account does not accept direct posting"
Scope     : CREATE · Field : accountId per line · kind BUSINESS_RULE · when submit
Validation shape : the account picker filters to `isLeafFl = true` and `isActiveFl = true`
            through API-FIN-001's own filters, so the common case never reaches the server as
            a failure; the server's refusal is still routed to the offending line, because the
            account's state may have changed since the picker loaded.
### F3-VALIDATION — RULE-FIN-008      traces=REQ-FIN-020,AC-FIN-020
Statement : the entry's period must be Open at the moment of posting.
Message   : `FIN-409-PERIOD-NOT-OPEN` — ar: "الفترة المستهدفة غير مفتوحة" ·
            en: "The target period is not open"
Scope     : CREATE · Field : periodId · kind BUSINESS_RULE · when submit
Validation shape : **server-side only at the moment that matters.** The period select shows
            each period's state and defaults to an Open one, but the check is at post time, not
            build time (RULE-FIN-008's own words), so a period that closed while the entry was
            being typed is caught by the server and its message routed to the period field.
### F3-VALIDATION — RULE-FIN-009      traces=REQ-FIN-021,AC-FIN-021
Statement : a cited dimension value must belong to its stated dimension and be active.
Message   : `FIN-409-INVALID-DIMENSION` — ar: "قيمة البُعد غير صالحة" ·
            en: "The dimension value is invalid"
Scope     : CREATE · Field : the line's dimension pair · kind LOOKUP_VALID + BUSINESS_RULE ·
            when submit
Validation shape : the value select is loaded from API-FIN-008 filtered by the chosen
            dimension and by `isActiveFl`, so it cannot offer a value of another dimension;
            activity can still change under it, and the server's refusal names the line.
### F3-VALIDATION — RULE-FIN-017      traces=REQ-FIN-014,AC-FIN-014
Statement : the submitted period must belong to the submitted fiscal year, and the document
            date must fall inside that period.
Message   : from the catalog codes `FIN-400-PERIOD-NOT-IN-YEAR` and
            `FIN-400-DOCDATE-OUTSIDE-PERIOD` —
            ar: "الفترة المحددة لا تتبع السنة المالية المحددة، أو تاريخ المستند خارج نطاقها" ·
            en: "The selected period does not belong to the selected fiscal year, or the
            document date falls outside it"
Scope     : CREATE · Field : fiscalYearId, periodId, docDate · kind DATE_RANGE +
            BUSINESS_RULE · when submit
Validation shape : the period select is narrowed to the chosen year and the date picker is
            bounded by the selected period's own `startDate` and `endDate`, both of which the
            period row already carries — so the pairing is expressible client-side and the two
            catalog codes are routed inline to the fields they name.
### F3-VALIDATION — RULE-FIN-016      traces=REQ-FIN-016,AC-FIN-016
Statement : a POSTED entry may not be edited or deleted; correction is only through a reversal.
Message   : the rule's own text — ar: "القيد المُرحَّل مقفل؛ التصحيح فقط عبر العكس" ·
            en: "A posted entry is locked; correction is only through a reversal"
Scope     : ALL · Field : the whole entry · kind BUSINESS_RULE · not a form check at all
Validation shape : there is **no form to validate**: a posted entry opens read-only with no
            edit and no delete affordance anywhere on it, and the rule is expressed by the
            absence of the path rather than by a message on a control that would refuse.
### F3-VALIDATION — RULE-FIN-013      traces=REQ-FIN-030,AC-FIN-030
Statement : a reverse action is rejected on an entry that is not POSTED.
Message   : `FIN-409-NOT-POSTED` — ar: "لا يمكن عكس قيد غير مُرحَّل" ·
            en: "A non-posted entry cannot be reversed" — and `FIN-409-ALREADY-REVERSED` for
            an entry that already carries a reversal link
Scope     : the reverse action · Field : none (a row action) · kind BUSINESS_RULE · when submit
Validation shape : the affordance is drawn only on an entry whose `statusCode` is POSTED and
            whose `reversalEntryId` is absent, both of which the response carries; the server's
            refusal is still shown, because the row may be stale.
Business-code fields: `docNo` is system-generated and displayed read-only; the form never
composes or predicts it.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE, or without the reverse action, receives
`FIN-403-FORBIDDEN` on submit and the page shows the localized forbidden message; no field is
pre-emptively disabled, because neither permission is readable (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-006:END -->
