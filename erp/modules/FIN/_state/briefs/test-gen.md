# BRIEF — stage `test-gen` (Test Generation) · module FIN · v1 · profile `erp`

Lane `test-gen` · implementer claude:opus · effort high · round 1

## Rules that bind this run
- Questions: **forbidden**. A `[QUESTION]` block is refused. Ambiguity → ADR in `erp/decisions/FIN/` (`ADR-{MOD}-{seq:03d}.md`): non-breaking → continue; breaking → status BLOCKED and stop.
- Owns IDs: TC — ID grammar `{prefix}-{MOD}-{seq}` (seq width 3); never re-number, never restart a sequence.
- Read only what this brief contains (generated current state); never open version folders yourself.
- Write exactly these files (complete files; in a delta version only what changed, plus `change-manifest.md`):
- `erp/modules/FIN/test_gen/backend-test-plan-fin.md`
- `erp/modules/FIN/test_gen/frontend-test-plan-fin.md`
- `erp/modules/FIN/test_gen/test-execution-manifest-fin.md` (optional)
- `erp/system-test-index-erp.md` (optional)
- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; when running as the operator, write the files directly.

## Contracts checked by `gov.py analyze` after this stage
- **C10** acceptance criteria → test generation (standalone): C10.1 traces {'from': 'TC', 'to': ['AC', 'XM', 'UXD'], 'min': 1, 'mode': 'any'} [CRITICAL]; C10.2 orphans {'kind': 'AC', 'referenced_by': ['TC'], 'min': 1} [MAJOR]; C10.3 markers {'artifact': 'backend-test-plan', 'track': 'backend', 'plan': 'test'} [CRITICAL]; C10.4 markers {'artifact': 'frontend-test-plan', 'track': 'frontend', 'plan': 'test'} [CRITICAL]; C10.5 ids-owned {'stage': 'test-gen'} [CRITICAL]; C10.6 exists {'artifact': 'test-execution-manifest', 'when': 'profile.stack.testing.manifest'} [MINOR]

---
# ENGINE
```
ENGINE        : test-gen — Test Generation   (STANDALONE — outside the line, on demand)
LANE          : test-gen · questions forbidden · derives from `AC-*` (module) + `XM-*`/`UXD-*` (integration)
SCOPE         : module · modules FIN
MODULE        : FIN · v1 · profile erp (ERP Platform)
READS         : srs · backend-execution-plan? · frontend-execution-plan? · registry-srs · registry-db? · registry-exec-fe?   (from _state/ — "?" = optional — read for EACH module in scope)
PRODUCES      : backend-test-plan-fin.md · frontend-test-plan-fin.md · test-execution-manifest-fin.md (optional)
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

This run: **scope = `module`**, modules = `FIN`.

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
also in `FIN` — an `XM-*` targeting a module outside the selection is
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
module that owns the displayed data) is also in `FIN`.

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
<header>   sources (_state files + versions) · scope `module` · framework note (§3) · REDUCED? · open ADRs
<!-- PHASE:TEST-PLAN-BE:START traces=<union of the TCs' REQ/AC> -->
  <!-- SUB:RULE-SCENARIOS:START traces=… -->  …TC blocks…  <!-- SUB:RULE-SCENARIOS:END -->
  <!-- SUB:API-SCENARIOS:START traces=… -->  …TC blocks…  <!-- SUB:API-SCENARIOS:END -->
  (SUBs only when the threshold is met — decide WHILE writing, from the TC count)
<!-- PHASE:TEST-PLAN-BE:END -->
TC TRACEABILITY INDEX   AC → TC · REQ → TC · API → TC · RULE/code → TC
COVERAGE                AC covered <n>/<total> (a gap is ✗ and blocks the run) · REQ covered · API covered
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
<header>   sources (_state files + versions) · scope `module` · framework note (§3) · REDUCED? · open ADRs
<!-- PHASE:TEST-PLAN-FE:START traces=<union of the TCs' REQ/AC> -->
  <!-- SUB:UI-FLOWS:START traces=… -->  …TC blocks…  <!-- SUB:UI-FLOWS:END -->
  <!-- SUB:INT-FLOW:START traces=… -->  …TC blocks…  <!-- SUB:INT-FLOW:END -->
  (SUBs only when the threshold is met — decide WHILE writing, from the TC count)
<!-- PHASE:TEST-PLAN-FE:END -->
TC TRACEABILITY INDEX   AC → TC · REQ → TC · SCR → TC · RULE/code → TC
COVERAGE                AC covered <n>/<total> (a gap is ✗ and blocks the run) · REQ covered · SCR covered
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
[ ] every TC-* carries traces= with its AC-*/XM-*/UXD-* source (+ the upstream ids the plan names) and the atom marker pair
[ ] every TC names one of AC/XM/UXD as its source; no reworded rule/message/endpoint; test data never invented
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
| `TC-*`, the test plans, the manifest | `REQ/AC/RULE` (P1), `API` (P3.1), `SCR/UXD` (P3.2 — `UXD` is `P3.2`'s, cited never redefined), `DBF/XM` (P2 — `XM` is `P2`'s, cited never redefined), catalog codes | test code, framework scaffolding, any edit to a line artifact, any gate or verdict, a cross-module TC for a module outside the current selection |


---
# INPUTS (generated current state)

<<<INPUT: srs>>>
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
| transactional | PRIVATE | **Yes** — `docNo` is exactly the numbered transactional document case [§3.3 test (c)]: system-generated on first save, read-only after, unique per fiscal year. Format `JV-{fiscalYearCode}-{NNNNNN}` (e.g. `JV-2026-000123`), counter scoped per `fiscalYearId` and restarting at `000001` each year, one counter across all journal types, produced by a FIN-local generator in `com.erp.fin` — NOT a "platform numbering engine", which does not exist in this platform and never did | create (4 sources), read, search, reverse | none | general-accounting-system-plan-en.md §7, §8, §9 |

| Field | Logical type | Required | Values / source | Notes | Label-ar | Label-en |
|---|---|---|---|---|---|---|
| journalEntryPk | number | yes (system) | — | primary key | معرّف القيد | Journal entry id |
| docNo | text | yes (system) | FIN-local generator (`com.erp.fin`), format `JV-{fiscalYearCode}-{NNNNNN}`; unique per fiscalYearId (UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO) | read-only after create | رقم المستند | Document number |
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
Rationale  : RULE-FIN-013 — prevents double-reversal (an entry that already carries a reversal link) or reversing a DRAFT row
Source     : general-accounting-system-plan-en.md §9
Priority   : MEDIUM
#### AC-FIN-030 — [REQ-FIN-030]
Given an entry already reversed once (it stays POSTED and carries a reversalEntryId link to its reversal)
When an accountant attempts to reverse it again
Then the system rejects the action

### REQ-FIN-031 — إنشاء سنة مالية وفتراتها / Create a fiscal year with its periods
Pattern    : event
Statement  : When a finance administrator creates a fiscal year, the system shall generate its periods in the Open state per the chosen calendar. As built: a `periodCount` of twelve over a whole year generates the twelve calendar months, named from the JDK's CLDR month names in Arabic and English; any other count falls back to an even day split named "الفترة N" / "Period N".
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
Data source: ENT-FIN-001.parentAccountId, ENT-FIN-001.isLeafFl
Message    : ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" · en: "An account with sub-accounts cannot accept direct posting"
Traces     : REQ-FIN-002
Source     : general-accounting-system-plan-en.md §4.2

### RULE-FIN-002 — رفض رمز مكرر ضمن البُعد / Reject a duplicate code within a dimension
Scope      : ENT-FIN-003
Trigger    : on create (dimension value)
Statement  : The system shall reject a dimension value whose code already exists under the same dimension.
Data source: ENT-FIN-003.code, ENT-FIN-003.dimensionId
Message    : ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" · en: "This code is already used within this dimension"
Traces     : REQ-FIN-006
Source     : general-accounting-system-plan-en.md §4.2

### RULE-FIN-003 — سطر/هدف باقٍ واحد بالضبط عند التوزيع النسبي / Exactly one remainder line/target under percentage distribution
Scope      : ENT-FIN-010, ENT-FIN-014
Trigger    : on create/update (rule line or allocation target set)
Statement  : The system shall require exactly one line or target marked as the remainder whenever the set forms a compound or percentage distribution — that is, whenever any sibling line or target uses percentage distribution, or any line or target is already marked as the remainder (POL-FIN-006). The marker is `isRemainderFl`; a line or target whose marker disagrees with its own REMAINDER distribution/amount-source type code is rejected, since which line is the remainder decides every other line's amount under RULE-FIN-010.
Data source: ENT-FIN-010.isRemainderFl, ENT-FIN-010.distributionTypeCode, ENT-FIN-014.isRemainderFl, ENT-FIN-014.distributionTypeCode
Message    : ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" · en: "Exactly one remainder line is required when any percentage distribution is present"
Traces     : REQ-FIN-009
Source     : general-accounting-system-plan-en.md §6.3, §12.6

### RULE-FIN-004 — رفض مرجع حدث مكرر / Reject a duplicate event reference
Scope      : ENT-FIN-004
Trigger    : on create (event-sourced entry)
Statement  : The system shall reject building an entry for an event reference that has already produced a posted entry.
Data source: ENT-FIN-004.eventReference, ENT-FIN-004.statusCode
Message    : ar: "تم بالفعل ترحيل قيد لهذا المرجع" · en: "An entry for this event reference has already been posted"
Traces     : REQ-FIN-011
Source     : general-accounting-system-plan-en.md §12.12

### RULE-FIN-005 — رفض حدث بلا قاعدة نشطة / Reject an event with no active rule
Scope      : ENT-FIN-009
Trigger    : on create (event-sourced entry)
Statement  : The system shall reject building an entry for an event whose type has no active rule.
Data source: ENT-FIN-009.eventTypeCode, ENT-FIN-009.isActiveFl
Message    : ar: "لا توجد قاعدة نشطة لهذا النوع من الأحداث" · en: "No active rule exists for this event type"
Traces     : REQ-FIN-013
Source     : general-accounting-system-plan-en.md §6.1

### RULE-FIN-006 — ثبات تساوي المدين والدائن / Debit=Credit invariant
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on post (any source)
Statement  : The system shall reject posting an entry whose total debits do not equal its total credits to the smallest currency unit.
Data source: ENT-FIN-005.amount, ENT-FIN-005.directionCode
Message    : ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" · en: "The entry is unbalanced — total debits do not equal total credits"
Traces     : REQ-FIN-018
Source     : general-accounting-system-plan-en.md §12.1

### RULE-FIN-007 — الترحيل للأوراق النشطة فقط / Posting only to leaf, active accounts
Scope      : ENT-FIN-001, ENT-FIN-005
Trigger    : on post (any source)
Statement  : The system shall reject posting a line targeting an account that is not a leaf, not active, or not marked as accepting direct posting.
Data source: ENT-FIN-001.isLeafFl, ENT-FIN-001.isActiveFl, ENT-FIN-005.accountId
Message    : ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" · en: "The target account does not accept direct posting"
Traces     : REQ-FIN-019
Source     : general-accounting-system-plan-en.md §12.3

### RULE-FIN-008 — بوابة الفترة عند الترحيل / Period gate at post time
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on post (any source)
Statement  : The system shall reject posting an entry whose period is not Open at that moment, except the year-end closing and opening entries generated by the year-end close (REQ-FIN-036, API-FIN-027), which are exempt from this gate: that close may only run once every period of the year is Hard Closed, so no Open period exists for its own entries by construction. The exemption is part of this rule and applies to no other entry and to no other rule — RULE-FIN-006, RULE-FIN-007 and RULE-FIN-009 apply to both generated entries in full.
Data source: ENT-FIN-004.periodId, ENT-FIN-008.statusCode
Message    : ar: "الفترة المستهدفة غير مفتوحة" · en: "The target period is not open"
Traces     : REQ-FIN-020
Source     : general-accounting-system-plan-en.md §12.4

### RULE-FIN-009 — صحة قيمة البُعد / Dimension value validity
Scope      : ENT-FIN-006
Trigger    : on post (any source)
Statement  : The system shall reject posting a line whose cited dimension value does not belong to its stated dimension or is inactive.
Data source: ENT-FIN-006.dimensionId, ENT-FIN-006.dimensionValueId, ENT-FIN-003.dimensionId, ENT-FIN-003.isActiveFl
Message    : ar: "قيمة البُعد غير صالحة" · en: "The dimension value is invalid"
Traces     : REQ-FIN-021
Source     : general-accounting-system-plan-en.md §8.1

### RULE-FIN-010 — سطر الباقي يمتص فرق التقريب / The remainder line absorbs the rounding difference
Scope      : ENT-FIN-005, ENT-FIN-010, ENT-FIN-014
Trigger    : on build (compound/percentage distribution — rule engine or allocation)
Statement  : The system shall compute the remainder line's amount per posting side — the total already carried by the opposing side minus the sum of every other line on the remainder line's own side — after every percentage line rounds to the smallest currency unit. The remainder line is never itself computed as a percentage, and its computed amount must be positive (POL-FIN-005): a distribution whose other lines already equal or exceed the opposing side leaves no residue to absorb and is rejected.
Data source: ENT-FIN-005.amount, ENT-FIN-005.isRemainderFl, ENT-FIN-010.distributionTypeCode, ENT-FIN-014.distributionValue
Message    : ar: "سطر الباقي يُحسب كفرق، لا كنسبة" · en: "The remainder line is computed as a difference, never as a percentage"
Traces     : REQ-FIN-012, REQ-FIN-026
Source     : general-accounting-system-plan-en.md §6.3, §12.6

### RULE-FIN-011 — العكس تام ومرتبط / Reversal is exact and linked
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on reverse
Statement  : The system shall build the reversal entry with the same lines as the original, each with the opposite direction and the same amount, and link both entries to each other.
Data source: ENT-FIN-005.amount, ENT-FIN-005.directionCode, ENT-FIN-004.originalEntryId, ENT-FIN-004.reversalEntryId
Message    : ar: "قيد العكس يطابق الأصل بعكس الاتجاه" · en: "The reversal entry mirrors the original with opposite direction"
Traces     : REQ-FIN-028
Source     : general-accounting-system-plan-en.md §12.7, §9

### RULE-FIN-012 — ترحيل العكس بالفترة الحالية عند إغلاق الأصل / Reversal posts to the current period when the original's is closed
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on reverse
Statement  : The system shall post the reversal into the current open period when the original entry's own period is no longer Open.
Data source: ENT-FIN-004.periodId, ENT-FIN-008.statusCode
Message    : ar: "سيُرحَّل قيد العكس في الفترة المفتوحة الحالية" · en: "The reversal will post into the current open period"
Traces     : REQ-FIN-029
Source     : general-accounting-system-plan-en.md §9

### RULE-FIN-013 — رفض عكس قيد غير مُرحَّل / Reject reversing a non-posted entry
Scope      : ENT-FIN-004
Trigger    : on reverse
Statement  : The system shall reject a reverse action on an entry that is not POSTED.
Data source: ENT-FIN-004.statusCode
Message    : ar: "لا يمكن عكس قيد غير مُرحَّل" · en: "A non-posted entry cannot be reversed"
Traces     : REQ-FIN-030
Source     : general-accounting-system-plan-en.md §9

### RULE-FIN-014 — رفض إعادة فتح فترة مغلقة صارمًا / Reject reopening a hard-closed period
Scope      : ENT-FIN-008
Trigger    : on update (period status)
Statement  : The system shall reject any attempt to reopen a Hard Closed period.
Data source: ENT-FIN-008.statusCode
Message    : ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" · en: "The period is hard-closed and cannot be reopened"
Traces     : REQ-FIN-035
Source     : general-accounting-system-plan-en.md §10.2

### RULE-FIN-015 — فصل صلاحية الاعتماد عن صلاحية الإنشاء / Separate the approval permission from the creation permission
Scope      : ENT-FIN-008
Trigger    : on evaluate (period-close-approval action)
Statement  : The system shall require the period-close-approval action to be gated by a permission distinct from the journal-entry-creation permission, enforced through the Security module.
Data source: DEFERRED — the permission matrix is the Security module's declaration surface; FIN declares no permission entity in this version, so the separation is enforced there and has no FIN-side field to read
Message    : ar: "صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود" · en: "The close-approval permission is separate from the entry-creation permission"
Traces     : REQ-FIN-038
Source     : general-accounting-system-plan-en.md §2.2, §8.2, §10.3
Enforcement note (2026-09-12, does not change the Statement above): satisfied in full by the
             `@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on `FiscalPeriodService.hardClose`
             (API-FIN-026) and `FiscalYearService.yearEndClose` (API-FIN-027) — a permission code
             distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`, enforced by SEC, exactly as the
             Statement and AC-FIN-038 describe. A STRICTER check once existed in FIN code and was
             removed by recorded human decision: `FinSeparationOfDutiesService` +
             `FiscalPeriodDomain.assertCanHardClose(...)` refused the close for EVERY caller
             whenever ANY single user in the system held both permissions — global user-set
             disjointness, which this rule does not ask for and which the `Data source` line above
             explicitly rules out by stating there is no FIN-side fact to read. `FIN-403-SOD-VIOLATION`
             is struck as unreachable; do not re-derive the removed behaviour from this rule.

### RULE-FIN-016 — قفل القيد بعد الترحيل / Lock an entry after posting
Scope      : ENT-FIN-004, ENT-FIN-005
Trigger    : on evaluate (any edit/delete attempt)
Statement  : The system shall reject any edit or delete attempt on a POSTED entry or its lines; correction is only through a reversal (REQ-FIN-028).
Data source: ENT-FIN-004.statusCode, ENT-FIN-005.journalEntryId
Message    : ar: "القيد المُرحَّل مقفل؛ التصحيح فقط عبر العكس" · en: "A posted entry is locked; correction is only through a reversal"
Traces     : REQ-FIN-016, REQ-FIN-017
Source     : general-accounting-system-plan-en.md §8.3, §12.13

### RULE-FIN-017 — تماسك السنة والفترة وتاريخ المستند / Fiscal year, period and document date must cohere
Scope      : ENT-FIN-004, ENT-FIN-008
Trigger    : on create (an entry whose fiscalYearId, periodId and docDate are all submitted)
Statement  : The system shall reject an entry whose submitted period does not belong to its submitted fiscal year, or whose document date falls outside that period's start/end dates. Entries the system itself generates derive the three from one another and are coherent by construction.
Data source: ENT-FIN-004.fiscalYearId, ENT-FIN-004.periodId, ENT-FIN-004.docDate, ENT-FIN-008.fiscalYearId, ENT-FIN-008.startDate, ENT-FIN-008.endDate
Message    : ar: "الفترة المحددة لا تتبع السنة المالية المحددة، أو تاريخ المستند خارج نطاقها" · en: "The selected period does not belong to the selected fiscal year, or the document date falls outside it"
Traces     : REQ-FIN-014, REQ-FIN-017
Source     : general-accounting-system-plan-en.md §8.1, §10.1

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
| JOURNAL_STATUS | DRAFT, POSTED, VOID (VOID is seeded in MDL by V26 and declared as `JournalEntry.STATUS_VOID`, but is now UNREACHABLE: classic reversal leaves the original POSTED and no code path writes VOID — see §A7) |
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
DRAFT  --(REQ-FIN-017, automatic validation passes)--> POSTED   (terminal)
POSTED --(REQ-FIN-028, reverse action)----------------> POSTED  (no transition — classic reversal: the original STAYS POSTED; its reversal is itself a new POSTED entry, and the two are linked through originalEntryId/reversalEntryId)
```
Classic reversal is the convention FIN follows: reversing an entry posts an equal, opposite
mirror entry and leaves the original POSTED and untouched, so the net effect on every account
balance is zero and both entries stay visible in the ledger and its audit trail. VOIDing the
original instead would remove it from the POSTED-only reports while the mirror remained,
netting to −(original). It also means RULE-FIN-016 (a POSTED row is never modified) holds
without exception — the reverse action's only write back to the original is the
reversalEntryId link.

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
Operations   : search, create, update, deactivate. No by-id read — deliberate v1 exclusion, see
               the note under B5
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
Page code: FIN_ACCOUNTS. Actions: VIEW, CREATE, UPDATE (covers deactivate — there is no DELETE
endpoint and no `PERM_FIN_ACCOUNTS_DELETE`; deactivate is `PUT /{id}/deactivate` gated by
`PERM_FIN_ACCOUNTS_UPDATE`).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search accounts | POST | /api/v1/fin/accounts/search | filters, paging (request body) | Page\<Account\> | — | REQ-FIN-001 |
| create account | POST | /api/v1/fin/accounts | account fields | Account | RULE-FIN-001 | REQ-FIN-001, REQ-FIN-002 |
| update account | PUT | /api/v1/fin/accounts/{id} | account fields | Account | RULE-FIN-001 | REQ-FIN-002 |
| deactivate account | PUT | /api/v1/fin/accounts/{id}/deactivate | id | Account | — | REQ-FIN-003 |

**No by-id read, and why.** `AccountController` publishes exactly these four endpoints — create,
update, deactivate and search (`AccountController.java:45, 52, 60, 66`) — and no `GET /{id}`. The
`read` this section's B1 Operations line used to name was never in B5 either, so the B1 line was
its only claim; it is narrowed here rather than deleted so the decision stays legible. A by-id read
is a deliberate v1 exclusion, not a pending endpoint: no REQ or AC asks for one (REQ-FIN-001/002/003
and AC-FIN-001…003 cover create, the leaf-flag rejection and deactivate), this is a Composite
"Search + Entry = ONE screen" requirement whose Entry form is populated from the search-result row,
and API-FIN-001 already returns the complete `Account` record, not a trimmed projection. Contrast
SCR-REQ-FIN-006, where a by-id read WAS built (API-FIN-022) because REQ-FIN-016/REQ-FIN-027 need
the entry's lines, which its search result does not carry.

## SCR-REQ-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values
### B1 — Definition
Purpose      : إدارة الأبعاد وقيمها.
Entities     : ENT-FIN-002, ENT-FIN-003
Operations   : search, create (dimension — no deactivate, deliberate; see B4); search, create,
               deactivate (value — API-FIN-035)
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
Page code: FIN_DIMENSIONS. Actions: VIEW, CREATE, UPDATE.

**UPDATE — the dimension-VALUE deactivate, and only that.** UPDATE covers exactly one endpoint:
API-FIN-035, `PUT /api/v1/fin/dimensions/values/{id}/deactivate`, published on
`DimensionController` (child endpoints live on the parent's controller) and delegating to
`DimensionValueService.deactivate`, gated by `PERM_FIN_DIMENSIONS_UPDATE`. That permission is
declared in `PermissionConstants` and is both registered and granted to `SYS_ADMIN` by migration
`V28__fin_dimensions_update_action.sql` — V24 had seeded VIEW and CREATE only, and V25's grant
statement (a `SELECT` over the registry) had already run, so V28 carries its own explicit grant
rather than relying on it. Deactivate is modelled as UPDATE and not DELETE, exactly as
FIN_ACCOUNTS models API-FIN-004. An unknown dimension-value id answers `FIN-404-DIMVALUE`, a new
code registered in `FinErrorCodes` and in both i18n bundles.

**The PARENT dimension deliberately has no deactivate.** No REQ, AC or RULE asks for one and
`Dimension.isActiveFl` (DBF-FIN-018) drives no behaviour, so that column stays unflippable through
the API by decision, not by oversight. The value-level flag (DBF-FIN-029) is the one RULE-FIN-009 /
REQ-FIN-021 read when rejecting a journal line that cites an INACTIVE dimension value —
`DimensionValueDomain.checkUsableOnLine` returns `FIN-409-INVALID-DIMENSION` off exactly this flag
— so before API-FIN-035 that branch was unreachable and untestable, and closing that gap is the
whole reason this half, and only this half, was built. No `activate` counterpart was added either,
matching the delivered `AccountService.deactivate` precedent.

**Previously recorded here, now superseded**: this section stated that FIN publishes no dimension
or dimension-value update/deactivate endpoint at all and that V24 seeds no
`PERM_FIN_DIMENSIONS_UPDATE`. That was an accurate description of the as-built state before
API-FIN-035 and V28; it is no longer true for the value half, and remains true for the parent half.

No DELETE: FIN publishes no `DELETE` endpoint on any screen, and neither V24 nor V28 seeds a
`PERM_FIN_DIMENSIONS_DELETE` row.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search dimensions | POST | /api/v1/fin/dimensions/search | filters, paging (request body) | Page\<Dimension\> | — | REQ-FIN-004 |
| create dimension | POST | /api/v1/fin/dimensions | code, nameAr, nameEn | Dimension | — | REQ-FIN-004 |
| create dimension value | POST | /api/v1/fin/dimensions/{id}/values | code, nameAr, nameEn, sortOrder | DimensionValue | RULE-FIN-002 | REQ-FIN-005, REQ-FIN-006 |
| search dimension values | POST | /api/v1/fin/dimensions/values/search | filters (incl. dimensionId), paging (request body) | Page\<DimensionValue\> | — | REQ-FIN-005 |
| deactivate dimension value | PUT | /api/v1/fin/dimensions/values/{id}/deactivate | id | DimensionValue (isActiveFl=false) | — | REQ-FIN-005 |

API-FIN-035 (the last row) is the endpoint that makes REQ-FIN-021 / RULE-FIN-009 reachable at all:
it is the only way to set `DimensionValue.isActiveFl` to false. There is no parent-dimension
counterpart and no `activate` — see B4.

## SCR-REQ-FIN-003 — قواعد المحرك / Engine rules
### B1 — Definition
Purpose      : إدارة قواعد ربط أنواع الأحداث بسطور القيد.
Entities     : ENT-FIN-009, ENT-FIN-010
Operations   : search, create, deactivate (rule — API-FIN-034); create (line). As built there is
               no update and no by-id read on either, and no line delete — see B4
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
Page code: FIN_RULES. Actions: VIEW, CREATE, UPDATE.

**UPDATE covers two endpoints**, both gated by the single `PERM_FIN_RULES_UPDATE` that V24 already
seeds — no new permission constant and no migration were needed: API-FIN-011 (add a rule line) and
API-FIN-034, `PUT /api/v1/fin/event-rules/{id}/deactivate` (note the base path is
`/api/v1/fin/event-rules`, not `event-type-rules`). An unknown rule id answers the pre-existing
`FIN-404-RULE`. API-FIN-034 exists because until it landed no rule could ever be retired, which
left `FIN-404-NO-ACTIVE-RULE` (RULE-FIN-005, raised by API-FIN-020) unreachable. **Stated
limitation**, recorded in `EventTypeRuleService`'s own javadoc: deactivating a rule does NOT free
its event type for a replacement rule, because `EventTypeRuleService.create` guards uniqueness with
`existsByEventTypeCode`, which is not scoped to the active flag. No `activate` counterpart was
added, matching the delivered `AccountService.deactivate` precedent.

**Not built, and why.** `EventTypeRuleService` publishes exactly `create`, `deactivate` and
`search`; `RuleLineService` publishes `create` alone. So the rule has no update and no by-id read
endpoint, and the line has none of update, by-id read or delete. The rule-line *delete* named under
B1 Operations is a deliberate v1 exclusion rather than an oversight: ENT-FIN-010 carries no active
flag to soft-delete against, and FIN publishes no `DELETE` endpoint on any screen — V24 seeds no
`PERM_FIN_RULES_DELETE` row for this or any other FIN screen.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search rules | POST | /api/v1/fin/event-rules/search | filters, paging (request body) | Page\<EventTypeRule\> | — | REQ-FIN-007 |
| create rule | POST | /api/v1/fin/event-rules | eventTypeCode, nameAr, nameEn | EventTypeRule | — | REQ-FIN-007 |
| add rule line | POST | /api/v1/fin/event-rules/{id}/lines | line fields | RuleLine | RULE-FIN-003 | REQ-FIN-008, REQ-FIN-009 |
| deactivate rule | PUT | /api/v1/fin/event-rules/{id}/deactivate | id | EventTypeRule (isActiveFl=false) | — | REQ-FIN-007 |

## SCR-REQ-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates
### B1 — Definition
Purpose      : إدارة القوالب المتكررة والعكسية.
Entities     : ENT-FIN-011, ENT-FIN-012
Operations   : search, create (template with its lines in one request), run, deactivate —
               API-FIN-012/013/014/036, which is everything `RecurringTemplateController`
               publishes. **`deactivate` (template) is DELIVERED as API-FIN-036 and, since
               2026-09-12, it DOES stop the template from running — that defect is CLOSED, see
               B4.** **`update` (template) is still NOT built and is now the ONLY open half of
               the original gap — also B4.** No by-id read and no line-level read/update/delete:
               deliberate v1 exclusions, also B4
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
Page code: FIN_RECURRING_TEMPLATES. Actions: VIEW, CREATE, UPDATE (covers BOTH "run" —
API-FIN-014 — and "deactivate" — API-FIN-036; one permission, `PERM_FIN_RECURRING_TEMPLATES_UPDATE`,
already seeded by V24 and already granted by V25's blanket Tier-3 grant, so API-FIN-036 needed no
new constant, no new error code and no migration). No DELETE endpoint and no
`PERM_FIN_RECURRING_TEMPLATES_DELETE`.

**As built.** `RecurringTemplateController` publishes exactly four endpoints, each at its mapping
annotation: `POST` create (API-FIN-013, `RecurringTemplateController.java:51`), `POST /{id}/run`
(API-FIN-014, `:62`), `PUT /{id}/deactivate` (API-FIN-036, `:68`) and `POST /search` (API-FIN-012,
`:76`). The B1 Operations line originally promised `read, update, deactivate` on the template and
`create, read, update, delete` on the line; `deactivate` has since been built, but `read` and
`update` on the template and everything but `create` on the line have not.

**Deliberate v1 exclusions.** *By-id read*: API-FIN-012's search already returns the FULL aggregate
— `RecurringTemplateService.search` batch-loads each page's lines and maps them into
`RecurringTemplateResponse.lines` (`RecurringTemplateService.java:405-411`) — so a `GET /{id}`
would return nothing the search does not, and no REQ or AC asks for one. *Line delete*: FIN
publishes no `DELETE` endpoint on any screen and V24 seeds no `PERM_FIN_*_DELETE` row, the same
already-taken decision recorded at SCR-REQ-FIN-003 §B4. *No `activate` counterpart to API-FIN-036*:
FIN ships none for any entity, following the delivered `AccountService.deactivate` precedent.

**`deactivate` (template) — DELIVERED as API-FIN-036.** The half of the defect this section used
to report — that no endpoint could ever set `IS_ACTIVE_FL` to FALSE — is closed.
`RecurringTemplateService.deactivate` loads the template, calls the entity's own `deactivate()`
helper (`RecurringTemplate.java:99`, which until now had zero callers), persists, then re-reads the
template's lines and hands them to the mapper before returning — the re-read is required because
`RecurringTemplateResponse.lineCount` is derived from the list the mapper is given, so an empty
list would misreport the aggregate as having no lines. Unknown id answers the pre-existing
`FIN-404-TEMPLATE`. It is gated on the pre-existing `PERM_FIN_RECURRING_TEMPLATES_UPDATE`, the same
permission API-FIN-014's run uses. No migration, no new constant, no new error code.

**DEFECT CLOSED 2026-09-12 — deactivate now stops the run.** This paragraph used to report an OPEN
DEFECT: `RecurringTemplateService.run` (API-FIN-014) did not read `isActiveFl`, so a deactivated
template still ran and still posted, and setting the flag changed no behaviour whatever. It is now
closed. `RecurringTemplateDomain.assertCanRun()` — a NEW Domain companion for ENT-FIN-011, created
for this — is called by `RecurringTemplateService.run` immediately after the template is loaded and
before the run date, period or lines are resolved, and refuses a deactivated template with a new
`FIN-409-NOT-ACTIVE` (HTTP 409; ar "هذا التعريف غير نشط ولا يمكن تشغيله", en "This definition is
deactivated and cannot be run"). `FIN-404-TEMPLATE` was deliberately NOT reused, because the
template does exist. AC-FIN-023, written "Given an **active** recurring template", is now fully
satisfied: the inactive state is reachable AND behaves differently. The flag's other observable
effect is unchanged — B2's advertised `isActiveFl(EXACT)` filter discriminates
(`RecurringTemplateService`'s sort/filter whitelist honours it).

**READ THIS BEFORE CITING THE GATE AS A REQUIREMENT.** No RULE-FIN-* states it. It was closed on a
**recorded human decision**, because closing it required inventing an "exists but is inactive"
error code, its HTTP status, its ar+en messages and its Error Catalog row — none of which any REQ,
AC or RULE asks for. A later session must not cite `FIN-409-NOT-ACTIVE` as pre-existing spec, and
must not infer from it that other unstated gates may be added the same way without a fresh
decision.

**OPEN DEFECT — `update` (template) is still missing.** This is now the ONLY open half of the
original gap: with deactivate but no update, a template created with a wrong account or amount
cannot be corrected — it can only be retired. Since 2026-09-12 retiring it does at least stop it
(above), so the wrong entries stop arriving; entries already posted before the retirement remain
recoverable only by reversing them one by one. It was not built because a correct update must decide the fate of the template's existing child
lines (replace wholesale? merge? reject if any line changed?), which is a design question no REQ,
AC or RULE answers. It is recorded here as a known gap, not as a reasoned exclusion.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search templates | POST | /api/v1/fin/recurring-templates/search | filters, paging (request body) | Page\<RecurringTemplate\> | — | REQ-FIN-022 |
| create template | POST | /api/v1/fin/recurring-templates | template + lines | RecurringTemplate | RULE-FIN-006 (reused, balance check applied at run time not save time) | REQ-FIN-022 |
| run template (system/scheduled) | POST | /api/v1/fin/recurring-templates/{id}/run | — | JournalEntry | RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009, RULE-FIN-011 | REQ-FIN-023, REQ-FIN-024 |
| deactivate template (API-FIN-036) | PUT | /api/v1/fin/recurring-templates/{id}/deactivate | path `id`, no body | RecurringTemplate (isActiveFl=false, lines included) | — (none beyond existence; since 2026-09-12 it DOES gate the run — a subsequent API-FIN-014 answers `FIN-409-NOT-ACTIVE`, by decision not by RULE — see B4) | REQ-FIN-022 |

## SCR-REQ-FIN-005 — قواعد التوزيع / Allocation rules
### B1 — Definition
Purpose      : إدارة قواعد توزيع رصيد حساب مصدر على أهدافه.
Entities     : ENT-FIN-013, ENT-FIN-014
Operations   : search, create (rule with its targets in one request), run, deactivate —
               API-FIN-015/016/017/037, which is everything `AllocationRuleController` publishes.
               **`deactivate` (rule) is DELIVERED as API-FIN-037 and, since 2026-09-12, it DOES
               stop the rule from running — that defect is CLOSED, see B4.** **`update` (rule) is
               still NOT built and is now the ONLY open half of the original gap — also B4.** No
               by-id read and no target-level read/update/delete: deliberate v1 exclusions, also B4
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
Page code: FIN_ALLOCATION_RULES. Actions: VIEW, CREATE, UPDATE (covers BOTH "run" — API-FIN-017 —
and "deactivate" — API-FIN-037; one permission, `PERM_FIN_ALLOCATION_RULES_UPDATE`, already seeded
by V24 and already granted by V25's blanket Tier-3 grant, so API-FIN-037 needed no new constant, no
new error code and no migration). No DELETE endpoint and no `PERM_FIN_ALLOCATION_RULES_DELETE`.

**As built.** `AllocationRuleController` publishes exactly four endpoints, each at its mapping
annotation: `POST` create (API-FIN-016, `AllocationRuleController.java:52`), `POST /{id}/run`
(API-FIN-017, `:63`), `PUT /{id}/deactivate` (API-FIN-037, `:69`) and `POST /search` (API-FIN-015,
`:76`). The B1 Operations line originally promised `read, update, deactivate` on the rule and
`create, read, update, delete` on the target; `deactivate` has since been built, but `read` and
`update` on the rule and everything but `create` on the target have not.

**Deliberate v1 exclusions.** *By-id read*: API-FIN-015's search returns the FULL aggregate,
targets included (`AllocationRuleResponse.targets`), so a `GET /{id}` would add nothing and no REQ
or AC asks for one — the same reasoning as SCR-REQ-FIN-004 §B4. *Target delete*: FIN publishes no
`DELETE` endpoint on any screen and V24 seeds no `PERM_FIN_*_DELETE` row. *No `activate`
counterpart to API-FIN-037*: FIN ships none for any entity, following the delivered
`AccountService.deactivate` precedent.

**`deactivate` (rule) — DELIVERED as API-FIN-037.** The half of the defect this section used to
report — that no endpoint could ever set `IS_ACTIVE_FL` to FALSE — is closed.
`AllocationRuleService.deactivate` loads the rule, calls the entity's own `deactivate()` helper
(`AllocationRule.java:91`, which until now had zero callers), persists, then re-reads the rule's
targets and hands them to the mapper before returning — the re-read is required because
`AllocationRuleResponse.targetCount` is derived from the list the mapper is given, so an empty list
would misreport the aggregate as having no targets. Unknown id answers the pre-existing
`FIN-404-ALLOCATION-RULE`. It is gated on the pre-existing `PERM_FIN_ALLOCATION_RULES_UPDATE`, the
same permission API-FIN-017's run uses. No migration, no new constant, no new error code. Nothing
is delegated to `AllocationRuleDomain` before the mutation: RULE-FIN-003, the one rule that Domain
owns, governs the remainder-target SET at create and run time and says nothing about the active
flag.

**DEFECT CLOSED 2026-09-12 — deactivate now stops the run.** This paragraph used to report an OPEN
DEFECT: `AllocationRuleService.run` (API-FIN-017) did not read `isActiveFl`, so a deactivated
allocation rule still ran and still posted, and the Domain accessor built for the flag was dead
code. It is now closed. `AllocationRuleDomain.assertCanRun()` is called by
`AllocationRuleService.run` immediately after the rule is loaded and before its targets are even
fetched, and refuses a deactivated rule with a new `FIN-409-NOT-ACTIVE` (HTTP 409; ar "هذا التعريف
غير نشط ولا يمكن تشغيله", en "This definition is deactivated and cannot be run").
`FIN-404-ALLOCATION-RULE` was deliberately NOT reused, because the rule does exist. B2's advertised
`isActiveFl(EXACT)` filter still discriminates as before.

**READ THIS BEFORE CITING THE GATE AS A REQUIREMENT.** No RULE-FIN-* states it — RULE-FIN-003, the
one rule `AllocationRuleDomain` owns, governs the remainder-target set and says nothing about the
active flag. The gate was added on a **recorded human decision**, since closing the gap required
inventing an error code, status and messages no REQ, AC or RULE asks for. Do not cite
`FIN-409-NOT-ACTIVE` as pre-existing spec. It closed on the same decision as SCR-REQ-FIN-004's.

**OPEN DEFECT — `update` (rule) is still missing.** This is now the ONLY open half of the original
gap: with deactivate but no update, a rule created with the wrong source account or target split
cannot be corrected — it can only be retired. Since 2026-09-12 retiring it does at least stop it
(above), so the wrong distributions stop arriving. It was not built because a correct update must decide the fate
of the rule's existing targets, and therefore of RULE-FIN-003's remainder-target set (replace
wholesale? merge? re-validate the remainder marker across the new set?), which is a design question
no REQ, AC or RULE answers. It is recorded here as a known gap, not as a reasoned exclusion.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search allocation rules | POST | /api/v1/fin/allocation-rules/search | filters, paging (request body) | Page\<AllocationRule\> | — | REQ-FIN-025 |
| create allocation rule | POST | /api/v1/fin/allocation-rules | rule + targets | AllocationRule | RULE-FIN-003 | REQ-FIN-025 |
| run allocation rule | POST | /api/v1/fin/allocation-rules/{id}/run | — | JournalEntry | RULE-FIN-006..011 | REQ-FIN-026 |
| deactivate allocation rule (API-FIN-037) | PUT | /api/v1/fin/allocation-rules/{id}/deactivate | path `id`, no body | AllocationRule (isActiveFl=false, targets included) | — (none beyond existence; since 2026-09-12 it DOES gate the run — a subsequent API-FIN-017 answers `FIN-409-NOT-ACTIVE`, by decision not by RULE — see B4) | REQ-FIN-025 |

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
| search entries | POST | /api/v1/fin/journal-entries/search | filters, paging (request body) | Page\<JournalEntry\> | — | REQ-FIN-027 |
| create manual entry | POST | /api/v1/fin/journal-entries | header + lines | JournalEntry (DRAFT then POSTED) | RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009, RULE-FIN-017 | REQ-FIN-014, REQ-FIN-015, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021 |
| build event entry (system) | POST | /api/v1/fin/journal-entries/from-event | canonical event payload | JournalEntry | RULE-FIN-004, RULE-FIN-005, RULE-FIN-006..009, RULE-FIN-010 | REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-017..021 |
| reverse entry | POST | /api/v1/fin/journal-entries/{id}/reverse | id | JournalEntry (the new reversal) | RULE-FIN-011, RULE-FIN-012, RULE-FIN-013 | REQ-FIN-028, REQ-FIN-029, REQ-FIN-030 |
| read entry | GET | /api/v1/fin/journal-entries/{id} | id | JournalEntry with lines | — | REQ-FIN-016, REQ-FIN-027 |

## SCR-REQ-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years + close approval + year-end close
### B1 — Definition
Purpose      : إدارة السنوات والفترات المالية، اعتماد الإغلاق، وتشغيل إقفال نهاية السنة.
Entities     : ENT-FIN-007, ENT-FIN-008
Operations   : create (year); search — PERIODS only (API-FIN-033); open, soft-close, hard-close
               (period); run year-end close. There is NO fiscal-YEAR search and no by-id read of
               either a year or a period — see the note under B5
Users        : مسؤول مالي (إدارة) / مراقب مالي (اعتماد الإغلاق — دور منفصل، POL-FIN-016)
Navigation   : FIN → Control → Fiscal periods & years
Content shape: header + repeating lines (year + its periods)
Traces       : REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038
Composite    : Master (years) + Detail (periods) = ONE screen requirement
### B2 — Search / list
Filters: fiscalYearId(EXACT), statusCode(EXACT) — both OPTIONAL. As delivered by API-FIN-033 these
are exactly the two filters implemented (`FiscalPeriodSearchRequest`), plus paging and sort.
`fiscalYearId` travels inside the body's `filters` list and narrows to one year's periods when
supplied; omitting it is a legitimate "all periods" request, deliberately unlike the dimension-value
child search (API-FIN-008), which rejects a missing parent id. The divergence is the point of the
endpoint: a client that did not create the fiscal year in the same session must still be able to
discover a period id.
### B3 — Input
Year fields: code, startDate, endDate, periodCount (ENT-FIN-007). Period actions per row:
Open, Soft-close, Hard-close (approval-gated). Year action: "Run year-end close" (enabled
only once every period is Hard Closed).
### B4 — Access
Page code: FIN_PERIODS. Actions: VIEW (`PERM_FIN_PERIODS_VIEW` — the screen's gateway, and since
API-FIN-033 also the permission behind a real read endpoint), CREATE (year), UPDATE
(open/soft-close, and a distinct custom action `PERM_FIN_PERIODS_CLOSE_APPROVE` for
hard-close/year-end-close — RULE-FIN-015).
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| search fiscal periods | POST | /api/v1/fin/fiscal-periods/search | filters (fiscalYearId?, statusCode?), paging (request body) | Page\<FiscalPeriod\> | — | REQ-FIN-031 |
| create fiscal year | POST | /api/v1/fin/fiscal-years | code, startDate, endDate, periodCount | FiscalYear + FiscalPeriod[] | — | REQ-FIN-031 |
| open period | PATCH | /api/v1/fin/fiscal-periods/{id}/open | id | FiscalPeriod | — | REQ-FIN-032 |
| soft-close period | PATCH | /api/v1/fin/fiscal-periods/{id}/soft-close | id | FiscalPeriod | — | REQ-FIN-033 |
| hard-close period (approval) | PATCH | /api/v1/fin/fiscal-periods/{id}/hard-close | id | FiscalPeriod | RULE-FIN-014, RULE-FIN-015 | REQ-FIN-034, REQ-FIN-035, REQ-FIN-037, REQ-FIN-038 |
| run year-end close | POST | /api/v1/fin/fiscal-years/{id}/year-end-close | id | closing + opening JournalEntry | RULE-FIN-006, RULE-FIN-007, RULE-FIN-009, RULE-FIN-015 (RULE-FIN-008 does NOT apply — the year-end CLOSING/OPENING entries are exempt from the period gate by RULE-FIN-008's own carve-out; they are precisely the entries a hard-closed period must still accept) | REQ-FIN-036 |

**A fiscal-period search API now exists: API-FIN-033**, `POST /api/v1/fin/fiscal-periods/search`
(`FiscalPeriodController.search` → `FiscalPeriodService.search`), serving the B2 filters directly
and gated by `PERM_FIN_PERIODS_VIEW` — which was already a registered V24 action row and already
granted by V25/V27, so no migration was needed; the endpoint only added the matching
`PermissionConstants` constant. Until it landed, the B2 filters were served solely by API-FIN-023's
response (the year with its generated periods), which is what this paragraph previously recorded,
and `PERM_FIN_PERIODS_VIEW` was a gateway row with no endpoint behind it. That is no longer the
case.

Why it was built: `JournalEntryCreateRequest` requires both `fiscalYearId` and `periodId`
(API-FIN-019, RULE-FIN-017), and API-FIN-029/030/031 require a period or year id of their own, yet
no API returned a fiscal period except the API-FIN-023 create response. A client that had not
created the year in the same session therefore could not post an entry or run a report at all.

**What API-FIN-033 is NOT, and what B1 no longer claims.** The B1 Operations line used to read
`create (year), search, read`. Measured against the controllers: `FiscalYearController` publishes
exactly two endpoints, `POST` create (API-FIN-023, `FiscalYearController.java:39`) and
`POST /{id}/year-end-close` (API-FIN-027, `:47`); `FiscalPeriodController` publishes the three
PATCH transitions plus `POST /search` (`FiscalPeriodController.java:49, 55, 61, 68`). So the
`search` B1 named is API-FIN-033 over fiscal PERIODS — **there is no fiscal-year search**, and
API-FIN-033 must not be read as one — and the `read` B1 named exists for neither resource: no
`GET /{id}` is published on a year or on a period.

*By-id read* is a deliberate v1 exclusion: API-FIN-023 returns the year together with its generated
periods, and API-FIN-033 returns the full `FiscalPeriodResponse` row, so neither a year nor a
period has a field a by-id read would newly expose. *Fiscal-year search* is recorded as a KNOWN GAP
rather than a reasoned exclusion — no REQ or AC asks for one (REQ-FIN-031 asks only that creating a
year generate its periods), and it is not blocking, because `FiscalPeriodResponse` carries
`fiscalYearId` (`FiscalPeriodResponse.java:31`), so an unfiltered API-FIN-033 call discovers year
ids indirectly. It is a gap and not a defect for that reason alone: the discovery path is awkward
(read a year id off any period row) but it exists, and nothing in the ledger can be corrupted by
its absence.

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
Filters: periodId(EXACT), accountTypeCode(EXACT) — both OPTIONAL query parameters as built.
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_TRIAL_BALANCE. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| trial balance | GET | /api/v1/fin/reports/trial-balance | periodId?, accountTypeCode? | one row per account (debit/credit balance) | — | REQ-FIN-040, REQ-FIN-046 |

**404 on an unknown keying id, as built.** `periodId` stays an OPTIONAL narrowing: omitting it
means "no period narrowing" and remains a 200 (AC-FIN-040's happy path). When it IS supplied it
must resolve — an unknown id now answers the pre-existing `FIN-404-PERIOD` rather than a silent 200
carrying an all-zero report. This aligns the screen with FIN's existing house style, where a
keying entity id 404s (API-FIN-028 → `FIN-404-ACCOUNT`, API-FIN-032 → `FIN-404-DIMENSION`).

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
Filters: fiscalYearId(EXACT, REQUIRED), asOfDate (optional cut-off).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_BALANCE_SHEET. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| balance sheet | GET | /api/v1/fin/reports/balance-sheet | fiscalYearId (required), asOfDate? | grouped balance-sheet accounts with balances | — | REQ-FIN-041, REQ-FIN-046 |

**404 on an unknown fiscal year, as built.** `fiscalYearId` is the REQUIRED keying identifier and
is resolved first: an unknown id answers the pre-existing `FIN-404-YEAR`. Previously it returned a
200 carrying an all-zero statement that a caller could not tell apart from a genuinely dormant
year.

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
Filters: fiscalYearId(EXACT, REQUIRED); the period range is expressed as built by two optional
period ids, `fromPeriodId` and `toPeriodId`, translated into the `docDate` bounds those periods
span (DBF-FIN-080 / DBF-FIN-081).
### B3 — Input
Not applicable.
### B4 — Access
Page code: FIN_INCOME_STATEMENT. Action: VIEW.
### B5 — API expectations
| Operation | Verb | Path | Inputs | Outputs | RULEs | Traces (REQ) |
|---|---|---|---|---|---|---|
| income statement | GET | /api/v1/fin/reports/income-statement | fiscalYearId (required), fromPeriodId?, toPeriodId? | grouped revenue/expense accounts with balances | — | REQ-FIN-042, REQ-FIN-046 |

**404 on an unknown keying id, as built.** `fiscalYearId` is resolved first and raises the
pre-existing `FIN-404-YEAR` when it does not exist; `fromPeriodId` / `toPeriodId` stay OPTIONAL
narrowings and already raised `FIN-404-PERIOD` when supplied and unknown — that half is unchanged.
The year check closes an internal contradiction: the same request used to answer 404 on an unknown
period and 200 on an unknown year.

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
| FIN_ACCOUNTS | Chart of accounts | role-granted | role-granted | role-granted (incl. deactivate) | — | — |
| FIN_DIMENSIONS | Dimensions | role-granted | role-granted | role-granted (dimension-VALUE deactivate only — API-FIN-035; `PERM_FIN_DIMENSIONS_UPDATE`, registered and granted by V28) | — | — |
| FIN_RULES | Engine rules | role-granted | role-granted | role-granted (add line — API-FIN-011; and deactivate rule — API-FIN-034; one permission, `PERM_FIN_RULES_UPDATE`) | — | — |
| FIN_RECURRING_TEMPLATES | Recurring/reversing templates | role-granted | role-granted | role-granted (run — API-FIN-014; and deactivate template — API-FIN-036; one permission, `PERM_FIN_RECURRING_TEMPLATES_UPDATE`) | — | — |
| FIN_ALLOCATION_RULES | Allocation rules | role-granted | role-granted | role-granted (run — API-FIN-017; and deactivate rule — API-FIN-037; one permission, `PERM_FIN_ALLOCATION_RULES_UPDATE`) | — | — |
| FIN_JOURNAL_ENTRIES | Journal entries | role-granted | role-granted (incl. Post) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`) |
| FIN_PERIODS | Fiscal periods & years | role-granted (gateway, and now also the read endpoint API-FIN-033) | role-granted (year) | role-granted (open/soft-close) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE` — the distinct permission RULE-FIN-015 requires. Since V30 it is granted to `SYS_ADMIN`, so the bootstrap `admin` can close; V27's dedicated `FIN_CLOSE_APPROVER` role remains valid as a least-privilege alternative but is no longer required — see the SoD note below) |
| FIN_ACCOUNT_LEDGER | Account ledger | role-granted | — | — | — | — |
| FIN_TRIAL_BALANCE | Trial balance | role-granted | — | — | — | — |
| FIN_BALANCE_SHEET | Balance sheet | role-granted | — | — | — | — |
| FIN_INCOME_STATEMENT | Income statement | role-granted | — | — | — | — |
| FIN_DIMENSION_REPORTS | Dimension reports | role-granted | — | — | — | — |
Every action beyond VIEW additionally requires VIEW on the same screen (platform gateway
convention, `profiles/erp.yaml → conventions.security_model.gateway_action`, enforced by
SEC's own mechanism — not restated as a FIN-owned RULE).

**DELETE column, as built**: empty for every FIN screen. FIN publishes no `DELETE` endpoint;
deactivation, where it exists, is `PUT /{id}/deactivate` gated by the screen's UPDATE permission,
and V24 seeds no `PERM_FIN_*_DELETE` row (nor does V28, which adds only
`PERM_FIN_DIMENSIONS_UPDATE`). The DELETE ✓ marks above were pre-implementation and were corrected
at ALIGN-BE.

**Deactivate endpoints, as built**: five — API-FIN-004 (account), API-FIN-034 (event-type rule),
API-FIN-035 (dimension value), API-FIN-036 (recurring/reversing template) and API-FIN-037
(allocation rule). None has an `activate` counterpart, following the delivered
`AccountService.deactivate` precedent. Each is `PUT /{id}/deactivate` gated by its screen's UPDATE
permission; API-FIN-036 and API-FIN-037 reuse `PERM_FIN_RECURRING_TEMPLATES_UPDATE` and
`PERM_FIN_ALLOCATION_RULES_UPDATE`, both already seeded by V24 and already granted by V25's blanket
Tier-3 grant, so neither needed a new permission, a new error code or a migration. Deliberately NOT
built, and not pending: a deactivate on the parent `Dimension` (no REQ/AC/RULE requires it and
`Dimension.isActiveFl` drives no behaviour) and a rule-line delete (ENT-FIN-010 has no active-flag
column and FIN publishes no `DELETE` endpoint on any screen) — see SCR-REQ-FIN-002 §B4 and
SCR-REQ-FIN-003 §B4.

**DEFECT CLOSED 2026-09-12 — on those two screens, deactivating now DOES stop the run.** This
supersedes the entry that used to stand here reporting the run as ungated. `RecurringTemplateDomain
.assertCanRun()` (a new Domain companion) and `AllocationRuleDomain.assertCanRun()` are each called
first thing in their service's `run`, so a deactivated template or allocation rule is refused with
`FIN-409-NOT-ACTIVE` (409) and posts nothing. The UPDATE cells above cover run AND deactivate for
these two screens, and "deactivate" there now means a real gate, not only a record-keeping state.
**The gate is a recorded human decision, not stated requirement: no RULE-FIN-* asks for it**, and
closing the gap required inventing an error code, status and ar+en messages that no REQ, AC or RULE
provides — do not read `FIN-409-NOT-ACTIVE` back out of these tables as pre-existing spec. See
SCR-REQ-FIN-004 §B4 and SCR-REQ-FIN-005 §B4.

**SoD on FIN_PERIODS — what was removed, and what still holds (2026-09-12).** RULE-FIN-015 stands
and is enforced by the `PERM_FIN_PERIODS_CLOSE_APPROVE` gate alone, which is exactly what the rule
asks for. A stricter, unrequested check — FIN service code that refused the close for every caller
whenever any single user in the system held both that permission and
`PERM_FIN_JOURNAL_ENTRIES_CREATE` — was deleted by recorded human decision, together with the SEC
user-directory read behind it; `FIN-403-SOD-VIOLATION` is struck as unreachable. Migration V30 then
granted `PERM_FIN_PERIODS_CLOSE_APPROVE` to `SYS_ADMIN`, which V25 had deliberately withheld, so
the bootstrap `admin` can now close. Note that V27's header, being applied and immutable, still
describes the removed mechanism as live in both its numbered "OPERATIONAL PRECONDITIONS" — both are
now false; see the SEC-BE phase document for the correction in full.

**OPEN DEFECT — `update` is still missing on the same two screens.** This is now the only open half
of the original gap: a template or allocation rule created with wrong content can be retired — and,
since 2026-09-12, retiring it does stop it running — but it still cannot be corrected. Neither update was built because a
correct one must decide the fate of the aggregate's children — a template's existing lines, a
rule's existing targets and hence RULE-FIN-003's remainder-target set — which is a design question
no REQ, AC or RULE answers. Recorded as a known gap, not a reasoned exclusion. See SCR-REQ-FIN-004
§B4 and SCR-REQ-FIN-005 §B4.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: backend-execution-plan>>>
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
RULES         17 — RULE-FIN-001..017 (RULE-FIN-017, fiscal-year/period/docDate coherence,
              added during SVC-API and carried back into srs-fin.md §A5), all 14 §12
              must-honor points covered (see ALIGN)
SCREENS       12 — SCR-REQ-FIN-001..012
PERMISSIONS   12 secured page codes + PERM_<PAGE_CODE>_<ACTION>, gateway VIEW, plus the
              custom `PERM_FIN_PERIODS_CLOSE_APPROVE` (RULE-FIN-015 SoD)
LOOKUPS       13 keys, all FIN-owned, registered into MDL (SRS A6) — none CHECK-constrained
              locally (unlike SEC's ADR-SEC-001; MDL is already gated)
BUSINESS CODE JournalEntry.docNo — system-generated `JV-{fiscalYearCode}-{NNNNNN}`
              (e.g. JV-2026-000123) by a FIN-local generator in com.erp.fin; counter
              scoped per fiscalYearId, restarts at 000001 each fiscal year, single
              counter across all journal types; unique per fiscalYearId
              (UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO), read-only after create
── FROM db-script ────────────────────────────────────────────────────────
TABLES        14 tables, FIN_ACCOUNT … FIN_ALLOCATION_TARGET
PK GENERATION every table: an explicit `SEQ_<TABLE>` sequence (V22 BLOCK 1) — a deliberate,
              documented deviation from db-script's `GENERATED ALWAYS AS IDENTITY`, required by
              build-create-entity A.1.3/A.1.4 and matching SEC/MDL/CU/NOTIF/FILE
COLUMNS       147 DBF-FIN-001..147
CONSTRAINTS   PK_*, UQ_*, CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE (POL-FIN-005), FK_*; INDEXES IDX_*
XM            1 — XM-FIN-001 SOFT-READ → MDL_LOOKUP_VALUE, status ACTIVE. XM-FIN-002
              (READ → SEC user directory, SecUserDirectoryApi) was assigned at ALIGN-BE and
              RETIRED 2026-09-12 with the deletion of FinSeparationOfDutiesService — INT-C
── FROM registries ───────────────────────────────────────────────────────
SHARED ENTITIES CONSUMED   LookupType/LookupValue (MDL) via XM-FIN-001; SEC's identity/
                           authorization for every request, and FIN's self-registration into
                           SEC, consumed as platform-standard integration, not an XM row
                           (ADR-FIN-001 — unchanged). SEC's user→permission read model
                           (SecUserDirectoryApi) was consumed via XM-FIN-002 until
                           2026-09-12 and is not consumed any more
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
| ENT-FIN-004 | JournalEntry | FIN_JOURNAL_ENTRY | **docNo** (`JV-{fiscalYearCode}-{NNNNNN}`, FIN-local generator) | create (4 sources), read, search, reverse |
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

**FIELD REGISTRY** — see DB Alignment Manifest below (147 rows; property = camelCase of the
db-script column, per the same 1:1 transformation used for SEC/MDL — not restated as a
separate lighter table here given the row count, per this stage's own economy: the
Manifest already carries property/type/status, and read-only is uniformly: **Yes** for
every PK, every audit column, every system-timestamp column (postedAt, closedAt/closedBy,
createdAt-only child rows); **No** for every business-input field named in each entity's
SRS A3 "Required" column. The DB Alignment Manifest is the single canonical binding.

**API REGISTRY**
| API | Operation | Verb | Path | Traces (REQ) |
|---|---|---|---|---|
| API-FIN-001 | search accounts | POST | /api/v1/fin/accounts/search | REQ-FIN-001 |
| API-FIN-002 | create account | POST | /api/v1/fin/accounts | REQ-FIN-001, REQ-FIN-002 |
| API-FIN-003 | update account | PUT | /api/v1/fin/accounts/{id} | REQ-FIN-002 |
| API-FIN-004 | deactivate account | PUT | /api/v1/fin/accounts/{id}/deactivate | REQ-FIN-003 |
| API-FIN-005 | search dimensions | POST | /api/v1/fin/dimensions/search | REQ-FIN-004 |
| API-FIN-006 | create dimension | POST | /api/v1/fin/dimensions | REQ-FIN-004 |
| API-FIN-007 | create dimension value | POST | /api/v1/fin/dimensions/{id}/values | REQ-FIN-005, REQ-FIN-006 |
| API-FIN-008 | search dimension values | POST | /api/v1/fin/dimensions/values/search | REQ-FIN-005 |
| API-FIN-009 | search event-type rules | POST | /api/v1/fin/event-rules/search | REQ-FIN-007 |
| API-FIN-010 | create event-type rule | POST | /api/v1/fin/event-rules | REQ-FIN-007 |
| API-FIN-011 | add rule line | POST | /api/v1/fin/event-rules/{id}/lines | REQ-FIN-008, REQ-FIN-009 |
| API-FIN-012 | search templates | POST | /api/v1/fin/recurring-templates/search | REQ-FIN-022 |
| API-FIN-013 | create template | POST | /api/v1/fin/recurring-templates | REQ-FIN-022 |
| API-FIN-014 | run template | POST | /api/v1/fin/recurring-templates/{id}/run | REQ-FIN-023, REQ-FIN-024 |
| API-FIN-015 | search allocation rules | POST | /api/v1/fin/allocation-rules/search | REQ-FIN-025 |
| API-FIN-016 | create allocation rule | POST | /api/v1/fin/allocation-rules | REQ-FIN-025 |
| API-FIN-017 | run allocation rule | POST | /api/v1/fin/allocation-rules/{id}/run | REQ-FIN-026 |
| API-FIN-018 | search journal entries | POST | /api/v1/fin/journal-entries/search | REQ-FIN-027 |
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

**QRC SUMMARY** — 49 QR ids, QR-FIN-001..049 (045-049 assigned at ALIGN-BE to queries that
were implemented but uncatalogued) — see Query Reference Catalog below.

**DB ALIGNMENT** — see manifest below — ALIGNED ✓ / issues: 0
**XM STATUS** — 1 live (XM-FIN-001, SOFT-READ → MDL, ACTIVE); XM-FIN-002 (READ → SEC) RETIRED 2026-09-12
**SECURITY** — 12 secured screens, data-driven role grants + 1 custom permission (close-approve, `PERM_FIN_PERIODS_CLOSE_APPROVE` — the distinct permission RULE-FIN-015 requires; the service-layer SoD check that once sat behind it was removed 2026-09-12, see SEC-BE)

## DB Alignment Manifest — FIN v1
All 147 rows: **status ✓ (aligned)**; XM populated only on lookup-backed columns (16
columns across 10 tables touch XM-FIN-001, noted individually below — a SOFT-READ, never
blocking; the count read 12/8 until ALIGN-BE recounted it against V22's 16 XM-FIN-001
`COMMENT ON COLUMN` lines). XM-FIN-002 bound no column — it was a service-to-service read of
SEC's user directory, not a lookup-backed value — so it carries no row in this manifest and
never did; it was retired on 2026-09-12 in any case.

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
| DBF-FIN-098 | ENT-FIN-010 | ruleLinePk | Long | — |
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
| DBF-FIN-109 | ENT-FIN-011 | recurringTemplatePk | Long | — |
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
| DBF-FIN-122 | ENT-FIN-012 | recurringTemplateLinePk | Long | — |
| DBF-FIN-123 | ENT-FIN-012 | recurringTemplateId | Long | — |
| DBF-FIN-124 | ENT-FIN-012 | lineNo | Integer | — |
| DBF-FIN-125 | ENT-FIN-012 | accountId | Long | — |
| DBF-FIN-126 | ENT-FIN-012 | amount | BigDecimal | — |
| DBF-FIN-127 | ENT-FIN-012 | directionCode | String | XM-FIN-001 |
| DBF-FIN-128 | ENT-FIN-012 | dimensionValueId | Long | — |
| DBF-FIN-129 | ENT-FIN-012 | createdAt | Instant | — |
| DBF-FIN-130 | ENT-FIN-013 | allocationRulePk | Long | — |
| DBF-FIN-131 | ENT-FIN-013 | nameAr | String | — |
| DBF-FIN-132 | ENT-FIN-013 | nameEn | String | — |
| DBF-FIN-133 | ENT-FIN-013 | sourceAccountId | Long | — |
| DBF-FIN-134 | ENT-FIN-013 | isActiveFl | Boolean | — |
| DBF-FIN-135 | ENT-FIN-013 | createdBy | String | — |
| DBF-FIN-136 | ENT-FIN-013 | createdAt | Instant | — |
| DBF-FIN-137 | ENT-FIN-013 | updatedBy | String | — |
| DBF-FIN-138 | ENT-FIN-013 | updatedAt | Instant | — |
| DBF-FIN-139 | ENT-FIN-014 | allocationTargetPk | Long | — |
| DBF-FIN-140 | ENT-FIN-014 | allocationRuleId | Long | — |
| DBF-FIN-141 | ENT-FIN-014 | lineNo | Integer | — |
| DBF-FIN-142 | ENT-FIN-014 | targetAccountId | Long | — |
| DBF-FIN-143 | ENT-FIN-014 | dimensionValueId | Long | — |
| DBF-FIN-144 | ENT-FIN-014 | distributionTypeCode | String | XM-FIN-001 |
| DBF-FIN-145 | ENT-FIN-014 | distributionValue | BigDecimal | — |
| DBF-FIN-146 | ENT-FIN-014 | isRemainderFl | Boolean | — |
| DBF-FIN-147 | ENT-FIN-001 | isRetainedEarningsFl | Boolean | — |

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
| QR-FIN-016 | EXISTS | API-FIN-011, API-FIN-016 | ENT-FIN-010, ENT-FIN-014 | RULE-FIN-003 | exactly one remainder line/target when a percentage distribution exists (scope widened here to match the id definition below and the code) |
| QR-FIN-017 | FIND_BY_CRITERIA | API-FIN-012 | ENT-FIN-011 | search | search templates |
| QR-FIN-018 | SAVE | API-FIN-013 | ENT-FIN-011, ENT-FIN-012 | create | create template with lines |
| QR-FIN-019 | FIND_ONE | API-FIN-014 | ENT-FIN-011 | run | load the template to run, by id (inherited `findById`; no due-date selection query exists — FIN exposes no scheduler endpoint) |
| QR-FIN-020 | FIND_BY_CRITERIA | API-FIN-015 | ENT-FIN-013 | search | search allocation rules |
| QR-FIN-021 | SAVE | API-FIN-016 | ENT-FIN-013, ENT-FIN-014 | create | create allocation rule with targets |
| QR-FIN-022 | FIND_ONE | API-FIN-017 | ENT-FIN-013 | run | load allocation rule + current source balance (via QR-FIN-043 — the shared balance aggregation; the earlier citation of QR-FIN-040, the hard-closed-period check, was wrong) |
| QR-FIN-023 | FIND_BY_CRITERIA | API-FIN-018 | ENT-FIN-004 | search | search journal entries |
| QR-FIN-024 | SAVE | API-FIN-019 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build manual entry (DRAFT) |
| QR-FIN-025 | SAVE | API-FIN-020 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build event entry (DRAFT) from rule |
| QR-FIN-026 | EXISTS | API-FIN-020 | ENT-FIN-004 | RULE-FIN-004 | duplicate eventReference |
| QR-FIN-027 | EXISTS | API-FIN-020 | ENT-FIN-009 | RULE-FIN-005 | active rule exists for event type |
| QR-FIN-028 | AGGREGATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-010 | compute remainder-line amount for a compound/percentage distribution |
| QR-FIN-029 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-005 | RULE-FIN-006 | debits = credits |
| QR-FIN-030 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-001 | RULE-FIN-007 | every line's account is leaf + active |
| QR-FIN-031 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-008 | RULE-FIN-008 | entry's period is Open at post time (not applied to API-FIN-027's CLOSING/OPENING entries — exempted by RULE-FIN-008 itself) |
| QR-FIN-032 | EXISTS | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-006 | RULE-FIN-009 | every dimension value valid + active |
| QR-FIN-033 | UPDATE | API-FIN-019, API-FIN-020, API-FIN-014, API-FIN-017 | ENT-FIN-004 | post | flip DRAFT → POSTED, set postedAt (RULE-FIN-016 lock takes effect) |
| QR-FIN-034 | SAVE | API-FIN-021 | ENT-FIN-004, ENT-FIN-005, ENT-FIN-006 | create | build reversal entry (RULE-FIN-011) |
| QR-FIN-035 | EXISTS | API-FIN-021, 014 | ENT-FIN-004 | RULE-FIN-013 | original entry is POSTED and not already reversed |
| QR-FIN-036 | FIND_ONE | API-FIN-021 | ENT-FIN-008 | RULE-FIN-012 | current open period, if original's is closed |
| QR-FIN-037 | FIND_ONE | API-FIN-022 | ENT-FIN-004 | read | read one entry with lines |
| QR-FIN-038 | SAVE | API-FIN-023 | ENT-FIN-007, ENT-FIN-008 | create | create fiscal year + periods |
| QR-FIN-039 | UPDATE | API-FIN-024, API-FIN-025, API-FIN-026 | ENT-FIN-008 | transition | open / soft-close / hard-close a period |
| QR-FIN-040 | EXISTS | API-FIN-026 | ENT-FIN-008 | RULE-FIN-014 | period not already Hard Closed before reopen attempts |
| QR-FIN-041 | AGGREGATE | API-FIN-027 | ENT-FIN-004, ENT-FIN-005 | year-end | compute closing balances, build closing + opening entries |
| QR-FIN-042 | FIND_BY_CRITERIA | API-FIN-028 | ENT-FIN-005 | report | account ledger — POSTED lines for one account, oldest first; the running balance is accumulated by the service, deliberately not returned by the query |
| QR-FIN-043 | AGGREGATE | API-FIN-029, API-FIN-030, API-FIN-031 | ENT-FIN-005 | report | trial balance / balance sheet / income statement account balances (shared aggregation, filtered per report by accountTypeCode) |
| QR-FIN-044 | AGGREGATE | API-FIN-032 | ENT-FIN-005, ENT-FIN-006 | report | dimension report (account × dimension value) |
| QR-FIN-045 | FIND_ONE | API-FIN-027 | ENT-FIN-001 | year-end | the single Retained Earnings account (DBF-FIN-147), lowest pk first |
| QR-FIN-046 | EXISTS | API-FIN-006 | ENT-FIN-002 | uniqueness | dimension code unique |
| QR-FIN-047 | EXISTS | API-FIN-023 | ENT-FIN-007 | uniqueness | fiscal year code unique |
| QR-FIN-048 | FIND_ONE | API-FIN-027 | ENT-FIN-007 | year-end | the next fiscal year, found by its startDate = this year's endDate + 1 day (the opening entry's target) |
| QR-FIN-049 | FIND_BY_CRITERIA | API-FIN-023, API-FIN-027, API-FIN-014 | ENT-FIN-008 | read | every period of one fiscal year, JOIN FETCH on the year, ordered by periodNo |

Join governance: every posting-pipeline QR (024, 025, 028-033) is intra-module only
(FIN_JOURNAL_ENTRY/LINE/LINE_DIM/ACCOUNT/FISCAL_PERIOD, all owned here); the one
cross-module read (QR for lookup-code validation, folded into QR-FIN-002/013/015/024/025/
etc.'s "Validations" step, per XM-FIN-001) is a separate in-process `MdlLookupApi` call,
never a SQL join. No
QR joins to resolve a lookup label — every lookup-backed column returns its code; the
frontend resolves the display label via MDL.

---

<!-- PHASE:CORE:START traces=REQ-FIN-017 -->
## PHASE 1 — CORE

**Layers**: controller → service → mapper → domain → repository (`profile.stack.backend.layers`).
Domain-behaviour placement: **domain classes** — one dedicated `<Entity>Domain` per entity —
for every rule that answers "is this operation allowed?"
(`profile.conventions.domain_behaviour_placement: domain_classes`). The service layer is
never a placement: it orchestrates only (load → delegate → persist → return) and holds no
business-rule conditional of its own. How many entities or tables a rule reads is NOT a
placement criterion — the service fetches those facts and passes them into the domain class
as plain arguments, so a multi-entity rule sits in exactly the same place as a single-entity
one. The decision moves to the domain class while the entity keeps the plain state mutation:
`JournalEntryDomain.assertCanPost(...)` then `JournalEntry.post()`;
`FiscalPeriodDomain.assertCanHardClose(...)` then `FiscalPeriod.hardClose()`. FIN domain
classes: `AccountDomain` (RULE-FIN-001, 007), `DimensionValueDomain` (RULE-FIN-002, 009),
`EventTypeRuleDomain` (RULE-FIN-003, 005, 010), `JournalEntryDomain` (RULE-FIN-004, 006,
008, 011, 012, 013, 016), `FiscalPeriodDomain` (RULE-FIN-014, 015), `AllocationRuleDomain`
(RULE-FIN-003, 010 as they apply to allocation targets).

**Error signalling**: `LocalizedException → {code, messageAr, messageEn}`; runtime code
format `FIN-{http}[-{SLUG}]`.

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

**Numbering**: `docNo` format is `JV-{fiscalYearCode}-{NNNNNN}` — literal prefix `JV-`, the
owning fiscal year's `code` (DBF-FIN-066, VARCHAR(10)), `-`, then a zero-padded 6-digit
counter starting at `000001`; e.g. `JV-2026-000123` (worst case 20 chars, inside
`doc_no VARCHAR(30)`). The counter is scoped per `fiscalYearId` and restarts at `000001`
for each new fiscal year — one counter for all journal types, never segmented by
`journalTypeCode`; `UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO (fiscal_year_id, doc_no)` backs the
uniqueness guarantee at the database level. Generated by a FIN-local generator in
`com.erp.fin`, deliberately NOT a shared `com.erp.common` component: no other module needs
document numbering today, so a general shared interface would be speculative — promote it
to `common` only if and when a second real consumer appears. This is a conscious, recorded
deviation from the profile's standing guidance that numbering "comes from the platform
numbering engine; never generated in a module" — that guidance presumes an engine which
does not exist in this repo, making literal compliance impossible. Assigned once on create,
immutable thereafter — excluded entirely from every create/update request DTO, present
only in responses.

**Workflow engine**: forbidden — every lifecycle below (JournalEntry, FiscalPeriod) is a
plain guarded transition, never a workflow definition.

**Languages**: every name field and catalog message present in ar + en.

**Cross-module contract placement**: XM-FIN-001 (SOFT-READ → MDL) is implemented in FIN's
service layer by injecting MDL's published cross-module interface
`com.erp.mdl.crossmodule.MdlLookupApi` directly — in-process Spring interface injection
within the single deployable, never a loopback HTTP call to API-MDL-011. FIN calls
`readActiveValuesByKey(String typeKey)` and consumes the narrow read-model record
`com.erp.mdl.crossmodule.LookupOptionView` (code, labelAr, labelEn, sortOrder) — never a
`LookupValue` entity or an MDL-internal DTO; a submitted code is validated by membership in
that returned list. Same pattern as the delivered `NotificationLookupService` and
`FileLookupService`. FIN's own dependency on SEC for identity/authorization uses the identical
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
FIELDS: DBF-FIN-001..013 + DBF-FIN-147 (`isRetainedEarningsFl`, REQ-FIN-036 — see API-FIN-027) — see DB Alignment Manifest; `accountTypeCode`/`natureCode` are
lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request excludes {accountPk, isActiveFl, audit}; update-request
excludes {accountPk, code, isActiveFl, audit} (code immutable, matching MDL's own `key`
precedent); response includes all.
LOOKUP FIELDS: `accountTypeCode`→`ACCOUNT_TYPE`, `natureCode`→`DEBIT_CREDIT`, both validated
in the service layer via injected `MdlLookupApi.readActiveValuesByKey(<key>)` (XM-FIN-001) —
stored as code, never a numeric FK.
DOMAIN RULES: **RULE-FIN-001** (full text: srs-fin.md §A5) — Scope ENT-FIN-001 · Trigger:
on update (`isLeafFl`) · DB enforcement: application layer (QR-FIN-006) · owner layer:
service.
STATE MACHINE: `isActiveFl` binary only — not applicable.
CROSS-MODULE: `accountTypeCode`/`natureCode` touch XM-FIN-001.
REPOSITORY OPS → QR-FIN-001, QR-FIN-002, QR-FIN-003, QR-FIN-004, QR-FIN-005, QR-FIN-006,
QR-FIN-045 (FIND_ONE the Retained Earnings account, DBF-FIN-147 — API-FIN-027).

#### ENT-FIN-007 — FiscalYear      kind: master
BINDINGS: table `FIN_FISCAL_YEAR` · PK `fiscalYearPk` (DBF-FIN-065) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-065..074 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: create-request `{code, startDate, endDate, periodCount}` (periodCount is a
transient input driving REQ-FIN-031's period-generation, not a persisted column); response
includes all persisted fields plus the generated periods.
DOMAIN RULES: **a CLOSED year is never closed again** — the year-end close's own re-run
guard, scoped to `statusCode` alone and therefore owned by `FiscalYearDomain` (ALIGN-BE;
`FIN-409-INVALID-TRANSITION`, reusing the catalog's existing invalid-transition row). Amends
this block's earlier "none scoped alone": the rest of year-end close (REQ-FIN-036) is still
orchestrated at the API layer over both FiscalYear and FiscalPeriod — see API-FIN-027 — and
this remains the entity's ONLY Domain object (A.0.7).
STATE MACHINE: `statusCode` (FISCAL_YEAR_STATUS) — OPEN→CLOSED, set once by REQ-FIN-036 —
binary, not applicable for a diagram (SRS A7).
CROSS-MODULE: `statusCode` touches XM-FIN-001.
REPOSITORY OPS → QR-FIN-038 (SAVE, with periods), QR-FIN-041 (AGGREGATE, year-end),
QR-FIN-047 (EXISTS, code unique), QR-FIN-048 (FIND_ONE, next year by startDate).

#### ENT-FIN-008 — FiscalPeriod      kind: master
BINDINGS: table `FIN_FISCAL_PERIOD` · PK `fiscalPeriodPk` (DBF-FIN-075) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: none
FIELDS: DBF-FIN-075..088 — see DB Alignment Manifest; `statusCode` lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: no direct create (generated with the year, REQ-FIN-031); transition
endpoints only (open/soft-close/hard-close) take just `{id}`; response includes all.
DOMAIN RULES:
**RULE-FIN-008** (srs-fin.md §A5) — period-open-at-post-time, except the year-end closing and
opening entries, which the rule itself exempts (REQ-FIN-036 / API-FIN-027) — DB enforcement:
application layer (QR-FIN-031) · owner layer: service.
**RULE-FIN-014** (srs-fin.md §A5) — reject reopening a Hard Closed period — DB enforcement:
application layer (QR-FIN-040) · owner layer: service.
**RULE-FIN-015** (srs-fin.md §A5) — close-approval permission distinct from entry-creation
permission — DB enforcement: application layer (service, reading SEC role/grant data,
Phase 1 CORE) · owner layer: service.
STATE MACHINE: `statusCode` (PERIOD_STATE) per SRS A7 — OPEN⇄SOFT_CLOSE→HARD_CLOSE→YEAR_END_CLOSE.
CROSS-MODULE: `statusCode` touches XM-FIN-001; the SoD check (RULE-FIN-015) reads SEC role
data (not a formal XM row — platform-standard integration, ADR-FIN-001).
REPOSITORY OPS → QR-FIN-038 (SAVE, with year), QR-FIN-039 (UPDATE, transitions), QR-FIN-040 (EXISTS),
QR-FIN-049 (FIND_BY_CRITERIA, every period of one year).
<!-- SUB:DATA-DOM-MASTER:END -->

<!-- SUB:DATA-DOM-TRANSACTIONAL:START traces=REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028 -->
### SUB — DATA-DOM-TRANSACTIONAL

#### ENT-FIN-004 — JournalEntry      kind: transactional
BINDINGS: table `FIN_JOURNAL_ENTRY` · PK `journalEntryPk` (DBF-FIN-034) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: **docNo** · column `doc_no` (DBF-FIN-035) · format:
`JV-{fiscalYearCode}-{NNNNNN}` (e.g. `JV-2026-000123`), counter scoped per `fiscalYearId`
and restarting at `000001` each fiscal year, single counter across all journal types
(`UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO`) · generation source: a FIN-local generator in
`com.erp.fin` (not `com.erp.common` — see CORE Numbering), invoked at create, before the
first save — excluded from every create/update request body, always present in responses.
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
**RULE-FIN-008** — period open at post, except the year-end closing/opening entries the rule
itself exempts (REQ-FIN-036 / API-FIN-027) — QR-FIN-031 — service (POL-FIN-004).
**RULE-FIN-011** — reversal exact and linked — QR-FIN-034 — service (POL-FIN-007).
**RULE-FIN-012** — reversal posts to current period if original's closed — QR-FIN-036 — service.
**RULE-FIN-013** — reject reverse of non-POSTED, and reject reversing an entry that already
carries a reversal link (double-reversal) — QR-FIN-035 — service.
**RULE-FIN-016** — lock after posting — enforced by omission (no UPDATE/DELETE mapping on
a POSTED row in the repository layer at all) — service/repository.
**RULE-FIN-017** — the submitted fiscalYearId, periodId and docDate must describe one
accounting context (the period belongs to that year, DBF-FIN-076; the date falls inside the
period, DBF-FIN-080/081) — API-FIN-019 only, since every system-generated entry derives the
three from one another — `JournalEntryDomain.assertHeaderCoherent(...)` (ALIGN-BE;
`FIN-400-PERIOD-NOT-IN-YEAR`, `FIN-400-DOCDATE-OUTSIDE-PERIOD`).
**RULE-FIN-013's second half under concurrency** — the "already reversed" read-then-write is
made atomic by a PESSIMISTIC_WRITE load of the original's header before the guard runs
(ALIGN-BE); no FIN entity carries `@Version`, so without it two concurrent reversals both
post a mirror.
(Full text of every RULE above: srs-fin.md §A5 — not restated here per the single-source rule.)
STATE MACHINE: `statusCode` (JOURNAL_STATUS) per SRS A7 — DRAFT→POSTED (RULE-FIN-016 locks
immediately); POSTED is terminal. Classic reversal (RULE-FIN-011): reversing an entry leaves the
original POSTED and posts an equal, opposite mirror entry, the two linked through
`originalEntryId`/`reversalEntryId` (DBF-FIN-042/043) — net ledger effect zero. No path sets VOID.
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
RULES: none scoped alone. REPOSITORY OPS → QR-FIN-007, QR-FIN-008, QR-FIN-046 (EXISTS, code unique).

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
**RULE-FIN-003** (exactly one remainder line whenever the line set is a compound or
percentage distribution — any sibling PERCENTAGE-distributed, or any line already marked
remainder — plus marker agreement: `isRemainderFl` (DBF-FIN-103) is the SINGLE remainder
marker, the one both this guard and the API-FIN-020 builder read, and must agree with the
line's own REMAINDER type code, `FIN-422-REMAINDER-MARKER`) — QR-FIN-016 —
`EventTypeRuleDomain`. REPOSITORY OPS → QR-FIN-015, QR-FIN-016; read as part of QR-FIN-025/028 at
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
**RULE-FIN-003** (reused — exactly one remainder target whenever the target set is a
compound or percentage distribution, plus marker agreement between `isRemainderFl`
(DBF-FIN-141, the SINGLE marker the API-FIN-017 builder reads) and `distributionTypeCode`,
`FIN-422-REMAINDER-MARKER`) — QR-FIN-016 (reused) — `AllocationRuleDomain`. REPOSITORY OPS → written with QR-FIN-021; read by
QR-FIN-022 at run time.
<!-- SUB:DATA-DOM-LOOKUP:END -->
<!-- PHASE:DATA-DOM:END -->

<!-- PHASE:SVC-API:START traces=REQ-FIN-001,REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028,REQ-FIN-036 -->
## PHASE 3 — SVC-API

API count = 32 ≥ 8 → split by threshold, grouped CRUD / SEARCH / INT.

<!-- SUB:SVC-API-SEARCH:START traces=REQ-FIN-001,REQ-FIN-004,REQ-FIN-007,REQ-FIN-022,REQ-FIN-027,REQ-FIN-031,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-043 -->
### SUB — SVC-API-SEARCH (read-only)

<!-- API:API-FIN-001:START traces=REQ-FIN-001,DBF-FIN-002,DBF-FIN-003,DBF-FIN-004,DBF-FIN-005 -->
### API-FIN-001 — search accounts
Endpoint: POST /api/v1/fin/accounts/search · Layers: `AccountController.search`→`AccountService.search`
Request: body `AccountSearchRequest` — `code`(LIKE), `nameAr/nameEn`(LIKE), `accountTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AccountResponse>` · `ApiResponse<...>`
Validations: none (read-only) · Errors: `FIN-500`
Orchestration: load (QR-FIN-001) → map → return · Repository: QR-FIN-001 · join NONE · READ_ONLY
Security: screen FIN_ACCOUNTS · `PERM_FIN_ACCOUNTS_VIEW` · Localization: nameAr/nameEn returned
<!-- API:API-FIN-001:END -->

<!-- API:API-FIN-005:START traces=REQ-FIN-004,DBF-FIN-015,DBF-FIN-016,DBF-FIN-017 -->
### API-FIN-005 — search dimensions
Endpoint: POST /api/v1/fin/dimensions/search · Layers: `DimensionController.search`→`DimensionService.search`
Request: body `DimensionSearchRequest` — `code`(LIKE), paging · Response: 200 · `Page<DimensionResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-007 → map → return · Repository: QR-FIN-007 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-005:END -->

<!-- API:API-FIN-008:START traces=REQ-FIN-005,DBF-FIN-024,DBF-FIN-025,DBF-FIN-026,DBF-FIN-027 -->
### API-FIN-008 — search dimension values
Endpoint: POST /api/v1/fin/dimensions/values/search · Layers: `DimensionController.searchDimensionValues`→`DimensionValueService.search`
Request: body `DimensionValueSearchRequest` — `dimensionId`(EXACT, required) carried in the body filters and read by the child parent-id extractor (never a path variable); `code`(LIKE), paging · Response: 200 · `Page<DimensionValueResponse>`
Validations: none · Errors: `FIN-404-DIMENSION`
Orchestration: QR-FIN-011 → map → return · Repository: QR-FIN-011 · join NONE · READ_ONLY
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-008:END -->

<!-- API:API-FIN-009:START traces=REQ-FIN-007,DBF-FIN-090,DBF-FIN-091,DBF-FIN-092 -->
### API-FIN-009 — search event-type rules
Endpoint: POST /api/v1/fin/event-rules/search · Layers: `EventTypeRuleController.search`→`EventTypeRuleService.search`
Request: body `EventTypeRuleSearchRequest` — `eventTypeCode`(EXACT), `isActiveFl`(EXACT), paging · Response: 200 · `Page<EventTypeRuleResponse>`
Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-012 → map → return · Repository: QR-FIN-012 · join NONE · READ_ONLY
Security: screen FIN_RULES · `PERM_FIN_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-009:END -->

<!-- API:API-FIN-012:START traces=REQ-FIN-022,DBF-FIN-110,DBF-FIN-111,DBF-FIN-112 -->
### API-FIN-012 — search templates
Endpoint: POST /api/v1/fin/recurring-templates/search · Layers: `RecurringTemplateController.search`→`RecurringTemplateService.search`
Request: body `RecurringTemplateSearchRequest` — `nameAr/nameEn`(LIKE), `scheduleTypeCode`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<RecurringTemplateResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-017 → map → return · Repository: QR-FIN-017 · join NONE · READ_ONLY
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-012:END -->

<!-- API:API-FIN-015:START traces=REQ-FIN-025,DBF-FIN-131,DBF-FIN-132,DBF-FIN-133 -->
### API-FIN-015 — search allocation rules
Endpoint: POST /api/v1/fin/allocation-rules/search · Layers: `AllocationRuleController.search`→`AllocationRuleService.search`
Request: body `AllocationRuleSearchRequest` — `nameAr/nameEn`(LIKE), `sourceAccountId`(EXACT), `isActiveFl`(EXACT), paging
Response: 200 · `Page<AllocationRuleResponse>` · Validations: none · Errors: `FIN-500`
Orchestration: QR-FIN-020 → map → return · Repository: QR-FIN-020 · join NONE · READ_ONLY
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_VIEW` · Localization: nameAr/nameEn
<!-- API:API-FIN-015:END -->

<!-- API:API-FIN-018:START traces=REQ-FIN-027,DBF-FIN-035,DBF-FIN-036,DBF-FIN-040 -->
### API-FIN-018 — search journal entries
Endpoint: POST /api/v1/fin/journal-entries/search · Layers: `JournalEntryController.search`→`JournalEntryService.search`
Request: body `JournalEntrySearchRequest` — `docNo`(LIKE), `docDate`(DATE_RANGE), `periodId`(EXACT), `statusCode`(EXACT), `journalTypeCode`(EXACT), paging
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
Validations: RULE-FIN-006 restated as a report-level guarantee (POL-FIN-008: the sums always match because every contributing entry individually balanced — no separate check needed, an invariant by construction). `periodId` is an OPTIONAL narrowing, validated ONLY when supplied: omitting it means "no period narrowing" and stays a 200 (AC-FIN-040's happy path) — it is NOT mandatory
Errors: `FIN-404-PERIOD` (supplied `periodId` does not resolve), `FIN-500`
Orchestration: QR-FIN-043 (POSTED lines only, live, grouped by account) → apply nature sign → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_TRIAL_BALANCE · `PERM_FIN_TRIAL_BALANCE_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-029:END -->

<!-- API:API-FIN-030:START traces=REQ-FIN-041,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-030 — balance sheet
Endpoint: GET /api/v1/fin/reports/balance-sheet · Layers: `ReportController.balanceSheet`→`ReportService.balanceSheet`
Request: `fiscalYearId`(EXACT), `asOfDate` · Response: 200 · grouped ASSET/LIABILITY/EQUITY balances
Validations: none (continuity itself is guaranteed by REQ-FIN-036's opening-entry generation, not re-validated at read time). The REQUIRED `fiscalYearId` is resolved FIRST, before any aggregation
Errors: `FIN-404-YEAR` (unknown `fiscalYearId` — previously a silent 200 carrying an all-zero statement), `FIN-500`
Orchestration: QR-FIN-043 (accountTypeCode IN ASSET,LIABILITY,EQUITY) → group → return
Repository: QR-FIN-043 · join intra-module · READ_ONLY
Security: screen FIN_BALANCE_SHEET · `PERM_FIN_BALANCE_SHEET_VIEW` · Localization: nameAr/nameEn per account
<!-- API:API-FIN-030:END -->

<!-- API:API-FIN-031:START traces=REQ-FIN-042,REQ-FIN-046,DBF-FIN-005,DBF-FIN-055 -->
### API-FIN-031 — income statement
Endpoint: GET /api/v1/fin/reports/income-statement · Layers: `ReportController.incomeStatement`→`ReportService.incomeStatement`
Request: `fiscalYearId`(EXACT), period range · Response: 200 · grouped REVENUE/EXPENSE balances
Validations: none (zero-opening is guaranteed by REQ-FIN-036 closing result accounts to Retained Earnings, not re-validated at read time). The REQUIRED `fiscalYearId` is resolved FIRST; the two OPTIONAL period bounds `fromPeriodId`/`toPeriodId` are validated only when supplied, as they already were
Errors: `FIN-404-YEAR` (unknown `fiscalYearId`), `FIN-404-PERIOD` (supplied period bound does not resolve — unchanged), `FIN-500`
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

<!-- API:API-FIN-033:START traces=REQ-FIN-031,DBF-FIN-076,DBF-FIN-077,DBF-FIN-080,DBF-FIN-081,DBF-FIN-082 -->
### API-FIN-033 — search fiscal periods
Endpoint: POST /api/v1/fin/fiscal-periods/search · Layers: `FiscalPeriodController.search`→`FiscalPeriodService.search`
Request: body `FiscalPeriodSearchRequest` — `fiscalYearId`(EXACT, **OPTIONAL**, DBF-FIN-076) carried in the body filters and read by the child parent-id extractor (never a path variable); `statusCode`(EXACT, DBF-FIN-082), paging/sort · Response: 200 · `Page<FiscalPeriodResponse>`
Validations: none (read-only) · Errors: `FIN-400-INVALID-SORT`, `FIN-500`
Orchestration: build the generic specification from the remaining filters → AND in an explicit join predicate on `fiscalYear.fiscalYearPk` ONLY when `fiscalYearId` is present → page → map → return
Repository: `FiscalPeriodRepository` via `JpaSpecificationExecutor.findAll(Specification, Pageable)` — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join intra-module (period→year, only when the parent filter is supplied) · READ_ONLY
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_VIEW` · Localization: nameAr/nameEn per period
Parent id OPTIONAL — deliberate divergence from API-FIN-008, which rejects a missing `dimensionId` with `FIN-404-DIMENSION`. SCR-REQ-FIN-007 §B2 makes both filters EXACT but neither mandatory, and the endpoint exists precisely so a client that did NOT create the fiscal year in the same session can discover a period id: requiring the year id first would leave that client with no way in. Same shape API-FIN-018 already uses for its optional `periodId`.
Why it exists: `JournalEntryCreateRequest` requires `fiscalYearId` + `periodId` (API-FIN-019) and API-FIN-029/030/031 require a period or year id, yet before this endpoint no API returned a fiscal period except API-FIN-023's create response. `PERM_FIN_PERIODS_VIEW` was already a V24 registry row and already granted by V25/V27, so **no migration was needed** — only the matching `PermissionConstants` constant was added.
<!-- API:API-FIN-033:END -->

**404 on a keying id, as built (API-FIN-029/030/031).** FIN's house style already 404s on the id
that keys a report — API-FIN-028 answers `FIN-404-ACCOUNT`, API-FIN-032 answers
`FIN-404-DIMENSION`. API-FIN-030 and API-FIN-031 now do the same for their REQUIRED `fiscalYearId`
(`FIN-404-YEAR`), and API-FIN-029 for its `periodId` when — and only when — one is supplied
(`FIN-404-PERIOD`). API-FIN-031 was internally contradictory before: 404 on an unknown period bound
and 200 on an unknown year, in the same request. No new error code was introduced; both codes were
already registered in `FinErrorCodes` and both i18n bundles.
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
Endpoint: PUT /api/v1/fin/accounts/{id}/deactivate · Layers: `AccountController.deactivate`→`AccountService.deactivate`
Request: path `id`, no body · Response: 200 · `AccountResponse` (isActiveFl=false)
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
Endpoint: POST /api/v1/fin/dimensions/{id}/values · Layers: `DimensionController.createDimensionValue`→`DimensionValueService.create`
Request: path `id` (dimensionId); body `{code, nameAr, nameEn, sortOrder}`
Response: 201 · `DimensionValueResponse`
Validations: RULE-FIN-002 (full text: DATA-DOM §ENT-FIN-003) — code unique within the
dimension (QR-FIN-010)
Errors: `FIN-409-DIMVALUE-DUP`, `FIN-404-DIMENSION`
Orchestration: validate dimension exists → check RULE-FIN-002 (QR-FIN-010) → persist (QR-FIN-009) → return
Repository: QR-FIN-009, QR-FIN-010 · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-007:END -->

<!-- API:API-FIN-035:START traces=REQ-FIN-005,REQ-FIN-021,DBF-FIN-029 -->
### API-FIN-035 — deactivate dimension value
Endpoint: PUT /api/v1/fin/dimensions/values/{id}/deactivate · Layers: `DimensionController.deactivateDimensionValue`→`DimensionValueService.deactivate`
Request: path `id` (dimensionValuePk), no body · Response: 200 · `DimensionValueResponse` (isActiveFl=false)
Validations: none beyond existence · Errors: `FIN-404-DIMVALUE`
Orchestration: load → `DimensionValue.deactivate()` (the entity's own helper, never a direct field assignment) → persist → return. Effect: `DimensionValueDomain.checkUsableOnLine` reads exactly this flag (DBF-FIN-029), so every posting path citing the value afterwards answers `FIN-409-INVALID-DIMENSION` (RULE-FIN-009 / REQ-FIN-021, via API-FIN-019, 020, 014, 017)
Repository: `DimensionValueRepository.findById` + `save` — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_DIMENSIONS · `PERM_FIN_DIMENSIONS_UPDATE` · Localization: n/a
New in this delivery: `FIN-404-DIMVALUE` (`FinErrorCodes.FIN_404_DIMVALUE`, added to BOTH i18n bundles) and `PERM_FIN_DIMENSIONS_UPDATE`. This is the first UPDATE-class endpoint on FIN_DIMENSIONS, so migration `V28__fin_dimensions_update_action.sql` registers the `FIN_DIMENSIONS / UPDATE` action row AND explicitly grants it to `SYS_ADMIN` — V25 grants by a `SELECT` over the registry and has already run, so a later row would otherwise be registered-but-ungrantable.
Why it exists: RULE-FIN-009 / REQ-FIN-021 reject a journal line citing an INACTIVE dimension value and `DimensionValueDomain` implements that check, but nothing could set the flag false, so the branch was unreachable and untestable. Deliberately NOT built (a decision, not a backlog item): a deactivate on the PARENT `Dimension` — no REQ/AC/RULE requires one and `Dimension.isActiveFl` (DBF-FIN-018) drives no behaviour. No `activate` counterpart either, matching the delivered `AccountService.deactivate` precedent.
<!-- API:API-FIN-035:END -->

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
Endpoint: POST /api/v1/fin/event-rules/{id}/lines · Layers: `EventTypeRuleController.createRuleLine`→`RuleLineService.create`
Request: path `id` (eventTypeRuleId); body `{accountDerivationTypeCode, accountDerivationValue,
amountSourceTypeCode, amountSourceValue?, directionCode, distributionTypeCode, isRemainderFl}`
Response: 201 · `RuleLineResponse`
Validations: RULE-FIN-003 (full text: DATA-DOM §ENT-FIN-010) — exactly one remainder line
once the line set is a compound or percentage distribution, i.e. any sibling line is
PERCENTAGE-distributed OR any line is already marked remainder (QR-FIN-016); and each line's
`isRemainderFl` marker (DBF-FIN-103) must agree with its own REMAINDER type code, since that
marker is the single one the API-FIN-020 builder reads; all four lookup codes validated via
XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-422-REMAINDER-MARKER`, `FIN-404-RULE`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate lookups → check RULE-FIN-003 across the rule's existing + new line
(QR-FIN-016) → persist (QR-FIN-015) → return
Repository: QR-FIN-015, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-011:END -->

<!-- API:API-FIN-034:START traces=REQ-FIN-007,DBF-FIN-093 -->
### API-FIN-034 — deactivate event-type rule
Endpoint: PUT /api/v1/fin/event-rules/{id}/deactivate · Layers: `EventTypeRuleController.deactivate`→`EventTypeRuleService.deactivate`
Request: path `id`, no body · Response: 200 · `EventTypeRuleResponse` (isActiveFl=false)
Validations: none beyond existence · Errors: `FIN-404-RULE`
Orchestration: load → clear the active flag (DBF-FIN-093) → persist → return
Repository: `EventTypeRuleRepository.findById` + `save` — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_RULES · `PERM_FIN_RULES_UPDATE` (pre-existing — no new constant, no migration) · Localization: n/a
Why it exists: until this endpoint landed no rule could ever be retired, so `FIN-404-NO-ACTIVE-RULE` (RULE-FIN-005, API-FIN-020) was unreachable. **Stated limitation**, recorded in the service's own javadoc: deactivating does NOT free the event type for a replacement rule, because `EventTypeRuleService.create` guards uniqueness with `existsByEventTypeCode`, which is not scoped to the active flag. No `activate` counterpart, and no rule-line delete — ENT-FIN-010 carries no active-flag column and FIN publishes no `DELETE` endpoint on any screen (a deliberate v1 exclusion, see srs-fin.md SCR-REQ-FIN-003 §B4).
<!-- API:API-FIN-034:END -->

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

<!-- API:API-FIN-036:START traces=REQ-FIN-022,DBF-FIN-117 -->
### API-FIN-036 — deactivate template
Endpoint: PUT /api/v1/fin/recurring-templates/{id}/deactivate · Layers: `RecurringTemplateController.deactivate`→`RecurringTemplateService.deactivate`
Request: path `id`, no body · Response: 200 · `RecurringTemplateResponse` (isActiveFl=false)
Validations: none beyond existence · Errors: `FIN-404-TEMPLATE`
Orchestration: load → `RecurringTemplate.deactivate()` (the entity's own helper, never a direct field assignment) → persist → re-read the template's lines and hand them to the mapper → return. The line re-read is not decoration: `RecurringTemplateResponse.lineCount` is derived from the list the mapper is handed, so passing an empty list would misreport the aggregate as having no lines. It is orchestration (load → map), not a rule.
Repository: `RecurringTemplateRepository.findById` + `save`, plus `RecurringTemplateLineRepository.findByRecurringTemplatePk` for the response's lines — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_UPDATE` (pre-existing — V24 seeds the `FIN_RECURRING_TEMPLATES / UPDATE` action row and V25's blanket Tier-3 grant already covers it, so no new constant, no new error code and no migration) · Localization: n/a
**DEFECT CLOSED 2026-09-12 — deactivate now DOES stop the run.** This paragraph used to report an OPEN DEFECT: `RecurringTemplateService.run` (API-FIN-014) ignored `isActiveFl`, so a deactivated template still ran and still posted. That is no longer true. `RecurringTemplateDomain.assertCanRun()` — a NEW Domain companion for ENT-FIN-011 — is called by `RecurringTemplateService.run` immediately after the row is loaded and before anything else is resolved, and refuses a deactivated template with `FIN-409-NOT-ACTIVE` (`Status.CONFLICT` → HTTP 409; ar "هذا التعريف غير نشط ولا يمكن تشغيله", en "This definition is deactivated and cannot be run"). The screen's 404 was deliberately not reused: the template does exist. **This gate is a RECORDED HUMAN DECISION, not spec.** No RULE-FIN-* states it, and AC-FIN-023 is written "Given an active recurring template" without stating any outcome for an inactive one — a later reader must not mistake the gate for a requirement that was always there. What remains OPEN on this screen is only that a template cannot be UPDATED after creation (next paragraph). Recorded identically at srs-fin.md SCR-REQ-FIN-004 §B4 and §"Access summary".
Why it exists: srs-fin.md SCR-REQ-FIN-004 §B4 recorded the absence of a template deactivate as an OPEN DEFECT rather than a scope decision — `IS_ACTIVE_FL` is NOT NULL, the entity's `activate()`/`deactivate()` shipped with zero callers, B2 advertises an `isActiveFl(EXACT)` filter over a column nothing could set to FALSE, and AC-FIN-023 is written "Given an active recurring template", presupposing a state nothing could produce. Deliberately NOT built, and NOT taken by this endpoint: a template `update` — a correct update must decide the fate of the template's existing child lines, which is a design question no REQ, AC or RULE answers, so it remains the still-open half of the same gap. No `activate` counterpart either; FIN ships none for any entity.
<!-- API:API-FIN-036:END -->

<!-- API:API-FIN-016:START traces=REQ-FIN-025,DBF-FIN-133,DBF-FIN-142,DBF-FIN-144 -->
### API-FIN-016 — create allocation rule
Endpoint: POST /api/v1/fin/allocation-rules · Layers: `AllocationRuleController.create`→`AllocationRuleService.create`
Request: `{nameAr, nameEn, sourceAccountId, targets: [...]}`
Response: 201 · `AllocationRuleResponse`
Validations: RULE-FIN-003 (reused) — exactly one remainder target when any sibling is
PERCENTAGE or any target is already marked remainder (QR-FIN-016, reused), and each target's
`isRemainderFl` (DBF-FIN-141) must agree with its own `distributionTypeCode`;
distributionTypeCode validated via XM-FIN-001
Errors: `FIN-409-REMAINDER-COUNT`, `FIN-422-REMAINDER-MARKER`, `FIN-404-ACCOUNT`, `FIN-400-INVALID-LOOKUP`
Orchestration: validate → check RULE-FIN-003 across targets (QR-FIN-016) → persist rule+targets (QR-FIN-021) → return
Repository: QR-FIN-021, QR-FIN-016 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_CREATE` · Localization: nameAr/nameEn required
<!-- API:API-FIN-016:END -->

<!-- API:API-FIN-037:START traces=REQ-FIN-025,DBF-FIN-134 -->
### API-FIN-037 — deactivate allocation rule
Endpoint: PUT /api/v1/fin/allocation-rules/{id}/deactivate · Layers: `AllocationRuleController.deactivate`→`AllocationRuleService.deactivate`
Request: path `id`, no body · Response: 200 · `AllocationRuleResponse` (isActiveFl=false)
Validations: none beyond existence — RULE-FIN-003, the one rule `AllocationRuleDomain` owns, governs the remainder-target SET at create and run time and says nothing about the active flag · Errors: `FIN-404-ALLOCATION-RULE`
Orchestration: load → `AllocationRule.deactivate()` (the entity's own helper, never a direct field assignment) → persist → re-read the rule's targets and hand them to the mapper → return. The target re-read is not decoration: `AllocationRuleResponse.targetCount` is derived from the list the mapper is handed, so passing an empty list would misreport the aggregate as having no targets. It is orchestration (load → map), not a rule.
Repository: `AllocationRuleRepository.findById` + `save`, plus `AllocationTargetRepository.findByAllocationRulePk` for the response's targets — no QR id is assigned; the Query Reference Catalog closes at QR-FIN-049 and extending it is a catalog-level change left to ALIGN · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_UPDATE` (pre-existing — V24 seeds the `FIN_ALLOCATION_RULES / UPDATE` action row and V25's blanket Tier-3 grant already covers it, so no new constant, no new error code and no migration) · Localization: n/a
**DEFECT CLOSED 2026-09-12 — deactivate now DOES stop the run.** This paragraph used to report an OPEN DEFECT: `AllocationRuleService.run` (API-FIN-017) ignored `isActiveFl`, so a deactivated rule still ran and still posted, and `AllocationRuleDomain.isActive()` had no caller. That is no longer true. `AllocationRuleDomain.assertCanRun()` is called by `AllocationRuleService.run` immediately after the row is loaded and before the target set is even fetched, and refuses a deactivated rule with `FIN-409-NOT-ACTIVE` (`Status.CONFLICT` → HTTP 409; ar "هذا التعريف غير نشط ولا يمكن تشغيله", en "This definition is deactivated and cannot be run"). The screen's 404 was deliberately not reused: the rule does exist. **This gate is a RECORDED HUMAN DECISION, not spec** — no RULE-FIN-* states it, and a later reader must not mistake it for a requirement that was always there. What remains OPEN on this screen is only that a rule cannot be UPDATED after creation (next paragraph). Recorded identically at srs-fin.md SCR-REQ-FIN-005 §B4 and §"Access summary".
Why it exists: srs-fin.md SCR-REQ-FIN-005 §B4 recorded the absence of a rule deactivate as an OPEN DEFECT rather than a scope decision — `IS_ACTIVE_FL` is NOT NULL, the entity's `activate()`/`deactivate()` shipped with zero callers, `AllocationRuleDomain.isActive()` was dead code, and B2 advertises an `isActiveFl(EXACT)` filter over a column nothing could set to FALSE. Deliberately NOT built, and NOT taken by this endpoint: a rule `update` — a correct update must decide the fate of the rule's existing targets (and therefore of RULE-FIN-003's remainder-target set), which is a design question no REQ, AC or RULE answers, so it remains the still-open half of the same gap. No `activate` counterpart either; FIN ships none for any entity.
<!-- API:API-FIN-037:END -->

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
QR-FIN-032) — every failure returned together (REQ-FIN-015), nothing posts if any fails.
RULE-FIN-017 (header coherence) runs FIRST and fail-fast: the submitted `periodId` must
belong to the submitted `fiscalYearId` (DBF-FIN-076) and `docDate` must fall inside that
period's [startDate, endDate] (DBF-FIN-080/081) — an incoherent triple makes RULE-FIN-008's
own period gate meaningless, lets the entry take a docNo from the wrong year's series, and
corrupts every period-scoped report and the year-end close. This is the only API that needs
it: every system-generated entry derives the three facts from one another
Errors: `FIN-400-PERIOD-NOT-IN-YEAR`, `FIN-400-DOCDATE-OUTSIDE-PERIOD`, `FIN-409-UNBALANCED`,
`FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`, `FIN-409-INVALID-DIMENSION`
Orchestration: resolve fiscal year UNDER A ROW LOCK (`SELECT ... FOR UPDATE` on
FIN_FISCAL_YEAR, the docNo series' allocation lock) → resolve period → check RULE-FIN-017 →
generate docNo (FIN-local generator, `JV-{fiscalYearCode}-{NNNNNN}`) → build DRAFT (QR-FIN-024) → validate
(QR-FIN-029..032) → on success: post (QR-FIN-033); on failure: discard the whole attempt
(one transaction, REQ-FIN-015) → return. The lock is what makes the per-fiscal-year counter
safe under concurrency: two simultaneous creates can no longer observe the same predecessor,
so `UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO` stays an unreachable backstop instead of surfacing as an
unlocalized data-integrity 409. A sequence was rejected (the counter restarts per year and the
schema declares none) and so was catch-and-retry (a service may not catch
DataIntegrityViolationException)
Repository: QR-FIN-024, QR-FIN-029, QR-FIN-030, QR-FIN-031, QR-FIN-032, QR-FIN-033 · join
NONE · READ_WRITE (one transaction, build-through-post)
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_CREATE` · Localization: descriptionAr/En
<!-- API:API-FIN-019:END -->
<!-- SUB:SVC-API-CRUD:END -->

<!-- SUB:SVC-API-INT:START traces=REQ-FIN-010,REQ-FIN-023,REQ-FIN-024,REQ-FIN-026,REQ-FIN-028,REQ-FIN-031,REQ-FIN-034,REQ-FIN-036,REQ-FIN-037 -->
### SUB — SVC-API-INT (posting-pipeline orchestration and period-control actions)

<!-- API:API-FIN-020:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,DBF-FIN-041,DBF-FIN-090,DBF-FIN-106,DBF-FIN-107 -->
### API-FIN-020 — build event entry (system)
Endpoint: POST /api/v1/fin/journal-entries/from-event · Layers: `JournalEntryController.buildFromEvent`→`EventEntryService.build`
Request: the canonical accounting event payload (opaque shape, out-of-scope Event consumer, POL-FIN-020)
Response: 201 · `JournalEntryResponse` (statusCode=POSTED) — or a rejection recorded for operator follow-up (REQ-FIN-013)
Validations: RULE-FIN-004 (duplicate eventReference, QR-FIN-026), RULE-FIN-005 (active
rule exists, QR-FIN-027), RULE-FIN-003 (the single-remainder guarantee RULE-FIN-010 depends
on, re-checked over the stored line set, QR-FIN-016), RULE-FIN-010 (PER-SIDE remainder
difference, QR-FIN-028), then the same RULE-FIN-006/007/008/009 checks as API-FIN-019
(QR-FIN-029..032)
Errors: `FIN-409-DUPLICATE-EVENT`, `FIN-404-NO-ACTIVE-RULE`, `FIN-409-REMAINDER-COUNT`,
`FIN-422-REMAINDER-MARKER`, `FIN-422-REMAINDER-NOT-POSITIVE`, `FIN-409-UNBALANCED`,
`FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`, `FIN-409-INVALID-DIMENSION`,
`FIN-422-MAPPING-UNSUPPORTED` (a rule line whose accountDerivationTypeCode is MAPPING — the
derivation fails loudly, since db-script-fin.md declares no mapping store; CONSTANT and
DIRECT are unaffected)
Orchestration: check RULE-FIN-004 (QR-FIN-026) → resolve active rule (QR-FIN-027) →
generate docNo (under the fiscal-year allocation lock, as API-FIN-019) → build lines from
the rule against the event's fields, computing the remainder line last as the difference
between the total already carried by the OPPOSING posting side and the total already carried
by the remainder line's own side (QR-FIN-028, QR-FIN-025) — a side-blind total would subtract
debit and credit lines alike from the base amount and produce a negative amount that dies on
CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE; a remainder that computes to zero or less is
`FIN-422-REMAINDER-NOT-POSITIVE`. Which line is the remainder is read from `isRemainderFl`
alone (DBF-FIN-103), the same marker RULE-FIN-003's guard counts → validate (QR-FIN-029..032)
→ post (QR-FIN-033) → return
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
Validations: the template must still be ACTIVE — `RecurringTemplateDomain.assertCanRun()`
(the NEW Domain companion for ENT-FIN-011) runs FIRST, immediately after the row is loaded and
before the period is resolved, and refuses a deactivated template with `FIN-409-NOT-ACTIVE`;
**no RULE-FIN-* states this gate — it rests on a recorded human decision of 2026-09-12, not on
stated requirement.** Then the same RULE-FIN-006/007/008/009 checks as API-FIN-019 (the
template's own lines were already balance-checked at API-FIN-013 create time, but re-validated
here since accounts/periods may have changed since)
Errors: same as API-FIN-019, plus `FIN-404-TEMPLATE` (unknown recurring template id) and
`FIN-409-NOT-ACTIVE` (the template exists but is deactivated)
Orchestration: load template (QR-FIN-019) → assert it is active → build entry from its lines (journalTypeCode=
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
Validations: the rule must still be ACTIVE — `AllocationRuleDomain.assertCanRun()` runs FIRST,
immediately after the row is loaded and before the target set is even fetched, and refuses a
deactivated rule with `FIN-409-NOT-ACTIVE`; **no RULE-FIN-* states this gate — it rests on a
recorded human decision of 2026-09-12, not on stated requirement.** Then RULE-FIN-003 (single
remainder marker over the stored targets, QR-FIN-016) and RULE-FIN-010 (per-side remainder
guarantee, QR-FIN-028, reused) then RULE-FIN-006/007/008/009
Errors: same family as API-FIN-019, plus `FIN-404-ALLOCATION-RULE`, `FIN-409-NOT-ACTIVE`,
`FIN-409-REMAINDER-COUNT`, `FIN-422-REMAINDER-MARKER`, `FIN-422-REMAINDER-NOT-POSITIVE`
Orchestration: load rule → assert it is active → load targets + current source-account balance (QR-FIN-022) →
distribute per target's distributionTypeCode, the target marked `isRemainderFl`
(DBF-FIN-141, the single marker — not `distributionTypeCode`) absorbing the rounding
difference between the source line's side and the targets' own side (QR-FIN-028) → build
entry (journalTypeCode=ALLOCATION) → validate + post (QR-FIN-029..033) → return
Repository: QR-FIN-022, QR-FIN-028, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-017:END -->

<!-- API:API-FIN-021:START traces=REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,DBF-FIN-042,DBF-FIN-043 -->
### API-FIN-021 — reverse entry
Endpoint: POST /api/v1/fin/journal-entries/{id}/reverse · Layers: `JournalEntryController.reverse`→`JournalEntryService.reverse`
Request: path `id` · Response: 201 · `JournalEntryResponse` (the new reversal entry)
Validations: RULE-FIN-013 (must be POSTED and not already reversed, QR-FIN-035); RULE-FIN-012
(period substitution if original's is closed, QR-FIN-036)
Errors: `FIN-409-NOT-POSTED`, `FIN-409-ALREADY-REVERSED`, `FIN-404-ENTRY`
Orchestration: load original UNDER A ROW LOCK (`SELECT ... FOR UPDATE` on the
FIN_JOURNAL_ENTRY header — no FIN entity carries `@Version`, so without it two concurrent
reversals both read reversalEntryId as null, both post a mirror, and the second save
overwrites the first link, leaving one orphaned mirror and a net effect of −(original)) →
check RULE-FIN-013 (QR-FIN-035) → resolve posting period
(original's if Open, else the current open period per RULE-FIN-012, QR-FIN-036) → build
mirrored lines with opposite directions, same amounts (RULE-FIN-011, QR-FIN-034) →
validate + post (QR-FIN-029..033, journalTypeCode=REVERSAL) → set originalEntryId/
reversalEntryId on both rows (bidirectional link) → return. Classic reversal: the original
STAYS POSTED — the only write back to it is the reversalEntryId link (DBF-FIN-043); its
statusCode is never modified, so both entries are seen by the POSTED-only report queries and
the pair nets to zero (SRS A7). Because the original stays POSTED, the double-reversal half of
RULE-FIN-013 is an explicit guard on the reversal link: a second reverse on the same entry is
rejected with `FIN-409-ALREADY-REVERSED` (AC-FIN-030), which would otherwise post a second
mirror and leave a net effect of −(original).
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
Period spans and names (governed, not implicit): when `periodCount` = 12 and
[startDate, endDate] spans one whole calendar year, each generated period IS a calendar
month — period N runs from the 1st to the last day of the Nth month of the span — and its
NAME_AR / NAME_EN (DBF-FIN-078/079, both NOT NULL) are that month's own name in Arabic and
English, taken from the platform's locale data (`java.time.Month` + CLDR), never a
hardcoded string table. For any other `periodCount`, or a span that is not a whole year,
the fallback is the even split: the days of [startDate, endDate] divided into periodCount
contiguous blocks, the first (totalDays mod periodCount) blocks one day longer, so the last
period always ends on the year's endDate and no day belongs to two periods; those periods
are named "الفترة N" / "Period N".
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
distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`. **That gate is the WHOLE of the rule**: the
`@PreAuthorize` on `FiscalPeriodService.hardClose`, enforced by SEC's own mechanism, exactly as
RULE-FIN-015 states it and AC-FIN-038 describes it. There is NO service-layer SoD read — the
one that existed was deleted on 2026-09-12 as an over-implementation (it refused the close for
every caller whenever any single user held both codes); see the Error Catalog's struck
`FIN-403-SOD-VIOLATION` row and retired XM-FIN-002
Errors: `FIN-409-NOT-REOPENABLE`(reused message context), `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040)
→ transition, set closedBy/closedAt to the approving principal (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` (custom — the distinct permission RULE-FIN-015 requires; since V30 it is also granted to SYS_ADMIN) · Localization: n/a
<!-- API:API-FIN-026:END -->

<!-- API:API-FIN-027:START traces=REQ-FIN-036,DBF-FIN-069,DBF-FIN-034 -->
### API-FIN-027 — run year-end close
Endpoint: POST /api/v1/fin/fiscal-years/{id}/year-end-close · Layers: `FiscalYearController.yearEndClose`→`FiscalYearService.yearEndClose`
Request: path `id` · Response: 201 · `{closingEntry: JournalEntryResponse, openingEntry: JournalEntryResponse}`
Validations, IN THIS ORDER (the order is part of the contract — a test asserting 409 on this
endpoint must not be defeated by a missing successor year or Retained Earnings
account): (1) the fiscal year's own statusCode must
still be OPEN — a re-run against an already-CLOSED year is rejected with
`FIN-409-INVALID-TRANSITION`, a stated rule on ENT-FIN-007's state machine rather than the
incidental `FIN-409-PERIODS-NOT-CLOSED` the first run's own YEAR_END_CLOSE transitions would
otherwise raise; (2) every period of the year must be HARD_CLOSE (§10.4 precondition), 409.
Only then are the successor year and the Retained Earnings account resolved.
RULE-FIN-015 is no longer a numbered step here: it is enforced entirely by this endpoint's
`@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate, which rejects before the method body
runs. The step that used to come first — a service-layer SoD read answering 403 — was deleted
on 2026-09-12 as an over-implementation; see the Error Catalog's struck `FIN-403-SOD-VIOLATION`
row. **A test written against the old contract and asserting 403 from inside this method will
now fail, and should be retargeted at the `@PreAuthorize` gate.**
Errors: `FIN-409-INVALID-TRANSITION` (year already closed), `FIN-409-PERIODS-NOT-CLOSED`, `FIN-404-YEAR` (unknown year id, or no adjacent successor year), `FIN-404-ACCOUNT` (no account marked as Retained Earnings)
Orchestration: verify the year is still OPEN → verify all periods Hard
Closed → resolve the successor year and the Retained Earnings account → compute closing
balances (QR-FIN-041) →
build + post a closing entry into the year's LAST period (result accounts → Retained
Earnings, journalTypeCode=CLOSING). The Retained Earnings account is DERIVED BY THE SYSTEM
from FIN_ACCOUNT.is_retained_earnings_fl (DBF-FIN-147, at most one row TRUE — partial unique
index UQ_FIN_ACCOUNT_RETAINED_EARNINGS) and is never supplied by the caller; no marked
account is `FIN-404-ACCOUNT`
→ build + post the next year's opening entry from the resulting balance-sheet balances
(journalTypeCode=OPENING, QR-FIN-041, POL-FIN-010) — CLOSING/OPENING are two values added
to the JOURNAL_TYPE lookup this stage (see Decisions Applied — a data-only, non-breaking
extension, not a new REQ/RULE) → mark FiscalYear statusCode=CLOSED, periods
statusCode=YEAR_END_CLOSE → return
Repository: QR-FIN-041, QR-FIN-029, QR-FIN-030, QR-FIN-032, QR-FIN-033 (both generated
entries go through the same validated posting pipeline) · QR-FIN-031 is deliberately NOT
applied to either of them: RULE-FIN-008 itself exempts the year-end closing and opening
entries, since this API's own all-periods-Hard-Closed precondition leaves no Open period for
the closing entry to post into. RULE-FIN-006/007/009 apply to both in full · the successor
fiscal year receiving the opening entry is resolved by DATE ADJACENCY (the year whose
startDate is the day after this year's endDate) — a DERIVED decision, recorded as such in
execution-state.json because ENT-FIN-007 declares no successor column; no such year is
`FIN-404-YEAR` · join intra-module · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` · Localization: n/a
DORMANT YEAR — a reviewed decision, not an accident. For a fiscal year in which no result account
carries a non-zero balance, `FiscalYearService.closingLines` contributes no line at all (each
result account with `net().signum() == 0` is skipped, and the Retained Earnings absorbing line is
added only when the running `resultTotal` is itself non-zero), and symmetrically
`openingLines` contributes none when no balance-sheet account carries a non-zero balance. The run
therefore posts a CLOSING (and OPENING) journal entry with an EMPTY line set, and that entry still
consumes a `docNo`: `JournalPostingService.buildValidateAndPost` allocates the number from the
locked fiscal-year series before it validates, and writes the entry unconditionally.
This was reviewed and deliberately KEPT. `JournalEntryDomain.checkBalanced` sums debits and
credits and returns empty when they compare equal, so 0 = 0 passes — a lineless entry literally
satisfies AC-FIN-036's "both entries individually balanced". Omitting the entry would make
AC-FIN-036's "posts a closing entry" false, and refusing the close outright would invent a rule no
artifact states.
Reachable only from here. `JournalEntryCreateRequest.lines` carries `@NotEmpty`, so API-FIN-019
rejects a lineless entry at the DTO boundary. This shape exists solely on the internal year-end
path, which builds its lines itself and never passes through that DTO.
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
A second row, XM-FIN-002 (READ → SEC), was assigned at ALIGN-BE — SEC-BE landed after this
phase was written and added what then looked like a second, genuinely distinct cross-module
consumption — and was RETIRED on 2026-09-12. Its block below is kept as a historical record,
struck; it must not be read as a live dependency.

<!-- XM:XM-FIN-001:START traces=REQ-FIN-001,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-018,REQ-FIN-022,REQ-FIN-025,REQ-FIN-031 -->
### XM-FIN-001 — validate/read lookup-backed codes against MDL
Target        : MDL · ENT-MDL-001/002 (LookupType/LookupValue) · classification SOFT-READ
Interface     : in-process Spring injection — FIN's service layer injects
`com.erp.mdl.crossmodule.MdlLookupApi` and calls `readActiveValuesByKey(typeKey)` for every
one of FIN's 13 owned keys, at the point each lookup-backed field is written or offered as a select-list
Contract      : data required = the submitted code exists as an active value under the
named type, checked by membership in the returned `List<LookupOptionView>` (code, labelAr,
labelEn, sortOrder); fallback if absent = reject with `FIN-400-INVALID-LOOKUP`; an unknown/
inactive `typeKey` raises MDL's `LocalizedException(NOT_FOUND, MDL_404_TYPE_KEY)`, which FIN
catches and translates to `FIN-400-INVALID-LOOKUP` (MDL's code never leaks out of FIN's API);
retry = none (same-process call, no network hop); idempotency
= read-only, naturally idempotent
Blocks        : none DEFERRED — MDL v1 is already gated (pass-1 APPROVE); ACTIVE from the
moment FIN v1 is created
<!-- XM:XM-FIN-001:END -->

<!-- XM:XM-FIN-002:START traces=REQ-FIN-037,REQ-FIN-038 -->
### ~~XM-FIN-002~~ — RETIRED 2026-09-12 (historical record, NOT a live dependency)
Status        : RETIRED. Kept so a reader reconstructing the decision can see what was
registered and why it went away. It binds nothing today and no code consumes it. The id is
burned, not reused.
What it was   : a READ of SEC's user→permission directory, classification READ, target SEC ·
ENT-SEC-001 (User) + SEC's role/permission grant tables. `FinSeparationOfDutiesService`
injected `com.erp.sec.crossmodule.SecUserDirectoryApi` and called
`findUserIdsHoldingPermission(permissionCode)` twice, for `PERM_FIN_PERIODS_CLOSE_APPROVE` and
`PERM_FIN_JOURNAL_ENTRIES_CREATE`, on every API-FIN-026 hard-close and API-FIN-027 year-end
close (never HTTP); it derived `closeApprovePermissionHeld` and `entryCreatePermissionShared`
and handed them to `FiscalPeriodDomain.assertCanHardClose`, which threw
`FIN-403-SOD-VIOLATION`.
Why it is gone: that check enforced GLOBAL user-set disjointness — if ANY single user in the
system held both permissions, the close was refused for EVERY caller, including a perfectly
clean approver — and no REQ, AC or RULE requires it. RULE-FIN-015 (srs-fin.md:1026-1033)
requires only that the close-approval action be gated by a permission DISTINCT from the
journal-entry-creation permission, "enforced through the Security module", and its `Data
source` line reads "DEFERRED — ... has no FIN-side field to read"; REQ-FIN-038
(srs-fin.md:781-788) and AC-FIN-038 (:789-792) say the same, the latter describing an ordinary
interceptor denial. By recorded human decision on 2026-09-12 the over-implementation was
removed: `FinSeparationOfDutiesService` and `FiscalPeriodDomain.assertCanHardClose(...)` were
deleted. RULE-FIN-015 still stands, enforced by the delivered
`@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on `FiscalPeriodService.hardClose` and
`FiscalYearService.yearEndClose`.
Consequence   : that service was FIN's ONLY consumer of `com.erp.sec.crossmodule`, so **FIN's
cross-module dependency on SEC is gone entirely**. The only remaining `com.erp.sec` mentions
under `src/main/java/com/erp/fin/` are `@PreAuthorize` SpEL string literals naming
`PermissionConstants`, plus two javadoc references — neither is a structural dependency.
`FIN-403-SOD-VIOLATION` is correspondingly struck as unreachable in the Error Catalog.
<!-- XM:XM-FIN-002:END -->

FIN's dependency on SEC for identity/authorization (the principal on every request, the
`@PreAuthorize` gate, and FIN's own self-registration of its module/screens/actions into SEC)
remains NOT a formal `XM` row — ADR-FIN-001 (carried from P2), unchanged — and since 2026-09-12
it is the ONLY relationship FIN has with SEC. XM-FIN-002 had been registered separately on the
grounds that it was a different thing: not the platform's ambient authorization of the caller
but FIN's own business logic reading SEC's data *about other users* — a named FIN service
calling a named SEC `crossmodule` interface method, whose returned rows were an input to a FIN
business rule (RULE-FIN-015) and whose absence had a defined, FIN-owned failure code. That
reasoning was sound for exactly as long as the consumption existed. It stopped applying when
the service making the call was deleted. Nothing about ADR-FIN-001 changed; what changed is
that there is no longer a second, non-ambient consumption for it to fail to cover.
<!-- PHASE:INT-C:END -->

<!-- PHASE:INT-R:START traces=REQ-FIN-001 -->
## PHASE 6 — INT-R (cross-module resolve)

| XM | Status | Workaround (if not READY/ACTIVE) |
|---|---|---|
| XM-FIN-001 | ACTIVE | not applicable — target already gated |
| ~~XM-FIN-002~~ | RETIRED 2026-09-12 | not applicable — the row is historical. `FinSeparationOfDutiesService`, its only consumer, was deleted with the SoD over-implementation (see INT-C); there is no read left to fail and so nothing to work around |

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
| FIN_ACCOUNTS | ✓ (API-FIN-001) | ✓ (API-FIN-002) | ✓ (API-FIN-003, and API-FIN-004 deactivate) | — | — |
| FIN_DIMENSIONS | ✓ (API-FIN-005,008) | ✓ (API-FIN-006,007) | ✓ (API-FIN-035, deactivate a dimension VALUE — `PERM_FIN_DIMENSIONS_UPDATE`, added by V28) | — | — |
| FIN_RULES | ✓ (API-FIN-009) | ✓ (API-FIN-010) | ✓ (API-FIN-011, add line; and API-FIN-034, deactivate rule) | — | — |
| FIN_RECURRING_TEMPLATES | ✓ (API-FIN-012) | ✓ (API-FIN-013) | ✓ (API-FIN-014, run; and API-FIN-036, deactivate template) | — | — |
| FIN_ALLOCATION_RULES | ✓ (API-FIN-015) | ✓ (API-FIN-016) | ✓ (API-FIN-017, run; and API-FIN-037, deactivate rule) | — | — |
| FIN_JOURNAL_ENTRIES | ✓ (API-FIN-018,022) | ✓ (API-FIN-019,020) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, API-FIN-021) |
| FIN_PERIODS | ✓ (API-FIN-033, search periods — and still the gateway, see below) | ✓ (API-FIN-023, year) | ✓ (API-FIN-024,025) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE`, API-FIN-026,027 — the distinct permission RULE-FIN-015 requires) |
| FIN_ACCOUNT_LEDGER | ✓ (API-FIN-028) | — | — | — | — |
| FIN_TRIAL_BALANCE | ✓ (API-FIN-029) | — | — | — | — |
| FIN_BALANCE_SHEET | ✓ (API-FIN-030) | — | — | — | — |
| FIN_INCOME_STATEMENT | ✓ (API-FIN-031) | — | — | — | — |
| FIN_DIMENSION_REPORTS | ✓ (API-FIN-032) | — | — | — | — |

**DELETE column — deliberately empty everywhere.** FIN exposes no `DELETE` endpoint at all.
Deactivation is `PUT /{id}/deactivate` gated by the screen's UPDATE permission (see
`AccountService.deactivate`, `@PreAuthorize` on `PERM_FIN_ACCOUNTS_UPDATE`), exactly as
MDL_LOOKUPS models it, and neither V24 nor V28 seeds a `PERM_FIN_*_DELETE` row for any FIN screen.
The FIN_ACCOUNTS row above read "✓ deactivate (API-FIN-004)" under DELETE until ALIGN-BE moved it
to UPDATE; inventing DELETE rows here would create permanently-unreferenced registry data. The two
later deactivates follow the same modelling: API-FIN-034 (event-type rule) under FIN_RULES/UPDATE,
API-FIN-035 (dimension value) under FIN_DIMENSIONS/UPDATE, API-FIN-036 (recurring template) under
FIN_RECURRING_TEMPLATES/UPDATE and API-FIN-037 (allocation rule) under FIN_ALLOCATION_RULES/UPDATE.
There are five deactivate endpoints in FIN and no `activate` anywhere — API-FIN-034, 035, 036 and
037 each deliberately omit a counterpart, following the delivered `AccountService.deactivate`
precedent.

**FIN_DIMENSIONS / UPDATE — the one cell V24 did not seed.** `PERM_FIN_DIMENSIONS_UPDATE` is
declared in `PermissionConstants` and registered by `V28__fin_dimensions_update_action.sql`, which
also grants it explicitly to `SYS_ADMIN`. The explicit grant is not optional: V25 grants SYS_ADMIN
its FIN actions with a `SELECT` over `SEC_ACTION_REG` and has already run everywhere, so Flyway
will never re-evaluate it against a row inserted later — registering without granting is exactly
the MDL failure V19/V21 had to repair. Tiers 1 and 2 need nothing new (V25 already grants SYS_ADMIN
the FIN module row and every FIN screen, FIN_DIMENSIONS included), and the RULE-SEC-007 gateway
holds because V24/V25 already registered and granted `PERM_FIN_DIMENSIONS_VIEW` on the same screen.
`FIN_CLOSE_APPROVER` (V27) deliberately gets nothing from V28 — its grants are scoped to
FIN_PERIODS and two permission codes.

**FIN_RULES / UPDATE — one permission, two endpoints.** API-FIN-034 reuses the pre-existing
`PERM_FIN_RULES_UPDATE` that V24 already seeds and V25 already granted, so it needed no new
constant, no new error code and no migration.

**FIN_RECURRING_TEMPLATES / UPDATE and FIN_ALLOCATION_RULES / UPDATE — the same shape, two
endpoints each.** API-FIN-036 reuses `PERM_FIN_RECURRING_TEMPLATES_UPDATE` and API-FIN-037 reuses
`PERM_FIN_ALLOCATION_RULES_UPDATE`; both action rows are seeded by V24 (`FIN_RECURRING_TEMPLATES /
UPDATE` and `FIN_ALLOCATION_RULES / UPDATE`) and both are already granted to SYS_ADMIN by V25's
Tier-3 statement, which grants every FIN action row except `PERM_FIN_PERIODS_CLOSE_APPROVE`. So
neither endpoint needed a new constant, a new error code or a migration — unlike API-FIN-035, whose
`FIN_DIMENSIONS / UPDATE` row did not exist and had to be both registered and explicitly granted by
V28. Each screen's UPDATE cell therefore now covers a run AND a deactivate.

**Deactivating now DOES stop the run — defect closed 2026-09-12, by decision rather than by rule.**
The permission gate above is still the whole of what API-FIN-036/037 themselves enforce, but the
two run endpoints are no longer indifferent to the flag. `RecurringTemplateService.run`
(API-FIN-014) and `AllocationRuleService.run` (API-FIN-017) each call `assertCanRun()` on the
loaded row's Domain companion — `RecurringTemplateDomain`, created for this, and
`AllocationRuleDomain` — and refuse a deactivated definition with `FIN-409-NOT-ACTIVE` (409).
**No RULE-FIN-* states this gate**; it rests on a recorded human decision, because closing the gap
required a new "exists but is inactive" error code that no requirement asks for. Do not cite it as
pre-existing spec. What remains open on those two screens is only that neither a template nor an
allocation rule can be UPDATED after creation. Recorded in full at srs-fin.md SCR-REQ-FIN-004 §B4,
SCR-REQ-FIN-005 §B4 and §"Access summary", and in SVC-API-CRUD's API-FIN-036/037 blocks.

**FIN_PERIODS / VIEW — a gateway that now also has an endpoint.** `PERM_FIN_PERIODS_VIEW` is a
real V24 action row and is load-bearing: `MenuService.effectiveAuthorityCodes()` keeps a granted
permission only if the same screen also carries a granted gateway (VIEW) action, so V27's
FIN_CLOSE_APPROVER role must hold it for `PERM_FIN_PERIODS_CLOSE_APPROVE` to survive into the
caller's authorities. That much is unchanged.

What HAS changed: the row is no longer constant-less and no longer endpoint-less. API-FIN-033
(`POST /api/v1/fin/fiscal-periods/search`, `FiscalPeriodService.search`) is gated on
`PERM_FIN_PERIODS_VIEW`, and the matching `PermissionConstants` constant was added with it. No
migration was needed — the action row was already registered by V24 and already granted by V25 and
V27. This section previously recorded the opposite state ("no `PermissionConstants` constant,
because FIN publishes no fiscal-period read endpoint … §B5 and the API registry define no search
API"); that was accurate before API-FIN-033 and is superseded now. srs-fin.md SCR-REQ-FIN-007 §B5
carries the endpoint row.

**Seed data** (REQ-FIN-044): 12 SEC_PAGES rows registered via SEC's screen-registration
endpoint at FIN onboarding; one action row per action above via SEC's action-registration
endpoint, following `PERM_<PAGE_CODE>_<ACTION>` — including the two custom actions
(`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, `PERM_FIN_PERIODS_CLOSE_APPROVE`). Delivered as migrations
V24 (registry) and V25 (SYS_ADMIN grants); V27 adds the dedicated `FIN_CLOSE_APPROVER` role; V28
adds the one later action row, `FIN_DIMENSIONS / UPDATE`, together with its own explicit SYS_ADMIN
grant; V30 grants `PERM_FIN_PERIODS_CLOSE_APPROVE` to `SYS_ADMIN`, the one row V25 had
deliberately withheld — see the SoD section below.

**SoD enforcement (RULE-FIN-015, POL-FIN-016) — SPECIFICATION REWRITTEN 2026-09-12.** What the
SRS actually requires, read at source: RULE-FIN-015 (srs-fin.md:1026-1033) requires the
period-close-approval action to be "gated by a permission distinct from the journal-entry-creation
permission, enforced through the Security module", and its `Data source` line reads "DEFERRED —
the permission matrix is the Security module's declaration surface; FIN declares no permission
entity in this version, so the separation is enforced there and has no FIN-side field to read".
REQ-FIN-038 (:781-788) states the same requirement, and AC-FIN-038 (:789-792) describes an
ordinary interceptor denial: "Given a role holding only the entry-creation permission / When that
role's user attempts the period-close-approval action / Then the system denies it (the CORE
interceptor, per SEC's own mechanism)."

That is the whole requirement, and it is satisfied in full by the delivered
`@PreAuthorize(PermissionConstants.PERM_FIN_PERIODS_CLOSE_APPROVE)` on
`FiscalPeriodService.hardClose` (API-FIN-026) and `FiscalYearService.yearEndClose`
(API-FIN-027). `PERM_FIN_PERIODS_CLOSE_APPROVE` is a different permission code from
`PERM_FIN_JOURNAL_ENTRIES_CREATE`, and SEC's own mechanism enforces it — `JwtAuthenticationFilter`
builds the caller's authorities from `MenuService`, which reads `SEC_ROLE_ACTION_GRANT`. Keeping
the two codes off the same role remains a sound administrative guideline, and `FIN_CLOSE_APPROVER`
(V27) is how a deployment expresses it; it is a guideline, not a constraint FIN code enforces.

**WHAT THIS SECTION USED TO SPECIFY, AND MUST NOT SPECIFY AGAIN.** Every earlier revision of this
paragraph said FIN's service layer "additionally checks at hard-close/year-end-close time that no
single *user* holds both, per role union". **That sentence is the origin of the defect** — it is a
GLOBAL user-set-disjointness rule, strictly stronger than anything the SRS states, and it was
implemented exactly as written: `FinSeparationOfDutiesService` read SEC's user directory and
`FiscalPeriodDomain.assertCanHardClose` threw `FIN-403-SOD-VIOLATION` whenever ANY single user in
the system held both codes, refusing the close for EVERY caller — including an approver who was
himself perfectly clean. Both classes were DELETED on 2026-09-12 by recorded human decision. This
section is rewritten rather than annotated precisely so that a future generation pass reading it
cannot regenerate the removed behaviour. **No FIN service reads SEC's user directory, and none may
be specified to here.** FIN has no cross-module dependency on SEC at all any more: XM-FIN-002 is
retired (INT-C), and `FIN-403-SOD-VIOLATION` is struck as unreachable in the Error Catalog.

**Who can actually close, as seeded.** V25 deliberately withheld `PERM_FIN_PERIODS_CLOSE_APPROVE`
from `SYS_ADMIN`, because granting it would have put the bootstrap `admin` user into both
permission sets and tripped the removed check on every close. With the check gone that exclusion
had no purpose, and `V30__fin_sys_admin_close_approve_grant.sql` reverses it by granting the single
withheld action row to `SYS_ADMIN`. So on a fresh database **the bootstrap `admin` user can now
hard-close a period and run a year-end close** — endpoints V25 had left answering 403 to every
principal. V27's `FIN_CLOSE_APPROVER` role (module FIN, screen FIN_PERIODS, exactly the
`PERM_FIN_PERIODS_VIEW` gateway plus `PERM_FIN_PERIODS_CLOSE_APPROVE`, and by construction no entry
creation) **remains valid** and is still the least-privilege way to give close approval to someone
who is not a system administrator. It is simply no longer REQUIRED for the close to work at all.

**V27's own "OPERATIONAL PRECONDITIONS" text is now factually wrong in BOTH numbered points, and
V27 is applied and immutable — this prose is the correction, because the source cannot be fixed.**
V27's header states (1) that a user assignment is still required, because
`FinSeparationOfDutiesService.resolveFacts()` reports `closeApprovePermissionHeld =
!approvers.isEmpty()` and `FiscalPeriodDomain.assertCanHardClose` throws when nobody holds
close-approval; and (2) that the assignee must not be a journal-entry creator and must NOT be the
bootstrap `admin`, or `FIN-403-SOD-VIOLATION` trips on every close. **Neither holds.** There is no
`resolveFacts()`, no `assertCanHardClose`, and no thrower of `FIN-403-SOD-VIOLATION` anywhere in
the codebase: "nobody holds close-approval" is no longer a failure mode, and assigning
`FIN_CLOSE_APPROVER` to a journal-entry creator — or to `admin`, who now holds the permission
directly via V30 — breaks nothing. Read V27's header as the history of a removed mechanism, never
as live operating instructions. (The same applies to V25's header, which explains its exclusion in
the same removed terms; V30's own header records the reversal in full.)

**Gateway**: every non-VIEW permission requires VIEW on the same screen first (platform
convention, SEC's own interceptor — not restated as a FIN-owned RULE).

**Forbidden responses**: both FIN 403 codes map through the `LocalizedException` envelope, each
carrying a registered FIN code and both ar/en messages — but only `FIN-403-FORBIDDEN` is still
reachable; see the next paragraph.

`FIN-403-SOD-VIOLATION` is STRUCK and no longer reachable, so it is not among them. It was never a
Spring Security `AccessDeniedException` — it was a business refusal thrown by hand as a
`LocalizedException`, so no advisor or handler for access denial was ever involved in it, and that
much is unchanged. What changed on 2026-09-12 is that BOTH of its throw sites were deleted with the
SoD over-implementation, so nothing raises it at all. The constant
`FinErrorCodes.FIN_403_SOD_VIOLATION` and both bundle entries were deliberately left in place by
the code session; they are dead text, not a live response.

`FIN-403-FORBIDDEN` now does too, and **this reverses what this section previously said**. It is a
real `FinErrorCodes.FIN_403_FORBIDDEN` constant and has entries in BOTH
`src/main/resources/i18n/messages.properties` and `messages_ar.properties`. A `@PreAuthorize`
denial on any `com.erp.fin.service.*` method is intercepted by
`com.erp.fin.security.FinForbiddenAdvisor`, which catches the `AccessDeniedException` and re-raises
it as `LocalizedException(Status.FORBIDDEN, FinErrorCodes.FIN_403_FORBIDDEN)`; `GlobalExceptionHandler`
then renders it like every other FIN error. The advisor is a `DefaultPointcutAdvisor` at
`Ordered.HIGHEST_PRECEDENCE`, declared once for the whole module — never per endpoint, and never as
a feature-module `@ControllerAdvice`, which `gov-enforce-backend-contract` CU.7 forbids. It mirrors
`com.erp.sec.security.SecForbiddenAdvisor`. So **FIN-403-FORBIDDEN does reach the wire**, and the
earlier claim that it is "the catalog's *name* for a platform response, not a FIN code" is
superseded.

Two boundaries bound that statement, and both were read in source rather than assumed:

1. **Filter-chain denials are still `SEC-403-FORBIDDEN`.** A denial raised before any FIN service is
   entered never reaches an AOP proxy or `GlobalExceptionHandler`; it is written directly by the
   chain's `accessDeniedHandler`. Today this is unreachable for FIN: `SecurityConfig` (`com.erp.main.config`)
   authorizes with `.anyRequest().authenticated()` and declares no FIN authority rule, so every FIN
   permission denial is in fact a `@PreAuthorize` denial on a FIN service and does pass through the
   advisor. Adding a URL-level authority rule for a FIN path would change that.
2. **`FIN-403-SOD-VIOLATION` is moot.** It never was an `AccessDeniedException`, so the advisor
   never saw it; and since 2026-09-12 it has no throw site at all. See the SoD section above.

What DID change, platform-wide: the 403 body is now localized. `handleAccessDenied` resolves its
message through the same `resolveMessage(...)` helper and `MessageSource` every other handler uses,
keyed on a new `CommonErrorCodes.ACCESS_DENIED` constant, and `ACCESS_DENIED` was added to BOTH
`messages.properties` and `messages_ar.properties`. The wire `code` is unchanged and the English
text is byte-identical to the string that was hardcoded before, so only Arabic callers observe any
difference. The earlier description of this response as carrying "a hardcoded English message,
bypassing `MessageSource`" is therefore no longer accurate; the separate point — that this is a
platform response and not a FIN code — still stands, as does the fact that routing it through
`LocalizedException` would change every module's 403 envelope and remains a platform decision.
<!-- PHASE:SEC-BE:END -->

<!-- PHASE:ALIGN-BE:START traces=REQ-FIN-017 -->
## PHASE 8 — ALIGN-BE

See Alignment self-check (ALIGN) below.
<!-- PHASE:ALIGN-BE:END -->

## Error Catalog — FIN v1

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `FIN-{http}[-{SLUG}]`.

| code | RULE / PLATFORM-STD | API | HTTP | trigger | message-AR | message-EN |
|---|---|---|---|---|---|---|
| FIN-409-ACCOUNT-DUP | PLATFORM-STD | API-FIN-002 | 409 | duplicate account code | رمز الحساب مستخدم بالفعل | Account code already in use |
| FIN-409-PARENT-NOT-LEAF-ELIGIBLE | RULE-FIN-001 | API-FIN-002 | 409 | parent account cannot remain a leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-400-INVALID-LOOKUP | PLATFORM-STD (XM-FIN-001) | many | 400 | submitted code not found in MDL | القيمة المُدخلة غير صالحة | The submitted value is not valid |
| FIN-409-HAS-CHILDREN | RULE-FIN-001 | API-FIN-003 | 409 | marking a parent as leaf | لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا | An account with sub-accounts cannot accept direct posting |
| FIN-404-ACCOUNT | PLATFORM-STD | API-FIN-002, 003, 004, 013, 016, 019, 020, 027, 028 | 404 | unknown account id — every path that resolves an account FK raises it, not only the three originally listed: API-FIN-002's `parentAccountId` (AccountService.java:168, reached only from `create`), a template line's `accountId` (API-FIN-013, RecurringTemplateService.java:304), an allocation rule's source and target accounts (API-FIN-016, AllocationRuleService.java:278), a manual entry line's `accountId` (API-FIN-019, JournalEntryService.java:349), the account code an event rule derives (API-FIN-020, EventEntryService.java:193) and API-FIN-027's Retained Earnings account, where the reachable failure is "none marked" rather than an unknown id (FiscalYearService.java:347) | الحساب غير موجود | Account not found |
| FIN-409-DIMENSION-DUP | PLATFORM-STD | API-FIN-006 | 409 | duplicate dimension code | رمز البُعد مستخدم بالفعل | Dimension code already in use |
| FIN-409-DIMVALUE-DUP | RULE-FIN-002 | API-FIN-007 | 409 | duplicate code within dimension | هذا الرمز مستخدم بالفعل ضمن هذا البُعد | This code is already used within this dimension |
| FIN-404-DIMENSION | PLATFORM-STD | API-FIN-007, 008, 032 | 404 | unknown dimension id | البُعد غير موجود | Dimension not found |
| FIN-404-DIMVALUE | PLATFORM-STD | API-FIN-035 | 404 | unknown dimension-value id | قيمة البُعد غير موجودة | Dimension value not found |
| FIN-409-RULE-DUP | PLATFORM-STD (§6.4) | API-FIN-010 | 409 | event type already has an active rule | يوجد بالفعل قاعدة نشطة لهذا النوع | An active rule already exists for this event type |
| FIN-409-REMAINDER-COUNT | RULE-FIN-003 | API-FIN-011, 016, 017, 020 | 409 | wrong remainder-line/target count — both guards are re-run on the consuming path, not only at create: the rule-line set is re-validated when an event entry is built (API-FIN-020, EventEntryService.java:104 → EventTypeRuleDomain.java:177) and the target set when an allocation rule is run (API-FIN-017, AllocationRuleService.java:179 → AllocationRuleDomain.java:122) | يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي | Exactly one remainder line is required when any percentage distribution is present |
| FIN-404-RULE | PLATFORM-STD | API-FIN-011, 034 | 404 | unknown event-type rule id | القاعدة غير موجودة | Rule not found |
| FIN-400-MISSING-FREQUENCY | PLATFORM-STD | API-FIN-013 | 400 | recurring template with no frequency | يلزم تحديد التكرار للقالب المتكرر | A frequency is required for a recurring template |
| FIN-404-TEMPLATE | PLATFORM-STD | API-FIN-014, 036 | 404 | unknown recurring template id — raised by `RecurringTemplateService.run` (API-FIN-014) and, since the template deactivate landed, by `RecurringTemplateService.deactivate` (API-FIN-036) resolving the same path id. API-FIN-036 raises it ONLY for an id that does not exist; deactivating an already-inactive template is not an error, and there is deliberately no "exists but is inactive" code — see the API-FIN-036 block in SVC-API-CRUD | القالب المتكرر غير موجود | Recurring template not found |
| FIN-404-ALLOCATION-RULE | PLATFORM-STD | API-FIN-017, 037 | 404 | unknown allocation rule id — raised by `AllocationRuleService.run` (API-FIN-017) and, since the rule deactivate landed, by `AllocationRuleService.deactivate` (API-FIN-037) resolving the same path id. API-FIN-037 raises it ONLY for an id that does not exist; deactivating an already-inactive rule is not an error, and there is deliberately no "exists but is inactive" code — see the API-FIN-037 block in SVC-API-CRUD | قاعدة التوزيع غير موجودة | Allocation rule not found |
| FIN-409-NOT-ACTIVE | (no RULE — recorded human decision, 2026-09-12) | API-FIN-014, 017 | 409 | running a DEACTIVATED recurring template (API-FIN-014) or a deactivated allocation rule (API-FIN-017). Thrown by `RecurringTemplateDomain.assertCanRun()` (a NEW Domain companion for ENT-FIN-011) and `AllocationRuleDomain.assertCanRun()`, each the first thing its service's `run` does after loading the row and before any period, line or target is resolved, so a retired definition posts nothing at all. `Status.CONFLICT` → HTTP 409, consistent with every other FIN refusal whose cause is the target row's own state (FIN-409-NOT-POSTED, FIN-409-NOT-REOPENABLE, FIN-409-PERIOD-NOT-OPEN, FIN-409-INVALID-TRANSITION); the screen's own 404 was NOT reused because the row does exist. **NO RULE-FIN-* STATES THIS GATE.** It closes the "deactivate does not stop the run" OPEN DEFECT by decision, not by implementing a requirement that was always there — do not cite it as pre-existing spec | هذا التعريف غير نشط ولا يمكن تشغيله | This definition is deactivated and cannot be run |
| FIN-409-UNBALANCED | RULE-FIN-006 | API-FIN-019, 020, 014, 017, 021, 027 | 409 | debits ≠ credits — checked once in JournalEntryService.createManual (API-FIN-019) and once in JournalPostingService.buildValidateAndPost (JournalPostingService.java:163), which is the single posting pipeline for API-FIN-014, 017, 020 AND for API-FIN-021's reversal and API-FIN-027's closing/opening pair; the last two were missing from this row | القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن | The entry is unbalanced — total debits do not equal total credits |
| FIN-409-NOT-POSTABLE-ACCOUNT | RULE-FIN-007 | API-FIN-019, 020, 014, 017, 021, 027 | 409 | non-leaf/inactive account — AccountDomain.checkPostable runs per line in JournalEntryService.createManual (API-FIN-019, :350) and in JournalPostingService.buildValidateAndPost (:141), so it also covers API-FIN-021's reversal and API-FIN-027's closing/opening pair | الحساب المستهدف لا يقبل ترحيلاً مباشرًا | The target account does not accept direct posting |
| FIN-409-PERIOD-NOT-OPEN | RULE-FIN-008 | API-FIN-019, 020, 014, 017, 021 | 409 | period not Open at post — API-FIN-021 raises it twice over: from the shared gate in JournalPostingService.buildValidateAndPost (:164) and, before that, when the original's period is closed and the ledger has no open period to receive the reversal (JournalEntryDomain.java:329). API-FIN-027 is deliberately NOT listed: RULE-FIN-008 exempts the year-end CLOSING/OPENING types (JournalEntryDomain.checkTargetPeriodOpenForGeneratedEntry, :236) | الفترة المستهدفة غير مفتوحة | The target period is not open |
| FIN-409-INVALID-DIMENSION | RULE-FIN-009 | API-FIN-013, 014, 016, 017, 019, 020, 021, 027 | 409 | invalid/inactive dimension value — RULE-FIN-009 (DimensionValueDomain.checkUsableOnLine) runs in JournalEntryService.createManual (API-FIN-019, :376) and in JournalPostingService.buildValidateAndPost (:144), so it also covers API-FIN-021 and API-FIN-027. API-FIN-013 and API-FIN-016 raise the SAME code for a different reason — plain FK resolution of a submitted `dimensionValueId` that does not exist (RecurringTemplateService.java:318, AllocationRuleService.java:291) — which is why they belong in this row even though no rule is evaluated there | قيمة البُعد غير صالحة | The dimension value is invalid |
| FIN-409-DUPLICATE-EVENT | RULE-FIN-004 | API-FIN-020 | 409 | repeated eventReference | تم بالفعل ترحيل قيد لهذا المرجع | An entry for this event reference has already been posted |
| FIN-404-NO-ACTIVE-RULE | RULE-FIN-005 | API-FIN-020 | 404 | no active rule for event type | لا توجد قاعدة نشطة لهذا النوع من الأحداث | No active rule exists for this event type |
| FIN-422-MAPPING-UNSUPPORTED | PLATFORM-STD | API-FIN-020 | 422 | rule line with accountDerivationTypeCode=MAPPING, for which no mapping store is declared in db-script-fin.md | يستخدم هذا السطر اشتقاق الحساب عبر جدول المطابقة وهو غير متاح حاليًا | This rule line uses mapping-based account derivation, which is not available yet |
| FIN-409-NOT-POSTED | RULE-FIN-013 | API-FIN-021, 014 | 409 | reversing a non-posted entry — raised by the same JournalEntryDomain.assertCanReverse guard as FIN-409-ALREADY-REVERSED (JournalEntryDomain.java:284), so a REVERSING template run reaches it too (API-FIN-014, RecurringTemplateService.java:249) | لا يمكن عكس قيد غير مُرحَّل | A non-posted entry cannot be reversed |
| FIN-409-ALREADY-REVERSED | RULE-FIN-013 | API-FIN-021, 014 | 409 | reversing an entry that already carries a reversal link | تم عكس هذا القيد بالفعل ولا يمكن عكسه مرة أخرى | This entry has already been reversed and cannot be reversed again |
| FIN-404-ENTRY | PLATFORM-STD | API-FIN-021, 022 | 404 | unknown entry id | القيد غير موجود | Entry not found |
| FIN-409-YEAR-DUP | PLATFORM-STD | API-FIN-023 | 409 | duplicate fiscal year code | رمز السنة المالية مستخدم بالفعل | Fiscal year code already in use |
| FIN-409-NOT-REOPENABLE | RULE-FIN-014 | API-FIN-024, 026 | 409 | period Hard Closed | الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها | The period is hard-closed and cannot be reopened |
| FIN-409-INVALID-TRANSITION | PLATFORM-STD | API-FIN-025, 027 | 409 | period not in the expected state; fiscal year already CLOSED when year-end close is re-run | لا يمكن تنفيذ هذا الانتقال من الحالة الحالية | This transition is not allowed from the current status |
| ~~FIN-403-SOD-VIOLATION~~ STRUCK | RULE-FIN-015 | — | — | UNREACHABLE since 2026-09-12 — both throw sites are gone. It was raised when the close-approver's permission set was not globally disjoint from the entry-creation permission's: `FinSeparationOfDutiesService` read SEC's user directory (XM-FIN-002, now retired) and `FiscalPeriodDomain.assertCanHardClose(...)` threw. Both were DELETED by recorded human decision as an OVER-IMPLEMENTATION: they refused the close for EVERY caller whenever ANY single user in the system held both `PERM_FIN_PERIODS_CLOSE_APPROVE` and `PERM_FIN_JOURNAL_ENTRIES_CREATE`, and no REQ, AC or RULE states that. RULE-FIN-015 (srs-fin.md:1026-1033) asks only for a DISTINCT permission "enforced through the Security module" and its `Data source` line reads DEFERRED — no FIN-side fact to read — so the rule is satisfied in full by the delivered `@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on API-FIN-026 and API-FIN-027, which is untouched. STRUCK RATHER THAN DELETED, following the `FIN-503` row's precedent in this same table (an unreachable code is struck, kept visible, and given no API/HTTP cells). ONE HONEST DIFFERENCE FROM THAT PRECEDENT: FIN-503 never existed in code, whereas the constant `FinErrorCodes.FIN_403_SOD_VIOLATION` and BOTH bundle entries (`messages.properties`, `messages_ar.properties`) were deliberately left in place by the code session, so the string is still in the build with no thrower — the message columns below are therefore the real, still-present bundle text, not a historical quotation. A session that removes the constant and the two bundle keys should delete this row's message cells with them | صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود | The close-approval permission is separate from the entry-creation permission |
| FIN-404-PERIOD | PLATFORM-STD | API-FIN-014, 017, 019, 020, 024, 025, 026, 027, 029, 031 | 404 | unknown period id — on API-FIN-029 only when the OPTIONAL `periodId` is actually supplied (omitting it stays a 200); API-FIN-031's `fromPeriodId`/`toPeriodId` already raised it before the report-404 change and are unchanged. The six ids added here were verified in source and are NOT all "unknown id" failures: API-FIN-024/025/026 resolve the path id (FiscalPeriodService.java:204); API-FIN-019 resolves the submitted `periodId` (JournalEntryService.java:174); API-FIN-014, 017 and 020 carry no period id at all and raise it when NO period's `[startDate, endDate]` covers the run/document date (JournalPostingService.java:208); API-FIN-014 additionally raises it when a REVERSING template's period has no successor inside the same fiscal year (RecurringTemplateService.java:284); API-FIN-027 raises it when the closing year has no last period or the successor year no first period (FiscalYearService.java:314, :322) | الفترة غير موجودة | Period not found |
| FIN-409-PERIODS-NOT-CLOSED | PLATFORM-STD (§10.4 precondition) | API-FIN-027 | 409 | not every period Hard Closed | يجب إغلاق كل الفترات إغلاقًا صارمًا أولًا | Every period must be hard-closed first |
| FIN-404-YEAR | PLATFORM-STD | API-FIN-014, 017, 019, 020, 021, 027, 030, 031 | 404 | unknown fiscal year id — on API-FIN-030 and API-FIN-031 the REQUIRED `fiscalYearId` is resolved first and raises this instead of the silent all-zero 200 those reports previously returned. The five ids added here were verified in source: API-FIN-019 resolves the submitted `fiscalYearId` under the docNo row lock (JournalEntryService.java:171), and every system-generated posting re-resolves the year under that same lock inside JournalPostingService.buildValidateAndPost (:152) — the single pipeline behind API-FIN-014, 017, 020, 021 and 027. API-FIN-027 raises it from two further sites of its own: an absent adjacent successor year (FiscalYearService.java:364) and an unknown path id (:371). API-FIN-023 does NOT raise it — FiscalYearService.create resolves no year | السنة المالية غير موجودة | Fiscal year not found |
| FIN-422-REMAINDER-MARKER | RULE-FIN-003, RULE-FIN-010 | API-FIN-011, 016, 017, 020 | 422 | `isRemainderFl` (DBF-FIN-103/141) disagrees with the line's/target's own REMAINDER type code, so which line is the remainder is ambiguous | علامة سطر الباقي لا تتفق مع نوع التوزيع أو مصدر المبلغ لنفس السطر | The remainder marker disagrees with the line's own distribution or amount-source type |
| FIN-422-REMAINDER-NOT-POSITIVE | RULE-FIN-010 | API-FIN-017, 020 | 422 | the remainder line's per-side difference is zero or negative — the other lines on its side already equal or exceed the opposing side (POL-FIN-005) | سطر الباقي يُحسب كفرق ويجب أن يكون موجبًا؛ السطور الأخرى تستهلك المبلغ بالكامل | The remainder line is computed as a difference and must be positive; the other lines already consume the full amount |
| FIN-400-PERIOD-NOT-IN-YEAR | RULE-FIN-017 | API-FIN-019 | 400 | submitted `periodId` belongs to a different fiscal year than the submitted `fiscalYearId` (DBF-FIN-076) | الفترة المحددة لا تتبع السنة المالية المحددة | The selected period does not belong to the selected fiscal year |
| FIN-400-DOCDATE-OUTSIDE-PERIOD | RULE-FIN-017 | API-FIN-019 | 400 | submitted `docDate` falls outside the submitted period's `[startDate, endDate]` span (DBF-FIN-080/081) | تاريخ المستند خارج نطاق الفترة المحددة | The document date falls outside the selected period |
| FIN-403-FORBIDDEN | PLATFORM-STD | every secured API (i.e. every `@PreAuthorize` on a `com.erp.fin.service.*` method — API-FIN-036 and API-FIN-037 included) | 403 | missing module/screen/action grant — **this code now REACHES THE WIRE as itself.** `com.erp.fin.security.FinForbiddenAdvisor` catches the `AccessDeniedException` raised by `@PreAuthorize` on any `com.erp.fin.service.*` method and re-raises it as `LocalizedException(Status.FORBIDDEN, FinErrorCodes.FIN_403_FORBIDDEN)`, which `GlobalExceptionHandler` renders like every other FIN error. It IS a `FinErrorCodes` constant (`FIN_403_FORBIDDEN`) and it IS in BOTH i18n bundles (`messages.properties`, `messages_ar.properties`). **Every earlier revision of this row said the opposite** — that FIN's 403 was rendered as the platform `ACCESS_DENIED` envelope, that this row was merely the catalog's *name* for that response, that the code was in no `FinErrorCodes` constant and in neither bundle, and that FIN had no `FIN-403-FORBIDDEN` on the wire. All of that is superseded and none of it is true any more. TWO BOUNDARIES, each read in source: (1) a denial raised by the Spring Security **filter chain**, before any FIN service is entered, never reaches an AOP proxy or `GlobalExceptionHandler` — it is written by the chain's `accessDeniedHandler` and still answers `SEC-403-FORBIDDEN`. That path is currently UNREACHABLE for FIN, because `SecurityConfig` (`com.erp.main.config`) authorizes with `.anyRequest().authenticated()` and declares no FIN authority rule, so every FIN permission denial is a `@PreAuthorize` denial on a FIN service and does pass through the advisor; adding a URL-level authority rule for a FIN path would change that. (2) `FIN-403-SOD-VIOLATION` is unaffected — it is a RULE-FIN-015 business failure thrown by hand as a `LocalizedException`, never an `AccessDeniedException`, so the advisor never sees it. Also note `CommonErrorCodes.ACCESS_DENIED` still exists and is still what `GlobalExceptionHandler.handleAccessDenied` emits for modules that have no forbidden advisor of their own; FIN is simply no longer one of them | لا تملك صلاحية المالية المطلوبة لهذه العملية | You do not hold the Finance permission required for this operation |
| FIN-400-INVALID-SORT | PLATFORM-STD | every search API | 400 | unrecognized sort field | حقل الترتيب غير معروف | Unrecognized sort field |
| ~~FIN-503~~ STRUCK | PLATFORM-STD (MDL unreachable) | — | — | unreachable: XM-FIN-001 is in-process `MdlLookupApi` injection, so there is no network hop to fail (and `Status` has no SERVICE_UNAVAILABLE); an invalid code raises `FIN-400-INVALID-LOOKUP`, anything else falls through to `FIN-500` | — | — |
| FIN-500 | PLATFORM-STD (infrastructure) | any | 500 | unhandled server error | حدث خطأ في الخادم | A server error occurred |

Every PLATFORM-STD row follows SEC's ADR-SEC-002 umbrella convention, cited (not re-derived).

## Alignment self-check (ALIGN) — FIN v1

```
RE-RUN AT ALIGN-BE, against the delivered code — every line below states what was actually
verified after implementation, not what was intended before it. The pre-implementation form of
this block read "PASSED ✓ — 0 findings"; that was false and is superseded here. REVISED AGAIN
2026-09-12 (final governance-state pass, after the separation-of-duties removal, the
FIN-409-NOT-ACTIVE run gate, and V30): EVERY COUNT BELOW WAS RE-MEASURED FROM THE REAL ARTIFACT
BY THAT SESSION, none carried from the previous revision, and each line names how it was taken.

TRACEABILITY      ✓ re-verified. REQ-FIN-001..046 and DBF-FIN-001..147 all defined upstream; every PHASE/SUB/atom carries traces=. Re-counted 2026-09-12: 147 unique DBF-FIN ids and 49 unique QR-FIN ids in this document (`grep -oE 'DBF-FIN-[0-9]{3}'` / `'QR-FIN-[0-9]{3}'`, sorted unique), contiguous in both cases; no id was ever renumbered. Two id sets that grew after this block was first written are still reflected everywhere: RULE-FIN-017 (srs §A5) and QR-FIN-045..049 (ALIGN-BE, for queries already implemented). === CORRECTED 2026-09-12: XM-FIN-002 IS NO LONGER A LIVE ID and must not be listed as one. It was registered at ALIGN-BE for FIN's read of SEC's SecUserDirectoryApi; that read was deleted together with FinSeparationOfDutiesService by a recorded human decision, so XM-FIN-002 is RETIRED — the id is kept, never reused and never renumbered, and survives only as a struck historical block in INT-C and INT-R. The live XM set is XM-FIN-001 alone; see CROSS-MODULE.
BINDING (§2A)     ✓ re-verified. No placeholder; every column cites a DBF; every RULE message present in ar+en. docNo is `JV-{fiscalYearCode}-{NNNNNN}`, counter per fiscalYearId, generated by a FIN-local generator in com.erp.fin (the "platform numbering engine" the pre-implementation text named does not exist and never did). The one place that phrase survived in the LIVE DATABASE — V22__fin_schema.sql:278's `COMMENT ON COLUMN FIN_JOURNAL_ENTRY.doc_no` — is corrected forward by V29__fin_comment_corrections.sql, whose replacement statement names `com.erp.fin.numbering.JournalDocNoGenerator` and the `JV-{fiscalYearCode}-{NNNNNN}` format explicitly (both of V29's two statements re-read in full today). V29 is WRITTEN BUT NOT YET APPLIED to any database — `git status --short src/main/resources/db/migration/` returns it as untracked (`??`) today — so until it runs the live comment still says "platform numbering engine". === CORRECTED 2026-09-12: V29 is NO LONGER the highest-numbered migration. `ls src/main/resources/db/migration/ | grep -oE '^V[0-9]+' | sort -t V -k2 -n | tail -1` now returns V30 (V30__fin_sys_admin_close_approve_grant.sql), also untracked and also not yet applied. The previous revision's "highest-numbered file" parenthetical is superseded; V29's unapplied status is unchanged.
MANIFEST (§4)     ✓ after correction. All 147 DBF listed, only the mandated columns. Corrected earlier and still standing: the XM count read "12 columns across 8 tables" and is 16 across 10 — re-measured today as 16 lines matching `^COMMENT ON COLUMN.*XM-FIN-001` in V22__fin_schema.sql, spanning FIN_ACCOUNT, FIN_JOURNAL_ENTRY, FIN_JOURNAL_LINE, FIN_FISCAL_YEAR, FIN_FISCAL_PERIOD, FIN_EVENT_TYPE_RULE, FIN_RULE_LINE, FIN_RECURRING_TEMPLATE, FIN_RECURRING_TEMPLATE_LINE and FIN_ALLOCATION_TARGET (a bare `grep -c XM-FIN-001` over V22 returns 18 and OVER-COUNTS — two of the hits are prose, at V22:6 and V22:482); five rows named a `_pk` column `...Id` (DBF-FIN-098/109/122/130/139) — one of them, DBF-FIN-130, colliding with DBF-FIN-140's real FK of the same name — and now match the entity. RESIDUAL, not corrected: db-script-fin.md's 14 matrix rows still describe `GENERATED ALWAYS AS IDENTITY` PKs where V22 deliberately built SEQUENCE PKs (deviation justified at V22:15-22 and noted in this plan's extraction block); 20 FK rows are modelled as scalar Long where the entity uses @ManyToOne. The (d) half — V22:240's FIN_ACCOUNT table comment omitting DBF-FIN-147 — is CLOSED by V29 (written, not applied; see SCHEMA COMMENT). The audit-width half is HALF-CLOSED and was re-measured from scratch today: AuditableEntity.createdBy/updatedBy are `length = 100` (AuditableEntity.java:26 and :32, both re-read), while the PHYSICAL schema is still split — `grep -rhoiE '(created_by|updated_by) +VARCHAR\([0-9]+\)' src/main/resources/db/migration/` returns 16 CREATED_BY + 16 UPDATED_BY at VARCHAR(100) (V16 SEC 5 · V18 MDL 2 · V22 FIN 9) and 14 + 14 at VARCHAR(255) (V1 · V2 · V6 · V8); discarding the eight V2 tables that V14__drop_legacy_security_schema.sql drops leaves 6 LIVE at 255 (CU_APP_CONFIGURATION, NOTIF_TEMPLATE, NOTIF_CHANNEL_CONFIG, NOTIF_LOG, FILE_CATEGORY, FILE_DOCUMENT), so 16 + 6 = 22 live tables — exactly the 22 classes `grep -rl "extends AuditableEntity" src/main/java/com/erp/` returns, re-counted today. Platform-wide, so still not FIN's to settle — written up in governance/project-artifacts/platform-audit-widths-and-error-localization.md.
QRC (§5)          ✓ after correction. Both directions re-run. Forward: all 49 QR ids have a real implementation; no join resolves a lookup label (zero MDL joins in any FIN @Query). Backward: four repository methods had ZERO call sites (contract rule A.2.9) and were DELETED at ALIGN-BE — FiscalPeriodRepository.existsByFiscalPeriodPkAndStatusCode, JournalEntryRepository.existsByJournalEntryPkAndStatusCode, JournalLineRepository.countByJournalEntryPk, RecurringTemplateRepository.findByIsActiveFlAndNextRunDateLessThanEqual; the first two claimed to be the "cheap pre-check" for QR-FIN-040/035, which are in fact decided by FiscalPeriodDomain.assertCanReopen and JournalEntryDomain.assertCanReverse on the loaded entity, with no query at all. Five real, called queries had no QR id and now carry QR-FIN-045..049. Three catalog cross-references corrected (QR-FIN-022 cited QR-FIN-040 for a balance, now QR-FIN-043; QR-FIN-016's table scope now matches its id definition and the code; QR-FIN-042 no longer claims to return a running balance). Re-counted 2026-09-12: 49 unique QR-FIN ids, contiguous QR-FIN-001..049. NOTE for the A.2.9 sweep: the SoD removal created a NEW dead chain, but it is in SEC, not FIN — carried below as SEC DEAD CHAIN.
API (R3)          ✓ re-measured against the controllers 2026-09-12, nothing carried over. 37 endpoints — counted by listing every `@GetMapping/@PostMapping/@PutMapping/@PatchMapping/@DeleteMapping` in each of the nine files under src/main/java/com/erp/fin/controller/ and summing: Account 4, AllocationRule 4, Dimension 5, EventTypeRule 4, FiscalPeriod 4, FiscalYear 2, JournalEntry 5, RecurringTemplate 4, Report 5 — covering exactly API-FIN-001..037. Unchanged from the previous revision's re-measurement; the run-gate and SoD changes added no endpoint and removed none. Shapes unchanged: every search is POST /<resource>/search, every deactivate is a PUT on the resource's own id path (`/{id}/deactivate`, or `/values/{id}/deactivate` for the dimension-value child), the three period transitions are PATCH, child endpoints sit on the parent's controller, and there is still NO @DeleteMapping and no activate anywhere in FIN (grep returns zero of each; re-run today). Create/update requests exclude PK/audit/system fields (docNo, statusCode, postedAt); docNo appears only in responses. === RE-COUNTED 2026-09-12, and the previous revision's figures are SUPERSEDED: 40 error codes, measured three ways and diffed pairwise with zero orphans in any direction — 40 `"FIN-*"` string literals in FinErrorCodes.java, 40 keys matching `^FIN-` in messages.properties, 40 in messages_ar.properties — 40/40/40, where the previous revision said 38/38/38. The two added since are FIN-409-NOT-ACTIVE (the run gate; FinErrorCodes.java:441) and FIN-422-INVALID-PERCENTAGE-VALUE (FinErrorCodes.java:357). THREE line references on the previous revision's text have MOVED because of those inserts and are corrected here: FIN_403_FORBIDDEN is now FinErrorCodes.java:400 (was :384), messages.properties:173 (was :172), messages_ar.properties:170 (was :169). The Error Catalog holds 41 code rows, not 39 — counted as _SECTIONS.md:378-418 inclusive and cross-checked as 41 unique codes in the first table column. Of those 41, exactly TWO are deliberately not constants: FIN-500, the infrastructure fallthrough (:418), and ~~FIN-503~~, struck (:417). ~~FIN-403-SOD-VIOLATION~~ is ALSO struck (:407) but, unlike those two, IS still a live constant and a live pair of bundle rows — that mismatch is a finding in its own right, carried below as SOD DEAD CODE. And the diff does not close in the other direction either: ONE constant has no catalog row at all — FIN-422-INVALID-PERCENTAGE-VALUE — carried below as CATALOG GAP. The previous revision's sentence "The Error Catalog holds 39 code rows, so exactly TWO are deliberately not constants" is therefore wrong twice over and is superseded by this measurement.
CROSS-MODULE      ✓ after correction, and the correction runs the OTHER WAY from the previous revision's. EXACTLY 1 XM, 1 placed, 0 mismatched, ACTIVE: XM-FIN-001 (SOFT-READ → MDL_LOOKUP_VALUE). The previous revision read "2 XM, 2 placed ... both ACTIVE" and listed XM-FIN-002 (READ → SEC's SecUserDirectoryApi); that stopped being true on 2026-09-12, when FinSeparationOfDutiesService — FIN's ONLY consumer of SecUserDirectoryApi — was deleted by a recorded human decision, together with FiscalPeriodDomain.assertCanHardClose(...). Re-measured today, not inferred: `ls src/main/java/com/erp/fin/service/FinSeparationOfDutiesService.java` returns "No such file or directory"; `grep -rn SecUserDirectoryApi src/main/java/com/erp/fin/` returns ZERO hits; and the complete set of non-com.erp.fin, non-com.erp.common imports anywhere under src/main/java/com/erp/fin/ is now exactly two lines — `import com.erp.mdl.crossmodule.LookupOptionView;` and `import com.erp.mdl.crossmodule.MdlLookupApi;`. XM-FIN-002 is RETIRED, not deleted: its id is kept and never reused, it survives as a struck historical block in INT-C and INT-R, and it binds no manifest row (it never did — it was a service-to-service read, not a column). Consumption of XM-FIN-001 is in-process Spring interface injection, never HTTP; CrossModuleBoundaryArchTest passes. Inbound stub XM-INBOUND-STUB-3 notation unchanged.
SECURITY (R7)     ✓ ORIGINAL FINDING CLOSED, fully re-measured 2026-09-12 from the files, nothing carried. 27 PERM_FIN_* constants — `grep -oE 'String (PERM_FIN_[A-Z_]+) *=' PermissionConstants.java`, sorted unique (a plain `PERM_FIN_` grep over-counts: comments mention PERM_FIN_ACCOUNTS_DELETE, which is NOT declared) — against 27 registered action rows: 26 in V24__fin_security_seed.sql's SEC_ACTION_REG VALUES block (counted per screen: FIN_ACCOUNTS 3, FIN_DIMENSIONS 2, FIN_RULES 3, FIN_RECURRING_TEMPLATES 3, FIN_ALLOCATION_RULES 3, FIN_JOURNAL_ENTRIES 3, FIN_PERIODS 4, five report screens 1 each) plus the one FIN_DIMENSIONS/UPDATE row added by V28__fin_dimensions_update_action.sql. Synthesising `PERM_<page_code>_<action_code>` from those 27 rows and `diff`ing the sorted set against the sorted constant list gives an EXACT 27/27 match with no orphan in either direction, and every one of the 27 is referenced from at least one file under src/main/java/com/erp/fin/ (checked individually today, zero unreferenced). V30 ADDS NO ACTION ROW: it is a grant only — a single INSERT INTO SEC_ROLE_ACTION_GRANT selecting SYS_ADMIN against `a.PERMISSION_CODE = 'PERM_FIN_PERIODS_CLOSE_APPROVE'` — so the 27/27 figure is unaffected by it. What V30 DOES change is reachability: V25__fin_role_grants.sql:111 deliberately excluded that one permission from SYS_ADMIN (`AND a.PERMISSION_CODE <> 'PERM_FIN_PERIODS_CLOSE_APPROVE'`) precisely because the deleted SoD service would have refused every close if one user held both codes; with that service gone the exclusion protects nothing and locks the bootstrap `admin` out of API-FIN-026/027, so V30 reverses it forward. Also corrected earlier and still standing: PERM_FIN_PERIODS_VIEW is declared (PermissionConstants.java:248) and consumed by FiscalPeriodService.java:176's @PreAuthorize behind API-FIN-033; PERM_FIN_DIMENSIONS_UPDATE (DimensionValueService.java:100) is the genuinely new one V28 both registers and grants; the FIN_ACCOUNTS ✓ sits on UPDATE, not DELETE. === @PreAuthorize RE-COUNTED 2026-09-12 AND THE PREVIOUS FIGURE CORRECTED: 42 annotations, not 43. Counted as lines matching `^[[:space:]]*@PreAuthorize\(` under src/main/java/com/erp/fin/ — AccountService 4, AllocationRuleService 4, DimensionService 2, DimensionValueService 3, EventEntryService 1, EventTypeRuleService 3, FinLookupValidationService 2, FiscalPeriodService 4, FiscalYearService 2, JournalEntryService 4, JournalPostingService 3, RecurringTemplateService 4, ReportService 5, RuleLineService 1 — 14 files, all under service/. TWO looser greps over-count and both are named so the next session does not repeat them: the bare word `@PreAuthorize` returns 58, and `@PreAuthorize(` (unanchored) returns 47, the extra 5 being javadoc `{@code @PreAuthorize(...)}` references in FiscalPeriod.java:38 and :158, FinLookupValidationService.java:44, JournalPostingService.java:73 and FiscalPeriodDomain.java:106. The previous revision's file list is also stale: it named FinSeparationOfDutiesService, which no longer exists, and the drop from 43 to 42 is exactly that file's single annotation leaving the tree.
CORE (R1)         ✓ re-verified. Layers, domain placement, error signalling (`FIN-{http}[-{SLUG}]`) and type mapping all as declared; services delegate every rule decision to a Domain companion. === RE-COUNTED 2026-09-12: 8 Domain classes, not 7 — `ls src/main/java/com/erp/fin/domain/*.java` returns AccountDomain, AllocationRuleDomain, DimensionValueDomain, EventTypeRuleDomain, FiscalPeriodDomain, FiscalYearDomain, JournalEntryDomain and RecurringTemplateDomain. RecurringTemplateDomain is NEW (untracked in the working tree today), added as the companion for the run gate; its only rule method is assertCanRun() at RecurringTemplateDomain.java:71. AllocationRuleDomain gained the matching assertCanRun() at :191. The count moved 7 → 8 for that reason and no other; FiscalPeriodDomain LOST a method in the same pass (assertCanHardClose) without losing the class.
DECISIONS         ✓ ADR-FIN-001 (carried from P2) cited and still correct as written. DEFAULTs landed since: JOURNAL_TYPE gains CLOSING/OPENING (data-only); docNo format and FIN-local generator ownership; classic reversal (the original stays POSTED and is linked to its reversal; a second reversal is rejected; nothing writes VOID); RULE-FIN-008 exempts API-FIN-027's year-end CLOSING/OPENING entries; MAPPING account derivation is rejected with FIN-422-MAPPING-UNSUPPORTED; a twelve-period fiscal year generates calendar months. No BLOCKED ADR. === ADDED 2026-09-12 — TWO RECORDED HUMAN DECISIONS, both of which change delivered behaviour and neither of which derives from any RULE-FIN-*, so both are named here rather than left implicit in the code: (1) SEPARATION OF DUTIES IS THE PERMISSION GATE AND NOTHING MORE. RULE-FIN-015 (srs-fin.md:1026-1033, re-read at those lines) requires only that the close-approval action be "gated by a permission distinct from the journal-entry-creation permission, enforced through the Security module", and its Data source line records that FIN has no field to read for it; REQ-FIN-038/AC-FIN-038 say the same. The delivered `@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` on FiscalPeriodService.hardClose and FiscalYearService.yearEndClose IS that enforcement. The previous implementation went further and enforced GLOBAL USER-SET DISJOINTNESS — it asked SEC which users held each permission and refused the close for EVERY caller whenever any single user in the system held both — which the SRS never asks for and which denied clean approvers. It was deleted. ADR-FIN-001 is unaffected by this: it excludes AMBIENT platform integration with SEC from the XM register, and the thing removed was FIN business logic reading SEC data about other users, which is why it had correctly been an XM row while it existed. (2) A DEACTIVATED TEMPLATE OR RULE MAY NOT RUN — see DEACTIVATE RUN below; likewise a decision, not a derived requirement.
ACCOUNTING §12    ✓ all 14 must-honor points still traced and re-verified: (1) RULE-FIN-006 · (2) POL-FIN-002/API-FIN-029 sign presentation · (3) RULE-FIN-007 · (4) RULE-FIN-008, now with its explicit carve-out for API-FIN-027's year-end CLOSING/OPENING entries · (5) CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE + directionCode · (6) RULE-FIN-003/010, plus FIN-422-REMAINDER-MARKER and FIN-422-REMAINDER-NOT-POSITIVE · (7) RULE-FIN-011, now CLASSIC reversal: the original stays POSTED, reversalEntryId/originalEntryId link the pair, a second reversal is rejected with FIN-409-ALREADY-REVERSED, net ledger effect zero, and no path writes VOID · (8) API-FIN-029 (balances by construction) · (9) every report QR reads POSTED lines live, no stored balance column anywhere in db-script-fin.md · (10) REQ-FIN-036/RULE for continuity · (11) RULE-FIN-009 + QR-FIN-044 dimension grouping · (12) RULE-FIN-004 · (13) RULE-FIN-016 lock + no DELETE mapping anywhere (FIN publishes no DELETE endpoint at all) · (14) POL-FIN-014, no host-specific branch anywhere in this plan
TEST PLAN         ✓ re-counted 2026-09-12, for the record only — THE TEST PHASE HAS NOT RUN and nothing below asserts that it has. governance/modules/FIN/test_gen/backend-test-plan-fin.md now carries 109 test-case ids, not 108: counted as 109 `<!-- TC:TC-FIN-nnn:START` markers and confirmed as 109 unique TC-FIN ids, contiguous TC-FIN-001..109. 108 of the 109 are IN FORCE. The arithmetic, from the plan's own header at its lines 6-9: 107 module-scope (phase TEST-PLAN-BE) + 2 integration (phase INT-XM) = 109 ids, less TC-FIN-091, RETIRED 2026-09-12 — its id deliberately kept rather than deleted so nothing renumbers, and it must NOT be counted as a coverage gap. TWO CHANGES SINCE THE PREVIOUS REVISION, both verified in the file: (a) TC-FIN-091 existed only to exercise the SEC user-directory read and was retired when that read was deleted; (b) TC-FIN-106 and TC-FIN-107 NO LONGER PIN AN OPEN DEFECT — they were FLIPPED (the plan says so at its line 24 and at :1502) and now read "a deactivated recurring template is REFUSED at run time (FIN-409-NOT-ACTIVE)" (:1449) and the same for an allocation rule (:1483), asserting the 409 rather than the old "still runs and still posts". The previous revision of this line said those two TCs "deliberately PIN THE OPEN DEFECT"; that is superseded. (c) TC-FIN-109 is new, added to cover FIN-422-INVALID-PERCENTAGE-VALUE, which had been a registered code with no test — a real gap the test session found and closed. execution-state.json's TEST-PLAN-BE and INT-XM remain PENDING and are not touched by this block.
ERROR ENVELOPE    ✓ CLOSED — by src/main/java/com/erp/fin/security/FinForbiddenAdvisor.java, re-read in full 2026-09-12. It is a `DefaultPointcutAdvisor` at `Ordered.HIGHEST_PRECEDENCE` (:57) whose pointcut matches any target class whose name starts with `com.erp.fin.service.` (:40); its interceptor catches `AccessDeniedException` from `invocation.proceed()` and re-throws `new LocalizedException(Status.FORBIDDEN, FinErrorCodes.FIN_403_FORBIDDEN)` (:54), which GlobalExceptionHandler's LocalizedException handler (:32-52) then renders through MessageSource. FIN-403-FORBIDDEN is therefore reachable on the wire, and is backed by a constant and by both bundles — all three re-grepped today AT THEIR CURRENT LINES, which have moved since the previous revision wrote them: FinErrorCodes.java:400 (was :384), messages.properties:173 (was :172), messages_ar.properties:170 (was :169). It is declared once for the module, never per endpoint and never as a feature-module @ControllerAdvice, mirroring com.erp.sec.security.SecForbiddenAdvisor. THE BOUNDARY, NAMED RATHER THAN GLOSSED, because the closure is real but not total: (1) only a denial raised INSIDE com.erp.fin.service.* is translated — a Spring Security FILTER-CHAIN denial never reaches an AOP proxy or GlobalExceptionHandler at all, being written directly by SecSecurityErrorHandler, which SecurityConfig.java:59 wires as `.accessDeniedHandler(securityErrorHandler)` and which answers SEC-403-FORBIDDEN (SecSecurityErrorHandler.java:42) — all three lines re-read today. That path is UNREACHABLE for FIN today: SecurityConfig.java:56 authorizes with `.anyRequest().authenticated()` and declares no FIN authority rule, so every FIN permission denial is in fact a @PreAuthorize denial on a FIN service. Add one URL-level authority rule for a FIN path and that stops being true. (2) Platform-wide, the shared handler's AccessDeniedException path still answers CommonErrorCodes.ACCESS_DENIED for any module without its own advisor — unchanged, and not a FIN finding. === CORRECTED 2026-09-12: the previous revision's clause (2), that "FIN-403-SOD-VIOLATION is UNAFFECTED ... raised as a LocalizedException directly (FinSeparationOfDutiesService.java:109, FiscalPeriodDomain.java:112)", is NO LONGER TRUE IN ANY PART — that file is gone, that method is gone, and `grep -rn 'FIN_403_SOD_VIOLATION' src/main/java/` returns no throw site at all. The code is unreachable; see SOD DEAD CODE.
SCHEMA COMMENT    ✓ CLOSED — by src/main/resources/db/migration/V29__fin_comment_corrections.sql, named here because this line's own prior text demanded that any closure point at the migration that closed it. Re-read in full 2026-09-12: V29 issues exactly two statements and changes no structure and no data — `COMMENT ON TABLE FIN_ACCOUNT IS 'ENT-FIN-001 Account — PRIVATE; [DBF-FIN-001..013, DBF-FIN-147]';` and a replacement `COMMENT ON COLUMN FIN_JOURNAL_ENTRY.doc_no` naming com.erp.fin.numbering.JournalDocNoGenerator and the JV format (see BINDING). The first is byte-for-byte the text db-script-fin.md:447 states, against V22__fin_schema.sql:240's `[DBF-FIN-001..013]`. V22 stays untouched and immutable, as required; the defect is corrected FORWARD, which is the only legal repair. STATED HONESTLY AND RE-CONFIRMED TODAY: V29 is WRITTEN BUT NOT YET APPLIED to any database — still untracked (`??`) in `git status --short`. This line is closed against the repository, not against a running database; if V29 is ever reverted or renumbered, reopen it. V30 has the same unapplied status but corrects no comment and does not bear on this line.
SCOPE vs SRS      ✓ ORIGINAL FINDING CLOSED — by a SPLIT decision, half built and half deliberately excluded, both recorded in srs-fin.md. BUILT: API-FIN-035, `PUT /api/v1/fin/dimensions/values/{id}/deactivate` (DimensionController.java:80), gated on the new PERM_FIN_DIMENSIONS_UPDATE (DimensionValueService.java:100), raising the new FIN-404-DIMVALUE, registered and granted by V28; and API-FIN-034, `PUT /api/v1/fin/event-rules/{id}/deactivate` (EventTypeRuleController.java:66), on the PRE-EXISTING PERM_FIN_RULES_UPDATE (EventTypeRuleService.java:100) and the PRE-EXISTING FIN-404-RULE — so it needed no migration and no new code. NOT BUILT, deliberately, and now v1 DECISIONS rather than gaps: a deactivate on the PARENT Dimension (srs-fin.md:1177, and the reasoning under B4 — no REQ, AC or RULE asks for one) and a rule-line DELETE (srs-fin.md:1235 and B4 — ENT-FIN-010 carries no active-flag column and FIN publishes no DELETE endpoint on any screen). The requirement text was narrowed WITH its reason attached, not silently deleted. A DIFFERENT, newly-surfaced SRS/code divergence is recorded below as SRS OPERATIONS — it is not this finding returning.
DOC QUOTATION     ⚠ STILL OPEN — re-verified 2026-09-12, unchanged, and structurally uncloseable. V24__fin_security_seed.sql:52-53, re-read at those exact lines today, still asserts that srs-fin.md's B4 "Actions:" lines for FIN_DIMENSIONS, FIN_RULES, FIN_RECURRING_TEMPLATES and FIN_ALLOCATION_RULES `say "DELETE (deactivate ..., modeled as UPDATE)"`. Re-measured today: `grep -c 'DELETE (deactivate' governance/modules/FIN/P1/srs-fin.md` returns 0 and `grep -c 'modeled as UPDATE' governance/modules/FIN/P1/srs-fin.md` returns 0 — the string occurs nowhere in srs-fin.md, in any spelling, and the further SRS narrowing done since has not introduced it either. V24 is applied and Flyway-checksummed, so it can NEVER be corrected at source, and a forward migration cannot amend a comment inside an earlier file; this self-check block and execution-state.json are the only mutable record. Any future session that meets V24:52-53 must treat that string as NOT srs text and re-read the real Operations/Actions lines — whose CURRENT line numbers are srs-fin.md:1177, :1235, :1281 and :1369, NOT the :1166/:1224/:1270/:1354 the previous revision of this line cited; every one of them moved when the SRS was renarrowed, which is itself the reason a quotation must never be carried by line number without re-opening the file. The CONCLUSION V24 draws from the false quotation — seed no PERM_FIN_*_DELETE rows — remains independently correct and is not in dispute; only its cited evidence is fabricated.
ERROR CAT COVER   ✓ CLOSED for the two rows it named, and re-verified against the code 2026-09-12 rather than accepted as done. FIN-404-YEAR's API column (_SECTIONS.md:410 and its P3_1 mirror) reads API-FIN-014, 017, 019, 020, 021, 027, 030, 031, and FIN-404-PERIOD's (:408 and mirror) reads API-FIN-014, 017, 019, 020, 024, 025, 026, 027, 029, 031 — note both row line numbers shifted by the FIN-409-NOT-ACTIVE row inserted at :393, and are restated here at their current values. Checked by re-grepping both constants across src/main/java/com/erp/fin/ and reading every hit: FIN_404_YEAR is thrown at ReportService.java:329, FiscalYearService.java:364 (successorOf) and :371 (findOrThrow — whose only caller is FiscalYearService.java:168, the year-end close, i.e. API-FIN-027 and NOT API-FIN-023), JournalEntryService.java:171 and JournalPostingService.java:152; FIN_404_PERIOD at RecurringTemplateService.java:284, ReportService.java:337, FiscalYearService.java:314 and :322, JournalEntryService.java:174, FiscalPeriodService.java:204 and JournalPostingService.java:208. Both columns cover every one of those paths. Report 404 behaviour re-read and correct: ReportService.assertFiscalYearExists resolves the REQUIRED fiscalYearId first on API-FIN-030/031, and trialBalance validates API-FIN-029's OPTIONAL periodId only `if (periodId != null)`. THIS LINE STAYS CLOSED ON ITS OWN TERMS — it was scoped to those two rows — but the same full-catalog sweep that re-verified it turned up a DIFFERENT coverage hole in the opposite direction, a constant with no catalog row at all; that is NOT this finding reopening and is carried separately as CATALOG GAP.
SRS OPERATIONS    ✓ CLOSED — every B1 Operations line named by the earlier revision is narrowed to what is built, each with its reason attached inline rather than silently deleted; all six re-opened and re-read 2026-09-12 AT THEIR CURRENT LINE NUMBERS, every one of which has MOVED since the previous revision recorded them (1128→1139, 1166→1177, 1224→1235, 1270→1281, 1354→1369, 1467→1484): srs-fin.md:1139 (SCR-REQ-FIN-001) reads "search, create, update, deactivate. No by-id read — deliberate v1 exclusion, see the note under B5". :1177 (SCR-REQ-FIN-002) reads "search, create (dimension — no deactivate, deliberate; see B4); search, create, deactivate (value — API-FIN-035)". :1235 (SCR-REQ-FIN-003) reads "search, create, deactivate (rule — API-FIN-034); create (line). As built there is no update and no by-id read on either, and no line delete — see B4". :1281 (SCR-REQ-FIN-004) and :1369 (SCR-REQ-FIN-005) name exactly API-FIN-012/013/014/036 and API-FIN-015/016/017/037 — everything their controllers publish. :1484 (SCR-REQ-FIN-007) reads "create (year); search — PERIODS only (API-FIN-033); open, soft-close, hard-close (period); run year-end close. There is NO fiscal-YEAR search and no by-id read of either a year or a period". SCR-REQ-FIN-006 and -008 were never affected. === UPDATED 2026-09-12: the previous revision said :1270/:1354 carry "two explicit bold caveats, that deactivate is delivered but does NOT stop the run, and that update is still not built". Re-read today, ONE of those two caveats has been REWRITTEN, not merely moved: both lines now say deactivate "is DELIVERED ... and, since 2026-09-12, it DOES stop the template/rule from running — that defect is CLOSED, see B4", while the update caveat survives as "the ONLY open half of the original gap". That matches DEACTIVATE RUN below being closed and TEMPLATE/RULE UPD below staying open, which is why this line can still close honestly.
PLATFORM I18N     ⚠ PARTIALLY CLOSED — 5 of 6 handlers localized, 1 RESIDUE STILL OPEN; unchanged in substance since the previous revision and re-read at GlobalExceptionHandler.java today (127 lines total). RESOLVING THROUGH MessageSource: handleLocalizedException (:32-52), handleValidation (:54-68), handleDataIntegrity (:89-97), handleAccessDenied (:99-106) and handleUnexpected (:108-116), all via the private resolveMessage(String, Object[]) at :118-126. The keys they need exist in BOTH bundles, re-grepped today: INTERNAL_ERROR (messages.properties:15 / messages_ar.properties:12), ACCESS_DENIED (:16 / :13), VALIDATION_ERROR (:17 / :14), DATA_INTEGRITY_VIOLATION (:18 / :15). CommonErrorCodes carries all four constants (:9 VALIDATION_ERROR, :10 INTERNAL_ERROR, :11 ACCESS_DENIED, :12 DATA_INTEGRITY_VIOLATION) and the handlers use the constants, not string literals. The INTERNAL_ERROR wording conflict WAS decided, in favour of the BUNDLE text: the wire returns messages.properties:15 "An unexpected error occurred. Please try again later." instead of the handler's former "An unexpected error occurred", so English 500 bodies did move — stated plainly rather than glossed as a no-op. OPEN RESIDUE, re-confirmed today: handleMalformedRequestBody (:79-87) still hardcodes English at :84, `.message("The request body is malformed or does not match the expected structure")`, and its own javadoc says why — it emits the SAME wire code as handleValidation (VALIDATION_ERROR, :83) but a DIFFERENT sentence, and one bundle key cannot carry two messages. So an Arabic caller still receives English for a malformed request body, and only for that. Closing it is a CONTRACT change, not a localization change: either give this response its own wire code (e.g. MALFORMED_REQUEST_BODY) with its own pair of keys, or collapse the two messages into one. Platform-wide — SEC, MDL, FIN, CU, NOTIF and FILE alike — so still not FIN's to settle. Written up in governance/project-artifacts/platform-audit-widths-and-error-localization.md.
DEACTIVATE RUN    ✓ CLOSED 2026-09-12 — by FIN-409-NOT-ACTIVE plus the two `assertCanRun()` guards, each read in source before this line was written. The defect was that a template or allocation rule deactivated through API-FIN-036/037 still ran and still posted. IT NO LONGER DOES. THE ARTIFACTS THAT CLOSED IT, named individually because this block's own standing rule requires it: (a) the new error code, `public static final String FIN_409_NOT_ACTIVE = "FIN-409-NOT-ACTIVE";` at src/main/java/com/erp/fin/exception/FinErrorCodes.java:441, with its two bundle entries (messages.properties and messages_ar.properties both carry the `FIN-409-NOT-ACTIVE` key — verified by the 40/40/40 three-way set diff under API (R3)); (b) `RecurringTemplateDomain.assertCanRun()` at src/main/java/com/erp/fin/domain/RecurringTemplateDomain.java:71-76, which throws `new LocalizedException(Status.CONFLICT, FinErrorCodes.FIN_409_NOT_ACTIVE, recurringTemplatePk)` when `!active` — RecurringTemplateDomain is itself NEW, FIN's 8th Domain class; (c) `AllocationRuleDomain.assertCanRun()` at src/main/java/com/erp/fin/domain/AllocationRuleDomain.java:191-196, the same shape with allocationRulePk; (d) the two call sites that make them live, RecurringTemplateService.java:206 (`RecurringTemplateDomain.from(template).assertCanRun();`, API-FIN-014) and AllocationRuleService.java:182 (`domain.assertCanRun();`, API-FIN-017) — both re-read today; and (e) TC-FIN-106 and TC-FIN-107, FLIPPED in backend-test-plan-fin.md to assert the 409 rather than pin the defect (:1449, :1483). Status.CONFLICT maps to HTTP 409. TWO THINGS THIS CLOSURE MUST NOT BE READ AS: first, NO RULE-FIN-* STATES THIS GATE and none was invented to pretend otherwise — RULE-FIN-006/007/008/009 govern the CONTENT of what is posted, not a template's or rule's own lifecycle, and no REQ-FIN-* or AC-FIN-* specifies it either; the catalog row at _SECTIONS.md:393 says so in its own RULE column, which reads "(no RULE — recorded human decision, 2026-09-12)", and the test plan's traceability rows for TC-FIN-106/107 repeat it. This gate therefore rests ENTIRELY on a recorded human decision, which is exactly the authority the previous revision of this line said was required, and it was obtained rather than assumed. Second, the third alternative that entry offered — removing isActiveFl from the search allow-list — was NOT taken and was not part of the decision; the flag remains searchable.
TEMPLATE/RULE UPD ⚠ STILL OPEN — a recurring template and an allocation rule CANNOT BE CORRECTED after creation. Re-measured 2026-09-12 by listing every mapping in both controllers: RecurringTemplateController publishes exactly four (POST create, POST /{id}/run, PUT /{id}/deactivate, POST /search) and AllocationRuleController exactly four (the same shape). There is no PUT /{id}, no line- or target-level endpoint of any kind (lines and targets travel inside the create body only), and the matching services expose no update method. THE PRACTICAL CONSEQUENCE HAS CHANGED FOR THE BETTER BUT THE GAP HAS NOT CLOSED: the previous revision said a typo could only be worked around by creating a replacement and deactivating the original, "which, per DEACTIVATE RUN above, does not actually stop the original from running". That second clause is now FALSE — deactivate does stop the run — so the workaround is at last sound. The gap itself is untouched: there is still no way to CORRECT a template or rule in place, only to replace it. Recorded as a KNOWN GAP WITH NO DERIVABLE REQUIREMENT: srs-fin.md:1281 and :1369 say outright that update "is still NOT built and is now the ONLY open half of the original gap", and no REQ-FIN-*, AC-FIN-* or RULE-FIN-* specifies update semantics for either aggregate (what happens to an in-flight schedule, whether past runs are re-derived, whether a target set may shrink), so no session can derive one. Needs a human to either write the requirement or record the exclusion the way the dimension and rule-line exclusions were recorded.
MIRROR DIVERGENCE ⚠ STILL OPEN, PRE-EXISTING and outside this session's scope. The two supposedly-mirrored copies of the API-FIN-019 block are still NOT identical. Re-measured 2026-09-12 by extracting each block between its own `<!-- API:API-FIN-019:START ... -->` and `:END -->` markers and diffing: SVC-API-CRUD.md:180-222 is 43 lines, P3_1/backend-execution-plan-fin.md:979-1011 is 33 lines (the P3_1 range has MOVED — the previous revision cited :977-1009), and `diff` reports 12 changed lines, 11 on the CRUD side and 1 on the P3_1 side. The substance is unchanged: a 10-line `Numbering:` paragraph (docNo format, the VARCHAR(30) width argument, the per-fiscalYearId counter, UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO, and the explicit "no platform numbering engine exists in this repo") is present ONLY in SVC-API-CRUD.md at :199-208, and the Orchestration line differs correspondingly, the package copy reading "generate docNo (FIN-local generator)" where P3_1 inlines it as "generate docNo (FIN-local generator, `JV-{fiscalYearCode}-{NNNNNN}`)". No fact contradicts the other — P3_1 carries LESS detail, not different detail — so nothing downstream is wrong today; the risk is that a future session reading only P3_1 re-derives the numbering scheme, which is exactly the failure BINDING records. NOT FIXED HERE: this session's scope is this self-check block, execution-state.json and one project-artifacts report, and the divergence sits in the API blocks, outside all three. The fix is mechanical — copy the `Numbering:` paragraph into P3_1 and re-align the Orchestration line, then re-verify byte-equality — but it must be done by a session authorized to edit those blocks. Note this ALIGN block itself IS byte-identical across both files, verified by md5 before and after this revision.
V22 HEADER COUNT  ⚠ STILL OPEN, lowest severity here and deliberately left alone. V22__fin_schema.sql:4, opened and read at that line 2026-09-12, still reads verbatim: `-- Target: POSTGRESQL_16 | 14 tables, 14 sequences | 146 DBF-IDs | 1 XM (SOFT-READ -> MDL)`. "146 DBF-IDs" has been stale since V23__fin_account_retained_earnings_flag.sql added DBF-FIN-147; the current count is 147, re-counted today. It is a HEADER COMMENT in the migration file, not a `COMMENT ON` statement, so it was never written into the database and no live object misreports anything — which is precisely why V29 deliberately did NOT touch it: V29 corrects only the two statements that ARE in the live catalog, and a forward migration cannot rewrite an earlier file's header in any case. V22 is applied and immutable, so this can never be corrected at source; it is recorded here so no future session quotes "146 DBF-IDs" as the current count. === NOTE 2026-09-12, and it is a curiosity rather than a repair: the SAME header's "1 XM (SOFT-READ -> MDL)" has become ACCIDENTALLY CORRECT AGAIN. It was accurate when V22 was written, went stale when XM-FIN-002 was registered at ALIGN-BE, and is accurate once more now that XM-FIN-002 is retired and XM-FIN-001 is the whole live set. Nothing was fixed; the world moved back. The DBF half is still wrong, so this finding stays open — and no session may cite the XM half as evidence that the header is reliable. Separately re-confirmed today: 16 `^COMMENT ON COLUMN.*XM-FIN-001` lines in V22, unchanged.
SOD DEAD CODE     ⚠ NEW OPEN FINDING — FIN-403-SOD-VIOLATION is a live constant and a live pair of bundle rows with NO THROW SITE ANYWHERE. Measured 2026-09-12, three greps, all over src/main/java/ and src/main/resources/i18n/: the constant is declared at src/main/java/com/erp/fin/exception/FinErrorCodes.java:78 (`public static final String FIN_403_SOD_VIOLATION = "FIN-403-SOD-VIOLATION";`); the message keys are live in BOTH bundles, messages.properties:142 and messages_ar.properties:139; and `grep -rn 'FIN_403_SOD_VIOLATION' src/main/java/` returns exactly TWO hits, the declaration itself and a `{@link}` javadoc reference at FinErrorCodes.java:392 — NOT ONE `throw`. Its only former throw sites were FinSeparationOfDutiesService (deleted) and FiscalPeriodDomain.assertCanHardClose (deleted with it). The Error Catalog row was struck at _SECTIONS.md:407, following the FIN-503 precedent, BUT the constant and the two bundle entries were DELIBERATELY LEFT IN PLACE by the catalog session — that is the divergence recorded here, not an accusation of oversight. WHY IT IS A FINDING AND NOT NOISE: it makes the three-way 40/40/40 code count under API (R3) include one code no caller can ever receive, so any future session diffing constants against reachable behaviour will re-discover it; and a struck catalog row beside a live constant is exactly the shape that invites someone to "restore" the rule. WHAT MUST NOT HAPPEN: nobody may re-add a throw for it. RULE-FIN-015 is satisfied by the @PreAuthorize gate alone (see DECISIONS), and re-introducing a SoD check is the precise thing FiscalPeriodDomain.java:110-117's "DO NOT RESTORE THE PREVIOUS IMPLEMENTATION" note forbids. The open question for a human is only whether to retire the constant and the two bundle rows too, or keep them as the struck row's counterpart; this session invented no answer.
SEC DEAD CHAIN    ⚠ NEW OPEN FINDING, and it is OUTSIDE FIN — reported here because FIN's change caused it, and fixed here by nobody, because it is SEC's code. Deleting FinSeparationOfDutiesService removed the only PRODUCTION caller of a three-link chain in SEC. Traced 2026-09-12 with `grep -rn findUserIdsHoldingPermission src/`, every hit read: the JPQL query `RoleActionGrantRepository.findUserIdsHoldingPermission` (src/main/java/com/erp/sec/repository/RoleActionGrantRepository.java:124) is called only by `UserService.findUserIdsHoldingPermission` (:199-203), which is called only by `SecUserDirectoryApiImpl.findUserIdsHoldingPermission` (:26-27), which implements `SecUserDirectoryApi.findUserIdsHoldingPermission` (:25) — and the ONLY remaining callers of that interface method anywhere are four assertions in src/test/java/com/erp/sec/SecCoverageIntegrationTest.java (:438, :442, :447, :452). Zero production call sites. That is an A.2.9 dead-code condition of exactly the kind this block's own QRC line deleted four FIN repository methods for — with the difference that a test still exercises it, so it is not unreachable, merely unused. NOT ACTIONED, and deliberately: this is SEC's module record, not FIN's, and FIN's ALIGN block has no authority to delete SEC code or to decide that SEC's published crossmodule contract should shrink because its only consumer went away. Note also that RoleActionGrantRepository.java:115's javadoc still names `UserService.findUserIdsHoldingPermission` as its caller under "(A.2.9)", which is true one link up but no longer true end-to-end. For a human: either keep the method as published SEC API with no current consumer (legitimate — `SecUserDirectoryApi.findContact` is in the same position, with no production consumer outside SEC today), or retire both. FIN has no stake in the answer.
CATALOG GAP       ⚠ NEW OPEN FINDING — FIN-422-INVALID-PERCENTAGE-VALUE is a registered, thrown, fully-bundled error code with NO ERROR CATALOG ROW. Measured 2026-09-12 by extracting the 41 codes in the catalog table's first column (_SECTIONS.md:378-418) and `comm`-diffing them against the 40 `"FIN-*"` literals in FinErrorCodes.java: the constants-minus-catalog set is exactly one element, FIN-422-INVALID-PERCENTAGE-VALUE. It is not a phantom — the constant is at FinErrorCodes.java:357, it IS thrown, at EventTypeRuleDomain.java:267 inside `sourcedAmount(...)` when `new BigDecimal(amountSourceValue)` raises NumberFormatException for a PERCENTAGE-sourced rule line, and both bundles carry the key (messages.properties:170, messages_ar.properties:167). `grep -n 'INVALID-PERCENTAGE' _SECTIONS.md` and the same over P3_1 both return ZERO, so the row is missing from BOTH mirrors identically — this is an omission, not a divergence. The test plan already noticed and covered it: TC-FIN-109 was added 2026-09-12 expressly to close the coverage half. What remains uncovered is the catalog half. NOT FIXED HERE because the Error Catalog table lies outside this session's scope (this block, execution-state.json and one project-artifacts report); the fix is mechanical and must be applied to BOTH mirrors — add one row reading code FIN-422-INVALID-PERCENTAGE-VALUE, RULE-FIN-010 (build half), API-FIN-020 and API-FIN-011, HTTP 422, with the trigger and the ar+en text taken from the bundles rather than reworded. Until then the API (R3) line's "41 catalog rows / 40 constants" must be read as a 40-row overlap plus two catalog-only entries and one constant-only entry, not as a superset relation.
INPUT VALIDATION  ⚠ NEW OPEN FINDING — `RuleLineCreateRequest.amountSourceValue` accepts any string, which is the whole reason FIN-422-INVALID-PERCENTAGE-VALUE is reachable at all. Read in source 2026-09-12 at src/main/java/com/erp/fin/dto/RuleLineCreateRequest.java:41-42: the field is declared `private String amountSourceValue;` under a single `@Schema(description = "Amount source value - قيمة مصدر المبلغ", example = "netAmount")` and NOTHING ELSE — no @NotBlank, no @Size, no @Pattern, no format constraint of any kind, in contrast with the neighbouring amountSourceTypeCode which carries @Size(max = 20). THE CONSEQUENCE, traced end to end: API-FIN-011 (create rule line) persists whatever arrives, including a value that can never be parsed as a decimal, on a line whose amountSourceTypeCode is PERCENTAGE. Nothing rejects it at write time. The failure surfaces only much later, at API-FIN-020 (post from event), when EventTypeRuleDomain.sourcedAmount(...) reaches `new BigDecimal(amountSourceValue)` at EventTypeRuleDomain.java:265-268 and converts the NumberFormatException into FIN-422-INVALID-PERCENTAGE-VALUE. So a configuration error committed on one screen is reported as a posting failure on another, to a different user, possibly much later — and the stored rule stays broken, because there is no update endpoint for a rule line either (FIN publishes create-only on rule lines; see SCOPE vs SRS). This is a REAL INPUT-VALIDATION GAP, not a documentation defect. NOT FIXED HERE: adding a constraint changes the API contract for API-FIN-011 (a previously-accepted body would start returning 400 VALIDATION_ERROR), and the correct constraint is conditional — amountSourceValue means a field NAME for a FIELD-sourced line and a NUMBER for a PERCENTAGE-sourced one, so a flat @Pattern is wrong and a class-level cross-field validator is a design decision no RULE-FIN-* states. For a human: either add the conditional validation at API-FIN-011 and downgrade FIN-422-INVALID-PERCENTAGE-VALUE to a defence-in-depth path, or accept late failure and say so in the SRS. This session invented neither.
RESULT            PASSED WITH FINDINGS — 9 open, 0 blocking the phase, 0 unverified lines. THE COUNT ROSE FROM 6 TO 9 AND THAT IS NOT A REGRESSION: one finding CLOSED, four were ADDED by a sweep the previous revision had not run, and the remainder carried. Line by line, because this block's own standing rule requires every movement to be named. CLOSED (1): DEACTIVATE RUN — closed by FinErrorCodes.java:441 (FIN-409-NOT-ACTIVE) plus its two bundle keys, RecurringTemplateDomain.java:71-76 and AllocationRuleDomain.java:191-196 (the two assertCanRun() guards), their call sites at RecurringTemplateService.java:206 and AllocationRuleService.java:182, and the flipped TC-FIN-106/107; it rests on a RECORDED HUMAN DECISION and on no RULE-FIN-*, which the catalog row at _SECTIONS.md:393 states in its own RULE column. CARRIED, UNCHANGED IN SUBSTANCE (4): DOC QUOTATION (V24:52-53, applied and immutable, structurally uncloseable — its cited srs line numbers refreshed today); PLATFORM I18N (residue — the malformed-request-body handler at GlobalExceptionHandler.java:79-87, which cannot be localized without a wire-contract change); TEMPLATE/RULE UPD (neither aggregate can be corrected after creation; its workaround clause corrected, since deactivate now does stop the run); MIRROR DIVERGENCE (the `Numbering:` paragraph still present only in SVC-API-CRUD.md; P3_1 range refreshed to :979-1011); V22 HEADER COUNT (`146 DBF-IDs` still stale; its XM half became accidentally correct again, which repairs nothing). ADDED (4), each verified against the real artifact before being written: SOD DEAD CODE, SEC DEAD CHAIN, CATALOG GAP, INPUT VALIDATION. THE NINE OPEN ARE THEREFORE: DOC QUOTATION, PLATFORM I18N (residue), TEMPLATE/RULE UPD, MIRROR DIVERGENCE, V22 HEADER COUNT, SOD DEAD CODE, SEC DEAD CHAIN, CATALOG GAP, INPUT VALIDATION. Of those, INPUT VALIDATION is the only one that is a defect in shipped behaviour rather than a documentation, history or dead-code divergence; SEC DEAD CHAIN is the only one outside FIN entirely. MEASUREMENTS THAT MOVED THIS REVISION, each stated on its own line above and each the measurement winning over the inherited claim: error codes 38/38/38 → 40/40/40; Error Catalog rows 39 → 41; @PreAuthorize annotations 43 → 42; XM 2 → 1; Domain classes 7 → 8; test-case ids 108 → 109 (108 in force, TC-FIN-091 retired); and every srs-fin.md Operations line number, all six of which shifted. Re-measured and UNCHANGED: 37 endpoints, 147 DBF ids, 49 QR ids, 27 PERM_FIN_* constants against 27 registered action rows, 16 XM-FIN-001 COMMENT ON COLUMN lines in V22, 22 AuditableEntity subclasses split 16/6 on audit width. ONE CLAIM INHERITED FROM THE HAND-OFF WAS CHECKED AND FOUND FALSE, and is recorded so it is not re-asserted: FiscalPeriodService.java:135 was reported as a stale javadoc still naming FinSeparationOfDutiesService and XM-FIN-002. It is NOT stale. Read at :131-135 today, it is a deliberate past-tense removal note — "A previous implementation resolved facts from SEC's user directory here ... It was removed by an explicit human decision, together with FinSeparationOfDutiesService and FIN's XM-FIN-002 dependency on SEC" — under a "Do not add a SoD check back into this body" warning. FiscalYearService.java:156 and FiscalPeriodDomain.java:110-117 carry the same deliberate note. Nothing was changed there. STANDING RULE, STRENGTHENED AGAIN: this block must NEVER be returned to "PASSED ✓ — 0 findings" while any finding above still stands. The open count must never be lowered without naming, ON THAT FINDING'S OWN LINE, the specific artifact — file and line, migration, or commit — that closed it; DEACTIVATE RUN above is the worked example of what that looks like, and the bar it sets is the bar. "Re-verified and now fine" is not a closure. A closure that rests on a human decision rather than on a stated requirement MUST say so and MUST say that no RULE-FIN-* states it, as DEACTIVATE RUN does. A closure asserted against a migration that has not been applied MUST say so, as SCHEMA COMMENT does. ADDING a finding is always permitted and needs no authority; REMOVING one is not, and a finding may be struck only by a session that RE-MEASURED it from the artifact, never by one that inherited the claim. Every line number quoted in this block was opened today; where a previously-recorded line number had moved, the line says both the old and the new value rather than silently substituting — carry that habit forward, because three separate line-reference sets drifted in a single day.
```

**Coverage — ENT/DBF → phases → QR → XM**: every ENT-FIN-001..014 appears in exactly one
DATA-DOM entity block with ≥1 QR cited under REPOSITORY OPS; every DBF-FIN-001..147
appears in the DB Alignment Manifest and its owning entity's block; XM-FIN-001 appears in
INT-C, INT-R and every lookup-backed field's manifest row, and is the whole live XM set.
XM-FIN-002 survives only as a struck historical block in INT-C and INT-R (RETIRED 2026-09-12)
and binds no manifest row — no column ever carried it.

**Coverage — RULE → API → catalog code**: RULE-FIN-001→API-FIN-002/003→
FIN-409-PARENT-NOT-LEAF-ELIGIBLE/FIN-409-HAS-CHILDREN · RULE-FIN-002→API-FIN-007→
FIN-409-DIMVALUE-DUP · RULE-FIN-003→API-FIN-011/016→FIN-409-REMAINDER-COUNT, FIN-422-REMAINDER-MARKER ·
RULE-FIN-004→API-FIN-020→FIN-409-DUPLICATE-EVENT · RULE-FIN-005→API-FIN-020→
FIN-404-NO-ACTIVE-RULE · RULE-FIN-006→API-FIN-019/020/014/017→FIN-409-UNBALANCED ·
RULE-FIN-007→(same APIs)→FIN-409-NOT-POSTABLE-ACCOUNT · RULE-FIN-008→(same)→
FIN-409-PERIOD-NOT-OPEN · RULE-FIN-009→(same)→FIN-409-INVALID-DIMENSION ·
RULE-FIN-010→API-FIN-020/014/017→FIN-422-REMAINDER-NOT-POSITIVE, FIN-422-REMAINDER-MARKER (the per-side computation itself is success-path; these two reject a distribution that leaves no positive residue, and a line whose remainder marker is ambiguous) ·
RULE-FIN-011→API-FIN-021→(no distinct code — success-path build) ·
RULE-FIN-012→API-FIN-021→(no distinct code — success-path period substitution) ·
RULE-FIN-013→API-FIN-021/014→FIN-409-NOT-POSTED, FIN-409-ALREADY-REVERSED ·
RULE-FIN-014→API-FIN-024/026→
FIN-409-NOT-REOPENABLE · RULE-FIN-015→API-FIN-026/027→(no code — satisfied by the distinct
`PERM_FIN_PERIODS_CLOSE_APPROVE` gate, exactly as the rule states it; FIN-403-SOD-VIOLATION
struck 2026-09-12 with the service-layer check that threw it) ·
RULE-FIN-016→(every posted-entry endpoint)→(enforced by omission, no code needed — no
UPDATE/DELETE mapping exists on a POSTED row) ·
RULE-FIN-017→API-FIN-019→FIN-400-PERIOD-NOT-IN-YEAR, FIN-400-DOCDATE-OUTSIDE-PERIOD.
One catalog code deliberately appears in NO line above: `FIN-409-NOT-ACTIVE` (API-FIN-014,
API-FIN-017) has no RULE-FIN-* behind it. The active gate it enforces rests on a recorded
human decision of 2026-09-12, not on stated requirement — see its Error Catalog row and
SVC-API-CRUD's API-FIN-036/037 blocks, and do not read it as pre-existing spec.

**Coverage — XM → status → blocks → workaround**: XM-FIN-001 → ACTIVE → blocks none → no
workaround needed. That is the whole live set. XM-FIN-002 → RETIRED 2026-09-12 → blocks none →
no workaround needed: `FinSeparationOfDutiesService`, the only caller, was deleted with the SoD
over-implementation, so there is no directory read left to fail.

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
**QR-FIN-019** — FIND_ONE load the template to run, by id [ENT-FIN-011, API-FIN-014]
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
**QR-FIN-035** — EXISTS original entry is POSTED and not already reversed (RULE-FIN-013) [ENT-FIN-004, API-FIN-021, API-FIN-014]
**QR-FIN-036** — FIND_ONE current open period for reversal (RULE-FIN-012) [ENT-FIN-008, API-FIN-021]
**QR-FIN-037** — FIND_ONE read one entry with lines [ENT-FIN-004, API-FIN-022]
**QR-FIN-038** — SAVE create fiscal year + periods [ENT-FIN-007, ENT-FIN-008, API-FIN-023]
**QR-FIN-039** — UPDATE open/soft-close/hard-close period [ENT-FIN-008, API-FIN-024, API-FIN-025, API-FIN-026]
**QR-FIN-040** — EXISTS period not already Hard Closed (RULE-FIN-014) [ENT-FIN-008, API-FIN-024, API-FIN-026]
**QR-FIN-041** — AGGREGATE year-end closing/opening balances [ENT-FIN-004, ENT-FIN-005, API-FIN-027]
**QR-FIN-042** — FIND_BY_CRITERIA account ledger POSTED lines; running balance accumulated in the service [ENT-FIN-005, API-FIN-028]
**QR-FIN-043** — AGGREGATE trial balance / balance sheet / income statement account balances [ENT-FIN-005, API-FIN-029, API-FIN-030, API-FIN-031]
**QR-FIN-044** — AGGREGATE dimension report [ENT-FIN-005, ENT-FIN-006, API-FIN-032]
**QR-FIN-045** — FIND_ONE the Retained Earnings account (DBF-FIN-147) [ENT-FIN-001, API-FIN-027]
**QR-FIN-046** — EXISTS dimension code unique [ENT-FIN-002, API-FIN-006]
**QR-FIN-047** — EXISTS fiscal year code unique [ENT-FIN-007, API-FIN-023]
**QR-FIN-048** — FIND_ONE next fiscal year by startDate [ENT-FIN-007, API-FIN-027]
**QR-FIN-049** — FIND_BY_CRITERIA every period of one fiscal year [ENT-FIN-008, API-FIN-023, API-FIN-027, API-FIN-014]

## XM id definitions
**XM-FIN-001** — SOFT-READ every FIN lookup-backed column → MDL_LOOKUP_VALUE [REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031]
**~~XM-FIN-002~~** — RETIRED 2026-09-12, id burned and not reused. Was: READ SEC's user→permission directory (`SecUserDirectoryApi.findUserIdsHoldingPermission`) for a global user-set-disjointness check that RULE-FIN-015 does not require; retired when `FinSeparationOfDutiesService` was deleted [REQ-FIN-037, REQ-FIN-038]

## Registry content
See `registry-exec-be-fin.md`.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: frontend-execution-plan>>>
# FRONTEND EXECUTION PLAN — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Track : frontend
Framework : react-ts-vite (profile.stack.frontend.framework) · routing react-router ·
            server-state tanstack-query · forms react-hook-form · validation zod ·
            state useState/useReducer + Context (no global store by default)
Inputs : srs (v1, PRD-approved), prd (v1), api-docs (v1, published by the backend repo),
         registry-srs (v1), registry-exec-be (v1)
Screens : 12 — SCR-FIN-001..012 · UXD : 12 — UXD-FIN-001..012 · API bound : 37 / 37
Open ADRs : 7 — erp/decisions/FIN/ (ADR-FIN-002..008, all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

## API SURFACE — FIN v1   (source: `_inputs/api-docs-fin.md` — the ONLY endpoint source)

```
ENDPOINTS   37 — API-FIN-001..037, bound to the published surface by the API ID BINDING
            annex of the api-docs (ADR-FIN-002), matched on verb + path with no shape diff.
            Envelope: every response is wrapped in ApiResponse<T> { success, data,
            error { code, message, fieldErrors[] }, timestamp }; every paged read returns
            Page<T> { totalPages, totalElements, first, last, numberOfElements, pageable,
            sort, size, number, empty }. Paging constraints (PageableBuilder): default page 0 ·
            default size 20 · maximum size 200.
            Ten reads are POST `…/search` with a `filters[] {field, operator, value}` body
            (operators EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL,
            LESS_THAN, LESS_THAN_OR_EQUAL, IN) plus sortField, sortDirection, page, size;
            the five report reads are GET with query params and are NOT paged. Per-endpoint
            request and response shapes are stated in each F2 block rather than duplicated here.
ERRORS      business codes, each already carrying its ar/en text in the module's catalog:
            FIN-400-INVALID-LOOKUP · FIN-400-INVALID-SORT · FIN-400-MISSING-FREQUENCY ·
            FIN-400-PERIOD-NOT-IN-YEAR · FIN-400-DOCDATE-OUTSIDE-PERIOD (400) ·
            FIN-403-FORBIDDEN (403) · FIN-404-ACCOUNT / -DIMENSION / -DIMVALUE / -RULE /
            -NO-ACTIVE-RULE / -TEMPLATE / -ALLOCATION-RULE / -ENTRY / -YEAR / -PERIOD (404) ·
            FIN-409-ACCOUNT-DUP / -DIMENSION-DUP / -DIMVALUE-DUP / -RULE-DUP / -YEAR-DUP (409,
            ALREADY_EXISTS) · FIN-409-HAS-CHILDREN · FIN-409-PARENT-NOT-LEAF-ELIGIBLE
            [RULE-FIN-001] · FIN-409-REMAINDER-COUNT [RULE-FIN-003] · FIN-409-DUPLICATE-EVENT
            [RULE-FIN-004] · FIN-409-UNBALANCED [RULE-FIN-006] · FIN-409-NOT-POSTABLE-ACCOUNT
            [RULE-FIN-007] · FIN-409-PERIOD-NOT-OPEN [RULE-FIN-008] · FIN-409-INVALID-DIMENSION
            [RULE-FIN-009] · FIN-409-NOT-POSTED [RULE-FIN-013] · FIN-409-ALREADY-REVERSED ·
            FIN-409-NOT-REOPENABLE [RULE-FIN-014] · FIN-409-INVALID-TRANSITION ·
            FIN-409-PERIODS-NOT-CLOSED · FIN-409-NOT-ACTIVE (409) ·
            FIN-422-MAPPING-UNSUPPORTED · FIN-422-REMAINDER-MARKER ·
            FIN-422-REMAINDER-NOT-POSITIVE [RULE-FIN-010] · FIN-422-INVALID-PERCENTAGE-VALUE
            (422) · framework codes VALIDATION_ERROR (400) and INTERNAL_ERROR (500).
            `FIN-403-SOD-VIOLATION` is struck in the module's own catalog as unreachable and
            is routed by nothing here.
            Routing is uniform across every F2 block: field validation → inline ·
            business rule → user message · unauthenticated → login · forbidden → the localized
            forbidden message · server → generic.
LOOKUPS     12 keys displayed on a FIN screen — ACCOUNT_TYPE, DEBIT_CREDIT, PERIOD_STATE,
            FISCAL_YEAR_STATUS, JOURNAL_TYPE, JOURNAL_STATUS, ACCOUNTING_EVENT_TYPE,
            ACCOUNT_DERIVATION_TYPE, AMOUNT_SOURCE_TYPE, DISTRIBUTION_TYPE,
            RECURRING_SCHEDULE_TYPE, RECURRING_FREQUENCY. FIN owns all thirteen keys and
            registers them into the lookup module (REQ-FIN-045), but **no FIN endpoint serves
            their values**: every value is runtime-loaded from the lookup module through the
            cross-module dependency each key mints — UXD-FIN-001..012, defined in
            `ui-ux-spec-fin.md` with the foreign endpoint named there (ADR-FIN-004). ONE hook
            per key, shared across every screen that shows it, long-lived cache. Every lookup
            field is a string holding the code; no enum and no union of literals is modelled
            anywhere below. PAYMENT_METHOD is registered but displayed by no FIN field in this
            version and mints nothing.
PERMISSIONS declared by the backend and read from the SRS Access summary and the backend
            registry, never redeclared here: PERM_FIN_ACCOUNTS_VIEW / _CREATE / _UPDATE ·
            PERM_FIN_DIMENSIONS_VIEW / _CREATE / _UPDATE · PERM_FIN_RULES_VIEW / _CREATE /
            _UPDATE · PERM_FIN_RECURRING_TEMPLATES_VIEW / _CREATE / _UPDATE ·
            PERM_FIN_ALLOCATION_RULES_VIEW / _CREATE / _UPDATE ·
            PERM_FIN_JOURNAL_ENTRIES_VIEW / _CREATE / _REVERSE · PERM_FIN_PERIODS_VIEW /
            _CREATE / _UPDATE / _CLOSE_APPROVE · PERM_FIN_ACCOUNT_LEDGER_VIEW ·
            PERM_FIN_TRIAL_BALANCE_VIEW · PERM_FIN_BALANCE_SHEET_VIEW ·
            PERM_FIN_INCOME_STATEMENT_VIEW · PERM_FIN_DIMENSION_REPORTS_VIEW.
            No FIN endpoint publishes the caller's own permission set: the screen gate is the
            security module's effective menu (ADR-FIN-005), and no `PERM_*` name is composed
            at runtime.
```

### Reconciliation against the SRS — run once, before any F-content

- **Every REQ that needs an endpoint has one.** REQ-FIN-001..043 map onto API-FIN-001..037
  with no gap; the mapping is the traces of the F2 blocks below. REQ-FIN-044 and REQ-FIN-045
  are onboarding acts with no screen in the SRS traceability matrix — the first is what makes
  the menu gate of SEC-FE resolve at all, the second is what makes the lookup hooks of F2
  return anything, and both are cited where they are depended on rather than given a screen
  they do not have. REQ-FIN-046 is covered by the drill-down links of SCR-FIN-008/009/010/011.
- **Every documented endpoint maps to a REQ.** All 37 are bound; none is unknown and none is
  used without a REQ behind it.
- **Naming and shape differences** — none. Every planned verb and path is the published verb
  and path (ADR-FIN-002's annex). What the registry lags by five ids is a registry gap, not a
  surface difference.
- **Operations the SRS names with no published endpoint** — template update, allocation-rule
  update, fiscal-year search, the by-id reads of account / template / allocation rule / year /
  period, the rule-line and target deletes, and the parent-dimension deactivate. None is
  required by a `REQ-*`, so none is breaking; each is omitted rather than faked (ADR-FIN-006).
- **Endpoints published but not called by this frontend** — API-FIN-020 alone, the
  event-sourced build a host system calls over the platform's in-process module interface
  (ADR-FIN-007). It is bound and blocked out in F2, and its entries are seen on SCR-FIN-006.
- **One screen's form differs from its SRS Part B input list** — SCR-FIN-006 takes
  `fiscalYearId` as an input (B3 lists neither it nor its absence; the request requires it and
  RULE-FIN-017 reads it) and holds `journalTypeCode` in the form model as the fixed value
  `MANUAL` (B3 marks it system-set; the request requires it). Both resolve against SRS A3 and
  RULE-FIN-017 rather than against B3's prose — ADR-FIN-008. The other eleven screens match
  their B3 list exactly.
- **Nothing is invented.** No value absent from the api-docs appears in this plan, and no
  lookup value, permission name, route or component is derived from anything but the SRS, the
  api-docs and the profile's own stack.

## EXECUTION PLAN INDEX — FIN v1 — frontend-execution-plan-fin.md

| # | Phase | Split | Blocks |
|---|---|---|---|
| 1 | F1 — Models & Types | per screen (12 SCR ≥ 5) | 12 SUB |
| 2 | F2 — Data Hooks | per screen | 12 SUB |
| 3 | F3 — Forms & Validators | per screen | 12 SUB |
| 4 | F4 — Screens & Routes | per screen | 12 SUB |
| 5 | SEC-FE | never split | level-1 only |
| 6 | ALIGN-FE | never split | level-1 only |

**SCREEN REGISTRY**

| SCR | Name (ar / en) | Page code | Container pattern | Owning ENT |
|---|---|---|---|---|
| SCR-FIN-001 | شجرة الحسابات / Chart of accounts | FIN_ACCOUNTS | TREE_MASTER_DETAIL | ENT-FIN-001 الحساب / Account |
| SCR-FIN-002 | تعريف الأبعاد وقيمها / Dimension definition & values | FIN_DIMENSIONS | TREE_MASTER_DETAIL | ENT-FIN-002 البُعد / Dimension (+ ENT-FIN-003 قيمة البُعد / DimensionValue) |
| SCR-FIN-003 | قواعد المحرك / Engine rules | FIN_RULES | FULL_PAGE | ENT-FIN-009 قاعدة نوع الحدث / EventTypeRule (+ ENT-FIN-010 سطر القاعدة / RuleLine) |
| SCR-FIN-004 | قوالب متكررة/عكسية / Recurring / reversing templates | FIN_RECURRING_TEMPLATES | FULL_PAGE | ENT-FIN-011 قالب متكرر/عكسي / RecurringTemplate (+ ENT-FIN-012 سطر القالب / TemplateLine) |
| SCR-FIN-005 | قواعد التوزيع / Allocation rules | FIN_ALLOCATION_RULES | FULL_PAGE | ENT-FIN-013 قاعدة توزيع / AllocationRule (+ ENT-FIN-014 هدف التوزيع / AllocationTarget) |
| SCR-FIN-006 | قيود اليومية / Journal entries | FIN_JOURNAL_ENTRIES | FULL_PAGE | ENT-FIN-004 رأس قيد اليومية / JournalEntry (+ ENT-FIN-005, ENT-FIN-006) |
| SCR-FIN-007 | الفترات والسنوات المالية / Fiscal periods & years | FIN_PERIODS | TREE_MASTER_DETAIL | ENT-FIN-007 السنة المالية / FiscalYear (+ ENT-FIN-008 الفترة المحاسبية / FiscalPeriod) |
| SCR-FIN-008 | دفتر الحساب / Account ledger | FIN_ACCOUNT_LEDGER | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-009 | ميزان المراجعة / Trial balance | FIN_TRIAL_BALANCE | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-010 | الميزانية العمومية / Balance sheet | FIN_BALANCE_SHEET | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-011 | قائمة الدخل / Income statement | FIN_INCOME_STATEMENT | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 سطر قيد اليومية / JournalLine (live-derived) |
| SCR-FIN-012 | تقارير الأبعاد / Dimension reports | FIN_DIMENSION_REPORTS | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005, ENT-FIN-006 (live-derived) |

Twelve screens, so every `sub_bearing` phase splits per screen (threshold: SCR count ≥ 5), and
every SUB id is phase-qualified — `SUB:F1-SCR-FIN-006` and `SUB:F2-SCR-FIN-006` are distinct
blocks for the same screen under different phases.

<!-- PHASE:F1:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 1 — F1 — Models & Types

Per `ENT-*` (from the response DTOs of the api-docs) and per `SCR-*`: the source DTO with each
property's type and read-only / system-only / lookup status, then the screen's search model,
form model and container. Lookup fields are strings holding the code — all LOV values are
runtime-loaded from the lookup module (`profile.conventions.lookups`, ADR-FIN-004) — and no
enum is modelled anywhere below. Both names are carried per language (ar, en). No internal or
tenant identifier is modelled, and nothing is modelled that the api-docs do not return.

<!-- SUB:F1-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F1 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F1-MODEL — ENT-FIN-001 — الحساب / Account
Source DTO   : `AccountResponse` (read) · `AccountCreateRequest` · `AccountUpdateRequest` (write)
  accountPk            : number · read-only (PK) · system-only
  code                 : string · maxLength 30 · required on create, **read-only on edit**
                         (`AccountUpdateRequest` does not carry it — the chart code is immutable)
  nameAr               : string · required · maxLength 200
  nameEn               : string · required · maxLength 200
  accountTypeCode      : string · required on create · maxLength 20 · lookup — `ACCOUNT_TYPE`
                         code held as a string (UXD-FIN-001); **read-only on edit**, absent
                         from the update request
  natureCode           : string · required on create · maxLength 10 · lookup — `DEBIT_CREDIT`
                         code held as a string (UXD-FIN-002); **read-only on edit**
  parentAccountId      : number · optional on create (omitted for a root) · **read-only on edit**
  isLeafFl             : boolean · optional on create, required on update — the only field the
                         update request carries besides the two names
  isActiveFl           : boolean · read-only — flipped only by API-FIN-004
  isRetainedEarningsFl : boolean · read-only · system-only — the published DTO states it is
                         never settable through the account APIs
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-SCREEN — SCR-FIN-001
Search model : filters — code : string · LIKE · nameAr/nameEn : string · LIKE ·
               accountTypeCode : string · EXACT (the code, from the shared UXD-FIN-001 hook) ·
               isActiveFl : boolean · EXACT
               paging + sort — page, size, sortField, sortDirection, all inside the one
               `AccountSearchRequest` object per `Page<T>`
Form model   : create — code, nameAr, nameEn, accountTypeCode, natureCode (required),
                        parentAccountId, isLeafFl (optional)
               edit   — nameAr, nameEn, isLeafFl (required); every other field read-only
               excluded system fields: accountPk, isActiveFl, isRetainedEarningsFl, audit fields
Container    : TREE_MASTER_DETAIL
The tree is built on the client from `parentAccountId` over the rows the search returns; no
endpoint returns a nested tree and none is invented. Nothing is modelled that the api-docs do
not return, and no lookup is modelled as an enum — both code fields are plain strings.

<!-- SUB:F1-SCR-FIN-001:END -->

<!-- SUB:F1-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F1 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F1-MODEL — ENT-FIN-002 — البُعد / Dimension
Source DTO   : `DimensionResponse` (read) · `DimensionCreateRequest` (write)
  dimensionPk : number · read-only (PK) · system-only
  code        : string · required on create · maxLength 30
  nameAr      : string · required on create · maxLength 150
  nameEn      : string · required on create · maxLength 150
  isActiveFl  : boolean · read-only — and never written at all: no endpoint sets it on the
                parent dimension (SRS §B4, ADR-FIN-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-003 — قيمة البُعد / DimensionValue
Source DTO   : `DimensionValueResponse` (read) · `DimensionValueCreateRequest` (write)
  dimensionValuePk : number · read-only (PK) · system-only
  dimensionId      : number · read-only on the form — it is the path id of API-FIN-007, taken
                     from the selected parent, never typed
  code             : string · required on create · maxLength 30 — unique within the dimension
  nameAr           : string · required on create · maxLength 150
  nameEn           : string · required on create · maxLength 150
  sortOrder        : number · required on create
  isActiveFl       : boolean · read-only — flipped only by API-FIN-035
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-SCREEN — SCR-FIN-002
Search model : dimension filters — code : string · LIKE
               value filters — code : string · LIKE · dimensionId : number · EXACT (set from
               the selected parent, not typed)
               paging + sort inside each of `DimensionSearchRequest` and
               `DimensionValueSearchRequest`
Form model   : dimension — code, nameAr, nameEn (all required, create only)
               value — code, nameAr, nameEn, sortOrder (all required, create only)
               excluded system fields: both PKs, both isActiveFl, the audit fields
               read-only on edit: not applicable — neither resource has an update endpoint
Container    : TREE_MASTER_DETAIL
No enum is modelled: this screen defines the values other screens' dimension selects read, and
holds no lookup code of its own.

<!-- SUB:F1-SCR-FIN-002:END -->

<!-- SUB:F1-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F1 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F1-MODEL — ENT-FIN-009 — قاعدة نوع الحدث / EventTypeRule
Source DTO   : `EventTypeRuleResponse` (read) · `EventTypeRuleCreateRequest` (write)
  eventTypeRulePk : number · read-only (PK) · system-only
  eventTypeCode   : string · required on create · maxLength 50 · lookup —
                    `ACCOUNTING_EVENT_TYPE` code held as a string (UXD-FIN-007)
  nameAr, nameEn  : string · required on create · maxLength 150
  isActiveFl      : boolean · read-only — flipped only by API-FIN-034
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-010 — سطر القاعدة / RuleLine
Source DTO   : `RuleLineResponse` (read) · `RuleLineCreateRequest` (write)
  ruleLinePk                : number · read-only (PK) · system-only
  eventTypeRuleId           : number · read-only — the path id of API-FIN-011
  lineNo                    : number · read-only · system-assigned
  accountDerivationTypeCode : string · required · maxLength 20 · lookup —
                              `ACCOUNT_DERIVATION_TYPE` (UXD-FIN-008)
  accountDerivationValue    : string · required — read per the derivation type: a constant
                              account code, an event field name, or a mapping-set key
  amountSourceTypeCode      : string · required · maxLength 20 · lookup — `AMOUNT_SOURCE_TYPE`
                              (UXD-FIN-009)
  amountSourceValue         : string · optional in the DTO; required unless the amount source
                              type is REMAINDER (SRS ENT-FIN-010)
  directionCode             : string · required · maxLength 10 · lookup — `DEBIT_CREDIT`
                              (UXD-FIN-002)
  distributionTypeCode      : string · required · maxLength 15 · lookup — `DISTRIBUTION_TYPE`
                              (UXD-FIN-010)
  isRemainderFl             : boolean · optional in the DTO, governed by RULE-FIN-003
  createdAt                 : date-time · read-only · system-only
### F1-SCREEN — SCR-FIN-003
Search model : filters — eventTypeCode : string · EXACT (from the UXD-FIN-007 hook) ·
               isActiveFl : boolean · EXACT
               paging + sort inside `EventTypeRuleSearchRequest`
Form model   : rule — eventTypeCode, nameAr, nameEn (required, create only)
               line — accountDerivationTypeCode, accountDerivationValue, amountSourceTypeCode,
                      directionCode, distributionTypeCode (required); amountSourceValue
                      (required unless REMAINDER); isRemainderFl (boolean)
               excluded system fields: both PKs, eventTypeRuleId, lineNo, isActiveFl, createdAt
               read-only on edit: not applicable — neither the rule nor the line has an update
               endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The rule's lines are NOT part of the create request: `EventTypeRuleCreateRequest` carries the
header alone and each line is a separate API-FIN-011 call. The form model reflects that — a
rule is created first and its lines added to it — rather than promising a single submission
the surface does not accept. Five lookup fields, five strings, no enum.

<!-- SUB:F1-SCR-FIN-003:END -->

<!-- SUB:F1-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F1 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F1-MODEL — ENT-FIN-011 — قالب متكرر/عكسي / RecurringTemplate
Source DTO   : `RecurringTemplateResponse` (read) · `RecurringTemplateCreateRequest` (write)
  recurringTemplatePk : number · read-only (PK) · system-only
  nameAr, nameEn      : string · required on create · maxLength 150
  scheduleTypeCode    : string · required on create · maxLength 15 · lookup —
                        `RECURRING_SCHEDULE_TYPE` (UXD-FIN-011)
  frequencyCode       : string · optional in the DTO · maxLength 15 · lookup —
                        `RECURRING_FREQUENCY` (UXD-FIN-012); required when the schedule type
                        is RECURRING (SRS ENT-FIN-011), which the server answers with
                        `FIN-400-MISSING-FREQUENCY`
  startDate           : date · required on create
  nextRunDate         : date · read-only · system-maintained — it advances after each run
  endDate             : date · optional on create
  isActiveFl          : boolean · read-only — flipped only by API-FIN-036
  lineCount           : number · read-only · derived by the server from the lines it returns
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-012 — سطر القالب المتكرر / RecurringTemplateLine
Source DTO   : `RecurringTemplateLineResponse` (read) · `RecurringTemplateLineCreateRequest`
  recurringTemplateLinePk : number · read-only (PK) · system-only
  recurringTemplateId     : number · read-only · system-only
  lineNo                  : number · read-only · system-assigned
  accountId               : number · required
  amount                  : number · required — always positive; the direction carries the sign
  directionCode           : string · required · maxLength 10 · lookup — `DEBIT_CREDIT`
                            (UXD-FIN-002)
  dimensionValueId        : number · optional — ONE per line, the §9.3.3 simplification
  createdAt               : date-time · read-only · system-only
### F1-SCREEN — SCR-FIN-004
Search model : filters — nameAr/nameEn : string · LIKE · scheduleTypeCode : string · EXACT ·
               isActiveFl : boolean · EXACT
               paging + sort inside `RecurringTemplateSearchRequest`
Form model   : create — nameAr, nameEn, scheduleTypeCode, startDate, lines[] (required);
                        frequencyCode (required when RECURRING), endDate (optional)
               lines[] — accountId, amount, directionCode (required); dimensionValueId (optional)
               excluded system fields: every PK, recurringTemplateId, lineNo, nextRunDate,
               isActiveFl, lineCount, createdAt, audit fields
               read-only on edit: not applicable — no update endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The template and its lines are ONE submission — `RecurringTemplateCreateRequest` carries
`lines[]` — unlike SCR-FIN-003, whose lines are separate calls. `lineCount` is modelled as
read-only and never computed on the client, because the server derives it from the list it
returns.

<!-- SUB:F1-SCR-FIN-004:END -->

<!-- SUB:F1-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F1 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F1-MODEL — ENT-FIN-013 — قاعدة توزيع / AllocationRule
Source DTO   : `AllocationRuleResponse` (read) · `AllocationRuleCreateRequest` (write)
  allocationRulePk : number · read-only (PK) · system-only
  nameAr, nameEn   : string · required on create · maxLength 150
  sourceAccountId  : number · required on create — the balance being distributed
  isActiveFl       : boolean · read-only — flipped only by API-FIN-037
  targetCount      : number · read-only · derived by the server from the targets it returns
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-014 — هدف التوزيع / AllocationTarget
Source DTO   : `AllocationTargetResponse` (read) · `AllocationTargetCreateRequest` (write)
  allocationTargetPk   : number · read-only (PK) · system-only
  allocationRuleId     : number · read-only · system-only
  lineNo               : number · read-only · system-assigned
  targetAccountId      : number · required
  dimensionValueId     : number · optional — ONE per target
  distributionTypeCode : string · required · maxLength 15 · lookup — `DISTRIBUTION_TYPE`
                         (UXD-FIN-010)
  distributionValue    : number · optional in the DTO; required unless the distribution type
                         is REMAINDER (SRS ENT-FIN-014)
  isRemainderFl        : boolean · optional in the DTO, governed by RULE-FIN-003
### F1-SCREEN — SCR-FIN-005
Search model : filters — nameAr/nameEn : string · LIKE · sourceAccountId : number · EXACT ·
               isActiveFl : boolean · EXACT
               paging + sort inside `AllocationRuleSearchRequest`
Form model   : create — nameAr, nameEn, sourceAccountId, targets[] (required)
               targets[] — targetAccountId, distributionTypeCode (required); dimensionValueId,
                           distributionValue, isRemainderFl (optional per the DTO, constrained
                           by RULE-FIN-003 and by the distribution type)
               excluded system fields: every PK, allocationRuleId, lineNo, isActiveFl,
               targetCount, audit fields
               read-only on edit: not applicable — no update endpoint (ADR-FIN-006)
Container    : FULL_PAGE
The rule and its targets are ONE submission. No model holds a computed allocation amount: the
distribution is produced by the server at run time from the source account's balance at that
moment, and the remainder target's amount is a difference RULE-FIN-010 computes, never a
percentage the client could anticipate.

<!-- SUB:F1-SCR-FIN-005:END -->

<!-- SUB:F1-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F1 · SCR-FIN-006 — قيود اليومية / Journal entries

### F1-MODEL — ENT-FIN-004 — رأس قيد اليومية / JournalEntry
Source DTO   : `JournalEntryResponse` (read) · `JournalEntryCreateRequest` (write)
  journalEntryPk  : number · read-only (PK) · system-only
  docNo           : string · read-only · system-only — generated on first save, immutable after
  docDate         : date · required on create
  fiscalYearId    : number · required on create — B3 lists it as neither an input nor a system
                    field; the published request requires it and RULE-FIN-017 reads it
                    (ADR-FIN-008)
  periodId        : number · required on create
  journalTypeCode : string · required on create · maxLength 20 · lookup — `JOURNAL_TYPE`
                    (UXD-FIN-005). On this form it is the fixed value `MANUAL`, held in the
                    model and rendered read-only (ADR-FIN-008)
  statusCode      : string · read-only · lookup — `JOURNAL_STATUS` (UXD-FIN-006); set by the
                    posting pipeline, never by a form
  eventReference  : string · read-only — present only on an event-sourced entry
  originalEntryId : number · read-only — set on a reversal
  reversalEntryId : number · read-only — set on the original once reversed
  descriptionAr, descriptionEn : string · optional on create
  postedAt        : date-time · read-only · system-only
  lineCount       : number · read-only · derived
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-005 — سطر قيد اليومية / JournalLine
Source DTO   : `JournalLineResponse` (read) · `JournalLineCreateRequest` (write)
  journalLinePk  : number · read-only (PK) · system-only
  journalEntryId : number · read-only · system-only
  lineNo         : number · read-only · system-assigned
  accountId      : number · required
  amount         : number · required — always positive
  directionCode  : string · required · maxLength 10 · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
  isRemainderFl  : boolean · read-only on this screen — the engine sets it on a built entry;
                   `JournalLineCreateRequest` does not carry it
  descriptionAr, descriptionEn : string · optional
  createdAt      : date-time · read-only · system-only
### F1-MODEL — ENT-FIN-006 — بُعد سطر القيد / JournalLineDimension
Source DTO   : `JournalLineDimensionResponse` (read) · `JournalLineDimensionCreateRequest`
  journalLineDimensionPk, journalLineId : number · read-only · system-only
  dimensionId      : number · required when a dimension is used
  dimensionValueId : number · required with it
### F1-SCREEN — SCR-FIN-006
Search model : filters — docNo : string · LIKE · docDate : DATE_RANGE · periodId : number ·
               EXACT · statusCode : string · EXACT · journalTypeCode : string · EXACT
               paging + sort inside `JournalEntrySearchRequest`; page and size are part of the
               same object and never independent state
Form model   : create — docDate, fiscalYearId, periodId, journalTypeCode (fixed `MANUAL`,
                        read-only), lines[] (required); descriptionAr, descriptionEn (optional)
               lines[] — accountId, amount, directionCode (required); descriptionAr,
                         descriptionEn, dimensions[] (optional)
               dimensions[] — dimensionId, dimensionValueId (both required together)
               excluded system fields: every PK, docNo, statusCode, eventReference,
               originalEntryId, reversalEntryId, postedAt, lineCount, isRemainderFl, audit fields
               read-only on edit: the whole entry — a POSTED entry is locked (RULE-FIN-016) and
               this screen has no edit mode at all
Container    : FULL_PAGE
No DRAFT is modelled as a stored state a user can return to: SRS §A7 makes DRAFT transient and
a failed build is never written. `isRemainderFl` is read on a built entry and never written by
this form.

<!-- SUB:F1-SCR-FIN-006:END -->

<!-- SUB:F1-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F1 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F1-MODEL — ENT-FIN-007 — السنة المالية / FiscalYear
Source DTO   : `FiscalYearResponse` (read) · `FiscalYearCreateRequest` (write)
  fiscalYearPk : number · read-only (PK) · system-only
  code         : string · required on create · maxLength 10
  startDate    : date · required on create
  endDate      : date · required on create
  periodCount  : number · required on create — an input to generation, returned on the response
  statusCode   : string · read-only · lookup — `FISCAL_YEAR_STATUS` (UXD-FIN-004)
  isActiveFl   : boolean · read-only
  periods      : FiscalPeriodResponse[] · read-only — the generated periods, returned with the
                 year by API-FIN-023
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — ENT-FIN-008 — الفترة المحاسبية / FiscalPeriod
Source DTO   : `FiscalPeriodResponse` (read) — no write DTO: a period is generated, never typed
  fiscalPeriodPk : number · read-only (PK) · system-only
  fiscalYearId   : number · read-only — also the field year ids are discovered from, since no
                   fiscal-year search is published (ADR-FIN-006)
  periodNo       : number · read-only · generated
  nameAr, nameEn : string · read-only · generated (month names for a twelve-period year,
                   "الفترة N" / "Period N" otherwise)
  startDate, endDate : date · read-only · generated
  statusCode     : string · read-only · lookup — `PERIOD_STATE` (UXD-FIN-003); changed only by
                   API-FIN-024, API-FIN-025, API-FIN-026
  closedBy       : string · read-only — the approving principal, set at hard-close
  closedAt       : date-time · read-only — set at hard-close
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-MODEL — YearEndCloseResponse (the year-end close result)
  closingEntry : JournalEntryResponse · read-only — the closing entry, modelled by the
                 SCR-FIN-006 entry model above and rendered through the same components
  openingEntry : JournalEntryResponse · read-only — the next year's opening entry
### F1-SCREEN — SCR-FIN-007
Search model : filters — fiscalYearId : number · EXACT · statusCode : string · EXACT — both
               OPTIONAL; omitting the year is a legitimate "all periods" request
               paging + sort inside `FiscalPeriodSearchRequest`
Form model   : create year — code, startDate, endDate, periodCount (all required)
               period actions — no form: open, soft-close and hard-close are path-id calls
               with no body
               excluded system fields: every PK, both statusCode, isActiveFl, periodNo, the
               generated names and dates, closedBy, closedAt, audit fields
               read-only on edit: not applicable — neither resource has an update endpoint
Container    : TREE_MASTER_DETAIL
The year list is derived from the distinct `fiscalYearId` of the period rows plus the year
API-FIN-023 returns on creation; no year-list model is invented on top of an endpoint that
does not exist.

<!-- SUB:F1-SCR-FIN-007:END -->

<!-- SUB:F1-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F1 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F1-MODEL — AccountLedgerResponse — دفتر الحساب / Account ledger
Source DTO   : `AccountLedgerResponse` (read only — this screen writes nothing)
  accountId, accountCode        : number, string · read-only
  accountNameAr, accountNameEn  : string · read-only
  accountTypeCode               : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001)
  natureCode                    : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
  fromDate, toDate              : date · read-only — echoed from the request
  dimensionId, dimensionValueId : number · read-only — echoed from the request
  debitTotal, creditTotal       : number · read-only
  closingBalance                : number · read-only
  rows[]                        : AccountLedgerRowResponse —
    journalEntryId : number · read-only — the link target on SCR-FIN-006
    docNo          : string · read-only
    docDate        : date · read-only
    journalTypeCode: string · read-only · lookup — `JOURNAL_TYPE` (UXD-FIN-005)
    eventReference : string · read-only — the end of the REQ-FIN-046 chain
    journalLineId, lineNo : number · read-only
    amount         : number · read-only
    directionCode  : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    signedAmount   : number · read-only
    runningBalance : number · read-only — computed by the server, never accumulated on the client
    descriptionAr, descriptionEn : string · read-only
### F1-SCREEN — SCR-FIN-008
Search model : query params — accountId : number · required · fromDate, toDate : date ·
               DATE_RANGE · dimensionId, dimensionValueId : number · EXACT — all five on the
               query string of a GET, so the report's address IS its filter
Form model   : none — a read-only report (SRS B3 "not applicable")
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`runningBalance` is modelled as a server field and is never recomputed client-side: the plan's
own accumulation could disagree with the ledger, which is exactly the class of defect
POL-FIN-009 exists to remove. This report is not paged — the endpoint returns the rows of the
requested range, and no `Page<T>` envelope appears in its response.

<!-- SUB:F1-SCR-FIN-008:END -->

<!-- SUB:F1-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F1 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F1-MODEL — TrialBalanceResponse — ميزان المراجعة / Trial balance
Source DTO   : `TrialBalanceResponse` (read only)
  periodId            : number · read-only — echoed from the request
  accountTypeCode     : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001)
  totalDebitBalance   : number · read-only
  totalCreditBalance  : number · read-only
  balanced            : boolean · read-only — the property REQ-FIN-040 asserts
  rows[]              : AccountBalanceRowResponse —
    accountId, accountCode : number, string · read-only
    accountNameAr, accountNameEn : string · read-only
    accountTypeCode : string · read-only · lookup (UXD-FIN-001)
    natureCode      : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    debitTotal, creditTotal, debitBalance, creditBalance, signedBalance : number · read-only
### F1-SCREEN — SCR-FIN-009
Search model : query params — periodId : number · EXACT · optional · accountTypeCode : string ·
               EXACT · optional. Both live in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`balanced` is the server's assertion and is modelled as such; the screen renders it and never
derives it by comparing the two totals itself. `AccountBalanceRowResponse` is shared with
SCR-FIN-010 and SCR-FIN-011 and is modelled once.

<!-- SUB:F1-SCR-FIN-009:END -->

<!-- SUB:F1-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F1 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F1-MODEL — BalanceSheetResponse — الميزانية العمومية / Balance sheet
Source DTO   : `BalanceSheetResponse` (read only)
  fiscalYearId : number · read-only — echoed from the request
  asOfDate     : date · read-only — echoed from the request
  groups[]     : AccountBalanceGroupResponse —
    accountTypeCode : string · read-only · lookup — `ACCOUNT_TYPE` (UXD-FIN-001); the section
    groupTotal      : number · read-only
    rows[]          : AccountBalanceRowResponse — the same row model as SCR-FIN-009, including
                      natureCode · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
### F1-SCREEN — SCR-FIN-010
Search model : query params — fiscalYearId : number · EXACT · **required** ·
               asOfDate : date · optional cut-off. Both in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
The grouping is the server's: `groups[]` arrives already keyed by account type with its total,
and no client-side grouping or subtotal is modelled. The continuity REQ-FIN-041 asserts is a
property of the posted data, not of this model — the opening balances are ordinary posted
lines of the year-end close entries.

<!-- SUB:F1-SCR-FIN-010:END -->

<!-- SUB:F1-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F1 · SCR-FIN-011 — قائمة الدخل / Income statement

### F1-MODEL — IncomeStatementResponse — قائمة الدخل / Income statement
Source DTO   : `IncomeStatementResponse` (read only)
  fiscalYearId             : number · read-only — echoed from the request
  fromPeriodId, toPeriodId : number · read-only — echoed from the request
  fromDate, toDate         : date · read-only — derived by the server from those two periods
  netResult                : number · read-only
  groups[]                 : AccountBalanceGroupResponse — accountTypeCode (lookup,
                             UXD-FIN-001) · groupTotal · rows[] (AccountBalanceRowResponse,
                             natureCode lookup UXD-FIN-002)
### F1-SCREEN — SCR-FIN-011
Search model : query params — fiscalYearId : number · EXACT · **required** ·
               fromPeriodId, toPeriodId : number · EXACT · optional. All three in the route's
               search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
`fromDate`/`toDate` are modelled as read-only server output, not as inputs: the request takes
period ids and the server translates them into the date bounds those periods span. A statement
of zeros for a freshly closed year is a correct result (REQ-FIN-042), and nothing in this model
treats it as an absence of data.

<!-- SUB:F1-SCR-FIN-011:END -->

<!-- SUB:F1-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F1 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F1-MODEL — DimensionReportResponse — تقرير الأبعاد / Dimension report
Source DTO   : `DimensionReportResponse` (read only)
  dimensionId, dimensionValueId, periodId : number · read-only — echoed from the request
  rows[] : DimensionReportRowResponse —
    accountId, accountCode : number, string · read-only
    accountNameAr, accountNameEn : string · read-only
    natureCode : string · read-only · lookup — `DEBIT_CREDIT` (UXD-FIN-002)
    dimensionId, dimensionValueId : number · read-only
    dimensionValueCode : string · read-only
    dimensionValueNameAr, dimensionValueNameEn : string · read-only
    debitTotal, creditTotal, signedBalance : number · read-only
### F1-SCREEN — SCR-FIN-012
Search model : query params — dimensionId : number · EXACT · **required** ·
               dimensionValueId : number · EXACT · optional · periodId : number · EXACT ·
               optional. All three in the route's search params
Form model   : none — a read-only report
Container    : FULL_PAGE (no entry sub-view — ADR-FIN-003)
The row is keyed by account **and** dimension value together — that pair is the model's unit,
which is how REQ-FIN-043's "never by the base account alone" is expressed in the type rather
than only in the rendering. The dimension value's names come from the row itself, so this
screen needs no dimension-value lookup hook.

<!-- SUB:F1-SCR-FIN-012:END -->

<!-- PHASE:F1:END -->

<!-- PHASE:F2:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-045,AC-FIN-045,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 2 — F2 — Data Hooks

What each screen needs from the API — not hook code. Every read query's cache key carries
**every** filter that changes the response, page and size included; page and page size live
inside the filter object and are never independent state. Every mutation declares its
invalidation. Components use the facade only; the facade uses the declared queries only
(server-state library: `tanstack-query`).

Two invalidation families are shared across screens and are declared once here. `[reports, *]`
covers the five live-derived reports of SCR-FIN-008..012: every one is computed from posted
lines at request time [POL-FIN-009], so every endpoint that posts — API-FIN-019, API-FIN-021,
API-FIN-014, API-FIN-017 and API-FIN-027 — invalidates it. `[fiscal-periods, *]` is one key
shared by SCR-FIN-007's list, SCR-FIN-006's period select and the period filters of SCR-FIN-009
and SCR-FIN-011, so a period that closes is stale everywhere at once rather than on one screen.

Every `F2-LOOKUP` block below names a key whose values come from the lookup module through the
`UXD-*` of `ui-ux-spec-fin.md`; the hooks are shared by key, not duplicated per screen, and
REQ-FIN-045 is what registers those keys in the first place.

<!-- SUB:F2-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F2-QUERY — API-FIN-001            traces=API-FIN-001,REQ-FIN-001
POST `/api/v1/fin/accounts/search` · request `AccountSearchRequest` { filters[], sortField,
sortDirection, page, size } · response `Page<AccountResponse>` · kind **read query**
(a POST that mutates nothing)
Cache key    : `[accounts, filters]` where `filters` is the whole request object — code,
               nameAr/nameEn, accountTypeCode, isActiveFl, sortField, sortDirection **and
               page, size**. Page and page size live inside the filter object; they are never
               independent state.
Errors       : `FIN-400-INVALID-SORT` (400) → inline on the sort control ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message ·
               server error (500) → generic message
Loading      : LOCAL — the SRS states nothing about this call being slow, so no GLOBAL indicator
Cache policy : defaults
Invalidation : this key is refreshed by every mutation below
### F2-QUERY — API-FIN-002            traces=API-FIN-002,REQ-FIN-001,REQ-FIN-002
POST `/api/v1/fin/accounts` · request `AccountCreateRequest` { code, nameAr, nameEn,
accountTypeCode, natureCode, parentAccountId?, isLeafFl? } · response `AccountResponse` ·
kind **mutation**
Errors       : `FIN-409-ACCOUNT-DUP` (409) → inline on `code` ·
               `FIN-409-PARENT-NOT-LEAF-ELIGIBLE` (409) → user message for RULE-FIN-001,
               ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" ·
               en: "An account with sub-accounts cannot accept direct posting" ·
               `FIN-404-ACCOUNT` (404) → inline on `parentAccountId` ·
               `FIN-400-INVALID-LOOKUP` (400) → inline on the offending code field ·
               validation (400) → inline per `error.fieldErrors[].field` ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[accounts, *]`
### F2-QUERY — API-FIN-003            traces=API-FIN-003,REQ-FIN-002
PUT `/api/v1/fin/accounts/{id}` · request `AccountUpdateRequest` { nameAr, nameEn, isLeafFl } ·
response `AccountResponse` · kind **mutation**
Errors       : `FIN-409-HAS-CHILDREN` (409) → user message for RULE-FIN-001, the same ar/en
               pair as above, shown on the `isLeafFl` control ·
               `FIN-404-ACCOUNT` (404) → user message · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[accounts, *]`
### F2-QUERY — API-FIN-004            traces=API-FIN-004,REQ-FIN-003
PUT `/api/v1/fin/accounts/{id}/deactivate` · no request body · response `AccountResponse`
(isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-ACCOUNT` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[accounts, *]`
### F2-LOOKUP — ACCOUNT_TYPE
Key `ACCOUNT_TYPE` · one shared hook, resolved through UXD-FIN-001 · options shape
{ code, labelAr, labelEn } · long-lived cache (the values change only when the lookup module's
data does) · shared with SCR-FIN-009, SCR-FIN-010 and SCR-FIN-011, never duplicated per screen
### F2-LOOKUP — DEBIT_CREDIT
Key `DEBIT_CREDIT` · one shared hook, resolved through UXD-FIN-002 · options shape
{ code, labelAr, labelEn } · long-lived cache · shared with every screen that shows a direction
or a nature
### F2-SCREEN-INIT — SCR-FIN-001
Permission read : `FIN_ACCOUNTS` present in the caller's effective menu → VIEW (ADR-FIN-005).
                  CREATE and UPDATE are not readable from any published endpoint; their
                  affordances render and the server's 403 is the authority.
Lookups used    : ACCOUNT_TYPE (form + filter), DEBIT_CREDIT (form)
Entity by id    : none published — the form hydrates from the row the `[accounts, filters]`
                  query already holds (ADR-FIN-006), so opening an account performs no second
                  read and an invalidation re-reads through the same key
### F2-FACADE — SCR-FIN-001
Composes     : API-FIN-001 (list) · API-FIN-002, API-FIN-003, API-FIN-004 (mutations) · the
               ACCOUNT_TYPE and DEBIT_CREDIT hooks
State it owns: the tree derived from the query's rows (never a copy of them), the selected
               account id (from the route param), the filter object including page and size,
               and a derived loading flag over the calls in flight
Operations   : createAccount · updateAccount · deactivateAccount (confirmation first, naming
               that history is retained)
Components use the facade only; the facade uses the declared queries only.

<!-- SUB:F2-SCR-FIN-001:END -->

<!-- SUB:F2-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F2 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F2-QUERY — API-FIN-005            traces=API-FIN-005,REQ-FIN-004
POST `/api/v1/fin/dimensions/search` · request `DimensionSearchRequest` { filters[], sortField,
sortDirection, page, size } · response `Page<DimensionResponse>` · kind **read query**
Cache key    : `[dimensions, filters]` — code, sort **and page, size**, all inside the one object
Errors       : `FIN-400-INVALID-SORT` (400) → inline on the sort control ·
               `FIN-403-FORBIDDEN` (403) → forbidden message · server error → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-006
### F2-QUERY — API-FIN-006            traces=API-FIN-006,REQ-FIN-004
POST `/api/v1/fin/dimensions` · request `DimensionCreateRequest` { code, nameAr, nameEn } ·
response `DimensionResponse` · kind **mutation**
Errors       : `FIN-409-DIMENSION-DUP` (409) → inline on `code` · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[dimensions, *]`
### F2-QUERY — API-FIN-008            traces=API-FIN-008,REQ-FIN-005
POST `/api/v1/fin/dimensions/values/search` · request `DimensionValueSearchRequest`
{ filters[] including `dimensionId`, sortField, sortDirection, page, size } ·
response `Page<DimensionValueResponse>` · kind **read query**
Cache key    : `[dimension-values, filters]` — dimensionId, code, sort **and page, size**.
               The parent id is part of the key, so selecting another dimension is a different
               cache entry rather than a refetch of the same one.
Errors       : `FIN-404-DIMENSION` (404) → user message · `FIN-400-INVALID-SORT` (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-007 and API-FIN-035
### F2-QUERY — API-FIN-007            traces=API-FIN-007,REQ-FIN-005,REQ-FIN-006
POST `/api/v1/fin/dimensions/{id}/values` · request `DimensionValueCreateRequest`
{ code, nameAr, nameEn, sortOrder } · response `DimensionValueResponse` · kind **mutation**
Errors       : `FIN-409-DIMVALUE-DUP` (409) → user message for RULE-FIN-002, routed inline to
               `code`, ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" ·
               en: "This code is already used within this dimension" ·
               `FIN-404-DIMENSION` (404) → user message · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[dimension-values, *]`
### F2-QUERY — API-FIN-035            traces=API-FIN-035,REQ-FIN-005
PUT `/api/v1/fin/dimensions/values/{id}/deactivate` · no request body ·
response `DimensionValueResponse` (isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-DIMVALUE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[dimension-values, *]`
### F2-SCREEN-INIT — SCR-FIN-002
Permission read : `FIN_DIMENSIONS` present in the caller's effective menu → VIEW (ADR-FIN-005)
Lookups used    : none — this screen writes the data other screens' dimension selects read
Entity by id    : none published for either resource; both panes hydrate from their own search
                  caches (ADR-FIN-006)
### F2-FACADE — SCR-FIN-002
Composes     : API-FIN-005, API-FIN-008 (lists) · API-FIN-006, API-FIN-007, API-FIN-035
               (mutations)
State it owns: the dimension list and the selected dimension's value list, both derived from
               their queries' data; the selected dimension id (from the route param); two
               filter objects, each carrying its own page and size; a derived loading flag
Operations   : createDimension · createValue (under the selected dimension) ·
               deactivateValue (confirmation naming that the value will be refused on any
               later journal line — REQ-FIN-021)
There is no deactivateDimension operation: no endpoint exists for it (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-002:END -->

<!-- SUB:F2-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F2-QUERY — API-FIN-009            traces=API-FIN-009,REQ-FIN-007
POST `/api/v1/fin/event-rules/search` · request `EventTypeRuleSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<EventTypeRuleResponse>` ·
kind **read query**
Cache key    : `[event-rules, filters]` — eventTypeCode, isActiveFl, sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-010            traces=API-FIN-010,REQ-FIN-007
POST `/api/v1/fin/event-rules` · request `EventTypeRuleCreateRequest` { eventTypeCode, nameAr,
nameEn } · response `EventTypeRuleResponse` · kind **mutation**
Errors       : `FIN-409-RULE-DUP` (409) → inline on `eventTypeCode` (one rule per event type;
               note that a deactivated rule still holds its type — SRS §B4) ·
               `FIN-400-INVALID-LOOKUP` (400) → inline on `eventTypeCode` ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[event-rules, *]`
### F2-QUERY — API-FIN-011            traces=API-FIN-011,REQ-FIN-008,REQ-FIN-009
POST `/api/v1/fin/event-rules/{id}/lines` · request `RuleLineCreateRequest`
{ accountDerivationTypeCode, accountDerivationValue, amountSourceTypeCode, amountSourceValue?,
directionCode, distributionTypeCode, isRemainderFl? } · response `RuleLineResponse` ·
kind **mutation**
Errors       : `FIN-409-REMAINDER-COUNT` (409) → user message for RULE-FIN-003,
               ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" ·
               en: "Exactly one remainder line is required when any percentage distribution
               is present" ·
               `FIN-422-REMAINDER-MARKER` (422) → user message on the remainder marker ·
               `FIN-422-INVALID-PERCENTAGE-VALUE` (422) → inline on `amountSourceValue` ·
               `FIN-404-RULE` (404) → user message · `FIN-400-INVALID-LOOKUP` (400) → inline
               on the offending code field · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[event-rules, *]` — the rule's line set is part of what the list shows
### F2-QUERY — API-FIN-034            traces=API-FIN-034,REQ-FIN-007
PUT `/api/v1/fin/event-rules/{id}/deactivate` · no request body ·
response `EventTypeRuleResponse` (isActiveFl=false) · kind **mutation**
Errors       : `FIN-404-RULE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[event-rules, *]`
### F2-LOOKUP — ACCOUNTING_EVENT_TYPE
Key `ACCOUNTING_EVENT_TYPE` · one shared hook, resolved through UXD-FIN-007 · options
{ code, labelAr, labelEn } · long-lived cache. The list is legitimately empty until a host
registers event types; an empty list disables the create affordance with an explanatory
empty-state and is never replaced by a free-text field.
### F2-LOOKUP — ACCOUNT_DERIVATION_TYPE · AMOUNT_SOURCE_TYPE · DISTRIBUTION_TYPE · DEBIT_CREDIT
Keys `ACCOUNT_DERIVATION_TYPE` (UXD-FIN-008) · `AMOUNT_SOURCE_TYPE` (UXD-FIN-009) ·
`DISTRIBUTION_TYPE` (UXD-FIN-010) · `DEBIT_CREDIT` (UXD-FIN-002) — one shared hook per key,
each `{ code, labelAr, labelEn }`, each long-lived, and each shared with the other screens that
use the same key rather than re-fetched here.
### F2-SCREEN-INIT — SCR-FIN-003
Permission read : `FIN_RULES` present in the caller's effective menu → VIEW (ADR-FIN-005)
Lookups used    : ACCOUNTING_EVENT_TYPE (header + filter), ACCOUNT_DERIVATION_TYPE,
                  AMOUNT_SOURCE_TYPE, DISTRIBUTION_TYPE, DEBIT_CREDIT (line grid)
Entity by id    : none published — the rule page hydrates from the `[event-rules, filters]`
                  cache (ADR-FIN-006)
### F2-FACADE — SCR-FIN-003
Composes     : API-FIN-009 (list) · API-FIN-010, API-FIN-011, API-FIN-034 (mutations) · the
               five lookup hooks above
State it owns: the rule list from the query's data, the selected rule id (route param), the
               filter object including page and size, the draft line being added, and a
               derived loading flag
Operations   : createRule · addRuleLine · deactivateRule (confirmation stating that the event
               type is not freed for a replacement rule — the limitation SRS §B4 records)
There is no updateRule and no deleteRuleLine operation: neither endpoint exists (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-003:END -->

<!-- SUB:F2-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F2-QUERY — API-FIN-012            traces=API-FIN-012,REQ-FIN-022
POST `/api/v1/fin/recurring-templates/search` · request `RecurringTemplateSearchRequest`
{ filters[], sortField, sortDirection, page, size } · response
`Page<RecurringTemplateResponse>` (each row carries its full `lines[]`) · kind **read query**
Cache key    : `[recurring-templates, filters]` — nameAr/nameEn, scheduleTypeCode, isActiveFl,
               sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-013            traces=API-FIN-013,REQ-FIN-022
POST `/api/v1/fin/recurring-templates` · request `RecurringTemplateCreateRequest` { nameAr,
nameEn, scheduleTypeCode, frequencyCode?, startDate, endDate?, lines[] { accountId, amount,
directionCode, dimensionValueId? } } · response `RecurringTemplateResponse` · kind **mutation**
Errors       : `FIN-400-MISSING-FREQUENCY` (400) → inline on `frequencyCode` when the schedule
               type is RECURRING · `FIN-404-ACCOUNT` (404) → inline on the offending line's
               account · `FIN-409-INVALID-DIMENSION` (409) → inline on the offending line's
               dimension value · `FIN-400-INVALID-LOOKUP` (400) → inline on the offending code ·
               validation (400) → inline per field · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[recurring-templates, *]`
### F2-QUERY — API-FIN-014            traces=API-FIN-014,REQ-FIN-023,REQ-FIN-024
POST `/api/v1/fin/recurring-templates/{id}/run` · no request body ·
response `JournalEntryResponse` (the posted entry) · kind **mutation**
Errors       : `FIN-409-NOT-ACTIVE` (409) → user message,
               ar: "هذا التعريف غير نشط ولا يمكن تشغيله" ·
               en: "This definition is deactivated and cannot be run" ·
               `FIN-404-TEMPLATE` (404) → user message ·
               the posting pipeline's refusals, each as its own user message —
               `FIN-409-UNBALANCED` (409) [RULE-FIN-006] ·
               `FIN-409-NOT-POSTABLE-ACCOUNT` (409) [RULE-FIN-007] ·
               `FIN-409-PERIOD-NOT-OPEN` (409) [RULE-FIN-008] ·
               `FIN-409-INVALID-DIMENSION` (409) [RULE-FIN-009] ·
               `FIN-404-PERIOD` / `FIN-404-YEAR` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[recurring-templates, *]` (the template's `nextRunDate` advanced) and
               `[journal-entries, *]` (a new entry exists) and `[reports, *]` (every live
               report over posted lines is now stale)
### F2-QUERY — API-FIN-036            traces=API-FIN-036,REQ-FIN-022
PUT `/api/v1/fin/recurring-templates/{id}/deactivate` · no request body ·
response `RecurringTemplateResponse` (isActiveFl=false, lines included) · kind **mutation**
Errors       : `FIN-404-TEMPLATE` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[recurring-templates, *]`
### F2-LOOKUP — RECURRING_SCHEDULE_TYPE · RECURRING_FREQUENCY · DEBIT_CREDIT
Keys `RECURRING_SCHEDULE_TYPE` (UXD-FIN-011) · `RECURRING_FREQUENCY` (UXD-FIN-012) ·
`DEBIT_CREDIT` (UXD-FIN-002) — one shared hook per key, `{ code, labelAr, labelEn }`,
long-lived cache, the DEBIT_CREDIT hook shared with every other screen that shows a direction.
### F2-SCREEN-INIT — SCR-FIN-004
Permission read : `FIN_RECURRING_TEMPLATES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005)
Lookups used    : RECURRING_SCHEDULE_TYPE (header + filter), RECURRING_FREQUENCY (header),
                  DEBIT_CREDIT (line grid)
Entity by id    : none published — the search row already carries the full aggregate, lines
                  included, so the page hydrates from the `[recurring-templates, filters]`
                  cache (ADR-FIN-006)
### F2-FACADE — SCR-FIN-004
Composes     : API-FIN-012 (list) · API-FIN-013, API-FIN-014, API-FIN-036 (mutations) · the
               three lookup hooks above
State it owns: the template list from the query's data, the selected template id (route
               param), the filter object including page and size, the draft template and its
               draft lines, and a derived loading flag
Operations   : createTemplate (header and lines in one submission) · runTemplate (confirmation
               first; on success the returned entry is offered on SCR-FIN-006) ·
               deactivateTemplate (confirmation stating that the template will no longer run)
No updateTemplate operation exists: no endpoint is published (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-004:END -->

<!-- SUB:F2-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F2-QUERY — API-FIN-015            traces=API-FIN-015,REQ-FIN-025
POST `/api/v1/fin/allocation-rules/search` · request `AllocationRuleSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<AllocationRuleResponse>` (each row
carries its full `targets[]`) · kind **read query**
Cache key    : `[allocation-rules, filters]` — nameAr/nameEn, sourceAccountId, isActiveFl,
               sort **and page, size**
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by every mutation below
### F2-QUERY — API-FIN-016            traces=API-FIN-016,REQ-FIN-025
POST `/api/v1/fin/allocation-rules` · request `AllocationRuleCreateRequest` { nameAr, nameEn,
sourceAccountId, targets[] { targetAccountId, dimensionValueId?, distributionTypeCode,
distributionValue?, isRemainderFl? } } · response `AllocationRuleResponse` · kind **mutation**
Errors       : `FIN-409-REMAINDER-COUNT` (409) → user message for RULE-FIN-003, the same ar/en
               pair the rule declares, shown on the target grid ·
               `FIN-422-REMAINDER-MARKER` (422) → user message on the remainder marker ·
               `FIN-422-INVALID-PERCENTAGE-VALUE` (422) → inline on the offending
               `distributionValue` · `FIN-404-ACCOUNT` (404) → inline on the offending account ·
               `FIN-409-INVALID-DIMENSION` (409) → inline on the offending dimension value ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`
### F2-QUERY — API-FIN-017            traces=API-FIN-017,REQ-FIN-026
POST `/api/v1/fin/allocation-rules/{id}/run` · no request body ·
response `JournalEntryResponse` (the posted distribution entry) · kind **mutation**
Errors       : `FIN-409-NOT-ACTIVE` (409) → user message, the same ar/en pair as the template
               run · `FIN-404-ALLOCATION-RULE` (404) → user message ·
               `FIN-409-REMAINDER-COUNT` (409) [RULE-FIN-003, re-checked at run time] ·
               `FIN-422-REMAINDER-NOT-POSITIVE` (422) → user message for RULE-FIN-010,
               ar: "سطر الباقي يُحسب كفرق، لا كنسبة" ·
               en: "The remainder line is computed as a difference, never as a percentage" ·
               the posting pipeline's refusals — `FIN-409-UNBALANCED`,
               `FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`,
               `FIN-409-INVALID-DIMENSION` (409) · `FIN-404-PERIOD` / `FIN-404-YEAR` (404) ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`, `[journal-entries, *]` and `[reports, *]`
### F2-QUERY — API-FIN-037            traces=API-FIN-037,REQ-FIN-025
PUT `/api/v1/fin/allocation-rules/{id}/deactivate` · no request body ·
response `AllocationRuleResponse` (isActiveFl=false, targets included) · kind **mutation**
Errors       : `FIN-404-ALLOCATION-RULE` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[allocation-rules, *]`
### F2-LOOKUP — DISTRIBUTION_TYPE
Key `DISTRIBUTION_TYPE` · the same shared hook SCR-FIN-003 uses, resolved through UXD-FIN-010 ·
options { code, labelAr, labelEn } · long-lived cache · one hook for the whole application
### F2-SCREEN-INIT — SCR-FIN-005
Permission read : `FIN_ALLOCATION_RULES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005)
Lookups used    : DISTRIBUTION_TYPE (target grid)
Entity by id    : none published — the search row carries the full aggregate, targets included
                  (ADR-FIN-006)
### F2-FACADE — SCR-FIN-005
Composes     : API-FIN-015 (list) · API-FIN-016, API-FIN-017, API-FIN-037 (mutations) · the
               DISTRIBUTION_TYPE hook
State it owns: the rule list from the query's data, the selected rule id (route param), the
               filter object including page and size, the draft rule and its draft targets,
               and a derived loading flag
Operations   : createRule (header and targets in one submission) · runRule (confirmation
               first; on success the returned entry is offered on SCR-FIN-006) ·
               deactivateRule (confirmation stating that the rule will no longer run)
No updateRule operation exists: no endpoint is published (ADR-FIN-006).

<!-- SUB:F2-SCR-FIN-005:END -->

<!-- SUB:F2-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-006 — قيود اليومية / Journal entries

### F2-QUERY — API-FIN-018            traces=API-FIN-018,REQ-FIN-027
POST `/api/v1/fin/journal-entries/search` · request `JournalEntrySearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<JournalEntryResponse>` ·
kind **read query**
Cache key    : `[journal-entries, filters]` — docNo, docDate range, periodId, statusCode,
               journalTypeCode, sort **and page, size**, all inside the one filter object
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-019 and API-FIN-021, and by the two run endpoints of
               SCR-FIN-004 and SCR-FIN-005 and the year-end close of SCR-FIN-007
### F2-QUERY — API-FIN-022            traces=API-FIN-022,REQ-FIN-016,REQ-FIN-027
GET `/api/v1/fin/journal-entries/{id}` · response `JournalEntryResponse` with its `lines[]`
and each line's `dimensions[]` · kind **read query**
Cache key    : `[journal-entry, id]`
Errors       : `FIN-404-ENTRY` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults — a POSTED entry is immutable (RULE-FIN-016), so a cached one cannot
               go stale except through its own reversal link, which API-FIN-021 invalidates
Invalidation : n/a (a read); invalidated by API-FIN-021 for the reversed original
This is the one by-id read in the module, and it exists because the search result is not where
REQ-FIN-016 and REQ-FIN-027 read an entry's lines from.
### F2-QUERY — API-FIN-019            traces=API-FIN-019,REQ-FIN-014,REQ-FIN-015,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021
POST `/api/v1/fin/journal-entries` · request `JournalEntryCreateRequest` { docDate,
fiscalYearId, periodId, journalTypeCode, descriptionAr?, descriptionEn?, lines[] { accountId,
amount, directionCode, descriptionAr?, descriptionEn?, dimensions[] { dimensionId,
dimensionValueId } } } · response `JournalEntryResponse` (POSTED) · kind **mutation**
Errors       : every automatic check REQ-FIN-015 asks to be shown, each routed to the line or
               field it names and all shown together rather than one at a time —
               `FIN-409-UNBALANCED` (409) [RULE-FIN-006],
               ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" ·
               en: "The entry is unbalanced — total debits do not equal total credits" ·
               `FIN-409-NOT-POSTABLE-ACCOUNT` (409) [RULE-FIN-007],
               ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" ·
               en: "The target account does not accept direct posting" — routed to the line ·
               `FIN-409-PERIOD-NOT-OPEN` (409) [RULE-FIN-008],
               ar: "الفترة المستهدفة غير مفتوحة" · en: "The target period is not open" ·
               `FIN-409-INVALID-DIMENSION` (409) [RULE-FIN-009],
               ar: "قيمة البُعد غير صالحة" · en: "The dimension value is invalid" ·
               `FIN-400-PERIOD-NOT-IN-YEAR` (400) and `FIN-400-DOCDATE-OUTSIDE-PERIOD` (400)
               [RULE-FIN-017] → inline on the period and the document date ·
               `FIN-404-ACCOUNT` / `FIN-404-PERIOD` / `FIN-404-YEAR` (404) → inline on the
               offending selection · validation (400) → inline per field ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL — the submit affordance is busy; the entry is not cleared
Invalidation : `[journal-entries, *]` and `[reports, *]`
### F2-QUERY — API-FIN-020            traces=API-FIN-020,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013
POST `/api/v1/fin/journal-entries/from-event` · request `EventEntryBuildRequest`
{ eventReference, eventTypeCode, docDate, baseAmount, amounts?, fields?, descriptionAr?,
descriptionEn? } · response `JournalEntryResponse` · kind **mutation**
**Bound, and called by no screen** (ADR-FIN-007): the caller is a host system over the
platform's in-process module interface, not a user with a form. It is stated here so the
published surface is completely accounted for.
Errors       : `FIN-404-NO-ACTIVE-RULE` (404) [RULE-FIN-005] · `FIN-409-DUPLICATE-EVENT` (409)
               [RULE-FIN-004] · `FIN-422-MAPPING-UNSUPPORTED` (422) · the same posting
               refusals as API-FIN-019 — all answered to the calling system, never rendered
               by a FIN screen
Invalidation : n/a — no client of this plan calls it
### F2-QUERY — API-FIN-021            traces=API-FIN-021,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030
POST `/api/v1/fin/journal-entries/{id}/reverse` · no request body ·
response `JournalEntryResponse` (the new reversal entry) · kind **mutation**
Errors       : `FIN-409-NOT-POSTED` (409) [RULE-FIN-013] → user message,
               ar: "لا يمكن عكس قيد غير مُرحَّل" · en: "A non-posted entry cannot be reversed" ·
               `FIN-409-ALREADY-REVERSED` (409) → user message (the entry already carries a
               reversal link) · `FIN-409-PERIOD-NOT-OPEN` (409) → user message, raised when no
               open period can receive the reversal [RULE-FIN-012] ·
               `FIN-404-ENTRY` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[journal-entries, *]`, `[journal-entry, id]` (the original now carries its
               `reversalEntryId`) and `[reports, *]`
### F2-LOOKUP — JOURNAL_TYPE · JOURNAL_STATUS · DEBIT_CREDIT
Keys `JOURNAL_TYPE` (UXD-FIN-005) · `JOURNAL_STATUS` (UXD-FIN-006) · `DEBIT_CREDIT`
(UXD-FIN-002) — one shared hook per key, `{ code, labelAr, labelEn }`, long-lived cache. The
first two serve the search filters and the read-only display; on the entry form the journal
type is the fixed value `MANUAL` and no select is rendered (ADR-FIN-008).
### F2-SCREEN-INIT — SCR-FIN-006
Permission read : `FIN_JOURNAL_ENTRIES` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). CREATE and the custom reverse action are not readable; their
                  affordances render and the server's 403 is the authority.
Lookups used    : JOURNAL_TYPE (filter + display), JOURNAL_STATUS (filter + display),
                  DEBIT_CREDIT (line grid)
Entity by id    : API-FIN-022 — the entry page reads by id rather than from the list cache,
                  because the lines and their dimensions are what the page renders
Period + year   : the period and year selects of the entry form are served by the SCR-FIN-007
                  fiscal-period query (API-FIN-033) through its own shared hook, keyed the
                  same way; this screen declares the dependency and does not duplicate the call
### F2-FACADE — SCR-FIN-006
Composes     : API-FIN-018 (list) · API-FIN-022 (entry) · API-FIN-019, API-FIN-021
               (mutations) · the three lookup hooks and the fiscal-period hook
State it owns: the list derived from the query's data, the selected entry id (route param),
               the filter object including page and size, the draft entry with its draft lines
               and their dimensions, the live debit and credit totals derived from those draft
               lines, and a derived loading flag
Operations   : postManualEntry (the draft is submitted whole; every returned refusal is
               displayed at once — REQ-FIN-015 — and nothing is cleared) ·
               reverseEntry (confirmation naming the period the reversal will land in)
The live totals are derived state over the draft lines and are never sent: the balance
judgement is RULE-FIN-006's, evaluated by the server.

<!-- SUB:F2-SCR-FIN-006:END -->

<!-- SUB:F2-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F2-QUERY — API-FIN-033            traces=API-FIN-033,REQ-FIN-031
POST `/api/v1/fin/fiscal-periods/search` · request `FiscalPeriodSearchRequest` { filters[]
optionally carrying `fiscalYearId` and `statusCode`, sortField, sortDirection, page, size } ·
response `Page<FiscalPeriodResponse>` · kind **read query**
Cache key    : `[fiscal-periods, filters]` — fiscalYearId, statusCode, sort **and page, size**.
               Omitting the year is a legitimate "all periods" request and is its own key.
Errors       : `FIN-400-INVALID-SORT` (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026 and API-FIN-027
This query is also the shared source of the period select on SCR-FIN-006's entry form and of
the period filters on SCR-FIN-009 and SCR-FIN-011 — one hook, one key, no duplicate call.
### F2-QUERY — API-FIN-023            traces=API-FIN-023,REQ-FIN-031
POST `/api/v1/fin/fiscal-years` · request `FiscalYearCreateRequest` { code, startDate, endDate,
periodCount } · response `FiscalYearResponse` with its generated `periods[]` · kind **mutation**
Errors       : `FIN-409-YEAR-DUP` (409) → inline on `code` · validation (400) → inline per
               field · `FIN-403-FORBIDDEN` (403) → forbidden message
Invalidation : `[fiscal-periods, *]` — the new year's periods must appear in every period list
### F2-QUERY — API-FIN-024            traces=API-FIN-024,REQ-FIN-032,REQ-FIN-035
PATCH `/api/v1/fin/fiscal-periods/{id}/open` · no request body · response
`FiscalPeriodResponse` · kind **mutation**
Errors       : `FIN-409-NOT-REOPENABLE` (409) [RULE-FIN-014] → user message,
               ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" ·
               en: "The period is hard-closed and cannot be reopened" ·
               `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-025            traces=API-FIN-025,REQ-FIN-033
PATCH `/api/v1/fin/fiscal-periods/{id}/soft-close` · no request body · response
`FiscalPeriodResponse` · kind **mutation**
Errors       : `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message · `FIN-403-FORBIDDEN` (403) → forbidden
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-026            traces=API-FIN-026,REQ-FIN-034,REQ-FIN-037,REQ-FIN-038
PATCH `/api/v1/fin/fiscal-periods/{id}/hard-close` · no request body · response
`FiscalPeriodResponse` (with `closedBy` and `closedAt` set) · kind **mutation**
Errors       : `FIN-409-INVALID-TRANSITION` (409) → user message ·
               `FIN-404-PERIOD` (404) → user message ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message — this is the
               refusal a caller without `PERM_FIN_PERIODS_CLOSE_APPROVE` receives, and it is
               the visible half of RULE-FIN-015
Invalidation : `[fiscal-periods, *]`
### F2-QUERY — API-FIN-027            traces=API-FIN-027,REQ-FIN-036
POST `/api/v1/fin/fiscal-years/{id}/year-end-close` · no request body ·
response `YearEndCloseResponse` { closingEntry, openingEntry } · kind **mutation**
Errors       : `FIN-409-PERIODS-NOT-CLOSED` (409) → user message (not every period of the year
               is hard-closed) · `FIN-404-YEAR` / `FIN-404-PERIOD` / `FIN-404-ACCOUNT` (404) →
               user message (the last covers a ledger with no account marked as retained
               earnings) · `FIN-409-UNBALANCED`, `FIN-409-NOT-POSTABLE-ACCOUNT`,
               `FIN-409-INVALID-DIMENSION` (409) → user message ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : GLOBAL — the only GLOBAL indicator in this plan. The call computes every
               balance-sheet balance of the year and posts two entries; the SRS describes it
               as the year's terminal act (REQ-FIN-036), and a screen-local spinner would
               leave the rest of the application looking usable while the ledger's year is
               being closed underneath it
Invalidation : `[fiscal-periods, *]`, `[journal-entries, *]` and `[reports, *]`
### F2-LOOKUP — PERIOD_STATE · FISCAL_YEAR_STATUS
Keys `PERIOD_STATE` (UXD-FIN-003) · `FISCAL_YEAR_STATUS` (UXD-FIN-004) — one shared hook per
key, `{ code, labelAr, labelEn }`, long-lived cache. The labels come from the lookup; which
transitions a row offers comes from SRS §A7, not from the lookup's value list.
### F2-SCREEN-INIT — SCR-FIN-007
Permission read : `FIN_PERIODS` present in the caller's effective menu → VIEW (ADR-FIN-005).
                  `PERM_FIN_PERIODS_CLOSE_APPROVE` is not readable from any published
                  endpoint, so the hard-close and year-end-close affordances render and the
                  server's 403 is the authority (ADR-FIN-005).
Lookups used    : PERIOD_STATE (row status + filter), FISCAL_YEAR_STATUS (year header)
Entity by id    : none published for either resource — the period rows come from API-FIN-033
                  and the year from the API-FIN-023 response and from the rows' `fiscalYearId`
                  (ADR-FIN-006)
### F2-FACADE — SCR-FIN-007
Composes     : API-FIN-033 (period list) · API-FIN-023, API-FIN-024, API-FIN-025,
               API-FIN-026, API-FIN-027 (mutations) · the two lookup hooks
State it owns: the period list from the query's data, the year list derived from those rows'
               `fiscalYearId`, the selected year id (route param), the filter object including
               page and size, the create-year draft, and a derived loading flag
Operations   : createYear · openPeriod · softClosePeriod · hardClosePeriod (confirmation using
               the word permanent — RULE-FIN-014) · runYearEndClose (confirmation; on success
               the two returned entries are offered on SCR-FIN-006)

<!-- SUB:F2-SCR-FIN-007:END -->

<!-- SUB:F2-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F2-QUERY — API-FIN-028            traces=API-FIN-028,REQ-FIN-039,REQ-FIN-046
GET `/api/v1/fin/reports/account-ledger` · query params `accountId` (required), `fromDate`,
`toDate`, `dimensionId`, `dimensionValueId` · response `AccountLedgerResponse` with its
`rows[]` · kind **read query**
Cache key    : `[reports, account-ledger, filters]` where `filters` carries all five params.
               Every parameter that changes the response is in the key; this report is not
               paged, so no page or size belongs in it.
Errors       : `FIN-404-ACCOUNT` (404) → user message (the keying id did not resolve) ·
               validation (400) → inline on the offending parameter ·
               `FIN-403-FORBIDDEN` (403) → the localized forbidden message
Loading      : LOCAL
Cache policy : defaults, and the key is in the `[reports, *]` family every posting mutation
               invalidates — a ledger computed live from posted lines is stale the moment
               anything posts [POL-FIN-009]
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT · JOURNAL_TYPE
Keys `ACCOUNT_TYPE` (UXD-FIN-001) · `DEBIT_CREDIT` (UXD-FIN-002) · `JOURNAL_TYPE`
(UXD-FIN-005) — the same shared hooks the entry screens use; this screen adds no hook of its own.
### F2-SCREEN-INIT — SCR-FIN-008
Permission read : `FIN_ACCOUNT_LEDGER` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). This screen has no other action.
Lookups used    : ACCOUNT_TYPE, DEBIT_CREDIT, JOURNAL_TYPE (all display-only)
Entity by id    : none — the report's own response carries the account's identity
Account select  : served by the SCR-FIN-001 account search (API-FIN-001) through its shared
                  key; this screen declares the dependency and duplicates no call
### F2-FACADE — SCR-FIN-008
Composes     : API-FIN-028 · the account search for its account picker · the three lookup hooks
State it owns: the filter object (account, date range, dimension, dimension value) mirrored
               from the route's search params, and a derived loading flag. No running balance
               and no total is owned here: all three come from the response
Operations   : none — this screen writes nothing. Navigation to SCR-FIN-006 for a row's entry
               is a route change, not an operation

<!-- SUB:F2-SCR-FIN-008:END -->

<!-- SUB:F2-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F2-QUERY — API-FIN-029            traces=API-FIN-029,REQ-FIN-040,REQ-FIN-046
GET `/api/v1/fin/reports/trial-balance` · query params `periodId` (optional),
`accountTypeCode` (optional) · response `TrialBalanceResponse` with its `rows[]` ·
kind **read query**
Cache key    : `[reports, trial-balance, filters]` — both params, and the unfiltered request is
               its own key rather than a variant of a filtered one
Errors       : `FIN-404-PERIOD` (404) → user message, raised only when `periodId` is supplied
               and does not resolve; omitting it stays a valid whole-ledger request ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
Keys `ACCOUNT_TYPE` (UXD-FIN-001, also the filter's option list) · `DEBIT_CREDIT`
(UXD-FIN-002) — the same shared hooks; no new hook here.
### F2-SCREEN-INIT — SCR-FIN-009
Permission read : `FIN_TRIAL_BALANCE` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (filter + display), DEBIT_CREDIT (display)
Entity by id    : none
Period select   : served by the shared fiscal-period query (API-FIN-033) of SCR-FIN-007
### F2-FACADE — SCR-FIN-009
Composes     : API-FIN-029 · the fiscal-period hook for its period select · the two lookup hooks
State it owns: the filter object (period, account type) mirrored from the route's search
               params, and a derived loading flag. `balanced` and both totals are read from the
               response and never derived here
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-009:END -->

<!-- SUB:F2-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F2-QUERY — API-FIN-030            traces=API-FIN-030,REQ-FIN-041,REQ-FIN-046
GET `/api/v1/fin/reports/balance-sheet` · query params `fiscalYearId` (**required**),
`asOfDate` (optional) · response `BalanceSheetResponse` with its `groups[]` ·
kind **read query**
Cache key    : `[reports, balance-sheet, filters]` — both params
Enabled      : only once a fiscal year is chosen — the query does not run with an absent
               required parameter, and the screen shows its choose-a-year state instead of a
               failed request
Errors       : `FIN-404-YEAR` (404) → user message (the required keying id did not resolve) ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
The same two shared hooks (UXD-FIN-001, UXD-FIN-002); the account type labels the section
headings the response groups by.
### F2-SCREEN-INIT — SCR-FIN-010
Permission read : `FIN_BALANCE_SHEET` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (section headings), DEBIT_CREDIT (row nature)
Entity by id    : none
Year select     : derived from the `fiscalYearId` of the shared fiscal-period query's rows
                  (API-FIN-033), since no fiscal-year search is published (ADR-FIN-006)
### F2-FACADE — SCR-FIN-010
Composes     : API-FIN-030 · the fiscal-period hook for its year select · the two lookup hooks
State it owns: the filter object (fiscal year, as-of date) mirrored from the route's search
               params, and a derived loading flag. No group total and no section is composed
               here — both arrive in the response
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-010:END -->

<!-- SUB:F2-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-011 — قائمة الدخل / Income statement

### F2-QUERY — API-FIN-031            traces=API-FIN-031,REQ-FIN-042,REQ-FIN-046
GET `/api/v1/fin/reports/income-statement` · query params `fiscalYearId` (**required**),
`fromPeriodId` (optional), `toPeriodId` (optional) · response `IncomeStatementResponse` with
its `groups[]` · kind **read query**
Cache key    : `[reports, income-statement, filters]` — all three params
Enabled      : only once a fiscal year is chosen, as on SCR-FIN-010
Errors       : `FIN-404-YEAR` (404) → user message (the required keying id) ·
               `FIN-404-PERIOD` (404) → user message, raised only when a period id is supplied
               and does not resolve · validation (400) → inline ·
               `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — ACCOUNT_TYPE · DEBIT_CREDIT
The same two shared hooks (UXD-FIN-001, UXD-FIN-002).
### F2-SCREEN-INIT — SCR-FIN-011
Permission read : `FIN_INCOME_STATEMENT` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : ACCOUNT_TYPE (section headings), DEBIT_CREDIT (row nature)
Entity by id    : none
Year + periods  : both selects served by the shared fiscal-period query (API-FIN-033); the
                  period selects are narrowed to the chosen year by the same filter object
### F2-FACADE — SCR-FIN-011
Composes     : API-FIN-031 · the fiscal-period hook · the two lookup hooks
State it owns: the filter object (fiscal year, from period, to period) mirrored from the
               route's search params, and a derived loading flag. `fromDate`, `toDate` and
               `netResult` are read from the response, never computed here
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-011:END -->

<!-- SUB:F2-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F2-QUERY — API-FIN-032            traces=API-FIN-032,REQ-FIN-043
GET `/api/v1/fin/reports/dimension` · query params `dimensionId` (**required**),
`dimensionValueId` (optional), `periodId` (optional) · response `DimensionReportResponse`
with its `rows[]` · kind **read query**
Cache key    : `[reports, dimension, filters]` — all three params
Enabled      : only once a dimension is chosen — the required parameter gates the call, and
               the screen shows its choose-a-dimension state until then
Errors       : `FIN-404-DIMENSION` (404) → user message (the required keying id) ·
               `FIN-404-PERIOD` (404) → user message when a supplied period does not resolve ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — DEBIT_CREDIT
Key `DEBIT_CREDIT` (UXD-FIN-002) — the shared hook, for the row's nature. The dimension and
dimension-value selects are NOT lookups: they read FIN's own API-FIN-005 and API-FIN-008
through the SCR-FIN-002 keys, and the row's dimension-value names come from the report itself.
### F2-SCREEN-INIT — SCR-FIN-012
Permission read : `FIN_DIMENSION_REPORTS` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : DEBIT_CREDIT (row nature)
Entity by id    : none
Dimension select: served by the SCR-FIN-002 dimension and dimension-value searches through
                  their shared keys; no call is duplicated here
### F2-FACADE — SCR-FIN-012
Composes     : API-FIN-032 · the dimension and dimension-value searches for its selects · the
               DEBIT_CREDIT hook
State it owns: the filter object (dimension, dimension value, period) mirrored from the
               route's search params, and a derived loading flag. No aggregation is performed
               here — the account × dimension-value rows arrive as they are
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-012:END -->

<!-- PHASE:F2:END -->

<!-- PHASE:F3:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 3 — F3 — Forms & Validators

One block per `RULE-*` enforced on a form, plus the field constraints the published DTOs state.
No frontend-only validation the SRS does not state; every message is read from its catalog
code, never hard-coded; the locale resolves session → browser → `ar`; and a caller without the
write permission is answered by the server rather than by a pre-emptively disabled field
(ADR-FIN-005). Schemas are written with `zod` + `react-hook-form`.

Five of the twelve screens carry no form at all: SCR-FIN-008..012 are read-only reports whose
SRS §B3 reads "not applicable". Their blocks state the filter validation and say plainly that
no `RULE-*` is enforced, rather than inventing one to fill the section.

<!-- SUB:F3-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F3 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

Validation timing for this form: **on blur for the unique code, on submit for the rest**
(declared once for the whole form).
### F3-FIELD — SCR-FIN-001 (create)
code            · REQUIRED · LENGTH (maxLength 30, from `AccountCreateRequest`) ·
                  UNIQUE_CHECK · when blur
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 200) · when submit
accountTypeCode · REQUIRED · LOOKUP_VALID (`ACCOUNT_TYPE`, UXD-FIN-001) · LENGTH (20) · when submit
natureCode      · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
parentAccountId · optional · when submit
isLeafFl        · optional · BUSINESS_RULE (RULE-FIN-001) · when submit
### F3-FIELD — SCR-FIN-001 (edit)
code, accountTypeCode, natureCode, parentAccountId · read-only — not inputs at all;
                  `AccountUpdateRequest` does not carry them
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 200) · when submit
isLeafFl        · REQUIRED · BUSINESS_RULE (RULE-FIN-001) · when submit
UNIQUE_CHECK    : async, on blur, via `API-FIN-001` with an EQUALS filter on `code`; on edit
                  the field is read-only so the check does not run at all. A failure never
                  blocks submit on its own — the authority is the server's
                  `FIN-409-ACCOUNT-DUP`, routed inline to the same field.
LOOKUP_VALID    : the value must be one the runtime-loaded option list contains; no static
                  list is written anywhere, and an empty option list leaves the field
                  unsatisfiable rather than falling back to a hardcoded set (ADR-FIN-004).
### F3-VALIDATION — RULE-FIN-001      traces=REQ-FIN-002,AC-FIN-002
Statement : The system shall prevent an account with any child account from being marked as
            accepting direct posting.
Message   : from the catalog codes `FIN-409-PARENT-NOT-LEAF-ELIGIBLE` (on create) and
            `FIN-409-HAS-CHILDREN` (on update) —
            ar: "لا يمكن لحساب له حسابات فرعية أن يقبل ترحيلاً مباشرًا" ·
            en: "An account with sub-accounts cannot accept direct posting"
Scope     : CREATE and UPDATE
Field     : isLeafFl · kind BUSINESS_RULE · when submit
Validation shape : the client knows, from the tree it already renders, whether the selected
            node has children, and uses that to explain the constraint beside the control
            before submit. It does **not** decide the outcome: the tree is a page of search
            results and may not hold every child, so the submission goes through and the
            catalog message is what the user is shown on refusal. The message is read from the
            catalog, never composed here.
Business-code fields: `code` is the chart-of-accounts code and is displayed read-only after
create; it is never regenerated or re-derived on the client.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `FIN-403-FORBIDDEN` on submit
and the form shows the localized forbidden message; fields are not pre-emptively disabled,
because the permission is not readable (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-001:END -->

<!-- SUB:F3-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F3 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

Validation timing for this form: **on blur for the unique codes, on submit for the rest**.
### F3-FIELD — SCR-FIN-002 (dimension, create)
code           · REQUIRED · LENGTH (maxLength 30) · UNIQUE_CHECK · when blur
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-FIN-002 (dimension value, create)
code           · REQUIRED · LENGTH (maxLength 30) · UNIQUE_CHECK (within the selected
                 dimension — RULE-FIN-002) · when blur
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder      · REQUIRED · when submit
UNIQUE_CHECK   : async, on blur — the dimension via `API-FIN-005` with an EQUALS filter on
                 `code`; the value via `API-FIN-008` with EQUALS filters on both `dimensionId`
                 and `code`, so the scope of the check is the same scope the rule has. Neither
                 blocks submit on its own: the server's `FIN-409-DIMENSION-DUP` and
                 `FIN-409-DIMVALUE-DUP` are the authority, routed inline to `code`.
### F3-VALIDATION — RULE-FIN-002      traces=REQ-FIN-006,AC-FIN-006
Statement : The system shall reject a dimension value whose code already exists under the same
            dimension.
Message   : from the catalog code `FIN-409-DIMVALUE-DUP` —
            ar: "هذا الرمز مستخدم بالفعل ضمن هذا البُعد" ·
            en: "This code is already used within this dimension"
Scope     : CREATE
Field     : code (of the value) · kind UNIQUE_CHECK · when blur, and again on submit by the server
Validation shape : uniqueness is scoped to the parent dimension, never globally — a code used
            under one dimension is legitimate under another, and a global check would reject a
            value the server accepts. Written with `zod` + `react-hook-form`, with the async
            check bound to the selected parent id.
Business-code fields: none of these codes is platform-numbered; both are client-defined and
are read-only after create because neither resource has an update endpoint.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit and the form shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-002:END -->

<!-- SUB:F3-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F3 · SCR-FIN-003 — قواعد المحرك / Engine rules

Validation timing for this form: **on submit** for the rule header and for each line
(declared once for the whole page). The remainder marker is judged across the line set, so it
has nothing to validate until a line is submitted.
### F3-FIELD — SCR-FIN-003 (rule header, create)
eventTypeCode  · REQUIRED · LOOKUP_VALID (`ACCOUNTING_EVENT_TYPE`, UXD-FIN-007) ·
                 LENGTH (maxLength 50) · UNIQUE_CHECK · when submit
nameAr, nameEn · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-FIN-003 (rule line)
accountDerivationTypeCode · REQUIRED · LOOKUP_VALID (`ACCOUNT_DERIVATION_TYPE`, UXD-FIN-008) ·
                            LENGTH (20) · when submit
accountDerivationValue    · REQUIRED · when submit
amountSourceTypeCode      · REQUIRED · LOOKUP_VALID (`AMOUNT_SOURCE_TYPE`, UXD-FIN-009) ·
                            LENGTH (20) · when submit
amountSourceValue         · BUSINESS_RULE (required unless the amount source type is
                            REMAINDER — SRS ENT-FIN-010) · when submit
directionCode             · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) ·
                            LENGTH (10) · when submit
distributionTypeCode      · REQUIRED · LOOKUP_VALID (`DISTRIBUTION_TYPE`, UXD-FIN-010) ·
                            LENGTH (15) · when submit
isRemainderFl             · BUSINESS_RULE (RULE-FIN-003) · when submit
UNIQUE_CHECK : async on `eventTypeCode` via `API-FIN-009` with an EQUALS filter. The check is
               **not** narrowed to active rules, because the server's own uniqueness guard is
               not either — a deactivated rule still holds its event type (SRS §B4). The
               authority remains `FIN-409-RULE-DUP`.
### F3-VALIDATION — RULE-FIN-003      traces=REQ-FIN-009,AC-FIN-009
Statement : The system shall require exactly one line marked as the remainder whenever the set
            forms a compound or percentage distribution.
Message   : from the catalog code `FIN-409-REMAINDER-COUNT` —
            ar: "يلزم تحديد سطر باقٍ واحد بالضبط عند وجود توزيع نسبي" ·
            en: "Exactly one remainder line is required when any percentage distribution is
            present"
Scope     : CREATE and UPDATE of the line set
Field     : isRemainderFl, across the line grid · kind BUSINESS_RULE · when submit
Validation shape : the marker is a single exclusive choice across the grid rather than a free
            checkbox per row, so "exactly one" is expressible before the server says it; and
            the rule's second half — a marker that disagrees with its own REMAINDER
            distribution or amount-source type — is surfaced as the catalog's
            `FIN-422-REMAINDER-MARKER` on the offending row. The count is judged by the server
            over the whole persisted set, which is the only place the whole set exists.
Business-code fields: none — this screen mints no business code.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-003:END -->

<!-- SUB:F3-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F3 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

Validation timing for this form: **on submit** (declared once for the whole page) —
there is no unique field on this screen to check on blur.
### F3-FIELD — SCR-FIN-004 (template header, create)
nameAr, nameEn   · REQUIRED · LENGTH (maxLength 150) · when submit
scheduleTypeCode · REQUIRED · LOOKUP_VALID (`RECURRING_SCHEDULE_TYPE`, UXD-FIN-011) ·
                   LENGTH (15) · when submit
frequencyCode    · BUSINESS_RULE (required when the schedule type is RECURRING; not applicable
                   to REVERSING — SRS ENT-FIN-011) · LOOKUP_VALID (`RECURRING_FREQUENCY`,
                   UXD-FIN-012) · LENGTH (15) · when submit
startDate        · REQUIRED · when submit
endDate          · optional · DATE_RANGE (not before `startDate`) · when submit
### F3-FIELD — SCR-FIN-004 (template line)
accountId        · REQUIRED · when submit
amount           · REQUIRED · BUSINESS_RULE (positive — RULE-FIN-006/POL-FIN-005: the amount
                   carries no sign, the direction does) · when submit
directionCode    · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
dimensionValueId · optional · when submit
### F3-VALIDATION — RULE-FIN-006 (applied at run time, not at save)   traces=REQ-FIN-018,AC-FIN-018
Statement : The system shall reject posting an entry whose total debits do not equal its total
            credits to the smallest currency unit.
Message   : from the catalog code `FIN-409-UNBALANCED` —
            ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي الدائن" ·
            en: "The entry is unbalanced — total debits do not equal total credits"
Scope     : the RUN of the template (API-FIN-014), not its creation — the SRS §B5 is explicit
            that the balance check is applied at run time, not at save time
Field     : the line grid · kind BUSINESS_RULE · when submit (of the run)
Validation shape : the grid shows a running debit and credit total while the template is
            drafted, as a display; it does **not** block the save, because an unbalanced
            template is a legal row the server accepts and refuses only when run. On the run,
            the catalog message is shown as a user message beside the template.
`FIN-400-MISSING-FREQUENCY` is the server's answer to the frequency rule above and is routed
inline to `frequencyCode`; the field is hidden, not disabled, when the schedule type is
REVERSING, because the SRS calls it "not applicable" rather than empty.
Business-code fields: none.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit or on run and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-004:END -->

<!-- SUB:F3-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F3 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

Validation timing for this form: **on submit** (declared once for the whole page).
### F3-FIELD — SCR-FIN-005 (rule header, create)
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sourceAccountId · REQUIRED · when submit
### F3-FIELD — SCR-FIN-005 (allocation target)
targetAccountId      · REQUIRED · when submit
dimensionValueId     · optional · when submit
distributionTypeCode · REQUIRED · LOOKUP_VALID (`DISTRIBUTION_TYPE`, UXD-FIN-010) ·
                       LENGTH (15) · when submit
distributionValue    · BUSINESS_RULE (required unless the distribution type is REMAINDER —
                       SRS ENT-FIN-014) · when submit
isRemainderFl        · BUSINESS_RULE (RULE-FIN-003) · when submit
### F3-VALIDATION — RULE-FIN-003      traces=REQ-FIN-025,AC-FIN-025
Statement : The system shall require exactly one target marked as the remainder whenever the
            set forms a compound or percentage distribution.
Message   : from the catalog code `FIN-409-REMAINDER-COUNT` — the same ar/en pair the rule
            declares, shown on the target grid; a marker disagreeing with its own type is the
            catalog's `FIN-422-REMAINDER-MARKER` on the offending row
Scope     : CREATE of the target set, and again at RUN — the server re-validates the set when
            the rule runs, not only when it is created
Field     : isRemainderFl, across the target grid · kind BUSINESS_RULE · when submit
Validation shape : one exclusive marker across the grid, as on SCR-FIN-003. The grid also
            shows the percentage targets' running sum as a display.
### F3-VALIDATION — RULE-FIN-010      traces=REQ-FIN-026,AC-FIN-026
Statement : The system shall compute the remainder line's amount as a difference after every
            percentage line rounds to the smallest currency unit, and that amount must be
            positive.
Message   : from the catalog codes `FIN-422-REMAINDER-NOT-POSITIVE` and the rule's own text —
            ar: "سطر الباقي يُحسب كفرق، لا كنسبة" ·
            en: "The remainder line is computed as a difference, never as a percentage"
Scope     : the RUN of the rule (API-FIN-017)
Field     : the remainder target · kind BUSINESS_RULE · when submit (of the run)
Validation shape : **server-side only, and deliberately not previewed.** The remainder depends
            on the source account's balance at the moment of the run, which no published
            endpoint gives this screen; the remainder cell therefore shows the word
            "الباقي / remainder" instead of a figure. Showing a predicted number would invite
            trust in a value the server has not produced, and the rule's own message says the
            remainder is a difference and never a percentage.
Business-code fields: none.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE or UPDATE receives `FIN-403-FORBIDDEN`
on submit or on run and the page shows the localized forbidden message (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-005:END -->

<!-- SUB:F3-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F3 · SCR-FIN-006 — قيود اليومية / Journal entries

Validation timing for this form: **on submit** (declared once for the whole entry page).
REQ-FIN-015 requires every failing check to come back together, so the submission is the point
at which the entry is judged; nothing pre-empts it.
### F3-FIELD — SCR-FIN-006 (entry header, create)
docDate         · REQUIRED · DATE_RANGE (inside the selected period — RULE-FIN-017) · when submit
fiscalYearId    · REQUIRED · when submit
periodId        · REQUIRED · BUSINESS_RULE (must belong to the selected year — RULE-FIN-017) ·
                  when submit
journalTypeCode · REQUIRED, fixed to `MANUAL`, read-only — in the model because the request
                  requires it, not an input (ADR-FIN-008)
descriptionAr, descriptionEn · optional · when submit
### F3-FIELD — SCR-FIN-006 (entry line, repeating)
accountId       · REQUIRED · BUSINESS_RULE (a leaf, active account — RULE-FIN-007) · when submit
amount          · REQUIRED · BUSINESS_RULE (positive — POL-FIN-005) · when submit
directionCode   · REQUIRED · LOOKUP_VALID (`DEBIT_CREDIT`, UXD-FIN-002) · LENGTH (10) · when submit
descriptionAr, descriptionEn · optional
dimensions[].dimensionId, dimensions[].dimensionValueId · REQUIRED together when a dimension
                  is used · BUSINESS_RULE (the value must belong to the dimension and be
                  active — RULE-FIN-009) · when submit
### F3-VALIDATION — RULE-FIN-006      traces=REQ-FIN-018,AC-FIN-018
Statement : total debits must equal total credits to the smallest currency unit.
Message   : `FIN-409-UNBALANCED` — ar: "القيد غير متوازن — إجمالي المدين لا يساوي إجمالي
            الدائن" · en: "The entry is unbalanced — total debits do not equal total credits"
Scope     : CREATE
Field     : the line grid · kind BUSINESS_RULE · when submit
Validation shape : the live totals at the foot of the grid show the difference as the user
            types, and the Post affordance stays enabled regardless. Disabling it would hide
            the other failing checks REQ-FIN-015 asks to be shown together.
### F3-VALIDATION — RULE-FIN-007      traces=REQ-FIN-019,AC-FIN-019
Statement : a line may not target an account that is not a leaf, not active, or not marked as
            accepting direct posting.
Message   : `FIN-409-NOT-POSTABLE-ACCOUNT` — ar: "الحساب المستهدف لا يقبل ترحيلاً مباشرًا" ·
            en: "The target account does not accept direct posting"
Scope     : CREATE · Field : accountId per line · kind BUSINESS_RULE · when submit
Validation shape : the account picker filters to `isLeafFl = true` and `isActiveFl = true`
            through API-FIN-001's own filters, so the common case never reaches the server as
            a failure; the server's refusal is still routed to the offending line, because the
            account's state may have changed since the picker loaded.
### F3-VALIDATION — RULE-FIN-008      traces=REQ-FIN-020,AC-FIN-020
Statement : the entry's period must be Open at the moment of posting.
Message   : `FIN-409-PERIOD-NOT-OPEN` — ar: "الفترة المستهدفة غير مفتوحة" ·
            en: "The target period is not open"
Scope     : CREATE · Field : periodId · kind BUSINESS_RULE · when submit
Validation shape : **server-side only at the moment that matters.** The period select shows
            each period's state and defaults to an Open one, but the check is at post time, not
            build time (RULE-FIN-008's own words), so a period that closed while the entry was
            being typed is caught by the server and its message routed to the period field.
### F3-VALIDATION — RULE-FIN-009      traces=REQ-FIN-021,AC-FIN-021
Statement : a cited dimension value must belong to its stated dimension and be active.
Message   : `FIN-409-INVALID-DIMENSION` — ar: "قيمة البُعد غير صالحة" ·
            en: "The dimension value is invalid"
Scope     : CREATE · Field : the line's dimension pair · kind LOOKUP_VALID + BUSINESS_RULE ·
            when submit
Validation shape : the value select is loaded from API-FIN-008 filtered by the chosen
            dimension and by `isActiveFl`, so it cannot offer a value of another dimension;
            activity can still change under it, and the server's refusal names the line.
### F3-VALIDATION — RULE-FIN-017      traces=REQ-FIN-014,AC-FIN-014
Statement : the submitted period must belong to the submitted fiscal year, and the document
            date must fall inside that period.
Message   : from the catalog codes `FIN-400-PERIOD-NOT-IN-YEAR` and
            `FIN-400-DOCDATE-OUTSIDE-PERIOD` —
            ar: "الفترة المحددة لا تتبع السنة المالية المحددة، أو تاريخ المستند خارج نطاقها" ·
            en: "The selected period does not belong to the selected fiscal year, or the
            document date falls outside it"
Scope     : CREATE · Field : fiscalYearId, periodId, docDate · kind DATE_RANGE +
            BUSINESS_RULE · when submit
Validation shape : the period select is narrowed to the chosen year and the date picker is
            bounded by the selected period's own `startDate` and `endDate`, both of which the
            period row already carries — so the pairing is expressible client-side and the two
            catalog codes are routed inline to the fields they name.
### F3-VALIDATION — RULE-FIN-016      traces=REQ-FIN-016,AC-FIN-016
Statement : a POSTED entry may not be edited or deleted; correction is only through a reversal.
Message   : the rule's own text — ar: "القيد المُرحَّل مقفل؛ التصحيح فقط عبر العكس" ·
            en: "A posted entry is locked; correction is only through a reversal"
Scope     : ALL · Field : the whole entry · kind BUSINESS_RULE · not a form check at all
Validation shape : there is **no form to validate**: a posted entry opens read-only with no
            edit and no delete affordance anywhere on it, and the rule is expressed by the
            absence of the path rather than by a message on a control that would refuse.
### F3-VALIDATION — RULE-FIN-013      traces=REQ-FIN-030,AC-FIN-030
Statement : a reverse action is rejected on an entry that is not POSTED.
Message   : `FIN-409-NOT-POSTED` — ar: "لا يمكن عكس قيد غير مُرحَّل" ·
            en: "A non-posted entry cannot be reversed" — and `FIN-409-ALREADY-REVERSED` for
            an entry that already carries a reversal link
Scope     : the reverse action · Field : none (a row action) · kind BUSINESS_RULE · when submit
Validation shape : the affordance is drawn only on an entry whose `statusCode` is POSTED and
            whose `reversalEntryId` is absent, both of which the response carries; the server's
            refusal is still shown, because the row may be stale.
Business-code fields: `docNo` is system-generated and displayed read-only; the form never
composes or predicts it.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE, or without the reverse action, receives
`FIN-403-FORBIDDEN` on submit and the page shows the localized forbidden message; no field is
pre-emptively disabled, because neither permission is readable (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-006:END -->

<!-- SUB:F3-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F3 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

Validation timing for this form: **on blur for the year code, on submit for the rest**.
The period transitions carry no form at all — each is a path-id call with no body.
### F3-FIELD — SCR-FIN-007 (fiscal year, create)
code        · REQUIRED · LENGTH (maxLength 10) · UNIQUE_CHECK · when blur
startDate   · REQUIRED · when submit
endDate     · REQUIRED · DATE_RANGE (after `startDate`) · when submit
periodCount · REQUIRED · when submit
UNIQUE_CHECK : the year code has no published search to check against — no fiscal-year search
               exists (ADR-FIN-006) — so the check is **not** written as an async pre-check.
               `FIN-409-YEAR-DUP` from the server is the only authority, routed inline to
               `code`. A pre-check over the period rows would test a proxy, not the code.
### F3-VALIDATION — RULE-FIN-014      traces=REQ-FIN-035,AC-FIN-035
Statement : The system shall reject any attempt to reopen a Hard Closed period.
Message   : from the catalog code `FIN-409-NOT-REOPENABLE` —
            ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" ·
            en: "The period is hard-closed and cannot be reopened"
Scope     : the open action (API-FIN-024)
Field     : none — a row action · kind BUSINESS_RULE · when submit
Validation shape : the row offers only the transitions SRS §A7 allows from its current state,
            so a hard-closed row shows no Open affordance at all; the catalog message is still
            routed to a user message, because a row may be stale when the action is taken.
### F3-VALIDATION — RULE-FIN-015      traces=REQ-FIN-038,AC-FIN-038
Statement : The system shall gate the period-close-approval action behind a permission
            distinct from the journal-entry-creation permission, enforced by the Security
            module.
Message   : the rule's own text — ar: "صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود" ·
            en: "The close-approval permission is separate from the entry-creation permission"
            — and, on refusal, the catalog's `FIN-403-FORBIDDEN`
Scope     : the hard-close and year-end-close actions
Field     : none — a row and a header action · kind BUSINESS_RULE · when submit
Validation shape : **server-side only, and by design.** The rule's own `Data source` line
            reads DEFERRED — there is no FIN-side fact to read — and no published endpoint
            tells this screen whether the caller holds `PERM_FIN_PERIODS_CLOSE_APPROVE`. The
            affordance therefore renders for anyone holding the screen and the server's 403 is
            the answer (ADR-FIN-005). Hiding the button would be a weaker copy of a check that
            already exists where the rule puts it.
The year-end close additionally answers `FIN-409-PERIODS-NOT-CLOSED` when a period of the year
is not hard-closed; the header shows that count as context beside the affordance, not as a gate.
Business-code fields: the year `code` is client-defined, not platform-numbered, and is
read-only after create because no update endpoint exists.
Locale       : session → browser → `ar`.
Permission-driven behaviour: as above — the forbidden message is the localized catalog text,
never a silent no-op.

<!-- SUB:F3-SCR-FIN-007:END -->

<!-- SUB:F3-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F3 · SCR-FIN-008 — دفتر الحساب / Account ledger

This screen has **no form**: SRS SCR-REQ-FIN-008 §B3 reads "not applicable — read-only
report", and every field of `AccountLedgerResponse` is read-only.
### F3-FIELD — SCR-FIN-008 (filters, not a form)
accountId        · REQUIRED (the endpoint's required query param) — the report does not run
                   without it, and the screen shows its choose-an-account state instead
fromDate, toDate · optional · DATE_RANGE (`toDate` not before `fromDate`)
dimensionId, dimensionValueId · optional · the value select is loaded from API-FIN-008
                   filtered by the chosen dimension, so it cannot offer a foreign value
Validation shape : filter validation only, written with `zod` over the route's search params
                   so that an address someone shared is validated the same way a typed filter
                   is. No business rule is enforced here, because nothing is written.
No RULE-* is enforced on this screen. `FIN-404-ACCOUNT` from the server is shown as a user
message when the account id in the address does not resolve — which is the case a shared link
to a since-deleted account produces.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen — the navigation
guard of SEC-FE stops the route (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-008:END -->

<!-- SUB:F3-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F3 · SCR-FIN-009 — ميزان المراجعة / Trial balance

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-009 (filters, not a form)
periodId        · optional · the select is served by the shared fiscal-period query
accountTypeCode · optional · LOOKUP_VALID (`ACCOUNT_TYPE`, UXD-FIN-001) — the option list is
                  runtime-loaded, never a static list
Validation shape : filter validation only, over the route's search params. Both filters are
                  optional and the unfiltered request is valid, so there is no required-field
                  state to enforce.
No RULE-* is enforced on this screen. REQ-FIN-040's balance property is asserted by the server
and rendered from `balanced`; the client does not re-derive it, and there is no client-side
condition under which the screen would contradict the report.
`FIN-404-PERIOD` is shown as a user message when a supplied period id does not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-009:END -->

<!-- SUB:F3-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F3 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-010 (filters, not a form)
fiscalYearId · REQUIRED (the endpoint's required query param) — the report does not run until
               it is chosen, and the screen shows its choose-a-year state instead of a blank
               statement
asOfDate     · optional cut-off
Validation shape : filter validation only, over the route's search params.
No RULE-* is enforced on this screen. REQ-FIN-041's continuity is a property of the posted
data — the prior year's closing balances are the opening entry's posted lines — and nothing
here asserts or recomputes it.
`FIN-404-YEAR` is shown as a user message when the year in the address does not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-010:END -->

<!-- SUB:F3-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F3 · SCR-FIN-011 — قائمة الدخل / Income statement

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-011 (filters, not a form)
fiscalYearId             · REQUIRED (the endpoint's required query param)
fromPeriodId, toPeriodId · optional · both selects narrowed to the chosen year, and
                           `toPeriodId` not before `fromPeriodId`
Validation shape : filter validation only, over the route's search params. The date bounds are
                   NOT validated here: the server derives `fromDate`/`toDate` from the chosen
                   periods and returns them, so the client has nothing of its own to check.
No RULE-* is enforced on this screen. REQ-FIN-042's "opens at zero" is the server's result for
a freshly closed year, and the screen labels an all-zero statement as such rather than treating
it as an absence of data.
`FIN-404-YEAR` and `FIN-404-PERIOD` are shown as user messages when an id in the address does
not resolve.
Business-code fields: `accountCode` is displayed read-only, from the response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-011:END -->

<!-- SUB:F3-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F3 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

This screen has **no form** (SRS §B3 "not applicable").
### F3-FIELD — SCR-FIN-012 (filters, not a form)
dimensionId      · REQUIRED (the endpoint's required query param) — the report does not run
                   until a dimension is chosen
dimensionValueId · optional · the select is loaded from API-FIN-008 filtered by the chosen
                   dimension, so it cannot offer a value of another dimension
periodId         · optional · served by the shared fiscal-period query
Validation shape : filter validation only, over the route's search params.
No RULE-* is enforced on this screen. REQ-FIN-043's "never by the base account alone" is a
property of the rows the server returns — one per account-and-dimension-value pair — and the
screen neither merges nor re-aggregates them.
`FIN-404-DIMENSION` and `FIN-404-PERIOD` are shown as user messages when an id in the address
does not resolve.
Business-code fields: `accountCode` and `dimensionValueCode` are displayed read-only, from the
response.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen (ADR-FIN-005).

<!-- SUB:F3-SCR-FIN-012:END -->

<!-- PHASE:F3:END -->

<!-- PHASE:F4:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 4 — F4 — Screens & Routes

One block per `SCR-*`: routes, chunk, guard, components, mode, facade, shared UI and
cross-module citations. Routes are named by the container pattern — `TREE_MASTER_DETAIL` → a
TreePage hosting the tree and its detail, with the tree route registered **before** any `:id`
route; `FULL_PAGE` with an entry → SearchPage + EntryPage on separate routes; `FULL_PAGE` with
no entry sub-view → a single Page and no entry route. One lazy chunk per composite screen:
search and entry are separate components under ONE `SCR-*` sharing ONE chunk, never a second
chunk for a sub-view. Every `PERM_*` name below is the backend's, never invented here, and
every route sits under the module segment `/finance`.

<!-- SUB:F4-SCR-FIN-001:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001 -->
### F4 · SCR-FIN-001 — شجرة الحسابات / Chart of accounts

### F4-SCREEN — SCR-FIN-001            traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `accounts`, under the module segment `/finance` —
               `/finance/accounts` (the tree, registered **before** any `:id` route so a node
               id is never matched as the tree itself) ·
               `/finance/accounts/new` (create, the form beside the tree) ·
               `/finance/accounts/:id` (view) ·
               `/finance/accounts/:id/edit` (edit)
Chunk        : one lazy chunk for this composite screen — tree and form share it; the form is
               never a second chunk
Guard        : every route element guarded by `PERM_FIN_ACCOUNTS_VIEW`, evaluated as
               "`FIN_ACCOUNTS` is present in the caller's effective menu" (ADR-FIN-005).
               CREATE and UPDATE are not readable from any published endpoint, so `/new` and
               `/:id/edit` carry the same VIEW guard and the server's 403 is the authority on
               the write itself.
Components   : `AccountsTreePage` (route-level, TREE_MASTER_DETAIL — hosts the tree and the
               detail form) · `AccountTree`, `AccountFilters`, `AccountForm`,
               `AccountDeactivateConfirm` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` → CREATE,
               `/:id/edit` → EDIT, `/:id` → VIEW — never from a parent prop
Facade       : the SCR-FIN-001 facade of F2; the page never calls a query directly
Shared UI    : tree, filter bar, text field, select, checkbox, confirmation dialog, inline
               field errors, localized message banner
Cross-module : UXD-FIN-001 (account type) and UXD-FIN-002 (nature) — both fields display a
               value whose authoritative source is the lookup module
The selected node is a route param, so an account being edited is linkable and the browser's
back gesture returns to the tree. Creating a child from a selected node pre-fills the parent
and the tree scrolls to the new row on success.

<!-- SUB:F4-SCR-FIN-001:END -->

<!-- SUB:F4-SCR-FIN-002:START traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002 -->
### F4 · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values

### F4-SCREEN — SCR-FIN-002            traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035
Routes       : base slug `dimensions`, under `/finance` —
               `/finance/dimensions` (the dimension list) ·
               `/finance/dimensions/new` (create a dimension — a **static** segment registered
               BEFORE the `:id` routes) ·
               `/finance/dimensions/:id` (the dimension with its values) ·
               `/finance/dimensions/:id/values/new` (create a value under it)
Chunk        : one lazy chunk for this composite screen — both panes and both forms share it
Guard        : every route element guarded by `PERM_FIN_DIMENSIONS_VIEW`, evaluated as
               "`FIN_DIMENSIONS` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `DimensionsPage` (route-level, TREE_MASTER_DETAIL) · `DimensionList`,
               `DimensionForm`, `DimensionValueTable`, `DimensionValueForm`,
               `DimensionValueDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match — there is no EDIT mode on either
               resource, because neither has an update endpoint (ADR-FIN-006)
Facade       : the SCR-FIN-002 facade of F2
Shared UI    : split pane, data table, text field, number field, confirmation dialog, inline
               errors, localized message banner
Cross-module : none — every field on this screen is FIN's own (ENT-FIN-002, ENT-FIN-003), and
               no `UXD-*` is cited
The selected dimension is a route param, so a dimension's value list is a shareable address.
No deactivate affordance is drawn on the dimension itself: no endpoint exists (ADR-FIN-006).

<!-- SUB:F4-SCR-FIN-002:END -->

<!-- SUB:F4-SCR-FIN-003:START traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003 -->
### F4 · SCR-FIN-003 — قواعد المحرك / Engine rules

### F4-SCREEN — SCR-FIN-003            traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-002,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010
Routes       : base slug `engine-rules`, under `/finance` —
               `/finance/engine-rules` (search) ·
               `/finance/engine-rules/new` (create the rule header — a static segment before
               the `:id` routes) ·
               `/finance/engine-rules/:id` (the rule page with its line grid) ·
               `/finance/engine-rules/:id/lines/new` (add a line)
Chunk        : one lazy chunk for this composite screen — search page and rule page share it
Guard        : every route element guarded by `PERM_FIN_RULES_VIEW`, evaluated as
               "`FIN_RULES` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `EngineRulesSearchPage` (route-level, FULL_PAGE) · `EngineRulePage`
               (route-level, FULL_PAGE — the header and its lines) · `RuleFilters`,
               `RuleResultTable`, `RuleHeaderForm`, `RuleLineGrid`, `RuleLineForm`,
               `RuleDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match; there is no EDIT mode — neither
               the rule nor the line has an update endpoint (ADR-FIN-006)
Facade       : the SCR-FIN-003 facade of F2
Shared UI    : data table, filter bar, text field, select, exclusive-choice control (the
               remainder marker across the grid), confirmation dialog, inline errors,
               localized message banner
Cross-module : UXD-FIN-007 (event type), UXD-FIN-008 (account derivation type), UXD-FIN-009
               (amount source type), UXD-FIN-010 (distribution type), UXD-FIN-002 (direction)
Search and the rule page are separate components under ONE `SCR-*` sharing ONE chunk, linked
by the `:id` route param. The line grid's three references stay three columns and are never
collapsed into one control.

<!-- SUB:F4-SCR-FIN-003:END -->

<!-- SUB:F4-SCR-FIN-004:START traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004 -->
### F4 · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates

### F4-SCREEN — SCR-FIN-004            traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-002,UXD-FIN-011,UXD-FIN-012
Routes       : base slug `recurring-templates`, under `/finance` —
               `/finance/recurring-templates` (search) ·
               `/finance/recurring-templates/new` (create — a static segment registered BEFORE
               the `:id` route) ·
               `/finance/recurring-templates/:id` (the template page, read-only)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_RECURRING_TEMPLATES_VIEW`, evaluated
               as "`FIN_RECURRING_TEMPLATES` is present in the caller's effective menu"
               (ADR-FIN-005)
Components   : `RecurringTemplatesSearchPage` (route-level, FULL_PAGE) ·
               `RecurringTemplatePage` (route-level, FULL_PAGE — header and line grid) ·
               `TemplateFilters`, `TemplateResultTable`, `TemplateHeaderForm`,
               `TemplateLineGrid`, `TemplateRunConfirm`, `TemplateDeactivateConfirm`
               (presentational)
Mode         : CREATE | VIEW resolved from the route match; no EDIT mode exists (ADR-FIN-006)
Facade       : the SCR-FIN-004 facade of F2
Shared UI    : data table, filter bar, text field, select, date field, number field,
               confirmation dialog, inline errors, localized message banner
Cross-module : UXD-FIN-011 (schedule type), UXD-FIN-012 (frequency), UXD-FIN-002 (direction)
The header and its lines are one submission, so the create route is a single page rather than
a wizard. On a successful run the returned entry's id is used to offer navigation to
`/finance/journal-entries/:id`, which is SCR-FIN-006's own route and guard — this screen never
renders an entry itself.

<!-- SUB:F4-SCR-FIN-004:END -->

<!-- SUB:F4-SCR-FIN-005:START traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010,SCR-FIN-005 -->
### F4 · SCR-FIN-005 — قواعد التوزيع / Allocation rules

### F4-SCREEN — SCR-FIN-005            traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,UXD-FIN-010
Routes       : base slug `allocation-rules`, under `/finance` —
               `/finance/allocation-rules` (search) ·
               `/finance/allocation-rules/new` (create — a static segment before the `:id`
               route) ·
               `/finance/allocation-rules/:id` (the rule page, read-only)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_ALLOCATION_RULES_VIEW`, evaluated as
               "`FIN_ALLOCATION_RULES` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `AllocationRulesSearchPage` (route-level, FULL_PAGE) · `AllocationRulePage`
               (route-level, FULL_PAGE — header and target grid) · `AllocationRuleFilters`,
               `AllocationRuleResultTable`, `AllocationRuleHeaderForm`, `AllocationTargetGrid`,
               `AllocationRunConfirm`, `AllocationDeactivateConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match; no EDIT mode exists (ADR-FIN-006)
Facade       : the SCR-FIN-005 facade of F2
Shared UI    : data table, filter bar, text field, select, number field, exclusive-choice
               control (the remainder target), confirmation dialog, inline errors, localized
               message banner
Cross-module : UXD-FIN-010 (distribution type)
The remainder target's amount cell renders the word "الباقي / remainder" rather than a figure,
which is the routing decision of F3's RULE-FIN-010 block expressed as a component. On a
successful run the returned entry is offered on SCR-FIN-006's route, never rendered here.

<!-- SUB:F4-SCR-FIN-005:END -->

<!-- SUB:F4-SCR-FIN-006:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006 -->
### F4 · SCR-FIN-006 — قيود اليومية / Journal entries

### F4-SCREEN — SCR-FIN-006            traces=REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-027,AC-FIN-028,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-021,API-FIN-022,UXD-FIN-002,UXD-FIN-005,UXD-FIN-006
Routes       : base slug `journal-entries`, under `/finance` —
               `/finance/journal-entries` (search) ·
               `/finance/journal-entries/new` (the manual entry page — a static segment
               registered BEFORE the `:id` route) ·
               `/finance/journal-entries/:id` (the entry, read-only, with the Reverse action)
               There is no `:id/edit` route at all: a POSTED entry is locked (RULE-FIN-016),
               and the absence of the route is how that is expressed in the router.
Chunk        : one lazy chunk for this composite screen — search, entry page and the read-only
               entry share it
Guard        : every route element guarded by `PERM_FIN_JOURNAL_ENTRIES_VIEW`, evaluated as
               "`FIN_JOURNAL_ENTRIES` is present in the caller's effective menu"
               (ADR-FIN-005). CREATE and the custom reverse action are not readable, so `/new`
               carries the same VIEW guard and the server's 403 is the authority on the write.
Components   : `JournalEntriesSearchPage` (route-level, FULL_PAGE) · `JournalEntryPage`
               (route-level, FULL_PAGE — create mode, or read-only on a posted entry) ·
               `EntryFilters`, `EntryResultTable`, `EntryHeaderForm`, `EntryLineGrid`,
               `EntryLineDimensions`, `EntryTotalsBar`, `ReverseConfirm`,
               `ValidationFailureList` (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new` → CREATE, `/:id` → VIEW.
               There is no EDIT mode to resolve.
Facade       : the SCR-FIN-006 facade of F2; pages never call queries directly
Shared UI    : data table, filter bar, date field, date-range filter, select, number field,
               editable line grid, totals bar, confirmation dialog, inline errors, localized
               message banner
Cross-module : UXD-FIN-005 (journal type), UXD-FIN-006 (status), UXD-FIN-002 (direction)
`ValidationFailureList` exists because REQ-FIN-015 asks for every failing check at once: the
refusals of one submission are listed together above the entry, each also routed inline to the
line or field it names, and nothing the user typed is cleared. API-FIN-020 has no component
and no route on this screen (ADR-FIN-007); its entries appear in the list like any other.

<!-- SUB:F4-SCR-FIN-006:END -->

<!-- SUB:F4-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F4 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

### F4-SCREEN — SCR-FIN-007            traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004
Routes       : base slug `fiscal-periods`, under `/finance` —
               `/finance/fiscal-periods` (the year list beside the period list, registered
               **before** any `:id` route) ·
               `/finance/fiscal-periods/new-year` (create a fiscal year — a static segment
               before the `:id` routes) ·
               `/finance/fiscal-periods/:yearId` (that year's periods)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_FIN_PERIODS_VIEW`, evaluated as
               "`FIN_PERIODS` is present in the caller's effective menu" (ADR-FIN-005).
               `PERM_FIN_PERIODS_CLOSE_APPROVE` is not readable, so the hard-close and
               year-end-close affordances render under the same VIEW guard and the server's
               403 is the authority — which is exactly what RULE-FIN-015 asks for.
Components   : `FiscalCalendarPage` (route-level, TREE_MASTER_DETAIL — years beside their
               periods) · `FiscalYearList`, `FiscalYearForm`, `FiscalPeriodTable`,
               `PeriodFilters`, `PeriodTransitionConfirm`, `YearEndCloseConfirm`
               (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new-year` → CREATE,
               `/:yearId` → VIEW. Neither resource has an EDIT mode (ADR-FIN-006).
Facade       : the SCR-FIN-007 facade of F2
Shared UI    : split pane, data table, text field, date field, number field, confirmation
               dialog, global busy indicator (the year-end close alone), inline errors,
               localized message banner
Cross-module : UXD-FIN-003 (period state), UXD-FIN-004 (fiscal year status)
The year list is derived from the period rows' `fiscalYearId` (ADR-FIN-006) and is presented
as an ordinary list; the indirection is not exposed to the user. Each period row renders only
the transitions §A7 allows from its current state, so a hard-closed row has no Open affordance
at all. On a successful year-end close the two returned entries are offered on SCR-FIN-006's
route.

<!-- SUB:F4-SCR-FIN-007:END -->

<!-- SUB:F4-SCR-FIN-008:START traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005,SCR-FIN-008 -->
### F4 · SCR-FIN-008 — دفتر الحساب / Account ledger

### F4-SCREEN — SCR-FIN-008            traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,UXD-FIN-001,UXD-FIN-002,UXD-FIN-005
Routes       : base slug `account-ledger`, under `/finance` —
               `/finance/account-ledger` — the only route; no `new`, no `:id`, no `:id/edit`,
               because this screen addresses no record it could edit. The account, date range
               and dimension live in the route's search params, so the report IS its address
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_ACCOUNT_LEDGER_VIEW`, evaluated as
               "`FIN_ACCOUNT_LEDGER` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `AccountLedgerPage` (route-level, FULL_PAGE) · `LedgerFilters`,
               `LedgerSummaryHeader`, `LedgerRowTable` (presentational)
Mode         : not applicable — no CREATE, EDIT or VIEW mode exists to resolve; this screen
               writes nothing
Facade       : the SCR-FIN-008 facade of F2
Shared UI    : filter bar, account picker, date-range filter, select, data table, localized
               message banner
Cross-module : UXD-FIN-001 (account type), UXD-FIN-002 (nature and direction), UXD-FIN-005
               (journal type on each row)
Each row's document number links to `/finance/journal-entries/:id`, which is SCR-FIN-006's own
route and carries its own guard — the third hop of REQ-FIN-046's chain. This screen is the
drill-down target of SCR-FIN-009 and SCR-FIN-012, and arrives with its filters already in the
address.

<!-- SUB:F4-SCR-FIN-008:END -->

<!-- SUB:F4-SCR-FIN-009:START traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002,SCR-FIN-009 -->
### F4 · SCR-FIN-009 — ميزان المراجعة / Trial balance

### F4-SCREEN — SCR-FIN-009            traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,API-FIN-029,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `trial-balance`, under `/finance` —
               `/finance/trial-balance` — the only route; both filters live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_TRIAL_BALANCE_VIEW`, evaluated as
               "`FIN_TRIAL_BALANCE` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `TrialBalancePage` (route-level, FULL_PAGE) · `TrialBalanceFilters`,
               `BalancedBanner`, `AccountBalanceTable` (presentational)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-009 facade of F2
Shared UI    : filter bar, select, data table, status banner, localized message banner
Cross-module : UXD-FIN-001 (account type), UXD-FIN-002 (nature)
`BalancedBanner` renders the server's `balanced` value and nothing derived: REQ-FIN-040 makes
the equality the report's property, and a client that recomputed it could contradict the
report it is displaying. Each row's account links to `/finance/account-ledger` carrying the
account and the period's range — the second hop of the drill-down chain. This screen is itself
the target of SCR-FIN-010's and SCR-FIN-011's statement lines.

<!-- SUB:F4-SCR-FIN-009:END -->

<!-- SUB:F4-SCR-FIN-010:START traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002,SCR-FIN-010 -->
### F4 · SCR-FIN-010 — الميزانية العمومية / Balance sheet

### F4-SCREEN — SCR-FIN-010            traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,API-FIN-030,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `balance-sheet`, under `/finance` —
               `/finance/balance-sheet` — the only route; the fiscal year and as-of date live
               in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_BALANCE_SHEET_VIEW`, evaluated as
               "`FIN_BALANCE_SHEET` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `BalanceSheetPage` (route-level, FULL_PAGE) · `StatementFilters`,
               `StatementSection`, `AccountBalanceTable` (presentational — the table is the
               same component SCR-FIN-009 uses, since the row shape is the same)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-010 facade of F2
Shared UI    : filter bar, select, date field, data table, section headings, localized message
               banner
Cross-module : UXD-FIN-001 (account type — the section heading), UXD-FIN-002 (nature)
The required fiscal year gates the call, so the page shows a choose-a-year state rather than a
blank statement. Each row links to `/finance/trial-balance` narrowed to that account type —
the first hop of REQ-FIN-046's chain.

<!-- SUB:F4-SCR-FIN-010:END -->

<!-- SUB:F4-SCR-FIN-011:START traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002,SCR-FIN-011 -->
### F4 · SCR-FIN-011 — قائمة الدخل / Income statement

### F4-SCREEN — SCR-FIN-011            traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,API-FIN-031,UXD-FIN-001,UXD-FIN-002
Routes       : base slug `income-statement`, under `/finance` —
               `/finance/income-statement` — the only route; the fiscal year and the two
               period ids live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_INCOME_STATEMENT_VIEW`, evaluated as
               "`FIN_INCOME_STATEMENT` is present in the caller's effective menu" (ADR-FIN-005)
Components   : `IncomeStatementPage` (route-level, FULL_PAGE) · `StatementFilters`,
               `StatementSection`, `AccountBalanceTable`, `NetResultFooter` (presentational —
               the first three shared with SCR-FIN-010)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-011 facade of F2
Shared UI    : filter bar, select, data table, section headings, localized message banner
Cross-module : UXD-FIN-001 (account type — the section heading), UXD-FIN-002 (nature)
The period range is two selects narrowed to the chosen year, and the dates the server derived
from them are shown read-only beside the filters. An all-zero statement for a freshly closed
year is labelled as the correct result of REQ-FIN-042, not as an empty list. Each row links to
`/finance/trial-balance` for that account type.

<!-- SUB:F4-SCR-FIN-011:END -->

<!-- SUB:F4-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012 -->
### F4 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F4-SCREEN — SCR-FIN-012            traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002
Routes       : base slug `dimension-reports`, under `/finance` —
               `/finance/dimension-reports` — the only route; the dimension, its value and the
               period live in its search params
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_FIN_DIMENSION_REPORTS_VIEW`, evaluated as
               "`FIN_DIMENSION_REPORTS` is present in the caller's effective menu"
               (ADR-FIN-005)
Components   : `DimensionReportPage` (route-level, FULL_PAGE) · `DimensionReportFilters`,
               `DimensionReportTable` (presentational)
Mode         : not applicable — this screen writes nothing
Facade       : the SCR-FIN-012 facade of F2
Shared UI    : filter bar, select, data table, localized message banner
Cross-module : UXD-FIN-002 (nature). The dimension and its values are FIN's own entities, read
               through this module's own endpoints, so they cite no `UXD-*`
The table renders the account and the dimension value as two columns of the same row and never
merges them, which is REQ-FIN-043 expressed in the component. Each row links to
`/finance/account-ledger` carrying the account **and** the dimension pair, so the ledger behind
the figure shows the same slice.

<!-- SUB:F4-SCR-FIN-012:END -->

<!-- PHASE:F4:END -->

<!-- PHASE:SEC-FE:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012,REQ-FIN-044,AC-FIN-044 -->
## PHASE 5 — SEC-FE

The frontend half of the security model, per `SCR-*`: the navigation guard and the per-action
UI behaviour. Permission names are the backend registry's and the SRS Access summary's, never
redeclared. One mechanism gates every screen — the **menu gate**: the screen's page code is
present in the effective menu the security module serves for this caller, which exists because
REQ-FIN-044 registers FIN's module, screens and actions there as data. Action-level
permissions are not readable from any published endpoint, so an action's affordance renders for
a caller who holds the screen and the server's `FIN-403-FORBIDDEN` is the authority, shown as
its localized catalog message (ADR-FIN-005). Never split — level-1 only.

### SEC-FE · SCR-FIN-001 — شجرة الحسابات / Chart of accounts
Permissions      : `PERM_FIN_ACCOUNTS_VIEW`, `PERM_FIN_ACCOUNTS_CREATE`,
`PERM_FIN_ACCOUNTS_UPDATE`
Navigation guard : `FIN_ACCOUNTS` must be present in the caller's effective menu; a caller
without it is sent to the unauthorized destination, and every route of this screen — the tree,
`new`, `:id`, `:id/edit` — carries the same guard.
Per action       : VIEW → the gate above, exact. CREATE (new account) and UPDATE (edit, and
deactivate) → the affordances render for a caller who holds the screen, and `FIN-403-FORBIDDEN`
from the server is shown as the localized forbidden message (ADR-FIN-005). DELETE → no delete
action exists: deactivation is an UPDATE (API-FIN-004), and the SRS Access summary leaves this
screen's DELETE column empty.

### SEC-FE · SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values
Permissions      : `PERM_FIN_DIMENSIONS_VIEW`, `PERM_FIN_DIMENSIONS_CREATE`,
`PERM_FIN_DIMENSIONS_UPDATE`
Navigation guard : `FIN_DIMENSIONS` must be present in the caller's effective menu; every route
of this screen carries it.
Per action       : VIEW → the gate above. CREATE (a dimension, or a value under it) → the
affordances render and the server's 403 is the authority. UPDATE → it covers exactly one
operation, deactivating a dimension **value** (API-FIN-035); the parent dimension has no
deactivate affordance because no endpoint exists for it (ADR-FIN-006), so nothing is gated
there. DELETE → no delete action exists on this screen.

### SEC-FE · SCR-FIN-003 — قواعد المحرك / Engine rules
Permissions      : `PERM_FIN_RULES_VIEW`, `PERM_FIN_RULES_CREATE`, `PERM_FIN_RULES_UPDATE`
Navigation guard : `FIN_RULES` must be present in the caller's effective menu; every route of
this screen carries it.
Per action       : VIEW → the gate above. CREATE (a rule header) and UPDATE (adding a line,
API-FIN-011; deactivating the rule, API-FIN-034 — both under the one `PERM_FIN_RULES_UPDATE`)
→ the affordances render and the server's 403 is the authority. DELETE → no delete action
exists: there is no rule-line delete endpoint and V24 seeds no `PERM_FIN_RULES_DELETE`
(ADR-FIN-006).

### SEC-FE · SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates
Permissions      : `PERM_FIN_RECURRING_TEMPLATES_VIEW`,
`PERM_FIN_RECURRING_TEMPLATES_CREATE`, `PERM_FIN_RECURRING_TEMPLATES_UPDATE`
Navigation guard : `FIN_RECURRING_TEMPLATES` must be present in the caller's effective menu;
every route of this screen carries it.
Per action       : VIEW → the gate above. CREATE (a template with its lines) and UPDATE (run,
API-FIN-014; deactivate, API-FIN-036 — both under the one
`PERM_FIN_RECURRING_TEMPLATES_UPDATE`) → the affordances render and the server's 403 is the
authority. DELETE → no delete action exists. No Edit affordance is drawn at all, since no
update endpoint is published (ADR-FIN-006) — an absent affordance, not a gated one.

### SEC-FE · SCR-FIN-005 — قواعد التوزيع / Allocation rules
Permissions      : `PERM_FIN_ALLOCATION_RULES_VIEW`, `PERM_FIN_ALLOCATION_RULES_CREATE`,
`PERM_FIN_ALLOCATION_RULES_UPDATE`
Navigation guard : `FIN_ALLOCATION_RULES` must be present in the caller's effective menu; every
route of this screen carries it.
Per action       : VIEW → the gate above. CREATE (a rule with its targets) and UPDATE (run,
API-FIN-017; deactivate, API-FIN-037 — both under the one `PERM_FIN_ALLOCATION_RULES_UPDATE`)
→ the affordances render and the server's 403 is the authority. DELETE → no delete action
exists. No Edit affordance is drawn (ADR-FIN-006).

### SEC-FE · SCR-FIN-006 — قيود اليومية / Journal entries
Permissions      : `PERM_FIN_JOURNAL_ENTRIES_VIEW`, `PERM_FIN_JOURNAL_ENTRIES_CREATE`,
and the custom action `PERM_FIN_JOURNAL_ENTRIES_REVERSE`
Navigation guard : `FIN_JOURNAL_ENTRIES` must be present in the caller's effective menu; the
search, `new` and `:id` routes all carry it.
Per action       : VIEW → the gate above. CREATE (the manual entry, posting included) and the
custom reverse action → the affordances render for a caller who holds the screen, and
`FIN-403-FORBIDDEN` is shown as the localized forbidden message (ADR-FIN-005). UPDATE and
DELETE → **neither exists on this screen at all**, and their absence is RULE-FIN-016 rather
than a permission decision: a posted entry is locked, there is no edit route to guard, and the
SRS Access summary leaves both columns empty.

### SEC-FE · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years
Permissions      : `PERM_FIN_PERIODS_VIEW`, `PERM_FIN_PERIODS_CREATE`,
`PERM_FIN_PERIODS_UPDATE`, and the distinct custom action `PERM_FIN_PERIODS_CLOSE_APPROVE`
Navigation guard : `FIN_PERIODS` must be present in the caller's effective menu; every route of
this screen carries it.
Per action       : VIEW → the gate above, and since API-FIN-033 it is also the permission
behind a real read. CREATE (a fiscal year) and UPDATE (open, soft-close) → the affordances
render and the server's 403 is the authority. The close-approval action (hard-close,
API-FIN-026; year-end close, API-FIN-027) is gated by its **own** permission, distinct from
`PERM_FIN_JOURNAL_ENTRIES_CREATE` — which is exactly what RULE-FIN-015 requires — and it is
**not readable from any published endpoint**, so its affordances render under the screen's
VIEW gate and a caller who does not hold it receives the server's localized forbidden message
(ADR-FIN-005). Hiding the affordance would be a weaker copy of a check the Security module
already performs. DELETE → no delete action exists on this screen.

### SEC-FE · SCR-FIN-008 — دفتر الحساب / Account ledger
Permissions      : `PERM_FIN_ACCOUNT_LEDGER_VIEW`
Navigation guard : `FIN_ACCOUNT_LEDGER` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE: the SRS Access
summary gives this screen VIEW alone, and the screen writes nothing. The links it draws to
SCR-FIN-006 are rendered unconditionally; the target route's own guard stops a caller who does
not hold it.

### SEC-FE · SCR-FIN-009 — ميزان المراجعة / Trial balance
Permissions      : `PERM_FIN_TRIAL_BALANCE_VIEW`
Navigation guard : `FIN_TRIAL_BALANCE` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-008 are rendered unconditionally and the target's guard is what decides.

### SEC-FE · SCR-FIN-010 — الميزانية العمومية / Balance sheet
Permissions      : `PERM_FIN_BALANCE_SHEET_VIEW`
Navigation guard : `FIN_BALANCE_SHEET` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-009 are rendered unconditionally and the target's guard is what decides.

### SEC-FE · SCR-FIN-011 — قائمة الدخل / Income statement
Permissions      : `PERM_FIN_INCOME_STATEMENT_VIEW`
Navigation guard : `FIN_INCOME_STATEMENT` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-009 are rendered unconditionally and the target's guard is what decides.

### SEC-FE · SCR-FIN-012 — تقارير الأبعاد / Dimension reports
Permissions      : `PERM_FIN_DIMENSION_REPORTS_VIEW`
Navigation guard : `FIN_DIMENSION_REPORTS` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE. Its links to
SCR-FIN-008 are rendered unconditionally and the target's guard is what decides.

**Across every screen.** A forbidden response is shown as its localized catalog message,
never as a silent no-op and never as a generic failure. An unauthenticated response returns the
caller to the platform's sign-in destination and discards the server-state cache, so no data of
the previous identity survives into the next. No screen composes a permission name, and no
screen holds a local copy of the caller's grants: the menu response is the single source, and a
failure to load it renders no FIN entry and grants no FIN route — access narrows, never widens.

<!-- PHASE:SEC-FE:END -->

<!-- PHASE:ALIGN-FE:START traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,API-FIN-001,API-FIN-002,API-FIN-003,API-FIN-004,UXD-FIN-001,UXD-FIN-002,SCR-FIN-001,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006,API-FIN-005,API-FIN-006,API-FIN-007,API-FIN-008,API-FIN-035,SCR-FIN-002,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,API-FIN-009,API-FIN-010,API-FIN-011,API-FIN-034,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,SCR-FIN-003,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,API-FIN-012,API-FIN-013,API-FIN-014,API-FIN-036,UXD-FIN-011,UXD-FIN-012,SCR-FIN-004,REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,API-FIN-015,API-FIN-016,API-FIN-017,API-FIN-037,SCR-FIN-005,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-010,AC-FIN-011,AC-FIN-012,AC-FIN-013,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,API-FIN-018,API-FIN-019,API-FIN-020,API-FIN-021,API-FIN-022,UXD-FIN-005,UXD-FIN-006,SCR-FIN-006,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007,REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,API-FIN-028,SCR-FIN-008,REQ-FIN-040,AC-FIN-040,API-FIN-029,SCR-FIN-009,REQ-FIN-041,AC-FIN-041,API-FIN-030,SCR-FIN-010,REQ-FIN-042,AC-FIN-042,API-FIN-031,SCR-FIN-011,REQ-FIN-043,AC-FIN-043,API-FIN-032,SCR-FIN-012 -->
## PHASE 6 — ALIGN-FE

The alignment self-check is this phase's content: see the section of the same name below, whose
`RESULT` row is written by the orchestrator from the analyze report. Never split — level-1 only.

```
ALIGN-FE — FIN v1
row           backing check   assertion
SCREENS       orphans         every SCR-FIN-001..012 is referenced by a plan block — each has
                              one SUB in F1, F2, F3 and F4 (48 SUB blocks) and one RF5 block
                              in SEC-FE
UXD           orphans         every UXD-FIN-001..012 is cited by a plan block — each is named
                              by the F2-LOOKUP of the screens that display its key and by the
                              Cross-module line of those screens' F4 blocks
TRACES        traces          every PHASE and every SUB carries traces=; every UXD traces to
                              its REQ and its AC; every SCR traces to its REQ and, where it
                              displays foreign data, its UXD
API           traces          every API-FIN-* this plan cites is defined in the fetched
                              api-docs — through the API ID BINDING annex of ADR-FIN-002, and
                              never in the backend plan's contract draft. No foreign module's
                              API id is cited here at all; the one cross-module endpoint this
                              frontend depends on is named in ui-ux-spec-fin.md, where its
                              UXD-* are defined
FOREIGN       xref-surface    every reference to another module's surface resolves in that
                              module's own artifacts
REGISTRY      registry-agree  every UXD and SCR defined here is in registry-exec-fe-fin.md,
                              and nothing else is
LANGUAGES     languages       labels and messages in ar + en
MARKERS       markers         the parser reports no structural or semantic error for the
                              frontend track's exec plan
DECISIONS     refs-exist      every ADR this plan cites exists on disk in erp/decisions/FIN/ —
                              ADR-FIN-002, ADR-FIN-003, ADR-FIN-004, ADR-FIN-005, ADR-FIN-006,
                              ADR-FIN-007, ADR-FIN-008
COVERAGE      (the report)    C7.16 and C7.18 — both P3.1 clauses, over backend
                              artifacts this stage does not write. No C8.* or C9.* clause
                              reported having examined nothing
RESULT        PASSED ✓ — 0 findings
```

### Operations coverage

| Operation | API | SCR action | Route | Status |
|---|---|---|---|---|
| search accounts | API-FIN-001 | SCR-FIN-001 search | /finance/accounts | ✓ |
| create account | API-FIN-002 | SCR-FIN-001 create | /finance/accounts/new | ✓ |
| update account | API-FIN-003 | SCR-FIN-001 edit | /finance/accounts/:id/edit | ✓ |
| deactivate account | API-FIN-004 | SCR-FIN-001 deactivate | /finance/accounts/:id | ✓ |
| search dimensions | API-FIN-005 | SCR-FIN-002 search | /finance/dimensions | ✓ |
| create dimension | API-FIN-006 | SCR-FIN-002 create | /finance/dimensions/new | ✓ |
| create dimension value | API-FIN-007 | SCR-FIN-002 create value | /finance/dimensions/:id/values/new | ✓ |
| search dimension values | API-FIN-008 | SCR-FIN-002 value list | /finance/dimensions/:id | ✓ |
| deactivate dimension value | API-FIN-035 | SCR-FIN-002 deactivate value | /finance/dimensions/:id | ✓ |
| search event-type rules | API-FIN-009 | SCR-FIN-003 search | /finance/engine-rules | ✓ |
| create event-type rule | API-FIN-010 | SCR-FIN-003 create | /finance/engine-rules/new | ✓ |
| add rule line | API-FIN-011 | SCR-FIN-003 add line | /finance/engine-rules/:id/lines/new | ✓ |
| deactivate event-type rule | API-FIN-034 | SCR-FIN-003 deactivate | /finance/engine-rules/:id | ✓ |
| search recurring templates | API-FIN-012 | SCR-FIN-004 search | /finance/recurring-templates | ✓ |
| create recurring template | API-FIN-013 | SCR-FIN-004 create | /finance/recurring-templates/new | ✓ |
| run recurring template | API-FIN-014 | SCR-FIN-004 run | /finance/recurring-templates/:id | ✓ |
| deactivate recurring template | API-FIN-036 | SCR-FIN-004 deactivate | /finance/recurring-templates/:id | ✓ |
| search allocation rules | API-FIN-015 | SCR-FIN-005 search | /finance/allocation-rules | ✓ |
| create allocation rule | API-FIN-016 | SCR-FIN-005 create | /finance/allocation-rules/new | ✓ |
| run allocation rule | API-FIN-017 | SCR-FIN-005 run | /finance/allocation-rules/:id | ✓ |
| deactivate allocation rule | API-FIN-037 | SCR-FIN-005 deactivate | /finance/allocation-rules/:id | ✓ |
| search journal entries | API-FIN-018 | SCR-FIN-006 search | /finance/journal-entries | ✓ |
| create manual entry (post) | API-FIN-019 | SCR-FIN-006 post | /finance/journal-entries/new | ✓ |
| build entry from an event | API-FIN-020 | — a host system's call | — (ADR-FIN-007) | ✗ |
| reverse a posted entry | API-FIN-021 | SCR-FIN-006 reverse | /finance/journal-entries/:id | ✓ |
| read an entry with its lines | API-FIN-022 | SCR-FIN-006 read | /finance/journal-entries/:id | ✓ |
| search fiscal periods | API-FIN-033 | SCR-FIN-007 search | /finance/fiscal-periods | ✓ |
| create fiscal year | API-FIN-023 | SCR-FIN-007 create year | /finance/fiscal-periods/new-year | ✓ |
| open a period | API-FIN-024 | SCR-FIN-007 open | /finance/fiscal-periods/:yearId | ✓ |
| soft-close a period | API-FIN-025 | SCR-FIN-007 soft-close | /finance/fiscal-periods/:yearId | ✓ |
| hard-close a period (approval) | API-FIN-026 | SCR-FIN-007 hard-close | /finance/fiscal-periods/:yearId | ✓ |
| run year-end close | API-FIN-027 | SCR-FIN-007 year-end close | /finance/fiscal-periods/:yearId | ✓ |
| account ledger | API-FIN-028 | SCR-FIN-008 render | /finance/account-ledger | ✓ |
| trial balance | API-FIN-029 | SCR-FIN-009 render | /finance/trial-balance | ✓ |
| balance sheet | API-FIN-030 | SCR-FIN-010 render | /finance/balance-sheet | ✓ |
| income statement | API-FIN-031 | SCR-FIN-011 render | /finance/income-statement | ✓ |
| dimension report | API-FIN-032 | SCR-FIN-012 render | /finance/dimension-reports | ✓ |
| update a recurring template | — none published | SCR-FIN-004 — not drawn | — (ADR-FIN-006) | ✗ |
| update an allocation rule | — none published | SCR-FIN-005 — not drawn | — (ADR-FIN-006) | ✗ |
| search fiscal years | — none published | SCR-FIN-007 — derived from period rows | — (ADR-FIN-006) | ✗ |
| read account / template / rule / year / period by id | — none published | hydrated from the search cache | — (ADR-FIN-006) | ✗ |
| delete a rule line / template line / target | — none published | not drawn on any screen | — (ADR-FIN-006) | ✗ |
| deactivate the parent dimension | — none published | SCR-FIN-002 — not drawn | — (ADR-FIN-006) | ✗ |

Thirty-seven rows carry a published endpoint; thirty-six of those carry a route and a ✓. Six
rows carry a ✗ with the ADR that explains it — one endpoint published for a caller that is not
this frontend (ADR-FIN-007), and five operations with no endpoint at all (ADR-FIN-006). No row
is a ✗ for want of a decision.

<!-- PHASE:ALIGN-FE:END -->

---

## Hand-off

The implementer reads the phases in profile order — F1 models, F2 hooks, F3 forms, F4 screens
and routes, SEC-FE guards — takes design intent from `ui-ux-spec-fin.md`, and takes every
request and response shape from `_inputs/api-docs-fin.md`. No route, component, permission or
field that is not traceable to an F-block above is invented: a gap is an ADR in
`erp/decisions/FIN/`, never an invention. The plan and its registry are split by the toolkit
into `packages/frontend-execution/` and delivered on the frontend delivery branch after the
`gate:pass-2` verdict, then tagged.

══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-srs>>>
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
REQ count: 46 · AC count: 46 · RULE count: 17 · ENT count: 14 · SCR-REQ count: 12
Last sequence per atom: REQ: 046 · AC: 046 · ENT: 014 · RULE: 017 · SCR-REQ: 012

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
RULE-FIN-016, RULE-FIN-017

Decisions
ADR ids: none.

Event
"P1 completed: FIN v1 — 14 entities, 46 requirements, 46 acceptance criteria, 16 rules, 12 screen requirements, 0 ADRs"
(RULE-FIN-017 — fiscal-year/period/docDate coherence — was added later, during SVC-API, and
carried back into srs-fin.md §A5; the counts above are the current 17, while this event line
records what P1 itself emitted.)
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-db>>>
## REGISTRY — P2 — FIN v1
══════════════════════════════════════════════════════════════════

Tables
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| FIN_ACCOUNT | ENT-FIN-001 | master | DBF-FIN-001 … DBF-FIN-013, DBF-FIN-147 |
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
DBF-FIN-144, DBF-FIN-145, DBF-FIN-146, DBF-FIN-147

XM index
| XM id | Type | From | To | Status |
|---|---|---|---|---|
| XM-FIN-001 | SOFT-READ | FIN | MDL | ACTIVE |
| ~~XM-FIN-002~~ | READ | FIN | SEC | RETIRED 2026-09-12 (see db-script-fin.md §2) |

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
Last DBF: DBF-FIN-147 · Last XM: XM-FIN-002 (retired 2026-09-12; the id is burned, not
reused — the live XM set is XM-FIN-001 alone)

Decisions
ADR-FIN-001 (ACCEPTED, non-breaking) — see erp/decisions/FIN/ADR-FIN-001.md

Event
"P2 completed: FIN v1 — 14 tables, 147 DBF, 1 XM"
(XM-FIN-002 was assigned later, at ALIGN-BE, once SEC-BE introduced FIN's read of SEC's user
directory, and RETIRED on 2026-09-12 when the service making that read was deleted. The P2
event line records what P2 itself saw, is left as written, and happens to describe the live
state again.)

Cascade
No registry XM row anywhere in the platform currently targets FIN with status DEFERRED
(FIN is the last module of this batch) — nothing to resolve. XM-FIN-001 resolves
immediately to ACTIVE since MDL v1 is already gated. XM-FIN-002's retirement cascades
nowhere: no other module ever consumed it, and FIN's outbound set is now XM-FIN-001 alone.
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-exec-fe>>>
## REGISTRY — P3.2 — FIN v1
══════════════════════════════════════════════════════════════════

ID RANGES
UXD-FIN-001 .. UXD-FIN-012 · SCR-FIN-001 .. SCR-FIN-012

SCR ids: SCR-FIN-001, SCR-FIN-002, SCR-FIN-003, SCR-FIN-004, SCR-FIN-005, SCR-FIN-006,
SCR-FIN-007, SCR-FIN-008, SCR-FIN-009, SCR-FIN-010, SCR-FIN-011, SCR-FIN-012

UXD ids: UXD-FIN-001, UXD-FIN-002, UXD-FIN-003, UXD-FIN-004, UXD-FIN-005, UXD-FIN-006,
UXD-FIN-007, UXD-FIN-008, UXD-FIN-009, UXD-FIN-010, UXD-FIN-011, UXD-FIN-012

Last sequence per atom: SCR: 012 · UXD: 012

SCREENS
| SCR | Name (ar / en) | Container pattern | Owning ENT | Permissions |
|---|---|---|---|---|
| SCR-FIN-001 | شجرة الحسابات / Chart of accounts | TREE_MASTER_DETAIL | ENT-FIN-001 | PERM_FIN_ACCOUNTS_VIEW, PERM_FIN_ACCOUNTS_CREATE, PERM_FIN_ACCOUNTS_UPDATE |
| SCR-FIN-002 | تعريف الأبعاد وقيمها / Dimension definition & values | TREE_MASTER_DETAIL | ENT-FIN-002 (+ ENT-FIN-003) | PERM_FIN_DIMENSIONS_VIEW, PERM_FIN_DIMENSIONS_CREATE, PERM_FIN_DIMENSIONS_UPDATE |
| SCR-FIN-003 | قواعد المحرك / Engine rules | FULL_PAGE | ENT-FIN-009 (+ ENT-FIN-010) | PERM_FIN_RULES_VIEW, PERM_FIN_RULES_CREATE, PERM_FIN_RULES_UPDATE |
| SCR-FIN-004 | قوالب متكررة/عكسية / Recurring / reversing templates | FULL_PAGE | ENT-FIN-011 (+ ENT-FIN-012) | PERM_FIN_RECURRING_TEMPLATES_VIEW, PERM_FIN_RECURRING_TEMPLATES_CREATE, PERM_FIN_RECURRING_TEMPLATES_UPDATE |
| SCR-FIN-005 | قواعد التوزيع / Allocation rules | FULL_PAGE | ENT-FIN-013 (+ ENT-FIN-014) | PERM_FIN_ALLOCATION_RULES_VIEW, PERM_FIN_ALLOCATION_RULES_CREATE, PERM_FIN_ALLOCATION_RULES_UPDATE |
| SCR-FIN-006 | قيود اليومية / Journal entries | FULL_PAGE | ENT-FIN-004 (+ ENT-FIN-005, ENT-FIN-006) | PERM_FIN_JOURNAL_ENTRIES_VIEW, PERM_FIN_JOURNAL_ENTRIES_CREATE, PERM_FIN_JOURNAL_ENTRIES_REVERSE |
| SCR-FIN-007 | الفترات والسنوات المالية / Fiscal periods & years | TREE_MASTER_DETAIL | ENT-FIN-007 (+ ENT-FIN-008) | PERM_FIN_PERIODS_VIEW, PERM_FIN_PERIODS_CREATE, PERM_FIN_PERIODS_UPDATE, PERM_FIN_PERIODS_CLOSE_APPROVE |
| SCR-FIN-008 | دفتر الحساب / Account ledger | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_ACCOUNT_LEDGER_VIEW |
| SCR-FIN-009 | ميزان المراجعة / Trial balance | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_TRIAL_BALANCE_VIEW |
| SCR-FIN-010 | الميزانية العمومية / Balance sheet | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_BALANCE_SHEET_VIEW |
| SCR-FIN-011 | قائمة الدخل / Income statement | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_INCOME_STATEMENT_VIEW |
| SCR-FIN-012 | تقارير الأبعاد / Dimension reports | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005, ENT-FIN-006 (live-derived) | PERM_FIN_DIMENSION_REPORTS_VIEW |

UXD INDEX
| UXD | Screen(s) | Field | Owner module · API used |
|---|---|---|---|
| UXD-FIN-001 | SCR-FIN-001, SCR-FIN-009, SCR-FIN-010, SCR-FIN-011 | accountTypeCode (`ACCOUNT_TYPE`) | MDL · the lookup module's consumer read (named in ui-ux-spec-fin.md) |
| UXD-FIN-002 | SCR-FIN-001, SCR-FIN-003, SCR-FIN-004, SCR-FIN-006, SCR-FIN-008, SCR-FIN-009, SCR-FIN-010, SCR-FIN-011, SCR-FIN-012 | natureCode / directionCode (`DEBIT_CREDIT`) | MDL · same |
| UXD-FIN-003 | SCR-FIN-007 | period statusCode (`PERIOD_STATE`) | MDL · same |
| UXD-FIN-004 | SCR-FIN-007 | year statusCode (`FISCAL_YEAR_STATUS`) | MDL · same |
| UXD-FIN-005 | SCR-FIN-006, SCR-FIN-008 | journalTypeCode (`JOURNAL_TYPE`) | MDL · same |
| UXD-FIN-006 | SCR-FIN-006 | entry statusCode (`JOURNAL_STATUS`) | MDL · same |
| UXD-FIN-007 | SCR-FIN-003 | eventTypeCode (`ACCOUNTING_EVENT_TYPE`) | MDL · same |
| UXD-FIN-008 | SCR-FIN-003 | accountDerivationTypeCode (`ACCOUNT_DERIVATION_TYPE`) | MDL · same |
| UXD-FIN-009 | SCR-FIN-003 | amountSourceTypeCode (`AMOUNT_SOURCE_TYPE`) | MDL · same |
| UXD-FIN-010 | SCR-FIN-003, SCR-FIN-005 | distributionTypeCode (`DISTRIBUTION_TYPE`) | MDL · same |
| UXD-FIN-011 | SCR-FIN-004 | scheduleTypeCode (`RECURRING_SCHEDULE_TYPE`) | MDL · same |
| UXD-FIN-012 | SCR-FIN-004 | frequencyCode (`RECURRING_FREQUENCY`) | MDL · same |

One `UXD-*` per displayed lookup key, not per screen occurrence — the key is the unit the one
shared hook is built on (ADR-FIN-004). `PAYMENT_METHOD` is FIN-owned and registered by
REQ-FIN-045 but displayed by no FIN field in this version, so it mints none. The screen gate
(the security module's effective menu) is an authorization dependency, not a displayed field,
and is recorded in ADR-FIN-005 rather than minted as a `UXD-*`.

API COVERAGE
| Status | Count | API ids |
|---|---|---|
| used by this frontend | 36 | API-FIN-001..019, API-FIN-021..037 |
| documented, deliberately uncalled | 1 | API-FIN-020 — the event-sourced build a host system calls over the platform's in-process module interface; bound and blocked out in F2 — ADR-FIN-007 |
| used but undocumented | 0 | — no endpoint is called that the api-docs lack |
| documented but unbound | 0 | all 37 published endpoints are bound by the API ID BINDING annex — ADR-FIN-002 |

No verb or path differs between the plan, the SRS Part B tables and the published surface: the
annex matched all 37 on verb + path with no shape diff.

**Backend registry gap, carried forward.** `registry-exec-be-fin.md` lists
`API-FIN-001 .. API-FIN-032`. API-FIN-033 (fiscal-period search), API-FIN-034, API-FIN-035,
API-FIN-036 and API-FIN-037 (the four deactivates) are defined in
`backend-execution-plan-fin.md`, published in the api-docs and used by this frontend, but were
never carried into that registry's ID RANGES line — `gov.py analyze` already reports it against
P3.1. Closing it is one line in a backend artifact, which §8 puts outside this stage's
boundary. Recorded here and in ADR-FIN-002.

OPERATIONS WITHOUT AN ENDPOINT
template update · allocation-rule update · fiscal-year search · by-id read of an account, a
template, an allocation rule, a fiscal year or a fiscal period · rule-line, template-line and
allocation-target delete · parent-dimension deactivate — named by SRS Part B, required by no
`REQ-*`, and omitted from the frontend rather than faked (ADR-FIN-006).

LOOKUPS
| Key | Owner | Hook | Endpoint |
|---|---|---|---|
| ACCOUNT_TYPE | FIN (registered into MDL, REQ-FIN-045) | one shared hook | the lookup module's consumer read — UXD-FIN-001 |
| DEBIT_CREDIT | FIN → MDL | one shared hook | UXD-FIN-002 |
| PERIOD_STATE | FIN → MDL | one shared hook | UXD-FIN-003 |
| FISCAL_YEAR_STATUS | FIN → MDL | one shared hook | UXD-FIN-004 |
| JOURNAL_TYPE | FIN → MDL | one shared hook | UXD-FIN-005 |
| JOURNAL_STATUS | FIN → MDL | one shared hook | UXD-FIN-006 |
| ACCOUNTING_EVENT_TYPE | FIN → MDL | one shared hook | UXD-FIN-007 |
| ACCOUNT_DERIVATION_TYPE | FIN → MDL | one shared hook | UXD-FIN-008 |
| AMOUNT_SOURCE_TYPE | FIN → MDL | one shared hook | UXD-FIN-009 |
| DISTRIBUTION_TYPE | FIN → MDL | one shared hook | UXD-FIN-010 |
| RECURRING_SCHEDULE_TYPE | FIN → MDL | one shared hook | UXD-FIN-011 |
| RECURRING_FREQUENCY | FIN → MDL | one shared hook | UXD-FIN-012 |
| PAYMENT_METHOD | FIN → MDL | none | displayed by no FIN field this version |
Every lookup field stays a string holding the code and no enum is modelled anywhere in the
plan; no lookup validator binds a static list.

ALIGN-FE
The verdict row inside the plan's ALIGN-FE block is written by the orchestrator from the
analyze report; findings fixed by this stage: 0.

ADRs
erp/decisions/FIN/ADR-FIN-002.md (ACCEPTED, non-breaking — API id binding annex, and the stale backend API range) ·
erp/decisions/FIN/ADR-FIN-003.md (ACCEPTED, non-breaking — container pattern for screens with no entry sub-view) ·
erp/decisions/FIN/ADR-FIN-004.md (ACCEPTED, non-breaking — lookup values through the lookup module's consumer API, one UXD per key) ·
erp/decisions/FIN/ADR-FIN-005.md (ACCEPTED, non-breaking — screen gating reads the security module's effective menu) ·
erp/decisions/FIN/ADR-FIN-006.md (ACCEPTED, non-breaking — operations with no published endpoint) ·
erp/decisions/FIN/ADR-FIN-007.md (ACCEPTED, non-breaking — API-FIN-020 bound but drawn on no screen) ·
erp/decisions/FIN/ADR-FIN-008.md (ACCEPTED, non-breaking — the manual entry's journalTypeCode and fiscalYearId vs SRS B3)
Carried from earlier stages: ADR-FIN-001 (P2). No BLOCKED ADR.

TRACEABILITY
REQ covered by ≥1 SCR/F-block: 46/46 — REQ-FIN-001..043 each appear in the `traces=` of at
least one SUB block of every sub-bearing phase that owns their screen; REQ-FIN-044 is cited by
the SEC-FE phase (it is what registers FIN's screens in the security module, which is what the
menu gate reads) and REQ-FIN-045 by the F2 phase and by every lookup-bearing F2 SUB (it is what
registers the twelve lookup keys the hooks read); REQ-FIN-046 is cited by the four report
screens whose links form its drill-down chain.
Orphan REQ: none.
AC covered: 46/46 (each AC accompanies its REQ in the same traces).
SCR covered: 12/12 — every `SCR-*` carries a block in F1, F2, F3 and F4 (48 SUB blocks) and an
RF5 block in SEC-FE.
UXD cited by an F-block: 12 of 12 — none unreferenced, none dangling.

Event
"P3.2 completed: FIN v1 — 12 screens, 12 UXD, 37/37 API bound (36 called), 4 sub-bearing phases
× 12 SUB blocks, ALIGN-FE stamped by the orchestrator, 7 ADRs"
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
