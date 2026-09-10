# PLATFORM SUMMARY — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile : erp   Domain profile : v1   Registry : v1.2.0
══════════════════════════════════════════════════════════════════

## OVERVIEW
منصة ERP متعددة الوحدات، قائمة على مبدأ "كل ما يمكن أن يتغير = بيانات، لا شيفرة"، تُبنى
بـ Spring (خلفية) وReact (واجهة) على PostgreSQL. الوحدتان التأسيسيتان (SEC، MDL) اكتملتا
(pass-1 APPROVE لكل منهما)؛ هذه الجلسة تُنشئ **الوحدة الثالثة والأخيرة لهذه الدفعة: FIN**
(الحسابات العامة / دفتر الأستاذ العام)، أول وحدة أعمال حقيقية تستهلك SEC وMDL معًا.
[domain-profile §1-§2; project-registry PIPELINE/PROGRESS STATUS]

## MODULES
| #   | Code | Module (ar/en) | Bounded context | Layer | Type | Depends on | Status |
|-----|------|--------|-----------------|-------|------|------------|--------|
| 1.1 | ORG | الهيكل التنظيمي / Organization | organization | L1 | master data | ROOT | NEW (not this batch) |
| 1.2 | SEC | الأمان / Security | organization | L1 | security engine | ROOT | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 1.3 | MDL | البيانات المرجعية / Master Data Lookup | organization | L1 | reference | SEC (SOFT-READ) | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 2.1 | PRC | المشتريات / Procurement | supply | L3 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
| 2.2 | FIN | الحسابات العامة / Finance (GL) | finance | L3 | transactional/reporting | SEC (HARD), MDL (HARD) | NEW — this batch, third (last) |
| 2.3 | INV | المخزون / Inventory | supply | L3 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
| 3.1 | SLS | المبيعات / Sales | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
| 3.2 | CTR | العقود / Contracts | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
| 3.3 | HR | الموارد البشرية / Human Resources | people | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this batch) |
Status: NEW (Phase 2 produces) · EXISTING (Phase 2 extends) · EXCEPTION (read as-is)
Numbering: [tier].[sequence within tier] — the user requests Phase 2 by this number.
This run's Phase 2 request: **2.2 FIN** (module convergence below) — the last module in
this batch's mandated order (GENERATION-INSTRUCTIONS.md §3: SEC → MDL → FIN).

## DEPENDENCY MAP
Build order: Tier 1 [ORG, SEC, MDL] → Tier 2 [PRC, FIN, INV] → Tier 3 [SLS, CTR, HR] → Tier 4 (reporting, none yet)
Key dependencies (one line each):
  FIN → HARD → SEC : identity + module/screen/action grants + SoD (entry-creator ≠ period-close approver) — target SEC v1 GATED
  FIN → HARD → MDL : payment methods, accounting event types, account types, period states, journal types — target MDL v1 GATED
  FIN → SOFT → NOTIF (external, ready) : period-close-awaiting notice, optional only
  FIN → SOFT → FILESVC (external, ready) : statement export, optional only
  (host business system) → EVENT → FIN : canonical accounting event only, no table read/write

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
| ORG, PRC, HR, INV, SLS, CTR detailed analysis | out of this batch (GENERATION-INSTRUCTIONS.md §3) |
| Multi-currency, multi-ledger/entity, statistical accounts, multi-pattern calendar, attachments | excluded by explicit decision [general-accounting-system-plan-en.md §15] |
| Workflow engine | profile: `forbidden` |
| Notifications / File Service redesign | ready external modules; consumed only on real need [general-accounting-system-plan-en.md §2.3] |
| Event consumer, idempotency de-duplication logic, AQ/RabbitMQ transport | out of scope — FIN assumes boundary idempotency, never re-implements it [general-accounting-system-plan-en.md §15, point 12] |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Phase 2 request for this P0 run | Module 2.2 FIN (third and last of the batch order) | Yes — GENERATION-INSTRUCTIONS.md §3 | GENERATION-INSTRUCTIONS.md §3 |
| 2 | FIN's dependency targets | SEC v1 and MDL v1, both already gated (pass-1 APPROVE) — no DEFERRED XM expected | Yes — project-registry.md PIPELINE/PROGRESS STATUS | project-registry.md |

## OPEN ITEMS
None.

## NEXT STEP
Module 2.2 FIN converges below (module-registry-fin.md, business-policies-fin.md). This
is the last module of the current batch; once FIN's own pass-1 gate is APPROVE, the batch
mandated by GENERATION-INSTRUCTIONS.md is complete.
