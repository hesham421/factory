# BRIEF — stage `test-gen` (Test Generation) · module MDL · v1 · profile `erp`

Lane `test-gen` · implementer claude:opus · effort high · round 1

## Rules that bind this run
- Questions: **forbidden**. A `[QUESTION]` block is refused. Ambiguity → ADR in `erp/decisions/MDL/` (`ADR-{MOD}-{seq:03d}.md`): non-breaking → continue; breaking → status BLOCKED and stop.
- Owns IDs: TC — ID grammar `{prefix}-{MOD}-{seq}` (seq width 3); never re-number, never restart a sequence.
- Read only what this brief contains (generated current state); never open version folders yourself.
- Write exactly these files (complete files; in a delta version only what changed, plus `change-manifest.md`):
- `erp/modules/MDL/test_gen/backend-test-plan-mdl.md`
- `erp/modules/MDL/test_gen/frontend-test-plan-mdl.md`
- `erp/modules/MDL/test_gen/test-execution-manifest-mdl.md` (optional)
- `erp/system-test-index-erp.md` (optional)
- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; when running as the operator, write the files directly.

## Contracts checked by `gov.py analyze` after this stage
- **C10** acceptance criteria → test generation (standalone): C10.1 traces {'from': 'TC', 'to': ['AC', 'XM', 'UXD'], 'min': 1, 'mode': 'any'} [CRITICAL]; C10.2 orphans {'kind': 'AC', 'referenced_by': ['TC'], 'min': 1} [MAJOR]; C10.3 markers {'artifact': 'backend-test-plan', 'track': 'backend', 'plan': 'test'} [CRITICAL]; C10.4 markers {'artifact': 'frontend-test-plan', 'track': 'frontend', 'plan': 'test'} [CRITICAL]; C10.5 ids-owned {'stage': 'test-gen'} [CRITICAL]; C10.6 exists {'artifact': 'test-execution-manifest', 'when': 'profile.stack.testing.manifest'} [MINOR]

---
# ENGINE
```
ENGINE        : test-gen — Test Generation   (STANDALONE — outside the line, on demand)
LANE          : test-gen · questions forbidden · derives from `AC-*` (module) + `XM-*`/`UXD-*` (integration)
SCOPE         : module · modules MDL
MODULE        : MDL · v1 · profile erp (ERP Platform)
READS         : srs · backend-execution-plan? · frontend-execution-plan? · registry-srs · registry-db? · registry-exec-fe?   (from _state/ — "?" = optional — read for EACH module in scope)
PRODUCES      : backend-test-plan-mdl.md · frontend-test-plan-mdl.md · test-execution-manifest-mdl.md (optional)
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

This run: **scope = `module`**, modules = `MDL`.

| Scope | TC sources | Phases populated |
|---|---|---|
| `module` | `AC-*` of the one module (§3) | the module-scope phases only (`TEST-PLAN-BE` on backend; the equivalent on frontend) — **identical in shape to a single-module run today** |
| `modules` | `AC-*` per module (§3) **+** `XM-*` (§4) and `UXD-*` (§5) between the *selected* modules only | module-scope phases for every selected module, plus the integration phase(s) (`profile…phases[*].integration: true`) wherever a real linking atom pairs two selected modules |
| `project` | everything `modules` does, across **every** module the factory has ever produced a version for, **plus** a derived coverage rollup | the same as `modules`, plus `system-test-index-{profile}.md` (§9) — no new atom, no new gate |

Rules that hold at every scope:
1. a module never gets an integration TC for a module that is **not** in the current
   selection — running `--module MDL` alone never touches another module's `XM`/`UXD`;
2. an integration phase with no real linking atom among the selected modules stays **absent**
   from the output — never an empty `PHASE` block, never a guessed pairing;
3. `--module` output is produced exactly as it always was — no integration phase key, no
   `system-test-index`, no extra section — so a single-module run stays byte-identical in
   shape to before this scope model existed.

## 3. Derivation (module scope) — every `TC-*` comes from an `AC-*`

`TC-*` (`TC-MDL-{seq}`, 3-digit seq,
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
also in `MDL` — an `XM-*` targeting a module outside the selection is
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
module that owns the displayed data) is also in `MDL`.

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
<!-- TC:TC-MDL-<seq>:START traces=AC-MDL-<seq>,REQ-MDL-<seq>[,API-MDL-<seq>|SCR-MDL-<seq>|XM-MDL-<seq>|UXD-MDL-<seq>] -->
### TC-MDL-<seq> — <title>
Derived from : AC-MDL-<seq>  (REQ-MDL-<seq>)   |   XM-MDL-<seq> (REQ-MDL-<seq>)   |   UXD-MDL-<seq> (REQ-MDL-<seq>, AC-MDL-<seq>)
Exercises    : API-MDL-<seq> <verb path>   |   SCR-MDL-<seq> <route>
Rule / code  : RULE-MDL-<seq> → <catalog code> | —
Scenario     : <tag> · data class <class> · language <ar|en|ALL>
Preconditions: <from Given — concrete entities, role, state | for XM/UXD: the target/owner entity present or absent>
Steps        : 1. … 2. … (from When — one observable action per step)
Expected     : <from Then — status / body shape / message per language / UI state>
Test data    : <values named in the AC; placeholders marked, never invented business data>
<!-- TC:TC-MDL-<seq>:END -->
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

### Track `backend` — one file per selected module: `backend-test-plan-mdl.md`

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

### Track `frontend` — one file per selected module: `frontend-test-plan-mdl.md`

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
`test-execution-manifest-mdl.md` —
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
Data source: ENT-MDL-001.ownerModuleCode — validated against SEC's module registry through XM-MDL-001 (SOFT-READ, application layer)
Message    : ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" · en: "The owning module is not registered in the Security module"
Traces     : REQ-MDL-002
Source     : lookup-module-plan-en.md §3

### RULE-MDL-002 — رفض رمز مكرر ضمن النوع / Reject a duplicate code within a type
Scope      : ENT-MDL-002
Trigger    : on create (lookup value)
Statement  : The system shall reject a lookup value whose code already exists under the same lookup type.
Data source: ENT-MDL-002.code, ENT-MDL-002.lookupTypeId
Message    : ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" · en: "This code is already used within this type"
Traces     : REQ-MDL-007
Source     : lookup-module-plan-en.md §6

### RULE-MDL-003 — عدم تغيير مفتاح النوع بعد إنشائه / Key immutability after creation
Scope      : ENT-MDL-001
Trigger    : on update (lookup type)
Statement  : The system shall prevent editing a lookup type's key after creation.
Data source: ENT-MDL-001.key
Message    : ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" · en: "A lookup type's key cannot be changed after creation"
Traces     : REQ-MDL-003
Source     : lookup-module-plan-en.md §3 (the key is what every consumer already cites)

### RULE-MDL-004 — استبعاد قيم النوع المعطّل / Exclude an inactive type's values from reads
Scope      : ENT-MDL-001
Trigger    : on evaluate (consumer read, REQ-MDL-011)
Statement  : While a lookup type is inactive, the system shall exclude its values from consumer reads.
Data source: ENT-MDL-001.isActiveFl
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
| search types | POST | /api/v1/mdl/lookup-types/search | filters, paging | Page\<LookupType\> | — | REQ-MDL-001 |
| create type | POST | /api/v1/mdl/lookup-types | key, ownerModuleCode, nameAr, nameEn | LookupType | RULE-MDL-001 | REQ-MDL-001, REQ-MDL-002 |
| update type | PUT | /api/v1/mdl/lookup-types/{id} | nameAr, nameEn | LookupType | RULE-MDL-003 | REQ-MDL-003 |
| deactivate type | DELETE | /api/v1/mdl/lookup-types/{id} | id | confirmation | — | REQ-MDL-004 |
| search values | POST | /api/v1/mdl/lookup-types/values/search | filters, paging (parent lookupTypeId in filters) | Page\<LookupValue\> | — | REQ-MDL-005 |
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
| browse registry | POST | /api/v1/mdl/lookup-types/by-owner/search | filters | grouped List\<OwnerGroupResponse\> | — | REQ-MDL-013 |
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

<<<INPUT: backend-execution-plan>>>
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
| API-MDL-001 | search types | POST | /api/v1/mdl/lookup-types/search | REQ-MDL-001 · DBF-MDL-002,003,004,005,006 |
| API-MDL-002 | create type | POST | /api/v1/mdl/lookup-types | REQ-MDL-001,REQ-MDL-002 · DBF-MDL-002,003,004,005 |
| API-MDL-003 | update type | PUT | /api/v1/mdl/lookup-types/{id} | REQ-MDL-003 · DBF-MDL-004,005 |
| API-MDL-004 | deactivate type | DELETE | /api/v1/mdl/lookup-types/{id} | REQ-MDL-004 · DBF-MDL-006 |
| API-MDL-005 | search values | POST | /api/v1/mdl/lookup-types/values/search | REQ-MDL-005 · DBF-MDL-012,013,014,015,016,017 |
| API-MDL-006 | create value | POST | /api/v1/mdl/lookup-types/{id}/values | REQ-MDL-006,REQ-MDL-007 · DBF-MDL-012,013,014,015,016 |
| API-MDL-007 | update value | PUT | /api/v1/mdl/lookup-values/{id} | REQ-MDL-008 · DBF-MDL-014,015,016 |
| API-MDL-008 | deactivate value | DELETE | /api/v1/mdl/lookup-values/{id} | REQ-MDL-009 · DBF-MDL-017 |
| API-MDL-009 | reorder values | PATCH | /api/v1/mdl/lookup-types/{id}/values/reorder | REQ-MDL-010 · DBF-MDL-016 |
| API-MDL-010 | browse registry by owner | POST | /api/v1/mdl/lookup-types/by-owner/search | REQ-MDL-013 · DBF-MDL-003,002,004,005 |
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
format `MDL-{http}[-{SLUG}]` (`profile.stack.backend.api.error_code_format`; {http} = the row's HTTP status, {SLUG} = SCREAMING-KEBAB, the [ ] half optional).

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
search endpoint (API-SEC-021), filtered by `code`) — not a physical join, not a shared transaction.

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
Endpoint     : POST /api/v1/mdl/lookup-types/search
Layers       : controller → `LookupTypeController.search` ; service → `LookupTypeService.search`
Request      : body `LookupTypeSearchRequest` (BaseSearchContractRequest) — `filters[]` of (field, operator, value) over `key`, `ownerModuleCode`, `isActiveFl`, and `page`, `size`, `sortField`, `sortDirection`
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
Endpoint     : POST /api/v1/mdl/lookup-types/values/search
Layers       : controller → `LookupValueController.search` ; service → `LookupValueService.search`
Request      : body `LookupValueSearchRequest` (BaseSearchContractRequest) — the CHILD variant: the parent `lookupTypeId` travels inside `filters[]` (never a path variable), plus `filters[]` of (field, operator, value) over `code`, and `page`, `size`, `sortField`, `sortDirection` (default sort = sortOrder)
Response     : 200 · `Page<LookupValueResponse>` · `ApiResponse<Page<LookupValueResponse>>`
Validations  : none
Errors       : `MDL-404-TYPE` (404, unknown or missing lookupTypeId)
Orchestration: load (QR-MDL-005) → map → return
Repository   : QR-MDL-005 · join NONE · transaction READ_ONLY
Security     : screen MDL_LOOKUPS · permission `PERM_MDL_LOOKUPS_VIEW`
Localization : nameAr/nameEn returned
<!-- API:API-MDL-005:END -->

<!-- API:API-MDL-010:START traces=REQ-MDL-013,DBF-MDL-003,DBF-MDL-002,DBF-MDL-004,DBF-MDL-005 -->
### API-MDL-010 — browse registry by owner
Endpoint     : POST /api/v1/mdl/lookup-types/by-owner/search
Layers       : controller → `LookupTypeController.browseByOwner` ; service → `LookupTypeService.browseByOwner`
Request      : body `LookupTypeByOwnerSearchRequest` (BaseSearchContractRequest) — `filters[]` of (field, operator, value) over `ownerModuleCode`, `key`; `isActiveFl` is NOT a client-supplied filter — the service applies "active types only" unconditionally; `page`/`size`/`sortField` are inherited but unused (response is not paginated)
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
| API-MDL-001 | /lookup-types/search | POST | LookupTypeSearchRequest | paginated list of LookupTypeResponse | v1 |
| API-MDL-002 | /lookup-types | POST | LookupTypeCreateRequest | LookupTypeResponse | v1 |
| API-MDL-003 | /lookup-types/{id} | PUT | LookupTypeUpdateRequest | LookupTypeResponse | v1 |
| API-MDL-004 | /lookup-types/{id} | DELETE | — | LookupTypeResponse | v1 |
| API-MDL-005 | /lookup-types/values/search | POST | LookupValueSearchRequest | paginated list of LookupValueResponse | v1 |
| API-MDL-006 | /lookup-types/{id}/values | POST | LookupValueCreateRequest | LookupValueResponse | v1 |
| API-MDL-007 | /lookup-values/{id} | PUT | LookupValueUpdateRequest | LookupValueResponse | v1 |
| API-MDL-008 | /lookup-values/{id} | DELETE | — | LookupValueResponse | v1 |
| API-MDL-009 | /lookup-types/{id}/values/reorder | PATCH | LookupValueReorderRequest | array of LookupValueResponse | v1 |
| API-MDL-010 | /lookup-types/by-owner/search | POST | LookupTypeByOwnerSearchRequest | array of OwnerGroupResponse | v1 |
| API-MDL-011 | /lookups | GET | — | array of LookupValueResponse | v1 |
(paths relative to `/api/v1/mdl`. A `—` request means the endpoint takes no body: API-MDL-004
and API-MDL-008 carry their id in the path, and API-MDL-011 reads its `type` key from a query
parameter. RESOLVED 2026-09-12 against the published `_inputs/api-docs-mdl.md`: every type name
above was previously marked `(proposed)` — derived before any implementation existed — and each
is now the name the surface really publishes, so the `(proposed)` marks are gone rather than
carried beside real names. THREE ROWS ALSO CHANGED VERB AND PATH, and that is the substantive
correction: API-MDL-001, API-MDL-005 and API-MDL-010 were written here as `GET` with query
parameters and are published as `POST …/search` taking a `filters[]` envelope. The `Endpoint :`
lines of their own API blocks above already said `POST …/search`, and so did `srs-mdl.md`
§B5 — this table was the only artifact in the module still predicting the GET form, which is
why `gov.py analyze` raised it here as three C8.4 `endpoint-agrees` findings and nowhere else.
The Response DTO cells are written in the api-docs' own words — `paginated list of X` where the
response carries a `Page<T>` envelope and `array of X` where it does not — rather than in a
`Page<X>` / `List<X>` notation the published document never uses; only two of the eleven are
paged, and the notation now shows which. Two response types also moved: API-MDL-004 and
API-MDL-008 were predicted to return a
`DeactivateConfirmation`, and each really returns its own entity response with
`isActiveFl=false`. The frontend was bound to the published shape throughout —
`erp/decisions/MDL/ADR-MDL-002.md` records the divergence and names this table as where the fix
belonged.)

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

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `MDL-{http}[-{SLUG}]`.

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
CORE (R1)         ✓ layers, domain placement, error signalling (`MDL-{http}[-{SLUG}]`), type mapping (incl. the stated sort_order→Integer deviation) all declared
DECISIONS         ✓ 0 new ADR this stage; SEC's ADR-SEC-002 convention correctly cited, not re-derived
RESULT            BLOCKED ✗ — 3 findings
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

<<<INPUT: frontend-execution-plan>>>
# FRONTEND EXECUTION PLAN — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Track : frontend
Framework : react-ts-vite (profile.stack.frontend.framework) · routing react-router ·
            server-state tanstack-query · forms react-hook-form · validation zod ·
            state useState/useReducer + Context (no global store by default)
Inputs : srs (v1, PRD-approved), prd (v1), api-docs (v1, published by the backend repo),
         registry-srs (v1), registry-exec-be (v1)
Screens : 2 — SCR-MDL-001..002 · UXD : 1 — UXD-MDL-001 · API bound : 11 / 11
Open ADRs : 7 — erp/decisions/MDL/ (ADR-MDL-001..007, all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

## API SURFACE — MDL v1   (source: `_inputs/api-docs-mdl.md` — the ONLY endpoint source)

```
ENDPOINTS   11 — API-MDL-001..011, bound to the published surface by the API ID BINDING annex
            of the api-docs (ADR-MDL-001). Envelope: every response is wrapped in
            ApiResponse<T> { success, data, error { code, message, fieldErrors[] }, timestamp }.
            Paging constraints (PageableBuilder): default page 0 · default size 20 · maximum
            size 200. THREE response shapes, and the difference matters to every F2 block:
              · Page<T> — API-MDL-001 and API-MDL-005 alone
              · a bare array — API-MDL-009 (the reordered values), API-MDL-010
                (OwnerGroupResponse[]) and API-MDL-011 (LookupValueResponse[]); none of these
                carries a paging envelope and none may be read as one
              · a single object — API-MDL-002, 003, 004, 006, 007, 008
            Two reads and one browse are POST `…/search` with a `filters[] {field, operator,
            value}` envelope rather than GET with query params (operators EQUALS, NOT_EQUALS,
            LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN) —
            which is what the SRS B5 tables state too; only the backend plan's contract table
            still predicts GET (ADR-MDL-002). API-MDL-010's request carries `filters` alone,
            with no sort and no paging.
ERRORS      business codes, each already carrying its ar/en text in the module's catalog:
            MDL-400-REORDER-MISMATCH (400) · MDL-404-TYPE · MDL-404-VALUE · MDL-404-TYPE-KEY
            (404) · MDL-409-MODULE-NOT-REGISTERED [RULE-MDL-001] · MDL-409-TYPE-DUP ·
            MDL-409-VALUE-DUP [RULE-MDL-002] (409) · framework codes VALIDATION_ERROR (400) ·
            DATA_INTEGRITY_VIOLATION (409) · ACCESS_DENIED (403) · INTERNAL_ERROR (500).
            Routing is uniform across every F2 block: field validation → inline · business
            rule → user message · unauthenticated → login · forbidden → the localized
            forbidden message · server → generic.
LOOKUPS     **none.** SRS §A6 records that MDL introduces no coded list of its own — it is the
            mechanism every other module's lists run on. No field on either screen is a
            lookup-backed code, no lookup hook exists anywhere in this plan, and no enum is
            modelled. The one cross-module dependency, UXD-MDL-001, is the owner-module field,
            whose valid set the security module owns (ADR-MDL-004) — not lookup data, and not
            read through API-MDL-011.
PERMISSIONS declared by the backend and read from the SRS Access summary and the backend
            registry, never redeclared here: PERM_MDL_LOOKUPS_VIEW / _CREATE / _UPDATE /
            _DELETE · PERM_MDL_TYPE_REGISTRY_VIEW.
            No MDL endpoint publishes the caller's own permission set: the screen gate is the
            security module's effective menu (SEC-FE below), and no `PERM_*` name is composed
            at runtime.
```

### Reconciliation against the SRS — run once, before any F-content

- **Every REQ that needs an endpoint has one.** REQ-MDL-001..013 map onto API-MDL-001..011
  with no gap; the mapping is the traces of the F2 blocks below.
- **Every documented endpoint maps to a REQ.** All 11 are bound; none is unknown and none is
  used without a REQ behind it.
- **Naming and shape differences** — three reads are POST `…/search` where the backend plan's
  contract table predicted GET. The api-docs and the SRS B5 tables agree with each other; the
  backend plan is the one artifact that lags, and `gov.py analyze` reports it there as C8.4.
  The frontend binds to the published shape (ADR-MDL-002).
- **Operations the SRS names with no published endpoint** — `activate` at either level, and
  the by-id reads of a type and of a value. None is required by a `REQ-*`, so none is
  breaking; each is omitted rather than faked (ADR-MDL-005).
- **Endpoints published but not called by this frontend** — API-MDL-011 alone, the consumer
  read another module's backend performs over the platform's in-process module interface
  (ADR-MDL-007). It is bound and blocked out in F2 below.
- **One screen's form differs from its SRS Part B input list** — SCR-MDL-001 renders
  `isActiveFl` read-only at both levels although B3 lists it among the detail inputs; no
  published write DTO accepts it and the deactivate endpoints are what change it
  (ADR-MDL-006).
- **Nothing is invented.** No value absent from the api-docs appears in this plan, and no
  permission name, route or component is derived from anything but the SRS, the api-docs and
  the profile's own stack.

## EXECUTION PLAN INDEX — MDL v1 — frontend-execution-plan-mdl.md

| # | Phase | Split | Blocks |
|---|---|---|---|
| 1 | F1 — Models & Types | not split — 2 SCR < 5 | level-1, one block per screen |
| 2 | F2 — Data Hooks | not split — 2 SCR < 5 | level-1, one block per screen |
| 3 | F3 — Forms & Validators | not split — 2 SCR < 5 | level-1, one block per screen |
| 4 | F4 — Screens & Routes | not split — 2 SCR < 5 | level-1, one block per screen |
| 5 | SEC-FE | never split | level-1 only |
| 6 | ALIGN-FE | never split | level-1 only |

**SCREEN REGISTRY**

| SCR | Name (ar / en) | Page code | Container pattern | Owning ENT |
|---|---|---|---|---|
| SCR-MDL-001 | اللوكبات العامة / Generic Lookups | MDL_LOOKUPS | TREE_MASTER_DETAIL | ENT-MDL-001 نوع اللوكب / LookupType (+ ENT-MDL-002 قيمة اللوكب / LookupValue) |
| SCR-MDL-002 | سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner | MDL_TYPE_REGISTRY | FULL_PAGE (no entry sub-view — ADR-MDL-003) | ENT-MDL-001 نوع اللوكب / LookupType |

Two screens, so the `sub_bearing` phases do **not** split per screen: the threshold is an SCR
count of 5 or more. Each phase below carries its screens' blocks at level 1, and every block
heading still names the `SCR-*` it belongs to, exactly as §3.3 requires below the threshold.

<!-- PHASE:F1:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 1 — F1 — Models & Types

Per `ENT-*` (from the response DTOs of the api-docs) and per `SCR-*`: the source DTO with each
property's type and read-only / system-only status, then the screen's search model, form model
and container. Both names are carried per language (ar, en). No internal or tenant identifier
is modelled, and nothing is modelled that the api-docs do not return. **No lookup field and no
enum appears anywhere in this phase** — MDL owns no coded list of its own (SRS §A6).

### F1 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F1-MODEL — ENT-MDL-001 — نوع اللوكب / LookupType
Source DTO   : `LookupTypeResponse` (read) · `LookupTypeCreateRequest` · `LookupTypeUpdateRequest`
  lookupTypePk    : number · read-only (PK) · system-only
  key             : string · maxLength 80 · required on create, **read-only on edit** —
                    RULE-MDL-003, and `LookupTypeUpdateRequest` does not carry it
  ownerModuleCode : string · maxLength 10 · required on create, **read-only on edit** — not in
                    the update request; its valid set is the security module's registry
                    (UXD-MDL-001), and it is held as a plain string, never an enum
  nameAr          : string · required · maxLength 150
  nameEn          : string · required · maxLength 150
  isActiveFl      : boolean · read-only — flipped only by API-MDL-004 (ADR-MDL-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — ENT-MDL-002 — قيمة اللوكب / LookupValue
Source DTO   : `LookupValueResponse` (read) · `LookupValueCreateRequest` ·
               `LookupValueUpdateRequest` · `LookupValueReorderRequest`
  lookupValuePk : number · read-only (PK) · system-only
  lookupTypeId  : number · read-only — the path id of API-MDL-006, taken from the selected
                  parent, never typed
  code          : string · maxLength 50 · required on create, **read-only on edit** — the
                  update request does not carry it; unique within its type (RULE-MDL-002)
  nameAr        : string · required · maxLength 150
  nameEn        : string · required · maxLength 150
  sortOrder     : number · required on create **and** on update — and the same field the
                  reorder writes, through `LookupValueReorderRequest { orderedValueIds[] }`
  isActiveFl    : boolean · read-only — flipped only by API-MDL-008 (ADR-MDL-006)
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only
### F1-SCREEN — SCR-MDL-001
Search model : master filters — key : string · LIKE · ownerModuleCode : string · EXACT (from
               the UXD-MDL-001 hook) · isActiveFl : boolean · EXACT
               detail filters — code : string · LIKE · lookupTypeId : number · EXACT (set from
               the selected parent, not typed)
               paging + sort — page, size, sortField, sortDirection, inside each of
               `LookupTypeSearchRequest` and `LookupValueSearchRequest` per `Page<T>`
Form model   : type, create — key, ownerModuleCode, nameAr, nameEn (all required)
               type, edit   — nameAr, nameEn (required); key and ownerModuleCode read-only
               value, create — code, nameAr, nameEn, sortOrder (all required)
               value, edit   — nameAr, nameEn, sortOrder (required); code read-only
               reorder       — the ordered list of value ids, not a per-row edit
               excluded system fields: both PKs, lookupTypeId, both isActiveFl, the audit fields
Container    : TREE_MASTER_DETAIL
`isActiveFl` is modelled read-only at both levels: it is in the response and in no write
request, so a form that offered it would be offering a field the server ignores (ADR-MDL-006).

### F1 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F1-MODEL — OwnerGroupResponse — المجموعة حسب المالك / Owner group
Source DTO   : `OwnerGroupResponse[]` (read only — this screen writes nothing)
  ownerModuleCode : string · read-only — the group key (UXD-MDL-001)
  types[]         : LookupTypeResponse — the same type model as SCR-MDL-001 above, every
                    property read-only here: lookupTypePk, key, ownerModuleCode, nameAr,
                    nameEn, isActiveFl, and the four audit fields
### F1-SCREEN — SCR-MDL-002
Search model : filters — ownerModuleCode : string · EXACT · key : string · LIKE.
               **No paging and no sort**: `LookupTypeByOwnerSearchRequest` carries `filters`
               alone, so no page or size is modelled and none belongs in this screen's cache key
Form model   : none — a read-only browse (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-MDL-003)
The response is a bare array of groups, not a `Page<T>`, and is modelled as one: reading it
through a paging envelope would invent fields the endpoint does not send.

<!-- PHASE:F1:END -->

<!-- PHASE:F2:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 2 — F2 — Data Hooks

What each screen needs from the API — not hook code. Every read query's cache key carries
**every** filter that changes the response, page and size included **where the endpoint is
paged**; page and page size live inside the filter object and are never independent state.
Every mutation declares its invalidation. Components use the facade only; the facade uses the
declared queries only (server-state library: `tanstack-query`).

Only two of the eleven endpoints return `Page<T>` — API-MDL-001 and API-MDL-005. API-MDL-009,
API-MDL-010 and API-MDL-011 return bare arrays, so their keys carry no page or size and their
blocks say so rather than leaving a reader to assume the usual envelope.

### F2 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F2-QUERY — API-MDL-001            traces=API-MDL-001,REQ-MDL-001
POST `/api/v1/mdl/lookup-types/search` · request `LookupTypeSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<LookupTypeResponse>` ·
kind **read query** (a POST that mutates nothing — ADR-MDL-002)
Cache key    : `[lookup-types, filters]` where `filters` is the whole request object — key,
               ownerModuleCode, isActiveFl, sortField, sortDirection **and page, size**
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `VALIDATION_ERROR` (400) → inline on the offending filter ·
               `INTERNAL_ERROR` (500) → generic message
Loading      : LOCAL — the SRS states nothing about this call being slow, so no GLOBAL indicator
Cache policy : defaults
Invalidation : refreshed by API-MDL-002, API-MDL-003 and API-MDL-004
### F2-QUERY — API-MDL-002            traces=API-MDL-002,REQ-MDL-001,REQ-MDL-002
POST `/api/v1/mdl/lookup-types` · request `LookupTypeCreateRequest` { key, ownerModuleCode,
nameAr, nameEn } · response `LookupTypeResponse` · kind **mutation**
Errors       : `MDL-409-MODULE-NOT-REGISTERED` (409) → user message for RULE-MDL-001, routed to
               the owner-module field, ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" ·
               en: "The owning module is not registered in the Security module" ·
               `MDL-409-TYPE-DUP` (409) → inline on `key` ·
               `VALIDATION_ERROR` (400) → inline per `error.fieldErrors[].field` ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-types, *]`
### F2-QUERY — API-MDL-003            traces=API-MDL-003,REQ-MDL-003
PUT `/api/v1/mdl/lookup-types/{id}` · request `LookupTypeUpdateRequest` { nameAr, nameEn } ·
response `LookupTypeResponse` · kind **mutation**
Errors       : `MDL-404-TYPE` (404) → user message · `VALIDATION_ERROR` (400) → inline ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-types, *]`
The request carries the two names and nothing else, which is RULE-MDL-003 expressed in the
surface: there is no key field to send and none is sent.
### F2-QUERY — API-MDL-004            traces=API-MDL-004,REQ-MDL-004
DELETE `/api/v1/mdl/lookup-types/{id}` · no request body · response `LookupTypeResponse`
(isActiveFl=false) · kind **mutation**
Errors       : `MDL-404-TYPE` (404) → user message · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-types, *]` and `[lookup-values, *]` — RULE-MDL-004 makes an inactive
               type's values invisible to consumers, so any cached value list of that type is
               stale in meaning even though its rows have not changed
### F2-QUERY — API-MDL-005            traces=API-MDL-005,REQ-MDL-005
POST `/api/v1/mdl/lookup-types/values/search` · request `LookupValueSearchRequest`
{ filters[] including `lookupTypeId`, sortField, sortDirection, page, size } ·
response `Page<LookupValueResponse>` · kind **read query** (ADR-MDL-002)
Cache key    : `[lookup-values, filters]` — lookupTypeId, code, sort **and page, size**. The
               parent id is part of the key, so selecting another type is a different cache
               entry rather than a refetch of the same one.
Errors       : `ACCESS_DENIED` (403) → forbidden message · `VALIDATION_ERROR` (400) → inline ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-MDL-006, API-MDL-007, API-MDL-008 and API-MDL-009
This read returns inactive values as well as active ones — it is the manager's view, not the
consumer's, and the screen shows what API-MDL-011 would hide.
### F2-QUERY — API-MDL-006            traces=API-MDL-006,REQ-MDL-006,REQ-MDL-007
POST `/api/v1/mdl/lookup-types/{id}/values` · request `LookupValueCreateRequest` { code,
nameAr, nameEn, sortOrder } · response `LookupValueResponse` · kind **mutation**
Errors       : `MDL-409-VALUE-DUP` (409) → user message for RULE-MDL-002, routed inline to
               `code`, ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" ·
               en: "This code is already used within this type" ·
               `MDL-404-TYPE` (404) → user message (the parent type is gone) ·
               `VALIDATION_ERROR` (400) → inline · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]`
### F2-QUERY — API-MDL-007            traces=API-MDL-007,REQ-MDL-008
PUT `/api/v1/mdl/lookup-values/{id}` · request `LookupValueUpdateRequest` { nameAr, nameEn,
sortOrder } · response `LookupValueResponse` · kind **mutation**
Errors       : `MDL-404-VALUE` (404) → user message · `VALIDATION_ERROR` (400) → inline ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]` — the sort order may have moved the row
### F2-QUERY — API-MDL-008            traces=API-MDL-008,REQ-MDL-009
DELETE `/api/v1/mdl/lookup-values/{id}` · no request body · response `LookupValueResponse`
(isActiveFl=false) · kind **mutation**
Errors       : `MDL-404-VALUE` (404) → user message · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]`
### F2-QUERY — API-MDL-009            traces=API-MDL-009,REQ-MDL-010
PATCH `/api/v1/mdl/lookup-types/{id}/values/reorder` · request `LookupValueReorderRequest`
{ orderedValueIds[] } · response **a bare array** of `LookupValueResponse` in the persisted
order — not a `Page<T>` · kind **mutation**
Errors       : `MDL-400-REORDER-MISMATCH` (400) → user message on the value list (the submitted
               set is not exactly that type's values) · `MDL-404-TYPE` (404) → user message ·
               `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[lookup-values, *]` — every row's `sortOrder` may have changed, and the
               response's order is the persisted one, so the list re-renders from it
The whole ordered set is submitted, never one row's new position: the endpoint takes
`orderedValueIds[]` and the mismatch error exists precisely because a partial set is wrong.
### F2-SCREEN-INIT — SCR-MDL-001
Permission read : `MDL_LOOKUPS` present in the caller's effective menu → VIEW. CREATE, UPDATE
                  and DELETE are not readable from any published endpoint; their affordances
                  render and the server's `ACCESS_DENIED` is the authority (see SEC-FE).
Lookups used    : none — MDL has no lookup of its own (SRS §A6)
Foreign data    : the owner-module select and filter resolve through UXD-MDL-001; ONE shared
                  hook, long-lived cache, shared with SCR-MDL-002
Entity by id    : none published for either level — both forms hydrate from the row their own
                  search query already holds (ADR-MDL-005), so opening an edit performs no
                  second read and an invalidation re-reads through the same key
### F2-FACADE — SCR-MDL-001
Composes     : API-MDL-001, API-MDL-005 (lists) · API-MDL-002, API-MDL-003, API-MDL-004,
               API-MDL-006, API-MDL-007, API-MDL-008, API-MDL-009 (mutations) · the
               UXD-MDL-001 hook
State it owns: the type list and the selected type's value list, both derived from their
               queries' data (never a copy); the selected type id (from the route param); two
               filter objects, each carrying its own page and size; the pending drag order
               while a reorder is in flight; and a derived loading flag over the calls in flight
Operations   : createType · updateType · deactivateType (confirmation naming that consumer
               reads will stop returning its values — RULE-MDL-004) · createValue ·
               updateValue · deactivateValue (confirmation) · reorderValues (the whole ordered
               list, submitted once)
There is no activateType and no activateValue operation: no endpoint exists for either
(ADR-MDL-005). Components use the facade only; the facade uses the declared queries only.

### F2 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F2-QUERY — API-MDL-010            traces=API-MDL-010,REQ-MDL-013
POST `/api/v1/mdl/lookup-types/by-owner/search` · request `LookupTypeByOwnerSearchRequest`
{ filters[] } — **no sortField, no sortDirection, no page, no size** · response **a bare
array** of `OwnerGroupResponse` { ownerModuleCode, types[] } · kind **read query**
(ADR-MDL-002)
Cache key    : `[lookup-types-by-owner, filters]` — ownerModuleCode and key, and nothing more.
               No page or size belongs in this key because the endpoint accepts neither; adding
               them would key a variation the server cannot produce.
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `VALIDATION_ERROR` (400) → inline on the offending filter ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : n/a (a read). It is refreshed by SCR-MDL-001's type mutations through the shared
               `[lookup-types, *]` family, since a type created or deactivated there changes
               what this registry shows.
### F2-QUERY — API-MDL-011            traces=API-MDL-011,REQ-MDL-011,REQ-MDL-012
GET `/api/v1/mdl/lookups` · query param `type` = the lookup type's key · response **a bare
array** of `LookupValueResponse` — active values only, ordered by `sortOrder` · kind
**read query**
**Bound, and called by no screen** (ADR-MDL-007): the caller is a consuming module's backend
over the platform's in-process module interface, not a user with a screen. It is stated here so
the published surface is completely accounted for.
Errors       : `MDL-404-TYPE-KEY` (404) [REQ-MDL-012] → answered to the calling module — an
               unknown key is a not-found, never an empty success ·
               `ACCESS_DENIED` (403) → answered to the calling module
Cache key    : n/a — no client of this plan calls it
Invalidation : n/a. What a user can observe of this endpoint is indirect: deactivating a value
               or its type on SCR-MDL-001 is what makes it stop being returned (RULE-MDL-004).
### F2-SCREEN-INIT — SCR-MDL-002
Permission read : `MDL_TYPE_REGISTRY` present in the caller's effective menu → VIEW. This
                  screen has no other action.
Lookups used    : none
Foreign data    : the owner-module filter and the group headings resolve through UXD-MDL-001 —
                  the same shared hook SCR-MDL-001 uses, not a second call
Entity by id    : none — the groups carry their full type rows
### F2-FACADE — SCR-MDL-002
Composes     : API-MDL-010 · the UXD-MDL-001 hook
State it owns: the groups derived from the query's data, and the filter object (owner module,
               key) mirrored from the route's search params. No grouping and no count is
               composed here — both arrive in the response
Operations   : none — this screen writes nothing. Navigation to SCR-MDL-001 with a type
               selected is a route change, not an operation

<!-- PHASE:F2:END -->

<!-- PHASE:F3:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 3 — F3 — Forms & Validators

One block per `RULE-*` enforced on a form, plus the field constraints the published DTOs state.
No frontend-only validation the SRS does not state; every message is read from its catalog
code, never hard-coded; the locale resolves session → browser → `ar`; and a caller without the
write permission is answered by the server rather than by a pre-emptively disabled field.
Schemas are written with `zod` + `react-hook-form`.

**No `LOOKUP_VALID` validator exists anywhere in this module.** MDL owns no coded list (SRS
§A6), so no field binds to an option set of lookup values. The one field with a constrained set
is `ownerModuleCode`, whose set is another module's registry — its validator is named in the
SCR-MDL-001 block below and binds to the runtime-loaded list of UXD-MDL-001, never to a static
list of module codes.

### F3 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

Validation timing for this screen: **on blur for the unique key and code, on submit for the
rest** — declared once, and it holds for both the type form and the value form.
### F3-FIELD — SCR-MDL-001 (type, create)
key             · REQUIRED · LENGTH (maxLength 80, from `LookupTypeCreateRequest`) ·
                  UNIQUE_CHECK · when blur
ownerModuleCode · REQUIRED · LENGTH (maxLength 10) · BUSINESS_RULE (RULE-MDL-001) · when submit
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-MDL-001 (type, edit)
key, ownerModuleCode · read-only — not inputs at all; `LookupTypeUpdateRequest` carries neither
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
### F3-FIELD — SCR-MDL-001 (value, create)
code            · REQUIRED · LENGTH (maxLength 50) · UNIQUE_CHECK (within the selected type —
                  RULE-MDL-002) · when blur
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder       · REQUIRED · when submit
### F3-FIELD — SCR-MDL-001 (value, edit)
code            · read-only — `LookupValueUpdateRequest` does not carry it
nameAr, nameEn  · REQUIRED · LENGTH (maxLength 150) · when submit
sortOrder       · REQUIRED · when submit
UNIQUE_CHECK    : async, on blur — the type's `key` via `API-MDL-001` with an EQUALS filter;
                  the value's `code` via `API-MDL-005` with EQUALS filters on **both**
                  `lookupTypeId` and `code`, so the check's scope is the rule's scope. Neither
                  blocks submit on its own: the server's `MDL-409-TYPE-DUP` and
                  `MDL-409-VALUE-DUP` are the authority, routed inline to the same field. On
                  edit neither field is an input, so neither check runs.
### F3-VALIDATION — RULE-MDL-001      traces=REQ-MDL-002,AC-MDL-002
Statement : The system shall reject a lookup type registration whose owner module code has no
            ModuleRegistry row in the Security module.
Message   : from the catalog code `MDL-409-MODULE-NOT-REGISTERED` —
            ar: "الوحدة المالكة غير مسجّلة في وحدة الأمان" ·
            en: "The owning module is not registered in the Security module"
Scope     : CREATE
Field     : ownerModuleCode · kind BUSINESS_RULE · when submit
Validation shape : the control is a **select over the registered module codes** loaded through
            UXD-MDL-001, so the common case cannot be typed wrong at all; the validator asserts
            that the submitted value is one the runtime-loaded list contains, never that it is
            one of a static set. The server remains the authority — a module deregistered
            between load and submit is caught there — and the catalog message routes to this
            field. The rule's `Data source` is another module's registry, read SOFT at the
            application layer, so the client cannot decide it alone and does not try.
### F3-VALIDATION — RULE-MDL-002      traces=REQ-MDL-007,AC-MDL-007
Statement : The system shall reject a lookup value whose code already exists under the same
            lookup type.
Message   : from the catalog code `MDL-409-VALUE-DUP` —
            ar: "هذا الرمز مستخدم بالفعل ضمن هذا النوع" ·
            en: "This code is already used within this type"
Scope     : CREATE
Field     : code (of the value) · kind UNIQUE_CHECK · when blur, and again on submit by the server
Validation shape : uniqueness is scoped to the parent type, never globally — the same code
            under another type is legitimate, and a global check would reject a value the
            server accepts. The async check is bound to the selected parent id.
### F3-VALIDATION — RULE-MDL-003      traces=REQ-MDL-003,AC-MDL-003
Statement : The system shall prevent editing a lookup type's key after creation.
Message   : the rule's own text — ar: "لا يمكن تعديل مفتاح نوع اللوكب بعد إنشائه" ·
            en: "A lookup type's key cannot be changed after creation"
Scope     : UPDATE
Field     : key · kind BUSINESS_RULE · not a form check at all
Validation shape : there is **nothing to validate**: `key` is not an input on edit, because
            `LookupTypeUpdateRequest` does not carry it. The rule is expressed by the absence
            of the field rather than by a message on a control that would refuse. The form
            still *states* the rule beside the read-only key, so an editor learns why it cannot
            be changed instead of discovering a disabled control with no explanation.
### F3-VALIDATION — RULE-MDL-004      traces=REQ-MDL-004,AC-MDL-004
Statement : While a lookup type is inactive, the system shall exclude its values from consumer
            reads.
Message   : the rule's own text — ar: "هذا النوع معطّل حاليًا" ·
            en: "This lookup type is currently inactive"
Scope     : the deactivate action (API-MDL-004)
Field     : none — a row action · kind BUSINESS_RULE · when submit
Validation shape : **not a validation this form performs at all** — it is a consequence the
            deactivate confirmation names before the act: every consuming module stops
            receiving this type's values. The rule's text is shown as the state label on an
            inactive type row, so the same words explain the row and the warning. Nothing on
            this screen is hidden by it: the manager's value list (API-MDL-005) still shows the
            values, which is the difference between this screen and a consumer.
Business-code fields: `key` and `code` are both client-chosen strings, not platform-numbered,
and both are read-only after create (per the two update DTOs). Neither is generated or
predicted on the client.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without CREATE, UPDATE or DELETE receives `ACCESS_DENIED`
on submit and the form shows the localized forbidden message; fields are not pre-emptively
disabled, because no published endpoint tells the screen which actions the caller holds.

### F3 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

This screen has **no form**: SRS SCR-REQ-MDL-002 §B3 reads "read-only browse; no create/update
here", and every field of `OwnerGroupResponse` is read-only.
### F3-FIELD — SCR-MDL-002 (filters, not a form)
ownerModuleCode · optional · the select is the UXD-MDL-001 hook's list, so it offers only
                  registered module codes
key             · optional · LENGTH (maxLength 80) · a LIKE filter
Validation shape : filter validation only, written with `zod` over the route's search params so
                  that an address someone shared is validated the same way a typed filter is.
                  No business rule is enforced here, because nothing is written.
No RULE-* is enforced on this screen. RULE-MDL-004's effect is visible — a deactivated type
leaves this registry's active set — but the rule fires on the consumer read, not here.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen — the navigation
guard of SEC-FE stops the route.

<!-- PHASE:F3:END -->

<!-- PHASE:F4:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 4 — F4 — Screens & Routes

One block per `SCR-*`: routes, chunk, guard, components, mode, facade, shared UI and
cross-module citations. Routes are named by the container pattern — `TREE_MASTER_DETAIL` → a
TreePage hosting the master list and its detail, with the list route registered **before** any
`:id` route; `FULL_PAGE` with no entry sub-view → a single Page and no entry route. One lazy
chunk per composite screen. Every `PERM_*` name below is the backend's, never invented here,
and every route sits under the module segment `/reference-data`.

### F4 · SCR-MDL-001 — اللوكبات العامة / Generic Lookups

### F4-SCREEN — SCR-MDL-001            traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001
Routes       : base slug `lookups`, under the module segment `/reference-data` —
               `/reference-data/lookups` (the type list, registered **before** any `:id` route
               so a type id is never matched as the list itself) ·
               `/reference-data/lookups/new` (create a type — a **static** segment registered
               BEFORE the `:id` routes) ·
               `/reference-data/lookups/:typeId` (that type's values beside the list) ·
               `/reference-data/lookups/:typeId/edit` (edit the type) ·
               `/reference-data/lookups/:typeId/values/new` (create a value under it) ·
               `/reference-data/lookups/:typeId/values/:valueId/edit` (edit a value)
Chunk        : one lazy chunk for this composite screen — both panes and both forms share it;
               neither form is a second chunk
Guard        : every route element guarded by `PERM_MDL_LOOKUPS_VIEW`, evaluated as
               "`MDL_LOOKUPS` is present in the caller's effective menu". CREATE, UPDATE and
               DELETE are not readable from any published endpoint, so `/new`, `/edit` and the
               value routes carry the same VIEW guard and the server's 403 is the authority on
               the write itself.
Components   : `LookupsPage` (route-level, TREE_MASTER_DETAIL — hosts the type list and the
               value detail) · `LookupTypeList`, `LookupTypeFilters`, `LookupTypeForm`,
               `LookupValueTable`, `LookupValueFilters`, `LookupValueForm`,
               `ValueReorderHandle`, `DeactivateConfirm` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` and
               `/values/new` → CREATE, `/edit` → EDIT, `/:typeId` → VIEW — never from a parent
               prop
Facade       : the SCR-MDL-001 facade of F2; the page never calls a query directly
Shared UI    : split pane, data table, filter bar, text field, number field, select (the owner
               module), drag handle, confirmation dialog, inline field errors, localized
               message banner
Cross-module : UXD-MDL-001 (the owner module) — the one field on this screen whose
               authoritative source is another module
The selected type is a route param, so a type's value list is a linkable address and the
browser's back gesture returns to the list. Both levels show Deactivate and neither shows an
Activate: no endpoint exists for the second half (ADR-MDL-005). The drag handle submits the
whole ordered set through API-MDL-009 rather than writing one row's `sortOrder`.

### F4 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

### F4-SCREEN — SCR-MDL-002            traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001
Routes       : base slug `type-registry`, under `/reference-data` —
               `/reference-data/type-registry` — the only route; no `new`, no `:id`, no
               `:id/edit`, because this screen addresses no record it could edit. The owner
               module and the key filter live in the route's search params, so the browse IS
               its address
Chunk        : one lazy chunk for this screen
Guard        : the route element guarded by `PERM_MDL_TYPE_REGISTRY_VIEW`, evaluated as
               "`MDL_TYPE_REGISTRY` is present in the caller's effective menu"
Components   : `TypeRegistryPage` (route-level, FULL_PAGE) · `RegistryFilters`,
               `OwnerGroupSection`, `RegistryTypeTable` (presentational)
Mode         : not applicable — no CREATE, EDIT or VIEW mode exists to resolve; this screen
               writes nothing
Facade       : the SCR-MDL-002 facade of F2
Shared UI    : filter bar, select (the owner module), section headings, data table, localized
               message banner
Cross-module : UXD-MDL-001 — here it is the grouping itself, not a field of a form
Each type row links to `/reference-data/lookups/:typeId`, which is SCR-MDL-001's own route and
carries its own guard — reviewing and managing are two steps of one task, and this screen does
neither half of the second. API-MDL-011 has no component and no route here (ADR-MDL-007).

<!-- PHASE:F4:END -->

<!-- PHASE:SEC-FE:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 5 — SEC-FE

The frontend half of the security model, per `SCR-*`: the navigation guard and the per-action
UI behaviour. Permission names are the backend registry's and the SRS Access summary's, never
redeclared. One mechanism gates both screens — the **menu gate**: the screen's page code is
present in the effective menu the security module serves for this caller. Action-level
permissions are not readable from any published MDL endpoint, so an action's affordance renders
for a caller who holds the screen and the server's `ACCESS_DENIED` is the authority, shown as
its localized message. Never split — level-1 only.

### SEC-FE · SCR-MDL-001 — اللوكبات العامة / Generic Lookups
Permissions      : `PERM_MDL_LOOKUPS_VIEW`, `PERM_MDL_LOOKUPS_CREATE`,
`PERM_MDL_LOOKUPS_UPDATE`, `PERM_MDL_LOOKUPS_DELETE`
Navigation guard : `MDL_LOOKUPS` must be present in the caller's effective menu; a caller
without it is sent to the unauthorized destination, and every route of this screen — the list,
`new`, `:typeId`, `:typeId/edit` and both value routes — carries the same guard.
Per action       : VIEW → the gate above, exact, and it covers both panes: a caller who holds
the screen sees types and values alike. CREATE (a type, and a value under it), UPDATE (edit at
either level, and the reorder) and DELETE (deactivate at either level) → the affordances render
and `ACCESS_DENIED` from the server is shown as the localized forbidden message. DELETE here
means deactivate and nothing else: no hard delete exists at either level, which is why the SRS
Access summary's DELETE column reads "role-granted (deactivate)".
The screen-level grant is the whole granularity. Per-lookup-type permissions — letting a role
manage `USER_STATUS` but not `PAYMENT_METHOD` — are an explicit SRS scope exception
(§A2 Out of scope), so no per-type gate is drawn, attempted, or hinted at in the UI.

### SEC-FE · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner
Permissions      : `PERM_MDL_TYPE_REGISTRY_VIEW`
Navigation guard : `MDL_TYPE_REGISTRY` must be present in the caller's effective menu.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE: the SRS Access
summary gives this screen VIEW alone, and the screen writes nothing. Its links into
SCR-MDL-001 are rendered unconditionally; the target route's own guard stops a caller who does
not hold that screen, so a reviewer who may browse but not manage sees the registry and is
refused at the door of the editor rather than shown a dead link.

**Across both screens.** A forbidden response is shown as its localized catalog message, never
as a silent no-op and never as a generic failure. An unauthenticated response returns the
caller to the platform's sign-in destination and discards the server-state cache, so no data of
the previous identity survives into the next. No screen composes a permission name, and no
screen holds a local copy of the caller's grants: the menu response is the single source, and a
failure to load it renders no MDL entry and grants no MDL route — access narrows, never widens.

<!-- PHASE:SEC-FE:END -->

<!-- PHASE:ALIGN-FE:START traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,API-MDL-001,API-MDL-002,API-MDL-003,API-MDL-004,API-MDL-005,API-MDL-006,API-MDL-007,API-MDL-008,API-MDL-009,UXD-MDL-001,SCR-MDL-001,REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,SCR-MDL-002 -->
## PHASE 6 — ALIGN-FE

The alignment self-check is this phase's content, and its `RESULT` row is written by the
orchestrator from the analyze report. Never split — level-1 only.

```
ALIGN-FE — MDL v1
row           backing check   assertion
SCREENS       orphans         both SCR-MDL-001 and SCR-MDL-002 are referenced by a plan block —
                              each has a block in F1, F2, F3 and F4 and an RF5 block in SEC-FE.
                              The phases are not split per screen because the SCR count is 2,
                              below the threshold of 5
UXD           orphans         UXD-MDL-001 is cited by a plan block — by both screens' F2
                              SCREEN-INIT blocks, by SCR-MDL-001's F3 validator for
                              RULE-MDL-001, and by both F4 Cross-module lines
TRACES        traces          every PHASE carries traces=; UXD-MDL-001 traces to its REQ and
                              its AC; every SCR traces to its REQ and to its UXD
API           traces          every API-MDL-* this plan cites is defined in the fetched
                              api-docs — through the API ID BINDING annex of ADR-MDL-001, and
                              never in the backend plan's contract table, which is the artifact
                              the three shape diffs belong to. No foreign module's API id is
                              cited here at all; the one cross-module endpoint this frontend
                              depends on is named in ui-ux-spec-mdl.md, where UXD-MDL-001 is
                              defined
FOREIGN       xref-surface    every reference to another module's surface resolves in that
                              module's own artifacts
REGISTRY      registry-agree  the UXD and both SCR defined here are in registry-exec-fe-mdl.md,
                              and nothing else is
LANGUAGES     languages       labels and messages in ar + en
MARKERS       markers         the parser reports no structural or semantic error for the
                              frontend track's exec plan
DECISIONS     refs-exist      every ADR this plan cites exists on disk in erp/decisions/MDL/ —
                              ADR-MDL-001 … ADR-MDL-007
COVERAGE      (the report)    C7.16, C7.18 and C7.20 — all three are P3.1
                              clauses over backend artifacts this stage does not write. No
                              C8.* or C9.* clause reported having examined nothing
RESULT        PASSED ✓ — 0 findings
```

### Operations coverage

| Operation | API | SCR action | Route | Status |
|---|---|---|---|---|
| search lookup types | API-MDL-001 | SCR-MDL-001 search | /reference-data/lookups | ✓ |
| create lookup type | API-MDL-002 | SCR-MDL-001 create type | /reference-data/lookups/new | ✓ |
| update lookup type | API-MDL-003 | SCR-MDL-001 edit type | /reference-data/lookups/:typeId/edit | ✓ |
| deactivate lookup type | API-MDL-004 | SCR-MDL-001 deactivate type | /reference-data/lookups/:typeId | ✓ |
| search lookup values of a type | API-MDL-005 | SCR-MDL-001 value list | /reference-data/lookups/:typeId | ✓ |
| create lookup value | API-MDL-006 | SCR-MDL-001 create value | /reference-data/lookups/:typeId/values/new | ✓ |
| update lookup value | API-MDL-007 | SCR-MDL-001 edit value | /reference-data/lookups/:typeId/values/:valueId/edit | ✓ |
| deactivate lookup value | API-MDL-008 | SCR-MDL-001 deactivate value | /reference-data/lookups/:typeId | ✓ |
| reorder lookup values | API-MDL-009 | SCR-MDL-001 drag to reorder | /reference-data/lookups/:typeId | ✓ |
| browse the registry by owner | API-MDL-010 | SCR-MDL-002 render | /reference-data/type-registry | ✓ |
| read values by key (consumer API) | API-MDL-011 | — a consuming module's backend call | — (ADR-MDL-007) | ✗ |
| activate a lookup type | — none published | SCR-MDL-001 — not drawn | — (ADR-MDL-005) | ✗ |
| activate a lookup value | — none published | SCR-MDL-001 — not drawn | — (ADR-MDL-005) | ✗ |
| read one type / one value by id | — none published | hydrated from the search cache | — (ADR-MDL-005) | ✗ |

Eleven rows carry a published endpoint; ten of those carry a route and a ✓. Four rows carry a
✗ with the ADR that explains it — one endpoint published for a caller that is not this frontend
(ADR-MDL-007), and three operations with no endpoint at all (ADR-MDL-005). No row is a ✗ for
want of a decision.

<!-- PHASE:ALIGN-FE:END -->

---

## Hand-off

The implementer reads the phases in profile order — F1 models, F2 hooks, F3 forms, F4 screens
and routes, SEC-FE guards — takes design intent from `ui-ux-spec-mdl.md`, and takes every
request and response shape from `_inputs/api-docs-mdl.md`. No route, component, permission or
field that is not traceable to an F-block above is invented: a gap is an ADR in
`erp/decisions/MDL/`, never an invention. Three response shapes travel in this module and the
difference is load-bearing — two paged reads, five bare arrays or single objects, and the rest
single objects — so no block may be read through an envelope another block declares. The plan
and its registry are split by the toolkit into `packages/frontend-execution/` and delivered on
the frontend delivery branch after the `gate:pass-2` verdict, then tagged.

══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-srs>>>
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

<<<INPUT: registry-db>>>
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

<<<INPUT: registry-exec-fe>>>
## REGISTRY — P3.2 — MDL v1
══════════════════════════════════════════════════════════════════

ID RANGES
UXD-MDL-001 .. UXD-MDL-001 · SCR-MDL-001 .. SCR-MDL-002

SCR ids: SCR-MDL-001, SCR-MDL-002

UXD ids: UXD-MDL-001

Last sequence per atom: SCR: 002 · UXD: 001

SCREENS
| SCR | Name (ar / en) | Container pattern | Owning ENT | Permissions |
|---|---|---|---|---|
| SCR-MDL-001 | اللوكبات العامة / Generic Lookups | TREE_MASTER_DETAIL | ENT-MDL-001 (+ ENT-MDL-002) | PERM_MDL_LOOKUPS_VIEW, PERM_MDL_LOOKUPS_CREATE, PERM_MDL_LOOKUPS_UPDATE, PERM_MDL_LOOKUPS_DELETE |
| SCR-MDL-002 | سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner | FULL_PAGE (no entry sub-view — ADR-MDL-003) | ENT-MDL-001 | PERM_MDL_TYPE_REGISTRY_VIEW |

Two screens, so no `sub_bearing` phase splits per screen (the threshold is an SCR count of 5 or
more): F1, F2, F3 and F4 each carry both screens' blocks at level 1, with every block heading
naming its `SCR-*`.

UXD INDEX
| UXD | Screen(s) | Field | Owner module · API used |
|---|---|---|---|
| UXD-MDL-001 | SCR-MDL-001, SCR-MDL-002 | ownerModuleCode — the type's owning module | SEC · `ModuleRegistry` (ENT-SEC-004), read through the security module's registry search (named in ui-ux-spec-mdl.md) |

One `UXD-*` for the whole module. It is **not** a lookup dependency: SRS §A6 records that MDL
introduces no coded list of its own, and the owner-module field's valid set is another module's
registry data, consumed through XM-MDL-001 (SOFT-READ) — §A.5's definition exactly
(ADR-MDL-004). The screen gate (the security module's effective menu) is an authorization
dependency, not a displayed field, and is recorded in the plan's SEC-FE phase rather than
minted here.

API COVERAGE
| Status | Count | API ids |
|---|---|---|
| used by this frontend | 10 | API-MDL-001 .. API-MDL-010 |
| documented, deliberately uncalled | 1 | API-MDL-011 — the consumer read a consuming module's backend performs over the platform's in-process module interface; bound and blocked out in F2 — ADR-MDL-007 |
| used but undocumented | 0 | — no endpoint is called that the api-docs lack |
| documented but unbound | 0 | all 11 published endpoints are bound by the API ID BINDING annex — ADR-MDL-001 |

RESPONSE SHAPES — the difference is load-bearing and is stated per endpoint in F2
| Shape | API ids |
|---|---|
| `Page<T>` | API-MDL-001, API-MDL-005 |
| a bare array | API-MDL-009, API-MDL-010, API-MDL-011 |
| a single object | API-MDL-002, API-MDL-003, API-MDL-004, API-MDL-006, API-MDL-007, API-MDL-008 |
Only the two paged reads carry `page` and `size` in their cache keys. API-MDL-010 accepts
`filters` alone — no sort and no paging — so neither belongs in its key.

SHAPE DIFFS AGAINST THE BACKEND PLAN
Three reads are `POST …/search` where `backend-execution-plan-mdl.md`'s contract table still
predicts `GET`: API-MDL-001, API-MDL-005, API-MDL-010. The api-docs and the SRS Part B `B5`
tables agree with each other, so the backend plan is the one artifact that lags, and
`gov.py analyze` reports it there as three C8.4 findings. Correcting it is three rows in a P3.1
artifact, which §8 puts outside this stage's boundary. Recorded here and in ADR-MDL-002.

OPERATIONS WITHOUT AN ENDPOINT
activate a lookup type · activate a lookup value · read one type by id · read one value by id —
named by SRS Part B, required by no `REQ-*`, and omitted from the frontend rather than faked
(ADR-MDL-005). Deactivation is therefore one-way from the screen, and the confirmation says so.

LOOKUPS
None. SRS §A6: MDL introduces no domain-specific coded list of its own — it is the generic
mechanism every other module's lookup types run on top of. No lookup hook exists anywhere in
the plan, no `LOOKUP_VALID` validator binds an option set, and no enum is modelled. The one
constrained field, `ownerModuleCode`, binds to the runtime-loaded module list of UXD-MDL-001.

ALIGN-FE
The verdict row inside the plan's ALIGN-FE block is written by the orchestrator from the
analyze report; findings fixed by this stage: 0.

ADRs
erp/decisions/MDL/ADR-MDL-001.md (ACCEPTED, non-breaking — API id binding annex) ·
erp/decisions/MDL/ADR-MDL-002.md (ACCEPTED, non-breaking — three POST `…/search` reads, and the stale backend contract table) ·
erp/decisions/MDL/ADR-MDL-003.md (ACCEPTED, non-breaking — container pattern for the read-only registry browse) ·
erp/decisions/MDL/ADR-MDL-004.md (ACCEPTED, non-breaking — the owner-module field reads the security module's registry; UXD-MDL-001) ·
erp/decisions/MDL/ADR-MDL-005.md (ACCEPTED, non-breaking — operations with no published endpoint) ·
erp/decisions/MDL/ADR-MDL-006.md (ACCEPTED, non-breaking — `isActiveFl` read-only vs SRS B3's input list) ·
erp/decisions/MDL/ADR-MDL-007.md (ACCEPTED, non-breaking — API-MDL-011 bound but drawn on no screen)
Carried from earlier stages: none — MDL raised no ADR before P3.2. No BLOCKED ADR.

TRACEABILITY
REQ covered by ≥1 SCR/F-block: 13/13 — REQ-MDL-001..010 appear in the `traces=` of SCR-MDL-001's
blocks in every phase, and REQ-MDL-011, REQ-MDL-012, REQ-MDL-013 in SCR-MDL-002's. REQ-MDL-011
and REQ-MDL-012 are covered the only way a UI can cover a server-to-server read: through
API-MDL-011's bound F2 block, and through the values and active flags managed on SCR-MDL-001
that decide what that read returns.
Orphan REQ: none.
AC covered: 13/13 (each AC accompanies its REQ in the same traces).
SCR covered: 2/2 — both carry a block in F1, F2, F3 and F4 and an RF5 block in SEC-FE.
UXD cited by an F-block: 1 of 1 — none unreferenced, none dangling.

Event
"P3.2 completed: MDL v1 — 2 screens, 1 UXD, 11/11 API bound (10 called), 4 sub-bearing phases
unsplit (2 SCR < 5), ALIGN-FE stamped by the orchestrator, 7 ADRs"
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
