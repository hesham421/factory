<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-009 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-027, AC-SEC-028, API-SEC-025, API-SEC-026, REQ-SEC-027, REQ-SEC-028, SCR-SEC-009 -->
<!-- SUB:F3-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F3 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

This screen has **no entry form** (SRS B3: no create, no update). Only the filter set
accepts input, with timing **on change**.
### F3-FIELD — SCR-SEC-009 (filters)
user / username · optional · LENGTH (no published maximum — none asserted) · when change
ipAddress       · optional · when change
Validation shape : two optional free-text filters; no pattern is asserted on the IP filter,
                   because a partial address is a legitimate LIKE search and a strict pattern
                   would reject it. Written with `zod` + `react-hook-form`.
No `RULE-*` is enforced on this screen. REQ-SEC-028's termination is a server operation whose
only client surface is the confirmation described in F2, and `SEC-409-ALREADY-TERMINATED` is
routed to a user message followed by a re-read of the list — never a local removal of the row.
No LOOKUP_VALID and no UNIQUE_CHECK apply: nothing on this screen is a lookup field and nothing
is created.
Locale        : session → browser → `ar`; `startedAt` and `lastActivityAt` are rendered in the
                tenant timezone by the active locale.
Permission-driven behaviour: a caller without VIEW never reaches this screen (F4 guard); the
terminate affordance renders for anyone who does, and `ACCESS_DENIED` is shown as the localized
forbidden message (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-009:END -->
