<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-007 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-022, AC-SEC-023, API-SEC-022, REQ-SEC-022, REQ-SEC-023, SCR-SEC-007 -->
<!-- SUB:F2-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F2 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F2-QUERY — API-SEC-022            traces=API-SEC-022,REQ-SEC-022,REQ-SEC-023
GET `/api/v1/sec/dashboard` · no request body · response `DashboardResponse` ·
kind **read query**
Cache key    : `[dashboard]` — no filter exists, so the key carries none
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message, shown in place of the
               grid · `INTERNAL_ERROR` (500) → generic. A widget the caller may not see is not
               an error: it is simply absent from the response (ADR-SEC-005).
Loading      : LOCAL, per widget — one slow figure must not hold the page. The SRS does not
               state that this call is slow, so no GLOBAL indicator.
Cache policy : **no caching of the figures across visits** — REQ-SEC-022 requires every figure
               computed from live data at the moment the dashboard is opened, so this entry is
               always considered stale and refetched on mount. This is a deliberate deviation
               from the defaults, required by the requirement itself rather than chosen; it is
               recorded here rather than in an ADR because the requirement states it outright.
Invalidation : not applicable — the screen writes nothing
### F2-SCREEN-INIT — SCR-SEC-007
Permission read : `SEC_DASHBOARD` present in the API-SEC-027 menu response → VIEW. Per-widget
                  permission is not read at all: the server returns only the widgets the caller
                  may see, so presence in the response **is** the permission (REQ-SEC-023,
                  ADR-SEC-005).
Lookups used    : AUDIT_EVENT_TYPE — the recent-activity widget shows event type codes and
                  resolves their labels through the shared hook (ADR-SEC-006)
Entity by id    : none
### F2-FACADE — SCR-SEC-007
Composes     : the API-SEC-022 query and the AUDIT_EVENT_TYPE lookup hook
State it owns: which widgets the response actually carried (the render list), and a derived
               per-widget loading flag; no figure is held beyond the render
Operations   : none — read-only (SRS B3). Each widget's navigation target is a route, not an
               operation: recent activity → SCR-SEC-008, active sessions → SCR-SEC-009,
               onboarding funnel → SCR-SEC-004's pending sub-view.

<!-- SUB:F2-SCR-SEC-007:END -->
