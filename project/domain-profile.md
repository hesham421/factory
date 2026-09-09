<!-- domain-profile stage output — governed by factory.yaml stages[domain-profile]; see shared/GOVERNANCE-CORE.md -->
# DOMAIN PROFILE — ERP Platform / منصة تخطيط موارد المؤسسات
══════════════════════════════════════════════════════════════════
Profile         : erp (ERP Platform)
Version         : 1            (per shared/VERSIONING.md)
Last Updated    : 2026-09-09
Status          : FRESH
Research        : 2 sources cited (block 9)
══════════════════════════════════════════════════════════════════

## 1. SCOPE / النطاق

**In bounds:**
- The ten domains already declared in `profiles/erp.yaml → vocabulary.module_prefixes`:
  organization, security, master-data lookup, procurement, finance, HR, inventory,
  sales, contracts, and a dedicated pipeline-test module (see block 4).
- Bilingual delivery (Arabic + English) on every module, per `profiles/erp.yaml → languages`.
- The stack already committed to in the profile: Spring Boot (Java) backend,
  PostgreSQL 16 / Oracle 19c dual-dialect persistence, React+TS frontend, Flutter
  mobile shell (`profiles/erp.yaml → stack`).

**Out of bounds:**
- Any workflow/BPM engine — explicitly `forbidden` (`profiles/erp.yaml → conventions.workflow_engine`).
- Writing or running application code, or auditing a consumer repo's code — this
  factory is `boundary: analysis-only` (`factory.yaml → factory.boundary`); it stops
  at delivering execution plans to the backend/frontend consumer repos.
- Production business data or real cross-module dependencies through the
  pipeline-test module (block 6) — it exists only to exercise the pipeline
  mechanics safely.

## 2. PURPOSE / الغرض

To give a mid-size organization one governed, traceable, bilingual specification
line for its core back-office operations — organizational structure, security,
procurement, finance, HR, inventory, sales and contracts — so every requirement,
entity, API and screen downstream traces back to a confirmed business policy,
instead of being decided ad hoc per module. A dedicated, isolated test module
(block 6) lets the factory's own mechanics (stages, gates, split, delivery) be
exercised end-to-end without touching real business modules.

## 3. RESPONSIBILITIES / المسؤوليات

| Bounded context | Owns | Responsibility |
|---|---|---|
| organization | ORG, SEC, MDL | Org structure, branches/departments, security/permissions, shared reference (lookup) data — the foundation every other context depends on |
| supply | PRC, INV | Sourcing/vendors and warehousing/stock |
| finance | FIN | General ledger, fiscal periods, postings originated by other contexts |
| people | HR | Employee master data, payroll-adjacent records |
| commercial | SLS, CTR | Customers/orders and contracts/agreements |
| platform-testing | DEMO | Pipeline smoke-testing only — no business responsibility |

## 4. MAIN COMPONENTS / المكونات الرئيسية

| # | Component (English) | المكون (عربي) | Module code | Bounded context | Category | Core / extension |
|---|---|---|---|---|---|---|
| 1 | Organization | التنظيم | `ORG` | organization | Foundation | Core |
| 2 | Security | الأمان والصلاحيات | `SEC` | organization | Foundation | Core |
| 3 | Master Data Lookup | البيانات المرجعية | `MDL` | organization | Foundation | Core |
| 4 | Procurement | المشتريات | `PRC` | supply | Business | Core |
| 5 | Inventory | المخزون | `INV` | supply | Business | Core |
| 6 | Finance | المحاسبة / المالية | `FIN` | finance | Business | Core |
| 7 | Human Resources | الموارد البشرية | `HR` | people | Business | Core |
| 8 | Sales | المبيعات | `SLS` | commercial | Business | Core |
| 9 | Contracts | العقود | `CTR` | commercial | Business | Core |
| 10 | Demo / Pipeline Test | تجريبي - اختبار خط الأنابيب | `DEMO` | platform-testing | Non-production | Extension |

Codes, bounded contexts and every glossary term are `profiles/erp.yaml → vocabulary`
data, referenced here rather than restated (`project/README.md`) — this table adds
only the core/extension classification and the one-line role from block 3.

## 5. GOVERNING RULES / القواعد الحاكمة

| Rule | Source |
|---|---|
| No workflow engine anywhere in the platform | `profiles/erp.yaml → conventions.workflow_engine` (user-set, in profile) |
| Every screen is one composite screen (Search+Entry / Master+Detail / Wizard) with one `SEC_PAGES` row | `profiles/erp.yaml → conventions.composite_screen`, `security_model` |
| Gateway permission action is `VIEW` — no other permission applies without it | `profiles/erp.yaml → conventions.security_model.gateway_action` |
| Document numbers always come from the platform numbering engine, never generated in a module | `profiles/erp.yaml → conventions.numbering` |
| All list-of-values are runtime-loaded from `MDL`, never hardcoded | `profiles/erp.yaml → conventions.lookups` |
| Soft delete only (`isActiveFl`); four audit fields on every table | `profiles/erp.yaml → stack.db.naming`, `engines` KB defaults |
| Modular decomposition by business function, one bounded context can own several module codes | Research R1 (block 9) — standard ERP practice |

## 6. RELATIONSHIPS WITH OTHER DOMAINS / العلاقات بين المكونات

| This component | Depends on | Kind | Direction | Stated by |
|---|---|---|---|---|
| PRC | INV | HARD-FK | PRC → INV (goods receipt updates stock) | user (this session) |
| SLS | INV | HARD-FK | SLS → INV (order fulfillment consumes stock) | user (this session) |
| PRC, SLS, HR | FIN | SOFT-READ→HARD-FK | postings flow into FIN's ledger | user (this session) |
| HR | ORG | HARD-FK | employees belong to an org unit | user (this session) |
| ORG, SEC, MDL | (all business modules) | SOFT-READ | every business module reads structure, permissions and lookups | user (this session) |
| CTR | SLS, PRC | SOFT-READ | contracts reference sales/procurement documents | user (this session) |
| DEMO | none | — | isolated by design — never a source or target of a real `XM` record (block 8, decision 2) | user (this session) |

Directions and kinds follow `factory.yaml → markers.kinds` (`HARD-FK` only downward
in tier, `SOFT-READ` any direction) — the exact tiering is settled per-module at `P0`,
not here; this block only records which pairs are related and why.

## 7. STEERING (read verbatim by every later stage)

### 7.1 Ubiquitous language
Full glossary: `profiles/erp.yaml → vocabulary.glossary` (Module, Composite Screen,
XM, LOV). No new domain term is added by this bootstrap; module display names and
Arabic labels are in block 4.

### 7.2 Bounded contexts
`profiles/erp.yaml → vocabulary.bounded_contexts` — six contexts, unchanged, referenced
in blocks 3 and 6.

### 7.3 Module prefixes proposal
All ten codes used above are already `profiles/erp.yaml → vocabulary.module_prefixes`
— **IN PROFILE**. Nothing PROPOSED; `P-1` may start immediately.

### 7.4 Identifier rules
`{prefix}-{MOD}-{seq}`, seq width 3 (`factory.yaml → ids`). Entity kinds:
`master, transactional, lookup, config, security` (`profiles/erp.yaml → vocabulary.entity_kinds`).
No domain-specific atom added by this profile.

### 7.5 Knowledge sources to cite
- `profiles/erp/knowledge/erp-domain-standards.md`
- research sources in block 9

## 8. RESOLVED DECISIONS

| # | Point | Decision | Recommended by dialogue? | Confirmed by user | Sources |
|---|---|---|---|---|---|
| 1 | What is this platform's module composition? | The ten domains already fixed in `profiles/erp.yaml` (block 4) — no new module invented at bootstrap | Yes — matches standard ERP taxonomy (R1) | Yes (this session) | Research block 9 |
| 2 | How should the pipeline itself be validated without risking real business modules? | Use the existing `DEMO` module as an isolated, no-XM pipeline-test island; this bootstrap's triggering idea ("a very simple notes feature") is exactly the kind of throwaway scenario `DEMO` exists for (`profiles/erp.yaml → vocabulary.keyword_map.DEMO`) | Yes | Yes (this session) | `profiles/erp.yaml` |
| 3 | Narrative language for this bootstrap document | English narrative, with genuine Arabic for headings/module names/glossary labels (satisfies `languages.require_all` presence check) rather than a fully Arabic-primary narrative — a scoped exception for this pipeline-smoke-test bootstrap, not a change to the profile's stated convention for production modules | Presented as a trade-off (speed vs. full fidelity) | Yes (this session) | user instruction |
| 4 | Does this factory ever write application code? | No — `analysis-only`; this and every later stage produce specs/plans delivered to separate consumer repos | N/A — inherited fact from `factory.yaml` | Acknowledged | `factory.yaml → factory.boundary` |

## 9. RESEARCH LOG

| # | Point | What established systems do | Source(s) | Used in |
|---|---|---|---|---|
| 1 | Modular decomposition (R1) | Mainstream ERP suites decompose into finance, HR/workforce, procurement, inventory/supply-chain, sales/order management as core modules, sharing one database, with cross-module postings (e.g. a purchase updates both inventory and finance) | [ERP Modules: Types, Features & Functions](https://www.netsuite.com/portal/resource/articles/erp/erp-modules.shtml) (NetSuite, accessed 2026-09-09) | Blocks 3, 4, 5, 6 |
| 2 | Module coverage checklist | A representative ERP module list used for platform-selection scoping: finance, procurement, inventory, HR, sales/CRM, plus supporting/foundation modules | [ERP Modules List for Your ERP Selection Project](https://www.panorama-consulting.com/heres-an-erp-modules-list-to-inform-your-erp-selection/) (Panorama Consulting, accessed 2026-09-09) | Block 4 |

## 10. OPEN ITEMS

None. `DEMO`'s isolation (block 6, row 7) and the language exception (block 8,
decision 3) are recorded as resolved decisions, not open points.
══════════════════════════════════════════════════════════════════
