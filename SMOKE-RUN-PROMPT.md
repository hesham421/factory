# Prompt — full-auto smoke run of the whole pipeline (module `NOTE`)

انسخ كل ما تحت الخط إلى جلسة delegate جديدة.

---

You are running a **full-auto end-to-end smoke test** of this governance
pipeline, from the factory through the shared repo into both consumer repos.

**Do not come back to ask anything. Decide, act, record, continue.** The only
thing you report is the final findings file. If something is genuinely
undecidable, write it down as a finding and keep going with the rest.

## The subject: one deliberately tiny module

`NOTE` — *Notes*. A user writes a short note and reads their own notes back.

Keep it at exactly this size, because the point is to exercise the **pipeline**,
not to design a product. A bigger module costs more and finds nothing extra:

- **one entity**: note (id, title, body, owner, created/updated audit fields, active flag)
- **four operations**: create · update · deactivate · search (own notes only)
- **one screen**: a list with a create/edit form
- **one permission set** on that screen
- **zero cross-module dependencies** — no `XM`, no lookups, no foreign data

If any stage starts to grow this beyond one entity and one screen, that is
itself a finding: record it and hold the scope.

## Setup

```bash
cd "<repo root>/factory"
PY=.venv/bin/python

# `NOTE` is not in the profile's module vocabulary yet — add it, minimally:
#   profiles/erp.yaml → vocabulary.module_prefixes → NOTE: Notes
# then confirm the factory sees it:
$PY governance-tools/gov.py lint
```

Full-auto dispatch (the runner contract is in `governance-tools/dispatch.py`):

```bash
export GOV_RUNNER=cmd
export GOV_RUNNER_CMD='cat {brief} | claude -p --model {model} --permission-mode bypassPermissions > {out}'
```

The brief already tells each implementer to answer with
`<<<FILE: path>>> … <<<END FILE>>>` blocks; `dispatch.ingest()` writes them.
Available placeholders: `{brief} {implementer} {provider} {model} {effort} {out}
{lane} {read_only_flag}`.

## The run, in order

Every step is either a dispatched stage or a mechanical `gov.py` call. After
**each** one: read the output, and if it failed, diagnose and fix before moving
on — a later stage standing on a broken earlier one teaches nothing.

```bash
$PY governance-tools/gov.py run-pass 1 -m NOTE -v 1        # P0 · P0.5 · P1 · P2 · P3.1
$PY governance-tools/gov.py approve prd-approval -m NOTE -v 1 --by smoke-run   # gate id is positional
$PY governance-tools/gov.py gate 1 -m NOTE -v 1
$PY governance-tools/gov.py split --track backend -m NOTE -v 1
$PY governance-tools/gov.py deliver --track backend -m NOTE -v 1
```

Then the **backend** repo implements it (`/orchestrate-module NOTE`), publishes
api-docs with `/generate-api-docs NOTE` — which must land in
`governance/shared/backend/modules/NOTE/api-docs/` — and pushes the shared repo.

Back in the factory:

```bash
$PY governance-tools/gov.py sync                            # shared state + consumer pointers
$PY governance-tools/gov.py fetch-inputs -m NOTE -v 1        # folds the published folder
$PY governance-tools/gov.py run-pass 2 -m NOTE -v 1          # P3.2
$PY governance-tools/gov.py gate 2 -m NOTE -v 1
$PY governance-tools/gov.py split --track frontend -m NOTE -v 1
$PY governance-tools/gov.py deliver --track frontend -m NOTE -v 1
```

Then the **frontend** repo implements it (`/orchestrate-module NOTE`).

Close with:

```bash
$PY governance-tools/gov.py analyze -m NOTE -v 1 --scope all
$PY governance-tools/gov.py lint
$PY -m pytest governance-tools/tests -q
```

## What you are actually hunting

The module is disposable. **The findings are the deliverable.** Watch for:

| Where | What to catch |
|---|---|
| a `gov.py` command | non-zero exit, a path that resolves to nothing, a gate that will not open |
| a rendered brief | a placeholder left unrendered, a value that belongs to another module |
| a generated artifact | an id that traces nowhere, a phase with no content, a self-check row with nothing behind it |
| `fetch-inputs` | a fold that is not deterministic — run it twice, the second must say `unchanged` |
| the shared repo | a write outside this repo's owned path; a second api-docs copy appearing anywhere |
| `analyze` | a clause that examines nothing while reporting a clean verdict |
| the consumers | a command still naming a path that no longer exists |

Two known conditions, so you do not re-report them as new:

1. `C7.23` cannot judge operation coverage until every `API-*` block carries its
   `Entity` line. Existing modules do not. **A brand-new module should** — if
   `NOTE`'s plan omits it too, that is a real finding about the engine, not
   about the old modules.
2. `test_markers.py::test_threshold_of_non_marker_kind_is_not_counted` skips by
   design: this profile declares no such threshold.

## Recording findings — keep this cheap

One file, appended as you go. No database, no tooling, no ceremony:

```
factory/erp/modules/NOTE/_state/smoke-findings.md
```

One block per finding, and nothing else:

```
## F-<n> — <one line>
Where   : <command, file:line, or stage id>
Expected: <what should have happened>
Actual  : <what did>
Fix     : <what you changed, or WONTFIX + why>
Status  : FIXED | OPEN | WONTFIX
```

Rules that keep it honest:

- **Fix what belongs to the factory or to a generated file**: engine templates,
  `factory.yaml`, the profile, `gov.py`, contracts, the generated commands, the
  shared repo layout. Fix it, re-run the step that failed, and record it.
- **Do not fix product code** in the backend or frontend beyond what `NOTE`
  itself needs. A defect in existing module code is a finding, not your task.
- **Do not weaken a check to make a step pass.** If a check fires wrongly, the
  check is the defect — fix the check and say so. A row with nothing behind it
  is deleted, never softened.
- Re-run `lint` and the test suite after every factory-side fix. Baseline:
  `0 critical · 0 major · 0 minor` and `237 passed, 1 skipped`. Any new failure
  is yours.
- Commit per logical change, in the repo that owns it. Never force-push. If a
  push is rejected, fetch and rebase — check for overlap first.

## When you are done

Append to the same file:

```
## SUMMARY
Pipeline : <the furthest step that completed>
Findings : <n> total — <n> FIXED · <n> OPEN · <n> WONTFIX
Baseline : lint <c/m/m> · tests <passed/skipped/failed>
Verdict  : the pipeline runs end to end / it stops at <step> because <reason>
```

Then commit it. **That file is the entire deliverable** — the `NOTE` module is
scaffolding and can be deleted afterwards with `gov.py archive -m NOTE --source <path>`.

## Standing rules

- No hardcoded paths, module names or stage ids in anything you write. Every
  such value has a home in `factory.yaml` or the profile; if you cannot find it
  there, that is a finding.
- Verify by running, not by reading. Every claim in your findings file must
  have a command behind it.
- If a fix needs a decision you cannot ground in the repo, record it as `OPEN`
  with both options and move on. Do not stop.
