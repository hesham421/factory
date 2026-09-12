<!-- source: PHASE:TEST-PLAN-FE / SUB:INT-FLOW -->
<!-- context: TEST-PLAN-FE-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-013, API-MDL-010, REQ-MDL-013, SCR-MDL-001, SCR-MDL-002 -->
<!-- SUB:INT-FLOW:START traces=AC-MDL-013,REQ-MDL-013,SCR-MDL-002,SCR-MDL-001,API-MDL-010 -->
### SUB — INT-FLOW

The one flow that crosses screens: the registry browse and the hand-off into the screen that manages what it shows.

<!-- TC:TC-MDL-025:START traces=AC-MDL-013,REQ-MDL-013,SCR-MDL-002,SCR-MDL-001,API-MDL-010 -->
### TC-MDL-025 — browse the registry by owner and cross into the screen that manages a type
Derived from : AC-MDL-013 (REQ-MDL-013) · Exercises: SCR-MDL-002 /reference-data/type-registry → SCR-MDL-001 · API-MDL-010
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: lookup types owned by more than one module, and a caller holding both screens
Steps        : 1. open /reference-data/type-registry 2. read the groups 3. narrow by owner module 4. follow a type row into the manager
Expected     : the types are shown grouped under their owner-module headings, the grouping being the one the response carries rather than one composed on the client; the filter is mirrored into the route's search params, so the narrowed view is a shareable address; the type row lands on /reference-data/lookups/:typeId with that type selected, and this screen offers no create or edit of its own
Test data    : types owned by SEC and by FIN
<!-- TC:TC-MDL-025:END -->

<!-- SUB:INT-FLOW:END -->
