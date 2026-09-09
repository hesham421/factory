<!-- source: PHASE:SEC-BE -->
<!-- traces: REQ-DEMO-001, REQ-DEMO-002, REQ-DEMO-003, REQ-DEMO-004, REQ-DEMO-005, SCR-REQ-DEMO-001 -->
<!-- PHASE:SEC-BE:START traces=SCR-REQ-DEMO-001,REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: SEC-BE — security (backend half)

**Per-screen enforcement.** SCR-REQ-DEMO-001 (Daily Notes): every serving API (API-DEMO-001..005) verifies its permission before processing (VIEW is the gateway — without it no other action applies, per `profile.conventions.security_model`).

**SEC_PAGES seed data**
| Page code | Name (ar/en) | Parent |
|---|---|---|
| PAGE_DEMO_NOTES | الملاحظات اليومية / Daily Notes | — (top-level under DEMO menu) |

**Permission seed data**
| Permission | Action | API(s) |
|---|---|---|
| PERM_PAGE_DEMO_NOTES_VIEW | VIEW (gateway) | API-DEMO-002, API-DEMO-003 |
| PERM_PAGE_DEMO_NOTES_CREATE | CREATE | API-DEMO-001 |
| PERM_PAGE_DEMO_NOTES_UPDATE | UPDATE | API-DEMO-004 |
| PERM_PAGE_DEMO_NOTES_DELETE | DELETE | API-DEMO-005 |

Role USER holds all four (SRS B4 Access — single-role module, no sharing). No permission name appears here that is absent from the SRS permission matrix (SRS B4).

**Forbidden responses.** Map through `LocalizedException → {code: FORBIDDEN, messageAr, messageEn}` — a catalog row, same envelope as every other error (§7).
<!-- PHASE:SEC-BE:END -->
