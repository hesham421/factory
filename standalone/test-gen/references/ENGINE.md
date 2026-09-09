{#- ─────────────────────────────────────────────────────────────────────────
    ENGINE.md — {{ stage.id }} (standalone) · rendered at brief-build time (Jinja2)
    Context: profile · factory · stage · mod · version
    Facts come from factory.yaml + profiles/<id>.yaml only (C1/C2).
   ───────────────────────────────────────────────────────────────────────── -#}
{%- set st = (factory.stages + factory.standalone) | selectattr('id', 'equalto', stage.id) | first -%}
{%- set testing = profile.stack.testing -%}
{%- set api = profile.stack.backend.api -%}
{%- set conv = profile.conventions or {} -%}
{%- set sec = conv.get('security_model') -%}
{%- set langs = profile.languages -%}
{%- set MOD = (mod | default('MOD')) | upper -%}
{%- set ver = version | default(1) -%}
{%- set state_dir = factory.paths.module.state_dir -%}
{%- set atoms = factory.ids.atoms -%}
{%- set tc_kind = factory.markers.kinds.TC -%}
```
ENGINE        : {{ stage.id }} — {{ st.title }}   (STANDALONE — outside the line, on demand)
LANE          : {{ st.lane }} · questions {{ st.questions }} · derives from `{{ st.derives_from }}-*`
MODULE        : {{ MOD }} · v{{ ver }} · profile {{ profile.identity.id }} ({{ profile.identity.display }})
READS         : {% for i in st.inputs %}{{ i }}{% if not loop.last %} · {% endif %}{% endfor %}   (from {{ state_dir }}/ — "?" = optional)
PRODUCES      : {% for a in st.produces %}{{ a.file.replace('{mod}', MOD | lower) }}{% if a.get('optional') %} (optional){% endif %}{% if not loop.last %} · {% endif %}{% endfor %}
OWNS IDS      : {% for x in st.owns_ids %}{{ x }}{% if not loop.last %}, {% endif %}{% endfor %}
FRAMEWORK     : backend `{{ testing.get('backend') | default('agnostic', true) }}` · frontend `{{ testing.get('frontend') | default('agnostic', true) }}` · manifest {{ 'ON' if testing.manifest else 'OFF' }}   (profile.stack.testing)
BOUNDARY      : {{ factory.factory.boundary }} — test PLANS, never test code; never a gate for the core
```

# {{ st.title }} — engine reference

## 0. Position

This engine runs **outside the governed line** (`factory.yaml → standalone`). No pass gates
on it, it gates nothing, and the pass gates never wait for it. It is invoked on demand
(`/{{ (factory.commands | selectattr('id', 'equalto', 'test-gen') | first).id }}`) once the
artifacts it consumes exist in `{{ state_dir }}/`. It **invents nothing**: no rule, error,
endpoint, field or screen — it only adds test cases and the indexes derived from them.

Questions are `{{ st.questions }}`; ambiguity → `factory.yaml → ambiguity` (ADR, then
`{{ factory.ambiguity.non_breaking.then }}`; breaking → `{{ factory.ambiguity.breaking.status }}`,
`{{ factory.ambiguity.breaking.then }}`) — shared/GOVERNANCE-CORE.md.

Delta versions: read `{{ state_dir }}/` as the baseline, emit only ADDED / MODIFIED / REMOVED
test cases, continue the `TC` sequence — shared/VERSIONING.md.

## 1. Inputs

| Input | Read from | Use |
|---|---|---|
{% for raw in st.inputs -%}
{%- set i = raw.rstrip('?') -%}
| `{{ i }}`{% if raw.endswith('?') %} (optional){% endif %} | `{{ state_dir }}/{{ factory.naming.current_state_file.replace('{artifact}', i) }}.md` | {% if i == 'srs' %}**the derivation source**: every `REQ-*` with its `AC-*` (Given / When / Then), `RULE-*` messages, screens, permissions{% elif 'backend-execution' in i %}`API-*` (verb, path, request/response, catalog codes) to bind backend steps to endpoints{% elif 'frontend-execution' in i %}`SCR-*`, routes, F-blocks to bind frontend steps to screens{% else %}ID ranges, coverage of REQ by API/SCR{% endif %} |
{% endfor %}
A missing optional plan → the corresponding test plan is written in **REDUCED** mode
(steps reference the AC only, no endpoint/screen binding) and says so in its header.

## 2. Derivation — every `TC-*` comes from an `AC-*`

`TC-*` (`{{ factory.ids.pattern.replace('{prefix}', 'TC').replace('{MOD}', MOD) }}`, {{ factory.ids.seq_width }}-digit seq,
one continuous sequence across the module — both plans share it, so no TC id repeats) traces → {{ atoms.TC.traces_to | join(' + ') }}. The
derivation is **mechanical**:

| AC part | becomes |
|---|---|
| **Given** | preconditions — data state, role/permission, system state (bound to real entities/screens from the plans) |
| **When** | the step list — for backend: the endpoint call (`API-*`, verb, path, payload from the AC); for frontend: navigation + user actions on `SCR-*` |
| **Then** | expected result — status/response (per `{{ api.get('error_envelope') | default('the error envelope', true) }}` when a RULE fires) or UI state; message asserted in every language ({{ langs.all | join(', ') }}) |

Rules:
1. one `TC-*` per `AC-*`, always — an AC without a TC is a coverage gap (✗), never skipped;
2. an AC whose Then names a `RULE-*` violation yields the **violation** TC; its happy-path
   twin exists only if another AC states it — do not fabricate happy paths;
3. a **boundary** TC is added only when the AC (or the RULE it cites) states a numeric limit;
4. every TC cites, besides its AC: the `REQ-*`, and the `API-*` (backend) or `SCR-*`
   (frontend) it exercises, plus the `RULE-*` / catalog code when a violation is expected;
5. never reword a rule, message or endpoint — reference by ID/code; message text is copied
   character-perfect from the SRS in every language;
6. over-engineering guard: if a track's TC count exceeds ~2× its AC count, review — the
   extra TCs are almost always fabricated variants; remove them.

Scenario tags (one per TC): `HAPPY | VIOLATION | BOUNDARY | PERMISSION | STATE | INTEGRATION`;
data class: `VALID | INVALID | BOUNDARY | EDGE | ATTACK`.
{% if sec %}Permission ACs (no `{{ sec.gateway_action }}` / no action permission) produce `PERMISSION` TCs on both tracks.{% endif %}

## 3. TC block — framework-agnostic form

```
<!-- TC:TC-{{ MOD }}-<seq>:START traces=AC-{{ MOD }}-<seq>,REQ-{{ MOD }}-<seq>[,API-{{ MOD }}-<seq>|SCR-{{ MOD }}-<seq>] -->
### TC-{{ MOD }}-<seq> — <title>
Derived from : AC-{{ MOD }}-<seq>  (REQ-{{ MOD }}-<seq>)
Exercises    : API-{{ MOD }}-<seq> <verb path>   |   SCR-{{ MOD }}-<seq> <route>
Rule / code  : RULE-{{ MOD }}-<seq> → <catalog code> | —
Scenario     : <tag> · data class <class> · language <{{ langs.all | join('|') }}|ALL>
Preconditions: <from Given — concrete entities, role, state>
Steps        : 1. … 2. … (from When — one observable action per step)
Expected     : <from Then — status / body shape / message per language / UI state>
Test data    : <values named in the AC; placeholders marked, never invented business data>
<!-- TC:TC-{{ MOD }}-<seq>:END -->
```
Framework: {% if (testing.get('backend') | default('agnostic', true)) == 'agnostic' and (testing.get('frontend') | default('agnostic', true)) == 'agnostic' %}`profile.stack.testing` is **agnostic** on both tracks — the block above is the whole
contract; the consumer repo chooses its tool and turns each TC into a test. No framework
name, annotation or file layout is mentioned anywhere in the plan.{% else %}`profile.stack.testing` names a framework
(backend `{{ testing.get('backend') | default('agnostic', true) }}`, frontend `{{ testing.get('frontend') | default('agnostic', true) }}`). The
block above stays the contract; add one "framework note" line per plan header (naming
convention / grouping the framework expects) — still no code, no scaffolding.{% endif %}

## 4. Test plans — organised by the profile's test phases

Each track with a `test` plan in the profile gets one file, wrapped in the profile's test
phases with `TC` atoms (kind `TC`, level {{ tc_kind.level }}, parents {{ tc_kind.allowed_parents | join('/') }},
plans {{ tc_kind.plans | join('/') }}). Test-plan SUB ids are **bare** labels
(`factory.markers.rules.sub_unqualified_exempt_plans` = {{ factory.markers.rules.sub_unqualified_exempt_plans | join(', ') }}).
{% for tr, tdef in profile.tracks.items() if tdef.plans.get('test') %}
### Track `{{ tr }}` — `{{ (st.produces | selectattr('track', 'defined') | selectattr('track', 'equalto', tr) | first).file.replace('{mod}', MOD | lower) }}`

| Phase key | Split rule | SUB labels |
|---|---|---|
{% for p in tdef.plans.test.phases -%}
| `{{ p.key }}` | {% if p.get('never_split') %}never split{% elif p.get('split_threshold') %}SUB when {{ p.get('split_threshold').kind }} count {{ p.get('split_threshold').op }} {{ p.get('split_threshold').count }}{% if p.get('split_threshold').grouping %} — grouped {{ p.get('split_threshold').grouping }}{% endif %}{% else %}as the profile describes{% endif %} | {% for l in p.get('sub_labels') or [] %}`{{ l }}`{% if not loop.last %}, {% endif %}{% else %}—{% endfor %} |
{% endfor %}
Layout:
```
<header>   sources ({{ state_dir }} files + versions) · framework note (§3) · REDUCED? · open ADRs
{% for p in tdef.plans.test.phases -%}
<!-- PHASE:{{ p.key }}:START traces=<union of the TCs' REQ/AC> -->
{%- if p.get('sub_labels') %}
  {% for l in p.get('sub_labels') %}<!-- SUB:{{ l }}:START traces=… -->  …TC blocks…  <!-- SUB:{{ l }}:END -->{% if not loop.last %}
  {% endif %}{% endfor %}
  (SUBs only when the threshold is met — decide WHILE writing, from the AC count){% else %}
  …TC blocks…{% endif %}
<!-- PHASE:{{ p.key }}:END -->
{% endfor -%}
TC TRACEABILITY INDEX   AC → TC · REQ → TC · {% if tr == 'backend' %}API → TC · RULE/code → TC{% else %}SCR → TC · RULE/code → TC{% endif %}
COVERAGE                AC covered <n>/<total> (a gap is ✗ and blocks the run) · REQ covered · {% if tr == 'backend' %}API{% else %}SCR{% endif %} covered
```
{% if tr == 'backend' -%}
Backend grouping hint: rule-driven ACs (violations, state transitions) vs endpoint-driven ACs
(happy paths, permission, paging/empty-result per `{{ api.get('paging') | default('the documented envelope', true) }}`).
{%- else -%}
Frontend grouping hint: per-screen flows (search, create/edit, violation shown on screen,
permission-hidden affordance) vs the single module lifecycle flow (create → search → update →
deactivate → gone from active results){% if conv.get('composite_screen') %}; the composite-screen invariant (entry never rendered open by default) is one TC when an AC states it{% endif %}.
{%- endif %}
{% else %}
The profile declares no `test` plan for any track — nothing to produce; report it and stop.
{% endfor %}
## 5. Test-execution manifest {% if testing.manifest %}(ON — `profile.stack.testing.manifest`){% else %}(OFF — `profile.stack.testing.manifest` is false){% endif %}
{% if testing.manifest %}
Emitted in the same run, after the backend test plan, as
`{{ (st.produces | selectattr('artifact', 'equalto', 'test-execution-manifest') | first).file.replace('{mod}', MOD | lower) }}` —
a **derived view** for the `api-verify` standalone (it introduces no ID):
```
DEPENDENCY ORDER      topological entity build order (from FK/XM relations in the backend plan and "must belong to" RULEs)
RULE → CODE → TC      RULE-* │ catalog code (runtime format per {{ api.get('error_envelope') | default('the error envelope', true) }}) │ TC-* │ HTTP │ API-*   (informational-only RULEs excluded)
ENTITY CRUD CHECKLIST ENT-* │ create │ read │ search │ update │ {{ api.verbs.get('DELETE') | default('delete', true) }} │ activate (each ✓ / —, from the API-* set)
```
Regenerate whenever the backend plan or test plan changes — a stale manifest is a defect.
{%- else %}
Not produced for this profile. `api-verify` runs in its minimal tier without it.
{%- endif %}

## 6. Split

The same toolkit splits test plans, with plan key `test`
(`factory.tracks.<track>.packages.test` → {% for tr, t in factory.tracks.items() %}`{{ t.packages.test }}`{% if not loop.last %}, {% endif %}{% endfor %}):
```
gov.py split --track <track> --module {{ MOD }} --version {{ ver }} --plan test --dry-run   # validate, non-zero exit = fix first
gov.py split --track <track> --module {{ MOD }} --version {{ ver }} --plan test
```
Every TC atom is verified by content hash (`factory.markers.rules.verify` = {{ factory.markers.rules.verify }}) after the split.

## 7. Self-check before finishing

```
[ ] every AC-* in the SRS has ≥1 TC-* (coverage ✗ = not done)
[ ] every TC-* carries traces= with its AC-* (+ REQ, API/SCR) and the atom marker pair
[ ] no TC without an AC source; no reworded rule/message/endpoint; test data never invented
[ ] phases = the profile's test phases, in order; SUB labels bare; thresholds checked while writing
[ ] framework wording matches §3; manifest emitted iff profile.stack.testing.manifest
[ ] ADRs written for every derivation choice that was not mechanical
```

## 8. Boundaries

| Owns | References (never redefines) | Never |
|---|---|---|
| `{{ st.owns_ids | join('-*`, `') }}-*`, the test plans{% if testing.manifest %}, the manifest{% endif %} | `REQ/AC/RULE` ({{ atoms.AC.owner }}), `API` ({{ atoms.API.owner }}), `SCR/UXD` ({{ atoms.SCR.owner }}), `DBF/XM` ({{ atoms.DBF.owner }}), catalog codes | test code, framework scaffolding, any edit to a line artifact, any gate or verdict |
