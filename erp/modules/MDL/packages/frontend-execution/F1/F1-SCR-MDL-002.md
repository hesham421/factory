<!-- source: PHASE:F1 / SUB:F1-SCR-MDL-002 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-010, API-MDL-011, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, SCR-MDL-002, UXD-MDL-001 -->
<!-- SUB:F1-SCR-MDL-002:START traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001,SCR-MDL-002 -->
### F1 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F1-MODEL — OwnerGroupResponse — المجموعة حسب المالك / Owner group
Source DTO   : `OwnerGroupResponse[]` (read only — this screen writes nothing)
  ownerModuleCode : string · read-only — the group key (UXD-MDL-001)
  types[]         : LookupTypeResponse — the same type model as SCR-MDL-001 above, every
                    property read-only here: lookupTypePk, key, ownerModuleCode, nameAr,
                    nameEn, isActiveFl, and the four audit fields
### F1-SCREEN — SCR-MDL-002
Search model : filters — ownerModuleCode : string · EXACT · key : string · LIKE.
               **No paging and no sort**: `LookupTypeByOwnerSearchRequest` carries `filters`
               alone, so no page or size is modelled and none belongs in this screen's cache key
Form model   : none — a read-only browse (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-MDL-003)
The response is a bare array of groups, not a `Page<T>`, and is modelled as one: reading it
through a paging envelope would invent fields the endpoint does not send.
<!-- SUB:F1-SCR-MDL-002:END -->
