# FRONTEND TEST PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Scope : module (MDL)
Sources: srs-mdl.md v1 · frontend-execution-plan-mdl.md v1 · registry-srs-mdl.md v1 ·
         registry-exec-fe-mdl.md v1
Framework: agnostic (profile.stack.testing.frontend). REDUCED: **no** — P3.2 has run for MDL,
so every test case below binds to a real `SCR-*` and its route.
TC count: 11 — TC-MDL-015 … TC-MDL-025, continuing the module's one TC sequence after the
backend plan's highest id (TC-MDL-014). No id is renumbered and no backend TC is touched.
Open ADRs: 0 new. The plan cites ADR-MDL-005 and ADR-MDL-007 where a screen's behaviour
follows one of them.
SUPERSEDES the REDUCED stub this file previously held, which recorded that P3.2 had not run
for MDL and that no `SCR-*` existed. That is no longer true: SCR-MDL-001, SCR-MDL-002 and
UXD-MDL-001 exist.
══════════════════════════════════════════════════════════════════

Scope is `module`, so this run derives from MDL's own `AC-*` only. The integration phase
`INT-UXD` is **absent by rule**, not empty and not a gap: UXD-MDL-001 names the security
module as the owner of the displayed data, and that module is not in this selection — §2 rule
1 and §5 of the engine. An `INT-UXD` phase appears the first time this stage runs at
`--modules MDL,SEC` or `--scope project`.

<!-- PHASE:TEST-PLAN-FE:START traces=AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,AC-MDL-013,REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,REQ-MDL-013 -->
## TEST-PLAN-FE — MDL v1

Eleven test cases, so the phase splits (threshold: TC count > 8) into the two labels the
profile names: `UI-FLOWS` for the per-screen flows, and `INT-FLOW` for the one flow that
crosses screens. Every case derives from exactly one `AC-*`, cites the `SCR-*` and route it
exercises, and asserts the catalog message in both languages wherever a `RULE-*` fires.

<!-- SUB:UI-FLOWS:START traces=AC-MDL-001,REQ-MDL-001,SCR-MDL-001,API-MDL-002,AC-MDL-002,REQ-MDL-002,AC-MDL-003,REQ-MDL-003,API-MDL-003,AC-MDL-004,REQ-MDL-004,API-MDL-004,AC-MDL-005,REQ-MDL-005,API-MDL-005,AC-MDL-006,REQ-MDL-006,API-MDL-006,AC-MDL-007,REQ-MDL-007,AC-MDL-008,REQ-MDL-008,API-MDL-007,AC-MDL-009,REQ-MDL-009,API-MDL-008,AC-MDL-010,REQ-MDL-010,API-MDL-009 -->
### SUB — UI-FLOWS

Per-screen flows on SCR-MDL-001: create, the violation as the screen shows it, the edit whose immutable field is not an input, the one-way deactivation, and the reorder.

<!-- TC:TC-MDL-015:START traces=AC-MDL-001,REQ-MDL-001,SCR-MDL-001,API-MDL-002 -->
### TC-MDL-015 — create a lookup type
Derived from : AC-MDL-001 (REQ-MDL-001) · Exercises: SCR-MDL-001 /reference-data/lookups/new · API-MDL-002
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: signed in holding MDL_LOOKUPS VIEW and CREATE; the owner-module select is loaded from the security module's registry; the key is not yet used
Steps        : 1. open /reference-data/lookups 2. choose New 3. enter the key, pick the owner module from the select, fill both names 4. submit
Expected     : the type is created active and appears in the type list; its (empty) value pane opens; the owner module was chosen from the registered set, never typed
Test data    : key "PAYMENT_METHOD", owner module FIN, nameAr "طريقة الدفع", nameEn "Payment method"
<!-- TC:TC-MDL-015:END -->

<!-- TC:TC-MDL-016:START traces=AC-MDL-002,REQ-MDL-002,SCR-MDL-001,API-MDL-002 -->
### TC-MDL-016 — a type naming an unregistered owner module is refused on screen
Derived from : AC-MDL-002 (REQ-MDL-002) · Exercises: SCR-MDL-001 /reference-data/lookups/new · API-MDL-002
Rule / code  : RULE-MDL-001 → MDL-409-MODULE-NOT-REGISTERED
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: an owner module code with no ModuleRegistry row in the security module — reachable when a module is deregistered between the select loading and the submit
Steps        : 1. open the type form with the select already loaded 2. submit with that owner module
Expected     : nothing is created and the message is shown on the owner-module field — ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" · en: "The owning module is not registered in the Security module"
Test data    : a module code absent from the security module's registry
<!-- TC:TC-MDL-016:END -->

<!-- TC:TC-MDL-017:START traces=AC-MDL-003,REQ-MDL-003,SCR-MDL-001,API-MDL-003 -->
### TC-MDL-017 — editing a type changes its names and never its key
Derived from : AC-MDL-003 (REQ-MDL-003) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId/edit · API-MDL-003
Rule / code  : RULE-MDL-003
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an existing lookup type, open in the detail form
Steps        : 1. open the type's edit route 2. look for an editable key field 3. change both names 4. submit
Expected     : the key and the owner module are rendered read-only and are not inputs at all — the update request carries neither — and the form states the immutability beside the key rather than showing a disabled control with no explanation; the new names are saved and the key is unchanged
Test data    : a type whose key is already cited by a consumer
<!-- TC:TC-MDL-017:END -->

<!-- TC:TC-MDL-018:START traces=AC-MDL-004,REQ-MDL-004,SCR-MDL-001,API-MDL-004 -->
### TC-MDL-018 — deactivating a type warns that consumer reads will stop returning its values
Derived from : AC-MDL-004 (REQ-MDL-004) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId · API-MDL-004
Rule / code  : RULE-MDL-004
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active lookup type with values; signed in holding MDL_LOOKUPS VIEW and DELETE
Steps        : 1. select the type 2. choose Deactivate 3. read the confirmation 4. confirm 5. look for an Activate affordance on the row afterwards
Expected     : the confirmation names the consequence — every consuming module stops receiving this type's values — before the act; the row's state becomes inactive and the row stays in the list; **no Activate affordance is drawn**, because no endpoint exists for it, so the act is one-way from this screen
Test data    : an active type with three values
<!-- TC:TC-MDL-018:END -->

<!-- TC:TC-MDL-019:START traces=AC-MDL-005,REQ-MDL-005,SCR-MDL-001,API-MDL-005 -->
### TC-MDL-019 — selecting a type lists exactly its values in sort order
Derived from : AC-MDL-005 (REQ-MDL-005) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId · API-MDL-005
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a lookup type with three values, and another type with values of its own
Steps        : 1. open /reference-data/lookups 2. select the first type 3. read the detail pane 4. select the second type and read it
Expected     : exactly that type's three values are listed, ordered by sort order, and none of the other type's values appears; the parent id is part of the cache key, so the second selection is a different entry rather than a refetch of the first
Test data    : three values with sortOrder 1, 2, 3
<!-- TC:TC-MDL-019:END -->

<!-- TC:TC-MDL-020:START traces=AC-MDL-006,REQ-MDL-006,SCR-MDL-001,API-MDL-006 -->
### TC-MDL-020 — create a value under the selected type
Derived from : AC-MDL-006 (REQ-MDL-006) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId/values/new · API-MDL-006
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a selected lookup type and a code not yet used within it
Steps        : 1. select the type 2. choose New value 3. fill code, both names and the sort order 4. submit
Expected     : the value is created active under that type and appears in the value list at its sort position; the parent type id came from the route, never from a typed field
Test data    : code "CASH", nameAr "نقدًا", nameEn "Cash", sortOrder 1
<!-- TC:TC-MDL-020:END -->

<!-- TC:TC-MDL-021:START traces=AC-MDL-007,REQ-MDL-007,SCR-MDL-001,API-MDL-006,API-MDL-005 -->
### TC-MDL-021 — a duplicate code under the same type is refused, and the same code under another type is not
Derived from : AC-MDL-007 (REQ-MDL-007) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId/values/new · API-MDL-006
Rule / code  : RULE-MDL-002 → MDL-409-VALUE-DUP
Scenario     : VIOLATION · data class INVALID · language ALL
Preconditions: a lookup type already holding a value with code "ACTIVE", and a second type holding no such code
Steps        : 1. open the value form under the first type and enter code "ACTIVE" 2. leave the field (blur) 3. submit 4. open the value form under the SECOND type and enter code "ACTIVE" 5. submit
Expected     : the first submission creates no second row and the message is shown inline on `code` — ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" · en: "This code is already used within this type"; the second submission SUCCEEDS, because the uniqueness scope is the parent type and not the system — the blur check queries with EQUALS filters on both the type id and the code, so it has the same scope the rule has
Test data    : code "ACTIVE" under two different types
<!-- TC:TC-MDL-021:END -->

<!-- TC:TC-MDL-022:START traces=AC-MDL-008,REQ-MDL-008,SCR-MDL-001,API-MDL-007 -->
### TC-MDL-022 — editing a value changes its names and sort order, never its code
Derived from : AC-MDL-008 (REQ-MDL-008) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId/values/:valueId/edit · API-MDL-007
Rule / code  : —
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: an existing lookup value
Steps        : 1. open the value's edit route 2. look for an editable code field 3. change both names and the sort order 4. submit
Expected     : the code is rendered read-only and is not an input — `LookupValueUpdateRequest` does not carry it — and neither is the active flag; the new names and sort order are saved and the row moves to its new position
Test data    : sortOrder changed from 2 to 1
<!-- TC:TC-MDL-022:END -->

<!-- TC:TC-MDL-023:START traces=AC-MDL-009,REQ-MDL-009,SCR-MDL-001,API-MDL-008,API-MDL-005 -->
### TC-MDL-023 — deactivating a value removes it from consumer reads and leaves it visible to the manager
Derived from : AC-MDL-009 (REQ-MDL-009) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId · API-MDL-008
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: an active lookup value under a selected type
Steps        : 1. select the type 2. choose Deactivate on the value row 3. confirm 4. read the value list again
Expected     : the row's active state becomes false and **the row is still listed**, marked inactive — the manager's read returns inactive values, which is exactly what the consumer read hides; no Activate affordance is drawn, so the act is one-way from this screen
Test data    : one of three values
<!-- TC:TC-MDL-023:END -->

<!-- TC:TC-MDL-024:START traces=AC-MDL-010,REQ-MDL-010,SCR-MDL-001,API-MDL-009 -->
### TC-MDL-024 — reordering the values persists the new order for every affected row
Derived from : AC-MDL-010 (REQ-MDL-010) · Exercises: SCR-MDL-001 /reference-data/lookups/:typeId · API-MDL-009
Rule / code  : MDL-400-REORDER-MISMATCH (on a partial set)
Scenario     : HAPPY · data class VALID · language ALL
Preconditions: a type with three values at sortOrder 1, 2, 3
Steps        : 1. select the type 2. drag the third value to the first position 3. read the list the response re-renders
Expected     : the whole ordered set of value ids is submitted once — never one row's new position — and the three rows persist sortOrder 3, 1, 2 respectively; the list re-renders from the response's own order, and the sort order shown on each value's form is the one the drag produced. A partial set would answer the mismatch code, which is why the whole set is sent
Test data    : sortOrder 1,2,3 reordered to 3,1,2
<!-- TC:TC-MDL-024:END -->

<!-- SUB:UI-FLOWS:END -->

<!-- SUB:INT-FLOW:START traces=AC-MDL-013,REQ-MDL-013,SCR-MDL-002,SCR-MDL-001,API-MDL-010 -->
### SUB — INT-FLOW

The one flow that crosses screens: the registry browse and the hand-off into the screen that manages what it shows.

<!-- TC:TC-MDL-025:START traces=AC-MDL-013,REQ-MDL-013,SCR-MDL-002,SCR-MDL-001,API-MDL-010 -->
### TC-MDL-025 — browse the registry by owner and cross into the screen that manages a type
Derived from : AC-MDL-013 (REQ-MDL-013) · Exercises: SCR-MDL-002 /reference-data/type-registry → SCR-MDL-001 · API-MDL-010
Rule / code  : —
Scenario     : STATE · data class VALID · language ALL
Preconditions: lookup types owned by more than one module, and a caller holding both screens
Steps        : 1. open /reference-data/type-registry 2. read the groups 3. narrow by owner module 4. follow a type row into the manager
Expected     : the types are shown grouped under their owner-module headings, the grouping being the one the response carries rather than one composed on the client; the filter is mirrored into the route's search params, so the narrowed view is a shareable address; the type row lands on /reference-data/lookups/:typeId with that type selected, and this screen offers no create or edit of its own
Test data    : types owned by SEC and by FIN
<!-- TC:TC-MDL-025:END -->

<!-- SUB:INT-FLOW:END -->

<!-- PHASE:TEST-PLAN-FE:END -->

## TC TRACEABILITY INDEX

| AC | TC | REQ | SCR | RULE / code |
|---|---|---|---|---|
| AC-MDL-001 | TC-MDL-015 | REQ-MDL-001 | SCR-MDL-001 | — |
| AC-MDL-002 | TC-MDL-016 | REQ-MDL-002 | SCR-MDL-001 | RULE-MDL-001 → MDL-409-MODULE-NOT-REGISTERED |
| AC-MDL-003 | TC-MDL-017 | REQ-MDL-003 | SCR-MDL-001 | RULE-MDL-003 |
| AC-MDL-004 | TC-MDL-018 | REQ-MDL-004 | SCR-MDL-001 | RULE-MDL-004 |
| AC-MDL-005 | TC-MDL-019 | REQ-MDL-005 | SCR-MDL-001 | — |
| AC-MDL-006 | TC-MDL-020 | REQ-MDL-006 | SCR-MDL-001 | — |
| AC-MDL-007 | TC-MDL-021 | REQ-MDL-007 | SCR-MDL-001 | RULE-MDL-002 → MDL-409-VALUE-DUP |
| AC-MDL-008 | TC-MDL-022 | REQ-MDL-008 | SCR-MDL-001 | — |
| AC-MDL-009 | TC-MDL-023 | REQ-MDL-009 | SCR-MDL-001 | — |
| AC-MDL-010 | TC-MDL-024 | REQ-MDL-010 | SCR-MDL-001 | MDL-400-REORDER-MISMATCH (on a partial set) |
| AC-MDL-013 | TC-MDL-025 | REQ-MDL-013 | SCR-MDL-002, SCR-MDL-001 | — |

### AC covered on the backend track only — not a gap on this track

| AC | REQ | Why no frontend case |
|---|---|---|
| AC-MDL-011 | REQ-MDL-011 | the consumer read by key — API-MDL-011's caller is a consuming module's backend over the platform's in-process module interface, and no MDL screen calls it (ADR-MDL-007) |
| AC-MDL-012 | REQ-MDL-012 | the not-found answer for an unknown key — answered to that same calling module; no screen requests a key that was never registered |

## COVERAGE

AC covered on this track: 11/13 — the two above are backend-only by construction, and 13/13
across the module when both plans are read together (`backend-test-plan-mdl.md` carries one TC
per AC for all 13).
REQ covered on this track: 11/13 — the same two REQ ids, for the same reason.
SCR covered: 2/2 — SCR-MDL-001 by ten cases, SCR-MDL-002 by the drill-across case, which
touches both.
UXD covered: not derived in this run — `INT-UXD` is an integration phase and this run is
`--module MDL`; UXD-MDL-001's owner module is outside the selection.
TC count check (§3 over-engineering guard): 11 cases against 13 ACs is well under 2×, and no
case is a fabricated variant — every one derives from a distinct AC.
Scenario mix: HAPPY 6 · VIOLATION 2 · STATE 3 · PERMISSION 0 (no MDL AC states a permission
outcome — the SRS Access summary grants MDL_LOOKUPS four actions and MDL_TYPE_REGISTRY one,
and no AC asserts a denial) · BOUNDARY 0 (no AC or RULE states a numeric limit).

## NOTES

- Every message asserted above is copied character-perfect from `srs-mdl.md` §A5 in both
  languages; no message is reworded and none is composed by a test.
- Two cases assert an **absence** deliberately: TC-MDL-018 and TC-MDL-023 check that no
  Activate affordance is drawn, because no endpoint exists for one (ADR-MDL-005) and a
  half-working toggle would be the likeliest thing for an implementer to add.
- TC-MDL-021 is one case with two submissions on purpose: AC-MDL-007's rule is scoped to the
  parent type, and a test that only checked the refusal would pass against a wrongly global
  uniqueness check.
- `test-execution-manifest-mdl.md` is a derived view of the **backend** plan and its API set.
  Neither changed in this run, so it is current and is not rewritten.
══════════════════════════════════════════════════════════════════
