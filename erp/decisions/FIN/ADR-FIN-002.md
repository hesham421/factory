# ADR-FIN-002 — the api-docs input carries an API ID BINDING annex, and the backend registry's API range is stale

Module  : FIN     Version : v1     Stage raised : P3.2 (Frontend — UX Design + Execution Plan)
Status  : ACCEPTED (non-breaking)

## Context
`_inputs/api-docs-fin.md` is generated from the implemented backend's OpenAPI document and
emits no governance `API-*` id — it knows verbs, paths and DTOs, nothing about the factory's
id grammar. Two contracts read that file expecting ids in it: C8.2/C8.3 (the api-docs and
`registry-exec-be` must name the same API ids) and C9.5 (every `API-*` the frontend plan
cites must be defined in the api-docs).

Two facts about the surface:

1. The published surface is exactly 37 endpoints, and `backend-execution-plan-fin.md`
   defines exactly `API-FIN-001 .. API-FIN-037`. Matched on verb + path the mapping is 1:1
   with no shape diff — every planned verb and path is the published verb and path.
2. `registry-exec-be-fin.md` still reads `API-FIN-001 .. API-FIN-032`. The five endpoints
   added after that registry was last written — API-FIN-033 (fiscal-period search),
   API-FIN-034, API-FIN-035, API-FIN-036, API-FIN-037 (the four deactivates) — are in the
   backend plan and in the SRS Part B tables, but never reached the registry. `gov.py
   analyze` already reports this against P3.1 as five C7.4 findings.

## Decision
An **API ID BINDING** annex is added to `_inputs/api-docs-fin.md`, following the precedent of
`_inputs/api-docs-sec.md` (ADR-SEC-004): one row per `API-FIN-*`, binding it to the endpoint
this document publishes, matched on verb and path. No endpoint is invented, no id is
re-numbered, and the generated body below the annex is untouched.

The annex binds all 37, including 033–037. The frontend is planned against the surface that
exists, not against a registry line that has fallen behind it.

## Consequences
- C9.5 resolves: every `API-FIN-*` the frontend plan cites is now defined in the api-docs.
- C8.3 resolves in the registry→artifact direction: all 32 registered ids are in the annex.
- C8.2 will report five findings in the artifact→registry direction — API-FIN-033..037 are
  in the api-docs and absent from `registry-exec-be`. Those findings are **true**, and their
  fix is one line in the backend registry's ID RANGES, which is P3.1's artifact and outside
  this stage's boundary (§8: P3.2 references `API`, never writes a backend artifact). They
  are recorded here rather than hidden by binding only the first 32 — binding 32 would have
  made the checker quiet and the plan wrong about the surface it is written against.
- No `REQ-*` changes and no operation is added or removed by this decision.
