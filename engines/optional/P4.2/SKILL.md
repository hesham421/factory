---
name: optional/P4.2
description: Frontend Governance Audit → FIX-PROMPTS engine of the governance factory (optional (`/audit frontend`)). Optional. Output = paste-ready fix-prompts per owning engine.
---

# optional/P4.2 — Frontend Governance Audit → FIX-PROMPTS

Full instruction in `references/` (loaded only when this stage runs).

```
WHEN      : optional (`/audit frontend`)
INPUTS    : frontend analysis set + api-docs/ui-shell inputs
PRODUCES  : FIX-PROMPTS grouped by owning engine into modules/[MOD][/vN]/P4-Audit/
NEXT      : owning engines apply fixes
REVIEW    : — (it IS a review)
LANE      : LANES["review-holistic"] — model/effort from the delegate brief per run.
```

## LOAD FIRST (shared governance)
`shared/FACTORY-PRECEDENCE.md` → `shared/GOVERNANCE-CONFIG.md` →
`shared/shared-governance-rules.md` + `shared/shared-artifact-contracts.md`
(+ `shared/PROJECT-3-REGISTRY.md` for P3.x / P3.5 / P4.x) → then `references/`.

## Factory completion protocol (git-native)
1. Write artifacts into `modules/[MOD]/[vN/]<stage-folder>/` (or `platform/` for
   platform-level outputs) with module-qualified names (config.ARTIFACT_FILES).
2. Inline REGISTRY step where the reference defines one — same commit.
3. `git add` + commit `"optional/P4.2: [MOD] v[N] — <one line>"` (the commit is the ledger).
4. Print the NEXT-ENGINE INPUT block for the next stage.
