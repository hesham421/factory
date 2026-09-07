# PLATFORM STANDARDS — factory (single-project instance)
══════════════════════════════════════════════════════════════════
Version       : 1.0.0
Last Updated  : 2026-09-07 by P-1 (bootstrap)
Applies to    : every module analyzed by this factory instance
══════════════════════════════════════════════════════════════════

This file records the platform-wide engineering conventions every
downstream engine (P0 → P3.5) inherits, so no single module's SRS/DB/
execution-plan has to restate them. It is informational/conventions-level
— the authoritative, machine-checked values for anything it restates live
in `shared/GOVERNANCE-CONFIG.md` (never here; see note under STACK below).

## STACK (mirrors GOVERNANCE-CONFIG.md — never a second source of truth)
```
BACKEND_STACK   : SPRING_BOOT_JAVA
FRONTEND_STACK  : REACT_TS_VITE  (Vite, React Router, TanStack Query,
                  React Hook Form + Zod, useState/useReducer + Context —
                  no Redux/global-state library unless a DRV-ID justifies it)
MOBILE_STACK    : FLUTTER_DART (not in scope — no mobile track requested
                  for DEMO or any module yet)
DB_TARGET       : POSTGRESQL_16
WORKFLOW-ENGINE-TIER : OFF
BUSINESS-CODE-DEFAULT: NOT-APPLIED-UNLESS-EXPLICIT
```
If GOVERNANCE-CONFIG.md is ever amended, that file's new value governs
immediately — this section is updated to match at the next P-1/registry
touch, never the other way around.

## API CONVENTIONS
- REST, Spring Boot conventions (per shared-governance-rules.md Project 1
  scope): resource-oriented paths, plural nouns, standard HTTP verbs
  (GET/POST/PUT/PATCH/DELETE), standard status codes (200/201/204/400/
  401/403/404/409/422/500).
- Base path pattern: `/api/v1/{module-lowercase}/{resource-plural}`
  (e.g. `/api/v1/demo/notes`).
- List endpoints support pagination (page/size) and return a bounded
  page, never an unbounded collection.
- Every API is documented in the owning module's SRS Part B5 and carries
  an API-ID; error responses reference the module's Error Catalog by
  ERR-ID (CONTRACT-4) — never inline free-text error contracts.

## ENTITY / DB CONVENTIONS
- Table names: `{MODULE}_{ENTITY_ABBREV}` in upper snake case (matches
  shared/MASTER-REGISTRY-SCHEMA.md §13 naming convention), e.g.
  `DEMO_NOTE`.
- Every entity carries standard audit columns at minimum: `id` (PK,
  BIGINT via explicit SEQUENCE per DB_TARGET=POSTGRESQL_16 — no SERIAL/
  IDENTITY, per GOVERNANCE-CONFIG.md §3 note), `created_at`,
  `updated_at`, `created_by` (owner reference), `is_active_fl`
  (SMALLINT DEFAULT 1) for soft-delete/status where the module's SRS
  calls for it.
- Owner-scoped entities (the norm for the General/Personal-Productivity
  domain — see domain/domain-profile.md) carry an owner column
  (`owner_user_id` or equivalent) enforced at the application layer on
  every query; there is no row-level DB policy by default.
- Field types follow the DB_TARGET Syntax Mapping table in
  GOVERNANCE-CONFIG.md §3 exactly — no ad hoc type choices per module.

## NAMING CONVENTIONS
```
Module prefix     : the factory's per-module naming scheme (see
                     governance-tools/tracks/backend/config.py
                     ARTIFACT_FILES) uses the FULL module code as the
                     ID/filename prefix (e.g. "demo"), not a separately
                     assigned 3-letter abbreviation as
                     MASTER-REGISTRY-SCHEMA.md §13 illustrates. This is a
                     deliberate simplification for this factory instance,
                     recorded once here so no per-module artifact needs
                     to re-justify it.
ENTITY-ID          : ENTITY-[MOD]-[3-digit seq]      e.g. ENTITY-DEMO-001
RULE-ID            : RULE-[MOD]-[3-digit seq]        e.g. RULE-DEMO-001
API-ID              : API-[MOD]-[3-digit seq]        e.g. API-DEMO-001
DBF-ID              : DBF-[MOD]-[3-digit seq]        e.g. DBF-DEMO-001
FIELD-ID            : FIELD-[MOD]-[3-digit seq]      e.g. FIELD-DEMO-001
ERR-ID              : ERR-[MOD]-[3-digit seq]        e.g. ERR-DEMO-001
TC-BE-ID            : TC-BE-[MOD]-[3-digit seq]      e.g. TC-BE-DEMO-001
```

## GOVERNANCE CONVENTIONS (inherited, not re-decided per module)
- No Workflow Engine anywhere by default (RULE-13, WORKFLOW-ENGINE-TIER
  = OFF) — a module requesting one records a Tier 1/Tier 2 exception in
  its own SRS/General Notes, never assumed.
- No Business Code Pattern by default (BUSINESS-CODE-DEFAULT) — applied
  only when an entity explicitly needs it.
- Module Governance Index / Pipeline Status Grid is maintained inline by
  every engine's REGISTRY step (project-registry.md Section 15) — no
  separate MGI file in this factory instance.

## KNOWLEDGE BASE (Section M reference — not applicable yet)
GOVERNANCE-CONFIG.md §2 notes an optional ERP Knowledge Base
("platform-standards.md Section M"), consulted only when Domain Identity
= ERP. This platform's only domain so far is GENERAL (see
domain/domain-profile.md) — no ERP Knowledge Base section is authored
here; add one only if/when an ERP domain is introduced.

══════════════════════════════════════════════════════════════════
*Maintained inline by every engine's completion protocol when a
convention changes; P-1 does not re-run per module.*
