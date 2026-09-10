## MODULE REGISTRY — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module Code    : MDL   (profile.vocabulary.module_prefixes)
Bounded context: organization
Layer / Type   : L1 / reference hub     Execution tier : 1.3
Source         : NEW
Knowledge      : new project/lookup-module-plan-en.md; profiles/erp/knowledge/erp-domain-standards.md §2-§3
Readiness      : READY
══════════════════════════════════════════════════════════════════

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar/en) | Kind (master / transactional / lookup / config / security) | PRIVATE / SHARED | Source |
|---|---|---|---|
| نوع اللوكب / LookupType | master | SHARED (owner) — every consuming module registers and reads its own types here | lookup-module-plan-en.md §2-§3 |
| قيمة اللوكب / LookupValue | lookup | SHARED (owner) — every consuming module reads/manages its own values here | lookup-module-plan-en.md §3 |

LOOKUPS OWNED    (value lists this module masters — MDL owns the MECHANISM only; see rule below)
| Lookup key | Description | Initial values (only those the user named) | Source |
None — MDL itself introduces no domain-specific coded list of its own; it is the generic
mechanism every OTHER module's lookup types run on top of. (MDL does not "consume itself.")
Rule (profile): all LOV values runtime-loaded from the lookup module; no hardcoded enums in APIs or field specs — this rule is MDL's own reason to exist.

LOOKUPS CONSUMED (from other modules)
| Lookup key | Owner code | READ-ONLY |
None.

SHARED ENTITIES CONSUMED
| Entity | Owner code | HARD-FK / SOFT-READ | Why |
| ModuleRegistry (ENT-SEC-004) | SEC | SOFT-READ | validate that a lookup type's declared owner module code is a real, registered platform module before accepting the registration — mirrors SEC's own RULE-SEC-004 pattern for screens, applied here to lookup types |

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
| SEC | SOFT | ModuleRegistry (owner-code validation only — see SHARED ENTITIES CONSUMED) |
ROOT: NO (has one SOFT dependency on SEC; still Tier 0 Foundation per KB §1 — a SOFT-READ
foundation dependency on another Tier-0 module does not change tiering)

AUTO-DECISIONS
AUTO: classified MDL's SEC dependency as SOFT-READ, not HARD-FK
  FROM: [KB:erp-domain-standards §5] "SOFT-READ: a read-only lookup by code — allowed in any direction"; a HARD-FK would make MDL's own schema depend physically on SEC's PK, which is heavier than the actual need (a one-time/per-write existence check)
  IF WRONG: promote to HARD-FK if a later requirement needs referential-integrity-level guarantees stronger than an application-level check — would need its own ADR.
AUTO: LookupType classified kind=master, LookupValue kind=lookup
  FROM: profiles/erp.yaml conventions.entity_defaults — LookupValue's fields (code, nameAr, nameEn, sortOrder, isActiveFl) match the `lookup` kind's default set exactly; LookupType (code, nameAr, nameEn, ownerModuleCode, isActiveFl) is closer to `master` (bilingual, coded, soft-deletable, not itself a coded VALUE of some other type)
  IF WRONG: none recommended — this is the plan's own vocabulary (§3 "a lookup is a type (master) + its values (detail)").
AUTO: tier/numbering 1.3 (Foundation, Tier 0)
  FROM: [KB:erp-domain-standards §1]
  IF WRONG: renumber if the platform later reprioritizes.

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
None — lookup-module-plan-en.md fully settles this module's P0 scope; no point required dialogue.

POLICIES OWNED (full text in business-policies-mdl.md)
POL-MDL-001, POL-MDL-002, POL-MDL-003, POL-MDL-004, POL-MDL-005, POL-MDL-006
══════════════════════════════════════════════════════════════════
