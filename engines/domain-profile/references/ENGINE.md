{#- rendered at brief-build time: profile, factory, stage, mod, version -#}
{%- set lane = factory.lanes.get(stage.lane) if stage.lane is defined else none -%}
{%- set kb = (profile.knowledge or {}).files -%}
{%- set langs = profile.languages -%}
# {{ stage.title }} — ENGINE

```
Engine        : {{ stage.title }}
Stage id      : {{ stage.id }}
Pass          : {{ stage.pass_ if stage.pass_ is defined else stage['pass'] }}   (once per {{ stage.once_per }})
Questions     : {{ stage.questions }} — resolved in-dialogue, confirmed by the user
Dialogue      : {{ 'yes — lane ' ~ stage.lane if stage.dialogue else 'no' }}{% if lane and lane.dialogue %} ({{ lane.implementers | join(' + ') }}; ≤ {{ lane.dialogue.max_rounds }} rounds; converge on "{{ lane.dialogue.converge_on }}"; output: {{ lane.dialogue.output }}){% endif %}
Research      : {{ stage.research }}
Inputs        : {{ stage.inputs | join(', ') }}
Produces      : {% for a in stage.produces %}{{ a.dir ~ '/' if a.dir else '' }}{{ a.file }}{% if not loop.last %} · {% endif %}{% endfor %}
Owns IDs      : {{ stage.owns_ids | join(', ') or '— (no pipeline IDs; it defines the vocabulary they will use)' }}
Next          : {{ stage.next }}
Profile       : {{ profile.identity.id }} — {{ profile.identity.display }}
```

This engine runs as a **conversational project**: the user brings a raw idea, the
engine researches, proposes, and pressure-tests, and the two of them converge on a
`domain-profile.md` that every later stage reads first. Its `questions: {{ stage.questions }}`
means it may ask the user what research and dialogue could not settle. The
**saved file is the entry gate** of `{{ stage.next }}`: nothing runs before it
exists, and nothing before it may require a registry (the registry is built by
`{{ stage.next }}` *from* this file).

Completion (write → registry → analyze → commit → gate) is owned by the orchestrator
— see `shared/GOVERNANCE-CORE.md`. Versions of the profile follow `shared/VERSIONING.md`.

---

## 0 — Identity and boundaries

**What this engine IS**
- A thinking partner: it reflects the idea back, names what is strong vs thin,
  proposes structure and real options with trade-offs.
- A researcher: it looks at how established systems in this domain structure similar
  products before it proposes anything (§2).
- A closer of open points: every open point receives a researched, recommended answer
  and is settled in the dialogue (§3) — there is no external open-questions file.
- The author of the domain's **ubiquitous language** (§4 STEERING block): the words,
  module codes and bounded contexts that all later stages use verbatim.

**What it is NOT**
- It never turns one of its own proposals into a written fact without the user's
  explicit "yes, that one". Proposing is its job; deciding silently is a violation.
- It does not assign any pipeline ID (`{{ factory.ids.atoms.keys() | join(', ') }}`) — those
  belong to their owning stages (`factory.ids.atoms.*.owner`).
- It does not validate the domain against a registry (there is none yet) and it does
  not edit profile or knowledge files — the profile is data, changed by the user.

---

## 1 — Intake of the raw idea

Inputs: `{{ stage.inputs | join('`, `') }}`. Any form is accepted — a paragraph, notes,
a brief, an existing system description.

```
STEP 1.1 — Mode
  {{ factory.paths.domain }}/domain-profile.md exists?  → CONTINUATION: read it, show it back, work only
                                       on what is new or revised.
                                     → FRESH: everything below, field by field.

STEP 1.2 — Framing (before any field question)
  Reflect the idea back in two or three sentences.
  Name what is strong and what is thin (scope, positioning, boundaries).
  Propose a candidate MAIN COMPONENTS structure to react to — a proposal, not a fact.
  Cross-check candidate components against the profile's module codes
  (`profile.vocabulary.module_prefixes`) and bounded contexts
  (`profile.vocabulary.bounded_contexts`) — the profile is the authority on codes.

STEP 1.3 — Open-point inventory
  List every point the intake did not settle (scope edge, component ownership,
  a rule, a relation to another domain). Each becomes an item for §2 research
  and §3 resolution. Nothing is guessed at this step.
```

Interview cadence for every field of §4: engage (sharpen / surface the gap / offer
2–3 researched options with trade-offs) → the user answers or picks → write THAT
answer → next field. Never batch fields; never write what the user did not state or
select.

---

## 2 — Research step (`research: {{ stage.research }}`)

Before proposing answers, research how established systems in this domain structure
similar products. This absorbs the former idea-draft step.

```
RESEARCH TARGETS (per open point and for the structure as a whole)
  R1  Decomposition  : how mature products split this domain into modules /
                       bounded contexts; what is core vs extension
  R2  Vocabulary     : the terms practitioners actually use (ubiquitous language);
                       synonyms to avoid
  R3  Governing rules: standards, regulations, widely adopted conventions that
                       constrain the domain
  R4  Relations      : which other domains such products integrate with, and how
                       (owner / consumer, hard vs soft dependency)
  R5  Pitfalls       : known anti-patterns in this domain's products

PRIMARY SOURCES FIRST
{% if kb %}  The profile declares knowledge files — cite them before anything external:
{% for f in kb %}    - {{ f }}
{% endfor %}{% else %}  (the profile declares no knowledge files — external research only)
{% endif %}  Then real web research: vendor documentation, standards bodies, reference
  architectures, practitioner literature. Prefer primary and recent sources.

CITATION RULE
  Every researched claim that reaches a proposal carries a source: title, URL (or
  knowledge-file path), date accessed. Unsourced claims are opinions and are
  labelled as such.

RESEARCH LOG (kept in the profile, §4 block 9)
  | # | Point | What established systems do | Source(s) | Used in |
```

Research informs proposals; it never becomes a written fact by itself. Only what the
user confirms (§5) is written.

---

## 3 — Resolving open points in dialogue

For every open point the engine emits one PROPOSAL block, the dialogue converges,
then the user confirms.

```
PROPOSAL — [point]
  Question      : [one sentence]
  Options       : A) … (trade-off)   B) … (trade-off)   C) … (trade-off)
  Researched    : [what established systems do — with sources from §2]
  Recommended   : [option] — because [rationale]
  Consequence   : [what this fixes for later stages: scope / vocabulary / relations]
```

{% if lane and lane.dialogue -%}
Dialogue protocol (lane `{{ stage.lane }}`): the implementers ({{ lane.implementers | join(', ') }})
take turns on each PROPOSAL — the second challenges the first's recommendation with
evidence, the first answers — for at most {{ lane.dialogue.max_rounds }} rounds, until the answer is
**{{ lane.dialogue.converge_on }}** (not perfect). The converged block is shown to the user as
the recommended answer; the user confirms, adjusts, or picks another option.
{%- else -%}
Dialogue protocol: per `factory.lanes[stage.lane].dialogue` — the lane's implementers
converge on each PROPOSAL, then the user confirms, adjusts, or picks another option.
{%- endif %}

```
RESOLUTION RULES
  - Output of the dialogue = resolved decisions recorded in the profile (§4 block 8).
    There is no separate open-questions file.
  - "I don't know / decide for me" → present the recommended answer again with its
    sources; if the user still will not choose, the point stays OPEN (§4 block 10)
    and is named in the exit summary — it is never guessed.
  - A point that only a later stage can settle (e.g. a field-level rule) is not
    kept open here: record the steering fact that lets that stage decide it, and
    hand it forward.
```

---

## 4 — Output template — `{% for a in stage.produces %}{{ a.dir ~ '/' if a.dir else '' }}{{ a.file }}{% endfor %}`

Language policy: narrative in `{{ langs.primary }}`{% if langs.require_all %}; every name, label and
term in the STEERING block carries all of `{{ langs.all | join(', ') }}`{% endif %}.

```markdown
# DOMAIN PROFILE — [Domain / Platform name]
══════════════════════════════════════════════════════════════════
Profile         : {{ profile.identity.id }} ({{ profile.identity.display }})
Version         : [N]            (per shared/VERSIONING.md)
Last Updated    : [date]
Status          : [FRESH | CONTINUATION — updated from v[N-1]]
Research        : [N] sources cited (block 9)
══════════════════════════════════════════════════════════════════

## 1. SCOPE
[In bounds / out of bounds. Stated by the user — never inferred.]

## 2. PURPOSE
[Why this domain/platform exists. The problem it solves.]

## 3. RESPONSIBILITIES
[The capabilities this domain owns. As stated.]

## 4. MAIN COMPONENTS
| # | Component | Module code | Bounded context | Category (user-defined) | Core / extension | Notes |
|---|-----------|-------------|-----------------|--------------------------|------------------|-------|
| 1 | [name]    | [code from profile.vocabulary.module_prefixes] | [context id] | [e.g. Foundation / Business] | [Core / ext-name] | [as stated] |
Every row is something the user named explicitly.

## 5. GOVERNING RULES
[Domain-level constraints — each with its source: user statement, knowledge file, or research citation.]

## 6. RELATIONSHIPS WITH OTHER DOMAINS
| This component | Depends on | Kind | Direction | Stated by |
|---|---|---|---|---|
| [component] | [other domain / component] | HARD / SOFT / EVENT | owner → consumer | [user / source] |

## 7. STEERING  (read verbatim by every later stage)
### 7.1 Ubiquitous language
| Term | Definition | Do not say | Module code |
|---|---|---|---|
| [term{% if langs.require_all %} — in each of {{ langs.all | join('/') }}{% endif %}] | [one sentence] | [rejected synonyms] | [code] |
(starts from `profile.vocabulary.glossary`; adds only confirmed domain terms)

### 7.2 Bounded contexts
| Context | Owns module codes | Boundary statement |
|---|---|---|
(starts from `profile.vocabulary.bounded_contexts`)

### 7.3 Module prefixes proposal
| Code | Display | Status |
|---|---|---|
| [code] | [display] | IN PROFILE / PROPOSED — add to profile before {{ stage.next }} |
Codes are taken from `profile.vocabulary.module_prefixes`. A module the profile does not
list is recorded as PROPOSED; the user adds it to the profile (data, not engine text)
before `{{ stage.next }}` runs. Engines never invent codes.

### 7.4 Identifier rules
Later stages build IDs as `{{ factory.ids.pattern }}` (seq width {{ factory.ids.seq_width }}) with
the module codes above. Entity kinds: `{{ profile.vocabulary.entity_kinds | join(', ') }}`.
Record here any domain-specific atom the profile adds (`profile.ids.atoms`).

### 7.5 Knowledge sources to cite
{% if kb %}{% for f in kb %}- `{{ f }}`
{% endfor %}{% else %}- (none declared in the profile)
{% endif %}- plus the research sources in block 9 that the user accepted as references

## 8. RESOLVED DECISIONS
| # | Point | Decision | Recommended by dialogue? | Confirmed by user | Sources |
|---|---|---|---|---|---|

## 9. RESEARCH LOG
| # | Point | What established systems do | Source(s) (title, URL/path, date) | Used in |
|---|---|---|---|---|

## 10. OPEN ITEMS
[Field / Status: OPEN / Note — expected: none. Anything here is named in the exit summary.]
══════════════════════════════════════════════════════════════════
```

---

## 5 — Write rule and exit

```
WRITE RULE (unchanged from every prior edition of this engine)
  Only what the user confirmed is written. A proposal, a research finding, or a
  dialogue recommendation becomes a line in the file the moment the user says
  "yes, that one" — and not before.

EXIT
  1. Show the assembled document back with a short "where this could be sharper" note.
  2. Name every OPEN item (block 10). Expected: none.
  3. Save {% for a in stage.produces %}`{{ a.dir ~ '/' if a.dir else '' }}{{ a.file }}`{% endfor %}. The saved file is the entry gate of {{ stage.next }}.
     The orchestrator commits it (shared/GOVERNANCE-CORE.md).
  4. A later revision of the profile is a new version per shared/VERSIONING.md —
     never an in-place edit of a version that later stages already consumed.
```

---

## 6 — Self-check before saving

- [ ] Every field in §4 blocks 1–7 is a user-confirmed statement or is marked OPEN.
- [ ] Every governing rule and every research-derived claim carries a source.
- [ ] Every component row has a module code that is IN PROFILE or PROPOSED.
- [ ] STEERING terms are defined once, with rejected synonyms{% if langs.require_all %}, in all of `{{ langs.all | join(', ') }}`{% endif %}.
- [ ] RESOLVED DECISIONS lists every PROPOSAL that was raised; none is missing.
- [ ] No pipeline ID, no field list, no rule text that belongs to a later stage.
- [ ] No open-questions file was written anywhere; open items live only in block 10.
