<!-- source: PHASE:F1 / SUB:F1-SCR-MDL-001 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, SCR-MDL-001, UXD-MDL-001 -->
<!-- SUB:F1-SCR-MDL-001:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001 -->
### F1 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F1-MODEL — ENT-MDL-001 — نوع اللوكب / LookupType
Source DTO   : `LookupTypeResponse` (read) · `LookupTypeCreateRequest` · `LookupTypeUpdateRequest`
  lookupTypePk    : number · read-only (PK) · system-only
  key             : string · maxLength 80 · required on create, **read-only on edit** —
                    RULE-MDL-003, and `LookupTypeUpdateRequest` does not carry it
  ownerModuleCode : string · maxLength 10 · required on create, **read-only on edit** — not in
                    the update request; its valid set is the security module's registry
                    (UXD-MDL-001), and it is held as a plain string, never an enum
  nameAr          : string · required · maxLength 150
  nameEn          : string · required · maxLength 150
  isActiveFl      : boolean · read-only — flipped only by API-MDL-004 (ADR-MDL-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — ENT-MDL-002 — قيمة اللوكب / LookupValue
Source DTO   : `LookupValueResponse` (read) · `LookupValueCreateRequest` ·
               `LookupValueUpdateRequest` · `LookupValueReorderRequest`
  lookupValuePk : number · read-only (PK) · system-only
  lookupTypeId  : number · read-only — the path id of API-MDL-006, taken from the selected
                  parent, never typed
  code          : string · maxLength 50 · required on create, **read-only on edit** — the
                  update request does not carry it; unique within its type (RULE-MDL-002)
  nameAr        : string · required · maxLength 150
  nameEn        : string · required · maxLength 150
  sortOrder     : number · required on create **and** on update — and the same field the
                  reorder writes, through `LookupValueReorderRequest { orderedValueIds[] }`
  isActiveFl    : boolean · read-only — flipped only by API-MDL-008 (ADR-MDL-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-SCREEN — SCR-MDL-001
Search model : master filters — key : string · LIKE · ownerModuleCode : string · EXACT (from
               the UXD-MDL-001 hook) · isActiveFl : boolean · EXACT
               detail filters — code : string · LIKE · lookupTypeId : number · EXACT (set from
               the selected parent, not typed)
               paging + sort — page, size, sortField, sortDirection, inside each of
               `LookupTypeSearchRequest` and `LookupValueSearchRequest` per `Page<T>`
Form model   : type, create — key, ownerModuleCode, nameAr, nameEn (all required)
               type, edit   — nameAr, nameEn (required); key and ownerModuleCode read-only
               value, create — code, nameAr, nameEn, sortOrder (all required)
               value, edit   — nameAr, nameEn, sortOrder (required); code read-only
               reorder       — the ordered list of value ids, not a per-row edit
               excluded system fields: both PKs, lookupTypeId, both isActiveFl, the audit fields
Container    : TREE_MASTER_DETAIL
`isActiveFl` is modelled read-only at both levels: it is in the response and in no write
request, so a form that offered it would be offering a field the server ignores (ADR-MDL-006).
<!-- SUB:F1-SCR-MDL-001:END -->
