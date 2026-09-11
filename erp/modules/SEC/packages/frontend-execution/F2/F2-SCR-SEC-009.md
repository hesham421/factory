<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-009 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-027, AC-SEC-028, API-SEC-025, API-SEC-026, REQ-SEC-027, REQ-SEC-028, SCR-SEC-009 -->
<!-- SUB:F2-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F2 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F2-QUERY — API-SEC-025            traces=API-SEC-025,REQ-SEC-027
POST `/api/v1/sec/sessions/search` · request `ActiveSessionSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<ActiveSessionResponse>` ·
kind **read query** (ADR-SEC-003)
Cache key    : `[sessions, filters]` — user/username, ipAddress, sort **and page, size**, in
               the one filter object
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on sort · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-SEC-026 below, and by API-SEC-009 on SCR-SEC-004 — deactivating
               a user ends that user's sessions server-side (REQ-SEC-011)
### F2-QUERY — API-SEC-026            traces=API-SEC-026,REQ-SEC-028
DELETE `/api/v1/sec/sessions/{id}` · response `SessionTerminationResponse` { activeSessionPk,
terminatedAt } · kind **mutation**
Errors       : `SEC-404-SESSION` (404) → user message · `SEC-409-ALREADY-TERMINATED` (409) →
               user message (the session ended between the render and the click; the list is
               refreshed rather than the row patched) · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[sessions, *]` and `[dashboard]` — the active-sessions figure changes with it
### F2-SCREEN-INIT — SCR-SEC-009
Permission read : `SEC_SESSIONS` present in the API-SEC-027 menu response → VIEW. The DELETE
                  (terminate) permission is not readable from any published endpoint; the
                  affordance renders and the server's 403 is the authority (ADR-SEC-005).
Lookups used    : none
Entity by id    : none — the list row carries `username` beside `userId`, so naming the session
                  owner needs no second call
### F2-FACADE — SCR-SEC-009
Composes     : API-SEC-025 (list) · API-SEC-026 (terminate)
State it owns: the session list derived from the query's data, the filter object including page
               and size, the row awaiting confirmation, and a derived loading flag
Operations   : terminateSession(id) — usage check first: the confirmation names the affected
               user, because the consequence lands on someone working at that moment

<!-- SUB:F2-SCR-SEC-009:END -->
