<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-008 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-039, AC-FIN-046, API-FIN-028, REQ-FIN-039, REQ-FIN-046, SCR-FIN-008, UXD-FIN-001, UXD-FIN-002, UXD-FIN-005 -->
<!-- SUB:F4-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F4 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F4-SCREEN — SCR-FIN-008            traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005
Routes       : base slug `account-ledger`, under `/finance` —
               `/finance/account-ledger` — the only route; no `new`, no `:id`, no `:id/edit`,
               because this screen addresses no record it could edit. The account, date range
               and dimension live in the route's search params, so the report IS its address
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_ACCOUNT_LEDGER_VIEW`, evaluated as
               "`FIN_ACCOUNT_LEDGER` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `AccountLedgerPage` (route-level, FULL_PAGE) · `LedgerFilters`,
               `LedgerSummaryHeader`, `LedgerRowTable` (presentational)
Mode         : not applicable — no CREATE, EDIT or VIEW mode exists to resolve; this screen
               writes nothing
Facade       : the SCR-FIN-008 facade of F2
Shared UI    : filter bar, account picker, date-range filter, select, data table, localized
               message banner
Cross-module : UXD-FIN-001 (account type), UXD-FIN-002 (nature and direction), UXD-FIN-005
               (journal type on each row)
Each row's document number links to `/finance/journal-entries/:id`, which is SCR-FIN-006's own
route and carries its own guard — the third hop of REQ-FIN-046's chain. This screen is the
drill-down target of SCR-FIN-009 and SCR-FIN-012, and arrives with its filters already in the
address.

<!-- SUB:F4-SCR-FIN-008:END -->
