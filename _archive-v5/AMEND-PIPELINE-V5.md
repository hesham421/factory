# AMEND-PIPELINE-V5 — Pipeline Restructure (2026-09-06)

```
Status  : APPLIED — this zip contains the REPLACEMENT files. Authoritative
          spec = GOVERNANCE-CONFIG.md §1D (single source; nothing below is
          repeated as hardcode anywhere else).
Evidence: backend tools 51 passed · frontend tools 22 passed (see PYTEST-EVIDENCE-*.txt)
Supersedes in part: AMEND-ROUTER-A (P-ROUTER demoted), P-REG project (retired).
Builds on: AMEND-IFA (versioning / v1 frozen — unchanged and still in force).
```

## What changed — by decision

| # | Decision | Implemented as |
|---|---|---|
| **5** | Module-qualified filenames, matched by tools, no hardcode | §1D.2 vocabulary. Tools: names defined ONCE (`EXEC_PLAN_FILE`/`TEST_PLAN_FILE`) → `ARTIFACT_FILES`/`PLAN_ARTIFACTS`/`plan_file()`/`plan_label()`. **Zero literal plan names** in both `agent3` (guarded by tests). `classify_artifact()` is template-based — the old exact-match silently **skipped all semantic checks** for a qualified name; now fixed + regression-tested. Un-qualified names are retired (rejected). |
| **1 · 0a · 0b · 3b** | No P-ROUTER dependency; engines talk to each other; handoff prompt; journey ledger; registry inline | §1D.4 **unified COMPLETION PROTOCOL** stamped on every core engine: artifact → **inline REGISTRY** (ex-P-REG) → **LEDGER row** → **NEXT-ENGINE INPUT** (§1D.5). P-ROUTER = optional read-only viewer. |
| **3a** | Full registry merge | P-REG **retired** (stub file). Master Registry Builder = **bootstrap only**. Per-module registry lives in each engine's step 2. |
| **2** | Python loader in process-project-files (BE+FE) | `journey_loader.py` (`--plan / --verify / --append / --open / --close`) + ledger schema/helpers in `config.py` (§1D.3). Wired as **STEP 0** in both orchestrators. Bytes move via the Drive **connector**; the script does the deterministic part. |
| **3c** | Test Gen: TC only, TestSprite executes | §1D.6. Test Gen engine re-scoped: framework-agnostic TC specs; JUnit/Playwright/manifest dropped; markers kept so the splitter still works. TestSprite is spec-driven (verified from its docs). |
| **4** | Audit → fix-prompts | §1D.7. P4.1/P4.2 output = ready fix-prompts **grouped by target project** with PROBLEM/WHY/RECOMMENDED/**DEPENDENCIES**/VERIFY + paste-ready prompt. Still markdown, used manually. |
| core | Core = P(-1)…P3.2; rest optional | §1D.1. |

## Naming rule (the one everyone follows)
`<artifact>-{mod}.md` (lower-case module suffix) — e.g. `srs-org.md`,
`backend-execution-plan-org.md`. Same convention as the pre-existing
`registry-*-{mod}.md`. `platform-summary.md` stays platform-level.

## Migration notes
- Existing modules on Drive with un-qualified names: rename once to the §1D.2
  form (STEP 2.5 of the orchestrator can do it from the file header), then
  they flow through the tools. The tools **refuse** the old names on purpose.
- Existing v1 trees under `modules/[MOD]/` are unaffected (paths unchanged;
  only filenames inside changed).
- P-REG sessions: stop opening them; the engine that produced the artifact
  runs the registry step itself now.

## Gap closure (2026-09-06, second pass)

| Gap | Closed by |
|---|---|
| **Link recording — HOW an engine writes the Drive-hosted ledger** | §1D.8 **LEDGER-WRITE PROCEDURE**: upload → capture `id`/`webViewLink` → fetch `journey-<mod>.json` → START/APPEND/END in memory → **re-create** the file → trash the old copy (the connector's `update_file` cannot change content). Referenced from every engine's completion protocol. |
| **Package links not recorded automatically** | agent3 stage 5 (both tracks) writes `receipts/split-receipt-<mod>-v<N>.json` (one row per package file, `repo_path`); orchestrators' new **STEP 4.4** appends it with `journey_loader --append-receipts` and writes the ledger back. Ledger rows are location-aware (Drive `drive_file_id` **or** repo `repo_path`). |
| **Old names inside engine bodies** | Controlled rename pass across all 13 project files (`srs.md`→`srs-[MOD].md` …), protecting the lines that intentionally list retired names. 0 stray old names remain. |
| **Drive consistency with the new system** | §1B `[LEDGER]` token; §1C Drive Dependency Map rows renamed to `-[MOD]`, P-REG row RETIRED, P-ROUTER row = optional viewer, manifest retired. **`DRIVE-MIGRATION-V5.md`** + `journey_loader --backfill`: builds a CLOSED v1 ledger from a connector listing of an existing module and prints the exact rename plan (derived from `config.legacy_name_map`, never hand-listed). |

## Drive layout governance (2026-09-06, third pass) — §1E

| Problem observed | Closed by |
|---|---|
| Files loose outside folders ([CTX] root, module root); engines unsure where to read/write | **`config.DRIVE_LAYOUT`** — the single machine-readable map (stage → folder → ONE writer → readers). **§1E is RENDERED from it**, every engine's completion protocol gets a rendered **PATHS block** (WRITES TO / READS FROM), and a test proves prose == code. |
| The LAW | §1E.1: a file lives only in its stage folder; [CTX] root + module root = folders only; one Drive tree per module (both tracks); versions nest as `/vN/`; ledger in `_journey/`, platform files in `_platform/`; one writer per folder. |
| Multi-project / multi-module / loader | Addressing `[GOVERNANCE-ROOT]/[Project]/[Domain]/<slot>/[Module][/vN]/<stage>/<file>`; loader reads `[CTX]/[Module]/_journey/journey-<mod>.json`; `drive_layout.py --tree` (mkdir plan) / `--audit` (move+rename+missing plan, exit 1 while dirty) gate STEP 0 of both orchestrators. |
| Legacy P0-at-root convention | Retired: `module-registry-<mod>.md`/`business-policies-<mod>.md` → `P0-Platform/`; `platform-summary.md` → `_platform/`. §1B/§1C/§1D/engine bodies aligned. |

## Automatic migration (2026-09-06, fourth pass) — §1E.5

Migration is no longer a human step. Two automatic paths:
1. **Engine self-heal at Pre-Flight (§1E.5):** an input not at its governed path is searched in the module subtree (V5 or legacy name), renamed + moved via connector metadata ops, reported under `HEALED:` in the handoff; a missing ledger is created (START v1) on first contact. A legacy module becomes compliant progressively, by the engines themselves.
2. **Orchestrator autonomous apply (STEP 0.0):** `drive_layout.py --audit` → the orchestrator itself creates folders, renames, moves, re-audits (≤3 rounds) and backfills the ledger; stops only for unknown files. Reported under "Layout healed (0.0)".
`DRIVE-MIGRATION-V5.md` is now the OPTIONAL bulk path.

## Governed references — UI Shell + API Docs (2026-09-06, fifth pass) — §1F

- Two governed REFERENCE folders per module version (`_ref/ui-shell`, `_ref/api-docs`) added to `config.DRIVE_LAYOUT` (single source) → they appear in §1E, the expected tree, and `drive_layout.py --audit` like any artifact.
- **P3.2 §1F ingest:** first attach → upload once to the governed folder; newer attach → **replace in place** (re-create same path, trash old, supersede ledger row — one live copy per version); nothing attached → read the governed copy, so **any later conversation on the module inherits UI Shell + API Docs automatically**.
- **New IFA version:** fresh attach ingested into vN, else **carry forward** from vN-1; vN-1 references stay frozen. A replacement for the same version integrates cleanly (old removed).
