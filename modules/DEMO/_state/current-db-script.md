# DATABASE — Daily Notes / Demo (DEMO)
══════════════════════════════════════════════════════════════════
Module     : DEMO   Version : v1   Dialect : postgresql16
Schema prefix : none — objects unqualified (S-7)
Identifier transformation : SRS logical field (camelCase) → physical column
  (snake_case): each uppercase letter is lower-cased and preceded by `_`
  (e.g. `notePk` → `note_pk`, `isActiveFl` → `is_active_fl`).
Date       : 2026-09-08
Counts     : 1 table · 8 DBF · 0 XM
══════════════════════════════════════════════════════════════════

## DB FIELD TRACEABILITY MATRIX — DEMO v1
| DBF id | Table | Column | Type (postgresql16) | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|---|
| DBF-DEMO-001 | demo_note | note_pk | GENERATED ALWAYS AS IDENTITY | ENT-DEMO-001.notePk | REQ-DEMO-001 | NOT NULL | identity |
| DBF-DEMO-002 | demo_note | title | VARCHAR(200) | ENT-DEMO-001.title | REQ-DEMO-001, REQ-DEMO-004 | NOT NULL | — |
| DBF-DEMO-003 | demo_note | content | TEXT | ENT-DEMO-001.content | REQ-DEMO-001, REQ-DEMO-004 | NOT NULL | — |
| DBF-DEMO-004 | demo_note | is_active_fl | BOOLEAN | ENT-DEMO-001.isActiveFl | REQ-DEMO-005 | NOT NULL | TRUE |
| DBF-DEMO-005 | demo_note | created_by | VARCHAR(100) | ENT-DEMO-001.createdBy | REQ-DEMO-001 | NOT NULL | — |
| DBF-DEMO-006 | demo_note | created_at | TIMESTAMPTZ | ENT-DEMO-001.createdAt | REQ-DEMO-001 | NOT NULL | now() |
| DBF-DEMO-007 | demo_note | updated_by | VARCHAR(100) | ENT-DEMO-001.updatedBy | REQ-DEMO-004 | NOT NULL | — |
| DBF-DEMO-008 | demo_note | updated_at | TIMESTAMPTZ | ENT-DEMO-001.updatedAt | REQ-DEMO-004 | NOT NULL | now() |

Total: 8 DBF ids across 1 table.

Column length note: `title` is bounded at VARCHAR(200) — a DEFAULT (no SRS
value stated; standard short-text column bound, see DECISIONS APPLIED),
distinct from RULE-DEMO-002's 4000-character bound on `content` (ADR-DEMO-001).

### DBF field definitions (canonical — the matrix above is a summary view)

### DBF-DEMO-001 — note_pk
  Table    : demo_note
  Column   : note_pk
  Type     : GENERATED ALWAYS AS IDENTITY
  Traces   : ENT-DEMO-001, REQ-DEMO-001
  Nullable : NOT NULL
  Default  : identity

### DBF-DEMO-002 — title
  Table    : demo_note
  Column   : title
  Type     : VARCHAR(200)
  Traces   : ENT-DEMO-001, REQ-DEMO-001, REQ-DEMO-004
  Nullable : NOT NULL
  Default  : —

### DBF-DEMO-003 — content
  Table    : demo_note
  Column   : content
  Type     : TEXT
  Traces   : ENT-DEMO-001, REQ-DEMO-001, REQ-DEMO-004
  Nullable : NOT NULL
  Default  : —

### DBF-DEMO-004 — is_active_fl
  Table    : demo_note
  Column   : is_active_fl
  Type     : BOOLEAN
  Traces   : ENT-DEMO-001, REQ-DEMO-005
  Nullable : NOT NULL
  Default  : TRUE

### DBF-DEMO-005 — created_by
  Table    : demo_note
  Column   : created_by
  Type     : VARCHAR(100)
  Traces   : ENT-DEMO-001, REQ-DEMO-001
  Nullable : NOT NULL
  Default  : —

### DBF-DEMO-006 — created_at
  Table    : demo_note
  Column   : created_at
  Type     : TIMESTAMPTZ
  Traces   : ENT-DEMO-001, REQ-DEMO-001
  Nullable : NOT NULL
  Default  : now()

### DBF-DEMO-007 — updated_by
  Table    : demo_note
  Column   : updated_by
  Type     : VARCHAR(100)
  Traces   : ENT-DEMO-001, REQ-DEMO-004
  Nullable : NOT NULL
  Default  : —

### DBF-DEMO-008 — updated_at
  Table    : demo_note
  Column   : updated_at
  Type     : TIMESTAMPTZ
  Traces   : ENT-DEMO-001, REQ-DEMO-004
  Nullable : NOT NULL
  Default  : now()

## XM REGISTER — DEMO v1
None — DEMO declares no cross-module dependency (SRS A8: empty;
project-registry Cross-module dependency index: "None yet"; domain-profile
§8 decision 3, confirmed).

## FULL_DATABASE_SCRIPT

```sql
-- ════════════════════════════════════════════════════════════════
-- DEMO v1 — Daily Notes — PostgreSQL 16
-- Identifier transformation: camelCase (SRS) -> snake_case (this script)
-- No schema prefix. No cross-module (XM) dependency in this version.
-- ════════════════════════════════════════════════════════════════

-- BLOCK 1: SEQUENCES
-- none — note_pk uses GENERATED ALWAYS AS IDENTITY (profile.stack.db.syntax_map: identity)

-- BLOCK 2: PARENT TABLES
-- none — demo_note has no FK dependency; it is its own parent

-- BLOCK 3: CHILD TABLES
CREATE TABLE demo_note (
    note_pk      INTEGER GENERATED ALWAYS AS IDENTITY,
    title        VARCHAR(200) NOT NULL,
    content      TEXT NOT NULL,
    is_active_fl BOOLEAN NOT NULL DEFAULT TRUE,
    created_by   VARCHAR(100) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by   VARCHAR(100) NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- BLOCK 4: COMMENTS
COMMENT ON TABLE demo_note IS 'ENT-DEMO-001 Note (daily note) — DEMO pipeline-test module, simple kind exception';
COMMENT ON COLUMN demo_note.note_pk IS 'DBF-DEMO-001 — primary key';
COMMENT ON COLUMN demo_note.title IS 'DBF-DEMO-002 — required title (RULE-DEMO-001)';
COMMENT ON COLUMN demo_note.content IS 'DBF-DEMO-003 — required free-text content, max 4000 chars (RULE-DEMO-002, ADR-DEMO-001)';
COMMENT ON COLUMN demo_note.is_active_fl IS 'DBF-DEMO-004 — soft-delete flag (REQ-DEMO-005)';
COMMENT ON COLUMN demo_note.created_by IS 'DBF-DEMO-005 — audit: creator principal';
COMMENT ON COLUMN demo_note.created_at IS 'DBF-DEMO-006 — audit: creation timestamp (UTC)';
COMMENT ON COLUMN demo_note.updated_by IS 'DBF-DEMO-007 — audit: last updater principal';
COMMENT ON COLUMN demo_note.updated_at IS 'DBF-DEMO-008 — audit: last update timestamp (UTC)';

-- BLOCK 5: CONSTRAINTS
-- 5a PK
ALTER TABLE demo_note ADD CONSTRAINT PK_DEMO_NOTE PRIMARY KEY (note_pk);
-- 5b UNIQUE
-- none — no SRS RULE requires a unique business key on Note
-- 5c CHECK
ALTER TABLE demo_note ADD CONSTRAINT CHK_DEMO_NOTE_TITLE CHECK (length(btrim(title)) > 0); -- RULE-DEMO-001
ALTER TABLE demo_note ADD CONSTRAINT CHK_DEMO_NOTE_CONTENT_LEN CHECK (char_length(content) <= 4000); -- RULE-DEMO-002, ADR-DEMO-001
-- 5d intra-module FK
-- none — single-table module

-- BLOCK 6: TRIGGERS
-- none — no SRS RULE requires a trigger; updated_at is set by the application on update

-- BLOCK 7: INDEXES
CREATE INDEX IDX_DEMO_NOTE_TITLE ON demo_note (title); -- SRS PART B B2 search filter (title)
CREATE INDEX IDX_DEMO_NOTE_UPDATED_AT ON demo_note (updated_at); -- SRS REQ-DEMO-002 ordering (newest first)

-- BLOCK 8: LOOKUP SEED DATA
-- none — DEMO owns no lookup (SRS A6: none)
COMMIT;

-- BLOCK 9: VIEWS
-- none

-- BLOCK 10: FUNCTIONS / PROCEDURES
-- none

-- BLOCK 11: DEFERRED FK PATCH BLOCKS
-- none — no XM in this version
```

## DECISIONS APPLIED
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| DEFAULT | `title` bounded at VARCHAR(200) | no SRS value stated; standard short-text column bound for a title field | override: none requested |
| DEFAULT | identity PK generation (`GENERATED ALWAYS AS IDENTITY`), no PK trigger | `profile.stack.db.syntax_map` (identity syntax declared) | override: none requested |
| DEFAULT | audit columns hold a principal string (`VARCHAR(100)`), not a numeric FK | `[KB:erp-domain-standards §6]` audit trail default | override: none requested |
| ADR-DEMO-001 | `content` maximum length = 4000 characters, enforced by `CHK_DEMO_NOTE_CONTENT_LEN` | `decisions/DEMO/ADR-DEMO-001.md` | status: ACCEPTED (non-breaking) |

## REGISTRY CONTENT
See `registry-db-demo.md`.
══════════════════════════════════════════════════════════════════
