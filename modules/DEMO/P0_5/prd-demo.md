# PRD — Personal Notes (DEMO)
══════════════════════════════════════════════════════════════════
Module          : Personal Notes (DEMO prefix)
Source artifacts: platform-summary.md, module-registry-demo.md,
                  business-policies-demo.md
Status          : DRAFT — awaiting Reconciliation Gate (Project 2.5)
══════════════════════════════════════════════════════════════════

## USER STORIES

US-DEMO-001
  Story    : As the owner of my notes, I need to create a new note with
             a title and content, so that I can capture something I
             want to remember.
  Priority : —
  Success metric : —
  Source   : module-registry-demo.md — ENTITIES OWNED ("Note ...
             Transactional ... PRIVATE")
  Status   : DRAFT

US-DEMO-002
  Story    : As the owner of my notes, I need to see a list of my
             notes, so that I can find the one I'm looking for.
  Priority : —
  Success metric : —
  Source   : module-registry-demo.md — ENTITIES OWNED (Note) + LOVs
             OWNED (NOTE_STATUS: ACTIVE/DELETED implies a default
             "active notes" list view)
  Status   : DRAFT

US-DEMO-003
  Story    : As the owner of my notes, I need to open a single note and
             read its full title and content, so that I can review what
             I wrote.
  Priority : —
  Success metric : —
  Source   : module-registry-demo.md — ENTITIES OWNED (Note)
  Status   : DRAFT

US-DEMO-004
  Story    : As the owner of my notes, I need to edit an existing
             note's title and/or content, so that I can correct or
             update it.
  Priority : —
  Success metric : —
  Source   : module-registry-demo.md — ENTITIES OWNED (Note); brief
             requires "CRUD كامل" (full CRUD)
  Status   : DRAFT

US-DEMO-005
  Story    : As the owner of my notes, I need to delete a note I no
             longer want, so that my note list stays relevant to me.
  Priority : —
  Success metric : —
  Source   : module-registry-demo.md — ENTITIES OWNED (Note) +
             AUTO-DECISIONS (soft-delete via NOTE_STATUS); brief
             requires "CRUD كامل" (full CRUD)
  Status   : DRAFT

## OPEN ITEMS (ambiguous, not yet a story)

  ? Sharing a note with another user — business-policies-demo.md SCOPE
    EXCEPTIONS notes this as an analyst boundary call (out of scope),
    not something the user stated either way. Not written as a story;
    flagged here rather than silently assumed permanently out of
    reach — a future module version could revisit it.

══════════════════════════════════════════════════════════════════
*End of prd-demo.md*
*Next stage: Project 2.5 (UI/UX Design Engine) — requires this file
 AND srs-demo.md together (CONTRACT-11). Does not gate Project 1.*
══════════════════════════════════════════════════════════════════
