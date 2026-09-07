# ERP GOVERNANCE — MULTI-PROJECT + VERSIONING ARCHITECTURE (v4.0)
## The Selection & Reuse Layer that sits ABOVE the pipeline

```
File ID   : MULTI-PROJECT-VERSIONING-ARCHITECTURE (v4.0)
Status    : MANDATORY — the single source of truth for the v4.0 layer.
            Every engine loads it (as part of the shared layer) and
            obeys the Session Project-Selection protocol before doing
            anything else.
Owns      : Projects Index, project-manifest, project-registry scoping,
            the Core/Extension/Version/Domain-Release model, the Version
            Ledger, VRE, versioned-reuse-by-pinning, AND the automatic
            provisioning of the whole structure (§1.3 — self-building).
Owning    : P(-1) Master Registry Builder (project/registry authority)
engines     + P-DOMAIN Domain Profile Builder (domain evolution authority).
            No new claude.ai project is created for this layer — these
            two existing engines absorb it (deliberate simplicity choice).
Companion : GOVERNANCE-CONFIG.md (paths), SHARED-GOVERNANCE-CORE.md
            (CORE-10 Drive Automation + CORE-11 selection), shared-
            artifact-contracts.md (CONTRACT-14 reuse, CONTRACT-15 VRE),
            XM-RESOLUTION-EVENT-PROTOCOL.md (RXE — VRE extends it).
```

```
════════════════════════════════════════════════════════════════
WHY THIS LAYER EXISTS
════════════════════════════════════════════════════════════════
The pipeline (P0→P5 + Test Generation Engine) generates artifacts for
ONE unit at a time. It has no concept of "which project am I in" or
"which version of this model." This layer adds exactly two capabilities,
and NOTHING inside the pipeline changes — it simply runs inside the
context this layer selects:

  1. MULTIPLE PROJECTS IN PARALLEL, each in an ISOLATED context, so
     work on several ideas/domains never mixes.
  2. VERSIONED, REUSABLE DOMAINS/MODELS/EXTENSIONS, so a domain can
     grow (v1→v2→v3) without breaking what depends on it, and other
     projects can reuse a pinned version or a new extension without
     touching the original.

And it builds its own folder/index structure AUTOMATICALLY (§1.3) — the
operator never hand-creates a folder or an index file.

Design principle (explicit): keep it SIMPLE. One spec file (this one),
reuse of existing mechanisms (project-registry, CORE-10, RXE, domain-
profile) instead of parallel new machinery, templates embedded here
rather than scattered, and no new engine project.
════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# PART 1 — MULTIPLE PROJECTS, ISOLATED CONTEXT
═══════════════════════════════════════════════════════════════════

## 1.1 The three registry-layer files

```
_ecosystem/projects-index.md   — GLOBAL, thin. One row per open project:
                                 name, status, domain(s), pointer to its
                                 project-manifest. Nothing else lives here.
[Project]/project-manifest.md  — PER PROJECT. The project's metadata card
                                 (see template §5.1): domain(s), models +
                                 pinned versions, current Domain Release,
                                 references/instructions specific to this
                                 project, extensions in use, and cross-
                                 project/cross-domain dependencies.
[Project]/project-registry.md  — PER PROJECT. This project's own registry
                                 (the scoped replacement for the single
                                 global master-registry.md). Entities,
                                 IDs, XM/UXD indices — all project-local.
```

**Decision (locked): independent per-project registry + a thin global
index.** Each project's IDs (ENTITY-ID, RULE-ID, XM-ID, …) stay LOCAL to
that project's registry. There is NO global project prefix on IDs — the
ID formats every engine already uses are unchanged. Two projects can
each have `ENTITY-FIN-001` with zero collision, because their contexts
never load together. Cross-project use is ONLY ever the explicit,
pinned, read-only import of PART 2 — never an implicit shared namespace.

## 1.2 Session Project-Selection Protocol (mandatory first step)

This runs BEFORE CORE-10 Step A (Pre-Flight Discovery) in every engine
session, for every engine, no exceptions:

```
STEP P0 — Project declaration
  The session MUST open with an explicit project line:
      Project: <name>            e.g.  Project: ERP
  - Provided → the engine reads _ecosystem/projects-index.md, resolves
    <name> to its [Project]/ folder, and from that point loads ONLY:
      • that project's project-manifest.md + project-registry.md
      • its selected [Domain]/domain-profile.md (+ version-ledger.md)
      • the module/version subtree the task targets
      • the references named in project-manifest.md
  - Absent → the engine DISPLAYS projects-index.md and asks which
    project. It NEVER guesses, and NEVER proceeds against an unscoped
    or mixed context.
  - Unknown name → the engine asks whether to CREATE it. Creating a
    project is a deliberate P(-1) action — but once confirmed, the
    folders/index/skeleton are built AUTOMATICALLY (§1.3), never by
    the operator hand-making folders.

STEP P1 — Domain + version resolution
  From project-manifest.md the engine resolves which Domain, which
  Domain Release (e.g. ERP@R3), and therefore which pinned Model/
  Extension versions are in scope for this session. Everything the
  engine reads or writes afterward is under that resolved context.

Only after P0+P1 does normal CORE-10 discovery run — now correctly
scoped to one project + one version context.
```

**Context isolation guarantee:** an engine never reads a second
project's registry, profile, or artifacts in the same session. The only
cross-project data that enters is a pinned import the project-manifest
explicitly declares (PART 2), and it enters READ-ONLY.

## 1.3 AUTO-PROVISIONING — the structure builds itself (NEW)

The v4.0 folder tree and its index files are created and maintained
AUTOMATICALLY by the engines via CORE-10 Drive Automation. The operator
never hand-creates a folder, an index, a manifest, or a ledger. The
rule, in one line: **if a required structural path is missing, the
responsible engine creates it from the template here, as part of its
normal CORE-10 Post-Flight Publish — silently for structure, without a
separate confirmation step.**

```
WHO CREATES WHAT, AUTOMATICALLY:

P(-1) Master Registry Builder — on the run that creates/selects a project:
  • _ecosystem/ + projects-index.md + domains-index.md +
    reuse-registry.md      → created from templates (§5.2) if absent.
  • [Project]/ + project-manifest.md (§5.1) + project-registry.md
                            → created if absent; projects-index gets the row.
  • [Project]/[Domain]/ + Core/ + Extensions/ + Models/ +
    _versions/version-ledger.md (§2.3)
                            → the domain skeleton, created if absent.

P-DOMAIN Domain Profile Builder — on the run that authors/evolves a domain:
  • [Project]/[Domain]/domain-profile.md, and the _versions/version-
    ledger.md entries for any Core/Model/Extension version it publishes
                            → created/updated if absent.

ANY engine (P0→P5, Test Gen) — on Post-Flight Publish of its own output:
  • Any missing intermediate folder on its resolved output path
    ([Project]/[Domain]/{Core|Extensions/…|Models/…}/[Module]/[PXX])
                            → created on the fly (standard CORE-10 STEP C
                              "create at designated path"), so an engine
                              never fails because a parent folder is absent.

SELF-HEALING: if any engine's Pre-Flight (CORE-10 STEP A) finds an
_ecosystem/ index file missing, it recreates it empty from the template
before proceeding — the index set can never be permanently lost by an
engine simply not finding it.
```

```
BOUNDARIES (what stays deliberate, NOT auto-invented):
  ✗ A NEW PROJECT is never invented silently — an engine auto-builds the
    skeleton only for a project name the operator declared/confirmed
    (CORE-11 STEP P0). Auto-provisioning creates STRUCTURE, never
    governed CONTENT.
  ✗ A version BUMP (new Extension / new major Version / new Domain
    Release) is never auto-published — that is a P-DOMAIN decision the
    user approves (§2.2, RULE-15). Only the empty folder/ledger scaffold
    is auto-made; what goes in it is governed normally.
  ✗ Auto-provisioning never moves, overwrites, or deletes existing
    content — it only creates what is MISSING. Existing artifacts follow
    the normal CORE-10 STEP C backup-then-replace path.
```

---

═══════════════════════════════════════════════════════════════════
# PART 2 — VERSIONED DOMAINS / MODELS / EXTENSIONS + REUSE
═══════════════════════════════════════════════════════════════════

## 2.1 The taxonomy — Core → Extension → Version → Reuse

```
Core       : the frozen base of a Domain — its foundational models.
Extension  : an ADDITIVE capability layered on top of a specific Core
             version. It never edits Core; it adds to it.
Version     : every Model and every Extension carries v1 → v2 → v3 …
             A PUBLISHED version is IMMUTABLE. New requirements produce a
             new Extension or a new Version — never a mutation of a
             published one that others may depend on.
Reuse      : another project consumes a PINNED version of a Model or
             Extension, READ-ONLY, via its project-manifest dependencies.
```

**Decision (locked): version granularity = Model + Extension + Domain
Release.** Individual Models and Extensions carry their own version
lines; a **Domain Release** is a named lockfile that pins one compatible
set of them together.

## 2.2 The evolution rule (semver-style, deliberately simple)

```
Change is ADDITIVE (new fields/rules/screens that do NOT break an
existing consumer):
  → publish a new EXTENSION, or a MINOR bump of the model.
  → consumers pinned to the prior version keep working untouched.

Change is BREAKING (removes/renames/changes the meaning of something a
consumer relies on):
  → publish a new MAJOR VERSION (v2). The old v1 is FROZEN and RETAINED.
  → no consumer is auto-moved. Upgrading to v2 is an explicit, opt-in
    act recorded in that consumer's project-manifest.

Never: edit a published version in place. If it is published and
something depends on it, it is immutable — full stop.
```

## 2.3 The Version Ledger (the lockfile)

One per domain: `[Project]/[Domain]/_versions/version-ledger.md`.
It records, for the domain, every published Model/Extension version, its
dependencies, and the composition of each Domain Release.

```
## VERSION LEDGER — [Domain]
──────────────────────────────────────────────────────────────────
MODELS
  Model-[name] │ v1 (frozen [date]) │ depends: Core@v1
               │ v2 (frozen [date]) │ depends: Core@v1  │ BREAKING vs v1: [what]
EXTENSIONS
  ext-[name]   │ v1 (frozen [date]) │ on: Model-[name]@v1 │ additive
DOMAIN RELEASES (lockfiles — a named compatible set)
  [Domain]@R1  │ Core@v1 + Model-A@v1 + ext-Tax@v1
  [Domain]@R2  │ Core@v1 + Model-A@v2 + ext-Tax@v1 + ext-Audit@v1
──────────────────────────────────────────────────────────────────
Rule: a Release, once named, is itself immutable. A new compatible set
is a new Release (R3), never an edit of R2.
```

## 2.4 VRE — Version Resolution Event (propagation, extends RXE)

When a depended-on Model/Extension publishes a NEW version, dependents
are NOTIFIED, never silently upgraded. This is the exact shape of the
existing XM Resolution Event (RXE, XM-RESOLUTION-EVENT-PROTOCOL.md /
CONTRACT-8), reused for versions:

```
VRE-[TARGET]-[SEQ] carries to each dependent project/domain:
  Affected item   : Model/Extension + new version (e.g. Model-A@v2)
  Change class    : ADDITIVE | BREAKING
  Required action : evaluate impact; decide pin-stay or opt-in upgrade
Dependent response (in its own project-manifest + registry):
  - ADDITIVE  → may adopt the new extension at will; staying is safe.
  - BREAKING  → stays on the pinned old version unless it explicitly
                upgrades; upgrade is recorded, never assumed.
No dependent is ever moved to a new version without an explicit,
recorded decision. (Same discipline as CONTRACT-7 shared-entity change.)
```

## 2.5 Reuse by pinning (read-only, cross-project)

```
_ecosystem/reuse-registry.md — GLOBAL catalog of what is PUBLISHED and
  available to import: Domain/Model/Extension + version + owning project.

A consuming project imports in its project-manifest.md:
  imports:
    - [OwnerProject]/[Domain]/Model-A@v1      (read-only)
    - [OwnerProject]/[Domain]/ext-Tax@v1      (read-only)

Rules:
  ✓ The import is PINNED to an exact version.
  ✓ The imported artifacts are READ-ONLY — the consumer never edits the
    owner's files, never re-assigns the owner's IDs; it references them.
  ✓ If the consumer needs a change, it either pins a newer published
    version (opt-in) or builds its own Extension on top — the owner's
    original is never modified for the consumer's sake.
  ✗ No implicit reuse. If it is not declared in imports, it is not in
    scope — the isolation guarantee of PART 1 still holds.
```

---

═══════════════════════════════════════════════════════════════════
# PART 3 — DRIVE / REPOSITORY LAYOUT (v4.0)
═══════════════════════════════════════════════════════════════════

Replaces the flat `[GOVERNANCE-ROOT]/[Platform]/[Module]/…` convention.
`[Project]` takes the place of the old `[Platform]`; a `[Domain]` level
and the Core/Extensions/Models/version structure are inserted. This tree
is BUILT AUTOMATICALLY by the engines (§1.3) — it is shown here as the
target shape, not a manual checklist.

```
[GOVERNANCE-ROOT]/
├── _ecosystem/
│   ├── projects-index.md          (global, thin — all open projects)
│   ├── domains-index.md           (global — all domains + their versions)
│   └── reuse-registry.md          (global — published, importable items)
├── _backup/                        (existing — dated pre-replace copies)
└── [Project]/                       e.g. ERP
    ├── project-manifest.md
    ├── project-registry.md         (this project's scoped registry)
    └── [Domain]/                    e.g. erp-core
        ├── domain-profile.md        (P-DOMAIN output — now version-aware)
        ├── _versions/version-ledger.md
        ├── Core/
        │   └── [Module]/[PXX-Folder]/…   (pipeline artifacts, unchanged)
        ├── Extensions/
        │   └── ext-[name]/v{N}/[Module]/[PXX-Folder]/…
        └── Models/
            └── [Model]/v{N}/[Module]/[PXX-Folder]/…
```

```
Notes:
- The inner [PXX-Folder]/[filename] convention (P0.5-PRD/prd.md, P1-SRS/
  srs.md, P2-DB/db-script.md, P3.1-Backend-Exec/…, TEST-GEN/…, etc.) is
  UNCHANGED — only its position in the tree deepened by [Project]/
  [Domain]/{Core|Extensions/ext@v|Models/model@v}.
- Every engine's DRIVE DEPENDENCY TABLE path resolves under the context
  the Session Project-Selection protocol picked (PART 1.2), so the same
  table works for every project/version without per-engine edits.
- master-registry.md (the old single global file) is superseded by the
  per-project project-registry.md + the three _ecosystem/ index files.
  During migration it is split/moved per project; nothing in it is lost.
- REFERENCE (the ERP project, migrated 2026-09-03): the former
  "Foundation" platform layer maps to ERP/erp-core/Core/ (modules SEC,
  NOTIF, FILE, CU); _registry/master-registry.md → ERP/project-registry.md;
  _domain/domain-profile-ERP.md → ERP/erp-core/domain-profile.md. This
  is the worked example of the migration this layout expects.
```

---

═══════════════════════════════════════════════════════════════════
# PART 4 — WHICH ENGINE OWNS WHAT (no new engine)
═══════════════════════════════════════════════════════════════════

## 4.1 P(-1) Master Registry Builder — Ecosystem Registry Authority
```
Now also owns and maintains — creating each AUTOMATICALLY (§1.3) when
missing, never asking the operator to hand-make a folder:
  • _ecosystem/projects-index.md — creates a project (the ONLY place a
    new [Project]/ + project-manifest.md is minted), lists/updates all.
  • each [Project]/project-registry.md — the per-project scoped registry.
  • _ecosystem/reuse-registry.md + domains-index.md — records what each
    project publishes as importable, and the domain roster.
  • the [Project]/[Domain]/{Core|Extensions|Models|_versions} skeleton —
    scaffolded on project/domain creation.
Unchanged: it is still pre-pipeline registry intelligence; it never
generates a module artifact. Auto-provisioning creates STRUCTURE only.
```

## 4.2 P-DOMAIN Domain Profile Builder — Domain Evolution Authority
```
Now also owns and maintains (auto-creating the scaffold per §1.3):
  • the Core/Extensions/Models structure of a domain.
  • [Domain]/_versions/version-ledger.md — records every published
    version, dependencies, and Domain Releases; enforces immutability
    (a published version is never edited) and the additive-vs-breaking
    rule (§2.2).
  • raising VRE (§2.4) when a version is published that others depend on.
Unchanged: it still authors domain-profile.md as an active thinking
partner, and never invents a fact or a version the user did not choose.
A version BUMP is always the user's decision — only its empty scaffold
is auto-made.
```

Every other engine (P0→P5, Test Generation Engine) is UNCHANGED except
that it now begins with the Session Project-Selection protocol (PART
1.2) and reads/writes under the resolved project+version context —
auto-creating any missing intermediate folder on its own output path via
CORE-10 Post-Flight (§1.3).

---

═══════════════════════════════════════════════════════════════════
# PART 5 — TEMPLATES (embedded — no separate files)
═══════════════════════════════════════════════════════════════════

## 5.1 project-manifest.md
```
## PROJECT MANIFEST — [Project]
──────────────────────────────────────────────────────────────────
Project        : [name]                Status: ACTIVE | PAUSED | ARCHIVED
Domain(s)      : [domain] (+ others if the project spans several)
Current Release: [Domain]@R[N]         (the pinned compatible set)
Models in use  : Model-A@v2, Model-B@v1, …
Extensions     : ext-Tax@v1, ext-Audit@v1, …
References     : [project-specific instruction/reference files]
Imports (reuse): [OwnerProject]/[Domain]/Model-X@v1 (read-only), …
Dependencies   : [other projects/domains this one relies on]
Notes          : [free-form context / ideas specific to this project]
──────────────────────────────────────────────────────────────────
```

## 5.2 projects-index.md (row form)
```
## PROJECTS INDEX (global)
──────────────────────────────────────────────────────────────────
Project │ Status  │ Domain(s)     │ Current Release │ Manifest
────────┼─────────┼───────────────┼─────────────────┼──────────────────
ERP     │ ACTIVE  │ erp-core      │ erp-core@R1     │ ERP/project-manifest.md
Retail  │ ACTIVE  │ retail        │ retail@R1       │ Retail/project-manifest.md
──────────────────────────────────────────────────────────────────
```

(version-ledger.md template is in §2.3; reuse-registry rows mirror the
Imports line of §2.5.)

---

═══════════════════════════════════════════════════════════════════
# PART 6 — GOVERNANCE BOUNDARIES & INVARIANTS
═══════════════════════════════════════════════════════════════════
```
INV-1  No engine proceeds without a resolved Project (PART 1.2). No
       guessing, no mixed context.
INV-2  Per-project registries are isolated. An ID is local to its
       project. The only cross-project data is a pinned read-only import.
INV-3  A published Model/Extension/Release version is IMMUTABLE. Change =
       new Extension (additive) or new Version (breaking); the old one is
       frozen and kept.
INV-4  No consumer is auto-upgraded. Version moves are explicit, recorded
       in the consumer's project-manifest, and announced via VRE.
INV-5  Reuse is read-only. A consumer never edits an owner's artifacts or
       re-assigns an owner's IDs.
INV-6  This layer adds NO logic to the pipeline. P0→P5 + Test Gen are
       unchanged; they just run inside the selected context.
INV-7  Simplicity: this ONE file is the whole layer's spec. Do not spread
       it into parallel mechanisms — reuse project-registry, CORE-10,
       RXE, and domain-profile as stated here.
INV-8  The structure is SELF-BUILDING (§1.3). Engines auto-create any
       missing folder/index/manifest/ledger via CORE-10; the operator
       never hand-creates structure. Auto-provisioning makes STRUCTURE
       only — never governed content, never a version bump, and never
       moves/overwrites existing artifacts.
```

---

*End of MULTI-PROJECT-VERSIONING-ARCHITECTURE.md (v4.0)*
*The Selection & Reuse Layer above the pipeline.*
*Two capabilities: parallel isolated projects, and versioned reusable*
*domains/models/extensions (Core → Extension → Version → Reuse).*
*Self-building: the whole structure is auto-provisioned by the engines*
*via CORE-10 (§1.3) — no manual folder creation.*
*Owned by P(-1) (registry/projects) + P-DOMAIN (domain evolution).*
*No new engine, no pipeline change, one spec file — deliberately simple.*
