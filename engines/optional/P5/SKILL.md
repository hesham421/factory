---
name: optional/P5
description: API Verify (Mode 5) engine of the governance factory (optional, POST-delivery — runs against the implemented backend (outside the factory's core path)). Optional, post-implementation. Kept for completeness; runs after the backend repo implemented a version.
---

# optional/P5 — API Verify (Mode 5)

Full instruction in `references/` (loaded only when this stage runs).

```
WHEN      : optional, POST-delivery — runs against the implemented backend (outside the factory's core path)
INPUTS    : delivered backend + api-docs
PRODUCES  : verification report
NEXT      : —
REVIEW    : —
LANE      : LANES["review-per-engine"] — model/effort from the delegate brief per run.
```

## LOAD FIRST (shared governance)
`shared/FACTORY-PRECEDENCE.md` → `shared/GOVERNANCE-CONFIG.md` →
`shared/shared-governance-rules.md` + `shared/shared-artifact-contracts.md`
(+ `shared/PROJECT-3-REGISTRY.md` for P3.x / P3.5 / P4.x) → then `references/`.

## Factory completion protocol (git-native)
1. Write artifacts into `modules/[MOD]/[vN/]<stage-folder>/` (or `platform/` for
   platform-level outputs) with module-qualified names (config.ARTIFACT_FILES).
2. Inline REGISTRY step where the reference defines one — same commit.
3. `git add` + commit `"optional/P5: [MOD] v[N] — <one line>"` (the commit is the ledger).
4. Print the NEXT-ENGINE INPUT block for the next stage.
