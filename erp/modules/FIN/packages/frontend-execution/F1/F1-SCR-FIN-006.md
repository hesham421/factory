<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-006 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-010, AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-014, AC-FIN-015, AC-FIN-016, AC-FIN-017, AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-027, AC-FIN-028, AC-FIN-029, AC-FIN-030, API-FIN-018, API-FIN-019, API-FIN-020, API-FIN-021, API-FIN-022, REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, SCR-FIN-006, UXD-FIN-002, UXD-FIN-005, UXD-FIN-006 -->
<!-- SUB:F1-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F1 · SCR-FIN-006 — قيود اليومية / Journal entries

### F1-MODEL — ENT-FIN-004 — رأس قيد اليومية / JournalEntry
Source DTO   : `JournalEntryResponse` (read) · `JournalEntryCreateRequest` (write)
  journalEntryPk  : number · read-only (PK) · system-only
  docNo           : string · read-only · system-only — generated on first save, immutable after
  docDate         : date · required on create
  fiscalYearId    : number · required on create — B3 lists it as neither an input nor a system
                    field; the published request requires it and RULE-FIN-017 reads it
                    (ADR-FIN-008)
  periodId        : number · required on create
  journalTypeCode : string · required on create · maxLength 20 · lookup — `JOURNAL_TYPE`
                    (UXD-FIN-005). On this form it is the fixed value `MANUAL`, held in the
                    model and rendered read-only (ADR-FIN-008)
  statusCode      : string · read-only · lookup — `JOURNAL_STATUS` (UXD-FIN-006); set by the
                    posting pipeline, never by a form
  eventReference  : string · read-only — present only on an event-sourced entry
  originalEntryId : number · read-only — set on a reversal
  reversalEntryId : number · read-only — set on the original once reversed
  descriptionAr, descriptionEn : string · optional on create
  postedAt        : date-time · read-only · system-only
  lineCount       : number · read-only · derived
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-005 — سطر قيد اليومية / JournalLine
Source DTO   : `JournalLineResponse` (read) · `JournalLineCreateRequest` (write)
  journalLinePk  : number · read-only (PK) · system-only
  journalEntryId : number · read-only · system-only
  lineNo         : number · read-only · system-assigned
  accountId      : number · required
  amount         : number · required — always positive
  directionCode  : string · required · maxLength 10 · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
  isRemainderFl  : boolean · read-only on this screen — the engine sets it on a built entry;
                   `JournalLineCreateRequest` does not carry it
  descriptionAr, descriptionEn : string · optional
  createdAt      : date-time · read-only · system-only
### F1-MODEL — ENT-FIN-006 — بُعد سطر القيد / JournalLineDimension
Source DTO   : `JournalLineDimensionResponse` (read) · `JournalLineDimensionCreateRequest`
  journalLineDimensionPk, journalLineId : number · read-only · system-only
  dimensionId      : number · required when a dimension is used
  dimensionValueId : number · required with it
### F1-SCREEN — SCR-FIN-006
Search model : filters — docNo : string · LIKE · docDate : DATE_RANGE · periodId : number ·
               EXACT · statusCode : string · EXACT · journalTypeCode : string · EXACT
               paging + sort inside `JournalEntrySearchRequest`; page and size are part of the
               same object and never independent state
Form model   : create — docDate, fiscalYearId, periodId, journalTypeCode (fixed `MANUAL`,
                        read-only), lines[] (required); descriptionAr, descriptionEn (optional)
               lines[] — accountId, amount, directionCode (required); descriptionAr,
                         descriptionEn, dimensions[] (optional)
               dimensions[] — dimensionId, dimensionValueId (both required together)
               excluded system fields: every PK, docNo, statusCode, eventReference,
               originalEntryId, reversalEntryId, postedAt, lineCount, isRemainderFl, audit fields
               read-only on edit: the whole entry — a POSTED entry is locked (RULE-FIN-016) and
               this screen has no edit mode at all
Container    : FULL_PAGE
No DRAFT is modelled as a stored state a user can return to: SRS §A7 makes DRAFT transient and
a failed build is never written. `isRemainderFl` is read on a built entry and never written by
this form.

<!-- SUB:F1-SCR-FIN-006:END -->
