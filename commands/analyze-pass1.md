# /analyze-pass1 — Domain → P3.1, review gates, split (backend), DELIVER. Stops there.

```
/analyze-pass1 [MODULE] [--version N | --new]  "<optional free-text brief>"
```
The factory's first analysis pass for a module version. Everything is git-
native; model/effort per step come from the delegate brief (config.LANES).

## 0 — Resolve
- `MODULE`; version: `--new` → `gov.py version -m MOD --new` (vN), else current.
  vN ≥ 2 = an EXTENSION: read v[N-1] as baseline, work in delta mode
  (Change Manifest: CS-ID, baseline, NEW/MODIFIED/UNCHANGED), v[N-1] frozen.
- Domain: if `domain/domain-profile.md` is missing → run `engines/domain-profile`
  first (once per platform). Ensure the module's inherit section exists.

## 1 — Run the pass-1 engines in order (config.PASS_1)
`domain-profile → P0 → P0.5 → P1 → P2 → P2.5 → P3.1 → P3.5(backend tests)`
(`/bootstrap` must have run once for the platform: `platform/project-registry.md` exists.)
For each stage: load `engines/<id>/SKILL.md` (+ its reference), run it through
delegate `LANES["analysis"]` (default opus/high — override per run), commit per
stage (the commit is the ledger). Dependencies: continue ID sequences; honor
XM/UXD/ALIGN; a breaking change STOPS.

## 2 — Per-engine review gates (config.PER_ENGINE_REVIEW_AT = P1, P2, P3.1)
After each of those stages → `/review-gate <stage>` (reviewers/per-engine-
review.md, LANES["review-per-engine"]). REVISE → merge (low effort) → re-gate
once → else escalate. Do not proceed past a station that is not APPROVED.

## 3 — Holistic gate, after pass 1 (backend set)
`/review-gate holistic after-pass-1` (reviewers/holistic-review.md,
LANES["review-holistic"], default codex/high). APPROVE required.

## 4 — Split (tools, no model) — backend only (execution + test plans from P3.1 + P3.5)
```bash
python3 governance-tools/gov.py structure --track backend --module MOD [--new-version]
python3 governance-tools/gov.py archive   --track backend --module MOD --source modules/MOD[/vN]/P3_1-staging
python3 governance-tools/gov.py split     --track backend --module MOD      # 5 stages
```
Then generate `execution-state.json` for the backend packages (same shape as
the repos' generate-module-setup expects) into `modules/MOD[/vN]/`.

## 5 — DELIVER (end of pass 1 — the factory stops here)
```bash
python3 governance-tools/gov.py deliver --track backend --module MOD --version N [--push]
```
Packages + execution-state land on branch `gov/<mod>-vN-backend` in the
backend repo (config.REPOS). Commit + `gov.py tag` is done after pass 2.

## 6 — Hand-off note (print)
```
PASS 1 COMPLETE — [MOD] v[N]  delivered: backend branch gov/<mod>-vN-backend
WAITING (outside the factory):
  backend repo  → implement → publish  governance/api-docs/api-docs-<mod>.md
  frontend repo → implement UI/UX → publish governance/ui-shell/ui-shell-manifest-<mod>.md
Then run: /analyze-pass2 [MOD] --version N
```

## Constraints
- NEVER implement code. NEVER touch the consumer repos beyond the delivery branch.
- NEVER skip a review station; NEVER continue past a REVISE.
- Names, paths, branches, lanes: from config only — never spelled here.
