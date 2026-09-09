# QUALITY RUBRIC — how a pass is scored at its gate

```
Doc            : shared/QUALITY-RUBRIC.md
Role           : the ISO/IEC/IEEE 29148 attributes as applied to factory artifacts, the scoring, the verdicts, the gate record
Loaded by      : reviewers/pass-review.md, gov.py gate, the merge-review-notes lane
Generated parts: RENDER:review-rubric (attributes, scale, threshold, verdicts from factory.review)
Links          : CONSTITUTION.md · ARTIFACT-CONTRACTS.md · GOVERNANCE-CORE.md · VERSIONING.md
```

One gate per pass (`factory.gates`, `type: review`), one read-only reviewer
lane, one scorecard. The reviewer scores; the human decides on the verdict.

## 1. Attributes, scale, threshold, verdicts

<!-- RENDER:review-rubric -->
Scale 0–3; every attribute must score ≥ 2 to APPROVE; verdicts `APPROVE`, `REVISE`, `ESCALATE`; at most 1 REVISE per finding before ESCALATE.

- `unambiguous`
- `verifiable`
- `complete`
- `consistent`
- `singular`
- `feasible`
- `traceable`
<!-- /RENDER:review-rubric -->

## 2. What each attribute means for our artifacts

| Attribute | The artifact set of the pass scores high when … | Typical evidence / failure |
|---|---|---|
| **unambiguous** | every statement has one reading; every requirement follows an EARS pattern (`factory.ids.ears.patterns`); glossary terms (`profile.vocabulary.glossary`) are used verbatim; no "etc.", "as appropriate", "and/or" | a `REQ` that two implementers would build differently; a mixed-term entity name |
| **verifiable** | every `REQ` has ≥1 `AC` in Given / When / Then that a test could execute; plan blocks name observable outcomes | an `AC` that restates the requirement instead of a check; "fast", "user-friendly" without a measure |
| **complete** | every input ID that should have a downstream counterpart has one (no orphan `US`/`REQ`/`ENT`/`UXD`); every `profile.languages.all` language present when `require_all`; every phase of the plan present; delta versions list UNCHANGED explicitly | an entity with no fields; a policy no story cites; a screen with no flow |
| **consistent** | no artifact contradicts an upstream one (upstream wins — [GOVERNANCE-CORE.md §1](GOVERNANCE-CORE.md#1-truth-layers)); registries agree with artifacts; the same fact appears once and is referenced by ID elsewhere | a plan restating a column type that differs from the DB script; two IDs for one concept |
| **singular** | one requirement per `REQ`, one decision per ADR, one screen per `SCR` (a composite counts as one when `profile.conventions.composite_screen`), one atom per marker block | a `REQ` with "and" joining two behaviours; a grouped API block |
| **feasible** | the plan is buildable on `profile.stack` with the declared conventions; dependencies are READY or DEFERRED with a workaround ([XM-PROTOCOL.md](XM-PROTOCOL.md)); nothing assumes a component outside the stack | a frontend block calling an endpoint absent from api-docs; a workflow engine when `conventions.workflow_engine` is forbidden |
| **traceable** | every `traces` clause of the pass's contracts holds; the traceability matrix in `_state/` has no dangling reference and no sequence gap; every ADR carries `traces` | an `API` with no `REQ`; a `DBF` citing a non-existent `ENT` |

## 3. Scoring

- Each attribute gets one integer score on `factory.review.scale` for the
  **pass as a whole** (all artifacts of the pass in this version), plus a
  per-artifact breakdown in the findings.
- The reviewer scores what `gov.py analyze` cannot: the analyze report is
  input, not the score. A CRITICAL analyze finding means the gate never opened
  (`gates[*].requires_analyze`), so the reviewer sees only MAJOR/MINOR ones.
- `profile.review.extra_checks` are scored **as data**: each entry (`id`,
  `stage`, `check`, `severity`) becomes one row with PASS / FAIL and a finding
  on FAIL, at the entry's severity. No profile check is described in prose
  here or in the reviewer template.
- Every score below `factory.review.pass_threshold` must be accompanied by ≥1
  finding that explains it.

## 4. Verdict

| Verdict (`factory.review.verdicts`) | Condition | Orchestrator effect |
|---|---|---|
| APPROVE | every attribute ≥ `review.pass_threshold`, no CRITICAL finding, every extra check PASS or MINOR | gate commit (`naming.commit.gate`), then `passes.<n>.then` continues (split, deliver, tag) |
| REVISE | any attribute < threshold or any MAJOR finding, and this is the first REVISE for the finding set | findings go to the `gates[*].on_revise` lane, which edits the owning stage's artifacts; `analyze` reruns; the gate reruns once (`review.revise_max`) |
| ESCALATE | a CRITICAL finding, a BLOCKED ADR, or a REVISE already spent on the same finding | the pass stops; the human resolves at the gate |

The human accepts or overrides the reviewer's verdict; an override is recorded
in the gate record with a reason.

## 5. Findings

Each finding: `id` (per gate, sequential), `severity` (CRITICAL / MAJOR /
MINOR), `artifact`, `line` (optional), `clause` (the contract clause id from
[ARTIFACT-CONTRACTS.md](ARTIFACT-CONTRACTS.md) or the extra-check id, or the
rubric attribute when neither applies), `problem`, `fix` (concrete enough for
the merge lane to apply without judgement). A finding without a fix is a
question, and questions are not allowed at this point (C6): the reviewer
proposes the best-practice fix and marks it for an ADR.

## 6. Gate record

Written by `gov.py gate` to `paths.module.gate_record` and committed with the
gate commit:

```
# GATE pass-<n> — <MOD> v<N>
Verdict      : <verdict>            Reviewer lane: <lane>   Attempt: <1|2>
Analyze      : critical <n> · major <n> · minor <n>   (paths.module.analyze_report)
Scores       : <attribute>: <score> … (one per rubric attribute)
Extra checks : <id>: PASS|FAIL …
Findings     : <the findings list, §5>
ADRs read    : <ADR ids of this version, with status>
Human        : accepted | overridden (<reason>)
```

The scores are also written into the delivery state
(`factory.delivery.execution_state.schema.gate`) so the consumer repo sees
what the analysis was cleared with.
