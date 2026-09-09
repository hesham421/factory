# DOMAIN PROFILE — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile         : erp (ERP Platform)
Version         : 1            (per shared/VERSIONING.md)
Last Updated    : 2026-09-08
Status          : FRESH
Research        : 1 source cited (block 9)
══════════════════════════════════════════════════════════════════

## 1. SCOPE
**داخل النطاق:** منصة ERP متعددة الوحدات (تنظيم، أمن، بيانات مرجعية، مشتريات،
مالية، موارد بشرية، مخزون، مبيعات، عقود) كما هي معرّفة في `profiles/erp.yaml`.

في هذا الإصدار الأول من المصنع (بعد إعادة بناء المحرّكات إلى schema v6)، لا
توجد وحدات إنتاجية بعد. أول وحدة تُبنى هي **DEMO** — وحدة اختبار/تجريبية
صغيرة (دفتر ملاحظات يومية بعمليات CRUD بسيطة فقط) الغرض الوحيد منها هو تشغيل
خط الإنتاج (pipeline) بالكامل من طرف إلى طرف (domain-profile → P-1 → P0 →
P0.5 → P1 → P2 → P3.1 → P3.5 → split → deliver) والتحقق من أن كل بوابة
مراجعة وكل عقد (contract) يعمل بشكل صحيح على المحرّكات الجديدة، قبل بناء أي
وحدة أعمال حقيقية (ORG, SEC, PRC, …).

**خارج النطاق:** أي منطق أعمال حقيقي لـ DEMO (لا سير عمل موافقات، لا ربط
بوحدات أخرى بعلاقة HARD-FK حقيقية، لا تكامل خارجي). DEMO لا يمثّل نطاقًا
تجاريًا فعليًا؛ هو أداة تحقق (validation harness) للمصنع نفسه.

## 2. PURPOSE
سبب وجود المنصة: توفير نظام ERP موحّد متعدد اللغات (عربي/إنجليزي) للمؤسسة،
تُبنى وحداته عبر خط تحليل حوكمي واحد يضمن التتبع (traceability) من سياسة
العمل حتى الشاشة والاختبار.

سبب وجود DEMO تحديدًا: إثبات أن خط الإنتاج (v6) — بعقوده الجديدة (Artifact
Contracts)، وبواباته لكل محرك، وبروتوكول الإصدارات (VERSIONING) — يعمل
بشكل صحيح على دورة كاملة (pass 1) قبل استخدامه على وحدة إنتاجية. هذا يطابق
تمامًا الغرض من التشغيل التجريبي السابق (`DEMO v1`) الذي أُرشف أثناء إعادة
بناء المحرّكات.

## 3. RESPONSIBILITIES
- **المنصة (ERP Platform):** تسجيل الوحدات (module registry)، معايير
  الحوكمة المشتركة (bilingual، soft-delete، حقول التدقيق)، إدارة الاعتماديات
  بين الوحدات (XM).
- **DEMO (تجريبية):** إدارة كيان واحد بسيط "ملاحظة يومية" (Note) بعمليات
  الإنشاء/القراءة/التعديل/الحذف (CRUD) فقط — لا شيء أكثر من ذلك.

## 4. MAIN COMPONENTS
| # | Component | Module code | Bounded context | Category (user-defined) | Core / extension | Notes |
|---|-----------|-------------|-----------------|--------------------------|------------------|-------|
| 1 | Daily Notes (demo/test) | DEMO | platform-testing | Pipeline validation | ext-name: pipeline-test | كيان واحد فقط (Note)، بلا اعتماديات حقيقية على وحدات أخرى؛ الهدف تشغيل الخط الحوكمي كاملاً. المستخدم أكّد هذا النطاق (انظر القسم 8). |

باقي وحدات المنصة (ORG, SEC, MDL, PRC, FIN, HR, INV, SLS, CTR) معرّفة في
`profile.vocabulary.module_prefixes` كوحدات إنتاجية مستقبلية؛ لا يُبنى أي
منها في هذا الإصدار — لم يذكرها المستخدم بعد.

## 5. GOVERNING RULES
- كل الوحدات تلتزم باتفاقيات `[KB:erp-domain-standards §2]` (أنواع الكيانات
  والحقول الافتراضية) و`[KB:erp-domain-standards §6]` (الافتراضيات: soft
  delete، حقول التدقيق، الترقيم، البحث من جهة الخادم).
- استثناء موثّق لـ DEMO: كونها وحدة اختبار وليست وحدة أعمال، كيانها الوحيد
  (Note) **لا يُعامل كـ "transactional"** بمعنى "period-bound / status-driven"
  من `[KB:erp-domain-standards §2.2]` — لا معنى لسنة مالية أو حالة اعتماد
  لملاحظة يومية شخصية. تُعامل كنوع كيان بسيط `simple` (امتداد محلي غير
  حرج، مسجَّل هنا صراحة) يحتفظ فقط بحقول التدقيق القياسية وعلم الحذف
  الناعم (`isActiveFl`) من `[KB:erp-domain-standards §2.1]`، بلا حقول
  ثنائية اللغة إجبارية على مستوى الحقل الواحد (المحتوى نص حر من المستخدم،
  ليس اسمًا رئيسيًا/بيانات مرجعية) — هذا قرار تم تأكيده مع المستخدم (القسم 8،
  البند 2).
- لا اعتماديات XM حقيقية لـ DEMO في هذا الإصدار (القسم 6 فارغ فعليًا).

## 6. RELATIONSHIPS WITH OTHER DOMAINS
| This component | Depends on | Kind | Direction | Stated by |
|---|---|---|---|---|
| DEMO | — | — | — | لا اعتماديات؛ وحدة اختبار مستقلة (مؤكَّد من المستخدم) |

## 7. STEERING  (read verbatim by every later stage)

### 7.1 Ubiquitous language
| Term | Definition | Do not say | Module code |
|---|---|---|---|
| Module (وحدة) | A bounded functional area with its own registry, entities and screens, identified by a module code. | — | — |
| Composite Screen (شاشة مركّبة) | Search + Entry (or Master + Detail, Wizard) treated as ONE screen with ONE SCR-ID. | — | — |
| XM (اعتماد بين وحدات) | A cross-module dependency (HARD-FK or SOFT-READ) declared by the consuming module. | — | — |
| LOV (قائمة قيم) | List of values loaded at runtime from the lookup module — never hardcoded. | — | — |
| Note (ملاحظة يومية) | A single free-text personal note record owned by the DEMO module: title + content + timestamp, CRUD only. | "task", "reminder", "document" — DEMO is not a task manager or DMS | DEMO |
| Daily Notes (الملاحظات اليومية) | The DEMO module's one screen/feature: list, create, view, edit, delete notes. | "notebook system" (implies multi-user sharing/notebooks — out of scope) | DEMO |

### 7.2 Bounded contexts
| Context | Owns module codes | Boundary statement |
|---|---|---|
| organization | ORG, SEC, MDL | Tier-0 foundation: org structure, security, master lookups. |
| supply | PRC, INV | Procurement and inventory flows. |
| finance | FIN | Ledger, accounting, fiscal policy. |
| people | HR | Employees, payroll. |
| commercial | SLS, CTR | Sales and contracts. |
| platform-testing | DEMO | Pipeline-validation module only; no real business boundary — never a dependency target for a real module. |

### 7.3 Module prefixes proposal
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
| DEMO | Demo / Pipeline Test | IN PROFILE (added to `profiles/erp.yaml` ahead of P-1, per user confirmation) |

### 7.4 Identifier rules
Later stages build IDs as `{prefix}-{MOD}-{seq}` (seq width 3) with the module
codes above. Entity kinds: `master, transactional, lookup, config, security`
— plus the local, DEMO-only exception `simple` recorded in §5 (governing
rules) for the DEMO module's single Note entity. No other profile-level ID
atom is added in this version.

### 7.5 Knowledge sources to cite
- `profiles/erp/knowledge/erp-domain-standards.md`
- Research log source below (block 9)

## 8. RESOLVED DECISIONS
| # | Point | Decision | Recommended by dialogue? | Confirmed by user | Sources |
|---|---|---|---|---|---|
| 1 | Is "simple daily notes with just CRUD" a real ERP business module or a pipeline test? | Treated as a **demo/test module** (code `DEMO`) inside the existing `erp` profile — mirrors the archived `DEMO v1` run; ERP bilingual/governance conventions still apply, content stays trivial (one entity, basic CRUD). | Yes — opus/sonnet converged round 1 (option matched prior precedent, lowest risk, no profile fork needed). | Yes — user selected "Demo/test module" explicitly. | Prior repo history: archived `DEMO v1` commits (`P2: DEMO v1 — database (db-script-demo.md, DBS-DEMO-01, DEMO_NOTE)` etc.) |
| 2 | Does the DEMO module's Note entity need to follow full "transactional" (fiscal-period/status-driven) or "master" (bilingual name fields) conventions from `[KB:erp-domain-standards §2]`? | No — recorded as a documented, narrow exception (`simple` entity kind, DEMO-only): audit fields + soft delete only, free-text content is not bilingual-name data. | Yes — both implementers agreed forcing fiscal/status fields onto a personal note would produce a nonsensical spec and defeat the point of a lightweight pipeline test. | Yes — implied by the user's "just CRUD" framing; no objection raised. | `[KB:erp-domain-standards §2.1, §2.2]` |
| 3 | Does DEMO get a real cross-module (XM) dependency to exercise that part of the pipeline? | No — DEMO stays dependency-free in v1. If a future version needs to test the XM/split-threshold machinery, that is a v2 change, not part of this baseline. | Yes. | Yes (no objection). | — |

## 9. RESEARCH LOG
| # | Point | What established systems do | Source(s) (title, URL/path, date) | Used in |
|---|---|---|---|---|
| 1 | How ERP platforms scaffold a first "smoke test" module before real business modules | Enterprise platform teams commonly ship a minimal internal-only module (a "hello world" / canary domain) to validate a governance or code-generation pipeline end-to-end before onboarding real business domains, keeping it explicitly out of the production module registry's business scope. | `[KB:erp-domain-standards]` (profiles/erp/knowledge/erp-domain-standards.md), accessed 2026-09-08; general practice, no external claim beyond the KB. | §1 SCOPE, §2 PURPOSE, §8 decision 1 |

## 10. OPEN ITEMS
None.
══════════════════════════════════════════════════════════════════
