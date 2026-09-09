# project/ — project-level artifacts (not per module)

```
Doc            : project/README.md
Role           : what lives here and why nothing runs without it
Loaded by      : humans; the bootstrap stage and every later stage read these files
                 through the orchestrator (paths.domain, paths.platform)
Generated parts: none
Links          : ../shared/ARTIFACT-CONTRACTS.md C1–C2 · ../shared/GOVERNANCE-CORE.md §1–2 ·
                 ../shared/REGISTRY-SCHEMA.md · ../shared/XM-PROTOCOL.md · ../profiles/_schema.yaml
```

This folder holds the two artifacts that exist once per platform, not once per
module: the domain profile (entry gate of the line) and the project registry
(the orchestrator's running index). Nothing else is written here by any
stage.

## Domain profile

- **What is here:** exactly the product of the `domain-profile` stage
  (`stages[domain-profile].produces`) — one file per platform, saved here
  from the conversational domain-profile project.
- **Where it comes from:** the `domain-profile` stage is conversational
  (`questions: allowed`, `dialogue: true`, `research: web`): it absorbs the raw
  idea, researches how established systems structure similar products,
  proposes recommended answers, and closes every question in-dialogue on its
  lane. The user's review is of the **saved file**, not a gate.
- **Entry gate:** the bootstrap stage (`P-1`) refuses to start until this
  file exists and carries no open question (contract C1). The same file is
  an input to the inception and SRS stages (`stages[*].inputs`).
- **The steering block** — the part every later stage must obey verbatim:
  the confirmed `profile.vocabulary` entries (module codes, glossary,
  bounded contexts), the platform decisions taken during the dialogue, and
  the `profile.knowledge.files` the later stages cite as primary sources.
  Anything in the steering block is a locked decision; contradicting it after
  PRD approval is a breaking ambiguity (`factory.ambiguity.breaking`).
- **Relation to the profile:** the profile (`profiles/<id>.yaml`) is the
  domain as reusable data; the domain-profile file is this platform's
  instance of it. The file never restates profile values — it references them.
- Maintained by commit like every artifact. A platform has one; a change to
  it is a new commit and, if breaking for existing modules, an ADR per
  affected module.

## Project registry

- **Content:** exactly the products of `P-1` (`stages[P-1].produces`): the
  **project registry**, one per platform. No other file is created here by
  any stage; a file that is not a `P-1` product does not belong in this
  folder.
- **Created once** (`once_per: platform`) by the bootstrap command
  (`factory.commands[bootstrap]`), from the domain profile above. Nothing
  before it may require it, so a new platform never deadlocks.
- **Maintained by the orchestrator**, never by hand: after every stage the
  registry step of `gov.py run-stage` applies the stage's rows (module index,
  entity ownership, shared declarations, dependency indexes, decision index,
  status, event history) under the update discipline of
  [REGISTRY-SCHEMA.md §1](../shared/REGISTRY-SCHEMA.md).
- **Shape:** the nine canonical categories with a compliance map; the
  domain's preferred section layout, if any, comes from
  `profile.knowledge.files`.
- Committed like everything else; git history is the ledger.
