# Governance Factory — Project Reference

> A single, self-contained reference for continuing and improving this system
> in a **new Claude.ai project**. Everything needed to understand the design,
> the current state, what is proven, and what to work on next.

**Repositories**
- Factory (this system): **https://github.com/hesham421/factory.git**
- Delegation skills used for model/effort control: **https://github.com/amElnagdy/delegate-skills**

---

## 1. What this is (one paragraph)

A standalone **analysis factory**: a git repository that owns the *analysis,
review, splitting, and delivery* of every software module of a platform, for
**both** the backend and frontend tracks. It runs a chain of governance
"engines" (domain → requirements → database → UI/UX → execution plans → test
specs), reviews the output at defined gates, splits the execution plans into
implementable package files with deterministic tools, and **delivers** those
packages to the separate backend/frontend repositories over **git branches**.
It deliberately **stops at delivery** — it never implements code. Model choice
and cost are controlled per step through the `delegate-skills` fleet (lanes).

---

## 2. How this came to be (design decisions, in order)

The system evolved through a long design conversation. The decisions that shaped it:

1. **Two independent toolsets** (backend, frontend) already existed, each with
   `agent1_create_structure.py` (folders), `agent2_archive.py` (archiving),
   `agent3_splitter.py` (marker-based splitting), `config.py`, `marker_parser.py`.
2. **Incremental Feature Addition (IFA):** adding a feature to an already-built
   module must produce a **delta** analysis as a **new version** (v2, v3…),
   leaving the prior version **frozen**. Implemented via `--new-version`, a
   Change Manifest header (CS-ID, baseline, NEW/MODIFIED/UNCHANGED), and
   filesystem/registry version resolution.
3. **Module-qualified filenames** (`srs-<mod>.md`, `backend-execution-plan-<mod>.md`)
   so multiple modules can share a folder without collision and tools never
   sniff content to find the module. Defined once in `config.py`; **no hardcoded
   filenames** anywhere (guarded by tests).
4. **Governed Drive layout** was designed (§1E) then **cancelled** in favour of
   **git** as the single transport and ledger.
5. **Central factory repo** (`governance`, later `factory`): the analysis logic
   lives in one place and *distributes* results to the consumer repos. Backend
   and frontend become **consumers** that only implement.
6. **git replaces Drive** end-to-end: versions = folders + tags (`<mod>-vN`);
   the **commit is the ledger**; delivery = a branch/PR to each repo; pass-2
   inputs are pulled back from the repos via git.
7. **The factory stops at delivery**, and **implementation happens inside the
   consumer repos** (out of factory scope).
8. **Two-pass analysis** because of a real dependency gap: `P3.2` (frontend
   execution plan) needs the **real API Docs** (produced by *implementing* the
   backend) and the **real UI Shell** (produced by *implementing* UI/UX). So:
   - **Pass 1** runs `domain → … → P3.1` (+ backend test spec), delivers backend, **stops**.
   - Outside the factory: backend implements → publishes `api-docs`; frontend
     implements UI/UX → publishes `ui-shell manifest`.
   - **Pass 2** runs `P3.2` (+ frontend test spec) once those inputs are fetched back.
9. **Repos linked to the factory as git remotes** (config, not code): the
   factory delivers to them and reads their published inputs back for pass 2.
10. **Reviews via delegate:** analysis on the strong model; reviews as
    **read-only** lanes (a reviewer proposes, the orchestrator commits).
11. **Recommended review shape for a mature system:** per-engine review at 4
    stations (P1, P2, P3.1, P3.2); holistic review at 2 gates (after pass 1,
    after pass 2). Model/effort concentrated where it matters.
12. **Everything reached before the factory is archived** under `_archive-v5/`.

---

## 3. Repository layout (what is on GitHub now)

```
factory/
  domain/            ONE platform domain profile (+ per-module inherit sections)
  platform/          platform-level artifacts (project-registry, standards, indexes) — created by P-1 once
  engines/           governance engines as skills — each: SKILL.md (contract) + references/ (full engine text)
    P-1/             Master Registry Builder (BOOTSTRAP, once per platform)
    domain-profile/  Domain Profile builder (entry of analysis)
    P0/  P0.5/  P1/  P2/  P2.5/  P3.1/  P3.2/  P3.5/
    optional/  P4.1/ P4.2/ (audit → fix-prompts) · P5/ (api-verify) · P-REG/ (RETIRED stub)
  governance-tools/
    config.py        SINGLE source of truth: tracks, REPOS, passes, gates, lanes, versioning
    gov.py           factory CLI: --track dispatch · version/tag · fetch-inputs · deliver · status
    tests/           factory-layer tests (7)
    tracks/backend/  proven backend toolset (agent1/2/3, config, marker_parser) + tests (40)
    tracks/frontend/ proven frontend toolset + tests (22)
  reviewers/         delegate briefs: per-engine-review.md · holistic-review.md (+ references/MASTER-REVIEWER.md)
  commands/          slash commands (copy to .claude/commands/ to activate in Claude Code):
                     bootstrap · analyze-pass1 · analyze-pass2 · review-gate · audit · micro-feature · link-repos
  shared/            governance loaded FIRST by every engine:
                     FACTORY-PRECEDENCE.md (git supersedes Drive — READ FIRST),
                     GOVERNANCE-CONFIG.md, shared-governance-rules.md, shared-artifact-contracts.md,
                     AMEND-IFA…, XM-RESOLUTION-EVENT-PROTOCOL.md, PROJECT-3-REGISTRY.md, MASTER-REGISTRY-SCHEMA.md,
                     SHARED-GOVERNANCE-CORE.md, START-HERE.md, docs/ (versioning arch, workspace ref, deployment, stage-2 tools)
  delegate-skills/   how model/effort is controlled per call (install note)
  _archive-v5/       snapshot of the pre-factory system (reference only)
  COVERAGE-MAP.md    every original Claude-Project file → its home here (all 33 accounted for)
  REVIEW-REPORT-2026-09-07.md   audit findings F1–F11 and their fixes
  README.md · FACTORY-BLUEPRINT.md · PYTEST-EVIDENCE.txt
```

> **Activation note:** Claude Code only registers slash commands under
> `.claude/commands/`. To use them: `mkdir -p .claude/commands && cp commands/*.md .claude/commands/`
> then start Claude Code from the repo root. (This was discovered during first-run testing.)

---

## 4. The flow (end to end)

```
BOOT    /bootstrap (engine P-1) — once per platform → platform/project-registry.md

PASS 1  domain-profile → P0 → P0.5 → P1* → P2* → P2.5 → P3.1* → P3.5(backend test spec)
        → holistic gate (after pass 1)  → split backend (tools) → DELIVER (branch → backend repo) → STOP
        (* = per-engine review gate)

  ── outside the factory (in the consumer repos) ──
  backend repo  : implement the plan → publish  governance/api-docs/api-docs-<mod>.md
  frontend repo : implement UI/UX     → publish  governance/ui-shell/ui-shell-manifest-<mod>.md

PASS 2  gov.py fetch-inputs (HARD GATE: needs both published inputs) → P3.2* → P3.5(frontend test spec)
        → holistic gate (after pass 2, integration) → split frontend (tools) → DELIVER (branch → frontend repo)
        → tag <mod>-vN   (freezes the version)
```

**Extensions** (`/micro-feature`) run the *same* flow on a **new version** in
delta mode (Change Manifest, dependencies preserved, prior version frozen +
tagged). A backend-only or frontend-only extension simply skips the empty track.

---

## 5. Model / cost control via delegate-skills (lanes)

Every reasoning step is a **self-contained brief** dispatched to a **lane**;
mechanical steps use tools (no model, no cost). The lanes as defined in
`governance-tools/config.py` (the source of truth):

| Lane | Implementer | Model | Effort | Notes |
|---|---|---|---|---|
| `analysis` | claude | opus | high | engine analysis stages |
| `merge-review-notes` | claude | sonnet | low | apply review fixes |
| `review-per-engine` | claude | sonnet | medium | read-only in use (P1,P2,P3.1,P3.2) |
| `review-holistic` | codex | default | high | read-only; independent model |
| `split` | tools | — | — | agent3, no model |
| `deliver` | tools | — | — | gov.py, no model |

**The user's active fleet on their machine** (written by `/delegate-setup`,
global config) currently is claude-only because codex is not installed:

```json
{
  "version": "delegate-fleet.v1",
  "lanes": {
    "analysis":           { "implementer": "claude", "model": "opus",   "effort": "high",   "timeout": "2h" },
    "merge-review-notes": { "implementer": "claude", "model": "sonnet", "effort": "low",    "timeout": "30m" },
    "review-per-engine":  { "implementer": "claude", "model": "sonnet", "effort": "medium", "timeout": "30m", "readOnly": true },
    "review-holistic":    { "implementer": "claude", "model": "fable",  "effort": "high",   "timeout": "1h",  "readOnly": true }
  }
}
```

**Dispatch pattern (from the commands):**
```
$claude-delegate --lane analysis          --brief <brief>
$claude-delegate --lane review-per-engine --read-only --brief <brief>
$claude-delegate --lane review-holistic   --read-only --brief <brief>
gov.py structure|archive|split|deliver …   (tools — no lane)
```
Explicit `--model`/`--effort` flags override the lane per call. A read-only
lane means the reviewer never edits/commits — **the orchestrator lands the
commit** (the delegate-skills contract).

**Known divergence to reconcile:** `config.LANES` names `review-holistic`
implementer as `codex` (the intended end state), but codex is not installed on
the current machine, so the live fleet uses `claude/fable` for it. When codex
is installed, switch that one lane's implementer back to `codex` (config edit,
no code change).

---

## 6. git-native mechanics (what replaced Drive)

| Concern | Mechanism |
|---|---|
| Versions | folders `modules/<MOD>/` (v1) and `modules/<MOD>/vN/` (N≥2) + tag `<mod>-vN` |
| Ledger | the **git commit** per stage (message = `"<engine>: <MOD> vN — …"`) |
| Delivery | `gov.py deliver` copies a track's packages + execution-state into the consumer repo checkout and commits on branch `gov/<mod>-vN-<track>` (optional `--push`) |
| Pass-2 inputs | `gov.py fetch-inputs` pulls `api-docs`/`ui-shell` from the linked repos into `modules/<MOD>[/vN]/_inputs/`; a hard gate blocks P3.2 until both exist |
| Linking repos | `config.REPOS` (url + checkout + agreed input paths + delivery branch) — see `commands/link-repos.md` |

Agreed published paths the consumer repos must honour:
- backend → `governance/api-docs/api-docs-<mod>.md`
- frontend → `governance/ui-shell/ui-shell-manifest-<mod>.md`

---

## 7. Governance rules still in force (unchanged from the mature system)

- **Module-qualified names** for every per-module artifact; no hardcoded names.
- **PHASE / SUB / TC markers** (PROJECT-3-REGISTRY §5.7) drive the splitter.
- **Change Manifest + IFA versioning** for any extension.
- **Inline REGISTRY step** in each engine (the retired P-REG's job): it emits
  `registry-<stage>-<mod>.md` and updates the project registry in the same commit.
- **Dependency preservation:** XM (cross-module), UXD (cross-screen), ALIGN
  (plan↔DB / plan↔API) must resolve; a breaking change STOPS and escalates.
- **Test specs are framework-agnostic** (TC-BE / TC-FE), executed later by
  **TestSprite** inside the repos — no JUnit/Playwright scaffolding in the factory.
- **Audit output = fix-prompts** grouped by owning engine (optional P4.1/P4.2).

---

## 8. Verification status (what is proven)

Run against the actual pushed repo (fresh clone), all green:

| Suite | Result |
|---|---|
| `governance-tools/tests` (factory layer: versioning, pass-2 gate, delivery to a real git repo, dispatch, structure integrity) | **7 passed** |
| `governance-tools/tracks/backend/tests` | **40 passed** |
| `governance-tools/tracks/frontend/tests` | **22 passed** |
| **Total** | **69 passed** |

Live smoke tests also passed: `gov.py version/status/structure` create the
correct `modules/<MOD>/…` paths; `gov.py deliver` creates a real branch
`gov/<mod>-v1-backend` in a throwaway backend repo with packages in the right
place and the correct commit message; track separation holds (frontend never
lands in the backend repo). A live `$claude-delegate --lane review-per-engine
--read-only` run correctly returned a structured `VERDICT: REVISE` on a planted
duplicate-ID artifact without editing any file.

**How to reproduce:**
```
git clone https://github.com/hesham421/factory.git && cd factory
cd governance-tools && python3 -m pytest tests/ -q
cd tracks/backend  && python3 -m pytest tests/ -q
cd ../frontend     && python3 -m pytest -q
```

---

## 9. What is NOT yet proven / open items (the improvement backlog)

1. **Real end-to-end analysis run** (bootstrap → P3.1 for a real module) has
   been *started* via a background subagent but not yet confirmed complete with
   its hand-off report. The engines' *reasoning* content (as opposed to the
   tools/flow) is unverified in a live run.
2. **True per-lane dispatch vs. subagent substitution.** On the current
   machine (claude-only, no codex, `codex-delegate` skill not installed), the
   orchestrator tends to perform stages/reviews itself instead of shelling out
   to a separate implementer per lane. Design intent is an explicit
   `$claude-delegate --lane <name>` per step (even when the implementer is
   claude) so review runs are separate sessions with real `readOnly`. Reconcile.
3. **codex not installed** → `review-holistic` runs on claude/fable instead of a
   different model family. Install codex to get genuine independent review.
4. **Consumer repos not linked yet** → `gov.py deliver`/`fetch-inputs` will not
   push/pull until `config.REPOS` urls + checkouts are set. Delivery commits
   locally in the meantime (expected, not an error).
5. **Slash commands** must be copied to `.claude/commands/` (and committed) to
   register in Claude Code — not auto-discovered from `commands/`.
6. **Engine references still carry Drive-era prose**, superseded by
   `shared/FACTORY-PRECEDENCE.md` (loaded first). A future cleanup could rewrite
   the references themselves to be git-native rather than relying on precedence.
7. **Two track toolsets are not merged** into one `--track`-aware splitter; they
   are the proven V5 code kept side by side. A future consolidation is possible
   but was deliberately deferred to avoid destabilising tested code.
8. **RTL/Arabic in terminal briefs** renders visually reversed (cosmetic; the
   content processed is correct). Prefer English in briefs during testing.

---

## 10. Glossary (engine → role)

| Engine | Role |
|---|---|
| P-1 | Master Registry Builder — platform bootstrap (once) |
| domain-profile | Domain Profile — analysis entry |
| P0 | Platform Inception — platform summary, module registry, business policies |
| P0.5 | PRD |
| P1 | SRS (requirements) — **review gate** |
| P2 | Database script — **review gate** |
| P2.5 | UI/UX design (flow diagram + spec) |
| P3.1 | Backend execution plan — **review gate**; pass-1 end |
| P3.2 | Frontend execution plan — **review gate**; pass-2 (needs api-docs + ui-shell) |
| P3.5 | Test-case spec (backend/frontend) — TestSprite-ready |
| P4.1/P4.2 | Governance audit → fix-prompts (optional) |
| P5 | API verify (optional, post-implementation) |
| P-REG | RETIRED — registry extraction is now inline in each engine |

---

## 11. Suggested first tasks in the new project

1. Complete and capture one **real `/analyze-pass1 DEMO` run**; save the
   hand-off report and any REVISE findings as the first end-to-end evidence.
2. Decide and document the **explicit per-lane dispatch** convention so reviews
   are real separate read-only runs (item 9.2), and update the commands if needed.
3. Install **codex** and flip `review-holistic` to it (item 9.3).
4. **Link the repos** (`config.REPOS`) and prove `deliver --push` + a full
   pass-1 → implement → `fetch-inputs` → pass-2 cycle on the DEMO module.
5. Optionally rewrite engine references to be **git-native** (item 9.6).
