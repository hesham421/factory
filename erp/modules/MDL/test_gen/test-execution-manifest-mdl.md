## TEST EXECUTION MANIFEST — MDL v1
══════════════════════════════════════════════════════════════════
Derived from: backend-test-plan-mdl.md v1 (this run) · db-script-mdl.md v1 (FK/XM) ·
srs-mdl.md v1 (RULE messages).
══════════════════════════════════════════════════════════════════

## DEPENDENCY ORDER
1. LookupType (no local FK dependency; validated against SEC's ModuleRegistry via
   XM-MDL-001, an external read, not a build-order dependency within MDL's own schema)
2. LookupValue (FK → LookupType)

## RULE → CODE → TC
| RULE | Catalog code | TC | HTTP | API |
|---|---|---|---|---|
| RULE-MDL-001 | MDL-409-MODULE-NOT-REGISTERED | TC-MDL-002 | 409 | API-MDL-002 |
| RULE-MDL-002 | MDL-409-VALUE-DUP | TC-MDL-007 | 409 | API-MDL-006 |
| RULE-MDL-003 | — (enforced by DTO shape, no error code) | TC-MDL-003 | 200 | API-MDL-003 |
| RULE-MDL-004 | MDL-404-TYPE-KEY (negative) / — (positive, exclusion) | TC-MDL-011, TC-MDL-012, TC-MDL-004 | 200 / 404 | API-MDL-011, API-MDL-004 |

## ENTITY CRUD CHECKLIST
| ENT | create | read | search | update | deactivate (soft) | activate |
|---|---|---|---|---|---|---|
| ENT-MDL-001 LookupType | ✓ (API-MDL-002) | — | ✓ (API-MDL-001, API-MDL-010) | ✓ (API-MDL-003) | ✓ (API-MDL-004) | — |
| ENT-MDL-002 LookupValue | ✓ (API-MDL-006) | ✓ (API-MDL-011) | ✓ (API-MDL-005) | ✓ (API-MDL-007, API-MDL-009 reorder) | ✓ (API-MDL-008) | — |

## CROSS-MODULE (this module's declared XM)
| XM | Target | TC | Status |
|---|---|---|---|
| XM-MDL-001 | SEC | TC-MDL-014 | ACTIVE — covered |
══════════════════════════════════════════════════════════════════
