{#- rendered at brief-build time: profile, factory, stage, mod, version -#}
{%- set langs = profile.languages -%}
{%- set conv = profile.conventions or {} -%}
{%- set db = profile.stack.db -%}
{%- set dialect = db.target_dialect -%}{#- REQUIRED: stated, not the list's first element -#}
{%- set naming = db.naming or {} -%}
{%- set smap = db.syntax_map or {} -%}
{%- set pkgen = db.pk_generation -%}{#- REQUIRED: no engine-side default (F5a) -#}
{%- set seqpat = naming.sequence_pattern -%}
{%- set atoms = factory.ids.atoms -%}
{%- set idp = factory.ids.pattern -%}
{%- set amb = factory.ambiguity -%}
{%- set extra = (profile.review or {}).extra_checks or [] -%}
{%- macro art(name) %}{% for a in stage.produces if a.artifact == name %}{{ a.file }}{% endfor %}{% endmacro -%}
{%- macro owner(atom) %}{{ atoms[atom].owner if atom in atoms else '?' }}{% endmacro -%}
{%- macro syn(type) %}{{ smap[type][dialect] if type in smap and dialect in smap[type] else '[' ~ type ~ ' — not in syntax_map: state the dialect syntax in the script header]' }}{% endmacro -%}
# {{ stage.title }} — ENGINE

```
Engine        : {{ stage.title }}
Stage id      : {{ stage.id }}
Pass          : {{ stage.pass_ if stage.pass_ is defined else stage['pass'] }}
Questions     : {{ stage.questions }} — ambiguity is self-resolved (§9)
Lane          : {{ stage.lane }}
Inputs        : {{ stage.inputs | join(', ') }}
Produces      : {% for a in stage.produces %}{{ a.file }}{% if a.registry %} (registry){% endif %}{% if not loop.last %} · {% endif %}{% endfor %}
Owns IDs      : {{ stage.owns_ids | join(', ') }}   → `{{ idp }}` (seq width {{ factory.ids.seq_width }})
Dialect       : {{ dialect }}   (profile.stack.db.target_dialect; syntax from profile.stack.db.syntax_map)
Next          : {{ stage.next }}
Module        : {{ mod }}   Version: {{ version }}
Profile       : {{ profile.identity.id }} — {{ profile.identity.display }}
```

This engine produces the module's **structural truth**: an executable database script
derived from the SRS, a field-level traceability matrix and the cross-module dependency
register. It invents no business logic and never redesigns SRS meaning; when the script
and the SRS disagree, the SRS governs and the script is corrected. It produces no
execution phases and no implementation sequencing.

Completion (write → registry → analyze → commit) is owned by the orchestrator — see
`shared/GOVERNANCE-CORE.md`. {% if version is defined and version and version > 1 %}**Delta mode is active (v{{ version }})**{% else %}In a delta version (version > 1){% endif %}: read
`{{ factory.paths.module.state_dir }}/{{ factory.naming.current_state_file }}` of the previous version for every input and for this
stage's own artifacts, and emit only ADDED / MODIFIED / REMOVED elements plus the
`{{ factory.paths.module.change_manifest }}` per `shared/VERSIONING.md` — the script of a delta version is a
migration (ALTER / CREATE / DROP for the changed objects only); sequences continue.

### IDs this stage assigns

| Atom | Meaning | Traces to |
|---|---|---|
{% for p in stage.owns_ids %}| `{{ p }}` | {{ atoms[p].title if p in atoms else '—' }} | {{ (atoms[p].traces_to | join(', ')) if p in atoms and atoms[p].traces_to else '—' }} |
{% endfor %}
---

## 1 — Inputs and entry check

```
{% for i in stage.inputs %}  {{ i }}{{ ' ' * (16 - i|length) }}: ✓ present / ✗ MISSING (pipeline error — not a question)
{% endfor %}  domain-profile STEERING : vocabulary verbatim; identifier rules
  project-registry        : structural registry (names fixed by other modules),
                            dependency index, shared declarations
  Extracted               : [N] entities → [N] tables · [N] intra-module FKs ·
                            [N] XM candidates (SRS A8) · [N] lookups (SRS A6)
```

Reading protocol for the SRS: PART A entirely — A3 (entities, fields, logical types),
A5 (rules → constraints), A6 (lookups → seed data), A7 (status → check constraints),
A8 (consumed entities → XM). PART B is not read for structure (screens are not tables).

---

## 2 — DB field traceability matrix (`DBF`)

The single canonical source of `DBF` → column → type → SRS origin. Downstream
artifacts (the backend plan's alignment manifest) reference columns **by DBF id only**
and never restate column names, types or SRS references.

```
## DB FIELD TRACEABILITY MATRIX — {{ mod }} v{{ version }}
| DBF id            | Table | Column | Type ({{ dialect }}) | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
| DBF-{{ mod }}-001 | …     | …      | …                    | ENT-{{ mod }}-001.[field] | REQ-{{ mod }}-… | NOT NULL | — |
Total: [N] DBF ids across [N] tables
```

```
ASSIGNMENT RULES
  - Sequence continuous across the module (not per table); never reused, even for a
    removed column.
  - Per table: PK first, then the entity's own columns in SRS order, then FK columns,
    then standard columns (audit fields last).
  - Every column traces to an ENT.field of the SRS AND to ≥ 1 REQ (via the entity's
    requirements); a standard column traces to the profile default that mandates it
    ("profile: entity_defaults.<kind>") and to the ENT.
  - A column with no SRS origin does not exist (NO-COLUMN-INVENTION, §3).
```

---

## 3 — Naming and column rules

```
IDENTIFIER TRANSFORMATION (stated once in the script header, applied everywhere)
  logical field name (SRS)  →  physical column name: one deterministic transformation
  (case + word separator) declared for {{ dialect }} — never two spellings of one field.
  Respect the dialect's identifier length limit and reserved words.

TABLE NAMES     : [module code]_[entity abbreviation] — module code from the domain-profile
{% if naming.pk_pattern %}PRIMARY KEY     : the SRS field named by `{{ naming.pk_pattern }}` (profile.stack.db.naming.pk_pattern)
{% endif %}FOREIGN KEYS    : the SRS reference field; constraint FK_[LOCAL]_[REF] (FK_[LOCAL]_[REF]_[n] when several)
{% if naming.audit_fields %}AUDIT COLUMNS   : {{ naming.audit_fields | join(', ') }} on every table that carries them per its entity kind —
                  filled by the platform, never by a client; user columns hold a
                  principal string, not a numeric FK
{% endif %}{% if naming.flag_suffix %}FLAG COLUMNS    : end with `{{ naming.flag_suffix }}`; type {{ syn('boolean') }}; soft-deactivate flag defaults to active —
                  there is no "deleted" column: deactivation, not deletion
{% endif %}INDEXES         : IDX_[TABLE]_[COLUMN] (composite: IDX_[TABLE]_[ABBR1]_[ABBR2])
CONSTRAINTS     : PK_[TABLE] · UQ_[TABLE]_[COL] · CHK_[TABLE]_[COL]
SEQUENCES       : {% if seqpat %}`{{ seqpat }}` (profile.stack.db.naming.sequence_pattern){% else %}(profile.stack.db.naming.sequence_pattern — not declared){% endif %} — emitted only when
                  profile.stack.db.pk_generation is `sequence` (§4)

NO-COLUMN-INVENTION (CRITICAL)
  Every column is (1) an SRS field, or (2) a profile default for the entity's kind,
  or (3) derived from an FK / XM. Nothing from generic templates or prior examples.
  Modules declared EXCEPTION in the registry keep their real names as-is.
```

---

## 4 — Table definition rules

```
For every ENT in SRS A3 → one table (consumed SHARED entities are NOT re-created).
Each table block, in order:
  CREATE TABLE (all columns, inline NOT NULL, inline CHECK)
  COMMENT ON TABLE + COMMENT ON COLUMN for every column (the comment cites the DBF id)
  PRIMARY KEY · UNIQUE (from RULEs) · CHECK (from RULEs / status values)
  FK constraints — inline only when intra-module; XM FKs per §6/§7
PK GENERATION — profile.stack.db.pk_generation = `{{ pkgen }}` (a PROFILE decision, never a
  dialect default; the same database may not carry two PK strategies)
{% if pkgen == 'sequence' %}  Strategy `sequence`: BLOCK 1 carries ONE sequence per table, named by
  {% if seqpat %}`{{ seqpat }}`{% else %}profile.stack.db.naming.sequence_pattern (not declared — declare it before emitting){% endif %}, emitted with the {{ dialect }} syntax from
  profile.stack.db.syntax_map.sequence:
      {{ syn('sequence') }}
  ({name} = the sequence name; use this row verbatim — never another dialect's spelling
  of the cache/cycle clauses.)
  The PK column is declared as a plain `{{ syn('pk') }} NOT NULL` column (syntax_map.pk) and
  carries NO identity clause and NO sequence DEFAULT. The application populates the key
  from the named sequence; the sequence name is carried into the plan by {{ owner('API') }}.
  `{{ syn('identity') }}` must not appear anywhere in the script.
{% else %}  Strategy `identity`: the PK column carries the {{ dialect }} identity clause from
  profile.stack.db.syntax_map.identity:
      {{ syn('identity') }}
  BLOCK 1 stays empty (state "none: every PK uses the identity clause") unless the SRS
  needs a sequence for something other than a PK.
{% endif %}  NEVER a trigger for PK population; NEVER a default that calls a sequence on the PK column.
```

### 4.1 Datatype governance (profile.stack.db.syntax_map → {{ dialect }})

| Logical type (SRS) | {{ dialect }} syntax |
|---|---|
{% for t in smap if t not in ['identity', 'sequence'] %}| {{ t }} | {{ syn(t) }} |
{% endfor %}{% if not smap %}| (profile declares no syntax_map) | state each type once in the script header and use it consistently |
{% endif %}
(`identity` and `sequence` are not column types — they are the PK-generation clauses of
§4, selected by `profile.stack.db.pk_generation`, and are listed there only.)

Rules: only the syntaxes above (or one stated once in the script header for a logical
type the map lacks); `n` / `p,s` are filled from the SRS field definition; a
deviation carries a governance note citing the SRS field that requires it; the other
declared dialects ({{ db.dialects[1:] | join(', ') if db.dialects | length > 1 else 'none' }}) are not emitted — one dialect per script.

### 4.2 Lookup and reference data

{% if conv.lookups %}Profile rule: {{ conv.lookups }}
{% endif %}```
Lookup-backed field (SRS A6, control = lookup) → the stored value is the lookup CODE
  (never a numeric key); seed rows for every value the SRS lists, each block citing
  the SRS lookup key; the shared lookup tables (if the platform uses them) are created
  once by the first module that needs them and only seeded afterwards — never
  re-created in a later module's script.
SEED ROWS FOR A TABLE THIS SCRIPT DOES NOT CREATE — required, not optional. The common
  case is that the lookup tables belong to ANOTHER module, and a seed block written only
  for tables this script creates is then EMPTY: nothing anywhere in the pipeline ever
  creates the values, and the module's first create call fails validating a code against
  an empty table. Emit the INSERT block for every key this module owns, against the owning
  module's table by its exact name, and say which module owns it. Whichever module owns the
  table, the module that owns the KEY owns the seed.
Reference entity (SRS decided: its own ENT) → an ordinary table per §4; consumers
  hold an FK.
```

### 4.3 Indexes

```
Mandatory : every FK column; every column used in SRS search / list filters (PART B B2);
            every UNIQUE business key. PK indexes are implicit — never duplicated.
```

---

## 5 — XM register (`XM`) — cross-module dependencies

`XM` is the single identifier for every cross-module dependency in the pipeline
(lifecycle and states: `shared/XM-PROTOCOL.md`). Assigned here; extended by
`{{ owner('API') }}` (status, blocks, workaround, unblock condition) — never re-assigned;
never touched by the frontend stage. The factory's lifecycle ends at DELIVERED; CLOSED
belongs to the consumer repository.

```
## XM REGISTER — {{ mod }} v{{ version }}
| XM id            | Type      | This table | Column / access | Target table | Target module | Traces (REQ) | Status |
| XM-{{ mod }}-001 | HARD-FK   | …          | [FK column]     | …            | [code]        | REQ-{{ mod }}-… | READY / DEFERRED |
| XM-{{ mod }}-002 | SOFT-READ | (application) | [join / read pattern] | … | [code]  | REQ-{{ mod }}-… | ACTIVE / CONDITIONAL |

TYPES
  HARD-FK    physical FK constraint; target table must exist → DEFERRED until the
             target module's script is gated
  SOFT-READ  application-level read of another module's table, no FK column; the
             "column / access" cell describes the access pattern
STATUS (at this stage)
  READY        target script gated — constraint applied
  DEFERRED     HARD-FK whose target is not yet gated — column created, constraint in
               the deferred patch block (§6)
  CONDITIONAL  SOFT-READ whose target table exists in no gated script yet
  ACTIVE       SOFT-READ whose target is gated (never "closed")
SOURCES
  SRS A8 consumed entities (HARD-FK / SOFT-READ as classified there); RULEs that
  join by code to another module's table; APIs that read another module's data.
  An XM with no SRS A8 origin is an ORPHAN finding. Audit columns are never XMs.
```

### 5.1 Deferred FK handling

```
For every DEFERRED XM: create the column (with its DBF id); comment it
  '[XM id]: FK to [target] — DEFERRED pending [module] script';
do NOT create the constraint in the main DDL; emit a commented patch block:
  -- DEFERRED FK — XM-{{ mod }}-[n]
  -- Target module : [code]   Apply when : target script gated and deployed
  -- Unblock       : [condition, extended by {{ owner('API') }}]
  -- ALTER TABLE [table] ADD CONSTRAINT FK_[local]_[ref] FOREIGN KEY ([col]) REFERENCES [target] ([pk]);
```

### 5.2 SOFT-READ handling

```
For every SOFT-READ XM: register it (Type SOFT-READ); add a commentary block:
  -- XM-{{ mod }}-[n] SOFT-READ — this module's [service/query] reads [TARGET].[COLUMN]
  -- from [module] without an FK. Rationale: [from SRS]. Risk: changes to [TARGET]
  -- require impact assessment on [affected requirements].
```

---

## 6 — FK classification (every FK is exactly one of these)

```
INTRA-MODULE FK    both tables in this script → constraint in main DDL; DBF on the column; no XM
READY HARD-FK      target in another module's gated script → constraint applied; XM READY
DEFERRED HARD-FK   target not yet gated → no constraint; XM DEFERRED; patch block §5.1
SOFT-READ          application read → no constraint by design; XM SOFT-READ (§5.2)
```

---

## 7 — `{{ art('db-script') }}` — output structure

```
1. HEADER          module · version · dialect {{ dialect }} · schema prefix (or "none") ·
                   identifier transformation (§3) · date · counts
2. DB FIELD TRACEABILITY MATRIX   (§2 — governance documentation, not SQL)
3. XM REGISTER                    (§5)
4. FULL_DATABASE_SCRIPT           (§7.1 — the ONLY place SQL appears)
5. DECISIONS APPLIED              (DEFAULTs + ADR ids, §9)
6. REGISTRY CONTENT               (§10)
```

### 7.1 FULL_DATABASE_SCRIPT — one consolidated executable

Copy-and-run against a clean schema of {{ dialect }} without editing. Not documentation:
a deployable. Mandatory block order (guarantees zero dependency errors):

```
BLOCK 1   SEQUENCES {% if pkgen == 'sequence' %}— MANDATORY: one per table (§4), count == table count{% else %}(only if the SRS needs one; PK generation uses the identity clause){% endif %}
BLOCK 2   PARENT TABLES (no FK dependencies; lookup/reference tables DDL only)
BLOCK 3   CHILD TABLES (intra-module FK targets already created; chain A → B → C)
BLOCK 4   COMMENTS (table + every column; each column comment cites its DBF id)
BLOCK 5   CONSTRAINTS  5a PK · 5b UNIQUE · 5c CHECK · 5d intra-module FK (parent PK first)
BLOCK 6   TRIGGERS — audit triggers only when an SRS RULE requires them; NEVER PK triggers
BLOCK 7   INDEXES (non-PK)
BLOCK 8   LOOKUP SEED DATA (INSERT with column lists; COMMIT at the end of the block)
BLOCK 9   VIEWS (CREATE OR REPLACE)
BLOCK 10  FUNCTIONS / PROCEDURES (dialect terminator syntax; only if the SRS needs them)
BLOCK 11  DEFERRED FK PATCH BLOCKS — commented out, one per DEFERRED XM, labelled
```

```
SYNTAX RULES (dialect-conditional — the dialect's own syntax comes from
profile.stack.db.syntax_map; the rules below hold for any dialect)
  S-1  Every statement ends with the dialect's terminator; no trailing comma before a
       closing parenthesis; every referenced object has its CREATE in this script.
  S-2  Types: only §4.1 syntaxes; never a type from another dialect.
  S-3  Constraints in ALTER TABLE form (PK / FK / UQ / CHK names per §3); FK declared
       after the parent PK exists.
  S-4  No PK-population trigger; no sequence default on a PK column.
  S-5  Seed INSERTs carry a column list; NULL is never the string 'NULL'; COMMIT after DML.
  S-6  Deferred FK blocks are fully commented and carry their XM id and target module.
  S-7  Schema prefix: all objects qualified, or none — never mixed.
  S-8  No placeholders: no "...", no "[...]" inside SQL — real names and values only.
```

### 7.2 Self-verification before emitting the script

```
SYNTAX        □ S-1 … S-8 hold for every statement
              □ every type appears in §4.1 (or is declared once in the header)
PK STRATEGY   □ every PK follows profile.stack.db.pk_generation (`{{ pkgen }}`) — {% if pkgen == 'sequence' %}one
                {% if seqpat %}`{{ seqpat }}`{% else %}sequence{% endif %} per table in BLOCK 1, PK columns plain `{{ syn('pk') }} NOT NULL`,
                and `{{ syn('identity') }}` nowhere in the script{% else %}the identity clause on every
                PK column and no PK sequence{% endif %}
ORDER         □ sequences first (if any) · parents before children · PK before FK ·
                lookup DDL before lookup INSERTs · COMMIT after the last INSERT of a block
COMPLETENESS  □ every SRS entity has a table · every SRS field a column (DBF) ·
                every lookup its seed rows · every index present ·
                every DEFERRED XM a commented block in BLOCK 11 ·
                shared lookup tables not re-created
DEFERRED FK   □ every deferred block commented · labelled with its XM id ·
                no live FK references another module's table
TRACE         □ every DBF traces to ENT.field + REQ · every XM traces to REQ and to an
                SRS A8 row · no orphan, no dangling id
```

---

## 8 — Governance recovery

```
A module whose script was produced from an incomplete or corrected SRS, or whose
script arrives after downstream artifacts exist:
  1. Re-run this stage on the current SRS ({{ factory.paths.module.state_dir }}/ current state).
  2. Re-run `gov.py analyze` on the affected artifacts (this script, the backend plan's
     alignment manifest, the registries). Findings are resolved at the next pass gate.
  3. XM rows whose target became gated → status update per shared/XM-PROTOCOL.md.
No separate audit stage exists; `analyze` is the recovery check.
```

---

## 9 — Ambiguity rule (questions are forbidden here)

```
Structural choices the SRS does not settle (normalisation of a repeating group, a
composite vs surrogate key, an index strategy, a precision):
  NON-BREAKING → ADR, CONTINUE with the chosen best practice
      action: {{ amb.non_breaking.action }} · then: {{ amb.non_breaking.then }}
  BREAKING (contradicts an SRS REQ / ENT, a registered name, or a gated module's
  structure) → ADR status {{ amb.breaking.status }}, STOP the pass
      action: {{ amb.breaking.action }} · status: {{ amb.breaking.status }} · then: {{ amb.breaking.then }}
ADR file : {{ factory.paths.decisions }}/{{ mod }}/{{ factory.naming.adr_file }}  (Context · Decision · Consequences · traces · status)
Details  : shared/GOVERNANCE-CORE.md
```

---

## 10 — `{{ art('registry-db') }}` — registry content

```
## REGISTRY — {{ stage.id }} — {{ mod }} v{{ version }}
Tables        : table · ENT id · kind · DBF range              (→ structural registry)
XM index      : XM id · type · from {{ mod }} · to [code] · status    (→ dependency index)
Lookups       : key · seeded values count · owner
Sequences     : last DBF · last XM
Decisions     : ADR ids (+ BLOCKED, if any)
Event         : "{{ stage.id }} completed: {{ mod }} v{{ version }} — [N] tables, [N] DBF, [N] XM"
Cascade       : for every registry XM row targeting {{ mod }} with status DEFERRED, note
                that this script now exists → resolution per shared/XM-PROTOCOL.md
```

---

## 11 — Boundaries

```
OWNS      : {{ stage.owns_ids | join(', ') }} · the traceability matrix · the XM register · DDL structure,
            naming and datatype governance for this module
DOES NOT  : {% for atom, spec in atoms.items() if spec.owner != stage.id and spec.owner not in ['any', 'versioning'] %}{{ atom }} ({{ spec.owner }}){% if not loop.last %} · {% endif %}{% endfor %}
            · business logic · execution phases · frontend structure (the frontend stage
            never reads this script; it consumes API docs)
```

---

## 12 — Self-check before emitting

- [ ] Every SRS entity → one table; every consumed SHARED entity → FK / XM, not a table.
- [ ] Every column has a DBF id, a type from §4.1, a comment, and traces (ENT.field + REQ).
- [ ] Every cross-module reference is exactly one FK class (§6) and, unless intra-module, an XM row traced to REQ + SRS A8.
- [ ] Every DEFERRED XM has its column, its comment and its commented patch block; no live cross-module FK.
- [ ] Script block order 1–11 respected; §7.2 checklist passed; script is copy-and-run for {{ dialect }}.
- [ ] PK generation matches `profile.stack.db.pk_generation` = `{{ pkgen }}` for **every** table (§4) — no second strategy anywhere.
- [ ] Every RULE that maps to a constraint is present (UNIQUE / CHECK) and named per §3.
- [ ] Every DEFAULT / ADR listed under Decisions applied; no BLOCKED ADR unless the pass stopped.
- [ ] No question raised; sequences continuous{% if version is defined and version and version > 1 %}; continued from v{{ version - 1 }} current state; the script is a migration{% endif %}.
{% for c in extra if c.stage == stage.id %}- [ ] Profile check `{{ c.id }}` ({{ c.severity }}): {{ c.check }}.
{% endfor %}