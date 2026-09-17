# ADR-NOTE-005 — صفوف الأخطاء المنصّية في كتالوج الأخطاء / PLATFORM-STD rows in the error catalog

| Item | Value |
|---|---|
| Status | ACCEPTED (non-breaking) |
| Stage | P3.1 — backend execution plan |
| Module | NOTE v1 |
| Date | 2026-09-17 |
| Traces | REQ-NOTE-004, REQ-NOTE-016, REQ-NOTE-018 |

## Context

The error catalog must carry a row for every error an endpoint of this module can raise, and
every row must name the RULE behind it. Five of the module's raisable errors have no business
rule behind them at all: an unauthenticated request (401), a request refused by the module
gate (403), a request refused for an ungranted action (403), a request asking to sort on a
field the screen does not offer (400) and an unexpected server failure (500). The SRS states
the user-facing message for two of them (AC-NOTE-022, AC-NOTE-024) but declares no `RULE-*`
for any: they are platform behaviours the module inherits, not data constraints it owns.
Inventing a `RULE-NOTE-*` for each would put rules in the SRS's own atom space that the SRS
never declared, from a stage that does not own that atom.

## Decision

These five rows carry `PLATFORM-STD` in the RULE column, with this ADR as the reference:
`NOTE-401`, `NOTE-403-SCREEN-FORBIDDEN`, `NOTE-403-ACTION-FORBIDDEN`, `NOTE-400-INVALID-SORT`
and `NOTE-500`. Their messages are the SRS's own where the SRS states them (the two 403 rows)
and platform-standard text in ar and en where it does not. Every one of them is an instance of
the declared code format and carries a status the platform can emit.

## Consequences

- The catalog stays complete — no raisable error is missing a row — without minting a business
  rule the SRS never declared.
- Downstream consumers (frontend plan, test-gen, api-verify) cite these codes exactly as they
  cite the rule-backed ones; nothing about the envelope differs.
- If a later version turns one of these into a genuine business rule (a configurable sort
  policy, for instance), the row changes its RULE column and this ADR is superseded.
