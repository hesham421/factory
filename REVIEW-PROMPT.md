# Prompt — review the factory, the flow, and the two consumers

انسخ كل ما تحت الخط إلى محادثة جديدة.

---

You are reviewing a governance factory and the two repositories it serves. You
are not being asked to extend it. You are being asked to find where it is
**wrong, arbitrary, coupled, or hardcoded** — and to prove each finding by
running something, not by reading it.

## The three conditions, and what each actually means here

**1 — No arbitrariness.** Every value a tool acts on must be *declared* and
*derivable*. A value that appears in exactly one place, that nothing reads, or
that two places state differently, is a finding. So is a default nobody chose:
downstream it is indistinguishable from a decision.

**2 — No coupling.** A module must not need another to be loadable. The
specific failure this repo already made twice: a checker that imports the thing
it checks. Walk the import graph yourself.

**3 — No hardcode (Constitution C1).** No factory or domain literal in code: no
stage id, phase key, ID prefix, path, profile name, repo key, branch or
vocabulary term typed in Python. The same rule now extends to the consumer
repos' commands, skills and CI — they resolve those facts from a published file.

A fourth, implicit in all three: **a check that cannot see its answer must say
so**, never pass quietly. Several checks here were rewritten for exactly that.

## Scan before you judge — the ground may have moved

Do not trust a number below. Each was measured; re-measure it. Where reality
and this document disagree, **reality is right** — say so, and do not quietly
edit the document.

```bash
cd factory
.venv/bin/python governance-tools/gov.py lint        # expect 0 critical · 0 major · 0 minor
.venv/bin/python -m pytest governance-tools/tests -q # expect 262 passed, 1 skipped
```

Do not use bare `python3`. `.venv/bin/python` has jinja2 and yaml.

```
governance-tools : 11 modules, ~5.7k lines
shared repo      : 893 tracked files, 7 modules (CU FILE FIN MDL NOTE NOTIF SEC)
backend/frontend : 0 governance files outside the submodule
commands         : run-stage run-standalone run-pass gate approve analyze state
                   version tag fetch-inputs publish feedback waive-feedback sync
                   verify-split status structure archive split render lint new-domain
```

**zsh does not word-split an unquoted variable.** `for c in "a b"; cmd $c` passes
`"a b"` as ONE argument. This has already produced two false results in this
repo's history — a CI guard that always passed, and a smoke test that reported
six failures that were not there. Use `eval`, arrays, or `while IFS= read -r`.

## The architecture you are checking

**One home for governance. The three repos hold code and a pointer.**

```
governance-shared/                     ← the only place governance lives
  platform/
      modules-registry.json            ← factory publishes
      profile-summary.json             ← factory publishes: the facts consumers must not retype
      rules/                           ← rules every runtime reads
  {profile}/modules/{MOD}/
      P0…P3_2 · packages · _state      ← FACTORY writes
      api-docs/ · backend/             ← BACKEND writes
      frontend/                        ← FRONTEND writes

factory/    gov.py · factory.yaml · profiles · engines      — no module artifacts
backend/    source code + governance/shared (submodule)     — no governance/
frontend/   source code + governance/shared (submodule)     — no governance/
```

Each repo knows two things: **where to read, where to write.** Nothing else.

## What to verify, in order

### 1 — The lever holds

Every artifact path funnels through `config.dir()`, and `paths.external` decides
which keys resolve against the shared checkout. Verify that is still true: list
every caller of `dir()` and every direct `self.root /`, and say which — if any —
escape the funnel. Two that look like escapes are not: `dispatch.ingest()` and
`toolkit.splitter._clean_previous()` build root-relative paths, and hold only
because the shared checkout sits INSIDE the factory root. **That property is
load-bearing and undeclared in code.** Decide whether it should be checked.

### 2 — No cycles, and each module earns its place

```bash
# walk the AST, do not grep imports
```
Expected: `config` and `findings` depend on nothing; `contracts`, `idmodel`,
`publications` on `config` alone; zero cycles. If you find one, it is a finding
regardless of how harmless it looks — the two that existed here were both
introduced by someone adding a check.

### 3 — Hardcode, in all four places

- **Factory Python** — `lint` already enforces this (`scan_code_literals`).
  Verify the check is not blind: make it fail on purpose, then restore.
- **factory.yaml / profiles** — every key some code reads; every value some code
  reads. A declared value nothing reads is dead config and should be deleted,
  not kept "for later".
- **Consumer commands, skills, CLAUDE.md, CI** — these must resolve the profile
  and the phase list from `platform/profile-summary.json`. A phase key or the
  profile name typed as an authoritative value is a finding. Illustrative
  examples ("e.g. `INT-XM`") are not — judge by whether a tool would act on it.
- **Generated per-module commands** (`.claude/commands/<MOD>/…`) legitimately
  carry concrete paths: they are resolved output. Check they were regenerated,
  not hand-edited.

**The test that settles it:** create a second profile and show that nothing
outside `factory/profiles/` needs an edit. It has been done once and should
still hold.

### 4 — The flow, end to end

Trace and run it. Say where it would break, not where it might.

```
factory:  run-pass 1 → gate 1 → split                  (writes into shared)
          publish                                       (registry + profile summary)
backend:  ./scripts/governance pull
          /generate-module-setup MOD → /orchestrate-module MOD
          generate-api-docs → ./scripts/governance push  (api-docs, execution state)
factory:  fetch-inputs → run-pass 2 → gate 2 → split
frontend: ./scripts/governance pull → setup → orchestrate → push
factory:  feedback                                      (what execution found)
```

Check specifically:
- `fetch-inputs` really reads the backend's partition (it folds 11 / 10 / 4
  api-doc files for SEC / FIN / MDL — re-measure)
- nothing is copied between repositories at any point
- `gov.py sync` reports per-partition presence and stale consumer pointers,
  and the stale detection actually fires (force it)

### 5 — Read/write boundaries are enforced, not merely stated

- `CODEOWNERS` in the shared repo matches `GOVERNANCE-SHARED-DESIGN.md` §3.
  A mismatch is a finding in whichever is wrong — decide which.
- No consumer command writes outside its own partition. Check the placeholder
  forms too (`[MODULE]`, `$MODULE`, `<MOD>`): a path audit that matched only
  concrete module codes missed four real violations here.
- Each consumer's CI guard bites in **both** directions. Prove it.

### 6 — The feedback loop closes

The consumers record what implementation found that the plan could not know;
the factory reads it and a gate will not open over an unanswered item.

- `gov.py feedback` — currently **38 items unanswered** across FIN, NOTIF, CU,
  FILE, MDL, SEC. Re-measure.
- The status vocabulary is declared (`feedback.status`) because `resolution` was
  being written eleven ways. An unrecognised word must come back
  `UNRECOGNISED`, never bucketed by guess.
- `gov.py waive-feedback` is pinned to the items it saw. **Prove a gap recorded
  after a waiver still closes the gate.** If it does not, the waiver is an off
  switch and the gate is theatre.

### 7 — The checks are not theatre

For each of these, make it fail on purpose and restore:
`lint.scan_config` (4 disagreements) · the publication-builder check ·
`_commit`'s repo routing and pathspec limiting · the detached-HEAD guard ·
both consumers' CI guards · `verify-split`.

A check you cannot make fail is a check with nothing behind it. Say which.

## Known open state — do NOT report these as discoveries

| | |
|---|---|
| **F-29** | `/FIN:execute-backend-test` names `test_gen/backend-test-plan-fin.md`, which was never generated. Pre-existing. |
| **verify-split SEC backend/test** | 2 missing, 3 drifted blocks — packages were hand-edited by the backend during implementation and merged in deliberately. The mechanism is working; the drift is real and unresolved. |
| **`gov.py analyze`** | MAJOR findings on SEC/FIN/MDL/NOTE (C7.19, C8.3, C8.4, C9.8, C7.23). Content defects in plans, not tool defects. |
| **38 unanswered feedback items** | Real, and they will close `gate 1` for those modules. Intended. |

Report whether each is still what it says, not that it exists.

## What a finding must contain

```
## F-<n> — <one line: the defect, not the symptom>
Where   : file:line
Expected: what the repo's own rule says (quote it — constitution, design doc, contract)
Actual  : what you RAN, and its output
Fix     : FIXED (what changed) | OPEN (both options, and why the repo cannot settle it)
Status  : FIXED | OPEN | WONTFIX
```

A finding with no command behind it is an opinion. Say so if that is what it is.

## Rules while reviewing

- **Read-only by default.** Fix only what you can prove and re-verify.
- **Never weaken a check to make something pass.** A check that fires wrongly is
  the defect; a row with nothing behind it is deleted, never softened.
- **Re-run lint and the full suite after every change.** Baseline above —
  measure it yourself first.
- **Never force-push.** On a rejected push: fetch, check overlap, rebase.
- **`git checkout main` inside a submodule before writing to it.** `git submodule
  update` leaves a detached HEAD, and a commit there is lost silently. The
  factory now refuses that write; the consumers' `./scripts/governance` recovers
  it. Neither protects a raw `git -C` call you make yourself.
- **Do not regenerate pass 1 for any module.** Those are implemented and
  approved at the backend level.

## When you are done

Append to `governance-shared/{profile}/modules/NOTE/_state/smoke-findings.md`,
continuing the `## F-<n>` numbering (it currently ends at F-29). Do not start a
new file — the pipeline review, the migration and this review are one record.

Close with:

```
## REVIEW — factory, flow, boundaries

Scope       : <what you actually ran, and what you only read>
Arbitrary   : <n> — values declared once and read by nothing / stated twice
Coupling    : cycles <n> · modules that cannot load alone <list>
Hardcode    : factory <n> · consumers <n> · <where>
Flow        : <the step that would break first, and why — or "none found">
Boundaries  : <a write outside its partition? a CODEOWNERS/design mismatch?>
Checks      : <n> made to fail on purpose · <n> that could not be made to fail
Findings    : F-30 … F-<n> — <n> FIXED · <n> OPEN
Baseline    : lint <c/m/m> · tests <passed/skipped/failed>
Verdict     : does each repo know only where to read and where to write — yes / no, because <reason>
```
