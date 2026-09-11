<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-010 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-021, AC-SEC-032, AC-SEC-033, API-SEC-027, REQ-SEC-021, REQ-SEC-032, REQ-SEC-033, SCR-SEC-010 -->
<!-- SUB:F1-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F1 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F1-MODEL — effective menu (read-only projection of ENT-SEC-004 / ENT-SEC-005)
Source DTO   : `ModuleMenuResponse[]` — a bare array, **not** a `Page<T>` (this endpoint does
               not page, and the model must not assume the pagination envelope)
  moduleRegPk : number · read-only (PK) · system-only
  code        : string · read-only — the module code
  nameAr      : string · read-only
  nameEn      : string · read-only
  screens     : ScreenMenuResponse[] · read-only —
                { screenRegPk : number, pageCode : string, nameAr : string, nameEn : string }
Read-only    : every property — the menu is derived from the caller's effective grants and is
               never composed, extended or reordered on the client
### F1-SCREEN — SCR-SEC-010
Search model : none
Form model   : none
Container    : none — a global shell component with no route of its own (ADR-SEC-007)
Exactly two tiers are modelled, because the endpoint returns exactly two (REQ-SEC-021). The
`pageCode` set of this response is also the module's screen-level permission model: it is what
every route guard reads (ADR-SEC-005), so it is modelled once here and consumed by F4, never
duplicated as a static route table.

<!-- SUB:F1-SCR-SEC-010:END -->
