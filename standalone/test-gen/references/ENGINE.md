{#- ─────────────────────────────────────────────────────────────────────────
    ENGINE.md — {{ stage.id }} (standalone) · rendered at brief-build time (Jinja2)
    Context: profile · factory · stage · mod · version (+ scope · mods for
    multi-module / project runs — additive context, see §2 Scope)
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
{%- set scope = scope | default('module') -%}
{%- set sel_mods = (mods | default([MOD])) -%}
{%- set state_dir = factory.paths.module.state_dir -%}
{%- set atoms = factory.ids.atoms -%}
{%- set tc_kind = factory.markers.kinds.TC -%}
{%- set produces_now = st.produces | rejectattr('artifact', 'equalto', 'system-test-index') | list -%}
{%- if scope == 'project' -%}{%- set produces_now = st.produces -%}{%- endif -%}
```
ENGINE        : {{ stage.id }} — {{ st.title }}   (STANDALONE — outside the line, on demand)
LANE          : {{ st.lane }} · questions {{ st.questions }} · derives from `{{ st.derives_from }}-*` (module) + `XM-*`/`UXD-*` (integration)
SCOPE         : {{ scope }} · modules {{ sel_mods | join(', ') }}{% if scope == 'project' %} (every module with a committed version){% endif %}
MODULE        : {{ MOD }} · v{{ ver }} · profile {{ profile.identity.id }} ({{ profile.identity.display }})
READS         : {% for i in st.inputs %}{{ i }}{% if not loop.last %} · {% endif %}{% endfor %}   (from {{ state_dir }}/ — "?" = optional — read for EACH module in scope)
PRODUCES      : {% for a in produces_now %}{{ a.file.replace('{mod}', MOD | lower).replace('{profile}', profile.identity.id) }}{% if a.get('optional') %} (optional){% endif %}{% if not loop.last %} · {% endif %}{% endfor %}
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
endpoint, field, screen or cross-module flow — it only adds test cases and the indexes
derived from them.

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
| `{{ i }}`{% if raw.endswith('?') %} (optional){% endif %} | `{{ state_dir }}/{{ factory.naming.current_state_file.replace('{artifact}', i) }}.md` | {% if i == 'srs' %}**the derivation source**: every `REQ-*` with its `AC-*` (Given / When / Then), `RULE-*` messages, screens, permissions{% elif 'backend-execution' in i %}`API-*` (verb, path, request/response, catalog codes) to bind backend steps to endpoints; its `XM-*` blocks (target module, type HARD-FK/SOFT-READ, traces) are the **integration derivation source** on the backend track{% elif 'frontend-execution' in i %}`SCR-*`, routes, F-blocks to bind frontend steps to screens; its `UXD-*` references (screen, foreign field, owner module) are the **integration derivation source** on the frontend track{% elif i == 'registry-db' %}the module's `XM-*` register (target module, type) — cross-checked against the `XM` blocks above, never restated{% elif i == 'registry-exec-fe' %}the module's `UXD-*` register (screen, field, owner module, API used) — cross-checked against the `UXD-*` references above, never restated{% else %}ID ranges, coverage of REQ by API/SCR{% endif %} |
{% endfor %}
A missing optional plan → the corresponding test plan is written in **REDUCED** mode
(steps reference the AC only, no endpoint/screen binding) and says so in its header. A
missing `registry-db`/`registry-exec-fe` never blocks module-scope derivation — it only
narrows what integration-scope cross-checking can do.

## 2. Scope — a command flag, never prose

```
gov.py run-standalone test-gen --module MOD                 # this run: scope=module, mods=[MOD]
gov.py run-standalone test-gen --modules MOD-A,MOD-B,…       # this run: scope=modules, mods=[MOD-A, MOD-B, …]
gov.py run-standalone test-gen --scope project               # this run: scope=project, mods=every module with a committed version
```

This run: **scope = `{{ scope }}`**, modules = `{{ sel_mods | join(', ') }}`.

| Scope | TC sources | Phases populated |
|---|---|---|
| `module` | `AC-*` of the one module (§3) | the module-scope phases only (`{{ profile.tracks.backend.plans.test.phases | rejectattr('integration') | map(attribute='key') | join(', ') }}` on backend; the equivalent on frontend) — **identical in shape to a single-module run today** |
| `modules` | `AC-*` per module (§3) **+** `XM-*` (§4) and `UXD-*` (§5) between the *selected* modules only | module-scope phases for every selected module, plus the integration phase(s) (`profile…phases[*].integration: true`) wherever a real linking atom pairs two selected modules |
| `project` | everything `modules` does, across **every** module the factory has ever produced a version for, **plus** a derived coverage rollup | the same as `modules`, plus `system-test-index-{{ '{profile}' }}.md` (§9) — no new atom, no new gate |

Rules that hold at every scope:
1. a module never gets an integration TC for a module that is **not** in the current
   selection — running `--module {{ MOD }}` alone never touches another module's `XM`/`UXD`;
2. an integration phase with no real linking atom among the selected modules stays **absent**
   from the output — never an empty `PHASE` block, never a guessed pairing;
3. `--module` output is produced exactly as it always was — no integration phase key, no
   `system-test-index`, no extra section — so a single-module run stays byte-identical in
   shape to before this scope model existed.

## 3. Derivation (module scope) — every `TC-*` comes from an `AC-*`

`TC-*` (`{{ factory.ids.pattern.replace('{prefix}', 'TC').replace('{MOD}', MOD) }}`, {{ factory.ids.seq_width }}-digit seq,
one continuous sequence across the module — both plans share it, so no TC id repeats) traces → {{ atoms.TC.traces_to | join(' + ') }}. The
module-scope derivation is **mechanical**:

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

## 4. XM → TC derivation (integration scope, backend)

Runs only at `scope: modules|project`, and only for an `XM-*` whose **target module** is
also in `{{ sel_mods | join(', ') }}` — an `XM-*` targeting a module outside the selection is
left alone (not this run's concern, not a gap either).

Source: the `XM-*` blocks of the **declaring** (consuming) module's `backend-execution-plan`
(cross-checked against its `registry-db`, never restated — [XM-PROTOCOL.md](../../../shared/XM-PROTOCOL.md)).
The **declaring module owns the resulting TC** — one continuous `TC-{MOD}-<seq>` sequence,
same rule as module scope (design decision: integration TC ownership follows declaration,
not the target).

| XM type | TC scenario |
|---|---|
| `HARD-FK` | one `EXISTS` TC (the referenced row is present — request/flow succeeds) **and** one `MISSING` TC (the referenced row is absent — the physical constraint is honoured: the documented rejection, never a silent pass) |
| `SOFT-READ` | one `GRACEFUL-DEGRADATION` TC — the target read fails or returns empty and the declaring module's flow still returns a defined result (never a 500 / unhandled state) |

Rules:
1. never invent the target entity's shape — bind by `ENT`/`DBF` ID only, as the `XM` block
   already does; the TC exercises the declaring module's own `API-*`, not the target's;
2. tag every such TC `INTEGRATION`, data class per the row above;
3. `traces=` carries the `XM-*` id plus the `REQ-*` the XM itself traces to (and the `API-*`
   exercised, when the plan binds one) — never an `AC-*` that does not exist for it;
4. one `XM-*` never yields more than the two/one TC(s) in the table above — no fabricated
   extra scenarios ("over-engineering guard" of §3 applies here too).

## 5. UXD → TC derivation (integration scope, frontend)

Runs only at `scope: modules|project`, and only for a `UXD-*` whose **owner module** (the
module that owns the displayed data) is also in `{{ sel_mods | join(', ') }}`.

Source: the `UXD-*` references of the **displaying** module's `frontend-execution-plan`
F4 blocks (cross-checked against its `registry-exec-fe`, never restated). The **displaying
module owns the resulting TC** (it is the one whose screen renders the foreign field).

| UXD case | TC scenario |
|---|---|
| foreign field rendered | one TC: navigate to the `SCR-*`, the foreign-owned field renders the value the owner module's API returns |
| foreign field empty / owner API failure | one TC: the screen shows its declared empty/error state (§A.3 `States` of the ui-ux-spec) — never a blank crash, never invented copy |

Rules:
1. never invent the owner module's field shape or a new permission — the UXD block and the
   owner's real `API-*` (from api-docs, when present in state) are the only sources;
2. tag every such TC `INTEGRATION`; `traces=` carries the `UXD-*` id plus its `REQ-*`/`AC-*`
   and the `SCR-*` it renders on;
3. one `UXD-*` never yields more than the two TCs in the table above.

## 6. TC block — framework-agnostic form

```
<!-- TC:TC-{{ MOD }}-<seq>:START traces=AC-{{ MOD }}-<seq>,REQ-{{ MOD }}-<seq>[,API-{{ MOD }}-<seq>|SCR-{{ MOD }}-<seq>|XM-{{ MOD }}-<seq>|UXD-{{ MOD }}-<seq>] -->
### TC-{{ MOD }}-<seq> — <title>
Derived from : AC-{{ MOD }}-<seq>  (REQ-{{ MOD }}-<seq>)   |   XM-{{ MOD }}-<seq> (REQ-{{ MOD }}-<seq>)   |   UXD-{{ MOD }}-<seq> (REQ-{{ MOD }}-<seq>, AC-{{ MOD }}-<seq>)
Exercises    : API-{{ MOD }}-<seq> <verb path>   |   SCR-{{ MOD }}-<seq> <route>
Rule / code  : RULE-{{ MOD }}-<seq> → <catalog code> | —
Scenario     : <tag> · data class <class> · language <{{ langs.all | join('|') }}|ALL>
Preconditions: <from Given — concrete entities, role, state | for XM/UXD: the target/owner entity present or absent>
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

## 7. Test plans — organised by the profile's test phases

Each track with a `test` plan in the profile gets one file per module, wrapped in the
profile's test phases with `TC` atoms (kind `TC`, level {{ tc_kind.level }}, parents {{ tc_kind.allowed_parents | join('/') }},
plans {{ tc_kind.plans | join('/') }}). Test-plan SUB ids are **bare** labels
(`factory.markers.rules.sub_unqualified_exempt_plans` = {{ factory.markers.rules.sub_unqualified_exempt_plans | join(', ') }}).
A phase flagged `integration: true` in the profile is populated **only** at `scope:
modules|project`, per §2/§4/§5 — at `scope: module` it is skipped entirely, so single-module
output carries the module-scope phases only, exactly as before this scope model existed.
{% for tr, tdef in profile.tracks.items() if tdef.plans.get('test') %}
### Track `{{ tr }}` — one file per selected module: `{{ (st.produces | selectattr('track', 'defined') | selectattr('track', 'equalto', tr) | first).file.replace('{mod}', MOD | lower) }}`

| Phase key | Split rule | SUB labels |
|---|---|---|
{% for p in tdef.plans.test.phases -%}
| `{{ p.key }}`{% if p.get('integration') %} _(integration — `scope: modules|project` only)_{% endif %} | {% if p.get('never_split') %}never split{% elif p.get('split_threshold') %}SUB when {{ p.get('split_threshold').kind }} count {{ p.get('split_threshold').op }} {{ p.get('split_threshold').count }}{% if p.get('split_threshold').grouping %} — grouped {{ p.get('split_threshold').grouping }}{% endif %}{% else %}as the profile describes{% endif %} | {% for l in p.get('sub_labels') or [] %}`{{ l }}`{% if not loop.last %}, {% endif %}{% else %}—{% endfor %} |
{% endfor %}
{%- set int_phases = tdef.plans.test.phases | selectattr('integration') | map(attribute='key') | list -%}
{%- set int_phase = int_phases | first if int_phases else 'the integration phase' -%}
Layout (per selected module):
```
<header>   sources ({{ state_dir }} files + versions) · scope `{{ scope }}` · framework note (§3) · REDUCED? · open ADRs
{% for p in tdef.plans.test.phases if not p.get('integration') or scope != 'module' -%}
<!-- PHASE:{{ p.key }}:START traces=<union of the TCs' REQ/AC{% if p.get('integration') %}/XM/UXD{% endif %}> -->
{%- if p.get('integration') %}
  (populate ONLY when a real linking atom pairs this module with another module in {{ sel_mods | join(', ') }} — §4/§5; omit this PHASE entirely when none exists, never an empty block)
{%- endif %}
{%- if p.get('sub_labels') %}
  {% for l in p.get('sub_labels') %}<!-- SUB:{{ l }}:START traces=… -->  …TC blocks…  <!-- SUB:{{ l }}:END -->{% if not loop.last %}
  {% endif %}{% endfor %}
  (SUBs only when the threshold is met — decide WHILE writing, from the TC count){% else %}
  …TC blocks…{% endif %}
<!-- PHASE:{{ p.key }}:END -->
{% endfor -%}
TC TRACEABILITY INDEX   AC → TC · REQ → TC · {% if tr == 'backend' %}API → TC · RULE/code → TC{% if scope != 'module' %} · XM → TC{% endif %}{% else %}SCR → TC · RULE/code → TC{% if scope != 'module' %} · UXD → TC{% endif %}{% endif %}
COVERAGE                AC covered <n>/<total> (a gap is ✗ and blocks the run) · REQ covered · {% if tr == 'backend' %}API covered{% if scope != 'module' %} · every selected-module XM covered <n>/<total> (an integration gap is ✗ exactly like an AC gap — recorded, never silently dropped){% endif %}{% else %}SCR covered{% if scope != 'module' %} · every selected-module UXD covered <n>/<total> (an integration gap is ✗ exactly like an AC gap — recorded, never silently dropped){% endif %}{% endif %}
```
{% if tr == 'backend' -%}
Backend grouping hint: rule-driven ACs (violations, state transitions) vs endpoint-driven ACs
(happy paths, permission, paging/empty-result per `{{ api.get('paging') | default('the documented envelope', true) }}`); integration TCs (§4) group by target module inside `{{ int_phase }}`.
{%- else -%}
Frontend grouping hint: per-screen flows (search, create/edit, violation shown on screen,
permission-hidden affordance) vs the single module lifecycle flow (create → search → update →
deactivate → gone from active results){% if conv.get('composite_screen') %}; the composite-screen invariant (entry never rendered open by default) is one TC when an AC states it{% endif %}; integration TCs (§5) group by source (owner) module inside `{{ int_phase }}`.
{%- endif %}
{% else %}
The profile declares no `test` plan for any track — nothing to produce; report it and stop.
{% endfor %}
## 8. Test-execution manifest {% if testing.manifest %}(ON — `profile.stack.testing.manifest`){% else %}(OFF — `profile.stack.testing.manifest` is false){% endif %}
{% if testing.manifest %}
Emitted in the same run, after the backend test plan, as
`{{ (st.produces | selectattr('artifact', 'equalto', 'test-execution-manifest') | first).file.replace('{mod}', MOD | lower) }}` —
a **derived view** for the `api-verify` standalone (it introduces no ID), one per module:
```
DEPENDENCY ORDER      topological entity build order (from FK/XM relations in the backend plan and "must belong to" RULEs)
RULE → CODE → TC      RULE-* │ catalog code (runtime format per {{ api.get('error_envelope') | default('the error envelope', true) }}) │ TC-* │ HTTP │ API-*   (informational-only RULEs excluded)
ENTITY CRUD CHECKLIST ENT-* │ create │ read │ search │ update │ {{ api.verbs.get('DELETE') | default('delete', true) }} │ activate (each ✓ / —, from the API-* set)
```
Regenerate whenever the backend plan or test plan changes — a stale manifest is a defect.
{%- else %}
Not produced for this profile. `api-verify` runs in its minimal tier without it.
{%- endif %}

## 9. System test index (`scope: project` only)

Emitted once per run, after every selected module's test plans, as
`system-test-index-{{ profile.identity.id }}.md` — a platform-level **derived view**
(introduces no ID, never a gate, `paths.platform` — same tier as `project-registry.md`):
```
SYSTEM TEST INDEX — {{ profile.identity.display }} — generated {scope: project}
AC → TC       per module: AC covered <n>/<total>, list of uncovered AC (✗)
XM → TC       every XM-* between two modules that both have a committed version: covered ✓/✗ (✗ = gap, never silently dropped)
UXD → TC      every UXD-* whose owner module also has a committed version: covered ✓/✗
COVERAGE %    per module: AC%, and — where the module both declares and is targeted by XM/UXD — integration%
CROSS-MODULE  matrix of module → module, one row per XM/UXD pair, TC id(s) covering it (— if none: gap ✗)
```
Never restates TC content — every row is an ID reference. A module the platform has never
produced a version for is out of scope (not a gap): the index only rolls up modules that
exist.

## 10. Split

The same toolkit splits test plans, with plan key `test`
(`factory.tracks.<track>.packages.test` → {% for tr, t in factory.tracks.items() %}`{{ t.packages.test }}`{% if not loop.last %}, {% endif %}{% endfor %}), **per module**:
```
gov.py split --track <track> --module <MOD> --version <v> --plan test --dry-run   # validate, non-zero exit = fix first
gov.py split --track <track> --module <MOD> --version <v> --plan test
```
Every TC atom is verified by content hash (`factory.markers.rules.verify` = {{ factory.markers.rules.verify }}) after the split.
`system-test-index-{{ profile.identity.id }}.md` is a platform-level file — it is never split, never packaged, never delivered to a consumer repo.

## 11. Self-check before finishing

```
[ ] every AC-* in the SRS (of every selected module) has ≥1 TC-* (coverage ✗ = not done)
[ ] every TC-* carries traces= with its AC-*/XM-*/UXD-* source (+ REQ, API/SCR) and the atom marker pair
[ ] no TC without an AC/XM/UXD source; no reworded rule/message/endpoint; test data never invented
[ ] phases = the profile's test phases, in order; SUB labels bare; thresholds checked while writing
[ ] framework wording matches §6; manifest emitted iff profile.stack.testing.manifest (per module)
[ ] at scope module: no integration phase, no system-test-index — output unchanged from before
[ ] at scope modules|project: every XM-*/UXD-* between two SELECTED modules has ≥1 TC or is
    recorded as a gap (✗) — never silently dropped, never fabricated when absent
[ ] at scope project: system-test-index-{{ profile.identity.id }}.md rolls up every module with
    a committed version; every AC/XM/UXD gap listed is ✗, exactly like a module-scope AC gap
[ ] ADRs written for every derivation choice that was not mechanical
```

## 12. Boundaries

| Owns | References (never redefines) | Never |
|---|---|---|
| `{{ st.owns_ids | join('-*`, `') }}-*`, the test plans{% if testing.manifest %}, the manifest{% endif %}{% if scope == 'project' %}, the system test index{% endif %} | `REQ/AC/RULE` ({{ atoms.AC.owner }}), `API` ({{ atoms.API.owner }}), `SCR/UXD` ({{ atoms.SCR.owner }} — `UXD` is `{{ atoms.UXD.owner }}`'s, cited never redefined), `DBF/XM` ({{ atoms.DBF.owner }} — `XM` is `{{ atoms.XM.owner }}`'s, cited never redefined), catalog codes | test code, framework scaffolding, any edit to a line artifact, any gate or verdict, a cross-module TC for a module outside the current selection |
