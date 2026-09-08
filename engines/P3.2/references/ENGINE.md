{#- ─────────────────────────────────────────────────────────────────────────
    ENGINE.md — {{ stage.id }} · rendered at brief-build time (Jinja2)
    Context: profile · factory · stage · mod · version
    Facts come from factory.yaml + profiles/<id>.yaml only (C1/C2).
   ───────────────────────────────────────────────────────────────────────── -#}
{%- set st = (factory.stages + factory.standalone) | selectattr('id', 'equalto', stage.id) | first -%}
{%- set track = st.track -%}
{%- set phases = profile.tracks[track].plans.exec.phases -%}
{%- set fe = profile.stack.frontend -%}
{%- set libs = fe.get('libraries') or {} -%}
{%- set api = profile.stack.backend.api -%}
{%- set conv = profile.conventions or {} -%}
{%- set sec = conv.get('security_model') -%}
{%- set langs = profile.languages -%}
{%- set MOD = (mod | default('MOD')) | upper -%}
{%- set ver = version | default(1) -%}
{%- set state_dir = factory.paths.module.state_dir -%}
{%- set inputs_dir = factory.paths.module.inputs_dir -%}
{%- set atoms = factory.ids.atoms -%}
{%- set api_docs = factory.inputs['api-docs'].file.replace('{mod}', MOD | lower) -%}
{%- set plan_art = st.produces | selectattr('plan', 'defined') | first -%}
{%- set reg_art = st.produces | selectattr('registry', 'defined') | first -%}
{%- set sub_phases = phases | selectattr('sub_bearing', 'defined') | selectattr('sub_bearing') | list -%}
```
ENGINE        : {{ stage.id }} — {{ st.title }}
PASS / TRACK  : pass {{ st['pass'] }} · track {{ track }} · lane {{ st.lane }} · questions {{ st.questions }}
MODULE        : {{ MOD }} · v{{ ver }} · profile {{ profile.identity.id }} ({{ profile.identity.display }})
READS         : {% for i in st.inputs %}{{ i }}{% if not loop.last %} · {% endif %}{% endfor %}
                ({{ state_dir }}/ for current state; {{ inputs_dir }}/{{ api_docs }} for the real API surface)
PRODUCES      : {% for a in st.produces %}{{ a.file.replace('{mod}', MOD | lower) }}{% if not loop.last %} · {% endif %}{% endfor %}   — ONE run, ONE input set
OWNS IDS      : {% for x in st.owns_ids %}{{ x }}{% if not loop.last %}, {% endif %}{% endfor %}
NEXT          : {{ st.next }}   (the orchestrator owns the completion protocol — shared/GOVERNANCE-CORE.md)
BOUNDARY      : {{ factory.factory.boundary }} — design artifacts and specifications, never a build
```

# {{ st.title }} — engine reference

## 0. Position and authority

One engine, one run, two internal parts that share the same input set:

- **Part A — UX design** (§2): from the SRS (functional ceiling) and the PRD (priority and
  intent) it produces the flow diagram and the ui-ux-spec, minting `SCR-*` and `UXD-*`.
- **Part B — frontend execution plan** (§3): bound to the **real** API surface in
  `{{ inputs_dir }}/{{ api_docs }}` (published by the backend repo after implementation —
  `factory.repos.backend.publishes`), organised by the profile's frontend phases, plus the
  registry.

Authority order: SRS `REQ/AC` are the functional ceiling; the api-docs are the only source
for endpoint shape; the PRD informs sequencing and priority; Part A's spec is strong design
intent for Part B — never a licence to add a field, rule or permission the SRS does not
have. A conflict is a finding (ADR — §7), never a silent resolution. The backend execution
plan's contract summary is **never** read as an API source (it may be opened for `DBF`/catalog
code lookup only).

Questions are `{{ st.questions }}`. Ambiguity → `factory.yaml → ambiguity` (§7). No human
approval sits inside this engine: the human decision is the `{{ st.next }}` gate.

Mockups are a **design artifact** (a per-screen mockup spec, optionally one generated image)
— never an implemented shell, never code, never a gate for anything.

{% if ver | int > 1 -%}
**Delta run (v{{ ver }}).** Baseline = `{{ state_dir }}/`; emit only ADDED / MODIFIED / REMOVED
blocks + `{{ factory.paths.module.change_manifest }}`; `SCR/UXD` sequences continue; v{{ ver | int - 1 }} stays frozen. Rules: shared/VERSIONING.md.
{%- else -%}
**Delta versions** (v2+) emit only ADDED / MODIFIED / REMOVED blocks +
`{{ factory.paths.module.change_manifest }}` against `{{ state_dir }}/`; `SCR/UXD` sequences continue,
never renumbered. Rules: shared/VERSIONING.md.
{%- endif %}

## 1. Inputs and entry check

| Input | Read from | Use |
|---|---|---|
{% for i in st.inputs -%}
| `{{ i }}` | {% if i == 'api-docs' %}`{{ inputs_dir }}/{{ api_docs }}`{% else %}`{{ state_dir }}/{{ factory.naming.current_state_file.replace('{artifact}', i) }}.md`{% endif %} | {% if i == 'srs' %}REQ/AC (EARS + Given/When/Then), ENT, RULE with messages, screen entries, permission matrix, lookup keys{% elif i == 'prd' %}US-* priority, intent, navigation expectations{% elif i == 'api-docs' %}real endpoints, DTOs, paging + error envelope, runtime error codes{% elif i == 'registry-exec-be' %}API-* ranges, catalog codes, XM status, permission names declared by the backend plan{% else %}ID ranges, screen entries, shared entities{% endif %} |
{% endfor %}
Entry: the orchestrator's `fetch-inputs` already refused the pass when
`factory.passes.2.required_inputs` are missing — this engine does not re-gate. It does
run one **reconciliation of api-docs against the SRS** (§3.0) before any F-content.

## 2. Part A — UX design (flow diagram + ui-ux-spec)

### A.0 Role

Translate the approved functional truth into navigation and component **intent**. Never
invent scope, business rules or permissions; never fix an SRS↔PRD contradiction by choosing
an interpretation (§7 decides). Final component names, code and routing are Part B's.

### A.1 Screens — `SCR-*`

Mint one `SCR-*` per screen the SRS declares (`{{ factory.ids.pattern.replace('{prefix}', 'SCR').replace('{MOD}', MOD) }}`,
traces → {{ atoms.SCR.traces_to | join(' + ') }}).
{% if conv.get('composite_screen') -%}
**Composite-screen rule** (`profile.conventions.composite_screen`): Search + Entry (or Master +
Detail, Wizard) are ONE screen with ONE `SCR-*`; the sub-views are UX sub-screens under it.
Each additional independent composite gets its own `SCR-*`.
{%- else -%}
The profile declares no composite-screen convention: each SRS screen entry is one `SCR-*`.
{%- endif %}

### A.2 Flow diagram — `{{ st.produces[0].file.replace('{mod}', MOD | lower) }}`

One flow block per navigation path (identified by its starting `SCR-*` + a short name; flows
carry no atom of their own):
```
FLOW — <name>                                   traces=US-{{ MOD }}-<seq>,REQ-{{ MOD }}-<seq>,SCR-{{ MOD }}-<seq>
Screens   : SCR-{{ MOD }}-<seq> [, SCR-{{ MOD }}-<seq> …]
Sequence  : <entry> → <screen A> → <screen B> → <exit>
Trigger   : <what gets the user here>
Priority  : <from the PRD, if stated>
```
Every flow cites a `US-*` **and** an `SCR-*`. A flow with no SRS-backed screen is inventing
navigation → ADR, not silently included.

### A.3 UI/UX spec — `{{ st.produces[1].file.replace('{mod}', MOD | lower) }}`

One block per `SCR-*`, fields and permissions copied from the SRS (no additions, no omissions):
```
## SCR-{{ MOD }}-<seq> — <name>                 traces=REQ-{{ MOD }}-<seq>,AC-{{ MOD }}-<seq>[,UXD-{{ MOD }}-<seq>]
UI pattern        : <from the SRS screen entry — do not change>
Container pattern : SIDE_DRAWER | FULL_PAGE | TREE_MASTER_DETAIL   (entry screens only — decided here, §A.4)
Sub-views         : {% if conv.get('composite_screen') %}Search · Entry (· Detail · Wizard) under this ONE SCR{% else %}as the SRS declares{% endif %}
Fields shown      : <every SRS field of the owning ENT — label per language ({{ langs.all | join('/') }}), read-only flags>
Permissions       : <SRS matrix rows for this screen — reference only>{% if sec %} — names follow `{{ sec.permission_pattern }}`, gateway `{{ sec.gateway_action }}`{% endif %}
Cross-module data : <field → UXD-{{ MOD }}-<seq> (owner module)> | none
States            : empty · loading · error (generic — catalog codes are Part B's) · offline (if the SRS says so)
Design intent     : <proposal, clearly marked PROPOSAL — never a rule>
Mockup            : <optional — see §A.6>
```

### A.4 Container pattern — decision order (stop at the first match)

1. hierarchical parent–child data (trees) → `TREE_MASTER_DETAIL` (two-pane, tree + permanently visible form);
2. header + repeating line items with a computed total (document-style) → `FULL_PAGE`;
3. otherwise (bounded field count, no repeating rows) → `SIDE_DRAWER`.

A screen that fits none is a signal to re-read the SRS field list, not to invent a fourth
pattern. The choice is authoritative input to Part B's screens/routes role.

### A.5 Cross-module display dependencies — `UXD-*`

`UXD-*` (`{{ factory.ids.pattern.replace('{prefix}', 'UXD').replace('{MOD}', MOD) }}`, traces → {{ atoms.UXD.traces_to | join(' + ') }})
names an application-layer need: a screen owned by **this** module displays data whose
authoritative source is another module's real API. It is minted the moment such a field is
drafted, keyed by the module owning the **screen**, recorded in the spec block and in the
registry. It is not a DB constraint, shares nothing with `XM-*`, and never appears in
backend artifacts.

Lifecycle: minted here → cited (never reassigned) by the F-blocks of Part B → verified at the
`{{ st.next }}` gate by `gov.py analyze`: every `UXD-*` must be referenced by an F-block and
every referenced one must exist (unreferenced or dangling = MAJOR).

### A.6 Reconciliation self-check (SRS B1–B4 ↔ draft) — no human gate

Run before Part B, on the whole draft:
```
RECONCILIATION — {{ MOD }} v{{ ver }}
B1 every US-* used in a flow has an SRS counterpart (REQ/AC/screen)   → none: ADR (no invented screen), flow excluded
B2 no RULE-* contradicts a flow/spec outcome                           → contradiction: both texts verbatim in an ADR (breaking → BLOCKED)
B3 every field/permission on a screen exists in the SRS               → extra: removed; missing: added
B4 every screen entry of the SRS has exactly one SCR-* block          → gap: block added
RESULT  reconciled <n> · reworked <n> (bounded to flagged blocks) · ADRs <list>
```

### A.7 Mockup spec (optional design artifact)

Per screen, a bounded brief: the A.3 block as the sole input, "render exactly these fields,
pattern and states — nothing more, nothing less; anything that seems missing is flagged back,
never added". Output = the spec (+ one generated image if the run produces one), verified
against B1–B4 (every SRS field present, none extra, permission-gated actions represented,
container pattern respected). It is never implemented, never a prerequisite for Part B.

## 3. Part B — frontend execution plan

### 3.0 Binding to the real API surface

Before writing any phase, extract from `{{ inputs_dir }}/{{ api_docs }}` and bind:
```
API SURFACE — {{ MOD }} v{{ ver }}   (source: {{ api_docs }} — the ONLY endpoint source)
ENDPOINTS   API-{{ MOD }}-<seq> │ verb │ path │ request DTO (fields, types, required) │ response DTO │ paging ({{ api.get('paging') | default('as documented') }}) │ envelope ({{ api.get('envelope') | default('as documented') }})
ERRORS      runtime code (per {{ api.get('error_envelope') | default('the documented envelope') }}) │ HTTP │ RULE-* │ message per language ({{ langs.all | join(', ') }})
{% if conv.get('lookups') %}LOOKUPS     endpoint per lookup key — rule: {{ conv.get('lookups') }}
{% endif -%}
PERMISSIONS names the backend registry declares{% if sec %} (`{{ sec.permission_pattern }}`){% endif %}
```
Reconcile once against the SRS: every REQ that needs an endpoint has one (missing/renamed
→ ADR — naming diffs continue, a missing core operation is breaking); every documented
endpoint maps to a REQ (unknown → ADR, never silently used). A value not in the api-docs is
never invented — mark `PENDING ADR-<id>`.

### 3.1 Markers, thresholds, traces

Grammar: `factory.markers` (schema v{{ factory.markers.schema_version }}, syntax `{{ factory.markers.syntax }}`) —
`<!-- KIND:ID:START [traces=…] -->` … `<!-- KIND:ID:END -->`. Kinds allowed in a `{{ track }}` execution plan:

| Kind | Level | Allowed parents | Notes |
|---|---|---|---|
{% for k, spec in factory.markers.kinds.items() if (spec.tracks is not defined or track in spec.tracks) and (spec.plans is not defined or 'exec' in spec.plans) -%}
| `{{ k }}` | {{ spec.level }} | {{ spec.allowed_parents | join(', ') if spec.allowed_parents else '— (top level)' }} | {% if spec.keys_from is defined %}keys from `{{ spec.keys_from }}`{% elif spec.qualified_by_phase is defined %}id = `{PHASE-KEY}-{SCR-ID}` — always phase-qualified{% endif %} |
{% endfor %}
- No atom kind is carried by this track: `API-*` and `XM-*` are backend-owned and only cited.
  The unit of addressing here is the **SUB per screen** in `sub_bearing` phases.
- `{{ factory.markers.attributes | join(', ') }}=` on **every** PHASE and SUB block: the
  `REQ/AC/API/UXD/SCR` IDs the block implements (grammar `{{ factory.ids.pattern }}`,
  {{ factory.ids.seq_width }}-digit seq). A PHASE traces to the union of its SUBs.
- The same screen legitimately appears under several phases; without the `{PHASE-KEY}-`
  prefix the SUB ids would collide — the prefix is mandatory, always.
- First line of a phase = its START marker; last = END. Threshold checked **while** writing.
  Unknown key → the toolkit refuses (`{{ factory.markers.rules.unknown_phase }}`).
- Headings with the word PHASE use a profile key only; index, ALIGN table (unless a phase),
  registry and hand-off are trailing content after the last END. Protocol: shared/MARKER-PROTOCOL.md.

Phase table for `profile.tracks.{{ track }}.plans.exec` (plan order):

| # | Key | Display | Split rule | Per-screen SUB |
|---|---|---|---|---|
{% for p in phases -%}
| {{ loop.index }} | `{{ p.key }}` | {{ p.get('display') | default(p.key, true) }} | {% if p.get('never_split') %}never split{% elif p.get('split_threshold') %}SUB when {{ p.get('split_threshold').kind }} count {{ p.get('split_threshold').op }} {{ p.get('split_threshold').count }}{% else %}as the profile describes{% endif %} | {% if p.get('sub_bearing') %}yes — `SUB:{{ p.key }}-SCR-{{ MOD }}-<seq>`{% else %}no{% endif %} |
{% endfor %}

### 3.2 Content roles

The profile names the phases; the engine supplies content **by role**, matched on the words
in the phase display ("Models & Types", "Data Hooks", "Forms & Validators", "Screens & Routes",
security, alignment). A phase matching no role is filled as the profile describes it. Stack
facts come from `profile.stack.frontend`: framework `{{ fe.framework }}`{% if libs %}; libraries — {% for role, lib in libs.items() %}{{ role }}: `{{ lib }}`{% if not loop.last %}, {% endif %}{% endfor %}{% endif %}{% if fe.get('lazy_chunk_per') %}; lazy chunk per `{{ fe.get('lazy_chunk_per') }}`{% endif %}.

**RF1 — Models & types.** Per `ENT-*` (from the response DTOs in the api-docs) and per `SCR-*`:
```
### <role>-MODEL — ENT-{{ MOD }}-<seq> — <name>          (inside SUB:<phase>-SCR-… of the owning screen)
Source DTO   : <api-docs DTO>            fields: <property : type · read-only · system-only · lookup (code string, never enum) · deferred ⏸>
Read-only    : PK, business code, audit fields — never form input
### <role>-SCREEN — SCR-{{ MOD }}-<seq>
Search model : filters (type, filter kind EXACT|LIKE|DATE_RANGE|SET) · paging + sort params (per {{ api.get('paging') | default('the documented envelope') }})
Form model   : fields (required/optional) · excluded system fields · read-only on edit
Container    : <from A.3>
```
Rules: {% if conv.get('lookups') %}lookup fields are strings holding the code ({{ conv.get('lookups') }}); {% endif %}both names per language ({{ langs.all | join(', ') }}); no internal/tenant identifiers in any model; nothing modelled that the api-docs do not return.

**RF2 — Data hooks.** Declares WHAT each screen needs from the API — not hook code:
```
### <role>-QUERY — API-{{ MOD }}-<seq>            traces=API-…,REQ-…
Verb · path (exact from api-docs) · request shape · response shape · kind (read query | mutation)
Cache key    : [resource, filters] — every filter that changes the response is in the key
Errors       : catalog code → routing (field validation → inline · business rule → user message · unauthenticated → login · forbidden → unauthorized · server → generic)
Loading      : NONE | LOCAL | GLOBAL (GLOBAL only when the SRS says the call is slow → ADR)
Cache policy : defaults | <stale/gc values> (deviation → ADR)
Invalidation : keys refreshed on success (mutations MUST declare this)
{% if conv.get('lookups') %}### <role>-LOOKUP — <lookup key>     endpoint · key · options shape (code + label per language) · ONE hook per key, shared across screens · long-lived cache
{% endif -%}
### <role>-SCREEN-INIT — SCR-{{ MOD }}-<seq>   permission read for the screen{% if sec %} ({{ sec.actions | join('/') }}){% endif %} · lookups used · entity-by-id when editing
### <role>-FACADE — SCR-{{ MOD }}-<seq>         composes the queries above · state it owns (list from query data, selection, filters incl. page/size, derived loading) · imperative operations (create/update/deactivate with usage check first)
```
State rule: page and page size live **inside** the filter object that forms the cache key —
never as independent state. Components use the facade only; the facade uses the declared
queries only (server-state library: {% if libs.get('server-state') %}`{{ libs.get('server-state') }}`{% else %}as the profile declares{% endif %}).

**RF3 — Forms & validators.** One block per `RULE-*` enforced on a form:
```
### <role>-VALIDATION — RULE-{{ MOD }}-<seq>      traces=REQ-…,AC-…
Statement · message per language (from the catalog code, never hard-coded) · scope (CREATE|UPDATE|ALL)
Field · kind (REQUIRED | LENGTH | PATTERN | LOOKUP_VALID | UNIQUE_CHECK | BUSINESS_RULE | DATE_RANGE) · when (change | blur | submit — declared once per form)
Validation shape : <what the schema must express — the implementer writes it with {% if libs.get('validation') %}`{{ libs.get('validation') }}`{% else %}the profile's validation library{% endif %}{% if libs.get('forms') %} + `{{ libs.get('forms') }}`{% endif %}>
UNIQUE_CHECK     : async, on blur, via API-…; current record excluded on edit
LOOKUP_VALID     : value ∈ runtime-loaded options — never a static list
```
Rules: no frontend-only validation the SRS does not state; business code displayed read-only,
never an input; locale from session → browser → `{{ langs.primary }}`; permission-driven field
behaviour (no edit permission → read-only form).

**RF4 — Screens & routes.** One block per `SCR-*`:
```
### <role>-SCREEN — SCR-{{ MOD }}-<seq>            traces=REQ-…,UXD-…,API-…
Routes       : base slug (lower, plural, kebab) · new · :id · :id/edit · [tree — registered BEFORE :id routes]
Chunk        : one lazy chunk per {{ fe.get('lazy_chunk_per') | default('the profile unit') }} (routing: {% if libs.get('routing') %}`{{ libs.get('routing') }}`{% else %}per profile{% endif %})
Guard        : every route element guarded by its permission{% if sec %} (`{{ sec.permission_pattern }}` from the SRS matrix — never invented here){% endif %}
Components   : route-level pages (suffix "Page") · presentational parts (no suffix) — named by container pattern:
               FULL_PAGE → SearchPage + EntryPage (separate routes)
               SIDE_DRAWER → SearchPage + FormDrawer (drawer toggled by a route param, never local-only state)
               TREE_MASTER_DETAIL → TreePage hosting tree + detail (node route param)
Mode         : CREATE | EDIT | VIEW resolved from the route match, never from a parent prop
Facade       : the RF2 facade of this screen · pages never call queries directly
Shared UI    : only the design-system components this screen renders
Cross-module : UXD-* cited for every foreign-data field (missing → ADR, never minted here)
```
{% if conv.get('composite_screen') %}Composite invariant: Search and Entry are always separate components under ONE `SCR-*`, one lazy chunk, linked by route params — never a second chunk for the sub-view.{% endif %}

**RF5 — Security (frontend half).**{% if sec %} Per `SCR-*`: navigation guard (no `{{ sec.gateway_action }}` → unauthorized redirect) and UI behaviour per action ({% for a in sec.actions %}no {{ a }} → its affordance hidden / read-only{% if not loop.last %}; {% endif %}{% endfor %}); forbidden responses shown as the localized catalog message. Permission names are the backend registry's — never redeclared.{% else %} No security model in the profile: write "no permission model — screens open per the SRS" and cite the REQs.{% endif %}

**RF6 — Alignment.** The ALIGN-FE table (§4) as the alignment-role phase content (never
split); trailing content if the profile has no such phase.

### 3.3 Phase-by-phase
{% for p in phases %}
#### PHASE {{ loop.index }} — `{{ p.key }}` ({{ p.get('display') | default(p.key, true) }})
- `<!-- PHASE:{{ p.key }}:START traces=… -->` … `<!-- PHASE:{{ p.key }}:END -->`; content = the roles whose words appear in "{{ p.get('display') | default(p.key, true) }}", else as the profile describes.
- {% if p.get('sub_bearing') %}Per-screen SUB: `<!-- SUB:{{ p.key }}-SCR-{{ MOD }}-<seq>:START traces=… -->` for **every** `SCR-*`{% if p.get('split_threshold') %} when the {{ p.get('split_threshold').kind }} count is {{ p.get('split_threshold').op }} {{ p.get('split_threshold').count }}; below that the screens may share the phase body, but the block heading still names the SCR{% endif %}.{% elif p.get('never_split') %}Never split — level-1 only.{% else %}Split as the profile describes.{% endif %}
{% endfor %}
### 3.4 Mutual consistency rule

Every `SCR-*` in the ui-ux-spec has an F-block in **each** `sub_bearing` phase
({% for p in sub_phases %}`{{ p.key }}`{% if not loop.last %}, {% endif %}{% else %}none declared{% endfor %}) and every F-block names an
`SCR-*` that exists in the spec; every `UXD-*` in the spec is cited by an F-block. `gov.py
analyze` checks this at the gate — a mismatch is MAJOR.

## 4. ALIGN-FE self-check

Against the plan itself, the api-docs and the SRS ceiling (cross-artifact = `gov.py analyze`):
```
ALIGN-FE — {{ MOD }} v{{ ver }}
SCREENS      every SRS screen entry ↔ one SCR │ every SCR has a block in each sub-bearing phase │ composite separation declared │ container pattern set for every entry screen
API          every documented endpoint the module uses has an RF2 block │ no endpoint used that the api-docs lack │ every mutation declares invalidation │ page/size inside the cache key
{% if conv.get('lookups') %}LOOKUPS      every lookup key has one shared hook │ no enum models │ lookup validators use runtime options
{% endif -%}
VALIDATION   every form RULE has an RF3 block citing a catalog code │ no hard-coded message │ no frontend-only rule
ROUTES       every route guarded │ tree routes before :id │ pages use the facade │ naming matches the container pattern
UXD          every UXD cited by an F-block │ no foreign-data field without a UXD
SECURITY     {% if sec %}every SCR has an RF5 block │ every permission name exists in the backend registry{% else %}n/a{% endif %}
LANGUAGES    labels and messages in {{ langs.all | join(' + ') }}
TRACES       every PHASE/SUB carries traces= │ every target exists (REQ/AC/API/UXD/SCR)
DECISIONS    every non-obvious choice is an ADR in decisions/{{ MOD }}/
RESULT       PASSED ✓ / ✗ list (each fixed)
```
Operations coverage table (operation │ API │ SCR action │ route │ status) closes the section —
a row with an empty route is a ✗.

## 5. Registry update — `{{ reg_art.file.replace('{mod}', MOD | lower) }}`

```
REGISTRY — {{ stage.id }} — {{ MOD }} v{{ ver }}
ID RANGES     {% for x in st.owns_ids %}{{ x }}-{{ MOD }}-<first>..<last>{% if not loop.last %} · {% endif %}{% endfor %}
SCREENS       SCR │ name │ container pattern │ owning ENT │ permissions
UXD INDEX     UXD │ screen │ field │ owner module · API used
API COVERAGE  documented endpoints used / unused (with ADR)
ALIGN-FE      PASSED ✓ · findings fixed
ADRs          decisions/{{ MOD }}/ADR-{{ MOD }}-<seq> … (status)
TRACEABILITY  REQ covered by ≥1 SCR/F-block: <n>/<total> · orphan REQ: <list — a gate blocker>
```

## 6. Structural self-check (toolkit)

```
[ ] every profile key has exactly one PHASE START/END pair, in profile order
[ ] every SUB id is {PHASE-KEY}-SCR-…; the same screen under different phases carries different prefixes
[ ] every PHASE/SUB carries traces=
[ ] no heading repeats; trailing content sits after the last PHASE END
[ ] §3.4 mutual consistency holds
```
Then (non-zero exit is blocking):
```
gov.py split --track {{ track }} --module {{ MOD }} --version {{ ver }} --dry-run
```
`gov.py analyze` runs before `{{ st.next }}`; CRITICAL keeps the gate closed.

## 7. Ambiguity rule

`factory.yaml → ambiguity` (shared/GOVERNANCE-CORE.md): non-breaking → ADR
`decisions/{{ MOD }}/{{ factory.naming.adr_file.replace('{MOD}', MOD) }}` and
**{{ factory.ambiguity.non_breaking.then }}**; breaking (contradicts a locked decision or a
REQ, including an SRS↔PRD contradiction) → ADR `{{ factory.ambiguity.breaking.status }}`,
**{{ factory.ambiguity.breaking.then }}**. Use `profile.knowledge.files` and `domain/` steering
for the best-practice choice. No question is raised at this stage.

## 8. Boundaries and hand-off

| Owns (mints) | References (read-only) | Never touches |
|---|---|---|
| {% for x in st.owns_ids %}`{{ x }}-*`{% if not loop.last %}, {% endif %}{% endfor %}; flow diagram; ui-ux-spec; mockup spec; F-blocks; ALIGN-FE; ADRs it raises | `REQ/AC/ENT/RULE` ({{ atoms.REQ.owner }}), `API` ({{ atoms.API.owner }} — shape from the api-docs), catalog codes, permission names, `US` ({{ atoms.US.owner }}) | `DBF/XM` ({{ atoms.DBF.owner }} — backend-only), `QR`, `TC` ({{ atoms.TC.owner }}), any code, any build |

Hand-off (the orchestrator prints it): plan + registry split by the toolkit into
`{{ factory.paths.module.packages_dir }}/{{ factory.tracks[track].packages.exec }}/`, delivered on
`{{ factory.naming.delivery_branch }}` after the `{{ st.next }}` verdict, then tagged
`{{ factory.naming.tag }}`. The implementer reads the plan in profile-phase order, the spec for
intent, the api-docs for shapes, and never invents a route, component, permission or field
not traceable to an F-block (a gap → ADR, not an invention).
