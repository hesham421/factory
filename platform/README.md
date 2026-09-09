# platform/ — platform-level artifacts (not per module)

```
Doc            : platform/README.md
Role           : what the bootstrap stage writes here — nothing more
Loaded by      : humans; every stage reads the registry through the orchestrator (paths.platform)
Generated parts: none
Links          : ../shared/REGISTRY-SCHEMA.md · ../shared/ARTIFACT-CONTRACTS.md C2 · ../shared/XM-PROTOCOL.md
```

- **Content:** exactly the products of `P-1` (`stages[P-1].produces`): the
  **project registry**, one per platform. No other file is created here by
  any stage; a file that is not a `P-1` product does not belong in this
  folder.
- **Created once** (`once_per: platform`) by the bootstrap command
  (`factory.commands[bootstrap]`), from the domain profile
  (`../domain/`). Nothing before it may require it, so a new platform never
  deadlocks.
- **Maintained by the orchestrator**, never by hand: after every stage the
  registry step of `gov.py run-stage` applies the stage's rows (module index,
  entity ownership, shared declarations, dependency indexes, decision index,
  status, event history) under the update discipline of
  [REGISTRY-SCHEMA.md §1](../shared/REGISTRY-SCHEMA.md).
- **Shape:** the nine canonical categories with a compliance map; the
  domain's preferred section layout, if any, comes from
  `profile.knowledge.files`.
- Committed like everything else; git history is the ledger.
