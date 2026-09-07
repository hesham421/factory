# FACTORY PRECEDENCE — what the git-native factory supersedes (read FIRST)

The engine references under `engines/*/references/` and the shared files here
were written for the Claude-Projects + Google-Drive era (AMEND-PIPELINE-V5).
Inside the factory the following are SUPERSEDED. Where a reference and this
file disagree, THIS FILE WINS.

| Drive-era instruction (in references) | Factory rule (git-native) |
|---|---|
| Upload artifacts via the Drive connector; §1E governed Drive folders; `[CTX]/[Module]/…` paths | Write artifacts into `modules/[MOD][/vN]/<stage>/` in THIS repo and **commit**. No upload. |
| §1D.8 LEDGER-WRITE (journey-{mod}.json, START/END rows, connector re-create) | The **commit** is the ledger row; versions are folders + tags (`gov.py version/tag`). No JSON ledger. |
| §1F `_ref/ui-shell`, `_ref/api-docs` reference folders on Drive | Pass-2 inputs are **fetched from the consumer repos via git** into `modules/[MOD][/vN]/_inputs/` (`gov.py fetch-inputs`). |
| §1E.5 layout self-heal via connector; `drive_layout.py`; `journey_loader.py` | Not used. Layout = this repo's folder tree; `git status` is the audit. |
| CORE-10 Pre-Flight "read from Drive paths" | Read from the repo (local files); baseline = `v[N-1]` folder / tag. |
| NEXT-ENGINE INPUT "paste into the next Claude Project" | Still printed, but the next stage runs in the SAME Claude Code session via `commands/analyze-pass*.md` (delegate lane). |
| P-ROUTER / pipeline-state.json | Not present. `gov.py status` + git history. |
| §1G `/micro-feature` Drive upload steps | `commands/micro-feature.md` (same flow, new version, git). |

STILL IN FORCE (unchanged): module-qualified names (§1D.2), PHASE/SUB/TC
markers, Change Manifest + IFA versioning, inline REGISTRY step (§1D.4 step 2),
per-engine MUST/MUST NOT, XM/UXD/ALIGN dependency rules, shared rules and
artifact contracts, PROJECT-3-REGISTRY backbone, TestSprite TC-spec scope
(§1D.6), audit fix-prompt format (§1D.7).

LOAD ORDER for any engine run: this file → shared/GOVERNANCE-CONFIG.md →
shared/shared-governance-rules.md + shared-artifact-contracts.md →
(P3.x only) shared/PROJECT-3-REGISTRY.md → the engine's SKILL.md →
its references/ file.
