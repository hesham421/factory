---
name: P-1
description: Master Registry Builder (BOOTSTRAP) engine of the governance factory (bootstrap — ONCE per platform, before any module (`/bootstrap`)). Runs once to create the platform registry; per-module maintenance is inline.
---

# P-1 — Master Registry Builder (BOOTSTRAP)

Full instruction in `references/` (loaded only when this stage runs).

```
WHEN      : bootstrap — ONCE per platform, before any module (`/bootstrap`)
INPUTS    : domain/domain-profile.md (or the platform brief)
PRODUCES  : platform/project-registry.md + platform/platform-standards.md (+ indexes)
NEXT      : domain-profile / P0 for the first module
REVIEW    : no (per-module registry maintenance is inline in each engine)
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
3. `git add` + commit `"P-1: [MOD] v[N] — <one line>"` (the commit is the ledger).
4. Print the NEXT-ENGINE INPUT block for the next stage.
