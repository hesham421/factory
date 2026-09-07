# PROJECT-REG — STATE REGISTRY EXTRACTOR — RETIRED (AMEND-PIPELINE-V5)

```
Status : RETIRED 2026-09-06. Do not run this as a separate project.
Why    : Its extraction (registry-srs / registry-db / registry-exec-* /
         registry-test-* -{mod}.md) is now the INLINE REGISTRY step of every
         core engine's completion protocol — GOVERNANCE-CONFIG.md §1D.4 —
         executed in the same session right after the stage artifact.
Where  : P1 → registry-srs-{mod}.md · P2 → registry-db-{mod}.md ·
         P3.1 → registry-exec-be-{mod}.md · P3.2 → registry-exec-fe-{mod}.md ·
         P3.5 → registry-test-*-{mod}.md   (names per §1D.2)
Master : the project-registry update that used to follow extraction is also
         inline (§1D.4 step 2). P(-1) Master Registry Builder now only
         BOOTSTRAPS the registry once per project.
```

If a session is opened in this project by mistake, reply with exactly:
"P-REG is retired — this step now runs inside the engine that produced the
artifact (GOVERNANCE-CONFIG §1D.4). Re-run that engine's completion protocol."
