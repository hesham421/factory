<!-- source: PHASE:INT-C -->
<!-- traces: REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031 -->
<!-- PHASE:INT-C:START traces=REQ-FIN-001 -->
## PHASE 5 — INT-C (cross-module consume)

One `XM-*` row (XM-FIN-001), below the split threshold (1 < 5) — no SUB opened.

<!-- XM:XM-FIN-001:START traces=REQ-FIN-001,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-018,REQ-FIN-022,REQ-FIN-025,REQ-FIN-031 -->
### XM-FIN-001 — validate/read lookup-backed codes against MDL
Target        : MDL · ENT-MDL-001/002 (LookupType/LookupValue) · classification SOFT-READ
Interface     : REST call — `GET /api/v1/mdl/lookups?type={key}` (API-MDL-011) for every
one of FIN's 13 owned keys, called at the point each lookup-backed field is written or offered as a select-list
Contract      : data required = the submitted code exists as an active value under the
named type; fallback if absent = reject with `FIN-400-INVALID-LOOKUP`; retry = none
(synchronous, user-facing call — a transient MDL outage surfaces as `FIN-503`); idempotency
= read-only, naturally idempotent
Blocks        : none DEFERRED — MDL v1 is already gated (pass-1 APPROVE); ACTIVE from the
moment FIN v1 is created
<!-- XM:XM-FIN-001:END -->

FIN's dependency on SEC (identity/authorization for every request, and FIN's own
self-registration into SEC) is not a formal `XM` row — ADR-FIN-001 (carried from P2).
<!-- PHASE:INT-C:END -->
