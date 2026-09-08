## MODULE REGISTRY — Daily Notes / Demo (DEMO)
══════════════════════════════════════════════════════════════════
Module Code    : DEMO   (profile.vocabulary.module_prefixes)
Bounded context: platform-testing
Layer / Type   : L0 / pipeline-test harness     Execution tier : 1.1
Source         : NEW
Knowledge      : `[KB:erp-domain-standards §2.1]`, domain-profile §3, §5, §7.1
Readiness      : READY
══════════════════════════════════════════════════════════════════

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar/en) | Kind (master / transactional / lookup / config / security) | PRIVATE / SHARED | Source |
|---|---|---|---|
| ملاحظة يومية / Note | simple (DEMO-only local exception — see AUTO-DECISIONS; not master/transactional/lookup/config/security) | PRIVATE | domain-profile §3, §7.1; project-registry CAND-DEMO-001 |

LOOKUPS OWNED    (value lists this module masters)
None — standard values apply; DEMO masters no lookup (domain-profile §3 names only the Note entity).

LOOKUPS CONSUMED (from other modules)
None — DEMO consumes no lookup from another module (confirmed decision, domain-profile §8 row 3).

SHARED ENTITIES CONSUMED
None.

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
|---|---|---|
| — | — | none |
ROOT: YES

AUTO-DECISIONS
AUTO: Note is classified with the local, DEMO-only entity kind `simple` instead of `master`/`transactional`/`lookup`/`config`/`security`.  FROM: domain-profile §5 (documented exception) and `[KB:erp-domain-standards §2.2]` (transactional = fiscal-period/status-driven, inapplicable to a personal note).  IF WRONG: reclassify Note as `transactional` and add `fiscalYearId`/`periodId`/`statusCode` per the standard pattern.
AUTO: Note carries the four standard audit fields plus soft-delete (`isActiveFl`), but no bilingual `nameAr`/`nameEn` pair (its "name" is free-text user content, not reference data).  FROM: `[KB:erp-domain-standards §2.1]` (bilingual name rule applies to master reference data) and `[KB:erp-domain-standards §6]` (audit trail / soft delete defaults apply universally).  IF WRONG: add bilingual title fields instead of a single free-text title.
AUTO: DEMO is ROOT with no dependency of any kind.  FROM: domain-profile §6 (empty relationships table) and §8 decision 3 (confirmed).  IF WRONG: none expected without a new user request.

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Should DEMO's single entity be pre-registered as `master` (to get bilingual name handling automatically) or as a documented exception? | Documented `simple` exception (see AUTO-DECISIONS) — matches domain-profile §5's explicit ruling; forcing `master` would wrongly imply Note is reference/lookup data. | Confirmed — carries forward domain-profile §8 row 2, already confirmed by the user. | domain-profile §5, §7.1, §8 row 2 |
══════════════════════════════════════════════════════════════════
