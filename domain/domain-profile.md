# DOMAIN PROFILE — General / Personal Productivity
══════════════════════════════════════════════════════════════════
Domain Identity : GENERAL
Project         : DEFAULT (single-project factory instance — this factory
                  instance has not adopted the multi-project ecosystem
                  layer; see platform/projects-index.md)
Version         : 1
Current Release : General-Productivity@R1
Last Updated    : 2026-09-07
Status          : FRESH
══════════════════════════════════════════════════════════════════

## SCOPE
**In bounds:** small, general-purpose "personal productivity" software
modules built for a single authenticated owner per record — utilities such
as personal notes, personal to-do/checklist style records, and similar
lightweight owner-scoped CRUD tools. Each module is a self-contained set of
entities owned by the acting user, with standard create/read/update/delete
operations and simple field-level validation.

**Out of bounds:** enterprise resource planning modules (Finance, HR,
Procurement, ...), multi-tenant organization/department hierarchies,
approval workflows, cross-module financial or operational business logic,
and any capability that requires the ERP-flavored pattern library (Business
Code Pattern, Composite Screen Governance) — those stay unavailable by
default per GOVERNANCE-CONFIG.md §2, and are only turned on for a specific
future module by explicit request, never assumed for this domain.

This is deliberately a small domain, sized for the first module the factory
runs (DEMO — personal notes). It is expected to grow in place as more
general-purpose modules are added, rather than being replaced by an ERP
domain profile.

## PURPOSE
This factory instance's first modules are small personal-utility tools, not
ERP components. This domain exists so those modules can go through the same
governed pipeline (P0 → P3.1, review gates, split, deliver) as an ERP
platform would, without inheriting ERP-scale ceremony (multi-tenant roles,
approval chains, cross-module financial dependencies) that does not apply
to a single-owner utility module.

## RESPONSIBILITIES
- Owns general personal-productivity capabilities: CRUD over records that
  belong to one authenticated owner (the acting user).
- Owns the convention that every entity in this domain carries standard
  audit fields (created/updated timestamps, created-by user) and is
  filtered by owner at the application layer.
- Does **not** own identity/authentication itself — modules in this domain
  assume an already-authenticated user context (`ownerUserId`) is available
  to the backend; no module in this domain builds its own auth system.

## MAIN COMPONENTS
| # | Component | Category (user-defined) | Core/Ext? | Notes |
|---|-----------|--------------------------|-----------|-------|
| 1 | Personal Notes (DEMO) | Business | Core | Title + content CRUD, single-owner scoped. First module run through this factory instance. |

## GOVERNING RULES
- **No Workflow Engine** — WORKFLOW-ENGINE-TIER = OFF (GOVERNANCE-CONFIG.md
  §8) applies at full strength; no module in this domain introduces
  approval flows or a workflow engine without a formally recorded RULE-13
  exception (Tier 1 or Tier 2), and none is anticipated.
- **No Business Code Pattern by default** — BUSINESS-CODE-DEFAULT =
  NOT-APPLIED-UNLESS-EXPLICIT (GOVERNANCE-CONFIG.md §9); a business code
  field is only added to an entity in this domain on explicit request.
- **Owner-based access, not role-based** — every entity is scoped to its
  owning user (`ownerUserId` / equivalent). There is no multi-tenant
  organization hierarchy in this domain; "permissions" mean "is this
  record's owner," not a role/permission matrix.
- **Standard audit fields** — every entity carries `createdAt`,
  `updatedAt`, `createdBy` (owner) at minimum; soft-delete vs. hard-delete
  is a per-module SRS decision (DEMO uses soft status, see srs-demo.md A3).
- Stack: BACKEND_STACK = SPRING_BOOT_JAVA, FRONTEND_STACK = REACT_TS_VITE,
  DB_TARGET = POSTGRESQL_16 (GOVERNANCE-CONFIG.md §3-5) — unchanged from
  the platform default; this domain does not declare its own stack.

## RELATIONSHIPS WITH OTHER DOMAINS
None. This is currently the only domain in the platform. DEMO (the first
module) has no cross-module dependencies — no XM candidates, no SHARED
entities, no reuse imports from another project/domain.

## OPEN ITEMS
None blocking. When a second domain (e.g. an ERP domain) is added later,
this profile's "Relationships With Other Domains" section must be revisited
to declare any HARD/SOFT/Event relationship between the two.
══════════════════════════════════════════════════════════════════

---

## Module: DEMO

```
Module          : DEMO
Domain          : General / Personal Productivity (this file)
Prefix          : DEMO   (this factory's module-qualified naming scheme
                  uses the full module code as the ID/file-name prefix
                  rather than deriving a separate 3-letter abbreviation —
                  see the Assumptions note in this module's v1 hand-off)
Entered pass 1  : 2026-09-07
Brief (as given): "موديول بسيط لإدارة ملاحظات شخصية: عنوان + محتوى + CRUD
                  كامل" — a simple module for managing personal notes:
                  title + content, full CRUD.
```

**Inherits from the domain profile above, without modification:**
- Domain Identity: GENERAL (no ERP pattern library, no Business Code
  Pattern, no Workflow Engine).
- Owner-based access model (`ownerUserId`), standard audit fields.
- Stack: SPRING_BOOT_JAVA / REACT_TS_VITE / POSTGRESQL_16.

**DEMO-specific scope (confirmed for this module only):**
- One entity: Note — fields limited to a title and a content body plus
  standard audit/owner fields (exact field list, types, and constraints are
  P1/P2's decision, not fixed here).
- Full CRUD: Create, Read (single + list), Update, Delete.
- No sharing between users, no folders/tags, no attachments, no versioning
  of note content — kept intentionally minimal per the brief ("simple").
  Any of these would be a new module version (IFA), not part of v1.
