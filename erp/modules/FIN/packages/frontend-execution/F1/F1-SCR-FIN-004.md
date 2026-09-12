<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-004 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-022, AC-FIN-023, AC-FIN-024, API-FIN-012, API-FIN-013, API-FIN-014, API-FIN-036, REQ-FIN-022, REQ-FIN-023, REQ-FIN-024, SCR-FIN-004, UXD-FIN-002, UXD-FIN-011, UXD-FIN-012 -->
<!-- SUB:F1-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F1 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F1-MODEL — ENT-FIN-011 — قالب متكرر/عكسي / RecurringTemplate
Source DTO   : `RecurringTemplateResponse` (read) · `RecurringTemplateCreateRequest` (write)
  recurringTemplatePk : number · read-only (PK) · system-only
  nameAr, nameEn      : string · required on create · maxLength 150
  scheduleTypeCode    : string · required on create · maxLength 15 · lookup —
                        `RECURRING_SCHEDULE_TYPE` (UXD-FIN-011)
  frequencyCode       : string · optional in the DTO · maxLength 15 · lookup —
                        `RECURRING_FREQUENCY` (UXD-FIN-012); required when the schedule type
                        is RECURRING (SRS ENT-FIN-011), which the server answers with
                        `FIN-400-MISSING-FREQUENCY`
  startDate           : date · required on create
  nextRunDate         : date · read-only · system-maintained — it advances after each run
  endDate             : date · optional on create
  isActiveFl          : boolean · read-only — flipped only by API-FIN-036
  lineCount           : number · read-only · derived by the server from the lines it returns
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-012 — سطر القالب المتكرر / RecurringTemplateLine
Source DTO   : `RecurringTemplateLineResponse` (read) · `RecurringTemplateLineCreateRequest`
  recurringTemplateLinePk : number · read-only (PK) · system-only
  recurringTemplateId     : number · read-only · system-only
  lineNo                  : number · read-only · system-assigned
  accountId               : number · required
  amount                  : number · required — always positive; the direction carries the sign
  directionCode           : string · required · maxLength 10 · lookup — `DEBIT_CREDIT`
                            (UXD-FIN-002)
  dimensionValueId        : number · optional — ONE per line, the §9.3.3 simplification
  createdAt               : date-time · read-only · system-only
### F1-SCREEN — SCR-FIN-004
Search model : filters — nameAr/nameEn : string · LIKE · scheduleTypeCode : string · EXACT ·
               isActiveFl : boolean · EXACT
               paging + sort inside `RecurringTemplateSearchRequest`
Form model   : create — nameAr, nameEn, scheduleTypeCode, startDate, lines[] (required);
                        frequencyCode (required when RECURRING), endDate (optional)
               lines[] — accountId, amount, directionCode (required); dimensionValueId (optional)
               excluded system fields: every PK, recurringTemplateId, lineNo, nextRunDate,
               isActiveFl, lineCount, createdAt, audit fields
               read-only on edit: not applicable — no update endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The template and its lines are ONE submission — `RecurringTemplateCreateRequest` carries
`lines[]` — unlike SCR-FIN-003, whose lines are separate calls. `lineCount` is modelled as
read-only and never computed on the client, because the server derives it from the list it
returns.

<!-- SUB:F1-SCR-FIN-004:END -->
