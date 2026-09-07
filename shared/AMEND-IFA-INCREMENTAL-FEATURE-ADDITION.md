# ERP GOVERNANCE — AMENDMENT: INCREMENTAL FEATURE ADDITION (IFA)
## Adding a feature/change to an ALREADY-IMPLEMENTED module — delta-only, v1 frozen

```
File ID   : AMEND-IFA (Incremental Feature Addition)
Status    : PROPOSED — ready to apply. Engines layer (PART A) is complete
            and apply-ready. Splitter-tool layer (PART B) is an
            implementation SPEC — the actual Python diffs require the
            live agent1/agent2/agent3 source in-session.
Scope     : P1 (SRS), P2 (DB), P2.5 (UI/UX), P3.1 (Backend Exec),
            P3.2 (Frontend Exec), P4.1/P4.2 (Audit), P(-1)/Registry,
            Stage-2 tooling (config.py / marker_parser.py /
            agent1_create_structure.py / agent2_archive.py /
            agent3_splitter.py)
Companion : MULTI-PROJECT-VERSIONING-ARCHITECTURE.md (version model),
            PROJECT-3-REGISTRY.md §3 (task-type detection — the seed of
            this protocol), STAGE-2-GOVERNANCE-TOOLS-2.md (--new-version),
            GOVERNANCE-STABILIZATION-AMENDMENTS.md (amendment style)
Amendment IDs (next-available per engine — adjust if they collide):
            AMEND-P1-D · AMEND-P2-I · AMEND-P25-A · AMEND-P3-P ·
            AMEND-P4-E · AMEND-REG-A · AMEND-TOOL-A
```

```
════════════════════════════════════════════════════════════════
THE PROBLEM THIS SOLVES
════════════════════════════════════════════════════════════════
A module reached implementation — v1 is built and running. A new
feature (or a change to an existing one) is now needed. Two facts
collide:

  1. The pipeline's default path regenerates a module WHOLE. Re-running
     it for one small feature re-emits everything already built.
  2. v1 is real, deployed code. Regenerating over it risks silent drift
     and wasted implementation effort.

Today the ecosystem has TWO PARTIAL mechanisms that already point the
right way but are not wired end-to-end:

  • P3.1/P3.2 task-type "Feature Ext. → Affected phases only"
    (PROJECT-3-REGISTRY.md §3) — but this exists ONLY inside P3. P1, P2,
    and P2.5 have no equivalent formal delta mode, so a feature that
    needs a new field/rule/screen has no clean upstream delta path.
  • agent1 --new-version creates vN alongside v1
    (STAGE-2-GOVERNANCE-TOOLS-2.md) — documented as a capability, but
    the WORKED example never uses it, and agent2/agent3 are not shown
    reading it, and there is no test for the "v1 exists + partial delta"
    scenario.

IFA connects these into ONE coherent delta path across every engine and
the splitter, so that a feature added to an implemented module produces
ONLY the delta, versioned as v2, with v1 left frozen.
════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# PART 0 — CORE CONCEPTS (shared by every engine below)
═══════════════════════════════════════════════════════════════════

## C1 — Change Set (CS-ID) — the delta container

Every incremental addition to an implemented module is wrapped in a
**Change Set**, identified once and carried through every engine:

```
CS-[MOD]-[SEQ]   e.g. CS-PRC-001, CS-PRC-002

A Change Set names ONE coherent incremental change (one feature, one
group of related changes). It is the unit that:
  - selects IFA mode in every engine,
  - stamps every delta artifact header,
  - increments the module version,
  - scopes the splitter package.

The CS-ID is assigned by the FIRST engine that runs for the change
(normally P1) and RECEIVED unchanged by every downstream engine — the
same discipline already used for ENTITY-ID / PLAN-ID.
```

## C2 — Module Version stamping (v1 immutable)

```
Every IFA artifact header carries:
    Module Version : v[N]        (the version being produced, e.g. v2)
    Baseline       : v[N-1]      (the frozen version read as baseline)
    Change Set     : CS-[MOD]-[SEQ]

RULE (immutability — inherited from MULTI-PROJECT-VERSIONING §2.2):
  A published/implemented version is FROZEN. IFA NEVER edits a v1
  artifact in place. It produces v2 artifacts ALONGSIDE v1. v1 files
  are read-only baseline inputs.
```

## C3 — Baseline-Read-Before-Delta (BLOCKING, every engine)

```
No IFA engine may emit a delta without FIRST reading the corresponding
v[N-1] baseline artifact for the module.

  P1   must read v1 srs.md
  P2   must read v1 db-script.md
  P2.5 must read v1 flow-diagram.md + ui-ux-spec.md
  P3.1 must read v1 backend-execution-plan.md
  P3.2 must read v1 frontend-execution-plan.md
  P4.x must read v1 audit report(s) + the v2 delta being audited

If the required baseline is MISSING → STOP (same discipline as CORE-10
Pre-Flight "MISSING = blocking"). IFA cannot run against a module with
no prior implemented version — that case is a normal New-Module run,
not IFA.
```

## C4 — Change Manifest (mandatory header block on every IFA output)

Every IFA artifact opens with a Change Manifest classifying **by ID**
exactly what the delta does. This is the single machine-readable contract
the downstream engines and the splitter read to know what to touch.

```
## CHANGE MANIFEST — CS-[MOD]-[SEQ]
──────────────────────────────────────────────────────────────────
Module          : [MOD]        Module Version : v[N]   Baseline : v[N-1]
Change type     : ADDITIVE | BREAKING           (see C5)
──────────────────────────────────────────────────────────────────
NEW        : [IDs created by this delta — continue existing sequences]
MODIFIED   : [existing IDs whose definition changed — reference v1 ID]
UNCHANGED  : [phases/blocks intentionally NOT re-emitted — by phase/ID]
REMOVED    : [IDs deprecated by this delta — see C5, BREAKING only]
──────────────────────────────────────────────────────────────────
Affected phases (this pass) : [list — the ONLY phases emitted in full]
Untouched phases            : [list — emitted as UNCHANGED stubs only]
──────────────────────────────────────────────────────────────────
```

## C5 — Additive vs Breaking gate (human decision)

```
ADDITIVE  (default IFA): new entities/fields/rules/screens/APIs that do
          NOT remove or change the meaning of anything v1 consumers rely
          on. → stays a MINOR module version bump (v1 → v2). v1 keeps
          working untouched.

BREAKING  : removes/renames/changes the meaning of an existing element a
          consumer (this module OR another module's XM/UXD dependency)
          relies on. → NOT auto-processed. Escalates to a MAJOR-version
          decision owned by the human architecture authority
          (MULTI-PROJECT-VERSIONING §2.2). The engine STOPS and surfaces
          the breaking impact; it never silently produces a breaking v2.

New IDs ALWAYS continue existing sequences — an IFA delta never restarts
a counter (ENTITY-[MOD]-004 after v1 ended at 003, never back to 001).
```

---

═══════════════════════════════════════════════════════════════════
# PART A — ENGINE LAYER (priority 1 — apply first)
═══════════════════════════════════════════════════════════════════

## AMEND-P1-D — SRS Engine: formal IFA (delta-SRS) mode

**Target:** PROJECT-1-SRS-GOVERNANCE-ENGINE.md — MODE 1 entry gate + a
new "IFA MODE" subsection.
**Type:** New governance mode (formalizes the existing informal
"Existing srs.md → amendment mode").

```
TRIGGER (auto-detected, never asked):
  An existing srs.md for this module is attached AS BASELINE, AND the
  request is phrased as an addition/change to an implemented module
  ("add …", "new feature on …", a CS-ID is supplied) → IFA MODE.

IFA MODE behaviour:
  1. Read v1 srs.md as baseline (C3). Load its ID sequences.
  2. Assign/receive CS-[MOD]-[SEQ] (C1).
  3. Produce a DELTA srs.md (Module Version v2) containing:
       - Change Manifest header (C4)
       - PART A: only NEW/MODIFIED entities, rules, LOVs, dependencies
         (new IDs continue v1 sequences; modified blocks cite the v1 ID)
       - PART B: only NEW screen blocks in full; MODIFIED screens as a
         SCREEN DIFF block (what changed only); UNCHANGED screens listed
         by SCR-ID in the manifest, NOT re-emitted.
  4. Run the Additive-vs-Breaking gate (C5). If BREAKING → STOP, surface
     impact, do not emit v2 until the human confirms a major version.
  5. Registry Update block scoped to the delta only.

MUST NOT: renumber v1 IDs; re-emit unchanged blocks; drop the bilingual
message rule for any NEW/MODIFIED RULE-ID; treat the delta as a fresh
module (Zero-Question Protocol still applies to the delta only).
```

---

## AMEND-P2-I — Database Engine: delta-migration mode

**Target:** PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md — new "IFA MODE"
subsection + FULL_DATABASE_SCRIPT note.
**Type:** New governance mode.

```
TRIGGER: delta srs.md (v2, carrying a CS-ID) + v1 db-script.md baseline.

IFA MODE behaviour:
  1. Read v1 db-script.md as baseline (C3) — know every existing table,
     column, sequence, FK, XM-ID.
  2. Produce a DELTA db-script (v2) containing ONLY:
       - a NEW additive Flyway migration (CREATE new tables; ALTER TABLE
         ADD new columns/constraints; new sequences; new lookup seed
         rows) — never a re-emission of v1's FULL_DATABASE_SCRIPT.
       - Change Manifest header (C4) mapping each new object to its
         NEW ENTITY-ID/DBF-ID from the delta srs.
       - new/extended XM-IDs only (XM-ID remains P2-owned).
  3. FULL_DATABASE_SCRIPT rule: the effective v2 schema = v1 script +
     this delta migration, applied in order. The delta file itself
     stays delta-only; the consolidated view is a build-time
     composition, never a hand-copied full re-emit.
  4. Additive-only enforcement (C5): a column DROP/RENAME that v1 (or a
     cross-module XM/UXD) depends on = BREAKING → STOP + escalate.
  5. Registry cascade unchanged: a new DBS-ID/XM-ID still fires the
     XM RESOLUTION EVENT scan for DEFERRED dependents.

Flyway note: the delta migration is a NEW versioned migration file
(Vn__cs_[mod]_[seq].sql), never an edit to an already-applied v1
migration — matches Flyway's own immutability rule and C2.
```

---

## AMEND-P25-A — UI/UX Design Engine: delta-design + Shell Delta (FRONTEND FOCUS)

**Target:** UI-UX-DESIGN-ENGINE.md — extends Section 6 (Continuation)
into a full IFA mode, and adds a Shell Delta handoff to Section 5.
**Type:** New governance mode. **This is the frontend-impact core of the
amendment — a feature on an implemented module changes the running UI.**

```
WHY THIS MATTERS: v1's UI Shell is REAL, deployed React code. A delta
feature must NOT trigger a fresh full-shell rebuild. P2.5 must tell
Claude Code precisely which shell pieces are NEW / MODIFIED / UNCHANGED
so the v2 shell touches only the delta.

TRIGGER: delta srs.md (v2, new/changed US-IDs or SCR-IDs) + approved v1
flow-diagram.md + ui-ux-spec.md (Status: RECONCILED) as baseline.

IFA MODE behaviour:
  1. Read v1 flow-diagram.md + ui-ux-spec.md as baseline (C3).
  2. Produce a DELTA design (v2):
       - NEW screens: full flow + spec + mockup (Claude Design), as normal.
       - MODIFIED screens: a SCREEN DIFF block — only the fields/sections/
         interactions that changed, plus ONE updated mockup of the changed
         screen. The unchanged parts of the screen are referenced, not
         redrawn.
       - UNCHANGED screens: listed by SCR-ID in the Change Manifest,
         NOT re-drawn and NOT re-mocked.
       - Container Pattern (AMEND-P3-O) re-evaluated ONLY for new/modified
         screens; unchanged screens keep their v1 pattern.
  3. Emit a SHELL DELTA MANIFEST (new — the frontend-critical artifact):

     ## SHELL DELTA MANIFEST — CS-[MOD]-[SEQ]
     ──────────────────────────────────────────────────────────────
     NEW shell pieces      : [routes/components Claude Code must ADD]
     MODIFIED shell pieces : [existing routes/components to EDIT + what]
     UNCHANGED shell pieces: [existing routes/components to LEAVE AS-IS]
     ──────────────────────────────────────────────────────────────

  4. New gate: GATE: UI SHELL DELTA COMPLETE — human sign-off on JUST
     the delta shell (the NEW + MODIFIED pieces), not a full-shell
     re-review. This replaces GATE: UI SHELL COMPLETE for IFA runs.

Downstream sequence (IFA variant of Section 5's v2.1 chain):
  P2.5 delta design (approved)
        ↓
  Claude Code — Shell DELTA only (add NEW, edit MODIFIED, leave UNCHANGED)
        ↓
  GATE: UI SHELL DELTA COMPLETE (human sign-off on delta shell)
        ↓ (with GATE: BACKEND MODULE COMPLETE for the delta APIs)
  P3.2 IFA mode — F1 confirms only new/changed models; F4 documents the
  delta shell routing/wiring only.

MUST NOT: re-mock unchanged screens; re-review the whole shell;
re-select container patterns for unchanged screens; renumber SCR-IDs.
```

---

## AMEND-P3-P — Execution Plan engines: formal IFA (delta-plan) mode

**Target:** PROJECT-3-REGISTRY.md §3 (task-type table),
PROJECT-3-BACKEND-ENGINE.md, PROJECT-3-FRONTEND-ENGINE.md.
**Type:** Formalizes "Feature Ext. → Affected phases only" into a full,
baseline-anchored, version-stamped delta with a machine-readable manifest.

```
§3 task-type table — ADD an IFA column note:
  "Feature Ext." and "Behavior Mod." running against an IMPLEMENTED
  module (a v1 execution-plan baseline is attached + a CS-ID present)
  are IFA runs. Scope stays "Affected phases only", now with the
  additional IFA obligations below.

IFA MODE behaviour (both passes):
  1. Read v1 execution-plan as baseline (C3); load ID sequences.
  2. Receive CS-[MOD]-[SEQ] + Module Version from the delta srs (C1/C2).
  3. Emit the plan with:
       - Change Manifest header (C4), including "Affected phases" and
         "Untouched phases".
       - AFFECTED phases: full phase content, but only NEW/MODIFIED
         elements (new FIELD/API/ERR/QR IDs continue v1 sequences).
       - UNTOUCHED phases: a one-line UNCHANGED STUB —
         "### [PHASE] — UNCHANGED from v1 — see v1 plan" — NO body.
         (The splitter reads these stubs and skips them, PART B.)
  4. Backend F-path: F1 (IFA) confirms only new/changed models against
     the delta db-script + real delta API Docs; F4 documents only the
     Shell Delta pieces from the P2.5 Shell Delta Manifest.
  5. ALIGN-BE/ALIGN-FE gate runs over the DELTA scope, but ALSO performs
     a REGRESSION assertion: no NEW/MODIFIED element breaks an existing
     v1 ALIGN mapping (if it would → BREAKING, C5 → STOP).

MUST NOT: emit unchanged phases in full; renumber IDs; assign XM-IDs in
either pass; start P3.2 IFA before GATE: UI SHELL DELTA COMPLETE +
GATE: BACKEND MODULE COMPLETE (delta) are both confirmed.
```

---

## AMEND-P4-E — Audit engines: scoped delta audit + regression check

**Target:** PROJECT-4-BACKEND-AUDIT.md, PROJECT-4-FRONTEND-AUDIT.md.
**Type:** New audit scope mode.

```
TRIGGER: a v2 delta plan (carrying a Change Manifest + CS-ID) + its v1
baseline + v1 audit report.

IFA AUDIT behaviour:
  1. Read the Change Manifest (C4). Audit CONTENT correctness only for
     NEW/MODIFIED IDs and their cross-references — not the whole module.
  2. REGRESSION CHECK (new, mandatory): for every existing v1 XM-ID
     (P4.1) / UXD-ID (P4.2) that touches a MODIFIED element, re-verify
     it is still satisfied. A regression = Finding, severity MAJOR,
     blocks delta implementation.
  3. Confirm UNCHANGED phases were genuinely not altered (hash/ID match
     against v1) — a phase claimed UNCHANGED whose content differs from
     v1 is a CRITICAL finding (silent scope creep).
  4. Confirm Additive-vs-Breaking classification (C5) is honest — a
     delta labelled ADDITIVE that actually removes/renames a depended-on
     element is CRITICAL.
  5. Report scoped to the delta; overall verdict clears only the delta.
```

---

## AMEND-REG-A — Registry & versioning: Change Set ledger + version bump

**Target:** P(-1) Master Registry Builder / project-registry.md,
modules-registry.json, MULTI-PROJECT-VERSIONING linkage.
**Type:** Registry mechanism.

```
On a completed IFA delta:
  1. modules-registry.json: bump the module version (v1 → v2) for [MOD];
     v1 entry retained/frozen.
  2. project-registry.md: append NEW IDs (never delete v1 IDs);
     add a CHANGE SET LOG entry:
       CS-[MOD]-[SEQ] | date | ADDITIVE/BREAKING | NEW/MODIFIED IDs |
       from vN-1 → vN | Registry Event Log ref
  3. Version-model linkage (MULTI-PROJECT-VERSIONING §2.2):
       ADDITIVE delta  → MINOR bump / new Extension of the module.
       BREAKING delta   → MAJOR version (v2 as a new major line), frozen
                          v1 retained; dependents notified via VRE.
  4. Global XM/UXD indexes: new dependencies from the delta appended;
     existing ones re-evaluated only where a MODIFIED element touches them.
```

---

═══════════════════════════════════════════════════════════════════
# PART B — SPLITTER TOOL LAYER (priority 2 — the second phase)
═══════════════════════════════════════════════════════════════════

**Status: IMPLEMENTATION SPEC, not code.** The actual Python diffs need
the live `config.py`, `marker_parser.py`, `agent1_create_structure.py`,
`agent2_archive.py`, `agent3_splitter.py` in-session (they were reviewed
previously as a zip, not present in this session). This section defines
exactly what each tool must do so the code change is mechanical when the
files are available.

## AMEND-TOOL-A — end-to-end `--new-version` + delta packaging

```
GOAL: the packages handed to the implementation agent for a v2 delta
contain ONLY the delta phases — never the whole module again.

agent1_create_structure.py
  --module [MOD] --new-version
    → creates modules/[MOD]/v2/{P0…P4_2,packages}/ ALONGSIDE v1
      (v1 untouched). Increments the version in modules-registry.json.
    → manifest.json for v2 records: baseline_version = v1,
      change_set = CS-[MOD]-[SEQ].
  [GAP TO CLOSE: the WORKED example in STAGE-2-GOVERNANCE-TOOLS-2.md §5
   STEP 1 must be updated to show the --new-version path, not only the
   bare --module path.]

agent2_archive.py
  --module [MOD] --stage backend|frontend --version v2
    → archives the v2 DELTA artifacts into modules/[MOD]/v2/…
    → reads v1 manifest to record baseline_version; archives the delta
      srs/db-script/execution-plan (which already contain UNCHANGED
      stubs, per AMEND-P3-P), plus the Change Manifest.
  [GAP TO CLOSE: add the --version flag; default to latest if omitted;
   never overwrite v1.]

agent3_splitter.py
  --module [MOD] --stage backend|frontend --version v2
    → Stage 1 parse: recognise UNCHANGED-STUB phases (AMEND-P3-P) and
      the Change Manifest. SKIP UNCHANGED phases entirely — produce NO
      package file for them.
    → Stage 2/3: group + write package files ONLY for AFFECTED phases.
    → Stage 5 verification: hash-check only the delta package content
      against the delta source (unchanged phases are out of scope by
      construction).
    → NEW option (or auto from Change Manifest): --delta — assert that
      at least one UNCHANGED stub exists; if a run flagged --version v2
      but every phase is full (no stubs), warn (possible accidental
      full re-emit).
  [GAP TO CLOSE: (a) UNCHANGED-stub recognition in marker_parser.py /
   Stage 1; (b) delta-only packaging in Stage 2/3; (c) config.py must
   know the vN folder layout for archive/package paths.]

pytest (the missing evidence, per this session's audit)
  Add a scenario test: module with v1 fully packaged, then a v2 delta
  with (i) one AFFECTED phase carrying one NEW id, (ii) the rest as
  UNCHANGED stubs. Assert:
    - agent1 --new-version creates v2/ without touching v1/,
    - agent2 --version v2 archives only the delta,
    - agent3 produces package files for the AFFECTED phase ONLY,
    - v1 packages are byte-identical before/after (frozen),
    - Stage 5 passes on the delta.
```

## AMEND-TOOL-A — impact checklist (append to STAGE-2 §10)

```
[ ] Adding IFA/--new-version delta packaging
      → agent1: --new-version folder + modules-registry.json bump +
        v2 manifest (baseline_version, change_set)
      → agent2: --version flag, never overwrite v1
      → agent3 + marker_parser.py: UNCHANGED-stub recognition +
        delta-only Stage 2/3 + scoped Stage 5
      → config.py: vN path layout
      → STAGE-2 §5 worked example: show the --new-version path
      → pytest: the v1-frozen + v2-delta scenario above
```

---

═══════════════════════════════════════════════════════════════════
# APPLICATION ORDER
═══════════════════════════════════════════════════════════════════

```
1. PART A first (engines) — apply AMEND-P1-D → P2-I → P25-A → P3-P →
   P4-E → REG-A into the corresponding engine instruction files and
   re-sync into their Claude Projects. These are prose-governance edits;
   no code, no tooling dependency.

2. Verify PART A end-to-end on ONE small dry-run: take an implemented
   module, request a tiny additive feature, confirm each engine emits a
   Change Manifest + delta-only output + v1 read as baseline.

3. PART B second (tooling) — bring the live agent1/2/3 + config.py +
   marker_parser.py into a session and apply AMEND-TOOL-A, then run the
   new pytest scenario. Keep prose (PART A stubs) and tooling in sync in
   the SAME change — the standing ecosystem rule.
```

*End of AMEND-IFA. PART A is complete and apply-ready. PART B is a*
*precise spec pending the live tooling source.*
