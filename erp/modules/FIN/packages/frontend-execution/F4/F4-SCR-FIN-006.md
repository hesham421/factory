<!-- source: PHASE:F4 / SUB:F4-SCR-FIN-006 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-010, AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-014, AC-FIN-015, AC-FIN-016, AC-FIN-017, AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-027, AC-FIN-028, AC-FIN-029, AC-FIN-030, API-FIN-018, API-FIN-019, API-FIN-020, API-FIN-021, API-FIN-022, REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, SCR-FIN-006, UXD-FIN-002, UXD-FIN-005, UXD-FIN-006 -->
<!-- SUB:F4-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F4 · SCR-FIN-006 — قيود اليومية / Journal entries

### F4-SCREEN — SCR-FIN-006            traces=REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-027,AC-FIN-028,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006
Routes       : base slug `journal-entries`, under `/finance` —
               `/finance/journal-entries` (search) ·
               `/finance/journal-entries/new` (the manual entry page — a static segment
               registered BEFORE the `:id` route) ·
               `/finance/journal-entries/:id` (the entry, read-only, with the Reverse action)
               There is no `:id/edit` route at all: a POSTED entry is locked (RULE-FIN-016),
               and the absence of the route is how that is expressed in the router.
Chunk        : one lazy chunk for this composite screen — search, entry page and the read-only
               entry share it
Guard        : every route element guarded by `PERM_FIN_JOURNAL_ENTRIES_VIEW`, evaluated as
               "`FIN_JOURNAL_ENTRIES` is present in the caller's effective menu"
               (ADR-FIN-005). CREATE and the custom reverse action are not readable, so `/new`
               carries the same VIEW guard and the server's 403 is the authority on the write.
Components   : `JournalEntriesSearchPage` (route-level, FULL_PAGE) · `JournalEntryPage`
               (route-level, FULL_PAGE — create mode, or read-only on a posted entry) ·
               `EntryFilters`, `EntryResultTable`, `EntryHeaderForm`, `EntryLineGrid`,
               `EntryLineDimensions`, `EntryTotalsBar`, `ReverseConfirm`,
               `ValidationFailureList` (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new` → CREATE, `/:id` → VIEW.
               There is no EDIT mode to resolve.
Facade       : the SCR-FIN-006 facade of F2; pages never call queries directly
Shared UI    : data table, filter bar, date field, date-range filter, select, number field,
               editable line grid, totals bar, confirmation dialog, inline errors, localized
               message banner
Cross-module : UXD-FIN-005 (journal type), UXD-FIN-006 (status), UXD-FIN-002 (direction)
`ValidationFailureList` exists because REQ-FIN-015 asks for every failing check at once: the
refusals of one submission are listed together above the entry, each also routed inline to the
line or field it names, and nothing the user typed is cleared. API-FIN-020 has no component
and no route on this screen (ADR-FIN-007); its entries appear in the list like any other.

<!-- SUB:F4-SCR-FIN-006:END -->
