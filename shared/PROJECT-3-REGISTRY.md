<!-- ════════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-IFA — Incremental Feature Addition                -->
<!-- ════════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-IFA (Incremental Feature Addition).**
> هذا المحرك (P3 backbone — loaded in BOTH P3.1 and P3.2) يكتسب **وضع IFA (delta-only)** لإضافة ميزة إلى
> موديول **تم تنفيذه بالفعل** — يقرأ إصدار v1 كـ baseline، يُخرج الجديد/
> المعدَّل فقط، ويُبقي v1 مجمَّداً. التعديل الخاص بهذا الملف: **AMEND-P3-P**.
>
> حمِّل `AMEND-IFA-INCREMENTAL-FEATURE-ADDITION.md` بجانب هذا الملف في نفس
> المشروع. التفاصيل الكاملة (المفاهيم المشتركة C1–C5 + سلوك كل محرك) في
> ذلك الملف. عند تعارض ظاهري، AMEND-IFA يحكم نطاق الـ delta فقط ولا يغيّر
> سلوك المسار الكامل (New-Module) القائم.
<!-- ════════════════════════════════════════════════════════════════ -->

# ERP GOVERNANCE — PROJECT 3 REGISTRY
## Shared Protocol, Pipeline Sequencing & ID Backbone (Project 3.1 + 3.2 + Test Generation Engine)

```
File ID        : EXEC-GOV-REGISTRY-v2
Role           : Backbone file for Project 3 — NOT a generation engine
                 itself. Contains the mechanisms, tables, and pipeline
                 map shared identically by PASS 1 (Backend) and PASS 2
                 (Frontend). As of v3.0 it is ALSO loaded by the
                 standalone Test Generation Engine, which reuses this
                 file's marker protocol and ID table for the test-plans
                 it now owns. Neither pass nor the Test Gen Engine
                 duplicates this content.
Truth Layer    : N/A — this file is infrastructure, not a Truth Layer
                 producer. See PROJECT-3-BACKEND-ENGINE.md (Layer 3.1),
                 PROJECT-3-FRONTEND-ENGINE.md (Layer 3.2), and
                 PROJECT-TEST-GENERATION-ENGINE.md (test artifacts).
Companion files: PROJECT-3-BACKEND-ENGINE.md   — PASS 1 (Backend, LIGHT)
                 PROJECT-3-FRONTEND-ENGINE.md  — PASS 2 (Frontend, LIGHT)
                 PROJECT-TEST-GENERATION-ENGINE.md — standalone test engine
```

```
════════════════════════════════════════════════════════════════
v3.0 NOTE — P3 LIGHT (test generation relocated)
════════════════════════════════════════════════════════════════
As of Project 3 v3.0, PASS 1 and PASS 2 produce ONLY execution plans —
no test artifact. The TEST-BE / TEST-FE phases and the TC Coverage
Matrix Summary (SECTION D) are REMOVED from the execution plans. Test
generation moved to the standalone Test Generation Engine
(PROJECT-TEST-GENERATION-ENGINE.md), which:
  - loads THIS backbone file (for the marker protocol + ID table),
  - owns TC-BE-[MOD]-ID and TC-FE-[MOD]-ID,
  - produces backend-test-plan.md, frontend-test-plan.md, and
    test-execution-manifest.md.
The marker protocol below (including the TEST-PLAN-BE / TEST-PLAN-FE
phase keys and TC atomic markers) is UNCHANGED and now applies to the
Test Generation Engine's output. Only the OWNER of those artifacts
changed; the mechanism is the same.
════════════════════════════════════════════════════════════════
```

**Why this file exists (maintainability rationale):** Project 3 is the
largest and most frequently amended engine in the ecosystem. Splitting
it into Backend/Frontend without a shared backbone would force every
future amendment to shared mechanisms (marker protocol, extraction
discipline, ID table) to be applied twice, with the risk of the two
copies silently drifting apart. This file is the single place those
mechanisms are defined; both engine files and the Test Generation
Engine reference it, none reproduce it.

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — PIPELINE SEQUENCING (Project 3 full map)
═══════════════════════════════════════════════════════════════════

```
                         ┌─────────────────────────────┐
                         │  PROJECT-3-BACKEND-ENGINE.md │
                         │  PASS 1 (LIGHT)              │
                         │                               │
                         │  CORE → DATA+DOM → SVC+API   │
                         │  → DOC → INT-C → INT-R       │
                         │  → SEC-BE                    │
                         │  → ALIGN-BE gate ✓            │
                         │                               │
                         │  → backend-execution-plan.md  │
                         │    (NO test artifacts)        │
                         └───────────────┬───────────────┘
                                         │
              ┌──────────────────────────┴───────────────────────┐
              │ (outside pipeline, after ALIGN-BE ✓)              │
              ▼                                                    │
   ┌─────────────────────────────────┐                            │
   │ PROJECT-TEST-GENERATION-ENGINE  │  ── standalone, off-pipeline│
   │ (Backend mode)                  │                            │
   │  → backend-test-plan.md          │                            │
   │  → test-execution-manifest.md    │  ── feeds P5 (api-verify)  │
   └─────────────────────────────────┘                            │
                                         ┌──────────────────────────┘
                          ─── MANDATORY PAUSE POINT ───
                          Real implementation happens here
                          (Claude Code, outside this project)
                          Real API Docs generated here
                          (api-doc-generator, outside this project)
                          Project 2.5 (UI/UX) may run in parallel
                          with all of the above
                                         │
                                         ▼
                         ┌─────────────────────────────────────┐
                         │  GATE: BACKEND MODULE COMPLETE       │
                         │  (CONTRACT-12 — evaluated by         │
                         │  PROJECT-3-FRONTEND-ENGINE.md         │
                         │  at its own entry, Section 2.0)      │
                         └───────────────┬───────────────────────┘
                                         │
                         ┌───────────────▼───────────────┐
                         │ PROJECT-3-FRONTEND-ENGINE.md   │
                         │ PASS 2 (LIGHT)                 │
                         │                                 │
                         │ F1 → F2 → F3 → F4 → SEC-FE      │
                         │ → ALIGN-FE gate ✓               │
                         │                                 │
                         │ → frontend-execution-plan.md    │
                         │   (NO test artifacts)           │
                         └───────────────┬───────────────┘
                                         │
              ┌──────────────────────────┴───────────────────────┐
              │ (outside pipeline, after ALIGN-FE ✓)              │
              ▼                                                    │
   ┌─────────────────────────────────┐                            │
   │ PROJECT-TEST-GENERATION-ENGINE  │  ── standalone, off-pipeline│
   │ (Frontend mode)                 │                            │
   │  → frontend-test-plan.md         │                            │
   └─────────────────────────────────┘                            │
                                         ┌──────────────────────────┘
                                         ▼
                              [Claude Code — frontend build]
```

**This is ONE project (Project 3), not two.** The split is temporal —
PASS 2 resumes the SAME governance identity as PASS 1, using the
Universal Continuation Protocol (SHARED-GOVERNANCE-CORE.md CORE-6),
after the pause point above. The Test Generation Engine is a SEPARATE
real project that hangs off each pass after its ALIGN gate ✓. See
shared-governance-rules.md RULE-8 for the full ecosystem-level
sequencing this fits into.

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — PHASE OWNERSHIP INDEX
═══════════════════════════════════════════════════════════════════

```
╔═══════════════╦══════════════════════════════════╦═══════════════════════════════╗
║ Phase / Gate  ║ Owning File                       ║ Section                        ║
╠═══════════════╬══════════════════════════════════╬═══════════════════════════════╣
║ CORE          ║ PROJECT-3-BACKEND-ENGINE.md       ║ 8.1                             ║
║ DATA+DOM      ║ PROJECT-3-BACKEND-ENGINE.md       ║ 8.2                             ║
║ SVC+API       ║ PROJECT-3-BACKEND-ENGINE.md       ║ 8.3                             ║
║ DOC           ║ PROJECT-3-BACKEND-ENGINE.md       ║ 8.4 (internal-only, v2.0)       ║
║ INT-C         ║ PROJECT-3-BACKEND-ENGINE.md       ║ 8.5                             ║
║ INT-R         ║ PROJECT-3-BACKEND-ENGINE.md       ║ 8.6                             ║
║ SEC-BE        ║ PROJECT-3-BACKEND-ENGINE.md       ║ 8.7                             ║
║ ALIGN-BE      ║ PROJECT-3-BACKEND-ENGINE.md       ║ 9                               ║
║ backend-test-plan.md │ PROJECT-TEST-GENERATION-ENGINE.md ║ 16 (v3.0 — moved)     ║
║ test-execution-manifest.md │ PROJECT-TEST-GENERATION-ENGINE.md ║ 16A (v3.0 — moved)║
╠═══════════════╬══════════════════════════════════╬═══════════════════════════════╣
║ GATE: BACKEND MODULE COMPLETE ║ PROJECT-3-FRONTEND-ENGINE.md ║ 2.0 (CONTRACT-12)     ║
║ F1            ║ PROJECT-3-FRONTEND-ENGINE.md      ║ 8.1                             ║
║ F2            ║ PROJECT-3-FRONTEND-ENGINE.md      ║ 8.2                             ║
║ F3            ║ PROJECT-3-FRONTEND-ENGINE.md      ║ 8.3                             ║
║ F4            ║ PROJECT-3-FRONTEND-ENGINE.md      ║ 8.4                             ║
║ SEC-FE        ║ PROJECT-3-FRONTEND-ENGINE.md      ║ 8.5                             ║
║ ALIGN-FE      ║ PROJECT-3-FRONTEND-ENGINE.md      ║ 9                               ║
║ frontend-test-plan.md │ PROJECT-TEST-GENERATION-ENGINE.md ║ 12 (v3.0 — moved)     ║
╠═══════════════╬══════════════════════════════════╬═══════════════════════════════╣
║ Task Detection║ THIS FILE (Registry)              ║ 3                               ║
║ Element ID Table ║ THIS FILE (Registry)           ║ 4                               ║
║ Extraction Protocol (2A) ║ PROJECT-3-BACKEND-ENGINE.md (full) ║ Section 2A/Sec3    ║
║ Marker Protocol ║ THIS FILE (Registry)             ║ 5                               ║
║ Single-File Output Rule ║ THIS FILE (Registry)     ║ 5.1                            ║
╚═══════════════╩══════════════════════════════════╩═══════════════════════════════╝
```

Note (v3.0): TEST-BE and TEST-FE are no longer phases of the execution
plans — they are removed. The backend-test-plan.md, frontend-test-plan.md,
and test-execution-manifest.md rows above now point to the standalone
Test Generation Engine, which reuses this file's marker protocol.

Any future amendment: check this table first. A change to shared
mechanism (extraction discipline, marker rules, ID table) is made HERE
ONLY — neither engine file nor the Test Generation Engine needs to
change as a result, which is the entire point of this split.

---

═══════════════════════════════════════════════════════════════════
# SECTION 3 — TASK TYPE DETECTION — AUTO-TRIGGER
═══════════════════════════════════════════════════════════════════

The engine (either pass) detects the task type from the user's request
automatically. Never ask the user which type — infer it.

```
╔══════════════════════════════════════════════╦═══════════════════╦══════════════════════╗
║ User Request Pattern                         ║ Task Type         ║ Scope                ║
╠══════════════════════════════════════════════╬═══════════════════╬══════════════════════╣
║ "New Feature —" or full new screen described ║ 🆕 New Feature    ║ All phases (this pass)║
║ "Feature Ext. —" or extend existing screen   ║ ➕ Feature Ext.   ║ Affected phases only ║
║ "Task Continue —" or resume from phase       ║ 🔄 Task Continue  ║ Named phase onward   ║
║ "Behavior Mod. —" or change logic only       ║ 🔧 Behavior Mod.  ║ Affected phases only ║
╚══════════════════════════════════════════════╩═══════════════════╩══════════════════════╝
```

## 3.1 Naming Convention

```
[Task Type] — [Screen/Feature Name] — [Module] — [Pass: BE | FE]

Examples:
  New Feature    — Vendor Management Screen  — Procurement Module — BE
  Feature Ext.   — Add Approval Field        — Purchase Orders Screen — FE
  Task Continue  — Resume Phase F2           — HR Employee Entry — FE
  Behavior Mod.  — Update Invoice Validation — Finance Module — BE
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 4 — ELEMENT IDs — REFERENCE TABLE
═══════════════════════════════════════════════════════════════════

```
╔═══════════════╦═══════════════════╦══════════════╦══════════════════════════════════╦══════════════════════════════╗
║ Element Type  ║ ID Format         ║ Owner        ║ Origin / Action                  ║ Used In                      ║
╠═══════════════╬═══════════════════╬══════════════╬══════════════════════════════════╬══════════════════════════════╣
║ Entity        ║ ENTITY-[MOD]-[SEQ]║ P1           ║ RECEIVED from srs.md             ║ DATA+DOM, F1, ALIGN-BE/FE     ║
║ Rule          ║ RULE-[MOD]-[SEQ]  ║ P1           ║ RECEIVED from srs.md             ║ DOMAIN, F3, ALIGN-BE/FE       ║
║ XM Dependency ║ XM-[MOD]-[SEQ]   ║ P2           ║ RECEIVED from db-script.md       ║ INT-C, INT-R (Backend only)  ║
║               ║                   ║              ║ P3.1 EXTENDS status/workaround   ║                              ║
║               ║                   ║              ║ P3.1 NEVER assigns new XM-IDs    ║                              ║
║               ║                   ║              ║ P3.2 NEVER touches XM-IDs at all ║                              ║
╠═══════════════╬═══════════════════╬══════════════╬══════════════════════════════════╬══════════════════════════════╣
║ Field         ║ FIELD-[4-digit]   ║ P3.1 ✓       ║ ASSIGNED in DATA+DOM phase       ║ SVC+API, F1, F2, F3 (ref)     ║
║ API           ║ API-[MOD]-[SEQ]   ║ P3.1 ✓       ║ ASSIGNED in SVC+API phase        ║ DOC, F2, F3, ALIGN-BE/FE      ║
║ Error Code    ║ ERR-[4-digit]     ║ P3.1 ✓       ║ ASSIGNED in SVC+API phase        ║ DOC, F3 (ref)                 ║
║ Plan          ║ PLAN-[MOD]-[SEQ]  ║ P3.1 ✓       ║ ASSIGNED at plan creation        ║ all backend artifacts         ║
║ Screen        ║ SCR-[MOD]-[SEQ]   ║ P1→P3.1/2    ║ RECEIVED from SRS; used in F1    ║ F2, F3, F4, SEC-BE/FE, ALIGN  ║
║ Test Case (BE)║ TC-BE-[MOD]-[SEQ] ║ TEST-GEN ✓   ║ ASSIGNED in backend-test-plan.md ║ backend-test-plan.md          ║
║               ║                   ║ (v3.0)       ║ (Test Generation Engine)         ║                              ║
║ Test Case (FE)║ TC-FE-[MOD]-[SEQ] ║ TEST-GEN ✓   ║ ASSIGNED in frontend-test-plan.md║ frontend-test-plan.md         ║
║               ║                   ║ (v3.0)       ║ (Test Generation Engine)         ║                              ║
║ Open Question ║ OQ-[MOD]-[SEQ]   ║ P1→P3        ║ RECEIVED from SRS; continued     ║ OQ Log (any phase)            ║
║ Query Ref     ║ QR-[MOD]-[SEQ]   ║ P3.1 ✓       ║ ASSIGNED in DATA+DOM / SVC+API   ║ Query Reference Catalog (BE)  ║
╚═══════════════╩═══════════════════╩══════════════╩══════════════════════════════════╩══════════════════════════════╝

CRITICAL RULES:
- ENTITY-ID, RULE-ID: always sourced from srs.md — neither pass ever invents them
- XM-[MOD]-[N]: always sourced from db-script.md XM Register — PASS 1 never
  assigns new XM-IDs; PASS 2 never touches XM-IDs in any way
- QR-IDs are agent-reference only — agent rewrites queries from scratch
- FIELD-ID, ERR-ID: PASS 1 assigns; PASS 2 references only, never reassigns
- TC-BE-ID and TC-FE-ID are owned ONLY by the standalone Test Generation
  Engine (v3.0) — P3.1/P3.2 never assign them. They are separate
  namespaces — no shared counter, no collision risk.
- Any ID conflict between a plan and an upstream artifact → flag immediately as ✗
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 5 — SINGLE-FILE OUTPUT RULE + MARKER PROTOCOL
═══════════════════════════════════════════════════════════════════


## 5.1 The Fundamental Rule

```
╔══════════════════════════════════════════════════════════════════╗
║      SINGLE-FILE OUTPUT — PER PASS — MANDATORY SEQUENCE          ║
╠══════════════════════════════════════════════════════════════════╣
║ PASS 1 — backend-execution-plan.md (LIGHT)                      ║
║   Generated as ONE uninterrupted MD file (backend phases only). ║
║   ✗ No session breaks between phases  ✗ No Human Checkpoint      ║
║   ✓ Internal gates auto-evaluated — failures corrected inline    ║
║   ✓ ALIGN-BE gate runs automatically after SEC-BE phase          ║
║   ✓ Plan is complete and agent-ready at end of generation        ║
║   ✗ NO test artifact produced here (v3.0)                        ║
╠══════════════════════════════════════════════════════════════════╣
║ (OUTSIDE PIPELINE) — backend-test-plan.md + manifest            ║
║   PREREQUISITE: Gate ALIGN-BE ✓ confirmed                        ║
║   Produced by the standalone Test Generation Engine (v3.0),     ║
║   which assigns TC-BE-[MOD]-IDs. See                            ║
║   PROJECT-TEST-GENERATION-ENGINE.md Section 16 + 16A.           ║
╠══════════════════════════════════════════════════════════════════╣
║ ─── MANDATORY PAUSE POINT — real implementation + real API Docs ║
╠══════════════════════════════════════════════════════════════════╣
║ PASS 2 — frontend-execution-plan.md (LIGHT)                     ║
║   PREREQUISITE: GATE: BACKEND MODULE COMPLETE ✓ (CONTRACT-12)    ║
║   Generated as ONE uninterrupted MD file (frontend phases only). ║
║   ✓ ALIGN-FE gate runs automatically after SEC-FE phase          ║
║   ✗ NO test artifact produced here (v3.0)                        ║
╠══════════════════════════════════════════════════════════════════╣
║ (OUTSIDE PIPELINE) — frontend-test-plan.md                      ║
║   PREREQUISITE: Gate ALIGN-FE ✓ confirmed                        ║
║   Produced by the standalone Test Generation Engine (v3.0),     ║
║   which assigns TC-FE-[MOD]-IDs. See                            ║
║   PROJECT-TEST-GENERATION-ENGINE.md Section 12.                 ║
╚══════════════════════════════════════════════════════════════════╝
```

## 5.2 Gate Failure Handling (Inline Correction)

When an internal gate detects a violation during generation:

```
INLINE CORRECTION PROTOCOL:
  1. Detect: gate condition not met
  2. Identify: which element is missing or inconsistent
  3. Correct: fix the element in the same generation pass
  4. Record: correction in Derivation Log (DRV-ID)
  5. Continue: proceed to next phase — do not stop

  If correction requires revisiting a prior phase:
    → Mark the prior phase with a REVISION note
    → Apply correction retroactively
    → Record in Derivation Log
    → Gate PASSED ✓ after correction

  If a gate failure CANNOT be corrected without user input:
    → Assign OQ-ID (CLIENT-POLICY-OQ level)
    → Mark gate as ⏸ BLOCKED — see OQ-[ID]
    → Continue remaining phases where possible
    → ALIGN gate captures all ⏸ items
```

## 5.3 File Structures (per pass)

```
backend-execution-plan.md — COMPLETE SINGLE FILE (PASS 1, LIGHT)
══════════════════════════════════════════════════════════════════
[SECTION 0]  PLAN HEADER
[SECTION 1]  PLAN INDEX (entity, field, API, rule, screen, LOV, QR registries)
[SECTION 2]  DB ALIGNMENT MANIFEST
[SECTION 3]  OPEN QUESTIONS LOG (continuation)
[SECTION 4]  DERIVATION LOG
──────────────────────────────────────────────────────────────────
[PHASE CORE]      Architectural Policies & Package Structure
[PHASE DATA+DOM]  Entity Specs + Field Assignments + Domain Rules
[PHASE SVC+API]   API Contracts + DTOs + Error Catalog
[PHASE DOC]       Contract Stabilization — internal-only (v2.0)
[PHASE INT-C]     Integration Contracts — INT-C GATE ✓
[PHASE INT-R]     Runtime Activation Status
[PHASE SEC-BE]    API-level Security + Permission Seed Data
[PHASE ALIGN-BE]  Internal Consistency Gate — auto-runs after SEC-BE
──────────────────────────────────────────────────────────────────
[SECTION A]  ERROR CATALOG (canonical)
[SECTION B]  QUERY REFERENCE CATALOG (agent reference)
[SECTION C]  REGISTRY UPDATE BLOCK
══════════════════════════════════════════════════════════════════
NOTE (v3.0): there is NO SECTION D / TC Coverage Matrix Summary here.
The plan is LIGHT — all TC content lives in the Test Generation
Engine's backend-test-plan.md, never in the execution plan.

frontend-execution-plan.md — COMPLETE SINGLE FILE (PASS 2, LIGHT)
══════════════════════════════════════════════════════════════════
[SECTION 0]  PLAN HEADER (+ GATE: BACKEND MODULE COMPLETE confirmation)
──────────────────────────────────────────────────────────────────
[PHASE F1]        Frontend Model Specifications
[PHASE F2]        Frontend Service Contracts
[PHASE F3]        Frontend Validation Rules
[PHASE F4]        Frontend Routing & Component Structure
[PHASE SEC-FE]    UI-level Security (guards + show/hide behavior)
[PHASE ALIGN-FE]  Internal Consistency Gate — auto-runs after SEC-FE
══════════════════════════════════════════════════════════════════
NOTE (v3.0): there is NO SECTION D / TC Coverage Matrix Summary here
either. All TC content lives in the Test Generation Engine's
frontend-test-plan.md.

Full TC blocks (Given/When/Then) live in backend-test-plan.md and
frontend-test-plan.md — both produced by the standalone Test
Generation Engine — never in either execution-plan.md.
```

## 5.4 Derivation — Controlled Inference Rules

Derivation is inferring a plan element not explicitly stated in the SRS.
Allowed ONLY when ONE criterion is met:

```
CRITERION-1 — Present implicitly in a related entity, attribute, or relationship in SRS
CRITERION-2 — Referenced or implied in a "The system MUST" validation rule
CRITERION-3 — Part of a workflow step, state transition, or operation sequence in SRS

IF NONE MET:
  Do NOT infer. Mark as: [NOT DEFINED IN SRS → OQ-XXX]
  Add to OQ Log. Reference OQ-ID inline.

EVERY derivation logged in Derivation Log:
  DRV-[SEQ] | Element | Criterion (1/2/3) | SRS source reference
```

## 5.5 Zero-Question Protocol — P3

```
Before raising any OQ during plan generation, apply in order:

STEP 0 — Client Policy check (FIRST)
  RULE-ID marked "Source: Client Policy"?
  YES → raise OQ immediately — flag as CLIENT-POLICY-OQ

STEP 1 — SRS (srs.md)             Answer in srs.md? YES → use it — no OQ
STEP 2 — DB Script (db-script.md) Answer in db-script.md? YES → use it — no OQ
STEP 3 — Registries               Answer in module/master-registry? YES → use it — no OQ
STEP 4 — ERP Technical Best Practice
  Clear Spring Boot / React / DB best practice?
  YES → apply + log as DRV-[SEQ] — no OQ

OQ raised only if: Steps 0–4 all fail AND gap blocks implementation
OQ target: 0–1 per module
```

## 5.6 EXCEPTION Module Handling

```
EXCEPTION modules: pre-existing systems — not built by this project.

P3 rules:
  ✓ Write FK references using registry IDs
  ✓ Write SOFT-READ calls per XM-ID entries from DB Script
  ✓ Write API call specifications for EXCEPTION module interfaces

  ✗ Never write DDL for EXCEPTION tables
  ✗ Never specify entity/repository for EXCEPTION tables
  ✗ Never specify frontend models duplicating EXCEPTION module screens

  EXCEPTION flag in phase outputs:
    Every reference to EXCEPTION entity must note:
    [EXCEPTION — [Module Name] — read-only reference]
```

## 5.7 Artifact Marker Protocol — Navigability & Extraction

### 5.7.1 — Purpose

```
Markers are HTML comments embedded during artifact generation.
They add addressability to the artifact — NOT new structure.

They do NOT:
  ✗ Change any content
  ✗ Split files into multiple files
  ✗ Add new phases or sections
  ✗ Affect gate conditions or governance logic

They DO:
  ✓ Allow any Agent to extract a specific Phase without loading the full file
  ✓ Allow an agent to target individual TC blocks directly
  ✓ Allow Claude Code to extract a specific API contract by ID
  ✓ Reduce context window consumption for targeted operations
```

### 5.7.2 — Marker Levels

```
Level 1 — PHASE Marker     : wraps every phase (always)
Sub-phase Markers          : inside PHASE — conditional, threshold-triggered
Level 2 — Atomic Marker    : wraps API-ID / XM-ID / TC-ID only (always)
                             innermost level — never contains other markers

Hierarchy in backend-/frontend-execution-plan.md : PHASE → [SUB] → ATOMIC
Hierarchy in backend-/frontend-test-plan.md      : PHASE → [SUB] → ATOMIC (v2.0 — no MARK level)

No other levels permitted.
No markers for: FIELD-ID / ERR-ID / RULE-ID / LOV-ID / SCR-ID
These are read within their containing Phase — not targeted individually.
```

### 5.7.3 — Level 1: Phase Markers (Mandatory — Every Phase)

Every phase in either execution-plan.md, or in a test-plan produced by
the Test Generation Engine, MUST be wrapped with Level 1 markers upon
generation:

```
<!-- PHASE:{PHASE-KEY}:START -->
...full phase content...
<!-- PHASE:{PHASE-KEY}:END -->
```

Phase keys — canonical, no variation permitted:

```
╔══════════════════╦══════════════╦═════════════════════════════════════╗
║ Phase            ║ Key          ║ Lives in                             ║
╠══════════════════╬══════════════╬═════════════════════════════════════╣
║ CORE             ║ CORE         ║ backend-execution-plan.md            ║
║ DATA+DOM         ║ DATA-DOM     ║ backend-execution-plan.md            ║
║ SVC+API          ║ SVC-API      ║ backend-execution-plan.md            ║
║ DOC              ║ DOC          ║ backend-execution-plan.md            ║
║ INT-C            ║ INT-C        ║ backend-execution-plan.md            ║
║ INT-R            ║ INT-R        ║ backend-execution-plan.md            ║
║ SEC-BE           ║ SEC-BE       ║ backend-execution-plan.md            ║
║ ALIGN-BE         ║ ALIGN-BE     ║ backend-execution-plan.md            ║
║ F1               ║ F1           ║ frontend-execution-plan.md           ║
║ F2               ║ F2           ║ frontend-execution-plan.md           ║
║ F3               ║ F3           ║ frontend-execution-plan.md           ║
║ F4               ║ F4           ║ frontend-execution-plan.md           ║
║ SEC-FE           ║ SEC-FE       ║ frontend-execution-plan.md           ║
║ ALIGN-FE         ║ ALIGN-FE     ║ frontend-execution-plan.md           ║
║ backend-test-plan.md  ║ TEST-PLAN-BE ║ backend-test-plan.md (Test Gen) ║
║ frontend-test-plan.md ║ TEST-PLAN-FE ║ frontend-test-plan.md (Test Gen)║
╚══════════════════╩══════════════╩═════════════════════════════════════╝
```

Note (v3.0): the TEST-PLAN-BE / TEST-PLAN-FE keys are used by the
standalone Test Generation Engine (which loads this backbone), not by
the execution-plan passes.

### 5.7.4 — Sub-phase Markers (Conditional — Threshold Trigger Only)

Sub-phase markers are added ONLY when a Phase exceeds its threshold.
Split is always semantic — never by arbitrary count or line length.

```
╔══════════════════╦══════════════════════════╦════════════════════════════════╗
║ Phase            ║ Threshold                ║ Sub-phase Grouping             ║
╠══════════════════╬══════════════════════════╬════════════════════════════════╣
║ CORE             ║ Never splits             ║ —                              ║
║ DATA+DOM         ║ Entities ≥ 5             ║ per entity semantic group      ║
║ SVC+API          ║ APIs ≥ 8 / Methods ≥ 6  ║ CRUD / SEARCH / INT            ║
║ DOC              ║ Never splits             ║ —                              ║
║ INT-C            ║ XM-IDs ≥ 5              ║ per target module group        ║
║ INT-R            ║ XM-IDs ≥ 5              ║ per target module group        ║
║ F1               ║ Screens ≥ 5             ║ per SCR-ID                     ║
║ F2               ║ Screens ≥ 5             ║ per SCR-ID                     ║
║ F3               ║ Screens ≥ 5             ║ per SCR-ID                     ║
║ SEC-BE / SEC-FE  ║ Never splits             ║ —                              ║
║ ALIGN-BE/ALIGN-FE║ Never splits             ║ —                              ║
║ backend-test-plan.md  ║ TCs > 12            ║ SUB:RULE-SCENARIOS /            ║
║ (TEST-PLAN-BE)   ║                          ║ SUB:API-SCENARIOS              ║
║ frontend-test-plan.md ║ TCs > 8             ║ SUB:UI-FLOWS / SUB:INT-FLOW    ║
║ (TEST-PLAN-FE)   ║                          ║                                ║
╚══════════════════╩══════════════════════════╩════════════════════════════════╝
```

```
v2.0 SIMPLIFICATION: the MARK:JUNIT / MARK:PLAYWRIGHT layer from the
pre-split version is REMOVED. Now that backend-test-plan.md is
JUnit-only and frontend-test-plan.md is Playwright-only, the FILE ITSELF
is the tool boundary. (Both files are produced by the Test Generation
Engine as of v3.0.)

backend-test-plan.md TC threshold  : TCs > 12 → split into
                                      SUB:RULE-SCENARIOS / SUB:API-SCENARIOS
                                      TCs ≤ 12 → all TCs directly under
                                      PHASE:TEST-PLAN-BE, no SUB
frontend-test-plan.md TC threshold : TCs > 8  → split into
                                      SUB:UI-FLOWS / SUB:INT-FLOW
                                      TCs ≤ 8  → all TCs directly under
                                      PHASE:TEST-PLAN-FE, no SUB
```

Sub-phase marker format:

```
<!-- PHASE:{PHASE-KEY}:START -->
  <!-- SUB:{LABEL}:START -->
  ...sub-phase content...
  <!-- SUB:{LABEL}:END -->
<!-- PHASE:{PHASE-KEY}:END -->
```

Sub-phase label conventions:
```
F1 / F2 / F3 / F4 → label = SCR-ID    e.g. SUB:F1-SCR-ORG-001 (with phase prefix, AMEND-P3-N)
SVC+API       → label = semantic group e.g. SUB:SVC-API-CRUD / SUB:SVC-API-SEARCH
INT-C / INT-R → label = module name    e.g. SUB:INT-C-FINANCE / SUB:INT-R-FINANCE
DATA+DOM      → label = entity group   e.g. SUB:DATA-DOM-MASTER
backend-test-plan.md  : label = RULE-SCENARIOS | API-SCENARIOS (if TCs > 12)
frontend-test-plan.md : label = UI-FLOWS | INT-FLOW (if TCs > 8)
                ✗ TP-SEC-N is a documentation section label — NOT a SUB marker label
                ✗ Below threshold: TCs sit directly under PHASE:TEST-PLAN-BE/FE — no SUB
```

Gate rule: PHASE gate is issued only after ALL sub-phases are complete.
ALIGN-BE / ALIGN-FE phases: never split — gate requires full phase as one unit.

### 5.7.5 — Level 2: Atomic Markers (Three Types Only — Always Applied)

Atomic markers wrap individual addressable elements.
Applied to these three types regardless of phase size:

```
<!-- API:{API-ID}:START -->
...API contract content (method, endpoint, request, response, errors)...
<!-- API:{API-ID}:END -->

<!-- XM:{XM-ID}:START -->
...XM dependency content (type, target, status, workaround)...
<!-- XM:{XM-ID}:END -->

<!-- TC:{TC-ID}:START -->
...TC block (Given / When / Then — full scenario)...
<!-- TC:{TC-ID}:END -->
```

**v2.0 — no MARK level.** TC markers sit directly under PHASE:TEST-PLAN-BE
or PHASE:TEST-PLAN-FE (within SUB if the threshold is exceeded), in the
test-plans produced by the Test Generation Engine.

```
Example A — below threshold (no SUB):

<!-- PHASE:TEST-PLAN-BE:START -->
    <!-- TC:TC-BE-[MOD]-001:START -->...<!-- TC:TC-BE-[MOD]-001:END -->
    <!-- TC:TC-BE-[MOD]-002:START -->...<!-- TC:TC-BE-[MOD]-002:END -->
<!-- PHASE:TEST-PLAN-BE:END -->
```

```
Example B — above threshold (SUB added):

<!-- PHASE:TEST-PLAN-BE:START -->        (> 12 TCs → split)
    <!-- SUB:RULE-SCENARIOS:START -->
    <!-- TC:TC-BE-[MOD]-001:START -->...<!-- TC:TC-BE-[MOD]-001:END -->
    <!-- SUB:RULE-SCENARIOS:END -->
    <!-- SUB:API-SCENARIOS:START -->
    <!-- TC:TC-BE-[MOD]-009:START -->...<!-- TC:TC-BE-[MOD]-009:END -->
    <!-- SUB:API-SCENARIOS:END -->
<!-- PHASE:TEST-PLAN-BE:END -->
```

Placement:
```
API Atomic Markers    → inside PHASE:SVC-API (within SUB if present) — backend
XM Atomic Markers     → inside PHASE:INT-C and PHASE:INT-R (within SUB if present) — backend
TC Atomic Markers     → inside PHASE:TEST-PLAN-BE or PHASE:TEST-PLAN-FE (Test Gen Engine)
PHASE:TEST-PLAN-BE    → contains: RULE-ID TCs + API-ID TCs + Mandatory-J TCs
PHASE:TEST-PLAN-FE    → contains: UI Flow TCs + INT Flow TCs + Mandatory-P TCs
```

No other element types receive Atomic markers.

**CRITICAL — Atomic Markers are addressing, NOT a file-splitting instruction:**

```
Atomic markers (API/XM/TC) exist so an Agent can locate and extract a
specific element BY SEARCHING WITHIN a file — they do NOT mean each
atomic element becomes its own physical file.

When Agent 3 (or any packaging tool) physically splits artifacts into
separate files, the splitting unit is ALWAYS the SUB (if present) or
the PHASE (if no SUB) — never the individual API/XM/TC.
```

### 5.7.6 — Marker Rules (Non-Negotiable)

```
Rule 1 — Every START has a matching END in the same artifact.
Rule 2 — Hierarchy is strict (v2.0 — no MARK level):
            Any of the four files : PHASE → [SUB] → ATOMIC     ✓
            ATOMIC outside PHASE                                ✗ forbidden
            SUB outside PHASE                                   ✗ forbidden
Rule 3 — Every ID in a marker is exact and sourced from the artifact registry.
Rule 4 — Markers are content-neutral.
Rule 5 — CORE, ALIGN-BE, ALIGN-FE phases: Level 1 marker only.
Rule 6 — One atomic ID = one dedicated block, never grouped.
```

### 5.7.7 — Context Window Overhead Estimate

```
Total marker overhead across artifacts: < 5% — acceptable.
Benefit: targeted extraction eliminates 95%+ of context for scoped tasks.
```

---

═══════════════════════════════════════════════════════════════════

---

## DRIVE DEPENDENCY TABLE

Note: This is a shared backbone file (task detection, ID reference table,
extraction protocol, marker protocol, pipeline sequencing) — it does not
itself read or publish module artifacts. Drive I/O for backend planning
is governed by PROJECT-3-BACKEND-ENGINE.md's table; for frontend
planning by PROJECT-3-FRONTEND-ENGINE.md's table; and for test artifacts
by PROJECT-TEST-GENERATION-ENGINE.md's table (v3.0).

---

*End of PROJECT-3-REGISTRY.md*
*Shared backbone for PROJECT-3-BACKEND-ENGINE.md (PASS 1, LIGHT),*
*PROJECT-3-FRONTEND-ENGINE.md (PASS 2, LIGHT), and (v3.0)*
*PROJECT-TEST-GENERATION-ENGINE.md (standalone test engine).*
*Amend mechanisms HERE only — no consuming file needs to change as a result.*
