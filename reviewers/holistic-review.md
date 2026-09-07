# Holistic review brief (delegate) — gates: after pass 1 (backend) · after pass 2 (frontend)

Independent, cross-stage review of the WHOLE analysis of a module version.
Default implementer is **codex** (a different model family catches what the
analysing model misses on itself) — override per run.

```
LANE        : review-holistic     (config.LANES — default codex / high)
implementer : {codex|claude}      model: {…}      effort: {high}
```

## Reference
`references/MASTER-REVIEWER.md` — the former Master Reviewer project; its
checklist is folded into the CHECK list below and may be pasted into the brief.

## Brief (self-contained)
```
ROLE   : holistic reviewer of a module version's complete analysis.
GATE   : [after-pass-1 (backend set) | after-pass-2 (frontend set + integration)]
MODULE : [MOD]  VERSION: v[N]  CS-ID: [… | none]
SET    : <paste ALL artifacts of the gate: domain section, P0…P3.1 (pass 1)
          or P3.2 + api-docs + ui-shell inputs (pass 2), + all registries>
BASELINE (vN≥2): <v[N-1] set or its Change Manifest>

CHECK — cross-stage, report PASS / FAIL(where, why):
 1. Chain integrity: PRD → SRS → DB → UI/UX → execution plan — every element
    traceable end to end; no orphan, no silent drop.
 2. Dependency graph: XM (cross-module), UXD (cross-screen), ALIGN (plan↔DB /
    plan↔API) all resolve and are consistent across stages.
 3. Pass-2 only: frontend plan consumes ONLY endpoints present in api-docs and
    ONLY shell pieces present in the ui-shell manifest; nothing assumed.
 4. Versioning (vN≥2): delta is additive; v[N-1] behaviour untouched except
    where the Change Manifest says MODIFIED; IDs continue sequences.
 5. Split-readiness: markers/thresholds such that agent3 will package it
    deterministically (canonical phase keys, SUB qualification).

OUTPUT: VERDICT APPROVE|REVISE · FINDINGS[{id, severity, stage, location,
problem, fix, dependencies-to-move-with}] · QUESTIONS[]. No edits. No commits.
```

## Orchestrator after the report
REVISE → route each finding to its owning stage (fix via merge lane), re-run
only that stage's per-engine gate, then this holistic gate once more.
APPROVE → tag `gov.py tag -m [MOD] -v N` (pass 2) / proceed to split (pass 1).
