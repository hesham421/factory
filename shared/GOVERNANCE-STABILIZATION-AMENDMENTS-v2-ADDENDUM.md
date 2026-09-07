═══════════════════════════════════════════════════════════════════
# GOVERNANCE STABILIZATION AMENDMENTS — v2.0 ADDENDUM
## Backend/Frontend Split + PRD/UI-UX Integration
═══════════════════════════════════════════════════════════════════

```
Document Type  : Stabilization Patch Record — ADDENDUM (append to end
                 of existing GOVERNANCE-STABILIZATION-AMENDMENTS.md,
                 immediately before the file's closing lines)
Scope          : Project 3, Project 4, and two brand-new engines
Status         : APPLY IN FULL — these amendments harden the v2.0
                 architecture without discarding the original 27
Application    : New amendments follow the exact same surgical
                 replace/insert convention as AMEND-P1-A through
                 AMEND-MAP-D above. Nothing above this addendum is
                 altered or removed.
Traceability   : Each amendment cites the architectural decision it
                 implements (from the Master Reviewer session record)
```

```
════════════════════════════════════════════════════════════════
⚠ v3.0 SUPERSESSION NOTICE — READ BEFORE APPLYING P3/P4 AMENDMENTS
════════════════════════════════════════════════════════════════
This addendum was written for v2.0/v2.1, when the Execution Plan
engine (P3) ALSO generated the test artifacts in a "MODE 2.5" step,
and the Audit engine (P4) ran a CHECK-4 against those test plans.

BOTH of those are NO LONGER TRUE as of v3.0 ("P3 LIGHT"). Where this
addendum still says otherwise, the following overrides it:

  1. AMEND-P3-K — the "MODE 2.5 (… Output: backend-test-plan.md +
     test-execution-manifest.md)" and "MODE 2.5 (… Output:
     frontend-test-plan.md)" lines are SUPERSEDED. P3.1/P3.2 now
     produce ONLY their execution plans. There is no MODE 2.5 in P3.
     The ALIGN-BE / ALIGN-FE gate split and the PASS 1 / PASS 2
     structure in AMEND-P3-K remain fully in force — only the test
     outputs are removed.

  2. AMEND-P3-L — the test-execution-manifest.md generation rule is
     SUPERSEDED as a P3 rule. It is now owned, verbatim in substance,
     by the standalone Test Generation Engine
     (PROJECT-TEST-GENERATION-ENGINE.md), which generates
     backend-test-plan.md + test-execution-manifest.md after ALIGN-BE ✓
     and frontend-test-plan.md after ALIGN-FE ✓. CONTRACT-13 (manifest
     → P5) still holds; only the producer changed from P3 to the Test
     Generation Engine.

  3. AMEND-P4-E — every "CHECK-4" reference is SUPERSEDED. P4.1 and
     P4.2 no longer carry CHECK-4; test coverage is OUT of audit scope
     entirely. The dual-gate split (P4.1 backend / P4.2 frontend, both
     pre-implementation, P4.2 reads P4.1 first), the 4A-BE-/4A-FE-
     Finding-ID formats, and CHECK-8's DOC/INT-C handling all remain
     fully in force. Where AMEND-P4-E lists the checks each gate
     applies, strike CHECK-4 from both lists and leave the rest.

Net for the two AUDIT projects that load this file: apply everything
in AMEND-P4-E EXCEPT any instruction to run CHECK-4 against a
test-plan. If a session asks the audit to "run CHECK-4", the correct
response is that CHECK-4 was removed in v3.0.

v4.0 note: these amendments are unaffected by the Multi-Project +
Versioning layer, except that the per-project project-registry.md
replaces the single master-registry.md wherever an amendment references
the registry. See MULTI-PROJECT-VERSIONING-ARCHITECTURE.md.
════════════════════════════════════════════════════════════════
```

**Why an addendum, not a rewrite:** The 27 amendments above already
apply cleanly to the pre-v2.0 project files. v2.0 does not invalidate
any of them — CORE-8 (stack), CORE-9 (composite screens), the XM-ID
format work (AMEND-P2-B/C/E/F), the SOFT-READ mechanism (AMEND-P2-D),
Recovery Protocol (AMEND-P2-G), and the B2/F2 determinism work
(AMEND-P3-B/C) all remain exactly as specified. Only Project 3 and
Project 4 need structural amendment for the Backend/Frontend split;
everything else is additive (two new engines).

---

═══════════════════════════════════════════════════════════════════
# ADDITIONAL AMENDMENTS — v2.1 — TO SHARED-GOVERNANCE-CORE.md,
# shared-governance-rules.md, shared-artifact-contracts.md,
# PRD-ENGINE.md, UI-UX-DESIGN-ENGINE.md,
# PROJECT-1-SRS-GOVERNANCE-ENGINE.md
═══════════════════════════════════════════════════════════════════

---

## AMEND-CORE-A
**Resolves:** Ambiguity in how Product Intent (PRD) and Design Intent
(UI/UX) relate to the functional pipeline — v2.0 treated PRD as a
non-gating parallel input and required UI/UX to wait for both PRD and
SRS before starting. Session decision reverses both defaults.
**Target:** SHARED-GOVERNANCE-CORE.md (CORE-2, CORE-5 RULE-1/RULE-8),
shared-governance-rules.md (RULE-1, RULE-8, RULE-14, new RULE-16,
Section 2 boundaries for Project 1 and Project 2.5, Section 4 state
machine), shared-artifact-contracts.md (CONTRACT-10, CONTRACT-11),
PRD-ENGINE.md, UI-UX-DESIGN-ENGINE.md, PROJECT-1-SRS-GOVERNANCE-ENGINE.md
**Type:** Two paired decisions — one gate added, one gate relaxed

```
DECISION 1 — Project 0.5 (PRD) now HARD-GATES Project 1 (SRS):
  Was (v2.0)  : PRD never gates P1; P1 and P0.5 run in parallel,
                fully independent (CONTRACT-10 "never waits on
                Project 1").
  Now (v2.1)  : P1 MUST NOT begin without prd-[MOD].md attached, in
                addition to its existing P0 inputs (CONTRACT-10
                REVISED). Chosen deliberately for traceability over
                parallelism. RULE-14/HR-10 are UNCHANGED — a hard
                gate on prd.md's existence never becomes authority
                over its content; every RULE-ID/ENTITY-ID/API-ID is
                still P1's own independent decision.

DECISION 2 — Project 2.5 (UI/UX) now starts from prd.md ALONE, in
              parallel with Project 1 (not after both are done):
  Was (v2.0)  : UI/UX Design Engine MUST NOT begin generation until
                BOTH prd.md AND srs.md are attached (CONTRACT-11
                "does not start from PRD alone and complete later").
  Now (v2.1)  : UI/UX begins the moment prd.md exists, drafting
                flow-diagram.md/ui-ux-spec.md/mockups from PRD alone,
                concurrently with Project 1. The PRD↔SRS
                Reconciliation Gate (CONTRACT-11) MOVES from
                "before generation" to "before human approval" — it
                now catches drift in an already-drafted package and
                triggers BOUNDED rework (flagged screens only, never
                a full restart), rather than preventing draft-time
                drift by forcing sequencing.

NET EFFECT ON PARALLELISM (important — the two decisions pull in
opposite directions, and net out to a specific shape, not simple
"more" or "less" parallelism):
  Track 1 (P1 → P2 → P3.1 → P4.1 → IMPL-BE → API-DOC-GEN) now starts
    later (blocked on P0.5 first) but then runs completely
    independently of Track 2 all the way to GATE: BACKEND MODULE
    COMPLETE — it is NEVER blocked by the Reconciliation Gate or
    human approval.
  Track 2 (P2.5-draft → Reconciliation Gate → approval) starts as
    early as possible (right after P0.5, same moment as Track 1
    begins) and only needs to FINISH by the time Track 1 reaches
    GATE: BACKEND MODULE COMPLETE — which, given how much happens in
    Track 1 (P2, P3.1, P4.1, full backend implementation, API doc
    generation), leaves Track 2 a very wide completion window.

Self-correction logged: an earlier draft of this amendment
(mid-session) incorrectly sequenced P2/P3.1 AFTER the Reconciliation
Gate/human approval. This was caught and fixed before delivery — P2
and P3.1 depend only on Project 1's srs.md, never on Track 2's state.
```

**Contract violation additions:**
```
srs.md generated without prd-[MOD].md attached
  → SEQUENCE VIOLATION, CRITICAL severity (CONTRACT-10)
Project 2.5 output reaching human approval without the
  Reconciliation Gate having run against the finished srs.md
  → SEQUENCE VIOLATION, CRITICAL severity (CONTRACT-11)
Project 2 or Project 3.1 blocked/delayed pending Track 2's
  Reconciliation Gate or human approval
  → BOUNDARY VIOLATION, MAJOR severity — Track 1 must never wait on
    Track 2 before GATE: BACKEND MODULE COMPLETE
```

---

═══════════════════════════════════════════════════════════════════
# ADDITIONAL AMENDMENTS TO PROJECT 3
# (at the time a single file, PROJECT-3-EXECUTION-PLAN-GOVERNANCE-
#  ENGINE.md — AMEND-P3-K below is the amendment that splits it into
#  PROJECT-3-BACKEND-ENGINE.md + PROJECT-3-FRONTEND-ENGINE.md, sharing
#  PROJECT-3-REGISTRY.md as backbone; that single pre-split filename
#  no longer exists anywhere in the ecosystem — this is expected, not
#  a broken reference)
═══════════════════════════════════════════════════════════════════

---

## AMEND-P3-K
**Resolves:** Real-contract drift risk — a frontend built against a
planned (not real) backend API surface
**Target:** the then-single Project 3 engine file (pre-split) — Section
1 (Role/Scope) and Section 9 (ALIGN Gate). This amendment IS the split:
its Role/Scope replacement text below is what now lives, respectively,
as PROJECT-3-BACKEND-ENGINE.md Section 1 (PASS 1 content) and
PROJECT-3-FRONTEND-ENGINE.md Section 1 (PASS 2 content); its ALIGN
Gate rename is now PROJECT-3-BACKEND-ENGINE.md's ALIGN-BE gate and
PROJECT-3-FRONTEND-ENGINE.md's ALIGN-FE gate.
**Type:** Structural split — one project, two temporal passes
**⚠ v3.0:** the two "MODE 2.5" blocks in the text below are SUPERSEDED
— P3 no longer generates any test artifact; those outputs are now the
Test Generation Engine's (see the v3.0 Supersession Notice at the top
of this addendum). Everything else in AMEND-P3-K stands.

Replace the project's opening Role/Scope statement with:

```
This engine operates in TWO temporally separate passes within the
same project. It is not split into two Claude Projects — it is one
project with a mandatory pause point between passes.

PASS 1 (Backend) — MODE 2:
  Phases: CORE, DATA+DOM, SVC+API, DOC, INT-C, INT-R, SEC
  Output: backend-execution-plan.md
  Gate  : ALIGN-BE (renamed from ALIGN — see below)
  [v3.0 SUPERSEDED — MODE 2.5 removed: backend-test-plan.md +
    test-execution-manifest.md are now generated by the Test
    Generation Engine after ALIGN-BE ✓, not here. See AMEND-P3-L note.]

  ─── MANDATORY PAUSE POINT ───
  Real implementation happens here (Claude Code, outside this project).
  Real API Docs are generated here (api-doc-generator, outside this
  project). This project does NOT resume until GATE: BACKEND MODULE
  COMPLETE is confirmed by the user (see CONTRACT-12 in
  shared-artifact-contracts.md).

PASS 2 (Frontend) — MODE 2, resumed:
  Phases: F1, F2, F3, F4, SEC (frontend-facing)
  Input : real API Docs (NOT the PASS 1 DOC-1 artifact) + flow-diagram.md
          + ui-ux-spec.md (Project 2.5, human-approved) + srs.md
  Output: frontend-execution-plan.md
  Gate  : ALIGN-FE
  [v3.0 SUPERSEDED — MODE 2.5 removed: frontend-test-plan.md is now
    generated by the Test Generation Engine after ALIGN-FE ✓, not here.]

This project uses the SAME continuation protocol (CORE-6) to resume
into PASS 2 as it would to resume any interrupted session — the pause
is a designed session boundary, not an exception to normal behavior.
```

In Section 9 (ALIGN Gate), rename every instance of "ALIGN" to
"ALIGN-BE" when the gate is evaluating PASS 1 content, and add a new
parallel gate "ALIGN-FE" with the identical table structure (Tables
1-5 as already defined), evaluated against PASS 2 content only. The
two gates are never merged into one table — they gate two different
implementation events.

**DOC phase note (supersedes prior framing):** The DOC phase (API
Contract Summary) still exists in PASS 1 as an internal planning
artifact — it is useful for the backend team's own consistency check.
What changes is its status as a FRONTEND input: PASS 2 never reads it.
See CONTRACT-12.

---

## AMEND-P3-L
**⚠ v3.0 SUPERSEDED AS A P3 RULE.** The manifest-generation rule below
no longer runs inside P3. It moved, unchanged in substance, to the
standalone Test Generation Engine (PROJECT-TEST-GENERATION-ENGINE.md),
which now generates test-execution-manifest.md alongside
backend-test-plan.md after ALIGN-BE ✓. CONTRACT-13 (manifest → P5)
still holds; only the producer changed. The specification is preserved
below for historical continuity and because the Test Generation Engine
implements it verbatim.

**Resolves:** P5 (api-verify) coupling to execution-plan.md/test-plan.md
internal structure
**Target (original):** the then-single Project 3 engine file (pre-split)
— Section 8.12 (TC Coverage Matrix Summary) or nearest MODE 2.5 section.
**Target (v3.0):** PROJECT-TEST-GENERATION-ENGINE.md — the manifest is a
backend-mode Test Generation Engine artifact.
**Type:** New output artifact, generated alongside backend-test-plan.md

Insert immediately after backend-test-plan.md generation (now in the
Test Generation Engine's backend mode):

```
## test-execution-manifest.md — Generation Rule

Generated automatically, same session, immediately after
backend-test-plan.md, once ALIGN-BE ✓ is confirmed. This is a DERIVED
VIEW — it introduces no new RULE-ID, ERR-ID, or TC-ID; it only
reorganizes what backend-execution-plan.md and backend-test-plan.md
already established, into a form Project 5 can consume without
re-parsing either source file.

Contents (three sections, all pre-computed by this engine, not left
for Project 5 to derive):

SECTION: DEPENDENCY ORDER
  Topological entity build order, derived from the ENTITY REGISTRY
  Business Code pattern column (e.g. BR-[LE_CODE]-NNNNN ⇒ Branch
  depends on LegalEntity) cross-checked against RULE-IDs of the form
  "X must belong to active Y".

SECTION: RULE→ERR→TC TRIPLES
  For every RULE-ID that has both a corresponding ERR-ID (Error
  Catalog) and a TC-BE-ID (backend-test-plan.md), emit one row:
  RULE-ID │ ERR-ID │ TC-BE-ID │ HTTP Status
  Skip any RULE-ID explicitly marked "consuming-module only" /
  "informational" (not independently testable at this module's API).

SECTION: ENTITY CRUD CHECKLIST
  Per entity: which of Create/Search/Update/Activate/Deactivate/
  GetById/Delete actually exist, per the SVC+API phase — a direct
  flag table, not narrative.

Regeneration rule: if backend-execution-plan.md or backend-test-plan.md
is amended after this manifest was generated, the manifest MUST be
regenerated in the same session before being handed to Project 5. A
stale manifest is a CONTRACT-13 violation risk, not a cosmetic issue.
```

---

═══════════════════════════════════════════════════════════════════
# ADDITIONAL AMENDMENTS TO PROJECT 4
# (at the time a single file, PROJECT-4-GOVERNANCE-AUDIT-ENGINE.md —
#  AMEND-P4-E below is the amendment that splits it into
#  PROJECT-4-BACKEND-AUDIT.md + PROJECT-4-FRONTEND-AUDIT.md; that
#  single pre-split filename no longer exists anywhere in the
#  ecosystem — this is expected, not a broken reference)
═══════════════════════════════════════════════════════════════════

---

## AMEND-P4-E
**Resolves:** Single-gate assumption no longer matches a two-pass
execution plan (Backend then Frontend, separated by real implementation)
**Target:** the then-single Project 4 engine file (pre-split) — Section
1 (Role), Section 5 (Report Format), and every CHECK that references
"execution-plan.md" or "test-plan.md" as a single file. This amendment
IS the split: its Role replacement text below is what now lives,
respectively, as PROJECT-4-BACKEND-AUDIT.md (P4.1 content) and
PROJECT-4-FRONTEND-AUDIT.md (P4.2 content).
**Type:** Structural split — the engine runs twice, both pre-implementation
**⚠ v3.0:** every CHECK-4 reference below is SUPERSEDED — P4.1/P4.2 no
longer run CHECK-4 and take no test-plan/manifest input. Apply this
amendment with CHECK-4 struck from both gates' check lists; everything
else (the dual-gate split, Finding-ID formats, CHECK-8 handling)
stands. The Role text below is shown with the v3.0 correction applied.

Replace the project's opening Role statement with:

```
This engine runs TWICE per module — never once, never post-implementation.

P4.1 — BACKEND AUDIT GATE
  Runs      : after PASS 1 ALIGN-BE ✓ (backend-execution-plan.md exists)
  Runs before: Backend implementation begins
  Applies   : CHECK-0 through CHECK-9 (backend-relevant scope)
              [v3.0: NO CHECK-4 — test coverage is out of audit scope;
               no test-plan/manifest input]
  Produces  : Finding-IDs formatted 4A-BE-[AUDIT]-[SEQ]
  Does NOT read: any frontend artifact (none exist yet); any test
              artifact (out of scope, v3.0)

P4.2 — FRONTEND AUDIT GATE
  Runs      : after PASS 2 ALIGN-FE ✓ (frontend-execution-plan.md exists)
              AND after real API Docs + Project 2.5 human-approved
              outputs exist
  Runs before: Frontend implementation begins
  Applies   : CHECK-2 (SRS↔Plan), CHECK-9 (LOV E2E), CHECK-10
              (Security Completeness) — scoped to frontend artifacts
              [v3.0: NO CHECK-4 — test coverage is out of audit scope]
  MANDATORY : reads the P4.1 report first — confirms no backend drift
              occurred between P4.1 and the start of frontend planning
  Produces  : Finding-IDs formatted 4A-FE-[AUDIT]-[SEQ]

Both gates are pre-implementation. This is NOT a reintroduction of
MODE 4B (post-implementation audit remains permanently abolished).
Running twice, both before their own respective build, is a different
governance statement than running once, after everything is built.
```

Update every CHECK section (CHECK-0 through CHECK-10) that currently
reads "execution-plan.md" to instead read "backend-execution-plan.md
(P4.1 scope) or frontend-execution-plan.md (P4.2 scope), as applicable
to the check". [v3.0: the former instruction to split test-plan.md
references per gate is dropped — no CHECK reads a test-plan anymore.]

In Section 5 (Report Format), change the report header field from a
single AUDIT-SEQ to two independent sequences (4A-BE-[SEQ] and
4A-FE-[SEQ]), each reset/continued independently per CONTRACT-5.

**CHECK-8 note (Contract Gate Compliance):** This check's DOC/INT-C
gate verification now runs exclusively within P4.1 (both gates are
backend-only concepts under v2.0 — see CONTRACT-12). P4.2 does not
re-check DOC/INT-C; it instead verifies the NEW gate (GATE: BACKEND
MODULE COMPLETE) was satisfied before PASS 2 began.

---

═══════════════════════════════════════════════════════════════════
# NEW ENGINES (NOT AMENDMENTS — NEW FILES, NOTED HERE FOR TRACEABILITY)
═══════════════════════════════════════════════════════════════════

```
These are NEW project files, not amendments to existing ones. They are
tracked here only so the amendment history stays a complete audit trail.
Full content is delivered as standalone files, not as patches:

  PRD-ENGINE.md              — Project 0.5, new
  UI-UX-DESIGN-ENGINE.md     — Project 2.5, new
  PROJECT-TEST-GENERATION-ENGINE.md — Test Generation Engine, new in
                                v3.0 (standalone, OUTSIDE the pipeline).
                                Now the owner of backend-test-plan.md,
                                frontend-test-plan.md, and
                                test-execution-manifest.md — the outputs
                                AMEND-P3-K's MODE 2.5 and AMEND-P3-L used
                                to place inside P3.
  PROJECT-5-MODE-5-instructions.md — amended separately (see its own
                                file) to consume test-execution-manifest.md
                                per CONTRACT-13/AMEND-P3-L above. v3.0:
                                the manifest now comes from the Test
                                Generation Engine, not P3 — P5's consume
                                behavior is unchanged.
  PROJECT-REG-STATE-REGISTRY-EXTRACTOR.md — amended separately (its
                                1:1 file mapping table needs updating
                                for the now-doubled execution-plan/
                                test-plan file count)
```

---

═══════════════════════════════════════════════════════════════════
# v2.0 AMENDMENT APPLICATION CHECKLIST
═══════════════════════════════════════════════════════════════════

Apply AFTER all 27 original amendments (Priority 1-4) are already in
place — this checklist assumes the pre-v2.0 baseline is stable.

```
Priority 5 — Backend/Frontend structural split (v2.0):
  □ AMEND-P3-K — PASS 1 / PASS 2 split + ALIGN-BE / ALIGN-FE rename
                 (v3.0: MODE 2.5 test outputs removed)
  □ AMEND-P3-L — test-execution-manifest.md generation rule
                 (v3.0: now the Test Generation Engine's, not P3's)
  □ AMEND-P4-E — P4.1 / P4.2 dual-gate split
                 (v3.0: CHECK-4 struck from both gates)

Priority 5.5 — PRD/UI-UX pipeline relationship (v2.1 — apply AFTER
Priority 5, since it touches the same shared files):
  □ AMEND-CORE-A — PRD hard-gates P1 (CONTRACT-10 revised) +
    UI/UX starts from PRD alone in parallel with P1, reconciles
    against SRS before human approval (CONTRACT-11 revised)
  □ Verify Track 1 (P1→P2→P3.1→...) never blocked by Track 2's
    Reconciliation Gate or approval — this was a caught-and-fixed
    sequencing error during drafting; re-verify after deployment

Priority 6 — New engine deployment (v2.0/v2.1/v3.0):
  □ Deploy PRD-ENGINE.md as Project 0.5 (now v2.1 — hard gate)
  □ Deploy UI-UX-DESIGN-ENGINE.md as Project 2.5 (now v2.1 — parallel-draft)
  □ Deploy PROJECT-TEST-GENERATION-ENGINE.md as the standalone Test
    Generation Engine (v3.0 — owns the test artifacts P3 no longer makes)
  □ Apply the P5 amendment documented in
    PROJECT-5-MODE-5-instructions.md's own change log
  □ Apply the P-REG amendment documented in
    PROJECT-REG-STATE-REGISTRY-EXTRACTOR.md's own change log

Priority 7 — Companion file sync (v2.0/v2.1):
  □ shared-artifact-contracts.md   → v2.1 (already delivered)
  □ SHARED-GOVERNANCE-CORE.md      → v2.1 (already delivered)
  □ shared-governance-rules.md     → v2.1 (already delivered)
  □ PROJECT-1-SRS-GOVERNANCE-ENGINE.md → v2.1 patch (already delivered)
  □ DEPLOYMENT-MANIFEST.md         → update file inventory + project count
  □ MASTER-REVIEWER.md (this project) → update pipeline map (Section 2/8)

Total v2.0 amendments: 3 (structural) + 2 new engines + 2 companion
                        engine amendments + 5 file syncs
Total v2.1 amendments: 1 (AMEND-CORE-A, spanning 6 files)
Grand total (v1 + v2.0 + v2.1): 27 + 3 + 1 = 31 amendments across the ecosystem
Critical path: Priority 5 → Priority 5.5 → Priority 6 → Priority 7
(v3.0 note: P3-light + Test Generation Engine is a later structural
change layered on top of this checklist — see the v3.0 Supersession
Notice at the top of this addendum.)
```

---

*End of v2.0/v2.1 ADDENDUM*
*Append immediately before the closing lines of*
*GOVERNANCE-STABILIZATION-AMENDMENTS.md.*
*Original 27 amendments remain unmodified and fully in force.*
*4 new amendments (3 structural + 1 pipeline-relationship). 2 new*
*engines. Architecture philosophy preserved — this is a structural*
*extension (one gate, two independent tracks, one join point),*
*not a redesign.*
*v3.0 layered on top: P3 MODE 2.5 removed, test generation moved to the*
*standalone Test Generation Engine, and CHECK-4 struck from P4.1/P4.2 —*
*see the v3.0 Supersession Notice at the top of this file.*
