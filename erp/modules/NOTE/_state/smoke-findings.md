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

