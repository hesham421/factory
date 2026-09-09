<!-- P-1 stage output — governed by factory.yaml stages[P-1]; see shared/REGISTRY-SCHEMA.md -->
# PROJECT REGISTRY — ERP Platform
══════════════════════════════════════════════════════════════════
Profile            : erp
Registry Version   : 1.0.0
Domain Profile     : project/domain-profile.md v1
Last Updated       : 2026-09-09 by P-1
Modules registered : 10   Entity candidates : 0   Open items : 0
══════════════════════════════════════════════════════════════════

## SCHEMA COMPLIANCE MAP
| Section of this registry | Category (shared/REGISTRY-SCHEMA.md) |
|---|---|
| Identity & versioning | CAT-1 |
| Conventions & steering | CAT-1 |
| Module / component index | CAT-2 |
| Entity ownership | CAT-3 |
| Shared entity declarations | CAT-4 |
| Structural / implementation registry | CAT-5 |
| Cross-module dependency index | CAT-6 |
| Open question index | (none yet) |
| Decision index | CAT-7 |
| Pipeline / progress status | CAT-8 |
| Change / event history | CAT-9 |

Uncovered: none.

## Identity & versioning
Platform: `erp` (ERP Platform). Registry is the orchestrator-maintained index for
this platform; humans never edit it by hand (shared/REGISTRY-SCHEMA.md).

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-09-09 | Initial bootstrap from `project/domain-profile.md` v1 |

## Conventions & steering (copied verbatim from domain-profile §7)

**7.1 Ubiquitous language** — `profiles/erp.yaml → vocabulary.glossary` (Module,
Composite Screen, XM, LOV). No new domain term added at bootstrap.

**7.2 Bounded contexts** — `profiles/erp.yaml → vocabulary.bounded_contexts`:
organization [ORG, SEC, MDL] · supply [PRC, INV] · finance [FIN] · people [HR] ·
commercial [SLS, CTR] · platform-testing [DEMO].

**7.3 Module prefixes** — all ten codes below are IN PROFILE
(`profiles/erp.yaml → vocabulary.module_prefixes`); none PROPOSED, none RESERVED.

**7.4 Identifier rules** — `{prefix}-{MOD}-{seq}`, seq width 3
(`factory.yaml → ids`). Entity kinds: `master, transactional, lookup, config, security`.

**7.5 Knowledge sources to cite** — `profiles/erp/knowledge/erp-domain-standards.md`;
research: [NetSuite — ERP Modules](https://www.netsuite.com/portal/resource/articles/erp/erp-modules.shtml),
[Panorama Consulting — ERP Modules List](https://www.panorama-consulting.com/heres-an-erp-modules-list-to-inform-your-erp-selection/).

**ENFORCEMENT NOTES**
- **E1** Every later artifact uses the terms above verbatim; a rejected synonym is a consistency finding at the pass gate.
- **E2** IDs follow `{prefix}-{MOD}-{seq}` (seq width 3) with the module codes registered below only.
- **E3** Entities are classified as `master, transactional, lookup, config, security`.
- **E4** Ambiguity-resolution sources, in order: knowledge files above, then `project/domain-profile.md`.
- **E5** Pipeline status per module (below) is maintained by the orchestrator from commits; seeded here as NOT STARTED.

## Module / component index (CAT-2)

| Module code | Display name | Bounded context | Category | Core/extension | Versions | Last committed stage | Status | Source |
|---|---|---|---|---|---|---|---|---|
| `ORG` | Organization | organization | Foundation | Core | none | — | CANDIDATE | domain-profile §4 |
| `SEC` | Security | organization | Foundation | Core | none | — | CANDIDATE | domain-profile §4 |
| `MDL` | Master Data Lookup | organization | Foundation | Core | none | — | CANDIDATE | domain-profile §4 |
| `PRC` | Procurement | supply | Business | Core | none | — | CANDIDATE | domain-profile §4 |
| `INV` | Inventory | supply | Business | Core | none | — | CANDIDATE | domain-profile §4 |
| `FIN` | Finance | finance | Business | Core | none | — | CANDIDATE | domain-profile §4 |
| `HR` | Human Resources | people | Business | Core | none | — | CANDIDATE | domain-profile §4 |
| `SLS` | Sales | commercial | Business | Core | none | — | CANDIDATE | domain-profile §4 |
| `CTR` | Contracts | commercial | Business | Core | none | — | CANDIDATE | domain-profile §4 |
| `DEMO` | Demo / Pipeline Test | platform-testing | Non-production | Extension | none | — | CANDIDATE | domain-profile §4 |

## Entity ownership (CAT-3)
None yet — no `P1` (SRS) run has occurred for any module.

## Shared entity declarations (CAT-4)
None yet.

## Structural / implementation registry (CAT-5)
None yet — filled by `P2` (`DBF` owner) / `P3.1` (`API` owner) per module version.

## Cross-module dependency index (CAT-6)

### Backend (XM candidates)
| Candidate ref | Kind | From module | To module | Consumes | Status | Evidence |
|---|---|---|---|---|---|---|
| XM-CAND-001 | HARD-FK? | PRC | INV | goods receipt updates stock | CANDIDATE | domain-profile §6 |
| XM-CAND-002 | HARD-FK? | SLS | INV | order fulfillment consumes stock | CANDIDATE | domain-profile §6 |
| XM-CAND-003 | SOFT-READ?→HARD-FK? | PRC | FIN | postings into ledger | CANDIDATE | domain-profile §6 |
| XM-CAND-004 | SOFT-READ?→HARD-FK? | SLS | FIN | postings into ledger | CANDIDATE | domain-profile §6 |
| XM-CAND-005 | SOFT-READ?→HARD-FK? | HR | FIN | postings into ledger | CANDIDATE | domain-profile §6 |
| XM-CAND-006 | HARD-FK? | HR | ORG | employee belongs to org unit | CANDIDATE | domain-profile §6 |
| XM-CAND-007 | SOFT-READ | (all business modules) | ORG, SEC, MDL | structure, permissions, lookups | CANDIDATE | domain-profile §6 |
| XM-CAND-008 | SOFT-READ? | CTR | SLS | contract references sales documents | CANDIDATE | domain-profile §6 |
| XM-CAND-009 | SOFT-READ? | CTR | PRC | contract references procurement documents | CANDIDATE | domain-profile §6 |

`DEMO` deliberately has none — an isolated pipeline-test island by design (domain-profile §6, §8 decision 2).
Exact tiering / kind confirmation is settled per-module at `P0`; formal `XM` IDs are assigned at `P3.1` (see shared/XM-PROTOCOL.md).

### Frontend (UXD index)
None yet — no frontend (`P3.2`) run has occurred for any module.

## Open question index
None. domain-profile §10 recorded none.

## Decision index (CAT-7)

| # | Decision | Status | Source |
|---|---|---|---|
| 1 | Platform module composition = the ten domains already fixed in `profiles/erp.yaml` | ACCEPTED | domain-profile §8 #1 |
| 2 | `DEMO` is the designated isolated pipeline-smoke-test module; this bootstrap's triggering idea ("a very simple notes feature") is the kind of scenario it exists for | ACCEPTED | domain-profile §8 #2 |
| 3 | This bootstrap's narrative documents use English narrative + genuine Arabic terms/headings (scoped exception, not a profile change) | ACCEPTED | domain-profile §8 #3 |
| 4 | This factory is analysis-only; it never writes or runs application code | ACCEPTED (inherited fact) | factory.yaml → factory.boundary |

No ADR was required — every decision above was confirmed by the user, not decided by an engine.

## Pipeline / progress status (CAT-8)

| Module | Last committed stage | Last gate verdict | Delivered tracks | Tag |
|---|---|---|---|---|
| `ORG` | — | — | — | — |
| `SEC` | — | — | — | — |
| `MDL` | — | — | — | — |
| `PRC` | — | — | — | — |
| `INV` | — | — | — | — |
| `FIN` | — | — | — | — |
| `HR` | — | — | — | — |
| `SLS` | — | — | — | — |
| `CTR` | — | — | — | — |
| `DEMO` | — | — | — | — |

All NOT STARTED — no module version has been created yet (`gov.py version --new`).

## Change / event history (CAT-9)

| Date | Stage/tool | Module | Version | Event |
|---|---|---|---|---|
| 2026-09-09 | domain-profile | — | — | Platform domain profile created (10 modules, 9 XM candidates, 4 decisions) |
| 2026-09-09 | BOOTSTRAP (P-1) | — | — | Registry created: 10 modules registered, 0 entity candidates, 9 XM candidates, 4 decisions, 0 open items |
══════════════════════════════════════════════════════════════════
