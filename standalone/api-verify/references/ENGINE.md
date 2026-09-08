{#- ─────────────────────────────────────────────────────────────────────────
    ENGINE.md — {{ stage.id }} (standalone, post-implementation) · rendered at
    brief-build time (Jinja2). Context: profile · factory · stage · mod · version
    Facts come from factory.yaml + profiles/<id>.yaml only (C1/C2).
   ───────────────────────────────────────────────────────────────────────── -#}
{%- set st = (factory.stages + factory.standalone) | selectattr('id', 'equalto', stage.id) | first -%}
{%- set api = profile.stack.backend.api -%}
{%- set db = profile.stack.db -%}
{%- set conv = profile.conventions or {} -%}
{%- set sec = conv.get('security_model') -%}
{%- set langs = profile.languages -%}
{%- set testing = profile.stack.testing -%}
{%- set MOD = (mod | default('MOD')) | upper -%}
{%- set ver = version | default(1) -%}
{%- set state_dir = factory.paths.module.state_dir -%}
{%- set inputs_dir = factory.paths.module.inputs_dir -%}
{%- set api_docs = factory.inputs['api-docs'].file.replace('{mod}', MOD | lower) -%}
{%- set script = (st.produces | selectattr('artifact', 'equalto', 'api-verify-script') | first).file.replace('{mod}', MOD | lower) -%}
{%- set report = (st.produces | selectattr('artifact', 'equalto', 'api-verify-report') | first).file.replace('{mod}', MOD | lower) -%}
```
ENGINE        : {{ stage.id }} — {{ st.title }}   (STANDALONE — post-implementation)
LANE          : {{ st.lane }} · questions {{ st.questions }}
MODULE        : {{ MOD }} · v{{ ver }} · profile {{ profile.identity.id }} ({{ profile.identity.display }})
READS         : {% for i in st.inputs %}{{ i }}{% if not loop.last %} · {% endif %}{% endfor %}   ("?" = optional)
PRODUCES      : {{ script }} · {{ report }}
OWNS IDS      : {% if st.owns_ids %}{{ st.owns_ids | join(', ') }}{% else %}none — it mints no ID{% endif %}
BOUNDARY      : runs OUTSIDE the factory boundary ({{ factory.factory.boundary }}), never inside a pass
```

# {{ st.title }} — engine reference

## 0. Position

This engine runs **after** the backend module has been implemented and its api-docs
published, on demand (`/{{ (factory.commands | selectattr('id', 'equalto', 'api-verify') | first).id }}`).
It sits outside the factory boundary: no pass includes it, no gate waits for it, and its
result never changes a line artifact. Its job is **translation, not derivation** — it turns
already-governed specifications into one runnable verification script that exercises the
real API in dependency order, plus a report of what it found.

It designs no test and invents no rule, message, dependency or data value. Anything not
traceable to an input document is skipped and named as skipped. Questions are
`{{ st.questions }}`; a real blocker (an unresolvable dependency cycle, an ambiguous
payload) becomes an ADR per `factory.yaml → ambiguity` and the run stops there.

## 1. Inputs and tiers

| Input | Read from | Role |
|---|---|---|
| `api-docs` | `{{ inputs_dir }}/{{ api_docs }}` (published at `{{ factory.repos.backend.publishes['api-docs'] }}`) | **mandatory** — endpoints, verbs, paths, request/response field tables, examples, error codes |
| `test-execution-manifest` | `{{ state_dir }}/{{ factory.naming.current_state_file.replace('{artifact}', 'test-execution-manifest') }}.md` (from `test-gen`, when `profile.stack.testing.manifest` is true{% if not testing.manifest %} — **false for this profile**{% endif %}) | optional — pre-computed dependency order, RULE → code → TC triples, entity CRUD checklist |
| base URL · credentials · auth endpoint | the run's arguments | optional — placeholders otherwise (§6) |

| Tier | Present | Generates |
|---|---|---|
| **Full** | api-docs + manifest | happy-path CRUD per entity **and** negative (rule-violation) tests; dependency order and triples read from the manifest — zero self-derivation, even if other artifacts are also attached |
| **Minimal** | api-docs only | happy-path CRUD only; FK order inferred from FK-typed fields and "parent …" descriptions in the request tables; the report states that negative cases were skipped and why |

State the tier at the start of the run. When the manifest is present, re-deriving what it
already holds is a boundary violation.

Multi-batch api-docs (a large module documented across several files): reconcile received
endpoints against the manifest's CRUD checklist (or the catalogue the api-docs carry),
report entity-level coverage briefly, never ask — when a batch trails off, generate what is
documented and list every entity without a documented create endpoint as *out of scope for
this run*; one function per entity lets a later batch append without a rewrite.

## 2. Stack conventions (from the profile — never assumed)

| Convention | Value | Use in the script |
|---|---|---|
| base path | `{{ api.base_path }}` | every path is an instance of it; the module segment is `{{ MOD | lower }}` |
| verbs | {% for v, m in api.verbs.items() %}`{{ v }}`={{ m }}{% if not loop.last %} · {% endif %}{% endfor %} | operation type per endpoint (create / read / search / update / {{ api.verbs.get('DELETE') | default('delete', true) }} / partial) |
| response envelope | {{ api.get('envelope') | default('none declared', true) }} | unwrap before asserting on data |
| paging envelope | {{ api.get('paging') | default('none declared', true) }} | search assertions read the page fields the api-docs document (page number, size, total, content list) — confirm names in the api-docs; an undocumented field is a documentation gap to flag, not an assertion |
| error envelope | {{ api.get('error_envelope') | default('none declared', true) }} | negative assertions check HTTP status + the runtime `code`; the runtime code format is the one the api-docs / manifest state — never the hyphenated governance ID |
| languages | {{ langs.all | join(', ') }} (primary `{{ langs.primary }}`) | message presence asserted per language field the envelope carries; assertion text and report language = `{{ langs.primary }}`{% if langs.all | length > 1 %} with `{{ langs.all | reject('equalto', langs.primary) | join('/') }}` beside it{% endif %} |
| {{ api.verbs.get('DELETE') | default('DELETE', true) }} semantics | {% if (db.naming or {}).get('flag_suffix') %}soft — active flag (suffix `{{ (db.naming or {}).get('flag_suffix') }}`){% else %}as the api-docs document{% endif %} | cleanup strategy (§3 stage F) |
{% if sec %}| permissions | `{{ sec.permission_pattern }}`, gateway `{{ sec.gateway_action }}` | a forbidden call asserts the forbidden status through the error envelope |
{% endif %}
## 3. Processing pipeline

**A — Inventory.** Parse every documented endpoint: id (`API-*` when the docs carry it),
verb, path, entity (path segment), operation type (from verb + path suffix), request field
table (name, type, required, constraints, example), response shape.

**B — Dependency order.** Full tier: read the manifest's DEPENDENCY ORDER as-is. Minimal
tier: infer edges from FK-typed fields whose description names a parent, then sort
topologically; roots first. A cycle or an unresolvable edge → ADR, stop.

**C — Negative mapping.** Full tier: for each manifest triple (RULE → code → TC, HTTP): set up
the precondition the RULE describes, call the endpoint that must be blocked, assert the HTTP
status and the runtime code, tag the function with RULE/TC ids. Minimal tier: none — say so.
Informational-only RULEs are excluded (the manifest already does this).

**D — Assembly.** One fixed structure (§4), one `test_<entity>()` per entity in stage-B order,
FK ids threaded as parameters from the parent's return value — never hard-coded.

**E — Exploratory scenarios (bounded).** Only for fields with `required = yes` or a stated
constraint (length, numeric range): at-limit / one-over, omission, type mismatch, an
undocumented lookup value, CRUD idempotency (deactivate twice, activate active), invalid FK
reference. **Assert vs observe:** an outcome governed by a RULE + code is stage C's; any
other expected status is undocumented → executed as an *observation* (recorded, never
pass/fail, listed apart in the report). No documented source value → skip.

**F — Teardown.** Every created id is tracked per entity; cleanup runs in `finally`, in
reverse dependency order; a hard-delete endpoint is used only when the api-docs document
one, otherwise the {{ api.verbs.get('DELETE') | default('deactivate', true) }} endpoint is called and the report
states that records remain (deactivated) — never a silent "cleaned up".

**G — Problems report.** The report `{{ report }}` lists only failures, bucketed: *likely real
bug* (a documented rejection did not happen, or an unexplained status), *test assumption
mismatch* (rejected, but with a status the manifest did not state — fix the expectation, not
the backend), *infrastructure* (connection / timeout — rerun). Ambiguous → *likely real bug*.

**H — Log correlation and database access (opt-in).** Log excerpts around a failing call are
attached as *approximate* unless a trace id exists. Database writes are two-tier: deleting
rows this run created (tracked ids only) is allowed for teardown; any other data fix is
emitted as *suggested SQL* for a human — never executed. All DB writes sit behind an
explicit opt-in flag (default off = print only), in a transaction, with separate credentials.

## 4. Script structure — `{{ script }}`

The file extension of the produced artifact decides the language (`factory.standalone` →
`{{ script.split('.') | last }}`). Structure (a fixed skeleton the run extends, never redesigns):

```
# Intended for Dev/Test environments only.
config      : BASE_URL (argument or localhost placeholder) · credentials (placeholders unless given) · auth endpoint · DB opt-in flag
client      : thin HTTP wrapper (get / post / put / patch / delete as the api-docs need) that unwraps {{ api.get('envelope') | default('the response', true) }}
results     : TestResult / TestSuite records · run() for asserted calls · run_observation() for stage-E observations (separate bucket, never in totals)
helpers     : extract_token · extract_id · first id of a page (per {{ api.get('paging') | default('the documented page shape', true) }})
per entity  : test_<entity>(parent_ids…) → create → get-by-id (ok) → get-by-id (missing id → not found) → update → [stage C negatives] → [stage E observations] → deactivate → activate ; appends created ids
cleanup()   : stage F
report      : HTML/Markdown with pass/fail suites, an "observations" section, and the problems buckets → {{ report }}
main()      : suites in stage-B order inside try/finally; exit non-zero on any asserted failure (observations never affect the exit code)
```
Every test function carries a traceability comment: `Covers: API-… ; Negative: RULE-… / <code> / TC-…`.

Payload rules: use the api-docs `example` values verbatim; a required field without an
example gets a clearly marked placeholder of the right type; lookup / enum values only as
seen in the docs; FK ids threaded, never literal.

## 5. Generation gate (silent; only failures are reported)

```
[ ] every entity in the api-docs has a test_<entity>() function
[ ] main() order = stage-B order — no forward FK reference
[ ] every payload value comes from an example or a marked placeholder
[ ] negatives only where RULE + code + TC resolve (Full tier) — none self-derived beside a present manifest
[ ] exploratory scenarios only on required/constrained fields; undocumented outcomes use run_observation()
[ ] every create appends its id; cleanup() in finally, reverse order; hard-delete used only if documented
[ ] runtime error codes in the format the docs/manifest state; page fields as documented
[ ] no invented credentials, business codes or lookup values; traceability comment on every function
```

## 6. Safety

Credentials are placeholders unless supplied in the run; the script targets only the
supplied base URL or a localhost default; DB writes are opt-in and scoped to ids this run
created; the report never presents an approximate log correlation as a confirmed root cause.

## 7. Boundaries

| Consumes (read-only) | Produces | Never |
|---|---|---|
| api-docs, the manifest{% if not testing.manifest %} (not emitted for this profile){% endif %}, run arguments | `{{ script }}`, `{{ report }}` | an ID of any kind, a change to any line artifact, a gate verdict, a data fix against records it did not create |
