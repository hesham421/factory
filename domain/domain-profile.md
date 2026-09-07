# DOMAIN PROFILE — General / Personal Productivity
══════════════════════════════════════════════════════════════════
Domain Identity : GENERAL
Version         : 1
Last Updated    : 2026-09-07
Status          : FRESH
══════════════════════════════════════════════════════════════════

Note on scope (this factory instance): this platform is a single,
git-native governance factory (no multi-project ecosystem layer —
no `[ECO]/projects-index.md`, no per-project `project-registry.md`
split, no Core/Extension/Model version-ledger). `Project` and
`Current Release` fields from the v4.0 domain-profile format are
therefore not tracked separately; the factory repo itself is the one
project, and this file's own `Version` line is the only version this
instance carries. If a second, unrelated domain is ever introduced
into this factory, this simplification should be revisited.

## SCOPE

In bounds: small, general-purpose productivity and personal-utility
modules — record-keeping tools a single authenticated user manages
for themselves (e.g. personal notes, personal task lists, personal
bookmarks). Full CRUD over simple, self-contained entities with
standard audit fields and owner-based access (a user only ever sees
and edits their own records).

Out of bounds: multi-tenant organizational workflows, approval
chains, financial/inventory/procurement logic, cross-user sharing or
collaboration features, complex role/permission hierarchies, and any
ERP-style business process. This is deliberately NOT an ERP domain —
Business Code Pattern and Composite Screen Governance (CORE-9) are
NOT applied by default here (GOVERNANCE-CONFIG.md §2), and are only
invoked if a future module explicitly requests one of them.

## PURPOSE

To give one person a small, well-governed set of personal utility
tools — starting with personal note-taking — without pulling in the
organizational/business machinery this factory's governance rules
were originally written for. The domain exists to prove out (and
host) genuinely small modules end to end, analyzed with the same
rigor as an ERP module but sized to their actual scope.

## RESPONSIBILITIES

- Own simple, single-user record types (title/content-style entities)
  with full Create/Read/Update/Delete.
- Own standard audit trail fields (created/updated by + at) and
  soft-delete/active-flag conventions consistent with the platform's
  declared stack (GOVERNANCE-CONFIG.md §3 DB_TARGET, §4 BACKEND_STACK).
- Own owner-based (single-user) access control for its own entities.
  Does NOT own multi-user sharing, roles, or approval logic — a
  module needing those is out of this domain's scope (see SCOPE).

## MAIN COMPONENTS

| # | Component | Category (user-defined) | Core/Ext? | Notes |
|---|-----------|--------------------------|-----------|-------|
| 1 | Personal Notes | Business | Core | First module (MOD=DEMO): title + content, full CRUD, single-owner |

## GOVERNING RULES

- No Workflow Engine of any kind (RULE-13 default OFF, confirmed by
  GOVERNANCE-CONFIG.md §8 WORKFLOW-ENGINE-TIER = OFF) — a personal
  CRUD tool has no approval flow.
- No Business Code Pattern by default (GOVERNANCE-CONFIG.md §9
  BUSINESS-CODE-DEFAULT = NOT-APPLIED-UNLESS-EXPLICIT) — records in
  this domain do not need human-readable business codes unless a
  future module explicitly asks for one.
- Every entity is owned by exactly one user (`ownerUserId` or
  equivalent) — no entity in this domain is shared across users by
  default.
- Standard stack only (GOVERNANCE-CONFIG.md §3-6): PostgreSQL 16 /
  Spring Boot Java / React+TS+Vite. No stack substitution.

## RELATIONSHIPS WITH OTHER DOMAINS

None yet — this is the first domain and first module in this factory
instance. No HARD/SOFT/Event relationships exist to declare.

## OPEN ITEMS

| Field | Status | Note |
|---|---|---|
| Multi-project ecosystem layer (Project field, version-ledger.md, Domain Releases) | OPEN | Not instantiated — this factory runs a single implicit project. Revisit if a second, genuinely separate domain/project is added. |
══════════════════════════════════════════════════════════════════

## Module: DEMO

```
Inherits from      : this domain-profile.md (GENERAL identity)
Entered pass 1     : 2026-09-07
Brief (as given)   : "موديول بسيط لإدارة ملاحظات شخصية: عنوان + محتوى + CRUD كامل"
                     (EN gloss: a simple module for managing personal
                     notes — title + content, full CRUD)
Scope inherited    : SCOPE / GOVERNING RULES above apply in full —
                     single-owner records, no workflow, no Business
                     Code Pattern, standard stack only.
Component          : Main Components row #1 (Personal Notes)
```
