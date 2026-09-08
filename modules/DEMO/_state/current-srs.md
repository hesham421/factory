# SRS — Daily Notes / Demo (DEMO)
══════════════════════════════════════════════════════════════════
Module : DEMO   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-08)
Counts : ENT 1 · REQ 5 · AC 10 · RULE 2 · SCR-REQ 1 · ADR 1
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |
|---|---|
| Module | DEMO — Daily Notes / Demo |
| Feature code | DEMO |
| Version | v1 |
| Date | 2026-09-08 |
| Status | DRAFT |
| Prepared by | P1 — SRS engine (analysis lane) |
| Decisions applied | 1 (ADR-DEMO-001) |

## A2 — Functional context
**In scope (داخل النطاق):** إدارة ملاحظة يومية واحدة (Note) بعمليات الإنشاء،
العرض/البحث، التعديل، والحذف (الحذف الناعم) فقط — وفق قصص المستخدم
US-DEMO-001..004 المعتمدة.

**Out of scope (خارج النطاق):** المشاركة أو دفاتر متعددة المستخدمين، سير عمل
الموافقات، أي تكامل مع وحدة أخرى (لا XM)، عرض تقويمي/تجميع حسب اليوم
(مؤجّل — PRD DEFERRED).

**Module function (وظيفة الوحدة):** واجهة CRUD بسيطة تتيح للمستخدم كتابة
ملاحظة (عنوان + نص حر) وحفظها، ثم استعراض قائمة ملاحظاته، فتح إحداها،
تعديلها، أو حذفها.

**Detailed description (وصف تفصيلي):** لا يوجد سير عمل أو حالات اعتماد؛
المستخدم هو نفسه مالك الملاحظة من الإنشاء حتى الحذف. لا توجد أدوار متعددة
تتفاعل مع نفس الملاحظة.

**Current situation:** لا يوجد نظام سابق لهذه الوحدة — DEMO أداة اختبار
جديدة بالكامل لخط الإنتاج (domain-profile §1–§2).

**Current difficulties:** لا ينطبق (وحدة جديدة).

**Proposed system and benefits:** واجهة CRUD صغيرة تتحقق من أن كل مرحلة من
خط الإنتاج الحوكمي (P1 حتى التسليم) تعمل بشكل صحيح قبل استخدامه على وحدة
أعمال حقيقية.

**General notes (constraints, deferred items):** لا اعتماديات بين وحدات
(XM) في هذا الإصدار (project-registry — Cross-module dependency index:
"None yet"). العناصر المؤجَّلة: العرض التقويمي، المشاركة متعددة المستخدمين
(prd-demo.md — DEFERRED).

## A3 — Entities and fields

**Standard fields per kind (profile):** الكيان الوحيد في هذه الوحدة يستخدم
النوع المحلي الخاص بـ DEMO فقط `simple` (استثناء موثّق في domain-profile §5
و module-registry-demo.md AUTO-DECISIONS) — وليس `master`/`transactional`/
`lookup`/`config`/`security`. حقوله القياسية: حقول التدقيق الأربعة
(`createdBy, createdAt, updatedBy, updatedAt`) + علم الحذف الناعم
(`isActiveFl`) من `[KB:erp-domain-standards §2.1, §6]`. لا حقول اسم ثنائية
اللغة (`nameAr`/`nameEn`) لأن عنوان الملاحظة نص حر من المستخدم وليس بيانات
مرجعية (domain-profile §5).

### ENT-DEMO-001 — Note (ملاحظة يومية)
| Kind | Ownership | Business number (yes/no) | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| simple (DEMO-only exception) | PRIVATE | no — not used outside the system, not a numbered transactional document, no story asks for a human-readable reference (§3.3 test, all three "no") | create, search/list, read, update, deactivate (soft delete) | none | project-registry CAND-DEMO-001; module-registry-demo.md ENTITIES OWNED |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| notePk | reference (PK) | yes (system) | system-generated | primary key, per `profile.stack.db.naming` (`{entity}Pk`) | معرّف الملاحظة | Note ID |
| title | text | yes | user input, max length per RULE-DEMO-002 pattern (title itself has no separate length rule; DEFAULT: bounded by the platform's standard short-text column) | free text, not bilingual name data | عنوان الملاحظة | Title |
| content | text | yes | user input, max 4000 chars (RULE-DEMO-002, ADR-DEMO-001) | free text | محتوى الملاحظة | Content |
| isActiveFl | flag | yes (system) | true / false, default true | soft-delete flag, `[KB:erp-domain-standards §6]` DEFAULT | نشِط | Active |
| createdBy | reference | yes (system) | current user id | system-filled, never accepted from client | أنشئ بواسطة | Created by |
| createdAt | date-time | yes (system) | server timestamp, UTC | system-filled | تاريخ الإنشاء | Created at |
| updatedBy | reference | yes (system) | current user id | system-filled | عُدّل بواسطة | Updated by |
| updatedAt | date-time | yes (system) | server timestamp, UTC | system-filled; bumped on every update | تاريخ التعديل | Updated at |

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-DEMO-001 — Create a note
Pattern    : event
Statement  : When a user submits a new note with a title and content, the system shall create a note record owned by that user.
Traces     : US-DEMO-001
Entities   : ENT-DEMO-001
Rationale  : direct expression of the create-a-note need.
Source     : prd-demo.md US-DEMO-001
Priority   : HIGH

#### AC-DEMO-001 — [REQ-DEMO-001] happy path
Given  : the create-note form is open and the user has entered a non-empty title and content within the allowed length
When   : the user submits the form
Then   : the system creates the note, sets `isActiveFl = true`, `createdBy`/`createdAt` to the current user/time, and shows it in the notes list — ar: "تم إنشاء الملاحظة" · en: "Note created"

#### AC-DEMO-002 — [REQ-DEMO-001, RULE-DEMO-001] empty title
Given  : the create-note form is open
When   : the user submits with an empty title
Then   : the system rejects the save and shows the RULE-DEMO-001 message — ar: "عنوان الملاحظة مطلوب" · en: "Note title is required"

#### AC-DEMO-003 — [REQ-DEMO-001, RULE-DEMO-002] content too long
Given  : the create-note form is open
When   : the user submits content longer than 4000 characters
Then   : the system rejects the save and shows the RULE-DEMO-002 message — ar: "محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف)" · en: "Note content exceeds the maximum allowed length (4000 characters)"

### REQ-DEMO-002 — List the user's notes
Pattern    : ubiquitous
Statement  : The system shall display the current user's notes, ordered by last-updated time, newest first.
Traces     : US-DEMO-002
Entities   : ENT-DEMO-001
Rationale  : direct expression of "see a list of my notes".
Source     : prd-demo.md US-DEMO-002
Priority   : HIGH

#### AC-DEMO-004 — [REQ-DEMO-002] notes exist
Given  : the current user owns one or more active notes
When   : the user opens the Daily Notes screen
Then   : the system shows each note's title and last-updated date, most recently updated first

#### AC-DEMO-005 — [REQ-DEMO-002] no notes
Given  : the current user owns no active notes
When   : the user opens the Daily Notes screen
Then   : the system shows an empty-state message — ar: "لا توجد ملاحظات بعد" · en: "No notes yet"

### REQ-DEMO-003 — View a note's full content
Pattern    : event
Statement  : When a user selects a note from the list, the system shall display that note's full title and content.
Traces     : US-DEMO-002
Entities   : ENT-DEMO-001
Rationale  : "open one to read its full content" from US-DEMO-002.
Source     : prd-demo.md US-DEMO-002
Priority   : HIGH

#### AC-DEMO-006 — [REQ-DEMO-003] happy path
Given  : the user is on the Daily Notes list and owns an active note
When   : the user selects that note
Then   : the system displays its full title and content

### REQ-DEMO-004 — Edit a note
Pattern    : event
Statement  : When a user submits changed title or content for an existing note, the system shall save the changes and update the note's last-updated time.
Traces     : US-DEMO-003
Entities   : ENT-DEMO-001
Rationale  : direct expression of the edit need.
Source     : prd-demo.md US-DEMO-003
Priority   : MEDIUM

#### AC-DEMO-007 — [REQ-DEMO-004] happy path
Given  : the user has an existing active note open for editing with a valid non-empty title and content within the allowed length
When   : the user submits the change
Then   : the system saves the new title/content, sets `updatedBy`/`updatedAt` to the current user/time, and shows the updated note — ar: "تم حفظ التعديلات" · en: "Changes saved"

#### AC-DEMO-008 — [REQ-DEMO-004, RULE-DEMO-001] empty title
Given  : the user has an existing note open for editing
When   : the user submits with an empty title
Then   : the system rejects the save and shows the RULE-DEMO-001 message (AC-DEMO-002 wording)

#### AC-DEMO-009 — [REQ-DEMO-004, RULE-DEMO-002] content too long
Given  : the user has an existing note open for editing
When   : the user submits content longer than 4000 characters
Then   : the system rejects the save and shows the RULE-DEMO-002 message (AC-DEMO-003 wording)

### REQ-DEMO-005 — Delete (deactivate) a note
Pattern    : event
Statement  : When a user requests to delete one of their notes, the system shall deactivate that note (soft delete) and remove it from the notes list.
Traces     : US-DEMO-004
Entities   : ENT-DEMO-001
Rationale  : direct expression of the delete need; soft delete per `[KB:erp-domain-standards §6]` DEFAULT.
Source     : prd-demo.md US-DEMO-004; `[KB:erp-domain-standards §6]`
Priority   : MEDIUM

#### AC-DEMO-010 — [REQ-DEMO-005] happy path
Given  : the user owns an active note
When   : the user confirms deletion of that note
Then   : the system sets `isActiveFl = false` on the note and the note no longer appears in the notes list — ar: "تم حذف الملاحظة" · en: "Note deleted"

## A5 — Business rules

### RULE-DEMO-001 — Note title is required
Scope      : ENT-DEMO-001
Trigger    : on create / on update
Statement  : The system shall reject a save when the note's title is empty.
Message    : ar: "عنوان الملاحظة مطلوب" · en: "Note title is required"
Traces     : REQ-DEMO-001, REQ-DEMO-004
Source     : DEFAULT — a required primary field is standard CRUD practice for a user-facing record; no field in this module can be meaningfully identified in a list (REQ-DEMO-002) without one.
Test-Hint  : reject on empty/whitespace-only title, both on create and on update.

### RULE-DEMO-002 — Note content maximum length
Scope      : ENT-DEMO-001
Trigger    : on create / on update
Statement  : The system shall reject a save when the note's content exceeds 4000 characters.
Message    : ar: "محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف)" · en: "Note content exceeds the maximum allowed length (4000 characters)"
Traces     : REQ-DEMO-001, REQ-DEMO-004
Source     : ADR-DEMO-001 (no input states a bound; DEFAULT set by ADR, non-breaking).
Test-Hint  : boundary at exactly 4000 (accept) and 4001 (reject) characters.

## A6 — Lookups
لا يوجد — لا تمتلك DEMO أي قائمة قيم (lookup)؛ لا حقل في ENT-DEMO-001 يستند
إلى lookup. / None — DEMO owns no lookup; no field of ENT-DEMO-001 is
lookup-backed.

## A7 — Status lifecycle
لا ينطبق — الكيان يحمل علم حذف ناعم (`isActiveFl`) بحالتين فقط (نشِط /
غير نشِط)، وهو ≤ 2 حالة فلا يستدعي مخطط دورة حياة. / Not applicable —
`isActiveFl` is a 2-state flag, not a status lifecycle (§6 rule: diagram
required only for > 2 transitions).

## A8 — Module dependencies
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate |
|---|---|---|---|---|
| none | — | — | — | — |

| External service | Purpose | Integration kind |
|---|---|---|
| none | — | — |

DEMO ذات اعتمادية صفرية على وحدات أخرى، بما يطابق project-registry
(Cross-module dependency index: "None yet") و domain-profile §6/§8 (قرار 3).

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-DEMO-001 — الملاحظات اليومية / Daily Notes

### B1 — Definition
Purpose      : يتيح للمستخدم إدارة ملاحظاته اليومية بالكامل (بحث/عرض، إنشاء، تعديل، حذف) من مكان واحد.
Entities     : ENT-DEMO-001
Operations   : search, list, create, read, update, deactivate
Users        : USER (كل مستخدم مصادَق عليه يدير ملاحظاته الخاصة فقط)
Navigation   : DEMO → Daily Notes (menu) → screen; from: main menu; to: — (leaf screen)
Content shape: flat record
Traces       : REQ-DEMO-001, REQ-DEMO-002, REQ-DEMO-003, REQ-DEMO-004, REQ-DEMO-005
Composite    : Search + Entry as ONE screen requirement (profile.conventions.composite_screen)

### B2 — Search / list
Filter: title (نص، يحتوي على) — يطابق عمود النتيجة "العنوان".
Result columns: title (العنوان), updatedAt (تاريخ آخر تعديل) — مطابقة لـ REQ-DEMO-002.
لا قوائم قيم (lookup) في الفلاتر — A6 فارغ.

### B3 — Input
Fields (تشير إلى ENT-DEMO-001): title (نص، مطلوب — RULE-DEMO-001)، content (نص طويل، مطلوب، حد أقصى 4000 حرف — RULE-DEMO-002).
Buttons/actions: Save → create (REQ-DEMO-001) أو update (REQ-DEMO-004) حسب السياق؛ Delete → deactivate (REQ-DEMO-005)؛ Cancel → إغلاق بدون حفظ.

### B4 — Access
Page code : PAGE_DEMO_NOTES (SEC_PAGES)
| Role | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|
| USER | ✓ | ✓ | ✓ | ✓ |
Gateway: VIEW مطلوب قبل أي إجراء آخر (profile.conventions.security_model). لا صلاحيات إضافية أو أدوار أخرى — كل مستخدم يدير ملاحظاته فقط (لا مشاركة، domain-profile §7.1).

### B5 — API expectations
Base path : /api/v1/demo/notes
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| create note | POST | /api/v1/demo/notes | title, content | Note | RULE-DEMO-001, RULE-DEMO-002 | REQ-DEMO-001 |
| search notes | GET | /api/v1/demo/notes | title filter, paging | Page\<Note\> | — | REQ-DEMO-002 |
| read note | GET | /api/v1/demo/notes/{id} | id | Note | — | REQ-DEMO-003 |
| update note | PUT | /api/v1/demo/notes/{id} | title, content | Note | RULE-DEMO-001, RULE-DEMO-002 | REQ-DEMO-004 |
| deactivate note | DELETE | /api/v1/demo/notes/{id} | id | confirmation | — | REQ-DEMO-005 |

# STANDALONE

## Traceability matrix
| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-DEMO-001 | REQ-DEMO-001 | AC-DEMO-001, AC-DEMO-002, AC-DEMO-003 | RULE-DEMO-001, RULE-DEMO-002 | ENT-DEMO-001 | SCR-REQ-DEMO-001 |
| US-DEMO-002 | REQ-DEMO-002, REQ-DEMO-003 | AC-DEMO-004, AC-DEMO-005, AC-DEMO-006 | — | ENT-DEMO-001 | SCR-REQ-DEMO-001 |
| US-DEMO-003 | REQ-DEMO-004 | AC-DEMO-007, AC-DEMO-008, AC-DEMO-009 | RULE-DEMO-001, RULE-DEMO-002 | ENT-DEMO-001 | SCR-REQ-DEMO-001 |
| US-DEMO-004 | REQ-DEMO-005 | AC-DEMO-010 | — | ENT-DEMO-001 | SCR-REQ-DEMO-001 |

## Decisions applied
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| DEFAULT | soft delete via `isActiveFl` instead of hard delete | `[KB:erp-domain-standards §6]` | override: none requested |
| DEFAULT | audit fields (`createdBy/At`, `updatedBy/At`) on Note | `[KB:erp-domain-standards §6]` | override: none requested |
| DEFAULT | Note has no business/document number | §3.3 NUMBERING test (all three conditions "no") | override: none requested |
| ADR-DEMO-001 | maximum content length = 4000 characters | `decisions/DEMO/ADR-DEMO-001.md` | status: ACCEPTED (non-breaking) |

## Access summary
| Page code | Screen | Role | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|---|---|
| PAGE_DEMO_NOTES | Daily Notes / الملاحظات اليومية | USER | ✓ | ✓ | ✓ | ✓ |
══════════════════════════════════════════════════════════════════
