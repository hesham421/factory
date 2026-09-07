# ERP GOVERNANCE — STABILIZATION AMENDMENTS (BASE RECORD)
## The Original Hardening Pass — Reconstructed

```
Document Type  : Stabilization Patch Record — BASE FILE
Status         : RECONSTRUCTED, 2026-09-02 — see Reconstruction Notice
                 below before relying on any entry's exact wording
Scope          : Project 1 (SRS), Project 2 (Database), Project 3
                 (Execution Plan — pre-split), Project 4 (Audit —
                 pre-split)
Companion file : GOVERNANCE-STABILIZATION-AMENDMENTS-v2-ADDENDUM.md
                 (append this file, then that one, when loading into
                 P4.1/P4.2 — see that file's own header)
```

---

═══════════════════════════════════════════════════════════════════
# RECONSTRUCTION NOTICE — READ BEFORE USING THIS FILE
═══════════════════════════════════════════════════════════════════

**This file does not exist anywhere in the ecosystem's delivered
files, uploaded documents, or session history.** It was referenced by
name in 8 separate places (P4.1/P4.2 project instructions, the
engine-instruction-files-map.md and START-HERE.md overview files,
DEPLOYMENT-MANIFEST.md, PROJECT-3-FRONTEND-ENGINE.md, and inside the
v2.0/v2.1 ADDENDUM itself) as something every audit engine loads — but
no copy of it, past or present, was ever found. The user confirmed
they do not have a copy either, and asked for it to be reconstructed.

**What this reconstruction is built from** — real, verifiable evidence
already present in the currently-shipped files, not invented history:

```
HIGH CONFIDENCE  — an in-file changelog block that names the amendment
                   ID and its exact target section explicitly
                   (PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md is the only
                   file with one; its 8 entries below are reconstructed
                   directly from it)
MEDIUM CONFIDENCE— the amendment ID is referenced by name with a target
                   file/section, but no changelog states the original
                   before/after — reconstructed by describing the real,
                   current mechanism at that location and presenting it
                   as this amendment's effect
GROUPED          — the amendment ID appears ONLY inside a same-priority
                   grouping in DEPLOYMENT-MANIFEST.md's application
                   checklist (e.g. "AMEND-P3-B/C/E/F/G/I"), with no
                   other trace anywhere — reconstructed from the
                   grouping's stated theme plus the real current
                   content of the area it plausibly covers
UNRECOVERABLE    — the ID is referenced but nothing else about it
                   survives anywhere; listed as a placeholder only
```

**A second, separate finding surfaced while reconstructing this file:**
`AMEND-P3-M`, `AMEND-P3-N`, and `AMEND-P3-O` are real, heavily-evidenced
amendments — cited with full effect descriptions across
STAGE-2-GOVERNANCE-TOOLS-2.md, PROJECT-3-REGISTRY-2.md,
PROJECT-3-BACKEND-ENGINE.md, PROJECT-3-FRONTEND-ENGINE.md,
UI-UX-DESIGN-ENGINE.md, and PROJECT-1-SRS-GOVERNANCE-ENGINE.md — but
they appear in **none** of the amendment-count summaries anywhere
(DEPLOYMENT-MANIFEST's "31 amendments", the ADDENDUM's "27 + 3 + 1 =
31" arithmetic). They are documented in this file's final section
(Section 5) on the strength of that direct evidence, separately from
the reconstructed-from-inference entries above. **The "31 total
amendments" figure quoted elsewhere in the ecosystem is stale — it
should read at least 34 once M/N/O are folded in.** This file does not
silently correct those other counts; that is flagged to the user
separately.

`AMEND-MAP-A` through `AMEND-MAP-D` are referenced once, as a range
boundary ("AMEND-P1-A through AMEND-MAP-D"), with no other trace of
their content anywhere in the ecosystem. They are listed in Section 4
as placeholders only — reconstructing their content would be pure
invention, which this file avoids throughout.

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — PRIORITY 1: STRUCTURAL FOUNDATIONS
═══════════════════════════════════════════════════════════════════

---

## AMEND-P1-A / AMEND-P2-A / AMEND-P3-A / AMEND-P4-A
**Confidence:** HIGH (P2-A confirmed by in-file changelog; P1-A/P3-A/
P4-A reconstructed as the same change applied identically to the other
three engines, per SHARED-GOVERNANCE-CORE.md's own "LOADING
INSTRUCTION FOR ALL PROJECTS")
**Resolves:** Each engine needed a single, canonical, version-locked
copy of the shared vocabulary and Drive-automation rules embedded at
the top of its own instructions, rather than re-deriving or
paraphrasing them per project.
**Target:** SHARED-GOVERNANCE-CORE.md header, embedded in full at the
top of PROJECT-1-SRS-GOVERNANCE-ENGINE.md, PROJECT-2-DATABASE-
GOVERNANCE-ENGINE.md, PROJECT-3 (pre-split), and PROJECT-4 (pre-split)
**Type:** Structural — one-time embed, still in force

```
Every governance engine embeds SHARED-GOVERNANCE-CORE.md IN FULL in
its system prompt, before its own project-specific content — not by
reference, not paraphrased. All engines load the same version; a
version mismatch across engines is a GOVERNANCE EXCEPTION (see that
file's own header, "LOADING INSTRUCTION FOR ALL PROJECTS").
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — PRIORITY 2: XM-ID FORMAT (ALL OR NOTHING)
═══════════════════════════════════════════════════════════════════

---

## AMEND-P2-B
**Confidence:** HIGH (in-file changelog)
**Target:** PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md — Section 5.1
**Type:** New ID format
**Effect:** Establishes the XM-ID format and lifecycle: `XM-[MOD]-[N]`,
always module-qualified, never a bare `XM-[N]` — the identifier for
every cross-module dependency the Database Engine declares.

## AMEND-P2-C
**Confidence:** HIGH (in-file changelog)
**Target:** PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md — Section 5.2
**Type:** New artifact format
**Effect:** Establishes the XM Register format, including the
SOFT-READ dependency category alongside HARD-FK, in the DB Script's
output.

## AMEND-P2-E
**Confidence:** HIGH (in-file changelog)
**Target:** PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md — Section 5.3
**Type:** New comment convention
**Effect:** Establishes the deferred-FK comment format, always citing
the qualified XM-[MOD]-[N] ID rather than a bare table/column note.

## AMEND-P2-F
**Confidence:** HIGH (in-file changelog)
**Target:** PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md — Section 6
**Type:** Classification extension
**Effect:** Adds the SOFT-READ category to FK classification, alongside
the existing HARD-FK category.

## AMEND-P3-D / AMEND-P3-H
**Confidence:** MEDIUM (reconstructed from current INT-C/INT-R phase
content and the XM Execution Register in PROJECT-3-BACKEND-ENGINE.md
— no changelog states which of the two IDs covers which half)
**Target:** PROJECT-3 (pre-split) — the INT-C (Integration Contract)
and INT-R (Integration Runtime/Register) phases, and the INT Summary
(XM Execution Register) that gates ALIGN
**Type:** New phase content + new gate condition
**Effect:** Requires every XM-[MOD]-[N] ID received from the DB Script
to appear in the plan's INT Summary before the ALIGN gate can pass;
requires DEFERRED XM dependencies to carry a documented unblock
condition and workaround, never a bare "TODO: XM-[MOD]-[N]" placeholder.
This content now lives, split, across PROJECT-3-BACKEND-ENGINE.md's
INT-C/INT-R phases and ALIGN-BE table (PASS 1 only — see AMEND-P3-K in
the v2.0/v2.1 ADDENDUM for why PASS 2/Frontend never touches XM-ID).

## AMEND-P4-C
**Confidence:** MEDIUM (reconstructed from PROJECT-4-BACKEND-AUDIT.md
CHECK-5.1/5.2, which match this amendment's evident purpose exactly)
**Target:** PROJECT-4 (pre-split) — the audit CHECK covering XM-ID
completeness
**Type:** New CHECK
**Effect:** Establishes what is now CHECK-5 (XM Completeness): all
XM-[MOD]-[N] IDs from the DB Script's XM Register must appear in the
execution plan's INT Summary (5.1); all DEFERRED XM IDs must carry
documented unblock conditions and workarounds (5.2); any unqualified
placeholder in place of a real XM-ID is a DRIFT finding, MAJOR
severity.

---

═══════════════════════════════════════════════════════════════════
# SECTION 3 — PRIORITY 3: NEW GOVERNANCE MECHANISMS
═══════════════════════════════════════════════════════════════════

---

## AMEND-P2-D
**Confidence:** HIGH (in-file changelog)
**Target:** PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md — Section 5.4
**Type:** New dependency-handling mechanism
**Effect:** Establishes SOFT-READ dependency handling — a cross-module
read that does not require a hard foreign key, distinct from a
HARD-FK dependency, with its own resolution path.

## AMEND-P2-G
**Confidence:** HIGH (in-file changelog)
**Target:** PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md — Section 2.3
**Type:** Protocol expansion
**Effect:** Expands the GOVERNANCE RECOVERY PROTOCOL — the mechanism
by which a session recovers from an incomplete or interrupted prior
run without silently dropping context.

## AMEND-P1-B / AMEND-P1-C
**Confidence:** GROUPED (no independent trace beyond the Priority-3
grouping alongside P2-D and P2-G; description below is the most
defensible inference from what P1 actually owns and what a "new
governance mechanism" pairing with SOFT-READ + Recovery Protocol would
plausibly mean for the SRS Engine specifically)
**Target:** PROJECT-1-SRS-GOVERNANCE-ENGINE.md
**Type:** New governance mechanism (two related additions)
**Effect (best-evidence reconstruction — verify against P1's current
content if precision matters):** P1's own continuation/recovery
mechanism (paralleling P2-G) for resuming an interrupted SRS session
without silently dropping prior RULE-ID/ENTITY-ID context; and a
formal Open Question (OQ-ID) escalation mechanism for flagging an
ambiguity in scope for human resolution rather than the engine
silently deciding it. **If the original intent differs from this
description, this entry should be corrected — it is the reconstructor's
best inference, not a recovered original.**

---

═══════════════════════════════════════════════════════════════════
# SECTION 4 — PRIORITY 4: EXECUTION DETERMINISM
═══════════════════════════════════════════════════════════════════

---

## AMEND-P3-B
**Confidence:** GROUPED (Priority-4 grouping; "B2 determinism" per the
ADDENDUM's own retrospective summary at its line 24-26)
**Target:** PROJECT-3 (pre-split) — Phase B2 (SVC+API — backend service
and API specification)
**Type:** Determinism rule
**Effect (reconstructed from current B2/SVC+API content in
PROJECT-3-BACKEND-ENGINE.md):** Requires every backend API endpoint
specification to be fully deterministic — exact request/response
shapes, exact error codes tied to ERR-IDs, no "TBD" or placeholder
left for implementation time to resolve.

## AMEND-P3-C
**Confidence:** MEDIUM (PROJECT-3-FRONTEND-ENGINE.md explicitly marks
this ID "SUPERSEDES AMEND-P3-C" at its Section 8.8, confirming P3-C
originally governed F2 — Frontend Data & Facade Hook Specifications)
**Target:** PROJECT-3 (pre-split) — Phase F2 (Frontend Data & Facade
Hook Specifications)
**Type:** Determinism rule
**Status:** SUPERSEDED — PROJECT-3-FRONTEND-ENGINE.md Section 8.8 is
now the canonical source for F2 determinism rules. Any reference to
AMEND-P3-C should point to that section instead, per that file's own
explicit note (line 578-579).

## AMEND-P3-E / AMEND-P3-F / AMEND-P3-G / AMEND-P3-I
**Confidence:** GROUPED (Priority-4 grouping only; no independent
trace of what distinguishes these four from B/C beyond "B2/F2
determinism work" as a category)
**Target:** PROJECT-3 (pre-split) — remaining B2/F2-adjacent phases
(plausibly: CORE, DATA+DOM, DOC, and the ALIGN gate's own determinism
checks)
**Type:** Determinism rules (exact scope of each individual letter not
independently recoverable)
**Note:** These four IDs could not be distinguished from one another
with any confidence — no evidence anywhere ties a specific one to a
specific phase. They are listed here as a placeholder group only, so
the ID range is not silently dropped from the record. If precision on
any one of E/F/G/I matters, treat it as open until independently
confirmed.

## AMEND-P4-B / AMEND-P4-D
**Confidence:** GROUPED (Priority-4 grouping only)
**Target:** PROJECT-4 (pre-split) — the CHECKs verifying B2/F2
determinism was actually followed in a submitted execution plan
**Type:** New CHECKs (exact scope of B vs D not independently
recoverable)
**Note:** Same caveat as P3-E/F/G/I above — listed to preserve the ID
range, not independently distinguishable from current evidence.

---

═══════════════════════════════════════════════════════════════════
# SECTION 5 — UNACCOUNTED-FOR AMENDMENTS FOUND DURING RECONSTRUCTION
═══════════════════════════════════════════════════════════════════

These three IDs are NOT part of the "27 original" grouping in
DEPLOYMENT-MANIFEST.md or the ADDENDUM's "27 + 3 + 1 = 31" arithmetic
anywhere — but they are real, heavily evidenced, and clearly already
in force across the shipped files. They belong in the permanent record
regardless of which historical count they were meant to sit inside.

---

## AMEND-P3-M
**Confidence:** HIGH (extensively documented in-place across multiple
files, with explicit before/after content)
**Target:** STAGE-2-GOVERNANCE-TOOLS-2.md (Section 3A, new validation
mode; multiple RESOLVED tool-boundary fixes), PROJECT-3-REGISTRY-2.md
("TRAILING CONTENT" boundary rule, applies to all four P3 files),
PROJECT-3-BACKEND-ENGINE.md, PROJECT-3-FRONTEND-ENGINE.md
**Type:** Tooling + structural-output hardening
**Effect:** Every generated phase is wrapped already-complete, never
left for a later pass to close; adds STEP 0.5/0.5B (runs immediately
after backend/frontend-execution-plan.md generation); adds a
mandatory STRUCTURAL SELF-CHECK before either plan can be declared
complete; fixes multiple splitter-tool boundary bugs (marker regex,
folder mapping, allowed-parents list) so the actual Python tooling in
STAGE-2-GOVERNANCE-TOOLS-2.md matches this rule.

## AMEND-P3-N
**Confidence:** HIGH (explicit bug description in PROJECT-3-REGISTRY-2.md
and cross-referenced consistently elsewhere)
**Target:** PROJECT-3-REGISTRY.md Section 5.7.5, PROJECT-3-BACKEND-
ENGINE.md, PROJECT-3-FRONTEND-ENGINE.md
**Type:** Bug fix
**Effect:** Fixes a global SUB-marker-ID collision — SUB marker IDs
across phases must be distinct, never the same bare `SUB:{MODULE}`
token repeated; a repeated bare token is now a structural defect that
fails validation.

## AMEND-P3-O
**Confidence:** HIGH (explicit "mandatory, applies to..." language in
PROJECT-3-FRONTEND-ENGINE.md, cross-referenced in UI-UX-DESIGN-
ENGINE.md and PROJECT-1-SRS-GOVERNANCE-ENGINE.md, including an
explicit Arabic note there calling it "a substantive change to the
standard, not just a rename")
**Target:** PROJECT-3-FRONTEND-ENGINE.md (F1 — Create/Edit Container
Pattern Decision), UI-UX-DESIGN-ENGINE.md, PROJECT-1-SRS-GOVERNANCE-
ENGINE.md screen-pattern tables
**Type:** Standard change (not a rename — a behavioral change)
**Effect:** Establishes the Container Pattern decision rules replacing
the old "P3 Implication" field: FULL_PAGE is mandatory for the
patterns it governs (not optional), editing goes through a SIDE_DRAWER
by choice rather than navigation, and TREE_MASTER_DETAIL is reserved
for its own specific case — with one documented exception noted at
PROJECT-1-SRS-GOVERNANCE-ENGINE.md line 928 for a named special screen
type.

---

═══════════════════════════════════════════════════════════════════
# SECTION 6 — UNRECOVERABLE PLACEHOLDERS
═══════════════════════════════════════════════════════════════════

```
AMEND-MAP-A, AMEND-MAP-B, AMEND-MAP-C, AMEND-MAP-D
  Confidence : UNRECOVERABLE
  Evidence   : Referenced exactly once, as a range boundary
               ("AMEND-P1-A through AMEND-MAP-D above") in the
               v2.0/v2.1 ADDENDUM's own header — implying they were
               the last four entries of this base file, plausibly
               governing project-files-map.md / engine-instruction-
               files-map.md (the two "-map" reference files in this
               ecosystem), but nothing about their actual content
               survives anywhere.
  Action     : Left as an explicit gap rather than invented content.
               If their subject matter is remembered or recovered,
               fill this section in directly — do not infer it from
               the current map files' content, since those files have
               changed substantially since (13 → 14 projects, this
               session's own edits) and would not reflect what these
               amendments originally changed.
```

---

*End of GOVERNANCE-STABILIZATION-AMENDMENTS.md (RECONSTRUCTED)*
*This file replaces a genuinely lost original. Every entry above states*
*its own confidence level — read that before treating any entry as a*
*precise historical record rather than a defensible reconstruction.*
*Section 5 (AMEND-P3-M/N/O) is real and current regardless of*
*reconstruction status; the "31 total amendments" figure quoted*
*elsewhere in this ecosystem does not yet include it.*
