<!-- P0 stage output — governed by factory.yaml stages[P0]; see shared/GOVERNANCE-CORE.md -->
# PLATFORM SUMMARY — ERP Platform / منصة تخطيط موارد المؤسسات
══════════════════════════════════════════════════════════════════
Profile : erp   Domain profile : v1   Registry : v1.0.0
══════════════════════════════════════════════════════════════════

## OVERVIEW
One governed, bilingual (Arabic / English — عربي / إنجليزي) specification line for a
mid-size organization's back-office operations, across the ten modules already fixed
in `profiles/erp.yaml` (domain-profile §4). This run converges module 2.2 — Finance
(المحاسبة / المالية, `FIN`) — using a dedicated General Ledger vision document
(`general-accounting-system-plan-en.md`) as its Phase-2 source, in addition to the
platform's domain-profile and project-registry.

## MODULES
| #   | Code | Module (en / ar) | Bounded context | Layer | Type | Depends on | Status |
|-----|------|-------------------|------------------|-------|------|------------|--------|
| 1.1 | ORG  | Organization / التنظيم | organization | L1 | master data | ROOT | NEW |
| 1.2 | SEC  | Security / الأمان والصلاحيات | organization | L1 | reference | ROOT | NEW |
| 1.3 | MDL  | Master Data Lookup / البيانات المرجعية | organization | L1 | reference | ROOT | NEW |
| 2.1 | PRC  | Procurement / المشتريات | supply | L2 | transactional | INV (HARD), FIN (SOFT→HARD), ORG, SEC, MDL (SOFT) | NEW |
| 2.2 | FIN  | Finance / المحاسبة والمالية | finance | L2 | engine | NONE — isolated by design (see Resolved Decision #1) | NEW |
| 2.3 | INV  | Inventory / المخزون | supply | L2 | transactional | ORG, SEC, MDL (SOFT) | NEW |
| 3.1 | SLS  | Sales / المبيعات | commercial | L3 | transactional | INV (HARD), FIN (SOFT→HARD), ORG, SEC, MDL (SOFT) | NEW |
| 3.2 | CTR  | Contracts / العقود | commercial | L3 | transactional | SLS (SOFT), PRC (SOFT), ORG, SEC, MDL (SOFT) | NEW |
| 3.3 | HR   | Human Resources / الموارد البشرية | people | L3 | master data | ORG (HARD), FIN (SOFT→HARD), SEC, MDL (SOFT) | NEW |
| 4.1 | DEMO | Demo / Pipeline Test / تجريبي - اختبار خط الأنابيب | platform-testing | L4 | reference | NONE — isolated by design | NEW |

Status: NEW (Phase 2 produces) · EXISTING (Phase 2 extends) · EXCEPTION (read as-is)
Numbering: [tier].[sequence within tier] — the user requests Phase 2 by this number.
This run performs Phase 2 for **2.2 FIN** only; the other nine remain NEW (pending, not yet requested).

## DEPENDENCY MAP
Build order: Tier 1 [ORG, SEC, MDL] → Tier 2 [PRC, FIN, INV] → Tier 3 [SLS, CTR, HR] → Tier 4 [DEMO, isolated]

Key dependencies (one line each):
  PRC → HARD → INV : goods receipt updates stock
  SLS → HARD → INV : order fulfillment consumes stock
  PRC → SOFT→HARD → FIN : procurement postings arrive as canonical accounting events
  SLS → SOFT→HARD → FIN : sales postings arrive as canonical accounting events
  HR  → SOFT→HARD → FIN : payroll postings arrive as canonical accounting events
  HR  → HARD → ORG : employees belong to an org unit
  (ORG, SEC, MDL) ← SOFT ← (PRC, INV, SLS, CTR, HR) : structure, permissions, lookups — **FIN is exempt** (Resolved Decision #1)
  CTR → SOFT → SLS, PRC : contracts reference sales/procurement documents
  FIN : receives data only through its own generic canonical-event contract (owned by
        the out-of-scope Event consumer); it declares no XM dependency on any platform
        module and none is declared on it — other modules' obligation to emit a
        canonical event is recorded on *their* side (project-registry XM-CAND-003/004/005).

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
|---|---|
| Workflow / BPM engine | profile: `forbidden` (`profiles/erp.yaml → conventions.workflow_engine`) — permanent, platform-wide |
| Multi-currency, multi-ledger/multi-entity, intercompany entries, statistical accounts, multi-pattern fiscal calendar, attachments on entries | FIN vision document §12 — explicit v1 exclusion; reconsider as a FIN v2+ scope item |
| The Business Module, the Event consumer, the AQ/RabbitMQ transport layer | FIN vision document §0, §12 — each has its own separate governance line, out of FIN's scope |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Does FIN follow the platform default (SOFT-READ on ORG/SEC/MDL for structure, permissions, lookups, per project-registry XM-CAND-007) or the isolated design its own vision document demands (dedicated reference-data tables, fully independent RBAC, no read/write to any host-system table)? | Honor the FIN vision document's explicit, repeated design (§0, §2.1, §8.1, §10 — framed as "Governing rule" / "Decision (best practice)", not an oversight): FIN is a self-contained, pluggable module with **no** dependency on ORG/SEC/MDL; a documented exception to the general XM-CAND-007 row, carried into FIN's own module registry as `DEPENDENCIES: NONE — ROOT: YES` | **Recommended and adopted for this draft** — flagged for explicit confirmation at the `prd-approval` gate; the user may instead choose the platform-shared default, which reverts FIN to a normal Tier-2 dependent module | FIN vision document §0, §2.1, §8.1, §10; `profiles/erp/knowledge/erp-domain-standards.md` §5; project-registry CAT-6 XM-CAND-007 |
| 2 | Narrative language for FIN's pipeline documents — full Arabic-primary narrative (profile default, `languages.primary: ar`) or English narrative with bilingual (ar/en) names, titles and policy statements? | English narrative + genuine bilingual (ar/en) names/titles/policy statements — the same pragmatic style already used for `project/domain-profile.md` (there scoped to the platform bootstrap only); extended here to FIN for speed and internal consistency, while still satisfying `languages.require_all` (both scripts present) | Recommended and adopted for this draft — confirm or reject at gate | domain-profile §8 decision 3 (precedent, not a binding rule for production modules); `profiles/erp.yaml → languages` |

## OPEN ITEMS
None — both points above were closed in-dialogue with a recommended answer per §5;
carried into the RESOLVED DECISIONS tables of `module-registry-fin.md` and
`business-policies-fin.md` for explicit user confirmation at the `prd-approval` gate,
not left as an external question.

## NEXT STEP
Reply with a plain instruction to adjust, or with a module number to start Phase 2 for
another module (this run already completed Phase 2 for 2.2 FIN).
