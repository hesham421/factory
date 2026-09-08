{#- rendered at brief-build time: profile, factory, stage, mod, version -#}
{%- set lane = factory.lanes.get(stage.lane) if stage.lane is defined else none -%}
{%- set langs = profile.languages -%}
{%- set vocab = profile.vocabulary -%}
{%- set conv = profile.conventions or {} -%}
{%- set kb = (profile.knowledge or {}).files -%}
{%- set ears = factory.ids.ears.patterns -%}
{%- set idp = factory.ids.pattern -%}
{%- macro art(name) %}{% for a in stage.produces if a.artifact == name %}{{ a.file }}{% endfor %}{% endmacro -%}
# {{ stage.title }} — ENGINE

```
Engine        : {{ stage.title }}
Stage id      : {{ stage.id }}
Pass          : {{ stage.pass_ if stage.pass_ is defined else stage['pass'] }}
Questions     : {{ stage.questions }} — resolved in-dialogue with recommended answers; user confirms
Dialogue      : {{ 'yes — lane ' ~ stage.lane if stage.dialogue else 'no' }}{% if lane and lane.dialogue %} ({{ lane.implementers | join(' + ') }}; ≤ {{ lane.dialogue.max_rounds }} rounds; converge on "{{ lane.dialogue.converge_on }}"; output: {{ lane.dialogue.output }}){% endif %}
Inputs        : {{ stage.inputs | join(', ') }}
Produces      : {% for a in stage.produces %}{{ a.file }}{% if not loop.last %} · {% endif %}{% endfor %}
Owns IDs      : {{ stage.owns_ids | join(', ') }}   → `{{ idp }}` (seq width {{ factory.ids.seq_width }})
Next          : {{ stage.next }}
Module        : {{ mod }}   Version: {{ version }}
Profile       : {{ profile.identity.id }} — {{ profile.identity.display }}
```

This engine turns free-form vision text into a closed architectural context: first a
**platform summary** (tiered module table, dependency map), then — per module — a
**module registry** and **business policies** written as EARS statements with
`{{ stage.owns_ids | join('/') }}` IDs. Its outputs are CONTEXT for `{{ stage.next }}`, never requirements.

Completion (write → registry → analyze → commit) is owned by the orchestrator — see
`shared/GOVERNANCE-CORE.md`. {% if version is defined and version and version > 1 %}**Delta mode is active (v{{ version }})**{% else %}In a delta version (version > 1){% endif %}: read `{{ factory.paths.module.state_dir }}/{{ factory.naming.current_state_file }}` of the previous
version for every input and for this stage's own artifacts, and emit only ADDED /
MODIFIED / REMOVED elements plus the `{{ factory.paths.module.change_manifest }}` per `shared/VERSIONING.md`.

```
╔══════════════════════════════════════════════════════════════════════╗
║ ABSOLUTE BOUNDARY                                                    ║
║ This stage does not write requirements, screens, field lists,        ║
║ validation rules, entity IDs or any content owned by {{ stage.next }} or later.  ║
║ A request for such content → produce this stage's artifacts, then    ║
║ redirect once (§7). No partial draft. No exception.                  ║
╚══════════════════════════════════════════════════════════════════════╝
```

Language policy: narrative in `{{ langs.primary }}`{% if langs.require_all %}; every module name, entity name and policy
statement carries all of `{{ langs.all | join(', ') }}`{% endif %}.

---

## 1 — Reading protocol (before any analysis)

```
STEP A — domain-profile.md (steering — read first)
  §7 STEERING → vocabulary (use verbatim), bounded contexts, module codes,
                identifier rules, knowledge sources
  §1–§6       → scope, purpose, responsibilities, components, rules, relations
  §8          → resolved decisions — never re-open one

STEP B — project-registry.md (categories per shared/REGISTRY-SCHEMA.md)
  module index            → known modules — do NOT re-discover
  entity ownership        → known owners — apply directly
  shared declarations     → known shared entities — apply directly
  dependency index        → extend, never contradict
  open-question index     → OPEN rows this stage may resolve in dialogue (§5)
  pipeline status         → modules already past this stage → EXISTING / EXCEPTION

STEP C — prior module artifacts (this stage's own outputs for other modules,
         from {{ factory.paths.module.state_dir }}/ when they exist)
  entities owned / lookups owned / lookups consumed / dependencies → ground truth;
  a conflict between vision text and a module registry → the registry wins and the
  conflict is listed under OPEN ITEMS of the platform summary.

STEP D — knowledge sources (cite when applying a default)
{% if kb %}{% for f in kb %}  - {{ f }}
{% endfor %}{% else %}  - (the profile declares no knowledge files — domain-profile §7.5 sources only)
{% endif %}```

Every structural decision comes from A → B → C → D in that order, then from domain
best practice; the user is asked only what none of these settle (§5).

---

## 2 — Phase 1: vision → `{{ art('platform-summary') }}`

### 2.1 Transformation (three steps)

```
STEP 1 — EXTRACT from the vision text
  Modules (explicit or implied) — detection table from the profile:
{% if vocab.keyword_map %}{% for code, words in vocab.keyword_map.items() %}    {{ '%-6s' | format(code) }} {{ vocab.module_prefixes[code] if code in vocab.module_prefixes else '' }}  ← {{ words | join(' / ') }}
{% endfor %}{% else %}    (profile.vocabulary.keyword_map not declared — match against module display names)
{% endif %}    (unlisted) → domain-profile §4 components + layer heuristics; still one of the
               profile's codes ({{ vocab.module_prefixes.keys() | join(', ') }}) or RESERVED per the registry.
  Explicit statements:
    scope exclusions ("without X", "not now")
    specific policies (limits, thresholds, exceptions)   → §3.3 candidates
    custom values (named lookup values)                   → §3.3 candidates

STEP 2 — ENRICH from knowledge sources + domain-profile
  For each module: layer, type, tier, dependencies from the knowledge files and
  the domain-profile relations; remove what the user excluded; add what the user
  mentioned beyond the pattern. Cite the source of every enrichment.

STEP 3 — RESOLVE from the registry
  module past this stage in pipeline status   → EXCEPTION (read as-is; skip in Phase 2)
  module with a prior module-registry artifact → EXISTING (Phase 2 extends it)
  otherwise                                    → NEW
```

### 2.2 Platform summary — template

```markdown
# PLATFORM SUMMARY — [Platform name — from the vision text or domain-profile]
══════════════════════════════════════════════════════════════════
Profile : {{ profile.identity.id }}   Domain profile : v[N]   Registry : v[semver]
══════════════════════════════════════════════════════════════════

## OVERVIEW
[One paragraph — what the platform does; enriched with domain context, not a restatement.]

## MODULES
| #   | Code | Module | Bounded context | Layer | Type | Depends on | Status |
|-----|------|--------|-----------------|-------|------|------------|--------|
| 1.1 | [code] | [display] | [context] | L1 | [master data / engine / reference / transactional / reporting] | ROOT | NEW |
| 2.1 | [code] | [display] | [context] | L3 | [type] | [code], [code] (SOFT) | EXISTING |
Status: NEW (Phase 2 produces) · EXISTING (Phase 2 extends) · EXCEPTION (read as-is)
Numbering: [tier].[sequence within tier] — the user requests Phase 2 by this number.

## DEPENDENCY MAP
Build order: Tier 1 [codes] → Tier 2 [codes] → Tier 3 [codes] → Tier 4 [reporting]
Key dependencies (one line each):
  [CODE-A] → HARD → [CODE-B] : [reason]
  [CODE-C] → SOFT → [CODE-D] : [reason]
  [CODE-E] → LOOKUP → [CODE-F] : consumes [lookup key]

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
{% if conv.workflow_engine %}| Workflow engine | profile: `{{ conv.workflow_engine }}` |
{% endif %}| [user-excluded item] | user stated "not now" |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |

## OPEN ITEMS
[Only a registry ↔ vision conflict or a genuinely ambiguous scope boundary that the
 dialogue could not close. Otherwise: "None — platform scope fully determined."]

## NEXT STEP
Reply with a plain instruction to adjust, or with a module number to start Phase 2.
```

### 2.3 Confirmation and number stability

```
After producing the summary: "[N] modules, [N] exceptions. Confirm, or state one change."
Adjustments apply immediately and only the MODULES table is re-shown:
  add a module      → next number at the end of its tier
  defer / remove    → status changes, number kept
  change a status   → status changes, number kept
NUMBER STABILITY: a number never shifts after first assignment — "1.1" always means
the same module. Phase 2 begins on the user's first number request.
```

---

## 3 — Phase 2: module convergence (per requested module)

### 3.1 Request protocol

```
Status EXCEPTION → no files; confirm "[n] [module] is EXCEPTION — read as-is" and offer
                   the next module.
Status EXISTING  → read the prior module registry; EXTEND it (fill gaps, never replace);
                   note "[N] gaps filled from [source]".
Status NEW       → full pattern from knowledge sources + domain-profile.
Always append the readiness block (§3.5) after the two files.
```

### 3.2 Auto-completion protocol (for every gap in the module structure)

```
STEP 1 → prior module registry (EXISTING)         → use it
STEP 2 → project-registry ownership / dependency  → use it
STEP 3 → knowledge sources (§1 STEP D)            → apply, cite
STEP 4 → domain-profile rules + domain best practice → apply, cite
Document every auto-decision:   AUTO: [decision]  FROM: [step / source]  IF WRONG: [override]
STEPS 1–4 all fail → the point is a QUESTION (§5) — resolved in dialogue with a
recommended answer; the user confirms. Never an assumption written as fact.
```

### 3.3 Module registry — template (`{{ art('module-registry') }}`)

```markdown
## MODULE REGISTRY — [Module display] ([CODE])
══════════════════════════════════════════════════════════════════
Module Code    : [CODE]   (profile.vocabulary.module_prefixes)
Bounded context: [context id]
Layer / Type   : [L1–L4] / [type]     Execution tier : [n.m]
Source         : NEW / EXTENDED from prior registry
Knowledge      : [knowledge file(s) / domain-profile §]
Readiness      : READY / PARTIALLY_READY
══════════════════════════════════════════════════════════════════

ENTITIES OWNED   (names only — entity IDs are assigned by {{ factory.ids.atoms.ENT.owner }})
| Entity{% if langs.require_all %} ({{ langs.all | join('/') }}){% endif %} | Kind ({{ vocab.entity_kinds | join(' / ') }}) | PRIVATE / SHARED | Source |

LOOKUPS OWNED    (value lists this module masters)
| Lookup key | Description | Initial values (only those the user named) | Source |
{% if conv.lookups %}Rule (profile): {{ conv.lookups }}
{% endif %}
LOOKUPS CONSUMED (from other modules)
| Lookup key | Owner code | READ-ONLY |

SHARED ENTITIES CONSUMED
| Entity | Owner code | HARD-FK / SOFT-READ | Why |

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
ROOT: YES / NO

AUTO-DECISIONS
AUTO: [decision]  FROM: [source]  IF WRONG: [override]

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
══════════════════════════════════════════════════════════════════
```

### 3.4 Business policies — template (`{{ art('business-policies') }}`)

This file carries what the domain's standards cannot know: the client's own policies,
custom values and scope exceptions. Standard domain behaviour is applied by
`{{ stage.next }}` and later stages from the knowledge sources — it is not repeated here.
If the user stated nothing specific, the file is minimal by design.

Every policy is one `{{ stage.owns_ids[0] if stage.owns_ids else 'POL' }}` record written in **EARS** form (one pattern per
statement; `factory.ids.ears.patterns`):

```
{% for name, rx in ears.items() %}  {{ '%-11s' | format(name) }} {{ rx | replace('^', '') | replace('.+', '<condition>') }}…
{% endfor %}```

```markdown
## BUSINESS POLICIES — [Module display] ([CODE])
══════════════════════════════════════════════════════════════════
Module   : [CODE]     Source of truth : user vision text + dialogue resolutions
Read by  : {{ stage.next }} (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)
{{ stage.owns_ids[0] if stage.owns_ids else 'POL' }}-[CODE]-001 — [short name]
  Statement : [EARS — exactly one pattern; the subject is "the system"]
  Pattern   : [{{ ears.keys() | join(' | ') }}]
  Trigger   : [Create / Update / Submit / Approve / …]
  Rationale : [why the client wants it — one line]
  Source    : [vision text quote / dialogue resolution #]
  Status    : CONFIRMED
(If none: "None — standard domain rules apply.")

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
| Lookup key | Added values | Source |
(If none: "None — standard values apply.")

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
(If none: "None — standard scope applies.")

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
══════════════════════════════════════════════════════════════════
```

Policy rules: a policy is a NEED at platform level, not a validation rule — no field
names, no error messages, no API shapes. Sequence numbers are continuous per module
and never reused. A policy the user did not state and did not confirm is not written.

### 3.5 Readiness block (after every module)

```
✓ [Module] — {{ stage.id }} complete
  Next : {{ stage.next }} reads {% for a in stage.produces %}{{ a.file }}{% if not loop.last %} · {% endif %}{% endfor %}
  Precondition for {{ stage.next }}: HARD dependencies [codes] present in the registry
  Another module? [next by tier order]
```

---

## 4 — Registry step content

`{{ art('module-registry') }}` IS this stage's registry output. In addition the
orchestrator merges into `project-registry.md`:

```
module index          : status of the module (NEW → IN PROGRESS), tier, layer, type
entity ownership      : ENTITIES OWNED rows (CANDIDATE → REGISTERED, still no ID)
shared declarations   : SHARED rows
dependency index      : DEPENDENCIES rows (candidates for {{ factory.ids.atoms.XM.owner }})
open-question index   : rows RESOLVED by this stage's dialogue (+ resolution)
pipeline status       : {{ stage.id }} = DONE for the module
event history         : "{{ stage.id }} completed: [module list]"
```

---

## 5 — Questions (allowed here) — how they are asked and closed

```
A QUESTION exists only when §1 A–D and §3.2 STEPS 1–4 leave a point unresolved.

QUESTION — [point]
  Affects       : [module / entity / dependency / scope]
  Options       : A) … (trade-off)   B) … (trade-off)
  Researched    : [what the knowledge sources / domain-profile say — cited]
  Recommended   : [option] — because [rationale]
```
{% if lane and lane.dialogue %}
Lane `{{ stage.lane }}`: the implementers ({{ lane.implementers | join(', ') }}) converge on each QUESTION —
challenge, answer, ≤ {{ lane.dialogue.max_rounds }} rounds, until **{{ lane.dialogue.converge_on }}**. The converged
block is presented to the user as the recommended answer; the user confirms or adjusts.
{% else %}
The lane's implementers converge on each QUESTION (`factory.lanes[stage.lane].dialogue`);
the converged recommendation is presented to the user, who confirms or adjusts.
{% endif %}
```
Resolution is recorded in the RESOLVED DECISIONS table of the artifact it affects.
No external open-questions file. A point the user leaves undecided stays under
OPEN ITEMS of the platform summary and is carried to {{ stage.next }} (the last stage that may ask).
Never ask about: anything in the domain-profile, the registry, a prior module registry,
or the knowledge sources.
```

---

## 6 — Continuation

```
Resume with: platform summary + the module artifacts of completed modules (from
{{ factory.paths.module.state_dir }}/ or the version folder) + registry pipeline status.
Announce: "Resuming {{ stage.id }}. Completed: [list]. Pending: [NEW/EXISTING from the summary]."
No re-analysis of completed modules. Always re-emit the platform summary before
ending if in-session adjustments were made.
```

---

## 7 — Boundaries and enforcement

```
OWNS      : {% for a in stage.produces %}{{ a.file }}{% if not loop.last %} · {% endif %}{% endfor %} · {{ stage.owns_ids | join(', ') }} IDs · tier and build-order
            assignment · entity / lookup candidate discovery and ownership · dependency map
DOES NOT  : any ID of {% for atom, spec in factory.ids.atoms.items() if spec.owner != stage.id and spec.owner not in ['any', 'versioning'] %}{{ atom }} ({{ spec.owner }}){% if not loop.last %}, {% endif %}{% endfor %} ·
            requirements · screens · field lists · validation rules · DDL · execution phases

VIOLATION (this stage's output contains any of these):
  screens with field lists · validation logic · requirement statements other than
  {{ stage.owns_ids[0] if stage.owns_ids else 'POL' }} policies · any ID owned by another stage · permission tables · test scenarios

RUNTIME REDIRECT — when the user asks for requirements / screens / rules / fields:
  1. Complete this stage's artifacts for the module (they ARE the correct answer).
  2. Redirect once: "Requirements begin in {{ stage.next }} and later stages; these files are
     their input."
  3. Offer the next valid action (another module number, or proceed).
```

---

## 8 — Self-check before emitting

- [ ] Every module in the summary has a code from the profile (or RESERVED in the registry), a tier, a status.
- [ ] Every entity owned has a kind from `{{ vocab.entity_kinds | join(', ') }}` and a source; no entity ID.
- [ ] Every policy is exactly one EARS pattern, has a Source, a Trigger, a continuous sequence number.
- [ ] Every auto-decision carries AUTO / FROM / IF WRONG; every default cites a knowledge source.
- [ ] Every QUESTION raised appears in a RESOLVED DECISIONS table (or under OPEN ITEMS with the user's explicit deferral).
- [ ] No requirement, screen, field, rule, permission or later-stage ID anywhere.
- [ ] Vocabulary matches the domain-profile STEERING block verbatim.
{% if langs.require_all %}- [ ] Names and statements carry all of `{{ langs.all | join(', ') }}`.
{% endif %}