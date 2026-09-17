# Pipeline review — issues and fixes

One module (`NOTE` — Notes) driven through the governance pipeline to produce
evidence. **The findings are the deliverable; the module is scaffolding.**

| | |
|---|---|
| Subject | `NOTE` · 1 entity · 4 operations · 1 screen · 0 cross-module deps |
| Pipeline reached | pass 1 complete (P0 · P0.5 · P1 · P2 · P3.1) · **gate 1 ran and returned REVISE** |
| Findings | **22** — 11 FIXED · 10 OPEN · 1 WONTFIX |
| Baseline before | lint `0 critical · 0 major · 0 minor` · `237 passed, 1 skipped` |
| Baseline after | lint `0 critical · 0 major · 0 minor` · `242 passed, 1 skipped` (+5 regression tests) |
| Detailed log | [`erp/modules/NOTE/_state/smoke-findings.md`](erp/modules/NOTE/_state/smoke-findings.md) — full evidence per finding |

Every claim below has a command behind it. Nothing here was concluded by reading.

---

## 1 · The headline: a schema change closed every gate, and nothing noticed

**F-20 · FIXED.** `CAT-10 platform findings` was added to
`shared/REGISTRY-SCHEMA.md` in commit `31d82fa`. The derived platform artifact
`erp/project-registry.md` never grew the matching section — while still
asserting `Uncovered: none`, a claim that had become false. `C2.2
registry-agree` checks exactly that, and a gate opens only when analyze is
clean.

```
[MAJOR] C2.2 (registry-agree) project-registry — registry does not map categories ['CAT-10']
GATE CLOSED: analyze is not clean
```

Not caused by `NOTE`: **SEC and MDL report the identical finding**. Their
recorded `APPROVE`s are all dated 2026-09-10, before that commit — so no gate
had been re-run since, and the breakage sat invisible. **Since `31d82fa`, no
module's gate in this factory could open.**

The check behaved perfectly; it is why this is a finding and not a mystery.
What failed is that a change to a *shared* schema silently invalidated a
*derived* artifact, and the only thing that could see it fires at a gate nobody
re-runs between releases.

*Fix:* added the `## PLATFORM FINDINGS` section in the shape §4 specifies, plus
its category-map row. By hand rather than re-running P-1, which would
regenerate an artifact three shipped modules depend on to add one empty
section. `C2.2` now clears for NOTE, SEC and MDL alike.

---

## 2 · Governance that certified nothing

### F-8 · FIXED — the human-approval gate approved a PRD that did not exist

The Constitution calls this the point where *"the user approves the PRD file
itself"*. With the file deleted:

```
$ gov.py approve prd-approval -m NOTE -v 1 --by smoke-run
approved `prd-approval` for NOTE v1 by smoke-run      ← exit 0
                                  "artifact_sha": {}   ← the record it wrote
```

`_artifact_shas()` collects a hash only `if p.exists()`, and `approve()` never
looked at what came back. The one field that could have noticed recorded the
emptiness and told nobody.

*Fix:* `approve()` compares the shas against the gate's `after` stage
`produces` and returns BLOCKED, naming the path it looked at. The happy path
still approves and now provably binds the record to the bytes. No gate id,
stage id or filename is spelled — all from `CFG`.

### F-11 · FIXED — `analyze` read a dead copy and answered CLEAN

`_state/` is generated, so it must be a function of its sources. It was only
ever *added to*. Delete an artifact, re-run `gov.py state`, and it prints
`missing ['prd', …]` — it **knows** — while leaving `_state/current-prd.md` in
place. `analyze` then examines the stale copy:

| `_state/current-prd.md` | verdict |
|---|---|
| stale copy present | `0 critical · 0 major · 0 minor · CLEAN` |
| pruned | `[CRITICAL] C4.1 (exists) prd — 'prd' is missing or empty` · BLOCKED |

Two tools looking at one module, disagreeing, with only the quieter one
believed. `versioning.delta_only` makes the shape routine: a vN that REMOVES an
artifact would keep passing the existence clause off v1's snapshot.

*Fix:* `build_state` prunes any `current-*` not among the copies it just wrote,
reporting them in `StateReport.pruned` and `state.json`.

### F-1 · FIXED — `lint` reported clean over a check that never ran

`except ImportError: pass` around the render import. With a genuinely tampered
README present, `lint.run()` returned `{'CRITICAL': 0, 'MAJOR': 0, 'MINOR': 0}`.

*Fix:* charges `C1-render-unavailable` at the same rank a stale render charges,
so it blocks in the same place, and says outright that the verdict proves
nothing about freshness. The check was not weakened — it was made able to speak.

### F-19 · FIXED — a clause said "examined nothing" when it could not *read*

`C7.23` reported itself vacuous for NOTE while the line it needed sat in front
of it:

```
Operations   : search · list · create · read · update · deactivate
      ↓  re.split(r"[,;/]", …)     → one token
      ↓  {w for w in words if w.isalpha()}  → ∅   (spaces, "·")
      ↓  loop never runs, seen = 0 → "examined nothing"
```

The operation *words* are read `verbatim` so the factory never anticipates a
project's vocabulary — but the separator between them was a factory-side
literal, and `·` is what the engines render as their own list separator
throughout. "Empty by nature" and "I could not read this" are different
answers, and `analyze`'s own guidance tells the reader to distinguish them
while nothing let them.

*Fix:* the separator moves to `plan_vocabulary.operation_separators`, the
clauses name its address, the engine renders it, and an unreadable line is now
a **finding** rather than a silent zero. C7.23 on NOTE: 0 subjects → 6.
SEC/FIN/MDL byte-identical to baseline.

---

## 3 · The pipeline could not actually be driven

### F-13 · FIXED — `run-pass` could not resume, and the pass is designed to stop

`gates.prd-approval` blocks `P1`, which sits in the *middle* of pass 1's stage
list. So every module's pass 1 halts inside itself, and re-invoking `run-pass`
is the documented way forward. It re-dispatched from the first stage.

Observed live: the resume rewrote `_state/briefs/P0.md` and left all three P0
artifacts modified in `git status`. Two costs — the two dialogue stages paid
again, and **the PRD the human had just approved was rewritten underneath the
approval record that binds its sha (F-8)**.

*Fix:* a stage whose declared artifacts are all present is skipped and says so.
`run-stage` stays unconditional; `--redo` restores the old behaviour.

```
skipped P0: already produced platform-summary, module-registry, business-policies
skipped P0.5: already produced prd
```

*Stated limitation:* the rule is "artifacts exist", not "artifacts are
current". `state.is_fresh()` cannot close it — it compares one module-wide
mtime that every stage commit moves, so wiring it in would skip nothing at all.
A per-stage input digest is the real answer and was larger than this defect
warranted.

### F-9 · FIXED — a dialogue's artifact survived by luck

`res.written = ingest(previous)` ingested only the **last** round. A converging
dialogue's final round is a self-review that argues about the artifact instead
of re-emitting it — the normal shape, not an edge case.

| response | FILE blocks |
|---|---|
| `P0.5.response1.md` | 1 (the PRD) |
| `P0.5-round2.response2.md` | 0 — only `<!-- CONVERGED -->` |

Reported `wrote 0 file(s)` while committing a PRD. It existed only because the
runner is an agent with write tools that had saved it itself — *"written to
…/prd-note.md (as operator, not a file block)"*, in its own words. Under the
documented contract this stage would have produced nothing.

*Fix:* every round is ingested, oldest first. Verified against this run's own
recorded responses: last round alone recovers `[]`; both recover `prd-note.md`.

---

## 4 · The one-copy invariant

### F-15 · FIXED — a second api-docs copy lived in the factory, and had drifted

Three full `api-docs/` trees committed inside `erp/modules/{SEC,FIN,MDL}/`,
left from before the shared repo. The ownership table gives that path **one**
writer and one location.

```
$ diff -rq erp/modules/SEC/api-docs governance-shared/backend/modules/SEC/api-docs
  → index.md and all eight endpoint files differ
```

The factory-side copy is the **older** one — it lacks the `Contract ID:
API-SEC-###` lines the published copy carries, so a contract id resolved
against it would resolve to nothing. FIN and MDL were still byte-identical: the
drift was silent and partial, which is the state a second copy decays into.
Nothing read them, which is the kind that drifts unnoticed longest.

*Fix:* removed (25 files). No `api-docs` directory remains in the factory
outside the shared submodule; `fetch-inputs -m SEC` reports `unchanged` twice.

### F-5 · FIXED — the backend generator wrote `api_docs_path` into its own repo

`generate-module-setup.md` derived it from `$MBASE`, which Step 0.5 resolves to
`governance/modules/$MODULE/` — inside the backend repo. Every generated module
would declare a second api-docs location, and a vN module a per-version one,
for an artifact derived from the running app that has no version.

The contradiction was *inside one file*: its own STEP 0.3 and test-phase input
list already name the shared path, and the frontend twin has always been
correct. That is why the shipped `execution-state.json` files carry the right
path — each was fixed by hand after generation. That hand-correction was the
cost this defect charged, once per module, invisibly.

---

## 5 · Open — recorded with both options, not guessed at

| # | Issue | Why it is open |
|---|---|---|
| **F-18** | The P2 engine's canonical `DBF` form is one the ID model cannot read | See below — the obvious fix was **measured and rejected** |
| **F-6** | Two writers target one `execution-state.json` (`gov.py deliver` vs the backend generator) | Either the generator writes its own file (renames what two repos read) or it preserves the factory block (keeps two writers). Both defensible |
| **F-21** | The gate declares `review-per-engine` / `review-holistic` and dispatches neither | The additive fix removes the only manual step; but it is a design call about how much of a human gate may be pre-computed |
| **F-7** | `shared-pointer-fresh` promised CRITICAL in §6/§8, exists nowhere | `cmd_sync` prints "BEHIND" and returns OK; `fetch-inputs` never consults it. The gate belongs in `fetch-inputs`, but that is a new check, not a repair |
| **F-10** | The shipped artifact is not reconstructible from the archived run | Enforce the block contract, or drop it for agent runners and record per-artifact digests |
| **F-17** | `wrote N file(s)` means nothing — the block contract is honoured inconsistently | Follows from F-10; patching the message alone would paper over the same gap elsewhere |
| **F-4** | The no-hardcode scan does not cover severity names | Needs either an owner-exemption concept or a factory-side twin of `profile_term_sources` |
| **F-12** | A consumer repo must silently share its track's name (`CFG.repos[track]`, 6 sites) | Merge the two tables, or let a track name its repo. Undeclared either way |
| **F-14** | The phase list is restated twice in each consumer generator | Blocked on F-6: the data the generator should read is the data it destroys |
| **F-22** | The ALIGN self-check's COVERAGE prose goes stale and no machine check sees it | Stamp it like the verdict line, or guard it like `verdict-agrees` guards the count — the second keeps the author's reasoning about *why* a clause is empty |

### F-18 in full, because the measurement is the point

P2 blocked NOTE with 10 MAJOR — nine `DBF-NOTE-00n` *"registered in
`registry-db` but not defined in `db-script`"*. The db-script was **not wrong**.
It carries all nine exactly where §2 puts them, in the matrix that §2 calls
*"the single canonical source"*; §7's six-section output structure contains no
definition list at all. `idmodel._HEAD` only accepts an id at the start of a
line, and a table row starts with `|`.

**SEC and MDL pass only because they carry an extra section the engine never
asks for** — 104 such lines in SEC. The suite has been passing on a convention
that exists in the authored artifacts and nowhere in the template. NOTE, the
first module generated strictly from the template, is the first to expose it.

I implemented the obvious repair — teach `records()` that a table row's first
cell defines — and measured it before keeping it:

| | before | after |
|---|---|---|
| SEC | 62 MAJOR | **96** |
| MDL | 30 MAJOR | **67** |
| NOTE | 34 MAJOR | **61** |

A `Record`'s traces come from a `Traces:` line in its body; a table row carries
traces in *columns*. Recognising the row without reading its columns makes
every newly-defined id an untraced one. **Reverted.**

*Run unblocked by* adding the definition list to NOTE's own artifact, as every
shipped module carries. P2 → `CLEAN · 1 clause examined nothing (C6.3)`, and
C6.3 is XM-traces, correctly empty. No check was weakened; the artifact was
made to carry what the checker requires. The engine still does not ask for it,
so the next module blocks in the same place — which is what F-18 stays open for.

---

## 6 · Coupling — one cycle found and cut

`lint → render` (for `check_fresh`) and `render → lint` (for `Finding`), each a
function-local import whose comment explained the other. `render` needed **one
ten-line dataclass with zero dependencies** out of a 366-line checker — the
same shape as the `analyze → render` edge that `contracts.py` had already cut,
so it got the same treatment.

`findings.py`, 31 lines, one dependency, re-exported from `lint` so **no call
site changed**. Re-measured: **no cycles, the graph is a DAG.**

```
analyze   -> config contracts idmodel state toolkit      lint    -> config findings render toolkit
contracts -> config                                      render  -> config contracts findings toolkit
dispatch  -> config contracts idmodel state              state   -> config idmodel toolkit
idmodel   -> config                                      toolkit -> config
gov       -> analyze config dispatch idmodel lint render state toolkit
```

No other edge has that shape. Examined and left: `dispatch → contracts` (one
symbol, but `contracts` is already the thin module); `gov → everything` (gov is
the orchestrator — breadth is its job, and every edge is named symbols, not a
god-object reach).

---

## 7 · Extension points — measured

| To add … | Files outside its own artifacts | Where the literal lives |
|---|---|---|
| **a module** (`NOTE` was one) | **2** — `profiles/erp.yaml`, `README.md` (regenerated) | the profile. Correct home |
| a phase to a track | **3** — the profile + both consumer generators (F-14) | the two consumer copies have no home in config, and `lint` cannot see them |
| a contract clause | **2** — the contract frontmatter + the check function | none. Both are "the thing itself" |
| a third consumer repo | **1** — `factory.yaml`, plus the profile's track | none typed, but the repo key must equal the track name (F-12) |
| a second profile | **1** — `profiles/<id>.yaml`, then `render` | none. No `erp` literal survives outside generated blocks |

**Adding a module cost exactly two files, one of them regenerated.** That is the
bar ("config only, plus the thing itself") and the factory meets it. C1 is doing
the work it was built to do.

Everything else changed in this review was a **defect repair the run exposed**,
not a cost of extending — counting it as extension cost would be the wrong
lesson. Those were: `governance-tools/{findings.py, lint.py, render.py,
dispatch.py, state.py, gov.py, tests/test_silent_success.py}`,
`erp/modules/{SEC,FIN,MDL}/api-docs/**` (deleted),
`backend/.claude/commands/generate-module-setup.md`, `erp/project-registry.md`.

---

## 8 · What held

Recorded because "no finding" is only credible if the check that would have
produced one is named and was run.

- **Determinism — held, both halves.** `fetch-inputs -m SEC` reports
  `unchanged` on the **first** run as well as the second — the committed
  `_inputs/` fold is byte-identical to a fresh one, so no hand-edit has crept
  in. `gov.py state` twice leaves `git status` empty.
- **Empty-but-present phases — correct and legible.** All eight backend phases
  present; `INT-C` opens *"Empty by construction, present by requirement"* with
  a paragraph per SEC entity explaining why each is not an `XM`. A phase that
  ran and found nothing is unmistakable from one that was skipped.
- **The contract set — clean.** 12 contracts, 94 clauses, audited: zero naming
  an unimplemented check, zero unused checks, zero undeclared severities. An
  unknown check is a **finding**, not a skip.
- **The vacuous-clause reporter works** — it names every clause that examined
  nothing and explains how to read it. It is what led me to F-19.
- **The ambiguity rule works.** Six ADRs, all `ACCEPTED — non-breaking`, none
  BLOCKED. No stage wrote "STOP and ask the user".
- **The gate's own enforcement is real:** `if verdict == "APPROVE" and low:
  verdict = "REVISE"`. A reviewer cannot approve with any attribute below
  threshold, and the downgrade is announced.
- **Scope discipline held.** 1 `ENT`, 1 `SCR-REQ`, 18 `REQ`, 9 `DBF`, 0 `XM`.
- **Known condition 1 — the engine's half is sound.** NOTE carries the `Entity`
  line (12 lines / 10 API blocks); the P3.1 engine instructs it. *Correction to
  an earlier reading of mine:* carrying it did **not** make C7.23 able to judge
  — that was F-19, a different cause entirely.

---

## 9 · Gate 1 — the gate caught what no machine clause could

Analyze was clean, so the gate opened. I acted as the operator F-21 leaves in
the loop, ran the brief through the reviewer lane's own model, and completed
the gate with its JSON:

```
GATE pass-1: REVISE          (exit 1)
unambiguous 3 · verifiable 3 · complete 3 · consistent 2
singular 3 · feasible 3 · traceable 2
```

Every attribute is at or above `review.pass_threshold` (2), so this was the
reviewer's **own judgement**, not the automatic downgrade. Five ERP extra
checks PASS; six ADRs reviewed and confirmed accurate; all three vacuous
clauses confirmed empty *by nature* rather than by check failure — the exact
confirmation the vacuous-clause paragraph asks a human to make.

Its one MAJOR finding is now **F-22**, and it is a good one: the plan's
ALIGN-BE COVERAGE narrative names `C7.23` as vacuous, but the analyze report
bound to the gate lists `C6.3, C7.5, C7.5b` — C7.23 now examines 6 subjects.
The cause is mine: the plan was generated before I fixed F-19, and my fix
changed the analyze result underneath it. The plan honestly described the world
when it was written, and the one clause genuinely vacuous this run is named
nowhere in the artifact while a defect that no longer reproduces is explained
at length.

`gov.py` stamps the verdict *line* and `verdict-agrees` guards its *count*; the
coverage list beside it is author prose that nothing writes and nothing checks.
**`analyze` could not see this and the reviewer could** — which is the clearest
argument in this run for why the review lane is worth dispatching (F-21).

## 10 · Where the run stops, and why

The run stops after gate 1, at REVISE — which is the pipeline working, not
failing. Acting on it means regenerating one section of a disposable module's
plan; the pipeline question it would answer has already been answered.

Beyond that, `/orchestrate-module NOTE --auto` builds an actual Spring Boot
module across eight phases plus a test phase that needs a running backend —
hours of implementation work whose findings would be about *that* module's
code, not about the pipeline. The pipeline questions it would answer (F-6's
collision, F-5's fix in practice) are reachable much more cheaply by running
`/generate-module-setup NOTE` alone.

**Verdict:** the factory-side pipeline runs end to end once F-20 is fixed —
P0 → P0.5 → gate → P1 → P2 → P3.1 → gate 1, ending in a reasoned REVISE. Before
that fix it could not have, for any module. The three invariants:
**one-copy** violated and repaired (F-15, F-5); **determinism** held;
**no-weakened-check** held — every check that fired wrongly was fixed as the
defect, one proposed fix was measured and reverted for making things worse
(F-18), and no row was ever softened to let a step pass.

---

## Commits

| Repo | Commit | What |
|---|---|---|
| factory | `0063fab` | lint: a freshness check that cannot run says so (F-1, F-2, F-3) |
| factory | `594eaca` | dispatch: a dialogue's artifact survives the converging round (F-9, F-10a) |
| factory | `9ca6310` | state: a derived copy does not outlive its artifact (F-11) |
| factory | `a24a017` | run-pass: resume instead of re-running from the top (F-13) |
| factory | `72792b9` | drop the factory's stale duplicate api-docs (F-15) |
| factory | `9f4c320` | analyze: a clause that cannot read its subject says so (F-19) |
| factory | `e0acf03` | registry: the platform registry maps CAT-10 (F-20) |
| backend | `75fbced` | generate-module-setup: api_docs_path is the shared copy (F-5) |

`NOTE` is scaffolding and can be removed with
`gov.py archive -m NOTE --source <path>`.
