# Prompt — move governance INTO the shared repo, leave the three repos clean

انسخ كل ما تحت الخط إلى جلسة delegate جديدة.

---

You are completing an architecture the last session got **half right**.

## What was built, and why it is not what was wanted

The shared repo exists and is mounted as a submodule in all three repos — but
only `api-docs` and the module registry moved into it. Everything else still
lives in the repositories, and the same artifacts exist in **two or three
copies**:

```
factory/erp/modules/SEC/      P0 P0_5 P1 P2 P3_1 P3_2 packages _state _inputs …
backend/governance/modules/SEC/   P0 P0_5 P1 P2 P3_1 packages …   ← delivered copies
frontend/governance/modules/SEC/  P0_5 P3_2 packages …            ← delivered copies

factory/erp/         702 files
backend/governance/  484 files
frontend/governance/ 230 files
governance-shared/    48 files     ← should hold nearly all of the above
```

`gov.py deliver` exists **only** to make those copies. The last session removed
exactly this duplication for `api-docs` and stopped there.

## The target

**One home for governance. The three repos hold code and a pointer.**

```
governance-shared/
  platform/                        ← FACTORY writes · all read
      rules/  modules-registry.json  profile-summary.md
  modules/{MOD}/                   ← one module's governance, in one place
      P0/ P0_5/ P1/ P2/ P3_1/ P3_2/    ← FACTORY writes
      decisions/  _state/  _inputs/     ← FACTORY writes
      packages/                         ← FACTORY writes (both tracks)
      api-docs/                         ← BACKEND writes
      backend/                          ← BACKEND writes (execution-state, test-api)
      frontend/                         ← FRONTEND writes (execution-state, tests)

factory/     gov.py · factory.yaml · profiles/ · engines/ · shared/ docs   — no module artifacts
backend/     source code                                                    — no governance/
frontend/    source code                                                    — no governance/
```

Each repo knows two things only: **where to read, where to write.** Nothing else.

### Why this is better than what exists

- **`deliver` disappears.** There is nothing to copy. A consumer reads the plan
  where it was written.
- **Drift becomes impossible**, not merely detected. Today three copies are kept
  in step by a command; one copy cannot diverge from itself.
- **A frozen version is a pinned commit.** A consumer that pins commit X sees
  exactly the plans, packages and api-docs that existed at X — plan and
  implementation cannot slide apart.
- **The backend and frontend become real writers**, not recipients. Each owns
  its own paths and writes them directly. That is what "shared" was supposed to
  mean.

## The lever — check this FIRST, it decides the shape of the work

Nearly every artifact path in the factory funnels through one method:

```python
# governance-tools/config.py
def modules_root(self)  -> Path:  return self.dir("modules")
def dir(self, key: str) -> Path:  return self.root / self.paths[key]
```

`module_root`, `version_root`, `artifact_path`, `decisions_dir`, `state_dir`,
`inputs_dir`, `packages_dir` all build on it. **If `dir()` can resolve certain
path keys against the shared checkout instead of `CFG.root`, this migration is
mostly configuration.** Verify that before planning anything: read
`config.py`, list every caller of `dir()` and every direct `self.root /` use,
and report which ones would need to move. If the funnel turns out to leak, say
so and plan around the leaks rather than pretending it is clean.

Suggested shape — confirm or improve it:

```yaml
paths:
  # resolved against the SHARED checkout, not this repo
  shared_root: governance-shared
  modules:   "modules"          # → <shared>/modules
  decisions: "modules/{MOD}/decisions"
  platform:  "platform"
```

Whatever you choose, it must be **declared, not computed in code** (C1).

## Order of work

Do not batch these. Each step ends green — `gov.py lint` clean and the suite at
its baseline — before the next begins.

| # | Step | Done when |
|---|---|---|
| 1 | Confirm the lever; write the partition + ownership table into `GOVERNANCE-SHARED-DESIGN.md` §2–§3 | the design says what the code will do |
| 2 | Teach `config.py` the shared root; `lint` + tests green with paths still pointing at the old place | a switch exists, nothing moved |
| 3 | Move `factory/erp/**` into `<shared>/modules/**` **with history** (`git subtree split` per module, as api-docs were moved) | content identical, history intact |
| 4 | Flip the config. Re-run `lint`, the suite, `analyze --scope all` for every module | the factory reads and writes the shared repo |
| 5 | Retire `deliver`: delete the command, its tests, `repos.*.deliver_to`, and the delivered copies in both consumers | nothing copies anything |
| 6 | Repoint both consumers: `execution-state.json`, the per-module commands, the two setup generators, both `orchestrate-module`, `api-verify-config.md`, `CLAUDE.md` ownership tables | no path in either repo names a local governance folder |
| 7 | `CODEOWNERS` in the shared repo enforces the ownership table from step 1 | a write outside an owned path is refused at review |
| 8 | Extend `gov.py sync` to report per-partition state and stale consumer pointers | one command shows who is behind |

## Rules

- **C1 above all.** Every path is a declared value in `factory.yaml` or the
  profile. If you find yourself typing a path in Python, that is the finding.
- **Move with history.** `git subtree split` per module, as api-docs were moved.
  Verify content byte-identical against the source before deleting anything.
- **One writer per path, enforced.** Not a convention — `CODEOWNERS`.
- **Never weaken a check to make a step pass.** A check that fires wrongly is
  the defect. A row with nothing behind it is deleted, never softened.
- **Re-run `lint` and the suite after every step.** Baseline: `0 critical · 0
  major · 0 minor`, and the test count as you measured it at the start — measure
  it yourself, do not trust a number written here.
- **Never force-push.** On a rejected push, fetch, check for overlap, rebase.
- Commit per step, in the repo that owns the change.

## Do not stop to ask

Decide, act, record, continue. If a decision cannot be grounded in the repo or
in `GOVERNANCE-SHARED-DESIGN.md`, record it as `OPEN` with both options and move
on to work that does not depend on it.

Two things are genuinely load-bearing — if either turns out to be false, **stop
and write down why**, because the plan rests on them:

1. `dir()` really is the funnel (step 1 verifies it).
2. A submodule can be written to by three repos without constant conflict —
   which holds only while partitions never overlap. If you find a path two
   parties must both write, that is a design flaw to report, not to work around.

## Before you start

There is uncommitted and unpushed work from the previous session:

```
factory            26 commits unpushed
backend             1 commit  unpushed
governance-shared   5 files   uncommitted
```

Review it, commit what belongs, push all four. Starting a migration on top of
unpushed work makes any rollback ambiguous.

Also read `factory/erp/modules/NOTE/_state/smoke-findings.md` — 22 findings from
the pipeline review, 10 still OPEN. Several touch what you are about to change:

- **F-6** two writers target one `execution-state.json` — the partition table in
  step 1 must answer this, not inherit it
- **F-14** the phase list is restated in both consumer generators — step 6
  touches those files; fix it there
- **F-12** a consumer repo key must silently equal its track name — step 2 is
  where that either gets a declared home or gets recorded as accepted
- **F-16** a fourth unpinned clone of the shared repo sits beside the three —
  this migration makes that clone dangerous; resolve it

## When you are done

**Append to the same file** — `factory/erp/modules/NOTE/_state/smoke-findings.md`
(it moves to `<shared>/modules/NOTE/_state/` during step 3; append to it wherever
it then lives). Do not start a new file: the findings from the run and the
findings from the migration belong in one record.

```
## MIGRATION — governance into the shared repo

Steps completed : <n>/8 — stopped at <step> because <reason>, or "all 8"
Repos cleaned   : factory <before>→<after> files · backend <b>→<a> · frontend <b>→<a>
Shared repo     : <n> files · <n> modules · partitions <list>
deliver         : retired / still present because <reason>
Findings        : F-23 … F-<n> — <n> FIXED · <n> OPEN · <n> WONTFIX
Prior findings  : <which of F-1..F-22 this migration closed>
Baseline        : lint <c/m/m> · tests <passed/skipped/failed>
Coupling        : cycles <n> · edges cut <list>
Verdict         : each repo now knows only where to read and where to write — yes / no, because <reason>
```

Keep using the same `## F-<n>` block format the file already uses, continuing
the numbering from F-22.
