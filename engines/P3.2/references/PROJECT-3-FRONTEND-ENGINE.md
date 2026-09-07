<!-- FACTORY NOTICE: this reference predates the git-native factory. Drive /
     ledger / connector steps in it are SUPERSEDED — see shared/FACTORY-PRECEDENCE.md
     (loaded first). Everything else (names, markers, gates, dependencies) applies. -->

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-PIPELINE-V5 — see GOVERNANCE-CONFIG.md §1D          -->
<!-- ══════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-PIPELINE-V5** (GOVERNANCE-CONFIG §1D — المصدر الواحد).
> هذا المحرك (P3.2 Frontend Execution Plan) ضمن **المسار الأساسي** (1D.1). يلتزم بـ:
> **أسماء الملفات المؤهَّلة بالموديول** (1D.2) · **بروتوكول الإنهاء الموحّد**
> (1D.4: artifact → registry inline → ledger → handoff) · **NEXT-ENGINE INPUT**
> (1D.5). تفاصيل هذا المحرك في القسم الختامي "COMPLETION PROTOCOL" أسفل الملف.
> 
<!-- ══════════════════════════════════════════════════════════════ -->

<!-- ════════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-IFA — Incremental Feature Addition                -->
<!-- ════════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-IFA (Incremental Feature Addition).**
> هذا المحرك (P3.2 — Frontend Execution Plan) يكتسب **وضع IFA (delta-only)** لإضافة ميزة إلى
> موديول **تم تنفيذه بالفعل** — يقرأ إصدار v1 كـ baseline، يُخرج الجديد/
> المعدَّل فقط، ويُبقي v1 مجمَّداً. التعديل الخاص بهذا الملف: **AMEND-P3-P**.
>
> حمِّل `AMEND-IFA-INCREMENTAL-FEATURE-ADDITION.md` بجانب هذا الملف في نفس
> المشروع. التفاصيل الكاملة (المفاهيم المشتركة C1–C5 + سلوك كل محرك) في
> ذلك الملف. عند تعارض ظاهري، AMEND-IFA يحكم نطاق الـ delta فقط ولا يغيّر
> سلوك المسار الكامل (New-Module) القائم.
<!-- ════════════════════════════════════════════════════════════════ -->

# ERP GOVERNANCE — PROJECT 3.2
# FRONTEND EXECUTION PLAN GOVERNANCE ENGINE
## Execution Truth Authority — Frontend Pass (PASS 2)

```
Project ID     : EXEC-GOV-ENGINE-FRONTEND-v2 (Project 3.2)
Responsibility : Frontend Execution Truth (light — no test generation)
Pipeline Stage : PASS 2 of Project 3 — see PROJECT-3-REGISTRY.md for
                 the full pipeline map (this file covers PASS 2 only)
Truth Layer    : Layer 3.2 — Frontend Execution Truth (CORE-1)
Canonical Owns : Component/routing structure decisions (F1/F4) —
                 informed by, but not owned by, Project 2.5's design intent
                 ALIGN-FE gate
                 (References FIELD-ID / ERR-ID / XM-ID — never reassigns)
Consumes       : real API Docs (post-implementation, from api-doc-generator)
                 + real UI Shell code (v2.1, from Claude Code — the
                   actual implemented components/routing, confirmed
                   against approved mockups at GATE: UI SHELL COMPLETE)
                 + flow-diagram-[MOD].md + ui-ux-spec-[MOD].md (Project 2.5, human-approved
                   — secondary reference once the real Shell exists)
                 + srs-[MOD].md (B1-B4)
Produces       : frontend-execution-plan-[MOD].md (PASS 2)
Companion files: PROJECT-3-REGISTRY.md        — shared protocol, ID map,
                                                 extraction rules, markers
                 PROJECT-3-BACKEND-ENGINE.md   — PASS 1, must be fully
                                                 implemented before this
                                                 pass may begin
                 PROJECT-TEST-GENERATION-ENGINE.md — standalone engine
                                                 (OUTSIDE the pipeline) that
                                                 consumes frontend-execution-plan-[MOD].md
                                                 and produces frontend-test-plan-[MOD].md
```

```
════════════════════════════════════════════════════════════════
v3.0 — P3 LIGHT (TEST GENERATION REMOVED FROM THIS ENGINE)
════════════════════════════════════════════════════════════════
As of v3.0, Project 3.2 is a LIGHT execution-plan engine. It no longer
generates any test artifact. Specifically REMOVED from this engine:

  ✗ Phase TEST-FE + the TC Coverage Matrix Summary (SECTION D)
  ✗ TEST-FE gate
  ✗ frontend-test-plan-[MOD].md generation (was SECTION 12)
  ✗ TC-FE-[MOD]-ID namespace ownership
  ✗ All ALIGN-FE checks that validated test coverage

Test generation now lives in a SEPARATE, STANDALONE project OUTSIDE the
governance pipeline: PROJECT-TEST-GENERATION-ENGINE.md. That engine
consumes this engine's frontend-execution-plan-[MOD].md (after ALIGN-FE ✓) and
produces frontend-test-plan-[MOD].md. Project 4.2 (Frontend Audit) no longer
reviews any test artifact (CHECK-4 removed).

This engine's job ends at frontend-execution-plan-[MOD].md + ALIGN-FE ✓.
════════════════════════════════════════════════════════════════
```

```
════════════════════════════════════════════════════════════════

---

# REFERENCE INGEST — governed UI Shell + API Docs (AMEND-PIPELINE-V5 §1F)

This engine no longer depends on the UI Shell manifest and API Docs being
re-attached every session. At Pre-Flight it INGESTS them once per module
version into the governed reference folders and reads them there afterward:

```
  UI Shell manifest → [MROOT]/_ref/ui-shell/ui-shell-manifest-[mod].md
  API Docs          → [MROOT]/_ref/api-docs/api-docs-[mod].md     ([MROOT] = [CTX]/[Module][/vN])

  first attach       → upload to the governed folder (create_file) + ledger row
  newer attach       → REPLACE IN PLACE (re-create same path, trash old,
                       supersede ledger row) — one live copy per version
  nothing attached   → read the governed copy (any session inherits it)
  new IFA version vN → fresh attach ingested into vN, else CARRY FORWARD from
                       vN-1; vN-1 stays frozen
```

So GATE: UI SHELL COMPLETE and the "real API Docs REQUIRED" precondition are
satisfied from the governed reference when no new file is attached — a
conversation opened later on the module already has them. Full rule: §1F.

v2.1 — WHAT CHANGED FROM v2.0 (UI SHELL STEP ADDED)
════════════════════════════════════════════════════════════════
v2.0 had F1/F4 DESIGN frontend structure fresh, informed by (but not
built from) Project 2.5's mockups. As of v2.1:

  ✓ A new step sits between UI/UX approval and this engine: Claude
    Code implements the UI Shell for real (components + routing +
    styling, matching approved mockups, no data binding yet).
  ✓ A second gate, GATE: UI SHELL COMPLETE, is checked alongside
    GATE: BACKEND MODULE COMPLETE (Section 2.0b) — both must pass.
  ✓ F1 (models) now CONFIRMS models already used in the real Shell
    against real API Docs, rather than designing them fresh.
  ✓ F4 (routing/components) now DOCUMENTS the real Shell's existing
    structure and adds only missing integration wiring, rather than
    designing routing/components fresh.
  ✓ Rationale: the same "real artifact beats planned artifact"
    principle CONTRACT-12 already applied to the backend API surface
    now applies to the frontend visual surface too — a mockup can
    drift once translated to code; a real, confirmed Shell cannot.

See CONTRACT-12 in shared-artifact-contracts.md for the full contract.
════════════════════════════════════════════════════════════════
```

```
════════════════════════════════════════════════════════════════
v2.0 — WHAT CHANGED FROM THE UNIFIED PROJECT 3
════════════════════════════════════════════════════════════════
This file used to be the second half of a single "Project 3" that
generated backend and frontend phases in one continuous pass,
gated internally on its own DOC-1 artifact. As of v2.0:

  ✓ This pass does NOT start automatically after PASS 1's ALIGN-BE ✓.
    It requires GATE: BACKEND MODULE COMPLETE (CONTRACT-12):
      - Backend fully implemented (the whole module, not partial)
      - Real API Docs generated from the live backend (api-doc-generator)
      - Project 2.5 outputs (flow-diagram, ui-ux-spec, mockups)
        human-approved
  ✓ This pass consumes REAL API Docs — never the PASS 1 internal
    DOC-1 artifact. A planned contract can drift during backend
    implementation; a real one cannot. See RULE-15 in
    shared-governance-rules.md.
  ✓ ALIGN gate renamed ALIGN-FE — validates frontend content only.
  ✓ Screen structure now also takes design intent from flow-diagram-[MOD].md
    / ui-ux-spec-[MOD].md (Project 2.5) — treated as strong intent, not a
    locked spec. srs-[MOD].md B1-B4 remains the functional ceiling.
  ✓ Shared mechanisms (extraction protocol, marker protocol,
    single-file output rule, task detection) live in
    PROJECT-3-REGISTRY.md — referenced here, not duplicated.

Every phase template (F1-F4) and every governance rule for those
phases is UNCHANGED from the prior version. This is a reorganization
plus one new precondition gate — not a rewrite.
════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# MANDATORY — SHARED GOVERNANCE CORE + PROJECT 3 REGISTRY
═══════════════════════════════════════════════════════════════════

## Project Instructions (permanent — load in this order)

```
┌────────────────────────────────────┬───────────────────────────────┐
│ FILE                               │ WHY                           │
├────────────────────────────────────┼───────────────────────────────┤
│ 1. shared-governance-core.md       │ Pipeline, truth layers,        │
│                                    │ ID namespace, vocabulary,      │
│                                    │ continuation protocol          │
├────────────────────────────────────┼───────────────────────────────┤
│ 2. shared-governance-rules.md      │ Operational rules, RULE-15     │
│                                    │ (real contracts only), no      │
│                                    │ workflow engine                │
├────────────────────────────────────┼───────────────────────────────┤
│ 3. shared-artifact-contracts.md    │ CONTRACT-11, 12 govern          │
│                                    │ this file specifically         │
├────────────────────────────────────┼───────────────────────────────┤
│ 4. platform-standards.md          │ Section M — ERP KB reference   │
├────────────────────────────────────┼───────────────────────────────┤
│ 5. PROJECT-3-REGISTRY.md          │ Shared P3 protocol: extraction, │
│                                    │ markers, output rule, task     │
│                                    │ detection, ID reference table  │
├────────────────────────────────────┼───────────────────────────────┤
│ 6. THIS FILE                       │ Frontend phase behavior/formats│
└────────────────────────────────────┴───────────────────────────────┘
```

## Session Uploads (per session — not instructions)

```
┌──────────────────────────────────┬─────────────────┬─────────────┐
│ FILE                             │ WHEN            │ EFFECT      │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ srs-[MOD].md                           │ Every session   │ REQUIRED    │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ Real API Docs (post-impl.)       │ Every session   │ REQUIRED    │
│                                  │                 │ (CONTRACT-12│
│                                  │                 │ precondition│
├──────────────────────────────────┼─────────────────┼─────────────┤
│ flow-diagram-[MOD].md (Project 2.5)     │ Every session   │ REQUIRED    │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ ui-ux-spec-[MOD].md (Project 2.5)       │ Every session   │ REQUIRED    │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ Real UI Shell code (v2.1)         │ Every session   │ REQUIRED    │
│ (from Claude Code — access to    │                 │ (CONTRACT-12│
│ the real frontend repo/components)│                 │ precondition│
├──────────────────────────────────┼─────────────────┼─────────────┤
│ backend-execution-plan-[MOD].md         │ Every session   │ RECOMMENDED │
│ (for ENTITY/RULE/FIELD/ERR lookup)│                 │ (reference  │
│                                  │                 │  only)      │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ master-registry.md               │ Every session   │ RECOMMENDED │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ frontend-execution-plan-[MOD].md (prior)│ Continuation    │ OPTIONAL    │
└──────────────────────────────────┴─────────────────┴─────────────┘

Note: this engine NEVER reads backend-execution-plan-[MOD].md as its API
source — real API Docs are the only acceptable source for endpoint
shape (CONTRACT-12, RULE-15). backend-execution-plan-[MOD].md may still be
attached for FIELD-ID/ERR-ID/XM-ID lookup convenience only.
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — AUTHORITY DECLARATION
═══════════════════════════════════════════════════════════════════

This engine treats **real API Docs, srs-[MOD].md, flow-diagram-[MOD].md, and
ui-ux-spec-[MOD].md as authoritative inputs**. It MUST NOT invent new
business meaning. It MUST NOT redefine SRS governance. It MUST NOT
treat flow-diagram-[MOD].md/ui-ux-spec-[MOD].md as overriding srs-[MOD].md B1-B4 — SRS
is the functional ceiling (CONTRACT-11 Resolution Authority Rule).

This engine synthesizes the real API surface, the SRS functional
ceiling, and the approved design intent into a **complete, agent-ready
frontend specification** that an implementation agent (Claude Code or
equivalent) can execute directly.

**Truth Layer reference:** see SHARED-GOVERNANCE-CORE.md CORE-1.
This engine generates Layer 3.2 — Frontend Execution Truth.
When conflict exists between frontend-execution-plan-[MOD].md and srs-[MOD].md,
srs-[MOD].md governs — this engine raises a Finding, never resolves silently.

**Agent Execution Model:**
The frontend-execution-plan-[MOD].md produced by this engine is the SOLE
frontend input to the implementation agent. The agent reads the plan
and writes all frontend code independently. This engine does NOT write
code.

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — PASS 2 — PRECONDITION + ENTRY GATE
═══════════════════════════════════════════════════════════════════

## 2.0 GATE: BACKEND MODULE COMPLETE (CONTRACT-12 — mandatory, checked FIRST)

This gate is evaluated BEFORE the normal entry gate below. If it fails,
this engine does not proceed to Section 2.1 at all.

```
╔══════════════════════════════════════════════════════════════════╗
║        GATE: BACKEND MODULE COMPLETE (must PASS before PASS 2)   ║
╠════════════════════════════════╦═════════════════════════════════╣
║ Backend 100% implemented       ║ [Yes / No — STOP, cannot proceed]║
║ (whole module, no partial)     ║                                  ║
║ Real API Docs attached          ║ [Yes / No — STOP]                ║
║ (from api-doc-generator)        ║                                  ║
║ flow-diagram-[MOD].md attached        ║ [Yes / No — STOP]                ║
║ (Project 2.5, human-approved)  ║                                  ║
║ ui-ux-spec-[MOD].md attached          ║ [Yes / No — STOP]                ║
║ (Project 2.5, human-approved)  ║                                  ║
╠══════════════════════════════════════════════════════════════════╣
║ SWAGGER ↔ SRS RECONCILIATION (runs once here):                    ║
║ Every API-ID in srs-[MOD].md B5 has a matching real endpoint?           ║
║   → No match: raise DRV-ID (naming) or OQ (missing/renamed core   ║
║     operation) — does not silently block minor naming diffs      ║
║ Every real endpoint has a corresponding API-ID in srs-[MOD].md?         ║
║   → No: raise OQ — proceed around it, never silently absorbed     ║
╠══════════════════════════════════════════════════════════════════╣
║ GATE RESULT: [PASSED ✓ — proceed to 2.1 / FAILED ✗ — STOP, state ║
║ exactly which precondition is missing]                            ║
╚══════════════════════════════════════════════════════════════════╝
```

**If this gate fails:** do not generate any frontend-execution-plan-[MOD].md
content. State plainly which precondition is missing and wait. This is
one of the two most important gates in this engine — it exists specifically
to prevent frontend work being built against a contract that changed
during backend implementation (see CONTRACT-12).

## 2.0b GATE: UI SHELL COMPLETE (NEW, v2.1 — CONTRACT-12 — mandatory, checked SECOND)

This gate is evaluated immediately after 2.0, still BEFORE the normal
entry gate. Both 2.0 AND 2.0b must pass before proceeding to 2.1.

```
╔══════════════════════════════════════════════════════════════════╗
║        GATE: UI SHELL COMPLETE (must PASS before PASS 2)         ║
╠════════════════════════════════╦═════════════════════════════════╣
║ UI Shell implemented           ║ [Yes / No — STOP, cannot proceed]║
║ (Claude Code, real React       ║                                  ║
║ components + routing +         ║                                  ║
║ styling — no data binding yet) ║                                  ║
║ Visual fidelity to approved    ║ [Yes / No — STOP]                ║
║ mockups confirmed by human     ║                                  ║
║ review (separate sign-off from ║                                  ║
║ the mockup approval itself)    ║                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**If this gate fails:** do not generate any frontend-execution-plan-[MOD].md
content, even if GATE: BACKEND MODULE COMPLETE already passed. State
plainly that the UI Shell is not yet implemented/confirmed and wait.

**Why this gate exists (v2.1):** F1 (models) and F4 (routing/
components) used to be DESIGNED by this engine from mockups alone.
Under v2.1, the actual UI Shell is built first, in real code, by
Claude Code — and F1/F4 CONFIRM and INTEGRATE with that real Shell
instead of designing a second, independent version of it on paper.
Without this gate, P3.2 could run before the Shell exists, defeating
the entire purpose of the change (see CONTRACT-12).

## 2.1 PASS 2 Entry Gate (after BOTH GATE: BACKEND MODULE COMPLETE and GATE: UI SHELL COMPLETE pass)

```
╔══════════════════════════════════════════════════════════════════╗
║                  PASS 2 (FRONTEND) — ENTRY GATE                  ║
╠════════════════════════════════╦═════════════════════════════════╣
║ SRS attached + feature code?   ║ [Yes / No — STOP]               ║
║ Real API Docs attached          ║ [Yes / No — STOP]                ║
║ flow-diagram-[MOD].md + ui-ux-spec-[MOD].md ║ [Yes / No — STOP]                ║
║ Real UI Shell code accessible   ║ [Yes / No — STOP]                ║
║ (v2.1 — the actual components/ ║                                  ║
║ routing Claude Code built)      ║                                  ║
║ Registry loaded, no conflicts? ║ [✓ / ✗ — conflicts listed]      ║
╠══════════════════════════════════════════════════════════════════╣
║ Extracted: [N] screens (SCR-IDs), [N] real endpoints, [N] LOVs,   ║
║ [N] open OQs                                                       ║
╠══════════════════════════════════════════════════════════════════╣
║ PROCEED? (Yes / Modify)                                           ║
╚══════════════════════════════════════════════════════════════════╝
```

## 2.2 Gate Conditions — Frontend Phases (Auto-Evaluated)

```
╔══════════════╦══════════════════════════════════════════════════════════════════╗
║ Gate         ║ Condition for PASSED ✓                                           ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ F1 ✓         ║ GATE: BACKEND MODULE COMPLETE + GATE: UI SHELL COMPLETE          ║
║              ║ both confirmed before start. Models used in the real UI Shell    ║
║              ║ CONFIRMED against REAL API Docs + DTO shapes (mismatches         ║
║              ║ corrected, no new models invented beyond what the Shell needs), ║
║              ║ screens separated per SCR-IDs, LOV types all string,            ║
║              ║ DEFERRED fields marked, Business Code readonly                   ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ F2 ✓         ║ All API-IDs have service method specifications (matching        ║
║              ║ real endpoints), all LOV-IDs have loading method specs,          ║
║              ║ loading/caching decisions justified                              ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ F3 ✓         ║ All RULE-IDs have validator specifications aligned with ERR-IDs, ║
║              ║ Arabic + English messages covered,                              ║
║              ║ no hardcoded values, no frontend-only validations               ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ F4 ✓         ║ All SCR-IDs have F4-SCREEN blocks DOCUMENTING the real Shell's   ║
║              ║ existing routes/components (not redesigning them); any missing  ║
║              ║ guard/integration wiring added as a flagged addition; all routes ║
║              ║ carry guards,                                                    ║
║              ║ tree-bearing entities have TreeComponent + correct route order,  ║
║              ║ no PERM_* invented outside the Permissions Matrix,              ║
║              ║ no "Page"/"Container" component suffixes                        ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ SEC-FE ✓     ║ All SCR-IDs have route guard specs + permission-based UI        ║
║              ║ behavior specs, EXCEPTION module interfaces respected           ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ ALIGN-FE ✓   ║ No ✗ in any frontend alignment table, all ⏸ documented,        ║
║              ║ derivation log complete, OQ Log reviewed                        ║
╚══════════════╩══════════════════════════════════════════════════════════════════╝
```

**v3.0 note — no TEST-FE gate:** test coverage is no longer produced or
gated here. After ALIGN-FE ✓, frontend-execution-plan-[MOD].md is handed to
the standalone Test Generation Engine (outside the pipeline), which
produces frontend-test-plan-[MOD].md.

## 2.3 Artifact Continuity Behavior

If the user uploads prior artifacts at session start, this engine MUST:

1. Read all uploaded artifacts first
2. Reconstruct: plan structure
3. Identify: last governed plan checkpoint and next safe action
4. Confirm: "Continuing [module] PASS 2 from [checkpoint]. Next action: [action]. Proceed?"
5. Continue from latest safe point WITHOUT requiring repeated context

---

═══════════════════════════════════════════════════════════════════
# SECTION 8 — FRONTEND PHASE EXECUTION SPECIFICATIONS
═══════════════════════════════════════════════════════════════════

## 8.0 — MARKER & THRESHOLD APPLICATION (READ BEFORE WRITING ANY PHASE)

**AMEND-P3-M.** Every phase below is generated ALREADY WRAPPED — not
wrapped afterward as a separate pass. Before writing phase [X]'s
content, look it up here:

```
╔══════════════╦══════════════╦═══════════════════════╦═══════════════════╗
║ Phase (name) ║ Marker KEY   ║ Threshold (SUB split)  ║ Atomic markers     ║
╠══════════════╬══════════════╬═══════════════════════╬═══════════════════╣
║ F1           ║ F1           ║ screens ≥ 5            ║ none               ║
║ F2           ║ F2           ║ screens ≥ 5            ║ none               ║
║ F3           ║ F3           ║ screens ≥ 5            ║ none               ║
║ F4           ║ F4           ║ screens ≥ 5            ║ none               ║
║ SEC-FE       ║ SEC-FE       ║ never splits           ║ none               ║
║ ALIGN-FE     ║ ALIGN-FE     ║ never splits           ║ none               ║
╚══════════════╩══════════════╩═══════════════════════╩═══════════════════╝
```

```
Note: unlike the backend pass, no frontend phase carries atomic
(API/XM/TC) markers — API-ID and XM-ID are backend-owned and only
referenced here, never re-marked. No TC markers appear in
frontend-execution-plan-[MOD].md at all (P3 light — this engine produces no
test artifact).

RULE: the very first line you write for a phase IS
  <!-- PHASE:{KEY}:START -->
and the very last line you write for it IS
  <!-- PHASE:{KEY}:END -->
There is no "write content, then mark it" step.

RULE: check the Threshold column WHILE writing the phase. If screen
count is already ≥ 5 from the SRS extraction, wrap the first SCR-ID
group in <!-- SUB:{KEY}-{SCR-ID}:START --> — e.g. <!-- SUB:F1-SCR-ORG-001:START -->
in this phase, <!-- SUB:F2-SCR-ORG-001:START --> in F2, and so on —
never the bare <!-- SUB:SCR-ORG-001:START --> alone. The SAME screen
is legitimately discussed under F1 (model/spec), F2 (data/facade
hooks), F3 (validation), and F4 (routing/components); without the
phase KEY prefix these four blocks would emit the identical marker_id
four times in one file, which Stage 5's global (kind, marker_id)
lookup rejects as a duplicate (AMEND-P3-N — see
PROJECT-3-REGISTRY.md Section 5.7.5). Never write the phase flat and
split later, and never drop the {KEY}- prefix.

RULE: any heading containing the literal word "PHASE" must use exactly
one of the six keys above. Agent Handoff Summary is NEVER a phase and
never gets a "# PHASE ..." heading or a <!-- PHASE:...--> marker (see
PROJECT-3-REGISTRY.md Section 5.3, "TRAILING CONTENT").

RULE: one atomic ID = one dedicated block, never grouped — see
PROJECT-3-REGISTRY.md Section 5.7.6 Rule 6.

Full protocol reference: PROJECT-3-REGISTRY.md Section 5.7.
```

---

## 8.1 Phase F1 — Frontend Model Specifications (v2.1 — CONFIRM, not design)

**Responsibility (v2.1 — REVISED):** CONFIRM that the TypeScript
interfaces and form models already used in the real UI Shell (built by
Claude Code, possibly against dummy/static data) match the real API
Docs' request/response DTO shapes. Correct any mismatch found. Do NOT
invent new models the Shell doesn't already need — if the Shell is
missing a model the API requires, flag it as a gap for the Shell to be
updated, rather than silently specifying it here as if it were new
design work.
Consumes: real API Docs (DTO shapes) + the real UI Shell's existing
models (primary reference, v2.1) + flow-diagram-[MOD].md/ui-ux-spec-[MOD].md
(secondary — original design intent, useful only if the Shell itself
is ambiguous) + srs-[MOD].md B1-B4 (functional ceiling).

Note: F1 specifies MODEL STRUCTURE — not TypeScript code. Under v2.1,
"specifies" means "documents and corrects what already exists," not
"designs from a blank page" — the agent already wrote the actual
TypeScript in the UI Shell step; this phase confirms it, in writing,
against the real API.

**GATE: BACKEND MODULE COMPLETE + GATE: UI SHELL COMPLETE both confirmed. Proceeding.**

**Entity Model Confirmation — one per ENTITY-ID (v2.1: confirm existing, not design new):**

```
### F1-MODEL — ENTITY-[MOD]-[ID] — [EntityName]
─────────────────────────────────────────────────────────────────
Model name       : [EntityName] (maps to DTO: [ResponseDTO name])
Source DTO       : [DTO Catalog reference]
Shell status     : [Already implemented in UI Shell / Missing from
                    Shell — flagged for Shell update]

Fields:
  [entityPk]     : number       — PK — system only, never displayed
  [entityCode]   : string       — Business Code — readonly — never in form input
  nameAr         : string       — Arabic name — mandatory
  nameEn         : string       — English name — mandatory
  [lovFieldName]Id: string      — LOV field — stores detail code — never ENUM
                                  LOV-ID: [LOV-ID] — lookupKey: [EXACT_KEY]
  isActiveFl     : boolean      — active/inactive flag — maps to IS_ACTIVE_FL column
                                  naming convention: flag fields end with Fl
                                  (EXCEPTION modules may use isActive — sourced from db-script)
  createdBy      : string       — audit field — set by AuditEntityListener
  createdAt      : Date         — audit field — set by AuditEntityListener
  updatedBy      : string       — audit field — set by AuditEntityListener
  updatedAt      : Date         — audit field — set by AuditEntityListener
  [additional fields per DBF-ID mapping from db-script-[MOD].md]

Readonly fields  : [entityCode], [entityPk], createdBy, createdAt
                   (these fields are never part of form input)
⚠ Agent: orgUnitId is NEVER in the TypeScript model
⚠ Audit field naming: createdAt/updatedAt — NOT createdDate/modifiedDate
DEFERRED fields  : [any fields blocked by DEFERRED XM-IDs — marked ⏸]

F1 Governance:
  ✓ Business Code field: readonly — never in form
  ✓ All LOV fields: String type (detail code) — never ENUM
  ✓ Both nameAr and nameEn always present
  ✓ PK field: number — never shown to user
  ✓ isActiveFl: boolean — standard naming — maps to IS_ACTIVE_FL column
  ✓ Audit fields: createdBy, createdAt, updatedBy, updatedAt (not createdDate/modifiedDate)
  ✗ NO orgUnitId in any TypeScript model
─────────────────────────────────────────────────────────────────
```

**Screen Model Specifications — one per SCR-ID:**

```
### F1-SCREEN — SCR-[MOD]-[ID] — [Screen Name]
─────────────────────────────────────────────────────────────────
Screen type      : [SEARCH | ENTRY | DETAIL | APPROVAL]
Entity           : ENTITY-[MOD]-[ID]

[If SEARCH screen:]
Search Filter Model — [EntityName]SearchFilter:
  Filter fields  :
    [fieldName]  : [type]  [OPTIONAL]  Filter type: [EXACT | LIKE | DATE_RANGE]
    [fieldName]  : [type]  [OPTIONAL]  Filter type: [EXACT | LIKE | DATE_RANGE]
  Pagination     : page (number), size (number)
  Sort           : sortBy (string), sortDir (ASC|DESC)

Result columns   : [field list — must match entity model fields]

[If ENTRY screen:]
Form Model — [EntityName]FormModel:
  Form fields    :
    [fieldName]  : [type]  [REQUIRED | OPTIONAL]
    nameAr       : string  REQUIRED
    nameEn       : string  REQUIRED
    [lovField]Id : string  REQUIRED — LOV-ID: [ID] — user selects from dropdown
  Excluded       : [entityPk], [entityCode] (system-managed)
  Read-only on EDIT: [any fields that become read-only after creation]

Create/Edit Container Pattern : [SIDE_DRAWER | FULL_PAGE | TREE_MASTER_DETAIL]
                                 — chosen per the decision order in
                                 "F1 — Create/Edit Container Pattern
                                 Decision" below. Never left blank for
                                 an ENTRY screen.
Shell status (pattern)         : [Shell already built with this
                                 pattern — confirmed match / Shell
                                 built with a DIFFERENT pattern —
                                 flagged for Shell correction /
                                 Pattern not yet reflected in Shell]
─────────────────────────────────────────────────────────────────
```

**F1 — Create/Edit Container Pattern Decision (AMEND-P3-O, mandatory
for every ENTRY screen, decided/confirmed here before F4 is written):**

Three container patterns for create/edit UI, chosen by content shape,
not by module or developer preference.

```
1. SIDE_DRAWER — default for simple entity forms
Use when: a single entity with a bounded field count and no repeating
child rows (name, code, a few selects/toggles, a description, an
active switch).
  - One consistent slide-in panel behavior across every simple CRUD screen.
  - A record-picker or matrix that grows past a handful of rows gets
    its own separate Drawer, launched from a button in this one —
    don't let it inflate the main entity Drawer.

2. FULL_PAGE — for document-style entities
Use when: the entity has a header section plus one or more repeating
line-item tables (add row / remove row) and a computed total —
invoices, purchase orders, sales orders, anything with a grid of lines.
  - A Drawer/Dialog can't fit an editable line-items grid without
    becoming a scroll-within-a-scroll problem — don't try.
  - Inside that full page, a supporting Drawer/Dialog is still the
    right tool for a secondary, bounded lookup (e.g. an advanced
    product search opened from a line-item field) — it's a helper
    tool, not the primary edit surface.

3. TREE_MASTER_DETAIL — for hierarchical data (custom, not a Drawer/Dialog at all)
Use when: the data is genuinely parent-child/hierarchical (org charts,
cost-center trees, category trees).
  - Inline two-column layout: tree on one side, the selected node's
    form permanently visible on the other side.
  - Beats any overlay because the user needs the tree's context
    visible while editing — don't convert this to a Drawer for the
    sake of consistency; the difference here is content-driven, not
    an oversight.

Decision order (apply in this order — stop at the first match):
  1. Hierarchical parent-child data           → TREE_MASTER_DETAIL
  2. Repeating line items + a computed total  → FULL_PAGE
  3. Otherwise                                → SIDE_DRAWER

If a screen doesn't cleanly fit one of the three, that's a signal to
look again at what it actually contains before picking — not to
invent a fourth container.
```

**How this interacts with CORE-9 (does NOT relax it):** all three
patterns satisfy CORE-9's actual requirement — one SCR-ID, one
React.lazy chunk per Composite Screen, Search↔Entry linkage via route
params. FULL_PAGE reaches Entry via a distinct route inside the same
chunk. SIDE_DRAWER and TREE_MASTER_DETAIL reach Entry via a route
param on the SAME route as Search (e.g. `?editId=123` or `/:nodeId`)
that toggles the Drawer/detail-panel open — still "internal routing
only," never a second lazy-loaded chunk, never bypassing the
Search-page's own permission gate. See F4-RULE-5 (revised) for the
routing consequence of each pattern.

---

## 8.8 Phase F2 — Frontend Data & Facade Hook Specifications

**Responsibility:** Specify what each screen needs from the backend:
which API calls, which LOV loads, what state the screen owns,
and how errors route to the user.

F2 has three sub-specifications per screen:
  F2-QUERY        — one block per API-ID: the TanStack Query hook contract
  F2-LOV-QUERY    — one block per LOV-ID: the lookup load the screen needs
  F2-SCREEN-INIT  — one block per SCR-ID: screen startup sequence and state

Note: F2 specifies WHAT the screen needs — not the exact hook
implementation code. The agent writes the actual `useQuery`/`useMutation`
calls and Facade Hook from these specifications.

```
⚠ SUPERSEDES AMEND-P3-C:
  The F2-QUERY block format in this section (Section 8.8) is the
  current governing specification for frontend data-fetching contracts.
  AMEND-P3-C in GOVERNANCE-STABILIZATION-AMENDMENTS.md is superseded
  by this section. P4 must reference Section 8.8 — not AMEND-P3-C.
```

**FRONTEND CONTRACTS (what the plan declares — agent implements):**
```
State ownership:
  currentPage and pageSize — derived from the query key's filter object
  (not independent useState) — TanStack Query re-fetches automatically
  when the query key changes, so pagination lives IN the query key,
  never as separate component state that must be manually kept in sync
  ✗ Never declare currentPage or pageSize as standalone independent state

Error routing per HTTP status (surfaced via each hook's `onError` /
the shared Axios/fetch error interceptor — declare which mechanism
this project uses once, in CORE phase, and reference it here):
  HTTP 400 (field validation) → displayed inline under the triggering
    field (via React Hook Form's `setError`, see F3)
  HTTP 409/422 (business rule) → routed through the shared error mapper
    → user toast
  HTTP 401 → redirect to login
  HTTP 403 → redirect to unauthorized
  HTTP 500 → generic message only — no technical detail shown

Pre-deactivation check:
  Before any deactivate/delete: backend usage check must be declared
  If blocked → reason shown to user — no confirmation dialog opened
  If allowed → confirmation dialog → proceed
```

**F2-QUERY — one per API-ID:**

```
### F2-QUERY — API-[MOD]-[ID] — [Operation Name]
─────────────────────────────────────────────────────────────────
API-ID           : [API-[MOD]-[ID]]
HTTP method      : [GET | POST | PUT | PATCH | DELETE]
Endpoint path    : [matches DOC contract / real API Docs exactly]
Request shape    : [DTO name | void | filter params]
Response shape   : [ResponseDTO | Page<ResponseDTO> | void]
Hook type        : [useQuery — for GET | useMutation — for POST/PUT/
                    PATCH/DELETE]
Query key        : [ [ '[entity-plural-kebab]', filters ] — GET only;
                    include every filter param that affects the
                    response, so cache invalidation is correct ]

Errors this call can produce:
  [ERR-ID] → HTTP [4xx] → business error → user toast via error mapper
  HTTP 400  → field validation → inline display under triggering field
  HTTP 401  → redirect to login
  HTTP 403  → redirect to unauthorized
  HTTP 500  → generic message only

Loading behavior : [NONE | LOCAL | GLOBAL]
  Maps to the hook's own `isLoading`/`isFetching` — LOCAL means the
  calling component reads it directly; GLOBAL means it also feeds a
  shared loading indicator (declare the mechanism once in CORE phase)
  GLOBAL only if: SRS indicates this call takes > 500ms
  Any non-default requires DRV-ID in Derivation Log

Caching (TanStack Query options) : [staleTime, gcTime — state exact
  values, or "defaults" if no deviation from the project-wide default
  declared in CORE phase]
  Non-default staleTime/gcTime only if: SRS describes stable reference
  data rarely mutated
  Any caching deviation requires DRV-ID in Derivation Log

Invalidation      : [which query keys this mutation invalidates on
  success, e.g. `['[entity-plural-kebab]']` — mutations that change
  data MUST declare what they invalidate; a mutation with no
  invalidation entry is a gap, not an assumed no-op]

XM-ID impact     : [XM-[MOD]-[N] — DEFERRED — behavior: [describe] / None]
─────────────────────────────────────────────────────────────────
```

**LOV Query Hook — one per LOV-ID:**

```
### F2-LOV-QUERY — LOV-[MOD]-[ID] — [Exact LOV name from SRS]
─────────────────────────────────────────────────────────────────
LOV-ID           : LOV-[MOD]-[ID]
LOOKUP_CODE      : [from Section 2A.1 extraction table]
                   ⚠ LOOKUP_CODE governance: Section 2A.1 is the canonical source
Hook name        : use[ExactLovName]Options()
Endpoint         : GET /api/v1/sys/lookups/[EXACT_LOOKUP_CODE]
Query key        : [ ['lookups', '[EXACT_LOOKUP_CODE]'] ]
Returns          : list of lookup options — each option: { detailCode, nameAr, nameEn }
Used by field    : [field name from F1 model] in [EntityName]
DB Column        : [EXACT_COLUMN_NAME] DBF-[ID]  ← stores DETAIL_CODE
Caching          : staleTime: long (e.g. 10+ minutes) — stable reference data
Reuse rule       : ONE hook per LOOKUP_CODE — shared across all screens
                   using this LOV (same query key → TanStack Query
                   deduplicates automatically, no manual sharing needed)
─────────────────────────────────────────────────────────────────
```

**F2-SCREEN-INIT — one per SCR-ID:**

```
### F2-SCREEN-INIT — SCR-[MOD]-[ID] — [Exact screen name from SRS]
─────────────────────────────────────────────────────────────────
On screen mount, these hooks fire (TanStack Query fires automatically
on mount by default — this block declares WHICH hooks the screen
calls, not an imperative sequence to hand-code):
  1. Permission hook for SCR-[MOD]-[ID]
     Produces: canView, canCreate, canEdit, canDelete, canApprove
  2. LOV hooks needed by this screen:
     [LOV-ID: LOV-[MOD]-[N] — LOOKUP_CODE: [EXACT_CODE]]
     [list every LOV this screen uses]
  3. [If ENTRY screen, edit mode: entity-by-PK query, `enabled: !!id`]

Search screen state:
  currentPage — lives in the query key's filter object (see F2-QUERY
    "Query key"), never a separate useState
  pageSize    — same
─────────────────────────────────────────────────────────────────
```

**F2-FACADE-HOOK — one per SCR-ID:**

```
### F2-FACADE-HOOK — SCR-[MOD]-[ID] — [Screen Name]
─────────────────────────────────────────────────────────────────
Facade Hook name : use[ScreenName]Facade()
Composes         : [list the useQuery/useMutation hooks from F2-QUERY/
                    F2-LOV-QUERY this Facade Hook wraps]

STATE THIS FACADE HOOK OWNS OR EXPOSES:
  [entityList]        — from the search useQuery's `data` — not
                        duplicated into local state
  [selectedItem]       — local useState (null if none) — UI selection
                        only, not server data
  [isLoading]          — derived from the composed hooks' `isLoading`/
                        `isFetching` — not a separate manually-toggled flag
  [searchFilters]      — local useState (or URL search params — state
                        which this project uses, declare once in CORE)
                        — currentPage/pageSize live inside this object
  [lovName]Options     — one per LOV-ID used on this screen, from the
                        composed F2-LOV-QUERY hook's `data`

OPERATIONS EXPOSED TO COMPONENTS:
  [nothing — components call the exposed values/functions directly;
   there is no imperative "load[Entities]()" call to trigger a fetch,
   since TanStack Query fetches reactively when searchFilters change —
   list only genuinely imperative actions below, e.g.:]
  create[Entity](data)      → calls the create useMutation
  update[Entity](id, data)  → calls the update useMutation
  deactivate[Entity](id)    → checks usage first → calls the
                              deactivate useMutation
                              if blocked: surfaces reason — no
                              confirmation shown
                              if allowed: triggers confirmation → proceeds
  selectItem(item)          → updates [selectedItem] — no API call
  setSearchFilters(filters) → updates [searchFilters] — TanStack Query
                              refetches automatically via the query key

BOUNDARIES:
  ✓ Components call the Facade Hook only — no direct `useQuery`/
    `useMutation` calls inside a component
  ✓ The Facade Hook composes F2-QUERY/F2-LOV-QUERY hooks only — no
    direct `fetch`/`axios` calls inside a Facade Hook
  ✓ currentPage and pageSize live inside searchFilters (the query key)
    — never separate state
─────────────────────────────────────────────────────────────────
```

---

## 8.9 Phase F3 — Frontend Validation Rule Specifications

**Responsibility:** Specify validation behavior for every RULE-ID,
including error message handling and permission-based field behavior.

Note: F3 specifies VALIDATION RULES — not the exact Zod schema code.
The agent writes the actual Zod schema (used with React Hook Form via
`zodResolver`) from these specifications.

**Validation Rule Block — one per RULE-ID:**

```
### F3-VALIDATION — RULE-[MOD]-[ID] — [Exact rule name from SRS]
─────────────────────────────────────────────────────────────────
RULE SOURCE:
  Statement  : [exact "The system MUST..." from SRS — character-perfect]
  Message-AR : [exact Arabic from SRS — this is what the user sees]
  Message-EN : [exact English from SRS]
  Scope      : [CREATE | UPDATE | EDIT | ALL]

VALIDATION SPEC:
  Field            : [exact fieldName in the screen's form model — from F1 phase]
  DB Column        : [EXACT_COLUMN_NAME] DBF-[ID]  ← from DATA+DOM binding
  Validation type  : [REQUIRED | LENGTH(min,max) | PATTERN | BUSINESS_RULE |
                      LOV_VALID | UNIQUE_CHECK | DATE_RANGE]
  Zod primitive    : [e.g. z.string().min(1) | z.string().max(N) |
                      z.string().regex(...) | z.string().refine(...) for
                      BUSINESS_RULE/UNIQUE_CHECK — state the shape, agent
                      writes the exact schema]
  When evaluated   : [ON_CHANGE | ON_BLUR | ON_SUBMIT — maps to React
                      Hook Form's `mode`/`reValidateMode` config,
                      declared once per form in F3, not per field,
                      unless a field genuinely needs to deviate]
  ERR-ID           : ERR-[ID] — bound in Error Catalog
  Message shown    : messageAr when locale=AR, messageEn otherwise
                     Text sourced from Error Catalog — never hardcoded
                     Surfaced via React Hook Form's `formState.errors`
                     (or `setError` for server-side/async errors — see
                     UNIQUE_CHECK below)

[If LOV_VALID:]
  LOV-ID           : LOV-[MOD]-[ID]
  LOOKUP_CODE      : [from Section 2A.1 — canonical source]
  LOV hook         : use[ExactLovName]Options() ← exact hook from F2 phase
  Endpoint bound   : GET /api/v1/sys/lookups/[EXACT_LOOKUP_CODE]
  Valid condition  : submitted value must exist in the loaded options
  Error trigger    : value not found in runtime-loaded options —
                      implement as a Zod `.refine()` that checks
                      against the loaded options list, not a static enum

[If UNIQUE_CHECK:]
  API call         : API-[MOD]-[ID] — [operation name] — QR-[MOD]-[N]
  DB check         : [EXACT_TABLE_NAME].[EXACT_UNIQUE_COLUMN] — constraint [name from db-script]
  When             : on blur — not on every keystroke — implement via
                      React Hook Form's `setError`/`clearErrors` from an
                      async check triggered in the field's `onBlur`, not
                      inside the Zod schema itself (Zod's `.refine()` is
                      synchronous-first; an async uniqueness check
                      belongs in the form handler, not the schema)
  Edit exception   : current record's PK excluded from the uniqueness check

[If BUSINESS_RULE:]
  Logic            : [exact rule logic from SRS — not a paraphrase]
  Dependent fields : [exact field names this rule reads]
  DB reference     : [any DB constraint enforcing the same rule — from db-script-[MOD].md]
─────────────────────────────────────────────────────────────────
```

**F3 Business Code Rules:**
```
F3-BC-RULE-1 — Business Code field [exact field name]: read-only on all screens
               DB Column: [TABLE_PREFIX]_CODE — format: [MOD]-YYYY-NNNN
               Never part of user input — displayed only
F3-BC-RULE-2 — Business Code on create form: shown as read-only display, not an input field
F3-BC-RULE-3 — Business Code on edit form: value from GET response — shown, never editable
```

**F3 Localization Rules:**
```
F3-LOC-RULE-1 — No hardcoded message text — all keyed by ERR-ID → Error Catalog
F3-LOC-RULE-2 — nameAr (NAME_AR col) / nameEn (NAME_EN col): separate inputs, RTL/LTR aware
F3-LOC-RULE-3 — Locale detection: session preference → browser locale → default AR
```

**F3 Permission-Based Field Behavior:**
```
F3-SEC-RULE-1 — Field visibility and editability are governed by screen permissions
  Permission source : screen permissions loaded for SCR-[MOD]-[ID] on init
  canEdit = false   → all form fields become read-only (`disabled` prop,
                       or React Hook Form's `disabled` field config)
  canCreate = false → new record entry form is not accessible
  canApprove = false→ approve/reject actions are not shown
```

---

## 8.10 Phase F4 — Frontend Routing & Component Structure (v2.1 — DOCUMENT + INTEGRATE, not design fresh)

**Responsibility (v2.1 — REVISED):** DOCUMENT the React Router route
configuration, component structure, code-split boundaries, and file
paths that ALREADY EXIST in the real UI Shell (built by Claude Code,
confirmed against approved mockups at GATE: UI SHELL COMPLETE) — for
every SCR-ID in the plan. Where the Shell is missing an integration
concern it was never expected to have on its own (a route guard, a
permission check, a code-split boundary), F4 adds it as an explicit,
flagged addition — never as a silent redesign of structure the Shell
already has. F4 is the single governed source of truth the agent uses
for wiring the Shell to real functionality — not for inventing
routing/component decisions from scratch.

Note: F4 specifies STRUCTURE — not the exact route config or component
code. The agent already wrote the actual route definitions and
components in the UI Shell step; this phase documents that structure
and adds integration wiring on top of it.

**F4-SCREEN Block — one per SCR-ID (v2.1: Shell status column added):**

```
### F4-SCREEN — SCR-[MOD]-[ID] — [Exact screen name from SRS]
─────────────────────────────────────────────────────────────────
Shell status     : [Route/component already exists in UI Shell /
                    Missing — flagged as integration gap to add]
Route path       : /[module-plural-kebab]                 ← F4-RULE-1
                    /[module-plural-kebab]/new
                    /[module-plural-kebab]/:id
                    /[module-plural-kebab]/:id/edit
                    [/[module-plural-kebab]/tree]          ← only if tree-bearing (F4-RULE-1)
                    ⚠ /tree route MUST be declared BEFORE /:id/* routes
                      in the route config (ordering — see F4-RULE-1)

Route module     : code-split via `React.lazy()`             ← F4-RULE-2
Route file       : src/features/[module-kebab]/[module-kebab].routes.tsx
                    (exports the route objects for this module, consumed
                    by the app's top-level router config)

Route guard      : <ProtectedRoute requiredPermission="...">← F4-RULE-3
                    wrapping this route's element
                    [Already wired in Shell / Added here as integration gap]
PERM_* required  : PERM_[PAGE_CODE]_VIEW (list route + entry-view mode)
                   PERM_[PAGE_CODE]_CREATE (new route)
                   PERM_[PAGE_CODE]_UPDATE (edit route)
                   [PERM_* sourced from the pre-bound Permissions Matrix —
                    Section 2.1.1 extraction — same source SEC phase
                    documents; F4 does not wait on SEC to be generated]

Child routes     : [list — e.g. :id resolves EntryPage in VIEW mode,
                    :id/edit resolves EntryPage in EDIT mode]

COMPONENTS:                                                    ← F4-RULE-4, F4-RULE-5
  [ModuleName]SearchPage
    Path       : src/features/[module-kebab]/pages/[module-kebab]-search-page.tsx
    Route      : /[module-plural-kebab]
    Facade Hook: use[ModuleName]Facade()                       ← F4-RULE-6
  [ModuleName]EntryPage
    Path       : src/features/[module-kebab]/pages/[module-kebab]-entry-page.tsx
    Route      : /[module-plural-kebab]/new, /:id, /:id/edit
    Mode       : CREATE | EDIT | VIEW — resolved from `useParams()`/
                 the matched route shape — never from a prop passed by
                 a parent component                                ← F4-RULE-7
    Facade Hook: use[ModuleName]Facade()
  [ModuleName]TreePage                                        ← only if tree-bearing entity
    Path       : src/features/[module-kebab]/pages/[module-kebab]-tree-page.tsx
    Route      : /[module-plural-kebab]/tree
    Facade Hook: use[ModuleName]Facade()

Shared UI imports : [design-system components actually used — e.g.
                     Button, DataTable, FormField from the shared UI
                     library — list only what this screen imports]  ← F4-RULE-8
─────────────────────────────────────────────────────────────────
```

**F4 Governance Rules:**
```
F4-RULE-1 — Path slug derivation: lowercase, plural, kebab-case, no PK
            in the base path (e.g. /legal-entities, not /LegalEntity or
            /legal-entity/{id}s). Tree-bearing entities (self-referencing
            FK) declare a /tree child route, and it MUST be registered
            BEFORE any /:id/* route in the route config — React Router
            matches more specific static segments first when both could
            match, but relying on that implicitly is fragile; declare
            /tree explicitly earlier in the route array so match order
            is never ambiguous.
F4-RULE-2 — One code-split chunk per functional module, via
            `React.lazy(() => import('./[module-kebab].routes'))` at
            the top-level router — no route for a screen may live
            outside its module's lazy chunk. Wrap the lazy route's
            element in `<Suspense fallback={...}>` at the module's
            route boundary, not per-component.
F4-RULE-3 — Every route element is wrapped in `<ProtectedRoute
            requiredPermission="PERM_...">` — no route is ever left
            unguarded. PERM_* codes used in guards are never invented
            in F4: they are sourced from the pre-bound Permissions
            Matrix (Section 2.1.1 extraction) — the same source SEC
            phase documents.
F4-RULE-4 — Component naming convention, branched by this screen's
            Create/Edit Container Pattern (F1):
              FULL_PAGE           → [ModuleName]SearchPage /
                                     [ModuleName]EntryPage (route-level,
                                     "Page" suffix — each mounted at its
                                     own route)
              SIDE_DRAWER         → [ModuleName]SearchPage (route-level)
                                     + [ModuleName]FormDrawer
                                     (presentational, no "Page" suffix —
                                     it is never mounted at its own
                                     top-level route, per the existing
                                     "Page" suffix philosophy below)
              TREE_MASTER_DETAIL  → [ModuleName]TreePage (route-level,
                                     hosts both the tree and the
                                     permanently-visible detail form as
                                     one composite; no separate
                                     "EntryPage")
            (this "Page" suffix is intentional and idiomatic React
            practice — it distinguishes route-mounted components from
            the smaller, reusable presentational components they
            compose, which carry no mandated suffix)
F4-RULE-5 — Composite Screen separation (CORE-9): Search and Entry are
            ALWAYS separate components — never a single component
            switching view via a flag/conditional render. This holds
            for every Container Pattern. What differs is whether Entry
            is also a SEPARATE ROUTE:
              FULL_PAGE           → Entry IS a separate route
                                     (SearchPage and EntryPage are two
                                     distinct route entries)
              SIDE_DRAWER         → Entry is NOT a separate route — the
                                     FormDrawer is rendered by
                                     SearchPage itself, toggled by a
                                     route param (e.g. ?editId=123),
                                     never by local-only component
                                     state disconnected from the URL
              TREE_MASTER_DETAIL  → Entry is not a separate route
                                     either — the detail form is
                                     rendered by TreePage itself,
                                     toggled by a route param (e.g.
                                     /:nodeId)
            In every case CORE-9's actual invariant holds: one
            React.lazy chunk per Composite Screen, Search↔Entry linkage
            is route-param-based, never a second lazy-loaded chunk for
            the sub-screen.
F4-RULE-6 — Facade Hook binding: Page components never call
            `useQuery`/`useMutation` directly. All data access goes
            through the screen's Facade Hook (F2 phase) —
            Page component → Facade Hook → TanStack Query hooks.
F4-RULE-7 — Mode resolution (CREATE / EDIT / VIEW), branched by
            Container Pattern — always from `useParams()`/the matched
            route shape, never from a prop passed by a parent, for
            every pattern:
              FULL_PAGE           → resolved from EntryPage's own
                                     route (e.g. presence of an `:id`
                                     param, or an `/edit` path segment)
              SIDE_DRAWER         → resolved from a route param on
                                     SearchPage's OWN route (e.g.
                                     `?editId=123` = EDIT, `?new=true`
                                     = CREATE, param absent = Drawer
                                     closed) — the Drawer itself stays
                                     a controlled presentational
                                     component; it never owns routing
                                     logic itself
              TREE_MASTER_DETAIL  → resolved from the selected-node
                                     route param on TreePage's own
                                     route (e.g. `/:nodeId`; absence =
                                     no node selected, form hidden or
                                     shows a placeholder)
F4-RULE-8 — Shared UI import contract: every feature imports only the
            shared design-system components it actually renders — no
            blanket `import * from '@ui/components'` pattern.
```

**F4 Hallucination Resistance Rule:**
```
HR-8 — F4 Structure Constraint:
  The agent MUST NOT invent route paths, component names, file paths,
  or PERM_* codes during implementation. Every value used in generated
  React code must trace back to an F4-SCREEN block. If a value is
  needed and no F4-SCREEN block covers it, this is a plan gap — raise
  an OQ-ID, do not invent the value.
```

**F4 Gate Checklist (self-check before phase closes):**
```
[ ] Every SCR-ID in the plan has exactly one F4-SCREEN block
[ ] Every tree-bearing entity's F4-SCREEN block declares a TreePage
    and its /tree route is ordered before /:id/* routes
[ ] Every route element is wrapped in <ProtectedRoute> — none omitted
[ ] Every PERM_* referenced in F4 also appears in the SEC phase's
    Permissions Matrix for the same SCR-ID — no F4-only permission names
[ ] Every route-level component uses the Page suffix; no route element
    is a bare presentational component
[ ] Every ENTRY screen's Container Pattern (F1) is one of SIDE_DRAWER /
    FULL_PAGE / TREE_MASTER_DETAIL — never blank, never invented
    outside these three
[ ] Search and Entry are declared as separate components (CORE-9) for
    every Composite Screen, regardless of pattern
[ ] Component naming matches the declared pattern per F4-RULE-4 —
    e.g. a SIDE_DRAWER screen does NOT have a "...EntryPage" component,
    a FULL_PAGE screen does NOT have an unrouted "...FormDrawer" as its
    primary edit surface
[ ] For FULL_PAGE screens only: Entry has its own separate route
[ ] For SIDE_DRAWER / TREE_MASTER_DETAIL screens: Entry mode is
    resolved from a route param on the SAME route as Search/Tree — not
    from local-only state disconnected from the URL
[ ] Every EntryPage's / Drawer's / detail-panel's mode resolution
    source is useParams()/route match — never a prop
```

---


## 8.5 Phase SEC-FE — Frontend Security Specifications

**Responsibility:** Specify navigation guards and permission-based UI
behavior for every SCR-ID in the plan.

**v2.0 split note:** This phase used to be combined with backend
API-level enforcement in one "Phase SEC". That backend half now lives
in PROJECT-3-BACKEND-ENGINE.md as Phase SEC-BE. This file covers only
the frontend (UI behavior) half — it references the SAME PERMISSIONS
seed data SEC-BE declares, never redefining it.

```
### SEC-FE — SCR-[MOD]-[ID] — [Screen Name]
─────────────────────────────────────────────────────────────────
Screen guard     : navigation to this screen requires canView = true
                   canView = false → redirect to unauthorized

Permission-based UI behavior:
  canView   = false → blocked at navigation — unauthorized redirect
  canCreate = false → new/add entry point not shown
  canEdit   = false → all edit fields become read-only, save not available
  canDelete = false → delete/deactivate action not shown
  canApprove= false → approve/reject actions not shown

EXCEPTION module scope:
  [If screen references EXCEPTION entities: declare scope boundary here]
─────────────────────────────────────────────────────────────────

SEC-FE Governance Rules:
  SEC-IMPL-RULE-2 — All UI show/hide decisions reference permission flags
                    loaded at F2-SCREEN-INIT (Section 8.2)
  SEC-IMPL-RULE-3 — HTTP 403 responses: caught and shown as localized
                    message (routed per F2 error routing table)

Note: PERMISSIONS seed data (PERM_[PAGE_CODE]_VIEW/CREATE/UPDATE/DELETE)
is declared once, in PROJECT-3-BACKEND-ENGINE.md Phase SEC-BE. This
phase references those exact permission names — it never invents new
ones and never redeclares the seed data rows.
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 9 — ALIGN-FE GATE (FRONTEND INTERNAL SELF-CONSISTENCY — AUTO-RUNS)
═══════════════════════════════════════════════════════════════════

**ALIGN-FE validates the frontend execution plan against ITSELF and**
**against real API Docs + srs-[MOD].md B1-B4 (the functional ceiling).**
**External cross-artifact validation = Project 4.2 scope.**
**ALIGN-FE runs automatically after SEC-FE phase — no user trigger needed.**
**After ALIGN-FE ✓, frontend-execution-plan-[MOD].md is complete. Test artifacts**
**(frontend-test-plan-[MOD].md) are generated separately by the standalone Test**
**Generation Engine, OUTSIDE this engine and OUTSIDE the pipeline —**
**see PROJECT-TEST-GENERATION-ENGINE.md.**

```
## ALIGN-FE GATE — [Module] — PLAN-ID: [xxx]
═══════════════════════════════════════════════════════════════════════════

SCREEN STRUCTURE CHECKS                                    │ Status
───────────────────────────────────────────────────────────┼──────────────
All SCR-IDs from SRS appear in Screen Registry              │ [✓ / ✗ list]
Every SCR-ID has F1 model specification                     │ [✓ / ✗ list]
Every SCR-ID has F2 screen init specification                │ [✓ / ✗ list]
Every SCR-ID has F2 facade specification                     │ [✓ / ✗ list]
Every SCR-ID has SEC-FE block defined                        │ [✓ / ✗ list]
Every SCR-ID has F4-SCREEN block defined                     │ [✓ / ✗ list]
Composite Screen UX separation declared for all entities     │ [✓ / ✗ list]
  (Search view ≠ Entry view — same SCR-ID per CORE-9)         │
Every F1/F4 element traces to flow-diagram-[MOD].md / ui-ux-spec-[MOD].md│ [✓ / ✗ list]
  or to srs-[MOD].md B1-B4 directly — no untraceable UI decision   │
───────────────────────────────────────────────────────────┼──────────────
LOV / LOOKUP CHECKS                                         │ Status
───────────────────────────────────────────────────────────┼──────────────
All LOV-IDs from SRS appear in LOV Registry                 │ [✓ / ✗ list]
Every LOV-ID has F2 LOV service method specification        │ [✓ / ✗ list]
No F1 model uses ENUM for LOV fields (all string)           │ [✓ / ✗ list]
Every LOV F3 validator references runtime options           │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
BUSINESS CODE CHECKS (frontend half)                        │ Status
───────────────────────────────────────────────────────────┼──────────────
Every master entity has Business Code field in F1           │ [✓ / ✗ list]
Business Code fields are readonly in F1 specifications      │ [✓ / ✗ list]
Business Code shown as read-only display in F3 specs        │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
LOCALIZATION CHECKS (frontend half)                         │ Status
───────────────────────────────────────────────────────────┼──────────────
All F3 validators reference ERR-ID (no hardcoded messages)  │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
SECURITY CHECKS (frontend half)                             │ Status
───────────────────────────────────────────────────────────┼──────────────
Every SCR-ID has SEC-FE block                                │ [✓ / ✗ list]
Every PERM_* in F4 also appears in SEC-BE's Permissions      │ [✓ / ✗ list]
  Matrix for the same SCR-ID — no F4-only permission names   │
═══════════════════════════════════════════════════════════════════════════
ALIGN-FE GATE RESULT: [PASSED ✓ / FAILED ✗ — list all ✗ items]
Auto-correction applied: [list DRV-IDs for corrections made / None]
═══════════════════════════════════════════════════════════════════════════
```

**Table — Operations Coverage (UI/Route view):**
```
Operation │ API-ID  │ UI Action (SCR-ID)                    │ F4 Route          │ Status
──────────┼─────────┼────────────────────────────────────────┼───────────────────┼───────
Create    │ API-001 │ SCR-[MOD]-001 Add button (Entry view)  │ /[mod-plural]/new │ ✓
Search    │ API-002 │ SCR-[MOD]-001 Search btn (Search view) │ /[mod-plural]     │ ✓
```
Note: F4 Route is populated from the F4-SCREEN block for the same
SCR-ID. A row missing its F4 Route while other columns are populated
is a gap the ALIGN-FE gate must flag ✗.

---

═══════════════════════════════════════════════════════════════════
# SECTION 10 — GOVERNANCE BOUNDARY RULES
═══════════════════════════════════════════════════════════════════

**What this engine OWNS (canonical authority):**
- ALIGN-FE gate (frontend internal self-consistency)
- Component/routing structure decisions (F1/F4) — informed by, but
  not owned by, Project 2.5's design intent

**What this engine NO LONGER owns (v3.0 — moved to Test Generation Engine):**
- TC-FE-[MOD]-ID namespace → now owned by PROJECT-TEST-GENERATION-ENGINE.md
- frontend-test-plan-[MOD].md → now produced by PROJECT-TEST-GENERATION-ENGINE.md

**What this engine REFERENCES (read-only — authoritative sources):**
- srs-[MOD].md B1-B4 — functional ceiling, never overridden
- real API Docs — authoritative API shape (never backend-execution-plan-[MOD].md)
- flow-diagram-[MOD].md / ui-ux-spec-[MOD].md (Project 2.5) — strong design intent
- FIELD-ID, ERR-ID (Project 3.1) — reference only, never reassigned
- UXD-ID (Project 2.5, NEW v2.2) — reference only, never reassigned
- PERMISSIONS seed data (Project 3.1 SEC-BE) — reference only

CORRECTION (v2.2, found during ecosystem verification): XM-ID was
previously listed here as something this engine references. That was
a governance conflict — XM-ID is exclusively a Backend/Database-layer
concern (CORE-5 RULE-6) and this engine never touches it, referenced
or otherwise. Real API Docs abstract the database layer away entirely;
there is no legitimate path for a Frontend-side artifact to need
XM-ID. Removed.

**What this engine does NOT touch:**
- ENTITY-ID, RULE-ID, LOV-ID, SCR-ID (owned by Project 1)
- FIELD-ID, ERR-ID, XM-ID, PLAN-ID (owned by Project 3.1)
- TC-BE-ID, TC-FE-ID (owned by the Test Generation Engine)
- Finding IDs, audit verdicts (owned by Project 4.1 / 4.2)
- Any backend phase content (CORE, DATA+DOM, SVC+API, DOC, INT-C,
  INT-R, SEC-BE) — see PROJECT-3-BACKEND-ENGINE.md

**UXD-ID REFERENCE RULE (NEW, v2.2):**
  When documenting a screen in frontend-execution-plan-[MOD].md that displays
  data sourced from a different module's real API, Project 3.2
  references the corresponding UXD-[MOD]-[SEQ] (assigned upstream by
  Project 2.5 in ui-ux-spec-[MOD].md) by citing it — it NEVER assigns,
  reassigns, or redefines a UXD-ID. If a screen displays cross-module
  data with no corresponding UXD-ID found in ui-ux-spec-[MOD].md, this is a
  traceability gap — raise it as an OQ-ID rather than inventing one.

**What this engine does NOT produce:**
- Code of any kind (TypeScript, HTML, SCSS)
- Any test artifact (frontend-test-plan-[MOD].md, TC blocks) — those belong
  to PROJECT-TEST-GENERATION-ENGINE.md
- Any backend phase content
- A resolved PRD↔SRS conflict (that's Project 2.5's Reconciliation
  Gate — SRS always wins, this engine never re-litigates it)

---

═══════════════════════════════════════════════════════════════════
# SECTION 11 — AGENT HANDOFF SUMMARY (FRONTEND)
═══════════════════════════════════════════════════════════════════

## 11.1 What the Agent Receives

```
AGENT INPUT PACKAGE:
  ✓ frontend-execution-plan-[MOD].md — this file (complete frontend specification)
  ✓ srs-[MOD].md — functional requirements (read for clarification)
  ✓ real API Docs — actual endpoint shapes
  ✓ flow-diagram-[MOD].md + ui-ux-spec-[MOD].md — design intent reference
  ✓ OQ Log — open questions the agent must not resolve unilaterally
```

## 11.2 Agent Reading Order

```
1. Read PLAN HEADER — understand full scope
2. Read PHASE F1 — TypeScript models
3. Read PHASE F2 — Service contracts and Facade state
4. Read PHASE F3 — Validation rules
5. Read PHASE F4 — Routing configuration, component structure, file paths
6. Read PHASE SEC-FE — security and permission-based UI behavior
7. Cross-reference real API Docs for exact endpoint/DTO shapes

Note: test authoring is not driven from this plan. If tests are needed,
the Test Generation Engine (outside the pipeline) consumes this plan and
produces frontend-test-plan-[MOD].md separately.
```

## 11.3 Frontend Plan Completeness Self-Check (Before Closing)

```
FRONTEND PLAN CHECKS:
[ ] Every SCR-ID has F1 model spec
[ ] Every SCR-ID has F2-SCREEN-INIT spec
[ ] Every SCR-ID has F2-FACADE spec
[ ] Every API-ID has F2-SERVICE spec (matching a REAL endpoint)
[ ] Every LOV-ID has F2-LOV-SERVICE spec
[ ] Facade state: currentPage and pageSize declared as derived — not separate state
[ ] Error routing declared: 400→inline / 409→toast / 401→login / 403→unauth
[ ] Pre-deactivation usage check declared for every deactivate operation
[ ] Every F3 RULE-ID: references ERR-ID — no hardcoded message text
[ ] Every SCR-ID has F4-SCREEN block (route path, guards, components,
    file paths)
[ ] Every tree-bearing entity (self-referencing FK) has a
    TreeComponent declared in its F4-SCREEN block
[ ] /tree child routes declared BEFORE /:id/* routes in F4 block
    for all tree entities
[ ] All PERM_* codes in F4 blocks sourced from SEC-BE's Permissions
    Matrix — none invented in F4

CROSS-CUTTING CHECKS:
[ ] Derivation Log entries present for every non-obvious inference
[ ] ALIGN-FE gate passed ✓

STRUCTURAL SELF-CHECK (AMEND-P3-M, mandatory before declaring the plan complete):
[ ] Every phase intended has exactly one <!-- PHASE:{key}:START --> and
    one matching :END, and {key} is exactly one of the six canonical
    keys in Section 8.0 — no near-misses
[ ] No section or heading label repeats anywhere in this document
[ ] Trailing content (this Agent Handoff Summary, this Self-Check) sits
    after <!-- PHASE:ALIGN-FE:END -->, with a heading that does not
    contain the word "PHASE" and carries no marker of its own
[ ] Every SUB threshold in Section 8.0 was checked while writing that
    phase (F1/F2/F3/F4 at screens ≥ 5) — not retrofitted after the fact
[ ] Every SUB marker ID is written as {PHASE-KEY}-{SCR-ID}, never the
    bare SCR-ID: grep this document for every screen that appears in
    more than one of F1/F2/F3/F4 and confirm each phase's SUB marker
    for that screen carries its OWN phase prefix (SUB:F1-SCR-X vs
    SUB:F2-SCR-X vs SUB:F3-SCR-X vs SUB:F4-SCR-X) — a bare
    SUB:SCR-X repeated across phases is the single most common
    structural defect in this document type (AMEND-P3-N,
    PROJECT-3-REGISTRY.md Section 5.7.5)
If any item above fails, fix the plan now. Additionally run:
  python3 agent3_splitter.py --validate-markers --file frontend-execution-plan-[MOD].md
— see STAGE-2-GOVERNANCE-TOOLS.md Section 3A. Treat any non-zero exit /
reported structural error from that tool as blocking, on top of this
manual checklist — the two are complementary, not either/or.
```

---

## DRIVE DEPENDENCY TABLE

Inputs required (Step A):
  Real API Docs                 — (post-implementation artifact, generated by api-doc-generator from the live backend; not part of the [GOVERNANCE-ROOT] Drive tree unless separately mirrored by the team)
  ui-ux-spec-[MOD].md, flow-diagram-[MOD].md (human-approved) — [GOVERNANCE-ROOT]/[Platform]/[Module]/P2.5-UIUX/
  srs-[MOD].md                        — [GOVERNANCE-ROOT]/[Platform]/[Module]/P1-SRS/srs-[MOD].md

Never read (CONTRACT-12 / CORE-5 RULE-6):
  db-script-[MOD].md, backend-execution-plan-[MOD].md, XM-RESOLUTION-EVENT-PROTOCOL.md content — these stay exclusively Backend-side

Outputs published (Step C):
  frontend-execution-plan-[MOD].md    — [GOVERNANCE-ROOT]/[Platform]/[Module]/P3.2-Frontend-Exec/frontend-execution-plan-[MOD].md

Note: frontend-test-plan-[MOD].md is NO LONGER produced here. It is generated
by the standalone Test Generation Engine (PROJECT-TEST-GENERATION-ENGINE.md)
from frontend-execution-plan-[MOD].md, and published under
[GOVERNANCE-ROOT]/[Platform]/[Module]/TEST-GEN/.

---

*End of PROJECT-3-FRONTEND-ENGINE.md (v3.0 — PASS 2 of Project 3, LIGHT)*
*Frontend stack: React (TypeScript) + Vite + React Router + TanStack*
*Query + React Hook Form + Zod — see GOVERNANCE-CONFIG.md.*
*Canonical owner: ALIGN-FE Gate | F1/F4 structure decisions*
*No longer owns: TC-FE-[MOD]-ID | frontend-test-plan-[MOD].md*
*             (moved to PROJECT-TEST-GENERATION-ENGINE.md — outside pipeline)*
*References only: FIELD-ID, ERR-ID, XM-ID (Project 3.1) — never reassigns*
*Companion   : PROJECT-3-REGISTRY.md (shared protocol)*
*              PROJECT-3-BACKEND-ENGINE.md (PASS 1 — must be fully*
*              implemented + real API Docs generated before this pass*
*              may begin — GATE: BACKEND MODULE COMPLETE, CONTRACT-12)*
*              PROJECT-TEST-GENERATION-ENGINE.md (standalone test engine)*
*Phase lifecycle (this file): F1 → F2 → F3 → F4 → SEC-FE → ALIGN-FE*
*               (test artifacts generated separately by the Test*
*               Generation Engine)*


---

# COMPLETION PROTOCOL — P3.2 Frontend Execution Plan (AMEND-PIPELINE-V5 · GOVERNANCE-CONFIG §1D.4)

This section is MANDATORY at the end of every run of this engine. It is the
inline replacement for P-REG (retired) and P-ROUTER (demoted). Nothing here is
hardcoded: names come from §1D.2 / the tools' config.ARTIFACT_FILES.

```
STAGE KEY   : P3.2

1. ARTIFACT — emit, with the §1D.2 module-qualified names, then upload via the
   connector and capture {drive_file_id, drive_url} for each:
    frontend-execution-plan-{mod}.md

2. REGISTRY (inline — the former P-REG step, same session):
    registry-exec-fe-{mod}.md + project-registry update (ALIGN-FE, UXD resolution)
   Upload it too. Never create a separate registry session.

3. LEDGER — record the links using the LEDGER-WRITE PROCEDURE (§1D.8:
   upload → capture id/webViewLink → fetch journey json → append/START/END
   in memory → re-create the file → trash the old copy). Append one row per
   uploaded file to [LEDGER] =
   [CTX]/[Module]/journey-{mod}.json (schema §1D.3):
    { engine: "P3.2", stage, filename, artifact, drive_file_id,
       drive_url, recorded_at, status: "UPLOADED" }
   If this is the FIRST engine of this version → also write START (open the
   version section; IFA versions carry change_set = CS-ID).
   If this is the LAST engine run for this version → write END (close it).

4. HANDOFF — print the NEXT-ENGINE INPUT block (§1D.5), filled in:
    NEXT ENGINE : END OF CORE — optional next: P3.5 Test-Case Spec (1D.6) / P4 Audit (1D.7)
    Read        : both execution plans + registries
    Do          : TestSprite-ready TC specs (optional)
    Gate        : none — write END module <MOD> vN to the ledger (1D.3)
   The user pastes that block as the first message of the next project.
```


PATHS (rendered from config.DRIVE_LAYOUT — GOVERNANCE-CONFIG §1E; never edit by hand)
  [MROOT] = [CTX]/[Module]/          (v1)   or   [CTX]/[Module]/v[N]/   (IFA, N ≥ 2)
  WRITES TO (this engine is the ONLY writer of these folders):
    [MROOT]/P3.2-Frontend-Exec/   → frontend-execution-plan-[mod].md, registry-exec-fe-[mod].md
    [MROOT]/_ref/ui-shell/   → ui-shell-manifest-[mod].md
    [MROOT]/_ref/api-docs/   → api-docs-[mod].md
  READS FROM:
    [MROOT]/P0-Platform/   ← platform-summary.md, module-registry-[mod].md, business-policies-[mod].md
    [MROOT]/P1-SRS/   ← srs-[mod].md, registry-srs-[mod].md
    [MROOT]/P2.5-UIUX/   ← flow-diagram-[mod].md, ui-ux-spec-[mod].md
    [MROOT]/P3.1-Backend-Exec/   ← backend-execution-plan-[mod].md, registry-exec-be-[mod].md
    [MROOT]/_ref/ui-shell/   ← ui-shell-manifest-[mod].md
    [MROOT]/_ref/api-docs/   ← api-docs-[mod].md
    [CTX]/_platform/                        ← platform-summary.md
  LEDGER: [CTX]/[Module]/_journey/journey-[mod].json   (cross-version; §1D.8)
  LAW (§1E.1): never write a file at [CTX] root or [MROOT] root — folders only.
  SELF-HEAL (§1E.5, AUTOMATIC at Pre-Flight): an input not at its governed path
  is searched in the module subtree (V5 or legacy name), renamed + moved there
  via the connector, and reported under HEALED: in the handoff — no human step.
  A missing ledger is created (START v1) on first contact.
  The connector upload in step 1 targets the WRITES-TO folder above, nothing else.

MUST NOT: emit a retired un-qualified filename (srs.md, db-script.md,
backend-execution-plan.md, frontend-execution-plan.md …); skip the registry step; write to
[STATE]/_router; rely on P-ROUTER for the next hop.
