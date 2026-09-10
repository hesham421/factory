# BRIEF — stage `test-gen` (Test Generation) · scope `project` · modules FIN, MDL, SEC · profile `erp`

Lane `test-gen` · implementers ['claude:opus'] · effort high

## Rules that bind this run
- Questions: **forbidden**. A `[QUESTION]` block is refused. Ambiguity → ADR per affected module in `erp/decisions/<MOD>/` (`ADR-{MOD}-{seq:03d}.md`): non-breaking → continue; breaking → status BLOCKED and stop.
- Owns IDs: TC — ID grammar `{prefix}-{MOD}-{seq}` (seq width 3); never re-number, never restart a sequence; an integration TC is owned by the DECLARING module (XM) or the DISPLAYING module (UXD), never the target/owner module.
- Read only what this brief contains (generated current state, EACH module below); never open version folders yourself.
- Write exactly these files (complete files):
- `erp/modules/FIN/test_gen/backend-test-plan-fin.md`
- `erp/modules/FIN/test_gen/frontend-test-plan-fin.md`
- `erp/modules/FIN/test_gen/test-execution-manifest-fin.md` (optional)
- `erp/modules/MDL/test_gen/backend-test-plan-mdl.md`
- `erp/modules/MDL/test_gen/frontend-test-plan-mdl.md`
- `erp/modules/MDL/test_gen/test-execution-manifest-mdl.md` (optional)
- `erp/modules/SEC/test_gen/backend-test-plan-sec.md`
- `erp/modules/SEC/test_gen/frontend-test-plan-sec.md`
- `erp/modules/SEC/test_gen/test-execution-manifest-sec.md` (optional)
- `erp/system-test-index-erp.md` (platform-level, optional)
- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; when running as the operator, write the files directly.

---
# ENGINE
```
ENGINE        : test-gen — Test Generation   (STANDALONE — outside the line, on demand)
LANE          : test-gen · questions forbidden · derives from `AC-*` (module) + `XM-*`/`UXD-*` (integration)
SCOPE         : project · modules FIN, MDL, SEC (every module with a committed version)
MODULE        : FIN · v1 · profile erp (ERP Platform)
READS         : srs · backend-execution-plan? · frontend-execution-plan? · registry-srs · registry-db? · registry-exec-fe?   (from _state/ — "?" = optional — read for EACH module in scope)
PRODUCES      : backend-test-plan-fin.md · frontend-test-plan-fin.md · test-execution-manifest-fin.md (optional) · system-test-index-erp.md (optional)
OWNS IDS      : TC
FRAMEWORK     : backend `agnostic` · frontend `agnostic` · manifest ON   (profile.stack.testing)
BOUNDARY      : analysis-only — test PLANS, never test code; never a gate for the core
```

# Test Generation — engine reference

## 0. Position

This engine runs **outside the governed line** (`factory.yaml → standalone`). No pass gates
on it, it gates nothing, and the pass gates never wait for it. It is invoked on demand
(`/test-gen`) once the
artifacts it consumes exist in `_state/`. It **invents nothing**: no rule, error,
endpoint, field, screen or cross-module flow — it only adds test cases and the indexes
derived from them.

Questions are `forbidden`; ambiguity → `factory.yaml → ambiguity` (ADR, then
`continue`; breaking → `BLOCKED`,
`stop`) — shared/GOVERNANCE-CORE.md.

Delta versions: read `_state/` as the baseline, emit only ADDED / MODIFIED / REMOVED
test cases, continue the `TC` sequence — shared/VERSIONING.md.

## 1. Inputs

| Input | Read from | Use |
|---|---|---|
| `srs` | `_state/current-srs.md` | **the derivation source**: every `REQ-*` with its `AC-*` (Given / When / Then), `RULE-*` messages, screens, permissions |
| `backend-execution-plan` (optional) | `_state/current-backend-execution-plan.md` | `API-*` (verb, path, request/response, catalog codes) to bind backend steps to endpoints; its `XM-*` blocks (target module, type HARD-FK/SOFT-READ, traces) are the **integration derivation source** on the backend track |
| `frontend-execution-plan` (optional) | `_state/current-frontend-execution-plan.md` | `SCR-*`, routes, F-blocks to bind frontend steps to screens; its `UXD-*` references (screen, foreign field, owner module) are the **integration derivation source** on the frontend track |
| `registry-srs` | `_state/current-registry-srs.md` | ID ranges, coverage of REQ by API/SCR |
| `registry-db` (optional) | `_state/current-registry-db.md` | the module's `XM-*` register (target module, type) — cross-checked against the `XM` blocks above, never restated |
| `registry-exec-fe` (optional) | `_state/current-registry-exec-fe.md` | the module's `UXD-*` register (screen, field, owner module, API used) — cross-checked against the `UXD-*` references above, never restated |

A missing optional plan → the corresponding test plan is written in **REDUCED** mode
(steps reference the AC only, no endpoint/screen binding) and says so in its header. A
missing `registry-db`/`registry-exec-fe` never blocks module-scope derivation — it only
narrows what integration-scope cross-checking can do.

## 2. Scope — a command flag, never prose

```
gov.py run-standalone test-gen --module MOD                 # this run: scope=module, mods=[MOD]
gov.py run-standalone test-gen --modules MOD-A,MOD-B,…       # this run: scope=modules, mods=[MOD-A, MOD-B, …]
gov.py run-standalone test-gen --scope project               # this run: scope=project, mods=every module with a committed version
```

This run: **scope = `project`**, modules = `FIN, MDL, SEC`.

| Scope | TC sources | Phases populated |
|---|---|---|
| `module` | `AC-*` of the one module (§3) | the module-scope phases only (`TEST-PLAN-BE` on backend; the equivalent on frontend) — **identical in shape to a single-module run today** |
| `modules` | `AC-*` per module (§3) **+** `XM-*` (§4) and `UXD-*` (§5) between the *selected* modules only | module-scope phases for every selected module, plus the integration phase(s) (`profile…phases[*].integration: true`) wherever a real linking atom pairs two selected modules |
| `project` | everything `modules` does, across **every** module the factory has ever produced a version for, **plus** a derived coverage rollup | the same as `modules`, plus `system-test-index-{profile}.md` (§9) — no new atom, no new gate |

Rules that hold at every scope:
1. a module never gets an integration TC for a module that is **not** in the current
   selection — running `--module FIN` alone never touches another module's `XM`/`UXD`;
2. an integration phase with no real linking atom among the selected modules stays **absent**
   from the output — never an empty `PHASE` block, never a guessed pairing;
3. `--module` output is produced exactly as it always was — no integration phase key, no
   `system-test-index`, no extra section — so a single-module run stays byte-identical in
   shape to before this scope model existed.

## 3. Derivation (module scope) — every `TC-*` comes from an `AC-*`

`TC-*` (`TC-FIN-{seq}`, 3-digit seq,
one continuous sequence across the module — both plans share it, so no TC id repeats) traces → AC + XM + UXD. The
module-scope derivation is **mechanical**:

| AC part | becomes |
|---|---|
| **Given** | preconditions — data state, role/permission, system state (bound to real entities/screens from the plans) |
| **When** | the step list — for backend: the endpoint call (`API-*`, verb, path, payload from the AC); for frontend: navigation + user actions on `SCR-*` |
| **Then** | expected result — status/response (per `LocalizedException → {code, messageAr, messageEn}` when a RULE fires) or UI state; message asserted in every language (ar, en) |

Rules:
1. one `TC-*` per `AC-*`, always — an AC without a TC is a coverage gap (✗), never skipped;
2. an AC whose Then names a `RULE-*` violation yields the **violation** TC; its happy-path
   twin exists only if another AC states it — do not fabricate happy paths;
3. a **boundary** TC is added only when the AC (or the RULE it cites) states a numeric limit;
4. every TC cites, besides its AC: the `REQ-*`, and the `API-*` (backend) or `SCR-*`
   (frontend) it exercises, plus the `RULE-*` / catalog code when a violation is expected;
5. never reword a rule, message or endpoint — reference by ID/code; message text is copied
   character-perfect from the SRS in every language;
6. over-engineering guard: if a track's TC count exceeds ~2× its AC count, review — the
   extra TCs are almost always fabricated variants; remove them.

Scenario tags (one per TC): `HAPPY | VIOLATION | BOUNDARY | PERMISSION | STATE | INTEGRATION`;
data class: `VALID | INVALID | BOUNDARY | EDGE | ATTACK`.
Permission ACs (no `VIEW` / no action permission) produce `PERMISSION` TCs on both tracks.

## 4. XM → TC derivation (integration scope, backend)

Runs only at `scope: modules|project`, and only for an `XM-*` whose **target module** is
also in `FIN, MDL, SEC` — an `XM-*` targeting a module outside the selection is
left alone (not this run's concern, not a gap either).

Source: the `XM-*` blocks of the **declaring** (consuming) module's `backend-execution-plan`
(cross-checked against its `registry-db`, never restated — [XM-PROTOCOL.md](../../../shared/XM-PROTOCOL.md)).
The **declaring module owns the resulting TC** — one continuous `TC-{MOD}-<seq>` sequence,
same rule as module scope (design decision: integration TC ownership follows declaration,
not the target).

| XM type | TC scenario |
|---|---|
| `HARD-FK` | one `EXISTS` TC (the referenced row is present — request/flow succeeds) **and** one `MISSING` TC (the referenced row is absent — the physical constraint is honoured: the documented rejection, never a silent pass) |
| `SOFT-READ` | one `GRACEFUL-DEGRADATION` TC — the target read fails or returns empty and the declaring module's flow still returns a defined result (never a 500 / unhandled state) |

Rules:
1. never invent the target entity's shape — bind by `ENT`/`DBF` ID only, as the `XM` block
   already does; the TC exercises the declaring module's own `API-*`, not the target's;
2. tag every such TC `INTEGRATION`, data class per the row above;
3. `traces=` carries the `XM-*` id plus the `REQ-*` the XM itself traces to (and the `API-*`
   exercised, when the plan binds one) — never an `AC-*` that does not exist for it;
4. one `XM-*` never yields more than the two/one TC(s) in the table above — no fabricated
   extra scenarios ("over-engineering guard" of §3 applies here too).

## 5. UXD → TC derivation (integration scope, frontend)

Runs only at `scope: modules|project`, and only for a `UXD-*` whose **owner module** (the
module that owns the displayed data) is also in `FIN, MDL, SEC`.

Source: the `UXD-*` references of the **displaying** module's `frontend-execution-plan`
F4 blocks (cross-checked against its `registry-exec-fe`, never restated). The **displaying
module owns the resulting TC** (it is the one whose screen renders the foreign field).

| UXD case | TC scenario |
|---|---|
| foreign field rendered | one TC: navigate to the `SCR-*`, the foreign-owned field renders the value the owner module's API returns |
| foreign field empty / owner API failure | one TC: the screen shows its declared empty/error state (§A.3 `States` of the ui-ux-spec) — never a blank crash, never invented copy |

Rules:
1. never invent the owner module's field shape or a new permission — the UXD block and the
   owner's real `API-*` (from api-docs, when present in state) are the only sources;
2. tag every such TC `INTEGRATION`; `traces=` carries the `UXD-*` id plus its `REQ-*`/`AC-*`
   and the `SCR-*` it renders on;
3. one `UXD-*` never yields more than the two TCs in the table above.

## 6. TC block — framework-agnostic form

```
<!-- TC:TC-FIN-<seq>:START traces=AC-FIN-<seq>,REQ-FIN-<seq>[,API-FIN-<seq>|SCR-FIN-<seq>|XM-FIN-<seq>|UXD-FIN-<seq>] -->
### TC-FIN-<seq> — <title>
Derived from : AC-FIN-<seq>  (REQ-FIN-<seq>)   |   XM-FIN-<seq> (REQ-FIN-<seq>)   |   UXD-FIN-<seq> (REQ-FIN-<seq>, AC-FIN-<seq>)
Exercises    : API-FIN-<seq> <verb path>   |   SCR-FIN-<seq> <route>
Rule / code  : RULE-FIN-<seq> → <catalog code> | —
Scenario     : <tag> · data class <class> · language <ar|en|ALL>
Preconditions: <from Given — concrete entities, role, state | for XM/UXD: the target/owner entity present or absent>
Steps        : 1. … 2. … (from When — one observable action per step)
Expected     : <from Then — status / body shape / message per language / UI state>
Test data    : <values named in the AC; placeholders marked, never invented business data>
<!-- TC:TC-FIN-<seq>:END -->
```
Framework: `profile.stack.testing` is **agnostic** on both tracks — the block above is the whole
contract; the consumer repo chooses its tool and turns each TC into a test. No framework
name, annotation or file layout is mentioned anywhere in the plan.

## 7. Test plans — organised by the profile's test phases

Each track with a `test` plan in the profile gets one file per module, wrapped in the
profile's test phases with `TC` atoms (kind `TC`, level 3, parents PHASE/SUB,
plans test). Test-plan SUB ids are **bare** labels
(`factory.markers.rules.sub_unqualified_exempt_plans` = test).
A phase flagged `integration: true` in the profile is populated **only** at `scope:
modules|project`, per §2/§4/§5 — at `scope: module` it is skipped entirely, so single-module
output carries the module-scope phases only, exactly as before this scope model existed.

### Track `backend` — one file per selected module: `backend-test-plan-fin.md`

| Phase key | Split rule | SUB labels |
|---|---|---|
| `TEST-PLAN-BE` | SUB when TC count > 12 — grouped RULE-SCENARIOS / API-SCENARIOS | `RULE-SCENARIOS`, `API-SCENARIOS` |
| `INT-XM` _(integration — `scope: modules|project` only)_ | SUB when TC count > 8 — grouped per target module | — |
Layout (per selected module):
```
<header>   sources (_state files + versions) · scope `project` · framework note (§3) · REDUCED? · open ADRs
<!-- PHASE:TEST-PLAN-BE:START traces=<union of the TCs' REQ/AC> -->
  <!-- SUB:RULE-SCENARIOS:START traces=… -->  …TC blocks…  <!-- SUB:RULE-SCENARIOS:END -->
  <!-- SUB:API-SCENARIOS:START traces=… -->  …TC blocks…  <!-- SUB:API-SCENARIOS:END -->
  (SUBs only when the threshold is met — decide WHILE writing, from the TC count)
<!-- PHASE:TEST-PLAN-BE:END -->
<!-- PHASE:INT-XM:START traces=<union of the TCs' REQ/AC/XM/UXD> -->
  (populate ONLY when a real linking atom pairs this module with another module in FIN, MDL, SEC — §4/§5; omit this PHASE entirely when none exists, never an empty block)
  …TC blocks…
<!-- PHASE:INT-XM:END -->
TC TRACEABILITY INDEX   AC → TC · REQ → TC · API → TC · RULE/code → TC · XM → TC
COVERAGE                AC covered <n>/<total> (a gap is ✗ and blocks the run) · REQ covered · API covered · every selected-module XM covered <n>/<total> (an integration gap is ✗ exactly like an AC gap — recorded, never silently dropped)
```
Backend grouping hint: rule-driven ACs (violations, state transitions) vs endpoint-driven ACs
(happy paths, permission, paging/empty-result per `Page<T>`); integration TCs (§4) group by target module inside `INT-XM`.

### Track `frontend` — one file per selected module: `frontend-test-plan-fin.md`

| Phase key | Split rule | SUB labels |
|---|---|---|
| `TEST-PLAN-FE` | SUB when TC count > 8 — grouped UI-FLOWS / INT-FLOW | `UI-FLOWS`, `INT-FLOW` |
| `INT-UXD` _(integration — `scope: modules|project` only)_ | SUB when TC count > 8 — grouped per source module | — |
Layout (per selected module):
```
<header>   sources (_state files + versions) · scope `project` · framework note (§3) · REDUCED? · open ADRs
<!-- PHASE:TEST-PLAN-FE:START traces=<union of the TCs' REQ/AC> -->
  <!-- SUB:UI-FLOWS:START traces=… -->  …TC blocks…  <!-- SUB:UI-FLOWS:END -->
  <!-- SUB:INT-FLOW:START traces=… -->  …TC blocks…  <!-- SUB:INT-FLOW:END -->
  (SUBs only when the threshold is met — decide WHILE writing, from the TC count)
<!-- PHASE:TEST-PLAN-FE:END -->
<!-- PHASE:INT-UXD:START traces=<union of the TCs' REQ/AC/XM/UXD> -->
  (populate ONLY when a real linking atom pairs this module with another module in FIN, MDL, SEC — §4/§5; omit this PHASE entirely when none exists, never an empty block)
  …TC blocks…
<!-- PHASE:INT-UXD:END -->
TC TRACEABILITY INDEX   AC → TC · REQ → TC · SCR → TC · RULE/code → TC · UXD → TC
COVERAGE                AC covered <n>/<total> (a gap is ✗ and blocks the run) · REQ covered · SCR covered · every selected-module UXD covered <n>/<total> (an integration gap is ✗ exactly like an AC gap — recorded, never silently dropped)
```
Frontend grouping hint: per-screen flows (search, create/edit, violation shown on screen,
permission-hidden affordance) vs the single module lifecycle flow (create → search → update →
deactivate → gone from active results); the composite-screen invariant (entry never rendered open by default) is one TC when an AC states it; integration TCs (§5) group by source (owner) module inside `INT-UXD`.

## 8. Test-execution manifest (ON — `profile.stack.testing.manifest`)

Emitted in the same run, after the backend test plan, as
`test-execution-manifest-fin.md` —
a **derived view** for the `api-verify` standalone (it introduces no ID), one per module:
```
DEPENDENCY ORDER      topological entity build order (from FK/XM relations in the backend plan and "must belong to" RULEs)
RULE → CODE → TC      RULE-* │ catalog code (runtime format per LocalizedException → {code, messageAr, messageEn}) │ TC-* │ HTTP │ API-*   (informational-only RULEs excluded)
ENTITY CRUD CHECKLIST ENT-* │ create │ read │ search │ update │ deactivate (soft) │ activate (each ✓ / —, from the API-* set)
```
Regenerate whenever the backend plan or test plan changes — a stale manifest is a defect.

## 9. System test index (`scope: project` only)

Emitted once per run, after every selected module's test plans, as
`system-test-index-erp.md` — a platform-level **derived view**
(introduces no ID, never a gate, `paths.platform` — same tier as `project-registry.md`):
```
SYSTEM TEST INDEX — ERP Platform — generated {scope: project}
AC → TC       per module: AC covered <n>/<total>, list of uncovered AC (✗)
XM → TC       every XM-* between two modules that both have a committed version: covered ✓/✗ (✗ = gap, never silently dropped)
UXD → TC      every UXD-* whose owner module also has a committed version: covered ✓/✗
COVERAGE %    per module: AC%, and — where the module both declares and is targeted by XM/UXD — integration%
CROSS-MODULE  matrix of module → module, one row per XM/UXD pair, TC id(s) covering it (— if none: gap ✗)
```
Never restates TC content — every row is an ID reference. A module the platform has never
produced a version for is out of scope (not a gap): the index only rolls up modules that
exist.

## 10. Split

The same toolkit splits test plans, with plan key `test`
(`factory.tracks.<track>.packages.test` → `backend-test`, `frontend-test`), **per module**:
```
gov.py split --track <track> --module <MOD> --version <v> --plan test --dry-run   # validate, non-zero exit = fix first
gov.py split --track <track> --module <MOD> --version <v> --plan test
```
Every TC atom is verified by content hash (`factory.markers.rules.verify` = sha256) after the split.
`system-test-index-erp.md` is a platform-level file — it is never split, never packaged, never delivered to a consumer repo.

## 11. Self-check before finishing

```
[ ] every AC-* in the SRS (of every selected module) has ≥1 TC-* (coverage ✗ = not done)
[ ] every TC-* carries traces= with its AC-*/XM-*/UXD-* source (+ REQ, API/SCR) and the atom marker pair
[ ] no TC without an AC/XM/UXD source; no reworded rule/message/endpoint; test data never invented
[ ] phases = the profile's test phases, in order; SUB labels bare; thresholds checked while writing
[ ] framework wording matches §6; manifest emitted iff profile.stack.testing.manifest (per module)
[ ] at scope module: no integration phase, no system-test-index — output unchanged from before
[ ] at scope modules|project: every XM-*/UXD-* between two SELECTED modules has ≥1 TC or is
    recorded as a gap (✗) — never silently dropped, never fabricated when absent
[ ] at scope project: system-test-index-erp.md rolls up every module with
    a committed version; every AC/XM/UXD gap listed is ✗, exactly like a module-scope AC gap
[ ] ADRs written for every derivation choice that was not mechanical
```

## 12. Boundaries

| Owns | References (never redefines) | Never |
|---|---|---|
| `TC-*`, the test plans, the manifest, the system test index | `REQ/AC/RULE` (P1), `API` (P3.1), `SCR/UXD` (P3.2 — `UXD` is `P3.2`'s, cited never redefined), `DBF/XM` (P2 — `XM` is `P2`'s, cited never redefined), catalog codes | test code, framework scaffolding, any edit to a line artifact, any gate or verdict, a cross-module TC for a module outside the current selection |


---
# INPUTS — module FIN (generated current state)

<<<INPUT: srs (FIN)>>>
# SRS — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-10)
Counts : ENT 14 · REQ 46 · AC 46 · RULE 16 · SCR-REQ 12 · ADR 0
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |
|---|---|
| Module | FIN — الحسابات العامة / Finance (General Ledger) |
| Feature code | FIN |
| Version | v1 |
| Date | 2026-09-10 |
| Status | DRAFT (P1) |
| Prepared by | governance-factory (analysis lane) |
| Decisions applied count | 0 |

## A2 — Functional context

**In scope:** شجرة حسابات هرمية بأبعاد كبيانات، محرك قواعد يبني القيد من الحدث المحاسبي
القياسي، مصادر يومية أربعة (حدث/يدوي/متكرر-عكسي/توزيع) بدورة حياة موحدة (بناء → تحقق آلي →
ترحيل مباشر، لا اعتماد لكل قيد)، تصحيح بالعكس فقط، دورة حياة فترة محاسبية داخلية بالكامل
مع بوابة اعتماد واحدة عند الإغلاق، تقارير مالية مُشتقة حيًا مع تتبع نازل، تسجيل FIN في SEC
وMDL كبيانات.

**Out of scope:** تعدد العملات، تعدد الدفاتر/الكيانات والقيود البينية، الحسابات الإحصائية،
التقويم متعدد الأنماط، المرفقات — استبعاد صريح [business-policies-fin.md → SCOPE
EXCEPTIONS]؛ الوحدة التجارية، مستهلك الأحداث، طبقة النقل — خارج النطاق تمامًا
[general-accounting-system-plan-en.md §15].

**Module function (one paragraph):** FIN دفتر أستاذ عام قابل للتوصيل بأي نظام مضيف: يستقبل
حدثًا محاسبيًا قياسيًا فقط (لا قراءة ولا كتابة مباشرة لجداول المضيف)، يبني منه قيدًا متوازنًا
عبر قاعدة مُعرَّفة كبيانات، يرحّله مباشرة بعد تحقق آلي، ويشتق كل رصيد وتقرير من القيود
المُرحَّلة فقط — لا عمود رصيد مُخزَّن في أي مكان.

**Detailed description (workflow narrative, roles):** حدث محاسبي يصل → المحرك يحدد قاعدته
عبر نوع الحدث → يبني سطور القيد (اشتقاق حساب + مصدر مبلغ + اتجاه لكل سطر، مع سطر باقٍ ضامن
عند التوزيع النسبي) → تحقق آلي (توازن، أوراق نشطة قابلة للترحيل، أبعاد صالحة، فترة مفتوحة)
→ ترحيل مباشر. محاسب يُدخل قيودًا يدوية بنفس المسار. مراقب مالي (منفصل عن منشئ القيود) يعتمد
إغلاق الفترة فقط — نقطة التحكم البشري الوحيدة. كل التقارير تُشتق حيًا من القيود المُرحَّلة.

**Current situation:** لا نظام محاسبي سابق ضمن هذه الدفعة؛ FIN أول وحدة أعمال حقيقية تُبنى،
تستهلك SEC وMDL المكتملتين بالفعل.

**Current difficulties:** الأنظمة القديمة المشابهة (المصدر الملهم لهذا التصميم) تعتمد على
أعمدة رصيد مُخزَّنة تفقد تزامنها — بالضبط ما يحله POL-FIN-009.

**Proposed system and benefits:** محرك قواعد بيانات-محور يفصل منطق الحساب عن مصدر المبلغ،
دورة حياة قيد موحدة بلا اعتماد فردي يُسرّع التشغيل مع نقل الرقابة لمستوى الفترة، وأرصدة
مُشتقة دائمًا تضمن التطابق التام مع القيود الفعلية.

**General notes (constraints, deferred items):** لا محرك سير عمل؛ لا رقم حساب داخل حمولة
الحدث؛ الالتزام بحدود idempotency عند الحد الخارجي مفترض لا مُعاد تنفيذه [§12.12].

## A3 — Entities and fields

Standard fields per kind (profile.conventions.entity_defaults): master → nameAr, nameEn,
code, isActiveFl, createdBy, createdAt, updatedBy, updatedAt; transactional → docNo,
docDate, statusCode, fiscalYearId, periodId, createdBy, createdAt, updatedBy, updatedAt;
lookup → code, nameAr, nameEn, sortOrder, isActiveFl; config → key, valueAr, valueEn,
isActiveFl (adapted per entity below where the plan's own vocabulary differs, e.g. `code`
in place of a generic `key`, cited per field).

### ENT-FIN-001 — الحساب / Account
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | No — `code` is a client-defined chart-of-accounts code, not a platform-numbered sequence [§3.3 test] | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| accountPk | number | yes (system) | — | primary key | معرّف الحساب | Account id |
| code | text | yes | unique | chart-of-accounts code | رمز الحساب | Account code |
| nameAr | text | yes | — | — | اسم الحساب (عربي) | Account name (Arabic) |
| nameEn | text | yes | — | — | اسم الحساب (إنجليزي) | Account name (English) |
| accountTypeCode | lookup | yes | lookup key `ACCOUNT_TYPE` (A6) | asset/liability/equity/revenue/expense | نوع الحساب | Account type |
| natureCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | normal balance side [POL-FIN-002] | الطبيعة | Nature |
| parentAccountId | reference | no | ENT-FIN-001 (self) | null = root | الحساب الأب | Parent account |
| isLeafFl | flag | yes | — | accepts direct posting only when true [RULE-FIN-001, POL-FIN-003] | ورقة (يقبل ترحيلاً مباشرًا) | Leaf (accepts direct posting) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-002 — البُعد / Dimension
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, deactivate | none | general-accounting-system-plan-en.md §4.2 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| dimensionPk | number | yes (system) | — | primary key | معرّف البُعد | Dimension id |
| code | text | yes | unique | e.g. `PROJECT`, `INVESTOR` | رمز البُعد | Dimension code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-003 — قيمة البُعد / DimensionValue
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| lookup | PRIVATE | No | create, read, search, deactivate | none | general-accounting-system-plan-en.md §4.2 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| dimensionValuePk | number | yes (system) | — | primary key | معرّف قيمة البُعد | Dimension value id |
| dimensionId | reference | yes | ENT-FIN-002 | — | البُعد | Dimension |
| code | text | yes | unique within dimensionId [RULE-FIN-002] | — | الرمز | Code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| sortOrder | number | yes | — | — | ترتيب العرض | Sort order |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-004 — رأس قيد اليومية / JournalEntry
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | **Yes** — `docNo` is exactly the numbered transactional document case [§3.3 test (c)]: system-generated on first save, read-only after, unique per fiscal year, from the platform numbering engine | create (4 sources), read, search, reverse | none | general-accounting-system-plan-en.md §7, §8, §9 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalEntryPk | number | yes (system) | — | primary key | معرّف القيد | Journal entry id |
| docNo | text | yes (system) | platform numbering engine; unique per fiscalYearId | read-only after create | رقم المستند | Document number |
| docDate | date | yes | — | — | تاريخ المستند | Document date |
| fiscalYearId | reference | yes | ENT-FIN-007 | — | السنة المالية | Fiscal year |
| periodId | reference | yes | ENT-FIN-008; must be Open at post [RULE-FIN-008] | — | الفترة | Period |
| journalTypeCode | lookup | yes | lookup key `JOURNAL_TYPE` (A6) | classifies the source | نوع اليومية | Journal type |
| statusCode | lookup | yes | lookup key `JOURNAL_STATUS` (A6) | drives A7 lifecycle | الحالة | Status |
| eventReference | text | no | unique when not null [RULE-FIN-004] | idempotency key for event-sourced entries [POL-FIN-012] | مرجع الحدث | Event reference |
| originalEntryId | reference | no | ENT-FIN-004 (self) | set on a reversal entry [POL-FIN-007] | القيد الأصلي | Original entry |
| reversalEntryId | reference | no | ENT-FIN-004 (self) | set on the original once reversed (bidirectional link) | قيد العكس | Reversal entry |
| descriptionAr | text | no | — | — | الوصف (عربي) | Description (Arabic) |
| descriptionEn | text | no | — | — | الوصف (إنجليزي) | Description (English) |
| postedAt | date-time | no (system) | set at post time | — | تاريخ الترحيل | Posted at |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields; immutable after posting [POL-FIN-013] | — | — |

### ENT-FIN-005 — سطر قيد اليومية / JournalLine
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | No | create (with header), read | none | general-accounting-system-plan-en.md §6, §8 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalLinePk | number | yes (system) | — | primary key | معرّف السطر | Line id |
| journalEntryId | reference | yes | ENT-FIN-004 | — | القيد | Journal entry |
| lineNo | number | yes | — | display/build order | رقم السطر | Line number |
| accountId | reference | yes | ENT-FIN-001; must be leaf+active [RULE-FIN-007] | — | الحساب | Account |
| amount | decimal | yes | always positive [RULE-FIN-006, POL-FIN-005] | `NUMERIC(18,4)` per [KB:erp-domain-standards §6] | المبلغ | Amount |
| directionCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | carries the sign, never the amount [POL-FIN-005] | الاتجاه | Direction |
| isRemainderFl | flag | yes | default false | marks the POL-FIN-006 guarantor line, at most one true per compound distribution [RULE-FIN-010] | سطر الباقي | Remainder line |
| descriptionAr | text | no | — | — | الوصف (عربي) | Description (Arabic) |
| descriptionEn | text | no | — | — | الوصف (إنجليزي) | Description (English) |
| createdAt | system | yes | — | lines are written atomically with the header, never edited independently | — | — |

### ENT-FIN-006 — بُعد سطر القيد / JournalLineDimension
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| transactional | PRIVATE | No | create (with line), read | none | general-accounting-system-plan-en.md §4.3, §12.11 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalLineDimensionPk | number | yes (system) | — | primary key | معرّف بُعد السطر | Line dimension id |
| journalLineId | reference | yes | ENT-FIN-005 | — | سطر القيد | Journal line |
| dimensionId | reference | yes | ENT-FIN-002 | — | البُعد | Dimension |
| dimensionValueId | reference | yes | ENT-FIN-003; must belong to dimensionId and be active [RULE-FIN-009] | — | قيمة البُعد | Dimension value |

### ENT-FIN-007 — السنة المالية / FiscalYear
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | No | create, read, search | none | general-accounting-system-plan-en.md §10 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| fiscalYearPk | number | yes (system) | — | primary key | معرّف السنة المالية | Fiscal year id |
| code | text | yes | unique, e.g. `2026` | — | رمز السنة | Year code |
| startDate | date | yes | — | — | تاريخ البداية | Start date |
| endDate | date | yes | — | — | تاريخ النهاية | End date |
| statusCode | lookup | yes | lookup key `FISCAL_YEAR_STATUS` (A6) | — | الحالة | Status |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-008 — الفترة المحاسبية / FiscalPeriod
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | PRIVATE | No | create, read, search, open, soft-close, hard-close | none | general-accounting-system-plan-en.md §10 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| fiscalPeriodPk | number | yes (system) | — | primary key | معرّف الفترة | Period id |
| fiscalYearId | reference | yes | ENT-FIN-007 | — | السنة المالية | Fiscal year |
| periodNo | number | yes | — | 1..N within the year | رقم الفترة | Period number |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| startDate | date | yes | — | — | تاريخ البداية | Start date |
| endDate | date | yes | — | — | تاريخ النهاية | End date |
| statusCode | lookup | yes | lookup key `PERIOD_STATE` (A6) | drives A7 lifecycle | الحالة | Status |
| closedBy | text | no | — | set at hard-close, by the approver [POL-FIN-016] | أُغلقت بواسطة | Closed by |
| closedAt | date-time | no | — | — | تاريخ الإغلاق | Closed at |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-009 — قاعدة نوع الحدث / EventTypeRule
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §6 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| eventTypeRuleId | number | yes (system) | — | primary key | معرّف قاعدة الحدث | Event type rule id |
| eventTypeCode | lookup | yes | lookup key `ACCOUNTING_EVENT_TYPE` (A6); unique | one rule per event type [§6.4] | نوع الحدث | Event type |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-010 — سطر القاعدة / RuleLine
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create (with rule), read, update, delete | none | general-accounting-system-plan-en.md §6.2, §6.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| ruleLineId | number | yes (system) | — | primary key | معرّف سطر القاعدة | Rule line id |
| eventTypeRuleId | reference | yes | ENT-FIN-009 | — | قاعدة الحدث | Event type rule |
| lineNo | number | yes | — | — | رقم السطر | Line number |
| accountDerivationTypeCode | lookup | yes | lookup key `ACCOUNT_DERIVATION_TYPE` (A6) | constant / direct / mapping [§6.2(a)] | نوع اشتقاق الحساب | Account derivation type |
| accountDerivationValue | text | yes | interpreted per accountDerivationTypeCode | constant account code, event field name, or mapping-set key | قيمة الاشتقاق | Derivation value |
| amountSourceTypeCode | lookup | yes | lookup key `AMOUNT_SOURCE_TYPE` (A6) | field / percentage / remainder [§6.2(b)] | نوع مصدر المبلغ | Amount source type |
| amountSourceValue | text | no | event field name or percentage figure | required unless amountSourceTypeCode=REMAINDER | قيمة مصدر المبلغ | Amount source value |
| directionCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | — | الاتجاه | Direction |
| distributionTypeCode | lookup | yes | lookup key `DISTRIBUTION_TYPE` (A6) | fixed / percentage / remainder [§6.3] | نوع التوزيع | Distribution type |
| isRemainderFl | flag | yes | default false | exactly one true per rule when any line is PERCENTAGE [RULE-FIN-003] | سطر الباقي | Remainder line |
| createdAt | system | yes | — | — | — | — |

### ENT-FIN-011 — قالب متكرر/عكسي / RecurringTemplate
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §7.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| recurringTemplateId | number | yes (system) | — | primary key | معرّف القالب | Template id |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| scheduleTypeCode | lookup | yes | lookup key `RECURRING_SCHEDULE_TYPE` (A6) | recurring / reversing | نوع الجدولة | Schedule type |
| frequencyCode | lookup | yes (when scheduleTypeCode=RECURRING) | lookup key `RECURRING_FREQUENCY` (A6) | not applicable to a pure reversing template | التكرار | Frequency |
| startDate | date | yes | — | — | تاريخ البدء | Start date |
| nextRunDate | date | yes (system-maintained) | — | advances after each run | تاريخ التشغيل القادم | Next run date |
| endDate | date | no | — | — | تاريخ الانتهاء | End date |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-012 — سطر القالب المتكرر / RecurringTemplateLine
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create (with template), read, update, delete | none | general-accounting-system-plan-en.md §7.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| recurringTemplateLineId | number | yes (system) | — | primary key | معرّف سطر القالب | Template line id |
| recurringTemplateId | reference | yes | ENT-FIN-011 | — | القالب | Template |
| lineNo | number | yes | — | — | رقم السطر | Line number |
| accountId | reference | yes | ENT-FIN-001; must be leaf+active at run time [RULE-FIN-007, reused] | — | الحساب | Account |
| amount | decimal | yes | positive [RULE-FIN-006, reused] | — | المبلغ | Amount |
| directionCode | lookup | yes | lookup key `DEBIT_CREDIT` (A6) | — | الاتجاه | Direction |
| dimensionValueId | reference | no | ENT-FIN-003 | single optional dimension per line — a simplification vs the header's multi-dimension model (§9.3.3, AUTO-DECISION) | قيمة البُعد | Dimension value |
| createdAt | system | yes | — | — | — | — |

### ENT-FIN-013 — قاعدة توزيع / AllocationRule
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create, read, search, update, deactivate | none | general-accounting-system-plan-en.md §7.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| allocationRuleId | number | yes (system) | — | primary key | معرّف قاعدة التوزيع | Allocation rule id |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| sourceAccountId | reference | yes | ENT-FIN-001 | the balance being distributed | الحساب المصدر | Source account |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-FIN-014 — هدف التوزيع / AllocationTarget
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| config | PRIVATE | No | create (with rule), read, update, delete | none | general-accounting-system-plan-en.md §7.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| allocationTargetId | number | yes (system) | — | primary key | معرّف هدف التوزيع | Allocation target id |
| allocationRuleId | reference | yes | ENT-FIN-013 | — | قاعدة التوزيع | Allocation rule |
| lineNo | number | yes | — | — | رقم السطر | Line number |
| targetAccountId | reference | yes | ENT-FIN-001 | — | الحساب الهدف | Target account |
| dimensionValueId | reference | no | ENT-FIN-003 | single optional dimension (same simplification as ENT-FIN-012) | قيمة البُعد | Dimension value |
| distributionTypeCode | lookup | yes | lookup key `DISTRIBUTION_TYPE` (A6) | fixed / percentage / remainder [§6.3, reused for allocations §7.4] | نوع التوزيع | Distribution type |
| distributionValue | decimal | no | required unless distributionTypeCode=REMAINDER | — | قيمة التوزيع | Distribution value |
| isRemainderFl | flag | yes | default false | exactly one true per rule when any target is PERCENTAGE [RULE-FIN-003, reused] | هدف الباقي | Remainder target |

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-FIN-001 — إنشاء حساب / Create an account
Pattern    : event
Statement  : When a finance administrator creates an account, the system shall record its code, bilingual name, type and nature within the chart hierarchy.
Traces     : US-FIN-001
Entities   : ENT-FIN-001
Rationale  : the reference structure that determines where values are recorded
Source     : general-accounting-system-plan-en.md §4.1-§4.2
Priority   : HIGH
#### AC-FIN-001 — [REQ-FIN-001]
Given a unique code, bilingual name, account type and nature, optionally a parent account
When a finance administrator submits the account form
Then the system creates the account

### REQ-FIN-002 — رفض ترحيل مباشر لحساب له أبناء / Reject direct-posting on an account with children
Pattern    : unwanted
Statement  : If an account has any child account, then the system shall prevent it from being marked as accepting direct posting.
Traces     : US-FIN-001
Entities   : ENT-FIN-001
Rationale  : RULE-FIN-001; POL-FIN-003 — only leaves accept postings
Source     : general-accounting-system-plan-en.md §4.2
Priority   : HIGH
#### AC-FIN-002 — [REQ-FIN-002]
Given an account with at least one child account
When an administrator attempts to mark it as accepting direct posting (isLeafFl=true)
Then the system rejects the change

### REQ-FIN-003 — تعطيل حساب / Deactivate an account
Pattern    : event
Statement  : When a finance administrator deactivates an account, the system shall block any future posting to it.
Traces     : US-FIN-001
Entities   : ENT-FIN-001
Rationale  : POL-FIN-003
Source     : general-accounting-system-plan-en.md §4.2
Priority   : MEDIUM
#### AC-FIN-003 — [REQ-FIN-003]
Given an active account
When an administrator deactivates it
Then the system sets isActiveFl=false and REQ-FIN-019 subsequently rejects any posting to it

### REQ-FIN-004 — إنشاء بُعد / Create a dimension
Pattern    : event
Statement  : When a finance administrator creates a dimension, the system shall record it as an active dimension available for account combinations.
Traces     : US-FIN-002
Entities   : ENT-FIN-002
Rationale  : dimensions defined as data, a governing design constraint
Source     : general-accounting-system-plan-en.md §4.2-§4.3
Priority   : HIGH
#### AC-FIN-004 — [REQ-FIN-004]
Given a unique code and bilingual name
When an administrator submits the dimension form
Then the system creates an active Dimension

### REQ-FIN-005 — إنشاء قيمة بُعد / Create a dimension value
Pattern    : event
Statement  : When a finance administrator creates a value under a dimension, the system shall record its code, bilingual name and sort order.
Traces     : US-FIN-002
Entities   : ENT-FIN-003
Rationale  : §4.2
Source     : general-accounting-system-plan-en.md §4.2
Priority   : HIGH
#### AC-FIN-005 — [REQ-FIN-005]
Given a selected dimension and a code not yet used under it
When an administrator submits the value form
Then the system creates the DimensionValue

### REQ-FIN-006 — رفض رمز مكرر ضمن البُعد / Reject a duplicate code within a dimension
Pattern    : unwanted
Statement  : If two dimension values under the same dimension share the same code, then the system shall reject the second.
Traces     : US-FIN-002
Entities   : ENT-FIN-003
Rationale  : RULE-FIN-002
Source     : general-accounting-system-plan-en.md §4.2
Priority   : MEDIUM
#### AC-FIN-006 — [REQ-FIN-006]
Given a dimension already holding a value with code "NORTH"
When a second value with code "NORTH" is created under the same dimension
Then the system rejects it

### REQ-FIN-007 — إنشاء قاعدة نوع حدث / Create an event-type rule
Pattern    : event
Statement  : When a finance administrator creates a rule for an event type, the system shall record it as the single active rule for that type.
Traces     : US-FIN-003
Entities   : ENT-FIN-009
Rationale  : §6.4 — one rule per event type
Source     : general-accounting-system-plan-en.md §6.1, §6.4
Priority   : HIGH
#### AC-FIN-007 — [REQ-FIN-007]
Given an event type registered in MDL with no existing rule
When an administrator creates a rule for it
Then the system creates an active EventTypeRule

### REQ-FIN-008 — إضافة سطر قاعدة / Add a rule line
Pattern    : event
Statement  : When a finance administrator adds a line to an event-type rule, the system shall record its account derivation, amount source and direction as three separate references.
Traces     : US-FIN-003
Entities   : ENT-FIN-010
Rationale  : POL-FIN-014; §6.2 separation of (a) and (b) is deliberate
Source     : general-accounting-system-plan-en.md §6.2
Priority   : HIGH
#### AC-FIN-008 — [REQ-FIN-008]
Given an event-type rule
When an administrator adds a line with an account-derivation spec, an amount-source spec and a direction
Then the system creates the RuleLine

### REQ-FIN-009 — رفض عدد غير صحيح من سطور الباقي / Reject an incorrect remainder-line count
Pattern    : unwanted
Statement  : If an event-type rule's lines include any percentage-distribution line, then the system shall require exactly one line marked as the remainder.
Traces     : US-FIN-003
Entities   : ENT-FIN-010
Rationale  : RULE-FIN-003; POL-FIN-006
Source     : general-accounting-system-plan-en.md §6.3, §12.6
Priority   : HIGH
#### AC-FIN-009 — [REQ-FIN-009]
Given a rule with two PERCENTAGE-distribution lines and zero lines marked remainder
When an administrator attempts to save the rule
Then the system rejects it until exactly one line is marked remainder

### REQ-FIN-010 — بناء قيد من حدث / Build an entry from an event
Pattern    : event
Statement  : When a canonical accounting event arrives, the system shall build a journal entry from it using its event type's active rule.
Traces     : US-FIN-004
Entities   : ENT-FIN-004, ENT-FIN-005, ENT-FIN-009, ENT-FIN-010
Rationale  : POL-FIN-014, POL-FIN-020 — no host-specific logic, only rule + event data
Source     : general-accounting-system-plan-en.md §7.1
Priority   : HIGH
#### AC-FIN-010 — [REQ-FIN-010]
Given a canonical event with a type that has an active rule
When the event arrives
Then the system builds a DRAFT journal entry whose lines follow the rule, then proceeds to REQ-FIN-017 (validate + post)

### REQ-FIN-011 — رفض مرجع حدث مكرر / Reject a duplicate event reference
Pattern    : unwanted
Statement  : If a canonical event's reference has already produced a posted entry, then the system shall reject a second entry for the same reference.
Traces     : US-FIN-004
Entities   : ENT-FIN-004
Rationale  : RULE-FIN-004; POL-FIN-012 — boundary idempotency is assumed, a repeat is a defect
Source     : general-accounting-system-plan-en.md §12.12
Priority   : HIGH
#### AC-FIN-011 — [REQ-FIN-011]
Given a POSTED entry with eventReference "EVT-1001"
When another event with reference "EVT-1001" arrives
Then the system rejects building a second entry for it

### REQ-FIN-012 — امتصاص فرق التقريب عبر سطر الباقي / Absorb the rounding difference via the remainder line
Pattern    : event
Statement  : When a rule's lines produce a compound or percentage distribution, the system shall compute the remainder line's amount as the original amount minus the sum of every other line, after each percentage line is rounded to the smallest currency unit.
Traces     : US-FIN-004
Entities   : ENT-FIN-005, ENT-FIN-010
Rationale  : RULE-FIN-010; POL-FIN-006
Source     : general-accounting-system-plan-en.md §6.3
Priority   : HIGH
#### AC-FIN-012 — [REQ-FIN-012]
Given a rule distributing 100.00 as 33% + 33% + remainder
When the entry is built
Then the two percentage lines total 66.00 (each rounded to the smallest currency unit) and the remainder line is exactly 34.00, so the entry balances exactly

### REQ-FIN-013 — رفض حدث بلا قاعدة نشطة / Reject an event with no active rule
Pattern    : unwanted
Statement  : If an event's type has no active event-type rule, then the system shall reject building an entry for it.
Traces     : US-FIN-004
Entities   : ENT-FIN-009
Rationale  : the engine applies rules, it never guesses
Source     : general-accounting-system-plan-en.md §6.1
Priority   : MEDIUM
#### AC-FIN-013 — [REQ-FIN-013]
Given an event type with no active EventTypeRule
When an event of that type arrives
Then the system rejects building an entry and records the failure for operator follow-up

### REQ-FIN-014 — إدخال يدوي / Create a manual journal entry
Pattern    : event
Statement  : When an accountant creates a manual journal entry with its lines, the system shall build it exactly as any other source, then proceed through the same validation and posting path.
Traces     : US-FIN-005
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : POL-FIN-001, POL-FIN-018 — one unified rule for every source
Source     : general-accounting-system-plan-en.md §7.2
Priority   : HIGH
#### AC-FIN-014 — [REQ-FIN-014]
Given a fiscal period, at least two balanced lines with leaf active accounts
When an accountant submits the manual entry form
Then the system builds a DRAFT entry and proceeds to REQ-FIN-017

### REQ-FIN-015 — عرض تفاصيل الفشل قبل الترحيل / Show validation failures before posting
Pattern    : event
Statement  : When a manual entry fails automatic validation, the system shall return every failing check to the accountant without posting anything.
Traces     : US-FIN-005
Entities   : ENT-FIN-004
Rationale  : usable error feedback for the one path with a live human editor
Source     : general-accounting-system-plan-en.md §8.1
Priority   : MEDIUM
#### AC-FIN-015 — [REQ-FIN-015]
Given a manual entry with two failing validations
When the accountant submits it
Then the system returns both failures and posts nothing

### REQ-FIN-016 — إبقاء السجل دون حذف فعلي / Retain records without hard deletion
Pattern    : ubiquitous
Statement  : The system shall retain every posted journal entry's record permanently, never hard-deleting it.
Traces     : US-FIN-008
Entities   : ENT-FIN-004
Rationale  : POL-FIN-013
Source     : general-accounting-system-plan-en.md §12.13
Priority   : HIGH
#### AC-FIN-016 — [REQ-FIN-016]
Given a POSTED journal entry
When any attempt is made to delete it
Then the system rejects the delete — the only path that changes its effect is a reversal (REQ-FIN-028)

### REQ-FIN-017 — تحقق آلي وترحيل مباشر موحّد / Unified automatic validation and direct posting
Pattern    : event
Statement  : When any journal entry, regardless of source, passes automatic validation, the system shall post it directly with no separate human approval step.
Traces     : US-FIN-004, US-FIN-005, US-FIN-006, US-FIN-007, US-FIN-009
Entities   : ENT-FIN-004
Rationale  : POL-FIN-001, POL-FIN-003, POL-FIN-004, POL-FIN-018 — the single unified rule
Source     : general-accounting-system-plan-en.md §8.1
Priority   : HIGH
#### AC-FIN-017 — [REQ-FIN-017]
Given a DRAFT entry that passes every check in REQ-FIN-018..021
When validation completes
Then the system sets statusCode=POSTED, postedAt=now(), and the entry becomes fully locked (no edit, no delete — REQ-FIN-034-equivalent lock, POL-FIN-013)

### REQ-FIN-018 — رفض عدم توازن القيد / Reject an unbalanced entry
Pattern    : unwanted
Statement  : If a journal entry's total debits do not equal its total credits, then the system shall reject posting.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : RULE-FIN-006; POL-FIN-001
Source     : general-accounting-system-plan-en.md §12.1
Priority   : HIGH
#### AC-FIN-018 — [REQ-FIN-018]
Given a DRAFT entry with debit lines totaling 100.00 and credit lines totaling 99.99
When the system validates it
Then it rejects posting with the imbalance amount shown

### REQ-FIN-019 — رفض حساب غير مؤهَّل للترحيل / Reject a non-postable account
Pattern    : unwanted
Statement  : If a journal line targets an account that is not a leaf, not active, or not marked as accepting direct posting, then the system shall reject posting.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-001, ENT-FIN-005
Rationale  : RULE-FIN-007; POL-FIN-003
Source     : general-accounting-system-plan-en.md §12.3
Priority   : HIGH
#### AC-FIN-019 — [REQ-FIN-019]
Given a DRAFT entry with a line targeting a non-leaf (rollup) account
When the system validates it
Then it rejects posting, naming the offending line

### REQ-FIN-020 — رفض فترة مغلقة عند الترحيل / Reject a closed period at post time
Pattern    : unwanted
Statement  : If a journal entry's period is not Open at the moment of posting, then the system shall reject posting, even if it was Open when the entry was built.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-004, ENT-FIN-008
Rationale  : RULE-FIN-008; POL-FIN-004 — checked at post time, not build time
Source     : general-accounting-system-plan-en.md §12.4
Priority   : HIGH
#### AC-FIN-020 — [REQ-FIN-020]
Given a DRAFT entry whose period was Open when built but is now Hard Closed
When the system attempts to post it
Then it rejects posting citing the period's current state

### REQ-FIN-021 — رفض قيمة بُعد غير صالحة / Reject an invalid dimension value
Pattern    : unwanted
Statement  : If a journal line cites a dimension value that does not belong to its stated dimension or is inactive, then the system shall reject posting.
Traces     : US-FIN-004, US-FIN-005
Entities   : ENT-FIN-006
Rationale  : RULE-FIN-009
Source     : general-accounting-system-plan-en.md §8.1 ("dimension valid")
Priority   : MEDIUM
#### AC-FIN-021 — [REQ-FIN-021]
Given a DRAFT entry line citing an inactive DimensionValue
When the system validates it
Then it rejects posting, naming the offending line and dimension

### REQ-FIN-022 — إنشاء قالب متكرر/عكسي / Create a recurring or reversing template
Pattern    : event
Statement  : When an accountant creates a recurring or reversing template with its lines, the system shall record its schedule and store it for future runs.
Traces     : US-FIN-006
Entities   : ENT-FIN-011, ENT-FIN-012
Rationale  : §7.3 — templates defined once as data
Source     : general-accounting-system-plan-en.md §7.3
Priority   : MEDIUM
#### AC-FIN-022 — [REQ-FIN-022]
Given a schedule type, a frequency (for recurring) and at least two balanced lines
When an accountant submits the template form
Then the system creates the active RecurringTemplate

### REQ-FIN-023 — تشغيل قالب متكرر / Run a recurring template on schedule
Pattern    : event
Statement  : When a recurring template's next run date arrives, the system shall generate and post a journal entry from it exactly as REQ-FIN-017 describes.
Traces     : US-FIN-006
Entities   : ENT-FIN-004, ENT-FIN-011
Rationale  : §7.3
Source     : general-accounting-system-plan-en.md §7.3
Priority   : MEDIUM
#### AC-FIN-023 — [REQ-FIN-023]
Given an active recurring template whose nextRunDate is today
When the scheduled run executes
Then the system builds and posts one entry from the template and advances nextRunDate per its frequency

### REQ-FIN-024 — عكس تلقائي في الفترة التالية / Automatic reversal in the next period
Pattern    : event
Statement  : When a reversing template's entry posts, the system shall automatically build and post its exact reversal in the next period.
Traces     : US-FIN-006
Entities   : ENT-FIN-004
Rationale  : §7.3; POL-FIN-007
Source     : general-accounting-system-plan-en.md §7.3
Priority   : MEDIUM
#### AC-FIN-024 — [REQ-FIN-024]
Given a reversing-type template entry posted in period N
When period N+1 opens (or immediately, per the template's own trigger)
Then the system posts a linked reversal entry in period N+1

### REQ-FIN-025 — إنشاء قاعدة توزيع / Create an allocation rule
Pattern    : event
Statement  : When an accountant creates an allocation rule with its targets, the system shall record how the source account's balance distributes across them.
Traces     : US-FIN-007
Entities   : ENT-FIN-013, ENT-FIN-014
Rationale  : §7.4
Source     : general-accounting-system-plan-en.md §7.4
Priority   : MEDIUM
#### AC-FIN-025 — [REQ-FIN-025]
Given a source account and at least one target with a distribution type
When an accountant submits the allocation rule form
Then the system creates the active AllocationRule

### REQ-FIN-026 — تشغيل قاعدة توزيع / Run an allocation rule
Pattern    : event
Statement  : When an allocation rule runs, the system shall distribute the source account's current balance across its targets per their distribution type, applying the same remainder guarantee as any compound distribution.
Traces     : US-FIN-007
Entities   : ENT-FIN-004, ENT-FIN-013, ENT-FIN-014
Rationale  : §7.4; RULE-FIN-010 reused
Source     : general-accounting-system-plan-en.md §7.4, §6.3
Priority   : MEDIUM
#### AC-FIN-026 — [REQ-FIN-026]
Given an allocation rule with two PERCENTAGE targets and one REMAINDER target, and a source balance of 1,000.00
When an accountant runs it
Then the system builds and posts one entry whose target lines sum exactly to 1,000.00, the remainder target absorbing the rounding difference

### REQ-FIN-027 — عرض/بحث قيود اليومية / Search and view journal entries
Pattern    : event
Statement  : When an accountant searches journal entries, the system shall return matching entries with their full status detail, unmodified.
Traces     : US-FIN-008
Entities   : ENT-FIN-004
Rationale  : POL-FIN-013
Source     : general-accounting-system-plan-en.md §8.4
Priority   : HIGH
#### AC-FIN-027 — [REQ-FIN-027]
Given entries across several statuses and periods
When an accountant filters by period and status
Then the system returns exactly the matching entries, unmodified

### REQ-FIN-028 — عكس قيد / Reverse a posted entry
Pattern    : event
Statement  : When an accountant reverses a posted entry, the system shall build and post a new entry mirroring it line-for-line with opposite directions and equal amounts, linked bidirectionally to the original.
Traces     : US-FIN-009
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : RULE-FIN-011; POL-FIN-007
Source     : general-accounting-system-plan-en.md §9
Priority   : HIGH
#### AC-FIN-028 — [REQ-FIN-028]
Given a POSTED entry with three lines
When an accountant reverses it
Then the system posts a new entry with the same three lines' amounts and opposite directions, and both entries reference each other (originalEntryId/reversalEntryId)

### REQ-FIN-029 — ترحيل العكس في الفترة الحالية عند إغلاق الأصل / Post the reversal in the current period when the original's period is closed
Pattern    : event
Statement  : When the original entry's period is closed, the system shall post its reversal into the current open period instead.
Traces     : US-FIN-009
Entities   : ENT-FIN-004, ENT-FIN-008
Rationale  : RULE-FIN-012
Source     : general-accounting-system-plan-en.md §9
Priority   : MEDIUM
#### AC-FIN-029 — [REQ-FIN-029]
Given a POSTED entry whose period is now Hard Closed
When an accountant reverses it
Then the system posts the reversal into the current open period, not the closed one

### REQ-FIN-030 — رفض عكس قيد غير مُرحَّل / Reject reversing a non-posted entry
Pattern    : unwanted
Statement  : If an entry is not POSTED, then the system shall reject a reverse action on it.
Traces     : US-FIN-009
Entities   : ENT-FIN-004
Rationale  : RULE-FIN-013 — prevents double-reversal or reversing a DRAFT/VOID row
Source     : general-accounting-system-plan-en.md §9
Priority   : MEDIUM
#### AC-FIN-030 — [REQ-FIN-030]
Given an entry already reversed once (statusCode=VOID via its own reversal link)
When an accountant attempts to reverse it again
Then the system rejects the action

### REQ-FIN-031 — إنشاء سنة مالية وفتراتها / Create a fiscal year with its periods
Pattern    : event
Statement  : When a finance administrator creates a fiscal year, the system shall generate its periods in the Open state per the chosen calendar.
Traces     : US-FIN-010
Entities   : ENT-FIN-007, ENT-FIN-008
Rationale  : §10.1-§10.2
Source     : general-accounting-system-plan-en.md §10.1, §10.4
Priority   : HIGH
#### AC-FIN-031 — [REQ-FIN-031]
Given a start date, end date and period count
When an administrator creates the fiscal year
Then the system creates the year and its periods, each initially Open

### REQ-FIN-032 — فتح فترة / Open a period
Pattern    : event
Statement  : When a finance administrator opens a period, the system shall allow normal posting into it.
Traces     : US-FIN-010
Entities   : ENT-FIN-008
Rationale  : §10.2
Source     : general-accounting-system-plan-en.md §10.2
Priority   : MEDIUM
#### AC-FIN-032 — [REQ-FIN-032]
Given a period not currently Open
When an administrator reopens it (soft-closed only, per §10.2 "re-openable")
Then the system sets statusCode=OPEN

### REQ-FIN-033 — إغلاق ناعم لفترة / Soft-close a period
Pattern    : event
Statement  : When a finance administrator soft-closes a period, the system shall block normal posting into it while still allowing authorized adjustments.
Traces     : US-FIN-010
Entities   : ENT-FIN-008
Rationale  : §10.2
Source     : general-accounting-system-plan-en.md §10.2
Priority   : MEDIUM
#### AC-FIN-033 — [REQ-FIN-033]
Given an Open period
When an administrator soft-closes it
Then the system sets statusCode=SOFT_CLOSE and REQ-FIN-020 rejects normal (non-adjustment) postings to it thereafter

### REQ-FIN-034 — إغلاق صارم لفترة / Hard-close a period
Pattern    : event
Statement  : When an authorized approver hard-closes a period, the system shall permanently block any posting into it.
Traces     : US-FIN-010, US-FIN-011
Entities   : ENT-FIN-008
Rationale  : §10.2-§10.3
Source     : general-accounting-system-plan-en.md §10.2, §10.3
Priority   : HIGH
#### AC-FIN-034 — [REQ-FIN-034]
Given a Soft Closed period
When an authorized approver hard-closes it
Then the system sets statusCode=HARD_CLOSE, closedBy and closedAt, and the period becomes permanently not re-openable

### REQ-FIN-035 — رفض إعادة فتح فترة مغلقة صارمًا / Reject reopening a hard-closed period
Pattern    : unwanted
Statement  : If a period is Hard Closed, then the system shall reject any attempt to reopen it.
Traces     : US-FIN-010
Entities   : ENT-FIN-008
Rationale  : RULE-FIN-014 — "not re-openable" per §10.2
Source     : general-accounting-system-plan-en.md §10.2
Priority   : MEDIUM
#### AC-FIN-035 — [REQ-FIN-035]
Given a Hard Closed period
When an administrator attempts to reopen it
Then the system rejects the action

### REQ-FIN-036 — تشغيل إقفال نهاية السنة / Run year-end close
Pattern    : event
Statement  : When an authorized approver runs year-end close for a fiscal year whose periods are all Hard Closed, the system shall generate a balanced closing entry and a balanced opening entry for the next year.
Traces     : US-FIN-010
Entities   : ENT-FIN-004, ENT-FIN-007
Rationale  : POL-FIN-010
Source     : general-accounting-system-plan-en.md §10.4
Priority   : HIGH
#### AC-FIN-036 — [REQ-FIN-036]
Given a fiscal year with every period Hard Closed
When an approver runs year-end close
Then the system posts a closing entry (result accounts → Retained Earnings) and generates the next year's opening entry from the resulting balance-sheet balances, both entries individually balanced

### REQ-FIN-037 — تسجيل اعتماد إغلاق الفترة / Record period-close approval distinctly
Pattern    : event
Statement  : When an authorized approver closes a period, the system shall record that approval as a distinct act from any entry creation in that period.
Traces     : US-FIN-011
Entities   : ENT-FIN-008
Rationale  : §8.2, §10.3 — the single human control point
Source     : general-accounting-system-plan-en.md §8.2, §10.3
Priority   : HIGH
#### AC-FIN-037 — [REQ-FIN-037]
Given a period ready to hard-close
When the approval is recorded
Then closedBy and closedAt are set to the approving principal and moment, distinct from any entry's createdBy in that period

### REQ-FIN-038 — فصل صلاحية الاعتماد عن صلاحية الإنشاء / Separate the approval permission from the creation permission
Pattern    : ubiquitous
Statement  : The system shall gate the period-close-approval action behind a permission distinct from the journal-entry-creation permission, enforced by the Security module.
Traces     : US-FIN-011
Entities   : ENT-FIN-008
Rationale  : POL-FIN-016; RULE-FIN-015
Source     : general-accounting-system-plan-en.md §2.2, §8.2, §10.3
Priority   : HIGH
#### AC-FIN-038 — [REQ-FIN-038]
Given a role holding only the entry-creation permission
When that role's user attempts the period-close-approval action
Then the system denies it (the CORE interceptor, per SEC's own mechanism)

### REQ-FIN-039 — دفتر الحساب المُشتق حيًا / Live-derived account ledger
Pattern    : event
Statement  : When an accountant opens the account ledger for an account and period range, the system shall compute it from POSTED lines at that moment.
Traces     : US-FIN-012
Entities   : ENT-FIN-005
Rationale  : POL-FIN-009, POL-FIN-011
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-039 — [REQ-FIN-039]
Given an account with posted lines across two periods
When the ledger is opened for that range
Then the system computes the running balance live from those lines, never from a stored column

### REQ-FIN-040 — ميزان مراجعة مُشتق حيًا ومتوازن دائمًا / Live-derived, always-balanced trial balance
Pattern    : event
Statement  : When a financial controller opens the trial balance for a period, the system shall compute it from POSTED lines such that total debit balances equal total credit balances.
Traces     : US-FIN-013
Entities   : ENT-FIN-005
Rationale  : POL-FIN-008, POL-FIN-009
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-040 — [REQ-FIN-040]
Given any set of POSTED entries in a period
When the trial balance is generated
Then its total debit balances equal its total credit balances exactly

### REQ-FIN-041 — ميزانية عمومية مع استمرارية / Balance sheet with continuity
Pattern    : event
Statement  : When a financial controller opens the balance sheet, the system shall compute balance-sheet account balances from POSTED lines, consistent with the prior year's closing balances as this year's opening balances.
Traces     : US-FIN-014
Entities   : ENT-FIN-005
Rationale  : POL-FIN-002, POL-FIN-009, POL-FIN-010
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-041 — [REQ-FIN-041]
Given a completed year-end close (REQ-FIN-036)
When the new year's balance sheet is opened
Then its opening balances equal the prior year's closing balances for every balance-sheet account

### REQ-FIN-042 — قائمة دخل تُفتح بصفر / Income statement opening at zero
Pattern    : event
Statement  : When a financial controller opens the income statement for a new fiscal year, the system shall compute result-account balances starting from zero for that year.
Traces     : US-FIN-015
Entities   : ENT-FIN-005
Rationale  : POL-FIN-002, POL-FIN-010
Source     : general-accounting-system-plan-en.md §11
Priority   : HIGH
#### AC-FIN-042 — [REQ-FIN-042]
Given a completed year-end close
When the new year's income statement is opened before any posting
Then every revenue/expense account shows a zero balance

### REQ-FIN-043 — تقارير أبعاد دون تكرار الحسابات / Dimension reports without duplicating accounts
Pattern    : event
Statement  : When a financial controller opens a dimension report, the system shall aggregate POSTED lines by the full account-and-dimension combination, never by the base account alone when a dimension is in play.
Traces     : US-FIN-016
Entities   : ENT-FIN-005, ENT-FIN-006
Rationale  : POL-FIN-011
Source     : general-accounting-system-plan-en.md §11, §12.11
Priority   : MEDIUM
#### AC-FIN-043 — [REQ-FIN-043]
Given postings to one account under two different PROJECT dimension values
When the dimension report is generated by PROJECT
Then the system shows two separate rows for that account, one per project, not one combined row

### REQ-FIN-044 — تسجيل FIN في وحدة الأمان / Register FIN into the Security module
Pattern    : event
Statement  : When FIN is deployed, the system shall register its module, screens and every action as data into the Security module.
Traces     : US-FIN-017
Entities   : ENT-FIN-004
Rationale  : POL-FIN-015
Source     : general-accounting-system-plan-en.md §2.2, §2.4
Priority   : HIGH
#### AC-FIN-044 — [REQ-FIN-044]
Given SEC v1 is gated and reachable
When FIN's onboarding runs
Then SEC records one ModuleRegistry row for FIN, one ScreenRegistry row per FIN screen, and one ActionRegistry row per action

### REQ-FIN-045 — تسجيل قوائم FIN في MDL / Register FIN's lookup types into the Lookup module
Pattern    : event
Statement  : When FIN is deployed, the system shall register its 13 lookup types as data into the Lookup module, naming FIN as owner.
Traces     : US-FIN-018
Entities   : ENT-FIN-001, ENT-FIN-004, ENT-FIN-007, ENT-FIN-008, ENT-FIN-009, ENT-FIN-010, ENT-FIN-011, ENT-FIN-013
Rationale  : POL-FIN-017
Source     : general-accounting-system-plan-en.md §5.2-§5.3
Priority   : HIGH
#### AC-FIN-045 — [REQ-FIN-045]
Given MDL v1 is gated and reachable
When FIN's onboarding runs
Then MDL records 13 LookupType rows owned by FIN (module-registry-fin.md → LOOKUPS OWNED)

### REQ-FIN-046 — تتبع نازل من التقرير إلى الحدث / Drill down from a report to its source event
Pattern    : event
Statement  : When a financial controller drills down from a financial-statement line, the system shall lead through the trial balance to the account ledger, to the original entry, to its source event reference.
Traces     : US-FIN-019
Entities   : ENT-FIN-004, ENT-FIN-005
Rationale  : POL-FIN-013
Source     : general-accounting-system-plan-en.md §11
Priority   : MEDIUM
#### AC-FIN-046 — [REQ-FIN-046]
Given a balance-sheet line
When a controller drills into it
Then the system navigates statement line → trial balance row → account ledger → the originating entry → its eventReference (or "manual", "recurring", "allocation" if not event-sourced)

## A5 — Business rules

### RULE-FIN-001 — منع ترحيل مباشر لحساب له أبناء / No direct posting on an account with children
Scope      : ENT-FIN-001
Trigger    : on update (isLeafFl)
Statement  : The system shall prevent an account with any child account from being marked as accepting direct posting.
Message    : ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" · en: "An account with sub-accounts cannot accept direct posting"
Traces     : REQ-FIN-002
Source     : general-accounting-system-plan-en.md §4.2

### RULE-FIN-002 — رفض رمز مكرر ضمن البُعد / Reject a duplicate code within a dimension
Scope      : ENT-FIN-003
Trigger    : on create (dimension value)
Statement  : The system shall reject a dimension value whose code already exists under the same dimension.
Message    : ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" · en: "This code is already used within this dimension"
Traces     : REQ-FIN-006
Source     : general-accounting-system-plan-en.md §4.2

### RULE-FIN-003 — سطر/هدف باقٍ واحد بالضبط عند التوزيع النسبي / Exactly one remainder line/target under percentage distribution
Scope      : ENT-FIN-010, ENT-FIN-014
Trigger    : on create/update (rule line or allocation target set)
Statement  : The system shall require exactly one line or target marked as the remainder whenever any sibling line or target uses percentage distribution.
Message    : ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" · en: "Exactly one remainder line is required when any percentage distribution is present"
Traces     : REQ-FIN-009
Source     : general-accounting-system-plan-en.md §6.3, §12.6

### RULE-FIN-004 — رفض مرجع حدث مكرر / Reject a duplicate event reference
Scope      : ENT-FIN-004
Trigger    : on create (event-sourced entry)
Statement  : The system shall reject building an entry for an event reference that has already produced a posted entry.
Message    : ar: "تم بالفعل ترحيل قيد لهذا المرجع" · en: "An entry for this event reference has already been posted"
Traces     : REQ-FIN-011
Source     : general-accounting-system-plan-en.md §12.12

### RULE-FIN-005 — رفض حدث بلا قاعدة نشطة / Reject an event with no active rule
Scope      : ENT-FIN-009
Trigger    : on create (event-sourced entry)
Statement  : The system shall reject building an entry for an event whose type has no active rule.
Message    : ar: "لا توجد قاعدة نشطة لهذا النوع من الأحداث" · en: "No active rule exists for this event type"
Traces     : REQ-FIN-013
Source     : general-accounting-system-plan-en.md §6.1

### RULE-FIN-006 — ثبات تساوي المدين والدائن / Debit=Credit invariant
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on post (any source)
Statement  : The system shall reject posting an entry whose total debits do not equal its total credits to the smallest currency unit.
Message    : ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" · en: "The entry is unbalanced — total debits do not equal total credits"
Traces     : REQ-FIN-018
Source     : general-accounting-system-plan-en.md §12.1

### RULE-FIN-007 — الترحيل للأوراق النشطة فقط / Posting only to leaf, active accounts
Scope      : ENT-FIN-001, ENT-FIN-005
Trigger    : on post (any source)
Statement  : The system shall reject posting a line targeting an account that is not a leaf, not active, or not marked as accepting direct posting.
Message    : ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" · en: "The target account does not accept direct posting"
Traces     : REQ-FIN-019
Source     : general-accounting-system-plan-en.md §12.3

### RULE-FIN-008 — بوابة الفترة عند الترحيل / Period gate at post time
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on post (any source)
Statement  : The system shall reject posting an entry whose period is not Open at that moment.
Message    : ar: "الفترة المستهدفة غير مفتوحة" · en: "The target period is not open"
Traces     : REQ-FIN-020
Source     : general-accounting-system-plan-en.md §12.4

### RULE-FIN-009 — صحة قيمة البُعد / Dimension value validity
Scope      : ENT-FIN-006
Trigger    : on post (any source)
Statement  : The system shall reject posting a line whose cited dimension value does not belong to its stated dimension or is inactive.
Message    : ar: "قيمة البُعد غير صالحة" · en: "The dimension value is invalid"
Traces     : REQ-FIN-021
Source     : general-accounting-system-plan-en.md §8.1

### RULE-FIN-010 — سطر الباقي يمتص فرق التقريب / The remainder line absorbs the rounding difference
Scope      : ENT-FIN-005, ENT-FIN-010, ENT-FIN-014
Trigger    : on build (compound/percentage distribution — rule engine or allocation)
Statement  : The system shall compute the remainder line's amount as the total minus the sum of every other line, after every percentage line rounds to the smallest currency unit; the remainder line is never itself computed as a percentage.
Message    : ar: "سطر الباقي يُحسب كفرق، لا كنسبة" · en: "The remainder line is computed as a difference, never as a percentage"
Traces     : REQ-FIN-012, REQ-FIN-026
Source     : general-accounting-system-plan-en.md §6.3, §12.6

### RULE-FIN-011 — العكس تام ومرتبط / Reversal is exact and linked
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on reverse
Statement  : The system shall build the reversal entry with the same lines as the original, each with the opposite direction and the same amount, and link both entries to each other.
Message    : ar: "قيد العكس يطابق الأصل بعكس الاتجاه" · en: "The reversal entry mirrors the original with opposite direction"
Traces     : REQ-FIN-028
Source     : general-accounting-system-plan-en.md §12.7, §9

### RULE-FIN-012 — ترحيل العكس بالفترة الحالية عند إغلاق الأصل / Reversal posts to the current period when the original's is closed
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on reverse
Statement  : The system shall post the reversal into the current open period when the original entry's own period is no longer Open.
Message    : ar: "سيُرحَّل قيد العكس في الفترة المفتوحة الحالية" · en: "The reversal will post into the current open period"
Traces     : REQ-FIN-029
Source     : general-accounting-system-plan-en.md §9

### RULE-FIN-013 — رفض عكس قيد غير مُرحَّل / Reject reversing a non-posted entry
Scope      : ENT-FIN-004
Trigger    : on reverse
Statement  : The system shall reject a reverse action on an entry that is not POSTED.
Message    : ar: "لا يمكن عكس قيد غير مُرحَّل" · en: "A non-posted entry cannot be reversed"
Traces     : REQ-FIN-030
Source     : general-accounting-system-plan-en.md §9

### RULE-FIN-014 — رفض إعادة فتح فترة مغلقة صارمًا / Reject reopening a hard-closed period
Scope      : ENT-FIN-008
Trigger    : on update (period status)
Statement  : The system shall reject any attempt to reopen a Hard Closed period.
Message    : ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" · en: "The period is hard-closed and cannot be reopened"
Traces     : REQ-FIN-035
Source     : general-accounting-system-plan-en.md §10.2

### RULE-FIN-015 — فصل صلاحية الاعتماد عن صلاحية الإنشاء / Separate the approval permission from the creation permission
Scope      : ENT-FIN-008
Trigger    : on evaluate (period-close-approval action)
Statement  : The system shall require the period-close-approval action to be gated by a permission distinct from the journal-entry-creation permission, enforced through the Security module.
Message    : ar: "صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود" · en: "The close-approval permission is separate from the entry-creation permission"
Traces     : REQ-FIN-038
Source     : general-accounting-system-plan-en.md §2.2, §8.2, §10.3

### RULE-FIN-016 — قفل القيد بعد الترحيل / Lock an entry after posting
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on evaluate (any edit/delete attempt)
Statement  : The system shall reject any edit or delete attempt on a POSTED entry or its lines; correction is only through a reversal (REQ-FIN-028).
Message    : ar: "القيد المُرحَّل مقفل؛ التصحيح فقط عبر العكس" · en: "A posted entry is locked; correction is only through a reversal"
Traces     : REQ-FIN-016, REQ-FIN-017
Source     : general-accounting-system-plan-en.md §8.3, §12.13

## A6 — Lookups

All 13 lookup types below are owned by FIN and registered into MDL (module-registry-fin.md
→ LOOKUPS OWNED carries the full source citation per key; only the values are repeated here).

| Key | Values |
|---|---|
| ACCOUNT_TYPE | ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| DEBIT_CREDIT | DEBIT, CREDIT |
| PERIOD_STATE | OPEN, SOFT_CLOSE, HARD_CLOSE, YEAR_END_CLOSE |
| FISCAL_YEAR_STATUS | OPEN, CLOSED |
| JOURNAL_TYPE | EVENT_GENERATED, MANUAL, RECURRING, ALLOCATION, REVERSAL |
| JOURNAL_STATUS | DRAFT, POSTED, VOID |
| ACCOUNTING_EVENT_TYPE | none seeded — host-specific, added as data [§3, §6.4] |
| PAYMENT_METHOD | none seeded — host-specific |
| ACCOUNT_DERIVATION_TYPE | CONSTANT, DIRECT, MAPPING |
| AMOUNT_SOURCE_TYPE | FIELD, PERCENTAGE, REMAINDER |
| DISTRIBUTION_TYPE | FIXED, PERCENTAGE, REMAINDER |
| RECURRING_SCHEDULE_TYPE | RECURRING, REVERSING |
| RECURRING_FREQUENCY | MONTHLY, QUARTERLY, ANNUALLY, WEEKLY |

Consumed lookups: none — FIN owns every coded value list it uses.

## A7 — Status lifecycle

**ENT-FIN-004 JournalEntry.statusCode (JOURNAL_STATUS, 3 states)**
```
DRAFT  --(REQ-FIN-017, automatic validation passes)--> POSTED
POSTED --(REQ-FIN-028, reverse action)----------------> VOID   (the original; its reversal is itself a new POSTED entry)
```
DRAFT is transient (build → validate happens in one orchestration, RULE-FIN-016 locks
POSTED immediately); a DRAFT that fails validation is never saved (REQ-FIN-015/018-021
reject before any row is written) — not a stored intermediate state a user can browse.

**ENT-FIN-008 FiscalPeriod.statusCode (PERIOD_STATE, 4 states)**
```
OPEN        --(REQ-FIN-033, soft-close)--------> SOFT_CLOSE
SOFT_CLOSE  --(REQ-FIN-032, reopen)------------> OPEN
SOFT_CLOSE  --(REQ-FIN-034, hard-close)--------> HARD_CLOSE
HARD_CLOSE  --(REQ-FIN-036, year-end close, all periods of the year)--> YEAR_END_CLOSE
```
HARD_CLOSE and YEAR_END_CLOSE are terminal (RULE-FIN-014 — never reopened).

**ENT-FIN-007 FiscalYear.statusCode (FISCAL_YEAR_STATUS, 2 states)** — binary
(OPEN/CLOSED, set by REQ-FIN-036) — not applicable for a diagram.

All other statuses in this module (isActiveFl flags) are binary — not applicable.

## A8 — Module dependencies

| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate (assigned by P2) |
|---|---|---|---|---|
| User (identity, principal string on audit columns) | ENT-SEC-001 | SEC | HARD-FK (per SEC's own precedent: principal string, not numeric FK — see AUTO-DECISIONS) | assigned by P2 |
| ModuleRegistry, ScreenRegistry, ActionRegistry | ENT-SEC-004, ENT-SEC-005, ENT-SEC-006 | SEC | HARD-FK (registration as data) | assigned by P2 |
| LookupType, LookupValue | ENT-MDL-001, ENT-MDL-002 | MDL | HARD-FK (registration + runtime read) | assigned by P2 |

| External service | Purpose | Integration kind |
|---|---|---|
| Notifications (ready, external) | period-close-awaiting notice | SOFT / optional, per general-accounting-system-plan-en.md §2.3 |
| File Service (ready, external) | statement export | SOFT / optional, per general-accounting-system-plan-en.md §2.3 |

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-FIN-001 — شجرة الحسابات / Chart of accounts
### B1 — Definition
Purpose      : إدارة شجرة الحسابات الهرمية.
Entities     : ENT-FIN-001
Operations   : search, create, read, update, deactivate
Users        : مسؤول مالي
Navigation   : FIN → Setup → Chart of accounts
Content shape: true hierarchy (parent/child)
Traces       : REQ-FIN-001, REQ-FIN-002, REQ-FIN-003
Composite    : Search + Entry = ONE screen requirement
### B2 — Search / list
Filters: code(LIKE), nameAr/nameEn(LIKE), accountTypeCode(EXACT), isActiveFl(EXACT) — correspond to result columns.
### B3 — Input
Fields: code, nameAr, nameEn, accountTypeCode, natureCode, parentAccountId, isLeafFl (ENT-FIN-001; RULE-FIN-001 blocks isLeafFl=true on a parent). Button: Deactivate.
### B4 — Access
Page code: FIN_ACCOUNTS. Actions: VIEW, CREATE, UPDATE, DELETE (deactivate).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search accounts | GET | /api/v1/fin/accounts | filters, paging | Page\<Account\> | — | REQ-FIN-001 |
| create account | POST | /api/v1/fin/accounts | account fields | Account | RULE-FIN-001 | REQ-FIN-001, REQ-FIN-002 |
| update account | PUT | /api/v1/fin/accounts/{id} | account fields | Account | RULE-FIN-001 | REQ-FIN-002 |
| deactivate account | DELETE | /api/v1/fin/accounts/{id} | id | confirmation | — | REQ-FIN-003 |

## SCR-REQ-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values
### B1 — Definition
Purpose      : إدارة الأبعاد وقيمها.
Entities     : ENT-FIN-002, ENT-FIN-003
Operations   : search, create, read, deactivate (dimension); create, read, search, deactivate (value)
Users        : مسؤول مالي
Navigation   : FIN → Setup → Dimensions
Content shape: header + repeating lines (master dimensions + detail values)
Traces       : REQ-FIN-004, REQ-FIN-005, REQ-FIN-006
Composite    : Master (dimensions) + Detail (values) = ONE screen requirement
### B2 — Search / list
Dimension filters: code(LIKE). Value filters: code(LIKE) — correspond to result columns.
### B3 — Input
Dimension fields: code, nameAr, nameEn. Value fields: code, nameAr, nameEn, sortOrder (ENT-FIN-002/003).
### B4 — Access
Page code: FIN_DIMENSIONS. Actions: VIEW, CREATE, UPDATE (deactivate only, modeled as UPDATE).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search dimensions | GET | /api/v1/fin/dimensions | filters, paging | Page\<Dimension\> | — | REQ-FIN-004 |
| create dimension | POST | /api/v1/fin/dimensions | code, nameAr, nameEn | Dimension | — | REQ-FIN-004 |
| create dimension value | POST | /api/v1/fin/dimensions/{id}/values | code, nameAr, nameEn, sortOrder | DimensionValue | RULE-FIN-002 | REQ-FIN-005, REQ-FIN-006 |
| search dimension values | GET | /api/v1/fin/dimensions/{id}/values | filters, paging | Page\<DimensionValue\> | — | REQ-FIN-005 |

## SCR-REQ-FIN-003 — قواعد المحرك / Engine rules
### B1 — Definition
Purpose      : إدارة قواعد ربط أنواع الأحداث بسطور القيد.
Entities     : ENT-FIN-009, ENT-FIN-010
Operations   : search, create, read, update, deactivate (rule); create, read, update, delete (line)
Users        : مسؤول مالي
Navigation   : FIN → Setup → Engine rules
Content shape: header + repeating lines (rule header + its lines)
Traces       : REQ-FIN-007, REQ-FIN-008, REQ-FIN-009
Composite    : Master (rules) + Detail (lines) = ONE screen requirement
### B2 — Search / list
Filters: eventTypeCode(EXACT), isActiveFl(EXACT) — correspond to result columns.
### B3 — Input
Rule fields: eventTypeCode, nameAr, nameEn (ENT-FIN-009). Line fields: accountDerivationTypeCode,
accountDerivationValue, amountSourceTypeCode, amountSourceValue, directionCode, distributionTypeCode,
isRemainderFl (ENT-FIN-010; RULE-FIN-003 blocks saving until exactly one remainder line exists
when a percentage line is present).
### B4 — Access
Page code: FIN_RULES. Actions: VIEW, CREATE, UPDATE, DELETE (deactivate rule / delete line).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search rules | GET | /api/v1/fin/event-rules | filters, paging | Page\<EventTypeRule\> | — | REQ-FIN-007 |
| create rule | POST | /api/v1/fin/event-rules | eventTypeCode, nameAr, nameEn | EventTypeRule | — | REQ-FIN-007 |
| add rule line | POST | /api/v1/fin/event-rules/{id}/lines | line fields | RuleLine | RULE-FIN-003 | REQ-FIN-008, REQ-FIN-009 |

## SCR-REQ-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates
### B1 — Definition
Purpose      : إدارة القوالب المتكررة والعكسية.
Entities     : ENT-FIN-011, ENT-FIN-012
Operations   : search, create, read, update, deactivate (template); create, read, update, delete (line)
Users        : محاسب
Navigation   : FIN → Setup → Recurring/reversing templates
Content shape: header + repeating lines
Traces       : REQ-FIN-022, REQ-FIN-023, REQ-FIN-024
Composite    : Master (templates) + Detail (lines) = ONE screen requirement
### B2 — Search / list
Filters: nameAr/nameEn(LIKE), scheduleTypeCode(EXACT), isActiveFl(EXACT).
### B3 — Input
Template fields: nameAr, nameEn, scheduleTypeCode, frequencyCode, startDate, endDate (ENT-FIN-011).
Line fields: accountId, amount, directionCode, dimensionValueId (ENT-FIN-012).
### B4 — Access
Page code: FIN_RECURRING_TEMPLATES. Actions: VIEW, CREATE, UPDATE, DELETE.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search templates | GET | /api/v1/fin/recurring-templates | filters, paging | Page\<RecurringTemplate\> | — | REQ-FIN-022 |
| create template | POST | /api/v1/fin/recurring-templates | template + lines | RecurringTemplate | RULE-FIN-006 (reused, balance check applied at run time not save time) | REQ-FIN-022 |
| run template (system/scheduled) | POST | /api/v1/fin/recurring-templates/{id}/run | — | JournalEntry | RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009, RULE-FIN-011 | REQ-FIN-023, REQ-FIN-024 |

## SCR-REQ-FIN-005 — قواعد التوزيع / Allocation rules
### B1 — Definition
Purpose      : إدارة قواعد توزيع رصيد حساب مصدر على أهدافه.
Entities     : ENT-FIN-013, ENT-FIN-014
Operations   : search, create, read, update, deactivate (rule); create, read, update, delete (target); run
Users        : محاسب
Navigation   : FIN → Setup → Allocation rules
Content shape: header + repeating lines
Traces       : REQ-FIN-025, REQ-FIN-026
Composite    : Master (rules) + Detail (targets) = ONE screen requirement
### B2 — Search / list
Filters: nameAr/nameEn(LIKE), sourceAccountId(EXACT), isActiveFl(EXACT).
### B3 — Input
Rule fields: nameAr, nameEn, sourceAccountId (ENT-FIN-013). Target fields: targetAccountId,
dimensionValueId, distributionTypeCode, distributionValue, isRemainderFl (ENT-FIN-014;
RULE-FIN-003 applies).
### B4 — Access
Page code: FIN_ALLOCATION_RULES. Actions: VIEW, CREATE, UPDATE, DELETE.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search allocation rules | GET | /api/v1/fin/allocation-rules | filters, paging | Page\<AllocationRule\> | — | REQ-FIN-025 |
| create allocation rule | POST | /api/v1/fin/allocation-rules | rule + targets | AllocationRule | RULE-FIN-003 | REQ-FIN-025 |
| run allocation rule | POST | /api/v1/fin/allocation-rules/{id}/run | — | JournalEntry | RULE-FIN-006..011 | REQ-FIN-026 |

## SCR-REQ-FIN-006 — قيود اليومية / Journal entries (view + manual entry + reverse)
### B1 — Definition
Purpose      : عرض قيود اليومية بكل مصادرها، إدخال يدوي، وعكس قيد مُرحَّل.
Entities     : ENT-FIN-004, ENT-FIN-005, ENT-FIN-006
Operations   : search, create (manual), read, reverse
Users        : محاسب
Navigation   : FIN → Operations → Journal entries
Content shape: header + repeating lines with totals (debit/credit totals shown live while entering)
Traces       : REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030
Composite    : Search + Entry (with a "Reverse" action on a posted entry) = ONE screen requirement
### B2 — Search / list
Filters: docNo(LIKE), docDate(DATE_RANGE), periodId(EXACT), statusCode(EXACT), journalTypeCode(EXACT) — correspond to result columns.
### B3 — Input
Header fields: docDate, periodId, descriptionAr, descriptionEn (ENT-FIN-004; docNo/statusCode/
journalTypeCode system-set). Line fields (repeating): accountId, amount, directionCode,
dimension value(s) per JournalLineDimension, descriptionAr, descriptionEn (ENT-FIN-005/006).
Buttons: "Post" → REQ-FIN-017 (validates REQ-FIN-018..021 first, REQ-FIN-015 shows failures);
"Reverse" (on a POSTED row) → REQ-FIN-028/029/030.
### B4 — Access
Page code: FIN_JOURNAL_ENTRIES. Actions: VIEW, CREATE (incl. Post), UPDATE (Reverse, modeled
as an update-class action per §7.1 custom-action convention — `PERM_FIN_JOURNAL_ENTRIES_REVERSE`).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search entries | GET | /api/v1/fin/journal-entries | filters, paging | Page\<JournalEntry\> | — | REQ-FIN-027 |
| create manual entry | POST | /api/v1/fin/journal-entries | header + lines | JournalEntry (DRAFT then POSTED) | RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009 | REQ-FIN-014, REQ-FIN-015, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021 |
| build event entry (system) | POST | /api/v1/fin/journal-entries/from-event | canonical event payload | JournalEntry | RULE-FIN-004, RULE-FIN-005, RULE-FIN-006..009, RULE-FIN-010 | REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-017..021 |
| reverse entry | POST | /api/v1/fin/journal-entries/{id}/reverse | id | JournalEntry (the new reversal) | RULE-FIN-011, RULE-FIN-012, RULE-FIN-013 | REQ-FIN-028, REQ-FIN-029, REQ-FIN-030 |
| read entry | GET | /api/v1/fin/journal-entries/{id} | id | JournalEntry with lines | — | REQ-FIN-016, REQ-FIN-027 |

## SCR-REQ-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years + close approval + year-end close
### B1 — Definition
Purpose      : إدارة السنوات والفترات المالية، اعتماد الإغلاق، وتشغيل إقفال نهاية السنة.
Entities     : ENT-FIN-007, ENT-FIN-008
Operations   : create (year), search, read; open, soft-close, hard-close (period); run year-end close
Users        : مسؤول مالي (إدارة) / مراقب مالي (اعتماد الإغلاق — دور منفصل، POL-FIN-016)
Navigation   : FIN → Control → Fiscal periods & years
Content shape: header + repeating lines (year + its periods)
Traces       : REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038
Composite    : Master (years) + Detail (periods) = ONE screen requirement
### B2 — Search / list
Filters: fiscalYearId(EXACT), statusCode(EXACT).
### B3 — Input
Year fields: code, startDate, endDate, periodCount (ENT-FIN-007). Period actions per row:
Open, Soft-close, Hard-close (approval-gated). Year action: "Run year-end close" (enabled
only once every period is Hard Closed).
### B4 — Access
Page code: FIN_PERIODS. Actions: VIEW, CREATE (year), UPDATE (open/soft-close, and a distinct
custom action `PERM_FIN_PERIODS_CLOSE_APPROVE` for hard-close/year-end-close — RULE-FIN-015).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| create fiscal year | POST | /api/v1/fin/fiscal-years | code, startDate, endDate, periodCount | FiscalYear + FiscalPeriod[] | — | REQ-FIN-031 |
| open period | PATCH | /api/v1/fin/fiscal-periods/{id}/open | id | FiscalPeriod | — | REQ-FIN-032 |
| soft-close period | PATCH | /api/v1/fin/fiscal-periods/{id}/soft-close | id | FiscalPeriod | — | REQ-FIN-033 |
| hard-close period (approval) | PATCH | /api/v1/fin/fiscal-periods/{id}/hard-close | id | FiscalPeriod | RULE-FIN-014, RULE-FIN-015 | REQ-FIN-034, REQ-FIN-035, REQ-FIN-037, REQ-FIN-038 |
| run year-end close | POST | /api/v1/fin/fiscal-years/{id}/year-end-close | id | closing + opening JournalEntry | RULE-FIN-006..009, RULE-FIN-015 | REQ-FIN-036 |

## SCR-REQ-FIN-008 — دفتر الحساب / Account ledger
### B1 — Definition
Purpose      : عرض دفتر حساب مُشتق حيًا مع تتبع نازل.
Entities     : ENT-FIN-005
Operations   : read
Users        : محاسب / مراقب مالي
Navigation   : FIN → Reports → Account ledger; to: SCR-REQ-FIN-006 (drill-down to entry)
Content shape: flat record (running balance list)
Traces       : REQ-FIN-039, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: accountId(EXACT), periodId or date range(DATE_RANGE), dimension value(s)(EXACT).
### B3 — Input
Not applicable — read-only report.
### B4 — Access
Page code: FIN_ACCOUNT_LEDGER. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| account ledger | GET | /api/v1/fin/reports/account-ledger | accountId, date range, dimension filters | running-balance list, each row linking to its JournalEntry | — | REQ-FIN-039, REQ-FIN-046 |

## SCR-REQ-FIN-009 — ميزان المراجعة / Trial balance
### B1 — Definition
Purpose      : عرض ميزان مراجعة مُشتق حيًا ومتوازن دائمًا.
Entities     : ENT-FIN-005
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Trial balance; to: SCR-REQ-FIN-008 (drill-down per account)
Content shape: flat record (one row per account)
Traces       : REQ-FIN-040, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: periodId(EXACT), accountTypeCode(EXACT).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_TRIAL_BALANCE. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| trial balance | GET | /api/v1/fin/reports/trial-balance | periodId, filters | one row per account (debit/credit balance) | — | REQ-FIN-040, REQ-FIN-046 |

## SCR-REQ-FIN-010 — الميزانية العمومية / Balance sheet
### B1 — Definition
Purpose      : عرض ميزانية عمومية مُشتقة حيًا مع استمرارية الأرصدة الافتتاحية.
Entities     : ENT-FIN-005
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Balance sheet; to: SCR-REQ-FIN-009 (drill-down)
Content shape: header + repeating lines with totals (assets / liabilities / equity sections)
Traces       : REQ-FIN-041, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: fiscalYearId(EXACT), asOfDate.
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_BALANCE_SHEET. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| balance sheet | GET | /api/v1/fin/reports/balance-sheet | fiscalYearId, asOfDate | grouped balance-sheet accounts with balances | — | REQ-FIN-041, REQ-FIN-046 |

## SCR-REQ-FIN-011 — قائمة الدخل / Income statement
### B1 — Definition
Purpose      : عرض قائمة دخل مُشتقة حيًا تُفتح بصفر كل سنة.
Entities     : ENT-FIN-005
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Income statement; to: SCR-REQ-FIN-009 (drill-down)
Content shape: header + repeating lines with totals (revenue / expense sections)
Traces       : REQ-FIN-042, REQ-FIN-046
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: fiscalYearId(EXACT), periodId(DATE_RANGE within the year).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_INCOME_STATEMENT. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| income statement | GET | /api/v1/fin/reports/income-statement | fiscalYearId, period range | grouped revenue/expense accounts with balances | — | REQ-FIN-042, REQ-FIN-046 |

## SCR-REQ-FIN-012 — تقارير الأبعاد / Dimension reports
### B1 — Definition
Purpose      : عرض تقارير مجمّعة حسب البُعد دون تكرار الحسابات.
Entities     : ENT-FIN-005, ENT-FIN-006
Operations   : read
Users        : مراقب مالي
Navigation   : FIN → Reports → Dimension reports
Content shape: flat record (account × dimension-value rows)
Traces       : REQ-FIN-043
Composite    : single screen (report; no entry)
### B2 — Search / list
Filters: dimensionId(EXACT), dimensionValueId(EXACT), periodId(EXACT).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_DIMENSION_REPORTS. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| dimension report | GET | /api/v1/fin/reports/dimension | dimensionId, filters | one row per account+dimension-value combination | — | REQ-FIN-043 |

# STANDALONE

## Traceability matrix
| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-FIN-001 | REQ-FIN-001, REQ-FIN-002, REQ-FIN-003 | AC-FIN-001…003 | RULE-FIN-001 | ENT-FIN-001 | SCR-REQ-FIN-001 |
| US-FIN-002 | REQ-FIN-004, REQ-FIN-005, REQ-FIN-006 | AC-FIN-004…006 | RULE-FIN-002 | ENT-FIN-002, ENT-FIN-003 | SCR-REQ-FIN-002 |
| US-FIN-003 | REQ-FIN-007, REQ-FIN-008, REQ-FIN-009 | AC-FIN-007…009 | RULE-FIN-003 | ENT-FIN-009, ENT-FIN-010 | SCR-REQ-FIN-003 |
| US-FIN-004 | REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013 | AC-FIN-010…013 | RULE-FIN-004, RULE-FIN-005, RULE-FIN-010 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-009, ENT-FIN-010 | SCR-REQ-FIN-006 |
| US-FIN-005 | REQ-FIN-014, REQ-FIN-015 | AC-FIN-014, AC-FIN-015 | — | ENT-FIN-004, ENT-FIN-005 | SCR-REQ-FIN-006 |
| US-FIN-006 | REQ-FIN-022, REQ-FIN-023, REQ-FIN-024 | AC-FIN-022…024 | — | ENT-FIN-011, ENT-FIN-012 | SCR-REQ-FIN-004 |
| US-FIN-007 | REQ-FIN-025, REQ-FIN-026 | AC-FIN-025, AC-FIN-026 | RULE-FIN-010 | ENT-FIN-013, ENT-FIN-014 | SCR-REQ-FIN-005 |
| US-FIN-008 | REQ-FIN-016, REQ-FIN-027 | AC-FIN-016, AC-FIN-027 | RULE-FIN-016 | ENT-FIN-004 | SCR-REQ-FIN-006 |
| US-FIN-009 | REQ-FIN-028, REQ-FIN-029, REQ-FIN-030 | AC-FIN-028…030 | RULE-FIN-011, RULE-FIN-012, RULE-FIN-013 | ENT-FIN-004, ENT-FIN-005 | SCR-REQ-FIN-006 |
| US-FIN-010 | REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036 | AC-FIN-031…036 | RULE-FIN-014 | ENT-FIN-007, ENT-FIN-008 | SCR-REQ-FIN-007 |
| US-FIN-011 | REQ-FIN-037, REQ-FIN-038 | AC-FIN-037, AC-FIN-038 | RULE-FIN-015 | ENT-FIN-008 | SCR-REQ-FIN-007 |
| US-FIN-012 | REQ-FIN-039 | AC-FIN-039 | — | ENT-FIN-005 | SCR-REQ-FIN-008 |
| US-FIN-013 | REQ-FIN-040 | AC-FIN-040 | RULE-FIN-006 | ENT-FIN-005 | SCR-REQ-FIN-009 |
| US-FIN-014 | REQ-FIN-041 | AC-FIN-041 | — | ENT-FIN-005 | SCR-REQ-FIN-010 |
| US-FIN-015 | REQ-FIN-042 | AC-FIN-042 | — | ENT-FIN-005 | SCR-REQ-FIN-011 |
| US-FIN-016 | REQ-FIN-043 | AC-FIN-043 | — | ENT-FIN-005, ENT-FIN-006 | SCR-REQ-FIN-012 |
| US-FIN-017 | REQ-FIN-044 | AC-FIN-044 | — | ENT-FIN-004 | — (onboarding, no screen) |
| US-FIN-018 | REQ-FIN-045 | AC-FIN-045 | — | ENT-FIN-001, ENT-FIN-004, ENT-FIN-007, ENT-FIN-008, ENT-FIN-009, ENT-FIN-010, ENT-FIN-011, ENT-FIN-013 | — (onboarding, no screen) |
| US-FIN-019 | REQ-FIN-046 | AC-FIN-046 | — | ENT-FIN-004, ENT-FIN-005 | SCR-REQ-FIN-008, SCR-REQ-FIN-009, SCR-REQ-FIN-010 |

Plus REQ-FIN-017 through REQ-FIN-021 (unified validation, traced to US-FIN-004/005/006/007/009
collectively — see each REQ's own Traces line) and RULE-FIN-006 through RULE-FIN-009 (the four
post-time checks) — every REQ traces to ≥1 story, every AC to ≥1 REQ, every RULE to ≥1 REQ,
every SCR-REQ to ≥1 REQ. No orphan, no dangling id.

## Decisions applied
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| DEFAULT | `amount` type `NUMERIC(18,4)` | [KB:erp-domain-standards §6] platform default for money | non-breaking |
| DEFAULT | RecurringTemplateLine/AllocationTarget carry a single optional dimension value, not the header's full multi-dimension model | this stage, applying §9.3.3 "as data" philosophy pragmatically — the plan does not detail multi-dimension templates/allocations explicitly | non-breaking; extend to a full JournalLineDimension-style child table if multi-dimension templates are needed later |
No ADR was raised — no ambiguity reached the breaking/non-breaking fork of §9; every point
was settled by business policies, PRD stories, the registries, the knowledge source, or
documented above as a plain DEFAULT.

## Access summary
| Page code | Screen | VIEW | CREATE | UPDATE | DELETE | Custom |
|---|---|---|---|---|---|---|
| FIN_ACCOUNTS | Chart of accounts | role-granted | role-granted | role-granted | role-granted (deactivate) | — |
| FIN_DIMENSIONS | Dimensions | role-granted | role-granted | role-granted | — | — |
| FIN_RULES | Engine rules | role-granted | role-granted | role-granted | role-granted (deactivate/delete line) | — |
| FIN_RECURRING_TEMPLATES | Recurring/reversing templates | role-granted | role-granted | role-granted | role-granted | — |
| FIN_ALLOCATION_RULES | Allocation rules | role-granted | role-granted | role-granted | role-granted | — |
| FIN_JOURNAL_ENTRIES | Journal entries | role-granted | role-granted (incl. Post) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`) |
| FIN_PERIODS | Fiscal periods & years | role-granted | role-granted (year) | role-granted (open/soft-close) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE` — RULE-FIN-015, held by a role distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`) |
| FIN_ACCOUNT_LEDGER | Account ledger | role-granted | — | — | — | — |
| FIN_TRIAL_BALANCE | Trial balance | role-granted | — | — | — | — |
| FIN_BALANCE_SHEET | Balance sheet | role-granted | — | — | — | — |
| FIN_INCOME_STATEMENT | Income statement | role-granted | — | — | — | — |
| FIN_DIMENSION_REPORTS | Dimension reports | role-granted | — | — | — | — |
Every action beyond VIEW additionally requires VIEW on the same screen (platform gateway
convention, `profiles/erp.yaml → conventions.security_model.gateway_action`, enforced by
SEC's own mechanism — not restated as a FIN-owned RULE).
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: backend-execution-plan (FIN)>>>
# BACKEND EXECUTION PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Dialect : postgresql16
Framework : spring-boot-java (profile.stack.backend.framework)
Inputs : srs (v1, PRD-approved), db-script (v1), registry-srs (v1), registry-db (v1)
Open ADRs : 1 — erp/decisions/FIN/ (ADR-FIN-001, carried from P2; no new ADR this stage)
══════════════════════════════════════════════════════════════════

## PRE-GENERATION EXTRACTION — FIN v1 (working set; not part of the plan proper)

```
── FROM srs ──────────────────────────────────────────────────────────────
ENTITIES      14 — ENT-FIN-001..014 (master/config/lookup/transactional per SRS A3)
REQUIREMENTS  46 — REQ-FIN-001..046, each with 1 AC-FIN-*
RULES         16 — RULE-FIN-001..016, all 14 §12 must-honor points covered (see ALIGN)
SCREENS       12 — SCR-REQ-FIN-001..012
PERMISSIONS   12 secured page codes + PERM_<PAGE_CODE>_<ACTION>, gateway VIEW, plus the
              custom `PERM_FIN_PERIODS_CLOSE_APPROVE` (RULE-FIN-015 SoD)
LOOKUPS       13 keys, all FIN-owned, registered into MDL (SRS A6) — none CHECK-constrained
              locally (unlike SEC's ADR-SEC-001; MDL is already gated)
BUSINESS CODE JournalEntry.docNo — system-generated (platform numbering engine), unique
              per fiscalYearId, read-only after create
── FROM db-script ────────────────────────────────────────────────────────
TABLES        14 tables, FIN_ACCOUNT … FIN_ALLOCATION_TARGET
PK GENERATION every table: `GENERATED ALWAYS AS IDENTITY`
COLUMNS       146 DBF-FIN-001..146
CONSTRAINTS   PK_*, UQ_*, CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE (POL-FIN-005), FK_*; INDEXES IDX_*
XM            1 — XM-FIN-001 SOFT-READ → MDL_LOOKUP_VALUE, status ACTIVE
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   LookupType/LookupValue (MDL) via XM-FIN-001; SEC's identity/
                           authorization consumed as platform-standard integration, not
                           an XM row (ADR-FIN-001)
EXISTING LOOKUP KEYS        none reused — all 13 are new, FIN-owned
ID RANGES already used      API: none yet · QR: none yet
──────────────────────────────────────────────────────────────────────────
No row required §2A.3 extraction-failure handling.
```

## EXECUTION PLAN INDEX — FIN v1 — backend-execution-plan-fin.md
Profile: erp · dialect: postgresql16 · framework: spring-boot-java
Open ADRs: 1 — decisions/FIN/ (ADR-FIN-001, non-breaking, carried from P2)

**ENTITY REGISTRY**
| ENT | Name | Table | Business code | Operations |
|---|---|---|---|---|
| ENT-FIN-001 | Account | FIN_ACCOUNT | none | create, read, search, update, deactivate |
| ENT-FIN-002 | Dimension | FIN_DIMENSION | none | create, read, search, deactivate |
| ENT-FIN-003 | DimensionValue | FIN_DIMENSION_VALUE | none | create, read, search, deactivate |
| ENT-FIN-004 | JournalEntry | FIN_JOURNAL_ENTRY | **docNo** (numbering engine) | create (4 sources), read, search, reverse |
| ENT-FIN-005 | JournalLine | FIN_JOURNAL_LINE | none | create (with header), read |
| ENT-FIN-006 | JournalLineDimension | FIN_JOURNAL_LINE_DIM | none | create (with line), read |
| ENT-FIN-007 | FiscalYear | FIN_FISCAL_YEAR | none | create, read, search |
| ENT-FIN-008 | FiscalPeriod | FIN_FISCAL_PERIOD | none | create, read, search, open, soft-close, hard-close |
| ENT-FIN-009 | EventTypeRule | FIN_EVENT_TYPE_RULE | none | create, read, search, update, deactivate |
| ENT-FIN-010 | RuleLine | FIN_RULE_LINE | none | create, read, update, delete |
| ENT-FIN-011 | RecurringTemplate | FIN_RECURRING_TEMPLATE | none | create, read, search, update, deactivate |
| ENT-FIN-012 | RecurringTemplateLine | FIN_RECURRING_TEMPLATE_LINE | none | create, read, update, delete |
| ENT-FIN-013 | AllocationRule | FIN_ALLOCATION_RULE | none | create, read, search, update, deactivate |
| ENT-FIN-014 | AllocationTarget | FIN_ALLOCATION_TARGET | none | create, read, update, delete |

**FIELD REGISTRY** — see DB Alignment Manifest below (146 rows; property = camelCase of the
db-script column, per the same 1:1 transformation used for SEC/MDL — not restated as a
separate lighter table here given the row count, per this stage's own economy: the
Manifest already carries property/type/status, and read-only is uniformly: **Yes** for
every PK, every audit column, every system-timestamp column (postedAt, closedAt/closedBy,
createdAt-only child rows); **No** for every business-input field named in each entity's
SRS A3 "Required" column. The DB Alignment Manifest is the single canonical binding.

**API REGISTRY**
| API | Operation | Verb | Path | Traces (REQ) |
|---|---|---|---|---|
| API-FIN-001 | search accounts | GET | /api/v1/fin/accounts | REQ-FIN-001 |
| API-FIN-002 | create account | POST | /api/v1/fin/accounts | REQ-FIN-001, REQ-FIN-002 |
| API-FIN-003 | update account | PUT | /api/v1/fin/accounts/{id} | REQ-FIN-002 |
| API-FIN-004 | deactivate account | DELETE | /api/v1/fin/accounts/{id} | REQ-FIN-003 |
| API-FIN-005 | search dimensions | GET | /api/v1/fin/dimensions | REQ-FIN-004 |
| API-FIN-006 | create dimension | POST | /api/v1/fin/dimensions | REQ-FIN-004 |
| API-FIN-007 | create dimension value | POST | /api/v1/fin/dimensions/{id}/values | REQ-FIN-005, REQ-FIN-006 |
| API-FIN-008 | search dimension values | GET | /api/v1/fin/dimensions/{id}/values | REQ-FIN-005 |
| API-FIN-009 | search event-type rules | GET | /api/v1/fin/event-rules | REQ-FIN-007 |
| API-FIN-010 | create event-type rule | POST | /api/v1/fin/event-rules | REQ-FIN-007 |
| API-FIN-011 | add rule line | POST | /api/v1/fin/event-rules/{id}/lines | REQ-FIN-008, REQ-FIN-009 |
| API-FIN-012 | search templates | GET | /api/v1/fin/recurring-templates | REQ-FIN-022 |
| API-FIN-013 | create template | POST | /api/v1/fin/recurring-templates | REQ-FIN-022 |
| API-FIN-014 | run template | POST | /api/v1/fin/recurring-templates/{id}/run | REQ-FIN-023, REQ-FIN-024 |
| API-FIN-015 | search allocation rules | GET | /api/v1/fin/allocation-rules | REQ-FIN-025 |
| API-FIN-016 | create allocation rule | POST | /api/v1/fin/allocation-rules | REQ-FIN-025 |
| API-FIN-017 | run allocation rule | POST | /api/v1/fin/allocation-rules/{id}/run | REQ-FIN-026 |
| API-FIN-018 | search journal entries | GET | /api/v1/fin/journal-entries | REQ-FIN-027 |
| API-FIN-019 | create manual entry | POST | /api/v1/fin/journal-entries | REQ-FIN-014, REQ-FIN-015, REQ-FIN-017, REQ-FIN-018..021 |
| API-FIN-020 | build event entry (system) | POST | /api/v1/fin/journal-entries/from-event | REQ-FIN-010..013, REQ-FIN-017..021 |
| API-FIN-021 | reverse entry | POST | /api/v1/fin/journal-entries/{id}/reverse | REQ-FIN-028, REQ-FIN-029, REQ-FIN-030 |
| API-FIN-022 | read entry | GET | /api/v1/fin/journal-entries/{id} | REQ-FIN-016, REQ-FIN-027 |
| API-FIN-023 | create fiscal year | POST | /api/v1/fin/fiscal-years | REQ-FIN-031 |
| API-FIN-024 | open period | PATCH | /api/v1/fin/fiscal-periods/{id}/open | REQ-FIN-032 |
| API-FIN-025 | soft-close period | PATCH | /api/v1/fin/fiscal-periods/{id}/soft-close | REQ-FIN-033 |
| API-FIN-026 | hard-close period (approval) | PATCH | /api/v1/fin/fiscal-periods/{id}/hard-close | REQ-FIN-034, REQ-FIN-035, REQ-FIN-037, REQ-FIN-038 |
| API-FIN-027 | run year-end close | POST | /api/v1/fin/fiscal-years/{id}/year-end-close | REQ-FIN-036 |
| API-FIN-028 | account ledger | GET | /api/v1/fin/reports/account-ledger | REQ-FIN-039, REQ-FIN-046 |
| API-FIN-029 | trial balance | GET | /api/v1/fin/reports/trial-balance | REQ-FIN-040, REQ-FIN-046 |
| API-FIN-030 | balance sheet | GET | /api/v1/fin/reports/balance-sheet | REQ-FIN-041, REQ-FIN-046 |
| API-FIN-031 | income statement | GET | /api/v1/fin/reports/income-statement | REQ-FIN-042, REQ-FIN-046 |
| API-FIN-032 | dimension report | GET | /api/v1/fin/reports/dimension | REQ-FIN-043 |

**RULE REGISTRY** — all 16 SRS rules; full text: srs-fin.md §A5, cited by id in each API's
Validations line below (never restated in full here — single-source rule).

**SCREEN REGISTRY** — 12 secured screens; see SEC-BE (Phase 7) below.

**LOOKUP REGISTRY** — 13 keys; see SRS A6 (not restated).

**QRC SUMMARY** — 44 QR ids, QR-FIN-001..044 — see Query Reference Catalog below.

**DB ALIGNMENT** — see manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 1 (XM-FIN-001, SOFT-READ → MDL, ACTIVE)
**SECURITY** — 12 secured screens, data-driven role grants + 1 custom SoD-gated permission

## DB Alignment Manifest — FIN v1
All 146 rows: **status ✓ (aligned)**; XM populated only on lookup-backed columns (12
columns across 8 tables touch XM-FIN-001, noted individually below — a SOFT-READ, never
blocking).

| DBF | ENT | property | type | XM |
|---|---|---|---|---|
| DBF-FIN-001 | ENT-FIN-001 | accountPk | Long | — |
| DBF-FIN-002 | ENT-FIN-001 | code | String | — |
| DBF-FIN-003 | ENT-FIN-001 | nameAr | String | — |
| DBF-FIN-004 | ENT-FIN-001 | nameEn | String | — |
| DBF-FIN-005 | ENT-FIN-001 | accountTypeCode | String | XM-FIN-001 |
| DBF-FIN-006 | ENT-FIN-001 | natureCode | String | XM-FIN-001 |
| DBF-FIN-007 | ENT-FIN-001 | parentAccountId | Long | — |
| DBF-FIN-008 | ENT-FIN-001 | isLeafFl | Boolean | — |
| DBF-FIN-009 | ENT-FIN-001 | isActiveFl | Boolean | — |
| DBF-FIN-010 | ENT-FIN-001 | createdBy | String | — |
| DBF-FIN-011 | ENT-FIN-001 | createdAt | Instant | — |
| DBF-FIN-012 | ENT-FIN-001 | updatedBy | String | — |
| DBF-FIN-013 | ENT-FIN-001 | updatedAt | Instant | — |
| DBF-FIN-014 | ENT-FIN-002 | dimensionPk | Long | — |
| DBF-FIN-015 | ENT-FIN-002 | code | String | — |
| DBF-FIN-016 | ENT-FIN-002 | nameAr | String | — |
| DBF-FIN-017 | ENT-FIN-002 | nameEn | String | — |
| DBF-FIN-018 | ENT-FIN-002 | isActiveFl | Boolean | — |
| DBF-FIN-019 | ENT-FIN-002 | createdBy | String | — |
| DBF-FIN-020 | ENT-FIN-002 | createdAt | Instant | — |
| DBF-FIN-021 | ENT-FIN-002 | updatedBy | String | — |
| DBF-FIN-022 | ENT-FIN-002 | updatedAt | Instant | — |
| DBF-FIN-023 | ENT-FIN-003 | dimensionValuePk | Long | — |
| DBF-FIN-024 | ENT-FIN-003 | dimensionId | Long | — |
| DBF-FIN-025 | ENT-FIN-003 | code | String | — |
| DBF-FIN-026 | ENT-FIN-003 | nameAr | String | — |
| DBF-FIN-027 | ENT-FIN-003 | nameEn | String | — |
| DBF-FIN-028 | ENT-FIN-003 | sortOrder | Integer | — |
| DBF-FIN-029 | ENT-FIN-003 | isActiveFl | Boolean | — |
| DBF-FIN-030 | ENT-FIN-003 | createdBy | String | — |
| DBF-FIN-031 | ENT-FIN-003 | createdAt | Instant | — |
| DBF-FIN-032 | ENT-FIN-003 | updatedBy | String | — |
| DBF-FIN-033 | ENT-FIN-003 | updatedAt | Instant | — |
| DBF-FIN-034 | ENT-FIN-004 | journalEntryPk | Long | — |
| DBF-FIN-035 | ENT-FIN-004 | docNo | String | — |
| DBF-FIN-036 | ENT-FIN-004 | docDate | LocalDate | — |
| DBF-FIN-037 | ENT-FIN-004 | fiscalYearId | Long | — |
| DBF-FIN-038 | ENT-FIN-004 | periodId | Long | — |
| DBF-FIN-039 | ENT-FIN-004 | journalTypeCode | String | XM-FIN-001 |
| DBF-FIN-040 | ENT-FIN-004 | statusCode | String | XM-FIN-001 |
| DBF-FIN-041 | ENT-FIN-004 | eventReference | String | — |
| DBF-FIN-042 | ENT-FIN-004 | originalEntryId | Long | — |
| DBF-FIN-043 | ENT-FIN-004 | reversalEntryId | Long | — |
| DBF-FIN-044 | ENT-FIN-004 | descriptionAr | String | — |
| DBF-FIN-045 | ENT-FIN-004 | descriptionEn | String | — |
| DBF-FIN-046 | ENT-FIN-004 | postedAt | Instant | — |
| DBF-FIN-047 | ENT-FIN-004 | createdBy | String | — |
| DBF-FIN-048 | ENT-FIN-004 | createdAt | Instant | — |
| DBF-FIN-049 | ENT-FIN-004 | updatedBy | String | — |
| DBF-FIN-050 | ENT-FIN-004 | updatedAt | Instant | — |
| DBF-FIN-051 | ENT-FIN-005 | journalLinePk | Long | — |
| DBF-FIN-052 | ENT-FIN-005 | journalEntryId | Long | — |
| DBF-FIN-053 | ENT-FIN-005 | lineNo | Integer | — |
| DBF-FIN-054 | ENT-FIN-005 | accountId | Long | — |
| DBF-FIN-055 | ENT-FIN-005 | amount | BigDecimal | — |
| DBF-FIN-056 | ENT-FIN-005 | directionCode | String | XM-FIN-001 |
| DBF-FIN-057 | ENT-FIN-005 | isRemainderFl | Boolean | — |
| DBF-FIN-058 | ENT-FIN-005 | descriptionAr | String | — |
| DBF-FIN-059 | ENT-FIN-005 | descriptionEn | String | — |
| DBF-FIN-060 | ENT-FIN-005 | createdAt | Instant | — |
| DBF-FIN-061 | ENT-FIN-006 | journalLineDimensionPk | Long | — |
| DBF-FIN-062 | ENT-FIN-006 | journalLineId | Long | — |
| DBF-FIN-063 | ENT-FIN-006 | dimensionId | Long | — |
| DBF-FIN-064 | ENT-FIN-006 | dimensionValueId | Long | — |
| DBF-FIN-065 | ENT-FIN-007 | fiscalYearPk | Long | — |
| DBF-FIN-066 | ENT-FIN-007 | code | String | — |
| DBF-FIN-067 | ENT-FIN-007 | startDate | LocalDate | — |
| DBF-FIN-068 | ENT-FIN-007 | endDate | LocalDate | — |
| DBF-FIN-069 | ENT-FIN-007 | statusCode | String | XM-FIN-001 |
| DBF-FIN-070 | ENT-FIN-007 | isActiveFl | Boolean | — |
| DBF-FIN-071 | ENT-FIN-007 | createdBy | String | — |
| DBF-FIN-072 | ENT-FIN-007 | createdAt | Instant | — |
| DBF-FIN-073 | ENT-FIN-007 | updatedBy | String | — |
| DBF-FIN-074 | ENT-FIN-007 | updatedAt | Instant | — |
| DBF-FIN-075 | ENT-FIN-008 | fiscalPeriodPk | Long | — |
| DBF-FIN-076 | ENT-FIN-008 | fiscalYearId | Long | — |
| DBF-FIN-077 | ENT-FIN-008 | periodNo | Integer | — |
| DBF-FIN-078 | ENT-FIN-008 | nameAr | String | — |
| DBF-FIN-079 | ENT-FIN-008 | nameEn | String | — |
| DBF-FIN-080 | ENT-FIN-008 | startDate | LocalDate | — |
| DBF-FIN-081 | ENT-FIN-008 | endDate | LocalDate | — |
| DBF-FIN-082 | ENT-FIN-008 | statusCode | String | XM-FIN-001 |
| DBF-FIN-083 | ENT-FIN-008 | closedBy | String | — |
| DBF-FIN-084 | ENT-FIN-008 | closedAt | Instant | — |
| DBF-FIN-085 | ENT-FIN-008 | createdBy | String | — |
| DBF-FIN-086 | ENT-FIN-008 | createdAt | Instant | — |
| DBF-FIN-087 | ENT-FIN-008 | updatedBy | String | — |
| DBF-FIN-088 | ENT-FIN-008 | updatedAt | Instant | — |
| DBF-FIN-089 | ENT-FIN-009 | eventTypeRulePk | Long | — |
| DBF-FIN-090 | ENT-FIN-009 | eventTypeCode | String | XM-FIN-001 |
| DBF-FIN-091 | ENT-FIN-009 | nameAr | String | — |
| DBF-FIN-092 | ENT-FIN-009 | nameEn | String | — |
| DBF-FIN-093 | ENT-FIN-009 | isActiveFl | Boolean | — |
| DBF-FIN-094 | ENT-FIN-009 | createdBy | String | — |
| DBF-FIN-095 | ENT-FIN-009 | createdAt | Instant | — |
| DBF-FIN-096 | ENT-FIN-009 | updatedBy | String | — |
| DBF-FIN-097 | ENT-FIN-009 | updatedAt | Instant | — |
| DBF-FIN-098 | ENT-FIN-010 | ruleLineId | Long | — |
| DBF-FIN-099 | ENT-FIN-010 | eventTypeRuleId | Long | — |
| DBF-FIN-100 | ENT-FIN-010 | lineNo | Integer | — |
| DBF-FIN-101 | ENT-FIN-010 | accountDerivationTypeCode | String | XM-FIN-001 |
| DBF-FIN-102 | ENT-FIN-010 | accountDerivationValue | String | — |
| DBF-FIN-103 | ENT-FIN-010 | amountSourceTypeCode | String | XM-FIN-001 |
| DBF-FIN-104 | ENT-FIN-010 | amountSourceValue | String | — |
| DBF-FIN-105 | ENT-FIN-010 | directionCode | String | XM-FIN-001 |
| DBF-FIN-106 | ENT-FIN-010 | distributionTypeCode | String | XM-FIN-001 |
| DBF-FIN-107 | ENT-FIN-010 | isRemainderFl | Boolean | — |
| DBF-FIN-108 | ENT-FIN-010 | createdAt | Instant | — |
| DBF-FIN-109 | ENT-FIN-011 | recurringTemplateId | Long | — |
| DBF-FIN-110 | ENT-FIN-011 | nameAr | String | — |
| DBF-FIN-111 | ENT-FIN-011 | nameEn | String | — |
| DBF-FIN-112 | ENT-FIN-011 | scheduleTypeCode | String | XM-FIN-001 |
| DBF-FIN-113 | ENT-FIN-011 | frequencyCode | String | XM-FIN-001 |
| DBF-FIN-114 | ENT-FIN-011 | startDate | LocalDate | — |
| DBF-FIN-115 | ENT-FIN-011 | nextRunDate | LocalDate | — |
| DBF-FIN-116 | ENT-FIN-011 | endDate | LocalDate | — |
| DBF-FIN-117 | ENT-FIN-011 | isActiveFl | Boolean | — |
| DBF-FIN-118 | ENT-FIN-011 | createdBy | String | — |
| DBF-FIN-119 | ENT-FIN-011 | createdAt | Instant | — |
| DBF-FIN-120 | ENT-FIN-011 | updatedBy | String | — |
| DBF-FIN-121 | ENT-FIN-011 | updatedAt | Instant | — |
| DBF-FIN-122 | ENT-FIN-012 | recurringTemplateLineId | Long | — |
| DBF-FIN-123 | ENT-FIN-012 | recurringTemplateId | Long | — |
| DBF-FIN-124 | ENT-FIN-012 | lineNo | Integer | — |
| DBF-FIN-125 | ENT-FIN-012 | accountId | Long | — |
| DBF-FIN-126 | ENT-FIN-012 | amount | BigDecimal | — |
| DBF-FIN-127 | ENT-FIN-012 | directionCode | String | XM-FIN-001 |
| DBF-FIN-128 | ENT-FIN-012 | dimensionValueId | Long | — |
| DBF-FIN-129 | ENT-FIN-012 | createdAt | Instant | — |
| DBF-FIN-130 | ENT-FIN-013 | allocationRuleId | Long | — |
| DBF-FIN-131 | ENT-FIN-013 | nameAr | String | — |
| DBF-FIN-132 | ENT-FIN-013 | nameEn | String | — |
| DBF-FIN-133 | ENT-FIN-013 | sourceAccountId | Long | — |
| DBF-FIN-134 | ENT-FIN-013 | isActiveFl | Boolean | — |
| DBF-FIN-135 | ENT-FIN-013 | createdBy | String | — |
| DBF-FIN-136 | ENT-FIN-013 | createdAt | Instant | — |
| DBF-FIN-137 | ENT-FIN-013 | updatedBy | String | — |
| DBF-FIN-138 | ENT-FIN-013 | updatedAt | Instant | — |
| DBF-FIN-139 | ENT-FIN-014 | allocationTargetId | Long | — |
| DBF-FIN-140 | ENT-FIN-014 | allocationRuleId | Long | — |
| DBF-FIN-141 | ENT-FIN-014 | lineNo | Integer | — |
| DBF-FIN-142 | ENT-FIN-014 | targetAccountId | Long | — |
| DBF-FIN-143 | ENT-FIN-014 | dimensionValueId | Long | — |
| DBF-FIN-144 | ENT-FIN-014 | distributionTypeCode | String | XM-FIN-001 |
| DBF-FIN-145 | ENT-FIN-014 | distributionValue | BigDecimal | — |
| DBF-FIN-146 | ENT-FIN-014 | isRemainderFl | Boolean | — |

## Query Reference Catalog (QR-FIN-*)

> Logical specification only — never executable code.

| QR | Operation | API | Entity | Kind | Intent |
|---|---|---|---|---|---|
| QR-FIN-001 | FIND_BY_CRITERIA | API-FIN-001 | ENT-FIN-001 | search | search accounts |
| QR-FIN-002 | SAVE | API-FIN-002 | ENT-FIN-001 | create | create account |
| QR-FIN-003 | UPDATE | API-FIN-003 | ENT-FIN-001 | update | update account |
| QR-FIN-004 | UPDATE | API-FIN-004 | ENT-FIN-001 | deactivate | deactivate account |
| QR-FIN-005 | EXISTS | API-FIN-002 | ENT-FIN-001 | uniqueness | account code unique |
| QR-FIN-006 | EXISTS | API-FIN-002, API-FIN-003 | ENT-FIN-001 | RULE-FIN-001 | account has no children before marking leaf |
| QR-FIN-007 | FIND_BY_CRITERIA | API-FIN-005 | ENT-FIN-002 | search | search dimensions |
| QR-FIN-008 | SAVE | API-FIN-006 | ENT-FIN-002 | create | create dimension |
| QR-FIN-009 | SAVE | API-FIN-007 | ENT-FIN-003 | create | create dimension value |
| QR-FIN-010 | EXISTS | API-FIN-007 | ENT-FIN-003 | RULE-FIN-002 | dimension value code unique within dimension |
| QR-FIN-011 | FIND_BY_CRITERIA | API-FIN-008 | ENT-FIN-003 | search | search dimension values |
| QR-FIN-012 | FIND_BY_CRITERIA | API-FIN-009 | ENT-FIN-009 | search | search event-type rules |
| QR-FIN-013 | SAVE | API-FIN-010 | ENT-FIN-009 | create | create event-type rule |
| QR-FIN-014 | EXISTS | API-FIN-010 | ENT-FIN-009 | uniqueness | one active rule per event type |
| QR-FIN-015 | SAVE | API-FIN-011 | ENT-FIN-010 | create | add rule line |
| QR-FIN-016 | EXISTS | API-FIN-011 | ENT-FIN-010 | RULE-FIN-003 | exactly one remainder line when a percentage line exists |
| QR-FIN-017 | FIND_BY_CRITERIA | API-FIN-012 | ENT-FIN-011 | search | search templates |
| QR-FIN-018 | SAVE | API-FIN-013 | ENT-FIN-011, ENT-FIN-012 | create | create template with lines |
| QR-FIN-019 | FIND_ONE | API-FIN-014 | ENT-FIN-011 | run | load template due to run |
| QR-FIN-020 | FIND_BY_CRITERIA | API-FIN-015 | ENT-FIN-013 | search | search allocation rules |
| QR-FIN-021 | SAVE | API-FIN-016 | ENT-FIN-013, ENT-FIN-014 | create | create allocation rule with targets |
| QR-FIN-022 | FIND_ONE | API-FIN-017 | ENT-FIN-013 | run | load allocation rule + current source balance (via QR-FIN-040) |
| QR-FIN-023 | FIND_BY_CRITERIA | API-FIN-018 | ENT-FIN-004 | search | search journal entries |
| QR-FIN-024 | SAVE | API-FIN-019 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build manual entry (DRAFT) |
| QR-FIN-025 | SAVE | API-FIN-020 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build event entry (DRAFT) from rule |
| QR-FIN-026 | EXISTS | API-FIN-020 | ENT-FIN-004 | RULE-FIN-004 | duplicate eventReference |
| QR-FIN-027 | EXISTS | API-FIN-020 | ENT-FIN-009 | RULE-FIN-005 | active rule exists for event type |
| QR-FIN-028 | AGGREGATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-010 | compute remainder-line amount for a compound/percentage distribution |
| QR-FIN-029 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-006 | debits = credits |
| QR-FIN-030 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-001 | RULE-FIN-007 | every line's account is leaf + active |
| QR-FIN-031 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-008 | RULE-FIN-008 | entry's period is Open at post time |
| QR-FIN-032 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-006 | RULE-FIN-009 | every dimension value valid + active |
| QR-FIN-033 | UPDATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-004 | post | flip DRAFT → POSTED, set postedAt (RULE-FIN-016 lock takes effect) |
| QR-FIN-034 | SAVE | API-FIN-021 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build reversal entry (RULE-FIN-011) |
| QR-FIN-035 | EXISTS | API-FIN-021 | ENT-FIN-004 | RULE-FIN-013 | original entry is POSTED |
| QR-FIN-036 | FIND_ONE | API-FIN-021 | ENT-FIN-008 | RULE-FIN-012 | current open period, if original's is closed |
| QR-FIN-037 | FIND_ONE | API-FIN-022 | ENT-FIN-004 | read | read one entry with lines |
| QR-FIN-038 | SAVE | API-FIN-023 | ENT-FIN-007, ENT-FIN-008 | create | create fiscal year + periods |
| QR-FIN-039 | UPDATE | API-FIN-024, API-FIN-025, API-FIN-026 | ENT-FIN-008 | transition | open / soft-close / hard-close a period |
| QR-FIN-040 | EXISTS | API-FIN-026 | ENT-FIN-008 | RULE-FIN-014 | period not already Hard Closed before reopen attempts |
| QR-FIN-041 | AGGREGATE | API-FIN-027 | ENT-FIN-004, ENT-FIN-005 | year-end | compute closing balances, build closing + opening entries |
| QR-FIN-042 | FIND_BY_CRITERIA | API-FIN-028 | ENT-FIN-005 | report | account ledger (running balance) |
| QR-FIN-043 | AGGREGATE | API-FIN-029, API-FIN-030, API-FIN-031 | ENT-FIN-005 | report | trial balance / balance sheet / income statement account balances (shared aggregation, filtered per report by accountTypeCode) |
| QR-FIN-044 | AGGREGATE | API-FIN-032 | ENT-FIN-005, ENT-FIN-006 | report | dimension report (account × dimension value) |

Join governance: every posting-pipeline QR (024, 025, 028-033) is intra-module only
(FIN_JOURNAL_ENTRY/LINE/LINE_DIM/ACCOUNT/FISCAL_PERIOD, all owned here); the one
cross-module read (QR for lookup-code validation, folded into QR-FIN-002/013/015/024/025/
etc.'s "Validations" step, per XM-FIN-001) is a separate REST call, never a SQL join. No
QR joins to resolve a lookup label — every lookup-backed column returns its code; the
frontend resolves the display label via MDL.

---

<!-- PHASE:CORE:START traces=REQ-FIN-017 -->
## PHASE 1 — CORE

**Layers**: controller → service → mapper → domain → repository (`profile.stack.backend.layers`).
Domain-behaviour placement: entity methods for single-entity invariants (e.g.
`JournalEntry.post()`, `FiscalPeriod.hardClose()`); service layer for every multi-entity
or multi-table rule (RULE-FIN-001, 003, 006-012, 014-016 all read beyond one row).

**Error signalling**: `LocalizedException → {code, messageAr, messageEn}`; runtime code
format `FIN-<3-digit>`.

**Transaction scope**: `READ_ONLY` for every `FIND_*`/`EXISTS`/`AGGREGATE` QR; `READ_WRITE`
for every `SAVE`/`UPDATE` QR. The build→validate→post sequence (QR-FIN-024/025 through
QR-FIN-033) runs in ONE transaction per entry — either the whole entry posts, or nothing is
written (no partially-built DRAFT survives a failed validation, per REQ-FIN-015/018-021).

**Search contract**: `{filters, page, size, sort}`, `Page<T>`, empty result = success.

**Audit fields**: `createdBy/createdAt/updatedBy/updatedAt` framework-filled; on
FIN_JOURNAL_ENTRY, `createdBy` records the entry-creator principal used by RULE-FIN-015's
distinct-permission check; `closedBy` on FIN_FISCAL_PERIOD records the period-close
approver principal, from a different principal-permission pair by construction.

**Type mapping** (postgresql16 → Java): identical table to SEC's/MDL's own Phase 1 CORE
(`GENERATED ALWAYS AS IDENTITY`→Long, `VARCHAR(n)`→String, `BOOLEAN`→Boolean,
`TIMESTAMPTZ`→Instant, `TEXT`→String, `DATE`→LocalDate, `NUMERIC(18,4)`→BigDecimal,
bare `NUMERIC` (line/period numbers, sort orders)→Integer, per the same governance note
MDL's plan already stated for its own `sort_order`).

**Lookup values**: all 13 FIN-owned lookup-backed columns are plain `String` holding the
code; validated at the service layer against MDL (XM-FIN-001) before any write — an
invalid code is rejected with a catalog error before it reaches the database.

**Numbering**: `docNo` is generated by the platform numbering engine on `JournalEntry`
create, scoped per `fiscalYearId`, immutable thereafter — excluded entirely from every
create/update request DTO.

**Workflow engine**: forbidden — every lifecycle below (JournalEntry, FiscalPeriod) is a
plain guarded transition, never a workflow definition.

**Languages**: every name field and catalog message present in ar + en.

**Cross-module contract placement**: XM-FIN-001 (SOFT-READ → MDL) is implemented as a
service-layer client (`MdlLookupClient`) calling MDL's `GET /api/v1/mdl/lookups?type=<key>`
(API-MDL-011); FIN's own dependency on SEC for identity/authorization uses the identical
CORE-interceptor mechanism SEC's and MDL's own plans already declare — not redeclared here,
only cited (ADR-FIN-001).

**Cross-cutting authorization**: every secured API below is gated by the platform's CORE
interceptor (module/screen/action grant check) before its controller method runs, exactly
as SEC's own Phase 1 CORE describes; `PERM_FIN_PERIODS_CLOSE_APPROVE` (API-FIN-026/027) is
additionally required to be held by a role distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`
(RULE-FIN-015) — this distinctness check itself runs in FIN's own service layer by reading
the two roles' user sets through SEC's role/grant read APIs, since SEC's interceptor alone
only proves "this caller holds permission X," not "no user holding X also holds Y."
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=REQ-FIN-001,REQ-FIN-010,REQ-FIN-014,REQ-FIN-031 -->
## PHASE 2 — DATA-DOM

Entity count is 14 (≥ threshold) — grouped below under `SUB:DATA-DOM-MASTER` (Account,
FiscalYear, FiscalPeriod — master-like reference data), `SUB:DATA-DOM-TRANSACTIONAL`
(JournalEntry, JournalLine, JournalLineDimension — the posting core), and
`SUB:DATA-DOM-LOOKUP` (Dimension, DimensionValue, EventTypeRule, RuleLine,
RecurringTemplate, RecurringTemplateLine, AllocationRule, AllocationTarget — FIN's own
config/lookup-kind structural data, grouped together here since the engine's three-way
split is by role, not literally the `lookup` kind alone).

<!-- SUB:DATA-DOM-MASTER:START traces=REQ-FIN-001,REQ-FIN-031 -->
### SUB — DATA-DOM-MASTER

#### ENT-FIN-001 — Account      kind: master
BINDINGS: table `FIN_ACCOUNT` · PK `accountPk` (DBF-FIN-001) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none (§3.3 test: no — `code` is client-chosen, not numbering-engine-generated)
FIELDS: DBF-FIN-001..013 — see DB Alignment Manifest; `accountTypeCode`/`natureCode` are
lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request excludes {accountPk, isActiveFl, audit}; update-request
excludes {accountPk, code, isActiveFl, audit} (code immutable, matching MDL's own `key`
precedent); response includes all.
LOOKUP FIELDS: `accountTypeCode`→`ACCOUNT_TYPE`, `natureCode`→`DEBIT_CREDIT`, both via
`GET /api/v1/mdl/lookups?type=<key>` (XM-FIN-001) — stored as code, never a numeric FK.
DOMAIN RULES: **RULE-FIN-001** (full text: srs-fin.md §A5) — Scope ENT-FIN-001 · Trigger:
on update (`isLeafFl`) · DB enforcement: application layer (QR-FIN-006) · owner layer:
service.
STATE MACHINE: `isActiveFl` binary only — not applicable.
CROSS-MODULE: `accountTypeCode`/`natureCode` touch XM-FIN-001.
REPOSITORY OPS → QR-FIN-001, QR-FIN-002, QR-FIN-003, QR-FIN-004, QR-FIN-005, QR-FIN-006.

#### ENT-FIN-007 — FiscalYear      kind: master
BINDINGS: table `FIN_FISCAL_YEAR` · PK `fiscalYearPk` (DBF-FIN-065) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-065..074 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request `{code, startDate, endDate, periodCount}` (periodCount is a
transient input driving REQ-FIN-031's period-generation, not a persisted column); response
includes all persisted fields plus the generated periods.
DOMAIN RULES: none scoped alone (year-end close, REQ-FIN-036, is orchestrated at the API
layer over both FiscalYear and FiscalPeriod — see API-FIN-027).
STATE MACHINE: `statusCode` (FISCAL_YEAR_STATUS) — OPEN→CLOSED, set once by REQ-FIN-036 —
binary, not applicable for a diagram (SRS A7).
CROSS-MODULE: `statusCode` touches XM-FIN-001.
REPOSITORY OPS → QR-FIN-038 (SAVE, with periods), QR-FIN-041 (AGGREGATE, year-end).

#### ENT-FIN-008 — FiscalPeriod      kind: master
BINDINGS: table `FIN_FISCAL_PERIOD` · PK `fiscalPeriodPk` (DBF-FIN-075) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-075..088 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: no direct create (generated with the year, REQ-FIN-031); transition
endpoints only (open/soft-close/hard-close) take just `{id}`; response includes all.
DOMAIN RULES:
**RULE-FIN-008** (srs-fin.md §A5) — period-open-at-post-time — DB enforcement: application
layer (QR-FIN-031) · owner layer: service.
**RULE-FIN-014** (srs-fin.md §A5) — reject reopening a Hard Closed period — DB enforcement:
application layer (QR-FIN-040) · owner layer: service.
**RULE-FIN-015** (srs-fin.md §A5) — close-approval permission distinct from entry-creation
permission — DB enforcement: application layer (service, reading SEC role/grant data,
Phase 1 CORE) · owner layer: service.
STATE MACHINE: `statusCode` (PERIOD_STATE) per SRS A7 — OPEN⇄SOFT_CLOSE→HARD_CLOSE→YEAR_END_CLOSE.
CROSS-MODULE: `statusCode` touches XM-FIN-001; the SoD check (RULE-FIN-015) reads SEC role
data (not a formal XM row — platform-standard integration, ADR-FIN-001).
REPOSITORY OPS → QR-FIN-038 (SAVE, with year), QR-FIN-039 (UPDATE, transitions), QR-FIN-040 (EXISTS).
<!-- SUB:DATA-DOM-MASTER:END -->

<!-- SUB:DATA-DOM-TRANSACTIONAL:START traces=REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028 -->
### SUB — DATA-DOM-TRANSACTIONAL

#### ENT-FIN-004 — JournalEntry      kind: transactional
BINDINGS: table `FIN_JOURNAL_ENTRY` · PK `journalEntryPk` (DBF-FIN-034) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: **docNo** · column `doc_no` (DBF-FIN-035) · format: platform numbering
engine, scoped per `fiscalYearId` (`UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO`) · generation source:
the numbering engine, invoked at create, before the first save — excluded from every
create/update request body, always present in responses.
FIELDS: DBF-FIN-034..050 — see DB Alignment Manifest; `journalTypeCode`/`statusCode`
lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: manual-create request `{docDate, fiscalYearId, periodId, descriptionAr,
descriptionEn, lines: [...]}`; event-build request = the canonical event payload (opaque
to this DTO description — shape owned by the out-of-scope Event consumer, POL-FIN-020);
no update endpoint exists once POSTED (RULE-FIN-016); response includes all fields
including nested lines.
LOOKUP FIELDS: `journalTypeCode`→`JOURNAL_TYPE`, `statusCode`→`JOURNAL_STATUS`, both via
XM-FIN-001.
DOMAIN RULES:
**RULE-FIN-004** — duplicate eventReference rejected — QR-FIN-026 — service.
**RULE-FIN-005** — no active rule for event type — QR-FIN-027 — service.
**RULE-FIN-006** — debit=credit invariant — QR-FIN-029 — service (POL-FIN-001).
**RULE-FIN-008** — period open at post — QR-FIN-031 — service (POL-FIN-004).
**RULE-FIN-011** — reversal exact and linked — QR-FIN-034 — service (POL-FIN-007).
**RULE-FIN-012** — reversal posts to current period if original's closed — QR-FIN-036 — service.
**RULE-FIN-013** — reject reverse of non-POSTED — QR-FIN-035 — service.
**RULE-FIN-016** — lock after posting — enforced by omission (no UPDATE/DELETE mapping on
a POSTED row in the repository layer at all) — service/repository.
(Full text of every RULE above: srs-fin.md §A5 — not restated here per the single-source rule.)
STATE MACHINE: `statusCode` (JOURNAL_STATUS) per SRS A7 — DRAFT→POSTED (RULE-FIN-016 locks
immediately)→VOID (via reversal, RULE-FIN-011).
CROSS-MODULE: `journalTypeCode`/`statusCode` touch XM-FIN-001.
REPOSITORY OPS → QR-FIN-023 through QR-FIN-037 (the full posting pipeline + reversal + read).

#### ENT-FIN-005 — JournalLine      kind: transactional
BINDINGS: table `FIN_JOURNAL_LINE` · PK `journalLinePk` (DBF-FIN-051) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-051..060 — see DB Alignment Manifest; `directionCode` lookup-backed
(XM-FIN-001); `amount` DB-CHECK'd positive (`CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE`, POL-FIN-005).
DTO MEMBERSHIP: written only as a nested array inside the entry create/build request; no
standalone line endpoint; never independently updated (locked with its header).
DOMAIN RULES: **RULE-FIN-007** (leaf/active account) — QR-FIN-030 — service;
**RULE-FIN-010** (remainder-line rounding) — QR-FIN-028 — service.
CROSS-MODULE: `directionCode` touches XM-FIN-001.
REPOSITORY OPS → written as part of QR-FIN-024/025/034 (SAVE, header+lines in one
transaction); read via QR-FIN-037, QR-FIN-042 (ledger), QR-FIN-043 (statements).

#### ENT-FIN-006 — JournalLineDimension      kind: transactional
BINDINGS: table `FIN_JOURNAL_LINE_DIM` · PK `journalLineDimensionPk` (DBF-FIN-061) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-061..064 — see DB Alignment Manifest.
DTO MEMBERSHIP: nested under each line in the entry create/build request (0..N per line).
DOMAIN RULES: **RULE-FIN-009** (dimension value validity) — QR-FIN-032 — service.
CROSS-MODULE: none.
REPOSITORY OPS → written as part of QR-FIN-024/025/034; read via QR-FIN-044 (dimension report).
<!-- SUB:DATA-DOM-TRANSACTIONAL:END -->

<!-- SUB:DATA-DOM-LOOKUP:START traces=REQ-FIN-004,REQ-FIN-007,REQ-FIN-022,REQ-FIN-025 -->
### SUB — DATA-DOM-LOOKUP (FIN's own config/lookup-kind structural data)

#### ENT-FIN-002 — Dimension      kind: config
BINDINGS: table `FIN_DIMENSION` · PK `dimensionPk` (DBF-FIN-014) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-014..022. DTO: create `{code, nameAr, nameEn}`; no update endpoint (name
edits go through a future v2 if needed — not named in the plan, so not built). DOMAIN
RULES: none scoped alone. REPOSITORY OPS → QR-FIN-007, QR-FIN-008.

#### ENT-FIN-003 — DimensionValue      kind: lookup
BINDINGS: table `FIN_DIMENSION_VALUE` · PK `dimensionValuePk` (DBF-FIN-023) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-023..033 — matches `profile.conventions.entity_defaults.lookup` exactly
(code, nameAr, nameEn, sortOrder, isActiveFl) plus PK/FK/audit. DOMAIN RULES:
**RULE-FIN-002** (duplicate code within dimension) — QR-FIN-010 — service + DB
(`UQ_FIN_DIMENSION_VALUE_DIM_CODE`). REPOSITORY OPS → QR-FIN-009, QR-FIN-010, QR-FIN-011.

#### ENT-FIN-009 — EventTypeRule      kind: config
BINDINGS: table `FIN_EVENT_TYPE_RULE` · PK `eventTypeRulePk` (DBF-FIN-089) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-089..097; `eventTypeCode` lookup-backed (XM-FIN-001). DOMAIN RULES: one
active rule per event type — DB (`UQ_FIN_EVENT_TYPE_RULE_CODE`) + QR-FIN-014. REPOSITORY
OPS → QR-FIN-012, QR-FIN-013, QR-FIN-014, QR-FIN-027 (reused at post time).

#### ENT-FIN-010 — RuleLine      kind: config
BINDINGS: table `FIN_RULE_LINE` · PK `ruleLinePk` (DBF-FIN-098) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-098..108; `accountDerivationTypeCode`/`amountSourceTypeCode`/
`directionCode`/`distributionTypeCode` all lookup-backed (XM-FIN-001). DOMAIN RULES:
**RULE-FIN-003** (exactly one remainder line under percentage distribution) — QR-FIN-016 —
service. REPOSITORY OPS → QR-FIN-015, QR-FIN-016; read as part of QR-FIN-025/028 at
event-entry build time.

#### ENT-FIN-011 — RecurringTemplate      kind: config
BINDINGS: table `FIN_RECURRING_TEMPLATE` · PK `recurringTemplatePk` (DBF-FIN-109) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-109..121; `scheduleTypeCode`/`frequencyCode` lookup-backed (XM-FIN-001).
DOMAIN RULES: none scoped alone (its run posts through the same shared pipeline as any
entry — RULE-FIN-006 through RULE-FIN-010, cited on API-FIN-014). REPOSITORY OPS →
QR-FIN-017, QR-FIN-018, QR-FIN-019.

#### ENT-FIN-012 — RecurringTemplateLine      kind: config
BINDINGS: table `FIN_RECURRING_TEMPLATE_LINE` · PK `recurringTemplateLinePk` (DBF-FIN-122) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-122..129; `directionCode` lookup-backed (XM-FIN-001); `amount` DB-CHECK'd
positive. DOMAIN RULES: none scoped alone. REPOSITORY OPS → written with QR-FIN-018; read
by QR-FIN-019 at run time.

#### ENT-FIN-013 — AllocationRule      kind: config
BINDINGS: table `FIN_ALLOCATION_RULE` · PK `allocationRulePk` (DBF-FIN-130) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-130..138. DOMAIN RULES: none scoped alone. REPOSITORY OPS → QR-FIN-020,
QR-FIN-021, QR-FIN-022.

#### ENT-FIN-014 — AllocationTarget      kind: config
BINDINGS: table `FIN_ALLOCATION_TARGET` · PK `allocationTargetPk` (DBF-FIN-139) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-139..146; `distributionTypeCode` lookup-backed (XM-FIN-001). DOMAIN RULES:
**RULE-FIN-003** (reused — exactly one remainder target under percentage distribution) —
QR-FIN-016 (reused) — service. REPOSITORY OPS → written with QR-FIN-021; read by
QR-FIN-022 at run time.
<!-- SUB:DATA-DOM-LOOKUP:END -->
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-FIN-001,REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028,REQ-FIN-036 -->
## PHASE 3 — SVC-API

API count = 32 ≥ 8 → split by threshold, grouped CRUD / SEARCH / INT.

<!-- SUB:SVC-API-SEARCH:START traces=REQ-FIN-001,REQ-FIN-004,REQ-FIN-007,REQ-FIN-022,REQ-FIN-027,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043 -->
### SUB — SVC-API-SEARCH (read-only)

<!-- API:API-FIN-001:START traces=REQ-FIN-001,DBF-FIN-002,DBF-FIN-003,DBF-FIN-004,DBF-FIN-005 -->
### API-FIN-001 — search accounts
Endpoint: GET /api/v1/fin/accounts · Layers: `AccountController.search`→`AccountService.search`
Request: `code`(LIKE), `nameAr/nameEn`(LIKE), `accountTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AccountResponse>` · `ApiResponse<...>`
Validations: none (read-only) · Errors: `FIN-500`
Orchestration: load (QR-FIN-001) → map → return · Repository: QR-FIN-001 · join NONE · READ_ONLY
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_VIEW` · Localization: nameAr/nameEn returned
<!-- API:API-FIN-001:END -->

<!-- API:API-FIN-005:START traces=REQ-FIN-004,DBF-FIN-015,DBF-FIN-016,DBF-FIN-017 -->
### API-FIN-005 — search dimensions
Endpoint: GET /api/v1/fin/dimensions · Layers: `DimensionController.search`→`DimensionService.search`
Request: `code`(LIKE), paging · Response: 200 · `Page<DimensionResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-007 → map → return · Repository: QR-FIN-007 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-005:END -->

<!-- API:API-FIN-008:START traces=REQ-FIN-005,DBF-FIN-024,DBF-FIN-025,DBF-FIN-026,DBF-FIN-027 -->
### API-FIN-008 — search dimension values
Endpoint: GET /api/v1/fin/dimensions/{id}/values · Layers: `DimensionValueController.search`→`DimensionValueService.search`
Request: path `id`; `code`(LIKE), paging · Response: 200 · `Page<DimensionValueResponse>`
Validations: none · Errors: `FIN-404-DIMENSION`
Orchestration: QR-FIN-011 → map → return · Repository: QR-FIN-011 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-008:END -->

<!-- API:API-FIN-009:START traces=REQ-FIN-007,DBF-FIN-090,DBF-FIN-091,DBF-FIN-092 -->
### API-FIN-009 — search event-type rules
Endpoint: GET /api/v1/fin/event-rules · Layers: `EventTypeRuleController.search`→`EventTypeRuleService.search`
Request: `eventTypeCode`(EXACT), `isActiveFl`(EXACT), paging · Response: 200 · `Page<EventTypeRuleResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-012 → map → return · Repository: QR-FIN-012 · join NONE · READ_ONLY
Security: screen FIN_RULES · `PERM_FIN_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-009:END -->

<!-- API:API-FIN-012:START traces=REQ-FIN-022,DBF-FIN-110,DBF-FIN-111,DBF-FIN-112 -->
### API-FIN-012 — search templates
Endpoint: GET /api/v1/fin/recurring-templates · Layers: `RecurringTemplateController.search`→`RecurringTemplateService.search`
Request: `nameAr/nameEn`(LIKE), `scheduleTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<RecurringTemplateResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-017 → map → return · Repository: QR-FIN-017 · join NONE · READ_ONLY
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-012:END -->

<!-- API:API-FIN-015:START traces=REQ-FIN-025,DBF-FIN-131,DBF-FIN-132,DBF-FIN-133 -->
### API-FIN-015 — search allocation rules
Endpoint: GET /api/v1/fin/allocation-rules · Layers: `AllocationRuleController.search`→`AllocationRuleService.search`
Request: `nameAr/nameEn`(LIKE), `sourceAccountId`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AllocationRuleResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-020 → map → return · Repository: QR-FIN-020 · join NONE · READ_ONLY
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-015:END -->

<!-- API:API-FIN-018:START traces=REQ-FIN-027,DBF-FIN-035,DBF-FIN-036,DBF-FIN-040 -->
### API-FIN-018 — search journal entries
Endpoint: GET /api/v1/fin/journal-entries · Layers: `JournalEntryController.search`→`JournalEntryService.search`
Request: `docNo`(LIKE), `docDate`(DATE_RANGE), `periodId`(EXACT), `statusCode`(EXACT), `journalTypeCode`(EXACT), paging
Response: 200 · `Page<JournalEntryResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-023 → map → return (REQ-FIN-027: unmodified) · Repository: QR-FIN-023 · join NONE · READ_ONLY
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_VIEW` · Localization: descriptionAr/En
<!-- API:API-FIN-018:END -->

<!-- API:API-FIN-022:START traces=REQ-FIN-016,REQ-FIN-027,DBF-FIN-034,DBF-FIN-041 -->
### API-FIN-022 — read entry
Endpoint: GET /api/v1/fin/journal-entries/{id} · Layers: `JournalEntryController.read`→`JournalEntryService.read`
Request: path `id` · Response: 200 · `JournalEntryResponse` with nested lines and their dimensions
Validations: none · Errors: `FIN-404-ENTRY`
Orchestration: QR-FIN-037 → map → return · Repository: QR-FIN-037 · join intra-module (entry→line→line-dim) · READ_ONLY
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_VIEW` · Localization: descriptionAr/En
<!-- API:API-FIN-022:END -->

<!-- API:API-FIN-028:START traces=REQ-FIN-039,REQ-FIN-046,DBF-FIN-054,DBF-FIN-055,DBF-FIN-056 -->
### API-FIN-028 — account ledger
Endpoint: GET /api/v1/fin/reports/account-ledger · Layers: `ReportController.accountLedger`→`ReportService.accountLedger`
Request: `accountId`(EXACT), date range, dimension filters · Response: 200 · running-balance list, each row linking journalEntryId
Validations: none · Errors: `FIN-404-ACCOUNT`
Orchestration: QR-FIN-042 (POSTED lines only, live) → compute running balance → return (POL-FIN-009)
Repository: QR-FIN-042 · join intra-module (line→entry for docDate/status) · READ_ONLY
Security: screen FIN_ACCOUNT_LEDGER · `PERM_FIN_ACCOUNT_LEDGER_VIEW` · Localization: n/a
<!-- API:API-FIN-028:END -->

<!-- API:API-FIN-029:START traces=REQ-FIN-040,REQ-FIN-046,DBF-FIN-005,DBF-FIN-006,DBF-FIN-055 -->
### API-FIN-029 — trial balance
Endpoint: GET /api/v1/fin/reports/trial-balance · Layers: `ReportController.trialBalance`→`ReportService.trialBalance`
Request: `periodId`(EXACT), `accountTypeCode`(EXACT) · Response: 200 · one row per account (debit/credit balance, sign per natureCode — POL-FIN-002)
Validations: RULE-FIN-006 restated as a report-level guarantee (POL-FIN-008: the sums always match because every contributing entry individually balanced — no separate check needed, an invariant by construction)
Errors: `FIN-500`
Orchestration: QR-FIN-043 (POSTED lines only, live, grouped by account) → apply nature sign → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_TRIAL_BALANCE · `PERM_FIN_TRIAL_BALANCE_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-029:END -->

<!-- API:API-FIN-030:START traces=REQ-FIN-041,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-030 — balance sheet
Endpoint: GET /api/v1/fin/reports/balance-sheet · Layers: `ReportController.balanceSheet`→`ReportService.balanceSheet`
Request: `fiscalYearId`(EXACT), `asOfDate` · Response: 200 · grouped ASSET/LIABILITY/EQUITY balances
Validations: none (continuity itself is guaranteed by REQ-FIN-036's opening-entry generation, not re-validated at read time)
Errors: `FIN-500`
Orchestration: QR-FIN-043 (accountTypeCode IN ASSET,LIABILITY,EQUITY) → group → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_BALANCE_SHEET · `PERM_FIN_BALANCE_SHEET_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-030:END -->

<!-- API:API-FIN-031:START traces=REQ-FIN-042,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-031 — income statement
Endpoint: GET /api/v1/fin/reports/income-statement · Layers: `ReportController.incomeStatement`→`ReportService.incomeStatement`
Request: `fiscalYearId`(EXACT), period range · Response: 200 · grouped REVENUE/EXPENSE balances
Validations: none (zero-opening is guaranteed by REQ-FIN-036 closing result accounts to Retained Earnings, not re-validated at read time)
Errors: `FIN-500`
Orchestration: QR-FIN-043 (accountTypeCode IN REVENUE,EXPENSE, scoped to the year/period range) → group → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_INCOME_STATEMENT · `PERM_FIN_INCOME_STATEMENT_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-031:END -->

<!-- API:API-FIN-032:START traces=REQ-FIN-043,DBF-FIN-063,DBF-FIN-064,DBF-FIN-055 -->
### API-FIN-032 — dimension report
Endpoint: GET /api/v1/fin/reports/dimension · Layers: `ReportController.dimensionReport`→`ReportService.dimensionReport`
Request: `dimensionId`(EXACT), `dimensionValueId`(EXACT), `periodId`(EXACT) · Response: 200 · one row per account+dimension-value combination (POL-FIN-011)
Validations: none · Errors: `FIN-404-DIMENSION`
Orchestration: QR-FIN-044 (group by account + dimension value, never base account alone) → return
Repository: QR-FIN-044 · join intra-module (line→line-dim→dimension-value) · READ_ONLY
Security: screen FIN_DIMENSION_REPORTS · `PERM_FIN_DIMENSION_REPORTS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-032:END -->
<!-- SUB:SVC-API-SEARCH:END -->

<!-- SUB:SVC-API-CRUD:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,REQ-FIN-014,REQ-FIN-022,REQ-FIN-025 -->
### SUB — SVC-API-CRUD

<!-- API:API-FIN-002:START traces=REQ-FIN-001,REQ-FIN-002,DBF-FIN-002,DBF-FIN-005,DBF-FIN-006,DBF-FIN-007,DBF-FIN-008 -->
### API-FIN-002 — create account
Endpoint: POST /api/v1/fin/accounts · Layers: `AccountController.create`→`AccountService.create`
Request: `{code, nameAr, nameEn, accountTypeCode, natureCode, parentAccountId?, isLeafFl}`
Response: 201 · `AccountResponse`
Validations: RULE-FIN-001 (leaf requires no children — only relevant if `parentAccountId`
is later given children; at create this only matters when the same call sets a parent
that itself must remain non-leaf — QR-FIN-006 checks the *parent*, not the new row);
uniqueness of code (QR-FIN-005); accountTypeCode/natureCode validated via XM-FIN-001
Errors: `FIN-409-ACCOUNT-DUP`, `FIN-409-PARENT-NOT-LEAF-ELIGIBLE`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookups (XM-FIN-001) → validate uniqueness (QR-FIN-005) → if
parentAccountId given, flip the parent's isLeafFl to false via RULE-FIN-001's inverse
effect (a parent gaining its first child can no longer itself be a leaf) → persist (QR-FIN-002) → return
Repository: QR-FIN-002, QR-FIN-005, QR-FIN-006 · join NONE · READ_WRITE
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-002:END -->

<!-- API:API-FIN-003:START traces=REQ-FIN-002,DBF-FIN-003,DBF-FIN-004,DBF-FIN-008 -->
### API-FIN-003 — update account
Endpoint: PUT /api/v1/fin/accounts/{id} · Layers: `AccountController.update`→`AccountService.update`
Request: `{nameAr, nameEn, isLeafFl}` — excludes {accountPk, code, accountTypeCode, natureCode, isActiveFl, audit}
Response: 200 · `AccountResponse`
Validations: RULE-FIN-002-equivalent — RULE-FIN-001 (full text: DATA-DOM §ENT-FIN-001) —
`isLeafFl=true` rejected if the account has any child (QR-FIN-006)
Errors: `FIN-409-HAS-CHILDREN`, `FIN-404-ACCOUNT`
Orchestration: load → check RULE-FIN-001 if isLeafFl changing to true (QR-FIN-006) → update (QR-FIN-003) → return
Repository: QR-FIN-003, QR-FIN-006 · join NONE · READ_WRITE
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_UPDATE` · Localization: both name fields updatable
<!-- API:API-FIN-003:END -->

<!-- API:API-FIN-004:START traces=REQ-FIN-003,DBF-FIN-009 -->
### API-FIN-004 — deactivate account
Endpoint: DELETE /api/v1/fin/accounts/{id} · Layers: `AccountController.deactivate`→`AccountService.deactivate`
Request: path `id` · Response: 200 · confirmation `{accountPk, isActiveFl: false}`
Validations: none beyond existence · Errors: `FIN-404-ACCOUNT`
Orchestration: load → `Account.deactivate()` → persist (QR-FIN-004) → return (REQ-FIN-019
subsequently rejects any posting to it)
Repository: QR-FIN-004 · join NONE · READ_WRITE
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_UPDATE` · Localization: n/a
<!-- API:API-FIN-004:END -->

<!-- API:API-FIN-006:START traces=REQ-FIN-004,DBF-FIN-015,DBF-FIN-016,DBF-FIN-017 -->
### API-FIN-006 — create dimension
Endpoint: POST /api/v1/fin/dimensions · Layers: `DimensionController.create`→`DimensionService.create`
Request: `{code, nameAr, nameEn}` · Response: 201 · `DimensionResponse`
Validations: uniqueness of code (DB `UQ_FIN_DIMENSION_CODE`, checked friendly at service layer)
Errors: `FIN-409-DIMENSION-DUP`
Orchestration: validate → persist (QR-FIN-008) → return · Repository: QR-FIN-008 · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-006:END -->

<!-- API:API-FIN-007:START traces=REQ-FIN-005,REQ-FIN-006,DBF-FIN-024,DBF-FIN-025,DBF-FIN-028 -->
### API-FIN-007 — create dimension value
Endpoint: POST /api/v1/fin/dimensions/{id}/values · Layers: `DimensionValueController.create`→`DimensionValueService.create`
Request: path `id` (dimensionId); body `{code, nameAr, nameEn, sortOrder}`
Response: 201 · `DimensionValueResponse`
Validations: RULE-FIN-002 (full text: DATA-DOM §ENT-FIN-003) — code unique within the
dimension (QR-FIN-010)
Errors: `FIN-409-DIMVALUE-DUP`, `FIN-404-DIMENSION`
Orchestration: validate dimension exists → check RULE-FIN-002 (QR-FIN-010) → persist (QR-FIN-009) → return
Repository: QR-FIN-009, QR-FIN-010 · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-007:END -->

<!-- API:API-FIN-010:START traces=REQ-FIN-007,REQ-FIN-044,REQ-FIN-045,DBF-FIN-090,DBF-FIN-091,DBF-FIN-092 -->
### API-FIN-010 — create event-type rule
Endpoint: POST /api/v1/fin/event-rules · Layers: `EventTypeRuleController.create`→`EventTypeRuleService.create`
Request: `{eventTypeCode, nameAr, nameEn}` · Response: 201 · `EventTypeRuleResponse`
Validations: eventTypeCode validated via XM-FIN-001; uniqueness of one-active-rule-per-type (QR-FIN-014)
Errors: `FIN-409-RULE-DUP`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookup → check uniqueness (QR-FIN-014) → persist (QR-FIN-013) → return
Repository: QR-FIN-013, QR-FIN-014 · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_CREATE` · Localization: nameAr/nameEn required
Precondition: this endpoint is only reachable once FIN's onboarding has completed —
FIN registered as a module with its screens/actions into SEC (REQ-FIN-044) and FIN's 13
lookup types, including ACCOUNTING_EVENT_TYPE, registered into MDL (REQ-FIN-045); both run
once at deployment, not per request.
<!-- API:API-FIN-010:END -->

<!-- API:API-FIN-011:START traces=REQ-FIN-008,REQ-FIN-009,DBF-FIN-101,DBF-FIN-103,DBF-FIN-105,DBF-FIN-106,DBF-FIN-107 -->
### API-FIN-011 — add rule line
Endpoint: POST /api/v1/fin/event-rules/{id}/lines · Layers: `RuleLineController.create`→`RuleLineService.create`
Request: path `id` (eventTypeRuleId); body `{accountDerivationTypeCode, accountDerivationValue,
amountSourceTypeCode, amountSourceValue?, directionCode, distributionTypeCode, isRemainderFl}`
Response: 201 · `RuleLineResponse`
Validations: RULE-FIN-003 (full text: DATA-DOM §ENT-FIN-010) — exactly one remainder line
once any sibling line is PERCENTAGE-distributed (QR-FIN-016); all four lookup codes
validated via XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-404-RULE`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookups → check RULE-FIN-003 across the rule's existing + new line
(QR-FIN-016) → persist (QR-FIN-015) → return
Repository: QR-FIN-015, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-011:END -->

<!-- API:API-FIN-013:START traces=REQ-FIN-022,DBF-FIN-112,DBF-FIN-113,DBF-FIN-114,DBF-FIN-115 -->
### API-FIN-013 — create template
Endpoint: POST /api/v1/fin/recurring-templates · Layers: `RecurringTemplateController.create`→`RecurringTemplateService.create`
Request: `{nameAr, nameEn, scheduleTypeCode, frequencyCode?, startDate, endDate?, lines: [...]}`
Response: 201 · `RecurringTemplateResponse`
Validations: scheduleTypeCode/frequencyCode/line directionCode validated via XM-FIN-001;
frequencyCode required unless scheduleTypeCode=REVERSING
Errors: `FIN-400-MISSING-FREQUENCY`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate → set nextRunDate=startDate → persist template+lines (QR-FIN-018) → return
Repository: QR-FIN-018 · join NONE · READ_WRITE
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-013:END -->

<!-- API:API-FIN-016:START traces=REQ-FIN-025,DBF-FIN-133,DBF-FIN-142,DBF-FIN-144 -->
### API-FIN-016 — create allocation rule
Endpoint: POST /api/v1/fin/allocation-rules · Layers: `AllocationRuleController.create`→`AllocationRuleService.create`
Request: `{nameAr, nameEn, sourceAccountId, targets: [...]}`
Response: 201 · `AllocationRuleResponse`
Validations: RULE-FIN-003 (reused) — exactly one remainder target when any sibling is
PERCENTAGE (QR-FIN-016, reused); distributionTypeCode validated via XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-404-ACCOUNT`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate → check RULE-FIN-003 across targets (QR-FIN-016) → persist rule+targets (QR-FIN-021) → return
Repository: QR-FIN-021, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-016:END -->

<!-- API:API-FIN-019:START traces=REQ-FIN-014,REQ-FIN-015,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,DBF-FIN-036,DBF-FIN-037,DBF-FIN-038,DBF-FIN-044 -->
### API-FIN-019 — create manual entry
Endpoint: POST /api/v1/fin/journal-entries · Layers: `JournalEntryController.createManual`→`JournalEntryService.createManual`
Request: `{docDate, fiscalYearId, periodId, journalTypeCode="MANUAL", descriptionAr,
descriptionEn, lines: [{accountId, amount, directionCode, descriptionAr?, descriptionEn?,
dimensions: [{dimensionId, dimensionValueId}]}]}` — excludes {journalEntryPk, docNo,
statusCode, postedAt, audit}
Response: 201 · `JournalEntryResponse` (statusCode=POSTED on success)
Validations: RULE-FIN-006 (debit=credit, QR-FIN-029), RULE-FIN-007 (leaf/active accounts,
QR-FIN-030), RULE-FIN-008 (period open, QR-FIN-031), RULE-FIN-009 (dimension valid,
QR-FIN-032) — every failure returned together (REQ-FIN-015), nothing posts if any fails
Errors: `FIN-409-UNBALANCED`, `FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`,
`FIN-409-INVALID-DIMENSION`
Orchestration: generate docNo (numbering engine) → build DRAFT (QR-FIN-024) → validate
(QR-FIN-029..032) → on success: post (QR-FIN-033); on failure: discard the whole attempt
(one transaction, REQ-FIN-015) → return
Repository: QR-FIN-024, QR-FIN-029, QR-FIN-030, QR-FIN-031, QR-FIN-032, QR-FIN-033 · join
NONE · READ_WRITE (one transaction, build-through-post)
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_CREATE` · Localization: descriptionAr/En
<!-- API:API-FIN-019:END -->
<!-- SUB:SVC-API-CRUD:END -->

<!-- SUB:SVC-API-INT:START traces=REQ-FIN-010,REQ-FIN-023,REQ-FIN-024,REQ-FIN-026,REQ-FIN-028,REQ-FIN-031,REQ-FIN-034,REQ-FIN-036,REQ-FIN-037 -->
### SUB — SVC-API-INT (posting-pipeline orchestration and period-control actions)

<!-- API:API-FIN-020:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,DBF-FIN-041,DBF-FIN-090,DBF-FIN-106,DBF-FIN-107 -->
### API-FIN-020 — build event entry (system)
Endpoint: POST /api/v1/fin/journal-entries/from-event · Layers: `EventEntryController.build`→`EventEntryService.build`
Request: the canonical accounting event payload (opaque shape, out-of-scope Event consumer, POL-FIN-020)
Response: 201 · `JournalEntryResponse` (statusCode=POSTED) — or a rejection recorded for operator follow-up (REQ-FIN-013)
Validations: RULE-FIN-004 (duplicate eventReference, QR-FIN-026), RULE-FIN-005 (active
rule exists, QR-FIN-027), RULE-FIN-010 (remainder-line rounding, QR-FIN-028), then the
same RULE-FIN-006/007/008/009 checks as API-FIN-019 (QR-FIN-029..032)
Errors: `FIN-409-DUPLICATE-EVENT`, `FIN-404-NO-ACTIVE-RULE`, `FIN-409-UNBALANCED`,
`FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`, `FIN-409-INVALID-DIMENSION`
Orchestration: check RULE-FIN-004 (QR-FIN-026) → resolve active rule (QR-FIN-027) →
generate docNo → build lines from the rule against the event's fields, computing the
remainder line last (QR-FIN-028, QR-FIN-025) → validate (QR-FIN-029..032) → post (QR-FIN-033) → return
Repository: QR-FIN-025, QR-FIN-026, QR-FIN-027, QR-FIN-028, QR-FIN-029..033 · join NONE ·
READ_WRITE (one transaction, build-through-post)
Security: system-to-system call (the Event consumer's own service principal), gated by
the same interceptor as any authenticated caller · `PERM_FIN_JOURNAL_ENTRIES_CREATE`
Localization: n/a (no free-text description supplied by an event)
<!-- API:API-FIN-020:END -->

<!-- API:API-FIN-014:START traces=REQ-FIN-023,REQ-FIN-024,DBF-FIN-115,DBF-FIN-112 -->
### API-FIN-014 — run template
Endpoint: POST /api/v1/fin/recurring-templates/{id}/run · Layers: `RecurringTemplateController.run`→`RecurringTemplateService.run`
Request: path `id` (or invoked by an internal scheduler with no path — the endpoint is the
same either way) · Response: 201 · `JournalEntryResponse`
Validations: same RULE-FIN-006/007/008/009 checks as API-FIN-019 (the template's own lines
were already balance-checked at API-FIN-013 create time, but re-validated here since
accounts/periods may have changed since)
Errors: same as API-FIN-019
Orchestration: load template (QR-FIN-019) → build entry from its lines (journalTypeCode=
RECURRING) → validate + post (QR-FIN-029..033) → advance nextRunDate per frequencyCode →
if scheduleTypeCode=REVERSING: also build and post the linked reversal in the next period
(REQ-FIN-024, reusing RULE-FIN-011/012 via QR-FIN-034/036) → return
Repository: QR-FIN-019, QR-FIN-024(-style build), QR-FIN-029..033, QR-FIN-034, QR-FIN-036
· join NONE · READ_WRITE
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_UPDATE` (running
a template is modeled as an update-class custom action) · Localization: n/a
<!-- API:API-FIN-014:END -->

<!-- API:API-FIN-017:START traces=REQ-FIN-026,DBF-FIN-133,DBF-FIN-145,DBF-FIN-146 -->
### API-FIN-017 — run allocation rule
Endpoint: POST /api/v1/fin/allocation-rules/{id}/run · Layers: `AllocationRuleController.run`→`AllocationRuleService.run`
Request: path `id` · Response: 201 · `JournalEntryResponse`
Validations: RULE-FIN-010 (remainder guarantee, QR-FIN-028, reused) then RULE-FIN-006/007/008/009
Errors: same family as API-FIN-019, plus `FIN-404-ALLOCATION-RULE`
Orchestration: load rule + targets + current source-account balance (QR-FIN-022) →
distribute per target's distributionTypeCode, remainder target absorbing rounding
(QR-FIN-028) → build entry (journalTypeCode=ALLOCATION) → validate + post (QR-FIN-029..033) → return
Repository: QR-FIN-022, QR-FIN-028, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-017:END -->

<!-- API:API-FIN-021:START traces=REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,DBF-FIN-042,DBF-FIN-043 -->
### API-FIN-021 — reverse entry
Endpoint: POST /api/v1/fin/journal-entries/{id}/reverse · Layers: `JournalEntryController.reverse`→`JournalEntryService.reverse`
Request: path `id` · Response: 201 · `JournalEntryResponse` (the new reversal entry)
Validations: RULE-FIN-013 (must be POSTED, QR-FIN-035); RULE-FIN-012 (period substitution
if original's is closed, QR-FIN-036)
Errors: `FIN-409-NOT-POSTED`, `FIN-404-ENTRY`
Orchestration: load original → check RULE-FIN-013 (QR-FIN-035) → resolve posting period
(original's if Open, else the current open period per RULE-FIN-012, QR-FIN-036) → build
mirrored lines with opposite directions, same amounts (RULE-FIN-011, QR-FIN-034) →
validate + post (QR-FIN-029..033, journalTypeCode=REVERSAL) → set originalEntryId/
reversalEntryId on both rows (bidirectional link) → return
Repository: QR-FIN-034, QR-FIN-035, QR-FIN-036, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_REVERSE` (custom action) · Localization: n/a
<!-- API:API-FIN-021:END -->

<!-- API:API-FIN-023:START traces=REQ-FIN-031,DBF-FIN-066,DBF-FIN-067,DBF-FIN-068,DBF-FIN-077 -->
### API-FIN-023 — create fiscal year
Endpoint: POST /api/v1/fin/fiscal-years · Layers: `FiscalYearController.create`→`FiscalYearService.create`
Request: `{code, startDate, endDate, periodCount}` · Response: 201 · `FiscalYearResponse` with its generated periods
Validations: uniqueness of code
Errors: `FIN-409-YEAR-DUP`
Orchestration: validate → persist year (statusCode=OPEN) + generate periodCount periods,
each statusCode=OPEN (QR-FIN-038) → return
Repository: QR-FIN-038 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CREATE` · Localization: n/a
<!-- API:API-FIN-023:END -->

<!-- API:API-FIN-024:START traces=REQ-FIN-032,DBF-FIN-082 -->
### API-FIN-024 — open period
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/open · Layers: `FiscalPeriodController.open`→`FiscalPeriodService.open`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: current state must be SOFT_CLOSE (§10.2 "re-openable" — Hard Closed is not, RULE-FIN-014)
Errors: `FIN-409-NOT-REOPENABLE`, `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040) → transition (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_UPDATE` · Localization: n/a
<!-- API:API-FIN-024:END -->

<!-- API:API-FIN-025:START traces=REQ-FIN-033,DBF-FIN-082 -->
### API-FIN-025 — soft-close period
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/soft-close · Layers: `FiscalPeriodController.softClose`→`FiscalPeriodService.softClose`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: current state must be OPEN · Errors: `FIN-409-INVALID-TRANSITION`, `FIN-404-PERIOD`
Orchestration: load → transition (QR-FIN-039) → return · Repository: QR-FIN-039 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_UPDATE` · Localization: n/a
<!-- API:API-FIN-025:END -->

<!-- API:API-FIN-026:START traces=REQ-FIN-034,REQ-FIN-035,REQ-FIN-037,REQ-FIN-038,DBF-FIN-082,DBF-FIN-083,DBF-FIN-084 -->
### API-FIN-026 — hard-close period (approval)
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/hard-close · Layers: `FiscalPeriodController.hardClose`→`FiscalPeriodService.hardClose`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: RULE-FIN-014 (not already Hard Closed, QR-FIN-040); RULE-FIN-015 (full text:
DATA-DOM §ENT-FIN-008) — caller must hold `PERM_FIN_PERIODS_CLOSE_APPROVE`, a permission
distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE` (checked by the CORE interceptor plus the
service-layer distinctness read, Phase 1 CORE)
Errors: `FIN-409-NOT-REOPENABLE`(reused message context), `FIN-403-SOD-VIOLATION`, `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040) → check RULE-FIN-015 (SEC role read)
→ transition, set closedBy/closedAt to the approving principal (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` (custom, SoD-gated) · Localization: n/a
<!-- API:API-FIN-026:END -->

<!-- API:API-FIN-027:START traces=REQ-FIN-036,DBF-FIN-069,DBF-FIN-034 -->
### API-FIN-027 — run year-end close
Endpoint: POST /api/v1/fin/fiscal-years/{id}/year-end-close · Layers: `FiscalYearController.yearEndClose`→`FiscalYearService.yearEndClose`
Request: path `id` · Response: 201 · `{closingEntry: JournalEntryResponse, openingEntry: JournalEntryResponse}`
Validations: every period of the year must be HARD_CLOSE (precondition) — `PERM_FIN_PERIODS_CLOSE_APPROVE` required (same SoD gate as API-FIN-026)
Errors: `FIN-409-PERIODS-NOT-CLOSED`, `FIN-404-YEAR`
Orchestration: verify all periods Hard Closed → compute closing balances (QR-FIN-041) →
build + post a closing entry (result accounts → Retained Earnings, journalTypeCode=CLOSING)
→ build + post the next year's opening entry from the resulting balance-sheet balances
(journalTypeCode=OPENING, QR-FIN-041, POL-FIN-010) — CLOSING/OPENING are two values added
to the JOURNAL_TYPE lookup this stage (see Decisions Applied — a data-only, non-breaking
extension, not a new REQ/RULE) → mark FiscalYear statusCode=CLOSED, periods
statusCode=YEAR_END_CLOSE → return
Repository: QR-FIN-041, QR-FIN-029..033 (both generated entries go through the same
validated posting pipeline) · join intra-module · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` · Localization: n/a
<!-- API:API-FIN-027:END -->
<!-- SUB:SVC-API-INT:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-FIN-017 -->
## PHASE 4 — DOC

**API contract summary** (backend self-check only; the frontend stage binds to the real
`api-docs-fin.md` published after implementation): 32 endpoints under `/api/v1/fin`, one
row per API-FIN-001..032 (path/verb/request/response per the API Registry table in the
Plan Index above — not restated a third time here, single-source rule).

**DTO typing constraints**: every lookup-backed field (`accountTypeCode`, `natureCode`,
`directionCode`, `journalTypeCode`, `statusCode`, `eventTypeCode`,
`accountDerivationTypeCode`, `amountSourceTypeCode`, `distributionTypeCode`,
`scheduleTypeCode`, `frequencyCode`) is `String`, never a Java enum; `docNo` never appears
in any create/update request body, always in every response.

**Pagination + filter standard**: identical to SEC's/MDL's own Phase 1 CORE.
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=REQ-FIN-001 -->
## PHASE 5 — INT-C (cross-module consume)

One `XM-*` row (XM-FIN-001), below the split threshold (1 < 5) — no SUB opened.

<!-- XM:XM-FIN-001:START traces=REQ-FIN-001,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-018,REQ-FIN-022,REQ-FIN-025,REQ-FIN-031 -->
### XM-FIN-001 — validate/read lookup-backed codes against MDL
Target        : MDL · ENT-MDL-001/002 (LookupType/LookupValue) · classification SOFT-READ
Interface     : REST call — `GET /api/v1/mdl/lookups?type={key}` (API-MDL-011) for every
one of FIN's 13 owned keys, called at the point each lookup-backed field is written or offered as a select-list
Contract      : data required = the submitted code exists as an active value under the
named type; fallback if absent = reject with `FIN-400-INVALID-LOOKUP`; retry = none
(synchronous, user-facing call — a transient MDL outage surfaces as `FIN-503`); idempotency
= read-only, naturally idempotent
Blocks        : none DEFERRED — MDL v1 is already gated (pass-1 APPROVE); ACTIVE from the
moment FIN v1 is created
<!-- XM:XM-FIN-001:END -->

FIN's dependency on SEC (identity/authorization for every request, and FIN's own
self-registration into SEC) is not a formal `XM` row — ADR-FIN-001 (carried from P2).
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-FIN-001 -->
## PHASE 6 — INT-R (cross-module resolve)

| XM | Status | Workaround (if not READY/ACTIVE) |
|---|---|---|
| XM-FIN-001 | ACTIVE | not applicable — target already gated |

No DEFERRED row exists. FIN is the third and last module of this batch
(GENERATION-INSTRUCTIONS.md §3); the next module to consume FIN (first candidate: PRC or
any future Tier-2/3 module needing accounting integration) is out of this batch's scope —
`XM-INBOUND-STUB-3` names FIN as the eventual target, formal id assigned by that module's
own P2 when it exists.
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=REQ-FIN-038,REQ-FIN-044 -->
## PHASE 7 — SEC-BE (security, backend half)

| Screen (page code) | VIEW | CREATE | UPDATE | DELETE | Custom |
|---|---|---|---|---|---|
| FIN_ACCOUNTS | ✓ (API-FIN-001) | ✓ (API-FIN-002) | ✓ (API-FIN-003) | ✓ deactivate (API-FIN-004) | — |
| FIN_DIMENSIONS | ✓ (API-FIN-005,008) | ✓ (API-FIN-006,007) | — | — | — |
| FIN_RULES | ✓ (API-FIN-009) | ✓ (API-FIN-010) | ✓ (API-FIN-011, add line) | — | — |
| FIN_RECURRING_TEMPLATES | ✓ (API-FIN-012) | ✓ (API-FIN-013) | ✓ (API-FIN-014, run) | — | — |
| FIN_ALLOCATION_RULES | ✓ (API-FIN-015) | ✓ (API-FIN-016) | ✓ (API-FIN-017, run) | — | — |
| FIN_JOURNAL_ENTRIES | ✓ (API-FIN-018,022) | ✓ (API-FIN-019,020) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, API-FIN-021) |
| FIN_PERIODS | ✓ | ✓ (API-FIN-023, year) | ✓ (API-FIN-024,025) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE`, API-FIN-026,027 — RULE-FIN-015 SoD) |
| FIN_ACCOUNT_LEDGER | ✓ (API-FIN-028) | — | — | — | — |
| FIN_TRIAL_BALANCE | ✓ (API-FIN-029) | — | — | — | — |
| FIN_BALANCE_SHEET | ✓ (API-FIN-030) | — | — | — | — |
| FIN_INCOME_STATEMENT | ✓ (API-FIN-031) | — | — | — | — |
| FIN_DIMENSION_REPORTS | ✓ (API-FIN-032) | — | — | — | — |

**Seed data** (REQ-FIN-044): 12 SEC_PAGES rows registered via SEC's screen-registration
endpoint at FIN onboarding; one action row per action above via SEC's action-registration
endpoint, following `PERM_<PAGE_CODE>_<ACTION>` — including the two custom actions
(`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, `PERM_FIN_PERIODS_CLOSE_APPROVE`).

**SoD enforcement (RULE-FIN-015, POL-FIN-016)**: `PERM_FIN_PERIODS_CLOSE_APPROVE` and
`PERM_FIN_JOURNAL_ENTRIES_CREATE` must never be held by the same role by platform
convention (an administrative guideline enforced by role design, not a database
constraint — SEC's RBAC model grants permissions per role, and FIN's service layer
additionally checks at hard-close/year-end-close time that no single *user* holds both,
per role union, Phase 1 CORE).

**Gateway**: every non-VIEW permission requires VIEW on the same screen first (platform
convention, SEC's own interceptor — not restated as a FIN-owned RULE).

**Forbidden responses**: `FIN-403-FORBIDDEN` / `FIN-403-SOD-VIOLATION` map through the
same `LocalizedException` envelope as every other module.
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-FIN-017 -->
## PHASE 8 — ALIGN-BE

See Alignment self-check (ALIGN) below.
<!-- PHASE:ALIGN-BE:END -->

## Error Catalog — FIN v1

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `FIN-<3-digit>`.

| code | RULE / PLATFORM-STD | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| FIN-409-ACCOUNT-DUP | PLATFORM-STD | API-FIN-002 | 409 | duplicate account code | رمز الحساب مستخدم بالفعل | Account code already in use |
| FIN-409-PARENT-NOT-LEAF-ELIGIBLE | RULE-FIN-001 | API-FIN-002 | 409 | parent account cannot remain a leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-400-INVALID-LOOKUP | PLATFORM-STD (XM-FIN-001) | many | 400 | submitted code not found in MDL | القيمة المُدخلة غير صالحة | The submitted value is not valid |
| FIN-409-HAS-CHILDREN | RULE-FIN-001 | API-FIN-003 | 409 | marking a parent as leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-404-ACCOUNT | PLATFORM-STD | API-FIN-003, 004, 028 | 404 | unknown account id | الحساب غير موجود | Account not found |
| FIN-409-DIMENSION-DUP | PLATFORM-STD | API-FIN-006 | 409 | duplicate dimension code | رمز البُعد مستخدم بالفعل | Dimension code already in use |
| FIN-409-DIMVALUE-DUP | RULE-FIN-002 | API-FIN-007 | 409 | duplicate code within dimension | هذا الرمز مستخدم بالفعل ضمن هذا البُعد | This code is already used within this dimension |
| FIN-404-DIMENSION | PLATFORM-STD | API-FIN-007, 008, 032 | 404 | unknown dimension id | البُعد غير موجود | Dimension not found |
| FIN-409-RULE-DUP | PLATFORM-STD (§6.4) | API-FIN-010 | 409 | event type already has an active rule | يوجد بالفعل قاعدة نشطة لهذا النوع | An active rule already exists for this event type |
| FIN-409-REMAINDER-COUNT | RULE-FIN-003 | API-FIN-011, 016 | 409 | wrong remainder-line/target count | يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي | Exactly one remainder line is required when any percentage distribution is present |
| FIN-404-RULE | PLATFORM-STD | API-FIN-011 | 404 | unknown event-type rule id | القاعدة غير موجودة | Rule not found |
| FIN-400-MISSING-FREQUENCY | PLATFORM-STD | API-FIN-013 | 400 | recurring template with no frequency | يلزم تحديد التكرار للقالب المتكرر | A frequency is required for a recurring template |
| FIN-404-ALLOCATION-RULE | PLATFORM-STD | API-FIN-017 | 404 | unknown allocation rule id | قاعدة التوزيع غير موجودة | Allocation rule not found |
| FIN-409-UNBALANCED | RULE-FIN-006 | API-FIN-019, 020, 014, 017 | 409 | debits ≠ credits | القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن | The entry is unbalanced — total debits do not equal total credits |
| FIN-409-NOT-POSTABLE-ACCOUNT | RULE-FIN-007 | API-FIN-019, 020, 014, 017 | 409 | non-leaf/inactive account | الحساب المستهدف لا يقبل ترحيلاً مباشرًا | The target account does not accept direct posting |
| FIN-409-PERIOD-NOT-OPEN | RULE-FIN-008 | API-FIN-019, 020, 014, 017 | 409 | period not Open at post | الفترة المستهدفة غير مفتوحة | The target period is not open |
| FIN-409-INVALID-DIMENSION | RULE-FIN-009 | API-FIN-019, 020, 014, 017 | 409 | invalid/inactive dimension value | قيمة البُعد غير صالحة | The dimension value is invalid |
| FIN-409-DUPLICATE-EVENT | RULE-FIN-004 | API-FIN-020 | 409 | repeated eventReference | تم بالفعل ترحيل قيد لهذا المرجع | An entry for this event reference has already been posted |
| FIN-404-NO-ACTIVE-RULE | RULE-FIN-005 | API-FIN-020 | 404 | no active rule for event type | لا توجد قاعدة نشطة لهذا النوع من الأحداث | No active rule exists for this event type |
| FIN-409-NOT-POSTED | RULE-FIN-013 | API-FIN-021 | 409 | reversing a non-posted entry | لا يمكن عكس قيد غير مُرحَّل | A non-posted entry cannot be reversed |
| FIN-404-ENTRY | PLATFORM-STD | API-FIN-021, 022 | 404 | unknown entry id | القيد غير موجود | Entry not found |
| FIN-409-YEAR-DUP | PLATFORM-STD | API-FIN-023 | 409 | duplicate fiscal year code | رمز السنة المالية مستخدم بالفعل | Fiscal year code already in use |
| FIN-409-NOT-REOPENABLE | RULE-FIN-014 | API-FIN-024, 026 | 409 | period Hard Closed | الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها | The period is hard-closed and cannot be reopened |
| FIN-409-INVALID-TRANSITION | PLATFORM-STD | API-FIN-025 | 409 | period not in the expected state | لا يمكن تنفيذ هذا الانتقال من الحالة الحالية | This transition is not allowed from the current status |
| FIN-403-SOD-VIOLATION | RULE-FIN-015 | API-FIN-026, 027 | 403 | close-approver also holds entry-creation permission | صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود | The close-approval permission is separate from the entry-creation permission |
| FIN-404-PERIOD | PLATFORM-STD | API-FIN-024, 025, 026 | 404 | unknown period id | الفترة غير موجودة | Period not found |
| FIN-409-PERIODS-NOT-CLOSED | PLATFORM-STD (§10.4 precondition) | API-FIN-027 | 409 | not every period Hard Closed | يجب إغلاق كل الفترات إغلاقًا صارمًا أولًا | Every period must be hard-closed first |
| FIN-404-YEAR | PLATFORM-STD | API-FIN-027 | 404 | unknown fiscal year id | السنة المالية غير موجودة | Fiscal year not found |
| FIN-403-FORBIDDEN | PLATFORM-STD (CORE interceptor) | every secured API | 403 | missing module/screen/action grant | غير مصرح بهذا الإجراء | You are not authorized to perform this action |
| FIN-400-INVALID-SORT | PLATFORM-STD | every search API | 400 | unrecognized sort field | حقل الترتيب غير معروف | Unrecognized sort field |
| FIN-503 | PLATFORM-STD (MDL unreachable) | any lookup-validating API | 503 | XM-FIN-001 call failed | تعذّر التحقق من القيمة المرجعية مؤقتًا | Could not verify the reference value right now |
| FIN-500 | PLATFORM-STD (infrastructure) | any | 500 | unhandled server error | حدث خطأ في الخادم | A server error occurred |

Every PLATFORM-STD row follows SEC's ADR-SEC-002 umbrella convention, cited (not re-derived).

## Alignment self-check (ALIGN) — FIN v1

```
TRACEABILITY      ✓ every API-*/QR-*/RULE-*/DBF-*/XM-* used in a phase appears in the Plan Index; every PHASE/SUB/atom carries traces=; every traces target exists upstream (REQ-FIN-001..046, DBF-FIN-001..146 all defined in srs/db-script)
BINDING (§2A)     ✓ no placeholder; every column cites a DBF; every RULE message present in ar+en; business code (docNo) format explicit with generation source
MANIFEST (§4)     ✓ only the mandated columns; all 146 DBF listed; 12 columns note XM-FIN-001 (SOFT-READ, never ⏸/blocking)
QRC (§5)          ✓ every API with a DB operation has ≥1 QR; no join for a lookup label; exact generation object named (Phase 1 CORE)
API (R3)          ✓ every RULE in a Validations line has a catalog row; platform errors carry RULE=PLATFORM-STD (SEC's ADR-SEC-002 convention); create/update requests exclude PK/audit/system fields (docNo, statusCode, postedAt); business code (docNo) always in responses, never in create/update bodies
CROSS-MODULE      ✓ 1 XM from db-script, 1 placed (XM-FIN-001), 0 mismatched; ACTIVE status correct; inbound stub XM-INBOUND-STUB-3 notation
SECURITY (R7)     ✓ every secured API declares its PERM_*; ERP-4 (every mutation endpoint declares its PERM_*): checked — every POST/PUT/PATCH/DELETE API above states one, including the two custom SoD-relevant actions
CORE (R1)         ✓ layers, domain placement, error signalling (`FIN-<3-digit>`), type mapping (incl. the NUMERIC→Integer governance note) all declared
DECISIONS         ✓ ADR-FIN-001 (carried from P2) cited; one new DEFAULT this stage (JOURNAL_TYPE gains CLOSING/OPENING, data-only, non-breaking); no BLOCKED ADR
ACCOUNTING §12    ✓ all 14 must-honor points traced: (1) RULE-FIN-006 · (2) POL-FIN-002/API-FIN-029 sign presentation · (3) RULE-FIN-007 · (4) RULE-FIN-008 · (5) CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE + directionCode · (6) RULE-FIN-003/010 · (7) RULE-FIN-011 · (8) API-FIN-029 (balances by construction) · (9) every report QR reads POSTED lines live, no stored balance column anywhere in db-script-fin.md · (10) REQ-FIN-036/RULE for continuity · (11) RULE-FIN-009 + QR-FIN-044 dimension grouping · (12) RULE-FIN-004 · (13) RULE-FIN-016 lock + no DELETE mapping anywhere · (14) POL-FIN-014, no host-specific branch anywhere in this plan
RESULT            PASSED ✓ — 0 findings
```

**Coverage — ENT/DBF → phases → QR → XM**: every ENT-FIN-001..014 appears in exactly one
DATA-DOM entity block with ≥1 QR cited under REPOSITORY OPS; every DBF-FIN-001..146
appears in the DB Alignment Manifest and its owning entity's block; XM-FIN-001 appears in
INT-C, INT-R and every lookup-backed field's manifest row.

**Coverage — RULE → API → catalog code**: RULE-FIN-001→API-FIN-002/003→
FIN-409-PARENT-NOT-LEAF-ELIGIBLE/FIN-409-HAS-CHILDREN · RULE-FIN-002→API-FIN-007→
FIN-409-DIMVALUE-DUP · RULE-FIN-003→API-FIN-011/016→FIN-409-REMAINDER-COUNT ·
RULE-FIN-004→API-FIN-020→FIN-409-DUPLICATE-EVENT · RULE-FIN-005→API-FIN-020→
FIN-404-NO-ACTIVE-RULE · RULE-FIN-006→API-FIN-019/020/014/017→FIN-409-UNBALANCED ·
RULE-FIN-007→(same APIs)→FIN-409-NOT-POSTABLE-ACCOUNT · RULE-FIN-008→(same)→
FIN-409-PERIOD-NOT-OPEN · RULE-FIN-009→(same)→FIN-409-INVALID-DIMENSION ·
RULE-FIN-010→API-FIN-020/014/017→(no distinct code — success-path computation) ·
RULE-FIN-011→API-FIN-021→(no distinct code — success-path build) ·
RULE-FIN-012→API-FIN-021→(no distinct code — success-path period substitution) ·
RULE-FIN-013→API-FIN-021→FIN-409-NOT-POSTED · RULE-FIN-014→API-FIN-024/026→
FIN-409-NOT-REOPENABLE · RULE-FIN-015→API-FIN-026/027→FIN-403-SOD-VIOLATION ·
RULE-FIN-016→(every posted-entry endpoint)→(enforced by omission, no code needed — no
UPDATE/DELETE mapping exists on a POSTED row).

**Coverage — XM → status → blocks → workaround**: XM-FIN-001 → ACTIVE → blocks none → no
workaround needed.

## QR id definitions (cross-reference index — full detail in Query Reference Catalog above)
**QR-FIN-001** — FIND_BY_CRITERIA search accounts [ENT-FIN-001, API-FIN-001]
**QR-FIN-002** — SAVE create account [ENT-FIN-001, API-FIN-002]
**QR-FIN-003** — UPDATE update account [ENT-FIN-001, API-FIN-003]
**QR-FIN-004** — UPDATE deactivate account [ENT-FIN-001, API-FIN-004]
**QR-FIN-005** — EXISTS account code unique [ENT-FIN-001, API-FIN-002]
**QR-FIN-006** — EXISTS account has no children (RULE-FIN-001) [ENT-FIN-001, API-FIN-002, API-FIN-003]
**QR-FIN-007** — FIND_BY_CRITERIA search dimensions [ENT-FIN-002, API-FIN-005]
**QR-FIN-008** — SAVE create dimension [ENT-FIN-002, API-FIN-006]
**QR-FIN-009** — SAVE create dimension value [ENT-FIN-003, API-FIN-007]
**QR-FIN-010** — EXISTS dimension value code unique within dimension (RULE-FIN-002) [ENT-FIN-003, API-FIN-007]
**QR-FIN-011** — FIND_BY_CRITERIA search dimension values [ENT-FIN-003, API-FIN-008]
**QR-FIN-012** — FIND_BY_CRITERIA search event-type rules [ENT-FIN-009, API-FIN-009]
**QR-FIN-013** — SAVE create event-type rule [ENT-FIN-009, API-FIN-010]
**QR-FIN-014** — EXISTS one active rule per event type [ENT-FIN-009, API-FIN-010]
**QR-FIN-015** — SAVE add rule line [ENT-FIN-010, API-FIN-011]
**QR-FIN-016** — EXISTS remainder-line/target count (RULE-FIN-003) [ENT-FIN-010, ENT-FIN-014, API-FIN-011, API-FIN-016]
**QR-FIN-017** — FIND_BY_CRITERIA search templates [ENT-FIN-011, API-FIN-012]
**QR-FIN-018** — SAVE create template with lines [ENT-FIN-011, ENT-FIN-012, API-FIN-013]
**QR-FIN-019** — FIND_ONE load template due to run [ENT-FIN-011, API-FIN-014]
**QR-FIN-020** — FIND_BY_CRITERIA search allocation rules [ENT-FIN-013, API-FIN-015]
**QR-FIN-021** — SAVE create allocation rule with targets [ENT-FIN-013, ENT-FIN-014, API-FIN-016]
**QR-FIN-022** — FIND_ONE load allocation rule + source balance [ENT-FIN-013, API-FIN-017]
**QR-FIN-023** — FIND_BY_CRITERIA search journal entries [ENT-FIN-004, API-FIN-018]
**QR-FIN-024** — SAVE build manual entry (DRAFT) [ENT-FIN-004, ENT-FIN-005, ENT-FIN-006, API-FIN-019]
**QR-FIN-025** — SAVE build event entry (DRAFT) [ENT-FIN-004, ENT-FIN-005, ENT-FIN-006, API-FIN-020]
**QR-FIN-026** — EXISTS duplicate eventReference (RULE-FIN-004) [ENT-FIN-004, API-FIN-020]
**QR-FIN-027** — EXISTS active rule for event type (RULE-FIN-005) [ENT-FIN-009, API-FIN-020]
**QR-FIN-028** — AGGREGATE compute remainder-line amount (RULE-FIN-010) [ENT-FIN-005, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-029** — EXISTS debits=credits (RULE-FIN-006) [ENT-FIN-005, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-030** — EXISTS every line account leaf+active (RULE-FIN-007) [ENT-FIN-001, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-031** — EXISTS period open at post (RULE-FIN-008) [ENT-FIN-008, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-032** — EXISTS every dimension value valid+active (RULE-FIN-009) [ENT-FIN-006, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-033** — UPDATE post entry DRAFT→POSTED [ENT-FIN-004, API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017]
**QR-FIN-034** — SAVE build reversal entry (RULE-FIN-011) [ENT-FIN-004, ENT-FIN-005, ENT-FIN-006, API-FIN-021]
**QR-FIN-035** — EXISTS original entry is POSTED (RULE-FIN-013) [ENT-FIN-004, API-FIN-021]
**QR-FIN-036** — FIND_ONE current open period for reversal (RULE-FIN-012) [ENT-FIN-008, API-FIN-021]
**QR-FIN-037** — FIND_ONE read one entry with lines [ENT-FIN-004, API-FIN-022]
**QR-FIN-038** — SAVE create fiscal year + periods [ENT-FIN-007, ENT-FIN-008, API-FIN-023]
**QR-FIN-039** — UPDATE open/soft-close/hard-close period [ENT-FIN-008, API-FIN-024, API-FIN-025, API-FIN-026]
**QR-FIN-040** — EXISTS period not already Hard Closed (RULE-FIN-014) [ENT-FIN-008, API-FIN-024, API-FIN-026]
**QR-FIN-041** — AGGREGATE year-end closing/opening balances [ENT-FIN-004, ENT-FIN-005, API-FIN-027]
**QR-FIN-042** — FIND_BY_CRITERIA account ledger running balance [ENT-FIN-005, API-FIN-028]
**QR-FIN-043** — AGGREGATE trial balance / balance sheet / income statement account balances [ENT-FIN-005, API-FIN-029, API-FIN-030, API-FIN-031]
**QR-FIN-044** — AGGREGATE dimension report [ENT-FIN-005, ENT-FIN-006, API-FIN-032]

## XM id definitions
**XM-FIN-001** — SOFT-READ every FIN lookup-backed column → MDL_LOOKUP_VALUE [REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031]

## Registry content
See `registry-exec-be-fin.md`.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-srs (FIN)>>>
## REGISTRY — P1 — FIN v1
══════════════════════════════════════════════════════════════════

Entities
| ENT id | Name (ar/en) | Kind | PRIVATE/SHARED | Status |
|---|---|---|---|---|
| ENT-FIN-001 | الحساب / Account | master | PRIVATE | REGISTERED |
| ENT-FIN-002 | البُعد / Dimension | config | PRIVATE | REGISTERED |
| ENT-FIN-003 | قيمة البُعد / DimensionValue | lookup | PRIVATE | REGISTERED |
| ENT-FIN-004 | رأس قيد اليومية / JournalEntry | transactional | PRIVATE | REGISTERED |
| ENT-FIN-005 | سطر قيد اليومية / JournalLine | transactional | PRIVATE | REGISTERED |
| ENT-FIN-006 | بُعد سطر القيد / JournalLineDimension | transactional | PRIVATE | REGISTERED |
| ENT-FIN-007 | السنة المالية / FiscalYear | master | PRIVATE | REGISTERED |
| ENT-FIN-008 | الفترة المحاسبية / FiscalPeriod | master | PRIVATE | REGISTERED |
| ENT-FIN-009 | قاعدة نوع الحدث / EventTypeRule | config | PRIVATE | REGISTERED |
| ENT-FIN-010 | سطر القاعدة / RuleLine | config | PRIVATE | REGISTERED |
| ENT-FIN-011 | قالب متكرر/عكسي / RecurringTemplate | config | PRIVATE | REGISTERED |
| ENT-FIN-012 | سطر القالب المتكرر / RecurringTemplateLine | config | PRIVATE | REGISTERED |
| ENT-FIN-013 | قاعدة توزيع / AllocationRule | config | PRIVATE | REGISTERED |
| ENT-FIN-014 | هدف التوزيع / AllocationTarget | config | PRIVATE | REGISTERED |

Consumed
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ |
|---|---|---|---|
| User | ENT-SEC-001 | SEC | HARD-FK (principal string) |
| ModuleRegistry | ENT-SEC-004 | SEC | HARD-FK |
| ScreenRegistry | ENT-SEC-005 | SEC | HARD-FK |
| ActionRegistry | ENT-SEC-006 | SEC | HARD-FK |
| LookupType | ENT-MDL-001 | MDL | HARD-FK |
| LookupValue | ENT-MDL-002 | MDL | HARD-FK |

Lookups owned
| Key | ENT | Values count |
|---|---|---|
| ACCOUNT_TYPE | ENT-FIN-001 | 5 |
| DEBIT_CREDIT | ENT-FIN-001, ENT-FIN-005, ENT-FIN-010, ENT-FIN-012 | 2 |
| PERIOD_STATE | ENT-FIN-008 | 4 |
| FISCAL_YEAR_STATUS | ENT-FIN-007 | 2 |
| JOURNAL_TYPE | ENT-FIN-004 | 5 |
| JOURNAL_STATUS | ENT-FIN-004 | 3 |
| ACCOUNTING_EVENT_TYPE | ENT-FIN-009 | 0 (host-defined) |
| PAYMENT_METHOD | (registered, no dedicated column this v1) | 0 (host-defined) |
| ACCOUNT_DERIVATION_TYPE | ENT-FIN-010 | 3 |
| AMOUNT_SOURCE_TYPE | ENT-FIN-010 | 3 |
| DISTRIBUTION_TYPE | ENT-FIN-010, ENT-FIN-014 | 3 |
| RECURRING_SCHEDULE_TYPE | ENT-FIN-011 | 2 |
| RECURRING_FREQUENCY | ENT-FIN-011 | 4 |

Lookups consumed
none.

Screens
| SCR-REQ id | Name (ar/en) | Page code |
|---|---|---|
| SCR-REQ-FIN-001 | شجرة الحسابات / Chart of accounts | FIN_ACCOUNTS |
| SCR-REQ-FIN-002 | تعريف الأبعاد وقيمها / Dimension definition & values | FIN_DIMENSIONS |
| SCR-REQ-FIN-003 | قواعد المحرك / Engine rules | FIN_RULES |
| SCR-REQ-FIN-004 | قوالب متكررة/عكسية / Recurring/reversing templates | FIN_RECURRING_TEMPLATES |
| SCR-REQ-FIN-005 | قواعد التوزيع / Allocation rules | FIN_ALLOCATION_RULES |
| SCR-REQ-FIN-006 | قيود اليومية / Journal entries | FIN_JOURNAL_ENTRIES |
| SCR-REQ-FIN-007 | الفترات والسنوات المالية / Fiscal periods & years | FIN_PERIODS |
| SCR-REQ-FIN-008 | دفتر الحساب / Account ledger | FIN_ACCOUNT_LEDGER |
| SCR-REQ-FIN-009 | ميزان المراجعة / Trial balance | FIN_TRIAL_BALANCE |
| SCR-REQ-FIN-010 | الميزانية العمومية / Balance sheet | FIN_BALANCE_SHEET |
| SCR-REQ-FIN-011 | قائمة الدخل / Income statement | FIN_INCOME_STATEMENT |
| SCR-REQ-FIN-012 | تقارير الأبعاد / Dimension reports | FIN_DIMENSION_REPORTS |

Requirements
REQ count: 46 · AC count: 46 · RULE count: 16 · ENT count: 14 · SCR-REQ count: 12
Last sequence per atom: REQ: 046 · AC: 046 · ENT: 014 · RULE: 016 · SCR-REQ: 012

REQ ids (full text in srs-fin.md → A4): REQ-FIN-001, REQ-FIN-002, REQ-FIN-003, REQ-FIN-004,
REQ-FIN-005, REQ-FIN-006, REQ-FIN-007, REQ-FIN-008, REQ-FIN-009, REQ-FIN-010, REQ-FIN-011,
REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018,
REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-022, REQ-FIN-023, REQ-FIN-024, REQ-FIN-025,
REQ-FIN-026, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-031, REQ-FIN-032,
REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038, REQ-FIN-039,
REQ-FIN-040, REQ-FIN-041, REQ-FIN-042, REQ-FIN-043, REQ-FIN-044, REQ-FIN-045, REQ-FIN-046

AC ids (full text in srs-fin.md → A4, one per REQ above): AC-FIN-001, AC-FIN-002, AC-FIN-003,
AC-FIN-004, AC-FIN-005, AC-FIN-006, AC-FIN-007, AC-FIN-008, AC-FIN-009, AC-FIN-010,
AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-014, AC-FIN-015, AC-FIN-016, AC-FIN-017,
AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-022, AC-FIN-023, AC-FIN-024,
AC-FIN-025, AC-FIN-026, AC-FIN-027, AC-FIN-028, AC-FIN-029, AC-FIN-030, AC-FIN-031,
AC-FIN-032, AC-FIN-033, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-037, AC-FIN-038,
AC-FIN-039, AC-FIN-040, AC-FIN-041, AC-FIN-042, AC-FIN-043, AC-FIN-044, AC-FIN-045,
AC-FIN-046

RULE ids (full text in srs-fin.md → A5): RULE-FIN-001, RULE-FIN-002, RULE-FIN-003,
RULE-FIN-004, RULE-FIN-005, RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009,
RULE-FIN-010, RULE-FIN-011, RULE-FIN-012, RULE-FIN-013, RULE-FIN-014, RULE-FIN-015,
RULE-FIN-016

Decisions
ADR ids: none.

Event
"P1 completed: FIN v1 — 14 entities, 46 requirements, 46 acceptance criteria, 16 rules, 12 screen requirements, 0 ADRs"
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-db (FIN)>>>
## REGISTRY — P2 — FIN v1
══════════════════════════════════════════════════════════════════

Tables
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| FIN_ACCOUNT | ENT-FIN-001 | master | DBF-FIN-001 … DBF-FIN-013 |
| FIN_DIMENSION | ENT-FIN-002 | config | DBF-FIN-014 … DBF-FIN-022 |
| FIN_DIMENSION_VALUE | ENT-FIN-003 | lookup | DBF-FIN-023 … DBF-FIN-033 |
| FIN_JOURNAL_ENTRY | ENT-FIN-004 | transactional | DBF-FIN-034 … DBF-FIN-050 |
| FIN_JOURNAL_LINE | ENT-FIN-005 | transactional | DBF-FIN-051 … DBF-FIN-060 |
| FIN_JOURNAL_LINE_DIM | ENT-FIN-006 | transactional | DBF-FIN-061 … DBF-FIN-064 |
| FIN_FISCAL_YEAR | ENT-FIN-007 | master | DBF-FIN-065 … DBF-FIN-074 |
| FIN_FISCAL_PERIOD | ENT-FIN-008 | master | DBF-FIN-075 … DBF-FIN-088 |
| FIN_EVENT_TYPE_RULE | ENT-FIN-009 | config | DBF-FIN-089 … DBF-FIN-097 |
| FIN_RULE_LINE | ENT-FIN-010 | config | DBF-FIN-098 … DBF-FIN-108 |
| FIN_RECURRING_TEMPLATE | ENT-FIN-011 | config | DBF-FIN-109 … DBF-FIN-121 |
| FIN_RECURRING_TEMPLATE_LINE | ENT-FIN-012 | config | DBF-FIN-122 … DBF-FIN-129 |
| FIN_ALLOCATION_RULE | ENT-FIN-013 | config | DBF-FIN-130 … DBF-FIN-138 |
| FIN_ALLOCATION_TARGET | ENT-FIN-014 | config | DBF-FIN-139 … DBF-FIN-146 |

DBF ids (full detail in db-script-fin.md → §1): DBF-FIN-001, DBF-FIN-002, DBF-FIN-003,
DBF-FIN-004, DBF-FIN-005, DBF-FIN-006, DBF-FIN-007, DBF-FIN-008, DBF-FIN-009, DBF-FIN-010,
DBF-FIN-011, DBF-FIN-012, DBF-FIN-013, DBF-FIN-014, DBF-FIN-015, DBF-FIN-016, DBF-FIN-017,
DBF-FIN-018, DBF-FIN-019, DBF-FIN-020, DBF-FIN-021, DBF-FIN-022, DBF-FIN-023, DBF-FIN-024,
DBF-FIN-025, DBF-FIN-026, DBF-FIN-027, DBF-FIN-028, DBF-FIN-029, DBF-FIN-030, DBF-FIN-031,
DBF-FIN-032, DBF-FIN-033, DBF-FIN-034, DBF-FIN-035, DBF-FIN-036, DBF-FIN-037, DBF-FIN-038,
DBF-FIN-039, DBF-FIN-040, DBF-FIN-041, DBF-FIN-042, DBF-FIN-043, DBF-FIN-044, DBF-FIN-045,
DBF-FIN-046, DBF-FIN-047, DBF-FIN-048, DBF-FIN-049, DBF-FIN-050, DBF-FIN-051, DBF-FIN-052,
DBF-FIN-053, DBF-FIN-054, DBF-FIN-055, DBF-FIN-056, DBF-FIN-057, DBF-FIN-058, DBF-FIN-059,
DBF-FIN-060, DBF-FIN-061, DBF-FIN-062, DBF-FIN-063, DBF-FIN-064, DBF-FIN-065, DBF-FIN-066,
DBF-FIN-067, DBF-FIN-068, DBF-FIN-069, DBF-FIN-070, DBF-FIN-071, DBF-FIN-072, DBF-FIN-073,
DBF-FIN-074, DBF-FIN-075, DBF-FIN-076, DBF-FIN-077, DBF-FIN-078, DBF-FIN-079, DBF-FIN-080,
DBF-FIN-081, DBF-FIN-082, DBF-FIN-083, DBF-FIN-084, DBF-FIN-085, DBF-FIN-086, DBF-FIN-087,
DBF-FIN-088, DBF-FIN-089, DBF-FIN-090, DBF-FIN-091, DBF-FIN-092, DBF-FIN-093, DBF-FIN-094,
DBF-FIN-095, DBF-FIN-096, DBF-FIN-097, DBF-FIN-098, DBF-FIN-099, DBF-FIN-100, DBF-FIN-101,
DBF-FIN-102, DBF-FIN-103, DBF-FIN-104, DBF-FIN-105, DBF-FIN-106, DBF-FIN-107, DBF-FIN-108,
DBF-FIN-109, DBF-FIN-110, DBF-FIN-111, DBF-FIN-112, DBF-FIN-113, DBF-FIN-114, DBF-FIN-115,
DBF-FIN-116, DBF-FIN-117, DBF-FIN-118, DBF-FIN-119, DBF-FIN-120, DBF-FIN-121, DBF-FIN-122,
DBF-FIN-123, DBF-FIN-124, DBF-FIN-125, DBF-FIN-126, DBF-FIN-127, DBF-FIN-128, DBF-FIN-129,
DBF-FIN-130, DBF-FIN-131, DBF-FIN-132, DBF-FIN-133, DBF-FIN-134, DBF-FIN-135, DBF-FIN-136,
DBF-FIN-137, DBF-FIN-138, DBF-FIN-139, DBF-FIN-140, DBF-FIN-141, DBF-FIN-142, DBF-FIN-143,
DBF-FIN-144, DBF-FIN-145, DBF-FIN-146

XM index
| XM id | Type | From | To | Status |
|---|---|---|---|---|
| XM-FIN-001 | SOFT-READ | FIN | MDL | ACTIVE |

Lookups
| Key | Seeded values count | Owner |
|---|---|---|
| ACCOUNT_TYPE | 5 | FIN |
| DEBIT_CREDIT | 2 | FIN |
| PERIOD_STATE | 4 | FIN |
| FISCAL_YEAR_STATUS | 2 | FIN |
| JOURNAL_TYPE | 5 | FIN |
| JOURNAL_STATUS | 3 | FIN |
| ACCOUNTING_EVENT_TYPE | 0 (host-defined) | FIN |
| PAYMENT_METHOD | 0 (host-defined) | FIN |
| ACCOUNT_DERIVATION_TYPE | 3 | FIN |
| AMOUNT_SOURCE_TYPE | 3 | FIN |
| DISTRIBUTION_TYPE | 3 | FIN |
| RECURRING_SCHEDULE_TYPE | 2 | FIN |
| RECURRING_FREQUENCY | 4 | FIN |
All seeded via MDL's API at onboarding time (BLOCK 8 note), not local INSERTs.

Sequences
Last DBF: DBF-FIN-146 · Last XM: XM-FIN-001

Decisions
ADR-FIN-001 (ACCEPTED, non-breaking) — see erp/decisions/FIN/ADR-FIN-001.md

Event
"P2 completed: FIN v1 — 14 tables, 146 DBF, 1 XM"

Cascade
No registry XM row anywhere in the platform currently targets FIN with status DEFERRED
(FIN is the last module of this batch) — nothing to resolve. XM-FIN-001 resolves
immediately to ACTIVE since MDL v1 is already gated.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

---
# INPUTS — module MDL (generated current state)

<<<INPUT: srs (MDL)>>>
# SRS — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-10)
Counts : ENT 2 · REQ 13 · AC 13 · RULE 4 · SCR-REQ 2 · ADR 0
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |
|---|---|
| Module | MDL — البيانات المرجعية / Master Data Lookup |
| Feature code | MDL |
| Version | v1 |
| Date | 2026-09-10 |
| Status | DRAFT (P1) |
| Prepared by | governance-factory (analysis lane) |
| Decisions applied count | 0 |

## A2 — Functional context

**In scope:** نوع اللوكب (Master) وقيمه (Detail)، شاشة عامة واحدة لإدارة كل القوائم، تسجيل
نوع جديد كبيانات من أي وحدة مستهلكة، قراءة القيم النشطة بالمفتاح لأي وحدة مستهلكة، سجل
الأنواع مجمّعًا حسب المالك، التحقق من صحة الوحدة المالكة عبر SEC.

**Out of scope:** تسلسل هرمي لقيم اللوكب (شجرة)، صلاحيات دقيقة لكل نوع لوكب على حدة (تبقى
الصلاحية على مستوى الشاشة فقط)؛ غير مذكورة في `lookup-module-plan-en.md`
[business-policies-mdl.md → SCOPE EXCEPTIONS].

**Module function (one paragraph):** MDL هو المركز الموحّد الوحيد لكل قوائم القيم
المُرمَّزة في المنصة؛ لا وحدة أخرى — بما فيها SEC وFIN لاحقًا — تحتفظ بجدول قيم مرجعية
خاص بها؛ كل وحدة تسجّل أنواعها هنا كبيانات وتقرأ قيمها من هنا وقت التشغيل.

**Detailed description (workflow narrative, roles):** وحدة مستهلكة (مثل FIN لاحقًا) تُسجّل
نوع لوكب جديد كبيانات، مسمّية نفسها مالكًا → MDL يتحقق من أن رمز الوحدة مسجَّل فعليًا في
SEC (قراءة فقط، بلا مفتاح خارجي فعلي) → مسؤول مخوَّل يدير قيم ذلك النوع عبر الشاشة العامة
الواحدة (رئيسي-تفصيلي) → أي وحدة تقرأ القيم النشطة بالمفتاح وقت التشغيل، مرتبة حسب الترتيب.

**Current situation:** لا يوجد نظام سابق ضمن هذه الدفعة؛ SEC هي الوحدة الوحيدة المكتملة
حتى الآن ولا تملك آلية قوائم مرجعية مركزية — قيمها الثلاث (USER_STATUS, SIGNUP_STATUS,
AUDIT_EVENT_TYPE) مُقيَّدة بـ CHECK محليًا (ADR-SEC-001)، على أن تُهاجَر لاحقًا إلى هنا.

**Current difficulties:** بلا مركزية، كل وحدة تخترع قوائمها الخاصة فتتضارب القيم — بالضبط
المشكلة التي يحلّها MDL (KB:erp-domain-standards §2 rule 3).

**Proposed system and benefits:** مركز واحد موثوق يمنع الازدواج والتضارب، ويجعل إضافة قائمة
أو قيمة جديدة عملية بيانات بحتة، لا تغييرًا في الشيفرة.

**General notes (constraints, deferred items):** لا محرك سير عمل؛ هجرة قوائم SEC الثلاث
إلى هذا المركز مؤجّلة لإصدار v2 من SEC (خارج نطاق هذه الدفعة، موثّقة في ADR-SEC-001).

## A3 — Entities and fields

Standard fields per kind (profile.conventions.entity_defaults):
master → nameAr, nameEn, code, isActiveFl, createdBy, createdAt, updatedBy, updatedAt;
lookup → code, nameAr, nameEn, sortOrder, isActiveFl.

### ENT-MDL-001 — نوع اللوكب / LookupType
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| master | SHARED (owner) — every consuming module registers and reads its own types here | No — `key` is a client-chosen stable string, not a platform-numbered sequence [§3.3 test] | create, read, search, update (name only), deactivate | consumed (registered into) by every future module | lookup-module-plan-en.md §2-§3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| lookupTypePk | number | yes (system) | — | primary key | معرّف نوع اللوكب | LookupType id |
| key | text | yes | unique, immutable after create [RULE-MDL-003] | the string every consumer cites (e.g. `USER_STATUS`) | المفتاح | Key |
| ownerModuleCode | text | yes | must exist in SEC's ModuleRegistry [RULE-MDL-001] | namespacing | رمز الوحدة المالكة | Owner module code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-MDL-002 — قيمة اللوكب / LookupValue
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| lookup | SHARED (owner) — every consuming module reads/manages its own values here | No | create, read, search, update, deactivate, reorder | consumed (read) by every future module | lookup-module-plan-en.md §3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| lookupValuePk | number | yes (system) | — | primary key | معرّف قيمة اللوكب | LookupValue id |
| lookupTypeId | reference | yes | ENT-MDL-001 | — | نوع اللوكب | Lookup type |
| code | text | yes | unique within its lookupTypeId [RULE-MDL-002] | the value a consumer stores | الرمز | Code |
| nameAr | text | yes | — | — | الاسم (عربي) | Name (Arabic) |
| nameEn | text | yes | — | — | الاسم (إنجليزي) | Name (English) |
| sortOrder | number | yes | — | display order | ترتيب العرض | Sort order |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-MDL-001 — إنشاء نوع لوكب / Create a lookup type
Pattern    : event
Statement  : When an administrator creates a lookup type naming its owner module, the system shall record it as an active lookup type.
Traces     : US-MDL-001, US-MDL-004
Entities   : ENT-MDL-001
Rationale  : registration as data, per module's own integration
Source     : lookup-module-plan-en.md §2-§3
Priority   : HIGH
#### AC-MDL-001 — [REQ-MDL-001]
Given a unique key and a registered owner module code
When an administrator submits the lookup type form
Then the system creates an active LookupType

### REQ-MDL-002 — رفض نوع لوحدة غير مسجّلة / Reject a type for an unregistered module
Pattern    : unwanted
Statement  : If a lookup type registration names a module that is not registered in the Security module, then the system shall reject the registration.
Traces     : US-MDL-001, US-MDL-004
Entities   : ENT-MDL-001
Rationale  : RULE-MDL-001; POL-MDL-003
Source     : lookup-module-plan-en.md §3
Priority   : HIGH
#### AC-MDL-002 — [REQ-MDL-002]
Given an owner module code with no ModuleRegistry row in SEC
When a lookup type registration names that code
Then the system rejects it and creates no LookupType

### REQ-MDL-003 — تعديل اسم نوع اللوكب / Edit a lookup type's name
Pattern    : event
Statement  : When an administrator edits a lookup type's name, the system shall update it without changing its key.
Traces     : US-MDL-001
Entities   : ENT-MDL-001
Rationale  : RULE-MDL-003 — key immutability
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-003 — [REQ-MDL-003]
Given an existing LookupType
When an administrator updates its nameAr/nameEn
Then the system saves the new names and leaves the key unchanged

### REQ-MDL-004 — تعطيل نوع لوكب / Deactivate a lookup type
Pattern    : event
Statement  : When an administrator deactivates a lookup type, the system shall exclude its values from every future consumer read.
Traces     : US-MDL-001
Entities   : ENT-MDL-001
Rationale  : RULE-MDL-004
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-004 — [REQ-MDL-004]
Given an active LookupType
When an administrator deactivates it
Then the system sets isActiveFl=false and REQ-MDL-011 no longer returns its values

### REQ-MDL-005 — اختيار النوع وعرض قيمه / Select a type and list its values
Pattern    : event
Statement  : When a user selects a lookup type in the master, the system shall list its values in the detail.
Traces     : US-MDL-002
Entities   : ENT-MDL-001, ENT-MDL-002
Rationale  : the generic master-detail mechanism, POL-MDL-004
Source     : lookup-module-plan-en.md §3
Priority   : HIGH
#### AC-MDL-005 — [REQ-MDL-005]
Given a lookup type with three values
When a user selects it in the master list
Then the system lists exactly those three values in the detail, ordered by sortOrder

### REQ-MDL-006 — إنشاء قيمة لوكب / Create a lookup value
Pattern    : event
Statement  : When an authorized user creates a value under a selected lookup type, the system shall record its code, bilingual labels, sort order and active flag.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : POL-MDL-005
Source     : lookup-module-plan-en.md §3
Priority   : HIGH
#### AC-MDL-006 — [REQ-MDL-006]
Given a selected lookup type and a code not yet used within it
When the user submits the value form
Then the system creates an active LookupValue under that type

### REQ-MDL-007 — رفض تكرار الرمز ضمن النوع / Reject a duplicate code within a type
Pattern    : unwanted
Statement  : If two lookup values under the same lookup type share the same code, then the system shall reject the second.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : RULE-MDL-002; POL-MDL-006
Source     : lookup-module-plan-en.md §6
Priority   : HIGH
#### AC-MDL-007 — [REQ-MDL-007]
Given a lookup type already holding a value with code "ACTIVE"
When a user attempts to create another value with code "ACTIVE" under the same type
Then the system rejects it and creates no second row

### REQ-MDL-008 — تعديل قيمة لوكب / Edit a lookup value
Pattern    : event
Statement  : When an authorized user edits a lookup value's labels or sort order, the system shall update it.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : POL-MDL-005
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-008 — [REQ-MDL-008]
Given an existing LookupValue
When the user updates its nameAr/nameEn/sortOrder
Then the system saves the new values (code and lookupTypeId remain unchanged)

### REQ-MDL-009 — تعطيل قيمة لوكب / Deactivate a lookup value
Pattern    : event
Statement  : When an authorized user deactivates a lookup value, the system shall exclude it from future consumer reads.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : POL-MDL-005
Source     : lookup-module-plan-en.md §3
Priority   : MEDIUM
#### AC-MDL-009 — [REQ-MDL-009]
Given an active LookupValue
When the user deactivates it
Then the system sets isActiveFl=false and REQ-MDL-011 no longer returns it

### REQ-MDL-010 — إعادة ترتيب قيم اللوكب / Reorder lookup values
Pattern    : event
Statement  : When an authorized user reorders the values of a lookup type, the system shall persist the new sort order for each affected value.
Traces     : US-MDL-002
Entities   : ENT-MDL-002
Rationale  : sortOrder is a stored, consumer-facing field (A3)
Source     : lookup-module-plan-en.md §3
Priority   : LOW
#### AC-MDL-010 — [REQ-MDL-010]
Given three values with sortOrder 1,2,3
When the user reorders them to 3,1,2
Then the system persists sortOrder=3,1,2 respectively and REQ-MDL-011 returns them in that order

### REQ-MDL-011 — قراءة القيم النشطة بالمفتاح / Read active values by key
Pattern    : event
Statement  : When a consuming module requests the active values of a lookup type by key, the system shall return them ordered by sort order.
Traces     : US-MDL-003
Entities   : ENT-MDL-001, ENT-MDL-002
Rationale  : POL-MDL-001 — the module's entire reason to exist
Source     : lookup-module-plan-en.md §2, §4
Priority   : HIGH
#### AC-MDL-011 — [REQ-MDL-011]
Given a lookup type "PAYMENT_METHOD" with two active and one inactive value
When a consuming module requests its values by key
Then the system returns exactly the two active values, ordered by sortOrder

### REQ-MDL-012 — رفض مفتاح نوع غير موجود / Reject an unknown type key
Pattern    : unwanted
Statement  : If a consuming module requests values for a lookup type key that does not exist, then the system shall return a not-found error.
Traces     : US-MDL-003
Entities   : ENT-MDL-001
Rationale  : distinguishes "type exists, zero values" (success, empty) from "type never registered" (integration defect)
Source     : lookup-module-plan-en.md §4
Priority   : MEDIUM
#### AC-MDL-012 — [REQ-MDL-012]
Given no LookupType with key "NOT_A_REAL_KEY"
When a consuming module requests its values
Then the system returns a not-found error, not an empty success

### REQ-MDL-013 — تصفّح سجل الأنواع حسب المالك / Browse the type registry by owner
Pattern    : event
Statement  : When an administrator browses the lookup-type registry, the system shall group active lookup types by their owner module.
Traces     : US-MDL-005
Entities   : ENT-MDL-001
Rationale  : POL-MDL-002
Source     : lookup-module-plan-en.md §7
Priority   : MEDIUM
#### AC-MDL-013 — [REQ-MDL-013]
Given lookup types owned by SEC and by MDL... (example: two types owned by SEC, one by MDL's own future host)
When an administrator opens the registry screen
Then the system shows the types grouped under their respective owner module headings

## A5 — Business rules

### RULE-MDL-001 — رفض نوع لوحدة غير مسجّلة / Reject a type for an unregistered owner module
Scope      : ENT-MDL-001
Trigger    : on create (lookup type)
Statement  : The system shall reject a lookup type registration whose owner module code has no ModuleRegistry row in SEC.
Message    : ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" · en: "The owning module is not registered in the Security module"
Traces     : REQ-MDL-002
Source     : lookup-module-plan-en.md §3

### RULE-MDL-002 — رفض رمز مكرر ضمن النوع / Reject a duplicate code within a type
Scope      : ENT-MDL-002
Trigger    : on create (lookup value)
Statement  : The system shall reject a lookup value whose code already exists under the same lookup type.
Message    : ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" · en: "This code is already used within this type"
Traces     : REQ-MDL-007
Source     : lookup-module-plan-en.md §6

### RULE-MDL-003 — عدم تغيير مفتاح النوع بعد إنشائه / Key immutability after creation
Scope      : ENT-MDL-001
Trigger    : on update (lookup type)
Statement  : The system shall prevent editing a lookup type's key after creation.
Message    : ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" · en: "A lookup type's key cannot be changed after creation"
Traces     : REQ-MDL-003
Source     : lookup-module-plan-en.md §3 (the key is what every consumer already cites)

### RULE-MDL-004 — استبعاد قيم النوع المعطّل / Exclude an inactive type's values from reads
Scope      : ENT-MDL-001
Trigger    : on evaluate (consumer read, REQ-MDL-011)
Statement  : While a lookup type is inactive, the system shall exclude its values from consumer reads.
Message    : ar: "هذا النوع معطّل حاليًا" · en: "This lookup type is currently inactive"
Traces     : REQ-MDL-004, REQ-MDL-011
Source     : lookup-module-plan-en.md §3

## A6 — Lookups
None — MDL introduces no domain-specific coded list of its own (it is the generic
mechanism every other module's lookup types run on top of; see module-registry-mdl.md →
LOOKUPS OWNED).

## A7 — Status lifecycle
`LookupType.isActiveFl` and `LookupValue.isActiveFl` are each a plain binary active flag
(≤2 states) — not applicable for a diagram.

## A8 — Module dependencies
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate (assigned by P2) |
|---|---|---|---|---|
| ModuleRegistry | ENT-SEC-004 | SEC | SOFT-READ | assigned by P2 (this module) |

| External service | Purpose | Integration kind |
|---|---|---|
None — lookup-module-plan-en.md §5 names Notifications/File Service as available but MDL's
PRD (US-MDL-001..005) states no need that would use either; not built this v1.

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-MDL-001 — اللوكبات العامة / Generic Lookups (master-detail, all lists)
### B1 — Definition
Purpose      : إدارة كل قوائم القيم المُرمَّزة عبر شاشة واحدة.
Entities     : ENT-MDL-001, ENT-MDL-002
Operations   : search, create, read, update, deactivate (type); create, read, search, update, deactivate, reorder (value)
Users        : مسؤول مخوَّل بصلاحية الشاشة (أي وحدة، حسب منحها من SEC)
Navigation   : MDL → Reference data → Generic Lookups
Content shape: header + repeating lines with totals — رئيسي (أنواع) + تفصيلي (قيم) قابل لإعادة الترتيب
Traces       : REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004, REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010
Composite    : Master (types) + Detail (values) = ONE screen requirement
### B2 — Search / list
Master filters: key(LIKE), ownerModuleCode(EXACT), isActiveFl(EXACT) — correspond to result columns.
Detail filters: code(LIKE) — corresponds to result column.
### B3 — Input
Master fields: key, ownerModuleCode, nameAr, nameEn (ENT-MDL-001). Detail fields: code,
nameAr, nameEn, sortOrder (drag-to-reorder), isActiveFl (ENT-MDL-002). Buttons: activate/
deactivate per row at both levels.
### B4 — Access
Page code: MDL_LOOKUPS. Actions: VIEW, CREATE, UPDATE, DELETE (deactivate), per §7.1
(gateway VIEW).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search types | GET | /api/v1/mdl/lookup-types | filters, paging | Page\<LookupType\> | — | REQ-MDL-001 |
| create type | POST | /api/v1/mdl/lookup-types | key, ownerModuleCode, nameAr, nameEn | LookupType | RULE-MDL-001 | REQ-MDL-001, REQ-MDL-002 |
| update type | PUT | /api/v1/mdl/lookup-types/{id} | nameAr, nameEn | LookupType | RULE-MDL-003 | REQ-MDL-003 |
| deactivate type | DELETE | /api/v1/mdl/lookup-types/{id} | id | confirmation | — | REQ-MDL-004 |
| search values | GET | /api/v1/mdl/lookup-types/{id}/values | filters, paging | Page\<LookupValue\> | — | REQ-MDL-005 |
| create value | POST | /api/v1/mdl/lookup-types/{id}/values | code, nameAr, nameEn, sortOrder | LookupValue | RULE-MDL-002 | REQ-MDL-006, REQ-MDL-007 |
| update value | PUT | /api/v1/mdl/lookup-values/{id} | nameAr, nameEn, sortOrder | LookupValue | — | REQ-MDL-008 |
| deactivate value | DELETE | /api/v1/mdl/lookup-values/{id} | id | confirmation | — | REQ-MDL-009 |
| reorder values | PATCH | /api/v1/mdl/lookup-types/{id}/values/reorder | ordered list of value ids | Page\<LookupValue\> | — | REQ-MDL-010 |

## SCR-REQ-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner
### B1 — Definition
Purpose      : تصفّح أنواع اللوكب مجمّعة حسب الوحدة المالكة.
Entities     : ENT-MDL-001
Operations   : search, read
Users        : مسؤول مخوَّل
Navigation   : MDL → Reference data → Type registry; from: SCR-REQ-MDL-001
Content shape: true hierarchy (parent/child) — وحدة مالكة → أنواعها
Traces       : REQ-MDL-013
Composite    : single screen (grouped list) = ONE screen requirement
### B2 — Search / list
Filters: ownerModuleCode(EXACT), key(LIKE) — correspond to result columns.
### B3 — Input
Read-only browse; no create/update here (management happens on SCR-REQ-MDL-001).
### B4 — Access
Page code: MDL_TYPE_REGISTRY. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| browse registry | GET | /api/v1/mdl/lookup-types/by-owner | filters | grouped Page\<LookupType\> | — | REQ-MDL-013 |
| read values by key (consumer API) | GET | /api/v1/mdl/lookups | type=key | List\<LookupValue\> (active only) | RULE-MDL-004 | REQ-MDL-011, REQ-MDL-012 |

# STANDALONE

## Traceability matrix
| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-MDL-001 | REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004 | AC-MDL-001…004 | RULE-MDL-001, RULE-MDL-003, RULE-MDL-004 | ENT-MDL-001 | SCR-REQ-MDL-001 |
| US-MDL-002 | REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010 | AC-MDL-005…010 | RULE-MDL-002 | ENT-MDL-001, ENT-MDL-002 | SCR-REQ-MDL-001 |
| US-MDL-003 | REQ-MDL-011, REQ-MDL-012 | AC-MDL-011, AC-MDL-012 | RULE-MDL-004 | ENT-MDL-001, ENT-MDL-002 | SCR-REQ-MDL-002 |
| US-MDL-004 | REQ-MDL-001, REQ-MDL-002 | AC-MDL-001, AC-MDL-002 | RULE-MDL-001 | ENT-MDL-001 | SCR-REQ-MDL-001 |
| US-MDL-005 | REQ-MDL-013 | AC-MDL-013 | — | ENT-MDL-001 | SCR-REQ-MDL-002 |

Every story traces to ≥1 REQ; every REQ traces to ≥1 AC; every RULE traces to a REQ; every
SCR-REQ traces to ≥1 REQ. No orphan, no dangling id.

## Decisions applied
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
No ADR was raised — no ambiguity reached the breaking/non-breaking fork of §9; the MDL→SEC
SOFT-READ classification was settled at P0 (module-registry-mdl.md → AUTO-DECISIONS), not
here, and every other point was settled by the plan directly.

## Access summary
| Page code | Screen | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|---|
| MDL_LOOKUPS | Generic Lookups | role-granted | role-granted | role-granted | role-granted (deactivate) |
| MDL_TYPE_REGISTRY | Type registry by owner | role-granted | — | — | — |
Every action beyond VIEW additionally requires VIEW on the same screen (platform gateway
convention, `profiles/erp.yaml → conventions.security_model.gateway_action`, applied the
same way SEC's own RULE-SEC-007 documents it — not restated as an MDL-owned RULE since it
is a platform-wide convention, not an MDL-specific constraint).
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: backend-execution-plan (MDL)>>>
# BACKEND EXECUTION PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Dialect : postgresql16
Framework : spring-boot-java (profile.stack.backend.framework)
Inputs : srs (v1, PRD-approved), db-script (v1), registry-srs (v1), registry-db (v1)
Open ADRs : 0
══════════════════════════════════════════════════════════════════

## PRE-GENERATION EXTRACTION — MDL v1 (working set; not part of the plan proper)

```
── FROM srs ──────────────────────────────────────────────────────────────
ENTITIES      2 — ENT-MDL-001 (master), ENT-MDL-002 (lookup)
REQUIREMENTS  13 — REQ-MDL-001..013, each with 1 AC-MDL-*
RULES         4 — RULE-MDL-001..004
SCREENS       2 — SCR-REQ-MDL-001..002, composite per profile.conventions.composite_screen
PERMISSIONS   MDL_LOOKUPS, MDL_TYPE_REGISTRY page codes + PERM_<PAGE_CODE>_<ACTION>, gateway VIEW
LOOKUPS       none owned by MDL itself (SRS A6)
BUSINESS CODE none — no MDL entity has a platform-numbered business code
── FROM db-script ────────────────────────────────────────────────────────
TABLES        2 — MDL_LOOKUP_TYPE, MDL_LOOKUP_VALUE
PK GENERATION every table: `GENERATED ALWAYS AS IDENTITY`
COLUMNS       21 DBF-MDL-001..021
CONSTRAINTS   PK_*, UQ_MDL_LOOKUP_TYPE_KEY, UQ_MDL_LOOKUP_VALUE_TYPE_CODE, FK_LOOKUP_VALUE_TYPE; INDEXES IDX_*
XM            1 — XM-MDL-001 SOFT-READ → SEC_MODULE_REG, status ACTIVE
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   ModuleRegistry (ENT-SEC-004, SEC) via XM-MDL-001
EXISTING LOOKUP KEYS        none reused (MDL is the mechanism, not a consumer of its own kind)
ID RANGES already used      API: none yet · QR: none yet
──────────────────────────────────────────────────────────────────────────
No row required §2A.3 extraction-failure handling.
```

## EXECUTION PLAN INDEX — MDL v1 — backend-execution-plan-mdl.md
Profile: erp · dialect: postgresql16 · framework: spring-boot-java
Open ADRs: 0

**ENTITY REGISTRY**
| ENT | Name | Table | Business code | Operations |
|---|---|---|---|---|
| ENT-MDL-001 | LookupType | MDL_LOOKUP_TYPE | none | create, read, search, update (name only), deactivate |
| ENT-MDL-002 | LookupValue | MDL_LOOKUP_VALUE | none | create, read, search, update, deactivate, reorder |

**FIELD REGISTRY**
| DBF | Property | Read-only | ENT |
|---|---|---|---|
| DBF-MDL-001 | lookupTypePk | Yes | ENT-MDL-001 |
| DBF-MDL-002 | key | create-only (immutable after, RULE-MDL-003) | ENT-MDL-001 |
| DBF-MDL-003 | ownerModuleCode | create-only | ENT-MDL-001 |
| DBF-MDL-004 | nameAr | No | ENT-MDL-001 |
| DBF-MDL-005 | nameEn | No | ENT-MDL-001 |
| DBF-MDL-006 | isActiveFl | Yes | ENT-MDL-001 |
| DBF-MDL-007 | createdBy | Yes | ENT-MDL-001 |
| DBF-MDL-008 | createdAt | Yes | ENT-MDL-001 |
| DBF-MDL-009 | updatedBy | Yes | ENT-MDL-001 |
| DBF-MDL-010 | updatedAt | Yes | ENT-MDL-001 |
| DBF-MDL-011 | lookupValuePk | Yes | ENT-MDL-002 |
| DBF-MDL-012 | lookupTypeId | create-only | ENT-MDL-002 |
| DBF-MDL-013 | code | create-only | ENT-MDL-002 |
| DBF-MDL-014 | nameAr | No | ENT-MDL-002 |
| DBF-MDL-015 | nameEn | No | ENT-MDL-002 |
| DBF-MDL-016 | sortOrder | No | ENT-MDL-002 |
| DBF-MDL-017 | isActiveFl | Yes | ENT-MDL-002 |
| DBF-MDL-018 | createdBy | Yes | ENT-MDL-002 |
| DBF-MDL-019 | createdAt | Yes | ENT-MDL-002 |
| DBF-MDL-020 | updatedBy | Yes | ENT-MDL-002 |
| DBF-MDL-021 | updatedAt | Yes | ENT-MDL-002 |

**API REGISTRY**
| API | Operation | Verb | Path | Traces (REQ, DBF) |
|---|---|---|---|---|
| API-MDL-001 | search types | GET | /api/v1/mdl/lookup-types | REQ-MDL-001 · DBF-MDL-002,003,004,005,006 |
| API-MDL-002 | create type | POST | /api/v1/mdl/lookup-types | REQ-MDL-001,REQ-MDL-002 · DBF-MDL-002,003,004,005 |
| API-MDL-003 | update type | PUT | /api/v1/mdl/lookup-types/{id} | REQ-MDL-003 · DBF-MDL-004,005 |
| API-MDL-004 | deactivate type | DELETE | /api/v1/mdl/lookup-types/{id} | REQ-MDL-004 · DBF-MDL-006 |
| API-MDL-005 | search values | GET | /api/v1/mdl/lookup-types/{id}/values | REQ-MDL-005 · DBF-MDL-012,013,014,015,016,017 |
| API-MDL-006 | create value | POST | /api/v1/mdl/lookup-types/{id}/values | REQ-MDL-006,REQ-MDL-007 · DBF-MDL-012,013,014,015,016 |
| API-MDL-007 | update value | PUT | /api/v1/mdl/lookup-values/{id} | REQ-MDL-008 · DBF-MDL-014,015,016 |
| API-MDL-008 | deactivate value | DELETE | /api/v1/mdl/lookup-values/{id} | REQ-MDL-009 · DBF-MDL-017 |
| API-MDL-009 | reorder values | PATCH | /api/v1/mdl/lookup-types/{id}/values/reorder | REQ-MDL-010 · DBF-MDL-016 |
| API-MDL-010 | browse registry by owner | GET | /api/v1/mdl/lookup-types/by-owner | REQ-MDL-013 · DBF-MDL-003,002,004,005 |
| API-MDL-011 | read values by key (consumer API) | GET | /api/v1/mdl/lookups | REQ-MDL-011,REQ-MDL-012 · DBF-MDL-002,013,014,015,016,006,017 |

**RULE REGISTRY**
| RULE | Name | Scope (ENT) | Message ar/en ✓ |
|---|---|---|---|
| RULE-MDL-001 | Reject a type for an unregistered owner module | ENT-MDL-001 | ✓ |
| RULE-MDL-002 | Reject a duplicate code within a type | ENT-MDL-002 | ✓ |
| RULE-MDL-003 | Key immutability after creation | ENT-MDL-001 | ✓ |
| RULE-MDL-004 | Exclude an inactive type's values from reads | ENT-MDL-001 | ✓ |

**SCREEN REGISTRY**
| Screen | Type | ENT | Permission names |
|---|---|---|---|
| MDL_LOOKUPS | secured | ENT-MDL-001, ENT-MDL-002 | PERM_MDL_LOOKUPS_VIEW, PERM_MDL_LOOKUPS_CREATE, PERM_MDL_LOOKUPS_UPDATE, PERM_MDL_LOOKUPS_DELETE |
| MDL_TYPE_REGISTRY | secured | ENT-MDL-001 | PERM_MDL_TYPE_REGISTRY_VIEW |

**LOOKUP REGISTRY** — none (MDL owns no lookup key of its own).

**QRC SUMMARY** — 15 QR ids, QR-MDL-001..015 — see Query Reference Catalog below.

**DB ALIGNMENT** — see manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 1 (XM-MDL-001, SOFT-READ → SEC, ACTIVE)
**SECURITY** — 2 secured screens, data-driven role grants (no fixed role count)

## DB Alignment Manifest — MDL v1
All 21 rows: **status ✓ (aligned)**; XM column populated only for the one field the
SOFT-READ touches (ownerModuleCode) — a SOFT-READ is an application-level read, not a
column-level FK, so it is noted, not blocking.

| DBF | ENT | property | type | XM |
|---|---|---|---|---|
| DBF-MDL-001 | ENT-MDL-001 | lookupTypePk | Long | — |
| DBF-MDL-002 | ENT-MDL-001 | key | String | — |
| DBF-MDL-003 | ENT-MDL-001 | ownerModuleCode | String | XM-MDL-001 (validated, not FK-constrained) |
| DBF-MDL-004 | ENT-MDL-001 | nameAr | String | — |
| DBF-MDL-005 | ENT-MDL-001 | nameEn | String | — |
| DBF-MDL-006 | ENT-MDL-001 | isActiveFl | Boolean | — |
| DBF-MDL-007 | ENT-MDL-001 | createdBy | String | — |
| DBF-MDL-008 | ENT-MDL-001 | createdAt | Instant | — |
| DBF-MDL-009 | ENT-MDL-001 | updatedBy | String | — |
| DBF-MDL-010 | ENT-MDL-001 | updatedAt | Instant | — |
| DBF-MDL-011 | ENT-MDL-002 | lookupValuePk | Long | — |
| DBF-MDL-012 | ENT-MDL-002 | lookupTypeId | Long | — |
| DBF-MDL-013 | ENT-MDL-002 | code | String | — |
| DBF-MDL-014 | ENT-MDL-002 | nameAr | String | — |
| DBF-MDL-015 | ENT-MDL-002 | nameEn | String | — |
| DBF-MDL-016 | ENT-MDL-002 | sortOrder | Integer | — |
| DBF-MDL-017 | ENT-MDL-002 | isActiveFl | Boolean | — |
| DBF-MDL-018 | ENT-MDL-002 | createdBy | String | — |
| DBF-MDL-019 | ENT-MDL-002 | createdAt | Instant | — |
| DBF-MDL-020 | ENT-MDL-002 | updatedBy | String | — |
| DBF-MDL-021 | ENT-MDL-002 | updatedAt | Instant | — |

## Query Reference Catalog (QR-MDL-*)

> Logical specification only — never executable code.

| QR | Operation | Phase | API | Entity | Kind | Intent |
|---|---|---|---|---|---|---|
| QR-MDL-001 | FIND_BY_CRITERIA | SVC-API | API-MDL-001 | ENT-MDL-001 | FIND_BY_CRITERIA | search lookup types |
| QR-MDL-002 | SAVE | SVC-API | API-MDL-002 | ENT-MDL-001 | SAVE | create lookup type |
| QR-MDL-003 | UPDATE | SVC-API | API-MDL-003 | ENT-MDL-001 | UPDATE | rename lookup type |
| QR-MDL-004 | UPDATE | SVC-API | API-MDL-004 | ENT-MDL-001 | UPDATE | deactivate lookup type |
| QR-MDL-005 | FIND_BY_CRITERIA | SVC-API | API-MDL-005 | ENT-MDL-002 | FIND_BY_CRITERIA | search values of a type |
| QR-MDL-006 | SAVE | SVC-API | API-MDL-006 | ENT-MDL-002 | SAVE | create lookup value |
| QR-MDL-007 | UPDATE | SVC-API | API-MDL-007 | ENT-MDL-002 | UPDATE | update lookup value |
| QR-MDL-008 | UPDATE | SVC-API | API-MDL-008 | ENT-MDL-002 | UPDATE | deactivate lookup value |
| QR-MDL-009 | UPDATE | SVC-API | API-MDL-009 | ENT-MDL-002 | UPDATE (batch) | persist new sortOrder per reordered value |
| QR-MDL-010 | FIND_BY_CRITERIA | SVC-API | API-MDL-010 | ENT-MDL-001 | FIND_BY_CRITERIA | browse types grouped by ownerModuleCode |
| QR-MDL-011 | FIND_BY_CRITERIA | SVC-API | API-MDL-011 | ENT-MDL-001, ENT-MDL-002 | FIND_BY_CRITERIA | active values of an active type, by key, ordered by sortOrder |
| QR-MDL-012 | EXISTS | SVC-API | API-MDL-002 | (SEC_MODULE_REG, cross-module) | EXISTS | XM-MDL-001 / RULE-MDL-001: owner module registered in SEC? |
| QR-MDL-013 | EXISTS | SVC-API | API-MDL-002 | ENT-MDL-001 | EXISTS | uniqueness: key |
| QR-MDL-014 | EXISTS | SVC-API | API-MDL-006 | ENT-MDL-002 | EXISTS | RULE-MDL-002: code unique within lookupTypeId (also DB UQ) |
| QR-MDL-015 | FIND_ONE | SVC-API | API-MDL-011 | ENT-MDL-001 | FIND_ONE | RULE-MDL-004: resolve type by key and confirm isActiveFl=true |

Standard operation defaults (SEC's Phase 1 CORE table applies verbatim, restated once in
Phase 1 below rather than duplicated per QR). Join governance: QR-MDL-011 joins
MDL_LOOKUP_TYPE → MDL_LOOKUP_VALUE (intra-module, both owned here) to filter by the type's
own `isActiveFl` and `key` — never joins to resolve a lookup LABEL for a consumer (the
consumer receives code+labels directly, since these ARE the labels, not a foreign lookup).
QR-MDL-012 is the module's one cross-module read (XM-MDL-001, SOFT-READ, no join — a
separate query against SEC's table, reconciled in the service layer, not a SQL JOIN across
schemas).

---

<!-- PHASE:CORE:START traces=REQ-MDL-002 -->
## PHASE 1 — CORE

**Layers**: controller → service → mapper → domain → repository (same as every module,
`profile.stack.backend.layers`). Domain-behaviour placement: entity methods for
single-entity invariants (e.g. `LookupType.deactivate()`); service layer for anything
spanning more than one entity or a cross-module read (RULE-MDL-001 via XM-MDL-001,
RULE-MDL-004's join, RULE-MDL-002's pre-check even though it is also DB-enforced).

**Error signalling**: `LocalizedException → {code, messageAr, messageEn}`; runtime code
format `MDL-<3-digit>` (module-scoped, same convention as SEC's `SEC-<3-digit>`).

**Transaction scope**: `READ_ONLY` for every `FIND_*`/`EXISTS` QR; `READ_WRITE` for every
`SAVE`/`UPDATE` QR (including the batch reorder, QR-MDL-009, in one transaction).

**Search contract**: `{filters, page, size, sort}`, `Page<T>`, empty result = success.

**Audit fields**: `createdBy/createdAt/updatedBy/updatedAt` framework-filled, never in a
request DTO.

**Type mapping** (postgresql16 → Java):
| postgresql16 | Java |
|---|---|
| GENERATED ALWAYS AS IDENTITY | Long |
| VARCHAR(n) | String |
| BOOLEAN | Boolean |
| TIMESTAMPTZ | Instant |
| NUMERIC (bare, `sort_order` only) | Integer — governance note: `sort_order` is a whole-number ordering field, not a monetary/precision decimal; the profile's `decimal` syntax-map row (`NUMERIC(p,s)`) does not fit a bare `NUMERIC` column, so this module maps it to `Integer` explicitly (deviation stated once here, per P2 engine §4.1) |

**Lookup values**: not applicable in the usual sense — MDL IS the lookup mechanism; its own
`ownerModuleCode` field is validated against SEC's `ModuleRegistry` (XM-MDL-001), not
against another lookup type.

**Numbering**: not applicable — no MDL entity has a business code.

**Workflow engine**: forbidden — not used.

**Languages**: every name field (`nameAr`/`nameEn`) and catalog message present in ar + en.

**Cross-module contract placement**: MDL's one cross-module read (XM-MDL-001) is a plain
outbound call from the service layer (`SecModuleRegistryClient` or an equivalent
inversion-of-control interface implemented against SEC's `GET /api/v1/sec/registry`
search endpoint, filtered by `code`) — not a physical join, not a shared transaction.

**Cross-cutting authorization**: the same CORE interceptor mechanism SEC's own plan
declares (SEC's backend-execution-plan-sec.md → Phase 1 CORE) applies platform-wide; MDL
does not redeclare it, only cites it — every secured MDL endpoint below is gated by it
before its controller method runs.
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=REQ-MDL-001,REQ-MDL-006 -->
## PHASE 2 — DATA-DOM

Entity count is 2 — below the engine's self-check split threshold; no SUB is opened, both
entities are written flat in profile.vocabulary order (LookupType first, as the master).

#### ENT-MDL-001 — LookupType      kind: master
BINDINGS: table `MDL_LOOKUP_TYPE` · PK `lookupTypePk` (DBF-MDL-001) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none (§3.3 test: no)
DEFAULT FIELDS (profile.conventions.entity_defaults.master): nameAr, nameEn, code, isActiveFl,
createdBy, createdAt, updatedBy, updatedAt — here `key` plays the role of `code` (SRS A3 note); `ownerModuleCode` is an addition beyond the default set, required by the plan's namespacing rule (POL-MDL-002).
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-MDL-001 | lookupTypePk | lookup_type_pk | Long | NOT NULL | Yes | PK_MDL_LOOKUP_TYPE | معرّف نوع اللوكب / LookupType id |
| DBF-MDL-002 | key | key | String | NOT NULL | create-only | UQ_MDL_LOOKUP_TYPE_KEY | المفتاح / Key |
| DBF-MDL-003 | ownerModuleCode | owner_module_code | String | NOT NULL | create-only | — (XM-MDL-001 app-level check) | رمز الوحدة المالكة / Owner module code |
| DBF-MDL-004 | nameAr | name_ar | String | NOT NULL | No | — | الاسم (عربي) / Name (Arabic) |
| DBF-MDL-005 | nameEn | name_en | String | NOT NULL | No | — | الاسم (إنجليزي) / Name (English) |
| DBF-MDL-006 | isActiveFl | is_active_fl | Boolean | NOT NULL | Yes | — | نشط / Active |
| DBF-MDL-007..010 | createdBy/createdAt/updatedBy/updatedAt | created_by/… | String/Instant | see db-script | Yes | — | audit |
DTO MEMBERSHIP: create-request `{key, ownerModuleCode, nameAr, nameEn}`; update-request `{nameAr, nameEn}` only (key and ownerModuleCode immutable — RULE-MDL-003); response includes all.
LOOKUP FIELDS: none (LookupType is not itself lookup-backed).
DOMAIN RULES:
**RULE-MDL-001** — Scope ENT-MDL-001 · Trigger: on create · Statement: "The system shall reject a lookup type registration whose owner module code has no ModuleRegistry row in SEC." · Message ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" / en: "The owning module is not registered in the Security module" · DB enforcement: application layer (service, via QR-MDL-012, XM-MDL-001) · owner layer: service.
**RULE-MDL-003** — Scope ENT-MDL-001 · Trigger: on update · Statement: "The system shall prevent editing a lookup type's key after creation." · Message ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" / en: "A lookup type's key cannot be changed after creation" · DB enforcement: application layer (enforced by omission — `key` is absent from the update DTO entirely) · owner layer: service/controller (DTO shape).
**RULE-MDL-004** — Scope ENT-MDL-001 · Trigger: on evaluate (consumer read, API-MDL-011) · Statement: "While a lookup type is inactive, the system shall exclude its values from consumer reads." · Message ar: "هذا النوع معطّل حاليًا" / en: "This lookup type is currently inactive" · DB enforcement: application layer (service, via QR-MDL-015 + QR-MDL-011's join filter) · owner layer: service.
STATE MACHINE: `isActiveFl` binary only — not applicable (SRS A7).
CROSS-MODULE: XM-MDL-001 (SOFT-READ → SEC_MODULE_REG, status ACTIVE) touches `ownerModuleCode`.
REPOSITORY OPS → QR-MDL-001 (FIND_BY_CRITERIA), QR-MDL-002 (SAVE), QR-MDL-003 (UPDATE), QR-MDL-004 (UPDATE, deactivate), QR-MDL-010 (FIND_BY_CRITERIA, grouped), QR-MDL-012 (EXISTS, cross-module), QR-MDL-013 (EXISTS, uniqueness), QR-MDL-015 (FIND_ONE, by key).

#### ENT-MDL-002 — LookupValue      kind: lookup
BINDINGS: table `MDL_LOOKUP_VALUE` · PK `lookupValuePk` (DBF-MDL-011) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
DEFAULT FIELDS (profile.conventions.entity_defaults.lookup): code, nameAr, nameEn, sortOrder, isActiveFl — matched exactly, plus PK/FK/audit.
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-MDL-011 | lookupValuePk | lookup_value_pk | Long | NOT NULL | Yes | PK_MDL_LOOKUP_VALUE | معرّف قيمة اللوكب / LookupValue id |
| DBF-MDL-012 | lookupTypeId | lookup_type_id | Long | NOT NULL | create-only | FK_LOOKUP_VALUE_TYPE | نوع اللوكب / Lookup type |
| DBF-MDL-013 | code | code | String | NOT NULL | create-only | UQ_MDL_LOOKUP_VALUE_TYPE_CODE | الرمز / Code |
| DBF-MDL-014 | nameAr | name_ar | String | NOT NULL | No | — | الاسم (عربي) / Name (Arabic) |
| DBF-MDL-015 | nameEn | name_en | String | NOT NULL | No | — | الاسم (إنجليزي) / Name (English) |
| DBF-MDL-016 | sortOrder | sort_order | Integer | NOT NULL | No | — | ترتيب العرض / Sort order |
| DBF-MDL-017 | isActiveFl | is_active_fl | Boolean | NOT NULL | Yes | — | نشط / Active |
| DBF-MDL-018..021 | createdBy/createdAt/updatedBy/updatedAt | … | — | see db-script | Yes | — | audit |
DTO MEMBERSHIP: create-request `{lookupTypeId, code, nameAr, nameEn, sortOrder}`; update-request `{nameAr, nameEn, sortOrder}` (lookupTypeId, code immutable); response includes all.
LOOKUP FIELDS: none — LookupValue rows are themselves the values other modules resolve; they hold no lookup-backed field of their own.
DOMAIN RULES: **RULE-MDL-002** — Scope ENT-MDL-002 · Trigger: on create · Statement: "The system shall reject a lookup value whose code already exists under the same lookup type." · Message ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" / en: "This code is already used within this type" · DB enforcement: `UQ_MDL_LOOKUP_VALUE_TYPE_CODE` (structural) + service pre-check (QR-MDL-014, friendly error before the DB would reject it) · owner layer: service + database.
STATE MACHINE: `isActiveFl` binary only — not applicable.
CROSS-MODULE: none.
REPOSITORY OPS → QR-MDL-005 (FIND_BY_CRITERIA), QR-MDL-006 (SAVE), QR-MDL-007 (UPDATE), QR-MDL-008 (UPDATE, deactivate), QR-MDL-009 (UPDATE batch, reorder), QR-MDL-011 (FIND_BY_CRITERIA, consumer read), QR-MDL-014 (EXISTS, uniqueness).
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-MDL-001,REQ-MDL-006,REQ-MDL-011 -->
## PHASE 3 — SVC-API

API count = 11 ≥ 8 → split by threshold. Only two of the three standard groups are
populated (no MDL endpoint is "INT"-shaped in the SEC sense — no auth flow, no onboarding
registration, no export); `SVC-API-INT` is therefore omitted rather than opened empty,
consistent with engine §6.2 ("Content: the roles whose words appear... otherwise as the
profile describes this phase" — an empty SUB with no atoms would violate "every atom then
sits inside a SUB — no orphan atoms beside SUBs" trivially, since there would be none to
place; omitting an unneeded SUB is the correct reading, not a violation).

<!-- SUB:SVC-API-SEARCH:START traces=REQ-MDL-001,REQ-MDL-005,REQ-MDL-011,REQ-MDL-013 -->
### SUB — SVC-API-SEARCH (read-only)

<!-- API:API-MDL-001:START traces=REQ-MDL-001,DBF-MDL-002,DBF-MDL-003,DBF-MDL-004,DBF-MDL-005,DBF-MDL-006 -->
### API-MDL-001 — search lookup types
Endpoint     : GET /api/v1/mdl/lookup-types
Layers       : controller → `LookupTypeController.search` ; service → `LookupTypeService.search`
Request      : query params `key`(LIKE), `ownerModuleCode`(EXACT), `isActiveFl`(EXACT), `page`, `size`, `sort`
Response     : 200 · `Page<LookupTypeResponse>` · `ApiResponse<Page<LookupTypeResponse>>`
Validations  : none (read-only)
Errors       : `MDL-500` only
Orchestration: load (QR-MDL-001) → map → return
Repository   : QR-MDL-001 · join NONE · transaction READ_ONLY
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_VIEW`
Localization : nameAr/nameEn returned
<!-- API:API-MDL-001:END -->

<!-- API:API-MDL-005:START traces=REQ-MDL-005,DBF-MDL-012,DBF-MDL-013,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016,DBF-MDL-017 -->
### API-MDL-005 — search values of a type
Endpoint     : GET /api/v1/mdl/lookup-types/{id}/values
Layers       : controller → `LookupValueController.search` ; service → `LookupValueService.search`
Request      : path `id` (lookupTypeId); query params `code`(LIKE), `page`, `size`, `sort` (default sort = sortOrder)
Response     : 200 · `Page<LookupValueResponse>` · `ApiResponse<Page<LookupValueResponse>>`
Validations  : none
Errors       : `MDL-404-TYPE` (404, unknown id)
Orchestration: load (QR-MDL-005) → map → return
Repository   : QR-MDL-005 · join NONE · transaction READ_ONLY
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_VIEW`
Localization : nameAr/nameEn returned
<!-- API:API-MDL-005:END -->

<!-- API:API-MDL-010:START traces=REQ-MDL-013,DBF-MDL-003,DBF-MDL-002,DBF-MDL-004,DBF-MDL-005 -->
### API-MDL-010 — browse registry by owner
Endpoint     : GET /api/v1/mdl/lookup-types/by-owner
Layers       : controller → `LookupTypeController.browseByOwner` ; service → `LookupTypeService.browseByOwner`
Request      : query params `ownerModuleCode`(EXACT), `key`(LIKE)
Response     : 200 · `List<OwnerGroupResponse>` (ownerModuleCode → nested active LookupType list) · `ApiResponse<List<OwnerGroupResponse>>`
Validations  : none
Errors       : `MDL-500` only
Orchestration: load grouped (QR-MDL-010) → assemble → return
Repository   : QR-MDL-010 · join NONE (single-table, grouped in the service layer) · transaction READ_ONLY
Security     : screen MDL_TYPE_REGISTRY · permission `PERM_MDL_TYPE_REGISTRY_VIEW`
Localization : nameAr/nameEn per type
<!-- API:API-MDL-010:END -->

<!-- API:API-MDL-011:START traces=REQ-MDL-011,REQ-MDL-012,DBF-MDL-002,DBF-MDL-013,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016 -->
### API-MDL-011 — read values by key (consumer API)
Endpoint     : GET /api/v1/mdl/lookups
Layers       : controller → `LookupConsumerController.readByKey` ; service → `LookupConsumerService.readByKey`
Request      : query param `type` (the LookupType key, e.g. `PAYMENT_METHOD`)
Response     : 200 · `List<LookupValueResponse>` (active values only, ordered by sortOrder) — 404 if the key itself is unknown
Validations  : RULE-MDL-004 (full text: DATA-DOM §ENT-MDL-001) — resolve the type, confirm it is active, then return only its active values (REQ-MDL-012: unknown key → not-found, not empty success)
Errors       : `MDL-404-TYPE-KEY` (404)
Orchestration: resolve type by key (QR-MDL-015) → if not found: 404 → else: load its active values ordered by sortOrder (QR-MDL-011) → return (empty list is a valid success if the type is active but has zero active values, per the FIND_BY_CRITERIA default)
Repository   : QR-MDL-015, QR-MDL-011 · join intra-module (type → value, both owned by MDL) · transaction READ_ONLY
Security     : called by other modules' backends, not an end-user screen — gated the same as any secured API (permission `PERM_MDL_LOOKUPS_VIEW`, granted to the calling module's own service principal per the platform's module-to-module auth pattern, same mechanism as any other authenticated caller — no special "system" bypass)
Localization : nameAr/nameEn returned per value
<!-- API:API-MDL-011:END -->
<!-- SUB:SVC-API-SEARCH:END -->

<!-- SUB:SVC-API-CRUD:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010 -->
### SUB — SVC-API-CRUD

<!-- API:API-MDL-002:START traces=REQ-MDL-001,REQ-MDL-002,DBF-MDL-002,DBF-MDL-003,DBF-MDL-004,DBF-MDL-005 -->
### API-MDL-002 — create lookup type
Endpoint     : POST /api/v1/mdl/lookup-types
Layers       : controller → `LookupTypeController.create` ; service → `LookupTypeService.create`
Request      : body `{key, ownerModuleCode, nameAr, nameEn}` — excludes {lookupTypePk, isActiveFl, audit}
Response     : 201 · `LookupTypeResponse`
Validations  : RULE-MDL-001 (full text: DATA-DOM §ENT-MDL-001) — owner module must be registered in SEC (QR-MDL-012); uniqueness of key (QR-MDL-013)
Errors       : `MDL-409-MODULE-NOT-REGISTERED` (409), `MDL-409-TYPE-DUP` (409)
Orchestration: check RULE-MDL-001 via XM-MDL-001 (QR-MDL-012) → validate key uniqueness (QR-MDL-013) → persist (QR-MDL-002) → return
Repository   : QR-MDL-002, QR-MDL-012, QR-MDL-013 · join NONE (QR-MDL-012 is a separate cross-module call, not a SQL join) · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_CREATE`
Localization : nameAr/nameEn required
<!-- API:API-MDL-002:END -->

<!-- API:API-MDL-003:START traces=REQ-MDL-003,DBF-MDL-004,DBF-MDL-005 -->
### API-MDL-003 — update lookup type (name only)
Endpoint     : PUT /api/v1/mdl/lookup-types/{id}
Layers       : controller → `LookupTypeController.update` ; service → `LookupTypeService.update`
Request      : body `{nameAr, nameEn}` — excludes {lookupTypePk, key, ownerModuleCode, isActiveFl, audit}
Response     : 200 · `LookupTypeResponse`
Validations  : RULE-MDL-003 (full text: DATA-DOM §ENT-MDL-001) — enforced by DTO shape (key absent from the request)
Errors       : `MDL-404-TYPE` (404)
Orchestration: load → update names (QR-MDL-003) → return
Repository   : QR-MDL-003 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : both name fields updatable
<!-- API:API-MDL-003:END -->

<!-- API:API-MDL-004:START traces=REQ-MDL-004,DBF-MDL-006 -->
### API-MDL-004 — deactivate lookup type
Endpoint     : DELETE /api/v1/mdl/lookup-types/{id}
Layers       : controller → `LookupTypeController.deactivate` ; service → `LookupTypeService.deactivate`
Request      : path `id`
Response     : 200 · confirmation `{lookupTypePk, isActiveFl: false}`
Validations  : none beyond existence
Errors       : `MDL-404-TYPE` (404)
Orchestration: load → `LookupType.deactivate()` → persist (QR-MDL-004) → (RULE-MDL-004 then applies automatically at the next API-MDL-011 read — no cascade write to values needed, since the exclusion is a read-time join filter, not a stored flag on each value)
Repository   : QR-MDL-004 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : n/a
<!-- API:API-MDL-004:END -->

<!-- API:API-MDL-006:START traces=REQ-MDL-006,REQ-MDL-007,DBF-MDL-012,DBF-MDL-013,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016 -->
### API-MDL-006 — create lookup value
Endpoint     : POST /api/v1/mdl/lookup-types/{id}/values
Layers       : controller → `LookupValueController.create` ; service → `LookupValueService.create`
Request      : path `id` (lookupTypeId); body `{code, nameAr, nameEn, sortOrder}` — excludes {lookupValuePk, isActiveFl, audit}
Response     : 201 · `LookupValueResponse`
Validations  : RULE-MDL-002 (full text: DATA-DOM §ENT-MDL-002) — code unique within the type (QR-MDL-014)
Errors       : `MDL-409-VALUE-DUP` (409), `MDL-404-TYPE` (404)
Orchestration: validate type exists → check RULE-MDL-002 (QR-MDL-014) → persist (QR-MDL-006) → return
Repository   : QR-MDL-006, QR-MDL-014 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_CREATE`
Localization : nameAr/nameEn required
<!-- API:API-MDL-006:END -->

<!-- API:API-MDL-007:START traces=REQ-MDL-008,DBF-MDL-014,DBF-MDL-015,DBF-MDL-016 -->
### API-MDL-007 — update lookup value
Endpoint     : PUT /api/v1/mdl/lookup-values/{id}
Layers       : controller → `LookupValueController.update` ; service → `LookupValueService.update`
Request      : body `{nameAr, nameEn, sortOrder}` — excludes {lookupValuePk, lookupTypeId, code, isActiveFl, audit}
Response     : 200 · `LookupValueResponse`
Validations  : none beyond existence
Errors       : `MDL-404-VALUE` (404)
Orchestration: load → update (QR-MDL-007) → return
Repository   : QR-MDL-007 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : both name fields updatable
<!-- API:API-MDL-007:END -->

<!-- API:API-MDL-008:START traces=REQ-MDL-009,DBF-MDL-017 -->
### API-MDL-008 — deactivate lookup value
Endpoint     : DELETE /api/v1/mdl/lookup-values/{id}
Layers       : controller → `LookupValueController.deactivate` ; service → `LookupValueService.deactivate`
Request      : path `id`
Response     : 200 · confirmation `{lookupValuePk, isActiveFl: false}`
Validations  : none beyond existence
Errors       : `MDL-404-VALUE` (404)
Orchestration: load → `LookupValue.deactivate()` → persist (QR-MDL-008) → return
Repository   : QR-MDL-008 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : n/a
<!-- API:API-MDL-008:END -->

<!-- API:API-MDL-009:START traces=REQ-MDL-010,DBF-MDL-016 -->
### API-MDL-009 — reorder lookup values
Endpoint     : PATCH /api/v1/mdl/lookup-types/{id}/values/reorder
Layers       : controller → `LookupValueController.reorder` ; service → `LookupValueService.reorder`
Request      : path `id` (lookupTypeId); body `{orderedValueIds: [Long]}`
Response     : 200 · `List<LookupValueResponse>` in the new order
Validations  : every id in `orderedValueIds` must belong to the given lookupTypeId
Errors       : `MDL-400-REORDER-MISMATCH` (400)
Orchestration: validate membership → assign sortOrder = list position for each id → persist (QR-MDL-009, batch update, one transaction) → return
Repository   : QR-MDL-009 · join NONE · transaction READ_WRITE
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_UPDATE`
Localization : n/a
<!-- API:API-MDL-009:END -->
<!-- SUB:SVC-API-CRUD:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-MDL-011 -->
## PHASE 4 — DOC

**API contract summary** (backend self-check only; the frontend stage binds to the real
`api-docs-mdl.md` published after implementation):

| API | Path | Verb | Request DTO | Response DTO | Stability |
|---|---|---|---|---|---|
| API-MDL-001 | /lookup-types | GET | (query params) | Page\<LookupTypeResponse\> | v1 |
| API-MDL-002 | /lookup-types | POST | LookupTypeCreateRequest | LookupTypeResponse | v1 |
| API-MDL-003 | /lookup-types/{id} | PUT | LookupTypeUpdateRequest | LookupTypeResponse | v1 |
| API-MDL-004 | /lookup-types/{id} | DELETE | — | DeactivateConfirmation | v1 |
| API-MDL-005 | /lookup-types/{id}/values | GET | (query params) | Page\<LookupValueResponse\> | v1 |
| API-MDL-006 | /lookup-types/{id}/values | POST | LookupValueCreateRequest | LookupValueResponse | v1 |
| API-MDL-007 | /lookup-values/{id} | PUT | LookupValueUpdateRequest | LookupValueResponse | v1 |
| API-MDL-008 | /lookup-values/{id} | DELETE | — | DeactivateConfirmation | v1 |
| API-MDL-009 | /lookup-types/{id}/values/reorder | PATCH | ReorderRequest | List\<LookupValueResponse\> | v1 |
| API-MDL-010 | /lookup-types/by-owner | GET | (query params) | List\<OwnerGroupResponse\> | v1 |
| API-MDL-011 | /lookups | GET | (query param `type`) | List\<LookupValueResponse\> | v1 |
(paths relative to `/api/v1/mdl`)

**DTO typing constraints**: `ownerModuleCode` is `String` (the platform module code, not
an enum); no business code field exists.

**Pagination + filter standard**: same as every module (Phase 1 CORE).
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=REQ-MDL-002 -->
## PHASE 5 — INT-C (cross-module consume)

One `XM-*` row, below the split threshold (1 < 5) — no SUB opened.

<!-- XM:XM-MDL-001:START traces=REQ-MDL-002 -->
### XM-MDL-001 — validate owner module against SEC
Target        : SEC · ENT-SEC-004 (ModuleRegistry) · classification SOFT-READ
Interface     : REST call — `GET /api/v1/sec/registry?moduleCode={code}` (an instance of `/api/v1/{module}/{resource}` on SEC, per API-SEC-021's search-registry contract)
Contract      : data required = the module code exists and `isActiveFl=true`; fallback if absent = reject with `MDL-409-MODULE-NOT-REGISTERED` (RULE-MDL-001); retry = none (synchronous, user-facing call — a transient SEC outage surfaces as `MDL-503` per the platform-standard infrastructure row, not a silent pass); idempotency = the call is read-only, naturally idempotent
Blocks        : none DEFERRED — SEC v1 is already gated (pass-1 APPROVE); this XM is ACTIVE from the moment MDL v1 is created, never DEFERRED
<!-- XM:XM-MDL-001:END -->
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-MDL-002 -->
## PHASE 6 — INT-R (cross-module resolve)

| XM | Status | Workaround (if not READY/ACTIVE) |
|---|---|---|
| XM-MDL-001 | ACTIVE | not applicable — target already gated |

No DEFERRED row exists this module; no mock/simulated strategy is needed. Inbound
dependency stub: any future consumer of MDL itself (every module from PRC onward, and FIN
next) reaches `ENT-MDL-001`/`ENT-MDL-002` through API-MDL-011 exactly as SEC's own consumers
reach SEC — `XM-INBOUND-STUB-2` (first expected consumer: FIN, per GENERATION-
INSTRUCTIONS.md §3), formal id assigned by FIN's own P2.
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=REQ-MDL-001 -->
## PHASE 7 — SEC-BE (security, backend half)

| Screen (page code) | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|
| MDL_LOOKUPS | PERM_MDL_LOOKUPS_VIEW (API-MDL-001, 005, 011) | PERM_MDL_LOOKUPS_CREATE (API-MDL-002, 006) | PERM_MDL_LOOKUPS_UPDATE (API-MDL-003, 004, 007, 008, 009) | (deactivate only, modeled as UPDATE — no hard-delete endpoint exists) |
| MDL_TYPE_REGISTRY | PERM_MDL_TYPE_REGISTRY_VIEW (API-MDL-010) | — | — | — |

**Seed data**: 2 SEC_PAGES rows (MDL_LOOKUPS, MDL_TYPE_REGISTRY) registered into SEC via SEC's own screen-registration endpoint (MDL is a consuming module registering itself, exactly the pattern security-module-plan-en.md §7 describes); action rows VIEW/CREATE/UPDATE per secured screen via SEC's own action-registration endpoint, following `PERM_<PAGE_CODE>_<ACTION>`.

**Gateway**: every non-VIEW permission requires VIEW on the same screen first (platform
convention, enforced by SEC's own CORE interceptor — not restated as an MDL-owned RULE).

**Forbidden responses**: `MDL` endpoints reuse the same `LocalizedException` envelope; a
403 from the interceptor is not module-specific (see SEC's `SEC-403-FORBIDDEN` — the same
mechanism denies MDL requests, this module mints no separate forbidden code).
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-MDL-011 -->
## PHASE 8 — ALIGN-BE

See Alignment self-check (ALIGN) below.
<!-- PHASE:ALIGN-BE:END -->

## Error Catalog — MDL v1

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `MDL-<3-digit>`.

| code | RULE / PLATFORM-STD | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| MDL-409-MODULE-NOT-REGISTERED | RULE-MDL-001 | API-MDL-002 | 409 | owner module not in SEC's ModuleRegistry | الوحدة المالكة غير مسجّلة في وحدة الأمان | The owning module is not registered in the Security module |
| MDL-409-TYPE-DUP | PLATFORM-STD (uniqueness, ADR-SEC-002 convention reused) | API-MDL-002 | 409 | duplicate key | هذا المفتاح مستخدم بالفعل | This key is already in use |
| MDL-404-TYPE | PLATFORM-STD (not found) | API-MDL-003, 004, 005 | 404 | unknown lookup type id | نوع اللوكب غير موجود | Lookup type not found |
| MDL-409-VALUE-DUP | RULE-MDL-002 | API-MDL-006 | 409 | duplicate code within type | هذا الرمز مستخدم بالفعل ضمن هذا النوع | This code is already used within this type |
| MDL-404-VALUE | PLATFORM-STD (not found) | API-MDL-007, 008 | 404 | unknown lookup value id | قيمة اللوكب غير موجودة | Lookup value not found |
| MDL-400-REORDER-MISMATCH | PLATFORM-STD (referential) | API-MDL-009 | 400 | reordered id not under the given type | إحدى القيم لا تنتمي لهذا النوع | One of the values does not belong to this type |
| MDL-404-TYPE-KEY | RULE-MDL-004 | API-MDL-011 | 404 | unknown or inactive type key | مفتاح النوع غير موجود أو غير نشط | This lookup type key does not exist or is inactive |
| MDL-403-FORBIDDEN | PLATFORM-STD (SEC's CORE interceptor) | every secured API | 403 | missing permission | غير مصرح بهذا الإجراء | You are not authorized to perform this action |
| MDL-503 | PLATFORM-STD (infrastructure) | API-MDL-002 | 503 | SEC unreachable during XM-MDL-001's validation call | تعذّر التحقق من الوحدة المالكة مؤقتًا | Could not verify the owning module right now |
| MDL-500 | PLATFORM-STD (infrastructure) | any | 500 | unhandled server error | حدث خطأ في الخادم | A server error occurred |

Every PLATFORM-STD row here follows the same umbrella convention SEC's ADR-SEC-002
established; MDL does not raise a new ADR for it (it cites SEC's, consistent with that
ADR's own consequence: "A future module's own P3.1 may cite the same PLATFORM-STD
convention... without re-deriving this decision").

## Alignment self-check (ALIGN) — MDL v1

```
TRACEABILITY      ✓ every API-*/QR-*/RULE-*/DBF-*/XM-* used in a phase appears in the Plan Index; every PHASE/SUB/atom carries traces=; every traces target exists upstream
BINDING (§2A)     ✓ no placeholder; every column cites a DBF; every RULE message present in ar+en; business code: none applicable
MANIFEST (§4)     ✓ only the mandated columns; all 21 DBF listed; the 1 XM-touched field (ownerModuleCode) is noted, not ⏸ (SOFT-READ is never blocking)
QRC (§5)          ✓ every API with a DB operation has ≥1 QR; no join for a lookup label; exact generation object named (Phase 1 CORE)
API (R3)          ✓ every RULE in a Validations line has a catalog row; platform errors carry RULE=PLATFORM-STD (citing SEC's ADR-SEC-002 convention); create/update requests exclude PK/audit/immutable fields
CROSS-MODULE      ✓ 1 XM from db-script, 1 placed (XM-MDL-001), 0 mismatched; ACTIVE status correctly reflects SEC's already-gated state; inbound stub uses XM-INBOUND-STUB-2 notation
SECURITY (R7)     ✓ both secured APIs' screens declare PERM_*; ERP-4 (every mutation endpoint declares its PERM_*): checked — every POST/PUT/PATCH/DELETE API above states one
CORE (R1)         ✓ layers, domain placement, error signalling (`MDL-<3-digit>`), type mapping (incl. the stated sort_order→Integer deviation) all declared
DECISIONS         ✓ 0 new ADR this stage; SEC's ADR-SEC-002 convention correctly cited, not re-derived
RESULT            PASSED ✓ — 0 findings
```

**Coverage — ENT/DBF → phases → QR → XM**: ENT-MDL-001/002 each appear in DATA-DOM with
≥1 QR under REPOSITORY OPS; all 21 DBF appear in the DB Alignment Manifest and their
owning entity's FIELDS table; XM-MDL-001 appears in INT-C, INT-R and ENT-MDL-001's
CROSS-MODULE line.

**Coverage — RULE → API → catalog code**: RULE-MDL-001→API-MDL-002→
MDL-409-MODULE-NOT-REGISTERED · RULE-MDL-002→API-MDL-006→MDL-409-VALUE-DUP ·
RULE-MDL-003→API-MDL-003→(enforced by DTO shape, no distinct error code needed — a request
including `key` simply has it ignored, not rejected, since the field is absent from the
DTO's schema entirely) · RULE-MDL-004→API-MDL-011→MDL-404-TYPE-KEY.

**Coverage — XM → status → blocks → workaround**: XM-MDL-001 → ACTIVE → blocks none →
no workaround needed.

## QR id definitions (cross-reference index — full detail in Query Reference Catalog above)
**QR-MDL-001** — FIND_BY_CRITERIA search lookup types [ENT-MDL-001, API-MDL-001]
**QR-MDL-002** — SAVE create lookup type [ENT-MDL-001, API-MDL-002]
**QR-MDL-003** — UPDATE rename lookup type [ENT-MDL-001, API-MDL-003]
**QR-MDL-004** — UPDATE deactivate lookup type [ENT-MDL-001, API-MDL-004]
**QR-MDL-005** — FIND_BY_CRITERIA search values of a type [ENT-MDL-002, API-MDL-005]
**QR-MDL-006** — SAVE create lookup value [ENT-MDL-002, API-MDL-006]
**QR-MDL-007** — UPDATE update lookup value [ENT-MDL-002, API-MDL-007]
**QR-MDL-008** — UPDATE deactivate lookup value [ENT-MDL-002, API-MDL-008]
**QR-MDL-009** — UPDATE batch persist reordered sortOrder [ENT-MDL-002, API-MDL-009]
**QR-MDL-010** — FIND_BY_CRITERIA browse types grouped by owner [ENT-MDL-001, API-MDL-010]
**QR-MDL-011** — FIND_BY_CRITERIA active values of an active type by key [ENT-MDL-001, ENT-MDL-002, API-MDL-011]
**QR-MDL-012** — EXISTS owner module registered in SEC (XM-MDL-001) [ENT-MDL-001, API-MDL-002]
**QR-MDL-013** — EXISTS uniqueness of key [ENT-MDL-001, API-MDL-002]
**QR-MDL-014** — EXISTS uniqueness of code within lookupTypeId [ENT-MDL-002, API-MDL-006]
**QR-MDL-015** — FIND_ONE resolve type by key + confirm active [ENT-MDL-001, API-MDL-011]

## Registry content
See `registry-exec-be-mdl.md`.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-srs (MDL)>>>
## REGISTRY — P1 — MDL v1
══════════════════════════════════════════════════════════════════

Entities
| ENT id | Name (ar/en) | Kind | PRIVATE/SHARED | Status |
|---|---|---|---|---|
| ENT-MDL-001 | نوع اللوكب / LookupType | master | SHARED (owner) | REGISTERED |
| ENT-MDL-002 | قيمة اللوكب / LookupValue | lookup | SHARED (owner) | REGISTERED |

Consumed
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ |
|---|---|---|---|
| ModuleRegistry | ENT-SEC-004 | SEC | SOFT-READ |

Lookups owned
None (see SRS A6).

Lookups consumed
None.

Screens
| SCR-REQ id | Name (ar/en) | Page code |
|---|---|---|
| SCR-REQ-MDL-001 | اللوكبات العامة / Generic Lookups | MDL_LOOKUPS |
| SCR-REQ-MDL-002 | سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner | MDL_TYPE_REGISTRY |

Requirements
REQ count: 13 · AC count: 13 · RULE count: 4 · ENT count: 2 · SCR-REQ count: 2
Last sequence per atom: REQ: 013 · AC: 013 · ENT: 002 · RULE: 004 · SCR-REQ: 002

REQ ids (full text in srs-mdl.md → A4): REQ-MDL-001, REQ-MDL-002, REQ-MDL-003, REQ-MDL-004,
REQ-MDL-005, REQ-MDL-006, REQ-MDL-007, REQ-MDL-008, REQ-MDL-009, REQ-MDL-010, REQ-MDL-011,
REQ-MDL-012, REQ-MDL-013

AC ids (full text in srs-mdl.md → A4, one per REQ above): AC-MDL-001, AC-MDL-002,
AC-MDL-003, AC-MDL-004, AC-MDL-005, AC-MDL-006, AC-MDL-007, AC-MDL-008, AC-MDL-009,
AC-MDL-010, AC-MDL-011, AC-MDL-012, AC-MDL-013

RULE ids (full text in srs-mdl.md → A5): RULE-MDL-001, RULE-MDL-002, RULE-MDL-003,
RULE-MDL-004

Decisions
ADR ids: none.

Event
"P1 completed: MDL v1 — 2 entities, 13 requirements, 13 acceptance criteria, 4 rules, 2 screen requirements, 0 ADRs"
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-db (MDL)>>>
## REGISTRY — P2 — MDL v1
══════════════════════════════════════════════════════════════════

Tables
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| MDL_LOOKUP_TYPE | ENT-MDL-001 | master | DBF-MDL-001 … DBF-MDL-010 |
| MDL_LOOKUP_VALUE | ENT-MDL-002 | lookup | DBF-MDL-011 … DBF-MDL-021 |

DBF ids (full detail in db-script-mdl.md → §1): DBF-MDL-001, DBF-MDL-002, DBF-MDL-003,
DBF-MDL-004, DBF-MDL-005, DBF-MDL-006, DBF-MDL-007, DBF-MDL-008, DBF-MDL-009, DBF-MDL-010,
DBF-MDL-011, DBF-MDL-012, DBF-MDL-013, DBF-MDL-014, DBF-MDL-015, DBF-MDL-016, DBF-MDL-017,
DBF-MDL-018, DBF-MDL-019, DBF-MDL-020, DBF-MDL-021

XM index
| XM id | Type | From | To | Status |
|---|---|---|---|---|
| XM-MDL-001 | SOFT-READ | MDL | SEC | ACTIVE |

Lookups
| Key | Seeded values count | Owner |
|---|---|---|
None — MDL owns the mechanism, not a domain-specific coded list of its own.

Sequences
Last DBF: DBF-MDL-021 · Last XM: XM-MDL-001

Decisions
None (no ADR this stage).

Event
"P2 completed: MDL v1 — 2 tables, 21 DBF, 1 XM"

Cascade
No registry XM row anywhere in the platform currently targets MDL with status DEFERRED —
nothing to resolve. XM-MDL-001 itself (MDL → SEC) resolves immediately to ACTIVE since SEC
v1 is already gated (pass-1 APPROVE, see project-registry.md PIPELINE/PROGRESS STATUS).
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

---
# INPUTS — module SEC (generated current state)

<<<INPUT: srs (SEC)>>>
# SRS — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp
Inputs : prd, domain-profile, project-registry (PRD approved 2026-09-10)
Counts : ENT 13 · REQ 33 · AC 33 · RULE 7 · SCR-REQ 10 · ADR 0
══════════════════════════════════════════════════════════════════

# PART A — MODULE FOUNDATION

## A1 — Document information
| Item | Value |
|---|---|
| Module | SEC — الأمان / Security |
| Feature code | SEC |
| Version | v1 |
| Date | 2026-09-10 |
| Status | DRAFT (P1) |
| Prepared by | governance-factory (analysis lane) |
| Decisions applied count | 0 (no ADR was needed — no ambiguity §9 was reached) |

## A2 — Functional context

**In scope:** المصادقة (تسجيل الدخول، التسجيل الذاتي، إعادة تعيين كلمة المرور)، RBAC هرمي
بثلاث مستويات (وحدة→شاشة→إجراء)، تسجيل الوحدات/الشاشات/الإجراءات كبيانات لأي وحدة مستهلكة،
فصل المهام (SoD) على مستوى المستخدم، القائمة الديناميكية ثنائية المستوى، لوحة تحكم الأمان،
سجل التدقيق غير القابل للتعديل، إدارة الجلسات النشطة، تكامل اختياري مع خدمة الإشعارات.

**Out of scope:** المصادقة متعددة العوامل (MFA)، تسجيل الدخول الموحد (SSO)/موفرو هوية
خارجيون — غير مذكورين في `security-module-plan-en.md` [business-policies-sec.md →
SCOPE EXCEPTIONS]؛ أي منطق عمل خاص بوحدة مستهلكة.

**Module function (one paragraph):** وحدة SEC هي نظام الأمان الوحيد للمنصة بأكملها: تُصدر
الهوية (المصادقة) وتُقرّر الصلاحيات الفعلية (RBAC هرمي)، بحيث لا تملك أي وحدة أخرى مستخدمين
أو أدوارًا أو تسجيل دخول خاصًا بها؛ كل وحدة تستهلك SEC عبر تسجيل نفسها كبيانات ثم فحص
المنح الصادرة عنها.

**Detailed description (workflow narrative, roles):** مستخدم يُسجّل ذاتيًا فيبقى معلّقًا بلا
صلاحيات → يوافق مسؤول أمان عليه فيصبح نشطًا → يُسنَد له دور واحد أو أكثر → عند كل طلب،
يُفحص منح الوحدة أولاً (بوابة)، ثم منح الشاشة، ثم منح الإجراء. مسؤول الأمان يدير الأدوار
والمستخدمين والجلسات النشطة ويراقب سجل التدقيق ولوحة التحكم. أي وحدة مستهلكة (مثل FIN
لاحقًا) تُسجّل نفسها وشاشاتها وإجراءاتها هنا كبيانات فقط، دون أي تعديل على شيفرة SEC.

**Current situation:** لا يوجد نظام أمان سابق ضمن هذه الدفعة — هذه أول وحدة تُبنى (Tier 0)؛
لا "وضع حالي" يُستبدل داخل هذه المنصة الجديدة.

**Current difficulties:** لا ينطبق (وحدة جديدة بالكامل).

**Proposed system and benefits:** نظام أمان مركزي واحد يمنع ازدواج/تضارب الصلاحيات بين
الوحدات، يضمن بوابة وحدة صارمة (لا شاشة يتيمة)، ويوفر أثرًا تدقيقيًا كاملاً غير قابل للتعديل.

**General notes (constraints, deferred items):** محرك سير العمل ممنوع منصّيًا
(`profiles/erp.yaml → conventions.workflow_engine: forbidden`)؛ لا آلية قفل تلقائي بعد محاولات
دخول فاشلة متكررة — لم يذكرها `security-module-plan-en.md`، فلم تُخترع (تُعرض فقط أعداد
الدخول الفاشل في لوحة التحكم، REQ-SEC-002/022).

## A3 — Entities and fields

Standard fields per kind (profile.conventions.entity_defaults): the `security` entity
kind carries no fixed default-field set in the profile (only master/transactional/
lookup/config do); every SEC entity below still carries the platform's audit fields
(`createdBy, createdAt, updatedBy, updatedAt`, `profile.stack.db.naming.audit_fields`)
except pure append-only log/session rows where a "who created it" field is redundant
with the row's own actor field (documented per entity).

### ENT-SEC-001 — المستخدم / User
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | SHARED (owner) — every module's audit fields (createdBy/updatedBy) reference it | No — login identity (email/username) is the natural key, not a generated number [§3.3 NUMBERING test] | create, read, search, update, activate, deactivate | consumed read-only by every future consumer module for its own audit fields | security-module-plan-en.md §3, §4.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| userPk | number | yes (system) | — | primary key | معرّف المستخدم | User id |
| username | text | yes | unique | login identity | اسم المستخدم | Username |
| email | text | yes | unique, valid email | used for password-reset delivery | البريد الإلكتروني | Email |
| passwordHash | text | yes (system) | never exposed to any client [POL-SEC-004] | write-only | تجزئة كلمة المرور | Password hash |
| fullNameAr | text | yes | — | — | الاسم الكامل (عربي) | Full name (Arabic) |
| fullNameEn | text | yes | — | — | الاسم الكامل (إنجليزي) | Full name (English) |
| statusCode | lookup | yes | lookup key `USER_STATUS` (A6) | drives A7 lifecycle | الحالة | Status |
| lastLoginAt | date-time | no | — | informational | آخر دخول | Last login |
| failedLoginCount24h | number | no | derived, not stored per ERP-…(see POL-SEC-010) — displayed from AuditLogEntry, not persisted on User | dashboard-only figure; kept here only as a documentation note, not a real column | عدد محاولات الدخول الفاشلة (٢٤س) | Failed logins (24h) |
| isActiveFl | flag | yes | true/false | mirrors statusCode ≠ DISABLED, kept for the platform's standard flag convention | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | standard audit fields | — | — |

### ENT-SEC-002 — الدور / Role
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create, read, search, update, deactivate | none | security-module-plan-en.md §4.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| rolePk | number | yes (system) | — | primary key | معرّف الدور | Role id |
| code | text | yes | unique | stable machine reference | رمز الدور | Role code |
| nameAr, nameEn | text | yes | — | — | اسم الدور | Role name |
| descriptionAr, descriptionEn | text | no | — | — | الوصف | Description |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | — | — | — |

### ENT-SEC-003 — ربط المستخدم بالدور / UserRoleAssignment
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create, read (list), delete (revoke) | none | security-module-plan-en.md §4.4 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| userRoleAssignmentPk | number | yes (system) | — | primary key | معرّف الإسناد | Assignment id |
| userId | reference | yes | ENT-SEC-001 | — | المستخدم | User |
| roleId | reference | yes | ENT-SEC-002 | — | الدور | Role |
| assignedBy, assignedAt | system | yes | — | who/when granted | — | — |

### ENT-SEC-004 — سجل الوحدات / ModuleRegistry
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | SHARED (owner) — every consuming module registers one row of itself here | No — the module code is the platform's own `{prefix}` (factory.ids), not a SEC-generated number | create (by a registering module), read, search, deactivate | consumed by every module registering itself (e.g. FIN in a later pass) | security-module-plan-en.md §4.3, §7 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| moduleRegistryPk | number | yes (system) | — | primary key | معرّف الوحدة المسجّلة | Registered module id |
| code | text | yes | unique — the platform module code (e.g. FIN, SEC) | matches `profile.vocabulary.module_prefixes` | رمز الوحدة | Module code |
| nameAr, nameEn | text | yes | — | — | اسم الوحدة | Module name |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | — | — | — |

### ENT-SEC-005 — سجل الشاشات / ScreenRegistry (SEC_PAGES)
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | SHARED (owner) | No | create (by a registering module), read, search, deactivate | consumed by every module registering its own screens | security-module-plan-en.md §4.3, §4.5; profiles/erp.yaml conventions.security_model.page_registry |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| screenRegistryPk | number | yes (system) | — | primary key | معرّف الشاشة المسجّلة | Registered screen id |
| pageCode | text | yes | unique | `SEC_PAGES` row per §7.1 | رمز الصفحة | Page code |
| moduleId | reference | yes | ENT-SEC-004; must already be registered [RULE-SEC-004] | — | الوحدة | Module |
| nameAr, nameEn | text | yes | — | — | اسم الشاشة | Screen name |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | — | — | — |

### ENT-SEC-006 — سجل الإجراءات / ActionRegistry
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | SHARED (owner) | No | create (by a registering module), read, search, deactivate | consumed by every module registering its own actions | security-module-plan-en.md §4.1, §4.3; profiles/erp.yaml conventions.security_model.permission_pattern |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| actionRegistryPk | number | yes (system) | — | primary key | معرّف الإجراء المسجّل | Registered action id |
| permissionCode | text | yes | unique, pattern `PERM_<PAGE_CODE>_<ACTION>` (profile.conventions.security_model.permission_pattern) — derived, never entered a second time as seed data | derivation, not duplication | رمز الصلاحية | Permission code |
| screenId | reference | yes | ENT-SEC-005; must already be registered [RULE-SEC-002] | — | الشاشة | Screen |
| actionCode | text | yes | one of the platform-standard set VIEW/CREATE/UPDATE/DELETE (profile.conventions.security_model.actions) or a module-declared custom code (e.g. "REVERSE_ENTRY") | free beyond the standard four, per plan §4.1 "custom actions" | الإجراء | Action |
| nameAr, nameEn | text | yes | — | — | اسم الإجراء | Action name |
| isActiveFl | flag | yes | — | — | نشط | Active |
| createdBy, createdAt, updatedBy, updatedAt | system | yes | — | — | — | — |

### ENT-SEC-007 — منح الوحدة للدور / RoleModuleGrant
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create (grant), read (list), delete (revoke — cascades per RULE-SEC-003) | none | security-module-plan-en.md §4.1-§4.2 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| roleModuleGrantPk | number | yes (system) | — | primary key | معرّف منح الوحدة | Module grant id |
| roleId | reference | yes | ENT-SEC-002 | — | الدور | Role |
| moduleId | reference | yes | ENT-SEC-004 | — | الوحدة | Module |
| grantedBy, grantedAt | system | yes | — | — | — | — |

### ENT-SEC-008 — منح الشاشة للدور / RoleScreenGrant
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create (grant, blocked without matching module grant — RULE-SEC-001), read (list), delete (revoke) | none | security-module-plan-en.md §4.1-§4.2 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| roleScreenGrantPk | number | yes (system) | — | primary key | معرّف منح الشاشة | Screen grant id |
| roleId | reference | yes | ENT-SEC-002 | — | الدور | Role |
| screenId | reference | yes | ENT-SEC-005; role must hold its module [RULE-SEC-001] | — | الشاشة | Screen |
| grantedBy, grantedAt | system | yes | — | — | — | — |

### ENT-SEC-009 — منح الإجراء للدور / RoleActionGrant
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create (grant, blocked without matching screen grant — RULE-SEC-002, and without VIEW on that screen unless the action itself is VIEW — RULE-SEC-007), read (list), delete (revoke) | none | security-module-plan-en.md §4.1-§4.2 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| roleActionGrantPk | number | yes (system) | — | primary key | معرّف منح الإجراء | Action grant id |
| roleId | reference | yes | ENT-SEC-002 | — | الدور | Role |
| actionId | reference | yes | ENT-SEC-006; role must hold the action's screen [RULE-SEC-002] and, unless the action itself is VIEW, must also hold VIEW on that screen [RULE-SEC-007] | — | الإجراء | Action |
| grantedBy, grantedAt | system | yes | — | — | — | — |

### ENT-SEC-010 — الجلسة النشطة / ActiveSession
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create (system, on login), read (list), terminate | none | security-module-plan-en.md §5.1, §5.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| activeSessionPk | number | yes (system) | — | primary key | معرّف الجلسة | Session id |
| userId | reference | yes | ENT-SEC-001 | — | المستخدم | User |
| tokenRef | text | yes | opaque reference — never the raw token/hash | — | مرجع الرمز | Token reference |
| startedAt | date-time | yes (system) | — | — | بدأت في | Started at |
| lastActivityAt | date-time | yes (system) | — | — | آخر نشاط | Last activity |
| ipAddress | text | no | — | — | عنوان IP | IP address |
| terminatedAt, terminatedBy | date-time / reference | no | set on logout or forced termination | null while active | أُنهيت في / بواسطة | Terminated at / by |

### ENT-SEC-011 — سجل التدقيق / AuditLogEntry
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create (system, append-only), read, search | none | security-module-plan-en.md §5.2-§5.3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| auditLogEntryPk | number | yes (system) | — | primary key | معرّف قيد التدقيق | Audit entry id |
| eventTypeCode | lookup | yes | lookup key `AUDIT_EVENT_TYPE` (A6) | — | نوع الحدث | Event type |
| actorUserId | reference | no | ENT-SEC-001 — null for an unauthenticated failed-login attempt | — | المستخدم الفاعل | Actor user |
| occurredAt | date-time | yes (system) | — | immutable once written [POL-SEC-009] | وقت الحدث | Occurred at |
| targetRef | text | no | free text (e.g. affected user/role id) | — | الهدف | Target |
| detailsAr, detailsEn | text | no | — | — | التفاصيل | Details |
| ipAddress | text | no | — | — | عنوان IP | IP address |
Note: this entity has no `createdBy`/`updatedBy` — it IS the audit record; `actorUserId` +
`occurredAt` serve that purpose, and it is never updated after insert (immutability, POL-SEC-009).

### ENT-SEC-012 — رمز إعادة تعيين كلمة المرور / PasswordResetToken
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create (system, on request), read (validate), invalidate (on use or expiry) | none | security-module-plan-en.md §3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| passwordResetTokenPk | number | yes (system) | — | primary key | معرّف الرمز | Token id |
| userId | reference | yes | ENT-SEC-001 | — | المستخدم | User |
| tokenHash | text | yes (system) | never exposed in full after issuance | write-once | تجزئة الرمز | Token hash |
| requestedAt, expiresAt | date-time | yes (system) | expiresAt = requestedAt + DEFAULT window (see A7 note) | — | — | — |
| usedAt | date-time | no | set once consumed [RULE-SEC-006] | — | استُخدم في | Used at |

### ENT-SEC-013 — طلب تسجيل معلّق / SignupRequest
| Kind | Ownership | Business number | Operations | Cross-module | Source |
|---|---|---|---|---|---|
| security | PRIVATE | No | create (self-service), read, search, approve, reject | none | security-module-plan-en.md §3 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| signupRequestPk | number | yes (system) | — | primary key | معرّف طلب التسجيل | Signup request id |
| email | text | yes | valid email | becomes the user's login on approval | البريد الإلكتروني | Email |
| fullNameAr, fullNameEn | text | yes | — | — | الاسم الكامل | Full name |
| submittedAt | date-time | yes (system) | — | — | تاريخ التقديم | Submitted at |
| statusCode | lookup | yes | lookup key `SIGNUP_STATUS` (A6) | — | الحالة | Status |
| reviewedBy, reviewedAt | reference / date-time | no | set on approve/reject | — | — | — |

## A4 — Functional requirements (EARS) and acceptance criteria

### REQ-SEC-001 — تسجيل دخول ناجح / Successful login
Pattern    : event
Statement  : When a registered, active user submits valid credentials, the system shall issue a session/access token representing that user's identity.
Traces     : US-SEC-001
Entities   : ENT-SEC-001, ENT-SEC-010
Rationale  : entry point every consuming module trusts
Source     : security-module-plan-en.md §3
Priority   : HIGH
#### AC-SEC-001 — [REQ-SEC-001]
Given an active user with a known username and password
When the user submits those correct credentials to the login screen
Then the system creates an active session for the user and grants access to the platform

### REQ-SEC-002 — رفض بيانات دخول غير صحيحة / Reject invalid credentials
Pattern    : unwanted
Statement  : If submitted credentials do not match an active user, then the system shall reject the login attempt and record a failed-login audit event.
Traces     : US-SEC-001
Entities   : ENT-SEC-001, ENT-SEC-011
Rationale  : POL-SEC-004 discipline; feeds the dashboard's failed-logins widget
Source     : security-module-plan-en.md §3, §5.1
Priority   : HIGH
#### AC-SEC-002 — [REQ-SEC-002]
Given a login attempt with a wrong password or an unknown/disabled username
When the user submits it
Then the system rejects the attempt with message ar: "بيانات الدخول غير صحيحة" · en: "Invalid credentials", issues no session, and appends one `LOGIN_FAILED` audit entry

### REQ-SEC-003 — تقديم طلب تسجيل / Submit sign-up
Pattern    : event
Statement  : When a prospective user submits a sign-up request, the system shall create a pending sign-up request with no permission granted to anyone.
Traces     : US-SEC-002
Entities   : ENT-SEC-013
Rationale  : self-registration without premature access
Source     : security-module-plan-en.md §3
Priority   : MEDIUM
#### AC-SEC-003 — [REQ-SEC-003]
Given a prospective user fills the sign-up form with a valid, not-already-registered email
When they submit it
Then the system creates a `SignupRequest` with status PENDING and creates no user account yet

### REQ-SEC-004 — الموافقة على طلب التسجيل / Approve a sign-up request
Pattern    : event
Statement  : When an administrator approves a pending sign-up request, the system shall create an active user account from it.
Traces     : US-SEC-002
Entities   : ENT-SEC-013, ENT-SEC-001
Rationale  : conversion from pending to real, permission-bearing identity
Source     : security-module-plan-en.md §3
Priority   : MEDIUM
#### AC-SEC-004 — [REQ-SEC-004]
Given a SignupRequest with status PENDING
When an administrator approves it
Then the system creates a User with status ACTIVE from its email/name, and marks the SignupRequest APPROVED

### REQ-SEC-005 — رفض طلب التسجيل / Reject a sign-up request
Pattern    : unwanted
Statement  : If an administrator rejects a pending sign-up request, then the system shall mark the request rejected and create no user account.
Traces     : US-SEC-002
Entities   : ENT-SEC-013
Rationale  : symmetric negative path to REQ-SEC-004
Source     : security-module-plan-en.md §3
Priority   : LOW
#### AC-SEC-005 — [REQ-SEC-005]
Given a SignupRequest with status PENDING
When an administrator rejects it
Then the system marks it REJECTED and creates no User

### REQ-SEC-006 — إصدار رمز إعادة تعيين / Issue a password-reset token
Pattern    : event
Statement  : When a user requests a password reset, the system shall issue a single-use, time-limited reset token for that user.
Traces     : US-SEC-003
Entities   : ENT-SEC-012
Rationale  : secure self-service reset
Source     : security-module-plan-en.md §3
Priority   : MEDIUM
#### AC-SEC-006 — [REQ-SEC-006]
Given a user identifies themselves by a registered email
When they request a password reset
Then the system creates one PasswordResetToken with an expiry, and no password is changed yet

### REQ-SEC-007 — إتمام إعادة التعيين بنجاح / Complete a password reset
Pattern    : event
Statement  : When a user submits a valid, unexpired reset token with a new password, the system shall update that user's password and invalidate the token.
Traces     : US-SEC-003
Entities   : ENT-SEC-012, ENT-SEC-001
Rationale  : one-time use enforced
Source     : security-module-plan-en.md §3
Priority   : MEDIUM
#### AC-SEC-007 — [REQ-SEC-007]
Given an unexpired, unused PasswordResetToken and a new password meeting the platform's password rules
When the user submits them
Then the system updates the user's password hash, sets the token's usedAt, and appends a `PASSWORD_RESET_COMPLETED` audit entry

### REQ-SEC-008 — رفض رمز منتهٍ أو مُستخدَم / Reject an expired or used reset token
Pattern    : unwanted
Statement  : If a submitted reset token is expired or already used, then the system shall reject the password reset.
Traces     : US-SEC-003
Entities   : ENT-SEC-012
Rationale  : RULE-SEC-006
Source     : security-module-plan-en.md §3
Priority   : MEDIUM
#### AC-SEC-008 — [REQ-SEC-008]
Given a PasswordResetToken that is expired or already has a usedAt value
When it is submitted with a new password
Then the system rejects the request with message ar: "رابط إعادة التعيين غير صالح أو منتهي" · en: "This reset link is invalid or has expired" and changes nothing

### REQ-SEC-009 — إنشاء مستخدم / Create a user
Pattern    : event
Statement  : When an administrator creates a user, the system shall record that user's bilingual name, login identity and status.
Traces     : US-SEC-004
Entities   : ENT-SEC-001
Rationale  : direct administrative provisioning (distinct from self sign-up)
Source     : security-module-plan-en.md §4.4
Priority   : HIGH
#### AC-SEC-009 — [REQ-SEC-009]
Given an administrator fills the user form with a unique username/email and both name labels
When they save it
Then the system creates the User with status ACTIVE (or as chosen)

### REQ-SEC-010 — إسناد أدوار متعددة / Assign one or more roles to a user
Pattern    : event
Statement  : When an administrator assigns one or more roles to a user, the system shall record each assignment individually.
Traces     : US-SEC-004
Entities   : ENT-SEC-001, ENT-SEC-002, ENT-SEC-003
Rationale  : a user may hold several roles; effective permission is their union [POL-SEC-008]
Source     : security-module-plan-en.md §4.4
Priority   : HIGH
#### AC-SEC-010 — [REQ-SEC-010]
Given an administrator selects one or more active roles for a user
When they save the assignment
Then the system creates one UserRoleAssignment row per selected role

### REQ-SEC-011 — تعطيل مستخدم / Deactivate a user
Pattern    : event
Statement  : When an administrator deactivates a user, the system shall immediately end that user's active sessions and prevent new logins for that user.
Traces     : US-SEC-004
Entities   : ENT-SEC-001, ENT-SEC-010
Rationale  : revoking access must be immediate, not just cosmetic
Source     : security-module-plan-en.md §4.4
Priority   : HIGH
#### AC-SEC-011 — [REQ-SEC-011]
Given an active user with one active session
When an administrator deactivates the user
Then the system sets status DISABLED, terminates every active session of that user, and a subsequent login attempt is rejected per REQ-SEC-002

### REQ-SEC-031 — إعادة تفعيل مستخدم / Reactivate a disabled user
Pattern    : event
Statement  : When an administrator reactivates a disabled user, the system shall restore that user's ability to sign in.
Traces     : US-SEC-004
Entities   : ENT-SEC-001
Rationale  : symmetric to REQ-SEC-011; "activate" listed alongside deactivate in the story
Source     : security-module-plan-en.md §4.4
Priority   : MEDIUM
#### AC-SEC-031 — [REQ-SEC-031]
Given a user with status DISABLED
When an administrator reactivates them
Then the system sets status ACTIVE and a subsequent login with correct credentials succeeds

### REQ-SEC-012 — منح وحدة لدور / Grant a module to a role
Pattern    : event
Statement  : When an administrator grants a module to a role, the system shall record that grant as the role's module-level access.
Traces     : US-SEC-005
Entities   : ENT-SEC-002, ENT-SEC-004, ENT-SEC-007
Rationale  : the module gate, evaluated first [POL-SEC-001]
Source     : security-module-plan-en.md §4.1-§4.2
Priority   : HIGH
#### AC-SEC-012 — [REQ-SEC-012]
Given an active role and an active registered module
When an administrator grants that module to that role
Then the system creates one RoleModuleGrant row

### REQ-SEC-013 — رفض منح شاشة دون منح وحدة / Reject a screen grant without its module grant
Pattern    : unwanted
Statement  : If an administrator attempts to grant a screen of a module the target role does not hold, then the system shall reject the grant.
Traces     : US-SEC-005
Entities   : ENT-SEC-002, ENT-SEC-005, ENT-SEC-007, ENT-SEC-008
Rationale  : RULE-SEC-001; structural integrity, no orphaned grant [POL-SEC-002]
Source     : security-module-plan-en.md §4.2
Priority   : HIGH
#### AC-SEC-013 — [REQ-SEC-013]
Given a role with no RoleModuleGrant for module FIN
When an administrator attempts to grant that role a FIN screen
Then the system rejects the grant with message ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" · en: "Cannot grant a screen without first granting its module" and creates no RoleScreenGrant

### REQ-SEC-014 — رفض منح إجراء دون منح شاشة / Reject an action grant without its screen grant
Pattern    : unwanted
Statement  : If an administrator attempts to grant an action of a screen the target role does not hold, then the system shall reject the grant.
Traces     : US-SEC-005
Entities   : ENT-SEC-002, ENT-SEC-006, ENT-SEC-008, ENT-SEC-009
Rationale  : RULE-SEC-002; same structural-integrity principle one level down
Source     : security-module-plan-en.md §4.2
Priority   : HIGH
#### AC-SEC-014 — [REQ-SEC-014]
Given a role with no RoleScreenGrant for a given screen
When an administrator attempts to grant that role an action on that screen
Then the system rejects the grant with message ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" · en: "Cannot grant an action without first granting its screen" and creates no RoleActionGrant

### REQ-SEC-015 — إلغاء المنح المتسلسل عند سحب الوحدة / Cascade-revoke on module-grant removal
Pattern    : event
Statement  : When an administrator revokes a role's module grant, the system shall also remove every screen and action grant that module covered for that role.
Traces     : US-SEC-005
Entities   : ENT-SEC-002, ENT-SEC-007, ENT-SEC-008, ENT-SEC-009
Rationale  : RULE-SEC-003; prevents an orphaned screen/action grant from surviving its module grant
Source     : security-module-plan-en.md §4.2
Priority   : HIGH
#### AC-SEC-015 — [REQ-SEC-015]
Given a role holding a module grant plus two screen grants and three action grants under that module
When an administrator revokes the module grant
Then the system deletes the module grant and every screen/action grant it covered, leaving none behind

### REQ-SEC-016 — تسجيل وحدة جديدة / Register a new module
Pattern    : event
Statement  : When a consuming module registers itself, the system shall record its code and bilingual name in the module registry.
Traces     : US-SEC-006
Entities   : ENT-SEC-004
Rationale  : "no change to security code" onboarding
Source     : security-module-plan-en.md §4.3, §7
Priority   : HIGH
#### AC-SEC-016 — [REQ-SEC-016]
Given a module code not yet registered
When it is registered with its bilingual name
Then the system creates one active ModuleRegistry row

### REQ-SEC-017 — تسجيل شاشة لوحدة مسجّلة / Register a screen under a registered module
Pattern    : event
Statement  : When a consuming module registers a screen, the system shall record it under that module's already-registered code.
Traces     : US-SEC-006
Entities   : ENT-SEC-004, ENT-SEC-005
Rationale  : SEC_PAGES per §7.1
Source     : security-module-plan-en.md §4.3, §4.5
Priority   : HIGH
#### AC-SEC-017 — [REQ-SEC-017]
Given a registered, active module
When it registers a screen with a unique page code and bilingual name
Then the system creates one active ScreenRegistry row under that module

### REQ-SEC-018 — رفض تسجيل شاشة لوحدة غير مسجّلة / Reject a screen registered under an unregistered module
Pattern    : unwanted
Statement  : If a screen registration names a module that is not registered, then the system shall reject the screen registration.
Traces     : US-SEC-006
Entities   : ENT-SEC-004, ENT-SEC-005
Rationale  : RULE-SEC-004
Source     : security-module-plan-en.md §4.3
Priority   : MEDIUM
#### AC-SEC-018 — [REQ-SEC-018]
Given a module code with no ModuleRegistry row
When a screen registration names that code
Then the system rejects it with message ar: "الوحدة غير مسجّلة" · en: "Module is not registered" and creates no ScreenRegistry row

### REQ-SEC-019 — تسجيل إجراء لشاشة مسجّلة / Register an action under a registered screen
Pattern    : event
Statement  : When a consuming module registers an action on one of its screens, the system shall record it under that screen.
Traces     : US-SEC-006
Entities   : ENT-SEC-005, ENT-SEC-006
Rationale  : permission catalog per §4.1
Source     : security-module-plan-en.md §4.1, §4.3
Priority   : HIGH
#### AC-SEC-019 — [REQ-SEC-019]
Given a registered, active screen
When it registers an action code with bilingual name
Then the system creates one active ActionRegistry row with permission code `PERM_<pageCode>_<actionCode>`

### REQ-SEC-020 — منع تضارب الإجراءات لدى مستخدم واحد / Prevent one user from holding two conflicting actions
Pattern    : optional
Statement  : Where a consumer module declares two of its actions as conflicting, the system shall prevent a single user from holding both action grants at the same time, whether obtained through one role or several.
Traces     : US-SEC-007
Entities   : ENT-SEC-001, ENT-SEC-003, ENT-SEC-006, ENT-SEC-009
Rationale  : RULE-SEC-005; SoD moved to the shared RBAC layer per general-accounting-system-plan-en.md §8.2/§10.3
Source     : security-module-plan-en.md §4.4
Priority   : MEDIUM
#### AC-SEC-020 — [REQ-SEC-020]
Given two actions declared conflicting by their owning module, and a user who already holds one of them (via any role)
When an administrator attempts to assign a role that would give that same user the other conflicting action
Then the system rejects the assignment with message ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" · en: "This user already holds a conflicting action"

### REQ-SEC-021 — القائمة تعرض الممنوح فقط / Menu shows only effective grants
Pattern    : event
Statement  : When a user's menu is rendered, the system shall include only the modules that user's effective grants hold, each showing only that user's effective granted screens beneath it.
Traces     : US-SEC-008
Entities   : ENT-SEC-004, ENT-SEC-005, ENT-SEC-007, ENT-SEC-008
Rationale  : POL-SEC-006
Source     : security-module-plan-en.md §6
Priority   : HIGH
#### AC-SEC-021 — [REQ-SEC-021]
Given a user whose roles' union grants exactly module FIN with screens "Journal Entries" and "Trial Balance"
When their menu renders
Then the system shows only FIN as a top-level entry with exactly those two screens beneath it

### REQ-SEC-032 — إخفاء الوحدة غير الممنوحة من القائمة / Hide an ungranted module from the menu
Pattern    : unwanted
Statement  : If a user's effective grants do not include a module, then the system shall omit that module entirely from that user's rendered menu.
Traces     : US-SEC-008
Entities   : ENT-SEC-004, ENT-SEC-007
Rationale  : POL-SEC-007 (first half)
Source     : security-module-plan-en.md §4.2, §6
Priority   : HIGH
#### AC-SEC-032 — [REQ-SEC-032]
Given a user whose roles hold no grant for module FIN
When their menu renders
Then FIN does not appear anywhere in the menu

### REQ-SEC-033 — بوابة الوحدة تُفحص على كل طلب / Module gate enforced on every request
Pattern    : ubiquitous
Statement  : The system shall verify a user's effective module grant before allowing any request to a screen or action of that module, independent of menu visibility.
Traces     : US-SEC-008
Entities   : ENT-SEC-004, ENT-SEC-007
Rationale  : POL-SEC-007 (second half) — "not merely hidden... blocked up front, not merely hidden"
Source     : security-module-plan-en.md §4.2
Priority   : HIGH
#### AC-SEC-033 — [REQ-SEC-033]
Given a user whose roles hold no grant for module FIN
When that user directly calls a FIN endpoint or navigates to a FIN screen URL
Then the system denies the request with an authorization error, regardless of how the request was reached

### REQ-SEC-022 — حساب أرقام لوحة التحكم حيًا / Compute dashboard figures live
Pattern    : event
Statement  : When an authorized administrator opens the admin dashboard, the system shall compute every widget figure from live data at that moment.
Traces     : US-SEC-009
Entities   : ENT-SEC-001, ENT-SEC-002, ENT-SEC-010, ENT-SEC-011
Rationale  : POL-SEC-010
Source     : security-module-plan-en.md §5.1-§5.2
Priority   : MEDIUM
#### AC-SEC-022 — [REQ-SEC-022]
Given the dashboard is opened
When it renders
Then every widget (users overview, failed logins 24h, active sessions, recent activity, roles/permissions summary, onboarding funnel) is computed from current data, never from a stored counter

### REQ-SEC-023 — إخفاء عنصر لوحة التحكم غير الممنوح / Hide an ungranted dashboard widget
Pattern    : unwanted
Statement  : If a user's role does not grant a dashboard widget's underlying permission, then the system shall omit that widget for that user.
Traces     : US-SEC-009
Entities   : ENT-SEC-001, ENT-SEC-002, ENT-SEC-007, ENT-SEC-008, ENT-SEC-009
Rationale  : POL-SEC-011
Source     : security-module-plan-en.md §5.1
Priority   : MEDIUM
#### AC-SEC-023 — [REQ-SEC-023]
Given an administrator role without the "active sessions" widget's permission
When that role's user opens the dashboard
Then the active-sessions widget does not appear for that user

### REQ-SEC-024 — تسجيل حدث تدقيقي / Append an audit-log entry
Pattern    : event
Statement  : When any security-relevant event occurs (login, failed login, password reset, role or permission change, session termination), the system shall append one immutable audit-log entry recording it.
Traces     : US-SEC-010
Entities   : ENT-SEC-011
Rationale  : POL-SEC-009
Source     : security-module-plan-en.md §5.2-§5.3
Priority   : MEDIUM
#### AC-SEC-024 — [REQ-SEC-024]
Given any of the listed events occurs
When it completes
Then the system appends one AuditLogEntry with the correct eventTypeCode, actor and timestamp, and no existing entry is altered

### REQ-SEC-025 — بحث/تصفية سجل التدقيق / Search and filter the audit log
Pattern    : event
Statement  : When an administrator searches or filters the audit log, the system shall return matching entries without altering any of them.
Traces     : US-SEC-010
Entities   : ENT-SEC-011
Rationale  : usable audit trail
Source     : security-module-plan-en.md §5.3
Priority   : MEDIUM
#### AC-SEC-025 — [REQ-SEC-025]
Given audit entries exist across several event types and dates
When an administrator filters by event type and date range
Then the system returns exactly the matching entries, unmodified

### REQ-SEC-026 — تصدير سجل التدقيق / Export the audit log
Pattern    : event
Statement  : When an administrator exports the audit log, the system shall produce a CSV file of the currently filtered entries.
Traces     : US-SEC-010
Entities   : ENT-SEC-011
Rationale  : plan §5.3 deliverable "CSV export"
Source     : security-module-plan-en.md §5.3
Priority   : LOW
#### AC-SEC-026 — [REQ-SEC-026]
Given a filtered audit-log view
When the administrator exports it
Then the system produces a CSV file containing exactly the filtered entries' fields

### REQ-SEC-027 — عرض الجلسات النشطة / List active sessions
Pattern    : event
Statement  : When an administrator views the active-sessions screen, the system shall list every session that has not been terminated, with its user and last-activity time.
Traces     : US-SEC-011
Entities   : ENT-SEC-010
Rationale  : plan §5.1, §5.3
Source     : security-module-plan-en.md §5.1, §5.3
Priority   : MEDIUM
#### AC-SEC-027 — [REQ-SEC-027]
Given several sessions exist, some terminated and some not
When an administrator opens the active-sessions screen
Then only the non-terminated sessions are listed, each with its user and last-activity time

### REQ-SEC-028 — إنهاء جلسة قسريًا / Force-terminate a session
Pattern    : event
Statement  : When an authorized administrator force-terminates a session, the system shall immediately end that session and require the affected user to sign in again.
Traces     : US-SEC-011
Entities   : ENT-SEC-010
Rationale  : plan §5.1 "force-terminate a session"
Source     : security-module-plan-en.md §5.1
Priority   : MEDIUM
#### AC-SEC-028 — [REQ-SEC-028]
Given an active session
When an authorized administrator force-terminates it
Then the system sets terminatedAt/terminatedBy and the associated token is no longer accepted for any subsequent request

### REQ-SEC-029 — إشعار اختياري عند إعادة التعيين / Optional notification on password reset
Pattern    : optional
Statement  : Where the Notifications integration is enabled, the system shall dispatch a password-reset message through it when a reset token is issued.
Traces     : US-SEC-012
Entities   : ENT-SEC-012
Rationale  : "only on real need", never a hard dependency
Source     : security-module-plan-en.md §8; new project/integration-notifications-fileservice.md §1
Priority   : LOW
#### AC-SEC-029 — [REQ-SEC-029]
Given the Notifications integration is enabled and a reset token is issued
When the token is created
Then the system dispatches one notification with templateCode identifying the password-reset message, and REQ-SEC-006 succeeds unchanged if the integration is disabled or unavailable

### REQ-SEC-030 — اشتراط VIEW لبقية الإجراءات / VIEW required for any other action on a screen
Pattern    : unwanted
Statement  : If a role does not hold the VIEW action grant for a screen, then the system shall deny every other action on that screen for that role.
Traces     : US-SEC-005
Entities   : ENT-SEC-006, ENT-SEC-009
Rationale  : RULE-SEC-007; profile.conventions.security_model.gateway_action = VIEW
Source     : profiles/erp.yaml conventions.security_model
Priority   : HIGH
#### AC-SEC-030 — [REQ-SEC-030]
Given a role holds CREATE on a screen but not VIEW on that same screen
When that role's user attempts the CREATE action
Then the system denies it until VIEW is also granted on that screen

## A5 — Business rules

### RULE-SEC-001 — منع منح شاشة دون منح الوحدة / No screen grant without its module grant
Scope      : ENT-SEC-008
Trigger    : on create (screen grant)
Statement  : The system shall prevent a screen grant for a role that does not hold the screen's module grant.
Message    : ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" · en: "Cannot grant a screen without first granting its module"
Traces     : REQ-SEC-013
Source     : security-module-plan-en.md §4.2

### RULE-SEC-002 — منع منح إجراء دون منح الشاشة / No action grant without its screen grant
Scope      : ENT-SEC-009
Trigger    : on create (action grant)
Statement  : The system shall prevent an action grant for a role that does not hold the action's screen grant.
Message    : ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" · en: "Cannot grant an action without first granting its screen"
Traces     : REQ-SEC-014
Source     : security-module-plan-en.md §4.2

### RULE-SEC-003 — الإلغاء المتسلسل عند سحب منح الوحدة / Cascade revoke on module-grant removal
Scope      : ENT-SEC-007
Trigger    : on delete (module grant)
Statement  : The system shall delete every screen grant and action grant that module covered for that role when its module grant is revoked.
Message    : ar: "سيتم سحب كل منح الشاشات والإجراءات ضمن هذه الوحدة لهذا الدور" · en: "Every screen and action grant under this module for this role will be revoked"
Traces     : REQ-SEC-015
Source     : security-module-plan-en.md §4.2

### RULE-SEC-004 — رفض تسجيل شاشة لوحدة غير مسجّلة / No screen under an unregistered module
Scope      : ENT-SEC-005
Trigger    : on create (screen registration)
Statement  : The system shall reject a screen registration whose module code has no ModuleRegistry row.
Message    : ar: "الوحدة غير مسجّلة" · en: "Module is not registered"
Traces     : REQ-SEC-018
Source     : security-module-plan-en.md §4.3

### RULE-SEC-005 — منع تضارب الإجراءات لمستخدم واحد / Prevent conflicting actions on one user
Scope      : ENT-SEC-003, ENT-SEC-009
Trigger    : on create (role assignment or action grant)
Statement  : The system shall prevent assigning a user, by any combination of roles, both actions of a module-declared conflicting pair.
Message    : ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" · en: "This user already holds a conflicting action"
Traces     : REQ-SEC-020
Source     : security-module-plan-en.md §4.4; general-accounting-system-plan-en.md §8.2

### RULE-SEC-006 — رفض رمز إعادة تعيين منتهٍ أو مُستخدَم / Reject expired or used reset token
Scope      : ENT-SEC-012
Trigger    : on submit (password reset completion)
Statement  : The system shall reject a password-reset submission whose token is expired or already used.
Message    : ar: "رابط إعادة التعيين غير صالح أو منتهي" · en: "This reset link is invalid or has expired"
Traces     : REQ-SEC-008
Source     : security-module-plan-en.md §3

### RULE-SEC-007 — اشتراط VIEW كبوابة على مستوى الشاشة / VIEW as the screen-level gateway action
Scope      : ENT-SEC-009
Trigger    : on evaluate (any action check) and on create (action grant, informational)
Statement  : The system shall require a role to hold the VIEW action grant on a screen before any other action grant on that screen takes effect for it.
Message    : ar: "يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة" · en: "The VIEW action must be granted on this screen first"
Traces     : REQ-SEC-030
Source     : profiles/erp.yaml conventions.security_model.gateway_action

## A6 — Lookups

**USER_STATUS** — owned by SEC — used by ENT-SEC-001.statusCode — control type: lookup
| Code | Label (ar) | Label (en) |
|---|---|---|
| PENDING | معلّق | Pending |
| ACTIVE | نشط | Active |
| DISABLED | معطّل | Disabled |
Source: AUTO (module-registry-sec.md → AUTO-DECISIONS), values fixed by the A7 lifecycle below.

**SIGNUP_STATUS** — owned by SEC — used by ENT-SEC-013.statusCode — control type: lookup
| Code | Label (ar) | Label (en) |
|---|---|---|
| PENDING | معلّق | Pending |
| APPROVED | مقبول | Approved |
| REJECTED | مرفوض | Rejected |
DEFAULT: a distinct lookup from USER_STATUS because a rejected sign-up never becomes a
User row (no DISABLED-equivalent needed) — Source: this stage, applying profile.conventions.lookups
("no hardcoded enums") to the SignupRequest lifecycle (REQ-SEC-003/004/005) — Override: merge
into USER_STATUS if the client prefers one shared status set.

**AUDIT_EVENT_TYPE** — owned by SEC — used by ENT-SEC-011.eventTypeCode — control type: lookup
| Code | Label (ar) | Label (en) |
|---|---|---|
| LOGIN_SUCCESS | دخول ناجح | Login success |
| LOGIN_FAILED | دخول فاشل | Login failed |
| LOGOUT | خروج | Logout |
| PASSWORD_RESET_REQUESTED | طلب إعادة تعيين | Password reset requested |
| PASSWORD_RESET_COMPLETED | إتمام إعادة التعيين | Password reset completed |
| ROLE_ASSIGNED | إسناد دور | Role assigned |
| ROLE_REVOKED | سحب دور | Role revoked |
| MODULE_GRANTED | منح وحدة | Module granted |
| MODULE_REVOKED | سحب منح وحدة | Module revoked |
| SCREEN_GRANTED | منح شاشة | Screen granted |
| SCREEN_REVOKED | سحب منح شاشة | Screen revoked |
| ACTION_GRANTED | منح إجراء | Action granted |
| ACTION_REVOKED | سحب منح إجراء | Action revoked |
| SESSION_TERMINATED | إنهاء جلسة | Session terminated |
Source: module-registry-sec.md → AUTO-DECISIONS; profiles/erp.yaml conventions.lookups.

Consumed lookups: none — SEC is a Tier-0 foundation module.

## A7 — Status lifecycle

**ENT-SEC-001 User.statusCode (USER_STATUS, 3 states, >2 transitions — diagram required)**
```
PENDING --(REQ-SEC-004, admin approves sign-up)--> ACTIVE
ACTIVE  --(REQ-SEC-011, admin deactivates)--------> DISABLED
DISABLED--(REQ-SEC-031, admin reactivates)--------> ACTIVE
```
(A User created directly by an administrator — REQ-SEC-009 — starts at ACTIVE, bypassing PENDING.)

**ENT-SEC-013 SignupRequest.statusCode (SIGNUP_STATUS, 3 states)**
```
PENDING --(REQ-SEC-004, approve)--> APPROVED
PENDING --(REQ-SEC-005, reject)---> REJECTED
```
APPROVED and REJECTED are terminal — no further transition.

All other statuses in this module (grant rows, sessions) are a binary
active/terminated flag, not a multi-state lifecycle — not applicable for a diagram.

**DEFAULT — reset-token expiry window**: not stated by the plan; this stage applies a
DEFAULT of 30 minutes from `requestedAt` to `expiresAt` (industry-standard short-lived
reset window) — Source: domain best practice (no conflicting statement in
security-module-plan-en.md or the knowledge file) — Override: configurable value if the
client states a different window; non-breaking, no ADR required (a pure numeric default
with no story/policy it could contradict).

## A8 — Module dependencies

| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ | XM candidate (assigned by P2) |
|---|---|---|---|---|
None — SEC is ROOT; it consumes no entity owned by another in-scope module.

| External service | Purpose | Integration kind |
|---|---|---|
| Notifications (ready, external) | password-reset message (REQ-SEC-029) | SOFT / optional, per new project/integration-notifications-fileservice.md §1 |

# PART B — SCREEN REQUIREMENTS

## SCR-REQ-SEC-001 — تسجيل الدخول / Login
### B1 — Definition
Purpose      : السماح لمستخدم مسجَّل بالدخول الآمن إلى المنصة.
Entities     : ENT-SEC-001, ENT-SEC-010
Operations   : create (session, via REQ-SEC-001/002)
Users        : أي مستخدم مسجَّل (غير مصادَق بعد)
Navigation   : (public) → Login; to: post-login landing / dashboard per the user's own menu
Content shape: flat record (username/password form)
Traces       : REQ-SEC-001, REQ-SEC-002
Composite    : single screen (no search/detail split)
### B2 — Search / list
Not applicable — no search on this screen.
### B3 — Input
Fields: username (ENT-SEC-001.username), password (write-only, not persisted as entered).
Buttons: "Sign in" → REQ-SEC-001/REQ-SEC-002; "Forgot password?" → navigates to SCR-REQ-SEC-003; "Sign up" → navigates to SCR-REQ-SEC-002.
### B4 — Access
Page code: SEC_LOGIN. Public (pre-authentication) — no role/permission gate applies to reaching this screen itself.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| login | POST | /api/v1/sec/auth/login | username, password | session/access token | — | REQ-SEC-001, REQ-SEC-002 |

## SCR-REQ-SEC-002 — التسجيل الذاتي / Sign-up
### B1 — Definition
Purpose      : السماح لمستخدم محتمل بتقديم طلب تسجيل ذاتي.
Entities     : ENT-SEC-013
Operations   : create
Users        : زائر غير مصادَق
Navigation   : (public) → Sign-up; from: SCR-REQ-SEC-001
Content shape: flat record
Traces       : REQ-SEC-003
Composite    : single screen
### B2 — Search / list
Not applicable.
### B3 — Input
Fields: email, fullNameAr, fullNameEn (ENT-SEC-013). Button "Submit" → REQ-SEC-003.
### B4 — Access
Page code: SEC_SIGNUP. Public (pre-authentication).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| submit sign-up | POST | /api/v1/sec/auth/signup | email, fullNameAr, fullNameEn | signup request confirmation | — | REQ-SEC-003 |

## SCR-REQ-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password
### B1 — Definition
Purpose      : السماح بإعادة تعيين ذاتية آمنة لكلمة المرور.
Entities     : ENT-SEC-012, ENT-SEC-001
Operations   : create (token), update (password)
Users        : أي مستخدم يعرف بريده الإلكتروني المسجَّل
Navigation   : (public) → Forgot password; from: SCR-REQ-SEC-001
Content shape: flat record (two steps: request → token+new password)
Traces       : REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-029
Composite    : Wizard (request step + reset step) = ONE screen requirement
### B2 — Search / list
Not applicable.
### B3 — Input
Step 1: email. Step 2: token (from the reset link), new password, confirm password.
### B4 — Access
Page code: SEC_PWD_RESET. Public (pre-authentication).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| request reset | POST | /api/v1/sec/auth/password-reset/request | email | confirmation (always generic, never reveals whether the email exists) | — | REQ-SEC-006, REQ-SEC-029 |
| complete reset | POST | /api/v1/sec/auth/password-reset/complete | token, newPassword | confirmation | RULE-SEC-006 | REQ-SEC-007, REQ-SEC-008 |

## SCR-REQ-SEC-004 — المستخدمون / Users
### B1 — Definition
Purpose      : إدارة المستخدمين وإسناد الأدوار لهم.
Entities     : ENT-SEC-001, ENT-SEC-002, ENT-SEC-003, ENT-SEC-013
Operations   : search, create, read, update, activate, deactivate; approve/reject a SignupRequest
Users        : مسؤول الأمان
Navigation   : SEC → Authorization → Users; to: user detail (roles tab)
Content shape: flat record (search list + entry form; roles shown as a repeating sub-list on the detail)
Traces       : REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-031, REQ-SEC-004, REQ-SEC-005
Composite    : Search + Entry = ONE screen requirement
### B2 — Search / list
Filters: username/email, fullName, statusCode — each corresponds to a result column.
### B3 — Input
Fields: username, email, fullNameAr, fullNameEn, statusCode (ENT-SEC-001); roles multi-select (ENT-SEC-003). Buttons: Activate/Deactivate → REQ-SEC-031/REQ-SEC-011; a separate "Pending sign-ups" tab lists SignupRequest rows with Approve/Reject → REQ-SEC-004/REQ-SEC-005.
### B4 — Access
Page code: SEC_USERS. Actions: VIEW (list/search), CREATE, UPDATE (incl. activate/deactivate/approve/reject), per §7.1 (RULE-SEC-007 gateway).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search users | GET | /api/v1/sec/users | filters, paging | Page\<User\> | — | REQ-SEC-009 |
| create user | POST | /api/v1/sec/users | user fields | User | — | REQ-SEC-009 |
| update user | PUT | /api/v1/sec/users/{id} | user fields | User | — | REQ-SEC-009 |
| assign roles | PUT | /api/v1/sec/users/{id}/roles | role ids | User with roles | — | REQ-SEC-010 |
| deactivate user | DELETE | /api/v1/sec/users/{id} | id | confirmation | RULE (session termination, REQ-SEC-011) | REQ-SEC-011 |
| reactivate user | PATCH | /api/v1/sec/users/{id} | status=ACTIVE | User | — | REQ-SEC-031 |
| approve/reject signup | PATCH | /api/v1/sec/signup-requests/{id} | decision | User (on approve) / SignupRequest (on reject) | — | REQ-SEC-004, REQ-SEC-005 |

## SCR-REQ-SEC-005 — الأدوار والصلاحيات (محرر المنح الثلاثي) / Roles & permissions (3-level grant editor)
### B1 — Definition
Purpose      : إدارة الأدوار ومنحها الوحدات ثم الشاشات ثم الإجراءات، بالترتيب الهرمي.
Entities     : ENT-SEC-002, ENT-SEC-004, ENT-SEC-005, ENT-SEC-006, ENT-SEC-007, ENT-SEC-008, ENT-SEC-009
Operations   : search, create, read, update, deactivate (role); create/delete (module/screen/action grants)
Users        : مسؤول الأمان
Navigation   : SEC → Authorization → Roles & permissions; from: SEC_USERS (role reference)
Content shape: true hierarchy (parent/child) — module → screen → action tree per role
Traces       : REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-020, REQ-SEC-030
Composite    : Master (role list) + Detail (3-level grant tree) = ONE screen requirement
### B2 — Search / list
Filters: role code/name, active flag — correspond to result columns.
### B3 — Input
Role fields: code, nameAr, nameEn, description. Grant tree: check a module (→ REQ-SEC-012), then screens within it (→ REQ-SEC-013/RULE-SEC-001 blocks illegal ones), then actions within a checked screen (→ REQ-SEC-014/RULE-SEC-002, RULE-SEC-007 VIEW gateway); unchecking a module cascades (REQ-SEC-015/RULE-SEC-003). A conflicting-action pair (RULE-SEC-005) blocks the second grant with its message.
### B4 — Access
Page code: SEC_ROLES. Actions: VIEW, CREATE, UPDATE, DELETE (deactivate role), plus grant-tree edits under UPDATE.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search roles | GET | /api/v1/sec/roles | filters, paging | Page\<Role\> | — | REQ-SEC-012 |
| create role | POST | /api/v1/sec/roles | role fields | Role | — | REQ-SEC-012 |
| grant module | POST | /api/v1/sec/roles/{id}/modules | moduleId | RoleModuleGrant | — | REQ-SEC-012 |
| revoke module | DELETE | /api/v1/sec/roles/{id}/modules/{moduleId} | — | confirmation | RULE-SEC-003 | REQ-SEC-015 |
| grant screen | POST | /api/v1/sec/roles/{id}/screens | screenId | RoleScreenGrant | RULE-SEC-001 | REQ-SEC-013 |
| grant action | POST | /api/v1/sec/roles/{id}/actions | actionId | RoleActionGrant | RULE-SEC-002, RULE-SEC-005, RULE-SEC-007 | REQ-SEC-014, REQ-SEC-020, REQ-SEC-030 |

## SCR-REQ-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry
### B1 — Definition
Purpose      : عرض وإدارة ما سجّلته كل وحدة مستهلكة من وحدات/شاشات/إجراءات كبيانات.
Entities     : ENT-SEC-004, ENT-SEC-005, ENT-SEC-006
Operations   : search, read, deactivate (modules/screens/actions arrive via each module's own registration call, not typed here by hand)
Users        : مسؤول الأمان / مطوّر الوحدة المستهلكة
Navigation   : SEC → Authorization → Module/screen/action registry
Content shape: true hierarchy (module → screen → action)
Traces       : REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019
Composite    : Master-detail tree = ONE screen requirement
### B2 — Search / list
Filters: module code, screen page code — correspond to result columns.
### B3 — Input
Read-mostly: registration itself happens via the registering module's own onboarding call (REQ-SEC-016/017/019); this screen's own edit surface is limited to deactivating a stale row.
### B4 — Access
Page code: SEC_MODULE_REGISTRY. Actions: VIEW, UPDATE (deactivate only).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| register module | POST | /api/v1/sec/registry/modules | code, nameAr, nameEn | ModuleRegistry | — | REQ-SEC-016 |
| register screen | POST | /api/v1/sec/registry/screens | moduleCode, pageCode, nameAr, nameEn | ScreenRegistry | RULE-SEC-004 | REQ-SEC-017, REQ-SEC-018 |
| register action | POST | /api/v1/sec/registry/actions | pageCode, actionCode, nameAr, nameEn | ActionRegistry | — | REQ-SEC-019 |
| search registry | GET | /api/v1/sec/registry | filters, paging | Page\<registry rows\> | — | REQ-SEC-016 |

## SCR-REQ-SEC-007 — لوحة تحكم الأمان / Admin dashboard
### B1 — Definition
Purpose      : عرض حالة الأمان العامة للمنصة بشكل حي.
Entities     : ENT-SEC-001, ENT-SEC-002, ENT-SEC-010, ENT-SEC-011
Operations   : read (aggregate figures)
Users        : مسؤول الأمان (لكل عنصر لوحة تحكم بمقتضى صلاحيته الخاصة)
Navigation   : SEC → Monitoring → Dashboard; to: SCR-REQ-SEC-008 (audit), SCR-REQ-SEC-009 (sessions)
Content shape: other (dashboard — a grid of independent widgets, not a record/list)
Traces       : REQ-SEC-022, REQ-SEC-023
Composite    : single screen (widgets are not separate screen requirements)
### B2 — Search / list
Not applicable — aggregate widgets, not a browsable list.
### B3 — Input
Read-only; no data entry.
### B4 — Access
Page code: SEC_DASHBOARD. Action: VIEW; each widget additionally requires the VIEW permission of the screen it summarizes (REQ-SEC-023) — e.g. the active-sessions widget requires SEC_SESSIONS VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| dashboard summary | GET | /api/v1/sec/dashboard | — | live aggregate figures per widget the caller may see | — | REQ-SEC-022, REQ-SEC-023 |

## SCR-REQ-SEC-008 — سجل التدقيق / Audit log
### B1 — Definition
Purpose      : تصفح وتصدير سجل الأحداث الأمنية غير القابل للتعديل.
Entities     : ENT-SEC-011
Operations   : search, export
Users        : مسؤول الأمان
Navigation   : SEC → Monitoring → Audit log; from: SCR-REQ-SEC-007
Content shape: flat record (append-only list)
Traces       : REQ-SEC-024, REQ-SEC-025, REQ-SEC-026
Composite    : single screen (search list; no entry — audit rows are never hand-created)
### B2 — Search / list
Filters: eventTypeCode, actorUserId, date range — each corresponds to a result column.
### B3 — Input
Not applicable — no create/update; rows are system-appended only (REQ-SEC-024).
### B4 — Access
Page code: SEC_AUDIT_LOG. Action: VIEW (search + export share the same permission — export is not a separate mutation).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search audit log | GET | /api/v1/sec/audit-log | filters, paging | Page\<AuditLogEntry\> | — | REQ-SEC-025 |
| export audit log | GET | /api/v1/sec/audit-log/export | filters | CSV file | — | REQ-SEC-026 |

## SCR-REQ-SEC-009 — إدارة الجلسات النشطة / Active sessions management
### B1 — Definition
Purpose      : عرض الجلسات الحية وإنهاء أي منها قسريًا عند الحاجة.
Entities     : ENT-SEC-010
Operations   : search, terminate
Users        : مسؤول الأمان
Navigation   : SEC → Monitoring → Active sessions; from: SCR-REQ-SEC-007
Content shape: flat record (live list)
Traces       : REQ-SEC-027, REQ-SEC-028
Composite    : single screen (search list + a terminate action; no separate entry form)
### B2 — Search / list
Filters: user, IP address — correspond to result columns.
### B3 — Input
Not applicable for create/update; the only mutation is "Terminate" per row → REQ-SEC-028.
### B4 — Access
Page code: SEC_SESSIONS. Actions: VIEW, DELETE (terminate, RULE-SEC-007 gateway applies).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| list active sessions | GET | /api/v1/sec/sessions | filters, paging | Page\<ActiveSession\> | — | REQ-SEC-027 |
| terminate session | DELETE | /api/v1/sec/sessions/{id} | id | confirmation | — | REQ-SEC-028 |

## SCR-REQ-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu
### B1 — Definition
Purpose      : عرض قائمة تنقّل لكل مستخدم مبنية من منحه الفعلية فقط.
Entities     : ENT-SEC-004, ENT-SEC-005, ENT-SEC-007, ENT-SEC-008
Operations   : read (rendered on every authenticated page load)
Users        : أي مستخدم مصادَق
Navigation   : rendered globally; not itself a destination
Content shape: other (navigation component, not a record/list)
Traces       : REQ-SEC-021, REQ-SEC-032, REQ-SEC-033
Composite    : single global component = ONE screen requirement (not per-module)
### B2 — Search / list
Not applicable.
### B3 — Input
Not applicable — read-only, derived.
### B4 — Access
No page code of its own (it is not a securable destination); its content is filtered
per-user by the same module/screen grants each target page already enforces (REQ-SEC-033).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| effective menu | GET | /api/v1/sec/menu | — | modules → screens tree, effective grants only | — | REQ-SEC-021, REQ-SEC-032 |

# STANDALONE

## Traceability matrix
| P0.5 | REQ | AC | RULE | ENT | SCR-REQ |
|---|---|---|---|---|---|
| US-SEC-001 | REQ-SEC-001, REQ-SEC-002 | AC-SEC-001, AC-SEC-002 | — | ENT-SEC-001, ENT-SEC-010, ENT-SEC-011 | SCR-REQ-SEC-001 |
| US-SEC-002 | REQ-SEC-003, REQ-SEC-004, REQ-SEC-005 | AC-SEC-003…005 | — | ENT-SEC-013, ENT-SEC-001 | SCR-REQ-SEC-002, SCR-REQ-SEC-004 |
| US-SEC-003 | REQ-SEC-006, REQ-SEC-007, REQ-SEC-008 | AC-SEC-006…008 | RULE-SEC-006 | ENT-SEC-012, ENT-SEC-001 | SCR-REQ-SEC-003 |
| US-SEC-004 | REQ-SEC-009, REQ-SEC-010, REQ-SEC-011, REQ-SEC-031 | AC-SEC-009…011, AC-SEC-031 | — | ENT-SEC-001, ENT-SEC-002, ENT-SEC-003, ENT-SEC-010 | SCR-REQ-SEC-004 |
| US-SEC-005 | REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-030 | AC-SEC-012…015, AC-SEC-030 | RULE-SEC-001, RULE-SEC-002, RULE-SEC-003, RULE-SEC-007 | ENT-SEC-002, ENT-SEC-004…009 | SCR-REQ-SEC-005 |
| US-SEC-006 | REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019 | AC-SEC-016…019 | RULE-SEC-004 | ENT-SEC-004, ENT-SEC-005, ENT-SEC-006 | SCR-REQ-SEC-006 |
| US-SEC-007 | REQ-SEC-020 | AC-SEC-020 | RULE-SEC-005 | ENT-SEC-001, ENT-SEC-003, ENT-SEC-006, ENT-SEC-009 | SCR-REQ-SEC-005 |
| US-SEC-008 | REQ-SEC-021, REQ-SEC-032, REQ-SEC-033 | AC-SEC-021, AC-SEC-032, AC-SEC-033 | — | ENT-SEC-004, ENT-SEC-005, ENT-SEC-007, ENT-SEC-008 | SCR-REQ-SEC-010 |
| US-SEC-009 | REQ-SEC-022, REQ-SEC-023 | AC-SEC-022, AC-SEC-023 | — | ENT-SEC-001, ENT-SEC-002, ENT-SEC-010, ENT-SEC-011 | SCR-REQ-SEC-007 |
| US-SEC-010 | REQ-SEC-024, REQ-SEC-025, REQ-SEC-026 | AC-SEC-024…026 | — | ENT-SEC-011 | SCR-REQ-SEC-008 |
| US-SEC-011 | REQ-SEC-027, REQ-SEC-028 | AC-SEC-027, AC-SEC-028 | — | ENT-SEC-010 | SCR-REQ-SEC-009 |
| US-SEC-012 | REQ-SEC-029 | AC-SEC-029 | — | ENT-SEC-012 | SCR-REQ-SEC-003 |

Every story traces to ≥1 REQ; every REQ traces to ≥1 AC; every RULE traces to a REQ;
every SCR-REQ traces to ≥1 REQ (rows above). No orphan, no dangling id.

## Decisions applied
| DEFAULT / ADR | What | Source | Override / status |
|---|---|---|---|
| DEFAULT | Password-reset token expiry = 30 minutes | domain best practice (A7 note) | configurable; non-breaking |
| DEFAULT | USER_STATUS/AUDIT_EVENT_TYPE/SIGNUP_STATUS initial lookup values | profiles/erp.yaml conventions.lookups + lookup-module-plan-en.md §3 | extend the value set as new events/states are needed; non-breaking |
No ADR was raised — no ambiguity reached the breaking/non-breaking fork of §9; every
point was settled by business policies, PRD stories, the registries or the knowledge
source, or documented above as a plain DEFAULT.

## Access summary
| Page code | Screen | VIEW | CREATE | UPDATE | DELETE | Custom |
|---|---|---|---|---|---|---|
| SEC_LOGIN | Login | public | — | — | — | — |
| SEC_SIGNUP | Sign-up | public | — | — | — | — |
| SEC_PWD_RESET | Forgot/reset password | public | — | — | — | — |
| SEC_USERS | Users | role-granted | role-granted | role-granted (incl. activate/deactivate, approve/reject signup) | — | — |
| SEC_ROLES | Roles & permissions | role-granted | role-granted | role-granted (grant tree edits) | role-granted (deactivate role) | — |
| SEC_MODULE_REGISTRY | Module/screen/action registry | role-granted | (via registering module's own call) | role-granted (deactivate row) | — | — |
| SEC_DASHBOARD | Admin dashboard | role-granted (+ per-widget VIEW of its source screen) | — | — | — | — |
| SEC_AUDIT_LOG | Audit log | role-granted | — | — | — | export (shares VIEW) |
| SEC_SESSIONS | Active sessions | role-granted | — | — | role-granted (terminate) | — |
| (menu) | Dynamic menu | derived from the above — no page code of its own | — | — | — | — |
Every action beyond VIEW additionally requires VIEW on the same screen (RULE-SEC-007).
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: backend-execution-plan (SEC)>>>
# BACKEND EXECUTION PLAN — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Dialect : postgresql16
Framework : spring-boot-java (profile.stack.backend.framework)
Inputs : srs (v1, PRD-approved), db-script (v1), registry-srs (v1), registry-db (v1)
Open ADRs : 1 — erp/decisions/SEC/ (ADR-SEC-001, carried from P2; no new ADR this stage)
══════════════════════════════════════════════════════════════════

## PRE-GENERATION EXTRACTION — SEC v1 (working set; not part of the plan proper)

```
── FROM srs ──────────────────────────────────────────────────────────────
ENTITIES      13 — ENT-SEC-001..013, all kind=security (SRS A3)
REQUIREMENTS  33 — REQ-SEC-001..033 (SRS A4), each with ≥1 AC-SEC-*
RULES         7 — RULE-SEC-001..007 (SRS A5), full text reused verbatim below
SCREENS       10 — SCR-REQ-SEC-001..010 (SRS Part B), each composite per profile.conventions.composite_screen
PERMISSIONS   SEC_PAGES page codes + PERM_<PAGE_CODE>_<ACTION>, gateway VIEW (SRS §7.1 / Access summary)
LOOKUPS       USER_STATUS, SIGNUP_STATUS, AUDIT_EVENT_TYPE (SRS A6) — CHECK-constrained in v1 per ADR-SEC-001
BUSINESS CODE none — no SEC entity has a platform-numbered business code (SRS §3.3 NUMBERING test: all "No")
── FROM db-script ────────────────────────────────────────────────────────
TABLES        13 tables, exact names SEC_USER … SEC_SIGNUP_REQUEST (db-script-sec.md §3 BLOCK 2/3)
PK GENERATION every table: `GENERATED ALWAYS AS IDENTITY` (postgresql16 identity clause, db-script §3 header)
COLUMNS       104 DBF-SEC-001..104, exact names/types/null/default per db-script §1 and §6
CONSTRAINTS   PK_*, UQ_*, CHK_*, FK_* per db-script §3 BLOCK 5; INDEXES IDX_* per BLOCK 7
XM            none — SEC is ROOT (db-script §2 XM REGISTER: empty)
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   none (SEC is ROOT)
EXISTING LOOKUP KEYS        USER_STATUS, SIGNUP_STATUS, AUDIT_EVENT_TYPE (registry-db-sec.md — reused, not recreated)
ID RANGES already used      API: none yet (this is the first use) · QR: none yet (this is the first use)
──────────────────────────────────────────────────────────────────────────
No row required §2A.3 extraction-failure handling — every field bound cleanly.
```

## EXECUTION PLAN INDEX — SEC v1 — backend-execution-plan-sec.md
Profile: erp · dialect: postgresql16 · framework: spring-boot-java
Open ADRs: 1 — decisions/SEC/ (ADR-SEC-001, non-breaking, carried from P2)

**ENTITY REGISTRY**
| ENT | Name | Table | Business code | Operations |
|---|---|---|---|---|
| ENT-SEC-001 | User | SEC_USER | none | create, read, search, update, activate, deactivate |
| ENT-SEC-002 | Role | SEC_ROLE | none | create, read, search, update, deactivate |
| ENT-SEC-003 | UserRoleAssignment | SEC_USER_ROLE | none | create, read (list), delete |
| ENT-SEC-004 | ModuleRegistry | SEC_MODULE_REG | none | create, read, search, deactivate |
| ENT-SEC-005 | ScreenRegistry | SEC_SCREEN_REG | none | create, read, search, deactivate |
| ENT-SEC-006 | ActionRegistry | SEC_ACTION_REG | none | create, read, search, deactivate |
| ENT-SEC-007 | RoleModuleGrant | SEC_ROLE_MODULE_GRANT | none | create, read (list), delete |
| ENT-SEC-008 | RoleScreenGrant | SEC_ROLE_SCREEN_GRANT | none | create, read (list), delete |
| ENT-SEC-009 | RoleActionGrant | SEC_ROLE_ACTION_GRANT | none | create, read (list), delete |
| ENT-SEC-010 | ActiveSession | SEC_ACTIVE_SESSION | none | create (system), read (list), terminate |
| ENT-SEC-011 | AuditLogEntry | SEC_AUDIT_LOG | none | create (system, append-only), read, search |
| ENT-SEC-012 | PasswordResetToken | SEC_PWD_RESET_TOKEN | none | create (system), read (validate), invalidate |
| ENT-SEC-013 | SignupRequest | SEC_SIGNUP_REQUEST | none | create, read, search, approve, reject |

**FIELD REGISTRY** (full binding detail: DB Alignment Manifest §below)
| DBF | Property | Read-only | ENT |
|---|---|---|---|
| DBF-SEC-001 | userPk | Yes | ENT-SEC-001 |
| DBF-SEC-002 | username | No | ENT-SEC-001 |
| DBF-SEC-003 | email | No | ENT-SEC-001 |
| DBF-SEC-004 | passwordHash | Yes | ENT-SEC-001 |
| DBF-SEC-005 | fullNameAr | No | ENT-SEC-001 |
| DBF-SEC-006 | fullNameEn | No | ENT-SEC-001 |
| DBF-SEC-007 | statusCode | Yes | ENT-SEC-001 |
| DBF-SEC-008 | lastLoginAt | Yes | ENT-SEC-001 |
| DBF-SEC-009 | isActiveFl | Yes | ENT-SEC-001 |
| DBF-SEC-010 | createdBy | Yes | ENT-SEC-001 |
| DBF-SEC-011 | createdAt | Yes | ENT-SEC-001 |
| DBF-SEC-012 | updatedBy | Yes | ENT-SEC-001 |
| DBF-SEC-013 | updatedAt | Yes | ENT-SEC-001 |
| DBF-SEC-014 | rolePk | Yes | ENT-SEC-002 |
| DBF-SEC-015 | code | No | ENT-SEC-002 |
| DBF-SEC-016 | nameAr | No | ENT-SEC-002 |
| DBF-SEC-017 | nameEn | No | ENT-SEC-002 |
| DBF-SEC-018 | descriptionAr | No | ENT-SEC-002 |
| DBF-SEC-019 | descriptionEn | No | ENT-SEC-002 |
| DBF-SEC-020 | isActiveFl | Yes | ENT-SEC-002 |
| DBF-SEC-021 | createdBy | Yes | ENT-SEC-002 |
| DBF-SEC-022 | createdAt | Yes | ENT-SEC-002 |
| DBF-SEC-023 | updatedBy | Yes | ENT-SEC-002 |
| DBF-SEC-024 | updatedAt | Yes | ENT-SEC-002 |
| DBF-SEC-025 | userRolePk | Yes | ENT-SEC-003 |
| DBF-SEC-026 | userId | No | ENT-SEC-003 |
| DBF-SEC-027 | roleId | No | ENT-SEC-003 |
| DBF-SEC-028 | assignedBy | Yes | ENT-SEC-003 |
| DBF-SEC-029 | assignedAt | Yes | ENT-SEC-003 |
| DBF-SEC-030 | moduleRegPk | Yes | ENT-SEC-004 |
| DBF-SEC-031 | code | No | ENT-SEC-004 |
| DBF-SEC-032 | nameAr | No | ENT-SEC-004 |
| DBF-SEC-033 | nameEn | No | ENT-SEC-004 |
| DBF-SEC-034 | isActiveFl | Yes | ENT-SEC-004 |
| DBF-SEC-035 | createdBy | Yes | ENT-SEC-004 |
| DBF-SEC-036 | createdAt | Yes | ENT-SEC-004 |
| DBF-SEC-037 | updatedBy | Yes | ENT-SEC-004 |
| DBF-SEC-038 | updatedAt | Yes | ENT-SEC-004 |
| DBF-SEC-039 | screenRegPk | Yes | ENT-SEC-005 |
| DBF-SEC-040 | pageCode | No | ENT-SEC-005 |
| DBF-SEC-041 | moduleId | No | ENT-SEC-005 |
| DBF-SEC-042 | nameAr | No | ENT-SEC-005 |
| DBF-SEC-043 | nameEn | No | ENT-SEC-005 |
| DBF-SEC-044 | isActiveFl | Yes | ENT-SEC-005 |
| DBF-SEC-045 | createdBy | Yes | ENT-SEC-005 |
| DBF-SEC-046 | createdAt | Yes | ENT-SEC-005 |
| DBF-SEC-047 | updatedBy | Yes | ENT-SEC-005 |
| DBF-SEC-048 | updatedAt | Yes | ENT-SEC-005 |
| DBF-SEC-049 | actionRegPk | Yes | ENT-SEC-006 |
| DBF-SEC-050 | permissionCode | Yes | ENT-SEC-006 |
| DBF-SEC-051 | screenId | No | ENT-SEC-006 |
| DBF-SEC-052 | actionCode | No | ENT-SEC-006 |
| DBF-SEC-053 | nameAr | No | ENT-SEC-006 |
| DBF-SEC-054 | nameEn | No | ENT-SEC-006 |
| DBF-SEC-055 | isActiveFl | Yes | ENT-SEC-006 |
| DBF-SEC-056 | createdBy | Yes | ENT-SEC-006 |
| DBF-SEC-057 | createdAt | Yes | ENT-SEC-006 |
| DBF-SEC-058 | updatedBy | Yes | ENT-SEC-006 |
| DBF-SEC-059 | updatedAt | Yes | ENT-SEC-006 |
| DBF-SEC-060 | roleModuleGrantPk | Yes | ENT-SEC-007 |
| DBF-SEC-061 | roleId | No | ENT-SEC-007 |
| DBF-SEC-062 | moduleId | No | ENT-SEC-007 |
| DBF-SEC-063 | grantedBy | Yes | ENT-SEC-007 |
| DBF-SEC-064 | grantedAt | Yes | ENT-SEC-007 |
| DBF-SEC-065 | roleScreenGrantPk | Yes | ENT-SEC-008 |
| DBF-SEC-066 | roleId | No | ENT-SEC-008 |
| DBF-SEC-067 | screenId | No | ENT-SEC-008 |
| DBF-SEC-068 | grantedBy | Yes | ENT-SEC-008 |
| DBF-SEC-069 | grantedAt | Yes | ENT-SEC-008 |
| DBF-SEC-070 | roleActionGrantPk | Yes | ENT-SEC-009 |
| DBF-SEC-071 | roleId | No | ENT-SEC-009 |
| DBF-SEC-072 | actionId | No | ENT-SEC-009 |
| DBF-SEC-073 | grantedBy | Yes | ENT-SEC-009 |
| DBF-SEC-074 | grantedAt | Yes | ENT-SEC-009 |
| DBF-SEC-075 | activeSessionPk | Yes | ENT-SEC-010 |
| DBF-SEC-076 | userId | Yes | ENT-SEC-010 |
| DBF-SEC-077 | tokenRef | Yes | ENT-SEC-010 |
| DBF-SEC-078 | startedAt | Yes | ENT-SEC-010 |
| DBF-SEC-079 | lastActivityAt | Yes | ENT-SEC-010 |
| DBF-SEC-080 | ipAddress | Yes | ENT-SEC-010 |
| DBF-SEC-081 | terminatedAt | Yes | ENT-SEC-010 |
| DBF-SEC-082 | terminatedBy | Yes | ENT-SEC-010 |
| DBF-SEC-083 | auditLogPk | Yes | ENT-SEC-011 |
| DBF-SEC-084 | eventTypeCode | Yes | ENT-SEC-011 |
| DBF-SEC-085 | actorUserId | Yes | ENT-SEC-011 |
| DBF-SEC-086 | occurredAt | Yes | ENT-SEC-011 |
| DBF-SEC-087 | targetRef | Yes | ENT-SEC-011 |
| DBF-SEC-088 | detailsAr | Yes | ENT-SEC-011 |
| DBF-SEC-089 | detailsEn | Yes | ENT-SEC-011 |
| DBF-SEC-090 | ipAddress | Yes | ENT-SEC-011 |
| DBF-SEC-091 | pwdResetTokenPk | Yes | ENT-SEC-012 |
| DBF-SEC-092 | userId | Yes | ENT-SEC-012 |
| DBF-SEC-093 | tokenHash | Yes | ENT-SEC-012 |
| DBF-SEC-094 | requestedAt | Yes | ENT-SEC-012 |
| DBF-SEC-095 | expiresAt | Yes | ENT-SEC-012 |
| DBF-SEC-096 | usedAt | Yes | ENT-SEC-012 |
| DBF-SEC-097 | signupRequestPk | Yes | ENT-SEC-013 |
| DBF-SEC-098 | email | No | ENT-SEC-013 |
| DBF-SEC-099 | fullNameAr | No | ENT-SEC-013 |
| DBF-SEC-100 | fullNameEn | No | ENT-SEC-013 |
| DBF-SEC-101 | submittedAt | Yes | ENT-SEC-013 |
| DBF-SEC-102 | statusCode | Yes | ENT-SEC-013 |
| DBF-SEC-103 | reviewedBy | Yes | ENT-SEC-013 |
| DBF-SEC-104 | reviewedAt | Yes | ENT-SEC-013 |

**API REGISTRY** (full blocks: §Phase 3 SVC-API below)
| API | Operation | Verb | Path | Traces (REQ, DBF) |
|---|---|---|---|---|
| API-SEC-001 | login | POST | /api/v1/sec/auth/login | REQ-SEC-001,REQ-SEC-002 · DBF-SEC-002,DBF-SEC-004,DBF-SEC-007,DBF-SEC-075..078 |
| API-SEC-002 | submit sign-up | POST | /api/v1/sec/auth/signup | REQ-SEC-003 · DBF-SEC-098,DBF-SEC-099,DBF-SEC-100,DBF-SEC-101,DBF-SEC-102 |
| API-SEC-003 | request password reset | POST | /api/v1/sec/auth/password-reset/request | REQ-SEC-006,REQ-SEC-029 · DBF-SEC-092,DBF-SEC-093,DBF-SEC-094,DBF-SEC-095 |
| API-SEC-004 | complete password reset | POST | /api/v1/sec/auth/password-reset/complete | REQ-SEC-007,REQ-SEC-008 · DBF-SEC-093,DBF-SEC-095,DBF-SEC-096,DBF-SEC-004 |
| API-SEC-005 | search users | GET | /api/v1/sec/users | REQ-SEC-009 · DBF-SEC-002,DBF-SEC-003,DBF-SEC-005,DBF-SEC-006,DBF-SEC-007 |
| API-SEC-006 | create user | POST | /api/v1/sec/users | REQ-SEC-009 · DBF-SEC-002,DBF-SEC-003,DBF-SEC-005,DBF-SEC-006,DBF-SEC-007 |
| API-SEC-007 | update user | PUT | /api/v1/sec/users/{id} | REQ-SEC-009 · DBF-SEC-003,DBF-SEC-005,DBF-SEC-006 |
| API-SEC-008 | assign roles to user | PUT | /api/v1/sec/users/{id}/roles | REQ-SEC-010 · DBF-SEC-026,DBF-SEC-027,DBF-SEC-028,DBF-SEC-029 |
| API-SEC-009 | deactivate user | DELETE | /api/v1/sec/users/{id} | REQ-SEC-011 · DBF-SEC-007,DBF-SEC-009,DBF-SEC-081,DBF-SEC-082 |
| API-SEC-010 | reactivate user | PATCH | /api/v1/sec/users/{id} | REQ-SEC-031 · DBF-SEC-007,DBF-SEC-009 |
| API-SEC-011 | approve/reject signup | PATCH | /api/v1/sec/signup-requests/{id} | REQ-SEC-004,REQ-SEC-005 · DBF-SEC-102,DBF-SEC-103,DBF-SEC-104,DBF-SEC-001 |
| API-SEC-012 | search roles | GET | /api/v1/sec/roles | REQ-SEC-012 · DBF-SEC-015,DBF-SEC-016,DBF-SEC-017,DBF-SEC-020 |
| API-SEC-013 | create role | POST | /api/v1/sec/roles | REQ-SEC-012 · DBF-SEC-015,DBF-SEC-016,DBF-SEC-017,DBF-SEC-018,DBF-SEC-019 |
| API-SEC-014 | grant module to role | POST | /api/v1/sec/roles/{id}/modules | REQ-SEC-012 · DBF-SEC-061,DBF-SEC-062,DBF-SEC-063,DBF-SEC-064 |
| API-SEC-015 | revoke module grant | DELETE | /api/v1/sec/roles/{id}/modules/{moduleId} | REQ-SEC-015 · DBF-SEC-061,DBF-SEC-062,DBF-SEC-066,DBF-SEC-071 |
| API-SEC-016 | grant screen to role | POST | /api/v1/sec/roles/{id}/screens | REQ-SEC-013 · DBF-SEC-066,DBF-SEC-067,DBF-SEC-068,DBF-SEC-069 |
| API-SEC-017 | grant action to role | POST | /api/v1/sec/roles/{id}/actions | REQ-SEC-014,REQ-SEC-020,REQ-SEC-030 · DBF-SEC-071,DBF-SEC-072,DBF-SEC-073,DBF-SEC-074 |
| API-SEC-018 | register module | POST | /api/v1/sec/registry/modules | REQ-SEC-016 · DBF-SEC-031,DBF-SEC-032,DBF-SEC-033 |
| API-SEC-019 | register screen | POST | /api/v1/sec/registry/screens | REQ-SEC-017,REQ-SEC-018 · DBF-SEC-040,DBF-SEC-041,DBF-SEC-042,DBF-SEC-043 |
| API-SEC-020 | register action | POST | /api/v1/sec/registry/actions | REQ-SEC-019 · DBF-SEC-050,DBF-SEC-051,DBF-SEC-052,DBF-SEC-053,DBF-SEC-054 |
| API-SEC-021 | search registry | GET | /api/v1/sec/registry | REQ-SEC-016 · DBF-SEC-031,DBF-SEC-040,DBF-SEC-050 |
| API-SEC-022 | dashboard summary | GET | /api/v1/sec/dashboard | REQ-SEC-022,REQ-SEC-023 · DBF-SEC-007,DBF-SEC-076,DBF-SEC-081,DBF-SEC-084,DBF-SEC-086 |
| API-SEC-023 | search audit log | GET | /api/v1/sec/audit-log | REQ-SEC-025 · DBF-SEC-084,DBF-SEC-085,DBF-SEC-086 |
| API-SEC-024 | export audit log | GET | /api/v1/sec/audit-log/export | REQ-SEC-026 · DBF-SEC-084,DBF-SEC-085,DBF-SEC-086,DBF-SEC-087,DBF-SEC-088,DBF-SEC-089 |
| API-SEC-025 | list active sessions | GET | /api/v1/sec/sessions | REQ-SEC-027 · DBF-SEC-076,DBF-SEC-079,DBF-SEC-081 |
| API-SEC-026 | terminate session | DELETE | /api/v1/sec/sessions/{id} | REQ-SEC-028 · DBF-SEC-081,DBF-SEC-082 |
| API-SEC-027 | effective menu | GET | /api/v1/sec/menu | REQ-SEC-021,REQ-SEC-032,REQ-SEC-033 · DBF-SEC-031,DBF-SEC-040,DBF-SEC-061,DBF-SEC-066 |

**RULE REGISTRY**
| RULE | Name | Scope (ENT) | Message ar/en ✓ |
|---|---|---|---|
| RULE-SEC-001 | No screen grant without its module grant | ENT-SEC-008 | ✓ |
| RULE-SEC-002 | No action grant without its screen grant | ENT-SEC-009 | ✓ |
| RULE-SEC-003 | Cascade revoke on module-grant removal | ENT-SEC-007 | ✓ |
| RULE-SEC-004 | No screen under an unregistered module | ENT-SEC-005 | ✓ |
| RULE-SEC-005 | Prevent conflicting actions on one user | ENT-SEC-003, ENT-SEC-009 | ✓ |
| RULE-SEC-006 | Reject expired or used reset token | ENT-SEC-012 | ✓ |
| RULE-SEC-007 | VIEW as the screen-level gateway action | ENT-SEC-009 | ✓ |

**SCREEN REGISTRY**
| Screen | Type | ENT | Permission names |
|---|---|---|---|
| SEC_LOGIN | public | ENT-SEC-001 | (none — public) |
| SEC_SIGNUP | public | ENT-SEC-013 | (none — public) |
| SEC_PWD_RESET | public | ENT-SEC-012 | (none — public) |
| SEC_USERS | secured | ENT-SEC-001 | PERM_SEC_USERS_VIEW, PERM_SEC_USERS_CREATE, PERM_SEC_USERS_UPDATE |
| SEC_ROLES | secured | ENT-SEC-002 | PERM_SEC_ROLES_VIEW, PERM_SEC_ROLES_CREATE, PERM_SEC_ROLES_UPDATE, PERM_SEC_ROLES_DELETE |
| SEC_MODULE_REGISTRY | secured | ENT-SEC-004 | PERM_SEC_MODULE_REGISTRY_VIEW, PERM_SEC_MODULE_REGISTRY_UPDATE |
| SEC_DASHBOARD | secured | (aggregate) | PERM_SEC_DASHBOARD_VIEW (+ per-widget source-screen VIEW) |
| SEC_AUDIT_LOG | secured | ENT-SEC-011 | PERM_SEC_AUDIT_LOG_VIEW |
| SEC_SESSIONS | secured | ENT-SEC-010 | PERM_SEC_SESSIONS_VIEW, PERM_SEC_SESSIONS_DELETE |
| (menu) | derived | — | none of its own — filtered per target page's own permissions |

**LOOKUP REGISTRY**
| Key | Used in field | ENT |
|---|---|---|
| USER_STATUS | statusCode | ENT-SEC-001 |
| SIGNUP_STATUS | statusCode | ENT-SEC-013 |
| AUDIT_EVENT_TYPE | eventTypeCode | ENT-SEC-011 |

**QRC SUMMARY** (agent reference only — full catalog below)
38 QR ids, QR-SEC-001..038 — see §Query Reference Catalog.

**DB ALIGNMENT** — see manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 0 (SEC is ROOT)
**SECURITY** — 7 secured screens × role-driven grants (no fixed role count — data-driven per RBAC)

## DB Alignment Manifest — SEC v1
DBF-* │ ENT-* │ plan property │ plan type │ XM-* │ status — sourced by lookup from db-script-sec.md §1; not reproduced here beyond the four bound columns.

All 104 rows: **status ✓ (aligned), XM — (none)** for every row; property/type below (Java types, `profile.stack.backend.framework` = spring-boot-java; TIMESTAMPTZ→Instant, VARCHAR/TEXT→String, BOOLEAN→Boolean, BIGINT identity→Long).

| DBF | ENT | property | type |
|---|---|---|---|
| DBF-SEC-001 | ENT-SEC-001 | userPk | Long |
| DBF-SEC-002 | ENT-SEC-001 | username | String |
| DBF-SEC-003 | ENT-SEC-001 | email | String |
| DBF-SEC-004 | ENT-SEC-001 | passwordHash | String |
| DBF-SEC-005 | ENT-SEC-001 | fullNameAr | String |
| DBF-SEC-006 | ENT-SEC-001 | fullNameEn | String |
| DBF-SEC-007 | ENT-SEC-001 | statusCode | String |
| DBF-SEC-008 | ENT-SEC-001 | lastLoginAt | Instant |
| DBF-SEC-009 | ENT-SEC-001 | isActiveFl | Boolean |
| DBF-SEC-010 | ENT-SEC-001 | createdBy | String |
| DBF-SEC-011 | ENT-SEC-001 | createdAt | Instant |
| DBF-SEC-012 | ENT-SEC-001 | updatedBy | String |
| DBF-SEC-013 | ENT-SEC-001 | updatedAt | Instant |
| DBF-SEC-014 | ENT-SEC-002 | rolePk | Long |
| DBF-SEC-015 | ENT-SEC-002 | code | String |
| DBF-SEC-016 | ENT-SEC-002 | nameAr | String |
| DBF-SEC-017 | ENT-SEC-002 | nameEn | String |
| DBF-SEC-018 | ENT-SEC-002 | descriptionAr | String |
| DBF-SEC-019 | ENT-SEC-002 | descriptionEn | String |
| DBF-SEC-020 | ENT-SEC-002 | isActiveFl | Boolean |
| DBF-SEC-021 | ENT-SEC-002 | createdBy | String |
| DBF-SEC-022 | ENT-SEC-002 | createdAt | Instant |
| DBF-SEC-023 | ENT-SEC-002 | updatedBy | String |
| DBF-SEC-024 | ENT-SEC-002 | updatedAt | Instant |
| DBF-SEC-025 | ENT-SEC-003 | userRolePk | Long |
| DBF-SEC-026 | ENT-SEC-003 | userId | Long |
| DBF-SEC-027 | ENT-SEC-003 | roleId | Long |
| DBF-SEC-028 | ENT-SEC-003 | assignedBy | String |
| DBF-SEC-029 | ENT-SEC-003 | assignedAt | Instant |
| DBF-SEC-030 | ENT-SEC-004 | moduleRegPk | Long |
| DBF-SEC-031 | ENT-SEC-004 | code | String |
| DBF-SEC-032 | ENT-SEC-004 | nameAr | String |
| DBF-SEC-033 | ENT-SEC-004 | nameEn | String |
| DBF-SEC-034 | ENT-SEC-004 | isActiveFl | Boolean |
| DBF-SEC-035 | ENT-SEC-004 | createdBy | String |
| DBF-SEC-036 | ENT-SEC-004 | createdAt | Instant |
| DBF-SEC-037 | ENT-SEC-004 | updatedBy | String |
| DBF-SEC-038 | ENT-SEC-004 | updatedAt | Instant |
| DBF-SEC-039 | ENT-SEC-005 | screenRegPk | Long |
| DBF-SEC-040 | ENT-SEC-005 | pageCode | String |
| DBF-SEC-041 | ENT-SEC-005 | moduleId | Long |
| DBF-SEC-042 | ENT-SEC-005 | nameAr | String |
| DBF-SEC-043 | ENT-SEC-005 | nameEn | String |
| DBF-SEC-044 | ENT-SEC-005 | isActiveFl | Boolean |
| DBF-SEC-045 | ENT-SEC-005 | createdBy | String |
| DBF-SEC-046 | ENT-SEC-005 | createdAt | Instant |
| DBF-SEC-047 | ENT-SEC-005 | updatedBy | String |
| DBF-SEC-048 | ENT-SEC-005 | updatedAt | Instant |
| DBF-SEC-049 | ENT-SEC-006 | actionRegPk | Long |
| DBF-SEC-050 | ENT-SEC-006 | permissionCode | String |
| DBF-SEC-051 | ENT-SEC-006 | screenId | Long |
| DBF-SEC-052 | ENT-SEC-006 | actionCode | String |
| DBF-SEC-053 | ENT-SEC-006 | nameAr | String |
| DBF-SEC-054 | ENT-SEC-006 | nameEn | String |
| DBF-SEC-055 | ENT-SEC-006 | isActiveFl | Boolean |
| DBF-SEC-056 | ENT-SEC-006 | createdBy | String |
| DBF-SEC-057 | ENT-SEC-006 | createdAt | Instant |
| DBF-SEC-058 | ENT-SEC-006 | updatedBy | String |
| DBF-SEC-059 | ENT-SEC-006 | updatedAt | Instant |
| DBF-SEC-060 | ENT-SEC-007 | roleModuleGrantPk | Long |
| DBF-SEC-061 | ENT-SEC-007 | roleId | Long |
| DBF-SEC-062 | ENT-SEC-007 | moduleId | Long |
| DBF-SEC-063 | ENT-SEC-007 | grantedBy | String |
| DBF-SEC-064 | ENT-SEC-007 | grantedAt | Instant |
| DBF-SEC-065 | ENT-SEC-008 | roleScreenGrantPk | Long |
| DBF-SEC-066 | ENT-SEC-008 | roleId | Long |
| DBF-SEC-067 | ENT-SEC-008 | screenId | Long |
| DBF-SEC-068 | ENT-SEC-008 | grantedBy | String |
| DBF-SEC-069 | ENT-SEC-008 | grantedAt | Instant |
| DBF-SEC-070 | ENT-SEC-009 | roleActionGrantPk | Long |
| DBF-SEC-071 | ENT-SEC-009 | roleId | Long |
| DBF-SEC-072 | ENT-SEC-009 | actionId | Long |
| DBF-SEC-073 | ENT-SEC-009 | grantedBy | String |
| DBF-SEC-074 | ENT-SEC-009 | grantedAt | Instant |
| DBF-SEC-075 | ENT-SEC-010 | activeSessionPk | Long |
| DBF-SEC-076 | ENT-SEC-010 | userId | Long |
| DBF-SEC-077 | ENT-SEC-010 | tokenRef | String |
| DBF-SEC-078 | ENT-SEC-010 | startedAt | Instant |
| DBF-SEC-079 | ENT-SEC-010 | lastActivityAt | Instant |
| DBF-SEC-080 | ENT-SEC-010 | ipAddress | String |
| DBF-SEC-081 | ENT-SEC-010 | terminatedAt | Instant |
| DBF-SEC-082 | ENT-SEC-010 | terminatedBy | String |
| DBF-SEC-083 | ENT-SEC-011 | auditLogPk | Long |
| DBF-SEC-084 | ENT-SEC-011 | eventTypeCode | String |
| DBF-SEC-085 | ENT-SEC-011 | actorUserId | Long |
| DBF-SEC-086 | ENT-SEC-011 | occurredAt | Instant |
| DBF-SEC-087 | ENT-SEC-011 | targetRef | String |
| DBF-SEC-088 | ENT-SEC-011 | detailsAr | String |
| DBF-SEC-089 | ENT-SEC-011 | detailsEn | String |
| DBF-SEC-090 | ENT-SEC-011 | ipAddress | String |
| DBF-SEC-091 | ENT-SEC-012 | pwdResetTokenPk | Long |
| DBF-SEC-092 | ENT-SEC-012 | userId | Long |
| DBF-SEC-093 | ENT-SEC-012 | tokenHash | String |
| DBF-SEC-094 | ENT-SEC-012 | requestedAt | Instant |
| DBF-SEC-095 | ENT-SEC-012 | expiresAt | Instant |
| DBF-SEC-096 | ENT-SEC-012 | usedAt | Instant |
| DBF-SEC-097 | ENT-SEC-013 | signupRequestPk | Long |
| DBF-SEC-098 | ENT-SEC-013 | email | String |
| DBF-SEC-099 | ENT-SEC-013 | fullNameAr | String |
| DBF-SEC-100 | ENT-SEC-013 | fullNameEn | String |
| DBF-SEC-101 | ENT-SEC-013 | submittedAt | Instant |
| DBF-SEC-102 | ENT-SEC-013 | statusCode | String |
| DBF-SEC-103 | ENT-SEC-013 | reviewedBy | String |
| DBF-SEC-104 | ENT-SEC-013 | reviewedAt | Instant |

## Query Reference Catalog (QR-SEC-*)

> Logical specification only — never executable code; the implementer rewrites every
> entry with real entity classes and the project's query strategy (§5 warning, engine).

| QR | Operation | Phase | API | Entity | Kind | Intent |
|---|---|---|---|---|---|---|
| QR-SEC-001 | FIND_ONE | SVC-API | API-SEC-001 | ENT-SEC-001 | FIND_ONE by username | resolve login identity |
| QR-SEC-002 | SAVE | SVC-API | API-SEC-002 | ENT-SEC-013 | SAVE | create pending sign-up |
| QR-SEC-003 | SAVE | SVC-API | API-SEC-003 | ENT-SEC-012 | SAVE | issue reset token |
| QR-SEC-004 | UPDATE | SVC-API | API-SEC-004 | ENT-SEC-001, ENT-SEC-012 | UPDATE | set new password hash + mark token used |
| QR-SEC-005 | FIND_BY_CRITERIA | SVC-API | API-SEC-005 | ENT-SEC-001 | FIND_BY_CRITERIA | search users |
| QR-SEC-006 | SAVE | SVC-API | API-SEC-006 | ENT-SEC-001 | SAVE | create user |
| QR-SEC-007 | UPDATE | SVC-API | API-SEC-007 | ENT-SEC-001 | UPDATE | update user profile fields |
| QR-SEC-008 | SAVE | SVC-API | API-SEC-008 | ENT-SEC-003 | SAVE (batch) | assign roles to user |
| QR-SEC-009 | UPDATE | SVC-API | API-SEC-009 | ENT-SEC-001, ENT-SEC-010 | UPDATE | deactivate user + terminate its sessions |
| QR-SEC-010 | UPDATE | SVC-API | API-SEC-010 | ENT-SEC-001 | UPDATE | reactivate user |
| QR-SEC-011 | UPDATE | SVC-API | API-SEC-011 | ENT-SEC-013, ENT-SEC-001 | UPDATE / SAVE | approve (creates user) / reject sign-up |
| QR-SEC-012 | FIND_BY_CRITERIA | SVC-API | API-SEC-012 | ENT-SEC-002 | FIND_BY_CRITERIA | search roles |
| QR-SEC-013 | SAVE | SVC-API | API-SEC-013 | ENT-SEC-002 | SAVE | create role |
| QR-SEC-014 | SAVE | SVC-API | API-SEC-014 | ENT-SEC-007 | SAVE | grant module |
| QR-SEC-015 | DELETE | SVC-API | API-SEC-015 | ENT-SEC-007 | DELETE | revoke module grant |
| QR-SEC-016 | SAVE | SVC-API | API-SEC-016 | ENT-SEC-008 | SAVE | grant screen |
| QR-SEC-017 | SAVE | SVC-API | API-SEC-017 | ENT-SEC-009 | SAVE | grant action |
| QR-SEC-018 | SAVE | SVC-API | API-SEC-018 | ENT-SEC-004 | SAVE | register module |
| QR-SEC-019 | SAVE | SVC-API | API-SEC-019 | ENT-SEC-005 | SAVE | register screen |
| QR-SEC-020 | SAVE | SVC-API | API-SEC-020 | ENT-SEC-006 | SAVE | register action |
| QR-SEC-021 | FIND_BY_CRITERIA | SVC-API | API-SEC-021 | ENT-SEC-004, ENT-SEC-005, ENT-SEC-006 | FIND_BY_CRITERIA | browse registry tree |
| QR-SEC-022 | AGGREGATE | SVC-API | API-SEC-022 | ENT-SEC-001, ENT-SEC-010, ENT-SEC-011, ENT-SEC-002 | AGGREGATE | dashboard figures (6 widget sub-counts) |
| QR-SEC-023 | FIND_BY_CRITERIA | SVC-API | API-SEC-023 | ENT-SEC-011 | FIND_BY_CRITERIA | search audit log |
| QR-SEC-024 | FIND_BY_CRITERIA | SVC-API | API-SEC-024 | ENT-SEC-011 | FIND_BY_CRITERIA | audit log rows for export |
| QR-SEC-025 | FIND_BY_CRITERIA | SVC-API | API-SEC-025 | ENT-SEC-010 | FIND_BY_CRITERIA | non-terminated sessions |
| QR-SEC-026 | UPDATE | SVC-API | API-SEC-026 | ENT-SEC-010 | UPDATE | terminate session |
| QR-SEC-027 | FIND_BY_CRITERIA | SVC-API | API-SEC-027 | ENT-SEC-004, ENT-SEC-005, ENT-SEC-007, ENT-SEC-008 | FIND_BY_CRITERIA | effective menu tree for caller |
| QR-SEC-028 | EXISTS | SVC-API | API-SEC-016 | ENT-SEC-007 | EXISTS | RULE-SEC-001: role holds the screen's module grant? |
| QR-SEC-029 | EXISTS | SVC-API | API-SEC-017 | ENT-SEC-008 | EXISTS | RULE-SEC-002: role holds the action's screen grant? |
| QR-SEC-030 | EXISTS | SVC-API | API-SEC-017 | ENT-SEC-009 | EXISTS | RULE-SEC-007: role holds VIEW on the action's screen? |
| QR-SEC-031 | EXISTS | SVC-API | API-SEC-008, API-SEC-017 | ENT-SEC-009 | EXISTS | RULE-SEC-005: user already holds the conflicting action? |
| QR-SEC-032 | FIND_ALL | SVC-API | API-SEC-015 | ENT-SEC-008, ENT-SEC-009 | FIND_ALL | RULE-SEC-003: dependent screen/action grants for cascade |
| QR-SEC-033 | EXISTS | SVC-API | API-SEC-006 | ENT-SEC-001 | EXISTS | uniqueness: username / email |
| QR-SEC-034 | EXISTS | SVC-API | API-SEC-013 | ENT-SEC-002 | EXISTS | uniqueness: role code |
| QR-SEC-035 | EXISTS | SVC-API | API-SEC-018 | ENT-SEC-004 | EXISTS | uniqueness: module code |
| QR-SEC-036 | EXISTS | SVC-API | API-SEC-019 | ENT-SEC-004, ENT-SEC-005 | EXISTS | RULE-SEC-004: module registered? + uniqueness: page code |
| QR-SEC-037 | EXISTS | SVC-API | API-SEC-020 | ENT-SEC-005, ENT-SEC-006 | EXISTS | screen exists? + uniqueness: permission code |
| QR-SEC-038 | EXISTS | SVC-API | API-SEC-004 | ENT-SEC-012 | EXISTS | RULE-SEC-006: token unexpired and unused? |

Standard operation defaults (engine §5) apply to every QR above unless noted; no QR overrides
paging/filter/transaction defaults except where its row states otherwise. Join governance:
every QR above is single-table or a documented FK join within SEC only (no cross-module join
— SEC has zero XM); no QR joins to resolve a lookup label (`statusCode`/`eventTypeCode` are
returned as codes; the frontend resolves the display label).

---

<!-- PHASE:CORE:START traces=REQ-SEC-033 -->
## PHASE 1 — CORE

**Layers** (`profile.stack.backend.layers`): controller → service → mapper → domain → repository.
- **controller**: HTTP binding, request validation shape (types/required), maps DTO ↔ command; never queries the repository directly; never contains a RULE-* check.
- **service**: orchestration — loads, validates every RULE-*, integrates (none for SEC — zero XM), persists via repository; the sole place RULE-* logic runs; the sole place PERM_* is asserted before any mutation proceeds.
- **mapper**: entity ↔ DTO conversion only; no business logic, no query.
- **domain**: entity classes; domain-behaviour placement = **in entity methods** for single-entity invariants (e.g. `User.deactivate()` flips `isActiveFl`/`statusCode`), and in the service layer for any rule spanning more than one entity (e.g. RULE-SEC-001/002/003/005/007, which read another table).
- **repository**: Spring Data JPA repositories, one per entity/table; every non-trivial query is a named method backed by a `QR-SEC-*` spec (§Query Reference Catalog); no business logic.

**Error signalling**: `LocalizedException → {code, messageAr, messageEn}`. Runtime `code` format:
`SEC-<3-digit-sequence>` (module-scoped, stated once here so `api-verify` can assert on it — e.g.
`SEC-001` for the first catalog row). Every catalog row (§Error Catalog) is registered as a
static enum/constant the controller-advice layer maps to the envelope; `messageAr`/`messageEn`
are copied character-perfect from the SRS RULE message or from this plan where PLATFORM-STD.

**Transaction scope defaults**: `READ_ONLY` for every `FIND_*`/`EXISTS`/`AGGREGATE` QR;
`READ_WRITE` for every `SAVE`/`UPDATE`/`DELETE` QR; no `REQUIRES_NEW` anywhere in SEC v1
(no QR overrides this).

**Search contract**: request shape `{filters: {...}, page, size, sort}`; allowed sort fields =
exactly the columns listed as filters in each screen's SRS B2; paging `Page<T>`
(`profile.stack.backend.api.paging`); an empty result is success with empty content, never
"not found" (§5 FIND_BY_CRITERIA default).

**Audit fields**: `createdBy, createdAt, updatedBy, updatedAt` are framework-filled (from the
authenticated principal + server clock) — never present in a create/update request DTO, never
set by a mapper or service method explicitly; the same applies to `grantedBy/grantedAt`,
`assignedBy/assignedAt`, `reviewedBy/reviewedAt`, `terminatedBy/terminatedAt`,
`occurredAt/actorUserId` (all system-set for the same reason, per Field Registry read-only=Yes).

**Type mapping** (`profile.stack.db.syntax_map` postgresql16 → Java, spring-boot-java):
| postgresql16 | Java |
|---|---|
| GENERATED ALWAYS AS IDENTITY | Long |
| VARCHAR(n) | String |
| BOOLEAN | Boolean |
| TIMESTAMPTZ | Instant |
| TEXT | String |
No `NUMERIC` column exists in SEC v1 (no money/decimal field) — not applicable this module; a
future decimal field would map to `BigDecimal` per the same syntax_map row, stated here for
completeness, no deviation ADR needed since none is used.

**Lookup values**: `statusCode` (User, SignupRequest) and `eventTypeCode` (AuditLogEntry) are
returned and accepted as plain strings (the lookup CODE) everywhere in every API below — never
as an enum type in a DTO, never as a numeric id. Per ADR-SEC-001 they are CHECK-constrained in
v1, not FK-backed; the service layer still validates the incoming code against the same closed
set the CHECK constraint enforces, so an invalid code is rejected with a catalog error before it
ever reaches the database.

**Numbering**: not applicable — SEC has no entity with a platform-numbered business code
(Pre-generation extraction: "BUSINESS CODE: none").

**Workflow engine**: forbidden (`profiles/erp.yaml → conventions.workflow_engine`) — every
status transition below (User, SignupRequest) is a plain field update guarded by a RULE or a
dedicated action endpoint, never a workflow definition.

**Languages**: every name field (`nameAr`/`nameEn`, `fullNameAr`/`fullNameEn`,
`descriptionAr`/`descriptionEn`, `detailsAr`/`detailsEn`) and every catalog message is present
in both `ar` and `en` in every DTO and every response — a single-language value anywhere is
incomplete per §Error Catalog / §6.1 rule.

**Cross-module contract placement**: not applicable this version — SEC has zero XM (it is
ROOT); no inversion-of-control interface is consumed by SEC. SEC itself is consumed by every
future module through its own REST surface (§SVC-API below), not through an injected interface.

**Cross-cutting authorization (REQ-SEC-033)**: a single servlet filter / method-level
interceptor runs before every secured controller method (i.e. every API below except
API-SEC-001..004, which are pre-authentication): it resolves the caller's effective module,
screen and action grants (via the same read path as API-SEC-027's effective-menu query) and
denies with a catalog error (§Error Catalog, `SEC-403`) before the controller method body runs
if the module grant, the screen's VIEW grant (RULE-SEC-007), or the specific action grant is
missing. This single mechanism is what §SEC-BE (Phase 7) and every API's "Security" line below
refer to — it is declared once here, never re-implemented per endpoint.
<!-- PHASE:CORE:END -->

<!-- PHASE:DATA-DOM:START traces=REQ-SEC-001,REQ-SEC-003,REQ-SEC-006,REQ-SEC-009,REQ-SEC-010,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-016,REQ-SEC-017,REQ-SEC-019,REQ-SEC-024 -->
## PHASE 2 — DATA-DOM

Entity count is 13 (≥ the engine's self-check threshold for a split) — grouped below under
`SUB:DATA-DOM-MASTER` (reference/master-like registries), `SUB:DATA-DOM-TRANSACTIONAL` (grant
and session/audit rows with a lifecycle or an occurrence timestamp), and
`SUB:DATA-DOM-LOOKUP` (none — SEC owns no `kind: lookup` entity in its own SRS; its lookup
*values* live in USER_STATUS/SIGNUP_STATUS/AUDIT_EVENT_TYPE, which are CHECK constraints on
other entities, not their own ENT — this SUB is intentionally empty and stated so, not omitted).

<!-- SUB:DATA-DOM-MASTER:START traces=REQ-SEC-009,REQ-SEC-012,REQ-SEC-016,REQ-SEC-017,REQ-SEC-019 -->
### SUB — DATA-DOM-MASTER

#### ENT-SEC-001 — User      kind: security
BINDINGS: table `SEC_USER` · PK `userPk` (DBF-SEC-001) · PK generation `GENERATED ALWAYS AS IDENTITY` · db-script v1
BUSINESS CODE: none (§3.3 test: no)
DEFAULT FIELDS: `security` kind carries no profile-fixed default set (SRS A3 note); every field below is explicit
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-SEC-001 | userPk | user_pk | Long | NOT NULL | Yes | PK_SEC_USER | معرّف المستخدم / User id |
| DBF-SEC-002 | username | username | String | NOT NULL | No | UQ_SEC_USER_USERNAME | اسم المستخدم / Username |
| DBF-SEC-003 | email | email | String | NOT NULL | No | UQ_SEC_USER_EMAIL | البريد الإلكتروني / Email |
| DBF-SEC-004 | passwordHash | password_hash | String | NOT NULL | Yes | — | تجزئة كلمة المرور / Password hash |
| DBF-SEC-005 | fullNameAr | full_name_ar | String | NOT NULL | No | — | الاسم الكامل (عربي) / Full name (Arabic) |
| DBF-SEC-006 | fullNameEn | full_name_en | String | NOT NULL | No | — | الاسم الكامل (إنجليزي) / Full name (English) |
| DBF-SEC-007 | statusCode | status_code | String | NOT NULL | Yes | CHK_SEC_USER_STATUS | الحالة / Status |
| DBF-SEC-008 | lastLoginAt | last_login_at | Instant | NULL | Yes | — | آخر دخول / Last login |
| DBF-SEC-009 | isActiveFl | is_active_fl | Boolean | NOT NULL | Yes | — | نشط / Active |
| DBF-SEC-010 | createdBy | created_by | String | NOT NULL | Yes | — | أُنشئ بواسطة / Created by |
| DBF-SEC-011 | createdAt | created_at | Instant | NOT NULL | Yes | — | تاريخ الإنشاء / Created at |
| DBF-SEC-012 | updatedBy | updated_by | String | NULL | Yes | — | حُدّث بواسطة / Updated by |
| DBF-SEC-013 | updatedAt | updated_at | Instant | NULL | Yes | — | تاريخ التحديث / Updated at |
DTO MEMBERSHIP: create-request excludes {userPk, passwordHash(raw password field instead, hashed server-side), statusCode, lastLoginAt, isActiveFl, audit}; update-request excludes {userPk, username, passwordHash, statusCode, isActiveFl, audit} (username immutable after create; password changes only via API-SEC-004); response includes all except passwordHash (never serialized).
LOOKUP FIELDS: `statusCode` → key `USER_STATUS` → GET /api/v1/mdl/lookups?type=USER_STATUS (once MDL exists; v1 validates server-side against the closed set per ADR-SEC-001) — stores the code, never a numeric FK.
DOMAIN RULES: none scoped to User alone (RULE-SEC-005 scopes ENT-SEC-003/009, cited there).
STATE MACHINE: `statusCode` (USER_STATUS) — values PENDING/ACTIVE/DISABLED; initial ACTIVE (direct create, API-SEC-006) or PENDING (via sign-up approval, API-SEC-011); transitions PENDING→ACTIVE (API-SEC-011, actor: administrator), ACTIVE→DISABLED (API-SEC-009, actor: administrator), DISABLED→ACTIVE (API-SEC-010, actor: administrator); no terminal state; no invalid-transition RULE beyond "the four listed transitions are the only ones exposed" (enforced by which endpoint exists, not a DB CHECK on the transition itself).
CROSS-MODULE: none (SEC is ROOT).
REPOSITORY OPS → QR-SEC-001 (FIND_ONE by username), QR-SEC-005 (FIND_BY_CRITERIA), QR-SEC-006 (SAVE), QR-SEC-007 (UPDATE), QR-SEC-009 (UPDATE, deactivate), QR-SEC-010 (UPDATE, reactivate), QR-SEC-033 (EXISTS, uniqueness).

#### ENT-SEC-002 — Role      kind: security
BINDINGS: table `SEC_ROLE` · PK `rolePk` (DBF-SEC-014) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-SEC-014 | rolePk | role_pk | Long | NOT NULL | Yes | PK_SEC_ROLE | معرّف الدور / Role id |
| DBF-SEC-015 | code | code | String | NOT NULL | No | UQ_SEC_ROLE_CODE | رمز الدور / Role code |
| DBF-SEC-016 | nameAr | name_ar | String | NOT NULL | No | — | اسم الدور (عربي) / Role name (Arabic) |
| DBF-SEC-017 | nameEn | name_en | String | NOT NULL | No | — | اسم الدور (إنجليزي) / Role name (English) |
| DBF-SEC-018 | descriptionAr | description_ar | String | NULL | No | — | الوصف (عربي) / Description (Arabic) |
| DBF-SEC-019 | descriptionEn | description_en | String | NULL | No | — | الوصف (إنجليزي) / Description (English) |
| DBF-SEC-020 | isActiveFl | is_active_fl | Boolean | NOT NULL | Yes | — | نشط / Active |
| DBF-SEC-021..024 | createdBy/createdAt/updatedBy/updatedAt | created_by/created_at/updated_by/updated_at | String/Instant | see db-script | Yes | — | audit / audit |
DTO MEMBERSHIP: create-request excludes {rolePk, isActiveFl, audit}; update-request excludes {rolePk, code, isActiveFl, audit} (code immutable); response includes all.
LOOKUP FIELDS: none.
DOMAIN RULES: none scoped to Role alone.
STATE MACHINE: `isActiveFl` binary only — not applicable for a diagram (SRS A7).
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-012 (FIND_BY_CRITERIA), QR-SEC-013 (SAVE), QR-SEC-034 (EXISTS, uniqueness).

#### ENT-SEC-004 — ModuleRegistry      kind: security
BINDINGS: table `SEC_MODULE_REG` · PK `moduleRegPk` (DBF-SEC-030) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none — `code` is the platform's own module prefix (factory.ids), supplied by the registering module, not system-generated.
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-SEC-030 | moduleRegPk | module_reg_pk | Long | NOT NULL | Yes | PK_SEC_MODULE_REG | معرّف الوحدة المسجّلة / Registered module id |
| DBF-SEC-031 | code | code | String | NOT NULL | No | UQ_SEC_MODULE_REG_CODE | رمز الوحدة / Module code |
| DBF-SEC-032 | nameAr | name_ar | String | NOT NULL | No | — | اسم الوحدة (عربي) / Module name (Arabic) |
| DBF-SEC-033 | nameEn | name_en | String | NOT NULL | No | — | اسم الوحدة (إنجليزي) / Module name (English) |
| DBF-SEC-034..038 | isActiveFl/audit | is_active_fl/… | Boolean/String/Instant | see db-script | Yes | — | — |
DTO MEMBERSHIP: create-request excludes {moduleRegPk, isActiveFl, audit}; update: deactivate only, no field-level update endpoint; response includes all.
LOOKUP FIELDS: none.
DOMAIN RULES: none scoped alone (RULE-SEC-004 scopes ENT-SEC-005, cited there).
STATE MACHINE: binary active flag only — not applicable.
CROSS-MODULE: none — this table IS the shared registry every future module writes into; no XM row exists because a registration is a plain REST call to SEC (API-SEC-018), not a physical FK from another module's schema.
REPOSITORY OPS → QR-SEC-018 (SAVE), QR-SEC-021 (FIND_BY_CRITERIA), QR-SEC-035 (EXISTS, uniqueness).

#### ENT-SEC-005 — ScreenRegistry      kind: security
BINDINGS: table `SEC_SCREEN_REG` · PK `screenRegPk` (DBF-SEC-039) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none — `pageCode` is caller-supplied per SEC_PAGES convention, not system-generated.
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-SEC-039 | screenRegPk | screen_reg_pk | Long | NOT NULL | Yes | PK_SEC_SCREEN_REG | معرّف الشاشة المسجّلة / Registered screen id |
| DBF-SEC-040 | pageCode | page_code | String | NOT NULL | No | UQ_SEC_SCREEN_REG_PAGE | رمز الصفحة / Page code |
| DBF-SEC-041 | moduleId | module_id | Long | NOT NULL | No | FK_SCREEN_REG_MODULE | الوحدة / Module |
| DBF-SEC-042 | nameAr | name_ar | String | NOT NULL | No | — | اسم الشاشة (عربي) / Screen name (Arabic) |
| DBF-SEC-043 | nameEn | name_en | String | NOT NULL | No | — | اسم الشاشة (إنجليزي) / Screen name (English) |
| DBF-SEC-044..048 | isActiveFl/audit | … | — | see db-script | Yes | — | — |
DTO MEMBERSHIP: create-request excludes {screenRegPk, isActiveFl, audit}; response includes all.
LOOKUP FIELDS: none.
DOMAIN RULES: **RULE-SEC-004** — Scope ENT-SEC-005 · Trigger: on create (screen registration) · Statement: "The system shall reject a screen registration whose module code has no ModuleRegistry row." · Message ar: "الوحدة غير مسجّلة" / en: "Module is not registered" · DB enforcement: `FK_SCREEN_REG_MODULE` (structural — the FK constraint itself makes an unregistered module impossible; the service layer pre-checks with QR-SEC-036 to raise the friendly catalog error before the DB would reject it) · owner layer: service (pre-check) + database (hard guarantee).
STATE MACHINE: binary active flag only — not applicable.
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-019 (SAVE), QR-SEC-036 (EXISTS: module registered + page code unique).

#### ENT-SEC-006 — ActionRegistry      kind: security
BINDINGS: table `SEC_ACTION_REG` · PK `actionRegPk` (DBF-SEC-049) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none — `permissionCode` is derived (`PERM_<pageCode>_<actionCode>`), never entered a second time as seed data (single source of truth).
FIELDS:
| DBF | property | column | type | null | read-only | constraint | label-ar / label-en |
|---|---|---|---|---|---|---|---|
| DBF-SEC-049 | actionRegPk | action_reg_pk | Long | NOT NULL | Yes | PK_SEC_ACTION_REG | معرّف الإجراء المسجّل / Registered action id |
| DBF-SEC-050 | permissionCode | permission_code | String | NOT NULL | Yes (derived) | UQ_SEC_ACTION_REG_PERM | رمز الصلاحية / Permission code |
| DBF-SEC-051 | screenId | screen_id | Long | NOT NULL | No | FK_ACTION_REG_SCREEN | الشاشة / Screen |
| DBF-SEC-052 | actionCode | action_code | String | NOT NULL | No | — | الإجراء / Action |
| DBF-SEC-053 | nameAr | name_ar | String | NOT NULL | No | — | اسم الإجراء (عربي) / Action name (Arabic) |
| DBF-SEC-054 | nameEn | name_en | String | NOT NULL | No | — | اسم الإجراء (إنجليزي) / Action name (English) |
| DBF-SEC-055..059 | isActiveFl/audit | … | — | see db-script | Yes | — | — |
DTO MEMBERSHIP: create-request excludes {actionRegPk, permissionCode (server-derived), isActiveFl, audit}; response includes all, including the derived `permissionCode`.
LOOKUP FIELDS: none — `actionCode` is not lookup-backed (open set: VIEW/CREATE/UPDATE/DELETE + module-declared custom codes, SRS A3 note).
DOMAIN RULES: none scoped alone.
STATE MACHINE: binary active flag only — not applicable.
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-020 (SAVE), QR-SEC-037 (EXISTS: screen exists + permission code unique).
<!-- SUB:DATA-DOM-MASTER:END -->

<!-- SUB:DATA-DOM-TRANSACTIONAL:START traces=REQ-SEC-001,REQ-SEC-010,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-024 -->
### SUB — DATA-DOM-TRANSACTIONAL

#### ENT-SEC-003 — UserRoleAssignment      kind: security
BINDINGS: table `SEC_USER_ROLE` · PK `userRolePk` (DBF-SEC-025) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS:
| DBF | property | column | type | null | read-only | constraint |
|---|---|---|---|---|---|---|
| DBF-SEC-025 | userRolePk | user_role_pk | Long | NOT NULL | Yes | PK_SEC_USER_ROLE |
| DBF-SEC-026 | userId | user_id | Long | NOT NULL | No | FK_USER_ROLE_USER, UQ_SEC_USER_ROLE_USER_ROLE |
| DBF-SEC-027 | roleId | role_id | Long | NOT NULL | No | FK_USER_ROLE_ROLE, UQ_SEC_USER_ROLE_USER_ROLE |
| DBF-SEC-028 | assignedBy | assigned_by | String | NOT NULL | Yes | — |
| DBF-SEC-029 | assignedAt | assigned_at | Instant | NOT NULL | Yes | — |
DTO MEMBERSHIP: request = `{roleIds: [Long]}` (batch); response = list of `{roleId, code, nameAr, nameEn}`.
DOMAIN RULES: **RULE-SEC-005** applies here too (assigning a role that carries an action already held via another role, for a conflicting pair, is rejected — same QR-SEC-031 check as API-SEC-017, cited fully under ENT-SEC-009 below to avoid duplication).
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-008 (SAVE, batch), QR-SEC-031 (EXISTS, conflict check, shared with API-SEC-017).

#### ENT-SEC-007 — RoleModuleGrant      kind: security
BINDINGS: table `SEC_ROLE_MODULE_GRANT` · PK `roleModuleGrantPk` (DBF-SEC-060) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS:
| DBF | property | column | type | null | read-only | constraint |
|---|---|---|---|---|---|---|
| DBF-SEC-060 | roleModuleGrantPk | role_module_grant_pk | Long | NOT NULL | Yes | PK_SEC_ROLE_MODULE_GRANT |
| DBF-SEC-061 | roleId | role_id | Long | NOT NULL | No | FK_ROLE_MODULE_GRANT_ROLE, UQ_SEC_ROLE_MODULE_GRANT_ROLE_MODULE |
| DBF-SEC-062 | moduleId | module_id | Long | NOT NULL | No | FK_ROLE_MODULE_GRANT_MODULE, UQ_SEC_ROLE_MODULE_GRANT_ROLE_MODULE |
| DBF-SEC-063 | grantedBy | granted_by | String | NOT NULL | Yes | — |
| DBF-SEC-064 | grantedAt | grant_at | Instant | NOT NULL | Yes | — |
DOMAIN RULES: **RULE-SEC-003** — Scope ENT-SEC-007 · Trigger: on delete (module grant) · Statement: "The system shall delete every screen grant and action grant that module covered for that role when its module grant is revoked." · Message ar: "سيتم سحب كل منح الشاشات والإجراءات ضمن هذه الوحدة لهذا الدور" / en: "Every screen and action grant under this module for this role will be revoked" · DB enforcement: application layer (service, transactional) · owner layer: service.
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-014 (SAVE), QR-SEC-015 (DELETE), QR-SEC-032 (FIND_ALL, cascade targets).

#### ENT-SEC-008 — RoleScreenGrant      kind: security
BINDINGS: table `SEC_ROLE_SCREEN_GRANT` · PK `roleScreenGrantPk` (DBF-SEC-065) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS:
| DBF | property | column | type | null | read-only | constraint |
|---|---|---|---|---|---|---|
| DBF-SEC-065 | roleScreenGrantPk | role_screen_grant_pk | Long | NOT NULL | Yes | PK_SEC_ROLE_SCREEN_GRANT |
| DBF-SEC-066 | roleId | role_id | Long | NOT NULL | No | FK_ROLE_SCREEN_GRANT_ROLE, UQ_SEC_ROLE_SCREEN_GRANT_ROLE_SCREEN |
| DBF-SEC-067 | screenId | screen_id | Long | NOT NULL | No | FK_ROLE_SCREEN_GRANT_SCREEN, UQ_SEC_ROLE_SCREEN_GRANT_ROLE_SCREEN |
| DBF-SEC-068 | grantedBy | granted_by | String | NOT NULL | Yes | — |
| DBF-SEC-069 | grantedAt | granted_at | Instant | NOT NULL | Yes | — |
DOMAIN RULES: **RULE-SEC-001** — Scope ENT-SEC-008 · Trigger: on create (screen grant) · Statement: "The system shall prevent a screen grant for a role that does not hold the screen's module grant." · Message ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" / en: "Cannot grant a screen without first granting its module" · DB enforcement: application layer (service, via QR-SEC-028 pre-check) · owner layer: service.
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-016 (SAVE), QR-SEC-028 (EXISTS, module-grant pre-check).

#### ENT-SEC-009 — RoleActionGrant      kind: security
BINDINGS: table `SEC_ROLE_ACTION_GRANT` · PK `roleActionGrantPk` (DBF-SEC-070) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS:
| DBF | property | column | type | null | read-only | constraint |
|---|---|---|---|---|---|---|
| DBF-SEC-070 | roleActionGrantPk | role_action_grant_pk | Long | NOT NULL | Yes | PK_SEC_ROLE_ACTION_GRANT |
| DBF-SEC-071 | roleId | role_id | Long | NOT NULL | No | FK_ROLE_ACTION_GRANT_ROLE, UQ_SEC_ROLE_ACTION_GRANT_ROLE_ACTION |
| DBF-SEC-072 | actionId | action_id | Long | NOT NULL | No | FK_ROLE_ACTION_GRANT_ACTION, UQ_SEC_ROLE_ACTION_GRANT_ROLE_ACTION |
| DBF-SEC-073 | grantedBy | granted_by | String | NOT NULL | Yes | — |
| DBF-SEC-074 | grantedAt | granted_at | Instant | NOT NULL | Yes | — |
DOMAIN RULES:
**RULE-SEC-002** — Scope ENT-SEC-009 · Trigger: on create (action grant) · Statement: "The system shall prevent an action grant for a role that does not hold the action's screen grant." · Message ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" / en: "Cannot grant an action without first granting its screen" · DB enforcement: application layer (service, via QR-SEC-029) · owner layer: service.
**RULE-SEC-005** — Scope ENT-SEC-003, ENT-SEC-009 · Trigger: on create (role assignment or action grant) · Statement: "The system shall prevent assigning a user, by any combination of roles, both actions of a module-declared conflicting pair." · Message ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" / en: "This user already holds a conflicting action" · DB enforcement: application layer (service, via QR-SEC-031, checked across all of a user's roles) · owner layer: service.
**RULE-SEC-007** — Scope ENT-SEC-009 · Trigger: on evaluate (any action check) and on create (action grant, informational) · Statement: "The system shall require a role to hold the VIEW action grant on a screen before any other action grant on that screen takes effect for it." · Message ar: "يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة" / en: "The VIEW action must be granted on this screen first" · DB enforcement: application layer (service, via QR-SEC-030 at grant time + the CORE interceptor at request time) · owner layer: service.
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-017 (SAVE), QR-SEC-029 (EXISTS), QR-SEC-030 (EXISTS), QR-SEC-031 (EXISTS).

#### ENT-SEC-010 — ActiveSession      kind: security
BINDINGS: table `SEC_ACTIVE_SESSION` · PK `activeSessionPk` (DBF-SEC-075) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-SEC-075..082 — see DB Alignment Manifest; all `read-only: Yes` (system lifecycle, no client-editable field).
DTO MEMBERSHIP: no create/update request (system-created at login, API-SEC-001); response includes all except `tokenRef` (never serialized back).
DOMAIN RULES: none scoped alone.
STATE MACHINE: `terminatedAt IS NULL` = active, `terminatedAt IS NOT NULL` = terminated — binary, not applicable for a diagram.
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-025 (FIND_BY_CRITERIA, non-terminated), QR-SEC-026 (UPDATE, terminate) — also written to by API-SEC-001 (create) and API-SEC-009 (bulk-terminate on deactivate), both via the same repository, no separate QR (plain SAVE / batch UPDATE, standard defaults apply).

#### ENT-SEC-011 — AuditLogEntry      kind: security
BINDINGS: table `SEC_AUDIT_LOG` · PK `auditLogPk` (DBF-SEC-083) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-SEC-083..090 — see DB Alignment Manifest; all `read-only: Yes` (append-only, no update endpoint exists at all — immutability, POL-SEC-009).
DTO MEMBERSHIP: no create/update request exposed to any client — rows are written internally by every other API's orchestration step, never by a dedicated "create audit entry" endpoint; response (search/export) includes all fields.
DOMAIN RULES: none (the immutability itself is enforced by omission — no UPDATE/DELETE mapping exists on this repository at all, not by a DB trigger).
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-023 (FIND_BY_CRITERIA, search), QR-SEC-024 (FIND_BY_CRITERIA, export) — writes happen inline from every other service method (SAVE, standard defaults, no dedicated QR per writer to avoid 20+ near-identical entries; the write shape is always `{eventTypeCode, actorUserId, occurredAt=now(), targetRef, detailsAr, detailsEn, ipAddress}`).

#### ENT-SEC-012 — PasswordResetToken      kind: security
BINDINGS: table `SEC_PWD_RESET_TOKEN` · PK `pwdResetTokenPk` (DBF-SEC-091) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-SEC-091..096 — see DB Alignment Manifest; all `read-only: Yes` (system-managed lifecycle).
DTO MEMBERSHIP: no direct create/read/update DTO — entirely internal to API-SEC-003/004's orchestration; the client only ever sees the opaque token string delivered out-of-band (§API-SEC-003 Response).
DOMAIN RULES: **RULE-SEC-006** — Scope ENT-SEC-012 · Trigger: on submit (password reset completion) · Statement: "The system shall reject a password-reset submission whose token is expired or already used." · Message ar: "رابط إعادة التعيين غير صالح أو منتهي" / en: "This reset link is invalid or has expired" · DB enforcement: application layer (service, via QR-SEC-038) · owner layer: service. `expiresAt` DEFAULT = `requestedAt + 30 minutes` (SRS A7 DEFAULT, non-breaking).
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-003 (SAVE), QR-SEC-004 (UPDATE, on completion), QR-SEC-038 (EXISTS, validity check).

#### ENT-SEC-013 — SignupRequest      kind: security
BINDINGS: table `SEC_SIGNUP_REQUEST` · PK `signupRequestPk` (DBF-SEC-097) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-SEC-097..104 — see DB Alignment Manifest.
DTO MEMBERSHIP: create-request = `{email, fullNameAr, fullNameEn}`; no update endpoint (only approve/reject via API-SEC-011); response includes all.
LOOKUP FIELDS: `statusCode` → key `SIGNUP_STATUS` (ADR-SEC-001, same treatment as USER_STATUS).
DOMAIN RULES: none scoped alone (RULE-SEC-004/007 do not apply here).
STATE MACHINE: `statusCode` (SIGNUP_STATUS) — values PENDING/APPROVED/REJECTED; initial PENDING; transitions PENDING→APPROVED (API-SEC-011 approve, actor: administrator), PENDING→REJECTED (API-SEC-011 reject, actor: administrator); both terminal; no invalid-transition RULE beyond "only PENDING may transition."
CROSS-MODULE: none.
REPOSITORY OPS → QR-SEC-002 (SAVE), QR-SEC-011 (UPDATE, decision).
<!-- SUB:DATA-DOM-TRANSACTIONAL:END -->

<!-- SUB:DATA-DOM-LOOKUP:START traces=REQ-SEC-004 -->
### SUB — DATA-DOM-LOOKUP
Not applicable — SEC owns no `kind: lookup` `ENT` of its own this version; `USER_STATUS`,
`SIGNUP_STATUS`, `AUDIT_EVENT_TYPE` are CHECK-constrained value sets on other entities'
`statusCode`/`eventTypeCode` columns (ADR-SEC-001), not separate lookup tables/entities. This
SUB exists to satisfy the engine's grouping convention and is intentionally empty.
<!-- SUB:DATA-DOM-LOOKUP:END -->
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-SEC-001,REQ-SEC-009,REQ-SEC-012,REQ-SEC-016,REQ-SEC-022,REQ-SEC-025 -->
## PHASE 3 — SVC-API

API count = 27 ≥ 8 → split by threshold, grouped CRUD / SEARCH / INT.

<!-- SUB:SVC-API-SEARCH:START traces=REQ-SEC-009,REQ-SEC-012,REQ-SEC-016,REQ-SEC-022,REQ-SEC-025,REQ-SEC-027 -->
### SUB — SVC-API-SEARCH (read-only)

<!-- API:API-SEC-005:START traces=REQ-SEC-009,DBF-SEC-002,DBF-SEC-003,DBF-SEC-005,DBF-SEC-006,DBF-SEC-007 -->
### API-SEC-005 — search users
Endpoint     : GET /api/v1/sec/users   verb: GET
Layers       : controller → `UserController.search` ; service → `UserService.search`
Request      : query params `username`(LIKE), `email`(LIKE), `fullName`(LIKE, matches fullNameAr or fullNameEn), `statusCode`(EXACT), `page`, `size`, `sort`
Response     : 200 · `Page<UserResponse>` (userPk, username, email, fullNameAr, fullNameEn, statusCode, lastLoginAt) · envelope `ApiResponse<Page<UserResponse>>`
Validations  : none (read-only)
Errors       : none beyond platform-standard (§Error Catalog SEC-500)
Orchestration: load (QR-SEC-005 FIND_BY_CRITERIA) → map → return
Repository   : QR-SEC-005 · join NONE · transaction READ_ONLY
Security     : screen SEC_USERS · permission `PERM_SEC_USERS_VIEW`
Localization : fullNameAr/fullNameEn both returned
<!-- API:API-SEC-005:END -->

<!-- API:API-SEC-012:START traces=REQ-SEC-012,DBF-SEC-015,DBF-SEC-016,DBF-SEC-017,DBF-SEC-020 -->
### API-SEC-012 — search roles
Endpoint     : GET /api/v1/sec/roles
Layers       : controller → `RoleController.search` ; service → `RoleService.search`
Request      : query params `code`(LIKE), `name`(LIKE, nameAr or nameEn), `isActiveFl`(EXACT), `page`, `size`, `sort`
Response     : 200 · `Page<RoleResponse>` (rolePk, code, nameAr, nameEn, descriptionAr, descriptionEn, isActiveFl) · `ApiResponse<Page<RoleResponse>>`
Validations  : none
Errors       : SEC-500 only
Orchestration: load (QR-SEC-012) → map → return
Repository   : QR-SEC-012 · join NONE · transaction READ_ONLY
Security     : screen SEC_ROLES · permission `PERM_SEC_ROLES_VIEW`
Localization : nameAr/nameEn/descriptionAr/descriptionEn returned
<!-- API:API-SEC-012:END -->

<!-- API:API-SEC-021:START traces=REQ-SEC-016,DBF-SEC-031,DBF-SEC-040,DBF-SEC-050 -->
### API-SEC-021 — search registry
Endpoint     : GET /api/v1/sec/registry
Layers       : controller → `RegistryController.search` ; service → `RegistryService.search`
Request      : query params `moduleCode`(EXACT), `pageCode`(LIKE), `page`, `size`, `sort`
Response     : 200 · `Page<RegistryRowResponse>` (a module row with its nested active screens and, per screen, its active actions) · `ApiResponse<Page<RegistryRowResponse>>`
Validations  : none
Errors       : SEC-500 only
Orchestration: load (QR-SEC-021, joins SEC_MODULE_REG → SEC_SCREEN_REG → SEC_ACTION_REG, all intra-module) → assemble tree → return
Repository   : QR-SEC-021 · join intra-module (module/screen/action — same table family, not cross-module) · transaction READ_ONLY
Security     : screen SEC_MODULE_REGISTRY · permission `PERM_SEC_MODULE_REGISTRY_VIEW`
Localization : nameAr/nameEn at every level
<!-- API:API-SEC-021:END -->

<!-- API:API-SEC-022:START traces=REQ-SEC-022,REQ-SEC-023,DBF-SEC-007,DBF-SEC-076,DBF-SEC-081,DBF-SEC-084,DBF-SEC-086 -->
### API-SEC-022 — dashboard summary
Endpoint     : GET /api/v1/sec/dashboard
Layers       : controller → `DashboardController.summary` ; service → `DashboardService.summary`
Request      : none
Response     : 200 · `DashboardResponse` — six sub-figures, each present only if the caller holds that widget's source-screen VIEW permission (omitted field, not a zeroed one, when absent): `usersOverview{total,active,disabled,pendingSignups}`, `failedLogins24h{count}`, `activeSessions{count}`, `recentActivity{list of last N AuditLogEntry}`, `rolesPermissionsSummary{roleCount,privilegedRoleCount,usersPerRole}`, `onboardingFunnel{pendingSignups,stalledCount}` · `ApiResponse<DashboardResponse>`
Validations  : none — this endpoint filters its OWN output by REQ-SEC-023 (unwanted pattern) rather than rejecting the call
Errors       : SEC-500 only
Orchestration: resolve caller's effective permissions (same read path as API-SEC-027) → for each widget whose source-screen VIEW the caller holds, compute it live (QR-SEC-022 sub-queries) → assemble → return (REQ-SEC-022: every figure computed at that moment, never cached)
Repository   : QR-SEC-022 (6 independent COUNT/aggregate sub-queries against SEC_USER, SEC_ACTIVE_SESSION, SEC_AUDIT_LOG, SEC_ROLE/SEC_USER_ROLE) · join NONE (each sub-query is single-table) · transaction READ_ONLY
Security     : screen SEC_DASHBOARD · permission `PERM_SEC_DASHBOARD_VIEW` (gateway) + per-widget the widget's own source-screen VIEW (SEC_USERS, SEC_SESSIONS, SEC_AUDIT_LOG, SEC_ROLES)
Localization : recentActivity entries carry detailsAr/detailsEn
<!-- API:API-SEC-022:END -->

<!-- API:API-SEC-023:START traces=REQ-SEC-025,DBF-SEC-084,DBF-SEC-085,DBF-SEC-086 -->
### API-SEC-023 — search audit log
Endpoint     : GET /api/v1/sec/audit-log
Layers       : controller → `AuditLogController.search` ; service → `AuditLogService.search`
Request      : query params `eventTypeCode`(EXACT), `actorUserId`(EXACT), `occurredFrom`/`occurredTo`(DATE_RANGE), `page`, `size`, `sort`
Response     : 200 · `Page<AuditLogEntryResponse>` (all fields, unmodified) · `ApiResponse<Page<AuditLogEntryResponse>>`
Validations  : none
Errors       : SEC-500 only
Orchestration: load (QR-SEC-023) → return unmodified (REQ-SEC-025: "without altering any of them")
Repository   : QR-SEC-023 · join NONE · transaction READ_ONLY
Security     : screen SEC_AUDIT_LOG · permission `PERM_SEC_AUDIT_LOG_VIEW`
Localization : detailsAr/detailsEn returned
<!-- API:API-SEC-023:END -->

<!-- API:API-SEC-025:START traces=REQ-SEC-027,DBF-SEC-076,DBF-SEC-079,DBF-SEC-081 -->
### API-SEC-025 — list active sessions
Endpoint     : GET /api/v1/sec/sessions
Layers       : controller → `SessionController.search` ; service → `SessionService.search`
Request      : query params `userId`(EXACT), `ipAddress`(LIKE), `page`, `size`, `sort`
Response     : 200 · `Page<ActiveSessionResponse>` (activeSessionPk, userId, username, startedAt, lastActivityAt, ipAddress) — `tokenRef` never returned · `ApiResponse<Page<ActiveSessionResponse>>`
Validations  : filter `terminatedAt IS NULL` always applied server-side (REQ-SEC-027: "every session that has not been terminated") — not a client-supplied filter
Errors       : SEC-500 only
Orchestration: load (QR-SEC-025, filter terminatedAt IS NULL) → map → return
Repository   : QR-SEC-025 · join NONE · transaction READ_ONLY
Security     : screen SEC_SESSIONS · permission `PERM_SEC_SESSIONS_VIEW`
Localization : username shown (via userId join within SEC_USER, intra-module)
<!-- API:API-SEC-025:END -->

<!-- API:API-SEC-027:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,DBF-SEC-031,DBF-SEC-040,DBF-SEC-061,DBF-SEC-066 -->
### API-SEC-027 — effective menu
Endpoint     : GET /api/v1/sec/menu
Layers       : controller → `MenuController.effective` ; service → `MenuService.effective`
Request      : none (caller resolved from the authenticated session)
Response     : 200 · `List<ModuleMenuResponse>` — only modules the caller's effective grants hold (REQ-SEC-021/032), each with only that caller's effective granted screens beneath it · `ApiResponse<List<ModuleMenuResponse>>`
Validations  : none — the endpoint's entire behaviour IS the filter (REQ-SEC-021, REQ-SEC-032)
Errors       : SEC-500 only
Orchestration: resolve caller's roles (QR-SEC-027, join SEC_ROLE_MODULE_GRANT/SEC_ROLE_SCREEN_GRANT to SEC_MODULE_REG/SEC_SCREEN_REG, all intra-module) → union across the caller's roles → assemble modules→screens tree → return
Repository   : QR-SEC-027 · join intra-module (grant tables to registry tables) · transaction READ_ONLY
Security     : no page code of its own (SRS B4) — every authenticated caller may call it; its content is the security boundary, not a permission on itself
Localization : nameAr/nameEn at module and screen level
<!-- API:API-SEC-027:END -->
<!-- SUB:SVC-API-SEARCH:END -->

<!-- SUB:SVC-API-CRUD:START traces=REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-028,REQ-SEC-030,REQ-SEC-031 -->
### SUB — SVC-API-CRUD (single-entity mutations)

<!-- API:API-SEC-006:START traces=REQ-SEC-009,DBF-SEC-002,DBF-SEC-003,DBF-SEC-005,DBF-SEC-006,DBF-SEC-007 -->
### API-SEC-006 — create user
Endpoint     : POST /api/v1/sec/users
Layers       : controller → `UserController.create` ; service → `UserService.create`
Request      : body `{username, email, fullNameAr, fullNameEn, password, statusCode?}` — statusCode optional, defaults ACTIVE; excludes {userPk, passwordHash, lastLoginAt, isActiveFl, audit}
Response     : 201 · `UserResponse` (no passwordHash)
Validations  : uniqueness of username and email (QR-SEC-033) — violation → catalog `SEC-409-USER-DUP`
Errors       : `SEC-409-USER-DUP` (409)
Orchestration: validate uniqueness (QR-SEC-033) → hash password → persist (QR-SEC-006) → append AuditLogEntry `MODULE_GRANTED`? no — no audit event type is defined for plain user creation in SRS A6, so none is appended here (only the 14 named AUDIT_EVENT_TYPE codes apply; user-creation itself is not one of them, per SRS A6 — no invention) → return
Repository   : QR-SEC-006, QR-SEC-033 · join NONE · transaction READ_WRITE
Security     : screen SEC_USERS · permission `PERM_SEC_USERS_CREATE`
Localization : fullNameAr and fullNameEn both required
<!-- API:API-SEC-006:END -->

<!-- API:API-SEC-007:START traces=REQ-SEC-009,DBF-SEC-003,DBF-SEC-005,DBF-SEC-006 -->
### API-SEC-007 — update user
Endpoint     : PUT /api/v1/sec/users/{id}
Layers       : controller → `UserController.update` ; service → `UserService.update`
Request      : body `{email, fullNameAr, fullNameEn}` — excludes {userPk, username, passwordHash, statusCode, isActiveFl, audit}
Response     : 200 · `UserResponse`
Validations  : uniqueness of email excluding the current PK (QR-SEC-033, EXISTS default "excludes the current PK on update")
Errors       : `SEC-409-USER-DUP` (409), `SEC-404-USER` (404, id not found)
Orchestration: load (QR-SEC-001-style FIND_ONE by PK) → validate → update (QR-SEC-007) → return
Repository   : QR-SEC-007 · join NONE · transaction READ_WRITE
Security     : screen SEC_USERS · permission `PERM_SEC_USERS_UPDATE`
Localization : both name fields updatable independently
<!-- API:API-SEC-007:END -->

<!-- API:API-SEC-008:START traces=REQ-SEC-010,DBF-SEC-026,DBF-SEC-027,DBF-SEC-028,DBF-SEC-029 -->
### API-SEC-008 — assign roles to user
Endpoint     : PUT /api/v1/sec/users/{id}/roles
Layers       : controller → `UserController.assignRoles` ; service → `UserRoleService.assign`
Request      : body `{roleIds: [Long]}`
Response     : 200 · `UserResponse` with nested `roles: [{roleId, code, nameAr, nameEn}]`
Validations  : RULE-SEC-005 (full text: DATA-DOM §ENT-SEC-009) — the union of the user's existing + newly assigned roles' actions must contain no conflicting pair (QR-SEC-031) → violation `SEC-409-SOD-CONFLICT`
Errors       : `SEC-409-SOD-CONFLICT` (409), `SEC-404-USER`/`SEC-404-ROLE` (404)
Orchestration: load user + roles → check RULE-SEC-005 (QR-SEC-031) → replace the assignment set (QR-SEC-008) → append AuditLogEntry `ROLE_ASSIGNED` per added role, `ROLE_REVOKED` per removed role → return
Repository   : QR-SEC-008, QR-SEC-031 · join NONE · transaction READ_WRITE
Security     : screen SEC_USERS · permission `PERM_SEC_USERS_UPDATE`
Localization : role name fields returned in both languages
<!-- API:API-SEC-008:END -->

<!-- API:API-SEC-009:START traces=REQ-SEC-011,DBF-SEC-007,DBF-SEC-009,DBF-SEC-081,DBF-SEC-082 -->
### API-SEC-009 — deactivate user
Endpoint     : DELETE /api/v1/sec/users/{id}
Layers       : controller → `UserController.deactivate` ; service → `UserService.deactivate`
Request      : path `id`
Response     : 200 · confirmation `{userPk, statusCode: "DISABLED"}`
Validations  : none beyond existence
Errors       : `SEC-404-USER` (404)
Orchestration: load user → `User.deactivate()` (domain method: statusCode→DISABLED, isActiveFl→false) → persist (QR-SEC-009) → terminate every active session of that user (QR-SEC-026, bulk) → append AuditLogEntry `SESSION_TERMINATED` per session — this is the "immediately end that user's active sessions" half of REQ-SEC-011
Repository   : QR-SEC-009, QR-SEC-026 (bulk) · join NONE · transaction READ_WRITE
Security     : screen SEC_USERS · permission `PERM_SEC_USERS_UPDATE`
Localization : n/a (no message text beyond the confirmation)
<!-- API:API-SEC-009:END -->

<!-- API:API-SEC-010:START traces=REQ-SEC-031,DBF-SEC-007,DBF-SEC-009 -->
### API-SEC-010 — reactivate user
Endpoint     : PATCH /api/v1/sec/users/{id}
Layers       : controller → `UserController.reactivate` ; service → `UserService.reactivate`
Request      : path `id`
Response     : 200 · confirmation `{userPk, statusCode: "ACTIVE"}`
Validations  : the user must currently be DISABLED (A7 lifecycle — an ACTIVE or PENDING user cannot be "reactivated")
Errors       : `SEC-404-USER` (404), `SEC-409-INVALID-TRANSITION` (409)
Orchestration: load user → verify statusCode=DISABLED → `User.reactivate()` → persist (QR-SEC-010) → return
Repository   : QR-SEC-010 · join NONE · transaction READ_WRITE
Security     : screen SEC_USERS · permission `PERM_SEC_USERS_UPDATE`
Localization : n/a
<!-- API:API-SEC-010:END -->

<!-- API:API-SEC-011:START traces=REQ-SEC-004,REQ-SEC-005,DBF-SEC-102,DBF-SEC-103,DBF-SEC-104,DBF-SEC-001 -->
### API-SEC-011 — approve / reject signup
Endpoint     : PATCH /api/v1/sec/signup-requests/{id}
Layers       : controller → `SignupRequestController.decide` ; service → `SignupRequestService.decide`
Request      : body `{decision: "APPROVE"|"REJECT"}`
Response     : 200 · on APPROVE: the created `UserResponse`; on REJECT: the updated `SignupRequestResponse` (statusCode=REJECTED)
Validations  : the request must currently be PENDING (A7 lifecycle)
Errors       : `SEC-404-SIGNUP` (404), `SEC-409-INVALID-TRANSITION` (409)
Orchestration: load SignupRequest → verify PENDING → on APPROVE: create User (QR-SEC-006-style, statusCode=ACTIVE) + update SignupRequest (statusCode=APPROVED, reviewedBy/At) (QR-SEC-011); on REJECT: update SignupRequest (statusCode=REJECTED, reviewedBy/At) only, no User row (REQ-SEC-005) → return
Repository   : QR-SEC-011 · join NONE · transaction READ_WRITE
Security     : screen SEC_USERS (the "Pending sign-ups" tab, SRS B3) · permission `PERM_SEC_USERS_UPDATE`
Localization : n/a
<!-- API:API-SEC-011:END -->

<!-- API:API-SEC-013:START traces=REQ-SEC-012,DBF-SEC-015,DBF-SEC-016,DBF-SEC-017,DBF-SEC-018,DBF-SEC-019 -->
### API-SEC-013 — create role
Endpoint     : POST /api/v1/sec/roles
Layers       : controller → `RoleController.create` ; service → `RoleService.create`
Request      : body `{code, nameAr, nameEn, descriptionAr?, descriptionEn?}` — excludes {rolePk, isActiveFl, audit}
Response     : 201 · `RoleResponse`
Validations  : uniqueness of code (QR-SEC-034)
Errors       : `SEC-409-ROLE-DUP` (409)
Orchestration: validate uniqueness → persist (QR-SEC-013) → return
Repository   : QR-SEC-013, QR-SEC-034 · join NONE · transaction READ_WRITE
Security     : screen SEC_ROLES · permission `PERM_SEC_ROLES_CREATE`
Localization : nameAr/nameEn required; descriptionAr/En optional but both-or-neither
<!-- API:API-SEC-013:END -->

<!-- API:API-SEC-014:START traces=REQ-SEC-012,DBF-SEC-061,DBF-SEC-062,DBF-SEC-063,DBF-SEC-064 -->
### API-SEC-014 — grant module to role
Endpoint     : POST /api/v1/sec/roles/{id}/modules
Layers       : controller → `RoleGrantController.grantModule` ; service → `RoleGrantService.grantModule`
Request      : body `{moduleId}`
Response     : 201 · `RoleModuleGrantResponse`
Validations  : role and module must be active; grant must not already exist (UQ_SEC_ROLE_MODULE_GRANT_ROLE_MODULE)
Errors       : `SEC-409-GRANT-DUP` (409), `SEC-404-ROLE`/`SEC-404-MODULE` (404)
Orchestration: validate → persist (QR-SEC-014) → append AuditLogEntry `MODULE_GRANTED` → return
Repository   : QR-SEC-014 · join NONE · transaction READ_WRITE
Security     : screen SEC_ROLES · permission `PERM_SEC_ROLES_UPDATE`
Localization : n/a
<!-- API:API-SEC-014:END -->

<!-- API:API-SEC-015:START traces=REQ-SEC-015,DBF-SEC-061,DBF-SEC-062,DBF-SEC-066,DBF-SEC-071 -->
### API-SEC-015 — revoke module grant
Endpoint     : DELETE /api/v1/sec/roles/{id}/modules/{moduleId}
Layers       : controller → `RoleGrantController.revokeModule` ; service → `RoleGrantService.revokeModule`
Request      : path `id` (role), `moduleId`
Response     : 200 · confirmation `{revokedScreenGrants: n, revokedActionGrants: m}`
Validations  : RULE-SEC-003 (full text: DATA-DOM §ENT-SEC-007) — cascade is mandatory, not optional
Errors       : `SEC-404-GRANT` (404, grant does not exist)
Orchestration: find dependent screen/action grants for this role under this module (QR-SEC-032) → delete them, then the module grant itself (QR-SEC-015) → append AuditLogEntry `MODULE_REVOKED` (+ `SCREEN_REVOKED`/`ACTION_REVOKED` per cascaded row) → return
Repository   : QR-SEC-015, QR-SEC-032 · join NONE (sequential deletes, same transaction) · transaction READ_WRITE
Security     : screen SEC_ROLES · permission `PERM_SEC_ROLES_UPDATE`
Localization : n/a
<!-- API:API-SEC-015:END -->

<!-- API:API-SEC-016:START traces=REQ-SEC-013,DBF-SEC-066,DBF-SEC-067,DBF-SEC-068,DBF-SEC-069 -->
### API-SEC-016 — grant screen to role
Endpoint     : POST /api/v1/sec/roles/{id}/screens
Layers       : controller → `RoleGrantController.grantScreen` ; service → `RoleGrantService.grantScreen`
Request      : body `{screenId}`
Response     : 201 · `RoleScreenGrantResponse`
Validations  : RULE-SEC-001 (full text: DATA-DOM §ENT-SEC-008) — role must already hold the screen's module grant (QR-SEC-028) → violation `SEC-409-NO-MODULE-GRANT`
Errors       : `SEC-409-NO-MODULE-GRANT` (409), `SEC-409-GRANT-DUP` (409), `SEC-404-ROLE`/`SEC-404-SCREEN` (404)
Orchestration: resolve screen's module → check RULE-SEC-001 (QR-SEC-028) → persist (QR-SEC-016) → append AuditLogEntry `SCREEN_GRANTED` → return
Repository   : QR-SEC-016, QR-SEC-028 · join NONE · transaction READ_WRITE
Security     : screen SEC_ROLES · permission `PERM_SEC_ROLES_UPDATE`
Localization : n/a
<!-- API:API-SEC-016:END -->

<!-- API:API-SEC-017:START traces=REQ-SEC-014,REQ-SEC-020,REQ-SEC-030,DBF-SEC-071,DBF-SEC-072,DBF-SEC-073,DBF-SEC-074 -->
### API-SEC-017 — grant action to role
Endpoint     : POST /api/v1/sec/roles/{id}/actions
Layers       : controller → `RoleGrantController.grantAction` ; service → `RoleGrantService.grantAction`
Request      : body `{actionId}`
Response     : 201 · `RoleActionGrantResponse`
Validations  : RULE-SEC-002 (full text: DATA-DOM §ENT-SEC-009) — role must hold the action's screen grant (QR-SEC-029); RULE-SEC-007 (full text: DATA-DOM §ENT-SEC-009) — unless the action itself is VIEW, role must also hold VIEW on that screen (QR-SEC-030); RULE-SEC-005 (full text: DATA-DOM §ENT-SEC-009) — the grant must not give the underlying user a conflicting-pair action (QR-SEC-031)
Errors       : `SEC-409-NO-SCREEN-GRANT` (409), `SEC-409-NO-VIEW-GRANT` (409), `SEC-409-SOD-CONFLICT` (409), `SEC-409-GRANT-DUP` (409), `SEC-404-ROLE`/`SEC-404-ACTION` (404)
Orchestration: resolve action's screen → check RULE-SEC-002 (QR-SEC-029) → check RULE-SEC-007 unless actionCode=VIEW (QR-SEC-030) → check RULE-SEC-005 across every user holding this role (QR-SEC-031) → persist (QR-SEC-017) → append AuditLogEntry `ACTION_GRANTED` → return
Repository   : QR-SEC-017, QR-SEC-029, QR-SEC-030, QR-SEC-031 · join NONE · transaction READ_WRITE
Security     : screen SEC_ROLES · permission `PERM_SEC_ROLES_UPDATE`
Localization : n/a
<!-- API:API-SEC-017:END -->

<!-- API:API-SEC-026:START traces=REQ-SEC-028,DBF-SEC-081,DBF-SEC-082 -->
### API-SEC-026 — terminate session
Endpoint     : DELETE /api/v1/sec/sessions/{id}
Layers       : controller → `SessionController.terminate` ; service → `SessionService.terminate`
Request      : path `id`
Response     : 200 · confirmation `{activeSessionPk, terminatedAt}`
Validations  : session must currently be active (`terminatedAt IS NULL`)
Errors       : `SEC-404-SESSION` (404), `SEC-409-ALREADY-TERMINATED` (409)
Orchestration: load session → verify active → set terminatedAt/terminatedBy (QR-SEC-026) → append AuditLogEntry `SESSION_TERMINATED` → the associated tokenRef is invalidated at the auth-filter cache layer (REQ-SEC-028: "no longer accepted for any subsequent request") → return
Repository   : QR-SEC-026 · join NONE · transaction READ_WRITE
Security     : screen SEC_SESSIONS · permission `PERM_SEC_SESSIONS_DELETE`
Localization : n/a
<!-- API:API-SEC-026:END -->
<!-- SUB:SVC-API-CRUD:END -->

<!-- SUB:SVC-API-INT:START traces=REQ-SEC-001,REQ-SEC-002,REQ-SEC-003,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,REQ-SEC-026,REQ-SEC-029 -->
### SUB — SVC-API-INT (auth flows, onboarding registration, export)

<!-- API:API-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,DBF-SEC-002,DBF-SEC-004,DBF-SEC-007,DBF-SEC-075,DBF-SEC-076,DBF-SEC-077,DBF-SEC-078 -->
### API-SEC-001 — login
Endpoint     : POST /api/v1/sec/auth/login   (pre-authentication)
Layers       : controller → `AuthController.login` ; service → `AuthService.login`
Request      : body `{username, password}`
Response     : 200 (success) · `{accessToken, tokenType, expiresIn}` · `ApiResponse<LoginResponse>` — 401 on failure, same envelope shape, `success:false`
Validations  : credentials must match an ACTIVE user (QR-SEC-001 + password verify)
Errors       : `SEC-401-INVALID-CREDENTIALS` (401)
Orchestration: load user by username (QR-SEC-001) → verify active + password → on success: create ActiveSession (QR-SEC-006-style SAVE on ENT-SEC-010), update `lastLoginAt`, append AuditLogEntry `LOGIN_SUCCESS`, issue token → on failure: append AuditLogEntry `LOGIN_FAILED` (actorUserId null if username unknown), return 401 (REQ-SEC-002)
Repository   : QR-SEC-001 · join NONE · transaction READ_WRITE (session + audit write even on the read-mostly path)
Security     : screen SEC_LOGIN · public — no permission required
Localization : `SEC-401-INVALID-CREDENTIALS` message ar: "بيانات الدخول غير صحيحة" / en: "Invalid credentials" (POL-SEC-004)
<!-- API:API-SEC-001:END -->

<!-- API:API-SEC-002:START traces=REQ-SEC-003,DBF-SEC-098,DBF-SEC-099,DBF-SEC-100,DBF-SEC-101,DBF-SEC-102 -->
### API-SEC-002 — submit sign-up
Endpoint     : POST /api/v1/sec/auth/signup   (pre-authentication)
Layers       : controller → `AuthController.signup` ; service → `SignupRequestService.submit`
Request      : body `{email, fullNameAr, fullNameEn}`
Response     : 201 · `SignupRequestResponse` (statusCode=PENDING)
Validations  : email not already a User.email and not an already-PENDING SignupRequest.email
Errors       : `SEC-409-SIGNUP-DUP` (409)
Orchestration: validate → persist (QR-SEC-002, statusCode=PENDING) → return
Repository   : QR-SEC-002 · join NONE · transaction READ_WRITE
Security     : screen SEC_SIGNUP · public — no permission required
Localization : fullNameAr/fullNameEn both required
<!-- API:API-SEC-002:END -->

<!-- API:API-SEC-003:START traces=REQ-SEC-006,REQ-SEC-029,DBF-SEC-092,DBF-SEC-093,DBF-SEC-094,DBF-SEC-095 -->
### API-SEC-003 — request password reset
Endpoint     : POST /api/v1/sec/auth/password-reset/request   (pre-authentication)
Layers       : controller → `AuthController.requestReset` ; service → `PasswordResetService.request`
Request      : body `{email}`
Response     : 200 · generic confirmation `{message}` — always the same shape whether or not the email exists (never reveals which)
Validations  : none exposed to the caller (existence check is internal only, never surfaced)
Errors       : none beyond platform-standard
Orchestration: look up user by email (internal) → if found: create PasswordResetToken (QR-SEC-003, expiresAt=now+30min) → append AuditLogEntry `PASSWORD_RESET_REQUESTED` → **Where** the Notifications integration is enabled (REQ-SEC-029, optional pattern): dispatch a `dispatch()` call per `new project/integration-notifications-fileservice.md` §1.2 with `templateCode` identifying the reset message, `recipientId=userPk`, `moduleCode="SEC"` → if not found: do nothing further (still returns the same generic 200) → return
Repository   : QR-SEC-003 · join NONE · transaction READ_WRITE
Security     : screen SEC_PWD_RESET · public — no permission required
Localization : generic confirmation message in ar + en
<!-- API:API-SEC-003:END -->

<!-- API:API-SEC-004:START traces=REQ-SEC-007,REQ-SEC-008,DBF-SEC-093,DBF-SEC-095,DBF-SEC-096,DBF-SEC-004 -->
### API-SEC-004 — complete password reset
Endpoint     : POST /api/v1/sec/auth/password-reset/complete   (pre-authentication)
Layers       : controller → `AuthController.completeReset` ; service → `PasswordResetService.complete`
Request      : body `{token, newPassword}`
Response     : 200 · confirmation `{message}`
Validations  : RULE-SEC-006 (full text: DATA-DOM §ENT-SEC-012) — token must be unexpired and unused (QR-SEC-038)
Errors       : `SEC-409-RESET-TOKEN-INVALID` (409)
Orchestration: validate token (QR-SEC-038) → hash newPassword → update user's passwordHash + mark token usedAt (QR-SEC-004) → append AuditLogEntry `PASSWORD_RESET_COMPLETED` → return
Repository   : QR-SEC-004, QR-SEC-038 · join NONE · transaction READ_WRITE
Security     : screen SEC_PWD_RESET · public — no permission required
Localization : `SEC-409-RESET-TOKEN-INVALID` message ar: "رابط إعادة التعيين غير صالح أو منتهي" / en: "This reset link is invalid or has expired"
<!-- API:API-SEC-004:END -->

<!-- API:API-SEC-018:START traces=REQ-SEC-016,DBF-SEC-031,DBF-SEC-032,DBF-SEC-033 -->
### API-SEC-018 — register module
Endpoint     : POST /api/v1/sec/registry/modules
Layers       : controller → `RegistryController.registerModule` ; service → `RegistryService.registerModule`
Request      : body `{code, nameAr, nameEn}`
Response     : 201 · `ModuleRegistryResponse`
Validations  : uniqueness of code (QR-SEC-035)
Errors       : `SEC-409-MODULE-DUP` (409)
Orchestration: validate → persist (QR-SEC-018) → return
Repository   : QR-SEC-018, QR-SEC-035 · join NONE · transaction READ_WRITE
Security     : screen SEC_MODULE_REGISTRY · permission `PERM_SEC_MODULE_REGISTRY_UPDATE` — called by a registering module's own onboarding process, itself acting through an administrator-held credential; SEC mints no special "system" principal
Localization : nameAr/nameEn both required
<!-- API:API-SEC-018:END -->

<!-- API:API-SEC-019:START traces=REQ-SEC-017,REQ-SEC-018,DBF-SEC-040,DBF-SEC-041,DBF-SEC-042,DBF-SEC-043 -->
### API-SEC-019 — register screen
Endpoint     : POST /api/v1/sec/registry/screens
Layers       : controller → `RegistryController.registerScreen` ; service → `RegistryService.registerScreen`
Request      : body `{moduleCode, pageCode, nameAr, nameEn}`
Response     : 201 · `ScreenRegistryResponse`
Validations  : RULE-SEC-004 (full text: DATA-DOM §ENT-SEC-005) — module must already be registered (QR-SEC-036); uniqueness of pageCode (QR-SEC-036)
Errors       : `SEC-409-MODULE-NOT-REGISTERED` (409), `SEC-409-SCREEN-DUP` (409)
Orchestration: check RULE-SEC-004 + uniqueness (QR-SEC-036) → persist (QR-SEC-019) → return
Repository   : QR-SEC-019, QR-SEC-036 · join NONE · transaction READ_WRITE
Security     : screen SEC_MODULE_REGISTRY · permission `PERM_SEC_MODULE_REGISTRY_UPDATE`
Localization : nameAr/nameEn both required
<!-- API:API-SEC-019:END -->

<!-- API:API-SEC-020:START traces=REQ-SEC-019,DBF-SEC-050,DBF-SEC-051,DBF-SEC-052,DBF-SEC-053,DBF-SEC-054 -->
### API-SEC-020 — register action
Endpoint     : POST /api/v1/sec/registry/actions
Layers       : controller → `RegistryController.registerAction` ; service → `RegistryService.registerAction`
Request      : body `{pageCode, actionCode, nameAr, nameEn}`
Response     : 201 · `ActionRegistryResponse` (includes server-derived `permissionCode`)
Validations  : screen must already be registered; uniqueness of the derived permissionCode (QR-SEC-037)
Errors       : `SEC-409-SCREEN-NOT-REGISTERED` (409), `SEC-409-ACTION-DUP` (409)
Orchestration: resolve screen by pageCode → derive `permissionCode = PERM_<pageCode>_<actionCode>` → validate uniqueness (QR-SEC-037) → persist (QR-SEC-020) → return
Repository   : QR-SEC-020, QR-SEC-037 · join NONE · transaction READ_WRITE
Security     : screen SEC_MODULE_REGISTRY · permission `PERM_SEC_MODULE_REGISTRY_UPDATE`
Localization : nameAr/nameEn both required
<!-- API:API-SEC-020:END -->

<!-- API:API-SEC-024:START traces=REQ-SEC-026,DBF-SEC-084,DBF-SEC-085,DBF-SEC-086,DBF-SEC-087,DBF-SEC-088,DBF-SEC-089 -->
### API-SEC-024 — export audit log
Endpoint     : GET /api/v1/sec/audit-log/export
Layers       : controller → `AuditLogController.export` ; service → `AuditLogService.export`
Request      : query params — same filter set as API-SEC-023 (eventTypeCode, actorUserId, occurredFrom/occurredTo), no paging (exports the full filtered set)
Response     : 200 · `Content-Type: text/csv` body, one row per matching AuditLogEntry, all fields
Validations  : none
Errors       : SEC-500 only
Orchestration: load the full filtered set (QR-SEC-024, same filters as QR-SEC-023, unpaged) → serialize to CSV → return (REQ-SEC-026: "exactly the filtered entries' fields")
Repository   : QR-SEC-024 · join NONE · transaction READ_ONLY
Security     : screen SEC_AUDIT_LOG · permission `PERM_SEC_AUDIT_LOG_VIEW` (shares VIEW — export is not a separate mutation, SRS Access summary)
Localization : detailsAr/detailsEn both included as separate CSV columns
<!-- API:API-SEC-024:END -->
<!-- SUB:SVC-API-INT:END -->
<!-- PHASE:SVC-API:END -->

<!-- PHASE:DOC:START traces=REQ-SEC-016 -->
## PHASE 4 — DOC

**API contract summary** (R4 — backend self-check only; the frontend stage binds to the
real `api-docs-sec.md` published after implementation, never to this table):

| API | Path | Verb | Request DTO | Response DTO | Stability |
|---|---|---|---|---|---|
| API-SEC-001 | /auth/login | POST | LoginRequest | LoginResponse | v1 |
| API-SEC-002 | /auth/signup | POST | SignupRequestDto | SignupRequestResponse | v1 |
| API-SEC-003 | /auth/password-reset/request | POST | ResetRequestDto | ConfirmationResponse | v1 |
| API-SEC-004 | /auth/password-reset/complete | POST | ResetCompleteDto | ConfirmationResponse | v1 |
| API-SEC-005 | /users | GET | (query params) | Page\<UserResponse\> | v1 |
| API-SEC-006 | /users | POST | UserCreateRequest | UserResponse | v1 |
| API-SEC-007 | /users/{id} | PUT | UserUpdateRequest | UserResponse | v1 |
| API-SEC-008 | /users/{id}/roles | PUT | RoleAssignmentRequest | UserResponse | v1 |
| API-SEC-009 | /users/{id} | DELETE | — | DeactivateConfirmation | v1 |
| API-SEC-010 | /users/{id} | PATCH | — | ReactivateConfirmation | v1 |
| API-SEC-011 | /signup-requests/{id} | PATCH | SignupDecisionRequest | UserResponse \| SignupRequestResponse | v1 |
| API-SEC-012 | /roles | GET | (query params) | Page\<RoleResponse\> | v1 |
| API-SEC-013 | /roles | POST | RoleCreateRequest | RoleResponse | v1 |
| API-SEC-014 | /roles/{id}/modules | POST | ModuleGrantRequest | RoleModuleGrantResponse | v1 |
| API-SEC-015 | /roles/{id}/modules/{moduleId} | DELETE | — | RevokeConfirmation | v1 |
| API-SEC-016 | /roles/{id}/screens | POST | ScreenGrantRequest | RoleScreenGrantResponse | v1 |
| API-SEC-017 | /roles/{id}/actions | POST | ActionGrantRequest | RoleActionGrantResponse | v1 |
| API-SEC-018 | /registry/modules | POST | ModuleRegisterRequest | ModuleRegistryResponse | v1 |
| API-SEC-019 | /registry/screens | POST | ScreenRegisterRequest | ScreenRegistryResponse | v1 |
| API-SEC-020 | /registry/actions | POST | ActionRegisterRequest | ActionRegistryResponse | v1 |
| API-SEC-021 | /registry | GET | (query params) | Page\<RegistryRowResponse\> | v1 |
| API-SEC-022 | /dashboard | GET | — | DashboardResponse | v1 |
| API-SEC-023 | /audit-log | GET | (query params) | Page\<AuditLogEntryResponse\> | v1 |
| API-SEC-024 | /audit-log/export | GET | (query params) | text/csv | v1 |
| API-SEC-025 | /sessions | GET | (query params) | Page\<ActiveSessionResponse\> | v1 |
| API-SEC-026 | /sessions/{id} | DELETE | — | TerminateConfirmation | v1 |
| API-SEC-027 | /menu | GET | — | List\<ModuleMenuResponse\> | v1 |
(paths relative to `/api/v1/sec`)

**DTO typing constraints**: `statusCode`/`eventTypeCode`/`actionCode` are `String` holding
the coded value, never a Java enum (profile lookup rule); business code fields — not
applicable, no SEC entity has one; PK fields never appear in a create-request body.

**Pagination + filter standard**: request shape `{page, size, sort}` + named filters per
screen (§Phase 1 CORE "Search contract"); an unrecognized `sort` field is rejected
(`SEC-400-INVALID-SORT`); an empty filtered result is `200` with empty `content`, never `404`.
<!-- PHASE:DOC:END -->

<!-- PHASE:INT-C:START traces=REQ-SEC-016 -->
## PHASE 5 — INT-C (cross-module consume)

No `XM-*` row exists for SEC (db-script-sec.md §2: "None — SEC is ROOT"). SEC consumes no
other module's entity, table or API. This phase is intentionally near-empty, stated so per
engine §6.2 rather than omitted; no SUB is opened (XM count 0 < the split threshold of 5).

SEC's actual cross-module role runs in the opposite direction: every future module
*consumes* SEC through the plain REST surface documented in Phase 3 (registration:
API-SEC-018/019/020; authorization: the CORE interceptor + API-SEC-027) — that is standard
API consumption by another module's own P3.1, not an `XM-*` row inside SEC's own plan.
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-SEC-016 -->
## PHASE 6 — INT-R (cross-module resolve)

No `XM-*` row to resolve — same basis as Phase 5. No SUB opened (0 < 5).

Inbound dependency stub (future consumers, not `TODO`): `XM-INBOUND-STUB-1` — any future
module (first expected: MDL, then FIN per GENERATION-INSTRUCTIONS.md §3) will register
itself via API-SEC-018/019/020 and consume identity/authorization via API-SEC-001/027 and
the CORE interceptor; the entity it reaches is `ENT-SEC-004` (ModuleRegistry) /
`ENT-SEC-005` (ScreenRegistry) / `ENT-SEC-006` (ActionRegistry); formal `XM-*` ids for that
direction are assigned by the *consuming* module's own P2, not by SEC.
<!-- PHASE:INT-R:END -->

<!-- PHASE:SEC-BE:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-020,REQ-SEC-023,REQ-SEC-030,REQ-SEC-033 -->
## PHASE 7 — SEC-BE (security, backend half)

One block per screen (R7); every API serving a screen verifies its permission via the CORE
interceptor (Phase 1) before its controller method body runs.

| Screen (page code) | VIEW | CREATE | UPDATE | DELETE |
|---|---|---|---|---|
| SEC_LOGIN | public | — | — | — |
| SEC_SIGNUP | public | — | — | — |
| SEC_PWD_RESET | public | — | — | — |
| SEC_USERS | PERM_SEC_USERS_VIEW (API-SEC-005) | PERM_SEC_USERS_CREATE (API-SEC-006) | PERM_SEC_USERS_UPDATE (API-SEC-007, 008, 009, 010, 011) | — |
| SEC_ROLES | PERM_SEC_ROLES_VIEW (API-SEC-012) | PERM_SEC_ROLES_CREATE (API-SEC-013) | PERM_SEC_ROLES_UPDATE (API-SEC-014..017) | PERM_SEC_ROLES_DELETE (reserved — no delete-role endpoint in v1, deactivate only, which is UPDATE) |
| SEC_MODULE_REGISTRY | PERM_SEC_MODULE_REGISTRY_VIEW (API-SEC-021) | (via registering module's own call, API-SEC-018/019/020) | PERM_SEC_MODULE_REGISTRY_UPDATE (deactivate — no v1 endpoint yet, reserved) | — |
| SEC_DASHBOARD | PERM_SEC_DASHBOARD_VIEW (API-SEC-022) + per-widget source VIEW | — | — | — |
| SEC_AUDIT_LOG | PERM_SEC_AUDIT_LOG_VIEW (API-SEC-023, 024) | — | — | — |
| SEC_SESSIONS | PERM_SEC_SESSIONS_VIEW (API-SEC-025) | — | — | PERM_SEC_SESSIONS_DELETE (API-SEC-026) |

**Seed data** (one SEC_PAGES row per composite screen, one action row per action per §7.1):
9 page rows (SEC_LOGIN, SEC_SIGNUP, SEC_PWD_RESET, SEC_USERS, SEC_ROLES,
SEC_MODULE_REGISTRY, SEC_DASHBOARD, SEC_AUDIT_LOG, SEC_SESSIONS) inserted via
API-SEC-019/registered by SEC's own bootstrap (SEC registers itself into itself — the one
module for which no external caller is needed); action rows: VIEW/CREATE/UPDATE/DELETE per
secured screen above, per PERM_<PAGE_CODE>_<ACTION> (profile.conventions.security_model).
Column names come from the db-script (SEC_SCREEN_REG, SEC_ACTION_REG), not restated here.

**Gateway**: every non-VIEW permission requires VIEW on the same screen first
(RULE-SEC-007, enforced by the CORE interceptor + at grant time by API-SEC-017/QR-SEC-030).

**Forbidden responses**: any denial from the CORE interceptor maps to
`LocalizedException{code: "SEC-403-FORBIDDEN", messageAr: "غير مصرح بهذا الإجراء",
messageEn: "You are not authorized to perform this action"}` (§Error Catalog `SEC-403`).
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-SEC-033 -->
## PHASE 8 — ALIGN-BE

See §Alignment self-check (ALIGN) below — its RESULT row is this phase's content, per
engine §6.1 R8 ("written as the phase content of the alignment-role phase").
<!-- PHASE:ALIGN-BE:END -->

## Error Catalog — SEC v1

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `SEC-<3-digit>` (Phase 1 CORE).

| code | RULE / PLATFORM-STD | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| SEC-401-INVALID-CREDENTIALS | PLATFORM-STD (ADR-SEC-002, new — see below) | API-SEC-001 | 401 | wrong/unknown credentials | بيانات الدخول غير صحيحة | Invalid credentials |
| SEC-409-USER-DUP | PLATFORM-STD (uniqueness) | API-SEC-006, 007 | 409 | duplicate username/email | اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل | Username or email already in use |
| SEC-404-USER | PLATFORM-STD (not found) | API-SEC-007, 008, 009, 010 | 404 | unknown user id | المستخدم غير موجود | User not found |
| SEC-409-SOD-CONFLICT | RULE-SEC-005 | API-SEC-008, 017 | 409 | conflicting action pair on one user | هذا المستخدم يملك إجراءً متعارضًا بالفعل | This user already holds a conflicting action |
| SEC-404-ROLE | PLATFORM-STD (not found) | API-SEC-008, 014, 016, 017 | 404 | unknown role id | الدور غير موجود | Role not found |
| SEC-409-INVALID-TRANSITION | PLATFORM-STD (lifecycle) | API-SEC-010, 011 | 409 | transition not allowed from current status | لا يمكن تنفيذ هذا الانتقال من الحالة الحالية | This transition is not allowed from the current status |
| SEC-404-SIGNUP | PLATFORM-STD (not found) | API-SEC-011 | 404 | unknown signup request id | طلب التسجيل غير موجود | Signup request not found |
| SEC-409-ROLE-DUP | PLATFORM-STD (uniqueness) | API-SEC-013 | 409 | duplicate role code | رمز الدور مستخدم بالفعل | Role code already in use |
| SEC-409-GRANT-DUP | PLATFORM-STD (uniqueness) | API-SEC-014, 016, 017 | 409 | grant already exists | هذا المنح موجود بالفعل | This grant already exists |
| SEC-404-MODULE | PLATFORM-STD (not found) | API-SEC-014, 015 | 404 | unknown module id | الوحدة غير موجودة | Module not found |
| SEC-404-GRANT | PLATFORM-STD (not found) | API-SEC-015 | 404 | grant does not exist | المنح غير موجود | Grant not found |
| SEC-409-NO-MODULE-GRANT | RULE-SEC-001 | API-SEC-016 | 409 | screen grant attempted without module grant | لا يمكن منح شاشة دون منح الوحدة أولًا | Cannot grant a screen without first granting its module |
| SEC-404-SCREEN | PLATFORM-STD (not found) | API-SEC-016, 017, 019 | 404 | unknown screen id / page code | الشاشة غير موجودة | Screen not found |
| SEC-409-NO-SCREEN-GRANT | RULE-SEC-002 | API-SEC-017 | 409 | action grant attempted without screen grant | لا يمكن منح إجراء دون منح الشاشة أولًا | Cannot grant an action without first granting its screen |
| SEC-409-NO-VIEW-GRANT | RULE-SEC-007 | API-SEC-017 | 409 | non-VIEW action grant attempted without VIEW | يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة | The VIEW action must be granted on this screen first |
| SEC-404-ACTION | PLATFORM-STD (not found) | API-SEC-017 | 404 | unknown action id | الإجراء غير موجود | Action not found |
| SEC-409-MODULE-DUP | PLATFORM-STD (uniqueness) | API-SEC-018 | 409 | duplicate module code | رمز الوحدة مستخدم بالفعل | Module code already in use |
| SEC-409-MODULE-NOT-REGISTERED | RULE-SEC-004 | API-SEC-019 | 409 | screen registered under an unregistered module | الوحدة غير مسجّلة | Module is not registered |
| SEC-409-SCREEN-DUP | PLATFORM-STD (uniqueness) | API-SEC-019 | 409 | duplicate page code | رمز الصفحة مستخدم بالفعل | Page code already in use |
| SEC-409-SCREEN-NOT-REGISTERED | PLATFORM-STD (referential) | API-SEC-020 | 409 | action registered under an unregistered screen | الشاشة غير مسجّلة | Screen is not registered |
| SEC-409-ACTION-DUP | PLATFORM-STD (uniqueness) | API-SEC-020 | 409 | duplicate permission code | رمز الصلاحية مستخدم بالفعل | Permission code already in use |
| SEC-409-RESET-TOKEN-INVALID | RULE-SEC-006 | API-SEC-004 | 409 | expired or used reset token | رابط إعادة التعيين غير صالح أو منتهي | This reset link is invalid or has expired |
| SEC-409-SIGNUP-DUP | PLATFORM-STD (uniqueness) | API-SEC-002 | 409 | duplicate pending/registered email | البريد الإلكتروني مستخدم بالفعل | This email is already in use |
| SEC-404-SESSION | PLATFORM-STD (not found) | API-SEC-026 | 404 | unknown session id | الجلسة غير موجودة | Session not found |
| SEC-409-ALREADY-TERMINATED | PLATFORM-STD (lifecycle) | API-SEC-026 | 409 | session already terminated | هذه الجلسة منتهية بالفعل | This session is already terminated |
| SEC-403-FORBIDDEN | PLATFORM-STD (RULE-SEC-007 + REQ-SEC-033, CORE interceptor) | every secured API | 403 | missing module/screen/action grant | غير مصرح بهذا الإجراء | You are not authorized to perform this action |
| SEC-400-INVALID-SORT | PLATFORM-STD (search contract) | every search API | 400 | unrecognized `sort` field | حقل الترتيب غير معروف | Unrecognized sort field |
| SEC-500 | PLATFORM-STD (infrastructure) | any | 500 | unhandled server error | حدث خطأ في الخادم | A server error occurred |

`SEC-401-INVALID-CREDENTIALS` and every other PLATFORM-STD row is a standard infrastructure
error (not-found / conflict / server / forbidden), not sourced from a specific SRS RULE — per
engine §7 these carry `RULE = PLATFORM-STD` and are covered by a single umbrella note rather
than 20 near-identical ADRs: **ADR-SEC-002** (below) records this once for the whole catalog.

## ADR-SEC-002 (new this stage)
See `erp/decisions/SEC/ADR-SEC-002.md` — PLATFORM-STD error rows (not-found, duplicate,
invalid-transition, forbidden, server, invalid-sort) are standard REST/CRUD infrastructure
errors implied by the SRS's own conventions (unique constraints, status lifecycles, the
module/screen/action gate) rather than restated as individual RULE-* ids; non-breaking.

## Alignment self-check (ALIGN) — SEC v1

```
TRACEABILITY      ✓ every API-*/QR-*/RULE-*/DBF-* used in a phase appears in the Plan Index; every PHASE/SUB/atom carries traces=; every traces target exists upstream (REQ-SEC-001..033, DBF-SEC-001..104 all defined in srs/db-script)
BINDING (§2A)     ✓ no placeholder table/column/key/generation object; every column cites a DBF (Field Registry + per-entity FIELDS tables); every RULE message present in ar+en; business code: none applicable (stated, not silently skipped)
MANIFEST (§4)     ✓ only the 4 mandated columns beyond DBF/ENT (property, type — status/XM added per engine format); all 104 DBF of every bound table listed; 0 ⏸ rows (0 XM)
QRC (§5)          ✓ every API with a DB operation has ≥1 QR (API-SEC-001..027 all cite one); every QR entry carries the "logical spec, not code" framing (catalog header); no join for a lookup label; exact generation object named (`GENERATED ALWAYS AS IDENTITY`, Phase 1 CORE type table)
API (R3)          ✓ every RULE in a Validations line has a catalog row; platform errors carry RULE=PLATFORM-STD + ADR-SEC-002; create/update requests exclude PK/audit/system fields (DTO MEMBERSHIP, Phase 2; Request lines, Phase 3); business code: not applicable (none exists)
CROSS-MODULE      ✓ 0 XM from db-script, 0 placed, 0 mismatched; inbound stub uses XM-INBOUND-STUB-1 notation, not TODO
SECURITY (R7)     ✓ every secured API declares its PERM_* (Phase 3 Security lines, cross-checked against Phase 7 table); every secured screen has a Phase 7 seed row; no permission outside SRS §7.1/Access summary — profile.review.extra_checks ERP-4 (every mutation endpoint declares its PERM_*): checked — every POST/PUT/PATCH/DELETE API above states one
CORE (R1)         ✓ layers declared, domain placement declared (entity methods for single-entity, service for multi-row), error signalling declared (code format `SEC-<3-digit>`), type mapping declared (postgresql16 → Java table)
DECISIONS         ✓ ADR-SEC-001 (carried from P2, lookup centralization deferral) and ADR-SEC-002 (this stage, PLATFORM-STD catalog umbrella) both ACCEPTED, non-breaking; no BLOCKED ADR
RESULT            PASSED ✓ — 0 findings
```

**Coverage — ENT/DBF → phases → QR → XM**: every ENT-SEC-001..013 appears in exactly one
DATA-DOM entity block (SUB-MASTER or SUB-TRANSACTIONAL) with ≥1 QR cited under REPOSITORY
OPS; every DBF-SEC-001..104 appears in the DB Alignment Manifest and its owning entity's
FIELDS table; 0 XM (n/a).

**Coverage — RULE → API → catalog code**: RULE-SEC-001→API-SEC-016→SEC-409-NO-MODULE-GRANT ·
RULE-SEC-002→API-SEC-017→SEC-409-NO-SCREEN-GRANT · RULE-SEC-003→API-SEC-015→(no dedicated
code — success path with a count in the response; failure paths are SEC-404-GRANT) ·
RULE-SEC-004→API-SEC-019→SEC-409-MODULE-NOT-REGISTERED ·
RULE-SEC-005→API-SEC-008,017→SEC-409-SOD-CONFLICT · RULE-SEC-006→API-SEC-004→
SEC-409-RESET-TOKEN-INVALID · RULE-SEC-007→API-SEC-017→SEC-409-NO-VIEW-GRANT (+ the
CORE interceptor at runtime → SEC-403-FORBIDDEN).

**Coverage — XM → status → blocks → workaround**: not applicable (0 XM).

## QR id definitions (cross-reference index — full detail in Query Reference Catalog above)
**QR-SEC-001** — FIND_ONE user by username [ENT-SEC-001, API-SEC-001]
**QR-SEC-002** — SAVE signup request [ENT-SEC-013, API-SEC-002]
**QR-SEC-003** — SAVE password reset token [ENT-SEC-012, API-SEC-003]
**QR-SEC-004** — UPDATE user password + mark token used [ENT-SEC-001, ENT-SEC-012, API-SEC-004]
**QR-SEC-005** — FIND_BY_CRITERIA search users [ENT-SEC-001, API-SEC-005]
**QR-SEC-006** — SAVE create user [ENT-SEC-001, API-SEC-006]
**QR-SEC-007** — UPDATE user profile fields [ENT-SEC-001, API-SEC-007]
**QR-SEC-008** — SAVE assign roles to user [ENT-SEC-003, API-SEC-008]
**QR-SEC-009** — UPDATE deactivate user + terminate sessions [ENT-SEC-001, ENT-SEC-010, API-SEC-009]
**QR-SEC-010** — UPDATE reactivate user [ENT-SEC-001, API-SEC-010]
**QR-SEC-011** — UPDATE approve/reject signup [ENT-SEC-013, ENT-SEC-001, API-SEC-011]
**QR-SEC-012** — FIND_BY_CRITERIA search roles [ENT-SEC-002, API-SEC-012]
**QR-SEC-013** — SAVE create role [ENT-SEC-002, API-SEC-013]
**QR-SEC-014** — SAVE grant module [ENT-SEC-007, API-SEC-014]
**QR-SEC-015** — DELETE revoke module grant [ENT-SEC-007, API-SEC-015]
**QR-SEC-016** — SAVE grant screen [ENT-SEC-008, API-SEC-016]
**QR-SEC-017** — SAVE grant action [ENT-SEC-009, API-SEC-017]
**QR-SEC-018** — SAVE register module [ENT-SEC-004, API-SEC-018]
**QR-SEC-019** — SAVE register screen [ENT-SEC-005, API-SEC-019]
**QR-SEC-020** — SAVE register action [ENT-SEC-006, API-SEC-020]
**QR-SEC-021** — FIND_BY_CRITERIA browse registry tree [ENT-SEC-004, ENT-SEC-005, ENT-SEC-006, API-SEC-021]
**QR-SEC-022** — AGGREGATE dashboard figures [ENT-SEC-001, ENT-SEC-010, ENT-SEC-011, ENT-SEC-002, API-SEC-022]
**QR-SEC-023** — FIND_BY_CRITERIA search audit log [ENT-SEC-011, API-SEC-023]
**QR-SEC-024** — FIND_BY_CRITERIA audit log export [ENT-SEC-011, API-SEC-024]
**QR-SEC-025** — FIND_BY_CRITERIA non-terminated sessions [ENT-SEC-010, API-SEC-025]
**QR-SEC-026** — UPDATE terminate session [ENT-SEC-010, API-SEC-026]
**QR-SEC-027** — FIND_BY_CRITERIA effective menu tree [ENT-SEC-004, ENT-SEC-005, ENT-SEC-007, ENT-SEC-008, API-SEC-027]
**QR-SEC-028** — EXISTS role holds module grant (RULE-SEC-001) [ENT-SEC-007, API-SEC-016]
**QR-SEC-029** — EXISTS role holds screen grant (RULE-SEC-002) [ENT-SEC-008, API-SEC-017]
**QR-SEC-030** — EXISTS role holds VIEW on screen (RULE-SEC-007) [ENT-SEC-009, API-SEC-017]
**QR-SEC-031** — EXISTS conflicting action already held (RULE-SEC-005) [ENT-SEC-009, API-SEC-008, API-SEC-017]
**QR-SEC-032** — FIND_ALL dependent screen/action grants for cascade (RULE-SEC-003) [ENT-SEC-008, ENT-SEC-009, API-SEC-015]
**QR-SEC-033** — EXISTS uniqueness username/email [ENT-SEC-001, API-SEC-006]
**QR-SEC-034** — EXISTS uniqueness role code [ENT-SEC-002, API-SEC-013]
**QR-SEC-035** — EXISTS uniqueness module code [ENT-SEC-004, API-SEC-018]
**QR-SEC-036** — EXISTS module registered + uniqueness page code (RULE-SEC-004) [ENT-SEC-004, ENT-SEC-005, API-SEC-019]
**QR-SEC-037** — EXISTS screen exists + uniqueness permission code [ENT-SEC-005, ENT-SEC-006, API-SEC-020]
**QR-SEC-038** — EXISTS reset token unexpired and unused (RULE-SEC-006) [ENT-SEC-012, API-SEC-004]

## Registry content
See `registry-exec-be-sec.md`.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-srs (SEC)>>>
## REGISTRY — P1 — SEC v1
══════════════════════════════════════════════════════════════════

Entities
| ENT id | Name (ar/en) | Kind | PRIVATE/SHARED | Status |
|---|---|---|---|---|
| ENT-SEC-001 | المستخدم / User | security | SHARED (owner) | REGISTERED |
| ENT-SEC-002 | الدور / Role | security | PRIVATE | REGISTERED |
| ENT-SEC-003 | ربط المستخدم بالدور / UserRoleAssignment | security | PRIVATE | REGISTERED |
| ENT-SEC-004 | سجل الوحدات / ModuleRegistry | security | SHARED (owner) | REGISTERED |
| ENT-SEC-005 | سجل الشاشات / ScreenRegistry | security | SHARED (owner) | REGISTERED |
| ENT-SEC-006 | سجل الإجراءات / ActionRegistry | security | SHARED (owner) | REGISTERED |
| ENT-SEC-007 | منح الوحدة للدور / RoleModuleGrant | security | PRIVATE | REGISTERED |
| ENT-SEC-008 | منح الشاشة للدور / RoleScreenGrant | security | PRIVATE | REGISTERED |
| ENT-SEC-009 | منح الإجراء للدور / RoleActionGrant | security | PRIVATE | REGISTERED |
| ENT-SEC-010 | الجلسة النشطة / ActiveSession | security | PRIVATE | REGISTERED |
| ENT-SEC-011 | سجل التدقيق / AuditLogEntry | security | PRIVATE | REGISTERED |
| ENT-SEC-012 | رمز إعادة تعيين كلمة المرور / PasswordResetToken | security | PRIVATE | REGISTERED |
| ENT-SEC-013 | طلب تسجيل معلّق / SignupRequest | security | PRIVATE | REGISTERED |

Consumed
none — SEC is ROOT (→ dependency index: no row this module).

Lookups owned
| Key | ENT | Values count |
|---|---|---|
| USER_STATUS | ENT-SEC-001 | 3 |
| SIGNUP_STATUS | ENT-SEC-013 | 3 |
| AUDIT_EVENT_TYPE | ENT-SEC-011 | 14 |

Lookups consumed
none.

Screens
| SCR-REQ id | Name (ar/en) | Page code |
|---|---|---|
| SCR-REQ-SEC-001 | تسجيل الدخول / Login | SEC_LOGIN |
| SCR-REQ-SEC-002 | التسجيل الذاتي / Sign-up | SEC_SIGNUP |
| SCR-REQ-SEC-003 | نسيت/إعادة تعيين كلمة المرور / Forgot/reset password | SEC_PWD_RESET |
| SCR-REQ-SEC-004 | المستخدمون / Users | SEC_USERS |
| SCR-REQ-SEC-005 | الأدوار والصلاحيات / Roles & permissions | SEC_ROLES |
| SCR-REQ-SEC-006 | سجل الوحدة/الشاشة/الإجراء / Module/screen/action registry | SEC_MODULE_REGISTRY |
| SCR-REQ-SEC-007 | لوحة تحكم الأمان / Admin dashboard | SEC_DASHBOARD |
| SCR-REQ-SEC-008 | سجل التدقيق / Audit log | SEC_AUDIT_LOG |
| SCR-REQ-SEC-009 | إدارة الجلسات النشطة / Active sessions management | SEC_SESSIONS |
| SCR-REQ-SEC-010 | القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu | (no page code — global component) |

Requirements
REQ count: 33 · AC count: 33 · RULE count: 7 · ENT count: 13 · SCR-REQ count: 10
Last sequence per atom: REQ: 033 · AC: 033 · ENT: 013 · RULE: 007 · SCR-REQ: 010

REQ ids (full text in srs-sec.md → A4): REQ-SEC-001, REQ-SEC-002, REQ-SEC-003,
REQ-SEC-004, REQ-SEC-005, REQ-SEC-006, REQ-SEC-007, REQ-SEC-008, REQ-SEC-009,
REQ-SEC-010, REQ-SEC-011, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015,
REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019, REQ-SEC-020, REQ-SEC-021,
REQ-SEC-022, REQ-SEC-023, REQ-SEC-024, REQ-SEC-025, REQ-SEC-026, REQ-SEC-027,
REQ-SEC-028, REQ-SEC-029, REQ-SEC-030, REQ-SEC-031, REQ-SEC-032, REQ-SEC-033

AC ids (full text in srs-sec.md → A4, one per REQ above): AC-SEC-001, AC-SEC-002,
AC-SEC-003, AC-SEC-004, AC-SEC-005, AC-SEC-006, AC-SEC-007, AC-SEC-008, AC-SEC-009,
AC-SEC-010, AC-SEC-011, AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-016,
AC-SEC-017, AC-SEC-018, AC-SEC-019, AC-SEC-020, AC-SEC-021, AC-SEC-022, AC-SEC-023,
AC-SEC-024, AC-SEC-025, AC-SEC-026, AC-SEC-027, AC-SEC-028, AC-SEC-029, AC-SEC-030,
AC-SEC-031, AC-SEC-032, AC-SEC-033

RULE ids (full text in srs-sec.md → A5): RULE-SEC-001, RULE-SEC-002, RULE-SEC-003,
RULE-SEC-004, RULE-SEC-005, RULE-SEC-006, RULE-SEC-007

Decisions
ADR ids: none (no ADR raised — §9 ambiguity fork was never reached this stage).

Event
"P1 completed: SEC v1 — 13 entities, 33 requirements, 33 acceptance criteria, 7 rules, 10 screen requirements, 0 ADRs"
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-db (SEC)>>>
## REGISTRY — P2 — SEC v1
══════════════════════════════════════════════════════════════════

Tables
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| SEC_USER | ENT-SEC-001 | security | DBF-SEC-001 … DBF-SEC-013 |
| SEC_ROLE | ENT-SEC-002 | security | DBF-SEC-014 … DBF-SEC-024 |
| SEC_USER_ROLE | ENT-SEC-003 | security | DBF-SEC-025 … DBF-SEC-029 |
| SEC_MODULE_REG | ENT-SEC-004 | security | DBF-SEC-030 … DBF-SEC-038 |
| SEC_SCREEN_REG | ENT-SEC-005 | security | DBF-SEC-039 … DBF-SEC-048 |
| SEC_ACTION_REG | ENT-SEC-006 | security | DBF-SEC-049 … DBF-SEC-059 |
| SEC_ROLE_MODULE_GRANT | ENT-SEC-007 | security | DBF-SEC-060 … DBF-SEC-064 |
| SEC_ROLE_SCREEN_GRANT | ENT-SEC-008 | security | DBF-SEC-065 … DBF-SEC-069 |
| SEC_ROLE_ACTION_GRANT | ENT-SEC-009 | security | DBF-SEC-070 … DBF-SEC-074 |
| SEC_ACTIVE_SESSION | ENT-SEC-010 | security | DBF-SEC-075 … DBF-SEC-082 |
| SEC_AUDIT_LOG | ENT-SEC-011 | security | DBF-SEC-083 … DBF-SEC-090 |
| SEC_PWD_RESET_TOKEN | ENT-SEC-012 | security | DBF-SEC-091 … DBF-SEC-096 |
| SEC_SIGNUP_REQUEST | ENT-SEC-013 | security | DBF-SEC-097 … DBF-SEC-104 |

DBF ids (full detail in db-script-sec.md → §1): DBF-SEC-001, DBF-SEC-002, DBF-SEC-003,
DBF-SEC-004, DBF-SEC-005, DBF-SEC-006, DBF-SEC-007, DBF-SEC-008, DBF-SEC-009, DBF-SEC-010,
DBF-SEC-011, DBF-SEC-012, DBF-SEC-013, DBF-SEC-014, DBF-SEC-015, DBF-SEC-016, DBF-SEC-017,
DBF-SEC-018, DBF-SEC-019, DBF-SEC-020, DBF-SEC-021, DBF-SEC-022, DBF-SEC-023, DBF-SEC-024,
DBF-SEC-025, DBF-SEC-026, DBF-SEC-027, DBF-SEC-028, DBF-SEC-029, DBF-SEC-030, DBF-SEC-031,
DBF-SEC-032, DBF-SEC-033, DBF-SEC-034, DBF-SEC-035, DBF-SEC-036, DBF-SEC-037, DBF-SEC-038,
DBF-SEC-039, DBF-SEC-040, DBF-SEC-041, DBF-SEC-042, DBF-SEC-043, DBF-SEC-044, DBF-SEC-045,
DBF-SEC-046, DBF-SEC-047, DBF-SEC-048, DBF-SEC-049, DBF-SEC-050, DBF-SEC-051, DBF-SEC-052,
DBF-SEC-053, DBF-SEC-054, DBF-SEC-055, DBF-SEC-056, DBF-SEC-057, DBF-SEC-058, DBF-SEC-059,
DBF-SEC-060, DBF-SEC-061, DBF-SEC-062, DBF-SEC-063, DBF-SEC-064, DBF-SEC-065, DBF-SEC-066,
DBF-SEC-067, DBF-SEC-068, DBF-SEC-069, DBF-SEC-070, DBF-SEC-071, DBF-SEC-072, DBF-SEC-073,
DBF-SEC-074, DBF-SEC-075, DBF-SEC-076, DBF-SEC-077, DBF-SEC-078, DBF-SEC-079, DBF-SEC-080,
DBF-SEC-081, DBF-SEC-082, DBF-SEC-083, DBF-SEC-084, DBF-SEC-085, DBF-SEC-086, DBF-SEC-087,
DBF-SEC-088, DBF-SEC-089, DBF-SEC-090, DBF-SEC-091, DBF-SEC-092, DBF-SEC-093, DBF-SEC-094,
DBF-SEC-095, DBF-SEC-096, DBF-SEC-097, DBF-SEC-098, DBF-SEC-099, DBF-SEC-100, DBF-SEC-101,
DBF-SEC-102, DBF-SEC-103, DBF-SEC-104

XM index
none — SEC is ROOT (→ dependency index: no row this module).

Lookups
| Key | Seeded values count | Owner |
|---|---|---|
| USER_STATUS | 3 (CHECK-constrained, not seeded rows — ADR-SEC-001) | SEC |
| SIGNUP_STATUS | 3 (CHECK-constrained, not seeded rows — ADR-SEC-001) | SEC |
| AUDIT_EVENT_TYPE | 14 (CHECK-constrained, not seeded rows — ADR-SEC-001) | SEC |

Sequences
Last DBF: DBF-SEC-104 · Last XM: none assigned (0 rows)

Decisions
ADR-SEC-001 (ACCEPTED, non-breaking) — see erp/decisions/SEC/ADR-SEC-001.md

Event
"P2 completed: SEC v1 — 13 tables, 104 DBF, 0 XM"

Cascade
No registry XM row anywhere in the platform currently targets SEC with status DEFERRED
(SEC is the first module through this pipeline this batch) — nothing to resolve.
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
