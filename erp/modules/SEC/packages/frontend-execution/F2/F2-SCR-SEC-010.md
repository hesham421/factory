<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-010 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-021, AC-SEC-032, AC-SEC-033, API-SEC-027, REQ-SEC-021, REQ-SEC-032, REQ-SEC-033, SCR-SEC-010 -->
<!-- SUB:F2-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F2 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F2-QUERY — API-SEC-027            traces=API-SEC-027,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033
GET `/api/v1/sec/menu` · no request body · response `array of ModuleMenuResponse` — a bare
array, **not** `Page<T>` · kind **read query**
Cache key    : `[menu]` — the response is per-caller and carries no filter, so the key carries
               none; it is discarded with the rest of the cache when the session changes
Errors       : `ACCESS_DENIED` (403) → the shell stays usable, states that navigation could not
               be loaded, and **no screen becomes reachable as a result** — a failed menu never
               widens access · `INTERNAL_ERROR` (500) → generic, same rule
Loading      : LOCAL — the shell renders before the menu resolves and shows no entry it has not
               received; nothing is guessed from a static route table
Cache policy : long-lived within a session — the effective grants change only when an
               administrator changes them
Invalidation : `[menu]` is invalidated by every grant mutation of SCR-SEC-005 (API-SEC-014,
               015, 016, 017) and refetched fresh after API-SEC-001, so a revoked grant cannot
               outlive its revoke in this client
### F2-SCREEN-INIT — SCR-SEC-010
Permission read : none of its own — the published endpoint requires only an authenticated
                  caller, and this screen is not a securable destination (SRS B4). This query
                  **is** the permission source every other screen's guard reads (ADR-SEC-005).
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-010
Composes     : the API-SEC-027 query only
State it owns: the module → screen tree derived from the query's data and the expanded module;
               it owns no list of its own and composes no entry locally
Operations   : none — read-only and fully derived (SRS B3)
This facade exposes one derived predicate, `holdsScreen(pageCode)`, computed from the response
it already holds. Every route guard in F4 and every RF5 block reads that predicate, so the
screen-level gate has exactly one source and one call site.

<!-- SUB:F2-SCR-SEC-010:END -->
