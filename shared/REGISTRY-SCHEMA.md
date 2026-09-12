# REGISTRY SCHEMA — what every registry must cover

```
Doc            : shared/REGISTRY-SCHEMA.md
Role           : content-coverage model for the project registry (platform) and the stage registries (module); domain-neutral
Loaded by      : the bootstrap stage, every stage with produces[*].registry: true, gov.py analyze (clause `registry-agree`), gov.py state
Generated parts: none (which stages carry a registry is in GOVERNANCE-CORE.md RENDER:stages)
Links          : GOVERNANCE-CORE.md · XM-PROTOCOL.md · ARTIFACT-CONTRACTS.md (C2, C3.7, C5.8, C6.5, C7.4, C9.8) · VERSIONING.md
```

Two registry levels exist and nothing else counts as a registry:

| Level | File | Written by | Read by |
|---|---|---|---|
| **project registry** — platform-wide | `project-registry` at `paths.platform` (bootstrap stage's product) | the orchestrator's registry step after every stage; humans never edit it by hand | every stage, `gov.py status`, the gates |
| **stage registry** — per module version | each `produces[*].registry: true` artifact of a stage, in the module version folder | the stage that produces it | the next stages, `gov.py analyze`, `gov.py split` |

Any domain-specific section layout (a reference template, a platform-specific
grouping) lives in `profile.knowledge.files`, never here.

## 1. Project registry — the canonical categories

The registry must **cover** each category in substance. Sections may be
named, grouped, split or ordered as the domain prefers; what is fixed is that
every category is findable and a compliance map says where.

| Category | Content |
|---|---|
| **CAT-1 identity & conventions** | which platform/profile the registry governs (`profile.identity`), the registry's own version, the conventions in force (by reference to `factory.naming` / `profile.vocabulary`, never restated) |
| **CAT-2 module index** | every module (`vocabulary.module_prefixes`), its bounded context, its versions and, per version, the last committed stage |
| **CAT-3 entity ownership** | every entity (`ENT` ID), owning module, kind (`vocabulary.entity_kinds`), PRIVATE or SHARED |
| **CAT-4 shared declarations** | canonical source for each SHARED entity and each reference/lookup data set: owner, ID, consumers |
| **CAT-5 structural registry** | the structural artifacts implementing the entities (tables or their domain equivalent), by `DBF`/entity ID, per module version |
| **CAT-6 dependency indexes** | every cross-module dependency: one index for `XM` (backend, [XM-PROTOCOL.md](XM-PROTOCOL.md)) and a separate one for `UXD` (frontend); the two are never merged |
| **CAT-7 decision index** | every ADR across modules with status, and every open resolution event — the cross-module view of the decision stream ([GOVERNANCE-CORE.md §5](GOVERNANCE-CORE.md#5-ambiguity-rule)) |
| **CAT-8 pipeline status** | per module version: last committed stage, last gate verdict and scores, delivered tracks, tag — as `gov.py status` reports it |
| **CAT-9 event history** | append-only: date, stage or tool, module, version, event (IDs registered, gate verdicts, deliveries, resolution events, waivers) |
| **CAT-10 platform findings** | every finding a module-scoped stage recorded that is **not that module's to settle**: a defect in a shared artifact, a platform-wide convention, or another module's surface. One row per finding: what was found, the evidence, the module and stage that found it, the artifact or convention it belongs to, and its status (OPEN · ACCEPTED · FIXED · WAIVED + the ADR). See §4 |

**Compliance map (required).** Near the header, a table `section → category`
plus the line `Uncovered: <list | none>`. `registry-agree` with
`categories: all` (contract C2.2) reads this map; an uncovered category is a
MAJOR finding unless an ADR records why it does not apply.

**Update discipline** (executed by the orchestrator, [GOVERNANCE-CORE.md §6](GOVERNANCE-CORE.md#6-completion-protocol--executed-by-the-orchestrator-stated-once)):
1. updates are applied in stage order; a later stage's update for a version
   whose earlier stage is uncommitted is held;
2. before applying, conflicts are checked — duplicate entity name, duplicate
   structural name, duplicate ID across modules — and any conflict stops the
   stage with a CRITICAL finding;
3. an update is applied whole or not at all;
4. every applied update appends one CAT-9 row;
5. a dependency-target version change appends a resolution event (CAT-7,
   CAT-9) for every consuming module.

## 2. Stage registries

A stage registry lists **every ID the stage's artifacts define** — no more, no
less (`registry-agree` clauses). One table per atom the stage owns, with the
columns:

| Column | Content |
|---|---|
| id | the atom ID (`factory.ids.pattern`) |
| label | short name in `profile.languages.primary` (all of `languages.all` when `require_all`) |
| traces | the upstream IDs per the atom's `traces_to` |
| status | §3 |
| location | the heading or marker block in the artifact where the ID is defined |

A stage registry also carries a header naming module, version, stage and, for
a delta version, the change set (`CS`) it belongs to. It is a delta like any
other artifact: in `vN/` it lists only IDs ADDED or MODIFIED in that version;
`gov.py state` produces the merged current registry that later stages read.

## 3. Statuses

| Applies to | Values | Set by |
|---|---|---|
| entity (CAT-3) | PRIVATE · SHARED | the SRS stage; SHARED needs a CAT-4 row |
| `XM` | see [XM-PROTOCOL.md §4](XM-PROTOCOL.md#4-states-inside-the-factory) | per that protocol |
| `UXD` | OPEN · CLOSED (referenced by a frontend plan block, C9.6) | frontend stage / analyze |
| ADR | ACCEPTED · BLOCKED · SUPERSEDED | the writing stage; BLOCKED resolved only at a human decision point |
| any other atom | ACTIVE · REMOVED (by a change set of a later version) | the owning stage |
| module version (CAT-8) | last committed stage id · gate verdict (`factory.review.verdicts`) · delivered tracks · tag | `gov.py` |
| platform finding (CAT-10) | OPEN · ACCEPTED · FIXED · WAIVED | the stage that recorded it; closed only by whoever owns the fix, never by the module that found it |

No status is implied. A status that the schema does not list is a finding.

## 4. Platform findings — where a finding that belongs to no module goes

A module-scoped stage that finds a defect **outside its own module** is right to
say "not mine to settle" and wrong to stop there. Three real platform-wide
defects were found exactly that way — a response envelope that never reaches the
wire as the documented code, a shared field whose declared length exceeds the
physical column in every module, a shared exception type that cannot carry more
than one error — and every module-scoped worker correctly declined to fix them,
and nothing escalated them anywhere.

```
CAT-10 row
  finding   : what is wrong, in one sentence
  evidence  : artifact + location (a shared doc, a convention, another module's surface)
  found by  : module · stage · version
  belongs to: the artifact, convention or module that owns the fix — never this module
  status    : OPEN | ACCEPTED (ADR-…) | FIXED (where) | WAIVED (ADR-…)
```

Rules:
1. A module-scoped stage **records** a platform finding; it never fixes one.
   Fixing outside your own module is the boundary violation the "not mine"
   instinct was protecting against — recording is not.
2. A platform finding is **not** a module gap and is never written into the
   module's own findings, where the next reader takes it for one.
3. The row is appended by the orchestrator's registry step like any other
   registry update (GOVERNANCE-CORE.md §6 step 4), with its CAT-9 event.
4. Every gate reads the OPEN rows of this category (`reviewers/pass-review.md`):
   a finding nobody can see is a finding nobody will fix.
