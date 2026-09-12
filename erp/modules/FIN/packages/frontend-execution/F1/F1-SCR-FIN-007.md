<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-007 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-031, AC-FIN-032, AC-FIN-033, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-037, AC-FIN-038, API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026, API-FIN-027, API-FIN-033, REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038, SCR-FIN-007, UXD-FIN-003, UXD-FIN-004 -->
<!-- SUB:F1-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F1 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F1-MODEL — ENT-FIN-007 — السنة المالية / FiscalYear
Source DTO   : `FiscalYearResponse` (read) · `FiscalYearCreateRequest` (write)
  fiscalYearPk : number · read-only (PK) · system-only
  code         : string · required on create · maxLength 10
  startDate    : date · required on create
  endDate      : date · required on create
  periodCount  : number · required on create — an input to generation, returned on the response
  statusCode   : string · read-only · lookup — `FISCAL_YEAR_STATUS` (UXD-FIN-004)
  isActiveFl   : boolean · read-only
  periods      : FiscalPeriodResponse[] · read-only — the generated periods, returned with the
                 year by API-FIN-023
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-008 — الفترة المحاسبية / FiscalPeriod
Source DTO   : `FiscalPeriodResponse` (read) — no write DTO: a period is generated, never typed
  fiscalPeriodPk : number · read-only (PK) · system-only
  fiscalYearId   : number · read-only — also the field year ids are discovered from, since no
                   fiscal-year search is published (ADR-FIN-006)
  periodNo       : number · read-only · generated
  nameAr, nameEn : string · read-only · generated (month names for a twelve-period year,
                   "الفترة N" / "Period N" otherwise)
  startDate, endDate : date · read-only · generated
  statusCode     : string · read-only · lookup — `PERIOD_STATE` (UXD-FIN-003); changed only by
                   API-FIN-024, API-FIN-025, API-FIN-026
  closedBy       : string · read-only — the approving principal, set at hard-close
  closedAt       : date-time · read-only — set at hard-close
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — YearEndCloseResponse (the year-end close result)
  closingEntry : JournalEntryResponse · read-only — the closing entry, modelled by the
                 SCR-FIN-006 entry model above and rendered through the same components
  openingEntry : JournalEntryResponse · read-only — the next year's opening entry
### F1-SCREEN — SCR-FIN-007
Search model : filters — fiscalYearId : number · EXACT · statusCode : string · EXACT — both
               OPTIONAL; omitting the year is a legitimate "all periods" request
               paging + sort inside `FiscalPeriodSearchRequest`
Form model   : create year — code, startDate, endDate, periodCount (all required)
               period actions — no form: open, soft-close and hard-close are path-id calls
               with no body
               excluded system fields: every PK, both statusCode, isActiveFl, periodNo, the
               generated names and dates, closedBy, closedAt, audit fields
               read-only on edit: not applicable — neither resource has an update endpoint
Container    : TREE_MASTER_DETAIL
The year list is derived from the distinct `fiscalYearId` of the period rows plus the year
API-FIN-023 returns on creation; no year-list model is invented on top of an endpoint that
does not exist.

<!-- SUB:F1-SCR-FIN-007:END -->
