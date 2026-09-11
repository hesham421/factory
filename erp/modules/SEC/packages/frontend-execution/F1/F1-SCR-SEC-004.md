<!-- source: PHASE:F1 / SUB:F1-SCR-SEC-004 -->
<!-- context: F1-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-004, AC-SEC-005, AC-SEC-009, AC-SEC-010, AC-SEC-011, AC-SEC-031, API-SEC-005, API-SEC-006, API-SEC-007, API-SEC-008, API-SEC-009, API-SEC-010, API-SEC-011, REQ-SEC-004, REQ-SEC-005, REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-031, SCR-SEC-004 -->
<!-- SUB:F1-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F1 · SCR-SEC-004 — المستخدمون / Users

### F1-MODEL — ENT-SEC-001 — المستخدم / User
Source DTO   : `UserResponse` (read) · `UserCreateRequest` · `UserUpdateRequest` (write)
  userPk     : number · read-only (PK) · system-only
  username   : string · maxLength 100 — required on create, **read-only on edit**
               (`UserUpdateRequest` does not carry it — the identity is immutable after create)
  email      : string · required · maxLength 255
  fullNameAr : string · required · maxLength 200
  fullNameEn : string · required · maxLength 200
  password   : string · required on create only · maxLength 200 · write-only — never returned
  statusCode : string · read-only · lookup — USER_STATUS code held as a string (ADR-SEC-006);
               changed only by API-SEC-009 / API-SEC-010 / API-SEC-011, never by a form
  lastLoginAt: date-time · read-only · system-only
  isActiveFl : boolean · read-only — mirrors statusCode
  roles      : RoleSummaryResponse[] · read-only on this DTO — { roleId, code, nameAr, nameEn };
               written only through API-SEC-008
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — ENT-SEC-013 — طلب تسجيل معلّق / SignupRequest (pending sub-view)
Source DTO   : `SignupRequestResponse` — every property read-only here; the only input is the
               decision value APPROVE | REJECT of `SignupDecisionRequest` (pattern-constrained)
### F1-SCREEN — SCR-SEC-004
Search model : filters — username/email : string · LIKE · fullName : string · LIKE ·
               statusCode : string · EXACT (the code, from the shared lookup hook — ADR-SEC-006)
               paging + sort — page, size, sortField, sortDirection, carried inside the filter
               object per `UserSearchRequest`
Form model   : create — username, email, fullNameAr, fullNameEn, password (all required)
               edit   — email, fullNameAr, fullNameEn (required); username read-only
               excluded system fields: userPk, statusCode, lastLoginAt, isActiveFl, roles,
               audit fields
               roles are a separate model written through API-SEC-008, not a property of the
               create or update body
Container    : SIDE_DRAWER
No internal or tenant identifier is modelled; `passwordHash` is never returned by any
published endpoint and is absent here, as SRS A3 requires [POL-SEC-004].

<!-- SUB:F1-SCR-SEC-004:END -->
