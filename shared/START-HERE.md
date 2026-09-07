# START HERE — ERP Governance Ecosystem, Plain-Language Guide

```
Document Type : Entry point — for a human setting this up, and for
                 any AI (including a fresh Claude session) that needs
                 to understand the ecosystem before touching it
Reads in      : ~10 minutes
Detail level  : Deliberately simple. For the full mechanics, exact
                 load order, and session-input tables, see
                 DEPLOYMENT-MANIFEST.md. This file tells you WHAT
                 each project is and HOW they connect — that file
                 tells you exactly how to set each one up.
Version       : v4.0 — Multi-Project + Versioning layer, on v3.0 —
                 P3 Light + standalone Test Generation Engine.
```

---

## 0. What changed recently (read this first if you knew the old version)

Two recent shifts. Both are additive — the assembly line itself still
runs in the same order.

- **v3.0 — P3 is now "light."** The two Execution Plan stations
  (Backend, Frontend) used to also write the test plans. They no
  longer do. A new, separate project — the **Test Generation Engine**
  — owns all test-plan and test-manifest generation. It sits *outside*
  the pipeline: nothing waits on it, and the audit stations no longer
  check test coverage (the old "CHECK-4" is gone).
- **v4.0 — many projects, versioned domains.** You can now run several
  products/domains side by side without their contexts bleeding into
  each other. Every session starts by naming which project you're in
  (`Project: <name>`), each project keeps its **own** registry, and
  domains/models can evolve in numbered, frozen versions that other
  projects reuse without breaking the original. One file carries all
  of this: `MULTI-PROJECT-VERSIONING-ARCHITECTURE.md`, loaded in every
  project.

---

## 1. The one-sentence version

Fifteen separate Claude Projects work together as an assembly line
that turns a raw product idea into a complete, implementation-ready
ERP (or other-domain) module — backend and frontend, each checked
before it's built, not after.

Twelve of them are stations on that assembly line, in a fixed order.
Three of them (Master Reviewer, Domain Profile Builder, Test
Generation Engine) are support projects you can call on when you need
them — they never sit *in* the line.

---

## 2. Before any station runs: name the project, then the two shared files

**v4.0 — the very first thing every session does** is state which
project it is operating on: `Project: <name>` (and `Domain: <name>`
where the station is domain-specific). Until that's given, the station
asks for it and does nothing else. This is what keeps two products'
work from mixing — every ID, every entity, every registry entry lives
inside the named project and never leaks to another one.

Once the project is named, two files are **mandatory in every
project's session, every time**, regardless of what that specific
project's own instructions say it needs:

- **`project-registry.md`** — the live record of what modules,
  entities, and cross-module dependencies exist **in this project**.
  (This replaces the old single, platform-wide `master-registry.md`:
  each project now keeps its own. A thin shared index — under
  `_ecosystem/` — lists all the projects above these per-project
  registries.)
- **`domain-profile.md`** — an analytical description of the domain
  itself: its scope, purpose, responsibilities, main components,
  governing rules, and how it relates to other domains. Not just a
  label like "ERP" — the actual thinking behind what this domain is.

Both are declared mandatory in one place — `GOVERNANCE-CONFIG.md` —
and every project's instruction file is wired to check for them.
If either is missing, the project stops and asks for it. Neither is
ever silently skipped.

There's also **`GOVERNANCE-CONFIG.md`** itself: the single file that
holds every setting that changes from platform to platform — the
Drive root folder name, the domain (ERP / general / a custom one),
the database engine, the backend/frontend/mobile stack, and so on.
Every project loads it as an instruction file. Change a setting once,
here, and every project picks it up — nothing is hardcoded per file.

And **`MULTI-PROJECT-VERSIONING-ARCHITECTURE.md`** — the v4.0 file that
defines project selection, context isolation, and how domains/models
evolve in frozen, reusable versions. Also loaded in every project.

---

## 3. The twelve-station pipeline, in order

Read top to bottom — this is the order a module actually moves
through. Each row says what the station does, in plain terms, and
what file name to load as its Claude Project instructions.

| # | Station | In plain terms | Instruction file |
|---|---------|-----------------|-------------------|
| P(-1) | Registry Builder | Creates/selects the project, then reads raw analysis notes and updates that project's `project-registry.md` so the rest of the pipeline has accurate shared context. **v4.0: it is the only project that creates a project, and it owns the shared `_ecosystem/` index.** | `MASTER-REGISTRY-BUILDER-instructions.md` |
| P0 | Platform Inception | Turns a free-form vision into structured architectural facts: platform tier, module list, business policies. | `PROJECT-0-PLATFORM-INCEPTION-ENGINE-v2.md` |
| P0.5 | PRD Engine | Turns P0's output into a Product Requirements Document (user stories). **Nothing in P1 can start until this exists.** | `PRD-ENGINE.md` |
| P1 | SRS Engine | Turns the PRD into a full functional spec: entities, business rules, screens, APIs. This is the ecosystem's source of functional truth. | `PROJECT-1-SRS-GOVERNANCE-ENGINE.md` |
| P2 | Database Engine | Turns the SRS into an actual database script — tables, fields, cross-module keys. | `PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md` |
| P2.5 | UI/UX Design Engine | Starts drafting screens from the PRD alone, in parallel with P1 (doesn't wait). Reconciles against the finished SRS before a human approves the design. | `UI-UX-DESIGN-ENGINE.md` |
| P3.1 | Exec Plan — Backend (LIGHT) | Turns the SRS + DB script into a step-by-step backend build plan. **v3.0: it no longer writes a test plan — only the execution plan.** | `PROJECT-3-BACKEND-ENGINE.md` (+ shared `PROJECT-3-REGISTRY.md`) |
| P4.1 | Audit — Backend | Checks the backend plan against everything upstream, before a single line of backend code is written. **v3.0: no test-coverage check (CHECK-4 removed).** | `PROJECT-4-BACKEND-AUDIT.md` |
| *(implementation)* | — | A human/Claude Code actually builds the backend, and an API-doc generator produces real, live API documentation. This is the only point the pipeline touches real code. | — |
| P3.2 | Exec Plan — Frontend (LIGHT) | Turns the **real** API docs (never the backend plan's internal draft) + the approved UI/UX design into a frontend build plan. Can only start once the backend is genuinely done. **v3.0: no test plan here either.** | `PROJECT-3-FRONTEND-ENGINE.md` (+ shared `PROJECT-3-REGISTRY.md`) |
| P4.2 | Audit — Frontend | Checks the frontend plan the same way P4.1 checked the backend — but must read the P4.1 report first. **v3.0: no CHECK-4.** | `PROJECT-4-FRONTEND-AUDIT.md` |
| *(implementation)* | — | The frontend is built. | — |
| P5 | api-verify | After the backend is live, generates and runs real automated tests against the real API — proof the backend actually works, not just that it was planned to. Consumes the test manifest produced by the Test Generation Engine. | `PROJECT-5-MODE-5-instructions.md` |

**The strict ordering rule:** P0.5 must exist before P1 starts. P1 and
P2.5 can run in parallel, but P2.5's design isn't final until it's
reconciled against P1's output and a human approves it. P2 needs P1.
P3.1 needs P1 + P2. P4.1 needs P3.1. The backend must be actually
*implemented* — not just planned — before P3.2 can start. P4.2 needs
P3.2, and must read P4.1's report first. P5 can run any time after the
backend is implemented.

---

## 4. The files shared across pipeline stations

| Shared file | Loaded by | What it's for |
|---|---|---|
| `SHARED-GOVERNANCE-CORE.md` | Every station | Vocabulary, Drive automation rules (CORE-1 through CORE-11) |
| `shared-governance-rules.md` | Every station | Cross-project coordination rules (how one station's output must look to satisfy the next) |
| `shared-artifact-contracts.md` | Every station except P0 and Registry Builder | 15 formal contracts defining exactly what one station hands the next (v4.0: adds versioned-reuse import and the Version Resolution Event) |
| `MULTI-PROJECT-VERSIONING-ARCHITECTURE.md` | Every one of the 15 projects | The v4.0 selection & reuse layer — project selection, context isolation, versioned domains/models |
| `GOVERNANCE-CONFIG.md` | Every one of the 15 projects | The settings owner — see Section 2 above |
| `MASTER-REGISTRY-SCHEMA.md` | P2 only | The structural rules for the registry itself |
| `XM-RESOLUTION-EVENT-PROTOCOL.md` | P2, P3.1, P4.1 only (backend-only) | How cross-module dependencies get declared and resolved |
| `GOVERNANCE-STABILIZATION-AMENDMENTS.md` + its addendum | P4.1, P4.2 only | A hardened-rules reference for the two audit stations |

---

## 5. What's outside the pipeline

Four projects exist in this ecosystem but never sit *in* the P(-1)→P5
line above. They don't gate it, and it doesn't gate them — call them
whenever you actually need them.

- **Test Generation Engine (v3.0, NEW).** Owns all test generation.
  Feed it a finished, aligned execution plan (backend or frontend) and
  it produces the matching test plan — plus, for the backend, the
  `test-execution-manifest.md` that P5 (api-verify) runs from. It sits
  outside the line on purpose: it doesn't gate the audit, and the
  audit doesn't check its output. Run it on demand, whenever you
  actually need the tests.
  Instruction file: `PROJECT-TEST-GENERATION-ENGINE.md`

- **P-REG — State Registry Extractor.** A compaction utility: feed it
  whichever of the pipeline's output files you have, it hands back a
  condensed `registry-state-[MOD].md` for cheaper session continuation
  later. Purely mechanical — it decides nothing.
  Instruction file: `PROJECT-REG-STATE-REGISTRY-EXTRACTOR.md`

- **Master Reviewer — this project.** Audits the governance files
  themselves for consistency (not a module — the ecosystem's own
  instruction files). This is how gaps like a missing mandatory-file
  check get caught before they cause a real module to fail partway
  through. Loads every file in this ecosystem.
  Instruction file: `MASTER-REVIEWER.md`

- **P-DOMAIN — Domain Profile Builder.** An active thinking partner
  that helps shape a raw idea into a sharp, competitive
  `domain-profile.md` — the mandatory file described in Section 2.
  Proposes structure, asks sharpening questions, offers real options
  — but only ever writes down what the user explicitly confirmed.
  **v4.0: it is also the Domain Evolution Authority — it owns the
  numbered, frozen versions of a domain's Core, its Extensions, and
  its Models, records them in `version-ledger.md`, and runs the
  Version Resolution Event when a version that another project depends
  on changes.** Can read/write to Drive directly, and can be called
  before a platform's very first module or years into production.
  Instruction file: `PROJECT-DOMAIN-PROFILE-BUILDER.md`

---

## 6. If you're setting this up for the first time

1. Read `DEPLOYMENT-MANIFEST.md` Part 3 for the exact, ordered load
   list for each of the 15 Claude Projects (this file gives you the
   plain-language map; that file gives you the precise setup steps).
2. Create the 15 Claude Projects and load each one's instruction
   files in the order that manifest specifies. Every project loads
   `MULTI-PROJECT-VERSIONING-ARCHITECTURE.md`.
3. Use P(-1) to create the project and seed its `project-registry.md`
   and the shared `_ecosystem/` index, and build a `domain-profile.md`
   via P-DOMAIN if this is a brand-new domain — both are mandatory
   before the pipeline stations will do any real work.
4. Start every session by stating `Project: <name>`, then start at
   P(-1) or P0 and follow the pipeline order in Section 3.

---

## 7. If you're an AI picking this up mid-project

First, note which project you're operating on (`Project: <name>`) —
context is isolated per project, so this is not optional. Then ask
which of the 15 projects you're being asked to act as, or whether
you're being asked to review the ecosystem itself (Master Reviewer).
Then load exactly that project's instruction files — never more, never
fewer than `DEPLOYMENT-MANIFEST.md` Part 3 specifies for it. Check for
`project-registry.md` and `domain-profile.md` before doing anything
else; if either is missing, stop and ask for it rather than proceeding
without it. Remember: the Execution Plan stations (P3.1/P3.2) do NOT
generate tests — that's the Test Generation Engine's job.

---

*End of START-HERE.md*
*This file is the simple map. DEPLOYMENT-MANIFEST.md is the precise*
*one. MASTER-REVIEWER.md is what checks that the two never drift apart.*
*v4.0: name the project first; per-project registries; versioned,*
*reusable domains. v3.0: P3 is light; the Test Generation Engine owns*
*tests and feeds P5; audits no longer check test coverage.*
