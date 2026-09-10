## TEST EXECUTION MANIFEST — FIN v1
══════════════════════════════════════════════════════════════════
Derived from: backend-test-plan-fin.md v1 (this run) · db-script-fin.md v1 (FK/XM) ·
srs-fin.md v1 (RULE messages).
══════════════════════════════════════════════════════════════════

## DEPENDENCY ORDER (topological entity build order)
1. Dimension (no FK)
2. Account (self-FK parent only)
3. FiscalYear (no FK)
4. EventTypeRule (no FK)
5. RecurringTemplate (no FK)
6. DimensionValue (FK → Dimension)
7. AllocationRule (FK → Account)
8. FiscalPeriod (FK → FiscalYear)
9. RuleLine (FK → EventTypeRule)
10. JournalEntry (FK → FiscalYear, FiscalPeriod, self)
11. RecurringTemplateLine (FK → RecurringTemplate, Account, DimensionValue)
12. AllocationTarget (FK → AllocationRule, Account, DimensionValue)
13. JournalLine (FK → JournalEntry, Account)
14. JournalLineDimension (FK → JournalLine, Dimension, DimensionValue)

## RULE → CODE → TC
| RULE | Catalog code | TC | HTTP | API |
|---|---|---|---|---|
| RULE-FIN-001 | FIN-409-HAS-CHILDREN / FIN-409-PARENT-NOT-LEAF-ELIGIBLE | TC-FIN-002 | 409 | API-FIN-002, API-FIN-003 |
| RULE-FIN-002 | FIN-409-DIMVALUE-DUP | TC-FIN-006 | 409 | API-FIN-007 |
| RULE-FIN-003 | FIN-409-REMAINDER-COUNT | TC-FIN-009 | 409 | API-FIN-011, API-FIN-016 |
| RULE-FIN-004 | FIN-409-DUPLICATE-EVENT | TC-FIN-011 | 409 | API-FIN-020 |
| RULE-FIN-005 | FIN-404-NO-ACTIVE-RULE | TC-FIN-013 | 404 | API-FIN-020 |
| RULE-FIN-006 | FIN-409-UNBALANCED | TC-FIN-018 | 409 | API-FIN-019, 020, 014, 017 |
| RULE-FIN-007 | FIN-409-NOT-POSTABLE-ACCOUNT | TC-FIN-019 | 409 | API-FIN-019, 020, 014, 017 |
| RULE-FIN-008 | FIN-409-PERIOD-NOT-OPEN | TC-FIN-020 | 409 | API-FIN-019, 020, 014, 017 |
| RULE-FIN-009 | FIN-409-INVALID-DIMENSION | TC-FIN-021 | 409 | API-FIN-019, 020, 014, 017 |
| RULE-FIN-010 | — (success-path computation) | TC-FIN-012, TC-FIN-026 | 200 | API-FIN-020, 014, 017 |
| RULE-FIN-011 | — (success-path) | TC-FIN-028 | 201 | API-FIN-021 |
| RULE-FIN-012 | — (success-path) | TC-FIN-029 | 201 | API-FIN-021 |
| RULE-FIN-013 | FIN-409-NOT-POSTED | TC-FIN-030 | 409 | API-FIN-021 |
| RULE-FIN-014 | FIN-409-NOT-REOPENABLE | TC-FIN-035 | 409 | API-FIN-024 |
| RULE-FIN-015 | FIN-403-SOD-VIOLATION | TC-FIN-038 | 403 | API-FIN-026 |
| RULE-FIN-016 | — (enforced by omission, no route) | TC-FIN-016, TC-FIN-017 | 404/405 | API-FIN-022 |

## ENTITY CRUD CHECKLIST
| ENT | create | read | search | update | deactivate (soft) | activate |
|---|---|---|---|---|---|---|
| ENT-FIN-001 Account | ✓ (API-FIN-002) | — | ✓ (API-FIN-001) | ✓ (API-FIN-003) | ✓ (API-FIN-004) | — |
| ENT-FIN-002 Dimension | ✓ (API-FIN-006) | — | ✓ (API-FIN-005) | — | — | — |
| ENT-FIN-003 DimensionValue | ✓ (API-FIN-007) | — | ✓ (API-FIN-008) | — | — | — |
| ENT-FIN-004 JournalEntry | ✓ (API-FIN-019, 020) | ✓ (API-FIN-022) | ✓ (API-FIN-018) | — (locked, RULE-FIN-016) | — (VOID via reverse, API-FIN-021) | — |
| ENT-FIN-005 JournalLine | ✓ (with header) | ✓ (with header) | — | — | — | — |
| ENT-FIN-006 JournalLineDimension | ✓ (with line) | ✓ (with line) | — | — | — | — |
| ENT-FIN-007 FiscalYear | ✓ (API-FIN-023) | — | — | — | ✓ (statusCode=CLOSED, API-FIN-027) | — |
| ENT-FIN-008 FiscalPeriod | ✓ (with year) | — | — | ✓ (API-FIN-024/025/026, transitions) | — | ✓ (API-FIN-024, reopen) |
| ENT-FIN-009 EventTypeRule | ✓ (API-FIN-010) | — | ✓ (API-FIN-009) | — | — | — |
| ENT-FIN-010 RuleLine | ✓ (API-FIN-011) | — | — | — | — | — |
| ENT-FIN-011 RecurringTemplate | ✓ (API-FIN-013) | — | ✓ (API-FIN-012) | — | — | — |
| ENT-FIN-012 RecurringTemplateLine | ✓ (with template) | — | — | — | — | — |
| ENT-FIN-013 AllocationRule | ✓ (API-FIN-016) | — | ✓ (API-FIN-015) | — | — | — |
| ENT-FIN-014 AllocationTarget | ✓ (with rule) | — | — | — | — | — |

## CROSS-MODULE (this module's declared XM)
| XM | Target | TC | Status |
|---|---|---|---|
| XM-FIN-001 | MDL | TC-FIN-047 | ACTIVE — covered |
══════════════════════════════════════════════════════════════════
