## MODULE REGISTRY — DEMO (Personal Notes)
══════════════════════════════════════════════════════════════════
Module Name    : Personal Notes
Module Code    : DEMO
Layer          : L1
Type           : Transactional
Execution Tier : T1-1 (see platform-summary.md numbering "1.1")
P0 Date        : 2026-09-07
Readiness      : READY
Domain KB Pattern : N/A — GENERAL domain (domain/domain-profile.md), no
                     ERP Knowledge Base pattern library in use
                     (GOVERNANCE-CONFIG.md §2)
Source         : NEW
══════════════════════════════════════════════════════════════════

ENTITIES OWNED
──────────────────────────────────────────────────────────────────
Note           │ Transactional                        │ PRIVATE
──────────────────────────────────────────────────────────────────
Note: Names only — ENTITY-IDs assigned by P1, not here. One entity,
directly from the brief ("عنوان + محتوى" — title + content). No
sub-entities (no tags, folders, or attachments — deliberately out of
scope per the brief's "simple").

LOVs OWNED
──────────────────────────────────────────────────────────────────
NOTE_STATUS    │ Note lifecycle status │ Dropdown/LOV │ ACTIVE, DELETED
──────────────────────────────────────────────────────────────────
Note: LOV-IDs assigned by P1, not here. NOTE_STATUS backs the
soft-delete convention declared in domain/domain-profile.md's Governing
Rules ("DEMO uses soft status").

LOVs CONSUMED (from other modules)
──────────────────────────────────────────────────────────────────
(none) — no other module exists in this platform to consume an LOV from.
──────────────────────────────────────────────────────────────────

SHARED ENTITIES CONSUMED
──────────────────────────────────────────────────────────────────
(none) — DEMO consumes no SHARED entity. It does read an authenticated
owner-user identity (`ownerUserId`) from the platform's auth context,
but per domain/domain-profile.md this platform does not model identity/
auth as a governed entity of its own — see AUTO-DECISIONS below.
──────────────────────────────────────────────────────────────────

DEPENDENCIES
──────────────────────────────────────────────────────────────────
(none)         │ —       │ DEMO has no dependency on any other module
──────────────────────────────────────────────────────────────────
ROOT: YES — no external module dependencies.

AUTO-DECISIONS
──────────────────────────────────────────────────────────────────
AUTO: Note is modeled as PRIVATE, single-owner (not SHARED), consistent
      with the brief's "personal notes" framing and the domain's
      owner-based access rule.
FROM: Step 4 (Level 2 default for the declared GENERAL domain) — the
      brief does not mention sharing between users, so none is assumed.
IF WRONG: if a future version needs cross-user sharing, that is a new
      module version (IFA) — P1 would then need to decide whether
      sharing makes Note SHARED or introduces a separate join entity.

AUTO: Soft-delete (NOTE_STATUS: ACTIVE/DELETED) chosen over hard delete.
FROM: Step 4 (Level 2 default) + platform-standards.md audit-field
      convention (is_active_fl-style status is the platform default for
      "full CRUD" unless the brief asks for permanent deletion).
IF WRONG: P1 can instead specify hard DELETE if the brief is read as
      requiring physical removal — flagged for P1/reviewer attention,
      not treated as fixed here.

AUTO: `ownerUserId` (authenticated user reference) is treated as an
      existing platform-level concept, not a new entity this module
      owns or a SHARED entity it consumes formally.
FROM: Step 4 (Level 2 default) — domain/domain-profile.md Purpose
      explicitly states no module in this domain builds its own auth
      system; an authenticated user context is assumed available.
IF WRONG: if this platform later formalizes a User/Identity entity as
      SHARED, DEMO's SRS would then declare a HARD-FK/XM dependency on
      it instead of treating ownerUserId as an opaque external
      reference.
──────────────────────────────────────────────────────────────────

INF-IDs (if any — should be empty)
──────────────────────────────────────────────────────────────────
(none) — no auto-completion step failed; the brief was sufficient at
every step above.
──────────────────────────────────────────────────────────────────
══════════════════════════════════════════════════════════════════
