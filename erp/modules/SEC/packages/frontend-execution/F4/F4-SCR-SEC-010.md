<!-- source: PHASE:F4 / SUB:F4-SCR-SEC-010 -->
<!-- context: F4-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-021, AC-SEC-032, AC-SEC-033, API-SEC-027, REQ-SEC-021, REQ-SEC-032, REQ-SEC-033, SCR-SEC-010 -->
<!-- SUB:F4-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F4 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F4-SCREEN — SCR-SEC-010            traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027
Routes       : **none of its own** — this is the application shell's navigation component,
               rendered inside every authenticated route rather than matched by one. It is not
               a securable destination and has no page code (SRS B4).
Chunk        : none — it belongs to the shell bundle, not to a lazy chunk. A menu loaded lazily
               would leave the shell without navigation on first paint.
Guard        : the component itself requires only an authenticated caller, as its endpoint
               does. It **is** the guard source for every other screen: each route element in
               F4 above tests `holdsScreen(pageCode)` against this component's facade
               (ADR-SEC-005).
Components   : `AppShellNav` (shell-level) · `ModuleMenuGroup`, `ScreenMenuItem`
               (presentational). No "Page" suffix appears here, because none of these is a
               route-level page.
Mode         : not applicable — no route match, so no mode
Facade       : the SCR-SEC-010 facade of F2, which exposes the derived `holdsScreen(pageCode)`
               predicate the guards read
Shared UI    : navigation list, disclosure group, active-item indicator, skeleton, empty state
Cross-module : none — the entries are rows of SEC's own registry entities
A module the response omits is absent from the menu entirely (REQ-SEC-032) and its routes are
refused by their own guards (REQ-SEC-033); neither behaviour is the enforcement, which is the
server's on every request. When the menu fails to load the shell renders no entry and no route
becomes reachable — a failure narrows access, never widens it.

<!-- SUB:F4-SCR-SEC-010:END -->
