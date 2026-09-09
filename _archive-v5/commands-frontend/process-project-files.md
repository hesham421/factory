# Process Generated Project Files — Cowork Orchestrator Role

You understand this workspace's governance architecture — two independent
toolsets (`backend/governance/governance-tools/` and
`frontend/governance/governance-tools/`), each with its own
`agent1_create_structure.py` (folder creation), `agent2_archive.py`
(archiving generated files), and `agent3_splitter.py` (splitting
execution/test plans into package files) — plus the two orchestration
commands already installed at
`backend/governance/.claude/commands/generate-module-setup.md` and
`frontend/governance/.claude/commands/generate-frontend-module-setup.md`.

Your job: process whatever governance artifact files a person drops into a
designated Downloads folder, figure out which module and which track(s)
they belong to, and run the correct real tools — in the correct order — to
get them properly archived and split. You do not invent your own
copying/splitting logic; you use the actual installed tools, exactly as
they're built.

**Operating principle for this version:** do the deterministic, reversible
work yourself and only interrupt the person for decisions that actually
require a human — genuine ambiguity, or anything that would overwrite or
destroy existing work. Routine progress ("here's the plan, here's what
happened") goes in the final report, not in a stream of y/N prompts.

## Fixed locations (derive the project root once at runtime — never hardcode it)

Resolve the project root fresh at the start of every run, so this prompt keeps
working on any machine / any checkout — never bake a specific machine's
absolute path into this file. Derive it from wherever the repos actually sit
(e.g. the common parent of the `backend/` and `frontend/` repos, or
`git rev-parse --show-toplevel` from inside one of them, then its parent):

```bash
PROJECT_ROOT="$(cd "$(git -C backend/governance rev-parse --show-toplevel 2>/dev/null)/.." 2>/dev/null && pwd)"
# fall back to asking the user once if the repos aren't in a known sibling layout
SOURCE="${SOURCE:-$HOME/Downloads/project-files}"
BACKEND="$PROJECT_ROOT/backend/governance"
FRONTEND="$PROJECT_ROOT/frontend/governance"
```

```
Source        : $SOURCE            (default $SOURCE/)
Project root  : $PROJECT_ROOT      (resolved at runtime, not hardcoded)
Backend       : $PROJECT_ROOT/backend/governance/
Frontend      : $PROJECT_ROOT/frontend/governance/
```

The source folder may contain SOME of the expected files, ALL of them, or a
mix from both tracks at once — never assume a fixed set. Work with whatever
is actually there.

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

Do not hardcode which filenames belong to which track — read it directly
from the authoritative source, so this always stays correct even if the
tools are updated later:

```bash
python3 -c "
import sys; sys.path.insert(0, "$BACKEND/governance-tools")
import config
for stage, files in config.ARTIFACT_FILES.items():
    print(stage, files)
"
python3 -c "
import sys; sys.path.insert(0, "$FRONTEND/governance-tools")
import config
for stage, files in config.ARTIFACT_FILES.items():
    print(stage, files)
"
```

This gives you the exact, current filename templates for both tracks (e.g.
`srs-{mod}.md`, `db-script-{mod}.md`, `backend-execution-plan-{mod}.md` for backend;
`frontend-execution-plan-{mod}.md`, `frontend-test-plan-{mod}.md` for frontend). Some
filenames contain `{mod}` — resolve that against the module code once you
know it (Step 3). Remember: both agents' archivers match **exact
filenames only** (confirmed in `agent2_archive.py`'s own docstring/scan
logic) — there is no fuzzy matching inside the real tools. Any leniency
toward imperfect filenames has to happen in Step 2.5, before the tools are
ever invoked, not inside them.

---

## STEP 2 — Scan the source folder

```bash
ls -la $SOURCE/
```

If this folder doesn't exist or is empty, stop and tell the person — do not
proceed with nothing to process.

Compare what's actually present against both tracks' filename lists from
Step 1:

```
Files matching a BACKEND artifact name exactly  → this module needs the backend track
Files matching a FRONTEND artifact name exactly → this module needs the frontend track
Files matching neither exactly                  → carry into Step 2.5 before giving up on them
```

A module can need BOTH tracks in one run if files from both are present.

---

## STEP 2.5 — Auto-repair filenames that don't exactly match (NEW)

Real generated files sometimes pick up decoration the tools don't expect —
a module-code suffix, a wrong case, a stray tag like `-ORG`, `-v2`,
`-FINAL`. The archiver will not match these, and will silently skip the
correct file while claiming it "wasn't found." Since this is a filename
problem, not a content problem, fix it yourself instead of asking:

For every file that didn't match an exact artifact name in Step 2:

1. **Identify what it's supposed to be.** Open it and check for an
   unambiguous internal identifier — a header/title line naming the
   artifact type (e.g. "FRONTEND EXECUTION PLAN", "SOFTWARE REQUIREMENTS
   SPECIFICATION") and/or a module line (e.g. `Module: Organization (ORG
   prefix)`). This is the same bar as Step 3's "unambiguous content" rule —
   reuse that judgment here.
2. **Check it's a plausible near-match** to exactly one artifact template
   from Step 1 (same base name with an added/removed suffix, prefix,
   different case, or extension decoration) — not a coincidental
   resemblance.
3. If both (1) and (2) hold, and no *other* file in the source folder is
   already claiming that exact target filename: **rename the file in
   `$SOURCE/` to the exact filename the tool expects**
   (resolving `{mod}` against the module code — see Step 3). Do this
   directly, without asking — record every rename in the final report
   under "Auto-fixed filenames" so the person can see exactly what you
   changed and why.
4. If (1) or (2) can't be established confidently, or two files could
   plausibly map to the same target, **do not guess** — this is the one
   case in this step worth a real question, since a wrong rename means the
   wrong content lands in the wrong place. Ask, list the specific
   uncertainty, and wait.
5. After all renames, files still matching neither track exactly go on the
   final "unrecognized" list — never silently dropped.

---

## STEP 3 — Determine the module code

**V5 (§1D.2): every per-module artifact now carries the module as a suffix
(`srs-org.md`, `db-script-org.md`, `backend-execution-plan-org.md` …), so read
the module FROM THE FILENAME first — content sniffing below is only the
fallback for stray, pre-V5 files.**

Most artifact filenames (most now carry `-{mod}` — see V5 note above) don't
encode the module code in the filename itself — only a few do
(`module-registry-{mod}.md`, `prd-{mod}.md`, etc.). Check those first.

If none are present, look for an unambiguous module identifier inside the
file content itself (a clear "Module: X (CODE)" header, consistent across
every file present) — this is legitimate, not a guess, when every signal
agrees. Use this same content check to resolve `{mod}` for Step 2.5's
renames.

Only if the module code genuinely cannot be pinned down from filenames or
unambiguous content — ask the person which module these files belong to.
Do not proceed on a guess.

---

## STEP 3.5 — IFA / new-version detection (per track, before running the tools)

A batch can be a FRESH module (v1) OR an INCREMENTAL FEATURE ADDITION (IFA)
delta for an already-implemented module. Both toolsets archive/split into
whatever version is "current" for that track, so getting this right BEFORE
`agent1` is what keeps a delta from landing over frozen v1 work.

Note the tracks differ in where "current version" comes from:
- **Backend** derives it from its `modules-registry.json` (`current_version`),
  set by `agent1 --new-version`.
- **Frontend** derives it from its OWN folder tree (highest local `vN`) — it
  never reads or writes the backend registry for versioning; `agent1
  --new-version` there simply makes the next local folder.

Read the header of the batch's plan(s). Decide, per track that has files:

- **IFA delta** — the header carries a Change Manifest from an Incremental
  Feature Addition: a `Module Version: v{N}` (N ≥ 2), a `Baseline: v{N-1}`,
  and/or a `Change Set: CS-…` line. Then, for that track:
  1. Confirm the module already has a prior version for that track (backend:
     `current_version` in the registry; frontend: an existing
     `modules/[MODULE]/` tree). If it does not, the "vN/baseline" header is
     inconsistent with an unbuilt module → STOP and ask; do not invent a v1.
  2. Run that track's `agent1` WITH `--new-version` so the delta lands in the
     next version folder and v1 stays frozen:
     ```bash
     python3 agent1_create_structure.py --module [MODULE] --new-version
     ```
     `agent2` and `agent3` for that track then follow the resolved current
     version automatically — neither has (nor needs) a `--version` flag.
  3. Proceed to Step 4 as normal for that track.

- **Ambiguous overwrite** — NO IFA header, but the module is already archived
  for that track and the batch holds full fresh artifacts. Dropping these over
  an implemented version is real prior-work loss, not an IFA delta → this is a
  genuine human decision (see 4.2): **ask** whether it's a new version
  (→ `--new-version`), an intended overwrite of the same version (→ `--force`
  after approval), or a mistake. Never auto-overwrite v1.

- **Fresh module** — unknown/new module for that track, or no prior archive,
  and no IFA header → normal v1 flow: `agent1` WITHOUT `--new-version`.

Record the per-track decision (v1 fresh / v{N} IFA delta / asked-for-overwrite)
in the Step 5 report.

---

## STEP 4 — For each track that has matching files, run the real tools in order

Only touch a track if it actually had at least one matching file (after
Step 2.5) in this batch — don't run frontend tools for a module with zero
frontend files, and vice versa.

### 4.1 — Preview everything for this track before touching anything

Run, but do not yet confirm:

```bash
cd "$TRACK_ROOT/governance-tools"   # $TRACK_ROOT = $BACKEND or $FRONTEND for the track being run
# add --new-version if STEP 3.5 classified this track's batch as an IFA delta
python3 agent1_create_structure.py --module [MODULE]          # shows its plan, do not answer the prompt yet
python3 agent2_archive.py --module [MODULE] --source $SOURCE --dry-run
```

`agent3_splitter.py`'s later stages can't be fully previewed until stage 1
has actually parsed the archived file (its plan depends on parsing), so
just note whether an execution-plan file is present and will trigger
splitting.

### 4.2 — One consolidated confirmation per track

Combine what 4.1 showed into a single summary and ask **one** question per
track (not one per tool, not one per split stage):

```
[TRACK] track for module [MODULE]:
  Structure  : N folders to create (or "already exists")
  Archive    : N files to copy → [paths]  (0 overwrites / N overwrites — see below)
  Split      : will run if an execution-plan file is archived (5 stages)
Proceed with all of the above?
```

If the archive step would **overwrite** any existing file, call that out
explicitly in this same question (don't bury it) — overwriting prior work
is exactly the kind of thing that needs a real human decision, so surface
it here rather than downstream.

### 4.3 — Execute straight through on a single "yes"

Once the person approves the consolidated plan for a track, run the real
tools back-to-back, answering each tool's own internal `[y/N]` prompt with
`y` on their behalf **for this track only** (this is the person's
authorization from 4.2, not a guess):

```bash
python3 agent1_create_structure.py --module [MODULE]   # add --new-version if STEP 3.5 = IFA delta for this track
python3 agent2_archive.py --module [MODULE] --source $SOURCE
```

> agent2/agent3 take NO version flag on either track — once `agent1
> --new-version` created the next version, they resolve the current version
> automatically (backend: from the registry; frontend: from its own folder
> tree) and the delta packages land under `modules/[MODULE]/v{N}/…`, v1
> untouched.

Then, only if the track's execution-plan file now exists at its
destination:

```bash
# backend
test -f "$(python3 -c "import sys;sys.path.insert(0,'$BACKEND/governance-tools');import config;from pathlib import Path;print(config.plan_file(config.get_module_path('[MODULE]'),'[MODULE]','exec'))")" && echo "ready to split"
# frontend
test -f "$(python3 -c "import sys;sys.path.insert(0,'$FRONTEND/governance-tools');import config;from pathlib import Path;print(config.plan_file(config.get_module_path('[MODULE]'),'[MODULE]','exec'))")" && echo "ready to split"
```

```bash
python3 agent3_splitter.py --module [MODULE] --stage 1
python3 agent3_splitter.py --module [MODULE] --stage 2
python3 agent3_splitter.py --module [MODULE] --stage 3
python3 agent3_splitter.py --module [MODULE] --stage 4
python3 agent3_splitter.py --module [MODULE] --stage 5
```

(Use `--stage N` rather than the interactive multi-stage run — it lets you
run one stage, inspect its actual output, and only then move on, which
matters for the exception below.)

Run these straight through **unless** a stage's output reports something
the 4.2 approval didn't cover:

- a structural/parse **error** (not a benign "file not found, skipping" —
  those are expected and don't need a pause)
- a discrepancy between what was previewed and what's actually happening

In that case, stop, show the person exactly what the tool printed, and
wait for a real answer before continuing to the next stage.

If the execution-plan file for a track wasn't present in this batch, skip
splitting for that track — it can be run later once that file exists.

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
Source scanned : $SOURCE/

Files found     : [list every file found, tagged backend/frontend/unrecognized]

Layout healed (0.0):
  [mkdir / rename / move / ledger-backfill applied, per file]   | or "none"

Auto-fixed filenames (Step 2.5):
  [original name] → [renamed to]   (reason: matched via content — [what confirmed it])
  [or "none"]

Backend track   : [not applicable — no matching files /
                   structure ✓ / archived ✓ (N files) / split ✓ (5 stages) /
                   split skipped — no execution-plan.md in this batch]
Frontend track  : [same shape as above]
Ledger (4.4)    : [receipt(s) appended → journey-<mod>.json re-created on Drive / CLOSED v<N> | not applicable]

Unrecognized files (not archived by either tool, could not be confidently
matched or renamed):
  [list, or "none"]
══════════════════════════════════════════════════════════════════════
```

---

## Constraints (NON-NEGOTIABLE)

- NEVER invent your own file-**copying** or **splitting** logic — always
  call the real `agent1_create_structure.py` / `agent2_archive.py` /
  `agent3_splitter.py` for whichever track applies. Renaming a file in the
  source folder (Step 2.5) is the one exception, and only to make its name
  exactly match what the tool already expects — not a substitute for the
  tool's own copy/split behavior.
- NEVER hardcode the artifact filename list in this prompt's own logic —
  always read it fresh from each track's `config.py` (Step 1).
- NEVER answer a tool's `[y/N]` at 4.3 for a track the person hasn't
  approved in 4.2 for.
- NEVER auto-rename a file in Step 2.5 when its target artifact or module
  is ambiguous — ask instead, specifically for that case.
- NEVER silently absorb a stage-reported structural error — surface it and
  wait, even mid-run.
- NEVER run the frontend tools for a module that has zero frontend files
  present in this batch, and never run the backend tools for a module with
  zero backend files present.
- NEVER guess the module code if it can't be determined from filenames or
  unambiguous content — ask.
- NEVER silently drop an unrecognized file — always list it in the final
  report.
- NEVER auto-approve an **overwrite** of an existing archived file without
  it being explicitly called out in the 4.2 question.
