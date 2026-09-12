<!-- source: PHASE:F3 / SUB:F3-SCR-MDL-001 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, SCR-MDL-001, UXD-MDL-001 -->
<!-- SUB:F3-SCR-MDL-001:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001 -->
### F3 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

Validation timing for this screen: **on blur for the unique key and code, on submit for the
rest** — declared once, and it holds for both the type form and the value form.
### F3-FIELD — SCR-MDL-001 (type, create)
key             · REQUIRED · LENGTH (maxLength 80, from `LookupTypeCreateRequest`) ·
                  UNIQUE_CHECK · when blur
ownerModuleCode · REQUIRED · LENGTH (maxLength 10) · BUSINESS_RULE (RULE-MDL-001) · when submit
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-MDL-001 (type, edit)
key, ownerModuleCode · read-only — not inputs at all; `LookupTypeUpdateRequest` carries neither
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-MDL-001 (value, create)
code            · REQUIRED · LENGTH (maxLength 50) · UNIQUE_CHECK (within the selected type —
                  RULE-MDL-002) · when blur
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder       · REQUIRED · when submit
### F3-FIELD — SCR-MDL-001 (value, edit)
code            · read-only — `LookupValueUpdateRequest` does not carry it
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder       · REQUIRED · when submit
UNIQUE_CHECK    : async, on blur — the type's `key` via `API-MDL-001` with an EQUALS filter;
                  the value's `code` via `API-MDL-005` with EQUALS filters on **both**
                  `lookupTypeId` and `code`, so the check's scope is the rule's scope. Neither
                  blocks submit on its own: the server's `MDL-409-TYPE-DUP` and
                  `MDL-409-VALUE-DUP` are the authority, routed inline to the same field. On
                  edit neither field is an input, so neither check runs.
### F3-VALIDATION — RULE-MDL-001      traces=REQ-MDL-002,AC-MDL-002
Statement : The system shall reject a lookup type registration whose owner module code has no
            ModuleRegistry row in the Security module.
Message   : from the catalog code `MDL-409-MODULE-NOT-REGISTERED` —
            ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" ·
            en: "The owning module is not registered in the Security module"
Scope     : CREATE
Field     : ownerModuleCode · kind BUSINESS_RULE · when submit
Validation shape : the control is a **select over the registered module codes** loaded through
            UXD-MDL-001, so the common case cannot be typed wrong at all; the validator asserts
            that the submitted value is one the runtime-loaded list contains, never that it is
            one of a static set. The server remains the authority — a module deregistered
            between load and submit is caught there — and the catalog message routes to this
            field. The rule's `Data source` is another module's registry, read SOFT at the
            application layer, so the client cannot decide it alone and does not try.
### F3-VALIDATION — RULE-MDL-002      traces=REQ-MDL-007,AC-MDL-007
Statement : The system shall reject a lookup value whose code already exists under the same
            lookup type.
Message   : from the catalog code `MDL-409-VALUE-DUP` —
            ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" ·
            en: "This code is already used within this type"
Scope     : CREATE
Field     : code (of the value) · kind UNIQUE_CHECK · when blur, and again on submit by the server
Validation shape : uniqueness is scoped to the parent type, never globally — the same code
            under another type is legitimate, and a global check would reject a value the
            server accepts. The async check is bound to the selected parent id.
### F3-VALIDATION — RULE-MDL-003      traces=REQ-MDL-003,AC-MDL-003
Statement : The system shall prevent editing a lookup type's key after creation.
Message   : the rule's own text — ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" ·
            en: "A lookup type's key cannot be changed after creation"
Scope     : UPDATE
Field     : key · kind BUSINESS_RULE · not a form check at all
Validation shape : there is **nothing to validate**: `key` is not an input on edit, because
            `LookupTypeUpdateRequest` does not carry it. The rule is expressed by the absence
            of the field rather than by a message on a control that would refuse. The form
            still *states* the rule beside the read-only key, so an editor learns why it cannot
            be changed instead of discovering a disabled control with no explanation.
### F3-VALIDATION — RULE-MDL-004      traces=REQ-MDL-004,AC-MDL-004
Statement : While a lookup type is inactive, the system shall exclude its values from consumer
            reads.
Message   : the rule's own text — ar: "هذا النوع معطّل حاليًا" ·
            en: "This lookup type is currently inactive"
Scope     : the deactivate action (API-MDL-004)
Field     : none — a row action · kind BUSINESS_RULE · when submit
Validation shape : **not a validation this form performs at all** — it is a consequence the
            deactivate confirmation names before the act: every consuming module stops
            receiving this type's values. The rule's text is shown as the state label on an
            inactive type row, so the same words explain the row and the warning. Nothing on
            this screen is hidden by it: the manager's value list (API-MDL-005) still shows the
            values, which is the difference between this screen and a consumer.
Business-code fields: `key` and `code` are both client-chosen strings, not platform-numbered,
and both are read-only after create (per the two update DTOs). Neither is generated or
predicted on the client.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE, UPDATE or DELETE receives `ACCESS_DENIED`
on submit and the form shows the localized forbidden message; fields are not pre-emptively
disabled, because no published endpoint tells the screen which actions the caller holds.
<!-- SUB:F3-SCR-MDL-001:END -->
