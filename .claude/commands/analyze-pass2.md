# /analyze-pass2 — P3.2 (frontend) after the repos published api-docs + ui-shell

```
/analyze-pass2 [MODULE] --version N
```

## 0 — Pass-2 gate (hard)
```bash
python3 governance-tools/gov.py fetch-inputs --module MOD --version N
```
Pulls `api-docs-<mod>.md` (backend repo) + `ui-shell-manifest-<mod>.md`
(frontend repo) from their agreed paths (config.REPOS[*].inputs) into
`modules/MOD[/vN]/_inputs/`. Exit 1 → GATE CLOSED: stop and print what is
still missing. Never run P3.2 on assumed inputs.

## 1 — Run P3.2 then P3.5 (frontend tests) (config.PASS_2)
`engines/P3.2` via delegate (`$claude-delegate --lane analysis`, override model/effort per run), reading `_inputs/` + flow/
ui-ux/registries (+ v[N-1] baseline in delta mode). The frontend plan may
consume ONLY endpoints in api-docs and ONLY shell pieces in the manifest.

## 2 — Gates
`/review-gate P3.2` (per-engine) → then `/review-gate holistic after-pass-2`
(codex/high by default) — integration across backend ↔ frontend.

## 3 — Split (frontend: execution + test plans) + execution-state
```bash
python3 governance-tools/gov.py structure --track frontend --module MOD [--new-version]
python3 governance-tools/gov.py archive   --track frontend --module MOD --source modules/MOD[/vN]/P3_2-staging
python3 governance-tools/gov.py split     --track frontend --module MOD
```

## 4 — DELIVER + tag (end of analysis)
```bash
python3 governance-tools/gov.py deliver --track frontend --module MOD --version N [--push]
python3 governance-tools/gov.py tag     --module MOD --version N        # [mod]-vN
```
Frontend packages → branch `gov/<mod>-vN-frontend`. The tag freezes the
version in the factory. Print: `ANALYSIS COMPLETE — [MOD] v[N]  (tag org-vN)`.

## Constraints
Same as pass 1. Track separation: frontend packages never enter the backend
repo and vice versa (delivery is per track by construction).
