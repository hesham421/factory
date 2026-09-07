# GOVERNANCE-CONFIG.md
## Single Source of Truth — All Configurable Platform Values

```
Document Type : Shared Configuration Layer
Loaded by      : Every Claude Project in the ecosystem, at the same tier
                 as SHARED-GOVERNANCE-CORE.md and shared-governance-rules.md
Owns           : Every value below. No other file defines a default,
                 a fallback, or a mapping table for any of these — it
                 only reads and references what is set here.
```

To change any value below, edit this file directly. No engine file
changes when a value here changes — every engine reads the current
value from this file.

---

## 1. GOVERNANCE-ROOT

```
Value    : ERP-Governance
```

Root folder name used by every Drive path template
(`[GOVERNANCE-ROOT]/...`) across all engines. Rename it here to move the
whole ecosystem's storage location; no other file changes.

**v4.0 layout (Multi-Project + Versioning).** As of v4.0 the tree under
GOVERNANCE-ROOT is organized by PROJECT → DOMAIN → {Core | Extensions |
Models}, not the old flat `[Platform]/[Module]`:

```
[GOVERNANCE-ROOT]/
├── _ecosystem/   projects-index.md · domains-index.md · reuse-registry.md
├── _backup/      (dated pre-replace copies — CORE-10)
└── [Project]/    e.g. ERP
    ├── project-manifest.md
    ├── project-registry.md
    └── [Domain]/
        ├── domain-profile.md · _versions/version-ledger.md
        ├── Core/[Module]/[PXX-Folder]/…
        ├── Extensions/ext-[name]/v{N}/[Module]/[PXX-Folder]/…
        └── Models/[Model]/v{N}/[Module]/[PXX-Folder]/…
```

The inner `[PXX-Folder]/[filename]` convention is UNCHANGED — only its
position deepened. Full spec: MULTI-PROJECT-VERSIONING-ARCHITECTURE.md.

---

## 1B. PATH VOCABULARY (v4.0 — the ONLY place Drive paths are defined)

```
Status : AUTHORITATIVE. Every engine's "Drive Dependency Table" and every
         "[GOVERNANCE-ROOT]/…" reference is written using the TOKENS below
         — never a literal folder layout. This is what makes the layout
         change in ONE place, keeps engines free of hardcoded paths, and
         lets new version slots (Extensions/Models/Releases) appear without
         editing any engine.
```

The tokens (each resolved once per session by CORE-11 + CORE-10, under the
selected Project / Domain / version context — see
MULTI-PROJECT-VERSIONING-ARCHITECTURE.md PART 1.2):

```
[ECO]        = [GOVERNANCE-ROOT]/_ecosystem/
               → projects-index.md, domains-index.md, reuse-registry.md
[MANIFEST]   = [GOVERNANCE-ROOT]/[Project]/project-manifest.md
[REGISTRY]   = [GOVERNANCE-ROOT]/[Project]/project-registry.md
               (the selected project's scoped registry)
[DOMAIN-ROOT]= [GOVERNANCE-ROOT]/[Project]/[Domain]/
               → domain-profile.md, _versions/version-ledger.md
[CTX]        = [DOMAIN-ROOT]<slot>     ← the "Artifact Context Root"
               <slot> is resolved by CORE-11 STEP P1 from the manifest's
               current context, and is exactly ONE of:
                 Core                          (default — the frozen base)
                 Extensions/ext-[name]/v{N}    (when working in an extension)
                 Models/[Model]/v{N}           (when working in a model version)
               A module artifact ALWAYS lives at:
                 [CTX]/[Module]/[PXX-Folder]/[filename]
               V5 §1E: NOTHING lives at [CTX] root. platform-summary.md →
               [PLATFORM]; module-registry-[MOD].md / business-policies-[MOD].md
               → [CTX]/[Module]/P0-Platform/ (they are per-module).
[BACKUP]     = [GOVERNANCE-ROOT]/_backup/
[STATE]      = [GOVERNANCE-ROOT]/[Project]/_router/     (AMEND-ROUTER-A — optional viewer only, V5)
               → pipeline-state.json, work-orders/, audit-findings.json,
                 generation-log.jsonl, router-config.json, receipts/
               Owned exclusively by P-ROUTER. Engines never write here;
               Stage-2 tooling drops receipts/*.json only.
[LEDGER]     = [CTX]/[Module]/_journey/journey-[mod].json   (V5 §1D.3/§1E — one per
               module, all versions; lives in its own folder, never loose)
[PLATFORM]   = [CTX]/_platform/                              (V5 §1E — platform-level files only)
[Module]/[MOD] = the module code (SEC, NOTIF, …) bound per task — a
               placeholder, not a layout choice.
```

```
RESOLUTION RULES:
  • [Project], [Domain] and <slot> are never written literally by an
    engine — CORE-11 STEP P0/P1 binds them from the session's
    `Project: <name>` line + the manifest's current Domain Release.
    Default <slot> = Core when the task does not target an extension or
    a specific model version.
  • An engine names only the TOKEN + filename, never a Core/Extensions/
    Models choice of its own. The layout lives here; the per-engine file
    LIST lives in §1C below (one authoritative map).
  • RETIRED tokens — never used as of v4.0:
      [GOVERNANCE-ROOT]/_registry/master-registry.md   → use [REGISTRY]
      [GOVERNANCE-ROOT]/[Platform]/…                     → use [CTX]/… (or
        [DOMAIN-ROOT]/… for domain-level, [ECO]/… for global)
    Any engine text still showing a retired token is read as its
    replacement above; §1C is authoritative over it.
```

---

## 1C. DRIVE DEPENDENCY MAP (v4.0 — the ONE authoritative per-engine path map)

```
Status : AUTHORITATIVE for EVERY engine's Pre-Flight (CORE-10 Step A)
         inputs and Post-Flight (Step C) outputs. Expressed entirely in
         the §1B tokens — zero hardcoded layout.

         Each engine also carries its own inline "## DRIVE DEPENDENCY
         TABLE" block for readability. Those inline blocks are a
         CONVENIENCE VIEW, not the source of truth: where an inline block
         still shows a retired path ( _registry/master-registry.md,
         [Platform]/[Module]/… ), THIS map governs and the inline block
         resolves through §1B. No engine ever hardcodes a path that
         disagrees with this map.

Universally mandatory for every engine (added on top of its row):
  [REGISTRY]  ·  [DOMAIN-ROOT]/domain-profile.md  ·  [MANIFEST]
  (all three blocking on MISSING — CORE-10 Step A item 0)
```

```
ENGINE (setup name)            │ INPUTS (Step A)                                   │ OUTPUTS (Step C)
───────────────────────────────┼──────────────────────────────────────────────────┼──────────────────────────────────────────────
P(-1) registry-builder         │ raw notes (session) · [ECO]/projects-index.md ·   │ [REGISTRY] · [ECO]/projects-index.md ·
                               │   [REGISTRY](existing) · [ECO]/reuse-registry.md  │   [ECO]/reuse-registry.md · [MANIFEST](on create)
P0  platform-inception-engine  │ vision text (session) · [REGISTRY](opt) ·         │ [CTX]/_platform/platform-summary.md ·
                               │   [CTX]/[Module]/P0-Platform/module-registry-[MOD].md (opt, extending)  │   [CTX]/[Module]/P0-Platform/module-registry-[MOD].md ·
                               │                                                    │   [CTX]/[Module]/P0-Platform/business-policies-[MOD].md
P0.5 prd-engine                │ [CTX]/_platform/platform-summary.md ·                        │ [CTX]/[Module]/P0.5-PRD/prd-[MOD].md
                               │   [CTX]/[Module]/P0-Platform/module-registry-[MOD].md ·                 │
                               │   [CTX]/[Module]/P0-Platform/business-policies-[MOD].md                 │
P1  srs-governance-engine      │ [CTX]/[Module]/P0.5-PRD/prd-[MOD].md (HARD GATE) · │ [CTX]/[Module]/P1-SRS/srs-[MOD].md
                               │   [CTX]/_platform/platform-summary.md ·                      │
                               │   [CTX]/[Module]/P0-Platform/module-registry-[MOD].md ·                 │
                               │   [CTX]/[Module]/P0-Platform/business-policies-[MOD].md · [REGISTRY]    │
P2  db-governance-engine       │ [CTX]/[Module]/P1-SRS/srs-[MOD].md · [REGISTRY]          │ [CTX]/[Module]/P2-DB/db-script-[MOD].md ·
                               │                                                    │   [REGISTRY](amended: Table + XM index)
P2.5 ui-ux-design-engine       │ [CTX]/[Module]/P0.5-PRD/prd-[MOD].md (start) ·     │ [CTX]/[Module]/P2.5-UIUX/flow-diagram-[MOD].md ·
                               │   [CTX]/[Module]/P1-SRS/srs-[MOD].md B1-B4 (reconcile)   │   ui-ux-spec-[MOD].md · visual-mockups/
P3.1 exec-plan-backend-engine  │ [CTX]/[Module]/P1-SRS/srs-[MOD].md ·                     │ [CTX]/[Module]/P3.1-Backend-Exec/
                               │   [CTX]/[Module]/P2-DB/db-script-[MOD].md · [REGISTRY]   │   backend-execution-plan-[MOD].md
P3.2 exec-plan-frontend-engine │ real API Docs (external) ·                        │ [CTX]/[Module]/P3.2-Frontend-Exec/
                               │   [CTX]/[Module]/P2.5-UIUX/{ui-ux-spec,flow-diagram}│  frontend-execution-plan-[MOD].md
                               │   · [CTX]/[Module]/P1-SRS/srs-[MOD].md                   │
TEST-GEN test-generation-engine│ [CTX]/[Module]/P3.1-Backend-Exec/backend-exec… (BE)│ [CTX]/[Module]/TEST-GEN/backend-test-plan-[MOD].md ·
                               │   [CTX]/[Module]/P3.2-Frontend-Exec/frontend-exec… │   (test-execution-manifest RETIRED, V5 §1D.6) ·
                               │   (FE) · [CTX]/[Module]/P1-SRS/srs-[MOD].md ·            │   frontend-test-plan-[MOD].md
                               │   [CTX]/[Module]/P2-DB/db-script-[MOD].md (BE ref)       │
P4.1 audit-backend-engine      │ [CTX]/_platform/platform-summary.md ·                        │ [CTX]/[Module]/P4.1-Backend-Audit/
                               │   [CTX]/[Module]/P0-Platform/module-registry-[MOD].md ·                 │   P4.1-audit-report.md
                               │   [CTX]/[Module]/P0-Platform/business-policies-[MOD].md ·               │
                               │   [CTX]/[Module]/P1-SRS/srs-[MOD].md ·                   │
                               │   [CTX]/[Module]/P2-DB/db-script-[MOD].md ·              │
                               │   [CTX]/[Module]/P3.1-Backend-Exec/backend-exec…   │
                               │   (NO test artifact — v3.0)                        │
P4.2 audit-frontend-engine     │ P4.1 report (mandatory) ·                         │ [CTX]/[Module]/P4.2-Frontend-Audit/
                               │   [CTX]/[Module]/P1-SRS/srs-[MOD].md ·                   │   P4.2-audit-report.md
                               │   [CTX]/[Module]/P3.2-Frontend-Exec/frontend-exec… │
                               │   · real API Docs · [CTX]/[Module]/P2.5-UIUX/*     │
                               │   (NO test artifact — v3.0)                        │
P5  api-verify-engine          │ [CTX]/[Module]/TEST-GEN/backend-test-plan-[MOD].md (manifest retired) │ [CTX]/[Module]/P5-api-verify/
                               │   · real API Docs                                  │   test_[mod]_apis.py + report
P-REG state-registry-extractor │ RETIRED (V5 §1D.1) — extraction is inline in each  │ (none — registry-<stage>-[MOD].md is written by the
                               │   core engine's completion protocol (§1D.4 step 2) │   engine itself, next to its stage artifact)
P-ROUTER pipeline-router       │ OPTIONAL read-only viewer (V5 §1D.1): [STATE]/* · │ [STATE]/* only — never a pipeline artifact;
                               │   [REGISTRY] · [LEDGER]                             │   engines never depend on it
                               │   OUTPUT path in this map (existence + probe)      │   (AMEND-ROUTER-A)
P-DOMAIN domain-profile-builder│ [DOMAIN-ROOT]/domain-profile.md ·                 │ [DOMAIN-ROOT]/domain-profile.md ·
                               │   [DOMAIN-ROOT]/_versions/version-ledger.md ·      │   [DOMAIN-ROOT]/_versions/version-ledger.md ·
                               │   [ECO]/domains-index.md                           │   [ECO]/domains-index.md
```

```
Notes:
  • real API Docs are a post-implementation artifact from the live
    backend (api-doc-generator) — outside the [GOVERNANCE-ROOT] tree
    unless the team separately mirrors them; no token applies.
  • To ADD an engine or change a file location, edit THIS map (and §1B
    if a new token is needed) — never an engine's inline block first.
    That is the whole point: one place, no overlap, extensible.
```

---

## 1A. PROJECT-SELECTION (v4.0 — mandatory session-start)

```
Status   : MANDATORY — blocking, runs BEFORE CORE-10 Pre-Flight Discovery
```

Every engine session MUST open with an explicit project line, e.g.:

```
Project: ERP
```

The engine then resolves that name against `[ECO]/projects-index.md`
and loads ONLY that project's context (its `[MANIFEST]`, `[REGISTRY]`,
selected `[DOMAIN-ROOT]/domain-profile.md` + `version-ledger.md`, and the
module/version subtree the task targets). If the line is absent → display
the projects index and ask; never guess, never proceed against a
mixed/unscoped context. Full protocol:
MULTI-PROJECT-VERSIONING-ARCHITECTURE.md PART 1.2. This is the same
on/off discipline every other MANDATORY value here follows.

---

## 2. DOMAIN-PROFILE

```
Status   : MANDATORY — blocking, same as DB_TARGET (not a silent
           default like GOVERNANCE-ROOT)
Value    : see domain-profile.md
```

DOMAIN-PROFILE is not a label — it is a required analytical document
(`domain-profile.md`), read by every engine before anything else, the
same way the project registry is read. A bare type tag (`ERP` /
`GENERAL` / `CUSTOM:<name>`) is only the document's Domain Identity
field, never a substitute for the document itself.

**v4.0 note:** domain-profile.md is now version-aware — it lives at
`[DOMAIN-ROOT]/domain-profile.md`, and the domain's evolution
(Core/Extensions/Models versions, Domain Releases) is tracked in the
adjacent `[DOMAIN-ROOT]/_versions/version-ledger.md`, both owned by
P-DOMAIN. See MULTI-PROJECT-VERSIONING-ARCHITECTURE.md PART 2 + 4.2.

**domain-profile.md must define, at minimum:**
```
Domain Identity   : ERP | GENERAL | CUSTOM:<name>
Scope             : what is in / out of bounds for this domain
Purpose           : why this domain/platform exists
Responsibilities  : the capabilities it owns
Main Components   : this domain's own Foundation/Business module
                     breakdown — user-declared, never auto-detected
                     or inferred by any engine
Governing Rules    : domain-level constraints specific to this domain
Relationships      : how this domain relates to other domains, when
                     the platform spans more than one
```

**Terminology.** Every engine's "ERP module" / "ERP platform" wording
resolves to this document's Domain Identity value instead of a fixed
literal.

**Pattern Library availability.** Business Code Pattern and CORE-9
(Composite Screen Governance) apply at full strength when Domain
Identity is `ERP`. For any other value, both become available on
explicit request only, instead of being applied by default — the
same on/off model already used for the Workflow Engine (see
WORKFLOW-ENGINE-TIER below). XM Cross-Module Dependency is not
governed by this parameter; it always applies at its current,
unconditional strength.

**Knowledge Base.** A domain may optionally have a matching Knowledge
Base session upload (platform-standards.md Section M is the ERP
Knowledge Base) — consulted only after domain-profile.md, never in
place of it, and only if one has been provided for the declared domain.

---

## 2A. PROJECT-REGISTRY / ECOSYSTEM INDEX (v4.0 — supersedes single master-registry.md)

```
Status   : MANDATORY — blocking, same as DOMAIN-PROFILE and DB_TARGET
Files    : [REGISTRY]              (per-project scoped registry)
           [ECO]/projects-index.md (global, thin)
           [ECO]/domains-index.md   (global)
           [ECO]/reuse-registry.md  (global — importable items)
```

As of v4.0 the single global `master-registry.md` is superseded by a
per-project `project-registry.md` (token `[REGISTRY]`) plus the three
`[ECO]/` index files. Every engine's Pre-Flight Discovery (CORE-10)
treats the SELECTED project's `[REGISTRY]` as a required file — MISSING
triggers the same STOP behavior as any other required file (not the old
"GOVERNANCE REDUCED, proceed anyway" fallback; that still applies,
unrelated, to a missing DB Script per RULE-7). The per-project registry
is owned by P(-1) (MULTI-PROJECT-VERSIONING-ARCHITECTURE.md PART 4.1).
Per §1B, the retired `master-registry.md` / `_registry/` path is read as
`[REGISTRY]` wherever any legacy engine text still shows it.

---

## 3. DB_TARGET

```
Value    : POSTGRESQL_16
Allowed  : ORACLE_19C | POSTGRESQL_16 | <any other declared dialect,
           provided its own syntax mapping row is added to the table
           below first>
```

Database dialect used by every DDL-producing and DDL-referencing
engine (P2, and any engine that cites a DB type).

### DB_TARGET Syntax Mapping

```
╔══════════════════════════╦══════════════════════╦══════════════════════════╗
║ Concept                  ║ ORACLE_19C            ║ POSTGRESQL_16            ║
╠══════════════════════════╬══════════════════════╬══════════════════════════╣
║ Integer PK / FK          ║ NUMBER(10)            ║ BIGINT                   ║
║ Small integer / flag     ║ NUMBER(1,0)           ║ SMALLINT                 ║
║ Boolean flag (isActiveFl)║ NUMBER(1) DEFAULT 1   ║ SMALLINT DEFAULT 1       ║
║ Decimal / monetary       ║ NUMBER(18,4)          ║ NUMERIC(18,4)            ║
║ Percentage / ratio       ║ NUMBER(5,2)           ║ NUMERIC(5,2)             ║
║ Short string             ║ VARCHAR2(N)           ║ VARCHAR(N)               ║
║ Audit user fields        ║ VARCHAR2(255)         ║ VARCHAR(255)             ║
║ Long text / notes        ║ CLOB                  ║ TEXT                     ║
║ Timestamp (audit)        ║ TIMESTAMP             ║ TIMESTAMP                ║
║ Timestamp with TZ        ║ TIMESTAMP WITH LOCAL  ║ TIMESTAMPTZ              ║
║                          ║   TIME ZONE           ║                          ║
║ Sequence (PK source)     ║ CREATE SEQUENCE       ║ CREATE SEQUENCE          ║
║                          ║   NOCACHE NOCYCLE     ║   START WITH 1           ║
║                          ║                       ║   INCREMENT BY 1         ║
║                          ║                       ║   NO CACHE NO CYCLE      ║
║ PL/SQL block terminator  ║ END name; /           ║ $$ LANGUAGE plpgsql;     ║
║ Audit trigger syntax     ║ CREATE OR REPLACE     ║ CREATE OR REPLACE        ║
║                          ║   TRIGGER + /         ║   FUNCTION → TRIGGER     ║
║ Execute tool             ║ SQL Developer/SQLPlus ║ psql / pgAdmin           ║
║ COMMENT ON syntax        ║ supported (same)      ║ supported (same)         ║
╚══════════════════════════╩══════════════════════╩══════════════════════════╝

Notes:
  — SERIAL / GENERATED ALWAYS AS IDENTITY (PostgreSQL) are not used.
    Sequences are always created explicitly; PK population by framework.
  — BOOLEAN native type (PostgreSQL) is not used.
    SMALLINT DEFAULT 1 is used for isActiveFl flags, consistent with
    the declared BACKEND_STACK's entity mapping and naming convention.
  — VARCHAR without a length is not permitted in either dialect.
  — CLOB → TEXT mapping is automatic; no governance note required.
```

---

## 4. BACKEND_STACK

```
Value    : SPRING_BOOT_JAVA   (Spring Boot, Java)
```

---

## 5. FRONTEND_STACK

```
Value    : REACT_TS_VITE
Detail   : React (TypeScript) — Vite build tool, React Router
           (routing), TanStack Query (server-state/data-fetching),
           React Hook Form + Zod (forms/validation), useState/
           useReducer + Context API (local/UI state — no Redux/global
           state library by default; introducing one requires a
           DRV-ID justifying the deviation)
```

---

## 6. MOBILE_STACK

```
Value    : FLUTTER_DART
Allowed  : <any declared stack name> | NONE (no mobile app in scope)
```

---

## 7. STACK VIOLATIONS

```
Any technology used that does not match BACKEND_STACK, FRONTEND_STACK,
MOBILE_STACK, or DB_TARGET above is a CRITICAL severity STACK
VIOLATION, detected at any phase / ALIGN-BE / ALIGN-FE gate / P4.1 /
P4.2 audit. No exception without a formally documented GOVERNANCE
EXCEPTION accepted by the human architecture authority.

Per-dialect DB_TARGET violations:

When DB_TARGET = ORACLE_19C:
  ✗ PostgreSQL-only syntax (SERIAL, BIGINT, TEXT, $$) → Oracle only
  ✗ VARCHAR without 2                                 → must be VARCHAR2
  ✗ BOOLEAN datatype                                  → use NUMBER(1,0)

When DB_TARGET = POSTGRESQL_16:
  ✗ Oracle-only syntax (VARCHAR2, NUMBER, NOCACHE,
    NOCYCLE, PL/SQL / terminator, DUAL)               → PostgreSQL only
  ✗ SERIAL or IDENTITY columns                        → use SEQUENCE explicitly
```

---

## 8. WORKFLOW-ENGINE-TIER

```
Value    : OFF
Allowed  : OFF | TIER-1 | TIER-2:<engine-name>
```

Current declared state of RULE-13 (Workflow Engine Absence
Declaration). `OFF` is the default across the ecosystem — no workflow
infrastructure anywhere. `TIER-1` and `TIER-2:<name>` are only ever
set here after their respective exception protocols in
shared-governance-rules.md (RULE-13) have been completed in full —
this field records the outcome, it does not itself grant the
exception.

---

## 9. BUSINESS-CODE-DEFAULT

```
Value    : NOT-APPLIED-UNLESS-EXPLICIT
```

Fixed policy reference for BC-RULE-0 (Business Code Pattern
applicability test, PROJECT-1-SRS-GOVERNANCE-ENGINE.md Section 5.5.5):
Business Code is never applied to an entity by default — only when
that entity explicitly needs it. This value is a cross-reference, not
a toggle; it does not vary with DOMAIN-PROFILE.

---

*End of GOVERNANCE-CONFIG.md*
*AMEND-ROUTER-A (2026-09-04): [STATE] token (§1B) + P-ROUTER row (§1C).*
*Every declarable, swappable platform value lives here — nowhere else.*
*v4.0: GOVERNANCE-ROOT tree is Project→Domain→{Core|Extensions|Models};*
*PATH VOCABULARY (§1B) defines every Drive path via tokens ([ECO],*
*[REGISTRY], [MANIFEST], [DOMAIN-ROOT], [CTX], [BACKUP]); the DRIVE*
*DEPENDENCY MAP (§1C) is the ONE authoritative per-engine input/output*
*map (engines' inline tables defer to it) — no engine hardcodes a*
*layout; PROJECT-SELECTION opens every session; per-project registries*
*supersede the single master-registry.md — see*
*MULTI-PROJECT-VERSIONING-ARCHITECTURE.md.*

---

## 1D. PIPELINE V5 — NAMING · LEDGER · COMPLETION PROTOCOL (AMEND-PIPELINE-V5)

```
Status : AUTHORITATIVE. Added 2026-09-06. This section is the ONLY place the
         following are defined; every engine, command, and tool references it
         and hardcodes none of it.
```

### 1D.1 — Core vs optional pipeline

```
CORE (mandatory, in order — the pipeline IS this chain):
  P(-1) Master Registry Builder (BOOTSTRAP only — creates the project/platform
        registry once; per-module maintenance is now inline, see 1D.4)
  → P0   Platform Inception
  → P0.5 PRD
  → P1   SRS
  → P2   Database
  → P2.5 UI/UX Design
  → P3.1 Backend Execution Plan
  → P3.2 Frontend Execution Plan          ← END of core

OPTIONAL (run only when wanted; never a gate for the core):
  P3.5 Test-Case Spec (TestSprite-ready — see 1D.6)
  P4.1 / P4.2 Governance Audit (emits FIX-PROMPTS — see 1D.7)
  P5, Master Reviewer
  P-ROUTER — demoted to an OPTIONAL read-only state viewer. Engines no longer
             depend on it; handoff is inline (1D.4). It never generates work.

RETIRED:
  P-REG (state-registry-extractor) — its extraction is now the inline
  REGISTRY step of every core engine's completion protocol (1D.4). Do not
  run it as a separate project; its outputs (registry-*-{mod}.md) are
  produced by the engines themselves.
```

### 1D.2 — Artifact naming vocabulary (module-qualified)

```
Every per-module artifact carries the module code as a lower-case SUFFIX,
exactly as the tools' config.ARTIFACT_FILES defines it (single source):

  Stage   │ Artifacts ({mod} = lower-case module code, e.g. org)
  ────────┼───────────────────────────────────────────────────────────
  P0      │ platform-summary.md (platform-level) · module-registry-{mod}.md
          │ business-policies-{mod}.md
  P0.5    │ prd-{mod}.md
  P1      │ srs-{mod}.md                · registry-srs-{mod}.md
  P2      │ db-script-{mod}.md          · registry-db-{mod}.md
  P2.5    │ flow-diagram-{mod}.md       · ui-ux-spec-{mod}.md
  P3.1    │ backend-execution-plan-{mod}.md   · registry-exec-be-{mod}.md
  P3.2    │ frontend-execution-plan-{mod}.md  · registry-exec-fe-{mod}.md
  P3.5    │ backend-test-plan-{mod}.md · frontend-test-plan-{mod}.md
          │ registry-test-be-{mod}.md · registry-test-fe-{mod}.md

RULES
- The un-qualified names (srs.md, db-script.md, backend-execution-plan.md …)
  are RETIRED and no longer valid: the tools' classify_artifact() rejects
  them, so a stale name cannot slip through the splitter's semantic checks.
- Engines emit these exact names. Commands/tools resolve them ONLY via
  config (resolve_filename / plan_file / plan_label) — never spelled inline.
- Several modules may share one drop folder without collision; the module
  is read from the filename, not sniffed from content.
```

### 1D.3 — [LEDGER] token and the Journey Ledger

```
[LEDGER] = [CTX]/[Module]/_journey/journey-{mod}.json   (ONE file per module,
                                                    ALL versions inside)
Schema (config.new_ledger / open_ledger_version / close_ledger_version):
  { "module": "ORG", "schema": "journey-ledger/1",
    "versions": {
      "1": { "status": "OPEN|CLOSED", "started_at", "started_by_engine",
             "ended_at", "change_set": null | "CS-ORG-001",
             "artifacts": [ { engine, stage, filename, artifact,
                              drive_file_id, drive_url, recorded_at,
                              status: UPLOADED|SUPERSEDED } ] },
      "2": { … }  } }

START module <MOD> vN  = open the "N" section (first engine of the journey —
                          P1 for a new module, or wherever an IFA delta enters).
END   module <MOD> vN  = close it (last core engine, P3.2, or the last engine
                          actually run for that version).
A re-uploaded artifact appends a new UPLOADED row; the previous one becomes
SUPERSEDED. The loader always resolves the latest UPLOADED row per filename.
Drive links come from the connector's upload result (file id + url).
```

### 1D.4 — ENGINE COMPLETION PROTOCOL (unified, every core engine)

```
After producing its stage artifact(s), EVERY core engine — in this order,
in the same session, no separate project:

  1. ARTIFACT   — emit the stage artifact(s) with the 1D.2 names; upload via
                  the connector; capture {drive_file_id, drive_url}.
  2. REGISTRY   — run the inline registry step for this stage (the former
                  P-REG extraction): emit registry-<stage>-{mod}.md AND apply
                  the master/project-registry update for the IDs this stage
                  created (entity ownership, XM/UXD indexes, sequences).
                  Upload both. (P(-1) created the registry; engines maintain it.)
  3. LEDGER     — append one row per uploaded file to [LEDGER] (1D.3 schema).
                  The first engine of a version writes START; the last writes
                  END. IFA versions carry change_set = CS-ID.
  4. HANDOFF    — print the NEXT-ENGINE INPUT block (1D.5). It is the literal
                  opening message for the next project's session.

The engine's own gates (CONTRACT-10/11/12, Zero-Question, IFA baseline read)
are unchanged and run BEFORE step 1. This protocol replaces: separate P-REG
sessions, talking to P-ROUTER, and any ad-hoc "Next step" line.
```

### 1D.5 — NEXT-ENGINE INPUT block (the handoff prompt)

```
══════════════════════════════════════════════════════════
NEXT-ENGINE INPUT — from [THIS ENGINE] → to [NEXT ENGINE]
══════════════════════════════════════════════════════════
Module / Version : [MOD] v[N]      Change Set : [CS-ID | none]
Journey          : [START|CONTINUE|END]  ledger: [LEDGER] link

PRODUCED (this stage)
  [filename]                  → [drive_url]        IDs: [range]
  registry-<stage>-{mod}.md   → [drive_url]
  master/project-registry     → [updated: what]

NEXT ENGINE MUST
  Read   : [the files above it needs, by name, + baselines for IFA]
  Do     : [its stage in one line]
  Gate   : [the CONTRACT gate it must clear first]
  Names  : emit 1D.2 names; run 1D.4 on completion
══════════════════════════════════════════════════════════
Paste this block as the first message of the next project's session.
```

### 1D.6 — Test-Case Spec (P3.5, OPTIONAL) — TestSprite-ready

```
P3.5 no longer produces JUnit / Playwright scaffolding or a
test-execution-manifest. It produces framework-agnostic TEST-CASE SPECS:
  backend-test-plan-{mod}.md   (TC-BE-{mod}-NNN)
  frontend-test-plan-{mod}.md  (TC-FE-{mod}-NNN)
Content = Feature → Use case → TC { id, title, preconditions, steps,
expected, data, rule/API/screen refs }. Marker vocabulary (PHASE/SUB/TC) is
kept so the splitter still works and IDs stay traceable.
Execution = TestSprite: the spec file is uploaded to TestSprite as the
product spec (it is spec-driven: PRD + live exploration → its own plan →
generate → run in its cloud). Backend = API project (+ OpenAPI/API docs);
frontend = UI project (+ live URL). Reports/archiving follow
TESTSPRITE-GOVERNANCE.md.
```

### 1D.7 — Governance Audit output (P4.1 / P4.2, OPTIONAL) — FIX-PROMPTS

```
P4 stays the auditor and still writes markdown, but the OUTPUT FORMAT is a
set of READY FIX-PROMPTS GROUPED BY TARGET PROJECT, used manually:

  ## FIX-PROMPTS — [MOD] v[N] — audit [date]
  ### → P3.1 (Backend Execution Plan)          [N findings]
  ┌ FIX-001  [severity]  [ID(s) affected]
  │ PROBLEM     : what is wrong, where (file/section/ID)
  │ WHY         : the rule/contract it violates
  │ RECOMMENDED : the concrete change
  │ DEPENDENCIES: what else must move with it (XM/UXD/ALIGN, other IDs,
  │               other engines' artifacts) — and what must NOT change
  │ VERIFY      : how the fixer proves it is fixed
  └ PASTE-READY PROMPT:
    "In [MOD] v[N] [artifact], fix FIX-001: … keep … unchanged; re-run …"
  ### → P2 (Database)  …   ### → P1 (SRS)  …   ### → P3.2 …
Findings with no owning engine go under "### → HUMAN DECISION".
```

### 1D.8 — LEDGER-WRITE PROCEDURE (how an engine records its links via the connector)

```
CONSTRAINT: the Google Drive connector's update_file changes metadata only
(title / location) — it NEVER changes content. So a JSON ledger on Drive can
only be "appended" by re-creating it. This procedure is the ONLY sanctioned
way; it keeps exactly one live ledger file per module.

STEP A — upload the artifact and capture its identity
  create_file(name = <§1D.2 filename>, parent = <stage folder under [CTX]/[Module]/>)
  → take from the response:   id            → row.drive_file_id
                              webViewLink   → row.drive_url
  (do this per file: the artifact, its registry-<stage>-{mod}.md, and any
   updated project-registry.md)

STEP B — fetch the current ledger (or start one)
  search_files(name = "journey-<mod>.json", parent = [CTX]/[Module]/)
  - found  → read_file_content(id)   → ledger JSON (note the OLD file id)
  - absent → this engine is the FIRST of the journey: ledger = new_ledger(MOD)
             and this write also performs START for this version.

STEP C — apply the change in memory (schema §1D.3; same rules as
  journey_loader.py so tooling and engines never diverge)
  - START  : open the version section {status OPEN, started_at, started_by_engine,
             change_set (IFA CS-ID or null)}  — only if the section doesn't exist
  - APPEND : one row per file uploaded in STEP A
             { engine, stage, filename, artifact, drive_file_id, drive_url,
               recorded_at, status: "UPLOADED" }
             if a row with the same filename is already UPLOADED → set it to
             SUPERSEDED first (re-upload semantics)
  - END    : only the LAST engine run for this version sets status CLOSED +
             ended_at (normally P3.2; for an optional-only run, that engine)

STEP D — write it back (re-create, then retire the old copy)
  create_file(name = "journey-<mod>.json", parent = [CTX]/[Module]/, content = ledger)
  → NEW id
  trash_file(OLD id)          ← only after the new file exists; skip if none
  Never leave two journey-<mod>.json files in the folder.

STEP E — put the NEW ledger link in the NEXT-ENGINE INPUT block (Journey line).

Failure rule: if STEP D fails, do NOT report the stage as complete — the
links exist on Drive but are unrecorded; re-run STEP B–D before handing off.
```

*1D added by AMEND-PIPELINE-V5 (2026-09-06): core/optional pipeline, module-*
*qualified naming, [LEDGER] token + schema, unified completion protocol,*
*NEXT-ENGINE INPUT, TestSprite TC spec, fix-prompt audit output, P-REG retired,*
*P-ROUTER demoted.*

---

## 1E. DRIVE LAYOUT GOVERNANCE (AMEND-PIPELINE-V5 — rendered from config.DRIVE_LAYOUT)

```
Status : AUTHORITATIVE. This section is GENERATED from the tools' single
         machine-readable source (backend config.py: DRIVE_LAYOUT,
         DRIVE_LAYOUT_FRONTEND, DRIVE_LAYOUT_OPTIONAL, DRIVE_JOURNEY_FOLDER,
         DRIVE_PLATFORM_FOLDER, ARTIFACT_FILES). Never edit the table by hand —
         change config.py and re-render. drive_layout.py audits real Drive
         trees against the same source.
```

### 1E.1 — THE LAW
```
1. A file lives ONLY inside its designated stage folder. [CTX] root and every
   module root hold FOLDERS ONLY. A loose file is a layout violation
   (drive_layout.py --audit reports it with the exact target folder).
2. ONE Drive tree per module, BOTH tracks in it (backend + frontend stage
   folders side by side). Tracks are separated in the REPOS, not on Drive.
3. Versions nest like the repos: v1 = [CTX]/[Module]/…  ·  vN = [CTX]/[Module]/vN/…
   The journey ledger is cross-version → [CTX]/[Module]/_journey/ (outside vN).
4. Platform-level files (not per-module) → [CTX]/_platform/ only.
5. Each stage folder has exactly ONE writer engine. Readers never write.
6. Multi-project · multi-module: addressing is always
   [GOVERNANCE-ROOT]/[Project]/[Domain]/<slot>/[Module][/vN]/<stage-folder>/<file>
   — bound per session by CORE-11 (never written literally by an engine).
```

### 1E.2 — Expected tree for a module (v1)
```
  [CTX]/_platform
  [CTX]/[MOD]/_journey
  [CTX]/[MOD]/P0-Platform
  [CTX]/[MOD]/P0.5-PRD
  [CTX]/[MOD]/P1-SRS
  [CTX]/[MOD]/P2-DB
  [CTX]/[MOD]/P2.5-UIUX
  [CTX]/[MOD]/P3.1-Backend-Exec
  [CTX]/[MOD]/P3.5-Tests
  [CTX]/[MOD]/P3.2-Frontend-Exec
  [CTX]/[MOD]/_ref/ui-shell
  [CTX]/[MOD]/_ref/api-docs
  [CTX]/[MOD]/P4-Audit
```
For a version N ≥ 2 the stage folders repeat under `/vN/` (the `_journey` and
`_platform` folders are shared, not repeated):
```
  [CTX]/[MOD]/v2/P0-Platform
  [CTX]/[MOD]/v2/P0.5-PRD
  [CTX]/[MOD]/v2/P1-SRS
  [CTX]/[MOD]/v2/P2-DB
  [CTX]/[MOD]/v2/P2.5-UIUX
  [CTX]/[MOD]/v2/P3.1-Backend-Exec
  [CTX]/[MOD]/v2/P3.5-Tests
  [CTX]/[MOD]/v2/P3.2-Frontend-Exec
  [CTX]/[MOD]/v2/_ref/ui-shell
  [CTX]/[MOD]/v2/_ref/api-docs
  [CTX]/[MOD]/v2/P4-Audit
```

### 1E.3 — WRITE / READ matrix (who writes where, who reads it)
```
  Stage folder        │ Write│ Read by                                 │ Files ({mod} = lower-case module)
  ────────────────────┼──────┼─────────────────────────────────────────┼──────────────────────────────
  P0-Platform         │ P0   │ P0.5, P1, P2, P2.5, P3.1, P3.2          │ platform-summary.md, module-registry-[mod].md, business-policies-[mod].md
  P0.5-PRD            │ P0.5 │ P1, P2.5, P3.5                          │ prd-[mod].md
  P1-SRS              │ P1   │ P2, P2.5, P3.1, P3.2, P3.5, P4.1, P4.2  │ srs-[mod].md, registry-srs-[mod].md
  P2-DB               │ P2   │ P2.5, P3.1, P3.5, P4.1                  │ db-script-[mod].md, registry-db-[mod].md
  P2.5-UIUX           │ P2.5 │ P3.1, P3.2, P4.2                        │ flow-diagram-[mod].md, ui-ux-spec-[mod].md
  P3.1-Backend-Exec   │ P3.1 │ P3.2, P3.5, P4.1                        │ backend-execution-plan-[mod].md, registry-exec-be-[mod].md
  P3.5-Tests          │ P3.5 │ P4.1, P5                                │ backend-test-plan-[mod].md, registry-test-be-[mod].md
  P3.2-Frontend-Exec  │ P3.2 │ P3.5, P4.2                              │ frontend-execution-plan-[mod].md, registry-exec-fe-[mod].md
  P3.5-Tests          │ P3.5 │ P4.2                                    │ frontend-test-plan-[mod].md, registry-test-fe-[mod].md
  _ref/ui-shell       │ P3.2 │ P3.2, P3.5, P4.2                        │ ui-shell-manifest-[mod].md
  _ref/api-docs       │ P3.2 │ P3.1, P3.2, P3.5, P4.1, P4.2            │ api-docs-[mod].md
  P4-Audit            │ P4.x │ —                                       │ (engine output)
  _journey            │ all  │ journey_loader / process-project-files │ journey-[mod].json  (§1D.3 / §1D.8)
  _platform           │ P0   │ every engine                            │ platform-summary.md
```
An engine's COMPLETION PROTOCOL carries its own PATHS block (WRITES TO / READS
FROM) rendered from this matrix.

### 1E.4 — Tooling
```
drive_layout.py --tree  --ctx "[CTX]" --module ORG --version N   → mkdir plan
drive_layout.py --audit listing.json --module ORG [--version N]   → move / rename /
        missing-folder plan for the connector; exit 1 while anything is loose.
process-project-files STEP 0 runs the audit BEFORE loading; a dirty layout is
fixed (connector applies the plan) or stopped, never silently loaded around.
```

### 1E.5 — LAYOUT SELF-HEAL (automatic — every engine, at Pre-Flight; no human step)

```
Engines run inside Claude Projects with the Drive connector but no Python, so
they cannot run drive_layout.py. They still migrate the layout AUTOMATICALLY,
one module at a time, on first contact — using only connector metadata ops:

At CORE-10 Pre-Flight, for EVERY input file this engine must read (its PATHS
block → READS FROM) and for its own WRITES-TO folder:

  1. LOOK at the governed path   [MROOT]/<stage-folder>/<V5 filename>.
     found → fine, continue.
  2. NOT found → SEARCH the module subtree [CTX]/[Module]/** and [CTX] root
     by the V5 name AND by its legacy un-qualified name (§1D.2 retired list:
     srs.md, db-script.md, flow-diagram.md, ui-ux-spec.md,
     backend-execution-plan.md, frontend-execution-plan.md,
     backend-test-plan.md, frontend-test-plan.md).
       found elsewhere → HEAL:
           a. if the folder is missing → create it (folders only, §1E.2)
           b. update_file(id, name = <V5 name>)           (rename if legacy)
           c. update_file(id, parent = <governed folder>) (move — metadata only,
              reversible, no content change)
           d. record it in the NEXT-ENGINE INPUT block under "HEALED:" and, if
              a ledger exists, append the row (§1D.8) with the new location
       not found anywhere → the input is genuinely MISSING → normal blocking
                            rule (CORE-10): STOP, do not guess.
  3. Ledger: if [CTX]/[Module]/_journey/journey-<mod>.json does not exist but the
     module already has artifacts → this engine creates it (§1D.8 STEP B:
     new_ledger + START v1) and records every artifact it just located, so a
     pre-V5 module gains its ledger automatically on first contact.
  4. Never move a file whose V5 name maps to NO known artifact (unknown file)
     — list it under "UNKNOWN (not moved):" in the handoff for a human.

Result: a legacy module becomes V5-compliant progressively, by the engines
themselves, without DRIVE-MIGRATION-V5.md — that document is now the OPTIONAL
bulk path (all modules at once, via the orchestrator), not a prerequisite.
```

---

## 1F. REFERENCE INGEST — UI SHELL + API DOCS (AMEND-PIPELINE-V5, P3.2)

```
Problem: P3.2 needs the real UI Shell manifest and the real API Docs EVERY
session, but before V5 they were re-attached by hand each time — no durable,
governed copy, no version story.

Rule: the FIRST time they are attached for a module version, P3.2 uploads a
durable copy to the module's governed REFERENCE folders (§1E), so ANY later
session opened for that module reads them from Drive without re-attaching.

  Locations (per version — §1E tree):
    UI Shell manifest : [CTX]/[Module][/vN]/_ref/ui-shell/ui-shell-manifest-[mod].md
    API Docs          : [CTX]/[Module][/vN]/_ref/api-docs/api-docs-[mod].md

INGEST (P3.2 Pre-Flight, after the two inputs are available):
  1. If the governed reference file is ABSENT for this version → upload the
     attached copy there (create_file), capture id/webViewLink.
  2. If PRESENT and the person attached a NEWER one → REPLACE IN PLACE:
     re-create at the SAME governed path, trash the old id, and mark the old
     ledger row SUPERSEDED + append the new one (§1D.8). Exactly ONE live copy
     per version — never a second file, never a loose copy.
  3. If PRESENT and nothing new attached → use the governed copy as-is (this is
     the "any session reads the reference" path — no re-attach needed).
  4. Record each in the ledger via config.reference_ledger_row(...).

NEW VERSION (IFA vN — extension / addition):
  A new version's _ref/ starts EMPTY. On the first P3.2 session for vN:
   • if a fresh UI Shell / API Docs is attached → ingest it into vN (rule above);
   • else CARRY FORWARD from vN-1: copy the vN-1 reference files into vN's
     governed folders (create_file from the vN-1 copy), so vN is self-contained.
  vN-1 references stay FROZEN — a new upload for vN never touches vN-1.
  When the new upload is meant to REPLACE the reference for the SAME version
  (a corrected shell/API doc, not a new module version) → rule 2 (replace in
  place) applies; the old file is superseded and removed, integrated cleanly.

This makes the UI Shell + API Docs a durable, per-version, self-healing
reference that every conversation on the module inherits automatically.
```

---

## 1G. MICRO-FEATURE FAST-PATH (MFF) — in-Claude-Code analysis for extensions

```
Status : AUTHORITATIVE. An ALTERNATIVE entry path (never a replacement): for
         ANY extension/addition to an already-implemented+analysed module, the
         full P1->P3 project journey MAY be short-circuited into a single Claude
         Code session that generates the SAME governed analysis artifacts (as a
         delta), uploads them to Drive in their governed places, then implements
         the feature. The full project journey stays available and unchanged as
         the alternative for anyone who prefers it, or for a first build.

SCOPE: no size threshold -- any feature-extension on a built module qualifies.
       A brand-new module (no prior version/analysis) does NOT: it goes the
       full project route. MFF requires a frozen v[N-1] to extend.

TRACK SEPARATION: backend and frontend are SEPARATE MFF runs, exactly like the
       rest of the system -- /micro-feature-backend and /micro-feature-frontend,
       each touching only its own repo + its own governance-tools + its own
       stage folders. Neither reaches into the other's tree. Backend runs first
       when the feature spans both (its API is the frontend's input), same
       ordering as P3.1 -> P3.2.
```

### 1G.1 -- The run (one Claude Code session, per track)

```
0. PRE-FLIGHT (1E.5 self-heal applies): resolve the module, confirm a frozen
   current version exists. New version = get_next_version(mod) -> vN. Assign
   CS-[MOD]-[SEQ].

1. BASELINE READ -- LOCAL governance first, Drive as fallback:
   Source of truth for reading is the LOCAL repo (prior versions are archived
   there): modules/[MOD][/v(N-1)]/ -- the FULL plans AND the split packages/**
   are both present, so read whichever the delta needs. Only if a file is not
   local (e.g. a clean checkout) -> read it from its governed Drive path
   (1E) via the connector. Drive is the upload target + cross-session
   reference, not the primary read source.
   backend  : modules/[MOD][/vN-1]/P1/srs . P2/db-script . P3_1/backend-
              execution-plan (full) + packages/backend-execution/** (split) .
              registries . _ref/api-docs (1F)
   frontend : modules/[MOD][/vN-1]/P1/srs . P2_5/flow-diagram + ui-ux-spec .
              P3_2/frontend-execution-plan (full) + packages/frontend-
              execution/** (split) . registries . _ref/ui-shell + _ref/api-docs

2. GENERATE DELTA ANALYSIS -- Claude Code THINKS and writes it (the agents do
   NOT generate or reason -- they are mechanical: agent1 makes folders, agent2
   copies, agent3 splits by markers). Claude Code applies the SAME reasoning
   the P3 engine encodes: it reads the baseline, RESPECTS DEPENDENCIES
   (continue ID sequences from the registries; honor XM / UXD / ALIGN mappings;
   an additive delta must not break an existing mapping -- a breaking one STOPS
   and escalates to the full route), and produces the SAME artifacts the
   projects would, delta only, with 1D.2 names + PHASE/SUB/TC markers + a
   Change Manifest header (CS-ID, baseline v[N-1], NEW/MODIFIED/UNCHANGED IDs +
   the dependencies each change carries). Inline REGISTRY (1D.4) produces
   registry-*-[mod].md for the delta. Full analysis, not a lighter format.
     backend  : backend-execution-plan-[mod].md (+ db-script delta if a column/
                table is truly needed) + registry-exec-be / registry-db
     frontend : frontend-execution-plan-[mod].md + registry-exec-fe
   (srs/flow/ui-ux deltas only if the feature changes them.)

3. SPLIT + ARCHIVE (mechanical -- run ONLY after step 2's full analysis exists):
   this track's governance-tools, on the generated delta, vN:
     agent1_create_structure.py --module [MOD] --new-version
     agent2_archive.py --module [MOD] --source <generated>
     agent3_splitter.py --module [MOD]   (5 stages -> packages + split receipt)

4. UPLOAD TO DRIVE -- governed placement only (1E), version vN:
     each artifact -> drive_folder_for_file(name, mod) under [MROOT]=[CTX]/[MOD]/vN/
     LEDGER (1D.8): START [MOD] vN (change_set = CS-ID) -> one row per uploaded
     file -> append the split receipt's package rows (repo_path). Nothing loose.

5. IMPLEMENT -- Claude Code reads the vN delta packages and applies the feature
   to the real code (add API / screen / field), respecting the dependencies the
   Change Manifest lists. Backend first if the feature spans both tracks.

6. CLOSE -- END [MOD] vN in the ledger once this track's implementation is done
   (frontend END closes the version when the feature spans both).
```


### 1G.3 -- Entry point: /micro-feature (ONE free-text prompt, internal split)

```
A SINGLE free-text launcher. The person types the whole feature once, in any
language, without saying "backend" or "frontend":
   /micro-feature  <free text>
The prompt UNDERSTANDS the request and SPLITS it itself into a backend part
(data/logic: endpoint, table/column, rule, service, permission) and a frontend
part (UI: screen, button, field-on-screen, form, route, component). Either part
may be empty. It infers the MODULE (asks only if missing), confirms in ONE line,
then drives BOTH governed commands in order under ONE new version + ONE CS-ID:
   backend part -> /micro-feature-backend   (runs FIRST; its API feeds frontend)
   frontend part -> /micro-feature-frontend
It is a ROUTER only; the track commands do the governed 1G.1 work.

Each track archives in ITS OWN established structure -- same agents (1/2/3),
run as-is, cleanly separated:
  backend  : FULL analysis set (srs / db-script / backend-execution-plan +
             registries), with clear phase separation inside
             backend-execution-plan-[mod].md; agent3 splits it.
  frontend : chiefly frontend-execution-plan-[mod].md (+ registry; flow/ui-ux
             deltas only when a screen changed); agent3 splits it.
Backend files never land in frontend folders or vice versa -- the split is
internal to the launcher, the separation is preserved on disk and on Drive.
```

### 1G.2 -- Guarantees (why this stays governed, not a shortcut around it)

```
. Same artifacts, same 1D.2 names, same markers, same registries as the
  projects -- an auditor/next session cannot tell an MFF delta from a
  project-generated one.
. Same 1E governed Drive placement + 1D.8 ledger -- analysis files are on
  Drive, discoverable, versioned; nothing is implemented without its analysis
  existing and uploaded first (step 4 precedes step 5).
. Same IFA versioning -- vN alongside a frozen v[N-1]; same tools, no new
  versioning logic.
. Track-separated exactly like the projects. Full project journey unchanged as
  the alternative path.
```
