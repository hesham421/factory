<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-005 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-025, AC-FIN-026, API-FIN-015, API-FIN-016, API-FIN-017, API-FIN-037, REQ-FIN-025, REQ-FIN-026, SCR-FIN-005, UXD-FIN-010 -->
<!-- SUB:F1-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F1 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F1-MODEL — ENT-FIN-013 — قاعدة توزيع / AllocationRule
Source DTO   : `AllocationRuleResponse` (read) · `AllocationRuleCreateRequest` (write)
  allocationRulePk : number · read-only (PK) · system-only
  nameAr, nameEn   : string · required on create · maxLength 150
  sourceAccountId  : number · required on create — the balance being distributed
  isActiveFl       : boolean · read-only — flipped only by API-FIN-037
  targetCount      : number · read-only · derived by the server from the targets it returns
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-014 — هدف التوزيع / AllocationTarget
Source DTO   : `AllocationTargetResponse` (read) · `AllocationTargetCreateRequest` (write)
  allocationTargetPk   : number · read-only (PK) · system-only
  allocationRuleId     : number · read-only · system-only
  lineNo               : number · read-only · system-assigned
  targetAccountId      : number · required
  dimensionValueId     : number · optional — ONE per target
  distributionTypeCode : string · required · maxLength 15 · lookup — `DISTRIBUTION_TYPE`
                         (UXD-FIN-010)
  distributionValue    : number · optional in the DTO; required unless the distribution type
                         is REMAINDER (SRS ENT-FIN-014)
  isRemainderFl        : boolean · optional in the DTO, governed by RULE-FIN-003
### F1-SCREEN — SCR-FIN-005
Search model : filters — nameAr/nameEn : string · LIKE · sourceAccountId : number · EXACT ·
               isActiveFl : boolean · EXACT
               paging + sort inside `AllocationRuleSearchRequest`
Form model   : create — nameAr, nameEn, sourceAccountId, targets[] (required)
               targets[] — targetAccountId, distributionTypeCode (required); dimensionValueId,
                           distributionValue, isRemainderFl (optional per the DTO, constrained
                           by RULE-FIN-003 and by the distribution type)
               excluded system fields: every PK, allocationRuleId, lineNo, isActiveFl,
               targetCount, audit fields
               read-only on edit: not applicable — no update endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The rule and its targets are ONE submission. No model holds a computed allocation amount: the
distribution is produced by the server at run time from the source account's balance at that
moment, and the remainder target's amount is a difference RULE-FIN-010 computes, never a
percentage the client could anticipate.

<!-- SUB:F1-SCR-FIN-005:END -->
