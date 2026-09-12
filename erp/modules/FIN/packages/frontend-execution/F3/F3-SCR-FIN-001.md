<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-001 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-001, AC-FIN-002, AC-FIN-003, API-FIN-001, API-FIN-002, API-FIN-003, API-FIN-004, REQ-FIN-001, REQ-FIN-002, REQ-FIN-003, SCR-FIN-001, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F3-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F3 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

Validation timing for this form: **on blur for the unique code, on submit for the rest**
(declared once for the whole form).
### F3-FIELD — SCR-FIN-001 (create)
code            · REQUIRED · LENGTH (maxLength 30, from `AccountCreateRequest`) ·
                  UNIQUE_CHECK · when blur
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 200) · when submit
accountTypeCode · REQUIRED · LOOKUP_VALID (`ACCOUNT_TYPE`, UXD-FIN-001) · LENGTH (20) · when submit
natureCode      · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
parentAccountId · optional · when submit
isLeafFl        · optional · BUSINESS_RULE (RULE-FIN-001) · when submit
### F3-FIELD — SCR-FIN-001 (edit)
code, accountTypeCode, natureCode, parentAccountId · read-only — not inputs at all;
                  `AccountUpdateRequest` does not carry them
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 200) · when submit
isLeafFl        · REQUIRED · BUSINESS_RULE (RULE-FIN-001) · when submit
UNIQUE_CHECK    : async, on blur, via `API-FIN-001` with an EQUALS filter on `code`; on edit
                  the field is read-only so the check does not run at all. A failure never
                  blocks submit on its own — the authority is the server's
                  `FIN-409-ACCOUNT-DUP`, routed inline to the same field.
LOOKUP_VALID    : the value must be one the runtime-loaded option list contains; no static
                  list is written anywhere, and an empty option list leaves the field
                  unsatisfiable rather than falling back to a hardcoded set (ADR-FIN-004).
### F3-VALIDATION — RULE-FIN-001      traces=REQ-FIN-002,AC-FIN-002
Statement : The system shall prevent an account with any child account from being marked as
            accepting direct posting.
Message   : from the catalog codes `FIN-409-PARENT-NOT-LEAF-ELIGIBLE` (on create) and
            `FIN-409-HAS-CHILDREN` (on update) —
            ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" ·
            en: "An account with sub-accounts cannot accept direct posting"
Scope     : CREATE and UPDATE
Field     : isLeafFl · kind BUSINESS_RULE · when submit
Validation shape : the client knows, from the tree it already renders, whether the selected
            node has children, and uses that to explain the constraint beside the control
            before submit. It does **not** decide the outcome: the tree is a page of search
            results and may not hold every child, so the submission goes through and the
            catalog message is what the user is shown on refusal. The message is read from the
            catalog, never composed here.
Business-code fields: `code` is the chart-of-accounts code and is displayed read-only after
create; it is never regenerated or re-derived on the client.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `FIN-403-FORBIDDEN` on submit
and the form shows the localized forbidden message; fields are not pre-emptively disabled,
because the permission is not readable (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-001:END -->
