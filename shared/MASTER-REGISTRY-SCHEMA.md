# ERP GOVERNANCE — MASTER-REGISTRY SCHEMA
## Canonical Registry Structure Standard

```
File ID        : MASTER-REGISTRY-SCHEMA
Version        : 2.3 — Flexible Category Model (was: fixed section list)
Status         : MANDATORY — governs master-registry.md CONTENT COVERAGE
                 across any project using this governance methodology
                 (the methodology is domain-general — ERP is the worked
                 example throughout this file, not a hard requirement;
                 see SECTION 1A)
Authority      : All governance engines (P(-1) through P5) read and
                 write to master-registry.md according to this schema
Maintained by  : Architecture Authority (human — registry maintainer)
                 Governance engines populate fields; humans own the file
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — PURPOSE AND GOVERNANCE MODEL
═══════════════════════════════════════════════════════════════════

master-registry.md is the SINGLE cross-module state authority for the
entire ERP governance ecosystem. It is the source of truth for:

- Which modules exist and their pipeline status
- Which entities exist, who owns them, and which are SHARED
- Which tables exist, under which DBS-IDs
- Which XM dependencies exist across the ecosystem (the global XM index)
- Which open OQ and XM Resolution Events are active ecosystem-wide

It is NOT:
- A replacement for module-level artifacts (srs.md, db-script.md)
- A truth layer (it is operational state, not governed content)
- A substitute for the Module Governance Index (MGI tracks per-module
  execution state; registry tracks cross-module entity and pipeline state)
- **A gating input for analysis depth or completeness (see rule below)**
- **A second source of truth for DB_TARGET, stack, or any other
  GOVERNANCE-CONFIG.md-owned setting.** GOVERNANCE-CONFIG.md is the
  exclusive owner of those values for GENERATION purposes (see
  CORE-8) — every engine reads the operative value from there, never
  from this file. In practice, the registry maintainer commonly also
  notes such a value in the Section 3 Registry Header as a dated,
  attributed DECISION RECORD (e.g. "DB Target: POSTGRESQL_16
  (confirmed by Architect 2026-09-02)") — that is legitimate,
  human-owned context, not a schema violation, and is not required to
  be removed. What is never legitimate is DISAGREEMENT: if this
  file's note and GOVERNANCE-CONFIG.md's declared value differ,
  GOVERNANCE-CONFIG.md's value is used regardless, and the difference
  is flagged as an advisory for the registry maintainer to reconcile
  (see CORE-10 STEP A item 5) — never silently ignored, and never
  cause to hesitate on GOVERNANCE-CONFIG.md's value.

**CRITICAL RULE — Status fields never reduce generation completeness:**
```
The Module Index Status column (Section 4) and the Pipeline Status
Grid (Section 10) record WHERE a module currently is in the pipeline
— NOT STARTED, IN PROGRESS, GOVERNANCE REDUCED, BLOCKED, COMPLETE,
MAINTENANCE, etc. These are TRACKING/NAVIGATION fields only.

No governance engine may use a module's recorded Status — its own or
any OTHER module's — to skip, truncate, abbreviate, or otherwise
reduce the completeness of analysis, SRS content, execution plans,
audits, or any other generated artifact. A module recorded as
"COMPLETE," "MAINTENANCE," "DEFERRED," or "NOT STARTED" elsewhere in
the registry gets exactly the same full-depth treatment from every
engine as a module with no recorded status at all.

This applies with equal force whether the status belongs to the
module currently being worked on or to a DIFFERENT module referenced
via a SHARED entity or XM dependency — e.g., discovering that a
dependency's target module shows status "NOT STARTED" or "DEFERRED"
is informational (it may affect an XM-ID's own Status: DEFERRED, see
Section 8) but is NEVER a reason to generate a shorter, partial, or
hedged analysis for the module actually being worked on right now.

Rationale: master-registry.md is operational bookkeeping, not
governed content (see "It is NOT" list above). Treating a
bookkeeping field as if it were a legitimate reason to produce less
complete governance output would let an administrative fact
(is a MODULE implemented yet) improperly influence a completely
separate concern (should THIS ANALYSIS be complete). The two are
unrelated by design.
```

**Write discipline:** Only canonical REGISTRY UPDATE blocks (per mode)
write to master-registry.md. No session writes arbitrary content.
Every write is a structured REGISTRY UPDATE block. The registry
maintainer applies REGISTRY UPDATE blocks in pipeline order.

**Read discipline:** Every governance engine entry gate reads the
relevant sections before proceeding. Reading is always the full
relevant section — not partial lookups. Per the CRITICAL RULE above,
reading this data is for CONTEXT AND NAVIGATION only — never as an
input that shortens what gets generated.

---

═══════════════════════════════════════════════════════════════════
# SECTION 1A — DOMAIN GENERALITY (NEW, v2.3)
═══════════════════════════════════════════════════════════════════

This governance methodology — and this Schema — describes a general
analysis and governance framework, not an ERP-only one. ERP is the
worked example used throughout this file (module names like Finance
GL, Procurement, HR Payroll; ID prefixes like FIN, PRC, HRP) because
it is a concrete, familiar domain that makes every rule easy to
illustrate. It is not a constraint on what kind of platform this
methodology can govern.

A project built on this methodology may be an ERP system, a general
software platform, or any other system decomposed into modules or
components with entities, dependencies, and a multi-stage delivery
pipeline. What this Schema requires is that master-registry.md
COVERS the canonical content categories in SECTION 2 — not that it
uses ERP vocabulary, ERP section names, or the exact section layout
shown in Part B (SECTIONS 3-13) of this file.

Real-world evidence: a production registry for a non-ERP-flavored
platform ("Enterprise Engine Platform" — layers: Foundation, Smart
Engines, Operational Modules, Reporting, Applications) already uses
a 13-section structure with different section names, different
groupings, and a different section count than Part B's template,
while still substantively satisfying nearly every canonical category
in SECTION 2. See the worked mapping at the end of SECTION 2.

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — CONTENT COVERAGE MODEL (v2.3 — FLEXIBLE)
═══════════════════════════════════════════════════════════════════

**What changed in v2.3:** Prior versions of this Schema required
master-registry.md to contain EXACTLY nine (plus 8A) named sections,
in a fixed order, with no renaming permitted, and required a formal
GOVERNANCE EXCEPTION for any deviation. That rule is RETIRED. It made
this Schema incompatible with real, working projects that organize
the same governance content differently — including non-ERP
projects, where ERP-flavored section names do not fit at all.

**What replaces it:** master-registry.md must COVER nine CANONICAL
CONTENT CATEGORIES, in substance. A project may name, group, split,
merge, or order its actual sections however suits its domain — as
long as every category below is findable somewhere in the file.

```
CANONICAL CONTENT CATEGORIES (v2.3):

CAT-1  REGISTRY IDENTITY & VERSIONING
       What the registry is, what platform/system it governs, its
       own version, and the naming/governance conventions in force.
       (Part B reference: SECTION 3 — Registry Header;
       SECTION 13 — Naming Conventions)

CAT-2  MODULE / COMPONENT INDEX
       Every module or top-level component that exists, its status,
       and its pipeline/delivery stage.
       (Part B reference: SECTION 4 — Module Index)

CAT-3  ENTITY / DATA OBJECT OWNERSHIP
       Every entity or data object, which module/component owns it,
       and whether it is private or shared.
       (Part B reference: SECTION 5 — Entity Ownership Registry)

CAT-4  SHARED ENTITY / REFERENCE DECLARATIONS
       Canonical source declarations for entities or reference data
       consumed by more than one module/component.
       (Part B reference: SECTION 6 — Shared Entity Declarations)

CAT-5  STRUCTURAL / IMPLEMENTATION REGISTRY
       The physical or structural artifacts implementing the
       entities above (tables, schemas, storage objects, or their
       domain equivalent).
       (Part B reference: SECTION 7 — Table Registry)

CAT-6  CROSS-COMPONENT DEPENDENCY INDEX(ES)
       Every dependency that crosses a module/component boundary,
       tracked at the ecosystem level. Where a project's pipeline
       distinguishes structural/backend dependencies from
       application-layer/frontend dependencies (as this ecosystem's
       XM-ID vs UXD-ID split does), each gets its OWN index — they
       are never merged into one namespace or one table.
       (Part B reference: SECTION 8 — Global XM Dependency Index;
       SECTION 8A — Global UXD Dependency Index)

CAT-7  OPEN QUESTION / ESCALATION INDEX
       Cross-module or cross-team open questions that need
       resolution outside the raising module/component.
       (Part B reference: SECTION 9 — Global OQ Escalation Index)

CAT-8  PIPELINE / PROGRESS STATUS
       An at-a-glance view of where every module/component stands
       in its delivery pipeline.
       (Part B reference: SECTION 10 — Pipeline Status Grid)

CAT-9  CHANGE / EVENT HISTORY
       An append-only record of what changed in the registry, when,
       and by which engine/process.
       (Part B reference: SECTION 11 — Registry Event Log)
```

**Coverage rule:** All nine categories must be covered IN SUBSTANCE.
A category is "covered" when the information it describes is
recorded somewhere in the file in a form a governance engine can
reliably read — not when a section carries the category's literal
name. A project may satisfy two categories in one section, split one
category across several sections, or use entirely different
terminology, provided the substance is present and locatable.

**Schema Compliance Map — REQUIRED:**
Every master-registry.md must carry, near its header, a short table
mapping its OWN section names to the canonical categories above.
This is what makes an unfamiliar registry structure auditable by
P4.1/P4.2/the Master Reviewer without requiring ERP-specific naming:

```
## SCHEMA COMPLIANCE MAP
══════════════════════════════════════════════════════════════════
This Registry's Section          │ Canonical Category
──────────────────────────────────┼──────────────────────────────
[this project's own section name] │ CAT-[N]
[this project's own section name] │ CAT-[N]
...                                │ ...
══════════════════════════════════════════════════════════════════
Uncovered categories (if any)     : [list, or "None"]
```

A registry with an uncovered category is not automatically invalid
— P4.1/P4.2 raise it as a finding and the registry maintainer
decides whether it is a real gap or genuinely not applicable to that
project's domain (e.g., a project with no application-layer/frontend
split has no need for a second row under CAT-6).

**No formal GOVERNANCE EXCEPTION is required** to organize a
registry differently from Part B's template — that template is a
reference default, not a mandatory literal structure (v2.3 change;
previously this required a GOVERNANCE EXCEPTION for any deviation).
A GOVERNANCE EXCEPTION IS still required to OMIT a canonical
category's substance entirely, with no equivalent recorded anywhere.

---

## PART A vs PART B

This file has two parts from here on:

**PART A (SECTIONS 1, 1A, 2 above)** — the MANDATORY content-coverage
model. This is what every project must satisfy, regardless of domain.

**PART B (SECTIONS 3-13 below)** — a REFERENCE DEFAULT TEMPLATE: a
complete, detailed, ERP-flavored worked example showing one valid way
to structure a registry that satisfies Part A. A new project with no
strong reason to do otherwise should start from Part B directly — it
is fully specified and ready to use. A project with a different
domain, or an existing registry with a different (but substantively
compliant) structure, uses Part A's categories and its own Schema
Compliance Map instead, and is NOT required to rename its sections to
match Part B's ERP-flavored names.

Every exact section number referenced elsewhere in this ecosystem
(e.g., "Section 8A" in the Global UXD Dependency Index, "Section 14"/
"Section 15" in PROJECT-0-PLATFORM-INCEPTION-ENGINE-v2.md's registry
update blocks) refers to PART B's numbering specifically. A project
using its own structure per Part A translates those references via
its own Schema Compliance Map (e.g., "Section 8A" → CAT-6, second
row → whatever that project calls its application-layer dependency
index).

---

## WORKED EXAMPLE — A REAL, NON-ERP-TEMPLATE REGISTRY MAPPED TO PART A

A real production registry (platform: "Enterprise Engine Platform",
layers: Foundation → Smart Engines → Operational Modules → Reporting
→ Applications) uses a 13-section structure that does not match Part
B's names, grouping, or count. Its actual Schema Compliance Map,
reconstructed against the categories above:

```
## SCHEMA COMPLIANCE MAP (worked example)
══════════════════════════════════════════════════════════════════
This Registry's Section              │ Canonical Category
────────────────────────────────────────┼──────────────────────────
Project Information                    │ CAT-1
Platform Layer Structure               │ CAT-1 (architectural context)
Module Registry                        │ CAT-2
Naming & Data Governance Rules         │ CAT-1 (conventions)
Entity Registry                        │ CAT-3
Data Ownership                         │ CAT-3
Shared Lookup & Reference Tables       │ CAT-4 / CAT-5
Module Dependencies                    │ CAT-6
Cross-Module Integration Rules         │ CAT-6 (rules, not index rows)
Internal Module Pattern                │ (domain-specific — no canonical
                                          category; not required by
                                          Part A)
Open Architectural Questions           │ CAT-7
P0 Architecture Convergence Status     │ CAT-8
Progress Snapshot                      │ CAT-8
══════════════════════════════════════════════════════════════════
Uncovered categories: CAT-9 (Change/Event History) — not present as
a distinct section in this snapshot; recommended finding for the
registry maintainer, not a structural non-compliance (the substance
may exist elsewhere, e.g. version control history).
```

This is the proof that Part A's flexible model works in practice:
nearly every substantive category this ecosystem depends on IS
present in this real registry, under this project's own vocabulary
— proving the coverage model (not the literal Part B template) is
the actual compliance bar. The one gap found (CAT-9) is exactly the
kind of finding this model is meant to surface: specific, actionable,
and never grounds to reject the registry's overall structure as
"non-compliant" for using different section names.

---

═══════════════════════════════════════════════════════════════════
# PART B — REFERENCE DEFAULT TEMPLATE (SECTIONS 3-13)
═══════════════════════════════════════════════════════════════════

Everything from here to the end of this file is Part B: a complete,
ready-to-use, ERP-flavored registry template that satisfies every
canonical category in SECTION 2. Use it as-is unless the project's
domain or an existing registry structure gives a specific reason to
organize the content differently (in which case, use Part A's
categories plus a Schema Compliance Map instead — see SECTION 2).
All section numbers below (3 through 13, including 8A) are internal
to Part B and are what other ecosystem files mean when they cite an
exact section number of this Schema.

═══════════════════════════════════════════════════════════════════
# SECTION 3 — REGISTRY HEADER
═══════════════════════════════════════════════════════════════════

```
# MASTER-REGISTRY — [ERP System Name]
══════════════════════════════════════════════════════════════════
Registry Version : [semver — e.g., 1.4.2]
Last Updated     : [date of most recent REGISTRY UPDATE applied]
Last Updated By  : [mode that triggered the update — e.g., MODE 1.5]
Module Count     : [N]
Active XM-IDs    : [total count across all modules]
Active OQ-IDs    : [total count across all modules]
Schema Version   : [MASTER-REGISTRY-SCHEMA.md version this conforms to]
══════════════════════════════════════════════════════════════════
```

This is the required field list — every field here must be present.
The registry maintainer may add informational fields beyond this list
(Platform Name, Domain, a dated DB_TARGET/stack decision note, etc.) —
common practice, and legitimate context, per Section 1's "It is NOT"
entry on GOVERNANCE-CONFIG.md-owned settings. Any added field is
informational only: never authoritative over, and never a substitute
for, the corresponding GOVERNANCE-CONFIG.md value.

---

═══════════════════════════════════════════════════════════════════
# SECTION 4 — MODULE INDEX
═══════════════════════════════════════════════════════════════════

One row per module. Modules are added when MODE 1 begins for that module.

```
## MODULE INDEX
══════════════════════════════════════════════════════════════════════════
Module        │ Prefix │ Status              │ Pipeline Stage  │ Feature Codes
──────────────┼────────┼─────────────────────┼─────────────────┼──────────────
Finance GL    │ FIN    │ BACKEND BUILDING    │ P3.1 — SVC-API  │ FIN-001
Procurement   │ PRC    │ GOVERNANCE REDUCED  │ P1 — REDUCED    │ PRC-001
HR Payroll    │ HRP    │ NOT STARTED         │ —               │ —
══════════════════════════════════════════════════════════════════════════

Status Values (v2.1 — matches shared-governance-rules.md Section 4
State Machine exactly; do not drift from that definition):
  NOT STARTED             — Module registered; no pipeline activity yet
  P0 IN PROGRESS          — Architecture convergence active
  P0.5 GATE               — PRD Engine running (hard-gates P1, v2.1)
  IN PROGRESS             — P1→P2 executing, P2.5-draft running in parallel
  GOVERNANCE REDUCED      — Pipeline running without DB Script
  GOVERNANCE RECOVERY     — DB Script arrived; upgrading from REDUCED to FULL
  BACKEND PLANNED         — P3.1 ALIGN-BE ✓
  BACKEND BUILDING        — IMPL-BE in progress
  BACKEND MODULE COMPLETE — GATE confirmed (CONTRACT-12): impl + real
                            API Docs + UI/UX approved
  FRONTEND PLANNED        — P3.2 ALIGN-FE ✓
  FRONTEND BUILDING       — IMPL-FE in progress
  BLOCKED                 — Pipeline halted pending resolution of blocking item
  COMPLETE                — Both P4.1 and P4.2 CLEARED; both builds done
  MAINTENANCE             — Complete module receiving change requests

⚠ These Status values are TRACKING fields only — see the CRITICAL RULE
  in Section 1. No engine reduces analysis completeness based on them.
```

**Module Prefix rules:**
- 3 uppercase letters
- Unique across the registry
- Used in: ENTITY-ID, RULE-ID, XM-ID prefixes for this module
- Once assigned, never changed (ID continuity)

---

═══════════════════════════════════════════════════════════════════
# SECTION 5 — ENTITY OWNERSHIP REGISTRY
═══════════════════════════════════════════════════════════════════

One row per ENTITY-ID across all modules. Added by each module's
MODE 1 REGISTRY UPDATE.

```
## ENTITY OWNERSHIP REGISTRY
══════════════════════════════════════════════════════════════════════════════════
ENTITY-ID       │ Entity Name       │ Owner Module │ Type    │ Source SRS
────────────────┼───────────────────┼──────────────┼─────────┼────────────
ENTITY-FIN-001  │ Journal Entry     │ Finance GL   │ PRIVATE │ FIN-001
ENTITY-FIN-002  │ GL Account        │ Finance GL   │ PRIVATE │ FIN-001
ENTITY-ORG-001  │ Organization Unit │ Org Master   │ SHARED  │ ORG-001
ENTITY-FIN-003  │ Fiscal Year       │ Finance GL   │ SHARED  │ FIN-001
══════════════════════════════════════════════════════════════════════════════════

Type Values:
  PRIVATE  — Entity belongs to one module; other modules must not define it
  SHARED   — Entity is mastered by owner-module; other modules consume read-only
```

**Conflict detection:** If two REGISTRY UPDATEs attempt to register the
same entity name under different ENTITY-IDs, this is a DUPLICATE finding.
The registry maintainer raises the conflict before applying either update.
The SRS Governance Engine of the module with the earlier feature code owns
the naming decision.

---

═══════════════════════════════════════════════════════════════════
# SECTION 6 — SHARED ENTITY DECLARATIONS
═══════════════════════════════════════════════════════════════════

All SHARED entities are listed here with their canonical source.
Consumer modules reference these declarations — they do not create
their own ENTITY-IDs for shared entities.

```
## SHARED ENTITY DECLARATIONS
══════════════════════════════════════════════════════════════════════════════════════
ENTITY-ID       │ Entity Name       │ Owner Module │ DBS-ID     │ Table Name
────────────────┼───────────────────┼──────────────┼────────────┼──────────────
ENTITY-ORG-001  │ Organization Unit │ Org Master   │ DBS-ORG-01 │ ORG_UNIT
ENTITY-FIN-003  │ Fiscal Year       │ Finance GL   │ DBS-FIN-01 │ FIN_FISCAL_YEAR
ENTITY-SYS-001  │ Currency          │ System Core  │ DBS-SYS-01 │ SYS_CURRENCY
ENTITY-SYS-002  │ System User       │ System Core  │ DBS-SYS-01 │ SYS_USER
══════════════════════════════════════════════════════════════════════════════════════

Consumer Module Rule:
  A consumer module referencing ENTITY-ORG-001 in its SRS writes:
  "Consumes SHARED ENTITY-ORG-001 (Organization Unit) — see master-registry"
  It does NOT assign a new ENTITY-ID for Organization Unit.
  It does NOT create a new table — it references ORG_UNIT via XM dependency.
```

**Change impact governance:**
When an owner-module amends a SHARED entity (new fields, deprecated fields,
constraint changes), all consumer-module XM dependencies for that entity
receive an XM RESOLUTION EVENT notification.
(See XM-RESOLUTION-EVENT-PROTOCOL.md)

---

═══════════════════════════════════════════════════════════════════
# SECTION 7 — TABLE REGISTRY
═══════════════════════════════════════════════════════════════════

One row per DB table across all modules. Added by each module's
MODE 1.5 REGISTRY UPDATE. This is the cross-module table namespace
authority — no two modules create tables with the same name.

```
## TABLE REGISTRY
══════════════════════════════════════════════════════════════════════════════
Table Name          │ Owner Module │ DBS-ID      │ ENTITY-ID Source
────────────────────┼──────────────┼─────────────┼──────────────────
FIN_JOURNAL_ENTRY   │ Finance GL   │ DBS-FIN-01  │ ENTITY-FIN-001
FIN_GL_ACCOUNT      │ Finance GL   │ DBS-FIN-01  │ ENTITY-FIN-002
FIN_FISCAL_YEAR     │ Finance GL   │ DBS-FIN-01  │ ENTITY-FIN-003
PRC_PURCHASE_ORDER  │ Procurement  │ DBS-PRC-01  │ ENTITY-PRC-001
══════════════════════════════════════════════════════════════════════════════
```

**Naming conflict rule:** If a MODE 1.5 REGISTRY UPDATE attempts to
register a table name already in the registry under a different module,
this is a governance CRITICAL finding. The DB Governance Engine of the
conflicting module halts MODE 1.5 until naming is resolved via the SRS
and MASTER-REGISTRY.

---

═══════════════════════════════════════════════════════════════════
# SECTION 8 — GLOBAL XM DEPENDENCY INDEX
═══════════════════════════════════════════════════════════════════

The ecosystem-level view of all XM dependencies. The module-level
XM Register (in each db-script.md) is the structural detail source.
This index is the cross-module tracking and orchestration layer.

```
## GLOBAL XM DEPENDENCY INDEX
══════════════════════════════════════════════════════════════════════════════════════
XM-ID        │ Type      │ From Module  │ To Module    │ Status    │ RXE-ID
─────────────┼───────────┼──────────────┼──────────────┼───────────┼──────────────
XM-FIN-001   │ HARD-FK   │ Finance GL   │ Org Master   │ READY     │ —
XM-FIN-002   │ HARD-FK   │ Finance GL   │ System Core  │ DEFERRED  │ RXE-SYS-001
XM-FIN-003   │ SOFT-READ │ Finance GL   │ System Core  │ READY     │ —
XM-PRC-001   │ HARD-FK   │ Procurement  │ Finance GL   │ DEFERRED  │ —
══════════════════════════════════════════════════════════════════════════════════════

Column definitions:
  XM-ID    : Qualified format XM-[MODULE-PREFIX]-[SEQ]
  Type     : HARD-FK (physical constraint) | SOFT-READ (application-layer read)
  From     : Module that has the dependency
  To       : Module that owns the target entity/table
  Status   : READY | DEFERRED | CONDITIONAL | CLOSED
  RXE-ID   : XM Resolution Event ID if an active event exists (see Section 10)

Status Values:
  READY       — Dependency resolved; target DBS-ID confirmed and available
  DEFERRED    — Target module DB Script not yet available
  CONDITIONAL — Target module exists but is in GOVERNANCE REDUCED state
  CLOSED      — Dependency physically implemented; Project 4.1 (Backend
                Audit Gate) CHECK-5 confirmed
```

**Index update discipline:**
- Added: when Module X's Project 2 (DB Engine) generates an XM-ID
- Status DEFERRED→READY: when target module's Project 2 gates with its DBS-ID
- Status READY→CLOSED: when Module X's Project 4.1 CHECK-5 confirms FK
  constraint applied (NOTE: this previously referenced "MODE 4B" —
  corrected here; MODE 4B was already abolished ecosystem-wide and
  this reference was simply never updated, the same pre-existing gap
  found and fixed in PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md and
  XM-RESOLUTION-EVENT-PROTOCOL.md)
- SOFT-READ added: when Module X's SRS identifies a SOFT-READ dependency in
  Section 5.5.1 cross-module candidate analysis

═══════════════════════════════════════════════════════════════════
# SECTION 8A — GLOBAL UXD DEPENDENCY INDEX (NEW, v2.2)
═══════════════════════════════════════════════════════════════════

The ecosystem-level view of all Frontend-visible, application-layer
cross-module data dependencies (UXD-IDs). This index is entirely
separate from the GLOBAL XM DEPENDENCY INDEX (Section 8) — UXD-ID
never shares a namespace, counter, or register with XM-ID, and this
index is never read or written by Project 2, Project 3.1, or
Project 4.1.

```
## GLOBAL UXD DEPENDENCY INDEX
══════════════════════════════════════════════════════════════════════════════════════
UXD-ID        │ Screen Module │ Data Owner Module │ Field/Data        │ Status
─────────────┼───────────────┼────────────────────┼───────────────────┼──────────
UXD-FIN-001   │ Finance GL    │ HR                 │ Employee Name     │ OPEN
UXD-PRC-001   │ Procurement   │ Org Master         │ Cost Center Name  │ CLOSED
══════════════════════════════════════════════════════════════════════════════════════

Column definitions:
  UXD-ID           : Qualified format UXD-[MODULE-PREFIX]-[SEQ]
  Screen Module    : Module that owns the screen displaying the foreign data
  Data Owner Module: Module that owns the real API this data is sourced from
  Field/Data       : What is being displayed
  Status           : OPEN | CLOSED

Status values:
  OPEN   — Registered by Project 2.5; not yet confirmed by Project 4.2
  CLOSED — Project 4.2 confirmed a real, documented API satisfies this
           UXD-ID (see PROJECT-4-FRONTEND-AUDIT.md)
```

**Index update discipline:**
- Added: when Module X's Project 2.5 (UI/UX Design Engine) identifies a
  cross-module data-display need while drafting flow-diagram.md/ui-ux-spec.md
- Status OPEN→CLOSED: when Module X's Project 4.2 confirms a real,
  documented API satisfies the dependency
- This index is informational for Project 3.2 (which references, never
  reassigns, UXD-IDs when documenting frontend-execution-plan.md) and is
  never a gating input for Project 2, Project 3.1, or Project 4.1

═══════════════════════════════════════════════════════════════════
# SECTION 9 — GLOBAL OQ ESCALATION INDEX
═══════════════════════════════════════════════════════════════════

Tracks OQs that have been escalated across module boundaries
(OQ ESCALATION field = XM-ESCALATION-[MODULE]).
These are cross-module questions that require input from a team
other than the raising module's team.

```
## GLOBAL OQ ESCALATION INDEX
══════════════════════════════════════════════════════════════════════════════
OQ-ID        │ Raising Module │ Target Module │ Question summary  │ Status
─────────────┼────────────────┼───────────────┼───────────────────┼──────────
OQ-FIN-003   │ Finance GL     │ Org Master    │ ORG_UNIT FK reqs  │ OPEN
OQ-PRC-001   │ Procurement    │ Finance GL    │ GL code mapping   │ RESOLVED
══════════════════════════════════════════════════════════════════════════════
```

**Escalation rule:** A cross-escalated OQ is tracked here AND mirrored
as an INFO Finding in the target module's Project 4 audit session.
Target module team acknowledges the OQ at their next governance entry gate.

---

═══════════════════════════════════════════════════════════════════
# SECTION 10 — PIPELINE STATUS GRID
═══════════════════════════════════════════════════════════════════

Quick-reference view of every module's pipeline position.
Updated by each REGISTRY UPDATE from any mode.

```
## PIPELINE STATUS GRID
═══════════════════════════════════════════════════════════════════════════════════════
Module        │ M1   │ M1.5 │ M2   │ 4A   │ M3   │ 4B   │ ALIGN │ Notes
──────────────┼──────┼──────┼──────┼──────┼──────┼──────┼───────┼──────────────────
Finance GL    │  ✓   │  ✓   │  ✓   │  ✓   │  ⚙   │  —   │  ✓    │ M3 in progress
Procurement   │  ✓   │  ⚠   │  ⚠   │  —   │  —   │  —   │  —    │ GOVERNANCE RED
HR Payroll    │  —   │  —   │  —   │  —   │  —   │  —   │  —    │ Not started
═══════════════════════════════════════════════════════════════════════════════════════

Legend: ✓ = PASSED | ⚙ = IN PROGRESS | ⚠ = GOVERNANCE REDUCED | — = Not reached
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 11 — REGISTRY EVENT LOG
═══════════════════════════════════════════════════════════════════

An append-only log of every REGISTRY UPDATE applied to master-registry.md.
This provides the audit trail for registry state transitions.

```
## REGISTRY EVENT LOG
══════════════════════════════════════════════════════════════════
Date       │ Engine   │ Module       │ Feature Code │ Event
───────────┼──────────┼──────────────┼──────────────┼──────────────────────
2025-01-10 │ P1       │ Finance GL   │ FIN-001      │ ENTITY-IDs registered
2025-01-12 │ P2       │ Finance GL   │ FIN-001      │ DBS-FIN-01 gated; XM-FIN-001,002,003 created
2025-01-15 │ P3.1     │ Finance GL   │ FIN-001      │ PLAN-FIN-01 created
2025-01-17 │ P4.1     │ Finance GL   │ FIN-001      │ P4.1 CLEARED; 2 MINOR findings
══════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 12 — REGISTRY UPDATE PROCESSING RULES
═══════════════════════════════════════════════════════════════════

When a REGISTRY UPDATE block is emitted by a governance engine,
the registry maintainer applies it according to these rules:

**Rule 1 — Apply in pipeline order (v2.1 — CORRECTED)**
P0 updates before P0.5 before P1 before P2 before P3.1 before P4.1
before P3.2 before P4.2. (NOTE: this rule previously read "MODE 1
before MODE 1.5 before MODE 2 before MODE 4A before MODE 3 before
MODE 4B" — a sequencing description that was already stale before
v2.0, since it omitted the split entirely and still referenced the
already-abolished MODE 4B. Corrected here to the full v2.1 order,
including the P0.5 hard-gate and the two independent tracks after it
— see SHARED-GOVERNANCE-CORE.md CORE-2 for the authoritative diagram;
P2.5's track runs in parallel and is not part of this strict
before/after chain.) If a later-stage update arrives before an
earlier-stage update for the same module, hold it.

**Rule 2 — Conflict check before application**
Before applying, check:
- Entity name conflicts (Section 4)
- Table name conflicts (Section 6)
- XM-ID namespace conflicts (globally qualified XM-IDs should not conflict)
If any conflict: STOP. Raise as GOVERNANCE EXCEPTION. Do not apply.

**Rule 3 — Cascade XM status on DBS-ID gate**
When Project 2 REGISTRY UPDATE adds a new DBS-ID for Module X:
Scan Global XM Dependency Index for all rows where To Module = X
and Status = DEFERRED. For each: evaluate whether the new DBS-ID
satisfies the DEFERRED condition. If yes: create XM RESOLUTION EVENT
(see XM-RESOLUTION-EVENT-PROTOCOL.md). If DBS-ID is GOVERNANCE REDUCED:
update Status to CONDITIONAL, not READY.

**Rule 4 — Closed XM confirmation**
When Project 4.1 REGISTRY UPDATE confirms XM-ID closure (CHECK-5):
Update Global XM Dependency Index Status to CLOSED.
Log the closure event in Registry Event Log.

**Rule 5 — No partial updates**
A REGISTRY UPDATE block is applied in full or not at all.
No partial application. If any field in the block causes a conflict,
the entire block is held until the conflict is resolved.

---

═══════════════════════════════════════════════════════════════════
# SECTION 13 — MASTER-REGISTRY NAMING CONVENTIONS
═══════════════════════════════════════════════════════════════════

```
Module prefix    : 3 uppercase letters — globally unique
                   Examples: FIN, PRC, HRP, ORG, SYS, INV, CRM
Feature code     : [MODULE-PREFIX]-[3-digit-seq]
                   Example: FIN-001, PRC-002
DBS-ID           : DBS-[MODULE-PREFIX]-[2-digit-seq]
                   Example: DBS-FIN-01
PLAN-ID          : PLAN-[MODULE-PREFIX]-[2-digit-seq]
                   Example: PLAN-FIN-01
Table name prefix: [MODULE-PREFIX]_[entity abbreviation]
                   Example: FIN_JOURNAL_ENTRY, PRC_PURCHASE_ORDER
```

---

*End of MASTER-REGISTRY-SCHEMA.md*
*Governs the CONTENT COVERAGE of master-registry.md across any project*
*using this governance methodology (Part A, SECTIONS 1-2) and supplies*
*a ready-to-use ERP-flavored default structure (Part B, SECTIONS 3-13).*
*v2.3 — Flexible Category Model: a project's registry no longer needs*
*to literally match Part B's section names/order/count; it needs a*
*Schema Compliance Map showing Part A's nine categories are covered.*
*Changes to the CANONICAL CATEGORIES themselves (Part A) still require*
*a GOVERNANCE EXCEPTION and propagation to all governance engine*
*projects. Reorganizing a single project's registry within Part A's*
*coverage model does NOT require a GOVERNANCE EXCEPTION.*
