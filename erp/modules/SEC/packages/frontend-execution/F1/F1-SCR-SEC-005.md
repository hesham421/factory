<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-005 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-020, AC-SEC-030, API-SEC-012, API-SEC-013, API-SEC-014, API-SEC-015, API-SEC-016, API-SEC-017, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-020, REQ-SEC-030, SCR-SEC-005 -->
<!-- SUB:F1-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F1 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F1-MODEL — ENT-SEC-002 — الدور / Role
Source DTO   : `RoleResponse` (read) · `RoleCreateRequest` (write)
  rolePk        : number · read-only (PK) · system-only
  code          : string · required on create · maxLength 50 — the stable machine reference;
                  read-only once created
  nameAr        : string · required · maxLength 150
  nameEn        : string · required · maxLength 150
  descriptionAr : string · optional · maxLength 500
  descriptionEn : string · optional · maxLength 500
  isActiveFl    : boolean · read-only
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — grant tree nodes (read-only projections of ENT-SEC-004/005/006)
Source DTO   : `RegistryRowResponse` — module { moduleRegPk, code, nameAr, nameEn, isActiveFl,
               screens[] }, screen { screenRegPk, pageCode, moduleId, moduleCode, nameAr,
               nameEn, isActiveFl, actions[] }, action { actionRegPk, permissionCode, screenId,
               pageCode, actionCode, nameAr, nameEn, isActiveFl }
               every property read-only — the tree displays the registry, it does not edit it
### F1-MODEL — grant rows (ENT-SEC-007/008/009)
Source DTO   : `RoleModuleGrantResponse` { roleModuleGrantPk, roleId, moduleId, grantedBy,
               grantedAt } · `RoleScreenGrantResponse` { roleScreenGrantPk, roleId, screenId,
               grantedBy, grantedAt } · `RoleActionGrantResponse` { roleActionGrantPk, roleId,
               actionId, grantedBy, grantedAt } · `ModuleGrantRevokeResponse`
               { revokedScreenGrants, revokedActionGrants }
               every property read-only — a grant is created or revoked by identifier, never
               edited field by field
### F1-SCREEN — SCR-SEC-005
Search model : filters — code/name : string · LIKE (the published `RoleSearchRequest` carries a
               `name` field beside the generic `filters[]`) · isActiveFl : boolean · EXACT
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : create — code, nameAr, nameEn (required); descriptionAr, descriptionEn (optional)
               edit   — not modelled: no role-update endpoint is published (ADR-SEC-008)
               excluded system fields: rolePk, isActiveFl, audit fields
Container    : TREE_MASTER_DETAIL
The tree holds selection state only. Which nodes are granted is derived from the grant rows the
server returns, never from a local mirror that could outlive a revoke.

<!-- SUB:F1-SCR-SEC-005:END -->
