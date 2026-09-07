# /review-gate — run a review station through delegate, decide, commit

```
/review-gate <P1|P2|P3.1|P3.2>                 (per-engine, reviewers/per-engine-review.md)
/review-gate holistic <after-pass-1|after-pass-2> (reviewers/holistic-review.md)
  [--implementer claude|codex] [--model …] [--effort low|medium|high]
```
1. Build the brief from the reviewer template (self-contained: artifact(s),
   baseline if vN≥2, registries, rules). Lane defaults from config.LANES;
   flags override — this is how model/effort are controlled per run.
2. Dispatch with delegate-skills (`$codex-delegate` for codex; the claude
   implementer otherwise). Wait for the structured report.
3. Decide: APPROVE → commit `"review(<station>): [MOD] v[N] APPROVED"`.
   REVISE → apply fixes via LANES["merge-review-notes"], re-run the gate ONCE;
   a repeated REVISE on the same finding → stop and ask the human.
The orchestrator owns every commit; the reviewer never edits or commits.
