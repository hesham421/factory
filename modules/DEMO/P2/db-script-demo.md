# DB SCRIPT — الملاحظات الشخصية (Personal Notes) — DEMO
══════════════════════════════════════════════════════════════════
DBS-ID          : DBS-DEMO-01
Module          : DEMO (Personal Notes)
SRS Feature Code: DEMO-001
DB_TARGET       : POSTGRESQL_16 (GOVERNANCE-CONFIG.md §3)
Date            : 2026-09-07
Status          : Draft
Open Questions  : None — see srs-demo.md OQ Log
Governed by     : Database Governance Engine (Project 2)
══════════════════════════════════════════════════════════════════

## 1 — DB FIELD TRACEABILITY MATRIX — DEMO — DBS-ID: DBS-DEMO-01

══════════════════════════════════════════════════════════════════════════════════════
DBF-ID    │ Table Name  │ Column Name    │ DB Type        │ SRS Source
──────────┼─────────────┼────────────────┼────────────────┼─────────────────────────
DBF-0001  │ DEMO_NOTE   │ ID             │ BIGINT         │ ENTITY-DEMO-001.noteId
DBF-0002  │ DEMO_NOTE   │ TITLE          │ VARCHAR(200)   │ ENTITY-DEMO-001.title
DBF-0003  │ DEMO_NOTE   │ CONTENT        │ TEXT           │ ENTITY-DEMO-001.content
DBF-0004  │ DEMO_NOTE   │ STATUS_ID      │ VARCHAR(20)    │ ENTITY-DEMO-001.statusId
DBF-0005  │ DEMO_NOTE   │ OWNER_USER_ID  │ BIGINT         │ ENTITY-DEMO-001.ownerUserId
DBF-0006  │ DEMO_NOTE   │ CREATED_BY     │ VARCHAR(255)   │ ENTITY-DEMO-001.createdBy
DBF-0007  │ DEMO_NOTE   │ CREATED_AT     │ TIMESTAMP      │ ENTITY-DEMO-001.createdAt
DBF-0008  │ DEMO_NOTE   │ UPDATED_BY     │ VARCHAR(255)   │ ENTITY-DEMO-001.updatedBy
DBF-0009  │ DEMO_NOTE   │ UPDATED_AT     │ TIMESTAMP      │ ENTITY-DEMO-001.updatedAt
══════════════════════════════════════════════════════════════════════════════════════
Total: 9 DBF-IDs across 1 table

Notes:
- STATUS_ID (DBF-0004) backs srs-demo.md LOV-DEMO-001 (NOTE_STATUS). Per the
  P1 review-gate fix, NOTE_STATUS is a fixed, static 2-value set (ACTIVE,
  DELETED) — implemented here as a plain column + CHECK constraint, NOT a
  row in MD_MASTER_LOOKUP/MD_LOOKUP_DETAIL. Those two shared lookup tables
  are therefore NOT created by this module (Section 4.2 of the engine
  reference: created only by "the first module that needs [them]" — DEMO
  does not, given the SRS's documented deviation).
- OWNER_USER_ID (DBF-0005) is NOT a foreign key. srs-demo.md A3 explicitly
  declares it references the platform's authenticated-user context, which
  is not a governed entity/table in this platform (domain/domain-profile.md
  — no module in this domain owns identity/auth). No FK constraint, no
  XM-ID — consistent with srs-demo.md A7 ("None").

---

## 2 — CROSS-MODULE DEPENDENCY REGISTER (XM REGISTER) — DEMO — DBS-ID: DBS-DEMO-01

None — DEMO has no HARD-FK or SOFT-READ dependency on any other module's
table (srs-demo.md A7; this platform has no other module yet). No XM-IDs
assigned by this stage.

---

## 3 — FULL_DATABASE_SCRIPT

```sql
-- ════════════════════════════════════════════════════════════════
-- DEMO — Personal Notes — DBS-DEMO-01
-- DB_TARGET: POSTGRESQL_16
-- Execution order per PROJECT-2-DATABASE-GOVERNANCE-ENGINE.md §7.1.2
-- ════════════════════════════════════════════════════════════════

-- ── BLOCK 1 — SEQUENCES ──────────────────────────────────────────
CREATE SEQUENCE SEQ_DEMO_NOTE
  START WITH 1
  INCREMENT BY 1
  NO CACHE NO CYCLE;

-- ── BLOCK 2 — PARENT TABLES (no FK dependencies) ─────────────────
-- DEMO_NOTE has no FK dependency on any other table (intra- or
-- cross-module) — it is both the only parent and only child table.
CREATE TABLE DEMO_NOTE (
    ID              BIGINT          NOT NULL,
    TITLE           VARCHAR(200)    NOT NULL,
    CONTENT         TEXT,
    STATUS_ID       VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    OWNER_USER_ID   BIGINT          NOT NULL,
    CREATED_BY      VARCHAR(255),
    CREATED_AT      TIMESTAMP,
    UPDATED_BY      VARCHAR(255),
    UPDATED_AT      TIMESTAMP
);

-- ── BLOCK 3 — CHILD TABLES (intra-module FK dependencies) ────────
-- (none — single-table module)

-- ── BLOCK 4 — COMMENTS ────────────────────────────────────────────
COMMENT ON TABLE DEMO_NOTE IS 'Personal notes — one row per note, owned by a single authenticated user (ENTITY-DEMO-001).';
COMMENT ON COLUMN DEMO_NOTE.ID             IS 'Primary key (DBF-0001).';
COMMENT ON COLUMN DEMO_NOTE.TITLE          IS 'Note title — required, max 200 chars (DBF-0002, RULE-DEMO-001).';
COMMENT ON COLUMN DEMO_NOTE.CONTENT        IS 'Note body — optional, max 20000 chars, enforced at the application layer (DBF-0003, RULE-DEMO-002).';
COMMENT ON COLUMN DEMO_NOTE.STATUS_ID      IS 'Fixed status set: ACTIVE | DELETED — soft-delete flag (DBF-0004, LOV-DEMO-001, RULE-DEMO-004).';
COMMENT ON COLUMN DEMO_NOTE.OWNER_USER_ID  IS 'Authenticated owner user id — not a FK in this platform (DBF-0005, RULE-DEMO-003).';
COMMENT ON COLUMN DEMO_NOTE.CREATED_BY     IS 'Audit — set by AuditEntityListener (DBF-0006).';
COMMENT ON COLUMN DEMO_NOTE.CREATED_AT     IS 'Audit — set by AuditEntityListener (DBF-0007).';
COMMENT ON COLUMN DEMO_NOTE.UPDATED_BY     IS 'Audit — set by AuditEntityListener (DBF-0008).';
COMMENT ON COLUMN DEMO_NOTE.UPDATED_AT     IS 'Audit — set by AuditEntityListener (DBF-0009).';

-- ── BLOCK 5 — CONSTRAINTS ─────────────────────────────────────────
-- 5a. PRIMARY KEY
ALTER TABLE DEMO_NOTE ADD CONSTRAINT PK_DEMO_NOTE PRIMARY KEY (ID);

-- 5b. UNIQUE constraints
-- (none — srs-demo.md defines no uniqueness rule for title/content)

-- 5c. CHECK constraints
ALTER TABLE DEMO_NOTE ADD CONSTRAINT CHK_DEMO_NOTE_STATUS_ID
    CHECK (STATUS_ID IN ('ACTIVE', 'DELETED'));
-- ^ Implements LOV-DEMO-001 (NOTE_STATUS) as a fixed, static value set per
--   the srs-demo.md P1 review-gate fix — no MD_LOOKUP_DETAIL row, no FK.

ALTER TABLE DEMO_NOTE ADD CONSTRAINT CHK_DEMO_NOTE_TITLE_NOT_BLANK
    CHECK (LENGTH(BTRIM(TITLE)) > 0);
-- ^ DB-level backstop for RULE-DEMO-001 ("non-blank title"); the
--   authoritative enforcement is the application validation layer
--   (P3.1), this CHECK exists only to prevent direct-SQL corruption.

-- 5d. INTRA-MODULE FK constraints
-- (none — single-table module)

-- ── BLOCK 6 — TRIGGERS ────────────────────────────────────────────
-- (none — audit columns are populated by AuditEntityListener at the
--  application layer, per srs-demo.md A3; no DB trigger governed here)

-- ── BLOCK 7 — INDEXES ─────────────────────────────────────────────
CREATE INDEX IDX_DEMO_NOTE_OWNER_STATUS
    ON DEMO_NOTE (OWNER_USER_ID, STATUS_ID);
-- ^ Serves API-DEMO-002 (list) and RULE-DEMO-003/004's owner+ACTIVE
--   filter — the module's only real query pattern.

-- ── BLOCK 8 — LOOKUP SEED DATA ────────────────────────────────────
-- (none — NOTE_STATUS is a fixed CHECK constraint, not a
--  MD_MASTER_LOOKUP/MD_LOOKUP_DETAIL row; see Traceability Matrix notes)

-- ── BLOCK 9 — VIEWS ───────────────────────────────────────────────
-- (none)

-- ── BLOCK 10 — FUNCTIONS AND PROCEDURES ───────────────────────────
-- (none)

-- ── BLOCK 11 — DEFERRED FK PATCH BLOCKS ───────────────────────────
-- (none — no cross-module FK is deferred; DEMO has no cross-module
--  dependency at all, see XM Register above)
```

---

## 4 — DB REGISTRY UPDATE

```
## REGISTRY UPDATE — 2026-09-07
────────────────────────────────────────────────────────────────
Source Mode    : MODE 1.5 (P2 — Database)
Feature Code   : DEMO-001
DBS-ID         : DBS-DEMO-01
Plan ID        : —  (assigned by P3.1)
────────────────────────────────────────────────────────────────
New Entities   : —
New Tables     : DEMO_NOTE
New Lookups    : None (NOTE_STATUS implemented as fixed CHECK constraint,
                 not MD_MASTER_LOOKUP/MD_LOOKUP_DETAIL — documented
                 deviation, see Traceability Matrix notes)
New APIs       : —
XM-IDs Open    : None
OQ-IDs Open    : None
Gate Status    : PASSED ✓
Next Action    : Trigger Project 3.1 — Execution Plan Governance Engine (Backend pass)
────────────────────────────────────────────────────────────────
```

══════════════════════════════════════════════════════════════════
*End of db-script-demo.md*
*Governed by: Database Governance Engine (Project 2)*
*DBS-ID: DBS-DEMO-01 | DB_TARGET: POSTGRESQL_16*
*Next Mode: MODE 2 — UI/UX Design Engine (Project 2.5, parallel-eligible) /
 MODE 1.5 output also feeds Project 3.1 (Backend Execution Plan)*
══════════════════════════════════════════════════════════════════
