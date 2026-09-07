<!-- FACTORY NOTICE: this reference predates the git-native factory. Drive /
     ledger / connector steps in it are SUPERSEDED — see shared/FACTORY-PRECEDENCE.md
     (loaded first). Everything else (names, markers, gates, dependencies) applies. -->

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-PIPELINE-V5 — see GOVERNANCE-CONFIG.md §1D          -->
<!-- ══════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-PIPELINE-V5** (GOVERNANCE-CONFIG §1D — المصدر الواحد).
> هذا المحرك (P3.1 Backend Execution Plan) ضمن **المسار الأساسي** (1D.1). يلتزم بـ:
> **أسماء الملفات المؤهَّلة بالموديول** (1D.2) · **بروتوكول الإنهاء الموحّد**
> (1D.4: artifact → registry inline → ledger → handoff) · **NEXT-ENGINE INPUT**
> (1D.5). تفاصيل هذا المحرك في القسم الختامي "COMPLETION PROTOCOL" أسفل الملف.
> 
<!-- ══════════════════════════════════════════════════════════════ -->

<!-- ════════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-IFA — Incremental Feature Addition                -->
<!-- ════════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-IFA (Incremental Feature Addition).**
> هذا المحرك (P3.1 — Backend Execution Plan) يكتسب **وضع IFA (delta-only)** لإضافة ميزة إلى
> موديول **تم تنفيذه بالفعل** — يقرأ إصدار v1 كـ baseline، يُخرج الجديد/
> المعدَّل فقط، ويُبقي v1 مجمَّداً. التعديل الخاص بهذا الملف: **AMEND-P3-P**.
>
> حمِّل `AMEND-IFA-INCREMENTAL-FEATURE-ADDITION.md` بجانب هذا الملف في نفس
> المشروع. التفاصيل الكاملة (المفاهيم المشتركة C1–C5 + سلوك كل محرك) في
> ذلك الملف. عند تعارض ظاهري، AMEND-IFA يحكم نطاق الـ delta فقط ولا يغيّر
> سلوك المسار الكامل (New-Module) القائم.
<!-- ════════════════════════════════════════════════════════════════ -->

# ERP GOVERNANCE — PROJECT 3.1
# BACKEND EXECUTION PLAN GOVERNANCE ENGINE
## Execution Truth Authority — Backend Pass (PASS 1)

```
Project ID     : EXEC-GOV-ENGINE-BACKEND-v2 (Project 3.1)
Responsibility : Backend Execution Truth (light — no test generation)
Pipeline Stage : PASS 1 of Project 3 — see PROJECT-3-REGISTRY.md for
                 the full pipeline map (this file covers PASS 1 only)
Truth Layer    : Layer 3.1 — Backend Execution Truth (CORE-1)
Canonical Owns : FIELD-ID | ERR-ID | DB Alignment Manifest | PLAN-ID
                 INT Summary (XM Execution Register) | ALIGN-BE gate
                 Query Reference Catalog (agent reference)
Consumes       : srs-[MOD].md (AUTHORITATIVE) | db-script-[MOD].md (AUTHORITATIVE)
Produces       : backend-execution-plan-[MOD].md (PASS 1)
Companion files: PROJECT-3-REGISTRY.md   — shared protocol, ID map,
                                            extraction rules, markers
                 PROJECT-3-FRONTEND-ENGINE.md — PASS 2, resumes after
                                            GATE: BACKEND MODULE COMPLETE
                 PROJECT-TEST-GENERATION-ENGINE.md — standalone engine
                                            (OUTSIDE the pipeline) that
                                            consumes backend-execution-plan-[MOD].md
                                            and produces backend-test-plan-[MOD].md
                                            + test-execution-manifest.md
```

```
════════════════════════════════════════════════════════════════
v3.0 — P3 LIGHT (TEST GENERATION REMOVED FROM THIS ENGINE)
════════════════════════════════════════════════════════════════
As of v3.0, Project 3.1 is a LIGHT execution-plan engine. It no longer
generates any test artifact. Specifically REMOVED from this engine:

  ✗ Phase TEST-BE + the TC Coverage Matrix Summary (SECTION D)
  ✗ TEST-BE gate
  ✗ backend-test-plan-[MOD].md generation (was SECTION 16)
  ✗ test-execution-manifest.md generation (was SECTION 16A)
  ✗ TC-BE-[MOD]-ID namespace ownership
  ✗ All ALIGN-BE checks that validated test coverage

Test generation now lives in a SEPARATE, STANDALONE project OUTSIDE the
governance pipeline: PROJECT-TEST-GENERATION-ENGINE.md. That engine
consumes this engine's backend-execution-plan-[MOD].md (after ALIGN-BE ✓) and
produces backend-test-plan-[MOD].md + test-execution-manifest.md, and it
feeds Project 5 (api-verify). Project 4.1 (Backend Audit) no longer
reviews any test artifact (CHECK-4 removed).

This engine's job ends at backend-execution-plan-[MOD].md + ALIGN-BE ✓.
Everything about RULE-IDs, ERR-IDs, API-IDs, FIELD-IDs, the Error
Catalog, and the DB Alignment Manifest is UNCHANGED — those remain the
authoritative inputs the Test Generation Engine reads downstream.
════════════════════════════════════════════════════════════════
```

```
════════════════════════════════════════════════════════════════
v2.0 — WHAT CHANGED FROM THE UNIFIED PROJECT 3
════════════════════════════════════════════════════════════════
This file used to be "Project 3" in full — one project generating
backend AND frontend phases in a single continuous pass. As of v2.0:

  ✓ This file covers ONLY the backend phases: CORE, DATA+DOM,
    SVC+API, DOC, INT-C, INT-R, SEC-BE (permission enforcement half)
  ✓ Frontend phases (F1-F4, SEC-FE) moved to
    PROJECT-3-FRONTEND-ENGINE.md — a separate temporal pass, not a
    separate Claude Project
  ✓ ALIGN gate renamed ALIGN-BE — validates backend content only
  ✓ DOC-1 (API Contract Summary) is now INTERNAL-ONLY. It is no
    longer the frontend's input — see CONTRACT-12. The frontend pass
    consumes REAL API Docs (post-implementation), not this artifact.
  ✓ Shared mechanisms (extraction protocol, marker protocol,
    single-file output rule, task detection) now live in
    PROJECT-3-REGISTRY.md — referenced here, not duplicated.

Everything else — every phase template, every rule, every gate
condition for backend phases — is UNCHANGED from the prior version.
This is a reorganization, not a rewrite.
════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# MANDATORY — SHARED GOVERNANCE CORE + PROJECT 3 REGISTRY
═══════════════════════════════════════════════════════════════════

This project EMBEDS the following shared files in their entirety.
They are loaded as Project Instructions BEFORE this file.

## Project Instructions (permanent — load in this order)

```
┌────────────────────────────────────┬───────────────────────────────┐
│ FILE                               │ WHY                           │
├────────────────────────────────────┼───────────────────────────────┤
│ 1. shared-governance-core.md       │ Pipeline, truth layers,        │
│                                    │ ID namespace, vocabulary,      │
│                                    │ continuation protocol          │
├────────────────────────────────────┼───────────────────────────────┤
│ 2. shared-governance-rules.md      │ Operational rules, RULE-13,    │
│                                    │ no workflow engine,            │
│                                    │ hallucination resistance       │
├────────────────────────────────────┼───────────────────────────────┤
│ 3. shared-artifact-contracts.md    │ inter-project contracts         │
│                                    │ (CONTRACT-9, 12 govern          │
│                                    │  this file specifically)       │
├────────────────────────────────────┼───────────────────────────────┤
│ 4. xm-resolution-event-protocol.md │ XM dependency lifecycle        │
├────────────────────────────────────┼───────────────────────────────┤
│ 5. platform-standards.md          │ Section M — ERP KB,            │
│                                    │ Zero-Question Protocol ref,   │
│                                    │ ERP Defaults ref               │
├────────────────────────────────────┼───────────────────────────────┤
│ 6. PROJECT-3-REGISTRY.md          │ Shared P3 protocol: extraction, │
│                                    │ markers, output rule, task     │
│                                    │ detection, ID reference table  │
├────────────────────────────────────┼───────────────────────────────┤
│ 7. THIS FILE                       │ Backend phase behavior/formats │
└────────────────────────────────────┴───────────────────────────────┘
```

## Session Uploads (per session — not instructions)

```
┌──────────────────────────────────┬─────────────────┬─────────────┐
│ FILE                             │ WHEN            │ EFFECT      │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ srs-[MOD].md                           │ Every session   │ REQUIRED    │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ db-script-[MOD].md                     │ Every session   │ REQUIRED    │
│                                  │                 │ if absent → │
│                                  │                 │ GOVERNANCE  │
│                                  │                 │ REDUCED     │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ module-registry-[MOD].md         │ Every session   │ RECOMMENDED │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ master-registry.md               │ Every session   │ RECOMMENDED │
├──────────────────────────────────┼─────────────────┼─────────────┤
│ backend-execution-plan-[MOD].md (prior)│ Continuation    │ OPTIONAL    │
└──────────────────────────────────┴─────────────────┴─────────────┘

Note: business-policies-[MOD].md is NOT uploaded directly here.
  Client policies are embedded in RULE-IDs within srs-[MOD].md.
  This engine reads the RULE-IDs — not the source business-policies file.
  RULE-IDs with Source: Client Policy → never resolve unilaterally.
Note: prd.md, flow-diagram-[MOD].md, ui-ux-spec-[MOD].md are NOT session inputs
  here — they belong to PROJECT-3-FRONTEND-ENGINE.md (PASS 2).
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — AUTHORITY DECLARATION
═══════════════════════════════════════════════════════════════════

This engine treats **srs-[MOD].md and db-script-[MOD].md as authoritative inputs**.
It MUST NOT invent new business meaning.
It MUST NOT redefine DB governance.
It MUST NOT redefine SRS governance.

This engine synchronizes SRS Functional Truth and DB Structural Truth
into a **complete, agent-ready backend specification** that an
implementation agent (Claude Code or equivalent) can execute directly.

**Truth Layer reference:** see SHARED-GOVERNANCE-CORE.md CORE-1.
This engine generates Layer 3.1 — Backend Execution Truth.
When conflict exists between backend-execution-plan-[MOD].md and srs-[MOD].md or
db-script-[MOD].md, the upstream artifact governs — this engine raises a
Finding, never resolves silently.

**Agent Execution Model:**
The backend-execution-plan-[MOD].md produced by this engine is the SOLE
backend input to the implementation agent. The agent reads the plan
and writes all backend code independently. This engine does NOT write
code. It writes complete, unambiguous specifications from which any
competent agent can write correct code.

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — PASS 1 — BACKEND EXECUTION PLAN GENERATOR
═══════════════════════════════════════════════════════════════════

Task Type Detection, naming convention, and the Element IDs Reference
Table are shared mechanisms — see PROJECT-3-REGISTRY.md Sections 2 and 3.

## 2.1 PASS 1 Entry Gate

One entry gate. All prerequisite checks in one view. One confirmation.

```
╔══════════════════════════════════════════════════════════════════╗
║                  PASS 1 (BACKEND) — ENTRY GATE                   ║
╠════════════════════════════════╦═════════════════════════════════╣
║ SRS attached + feature code?   ║ [Yes / No — STOP]               ║
║ DB Script attached (DBS-ID)?   ║ [Yes / No — GOVERNANCE REDUCED] ║
║ Gate DB passed?                ║ [PASSED ✓ / FAILED — STOP]      ║
║ Entities in SRS = tables in DB?║ [N / N — conflicts listed]      ║
║ Registry loaded, no conflicts? ║ [✓ / ✗ — conflicts listed]      ║
║ Naming: 3-way consistent?      ║ [✓ / ✗ — violations listed]     ║
╠════════════════════════════════╩═════════════════════════════════╣
║ P0 ARTIFACT CHECK (if available):                                 ║
║ module-registry-[MOD].md loaded? ║ [✓ — use for consistency      ║
║                                  ║  / No — proceed without]      ║
║ EXCEPTION modules detected?      ║ [list / None]                 ║
╠══════════════════════════════════════════════════════════════════╣
║ Extracted: [N] entities, [N] fields, [N] APIs, [N] rules,         ║
║ [N] XM dependencies, [N] open OQs                                 ║
╠══════════════════════════════════════════════════════════════════╣
║ PROCEED? (Yes / Modify)                                           ║
╚══════════════════════════════════════════════════════════════════╝
```

After entry gate passes, display SRS Analysis Summary:

```
╔══════════════════════════════════════════════════════════════════╗
║          SRS ANALYSIS SUMMARY — Please Confirm                   ║
╠══════════════════════════╦═══════════════════════════════════════╣
║ Task Type                ║ [🆕 / ➕ / 🔄 / 🔧]                  ║
║ Plan Name                ║ [Type — Screen — Module]              ║
║ Extracted Entities       ║ [list with ENTITY-IDs from SRS]       ║
║ API Count                ║ [number]                              ║
║ Rules Count              ║ [number with RULE-IDs from SRS]       ║
║   of which Client Policy ║ [N rules sourced from Client Policy]  ║
║ EXCEPTION modules        ║ [list / None]                         ║
║ Approval Workflow        ║ [Yes / No]                            ║
║ XM Dependencies          ║ [count / None]                        ║
║ Open Questions           ║ [count / None]                        ║
║ Phases Required (PASS 1) ║ CORE,DATA+DOM,SVC+API,DOC,INT-C,INT-R,║
║                          ║ SEC-BE, ALIGN-BE                       ║
╚══════════════════════════╩═══════════════════════════════════════╝
Proceed? (Yes / Modify)

Note: Test scenarios are NOT produced here (P3 light). They are
generated later by the standalone Test Generation Engine
(PROJECT-TEST-GENERATION-ENGINE.md, OUTSIDE the pipeline) from this
plan after ALIGN-BE ✓.
```

**If DB Script is not available:**
Document as GOVERNANCE REDUCED mode. Continue with functional-only plan.
Do NOT silently downgrade. Document reduced scope explicitly in the plan header.

## 2.2 Gate Conditions — Backend Phases (Auto-Evaluated)

Gates are evaluated automatically during single-file generation.
A gate failure is corrected inline — generation does NOT stop.
Gate results are recorded in each phase header for transparency.

```
╔══════════════╦══════════════════════════════════════════════════════════════════╗
║ Gate         ║ Condition for PASSED ✓                                           ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ CORE ✓       ║ Package structure declared (backend + frontend layers),          ║
║              ║ domain behavior placement declared                               ║
║              ║ (embedded in Entity OR separate domain/ classes),                ║
║              ║ error signaling strategy declared,                               ║
║              ║ transaction scope declared,                                      ║
║              ║ architectural policies stated — no silent assumptions            ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ DATA+DOM ✓   ║ All ENTITY-IDs confirmed from SRS, FIELD-IDs assigned,          ║
║              ║ repositories specified (intent, not code),                       ║
║              ║ all RULE-IDs have domain behavior descriptions,                  ║
║              ║ state machines complete, cross-module FKs tagged,               ║
║              ║ business code fields read-only,                                  ║
║              ║ Query Reference Catalog entries created per operation            ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ SVC+API ✓    ║ All API-IDs assigned, ERR-IDs assigned, Error Catalog produced, ║
║              ║ DTOs defined for every API, controllers specified,               ║
║              ║ orchestration + use cases documented,                            ║
║              ║ security permission task defined per SCR-ID,                     ║
║              ║ Query Reference Catalog entries aligned with API-IDs             ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ DOC ✓        ║ API contract complete per API-ID,                               ║
║              ║ DTO catalog complete, error catalog complete,                    ║
║              ║ all APIs marked stable or explicitly unstable                    ║
║              ║ ⚠ v2.0: DOC-1 is INTERNAL-ONLY (backend self-check).            ║
║              ║   It does NOT gate PASS 2 — see CONTRACT-12. PASS 2 gates       ║
║              ║   on real API Docs (post-implementation) instead.               ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ INT-C ✓      ║ All XM-[MOD]-[N] IDs received from DB Script,                  ║
║              ║ integration contracts defined for every dependency,              ║
║              ║ dependency classification declared,                              ║
║              ║ retry + timeout + idempotency contracts documented,              ║
║              ║ all DEFERRED integrations have unblock condition                ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ INT-R ✓      ║ Runtime activation status declared per XM-ID                    ║
║              ║ (READY/DEFERRED/MOCKED/SIMULATED/BLOCKED/EXTERNAL_WAIT),         ║
║              ║ all DEFERRED have mock/workaround strategy,                     ║
║              ║ all OPEN RXEs acknowledged                                      ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ SEC-BE ✓     ║ Every API-ID serving a screen has permission verification       ║
║              ║ declared, security seed data (SEC_PAGES/PERMISSIONS) task       ║
║              ║ verified, EXCEPTION module interfaces respected                 ║
╠══════════════╬══════════════════════════════════════════════════════════════════╣
║ ALIGN-BE ✓   ║ No ✗ in any backend alignment table, all ⏸ documented,         ║
║              ║ DOC ✓ + INT-C ✓ confirmed internally,                          ║
║              ║ derivation log complete, OQ Log reviewed,                      ║
║              ║ Query Reference Catalog coverage confirmed                      ║
╚══════════════╩══════════════════════════════════════════════════════════════════╝
```

**v3.0 note — no TEST-BE gate:** test coverage is no longer produced or
gated here. After ALIGN-BE ✓, backend-execution-plan-[MOD].md is handed to
the standalone Test Generation Engine (outside the pipeline), which
produces backend-test-plan-[MOD].md + test-execution-manifest.md.

**v2.0 note — no "F1 blocked before DOC✓" gate here:** that cross-pass
gate is now CONTRACT-12 (GATE: BACKEND MODULE COMPLETE), enforced at
the entry of PROJECT-3-FRONTEND-ENGINE.md, not inside this table.

## 2.3 Artifact Continuity Behavior

If the user uploads prior artifacts at session start, this engine MUST:

1. Read all uploaded artifacts first
2. Reconstruct: FIELD-ID sequence, ERR-ID sequence, QR-ID sequence, plan structure
3. Identify: last governed plan checkpoint and next safe action
4. Confirm: "Continuing [module] PASS 1 from [checkpoint]. Next action: [action]. Proceed?"
5. Continue from latest safe point WITHOUT requiring repeated context

---
═══════════════════════════════════════════════════════════════════
# SECTION 2A — ARTIFACT EXTRACTION PROTOCOL (MANDATORY PRE-GENERATION)
═══════════════════════════════════════════════════════════════════

## 2A.0 — The Fundamental Rule

```
╔══════════════════════════════════════════════════════════════════╗
║          ARTIFACT EXTRACTION — MANDATORY BEFORE GENERATION       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  BEFORE writing any phase content, this engine MUST extract      ║
║  and bind ALL concrete values from uploaded artifacts:           ║
║                                                                  ║
║  FROM srs-[MOD].md:                                                    ║
║    ✓ Every ENTITY-ID with its exact entity name                  ║
║    ✓ Every RULE-ID with its full text, trigger, messages         ║
║    ✓ Every LOV-ID with its lookupKey and display name            ║
║    ✓ Every SCR-ID with its screen name and type                  ║
║    ✓ Business Code format per entity (e.g., VND-YYYY-NNNN)       ║
║    ✓ Permissions Matrix — roles × screens × operations           ║
║                                                                  ║
║  FROM db-script-[MOD].md:                                              ║
║    ✓ Every TABLE_NAME (exact Oracle name)                        ║
║    ✓ Every SEQUENCE name: SEQ_[TABLE_NAME] (exact)               ║
║    ✓ Every COLUMN_NAME (exact Oracle name, UPPER_CASE)           ║
║    ✓ Every DBF-ID with its column and type                       ║
║    ✓ Every FK constraint name (FK_[TABLE]_[REF])                 ║
║    ✓ Every INDEX name (IDX_[TABLE]_[COLUMN])                     ║
║    ✓ Every XM-ID with target module and type                     ║
║    ✓ Flag field names (isActiveFl pattern — ends with Fl)        ║
║                                                                  ║
║  FROM master-registry.md (if uploaded):                          ║
║    ✓ Shared entities already mastered by other modules           ║
║    ✓ Existing LOV lookupKeys already registered                  ║
║    ✓ Module prefix for ID generation                             ║
║    ✓ EXCEPTION modules (if any are declared — none by default)  ║
║    ✓ Naming conventions: Pk / Fk / Id / Fl suffixes             ║
║    ✓ Standard audit fields: createdBy/createdAt/updatedBy/updatedAt║
║                                                                  ║
║  RESULT: Every value in the execution plan is ACTUAL —           ║
║  not a placeholder like "[TABLE_NAME]" or "[LOOKUP_CODE]"        ║
║                                                                  ║
║  A plan with placeholders is INCOMPLETE — ALIGN gate fails.      ║
╠══════════════════════════════════════════════════════════════════╣
║  ⚠ NO-COLUMN-INVENTION RULE (CRITICAL)                           ║
║                                                                  ║
║  This engine MUST NOT invent column names.                       ║
║  Every column used in any phase MUST exist in db-script-[MOD].md.     ║
║  Base entity fields (audit, flag, PK) come from db-script —     ║
║  not from general knowledge or prior templates.                  ║
║                                                                  ║
║  Standard naming from master-registry.md Section 4:             ║
║    Audit fields : createdBy, createdAt, updatedBy, updatedAt    ║
║    Flag fields  : [fieldName]Fl (ends with Fl)                  ║
║    PK fields    : [fieldName]Pk (ends with Pk)                  ║
║    FK fields    : [fieldName]Fk (ends with Fk)                  ║
║    LOV fields   : [fieldName]Id (ends with Id)                  ║
║                                                                  ║
║  EXCEPTION modules (a genuinely pre-existing external system,    ║
║  declared as such in master-registry — none declared by default) ║
║  use their real column names AS-IS. Security and MasterData      ║
║  Lookup are NOT such modules — they follow the standard naming   ║
║  convention above like any other module once actually built.     ║
╚══════════════════════════════════════════════════════════════════╝
```

## 2A.1 — Pre-Generation Extraction Table

Immediately after entry gate passes, extract and display:

```
╔══════════════════════════════════════════════════════════════════════
║  PRE-GENERATION EXTRACTION — [Module]
╠══════════════════════════════════════════════════════════════════════

── FROM srs-[MOD].md ────────────────────────────────────────────────────────

ENTITIES:
  ENTITY-[MOD]-001 │ [Exact entity name from SRS]  │ Type: [MASTER/TRANS/LINE]
  ENTITY-[MOD]-002 │ [Exact entity name from SRS]  │ Type: [MASTER/TRANS/LINE]

BUSINESS CODES (one per master entity):
  ENTITY-[MOD]-001 │ Format: [MOD]-YYYY-NNNN       │ Field name: [entityCode]
  [Pattern sourced from: SRS Section [X] / ERP-DEFAULT]

LOVs (every LOV-ID with LOOKUP_CODE):
  LOV-[MOD]-001 │ LOOKUP_CODE: [EXACT_CODE]   │ Usage: [field name in entity]
  LOV-[MOD]-002 │ LOOKUP_CODE: [EXACT_CODE]   │ Usage: [field name in entity]
  [If reusing from master-registry: LOV-SYS-001 — LOOKUP_CODE: [CODE] — Owner: System Core]

RULES (full extraction — not summary):
  RULE-[MOD]-001:
    Scope      : ENTITY-[MOD]-[ID]
    Trigger    : [exact trigger from SRS]
    Statement  : [exact "The system MUST..." from SRS]
    Message-AR : [exact Arabic text from SRS]
    Message-EN : [exact English text from SRS]
    Source     : [SRS section reference]

  RULE-[MOD]-002:
    [same format]

SCREENS (CORE-9 — ONE SCR-ID per Composite Screen):
  SCR-[MOD]-001 │ [Exact screen name] │ Type: COMPOSITE (Search + Entry) │ Entity: ENTITY-[MOD]-001
  ⚠ Search and Entry are UX sub-screens under ONE SCR-ID — not separate SCR-IDs.
  ⚠ Each additional independent composite gets its own SCR-ID.

PERMISSIONS MATRIX (from SRS — CORE-9 model):
  SCR-[MOD]-001 │ PERM_[PAGE_CODE]_VIEW   : [Role A] ✓, [Role B] ✓
                │ PERM_[PAGE_CODE]_CREATE : [Role A] ✗, [Role B] ✓
                │ PERM_[PAGE_CODE]_UPDATE : [Role A] ✗, [Role B] ✓
                │ PERM_[PAGE_CODE]_DELETE : [Role A] ✗, [Role B] ✓
  VIEW = gateway: grants access to Search view + Entry view (read mode).

── FROM db-script-[MOD].md ──────────────────────────────────────────────────

TABLES (exact Oracle names):
  ENTITY-[MOD]-001 → TABLE: [EXACT_TABLE_NAME]
  ENTITY-[MOD]-002 → TABLE: [EXACT_TABLE_NAME]

SEQUENCES (exact Oracle names — one per table):
  TABLE: [EXACT_TABLE_NAME] → SEQUENCE: SEQ_[EXACT_TABLE_NAME]
                               TRIGGER : TRG_[EXACT_TABLE_NAME]
  [Agent instruction: use this exact sequence name in PK generation logic]

COLUMNS (key fields per table — full list in DB Alignment Manifest):
  [EXACT_TABLE_NAME]:
    PK  : [TABLE_PREFIX]_ID        DBF-[ID]  NUMBER(10)
    BC  : [TABLE_PREFIX]_CODE      DBF-[ID]  VARCHAR2/VARCHAR(50)  ← Business Code column
    AR  : NAME_AR                  DBF-[ID]  VARCHAR2/VARCHAR(200)
    EN  : NAME_EN                  DBF-[ID]  VARCHAR2/VARCHAR(100)
    LOV : [COLUMN_NAME]            DBF-[ID]  VARCHAR2/VARCHAR(50)  ← stores detail code
    AUD : CREATED_BY               DBF-[ID]  VARCHAR2/VARCHAR(255) ← from AuditableEntity
    AUD : CREATED_AT               DBF-[ID]  TIMESTAMP
    AUD : UPDATED_BY               DBF-[ID]  VARCHAR2/VARCHAR(255) ← from AuditableEntity
    AUD : UPDATED_AT               DBF-[ID]  TIMESTAMP
    FLG : IS_ACTIVE_FL             DBF-[ID]  NUMBER(1)/SMALLINT    ← soft deactivate (standard naming)

FK CONSTRAINTS (exact constraint names from db-script-[MOD].md):
  FK_[LOCAL]_[REF] — [LOCAL_TABLE].[FK_COL] → [REF_TABLE].[PK_COL]
  [Agent instruction: use these exact constraint names in DDL references]

LOV TABLES (from db-script-[MOD].md lookup section):
  LOOKUP_CODE: [EXACT_CODE] → stored in: [COLUMN_NAME] of [TABLE_NAME]
  [If lookup table has dedicated DDL: TABLE: LOOKUP_[CATEGORY_NAME]]

XM DEPENDENCIES:
  XM-[MOD]-001 │ HARD-FK  │ [LOCAL_TABLE].[FK_COL] → [TARGET_TABLE] │ Status: READY
  XM-[MOD]-002 │ SOFT-READ │ reads [TARGET_TABLE].[TARGET_COL]       │ Status: DEFERRED

── FROM master-registry.md ────────────────────────────────────────────

SHARED ENTITIES CONSUMED (do not redeclare):
  [ENTITY-ID from other module] — [entity name] — Owner: [module]
  This module accesses it via: [XM-[MOD]-[N]]

EXISTING LOV LOOKUP_CODES (reuse — do not create new):
  LOOKUP_CODE: [CODE] — [description] — Owner: [module]

MODULE PREFIX: [3-letter prefix] — used for all IDs in this module

╠══════════════════════════════════════════════════════════════════════
║  Extraction complete. Generation begins below.
║  All values above are BOUND into every phase that follows.
║  ⚠ If any field above shows [placeholder] → STOP and raise OQ-ID.
╚══════════════════════════════════════════════════════════════════════
```

## 2A.2 — Binding Rules (How Extracted Values Are Used)

### SEQUENCE BINDING
```
Rule: Every PK auto-generation reference in any phase MUST use the
      exact sequence name extracted from db-script-[MOD].md.

Format in execution plan (DATA+DOM and QRC phases):
  PK Generation : SEQ_[EXACT_TABLE_NAME].NEXTVAL
                  (exact name — sourced from db-script-[MOD].md Section 4)
  Trigger name  : TRG_[EXACT_TABLE_NAME]
                  (exact name — sourced from db-script-[MOD].md)

❌ FORBIDDEN:  "sequence: auto-generated" / "uses a sequence" / "[SEQ_NAME]"
✓  REQUIRED:  "sequence: SEQ_FIN_VENDOR.NEXTVAL" (actual name from db-script)

Agent instruction embedded in QRC:
  ⚠ The sequence name above (SEQ_[EXACT_TABLE_NAME]) is sourced from
    db-script-[MOD].md. Use this exact name in your PK generation implementation.
    If your JPA config uses GenerationType.SEQUENCE, reference this name
    in @SequenceGenerator(sequenceName = "SEQ_[EXACT_TABLE_NAME]").
```

### LOV / LOOKUP_CODE BINDING
```
Rule: Every LOV reference in any phase MUST use the exact LOOKUP_CODE
      extracted from srs-[MOD].md, confirmed against db-script-[MOD].md.

Format in execution plan (F2 phase, F3 phase, QRC):
  LOV-[MOD]-001:
    LOOKUP_CODE : [EXACT_CODE_FROM_SRS]   ← not "[lookupCode]" or "[LOV name]"
    Display name: [LOV descriptive name]
    Endpoint    : GET /api/v1/sys/lookups/[EXACT_CODE_FROM_SRS]
    Column      : [EXACT_COLUMN_NAME] in [EXACT_TABLE_NAME]  ← from db-script

❌ FORBIDDEN:  "LOV endpoint: /api/v1/sys/lookups/{lookupCode}"
✓  REQUIRED:  "LOV endpoint: GET /api/v1/sys/lookups/VENDOR_TYPE"
              (actual LOOKUP_CODE — not a parameter placeholder)

Agent instruction embedded in F2:
  ⚠ LOOKUP_CODE "VENDOR_TYPE" is sourced from srs-[MOD].md LOV-[ID].
    Pass this exact string to the lookup API endpoint.
    Do not derive it from field names or entity names.
```

### RULE BINDING (Full Text — Not Reference Only)
```
Rule: Every RULE-ID referenced in any phase includes the full rule text
      extracted from srs-[MOD].md — not just the ID.

Format in execution plan (DATA+DOM, SVC+API, F3 phases):
  RULE-[MOD]-001 — [Rule name]:
    Trigger    : [exact trigger — copied from srs-[MOD].md]
    Behavior   : [exact "The system MUST..." — copied from srs-[MOD].md]
    Message-AR : [exact Arabic text — copied from srs-[MOD].md]
    Message-EN : [exact English text — copied from srs-[MOD].md]
    Scope      : [CREATE | UPDATE | DELETE | ALL]

❌ FORBIDDEN:  "applies RULE-[MOD]-001 — see SRS"
              "validation per SRS RULE-[MOD]-001"
✓  REQUIRED:  Full rule text inline — agent reads the plan, not the SRS

Rationale: The agent has the execution plan. It should not need to
cross-reference the SRS to understand what validation to implement.
The plan is self-contained.
```

### COLUMN NAME BINDING
```
Rule: Every field reference in any phase uses the EXACT Oracle column name
      from db-script-[MOD].md — not a camelCase invention.

Format in execution plan:
  Field reference includes:
    Java property : [camelCaseName]        ← agent's responsibility to name
    DB column     : [EXACT_COLUMN_NAME]    ← sourced from db-script-[MOD].md DBF-ID
    DBF-ID        : DBF-[NNNN]            ← canonical reference

❌ FORBIDDEN:  Inventing column names not in db-script-[MOD].md
✓  REQUIRED:  Every column name reference traces to a DBF-ID in the
              DB Field Traceability Matrix (Project 2)

Agent instruction:
  Map Java property names to DB columns using the DB Alignment Manifest.
  The @Column(name = "[EXACT_COLUMN_NAME]") annotation must use the
  exact column name from DBF-ID lookup — not the Java property name.
```

### BUSINESS CODE FORMAT BINDING
```
Rule: Business Code format is extracted from SRS and stated explicitly.
      It is never described as "auto-generated" without the actual format.

Format in execution plan:
  Entity: [EntityName]
  Business Code:
    Field name : [entityCode]          ← Java property
    Column     : [TABLE_PREFIX]_CODE   ← exact DB column from db-script
    DBF-ID     : DBF-[NNNN]
    Format     : [MOD]-YYYY-NNNN       ← exact format from SRS
    Example    : VND-2025-0001
    Generation : SEQ_[EXACT_TABLE_NAME] provides the sequential part
    Uniqueness : UNIQUE constraint on column [TABLE_PREFIX]_CODE (DB-enforced)

❌ FORBIDDEN:  "Business Code: auto-generated — read-only"
✓  REQUIRED:  "Business Code: format VND-YYYY-NNNN — column VENDOR_CODE —
               sequence SEQ_FIN_VENDOR — UNIQUE constraint UC_VENDOR_CODE"
```

## 2A.3 — Extraction Failure Protocol

```
If any extracted value cannot be confirmed from uploaded artifacts:

CASE 1 — Value missing from db-script (SRS entity exists, no DB table):
  → GOVERNANCE REDUCED mode declared for this entity
  → Mark all DBF-ID references as [PENDING DB Script]
  → Do NOT invent table or column names
  → Raise OQ-ID: "DB table missing for ENTITY-[MOD]-[N]"

CASE 2 — LOV LOOKUP_CODE not in srs-[MOD].md or db-script:
  → Raise OQ-ID: "LOOKUP_CODE not defined for LOV-[MOD]-[N]"
  → F2 LOV service spec: mark as [LOOKUP_CODE: OQ-[N] — PENDING]
  → ALIGN gate: ⏸ BLOCKED for this LOV

CASE 3 — RULE message text missing (no Message-AR):
  → Raise OQ-ID: "Message-AR missing for RULE-[MOD]-[N]"
  → Error Catalog: mark ERR-[ID] Message-AR as [→ OQ-[N]]
  → F3 validation spec: use OQ reference — do not invent text

CASE 4 — Sequence not in db-script (table exists, no sequence):
  → Flag in DATA+DOM phase: "⚠ SEQ_[TABLE_NAME] not found in db-script"
  → QRC entry: note SEQUENCE: [not confirmed — verify in db-script]
  → Raise OQ-ID if generation trigger is absent
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 3 — PLAN INDEX
═══════════════════════════════════════════════════════════════════

```
## EXECUTION PLAN INDEX — [Module] — PLAN-ID: [xxx]
══════════════════════════════════════════════════════════════════
Feature Code   : [SRS feature code]
DBS-ID         : [DBS-ID of governing DB Script]
Governed by    : Execution Plan Governance Engine (Project 3) v3 (light)
Output Mode    : SINGLE-FILE — Agent-Ready Specification
Open Questions : [N active / None] — see OQ Log
══════════════════════════════════════════════════════════════════

ENTITY REGISTRY (this plan)
───────────────────────────────────────────────────────────────
ENTITY-ID          │ Entity Name       │ DB Table     │ Business Code │ Operations
───────────────────┼───────────────────┼──────────────┼───────────────┼──────────────
ENTITY-[MOD]-001   │ [Name]            │ [TABLE_NAME] │ [MOD]-YYYY-N  │ CRUD

FIELD REGISTRY (this plan)
───────────────────────────────────────────────────────────────
FIELD-ID   │ Field Name        │ DBF-ID       │ Type          │ Read-Only
───────────┼───────────────────┼──────────────┼───────────────┼──────────────
[list]
Note: Business Code fields are always Read-Only = YES

API REGISTRY (this plan)
───────────────────────────────────────────────────────────────
API-ID     │ Operation         │ HTTP Method  │ Endpoint
───────────┼───────────────────┼──────────────┼──────────────
[list]

RULE REGISTRY (this plan)
───────────────────────────────────────────────────────────────
RULE-ID            │ Rule Name    │ Scope        │ ENTITY-ID         │ Message-AR defined
───────────────────┼──────────────┼──────────────┼───────────────────┼───────────────────
[list]

SCREEN REGISTRY (this plan)
───────────────────────────────────────────────────────────────
SCR-ID     │ Screen Name       │ Type         │ ENTITY-ID
───────────┼───────────────────┼──────────────┼──────────────
[list — every SCR-ID from SRS must appear here]

LOV REGISTRY (this plan)
───────────────────────────────────────────────────────────────
LOV-ID     │ LOOKUP_CODE       │ Used In Field│ ENTITY-ID
───────────┼───────────────────┼──────────────┼──────────────
[list — every LOV-ID from SRS must appear here]

QUERY REFERENCE CATALOG SUMMARY
───────────────────────────────────────────────────────────────
QR-ID      │ Operation         │ Phase        │ Entity
───────────┼───────────────────┼──────────────┼──────────────
[list — all QR-IDs generated in DATA+DOM and SVC+API]
⚠ ALL entries in this catalog are AGENT REFERENCE only.
  The agent MUST rewrite every query during implementation
  using the actual project structure, entity names, and field names.

DB ALIGNMENT     : see DB Alignment Manifest — [status: ALIGNED ✓ / ISSUES: N]
XM STATUS        : [N DEFERRED / None] — see INT-C Summary + INT-R Status
CONTRACT GATE    : DOC [✓ / ✗] | INT-C [✓ / ✗]
SECURITY         : [Permissions matrix: N screens × N roles]
══════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 4 — DB ALIGNMENT MANIFEST (CANONICAL — FIELD-ID→DBF-ID)
═══════════════════════════════════════════════════════════════════

**Ownership:** Canonical binding declaration for FIELD-ID → DBF-ID.
Does NOT reproduce column names, DB types, or SRS section references —
those are sourced from the DB Field Traceability Matrix (Project 2) by DBF-ID lookup.

```
CONTRACT-1 VIOLATION PREVENTION — NON-NEGOTIABLE:

The Manifest contains ONLY these five columns:
  FIELD-ID | DBF-ID | Plan Type | FK/XM-ID | Match Status

✗ FORBIDDEN — never include in the Manifest:
  Column Name  — sourced by Agent from db-script-[MOD].md via DBF-ID lookup
  DB Type      — sourced by Agent from db-script-[MOD].md via DBF-ID lookup
  SRS Source   — sourced by Agent from db-script-[MOD].md via DBF-ID lookup
  Table Name   — sourced by Agent from db-script-[MOD].md via DBF-ID lookup

These columns feel helpful but reproducing them violates CONTRACT-1
and creates a P4 DUPLICATE finding (MAJOR severity).
The Agent has db-script-[MOD].md — it performs the lookup directly.
```

```
## DB ALIGNMENT MANIFEST — [Module] — PLAN-ID: [xxx] / DBS-ID: [xxx]
══════════════════════════════════════════════════════════════════
FIELD-ID  │ DBF-ID   │ Plan Type   │ FK/XM-ID         │ Match Status
──────────┼──────────┼─────────────┼──────────────────┼─────────────
FIELD-0001│ DBF-0001 │ Long        │ —                │ ✓
FIELD-0002│ DBF-0002 │ String(200) │ —                │ ✓
FIELD-0007│ DBF-0007 │ Long        │ XM-[MOD]-001 ⏸   │ ⏸
══════════════════════════════════════════════════════════════════
Legend: ✓ = aligned | ✗ = type mismatch (finding) | ⏸ = XM deferred
```

**FIELD-ID Assignment Rules:**
- Format: `FIELD-[4-digit sequence]`
- Sequence continuous across the module (not reset per entity)
- One-to-one mapping to DBF-IDs where DB mapping exists
- FIELD-IDs without DBF-ID: derived/computed fields only

---

═══════════════════════════════════════════════════════════════════
# SECTION 5 — OPEN QUESTIONS LOG — CONTINUATION
═══════════════════════════════════════════════════════════════════

The OQ Log is canonical and owned by PROJECT 1 (SRS Governance Engine).
This engine continues the OQ Log — it does NOT create a new one.

During PASS 1 (backend generation):
- New OQs arising during plan generation are ADDED to the existing OQ Log
- OQs resolved during plan generation are UPDATED in the OQ Log
- Updated OQ Log travels with the execution plan as an attached artifact

Artifact reference format:
```
Open Questions: [N active / None] — see OQ Log
```

---


---

## 7.1 Purpose and Scope

The Query Reference Catalog (QRC) expresses the **data retrieval and
persistence intent** for every repository operation in the plan.

It is NOT executable code.
It is a specification of what each operation must accomplish —
expressed as pseudo-SQL that captures:
- Which tables are involved
- Which conditions apply
- What is returned or modified
- What joins are required (and why)
- What ordering or pagination applies

```
╔══════════════════════════════════════════════════════════════════╗
║              QUERY REFERENCE CATALOG — CRITICAL RULE             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ⚠ AGENT REFERENCE ONLY — NOT EXECUTABLE AS-IS                  ║
║                                                                  ║
║  Every entry in this catalog is a LOGICAL SPECIFICATION.         ║
║  The implementation agent MUST:                                  ║
║    1. Read the intent expressed in this catalog                  ║
║    2. Rewrite the query from scratch using:                      ║
║       - The actual project entity class names                    ║
║       - The actual JPA field names (not table column names)      ║
║       - The actual repository method naming convention           ║
║       - The actual pagination/sorting framework in use           ║
║       - The actual project's query strategy (JPQL / Criteria /   ║
║         QueryDSL / native — per project standards)               ║
║    3. Never copy-paste from this catalog into production code    ║
║                                                                  ║
║  Purpose: give the agent the LOGIC — the agent provides the CODE ║
╚══════════════════════════════════════════════════════════════════╝
```

## 7.2 QR-ID Assignment Rules

```
Format  : QR-[MOD]-[4-digit sequence]
Assigned: during DATA+DOM and SVC+API phases
Sequence: continuous across the module
Owned by: P3 (same ownership as FIELD-ID, ERR-ID)
```

## 7.3 QRC Entry Format — Standard

One entry per distinct repository operation:

```
QR-[MOD]-[ID] — [Operation Name]
──────────────────────────────────────────────────────────────────
Phase        : [DATA+DOM / SVC+API — phase that defines this operation]
API-ID       : [API-ID this operation serves — else "Repository-only"]
Entity       : [ENTITY-ID of primary entity]
Operation    : [FIND_ONE | FIND_ALL | FIND_BY_CRITERIA | SAVE |
                UPDATE | DELETE | COUNT | EXISTS | NATIVE_QUERY]
──────────────────────────────────────────────────────────────────
Intent:
  [Plain-language description of what this query must accomplish.
   What business question does it answer?
   What data must it return?]

Logical Specification (pseudo-SQL — agent reference only):
  SELECT [fields or *]
  FROM   [primary table/entity]
  [JOIN  [related table] ON [join condition] — only if required]
  WHERE  [conditions derived from RULE-IDs and business logic]
  [AND   [additional conditions]]
  [ORDER BY [field] [ASC/DESC]]
  [pagination if applicable: LIMIT / OFFSET or equivalent]

Join Justification  : [NONE required / Required because: SRS ref or RULE-ID]
Transaction         : [READ_ONLY | READ_WRITE | REQUIRES_NEW]
                      Default: READ_ONLY for SELECT, READ_WRITE for SAVE/UPDATE/DELETE
Transaction note    : [justification if non-default — DRV-ID required]
Pagination          : [YES — page + size params / NO]
Filter fields       : [list of filterable fields and their filter type:
                        EXACT | LIKE | DATE_RANGE | ENUM]
Result shape        : [full entity / projection — field list / count only]
Null handling       : [optional fields — handled as: IS NULL check / excluded / default]
──────────────────────────────────────────────────────────────────
⚠ Agent: rewrite this query using actual entity class and field names.
   Do not use table names — use JPA entity class names.
   Do not copy column names — use mapped field property names.
──────────────────────────────────────────────────────────────────
```

## 7.4 QRC Entry Format — Aggregation / Reporting Operations

```
QR-[MOD]-[ID] — [Report / Aggregation Name]
──────────────────────────────────────────────────────────────────
Phase        : [SVC+API]
API-ID       : [API-ID]
Entity       : [primary entity / multiple]
Operation    : [COUNT | SUM | GROUP_BY | NATIVE_QUERY]
──────────────────────────────────────────────────────────────────
Intent:
  [What business report / summary is this computing?]

Logical Specification (pseudo-SQL — agent reference only):
  SELECT [aggregated fields and grouping columns]
  FROM   [entity/table]
  [JOIN  ...]
  WHERE  [conditions]
  GROUP  BY [grouping fields]
  [HAVING [group-level condition]]
  [ORDER  BY ...]

Note: If this requires a native query, flag reason:
  NATIVE-REASON: [aggregation not expressible in JPQL / performance requirement]
──────────────────────────────────────────────────────────────────
⚠ Agent: complex aggregations may require @Query with nativeQuery=true.
   Confirm with project DBA before implementing native queries.
──────────────────────────────────────────────────────────────────
```

## 7.5 QRC Standard Operations — Default Specifications

These apply uniformly unless overridden by a specific QR-ID entry:

```
╔══════════════════════════════════════════════════════════════════╗
║              QRC STANDARD OPERATION DEFAULTS                     ║
╠══════════════════════════╦═══════════════════════════════════════╣
║ FIND_ONE (by PK)         ║ SELECT entity WHERE pk = :pk          ║
║                          ║ Transaction: READ_ONLY                ║
║                          ║ Result: full entity or throw          ║
║                          ║ LocalizedException(NOT_FOUND,         ║
║                          ║   ErrorCodes.[ENTITY]_NOT_FOUND)      ║
║                          ║ ⚠ NEVER use NotFoundException         ║
╠══════════════════════════╬═══════════════════════════════════════╣
║ FIND_BY_CRITERIA         ║ SearchRequest extends                 ║
║ (search screen)          ║ BaseSearchContractRequest             ║
║                          ║ ALLOWED_SORT_FIELDS declared in Svc   ║
║                          ║ PageableBuilder.from(request,         ║
║                          ║   ALLOWED_SORT_FIELDS)                ║
║                          ║ SpecBuilder.build(request,            ║
║                          ║   ALLOWED_SORT_FIELDS)                ║
║                          ║ Empty result → HTTP 200, content:[]   ║
║                          ║ NEVER HTTP 404 on empty result        ║
║                          ║ Transaction: READ_ONLY                ║
╠══════════════════════════╬═══════════════════════════════════════╣
║ SAVE (create)            ║ INSERT entity with generated PK       ║
║                          ║ Business Code: auto-generated         ║
║                          ║ (format per SRS RULE-ID)              ║
║                          ║ Audit fields: AuditEntityListener     ║
║                          ║ orgUnitId: from framework             ║
║                          ║ Transaction: READ_WRITE               ║
╠══════════════════════════╬═══════════════════════════════════════╣
║ UPDATE (modify)          ║ UPDATE entity WHERE pk = :pk          ║
║                          ║ Business Code field: excluded         ║
║                          ║ (immutable after creation)            ║
║                          ║ Transaction: READ_WRITE               ║
╠══════════════════════════╬═══════════════════════════════════════╣
║ DELETE / DEACTIVATE      ║ Check usage first:                    ║
║ (soft deactivate)        ║ canDelete / canDeactivate check       ║
║                          ║ If false → LocalizedException         ║
║                          ║ If true → UPDATE IS_ACTIVE_FL = 0     ║
║                          ║ (standard: isActiveFl = false)        ║
║                          ║ Hard delete only if SRS mandates it   ║
║                          ║ Transaction: READ_WRITE               ║
╠══════════════════════════╬═══════════════════════════════════════╣
║ EXISTS (uniqueness check)║ SELECT COUNT(*) > 0                   ║
║                          ║ WHERE [unique constraint field] = :val║
║                          ║ AND pk != :currentPk (for update)     ║
║                          ║ Transaction: READ_ONLY                ║
╚══════════════════════════╩═══════════════════════════════════════╝

Agent note: Map every "table" reference above to the actual JPA entity class.
Map every "field" reference to the actual @Column-mapped property name.
```

## 7.6 QRC — Join Governance Rules

```
Join is allowed ONLY when explicitly required.
Every non-trivial join must have a DRV-ID.

╔══════════════════════════════════════════════════════════════════╗
║ Condition                              ║ Join Decision            ║
╠════════════════════════════════════════╬══════════════════════════╣
║ Response needs data from ONE table     ║ NO JOIN — single entity  ║
║ Response needs name from LOV table     ║ SOFT-READ via service,   ║
║                                        ║ NOT a join               ║
║ Response requires parent entity data   ║ JOIN + DRV-ID required   ║
║ Search filters on related entity field ║ JOIN + DRV-ID required   ║
║ Report aggregates across entities      ║ JOIN + DRV-ID + possible ║
║                                        ║ native query             ║
╚════════════════════════════════════════╩══════════════════════════╝

LOV / Lookup values:
  NEVER join to the lookups table to get display names.
  The Frontend service loads LOV options separately (F2 LOV service).
  The Backend returns the DETAIL_CODE — frontend resolves display name.
  Any join to lookups table = governance violation → 4A-5 finding.
```

---

═══════════════════════════════════════════════════════════════════

---

═══════════════════════════════════════════════════════════════════
# SECTION 8 — BACKEND PHASE EXECUTION SPECIFICATIONS
═══════════════════════════════════════════════════════════════════

## 8.0 — MARKER & THRESHOLD APPLICATION (READ BEFORE WRITING ANY PHASE)

**AMEND-P3-M.** Every phase below is generated ALREADY WRAPPED — not
wrapped afterward as a separate pass. Before writing phase [X]'s
content, look it up here:

```
╔══════════════╦══════════════╦═══════════════════════╦═══════════════════╗
║ Phase (name) ║ Marker KEY   ║ Threshold (SUB split)  ║ Atomic markers     ║
╠══════════════╬══════════════╬═══════════════════════╬═══════════════════╣
║ CORE         ║ CORE         ║ never splits           ║ none               ║
║ DATA+DOM     ║ DATA-DOM     ║ entities ≥ 5           ║ none (entity blocks║
║              ║              ║                        ║ carry no own       ║
║              ║              ║                        ║ marker)            ║
║ SVC+API      ║ SVC-API      ║ APIs ≥ 8 / methods ≥ 6 ║ <!-- API:{id} -->  ║
║ DOC          ║ DOC          ║ never splits           ║ none               ║
║ INT-C        ║ INT-C        ║ XM-IDs ≥ 5             ║ <!-- XM:{id} -->   ║
║ INT-R        ║ INT-R        ║ XM-IDs ≥ 5             ║ <!-- XM:{id} -->   ║
║ SEC-BE       ║ SEC-BE       ║ never splits           ║ none               ║
║ ALIGN-BE     ║ ALIGN-BE     ║ never splits           ║ none               ║
╚══════════════╩══════════════╩═══════════════════════╩═══════════════════╝
```

```
⚠ Marker KEY ≠ display name. The phase is called "DATA+DOM" in prose but
  its marker key is "DATA-DOM" (hyphen — see PROJECT-3-REGISTRY.md
  Section 5.7.3). Never write "<!-- PHASE:DATA+DOM:START -->" — that key
  does not exist. Same applies to "SVC+API" → key "SVC-API".

RULE: the very first line you write for a phase IS
  <!-- PHASE:{KEY}:START -->
and the very last line you write for it IS
  <!-- PHASE:{KEY}:END -->
There is no "write content, then mark it" step. Writing content and
opening its marker are the same action.

RULE: check the Threshold column WHILE writing the phase, not after.
If the count is already at/above threshold when you start (e.g. you
can see from Section 2A.1 extraction that there are 6 entities), wrap
the first sub-group in <!-- SUB:{KEY}-{label}:START --> — note the
phase KEY prefix, not the bare label — before writing its first entity
block. Never write the whole phase flat and split later, and never
drop the {KEY}- prefix even if this module's SUB labels don't look
like they'd collide with anything: the prefix is mandatory in every
phase, always, per PROJECT-3-REGISTRY.md Section 5.7.5 (AMEND-P3-N) —
not conditional on whether a collision seems likely this time. This is
what keeps SUB:INT-C-FINANCE distinct from SUB:INT-R-FINANCE when the
same module both consumes from and resolves to Finance in one plan.

RULE: any heading you write that contains the literal word "PHASE"
must use exactly one of the eight keys in the table above. A summary,
index, or informational section (Plan Index, DB Alignment Manifest,
Error Catalog, Agent Handoff Summary) is NEVER a phase and must never
be headed "# PHASE ..." — give it a distinct, non-PHASE heading
instead, and it receives no <!-- PHASE:...--> marker at all (see
PROJECT-3-REGISTRY.md Section 5.3, "TRAILING CONTENT" for where this
applies to content that comes after ALIGN-BE).

RULE: one atomic ID = one dedicated block, never grouped — see
PROJECT-3-REGISTRY.md Section 5.7.6 Rule 6 before writing SVC+API,
INT-C, or INT-R content for a module with several similar APIs or
XM dependencies.

Full protocol reference: PROJECT-3-REGISTRY.md Section 5.7.
```

---

## 8.1 Phase CORE — Architectural Policies

**Responsibility:** Declare package structure, shared abstractions, and
architectural policies that apply to the entire module.

**CORE Specification Format:**

```
## PHASE CORE — Architectural Policies
─────────────────────────────────────────────────────────────────
Gate Status: PASSED ✓

CANONICAL ARCHITECTURE — NON-NEGOTIABLE — APPLIES TO ALL MODULES:

BACKEND LAYERS AND RESPONSIBILITIES:
  ├── controller/  ← REST endpoint — request/response handling only
  │                   What it does: receives request, delegates to service,
  │                   returns response. Nothing else.
  │                   ✗ No business logic
  │                   ✗ No validation logic
  │                   ✗ No transaction management
  │
  ├── service/     ← Application orchestration
  │                   What it does: load data, invoke domain, manage
  │                   transactions, call external integrations, persist changes
  │                   ✗ Does not own business rules — delegates to domain
  │
  ├── mapper/      ← Entity ↔ DTO transformation only
  │                   What it does: converts between entity and DTO shapes
  │                   ✗ No business logic
  │                   ✗ No validations
  │                   ✗ No decisions
  │                   ✗ Never assigns audit fields
  │
  ├── domain/      ← Business rules owner
  │                   What it does: business validations, business decisions,
  │                   state transitions, calculations, domain behaviors
  │                   Note: domain behavior may live inside Entity methods
  │                   or in separate domain classes — plan declares which
  │
  ├── repository/  ← Data access only
  │                   What it does: queries, persistence operations
  │                   ✗ No business logic
  │
  ├── entity/      ← JPA entity + domain behavior
  │                   What it does: represents business concepts,
  │                   contains domain methods, carries DB mapping
  │
  ├── dto/         ← Request and response data shapes
  ├── exception/   ← Module error codes
  └── config/      ← Module configuration (if required)

FRONTEND LAYERS AND RESPONSIBILITIES:
  ├── models/      ← Data structure definitions only
  │                   What it does: TypeScript interfaces mirroring DTO shapes
  │                   ✗ No logic, no methods, no state
  │
  ├── services/    ← HTTP communication only
  │                   What it does: API calls, returns Observable<T>
  │                   ✗ No state management
  │                   ✗ No signal orchestration
  │
  ├── facades/     ← Screen state and orchestration
  │                   What it does: owns state signals per screen,
  │                   orchestrates service calls, routes errors
  │                   ✗ No direct HTTP calls — delegates to services
  │
  ├── helpers/     ← Pure utility functions
  │                   What it does: formatters, pure validators, utilities
  │                   ✗ No state, no side effects
  │
  └── components/  ← UI presentation only
                      What it does: renders UI, delegates all actions to facade
                      ✗ No direct service calls — always through facade
                      ✗ No business logic

LAYER BOUNDARIES (enforced — violations are 4A findings):
  ✗ Controller contains validation or business logic
  ✗ Service owns business rules directly — delegates to domain
  ✗ Mapper makes any decision or validation
  ✗ Repository contains business logic
  ✗ Component calls service directly — must go through facade
  ✗ Facade makes direct HTTP calls — must go through service
  ✗ Helper contains state or side effects
  ✗ Model contains logic or methods

CROSS-MODULE (XM) CONTRACT PLACEMENT:
  Inversion-of-control interfaces consumed by other modules
  (cross-module validation/business contracts) live in service/ —
  not a separate "api/" layer.
  A domain/ class MAY depend on another module's service/ interface
  for XM business-rule consumption. This is a module-boundary
  dependency, not a layer-boundary violation, and is NOT flagged
  as "domain depends on service."

PLAN DECLARATION REQUIRED IN PHASE CORE:
  Domain behavior placement — declare one of:
    "Domain behavior: embedded in Entity methods"
    "Domain behavior: separate classes in domain/"
  This decision is stated once in CORE and applies to the entire module.

PROJECT-STANDARD CONSTRAINTS (what the plan specifies — agent implements):
  Entity base      : AuditableEntity — uniform across all modules, including
                     erp-security (TenantAuditableEntity retired — multi-tenancy
                     removed, see security-registry.md v2.0.0 / 2026-06-21)
                     ✗ orgUnitId never appears in any DTO
                     Exception: short-lived security/session artifacts (e.g.
                     refresh tokens) with their own lifecycle (issuedAt/
                     expiresAt/revoked) are NOT required to extend
                     AuditableEntity. Declare explicitly in Phase CORE:
                     "[EntityName]: Session artifact — does not extend
                     AuditableEntity."
  Error signaling  : service layer signals LocalizedException — not NotFoundException
  Audit fields     : filled by AuditEntityListener — never appear in CreateRequest/UpdateRequest
                     never set by mapper or service
  Error catalog    : every ERR-ID registered in 4 places:
                     ErrorCodes constant + messages.properties + i18n JSON + ErpErrorMapperService
  Search contract  : SearchRequest extends BaseSearchContractRequest
                     ALLOWED_SORT_FIELDS declared per search operation
  Deactivation     : isActiveFl = false (record preserved — NOT deleted)
                     usage.canDelete/canDeactivate checked before any deactivation

  TYPE MAPPING STANDARDS (project-wide — no DRV-ID required):
    Flag columns (any column ending in _FL):
      ORACLE_19C  : NUMBER(1)  → Java Boolean / TypeScript boolean
      POSTGRESQL_16: SMALLINT  → Java Boolean / TypeScript boolean
      (IS_ACTIVE_FL, IS_MAIN_FL, IS_DEFAULT_FL, and any _FL column)
      This is a project-standard ORM convention — not a deviation.
      ✗ DRV-ID only required if a flag column is mapped DIFFERENTLY than this standard.

    Full DB_TARGET → Java type mapping (sourced from GOVERNANCE-CONFIG.md):
      ORACLE_19C  NUMBER(10)    → Java Long
      ORACLE_19C  NUMBER(1,0)   → Java Boolean
      ORACLE_19C  NUMBER(18,4)  → Java BigDecimal
      ORACLE_19C  VARCHAR2(N)   → Java String
      ORACLE_19C  CLOB          → Java String + @Lob
      ORACLE_19C  TIMESTAMP     → Java LocalDateTime
      POSTGRESQL_16 BIGINT      → Java Long
      POSTGRESQL_16 SMALLINT    → Java Boolean (for _FL columns) / Java Short (others)
      POSTGRESQL_16 NUMERIC(p,s)→ Java BigDecimal
      POSTGRESQL_16 VARCHAR(N)  → Java String
      POSTGRESQL_16 TEXT        → Java String + @Lob
      POSTGRESQL_16 TIMESTAMP   → Java LocalDateTime
    These mappings are project-standard. No DRV-ID required.
    Use the mapping row matching the declared DB_TARGET (GOVERNANCE-CONFIG.md).

ARCHITECTURAL POLICIES:
  All layer responsibilities and boundaries are defined in the
  CANONICAL ARCHITECTURE section above — that is the single source of truth.
  No architectural rule may be restated or redefined elsewhere in this plan.

  Non-architectural policies (not covered by layer structure):
  - LOV values         : loaded at runtime — never hardcoded in any layer
  - Business Code      : system-generated — never accepted from client input
  - Arabic + English   : both name fields required on every named entity
─────────────────────────────────────────────────────────────────
```

Note: CORE rarely splits. If nothing module-specific to declare →
write "CORE: Standard configuration — no module-specific abstractions required."

---

## 8.2 Phase DATA+DOM — Entity & Domain Specifications

**Responsibility:** Specify every entity, its fields, domain rules,
state machines, and repository operation intents.
FIELD-IDs assigned here. QR-IDs generated here for repository operations.

**All values in this phase are BOUND from Section 2A.1 extraction.**
**No placeholder values. Every name, column, sequence, and LOOKUP_CODE is actual.**

**Entity Specification Block — one per ENTITY-ID:**

```
### ENTITY-[MOD]-[SEQ] — [Exact entity name from SRS]
────────────────────────────────────────────────────────────────────────
SOURCE BINDINGS (from artifact extraction):
  DB Table       : [EXACT_TABLE_NAME]              ← from db-script-[MOD].md
  PK Column      : [TABLE_PREFIX]_ID               ← from DBF-[ID]
  PK Sequence    : SEQ_[EXACT_TABLE_NAME]           ← exact sequence from db-script-[MOD].md
  PK Trigger     : TRG_[EXACT_TABLE_NAME]           ← exact trigger from db-script-[MOD].md
  DBS-ID ref     : [DBS-ID of governing db-script]

BUSINESS CODE:
  Java property  : [entityCode]                    ← camelCase per SRS naming rules
  DB Column      : [TABLE_PREFIX]_CODE             ← DBF-[ID] from db-script-[MOD].md
  Oracle type    : VARCHAR2(50)
  Format         : [MOD]-YYYY-NNNN                 ← exact format from SRS
  Example        : [MOD]-2025-0001
  Sequence used  : SEQ_[EXACT_TABLE_NAME] (sequential part)
  DB Constraint  : UNIQUE — [exact constraint name from db-script-[MOD].md]
  Rule           : System inserts on first SAVE — excluded from all client requests

SOFT DEACTIVATION:
  Governed by CORE Deactivation Policy (Section 8.1 QRC operation table).
  DB binding: isActiveFl → IS_ACTIVE_FL column — DBF-[ID] — sourced from db-script-[MOD].md
  [Confirm column name from db-script-[MOD].md — EXCEPTION modules may differ]

AUDIT COLUMNS (sourced from db-script-[MOD].md — AuditEntityListener fills automatically):
  CREATED_BY     : DBF-[ID]  String (VARCHAR/VARCHAR2 per DB_TARGET)  ← filled by AuditEntityListener — NEVER set manually
  CREATED_AT     : DBF-[ID]  TIMESTAMP                                ← filled by AuditEntityListener — NEVER set manually
  UPDATED_BY     : DBF-[ID]  String (VARCHAR/VARCHAR2 per DB_TARGET)  ← filled by AuditEntityListener — NEVER set manually
  UPDATED_AT     : DBF-[ID]  TIMESTAMP                                ← filled by AuditEntityListener — NEVER set manually
  ⚠ Agent: these fields MUST NOT appear in CreateRequest or UpdateRequest DTOs
           MUST NOT be set in Mapper or Service — AuditEntityListener handles them
  ⚠ Naming: Java properties use camelCase → createdBy, createdAt, updatedBy, updatedAt
             DB columns sourced from db-script-[MOD].md per DBF-ID — do NOT assume column names

────────────────────────────────────────────────────────────────────────
FIELDS (DB Field Traceability Matrix binding):
────────────────────────────────────────────────────────────────────────
FIELD-ID  │ Java Property      │ DB Column (exact)  │ DBF-ID   │ DB Type (*)   │ Null │ Read-Only │ Constraint          │ Label-AR          │ Label-EN
──────────┼────────────────────┼────────────────────┼──────────┼───────────────┼──────┼───────────┼─────────────────────┼───────────────────┼──────────────────
FIELD-0001│ [entityPk]         │ [TABLE_PREFIX]_ID  │ DBF-0001 │ NUMBER(10)    │ No   │ System    │ PK — SEQ_[TABLE]    │ المعرف            │ ID
FIELD-0002│ [entityCode]       │ [TABLE_PREFIX]_CODE│ DBF-0002 │ VARCHAR2/VARCHAR(50)  │ No   │ YES       │ UNIQUE — [name]     │ الرمز             │ Code
FIELD-0003│ nameAr             │ NAME_AR            │ DBF-0003 │ VARCHAR2/VARCHAR(200) │ No   │ No        │ NOT NULL            │ الاسم بالعربي     │ Name (Arabic)
FIELD-0004│ nameEn             │ NAME_EN            │ DBF-0004 │ VARCHAR2/VARCHAR(100) │ No   │ No        │ NOT NULL            │ الاسم بالإنجليزي  │ Name (English)
FIELD-0005│ [lovField]Id       │ [EXACT_LOV_COL]    │ DBF-0005 │ VARCHAR2/VARCHAR(50)  │ No   │ No        │ stores detail code  │ [Arabic label]    │ [English label]
FIELD-0006│ isActiveFl         │ IS_ACTIVE_FL       │ DBF-0006 │ NUMBER(1)     │ No   │ System    │ DEFAULT 1           │ نشط               │ Active
────────────────────────────────────────────────────────────────────────
(*) DB Type column: values are sourced from db-script-[MOD].md DBF-ID lookup
    and reflect the declared DB_TARGET for this session.
    ORACLE_19C   → NUMBER(10), VARCHAR2(N), CLOB, NUMBER(1), TIMESTAMP ...
    POSTGRESQL_16→ BIGINT, VARCHAR(N), TEXT, SMALLINT, TIMESTAMP ...
    Agent: copy the exact type from db-script-[MOD].md — do NOT invent or guess.

⚠ EVERY column name above is sourced from db-script-[MOD].md DBF-ID lookup.
  The NO-COLUMN-INVENTION RULE (Section 2A.0) applies to ALL rows in this table.

LABEL GOVERNANCE RULES:
  Label-AR and Label-EN are mandatory for every FIELD-ID row.
  Purpose: consumed directly by frontend (React form labels, table headers,
           tooltips) and by Flutter mobile (field labels).
           Eliminates hardcoded label strings in UI components.
  Source:  SRS entity/field definitions — if not specified in SRS,
           derive from the field semantic (name, code, date, status, etc.)
           using standard ERP terminology.
  Rules:
    ✗ Label-AR must be in Arabic — never transliterate English into Arabic letters
    ✗ Label-EN must be the human-readable business label — not the Java property name
       (e.g. "Contract Date" not "contractDate", "Active" not "isActiveFl")
    ✗ Audit fields (createdBy/createdAt/updatedBy/updatedAt) → include labels
       even though they are excluded from CreateRequest/UpdateRequest DTOs
    ✗ PK field → Label-AR: "المعرف" / Label-EN: "ID" (system field — no UI input)
    ✗ isActiveFl → Label-AR: "نشط" / Label-EN: "Active"

DTO MEMBERSHIP RULES (extracted from project standards):
  CreateRequest  : excludes → [entityPk], [entityCode], isActiveFl,
                               createdBy, createdAt, updatedBy, updatedAt
  UpdateRequest  : excludes → [entityPk], [entityCode], isActiveFl,
                               createdBy, createdAt, updatedBy, updatedAt
  ResponseDTO    : includes → all fields including [entityCode], isActiveFl,
                               createdBy, createdAt, updatedBy, updatedAt
  ⚠ Agent: map Java property → DB column via @Column(name="[EXACT_DB_COLUMN]")
    Source every column name from db-script-[MOD].md DBF-ID — never use Java property name as column.

────────────────────────────────────────────────────────────────────────
LOV FIELDS (LOOKUP_CODE binding):
────────────────────────────────────────────────────────────────────────
⚠ LOOKUP_CODE governance: Section 2A.1 (Artifact Extraction Protocol) is the
  canonical binding source. All LOOKUP_CODEs below come from that extraction.

FIELD-ID  │ Java Property  │ DB Column (exact) │ DBF-ID   │ LOV-ID       │ LOOKUP_CODE (exact)    │ Endpoint                                          │ Label-AR       │ Label-EN
──────────┼────────────────┼───────────────────┼──────────┼──────────────┼────────────────────────┼───────────────────────────────────────────────────┼────────────────┼────────────────
FIELD-0005│ [lovField]Id   │ [EXACT_COL]       │ DBF-0005 │ LOV-[MOD]-001│ [from Section 2A.1]    │ GET /api/v1/sys/lookups/[EXACT_LOOKUP_CODE]        │ [Arabic label] │ [English label]
────────────────────────────────────────────────────────────────────────
  Column stores DETAIL_CODE (VARCHAR/VARCHAR2 per DB_TARGET) — never a numeric FK to lookup table.

────────────────────────────────────────────────────────────────────────
DOMAIN RULES (full text — extracted from srs-[MOD].md — no "see SRS" shortcuts):
────────────────────────────────────────────────────────────────────────
RULE-[MOD]-001 — [Exact rule name from SRS]:
  Trigger    : [exact trigger text — copied from SRS]
  Statement  : [exact "The system MUST..." — copied from SRS character-perfect]
  Message-AR : [exact Arabic text — copied from SRS character-perfect]
  Message-EN : [exact English text — copied from SRS]
  Scope      : [CREATE | UPDATE | DELETE | ALL]
  DB Enforce : [UNIQUE constraint: [exact name] / CHECK constraint: [exact name] / app-level]
  ERR-ID     : [assigned in SVC+API phase — forward reference]
  Owned by   : [domain layer — per CANONICAL ARCHITECTURE declared in PHASE CORE]

RULE-[MOD]-002 — [Exact rule name from SRS]:
  [same format — all fields required]

────────────────────────────────────────────────────────────────────────
STATE MACHINE (if entity has status workflow):
────────────────────────────────────────────────────────────────────────
Status LOV   : LOV-[MOD]-[ID] — LOOKUP_CODE: [EXACT_LOOKUP_CODE from SRS]
Status column: [EXACT_STATUS_COLUMN] in [EXACT_TABLE_NAME] — DBF-[ID]
               DB type: VARCHAR/VARCHAR2(50) per DB_TARGET — stores DETAIL_CODE

Status values (DETAIL_CODEs from SRS LOV definition):
  [DETAIL_CODE_1] — [Arabic label from SRS] / [English label]
  [DETAIL_CODE_2] — [Arabic label from SRS] / [English label]
  [DETAIL_CODE_3] — [Arabic label from SRS] / [English label]

Initial status : [DETAIL_CODE] — set on INSERT

Transitions:
  [DETAIL_CODE_A] → [DETAIL_CODE_B] : Trigger: [action] │ Actor: [role from SRS]
  [DETAIL_CODE_B] → [DETAIL_CODE_C] : Trigger: [action] │ Actor: [role from SRS]
  [DETAIL_CODE_B] → [DETAIL_CODE_A] : Trigger: reject   │ Actor: [role from SRS]

Terminal states (no further transitions): [DETAIL_CODE list]
Invalid transition rule: RULE-[MOD]-[N] — Message-AR: [exact text]

────────────────────────────────────────────────────────────────────────
CROSS-MODULE DEPENDENCIES (from db-script-[MOD].md XM Register):
────────────────────────────────────────────────────────────────────────
XM-[MOD]-[N] — [HARD-FK | SOFT-READ]
  Local table  : [EXACT_TABLE_NAME]
  Local column : [EXACT_FK_COLUMN]           DBF-[ID]
  Target table : [EXACT_TARGET_TABLE]        in [Target Module]
  Status       : [READY | DEFERRED]
  [Or: None — no cross-module dependencies for this entity]

REPOSITORY OPERATIONS REQUIRED:
  → QR-[MOD]-[N] : FIND_ONE by PK
  → QR-[MOD]-[N] : FIND_BY_CRITERIA (search screen filters)
  → QR-[MOD]-[N] : SAVE (create)
  → QR-[MOD]-[N] : UPDATE (modify)
  → QR-[MOD]-[N] : EXISTS (Business Code uniqueness check)
  [Additional operations per SRS requirements]
  → QRC entries generated in Section 11
```

**DATA+DOM Governance Rules:**
```
BC-DOM-RULE-1 — Business Code: auto-generated by NumberingEngine (master-registry Section 8)
               — exact format from SRS — exact sequence name from db-script
               — Service Layer calls NumberingEngine.generate([entityType], [legalEntityFk], [branchFk])
               — No module may implement its own numbering sequence or pattern
BC-DOM-RULE-2 — Business Code: immutable after creation — UNIQUE constraint name from db-script
BC-DOM-RULE-3 — LOV fields: stored as DETAIL_CODE (VARCHAR2/VARCHAR per DB_TARGET) — LOOKUP_CODE governance: Section 2A.1
LOC-DOM-RULE-1 — nameAr (VARCHAR2/VARCHAR(200)) AND nameEn (VARCHAR2/VARCHAR(100)) — both mandatory — NOT NULL
SEC-DOM-RULE-1 — Soft deactivation: governed by CORE Deactivation Policy (Section 8.1 QRC table)
               Reference only — behavior definition is in CORE, not here
BIND-RULE-1   — Every DB column reference uses the EXACT Oracle name from db-script DBF-ID lookup
BIND-RULE-2   — Every sequence reference uses SEQ_[EXACT_TABLE_NAME] — not a generic placeholder
BIND-RULE-3   — Every LOOKUP_CODE is the exact code from SRS LOV definition — Section 2A.1 governs
BIND-RULE-4   — Every RULE statement is the exact text from SRS — not a summary or paraphrase
```

---

## 8.3 Phase SVC+API — Service & API Contract Specifications

**Responsibility:** Specify every API endpoint, its request/response
contracts, orchestration logic, and error handling.
API-IDs and ERR-IDs assigned here.

**All values bound from Section 2A.1. Endpoint paths, DTO fields,
validation rules, and error messages use actual names — not placeholders.**

**API Contract Block — one per API-ID:**

```
### API-[MOD]-[ID] — [Operation Name]
─────────────────────────────────────────────────────────────────
Endpoint         : /api/v1/[module-prefix]/[entity-plural-kebab]
                   ⚠ module-prefix: [exact 3-letter prefix from master-registry]
                   ⚠ entity-plural-kebab: [derived from EXACT entity name in SRS]
                   Examples: /api/v1/prc/vendors, /api/v1/fin/journal-entries
HTTP Method      : [GET | POST | PUT | PATCH | DELETE]
Controller       : [ControllerClassName] → method: [methodName]
Service          : [ServiceClassName] → method: [methodName]
─────────────────────────────────────────────────────────────────
REQUEST:
  Content-Type   : [application/json / N/A for GET]
  Path Params    : [param name: type — e.g., id: Long]
  Query Params   : [param: type, required/optional — for GET/search]
                   ⚠ Filter param names match FIELD-IDs from DATA+DOM
  Request Body   : [DTO name]
    Fields:
      [fieldName]   : [type]    [REQUIRED | OPTIONAL]  [constraint]
      nameAr        : String    REQUIRED  — VARCHAR2/VARCHAR(200) maps to NAME_AR
      nameEn        : String    REQUIRED  — VARCHAR2/VARCHAR(100) maps to NAME_EN
    Excluded fields : [exact Business Code field name] — system generates via SEQ_[TABLE]
                     [any other system-managed fields per db-script-[MOD].md]

RESPONSE:
  Success code   : [200 | 201 | 204]
  Response DTO   : [DTO name]
    Fields:
      [fieldName]   : [type]    [description]
      nameAr        : String    — maps to NAME_AR
      nameEn        : String    — maps to NAME_EN
      [entityCode]  : String    — Business Code — format [MOD]-YYYY-NNNN — always in GET
  Paginated      : [YES — JPA Page<T> — agent uses project's existing pagination framework / NO]

VALIDATIONS (full rule text from SRS — not reference only):
  1. RULE-[MOD]-[N] — [Exact rule name]:
       Statement  : [exact "The system MUST..." from SRS]
       Trigger    : [exact trigger]
       Message-AR : [exact Arabic from SRS]
       Message-EN : [exact English from SRS]
  2. RULE-[MOD]-[N] — [Exact rule name]:
       [same format]

ERRORS (assigned here — used by Error Catalog and F3):
  ERR-[ID] → RULE-[MOD]-[N] triggered → HTTP [4xx/5xx]
             Message-AR: [exact text from SRS RULE — character-perfect]
             Message-EN: [exact text from SRS RULE]
  ERR-[ID] → [next condition] → HTTP [4xx/5xx]
             Message-AR: [exact Arabic text]
             Message-EN: [exact English text]

SERVICE ORCHESTRATION:
  ⚠ Describes WHAT happens in sequence — not which layer executes each step.
     Layer placement is determined by CANONICAL ARCHITECTURE in PHASE CORE.

  1. [load]      — what data is fetched and from where (entity, related entities)
  2. [validate]  — which RULE-[MOD]-[N] is evaluated and what it checks
  3. [integrate] — which XM-[MOD]-[N] dependency is involved (if any)
  4. [persist]   — what gets saved/updated, which sequence/table is used
  Note: No business logic in controller.

REPOSITORY OPERATION:
  QR-ID      : [QR-[MOD]-[N]] — see Section 11 QRC
  Table      : [EXACT_TABLE_NAME]          ← from db-script-[MOD].md
  Operation  : [FIND_ONE | FIND_BY_CRITERIA | SAVE | UPDATE | DELETE]
  Join       : [NONE / required — DRV-[ID] — justified by SRS requirement]
  Transaction: [READ_ONLY | READ_WRITE]
  Sequence   : SEQ_[EXACT_TABLE_NAME]      ← used for SAVE operation PK

SECURITY:
  Screen     : SCR-[MOD]-[ID] — [exact screen name from SRS]
  Permission : [VIEW | CREATE | EDIT | DELETE | APPROVE]
  ⚠ Agent: enforce via permission check mechanism before processing request

LOCALIZATION:
  Error responses: messageAr AND messageEn (exact texts above — from Error Catalog)
  Name responses : nameAr (NAME_AR) AND nameEn (NAME_EN) — both always returned
─────────────────────────────────────────────────────────────────
```

**API Governance Rules:**
```
BC-B2-RULE-1 — Business Code excluded from POST body — system uses SEQ_[EXACT_TABLE]
BC-B2-RULE-2 — Business Code excluded from PUT/PATCH body — attempt → ERR with exact message
BC-B2-RULE-3 — Business Code always appears in GET responses (format [MOD]-YYYY-NNNN)
LOC-B2-RULE-1 — nameAr (NAME_AR) AND nameEn (NAME_EN) — both in all responses
LOC-B2-RULE-2 — Every error response: exact messageAr + messageEn from Error Catalog
SEC-B2-RULE-1 — Every controller method: permission check with exact SCR-ID and operation
SEC-B2-RULE-2 — No hardcoded role/user checks in service layer
BIND-RULE-5   — Every endpoint uses exact module prefix from master-registry
BIND-RULE-6   — Every validation block includes full rule text — not "see SRS" reference

API CONTRACT COMPLETENESS RULES:

RULE-ERR-CARRY — Errors field must reflect all Validations:
  For every API contract, every RULE-[MOD]-N in the Validations list
  must have a corresponding ERR-[MOD]-N in the Errors field.
  ✗ FORBIDDEN: RULE-ID present in Validations with no matching ERR-ID in Errors
  ✓ Exception: multiple RULE-IDs that share one ERR-ID — list ERR-ID once

RULE-PLATFORM-ERR — Platform-standard errors require documented source:
  HTTP 404 / 500 / 503 errors are infrastructure concerns, not business rules.
  When added to the Error Catalog:
  ✓ RULE-ID field = "PLATFORM-STD" (not "—")
  ✓ DRV-ID entry documenting it as platform-standard — not a business rule
  ✗ FORBIDDEN: ERR-ID with RULE-ID = "—" and no DRV-ID

RULE-REPO-DRV — Repository strategy deviations require DRV-ID:
  Default values (no DRV-ID needed):
    Read operations  : READ_ONLY transaction
    Fetch strategy   : LAZY
    Join             : NONE
  Deviations that require a DRV-ID in the Derivation Log:
    EAGER fetch      → DRV-[N]: justification for eager loading
    Compound UPDATE  → DRV-[N]: description of multi-step operation
    Native query     → DRV-[N]: reason JPQL cannot express this intent
```

**PROJECT-STANDARD Rules** — defined once in CORE phase (Section 8.1) — apply here:
```
Exception handling  : LocalizedException — NotFoundException BANNED — see CORE
Audit fields        : AuditEntityListener — never in DTO — see CORE
Search/Pagination   : BaseSearchContractRequest + ALLOWED_SORT_FIELDS — see CORE
Entity base         : AuditableEntity — uniform, no tenant variant — see CORE
ERR-ID registration : 4-point registration (ErrorCodes + messages + json + ErpErrorMapper) — see CORE
```

---

## 8.4 Phase DOC — Contract Stabilization

**Responsibility:** Extract and stabilize API contracts for frontend consumption.
DOC ✓ is required before F1, F2, F3 may proceed.

**DOC produces three sub-documents embedded in the plan:**

### DOC-1: API Contract Summary

```
## API CONTRACT SUMMARY — [Module] — PLAN-ID: [xxx]
─────────────────────────────────────────────────────────────────
API-ID      │ Endpoint                  │ Method │ Request DTO    │ Response DTO   │ Stability
────────────┼───────────────────────────┼────────┼────────────────┼────────────────┼──────────
API-[ID]-001│ /api/v1/[mod]/[entity]    │ GET    │ [filter params]│ [DTO name]     │ STABLE
API-[ID]-002│ /api/v1/[mod]/[entity]    │ POST   │ [DTO name]     │ [DTO name]     │ STABLE
API-[ID]-003│ /api/v1/[mod]/[entity]/id │ PUT    │ [DTO name]     │ [DTO name]     │ STABLE
─────────────────────────────────────────────────────────────────
Unstable APIs: [list with reason / None]
Frontend-governed contracts: [APIs where frontend owns the shape / None]
```

### DOC-2: DTO Typing Rules (Constraints — not a full catalog)

DTOs are fully defined in Phase SVC+API per API-ID.
DOC does NOT reproduce them — agent reads SVC+API directly.

Two constraints apply across all DTOs:
```
LOV field typing : String (stores detail code from MD_LOOKUP_DETAIL) — never ENUM
Business Code    : String — always in ResponseDTO — never in CreateRequest/UpdateRequest
```

### DOC-3: Pagination & Filter Standards

```
## PAGINATION & FILTER STANDARDS (PROJECT-STANDARD)
─────────────────────────────────────────────────────────────────
Backend strategy : JPA Page<T> — use directly — NO custom pagination wrapper
                   Agent reads the existing framework and uses it as-is.

Request contract : SearchRequest extends BaseSearchContractRequest
                   → page (0-based), size, sortBy, sortDir
                   → ALLOWED_SORT_FIELDS declared in every search Service
                   → PageableBuilder.from(request, ALLOWED_SORT_FIELDS) builds Pageable

Response contract: JPA Page<T> serialized by the project's response framework.
                   Do NOT create a new wrapper — use what exists.

Empty result rule : HTTP 200 with empty content — NEVER HTTP 404

Filter types     : EXACT (=), LIKE (%value%), DATE_RANGE (from/to)
Sort validation  : against ALLOWED_SORT_FIELDS set declared per Service

React frontend  : currentPage and pageSize are derived from last search request
                   — not independent state
                   ✗ NEVER declare them as separate independent state
─────────────────────────────────────────────────────────────────
```

**DOC GATE CHECK (auto-evaluated):**
```
[ ✓/✗ ] All API-IDs from SVC+API appear in API Contract Summary
[ ✓/✗ ] Error Catalog complete with Arabic + English messages
[ ✓/✗ ] All APIs marked STABLE or explicitly UNSTABLE
[ ✓/✗ ] Pagination standard declared
DOC Gate: [PASSED ✓ / FAILED ✗ — list issues — auto-corrected if possible]
```

**v2.0 STATUS NOTE (CONTRACT-12 — read this before relying on DOC-1):**
```
DOC-1 (API Contract Summary above) is now an INTERNAL, backend-only
self-consistency artifact. It is useful for this engine's own planning
discipline, but it is NO LONGER the frontend's source of truth for API
shape.

PROJECT-3-FRONTEND-ENGINE.md (PASS 2) gates on REAL API Docs, generated
from the live implemented backend (api-doc-generator), not on this
table. This exists specifically because a planned contract can drift
during implementation, and a real one cannot.

Do not treat DOC ✓ here as equivalent to "frontend may now start" —
that gate is GATE: BACKEND MODULE COMPLETE, evaluated independently
(see CONTRACT-12 in shared-artifact-contracts.md).
```

---

## 8.5 Phase INT-C — Integration Contract Specifications

**Responsibility:** Define contracts for every cross-module dependency (XM-ID).
CRITICAL: INT-C does NOT assign new XM-IDs. All XM-IDs come from DB Script.

```
## INT-C SUMMARY — [Module] — PLAN-ID: [xxx]
══════════════════════════════════════════════════════════════════════════
XM-ID        │ Classification │ Target Module  │ Interface Type  │ Contract Status
─────────────┼────────────────┼────────────────┼─────────────────┼────────────────
XM-[MOD]-001 │ HARD-FK        │ Org Master     │ DB Foreign Key  │ CONTRACTED ✓
XM-[MOD]-002 │ SOFT-READ      │ System Core    │ REST API call   │ CONTRACTED ✓
XM-[MOD]-003 │ HARD-FK        │ Finance Module │ DB Foreign Key  │ DEFERRED ⏸
══════════════════════════════════════════════════════════════════════════

Per XM-ID Contract Block:

### XM-[MOD]-[N] — [Dependency description]
─────────────────────────────────────────────────────────────────
Target Module    : [module name]
Target Entity    : [entity name] — ENTITY-ID: [ID]
Classification   : [HARD-FK | SOFT-READ | EVENT | READ_ONLY]
Interface Type   : [DB Foreign Key / REST API call / Message queue]
Contract:
  Endpoint (if API)    : [GET /api/v1/[target-mod]/[entity]/{id}]
  Data required        : [what fields are needed from target]
  Fallback if absent   : [error response / null handling / default value]
Retry policy     : [N retries, M ms backoff / Not applicable]
Timeout          : [N ms / Not applicable]
Idempotency      : [YES — safe to retry / NO — one-shot operation]
Blocks           : [FIELD-IDs blocked if DEFERRED]
Unblock condition: [what must happen for this to become READY]
DEFERRED strategy: [mock strategy / provisional value / skip field]
─────────────────────────────────────────────────────────────────
```

**INT-C GATE CHECK (auto-evaluated):**
```
[ ✓/✗ ] All XM-IDs from DB Script XM Register accounted for
[ ✓/✗ ] Classification declared for each XM-ID
[ ✓/✗ ] All DEFERRED have unblock condition
[ ✓/✗ ] No new XM-IDs invented (P3 never assigns XM-IDs)
[ ✓/✗ ] Open RXEs acknowledged
[ ✓/✗ ] Inbound XM stubs (from future consumers) use INBOUND-STUB notation
INT-C Gate: [PASSED ✓ / FAILED ✗ — list — auto-corrected if possible]
```

**INBOUND XM STUB NOTATION (when this module is ROOT/SOURCE):**

When this module is a source that future consumer modules will reference,
but those modules have not yet been built:

```
✗ FORBIDDEN: "TODO: XM-FIN-[N]" or any unqualified placeholder

✓ REQUIRED format:
  XM-INBOUND-STUB-[N]
    Consumer module  : [Finance | Inventory | TBD — from SRS cross-module section]
    Entity exposed   : [EntityName] — [SOFT-READ | HARD-FK]
    XM-ID assignment : will be assigned by consumer at their own MODE 1.5
    Current status   : NOT-YET-ASSIGNED
    DRV-[N]          : inbound XM-IDs are assigned by the consuming module —
                       this module does not assign them
```

---

## 8.6 Phase INT-R — Runtime Activation Status

**Responsibility:** Declare runtime activation status per XM-ID.
Consumes INT-C contracts — does NOT redefine them.

```
## INT-R STATUS — [Module] — PLAN-ID: [xxx]
══════════════════════════════════════════════════════════════════════════
XM-ID        │ Status           │ Workaround / Mock Strategy
─────────────┼──────────────────┼──────────────────────────────────────
XM-[MOD]-001 │ READY ✓          │ —
XM-[MOD]-002 │ DEFERRED ⏸       │ Return null / use default value [X]
XM-[MOD]-003 │ MOCKED 🔧        │ Mock service returns [mock data spec]
══════════════════════════════════════════════════════════════════════════

Status options:
  READY          — target module available, contract confirmed
  DEFERRED ⏸     — target not yet available, workaround in place
  MOCKED 🔧      — mock/stub in use during development
  SIMULATED      — simulated data for testing
  BLOCKED ✗      — no workaround possible, blocks implementation
  EXTERNAL_WAIT  — waiting on external system confirmation

DEFERRED items require workaround spec:
  → What the consuming code should do when target is unavailable
  → What mock/default value to use
  → Test behavior when deferred dependency resolves
```

---


## 8.7 Phase SEC-BE — Backend Security Specifications

**Responsibility:** Specify API-level permission enforcement and
security seed data requirements for every SCR-ID in the plan.

**v2.0 split note:** This phase used to be combined with frontend
screen-guard/UI behavior in one "Phase SEC". That UI-facing half now
lives in PROJECT-3-FRONTEND-ENGINE.md as Phase SEC-FE. This file
covers only the backend (API enforcement + seed data) half.

```
### SEC-BE — SCR-[MOD]-[ID] — [Screen Name]
─────────────────────────────────────────────────────────────────
API-level enforcement:
  Every API-ID serving this screen requires permission verification
  before the request is processed — see API Contract blocks in SVC+API

EXCEPTION module scope:
  [If screen references EXCEPTION entities: declare scope boundary here]
─────────────────────────────────────────────────────────────────

SECURITY SEED DATA REQUIREMENTS:
  Screen registration (table: SEC_PAGES — built like any other table,
  standard naming convention applies, see db-script-[MOD].md for exact
  column names once Security actually goes through P2):
    SEC_PAGES must contain one row per Composite Screen:
      page_code : [PAGE_CODE] — used in PERM_<PAGE_CODE>_<TYPE> pattern
      page_name : [screen name]
      parent_id_fk: [parent page id or null]
  Permission rows (table: PERMISSIONS — same, standard naming):
    PERMISSIONS must contain 4 rows per screen (CORE-9):
    ────────────────────────────────────────────────────────
    Permission Name              │ Roles Assigned
    ─────────────────────────────┼──────────────────────────
    PERM_[PAGE_CODE]_VIEW        │ [role A], [role B]
    PERM_[PAGE_CODE]_CREATE      │ [role B]
    PERM_[PAGE_CODE]_UPDATE      │ [role B]
    PERM_[PAGE_CODE]_DELETE      │ [role B]
    ────────────────────────────────────────────────────────
  Column names for SEC_PAGES and PERMISSIONS come from db-script-[MOD].md
  (Pk/Fk/Fl suffix conventions apply — no special-casing).

SEC-BE Governance Rules:
  SEC-IMPL-RULE-1 — Every SCR-ID has permission verification enforced
                    at the API level (no exceptions)
  SEC-IMPL-RULE-3 — HTTP 403 responses: mapped via LocalizedException,
                    carrying the correct ERR-ID
  SEC-IMPL-RULE-4 — Every SCR-ID verified in SEC_PAGES before launch

Note: canView/canCreate/canEdit/canDelete/canApprove UI-level behavior
(show/hide, read-only fields, navigation guards) is specified in
PROJECT-3-FRONTEND-ENGINE.md Phase SEC-FE — it consumes the SAME
PERMISSIONS seed data declared here (reference only, never redefined).
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 9 — ALIGN-BE GATE (BACKEND INTERNAL SELF-CONSISTENCY — AUTO-RUNS)
═══════════════════════════════════════════════════════════════════

**ALIGN-BE validates the backend execution plan against ITSELF.**
**ALIGN-BE does NOT validate against external inputs (SRS or DB Script).**
**External validation = Project 4.1 scope.**
**ALIGN-BE runs automatically after SEC-BE phase — no user trigger needed.**
**After ALIGN-BE ✓, backend-execution-plan-[MOD].md is complete. Test artifacts**
**(backend-test-plan-[MOD].md + test-execution-manifest.md) are generated**
**separately by the standalone Test Generation Engine, OUTSIDE this**
**engine and OUTSIDE the pipeline — see PROJECT-TEST-GENERATION-ENGINE.md.**

**v2.0 split note:** The original ALIGN gate validated backend AND
frontend content in one table. Frontend-specific checks (screen
structure, F1-F4, LOV service/validator wiring, UI-level security,
Business Code display in forms) now live in
PROJECT-3-FRONTEND-ENGINE.md as ALIGN-FE. This table covers backend
content only.

```
## ALIGN-BE GATE — [Module] — PLAN-ID: [xxx]
═══════════════════════════════════════════════════════════════════════════

TRACEABILITY CHECKS                                        │ Status
───────────────────────────────────────────────────────────┼──────────────
All FIELD-IDs used in phases appear in Plan Index          │ [✓ / ✗ list]
All API-IDs used in phases appear in Plan Index            │ [✓ / ✗ list]
All RULE-IDs used in phases appear in Plan Index           │ [✓ / ✗ list]
All ERR-IDs used in Error Catalog appear correctly         │ [✓ / ✗ list]
All QR-IDs in QRC appear in Plan Index QRC Summary         │ [✓ / ✗ list]
Derivation Log complete — no undocumented inferences       │ [✓ / ✗ list]
DB Structural Alignment confirms field coverage            │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
BUSINESS CODE CHECKS (backend half)                        │ Status
───────────────────────────────────────────────────────────┼──────────────
Business Code excluded from POST/PUT request bodies        │ [✓ / ✗ list]
Business Code always present in GET/response DTOs          │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
LOCALIZATION CHECKS (backend half)                         │ Status
───────────────────────────────────────────────────────────┼──────────────
All RULE-IDs have Message-AR defined                       │ [✓ / ✗ list]
All API error responses: messageAr + messageEn             │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
SECURITY CHECKS (backend half)                             │ Status
───────────────────────────────────────────────────────────┼──────────────
Every API-ID serving a screen has permission declared      │ [✓ / ✗ list]
Every SCR-ID has SEC-BE block                              │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
QUERY REFERENCE CATALOG CHECKS                             │ Status
───────────────────────────────────────────────────────────┼──────────────
Every API-ID with DB operation has QR-ID in QRC            │ [✓ / ✗ list]
Every QR-ID has agent-reference warning label               │ [✓ / ✗ list]
No QR entry references ENUM for LOV fields                 │ [✓ / ✗ list]
No QR entry joins to lookups table                          │ [✓ / ✗ list]
Every QR-ID states exact sequence name (not placeholder)   │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
CROSS-MODULE DEPENDENCY CHECKS                             │ Status
───────────────────────────────────────────────────────────┼──────────────
All DEFERRED items (⏸) have XM-[MOD]-[N] + workarounds    │ [✓ / ✗ list]
All OQ references point to valid OQ-IDs in OQ Log          │ [✓ / ✗ list]
Inbound XM stubs use INBOUND-STUB notation (not TODO)      │ [✓ / ✗ list]
───────────────────────────────────────────────────────────┼──────────────
ARTIFACT BINDING CHECKS (Section 2A compliance)             │ Status
───────────────────────────────────────────────────────────┼──────────────
No placeholder [TABLE_NAME] in any phase                   │ [✓ / ✗ list]
No placeholder [LOOKUP_CODE] in any phase                  │ [✓ / ✗ list]
No placeholder [SEQ_NAME] — all sequences are exact         │ [✓ / ✗ list]
No RULE block shows "see SRS" — all text is inline         │ [✓ / ✗ list]
Every LOV-ID has exact LOOKUP_CODE bound from SRS           │ [✓ / ✗ list]
Every sequence name matches SEQ_[TABLE] from db-script      │ [✓ / ✗ list]
Every column name traces to a DBF-ID in DB Traceability     │ [✓ / ✗ list]
Every Message-AR is exact text — not paraphrase or summary  │ [✓ / ✗ list]
Business Code format stated explicitly (not "auto-gen")     │ [✓ / ✗ list]
DB Alignment Manifest: 5 columns only — no Column Name,     │ [✓ / ✗]
  DB Type, or SRS Source (CONTRACT-1 compliance)            │
───────────────────────────────────────────────────────────┼──────────────
PLAN COMPLETENESS CHECKS (backend)                         │ Status
───────────────────────────────────────────────────────────┼──────────────
Canonical architecture declared in PHASE CORE               │ [✓ / ✗]
Domain behavior placement declared in PHASE CORE            │ [✓ / ✗]
Entity inheritance declared per module type                 │ [✓ / ✗ list]
No orgUnitId in any DTO described in the plan                │ [✓ / ✗ list]
No audit fields in any CreateRequest/UpdateRequest           │ [✓ / ✗ list]
Error signaling strategy declared (LocalizedException)       │ [✓ / ✗]
All ERR-IDs have 4-registration points declared              │ [✓ / ✗ list]
All search operations declare ALLOWED_SORT_FIELDS            │ [✓ / ✗ list]
Empty search result → HTTP 200 declared (not HTTP 404)       │ [✓ / ✗ list]
Pre-deactivation usage check declared per deactivate op       │ [✓ / ✗ list]
Inbound XM stubs use INBOUND-STUB notation (not TODO)        │ [✓ / ✗ list]
═══════════════════════════════════════════════════════════════════════════
ALIGN-BE GATE RESULT: [PASSED ✓ / FAILED ✗ — list all ✗ items]
Auto-correction applied: [list DRV-IDs for corrections made / None]
═══════════════════════════════════════════════════════════════════════════
```

**Table 1 — Entity & Field Coverage:**
```
ENTITY-ID / FIELD-ID │ DATA+DOM │ SVC+API │ QR-ID    │ XM-ID (if any) │ Status
─────────────────────┼──────────┼─────────┼──────────┼────────────────┼───────
ENTITY-[MOD]-001     │ ✓        │ ✓       │ QR-[ID]  │ —              │ ✓
FIELD-0001           │ ✓        │ ✓       │ —        │ —              │ ✓
FIELD-0007           │ ✓        │ ✓       │ QR-[ID]  │ XM-[MOD]-002 ⏸│ ⏸
```

**Table 2 — Validations Coverage:**
```
RULE-ID      │ SVC+API │ ERR-ID  │ Status
─────────────┼─────────┼─────────┼───────
RULE-[MOD]-001│ ✓      │ ERR-0001│ ✓
```

**Table 3 — XM Dependency Gate:**
```
XM-ID        │ Type     │ Status    │ Blocks       │ Workaround
─────────────┼──────────┼───────────┼──────────────┼──────────────────
XM-[MOD]-001 │ HARD-FK  │ READY ✓  │ —            │ —
XM-[MOD]-002 │ SOFT-READ│ DEFERRED⏸│ FIELD-0007   │ [mock strategy]
```

---
═══════════════════════════════════════════════════════════════════
# SECTION 10 — ERROR CATALOG (CANONICAL)
═══════════════════════════════════════════════════════════════════

The Error Catalog is canonical and owned by this engine.
Produced during SVC+API phase. Referenced by F3 (frontend) and by the
Test Generation Engine's test-plans by ERR-ID only. Those consumers
never reproduce error message text.

```
ERROR CATALOG CANONICAL LOCATION RULE — CONTRACT-4 COMPLIANCE:

The Error Catalog table lives in ONE location in the execution plan.
Choose one at plan generation time and apply it consistently:

OPTION A (preferred): Table in SECTION A
  → SECTION A contains the full catalog table
  → SVC+API phase references it: "see SECTION A Error Catalog"
  → No duplicate table in SVC+API

OPTION B: Table in PHASE SVC+API
  → SECTION A is a navigation pointer ONLY:
    "Error Catalog canonical location: PHASE SVC+API — [section ref]"
  → SECTION A title must NOT include "canonical" — it is not the owner
  → No duplicate table in SECTION A

✗ FORBIDDEN: SECTION A declares itself "Canonical Reference"
  AND redirects to a table in SVC+API — this is a CONTRACT-4 violation
  that P4 will flag as DUPLICATE/MAJOR.
```

```
## ERROR CATALOG — [Module] — PLAN-ID: [xxx]
══════════════════════════════════════════════════════════════════════════════════
ERR-ID   │ RULE-ID      │ API-ID  │ HTTP │ Trigger                 │ Message-AR              │ Message-EN
─────────┼──────────────┼─────────┼──────┼─────────────────────────┼─────────────────────────┼─────────────────────
ERR-0001 │ RULE-[M]-001 │ API-001 │ 422  │ Delete linked record     │ لا يمكن حذف سجل مرتبط   │ Cannot delete linked record
ERR-0002 │ RULE-[M]-002 │ API-002 │ 409  │ Duplicate Business Code  │ الكود مستخدم مسبقاً      │ Business code already in use
ERR-0003 │ RULE-[M]-003 │ API-001 │ 400  │ Required field missing   │ الحقل إلزامي             │ Field is required
══════════════════════════════════════════════════════════════════════════════════
Total Errors: [N]
```

**Error Catalog rules:**
- Every RULE-ID producing a user-facing message MUST have an ERR-ID
- Message-AR: copied character-perfect from RULE-ID Message-AR in SRS
- No Message-AR in SRS → mark [→ OQ-XXX] and add to OQ Log
- F3 and the Test Generation Engine reference ERR-IDs only — never reproduce message text

---

═══════════════════════════════════════════════════════════════════
# SECTION 11 — QUERY REFERENCE CATALOG (FULL — AGENT REFERENCE)
═══════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════╗
║        QUERY REFERENCE CATALOG — [Module] — PLAN-ID: [xxx]      ║
╠══════════════════════════════════════════════════════════════════╣
║  ⚠ AGENT REFERENCE ONLY — ALL ENTRIES MUST BE REWRITTEN         ║
║  The implementation agent must rewrite every query using:        ║
║    • Actual JPA entity class names (not table names)             ║
║    • Actual mapped field property names (not column names)       ║
║    • Project's query strategy (JPQL / Criteria / QueryDSL)       ║
║    • Project's pagination framework (Pageable, etc.)            ║
║  These entries express INTENT — the agent provides the CODE      ║
╚══════════════════════════════════════════════════════════════════╝
```

[QR-ID entries generated during DATA+DOM and SVC+API phases appear here,
 following the format defined in Section 7.3 and 7.4]


═══════════════════════════════════════════════════════════════════
# SECTION 12 — REGISTRY UPDATE SCHEMA
═══════════════════════════════════════════════════════════════════

Generated at end of PASS 1 — after ALIGN-BE gate PASSED.

```
## REGISTRY UPDATE — [date]
────────────────────────────────────────────────────────────────
Source          : Project 3.1 — PASS 1 (Backend)
Feature Code    : [SRS feature code]
DBS-ID          : [DBS-ID of governing DB Script]
Plan ID         : [PLAN-ID]
────────────────────────────────────────────────────────────────
New Entities    : [list / None]
New Tables      : [list / None]
New Lookups     : [list / None]
New APIs        : [API-[MOD]-[N] list / None]
QR-IDs Created  : [QR-[MOD]-[N] list — count]
XM-IDs Open     : [DEFERRED XM-[MOD]-[N] list / None]
OQ-IDs Open     : [OQ-ID list / None]
Gate Status     : ALIGN-BE PASSED ✓
Next Action     : Trigger Project 4.1 — Backend Audit Gate
                  (Test Generation Engine runs separately, outside the
                   pipeline, whenever test artifacts are needed)
────────────────────────────────────────────────────────────────
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 13 — PASS 1 COMPLETION BLOCK
═══════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════╗
║           BACKEND EXECUTION PLAN — PASS 1 COMPLETE ✓              ║
╠═══════════════════════╦══════════════════════════════════════════╣
║ Plan Name             ║ [Full Name]                              ║
║ Plan ID               ║ PLAN-[MOD]-[SEQ]                        ║
║ Output                ║ backend-execution-plan-[MOD].md — Agent-Ready  ║
║ Phases Complete       ║ CORE✓ DATA+DOM✓ SVC+API✓ DOC✓ INT-C✓   ║
║                       ║ INT-R✓ SEC-BE✓ ALIGN-BE✓                ║
║ Open Questions        ║ [count / None]                           ║
║ XM DEFERRED           ║ [count / None — list XM-[MOD]-[N] IDs]  ║
║ Blocked Elements      ║ [count / None]                           ║
║ QR-IDs Generated      ║ [count — see Query Reference Catalog]    ║
║ Next Stage            ║ Project 4.1 (Backend Audit) → Backend    ║
║                       ║ implementation → api-doc-generator →      ║
║                       ║ GATE: BACKEND MODULE COMPLETE → PASS 2    ║
╠═══════════════════════╩══════════════════════════════════════════╣
║  ⚠ AGENT INSTRUCTIONS                                            ║
║  This plan is ready for implementation by an agent               ║
║  (Claude Code or equivalent).                                    ║
║                                                                  ║
║  Agent MUST:                                                      ║
║    1. Read the full plan before writing any code                 ║
║    2. Rewrite ALL Query Reference Catalog entries from scratch    ║
║       using actual project entity class and field names          ║
║    3. Follow the architectural policies declared in CORE phase   ║
║    4. Apply all Business Rules declared in DATA+DOM phase        ║
║    5. Never copy-paste QRC entries — treat as logic reference     ║
║    6. Implement security checks per SEC-BE specifications        ║
║    7. After implementation, run api-doc-generator to produce      ║
║       real API Docs — required before PASS 2 (frontend) can start║
║                                                                  ║
║  Tests are NOT part of this plan (P3 light). backend-test-plan-[MOD].md ║
║  is produced separately by the Test Generation Engine (outside    ║
║  the pipeline) from this plan.                                     ║
╚══════════════════════════════════════════════════════════════════╝
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 14 — GOVERNANCE BOUNDARY RULES
═══════════════════════════════════════════════════════════════════

**What this engine OWNS (canonical authority):**
- FIELD-ID namespace (assigned in DATA+DOM phase)
- ERR-ID namespace (assigned in SVC+API phase)
- QR-ID namespace (assigned in DATA+DOM and SVC+API phases)
- PLAN-ID assignment
- DB Alignment Manifest (FIELD-ID→DBF-ID binding)
- Error Catalog (canonical throughout the backend pipeline)
- Derivation Log (backend plan generation inferences)
- ALIGN-BE gate (backend internal self-consistency)
- INT Summary (XM execution register — EXTENDS P2's XM Register)
- Query Reference Catalog (agent-reference specifications)
- Module Governance Index (MGI) — Maintenance Authority (shared with
  PROJECT-3-FRONTEND-ENGINE.md — both update the same MGI)

**What this engine NO LONGER owns (v3.0 — moved to Test Generation Engine):**
- TC-BE-[MOD]-ID namespace → now owned by PROJECT-TEST-GENERATION-ENGINE.md
- backend-test-plan-[MOD].md → now produced by PROJECT-TEST-GENERATION-ENGINE.md
- test-execution-manifest.md → now produced by PROJECT-TEST-GENERATION-ENGINE.md

**What this engine REFERENCES (read-only — authoritative sources):**
- srs-[MOD].md — AUTHORITATIVE Functional Truth
- db-script-[MOD].md — AUTHORITATIVE Structural Truth
- DB Field Traceability Matrix (Project 2) — sourced by DBF-ID
- XM Register (Project 2) — EXTENDED in INT Summary; never re-assigned
- OQ Log (Project 1) — updated in place; never replaced
- XM-RESOLUTION-EVENT-PROTOCOL.md — RXE lifecycle governance

**What this engine does NOT touch:**
- ENTITY-ID, RULE-ID, LOV-ID, SCR-ID (owned by Project 1)
- DBF-ID, XM-ID structural definition (owned by Project 2)
- FIELD-ID(FE), TC-FE-[MOD]-ID (owned by Project 3.2 / Test Generation Engine)
- Finding IDs, audit verdicts (owned by Project 4.1 / 4.2)
- prd.md, flow-diagram-[MOD].md, ui-ux-spec-[MOD].md (owned by Project 0.5 / 2.5)

**What this engine does NOT produce:**
- Code of any kind (Java, TypeScript, SQL, shell)
- Executable queries or scripts
- Framework-specific annotations or decorators
- Any test artifact (test-plan, manifest, test class skeletons) —
  those belong to PROJECT-TEST-GENERATION-ENGINE.md
- Any frontend phase content (F1-F4) — see PROJECT-3-FRONTEND-ENGINE.md

---

═══════════════════════════════════════════════════════════════════
# SECTION 15 — AGENT HANDOFF SUMMARY (BACKEND)
═══════════════════════════════════════════════════════════════════

This section is the definitive instruction set for the backend
implementation agent.

## 15.1 What the Agent Receives

```
AGENT INPUT PACKAGE:
  ✓ backend-execution-plan-[MOD].md — this file (complete backend specification)
  ✓ srs-[MOD].md — functional requirements (read for clarification)
  ✓ db-script-[MOD].md — database DDL (actual table and column names)
  ✓ OQ Log — open questions the agent must not resolve unilaterally
```

## 15.2 Agent Reading Order

```
1. Read PLAN HEADER and PLAN INDEX — understand full scope
2. Read DB ALIGNMENT MANIFEST — understand FIELD-ID → DBF-ID mapping
3. Read OQ LOG — identify what is blocked and must not be implemented
4. Read PHASE CORE — understand architectural patterns to follow
5. Read PHASE DATA+DOM — entity structure and domain rules
6. Read PHASE SVC+API — API contracts and orchestration
7. Read PHASE DOC — internal contract self-check (informational only)
8. Read PHASE INT-C + INT-R — integration dependencies and status
9. Read PHASE SEC-BE — security and permission requirements
10. Read QUERY REFERENCE CATALOG — understand query intent per operation
11. Read ERROR CATALOG — use ERR-IDs in all error handling code
12. AFTER implementation is complete: run api-doc-generator to produce
    real API Docs — this is required before PASS 2 (frontend) begins

Note: test authoring is not driven from this plan. If tests are needed,
the Test Generation Engine (outside the pipeline) consumes this plan and
produces backend-test-plan-[MOD].md separately.
```

## 15.3 Agent Implementation Rules — Quick Reference

PROJECT-STANDARD rules are defined in full in **CORE phase (Section 8.1)**.
The Pre-Commit Checklist (Section 15.4) is the actionable version.

```
QRC — NEVER copy-paste QRC entries as production code
      Read intent → rewrite using actual project entity/field names
      Use SpecBuilder.build() + PageableBuilder.from() for search

DEFERRED XM — Implement mock strategy from INT-R phase
              Mark code: TODO: XM-[MOD]-[N] DEFERRED — replace when READY

OPEN QUESTIONS — Never implement a blocked element without OQ resolution
                 Mark code: TODO: OQ-[ID] — pending resolution
```

## 15.4 Backend Plan Completeness Self-Check (Before Closing)

```
BACKEND PLAN CHECKS:
[ ] PHASE CORE: canonical architecture declared (backend + frontend layers)
[ ] PHASE CORE: domain behavior placement declared
[ ] PHASE CORE: entity inheritance declared per module type
[ ] PHASE CORE: error signaling strategy declared
[ ] PHASE CORE: transaction scope declared
[ ] Every ENTITY-ID has complete field table with DBF-ID bindings
[ ] Every RULE-ID has full text (Statement + Message-AR + Message-EN)
[ ] Every RULE-ID has "Owned by: domain layer" declared
[ ] Every API-ID: Errors field covers all RULE-IDs in Validations
[ ] Every platform-standard ERR-ID (404/500): RULE-ID = PLATFORM-STD + DRV-ID
[ ] Every Repository deviation (EAGER/compound/native): DRV-ID in Derivation Log
[ ] No orgUnitId in any DTO shape described
[ ] No audit fields in any CreateRequest/UpdateRequest shape
[ ] All ERR-IDs registered in 4 places declared

CROSS-CUTTING CHECKS:
[ ] All inbound XM references use INBOUND-STUB notation (not TODO placeholders)
[ ] Derivation Log entries present for every non-obvious inference
[ ] ALIGN-BE gate passed ✓

STRUCTURAL SELF-CHECK (AMEND-P3-M, mandatory before declaring the plan complete):
[ ] Every phase intended has exactly one <!-- PHASE:{key}:START --> and
    one matching :END, and {key} is exactly one of the eight canonical
    keys in Section 8.0 — no near-misses (e.g. DATA+DOM instead of DATA-DOM)
[ ] Every API-ID / XM-ID mentioned anywhere in this plan has exactly
    ONE dedicated marker pair — none merged under a shared heading
    (PROJECT-3-REGISTRY.md 5.7.6 Rule 6), none missing
[ ] No section or heading label repeats anywhere in this document
[ ] Trailing content (this Agent Handoff Summary, this Self-Check) sits
    after <!-- PHASE:ALIGN-BE:END -->, with a heading that does not
    contain the word "PHASE" and carries no marker of its own
[ ] Every SUB threshold in Section 8.0 was checked while writing that
    phase — not retrofitted after the fact
[ ] Every SUB marker ID is written as {PHASE-KEY}-{LABEL}, never a
    bare label — check INT-C/INT-R module-name labels specifically:
    if this module both consumes FROM and resolves TO the same target
    module, confirm SUB:INT-C-{MODULE} and SUB:INT-R-{MODULE} are
    distinct, not the same bare SUB:{MODULE} repeated (AMEND-P3-N,
    PROJECT-3-REGISTRY.md Section 5.7.5)
If any item above fails, fix the plan now. Additionally run:
  python3 agent3_splitter.py --validate-markers --file backend-execution-plan-[MOD].md
— see STAGE-2-GOVERNANCE-TOOLS.md Section 3A. Treat any non-zero exit /
reported structural error from that tool as blocking, on top of this
manual checklist — the two are complementary, not either/or.
```

---

## DRIVE DEPENDENCY TABLE

Inputs required (Step A):
  srs-[MOD].md                       — [GOVERNANCE-ROOT]/[Platform]/[Module]/P1-SRS/srs-[MOD].md
  db-script-[MOD].md                 — [GOVERNANCE-ROOT]/[Platform]/[Module]/P2-DB/db-script-[MOD].md
  master-registry.md           — [GOVERNANCE-ROOT]/_registry/master-registry.md

Outputs published (Step C):
  backend-execution-plan-[MOD].md     — [GOVERNANCE-ROOT]/[Platform]/[Module]/P3.1-Backend-Exec/backend-execution-plan-[MOD].md

Note: backend-test-plan-[MOD].md and test-execution-manifest.md are NO LONGER
produced here. They are generated by the standalone Test Generation
Engine (PROJECT-TEST-GENERATION-ENGINE.md) from backend-execution-plan-[MOD].md,
and published under [GOVERNANCE-ROOT]/[Platform]/[Module]/TEST-GEN/.

---

*End of PROJECT-3-BACKEND-ENGINE.md (v3.0 — PASS 1 of Project 3, LIGHT)*
*Canonical owner: FIELD-ID | ERR-ID | QR-ID | PLAN-ID*
*             | DB Alignment Manifest | Error Catalog | Derivation Log*
*             | ALIGN-BE Gate | INT Summary*
*No longer owns: TC-BE-ID | backend-test-plan-[MOD].md | test-execution-manifest.md*
*             (moved to PROJECT-TEST-GENERATION-ENGINE.md — outside pipeline)*
*Companion   : PROJECT-3-REGISTRY.md (shared protocol)*
*              PROJECT-3-FRONTEND-ENGINE.md (PASS 2 — after this pass's*
*              implementation + GATE: BACKEND MODULE COMPLETE)*
*              PROJECT-TEST-GENERATION-ENGINE.md (standalone test engine)*
*Phase lifecycle (this file): CORE → DATA+DOM → SVC+API → DOC → INT-C*
*               → INT-R → SEC-BE → ALIGN-BE (test artifacts generated*
*               separately by the Test Generation Engine)*


---

# COMPLETION PROTOCOL — P3.1 Backend Execution Plan (AMEND-PIPELINE-V5 · GOVERNANCE-CONFIG §1D.4)

This section is MANDATORY at the end of every run of this engine. It is the
inline replacement for P-REG (retired) and P-ROUTER (demoted). Nothing here is
hardcoded: names come from §1D.2 / the tools' config.ARTIFACT_FILES.

```
STAGE KEY   : P3.1

1. ARTIFACT — emit, with the §1D.2 module-qualified names, then upload via the
   connector and capture {drive_file_id, drive_url} for each:
    backend-execution-plan-{mod}.md

2. REGISTRY (inline — the former P-REG step, same session):
    registry-exec-be-{mod}.md + project-registry update (API/ERR/QR ranges, ALIGN-BE)
   Upload it too. Never create a separate registry session.

3. LEDGER — record the links using the LEDGER-WRITE PROCEDURE (§1D.8:
   upload → capture id/webViewLink → fetch journey json → append/START/END
   in memory → re-create the file → trash the old copy). Append one row per
   uploaded file to [LEDGER] =
   [CTX]/[Module]/journey-{mod}.json (schema §1D.3):
    { engine: "P3.1", stage, filename, artifact, drive_file_id,
       drive_url, recorded_at, status: "UPLOADED" }
   If this is the FIRST engine of this version → also write START (open the
   version section; IFA versions carry change_set = CS-ID).
   If this is the LAST engine run for this version → write END (close it).

4. HANDOFF — print the NEXT-ENGINE INPUT block (§1D.5), filled in:
    NEXT ENGINE : P3.2 Frontend Execution Plan
    Read        : real API Docs (after backend implementation) · ui-ux-spec-{mod}.md · flow-diagram-{mod}.md · registry-exec-be-{mod}.md
    Do          : frontend-execution-plan-{mod}.md
    Gate        : GATE: BACKEND MODULE COMPLETE + GATE: UI SHELL (DELTA) COMPLETE (CONTRACT-12)
   The user pastes that block as the first message of the next project.
```


PATHS (rendered from config.DRIVE_LAYOUT — GOVERNANCE-CONFIG §1E; never edit by hand)
  [MROOT] = [CTX]/[Module]/          (v1)   or   [CTX]/[Module]/v[N]/   (IFA, N ≥ 2)
  WRITES TO (this engine is the ONLY writer of these folders):
    [MROOT]/P3.1-Backend-Exec/   → backend-execution-plan-[mod].md, registry-exec-be-[mod].md
  READS FROM:
    [MROOT]/P0-Platform/   ← platform-summary.md, module-registry-[mod].md, business-policies-[mod].md
    [MROOT]/P1-SRS/   ← srs-[mod].md, registry-srs-[mod].md
    [MROOT]/P2-DB/   ← db-script-[mod].md, registry-db-[mod].md
    [MROOT]/P2.5-UIUX/   ← flow-diagram-[mod].md, ui-ux-spec-[mod].md
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
