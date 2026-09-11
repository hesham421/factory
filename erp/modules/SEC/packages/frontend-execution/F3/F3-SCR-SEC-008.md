<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-008 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-024, AC-SEC-025, AC-SEC-026, API-SEC-023, API-SEC-024, REQ-SEC-024, REQ-SEC-025, REQ-SEC-026, SCR-SEC-008 -->
<!-- SUB:F3-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F3 · SCR-SEC-008 — سجل التدقيق / Audit log

This screen has **no entry form**: audit rows are system-appended and never hand-created
(SRS B3). Only the filter set accepts input, and its validation timing is **on change** for the
selects and **on blur** for the date range.
### F3-FIELD — SCR-SEC-008 (filters)
eventTypeCode · optional · LOOKUP_VALID · when change
actorUserId   · optional · when change
occurredFrom / occurredTo · optional · DATE_RANGE (from ≤ to) · when blur
Validation shape : an optional code, an optional actor, and a date range whose start is not
                   after its end — the only constraint asserted, and it is a property of the
                   pair rather than a business rule. Written with `zod` + `react-hook-form`.
LOOKUP_VALID  : the event-type filter's value must be one of the runtime-loaded options of the
                `AUDIT_EVENT_TYPE` hook — **never a static list**. That hook is
                `PENDING ADR-SEC-006`: until the lookup endpoint is published the validator is
                not written at all, because the only list available would be a hardcoded enum,
                which `profile.conventions.lookups` forbids. An unrecognised code is answered
                by the server as an empty result, which is the correct answer to a filter
                matching nothing.
No `RULE-*` is enforced on this screen: REQ-SEC-024's append and the entries' immutability
[POL-SEC-009] are server properties with no client surface.
Locale        : session → browser → `ar`; `detailsAr` / `detailsEn` are rendered by the active
                locale, and the export carries both as the server writes them.
Permission-driven behaviour: a caller without VIEW never reaches this screen (F4 guard); export
shares that same permission, so no affordance on it is separately gated.

<!-- SUB:F3-SCR-SEC-008:END -->
