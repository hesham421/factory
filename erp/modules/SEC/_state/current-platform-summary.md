# PLATFORM SUMMARY — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile : erp   Domain profile : v1   Registry : v1.0.0
══════════════════════════════════════════════════════════════════

## OVERVIEW
منصة ERP متعددة الوحدات، قائمة على مبدأ "كل ما يمكن أن يتغير = بيانات، لا شيفرة"،
تُبنى بـ Spring (خلفية) وReact (واجهة) على PostgreSQL كهدف بناء وحيد؛ النظام القديم
Oracle/ADF يبقى مصدر أحداث فقط. هذه الدفعة تُنشئ ثلاث وحدات تأسيسية بالترتيب الصارم
SEC ← MDL ← FIN؛ باقي وحدات المنصة (ORG, PRC, HR, INV, SLS, CTR) معروفة الرمز
والسياق من `profiles/erp.yaml` لكنها خارج نطاق هذه الدفعة. [domain-profile §1-§2]

## MODULES
| #   | Code | Module (ar/en) | Bounded context | Layer | Type | Depends on | Status |
|-----|------|--------|-----------------|-------|------|------------|--------|
| 1.1 | ORG | الهيكل التنظيمي / Organization | organization | L1 | master data | ROOT | NEW (not this batch) |
| 1.2 | SEC | الأمان / Security | organization | L1 | security engine | ROOT | NEW — this batch, first |
| 1.3 | MDL | البيانات المرجعية / Master Data Lookup | organization | L1 | reference | ROOT | NEW (not this batch) |
| 2.1 | PRC | المشتريات / Procurement | supply | L3 | transactional | SEC, MDL (SOFT/HARD, not yet detailed) | NEW (not this batch) |
| 2.2 | FIN | الحسابات العامة / Finance (GL) | finance | L3 | transactional/reporting | SEC (HARD), MDL (HARD) | NEW — this batch, third |
| 2.3 | INV | المخزون / Inventory | supply | L3 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
| 3.1 | SLS | المبيعات / Sales | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
| 3.2 | CTR | العقود / Contracts | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
| 3.3 | HR | الموارد البشرية / Human Resources | people | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
Status: NEW (Phase 2 produces) · EXISTING (Phase 2 extends) · EXCEPTION (read as-is)
Numbering: [tier].[sequence within tier] — the user requests Phase 2 by this number.
This run's Phase 2 request: **1.2 SEC** (module convergence below).

## DEPENDENCY MAP
Build order: Tier 1 [ORG, SEC, MDL] → Tier 2 [PRC, FIN, INV] → Tier 3 [SLS, CTR, HR] → Tier 4 (reporting, none yet)
Key dependencies (one line each):
  FIN → HARD → SEC : identity + module/screen/action grants + SoD (entry-creator ≠ period-close approver)
  FIN → HARD → MDL : payment methods, accounting event types, account types, period states, journal types
  SEC → SOFT → NOTIF (external, ready) : password-reset message, optional only
  FIN → SOFT → NOTIF (external, ready) : period-close-awaiting notice, optional only
  FIN → SOFT → FILESVC (external, ready) : statement export, optional only
  (host business system) → EVENT → FIN : canonical accounting event only, no table read/write

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
| ORG, PRC, HR, INV, SLS, CTR detailed analysis | user-scoped this batch to SEC → MDL → FIN only (GENERATION-INSTRUCTIONS.md §3) |
| Workflow engine | profile: `forbidden` |
| Notifications / File Service redesign | ready external modules; consumed only on real need, never re-specified [security-module-plan-en.md §8; lookup-module-plan-en.md §5; general-accounting-system-plan-en.md §2.3] |
| Multi-currency, multi-ledger/entity, statistical accounts, multi-pattern calendar, attachments (FIN) | excluded by explicit decision [general-accounting-system-plan-en.md §15] |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Numbering/tiering of the 9 platform modules | Foundation=1.x, Core business=2.x, Extended business=3.x, per KB §1 tiers | Yes — no conflicting statement in the plans | [KB:erp-domain-standards §1] |
| 2 | Phase 2 request for this P0 run | Module 1.2 SEC (first of the batch order SEC→MDL→FIN) | Yes — GENERATION-INSTRUCTIONS.md §3 | GENERATION-INSTRUCTIONS.md §3 |

## OPEN ITEMS
None — platform scope fully determined for this batch (SEC, MDL, FIN); the other six
modules are out of scope, not ambiguous — no registry ↔ vision conflict exists.

## NEXT STEP
Module 1.2 SEC converges below (module-registry-sec.md, business-policies-sec.md).
Reply with a plain instruction to adjust, or request module 1.3 (MDL) next per the
mandated order.
