<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-008 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-024, AC-SEC-025, AC-SEC-026, API-SEC-023, API-SEC-024, REQ-SEC-024, REQ-SEC-025, REQ-SEC-026, SCR-SEC-008 -->
<!-- SUB:F4-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F4 · SCR-SEC-008 — سجل التدقيق / Audit log

### F4-SCREEN — SCR-SEC-008            traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024
Routes       : base slug `audit-log`, under the module segment — `/security/audit-log` (search)
               only. No `new`, no `:id`, no `:id/edit`: audit rows are never created and never
               opened alone (SRS B3).
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_AUDIT_LOG_VIEW`, evaluated as `SEC_AUDIT_LOG` present in
               the menu response (ADR-SEC-005). Export shares that permission (SRS B4), so its
               affordance carries no separate guard.
Components   : `AuditLogPage` (route-level) · `AuditFilters`, `AuditResultTable`,
               `ExportButton` (presentational)
Mode         : VIEW only — read-only screen
Facade       : the SCR-SEC-008 facade of F2
Shared UI    : data table, filter bar, select, date-range field, secondary button, skeleton,
               empty state, localized message banner
Cross-module : none
The filter set is mirrored into the route's search params, so a filtered investigation is
shareable by URL even though the search itself is a POST (ADR-SEC-003). Export builds its four
query parameters from that same filter object and deliberately omits `page` and `size`, so it
exports the investigation rather than the visible page (AC-SEC-026).

<!-- SUB:F4-SCR-SEC-008:END -->
