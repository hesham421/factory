# /micro-feature-frontend — add a feature to an implemented FRONTEND module (MFF)

Alternative to the full P2.5→P3.2 project journey (GOVERNANCE-CONFIG §1G). One
Claude Code session: generate the SAME governed backend analysis as a delta,
upload it to Drive in its governed place, then implement — for ANY extension on
a module that is already built + analysed. Backend only; frontend is
`/micro-feature-frontend`. Not for a brand-new module (→ full project route).

## Usage
```
/micro-feature-frontend [MODULE]   "<feature description>"
```
Resolve `$MODULE`; if missing, ask. Tools live in
`frontend/governance/governance-tools/` (config is the single source of truth
for names, versions, Drive placement, ledger — never spell any of them).

---

## STEP 0 — Pre-flight
- `validate_module($MODULE)`; confirm a FROZEN current version exists (a built
  module). None → STOP: "no prior version — use the full project route."
- `vN = config.get_next_version($MODULE)`; assign `CS-[MODULE]-[SEQ]`.
- §1E.5 self-heal: ensure the module's Drive layout is clean before reading.

## STEP 1 — Baseline read (LOCAL governance first, Drive fallback)
Read the prior version from the LOCAL repo — archived there, both FULL and split:
- `frontend/governance/modules/[MOD][/vN-1]/P1/srs-[mod].md`,
  `P2_5/flow-diagram-[mod].md`, `P2_5/ui-ux-spec-[mod].md`
- `.../P3_2/frontend-execution-plan-[mod].md` (full) **and**
  `.../packages/frontend-execution/**` (split) — read whichever the delta needs
- `registry-exec-fe-[mod].md`, and the §1F references
  `_ref/ui-shell/ui-shell-manifest-[mod].md` + `_ref/api-docs/api-docs-[mod].md`
FALLBACK: if a file isn't local, read it from its governed Drive path (§1E) via
the connector. Drive is the upload target + reference, not the primary read
source. IDs continue their sequences.

## STEP 2 — Generate the delta analysis — YOU (Claude Code) think and write it
The agents do NOT generate or reason — mechanical only (folders / copy / split).
YOU apply the P3.2 engine's reasoning against the baseline and RESPECT
DEPENDENCIES: continue ID sequences; honor UXD / ALIGN-FE mappings and the
backend API contract (from the §1F api-docs reference); a breaking change →
STOP, escalate. Produce, with §1D.2 names + PHASE/SUB/TC markers + a Change
Manifest header (CS-ID, baseline v[N-1], NEW/MODIFIED/UNCHANGED IDs +
dependencies):
- `frontend-execution-plan-[mod].md` — only new/changed phases/subs
- `db-script-[mod].md` — ONLY if a real new column/table is needed (additive
  migration; a breaking change → STOP, escalate to the full route)
- inline REGISTRY (§1D.4): `registry-exec-be-[mod].md` (+ `registry-db-[mod].md`
  if DB changed) + the project-registry update for the new IDs
Write them to a local staging folder.

## STEP 3 — Split + archive (mechanical — only AFTER step 2's full analysis)
```bash
cd frontend/governance/governance-tools
python3 agent1_create_structure.py --module [MODULE] --new-version
python3 agent2_archive.py           --module [MODULE] --source <staging>
python3 agent3_splitter.py          --module [MODULE]         # 5 stages + split receipt
```
Stage 1 re-validates markers (blocking); a NEW blocking error → stop and show it.

## STEP 4 — Upload to Drive (governed placement + ledger) — BEFORE implementing
For each generated analysis file, connector-upload to its governed folder:
`config.drive_folder_for_file(name, MODULE)` under `[CTX]/[MODULE]/vN/`
(never loose). Then the ledger (§1D.8):
```bash
python3 governance-tools/journey_loader.py --ledger $S/journey-<mod>.json -m [MODULE] -v N --open --engine micro-feature-frontend --change-set CS-[MODULE]-[SEQ]
# create_file each analysis file → its governed folder; capture id/webViewLink; --append one row each
python3 governance-tools/journey_loader.py --ledger $S/journey-<mod>.json -m [MODULE] -v N --append-receipts <base>/vN/receipts/split-receipt-<mod>-vN.json
# re-create journey-<mod>.json in [CTX]/[MODULE]/_journey/ and trash the old copy (§1D.8 STEP D)
```
Analysis on Drive is a precondition for STEP 5 — never implement first.

## STEP 5 — Implement the feature
Read the vN delta packages; apply ONLY the new/changed backend elements to the
real code (components/screens/routing/hooks), honoring the Change Manifest's
DEPENDENCIES (what must move with it, what must not change). Follow the normal
skill-routing rules. Do not touch v[N-1] behavior beyond what the delta states.

## STEP 6 — Close
`journey_loader --close -m [MODULE] -v N` (END) — the frontend run closes the
version whether the feature was frontend-only or spanned both tracks (it runs
after the backend one).

## Constraints (NON-NEGOTIABLE)
- NEVER implement before the delta analysis exists AND is uploaded (STEP 4 < 5).
- NEVER emit an un-qualified name or spell a Drive path — use config.
- NEVER restart ID sequences; always continue from the baseline registries.
- NEVER touch the backend repo/tools — this command is frontend-only; consume
  the backend API only via the §1F api-docs reference on Drive.
- A brand-new module → STOP, use the full project route. Frontend touches no DB.
- NEVER place any file loose — governed §1E folder only, verified before upload.
