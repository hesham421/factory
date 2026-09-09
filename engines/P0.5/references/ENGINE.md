{#- rendered at brief-build time: profile, factory, stage, mod, version -#}
{%- set lane = factory.lanes.get(stage.lane) if stage.lane is defined else none -%}
{%- set langs = profile.languages -%}
{%- set kb = (profile.knowledge or {}).files -%}
{%- set idp = factory.ids.pattern -%}
{%- set us = stage.owns_ids[0] if stage.owns_ids else 'US' -%}
{%- set us_traces = factory.ids.atoms[us].traces_to if us in factory.ids.atoms else [] -%}
{%- macro art(name) %}{% for a in stage.produces if a.artifact == name %}{{ a.file }}{% endfor %}{% endmacro -%}
# {{ stage.title }} — ENGINE

```
Engine        : {{ stage.title }}
Stage id      : {{ stage.id }}
Pass          : {{ stage.pass_ if stage.pass_ is defined else stage['pass'] }}
Questions     : {{ stage.questions }} — the LAST stage that may ask; resolved in-dialogue, user confirms
Dialogue      : {{ 'yes — lane ' ~ stage.lane if stage.dialogue else 'no' }}{% if lane and lane.dialogue %} ({{ lane.implementers | join(' + ') }}; ≤ {{ lane.dialogue.max_rounds }} rounds; converge on "{{ lane.dialogue.converge_on }}"; output: {{ lane.dialogue.output }}){% endif %}
Inputs        : {{ stage.inputs | join(', ') }}
Produces      : {% for a in stage.produces %}{{ a.file }}{% if not loop.last %} · {% endif %}{% endfor %}
Owns IDs      : {{ stage.owns_ids | join(', ') }}   → `{{ idp }}` (seq width {{ factory.ids.seq_width }}); each traces to {{ us_traces | join(', ') }}
Gate after    : {% for g in factory.gates if g.after == stage.id %}{{ g.id }} ({{ g.type }}) — blocks {{ g.blocks | join(', ') }}{% endfor %}
Next          : {{ stage.next }}
Module        : {{ mod }}   Version: {{ version }}
Profile       : {{ profile.identity.id }} — {{ profile.identity.display }}
```

This engine restates what the previous stage established about a module — its scope,
its policies, its priorities — as a set of clear, traceable **user stories**. A user
story is a NEED, never a RULE. If a story reads like an enforceable rule ("the system
shall reject any submission where X"), soften it back to intent ("the requester needs
to know the submission will not go through if X") and let `{{ stage.next }}` decide the rule.

Completion (write → registry → analyze → commit → gate) is owned by the orchestrator —
see `shared/GOVERNANCE-CORE.md`. {% if version is defined and version and version > 1 %}**Delta mode is active (v{{ version }})**{% else %}In a delta version (version > 1){% endif %}: read
`{{ factory.paths.module.state_dir }}/{{ factory.naming.current_state_file }}` of the previous version for every input and for this
stage's own artifact, and emit only ADDED / MODIFIED / REMOVED stories plus the
`{{ factory.paths.module.change_manifest }}` per `shared/VERSIONING.md`.

Language policy: narrative in `{{ langs.primary }}`{% if langs.require_all %}; story titles carry all of `{{ langs.all | join(', ') }}`{% endif %}.

---

## 1 — Inputs and entry check

```
{% for i in stage.inputs %}  {{ i }}{{ ' ' * (18 - i|length) }}: ✓ present / ✗ MISSING
{% endfor %}  Module             : {{ mod }}
```
A missing input is a pipeline error (the orchestrator does not start this stage
without it) — not a question for the user. The domain-profile STEERING block and the
project-registry are read for vocabulary and ownership; the knowledge sources are read
for recommended answers (§4).

---

## 2 — User story record (`{{ us }}` — mandatory format)

```
{{ us }}-[MOD]-[SEQ]
  Title          : [short name{% if langs.require_all %} — in each of {{ langs.all | join('/') }}{% endif %}]
  Story          : As a [role], I need [capability], so that [outcome]   — a NEED
  Priority       : HIGH / MEDIUM / LOW — only if stated or clearly implied; otherwise "—"
  Success metric : only if stated; otherwise "—"
  Traces         : {{ us_traces | join(', ') }}-[MOD]-[SEQ] [, …]   — the policies this story serves
  Source         : [document § / quote]   — MANDATORY, no exceptions
  Status         : DRAFT → APPROVED (by the PRD approval gate)
```

```
MANDATORY SOURCING RULE
  A story with no Source is a contract violation. Do not write one "to be thorough":
  an untraceable story looks governed when it is not.
TRACES RULE
  A story that serves no policy carries "Traces: — (scope only)" and cites the
  platform summary or module registry line that motivates it. `gov.py analyze`
  reports dangling {{ us_traces | join('/') }} references.
SEQUENCE RULE
  Continuous per module, never reused; a re-run continues from the highest existing
  sequence; an APPROVED story is never edited in place — amend via a new story.
```

---

## 3 — Extraction rules

```
FROM the business policies
  every policy → at least one story that expresses the NEED behind it (Traces: that policy)
  stated priorities and success criteria → Priority / Success metric
FROM the module registry
  each entity owned → "the [role] needs to manage [entity]" is a legitimate seed
  lookups owned / consumed, dependencies → integration needs — only when explicit
FROM the platform summary
  tier / dependency classification → cross-module needs — only if stated, never inferred
FROM the domain-profile
  scope statements → what NOT to write; vocabulary → use verbatim

DO NOT EXTRACT
  validation rules, data constraints, API shapes, permission matrices — those are
  {{ stage.next }} outputs. If a policy already states a mechanism, restate it at NEED level.
  Stories for entities or capabilities the inputs never mention.
```

---

## 4 — Questions (allowed — for the last time in the pipeline)

```
A QUESTION exists only when the inputs leave a story's scope, priority or role
genuinely ambiguous. It is never a request for a rule or a mechanism.

QUESTION — [point]
  Affects       : {{ us }} candidates [list] / scope
  Options       : A) … (trade-off)   B) … (trade-off)
  Researched    : [what the knowledge sources say — cited{% if kb %}: {{ kb | join(', ') }}{% endif %}]
  Recommended   : [option] — because [rationale]
```
{% if lane and lane.dialogue %}
Lane `{{ stage.lane }}`: the implementers ({{ lane.implementers | join(', ') }}) converge on each QUESTION —
challenge, answer, ≤ {{ lane.dialogue.max_rounds }} rounds, until **{{ lane.dialogue.converge_on }}** — and the converged
recommendation is presented to the user, who confirms or adjusts.
{% else %}
The lane's implementers converge on each QUESTION (`factory.lanes[stage.lane].dialogue`)
and the converged recommendation is presented to the user, who confirms or adjusts.
{% endif %}
```
Resolutions are recorded in the RESOLVED DECISIONS table of the PRD. No external
open-questions file. Because no later stage may ask, every question MUST be closed
before the approval gate: an item the user will not decide is written as a story
with Status DEFERRED and an explicit "out of scope for v{{ version }}" note — never left open.
```

---

## 5 — Extraction report (emitted before the PRD)

```
══════════════════════════════════════════════════════════════════
PRD EXTRACTION REPORT — {{ mod }} — [date]
══════════════════════════════════════════════════════════════════
STORIES DRAFTED
  + {{ us }}-{{ mod }}-001 — [one line] — Traces: [ids] — Source: [ref]
STORIES SKIPPED (no traceable source)
  — [what was considered and why it was not written]
QUESTIONS RAISED → RESOLVED IN DIALOGUE
  ? [point] → [resolution] (confirmed by user: yes/no)
POLICIES WITHOUT A STORY (must be empty)
  — [policy id] — [why]
══════════════════════════════════════════════════════════════════
```
The report precedes the file in the run output; its counts become the registry
event row (§7).

---

## 6 — Output template — `{{ art('prd') }}`

```markdown
# PRD — [Module display] ({{ mod }})
══════════════════════════════════════════════════════════════════
Module          : {{ mod }}     Version : v{{ version }}
Source artifacts: {{ stage.inputs | join(', ') }}
Stories         : [N]   Policies covered : [N]/[N]   Deferred : [N]
Status          : DRAFT — awaiting {% for g in factory.gates if g.after == stage.id %}{{ g.id }}{% endfor %}
══════════════════════════════════════════════════════════════════

## USER STORIES
{{ us }}-{{ mod }}-001
  Title / Story / Priority / Success metric / Traces / Source / Status   (record §2)
(repeat per story, in sequence order)

## TRACEABILITY — story → policy
| {{ us }} | Traces ({{ us_traces | join('/') }}) | Source |
|---|---|---|
(every policy of the module appears in at least one row; a policy with no story is a
 completeness finding)

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |

## DEFERRED
| {{ us }} | Reason | Activation trigger |

## APPROVAL
Approved by : [user]   Date : [date]
Once approved, no stage may raise a question; {{ stage.next }} onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════
```

---

## 7 — Registry step content

```
project-registry : module row → "PRD v{{ version }}: [N] stories"; open-question rows resolved
                   by this dialogue → RESOLVED (+ resolution); pipeline status {{ stage.id }} = DONE
event history    : "{{ stage.id }} completed: {{ mod }} v{{ version }} — [N] stories, [N] decisions"
```
(There is no separate registry artifact for this stage; the story index lives in the
PRD's traceability table.)

---

## 8 — Never produce

```
✗ any ID owned by another stage ({% for atom, spec in factory.ids.atoms.items() if spec.owner != stage.id and spec.owner not in ['any', 'versioning'] %}{{ atom }}{% if not loop.last %}, {% endif %}{% endfor %})
✗ enforceable validation logic, field-level constraints, API shapes, permissions
✗ a story with no Source, or a story invented to "fill out" the PRD
✗ an open question left unresolved at the gate
✗ padding — produce the PRD as fast as the sourcing discipline allows; the gate is
  about the file's existence and approval, not its volume
```

---

## 9 — PRD approval gate

```
{% for g in factory.gates if g.after == stage.id %}Gate `{{ g.id }}` (type {{ g.type }}) follows this stage and blocks {{ g.blocks | join(', ') }}.
{% endfor %}The user approves THIS FILE. After the user approves it:
  - no stage may raise a question — {{ stage.next }} and every later stage resolve
    ambiguity themselves: non-breaking → ADR + continue; breaking → ADR BLOCKED + stop
    (`factory.yaml → ambiguity`, shared/GOVERNANCE-CORE.md);
  - the approved stories are frozen for v{{ version }}; a change is a new story in a
    new version (shared/VERSIONING.md).
```

---

## 10 — Self-check before emitting

- [ ] Every story has Title, Story (As a / I need / So that), Traces, Source, Status.
- [ ] Every policy of the module is traced by at least one story; the traceability table is complete.
- [ ] No story states a mechanism (rule, constraint, API, permission).
- [ ] Every question raised is in RESOLVED DECISIONS or DEFERRED with the user's explicit decision.
- [ ] Sequence numbers continuous; no APPROVED story edited in place.
- [ ] Vocabulary matches the domain-profile STEERING block verbatim.
{% if langs.require_all %}- [ ] Titles carry all of `{{ langs.all | join(', ') }}`.
{% endif %}