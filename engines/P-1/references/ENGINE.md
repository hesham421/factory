{#- rendered at brief-build time: profile, factory, stage, mod, version -#}
{%- set langs = profile.languages -%}
{%- set vocab = profile.vocabulary -%}
{%- set kb = (profile.knowledge or {}).files -%}
# {{ stage.title }} — ENGINE

```
Engine        : {{ stage.title }}
Stage id      : {{ stage.id }}
Pass          : {{ stage.pass_ if stage.pass_ is defined else stage['pass'] }}   (once per {{ stage.once_per }})
Questions     : {{ stage.questions }}
Lane          : {{ stage.lane }}
Inputs        : {{ stage.inputs | join(', ') }}
Produces      : {% for a in stage.produces %}{{ a.dir ~ '/' if a.dir else '' }}{{ a.file }}{% if not loop.last %} · {% endif %}{% endfor %}   (ONLY this file)
Owns IDs      : {{ stage.owns_ids | join(', ') or '— (registers candidates; assigns no pipeline ID)' }}
Next          : {{ stage.next }}
Profile       : {{ profile.identity.id }} — {{ profile.identity.display }}
```

This engine bootstraps the platform registry from the saved `domain-profile.md`. It is
the first consumer of that file and the **creator** of `project-registry.md`; nothing
that runs before it may require a registry, and it asks no questions — every fact it
writes is extracted from its inputs and cited. The registry's categories are defined
in `shared/REGISTRY-SCHEMA.md` (Part A, domain-neutral); this engine fills them and
adds the **steering enforcement notes** that bind every later stage to the
domain-profile's vocabulary.

Completion (write → registry → analyze → commit) is owned by the orchestrator — see
`shared/GOVERNANCE-CORE.md`.

---

## 1 — Purpose and operating model

```
DOES
  - Reads domain/domain-profile.md completely (STEERING block first), then any
    platform brief supplied as input.
  - Reads an existing project-registry.md as the baseline when re-run (extend mode).
  - Extracts every governance-relevant fact into the registry categories (§3).
  - Copies the STEERING block into the registry's conventions section VERBATIM and
    writes the enforcement notes (§3.6).
  - Preserves every existing entry — never removes previously registered content.
  - Emits the complete registry file — never a diff.

DOES NOT
  - Invent information not present in the inputs, or pre-register modules/entities
    that are only mentioned in passing.
  - Assign any pipeline ID ({{ factory.ids.atoms.keys() | join(', ') }}) — IDs are assigned by their
    owning stages (`factory.ids.atoms.*.owner`). This engine registers CANDIDATES.
  - Generate implementation content (tables, columns, endpoints, screens).
  - Ask the user. A fact the inputs do not settle becomes an OPEN row in the
    open-question index (§3.5) with its evidence; the next stage that allows
    questions ({{ stage.next }}) resolves it in dialogue.
  - Decide on its own. Where a choice is unavoidable (e.g. two plausible owners for
    one candidate), it records BOTH as candidates with Status OPEN — it does not pick.
```

Language policy: narrative in `{{ langs.primary }}`{% if langs.require_all %}; names and terms carry all of `{{ langs.all | join(', ') }}`{% endif %}.

---

## 2 — Reading protocol

```
STEP A — domain-profile.md (mandatory; its absence is a pipeline error, not a question)
  §7 STEERING   → vocabulary, bounded contexts, module prefixes, identifier rules,
                  knowledge sources — copied verbatim (§3.6)
  §4 COMPONENTS → module index candidates (§3.1)
  §5 RULES      → platform-wide governance decisions (§3.4)
  §6 RELATIONS  → cross-module dependency candidates (§3.3)
  §8 DECISIONS  → confirmed decisions (§3.4) — only rows the user confirmed
  §10 OPEN      → open-question rows (§3.5)

STEP B — platform brief (optional input) → same extraction, every row cites it.

STEP C — existing project-registry.md (re-run only) → baseline; extend, never rewrite
  history; bump the registry version (§4 RULE-2).

STEP D — profile facts that the registry must echo (read-only, cited as "profile"):
  module codes    : {{ vocab.module_prefixes.keys() | join(', ') }}
  entity kinds    : {{ vocab.entity_kinds | join(', ') }}
{% if vocab.bounded_contexts %}  bounded contexts: {% for c in vocab.bounded_contexts %}{{ c.id }} [{{ c.owns | join(', ') }}]{% if not loop.last %}; {% endif %}{% endfor %}
{% endif %}{% if kb %}  knowledge files : {{ kb | join(', ') }}
{% endif %}```

A module code that appears in the domain-profile as PROPOSED but is not in
`profile.vocabulary.module_prefixes` is registered with Status RESERVED and a note
"awaiting profile update" — the profile is the authority on codes.

---

## 3 — Extraction rules (what goes where)

Category labels below are the ones in `shared/REGISTRY-SCHEMA.md`; the registry's own
section names map to them in its Schema Compliance Map (§5).

### 3.1 Domains and modules → module / component index
```
Look for : named business areas, functions, systems; any grouping of processes or
           data; any explicit system boundary (domain-profile §4 rows first).
Write    : one row per component the domain-profile names — module code, display
           name, bounded context, category, core/extension, Status.
Rules    : a module enters the index only when it is described as a scope boundary,
           not merely mentioned; never reuse a code already held by another row.
```

### 3.2 Entities → entity ownership + shared-entity declarations
```
Look for : named business objects; data that is created, stored, retrieved, managed;
           objects with described attributes or relations; objects referenced by
           more than one component.
Write    : CANDIDATE rows (§6 format) — name, owner module, kind (one of
           {{ vocab.entity_kinds | join(' / ') }}), PRIVATE / SHARED?, source.
Rules    : no entity ID here; unclear owner → Status OPEN + open-question row;
           referenced by several components → SHARED candidate in the shared
           declarations category.
```

### 3.3 Cross-module dependencies → dependency index
```
Look for : "needs data from", "depends on", "requires", shared data between
           components, integration points (domain-profile §6 first).
Write    : XM candidate rows (§6 format) — from module, to module, kind
           (HARD-FK? / SOFT-READ? / EVENT?), what is consumed, evidence, Status
           CANDIDATE. Formal XM IDs are assigned by {{ factory.ids.atoms.XM.owner }}
           (see shared/XM-PROTOCOL.md).
```

### 3.4 Governance decisions → decisions log
```
Look for : confirmed technology, naming or structural choices; system-wide business
           rules; constraints from existing infrastructure (domain-profile §5, §8).
Write    : decision text + rationale + source. Only CONFIRMED decisions — never
           options still under discussion.
Rules    : a decision this engine had to make itself is not a registry row — it is
           an ADR (`{{ factory.paths.decisions }}/{{ factory.naming.adr_file }}`, see shared/GOVERNANCE-CORE.md)
           referenced from the registry.
```

### 3.5 Open items → open-question / escalation index
```
Look for : unresolved ownership; ambiguous boundaries; conflicting statements;
           an entity or process without a clear owner; a dependency the inputs
           cannot resolve (domain-profile §10).
Write    : question, evidence (both sides of a conflict), affected rows, Status OPEN,
           "to be resolved by {{ stage.next }} dialogue".
Rules    : this engine RECORDS open items; it never resolves them by guess and never
           asks the user.
```

### 3.6 Steering → conventions section + enforcement notes
```
Copy verbatim from domain-profile §7:
  ubiquitous language table · bounded contexts · module prefixes · identifier rules
  · knowledge sources to cite
Then write the ENFORCEMENT NOTES:
  E1  Every later artifact uses these terms verbatim; a synonym listed under
      "do not say" is a consistency finding at the pass gate (`gov.py analyze`
      checks registry ↔ artifact agreement).
  E2  IDs follow `{{ factory.ids.pattern }}` (seq width {{ factory.ids.seq_width }}) with the module codes of
      this section only.
  E3  Entities are classified with the kinds `{{ vocab.entity_kinds | join(', ') }}`.
  E4  Sources to cite when a stage resolves an ambiguity: the knowledge sources
      listed here, then the domain-profile itself.
  E5  Pipeline status per module (category "pipeline / progress status") is
      maintained by the orchestrator from commits — this engine seeds the rows
      as NOT STARTED.
```

---

## 4 — Registry update rules

```
RULE-1  Always emit the complete project-registry.md, top to bottom.
RULE-2  Version the registry (semantic):
          rows / candidates added          → patch   1.0.0 → 1.0.1
          new module or domain registered  → minor   1.0.1 → 1.1.0
          registry structure changed       → major   1.1.0 → 2.0.0
RULE-3  Never remove an existing entry; corrections add a NOTE or a correction row
        that references the original.
RULE-4  Status vocabulary for analysis-phase rows:
          CANDIDATE  identified, not yet in the pipeline
          RESERVED   code or name reserved, module not started
          OPEN       question not yet resolved
RULE-5  Never assign pipeline IDs (see §1).
RULE-6  Append one event-history row per run:
          [date] | BOOTSTRAP | — | — | [what was extracted, N rows per category]
RULE-7  Resolve an OPEN row only when the inputs contain the evidence; cite it.
RULE-8  Every row cites its source (domain-profile section, brief section, profile).
```

---

## 5 — `{% for a in stage.produces %}{{ a.file }}{% endfor %}` — structure

One section per category of `shared/REGISTRY-SCHEMA.md` Part A, in that order, plus a
Schema Compliance Map. Section names may be the platform's own; the map binds them.

```markdown
# PROJECT REGISTRY — [Platform name]
══════════════════════════════════════════════════════════════════
Profile            : {{ profile.identity.id }}
Registry Version   : [semver]
Domain Profile     : domain/domain-profile.md v[N]
Last Updated       : [date] by {{ stage.id }}
Modules registered : [N]   Entity candidates : [N]   Open items : [N]
══════════════════════════════════════════════════════════════════

## SCHEMA COMPLIANCE MAP
| Section of this registry | Category (shared/REGISTRY-SCHEMA.md) |
|---|---|
| [section name] | [category] |
(every category appears at least once; a category with no content says "none yet")

## [Identity & versioning]          ← header above + version history table
## [Conventions & steering]         ← §3.6 verbatim copy + ENFORCEMENT NOTES E1–E5
## [Module / component index]       ← §3.1 rows
## [Entity ownership]               ← §3.2 CANDIDATE rows (format §6)
## [Shared entity declarations]     ← §3.2 SHARED candidates
## [Structural / implementation registry] ← "none yet — filled by {{ factory.ids.atoms.DBF.owner }} / {{ factory.ids.atoms.API.owner }}"
## [Cross-module dependency index]  ← §3.3 XM candidates (format §6)
## [Open question index]            ← §3.5 rows
## [Pipeline / progress status]     ← one row per module, NOT STARTED
## [Change / event history]         ← RULE-6 rows
```

---

## 6 — Candidate row formats

```
ENTITY OWNERSHIP — analysis-phase format
| Candidate ref     | Entity name | Owner module | Kind | PRIVATE/SHARED | Status    | Source |
| CAND-[MOD]-001    | [name]      | [MOD]        | [kind] | PRIVATE      | CANDIDATE | [ref]  |
| CAND-[MOD]-002    | [name]      | UNCLEAR      | [kind] | SHARED?      | OPEN      | [ref]  |

XM DEPENDENCY — analysis-phase format
| Candidate ref     | Kind       | From module | To module | Consumes | Status    | Evidence |
| XM-CAND-001       | HARD-FK?   | [MOD]       | [MOD]     | [what]   | CANDIDATE | [ref]    |
```
`CAND-*` / `XM-CAND-*` refs are registry-local handles, not pipeline IDs; they are
replaced by formal IDs when the owning stage registers the element.

---

## 7 — Extraction report (emitted before the registry, kept in the run output)

```
══════════════════════════════════════════════════════════════════
EXTRACTION REPORT — {{ stage.id }} — [date] — profile {{ profile.identity.id }}
Input : domain/domain-profile.md v[N] [+ brief]
══════════════════════════════════════════════════════════════════
MODULES IDENTIFIED     : + [code] [name] — context [id] — [Status]   (none —)
ENTITY CANDIDATES      : + [name] — owner [MOD] — [kind] — PRIVATE/SHARED?   (none —)
XM CANDIDATES          : + [MOD] → [MOD] for [what]                  (none —)
DECISIONS CONFIRMED    : + [text] — source [ref]                     (none —)
OPEN ITEMS RECORDED    : + [question] — evidence [ref]               (none —)
STEERING COPIED        : [N] terms · [N] contexts · [N] codes ([N] RESERVED)
SECTIONS UPDATED       : [list]        NOTHING EXTRACTED FOR: [list]
══════════════════════════════════════════════════════════════════
```
The report is informational; the run continues (no confirmation prompt — questions
are forbidden in this stage). Its counts become the RULE-6 event row.

---

## 8 — Quality rules

```
Q1  Extract conservatively — an OPEN row beats a silent inclusion or exclusion.
Q2  Cite the source of every row.
Q3  Distinguish confirmed / inferred / candidate; inferred content is never
    written as confirmed.
Q4  Flag conflicts — never overwrite silently; record both sides as OPEN.
Q5  Ownership first — unclear ownership is an OPEN row immediately.
Q6  No premature finalisation — analysis-phase rows stay CANDIDATE until a stage
    formally registers them.
Q7  No cross-platform bleed — everything goes into THIS platform's registry.
```

---

## 9 — Self-check before emitting

- [ ] Every category of `shared/REGISTRY-SCHEMA.md` appears in the Schema Compliance Map.
- [ ] STEERING copied verbatim; ENFORCEMENT NOTES E1–E5 present.
- [ ] Every module row has a code that is in the profile or RESERVED.
- [ ] No pipeline ID assigned anywhere; candidates use `CAND-*` / `XM-CAND-*` handles.
- [ ] Every row has a Source; every OPEN row has evidence.
- [ ] Existing rows (re-run) all preserved; version bumped per RULE-2; event row added.
- [ ] The report's counts equal the registry's counts.
