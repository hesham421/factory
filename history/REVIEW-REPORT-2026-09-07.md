# Factory review — findings & fixes (2026-09-07)

Full audit of `governance-factory` against the approved blueprint and the
delegate-skills contract. Every finding below is FIXED in this package and
guarded by a test where code is involved (see PYTEST-EVIDENCE.txt).

| # | Severity | Finding | Fix |
|---|---|---|---|
| F1 | **CRITICAL** | Track toolsets computed their `modules/` root from their own file location (`governance-tools/tracks/modules/…`) while the factory works in `<root>/modules/`. Split would write in one place, deliver read from another. | Both track configs honour `GOV_FACTORY_ROOT`; `gov.py` sets it on every dispatch. Test: `test_tracks_operate_on_factory_modules_root_and_same_version`. |
| F2 | **CRITICAL** | Version source mismatch: backend track versions by its registry (`current_version`), factory by filesystem folders. `gov.py version --new` created `v2/` but backend agents would still target v1. | `gov.py version --new` syncs the backend track registry (versions + current). Frontend was filesystem-based already. Same test. |
| F3 | **MAJOR** | Frontend track validated modules against `../../shared/modules-registry.json` — a path that does not exist in the factory. Every frontend run would reject the module. | Frontend reads the backend TRACK's registry directly (still read-only). Same test. |
| F4 | **MAJOR** | 11 shared governance files referenced by every engine (GOVERNANCE-CONFIG, shared rules, artifact contracts, AMEND-IFA, XM protocol, PROJECT-3-REGISTRY backbone…) were ABSENT from the factory. | Added `shared/` with all of them; every SKILL.md now states the load order (shared first). Test: `test_factory_structure_integrity`. |
| F5 | **MAJOR** | Engine references still instruct Drive uploads, JSON ledger writes, connector self-heal, `_ref/` folders — contradicting the git-native factory. | `shared/FACTORY-PRECEDENCE.md` (loaded FIRST) supersedes each Drive-era rule with its git equivalent; a FACTORY NOTICE banner tops every reference. Test guards both. |
| F6 | MINOR | `analyze-pass2` / `micro-feature` did not name the delegate lane for the analysis dispatch (delegate alignment). | `--lane analysis` stated explicitly. |
| F7 | MINOR | Latent bug in frontend agent1 (`relative_to` unguarded) surfaced once the toolset moved. | Guarded. |

## Second pass (completeness vs the current Claude Projects)
| # | Severity | Finding | Fix |
|---|---|---|---|
| F8 | **CRITICAL** | `P3.5 Test Generation` engine absent — yet both track splitters package `*-test-plan` artifacts. Test packages could never be produced. | `engines/P3.5` added; runs at the tail of pass 1 (backend tests) and pass 2 (frontend tests) before split. |
| F9 | **MAJOR** | `P-1 Master Registry Builder` (bootstrap) absent — nothing created `project-registry.md` initially. | `engines/P-1` + `/bootstrap` (once per platform) + `platform/` home for platform-level artifacts. |
| F10 | MAJOR | `P4.1/P4.2` audits, `P5`, `MASTER-REVIEWER`, `P-REG` stub absent. | `engines/optional/{P4.1,P4.2,P5,P-REG}` + `/audit`; MASTER-REVIEWER folded as a reference of the holistic reviewer. |
| F11 | MAJOR | Governing docs referenced but absent (versioning architecture, workspace reference, deployment manifest, stage-2 tools doc). | `shared/docs/`. |
| — | — | **Coverage now complete: all 33 original files accounted for** (`COVERAGE-MAP.md`, script-verified; integrity test extended). | |

## Delegate alignment (verified against the delegate-skills contract)
- Reviewers = `readOnly` lanes dispatched with `--lane <name> --read-only`;
  the reviewer never edits/commits — the orchestrator (Claude Code) owns
  review + commit. Matches `reviewers/*.md` and `commands/review-gate.md`.
- Model/effort per call via the brief/lane; explicit flags override lane dials.
- Codex not installed on the current machine → `review-holistic` runs on
  claude (different model than analysis) until codex is added; switching is a
  config edit (`LANES` / `.delegate` lane implementer), not a code change.

## Evidence
factory 7 · backend 40 · frontend 22 — all passing.
