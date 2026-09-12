<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-001 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-001, AC-FIN-002, AC-FIN-003, API-FIN-001, API-FIN-002, API-FIN-003, API-FIN-004, REQ-FIN-001, REQ-FIN-002, REQ-FIN-003, SCR-FIN-001, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F1-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F1 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F1-MODEL — ENT-FIN-001 — الحساب / Account
Source DTO   : `AccountResponse` (read) · `AccountCreateRequest` · `AccountUpdateRequest` (write)
  accountPk            : number · read-only (PK) · system-only
  code                 : string · maxLength 30 · required on create, **read-only on edit**
                         (`AccountUpdateRequest` does not carry it — the chart code is immutable)
  nameAr               : string · required · maxLength 200
  nameEn               : string · required · maxLength 200
  accountTypeCode      : string · required on create · maxLength 20 · lookup — `ACCOUNT_TYPE`
                         code held as a string (UXD-FIN-001); **read-only on edit**, absent
                         from the update request
  natureCode           : string · required on create · maxLength 10 · lookup — `DEBIT_CREDIT`
                         code held as a string (UXD-FIN-002); **read-only on edit**
  parentAccountId      : number · optional on create (omitted for a root) · **read-only on edit**
  isLeafFl             : boolean · optional on create, required on update — the only field the
                         update request carries besides the two names
  isActiveFl           : boolean · read-only — flipped only by API-FIN-004
  isRetainedEarningsFl : boolean · read-only · system-only — the published DTO states it is
                         never settable through the account APIs
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-SCREEN — SCR-FIN-001
Search model : filters — code : string · LIKE · nameAr/nameEn : string · LIKE ·
               accountTypeCode : string · EXACT (the code, from the shared UXD-FIN-001 hook) ·
               isActiveFl : boolean · EXACT
               paging + sort — page, size, sortField, sortDirection, all inside the one
               `AccountSearchRequest` object per `Page<T>`
Form model   : create — code, nameAr, nameEn, accountTypeCode, natureCode (required),
                        parentAccountId, isLeafFl (optional)
               edit   — nameAr, nameEn, isLeafFl (required); every other field read-only
               excluded system fields: accountPk, isActiveFl, isRetainedEarningsFl, audit fields
Container    : TREE_MASTER_DETAIL
The tree is built on the client from `parentAccountId` over the rows the search returns; no
endpoint returns a nested tree and none is invented. Nothing is modelled that the api-docs do
not return, and no lookup is modelled as an enum — both code fields are plain strings.

<!-- SUB:F1-SCR-FIN-001:END -->
