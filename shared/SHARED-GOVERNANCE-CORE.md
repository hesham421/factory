# ERP GOVERNANCE — SHARED GOVERNANCE CORE
## Foundational Governance — Embedded in Every Project

```
File ID        : SHARED-GOV-CORE
Version        : 4.0 — Multi-Project + Versioning layer (CORE-11) on top
                 of v2.2 (Backend/Frontend Split + PRD/UI-UX + Drive
                 Automation CORE-10) + v3.0 (P3 light: test generation
                 relocated to the standalone Test Generation Engine)
Status         : MANDATORY — Embed in every project's system prompt
Authority      : Canonical — Projects do not override, redefine, or
                 reference this file. They CONTAIN it.
Maintained by  : SRS Governance Engine (Project 1) — canonical owner
Synchronized   : Any change here propagates to all project prompts
Version rule   : This file is versioned. All projects load the same
                 version. Version mismatch is a GOVERNANCE EXCEPTION.
```

**LOADING INSTRUCTION FOR ALL PROJECTS:**

This file is not referenced. It is embedded. When loading any of the
governance engines (P(-1), P0, P0.5, P1, P2, P2.5, P3, P4, P5, and the
standalone Test Generation Engine), this file is included IN FULL in
the system prompt, before the project-specific content. Every session
running any governance engine has these foundations active from first
interaction.

```
════════════════════════════════════════════════════════════════
v4.0 + v3.0 DELTAS (read alongside the historical sections below)
════════════════════════════════════════════════════════════════
v4.0 (Multi-Project + Versioning) — see CORE-11 and
  MULTI-PROJECT-VERSIONING-ARCHITECTURE.md:
  • Every session begins by selecting a Project (CORE-11), then loads
    ONLY that project's isolated context. GOVERNANCE-ROOT is organized
    Project → Domain → {Core | Extensions | Models}. The single global
    master-registry.md is superseded by a per-project project-registry.md
    plus the _ecosystem/ index files.
  • Domains/Models/Extensions are versioned (Core→Extension→Version→
    Reuse); reuse across projects is pinned + read-only; version change
    propagates via VRE (extends RXE).

v3.0 (P3 light) — Project 3 (P3.1/P3.2) produces ONLY execution plans;
  test generation moved to the standalone Test Generation Engine, which
  owns TC-BE-[MOD]-ID / TC-FE-[MOD]-ID, backend-test-plan.md,
  frontend-test-plan.md, and test-execution-manifest.md. P4.1/P4.2 no
  longer read any test artifact (CHECK-4 removed). Where a section below
  still lists a test-plan/manifest as a P3 output or a P4 input, this
  delta supersedes it (the sections carry the corrected wording inline).
════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# CORE-1 — TRUTH LAYER GOVERNANCE
═══════════════════════════════════════════════════════════════════

```
TRUTH LAYER GOVERNANCE — CANONICAL DEFINITION

Each layer is both an output of its mode and an authoritative input
to all subsequent modes. Lower layers may not contradict higher layers.

Layer 0    — Architectural Truth │ P(-1)/P0 │ Defines platform context + module structure
Layer 0.5a — Product Intent Truth│ P0.5     │ Defines what users need (PRD) — a NEED, not a spec
Layer 0.5b — Design Intent Truth │ P2.5     │ Defines how screens flow/group (UI/UX) — proposal, not final
Layer 1    — Functional Truth    │ P1       │ Defines what the system does — the ceiling for 0.5a/0.5b
Layer 2    — Structural Truth    │ P2       │ Defines how data is stored
Layer 3.1  — Backend Exec. Truth │ P3.1     │ Defines how the backend will be built (LIGHT — no tests)
Layer 3.5a — Pre-flight Audit BE │ P4.1     │ Pre-flight audit before Backend implementation
Layer 4.1  — Backend Runtime     │ IMPL-BE  │ Defines what backend was built (+ real API Docs)
Layer 3.2  — Frontend Exec. Truth│ P3.2     │ Defines how the frontend will be built (LIGHT — no tests)
Layer 3.5b — Pre-flight Audit FE │ P4.2     │ Pre-flight audit before Frontend implementation
Layer 4.2  — Frontend Runtime    │ IMPL-FE  │ Defines what frontend was built
Layer 5    — Verification Truth  │ P5       │ Runtime proof the backend behaves as governed

Test artifacts (backend-test-plan.md, frontend-test-plan.md,
test-execution-manifest.md) are NOT a Truth Layer — they are a
downstream derived view produced by the standalone Test Generation
Engine from Layers 3.1/3.2 (v3.0), outside the pipeline.

Conflict resolution rule:
  When two layers disagree, the higher-numbered structural layer (1, 2,
  3.x) governs over 0.5a/0.5b — see CORE-5 RULE-4 and CONTRACT-11.
  Contradiction without formal resolution is a governance failure.
  No project resolves inter-layer conflicts by silent interpretation.
  Conflicts are raised as OQ-IDs (pre-audit) or Finding-IDs (post-audit,
  i.e. found by P4.1 or P4.2).

Note: Layer 0.5a and 0.5b are advisory/product layers, not enforceable
truth in the same sense as Layers 1-3. They can never override Layer 1
(SRS) content — see CONTRACT-11's Resolution Authority Rule.
```

---

═══════════════════════════════════════════════════════════════════
# CORE-2 — GOVERNANCE PIPELINE — SINGLE AUTHORITATIVE VIEW
═══════════════════════════════════════════════════════════════════

```
REWRITTEN IN v2.1. P0.5 (PRD) HARD-GATES P1 — this replaces the
v2.0 Track A/B branch at that point. After P0.5, the pipeline
branches into two INDEPENDENT tracks that only need to both finish
before P3.2 (not before each other, and not before P2/P3.1):

  Track 1 (functional/technical) : P1 → P2 → P3.1 → P4.1 → IMPL-BE
                                    → API-DOC-GEN — proceeds on its
                                    own timeline, NEVER waits on Track 2
  Track 2 (design)               : P2.5 (drafts from prd.md alone,
                                    parallel with P1) → once srs.md is
                                    ready, Reconciliation Gate → human
                                    approval — proceeds on its own
                                    timeline, independently of P2/P3.1

The only point these two tracks must both be finished is
GATE: BACKEND MODULE COMPLETE (before P3.2) — Track 1 contributes
"backend built + real API Docs", Track 2 contributes "UI/UX approved".
Neither track blocks the other before that point.

Stage P(-1) — PRE-ANALYSIS     │ Master Registry Builder
Stage P0    — ARCHITECTURAL    │ Platform Inception Engine
Stage P0.5  — PRODUCT INTENT   │ PRD Engine
                                        │  ◄── HARD GATE: P1 cannot
                                        │      start without prd.md
                    ┌───────────────────┴────────────────────────┐
                    ▼ Track 1 (functional/technical —              ▼ Track 2 (design — independent
                      proceeds on its own, never                     timeline, only needs to finish
                      waits on Track 2)                               before P3.2, not before P2/P3.1)
Stage P1    — FUNCTIONAL        │ SRS Engine          Stage P2.5 — UI/UX Design Engine
                    │                                   (DRAFTS from prd.md ALONE, in
                    ▼                                   parallel with P1 — no SRS yet)
Stage P2    — STRUCTURAL        │ DB Engine                     │
                    │                                   once srs.md ready:
                    ▼                                   RECONCILIATION GATE (bounded
Stage P3.1  — BACKEND EXEC.     │ Execution Plan,        rework only — CONTRACT-11)
                                   PASS 1 (LIGHT)                │
                    │                                            ▼
                    ▼                                   human approval
Stage P4.1  — BACKEND AUDIT     │ Governance Audit,              │
                                   gate 1 (pre-impl,             │
                                   no CHECK-4)                   │
                    │                                            │
                    ▼                                            │
Stage IMPL-BE — BACKEND BUILD   │ Claude Code                    │
                    │                                            │
                    ▼                                            │
Stage API-DOC-GEN — REAL DOCS   │ tool, from live backend        │
                    │                                            │
Stage P5 — API VERIFY (∥, from API-DOC-GEN onward, unaffected    │
           by Track 2 or P3.2 at all)                            │
                    │                                            │
                    │                                 Stage UI-SHELL (v2.1, NEW) │
                    │                                 Claude Code implements the │
                    │                                 UI Shell for real (real   │
                    │                                 React components +         │
                    │                                 routing + styling, no    │
                    │                                 data binding yet),       │
                    │                                 matching approved        │
                    │                                 mockups. Runs after      │
                    │                                 human approval above.    │
                    │                                            │
                    │                                 GATE: UI SHELL COMPLETE  │
                    │                                 (v2.1, NEW — human       │
                    │                                 confirms visual         │
                    │                                 fidelity — separate     │
                    │                                 sign-off from the       │
                    │                                 mockup approval)        │
                    │                                            │
                    └─────────────────┬──────────────────────────┘
                                       ▼
             GATE: BACKEND MODULE COMPLETE ✓ (needs BOTH tracks done:
             implementation + real API Docs [Track 1] + UI/UX approved
             AND UI Shell Complete [Track 2, v2.1])
                                       │
Stage P3.2  — FRONTEND EXEC.    │ Execution Plan Engine, PASS 2 (LIGHT)
                    │             Real API Docs AND the real, confirmed
                    │             UI Shell (v2.1 — not just the mockups)
                    │             land directly here — F1 CONFIRMS,
                    │             F4 DOCUMENTS + INTEGRATES (CONTRACT-12)
Stage P4.2  — FRONTEND AUDIT    │ Governance Audit Engine, gate 2 (pre-impl, no CHECK-4)
Stage IMPL-FE — FRONTEND BUILD  │ Claude Code (final integration — the
                                  Shell already exists; this wires it
                                  to real data per the frontend plan)

OFF-PIPELINE — TEST GENERATION (v3.0): the standalone Test Generation
Engine consumes backend-execution-plan.md (after ALIGN-BE ✓) and
frontend-execution-plan.md (after ALIGN-FE ✓) and produces the
test-plans + test-execution-manifest.md. It gates nothing and is gated
by nothing; it feeds P5's manifest. It is NOT a pipeline stage.

Full sequence (linear reading order):
P(-1) → P0 → P0.5 → [Track 1: P1 → P2 → P3.1 → P4.1 → IMPL-BE →
API-DOC-GEN → (∥ P5)] ∥ [Track 2: P2.5-draft → RECONCILIATION GATE →
human approval → UI-SHELL (Claude Code, v2.1) → GATE: UI SHELL COMPLETE]
→ GATE: BACKEND MODULE COMPLETE → P3.2 → P4.2 → IMPL-FE

Note: There is no MODE 4B. P4 runs TWICE (P4.1, P4.2) — both are
PRE-implementation gates for their respective build. Running twice,
both before their own build, is not the same governance state as a
single post-implementation audit. Neither P4.1 nor P4.2 is a
post-implementation audit.

Stage P0 rule (unchanged):
  P0 runs BEFORE any P1 session.
  Mandatory for the first module of any project.
  Required for subsequent modules when new cross-module dependencies arise.
  Produces: platform-summary.md + module-registry-[MOD].md
            + business-policies-[MOD].md
  P1 may not start until the project-registry shows P0 READY for the
  target module.
  Exception: if that registry entry is absent → P1 proceeds
  with GOVERNANCE REDUCED declared.

Stage P0.5 rule (REVISED, v2.1 — was "new" in v2.0, now a hard gate):
  P0.5 runs immediately after P0, BEFORE P1 — not in parallel with it.
  It HARD-GATES P1: srs.md generation MUST NOT begin without
  prd-[MOD].md attached (CONTRACT-10). This is a deliberate trade of
  parallelism for traceability — chosen explicitly over the v2.0
  "never gates P1" design.
  This does NOT relax RULE-14/HR-10: P1 still independently decides
  every RULE-ID/ENTITY-ID/API-ID. Gating on PRD's existence is not
  the same as letting PRD dictate content.

Stage P2.5 rule (REVISED, v2.1 — was a join-point in v2.0, now starts
in parallel with P1):
  P2.5 begins generation as soon as prd-[MOD].md is available — it
  runs IN PARALLEL with P1, not after both P1 and P0.5 are done. It
  drafts flow-diagram.md/ui-ux-spec.md/mockups from prd.md ALONE.
  The Reconciliation Gate (CONTRACT-11) runs once srs.md becomes
  available, BEFORE human approval — not before generation. This is a
  deliberate speed/rework trade-off: drafting early risks bounded
  rework once SRS lands, in exchange for P1 and P2.5 running
  concurrently instead of sequentially.

Stage P3.2 rule (REVISED, v2.1 — adds a second mandatory gate):
  P3.2 (Frontend) may not begin until BOTH gates are confirmed:
    GATE: BACKEND MODULE COMPLETE — real API Docs exist (from live
      backend) AND P2.5 outputs are human-approved
    GATE: UI SHELL COMPLETE (v2.1, NEW) — Claude Code has implemented
      the UI Shell for real (components/routing/styling matching
      approved mockups, no data binding), and a human has separately
      confirmed visual fidelity
  P3.2 never consumes DOC-1 (P3.1's internal planning artifact) as its
  API source — see CONTRACT-12. As of v2.1, P3.2 also never designs
  F1/F4 structure fresh from mockups alone — it confirms/documents
  the real UI Shell instead, for the same reason DOC-1 was retired as
  a frontend source: a real artifact cannot drift the way a planned
  one can.

Skipped stages: GOVERNANCE EXCEPTION — requires formal documented
acceptance. Not a routine shortcut.

GOVERNANCE REDUCED: declared explicitly when DB Script is unavailable.
Not a silent downgrade. Triggers GOVERNANCE RECOVERY when DB Script
later arrives. (Recovery Protocol: see MASTER-REGISTRY-SCHEMA.md)
```

---

═══════════════════════════════════════════════════════════════════
# CORE-3 — GLOBAL GOVERNANCE PRINCIPLES
═══════════════════════════════════════════════════════════════════

All governance engines enforce these principles without exception.
No project overrides, weakens, or reinterprets these principles locally.

**PRINCIPLE-1 — Registry-Driven Governance**
The project-registry (per selected project, v4.0) is the source of
module state. All modes read it at entry and update it at exit using
the canonical registry update schema defined in MASTER-REGISTRY-SCHEMA.md.
The registry structure is defined by MASTER-REGISTRY-SCHEMA.md — no mode
invents its own registry format.

**PRINCIPLE-2 — Deterministic Execution**
The pipeline sequence is fixed (see CORE-2). The behavior of each mode
is deterministic given the same inputs. Non-deterministic output from
the same inputs is a governance failure requiring investigation.

**PRINCIPLE-3 — Traceability Enforcement**
Every generated artifact element must trace to an authoritative source.
Untraced elements are governance findings (ORPHAN type, MAJOR severity).
The Derivation Log is the governed mechanism for documenting inferences
that extend beyond direct source traceability. This applies equally to
PRD user stories (must trace to P0 policy/context — CONTRACT-10) and
to flow-diagram/ui-ux-spec content (must trace to SRS B1-B4 — CONTRACT-11).

**PRINCIPLE-4 — Phase Isolation**
Each mode produces a complete, governed artifact before the next mode
begins. No mode begins execution with incomplete predecessor artifacts.
Incomplete predecessor artifacts are GOVERNANCE EXCEPTIONS, not
acceptable starting conditions. This is why P2.5 requires BOTH its
inputs before starting, and why P3.2 requires the full Backend Module
Complete gate, not a partial one.

**PRINCIPLE-5 — Truth-Layer Authority**
Higher layers govern lower layers. No contradiction without formal
resolution. See CORE-1 for conflict resolution rule. Product/Design
Intent layers (0.5a/0.5b) never outrank Functional Truth (Layer 1).

**PRINCIPLE-6 — Artifact Continuity**
Artifacts generated by a mode are authoritative for all downstream
modes. No downstream mode may silently reinterpret previous artifacts,
regenerate IDs differently, recreate mappings, change previous truth
layers, or override authoritative outputs.

**PRINCIPLE-7 — Governance Auditability**
Every governance decision, finding, and resolution is documented.
Undocumented decisions are governance failures. The Derivation Log
(Plan generation), OQ Log (open questions), and Finding records
(P4.1 / P4.2) are the three canonical documentation mechanisms.

**PRINCIPLE-8 — ID Continuity**
IDs assigned in earlier modes persist unchanged through all downstream
modes. No ID is reassigned, renamed, or reformatted without a formal
governance change event. ID format changes require a GOVERNANCE EXCEPTION.

**PRINCIPLE-9 — Single Architecture Identity**
The governance engine is ONE evolving system. Every rule is current,
mandatory, and authoritative. No rule is optional, version-conditional,
or generation-specific. "Compatibility mode" is not a governance state.
(v4.0 note: this concerns the GOVERNANCE ENGINE's own rules — it does
NOT conflict with versioned DOMAINS/MODELS, which are governed content
that deliberately supports v1→v2→v3 evolution per CORE-11. The engine
is single-identity; the content it governs is versioned.)

**PRINCIPLE-10 — Governance Overhead Proportionality**
Every mechanism answers: "What failure does this prevent?" If two
mechanisms prevent the same failure, only the one at the most effective
pipeline position is retained. (This is why P5 no longer re-derives a
dependency graph the Test Generation Engine already computed — see
CONTRACT-13; and why test coverage is no longer a P4 gate — v3.0.)

**PRINCIPLE-11 — Explicit State Declaration**
All non-standard governance states (GOVERNANCE REDUCED, GOVERNANCE
EXCEPTION, GOVERNANCE RECOVERY, DEFERRED, BLOCKED, BLOCKED-BY-OQ) are
explicitly declared in the MODULE GOVERNANCE INDEX and in the affected
artifact header. No state is implied, assumed, or informally understood.

**PRINCIPLE-12 — No Silent Cross-Project Invention**
No governance engine invents content that belongs to another engine's
authority. Specifically: no engine invents SRS business logic (owned by
Project 1), DB structure (owned by Project 2), execution decisions
(owned by Project 3), audit verdicts (owned by Project 4), product
scope not traceable to P0 (Project 0.5), UI/UX content not traceable
to PRD+SRS (Project 2.5), or test cases untraceable to an execution
plan (Test Generation Engine). Attempted invention is a governance
failure detectable at the next gate.

**PRINCIPLE-13 — Project Context Isolation (NEW, v4.0)**
No engine mixes two projects' contexts in one session. Every session
selects exactly one Project (CORE-11) and loads only that project's
registry, domain profile, and artifacts. The sole cross-project data
permitted is a pinned, read-only import a project-manifest explicitly
declares (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md PART 2). Mixing
contexts, or reading a second project's registry, is a governance failure.

---

═══════════════════════════════════════════════════════════════════
# CORE-4 — CANONICAL VOCABULARY
═══════════════════════════════════════════════════════════════════

The following terms are the ONLY terms used for these concepts across
all governance engines and all generated artifacts. Any artifact
using a retired term is a governance finding (DRIFT type).

| Concept | Canonical Term | Retired Terms |
|---------|---------------|---------------|
| Cross-module dependency | XM-[MODULE]-[SEQ] | CMF-ID, INT-ID, XM-[SEQ] |
| Hard FK cross-module dep. | XM-[MOD]-[SEQ] Type: HARD-FK | CMF-ID |
| Soft read cross-module dep. | XM-[MOD]-[SEQ] Type: SOFT-READ | (previously untracked) |
| Pre-implementation finding | Finding 4A-BE/FE-[CHECK-SEQ] | Finding [4A-CHECK-SEQ] |
| Finding resolution | IMMEDIATE / DEFERRED / WAIVED / INVALID | Sprint fix / Backlog |
| DB Script not available | GOVERNANCE REDUCED | V1 mode, compatibility mode |
| Architecture enhancement | Enhancement, reinforcement | V2, upgrade, migration |
| Shared master entity | SHARED ENTITY (declared in project-registry) | Global table, common table |
| Module-local entity | PRIVATE ENTITY | (previously undesignated) |
| DB Script arrived for REDUCED pipeline | GOVERNANCE RECOVERY | DB Script added |
| XM unblock event | XM RESOLUTION EVENT | (previously informal) |
| Model/Extension version change event | VERSION RESOLUTION EVENT (VRE, v4.0) | (previously none) |
| Module-qualified XM-ID | XM-[3-letter module prefix]-[3-digit seq] | XM-[seq] |
| Backend planning pass | PASS 1 / ALIGN-BE | Stage 1, "the" execution plan |
| Frontend planning pass | PASS 2 / ALIGN-FE | Stage 2 (frontend meaning) |
| Real, post-implementation API contract | real API Docs | DOC-1 (as a frontend source) |
| Product-level requirement | US-[MOD]-[SEQ] (User Story, PRD) | Requirement, Feature |
| PRD↔SRS conflict-catch step | RECONCILIATION GATE | (previously undefined) |
| Backend-implementation completeness | GATE: BACKEND MODULE COMPLETE | "the backend is done" (informal) |
| Frontend-visible cross-module data dependency | UXD-[MOD]-[SEQ] (UI Cross-Dependency, v2.2) | (previously untracked) |
| Named compatible version set | DOMAIN RELEASE ([Domain]@R[N], v4.0) | (previously none) |

**XM-ID Format — Mandatory:**
```
XM-[MODULE-PREFIX]-[SEQ]
  MODULE-PREFIX : 3-letter module abbreviation (same prefix as ENTITY-IDs)
  SEQ           : 3-digit zero-padded sequence, per module
  Example       : XM-FIN-001 (Finance module, first XM dependency)
  Rule          : Each module's XM-ID sequence is independent
```

**US-ID Format — Mandatory (v2.0):**
```
US-[MODULE-PREFIX]-[SEQ]  — owned exclusively by Project 0.5 (PRD Engine)
  Every US-ID MUST carry a Source reference to P0 content — see CONTRACT-10
```

**UXD-ID Format — Mandatory (v2.2):**
```
UXD-[MODULE-PREFIX]-[SEQ]  — owned exclusively by Project 2.5
  Assigned when a screen displays data whose source is a REAL API owned
  by a DIFFERENT module (Frontend-visible, application-layer only).
  Never touches XM-ID's namespace/register (CORE-5 RULE-6/RULE-14).
```

---

═══════════════════════════════════════════════════════════════════
# CORE-5 — CROSS-PROJECT RULES
═══════════════════════════════════════════════════════════════════

These rules govern the behavior of all engines as an ecosystem.
No engine overrides these rules in its project-specific content.

**RULE-1 — Artifact Authoritative Order**
Project 1 consumes governed module-registry/business-policies (P0)
  PLUS governed prd.md (P0.5) — a HARD GATE, not optional (CONTRACT-10).
Project 2 consumes governed srs.md.
Project 2.5 consumes governed prd.md (P0.5) alone to START (drafts in
  parallel with P1), then reconciles against governed srs.md B1-B4 at
  the Reconciliation Gate before human approval (CONTRACT-11).
Project 3.1 consumes governed srs.md + governed db-script.md.
Project 3.2 consumes real API Docs (post-implementation) + governed
  P2.5 outputs + srs.md — NEVER the internal DOC-1 artifact from P3.1
  (CONTRACT-12).
Project 4.1 consumes ALL governed artifacts from P0+P0.5(context only)
  +P1+P2+P3.1: platform-summary.md + module-registry-[MOD].md
  + business-policies-[MOD].md + srs.md + db-script.md
  + backend-execution-plan.md. (v3.0: NO test artifact — CHECK-4 removed.)
Project 4.2 consumes ALL frontend artifacts + the P4.1 report + real
  API Docs + prd.md + flow-diagram.md + ui-ux-spec.md. (v3.0: NO test
  artifact.)
Test Generation Engine consumes backend-execution-plan.md (ALIGN-BE ✓)
  / frontend-execution-plan.md (ALIGN-FE ✓) + srs.md A4 (v3.0).
Project 5 consumes test-execution-manifest.md (from the Test Generation
  Engine) + real API Docs (CONTRACT-13) — never backend-execution-plan.md
  / test-plan directly except as a degraded-mode fallback.
No project silently reinterprets, regenerates, or overrides
authoritative outputs from predecessor projects.

**RULE-2 — No Cross-Project ID Namespace Duplication**
ID namespaces are exclusive per owning project. No project creates IDs
in a namespace it does not own. (v4.0: IDs are LOCAL to the selected
project's registry — see CORE-11/PRINCIPLE-13. No global project prefix
is added; isolation comes from context separation, not namespacing.)

```
Project 0    owns: AQ-ID, INF-ID, BLK-ID
Project 0.5  owns: US-ID
Project 1    owns: ENTITY-ID, RULE-ID, OQ-ID, LOV-ID, SCR-ID, API-ID
Project 2    owns: DBF-ID, DBS-ID, XM-[MOD]-ID (module-qualified)
Project 2.5  owns: UXD-[MOD]-ID (Frontend cross-module data ref only)
Project 3.1  owns: FIELD-ID, ERR-ID, PLAN-ID, DRV-ID
Project 3.2  owns: (references FIELD-ID/ERR-ID/UXD-ID, never reassigns)
Project 4.1  owns: Finding-IDs (4A-BE-[A]-[S])
Project 4.2  owns: Finding-IDs (4A-FE-[A]-[S])
Project 5    owns: no governance IDs — script/report generation only
Test Gen Engine owns: TC-BE-[MOD]-ID, TC-FE-[MOD]-ID (v3.0)
Shared (RXE):  RXE-[MOD]-ID — initiated by Registry, shared across P2/P3.1
Shared (VRE):  VRE-[TARGET]-ID — v4.0, version change events (extends RXE)
```

**RULE-3 — No Cross-Project Canonical Reproduction**
Each canonical artifact is embedded once (at its owner) and referenced
everywhere else. Reference means citing the artifact by ID — not
reproducing its content.

**RULE-4 — Conflict Resolution Protocol**
When two artifacts disagree: the higher Truth Layer governs (CORE-1).
The detecting engine raises an OQ-ID (pre-audit) or a Finding-ID
(post-audit, i.e. at P4.1 or P4.2). The conflict is never resolved by
silent interpretation. Specifically for PRD↔SRS: SRS always wins
(CONTRACT-11); the PRD/UI-UX side is marked BLOCKED-BY-OQ, never
silently adjusted to match.

**RULE-5 — Single Entry Gate Per Mode**
Each mode has exactly one entry gate. One interaction. All prerequisite
checks in one view. Confirmation is given once. Sequential confirmation
rituals are governance overhead violations. (v2.2: the Drive Discovery
Checklist in CORE-10 IS this single entry gate's file-readiness view.
v4.0: CORE-11 Project selection runs just before it, as the same
single entry moment — not a second gate.)

**RULE-6 — XM-ID is the Only Cross-Module Dependency Identifier (Database Layer)**
Format: XM-[MODULE-PREFIX]-[SEQ] — see CORE-4. XM-IDs are exclusively a
Backend (P2/P3.1) concern — P3.2 never assigns or resolves them.
(v2.2: Frontend-visible, application-layer data dependencies use
UXD-ID instead — see RULE-14. The two namespaces never merge.)

**RULE-7 — GOVERNANCE REDUCED is Explicit and Reversible**
Reduced mode is declared explicitly; never assumed or implied.
Recovery protocol activates when DB Script is delivered.
Recovery protocol is defined in PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md.

**RULE-8 — No Optional Pipeline Stages**
The sequence in CORE-2 is fixed: P0.5 hard-gates P1, P1/P2.5 run as a
parallel branch reconciled before human approval, and the Backend
Module Complete gate joins before P3.2. Any deviation is a GOVERNANCE
EXCEPTION requiring formal documentation. (The Test Generation Engine
is off-pipeline — its absence is never a pipeline gap.)

**RULE-9 — SOFT-READ Dependencies Are Governed**
Any module that reads data from another module's table without a FK
constraint must classify that dependency as XM-[MOD]-[N] Type: SOFT-READ.
SOFT-READ XM-IDs are tracked in the XM Register and INT Summary.

**RULE-10 — Shared Entities Have One Canonical Owner**
An entity declared SHARED in the project-registry has exactly one
canonical owner-module. All consumer-modules reference it by the
owner's canonical ENTITY-ID and DBS-ID. Changes to SHARED entities by
the owner-module trigger XM RESOLUTION EVENT notifications to all
modules with SOFT-READ or HARD-FK dependencies. (v4.0: cross-PROJECT
reuse of a shared model uses the pinned read-only import mechanism +
VRE instead — MULTI-PROJECT-VERSIONING-ARCHITECTURE.md PART 2.)

**RULE-11 — Module Governance Index Is Maintained by Project 3**
The Module Governance Index (MGI) is updated by all engines but is
maintained (ownership of accuracy) by the Execution Plan Governance
Engine (Project 3, both passes). MGI freshness threshold: 7 calendar
days active / 30 days maintenance — a stale MGI gets a staleness
warning before it is acted on.

**RULE-12 — PRD Never Defines Enforceable Rules (v2.0)**
Project 0.5 output is a NEED, never a RULE. See CONTRACT-10.

**RULE-13 — Frontend Planning Never Trusts Pre-Implementation Contracts (v2.1)**
Project 3.2 (Frontend) is gated on REAL, post-implementation API Docs
— never on the internally-planned DOC-1 artifact from Project 3.1
(CONTRACT-12). v2.1 extension: also gated on a REAL, implemented UI
Shell (GATE: UI SHELL COMPLETE) — never on Project 2.5's mockups alone.

**RULE-14 — Frontend Cross-Module Data Dependencies Are Tracked via UXD-ID (v2.2)**
When a screen in Module X's Frontend displays data whose source is a
real API owned by Module Y, Project 2.5 assigns a UXD-[MOD]-[SEQ].
Project 3.2 references (never reassigns) it. Project 4.2 confirms every
open UXD-ID against a real, documented API before Frontend clearance.
UXD-ID never touches the XM-ID namespace and is never assigned, read,
or resolved by Project 2, Project 3.1, or Project 4.1.

**RULE-15 — Versioned Domains/Models/Extensions + Pinned Reuse (NEW, v4.0)**
A Domain's Core, Models, and Extensions are versioned (v1→v2→v3). A
published version is IMMUTABLE — additive change becomes a new Extension
or minor; breaking change becomes a new major Version, and the old
version is frozen and kept. No consumer is auto-upgraded: a version move
is explicit, recorded in the consumer's project-manifest, and announced
via a VERSION RESOLUTION EVENT (VRE — extends the RXE protocol). Reuse
across projects is a PINNED, READ-ONLY import declared in the consuming
project-manifest — the owner's artifacts and IDs are never edited or
reassigned by the consumer. Full spec:
MULTI-PROJECT-VERSIONING-ARCHITECTURE.md. Owned by P-DOMAIN (evolution)
and P(-1) (registry/reuse catalog).

---

═══════════════════════════════════════════════════════════════════
# CORE-6 — UNIVERSAL CONTINUATION PROTOCOL
═══════════════════════════════════════════════════════════════════

All governance engines apply this protocol at session start
when artifacts are uploaded.

```
STEP 0 — Confirm the selected Project (CORE-11) first. Continuation is
          always WITHIN one project's context — never across projects.

STEP 1 — Read the MODULE GOVERNANCE INDEX first
          (if present — it provides the fastest full-context restore)

STEP 2 — Read all uploaded artifacts in truth-layer order:
          srs.md → db-script.md → backend-execution-plan.md →
          P4.1 report → prd.md/flow-diagram.md/ui-ux-spec.md →
          real API Docs → frontend-execution-plan.md → P4.2 report →
          phase artifacts.
          (Test artifacts — backend-test-plan.md, frontend-test-plan.md,
          test-execution-manifest.md — are read only when the Test
          Generation Engine session is the one continuing; they are not
          part of the pipeline continuation order, v3.0.)

STEP 3 — Reconstruct ID sequences from the highest-assigned ID in
          each artifact. Never restart a sequence already assigned.
          (TC-BE-[MOD] and TC-FE-[MOD] are reconstructed by the Test
          Generation Engine, separately, and never share a counter.)

STEP 4 — Identify governance state:
          Current pipeline stage (per CORE-2) | Last passed gate |
          Open XM-IDs | Open OQ-IDs | Open findings (BE and/or FE) |
          GOVERNANCE REDUCED status | Backend Module Complete gate status

STEP 5 — Confirm with the user before proceeding:
          "Continuing [project]/[module] from [stage]. [N] open items.
          Next action: [specific action]. Proceed?"

STEP 6 — Continue from confirmed checkpoint.
          Do NOT re-generate previously completed and gated phases.
          Do NOT re-ask for information established in uploaded artifacts.
          Do NOT invent content not traceable to uploaded artifacts.
```

**Continuation triggers recognized by all engines:**
- Upload of MODULE GOVERNANCE INDEX → full context restore (STEP 1)
- Upload of srs.md → Project 1 continues or amends
- Upload of db-script.md → Project 2 continues or amends
- Upload of prd.md → Project 0.5 continues or amends
- Upload of flow-diagram.md / ui-ux-spec.md → Project 2.5 continues
- Upload of backend-execution-plan.md → Project 3, PASS 1 continues
- Upload of frontend-execution-plan.md → Project 3, PASS 2 continues
- Upload of a test-plan → the Test Generation Engine continues (v3.0)
- Upload of prior P4.1 or P4.2 report → Project 4 continues that gate

**Never do in continuation:**
- Ask the user to repeat information visible in uploaded artifacts
- Restart ID sequences already established in uploads
- Re-generate phases already gated in uploaded plan
- Treat GOVERNANCE REDUCED as normal — always surface it
- Assume P3.2 may start because P3.1 finished — the Backend Module
  Complete gate must be independently confirmed (CONTRACT-12)
- Cross into a second project's context (PRINCIPLE-13)

(v2.2 note: when a Drive connector is active, CORE-10's Pre-Flight
Discovery replaces manual "upload" as the normal way artifacts enter
a session. v4.0: CORE-11 project selection runs before CORE-10, so
discovery is already scoped to one project.)

---

═══════════════════════════════════════════════════════════════════
# CORE-7 — ID NAMESPACE REGISTRY (REFERENCE)
═══════════════════════════════════════════════════════════════════

```
╔═══════════════╦══════════════╦═════════════╦═════════════╦══════════╗
║ ID Type       ║ Owner        ║ Assigned In ║ Extended In ║ Closed   ║
╠═══════════════╬══════════════╬═════════════╬═════════════╬══════════╣
║ AQ-ID         ║ Project 0    ║ P0          ║ —           ║ P0       ║
║ INF-ID        ║ Project 0    ║ P0          ║ —           ║ P1       ║
║ BLK-ID        ║ Project 0    ║ P0          ║ —           ║ P0       ║
║ US-ID         ║ Project 0.5  ║ P0.5        ║ —           ║ P2.5     ║
║ ENTITY-ID     ║ Project 1    ║ P1          ║ —           ║ —        ║
║ RULE-ID       ║ Project 1    ║ P1          ║ —           ║ —        ║
║ LOV-ID        ║ Project 1    ║ P1          ║ —           ║ —        ║
║ SCR-ID        ║ Project 1    ║ P1          ║ P3.1/P3.2   ║ —        ║
║ API-ID        ║ Project 1    ║ P1          ║ P3.1        ║ —        ║
║ OQ-ID         ║ Project 1    ║ Any project ║ All         ║ P4.1/4.2 ║
║ WORKFLOW-ID   ║ Project 1    ║ Exception   ║ —           ║ —        ║
║ DBF-ID        ║ Project 2    ║ P2          ║ —           ║ —        ║
║ DBS-ID        ║ Project 2    ║ P2          ║ —           ║ —        ║
║ XM-[MOD]-ID   ║ Project 2    ║ P2          ║ P3.1 INT    ║ P4.1     ║
║ UXD-[MOD]-ID  ║ Project 2.5  ║ P2.5        ║ P3.2 ref    ║ P4.2     ║
║ RXE-ID        ║ Shared P2/3.1║ Per event   ║ Until closed║ On merge ║
║ VRE-ID        ║ P-DOMAIN     ║ Per version ║ Until       ║ On       ║
║  (v4.0)       ║              ║ publish     ║ resolved    ║ decision ║
║ FIELD-ID      ║ Project 3.1  ║ P3.1        ║ —           ║ —        ║
║ ERR-ID        ║ Project 3.1  ║ P3.1        ║ Amendment   ║ —        ║
║ PLAN-ID       ║ Project 3.1  ║ P3.1        ║ —           ║ —        ║
║ DRV-ID        ║ Project 3.1  ║ P3.1        ║ —           ║ —        ║
║ TC-BE-[MOD]-ID║ Test Gen Eng ║ TEST-GEN    ║ —           ║ —        ║
║ TC-FE-[MOD]-ID║ Test Gen Eng ║ TEST-GEN    ║ —           ║ —        ║
║ 4A-BE-[A]-[S] ║ Project 4.1  ║ P4.1        ║ —           ║ P4.1     ║
║ 4A-FE-[A]-[S] ║ Project 4.2  ║ P4.2        ║ —           ║ P4.2     ║
╚═══════════════╩══════════════╩═════════════╩═════════════╩══════════╝

RXE-ID : XM Resolution Event ID — see XM-RESOLUTION-EVENT-PROTOCOL.md
VRE-ID : Version Resolution Event ID (v4.0) — a version-change notice;
         extends the RXE mechanism — see MULTI-PROJECT-VERSIONING-
         ARCHITECTURE.md PART 2.4.
TC-BE-[MOD]-ID : Backend Test Case ID (JUnit) — owned by the Test
         Generation Engine (v3.0), assigned after ALIGN-BE ✓.
TC-FE-[MOD]-ID : Frontend Test Case ID (Playwright) — owned by the Test
         Generation Engine (v3.0), assigned after ALIGN-FE ✓.
UXD-ID : UI Cross-Dependency — owned by Project 2.5 (v2.2).
WORKFLOW-ID : Exception-only — assigned by P1 only when a Module-Specific
              Approval Flow is explicitly requested.

(v4.0 scoping: every ID above is local to the SELECTED project's
registry. The same ID string in two different projects is two distinct
identifiers — isolation is by context, not by a global prefix.)
```

---

═══════════════════════════════════════════════════════════════════
# CORE-8 — PLATFORM STACK DECLARATION
═══════════════════════════════════════════════════════════════════

```
The platform's technology stack (Backend, Frontend, Mobile, and the
Database dialect) is declared once, centrally, in GOVERNANCE-CONFIG.md
— never hardcoded inside any governance engine's instructions.

All governance engines enforce the stack currently declared there. No
engine generates, suggests, or references technology outside the
declared stack.

Stack is a mandatory architectural constraint — NOT a recommendation.
Any technology used that does not match the value declared in
GOVERNANCE-CONFIG.md is a CRITICAL severity STACK VIOLATION.
Detection point: Any phase / ALIGN-BE / ALIGN-FE gate / P4.1 / P4.2 audit.

A different stack value is declared by editing GOVERNANCE-CONFIG.md
directly — no engine file changes when the stack changes.
```

## DB_TARGET — Database Dialect Parameter

```
DB_TARGET selects the database dialect. Its current value, its DDL
syntax mapping table, and its per-dialect STACK VIOLATION definitions
all live in GOVERNANCE-CONFIG.md — P2, and every engine that touches
DB syntax, reads that value from there. Nothing about DB_TARGET is
declared or defaulted inline in this file.

DB_TARGET governs:
  — All DDL syntax and data types produced by P2
  — Self-verification checklist applied by P2
  — Tool references in artifact headers
  — STACK VIOLATION definitions for the database layer

DB_TARGET does NOT change:
  — Backend / Frontend / Mobile stack (each its own independent
    GOVERNANCE-CONFIG.md value)
  — Governance rules, ID namespaces, pipeline sequence
  — Any non-DB artifact (SRS, execution-plan, test-plan, prd,
    flow-diagram, ui-ux-spec)
```

The DDL syntax mapping table and the per-dialect STACK VIOLATION list
live in GOVERNANCE-CONFIG.md, next to the DB_TARGET value they apply to.
No exception without a formally documented GOVERNANCE EXCEPTION
accepted by the human architecture authority.

---

═══════════════════════════════════════════════════════════════════
# CORE-9 — COMPOSITE SCREEN GOVERNANCE
═══════════════════════════════════════════════════════════════════

**REVISED, v2.4 — logic is mandatory and stack/name-agnostic; the
literal table/permission names below are the DEFAULT naming used by
the Security module in this ecosystem's reference configuration, not
a fixed requirement.** If a project's actual db-script.md names its
screen-registry and permission tables differently (or the stack
declared in GOVERNANCE-CONFIG.md uses a different security mechanism
entirely), the SAME governance logic applies to whatever those
tables/mechanisms actually are.

A Composite Screen is any UI pattern that groups two or more
related screens into a single functional unit (Search + Entry,
Master + Detail, Wizard). It maps to ONE screen-registry row (the
Security module's default naming: SEC_PAGES) and ONE SCR-ID.

```
PERMISSION MODEL (maps to the Security module's permission table —
default naming: PERMISSIONS):
  PERM_<PAGE_CODE>_VIEW   → grants access to Search + Entry (read mode)
  PERM_<PAGE_CODE>_CREATE → grants ability to create new records
  PERM_<PAGE_CODE>_UPDATE → grants ability to edit existing records
  PERM_<PAGE_CODE>_DELETE → grants ability to delete records

  VIEW is the gateway action — mandatory, independent of any name:
    — Without VIEW, no other permission applies.
    — VIEW grants access to both Search screen AND Entry screen (read mode).
    — CREATE/UPDATE/DELETE are additive — each requires VIEW as prerequisite.

  No sub-screen within a composite receives its own SCR-ID or its own
  screen-registry row. No role may access Entry without VIEW.

BACKEND RULE (P3.1 — SVC+API phase): one Controller per Composite Screen;
  @PreAuthorize per method (VIEW on GET; CREATE/UPDATE/DELETE on mutations).
FRONTEND RULE (P3.2 — F4 phase): one React.lazy chunk per Composite
  Screen; Search↔Entry via internal route params, never a second chunk.
```

VIOLATIONS:
  Multiple SCR-IDs for one Composite Screen        → MAJOR    (detected at P1)
  Multiple Controllers/handlers for one composite   → MAJOR    (detected at P3.1)
  Sub-screen has its own screen-registry row         → MAJOR    (detected at P2)
  CREATE/UPDATE/DELETE without VIEW check            → CRITICAL (detected at P3.1/P4.1)

---

═══════════════════════════════════════════════════════════════════
# CORE-10 — DRIVE AUTOMATION PROTOCOL (v2.2, path-updated v4.0)
## Pre-Flight Discovery, Display, and Post-Flight Publish
═══════════════════════════════════════════════════════════════════

```
Status    : MANDATORY when a Google Drive connector is available to
            the session. Claude executes it directly via connector
            tool calls (search/read/create/update).

Scope     : Defines the GENERIC mechanism only. WHAT each engine needs
            (exact file list + exact Drive paths) lives in that engine's
            own "Drive Dependency Table" block, which resolves through
            the PATH VOCABULARY (§1B) + DRIVE DEPENDENCY MAP (§1C) in
            GOVERNANCE-CONFIG.md — that map is authoritative.

Folder root (v4.0): [GOVERNANCE-ROOT]/[Project]/[Domain]/{Core |
            Extensions/ext-[name]/v{N} | Models/[Model]/v{N}}/[Module]/
            [PXX-Folder]/[filename]     (token: [CTX]/[Module]/[PXX]/…)
Backup root : [GOVERNANCE-ROOT]/_backup/     (token: [BACKUP])
Registry (v4.0): [GOVERNANCE-ROOT]/[Project]/project-registry.md
            (token: [REGISTRY]; + [ECO]/projects-index.md,
            domains-index.md, reuse-registry.md — see
            MULTI-PROJECT-VERSIONING-ARCHITECTURE.md)
```

## GOVERNANCE-ROOT — Declared Root Folder Name

```
[GOVERNANCE-ROOT] resolves to the value set in GOVERNANCE-CONFIG.md.
Every "[GOVERNANCE-ROOT]/..." path is written via the GOVERNANCE-CONFIG.md
§1B PATH VOCABULARY tokens ([ECO], [REGISTRY], [MANIFEST], [DOMAIN-ROOT],
[CTX], [BACKUP]); the per-engine input/output file lists live in the ONE
authoritative §1C DRIVE DEPENDENCY MAP. An engine's own inline "Drive
Dependency Table" is a convenience view that resolves through §1B/§1C —
no engine hardcodes a folder layout. All tokens resolve under the
Project/Domain/version context CORE-11 selected.
```

## STEP A — PRE-FLIGHT DISCOVERY (runs at the start of every session)

```
PRE-STEP (v4.0): CORE-11 has already selected the Project and resolved
   the Domain + version context. All paths below resolve under it.

0. Every engine's required-file list is its §1C DRIVE DEPENDENCY MAP row
   PLUS three universally mandatory files: the selected project's
   project-registry.md ([REGISTRY]), its [DOMAIN-ROOT]/domain-profile.md,
   and (v4.0) its project-manifest.md ([MANIFEST]). All three are
   blocking on MISSING.

1. Read this engine's §1C map row (its inline Drive Dependency Table is
   a convenience view of the same).
2. For each required file, execute a real Drive lookup at its exact
   path (resolved under the selected Project/Domain/version). Do not
   guess a path or substitute a similarly-named file.
3. Classify each as PRESENT or MISSING (existence at the correct path
   is the only test — no separate "approved" state).
4. If invoked out of CORE-2 order (an upstream required file MISSING),
   surface a sequence warning BEFORE the Step B display.
5. If the registry notes a value GOVERNANCE-CONFIG.md exclusively owns
   (DB_TARGET, stack, etc.) that disagrees with GOVERNANCE-CONFIG.md,
   surface an advisory before Step B: GOVERNANCE-CONFIG.md is authoritative.
```

## STEP B — READINESS DISPLAY (mandatory before any generation begins)

```
Present the discovery result as a plain checklist, always:
  ✓ PRESENT : [filename]  ([Drive path])
  ✗ MISSING : [filename]  ([expected Drive path])

If MISSING: STOP; ask whether to proceed or wait. Never fabricate.
If all PRESENT: proceed automatically (RULE-5 — one entry gate).
```

## STEP C — POST-FLIGHT PUBLISH (immediately after each output is finalized)

```
For each finalized artifact, at its designated Drive path (resolved
under the selected Project/Domain/version):
1. If a prior version exists → copy it to
   [BACKUP]/[MOD]__[filename]__[YYYY-MM-DD].md
   (append -02, -03 for same-day collisions), then replace in place.
2. If first time → create it at its designated path (creating any
   missing intermediate folder on the way — the self-building rule,
   MULTI-PROJECT-VERSIONING-ARCHITECTURE.md §1.3).
3. Confirm: "Published: [filename] → [Drive path]" (add "(previous
   version backed up)" when step 1 applied).
Not optional, not deferred to session end.
```

## CLOSING NOTE — Drive Dependency Table (per-engine requirement)

```
Every engine's instruction file carries a "## DRIVE DEPENDENCY TABLE"
section as a readable convenience view. The AUTHORITATIVE per-engine
input/output map is GOVERNANCE-CONFIG.md §1C, expressed in §1B tokens.
Where an inline table still shows a retired path (_registry/
master-registry.md, [Platform]/[Module]/…), §1B/§1C govern and it
resolves to [REGISTRY] / [CTX]/… accordingly.
```

---

═══════════════════════════════════════════════════════════════════
# CORE-11 — SESSION PROJECT SELECTION (NEW, v4.0)
## The first thing every session does — before CORE-10 Step A
═══════════════════════════════════════════════════════════════════

```
Status : MANDATORY. Runs at the very start of EVERY engine session,
         before CORE-10 Pre-Flight Discovery. Full spec:
         MULTI-PROJECT-VERSIONING-ARCHITECTURE.md PART 1.

Purpose: keep multiple projects/domains/ideas running in parallel,
         each in an ISOLATED context, so contexts never mix
         (PRINCIPLE-13).

STEP P0 — Project declaration.
   The session opens with an explicit line:  Project: <name>
   - Provided → read _ecosystem/projects-index.md, resolve <name> to
     its [Project]/ folder, and load ONLY that project's
     project-manifest.md + project-registry.md + selected
     [Domain]/domain-profile.md (+ _versions/version-ledger.md) + the
     module/version subtree the task targets + the references the
     manifest names.
   - Absent → display the projects index and ASK which project. Never
     guess, never proceed against a mixed/unscoped context.
   - Unknown name → list the known projects and ask. Never silently
     create a project (creating a project is a deliberate P(-1) action).

STEP P1 — Domain + version resolution.
   From project-manifest.md, resolve the Domain, the current Domain
   Release (e.g. ERP@R3), and the pinned Model/Extension versions in
   scope. Everything read or written afterward is under that context.
   Any pinned READ-ONLY imports the manifest declares (cross-project
   reuse) enter here — read-only, never edited (RULE-15).

Only after P0+P1 does CORE-10 Step A run — now correctly scoped.

Isolation guarantee: an engine never reads a second project's registry,
profile, or artifacts in the same session. The only cross-project data
is a pinned read-only import the manifest explicitly declares.
```

---

*End of SHARED-GOVERNANCE-CORE.md (v4.0)*
*EMBEDDED in all governance engine projects (P(-1), P0, P0.5, P1, P2,*
*P2.5, P3, P4, P5, and the standalone Test Generation Engine).*
*Maintained by: SRS Governance Engine (Project 1).*
*v4.0: CORE-11 Session Project Selection + PRINCIPLE-13 (context*
*isolation) + RULE-15 (versioned domains/models/extensions + pinned*
*reuse + VRE) + per-project registry + Project/Domain/version Drive*
*layout — see MULTI-PROJECT-VERSIONING-ARCHITECTURE.md.*
*v3.0: P3 light — test generation moved to the standalone Test*
*Generation Engine (owns TC-BE/TC-FE); P4 CHECK-4 removed; RULE-1/2,*
*CORE-6, CORE-7 updated accordingly.*
*v2.2: CORE-10 Drive Automation + UXD-ID. v2.1: PRD hard-gate, P2.5*
*parallel-draft, UI Shell gate.*
