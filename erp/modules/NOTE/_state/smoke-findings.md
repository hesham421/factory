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

