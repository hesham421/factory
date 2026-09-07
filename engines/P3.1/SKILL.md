---
name: P3.1
description: Backend Execution Plan engine of the governance factory (analysis pass 1). Use when running `/analyze-pass1` reaches this stage, or to (re)generate this stage for a module version.
---

# P3.1 — Backend Execution Plan

The full engine instruction is in `references/` (loaded only when this stage
runs — keep this SKILL small). This file states the factory contract only.

```
PASS      : 1          (see governance-tools/config.py PASS_1 / PASS_2)
INPUTS    : srs · db-script · ui-ux-spec · registries
PRODUCES  : backend-execution-plan-{mod}.md + registry-exec-be-{mod}.md  → split (backend) → DELIVER (pass 1 ends)
NEXT      : — pass 1 ends; pass 2 = P3.2 after inputs
REVIEW    : YES — per-engine review gate (LANES['review-per-engine'])
LANE      : LANES["analysis"] — model/effort come from the delegate brief per
            run (default opus/high); override per call, never hardcode here.
```

## LOAD FIRST (shared governance)
`shared/FACTORY-PRECEDENCE.md` → `shared/GOVERNANCE-CONFIG.md` →
`shared/shared-governance-rules.md` + `shared/shared-artifact-contracts.md`
(+ `shared/PROJECT-3-REGISTRY.md` for P3.x) → then `references/`.

## Factory completion protocol (git-native — replaces the Drive/ledger steps)
1. Write the stage artifacts into `modules/[MOD]/[vN/]<stage-folder>/` using
   the module-qualified names above (config.ARTIFACT_FILES of the track).
2. Run the inline REGISTRY step (registry-<stage>-{mod}.md + project-registry
   update) — same session, same commit.
3. `git add` + commit: `"P3.1: [MOD] v[N] — <one line>"`. The commit IS the
   ledger row; no JSON ledger.
4. If REVIEW = YES → stop and run `/review-gate P3.1` before the next stage.
5. Print the NEXT-ENGINE INPUT block (references/… §1D.5 shape) for the next
   stage. Dependencies: continue ID sequences from the registries; honor
   XM / UXD / ALIGN; a breaking change STOPS.

## Versioning (extensions = same flow)
A new feature on a built module = `gov.py version -m [MOD] --new` → vN, then
this same engine runs in delta mode (Change Manifest: CS-ID, baseline v[N-1],
NEW/MODIFIED/UNCHANGED) — see commands/micro-feature.md. v[N-1] stays frozen
and tagged.
