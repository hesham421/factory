# GOVERNANCE CORE — truth layers, vocabulary, IDs, ambiguity, completion, lanes

```
Doc            : shared/GOVERNANCE-CORE.md
Role           : the shared rules every stage obeys, stated ONCE (C4); other docs link here
Loaded by      : every engine brief (core + standalone), reviewers/pass-review.md, gov.py analyze
Generated parts: RENDER:stages · RENDER:ids · RENDER:lanes (gov.py render)
Links          : CONSTITUTION.md · ARTIFACT-CONTRACTS.md · REGISTRY-SCHEMA.md · VERSIONING.md · XM-PROTOCOL.md · QUALITY-RUBRIC.md
```

## 1. Truth layers

Each artifact is both the output of its stage and an authoritative input to
every later stage. The order is the stage order in `factory.stages`; by
artifact it reads:

```
domain-profile  →  project-registry  →  prd  →  srs (+registry-srs)  →  db-script (+registry-db)
                →  execution plans per track (+registry-exec-*)  →  packages (split)  →  delivery
```

**Conflict rule.** When two artifacts disagree, the **upstream** artifact
governs. The downstream stage never silently adjusts the upstream text and
never silently follows its own reading: it records the deviation as an ADR
(§5) and continues if the deviation is non-breaking, or stops with a BLOCKED
ADR if it is breaking. A contradiction without an ADR is a governance failure
(`gov.py analyze` finding, severity per the contract clause it violates).

Corollaries that used to be separate rules and now follow from this one:
- a PRD expresses a **need**, never an enforceable rule — the SRS is where
  rules become requirements; a PRD that defines requirement-level content is a
  contract violation (see [ARTIFACT-CONTRACTS.md](ARTIFACT-CONTRACTS.md));
- no stage invents content another stage owns (business rules, data structure,
  execution decisions, UX decisions) — it cites the owning artifact by ID;
- no stage regenerates, renames or reformats an upstream ID (§3);
- an artifact is consumed whole: a stage never starts on an incomplete
  predecessor (the orchestrator refuses to build a brief whose inputs are
  missing from `_state/`).

## 2. Vocabulary — the domain's ubiquitous language

Every domain word comes from `profile.vocabulary` and nowhere else:

| Key | Used for |
|---|---|
| `vocabulary.module_prefixes` | the module codes registered so far (`naming.module_code`); a module named during a run but not yet listed here is used as RESERVED (never blocked) and the list is extended later — no stage invents a code, but no stage waits on the profile either |
| `vocabulary.keyword_map` | free-text → module detection at inception (any language) |
| `vocabulary.entity_kinds` | the classification every entity carries; `profile.conventions.entity_defaults` is keyed by it |
| `vocabulary.glossary` | terms used **verbatim** by every stage and every artifact (DDD ubiquitous language); a retired or synonymous term is a DRIFT finding |
| `vocabulary.bounded_contexts` | which modules belong together; cross-context dependencies are the ones [XM-PROTOCOL.md](XM-PROTOCOL.md) tracks most strictly |

Languages: `profile.languages.all` are carried by every artifact when
`profile.languages.require_all` is true; `profile.languages.primary` is the
language of headings and IDs' human labels. There is no other language rule.

## 3. Stages and ID ownership

The stage list, its passes, the question policy and each stage's inputs and
products are rendered from `factory.stages` / `factory.standalone`:

<!-- RENDER:stages -->
| Stage | Title | Pass | Questions | Lane | Inputs | Produces | Owns IDs | Then |
|---|---|---|---|---|---|---|---|---|
| `domain-profile` | Domain Profile | pre | allowed (dialogue) | `analysis` | `raw-idea`, `platform-brief?` | `domain-profile.md` | — | P-1 |
| `P-1` | Registry & Steering Builder | bootstrap | forbidden | `analysis` | `domain-profile` | `project-registry.md` | — | P0 |
| `P0` | Platform Inception | 1 | allowed (dialogue) | `analysis` | `domain-profile`, `project-registry` | `platform-summary.md`, `module-registry-{mod}.md`, `business-policies-{mod}.md` | `POL` | P0.5 |
| `P0.5` | PRD | 1 | allowed (dialogue) | `analysis` | `platform-summary`, `module-registry`, `business-policies` | `prd-{mod}.md` | `US` | gate `prd-approval` |
| `P1` | SRS | 1 | forbidden | `analysis` | `prd`, `domain-profile`, `project-registry` | `srs-{mod}.md`, `registry-srs-{mod}.md` | `REQ`, `AC`, `ENT`, `RULE`, `SCR-REQ` | P2 |
| `P2` | Database | 1 | forbidden | `analysis` | `srs`, `registry-srs` | `db-script-{mod}.md`, `registry-db-{mod}.md` | `DBF`, `XM` | P3.1 |
| `P3.1` | Backend Execution Plan | 1 | forbidden | `analysis` | `srs`, `db-script`, `registry-srs`, `registry-db` | `backend-execution-plan-{mod}.md`, `registry-exec-be-{mod}.md` | `API`, `QR` | gate `pass-1` |
| `P3.2` | Frontend — UX Design + Execution Plan | 2 | forbidden | `analysis` | `srs`, `prd`, `api-docs`, `registry-srs`, `registry-exec-be` | `flow-diagram-{mod}.md`, `ui-ux-spec-{mod}.md`, `frontend-execution-plan-{mod}.md`, `registry-exec-fe-{mod}.md` | `UXD`, `SCR` | gate `pass-2` |
<!-- /RENDER:stages -->

**ID namespace.** IDs follow `factory.ids.pattern` with `factory.ids.seq_width`
digits and one of `vocabulary.module_prefixes` as the module part. The atoms —
prefix, owning stage, what each atom must trace to and what it requires — are
`factory.ids.atoms`, extended (never redefined) by `profile.ids.atoms`:

<!-- RENDER:ids -->
Pattern `{prefix}-{MOD}-{seq}`, sequence width 3.

| Atom | Meaning | Owner | Traces to | Requires |
|---|---|---|---|---|
| `POL` | business policy | `P0` | — | — |
| `US` | user story | `P0.5` | `POL` | — |
| `REQ` | requirement (EARS) | `P1` | `US` | `AC` |
| `AC` | acceptance criterion (Given/When/Then) | `P1` | `REQ` | — |
| `ENT` | entity | `P1` | — | — |
| `RULE` | business rule | `P1` | `REQ` | — |
| `DBF` | db field | `P2` | `REQ`, `ENT` | — |
| `XM` | cross-module dependency | `P2` | `REQ` | — |
| `API` | api endpoint | `P3.1` | `REQ`, `DBF` | — |
| `QR` | query reference | `P3.1` | — | — |
| `UXD` | ux decision | `P3.2` | `REQ`, `AC` | — |
| `SCR` | screen | `P3.2` | `REQ`, `UXD` | — |
| `SCR-REQ` | screen requirement | `P1` | `REQ` | — |
| `TC` | test case | `test-gen` | `AC`, `XM`, `UXD` | — |
| `ADR` | analysis decision record | `any` | — | — |
| `CS` | change set | `versioning` | — | — |
<!-- /RENDER:ids -->

Rules (all machine-checked by `gov.py analyze`):
1. **Ownership.** An ID is created only by the stage whose `owns_ids` lists its
   atom. Every other stage references it by ID and never reassigns, renames,
   reformats or re-numbers it.
2. **Continuity.** Sequences are per module and per atom, never restart, and
   continue across versions (see [VERSIONING.md](VERSIONING.md)). A gap or a
   duplicate is a finding.
3. **Traces.** Every atom with `traces_to` carries a `traces:` reference to at
   least one ID of each listed kind (attribute grammar in
   [MARKER-PROTOCOL.md](MARKER-PROTOCOL.md) for marker-bearing artifacts; a
   `traces:` line in the ID's block otherwise). An atom with `requires` must be
   accompanied by at least one ID of the required kind pointing back at it.
4. **Registry agreement.** Every ID an artifact defines appears in the stage's
   registry artifact (`produces[*].registry: true`) and vice versa — see
   [REGISTRY-SCHEMA.md](REGISTRY-SCHEMA.md).
5. **No orphans.** An ID nothing downstream references by the end of a pass is
   an orphan; severity per the contract that expects the reference.

## 4. Continuation rule — engines read `_state/` only

The filesystem is the version authority (`factory.versioning`). Before a
stage runs, `gov.py state` regenerates the module's current state into
`paths.module.state_dir` (`naming.current_state_file` per artifact) from the
base version plus every delta. An engine brief contains **only** files from
`_state/` (plus `_inputs/` for inputs fetched from consumer repos,
`factory.inputs`). Engines never open `v1/…` or `vN/…` folders directly, never
ask the user to repeat what the state files show, never restart an ID sequence
visible in them, and never regenerate a stage already committed for the same
version. Continuation is therefore stateless: whoever runs next reads
`_state/`, the registries and the ADR stream, and continues from the last
commit.

## 5. Ambiguity rule

After the last stage with `questions: allowed`, no stage asks anything. It
chooses the best-practice answer itself, using `profile.knowledge.files` and
the steering block of `domain-profile`, and records the choice
(`factory.ambiguity`):

| Case | Definition | Action |
|---|---|---|
| **non-breaking** | does not contradict a locked upstream decision or an existing requirement | `ambiguity.non_breaking`: write an ADR, continue |
| **breaking** | contradicts a locked decision, an upstream artifact, or a consumer-facing ID | `ambiguity.breaking`: write an ADR with status BLOCKED, the orchestrator stops the pass; the ADR is surfaced at the next human decision point |

**ADR format** — one file per decision at
`paths.decisions/<MOD>/` named by `naming.adr_file`; immutable once committed;
numbered per module from the `ADR` atom's sequence:

```
# ADR-<MOD>-<SEQ> — <one-line title>
Status      : ACCEPTED | BLOCKED | SUPERSEDED (by ADR-<MOD>-<SEQ>)
Stage       : <stage id>        Module: <MOD>        Version: v<N>
Context     : what was ambiguous and which upstream text/IDs frame it
Decision    : the choice made and the best-practice source it follows
Consequences: what downstream stages must now do / may no longer do
traces      : <IDs affected — required, ≥1>
```

The pass gate reads every ADR of the version; a later version that revisits a
decision writes a new ADR that names the one it supersedes. "Derivation logs",
"open-question logs" and "findings records" of earlier designs are all this
single stream.

## 6. Completion protocol — executed by the orchestrator, stated once

`gov.py run-stage` performs the same steps for every stage; no engine text
restates them:

1. **state** — `gov.py state` refreshes `_state/`; the brief is built from the
   stage template + `profile` + `factory` + `_state/` (+ `_inputs/` when the
   stage's `inputs` name a fetched input).
2. **dispatch** — the stage's `lane` (`factory.lanes`) runs the brief; a
   dialogue lane converges first (§7). A `[QUESTION]` block from a stage with
   `questions: forbidden` is refused and the stage is re-run with §5 applied.
3. **write** — the stage's `produces[*]` files land in the module version
   folder ([VERSIONING.md](VERSIONING.md)); a delta version writes only the
   changed artifacts plus `paths.module.change_manifest`.
4. **registry** — the stage's `registry: true` artifacts are written and the
   project-registry rows it owns are updated ([REGISTRY-SCHEMA.md](REGISTRY-SCHEMA.md)).
5. **analyze** — `gov.py analyze` writes `paths.module.analyze_report`; any
   CRITICAL finding stops here (REVISE via `gates[*].on_revise` lane, at most
   `review.revise_max` times, then ESCALATE).
6. **commit** — one commit per stage, message `naming.commit.stage`.
7. **gate / next** — if `stage.next` names a gate, `gov.py gate` runs
   ([QUALITY-RUBRIC.md](QUALITY-RUBRIC.md)); otherwise the next stage starts.
   A pass with `session: bundled` runs its stages in one delegate session with
   per-stage commits and halts on a BLOCKED ADR.

## 7. Lanes and delegation

Every reasoning step is a self-contained brief dispatched on a lane; every
mechanical step (split, deliver, state, analyze, tag) is a direct `gov.py`
operation — deterministic, no brief, no lane, no model:

<!-- RENDER:lanes -->
| Lane | Implementers | Effort | Mode | Dialogue |
|---|---|---|---|---|
| `analysis` | `claude:opus` | high | — | max 4 rounds, converge on *mutually-acceptable* |
| `review-per-engine` | `claude:sonnet` | medium | read-only | — |
| `review-holistic` | `claude:sonnet` | medium | read-only | — |
| `merge-review-notes` | `claude:sonnet` | low | — | — |
| `test-gen` | `claude:opus` | high | — | — |
<!-- /RENDER:lanes -->

- `implementers` is a **list**. One entry → single implementer. More than one
  → the lane is a dialogue: the implementers exchange positions on each open
  point for at most `dialogue.max_rounds`, stop at `dialogue.converge_on`, and
  emit `dialogue.output` inside the artifact. Nothing is left open for a human.
- The reviewer lane is `read_only: true`: it never edits an artifact, never
  writes a registry, never commits.
- The orchestrator (`gov.py`) owns every commit and every registry write; an
  implementer that commits has violated the lane contract.
- Adding or swapping a model is an edit to `factory.lanes`, nothing else.

## 8. Profile conventions — applied only when declared (C5)

`profile.conventions` is optional; each block is applied only when present,
and no prose anywhere may add a convention that is not a profile field:

| When … | Then every stage that touches the concept … |
|---|---|
| `conventions.composite_screen` is true | treats a screen group (search + entry, master + detail, wizard) as ONE screen with ONE screen ID; sub-screens never get their own ID, registry row or lazy chunk; the backend plan declares one handler unit per composite; the frontend plan one `stack.frontend.lazy_chunk_per` unit |
| `conventions.security_model` is set | maps every screen to exactly one row of `security_model.page_registry`, names permissions by `security_model.permission_pattern` over `security_model.actions`, and treats `security_model.gateway_action` as the prerequisite of every other action |
| `conventions.entity_defaults` is set | gives every entity of a kind the listed default fields (checked at the SRS and DB stages; `profile.review.extra_checks` may score it) |
| `conventions.numbering` is set | follows that rule for document numbering and never generates numbers inside a module |
| `conventions.lookups` is set | follows that rule for list-of-values handling |
| `conventions.workflow_engine` is `forbidden` | models approvals as explicit states and rules inside the module; a generic workflow engine is a CRITICAL finding |

Violations of an applied convention are scored as `profile.review.extra_checks`
data at the pass gate ([QUALITY-RUBRIC.md](QUALITY-RUBRIC.md)); there is no
separate checklist.
