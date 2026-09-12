<!-- source: PHASE:TEST-PLAN-FE / SUB:INT-FLOW -->
<!-- context: TEST-PLAN-FE-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-046, API-FIN-022, API-FIN-028, API-FIN-029, API-FIN-030, REQ-FIN-046, SCR-FIN-006, SCR-FIN-008, SCR-FIN-009, SCR-FIN-010 -->
<!-- SUB:INT-FLOW:START traces=AC-FIN-046,REQ-FIN-046,SCR-FIN-010,SCR-FIN-009,SCR-FIN-008,SCR-FIN-006,API-FIN-030,API-FIN-029,API-FIN-028,API-FIN-022 -->
### SUB — INT-FLOW

The one flow that crosses screens: REQ-FIN-046's drill-down chain, which is a property of four screens' links and of no single screen.

<!-- TC:TC-FIN-148:START traces=AC-FIN-046,REQ-FIN-046,SCR-FIN-010,SCR-FIN-009,SCR-FIN-008,SCR-FIN-006,API-FIN-030,API-FIN-029,API-FIN-028,API-FIN-022 -->
### TC-FIN-148 — drill down from a statement line to the originating entry and its source
Derived from : AC-FIN-046 (REQ-FIN-046) · Exercises: SCR-FIN-010 → SCR-FIN-009 → SCR-FIN-008 → SCR-FIN-006 · API-FIN-030, 029, 028, 022
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a balance-sheet line with posted activity behind it, reachable by a caller holding all four screens
Steps        : 1. open /finance/balance-sheet for a fiscal year and choose a statement line 2. follow it to /finance/trial-balance narrowed to that account type 3. follow a row to /finance/account-ledger for that account and range 4. follow a ledger row to /finance/journal-entries/:id 5. read the entry's source
Expected     : each hop lands on the next screen with its filters already in the address, so every step is shareable; the chain ends on the entry's event reference, or on its journal type (manual, recurring, allocation) when the entry is not event-sourced
Test data    : a balance-sheet line whose activity traces to an event-sourced entry
<!-- TC:TC-FIN-148:END -->

<!-- SUB:INT-FLOW:END -->
