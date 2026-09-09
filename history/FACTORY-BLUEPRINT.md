# FACTORY BLUEPRINT (approved 2026-09-07)

| Decision | Choice |
|---|---|
| Transport / ledger | git only (Drive cancelled). Versions = `modules/[MOD]/vN/` + tag `[mod]-vN`. Commits are the ledger. |
| Factory boundary | Domain → … → delivery. **Stops at delivery.** No implementation inside the factory. |
| Two passes | Pass 1 ends at P3.1 (backend delivered). Pass 2 = P3.2 only, gated on api-docs + ui-shell fetched back from the repos. |
| Repos linkage | config.REPOS (url, checkout, deliver_to, inputs, branch). Read-back of inputs via git; delivery via branch/PR. |
| Domain | One platform profile (once) + per-module inherit sections. |
| Per-engine review | 4 stations: P1, P2, P3.1, P3.2 — claude by default. |
| Holistic review | 2 gates: after pass 1 (backend), after pass 2 (integration) — codex by default. |
| Model/effort | Per call via delegate brief; defaults in config.LANES. |
| Tracks | Proven toolsets kept under tracks/; addressed via `gov.py --track`. `--track` is back (config unified). |
| Extensions | Same flow, new version, delta mode with Change Manifest; dependencies preserved. |
| Shared governance | `shared/` — loaded first; `FACTORY-PRECEDENCE.md` maps every Drive-era rule to its git equivalent. |
| Archive | `_archive-v5/` keeps everything reached before. |

Out of scope (happens inside the consumer repos): implementation, code
review, TestSprite tests, UI/UX execution.
