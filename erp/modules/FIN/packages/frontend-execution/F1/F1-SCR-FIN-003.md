<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-003 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-007, AC-FIN-008, AC-FIN-009, API-FIN-009, API-FIN-010, API-FIN-011, API-FIN-034, REQ-FIN-007, REQ-FIN-008, REQ-FIN-009, SCR-FIN-003, UXD-FIN-002, UXD-FIN-007, UXD-FIN-008, UXD-FIN-009, UXD-FIN-010 -->
<!-- SUB:F1-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F1 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F1-MODEL — ENT-FIN-009 — قاعدة نوع الحدث / EventTypeRule
Source DTO   : `EventTypeRuleResponse` (read) · `EventTypeRuleCreateRequest` (write)
  eventTypeRulePk : number · read-only (PK) · system-only
  eventTypeCode   : string · required on create · maxLength 50 · lookup —
                    `ACCOUNTING_EVENT_TYPE` code held as a string (UXD-FIN-007)
  nameAr, nameEn  : string · required on create · maxLength 150
  isActiveFl      : boolean · read-only — flipped only by API-FIN-034
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-010 — سطر القاعدة / RuleLine
Source DTO   : `RuleLineResponse` (read) · `RuleLineCreateRequest` (write)
  ruleLinePk                : number · read-only (PK) · system-only
  eventTypeRuleId           : number · read-only — the path id of API-FIN-011
  lineNo                    : number · read-only · system-assigned
  accountDerivationTypeCode : string · required · maxLength 20 · lookup —
                              `ACCOUNT_DERIVATION_TYPE` (UXD-FIN-008)
  accountDerivationValue    : string · required — read per the derivation type: a constant
                              account code, an event field name, or a mapping-set key
  amountSourceTypeCode      : string · required · maxLength 20 · lookup — `AMOUNT_SOURCE_TYPE`
                              (UXD-FIN-009)
  amountSourceValue         : string · optional in the DTO; required unless the amount source
                              type is REMAINDER (SRS ENT-FIN-010)
  directionCode             : string · required · maxLength 10 · lookup — `DEBIT_CREDIT`
                              (UXD-FIN-002)
  distributionTypeCode      : string · required · maxLength 15 · lookup — `DISTRIBUTION_TYPE`
                              (UXD-FIN-010)
  isRemainderFl             : boolean · optional in the DTO, governed by RULE-FIN-003
  createdAt                 : date-time · read-only · system-only
### F1-SCREEN — SCR-FIN-003
Search model : filters — eventTypeCode : string · EXACT (from the UXD-FIN-007 hook) ·
               isActiveFl : boolean · EXACT
               paging + sort inside `EventTypeRuleSearchRequest`
Form model   : rule — eventTypeCode, nameAr, nameEn (required, create only)
               line — accountDerivationTypeCode, accountDerivationValue, amountSourceTypeCode,
                      directionCode, distributionTypeCode (required); amountSourceValue
                      (required unless REMAINDER); isRemainderFl (boolean)
               excluded system fields: both PKs, eventTypeRuleId, lineNo, isActiveFl, createdAt
               read-only on edit: not applicable — neither the rule nor the line has an update
               endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The rule's lines are NOT part of the create request: `EventTypeRuleCreateRequest` carries the
header alone and each line is a separate API-FIN-011 call. The form model reflects that — a
rule is created first and its lines added to it — rather than promising a single submission
the surface does not accept. Five lookup fields, five strings, no enum.

<!-- SUB:F1-SCR-FIN-003:END -->
