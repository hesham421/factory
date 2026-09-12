<!-- source: PHASE:ALIGN-FE -->
<!-- traces: AC-MDL-001, AC-MDL-002, AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009, AC-MDL-010, AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-001, API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-005, API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009, API-MDL-010, API-MDL-011, REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, SCR-MDL-001, SCR-MDL-002, UXD-MDL-001 -->
<!-- PHASE:ALIGN-FE:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 6 — ALIGN-FE

The alignment self-check is this phase's content, and its `RESULT` row is written by the
orchestrator from the analyze report. Never split — level-1 only.

```
ALIGN-FE — MDL v1
row           backing check   assertion
SCREENS       orphans         both SCR-MDL-001 and SCR-MDL-002 are referenced by a plan block —
                              each has a block in F1, F2, F3 and F4 and an RF5 block in SEC-FE.
                              Every sub_bearing phase splits per screen — 8 SUB blocks, two
                              per phase — at a screen count of 2, because the count gate was
                              removed from the profile
UXD           orphans         UXD-MDL-001 is cited by a plan block — by both screens' F2
                              SCREEN-INIT blocks, by SCR-MDL-001's F3 validator for
                              RULE-MDL-001, and by both F4 Cross-module lines
TRACES        traces          every PHASE carries traces=; UXD-MDL-001 traces to its REQ and
                              its AC; every SCR traces to its REQ and to its UXD
API           traces          every API-MDL-* this plan cites is defined in the fetched
                              api-docs — through the API ID BINDING annex of ADR-MDL-001, and
                              never in the backend plan's contract table, which is the artifact
                              the three shape diffs belong to. No foreign module's API id is
                              cited here at all; the one cross-module endpoint this frontend
                              depends on is named in ui-ux-spec-mdl.md, where UXD-MDL-001 is
                              defined
FOREIGN       xref-surface    every reference to another module's surface resolves in that
                              module's own artifacts
REGISTRY      registry-agree  the UXD and both SCR defined here are in registry-exec-fe-mdl.md,
                              and nothing else is
LANGUAGES     languages       labels and messages in ar + en
MARKERS       markers         the parser reports no structural or semantic error for the
                              frontend track's exec plan
DECISIONS     refs-exist      every ADR this plan cites exists on disk in erp/decisions/MDL/ —
                              ADR-MDL-001 … ADR-MDL-007
COVERAGE      (the report)    C7.16, C7.18 and C7.20 — all three are P3.1
                              clauses over backend artifacts this stage does not write. No
                              C8.* or C9.* clause reported having examined nothing
RESULT        PASSED ✓ — 0 findings
```

### Operations coverage

| Operation | API | SCR action | Route | Status |
|---|---|---|---|---|
| search lookup types | API-MDL-001 | SCR-MDL-001 search | /reference-data/lookups | ✓ |
| create lookup type | API-MDL-002 | SCR-MDL-001 create type | /reference-data/lookups/new | ✓ |
| update lookup type | API-MDL-003 | SCR-MDL-001 edit type | /reference-data/lookups/:typeId/edit | ✓ |
| deactivate lookup type | API-MDL-004 | SCR-MDL-001 deactivate type | /reference-data/lookups/:typeId | ✓ |
| search lookup values of a type | API-MDL-005 | SCR-MDL-001 value list | /reference-data/lookups/:typeId | ✓ |
| create lookup value | API-MDL-006 | SCR-MDL-001 create value | /reference-data/lookups/:typeId/values/new | ✓ |
| update lookup value | API-MDL-007 | SCR-MDL-001 edit value | /reference-data/lookups/:typeId/values/:valueId/edit | ✓ |
| deactivate lookup value | API-MDL-008 | SCR-MDL-001 deactivate value | /reference-data/lookups/:typeId | ✓ |
| reorder lookup values | API-MDL-009 | SCR-MDL-001 drag to reorder | /reference-data/lookups/:typeId | ✓ |
| browse the registry by owner | API-MDL-010 | SCR-MDL-002 render | /reference-data/type-registry | ✓ |
| read values by key (consumer API) | API-MDL-011 | — a consuming module's backend call | — (ADR-MDL-007) | ✗ |
| activate a lookup type | — none published | SCR-MDL-001 — not drawn | — (ADR-MDL-005) | ✗ |
| activate a lookup value | — none published | SCR-MDL-001 — not drawn | — (ADR-MDL-005) | ✗ |
| read one type / one value by id | — none published | hydrated from the search cache | — (ADR-MDL-005) | ✗ |

Eleven rows carry a published endpoint; ten of those carry a route and a ✓. Four rows carry a
✗ with the ADR that explains it — one endpoint published for a caller that is not this frontend
(ADR-MDL-007), and three operations with no endpoint at all (ADR-MDL-005). No row is a ✗ for
want of a decision.

<!-- PHASE:ALIGN-FE:END -->
