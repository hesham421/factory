# ADR-FIN-004 — lookup values are read through the lookup module's consumer API, and each such field mints a UXD

Module  : FIN     Version : v1     Stage raised : P3.2 (Frontend — UX Design + Execution Plan)
Status  : ACCEPTED (non-breaking)

## Context
`profiles/erp.yaml → conventions.lookups` requires every LOV value to be runtime-loaded from
the lookup module, with no hardcoded enum in an API or a field spec. FIN owns 13 lookup keys
(`srs-fin.md` §A6) and registers all of them into MDL as data (REQ-FIN-045); it stores only
codes and keeps no display text of its own (`erp-domain-standards.md` §2.3).

`_inputs/api-docs-fin.md` publishes no lookup endpoint. It cannot: the values live in MDL,
and the endpoint that serves them is MDL's own consumer read, `API-MDL-011`
(`GET /api/v1/mdl/lookups`, query param `type` = the lookup key; response
`List<LookupValueResponse>`, active values only, ordered by `sortOrder`, `nameAr`/`nameEn` per
value — `backend-execution-plan-mdl.md` → API-MDL-011), which is a gated endpoint of another
module, not of FIN.

Twelve of the 13 keys are actually displayed on a FIN screen. `PAYMENT_METHOD` is registered
by REQ-FIN-045 but no FIN column or field cites it in this version, so no screen shows it.

## Decision
Every FIN field whose displayed label comes from a lookup value is a cross-module display
dependency in §A.5's sense — a screen this module owns, showing data whose authoritative
source is another module's real API — and mints a `UXD-*`. One `UXD-*` per lookup key, not
per screen occurrence: the key is the unit the single shared hook is built on, and minting
the same dependency twelve times over for twelve screens would record the same fact twelve
times.

`UXD-FIN-001 .. UXD-FIN-012` are minted accordingly, one per displayed key, each naming the
screens that display it and each resolving through API-MDL-011.

The cross-module endpoint is named in `ui-ux-spec-fin.md`, where the `UXD-*` are defined.
`frontend-execution-plan-fin.md` cites the `UXD-*` and never the foreign path or the foreign
API id: C9.5 requires every `API-*` cited in that plan to be defined in FIN's own api-docs,
and a foreign module's id is by construction not.

## Consequences
- One shared hook per key, long-lived cache, shared across every screen that shows the key;
  a lookup field is a `string` holding the code everywhere in the models, and no enum and no
  union of literals is modelled anywhere in the plan.
- `LOOKUP_VALID` validators bind to the runtime-loaded option list, never to a static list.
- If MDL has not seeded a key, its select renders empty and the field stays a required code
  the user cannot satisfy — a deployment-data condition (REQ-FIN-045 onboarding), not a
  frontend fallback. No default value is invented client-side.
- `ACCOUNTING_EVENT_TYPE` is host-defined and seeded with zero values (§A6); its select is
  legitimately empty until a host registers event types.
- No `REQ-*` changes.
