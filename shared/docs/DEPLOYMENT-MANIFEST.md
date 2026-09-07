# ERP GOVERNANCE — DEPLOYMENT MANIFEST
## Complete Claude Project Setup and File Mapping Guide

```
Document Type  : Operational Deployment Guide
Version        : v4.0 — Multi-Project + Versioning (Selection & Reuse
                 Layer) on top of v3.0 — P3 Light + standalone Test
                 Generation Engine (built on v2.1 — Backend/Frontend
                 Split + PRD/UI-UX Integration + PRD Hard-Gate +
                 Parallel-Draft UI/UX)
Audience       : Developer setting up the governance Claude Projects
Purpose        : Map all generated files to Claude Projects, explain
                 naming conventions, provide amendment application order,
                 and give a verified setup checklist
Status         : AUTHORITATIVE — follow this manifest for project setup
```

```
════════════════════════════════════════════════════════════════
v4.0 — WHAT CHANGED (MULTI-PROJECT + VERSIONING LAYER)
════════════════════════════════════════════════════════════════
A "Selection & Reuse Layer" was added ABOVE the pipeline. The
module-generation pipeline (P0→P5, Test Gen Engine) is UNCHANGED;
v4.0 only adds how work is scoped to a Project/Domain and how
domains/models/extensions evolve in immutable versions and are
reused across projects.

ONE new self-contained spec file carries the whole layer:
  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md

Setup impact:
  ✓ NEW shared instruction file: MULTI-PROJECT-VERSIONING-ARCHITECTURE.md.
    Load it in EVERY governance project (alongside the shared core /
    rules / contracts / config set). It is the authority for session
    project selection, context isolation, and versioned reuse.
  ✓ SESSION START — every project now opens with CORE-11 Session Project
    Selection: the operator states `Project: <name>` (and, where it
    matters, `Domain: <name>`) before any work. No project selected ⇒
    the engine asks for it and does nothing else.
  ✓ Per-project project-registry.md SUPERSEDES the single global
    master-registry.md. IDs remain LOCAL to a project (no global prefix).
    A thin _ecosystem/ index (projects-index.md, domains-index.md,
    reuse-registry.md, version-ledger.md) sits above the per-project
    registries. See MULTI-PROJECT-VERSIONING-ARCHITECTURE.md Part 5.
  ✓ P(-1) Master Registry Builder is now the ECOSYSTEM REGISTRY
    AUTHORITY: it is the ONLY engine that creates a project, owns
    projects-index.md + each project-registry.md + reuse-registry.md.
  ✓ P-DOMAIN Domain Profile Builder is now the DOMAIN EVOLUTION
    AUTHORITY: it owns Core/Extension/Model versions + Domain Releases,
    version-ledger.md, and the VRE (Version Resolution Event, VRE-ID).
  ✓ shared-artifact-contracts.md is now v4.0 (adds CONTRACT-14 versioned
    reuse import, and CONTRACT-15 VRE version-change propagation).
    Re-sync it into every project that loads it.
  ✓ Google Drive is reorganized to
    [GOVERNANCE-ROOT]/[Project]/[Domain]/{Core | Extensions/ext-[name]/
    v{N} | Models/[Model]/v{N}}/[Module]/[PXX-Folder]/  plus _ecosystem/,
    _backup/, TEST-GEN/. GOVERNANCE-CONFIG.md Section 1 carries the tree.
The pipeline SEQUENCE and every engine's internal logic are otherwise
unchanged.
════════════════════════════════════════════════════════════════
```

```
════════════════════════════════════════════════════════════════
v3.0 — WHAT CHANGED (P3 LIGHT + TEST GENERATION ENGINE)
════════════════════════════════════════════════════════════════
Test generation was removed from Project 3 (P3.1, P3.2 are now LIGHT)
and relocated to a NEW, STANDALONE Claude Project OUTSIDE the pipeline:
the Test Generation Engine (PROJECT-TEST-GENERATION-ENGINE.md).

Setup impact:
  ✓ NEW project to create: "Test Generation Engine" (see Part 3.15).
  ✓ Execution Plan — Backend (Project 7) and Execution Plan — Frontend
    (Project 8) no longer have a "STAGE 2 — test-plan" step. Each now
    produces ONLY its execution plan.
  ✓ Governance Audit — Backend (Project 9) and Frontend (Project 10)
    no longer take a test-plan/manifest input, and no longer carry a
    CHECK-4. Remove those from their session-input lists.
  ✓ shared-artifact-contracts.md is now v3.0 (CONTRACT-9/13 point to the
    Test Generation Engine; CHECK-4 removed from CONTRACT-5). Re-sync it
    into every project that loads it.
The pipeline SEQUENCE is otherwise unchanged.
════════════════════════════════════════════════════════════════
```

```
════════════════════════════════════════════════════════════════
v2.1 — WHAT CHANGED FROM THE 4-PROJECT MODEL
════════════════════════════════════════════════════════════════
The prior version of this manifest assumed exactly FOUR Claude
Projects (SRS, DB, Execution Plan, Audit). That model is retired.
The ecosystem now has many separate engines/utilities, not all of
which need their own Claude Project (see Part 3 for the recommended
consolidation). Every Part below is rewritten accordingly.
════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# PART 1 — FILE INVENTORY (v4.0 — COMPLETE)
═══════════════════════════════════════════════════════════════════

Complete list of all governance ecosystem files, their role,
and the Claude Project setup guide name they correspond to.

```
╔══════════════════════════════════════════════════════════╦══════════════════════════════════════╦════════════╗
║ GENERATED FILE (actual name)                             ║ SETUP GUIDE NAME                     ║ ROLE       ║
╠══════════════════════════════════════════════════════════╬══════════════════════════════════════╬════════════╣
║ SHARED-GOVERNANCE-CORE.md                                ║ shared-governance-core.md            ║ INSTRUCTION║
║ shared-governance-rules.md                               ║ shared-governance-rules.md           ║ INSTRUCTION║
║ shared-artifact-contracts.md (v4.0)                      ║ shared-artifact-contracts.md         ║ INSTRUCTION║
║ MULTI-PROJECT-VERSIONING-ARCHITECTURE.md (NEW, v4.0)     ║ multi-project-versioning.md          ║ INSTRUCTION║
║   Selection & Reuse Layer — loaded in ALL projects        ║                                        ║ (all)      ║
║ MASTER-REGISTRY-SCHEMA.md                                ║ master-registry-schema.md            ║ INSTRUCTION║
║ XM-RESOLUTION-EVENT-PROTOCOL.md                          ║ xm-resolution-event-protocol.md      ║ INSTRUCTION║
║ GOVERNANCE-STABILIZATION-AMENDMENTS.md (+ ADDENDUM)      ║ governance-stabilization-amendments.md║ REFERENCE  ║
║ GOVERNANCE-CONFIG.md (v4.0 tree + PROJECT-SELECTION)     ║ GOVERNANCE-CONFIG.md                  ║ INSTRUCTION║
║   settings owner — loaded in ALL projects                 ║                                        ║ (all)      ║
╠══════════════════════════════════════════════════════════╬══════════════════════════════════════╬════════════╣
║ MASTER-REGISTRY-BUILDER-instructions.md (v4.0)           ║ registry-builder.md                  ║ INSTRUCTION║
║   P(-1) — Ecosystem Registry Authority                     ║                                        ║            ║
║ PROJECT-0-PLATFORM-INCEPTION-ENGINE-v2.md                ║ platform-inception-engine.md         ║ INSTRUCTION║
║ PRD-ENGINE.md                                            ║ prd-engine.md                         ║ INSTRUCTION║
║ PROJECT-1-SRS-GOVERNANCE-ENGINE.md                       ║ srs-governance-engine.md             ║ INSTRUCTION║
║ PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md                  ║ db-governance-engine.md              ║ INSTRUCTION║
║ UI-UX-DESIGN-ENGINE.md                                   ║ ui-ux-design-engine.md               ║ INSTRUCTION║
║ PROJECT-3-REGISTRY.md                                    ║ exec-plan-registry.md                ║ INSTRUCTION║
║ PROJECT-3-BACKEND-ENGINE.md (LIGHT, v3.0)                ║ exec-plan-backend-engine.md          ║ INSTRUCTION║
║ PROJECT-3-FRONTEND-ENGINE.md (LIGHT, v3.0)               ║ exec-plan-frontend-engine.md         ║ INSTRUCTION║
║ PROJECT-TEST-GENERATION-ENGINE.md (NEW, v3.0)            ║ test-generation-engine.md            ║ INSTRUCTION║
║   Standalone — OUTSIDE the pipeline; owns test-plans +    ║                                        ║            ║
║   test-execution-manifest.md, feeds P5                     ║                                        ║            ║
║ PROJECT-4-BACKEND-AUDIT.md (CHECK-4 removed, v3.0)       ║ audit-backend-engine.md              ║ INSTRUCTION║
║ PROJECT-4-FRONTEND-AUDIT.md (CHECK-4 removed, v3.0)      ║ audit-frontend-engine.md             ║ INSTRUCTION║
║ PROJECT-5-MODE-5-instructions.md                         ║ api-verify-engine.md                 ║ INSTRUCTION║
║ PROJECT-REG-STATE-REGISTRY-EXTRACTOR.md                  ║ state-registry-extractor.md          ║ INSTRUCTION║
║ PROJECT-DOMAIN-PROFILE-BUILDER.md (v4.0)                 ║ PROJECT-DOMAIN-PROFILE-BUILDER.md    ║ INSTRUCTION║
║   P-DOMAIN — Domain Evolution Authority, non-pipeline      ║                                        ║            ║
╠══════════════════════════════════════════════════════════╬══════════════════════════════════════╬════════════╣
║ STAGE-2-GOVERNANCE-TOOLS.md                               ║ (tooling reference — not loaded)     ║ REFERENCE  ║
║ WORKSPACE-ARCHITECTURE-REFERENCE.md                      ║ (repo/infra reference — not loaded)   ║ REFERENCE  ║
║ START-HERE.md                                             ║ (plain-language entry point — not     ║ REFERENCE  ║
║                                                          ║  loaded)                              ║            ║
║ generic-schema-reference.md                              ║ (Project 5 session upload)           ║ REFERENCE  ║
║ generic-boilerplate-reference.py                         ║ (Project 5 session upload)           ║ REFERENCE  ║
╠══════════════════════════════════════════════════════════╬══════════════════════════════════════╬════════════╣
║ MASTER-REVIEWER.md (v4.0)                                ║ (cross-ecosystem reviewer — its own  ║ INSTRUCTION║
║                                                          ║  standalone Claude Project, Part 3.13)║ (own proj) ║
╚══════════════════════════════════════════════════════════╩══════════════════════════════════════╩════════════╝
```

**Naming convention:** The setup guide uses lowercase-kebab-case.
The generated files use UPPERCASE or mixed case. When uploading to
Claude Projects, keep names consistent within each project.

**File count summary (v4.0):** 8 shared/reference instruction files
(adds MULTI-PROJECT-VERSIONING-ARCHITECTURE.md to the prior 7) +
15 engine instruction files + 5 tooling/repo reference files +
architecture/audit records = the full ecosystem. The one NEW
instruction file vs v3.0 is MULTI-PROJECT-VERSIONING-ARCHITECTURE.md,
loaded in EVERY governance project.

---

═══════════════════════════════════════════════════════════════════
# PART 2 — PRE-DEPLOYMENT: APPLY STABILIZATION AMENDMENTS
═══════════════════════════════════════════════════════════════════

**Before loading any file into Claude Projects, confirm the
stabilization amendments from GOVERNANCE-STABILIZATION-AMENDMENTS.md +
its ADDENDUM are reflected, PLUS the v3.0 P3-light change and the v4.0
Multi-Project + Versioning layer.**

```
Priority 1 — Structural foundations (apply first):
  □ SHARED GOVERNANCE CORE header (satisfied by loading it per Part 3)

Priority 2 — XM-ID format (all or nothing — apply together)
Priority 3 — New governance mechanisms
Priority 4 — Execution determinism

Priority 5 — Backend/Frontend structural split (v2.0):
  □ AMEND-P3-K — PASS 1 / PASS 2 split + ALIGN-BE / ALIGN-FE rename
  □ AMEND-P4-E — P4.1 / P4.2 dual-gate split

Priority 5.5 — PRD/UI-UX pipeline relationship (v2.1):
  □ AMEND-CORE-A — PRD hard-gates P1 + UI/UX parallel-draft

Priority 6 — New engine deployment (v2.0/v2.1):
  □ Deploy PRD-ENGINE.md, UI-UX-DESIGN-ENGINE.md, PROJECT-5, PROJECT-REG

Priority 7 — P3-LIGHT + TEST GENERATION ENGINE (v3.0):
  □ Confirm PROJECT-3-BACKEND-ENGINE.md and PROJECT-3-FRONTEND-ENGINE.md
    carry NO test phase / SECTION D / test-plan spec (light)
  □ Confirm PROJECT-4-BACKEND-AUDIT.md and PROJECT-4-FRONTEND-AUDIT.md
    carry NO CHECK-4
  □ Deploy PROJECT-TEST-GENERATION-ENGINE.md as its own new project
  □ Confirm shared-artifact-contracts.md carries CONTRACT-9/13/5 and is
    re-synced into every project that loads it
  □ Confirm PROJECT-5-MODE-5-instructions.md sources the manifest from
    the Test Generation Engine

Priority 8 — MULTI-PROJECT + VERSIONING LAYER (v4.0 — NEW):
  □ Deploy MULTI-PROJECT-VERSIONING-ARCHITECTURE.md and load it in EVERY
    governance project
  □ Confirm shared-artifact-contracts.md is v4.0 (adds CONTRACT-14 +
    CONTRACT-15) and re-synced everywhere
  □ Confirm GOVERNANCE-CONFIG.md carries the v4.0 Drive tree (Section 1)
    and the PROJECT-SELECTION block (Section 1A)
  □ Confirm P(-1) registry-builder.md carries the Ecosystem Registry
    Authority section (projects-index + per-project registries +
    reuse-registry)
  □ Confirm P-DOMAIN carries the Domain Evolution Authority section
    (Core/Extension/Model versions + version-ledger + VRE)
  □ Confirm every engine opens with CORE-11 Session Project Selection

Priority 9 — Companion file sync:
  □ All shared/*.md files, PROJECT-1, PROJECT-2, etc. confirmed current
```

**About GOVERNANCE-STABILIZATION-AMENDMENTS.md (+ ADDENDUM) placement:**
Loaded ONLY in the two Project 4 Claude Projects (Backend Audit,
Frontend Audit). Do not load it in any other project as an instruction.

---

═══════════════════════════════════════════════════════════════════
# PART 3 — CLAUDE PROJECT SETUP — INSTRUCTION FILE LOADING
═══════════════════════════════════════════════════════════════════

**Recommended project list (v4.0 — same 15 projects as v3.0):**

```
╔═══╦═══════════════════════════════╦══════════════════════════════════╗
║ # ║ Claude Project                ║ Engines it covers                 ║
╠═══╬═══════════════════════════════╬══════════════════════════════════╣
║ 1 ║ Master Registry Builder       ║ P(-1) — Ecosystem Registry Auth.  ║
║ 2 ║ Platform Inception Engine     ║ P0 — standalone                   ║
║ 3 ║ PRD Engine                    ║ P0.5 — standalone                 ║
║ 4 ║ SRS Governance Engine         ║ P1 — standalone                   ║
║ 5 ║ Database Governance Engine    ║ P2 — standalone                   ║
║ 6 ║ UI/UX Design Engine           ║ P2.5 — standalone                 ║
║ 7 ║ Execution Plan — Backend      ║ P3.1 (LIGHT) — REGISTRY + BACKEND ║
║ 8 ║ Execution Plan — Frontend     ║ P3.2 (LIGHT) — REGISTRY + FRONTEND║
║ 9 ║ Governance Audit — Backend    ║ P4.1 (no CHECK-4) — standalone    ║
║10 ║ Governance Audit — Frontend   ║ P4.2 (no CHECK-4) — standalone    ║
║11 ║ api-verify                    ║ P5 — standalone                   ║
║12 ║ State Registry Extractor      ║ P-REG — standalone                ║
║13 ║ Master Reviewer               ║ Cross-ecosystem consistency tool  ║
║14 ║ Domain Profile Builder        ║ P-DOMAIN — Domain Evolution Auth. ║
║15 ║ Test Generation Engine        ║ Standalone — OUTSIDE the pipeline,║
║   ║                               ║ consumes light execution plans,   ║
║   ║                               ║ produces test-plans + manifest,   ║
║   ║                               ║ feeds P5                          ║
╚═══╩═══════════════════════════════╩══════════════════════════════════╝
```

**v4.0 universal loading rule:** EVERY project in the list above loads
MULTI-PROJECT-VERSIONING-ARCHITECTURE.md as a Project Instruction,
immediately after shared-artifact-contracts.md and before
GOVERNANCE-CONFIG.md. It is what makes CORE-11 Session Project
Selection and per-project registries active in that project. The
per-project sections below show the delta only.

---

## Project 1 — Master Registry Builder (P(-1), Ecosystem Registry Authority)

**Load as Project Instructions (in this order):**
```
1. GOVERNANCE-CONFIG.md                       (GOVERNANCE-CONFIG.md — v4.0)
2. multi-project-versioning.md                (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
3. registry-builder.md                        (MASTER-REGISTRY-BUILDER-instructions.md — v4.0)
```
**v4.0 role:** ONLY engine that creates a project. Owns the _ecosystem/
index (projects-index.md, reuse-registry.md) and each per-project
project-registry.md. STEP 0 is CORE-11 Session Project Selection — it
either creates a new project entry or selects an existing one before
any registry work.

---

## Project 7 — Execution Plan Governance Engine (Backend, LIGHT)

**Load as Project Instructions (in this order):**
```
1. shared-governance-core.md          (SHARED-GOVERNANCE-CORE.md)
2. shared-governance-rules.md         (shared-governance-rules.md)
3. shared-artifact-contracts.md       (shared-artifact-contracts.md — v4.0)
4. multi-project-versioning.md        (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
5. GOVERNANCE-CONFIG.md               (GOVERNANCE-CONFIG.md — v4.0)
6. exec-plan-registry.md              (PROJECT-3-REGISTRY.md)
7. exec-plan-backend-engine.md        (PROJECT-3-BACKEND-ENGINE.md — LIGHT)
```

**Typical session inputs (v4.0 — light):**
```
SESSION START: state `Project: <name>` (CORE-11) before any work.
backend-execution-plan.md:
  Required: srs.md + db-script.md + project-registry.md (the selected
            project's registry — supersedes master-registry.md)
  Optional: Existing backend-execution-plan.md (for continuation)
NOTE (v3.0): there is NO STAGE 2 here anymore. This project produces
ONLY backend-execution-plan.md. The backend-test-plan.md +
test-execution-manifest.md are produced by the Test Generation Engine
(Project 15), after ALIGN-BE ✓.
```

---

## Project 8 — Execution Plan Governance Engine (Frontend, LIGHT)

**Load as Project Instructions (in this order):**
```
1. shared-governance-core.md          (SHARED-GOVERNANCE-CORE.md)
2. shared-governance-rules.md         (shared-governance-rules.md)
3. shared-artifact-contracts.md       (shared-artifact-contracts.md — v4.0)
4. multi-project-versioning.md        (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
5. GOVERNANCE-CONFIG.md               (GOVERNANCE-CONFIG.md — v4.0)
6. exec-plan-registry.md              (PROJECT-3-REGISTRY.md — same file as Project 7)
7. exec-plan-frontend-engine.md       (PROJECT-3-FRONTEND-ENGINE.md — LIGHT)
```

**Typical session inputs (v4.0 — light):**
```
SESSION START: state `Project: <name>` (CORE-11) before any work.
PRECONDITION (CONTRACT-12): GATE: BACKEND MODULE COMPLETE confirmed —
  real API Docs + human-approved flow-diagram.md/ui-ux-spec.md.
frontend-execution-plan.md:
  Required: real API Docs + flow-diagram.md + ui-ux-spec.md + srs.md
  Optional: Existing frontend-execution-plan.md (for continuation)
NOTE (v3.0): there is NO STAGE 2 here anymore. frontend-test-plan.md is
produced by the Test Generation Engine (Project 15), after ALIGN-FE ✓.
```

---

## Project 9 — Governance Audit Engine (Backend Gate)

**Load as Project Instructions (in this order):**
```
1. shared-governance-core.md              (SHARED-GOVERNANCE-CORE.md)
2. shared-governance-rules.md             (shared-governance-rules.md)
3. shared-artifact-contracts.md           (shared-artifact-contracts.md — v4.0)
4. multi-project-versioning.md            (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
5. governance-stabilization-amendments.md (+ ADDENDUM, appended)
6. GOVERNANCE-CONFIG.md                   (GOVERNANCE-CONFIG.md — v4.0)
7. audit-backend-engine.md                (PROJECT-4-BACKEND-AUDIT.md — no CHECK-4)
```

**Typical session inputs (v4.0):**
```
SESSION START: state `Project: <name>` (CORE-11) before any work.
Required: platform-summary + module-registry + business-policies (P0)
          + srs.md + db-script.md + backend-execution-plan.md
Optional: Prior P4.1 report (for continuation)
NOTE (v3.0): backend-test-plan.md and test-execution-manifest.md are
NOT inputs here — CHECK-4 was removed; test coverage is out of audit
scope.
```

---

## Project 10 — Governance Audit Engine (Frontend Gate)

**Load as Project Instructions (in this order):**
```
1. shared-governance-core.md              (SHARED-GOVERNANCE-CORE.md)
2. shared-governance-rules.md             (shared-governance-rules.md)
3. shared-artifact-contracts.md           (shared-artifact-contracts.md — v4.0)
4. multi-project-versioning.md            (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
5. governance-stabilization-amendments.md (+ ADDENDUM, appended)
6. GOVERNANCE-CONFIG.md                   (GOVERNANCE-CONFIG.md — v4.0)
7. audit-backend-engine.md                (PROJECT-4-BACKEND-AUDIT.md — shared Finding format, Section 2)
8. audit-frontend-engine.md               (PROJECT-4-FRONTEND-AUDIT.md — no CHECK-4)
```

**Typical session inputs (v4.0):**
```
SESSION START: state `Project: <name>` (CORE-11) before any work.
Required: P4.1 Audit Report — MANDATORY HARD GATE, read first
Required: srs.md + frontend-execution-plan.md + real API Docs
Recommended: prd.md + flow-diagram.md + ui-ux-spec.md
NOTE (v3.0): frontend-test-plan.md is NOT an input here — CHECK-4 was
removed.
```

---

## Project 11 — api-verify (Project 5 / MODE 5)

**Load as Project Instructions:**
```
1. multi-project-versioning.md   (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
2. GOVERNANCE-CONFIG.md          (GOVERNANCE-CONFIG.md — v4.0)
3. api-verify-engine.md          (PROJECT-5-MODE-5-instructions.md)
```
Attach `generic-schema-reference.md` and `generic-boilerplate-reference.py`
to Project Knowledge.

**Typical session inputs:**
```
SESSION START: state `Project: <name>` (CORE-11) before any work.
Full tier (preferred) : test-execution-manifest.md (from the Test
                        Generation Engine, Project 15) + real API Docs
Degraded tier          : backend-execution-plan.md + backend-test-plan.md
                         + real API Docs (no manifest)
Minimal tier           : real API Docs only
```

---

## Project 13 — Master Reviewer

**Claude Project Name:** `Master Reviewer`

**Load as Project Instructions:**
```
Every file in this manifest (the reviewer needs full ecosystem
visibility — including MULTI-PROJECT-VERSIONING-ARCHITECTURE.md (v4.0)
and PROJECT-TEST-GENERATION-ENGINE.md (v3.0)) + MASTER-REVIEWER.md
itself (v4.0).
```
Separate from, and does not participate in, the module-generation
pipeline. DIMENSION 13 (Project Isolation + Version Integrity) checks
the v4.0 layer.

---

## Project 14 — Domain Profile Builder (P-DOMAIN, Domain Evolution Authority)

**Load as Project Instructions (in this order):**
```
1. GOVERNANCE-CONFIG.md                       (GOVERNANCE-CONFIG.md — v4.0)
2. multi-project-versioning.md                (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
3. PROJECT-DOMAIN-PROFILE-BUILDER.md          (PROJECT-DOMAIN-PROFILE-BUILDER.md — v4.0)
```
**v4.0 role:** Domain Evolution Authority. Owns Core/Extension/Model
versions, Domain Releases, version-ledger.md, and the VRE (Version
Resolution Event, VRE-ID). Still "proposes freely, never decides
silently" — now extended to version bumps and reuse.

---

## Project 15 — Test Generation Engine (v3.0)

**Claude Project Name:** `Test Generation Engine`

**Load as Project Instructions (in this order):**
```
1. shared-governance-core.md          (SHARED-GOVERNANCE-CORE.md)
2. shared-governance-rules.md         (shared-governance-rules.md)
3. shared-artifact-contracts.md       (shared-artifact-contracts.md — v4.0, CONTRACT-9/13)
4. multi-project-versioning.md        (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
5. GOVERNANCE-CONFIG.md               (GOVERNANCE-CONFIG.md — v4.0)
6. exec-plan-registry.md              (PROJECT-3-REGISTRY.md — for the marker
                                        protocol + ID table it reuses)
7. test-generation-engine.md          (PROJECT-TEST-GENERATION-ENGINE.md)
```

**Typical session inputs:**
```
SESSION START: state `Project: <name>` (CORE-11) before any work.
BACKEND mode:
  Required: backend-execution-plan.md (Gate ALIGN-BE ✓ confirmed) + srs.md
  Optional: db-script.md (reference)
  Output  : backend-test-plan.md + test-execution-manifest.md
FRONTEND mode:
  Required: frontend-execution-plan.md (Gate ALIGN-FE ✓ confirmed) + srs.md
  Output  : frontend-test-plan.md
```
This project is OUTSIDE the pipeline — it does not gate any pipeline
stage and no pipeline stage gates on it. Its outputs are NOT audited by
Project 4. It feeds Project 11 (api-verify) via the manifest.

---

═══════════════════════════════════════════════════════════════════
# PART 4 — OPERATIONAL WORKFLOW (v4.0)
═══════════════════════════════════════════════════════════════════

## Session Start (v4.0 — applies to EVERY session, every project)

```
STEP 0 — CORE-11 Session Project Selection:
  The operator states `Project: <name>` (and `Domain: <name>` where the
  engine is domain-scoped). The engine loads ONLY that project's
  project-registry.md and that domain's pinned versions; contexts are
  isolated (PRINCIPLE-13). No selection ⇒ the engine asks and does
  nothing else. All IDs are LOCAL to the selected project.
```

## Standard Module Pipeline (single module, no cross-module deps)

```
SESSION 0 — Master Registry Builder (Project 1) — creates/selects the
            project, seeds project-registry.md + projects-index entry
SESSION 1 — Platform Inception Engine (Project 2)
SESSION 2 — PRD Engine (Project 3)  — HARD GATE for Session 3

── Sessions 3 and 4 can run IN PARALLEL from here ──

SESSION 3 — SRS Governance Engine (Project 4)
  Output : srs.md + OQ Log + REGISTRY UPDATE (project-registry.md)
SESSION 4 — UI/UX Design Engine (Project 6) — starts once prd.md exists
  Output : DRAFT flow-diagram.md + ui-ux-spec.md + mockups
           (Reconciliation Gate once srs.md is available)
SESSION 5 — Database Governance Engine (Project 5) — after Session 3
  Output : db-script.md + REGISTRY UPDATE

SESSION 6 — Execution Plan — Backend (Project 7, LIGHT)
  Input  : srs.md + db-script.md + project-registry.md
  Output : backend-execution-plan.md (Gate ALIGN-BE ✓) + REGISTRY UPDATE

SESSION 6b — Test Generation Engine (Project 15, Backend mode) — OUTSIDE
             the pipeline; run whenever test artifacts are needed
  Input  : backend-execution-plan.md (ALIGN-BE ✓) + srs.md
  Output : backend-test-plan.md + test-execution-manifest.md
  NOTE   : optional/on-demand — it does NOT gate Session 7 (audit).

SESSION 7 — Governance Audit — Backend (Project 9)
  Input  : platform-summary + srs.md + db-script.md
           + backend-execution-plan.md   (NO test artifact — v3.0)
  Output : P4.1 audit report
  Action : Resolve CRITICAL and MAJOR findings before implementation

── Real backend implementation happens here (Claude Code) ──

SESSION 8 — api-doc-generator (tool) → real API Docs

SESSION 9 — api-verify (Project 11) — after real API Docs
  Input  : test-execution-manifest.md (from Session 6b) + real API Docs
  Output : test_<module>_apis.py + HTML report

SESSION 10 — UI/UX Design Engine (Project 6), Reconciliation (if not
             already completed in parallel)

GATE: BACKEND MODULE COMPLETE — confirmed once Session 7 clears,
      real API Docs exist, and the UI/UX package is human-approved.

SESSION 11 — Execution Plan — Frontend (Project 8, LIGHT)
  Input  : real API Docs + flow-diagram.md + ui-ux-spec.md + srs.md
  Output : frontend-execution-plan.md (Gate ALIGN-FE ✓)

SESSION 11b — Test Generation Engine (Project 15, Frontend mode) —
              OUTSIDE the pipeline; on-demand
  Input  : frontend-execution-plan.md (ALIGN-FE ✓) + srs.md
  Output : frontend-test-plan.md

SESSION 12 — Governance Audit — Frontend (Project 10)
  Input  : P4.1 report (mandatory) + srs.md + frontend-execution-plan.md
           + real API Docs   (NO test artifact — v3.0)
  Output : P4.2 audit report

── Real frontend implementation happens here (Claude Code) ──
```

## Domain Evolution & Reuse (v4.0 — off-pipeline, P-DOMAIN)

```
When a domain/model/extension must change or be reused:
  1. P-DOMAIN proposes a version bump (Core edit, new Extension, or
     Model version) — never decides silently.
  2. On approval it publishes an IMMUTABLE version and records it in
     version-ledger.md; a set of pinned versions can be cut as a Domain
     Release.
  3. Another project REUSES a published version by pinned, read-only
     import (CONTRACT-14) — it never mutates the owning domain.
  4. If a pinned version a consumer depends on changes, a VRE (Version
     Resolution Event, CONTRACT-15) propagates the change, mirroring how
     an RXE (CONTRACT-8) propagates a cross-module change.
```

## Multi-Module & Continuation

```
Multi-module: each module runs its own pipeline within the SELECTED
project; coordination via that project's project-registry.md, XM
Resolution Events (Backend only), Shared Entity Declarations. XM-ID
namespace collisions prevented by module-qualified format. IDs never
cross project boundaries (PRINCIPLE-13).

Continuation: state `Project: <name>`, upload existing artifacts +
project-registry.md, prompt "Continue [module]" — the project restores
context (CORE-6). The Test Generation Engine has its own continuation
protocol for resuming a partially-written test-plan.
```

---

═══════════════════════════════════════════════════════════════════
# PART 5 — VERIFICATION CHECKLIST (v4.0 — UPDATED)
═══════════════════════════════════════════════════════════════════

## File Preparation

```
□ MULTI-PROJECT-VERSIONING-ARCHITECTURE.md: present; loaded in ALL 15
  projects
□ shared-artifact-contracts.md: v4.0 (CONTRACT-14 versioned reuse import;
  CONTRACT-15 VRE) — plus the v3.0 CONTRACT-9/13/5 test changes
□ GOVERNANCE-CONFIG.md: v4.0 Drive tree (Section 1) + PROJECT-SELECTION
  block (Section 1A); DB_TARGET = POSTGRESQL_16 preserved
□ registry-builder.md (P(-1)): Ecosystem Registry Authority section present
□ PROJECT-DOMAIN-PROFILE-BUILDER.md (P-DOMAIN): Domain Evolution Authority
  section present (version-ledger + VRE)
□ PROJECT-3-BACKEND-ENGINE.md / PROJECT-3-FRONTEND-ENGINE.md: LIGHT —
  no test phase, no SECTION D, no test-plan spec
□ PROJECT-4-BACKEND-AUDIT.md / PROJECT-4-FRONTEND-AUDIT.md: no CHECK-4
□ PROJECT-TEST-GENERATION-ENGINE.md: present, owns TC-BE/TC-FE, test-plans,
  manifest
□ _ecosystem/ index seeded: projects-index.md, domains-index.md,
  reuse-registry.md, version-ledger.md
□ Per-project project-registry.md created for each active project
  (supersedes the single master-registry.md)
```

## Claude Project Configuration

```
□ 15 Claude Projects created per Part 3
□ MULTI-PROJECT-VERSIONING-ARCHITECTURE.md loaded in EVERY project
□ Project 7 and Project 8 BOTH have PROJECT-3-REGISTRY.md loaded (correct)
□ Project 15 (Test Generation Engine) has PROJECT-3-REGISTRY.md loaded too
  (for the marker protocol it reuses)
□ governance-stabilization-amendments.md loaded ONLY in Projects 9 and 10
□ xm-resolution-event-protocol.md loaded ONLY in Project 7 (Backend)
□ Project 1 (P(-1)) and Project 14 (P-DOMAIN) carry their v4.0 authority
  sections
```

## Functional Verification Tests

```
TEST-0 (v4.0) — CORE-11 Session Project Selection is enforced
  Prompt: start any session with a work request but NO `Project:` line.
  Expected: the engine asks which project to operate on and does nothing
            else. Failure signal: it proceeds against an unnamed/implied
            project.

TEST-P (v4.0) — Context isolation (PRINCIPLE-13)
  Prompt: in Project X, reference an ID that only exists in Project Y.
  Expected: the engine treats it as unknown (IDs are local); it does NOT
            resolve across projects. Failure signal: cross-project ID leak.

TEST-Q (v4.0) — Versioned reuse is pinned + read-only (CONTRACT-14)
  Prompt: reuse a published model version from another domain and ask to
          edit it in place.
  Expected: refuses to mutate the owner; offers a new version via P-DOMAIN
            instead. Failure signal: edits the owning domain's version.

TEST-R (v4.0) — VRE fires on a pinned-version change (CONTRACT-15)
  Prompt: change a version that a consumer project has pinned.
  Expected: a VRE (VRE-ID) is opened to propagate/resolve, analogous to an
            RXE. Failure signal: silent change with no VRE.

TEST-A (v3.0) — Project 7/8 (Exec Plans) produce NO test artifact
  Prompt: "Generate the backend test plan for this module."
  Expected: Explains test generation is the Test Generation Engine's
            job (Project 15); this project produces only the execution
            plan. Failure signal: produces a backend-test-plan.md here.

TEST-B (v3.0) — Project 9/10 (Audits) carry NO CHECK-4
  Prompt: "Run CHECK-4 / audit the test coverage."
  Expected: States CHECK-4 was removed (v3.0); test coverage is out of
            audit scope. Failure signal: attempts a test-coverage check.

TEST-C (v3.0) — Test Generation Engine requires ALIGN ✓
  Prompt: attach a backend-execution-plan.md with ALIGN-BE ✗, ask for
          the test plan.
  Expected: Refuses/stops — ALIGN-BE ✓ is a precondition (CONTRACT-9).
            Failure signal: generates the test plan anyway.

TEST-D — Project 11 (api-verify) Manifest-Priority Check
  Prompt: attach test-execution-manifest.md AND backend-execution-plan.md.
  Expected: Uses the manifest directly; does not re-derive (CONTRACT-13).

TEST-E — Project 4 (SRS) Hard-Gate Check (v2.1)
  Prompt: "Generate SRS" (no prd-[MOD].md). Expected: refuses (CONTRACT-10).

TEST-F — Project 8 (Exec Frontend) Gate Check (v2.1)
  Prompt: "Generate the frontend execution plan" (no real API Docs).
  Expected: refuses — GATE: BACKEND MODULE COMPLETE requires real API Docs.

TEST-G — Project 10 (Audit Frontend) Mandatory-Read Check
  Prompt: "Run the frontend audit" (no P4.1 report). Expected: refuses.
```

---

═══════════════════════════════════════════════════════════════════
# PART 6 — QUICK REFERENCE CARD (v4.0)
═══════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════════╗
║              ERP GOVERNANCE ECOSYSTEM — QUICK REFERENCE (v4.0)       ║
╠══════════════════════════════════════════════════════════════════════╣
║ SELECT   : Session opens with `Project: <name>` (CORE-11); IDs local ║
║            per project; contexts isolated (PRINCIPLE-13)             ║
║ P(-1) Registry  : Ecosystem Registry Authority — projects-index +    ║
║                   per-project project-registry + reuse-registry      ║
║ P0    Platform  : Architectural Truth — platform-summary, AQ/INF/BLK ║
║ P0.5  PRD        : Product Intent — US-ID (HARD-GATES P1)            ║
║ P1    SRS        : Functional Truth — ENTITY-ID, RULE-ID, OQ-ID       ║
║ P2    DB         : Structural Truth — DBF-ID, DBS-ID, XM-[MOD]-ID    ║
║ P2.5  UI/UX      : Design Intent — UXD-ID; PRD-alone start           ║
║ P3.1  Exec BE    : Backend Exec Truth — FIELD-ID, ERR-ID (LIGHT)     ║
║ P3.2  Exec FE    : Frontend Exec Truth — refs FIELD/ERR (LIGHT)      ║
║ P4.1  Audit BE   : Pre-impl gate — 4A-BE (no CHECK-4)                ║
║ P4.2  Audit FE   : Pre-impl gate — 4A-FE (reads P4.1; no CHECK-4)   ║
║ P5    api-verify : Post-impl runtime verification — Backend only     ║
║ TEST-GEN         : Test-plans + manifest — OUTSIDE pipeline, owns    ║
║                    TC-BE/TC-FE; feeds P5                             ║
║ P-DOMAIN         : Domain Evolution Authority — Core/Extension/Model ║
║                    versions, version-ledger, Domain Releases, VRE    ║
║ P-REG            : Session-continuity compaction utility             ║
╠══════════════════════════════════════════════════════════════════════╣
║ Pipeline: P(-1)→P0→P0.5(GATE)→[P1∥P2.5-draft]→Reconcile→approval→P2→ ║
║   P3.1→P4.1→IMPL-BE→API-DOCS→(∥P5)→GATE→P3.2→P4.2→IMPL-FE            ║
║   (Test Gen Engine hangs off P3.1/P3.2 after ALIGN ✓; feeds P5)     ║
║ Selection/Reuse layer sits ABOVE the pipeline; pipeline unchanged.   ║
║ Versions: Core→Extension→Version→Reuse; immutable once published;    ║
║   pinned read-only reuse (CONTRACT-14); VRE propagates changes       ║
║   (CONTRACT-15).                                                     ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

═══════════════════════════════════════════════════════════════════
# PART 7 — GOVERNANCE ECOSYSTEM FILE MAP (v4.0)
═══════════════════════════════════════════════════════════════════

Which instruction file is present in which project (numbered per Part 3).
P15 = Test Generation Engine. multi-project-versioning.md is loaded in
ALL projects (its own row below).

```
FILE                              │P2│P3│P4│P5│P6│P7│P8│P9│P10│P11│P12│P15│ PURPOSE
──────────────────────────────────┼──┼──┼──┼──┼──┼──┼──┼──┼───┼───┼───┼───┼──────────────
shared-governance-core.md         │✓ │✓ │✓ │✓ │✓ │✓ │✓ │✓ │ ✓ │ — │ — │ ✓ │ Foundations
shared-governance-rules.md        │✓ │✓ │✓ │✓ │✓ │✓ │✓ │✓ │ ✓ │ — │ — │ ✓ │ Operational rules
shared-artifact-contracts.md(v4.0)│— │✓ │✓ │✓ │✓ │✓ │✓ │✓ │ ✓ │ — │ — │ ✓ │ 15 contracts
multi-project-versioning.md(v4.0) │✓ │✓ │✓ │✓ │✓ │✓ │✓ │✓ │ ✓ │ ✓ │ ✓ │ ✓ │ Selection & Reuse (ALL)
GOVERNANCE-CONFIG.md              │✓ │✓ │✓ │✓ │✓ │✓ │✓ │✓ │ ✓ │ ✓ │ ✓ │ ✓ │ Settings owner (all)
master-registry-schema.md         │— │— │✓ │— │— │— │— │— │ — │ — │ — │ — │ Registry structure
xm-resolution-event-protocol.md   │— │— │— │— │— │✓ │— │— │ — │ — │ — │ — │ XM lifecycle (BE only)
gov-stabilization-amendments+add. │— │— │— │— │— │— │— │✓ │ ✓ │ — │ — │ — │ Hardened rules ref.
platform-inception-engine.md      │✓ │— │— │— │— │— │— │— │ — │ — │ — │ — │ Project 2 instruction
prd-engine.md                     │— │✓ │— │— │— │— │— │— │ — │ — │ — │ — │ Project 3 instruction
srs-governance-engine.md          │— │— │✓ │— │— │— │— │— │ — │ — │ — │ — │ Project 4 instruction
db-governance-engine.md           │— │— │— │✓ │— │— │— │— │ — │ — │ — │ — │ Project 5 instruction
ui-ux-design-engine.md            │— │— │— │— │✓ │— │— │— │ — │ — │ — │ — │ Project 6 instruction
exec-plan-registry.md             │— │— │— │— │— │✓ │✓ │— │ — │ — │ — │ ✓ │ Shared P3 backbone
exec-plan-backend-engine.md       │— │— │— │— │— │✓ │— │— │ — │ — │ — │ — │ Project 7 (LIGHT)
exec-plan-frontend-engine.md      │— │— │— │— │— │— │✓ │— │ — │ — │ — │ — │ Project 8 (LIGHT)
test-generation-engine.md         │— │— │— │— │— │— │— │— │ — │ — │ — │ ✓ │ Project 15 (v3.0)
audit-backend-engine.md           │— │— │— │— │— │— │— │✓ │ ✓*│ — │ — │ — │ Project 9 (no CHECK-4)
audit-frontend-engine.md          │— │— │— │— │— │— │— │— │ ✓ │ — │ — │ — │ Project 10 (no CHECK-4)
api-verify-engine.md              │— │— │— │— │— │— │— │— │ — │ ✓ │ — │ — │ Project 11 instruction
state-registry-extractor.md       │— │— │— │— │— │— │— │— │ — │ — │ ✓ │ — │ Project 12 instruction
registry-builder.md               │(Project 1 — P(-1) — GOVERNANCE-CONFIG.md + multi-project-versioning.md)
PROJECT-DOMAIN-PROFILE-BUILDER.md │(Project 14 — P-DOMAIN — GOVERNANCE-CONFIG.md + multi-project-versioning.md)
──────────────────────────────────┴──┴──┴──┴──┴──┴──┴──┴──┴───┴───┴───┴───┴──────────────
```

**Reading the table:** P2 = Project 2 (Platform Inception) through
P15 = Project 15 (Test Generation Engine). Project 1 (Registry Builder,
P(-1)), Project 13 (Master Reviewer), and Project 14 (Domain Profile
Builder, P-DOMAIN) are described in prose in Part 3 rather than in this
grid. (*P10 loads audit-backend-engine.md only for the shared Finding
format.)

---

*End of DEPLOYMENT-MANIFEST.md (v4.0)*
*Follow Parts 2 → 3 → 5 in sequence for a verified deployment.*
*v4.0: a Multi-Project + Versioning "Selection & Reuse Layer" sits ABOVE*
*the unchanged pipeline. MULTI-PROJECT-VERSIONING-ARCHITECTURE.md is*
*loaded in every project; sessions open with CORE-11 `Project: <name>`;*
*per-project project-registry.md supersedes master-registry.md; P(-1) is*
*the Ecosystem Registry Authority and P-DOMAIN the Domain Evolution*
*Authority; shared-artifact-contracts.md at v4.0 (CONTRACT-14/15).*
*v3.0: P3 is LIGHT; the standalone Test Generation Engine (Project 15)*
*owns test-plans + manifest and feeds P5; P4 CHECK-4 removed.*
