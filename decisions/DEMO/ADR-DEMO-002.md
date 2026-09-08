# ADR-DEMO-002 — Not-found handling uses the platform standard exception

Status  : ACCEPTED (non-breaking)
Module  : DEMO   Version : v1
Traces  : API-DEMO-003, API-DEMO-004, API-DEMO-005

## Context
Reading, updating or deactivating a note by id when it does not exist (or is
already inactive) is an infrastructure-level error, not a business RULE from
the SRS. `[KB:erp-domain-standards]` and the SRS are silent on the exact
error code for this case, since it is a cross-cutting platform behaviour
(`LocalizedException → {code, messageAr, messageEn}`), not module-specific.

## Decision
Use the platform's standard "not found" exception (`RULE = PLATFORM-STD`)
for `API-DEMO-003` (read), `API-DEMO-004` (update) and `API-DEMO-005`
(deactivate) when the requested `note_pk` does not resolve to an active
`demo_note` row. Catalog code: `DEMO_NOTE_NOT_FOUND`, HTTP 404.

## Consequences
- The Error Catalog (P3.1 §7) carries one row for `DEMO_NOTE_NOT_FOUND` with
  `RULE = PLATFORM-STD (ADR-DEMO-002)` instead of a module RULE id.
- Non-breaking: this only names an existing platform mechanism; it does not
  add new behaviour or contradict any approved story, policy or REQ.
