<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-009 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-027, AC-SEC-028, API-SEC-025, API-SEC-026, REQ-SEC-027, REQ-SEC-028, SCR-SEC-009 -->
<!-- SUB:F1-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F1 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F1-MODEL — ENT-SEC-010 — الجلسة النشطة / ActiveSession
Source DTO   : `ActiveSessionResponse` (read) · `SessionTerminationResponse` (terminate result)
  activeSessionPk : number · read-only (PK) · system-only
  userId          : number · read-only
  username        : string · read-only — the owner's login, returned beside the id so the list
                    needs no second call to name the user
  startedAt       : date-time · read-only · system-only
  lastActivityAt  : date-time · read-only · system-only
  ipAddress       : string · read-only · optional
  terminatedAt    : date-time · read-only — returned only by `SessionTerminationResponse`
Read-only    : every property — the only mutation is terminate, by identifier
               `tokenRef` is never returned by any published endpoint and is not modelled; the
               SRS marks it an opaque reference that is never exposed
### F1-SCREEN — SCR-SEC-009
Search model : filters — userId or username : string · LIKE · ipAddress : string · LIKE
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : none — no create and no update (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
`terminatedAt` / `terminatedBy` are null for every row this screen lists — API-SEC-025 returns
non-terminated sessions only — so neither is modelled as a column.

<!-- SUB:F1-SCR-SEC-009:END -->
