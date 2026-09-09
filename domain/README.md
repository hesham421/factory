# domain/ — the platform's domain profile (entry gate of the line)

```
Doc            : domain/README.md
Role           : what lives here and why nothing runs without it
Loaded by      : humans; the bootstrap stage reads the file this folder holds (paths.domain)
Generated parts: none
Links          : ../shared/ARTIFACT-CONTRACTS.md C1 · ../shared/GOVERNANCE-CORE.md §1–2 · ../profiles/_schema.yaml
```

- **What is here:** exactly the product of the `domain-profile` stage
  (`stages[domain-profile].produces`) — one file per platform, saved here
  from the conversational domain-profile project. Nothing else is written to
  this folder.
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
