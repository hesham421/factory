<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-002 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-004, AC-FIN-005, AC-FIN-006, API-FIN-005, API-FIN-006, API-FIN-007, API-FIN-008, API-FIN-035, REQ-FIN-004, REQ-FIN-005, REQ-FIN-006, SCR-FIN-002 -->
<!-- SUB:F3-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F3 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

Validation timing for this form: **on blur for the unique codes, on submit for the rest**.
### F3-FIELD — SCR-FIN-002 (dimension, create)
code           · REQUIRED · LENGTH (maxLength 30) · UNIQUE_CHECK · when blur
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-FIN-002 (dimension value, create)
code           · REQUIRED · LENGTH (maxLength 30) · UNIQUE_CHECK (within the selected
                 dimension — RULE-FIN-002) · when blur
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder      · REQUIRED · when submit
UNIQUE_CHECK   : async, on blur — the dimension via `API-FIN-005` with an EQUALS filter on
                 `code`; the value via `API-FIN-008` with EQUALS filters on both `dimensionId`
                 and `code`, so the scope of the check is the same scope the rule has. Neither
                 blocks submit on its own: the server's `FIN-409-DIMENSION-DUP` and
                 `FIN-409-DIMVALUE-DUP` are the authority, routed inline to `code`.
### F3-VALIDATION — RULE-FIN-002      traces=REQ-FIN-006,AC-FIN-006
Statement : The system shall reject a dimension value whose code already exists under the same
            dimension.
Message   : from the catalog code `FIN-409-DIMVALUE-DUP` —
            ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" ·
            en: "This code is already used within this dimension"
Scope     : CREATE
Field     : code (of the value) · kind UNIQUE_CHECK · when blur, and again on submit by the server
Validation shape : uniqueness is scoped to the parent dimension, never globally — a code used
            under one dimension is legitimate under another, and a global check would reject a
            value the server accepts. Written with `zod` + `react-hook-form`, with the async
            check bound to the selected parent id.
Business-code fields: none of these codes is platform-numbered; both are client-defined and
are read-only after create because neither resource has an update endpoint.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit and the form shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-002:END -->
