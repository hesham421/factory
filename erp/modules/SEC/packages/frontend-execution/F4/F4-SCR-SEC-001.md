<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-001 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-001, AC-SEC-002, API-SEC-001, REQ-SEC-001, REQ-SEC-002, SCR-SEC-001 -->
<!-- SUB:F4-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F4 · SCR-SEC-001 — تسجيل الدخول / Login

### F4-SCREEN — SCR-SEC-001            traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001
Routes       : `/login` — the only route; no `new`, no `:id`, no `:id/edit` (this screen has no
               record to address)
Chunk        : one lazy chunk for this composite screen (`react-router`); the three public
               screens are separate chunks, since a signed-in user loads none of them
Guard        : **none — public.** SRS Access summary marks SEC_LOGIN public, so no
               `PERM_*` gates it. The inverse guard applies instead: a caller who already holds
               a session is sent to their own landing screen rather than shown this form again.
Components   : `LoginPage` (route-level) · `CredentialsForm` (presentational)
Mode         : not applicable — no CREATE / EDIT / VIEW mode exists; there is no route match to
               resolve one from
Facade       : the SCR-SEC-001 facade of F2; the page never calls the mutation directly
Shared UI    : the card shell, text field, password field, primary button and inline message of
               the design system — nothing else is rendered
Cross-module : none — no `UXD-*` is cited, because no field on this screen displays another
               module's data
On success the menu (API-SEC-027) is fetched before navigating, so the landing screen is
resolved from the caller's real grants rather than from a default route that may not be theirs.

<!-- SUB:F4-SCR-SEC-001:END -->
