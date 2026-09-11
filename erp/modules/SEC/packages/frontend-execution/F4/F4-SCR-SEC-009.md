<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-009 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-027, AC-SEC-028, API-SEC-025, API-SEC-026, REQ-SEC-027, REQ-SEC-028, SCR-SEC-009 -->
<!-- SUB:F4-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F4 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F4-SCREEN — SCR-SEC-009            traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026
Routes       : base slug `sessions`, under the module segment — `/security/sessions` (search)
               only. No `new` and no `:id/edit`: there is no entry form (SRS B3), and the sole
               mutation is a per-row terminate that needs no route of its own.
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_SESSIONS_VIEW`, evaluated as `SEC_SESSIONS` present in the
               menu response (ADR-SEC-005). `PERM_SEC_SESSIONS_DELETE` is not readable from any
               published endpoint, so the terminate affordance renders and the server's 403 is
               the authority.
Components   : `ActiveSessionsPage` (route-level) · `SessionFilters`, `SessionResultTable`,
               `TerminateSessionConfirm` (presentational)
Mode         : VIEW only — read-only list with one action
Facade       : the SCR-SEC-009 facade of F2
Shared UI    : data table, filter bar, text field, destructive button, confirmation dialog,
               skeleton, empty state, localized message banner
Cross-module : none
Terminating confirms first and names the affected user (AC-SEC-028); on success the row leaves
the list through a re-read rather than a local removal, because the screen's contract is
"sessions that have not been terminated" and the server decides which those are.

<!-- SUB:F4-SCR-SEC-009:END -->
