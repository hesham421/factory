# PRD — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module          : MDL     Version : v1
Source artifacts: platform-summary, module-registry, business-policies
Stories         : 5   Policies covered : 6/6   Deferred : 0
Status          : DRAFT — awaiting prd-approval
══════════════════════════════════════════════════════════════════

## USER STORIES

US-MDL-001
  Title          : إدارة أنواع اللوكب / Manage lookup types
  Story          : As a platform administrator, I need to create, edit and deactivate a lookup type naming its owning module, so that every coded list has one authoritative, namespaced home.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-MDL-002, POL-MDL-003
  Source         : lookup-module-plan-en.md §2-§3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-MDL-002
  Title          : إدارة قيم اللوكب عبر الشاشة العامة / Manage lookup values through the generic screen
  Story          : As a user authorized for a lookup type, I need one generic master-detail screen to pick the type and manage its values (code, bilingual labels, sort order, active flag), so that I never need a screen per list.
  Priority       : HIGH — plan names this the module's core mechanism (§3)
  Success metric : —
  Traces         : POL-MDL-004, POL-MDL-005, POL-MDL-006
  Source         : lookup-module-plan-en.md §3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-MDL-003
  Title          : قراءة القيم من أي وحدة مستهلكة / Read values from any consuming module
  Story          : As a consuming module's backend, I need to read a lookup type's active values by key, so that I never hardcode a coded value list of my own.
  Priority       : HIGH — this is the module's entire reason to exist (§2)
  Success metric : —
  Traces         : POL-MDL-001
  Source         : lookup-module-plan-en.md §2, §4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-MDL-004
  Title          : تسجيل نوع لوكب جديد كبيانات / Register a new lookup type as data
  Story          : As a consuming module's integrator, I need to register my own lookup type here as data (naming my module as owner), so that adding a new list never requires touching MDL's code.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-MDL-002, POL-MDL-003
  Source         : lookup-module-plan-en.md §4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-MDL-005
  Title          : سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner
  Story          : As a platform administrator, I need to browse lookup types grouped by their owning module, so that I can find and audit a module's reference lists at a glance.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-MDL-002
  Source         : lookup-module-plan-en.md §7 (screen inventory row 2)
  Status         : DRAFT → APPROVED (by the PRD approval gate)

## TRACEABILITY — story → policy
| US | Traces (POL) | Source |
|---|---|---|
| US-MDL-001 | POL-MDL-002, POL-MDL-003 | lookup-module-plan-en.md §2-§3 |
| US-MDL-002 | POL-MDL-004, POL-MDL-005, POL-MDL-006 | lookup-module-plan-en.md §3 |
| US-MDL-003 | POL-MDL-001 | lookup-module-plan-en.md §2, §4 |
| US-MDL-004 | POL-MDL-002, POL-MDL-003 | lookup-module-plan-en.md §4 |
| US-MDL-005 | POL-MDL-002 | lookup-module-plan-en.md §7 |
Every policy POL-MDL-001 … POL-MDL-006 appears in at least one row above.

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |
None — lookup-module-plan-en.md left no story's scope, priority or role genuinely
ambiguous; no dialogue question was required.

## DEFERRED
| US | Reason | Activation trigger |
None — every capability named in lookup-module-plan-en.md is represented by a story in
this v1 PRD.

## APPROVAL
Approved by : PENDING   Date : PENDING
Once approved, no stage may raise a question; P1 onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════
