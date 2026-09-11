<!-- source: PHASE:F2 / SUB:F2-SCR-SEC-008 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-024, AC-SEC-025, AC-SEC-026, API-SEC-023, API-SEC-024, REQ-SEC-024, REQ-SEC-025, REQ-SEC-026, SCR-SEC-008 -->
<!-- SUB:F2-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F2 · SCR-SEC-008 — سجل التدقيق / Audit log

### F2-QUERY — API-SEC-023            traces=API-SEC-023,REQ-SEC-024,REQ-SEC-025
POST `/api/v1/sec/audit-log/search` · request `AuditLogEntrySearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<AuditLogEntryResponse>` ·
kind **read query** (ADR-SEC-003)
Cache key    : `[audit-log, filters]` — eventTypeCode, actorUserId, the occurredFrom/occurredTo
               range, sort **and page, size**, all inside the one filter object
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on the sort control ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults — audit entries are append-only, so a returned page never changes
Invalidation : none — this screen writes nothing; new entries arrive through a refetch, not an
               invalidation (REQ-SEC-024 appends server-side, never from here)
### F2-QUERY — API-SEC-024            traces=API-SEC-024,REQ-SEC-026
GET `/api/v1/sec/audit-log/export` · query parameters `eventTypeCode`, `actorUserId`,
`occurredFrom`, `occurredTo` · response CSV · kind **read query (file)**
Cache key    : none — an export is requested, never cached
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL — the export affordance is busy while the file is produced
Cache policy : not applicable
Invalidation : none
The export's four parameters are rendered from **the same filter object** the search key holds,
so an export always matches what the screen is showing — and never the current page, since
`page` and `size` are not among the export's parameters (AC-SEC-026, ADR-SEC-003).
### F2-LOOKUP — AUDIT_EVENT_TYPE
Endpoint `PENDING ADR-SEC-006` · key `AUDIT_EVENT_TYPE` · options shape { code, labelAr,
labelEn } · ONE hook per key, shared with SCR-SEC-007's recent-activity widget · long-lived
cache. Labels resolve through the single seeded resolver until the lookup endpoint exists; the
hook exposes no value list a validator could bind to.
### F2-SCREEN-INIT — SCR-SEC-008
Permission read : `SEC_AUDIT_LOG` present in the API-SEC-027 menu response → VIEW. Export
                  shares that same permission (SRS B4), so no second read exists to make.
Lookups used    : AUDIT_EVENT_TYPE (the event-type filter and the result column)
Entity by id    : none — an audit entry is never opened on its own
### F2-FACADE — SCR-SEC-008
Composes     : API-SEC-023 (search) · API-SEC-024 (export) · the AUDIT_EVENT_TYPE hook
State it owns: the entry list derived from the query's data, the filter object including page
               and size (mirrored to the route's search params so the filtered view is
               shareable — ADR-SEC-003), and a derived loading flag
Operations   : exportCurrentFilter() — builds the four query parameters from the same filter
               object the list is reading; there is no create, update or delete

<!-- SUB:F2-SCR-SEC-008:END -->
