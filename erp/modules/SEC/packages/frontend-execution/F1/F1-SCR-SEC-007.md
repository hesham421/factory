<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-007 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-022, AC-SEC-023, API-SEC-022, REQ-SEC-022, REQ-SEC-023, SCR-SEC-007 -->
<!-- SUB:F1-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F1 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F1-MODEL — dashboard aggregates (no entity is edited)
Source DTO   : `DashboardResponse` — every property read-only, every property optional
  usersOverview : { total, active, disabled, pendingSignups } : number · read-only
  failedLogins24h : { count } : number · read-only — the derived figure SRS A3 documents as
                    computed from the audit log, never a stored column on ENT-SEC-001
  activeSessions : { count } : number · read-only
  recentActivity : AuditLogEntryResponse[] · read-only — { auditLogPk, eventTypeCode,
                   actorUserId, occurredAt, targetRef, detailsAr, detailsEn, ipAddress }
  rolesPermissionsSummary : { roleCount, privilegedRoleCount,
                   usersPerRole : { roleId, code, nameAr, nameEn, userCount }[] } · read-only
  onboardingFunnel : { pendingSignups, stalledCount } : number · read-only
Read-only    : all of the above — the dashboard has no input of any kind (SRS B3)
### F1-SCREEN — SCR-SEC-007
Search model : none — aggregate widgets, not a browsable list (SRS B2)
Form model   : none
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Every widget property is optional in the published DTO, and that is the permission mechanism:
a widget the caller may not see is absent from the response, so the model treats absence as
"not permitted", never as zero (REQ-SEC-023, ADR-SEC-005). No figure is stored, carried
between visits or recomputed on the client — REQ-SEC-022 requires each one computed live by
the server at the moment of opening.

<!-- SUB:F1-SCR-SEC-007:END -->
