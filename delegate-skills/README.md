# delegate-skills/ — how reasoning steps are dispatched

```
Doc            : delegate-skills/README.md
Role           : explains the lane mechanism; the lanes themselves are data in factory.yaml → lanes
Loaded by      : humans; gov.py reads factory.lanes directly
Generated parts: none (the lane table is rendered in shared/GOVERNANCE-CORE.md RENDER:lanes)
Links          : ../shared/GOVERNANCE-CORE.md §7 · ../shared/CONSTITUTION.md C6 · ../reviewers/pass-review.md
```

- Every reasoning step (a stage, a gate review, a merge of review notes) is a
  self-contained brief the orchestrator (`gov.py`) builds and dispatches on a
  **lane**. Every mechanical step (split, deliver, state, analyze, tag) is a
  direct `gov.py` operation — deterministic, no brief, no lane, no cost.
- A lane is `factory.lanes.<id>`: `implementers` (a **list** of
  `provider:model` entries), `effort`, and optionally `dialogue` or
  `read_only`. Each stage names its lane (`stages[*].lane`); each review gate
  names its lanes and its revise lane (`gates[*].lanes`, `gates[*].on_revise`).
- **Default: Claude only.** Every implementer entry shipped in `factory.yaml`
  is a Claude model; no other provider or tool is required. Adding or swapping
  a provider is an edit to `factory.lanes`, nothing else — no engine, reviewer
  or command changes.
- **Dialogue lanes** (`implementers` longer than one): the implementers argue
  each open point for at most `dialogue.max_rounds` and stop at
  `dialogue.converge_on`; the closed decisions (`dialogue.output`) are written
  into the artifact. Only stages with `dialogue: true` — which are exactly the
  stages with `questions: allowed` — use such a lane.
- **Read-only lane**: the gate reviewer (`read_only: true`) never edits, never
  writes a registry, never commits. It returns the JSON block that
  `reviewers/pass-review.md` specifies.
- **The orchestrator owns commits.** Implementers write artifacts into the
  brief's working set; `gov.py` runs the registry step, `analyze`, the commit
  and the gate. An implementer that commits has broken the lane contract.
- Overrides per run (`--model`, `--effort` on the gate command,
  `factory.commands`) change one dispatch; they never change `factory.yaml`.
