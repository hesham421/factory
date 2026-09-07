# delegate-skills (model/effort control)
Install once in this repo (Claude Code):
```
npx skills add amElnagdy/delegate-skills --skill codex-delegate --agent claude-code
```
Every reasoning step of the factory (analysis stages, review gates, merge of
review notes) is dispatched as a self-contained BRIEF through delegate: the
brief carries `implementer` (claude|codex), `model`, `effort`. Defaults live
in `governance-tools/config.py` LANES; `/review-gate` and the analysis
commands accept overrides per run. Mechanical steps (split, deliver, tag,
fetch-inputs) run tools only — no model, no cost.
The orchestrator (Claude Code) always owns review and commits; the implementer
never commits (delegate-skills contract).
