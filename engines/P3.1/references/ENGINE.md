{#- ─────────────────────────────────────────────────────────────────────────
    ENGINE.md — {{ stage.id }} · rendered at brief-build time (Jinja2)
    Context: profile · factory · stage · mod · version
    Facts come from factory.yaml + profiles/<id>.yaml only (C1/C2).
   ───────────────────────────────────────────────────────────────────────── -#}
{%- set st = (factory.stages + factory.standalone) | selectattr('id', 'equalto', stage.id) | first -%}
{%- set track = st.track -%}
{%- set phases = profile.tracks[track].plans.exec.phases -%}
{%- set api = profile.stack.backend.api -%}
{%- set db = profile.stack.db -%}
{%- set conv = profile.conventions or {} -%}
{%- set langs = profile.languages -%}
{%- set sec = conv.get('security_model') -%}
{%- set MOD = (mod | default('MOD')) | upper -%}
{%- set ver = version | default(1) -%}
{%- set state_dir = factory.paths.module.state_dir -%}
{%- set atoms = factory.ids.atoms -%}
{%- set plan_art = st.produces | selectattr('plan', 'defined') | first -%}
{%- set reg_art = st.produces | selectattr('registry', 'defined') | first -%}
```
ENGINE        : {{ stage.id }} — {{ st.title }}
PASS / TRACK  : pass {{ st['pass'] }} · track {{ track }} · lane {{ st.lane }} · questions {{ st.questions }}
MODULE        : {{ MOD }} · v{{ ver }} · profile {{ profile.identity.id }} ({{ profile.identity.display }})
READS         : {% for i in st.inputs %}{{ i }}{% if not loop.last %} · {% endif %}{% endfor %}   (all from {{ state_dir }}/ — generated current state)
PRODUCES      : {% for a in st.produces %}{{ a.file.replace('{mod}', MOD | lower) }}{% if not loop.last %} · {% endif %}{% endfor %}
OWNS IDS      : {% for x in st.owns_ids %}{{ x }}{% if not loop.last %}, {% endif %}{% endfor %}
NEXT          : {{ st.next }}   (the orchestrator owns the completion protocol — shared/GOVERNANCE-CORE.md)
BOUNDARY      : {{ factory.factory.boundary }} — this engine writes specifications, never code
```

# {{ st.title }} — engine reference

## 0. Position and authority

This engine turns the module's **functional truth** (the SRS) and **structural truth** (the
db-script) into one agent-ready backend execution plan. It reads its inputs from
`{{ state_dir }}/` only (the generated current state — never a raw `v{N}/` folder), and it
never invents business meaning, tables, columns, rules or IDs.

- Upstream artifacts govern. A conflict between this plan and the SRS or db-script is a
  **finding**, never a silent resolution.
- Questions are `{{ st.questions }}` at this stage. Ambiguity is resolved by the rule in
  `factory.yaml → ambiguity` (see §12): non-breaking → ADR (`{{ factory.ambiguity.non_breaking.action | upper }}`) and
  `{{ factory.ambiguity.non_breaking.then }}`; breaking → ADR with status
  `{{ factory.ambiguity.breaking.status }}` and `{{ factory.ambiguity.breaking.then }}`.
- Every block in the plan carries `traces=` to the upstream IDs it implements (§6.0). The
  traceability matrix built by `gov.py analyze` must be CLEAN before the pass gate opens.
- The plan is the **sole backend input** of the implementation agent. After implementation
  the consumer repo publishes `{{ factory.repos.backend.publishes['api-docs'] }}`; the
  frontend stage reads that file — never this plan's contract draft.

{% if ver | int > 1 -%}
**Delta run (v{{ ver }}).** Read `{{ state_dir }}/` as the baseline; emit only ADDED / MODIFIED /
REMOVED blocks plus `{{ factory.paths.module.change_manifest }}`; continue every ID sequence,
never renumber; keep v{{ ver | int - 1 }} frozen. Rules: shared/VERSIONING.md.
{%- else -%}
**Delta versions** (v2+) emit only ADDED / MODIFIED / REMOVED blocks plus
`{{ factory.paths.module.change_manifest }}` against the baseline in `{{ state_dir }}/`; IDs
continue their sequence and are never renumbered. Rules: shared/VERSIONING.md.
{%- endif %}

## 1. Inputs

| Input | Read from | Use |
|---|---|---|
{% for i in st.inputs -%}
| `{{ i }}` | `{{ state_dir }}/{{ factory.naming.current_state_file.replace('{artifact}', i) }}.md` | {% if 'registry' in i %}ID ranges already assigned, shared entities, existing lookups, module prefix{% elif i == 'srs' %}authoritative functional truth — REQ/AC/ENT/RULE, screens, permissions, lookup keys{% else %}authoritative structural truth — tables, columns (DBF), constraints, XM register{% endif %} |
{% endfor -%}
| `domain/` steering + `profile.knowledge.files` | {% for f in (profile.knowledge.files if profile.knowledge is defined and profile.knowledge else []) %}`{{ f }}`{% if not loop.last %}, {% endif %}{% else %}—{% endfor %} | primary sources cited when a best-practice choice must be made (§12) |

Business policies are not read directly: client policies are embedded in `RULE-*` inside
the SRS. A RULE sourced from a client policy is never resolved unilaterally — a conflict is a
breaking ambiguity (§12).

If the db-script is absent the run is **GOVERNANCE REDUCED**: declare it in the plan header,
produce a functional-only plan, mark every DB binding `PENDING`, and record an ADR. Never
downgrade silently.

## 2. Mandatory extraction and binding (§2A)

### 2A.0 The fundamental rule

Before writing any phase content, extract and **bind** every concrete value from the inputs.
A plan containing a placeholder (`[TABLE_NAME]`, `[LOOKUP_KEY]`, "uses a sequence",
"see SRS") is incomplete and fails the alignment self-check (§9).

```
NO-INVENTION RULE
  Every table, column, constraint, index and PK-generation object used anywhere in the plan
  MUST exist in the db-script and be cited by its DBF-* (or the exact object name the
  db-script declares). Base fields (audit, flag, PK) come from the db-script — not from
  memory, not from templates. Naming conventions are read from the profile:
    flag suffix   : {{ db.naming.flag_suffix | default('(profile.stack.db.naming.flag_suffix — not declared)') }}
    audit fields  : {{ db.naming.audit_fields | default([]) | join(', ') or '(profile.stack.db.naming.audit_fields — not declared)' }}
    PK pattern    : {{ db.naming.pk_pattern | default('(profile.stack.db.naming.pk_pattern — not declared)') }}
    target dialect: {{ db.dialects[0] }}{% if db.dialects | length > 1 %} (also kept: {{ db.dialects[1:] | join(', ') }}){% endif %}
```

### 2A.1 Pre-generation extraction table

Emit this table first in the run (it is not part of the plan file; it is the working set
every phase binds from):

```
PRE-GENERATION EXTRACTION — {{ MOD }} v{{ ver }}
── FROM srs ──────────────────────────────────────────────────────────────
ENTITIES      ENT-{{ MOD }}-<seq> │ exact name │ kind ∈ {{ profile.vocabulary.entity_kinds | join(' | ') }}
REQUIREMENTS  REQ-{{ MOD }}-<seq> │ EARS text  │ its AC-{{ MOD }}-<seq> list (Given/When/Then)
RULES         RULE-{{ MOD }}-<seq> │ scope ENT │ trigger │ statement │ message per language ({{ langs.all | join(', ') }}) │ source
SCREENS       every screen entry the SRS declares │ type │ owning ENT{% if conv.get('composite_screen') %} │ composite (Search + Entry = ONE screen){% endif %}
PERMISSIONS   the SRS permission matrix (roles × screens × actions){% if sec %} — actions {{ sec.actions | join('/') }}, gateway {{ sec.gateway_action }}{% endif %}
{% if conv.get('lookups') -%}
LOOKUPS       every lookup key the SRS names, exactly as written — rule: {{ conv.get('lookups') }}
{% endif -%}
{% if conv.get('numbering') -%}
BUSINESS CODE format per master entity — rule: {{ conv.get('numbering') }}
{% endif -%}
── FROM db-script ────────────────────────────────────────────────────────
TABLES        ENT → exact table name
PK GENERATION exact object the db-script declares per table (identity clause / sequence / trigger — as written for {{ db.dialects[0] }})
COLUMNS       exact column name │ DBF-{{ MOD }}-<seq> │ declared type │ null │ default
CONSTRAINTS   exact FK / UNIQUE / CHECK constraint names ; INDEXES exact names
XM            XM-{{ MOD }}-<seq> │ kind (HARD-FK | SOFT-READ …) │ local column │ target module.table │ status
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES consumed (owner module, reached via which XM) — never redeclared
EXISTING LOOKUP KEYS (reuse — never create a duplicate)
ID RANGES already used for {% for x in st.owns_ids %}{{ x }}{% if not loop.last %}, {% endif %}{% endfor %} (continue the sequence)
──────────────────────────────────────────────────────────────────────────
Any row that cannot be filled → §2A.3.
```

### 2A.2 Binding rules

| Binding | Rule | Forbidden → Required |
|---|---|---|
| PK generation | every PK reference names the exact object from the db-script | "auto-generated" → the exact identity/sequence clause as declared |
| Column names | every field reference cites the exact column + `DBF-*`; the implementer maps property → column through the DB Alignment Manifest (§4) | a camelCase invention → `DBF-*` lookup |
| Rule text | every RULE cited in a phase carries its full statement, trigger and message in every language ({{ langs.all | join(', ') }}) — the plan is self-contained | "applies RULE-… see SRS" → full text inline |
{% if conv.get('lookups') -%}
| Lookup keys | the exact key string from the SRS, confirmed against the db-script column that stores it; endpoint per the base path `{{ api.base_path }}` | a parameter placeholder → the literal key |
{% endif -%}
{% if conv.get('numbering') -%}
| Business code | format stated explicitly (exact pattern from the SRS, column, uniqueness constraint name) | "auto-generated, read-only" → format + column + constraint + generation source |
{% endif -%}
| Endpoints | every path is an instance of `{{ api.base_path }}`; verbs mean {% for v, m in api.verbs.items() %}`{{ v }}`={{ m }}{% if not loop.last %}, {% endif %}{% endfor %} | an ad-hoc path → the base-path pattern |

### 2A.3 Extraction failure

A value that cannot be confirmed from the inputs is never invented:

| Case | Action |
|---|---|
| SRS entity has no table in the db-script | mark the entity `PENDING DB` in the plan (GOVERNANCE REDUCED for that entity) + ADR |
| Lookup key / message text / business-code format missing | mark the field `PENDING` with the ADR id; the Error Catalog row carries the ADR id instead of text |
| PK generation object missing for a table | flag in the data phase; QR entry notes `generation: not confirmed`; ADR |
| Two upstream sources contradict | breaking ambiguity → ADR `{{ factory.ambiguity.breaking.status }}`, run stops (§12) |

## 3. Plan Index

The plan opens with an index — one table per element family, every row bound from §2A.1:

```
EXECUTION PLAN INDEX — {{ MOD }} v{{ ver }} — {{ plan_art.file.replace('{mod}', MOD | lower) }}
Profile: {{ profile.identity.id }} · dialect: {{ db.dialects[0] }} · framework: profile.stack.backend.framework
Open ADRs: <n> — decisions/{{ MOD }}/

ENTITY REGISTRY   ENT-*  │ name │ table │ business code (if any) │ operations
FIELD REGISTRY    DBF-*  │ property │ read-only? │ ENT-*
API REGISTRY      API-*  │ operation │ verb │ path │ traces (REQ-*, DBF-*)
RULE REGISTRY     RULE-* │ name │ scope │ ENT-* │ message in every language ✓/✗
SCREEN REGISTRY   screen │ type │ ENT-* │ permission names
{% if conv.get('lookups') %}LOOKUP REGISTRY   key    │ used in field │ ENT-*
{% endif -%}
QRC SUMMARY       QR-*   │ operation │ phase │ ENT-*         (agent reference only — §5)
DB ALIGNMENT      see manifest (§4) — ALIGNED ✓ / issues: <n>
XM STATUS         <n> deferred — see the cross-module phases
SECURITY          <n> screens × <n> roles
```

## 4. DB Alignment Manifest

The manifest is the canonical binding between plan fields and db-script fields. It contains
**only** these columns — column names, DB types and SRS references are *sourced by lookup*
from the db-script, never reproduced here (duplicating them is a contract violation —
shared/ARTIFACT-CONTRACTS.md):

```
DB ALIGNMENT MANIFEST — {{ MOD }} v{{ ver }}
DBF-*            │ ENT-*          │ plan property │ plan type │ XM-* (if FK crosses modules) │ status
DBF-{{ MOD }}-001 │ ENT-{{ MOD }}-001 │ <property>    │ <type>    │ —                            │ ✓
DBF-{{ MOD }}-007 │ ENT-{{ MOD }}-001 │ <property>    │ <type>    │ XM-{{ MOD }}-001 ⏸           │ ⏸
Legend  ✓ aligned · ✗ type mismatch (finding) · ⏸ deferred XM
Derived / computed properties (no DBF) are listed with DBF = "— (derived)" and an ADR id.
```

## 5. Query Reference Catalog (QR-*)

The QRC expresses the **retrieval and persistence intent** of every repository operation as
pseudo-SQL. It is a logical specification, never executable code: the implementer rewrites
every entry with the real entity classes, mapped property names and the project's query
strategy. Copy-pasting a QR entry into production code is a violation.

- Format: `{{ factory.ids.pattern.replace('{prefix}', 'QR').replace('{MOD}', MOD) }}` ({{ factory.ids.seq_width }}-digit sequence, continuous across the module).
- Assigned while writing the data and service phases; every API with a DB operation cites its QR.
- Ordering / paging use the profile's envelope: {% if api.paging %}`{{ api.paging }}`{% else %}(profile.stack.backend.api.paging — not declared){% endif %}; responses are wrapped in {% if api.envelope %}`{{ api.envelope }}`{% else %}(profile.stack.backend.api.envelope — not declared){% endif %}.

```
QR-{{ MOD }}-<seq> — <operation name>
Phase        : <p.key of the phase that defines it>
API          : API-{{ MOD }}-<seq> | repository-only
Entity       : ENT-{{ MOD }}-<seq>
Operation    : FIND_ONE | FIND_ALL | FIND_BY_CRITERIA | SAVE | UPDATE | DELETE | COUNT | EXISTS | NATIVE | AGGREGATE
Intent       : <what business question this answers / what it must return or change>
Logical spec : SELECT … FROM <exact table> [JOIN <table> ON …] WHERE <conditions from RULE-*> [ORDER BY …] [page/size]
Join         : NONE | required — ADR-<id> (why)
Transaction  : READ_ONLY (reads) | READ_WRITE (writes) | REQUIRES_NEW — ADR-<id> if non-default
Pagination   : YES ({{ api.paging | default('per profile') }}) | NO
Filters      : <field: EXACT | LIKE | DATE_RANGE | SET>
Result shape : full entity | projection <fields> | count
Null handling: <per optional field>
```

Standard operation defaults (apply unless a QR entry overrides them):

| Operation | Default |
|---|---|
| FIND_ONE by PK | read-only; not found → error per `{{ api.error_envelope | default('profile.stack.backend.api.error_envelope') }}` with the catalog row for "not found" |
| FIND_BY_CRITERIA | read-only; filters + allowed sort fields declared per search; empty result → success with empty content, **never** "not found" |
| SAVE | read-write; PK and audit fields system-set; {% if conv.get('numbering') %}business code from the numbering rule ({{ conv.get('numbering') }}){% else %}business code as the SRS states{% endif %} |
| UPDATE | read-write; immutable fields (PK, business code, audit) excluded from the request |
| `{{ api.verbs.DELETE | default('DELETE') }}` | usage check first (can-delete / can-deactivate); blocked → catalog error; allowed → {% if (db.naming or {}).get('flag_suffix') %}flip the active flag (suffix `{{ db.naming.flag_suffix }}`){% else %}apply the deletion semantics the SRS states{% endif %}; hard delete only where the SRS mandates it |
| EXISTS | read-only uniqueness check; excludes the current PK on update |

Join governance: single-table responses never join; {% if conv.get('lookups') %}display names of lookup values are **never** joined — the backend returns the stored code and the frontend resolves the label ({{ conv.get('lookups') }}); {% endif %}parent data or cross-entity filters require a join **and** an ADR; cross-entity aggregation may need a native query — say why.

## 6. Phase content

### 6.0 Markers, thresholds, traces — read before writing any phase

Marker grammar (`factory.markers`, schema v{{ factory.markers.schema_version }}, syntax `{{ factory.markers.syntax }}`):
`<!-- KIND:ID:START [traces=…] -->` … `<!-- KIND:ID:END -->`. Kinds that may appear in a
`{{ track }}` execution plan:

| Kind | Level | Allowed parents | Notes |
|---|---|---|---|
{% for k, spec in factory.markers.kinds.items() if (spec.tracks is not defined or track in spec.tracks) and (spec.plans is not defined or 'exec' in spec.plans) -%}
| `{{ k }}` | {{ spec.level }} | {{ spec.allowed_parents | join(', ') if spec.allowed_parents else '— (top level)' }} | {% if spec.keys_from is defined %}keys from `{{ spec.keys_from }}`{% elif spec.qualified_by_phase is defined %}id = `{PHASE-KEY}-{LABEL}` — always phase-qualified{% elif spec.atom is defined %}one atom `{{ spec.atom }}-*` = one dedicated block{% endif %} |
{% endfor %}
Rules:
- The first line you write for a phase **is** its `PHASE` START marker; the last line is its
  END marker. Content and markers are one action — never "write, then wrap".
- `{{ factory.markers.attributes | join(', ') }}=`: **every** PHASE, SUB and atom block carries
  `traces=` listing the upstream IDs it implements (comma-separated, grammar
  `{{ factory.ids.pattern }}`, {{ factory.ids.seq_width }}-digit seq). Obligations from `factory.ids`:
  {% for k in st.owns_ids if k in atoms and atoms[k].traces_to is defined %}`{{ k }}` → {{ atoms[k].traces_to | join(' + ') }}; {% endfor %}`XM` → {{ atoms.XM.traces_to | join(' + ') }} (XM is minted upstream and only placed here). A PHASE block traces to the union of its children.
- Split unit is `{{ factory.markers.rules.split_unit | join(' or ') }}` — never an atom. Check the
  threshold **while** writing: if the count is already at threshold from §2A.1, open the first
  SUB before its first block. Never write flat and split later.
- Unknown phase key → the toolkit **refuses** (`{{ factory.markers.rules.unknown_phase }}`). The key
  is `p.key`, never the display name{% if factory.markers.autofix.phase_key_normalise %} (the
  autofix normalises `+ _ space --` to `-` only when unambiguous — do not rely on it){% endif %}.
- Any heading containing the word PHASE uses exactly one profile key. Index, manifest, catalog
  and self-check sections are not phases: distinct headings, no marker, placed before the
  first PHASE or after the last END.
- Full protocol: shared/MARKER-PROTOCOL.md.

Phase table for `profile.tracks.{{ track }}.plans.exec` (the plan is organised in exactly this order):

| # | Key | Display | Split rule | Atoms carried |
|---|---|---|---|---|
{% for p in phases -%}
| {{ loop.index }} | `{{ p.key }}` | {{ p.display | default(p.key) }} | {% if p.get('never_split') %}never split{% elif p.get('split_threshold') %}SUB when {{ p.get('split_threshold').kind }} count {{ p.get('split_threshold').op }} {{ p.get('split_threshold').count }}{% if p.get('split_threshold').grouping %} — grouped {{ p.get('split_threshold').grouping }}{% endif %}{% elif p.get('sub_labels') %}SUB by engine self-check{% else %}as the profile describes{% endif %}{% if p.get('sub_labels') %}; labels {% for l in p.get('sub_labels') %}`{{ p.key }}-{{ l }}`{% if not loop.last %}, {% endif %}{% endfor %}{% endif %} | {% if p.get('split_threshold') and p.get('split_threshold').kind in factory.markers.kinds and factory.markers.kinds[p.get('split_threshold').kind].atom %}`{{ p.get('split_threshold').kind }}-*` blocks{% else %}none{% endif %} |
{% endfor %}

### 6.1 Content roles

The profile names the phases; this engine supplies the content **by role**. Match each
phase to the roles its display name declares (a display such as "SVC+API" declares the
service and API roles; "INT-C" declares cross-module consume). A phase whose display matches
no role is filled as the profile describes it. Atom placement is data-driven: `API-*` blocks
go in the phase whose `split_threshold.kind` is `API`, `XM-*` blocks in the phases whose
kind is `XM`.

**R1 — Core / configuration (architecture policies).** Declared once, applies to the module:
- Layers and responsibilities: {% if profile.stack.backend.layers %}{{ profile.stack.backend.layers | join(' → ') }}{% else %}as `profile.stack.backend.layers` declares{% endif %} — each layer's "does / never does" stated; boundary violations are review findings.
- Domain-behaviour placement (in entity methods | separate domain classes) — one choice.
- Error signalling: `{{ api.error_envelope | default('profile.stack.backend.api.error_envelope') }}`; every catalog row is registered in every place the framework needs (declare the list once here).
- Transaction scope defaults; search contract (request shape, allowed sort fields, paging `{{ api.paging | default('per profile') }}`).
- Audit fields {% if (db.naming or {}).get('audit_fields') %}(`{{ db.naming.audit_fields | join('`, `') }}`) {% endif %}are framework-filled — never in create/update requests, never set by mappers or services.
- Type mapping {{ db.dialects[0] }} → language types, stated once as a table (from `profile.stack.db.syntax_map` rows) — a deviation needs an ADR.
{% if conv.get('lookups') %}- Lookup values: {{ conv.get('lookups') }}.
{% endif -%}
{% if conv.get('numbering') %}- Numbering: {{ conv.get('numbering') }}.
{% endif -%}
{% if conv.get('workflow_engine') %}- Workflow engine: **{{ conv.get('workflow_engine') }}**.
{% endif -%}
- Languages: every named entity carries a name per language ({{ langs.all | join(', ') }}){% if langs.require_all %}; a single-language artifact is incomplete{% endif %}.
- Cross-module contract placement: inversion-of-control interfaces consumed by other modules live in the service layer; a domain class may depend on another module's service interface (module boundary, not a layer violation).
If nothing module-specific applies, write "Standard configuration — no module-specific abstractions".

**R2 — Data + domain.** One entity block per `ENT-*`, every value bound (§2A):
```
### ENT-{{ MOD }}-<seq> — <exact name>      kind: <{{ profile.vocabulary.entity_kinds | join('|') }}>
BINDINGS   table <exact> · PK <column, DBF> · PK generation <exact object> · db-script version
{% if conv.get('numbering') %}BUSINESS CODE property · column (DBF) · format <exact> · uniqueness constraint <exact name> · generation source
{% endif -%}
DEFAULT FIELDS per kind (profile.conventions.entity_defaults): {% for kind, fields in (conv.get('entity_defaults') or {}).items() %}{{ kind }} → {{ fields | join(', ') }}{% if not loop.last %}; {% endif %}{% else %}none declared{% endfor %}
FIELDS     DBF-* │ property │ column (exact) │ type ({{ db.dialects[0] }}) │ null │ read-only │ constraint │ label per language ({{ langs.all | join('/') }})
DTO MEMBERSHIP  create-request excludes / update-request excludes / response includes (PK, business code, audit, flag stated explicitly)
{% if conv.get('lookups') %}LOOKUP FIELDS  property │ column (DBF) │ exact lookup key │ endpoint (base path {{ api.base_path }}) — stores the code, never a numeric FK
{% endif -%}
DOMAIN RULES   RULE-* full text: trigger · statement · message per language · scope (CREATE|UPDATE|DELETE|ALL) · DB enforcement (constraint name | app-level) · owner layer
STATE MACHINE  (if status-bearing) status column (DBF) · values · initial · transitions (trigger, actor) · terminal · invalid-transition RULE
CROSS-MODULE   XM-* rows touching this entity (kind, local column, target, status)
REPOSITORY OPS → QR-* list (FIND_ONE, FIND_BY_CRITERIA, SAVE, UPDATE, EXISTS, …)
```
{% for p in phases if p.get('sub_labels') and not p.get('split_threshold') -%}
Grouping for `{{ p.key }}`: when the entity count justifies a split (engine self-check — not
marker-countable), group under `{% for l in p.get('sub_labels') %}SUB:{{ p.key }}-{{ l }}{% if not loop.last %} / {% endif %}{% endfor %}`.
{% endfor %}
**R3 — Service + API.** One `API-*` block per endpoint, each its own atom marker:
```
<!-- API:API-{{ MOD }}-<seq>:START traces=REQ-{{ MOD }}-<seq>,DBF-{{ MOD }}-<seq> -->
### API-{{ MOD }}-<seq> — <operation>
Endpoint     : <instance of {{ api.base_path }}>   verb: <{{ api.verbs.keys() | join('|') }}>
Layers       : <entry layer → method> ; <service layer → method>        (names per R1)
Request      : path params · query params (filter names = properties from R2) · body DTO fields (type, required, constraint) · excluded system fields
Response     : status · DTO fields · paginated? ({{ api.paging | default('per profile') }}) · envelope {{ api.envelope | default('per profile') }}
Validations  : RULE-* full text (statement, trigger, message per language) — every RULE listed here has a catalog row (§7)
Errors       : catalog rows this endpoint can raise (code, HTTP, RULE-*)
Orchestration: load → validate (RULE-*) → integrate (XM-*) → persist (QR-*, table, generation object)   — WHAT in sequence, layer placement per R1
Repository   : QR-* · operation · join (NONE | ADR) · transaction
Security     : screen · permission name{% if sec %} (`{{ sec.permission_pattern }}`){% endif %} — enforced before processing
Localization : every message in {{ langs.all | join(' + ') }}; every name field per language
<!-- API:API-{{ MOD }}-<seq>:END -->
```
Completeness rules: every RULE in Validations ↔ a catalog row (RULE-ERR-CARRY); infrastructure
errors (not found, forbidden, server) are catalog rows with RULE = `PLATFORM-STD` and an ADR;
repository deviations (eager fetch, compound update, native query) need an ADR. Business code
(if any) is excluded from create/update bodies and always present in responses. No hard-coded
role checks in services — permission names only.

**R4 — Contract documentation (internal).** API contract summary (API │ path │ verb │ request
DTO │ response DTO │ stability), DTO typing constraints ({% if conv.get('lookups') %}lookup fields are
strings holding the code, never enums; {% endif %}business code never in create/update), and the
pagination + filter standard (request shape, sort validation, empty result = success). This
section is a **backend self-check only** — the frontend stage binds to the real
`{{ factory.inputs['api-docs'].file.replace('{mod}', MOD | lower) }}` published after implementation, never to this summary.

**R5 — Cross-module consume (contracts).** The plan never mints `XM-*`; it places every XM
from the db-script register:
```
<!-- XM:XM-{{ MOD }}-<seq>:START traces=REQ-{{ MOD }}-<seq> -->
### XM-{{ MOD }}-<seq> — <dependency>
Target        : module · entity (ENT of the owner) · classification (HARD-FK | SOFT-READ | EVENT | READ-ONLY)
Interface     : DB foreign key | REST call (<instance of {{ api.base_path }} on the target>) | message
Contract      : data required · fallback if absent · retry / timeout / idempotency
Blocks        : DBF-* / API-* blocked while DEFERRED · unblock condition · deferred strategy
<!-- XM:XM-{{ MOD }}-<seq>:END -->
```
Summary table first (XM │ classification │ target │ interface │ status). Inbound
dependencies from future consumers use `XM-INBOUND-STUB-<n>` notation (consumer, entity
exposed, "assigned by the consumer"), never `TODO`. Lifecycle and RXE handling:
shared/XM-PROTOCOL.md — the factory ends at DELIVERED; CLOSED belongs to the consumer repo.

**R6 — Cross-module resolve (runtime activation).** One status row per XM (READY │ DEFERRED
│ MOCKED │ SIMULATED │ BLOCKED │ EXTERNAL_WAIT) with the workaround / mock strategy for every
non-READY row; consumes R5 contracts, never redefines them. Same XM atom-marker form when the
phase carries XM atoms.

**R7 — Security (backend half).**{% if sec %} Enforced by the profile's security model:
- one block per screen the SRS declares: every API serving it verifies its permission before processing;
- seed data: one row per {% if conv.get('composite_screen') %}composite {% endif %}screen in `{{ sec.page_registry }}` (page code, name, parent) and one permission row per action `{{ sec.actions | join('/') }}` following `{{ sec.permission_pattern }}`, `{{ sec.gateway_action }}` being the gateway (without it no other permission applies); column names come from the db-script, not from here;
- forbidden responses map through `{{ api.error_envelope | default('the error envelope') }}` with a catalog row.
The frontend stage references these permission names — it never redeclares them.{% else %} No security model is declared in `profile.conventions.security_model`; write "no permission model — endpoints are open per the SRS" and cite the REQs that say so.{% endif %}

**R8 — Alignment (self-check).** The ALIGN table of §9, written as the phase content of the
alignment-role phase (never split). If the profile declares no alignment-role phase, the
table is trailing content after the last PHASE END.

### 6.2 Phase-by-phase instructions
{% for p in phases %}
#### PHASE {{ loop.index }} — `{{ p.key }}` ({{ p.display | default(p.key) }})
- Open with `<!-- PHASE:{{ p.key }}:START traces=… -->`, close with `<!-- PHASE:{{ p.key }}:END -->`.
- Content: the roles in §6.1 whose words appear in "{{ p.display | default(p.key) }}"; otherwise as the profile describes this phase.
- Split: {% if p.get('never_split') %}never — level-1 only, no SUB.{% elif p.get('split_threshold') %}open `<!-- SUB:{{ p.key }}-<LABEL>:START traces=… -->` groups when the `{{ p.get('split_threshold').kind }}` count is {{ p.get('split_threshold').op }} {{ p.get('split_threshold').count }}{% if p.get('split_threshold').grouping %}, grouped {{ p.get('split_threshold').grouping }}{% endif %}{% if p.get('sub_labels') %}; labels {% for l in p.get('sub_labels') %}`{{ p.key }}-{{ l }}`{% if not loop.last %}, {% endif %}{% endfor %}{% endif %}. Every atom then sits inside a SUB — no orphan atoms beside SUBs.{% elif p.get('sub_labels') %}by engine self-check, labels {% for l in p.get('sub_labels') %}`{{ p.key }}-{{ l }}`{% if not loop.last %}, {% endif %}{% endfor %}.{% else %}as the profile describes.{% endif %}
- Atoms: {% if p.get('split_threshold') and p.get('split_threshold').kind in factory.markers.kinds and factory.markers.kinds[p.get('split_threshold').kind].atom %}one `{{ p.get('split_threshold').kind }}-*` marker pair per atom, `traces=` on each.{% else %}none — entity/rule blocks carry no marker of their own.{% endif %}
{% endfor %}
## 7. Error Catalog

Canonical, produced with the service/API role, kept in **one** location (a pointer elsewhere
is fine; a second table is a duplicate). Envelope: `{{ api.error_envelope | default('profile.stack.backend.api.error_envelope') }}`.

```
ERROR CATALOG — {{ MOD }} v{{ ver }}
code (runtime value per envelope) │ RULE-* (or PLATFORM-STD + ADR) │ API-* │ HTTP │ trigger │ {% for l in langs.all %}message-{{ l | upper }}{% if not loop.last %} │ {% endif %}{% endfor %}
```
- Every RULE that produces a user-facing message has a row; message text is copied
  character-perfect from the SRS in every language ({{ langs.all | join(', ') }}); a missing
  language → `PENDING ADR-<id>`, never invented.
- Downstream consumers (frontend plan, test-gen, api-verify) cite the **code**; they never
  reproduce message text.
- The runtime code format (as the framework serialises it) is stated once in R1 so that
  api-verify can assert on it.

## 8. Security

Covered by R7 (§6.1){% if sec %} — permission names follow
`{{ sec.permission_pattern }}`, minted only from the SRS permission matrix;
a permission name that appears in the plan but not in the matrix is a finding{% endif %}.
Review check: `profile.review.extra_checks` rows whose stage is `{{ stage.id }}`:
{% for c in (profile.review.extra_checks if profile.review is defined and profile.review else []) if c.stage == stage.id %}- `{{ c.id }}` ({{ c.severity }}): {{ c.check }}
{% else %}- none declared for this stage.
{% endfor %}
## 9. Alignment self-check (ALIGN)

Validates the plan **against itself and its bindings** — the cross-artifact check is
`gov.py analyze` at the gate. Runs automatically after the last content phase; a ✗ is fixed
in the plan before the run ends (the fix is an ADR if it was a choice).

```
ALIGN — {{ MOD }} v{{ ver }}
TRACEABILITY      every API-*/QR-*/RULE-*/DBF-* used in a phase appears in the Plan Index │ every block carries traces= │ every traces target exists upstream
BINDING (§2A)     no placeholder table/column/key/generation object │ no "see SRS" │ every column cites a DBF │ every message present in {{ langs.all | join(' + ') }} │ business code format explicit
MANIFEST (§4)     only the manifest's columns │ every DBF of every bound table listed │ ⏸ rows have an XM
QRC (§5)          every API with a DB operation has a QR │ every QR carries the agent-reference warning │ no join for lookup labels │ exact generation object named
API (R3)          every RULE in Validations has a catalog row │ platform errors have RULE = PLATFORM-STD + ADR │ create/update exclude system fields │ business code in responses
CROSS-MODULE      every XM from the db-script placed exactly once │ every DEFERRED has strategy + unblock │ inbound stubs use XM-INBOUND-STUB
SECURITY (R7)     {% if sec %}every API serving a screen declares its permission │ every screen has a seed row in {{ sec.page_registry }} │ no permission outside the matrix{% else %}n/a — no security model in profile{% endif %}
CORE (R1)         layers declared │ domain placement declared │ error signalling declared │ type mapping declared
DECISIONS         every non-obvious inference is an ADR in decisions/{{ MOD }}/ │ no BLOCKED ADR left unsurfaced
RESULT            PASSED ✓ / list of ✗ (each with the fix applied)
```
Coverage tables (ENT/DBF → phases → QR → XM; RULE → API → catalog code; XM → status → blocks
→ workaround) close the section.

## 10. Registry update — `{{ reg_art.file.replace('{mod}', MOD | lower) }}`

Written in the same run, after ALIGN ✓ (categories: shared/REGISTRY-SCHEMA.md):

```
REGISTRY — {{ stage.id }} — {{ MOD }} v{{ ver }}
ID RANGES        {% for x in st.owns_ids %}{{ x }}-{{ MOD }}-<first>..<last>{% if not loop.last %} · {% endif %}{% endfor %}
ENTITIES / TABLES bound   · lookups reused / new{% if conv.get('lookups') %} (keys){% endif %}
XM STATUS        open / deferred list
CATALOG          code count · rules without message → ADR ids
ALIGN            PASSED ✓ · findings fixed
ADRs             decisions/{{ MOD }}/ADR-{{ MOD }}-<seq> … (status)
TRACEABILITY     REQ covered by ≥1 API/DBF: <n>/<total> · orphan REQ: <list — a gate blocker>
```

## 11. Structural self-check (toolkit)

Before the run ends:
```
[ ] every profile key in §6.0 has exactly one PHASE START/END pair, in profile order
[ ] every API-*/XM-* mentioned anywhere has exactly ONE dedicated marker pair
[ ] every SUB id is {PHASE-KEY}-{LABEL}; identical labels under different phases stay distinct
[ ] every PHASE/SUB/atom carries traces=
[ ] no heading label repeats; trailing content (§9–§10 when not a phase) sits after the last PHASE END
[ ] thresholds were checked while writing, not retrofitted
```
Then run the toolkit validation — a non-zero exit is blocking:
```
gov.py split --track {{ track }} --module {{ MOD }} --version {{ ver }} --dry-run
```
`gov.py analyze` (traceability matrix, EARS, marker validity, registry ↔ artifact agreement)
runs before the gate `{{ st.next }}`; CRITICAL findings keep the gate closed.

## 12. Ambiguity rule (no questions here)

`factory.yaml → ambiguity`, stated once in shared/GOVERNANCE-CORE.md:
- **non-breaking** (does not contradict a locked decision or a REQ) → choose the best-practice
  answer using `profile.knowledge.files` + `domain/` steering, write
  `decisions/{{ MOD }}/{{ factory.naming.adr_file.replace('{MOD}', MOD) }}` (Context / Decision /
  Consequences / traces) and **{{ factory.ambiguity.non_breaking.then }}**;
- **breaking** (contradicts a locked decision or a REQ) → ADR with status
  `{{ factory.ambiguity.breaking.status }}`, then **{{ factory.ambiguity.breaking.then }}**; the
  orchestrator surfaces it at the next human point.
Every "STOP and ask" of earlier engine generations is replaced by this rule.

## 13. Boundaries and hand-off

| Owns (mints) | References (read-only) | Never touches |
|---|---|---|
| {% for x in st.owns_ids %}`{{ x }}-*`{% if not loop.last %}, {% endif %}{% endfor %}; DB Alignment Manifest; Error Catalog; QRC; ALIGN result; ADRs it raises | {% for a, spec in atoms.items() if spec.owner not in [stage.id, 'any', 'versioning'] and a not in ['UXD','SCR','TC'] %}`{{ a }}-*` ({{ spec.owner }}){% if not loop.last %}, {% endif %}{% endfor %} | frontend/UX atoms (`UXD`, `SCR` — {{ atoms.UXD.owner }}), `TC-*` ({{ atoms.TC.owner }}), any code, framework annotations, executable queries, test artifacts |

Hand-off (the orchestrator prints it): the plan + registry are split by the toolkit into
`{{ factory.paths.module.packages_dir }}/{{ factory.tracks[track].packages.exec }}/` and delivered on
`{{ factory.naming.delivery_branch }}` after the `{{ st.next }}` verdict. The implementer reads
the plan in order (index → manifest → ADRs → phases in profile order → QRC → catalog), rewrites
every QR, implements security per R7, and publishes the api-docs file the frontend stage
requires (`factory.passes.2.required_inputs`).
