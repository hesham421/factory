<!-- Source: PHASE:SEC-BE -->

## PHASE SEC-BE — Backend Security Specifications

### SEC-BE — SCR-DEMO-001 — ملاحظاتي (My Notes)
─────────────────────────────────────────────────────────────────
API-level enforcement:
  Every API-ID serving this screen (API-DEMO-001..005) requires
  permission verification before the request is processed — see the
  SECURITY block in each API contract in PHASE SVC+API. The substantive
  gate is record-level ownership (RULE-DEMO-003), not a role check — see
  DRV-DEMO-008.

EXCEPTION module scope: N/A — no EXCEPTION module referenced.
─────────────────────────────────────────────────────────────────

SECURITY SEED DATA REQUIREMENTS:
  Screen registration (table: SEC_PAGES, standard naming — column names
  per db-script-demo.md convention once Security itself goes through P2):
    page_code  : DEMO_NOTES
    page_name  : ملاحظاتي (My Notes) / My Notes
    parent_id_fk: DEMO_ROOT (per srs-demo.md B4 Security Seed Data note)
  Permission rows (table: PERMISSIONS):
    ────────────────────────────────────────────────────────
    Permission Name              │ Roles Assigned
    ─────────────────────────────┼──────────────────────────
    PERM_DEMO_NOTES_VIEW         │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    PERM_DEMO_NOTES_CREATE       │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    PERM_DEMO_NOTES_UPDATE       │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    PERM_DEMO_NOTES_DELETE       │ ALL AUTHENTICATED USERS (DRV-DEMO-008)
    ────────────────────────────────────────────────────────
  Note (DRV-DEMO-008): this domain has no role matrix (domain-profile.md
  — "owner-based access, not role-based"). Every authenticated user holds
  all 4 permission rows; the actual authorization boundary per request is
  RULE-DEMO-003 (record-level ownership), enforced in PHASE SVC+API — the
  permission rows above gate "is this feature reachable at all by an
  authenticated user," not "which user's records."

SEC-BE Governance Rules:
  SEC-IMPL-RULE-1 — SCR-DEMO-001 has permission verification enforced at
                    the API level (no exceptions) — see PHASE SVC+API.
  SEC-IMPL-RULE-3 — HTTP 403 responses mapped via LocalizedException,
                    carrying ERR-0003.
  SEC-IMPL-RULE-4 — SCR-DEMO-001 verified in SEC_PAGES before launch.

Note: UI-level show/hide, navigation guards (SEC-FE) belong to Project
3.2 (frontend pass, out of scope for this backend-only plan) — consumes
the SAME PERMISSIONS seed data declared above.
