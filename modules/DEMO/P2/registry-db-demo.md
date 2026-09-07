# REGISTRY — P2 (Database) — DEMO v1
══════════════════════════════════════════════════════════════════
Stage      : P2 — Database Governance Engine
Module     : DEMO
Date       : 2026-09-07
Source     : db-script-demo.md
══════════════════════════════════════════════════════════════════

## DBS-ID assigned
DBS-DEMO-01

## Tables created
| Table | DBS-ID | ENTITY-ID |
|---|---|---|
| DEMO_NOTE | DBS-DEMO-01 | ENTITY-DEMO-001 |

## DBF-IDs assigned (9)
DBF-0001 .. DBF-0009 — see db-script-demo.md Traceability Matrix.

## XM-IDs assigned
None.

## Lookups
None created — NOTE_STATUS implemented as a DB CHECK constraint
(CHK_DEMO_NOTE_STATUS_ID), not a MD_MASTER_LOOKUP/MD_LOOKUP_DETAIL row.
MD_MASTER_LOOKUP/MD_LOOKUP_DETAIL remain uncreated in this platform —
DEMO is not the "first module that needs them" (it doesn't).

## Sequence state (for continuation / IFA vN≥2)
```
DBF-        next = 0010
DBS-DEMO-   next = 02
XM-DEMO-    next = 001 (none used yet)
```

## project-registry.md update applied
- New Section 5 (Table Registry) added: DEMO_NOTE row.
- Section 9 (Event Log): P2 row appended.
- Section 15 (Pipeline Status/MGI): DEMO status → "P2 done → entering P2.5".
══════════════════════════════════════════════════════════════════
