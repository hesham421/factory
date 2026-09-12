# ADR-FIN-007 — API-FIN-020 (build an entry from an accounting event) is bound but drawn on no screen

Module  : FIN     Version : v1     Stage raised : P3.2 (Frontend — UX Design + Execution Plan)
Status  : ACCEPTED (non-breaking)

## Context
`POST /api/v1/fin/journal-entries/from-event` (API-FIN-020) takes an `EventEntryBuildRequest`
— `eventReference`, `eventTypeCode`, `docDate`, `baseAmount`, and free-form `amounts` and
`fields` maps — and builds, validates and posts an entry through the event-type rule
(REQ-FIN-010..013). `srs-fin.md` SCR-REQ-FIN-006 §B5 lists it as "build event entry
(system)", and US-FIN-004 is written from the accounting engine's point of view, not a
user's: "As the accounting engine, I need to build a balanced entry from an incoming
canonical event". §A2 puts the host's business module, the event consumer and the transport
layer explicitly out of scope.

The caller is therefore another system, over the platform's in-process module interface —
not an accountant with a form. A screen that let a user type an `eventReference` and an
amounts map would be inventing a data-entry path for a payload whose whole purpose is that it
arrives from a host.

## Decision
API-FIN-020 is **bound** — it has an F2 block on SCR-FIN-006 stating its verb, path, request,
response and error routing, so the surface is completely accounted for — and is **called by
no screen**. Its entries are seen in the journal-entry list like any other source, keyed by
`journalTypeCode = EVENT_GENERATED` and carrying an `eventReference`; the drill-down of
REQ-FIN-046 ends on exactly that field.

## Consequences
- The operations coverage table carries API-FIN-020 with a `✗` route and this ADR.
- REQ-FIN-010..013 remain covered by the frontend in the only way a UI can cover them: the
  entries the engine builds are searchable, readable line by line, and reversible, on
  SCR-FIN-006.
- No `REQ-*` is left without a screen: the traceability matrix maps US-FIN-004 to
  SCR-REQ-FIN-006, which is exactly where those entries are seen.
