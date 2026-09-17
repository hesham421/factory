# BRIEF — stage `P0` (Platform Inception) · module NOTE · v1 · profile `erp`

Lane `analysis` · implementer claude:opus · effort high · round 2

## Rules that bind this run
- Questions: **allowed**. Close every open point inside this dialogue with a researched, recommended answer; never write an external open-questions file.
- Owns IDs: POL — ID grammar `{prefix}-{MOD}-{seq}` (seq width 3); never re-number, never restart a sequence.
- Read only what this brief contains (generated current state); never open version folders yourself.
- Write exactly these files (complete files; in a delta version only what changed, plus `change-manifest.md`):
- `erp/modules/NOTE/P0/platform-summary.md`
- `erp/modules/NOTE/P0/module-registry-note.md`
- `erp/modules/NOTE/P0/business-policies-note.md`
- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; when running as the operator, write the files directly.

## Dialogue protocol (converging, in-brief)
Implementers claude:opus alternate for at most 4 rounds; converge on **mutually-acceptable**.
Round 1 drafts the artifacts and, for every open point, a `PROPOSAL:` block (options, researched recommendation, sources).
Each later round answers every open PROPOSAL (accept / amend with reason), refines the artifacts, and appends `<!-- CONVERGED -->` at the end of the response when nothing material remains open. The last response is final.

## Previous round
(see `erp/modules/NOTE/_state/briefs/P0.response1.md` — appended below)

## Contracts checked by `gov.py analyze` after this stage
- **C2** project registry → inception: C2.1 exists {'artifact': 'project-registry'} [CRITICAL]; C2.2 registry-agree {'registry': 'project-registry', 'categories': 'all'} [MAJOR]; C2.3 ids-owned {'artifact': 'project-registry', 'defines': []} [MAJOR]
- **C3** inception → PRD: C3.1 exists {'artifact': 'platform-summary'} [CRITICAL]; C3.2 exists {'artifact': 'module-registry'} [CRITICAL]; C3.3 exists {'artifact': 'business-policies'} [CRITICAL]; C3.4 ids-owned {'stage': 'P0'} [CRITICAL]; C3.5 no-questions {'stage': 'P0'} [CRITICAL]; C3.6 languages {'stage': 'P0'} [MAJOR]; C3.7 registry-agree {'artifact': 'business-policies', 'registry': 'module-registry', 'kinds': ['POL']} [MAJOR]

---
# ENGINE
# Platform Inception — ENGINE

```
Engine        : Platform Inception
Stage id      : P0
Pass          : 1
Questions     : allowed — resolved in-dialogue with recommended answers; user confirms
Dialogue      : yes — lane analysis (claude:opus; ≤ 4 rounds; converge on "mutually-acceptable"; output: resolved-decisions)
Inputs        : domain-profile, project-registry
Produces      : platform-summary.md · module-registry-{mod}.md · business-policies-{mod}.md
Owns IDs      : POL   → `{prefix}-{MOD}-{seq}` (seq width 3)
Next          : P0.5
Module        : NOTE   Version: 1
Profile       : erp — ERP Platform
```

This engine turns free-form vision text into a closed architectural context: first a
**platform summary** (tiered module table, dependency map), then — per module — a
**module registry** and **business policies** written as EARS statements with
`POL` IDs. Its outputs are CONTEXT for `P0.5`, never requirements.

Completion (write → registry → analyze → commit) is owned by the orchestrator — see
`shared/GOVERNANCE-CORE.md`. In a delta version (version > 1): read `_state/current-{artifact}` of the previous
version for every input and for this stage's own artifacts, and emit only ADDED /
MODIFIED / REMOVED elements plus the `change-manifest.md` per `shared/VERSIONING.md`.

```
╔══════════════════════════════════════════════════════════════════════╗
║ ABSOLUTE BOUNDARY                                                    ║
║ This stage does not write requirements, screens, field lists,        ║
║ validation rules, entity IDs or any content owned by P0.5 or later.  ║
║ A request for such content → produce this stage's artifacts, then    ║
║ redirect once (§7). No partial draft. No exception.                  ║
╚══════════════════════════════════════════════════════════════════════╝
```

Language policy: narrative in `ar`; every module name, entity name and policy
statement carries all of `ar, en`.

---

## 1 — Reading protocol (before any analysis)

```
STEP A — domain-profile.md (steering — read first)
  §7 STEERING → vocabulary (use verbatim), bounded contexts, module codes,
                identifier rules, knowledge sources
  §1–§6       → scope, purpose, responsibilities, components, rules, relations
  §8          → resolved decisions — never re-open one

STEP B — project-registry.md (categories per shared/REGISTRY-SCHEMA.md)
  module index            → known modules — do NOT re-discover
  entity ownership        → known owners — apply directly
  shared declarations     → known shared entities — apply directly
  dependency index        → extend, never contradict
  open-question index     → OPEN rows this stage may resolve in dialogue (§5)
  pipeline status         → modules already past this stage → EXISTING / EXCEPTION

STEP C — prior module artifacts (this stage's own outputs for other modules,
         from _state/ when they exist)
  entities owned / lookups owned / lookups consumed / dependencies → ground truth;
  a conflict between vision text and a module registry → the registry wins and the
  conflict is listed under OPEN ITEMS of the platform summary.

STEP D — knowledge sources (cite when applying a default)
  - profiles/erp/knowledge/erp-domain-standards.md
```

Every structural decision comes from A → B → C → D in that order, then from domain
best practice; the user is asked only what none of these settle (§5).

---

## 2 — Phase 1: vision → `platform-summary.md`

### 2.1 Transformation (three steps)

```
STEP 1 — EXTRACT from the vision text
  Modules (explicit or implied) — detection table from the profile:
    PRC    Procurement  ← مشتريات / procurement / vendors / suppliers
    HR     Human Resources  ← موظفين / HR / رواتب / payroll / employees
    INV    Inventory  ← مخزون / inventory / warehouses / stock
    FIN    Finance  ← محاسبة / finance / accounts / ledger
    SLS    Sales  ← مبيعات / sales / customers
    CTR    Contracts  ← عقود / contracts / agreements
    ORG    Organization  ← هيكل تنظيمي / org / branches / departments
    (unlisted) → domain-profile §4 components + layer heuristics; still one of the
               profile's codes (ORG, SEC, MDL, PRC, FIN, HR, INV, SLS, CTR, NOTE) or RESERVED per the registry.
  Explicit statements:
    scope exclusions ("without X", "not now")
    specific policies (limits, thresholds, exceptions)   → §3.3 candidates
    custom values (named lookup values)                   → §3.3 candidates

STEP 2 — ENRICH from knowledge sources + domain-profile
  For each module: layer, type, tier, dependencies from the knowledge files and
  the domain-profile relations; remove what the user excluded; add what the user
  mentioned beyond the pattern. Cite the source of every enrichment.

STEP 3 — RESOLVE from the registry
  module past this stage in pipeline status   → EXCEPTION (read as-is; skip in Phase 2)
  module with a prior module-registry artifact → EXISTING (Phase 2 extends it)
  otherwise                                    → NEW
```

### 2.2 Platform summary — template

```markdown
# PLATFORM SUMMARY — [Platform name — from the vision text or domain-profile]
══════════════════════════════════════════════════════════════════
Profile : erp   Domain profile : v[N]   Registry : v[semver]
══════════════════════════════════════════════════════════════════

## OVERVIEW
[One paragraph — what the platform does; enriched with domain context, not a restatement.]

## MODULES
| #   | Code | Module | Bounded context | Layer | Type | Depends on | Status |
|-----|------|--------|-----------------|-------|------|------------|--------|
| 1.1 | [code] | [display] | [context] | L1 | [master data / engine / reference / transactional / reporting] | ROOT | NEW |
| 2.1 | [code] | [display] | [context] | L3 | [type] | [code], [code] (SOFT) | EXISTING |
Status: NEW (Phase 2 produces) · EXISTING (Phase 2 extends) · EXCEPTION (read as-is)
Numbering: [tier].[sequence within tier] — the user requests Phase 2 by this number.

## DEPENDENCY MAP
Build order: Tier 1 [codes] → Tier 2 [codes] → Tier 3 [codes] → Tier 4 [reporting]
Key dependencies (one line each):
  [CODE-A] → HARD → [CODE-B] : [reason]
  [CODE-C] → SOFT → [CODE-D] : [reason]
  [CODE-E] → LOOKUP → [CODE-F] : consumes [lookup key]

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
| Workflow engine | profile: `forbidden` |
| [user-excluded item] | user stated "not now" |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |

## OPEN ITEMS
[Only a registry ↔ vision conflict or a genuinely ambiguous scope boundary that the
 dialogue could not close. Otherwise: "None — platform scope fully determined."]

## NEXT STEP
Reply with a plain instruction to adjust, or with a module number to start Phase 2.
```

### 2.3 Confirmation and number stability

```
After producing the summary: "[N] modules, [N] exceptions. Confirm, or state one change."
Adjustments apply immediately and only the MODULES table is re-shown:
  add a module      → next number at the end of its tier
  defer / remove    → status changes, number kept
  change a status   → status changes, number kept
NUMBER STABILITY: a number never shifts after first assignment — "1.1" always means
the same module. Phase 2 begins on the user's first number request.
```

---

## 3 — Phase 2: module convergence (per requested module)

### 3.1 Request protocol

```
Status EXCEPTION → no files; confirm "[n] [module] is EXCEPTION — read as-is" and offer
                   the next module.
Status EXISTING  → read the prior module registry; EXTEND it (fill gaps, never replace);
                   note "[N] gaps filled from [source]".
Status NEW       → full pattern from knowledge sources + domain-profile.
Always append the readiness block (§3.5) after the two files.
```

### 3.2 Auto-completion protocol (for every gap in the module structure)

```
STEP 1 → prior module registry (EXISTING)         → use it
STEP 2 → project-registry ownership / dependency  → use it
STEP 3 → knowledge sources (§1 STEP D)            → apply, cite
STEP 4 → domain-profile rules + domain best practice → apply, cite
Document every auto-decision:   AUTO: [decision]  FROM: [step / source]  IF WRONG: [override]
STEPS 1–4 all fail → the point is a QUESTION (§5) — resolved in dialogue with a
recommended answer; the user confirms. Never an assumption written as fact.
```

### 3.3 Module registry — template (`module-registry-{mod}.md`)

```markdown
## MODULE REGISTRY — [Module display] ([CODE])
══════════════════════════════════════════════════════════════════
Module Code    : [CODE]   (profile.vocabulary.module_prefixes)
Bounded context: [context id]
Layer / Type   : [L1–L4] / [type]     Execution tier : [n.m]
Source         : NEW / EXTENDED from prior registry
Knowledge      : [knowledge file(s) / domain-profile §]
Readiness      : READY / PARTIALLY_READY
══════════════════════════════════════════════════════════════════

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar/en) | Kind (master / transactional / lookup / config / security) | PRIVATE / SHARED | Source |

LOOKUPS OWNED    (value lists this module masters)
| Lookup key | Description | Initial values (only those the user named) | Source |
Rule (profile): all LOV values runtime-loaded from the lookup module; no hardcoded enums in APIs or field specs

LOOKUPS CONSUMED (from other modules)
| Lookup key | Owner code | READ-ONLY |

SHARED ENTITIES CONSUMED
| Entity | Owner code | HARD-FK / SOFT-READ | Why |

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
ROOT: YES / NO

AUTO-DECISIONS
AUTO: [decision]  FROM: [source]  IF WRONG: [override]

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
══════════════════════════════════════════════════════════════════
```

### 3.4 Business policies — template (`business-policies-{mod}.md`)

This file carries what the domain's standards cannot know: the client's own policies,
custom values and scope exceptions. Standard domain behaviour is applied by
`P0.5` and later stages from the knowledge sources — it is not repeated here.
If the user stated nothing specific, the file is minimal by design.

Every policy is one `POL` record written in **EARS** form (one pattern per
statement; `factory.ids.ears.patterns`):

```
  ubiquitous  The system shall …
  state       While <condition>, the system shall …
  event       When <condition>, the system shall …
  optional    Where <condition>, the system shall …
  unwanted    If <condition>, then the system shall …
```

```markdown
## BUSINESS POLICIES — [Module display] ([CODE])
══════════════════════════════════════════════════════════════════
Module   : [CODE]     Source of truth : user vision text + dialogue resolutions
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)
POL-[CODE]-001 — [short name]
  Statement : [EARS — exactly one pattern; the subject is "the system"]
  Pattern   : [ubiquitous | state | event | optional | unwanted]
  Trigger   : [Create / Update / Submit / Approve / …]
  Rationale : [why the client wants it — one line]
  Source    : [vision text quote / dialogue resolution #]
  Status    : CONFIRMED
(If none: "None — standard domain rules apply.")

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
| Lookup key | Added values | Source |
(If none: "None — standard values apply.")

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
(If none: "None — standard scope applies.")

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
══════════════════════════════════════════════════════════════════
```

Policy rules: a policy is a NEED at platform level, not a validation rule — no field
names, no error messages, no API shapes. Sequence numbers are continuous per module
and never reused. A policy the user did not state and did not confirm is not written.

### 3.5 Readiness block (after every module)

```
✓ [Module] — P0 complete
  Next : P0.5 reads platform-summary.md · module-registry-{mod}.md · business-policies-{mod}.md
  Precondition for P0.5: HARD dependencies [codes] present in the registry
  Another module? [next by tier order]
```

---

## 4 — Registry step content

`module-registry-{mod}.md` IS this stage's registry output. In addition the
orchestrator merges into `project-registry.md`:

```
module index          : status of the module (NEW → IN PROGRESS), tier, layer, type
entity ownership      : ENTITIES OWNED rows (CANDIDATE → REGISTERED, still no ID)
shared declarations   : SHARED rows
dependency index      : DEPENDENCIES rows (candidates for P2)
open-question index   : rows RESOLVED by this stage's dialogue (+ resolution)
pipeline status       : P0 = DONE for the module
event history         : "P0 completed: [module list]"
```

---

## 5 — Questions (allowed here) — how they are asked and closed

```
A QUESTION exists only when §1 A–D and §3.2 STEPS 1–4 leave a point unresolved.

QUESTION — [point]
  Affects       : [module / entity / dependency / scope]
  Options       : A) … (trade-off)   B) … (trade-off)
  Researched    : [what the knowledge sources / domain-profile say — cited]
  Recommended   : [option] — because [rationale]
```

Lane `analysis`: the implementers (claude:opus) converge on each QUESTION —
challenge, answer, ≤ 4 rounds, until **mutually-acceptable**. The converged
block is presented to the user as the recommended answer; the user confirms or adjusts.

```
Resolution is recorded in the RESOLVED DECISIONS table of the artifact it affects.
No external open-questions file. A point the user leaves undecided stays under
OPEN ITEMS of the platform summary and is carried to P0.5 (the last stage that may ask).
Never ask about: anything in the domain-profile, the registry, a prior module registry,
or the knowledge sources.
```

---

## 6 — Continuation

```
Resume with: platform summary + the module artifacts of completed modules (from
_state/ or the version folder) + registry pipeline status.
Announce: "Resuming P0. Completed: [list]. Pending: [NEW/EXISTING from the summary]."
No re-analysis of completed modules. Always re-emit the platform summary before
ending if in-session adjustments were made.
```

---

## 7 — Boundaries and enforcement

```
OWNS      : platform-summary.md · module-registry-{mod}.md · business-policies-{mod}.md · POL IDs · tier and build-order
            assignment · entity / lookup candidate discovery and ownership · dependency map
DOES NOT  : any ID of US (P0.5), REQ (P1), AC (P1), ENT (P1), RULE (P1), DBF (P2), XM (P2), API (P3.1), QR (P3.1), UXD (P3.2), SCR (P3.2), SCR-REQ (P1), TC (test-gen) ·
            requirements · screens · field lists · validation rules · DDL · execution phases

VIOLATION (this stage's output contains any of these):
  screens with field lists · validation logic · requirement statements other than
  POL policies · any ID owned by another stage · permission tables · test scenarios

RUNTIME REDIRECT — when the user asks for requirements / screens / rules / fields:
  1. Complete this stage's artifacts for the module (they ARE the correct answer).
  2. Redirect once: "Requirements begin in P0.5 and later stages; these files are
     their input."
  3. Offer the next valid action (another module number, or proceed).
```

---

## 8 — Self-check before emitting

- [ ] Every module in the summary has a code from the profile (or RESERVED in the registry), a tier, a status.
- [ ] Every entity owned has a kind from `master, transactional, lookup, config, security` and a source; no entity ID.
- [ ] Every policy is exactly one EARS pattern, has a Source, a Trigger, a continuous sequence number.
- [ ] Every auto-decision carries AUTO / FROM / IF WRONG; every default cites a knowledge source.
- [ ] Every QUESTION raised appears in a RESOLVED DECISIONS table (or under OPEN ITEMS with the user's explicit deferral).
- [ ] No requirement, screen, field, rule, permission or later-stage ID anywhere.
- [ ] Vocabulary matches the domain-profile STEERING block verbatim.
- [ ] Names and statements carry all of `ar, en`.


---
# INPUTS (generated current state)

<<<INPUT: domain-profile>>>
# DOMAIN PROFILE — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile         : erp (ERP Platform)
Version         : 1
Last Updated    : 2026-09-10
Status          : FRESH
Research        : 3 sources cited (block 9)
══════════════════════════════════════════════════════════════════

## 1. SCOPE

**داخل النطاق (In bounds):** بناء منصة ERP متعددة الوحدات (multi-module) بعمارة قائمة على
البيانات لا الشيفرة ("everything that can change = defined data, not code")، تُبنى بلغة
Spring (خلفية) و React (واجهة) وقاعدة بيانات **PostgreSQL** كهدف بناء جديد. النظام القديم
Oracle/ADF يبقى فقط كمصدر أحداث علوي (upstream event source) ولا يُبنى عليه أي وحدة جديدة.

دفعة العمل الحالية (هذه الجلسة) تُغطّي ثلاث وحدات أساسية مشتركة ومؤسِّسة:
1. **وحدة الأمان (SEC)** — مصادقة + تحكم هرمي بالصلاحيات (Module → Screen → Action).
2. **وحدة البيانات المرجعية (MDL/Lookup)** — مركز موحّد لكل قوائم القيم المُرمَّزة.
3. **وحدة الحسابات العامة (FIN/GL)** — دفتر أستاذ عام قابل للتوصيل (pluggable) بأي نظام مضيف.

باقي وحدات المنصة (ORG, PRC, HR, INV, SLS, CTR) معروفة الرمز والسياق ضمن `profiles/erp.yaml`
لكنها **خارج نطاق هذه الدفعة** — تُفصَّل لاحقًا بنفس الأسلوب.

**خارج النطاق صراحة (Out of bounds, stated by the user):**
- أي منطق عمل خاص بمجال مضيف (host business world) داخل وحدة الحسابات.
- تعدد العملات، تعدد الدفاتر/الكيانات، الحسابات الإحصائية، التقويم متعدد الأنماط،
  والمرفقات (attachments) — مستبعدة صراحة من GL في هذه الدفعة.
- محرك سير العمل (workflow engine) — ممنوع بحكم `profiles/erp.yaml → conventions.workflow_engine: forbidden`.
- طبقة النقل (AQ/RabbitMQ) ومستهلك الأحداث (Event consumer) والوحدة التجارية (Business Module)
  — خارج نطاق وثيقة FIN، توثَّق في مكان آخر.

## 2. PURPOSE

المنصّة تحل مشكلة تكرار وتضارب القدرات المشتركة (الهوية، الصلاحيات، البيانات المرجعية)
عبر كل وحدة أعمال جديدة: بدل أن تبني كل وحدة نظام دخول وصلاحيات وقوائم قيم خاصًا بها
(ما يُنتج ازدواجية وتضاربًا حتميًا)، تُبنى هذه القدرات **مرة واحدة، بشكل عام (generic) بالكامل**،
وتُستهلك بيانيًا من أي وحدة عمل — بدءًا بالحسابات العامة كأول وحدة عمل تستهلكها.
لكل واحدة من الوحدات الثلاث سبب وجود مستقل:
- **SEC** يحل مشكلة تشتّت الهوية والصلاحيات: نظام أمان واحد للمنصة بأكملها.
- **MDL** يحل مشكلة انحراف القيم المرجعية (reference-data drift) بين الوحدات.
- **FIN** يحل مشكلة الاعتماد على أرصدة مخزَّنة وغير موثوقة في الأنظمة القديمة، عبر دفتر
  أستاذ يُشتق كل رصيد فيه من القيود المُرحَّلة فقط، لا من عمود رصيد مُجمَّع يفقد التزامنه.

## 3. RESPONSIBILITIES

| الوحدة | تملك | لا تملك |
|---|---|---|
| SEC | تسجيل الدخول/التسجيل/استرجاع كلمة المرور، المستخدمون، الأدوار، التفويض الهرمي (Module→Screen→Action)، القائمة الديناميكية، لوحة تحكم الأمان، سجل التدقيق | أي منطق عمل خاص بوحدة أخرى |
| MDL | نوع اللوكب (Lookup Type) + قيمه (Lookup Value)، شاشة عامة واحدة Master-Detail لكل القوائم، تسجيل الملكية (namespacing) لكل وحدة | معنى القوائم الخاص بمجال وحدة أخرى — الملكية الدلالية تبقى للوحدة المسجِّلة |
| FIN | شجرة الحسابات والأبعاد، محرك القواعد (event_type → قيد)، دورة حياة القيد، دورة حياة الفترة المحاسبية، التقارير المالية المُشتقة | أي مستخدمين/أدوار/تسجيل دخول خاصة بها، أي جدول lookup خاص بها، أي معرفة بالعالم التجاري المضيف |

## 4. MAIN COMPONENTS

| # | Component | Module code | Bounded context | Category (user-defined) | Core / extension | Notes |
|---|-----------|-------------|-----------------|--------------------------|------------------|-------|
| 1 | الأمان / Security | SEC | organization | Foundation | Core | KB §1 Tier 0 — يجب أن يوجد قبل أي وحدة أعمال؛ لا وحدة تملك أمانها الخاص |
| 2 | البيانات المرجعية / Master Data Lookup | MDL | organization | Foundation | Core | KB §1 Tier 0 — مركز واحد لكل القوائم المُرمَّزة عبر المنصة |
| 3 | الحسابات العامة / Finance (General Ledger) | FIN | finance | Business — Tier 1 | Core | KB §1 Tier 1 — أول وحدة عمل تستهلك SEC وMDL؛ قابلة للتوصيل بأي مضيف |
| 4 | الهيكل التنظيمي / Organization | ORG | organization | Foundation | (غير مفصّلة هذه الدفعة) | من `profiles/erp.yaml → vocabulary.module_prefixes` — PROPOSED سابقًا في الملف الشخصي، خارج نطاق هذه الجلسة |
| 5 | المشتريات / Procurement | PRC | supply | Business — Tier 1 | (غير مفصّلة هذه الدفعة) | من الملف الشخصي؛ خارج النطاق |
| 6 | الموارد البشرية / Human Resources | HR | people | Business — Tier 2 | (غير مفصّلة هذه الدفعة) | من الملف الشخصي؛ خارج النطاق |
| 7 | المخزون / Inventory | INV | supply | Business — Tier 1 | (غير مفصّلة هذه الدفعة) | من الملف الشخصي؛ خارج النطاق |
| 8 | المبيعات / Sales | SLS | commercial | Business — Tier 2 | (غير مفصّلة هذه الدفعة) | من الملف الشخصي؛ خارج النطاق |
| 9 | العقود / Contracts | CTR | commercial | Business — Tier 2 | (غير مفصّلة هذه الدفعة) | من الملف الشخصي؛ خارج النطاق |

الصفوف 1–3 مصدرها خطط الوحدات الثلاث المرفقة لهذه الجلسة (security-module-plan-en.md،
lookup-module-plan-en.md، general-accounting-system-plan-en.md)؛ الصفوف 4–9 مصدرها
`profiles/erp.yaml → vocabulary.module_prefixes` المُثبَّت مسبقًا من قِبل المستخدم — تُدرَج هنا
للاكتمال المرجعي فقط ولا تُفصَّل في هذه الدفعة.

## 5. GOVERNING RULES

| # | القاعدة | المصدر |
|---|---|---|
| G1 | كل ما يمكن أن يتغير = بيانات مُعرَّفة، لا شيفرة (no hardcode / no duplication / no contradiction) | الخطط الثلاث §Governing rule؛ [KB:erp-domain-standards §2-3] |
| G2 | نظام أمان واحد للمنصة بأكملها؛ لا وحدة تملك مستخدمين/أدوار/دخولاً خاصًا بها | security-module-plan-en.md §2 |
| G3 | بوابة الوحدة (module gate) تُفحص أولاً، قبل أي فحص شاشة/إجراء؛ عدم امتلاك الوحدة = غياب تام من القائمة ومن الوصول المباشر بالرابط | security-module-plan-en.md §4.2 |
| G4 | مركز واحد وموثوق للبيانات المرجعية؛ لا وحدة تحتفظ بجداول lookup خاصة بها | lookup-module-plan-en.md §2؛ بحث: نمط "MDM hub" — راجع قسم 9 |
| G5 | التخزين والشاشة مركزيان، لكن المعنى الدلالي للقائمة يبقى ملكًا للوحدة المسجِّلة (namespacing بالمالك) | lookup-module-plan-en.md §2, §3 |
| G6 | الحسابات لا تعرف شيئًا عن العالم التجاري المضيف؛ لا اسم حساب داخل حمولة الحدث (event payload) | general-accounting-system-plan-en.md §3, §15 |
| G7 | تساوي المدين والدائن ثابت مطلق (debit = credit invariant) لكل قيد يصل POSTED | general-accounting-system-plan-en.md §12.1 |
| G8 | لا موافقة على مستوى القيد الفردي؛ نقطة التحكم البشري الوحيدة هي إغلاق الفترة، وفصل المهام بين منشئ القيد ومعتمد الإغلاق يُنفَّذ عبر SEC | general-accounting-system-plan-en.md §8.2, §10.3 |
| G9 | الأرصدة تُشتق دائمًا من القيود المُرحَّلة (POSTED) فقط، ولا يوجد عمود رصيد مُخزَّن يُعتمَد عليه | general-accounting-system-plan-en.md §11, §12.9 |
| G10 | الهدف الأول لقاعدة البيانات هو PostgreSQL؛ Oracle/ADF القديم مصدر أحداث فقط | الخطط الثلاث §1؛ توجيه GENERATION-INSTRUCTIONS.md |
| G11 | اللغتان العربية والإنجليزية إلزاميتان في كل قطعة مُسمّاة (وحدة/كيان/حقل/شاشة) | `profiles/erp.yaml → languages` |
| G12 | لا محرك سير عمل (workflow engine) في هذه المنصة | `profiles/erp.yaml → conventions.workflow_engine: forbidden` |

## 6. RELATIONSHIPS WITH OTHER DOMAINS

| This component | Depends on | Kind | Direction | Stated by |
|---|---|---|---|---|
| كل وحدة عمل (بما فيها FIN لاحقًا كل وحدة أخرى) | SEC | HARD (تسجيل الوحدة/الشاشات/الإجراءات كبيانات + بوابة الوحدة) | consumer → SEC | security-module-plan-en.md §7 |
| كل وحدة عمل (بما فيها FIN) | MDL | HARD (تسجيل أنواع lookup كبيانات + قراءة القيم) | consumer → MDL | lookup-module-plan-en.md §4 |
| FIN | SEC | HARD-FK (هوية + صلاحيات الشاشات/الإجراءات + SoD) | FIN → SEC | general-accounting-system-plan-en.md §2 |
| FIN | MDL | HARD-FK (طرق الدفع، أنواع أحداث المحاسبة، أنواع الحسابات، حالات الفترة، أنواع اليومية) | FIN → MDL | general-accounting-system-plan-en.md §5.2 |
| FIN | Notifications (جاهزة، خارج هذه الجلسة) | SOFT/EVENT — اختياري فقط | FIN → NOTIF | general-accounting-system-plan-en.md §2.3؛ `new project/integration-notifications-fileservice.md` |
| FIN | File Service (جاهزة، خارج هذه الجلسة) | SOFT/EVENT — اختياري فقط | FIN → FILESVC | general-accounting-system-plan-en.md §2.3؛ `new project/integration-notifications-fileservice.md` |
| SEC | Notifications (جاهزة) | SOFT — اختياري (مثال: بريد إعادة تعيين كلمة المرور) | SEC → NOTIF | security-module-plan-en.md §8 |
| FIN | نظام مضيف (host business system) | EVENT فقط، عبر حدث محاسبي قياسي (canonical event)؛ لا قراءة ولا كتابة مباشرة لجداول المضيف | host → FIN (event only) | general-accounting-system-plan-en.md §3 |

## 7. STEERING  (read verbatim by every later stage)

### 7.1 Ubiquitous language

| Term (ar/en) | Definition | Do not say | Module code |
|---|---|---|---|
| بوابة الوحدة / Module gate | الفحص الأول والحاسم لامتلاك الدور للوحدة قبل أي فحص شاشة/إجراء؛ غيابها = غياب تام | "صلاحية الوحدة" بمعنى فضفاض | SEC |
| منح الشاشة / Screen grant | صلاحية وصول لشاشة محددة داخل وحدة ممنوحة فعلاً | "صلاحية القائمة" | SEC |
| منح الإجراء / Action grant | صلاحية VIEW/CREATE/UPDATE/DELETE أو إجراء مخصّص على شاشة ممنوحة | "دور" (Role يبقى مصطلحًا مستقلاً) | SEC |
| الشاشة المركّبة / Composite Screen | بحث + إدخال (أو رئيسي + تفصيلي، أو معالج) تُعامَل كشاشة واحدة بمعرّف SCR واحد | "صفحة" منفردة لكل جزء | (عام) |
| نوع اللوكب / Lookup Type | الـ"master" لقائمة قيم مُرمَّزة، يملكه اسميًا موديول مُسجِّل | "جدول Enum" | MDL |
| قيمة اللوكب / Lookup Value | الـ"detail" — قيمة مُرمَّزة ضمن نوع لوكب: كود، تسميتان، ترتيب، حالة نشاط | "قيمة ثابتة" في الشيفرة | MDL |
| الحدث المحاسبي القياسي / Canonical accounting event | مدخل الحسابات الوحيد؛ حدث جاهز الشكل قادم من مستهلك الأحداث خارج النطاق | "معاملة تجارية" (يحمل دلالة عالم المضيف) | FIN |
| شجرة الحسابات / Chart of Accounts | بنية هرمية للحسابات؛ الأوراق فقط تقبل ترحيلاً مباشرًا | "دليل حسابات" بلا بنية هرمية | FIN |
| البُعد / Dimension | مقطع بيانات (segment) يُعرَّف كبيانات ليُشكّل مع الحساب الأساسي تركيبة الترحيل | "تصنيف تحليلي" غامض | FIN |
| الترحيل / Posting | إدخال قيد بحالة POSTED مؤثرًا في الأرصدة وغير قابل للتعديل | "اعتماد" (الاعتماد مصطلح مختلف يخص إغلاق الفترة) | FIN |
| قيد اليومية / Journal Entry | وحدة الإدخال المحاسبي الأساسية (رأس + سطور متوازنة مدين/دائن) | "سند" فقط دون تحديد | FIN |
| الفترة المحاسبية / Accounting Period | نافذة زمنية بحالة (Open / Soft Close / Hard Close / Year-End Close) تتحكم بقبول الترحيل | "شهر مالي" | FIN |
| قيد العكس / Reversing Entry | تصحيح عبر قيد جديد مرتبط ثنائي الاتجاه بالأصل، مطابق سطرًا بسطر بعكس الاتجاه | "حذف القيد" (ممنوع) | FIN |
| ميزان المراجعة / Trial Balance | تقرير متوازن دائمًا، مُشتق من القيود المُرحَّلة فقط | "كشف حساب" | FIN |

### 7.2 Bounded contexts

| Context | Owns module codes | Boundary statement |
|---|---|---|
| organization | ORG, SEC, MDL | القدرات المؤسِّسة (Tier 0) التي يعتمد عليها أي سياق آخر: الهيكل التنظيمي، الأمان، البيانات المرجعية |
| supply | PRC, INV | تدفقات التوريد والمخزون (خارج نطاق هذه الدفعة) |
| finance | FIN | الحسابات العامة ودفتر الأستاذ؛ تستهلك organization ولا تُنتج له شيئًا |
| people | HR | الموارد البشرية (خارج نطاق هذه الدفعة) |
| commercial | SLS, CTR | المبيعات والعقود (خارج نطاق هذه الدفعة) |

(منقولة حرفيًا من `profile.vocabulary.bounded_contexts`)

### 7.3 Module prefixes proposal

| Code | Display | Status |
|---|---|---|
| ORG | Organization | IN PROFILE |
| SEC | Security | IN PROFILE — هذه الدفعة |
| MDL | Master Data Lookup | IN PROFILE — هذه الدفعة |
| PRC | Procurement | IN PROFILE |
| FIN | Finance | IN PROFILE — هذه الدفعة |
| HR | Human Resources | IN PROFILE |
| INV | Inventory | IN PROFILE |
| SLS | Sales | IN PROFILE |
| CTR | Contracts | IN PROFILE |

كل الرموز موجودة مسبقًا في `profiles/erp.yaml → vocabulary.module_prefixes`؛ لا رمز جديد اقترحته
هذه الجلسة.

### 7.4 Identifier rules

المعرّفات اللاحقة تُبنى بالصيغة `{prefix}-{MOD}-{seq}` بعرض تسلسل 3 خانات
(`factory.ids.pattern`, `factory.ids.seq_width`). أنواع الكيانات: master, transactional,
lookup, config, security (`profile.vocabulary.entity_kinds`).

### 7.5 Knowledge sources to cite

- `profiles/erp/knowledge/erp-domain-standards.md`
- `new project/security-module-plan-en.md` — المصدر التأسيسي لوحدة SEC
- `new project/lookup-module-plan-en.md` — المصدر التأسيسي لوحدة MDL
- `new project/general-accounting-system-plan-en.md` — المصدر التأسيسي لوحدة FIN، بما فيه القسم
  12 "details the analysis agent MUST honor" المُلزِم لكل تحليل لاحق
- `new project/integration-notifications-fileservice.md` — يُستخدم فقط عند حاجة فعلية مذكورة
  صراحة في إحدى الخطط الثلاث (لا يُعاد تصميمه)
- plus the research sources in block 9

## 8. RESOLVED DECISIONS

| # | Point | Decision | Recommended by dialogue? | Confirmed by user | Sources |
|---|---|---|---|---|---|
| 1 | هدف قاعدة البيانات | PostgreSQL هو الهدف الوحيد لهذا البناء؛ Oracle/ADF يبقى مصدر أحداث فقط | لا — منصوص صراحة | نعم — منصوص في الخطط الثلاث وفي أمر التنفيذ | الخطط الثلاث §1؛ GENERATION-INSTRUCTIONS.md |
| 2 | نموذج الأمان | RBAC هرمي بثلاث مستويات (Module→Screen→Action) بديلاً عن أي أمان محلي بالوحدات | لا — منصوص صراحة | نعم | security-module-plan-en.md §4 |
| 3 | نموذج البيانات المرجعية | مركز lookup عام Master-Detail واحد لكل المنصة، بدل جداول lookup محلية | لا — منصوص صراحة | نعم | lookup-module-plan-en.md §2-3 |
| 4 | نموذج اعتماد قيود المحاسبة | لا اعتماد على مستوى القيد الفردي؛ الاعتماد الوحيد عند إغلاق الفترة فقط | لا — منصوص صراحة، ويتوافق مع ممارسات GL الحديثة القائمة على الأحداث (انظر قسم 9، R1) | نعم | general-accounting-system-plan-en.md §8 |
| 5 | نطاق هذه الدفعة | SEC ثم MDL ثم FIN فقط، بهذا الترتيب الصارم؛ باقي الوحدات خارج النطاق الآن | لا — منصوص صراحة | نعم | GENERATION-INSTRUCTIONS.md §3 |
| 6 | استخدام Notifications/File Service | تكامل اختياري بحت، فقط عند حاجة صريحة يذكرها أحد الخطط الثلاث؛ لا إعادة تصميم لهما | لا — منصوص صراحة | نعم | الخطط الثلاث §8/§5/§2.3؛ GENERATION-INSTRUCTIONS.md §4.6 |

## 9. RESEARCH LOG

| # | Point | What established systems do | Source(s) (title, URL/path, date) | Used in |
|---|---|---|---|---|
| R1 | RBAC هرمي بمستوى module→screen→action | الأنظمة الناضجة تفصل "ما الذي يمكن فعله" (action) عن "أين" (scope/module)، وتستخدم الهرمية لتقليل تكرار الأدوار؛ التفويض الهرمي يُستخدم بحيث تتحكم صلاحية بوحدة كاملة وأخرى بإجراء داخلها | [How to Design an RBAC System — NocoBase](https://www.nocobase.com/en/blog/how-to-design-rbac-role-based-access-control-system), accessed 2026-09-10; [Access Control Design for Scalable RBAC Systems](https://www.loginradius.com/blog/identity/design-effective-rbac-system), accessed 2026-09-10 | G3، §7.1 "بوابة الوحدة" |
| R2 | مركز بيانات مرجعية موحّد (MDM hub) | النمط الشائع هو مركز واحد (hub) يخزن البيانات المرجعية/الأساسية ويُنشرها للأنظمة الأخرى؛ النطاقات (domains) تتوافق مع بيانات مرجعية مُدارة مركزيًا بدل نسخ محلية متضاربة | [Why the Data Hub is the Future of Data Management — Semarchy](https://www.semarchy.com/blog/backtobasics-mdm-hub-patterns/), accessed 2026-09-10 | G4/G5، وحدة MDL بأكملها |
| R3 | محاسبة قائمة على الأحداث (event-driven GL) | الأنظمة الحديثة تدمج دفتر الأستاذ مع معمارية قائمة على الأحداث: مصدر يُصدر معاملات، خدمة تحقق/تطبيع، ثم خدمة ترحيل تطبّق قاعدة القيد المزدوج وتُلحق القيود في مخزن إلحاقي فقط (append-only)؛ من التحديات الشائعة الأحداث المكرَّرة التي تُسبب ترحيلاً مزدوجًا | [General Ledger Postings: A Comprehensive Guide — Dualentry](https://www.dualentry.com/blog/general-ledger-postings), accessed 2026-09-10 | G7/G9، §12.12 "idempotency at the boundary" في خطة FIN |

## 10. OPEN ITEMS

لا يوجد — النطاق محدَّد بالكامل من الخطط الثلاث المرفقة وتوجيهات GENERATION-INSTRUCTIONS.md؛
لا نقطة غموض تتطلب حوارًا إضافيًا مع المستخدم في هذه المرحلة.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: project-registry>>>
# PROJECT REGISTRY — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile            : erp
Registry Version   : 1.3.0
Domain Profile     : erp/domain-profile.md v1
Last Updated       : 2026-09-10 by P3.1 (FIN v1 pass-1 completion — batch complete)
Modules registered : 9   Entity candidates : 29 (13 SEC + 2 MDL + 14 FIN)   Open items : 0
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
| 1.1.0 | 2026-09-10 | SEC v1 registered a new module (pass-1 complete, gate APPROVE) — minor bump per RULE-2 |
| 1.2.0 | 2026-09-10 | MDL v1 registered a new module (pass-1 complete, gate APPROVE) — minor bump per RULE-2 |
| 1.3.0 | 2026-09-10 | FIN v1 registered a new module (pass-1 complete, gate APPROVE) — minor bump per RULE-2; this batch (SEC→MDL→FIN) is now complete |

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
| 1 | SEC | Security | organization | Foundation | Core | pass-1 COMPLETE (v1, gate APPROVE) | domain-profile §4 row 1 |
| 2 | MDL | Master Data Lookup | organization | Foundation | Core | pass-1 COMPLETE (v1, gate APPROVE) | domain-profile §4 row 2 |
| 3 | FIN | Finance (General Ledger) | finance | Business — Tier 1 | Core | pass-1 COMPLETE (v1, gate APPROVE) | domain-profile §4 row 3 |
| 4 | ORG | Organization | organization | Foundation | — | RESERVED — not this batch | domain-profile §4 row 4; profile |
| 5 | PRC | Procurement | supply | Business — Tier 1 | — | RESERVED — not this batch | domain-profile §4 row 5; profile |
| 6 | HR | Human Resources | people | Business — Tier 2 | — | RESERVED — not this batch | domain-profile §4 row 6; profile |
| 7 | INV | Inventory | supply | Business — Tier 1 | — | RESERVED — not this batch | domain-profile §4 row 7; profile |
| 8 | SLS | Sales | commercial | Business — Tier 2 | — | RESERVED — not this batch | domain-profile §4 row 8; profile |
| 9 | CTR | Contracts | commercial | Business — Tier 2 | — | RESERVED — not this batch | domain-profile §4 row 9; profile |

## ENTITY OWNERSHIP
| ENT id | Name | Owner module | Kind | PRIVATE/SHARED | Status |
|---|---|---|---|---|---|
| ENT-SEC-001 | User | SEC | security | SHARED (owner) | REGISTERED |
| ENT-SEC-002 | Role | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-003 | UserRoleAssignment | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-004 | ModuleRegistry | SEC | security | SHARED (owner) | REGISTERED |
| ENT-SEC-005 | ScreenRegistry | SEC | security | SHARED (owner) | REGISTERED |
| ENT-SEC-006 | ActionRegistry | SEC | security | SHARED (owner) | REGISTERED |
| ENT-SEC-007 | RoleModuleGrant | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-008 | RoleScreenGrant | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-009 | RoleActionGrant | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-010 | ActiveSession | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-011 | AuditLogEntry | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-012 | PasswordResetToken | SEC | security | PRIVATE | REGISTERED |
| ENT-SEC-013 | SignupRequest | SEC | security | PRIVATE | REGISTERED |
| ENT-MDL-001 | LookupType | MDL | master | SHARED (owner) | REGISTERED |
| ENT-MDL-002 | LookupValue | MDL | lookup | SHARED (owner) | REGISTERED |
| ENT-FIN-001 | Account | FIN | master | PRIVATE | REGISTERED |
| ENT-FIN-002 | Dimension | FIN | config | PRIVATE | REGISTERED |
| ENT-FIN-003 | DimensionValue | FIN | lookup | PRIVATE | REGISTERED |
| ENT-FIN-004 | JournalEntry | FIN | transactional | PRIVATE | REGISTERED |
| ENT-FIN-005 | JournalLine | FIN | transactional | PRIVATE | REGISTERED |
| ENT-FIN-006 | JournalLineDimension | FIN | transactional | PRIVATE | REGISTERED |
| ENT-FIN-007 | FiscalYear | FIN | master | PRIVATE | REGISTERED |
| ENT-FIN-008 | FiscalPeriod | FIN | master | PRIVATE | REGISTERED |
| ENT-FIN-009 | EventTypeRule | FIN | config | PRIVATE | REGISTERED |
| ENT-FIN-010 | RuleLine | FIN | config | PRIVATE | REGISTERED |
| ENT-FIN-011 | RecurringTemplate | FIN | config | PRIVATE | REGISTERED |
| ENT-FIN-012 | RecurringTemplateLine | FIN | config | PRIVATE | REGISTERED |
| ENT-FIN-013 | AllocationRule | FIN | config | PRIVATE | REGISTERED |
| ENT-FIN-014 | AllocationTarget | FIN | config | PRIVATE | REGISTERED |
(Source: erp/modules/SEC/P1/registry-srs-sec.md, erp/modules/MDL/P1/registry-srs-mdl.md,
erp/modules/FIN/P1/registry-srs-fin.md)

## SHARED ENTITY DECLARATIONS
| Entity | Owner ENT id | Owner module | Consumers so far |
|---|---|---|---|
| User | ENT-SEC-001 | SEC | every future module, for its own audit fields (createdBy/updatedBy reference a SEC principal string, not a physical FK — see SEC db-script §3 AUDIT COLUMNS rule; declared here as the canonical identity source, not as a live FK target) |
| ModuleRegistry | ENT-SEC-004 | SEC | every future module registers one row of itself here (API-SEC-018) |
| ScreenRegistry | ENT-SEC-005 | SEC | every future module registers its screens here (API-SEC-019) |
| ActionRegistry | ENT-SEC-006 | SEC | every future module registers its actions here (API-SEC-020) |
| LookupType | ENT-MDL-001 | MDL | every future module registers its own lookup types here (API-MDL-002) |
| LookupValue | ENT-MDL-002 | MDL | every future module reads active values by key here (API-MDL-011) |

## STRUCTURAL / IMPLEMENTATION REGISTRY
| Module | Version | Tables | DBF range | API range | XM range |
|---|---|---|---|---|---|
| SEC | v1 | 13 (SEC_USER … SEC_SIGNUP_REQUEST) | DBF-SEC-001 … DBF-SEC-104 | API-SEC-001 … API-SEC-027 (QR-SEC-001…038) | none (ROOT) |
| MDL | v1 | 2 (MDL_LOOKUP_TYPE, MDL_LOOKUP_VALUE) | DBF-MDL-001 … DBF-MDL-021 | API-MDL-001 … API-MDL-011 (QR-MDL-001…015) | XM-MDL-001 (SOFT-READ → SEC, ACTIVE) |
| FIN | v1 | 14 (FIN_ACCOUNT … FIN_ALLOCATION_TARGET) | DBF-FIN-001 … DBF-FIN-146 | API-FIN-001 … API-FIN-032 (QR-FIN-001…044) | XM-FIN-001 (SOFT-READ → MDL, ACTIVE) |

## CROSS-MODULE DEPENDENCY INDEX
| Candidate ref | Kind | From module | To module | Consumes | Status | Evidence |
|---|---|---|---|---|---|---|
| XM-CAND-001 | — | FIN | SEC | RESOLVED — identity/authorization + SoD are enforced via the platform-standard interceptor (narrated in FIN's P3.1 Phase 1/Phase 7), not a formal XM row; see ADR-FIN-001 | RESOLVED — not an XM (no physical cross-module FK) | domain-profile §6 row "FIN \| SEC \| HARD-FK" (superseded) |
| XM-CAND-002 | — | FIN | MDL | RESOLVED — see XM-FIN-001 below; the platform-summary/module-registry candidate assumed HARD-FK, P2 correctly reclassified to SOFT-READ (ADR-FIN-001) | RESOLVED | domain-profile §6 row "FIN \| MDL \| HARD-FK" (superseded) |
| XM-MDL-001 | SOFT-READ | MDL | SEC | ModuleRegistry (ENT-SEC-004) — validates a lookup type's owner module code | ACTIVE (assigned, not a candidate) | erp/modules/MDL/P2/db-script-mdl.md §2 |
| XM-FIN-001 | SOFT-READ | FIN | MDL | LookupValue — validates every FIN lookup-backed column's code (13 keys) | ACTIVE (assigned, not a candidate) | erp/modules/FIN/P2/db-script-fin.md §2; erp/decisions/FIN/ADR-FIN-001.md |
FIN's SEC dependency (identity/authorization, self-registration) is not an XM row — see
ADR-FIN-001: no physical cross-module FK exists anywhere in this pipeline.
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
| 7 | ADR-SEC-001 — SEC's owned lookups (USER_STATUS, SIGNUP_STATUS, AUDIT_EVENT_TYPE) stay CHECK-constrained in v1, not in a shared MDL lookup table, since SEC precedes MDL in this batch | ACCEPTED (non-breaking) | erp/decisions/SEC/ADR-SEC-001.md |
| 8 | ADR-SEC-002 — Error-catalog infrastructure rows (not-found, duplicate, invalid-transition, forbidden, invalid-sort, server) are cited as PLATFORM-STD under one umbrella ADR rather than a dedicated SRS RULE each | ACCEPTED (non-breaking) | erp/decisions/SEC/ADR-SEC-002.md |
| 9 | ADR-FIN-001 — FIN's SEC dependencies (identity/authorization, self-registration) are not modeled as XM rows; only XM-FIN-001 (SOFT-READ → MDL, lookup validation) is assigned, since no physical cross-module FK exists anywhere in this pipeline | ACCEPTED (non-breaking) | erp/decisions/FIN/ADR-FIN-001.md |

## OPEN QUESTION INDEX
none — `domain-profile.md` §10 records no open item.

## PIPELINE / PROGRESS STATUS
| Module | Version | Last committed stage | Last gate verdict | Delivered tracks | Tag |
|---|---|---|---|---|---|
| SEC | v1 | P3.1 (pass-1 complete) | APPROVE (pass-1, 2026-09-10) | backend: split done, deliver BLOCKED (no repo linked) | — |
| MDL | v1 | P3.1 (pass-1 complete) | APPROVE (pass-1, 2026-09-10) | backend: split done, deliver BLOCKED (no repo linked) | — |
| FIN | v1 | P3.1 (pass-1 complete) | APPROVE (pass-1, 2026-09-10) | backend: split done, deliver BLOCKED (no repo linked) | — |
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
| 2026-09-10 | P0 | SEC | v1 | P0 completed: SEC (platform-summary, module-registry-sec, business-policies-sec — 11 POL) |
| 2026-09-10 | P0.5 | SEC | v1 | P0.5 completed: SEC — 12 stories; prd-approval APPROVED by ahmed.alsabonabi@gmail.com |
| 2026-09-10 | P1 | SEC | v1 | P1 completed: SEC — 13 entities, 33 requirements, 33 AC, 7 rules, 10 screen requirements, 0 ADR |
| 2026-09-10 | P2 | SEC | v1 | P2 completed: SEC — 13 tables, 104 DBF, 0 XM; ADR-SEC-001 (ACCEPTED) |
| 2026-09-10 | P3.1 | SEC | v1 | P3.1 completed: SEC — 27 API, 38 QR, ALIGN PASSED; ADR-SEC-002 (ACCEPTED) |
| 2026-09-10 | gate:pass-1 | SEC | v1 | GATE pass-1: APPROVE (scores unambiguous 3, verifiable 3, complete 3, consistent 3, singular 3, feasible 3, traceable 2) |
| 2026-09-10 | split | SEC | v1 | backend/exec split: 15 files, verify ok (39 checked) |
| 2026-09-10 | P0 | MDL | v1 | P0 completed: MDL (platform-summary, module-registry-mdl, business-policies-mdl — 6 POL) |
| 2026-09-10 | P0.5 | MDL | v1 | P0.5 completed: MDL — 5 stories; prd-approval APPROVED by ahmed.alsabonabi@gmail.com |
| 2026-09-10 | P1 | MDL | v1 | P1 completed: MDL — 2 entities, 13 requirements, 13 AC, 4 rules, 2 screen requirements, 0 ADR |
| 2026-09-10 | P2 | MDL | v1 | P2 completed: MDL — 2 tables, 21 DBF, 1 XM (XM-MDL-001, SOFT-READ → SEC) |
| 2026-09-10 | P3.1 | MDL | v1 | P3.1 completed: MDL — 11 API, 15 QR, ALIGN PASSED, 0 new ADR |
| 2026-09-10 | gate:pass-1 | MDL | v1 | GATE pass-1: APPROVE (scores unambiguous 3, verifiable 3, complete 3, consistent 3, singular 3, feasible 3, traceable 3) |
| 2026-09-10 | split | MDL | v1 | backend/exec split: 11 files, verify ok (21 checked) |
| 2026-09-10 | P0 | FIN | v1 | P0 completed: FIN (platform-summary, module-registry-fin, business-policies-fin — 20 POL, incl. all 14 §12 must-honor points) |
| 2026-09-10 | P0.5 | FIN | v1 | P0.5 completed: FIN — 19 stories; prd-approval APPROVED by ahmed.alsabonabi@gmail.com |
| 2026-09-10 | P1 | FIN | v1 | P1 completed: FIN — 14 entities, 46 requirements, 46 AC, 16 rules, 12 screen requirements, 0 ADR |
| 2026-09-10 | P2 | FIN | v1 | P2 completed: FIN — 14 tables, 146 DBF, 1 XM (XM-FIN-001, SOFT-READ → MDL); ADR-FIN-001 (ACCEPTED) |
| 2026-09-10 | P3.1 | FIN | v1 | P3.1 completed: FIN — 32 API, 44 QR, ALIGN PASSED (14-point §12 coverage confirmed), 0 new ADR |
| 2026-09-10 | gate:pass-1 | FIN | v1 | GATE pass-1: APPROVE (scores unambiguous 3, verifiable 3, complete 3, consistent 3, singular 3, feasible 3, traceable 2) |
| 2026-09-10 | split | FIN | v1 | backend/exec split: 15 files, verify ok (45 checked) |
| 2026-09-10 | BATCH | (platform) | — | GENERATION-INSTRUCTIONS.md batch complete: SEC v1 → MDL v1 → FIN v1, all pass-1 APPROVE, in mandated dependency order |
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

---
# KNOWLEDGE (profile primary sources — cite as [KB:<file> §n])

<<<KB: profiles/erp/knowledge/erp-domain-standards.md>>>
# ERP Domain Standards — knowledge base for the `erp` profile

```
Profile   : erp            (profiles/erp.yaml → knowledge.files)
Role      : PRIMARY SOURCE the engines may cite (domain-profile, P0, P1, P2, P3.x)
            when they resolve an ambiguity themselves (factory.yaml → ambiguity).
Replaces  : the former "platform-standards.md Section M" that engines referenced
            but that never existed in the factory.
Rule      : a citation to this file is written as [KB:erp-domain-standards §n].
```

## §1 Module tiers
| Tier | Purpose | Typical modules |
|---|---|---|
| Tier 0 — Foundation | must exist before any business module | Organization (ORG), Security (SEC), Master Data Lookup (MDL) |
| Tier 1 — Core business | first revenue/cost flows | Procurement (PRC), Finance (FIN), Inventory (INV) |
| Tier 2 — Extended business | depends on Tier 1 | Sales (SLS), Contracts (CTR), Human Resources (HR) |

A module may only declare a HARD-FK XM towards a module of the same or a lower tier.

## §2 Entity kinds and defaults
Entity kinds and their default fields are declared in `profiles/erp.yaml → conventions.entity_defaults`.
Rules the engines apply on top:
1. Every master entity is bilingual (`nameAr`, `nameEn`) and soft-deletable (`isActiveFl`).
2. Transactional documents are period-bound (`fiscalYearId`, `periodId`) and status-driven (`statusCode` from a lookup).
3. Lookups are owned by MDL; a module never stores a lookup's display text, only its code.
4. No entity generates its own document numbers — the platform numbering engine does.

## §3 Business-policy conventions (P0 → POL-*)
- A policy is a single, testable sentence in EARS form (see factory.yaml → ids.ears).
- Policies that cross modules are declared once, in the owning (lower-tier) module, and referenced by code elsewhere.
- Fiscal policies (period locking, posting rules) belong to FIN; approval-limit policies belong to the module that owns the document.

## §4 Screens, security and permissions
- Composite screens: Search + Entry (or Master + Detail, Wizard) = ONE `SCR-*` and ONE `SEC_PAGES` row.
- Permission pattern and gateway action: `profiles/erp.yaml → conventions.security_model`.
- Backend: one controller per composite screen; authorization per method (gateway action on reads; CREATE/UPDATE/DELETE on mutations).
- Frontend: one lazily-loaded chunk per composite screen; Search↔Entry via route params.

## §5 Cross-module dependencies (XM)
- `HARD-FK`: a physical foreign key to another module's table — allowed only downward in tier.
- `SOFT-READ`: a read-only lookup by code — allowed in any direction.
- Every XM cites the `REQ-*` that needs it; the consuming module owns the XM record.

## §6 Defaults an engine may assume without asking (after PRD approval)
| Question | Default |
|---|---|
| Soft delete vs hard delete | soft (`isActiveFl`) |
| Audit trail | the four audit fields on every table |
| Paging | server-side, page size 20, max 200 |
| Search | server-side filter on code/name (both languages) |
| Money | `NUMERIC(18,4)`, currency code from MDL |
| Dates | `TIMESTAMPTZ`, stored UTC, displayed in tenant timezone |

Anything not covered here becomes an ADR (`decisions/<MOD>/`) per the ambiguity rule.

<<<END KB>>>

---
# PREVIOUS ROUND
I wrote the three P0 artifacts and verified them: `gov.py analyze -m NOTE -v 1 --scope all` reports **no C3 findings** (all of C3.1–C3.7 pass and each examined something); the remaining findings are downstream stages that haven't run yet, plus one pre-existing platform-registry gap noted below.

<<<FILE: erp/modules/NOTE/P0/platform-summary.md>>>
# PLATFORM SUMMARY — منصة تخطيط موارد المؤسسات (ERP Platform)
══════════════════════════════════════════════════════════════════
Profile : erp   Domain profile : v1   Registry : v1.3.0
══════════════════════════════════════════════════════════════════

## OVERVIEW
منصة ERP متعددة الوحدات، قائمة على مبدأ "كل ما يمكن أن يتغير = بيانات، لا شيفرة"، تُبنى
بـ Spring (خلفية) وReact (واجهة) على PostgreSQL. دفعة الوحدات الثلاث (SEC → MDL → FIN)
اكتملت بالكامل (pass-1 APPROVE لكل وحدة) [project-registry PIPELINE/PROGRESS STATUS].
هذه الجلسة تُضيف وحدة رابعة صغيرة ومستقلة تمامًا: **NOTE (الملاحظات / Notes)** — مستخدم
يكتب ملاحظة قصيرة ويقرأ ملاحظاته هو فقط. الوحدة مقصودة الصِّغَر: كيان واحد، أربع عمليات
(إنشاء · تعديل · تعطيل · بحث ضمن ملاحظات المستخدم نفسه)، شاشة واحدة، مجموعة صلاحيات
واحدة، وصفر اعتماديات بين الوحدات. حجمها هذا **قيد مُلزِم لكل مرحلة لاحقة**، لا نقطة
انطلاق قابلة للتوسيع.
The platform is a multi-module ERP built as data, not code. The three-module batch
(SEC → MDL → FIN) is complete; this run adds one small, fully self-contained module,
NOTE (Notes): a user writes a short note and reads their own notes back.

## MODULES
| #   | Code | Module (ar/en) | Bounded context | Layer | Type | Depends on | Status |
|-----|------|--------|-----------------|-------|------|------------|--------|
| 1.1 | ORG | الهيكل التنظيمي / Organization | organization | L1 | master data | ROOT | NEW (not this run) |
| 1.2 | SEC | الأمان / Security | organization | L1 | security engine | ROOT | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 1.3 | MDL | البيانات المرجعية / Master Data Lookup | organization | L1 | reference | SEC (SOFT-READ) | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 1.4 | NOTE | الملاحظات / Notes | productivity | L1 | master data | ROOT — none | NEW — this run |
| 2.1 | PRC | المشتريات / Procurement | supply | L3 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 2.2 | FIN | الحسابات العامة / Finance (GL) | finance | L3 | transactional/reporting | SEC (HARD), MDL (HARD) | **EXCEPTION — pass-1 COMPLETE, read as-is** |
| 2.3 | INV | المخزون / Inventory | supply | L3 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 3.1 | SLS | المبيعات / Sales | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 3.2 | CTR | العقود / Contracts | commercial | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
| 3.3 | HR | الموارد البشرية / Human Resources | people | L4 | transactional | SEC, MDL (not yet detailed) | NEW (not this run) |
Status: NEW (Phase 2 produces) · EXISTING (Phase 2 extends) · EXCEPTION (read as-is)
Numbering: [tier].[sequence within tier] — the user requests Phase 2 by this number.
أرقام 1.1–3.3 مُثبَّتة من دورات P0 السابقة ولم يتغير أي منها؛ NOTE أخذ الرقم التالي في
الطبقة الأولى (1.4) تطبيقًا لقاعدة ثبات الترقيم.
This run's Phase 2 request: **1.4 NOTE** (module convergence in module-registry-note.md).

## DEPENDENCY MAP
Build order: Tier 1 [ORG, SEC, MDL, NOTE] → Tier 2 [PRC, FIN, INV] → Tier 3 [SLS, CTR, HR] → Tier 4 (reporting, none yet)
Key dependencies (one line each):
  NOTE → (none) : لا اعتمادية وحدة-إلى-وحدة إطلاقًا — لا XM، لا lookup، لا بيانات أجنبية / no XM, no lookup, no foreign data
  NOTE → PLATFORM-STD → (identity & authorization) : الهوية والصلاحيات تصل عبر المعترِض القياسي للمنصة وتسجيل الوحدة لنفسها، وهو نمط منصّة لا صف XM (سابقة ADR-FIN-001)
  FIN → HARD → SEC : identity + grants + SoD (recorded in the completed batch, unchanged here)
  FIN → HARD → MDL : lookup-backed codes (recorded in the completed batch, unchanged here)
  (host business system) → EVENT → FIN : canonical accounting event only (unchanged here)

## DEFERRED (not in scope for this version)
| Item | Reason / activation trigger |
| ORG, PRC, HR, INV, SLS, CTR detailed analysis | out of the current scope; activate when a batch names them |
| Workflow engine | profile: `forbidden` |
| مشاركة الملاحظات بين المستخدمين / note sharing between users | خارج الرؤية صراحة: "reads their own notes back"؛ يُفعَّل فقط إذا طلب المستخدم مشاركة صريحة |
| تصنيف/وسوم/مرفقات الملاحظة / note categories, tags, attachments | ستجاوز حدّ "كيان واحد"؛ كل توسيع هنا مخالفة نطاق تُسجَّل كـ finding |
| ربط NOTE بأي وحدة أخرى (lookup أو FK) / any NOTE↔module link | الرؤية تنص على صفر اعتماديات؛ يُفعَّل بقرار صريح لاحق فقط |

## RESOLVED DECISIONS (this phase)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | السياق المحدود لوحدة NOTE — لا ينتمي لأي سياق في الملف الشخصي / NOTE's bounded context | سياق جديد `productivity` يملك NOTE وحده، سطر واحد في `profiles/erp.yaml → vocabulary.bounded_contexts` | موصى به — ينتظر تأكيد المستخدم؛ الملف الشخصي نفسه يسمح: "a new module can join an existing context or start a new one" | profiles/erp.yaml vocabulary.bounded_contexts (تعليق); domain-profile §7.2 |
| 2 | الطبقة والترقيم / tier and number | Tier 1، الرقم 1.4 — الوحدة بلا اعتماديات فتصلح للبناء في أي وقت، ووضعها في طبقة أعلى يوحي باعتمادية غير موجودة | موصى به | [KB:erp-domain-standards §1]; engines/P0 §2.3 number stability |
| 3 | التعارض بين "كل وحدة عمل تعتمد HARD على SEC وMDL" (domain-profile §6) و"صفر اعتماديات" لـ NOTE | لا صف XM لـ NOTE: الهوية/التفويض نمط منصّة قياسي (سابقة ADR-FIN-001: لا مفتاح أجنبي بين الوحدات في هذا الخط أصلًا)، وNOTE لا تملك ولا تستهلك أي قائمة قيم مُرمَّزة فلا يسري G4 عليها | موصى به | domain-profile §6, G2/G4; project-registry DECISION INDEX #9 (ADR-FIN-001); [KB:erp-domain-standards §5] |
| 4 | نوع الكيان: master أم transactional / entity kind | master — الملاحظة ليست مستندًا مرتبطًا بفترة محاسبية ولا مدفوعًا بحالة من lookup، وتُعطَّل تعطيلًا ناعمًا (isActiveFl)، وهو تعريف master في المعيار | موصى به | [KB:erp-domain-standards §2 rules 1–2, §6 soft delete] |
| 5 | ثنائية اللغة في محتوى الملاحظة / bilingual note content | الاصطلاح الثنائي (nameAr/nameEn) لا يسري على محتوى يكتبه المستخدم: العنوان والنص حقل حر واحد بلغة كاتبه — مُثبَّت كسياسة POL-NOTE-005؛ الاصطلاح يبقى ساريًا على أسماء الوحدة والكيان والشاشة | موصى به | [KB:erp-domain-standards §2 rule 1] (انحراف مُعلَن); domain-profile G11; profiles/erp.yaml languages |

## OPEN ITEMS
None — النطاق محدَّد بالكامل: كيان واحد، أربع عمليات، شاشة واحدة، صفر اعتماديات؛ القرارات
الخمس أعلاه تغلق كل نقطة أثارها هذا التحليل.

## NEXT STEP
Module 1.4 NOTE converges in module-registry-note.md and business-policies-note.md.
Requirements begin in P0.5 and later stages; these files are their input.
<<<END FILE>>>

<<<FILE: erp/modules/NOTE/P0/module-registry-note.md>>>
## MODULE REGISTRY — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module Code    : NOTE   (profile.vocabulary.module_prefixes → `NOTE: Notes`)
Bounded context: productivity   (سياق جديد يملك NOTE وحده — platform-summary RESOLVED DECISION #1)
Layer / Type   : L1 / master data     Execution tier : 1.4
Source         : NEW
Knowledge      : profiles/erp/knowledge/erp-domain-standards.md §1, §2, §4, §6; erp/domain-profile.md §7
Readiness      : READY
══════════════════════════════════════════════════════════════════

SCOPE (قيد مُلزِم — binding constraint on every later stage)
كيان واحد · أربع عمليات (إنشاء · تعديل · تعطيل · بحث ضمن ملاحظات المستخدم نفسه) · شاشة
مركّبة واحدة (قائمة + نموذج إنشاء/تعديل) · مجموعة صلاحيات واحدة على تلك الشاشة · صفر
اعتماديات بين الوحدات.
One entity · four operations (create · update · deactivate · search own notes) · one
composite screen (list + create/edit form) · one permission set · zero cross-module
dependencies. أي توسيع لهذا الحجم في مرحلة لاحقة هو مخالفة نطاق، لا تحسين.

ENTITIES OWNED   (names only — entity IDs are assigned by P1)
| Entity (ar/en) | Kind | PRIVATE / SHARED | Source |
|---|---|---|---|
| الملاحظة / Note | master | PRIVATE — لا وحدة أخرى تقرأها؛ الملاحظة مرئية لمالكها فقط (POL-NOTE-001) | رؤية الوحدة: "one entity: note (id, title, body, owner, audit fields, active flag)"; [KB:erp-domain-standards §2] |

LOOKUPS OWNED    (value lists this module masters)
None — الوحدة لا تملك أي قائمة قيم مُرمَّزة. علم النشاط (`isActiveFl`) قيمة منطقية باصطلاح
المنصة، لا نوع lookup [KB:erp-domain-standards §6 soft delete]، فلا شيء يُسجَّل في MDL.
Rule (profile): all LOV values runtime-loaded from the lookup module; no hardcoded enums
in APIs or field specs — تبقى سارية، وهي مُحقَّقة هنا بانعدام أي قائمة قيم أصلًا.

LOOKUPS CONSUMED (from other modules)
| Lookup key | Owner code | READ-ONLY |
None — لا قيمة مُرمَّزة تُقرأ من MDL ولا من غيرها.

SHARED ENTITIES CONSUMED
| Entity | Owner code | HARD-FK / SOFT-READ | Why |
None — لا مفتاح أجنبي ولا قراءة ناعمة لأي كيان خارج الوحدة. مالك الملاحظة يُسجَّل بمعرِّف
الأصل (principal) الذي يسلّمه المعترِض القياسي للمنصة، على نفس نمط حقول التدقيق
(createdBy/updatedBy) المعمول به في الوحدات الثلاث المكتملة — لا ارتباط فيزيائي بجدول وحدة أخرى.

DEPENDENCIES
| Module code | HARD / SOFT / LOOKUP | What is consumed |
None. ROOT: YES
الهوية والتفويض وتسجيل الوحدة/الشاشة/الإجراء تصل عبر النمط القياسي للمنصة لا عبر صف XM —
سابقة مُقرَّة في هذا الخط: ADR-FIN-001 (project-registry DECISION INDEX #9) تنص أن لا مفتاح
أجنبي بين الوحدات في هذه المنصة، وأن اعتماد الهوية/التفويض ليس صف XM. لذلك يُتوقَّع أن تكون
مرحلتا INT-C وINT-R في خطة التنفيذ **فارغتين لكن موجودتين**، لا محذوفتين.

AUTO-DECISIONS
AUTO: الكيان الوحيد مصنَّف master لا transactional
  FROM: [KB:erp-domain-standards §2] — المستند transactional مرتبط بفترة (fiscalYearId/periodId)
        ومدفوع بحالة من lookup، وليس للملاحظة أي من الاثنين؛ بينما التعطيل الناعم (isActiveFl)
        هو بالضبط اصطلاح master نفسه [KB:erp-domain-standards §2 rule 1, §6]
  IF WRONG: أعد تصنيفه transactional في P1 — يستدعي عندئذٍ حقول الفترة وحالة من MDL، أي
        اعتمادية XM جديدة ونموًّا في النطاق؛ لا يُفعَل إلا بقرار صريح.
AUTO: الشاشة المركّبة واحدة (قائمة + نموذج) بمعرّف SCR واحد
  FROM: [KB:erp-domain-standards §4] — Search + Entry = ONE SCR, ONE SEC_PAGES row;
        ومطابق لنص الرؤية "one screen: a list with a create/edit form"
  IF WRONG: فصلها إلى شاشتين يخالف المعيار والرؤية معًا — لا يُوصى به.
AUTO: مجموعة صلاحيات واحدة على تلك الشاشة تحكم العمليات الأربع
  FROM: رؤية الوحدة ("one permission set on that screen") + profiles/erp.yaml
        conventions.security_model (VIEW/CREATE/UPDATE/DELETE على شاشة ممنوحة)
  IF WRONG: إضافة مجموعة ثانية تتطلب شاشة ثانية — أي نموًّا في النطاق.
AUTO: التعطيل ناعم دائمًا، ولا حذف نهائي في أي عملية
  FROM: [KB:erp-domain-standards §6] (soft delete هو الافتراضي) + العملية الرابعة في الرؤية
        اسمها "deactivate" لا "delete"
  IF WRONG: الحذف النهائي يُلغي أثر التدقيق؛ لا يُوصى به.
AUTO: الطبقة L1 والتِّرتيب 1.4، وROOT: YES
  FROM: [KB:erp-domain-standards §1] + انعدام أي اعتمادية؛ engines/P0 §2.3 number stability
  IF WRONG: أعد الترقيم فقط إذا أعيد ترتيب الطبقات منصّيًا؛ الرقم لا ينزاح بعد تثبيته.

RESOLVED DECISIONS (dialogue, this module)
| # | Point | Recommended | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | السياق المحدود / bounded context | `productivity` — سياق جديد يملك NOTE وحده | موصى به — ينتظر تأكيد المستخدم | profiles/erp.yaml vocabulary.bounded_contexts; platform-summary decision #1 |
| 2 | صفر XM مقابل domain-profile §6 | لا صف XM؛ الهوية/التفويض نمط منصّة (سابقة ADR-FIN-001) | موصى به | project-registry DECISION INDEX #9; [KB:erp-domain-standards §5] |
| 3 | نوع الكيان / entity kind | master | موصى به | [KB:erp-domain-standards §2] |
| 4 | ثنائية اللغة في محتوى المستخدم | لا تسري على العنوان/النص؛ تسري على أسماء الوحدة والكيان والشاشة — POL-NOTE-005 | موصى به | domain-profile G11; [KB:erp-domain-standards §2 rule 1] |

POLICIES OWNED (full text in business-policies-note.md)
POL-NOTE-001, POL-NOTE-002, POL-NOTE-003, POL-NOTE-004, POL-NOTE-005, POL-NOTE-006
══════════════════════════════════════════════════════════════════
<<<END FILE>>>

<<<FILE: erp/modules/NOTE/P0/business-policies-note.md>>>
## BUSINESS POLICIES — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module   : NOTE     Source of truth : نص رؤية الوحدة + قرارات هذا الحوار / the module's vision text + this dialogue's resolutions
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)

POL-NOTE-001 — الملاحظة مرئية لمالكها فقط / A note is visible to its owner only
  Statement (ar) : يجب على النظام إتاحة قراءة الملاحظة لمستخدمها المالك دون سواه.
  Statement (en) : The system shall make a note readable only by the user who owns it.
  Pattern   : ubiquitous
  Trigger   : Search / Read
  Rationale : الرؤية تحصر القراءة في ملاحظات المستخدم نفسه — لا مشاركة ولا اطّلاع متبادل
  Source    : vision text — "A user writes a short note and reads their own notes back"; "search (own notes only)"
  Status    : CONFIRMED

POL-NOTE-002 — التعديل والتعطيل للمالك وحده / Owner-only update and deactivation
  Statement (ar) : إذا طلب مستخدم غير مالك الملاحظة تعديلها أو تعطيلها، فيجب على النظام رفض الطلب.
  Statement (en) : If a user who does not own a note requests its update or deactivation, then the system shall reject the request.
  Pattern   : unwanted
  Trigger   : Update / Deactivate
  Rationale : الملكية شرط كتابة كما هي شرط قراءة؛ بغير ذلك تُخترق حدود المالك من جهة الكتابة
  Source    : vision text — "four operations: create · update · deactivate · search (own notes only)"; resolved dialogue decision (module-registry-note.md #1 scope)
  Status    : CONFIRMED

POL-NOTE-003 — التقاعد بالتعطيل لا بالحذف / Retirement by deactivation, never by deletion
  Statement (ar) : يجب على النظام إخراج الملاحظة من الخدمة بالتعطيل وحده.
  Statement (en) : The system shall retire a note by deactivation alone.
  Pattern   : ubiquitous
  Trigger   : Deactivate
  Rationale : الحذف النهائي يُفقد أثر التدقيق؛ العملية الرابعة في الرؤية اسمها "تعطيل" لا "حذف"
  Source    : vision text — "four operations: … deactivate …"; [KB:erp-domain-standards §6 soft delete]
  Status    : CONFIRMED

POL-NOTE-004 — الملاحظة المعطَّلة خارج البحث الافتراضي / A deactivated note stays out of the default search
  Statement (ar) : أثناء كون الملاحظة معطَّلة، يجب على النظام استبعادها من البحث الافتراضي لمالكها.
  Statement (en) : While a note is deactivated, the system shall exclude it from its owner's default search.
  Pattern   : state
  Trigger   : Search
  Rationale : التعطيل يجب أن يُحدث أثرًا ملموسًا للمستخدم، وإلا صار علمًا بلا معنى
  Source    : vision text — "deactivate"; [KB:erp-domain-standards §6]
  Status    : CONFIRMED

POL-NOTE-005 — محتوى الملاحظة بلغة كاتبها / Note content is in its author's own language
  Statement (ar) : يجب على النظام حفظ عنوان الملاحظة ونصها كحقلين حرّين بلغة كاتبهما.
  Statement (en) : The system shall store a note's title and body as free-text fields in their author's own language.
  Pattern   : ubiquitous
  Trigger   : Create / Update
  Rationale : المحتوى الذي يكتبه المستخدم ليس بيانات مرجعية؛ فرض زوج ثنائي اللغة عليه يُلزم
              المستخدم بترجمة ملاحظته الشخصية. تبقى ثنائية اللغة سارية كاملةً على أسماء الوحدة
              والكيان والشاشة (domain-profile G11).
  Source    : resolved dialogue decision (platform-summary RESOLVED DECISIONS #5) — انحراف مُعلَن عن [KB:erp-domain-standards §2 rule 1]
  Status    : CONFIRMED

POL-NOTE-006 — مجموعة صلاحيات واحدة تحكم العمليات الأربع / One permission set governs all four operations
  Statement (ar) : يجب على النظام ضبط عمليات الملاحظة الأربع جميعها بمجموعة صلاحيات واحدة على شاشة الملاحظات الوحيدة.
  Statement (en) : The system shall govern all four note operations through a single permission set on the one Notes screen.
  Pattern   : ubiquitous
  Trigger   : Any authorization check
  Rationale : حجم الوحدة مقصود: شاشة واحدة، مجموعة صلاحيات واحدة — أي مجموعة ثانية تعني شاشة ثانية
  Source    : vision text — "one screen … one permission set on that screen"; [KB:erp-domain-standards §4]
  Status    : CONFIRMED

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
None — لا تملك الوحدة ولا تستهلك أي قائمة قيم مُرمَّزة / the module owns and consumes no coded value list.

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| مشاركة الملاحظة / note sharing | لا مسار لمشاركة ملاحظة مع مستخدم آخر ولا اطّلاع إداري شامل عليها في هذه النسخة / no sharing path and no administrative all-notes view in this version | طلب صريح من المستخدم لمشاركة أو لإشراف إداري | vision text — "reads their own notes back" |
| اعتماديات بين الوحدات / cross-module dependencies | لا XM ولا lookup ولا بيانات أجنبية / no XM, no lookup, no foreign data | قرار صريح لاحق يربط NOTE بوحدة أخرى | vision text — "zero cross-module dependencies" |
| توسيع النموذج / model growth | لا كيان ثانٍ ولا شاشة ثانية (وسوم، تصنيفات، مرفقات، تذكيرات) / no second entity or screen (tags, categories, attachments, reminders) | نسخة لاحقة تُعيد تحديد النطاق صراحة | vision text — "one entity … one screen" |
| ثنائية اللغة لمحتوى المستخدم / bilingual user content | العنوان والنص خارج اصطلاح nameAr/nameEn — انظر POL-NOTE-005 | طلب صريح بمحتوى ثنائي اللغة | [KB:erp-domain-standards §2 rule 1]; domain-profile G11 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | هل يرى مسؤول النظام كل الملاحظات؟ / Does an administrator see every note? | لا — لا استثناء لأي دور في هذه النسخة؛ الملكية هي الحدّ الوحيد (POL-NOTE-001) | موصى به — ينتظر تأكيد المستخدم | vision text — "own notes only"; [KB:erp-domain-standards §4] |
| 2 | ماذا يحدث للملاحظة المعطَّلة؟ / What becomes of a deactivated note? | تبقى محفوظة وتخرج من البحث الافتراضي لمالكها (POL-NOTE-003, POL-NOTE-004) | موصى به | [KB:erp-domain-standards §6] |
| 3 | هل يلزم أن يكون محتوى الملاحظة ثنائي اللغة؟ / Must note content be bilingual? | لا — حقل حر بلغة كاتبه (POL-NOTE-005)، مع بقاء ثنائية اللغة على الأسماء | موصى به | domain-profile G11; [KB:erp-domain-standards §2 rule 1] |
| 4 | هل تُسجَّل NOTE اعتمادية على SEC أو MDL؟ / Does NOTE record a SEC or MDL dependency? | لا — الهوية/التفويض نمط منصّة قياسي (سابقة ADR-FIN-001)، ولا قائمة قيم أصلًا | موصى به | project-registry DECISION INDEX #9; domain-profile §6 |
══════════════════════════════════════════════════════════════════
<<<END FILE>>>

---

## Round 1 — open points, each with a researched recommendation

PROPOSAL 1 — NOTE belongs to no bounded context
  Affects   : platform summary MODULES row 1.4; module-registry header
  Options   : **A)** join `organization` — zero further edits, but that context's boundary statement is "foundational capabilities (Tier 0) every other context depends on", which NOTE is demonstrably not (nothing depends on it). **B)** a new context `productivity` owning NOTE alone — one line in `profiles/erp.yaml → vocabulary.bounded_contexts`.
  Researched: the profile's own comment on `bounded_contexts` says the grouping is "a starting grouping, not a fixed partition — a new module can join an existing context or start a new one; only a tiering deviation from it needs an ADR". So B needs no ADR, and the module code line was already added to the same block.
  Recommended: **B** — filing a user-scoped utility inside the Tier-0 foundation context states something false that P1/P2 tiering rules ([KB:erp-domain-standards §1], HARD-FK only downward) would then have to work around. Cost is one line in the file the run already had to touch.

PROPOSAL 2 — "every business module HARD-depends on SEC and MDL" vs. NOTE's stated zero dependencies
  Affects   : DEPENDENCIES, dependency map, INT-C/INT-R phases downstream
  Options   : **A)** record HARD rows to SEC and MDL per domain-profile §6/G2/G4. **B)** record none; treat identity/authorization as a platform standard.
  Researched: ADR-FIN-001 (project-registry DECISION INDEX #9) already settled that identity/authorization and self-registration are **not** XM rows and that no physical cross-module FK exists anywhere in this pipeline — only XM-FIN-001 (SOFT-READ → MDL for lookup codes) was assigned. NOTE owns and consumes no coded value list at all, so G4 has nothing to bite on.
  Recommended: **B**, on the FIN precedent. Consequence to check downstream: INT-C and INT-R must come out **empty-but-present**, not absent.

PROPOSAL 3 — entity kind for `note`: master or transactional
  Affects   : ENTITIES OWNED; P1 field derivation
  Options   : **A)** `master`. **B)** `transactional`.
  Researched: [KB:erp-domain-standards §2] — transactional documents are period-bound (`fiscalYearId`, `periodId`) and status-driven from a lookup; a note is neither. Soft-deletability (`isActiveFl`) is the master convention, and it matches the vision's fourth operation exactly.
  Recommended: **A**. B would drag in fiscal fields and an MDL status lookup — a new XM and scope growth on a module budgeted at one entity.

PROPOSAL 4 — does the bilingual rule (G11, [KB §2 rule 1] "every master entity is bilingual") apply to note title/body?
  Affects   : POL-NOTE-005; P1 field list; P3.2 screen
  Options   : **A)** apply it — `titleAr`/`titleEn`, `bodyAr`/`bodyEn`. **B)** exempt user-authored content; keep it on module/entity/screen names.
  Researched: G11 and the KB rule are written for *named* platform artifacts (module, entity, field, screen) — reference data a second user must read. A personal note has one reader, its author.
  Recommended: **B**, fixed as POL-NOTE-005 so P1 cannot silently re-apply the convention. Flagging it as an engine observation too: the KB states the bilingual rule as unconditional on `master`, so any master entity holding user-authored content will hit this same friction — it is worth a qualifying clause in `erp-domain-standards.md §2 rule 1`.

PROPOSAL 5 — administrator override on note visibility
  Affects   : POL-NOTE-001, POL-NOTE-002, SCOPE EXCEPTIONS
  Options   : **A)** no override — ownership is the only boundary. **B)** an admin role that reads all notes.
  Researched: the vision says "search (own notes only)" with no exception, and B needs a second permission set, which contradicts "one permission set on that screen".
  Recommended: **A**, recorded as a scope exception with an explicit activation trigger rather than silently omitted.

Nothing is left open in the artifacts themselves — every point above carries a recommended answer already written into a RESOLVED DECISIONS row, so C3.5 (no-questions) passes. I am not appending the convergence marker in round 1; round 2 should accept or amend each proposal.

## Two things worth recording outside this stage

- `analyze --scope all` reports **C2.2 MAJOR: project-registry does not map categories ['CAT-10']**. `shared/REGISTRY-SCHEMA.md` §4 defines CAT-10 (platform findings) but `erp/project-registry.md` v1.3.0 predates it and has no such section. That is the orchestrator's artifact, not a P0 output — a real finding for the smoke run.
- Decision 1 above implies one line in `profiles/erp.yaml`; I did not make that edit, since this brief scopes me to the three P0 files. That makes **two** profile lines a new module costs so far (`module_prefixes`, `bounded_contexts`) — an input for the smoke run's "what a new module touched" tally.

