# ADR-FIN-001 — Recurring/reversing template schedule represented as data, not an enumerated frequency
Status      : ACCEPTED
Stage       : P1        Module: FIN        Version: v1
Context     : plan §4.3 requires a template that "recurs on a schedule (e.g., monthly), or auto-reverses in the next period" but does not specify the schedule's data shape. §2 resolution order step 6 (domain best practice) applies since no policy, story, registry fact, knowledge source or steering rule settles it.
Decision    : Model `ENT-FIN-008.scheduleRule` as a single data-defined recurrence definition (logical type text; physical encoding — e.g. cron-like or interval fields — is P2's job) rather than a fixed enumerated frequency list (MONTHLY/QUARTERLY/...). This keeps the schedule itself configuration, consistent with the module's governing rule "everything that can change = defined data, not code" (plan §0), and needs no future code change to support a new recurrence pattern.
Consequences: P2 designs the physical column(s) backing `scheduleRule`; P3.1/P3.2 expose it as a single configurable field, not a fixed dropdown of frequencies.
traces      : ENT-FIN-008, REQ-FIN-016
