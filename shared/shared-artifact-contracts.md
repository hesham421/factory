# ERP GOVERNANCE — SHARED ARTIFACT CONTRACTS
## Inter-Project Artifact Interface Specifications

```
File ID        : SHARED-ARTIFACT-CONTRACTS
Version        : 4.0 — Multi-Project + Versioning (CONTRACT-14 reuse,
                 CONTRACT-15 VRE) on top of v3.0 (P3 Light — test
                 generation relocated to the standalone Test Generation
                 Engine outside the pipeline)
Status         : MANDATORY — Embed in every project's system prompt
Companion to   : SHARED-GOVERNANCE-CORE.md (foundations, CORE-11)
                 SHARED-GOVERNANCE-RULES.md (operational rules)
                 MULTI-PROJECT-VERSIONING-ARCHITECTURE.md (the v4.0 layer)
Maintained by  : Architecture Authority
Change log     : v4.0 adds CONTRACT-14 (versioned reuse import — pinned,
                 read-only) and CONTRACT-15 (Version Resolution Event).
                 v3.0 rewrote CONTRACT-9/13 (test artifacts → Test
                 Generation Engine) and CONTRACT-5 (CHECK-4 removed).
                 See end of file for the full change summary.
```

These contracts define the precise interface between artifacts generated
by different governance engines. Every contract specifies: owner, consumer,
what crosses the interface, what does NOT cross the interface, and what
constitutes a violation of the contract.

All governance engines honor all contracts. No project selectively
applies only the contracts relevant to its own output.

**Engines governed by this file (post v4.0):**
```
P(-1)  Master Registry Builder      (pre-P0 analysis intelligence +
                                     v4.0 ecosystem registry authority)
P0     Platform Inception Engine
P0.5   PRD Engine
P1     SRS Governance Engine
P2     Database Governance Engine
P2.5   UI/UX Design Engine
P3.1   Execution Plan Engine — PASS 1 (Backend, LIGHT — no tests)
P3.2   Execution Plan Engine — PASS 2 (Frontend, LIGHT — no tests)
P4.1   Governance Audit Engine — Backend gate (pre-implementation)
P4.2   Governance Audit Engine — Frontend gate (pre-implementation)
P5     api-verify (MODE 5 — post-implementation script generation)
P-REG  Module State Registry Extractor (session-continuity utility)
P-DOMAIN Domain Profile Builder     (v4.0 domain evolution authority —
                                     owns Model/Extension versions + VRE)
TEST-GEN  Test Generation Engine    (STANDALONE — OUTSIDE the pipeline;
                                     owns backend/frontend test-plans +
                                     test-execution-manifest.md)
```

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-1 — DB Field Traceability Matrix → DB Alignment Manifest
═══════════════════════════════════════════════════════════════════

```
Owner    : Project 2 — Database Governance Engine
           (DB Field Traceability Matrix, embedded in db-script.md)
Consumer : Project 3.1 — Execution Plan Engine, PASS 1 (Backend)
           (DB Alignment Manifest, embedded in backend-execution-plan.md)
```

**What crosses the interface:**
```
DBF-ID  →  Project 3.1 Manifest references DBF-IDs for binding declarations
```

**What Project 3.1 ADDS at the interface (new content only):**
```
FIELD-ID    : Assigned by Project 3.1 (new — not from Project 2)
Plan Type   : How the plan represents this field (Java/TypeScript type)
FK/XM-ID    : XM-[MOD]-[N] if this field is a cross-module FK column
Match Status: ✓ aligned | ✗ type mismatch | ⏸ XM deferred
```

**What does NOT cross (Project 3.1 never reproduces):**
```
Column name    : Derived from DBF-ID lookup in Traceability Matrix
DB Type        : Derived from DBF-ID lookup in Traceability Matrix
SRS Source     : Derived from DBF-ID lookup in Traceability Matrix
Table name     : Derived from DBF-ID lookup in Traceability Matrix
```

**Contract violation:** Any DB Alignment Manifest that contains column
names, DB types, or SRS section references is a violation. Those facts
are sourced exclusively from the DB Field Traceability Matrix by DBF-ID.
Finding: DUPLICATE type, MAJOR severity.

**Interface format (Project 3.1 Manifest — canonical):**
```
FIELD-ID  │ DBF-ID   │ Plan Type   │ FK/XM-ID      │ Match Status
──────────┼──────────┼─────────────┼───────────────┼─────────────
FIELD-0001│ DBF-0001 │ Long        │ —             │ ✓
FIELD-0003│ DBF-0003 │ String(200) │ —             │ ✓
FIELD-0007│ DBF-0007 │ Long        │ XM-FIN-002    │ ⏸
```

**Note (v2.0):** FIELD-ID is exclusively a PASS 1 (Backend) namespace.
PASS 2 (Frontend) NEVER assigns a new FIELD-ID for the same data —
it references the PASS 1 FIELD-ID by ID only (see CONTRACT-12).

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-2 — XM Register → INT Summary
═══════════════════════════════════════════════════════════════════

```
Owner (structural) : Project 2 — XM Register in db-script.md
Owner (execution)  : Project 3.1 — INT Summary in backend-execution-plan.md
Coordinator        : Registry Maintainer — Global XM Dependency Index
```

**What crosses the interface (Project 2 → Project 3.1):**
```
XM-[MOD]-[N]       : Module-qualified XM-ID — assigned in MODE 1.5
Type               : HARD-FK | SOFT-READ
Target Table       : Structural detail (Project 2 owns; Project 3.1 does not restate)
Target Module      : Module name (Project 3.1 uses this for routing)
Initial Status     : READY | DEFERRED | CONDITIONAL
```

**What Project 3.1 ADDS at the interface (INT Summary new content):**
```
Execution Status   : READY | DEFERRED | ACTIVE | CONDITIONAL (may differ from DB Script status if RXE received)
Blocks             : Which B2 API-IDs are blocked by this dependency
Workaround         : How the dependency is handled while DEFERRED
Unblock Condition  : What must happen for DEFERRED→READY transition
RXE-ID             : If an XM Resolution Event is active for this XM-ID
```

**What does NOT cross (INT Summary never reproduces):**
```
Table names        : Stay in DB Field Traceability Matrix (Project 2)
FK column names    : Stay in XM Register (Project 2)
DBF-IDs            : Stay in Traceability Matrix (Project 2)
```

**ALIGN-BE Table 4 contract with INT Summary:**
```
ALIGN-BE Table 4 confirms gate conditions only — it does NOT reproduce INT Summary.
Three conditions + one RXE check + one pointer to INT Summary:

XM DEPENDENCY GATE CHECK
───────────────────────────────────────────────────────────────────
All XM-[MOD]-[N] IDs from DB Script accounted for │ [✓ / ✗ list]
All DEFERRED XM-[MOD]-[N] have workarounds         │ [✓ / ✗ list]
All READY XM-[MOD]-[N] integrated in plan          │ [✓ / ✗ list]
All OPEN RXEs targeting this module acknowledged   │ [✓ / ✗ list RXE-IDs]
───────────────────────────────────────────────────────────────────
See INT Summary for full XM register.
```

**Contract violation:** Any artifact that reproduces XM Register
structural detail (table names, FK column names) in INT Summary or
ALIGN-BE Table 4 is a violation. Finding: DUPLICATE type, MAJOR severity.

**Note (v2.0):** XM-IDs are exclusively a Backend (PASS 1) concern.
Cross-module dependencies are a data/integration matter — PASS 2
(Frontend) never assigns or resolves XM-IDs; it only consumes stable
API contracts (see CONTRACT-12), which already reflect XM resolution.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-3 — OQ Log → All Artifact Headers
═══════════════════════════════════════════════════════════════════

```
Owner    : Project 1 — SRS Governance Engine
           (OQ Log, canonical — embedded in srs.md and updated in place)
Consumers: ALL projects and ALL generated artifacts (P0.5 through P5,
           and the standalone Test Generation Engine)
```

**What crosses the interface:**
```
OQ count     : Number of currently active (OPEN) OQ-IDs
OQ-ID list   : The IDs themselves — for traceability reference
```

**Artifact header format (mandatory in all phase artifacts):**
```
Open Questions: [N active / None] — see OQ Log
```

**What does NOT cross (headers never reproduce):**
```
OQ question text   : Stays in OQ Log
OQ status detail   : Stays in OQ Log
OQ resolution notes: Stays in OQ Log
OQ escalation info : Stays in OQ Log
```

**Update discipline:**
Any project may ADD OQs to the OQ Log during its mode execution.
No project removes or overwrites existing OQ records.
When an OQ is resolved, the resolving project updates its STATUS
field in the OQ Log — it does not delete the OQ record.

**New in v2.0 — PRD↔SRS OQs:**
OQs raised by the PRD↔SRS Reconciliation Gate (CONTRACT-11) use the
same OQ Log and the same lifecycle rules as any other OQ. They are
NOT a separate log. Escalation field for this type: `RECONCILE-[MOD]`.

**Escalation extension:**
Cross-module OQs use the ESCALATION field: `XM-ESC-[MODULE]`
Escalated OQs are also registered in the project-registry
Global OQ Escalation Index.

**Contract violation:** Any artifact header that reproduces OQ question
text, status, or resolution detail is a violation (DUPLICATE type,
MINOR severity). Any project that deletes an OQ record is a CRITICAL
governance violation.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-4 — Error Catalog → F3 and TC
═══════════════════════════════════════════════════════════════════

```
Owner    : Project 3.1 — Execution Plan Engine, PASS 1 (Backend)
           (Error Catalog, canonical — embedded in backend-execution-plan.md)
Consumers: F3 (Frontend Validation) — within frontend-execution-plan.md (P3.2)
           TC (Test Cases) — within backend-test-plan.md / frontend-test-plan.md
           (owned by the standalone Test Generation Engine)
           — Error Catalog stays exclusively backend-owned; F3/TC reference only
```

**What crosses the interface:**
```
ERR-ID     : The identifier for each error condition
```

**F3 and TC format (reference only — never reproduce):**
```
F3: Validation → ERR-[ID] → React error type mapping
TC: Expected error → ERR-[ID]
```

**What does NOT cross (F3 and TC never reproduce):**
```
Error message text   : Stays in Error Catalog (backend-execution-plan.md)
HTTP status code     : Stays in Error Catalog (backend-execution-plan.md)
RULE-ID source       : Stays in Error Catalog (backend-execution-plan.md)
Message key          : Stays in Error Catalog (backend-execution-plan.md)
```

**Amendment protocol:** If F3 or TC needs an ERR-ID not in the catalog,
the Error Catalog Amendment Protocol activates. Since the Error Catalog
is frozen at ALIGN-BE ✓ (before PASS 2 / F3 even begins, and before the
Test Generation Engine runs), a missing ERR-ID discovered downstream
escalates back to PASS 1 as an amendment — it is never invented locally
in F3 or in a test-plan. The work pauses until the new ERR-ID is
formally assigned in backend-execution-plan.md.

**Contract violation:** Any ERR-ID appearing in F3 or TC that is not
in the Error Catalog is a violation. Finding: ORPHAN type, MAJOR severity.
Any reproduction of error message text outside the catalog is a violation.
Finding: DUPLICATE type, MINOR severity.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-5 — Finding Lifecycle (Dual Pre-Implementation Audit Gate)
═══════════════════════════════════════════════════════════════════

```
Owner: Project 4 — Governance Audit Engine
       RUNS TWICE, once per execution plan pass — NOT once at the end.
```

**REWRITTEN IN v2.0, UPDATED IN v3.0.** Under the Backend/Frontend
split (CONTRACT-9, CONTRACT-12), there are two independent
pre-implementation planning passes, each needing its own gate BEFORE
its own implementation begins. As of v3.0 (P3 light), neither gate
reads any test artifact — CHECK-4 (functional test coverage) is removed
from both P4.1 and P4.2, because test generation moved out of the
pipeline into the standalone Test Generation Engine.

```
P4.1 — Backend Audit Gate
  Runs after   : backend-execution-plan.md (ALIGN-BE ✓) exists
  Runs before  : Backend implementation (Claude Code) begins
  Reads        : platform-summary, module-registry, business-policies,
                 srs.md, db-script.md, backend-execution-plan.md
  Does NOT read: any test artifact (backend-test-plan.md,
                 test-execution-manifest.md) — v3.0, out of scope
  Does NOT read: frontend artifacts (do not yet exist at this point)

P4.2 — Frontend Audit Gate
  Runs after   : frontend-execution-plan.md (ALIGN-FE ✓) exists
  Runs before  : Frontend implementation (Claude Code) begins
  Reads        : srs.md, frontend-execution-plan.md,
                 prd-[MOD].md, flow-diagram.md, ui-ux-spec.md,
                 real API Docs (from api-doc-generator),
                 PLUS the P4.1 report (to confirm no backend drift
                 occurred between P4.1 and frontend planning)
  Does NOT read: any test artifact (frontend-test-plan.md) — v3.0,
                 out of scope
```

Both gates are pre-implementation. Neither is a post-implementation
audit — MODE 4B remains abolished; it is NOT reintroduced by having
two gates.

**Finding resolution states (within either gate's report):**
```
IMMEDIATE  : Must be resolved before implementation begins (CRITICAL/MAJOR)
DEFERRED   : Accepted risk — formally documented; scheduled for next iteration
WAIVED     : Human authority decision to accept the finding as-is
INVALID    : Finding raised in error — not a real issue
```

**Finding ID format (gate-qualified):**
```
4A-BE-[AUDIT-SEQ]-[FINDING-SEQ]   — from P4.1
4A-FE-[AUDIT-SEQ]-[FINDING-SEQ]   — from P4.2
Example: 4A-BE-001-003, 4A-FE-001-007
  Each gate keeps its own AUDIT-SEQ and FINDING-SEQ sequence.
  Finding sequence is assigned in CHECK order within that gate's run.
```

**Finding record continuity rule:**
If a prior P4.1 or P4.2 report is uploaded for continuation, all
existing Finding-IDs (BE or FE, matching the gate being continued) are
preserved verbatim. No Finding-ID is re-assigned or renumbered across
sessions. New findings in the continuation session use the next
available FINDING-SEQ within that gate's sequence.

**Contract violation:** Any new Finding-ID that duplicates or
renumbers an existing 4A-BE/FE-[AUDIT]-[SEQ] is a DUPLICATE governance
violation. Finding-ID continuity is mandatory for audit trail integrity.
Any P4.2 run that does not read the P4.1 report is an INCOMPLETE
violation (MAJOR) — cross-gate drift is exactly what P4.2's extra
input requirement exists to catch.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-6 — Module Governance Index (Shared Navigation)
═══════════════════════════════════════════════════════════════════

```
Maintenance Authority : Project 3 (both P3.1 and P3.2 update the same MGI)
Updated by            : ALL projects at each mode gate completion
Read by                : ALL projects at session start
```

**Nature of the MGI:**
The MGI is an OPERATIONAL NAVIGATION ARTIFACT. It is not a truth layer.
It is not a governance authority. It reflects state — it does not govern it.
No project reads the MGI and acts on it as authoritative — they confirm
its state against uploaded artifact content.

**What the MGI contains (v2.0 — extended fields):**
```
Pipeline Status    : Current stage — one of:
                      P(-1) | P0 | P0.5 | P1 | P2 | P2.5 |
                      P3.1 | P4.1 | IMPL-BE | API-DOC-GEN |
                      GATE | P3.2 | P4.2 | IMPL-FE
Attached Artifacts : Which governed artifacts exist for this module
Open Dependencies  : Open XM-[MOD]-IDs, open OQ-IDs, open findings
Execution State    : Current phase, completed phases, next safe action
Execution Readiness: READY | BLOCKED — reason | REDUCED — reason
LAST-VERIFIED      : Date and stage that last confirmed state is current
VERIFIED-BY        : Stage/gate that set LAST-VERIFIED
GOVERNANCE-STATE   : FULL | REDUCED | RECOVERY | EXCEPTION
GATE STATUS        : Backend-Module-Complete ✓/✗ (the P3.2 prerequisite —
                     see CONTRACT-12)
```

**Staleness protocol:**
If MGI LAST-VERIFIED is older than threshold (7 days active / 30 days
maintenance), the reading project emits:
`⚠ MGI last verified [N] days ago. Confirm pipeline state before proceeding.`

**Contract violation:** Any project that treats MGI state as authoritative
governance truth (rather than navigational summary) and acts without
confirming against artifact content is a governance risk. The MGI can
be stale; the artifacts cannot lie about their own content.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-7 — Shared Entity → Consumer Module SRS
═══════════════════════════════════════════════════════════════════

```
Owner    : The module declared as canonical owner in the project-registry
           Shared Entity Declarations section
Consumer : Any module (within the same project) that uses a SHARED entity
```

**What crosses the interface:**
```
ENTITY-ID   : Canonical ENTITY-ID from the project-registry
DBS-ID      : DBS-ID of the owner module's DB Script
Table name  : From the Shared Entity Declarations
```

**Consumer module SRS declaration format:**
```
Consumes SHARED [ENTITY-ID] ([Entity Name]) — owner: [Module name]
  See project-registry: Shared Entity Declarations
  Dependency type: HARD-FK | SOFT-READ
  XM candidate: Yes — to be formalized as XM-[CONSUMER-MOD]-[N] in MODE 1.5
```

**What does NOT cross:**
```
Consumer does NOT assign a new ENTITY-ID for the shared entity
Consumer does NOT create a new DB table for the shared entity
Consumer does NOT define new fields on the shared entity
```

**Change impact rule:**
When the owner module amends a SHARED entity (new fields, type changes,
deprecations), an XM RESOLUTION EVENT is created for all consumer modules.
Consumer modules evaluate impact and raise OQ-IDs if their implementation
is affected.

**Note (v4.0 — cross-PROJECT boundary):** CONTRACT-7 governs shared
entities WITHIN one project. A model reused ACROSS projects uses the
pinned read-only import mechanism of CONTRACT-14 (not a shared-entity
declaration), and version changes propagate via CONTRACT-15 (VRE), not
via an in-project RXE.

**Contract violation:** A consumer module assigning a new ENTITY-ID for
an entity already declared SHARED in the project-registry is a CRITICAL
violation (DUPLICATE type). Two modules each owning the same entity
creates permanent traceability corruption.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-8 — XM Resolution Event → Target Module INT Summary
═══════════════════════════════════════════════════════════════════

```
Initiator  : Registry Maintainer (per xm-resolution-event-protocol.md)
Target     : Module holding DEFERRED XM-IDs for the triggering module
Responder  : Project 3.1 — Execution Plan Engine, PASS 1 (Backend only —
             XM-IDs never exist in PASS 2 / Frontend, see CONTRACT-2 note)
Confirmer  : Project 4.1 — Governance Audit Engine, Backend gate (CHECK-5)
```

**What the RXE carries to the target:**
```
RXE-ID          : RXE-[TARGET-MOD]-[SEQ]
Affected XM-IDs : List of XM-[TARGET-MOD]-[N] IDs ready for re-evaluation
Change summary  : What changed in the initiating module (new DBS-ID, etc.)
Required action : What the target module's governance session must do
```

**Target module INT Summary update:**
```
XM-ID status update : DEFERRED → READY (or CONDITIONAL if REDUCED)
DRV-ID entry        : "XM-[ID] transitioned per RXE-[ID] — [date]"
Unblock condition   : Updated to "Resolved per RXE-[ID]"
```

**Audit confirmation (P4.1 CHECK-5):**
```
CHECK-5.4 : All OPEN RXEs at P4.1 entry are RESOLVED or WAIVED
CHECK-5.5 : All XM DEFERRED→READY transitions have DRV-ID documentation
```

**Contract violation:** An INT Summary that ignores an OPEN RXE and
does not update affected XM-ID statuses is a violation.
Finding: INCOMPLETE type, MAJOR severity.

**Note (v4.0):** CONTRACT-15 (VRE) is the version-change analogue of this
contract — same shape, applied to Model/Extension version publishes
instead of XM DEFERRED→READY transitions.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-9 — Execution Plans → Test Plans (Test Generation Engine)
═══════════════════════════════════════════════════════════════════

```
Owner (execution plans) : Project 3 (LIGHT — two temporal passes)
           PASS 1 produces: backend-execution-plan.md
           PASS 2 produces: frontend-execution-plan.md
Owner (test plans)      : Test Generation Engine (STANDALONE — outside pipeline)
           BE mode produces: backend-test-plan.md + test-execution-manifest.md
           FE mode produces: frontend-test-plan.md
Consumer : Each test-plan consumes ONLY from its own pass's execution-plan.
           frontend-test-plan.md does NOT consume from backend-execution-plan.md
           directly.
```

**REWRITTEN IN v3.0.** Under P3 light, the execution-plan engines
(P3.1, P3.2) no longer produce any test artifact. Test plans and the
execution manifest are produced by the standalone Test Generation
Engine (PROJECT-TEST-GENERATION-ENGINE.md), which runs OUTSIDE the
pipeline and consumes the execution plans. The underlying discipline
(reference-only, gate-first) is unchanged from v2.0 — only the producer
of the test artifacts changed.

**Pre-condition (mandatory — non-negotiable, applies to BOTH test-plans):**
```
Gate ALIGN-BE ✓ in backend-execution-plan.md MUST be confirmed before
the Test Generation Engine generates backend-test-plan.md.

Gate ALIGN-FE ✓ in frontend-execution-plan.md MUST be confirmed before
the Test Generation Engine generates frontend-test-plan.md.

Rationale (unchanged): each test-plan references ERR-IDs, RULE-IDs,
API-IDs, FIELD-IDs, and SCR-IDs that are only finalized after the
execution plan's own ALIGN gate. A test-plan generated before that gate
references unstable IDs and is a governance violation.

Violation: either test-plan generated while its source plan's ALIGN
gate is ✗ or absent → SEQUENCE VIOLATION type, CRITICAL severity.
```

**What crosses the interface (each test-plan references — never redefines):**
```
ERR-ID    : Referenced for expected error assertions — sourced from Error Catalog (BE only)
RULE-ID   : Referenced per TC scenario — sourced from srs.md via execution-plan.md
API-ID    : Referenced per TC scenario — sourced from SVC+API phase (BE) or real API Docs (FE)
FIELD-ID  : Referenced for field-level assertions — sourced from DB Alignment Manifest (BE)
SCR-ID    : Referenced for screen-level permission scenarios — sourced from SEC phase
XM-[MOD]-ID : Referenced for integration mock strategy — sourced from INT Summary (BE only)
Test-Hint : Optional testability note per RULE-ID — sourced from srs.md A4
```

**What does NOT cross (neither test-plan reproduces):**
```
Error message text    : Stays in Error Catalog (backend-execution-plan.md)
HTTP status codes     : Stays in Error Catalog (backend-execution-plan.md)
API request/response  : Stays in SVC+API (BE) or real API Docs (FE)
Field definitions     : Stays in DB Alignment Manifest (backend-execution-plan.md)
Rule descriptions     : Stays in srs.md A4
```

**What each test-plan ADDS (new content — owned by the Test Generation Engine):**
```
TC-BE-[MOD]-ID  : JUnit scenarios
TC-FE-[MOD]-ID  : Playwright scenarios
Given/When/Then blocks : Scenario specifications per TC-ID
Data-Class    : VALID | INVALID | BOUNDARY | EDGE_CASE
Mock strategy : For DEFERRED XM-[MOD]-IDs (BE only — FE has no XM-IDs)
TC Traceability Index : RULE-ID → TC-IDs | API-ID → TC-IDs | ERR-ID → TC-IDs
                        (kept separately per BE/FE — never merged into one index)
TC Coverage Matrix Summary : self-contained in the test-plan (NOT written
                        back into the execution plan — the plan is light)
```

**test-execution-manifest.md (owned by the Test Generation Engine):**
```
Generated alongside backend-test-plan.md, immediately after the test
plan, in the same BE-mode session.
Purpose: pre-resolve the dependency graph and RULE→ERR→TC joins that
P5 (api-verify) would otherwise have to re-derive itself — see CONTRACT-13.

Contents:
  DEPENDENCY ORDER      : topological entity build order (from ENTITY
                           REGISTRY Business Code pattern + RULE-IDs)
  RULE→ERR→TC TRIPLES    : pre-joined, ready-to-consume rows
  ENTITY CRUD CHECKLIST  : per-entity operation flags (Create/Search/
                           Update/Activate/Deactivate/GetById/Delete)

This file is a DERIVED VIEW, not a new Truth Layer. It never introduces
a RULE-ID, ERR-ID, or TC-ID that doesn't already exist in
backend-execution-plan.md / backend-test-plan.md. If those files are
amended after the manifest was generated, the manifest MUST be
regenerated — a stale manifest is a SEQUENCE VIOLATION risk for P5.
```

**TC Coverage Matrix contract (v3.0 — moved out of the execution plan):**
```
TC Coverage Matrix SUMMARY now lives in the test-plan itself (produced
by the Test Generation Engine for its own self-check). The execution
plan is LIGHT — it no longer carries a SECTION D / TC Coverage Matrix
Summary at all.
TC Coverage Matrix DETAIL (full TC blocks) lives in the matching test-plan.

Contract note: the execution plan (BE or FE) must NOT contain any TC
block or TC Coverage Matrix — a P3-light execution plan that does is a
regression. Finding: DUPLICATE type, MAJOR severity.
```

**P4 consumption (v3.0 — CHECK-4 removed):**
```
P4.1 and P4.2 no longer read any test-plan. CHECK-4 (functional test
coverage) has been removed from both audit engines. Test artifacts are
out of audit scope.
```

**Contract violation summary:**
```
1. Either test-plan generated before its source plan's ALIGN gate ✓
   → SEQUENCE VIOLATION, CRITICAL severity

2. Either test-plan redefines any ERR-ID, RULE-ID, API-ID, or FIELD-ID
   → ORPHAN type, CRITICAL severity

3. Either test-plan reproduces Error message text or API specs
   → DUPLICATE type, MAJOR severity

4. A P3-light execution-plan.md contains TC blocks or a TC Coverage
   Matrix Summary
   → DUPLICATE type, MAJOR severity

5. frontend-test-plan.md reads backend-execution-plan.md directly instead
   of going through real API Docs (CONTRACT-12)
   → BOUNDARY VIOLATION, MAJOR severity (defeats the decoupling purpose)
```

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-10 — Platform Summary → PRD Engine  (v2.0)
═══════════════════════════════════════════════════════════════════

```
Owner    : Project 0 — Platform Inception Engine
           (platform-summary.md, module-registry-[MOD].md,
            business-policies-[MOD].md)
Consumer : Project 0.5 — PRD Engine
```

**What crosses the interface:**
```
Module scope, entity candidates, LOV candidates (module-registry.md)
Client policies, business intent, priorities (business-policies.md)
Platform tier / dependency classification (platform-summary.md)
```

**What PRD Engine ADDS (new content — not from P0):**
```
US-[MOD]-[N]  : User Story ID — the only ID namespace PRD Engine owns
Priority tag  : Optional, per user story
Success metric: Optional, per user story or per module
```

**Mandatory sourcing rule (prevents invented scope):**
```
Every US-[MOD]-[N] MUST carry a Source reference, e.g.:
  "US-[MOD]-003 — [story text] — Source: business-policies.md §2.4"
A user story with no traceable source is a CONTRACT-10 violation
(ORPHAN type, MAJOR severity) and must be raised as an OQ instead of
silently included.
```

**What does NOT cross / what PRD Engine must NEVER produce:**
```
✗ RULE-ID or any enforceable business rule text (P1 exclusive)
✗ ENTITY-ID, LOV-ID, SCR-ID, API-ID (P1 exclusive)
✗ Any binding functional specification — a user story is a NEED,
  not a specification.
```

**Contract violation:** Any prd-[MOD].md that defines a RULE-ID,
ENTITY-ID, or any P1-owned identifier is a CRITICAL boundary violation.

**v2.1 — PRD hard-gates Project 1:**
```
Project 1 (SRS Engine) MUST NOT begin generation until prd-[MOD].md
is attached in the same session. HARD GATE.
Violation: srs.md generated without prd-[MOD].md → SEQUENCE VIOLATION, CRITICAL.
```

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-11 — PRD + SRS → UI/UX Design Engine (Reconciliation Gate) (v2.0)
═══════════════════════════════════════════════════════════════════

```
Owner (product intent) : Project 0.5 — PRD Engine (prd-[MOD].md)
Owner (functional truth): Project 1 — SRS Engine (srs.md, PART B: B1-B4)
Consumer                : Project 2.5 — UI/UX Design Engine
```

**Precondition (v2.1):** UI/UX Design Engine begins from prd-[MOD].md
ALONE, in parallel with P1. Drafts before srs.md exists are DRAFT status.

**Reconciliation Gate (v2.1 — runs before HUMAN APPROVAL):**
```
GATE: PRD ↔ SRS RECONCILIATION — runs once srs.md is available, before
approval. Every US-ID used has a traceable SRS counterpart or is raised
as OQ (RECONCILE-[MOD]) + BLOCKED-BY-OQ; no US-ID contradicts a RULE-ID;
every field/permission the draft shows is confirmed against srs.md B1-B4.
Flagged sections are reworked before approval; the rest proceeds.
```

**Resolution authority rule:** SRS is the authoritative ceiling for WHAT
is functionally true. PRD/flow-diagram reorganizes HOW screens group,
never drops a field/permission/rule SRS requires. Any US-ID left
BLOCKED-BY-OQ is excluded until a human resolves the OQ.

**What crosses:** US-ID + priority + one-line intent (PRD); SCR-ID
inventory + B1-B4 (SRS, read-only).
**UI/UX ADDS:** flow-diagram.md, ui-ux-spec.md, visual-mockups/.
**UI/UX must NEVER produce:** new fields/rules/permissions not in
srs.md B1-B4; final/binding component names/CSS/routing (P3.2 decides).

**Contract violation:** flow-diagram/ui-ux-spec that omits a required SRS
field/permission or introduces one not in SRS → MISMATCH, MAJOR.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-12 — Backend Module Complete + UI Shell Complete → Frontend Execution Plan (v2.1)
═══════════════════════════════════════════════════════════════════

```
Owner    : Real backend (api-doc-generator) + Project 2.5 (approved
           outputs) + Real UI Shell (Claude Code, v2.1)
Consumer : Project 3.2 — Execution Plan Engine, PASS 2 (Frontend)
```

PASS 2 gates on the REAL, implemented API surface (never DOC-1) and,
as of v2.1, on a REAL, implemented UI Shell (never mockups alone) — a
real artifact cannot drift the way a planned one can.

**UI Shell step (between UI/UX approval and P3.2):** Claude Code
implements the UI Shell for real (components + routing + styling
matching approved mockups, NO data binding yet); a human confirms
visual fidelity.

**Precondition — GATE: BACKEND MODULE COMPLETE (all three):**
```
□ Backend implementation 100% complete for the WHOLE module
□ api-doc-generator produced real API Docs for every API-ID in SRS B5
□ UI/UX outputs (flow-diagram, ui-ux-spec, mockups) human-approved
```

**Precondition — GATE: UI SHELL COMPLETE (v2.1 — both):**
```
□ Claude Code implemented the UI Shell in the real frontend codebase
□ Human review confirmed visual fidelity (separate sign-off)
```

**Both gates must pass before P3.2 begins — neither is sufficient alone.**

**Swagger ↔ SRS Reconciliation (part of the Backend gate):** every
API-ID in srs.md B5 has a matching real endpoint (else DRV-ID/OQ);
any real endpoint with no API-ID raised as OQ.

**F1/F4 role (v2.1 — confirm + integrate, not design fresh):** F1
CONFIRMS the Shell's models against real API Docs; F4 DOCUMENTS the
Shell's routing/components and adds only missing integration wiring.

**What P3.2 never re-derives:** DOC-1, PASS-1 FIELD-ID/ERR-ID (reference
only), a component/routing structure independent of the real Shell.

**Contract violation:** frontend-execution-plan.md generated before BOTH
gates confirm → SEQUENCE VIOLATION, CRITICAL (the most important gate).

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-13 — test-execution-manifest.md → api-verify (P5) (REVISED, v3.0)
═══════════════════════════════════════════════════════════════════

```
Owner    : Test Generation Engine (STANDALONE — outside pipeline)
           (produces the manifest alongside backend-test-plan.md, see CONTRACT-9)
Consumer : Project 5 — api-verify (MODE 5)
```

**v3.0 change:** the manifest's owner moved from Project 3.1 to the
standalone Test Generation Engine. Everything else is unchanged.

**Purpose:** decouple P5 from parsing execution-plan/test-plan structure.
P5's job is translation (governed spec → runnable script), not derivation.

**What crosses:** test-execution-manifest.md (DEPENDENCY ORDER,
RULE→ERR→TC TRIPLES, ENTITY CRUD CHECKLIST).
**What P5 no longer derives:** the dependency graph, the RULE→ERR→TC map.
**What P5 still does:** Stage A (inventory), D (assembly), E (exploratory).
**Degraded mode:** manifest absent → P5 falls back to self-derivation and
states it is in degraded mode.

**Contract violation:** P5 deriving a dependency graph or RULE→ERR→TC
mapping WHILE a valid manifest is present → BOUNDARY VIOLATION, MAJOR.

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-14 — Versioned Reuse Import (NEW, v4.0)
═══════════════════════════════════════════════════════════════════

```
Owner (published item) : the OWNER project's P-DOMAIN (the version) +
                          P(-1) (the reuse-registry catalog entry)
Consumer               : any OTHER project that imports it, declared in
                          the CONSUMER project's project-manifest.md
```

**Purpose:** let one project reuse a Model/Extension that another project
owns, WITHOUT copying it, mutating it, or coupling the two projects'
registries — the isolation guarantee of PRINCIPLE-13 must still hold.

**What crosses the interface:**
```
A PINNED reference to an exact published version:
  [OwnerProject]/[Domain]/Model-X@vN   (or ext-Y@vN)   — READ-ONLY
Recorded in the consumer's project-manifest.md `imports:` list, and
listed as available in _ecosystem/reuse-registry.md.
```

**What does NOT cross:**
```
✗ The owner's artifacts are NOT copied into the consumer's project.
✗ The owner's IDs (ENTITY-ID, FIELD-ID, etc.) are NOT re-assigned by
  the consumer — they are referenced by their owner-qualified form.
✗ The consumer NEVER edits the owner's version (immutability, RULE-15).
✗ An unpinned / "latest" import is forbidden — always an exact version.
```

**How the consumer changes what it needs:**
```
- Needs the owner's newer capability → pin a NEWER published version
  (an explicit, recorded opt-in — see CONTRACT-15).
- Needs something the owner doesn't provide → build its OWN Extension on
  top in its own project; never fork or edit the owner's version.
```

**Contract violation:**
```
1. Importing without an exact pinned version (e.g. "@latest")
   → BOUNDARY VIOLATION, MAJOR severity
2. A consumer editing, re-assigning IDs in, or copying the owner's
   version into its own registry
   → CRITICAL violation (breaks PRINCIPLE-13 isolation + RULE-15 immutability)
3. An import not declared in the consumer's project-manifest imports
   (implicit cross-project reach) → BOUNDARY VIOLATION, MAJOR severity
```

---

═══════════════════════════════════════════════════════════════════
# CONTRACT-15 — Version Resolution Event (VRE) (NEW, v4.0)
═══════════════════════════════════════════════════════════════════

```
Initiator : P-DOMAIN of the OWNER domain (when it publishes a new
            version of a Model/Extension that others depend on)
Target    : each dependent project/domain (via its project-manifest)
Responder : the dependent's own P-DOMAIN / P(-1) session (records the
            decision) — never auto-applied
```

**This is the version-change analogue of CONTRACT-8 (RXE)** — same shape,
applied to Model/Extension version publishes instead of XM DEFERRED→READY.

**What the VRE carries to each dependent:**
```
VRE-ID          : VRE-[TARGET]-[SEQ]
Affected item   : Model/Extension + new version (e.g. Model-A@v2)
Change class    : ADDITIVE | BREAKING
Required action : evaluate impact; decide pin-stay or opt-in upgrade
```

**Dependent response (recorded, never assumed):**
```
ADDITIVE  → may adopt the new extension/minor at will; staying on the
            pinned version is safe. The decision is recorded in the
            dependent's project-manifest imports.
BREAKING  → the dependent STAYS on its pinned older version unless it
            explicitly upgrades; the upgrade is recorded (new pinned
            version in project-manifest), never applied silently.
```

**Immutability guarantee:** the owner NEVER edits the published version
that dependents pin. A change is a NEW version; the old stays frozen and
importable (RULE-15). So a dependent that does nothing keeps working.

**Contract violation:**
```
1. A dependent auto-moved to a new version without a recorded decision
   → CRITICAL violation (silent upgrade — breaks RULE-15's opt-in rule)
2. An owner editing a published version in place instead of publishing a
   new one → CRITICAL violation (immutability breach)
3. A new depended-on version published with NO VRE raised to dependents
   → INCOMPLETE, MAJOR severity (dependents left uninformed)
```

---

═══════════════════════════════════════════════════════════════════
# CONTRACT QUICK REFERENCE
═══════════════════════════════════════════════════════════════════

**srs.md structure (canonical, unchanged):**
```
PART A — Module Foundation   : A1 (Info) | A2 (Context) | A3 (Entities) |
                               A4 (Rules) | A5 (LOVs) | A6 (Lifecycle) | A7 (Dependencies)
PART B — Screen Specs        : Per SCR-ID → B1 (Definition) | B2 (Search) |
                               B3 (Input) | B4 (Permissions) | B5 (APIs)
Standalone                   : Permissions Summary + Registry Update | OQ Log
Reading protocol:
  P2   reads : PART A (A3 + A4 + A5 + A7)
  P2.5 reads : prd.md (parallel with P1) to draft; then PART B (B1-B4)
               at the Reconciliation Gate before human approval
  P3.1 reads : PART A once → target SCR block in PART B (+ B5 for APIs)
  P3.2 reads : PART B (B1-B4) — jointly with real API Docs + P2.5 outputs
  P4.1 reads : PART A + all PART B blocks + Permissions Summary
  P4.2 reads : PART B blocks relevant to frontend + Permissions Summary
  TEST-GEN reads : A4 Test-Hints + the relevant execution-plan (BE/FE)
```

```
╔══════════════╦════════════════╦════════════════╦══════════════════════════╗
║ CONTRACT     ║ FROM           ║ TO             ║ INTERFACE ITEM           ║
╠══════════════╬════════════════╬════════════════╬══════════════════════════╣
║ CONTRACT-1   ║ Project 2      ║ Project 3.1    ║ DBF-ID (ref only)        ║
║ CONTRACT-2   ║ Project 2      ║ Project 3.1    ║ XM-[MOD]-ID              ║
║ CONTRACT-3   ║ Project 1      ║ All projects   ║ OQ count + IDs           ║
║ CONTRACT-4   ║ Project 3.1    ║ F3, TC         ║ ERR-ID (ref only)        ║
║ CONTRACT-5   ║ Project 4.1/4.2║ (each own)     ║ Finding lifecycle (×2)   ║
║ CONTRACT-6   ║ All projects   ║ All projects   ║ MGI state view           ║
║ CONTRACT-7   ║ Owner module   ║ Consumer SRS   ║ ENTITY-ID (canon)        ║
║ CONTRACT-8   ║ Reg. Maint.    ║ Project 3.1    ║ RXE-ID event             ║
║ CONTRACT-9   ║ Project 3      ║ Test Gen Engine║ ERR/RULE/API/FIELD-ID    ║
║              ║ exec-plan(×2)  ║ test-plan(×2)  ║ (ref only) — ALIGN-BE/FE ║
║ CONTRACT-10  ║ Project 0      ║ Project 0.5    ║ module-registry+policies ║
║ CONTRACT-11  ║ P0.5 + P1      ║ Project 2.5    ║ PRD+SRS (Reconcile Gate) ║
║ CONTRACT-12  ║ Real backend + ║ Project 3.2    ║ Real API Docs + Real     ║
║              ║ Project 2.5 +  ║                ║ UI Shell code (v2.1) +   ║
║              ║ Real UI Shell  ║                ║ flow-diagram/ui-ux-spec  ║
║ CONTRACT-13  ║ Test Gen Engine║ Project 5      ║ test-execution-manifest  ║
║ CONTRACT-14  ║ Owner P-DOMAIN ║ Consumer proj. ║ pinned read-only import  ║
║  (v4.0)      ║ + P(-1) catalog║ (manifest)     ║ Model/Ext@vN             ║
║ CONTRACT-15  ║ Owner P-DOMAIN ║ Dependent proj.║ VRE-ID (version change)  ║
║  (v4.0)      ║                ║                ║ ADDITIVE | BREAKING      ║
╚══════════════╩════════════════╩════════════════╩══════════════════════════╝
```

Every "INTERFACE ITEM" column represents the ONLY content that
crosses the contract boundary. Everything else stays at its owner.

---

═══════════════════════════════════════════════════════════════════
# CHANGE SUMMARY (for audit trail)
═══════════════════════════════════════════════════════════════════

```
v4.0:
ADDED     : CONTRACT-14 (versioned reuse import — pinned, read-only,
            cross-project, never mutates the owner).
ADDED     : CONTRACT-15 (Version Resolution Event — version-change
            propagation, the version analogue of CONTRACT-8/RXE).
ADDED     : P-DOMAIN (domain evolution authority) to the governed
            engine list; VRE-ID as a shared event ID.
UPDATED   : CONTRACT-3/7 — "master-registry.md" references now resolve
            to the SELECTED project's project-registry.md (v4.0 per-
            project registry); CONTRACT-7 scoped to WITHIN a project,
            cross-project reuse handed to CONTRACT-14/15.
UPDATED   : CONTRACT-8 — noted CONTRACT-15 as its version analogue.

v3.0:
REWRITTEN : CONTRACT-9 — test-plans + TC namespaces moved from Project 3
            to the standalone Test Generation Engine (outside pipeline).
            Execution plans are LIGHT (no TC blocks / SECTION D).
REVISED   : CONTRACT-13 — manifest owner Project 3.1 → Test Generation Engine.
UPDATED   : CONTRACT-5 — P4.1/P4.2 read no test artifact; CHECK-4 removed.
UPDATED   : CONTRACT-4 — TC consumers are the Test Gen Engine's test-plans.
ADDED     : TEST-GEN to the governed engine list.

v2.0 / v2.1:
CONTRACT-5 dual gate | CONTRACT-9 BE/FE split | CONTRACT-10 (PRD gate) |
CONTRACT-11 (Reconciliation Gate) | CONTRACT-12 (Backend Module Complete
+ UI Shell) | CONTRACT-13 (manifest → P5).
```

---

*End of SHARED-ARTIFACT-CONTRACTS.md (v4.0)*
*Embedded in every project's system prompt: P0.5, P1, P2, P2.5, P3, P4.1,*
*P4.2, P5, P-DOMAIN, and the standalone Test Generation Engine.*
*15 contracts governing all inter-project and inter-artifact interfaces.*
