# DATABASE — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Dialect : postgresql16   Schema prefix : none
Identifier transformation : SRS logical field name (camelCase) → physical column
  name (snake_case) — e.g. `lookupTypePk` → `lookup_type_pk`. Applied to every
  identifier in this script; no other spelling of any field exists.
Date : 2026-09-10
Counts : 2 tables · 21 DBF · 1 XM (SOFT-READ → SEC)
══════════════════════════════════════════════════════════════════

## 1. DB FIELD TRACEABILITY MATRIX — MDL v1

### Table MDL_LOOKUP_TYPE (ENT-MDL-001)
| DBF id | Column | Type (postgresql16) | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-MDL-001 | lookup_type_pk | GENERATED ALWAYS AS IDENTITY | ENT-MDL-001 (PK) | REQ-MDL-001 | NOT NULL | identity |
| DBF-MDL-002 | key | VARCHAR(80) | ENT-MDL-001.key | REQ-MDL-001, REQ-MDL-003 | NOT NULL | — |
| DBF-MDL-003 | owner_module_code | VARCHAR(10) | ENT-MDL-001.ownerModuleCode | REQ-MDL-002 | NOT NULL | — |
| DBF-MDL-004 | name_ar | VARCHAR(150) | ENT-MDL-001.nameAr | REQ-MDL-001, REQ-MDL-003 | NOT NULL | — |
| DBF-MDL-005 | name_en | VARCHAR(150) | ENT-MDL-001.nameEn | REQ-MDL-001, REQ-MDL-003 | NOT NULL | — |
| DBF-MDL-006 | is_active_fl | BOOLEAN | ENT-MDL-001.isActiveFl | REQ-MDL-004 | NOT NULL | TRUE |
| DBF-MDL-007 | created_by | VARCHAR(100) | profile: entity_defaults.master (audit) | REQ-MDL-001 | NOT NULL | — |
| DBF-MDL-008 | created_at | TIMESTAMPTZ | profile: entity_defaults.master (audit) | REQ-MDL-001 | NOT NULL | now() |
| DBF-MDL-009 | updated_by | VARCHAR(100) | profile: entity_defaults.master (audit) | REQ-MDL-001 | NULL | — |
| DBF-MDL-010 | updated_at | TIMESTAMPTZ | profile: entity_defaults.master (audit) | REQ-MDL-001 | NULL | — |

### Table MDL_LOOKUP_VALUE (ENT-MDL-002)
| DBF id | Column | Type | Traces (ENT.field) | Traces (REQ) | Nullable | Default |
|---|---|---|---|---|---|---|
| DBF-MDL-011 | lookup_value_pk | GENERATED ALWAYS AS IDENTITY | ENT-MDL-002 (PK) | REQ-MDL-006 | NOT NULL | identity |
| DBF-MDL-012 | lookup_type_id | NUMERIC | ENT-MDL-002.lookupTypeId → FK ENT-MDL-001 | REQ-MDL-005, REQ-MDL-006 | NOT NULL | — |
| DBF-MDL-013 | code | VARCHAR(50) | ENT-MDL-002.code | REQ-MDL-006, REQ-MDL-007 | NOT NULL | — |
| DBF-MDL-014 | name_ar | VARCHAR(150) | ENT-MDL-002.nameAr | REQ-MDL-006, REQ-MDL-008 | NOT NULL | — |
| DBF-MDL-015 | name_en | VARCHAR(150) | ENT-MDL-002.nameEn | REQ-MDL-006, REQ-MDL-008 | NOT NULL | — |
| DBF-MDL-016 | sort_order | NUMERIC | ENT-MDL-002.sortOrder | REQ-MDL-006, REQ-MDL-010 | NOT NULL | 0 |
| DBF-MDL-017 | is_active_fl | BOOLEAN | ENT-MDL-002.isActiveFl | REQ-MDL-009 | NOT NULL | TRUE |
| DBF-MDL-018 | created_by | VARCHAR(100) | profile: entity_defaults.lookup (audit) | REQ-MDL-006 | NOT NULL | — |
| DBF-MDL-019 | created_at | TIMESTAMPTZ | profile: entity_defaults.lookup (audit) | REQ-MDL-006 | NOT NULL | now() |
| DBF-MDL-020 | updated_by | VARCHAR(100) | profile: entity_defaults.lookup (audit) | REQ-MDL-006 | NULL | — |
| DBF-MDL-021 | updated_at | TIMESTAMPTZ | profile: entity_defaults.lookup (audit) | REQ-MDL-006 | NULL | — |

Total: 21 DBF ids across 2 tables.

## 2. XM REGISTER — MDL v1
| XM id | Type | This table | Column / access | Target table | Target module | Traces (REQ) | Status |
|---|---|---|---|---|---|---|---|
| XM-MDL-001 | SOFT-READ | MDL_LOOKUP_TYPE | `owner_module_code` — application-level read of `SEC_MODULE_REG.code` on create | SEC_MODULE_REG | SEC | REQ-MDL-002 | ACTIVE (target SEC v1 gated, pass-1 APPROVE) |

### 2.1 SOFT-READ handling
```
-- XM-MDL-001 SOFT-READ — MDL's lookup-type creation service reads SEC_MODULE_REG.code
-- from SEC without an FK. Rationale: RULE-MDL-001 / SRS A8 — validates owner_module_code
-- names a real registered module before accepting the registration.
-- Risk: a module deactivated in SEC_MODULE_REG after a LookupType already names it is not
-- retro-invalidated here — an accepted impact per XM-PROTOCOL.md (no cascading revoke
-- across modules); affected requirement: REQ-MDL-002 (checked only at creation time).
```

No DEFERRED FK — this XM is SOFT-READ by design (§6 FK classification: SOFT-READ never
gets a live constraint), not a HARD-FK blocked on gating (SEC is already gated in any case).

## 3. FULL_DATABASE_SCRIPT

```sql
-- ════════════════════════════════════════════════════════════════
-- MDL v1 — Master Data Lookup module — PostgreSQL 16
-- Identifier transformation: camelCase (SRS) -> snake_case (DB)
-- ════════════════════════════════════════════════════════════════

-- BLOCK 1 — SEQUENCES
-- none: every PK uses GENERATED ALWAYS AS IDENTITY (postgresql16 syntax_map)

-- BLOCK 2 — PARENT TABLES (no FK dependencies)

CREATE TABLE MDL_LOOKUP_TYPE (
  lookup_type_pk      BIGINT GENERATED ALWAYS AS IDENTITY,
  key                  VARCHAR(80)   NOT NULL,
  owner_module_code    VARCHAR(10)   NOT NULL,
  name_ar              VARCHAR(150)  NOT NULL,
  name_en              VARCHAR(150)  NOT NULL,
  is_active_fl         BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by           VARCHAR(100)  NOT NULL,
  created_at           TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by           VARCHAR(100),
  updated_at           TIMESTAMPTZ
);

-- BLOCK 3 — CHILD TABLES (parent already created above)

CREATE TABLE MDL_LOOKUP_VALUE (
  lookup_value_pk  BIGINT GENERATED ALWAYS AS IDENTITY,
  lookup_type_id   BIGINT        NOT NULL,
  code             VARCHAR(50)   NOT NULL,
  name_ar          VARCHAR(150)  NOT NULL,
  name_en          VARCHAR(150)  NOT NULL,
  sort_order       NUMERIC       NOT NULL DEFAULT 0,
  is_active_fl     BOOLEAN       NOT NULL DEFAULT TRUE,
  created_by       VARCHAR(100)  NOT NULL,
  created_at       TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_by       VARCHAR(100),
  updated_at       TIMESTAMPTZ
);

-- BLOCK 4 — COMMENTS

COMMENT ON TABLE MDL_LOOKUP_TYPE IS 'ENT-MDL-001 LookupType — SHARED(owner); [DBF-MDL-001..010]';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.lookup_type_pk IS 'DBF-MDL-001';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.key IS 'DBF-MDL-002 — immutable after create, RULE-MDL-003 (application layer)';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.owner_module_code IS 'DBF-MDL-003 — XM-MDL-001 SOFT-READ validates against SEC_MODULE_REG.code, RULE-MDL-001 (application layer)';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.name_ar IS 'DBF-MDL-004';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.name_en IS 'DBF-MDL-005';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.is_active_fl IS 'DBF-MDL-006';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.created_by IS 'DBF-MDL-007';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.created_at IS 'DBF-MDL-008';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.updated_by IS 'DBF-MDL-009';
COMMENT ON COLUMN MDL_LOOKUP_TYPE.updated_at IS 'DBF-MDL-010';

COMMENT ON TABLE MDL_LOOKUP_VALUE IS 'ENT-MDL-002 LookupValue — SHARED(owner); [DBF-MDL-011..021]';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.lookup_value_pk IS 'DBF-MDL-011';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.lookup_type_id IS 'DBF-MDL-012';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.code IS 'DBF-MDL-013 — unique within lookup_type_id, UQ_MDL_LOOKUP_VALUE_TYPE_CODE, RULE-MDL-002';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.name_ar IS 'DBF-MDL-014';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.name_en IS 'DBF-MDL-015';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.sort_order IS 'DBF-MDL-016';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.is_active_fl IS 'DBF-MDL-017';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.created_by IS 'DBF-MDL-018';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.created_at IS 'DBF-MDL-019';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.updated_by IS 'DBF-MDL-020';
COMMENT ON COLUMN MDL_LOOKUP_VALUE.updated_at IS 'DBF-MDL-021';

-- BLOCK 5 — CONSTRAINTS

-- 5a PK
ALTER TABLE MDL_LOOKUP_TYPE  ADD CONSTRAINT PK_MDL_LOOKUP_TYPE  PRIMARY KEY (lookup_type_pk);
ALTER TABLE MDL_LOOKUP_VALUE ADD CONSTRAINT PK_MDL_LOOKUP_VALUE PRIMARY KEY (lookup_value_pk);

-- 5b UNIQUE
ALTER TABLE MDL_LOOKUP_TYPE  ADD CONSTRAINT UQ_MDL_LOOKUP_TYPE_KEY        UNIQUE (key);
ALTER TABLE MDL_LOOKUP_VALUE ADD CONSTRAINT UQ_MDL_LOOKUP_VALUE_TYPE_CODE UNIQUE (lookup_type_id, code);   -- RULE-MDL-002, enforced structurally

-- 5c CHECK
-- none — no closed value set on any MDL column itself (MDL stores others' coded values, not its own).

-- 5d intra-module FK (parent PK first)
ALTER TABLE MDL_LOOKUP_VALUE ADD CONSTRAINT FK_LOOKUP_VALUE_TYPE FOREIGN KEY (lookup_type_id) REFERENCES MDL_LOOKUP_TYPE (lookup_type_pk);

-- No FK for owner_module_code -> SEC_MODULE_REG.code: XM-MDL-001 is SOFT-READ by design
-- (§6 FK classification — SOFT-READ never gets a live constraint), not a HARD-FK.

-- BLOCK 6 — TRIGGERS
-- none: RULE-MDL-001/003/004 are application-layer (cross-module read, field-omission,
-- and join-time filter respectively); RULE-MDL-002 is already enforced structurally by
-- UQ_MDL_LOOKUP_VALUE_TYPE_CODE above — no trigger needed.

-- BLOCK 7 — INDEXES (non-PK; every FK column + every SRS search/list filter column)
CREATE INDEX IDX_MDL_LOOKUP_TYPE_OWNER   ON MDL_LOOKUP_TYPE (owner_module_code);
CREATE INDEX IDX_MDL_LOOKUP_TYPE_ACTIVE  ON MDL_LOOKUP_TYPE (is_active_fl);
CREATE INDEX IDX_MDL_LOOKUP_VALUE_TYPE   ON MDL_LOOKUP_VALUE (lookup_type_id);
CREATE INDEX IDX_MDL_LOOKUP_VALUE_SORT   ON MDL_LOOKUP_VALUE (lookup_type_id, sort_order);

-- BLOCK 8 — LOOKUP SEED DATA
-- none: MDL introduces no domain-specific coded list of its own (SRS A6); it is the
-- generic mechanism other modules' types/values populate at runtime, not at deploy time.
COMMIT;

-- BLOCK 9 — VIEWS
-- none required by this SRS.

-- BLOCK 10 — FUNCTIONS / PROCEDURES
-- none required by this SRS.

-- BLOCK 11 — DEFERRED FK PATCH BLOCKS
-- none: MDL's one cross-module dependency (XM-MDL-001) is SOFT-READ, never a deferred
-- HARD-FK (see §2.1).
```

## 4. DECISIONS APPLIED
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
No ADR — every structural choice this stage traced cleanly to the SRS or a profile
default (identity PK generation, snake_case transformation, index-per-filter-column);
no ambiguity reached the §9 fork.

## 5. REGISTRY CONTENT
See `registry-db-mdl.md`.

## 6. DBF id definitions (cross-reference index — full detail in §1; `[traces]` = ENT + REQ)
**DBF-MDL-001** — MDL_LOOKUP_TYPE.lookup_type_pk [ENT-MDL-001, REQ-MDL-001]
**DBF-MDL-002** — MDL_LOOKUP_TYPE.key [ENT-MDL-001, REQ-MDL-001, REQ-MDL-003]
**DBF-MDL-003** — MDL_LOOKUP_TYPE.owner_module_code [ENT-MDL-001, REQ-MDL-002]
**DBF-MDL-004** — MDL_LOOKUP_TYPE.name_ar [ENT-MDL-001, REQ-MDL-001, REQ-MDL-003]
**DBF-MDL-005** — MDL_LOOKUP_TYPE.name_en [ENT-MDL-001, REQ-MDL-001, REQ-MDL-003]
**DBF-MDL-006** — MDL_LOOKUP_TYPE.is_active_fl [ENT-MDL-001, REQ-MDL-004]
**DBF-MDL-007** — MDL_LOOKUP_TYPE.created_by [ENT-MDL-001, REQ-MDL-001]
**DBF-MDL-008** — MDL_LOOKUP_TYPE.created_at [ENT-MDL-001, REQ-MDL-001]
**DBF-MDL-009** — MDL_LOOKUP_TYPE.updated_by [ENT-MDL-001, REQ-MDL-001]
**DBF-MDL-010** — MDL_LOOKUP_TYPE.updated_at [ENT-MDL-001, REQ-MDL-001]
**DBF-MDL-011** — MDL_LOOKUP_VALUE.lookup_value_pk [ENT-MDL-002, REQ-MDL-006]
**DBF-MDL-012** — MDL_LOOKUP_VALUE.lookup_type_id [ENT-MDL-002, ENT-MDL-001, REQ-MDL-005, REQ-MDL-006]
**DBF-MDL-013** — MDL_LOOKUP_VALUE.code [ENT-MDL-002, REQ-MDL-006, REQ-MDL-007]
**DBF-MDL-014** — MDL_LOOKUP_VALUE.name_ar [ENT-MDL-002, REQ-MDL-006, REQ-MDL-008]
**DBF-MDL-015** — MDL_LOOKUP_VALUE.name_en [ENT-MDL-002, REQ-MDL-006, REQ-MDL-008]
**DBF-MDL-016** — MDL_LOOKUP_VALUE.sort_order [ENT-MDL-002, REQ-MDL-006, REQ-MDL-010]
**DBF-MDL-017** — MDL_LOOKUP_VALUE.is_active_fl [ENT-MDL-002, REQ-MDL-009]
**DBF-MDL-018** — MDL_LOOKUP_VALUE.created_by [ENT-MDL-002, REQ-MDL-006]
**DBF-MDL-019** — MDL_LOOKUP_VALUE.created_at [ENT-MDL-002, REQ-MDL-006]
**DBF-MDL-020** — MDL_LOOKUP_VALUE.updated_by [ENT-MDL-002, REQ-MDL-006]
**DBF-MDL-021** — MDL_LOOKUP_VALUE.updated_at [ENT-MDL-002, REQ-MDL-006]

## 7. XM id definitions
**XM-MDL-001** — SOFT-READ MDL_LOOKUP_TYPE.owner_module_code → SEC_MODULE_REG.code [REQ-MDL-002]
══════════════════════════════════════════════════════════════════
