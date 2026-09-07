# v3.0 + v4.0 DEPLOYMENT CHECKLIST
## What to upload where, to push the P3-Light + Multi-Project/Versioning changes into your real projects

```
Scope     : This is the OPERATIONAL checklist for the two changes just
            made to the reviewer master copies:
              • v3.0 — P3 Light + standalone Test Generation Engine
              • v4.0 — Multi-Project + Versioning (Selection & Reuse Layer)
Source    : Every file named below is the master copy in THIS reviewer
            project. Open it here, copy its content, upload it to the
            target real project's Project Instructions (same filename).
Companion : DEPLOYMENT-MANIFEST.md has the FULL per-project load order
            (Part 3) and the verification tests (Part 5). This checklist
            is the delta — only what CHANGED and where it goes.
Method    : Manual upload (your chosen route). You stay in control of
            each project's Knowledge.
```

---

## 0 — THE THREE THINGS THAT CHANGED (read once)

```
1. ONE NEW FILE, loaded in EVERY project:
     MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
   Add it to all 15 projects, right after shared-artifact-contracts.md
   and before GOVERNANCE-CONFIG.md (or, for projects that don't load
   contracts, right before GOVERNANCE-CONFIG.md).

2. ONE NEW PROJECT to create:
     Test Generation Engine  (Project 15)
   Owns the test-plans + manifest that P3 no longer makes. Load list in
   §3 below.

3. A SET OF UPDATED FILES to re-upload (replace the old copy):
     see §1. Anything NOT in that list is unchanged — leave it.
```

---

## 1 — UPDATED FILES TO RE-UPLOAD (replace old copy with the reviewer master copy)

```
CHANGED — RE-UPLOAD EVERYWHERE IT IS LOADED
────────────────────────────────────────────────────────────────────
FILE (reviewer master copy)              │ WHY IT CHANGED
─────────────────────────────────────────┼──────────────────────────
MULTI-PROJECT-VERSIONING-ARCHITECTURE.md │ NEW (v4.0) — load in ALL 15
shared-artifact-contracts.md             │ v4.0 — now 15 contracts
                                          │ (adds CONTRACT-14 reuse,
                                          │  CONTRACT-15 VRE; v3.0
                                          │  CONTRACT-9/13/5 test moves)
SHARED-GOVERNANCE-CORE.md                │ v4.0 — CORE-11 selection,
                                          │  PRINCIPLE-13, RULE-15; +
                                          │  v3.0 P3-light fixes
GOVERNANCE-CONFIG.md                     │ v4.0 — Drive tree (Sec 1) +
                                          │  PROJECT-SELECTION (Sec 1A);
                                          │  DB_TARGET POSTGRESQL_16 kept
────────────────────────────────────────────────────────────────────

CHANGED — RE-UPLOAD IN THE SPECIFIC PROJECT(S) THAT LOAD THEM
────────────────────────────────────────────────────────────────────
FILE (reviewer master copy)              │ TARGET PROJECT(S) / WHY
─────────────────────────────────────────┼──────────────────────────
PROJECT-3-BACKEND-ENGINE.md              │ P7 Exec-BE — LIGHT (no test
                                          │  phase / SECTION D)
PROJECT-3-FRONTEND-ENGINE.md             │ P8 Exec-FE — LIGHT
PROJECT-3-REGISTRY.md                    │ P7, P8, P15 — v3.0 (test
                                          │  ownership → Test Gen Engine)
PROJECT-4-BACKEND-AUDIT.md               │ P9, P10 — no CHECK-4
PROJECT-4-FRONTEND-AUDIT.md              │ P10 — no CHECK-4
PROJECT-5-MODE-5-instructions.md         │ P11 api-verify — manifest now
                                          │  from Test Gen Engine
GOVERNANCE-STABILIZATION-AMENDMENTS-     │ P9, P10 ONLY — v3.0 note:
  v2-ADDENDUM.md                          │  strike CHECK-4, MODE 2.5,
                                          │  manifest-in-P3
MASTER-REGISTRY-BUILDER-instructions.md  │ P1 Registry Builder — v4.0
                                          │  Ecosystem Registry Authority
PROJECT-DOMAIN-PROFILE-BUILDER.md        │ P14 Domain Profile — v4.0
                                          │  Domain Evolution Authority
PROJECT-TEST-GENERATION-ENGINE.md        │ P15 (NEW project) — see §3
────────────────────────────────────────────────────────────────────

CHANGED — REVIEWER PROJECT ONLY (not loaded in the 15 pipeline projects)
────────────────────────────────────────────────────────────────────
MASTER-REVIEWER.md            │ v4.0 — DIMENSION 13, loaded-files list
DEPLOYMENT-MANIFEST.md        │ v4.0 — inventory, load order, tests
START-HERE.md                 │ v3.0 + v4.0 plain-language map
STAGE-2-GOVERNANCE-TOOLS-2.md │ v3.0/v4.0 note (test-gen moved, CHECK-4
                               │  gone) — reference file, not loaded
────────────────────────────────────────────────────────────────────
```

```
UNCHANGED — DO NOT RE-UPLOAD (still current as-is):
  shared-governance-rules.md, MASTER-REGISTRY-SCHEMA.md,
  XM-RESOLUTION-EVENT-PROTOCOL.md, GOVERNANCE-STABILIZATION-AMENDMENTS.md
  (base), PROJECT-0-PLATFORM-INCEPTION-ENGINE-v2.md, PRD-ENGINE.md,
  PROJECT-1-SRS-GOVERNANCE-ENGINE.md, PROJECT-2-DATABASE-GOVERNANCE-
  ENGINE.md, UI-UX-DESIGN-ENGINE.md, PROJECT-REG-STATE-REGISTRY-
  EXTRACTOR.md
```

> Note on PROJECT-3-REGISTRY-2.md: it is a fuller duplicate of
> PROJECT-3-REGISTRY.md left in the reviewer project. The REAL projects
> load PROJECT-3-REGISTRY.md (setup name: exec-plan-registry.md). Upload
> that one, not the -2 sibling. (Reconciling the duplicate is a separate
> housekeeping item — flagged, not urgent.)

---

## 2 — PER-PROJECT UPLOAD ACTIONS (the 14 existing projects)

For each project: (a) ADD the new v4.0 file, (b) REPLACE the shared
files that changed, (c) REPLACE that project's own changed engine file.
"= v4.0" means upload the reviewer master copy of that file.

```
P1  Master Registry Builder
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL GOVERNANCE-CONFIG.md
     ~ REPL MASTER-REGISTRY-BUILDER-instructions.md  (v4.0 authority)

P2  Platform Inception    │ P3  PRD Engine   │ P4  SRS   │ P5  Database
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL shared-artifact-contracts.md  (except P2 — it doesn't load it)
     ~ REPL SHARED-GOVERNANCE-CORE.md
     ~ REPL GOVERNANCE-CONFIG.md
     (their own engine files are UNCHANGED — don't re-upload them)

P6  UI/UX Design Engine
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL shared-artifact-contracts.md, SHARED-GOVERNANCE-CORE.md,
            GOVERNANCE-CONFIG.md
     (UI-UX-DESIGN-ENGINE.md UNCHANGED)

P7  Execution Plan — Backend (LIGHT)
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL shared-artifact-contracts.md, SHARED-GOVERNANCE-CORE.md,
            GOVERNANCE-CONFIG.md
     ~ REPL PROJECT-3-REGISTRY.md         (v3.0)
     ~ REPL PROJECT-3-BACKEND-ENGINE.md   (LIGHT)

P8  Execution Plan — Frontend (LIGHT)
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL shared-artifact-contracts.md, SHARED-GOVERNANCE-CORE.md,
            GOVERNANCE-CONFIG.md
     ~ REPL PROJECT-3-REGISTRY.md         (v3.0)
     ~ REPL PROJECT-3-FRONTEND-ENGINE.md  (LIGHT)

P9  Governance Audit — Backend
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL shared-artifact-contracts.md, SHARED-GOVERNANCE-CORE.md,
            GOVERNANCE-CONFIG.md
     ~ REPL GOVERNANCE-STABILIZATION-AMENDMENTS-v2-ADDENDUM.md  (v3.0)
     ~ REPL PROJECT-4-BACKEND-AUDIT.md    (no CHECK-4)

P10 Governance Audit — Frontend
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL shared-artifact-contracts.md, SHARED-GOVERNANCE-CORE.md,
            GOVERNANCE-CONFIG.md
     ~ REPL GOVERNANCE-STABILIZATION-AMENDMENTS-v2-ADDENDUM.md  (v3.0)
     ~ REPL PROJECT-4-BACKEND-AUDIT.md    (shared Finding format)
     ~ REPL PROJECT-4-FRONTEND-AUDIT.md   (no CHECK-4)

P11 api-verify
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL GOVERNANCE-CONFIG.md
     ~ REPL PROJECT-5-MODE-5-instructions.md  (manifest from Test Gen)

P12 State Registry Extractor
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL GOVERNANCE-CONFIG.md
     (PROJECT-REG-STATE-REGISTRY-EXTRACTOR.md UNCHANGED)

P13 Master Reviewer  (this project)
     ~ REPL every changed file above + MASTER-REVIEWER.md (v4.0).
       Already done here — this is the source of truth.

P14 Domain Profile Builder
     + ADD  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md
     ~ REPL GOVERNANCE-CONFIG.md
     ~ REPL PROJECT-DOMAIN-PROFILE-BUILDER.md  (v4.0 authority)
```

---

## 3 — CREATE THE NEW PROJECT: Test Generation Engine (P15)

```
Claude Project Name: Test Generation Engine
Load as Project Instructions, IN THIS ORDER:
  1. SHARED-GOVERNANCE-CORE.md
  2. shared-governance-rules.md
  3. shared-artifact-contracts.md              (v4.0)
  4. MULTI-PROJECT-VERSIONING-ARCHITECTURE.md   (v4.0)
  5. GOVERNANCE-CONFIG.md                        (v4.0)
  6. PROJECT-3-REGISTRY.md                       (marker protocol it reuses)
  7. PROJECT-TEST-GENERATION-ENGINE.md
It sits OUTSIDE the pipeline: it doesn't gate any stage, no stage gates
on it, and P4 does not audit its output. Backend mode →
backend-test-plan.md + test-execution-manifest.md (after ALIGN-BE ✓);
Frontend mode → frontend-test-plan.md (after ALIGN-FE ✓). Feeds P11.
```

---

## 4 — VERIFY (after uploading)

Run these prompts (full set in DEPLOYMENT-MANIFEST.md Part 5):

```
TEST-0  Start any project with a work request but NO `Project:` line →
        it must ASK which project, not proceed.
TEST-A  Ask P7/P8 "generate the backend test plan" → it must decline and
        point to the Test Generation Engine.
TEST-B  Ask P9/P10 "run CHECK-4 / audit test coverage" → it must say
        CHECK-4 was removed (v3.0).
TEST-C  Give the Test Gen Engine a plan with ALIGN-BE ✗ → it must stop.
TEST-Q  Ask to edit a reused published version in place → it must refuse
        (pinned, read-only) and offer a new version via P-DOMAIN.
```

---

## 5 — DRIVE (v4.0 skeleton — DONE; migration pending)

```
Already created in ERP-Governance (existing folders untouched):
  _ecosystem/{projects-index.md, domains-index.md, reuse-registry.md}
  ERP/{project-manifest.md, project-registry.md}
  ERP/erp-core/{_versions/version-ledger.md, Core/, Extensions/, Models/}

Pending (per-module, as work continues — your "migrate later" choice):
  • Move existing Foundation/ content into ERP/erp-core/{Core|Models}
    per module the next time P(-1)/P-DOMAIN run for it.
  • Migrate _registry/master-registry.md → ERP/project-registry.md
    (same schema, verbatim) and _domain/domain-profile.md →
    ERP/erp-core/domain-profile.md.
  Nothing in the old locations is deleted until you confirm each move.
```

---

*End of v3.0 + v4.0 DEPLOYMENT CHECKLIST.*
*Delta companion to DEPLOYMENT-MANIFEST.md (full load order + tests).*
*Upload each file from its reviewer master copy; anything not listed in*
*§1 is unchanged. One new file everywhere, one new project, done.*
