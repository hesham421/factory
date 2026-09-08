# PROJECT REGISTRY — ERP Platform
══════════════════════════════════════════════════════════════════
Profile            : erp
Registry Version   : 1.1.0
Domain Profile     : domain/domain-profile.md v1
Last Updated       : 2026-09-08 by P-1
Modules registered : 1   Entity candidates : 1   Open items : 0
══════════════════════════════════════════════════════════════════

## SCHEMA COMPLIANCE MAP
| Section of this registry | Category (shared/REGISTRY-SCHEMA.md) |
|---|---|
| Identity & versioning | CAT-1 identity & conventions |
| Conventions & steering | CAT-1 identity & conventions |
| Module / component index | CAT-2 module index |
| Entity ownership | CAT-3 entity ownership |
| Shared entity declarations | CAT-4 shared declarations |
| Structural / implementation registry | CAT-5 structural registry |
| Cross-module dependency index | CAT-6 dependency indexes |
| Decision index | CAT-7 decision index |
| Pipeline / progress status | CAT-8 pipeline status |
| Change / event history | CAT-9 event history |

Uncovered: none

## IDENTITY & VERSIONING
- Platform: ERP Platform (`profiles/erp.yaml`, id `erp`).
- Registry version history: `1.0.0` → bootstrap (this run) → `1.1.0` (new module `DEMO` registered).
- Domain profile: `domain/domain-profile.md` v1 (FRESH).

## CONVENTIONS & STEERING
Copied verbatim from `domain/domain-profile.md` §7.

### Ubiquitous language
| Term | Definition | Do not say | Module code |
|---|---|---|---|
| Module (وحدة) | A bounded functional area with its own registry, entities and screens, identified by a module code. | — | — |
| Composite Screen (شاشة مركّبة) | Search + Entry (or Master + Detail, Wizard) treated as ONE screen with ONE SCR-ID. | — | — |
| XM (اعتماد بين وحدات) | A cross-module dependency (HARD-FK or SOFT-READ) declared by the consuming module. | — | — |
| LOV (قائمة قيم) | List of values loaded at runtime from the lookup module — never hardcoded. | — | — |
| Note (ملاحظة يومية) | A single free-text personal note record owned by the DEMO module: title + content + timestamp, CRUD only. | "task", "reminder", "document" | DEMO |
| Daily Notes (الملاحظات اليومية) | The DEMO module's one screen/feature: list, create, view, edit, delete notes. | "notebook system" | DEMO |

### Bounded contexts
| Context | Owns module codes | Boundary statement |
|---|---|---|
| organization | ORG, SEC, MDL | Tier-0 foundation: org structure, security, master lookups. |
| supply | PRC, INV | Procurement and inventory flows. |
| finance | FIN | Ledger, accounting, fiscal policy. |
| people | HR | Employees, payroll. |
| commercial | SLS, CTR | Sales and contracts. |
| platform-testing | DEMO | Pipeline-validation module only; no real business boundary. |

### Module prefixes
| Code | Display | Status |
|---|---|---|
| ORG | Organization | IN PROFILE |
| SEC | Security | IN PROFILE |
| MDL | Master Data Lookup | IN PROFILE |
| PRC | Procurement | IN PROFILE |
| FIN | Finance | IN PROFILE |
| HR | Human Resources | IN PROFILE |
| INV | Inventory | IN PROFILE |
| SLS | Sales | IN PROFILE |
| CTR | Contracts | IN PROFILE |
| DEMO | Demo / Pipeline Test | IN PROFILE |

### Identifier rules
IDs follow `{prefix}-{MOD}-{seq}` (seq width 3). Entity kinds:
`master, transactional, lookup, config, security`, plus the DEMO-only local
exception `simple` (domain-profile §5) for the Note entity — audit fields +
soft delete only, no bilingual name fields, no fiscal/status fields.

### Knowledge sources to cite
- `profiles/erp/knowledge/erp-domain-standards.md`

### ENFORCEMENT NOTES
- **E1** Every later artifact uses these terms verbatim; a synonym listed under "do not say" is a consistency finding at the pass gate (`gov.py analyze` checks registry ↔ artifact agreement).
- **E2** IDs follow `{prefix}-{MOD}-{seq}` (seq width 3) with the module codes of this section only.
- **E3** Entities are classified with the kinds `master, transactional, lookup, config, security` (DEMO's `simple` exception noted above).
- **E4** Sources to cite when a stage resolves an ambiguity: the knowledge sources listed here, then the domain-profile itself.
- **E5** Pipeline status per module (CAT-8) is maintained by the orchestrator from commits; this engine seeds new module rows as NOT STARTED.

## MODULE / COMPONENT INDEX
| Code | Display | Bounded context | Category | Core/extension | Status | Source |
|---|---|---|---|---|---|---|
| DEMO | Daily Notes (demo/test) | platform-testing | Pipeline validation | ext-name: pipeline-test | CANDIDATE | domain-profile §4 row 1 |

## ENTITY OWNERSHIP
| Candidate ref | Entity name | Owner module | Kind | PRIVATE/SHARED | Status | Source |
|---|---|---|---|---|---|---|
| CAND-DEMO-001 | Note (ملاحظة يومية) | DEMO | simple (DEMO-only exception, see steering) | PRIVATE | CANDIDATE | domain-profile §3, §7.1 |

## SHARED ENTITY DECLARATIONS
None yet — DEMO's Note entity is PRIVATE and has no consumers outside DEMO.

## STRUCTURAL / IMPLEMENTATION REGISTRY
None yet — filled by P2 / P3.1.

## CROSS-MODULE DEPENDENCY INDEX
None yet — DEMO declares no XM dependency in v1 (domain-profile §6, §8 decision 3).

## DECISION INDEX
| # | Decision | Status | Source |
|---|---|---|---|
| 1 | DEMO is a demo/test module, not a real ERP business module; ERP bilingual/governance conventions still apply, content stays trivial. | CONFIRMED | domain-profile §8 row 1 |
| 2 | DEMO's Note entity uses a documented `simple` kind exception instead of `master`/`transactional` conventions. | CONFIRMED | domain-profile §8 row 2 |
| 3 | DEMO has no cross-module (XM) dependency in v1. | CONFIRMED | domain-profile §8 row 3 |

## OPEN QUESTION INDEX
None.

## PIPELINE / PROGRESS STATUS
| Module | Version | Last committed stage | Last gate verdict | Delivered tracks | Tag |
|---|---|---|---|---|---|
| DEMO | v1 | P-1 (platform bootstrap) | — | — | — |

## CHANGE / EVENT HISTORY
| Date | Stage/tool | Module | Version | Event |
|---|---|---|---|---|
| 2026-09-08 | domain-profile | — | — | Domain profile v1 created (FRESH); platform = ERP Platform; DEMO added to `profiles/erp.yaml` module_prefixes ahead of P-1. |
| 2026-09-08 | P-1 | DEMO | v1 | BOOTSTRAP — extracted 1 module (DEMO), 1 entity candidate (Note), 0 XM candidates, 3 decisions confirmed, 0 open items; steering copied (6 terms, 6 contexts, 10 codes, 0 RESERVED). |
══════════════════════════════════════════════════════════════════
