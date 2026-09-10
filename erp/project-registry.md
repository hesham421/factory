# PROJECT REGISTRY — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile            : erp
Registry Version   : 1.0.0
Domain Profile     : erp/domain-profile.md v1
Last Updated       : 2026-09-10 by P-1
Modules registered : 9   Entity candidates : 0   Open items : 0
══════════════════════════════════════════════════════════════════

## SCHEMA COMPLIANCE MAP
| Section of this registry | Category (shared/REGISTRY-SCHEMA.md) |
|---|---|
| IDENTITY & VERSIONING | CAT-1 identity & conventions |
| CONVENTIONS & STEERING | CAT-1 identity & conventions |
| MODULE / COMPONENT INDEX | CAT-2 module index |
| ENTITY OWNERSHIP | CAT-3 entity ownership |
| SHARED ENTITY DECLARATIONS | CAT-4 shared declarations |
| STRUCTURAL / IMPLEMENTATION REGISTRY | CAT-5 structural registry |
| CROSS-MODULE DEPENDENCY INDEX | CAT-6 dependency indexes |
| DECISION INDEX | CAT-7 decision index |
| PIPELINE / PROGRESS STATUS | CAT-8 pipeline status |
| CHANGE / EVENT HISTORY | CAT-9 event history |
Uncovered: none

## IDENTITY & VERSIONING
| Field | Value |
|---|---|
| Profile | erp — ERP Platform |
| Registry version | 1.0.0 |
| Domain profile source | erp/domain-profile.md v1 |

### Version history
| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-09-10 | Initial bootstrap from erp/domain-profile.md v1 (BOOTSTRAP event, see CHANGE/EVENT HISTORY) |

## CONVENTIONS & STEERING
(copied verbatim from `erp/domain-profile.md` §7 — the authoritative source; this section
mirrors it for engines that read only the registry)

### Ubiquitous language
See `erp/domain-profile.md` §7.1 for the full bilingual (ar/en) term table — copied verbatim,
not restated here to avoid drift; cite as `[domain-profile §7.1]`.

### Bounded contexts
| Context | Owns module codes | Boundary statement |
|---|---|---|
| organization | ORG, SEC, MDL | Foundational capabilities (Tier 0) every other context depends on |
| supply | PRC, INV | Supply and inventory flows (out of scope this batch) |
| finance | FIN | General ledger; consumes organization, produces nothing back to it |
| people | HR | Human resources (out of scope this batch) |
| commercial | SLS, CTR | Sales and contracts (out of scope this batch) |

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

### Identifier rules
`{prefix}-{MOD}-{seq}` — seq width 3 (`factory.ids.pattern`, `factory.ids.seq_width`).
Entity kinds: master, transactional, lookup, config, security.

### ENFORCEMENT NOTES
- **E1** Every later artifact uses the terms of `domain-profile.md §7.1` verbatim; a synonym
  listed under "do not say" is a consistency finding at the pass gate (`gov.py analyze`
  checks registry ↔ artifact agreement).
- **E2** IDs follow `{prefix}-{MOD}-{seq}` (seq width 3) with the module codes of this section only.
- **E3** Entities are classified with the kinds: master, transactional, lookup, config, security.
- **E4** Sources to cite when a stage resolves an ambiguity: `profiles/erp/knowledge/erp-domain-standards.md`,
  then `erp/domain-profile.md` itself, then the three module plans (`new project/*-plan-en.md`)
  named in `domain-profile.md §7.5`.
- **E5** Pipeline status (below) is maintained by the orchestrator from commits; seeded here as NOT STARTED.

## MODULE / COMPONENT INDEX
| # | Code | Module | Bounded context | Category | Core/ext | Status | Source |
|---|---|---|---|---|---|---|---|
| 1 | SEC | Security | organization | Foundation | Core | CANDIDATE — this batch, first | domain-profile §4 row 1 |
| 2 | MDL | Master Data Lookup | organization | Foundation | Core | CANDIDATE — this batch, second | domain-profile §4 row 2 |
| 3 | FIN | Finance (General Ledger) | finance | Business — Tier 1 | Core | CANDIDATE — this batch, third | domain-profile §4 row 3 |
| 4 | ORG | Organization | organization | Foundation | — | RESERVED — not this batch | domain-profile §4 row 4; profile |
| 5 | PRC | Procurement | supply | Business — Tier 1 | — | RESERVED — not this batch | domain-profile §4 row 5; profile |
| 6 | HR | Human Resources | people | Business — Tier 2 | — | RESERVED — not this batch | domain-profile §4 row 6; profile |
| 7 | INV | Inventory | supply | Business — Tier 1 | — | RESERVED — not this batch | domain-profile §4 row 7; profile |
| 8 | SLS | Sales | commercial | Business — Tier 2 | — | RESERVED — not this batch | domain-profile §4 row 8; profile |
| 9 | CTR | Contracts | commercial | Business — Tier 2 | — | RESERVED — not this batch | domain-profile §4 row 9; profile |

## ENTITY OWNERSHIP
none yet — `domain-profile.md` names no concrete entities (P1 SRS per module assigns `ENT` IDs;
this registry's entity section is populated as each module's P1 runs).

## SHARED ENTITY DECLARATIONS
none yet — no SHARED entity candidate identified at this stage; expected first candidates
(e.g. SEC's User/Role, MDL's Lookup Type/Value) are named once SEC's and MDL's P1 (SRS) run.

## STRUCTURAL / IMPLEMENTATION REGISTRY
none yet — filled by P2 (`DBF`) / P3.1 (`API`) per module version.

## CROSS-MODULE DEPENDENCY INDEX
| Candidate ref | Kind | From module | To module | Consumes | Status | Evidence |
|---|---|---|---|---|---|---|
| XM-CAND-001 | HARD-FK | FIN | SEC | identity + module/screen/action grants + SoD (entry-creator ≠ period-close approver) | CANDIDATE | domain-profile §6 row "FIN \| SEC \| HARD-FK" |
| XM-CAND-002 | HARD-FK | FIN | MDL | payment methods, accounting event types, account types, period states, journal types | CANDIDATE | domain-profile §6 row "FIN \| MDL \| HARD-FK" |
| XM-CAND-003 | SOFT/EVENT | FIN | Notifications (NOTIF, out of this batch) | period-close-awaiting notice, statement export — optional only | CANDIDATE | domain-profile §6; general-accounting-system-plan-en.md §2.3 |
| XM-CAND-004 | SOFT/EVENT | FIN | File Service (FILESVC, out of this batch) | statement/export file — optional only | CANDIDATE | domain-profile §6; general-accounting-system-plan-en.md §2.3 |
| XM-CAND-005 | SOFT | SEC | Notifications (NOTIF, out of this batch) | password-reset message — optional only | CANDIDATE | domain-profile §6; security-module-plan-en.md §8 |
| XM-CAND-006 | EVENT | host business system (out of scope) | FIN | canonical accounting event only — no direct table read/write either direction | CANDIDATE | domain-profile §6 row "host → FIN (event only)"; general-accounting-system-plan-en.md §3 |
Note: every consumer module (all 9, per SEC/MDL plans §7/§4) will register the same
FIN→SEC / FIN→MDL shape once it exists; only the three modules named in this batch are
pre-registered as candidates above — this is not a closed list.

## DECISION INDEX
| # | Decision | Status | Source |
|---|---|---|---|
| 1 | PostgreSQL is the sole DB build target; Oracle/ADF remains an upstream event source only | ACCEPTED | domain-profile §8 row 1 |
| 2 | Hierarchical 3-level RBAC (Module→Screen→Action) replaces any module-local security | ACCEPTED | domain-profile §8 row 2 |
| 3 | One central Lookup master-detail hub replaces module-local lookup tables | ACCEPTED | domain-profile §8 row 3 |
| 4 | No per-entry approval in GL; the only human control point is period close | ACCEPTED | domain-profile §8 row 4 |
| 5 | This batch's scope and order: SEC, then MDL, then FIN, strictly in that order | ACCEPTED | domain-profile §8 row 5 |
| 6 | Notifications/File Service integration is optional-only, used solely on explicit plan need | ACCEPTED | domain-profile §8 row 6 |

## OPEN QUESTION INDEX
none — `domain-profile.md` §10 records no open item.

## PIPELINE / PROGRESS STATUS
| Module | Version | Last committed stage | Last gate verdict | Delivered tracks | Tag |
|---|---|---|---|---|---|
| SEC | v1 | domain-profile (platform-level; module stages NOT STARTED) | — | — | — |
| MDL | v1 | NOT STARTED | — | — | — |
| FIN | v1 | NOT STARTED | — | — | — |
| ORG | — | NOT STARTED | — | — | — |
| PRC | — | NOT STARTED | — | — | — |
| HR | — | NOT STARTED | — | — | — |
| INV | — | NOT STARTED | — | — | — |
| SLS | — | NOT STARTED | — | — | — |
| CTR | — | NOT STARTED | — | — | — |

## CHANGE / EVENT HISTORY
| Date | Stage/tool | Module | Version | Event |
|---|---|---|---|---|
| 2026-09-10 | domain-profile | (platform) | — | domain-profile.md v1 saved and committed (23b3176) |
| 2026-09-10 | P-1 | (platform) | — | BOOTSTRAP — extracted 9 module rows, 0 entity candidates, 6 XM candidates, 6 confirmed decisions, 0 open items from domain-profile.md v1 |
══════════════════════════════════════════════════════════════════
