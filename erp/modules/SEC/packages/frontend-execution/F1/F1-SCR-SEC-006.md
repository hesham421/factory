<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-006 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-016, AC-SEC-017, AC-SEC-018, AC-SEC-019, API-SEC-018, API-SEC-019, API-SEC-020, API-SEC-021, REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019, SCR-SEC-006 -->
<!-- SUB:F1-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F1 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

### F1-MODEL — ENT-SEC-004 / ENT-SEC-005 / ENT-SEC-006 — registry tree
Source DTO   : `RegistryRowResponse` (the nested module → screens → actions shape returned by
               API-SEC-021), plus `ModuleRegistryResponse`, `ScreenRegistryResponse` and
               `ActionRegistryResponse` for the single-row shapes
  module  : moduleRegPk : number · read-only (PK) · code : string · read-only ·
            nameAr, nameEn : string · read-only · isActiveFl : boolean · read-only ·
            screens : ScreenRegistryResponse[] · audit fields read-only
  screen  : screenRegPk : number · read-only (PK) · pageCode : string · read-only ·
            moduleId : number · read-only · moduleCode : string · read-only ·
            nameAr, nameEn : string · read-only · isActiveFl : boolean · read-only ·
            actions : ActionRegistryResponse[] · audit fields read-only
  action  : actionRegPk : number · read-only (PK) ·
            permissionCode : string · read-only · system-only — derived server-side as
            `PERM_<PAGE_CODE>_<ACTION>`, never composed on the client ·
            screenId : number · read-only · pageCode : string · read-only ·
            actionCode : string · read-only · nameAr, nameEn : string · read-only ·
            isActiveFl : boolean · read-only · audit fields read-only
Read-only    : every property of all three levels — this screen writes nothing (SRS B3)
### F1-SCREEN — SCR-SEC-006
Search model : filters — module code : string · LIKE · pageCode : string · EXACT (the published
               `RegistrySearchRequest` carries `pageCode` beside the generic `filters[]`)
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : none — no create, no update and no deactivate affordance is drawn (ADR-SEC-008)
Container    : TREE_MASTER_DETAIL
The three register DTOs (`ModuleRegistryCreateRequest`, `ScreenRegistryCreateRequest`,
`ActionRegistryCreateRequest`) are modelled as read-only reference shapes so a consuming
module's integrator can see what their own onboarding call must send; this frontend never
builds one (ADR-SEC-009).

<!-- SUB:F1-SCR-SEC-006:END -->
