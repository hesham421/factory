# REGISTRY UPDATE — SRS (P1) — DEMO v1
══════════════════════════════════════════════════════════════════
Stage       : P1 (SRS Governance Engine)
Module      : DEMO
Date        : 2026-09-07
Feature Code: DEMO-001
══════════════════════════════════════════════════════════════════

## IDs ASSIGNED THIS STAGE

| Namespace | IDs | Notes |
|---|---|---|
| ENTITY-ID | ENTITY-DEMO-001 (Note) | PRIVATE |
| RULE-ID | RULE-DEMO-001 .. RULE-DEMO-005 | see srs-demo.md A4 |
| LOV-ID | LOV-DEMO-001 (NOTE_STATUS) | 2 values: ACTIVE, DELETED |
| SCR-ID | SCR-DEMO-001 (My Notes) | PATTERN-2, Unified/Side Drawer |
| API-ID | API-DEMO-001 .. API-DEMO-005 | Create/List/GetById/Update/Delete |

## SEQUENCE STATE (for the next SRS session on this module, if any)
```
ENTITY-DEMO next seq : 002
RULE-DEMO   next seq : 006
LOV-DEMO    next seq : 002
SCR-DEMO    next seq : 002
API-DEMO    next seq : 006
```

## project-registry.md UPDATE APPLIED
```
Section 2  — Module Index          : DEMO status → IN PROGRESS (P1 done)
Section 3  — Entity Ownership      : CAND-DEMO-001 (Note) → RESOLVED to
                                      ENTITY-DEMO-001, Status: CANDIDATE →
                                      REGISTERED (owner: DEMO, PRIVATE)
Section 6  — Global XM Index       : no change (no XM candidates)
Section 9  — Event Log             : P1 row appended
Section 15 — Pipeline Status / MGI : DEMO → "P1 done → entering P2"
```

══════════════════════════════════════════════════════════════════
*End of registry-srs-demo.md*
