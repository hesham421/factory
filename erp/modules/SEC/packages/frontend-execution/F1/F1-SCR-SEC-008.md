<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-008 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-024, AC-SEC-025, AC-SEC-026, API-SEC-023, API-SEC-024, REQ-SEC-024, REQ-SEC-025, REQ-SEC-026, SCR-SEC-008 -->
<!-- SUB:F1-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F1 · SCR-SEC-008 — سجل التدقيق / Audit log

### F1-MODEL — ENT-SEC-011 — سجل التدقيق / AuditLogEntry
Source DTO   : `AuditLogEntryResponse` — every property read-only (append-only entity)
  auditLogPk     : number · read-only (PK) · system-only
                   (the published property name for the SRS field `auditLogEntryPk`)
  eventTypeCode  : string · read-only · lookup — AUDIT_EVENT_TYPE code held as a string
                   (no enum — ADR-SEC-006)
  actorUserId    : number · read-only · optional — absent for an unauthenticated failed login
  occurredAt     : date-time · read-only · system-only
  targetRef      : string · read-only · optional
  detailsAr      : string · read-only · optional
  detailsEn      : string · read-only · optional
  ipAddress      : string · read-only · optional
Read-only    : every property — no form ever writes this entity [POL-SEC-009]
### F1-SCREEN — SCR-SEC-008
Search model : filters — eventTypeCode : string · EXACT (from the shared lookup hook) ·
               actorUserId : number · EXACT · occurredFrom/occurredTo : date · DATE_RANGE
               paging + sort — page, size, sortField, sortDirection inside the filter object
               export model — the same filter object rendered as the four query parameters
               `eventTypeCode, actorUserId, occurredFrom, occurredTo` that API-SEC-024 accepts
               (one filter object, two shapes — ADR-SEC-003)
Form model   : none — rows are system-appended only (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
This entity carries no `createdBy`/`updatedBy`: it is the audit record, and `actorUserId` +
`occurredAt` serve that purpose (SRS A3 note).

<!-- SUB:F1-SCR-SEC-008:END -->
