<!-- source: content outside every PHASE block (leading / between / trailing sections) -->
# FRONTEND EXECUTION PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Track : frontend
Framework : react-ts-vite (profile.stack.frontend.framework) · routing react-router ·
            server-state tanstack-query · forms react-hook-form · validation zod ·
            state useState/useReducer + Context (no global store by default)
Inputs : srs (v1, PRD-approved), prd (v1), api-docs (v1, published by the backend repo),
         registry-srs (v1), registry-exec-be (v1)
Screens : 2 — SCR-MDL-001..002 · UXD : 1 — UXD-MDL-001 · API bound : 11 / 11
Open ADRs : 7 — erp/decisions/MDL/ (ADR-MDL-001..007, all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

## API SURFACE — MDL v1   (source: `_inputs/api-docs-mdl.md` — the ONLY endpoint source)

```
ENDPOINTS   11 — API-MDL-001..011, bound to the published surface by the API ID BINDING annex
            of the api-docs (ADR-MDL-001). Envelope: every response is wrapped in
            ApiResponse<T> { success, data, error { code, message, fieldErrors[] }, timestamp }.
            Paging constraints (PageableBuilder): default page 0 · default size 20 · maximum
            size 200. THREE response shapes, and the difference matters to every F2 block:
              · Page<T> — API-MDL-001 and API-MDL-005 alone
              · a bare array — API-MDL-009 (the reordered values), API-MDL-010
                (OwnerGroupResponse[]) and API-MDL-011 (LookupValueResponse[]); none of these
                carries a paging envelope and none may be read as one
              · a single object — API-MDL-002, 003, 004, 006, 007, 008
            Two reads and one browse are POST `…/search` with a `filters[] {field, operator,
            value}` envelope rather than GET with query params (operators EQUALS, NOT_EQUALS,
            LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN) —
            which is what the SRS B5 tables state too; only the backend plan's contract table
            still predicts GET (ADR-MDL-002). API-MDL-010's request carries `filters` alone,
            with no sort and no paging.
ERRORS      business codes, each already carrying its ar/en text in the module's catalog:
            MDL-400-REORDER-MISMATCH (400) · MDL-404-TYPE · MDL-404-VALUE · MDL-404-TYPE-KEY
            (404) · MDL-409-MODULE-NOT-REGISTERED [RULE-MDL-001] · MDL-409-TYPE-DUP ·
            MDL-409-VALUE-DUP [RULE-MDL-002] (409) · framework codes VALIDATION_ERROR (400) ·
            DATA_INTEGRITY_VIOLATION (409) · ACCESS_DENIED (403) · INTERNAL_ERROR (500).
            Routing is uniform across every F2 block: field validation → inline · business
            rule → user message · unauthenticated → login · forbidden → the localized
            forbidden message · server → generic.
LOOKUPS     **none.** SRS §A6 records that MDL introduces no coded list of its own — it is the
            mechanism every other module's lists run on. No field on either screen is a
            lookup-backed code, no lookup hook exists anywhere in this plan, and no enum is
            modelled. The one cross-module dependency, UXD-MDL-001, is the owner-module field,
            whose valid set the security module owns (ADR-MDL-004) — not lookup data, and not
            read through API-MDL-011.
PERMISSIONS declared by the backend and read from the SRS Access summary and the backend
            registry, never redeclared here: PERM_MDL_LOOKUPS_VIEW / _CREATE / _UPDATE /
            _DELETE · PERM_MDL_TYPE_REGISTRY_VIEW.
            No MDL endpoint publishes the caller's own permission set: the screen gate is the
            security module's effective menu (SEC-FE below), and no `PERM_*` name is composed
            at runtime.
```

### Reconciliation against the SRS — run once, before any F-content

- **Every REQ that needs an endpoint has one.** REQ-MDL-001..013 map onto API-MDL-001..011
  with no gap; the mapping is the traces of the F2 blocks below.
- **Every documented endpoint maps to a REQ.** All 11 are bound; none is unknown and none is
  used without a REQ behind it.
- **Naming and shape differences** — three reads are POST `…/search` where the backend plan's
  contract table predicted GET. The api-docs and the SRS B5 tables agree with each other; the
  backend plan is the one artifact that lags, and `gov.py analyze` reports it there as C8.4.
  The frontend binds to the published shape (ADR-MDL-002).
- **Operations the SRS names with no published endpoint** — `activate` at either level, and
  the by-id reads of a type and of a value. None is required by a `REQ-*`, so none is
  breaking; each is omitted rather than faked (ADR-MDL-005).
- **Endpoints published but not called by this frontend** — API-MDL-011 alone, the consumer
  read another module's backend performs over the platform's in-process module interface
  (ADR-MDL-007). It is bound and blocked out in F2 below.
- **One screen's form differs from its SRS Part B input list** — SCR-MDL-001 renders
  `isActiveFl` read-only at both levels although B3 lists it among the detail inputs; no
  published write DTO accepts it and the deactivate endpoints are what change it
  (ADR-MDL-006).
- **Nothing is invented.** No value absent from the api-docs appears in this plan, and no
  permission name, route or component is derived from anything but the SRS, the api-docs and
  the profile's own stack.

## EXECUTION PLAN INDEX — MDL v1 — frontend-execution-plan-mdl.md

| # | Phase | Split | Blocks |
|---|---|---|---|
| 1 | F1 — Models & Types | always — one SUB per screen | 2 SUB |
| 2 | F2 — Data Hooks | always — one SUB per screen | 2 SUB |
| 3 | F3 — Forms & Validators | always — one SUB per screen | 2 SUB |
| 4 | F4 — Screens & Routes | always — one SUB per screen | 2 SUB |
| 5 | SEC-FE | never split | level-1 only |
| 6 | ALIGN-FE | never split | level-1 only |

**SCREEN REGISTRY**

| SCR | Name (ar / en) | Page code | Container pattern | Owning ENT |
|---|---|---|---|---|
| SCR-MDL-001 | اللوكبات العامة / Generic Lookups | MDL_LOOKUPS | TREE_MASTER_DETAIL | ENT-MDL-001 نوع اللوكب / LookupType (+ ENT-MDL-002 قيمة اللوكب / LookupValue) |
| SCR-MDL-002 | سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner | MDL_TYPE_REGISTRY | FULL_PAGE (no entry sub-view — ADR-MDL-003) | ENT-MDL-001 نوع اللوكب / LookupType |

Two screens, and every `sub_bearing` phase still splits per screen — one `SUB` per `SCR-*`,
at any screen count. The four phases below therefore carry two SUB blocks each, and every SUB
id is phase-qualified: `SUB:F1-SCR-MDL-001` and `SUB:F2-SCR-MDL-001` are distinct blocks for
the same screen under different phases.

These phases carried a `split_threshold` of `SCR >= 5` until 2026-09-12, which would have left
this module — and every small module after it — with a package whose folder tree differed from
a large module's for no reason a reader could act on. The gate was removed at its source in
`profiles/erp.yaml`, not worked around here; `shared/MARKER-PROTOCOL.md` now renders these four
rows as `per screen`.













---

## Hand-off

The implementer reads the phases in profile order — F1 models, F2 hooks, F3 forms, F4 screens
and routes, SEC-FE guards — takes design intent from `ui-ux-spec-mdl.md`, and takes every
request and response shape from `_inputs/api-docs-mdl.md`. No route, component, permission or
field that is not traceable to an F-block above is invented: a gap is an ADR in
`erp/decisions/MDL/`, never an invention. Three response shapes travel in this module and the
difference is load-bearing — two paged reads, five bare arrays or single objects, and the rest
single objects — so no block may be read through an envelope another block declares. The plan
and its registry are split by the toolkit into `packages/frontend-execution/` and delivered on
the frontend delivery branch after the `gate:pass-2` verdict, then tagged.

══════════════════════════════════════════════════════════════════
