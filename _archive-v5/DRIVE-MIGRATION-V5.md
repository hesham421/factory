# DRIVE MIGRATION — OPTIONAL bulk path (the system migrates itself automatically — §1E.5)

> **You do not have to run this.** Two automatic paths already exist:
> (a) every engine self-heals its inputs at Pre-Flight (GOVERNANCE-CONFIG §1E.5)
> and creates a missing ledger on first contact; (b) `process-project-files`
> STEP 0.0 audits AND applies the move/rename/mkdir plan + ledger backfill by
> itself. Use this document only to migrate MANY modules in one sitting.

```
Why    : Modules built before V5 sit on Drive with un-qualified names
         (srs.md, db-script.md …) and no journey-<mod>.json. The V5 tools and
         engines now REFUSE those names (§1D.2) and read links from the ledger
         (§1D.3). This procedure migrates each existing module ONCE.
Who    : run from Cowork/Claude with the Drive connector (bytes/renames go
         through the connector; journey_loader.py does the deterministic part).
Truth  : the rename map is derived from config.ARTIFACT_FILES
         (config.legacy_name_map) — nothing here is hand-listed.
```

## Per module (repeat for every existing module)

**1. List what exists** — connector `search_files` / `list` under
`[CTX]/[Module]/` (all stage sub-folders). Save as `listing.json`:
```json
{"files": [{"id":"…","name":"srs.md","webViewLink":"…","stage":"P1"}, …]}
```
(`stage` = the stage folder it was found in: P1, P2, P2.5, P3.1, P3.2, TEST-GEN.)

**2. Build the v1 ledger + rename plan** (deterministic, local):
```bash
python3 backend/governance/governance-tools/journey_loader.py \
        --ledger ./journey-<mod>.json --module <MOD> --version 1 --backfill ./listing.json
```
→ writes a **CLOSED v1** `journey-<mod>.json` (the module is already built)
whose rows already carry the NEW names + the existing file ids/links, and
prints `renames: [{drive_file_id, from, to}]`.

**2b. Audit placement (§1E)** — the same listing, checked against `config.DRIVE_LAYOUT`:
```bash
python3 backend/governance/governance-tools/drive_layout.py --audit ./listing.json --module <MOD> --version 1
```
→ `move` entries for every loose/misplaced file (e.g. `module-registry-<mod>.md`
sitting at `[CTX]` root → `<MOD>/P0-Platform/`, `platform-summary.md` → `_platform/`),
plus `missing_folders` to create (`drive_layout.py --tree` prints the full set).
Apply moves/mkdirs with the connector (`update_file` parent / create folder),
re-run the audit until exit 0.

**3. Apply the renames** — connector `update_file(id, name=to)` for each entry
(renaming is a metadata change, which `update_file` DOES support). Already-
qualified files (`registry-*-<mod>.md`, `prd-<mod>.md`, `module-registry-<mod>.md`)
are untouched — they pass through.

**4. Upload the ledger** — connector `create_file("journey-<mod>.json" →
`[CTX]/[Module]/_journey/`) — its own folder, never loose. Exactly one per module. From now on every engine appends
to it per §1D.8.

**5. Verify** — connector listing again: no un-qualified names remain, one
`journey-<mod>.json` present. Then the module flows through STEP 0 of
`process-project-files.md` like any V5 module.

## Also update on Drive (once, project-level)
- Replace `GOVERNANCE-CONFIG.md` everywhere with the V5 copy (§1B `[LEDGER]`
  token, §1C rows now use `-[MOD]` names, P-REG/P-ROUTER rows updated).
- Folder layout is now GOVERNED (§1E): stage folders as rendered from
  `config.DRIVE_LAYOUT`, `/vN/` for IFA versions, `_journey/` per module, `_platform/`
  per [CTX]. NOTHING loose at [CTX] root or module root. `drive_layout.py
  --tree` prints the exact expected tree; `--audit` proves compliance.
- Retire any `[CTX]/[Module]/registry-state-<MOD>.md` produced by P-REG:
  its content now lives in the per-stage `registry-<stage>-<mod>.md`.

## Existing repo trees (backend/frontend `modules/`)
Local archived copies keep their folders; rename the archived artifact files
to the V5 names (same `legacy_name_map`) or simply re-archive from Drive via
STEP 0 — the tools accept only V5 names.
