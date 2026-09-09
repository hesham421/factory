# PLATFORM SUMMARY — ERP Platform
══════════════════════════════════════════════════════════════════
Profile : erp   Domain profile : v1   Registry : v1.1.0
══════════════════════════════════════════════════════════════════

## OVERVIEW
منصة ERP متعددة الوحدات وثنائية اللغة (عربي/إنجليزي)، تُبنى وحداتها عبر خط
تحليل حوكمي واحد. في هذا الإصدار لا توجد وحدة أعمال حقيقية بعد؛ الوحدة
الوحيدة المطلوبة الآن هي **DEMO**، وحدة اختبار/تجريبية صغيرة (ملاحظات
يومية بعمليات CRUD فقط) الغرض منها التحقق من أن خط الإنتاج الجديد (v6)
يعمل بشكل صحيح من طرف إلى طرف قبل استخدامه على وحدة إنتاجية
(domain-profile §1–§2).

## MODULES
| #   | Code | Module | Bounded context | Layer | Type | Depends on | Status |
|-----|------|--------|-----------------|-------|------|------------|--------|
| 1.1 | DEMO | Daily Notes (demo/test) | platform-testing | L0 | pipeline-test harness | ROOT | NEW |

Status: NEW (Phase 2 produces this run).
Numbering: [tier].[sequence within tier] — 1.1 is a Tier-0/harness slot
reserved for pipeline-validation modules (a new tier label, not one of the
domain-profile's business tiers, since DEMO is not a business module —
AUTO: added an "L0 / pipeline-test" layer+tier distinct from Tier 0
Foundation (ORG/SEC/MDL). FROM: `[KB:erp-domain-standards §1]` does not
cover non-business modules; domain-profile §1, §5 (DEMO is explicitly not
a business tier). IF WRONG: fold DEMO into Tier 0 Foundation instead.

## DEPENDENCY MAP
Build order: L0 [DEMO] → Tier 1 [—] → Tier 2 [—] → Tier 3 [—] → Tier 4 [—]
Key dependencies: none — DEMO is ROOT with no HARD, SOFT or LOOKUP dependency
(domain-profile §6; confirmed decision §8 row 3).

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
| All real ERP business modules (ORG, SEC, MDL, PRC, FIN, HR, INV, SLS, CTR) | user has not requested them yet; domain-profile §4 notes they remain future modules |
| DEMO cross-module (XM) dependency | user confirmed v1 stays dependency-free (domain-profile §8 row 3); activation trigger: a future DEMO v2 requested specifically to exercise XM/split-threshold mechanics |
| Workflow engine | profile: forbidden |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | What layer/tier does a non-business "pipeline test" module occupy, given the profile's tiers (§1 KB) are all business tiers? | Introduce a local "L0 / pipeline-test harness" tier for DEMO only, outside the Tier 0–2 business tiering, so it is never mistaken for a real Foundation module and never becomes a HARD-FK target of a real module. | Recommended answer stands (implied acceptance — no objection to the earlier domain-profile framing this builds on). | `[KB:erp-domain-standards §1]`; domain-profile §1, §5, §7.2 (platform-testing context) |

## OPEN ITEMS
None — platform scope fully determined for this run (DEMO only).

## NEXT STEP
Reply with a plain instruction to adjust, or request module "1.1" to proceed — this run proceeds directly to Phase 2 for DEMO (the only requested module).
══════════════════════════════════════════════════════════════════
