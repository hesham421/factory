# Process Generated Project Files — Autonomous Split Orchestrator (Cowork)

You are the single agent responsible for taking whatever governance artifact
files a person drops into a Downloads folder and driving them ALL THE WAY to
fully split, verified package files — automatically, end to end, using the real
tools, fixing what can be fixed deterministically, and stopping only for the
few things that genuinely need a human.

This workspace has two independent toolsets — `backend/governance/governance-tools/`
and `frontend/governance/governance-tools/` — each with its own
`config.py` (artifact filename lists + validation config), `agent1_create_structure.py`
(folder creation), `agent2_archive.py` (archiving), and `agent3_splitter.py`
(marker validation, deterministic safe-fix, and 5-stage splitting).

**Operating principle:** do all the deterministic, reversible work yourself and
run the whole pipeline to completion without narrating a stream of prompts. Only
stop for a real human decision: (1) overwriting existing archived work, (2) an
error the tools cannot safely auto-fix, or (3) a module code / target that
cannot be determined unambiguously. Everything else goes in the final report,
not in a question.

You never invent copy/split logic and never hand-edit marker content. The only
edits you make are (a) normalizing a file's NAME in staging, and (b) invoking
`agent3_splitter.py --fix-safe`, which performs deterministic marker repairs and
keeps the untouched original as `<file>.orig`. Both are recorded in the report.

## Fixed locations — DERIVED AT RUNTIME, never hardcoded

Work on any machine, for any user, repos checked out anywhere — never bake a
specific absolute path into this file (same portability law as
`orchestrate-module.md`). At the start of every run resolve, this run:

```
Backend root  : the backend/governance/ this command lives under — derive via
                git rev-parse --show-toplevel (+ /governance), or by walking up
                from this file's own location. BE_TOOLS = <backend root>/governance-tools.
Frontend root : the sibling frontend/governance/ next to the project root.
                FE_TOOLS = <frontend root>/governance-tools. If not found at the
                expected sibling, ASK for it — never guess or persist it.
Source        : ~/Downloads/project-files/ by default; if the person named a
                different drop folder, use that.
```

Use derived roots for THIS run only — never write them back into this file. The
source may hold SOME, ALL, or a MIX of both tracks' files — work with what's there.

---

## STEP 0 — LOAD A MODULE VERSION FROM ITS JOURNEY LEDGER (AMEND-PIPELINE-V5 §1D.3)

Instead of waiting for files to be dropped by hand, a whole module version can
be pulled in one pass from its Journey Ledger — `journey-{mod}.json` at
`[LEDGER] = [CTX]/[Module]/_journey/` on Drive (one file per module, all versions).
The deterministic part is `journey_loader.py` (backend governance-tools; it is
track-neutral and is the ONE loader for this dual-track orchestrator); the
bytes move through the Drive connector.

### 0.0 — Drive layout gate (§1E) — BEFORE loading anything
Governance of WHERE files live is machine-checked, not assumed. Get a connector
listing of the module's Drive tree (files: id/name/path relative to [CTX];
folders) and audit it against the single source `config.DRIVE_LAYOUT`:

```bash
python3 "$BACKEND/governance-tools/drive_layout.py" --audit "$SOURCE/listing.json" --module [MODULE] --version [N]
#  exit 0 → clean.  exit 1 → the JSON plan lists: move (loose/misplaced files → target
#  folder), rename (legacy names), missing_folders, unknown. Apply move/rename/mkdir
#  with the connector, re-audit, and only then continue. Never load around a dirty tree.
```

**AUTONOMOUS APPLY (V5 §1E.5).** Do not hand the plan to the person. Moves,
renames and folder creation are metadata-only, reversible operations, so
apply them yourself with the connector, in this order, then re-audit until
exit 0 (max 3 rounds):
  1. `missing_folders`  → create each folder
  2. `rename`           → `update_file(id, name=to)`
  3. `move`             → `update_file(id, parent=<to folder>)`
Then, if the module has artifacts but NO `journey-<mod>.json` yet, build it
automatically (it is a legacy module):
```bash
python3 "$BACKEND/governance-tools/journey_loader.py" --ledger "$SOURCE/journey-<mod>.json" \
        --module [MODULE] --version 1 --backfill "$SOURCE/listing.json"
# then create_file(journey-<mod>.json → [CTX]/[Module]/_journey/)
```
Stop ONLY for `unknown` files (not artifacts of this ecosystem — list them,
do not move them). Record every applied move/rename/mkdir/backfill in the
Step 5 report under "Layout healed (0.0)".

The ledger itself lives at `[CTX]/[Module]/_journey/journey-<mod>.json` (its own
folder — never loose at the module root); platform-level files only at
`[CTX]/_platform/`. Every engine's PATHS block (its completion protocol) is
rendered from the same layout, so what engines write and what this step
audits can never disagree.

```bash
# 0.1 fetch the ledger itself via the connector → $SOURCE/journey-<mod>.json
# 0.2 ask the loader which files make up this version (connector executes it)
python3 "$BACKEND/governance-tools/journey_loader.py" \
        --ledger "$SOURCE/journey-<mod>.json" --module [MODULE] \
        --version [N | latest] --dest "$SOURCE" --plan
#     → JSON: files[] = {drive_file_id, drive_url, filename, dest}
#       download each drive_file_id with the connector into its "dest"
# 0.3 prove every artifact of that version landed under its exact name
python3 "$BACKEND/governance-tools/journey_loader.py" \
        --ledger "$SOURCE/journey-<mod>.json" --module [MODULE] \
        --version [N] --dest "$SOURCE" --verify        # exit 1 lists what is missing
```

- The version to load is the one you are processing (an IFA delta = v2/v3 …;
  the loader warns if that version is still OPEN in the ledger — the journey
  hasn't been ENDed — treat the plan as possibly partial).
- Because every ledger filename is already §1D.2 module-qualified
  (`srs-org.md`, `backend-execution-plan-org.md` …), STEP 2.5's rename step
  has nothing to do for ledger-loaded files and STEP 3 reads the module from
  the filename, not from content.
- If there is no ledger for the module (a pre-V5 journey), skip STEP 0 and
  proceed with the drop-folder flow below unchanged.
- The loader never invents a filename: its plan is exactly what the engines
  recorded from config.ARTIFACT_FILES.

---

## STEP 1 — Read the real filename lists from the tools themselves

Never hardcode which filenames belong to which track — read them from the
authoritative source so this stays correct if the tools change:

```bash
python3 -c "import sys; sys.path.insert(0, '$BE_TOOLS'); import config
for stage, files in config.ARTIFACT_FILES.items(): print(stage, files)"
python3 -c "import sys; sys.path.insert(0, '$FE_TOOLS'); import config
for stage, files in config.ARTIFACT_FILES.items(): print(stage, files)"
```

This yields the exact current templates (e.g. `srs.md`, `db-script.md`,
`backend-execution-plan-{mod}.md`, `backend-test-plan-{mod}.md` for backend). Some contain
`{mod}` — resolve against the module code (Step 3). The archivers match EXACT
filenames only — any leniency happens in Step 2.5, before the tools run.

---

## STEP 2 — Scan the source folder

```bash
ls -la <SOURCE>
```

Empty or missing → stop and say so. Compare what's present against both tracks'
lists from Step 1: exact BACKEND match → needs backend; exact FRONTEND match →
needs frontend; neither → carry into Step 2.5. A module can need BOTH tracks.

---

## STEP 2.5 — Auto-repair filenames that don't exactly match

Generated files sometimes pick up decoration the tools don't expect (`-ORG`,
`-v2`, `-FINAL`, wrong case). The archiver won't match these and will report the
correct file "not found." Since it's a name problem, fix it yourself:

For every file that didn't match an exact artifact name:
1. **Identify it** from an unambiguous internal header (e.g. "SOFTWARE
   REQUIREMENTS SPECIFICATION", "BACKEND EXECUTION PLAN") and/or a module line.
2. **Confirm a plausible near-match** to exactly one template (same base with
   an added/removed suffix, case, or extension decoration).
3. If (1) and (2) hold and no other file already claims that exact target:
   **rename it in the source folder** to the exact expected name (resolving
   `{mod}`). Record every rename in the report under "Auto-fixed filenames".
4. If identity/target is ambiguous, or two files map to the same target: **do
   not guess** — ask, naming the specific uncertainty.
5. Files still matching neither track go on the report's "unrecognized" list.

---

## STEP 2.6 — Validate markers and auto-fix what's safe (BEFORE archiving)

For each execution-plan / test-plan file now present in the source (backend:
`backend-execution-plan-{mod}.md`, `backend-test-plan-{mod}.md`; frontend: its equivalents — resolve `{mod}` via config.resolve_filename, never spell it),
validate it with its OWN track's tool — catching marker problems while the file
is still an editable staging copy:

```bash
python3 "$BE_TOOLS/agent3_splitter.py" --validate-markers --file "<SOURCE>/backend-execution-plan-<mod>.md"
```

Interpret the exit code and output:

- **Exit 0, no advisories** → clean. Proceed.
- **Exit 0 with THRESHOLD ADVISORIES** → non-blocking. A phase over its split
  threshold with no SUBs (or a never-split phase with SUBs) is a SEMANTIC call,
  NOT something to auto-restructure. Record each advisory in the report and
  proceed — do NOT add `--strict-thresholds` and do NOT invent SUB groupings.
- **Exit 1 (structural / semantic errors)** → attempt a deterministic repair:

  ```bash
  python3 "$BE_TOOLS/agent3_splitter.py" --fix-safe --file "<SOURCE>/backend-execution-plan-<mod>.md"
  ```

  `--fix-safe` repairs ONLY the unambiguous, reversible classes — a phase-key
  separator typo (`SVC_API` → `SVC-API`) and un-qualified SUB labels
  (`SUB:CRUD` → `SUB:SVC-API-CRUD`) — writing `<file>.orig` as backup and
  re-validating. Read its exit code:
    - **Exit 0** → the file is now valid. Record every applied fix (from→to,
      line) in the report and proceed to archive the corrected file.
    - **Exit 1** → some issue is NOT safe to auto-fix (unmatched/unclosed/
      mismatched markers, duplicate IDs, orphan atomics, an ambiguous phase key
      like `DATADOM` with the hyphen missing entirely, a `+`/space in a key that
      breaks tokenization). **STOP for this file.** Report exactly what remains,
      with line numbers, and do NOT archive or split a file that still fails
      validation — that would push a broken plan downstream. Ask the person to
      fix the flagged lines (or confirm a specific correction), then re-run.

Use `$FE_TOOLS/agent3_splitter.py` for frontend files. If a track's tool does
not support `--validate-markers`/`--fix-safe`, fall back to letting Agent 3
Stage 1 validate during Step 4 and stop on the error it reports there.

Never hand-edit markers yourself: if `--fix-safe` can't resolve it, a human
decides. Never "fix" a threshold advisory by restructuring — it's advisory.

---

## STEP 3 — Determine the module code

**V5 (§1D.2): every per-module artifact now carries the module as a suffix
(`srs-org.md`, `db-script-org.md`, `backend-execution-plan-org.md` …), so read
the module FROM THE FILENAME first — content sniffing below is only the
fallback for stray, pre-V5 files.**

Most filenames don't encode the module (`srs.md`, `db-script.md`,
`backend-execution-plan.md`); a few do (`module-registry-{mod}.md`,
`prd-{mod}.md`) — check those first. Otherwise read an unambiguous "Module: X
(CODE)" header consistent across every file present (legitimate when every
signal agrees). Use the same check to resolve `{mod}` in Steps 2.5/2.6. If it
still can't be pinned down — ask. Never proceed on a guess.

---

## STEP 3.5 — IFA / new-version detection (before running the tools)

A batch can be a FRESH module (v1) OR an INCREMENTAL FEATURE ADDITION (IFA)
delta for an already-implemented module. The tools archive into whatever
version is `current` in `modules-registry.json`, so getting this right BEFORE
`agent1` is what keeps a delta from landing over frozen v1 work.

Read the header of the batch's plan / srs. Decide:

- **IFA delta** — the header carries a Change Manifest from an Incremental
  Feature Addition: a `Module Version: v{N}` (N ≥ 2), a `Baseline: v{N-1}`,
  and/or a `Change Set: CS-…` line. Then, per track that has files:
  1. Confirm the module already exists in that track's `modules-registry.json`
     with a `current_version`. If it does NOT (the "vN/baseline" header
     describes a version of a module that was never built), the header is
     inconsistent → STOP and ask; do not invent a v1.
  2. Run `agent1` WITH `--new-version` so the delta lands in the next version
     folder and v1 stays frozen:
     ```bash
     python3 agent1_create_structure.py --module [MODULE] --new-version
     ```
     This sets `current_version = N`; `agent2` and `agent3` then follow it
     automatically — neither has (nor needs) a `--version` flag, by design.
  3. Proceed to Step 4 as normal — the version is now resolved for the whole
     chain.

- **Ambiguous overwrite** — NO IFA header, but the module is already archived
  for that track (`current_version` present and `manifest.status.archived`),
  and the batch holds full fresh artifacts. Dropping these over an implemented
  module is real prior-work loss and is NOT an IFA delta. This is a genuine
  human decision (STEP 4.2 territory): **ask** whether this is a new version
  (→ `--new-version`), an intended overwrite of the same version (→ `--force`
  later, after the 4.2 gate), or a mistake. Never auto-overwrite v1.

- **Fresh module** — unknown/new module, or a known module with no prior
  archive, and no IFA header → normal v1 flow: `agent1` WITHOUT `--new-version`
  (Step 4 unchanged).

Record the decision (v1 fresh / v{N} IFA delta / asked-for-overwrite) in the
Step 5 report.

---

## STEP 4 — Run the real tools to completion, per track (AUTONOMOUS)

Only touch a track that had at least one matching file (after Step 2.5) AND
whose plan files passed Step 2.6 (clean, or cleaned by `--fix-safe`). Never run
frontend tools for a module with zero frontend files, or vice versa.

### 4.1 — Preview

```bash
cd "<track>/governance-tools"
# add --new-version here too if STEP 3.5 classified this batch as an IFA delta
python3 agent1_create_structure.py --module [MODULE] [--new-version if IFA] --dry-run
python3 agent2_archive.py --module [MODULE] --source "<SOURCE>" --dry-run
```

Note whether structure is new or exists, how many files will copy, and — from
the dry-run — whether any archive step would **overwrite an existing file**.

### 4.2 — Decide whether a human gate is needed

- **No overwrite, no unresolved error** → PROCEED AUTOMATICALLY. This command's
  job is to run the whole split without pestering; do not ask just to ask.
- **An archive step would overwrite existing archived work** → this is real
  prior-work loss. Ask ONE consolidated question per track, calling out exactly
  which files would be overwritten, before doing anything for that track. Only
  after an explicit yes do you pass `--force`.

### 4.3 — Execute end to end on a single authorization

Run the real tools back to back (the person's Step-4.2 go — explicit for an
overwrite, implicit otherwise — authorizes answering each tool's own `[y/N]`
with `y` for THIS track):

```bash
python3 agent1_create_structure.py --module [MODULE]   # add --new-version if STEP 3.5 = IFA delta
python3 agent2_archive.py --module [MODULE] --source "<SOURCE>"    # add --force ONLY if approved in 4.2
```

> agent2/agent3 take NO version flag — once `agent1 --new-version` set the
> current version, they resolve it from the registry automatically and the
> delta packages land under `modules/[MODULE]/v{N}/…`, v1 untouched.

Then, only if the track's execution-plan file archived successfully:

```bash
test -f "$(python3 -c "import sys;sys.path.insert(0,'<track>/governance-tools');import config;print(config.plan_file(config.get_module_path('[MODULE]'),'[MODULE]','exec'))")" && echo ready
python3 agent3_splitter.py --module [MODULE] --stage 1
python3 agent3_splitter.py --module [MODULE] --stage 2
python3 agent3_splitter.py --module [MODULE] --stage 3
python3 agent3_splitter.py --module [MODULE] --stage 4
python3 agent3_splitter.py --module [MODULE] --stage 5
```

Run straight through. Stage 1 re-validates (structural + semantic, blocking;
thresholds advisory) — because Step 2.6 already validated/fixed the staging
copy, Stage 1 should pass; if it somehow reports a NEW blocking error, stop and
report it (do not push past a blocking error). A missing OPTIONAL file is not an
error: if only an execution plan was in this batch and no test plan, Stage 3
prints "not found — skipping" and the run still completes — that is expected,
not a failure. There is no P4/audit stage anywhere; its absence is normal and
breaks nothing.

Stage 2 also captures any content outside all phases as
`packages/<...-execution>/_SECTIONS.md` — note it in the report if produced.

If the execution-plan file wasn't in this batch, skip splitting for the track;
it can run later once that file exists.

---

### 4.4 — Record the package links in the module ledger (AMEND-PIPELINE-V5 §1D.8)

After Stage 5 passes, agent3 has written `receipts/split-receipt-<mod>-v<N>.json`
under the module version base — one ledger row per package file (repo-resident,
`repo_path`). Fold it into the module's Journey Ledger, then write the ledger
back to Drive with the same re-create procedure engines use (§1D.8 STEP B–D):

```bash
# ledger copy already in $SOURCE from STEP 0 (or fetch it now via the connector)
python3 "$BACKEND/governance-tools/journey_loader.py" \
        --ledger "$SOURCE/journey-<mod>.json" --module [MODULE] --version [N] \
        --append-receipts "<track root>/modules/[MODULE][/vN]/receipts/split-receipt-<mod>-v<N>.json"
# then: create_file(journey-<mod>.json → [CTX]/[Module]/_journey/) and trash the old copy
```

Do this per track that was split (backend receipt, frontend receipt — both
append to the SAME module ledger). If this run is the last engine/tool for the
version, also `--close` it (END module <MOD> vN) before writing back.

---

## STEP 5 — Report

```
══════════════════════════════════════════════════════════════════════
PROJECT FILES PROCESSED — [MODULE]
══════════════════════════════════════════════════════════════════════
Source scanned : <SOURCE>

Files found     : [every file, tagged backend / frontend / unrecognized]

Layout healed (0.0):
  [mkdir / rename / move / ledger-backfill applied, per file]   | or "none"

Auto-fixed filenames (2.5):
  [original] → [renamed]   (matched via: [what confirmed it])   | or "none"

Marker auto-fixes (2.6, via --fix-safe):
  [file]: PHASE:[from]→[to] (line N); SUB:[from]→[to] (line N)   | or "none"
  Backups kept: [file].orig ...                                  | or "none"

Threshold advisories (non-blocking, left as-is):
  [file]: PHASE:[key] over threshold, unsplit — verify intent    | or "none"

Backend track   : [n/a — no files / structure ✓ / archived ✓ (N, M overwritten)
                   / split ✓ (5 stages) / _SECTIONS.md captured
                   / split skipped — no execution plan this batch]
Frontend track  : [same shape]
Ledger (4.4)    : [receipt(s) appended → journey-<mod>.json re-created on Drive / CLOSED v<N> | n/a]

Stopped for a human (if any):
  [file/line]: [exact unfixable issue from --fix-safe / Stage 1, and what's
               needed]                                            | or "none"

Unrecognized files (not archived, not confidently matched):
  [list]                                                          | or "none"
══════════════════════════════════════════════════════════════════════
```

---

## Constraints (NON-NEGOTIABLE)

- NEVER invent your own copy/split logic — always call the real
  `agent1_create_structure.py` / `agent2_archive.py` / `agent3_splitter.py`.
- The ONLY edits permitted are: renaming a file in the source folder (2.5) to
  match an exact expected name, and running `agent3_splitter.py --fix-safe`
  (2.6), which itself only performs deterministic, backed-up marker repairs.
  NEVER hand-edit marker syntax or ANY substantive content.
- NEVER archive or split a plan file that still fails validation after
  `--fix-safe` — stop and report; a broken plan must not go downstream.
- NEVER "fix" a threshold advisory by inventing SUB groupings, and NEVER add
  `--strict-thresholds` on the person's behalf — thresholds are a semantic call.
- NEVER hardcode an absolute path — derive roots at runtime (Step 0).
- NEVER read the filename list from anywhere but each track's live `config.py`.
- NEVER auto-approve an OVERWRITE of existing archived work — it must be called
  out and approved in 4.2 before `--force` is used.
- NEVER run one track's tools for a module with zero files for that track.
- NEVER guess the module code — ask if it can't be determined unambiguously.
- NEVER treat a missing OPTIONAL artifact (no test plan yet, no P4) as an error
  — it is a graceful skip.
- NEVER silently drop an unrecognized file — list it in the report.
