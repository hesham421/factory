# DATABASE — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module : NOTE   Version : v1   Dialect : postgresql16   Schema prefix : none
Identifier transformation : SRS logical field name (camelCase) → physical column
  name (snake_case) — e.g. `notePk` → `note_pk`, `ownerUserRef` → `owner_user_ref`,
  `isActiveFl` → `is_active_fl`. Applied to every identifier in this script; no other
  spelling of any field exists. All identifiers are within the 63-character limit of
  postgresql16 and none is a reserved word.
PK generation : `sequence` (profile.stack.db.pk_generation) — one `SEQ_{TABLE}` per
  table in BLOCK 1; the PK column is a plain `BIGINT NOT NULL` populated by the
  application from that sequence. No identity clause and no sequence DEFAULT anywhere.
Date : 2026-09-17
Counts : 1 table · 9 DBF · 0 XM · 0 lookup keys owned · 0 lookup keys consumed
══════════════════════════════════════════════════════════════════

## 1. DB FIELD TRACEABILITY MATRIX — NOTE v1

### Table NOTE_NOTE (ENT-NOTE-001 — الملاحظة / Note, kind `master`, PRIVATE)
| DBF id | Column | Type (postgresql16) | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-NOTE-001 | note_pk | BIGINT | ENT-NOTE-001.notePk (PK, profile.stack.db.naming.pk_pattern) | REQ-NOTE-001, REQ-NOTE-006 | NOT NULL | — (from SEQ_NOTE_NOTE, set by the application) |
| DBF-NOTE-002 | note_title | VARCHAR(200) | ENT-NOTE-001.noteTitle | REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-011 | NOT NULL | — |
| DBF-NOTE-003 | note_body | VARCHAR(4000) | ENT-NOTE-001.noteBody | REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-011 | NOT NULL | — |
| DBF-NOTE-004 | owner_user_ref | VARCHAR(100) | ENT-NOTE-001.ownerUserRef | REQ-NOTE-002, REQ-NOTE-006, REQ-NOTE-009 | NOT NULL | — |
| DBF-NOTE-005 | is_active_fl | BOOLEAN | ENT-NOTE-001.isActiveFl | REQ-NOTE-003, REQ-NOTE-007, REQ-NOTE-008, REQ-NOTE-010, REQ-NOTE-013 | NOT NULL | TRUE |
| DBF-NOTE-006 | created_by | VARCHAR(100) | ENT-NOTE-001.createdBy (profile: entity_defaults.master — audit) | REQ-NOTE-001, REQ-NOTE-002 | NOT NULL | — |
| DBF-NOTE-007 | created_at | TIMESTAMPTZ | ENT-NOTE-001.createdAt (profile: entity_defaults.master — audit) | REQ-NOTE-001, REQ-NOTE-012 | NOT NULL | now() |
| DBF-NOTE-008 | updated_by | VARCHAR(100) | ENT-NOTE-001.updatedBy (profile: entity_defaults.master — audit) | REQ-NOTE-005 | NULL | — |
| DBF-NOTE-009 | updated_at | TIMESTAMPTZ | ENT-NOTE-001.updatedAt (profile: entity_defaults.master — audit) | REQ-NOTE-005, REQ-NOTE-012 | NULL | — |

Total: 9 DBF ids across 1 table.

## 1a. DB FIELD DEFINITIONS — NOTE v1

One line per `DBF`, addressed by its own id. The matrix above carries the full
row; this is the per-id definition the registry resolves against.

**DBF-NOTE-001** — NOTE_NOTE.note_pk [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-001, REQ-NOTE-006

**DBF-NOTE-002** — NOTE_NOTE.note_title [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-011

**DBF-NOTE-003** — NOTE_NOTE.note_body [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-011

**DBF-NOTE-004** — NOTE_NOTE.owner_user_ref [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-002, REQ-NOTE-006, REQ-NOTE-009

**DBF-NOTE-005** — NOTE_NOTE.is_active_fl [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-003, REQ-NOTE-007, REQ-NOTE-008, REQ-NOTE-010, REQ-NOTE-013

**DBF-NOTE-006** — NOTE_NOTE.created_by [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-001, REQ-NOTE-002

**DBF-NOTE-007** — NOTE_NOTE.created_at [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-001, REQ-NOTE-012

**DBF-NOTE-008** — NOTE_NOTE.updated_by [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-005

**DBF-NOTE-009** — NOTE_NOTE.updated_at [ENT-NOTE-001]
  Traces: ENT-NOTE-001, REQ-NOTE-005, REQ-NOTE-012


**Datatype governance notes**
- `note_title` / `note_body` — the SRS declares the logical type `text` for both, which
  §4.1 maps to `TEXT`. Both carry a declared maximum (200 / 4000 characters,
  RULE-NOTE-003 via ADR-NOTE-002), so each is emitted as `VARCHAR(n)` with `n` taken
  from that rule: the length limit is a structural fact of the field, and a `TEXT`
  column could not carry it. The business message of RULE-NOTE-003 is still produced by
  the application (P3.1) — the column is the floor, not the user-facing check.
- `owner_user_ref`, `created_by`, `updated_by` — the SRS declares the logical type `text`
  and states these hold the authenticated principal identifier delivered by the platform
  interceptor (ENT-SEC-001, a principal string, never a numeric key). Emitted as
  `VARCHAR(100)`, the same width SEC's own `created_by` / `updated_by` principal columns
  carry (DBF-SEC-010 … DBF-SEC-013) — one platform, one principal width.
- `created_at`, `updated_at` — `date-time` → `TIMESTAMPTZ`, stored UTC, displayed in the
  tenant timezone [KB:erp-domain-standards §6].
- `is_active_fl` — logical type `flag` → `BOOLEAN`, name ends with `Fl` per profile check
  `ERP-3`; defaults to active (`TRUE`) per REQ-NOTE-003. There is no "deleted" column:
  deactivation, not deletion (REQ-NOTE-008, POL-NOTE-003).

**Declared absences** — `name_ar`, `name_en`, `code` are NOT columns of this table:
ADR-NOTE-001 narrows the `master` defaults for this entity (the user's own content is
monolingual, POL-NOTE-005, and the note carries no business code, §3.3 NUMBERING).
Nothing is invented: every column above is an SRS field or an audit default of the
entity's kind (NO-COLUMN-INVENTION).

## 2. XM REGISTER — NOTE v1

| XM id | Type | This table | Column / access | Target table | Target module | Traces (REQ) | Status |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

**No XM row is assigned by this stage — 0 rows.** SRS A8 lists four consumed SEC
entities and classifies each as "لا شيء / none" rather than as an XM candidate:

| Consumed entity | Owner | Why no XM row |
|---|---|---|
| ENT-SEC-001 User | SEC | `owner_user_ref` and the audit columns hold the principal **string** handed over by the standard interceptor — no FK column, no join, no read of `SEC_USER` by this module's code. A8: "لا شيء". |
| ENT-SEC-004 ModuleRegistry | SEC | Deployment-time registration **as data** (REQ-NOTE-017), not a runtime dependency — precedent ADR-FIN-001 (project-registry DECISION INDEX #9): self-registration is neither an XM row nor a foreign key. |
| ENT-SEC-005 ScreenRegistry | SEC | same precedent |
| ENT-SEC-006 ActionRegistry | SEC | same precedent |

Consequently: no HARD-FK (READY or DEFERRED), no SOFT-READ row, no deferred patch block
(BLOCK 11 is empty by construction), and nothing for INT-C / INT-R to carry beyond the
empty-but-present phases the module registry requires. Audit columns are never XMs (§5).
An XM invented here would be an ORPHAN — it would have no SRS A8 origin.

## 3. FULL_DATABASE_SCRIPT

```sql
-- ════════════════════════════════════════════════════════════════
-- NOTE v1 — Notes module — PostgreSQL 16
-- Identifier transformation: camelCase (SRS) -> snake_case (DB)
-- PK generation: sequence (profile.stack.db.pk_generation) — the application draws
--   the key from SEQ_NOTE_NOTE; no identity clause, no sequence default on the PK.
-- Schema prefix: none (no object in this script is schema-qualified).
-- ════════════════════════════════════════════════════════════════

-- BLOCK 1 — SEQUENCES (one per table; table count = 1, sequence count = 1)
CREATE SEQUENCE SEQ_NOTE_NOTE START WITH 1 INCREMENT BY 1 CACHE 1 NO CYCLE;

-- BLOCK 2 — PARENT TABLES (no FK dependencies)
-- NOTE owns no lookup key and consumes none (SRS A6): no lookup or reference table is
-- created here, and none of another module's lookup tables is touched.
CREATE TABLE NOTE_NOTE (
  note_pk         BIGINT         NOT NULL,
  note_title      VARCHAR(200)   NOT NULL,
  note_body       VARCHAR(4000)  NOT NULL,
  owner_user_ref  VARCHAR(100)   NOT NULL,
  is_active_fl    BOOLEAN        NOT NULL DEFAULT TRUE,
  created_by      VARCHAR(100)   NOT NULL,
  created_at      TIMESTAMPTZ    NOT NULL DEFAULT now(),
  updated_by      VARCHAR(100),
  updated_at      TIMESTAMPTZ
);

-- BLOCK 3 — CHILD TABLES (intra-module FK targets)
-- none: the module owns exactly one entity (ENT-NOTE-001), so there is no intra-module
-- foreign key and no parent/child chain.

-- BLOCK 4 — COMMENTS (table + every column; each column comment cites its DBF id)
COMMENT ON TABLE  NOTE_NOTE                 IS 'ENT-NOTE-001 — الملاحظة / Note. Master entity, PRIVATE: no other module reads it (POL-NOTE-001). Soft deactivation only, never deletion (REQ-NOTE-008).';
COMMENT ON COLUMN NOTE_NOTE.note_pk         IS 'DBF-NOTE-001 — ENT-NOTE-001.notePk. Primary key, drawn by the application from SEQ_NOTE_NOTE. Not a business reference and never shown as one (REQ-NOTE-001).';
COMMENT ON COLUMN NOTE_NOTE.note_title      IS 'DBF-NOTE-002 — ENT-NOTE-001.noteTitle. العنوان / Title. Free text in its author''s language (POL-NOTE-005); max 200 chars per RULE-NOTE-003; non-blank per RULE-NOTE-001.';
COMMENT ON COLUMN NOTE_NOTE.note_body       IS 'DBF-NOTE-003 — ENT-NOTE-001.noteBody. النص / Body. Free text in its author''s language (POL-NOTE-005); max 4000 chars per RULE-NOTE-003; non-blank per RULE-NOTE-002.';
COMMENT ON COLUMN NOTE_NOTE.owner_user_ref  IS 'DBF-NOTE-004 — ENT-NOTE-001.ownerUserRef. المالك / Owner: the authenticated principal identifier (ENT-SEC-001 as a string, no FK). Set by the platform at creation, never accepted from a client (REQ-NOTE-002), never changed afterwards (RULE-NOTE-004).';
COMMENT ON COLUMN NOTE_NOTE.is_active_fl    IS 'DBF-NOTE-005 — ENT-NOTE-001.isActiveFl. فعّالة / Active. TRUE on creation (REQ-NOTE-003); set FALSE by the deactivate operation only (REQ-NOTE-007). The default list shows TRUE rows only (REQ-NOTE-010); the explicit deactivated path shows FALSE rows (REQ-NOTE-013).';
COMMENT ON COLUMN NOTE_NOTE.created_by      IS 'DBF-NOTE-006 — ENT-NOTE-001.createdBy (profile: entity_defaults.master, audit). Principal string filled by the platform, never accepted from the request (AC-NOTE-002).';
COMMENT ON COLUMN NOTE_NOTE.created_at      IS 'DBF-NOTE-007 — ENT-NOTE-001.createdAt (profile: entity_defaults.master, audit). Stored UTC, displayed in the tenant timezone [KB:erp-domain-standards §6].';
COMMENT ON COLUMN NOTE_NOTE.updated_by      IS 'DBF-NOTE-008 — ENT-NOTE-001.updatedBy (profile: entity_defaults.master, audit). NULL until the first update (REQ-NOTE-005).';
COMMENT ON COLUMN NOTE_NOTE.updated_at      IS 'DBF-NOTE-009 — ENT-NOTE-001.updatedAt (profile: entity_defaults.master, audit). NULL until the first update; stored UTC.';

-- BLOCK 5 — CONSTRAINTS

-- 5a PK
ALTER TABLE NOTE_NOTE ADD CONSTRAINT PK_NOTE_NOTE PRIMARY KEY (note_pk);

-- 5b UNIQUE
-- none: the SRS declares no business key for ENT-NOTE-001 (no code, no document number
-- — §3.3 NUMBERING), and no RULE demands uniqueness of any column or column pair.
-- Two notes of the same owner may carry the same title by design.

-- 5c CHECK
ALTER TABLE NOTE_NOTE ADD CONSTRAINT CHK_NOTE_NOTE_NOTE_TITLE     CHECK (btrim(note_title) <> '');
ALTER TABLE NOTE_NOTE ADD CONSTRAINT CHK_NOTE_NOTE_NOTE_BODY      CHECK (btrim(note_body) <> '');
ALTER TABLE NOTE_NOTE ADD CONSTRAINT CHK_NOTE_NOTE_OWNER_USER_REF CHECK (btrim(owner_user_ref) <> '');

-- 5d INTRA-MODULE FK
-- none: one entity, no intra-module reference. No cross-module FK exists either
-- (see §2 XM REGISTER) — owner_user_ref holds a principal string, not a key.

-- BLOCK 6 — TRIGGERS
-- none. No SRS RULE requires a database trigger: RULE-NOTE-004 (ownership immutable),
-- RULE-NOTE-005 (owner-scoped access), RULE-NOTE-006 (no edit while inactive) and
-- RULE-NOTE-007 (no repeated deactivation) are request-scoped business rules carrying
-- bilingual messages, enforced at the application layer (P3.1) — a trigger there would
-- surface a database error the user must never see (REQ-NOTE-004 rationale).
-- Never a PK trigger (§4).

-- BLOCK 7 — INDEXES (non-PK)
-- Owner + state is the shape of every list and search this module serves: the search is
-- always confined to the requester (REQ-NOTE-009) and filtered by state
-- (REQ-NOTE-010 / REQ-NOTE-013). The composite's leading column covers the owner-only
-- access path, so no separate single-column owner index is created (PK index implicit).
CREATE INDEX IDX_NOTE_NOTE_OWN_ACT ON NOTE_NOTE (owner_user_ref, is_active_fl);
-- Default ordering of the list is newest first, on updated_at falling back to created_at
-- (SCR-REQ-NOTE-001 §B2), within the requester's rows.
CREATE INDEX IDX_NOTE_NOTE_OWN_UPD ON NOTE_NOTE (owner_user_ref, updated_at);
CREATE INDEX IDX_NOTE_NOTE_OWN_CRT ON NOTE_NOTE (owner_user_ref, created_at);
-- note_title / note_body carry no index: the B2 text filter is a "contains" match
-- (REQ-NOTE-011) that a B-tree cannot serve — ADR-NOTE-004 (ACCEPTED, non-breaking).

-- BLOCK 8 — LOOKUP SEED DATA
-- none. SRS A6: NOTE owns no lookup key and consumes none in v1 — is_active_fl is a
-- platform boolean, not a lookup type, and the note's title and body are free text
-- (POL-NOTE-005). There is therefore no key this module owns whose values another
-- module's table would have to be seeded with, and no lookup table of any module is
-- created or populated by this script.

-- BLOCK 9 — VIEWS
-- none required by this SRS.

-- BLOCK 10 — FUNCTIONS / PROCEDURES
-- none required by this SRS.

-- BLOCK 11 — DEFERRED FK PATCH BLOCKS
-- none: no XM row exists in this version (see §2 XM REGISTER), so there is no deferred
-- cross-module constraint to apply later and no live FK to another module's table.
```

## 4. DECISIONS APPLIED

| DEFAULT / ADR | What | Status |
|---|---|---|
| ADR-NOTE-004 | No index on `note_title` / `note_body`: the B2 filter is a substring match a B-tree cannot serve; the owner-scoped composite index bounds the scan instead | ACCEPTED (non-breaking) — `erp/decisions/NOTE/ADR-NOTE-004.md` |
| ADR-NOTE-001 (P1, applied here) | `NOTE_NOTE` carries no `name_ar` / `name_en` / `code` — the declared narrowing of the `master` defaults | ACCEPTED (non-breaking) |
| ADR-NOTE-002 (P1, applied here) | `VARCHAR(200)` / `VARCHAR(4000)` — the physical form of the 200 / 4000-character limits | ACCEPTED (non-breaking) |
| DEFAULT | Soft deactivation via `is_active_fl DEFAULT TRUE`; no delete column, no delete statement | [KB:erp-domain-standards §6]; POL-NOTE-003 |
| DEFAULT | The four audit fields on the table; principal columns as `VARCHAR(100)` strings, not numeric FKs | [KB:erp-domain-standards §6]; profile: entity_defaults.master |
| DEFAULT | `TIMESTAMPTZ`, stored UTC, displayed in the tenant timezone | [KB:erp-domain-standards §6 dates] |
| Precedent ADR-FIN-001 | Self-registration in the SEC registries is neither an XM row nor a foreign key | project-registry DECISION INDEX #9 |

No BLOCKED ADR — the pass was not stopped. No question was raised.

## 5. REGISTRY CONTENT

See `erp/modules/NOTE/P2/registry-db-note.md` (the registry artifact of this stage).

## 6. DBF id definitions (cross-reference index — full detail in §1)

| DBF id | Table.column | Traces |
|---|---|---|
| DBF-NOTE-001 | NOTE_NOTE.note_pk | ENT-NOTE-001.notePk · REQ-NOTE-001, REQ-NOTE-006 |
| DBF-NOTE-002 | NOTE_NOTE.note_title | ENT-NOTE-001.noteTitle · REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-011 |
| DBF-NOTE-003 | NOTE_NOTE.note_body | ENT-NOTE-001.noteBody · REQ-NOTE-001, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-011 |
| DBF-NOTE-004 | NOTE_NOTE.owner_user_ref | ENT-NOTE-001.ownerUserRef · REQ-NOTE-002, REQ-NOTE-006, REQ-NOTE-009 |
| DBF-NOTE-005 | NOTE_NOTE.is_active_fl | ENT-NOTE-001.isActiveFl · REQ-NOTE-003, REQ-NOTE-007, REQ-NOTE-008, REQ-NOTE-010, REQ-NOTE-013 |
| DBF-NOTE-006 | NOTE_NOTE.created_by | ENT-NOTE-001.createdBy · REQ-NOTE-001, REQ-NOTE-002 |
| DBF-NOTE-007 | NOTE_NOTE.created_at | ENT-NOTE-001.createdAt · REQ-NOTE-001, REQ-NOTE-012 |
| DBF-NOTE-008 | NOTE_NOTE.updated_by | ENT-NOTE-001.updatedBy · REQ-NOTE-005 |
| DBF-NOTE-009 | NOTE_NOTE.updated_at | ENT-NOTE-001.updatedAt · REQ-NOTE-005, REQ-NOTE-012 |

## 7. RULE → constraint map (§12 self-check)

| RULE | Where it lands |
|---|---|
| RULE-NOTE-001 | `CHK_NOTE_NOTE_NOTE_TITLE` + `NOT NULL` on `note_title` |
| RULE-NOTE-002 | `CHK_NOTE_NOTE_NOTE_BODY` + `NOT NULL` on `note_body` |
| RULE-NOTE-003 | `VARCHAR(200)` / `VARCHAR(4000)` column widths |
| RULE-NOTE-004 | Application layer (P3.1) — `owner_user_ref NOT NULL` + `CHK_NOTE_NOTE_OWNER_USER_REF` is the structural floor; immutability is request-scoped |
| RULE-NOTE-005 | Application layer (P3.1) — the owner predicate on every read, update, deactivate and search; structurally supported by `IDX_NOTE_NOTE_OWN_ACT` |
| RULE-NOTE-006 | Application layer (P3.1) — a state-dependent rule with a bilingual message |
| RULE-NOTE-007 | Application layer (P3.1) — a state-dependent rule with a bilingual message |

**Data source binding (C6.9)** — every RULE's `Data source` resolves to a field of
ENT-NOTE-001 and is bound to a physical column here; none is DEFERRED:
RULE-NOTE-001 → ENT-NOTE-001.noteTitle → DBF-NOTE-002 · RULE-NOTE-002 →
ENT-NOTE-001.noteBody → DBF-NOTE-003 · RULE-NOTE-003 → ENT-NOTE-001.noteTitle,
ENT-NOTE-001.noteBody → DBF-NOTE-002, DBF-NOTE-003 · RULE-NOTE-004 →
ENT-NOTE-001.ownerUserRef → DBF-NOTE-004 · RULE-NOTE-005 → ENT-NOTE-001.ownerUserRef →
DBF-NOTE-004 · RULE-NOTE-006 → ENT-NOTE-001.isActiveFl → DBF-NOTE-005 · RULE-NOTE-007 →
ENT-NOTE-001.isActiveFl → DBF-NOTE-005.
══════════════════════════════════════════════════════════════════
