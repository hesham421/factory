<!-- source: PHASE:INT-C -->
<!-- traces: REQ-SEC-016 -->
<!-- PHASE:INT-C:START traces=REQ-SEC-016 -->
## PHASE 5 — INT-C (cross-module consume)

No `XM-*` row exists for SEC (db-script-sec.md §2: "None — SEC is ROOT"). SEC consumes no
other module's entity, table or API. This phase is intentionally near-empty, stated so per
engine §6.2 rather than omitted; no SUB is opened (XM count 0 < the split threshold of 5).

SEC's actual cross-module role runs in the opposite direction: every future module
*consumes* SEC through the plain REST surface documented in Phase 3 (registration:
API-SEC-018/019/020; authorization: the CORE interceptor + API-SEC-027) — that is standard
API consumption by another module's own P3.1, not an `XM-*` row inside SEC's own plan.
<!-- PHASE:INT-C:END -->
