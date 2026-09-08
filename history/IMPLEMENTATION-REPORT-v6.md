# Implementation report — Governance Factory v6 (2026-09-08)

```
Scope     : blueprint FACTORY-BLUEPRINT-v6 §12 migration order, steps 1–6, executed
Baseline  : factory-main as uploaded (v5) — commit `baseline`
Result    : lint 0/0/0 · 85 tests green · end-to-end dry run (ERP + non-ERP toy profile)
Repo      : 4 milestone commits on top of the baseline (M1 → M6)
```

## ملخّص عربي

نُفِّذ التصميم بالكامل كما اعتمدته: **مصدر حقيقة واحد** (`factory.yaml` + `profiles/<domain>.yaml`) تُولَّد منه كل الوثائق والـ SKILL والأوامر؛ **الدومين صار بيانات** (ERP ملف واحد، ودومين "عيادة" تجريبي غير-ERP يمرّ في نفس الخط كاملاً)؛ **أداة واحدة** بدل نسختين؛ **منسّق `gov.py` يفرض** البروتوكول (state → brief → write → analyze → commit → gate)، والأسئلة محصورة في domain-profile/P0/P0.5، وقرارك البشري = اعتماد الـ PRD + بوابة واحدة لكل Pass؛ **آليات النضج مفعّلة في الكود**: EARS، التتبّع، `analyze` الآلي لـ ٨٠ بنداً عقدياً، رُبريك 29148، تيار ADR، delta + حالة كاملة مولَّدة. حُذف نهائياً P4.1/P4.2/P-REG/`/audit`/ui-shell وكل وثائق حقبة Drive؛ P5 وTest-Gen مرحلتان مستقلتان خارج الخط. الـ lint نظيف تماماً (كان ٥٢٨ إشارة لمفاهيم محذوفة + ٩٥ literal مجالياً)، ٨٥ اختباراً ناجحاً، وتجربة كاملة من الفكرة حتى التسليم والوسم على ERP وعلى دومين غير-ERP.

## What was built (by milestone)

| Milestone | Delivered |
|---|---|
| **M1 single source of truth** | `factory.yaml` (stages, passes, gates, lanes, paths, naming, ID grammar incl. EARS patterns, marker grammar with `traces=`, tracks, repos, delivery state schema, review rubric, ambiguity rule, lint rules) · `profiles/_schema.yaml` · `profiles/erp.yaml` (every ERP fact moved out of engines/tools/docs) · `profiles/erp/knowledge/erp-domain-standards.md` (replaces the never-existing `platform-standards.md §M`) · `config.py` loader (zero literals) · `lint.py` (C1–C5 enforcement: profile schema, removed concepts, domain literals, code literals, generated-file freshness, duplicate trees). |
| **M2 one toolkit** | `governance-tools/toolkit/` — `markers` (grammar from config + profile phases; multi-marker tokeniser, tree, uniqueness, semantics, refuse-unknown-phase, foreign-kind detection, `traces=` attribute, safe autofix with `.orig`), `structure`, `archive`, `splitter` (per-phase / flat, headers, `_SECTIONS.md`, index, SHA-256 verification of every atom and unit, `state.json`, manifest status). Both old track toolsets (~1,900 duplicated lines) deleted. Non-interactive. |
| **M3 orchestrator** | `gov.py` — `run-stage`, `run-pass` (bundled brief = one delegate session per pass), `gate` (analyze must be CLEAN → reviewer brief → scorecard record), `approve` (PRD approval), `analyze`, `state`, `version`, `tag`, `fetch-inputs` (api-docs only), `deliver` (branch + generated `execution-state.json`), `status`, `split/structure/archive`, `render`, `lint`, `new-domain`. `idmodel.py` (one reading of IDs/records/traces), `state.py` (delta folding: marker blocks into their phase, records carried under a baseline marker; traceability matrix; freshness), `analyze.py` (all 12 clause kinds of ARTIFACT-CONTRACTS.md — 80 clauses over 12 contracts), `dispatch.py` (briefs from ENGINE.md templates + `_state/` + knowledge; lanes with implementer lists; dialogue rounds until `<!-- CONVERGED -->`; manual / cmd / fake runners; file-block ingestion; `[QUESTION]` refusal; BLOCKED-ADR stop), `render.py` + templates (SKILL.md ×10, commands ×11, README, START-HERE, RENDER blocks in shared docs). |
| **M4 shared docs** | 8 domain-neutral core docs (CONSTITUTION, GOVERNANCE-CORE, ARTIFACT-CONTRACTS with machine-readable front-matter, MARKER-PROTOCOL, XM-PROTOCOL, REGISTRY-SCHEMA Part A, VERSIONING, QUALITY-RUBRIC) + generated START-HERE; single gate template `reviewers/pass-review.md`; legacy/Drive/15-projects docs deleted; pre-v6 artefacts moved to `history/`. |
| **M5 engines** | 8 pipeline engines + 2 standalone rewritten as Jinja2 templates with `{{ profile.* }}` slots (12,285 → ~3,200 lines): P1 = EARS + AC + traceability + ambiguity rule; domain-profile = research step + dual-implementer dialogue + steering block; P2.5 ⊕ P3.2 merged; P3.5 → `standalone/test-gen` (TC derived from AC), P5 → `standalone/api-verify`; P4.1/P4.2/P-REG deleted with every dangling reference. |
| **M6 verification** | End-to-end dry run under ERP: domain-profile → P-1 → pass 1 (bundled brief) → PRD approval → P1/P2/P3.1 → gate 1 → split → deliver → api-docs back → pass 2 → gate 2 → split → deliver → tag → test-gen (standalone) → analyze `all` CLEAN. Same run under a non-ERP clinic profile (different prefixes, phases, one language, other stack). Delta version: folding + continuity (re-minting with changed content is CRITICAL). `new-domain` scaffold + lint. 85 tests, lint 0/0/0. |

## How the constitution is enforced (not just written)

| Principle | Mechanism now in code |
|---|---|
| C1 single source of truth | every table/SKILL/command/README/START-HERE generated; `lint` fails on stale render or a second command tree |
| C2 no hardcode | `lint` scans engines/shared/reviewers/tools for removed concepts and for the profile's own vocabulary/stack tokens; python may not spell stage ids, phase keys or ID prefixes |
| C3 no contradictions | precedence file deleted; superseded text removed at the source; `analyze` cross-checks artifacts against contracts |
| C4 no duplication | one toolkit, one parser, one gate template, one command tree, rules stated once and linked |
| C5 no exceptions | profile schema is the only place variability is declared; `lint --profile` validates every profile |
| C6 minimal questions | `questions: allowed` only on domain-profile/P0/P0.5; the orchestrator refuses `[QUESTION]` elsewhere; PRD approval + one gate per pass are the only human points |

## Baseline → now (measured)
- Removed-concept references: **528 → 0**; domain literals outside profiles: **95 → 0**.
- Engine references: **12,285 → 3,193 lines**, domain-neutral, template-rendered.
- Toolkits: **2 divergent copies → 1**; tests **69 → 85** (now covering orchestrator, contracts, delta folding, agnosticism).
- Stage list stated in **10+ files → 1** (`factory.yaml`), rendered everywhere.

## Operating model (what runs where)
- Reasoning steps (stages, dialogue, review) run through **lanes**. Default runner is `manual`: `gov.py` writes a self-contained brief under `modules/<MOD>/_state/briefs/`, exits with code 2, and the operator (Claude Code with delegate skills — Claude-only implementer lists per your decision) executes it and re-invokes with `--complete`. `GOV_RUNNER=cmd` automates the same loop through any CLI model runner; dialogue lanes alternate implementers until convergence.
- Mechanical steps (state, analyze, split, deliver, tag, fetch-inputs, render, lint) run with no model.
- The domain-profile stage stays conversational (your decision): its saved `domain/domain-profile.md` is the entry gate.

## Decisions taken during implementation (all reversible in data, none in code)
1. `SCR-REQ` added to the core ID atoms (owner P1, traces REQ) — P1 declares screen requirements, P3.2 mints `SCR`.
2. `TC` uses the core grammar `TC-{MOD}-{seq}` (one sequence across both test plans).
3. A registry never *defines* IDs (it lists them); a marker block or heading restating an upstream ID is a reference — `ids-owned` fires only when a stage mints an ID its owner never defined.
4. A delta may restate an unchanged record verbatim; changed content without `MODIFIED` is CRITICAL.
5. Contracts are evaluated when their **last owner** completes; contracts consumed by standalone stages only once that stage ran; `gate-approved` clauses on the consumer's side.
6. The five defaults of blueprint §11 stand (reuse as concept, testing from profile, mockups as design artifact, languages from profile, generated execution-state).

## Known limits / next steps
- The runners deliver briefs; actual model execution is the operator's (delegate skills) or a `GOV_RUNNER_CMD`. No model is called from the repo itself.
- `analyze` reads IDs by the documented text conventions (heading/marker definitions, `Traces:` lines, `[brackets]`, `traces=`); engines are written to emit exactly these. A profile that wants extra atoms adds them under `profile.ids.atoms`.
- `_archive-v5/` is kept untouched as the pre-factory snapshot (lint-exempt); delete it whenever you no longer need it.
- Real consumer repos: set `factory.yaml → repos` (or the `GOV_*_CHECKOUT` env) — the dry run used temporary git repos.
