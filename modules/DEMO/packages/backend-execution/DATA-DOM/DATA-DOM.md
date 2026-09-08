<!-- source: PHASE:DATA-DOM -->
<!-- traces: ENT-DEMO-001, REQ-DEMO-001, REQ-DEMO-002, REQ-DEMO-003, REQ-DEMO-004, REQ-DEMO-005 -->
<!-- PHASE:DATA-DOM:START traces=ENT-DEMO-001,REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: DATA-DOM — data + domain

No SUB split (single entity, well under any split threshold).

### ENT-DEMO-001 — Note      kind: simple (DEMO-only exception, see domain-profile §5)
BINDINGS   table demo_note · PK note_pk (DBF-DEMO-001) · PK generation `GENERATED ALWAYS AS IDENTITY` · db-script v1
BUSINESS CODE none — not applicable (§3.3 test, all "no"; db-script has no business-code column)
DEFAULT FIELDS  simple-kind exception fields only (domain-profile §5, module-registry-demo.md AUTO-DECISIONS): audit fields + `is_active_fl`; no `nameAr`/`nameEn`, no `docNo`/`statusCode`/fiscal fields — this entity is neither `master` nor `transactional`.
FIELDS
| DBF | property | column | type (postgresql16) | null | read-only | constraint | label ar/en |
|---|---|---|---|---|---|---|---|
| DBF-DEMO-001 | id | note_pk | GENERATED ALWAYS AS IDENTITY | NOT NULL | yes | PK_DEMO_NOTE | معرّف الملاحظة / Note ID |
| DBF-DEMO-002 | title | title | VARCHAR(200) | NOT NULL | no | CHK_DEMO_NOTE_TITLE | عنوان الملاحظة / Title |
| DBF-DEMO-003 | content | content | TEXT | NOT NULL | no | CHK_DEMO_NOTE_CONTENT_LEN | محتوى الملاحظة / Content |
| DBF-DEMO-004 | activeFl | is_active_fl | BOOLEAN | NOT NULL | no (system-flipped only) | — | نشِط / Active |
| DBF-DEMO-005 | createdBy | created_by | VARCHAR(100) | NOT NULL | yes | — | أنشئ بواسطة / Created by |
| DBF-DEMO-006 | createdAt | created_at | TIMESTAMPTZ | NOT NULL | yes | — | تاريخ الإنشاء / Created at |
| DBF-DEMO-007 | updatedBy | updated_by | VARCHAR(100) | NOT NULL | yes | — | عُدّل بواسطة / Updated by |
| DBF-DEMO-008 | updatedAt | updated_at | TIMESTAMPTZ | NOT NULL | yes | — | تاريخ التعديل / Updated at |

DTO MEMBERSHIP  create-request: title, content (excludes id, activeFl, audit fields) · update-request: title, content (excludes id, activeFl, audit fields) · response: id, title, content, activeFl, createdAt, updatedAt (audit "By" fields excluded from response DTO — internal only)
LOOKUP FIELDS  none
DOMAIN RULES
  RULE-DEMO-001 — trigger: on create/update — statement: "The system shall reject a save when the note's title is empty." — message ar: "عنوان الملاحظة مطلوب" · en: "Note title is required" — scope: CREATE|UPDATE — DB enforcement: CHK_DEMO_NOTE_TITLE — owner layer: domain entity (pure invariant) + DB constraint as backstop
  RULE-DEMO-002 — trigger: on create/update — statement: "The system shall reject a save when the note's content exceeds 4000 characters." — message ar: "محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف)" · en: "Note content exceeds the maximum allowed length (4000 characters)" — scope: CREATE|UPDATE — DB enforcement: CHK_DEMO_NOTE_CONTENT_LEN — owner layer: domain entity (pure invariant) + DB constraint as backstop
STATE MACHINE  not applicable — `activeFl` is a 2-state flag, not a status lifecycle (SRS A7).
CROSS-MODULE   none.
REPOSITORY OPS → QR-DEMO-001 (SAVE), QR-DEMO-002 (FIND_BY_CRITERIA), QR-DEMO-003 (FIND_ONE), QR-DEMO-004 (UPDATE), QR-DEMO-005 (UPDATE flag flip)
<!-- PHASE:DATA-DOM:END -->
