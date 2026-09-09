# CONSTITUTION — the six principles and how each is enforced

```
Doc            : shared/CONSTITUTION.md
Role           : the binding principles of the factory; everything else derives from them
Loaded by      : every engine brief, every reviewer brief, `gov.py lint` (as its rationale)
Generated parts: none (this file states rules only; every value lives in factory.yaml / profiles)
Links          : GOVERNANCE-CORE.md · ARTIFACT-CONTRACTS.md · QUALITY-RUBRIC.md · VERSIONING.md
```

## 0. Identity and boundary

The factory is a git-native, domain-agnostic **analysis factory**
(`factory.boundary`). Input: a raw product idea plus a domain profile.
Output: reviewed, versioned, traceable analysis artifacts and per-track
execution plans, split into packages and delivered to consumer repos
(`factory.repos`). The line runs domain-profile → … → delivery and **stops at
delivery**. It never implements, never audits an implementation, never runs
tests inside the line. A domain is a data file under `paths.profiles`, never
engine text.

## 1. The six principles

A principle that is only written down is a wish; each one below names the
mechanism that makes it true.

| # | Principle | Rule | Enforcement mechanism |
|---|---|---|---|
| C1 | **Single source of truth** | Every factory fact (stages, passes, gates, lanes, paths, naming, ID grammar, marker grammar, thresholds, rubric) lives in `factory.yaml`; every domain fact (vocabulary, phases, stack, languages, conventions, knowledge, extra checks) lives in `profiles/<id>.yaml`. | Tables in docs, every `SKILL.md`, the README pipeline map, the contracts index and the marker tables are produced by `gov.py render` inside `<!-- RENDER:… -->` blocks. A hand-edited generated block or a restated value fails `gov.py lint` (rule `C1-structure`, render freshness). |
| C2 | **No hardcode** | Engines, docs, reviewers and tools reference config keys (`factory.<key>`, `profile.<key>`, `CFG.*`), never literals — no stage id, phase key, ID prefix, stack name, path, model name or domain word outside the two sources. | `gov.py lint` scans `lint.scan_paths` for `lint.forbidden_terms` and for profile literals (`lint.profile_term_sources`), and scans `lint.code_paths` for stage ids / phase keys / ID prefixes as string literals. CI-blocking. |
| C3 | **No contradictions** | There is no precedence or override file. Superseded text is deleted from its source, never out-ranked. | `gov.py analyze` cross-checks artifacts against [ARTIFACT-CONTRACTS.md](ARTIFACT-CONTRACTS.md); `gov.py lint` cross-checks docs against `factory.yaml` through the render diff; `markers.rules.unknown_phase` refuses rather than skips. |
| C4 | **No duplication** | One toolkit, one parser, one registry per stage, one command tree (`paths.commands`), one completion protocol, one gate template. A rule is stated once; other files link to it. | `gov.py lint` rule `C4-duplicate` fails on a second command tree. Shared rules live in [GOVERNANCE-CORE.md](GOVERNANCE-CORE.md); the completion protocol is executed by the orchestrator, not restated per engine; `reviewers/pass-review.md` is the only gate brief. |
| C5 | **No exceptions** | Anything "special" is a profile field or a config flag, never a carve-out in prose. Absent optional field = behaviour not applied. | `profiles/_schema.yaml` is the only place variability is declared; `gov.py lint --profile <id>` validates every profile against it (rule `C5-profile`). A behaviour that cannot be expressed as a field is redesigned until it can. |
| C6 | **Flexibility + minimal questions** | A new domain is a new profile. Questions are asked only where `factory.stages[*].questions == allowed`, resolved in-dialogue by the lane's implementer list. Humans decide at exactly the points listed in `factory.gates`. | The orchestrator refuses a `[QUESTION]` block from any stage whose `questions` is `forbidden`; those stages self-resolve per `factory.ambiguity` (see [GOVERNANCE-CORE.md §5](GOVERNANCE-CORE.md#5-ambiguity-rule)). Dialogue lanes converge per `factory.lanes.<lane>.dialogue`. |

## 2. Question policy (C6) and the human decision points

- **Where questions may be raised:** only stages with `questions: allowed`
  (rendered in [GOVERNANCE-CORE.md §3](GOVERNANCE-CORE.md#3-stages-and-id-ownership)).
  Those stages run on a dialogue lane (`stages[*].dialogue: true`): the
  implementer list of `factory.lanes.<lane>` converges within
  `dialogue.max_rounds` on `dialogue.converge_on`; the output is
  `dialogue.output` — closed decisions, never an external open-questions file.
- **After the last question-allowed stage** every ambiguity is self-resolved:
  non-breaking → ADR and continue; breaking → ADR with status BLOCKED and the
  pass stops (`factory.ambiguity`). No engine ever writes "STOP and ask the user".
- **Human decision points** (`factory.gates`, nothing else):
  1. the gate of `type: human-approval` — the user approves the PRD file itself
     before the stage it `blocks` may start;
  2. one gate of `type: review` per pass — a read-only reviewer scores the pass
     against [QUALITY-RUBRIC.md](QUALITY-RUBRIC.md) and the human accepts
     APPROVE / REVISE / ESCALATE. A gate opens only when the analyze report is
     `requires_analyze: clean`.

## 3. Standalone stages are never a gate for the core

`factory.standalone` stages run outside the line, on demand, after the artifacts
they consume exist. Their absence is never a pipeline gap, their findings never
block a pass gate, and no core stage lists them as an input. They reuse the same
toolkit, lanes, ID grammar and contracts as the core.

## 4. What this document is not

It restates no value. Where a number, a name or a list is needed, the reader
follows the key reference or the rendered block. If this file and
`factory.yaml` ever disagree, `factory.yaml` is right and this file is fixed.
