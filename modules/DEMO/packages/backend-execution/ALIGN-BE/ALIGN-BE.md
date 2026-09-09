<!-- source: PHASE:ALIGN-BE -->
<!-- traces: ENT-DEMO-001, REQ-DEMO-001, REQ-DEMO-002, REQ-DEMO-003, REQ-DEMO-004, REQ-DEMO-005 -->
<!-- PHASE:ALIGN-BE:START traces=ENT-DEMO-001,REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: ALIGN-BE — alignment self-check

## Error Catalog — DEMO v1
| code | RULE-* (or PLATFORM-STD + ADR) | API-* | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| DEMO_NOTE_TITLE_REQUIRED | RULE-DEMO-001 | API-DEMO-001, API-DEMO-004 | 400 | empty title on save | عنوان الملاحظة مطلوب | Note title is required |
| DEMO_NOTE_CONTENT_TOO_LONG | RULE-DEMO-002 | API-DEMO-001, API-DEMO-004 | 400 | content > 4000 chars on save | محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف) | Note content exceeds the maximum allowed length (4000 characters) |
| DEMO_NOTE_NOT_FOUND | PLATFORM-STD (ADR-DEMO-002) | API-DEMO-003, API-DEMO-004, API-DEMO-005 | 404 | id does not resolve to an active note owned by the caller | الملاحظة غير موجودة | Note not found |

Runtime code format: the `code` field of the framework's standard `ApiResponse` error envelope carries the string exactly as in the `code` column above (stated once here for api-verify).

## Security
Covered by PHASE:SEC-BE above. Review check `ERP-4` (MAJOR — every mutation endpoint declares its PERM_* requirement): API-DEMO-001 → PERM_PAGE_DEMO_NOTES_CREATE ✓; API-DEMO-004 → PERM_PAGE_DEMO_NOTES_UPDATE ✓; API-DEMO-005 → PERM_PAGE_DEMO_NOTES_DELETE ✓.

## ALIGN — DEMO v1
```
TRACEABILITY      every API-*/QR-*/RULE-*/DBF-* used in a phase appears in the Plan Index ✓ · every block carries traces= ✓ · every traces target exists upstream ✓
BINDING (§2A)     no placeholder table/column/key/generation object ✓ · no "see SRS" ✓ · every column cites a DBF ✓ · every message present in ar + en ✓ · business code format explicit (none applicable — Note has no business code) ✓
MANIFEST (§4)     only the manifest's columns ✓ · every DBF of demo_note listed ✓ · no ⏸ rows (no XM) ✓
QRC (§5)          every API with a DB operation has a QR ✓ (5/5) · every QR carries the agent-reference warning (this plan §5 header) ✓ · no join for lookup labels (no lookups) ✓ · exact generation object named (GENERATED ALWAYS AS IDENTITY) ✓
API (R3)          every RULE in Validations has a catalog row ✓ · platform errors have RULE = PLATFORM-STD + ADR ✓ (ADR-DEMO-002) · create/update exclude system fields ✓ · business code in responses — not applicable (none) ✓
CROSS-MODULE      no XM from the db-script to place ✓ · no DEFERRED row ✓ · no inbound stub requested ✓
SECURITY (R7)     every API serving SCR-REQ-DEMO-001 declares its permission ✓ · SCR_PAGES seed row present ✓ · no permission outside the SRS matrix ✓
CORE (R1)         layers declared ✓ · domain placement declared ✓ · error signalling declared ✓ · type mapping declared ✓
DECISIONS         ADR-DEMO-001 (content length), ADR-DEMO-002 (not-found handling) — both ACCEPTED, non-breaking · no BLOCKED ADR
RESULT            PASSED ✓
```

**Coverage tables**
| ENT/DBF | Phases | QR | XM |
|---|---|---|---|
| ENT-DEMO-001 / DBF-DEMO-001..008 | DATA-DOM, SVC-API, SEC-BE, ALIGN-BE | QR-DEMO-001..005 | none |

| RULE | API | Catalog code |
|---|---|---|
| RULE-DEMO-001 | API-DEMO-001, API-DEMO-004 | DEMO_NOTE_TITLE_REQUIRED |
| RULE-DEMO-002 | API-DEMO-001, API-DEMO-004 | DEMO_NOTE_CONTENT_TOO_LONG |

| XM | Status | Blocks | Workaround |
|---|---|---|---|
| none | — | — | — |
<!-- PHASE:ALIGN-BE:END -->
