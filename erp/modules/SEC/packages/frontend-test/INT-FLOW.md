<!-- source: PHASE:TEST-PLAN-FE / SUB:INT-FLOW -->
<!-- context: TEST-PLAN-FE-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-021, AC-SEC-023, AC-SEC-032, AC-SEC-033, API-SEC-022, API-SEC-027, REQ-SEC-021, REQ-SEC-023, REQ-SEC-032, REQ-SEC-033, SCR-SEC-007, SCR-SEC-009, SCR-SEC-010 -->
<!-- SUB:INT-FLOW:START traces=AC-SEC-021,REQ-SEC-021,SCR-SEC-010,API-SEC-027,AC-SEC-032,REQ-SEC-032,AC-SEC-033,REQ-SEC-033,AC-SEC-023,REQ-SEC-023,SCR-SEC-007,SCR-SEC-009,API-SEC-022 -->
### SUB — INT-FLOW

The flows that span screens: the two-tier menu that is itself the guard source for every route above, and the dashboard widget whose gating is the server's.

<!-- TC:TC-SEC-060:START traces=AC-SEC-021,REQ-SEC-021,SCR-SEC-010,API-SEC-027 -->
### TC-SEC-060 — the menu shows exactly the modules and screens the caller's grants union to
Derived from : AC-SEC-021 (REQ-SEC-021) · Exercises: SCR-SEC-010 (shell) · API-SEC-027
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: a user whose roles union to exactly module FIN with the screens "Journal Entries" and "Trial Balance"
Steps        : 1. sign in as that user 2. read the two-tier menu
Expected     : FIN is the only top-level entry and exactly those two screens sit beneath it; the menu is derived entirely from the response and is never authored in the client, which is why it is also the source every route guard evaluates
Test data    : one module, two screens
<!-- TC:TC-SEC-060:END -->

<!-- TC:TC-SEC-061:START traces=AC-SEC-032,REQ-SEC-032,SCR-SEC-010,API-SEC-027 -->
### TC-SEC-061 — a module the caller does not hold is absent from the menu entirely
Derived from : AC-SEC-032 (REQ-SEC-032) · Exercises: SCR-SEC-010 (shell) · API-SEC-027
Rule / code  : —
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: a user whose roles hold no grant for module FIN
Steps        : 1. sign in as that user 2. search the menu for FIN
Expected     : FIN appears nowhere — not greyed out, not disabled, absent. What is not granted is not rendered
Test data    : a user without the FIN grant
<!-- TC:TC-SEC-061:END -->

<!-- TC:TC-SEC-062:START traces=AC-SEC-033,REQ-SEC-033,SCR-SEC-010,API-SEC-027 -->
### TC-SEC-062 — a route reached directly without its grant is refused
Derived from : AC-SEC-033 (REQ-SEC-033) · Exercises: SCR-SEC-010 (the guard source) · API-SEC-027
Rule / code  : —
Scenario     : PERMISSION · data class ATTACK · language ALL
Preconditions: the same user, and a FIN screen URL typed directly
Steps        : 1. sign in as that user 2. navigate straight to the FIN screen URL 3. call the FIN endpoint directly
Expected     : the route guard sends the caller to the unauthorized destination, and the server denies the direct endpoint call independently — the menu's omission is not the enforcement, the server's check is, and the test asserts both halves rather than only the one the UI performs
Test data    : a direct URL and a direct endpoint call
<!-- TC:TC-SEC-062:END -->

<!-- TC:TC-SEC-063:START traces=AC-SEC-023,REQ-SEC-023,SCR-SEC-007,SCR-SEC-009,API-SEC-022 -->
### TC-SEC-063 — a widget the caller may not see is absent, and its source screen still guards itself
Derived from : AC-SEC-023 (REQ-SEC-023) · Exercises: SCR-SEC-007 /security/dashboard → SCR-SEC-009 · API-SEC-022
Rule / code  : —
Scenario     : PERMISSION · data class VALID · language ALL
Preconditions: an administrator role without the "active sessions" widget's permission
Steps        : 1. sign in as that role's user 2. open /security/dashboard 3. look for the active-sessions widget 4. navigate directly to /security/sessions
Expected     : the widget is absent from the response and therefore from the screen — the server returns only the widgets the caller may see, and the client performs no second permission test of its own; the sessions route is then refused by its own guard, so the absence and the refusal are two independent mechanisms and neither is standing in for the other
Test data    : a role without the sessions permission
<!-- TC:TC-SEC-063:END -->

<!-- SUB:INT-FLOW:END -->
