# PROJECT REGISTRY — factory (single-project instance)
══════════════════════════════════════════════════════════════════
Registry Version   : 1.0.0
Registry Phase     : BOOTSTRAP
Registered Modules : 1 (DEMO — pass-1 in progress, P3.5 done)
Registered Entities: 1 confirmed (ENTITY-DEMO-001 Note)
Open AQ-IDs        : 0
Governance Decisions: 3 (GD-001..GD-003, inherited from GOVERNANCE-CONFIG.md)
Last Updated       : 2026-09-07 by P3.5 (backend-test-plan-demo.md)
══════════════════════════════════════════════════════════════════

Scope note: this factory instance runs a single implicit project (no
`_ecosystem/projects-index.md` / multi-project split — see
domain/domain-profile.md Open Items). This file is therefore the
whole registry, not one project's slice of a larger ecosystem. IDs
here are local to this factory.

## SCHEMA COMPLIANCE MAP
(per shared/MASTER-REGISTRY-SCHEMA.md §2, v2.3 — this registry uses its
own section numbering, kept from the earlier single-project template,
rather than Part B's literal 3-13 numbering; every canonical category
is still covered, mapped below)
══════════════════════════════════════════════════════════════════
This Registry's Section          │ Canonical Category
──────────────────────────────────┼──────────────────────────────
Section 2 — Module Index          │ CAT-2 (Module/Component Index)
Section 3 — Entity Ownership      │ CAT-3 (Entity/Data Object Ownership)
Section 4 — Shared Entity Decl.   │ CAT-4 (Shared Entity Declarations)
Section 5 — Table Registry        │ CAT-5 (Structural/Impl. Registry)
Section 6 — Global XM Index       │ CAT-6 (Cross-Component Dependency)
Section 9 — Event Log             │ CAT-9 (Change/Event History)
Section 10 — Domain Architecture  │ CAT-1 (architectural context)
Section 11 — Governance Decisions │ CAT-1 (conventions/decisions)
Section 12 — Open Questions       │ CAT-7 (Open Question/Escalation)
Section 15 — Pipeline Status/MGI  │ CAT-8 (Pipeline/Progress Status)
Header block (top of file)        │ CAT-1 (Registry Identity/Versioning)
══════════════════════════════════════════════════════════════════
Uncovered categories: none.

---

## SECTION 2 — MODULE INDEX

| Module | Domain | Scope (one line) | Prefix | Status |
|---|---|---|---|---|
| DEMO | General / Personal Productivity | Personal notes — title + content, full CRUD, single-owner | DEMO | IN PROGRESS (pass 1) |

---

## SECTION 3 — ENTITY OWNERSHIP REGISTRY

No ENTITY-IDs are assigned yet — Project 1 (SRS) is the sole owner of
ENTITY-ID assignment (SHARED-GOVERNANCE-RULES.md RULE-2). Candidate
entity noted here for traceability only, per P-1's own extraction
rules (Section 7 candidate format) — NOT a governance ID:

| ENTITY-ID / Cand. | Entity Name | Owner Module | Type | Status | Source |
|---|---|---|---|---|---|
| ENTITY-DEMO-001 | Note | DEMO | PRIVATE | CONFIRMED (P1, srs-demo.md A3) | brief: "عنوان + محتوى + CRUD كامل" |

---

## SECTION 4 — SHARED ENTITY DECLARATIONS

(none) — DEMO has no entities shared with any other module. No other
module exists yet in this factory instance.

---

## SECTION 5 — TABLE REGISTRY (CAT-5)

| Table Name | Owner Module | DBS-ID | ENTITY-ID Source |
|---|---|---|---|
| DEMO_NOTE | DEMO | DBS-DEMO-01 | ENTITY-DEMO-001 |

---

## SECTION 6 — GLOBAL XM (CROSS-MODULE) DEPENDENCY INDEX

(none) — DEMO is a single, self-contained module with no cross-module
dependency candidates identified in the brief.

---

## SECTION 9 — EVENT LOG

| Date | Event | Module | Detail |
|---|---|---|---|
| 2026-09-07 | ANALYSIS | — | domain/domain-profile.md authored (GENERAL identity, personal-productivity domain) |
| 2026-09-07 | BOOTSTRAP | — | P-1 bootstrap: project-registry.md + platform-standards.md created |
| 2026-09-07 | MODULE-REGISTERED | DEMO | Registered as CANDIDATE module in Section 2, pass 1 started |
| 2026-09-07 | P0 | DEMO | platform-summary.md + module-registry-demo.md + business-policies-demo.md produced; Module 1.1, Layer L1, Type Transactional, ROOT (no dependencies) |
| 2026-09-07 | P0.5 | DEMO | prd-demo.md produced; US-DEMO-001..005 (Create/List/Read/Update/Delete), all Source-traced to P0 outputs; 1 OPEN ITEM (cross-user sharing) not written as a story |
| 2026-09-07 | P1 | DEMO | srs-demo.md produced; ENTITY-DEMO-001 (Note) confirmed; RULE-DEMO-001..005; LOV-DEMO-001 (NOTE_STATUS); SCR-DEMO-001 (PATTERN-2/SIDE_DRAWER); API-DEMO-001..005; 0 open OQs |
| 2026-09-07 | review(P1) | DEMO | APPROVED after one REVISE→fix cycle (NOTE_STATUS disproportionate ERP lookup mechanism → fixed CHECK-constraint value set; noteId/notePk naming inconsistency fixed) |
| 2026-09-07 | P2 | DEMO | db-script-demo.md produced; DBS-DEMO-01; table DEMO_NOTE (9 DBF-IDs); no XM-IDs; NOTE_STATUS implemented as CHECK constraint (no MD_LOOKUP tables, per SRS deviation) |
| 2026-09-07 | review(P2) | DEMO | APPROVED after one REVISE→fix cycle (missing DB-level content-length CHECK constraint on DEMO_NOTE.CONTENT) |
| 2026-09-07 | P2.5 | DEMO | flow-diagram-demo.md + ui-ux-spec-demo.md produced; SCR-DEMO-001 (PATTERN-2, Side Drawer); reconciled cleanly against srs-demo.md B1-B4, no drift, no OQ raised; DRAFT status pending human approval (CONTRACT-11/12) — does not gate P3.1/P3.5; no new governance IDs (P2.5 owns none) |
| 2026-09-07 | P3.1 | DEMO | backend-execution-plan-demo.md produced; PLAN-DEMO-001; FIELD-0001..0009 (1:1 with DBF-0001..0009), ERR-0001..0005, QR-DEMO-0001..0005, DRV-DEMO-001..009; ALIGN-BE PASSED ✓; no XM-IDs (none exist for this module) |
| 2026-09-07 | review(P3.1) | DEMO | APPROVED after one REVISE→fix cycle (SVC+API ERRORS blocks duplicated Error Catalog message text, contradicting the artifact's own Option-A no-duplicate claim; API-DEMO-005 VALIDATIONS listed RULE-DEMO-004 with no matching ERR-ID, violating RULE-ERR-CARRY) |
| 2026-09-07 | P3.5 | DEMO | backend-test-plan-demo.md produced; TC-BE-DEMO-001..021 (21 TCs); 5/5 RULE-IDs, 5/5 API-IDs, 5/5 ERR-IDs covered; 4 mandatory scenarios applied/adapted, 4 N/A (documented); no per-engine review gate (P3.5 covered by the holistic gate) |

---

## SECTION 10 — DOMAIN ARCHITECTURE MAP

| Domain | Description | Prefix | Modules |
|---|---|---|---|
| General / Personal Productivity | Small, single-user record-keeping utilities (see domain/domain-profile.md) | (none — GENERAL domain, no ERP-style 3-letter domain prefix in use) | DEMO |

---

## SECTION 11 — GOVERNANCE DECISIONS (GD-ID)

| GD-ID | Decision | Rationale |
|---|---|---|
| GD-001 | BACKEND_STACK = SPRING_BOOT_JAVA, FRONTEND_STACK = REACT_TS_VITE, DB_TARGET = POSTGRESQL_16 | Per GOVERNANCE-CONFIG.md §3-5 (platform-wide stack declaration, inherited — not decided by this bootstrap) |
| GD-002 | WORKFLOW-ENGINE-TIER = OFF | Per GOVERNANCE-CONFIG.md §8 — no workflow infrastructure anywhere by default; DEMO has no approval-flow requirement |
| GD-003 | BUSINESS-CODE-DEFAULT = NOT-APPLIED-UNLESS-EXPLICIT | Per GOVERNANCE-CONFIG.md §9 — DEMO's Note entity does not request a business code |

---

## SECTION 12 — OPEN QUESTIONS (AQ-ID) — ARCHITECTURE-LEVEL

(none) — no unresolved ownership/boundary questions at bootstrap or at
DEMO's module registration. (Functional-level OQ-IDs, if any, are
raised and owned by Project 1 in srs-demo.md — see CONTRACT-3.)

---

## SECTION 15 — PIPELINE STATUS GRID / MODULE GOVERNANCE INDEX (MGI)

Per CONTRACT-6 — operational navigation only, not a truth layer;
downstream engines confirm against artifact content, not this table.

| Module | Pipeline Status | Attached Artifacts | Open Deps | Execution Readiness | LAST-VERIFIED | GOVERNANCE-STATE |
|---|---|---|---|---|---|---|
| DEMO | P3.5 done → entering holistic review (after-pass-1, backend set) | domain-profile.md (+DEMO inherit section), platform-summary.md, module-registry-demo.md, business-policies-demo.md, prd-demo.md, srs-demo.md, registry-srs-demo.md, db-script-demo.md, registry-db-demo.md, flow-diagram-demo.md, ui-ux-spec-demo.md, backend-execution-plan-demo.md, registry-exec-be-demo.md, backend-test-plan-demo.md, registry-test-be-demo.md | none | READY | 2026-09-07 | FULL |

---

*End of project-registry.md — maintained inline by every engine's
completion protocol (GOVERNANCE-CONFIG.md §1D.4 REGISTRY step) from
here on; P-1 does not run again per module.*
