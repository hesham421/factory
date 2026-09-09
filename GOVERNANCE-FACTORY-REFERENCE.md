# Governance Factory — Project Reference

> A single, self-contained reference for continuing and improving this system
> from a **separate Claude project** (the GOVERNANCE-FACTORY project) that
> discusses and decides, then hands prompts down to this repo to execute.
> This describes the **v6** design. Facts that can drift (exact tables, test
> counts, command list) are not restated here — they are generated or
> reproducible; follow the pointers to the live source.

**Repositories**
- Factory (this system): **https://github.com/hesham421/factory.git**
- Delegation skills used for model/effort control: **https://github.com/amElnagdy/delegate-skills**

---

## 1. What this is (one paragraph)

A standalone **analysis factory**: a git repository that owns the *analysis,
review, splitting, and delivery* of every software module of a platform, for
**both** the backend and frontend tracks. It runs a chain of governance
"engines" (domain profile → platform inception → PRD → SRS → database →
backend execution plan → frontend UX design + execution plan), reviews the
output at defined gates, splits the execution plans into implementable
package files with deterministic tools, and **delivers** those packages to
the separate backend/frontend repositories over **git branches**. It
deliberately **stops at delivery** — it never implements code, never audits
an implementation, never runs tests inside the line. Model choice and cost
are controlled per step through **lanes** (`factory.yaml → lanes`), optionally
backed by the `delegate-skills` fleet.

The full binding rule set is `shared/CONSTITUTION.md` (six principles, C1–C6).
The single source of truth for every stage/pass/gate/lane/naming/ID/marker
fact is `factory.yaml`; everything generated from it (SKILL.md files, the
`.claude/commands/` tree, README.md, START-HERE.md) is produced by
`python governance-tools/gov.py render` and kept fresh by `gov.py lint`.

---

## 2. How this came to be (design decisions, in order)

The system evolved through two generations. v5 (archived under
`_archive-v5/`) proved the concept with two independent toolsets (backend,
frontend) and Drive-based delivery; **v6** (the live system) is a full
redesign on top of what v5 proved:

1. **Two independent toolsets** (backend, frontend) existed in v5, each with
   its own structure/archive/splitter/config/marker-parser scripts. v6
   replaced both with **one domain-agnostic toolkit**
   (`governance-tools/toolkit/`) that reads its grammar from `factory.yaml` +
   the active profile.
2. **Incremental Feature Addition (IFA):** adding a feature to an
   already-built module produces a **delta** analysis as a **new version**
   (v2, v3…), leaving the prior version **frozen**. Implemented via
   `gov.py version --new`, a Change Manifest, and filesystem/registry version
   resolution (`shared/VERSIONING.md`).
3. **Module-qualified filenames** (`srs-<mod>.md`, `backend-execution-plan-<mod>.md`)
   so multiple modules can share a folder without collision. The naming
   grammar is declared once in `factory.yaml → naming`; no hardcoded
   filenames anywhere (guarded by `gov.py lint`).
4. **A governed Drive layout was designed in v5, then permanently cancelled**
   in favour of **git** as the single transport and ledger. v6 removes every
   remaining trace of Drive-era design (`Google Drive`, `GOVERNANCE-ROOT`,
   `journey_loader`, `platform-standards.md` are on the v6 forbidden-terms
   list enforced by `gov.py lint`).
5. **Central factory repo:** the analysis logic lives in one place and
   *distributes* results to the consumer repos. Backend and frontend become
   **consumers** that only implement.
6. **git-native end to end:** versions = folders + tags (`<mod>-vN`); the
   **commit is the ledger**; delivery = a branch to each repo
   (`factory.yaml → repos[*].deliver_to`); pass-2 inputs are pulled back from
   the repos via `gov.py fetch-inputs`.
7. **The factory stops at delivery**, and **implementation happens inside the
   consumer repos** (out of factory scope) — unchanged from v5 through v6.
8. **v6 domain-agnostic rewrite:** a domain became **data**
   (`profiles/<id>.yaml`, validated against `profiles/_schema.yaml`) instead
   of prose baked into engine text. Every engine is now a Jinja2 template
   (`engines/<id>/references/ENGINE.md`) rendered with `{{ profile.* }}`
   slots, so adding a domain never touches engine text.
9. **v6 merged the two-gate review shape into one review-pass gate**: rather
   than a per-engine review plus a separate holistic review, each pass
   (backend = pass 1, frontend = pass 2) has exactly **one** review gate
   (`factory.yaml → gates`, lane `review-pass`), scored against the same
   29148 rubric (`shared/QUALITY-RUBRIC.md`).
10. **v6 collapsed the frontend UX-design and execution-plan stages into a
    single stage `P3.2`.** It also dropped the former hard dependency on a
    published "UI shell" artifact — `P3.2`'s only required upstream input
    from the backend track is `api-docs` (`factory.yaml → inputs`).
11. **v6 permanently removed the governance-audit engines, the registry-
    extraction engine, and their command** — the retired ids are listed in
    `factory.yaml → lint.forbidden_terms`, which is the authoritative record
    of exactly what was removed (see also `history/IMPLEMENTATION-REPORT-v6.md`
    milestone M5). Registry extraction is now inline in each stage (every
    stage emits its own `registry-<stage>-<mod>.md` as one of its `produces`).
12. **Reviews via lanes:** analysis runs on a strong-model lane
    (`factory.yaml → lanes.analysis`); reviews run on a **read-only** lane
    (`lanes.review-pass`) — a reviewer proposes, the orchestrator commits.
13. **Everything superseded by v6 is archived** under `_archive-v5/` (the v5
    snapshot) and `history/` (the v6 migration record), both exempt from
    lint and left untouched by day-to-day work.

---

## 3. Repository layout (current, v6)

```
factory.yaml                 SINGLE source of truth: stages, passes, gates, lanes, paths,
                              naming, ID grammar, marker grammar, tracks, repos, review rubric, lint rules
profiles/                    a domain is DATA: _schema.yaml + <id>.yaml (+ <id>/knowledge/*.md)
domain/                      domain-profile.md saved from the conversational domain-profile stage
platform/                    P-1 output: project-registry.md (bootstrap, once per platform)
engines/                     the governed pipeline — one folder per stage in factory.yaml -> stages,
                              each: SKILL.md (generated) + references/ENGINE.md (Jinja2 template)
standalone/                  stages outside the line, on demand, never a gate (per factory.yaml -> standalone)
shared/                      the domain-neutral core doc set (CONSTITUTION, GOVERNANCE-CORE,
                              ARTIFACT-CONTRACTS, MARKER-PROTOCOL, XM-PROTOCOL, REGISTRY-SCHEMA,
                              VERSIONING, QUALITY-RUBRIC + generated START-HERE)
reviewers/pass-review.md     the single gate review template (one gate type, used by every pass)
decisions/<MOD>/             ADR stream
modules/<MOD>/[vN/]          v1 = base folder, vN = delta only; _state/ generated current state;
                              _inputs/ fetched inputs; packages/ split output
.claude/commands/            thin command wrappers — fully generated from factory.yaml -> commands
                              by `gov.py render` (nothing here is hand-written or hand-added)
governance-tools/            config.py (loader) · gov.py (orchestrator CLI) · render.py · lint.py ·
                              analyze.py · state.py · idmodel.py · dispatch.py ·
                              toolkit/ (one parser/splitter/structure/archive, domain-agnostic) · tests/
delegate-skills/             how model/effort is controlled per lane (install note; the lanes
                              themselves are data in factory.yaml -> lanes)
_archive-v5/                 snapshot of the pre-v6 system (reference only, lint-exempt, untouched)
history/                     the v6 migration record (blueprint, implementation report, coverage
                              map, review report, pytest evidence), lint-exempt, untouched
README.md                    generated overview + pipeline map (run `gov.py render` to refresh)
```

There is no separate `commands/` folder to copy into `.claude/commands/` —
`.claude/commands/` **is** the live command tree; `gov.py render` writes it
directly and deletes anything not declared in `factory.yaml → commands`.

For the exact current stage list, gate list, lane list, command list, and
active profile, read `README.md` (generated) or run `gov.py render` — do not
copy those tables into this file, or they will go stale again the way this
document itself did.

---

## 4. The flow (end to end)

```
BOOT    /bootstrap (engine P-1) — once per platform → platform/project-registry.md

PASS 1  domain-profile → P0 → PRD approval (human) → P1 → P2 → P3.1
        → gate:pass-1 (one review-pass gate)  → split (tools) → deliver (branch → backend repo)

  ── outside the factory (in the consumer repos) ──
  backend repo  : implement the plan → publish  governance/api-docs/api-docs-<mod>.md

PASS 2  gov.py fetch-inputs (HARD GATE: needs api-docs published) → P3.2
        → gate:pass-2 (one review-pass gate) → split (tools) → deliver (branch → frontend repo)
        → tag <mod>-vN   (freezes the version)
```

All stages of a pass run in **one bundled delegate session**, one commit per
stage (`factory.yaml → passes.<n>.session: bundled`). `test-gen` and
`api-verify` are standalone stages: they run on demand, outside the line, and
are never a gate for the core pipeline.

**Extensions** (`/micro-feature`) run the *same* flow on a **new version** in
delta mode (Change Manifest, dependencies preserved, prior version frozen and
tagged). A backend-only or frontend-only extension simply skips the empty
track.

---

## 5. Model / cost control via lanes

Every reasoning step is a **self-contained brief** dispatched to a **lane**;
mechanical steps (state, analyze, split, deliver, tag, fetch-inputs, render,
lint) use tools — no model, no cost. Lanes are declared once, in
`factory.yaml → lanes`, and rendered into `shared/GOVERNANCE-CORE.md` and
`README.md` by `gov.py render`; that table is the source of truth, not this
document.

**Default: Claude only.** Every implementer entry shipped in `factory.yaml`
is a Claude model; no other provider or tool is required to run the factory.
Adding or swapping a provider for a lane is an edit to `factory.yaml → lanes`
— it never touches an engine, a reviewer, or a command.

`delegate-skills/README.md` documents the mechanism itself (how a lane is
structured, dialogue convergence, the read-only contract for review gates,
and that the orchestrator — never the implementer — lands every commit).

---

## 6. git-native mechanics

| Concern | Mechanism |
|---|---|
| Versions | folders `modules/<MOD>/` (v1) and `modules/<MOD>/vN/` (N≥2) + tag `<mod>-vN` |
| Ledger | the **git commit** per stage (`factory.yaml → naming.commit.stage`) |
| Delivery | `gov.py deliver --track <backend\|frontend>` copies a track's packages + `execution-state.json` into the consumer repo checkout and commits on the branch named by `factory.yaml → naming.delivery_branch` |
| Pass-2 inputs | `gov.py fetch-inputs` pulls `api-docs` from the linked backend repo into `modules/<MOD>[/vN]/_inputs/`; a hard gate blocks `P3.2` until it exists |
| Linking repos | `factory.yaml → repos` (url + checkout env/default + `deliver_to` + `publishes`) — edit directly or via `/link-repos` |

The one published input the backend repo must honour (declared once, in
`factory.yaml → inputs`):
- backend → `governance/api-docs/api-docs-<mod>.md`

There is no published "UI shell" input in v6 — `P3.2` does not require one.

---

## 7. Governance rules still in force

- **Module-qualified names** for every per-module artifact; no hardcoded
  names (`factory.yaml → naming`).
- **PHASE / SUB markers** (`shared/MARKER-PROTOCOL.md`, grammar in
  `factory.yaml → markers`) drive the splitter.
- **Change Manifest + IFA versioning** for any extension
  (`shared/VERSIONING.md`).
- **Inline registry step** in every stage: each stage that owns IDs emits
  `registry-<stage>-<mod>.md` and updates the project registry in the same
  commit — there is no separate registry-extraction engine.
- **Dependency preservation:** cross-module (`XM`) and cross-screen (`UXD`)
  references must resolve; a breaking ambiguity after PRD approval writes a
  `BLOCKED` ADR and stops the pass (`factory.yaml → ambiguity`,
  `shared/GOVERNANCE-CORE.md § ambiguity`).
- **Test specs are framework-agnostic**, produced by the standalone
  `test-gen` stage, derived from acceptance criteria (`AC → TC`).
- The six constitutional principles (C1 single source of truth, C2 no
  hardcode, C3 no contradictions, C4 no duplication, C5 no exceptions, C6
  minimal questions) are enforced in code by `gov.py lint`, not just written
  down — see `shared/CONSTITUTION.md`.

---

## 8. Verification status

Run the toolkit's own test suite for the current, exact count — this
document does not restate it:

```
git clone https://github.com/hesham421/factory.git && cd factory
python governance-tools/gov.py lint            # constitution enforcement — must be 0 critical / 0 major / 0 minor
python -m pytest governance-tools/tests -q     # the toolkit + orchestrator test suite
```

`governance-tools/tests` covers the unified toolkit (structure, archive,
split, markers), the orchestrator (`gov.py` stage/pass/gate/version/deliver
flow), delta-version folding and continuity, contract analysis, and
domain-agnosticism (the same pipeline exercised under a second, non-ERP toy
profile) — there is a single test tree; the divided per-track test layout
from v5, with a separate toolset and test folder for each of the backend and
frontend tracks, no longer exists (see `_archive-v5/` for that snapshot).

See `history/IMPLEMENTATION-REPORT-v6.md` for the migration record (what
changed, milestone by milestone, and the before/after numbers measured at
the time of the v6 rewrite) and `history/REVIEW-REPORT-2026-09-07.md` for
the audit findings that preceded it. Both are historical snapshots, not live
status — for live status, run the commands above.

---

## 9. What is NOT yet proven / open items

1. **Consumer repos not linked yet in this checkout** — `gov.py
   deliver`/`fetch-inputs` will not push/pull until `factory.yaml → repos`
   urls and checkouts are set for this environment. Delivery commits locally
   in the meantime (expected, not an error).
2. **A real end-to-end analysis run on a live module** (bootstrap through
   delivery, both passes, against real consumer repos) has not yet been
   captured as evidence in this reference. `modules/DEMO/` holds a real
   historical dry-run record (see `modules/DEMO/_state/briefs/*.md`) but not
   a run against linked, real repos.
3. **RTL/Arabic in terminal briefs** can render visually reversed in some
   terminals (cosmetic; the content processed is correct). Prefer English in
   briefs while testing terminal-specific behavior.

---

## 10. Glossary (stage → role)

For the authoritative, current stage table (title, pass, questions policy,
lane, inputs, produces, owned ID atoms, and what runs next) read the
generated `<!-- RENDER:stages -->` block in `README.md`, or run `gov.py
render` after any change to `factory.yaml`. As of this writing the pipeline
is: `domain-profile → P-1 → P0 → P0.5 (PRD) → P1 (SRS) → P2 (Database) →
P3.1 (Backend Execution Plan) → [gate: pass-1] → P3.2 (Frontend UX Design +
Execution Plan) → [gate: pass-2]`, with `test-gen` and `api-verify` as
standalone stages outside the line. Every stage id, its title, and its role
are declared exactly once, in `factory.yaml → stages` / `factory.yaml →
standalone` — this glossary intentionally does not duplicate that table.

---

## 11. Suggested next tasks

1. **Link the consumer repos** (`factory.yaml → repos`) and prove `deliver
   --push` + a full pass-1 → implement → `fetch-inputs` → pass-2 cycle on a
   real module, against real backend/frontend checkouts.
2. **Capture a real end-to-end analysis run** (bootstrap → pass 1 → pass 2 →
   tag) on a live module as fresh evidence, alongside the `modules/DEMO/`
   dry-run record.
3. Keep this document itself honest: whenever `factory.yaml` changes shape
   (a stage added/removed/renamed, a gate merged or split, a lane renamed),
   re-check this file's §§3–7 against `README.md` and `shared/CONSTITUTION.md`
   rather than letting it drift the way the pre-v6 version of this document did.
