---
name: P3.5
description: Test-Case Spec (TestSprite-ready) engine of the governance factory (pass 1 tail (backend tests, after P3.1) and pass 2 tail (frontend tests, after P3.2)). Produces the TC specs the track splitter packages (backend-test / frontend-test). Framework-agnostic; executed later by TestSprite inside the repos.
---

# P3.5 — Test-Case Spec (TestSprite-ready)

Full instruction in `references/` (loaded only when this stage runs).

```
WHEN      : pass 1 tail (backend tests, after P3.1) and pass 2 tail (frontend tests, after P3.2)
INPUTS    : the track's execution plan + srs + registries
PRODUCES  : backend-test-plan-{mod}.md / frontend-test-plan-{mod}.md (+ registry-test-*) — SPLIT by agent3 into the *-test packages and DELIVERED with the track
NEXT      : split + deliver (same track)
REVIEW    : no (covered by the holistic gate)
LANE      : LANES["analysis"] — model/effort from the delegate brief per run.
```

## LOAD FIRST (shared governance)
`shared/FACTORY-PRECEDENCE.md` → `shared/GOVERNANCE-CONFIG.md` →
`shared/shared-governance-rules.md` + `shared/shared-artifact-contracts.md`
(+ `shared/PROJECT-3-REGISTRY.md` for P3.x / P3.5 / P4.x) → then `references/`.

## Factory completion protocol (git-native)
1. Write artifacts into `modules/[MOD]/[vN/]<stage-folder>/` (or `platform/` for
   platform-level outputs) with module-qualified names (config.ARTIFACT_FILES).
2. Inline REGISTRY step where the reference defines one — same commit.
3. `git add` + commit `"P3.5: [MOD] v[N] — <one line>"` (the commit is the ledger).
4. Print the NEXT-ENGINE INPUT block for the next stage.
