<!-- source: PHASE:F2 — preamble before the first SUB -->
<!-- traces: REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, UXD-MDL-001, SCR-MDL-001, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-010, API-MDL-011, SCR-MDL-002 -->
## PHASE 2 — F2 — Data Hooks

What each screen needs from the API — not hook code. Every read query's cache key carries
**every** filter that changes the response, page and size included **where the endpoint is
paged**; page and page size live inside the filter object and are never independent state.
Every mutation declares its invalidation. Components use the facade only; the facade uses the
declared queries only (server-state library: `tanstack-query`).

Only two of the eleven endpoints return `Page<T>` — API-MDL-001 and API-MDL-005. API-MDL-009,
API-MDL-010 and API-MDL-011 return bare arrays, so their keys carry no page or size and their
blocks say so rather than leaving a reader to assume the usual envelope.
