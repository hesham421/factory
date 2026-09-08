# PRD — Daily Notes / Demo (DEMO)
══════════════════════════════════════════════════════════════════
Module          : DEMO     Version : v1
Source artifacts: platform-summary, module-registry, business-policies
Stories         : 4   Policies covered : 0/0   Deferred : 2
Status          : DRAFT — awaiting prd-approval
══════════════════════════════════════════════════════════════════

## USER STORIES

US-DEMO-001
  Title          : إنشاء ملاحظة يومية / Create a daily note
  Story          : As a user (كمستخدم), I need to create a new note with a title and free-text content, so that I can capture a daily thought before I forget it.
  Priority       : HIGH
  Success metric : —
  Traces         : — (scope only)
  Source         : module-registry-demo.md — ENTITIES OWNED (Note); platform-summary.md OVERVIEW ("ملاحظات يومية بعمليات CRUD فقط")
  Status         : DRAFT

US-DEMO-002
  Title          : عرض الملاحظات / View my notes
  Story          : As a user (كمستخدم), I need to see a list of my notes and open one to read its full content, so that I can find and re-read something I wrote earlier.
  Priority       : HIGH
  Success metric : —
  Traces         : — (scope only)
  Source         : module-registry-demo.md — ENTITIES OWNED (Note); domain-profile §7.1 (Note term definition)
  Status         : DRAFT

US-DEMO-003
  Title          : تعديل ملاحظة / Edit a note
  Story          : As a user (كمستخدم), I need to change the title or content of a note I already created, so that I can fix a mistake or add to what I wrote.
  Priority       : MEDIUM
  Success metric : —
  Traces         : — (scope only)
  Source         : module-registry-demo.md — ENTITIES OWNED (Note)
  Status         : DRAFT

US-DEMO-004
  Title          : حذف ملاحظة / Delete a note
  Story          : As a user (كمستخدم), I need to remove a note I no longer want, so that my notes list only shows what is still relevant to me.
  Priority       : MEDIUM
  Success metric : —
  Traces         : — (scope only)
  Source         : module-registry-demo.md — ENTITIES OWNED (Note); `[KB:erp-domain-standards §6]` (soft delete default)
  Status         : DRAFT

## TRACEABILITY — story → policy
| US | Traces (POL) | Source |
|---|---|---|
| US-DEMO-001..004 | — (no POL exists for DEMO — business-policies-demo.md confirms "None — standard domain rules apply") | business-policies-demo.md CLIENT-SPECIFIC POLICIES |

No policy of this module is untraced: the module owns zero `POL` records, so
the completeness rule ("every policy traced by a story") is satisfied
vacuously — there is nothing to trace.

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Is a single "manage my notes" story enough, or should create/view/edit/delete be separate stories? | Separate stories (US-DEMO-001..004) — each is a distinct user need with its own priority and traceability, and it keeps P1's later requirement-splitting simple (one story ≈ one CRUD capability) for what is meant to be the simplest possible pipeline-test case. | Recommended answer stands (implied — matches the literal "just CRUD" framing; no objection). | domain-profile §2, §8 row 1; platform-summary OVERVIEW |
| 2 | Does "daily" in "daily notes" imply a per-day grouping/calendar view as a distinct capability? | No — "daily" describes the use pattern (a note taken on any given day), not a calendar/grouping feature; no such story is written. Recorded as DEFERRED rather than silently dropped. | Confirmed (no objection to the recommended reading). | domain-profile §7.1 (Daily Notes term) |

## DEFERRED
| US | Reason | Activation trigger |
|---|---|---|
| Calendar / per-day grouping view of notes | "daily" read as usage pattern, not a requested grouping feature (RESOLVED DECISIONS #2) | user explicitly asks for a calendar or date-grouped view in a future version |
| Sharing / multi-user notes | out of scope per business-policies-demo.md SCOPE EXCEPTIONS | user explicitly asks for multi-user/sharing in a future version |

## APPROVAL
Approved by : —   Date : —
Once approved, no stage may raise a question; P1 onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════
