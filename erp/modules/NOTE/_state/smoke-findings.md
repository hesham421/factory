# Smoke run — pipeline review findings

Subject: module `NOTE` (Notes) · one entity · four operations · one screen.
Baseline measured before any change: `lint 0 critical · 0 major · 0 minor` ·
`237 passed, 1 skipped`.

## F-1 — `lint` reported a clean verdict over a freshness check that never ran
Where   : governance-tools/lint.py:334 (`except ImportError: pass`)
Expected: invariant 3 — a check that cannot see the answer says so. An
          unrunnable `C1-stale-render` must be reported, at a blocking rank.
Actual  : the import of `render` was wrapped in `try/except ImportError: pass`.
          Reproduced by stubbing the import and tampering a rendered block in
          README.md: a genuinely stale generated file was present and
          `lint.run()` returned `{'CRITICAL': 0, 'MAJOR': 0, 'MINOR': 0}` —
          0 findings. The clean verdict was produced by a check that examined
          nothing, which is the precise failure the invariant names.
Fix     : the `except` now appends `C1-render-unavailable` at
          `sev(RENDER_UNAVAILABLE_RANK)` (rank 1 — the same rank the check it
          replaces charges, so it blocks exactly where a stale render would)
          and states in its message that the verdict says nothing about
          freshness. The check was NOT weakened — it was made able to speak.
          Pinned by `tests/test_silent_success.py::
          test_lint_says_so_when_it_cannot_run_the_freshness_check`, in the
          suite that already owns this defect class.
Status  : FIXED

## F-2 — `lint` ⇄ `render` import cycle, held open by two lazy imports
Where   : governance-tools/lint.py:347 · governance-tools/render.py:254
Expected: the module graph is a DAG — a cycle means neither module can be
          changed alone.
Actual  : `lint` imported `render` (for `check_fresh`) and `render` imported
          `lint` (for `Finding` — one 10-line dataclass with zero
          dependencies, out of a 366-line checker). Both sides were function-
          local imports whose comments explained each other
          ("local import: lint imports render lazily too"), i.e. the cycle was
          known and worked around rather than cut.
Fix     : the same cut the `analyze`→`render` edge got: `findings.py`
          (31 lines, one dependency: `dataclasses`) now holds `Finding`;
          `lint` re-exports it, so no call site changed. `render` imports
          `findings` at module top and no longer imports a checker at all.
          Graph re-measured after the cut: no cycles.
Status  : FIXED

## F-3 — `render.check_fresh` spelled a severity name as a literal
Where   : governance-tools/render.py:258
Expected: C1/C2 — the severity vocabulary and its order live in
          factory.yaml → `analyze.severities`; a checker charges by RANK.
          `lint.py` states this in its own imports ("lint charges by rank,
          never by a name spelled here") and every other checker obeys it.
Actual  : `Finding("MAJOR", "C1-stale-render", …)` — the string `MAJOR` typed
          into code. Narrowing or reordering `analyze.severities` would leave
          this one finding charged at a name that may no longer be declared,
          and `severity_rank()` sorts an undeclared severity after every
          declared one, so it would silently stop blocking.
          `lint.code_paths` does not catch it: that scan looks for stage ids,
          phase keys and ID prefixes, not severity names.
Fix     : `sev(STALE_RENDER_RANK)` with the rank named once as a module
          constant and documented. Found by inspection, not by a check — the
          gap in `scan_code_literals` is itself recorded as F-4.
Status  : FIXED

## F-4 — the no-hardcode scan does not cover severity names
Where   : governance-tools/lint.py `scan_code_literals` · factory.yaml `lint.code_paths`
Expected: C2 says engines, docs, reviewers and tools reference config keys,
          "never literals — no stage id, phase key, ID prefix, stack name,
          path, model name or domain word". `analyze.severities` is a
          factory fact of exactly the same kind, and it decides what blocks.
Actual  : the code scan enumerates stage ids / phase keys / ID prefixes only.
          F-3 was a severity name sitting in `governance-tools/` — inside
          `lint.code_paths` — for as long as that file has existed, and lint
          passed `0 critical · 0 major · 0 minor` over it every run.
Fix     : OPEN — deliberately not fixed here, because the two defensible
          options change different things and neither is groundable in the
          repo as written:
          (a) add `analyze.severities` to the code-literal scan. Cheap, but it
              would fire on `toolkit/common.py`, which must name them to
              resolve a rank, so it needs an owner-exemption concept that does
              not exist yet;
          (b) extend `lint.profile_term_sources` with a factory-side twin
              (`factory_term_sources`) so any factory.yaml value can be
              declared scannable as data. Larger, and the right shape, but it
              is a new config surface and C5 says variability is declared in
              `_schema.yaml` — which today validates profiles only.
          Recorded rather than guessed at. F-3's instance is fixed either way.
Status  : OPEN

## F-5 — the backend generator writes `api_docs_path` into the backend repo
Where   : backend/.claude/commands/generate-module-setup.md:91 and :190
Expected: invariant 1 — api-docs exist in exactly one place. The ownership
          table (GOVERNANCE-SHARED-DESIGN.md §3) gives `backend/modules/*/
          api-docs/` in the SHARED repo one writer, and factory.yaml
          `repos.backend.publishes.api-docs` resolves against
          `reads_from: shared`. So a generated `api_docs_path` must read
          `governance/shared/backend/modules/{MOD}/api-docs/`.
Actual  : both lines derived it from `$MBASE`, which Step 0.5 of the same file
          resolves to `governance/modules/$MODULE/` (or `…/v$N/`) — a path
          INSIDE the backend repo. Every module generated by this command
          would declare a second api-docs location, and a vN module would
          declare a per-version one, where api-docs are derived from the
          running app and have no version at all.
          The contradiction is INSIDE this one file (C3): its own STEP 0.3
          and test-phase input list (:408, :448) already name
          `governance/shared/backend/modules/[MODULE]/api-docs/`. The
          frontend twin, `generate-frontend-module-setup.md:218`, has always
          written the shared path — the backend generator was the only
          outlier, which is why the shipped `execution-state.json` files
          carry the correct shared path: they were corrected BY HAND after
          generation. That hand-correction is the cost this defect was
          charging, once per module, invisibly.
Fix     : both lines now name the shared path directly and no longer derive
          from `$MBASE`, with the reason stated inline (one copy; not
          version-suffixed). Verified by re-reading the generated
          `execution-state.json` for NOTE after `/generate-module-setup`.
Status  : FIXED

## F-6 — two writers target one `execution-state.json`
Where   : governance-tools/gov.py:755 (`cmd_deliver`) vs
          backend/.claude/commands/generate-module-setup.md:182 (Step 2)
Expected: GOVERNANCE-SHARED-DESIGN.md §1 — "one writer per path, no
          exception" — and §3's ownership table, which gives
          `*/execution-state.json` exactly one writer: **the factory**, via
          `gov.py deliver`. factory.yaml agrees:
          `delivery.execution_state.schema` is annotated "generated by
          `gov.py deliver`, never hand-written".
Actual  : both tools resolve to the SAME path.
          `cmd_deliver` writes `dest / "execution-state.json"` where
          `dest = <backend>/governance/modules/{MOD}`; the generator's Step 2
          writes `$MBASE/execution-state.json`, and Step 0.5 resolves
          `$MBASE` to `governance/modules/$MODULE/`. Identical.
          The schemas are disjoint, so this is a replacement, not a merge.
          Factory fields: module, version, track, profile,
          markers_schema_version, packages, phases, traceability, analyze,
          gate, generated_at. Generator fields: module, generated_at,
          current_phase, current_sub, api_docs_path, phases, test_phases,
          blocked, deferred_xm, api_doc_gaps.
          Measured on all three delivered modules — every one carries the
          GENERATOR's key set and none of `version`, `track`, `profile`,
          `packages`, `traceability`, `analyze`, `gate`:
            SEC/FIN/MDL -> [api_doc_gaps, api_docs_path, blocked,
            current_phase, current_sub, deferred_xm, generated_at, module,
            phases, test_phases]
          What is lost is precisely the delivery's audit trail: which gate
          verdict and which analyze counts the module passed, and which
          toolchain built it. The pipeline REQUIRES the overwriting command
          to run (orchestrate refuses a module without it), so the loss is
          not a mishap — it is the designed order of operations.
          NOT yet proven as a live overwrite: SEC/FIN/MDL predate this
          `cmd_deliver` (their file's first git revision is already the
          generator's schema, in the repo's `first` commit), so for them the
          factory record never existed rather than being destroyed. NOTE is
          the first module where both tools run in sequence — verified below
          in F-6a once `deliver` and `/generate-module-setup` have both run.
Fix     : OPEN — two defensible repairs, and the choice is not groundable in
          the repo as written:
          (a) STRUCTURAL: the generator writes its own file (runtime progress
              is a different concern from the delivery record), restoring one
              writer per path literally. Correct, but it renames a file that
              `orchestrate-module.md` and every generated per-module command
              in TWO repos reads, so it cannot be done from the factory side
              alone.
          (b) PRESERVING: the generator reads the delivered file and carries
              the factory-owned block forward under its own key, adding only
              runtime fields. Restores the audit trail today and is
              reversible, but leaves two writers on one path — the letter of
              §1 still broken, the consequence fixed.
          Recorded with both, per the standing rule, rather than guessed at.
Status  : OPEN

## F-7 — `shared-pointer-fresh` is promised as CRITICAL and does not exist
Where   : GOVERNANCE-SHARED-DESIGN.md §6 and §8 vs governance-tools/gov.py:673
Expected: §8 names "building on stale api-docs without knowing" the biggest
          risk of the whole design and gives its mitigation as
          `shared-pointer-fresh` **(CRITICAL)**. §6 lists it, `partition-writer`
          and `api-docs-reachable` as the checks the factory's two-sided
          awareness buys.
Actual  : none of the three exists anywhere in the repo — grepped across the
          factory outside `history/` and `_archive-v5/`, the only hits are
          the four lines of the design document that promise them.
          What stands in for the first is an advisory print in `cmd_sync`:
            if behind != "0": _say("BEHIND — a consumer pinning this commit
                                    is building on stale inputs …")
            return OK
          — a CRITICAL mitigation implemented as a message with exit code 0.
          `cmd_fetch_inputs` is where it would matter, and it never consults
          it: it reads the shared checkout's working tree at whatever commit
          it happens to be on, with `--pull` optional, and folds it into
          `_inputs/` without a word about freshness. A stale fold is
          therefore indistinguishable from a current one at the one command
          that turns a pointer into an input.
          Likewise the stale consumer pointers `cmd_sync` collects into
          `stale` are printed and never reach the exit code.
Fix     : OPEN — not fixed, and deliberately not fixed by making `sync` exit
          non-zero, which would be the weakening-shaped move in reverse:
          `sync` is documented as a reporter (`sync --push` is the writer),
          and changing its exit code silently breaks any caller that treats
          0 as "ran". The check belongs where the risk is — a freshness gate
          inside `cmd_fetch_inputs`, which already returns BLOCKED for a
          missing input and would return it for a stale one. That is a new
          check, not a repair of an existing one, and the severity it should
          carry (§8 says CRITICAL; `analyze.blocking` makes MAJOR block too)
          is a policy call the documents do not settle.
Status  : OPEN

## F-8 — the human-approval gate approved a PRD that did not exist
Where   : governance-tools/gov.py:437 `approve()` · :452 `_artifact_shas()`
Expected: CONSTITUTION.md §2 — this gate is where "the user approves the PRD
          **file itself**". The approval record carries `artifact_sha`, a
          field whose whole purpose is to bind the decision to the bytes
          approved.
Actual  : with `erp/modules/NOTE/P0_5/prd-note.md` deleted,
            gov.py approve prd-approval -m NOTE -v 1 --by smoke-run
          printed `approved 'prd-approval' for NOTE v1 by smoke-run`, exited
          0, and wrote a record whose `artifact_sha` was `{}`.
          `_artifact_shas()` collects a hash only `if p.exists()`, and
          `approve()` never looks at what came back — so the one field that
          could have noticed recorded the emptiness and told nobody. The gate
          the Constitution calls a human decision point certified nothing,
          and the pass continued into P1 on that certificate.
Fix     : `approve()` now compares the shas it collected against the
          `produces` list of the gate's `after` stage and returns BLOCKED,
          naming the missing artifact and the path it looked at, when any is
          absent. Nothing was softened: the happy path still approves and now
          provably binds the record to the file
          (`artifact_sha: {'prd': '2bbcf3d33900d215…'}`). Values all come
          from `CFG.gate()` / `CFG.stage().produces`; no gate id, stage id or
          filename is spelled. Pinned by
          `test_the_human_approval_gate_refuses_to_approve_an_absent_artifact`.
Status  : FIXED

## F-9 — only the last dialogue round was ingested; the artifact survived by luck
Where   : governance-tools/dispatch.py:344 (`res.written = ingest(previous)`)
Expected: a dialogue stage's artifacts are what the run produced across its
          rounds. The documented runner contract is that the response carries
          the work as `<<<FILE: path>>>` blocks and `dispatch.ingest()` writes
          them.
Actual  : `ingest()` was called on `previous` — the LAST round — only, so
          every earlier round's blocks were discarded. The triggering shape is
          not exotic, it is the NORMAL one for a converging dialogue: the
          final round is a self-review that argues about the artifact instead
          of re-emitting it. P0.5 of this run was exactly that —
          `P0.5.response1.md` carries one `<<<FILE: …/prd-note.md>>>` block,
          `P0.5-round2.response2.md` carries none and only
          `<!-- CONVERGED -->` — and the orchestrator duly reported
          `dispatched P0.5: 2 round(s), converged=True, wrote 0 file(s)`
          while committing a PRD.
          The PRD existed only because the runner is `claude -p
          --permission-mode bypassPermissions`, an agent holding write tools,
          which had saved the file itself. It said so in the response:
          "Round 2 — written to `erp/modules/NOTE/P0_5/prd-note.md`
          (as operator, not a file block)." Under the contract as documented —
          a runner that only answers text — this stage would have produced
          nothing at all.
Fix     : `dispatch()` now ingests every round, oldest first, so a file
          emitted once survives the rounds that do not mention it. Verified
          against this run's own recorded responses: ingesting the last round
          alone recovers `[]`; ingesting both recovers `prd-note.md`.
Status  : FIXED

## F-10 — the shipped artifact is not reconstructible from the archived run
Where   : same two response files as F-9
Expected: a dialogue's briefs and responses are archived under
          `_state/briefs/` so a run can be re-derived and audited.
Actual  : found while fixing F-9, and it is why that fix needed a second
          half. Round 2's amendments — a `القصة :` line per story, `Status :
          DRAFT`, the corrected trace on US-NOTE-001 — are in the artifact on
          disk and in **no file block anywhere**: the round-1 block is the
          pre-amendment draft (11756 bytes vs the shipped 15186; `القصة`
          appears 7 times on disk and 0 times in the block). The archived
          responses therefore do not contain the delivered artifact, and a
          naive replay of them REPLACES it with a superseded draft — which
          the first version of the F-9 fix did, silently.
Fix     : partially, and the remainder is OPEN.
          FIXED half — `ingest()` no longer overwrites a target whose mtime is
          newer than the response carrying the block and whose content
          differs: a response cannot supersede a write that happened after it.
          Verified both directions: with the shipped artifact present nothing
          is ingested and its 15186 bytes are preserved; with it absent the
          round-1 block is recovered. Pinned by two tests
          (`test_a_file_emitted_in_an_earlier_round_is_not_discarded`,
          `test_a_block_never_overwrites_a_newer_out_of_band_write`).
          OPEN half — the provenance gap itself. The runner contract asks for
          file blocks; the runners actually dispatched to hold write tools and
          may legitimately not use blocks. Two ways to close it, neither
          groundable in the documents as written:
          (a) enforce the contract — dispatch refuses a round that changed a
              declared artifact on disk without emitting its block. Honest,
              but it makes the factory police a CLI it does not own;
          (b) drop the contract for agent runners and record a content hash of
              each declared artifact per round instead, so provenance is a
              digest chain rather than a transcript.
Status  : OPEN

## F-11 — `_state/` was added to and never pruned, so `analyze` read a dead copy
Where   : governance-tools/state.py:189 `build_state` · reported via
          governance-tools/analyze.py (C4.1 `exists`)
Expected: invariant 2 — a derivation is deterministic, a function of its
          sources. `factory.yaml` says `versioning.current_state: generated`
          and "engines read `_state` only".
Actual  : `build_state` wrote a `current-*` for every artifact it found and
          removed none for artifacts it did not. Deleting `prd-note.md` and
          re-running `gov.py state` printed `missing ['prd', …]` — it KNEW —
          and left `_state/current-prd.md` in place. `analyze`, which reads
          `_state`, then examined the dead copy and reported
          `0 critical · 0 major · 0 minor · CLEAN`, where with the copy gone
          it correctly reports `[CRITICAL] C4.1 (exists) prd — 'prd' is
          missing or empty` and BLOCKED. Two tools looking at one module,
          disagreeing, with only the quieter one believed.
          `versioning.delta_only: true` makes this routine rather than
          exotic: a vN whose change manifest REMOVES an artifact would keep
          passing the existence clause off v1's snapshot.
          Worth recording that the surrounding machinery is SOUND and was not
          the defect: `C4.1 exists` fires correctly, and the vacuous-clause
          reporter does its job, printing "1 clause(s) examined nothing
          (C4.4)" with a paragraph on how to read it. Invariant 3 is well
          served here — the input to it was stale.
Fix     : `build_state` now prunes any `current-*` in the state dir that is
          not among the copies this run wrote, and reports them in
          `StateReport.pruned` and in `state.json`. The glob comes from
          `naming.current_state_file`, so no filename is spelled. Pinned by
          `test_a_derived_state_copy_does_not_outlive_its_artifact`.
Status  : FIXED

## F-12 — a consumer repo must silently share its track's name
Where   : governance-tools/gov.py:739, 740, 855, 962, 966, 1017
Expected: an extension point should be config only, and the config should say
          what it requires. Adding a third consumer repo is one of the five
          extension questions this review is asked to answer.
Actual  : six call sites index the repo table with a TRACK name —
          `CFG.repos[track]`, `CFG.repo_checkout(track)` — so a track and its
          consumer repo must carry the identical key. Nothing declares that
          and nothing checks it. Measured on the live config:
            tracks : ['backend', 'frontend']
            repos  : ['backend', 'frontend', 'shared']
            tracks with no repo of the same name: []
            repos that are not tracks           : ['shared']
          A track whose repo key differs fails with an unhandled
          `KeyError: 'mobile'` rather than a message naming the two tables
          that disagree — and the profile already ships
          `stack.mobile.framework`, so a third track is a live prospect, not
          a hypothetical.
          This is NOT a C2 violation: no literal is typed, the value is read
          from config. It is an undeclared invariant between two config
          tables, which `profiles/_schema.yaml` cannot catch because C5 scopes
          it to profiles — `factory.yaml`'s own structure is validated by
          nothing.
Fix     : OPEN. The one-line repair (a lint rule asserting every
          `tracks.<k>` has a `repos.<k>`) is easy but picks a winner between
          two readings the documents do not settle: either a track IS a
          consumer repo and the tables should be merged, or a track MAY name
          its repo (`tracks.<k>.repo`, defaulting to `<k>`), which is the more
          flexible shape and the larger change. Recorded with both rather
          than guessed at.
Status  : OPEN

## F-13 — `run-pass` could not resume, and the pass is designed to stop
Where   : governance-tools/gov.py:343 `run_pass` (`for sid in p["stages"]`)
Expected: `gates.prd-approval` has `blocks: [P1]`, and pass 1's stages are
          `[P0, P0.5, P1, P2, P3.1]`. So EVERY module's pass 1 halts in the
          middle of itself at a human-approval gate, and re-invoking
          `run-pass 1` after the approval is the documented way forward —
          the smoke prompt's own command list does exactly that. Resuming is
          the normal path, not an edge case.
Actual  : `run_pass` looped over `p["stages"]` unconditionally, with no
          completion check anywhere in it or in `run_stage`. The resume
          re-dispatched P0 from scratch. Observed live: after
          `approve prd-approval`, the second `run-pass 1` rewrote
          `_state/briefs/P0.md` at 16:10:15 and left all three P0 artifacts
          modified in `git status` before it was stopped.
          Two costs, the second serious:
          · the two dialogue stages are the most expensive in the pipeline
            (~4 opus dispatches) and were paid again for no new information;
          · it rewrites the PRD the human has just approved. The approval
            record binds `artifact_sha` to those exact bytes (F-8), so a
            resume silently leaves an approval pointing at content that no
            longer exists — the gate would still read as passed.
Fix     : `run_pass` now skips a stage whose non-optional `produces` are all
          present and non-empty, printing what it skipped and how to redo it.
          `run-stage <id>` stays unconditional — that is how a single stage is
          re-run — and `--redo` restores the old whole-pass behaviour.
          Nothing is spelled: the artifacts come from `CFG.stage().produces`.
          Verified on the live run: the resume printed
            skipped P0: already produced platform-summary, module-registry,
                        business-policies
            skipped P0.5: already produced prd
          and the approved PRD's md5 was unchanged.
Status  : FIXED

## F-14 — the track's phase list is restated in both consumer generators
Where   : backend/.claude/commands/generate-module-setup.md:129 and :211
          frontend/.claude/commands/generate-frontend-module-setup.md:168 and :232
Expected: the phase vocabulary is a PROFILE fact
          (`profile.tracks.<track>.plans.<plan>.phases`, C1). Adding a phase to
          a track should be a profile edit plus the phase's own content.
          `GOVERNANCE-SHARED-DESIGN.md` §7 lists both generators under "does
          not change" and credits C1 with keeping the blast radius small.
Actual   : each generator restates the whole ordered list twice — once as
          "Expected phases, in strict order" and once as the `gated_by_phases`
          array of the test phase (`grep -c` returns 2 in each file).
          The first is partly defensive: the surrounding text says to derive
          phases from the delivered package folders and "only include ones
          actually present", so the list reads as a sanity ordering. The
          second is not — `gated_by_phases` is written verbatim into
          `execution-state.json` and decides which phases must be COMPLETE
          before the test phase may run. A phase added to the profile and
          delivered in the package would be scanned into `phases` by the
          generator and silently ABSENT from `gated_by_phases`, so the test
          phase would run without it.
          Measured extension cost for "add a phase to a track": 1 profile file
          + 2 consumer files in 2 repos, of which the consumer half is invisible
          to `gov.py lint` — `lint.scan_paths` covers the factory only, so
          nothing in the factory can see these two files drift.
Fix     : OPEN. The clean repair is for `gated_by_phases` to be derived rather
          than typed: `gov.py deliver` already writes `phases` into the
          execution-state it delivers (`delivery.execution_state.schema`), so
          the generator could read the delivered list instead of restating it.
          That is blocked on F-6 — the generator currently OVERWRITES that
          delivered file rather than reading it, so the data it needs is the
          data it destroys. Recorded together; F-6 is the one to settle first.
Status  : OPEN

## F-15 — a second api-docs copy lived in the factory, and it had drifted
Where   : factory/erp/modules/{SEC,FIN,MDL}/api-docs/ (25 files, git-tracked)
Expected: invariant 1 — api-docs exist in exactly one place. The ownership
          table (§3) gives `backend/modules/*/api-docs/` one writer (the
          backend) and one location (the shared repo). §2 states the point
          outright: one source, not two, so drift is structurally impossible
          rather than merely visible.
Actual   : three full `api-docs/` trees — an `index.md` plus an `endpoints/`
          folder each — were committed inside the factory's own module
          folders, left over from before the shared repo existed.
          They had already drifted, which is the argument for one copy made
          concrete rather than hypothetically:
            diff erp/modules/SEC/api-docs governance-shared/backend/modules/SEC/api-docs
          reports all eight endpoint files and the index differing. The
          factory-side copy is the OLDER one — it lacks the
          `Contract ID: API-SEC-###` lines the published copy carries
          (index 9811 bytes vs 10785), so a contract id resolved against it
          would have resolved to nothing. FIN and MDL were still
          byte-identical: the drift was silent and partial, which is the state
          a second copy decays into rather than an accident.
          Nothing read them — `fetch-inputs` resolves
          `repos.backend.publishes.api-docs` against `reads_from: shared`,
          which is `factory/governance-shared/backend/modules/{MOD}/api-docs`,
          confirmed by resolving the path through `CFG` directly. So this was
          a dead second copy, which is the kind that drifts unnoticed longest.
Fix     : removed (`git rm -r`). Verified after: no `api-docs` directory
          remains anywhere in the factory outside the shared submodule, and
          `fetch-inputs -m SEC` reports `unchanged` twice in a row.
Status  : FIXED

## F-16 — a fourth, unpinned clone of the shared repo sits beside the three
Where   : <workspace>/governance-shared/ (workspace root)
Expected: §4 — the shared repo reaches each of the three repositories as a
          PINNED submodule, and the pin is what makes a delivered version
          provable: "any release knows what it was built on". Three consumers,
          three pointers, one commit.
Actual   : there are four checkouts, not three. The factory, backend and
          frontend each mount it correctly as a submodule, all three pinned to
          `7df6f10`. Beside them sits a plain clone at the workspace root that
          is a submodule of nothing and is pinned by nothing.
          It is at `7df6f10` too, so nothing is wrong today, and that is
          precisely the problem: it is the one copy no `git submodule status`
          will ever report as `+` (differs from its pinned commit) — the check
          §8 names as the mitigation for the biggest risk, and the one
          `cmd_sync` collects into `stale`. A commit made there is invisible to
          every freshness signal the design has.
          Its working tree is already dirty (five untracked `.DS_Store` files),
          which is evidence it is a place someone works, not a build artifact.
Fix     : WONTFIX — not mine to delete. It lies outside all three repositories,
          so removing it is a workspace decision, and it may be the clone used
          to push (the submodules are `shallow = true`, which makes pushing
          from them awkward — a plausible reason it exists). Recorded so the
          decision is made rather than inherited. If it IS the push clone, the
          honest fix is to say so in `GOVERNANCE-SHARED-DESIGN.md` §4, which
          today describes three checkouts and knows nothing of a fourth.
Status  : WONTFIX

