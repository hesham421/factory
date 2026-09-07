# governance — the Analysis Factory

A standalone repo that owns **analysis, review, split and delivery** for every
module of the platform, both tracks. It **stops at delivery** — it never
implements. git is the only transport and the only ledger (no Drive).

```
domain/            ONE platform domain profile (+ per-module inherit sections)
shared/            shared governance loaded FIRST by every engine: FACTORY-PRECEDENCE (git supersedes Drive),
                   GOVERNANCE-CONFIG, rules, artifact contracts, AMEND-IFA, XM protocol, PROJECT-3-REGISTRY…
platform/          platform-level artifacts (project-registry, standards, indexes) — created by P-1 once
engines/           the governance engines as skills — SKILL.md (contract) + references/ (full engine)
                   P-1 (bootstrap, once) · domain-profile · P0 · P0.5 · P1 · P2 · P2.5 · P3.1 · P3.2 · P3.5 (tests)
                   optional/ P4.1 · P4.2 (audit → fix-prompts) · P5 (api-verify) · P-REG (retired stub)
governance-tools/  config.py (single source: tracks, REPOS, passes, gates, lanes)
                   gov.py (CLI: --track dispatch · version/tag · fetch-inputs · deliver · status)
                   tracks/backend, tracks/frontend  (proven, tested toolsets — unchanged code)
reviewers/         delegate briefs: per-engine review · holistic review
commands/          /bootstrap · /analyze-pass1 · /analyze-pass2 · /review-gate · /audit · /micro-feature · /link-repos
modules/[MOD]/     full analysis per module: v1 in the base folder, vN/ for extensions
delegate-skills/   how model/effort are controlled per call
_archive-v5/       snapshot of everything reached before the factory (reference only)
```

## The flow
```
BOOT    /bootstrap (P-1) once per platform → platform/project-registry.md
PASS 1  domain → P0 → P0.5 → P1* → P2* → P2.5 → P3.1* → P3.5 (backend tests)   (* = per-engine gate)
        → holistic gate (backend set, codex) → split backend → DELIVER (branch to backend repo)
        ── factory stops; outside: backend implements → publishes api-docs;
                                    frontend implements UI/UX → publishes ui-shell manifest ──
PASS 2  gov.py fetch-inputs (hard gate) → P3.2* → P3.5 (frontend tests) → holistic gate (integration)
        → split frontend → DELIVER (branch to frontend repo) → tag [mod]-vN
```
Extensions = the same flow on a new version (`/micro-feature`): delta mode,
Change Manifest, dependencies preserved, v[N-1] frozen + tagged.

See `COVERAGE-MAP.md` — every current Claude-Project file and its home here.

## Model / cost control
Every reasoning step is a delegate brief carrying implementer/model/effort
(defaults in `config.LANES`: analysis opus/high · per-engine review sonnet/
medium · holistic codex/high · merge notes low). Split/deliver/tag/fetch are
tools — zero model cost.

## Linking your repos
Edit `governance-tools/config.py` REPOS (url + checkout) — see
`commands/link-repos.md`. Agreed paths: backend publishes
`governance/api-docs/api-docs-<mod>.md`; frontend publishes
`governance/ui-shell/ui-shell-manifest-<mod>.md`; the factory delivers to
`governance/modules/<MOD>[/vN]/` on `gov/<mod>-vN-<track>`.

## Tests
```
cd governance-tools && python3 -m pytest tests/ -q                 # factory layer
cd governance-tools/tracks/backend  && python3 -m pytest tests/ -q  # backend toolset
cd governance-tools/tracks/frontend && python3 -m pytest tests/ -q  # frontend toolset
```
# factory
