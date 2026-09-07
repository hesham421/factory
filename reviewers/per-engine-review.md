# Per-engine review brief (delegate) — stations: P1 · P2 · P3.1 · P3.2

Dispatched via delegate-skills (`$codex-delegate` or the claude implementer).
The ORCHESTRATOR (Claude Code) writes this brief, sends it, reads the report,
and decides — the reviewer never edits artifacts or commits.

```
LANE        : review-per-engine   (config.LANES — default claude / sonnet / medium)
implementer : {claude|codex}      ← set per run
model       : {…}                 ← set per run
effort      : {low|medium|high}   ← set per run
```

## Brief (self-contained — the reviewer sees ONLY this)
```
ROLE     : independent reviewer of ONE governance stage output.
STAGE    : [P1|P2|P3.1|P3.2]   MODULE: [MOD]   VERSION: v[N]   CS-ID: [… | none]
ARTIFACT : <paste the stage artifact(s) — full text>
BASELINE : <for vN≥2: the v[N-1] artifact — full text>   REGISTRIES: <paste>
RULES    : <paste the engine's MUST/MUST NOT + naming §1D.2 + marker rules>

CHECK, in order — report each as PASS / FAIL(line, why) / N-A:
 1. Internal consistency of this stage alone (IDs unique, sequences continue
    the registries, no restart; markers well-formed; module-qualified names).
 2. Traceability to its input stage (every element maps back; nothing invented).
 3. DEPENDENCIES: every XM / UXD / ALIGN reference resolves; an additive delta
    does not break an existing mapping; a breaking change is FLAGGED, not hidden.
 4. Completeness vs the input (nothing dropped silently; UNCHANGED items listed
    in the Change Manifest when vN≥2).
 5. Ambiguity: anything the next stage could not act on deterministically.

OUTPUT (structured, no prose):
 VERDICT  : APPROVE | REVISE
 FINDINGS : [{id, severity: CRITICAL|MAJOR|MINOR, location, problem, fix}]
 QUESTIONS: [anything only the human can decide]
Do NOT modify the artifact. Do NOT propose scope beyond the stage.
```

## Orchestrator after the report
- REVISE → apply fixes via LANES["merge-review-notes"] (low effort), re-run
  this gate once; a second REVISE on the same finding → escalate to the human.
- APPROVE → commit `"review({stage}): [MOD] v[N] APPROVED"` and continue.
