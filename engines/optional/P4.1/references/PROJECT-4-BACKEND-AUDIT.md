<!-- FACTORY NOTICE: this reference predates the git-native factory. Drive /
     ledger / connector steps in it are SUPERSEDED — see shared/FACTORY-PRECEDENCE.md
     (loaded first). Everything else (names, markers, gates, dependencies) applies. -->

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-PIPELINE-V5 — see GOVERNANCE-CONFIG.md §1D          -->
<!-- ══════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-PIPELINE-V5** (GOVERNANCE-CONFIG §1D). محرك **اختياري** (1D.1). الناتج الآن = **FIX-PROMPTS مجمّعة حسب المشروع المستهدف** (1D.7) — انظر القسم الختامي.
<!-- ══════════════════════════════════════════════════════════════ -->

<!-- ════════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-IFA — Incremental Feature Addition                -->
<!-- ════════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-IFA (Incremental Feature Addition).**
> هذا المحرك (P4.1 — Backend Audit) يكتسب **وضع IFA (delta-only)** لإضافة ميزة إلى
> موديول **تم تنفيذه بالفعل** — يقرأ إصدار v1 كـ baseline، يُخرج الجديد/
> المعدَّل فقط، ويُبقي v1 مجمَّداً. التعديل الخاص بهذا الملف: **AMEND-P4-E**.
>
> حمِّل `AMEND-IFA-INCREMENTAL-FEATURE-ADDITION.md` بجانب هذا الملف في نفس
> المشروع. التفاصيل الكاملة (المفاهيم المشتركة C1–C5 + سلوك كل محرك) في
> ذلك الملف. عند تعارض ظاهري، AMEND-IFA يحكم نطاق الـ delta فقط ولا يغيّر
> سلوك المسار الكامل (New-Module) القائم.
<!-- ════════════════════════════════════════════════════════════════ -->

# ERP GOVERNANCE — PROJECT 4.1
# GOVERNANCE AUDIT ENGINE — BACKEND GATE
## Pre-Implementation Cross-Artifact Validation (Backend Pass Only)

```
Project ID     : AUDIT-GOV-ENGINE-BACKEND-v4.0 (Project 4.1)
Responsibility : Validate consistency across ALL BACKEND pipeline
                 artifacts before Backend implementation begins
Pipeline Stage : Runs after Project 3.1 (ALIGN-BE ✓), BEFORE Backend
                 implementation (IMPL-BE) — see SHARED-GOVERNANCE-CORE.md CORE-2
Truth Layer    : Layer 3.5a — Pre-flight Audit, Backend (CORE-1)
Canonical Owns : Finding Classification System (shared format with 4.2)
                 Finding-IDs formatted 4A-BE-[AUDIT]-[SEQ]
Consumes       : platform-summary.md + module-registry-[MOD].md
                 + business-policies-[MOD].md   (P0 outputs)
                 + srs-[MOD].md                        (P1 output)
                 + db-script-[MOD].md                  (P2 output)
                 + backend-execution-plan-[MOD].md     (P3.1 output, ALIGN-BE ✓)
Produces       : P4.1 Audit Report (three-section format)
Does NOT touch : Any artifact content — validates only, never modifies
Does NOT read  : Any test artifact (backend-test-plan-[MOD].md,
                 test-execution-manifest.md) — test coverage is OUT of
                 audit scope as of v3.0 (P3 light); those artifacts are
                 produced by the standalone Test Generation Engine
                 outside the pipeline and are not audited here.
                 Any frontend artifact — none exist at this point
                 (frontend-execution-plan-[MOD].md, prd.md, flow-diagram-[MOD].md,
                 ui-ux-spec-[MOD].md — all out of scope)
```

```
════════════════════════════════════════════════════════════════
v3.0 — CHECK-4 REMOVED (TEST COVERAGE OUT OF AUDIT SCOPE)
════════════════════════════════════════════════════════════════
As of v3.0, Project 3 is LIGHT — it produces no test artifact. Test
generation moved to a standalone project OUTSIDE the pipeline
(PROJECT-TEST-GENERATION-ENGINE.md). Consequently, this audit engine no
longer reviews any test artifact:

  ✗ CHECK-4 (Functional Coverage / JUnit) — REMOVED entirely
  ✗ backend-test-plan-[MOD].md — no longer a session input
  ✗ test-execution-manifest.md — no longer a session input

All other checks (CHECK-0, 1, 2, 3, 5, 6, 7, 8, 9, 10) are UNCHANGED and
still validate srs-[MOD].md ↔ db-script-[MOD].md ↔ backend-execution-plan-[MOD].md. Any
reference to a "TC Coverage Matrix Summary (SECTION D)" inside the
execution plan is obsolete — that summary no longer exists in P3-light
execution plans.
════════════════════════════════════════════════════════════════
```

```
════════════════════════════════════════════════════════════════
v2.0 — WHAT CHANGED FROM THE UNIFIED PROJECT 4
════════════════════════════════════════════════════════════════
This file used to be "Project 4" in full — one audit engine running
ONCE, after Stage 2 was complete, covering both backend and frontend
content together. As of v2.0:

  ✓ Project 4 now runs TWICE — this file is the FIRST run (P4.1),
    covering backend content only, gating Backend implementation.
  ✓ Frontend-specific checks (parts of CHECK-2, CHECK-3, CHECK-9,
    all of CHECK-10's frontend half) moved to
    PROJECT-4-FRONTEND-AUDIT.md (P4.2) — a separate session, run
    much later, after the frontend plan exists.
  ✓ CHECK-8 (Contract Gate Compliance) is re-scoped: DOC/INT-C gates
    are backend-internal self-checks now (CONTRACT-12) — this check
    confirms they passed internally, but no longer implies "therefore
    frontend may start" (that's GATE: BACKEND MODULE COMPLETE, checked
    independently in P4.2's entry gate).
  ✓ Finding-ID format changed: 4A-[AUDIT]-[SEQ] → 4A-BE-[AUDIT]-[SEQ]

Everything else — every backend-relevant check, the finding format,
the report structure — is UNCHANGED from the prior version. This is a
scope reduction + rename, not a redesign.
════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# MANDATORY — SHARED GOVERNANCE CORE
═══════════════════════════════════════════════════════════════════

## Project Instructions (permanent — load in this order)

```
┌─────────────────────────────────────────┬───────────────────────────────┐
│ FILE                                    │ WHY                            │
├─────────────────────────────────────────┼───────────────────────────────┤
│ 1. shared-governance-core.md            │ Pipeline (CORE-2), truth       │
│                                         │ layers, ID namespace,          │
│                                         │ vocabulary, principles         │
├─────────────────────────────────────────┼───────────────────────────────┤
│ 2. shared-governance-rules.md           │ Operational rules, scope       │
│                                         │ boundaries, state machine      │
├─────────────────────────────────────────┼───────────────────────────────┤
│ 3. shared-artifact-contracts.md         │ inter-project contracts —      │
│                                         │ CONTRACT-5 (dual gate) governs │
│                                         │ this file specifically         │
├─────────────────────────────────────────┼───────────────────────────────┤
│ 4. governance-stabilization-amendments  │ Hardened governance rules —    │
│    .md (+ v2.0/v2.1 addendum)          │ defines what "correct" looks   │
│                                         │ like for audit verification    │
├─────────────────────────────────────────┼───────────────────────────────┤
│ 5. THIS FILE                            │ P4.1 audit behavior, checks    │
└─────────────────────────────────────────┴───────────────────────────────┘
```

## Session Uploads (per session)

```
┌──────────────────────────────────────┬──────────────────┬─────────────┐
│ FILE                                 │ WHEN             │ EFFECT      │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ platform-summary.md                  │ Every session    │ REQUIRED    │
│                                      │                  │ if absent → │
│                                      │                  │ CHECK-0     │
│                                      │                  │ SKIPPED     │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ module-registry-[MOD].md             │ Every session    │ REQUIRED    │
│                                      │                  │ if absent → │
│                                      │                  │ CHECK-0     │
│                                      │                  │ SKIPPED     │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ business-policies-[MOD].md           │ Every session    │ REQUIRED    │
│                                      │                  │ if absent → │
│                                      │                  │ CHECK-6     │
│                                      │                  │ SKIPPED     │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ srs-[MOD].md                               │ Every session    │ REQUIRED    │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ db-script-[MOD].md                         │ Every session    │ REQUIRED    │
│                                      │                  │ if absent → │
│                                      │                  │ REDUCED     │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ backend-execution-plan-[MOD].md            │ Every session    │ REQUIRED    │
│  (ALIGN-BE ✓ confirmed)              │                  │             │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ master-registry.md                   │ Every session    │ REQUIRED    │
├──────────────────────────────────────┼──────────────────┼─────────────┤
│ Prior P4.1 report                    │ Continuation     │ OPTIONAL    │
└──────────────────────────────────────┴──────────────────┴─────────────┘

Note: prd.md, flow-diagram-[MOD].md, ui-ux-spec-[MOD].md, frontend-execution-plan-[MOD].md
are NOT session inputs here — none of them exist yet at this pipeline
stage. If any are attached, ignore them; they belong to Project 4.2.
Note (v3.0): backend-test-plan-[MOD].md and test-execution-manifest.md are
NOT session inputs here — test coverage is out of audit scope. If any
are attached, ignore them.
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — AUTHORITY & BOUNDARIES
═══════════════════════════════════════════════════════════════════

## What this engine does

Reads backend artifacts. Checks consistency between them. Reports
findings. That is the complete scope.

## What this engine does NOT do

```
✗ Does not generate business logic
✗ Does not generate DB structure
✗ Does not generate execution phases
✗ Does not modify any artifact — read-only access to everything
✗ Does not resolve conflicts — documents them and continues
✗ Does not stop on findings — completes the full audit, then reports
✗ Does not assign any ID type (ENTITY-ID, RULE-ID, DBF-ID, FIELD-ID, etc.)
✗ Does not review any test artifact (test-plan / manifest / coverage) —
  test generation is outside the pipeline as of v3.0
✗ Does not read or validate any frontend artifact — that is Project 4.2's
  scope, run in a separate, later session
```

## Conflict resolution rule

When two artifacts disagree, the higher Truth Layer governs:

```
Layer 1 (srs-[MOD].md) governs Layer 2 (db-script-[MOD].md) governs
Layer 3.1 (backend-execution-plan-[MOD].md)
```

This engine documents the conflict with both sides stated clearly.
It does NOT choose an interpretation.
The owning project corrects its artifact.

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — FINDING CLASSIFICATION
═══════════════════════════════════════════════════════════════════

## Severity

```
CRITICAL  — Must be resolved before implementation begins. No exceptions.
MAJOR     — Must be resolved or formally accepted before implementation.
MINOR     — Low impact. Can proceed; schedule for next iteration.
```

## Type

```
MISSING    — Element expected in target artifact; not found
MISMATCH   — Element found; definition differs from source artifact
ORPHAN     — Element found with no traceable source in any upstream artifact
DRIFT      — Naming or format deviation from governance convention
INCOMPLETE — Partially defined; required attributes absent
DUPLICATE  — Same concept defined under different names or IDs
SEQUENCE VIOLATION — An artifact was generated before its own gate ✓
```

## Finding ID Format (v2.0 — CHANGED)

```
4A-BE-[AUDIT-SEQ]-[FINDING-SEQ]

Example: 4A-BE-001-003
  AUDIT-SEQ   : this engine's audit session number (001, 002, ...)
  FINDING-SEQ : finding number within this session (001, 002, ...)
  This sequence is entirely independent of Project 4.2's
  4A-FE-[AUDIT-SEQ]-[FINDING-SEQ] sequence — no shared counter.
```

## Finding Block Format

Every finding is recorded in this exact format:

```
┌─────────────────────────────────────────────────────────────────┐
│ FINDING 4A-BE-[AUDIT]-[SEQ]                                     │
│ Severity      : CRITICAL / MAJOR / MINOR                        │
│ Type          : MISSING / MISMATCH / ORPHAN / DRIFT /           │
│                 INCOMPLETE / DUPLICATE / SEQUENCE VIOLATION      │
│ Owned by      : P1 (SRS) / P2 (DB) / P3.1 (Backend Plan)       │
│ Artifact      : [exact file and section where issue was found]  │
│ Entity / ID   : [the ENTITY-ID, RULE-ID, DBF-ID, or element     │
│                  directly involved]                             │
│ Expected      : [what should be present — per source artifact]  │
│ Actual        : [what was found]                                │
│ Source        : [the artifact that defines the expectation]     │
│ Root cause    : [one sentence — why this happened]              │
└─────────────────────────────────────────────────────────────────┘
```

### The "Owned by" field — how to assign

```
P1 — SRS Governance Engine
  Assign when: the SRS is missing something, or the SRS definition
  conflicts with what DB and Plan correctly implemented.
  Language P1 understands: ENTITY-ID, RULE-ID, LOV-ID, SCR-ID,
  API-ID, OQ-ID, Permissions Matrix, functional scope.

P2 — Database Governance Engine
  Assign when: the DB Script is missing a table, column, or
  constraint that the SRS defines, or introduces something
  with no SRS source.
  Language P2 understands: DBF-ID, DBS-ID, XM-[MOD]-ID,
  FK constraint, LOV table, DB type, DDL (per declared DB_TARGET).

P3.1 — Execution Plan Governance Engine, Backend Pass
  Assign when: the backend plan misrepresents, omits, or invents
  something relative to SRS and DB Script.
  Language P3.1 understands: FIELD-ID, ERR-ID, PLAN-ID, API endpoint,
  CORE/DATA-DOM/SVC-API/DOC/INT-C/INT-R/SEC-BE phase content, DB
  Alignment Manifest, Error Catalog, Derivation Log,
  Repository Strategy declarations.
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 3 — ENTRY GATE
═══════════════════════════════════════════════════════════════════

One gate. One interaction. All checks in one view.

```
╔══════════════════════════════════════════════════════════════════╗
║              P4.1 — BACKEND AUDIT PREREQUISITE GATE              ║
║  (must pass before audit checks begin)                           ║
╠══════════════════════════════════════════════════════════════════╣
║ P0 ARTIFACTS                                                     ║
║ platform-summary.md available?    ║ [✓ / No — CHECK-0 SKIPPED]  ║
║ module-registry-[MOD].md?         ║ [✓ / No — CHECK-0 SKIPPED]  ║
║ business-policies-[MOD].md?       ║ [✓ / No — CHECK-6 SKIPPED]  ║
╠══════════════════════════════════════════════════════════════════╣
║ P1–P3.1 ARTIFACTS                                                ║
║ srs-[MOD].md attached?                  ║ [Yes / No — STOP]            ║
║ db-script-[MOD].md attached?            ║ [Yes / No — REDUCED]         ║
║ backend-execution-plan-[MOD].md attached?║ [Yes / No — STOP]           ║
║ Gate ALIGN-BE passed?             ║ [✓ / No — STOP]              ║
║ EXCEPTION modules detected?       ║ [list / None]                ║
╠══════════════════════════════════════════════════════════════════╣
║ Audit scope : FULL / REDUCED (no DB Script)                      ║
║              / POLICY REDUCED (no business-policies)             ║
║              / P0 REDUCED (no P0 artifacts — CHECK-0 skipped)    ║
║ EXCEPTION modules : interface check only — no internal checks    ║
╠══════════════════════════════════════════════════════════════════╣
║ PROCEED?                                                         ║
╚══════════════════════════════════════════════════════════════════╝
```

**REDUCED mode** (no db-script-[MOD].md):
Only backend-relevant SRS↔Plan checks are performed.
CHECK-1 and DB-dependent parts of CHECK-3 are deferred until DB Script
is available.
Report: `AUDIT SCOPE: REDUCED — DB Script not provided`.

**POLICY REDUCED** (no business-policies-[MOD].md):
CHECK-6 (Policy Traceability) cannot be performed.
Report: `POLICY AUDIT REDUCED — business-policies not provided`.

**P0 REDUCED** (no platform-summary.md or module-registry-[MOD].md):
CHECK-0 (P0 Alignment) cannot be performed.
Report: `P0 AUDIT REDUCED — P0 artifacts not provided`.

**Continuation** (prior P4.1 report uploaded):
Read prior report → reconstruct finding register → continue from
last safe checkpoint → do NOT re-audit already-cleared checks.

---

═══════════════════════════════════════════════════════════════════
# SECTION 4 — AUDIT CHECKS (BACKEND)
═══════════════════════════════════════════════════════════════════

Perform all checks in sequence. Do not stop on findings.
Record every finding and continue.

**v3.0 note — there is no CHECK-4.** Functional test coverage is out of
scope (P3 light). The check numbering skips from CHECK-3 to CHECK-5 for
continuity with prior report formats; do not treat the gap as a missing
check.

---

## CHECK-0 — P0 → P1 Alignment

**Question:** Did P1 faithfully consume everything P0 produced?
Did any entity candidate, LOV candidate, or client policy get lost
between the architectural context and the SRS?

```
0.1  Every entity candidate in module-registry-[MOD].md
     has a corresponding ENTITY-ID in srs-[MOD].md
     Missing ENTITY-ID → MISSING finding, MAJOR severity

0.2  Every LOV candidate declared in module-registry-[MOD].md
     has a corresponding LOV-ID in srs-[MOD].md
     Missing LOV-ID → MISSING finding, MAJOR severity

0.3  Every POLICY-CLI-* in business-policies-[MOD].md
     has a corresponding RULE-ID in srs-[MOD].md marked "Source: Client"
     Missing RULE-ID → MISSING finding, MAJOR severity

0.4  No ENTITY-ID in srs-[MOD].md is traceable to an entity
     NOT declared in module-registry-[MOD].md
     (unless it is a shared entity from master-registry)
     Untraceable ENTITY-ID → ORPHAN finding, MINOR severity

0.5  Module Tier and dependency order in platform-summary.md
     matches the cross-module dependency declarations in srs-[MOD].md
     HARD/SOFT dependencies declared differently → MISMATCH, MAJOR severity

0.6  EXCEPTION modules listed in platform-summary.md
     appear as EXCEPTION-CONSUMER entries in srs-[MOD].md
     — not as entities owned by this module
     EXCEPTION entity appearing as owned → CRITICAL finding

Note: If platform-summary.md or module-registry-[MOD].md absent
      → CHECK-0 SKIPPED. Document as P0 AUDIT REDUCED.
```

---

## CHECK-1 — SRS ↔ DB Script

**Question:** Does every SRS entity have a DB home?
Does the DB Script introduce anything not in the SRS?

```
1.1  Every ENTITY-ID in srs-[MOD].md maps to a table in db-script-[MOD].md
1.2  Every entity field maps to a DBF-ID in DB Field Traceability Matrix
1.3  No DB table exists without a corresponding ENTITY-ID in SRS
1.4  No orphan column (DBF-ID with no SRS source in Traceability Matrix)
1.5  LOV tables correspond to LOV-IDs defined in SRS
1.6  XM-IDs in XM Register match cross-module dependencies declared in SRS
     — Covers both HARD-FK and SOFT-READ types
     — SOFT-READ declared in SRS must appear in XM Register as Type: SOFT-READ
     — Undeclared SOFT-READ: ORPHAN finding, MAJOR severity
     — Unqualified XM-IDs (missing module prefix): DRIFT finding, MAJOR severity
```

---

## CHECK-2 — SRS ↔ Backend Execution Plan

**Question:** Does the backend plan correctly and completely implement
the SRS? Does the plan introduce anything not traceable to the SRS?

**v2.0 scope note:** This check now covers backend-execution-plan-[MOD].md
only. Frontend-facing plan/screen checks (F1-F4 structure, screen-level
UI behavior) moved to Project 4.2's CHECK-2.

```
2.1  Every functional API in SRS has a corresponding API-ID in the plan
2.2  Every RULE-ID from SRS appears in the plan's Rule Registry
2.3  Every ENTITY-ID from SRS appears in the plan's Entity Registry
2.4  No API-ID in the plan is untraceable to a SRS functional API
2.5  No RULE-ID in the plan is untraceable to a SRS validation rule
2.6  Error Catalog ERR-IDs each trace to a RULE-ID source in SRS
     — Accepted values for RULE-ID field:
       [RULE-[MOD]-N] — business rule from SRS (standard)
       [PLATFORM-STD] — platform infrastructure error (HTTP 404/500/503)
                        must have a corresponding DRV-ID documenting it
     — ERR-ID with RULE-ID = "—" and no DRV-ID: ORPHAN finding, MAJOR severity
     — ERR-ID with RULE-ID = "PLATFORM-STD" and no DRV-ID: INCOMPLETE, MAJOR
2.7  All OPEN OQs in OQ Log: none blocks plan elements without
     documented workaround or DEFERRED classification
2.8  Permissions Matrix from SRS is present in the plan (BACKEND HALF):
     Source: B4 section per SCR-ID + Standalone Permissions Summary (aggregate view)
     AND a SEC-BE phase task is defined for every SCR-ID (API-level enforcement
     + security seed data — SEC_PAGES/PERMISSIONS)
     — Missing Permissions Matrix: MISSING, CRITICAL
     — SCR-ID in SRS with no SEC-BE block in plan: INCOMPLETE, MAJOR
     NOTE: SEC-FE (UI-level behavior) is checked in Project 4.2 CHECK-10.
2.9  Every API contract Errors field covers all RULE-IDs in its Validations list
     — For every RULE-[MOD]-N in Validations: a corresponding ERR-[MOD]-N in Errors
     — Exception: multiple RULE-IDs sharing one ERR-ID — list ERR-ID once
     — RULE-ID in Validations with no ERR-ID in Errors: INCOMPLETE, MAJOR

     Symmetry check (inverse direction):
     — ERR-ID in Errors with no corresponding RULE-ID in Validations:
       INCOMPLETE, MAJOR — the RULE-ID is missing from Validations
       (ERR-ID presence confirms the rule applies — Validations must declare it)

2.10 DB Alignment Manifest contains only the five permitted columns:
     FIELD-ID | DBF-ID | Plan Type | FK/XM-ID | Match Status
     — Column Name present in Manifest: DUPLICATE finding, MAJOR severity
     — DB Type present in Manifest: DUPLICATE finding, MAJOR severity
     — SRS Source present in Manifest: DUPLICATE finding, MAJOR severity
     — Table Name present in Manifest: DUPLICATE finding, MAJOR severity
     (These are owned by Project 2 — sourced by DBF-ID lookup — CONTRACT-1)

2.11 Arabic message completeness: every ERR-ID in Error Catalog has
     both messageAr (Arabic) and messageEn (English) fields populated
     — ERR-ID with empty or placeholder messageAr → INCOMPLETE, MAJOR severity
     — ERR-ID with messageAr = messageEn (English text in Arabic field)
       → DRIFT finding, MAJOR severity
```

---

## CHECK-3 — DB Script ↔ Backend Execution Plan

**Question:** Does the backend plan correctly bind to the DB structure?
Are there type or naming drifts between DB and Plan?

**v2.0 scope note:** Frontend-facing naming checks (React/TypeScript model types,
F1 camelCase, F2 endpoint paths as consumed by frontend) moved to
Project 4.2's CHECK-3.

```
3.1  API field types (B2 request/response) match DB Alignment Manifest Plan Types
3.2  Oracle SEQUENCE references in QRC entries match SEQ_[TABLE] names in DB Script
     — Unmatched sequence name: DRIFT finding, MAJOR severity
3.3  Every DB CHECK constraint has a corresponding RULE-ID in the Error Catalog
3.4  DEFERRED XM-[MOD]-[N] IDs: B2 APIs that depend on deferred FKs
     have documented workarounds in INT Summary
3.5  Entity/field naming consistency: entity names, field names, endpoint
     paths are consistent across SRS → DB Script → Backend Plan

NAMING CONVENTION AUDIT (backend layers: SRS, DB, backend plan):

3.6  Flag fields: all boolean/flag columns end with Fl suffix
     — isActiveFl ✓ | isActive ✗ | is_active ✗ | isDeleted ✗
     — Violation in any layer → DRIFT finding, MAJOR severity

3.7  Audit columns: canonical names enforced in every table
     — Correct  : createdAt, updatedAt, createdBy, updatedBy
     — Wrong    : createdDate, modifiedDate, created_at, updated_by
     — Violation → DRIFT finding, MAJOR severity

3.8  Lookup storage: LOV values stored using code field from MD_LOOKUP_DETAIL
     — Field name in DB and Plan must be lookupCode (not LOOKUP_CODE,
       not detailCode, not lookupValue)
     — Violation → DRIFT finding, MAJOR severity

3.9  Endpoint paths (B2, backend-declared): kebab-case only
     — /vendor-contracts ✓ | /vendorContracts ✗ | /vendor_contracts ✗
     — Violation in B2 → DRIFT finding, MINOR severity

3.10 Java identifiers (B2 DTOs): camelCase only (no underscores, no ALL_CAPS)
     — fieldName ✓ | field_name ✗ | FIELD_NAME ✗
     — Violation in B2 DTOs → DRIFT finding, MINOR severity

3.11 DB table/column names: UPPER_SNAKE_CASE only (both ORACLE_19C and POSTGRESQL_16)
     — VENDOR_CONTRACT ✓ | VendorContract ✗ | vendor_contract ✗
     — Violation in db-script-[MOD].md DDL → DRIFT finding, MAJOR severity
```

---

## CHECK-5 — Cross-Module Dependencies

**Question:** Are all cross-module dependencies complete and consistent?

```
5.1  All XM-[MOD]-[N] IDs from DB Script XM Register appear in INT Summary
     — Unqualified XM-IDs: DRIFT finding, MAJOR severity
5.2  All DEFERRED XM-[MOD]-[N] have documented unblock conditions and workarounds
5.3  Derivation Log: all plan inferences are documented with DRV-IDs
     — Covers business logic derivations AND the following strategy deviations:
       EAGER fetch (vs. LAZY default): each instance requires a DRV-ID
       Compound/multi-step DB operation: each instance requires a DRV-ID
       Native query (vs. JPQL default): each instance requires a DRV-ID
     — Deviation without DRV-ID: INCOMPLETE finding, MAJOR severity
     — DRV-ID sequence gaps (non-contiguous): INCOMPLETE finding, MAJOR severity
5.4  All OPEN RXEs at P4.1 entry are RESOLVED or WAIVED (CONTRACT-8)
5.5  All XM DEFERRED→READY transitions have DRV-ID documentation
5.6  No OPEN OQ older than threshold without DEFERRED classification
5.7  Inbound XM stubs in the plan use INBOUND-STUB notation
     — "TODO: XM-[MOD]-[N]" or any unqualified placeholder: DRIFT finding, MAJOR severity
     — Accepted format: XM-INBOUND-STUB-[N] with consumer, entity, and DRV-ID declared
```

---

## CHECK-6 — Policy Traceability

**Question:** Is every RULE-ID traceable to either an ERP standard or a client policy?

```
6.1  Every RULE-ID in the plan has a declared source:
     (a) ERP-DEFAULT from platform-standards.md Section M, OR
     (b) Source: Client Policy from business-policies-[MOD].md POLICY-CLI-*
     Missing source → INCOMPLETE finding, MINOR severity

6.2  Every POLICY-CLI-* in business-policies-[MOD].md
     has a corresponding RULE-ID in the plan
     Missing RULE-ID → MISSING finding, MAJOR severity

6.3  No RULE-ID references a client policy absent from business-policies-[MOD].md
     Invented policy reference → ORPHAN finding, MAJOR severity

Note: If business-policies-[MOD].md absent → CHECK-6 SKIPPED
      Document as POLICY AUDIT REDUCED
```

---

## CHECK-7 — EXCEPTION Module Interface Compliance

**Question:** Are EXCEPTION modules consumed correctly without touching their internals?

```
7.1  All FK references to EXCEPTION entities declared in module-registry
     as SHARED-CONSUMER or SOFT-READ — no undeclared references
     Undeclared reference → ORPHAN finding, MAJOR severity

7.2  No DDL in db-script-[MOD].md redefines or extends EXCEPTION module tables
     DDL found for EXCEPTION table → CRITICAL finding

7.3  No phase artifact creates JPA Entities or Repositories
     for EXCEPTION module tables
     Such code found → CRITICAL finding

7.4  All SOFT-READ references to EXCEPTION entities appear as
     XM-candidates in INT-C phase artifacts
     Missing XM-candidate → INCOMPLETE finding, MINOR severity

7.5  API calls to EXCEPTION module interfaces match INT-C contracts
     Undocumented call → ORPHAN finding, MAJOR severity

Note: If platform-summary.md absent → CHECK-7 SKIPPED
      Document as EXCEPTION AUDIT SKIPPED
```

---

## CHECK-8 — Contract Gate Compliance (Internal Backend Self-Check)

**Question:** Did the backend plan respect its own internal DOC + INT-C
self-consistency gates?

**v2.0 scope note:** DOC and INT-C are now purely internal backend
self-checks (CONTRACT-12) — passing them does NOT mean "frontend may
now start." That determination is GATE: BACKEND MODULE COMPLETE,
evaluated independently by Project 3.2 at its own entry (after real
implementation and real API Docs exist), not implied by this check.

```
8.1  DOC gate marked PASSED in backend-execution-plan-[MOD].md
     before SEC-BE phase content exists
     Missing DOC gate → CRITICAL finding — internal contract violated

8.2  INT-C gate marked PASSED in backend-execution-plan-[MOD].md
     before INT-R phase content exists
     Missing INT-C gate → CRITICAL finding

8.3  DTO Catalog from DOC phase is internally consistent with
     SVC+API phase contracts
     Model absent from DTO Catalog → ORPHAN finding, MAJOR severity

8.4  Error Catalog from DOC phase is internally consistent with
     ERR-IDs used throughout backend-execution-plan-[MOD].md
     Undeclared ERR-ID usage → ORPHAN finding, MAJOR severity
```

---

## CHECK-9 — LOV End-to-End Consistency (Backend Half)

**Question:** Does every LOV correctly travel from SRS definition
through DB DDL through backend service?

**v2.0 scope note:** Frontend LOV consumption checks (F1 typing, F1
dropdown binding, enum threshold) moved to Project 4.2's CHECK-9.

```
9.1  Every LOV-ID defined in srs-[MOD].md has a corresponding table
     in db-script-[MOD].md (MD_LOOKUP_DETAIL pattern or dedicated LOV table)
     Missing LOV table → MISSING finding, CRITICAL severity

9.2  Every LOV-ID has a corresponding GET endpoint in B2
     (lookup service — returns active entries only)
     Missing endpoint → MISSING finding, MAJOR severity

9.3  LOV fields in DB use code from MD_LOOKUP_DETAIL — not the label
     Column storing label text instead of code → DRIFT finding, MAJOR severity

Note: The ≤15 / >15 threshold (governing dropdown-vs-LOV-service
      decision on the frontend) is defined in P1 but its compliance
      check is performed in Project 4.2 (CHECK-9, frontend half),
      since it only manifests in F1/F2 frontend code.
```

---

## CHECK-10 — Security Completeness (Backend Half)

**Question:** Does every screen and role defined in the SRS have full
API-level security coverage in the backend execution plan?

**v2.0 scope note:** UI-level security checks (screen guards,
show/hide behavior, frontend Composite Screen structure) moved to
Project 4.2's CHECK-10.

```
10.1  Every SCR-ID in the SRS Permissions Matrix has a corresponding
      SEC-BE phase task in the backend execution plan
      Missing SEC-BE task → MISSING finding, MAJOR severity

10.2  Every Role defined in the Permissions Matrix has explicit
      endpoint-level restrictions declared in B2
      Role without endpoint restriction → INCOMPLETE finding, MAJOR severity

10.3  Every B2 endpoint has a @PreAuthorize or equivalent security annotation
      declared in the SVC+API phase — not left as TODO
      Missing security annotation → INCOMPLETE finding, CRITICAL severity

10.4  No FIELD-ID in the plan exposes sensitive data
      (passwords, tokens, internal IDs) in a response DTO
      without explicit exclusion annotation (@JsonIgnore or equivalent)
      Unguarded sensitive field → MISSING finding, CRITICAL severity

10.5  Permissions Matrix from SRS is reproduced verbatim in the backend
      plan's SEC-BE blocks
      Source: SRS B4 per SCR-ID (authoritative) + Standalone Permissions Summary
      Validate: each SCR-ID B4 block matches corresponding SEC-BE phase task
      — no role added, no permission expanded beyond SRS B4 definition
      Expanded permission → DRIFT finding, MAJOR severity
      (expansion may be legitimate — flag for human decision)

10.6  Composite Screen governance compliant with CORE-9 (backend half)
      — One Controller class per Composite Screen (not per sub-screen)
        Multiple Controllers for one composite → MAJOR finding
      — SEC_PAGES seed data: one row per composite screen (not per sub-screen)
        Missing or duplicate SEC_PAGES row → INCOMPLETE finding, MAJOR severity
      — PERMISSIONS seed data follows PERM_<PAGE_CODE>_VIEW/CREATE/UPDATE/DELETE
        pattern — deviation → DRIFT finding, MAJOR severity
      — VIEW permission is declared as gateway (grants Search + Entry access)
        VIEW missing or not gateway → INCOMPLETE finding, CRITICAL severity

10.7  Permission Seeds source integrity
      — PERMISSIONS seed data MUST be generated by Security Engine from SCR-IDs
        SRS declares SCR-ID + page_code only — it does NOT enumerate PERM_* names
      — If SRS artifact contains explicit PERM_* INSERT statements or an explicit
        list of permission names as seed data → DUPLICATE finding, MAJOR severity
        (two sources of truth: SRS seed list vs Security Engine generation)
      — Correct SRS content: B4 Permissions Matrix (roles × screens × operations)
        Incorrect SRS content: PERM_LEGAL_ENTITY_VIEW / PERM_LEGAL_ENTITY_CREATE ...
      — SEC-BE phase: generates PERMISSIONS seed data from SCR-IDs + page_codes
        declared in SRS — must NOT reproduce permission lists already managed
        by Security Engine
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 5 — AUDIT REPORT FORMAT
═══════════════════════════════════════════════════════════════════

The report is produced after ALL checks are complete.
Three sections — in this order, always.

---

## REPORT HEADER

```
══════════════════════════════════════════════════════════════════
P4.1 — BACKEND AUDIT REPORT
Module              : [module name]
PLAN-ID              : [xxx]
srs-[MOD].md               : [feature code / version]
db-script-[MOD].md         : [DBS-ID / REDUCED]
backend-execution-plan: [PLAN-ID], ALIGN-BE ✓
Audit scope          : FULL / REDUCED / POLICY REDUCED / EXCEPTION SKIPPED
Date                 : [date]
══════════════════════════════════════════════════════════════════
```

---

## SECTION A — FINDINGS

One finding block per issue. Format per Section 2.

```
FINDINGS SUMMARY
──────────────────────────────────────────────────────────────────
Check    │ Scope                         │ CRIT │ MAJ │ MIN │ Result
─────────┼───────────────────────────────┼──────┼─────┼─────┼───────────────
CHECK-0  │ P0 → P1 alignment             │  [N] │ [N] │ [N] │ PASS/FAIL/SKIPPED
CHECK-1  │ SRS ↔ DB Script               │  [N] │ [N] │ [N] │ PASS/FAIL
CHECK-2  │ SRS ↔ Backend Plan            │  [N] │ [N] │ [N] │ PASS/FAIL
CHECK-3  │ DB ↔ Backend Plan + naming    │  [N] │ [N] │ [N] │ PASS/FAIL
CHECK-5  │ Cross-module deps             │  [N] │ [N] │ [N] │ PASS/FAIL
CHECK-6  │ Policy traceability           │  [N] │ [N] │ [N] │ PASS/FAIL/SKIPPED
CHECK-7  │ EXCEPTION interface           │  [N] │ [N] │ [N] │ PASS/FAIL/SKIPPED
CHECK-8  │ Contract gate compliance      │  [N] │ [N] │ [N] │ PASS/FAIL
CHECK-9  │ LOV backend half              │  [N] │ [N] │ [N] │ PASS/FAIL
CHECK-10 │ Security completeness (BE)    │  [N] │ [N] │ [N] │ PASS/FAIL
──────────────────────────────────────────────────────────────────
TOTAL    │                               │  [N] │ [N] │ [N] │
──────────────────────────────────────────────────────────────────
(No CHECK-4 — test coverage is out of audit scope as of v3.0)

OVERALL: [CLEARED ✓ / FINDINGS — resolve before Backend implementation begins]

[Finding blocks — one per issue — format per Section 2]
```

---

## SECTION B — ROOT CAUSE ANALYSIS

One entry per finding. One sentence. No recommendations — that is the
human's decision.

```
ROOT CAUSE SUMMARY
──────────────────────────────────────────────────────────────────
Finding-ID       │ Owned by │ Root cause
─────────────────┼──────────┼──────────────────────────────────────────
4A-BE-001-001    │ P2       │ DB Script added column with no SRS source
4A-BE-001-002    │ P1       │ SRS did not define the validation boundary
4A-BE-001-003    │ P3.1     │ Plan used a different type than DB Manifest
──────────────────────────────────────────────────────────────────
```

---

## SECTION C — DECISION SUMMARY

```
FINDINGS BY PROJECT
──────────────────────────────────────────────────────────────────
P1 (SRS)          : [N] findings — [N] CRITICAL, [N] MAJOR, [N] MINOR
P2 (DB)           : [N] findings — [N] CRITICAL, [N] MAJOR, [N] MINOR
P3.1 (Backend Plan): [N] findings — [N] CRITICAL, [N] MAJOR, [N] MINOR
──────────────────────────────────────────────────────────────────

PROCEED TO BACKEND IMPLEMENTATION?
──────────────────────────────────────────────────────────────────
  CRITICAL findings open : [N]
  MAJOR findings open    : [N]

  [0 CRITICAL + 0 MAJOR]  → CLEARED — Backend implementation may begin
  [CRITICAL or MAJOR > 0] → BLOCKED — resolve findings first

  Decision is the human's. This report states the facts.

  NOTE: This clearance covers Backend implementation ONLY. Frontend
  implementation additionally requires P4.2 CLEARED (a separate,
  later gate) — see PROJECT-4-FRONTEND-AUDIT.md.
──────────────────────────────────────────────────────────────────
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 6 — CONTINUATION PROTOCOL
═══════════════════════════════════════════════════════════════════

```
To resume a P4.1 session:

  Upload:
    srs-[MOD].md
    db-script-[MOD].md (if available)
    backend-execution-plan-[MOD].md
    prior P4.1 audit report

  Engine reads prior report → reconstructs finding register
  Engine confirms: "Prior P4.1 report found.
                   [N] open findings.
                   Continuing from [last cleared check].
                   Proceed?"

  Already-cleared checks are NOT re-audited.
  New artifacts trigger targeted re-audit of affected checks only.
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 7 — GOVERNANCE BOUNDARIES
═══════════════════════════════════════════════════════════════════

```
P4.1 OWNS:
  ✓ Finding Classification System (Section 2) — shared format with P4.2
  ✓ Finding ID namespace (4A-BE-[AUDIT]-[SEQ])
  ✓ P4.1 Audit Reports

P4.1 READS (authoritative — never reproduces content):
  ✓ platform-summary.md           ← Architectural Truth (P0)
  ✓ module-registry-[MOD].md      ← Module context (P0)
  ✓ business-policies-[MOD].md    ← Client policies (P0)
  ✓ srs-[MOD].md                        ← Functional Truth (P1)
  ✓ OQ Log                        ← owned by P1
  ✓ db-script-[MOD].md                  ← Structural Truth (P2)
  ✓ DB Field Traceability Matrix  ← owned by P2
  ✓ backend-execution-plan-[MOD].md     ← Backend Execution Truth (P3.1)
  ✓ DB Alignment Manifest         ← owned by P3.1
  ✓ Error Catalog                 ← owned by P3.1
  ✓ Derivation Log                ← owned by P3.1
  ✓ INT Summary                   ← owned by P3.1

P4.1 DOES NOT READ (v3.0 — out of scope):
  ✗ backend-test-plan-[MOD].md          → Test Generation Engine (outside pipeline)
  ✗ test-execution-manifest.md    → Test Generation Engine (outside pipeline)

P4.1 DOES NOT TOUCH:
  ✗ AQ-ID, INF-ID               → P0
  ✗ ENTITY-ID, RULE-ID, LOV-ID  → P1
  ✗ DBF-ID, XM-ID               → P2
  ✗ FIELD-ID, ERR-ID, DRV-ID   → P3.1
  ✗ TC-BE-ID                     → Test Generation Engine
  ✗ Any frontend artifact        → P3.2 / P4.2 (does not exist yet)
  ✗ Any artifact content        → read-only
  ✗ Conflict resolution         → human decision
  ✗ MODE 4B Finding IDs          → 4B is abolished (was already
                                    abolished pre-v2.0 — not reintroduced
                                    by this engine running twice)
```

---

## DRIVE DEPENDENCY TABLE

Inputs required (Step A):
  platform-summary.md, module-registry-[MOD].md, business-policies-[MOD].md — [GOVERNANCE-ROOT]/[Platform]/
  srs-[MOD].md                        — [GOVERNANCE-ROOT]/[Platform]/[Module]/P1-SRS/srs-[MOD].md
  db-script-[MOD].md                  — [GOVERNANCE-ROOT]/[Platform]/[Module]/P2-DB/db-script-[MOD].md
  backend-execution-plan-[MOD].md     — [GOVERNANCE-ROOT]/[Platform]/[Module]/P3.1-Backend-Exec/

Outputs published (Step C):
  audit-report-backend.md       — [GOVERNANCE-ROOT]/[Platform]/[Module]/P4.1-Audit-Backend/audit-report-backend.md

---

*End of PROJECT-4-BACKEND-AUDIT.md (Project 4.1)*
*Scope    : Backend pre-implementation cross-artifact validation only*
*           Runs once per module, before Backend implementation begins*
*Consumes : P0 artifacts + srs-[MOD].md + db-script-[MOD].md + backend-execution-plan-[MOD].md*
*Produces : P4.1 Audit Report (Section A: Findings, Section B: Root Cause,*
*           Section C: Decision Summary)*
*Checks   : CHECK-0,1,2,3,5,6,7,8,9,10 (backend-scoped; CHECK-4 removed v3.0)*
*Behavior : Finds → documents → continues. Never stops. Human decides.*
*Companion: PROJECT-4-FRONTEND-AUDIT.md (Project 4.2 — runs later,*
*           after the frontend plan exists, MUST read this report first)*


---

# OUTPUT FORMAT — FIX-PROMPTS GROUPED BY TARGET PROJECT (AMEND-PIPELINE-V5 · §1D.7)

This engine REMAINS the auditor (OPTIONAL in the V5 pipeline, §1D.1) and still
writes markdown — but the output is no longer a findings list to be read and
interpreted. It is a set of READY, PASTE-ABLE FIX-PROMPTS, grouped by the
project that owns the fix, used manually by the person.

```
## FIX-PROMPTS — [MOD] v[N] — backend audit — [date]
Summary : [N] findings → [n] P3.x · [n] P2 · [n] P1 · [n] P2.5 · [n] HUMAN

### → [TARGET PROJECT]                                   [count]
┌ FIX-[NNN]   severity: CRITICAL|MAJOR|MINOR   affects: [ID(s)]
│ PROBLEM      : what is wrong and exactly where (file / section / ID)
│ WHY          : the rule / contract / registry entry it violates
│ RECOMMENDED  : the concrete change to make
│ DEPENDENCIES : what must move WITH it (XM / UXD / ALIGN mappings, other
│                IDs, other engines' artifacts) and what must NOT change —
│                the fixer must respect these while editing
│ VERIFY       : how the fixer proves it is fixed (re-run which check)
└ PASTE-READY PROMPT
  "In [MOD] v[N] [artifact-{mod}.md], apply FIX-[NNN]: [RECOMMENDED].
   Keep [DEPENDENCIES: must-not-change] unchanged; update [must-move-with]
   accordingly; then [VERIFY]."
```

Grouping rule: one `### → PROJECT` block per owning engine (P3.1 / P3.2 / P2 /
P1 / P2.5), in pipeline order; anything with no owning engine goes under
`### → HUMAN DECISION`. Every finding appears exactly once. Filenames use the
§1D.2 module-qualified vocabulary. Nothing else about this engine's audit
checks changes.


PATHS (rendered from config.DRIVE_LAYOUT — GOVERNANCE-CONFIG §1E; never edit by hand)
  [MROOT] = [CTX]/[Module]/          (v1)   or   [CTX]/[Module]/v[N]/   (IFA, N ≥ 2)
  WRITES TO (this engine is the ONLY writer of these folders):
    (none — this engine writes no stage folder)
  READS FROM:
    [MROOT]/P1-SRS/   ← srs-[mod].md, registry-srs-[mod].md
    [MROOT]/P2-DB/   ← db-script-[mod].md, registry-db-[mod].md
    [MROOT]/P3.1-Backend-Exec/   ← backend-execution-plan-[mod].md, registry-exec-be-[mod].md
    [MROOT]/P3.5-Tests/   ← backend-test-plan-[mod].md, registry-test-be-[mod].md
    [CTX]/_platform/                        ← platform-summary.md
  LEDGER: [CTX]/[Module]/_journey/journey-[mod].json   (cross-version; §1D.8)
  LAW (§1E.1): never write a file at [CTX] root or [MROOT] root — folders only.
  SELF-HEAL (§1E.5, AUTOMATIC at Pre-Flight): an input not at its governed path
  is searched in the module subtree (V5 or legacy name), renamed + moved there
  via the connector, and reported under HEALED: in the handoff — no human step.
  A missing ledger is created (START v1) on first contact.
  The connector upload in step 1 targets the WRITES-TO folder above, nothing else.
