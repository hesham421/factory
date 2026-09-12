<!-- source: PHASE:F1 / SUB:F1-SCR-FIN-002 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-004, AC-FIN-005, AC-FIN-006, API-FIN-005, API-FIN-006, API-FIN-007, API-FIN-008, API-FIN-035, REQ-FIN-004, REQ-FIN-005, REQ-FIN-006, SCR-FIN-002 -->
<!-- SUB:F1-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F1 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F1-MODEL — ENT-FIN-002 — البُعد / Dimension
Source DTO   : `DimensionResponse` (read) · `DimensionCreateRequest` (write)
  dimensionPk : number · read-only (PK) · system-only
  code        : string · required on create · maxLength 30
  nameAr      : string · required on create · maxLength 150
  nameEn      : string · required on create · maxLength 150
  isActiveFl  : boolean · read-only — and never written at all: no endpoint sets it on the
                parent dimension (SRS §B4, ADR-FIN-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-003 — قيمة البُعد / DimensionValue
Source DTO   : `DimensionValueResponse` (read) · `DimensionValueCreateRequest` (write)
  dimensionValuePk : number · read-only (PK) · system-only
  dimensionId      : number · read-only on the form — it is the path id of API-FIN-007, taken
                     from the selected parent, never typed
  code             : string · required on create · maxLength 30 — unique within the dimension
  nameAr           : string · required on create · maxLength 150
  nameEn           : string · required on create · maxLength 150
  sortOrder        : number · required on create
  isActiveFl       : boolean · read-only — flipped only by API-FIN-035
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-SCREEN — SCR-FIN-002
Search model : dimension filters — code : string · LIKE
               value filters — code : string · LIKE · dimensionId : number · EXACT (set from
               the selected parent, not typed)
               paging + sort inside each of `DimensionSearchRequest` and
               `DimensionValueSearchRequest`
Form model   : dimension — code, nameAr, nameEn (all required, create only)
               value — code, nameAr, nameEn, sortOrder (all required, create only)
               excluded system fields: both PKs, both isActiveFl, the audit fields
               read-only on edit: not applicable — neither resource has an update endpoint
Container    : TREE_MASTER_DETAIL
No enum is modelled: this screen defines the values other screens' dimension selects read, and
holds no lookup code of its own.

<!-- SUB:F1-SCR-FIN-002:END -->
