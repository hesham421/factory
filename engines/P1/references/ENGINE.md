{#- rendered at brief-build time: profile, factory, stage, mod, version -#}
{%- set langs = profile.languages -%}
{%- set vocab = profile.vocabulary -%}
{%- set conv = profile.conventions or {} -%}
{%- set kb = (profile.knowledge or {}).files -%}
{%- set naming = profile.stack.db.naming or {} -%}
{%- set api = profile.stack.backend.api -%}
{%- set atoms = factory.ids.atoms -%}
{%- set ears = factory.ids.ears.patterns -%}
{%- set idp = factory.ids.pattern -%}
{%- set amb = factory.ambiguity -%}
{%- set extra = (profile.review or {}).extra_checks or [] -%}
{%- macro art(name) %}{% for a in stage.produces if a.artifact == name %}{{ a.file }}{% endfor %}{% endmacro -%}
{%- macro owner(atom) %}{{ atoms[atom].owner if atom in atoms else '?' }}{% endmacro -%}
# {{ stage.title }} — ENGINE

```
Engine        : {{ stage.title }}
Stage id      : {{ stage.id }}
Pass          : {{ stage.pass_ if stage.pass_ is defined else stage['pass'] }}
Questions     : {{ stage.questions }} — ambiguity is self-resolved (§9)
Lane          : {{ stage.lane }}
Inputs        : {{ stage.inputs | join(', ') }}   (PRD must be APPROVED — gate {% for g in factory.gates if stage.id in g.blocks %}{{ g.id }}{% endfor %})
Produces      : {% for a in stage.produces %}{{ a.file }}{% if a.registry %} (registry){% endif %}{% if not loop.last %} · {% endif %}{% endfor %}
Owns IDs      : {{ stage.owns_ids | join(', ') }}   → `{{ idp }}` (seq width {{ factory.ids.seq_width }})
Format        : {{ stage.requirement_format }} for every functional requirement (§4)
Next          : {{ stage.next }}
Module        : {{ mod }}   Version: {{ version }}
Profile       : {{ profile.identity.id }} — {{ profile.identity.display }}
```

This engine produces the module's **functional truth**: the SRS. Everything downstream
(database, execution plans, UX, tests) derives from it; when a downstream artifact
disagrees with the SRS, the SRS governs and the other artifact is corrected. The SRS
never contains DDL, execution phases, component names or any ID owned by a later stage.

Completion (write → registry → analyze → commit) is owned by the orchestrator — see
`shared/GOVERNANCE-CORE.md`. {% if version is defined and version and version > 1 %}**Delta mode is active (v{{ version }})**{% else %}In a delta version (version > 1){% endif %}: read
`{{ factory.paths.module.state_dir }}/{{ factory.naming.current_state_file }}` of the previous version for every input and for this
stage's own artifacts, and emit only ADDED / MODIFIED / REMOVED elements plus the
`{{ factory.paths.module.change_manifest }}` per `shared/VERSIONING.md`. ID sequences continue from the current state.

Language policy: narrative in `{{ langs.primary }}`{% if langs.require_all %}; every label, screen name and message carries all
of `{{ langs.all | join(', ') }}` — a single-language message is INCOMPLETE{% endif %}; identifiers, IDs and field names in
the domain-profile's identifier language.

### IDs this stage assigns

| Atom | Meaning | Traces to | Requires |
|---|---|---|---|
{% for p in stage.owns_ids %}| `{{ p }}` | {{ atoms[p].title if p in atoms else 'screen requirement — the screen list handed to ' ~ owner('SCR') ~ ' (§7)' }} | {{ (atoms[p].traces_to | join(', ')) if p in atoms and atoms[p].traces_to else '—' }} | {{ (atoms[p].requires | join(', ')) if p in atoms and atoms[p].requires else '—' }} |
{% endfor %}
Sequences are continuous per module and per atom, never reused.

---

## 1 — Inputs and reading protocol

```
STEP A — PRD (approved): every {{ owner('US') }} story with its Traces → the demand this SRS must cover
STEP B — domain-profile.md §7 STEERING: vocabulary (verbatim), bounded contexts, codes,
         identifier rules, knowledge sources; §8 resolved decisions — never re-opened
STEP C — project-registry.md (shared/REGISTRY-SCHEMA.md categories):
         entity ownership + shared declarations → reuse, never re-create
         dependency index                        → XM candidates to carry into A8
         structural registry                      → names already fixed by other modules
         open-question index                      → must be empty for this module
STEP D — this stage's upstream module artifacts (module registry, business policies):
         entities owned / lookups / dependencies → names as given
         policies                                → the rules and requirements they imply
STEP E — knowledge sources (cite when applying a default)
{% if kb %}{% for f in kb %}         - {{ f }}
{% endfor %}{% else %}         - (none declared in the profile — domain-profile §7.5 sources only)
{% endif %}```

### 1.1 Registry pre-check (before any generation)

```
Does this entity already exist (any module)?      → reuse its ID; do not re-create
Does an equivalent lookup exist?                    → reuse its key
Does the module exist in the registry?              → extend, continue sequences
Naming conflict with a registered element?          → §9: ADR (non-breaking) or ADR BLOCKED
A closed decision / resolved open item affects it?  → apply as-is, no deviation
```

### 1.2 Feature type (auto-determined, documented, not asked)

```
Entity kinds (profile.vocabulary.entity_kinds): {{ vocab.entity_kinds | join(' / ') }}
For every entity: kind + reason (one line), recorded in A3. The user is not asked.
```

---

## 2 — Resolution order (zero questions)

Before writing any section, answer every needed fact from, in order:

```
1. business policies ({{ owner('POL') }})   → apply directly; cite the policy id
2. PRD stories ({{ owner('US') }})            → the need; scope and priority
3. registries (project + module)         → ownership, names, dependencies
4. knowledge sources (§1 STEP E)         → domain defaults — apply and document as DEFAULT
5. domain-profile STEERING + rules       → vocabulary, constraints
6. domain best practice                  → choose, document as ADR (§9)

DEFAULT documentation (inline, where applied):
  DEFAULT : [what was decided]
  Source  : [knowledge file § / domain-profile §]
  Override: [what to change if the client wants otherwise]
```

Nothing is asked. A fact that 1–6 cannot settle is an ambiguity → §9.

---

## 3 — Entities (`ENT`)

### 3.1 Ownership classification — first step, before any ID

| Classification | Rule | Declaration |
|---|---|---|
| PRIVATE | fully owned by this module | `ENT-{{ mod }}-[SEQ]` — [name] — PRIVATE |
| SHARED (owner) | other modules consume read-only | `ENT-{{ mod }}-[SEQ]` — [name] — SHARED (owner) |
| SHARED (consumer) | mastered by another module — NO new ID | consumes `ENT-[OWNER]-[SEQ]` — HARD-FK / SOFT-READ → XM candidate for {{ owner('XM') }} |

Entities already registered by another module are consumed, never re-created.

### 3.2 Defaults per entity kind (profile.conventions.entity_defaults)

{% if conv.entity_defaults %}Every entity of a kind below carries these fields automatically (in A3 they are
listed once under "standard fields — per profile", not re-typed per entity):

| Kind | Default fields |
|---|---|
{% for kind, fields in conv.entity_defaults.items() %}| {{ kind }} | {{ fields | join(', ') }} |
{% endfor %}{% else %}The profile declares no entity defaults: every field of every entity is stated
explicitly in A3, with its source.
{% endif %}
Naming (profile.stack.db.naming): {% if naming.pk_pattern %}primary key `{{ naming.pk_pattern }}`; {% endif %}{% if naming.flag_suffix %}flag fields end with `{{ naming.flag_suffix }}`; {% endif %}{% if naming.audit_fields %}audit fields `{{ naming.audit_fields | join(', ') }}` are system-filled and never accepted from a client{% endif %}. Field names are
taken from the module registry, the policies and the knowledge sources — never invented
from generic templates. Physical types belong to {{ owner('DBF') }}; the SRS states the
logical type only (text / number / decimal / flag / date-time / lookup / reference).

### 3.3 Structural rules

```
ARCH-1  Reuse before create — registry first.
ARCH-2  Master data has ONE owner; others consume via XM (never duplicated).
ARCH-3  Every referenced entity is defined (own ID) or consumed (owner's ID); no
        undefined reference anywhere.
ARCH-4  Names match the registry exactly.
ARCH-5  A SHARED (owner) entity that can be deactivated/deleted → a RULE stating the
        effect on SOFT-READ consumers (prevent / notify / cascade), traced to the REQ
        that introduces the operation. Undecidable → ADR (§9), never an open question.
{% if conv.lookups %}LOOKUPS Profile rule: {{ conv.lookups }}
        Lookup-backed fields reference a lookup key declared in A6; the SRS decides
        control type (fixed short list → lookup; growing/large set → reference entity
        with its own ENT). Same field → same lookup key in every screen.
{% endif %}{% if conv.numbering %}NUMBERING Profile rule: {{ conv.numbering }}
        Business/document numbers: decided PER ENTITY, never module-wide. An entity gets
        a business number only if (a) its identifier is used outside the system, (b) a
        policy/story asks for a human-readable reference, or (c) it is the numbered
        transactional document itself. If yes → system-generated on first save,
        read-only after, unique per entity type; the RULE cites the numbering rule above.
{% endif %}{% if conv.workflow_engine %}WORKFLOW Profile: workflow engine `{{ conv.workflow_engine }}`. Status lifecycles (a status field +
        allowed transitions) are always documented (A7). A module-specific approval flow
        is written only when a story explicitly asks for it{% if conv.workflow_engine == 'forbidden' %} and is custom to the module —
        never a generic engine{% endif %}.
{% endif %}```

---

## 4 — Requirements (`REQ`) — EARS is mandatory

Every functional requirement is **exactly one** EARS pattern
(`factory.ids.ears.patterns`); free prose is a contract violation (`gov.py analyze`:
CRITICAL).

```
{% for name, rx in ears.items() %}  {{ '%-11s' | format(name) }} {{ rx | replace('^', '') | replace('.+', '<condition / trigger / feature>') }}<response>
{% endfor %}  complex     a legitimate composition of the above (e.g. While … , when … , the system shall …)
```

```
REQ-{{ mod }}-[SEQ] — [short name]
  Pattern    : [{{ ears.keys() | join(' | ') }} | complex]
  Statement  : [one EARS sentence — one behaviour, one subject "the system"]
  Traces     : {{ owner('US') }}-{{ mod }}-[SEQ] [, …]      (≥ 1, mandatory)
  Entities   : ENT-{{ mod }}-[SEQ] [, …]
  Rationale  : [one line — why]
  Source     : [PRD story / policy / knowledge file / ADR]
  Priority   : [from the story]
```

Rules: singular (one requirement per REQ — "and" between behaviours means two REQs);
verifiable (a test can pass/fail it); no design (no table, endpoint, component);
every {{ owner('US') }} story is covered by ≥ 1 REQ; every REQ traces to ≥ 1 story
(a REQ with no story = invented scope → remove or raise an ADR).

### 4.1 Acceptance criteria (`AC`) — ≥ 1 per REQ

```
AC-{{ mod }}-[SEQ] — [REQ-{{ mod }}-[SEQ]]
  Given  : [precondition / state]
  When   : [action / event]
  Then   : [observable outcome — with the exact message when one is shown{% if langs.require_all %}, in each of {{ langs.all | join('/') }}{% endif %}]
```

Rules: each AC tests one path of one REQ (happy path first, then each unwanted/edge
path); an AC that cannot be phrased Given/When/Then means the REQ is not verifiable —
rewrite the REQ. ACs are the mechanical source of test cases for the standalone
test-gen stage (`TC` traces to `AC`).

---

## 5 — Business rules (`RULE`)

```
RULE-{{ mod }}-[SEQ] — [short name]
  Scope      : ENT-{{ mod }}-[SEQ]
  Trigger    : [when evaluated — on create / update / submit / transition …]
  Statement  : The system shall [prevent / require / validate …] when [condition]
  Message    : {% if langs.require_all %}{% for l in langs.all %}{{ l }}: [text]{% if not loop.last %} · {% endif %}{% endfor %}{% else %}[text]{% endif %}   (business language, not a literal translation)
  Traces     : REQ-{{ mod }}-[SEQ] [, …]                     (≥ 1, mandatory)
  Source     : [policy id / story / DEFAULT / ADR]
  Test-Hint  : [optional, one line of business intent for test-gen; omit if obvious]
```

Rules: a RULE formalises a constraint that a REQ needs; it never introduces behaviour
absent from every REQ. Database errors never reach users — every constraint that can
fail has a RULE with a message. Rules are defined once (A5) and referenced by ID from
every screen block.

---

## 6 — Lookups and status lifecycle

```
A6 LOOKUPS — one block per lookup key this module OWNS
  Key · used by field(s) · ENT · control type · owner (this module / consumed from [code])
  · values (code{% if langs.require_all %} + label per {{ langs.all | join('/') }}{% endif %}) · source (policy custom values / knowledge default)
  Consumed lookups are listed by key + owner only (never redefined).

A7 STATUS LIFECYCLE — for every entity with a status field and > 2 transitions
  Diagram of states and allowed transitions ONLY — no roles, no approval steps.
  Each transition that carries a constraint → RULE id.
  Module-specific approval flow (only if a story explicitly asks and the profile allows):
  documented as its own block with the story it traces to.
```

---

## 7 — Screens for `{{ owner('SCR') }}` (`SCR-REQ`)

This stage lists what screens the module needs — functional scope, not design.
`{{ owner('SCR') }}` turns each entry into `SCR` / `UXD` decisions and owns pattern,
container, layout and component choices. This stage never decides those.

```
SCR-REQ-{{ mod }}-[SEQ] — [screen name{% if langs.require_all %} in each of {{ langs.all | join('/') }}{% endif %}]
  Purpose      : [what the user achieves]
  Entities     : ENT-{{ mod }}-[SEQ] [, …]
  Operations   : [search / list / create / read / update / deactivate / custom …]
  Users        : [roles]
  Navigation   : [module] → [menu] → [screen]; from: [screens]; to: [screens]
  Content shape: [flat record | header + repeating lines with totals | true hierarchy
                  (parent/child) | other (journal, calendar …)] — a hint, not a design
  Traces       : REQ-{{ mod }}-[SEQ] [, …]
{% if conv.composite_screen %}  Composite    : Search + Entry (or Master + Detail, Wizard) = ONE screen requirement
                 (profile.conventions.composite_screen) — never one per sub-screen
{% endif %}```

Screen rules: search filters correspond to result columns; the same field uses the same
lookup key in search and entry; every screen declares its navigation position; every
operation on a screen is backed by a REQ.

{% if conv.security_model -%}
### 7.1 Access (profile.conventions.security_model)

```
Page registry : {{ conv.security_model.page_registry }}   — one row per screen requirement
Permission    : {{ conv.security_model.permission_pattern }}  with actions {{ conv.security_model.actions | join(' / ') }}
Gateway       : {{ conv.security_model.gateway_action }} — without it no other action applies
```
The SRS declares, per screen requirement, its page code and which roles hold which
action. It does NOT enumerate permission names as seed data — the security module
derives them from the page code (a second source of truth is a DUPLICATE finding).
No hardcoded authorisation logic is specified anywhere; checks go through the platform
authorisation layer. Implementation (annotations, guards) belongs to later stages.
{%- endif %}

---

## 8 — API expectations (stack-neutral)

The SRS states what operations the backend must expose; `{{ owner('API') }}` assigns the
`API` ids and designs them. Expectations follow the profile's conventions
(profile.stack.backend.api) and are referenced from screens by REQ, never by an API id.

```
Base path      : {{ api.base_path }}
Verbs          : {% for v, m in api.verbs.items() %}{{ v }} = {{ m }}{% if not loop.last %} · {% endif %}{% endfor %}
{% if api.envelope %}Response       : {{ api.envelope }}
{% endif %}{% if api.paging %}Paging         : {{ api.paging }}
{% endif %}{% if api.error_envelope %}Errors         : {{ api.error_envelope }}
{% endif %}
| Operation | Verb | Path (per base path) | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| create [entity] | [verb] | [base path with module/resource] | [fields] | [entity] | RULE-… | REQ-… |
| search [entity] | [verb] | … | [filters, paging] | [page of entity] | — | REQ-… |
| update [entity] | [verb] | …/{id} | [fields] | [entity] | RULE-… (immutability of number/code if any; uniqueness of names) | REQ-… |
| deactivate [entity] | [verb] | …/{id} | id | confirmation | RULE-… | REQ-… |
| read [entity] | [verb] | …/{id} | id | [entity] | — | REQ-… |
```
Lookup values are runtime-loaded (never enumerated in an API definition). Mobile or
channel-specific behaviour is stated as a REQ (`Where` pattern), not as widget design.

---

## 9 — Ambiguity rule (questions are forbidden here)

```
When steps 1–6 of §2 leave a genuine choice:
  NON-BREAKING (does not contradict an approved story, a policy, a registry fact or
  a closed decision) → write an ADR and CONTINUE with the chosen best practice.
      action: {{ amb.non_breaking.action }} · then: {{ amb.non_breaking.then }}
  BREAKING (contradicts an approved story / policy / registry fact / closed decision,
  or would change a REQ another artifact already relies on) → write the ADR with
  status {{ amb.breaking.status }} and STOP the pass; the orchestrator surfaces it at the next
  human point.
      action: {{ amb.breaking.action }} · status: {{ amb.breaking.status }} · then: {{ amb.breaking.then }}

ADR file : {{ factory.paths.decisions }}/{{ mod }}/{{ factory.naming.adr_file }}
Content  : Context · Decision · Consequences · traces (REQ / ENT / story ids) · status
Every ADR is referenced from the SRS "Decisions applied" section (§10 STANDALONE).
Details: shared/GOVERNANCE-CORE.md.
```

---

## 10 — `{{ art('srs') }}` — canonical template

Structure: **PART A** (module foundation — defined once) → **PART B** (one block per
screen requirement — references PART A by ID, never redefines) → **STANDALONE**.
No section is omitted; a section that does not apply says so in one line.

```markdown
# SRS — [Module display] ({{ mod }})
══════════════════════════════════════════════════════════════════
Module : {{ mod }}   Version : v{{ version }}   Profile : {{ profile.identity.id }}
Inputs : {{ stage.inputs | join(', ') }} (PRD approved [date])
Counts : ENT [N] · REQ [N] · AC [N] · RULE [N] · SCR-REQ [N] · ADR [N]
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |   (module, feature code, version, date, status, prepared by, decisions applied count)

## A2 — Functional context
In scope · Out of scope · Module function (one paragraph) · Detailed description
(workflow narrative, roles) · Current situation (steps / party / notes) ·
Current difficulties · Proposed system and benefits · General notes (constraints,
deferred items) — delete a sub-section only if it has no content and say so.

## A3 — Entities and fields
Standard fields per kind (profile) — listed once here.
### ENT-{{ mod }}-001 — [name]
| Kind | Ownership | Business number (yes/no — per §3.3 test) | Operations | Cross-module | Source |
| Field | Logical type | Required | Values / source (lookup key, ENT ref) | Notes | {% if langs.require_all %}{% for l in langs.all %}Label-{{ l }}{% if not loop.last %} | {% endif %}{% endfor %}{% else %}Label{% endif %} |
(repeat per entity)

## A4 — Functional requirements (EARS) and acceptance criteria
### REQ-{{ mod }}-001 — [name]        (record §4)
#### AC-{{ mod }}-001 … (record §4.1, ≥ 1 per REQ)
(repeat per requirement)

## A5 — Business rules
### RULE-{{ mod }}-001 — [name]       (record §5)
(repeat per rule — the ONLY place rule text appears)

## A6 — Lookups                      (§6 — the ONLY place lookup values appear)

## A7 — Status lifecycle             (§6 — diagram only; "not applicable" if ≤ 2 states)

## A8 — Module dependencies
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate (assigned by {{ owner('XM') }}) |
| External service | Purpose | Integration kind |

# PART B — SCREEN REQUIREMENTS   (one block per SCR-REQ; references PART A by ID only)

## SCR-REQ-{{ mod }}-001 — [name]
### B1 — Definition        (record §7: purpose, entities, operations, users, navigation, content shape, traces)
### B2 — Search / list     (filters = result columns; lookup keys by reference; RULEs applied by id) — "not applicable" if no search
### B3 — Input             (fields by ENT reference; buttons/actions → operation + RULE ids)
### B4 — Access            ({% if conv.security_model %}page code + roles per action per §7.1{% else %}roles per operation{% endif %})
### B5 — API expectations  (table §8, scoped to this screen)
(repeat per screen requirement)

# STANDALONE

## Traceability matrix
| {{ owner('US') }} | REQ | AC | RULE | ENT | SCR-REQ |
(every story → ≥ 1 REQ; every REQ → ≥ 1 AC; every RULE → REQ; every SCR-REQ → REQ.
 Orphans and dangling references are gate failures — `gov.py analyze`.)

## Decisions applied
| DEFAULT / ADR | What | Source | Override / status |

## Access summary            ({% if conv.security_model %}aggregate of B4 — B4 is the source{% else %}roles × screens aggregate{% endif %})
══════════════════════════════════════════════════════════════════
```

Single-source rule: PART A defines; PART B references by ID ("applies RULE-{{ mod }}-003").
Restating rule, lookup or entity text in PART B is a DUPLICATE finding (MAJOR).

---

## 11 — `{{ art('registry-srs') }}` — registry content

```
## REGISTRY — {{ stage.id }} — {{ mod }} v{{ version }}
Entities      : ENT id · name · kind · PRIVATE / SHARED(owner) · status REGISTERED
Consumed      : owner ENT id · owner module · HARD-FK / SOFT-READ   (→ dependency index)
Lookups owned : key · ENT · values count          Lookups consumed : key · owner
Screens       : SCR-REQ id · name · page code{% if not conv.security_model %} (if any){% endif %}
Requirements  : REQ count · AC count · RULE count · last sequence per atom
                ({% for p in stage.owns_ids %}{{ p }}: [n]{% if not loop.last %}, {% endif %}{% endfor %})
Decisions     : ADR ids (+ BLOCKED, if any)
Event         : "{{ stage.id }} completed: {{ mod }} v{{ version }} — [counts]"
```
The orchestrator merges these rows into `project-registry.md` (entity ownership,
shared declarations, dependency index, structural registry, pipeline status, events).

---

## 12 — Boundaries

```
OWNS      : {{ stage.owns_ids | join(', ') }} · functional truth · the traceability matrix from stories down
DOES NOT  : {% for atom, spec in atoms.items() if spec.owner != stage.id and spec.owner not in ['any', 'versioning'] %}{{ atom }} ({{ spec.owner }}){% if not loop.last %} · {% endif %}{% endfor %}
            · DDL / physical types · execution phases · UX patterns, containers, components
            · endpoint design · permission seed data · test cases
```

---

## 13 — Self-check before emitting (ISO/IEC/IEEE 29148 attributes + structure)

Quality attributes scored at the pass gate (`factory.review.rubric`):
{% for r in factory.review.rubric %}- [ ] **{{ r }}** — {% if r == 'unambiguous' %}one reading per REQ / AC / RULE; no "etc.", "as appropriate", "fast"{% elif r == 'verifiable' %}every REQ has ≥ 1 Given/When/Then AC; every RULE has a message{% elif r == 'complete' %}every story covered; A1–A8, every B1–B5, STANDALONE present; no placeholder left{% elif r == 'consistent' %}vocabulary = STEERING block; names = registry; no REQ contradicts a policy or another REQ{% elif r == 'singular' %}one behaviour per REQ; one path per AC{% elif r == 'feasible' %}no requirement depends on an undefined entity, unavailable module or forbidden mechanism{% elif r == 'traceable' %}REQ→{{ owner('US') }}, AC→REQ, RULE→REQ, SCR-REQ→REQ all present; no orphan, no dangling id{% else %}per shared/QUALITY-RUBRIC.md{% endif %}
{% endfor %}
Structural checks:
- [ ] Every REQ statement matches exactly one EARS pattern.
- [ ] Every entity has a kind from `{{ vocab.entity_kinds | join(', ') }}`{% if conv.entity_defaults %} and carries its kind's default fields{% endif %}.
- [ ] Every consumed entity references the owner's ENT id; none re-created.
- [ ] Rules, lookups, entities defined in PART A only; PART B references by ID.
- [ ] Every DEFAULT has Source + Override; every ADR is listed under Decisions applied; no BLOCKED ADR unless the pass stopped.
- [ ] No question raised anywhere; no open-questions section exists.
- [ ] Sequences continuous per atom{% if version is defined and version and version > 1 %}; continued from v{{ version - 1 }} current state{% endif %}.
{% if langs.require_all %}- [ ] Every label, screen name and message carries all of `{{ langs.all | join(', ') }}`.
{% endif %}{% for c in extra if c.stage == stage.id %}- [ ] Profile check `{{ c.id }}` ({{ c.severity }}): {{ c.check }}.
{% endfor %}