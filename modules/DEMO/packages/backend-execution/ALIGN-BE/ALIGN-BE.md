<!-- Source: PHASE:ALIGN-BE -->

## ALIGN-BE GATE — DEMO — PLAN-ID: PLAN-DEMO-001
═══════════════════════════════════════════════════════════════════════════

TRACEABILITY CHECKS                                        │ Status
───────────────────────────────────────────────────────────┼──────────────
All FIELD-IDs used in phases appear in Plan Index          │ ✓
All API-IDs used in phases appear in Plan Index            │ ✓
All RULE-IDs used in phases appear in Plan Index           │ ✓
All ERR-IDs used in Error Catalog appear correctly         │ ✓
All QR-IDs in QRC appear in Plan Index QRC Summary         │ ✓
Derivation Log complete — no undocumented inferences       │ ✓ (DRV-DEMO-001..009)
DB Structural Alignment confirms field coverage            │ ✓ (see DB Alignment Manifest)
───────────────────────────────────────────────────────────┼──────────────
BUSINESS CODE CHECKS (backend half)                        │ Status
───────────────────────────────────────────────────────────┼──────────────
Business Code excluded from POST/PUT request bodies        │ ✓ N/A — no Business Code on this entity (DRV-DEMO-003)
Business Code always present in GET/response DTOs          │ ✓ N/A — same reason
───────────────────────────────────────────────────────────┼──────────────
LOCALIZATION CHECKS (backend half)                         │ Status
───────────────────────────────────────────────────────────┼──────────────
All RULE-IDs have Message-AR defined                       │ ✓
All API error responses: messageAr + messageEn             │ ✓
───────────────────────────────────────────────────────────┼──────────────
SECURITY CHECKS (backend half)                              │ Status
───────────────────────────────────────────────────────────┼──────────────
Every API-ID serving a screen has permission declared      │ ✓
Every SCR-ID has SEC-BE block                               │ ✓
───────────────────────────────────────────────────────────┼──────────────
QUERY REFERENCE CATALOG CHECKS                              │ Status
───────────────────────────────────────────────────────────┼──────────────
Every API-ID with DB operation has QR-ID in QRC              │ ✓
Every QR-ID has agent-reference warning label                 │ ✓
No QR entry references ENUM for LOV fields                    │ ✓
No QR entry joins to lookups table                             │ ✓
Every QR-ID states exact sequence name (not placeholder)      │ ✓
───────────────────────────────────────────────────────────┼──────────────
CROSS-MODULE DEPENDENCY CHECKS                               │ Status
───────────────────────────────────────────────────────────┼──────────────
All DEFERRED items (⏸) have XM-DEMO-[N] + workarounds        │ ✓ N/A — none exist
All OQ references point to valid OQ-IDs in OQ Log             │ ✓ N/A — no OQ raised
Inbound XM stubs use INBOUND-STUB notation (not TODO)         │ ✓ N/A — no inbound stub
───────────────────────────────────────────────────────────┼──────────────
ARTIFACT BINDING CHECKS (Section 2A compliance)               │ Status
───────────────────────────────────────────────────────────┼──────────────
No placeholder [TABLE_NAME] in any phase                      │ ✓
No placeholder [LOOKUP_CODE] in any phase                     │ ✓
No placeholder [SEQ_NAME] — all sequences are exact            │ ✓
No RULE block shows "see SRS" — all text is inline             │ ✓
Every LOV-ID has exact LOOKUP_CODE bound from SRS               │ ✓
Every sequence name matches SEQ_[TABLE] from db-script          │ ✓
Every column name traces to a DBF-ID in DB Traceability        │ ✓
Every Message-AR is exact text — not paraphrase or summary     │ ✓
Business Code format stated explicitly (not "auto-gen")        │ ✓ N/A — not applied
DB Alignment Manifest: 5 columns only — no Column Name, DB Type,│ ✓
  or SRS Source (CONTRACT-1 compliance)                        │
───────────────────────────────────────────────────────────┼──────────────
PLAN COMPLETENESS CHECKS (backend)                            │ Status
───────────────────────────────────────────────────────────┼──────────────
Canonical architecture declared in PHASE CORE                  │ ✓
Domain behavior placement declared in PHASE CORE               │ ✓
Entity inheritance declared per module type                    │ ✓
No orgUnitId in any DTO described in the plan                  │ ✓
No audit fields in any CreateRequest/UpdateRequest              │ ✓
Error signaling strategy declared (LocalizedException)          │ ✓
All ERR-IDs have 4-registration points declared                │ ✓ (see PHASE CORE "Error catalog: every ERR-ID registered in 4 places")
All search operations declare ALLOWED_SORT_FIELDS               │ ✓
Empty search result → HTTP 200 declared (not HTTP 404)          │ ✓
Pre-deactivation usage check declared per deactivate op          │ ✓ N/A — this module has no deactivate-with-usage-check op (DELETE is unconditional soft delete, not a "canDelete" usage check per srs-demo.md — no other entity references a Note)
Inbound XM stubs use INBOUND-STUB notation (not TODO)            │ ✓ N/A
═══════════════════════════════════════════════════════════════════════════
ALIGN-BE GATE RESULT: PASSED ✓
Auto-correction applied: None
═══════════════════════════════════════════════════════════════════════════

**Table 1 — Entity & Field Coverage:**
```
ENTITY-ID / FIELD-ID │ DATA+DOM │ SVC+API │ QR-ID        │ XM-ID │ Status
─────────────────────┼──────────┼─────────┼──────────────┼───────┼───────
ENTITY-DEMO-001      │ ✓        │ ✓       │ QR-DEMO-0001..0005 │ —  │ ✓
FIELD-0001..0009     │ ✓        │ ✓       │ —            │ —     │ ✓
```

**Table 2 — Validations Coverage:**
```
RULE-ID        │ SVC+API │ ERR-ID   │ Status
────────────────┼─────────┼──────────┼───────
RULE-DEMO-001  │ ✓       │ ERR-0001 │ ✓
RULE-DEMO-002  │ ✓       │ ERR-0002 │ ✓
RULE-DEMO-003  │ ✓       │ ERR-0003 │ ✓
RULE-DEMO-004  │ ✓       │ — (success message, not an error) │ ✓
RULE-DEMO-005  │ ✓       │ ERR-0005 │ ✓
```

**Table 3 — XM Dependency Gate:** N/A — no XM-ID exists for this module.
