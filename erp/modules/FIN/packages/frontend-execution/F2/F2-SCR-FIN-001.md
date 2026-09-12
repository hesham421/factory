<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-001 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-001, AC-FIN-002, AC-FIN-003, AC-FIN-045, API-FIN-001, API-FIN-002, API-FIN-003, API-FIN-004, REQ-FIN-001, REQ-FIN-002, REQ-FIN-003, REQ-FIN-045, SCR-FIN-001, UXD-FIN-001, UXD-FIN-002 -->
<!-- SUB:F2-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F2-QUERY — API-FIN-001            traces=API-FIN-001,REQ-FIN-001
POST `/api/v1/fin/accounts/search` · request `AccountSearchRequest` { filters[], sortField,
sortDirection, page, size } · response `Page<AccountResponse>` · kind **read query**
(a POST that mutates nothing)
Cache key    : `[accounts, filters]` where `filters` is the whole request object — code,
               nameAr/nameEn, accountTypeCode, isActiveFl, sortField, sortDirection **and
               page, size**. Page and page size live inside the filter object; they are never
               independent state.
Errors       : `FIN-400-INVALID-SORT` (400) → inline on the sort control ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message ·
               server error (500) → generic message
Loading      : LOCAL — the SRS states nothing about this call being slow, so no GLOBAL indicator
Cache policy : defaults
Invalidation : this key is refreshed by every mutation below
### F2-QUERY — API-FIN-002            traces=API-FIN-002,REQ-FIN-001,REQ-FIN-002
POST `/api/v1/fin/accounts` · request `AccountCreateRequest` { code, nameAr, nameEn,
accountTypeCode, natureCode, parentAccountId?, isLeafFl? } · response `AccountResponse` ·
kind **mutation**
Errors       : `FIN-409-ACCOUNT-DUP` (409) → inline on `code` ·
               `FIN-409-PARENT-NOT-LEAF-ELIGIBLE` (409) → user message for RULE-FIN-001,
               ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" ·
               en: "An account with sub-accounts cannot accept direct posting" ·
               `FIN-404-ACCOUNT` (404) → inline on `parentAccountId` ·
               `FIN-400-INVALID-LOOKUP` (400) → inline on the offending code field ·
               validation (400) → inline per `error.fieldErrors[].field` ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[accounts, *]`
### F2-QUERY — API-FIN-003            traces=API-FIN-003,REQ-FIN-002
PUT `/api/v1/fin/accounts/{id}` · request `AccountUpdateRequest` { nameAr, nameEn, isLeafFl } ·
response `AccountResponse` · kind **mutation**
Errors       : `FIN-409-HAS-CHILDREN` (409) → user message for RULE-FIN-001, the same ar/en
               pair as above, shown on the `isLeafFl` control ·
               `FIN-404-ACCOUNT` (404) → user message · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[accounts, *]`
### F2-QUERY — API-FIN-004            traces=API-FIN-004,REQ-FIN-003
PUT `/api/v1/fin/accounts/{id}/deactivate` · no request body · response `AccountResponse`
(isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-ACCOUNT` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[accounts, *]`
### F2-LOOKUP — ACCOUNT_TYPE
Key `ACCOUNT_TYPE` · one shared hook, resolved through UXD-FIN-001 · options shape
{ code, labelAr, labelEn } · long-lived cache (the values change only when the lookup module's
data does) · shared with SCR-FIN-009, SCR-FIN-010 and SCR-FIN-011, never duplicated per screen
### F2-LOOKUP — DEBIT_CREDIT
Key `DEBIT_CREDIT` · one shared hook, resolved through UXD-FIN-002 · options shape
{ code, labelAr, labelEn } · long-lived cache · shared with every screen that shows a direction
or a nature
### F2-SCREEN-INIT — SCR-FIN-001
Permission read : `FIN_ACCOUNTS` present in the caller's effective menu → VIEW (ADR-FIN-005).
                  CREATE and UPDATE are not readable from any published endpoint; their
                  affordances render and the server's 403 is the authority.
Lookups used    : ACCOUNT_TYPE (form + filter), DEBIT_CREDIT (form)
Entity by id    : none published — the form hydrates from the row the `[accounts, filters]`
                  query already holds (ADR-FIN-006), so opening an account performs no second
                  read and an invalidation re-reads through the same key
### F2-FACADE — SCR-FIN-001
Composes     : API-FIN-001 (list) · API-FIN-002, API-FIN-003, API-FIN-004 (mutations) · the
               ACCOUNT_TYPE and DEBIT_CREDIT hooks
State it owns: the tree derived from the query's rows (never a copy of them), the selected
               account id (from the route param), the filter object including page and size,
               and a derived loading flag over the calls in flight
Operations   : createAccount · updateAccount · deactivateAccount (confirmation first, naming
               that history is retained)
Components use the facade only; the facade uses the declared queries only.

<!-- SUB:F2-SCR-FIN-001:END -->
