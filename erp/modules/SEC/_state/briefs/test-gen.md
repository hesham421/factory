# BRIEF — stage `test-gen` (Test Generation) · module SEC · v1 · profile `erp`

Lane `test-gen` · implementer claude:opus · effort high · round 1

## Rules that bind this run
- Questions: **forbidden**. A `[QUESTION]` block is refused. Ambiguity → ADR in `erp/decisions/SEC/` (`ADR-{MOD}-{seq:03d}.md`): non-breaking → continue; breaking → status BLOCKED and stop.
- Owns IDs: TC — ID grammar `{prefix}-{MOD}-{seq}` (seq width 3); never re-number, never restart a sequence.
- Read only what this brief contains (generated current state); never open version folders yourself.
- Write exactly these files (complete files; in a delta version only what changed, plus `change-manifest.md`):
- `erp/modules/SEC/test_gen/backend-test-plan-sec.md`
- `erp/modules/SEC/test_gen/frontend-test-plan-sec.md`
- `erp/modules/SEC/test_gen/test-execution-manifest-sec.md` (optional)
- `erp/system-test-index-erp.md` (optional)
- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; when running as the operator, write the files directly.

## Contracts checked by `gov.py analyze` after this stage
- **C10** acceptance criteria → test generation (standalone): C10.1 traces {'from': 'TC', 'to': ['AC', 'XM', 'UXD'], 'min': 1, 'mode': 'any'} [CRITICAL]; C10.2 orphans {'kind': 'AC', 'referenced_by': ['TC'], 'min': 1} [MAJOR]; C10.3 markers {'artifact': 'backend-test-plan', 'track': 'backend', 'plan': 'test'} [CRITICAL]; C10.4 markers {'artifact': 'frontend-test-plan', 'track': 'frontend', 'plan': 'test'} [CRITICAL]; C10.5 ids-owned {'stage': 'test-gen'} [CRITICAL]; C10.6 exists {'artifact': 'test-execution-manifest', 'when': 'profile.stack.testing.manifest'} [MINOR]

---
# ENGINE
```
ENGINE        : test-gen — Test Generation   (STANDALONE — outside the line, on demand)
LANE          : test-gen · questions forbidden · derives from `AC-*` (module) + `XM-*`/`UXD-*` (integration)
SCOPE         : module · modules SEC
MODULE        : SEC · v1 · profile erp (ERP Platform)
READS         : srs · backend-execution-plan? · frontend-execution-plan? · registry-srs · registry-db? · registry-exec-fe?   (from _state/ — "?" = optional — read for EACH module in scope)
PRODUCES      : backend-test-plan-sec.md · frontend-test-plan-sec.md · test-execution-manifest-sec.md (optional)
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

This run: **scope = `module`**, modules = `SEC`.

| Scope | TC sources | Phases populated |
|---|---|---|
| `module` | `AC-*` of the one module (§3) | the module-scope phases only (`TEST-PLAN-BE` on backend; the equivalent on frontend) — **identical in shape to a single-module run today** |
| `modules` | `AC-*` per module (§3) **+** `XM-*` (§4) and `UXD-*` (§5) between the *selected* modules only | module-scope phases for every selected module, plus the integration phase(s) (`profile…phases[*].integration: true`) wherever a real linking atom pairs two selected modules |
| `project` | everything `modules` does, across **every** module the factory has ever produced a version for, **plus** a derived coverage rollup | the same as `modules`, plus `system-test-index-{profile}.md` (§9) — no new atom, no new gate |

Rules that hold at every scope:
1. a module never gets an integration TC for a module that is **not** in the current
   selection — running `--module SEC` alone never touches another module's `XM`/`UXD`;
2. an integration phase with no real linking atom among the selected modules stays **absent**
   from the output — never an empty `PHASE` block, never a guessed pairing;
3. `--module` output is produced exactly as it always was — no integration phase key, no
   `system-test-index`, no extra section — so a single-module run stays byte-identical in
   shape to before this scope model existed.

## 3. Derivation (module scope) — every `TC-*` comes from an `AC-*`

`TC-*` (`TC-SEC-{seq}`, 3-digit seq,
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
also in `SEC` — an `XM-*` targeting a module outside the selection is
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
module that owns the displayed data) is also in `SEC`.

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
<!-- TC:TC-SEC-<seq>:START traces=AC-SEC-<seq>,REQ-SEC-<seq>[,API-SEC-<seq>|SCR-SEC-<seq>|XM-SEC-<seq>|UXD-SEC-<seq>] -->
### TC-SEC-<seq> — <title>
Derived from : AC-SEC-<seq>  (REQ-SEC-<seq>)   |   XM-SEC-<seq> (REQ-SEC-<seq>)   |   UXD-SEC-<seq> (REQ-SEC-<seq>, AC-SEC-<seq>)
Exercises    : API-SEC-<seq> <verb path>   |   SCR-SEC-<seq> <route>
Rule / code  : RULE-SEC-<seq> → <catalog code> | —
Scenario     : <tag> · data class <class> · language <ar|en|ALL>
Preconditions: <from Given — concrete entities, role, state | for XM/UXD: the target/owner entity present or absent>
Steps        : 1. … 2. … (from When — one observable action per step)
Expected     : <from Then — status / body shape / message per language / UI state>
Test data    : <values named in the AC; placeholders marked, never invented business data>
<!-- TC:TC-SEC-<seq>:END -->
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

### Track `backend` — one file per selected module: `backend-test-plan-sec.md`

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

### Track `frontend` — one file per selected module: `frontend-test-plan-sec.md`

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
`test-execution-manifest-sec.md` —
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
Data source: ENT-SEC-007 (the role's module grants) · ENT-SEC-005 (the screen's owning module)
Message    : ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" · en: "Cannot grant a screen without first granting its module"
Traces     : REQ-SEC-013
Source     : security-module-plan-en.md §4.2

### RULE-SEC-002 — منع منح إجراء دون منح الشاشة / No action grant without its screen grant
Scope      : ENT-SEC-009
Trigger    : on create (action grant)
Statement  : The system shall prevent an action grant for a role that does not hold the action's screen grant.
Data source: ENT-SEC-008 (the role's screen grants) · ENT-SEC-006 (the action's owning screen)
Message    : ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" · en: "Cannot grant an action without first granting its screen"
Traces     : REQ-SEC-014
Source     : security-module-plan-en.md §4.2

### RULE-SEC-003 — الإلغاء المتسلسل عند سحب منح الوحدة / Cascade revoke on module-grant removal
Scope      : ENT-SEC-007
Trigger    : on delete (module grant)
Statement  : The system shall delete every screen grant and action grant that module covered for that role when its module grant is revoked.
Data source: ENT-SEC-008 and ENT-SEC-009 (the grants to remove) · ENT-SEC-005 and ENT-SEC-006 (which screens and actions that module covers)
Message    : ar: "سيتم سحب كل منح الشاشات والإجراءات ضمن هذه الوحدة لهذا الدور" · en: "Every screen and action grant under this module for this role will be revoked"
Traces     : REQ-SEC-015
Source     : security-module-plan-en.md §4.2

### RULE-SEC-004 — رفض تسجيل شاشة لوحدة غير مسجّلة / No screen under an unregistered module
Scope      : ENT-SEC-005
Trigger    : on create (screen registration)
Statement  : The system shall reject a screen registration whose module code has no ModuleRegistry row.
Data source: ENT-SEC-004 (the ModuleRegistry row the submitted module code must match)
Message    : ar: "الوحدة غير مسجّلة" · en: "Module is not registered"
Traces     : REQ-SEC-018
Source     : security-module-plan-en.md §4.3

### RULE-SEC-005 — منع تضارب الإجراءات لمستخدم واحد / Prevent conflicting actions on one user
Scope      : ENT-SEC-003, ENT-SEC-009
Trigger    : on create (role assignment or action grant)
Statement  : The system shall prevent assigning a user, by any combination of roles, both actions of a module-declared conflicting pair.
Data source: ENT-SEC-003 (every role the user holds) · ENT-SEC-009 (the action grants those roles carry) · ENT-SEC-006 (the owning module's action declarations, which carry the conflicting pair)
Message    : ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" · en: "This user already holds a conflicting action"
Traces     : REQ-SEC-020
Source     : security-module-plan-en.md §4.4; general-accounting-system-plan-en.md §8.2

### RULE-SEC-006 — رفض رمز إعادة تعيين منتهٍ أو مُستخدَم / Reject expired or used reset token
Scope      : ENT-SEC-012
Trigger    : on submit (password reset completion)
Statement  : The system shall reject a password-reset submission whose token is expired or already used.
Data source: ENT-SEC-012 (the token's expiry and used state)
Message    : ar: "رابط إعادة التعيين غير صالح أو منتهي" · en: "This reset link is invalid or has expired"
Traces     : REQ-SEC-008
Source     : security-module-plan-en.md §3

### RULE-SEC-007 — اشتراط VIEW كبوابة على مستوى الشاشة / VIEW as the screen-level gateway action
Scope      : ENT-SEC-009
Trigger    : on evaluate (any action check) and on create (action grant, informational)
Statement  : The system shall require a role to hold the VIEW action grant on a screen before any other action grant on that screen takes effect for it.
Data source: ENT-SEC-009 (the role's action grants on that screen) · ENT-SEC-006 (which registered action is VIEW, and the screen it belongs to)
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

<<<INPUT: backend-execution-plan>>>
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
| API-SEC-005 | search users | POST | /api/v1/sec/users/search | REQ-SEC-009 · DBF-SEC-002,DBF-SEC-003,DBF-SEC-005,DBF-SEC-006,DBF-SEC-007 |
| API-SEC-006 | create user | POST | /api/v1/sec/users | REQ-SEC-009 · DBF-SEC-002,DBF-SEC-003,DBF-SEC-005,DBF-SEC-006,DBF-SEC-007 |
| API-SEC-007 | update user | PUT | /api/v1/sec/users/{id} | REQ-SEC-009 · DBF-SEC-003,DBF-SEC-005,DBF-SEC-006 |
| API-SEC-008 | assign roles to user | PUT | /api/v1/sec/users/{id}/roles | REQ-SEC-010 · DBF-SEC-026,DBF-SEC-027,DBF-SEC-028,DBF-SEC-029 |
| API-SEC-009 | deactivate user | DELETE | /api/v1/sec/users/{id} | REQ-SEC-011 · DBF-SEC-007,DBF-SEC-009,DBF-SEC-081,DBF-SEC-082 |
| API-SEC-010 | reactivate user | PATCH | /api/v1/sec/users/{id} | REQ-SEC-031 · DBF-SEC-007,DBF-SEC-009 |
| API-SEC-011 | approve/reject signup | PATCH | /api/v1/sec/signup-requests/{id} | REQ-SEC-004,REQ-SEC-005 · DBF-SEC-102,DBF-SEC-103,DBF-SEC-104,DBF-SEC-001 |
| API-SEC-012 | search roles | POST | /api/v1/sec/roles/search | REQ-SEC-012 · DBF-SEC-015,DBF-SEC-016,DBF-SEC-017,DBF-SEC-020 |
| API-SEC-013 | create role | POST | /api/v1/sec/roles | REQ-SEC-012 · DBF-SEC-015,DBF-SEC-016,DBF-SEC-017,DBF-SEC-018,DBF-SEC-019 |
| API-SEC-014 | grant module to role | POST | /api/v1/sec/roles/{id}/modules | REQ-SEC-012 · DBF-SEC-061,DBF-SEC-062,DBF-SEC-063,DBF-SEC-064 |
| API-SEC-015 | revoke module grant | DELETE | /api/v1/sec/roles/{id}/modules/{moduleId} | REQ-SEC-015 · DBF-SEC-061,DBF-SEC-062,DBF-SEC-066,DBF-SEC-071 |
| API-SEC-016 | grant screen to role | POST | /api/v1/sec/roles/{id}/screens | REQ-SEC-013 · DBF-SEC-066,DBF-SEC-067,DBF-SEC-068,DBF-SEC-069 |
| API-SEC-017 | grant action to role | POST | /api/v1/sec/roles/{id}/actions | REQ-SEC-014,REQ-SEC-020,REQ-SEC-030 · DBF-SEC-071,DBF-SEC-072,DBF-SEC-073,DBF-SEC-074 |
| API-SEC-018 | register module | POST | /api/v1/sec/registry/modules | REQ-SEC-016 · DBF-SEC-031,DBF-SEC-032,DBF-SEC-033 |
| API-SEC-019 | register screen | POST | /api/v1/sec/registry/screens | REQ-SEC-017,REQ-SEC-018 · DBF-SEC-040,DBF-SEC-041,DBF-SEC-042,DBF-SEC-043 |
| API-SEC-020 | register action | POST | /api/v1/sec/registry/actions | REQ-SEC-019 · DBF-SEC-050,DBF-SEC-051,DBF-SEC-052,DBF-SEC-053,DBF-SEC-054 |
| API-SEC-021 | search registry | POST | /api/v1/sec/registry/search | REQ-SEC-016 · DBF-SEC-031,DBF-SEC-040,DBF-SEC-050 |
| API-SEC-022 | dashboard summary | GET | /api/v1/sec/dashboard | REQ-SEC-022,REQ-SEC-023 · DBF-SEC-007,DBF-SEC-076,DBF-SEC-081,DBF-SEC-084,DBF-SEC-086 |
| API-SEC-023 | search audit log | POST | /api/v1/sec/audit-log/search | REQ-SEC-025 · DBF-SEC-084,DBF-SEC-085,DBF-SEC-086 |
| API-SEC-024 | export audit log | GET | /api/v1/sec/audit-log/export | REQ-SEC-026 · DBF-SEC-084,DBF-SEC-085,DBF-SEC-086,DBF-SEC-087,DBF-SEC-088,DBF-SEC-089 |
| API-SEC-025 | list active sessions | POST | /api/v1/sec/sessions/search | REQ-SEC-027 · DBF-SEC-076,DBF-SEC-079,DBF-SEC-081 |
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
`{MOD}-{http}[-{SLUG}]` (profile.stack.backend.api.error_code_format; `{MOD}` = SEC, `{http}` =
the row's HTTP status, `{SLUG}` = SCREAMING-KEBAB, the slug half optional — e.g.
`SEC-409-USER-DUP`, and `SEC-500` where no slug is needed). Stated once here so `api-verify` can
assert on it. Every catalog row (§Error Catalog) is registered as a
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
LOOKUP FIELDS: `statusCode` → key `USER_STATUS` → GET /api/v1/mdl/lookups?type=USER_STATUS (API-MDL-011 — MDL's consumer lookup API; v1 validates server-side against the closed set per ADR-SEC-001) — stores the code, never a numeric FK.
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
| DBF-SEC-064 | grantedAt | granted_at | Instant | NOT NULL | Yes | — |
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
| API-SEC-002 | /auth/signup | POST | SignupSubmitRequest | SignupRequestResponse | v1 |
| API-SEC-003 | /auth/password-reset/request | POST | PasswordResetRequest | ConfirmationResponse | v1 |
| API-SEC-004 | /auth/password-reset/complete | POST | PasswordResetCompleteRequest | ConfirmationResponse | v1 |
| API-SEC-005 | /users/search | POST | UserSearchRequest | paginated list of UserResponse | v1 |
| API-SEC-006 | /users | POST | UserCreateRequest | UserResponse | v1 |
| API-SEC-007 | /users/{id} | PUT | UserUpdateRequest | UserResponse | v1 |
| API-SEC-008 | /users/{id}/roles | PUT | UserRoleAssignmentRequest | UserResponse | v1 |
| API-SEC-009 | /users/{id} | DELETE | — | UserStatusResponse | v1 |
| API-SEC-010 | /users/{id} | PATCH | — | UserStatusResponse | v1 |
| API-SEC-011 | /signup-requests/{id} | PATCH | SignupDecisionRequest | UserResponse \| SignupRequestResponse | v1 |
| API-SEC-012 | /roles/search | POST | RoleSearchRequest | paginated list of RoleResponse | v1 |
| API-SEC-013 | /roles | POST | RoleCreateRequest | RoleResponse | v1 |
| API-SEC-014 | /roles/{id}/modules | POST | RoleModuleGrantRequest | RoleModuleGrantResponse | v1 |
| API-SEC-015 | /roles/{id}/modules/{moduleId} | DELETE | — | ModuleGrantRevokeResponse | v1 |
| API-SEC-016 | /roles/{id}/screens | POST | RoleScreenGrantRequest | RoleScreenGrantResponse | v1 |
| API-SEC-017 | /roles/{id}/actions | POST | RoleActionGrantRequest | RoleActionGrantResponse | v1 |
| API-SEC-018 | /registry/modules | POST | ModuleRegistryCreateRequest | ModuleRegistryResponse | v1 |
| API-SEC-019 | /registry/screens | POST | ScreenRegistryCreateRequest | ScreenRegistryResponse | v1 |
| API-SEC-020 | /registry/actions | POST | ActionRegistryCreateRequest | ActionRegistryResponse | v1 |
| API-SEC-021 | /registry/search | POST | RegistrySearchRequest | paginated list of RegistryRowResponse | v1 |
| API-SEC-022 | /dashboard | GET | — | DashboardResponse | v1 |
| API-SEC-023 | /audit-log/search | POST | AuditLogEntrySearchRequest | paginated list of AuditLogEntryResponse | v1 |
| API-SEC-024 | /audit-log/export | GET | (proposed) query parameters — api-docs declares them but binds no schema | (proposed) CSV stream — api-docs declares no response schema | v1 |
| API-SEC-025 | /sessions/search | POST | ActiveSessionSearchRequest | paginated list of ActiveSessionResponse | v1 |
| API-SEC-026 | /sessions/{id} | DELETE | — | SessionTerminationResponse | v1 |
| API-SEC-027 | /menu | GET | — | array of ModuleMenuResponse | v1 |
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

Envelope: `LocalizedException → {code, messageAr, messageEn}`. Runtime code format: `{MOD}-{http}[-{SLUG}]` (Phase 1 CORE; profile.stack.backend.api.error_code_format).

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
CORE (R1)         ✓ layers declared, domain placement declared (entity methods for single-entity, service for multi-row), error signalling declared (code format `{MOD}-{http}[-{SLUG}]`), type mapping declared (postgresql16 → Java table)
DECISIONS         ✓ ADR-SEC-001 (carried from P2, lookup centralization deferral) and ADR-SEC-002 (this stage, PLATFORM-STD catalog umbrella) both ACCEPTED, non-breaking; no BLOCKED ADR
RESULT            BLOCKED ✗ — 1 findings
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

<<<INPUT: frontend-execution-plan>>>
# FRONTEND EXECUTION PLAN — الأمان / Security (SEC)
══════════════════════════════════════════════════════════════════
Module : SEC   Version : v1   Profile : erp   Track : frontend
Framework : react-ts-vite (profile.stack.frontend.framework) · routing react-router ·
            server-state tanstack-query · forms react-hook-form · validation zod ·
            state useState/useReducer + Context (no global store by default)
Inputs : srs (v1, PRD-approved), prd (v1), api-docs (v1, published by the backend repo),
         registry-srs (v1), registry-exec-be (v1)
Screens : 10 — SCR-SEC-001..010 · UXD : 0 (SEC is ROOT — SRS A8) · API bound : 27 / 27
Open ADRs : 9 — erp/decisions/SEC/ (ADR-SEC-003..011, all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

## API SURFACE — SEC v1   (source: `_inputs/api-docs-sec.md` — the ONLY endpoint source)

```
ENDPOINTS   27 — API-SEC-001..027, bound to the published surface by the API ID BINDING
            annex of the api-docs (ADR-SEC-004). Envelope: every response is wrapped in
            ApiResponse<T> { success, data, error { code, message, fieldErrors[] },
            timestamp }; every collection read returns Page<T> { totalPages, totalElements,
            first, last, numberOfElements, pageable, sort, size, number, empty } — except
            API-SEC-027, which returns a bare array and must not be read as a page.
            Paging constraints (PageableBuilder): default page 0 · default size 20 ·
            maximum size 200.
            Five reads are POST `…/search` with a filters[] body, not GET with query
            params — ADR-SEC-003. Per-endpoint request and response shapes are stated in
            each F2 block below rather than duplicated here.
ERRORS      business codes, each already carrying its ar/en text in the module's catalog:
            SEC-401-INVALID-CREDENTIALS (401) · SEC-403-FORBIDDEN (403) ·
            SEC-404-USER / -ROLE / -MODULE / -SCREEN / -ACTION / -GRANT / -SIGNUP /
            -SESSION (404) · SEC-409-USER-DUP / -ROLE-DUP / -MODULE-DUP / -SCREEN-DUP /
            -ACTION-DUP / -GRANT-DUP / -SIGNUP-DUP (409) · SEC-409-NO-MODULE-GRANT
            [RULE-SEC-001] · SEC-409-NO-SCREEN-GRANT [RULE-SEC-002] · SEC-409-NO-VIEW-GRANT
            [RULE-SEC-007] · SEC-409-SOD-CONFLICT [RULE-SEC-005] ·
            SEC-409-RESET-TOKEN-INVALID [RULE-SEC-006] · SEC-409-MODULE-NOT-REGISTERED
            [RULE-SEC-004] · SEC-409-SCREEN-NOT-REGISTERED · SEC-409-INVALID-TRANSITION ·
            SEC-409-ALREADY-TERMINATED (409) · SEC-400-INVALID-SORT (400)
            framework codes: VALIDATION_ERROR (400) · DATA_INTEGRITY_VIOLATION (409) ·
            ACCESS_DENIED (403) · INTERNAL_ERROR (500)
            Routing is uniform across every F2 block: field validation → inline ·
            business rule → user message · unauthenticated → login · forbidden →
            unauthorized / localized forbidden message · server → generic.
LOOKUPS     USER_STATUS · SIGNUP_STATUS · AUDIT_EVENT_TYPE — owned by SEC (SRS A6), and
            **no endpoint is published for any of them**. One shared hook per key, each
            PENDING ADR-SEC-006; every lookup field stays a string holding the code, and no
            enum is modelled anywhere in this plan.
PERMISSIONS declared by the backend and read from the api-docs, never redeclared here:
            PERM_SEC_USERS_VIEW / _CREATE / _UPDATE · PERM_SEC_ROLES_VIEW / _CREATE /
            _UPDATE · PERM_SEC_MODULE_REGISTRY_VIEW / _UPDATE · PERM_SEC_DASHBOARD_VIEW ·
            PERM_SEC_AUDIT_LOG_VIEW · PERM_SEC_SESSIONS_VIEW / _DELETE ·
            API-SEC-027 requires an authenticated caller only. No endpoint publishes the
            caller's own action-level permissions — ADR-SEC-005.
```

### Reconciliation against the SRS — run once, before any F-content

- **Every REQ that needs an endpoint has one.** REQ-SEC-001..033 map onto API-SEC-001..027
  with no gap; the mapping is the traces of the F2 blocks below.
- **Every documented endpoint maps to a REQ.** All 27 are bound; none is unknown and none is
  used without a REQ behind it.
- **Naming and shape differences** — five reads moved from GET to POST `…/search`
  (ADR-SEC-003), and the audit-entry PK is published as `auditLogPk` where the SRS calls it
  `auditLogEntryPk`. Both continue under an ADR; neither is a missing operation.
- **Operations the SRS names with no published endpoint** — role update, role deactivate,
  individual screen/action grant revoke, registry-row deactivate, read-one-user-by-id and
  logout. None is required by a `REQ-*`, so none is breaking; each is omitted rather than
  faked (ADR-SEC-008).
- **Endpoints published but not called by this frontend** — API-SEC-018, API-SEC-019,
  API-SEC-020, the three registration calls a consuming module makes for itself
  (SRS SCR-REQ-SEC-006 B3). Bound, blocked out in F2 and left uncalled (ADR-SEC-009).
- **One screen's form differs from its SRS Part B input list** — SCR-SEC-004 takes `password`
  on create (B3 omits it; `UserCreateRequest` requires it) and renders `statusCode` read-only
  (B3 lists it as an input; no write DTO accepts it). Both resolve against SRS A3 and A7
  rather than against B3's prose — ADR-SEC-010. The other nine screens match their B3 list.
- **Nothing is invented.** No value absent from the api-docs appears in this plan except as
  an explicit `PENDING ADR-…` marker.

## EXECUTION PLAN INDEX — SEC v1 — frontend-execution-plan-sec.md

| # | Phase | Split | Blocks |
|---|---|---|---|
| 1 | F1 — Models & Types | per screen (10 SCR ≥ 5) | 10 SUB |
| 2 | F2 — Data Hooks | per screen | 10 SUB |
| 3 | F3 — Forms & Validators | per screen | 10 SUB |
| 4 | F4 — Screens & Routes | per screen | 10 SUB |
| 5 | SEC-FE | never split | level-1 only |
| 6 | ALIGN-FE | never split | level-1 only |

**SCREEN REGISTRY**

| SCR | Name (ar / en) | Page code | Container pattern | Owning ENT |
|---|---|---|---|---|
| SCR-SEC-001 | تسجيل الدخول / Login | SEC_LOGIN | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001 المستخدم / User |
| SCR-SEC-002 | التسجيل الذاتي / Sign-up | SEC_SIGNUP | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-013 طلب تسجيل معلّق / SignupRequest |
| SCR-SEC-003 | نسيت / إعادة تعيين كلمة المرور / Forgot / reset password | SEC_PWD_RESET | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-012 رمز إعادة التعيين / PasswordResetToken |
| SCR-SEC-004 | المستخدمون / Users | SEC_USERS | SIDE_DRAWER | ENT-SEC-001 المستخدم / User (+ ENT-SEC-003 |
| SCR-SEC-005 | الأدوار والصلاحيات / Roles & permissions | SEC_ROLES | TREE_MASTER_DETAIL | ENT-SEC-002 الدور / Role (+ ENT-SEC-004..009 as tree nodes and grant rows) |
| SCR-SEC-006 | سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry | SEC_MODULE_REGISTRY | TREE_MASTER_DETAIL | ENT-SEC-004 ModuleRegistry |
| SCR-SEC-007 | لوحة تحكم الأمان / Admin dashboard | SEC_DASHBOARD | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001 |
| SCR-SEC-008 | سجل التدقيق / Audit log | SEC_AUDIT_LOG | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-011 سجل التدقيق / AuditLogEntry |
| SCR-SEC-009 | إدارة الجلسات النشطة / Active sessions management | SEC_SESSIONS | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-010 الجلسة النشطة / ActiveSession |
| SCR-SEC-010 | القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu | (none — global component) | none — global shell component (ADR-SEC-007) | ENT-SEC-004 ModuleRegistry |

Ten screens, so every `sub_bearing` phase splits per screen (threshold: SCR count ≥ 5), and
every SUB id is phase-qualified — `SUB:F1-SCR-SEC-004` and `SUB:F2-SCR-SEC-004` are distinct
blocks for the same screen under different phases.

<!-- PHASE:F1:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 1 — F1 — Models & Types

Per `ENT-*` (from the response DTOs of the api-docs) and per `SCR-*`: the source DTO with
each property's type and read-only / system-only / lookup status, then the screen's search
model, form model and container. Lookup fields are strings holding the code — all LOV values
are runtime-loaded (`profile.conventions.lookups`), and no enum is modelled anywhere below.
Both names are carried per language (ar, en). No internal or tenant identifier is modelled,
and nothing is modelled that the api-docs do not return.

<!-- SUB:F1-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F1 · SCR-SEC-001 — تسجيل الدخول / Login

### F1-MODEL — ENT-SEC-001 — المستخدم / User (credentials projection only)
Source DTO   : `LoginRequest` (request) · `LoginResponse` (response)
  request  : username : string · required · maxLength 100 — the login identity
             password : string · required · maxLength 200 · write-only — never held after submit
  response : accessToken : string · read-only · system-only — the signed token
             tokenType   : string · read-only · system-only
             expiresIn   : number (seconds) · read-only · system-only
Read-only    : every response property — the session is issued, never edited
### F1-SCREEN — SCR-SEC-001
Search model : none — this screen has no list (SRS B2 not applicable)
Form model   : username (required) · password (required, write-only)
               excluded system fields: every other ENT-SEC-001 property — the published
               `LoginRequest` carries two fields and the form models exactly those two
               read-only on edit: not applicable — this form has no edit mode
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Nothing is modelled that the api-docs do not return: `userPk`, `statusCode` and the user's
own profile are absent from `LoginResponse` and are therefore absent from this model. The
caller's identity for the rest of the session comes from the menu (API-SEC-027), not from a
user object this endpoint does not send.

<!-- SUB:F1-SCR-SEC-001:END -->

<!-- SUB:F1-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F1 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F1-MODEL — ENT-SEC-013 — طلب تسجيل معلّق / SignupRequest
Source DTO   : `SignupSubmitRequest` (request) · `SignupRequestResponse` (response)
  request  : email      : string · required · maxLength 255
             fullNameAr : string · required · maxLength 200
             fullNameEn : string · required · maxLength 200
  response : signupRequestPk : number · read-only (PK) · system-only
             email, fullNameAr, fullNameEn : string · read-only on the response
             submittedAt : date-time · read-only · system-only
             statusCode  : string · read-only · lookup — SIGNUP_STATUS code, held as a string
                           (no enum, no union of literals — ADR-SEC-006)
             reviewedBy  : string · read-only · system-only
             reviewedAt  : date-time · read-only · system-only
Read-only    : PK, submittedAt, statusCode, reviewedBy, reviewedAt — never form input
### F1-SCREEN — SCR-SEC-002
Search model : none — public single-purpose form
Form model   : email, fullNameAr, fullNameEn (all required)
               excluded system fields: signupRequestPk, submittedAt, statusCode, reviewedBy,
               reviewedAt
               read-only on edit: not applicable — the request is submitted once, never edited
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Both name properties are modelled separately per language (ar, en) as the DTO declares them;
neither is derived from the other.

<!-- SUB:F1-SCR-SEC-002:END -->

<!-- SUB:F1-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F1 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F1-MODEL — ENT-SEC-012 — رمز إعادة تعيين كلمة المرور / PasswordResetToken
Source DTO   : `PasswordResetRequest` · `PasswordResetCompleteRequest` · `ConfirmationResponse`
  step 1 request : email : string · required · maxLength 255
  step 2 request : token       : string · required · maxLength 200 · write-only
                   newPassword : string · required · maxLength 200 · write-only
  response       : messageAr : string · read-only — the confirmation text, Arabic
                   messageEn : string · read-only — the confirmation text, English
Read-only    : both message properties; `tokenHash`, `requestedAt`, `expiresAt` and `usedAt`
               are never returned by any published endpoint and are therefore not modelled
### F1-SCREEN — SCR-SEC-003
Search model : none
Form model   : step 1 — email (required)
               step 2 — token (required; pre-filled from the route when the link carries it),
                        newPassword (required), confirmPassword (required, client-side only —
                        it is a confirmation of the field above and is never sent)
               excluded system fields: every ENT-SEC-012 property above
               read-only on edit: not applicable
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007); the wizard step is a route param
The response carries the localized text itself, so the screen renders `messageAr`/`messageEn`
by the active locale rather than composing a message of its own.

<!-- SUB:F1-SCR-SEC-003:END -->

<!-- SUB:F1-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F1 · SCR-SEC-004 — المستخدمون / Users

### F1-MODEL — ENT-SEC-001 — المستخدم / User
Source DTO   : `UserResponse` (read) · `UserCreateRequest` · `UserUpdateRequest` (write)
  userPk     : number · read-only (PK) · system-only
  username   : string · maxLength 100 — required on create, **read-only on edit**
               (`UserUpdateRequest` does not carry it — the identity is immutable after create)
  email      : string · required · maxLength 255
  fullNameAr : string · required · maxLength 200
  fullNameEn : string · required · maxLength 200
  password   : string · required on create only · maxLength 200 · write-only — never returned
  statusCode : string · read-only · lookup — USER_STATUS code held as a string (ADR-SEC-006);
               changed only by API-SEC-009 / API-SEC-010 / API-SEC-011, never by a form
  lastLoginAt: date-time · read-only · system-only
  isActiveFl : boolean · read-only — mirrors statusCode
  roles      : RoleSummaryResponse[] · read-only on this DTO — { roleId, code, nameAr, nameEn };
               written only through API-SEC-008
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — ENT-SEC-013 — طلب تسجيل معلّق / SignupRequest (pending sub-view)
Source DTO   : `SignupRequestResponse` — every property read-only here; the only input is the
               decision value APPROVE | REJECT of `SignupDecisionRequest` (pattern-constrained)
### F1-SCREEN — SCR-SEC-004
Search model : filters — username/email : string · LIKE · fullName : string · LIKE ·
               statusCode : string · EXACT (the code, from the shared lookup hook — ADR-SEC-006)
               paging + sort — page, size, sortField, sortDirection, carried inside the filter
               object per `UserSearchRequest`
Form model   : create — username, email, fullNameAr, fullNameEn, password (all required)
               edit   — email, fullNameAr, fullNameEn (required); username read-only
               excluded system fields: userPk, statusCode, lastLoginAt, isActiveFl, roles,
               audit fields
               roles are a separate model written through API-SEC-008, not a property of the
               create or update body
Container    : SIDE_DRAWER
No internal or tenant identifier is modelled; `passwordHash` is never returned by any
published endpoint and is absent here, as SRS A3 requires [POL-SEC-004].

<!-- SUB:F1-SCR-SEC-004:END -->

<!-- SUB:F1-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F1 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F1-MODEL — ENT-SEC-002 — الدور / Role
Source DTO   : `RoleResponse` (read) · `RoleCreateRequest` (write)
  rolePk        : number · read-only (PK) · system-only
  code          : string · required on create · maxLength 50 — the stable machine reference;
                  read-only once created
  nameAr        : string · required · maxLength 150
  nameEn        : string · required · maxLength 150
  descriptionAr : string · optional · maxLength 500
  descriptionEn : string · optional · maxLength 500
  isActiveFl    : boolean · read-only
  createdBy, createdAt, updatedBy, updatedAt : read-only · system-only (audit)
### F1-MODEL — grant tree nodes (read-only projections of ENT-SEC-004/005/006)
Source DTO   : `RegistryRowResponse` — module { moduleRegPk, code, nameAr, nameEn, isActiveFl,
               screens[] }, screen { screenRegPk, pageCode, moduleId, moduleCode, nameAr,
               nameEn, isActiveFl, actions[] }, action { actionRegPk, permissionCode, screenId,
               pageCode, actionCode, nameAr, nameEn, isActiveFl }
               every property read-only — the tree displays the registry, it does not edit it
### F1-MODEL — grant rows (ENT-SEC-007/008/009)
Source DTO   : `RoleModuleGrantResponse` { roleModuleGrantPk, roleId, moduleId, grantedBy,
               grantedAt } · `RoleScreenGrantResponse` { roleScreenGrantPk, roleId, screenId,
               grantedBy, grantedAt } · `RoleActionGrantResponse` { roleActionGrantPk, roleId,
               actionId, grantedBy, grantedAt } · `ModuleGrantRevokeResponse`
               { revokedScreenGrants, revokedActionGrants }
               every property read-only — a grant is created or revoked by identifier, never
               edited field by field
### F1-SCREEN — SCR-SEC-005
Search model : filters — code/name : string · LIKE (the published `RoleSearchRequest` carries a
               `name` field beside the generic `filters[]`) · isActiveFl : boolean · EXACT
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : create — code, nameAr, nameEn (required); descriptionAr, descriptionEn (optional)
               edit   — not modelled: no role-update endpoint is published (ADR-SEC-008)
               excluded system fields: rolePk, isActiveFl, audit fields
Container    : TREE_MASTER_DETAIL
The tree holds selection state only. Which nodes are granted is derived from the grant rows the
server returns, never from a local mirror that could outlive a revoke.

<!-- SUB:F1-SCR-SEC-005:END -->

<!-- SUB:F1-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F1 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

### F1-MODEL — ENT-SEC-004 / ENT-SEC-005 / ENT-SEC-006 — registry tree
Source DTO   : `RegistryRowResponse` (the nested module → screens → actions shape returned by
               API-SEC-021), plus `ModuleRegistryResponse`, `ScreenRegistryResponse` and
               `ActionRegistryResponse` for the single-row shapes
  module  : moduleRegPk : number · read-only (PK) · code : string · read-only ·
            nameAr, nameEn : string · read-only · isActiveFl : boolean · read-only ·
            screens : ScreenRegistryResponse[] · audit fields read-only
  screen  : screenRegPk : number · read-only (PK) · pageCode : string · read-only ·
            moduleId : number · read-only · moduleCode : string · read-only ·
            nameAr, nameEn : string · read-only · isActiveFl : boolean · read-only ·
            actions : ActionRegistryResponse[] · audit fields read-only
  action  : actionRegPk : number · read-only (PK) ·
            permissionCode : string · read-only · system-only — derived server-side as
            `PERM_<PAGE_CODE>_<ACTION>`, never composed on the client ·
            screenId : number · read-only · pageCode : string · read-only ·
            actionCode : string · read-only · nameAr, nameEn : string · read-only ·
            isActiveFl : boolean · read-only · audit fields read-only
Read-only    : every property of all three levels — this screen writes nothing (SRS B3)
### F1-SCREEN — SCR-SEC-006
Search model : filters — module code : string · LIKE · pageCode : string · EXACT (the published
               `RegistrySearchRequest` carries `pageCode` beside the generic `filters[]`)
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : none — no create, no update and no deactivate affordance is drawn (ADR-SEC-008)
Container    : TREE_MASTER_DETAIL
The three register DTOs (`ModuleRegistryCreateRequest`, `ScreenRegistryCreateRequest`,
`ActionRegistryCreateRequest`) are modelled as read-only reference shapes so a consuming
module's integrator can see what their own onboarding call must send; this frontend never
builds one (ADR-SEC-009).

<!-- SUB:F1-SCR-SEC-006:END -->

<!-- SUB:F1-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F1 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F1-MODEL — dashboard aggregates (no entity is edited)
Source DTO   : `DashboardResponse` — every property read-only, every property optional
  usersOverview : { total, active, disabled, pendingSignups } : number · read-only
  failedLogins24h : { count } : number · read-only — the derived figure SRS A3 documents as
                    computed from the audit log, never a stored column on ENT-SEC-001
  activeSessions : { count } : number · read-only
  recentActivity : AuditLogEntryResponse[] · read-only — { auditLogPk, eventTypeCode,
                   actorUserId, occurredAt, targetRef, detailsAr, detailsEn, ipAddress }
  rolesPermissionsSummary : { roleCount, privilegedRoleCount,
                   usersPerRole : { roleId, code, nameAr, nameEn, userCount }[] } · read-only
  onboardingFunnel : { pendingSignups, stalledCount } : number · read-only
Read-only    : all of the above — the dashboard has no input of any kind (SRS B3)
### F1-SCREEN — SCR-SEC-007
Search model : none — aggregate widgets, not a browsable list (SRS B2)
Form model   : none
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
Every widget property is optional in the published DTO, and that is the permission mechanism:
a widget the caller may not see is absent from the response, so the model treats absence as
"not permitted", never as zero (REQ-SEC-023, ADR-SEC-005). No figure is stored, carried
between visits or recomputed on the client — REQ-SEC-022 requires each one computed live by
the server at the moment of opening.

<!-- SUB:F1-SCR-SEC-007:END -->

<!-- SUB:F1-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F1 · SCR-SEC-008 — سجل التدقيق / Audit log

### F1-MODEL — ENT-SEC-011 — سجل التدقيق / AuditLogEntry
Source DTO   : `AuditLogEntryResponse` — every property read-only (append-only entity)
  auditLogPk     : number · read-only (PK) · system-only
                   (the published property name for the SRS field `auditLogEntryPk`)
  eventTypeCode  : string · read-only · lookup — AUDIT_EVENT_TYPE code held as a string
                   (no enum — ADR-SEC-006)
  actorUserId    : number · read-only · optional — absent for an unauthenticated failed login
  occurredAt     : date-time · read-only · system-only
  targetRef      : string · read-only · optional
  detailsAr      : string · read-only · optional
  detailsEn      : string · read-only · optional
  ipAddress      : string · read-only · optional
Read-only    : every property — no form ever writes this entity [POL-SEC-009]
### F1-SCREEN — SCR-SEC-008
Search model : filters — eventTypeCode : string · EXACT (from the shared lookup hook) ·
               actorUserId : number · EXACT · occurredFrom/occurredTo : date · DATE_RANGE
               paging + sort — page, size, sortField, sortDirection inside the filter object
               export model — the same filter object rendered as the four query parameters
               `eventTypeCode, actorUserId, occurredFrom, occurredTo` that API-SEC-024 accepts
               (one filter object, two shapes — ADR-SEC-003)
Form model   : none — rows are system-appended only (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
This entity carries no `createdBy`/`updatedBy`: it is the audit record, and `actorUserId` +
`occurredAt` serve that purpose (SRS A3 note).

<!-- SUB:F1-SCR-SEC-008:END -->

<!-- SUB:F1-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F1 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F1-MODEL — ENT-SEC-010 — الجلسة النشطة / ActiveSession
Source DTO   : `ActiveSessionResponse` (read) · `SessionTerminationResponse` (terminate result)
  activeSessionPk : number · read-only (PK) · system-only
  userId          : number · read-only
  username        : string · read-only — the owner's login, returned beside the id so the list
                    needs no second call to name the user
  startedAt       : date-time · read-only · system-only
  lastActivityAt  : date-time · read-only · system-only
  ipAddress       : string · read-only · optional
  terminatedAt    : date-time · read-only — returned only by `SessionTerminationResponse`
Read-only    : every property — the only mutation is terminate, by identifier
               `tokenRef` is never returned by any published endpoint and is not modelled; the
               SRS marks it an opaque reference that is never exposed
### F1-SCREEN — SCR-SEC-009
Search model : filters — userId or username : string · LIKE · ipAddress : string · LIKE
               paging + sort — page, size, sortField, sortDirection inside the filter object
Form model   : none — no create and no update (SRS B3)
Container    : FULL_PAGE (no entry sub-view — ADR-SEC-007)
`terminatedAt` / `terminatedBy` are null for every row this screen lists — API-SEC-025 returns
non-terminated sessions only — so neither is modelled as a column.

<!-- SUB:F1-SCR-SEC-009:END -->

<!-- SUB:F1-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F1 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F1-MODEL — effective menu (read-only projection of ENT-SEC-004 / ENT-SEC-005)
Source DTO   : `ModuleMenuResponse[]` — a bare array, **not** a `Page<T>` (this endpoint does
               not page, and the model must not assume the pagination envelope)
  moduleRegPk : number · read-only (PK) · system-only
  code        : string · read-only — the module code
  nameAr      : string · read-only
  nameEn      : string · read-only
  screens     : ScreenMenuResponse[] · read-only —
                { screenRegPk : number, pageCode : string, nameAr : string, nameEn : string }
Read-only    : every property — the menu is derived from the caller's effective grants and is
               never composed, extended or reordered on the client
### F1-SCREEN — SCR-SEC-010
Search model : none
Form model   : none
Container    : none — a global shell component with no route of its own (ADR-SEC-007)
Exactly two tiers are modelled, because the endpoint returns exactly two (REQ-SEC-021). The
`pageCode` set of this response is also the module's screen-level permission model: it is what
every route guard reads (ADR-SEC-005), so it is modelled once here and consumed by F4, never
duplicated as a static route table.

<!-- SUB:F1-SCR-SEC-010:END -->

<!-- PHASE:F1:END -->

<!-- PHASE:F2:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 2 — F2 — Data Hooks

What each screen needs from the API — not hook code. Every read query's cache key carries
**every** filter that changes the response, page and size included; page and page size live
inside the filter object and are never independent state. Every mutation declares its
invalidation. Components use the facade only; the facade uses the declared queries only
(server-state library: `tanstack-query`).

<!-- SUB:F2-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F2 · SCR-SEC-001 — تسجيل الدخول / Login

### F2-QUERY — API-SEC-001            traces=API-SEC-001,REQ-SEC-001,REQ-SEC-002
POST `/api/v1/sec/auth/login` · request `LoginRequest` { username, password } ·
response `LoginResponse` { accessToken, tokenType, expiresIn } · kind **mutation**
Cache key    : none — a mutation holds no cache entry
Errors       : `SEC-401-INVALID-CREDENTIALS` (401) → user message, shown above the form,
               ar: "بيانات الدخول غير صحيحة" · en: "Invalid credentials" (AC-SEC-002) ·
               `VALIDATION_ERROR` (400) → inline, per `error.fieldErrors[].field` ·
               `INTERNAL_ERROR` (500) → generic message
Loading      : LOCAL — the submit affordance is busy; the SRS states nothing about this call
               being slow, so no GLOBAL indicator (a GLOBAL one would need an ADR)
Cache policy : defaults
Invalidation : the entire server-state cache is discarded and API-SEC-027 (menu) is fetched
               fresh on success — a new session must not read another identity's cached data
### F2-SCREEN-INIT — SCR-SEC-001
Permission read : none — this screen is public (SRS Access summary: SEC_LOGIN is public), so
                  no VIEW is read and no guard runs before it
Lookups used    : none
Entity by id    : none — this screen has no edit mode
### F2-FACADE — SCR-SEC-001
Composes     : the API-SEC-001 mutation only
State it owns: the form's submitted/failed state and the last rejection message; no list, no
               selection, no filters
Operations   : signIn(credentials) → on success, store the token through the session
               transport and navigate to the caller's own landing screen resolved from the
               freshly fetched menu; on `SEC-401-INVALID-CREDENTIALS`, stay and show the
               message — never a partial session
The rejected path records a `LOGIN_FAILED` audit entry server-side (REQ-SEC-002); the client
neither writes nor counts it.

<!-- SUB:F2-SCR-SEC-001:END -->

<!-- SUB:F2-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F2 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F2-QUERY — API-SEC-002            traces=API-SEC-002,REQ-SEC-003
POST `/api/v1/sec/auth/signup` · request `SignupSubmitRequest` { email, fullNameAr,
fullNameEn } · response `SignupRequestResponse` · kind **mutation**
Cache key    : none
Errors       : `SEC-409-SIGNUP-DUP` (409) → user message (a request for that email already
               exists) · `VALIDATION_ERROR` (400) → inline per field · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : none for this caller — the submitter is unauthenticated and holds no cached
               list. An administrator's pending-sign-ups list (API-SEC-005 on SCR-SEC-004) is a
               different session and refreshes on its own key.
### F2-SCREEN-INIT — SCR-SEC-002
Permission read : none — public screen (SRS Access summary: SEC_SIGNUP)
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-002
Composes     : the API-SEC-002 mutation only
State it owns: submitted / not submitted, and the returned request's status for the
               confirmation text
Operations   : submitSignup(form) → on success switch to the confirmation state, which states
               that the request is PENDING and that no account exists yet (REQ-SEC-003)

<!-- SUB:F2-SCR-SEC-002:END -->

<!-- SUB:F2-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F2 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F2-QUERY — API-SEC-003            traces=API-SEC-003,REQ-SEC-006,REQ-SEC-029
POST `/api/v1/sec/auth/password-reset/request` · request `PasswordResetRequest` { email } ·
response `ConfirmationResponse` { messageAr, messageEn } · kind **mutation**
Cache key    : none
Errors       : `VALIDATION_ERROR` (400) → inline. There is deliberately no not-found path: the
               endpoint answers identically whether or not the email is registered, and the
               client must not infer one from a timing or a status difference.
Loading      : LOCAL
Cache policy : defaults
Invalidation : none
### F2-QUERY — API-SEC-004            traces=API-SEC-004,REQ-SEC-007,REQ-SEC-008
POST `/api/v1/sec/auth/password-reset/complete` · request `PasswordResetCompleteRequest`
{ token, newPassword } · response `ConfirmationResponse` · kind **mutation**
Cache key    : none
Errors       : `SEC-409-RESET-TOKEN-INVALID` (409) → user message for RULE-SEC-006,
               ar: "رابط إعادة التعيين غير صالح أو منتهي" ·
               en: "This reset link is invalid or has expired" (AC-SEC-008) ·
               `VALIDATION_ERROR` (400) → inline · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : none — the caller is unauthenticated and holds no cached entity
### F2-SCREEN-INIT — SCR-SEC-003
Permission read : none — public screen (SRS Access summary: SEC_PWD_RESET)
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-003
Composes     : the two mutations above
State it owns: the wizard step (mirrored from the route param, not owned independently), the
               confirmation text returned by whichever step ran, and the last rejection
Operations   : requestReset(email) → always ends in the same generic confirmation ·
               completeReset(token, newPassword) → on success route to SCR-SEC-001; on
               `SEC-409-RESET-TOKEN-INVALID` stay on step 2 with the message and change nothing
The optional notification of REQ-SEC-029 is dispatched entirely server-side when a token is
issued; no client call, state or affordance represents it.

<!-- SUB:F2-SCR-SEC-003:END -->

<!-- SUB:F2-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F2 · SCR-SEC-004 — المستخدمون / Users

### F2-QUERY — API-SEC-005            traces=API-SEC-005,REQ-SEC-009
POST `/api/v1/sec/users/search` · request `UserSearchRequest` { filters[], sortField,
sortDirection, page, size, fullName } · response `Page<UserResponse>` · kind **read query**
(a POST that mutates nothing — ADR-SEC-003)
Cache key    : `[users, filters]` where `filters` is the whole request object — username/email,
               fullName, statusCode, sortField, sortDirection **and page, size**. Page and page
               size live inside the filter object; they are never independent state.
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on the sort control · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : this key is refreshed by every mutation below
### F2-QUERY — API-SEC-006            traces=API-SEC-006,REQ-SEC-009
POST `/api/v1/sec/users` · request `UserCreateRequest` { username, email, fullNameAr,
fullNameEn, password } · response `UserResponse` · kind **mutation**
Errors       : `SEC-409-USER-DUP` (409) → user message, routed to the duplicated field
               (username or email) where the response names it · `VALIDATION_ERROR` → inline ·
               `ACCESS_DENIED` → forbidden message
Invalidation : `[users, *]`
### F2-QUERY — API-SEC-007            traces=API-SEC-007,REQ-SEC-009
PUT `/api/v1/sec/users/{id}` · request `UserUpdateRequest` { email, fullNameAr, fullNameEn } ·
response `UserResponse` · kind **mutation**
Errors       : `SEC-404-USER` (404) → user message · `SEC-409-USER-DUP` (409) → inline on email ·
               `VALIDATION_ERROR` → inline · `ACCESS_DENIED` → forbidden message
Invalidation : `[users, *]`
### F2-QUERY — API-SEC-008            traces=API-SEC-008,REQ-SEC-010,REQ-SEC-020
PUT `/api/v1/sec/users/{id}/roles` · request `UserRoleAssignmentRequest` { roleIds[] } ·
response `UserResponse` · kind **mutation**
Errors       : `SEC-409-SOD-CONFLICT` (409) → user message for RULE-SEC-005,
               ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" ·
               en: "This user already holds a conflicting action" (AC-SEC-020) ·
               `SEC-404-ROLE` / `SEC-404-USER` (404) → user message · `ACCESS_DENIED` → forbidden
Invalidation : `[users, *]` and `[roles, *]` (the roles-per-user figure the role summary shows)
### F2-QUERY — API-SEC-009            traces=API-SEC-009,REQ-SEC-011
DELETE `/api/v1/sec/users/{id}` · response `UserStatusResponse` { userPk, statusCode } ·
kind **mutation**
Errors       : `SEC-404-USER` → user message · `SEC-409-INVALID-TRANSITION` (409) → user
               message · `ACCESS_DENIED` → forbidden
Invalidation : `[users, *]` and `[sessions, *]` — deactivation ends that user's live sessions
               server-side (REQ-SEC-011), so SCR-SEC-009's list is stale the moment it succeeds
### F2-QUERY — API-SEC-010            traces=API-SEC-010,REQ-SEC-031
PATCH `/api/v1/sec/users/{id}` · response `UserStatusResponse` · kind **mutation**
Errors       : `SEC-404-USER` · `SEC-409-INVALID-TRANSITION` · `ACCESS_DENIED` — as above
Invalidation : `[users, *]`
### F2-QUERY — API-SEC-011            traces=API-SEC-011,REQ-SEC-004,REQ-SEC-005
PATCH `/api/v1/sec/signup-requests/{id}` · request `SignupDecisionRequest`
{ decision: APPROVE | REJECT } · kind **mutation**
Errors       : `SEC-404-SIGNUP` (404) → user message · `SEC-409-INVALID-TRANSITION` (409) →
               user message (the request is no longer PENDING) · `SEC-409-USER-DUP` (409) →
               user message (approval would duplicate an existing login) ·
               `VALIDATION_ERROR` → inline · `ACCESS_DENIED` → forbidden
Invalidation : `[users, *]` — an approval creates a user (REQ-SEC-004) and both decisions move
               the request out of the pending sub-view's list
### F2-LOOKUP — USER_STATUS
Endpoint `PENDING ADR-SEC-006` · key `USER_STATUS` · options shape { code, labelAr, labelEn } ·
ONE hook per key, shared by the status filter here and by any other screen needing it ·
long-lived cache. Until the lookup endpoint is published the hook resolves labels through the
single seeded resolver of ADR-SEC-006; it never returns a value list a validator could bind to.
### F2-SCREEN-INIT — SCR-SEC-004
Permission read : `SEC_USERS` present in the API-SEC-027 menu response → VIEW (ADR-SEC-005).
                  CREATE / UPDATE are not readable from any published endpoint; their
                  affordances render and the server's 403 is the authority.
Lookups used    : USER_STATUS (filter), SIGNUP_STATUS (pending sub-view display)
Entity by id    : none published — the drawer hydrates from the row already held by the
                  `[users, filters]` query's cache (ADR-SEC-008), so opening an edit performs
                  no second read and an invalidation re-reads through the same key
### F2-FACADE — SCR-SEC-004
Composes     : API-SEC-005 (list) · API-SEC-006, API-SEC-007, API-SEC-008, API-SEC-009,
               API-SEC-010, API-SEC-011 (mutations) · the USER_STATUS and SIGNUP_STATUS hooks
State it owns: the list derived from the query's data (never a copy of it), the selected user
               id (from the route param), the filter object including page and size, the active
               sub-view (list | pending), and a derived loading flag over the calls in flight
Operations   : createUser · updateUser · assignRoles · deactivateUser (usage check first: the
               confirmation names that live sessions will end) · reactivateUser ·
               decideSignup(APPROVE | REJECT)
Components use the facade only; the facade uses the declared queries only.

<!-- SUB:F2-SCR-SEC-004:END -->

<!-- SUB:F2-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F2 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F2-QUERY — API-SEC-012            traces=API-SEC-012,REQ-SEC-012
POST `/api/v1/sec/roles/search` · request `RoleSearchRequest` { filters[], sortField,
sortDirection, page, size, name } · response `Page<RoleResponse>` · kind **read query**
(ADR-SEC-003)
Cache key    : `[roles, filters]` — code/name, isActiveFl, sort **and page, size**, all inside
               the one filter object
Errors       : `ACCESS_DENIED` → forbidden message · `SEC-400-INVALID-SORT` → inline on sort ·
               `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-SEC-013 and by the grant mutations below
### F2-QUERY — API-SEC-013            traces=API-SEC-013,REQ-SEC-012
POST `/api/v1/sec/roles` · request `RoleCreateRequest` { code, nameAr, nameEn, descriptionAr,
descriptionEn } · response `RoleResponse` · kind **mutation**
Errors       : `SEC-409-ROLE-DUP` (409) → inline on `code` · `VALIDATION_ERROR` → inline ·
               `ACCESS_DENIED` → forbidden
Invalidation : `[roles, *]`
### F2-QUERY — API-SEC-014            traces=API-SEC-014,REQ-SEC-012
POST `/api/v1/sec/roles/{id}/modules` · request `RoleModuleGrantRequest` { moduleId } ·
response `RoleModuleGrantResponse` · kind **mutation**
Errors       : `SEC-404-ROLE` / `SEC-404-MODULE` (404) → user message ·
               `SEC-409-GRANT-DUP` (409) → user message · `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]` — a grant changes what some user's menu
               resolves to (REQ-SEC-021)
### F2-QUERY — API-SEC-015            traces=API-SEC-015,REQ-SEC-015
DELETE `/api/v1/sec/roles/{id}/modules/{moduleId}` · response `ModuleGrantRevokeResponse`
{ revokedScreenGrants, revokedActionGrants } · kind **mutation**
Errors       : `SEC-404-GRANT` (404) → user message · `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]` — the cascade (RULE-SEC-003) removes screen
               and action grants the client must not keep showing. The returned counts are
               displayed as the outcome, never used to patch the tree locally.
### F2-QUERY — API-SEC-016            traces=API-SEC-016,REQ-SEC-013
POST `/api/v1/sec/roles/{id}/screens` · request `RoleScreenGrantRequest` { screenId } ·
response `RoleScreenGrantResponse` · kind **mutation**
Errors       : `SEC-409-NO-MODULE-GRANT` (409) → user message for RULE-SEC-001,
               ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" ·
               en: "Cannot grant a screen without first granting its module" (AC-SEC-013) ·
               `SEC-404-SCREEN` (404) → user message · `SEC-409-GRANT-DUP` → user message ·
               `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]`
### F2-QUERY — API-SEC-017            traces=API-SEC-017,REQ-SEC-014,REQ-SEC-020,REQ-SEC-030
POST `/api/v1/sec/roles/{id}/actions` · request `RoleActionGrantRequest` { actionId } ·
response `RoleActionGrantResponse` · kind **mutation**
Errors       : `SEC-409-NO-SCREEN-GRANT` (409) → user message for RULE-SEC-002,
               ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" ·
               en: "Cannot grant an action without first granting its screen" (AC-SEC-014) ·
               `SEC-409-NO-VIEW-GRANT` (409) → user message for RULE-SEC-007,
               ar: "يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة" ·
               en: "The VIEW action must be granted on this screen first" (AC-SEC-030) ·
               `SEC-409-SOD-CONFLICT` (409) → user message for RULE-SEC-005 (AC-SEC-020) ·
               `SEC-404-ACTION` (404) · `SEC-409-GRANT-DUP` (409) → user message ·
               `ACCESS_DENIED` → forbidden
Invalidation : `[role-grants, roleId]` and `[menu]`
### F2-QUERY — API-SEC-021 (grant tree source)   traces=API-SEC-021,REQ-SEC-012
POST `/api/v1/sec/registry/search` · response `Page<RegistryRowResponse>` · kind **read query**
Cache key    : `[registry, filters]` — module code, pageCode, sort **and page, size**, in the
               one filter object: byte-for-byte the key SCR-SEC-006 builds, so the registry is
               fetched once and both screens read one cache entry. A key that differed in page
               or size here would silently double the fetch.
Errors       : `ACCESS_DENIED` → forbidden message · `INTERNAL_ERROR` → generic
Cache policy : defaults; the registry changes only when a module onboards, so this entry is a
               natural candidate for a longer stale window — left at defaults, since deviating
               would need an ADR and nothing in the SRS asks for it
Invalidation : none from this screen — it registers nothing
### F2-SCREEN-INIT — SCR-SEC-005
Permission read : `SEC_ROLES` present in the API-SEC-027 menu response → VIEW (ADR-SEC-005).
                  CREATE / UPDATE affordances render; the server's 403 is the authority.
Lookups used    : none — every node label comes from the registry response itself
Entity by id    : none published; the master row already held by `[roles, filters]` hydrates
                  the detail pane (ADR-SEC-008)
### F2-FACADE — SCR-SEC-005
Composes     : API-SEC-012 (master list) · API-SEC-021 (the grantable tree) · the role-grant
               mutations API-SEC-013, 014, 015, 016, 017
State it owns: the role list derived from the query's data, the selected role id (route param),
               the filter object including page and size, the tree's expansion state, and a
               derived loading flag
Operations   : createRole · grantModule · grantScreen · grantModuleRevoke (usage check first —
               the confirmation names the cascade before it runs) · grantAction
               No role edit, no role deactivate and no individual screen/action revoke: no
               endpoint is published for them (ADR-SEC-008).

<!-- SUB:F2-SCR-SEC-005:END -->

<!-- SUB:F2-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F2 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

### F2-QUERY — API-SEC-021            traces=API-SEC-021,REQ-SEC-016,REQ-SEC-017,REQ-SEC-019
POST `/api/v1/sec/registry/search` · request `RegistrySearchRequest` { filters[], sortField,
sortDirection, page, size, pageCode } · response `Page<RegistryRowResponse>` (module → screens
→ actions, nested) · kind **read query** (ADR-SEC-003)
Cache key    : `[registry, filters]` — module code, pageCode, sort **and page, size**, in the
               one filter object. This is the same key SCR-SEC-005's grant tree reads, so the
               registry is fetched once for both screens.
Errors       : `ACCESS_DENIED` → forbidden message · `SEC-400-INVALID-SORT` → inline on sort ·
               `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : nothing this frontend does invalidates it — registration happens through the
               registering module's own call (ADR-SEC-009), so the tree is refreshed by an
               explicit refresh affordance rather than by a local mutation
### F2-QUERY — API-SEC-018            traces=API-SEC-018,REQ-SEC-016
POST `/api/v1/sec/registry/modules` · request `ModuleRegistryCreateRequest` { code, nameAr,
nameEn } · response `ModuleRegistryResponse` · kind **mutation — not called by this frontend**
Documented, bound and left uncalled (ADR-SEC-009): a module registers itself from its own
onboarding path (SRS SCR-REQ-SEC-006 B3). The block exists so the shape is on record for the
integrator reading this plan, and so a later pass adding an operator-driven registration has
its contract already reconciled. Errors when it is called: `SEC-409-MODULE-DUP` (409),
`VALIDATION_ERROR` (400), `ACCESS_DENIED` (403).
### F2-QUERY — API-SEC-019            traces=API-SEC-019,REQ-SEC-017,REQ-SEC-018
POST `/api/v1/sec/registry/screens` · request `ScreenRegistryCreateRequest` { moduleCode,
pageCode, nameAr, nameEn } · response `ScreenRegistryResponse` · kind **mutation — not called
by this frontend** (ADR-SEC-009). Errors when it is called:
`SEC-409-MODULE-NOT-REGISTERED` (409) — RULE-SEC-004, ar: "الوحدة غير مسجّلة" ·
en: "Module is not registered" (AC-SEC-018) · `SEC-409-SCREEN-DUP` (409) ·
`VALIDATION_ERROR` (400) · `ACCESS_DENIED` (403).
### F2-QUERY — API-SEC-020            traces=API-SEC-020,REQ-SEC-019
POST `/api/v1/sec/registry/actions` · request `ActionRegistryCreateRequest` { pageCode,
actionCode, nameAr, nameEn } · response `ActionRegistryResponse` · kind **mutation — not called
by this frontend** (ADR-SEC-009). The response's `permissionCode` is derived server-side as
`PERM_<PAGE_CODE>_<ACTION>` and is displayed, never composed here. Errors when it is called:
`SEC-409-SCREEN-NOT-REGISTERED` (409) · `SEC-409-ACTION-DUP` (409) · `VALIDATION_ERROR` (400) ·
`ACCESS_DENIED` (403).
### F2-SCREEN-INIT — SCR-SEC-006
Permission read : `SEC_MODULE_REGISTRY` present in the API-SEC-027 menu response → VIEW
                  (ADR-SEC-005). No UPDATE affordance is drawn at all (ADR-SEC-008), so none
                  is read.
Lookups used    : none
Entity by id    : none — the nested search response carries every level the detail pane shows
### F2-FACADE — SCR-SEC-006
Composes     : API-SEC-021 only
State it owns: the tree derived from the query's data, the selected node (route param), the
               filter object including page and size, the expansion state, and a derived
               loading flag
Operations   : none — this screen is read-only (SRS B3, ADR-SEC-008)

<!-- SUB:F2-SCR-SEC-006:END -->

<!-- SUB:F2-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F2 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F2-QUERY — API-SEC-022            traces=API-SEC-022,REQ-SEC-022,REQ-SEC-023
GET `/api/v1/sec/dashboard` · no request body · response `DashboardResponse` ·
kind **read query**
Cache key    : `[dashboard]` — no filter exists, so the key carries none
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message, shown in place of the
               grid · `INTERNAL_ERROR` (500) → generic. A widget the caller may not see is not
               an error: it is simply absent from the response (ADR-SEC-005).
Per-widget permission — **PENDING, one of six widgets documented.** REQ-SEC-023 is delegated
               entirely to the server here, and the api-docs annotate only `recentActivity`
               ("Most recent audit entries, requires SEC_AUDIT_LOG VIEW"). The other five —
               `usersOverview`, `failedLogins24h`, `activeSessions`, `rolesPermissionsSummary`,
               `onboardingFunnel` — are merely optional, as every property of
               `DashboardResponse` is, and optional is not evidence of gating. This plan
               **assumes** the omission is uniform across all six. If it is not, those five
               leak and no client-side check catches it, because none is readable
               (ADR-SEC-005). Resolve by having the backend annotate per-widget permission for
               all six, or state that the omission is uniform; do not add a client-side test.
Loading      : LOCAL, per widget — one slow figure must not hold the page. The SRS does not
               state that this call is slow, so no GLOBAL indicator.
Cache policy : **no caching of the figures across visits** — REQ-SEC-022 requires every figure
               computed from live data at the moment the dashboard is opened, so this entry is
               always considered stale and refetched on mount. This is a deliberate deviation
               from the defaults, required by the requirement itself rather than chosen; it is
               recorded here rather than in an ADR because the requirement states it outright.
Invalidation : not applicable — the screen writes nothing
### F2-SCREEN-INIT — SCR-SEC-007
Permission read : `SEC_DASHBOARD` present in the API-SEC-027 menu response → VIEW. Per-widget
                  permission is not read at all: the server returns only the widgets the caller
                  may see, so presence in the response **is** the permission (REQ-SEC-023,
                  ADR-SEC-005).
Lookups used    : AUDIT_EVENT_TYPE — the recent-activity widget shows event type codes and
                  resolves their labels through the shared hook (ADR-SEC-006)
Entity by id    : none
### F2-FACADE — SCR-SEC-007
Composes     : the API-SEC-022 query and the AUDIT_EVENT_TYPE lookup hook
State it owns: which widgets the response actually carried (the render list), and a derived
               per-widget loading flag; no figure is held beyond the render
Operations   : none — read-only (SRS B3). Each widget's navigation target is a route, not an
               operation: recent activity → SCR-SEC-008, active sessions → SCR-SEC-009,
               onboarding funnel → SCR-SEC-004's pending sub-view.

<!-- SUB:F2-SCR-SEC-007:END -->

<!-- SUB:F2-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F2 · SCR-SEC-008 — سجل التدقيق / Audit log

### F2-QUERY — API-SEC-023            traces=API-SEC-023,REQ-SEC-024,REQ-SEC-025
POST `/api/v1/sec/audit-log/search` · request `AuditLogEntrySearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<AuditLogEntryResponse>` ·
kind **read query** (ADR-SEC-003)
Cache key    : `[audit-log, filters]` — eventTypeCode, actorUserId, the occurredFrom/occurredTo
               range, sort **and page, size**, all inside the one filter object
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on the sort control ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL
Cache policy : defaults — audit entries are append-only, so a returned page never changes
Invalidation : none — this screen writes nothing; new entries arrive through a refetch, not an
               invalidation (REQ-SEC-024 appends server-side, never from here)
### F2-QUERY — API-SEC-024            traces=API-SEC-024,REQ-SEC-026
GET `/api/v1/sec/audit-log/export` · query parameters `eventTypeCode`, `actorUserId`,
`occurredFrom`, `occurredTo` · response CSV · kind **read query (file)**
Cache key    : none — an export is requested, never cached
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `INTERNAL_ERROR` (500) → generic
Loading      : LOCAL — the export affordance is busy while the file is produced
Cache policy : not applicable
Invalidation : none
The export's four parameters are rendered from **the same filter object** the search key holds,
so an export always matches what the screen is showing — and never the current page, since
`page` and `size` are not among the export's parameters (AC-SEC-026, ADR-SEC-003).
### F2-LOOKUP — AUDIT_EVENT_TYPE
Endpoint `PENDING ADR-SEC-006` · key `AUDIT_EVENT_TYPE` · options shape { code, labelAr,
labelEn } · ONE hook per key, shared with SCR-SEC-007's recent-activity widget · long-lived
cache. Labels resolve through the single seeded resolver until the lookup endpoint exists; the
hook exposes no value list a validator could bind to.
### F2-SCREEN-INIT — SCR-SEC-008
Permission read : `SEC_AUDIT_LOG` present in the API-SEC-027 menu response → VIEW. Export
                  shares that same permission (SRS B4), so no second read exists to make.
Lookups used    : AUDIT_EVENT_TYPE (the event-type filter and the result column)
Entity by id    : none — an audit entry is never opened on its own
### F2-FACADE — SCR-SEC-008
Composes     : API-SEC-023 (search) · API-SEC-024 (export) · the AUDIT_EVENT_TYPE hook
State it owns: the entry list derived from the query's data, the filter object including page
               and size (mirrored to the route's search params so the filtered view is
               shareable — ADR-SEC-003), and a derived loading flag
Operations   : exportCurrentFilter() — builds the four query parameters from the same filter
               object the list is reading; there is no create, update or delete

<!-- SUB:F2-SCR-SEC-008:END -->

<!-- SUB:F2-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F2 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F2-QUERY — API-SEC-025            traces=API-SEC-025,REQ-SEC-027
POST `/api/v1/sec/sessions/search` · request `ActiveSessionSearchRequest` { filters[],
sortField, sortDirection, page, size } · response `Page<ActiveSessionResponse>` ·
kind **read query** (ADR-SEC-003)
Cache key    : `[sessions, filters]` — user/username, ipAddress, sort **and page, size**, in
               the one filter object
Errors       : `ACCESS_DENIED` (403) → the localized forbidden message ·
               `SEC-400-INVALID-SORT` (400) → inline on sort · `INTERNAL_ERROR` → generic
Loading      : LOCAL
Cache policy : defaults
Invalidation : refreshed by API-SEC-026 below, and by API-SEC-009 on SCR-SEC-004 — deactivating
               a user ends that user's sessions server-side (REQ-SEC-011)
### F2-QUERY — API-SEC-026            traces=API-SEC-026,REQ-SEC-028
DELETE `/api/v1/sec/sessions/{id}` · response `SessionTerminationResponse` { activeSessionPk,
terminatedAt } · kind **mutation**
Errors       : `SEC-404-SESSION` (404) → user message · `SEC-409-ALREADY-TERMINATED` (409) →
               user message (the session ended between the render and the click; the list is
               refreshed rather than the row patched) · `ACCESS_DENIED` (403) → forbidden message
Invalidation : `[sessions, *]` and `[dashboard]` — the active-sessions figure changes with it
### F2-SCREEN-INIT — SCR-SEC-009
Permission read : `SEC_SESSIONS` present in the API-SEC-027 menu response → VIEW. The DELETE
                  (terminate) permission is not readable from any published endpoint; the
                  affordance renders and the server's 403 is the authority (ADR-SEC-005).
Lookups used    : none
Entity by id    : none — the list row carries `username` beside `userId`, so naming the session
                  owner needs no second call
### F2-FACADE — SCR-SEC-009
Composes     : API-SEC-025 (list) · API-SEC-026 (terminate)
State it owns: the session list derived from the query's data, the filter object including page
               and size, the row awaiting confirmation, and a derived loading flag
Operations   : terminateSession(id) — usage check first: the confirmation names the affected
               user, because the consequence lands on someone working at that moment

<!-- SUB:F2-SCR-SEC-009:END -->

<!-- SUB:F2-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F2 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F2-QUERY — API-SEC-027            traces=API-SEC-027,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033
GET `/api/v1/sec/menu` · no request body · response `array of ModuleMenuResponse` — a bare
array, **not** `Page<T>` · kind **read query**
Cache key    : `[menu]` — the response is per-caller and carries no filter, so the key carries
               none; it is discarded with the rest of the cache when the session changes
Errors       : `ACCESS_DENIED` (403) → the shell stays usable, states that navigation could not
               be loaded, and **no screen becomes reachable as a result** — a failed menu never
               widens access · `INTERNAL_ERROR` (500) → generic, same rule
Loading      : LOCAL — the shell renders before the menu resolves and shows no entry it has not
               received; nothing is guessed from a static route table
Cache policy : long-lived within a session — the effective grants change only when an
               administrator changes them
Invalidation : `[menu]` is invalidated by every grant mutation of SCR-SEC-005 (API-SEC-014,
               015, 016, 017) and refetched fresh after API-SEC-001, so a revoked grant cannot
               outlive its revoke in this client
### F2-SCREEN-INIT — SCR-SEC-010
Permission read : none of its own — the published endpoint requires only an authenticated
                  caller, and this screen is not a securable destination (SRS B4). This query
                  **is** the permission source every other screen's guard reads (ADR-SEC-005).
Lookups used    : none
Entity by id    : none
### F2-FACADE — SCR-SEC-010
Composes     : the API-SEC-027 query only
State it owns: the module → screen tree derived from the query's data and the expanded module;
               it owns no list of its own and composes no entry locally
Operations   : none — read-only and fully derived (SRS B3)
This facade exposes one derived predicate, `holdsScreen(pageCode)`, computed from the response
it already holds. Every route guard in F4 and every RF5 block reads that predicate, so the
screen-level gate has exactly one source and one call site.

<!-- SUB:F2-SCR-SEC-010:END -->

<!-- PHASE:F2:END -->

<!-- PHASE:F3:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 3 — F3 — Forms & Validators

One block per `RULE-*` enforced on a form, plus the field constraints the published DTOs
state. No frontend-only validation the SRS does not state; every message is read from its
catalog code, never hard-coded; the locale resolves session → browser → `ar`; and a caller
without the write permission is answered by the server rather than by a pre-emptively
disabled field (ADR-SEC-005). Schemas are written with `zod` + `react-hook-form`.

<!-- SUB:F3-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F3 · SCR-SEC-001 — تسجيل الدخول / Login

Validation timing for this form: **on submit** (declared once for the whole form). A login
form that validates while the user types leaks nothing useful and only interrupts them.
### F3-FIELD — SCR-SEC-001
username · REQUIRED · LENGTH (maxLength 100, from `LoginRequest`) · when submit
password · REQUIRED · LENGTH (maxLength 200, from `LoginRequest`) · when submit
Validation shape : both fields non-empty and within their published maximum; nothing more.
                   No pattern, no minimum length and no complexity rule is asserted here —
                   the SRS states none for the login form, and inventing one would reject a
                   credential the server would have accepted. Written with `zod` +
                   `react-hook-form`.
No RULE-* is enforced on this form. REQ-SEC-002's rejection is a server decision
(`SEC-401-INVALID-CREDENTIALS`), surfaced as the user message of the F2 block above, with the
catalog's own text and never a message composed on the client.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-001:END -->

<!-- SUB:F3-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F3 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

Validation timing for this form: **on blur for the email, on submit for the rest**.
### F3-FIELD — SCR-SEC-002
email      · REQUIRED · LENGTH (maxLength 255) · PATTERN (a valid email address —
             SRS ENT-SEC-013 states "valid email") · when blur
fullNameAr · REQUIRED · LENGTH (maxLength 200) · when submit
fullNameEn · REQUIRED · LENGTH (maxLength 200) · when submit
Validation shape : three required strings within their published maxima, the first also
                   matching an email shape. Written with `zod` + `react-hook-form`.
No UNIQUE_CHECK runs on this form: the only endpoint that could answer "is this email already
registered" is `API-SEC-005`, which requires `PERM_SEC_USERS_VIEW`, and the submitter here is
unauthenticated. A duplicate is answered by the server as `SEC-409-SIGNUP-DUP` after submit —
the same answer, without exposing the user directory to an anonymous caller.
No RULE-* is enforced on this form.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-002:END -->

<!-- SUB:F3-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F3 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

Validation timing for this form: **on submit**, per step.
### F3-FIELD — SCR-SEC-003 step 1
email · REQUIRED · LENGTH (maxLength 255) · PATTERN (valid email) · when submit
### F3-FIELD — SCR-SEC-003 step 2
token           · REQUIRED · LENGTH (maxLength 200) · when submit
newPassword     · REQUIRED · LENGTH (maxLength 200) · when submit
confirmPassword · REQUIRED · BUSINESS_RULE (equal to newPassword) · when submit — client-side
                  only, never sent; it is the SRS's "confirm password" field (B3)
Validation shape : step 1 one required email; step 2 a required token, a required new password
                   within the published maximum, and an equality check between the two password
                   fields. No password-complexity rule is asserted: the SRS refers to "the
                   platform's password rules" (AC-SEC-007) without stating them, and the server
                   is the only place they exist. Written with `zod` + `react-hook-form`.
### F3-VALIDATION — RULE-SEC-006      traces=REQ-SEC-008,AC-SEC-008
Statement : The system shall reject a password-reset submission whose token is expired or
            already used.
Message   : from the catalog code `SEC-409-RESET-TOKEN-INVALID` —
            ar: "رابط إعادة التعيين غير صالح أو منتهي" ·
            en: "This reset link is invalid or has expired"
Scope     : CREATE (the step-2 submission)
Field     : token · kind BUSINESS_RULE · when submit
Validation shape : **server-side only.** Expiry and single use are properties of a token the
            client cannot inspect — no published endpoint returns a token's `expiresAt` or
            `usedAt`. The form submits and routes the returned catalog code to a user message
            above the fields, leaving every field as the user left it (AC-SEC-008: "changes
            nothing"). The message is read from the catalog, never hard-coded.
Permission-driven behaviour: none — this screen is public.

<!-- SUB:F3-SCR-SEC-003:END -->

<!-- SUB:F3-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F3 · SCR-SEC-004 — المستخدمون / Users

Validation timing for this form: **on blur for the unique fields, on submit for the rest**
(declared once for the whole drawer).
### F3-FIELD — SCR-SEC-004 (create)
username   · REQUIRED · LENGTH (maxLength 100) · UNIQUE_CHECK · when blur
email      · REQUIRED · LENGTH (maxLength 255) · PATTERN (valid email) · UNIQUE_CHECK · when blur
fullNameAr · REQUIRED · LENGTH (maxLength 200) · when submit
fullNameEn · REQUIRED · LENGTH (maxLength 200) · when submit
password   · REQUIRED · LENGTH (maxLength 200) · when submit — create only
### F3-FIELD — SCR-SEC-004 (edit)
username   · read-only — not an input at all; `UserUpdateRequest` does not carry it
email      · REQUIRED · LENGTH · PATTERN · UNIQUE_CHECK (current record excluded) · when blur
fullNameAr, fullNameEn · REQUIRED · LENGTH · when submit
UNIQUE_CHECK : async, on blur, via `API-SEC-005` with an EQUALS filter on the field; the
               current record is excluded on edit by comparing the returned `userPk`. A
               failure of the check never blocks submit on its own — the authority is the
               server's `SEC-409-USER-DUP`, routed inline to the same field.
### F3-VALIDATION — RULE-SEC-005      traces=REQ-SEC-020,AC-SEC-020
Statement : The system shall prevent assigning a user, by any combination of roles, both
            actions of a module-declared conflicting pair.
Message   : from the catalog code `SEC-409-SOD-CONFLICT` —
            ar: "هذا المستخدم يملك إجراءً متعارضًا بالفعل" ·
            en: "This user already holds a conflicting action"
Scope     : CREATE and UPDATE of the role assignment (API-SEC-008)
Field     : roles (the multi-select) · kind BUSINESS_RULE · when submit
Validation shape : **server-side only.** Conflicting pairs are declared by the owning consumer
            module and no published endpoint exposes them, so the client cannot know which
            selection conflicts before it is sent. The returned catalog code routes to a user
            message on the roles field and the selection is left exactly as the administrator
            made it, so the offending choice is visible rather than silently reverted.
Business-code fields: none — no SEC entity carries a platform-numbered business code
(SRS §3.3 NUMBERING test: all "No"), so there is no read-only code display on this form.
LOOKUP_VALID : `statusCode` is never an input on this screen (it is changed by API-SEC-009 /
            010 / 011), so no lookup validator exists to bind — which is also why ADR-SEC-006's
            missing lookup endpoint costs this form nothing.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `ACCESS_DENIED` on submit and
the form shows the localized forbidden message; the fields are not pre-emptively disabled,
because the permission is not readable (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-004:END -->

<!-- SUB:F3-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F3 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

Validation timing for this form: **on blur for the role code, on submit for the rest**.
### F3-FIELD — SCR-SEC-005 (create role)
code          · REQUIRED · LENGTH (maxLength 50) · UNIQUE_CHECK · when blur
nameAr        · REQUIRED · LENGTH (maxLength 150) · when submit
nameEn        · REQUIRED · LENGTH (maxLength 150) · when submit
descriptionAr · optional · LENGTH (maxLength 500) · when submit
descriptionEn · optional · LENGTH (maxLength 500) · when submit
UNIQUE_CHECK  : async, on blur, via `API-SEC-012` with an EQUALS filter on `code`; no edit mode
                exists on this screen, so there is no current record to exclude. The authority
                remains the server's `SEC-409-ROLE-DUP`, routed inline to `code`.
The role code is displayed read-only everywhere after creation — it is the stable machine
reference (SRS ENT-SEC-002) and is never an input a second time.
### F3-VALIDATION — RULE-SEC-001      traces=REQ-SEC-013,AC-SEC-013
Statement : The system shall prevent a screen grant for a role that does not hold the screen's
            module grant.
Message   : from the catalog code `SEC-409-NO-MODULE-GRANT` —
            ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" ·
            en: "Cannot grant a screen without first granting its module"
Scope     : CREATE (a screen grant, API-SEC-016)
Field     : the screen node of the grant tree · kind BUSINESS_RULE · when submit
Validation shape : the tree's own reachability expresses the rule — a screen node is offered
            only beneath a module the role already holds, so the refusal is rare by
            construction. It is never relied on as the enforcement: the server's catalog code
            is routed to a user message beside the node and the tree is re-read, never patched.
### F3-VALIDATION — RULE-SEC-002      traces=REQ-SEC-014,AC-SEC-014
Statement : The system shall prevent an action grant for a role that does not hold the action's
            screen grant.
Message   : from the catalog code `SEC-409-NO-SCREEN-GRANT` —
            ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" ·
            en: "Cannot grant an action without first granting its screen"
Scope     : CREATE (an action grant, API-SEC-017)
Field     : the action node of the grant tree · kind BUSINESS_RULE · when submit
Validation shape : as RULE-SEC-001, one level down — an action node is offered only beneath a
            granted screen; the server's code is the authority.
### F3-VALIDATION — RULE-SEC-007      traces=REQ-SEC-030,AC-SEC-030
Statement : The system shall require a role to hold the VIEW action grant on a screen before
            any other action grant on that screen takes effect for it.
Message   : from the catalog code `SEC-409-NO-VIEW-GRANT` —
            ar: "يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة" ·
            en: "The VIEW action must be granted on this screen first"
Scope     : CREATE (an action grant other than VIEW, API-SEC-017)
Field     : the action node · kind BUSINESS_RULE · when submit
Validation shape : the tree presents VIEW as the first action of every screen and marks the
            others unreachable until it is held; the server's code is the authority.
### F3-VALIDATION — RULE-SEC-003      traces=REQ-SEC-015,AC-SEC-015
Statement : The system shall delete every screen grant and action grant that module covered for
            that role when its module grant is revoked.
Message   : ar: "سيتم سحب كل منح الشاشات والإجراءات ضمن هذه الوحدة لهذا الدور" ·
            en: "Every screen and action grant under this module for this role will be revoked"
            (SRS A5 — this is a confirmation, not a rejection: the rule always succeeds)
Scope     : ALL (the module-revoke step, API-SEC-015)
Field     : the module node · kind BUSINESS_RULE · when submit
Validation shape : a blocking confirmation before the call, carrying the message above; after
            the call the returned `revokedScreenGrants` / `revokedActionGrants` counts are
            shown as the outcome and the tree is re-read from the server.
### F3-VALIDATION — RULE-SEC-005      traces=REQ-SEC-020,AC-SEC-020
Statement : The system shall prevent assigning a user, by any combination of roles, both
            actions of a module-declared conflicting pair.
Message   : from the catalog code `SEC-409-SOD-CONFLICT` — ar / en as on SCR-SEC-004
Scope     : CREATE (an action grant, API-SEC-017)
Field     : the action node · kind BUSINESS_RULE · when submit
Validation shape : server-side only — the conflicting pairs are the owning module's
            declaration and no endpoint publishes them (as on SCR-SEC-004).
LOOKUP_VALID : none — every selectable value on this screen is a registry node the server
            returned, so there is no static list to validate against.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `ACCESS_DENIED` on a grant and
the tree shows the localized forbidden message, unchanged (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-005:END -->

<!-- SUB:F3-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F3 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

This screen has **no form**: every field is read-only, registration happens through the
registering module's own onboarding call, and the one edit the SRS names — deactivating a stale
row — has no published endpoint (ADR-SEC-008, ADR-SEC-009). There is therefore no validation
timing to declare and no field block to write.
### F3-VALIDATION — RULE-SEC-004      traces=REQ-SEC-018,AC-SEC-018
Statement : The system shall reject a screen registration whose module code has no
            ModuleRegistry row.
Message   : from the catalog code `SEC-409-MODULE-NOT-REGISTERED` —
            ar: "الوحدة غير مسجّلة" · en: "Module is not registered"
Scope     : CREATE (a screen registration, API-SEC-019)
Field     : `moduleCode` of `ScreenRegistryCreateRequest` · kind BUSINESS_RULE · when submit
Validation shape : **not enforced on any form in this frontend.** The rule binds
            `API-SEC-019`, which this frontend does not call (ADR-SEC-009); it is recorded here
            so the block that will enforce it — in the registering module's own screen — has a
            reconciled contract to inherit, message and catalog code included. No client-side
            pre-check is written, because a registry lookup before the call would be a second
            source of truth for a rule the server already owns.
Only the search filters accept input, and they are filters rather than a form: `module code`
(LIKE) and `pageCode` (EXACT), both plain strings with no published constraint to assert.
Locale       : session → browser → `ar`.
Permission-driven behaviour: the screen is read-only for every caller, so no permission
changes a field's behaviour here.

<!-- SUB:F3-SCR-SEC-006:END -->

<!-- SUB:F3-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F3 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

This screen has **no form and no input of any kind** (SRS B3: "Read-only; no data entry"),
so it declares no validation timing and carries no field block.
No `RULE-*` is enforced here. The one behavioural requirement that could look like a validation
— REQ-SEC-023, hiding a widget the caller's role does not grant — is not a client-side rule at
all: the server returns only the widgets the caller may see, and the screen renders exactly
what it received (ADR-SEC-005). A client-side permission test would be a second, weaker copy of
a decision the server already made.
Number and date formatting follow the active locale (session → browser → `ar`); no figure is
rounded, aggregated or recomputed on the client, because REQ-SEC-022 requires every figure to
be the server's live computation.
Permission-driven behaviour: none beyond the above — there is no field to make read-only.

<!-- SUB:F3-SCR-SEC-007:END -->

<!-- SUB:F3-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F3 · SCR-SEC-008 — سجل التدقيق / Audit log

This screen has **no entry form**: audit rows are system-appended and never hand-created
(SRS B3). Only the filter set accepts input, and its validation timing is **on change** for the
selects and **on blur** for the date range.
### F3-FIELD — SCR-SEC-008 (filters)
eventTypeCode · optional · LOOKUP_VALID · when change
actorUserId   · optional · when change
occurredFrom / occurredTo · optional · DATE_RANGE (from ≤ to) · when blur
Validation shape : an optional code, an optional actor, and a date range whose start is not
                   after its end — the only constraint asserted, and it is a property of the
                   pair rather than a business rule. Written with `zod` + `react-hook-form`.
LOOKUP_VALID  : the event-type filter's value must be one of the runtime-loaded options of the
                `AUDIT_EVENT_TYPE` hook — **never a static list**. That hook is
                `PENDING ADR-SEC-006`: until the lookup endpoint is published the validator is
                not written at all, because the only list available would be a hardcoded enum,
                which `profile.conventions.lookups` forbids. An unrecognised code is answered
                by the server as an empty result, which is the correct answer to a filter
                matching nothing.
No `RULE-*` is enforced on this screen: REQ-SEC-024's append and the entries' immutability
[POL-SEC-009] are server properties with no client surface.
Locale        : session → browser → `ar`; `detailsAr` / `detailsEn` are rendered by the active
                locale, and the export carries both as the server writes them.
Permission-driven behaviour: a caller without VIEW never reaches this screen (F4 guard); export
shares that same permission, so no affordance on it is separately gated.

<!-- SUB:F3-SCR-SEC-008:END -->

<!-- SUB:F3-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F3 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

This screen has **no entry form** (SRS B3: no create, no update). Only the filter set
accepts input, with timing **on change**.
### F3-FIELD — SCR-SEC-009 (filters)
user / username · optional · LENGTH (no published maximum — none asserted) · when change
ipAddress       · optional · when change
Validation shape : two optional free-text filters; no pattern is asserted on the IP filter,
                   because a partial address is a legitimate LIKE search and a strict pattern
                   would reject it. Written with `zod` + `react-hook-form`.
No `RULE-*` is enforced on this screen. REQ-SEC-028's termination is a server operation whose
only client surface is the confirmation described in F2, and `SEC-409-ALREADY-TERMINATED` is
routed to a user message followed by a re-read of the list — never a local removal of the row.
No LOOKUP_VALID and no UNIQUE_CHECK apply: nothing on this screen is a lookup field and nothing
is created.
Locale        : session → browser → `ar`; `startedAt` and `lastActivityAt` are rendered in the
                tenant timezone by the active locale.
Permission-driven behaviour: a caller without VIEW never reaches this screen (F4 guard); the
terminate affordance renders for anyone who does, and `ACCESS_DENIED` is shown as the localized
forbidden message (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-009:END -->

<!-- SUB:F3-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F3 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

This component has **no form and no input** (SRS B3: "read-only, derived"), so it
declares no validation timing and carries no field block.
No `RULE-*` is enforced here, and none could be: the menu asserts nothing — it renders what the
caller's effective grants already are (REQ-SEC-021) and omits what they are not (REQ-SEC-032).
The one rule that matters at this boundary, REQ-SEC-033, is explicitly **not** a client-side
validation: the server verifies the module grant on every request regardless of what the menu
shows, and this component's absence of an entry is a usability consequence, never the
enforcement (ADR-SEC-005).
Nothing is composed locally: no static route table is merged into the response, no entry is
sorted into existence, and no module the response omitted is added back from a cached earlier
menu. A menu that fails to load renders no entry rather than a remembered one.
Locale       : session → browser → `ar`; `nameAr` / `nameEn` are rendered by the active locale
               at both tiers.
Permission-driven behaviour: the whole component **is** the permission-driven behaviour of this
module's frontend — it is the single source every route guard reads (F4, RF5).

<!-- SUB:F3-SCR-SEC-010:END -->

<!-- PHASE:F3:END -->

<!-- PHASE:F4:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 4 — F4 — Screens & Routes

One block per `SCR-*`: routes, chunk, guard, components, mode, facade, shared UI and
cross-module citations. Routes are named by the container pattern — `SIDE_DRAWER` →
SearchPage + FormDrawer toggled by a route param; `TREE_MASTER_DETAIL` → TreePage with the
tree route registered **before** any `:id` route; `FULL_PAGE` with no entry sub-view → a
single Page and no entry route. One lazy chunk per composite screen: Search and Entry are
separate components under ONE `SCR-*` sharing ONE chunk, never a second chunk for a
sub-view. Every `PERM_*` name below is the backend's, never invented here.

<!-- SUB:F4-SCR-SEC-001:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001 -->
### F4 · SCR-SEC-001 — تسجيل الدخول / Login

### F4-SCREEN — SCR-SEC-001            traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001
Routes       : `/login` — the only route; no `new`, no `:id`, no `:id/edit` (this screen has no
               record to address)
Chunk        : one lazy chunk for this composite screen (`react-router`); the three public
               screens are separate chunks, since a signed-in user loads none of them
Guard        : **none — public.** SRS Access summary marks SEC_LOGIN public, so no
               `PERM_*` gates it. The inverse guard applies instead: a caller who already holds
               a session is sent to their own landing screen rather than shown this form again.
Components   : `LoginPage` (route-level) · `CredentialsForm` (presentational)
Mode         : not applicable — no CREATE / EDIT / VIEW mode exists; there is no route match to
               resolve one from
Facade       : the SCR-SEC-001 facade of F2; the page never calls the mutation directly
Shared UI    : the card shell, text field, password field, primary button and inline message of
               the design system — nothing else is rendered
Cross-module : none — no `UXD-*` is cited, because no field on this screen displays another
               module's data
On success the menu (API-SEC-027) is fetched before navigating, so the landing screen is
resolved from the caller's real grants rather than from a default route that may not be theirs.

<!-- SUB:F4-SCR-SEC-001:END -->

<!-- SUB:F4-SCR-SEC-002:START traces=REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002 -->
### F4 · SCR-SEC-002 — التسجيل الذاتي / Sign-up

### F4-SCREEN — SCR-SEC-002            traces=REQ-SEC-003,AC-SEC-003,API-SEC-002
Routes       : `/sign-up` — the only route
Chunk        : one lazy chunk for this composite screen
Guard        : **none — public** (SRS Access summary: SEC_SIGNUP). A caller holding a session
               is sent to their landing screen instead, as on SCR-SEC-001.
Components   : `SignUpPage` (route-level) · `SignUpForm` · `SignUpSubmittedNotice`
               (presentational)
Mode         : not applicable — CREATE is the screen's only purpose and is not resolved from a
               route match
Facade       : the SCR-SEC-002 facade of F2
Shared UI    : card shell, text fields, primary button, inline field errors, notice block
Cross-module : none
After a successful submission the page renders `SignUpSubmittedNotice` in place of the form, so
a second submission is a deliberate navigation rather than a second click on a cleared form
(REQ-SEC-003 creates a pending request, not an account).

<!-- SUB:F4-SCR-SEC-002:END -->

<!-- SUB:F4-SCR-SEC-003:START traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003 -->
### F4 · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password

### F4-SCREEN — SCR-SEC-003            traces=REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004
Routes       : `/password-reset` (step 1 — request) · `/password-reset/complete` (step 2 —
               token and new password; the emailed link points here and carries the token as a
               search param). The step is addressed by the route, never by local-only state.
Chunk        : **one** lazy chunk for both steps — they are one composite screen under one
               `SCR-*`, and a second chunk for a sub-view would break the composite invariant
Guard        : **none — public** (SRS Access summary: SEC_PWD_RESET)
Components   : `PasswordResetPage` (route-level, hosts both steps) · `ResetRequestForm` ·
               `ResetCompleteForm` · `ResetConfirmationNotice` (presentational)
Mode         : not applicable — the wizard step, not a CREATE/EDIT/VIEW mode, is what the route
               match resolves
Facade       : the SCR-SEC-003 facade of F2
Shared UI    : card shell, text field, password field, primary button, inline errors, notice
Cross-module : none
Arriving at `/password-reset/complete` with a token in the search params opens step 2 directly
with the field pre-filled, so the emailed link is a single click; arriving without one leaves
the token field editable rather than blocking the route.

<!-- SUB:F4-SCR-SEC-003:END -->

<!-- SUB:F4-SCR-SEC-004:START traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004 -->
### F4 · SCR-SEC-004 — المستخدمون / Users

### F4-SCREEN — SCR-SEC-004            traces=REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011
Routes       : base slug `users`, under the flat module segment `/security` — SRS Part B's
               `SEC → Authorization → Users` grouping is not rendered, because the two-tier
               menu of REQ-SEC-021 and `ModuleMenuResponse` cannot carry it (ADR-SEC-011);
               a route segment the menu cannot produce would disagree with the menu —
               `/security/users` (search) ·
               `/security/users/pending` (the pending sign-ups sub-view — a **static** segment,
               registered BEFORE the `:id` routes so it is never matched as an id) ·
               `/security/users/new` (drawer, create) ·
               `/security/users/:id` (drawer, view) ·
               `/security/users/:id/edit` (drawer, edit)
Chunk        : one lazy chunk for this composite screen — search, drawer and pending sub-view
               share it; the drawer is never a second chunk
Guard        : every route element guarded by `PERM_SEC_USERS_VIEW`, evaluated as
               "`SEC_USERS` is present in the menu response" (ADR-SEC-005). CREATE and UPDATE
               are not readable from any published endpoint, so `/new` and `/:id/edit` carry
               the same VIEW guard and the server's 403 is the authority on the write itself.
Components   : `UsersSearchPage` (route-level) · `UserFormDrawer` (route-level, `SIDE_DRAWER`) ·
               `PendingSignupsPage` (route-level) · `UserFilters`, `UserResultTable`,
               `UserRolesSelect`, `SignupDecisionRow` (presentational, no suffix)
Mode         : CREATE | EDIT | VIEW resolved from the route match — `/new` → CREATE,
               `/:id/edit` → EDIT, `/:id` → VIEW — never from a parent prop
Facade       : the SCR-SEC-004 facade of F2; pages never call queries directly
Shared UI    : side drawer, data table, filter bar, text field, select, multi-select,
               confirmation dialog, inline errors, localized message banner
Cross-module : none — no `UXD-*` is cited; every field is SEC's own (ENT-SEC-001/003/013)
The drawer is toggled by the route param, never by local-only state, so an edit is linkable and
the browser's back gesture closes it. Deactivate and reactivate are one affordance whose label
follows the row's status, and its confirmation names the session termination REQ-SEC-011
performs server-side.

<!-- SUB:F4-SCR-SEC-004:END -->

<!-- SUB:F4-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F4 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

### F4-SCREEN — SCR-SEC-005            traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017
Routes       : base slug `roles`, under the module segment —
               `/security/roles` (master list) ·
               `/security/roles/new` (create form — a **static** segment registered BEFORE the
               id routes) ·
               `/security/roles/:roleId` (the role's grant tree — the tree route, registered
               before any deeper id route) ·
               `/security/roles/:roleId/modules/:moduleId` (a module node selected inside the
               tree — the node route param)
Chunk        : one lazy chunk for this composite screen — master list, create form and grant
               tree share it
Guard        : every route element guarded by `PERM_SEC_ROLES_VIEW`, evaluated as `SEC_ROLES`
               present in the menu response (ADR-SEC-005). CREATE and UPDATE render their
               affordances; the server's 403 is the authority.
Components   : `RolesTreePage` (route-level, `TREE_MASTER_DETAIL` — hosts the role master list,
               the grant tree and the permanently visible detail) · `RoleCreatePage`
               (route-level) · `RoleMasterList`, `GrantTree`, `GrantNodeDetail`,
               `ModuleRevokeConfirm` (presentational)
Mode         : CREATE | VIEW resolved from the route match — `/new` → CREATE, `/:roleId` → VIEW
               with the tree editable in place. There is no EDIT mode: no role-update endpoint
               is published (ADR-SEC-008).
Facade       : the SCR-SEC-005 facade of F2
Shared UI    : two-pane tree layout, tree node with a checkbox affordance, data table, filter
               bar, text field, textarea, confirmation dialog, inline errors, message banner
Cross-module : none — the tree's nodes are rows of SEC's own registry entities
               (ENT-SEC-004/005/006), not another module's data, so no `UXD-*` is cited
The tree route is registered before the node route, so a role id is never matched as a module
id. Un-checking a screen or action node is not offered — only the module-level revoke exists
(API-SEC-015, ADR-SEC-008) — and the tree states this where a reader would expect otherwise.

<!-- SUB:F4-SCR-SEC-005:END -->

<!-- SUB:F4-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F4 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

### F4-SCREEN — SCR-SEC-006            traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021
Routes       : base slug `registry`, under the module segment —
               `/security/registry` (the module tree) ·
               `/security/registry/:moduleId` (module node — the tree route, registered BEFORE
               any deeper id route) ·
               `/security/registry/:moduleId/screens/:screenId` (screen node, with its actions
               in the detail pane)
Chunk        : one lazy chunk for this composite screen
Guard        : every route element guarded by `PERM_SEC_MODULE_REGISTRY_VIEW`, evaluated as
               `SEC_MODULE_REGISTRY` present in the menu response (ADR-SEC-005). No UPDATE
               affordance is drawn at all (ADR-SEC-008), so none is guarded.
Components   : `RegistryTreePage` (route-level, `TREE_MASTER_DETAIL`) · `RegistryTree`,
               `RegistryNodeDetail`, `PermissionCodeBadge` (presentational)
Mode         : VIEW only — resolved from the route match; there is no CREATE and no EDIT route,
               because this frontend calls none of the three register endpoints (ADR-SEC-009)
Facade       : the SCR-SEC-006 facade of F2
Shared UI    : two-pane tree layout, tree node, detail panel, filter bar, badge, empty state
Cross-module : none — the rows describe other modules but are owned by SEC (ENT-SEC-004/005/006
               are SHARED with SEC as owner), so no `UXD-*` is cited
Tree routes are registered before the `:id` routes at both levels. `PermissionCodeBadge`
displays the server-derived `permissionCode` verbatim — it is the string a consuming module's
developer checks on their own side, and composing it locally would invent a second derivation
of `PERM_<PAGE_CODE>_<ACTION>`.

<!-- SUB:F4-SCR-SEC-006:END -->

<!-- SUB:F4-SCR-SEC-007:START traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007 -->
### F4 · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard

### F4-SCREEN — SCR-SEC-007            traces=REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022
Routes       : `/security/dashboard` — a single route; no `new`, no `:id`, no `:id/edit`
               (there is no record to address)
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_DASHBOARD_VIEW`, evaluated as `SEC_DASHBOARD` present in
               the menu response (ADR-SEC-005). Per-widget permission is **not** guarded on the
               client: the server returns only the widgets the caller may see (REQ-SEC-023).
Components   : `SecurityDashboardPage` (route-level) · `UsersOverviewWidget`,
               `FailedLoginsWidget`, `ActiveSessionsWidget`, `RecentActivityWidget`,
               `RolesPermissionsWidget`, `OnboardingFunnelWidget` (presentational)
Mode         : VIEW only — read-only screen, no mode to resolve
Facade       : the SCR-SEC-007 facade of F2
Shared UI    : widget card, stat figure, compact table, skeleton, empty state, error state,
               localized message banner
Cross-module : none
Each widget renders only when its property is present in `DashboardResponse`, and each links to
the screen it summarizes — recent activity → `/security/audit-log`, active sessions →
`/security/sessions`, onboarding funnel → `/security/users/pending`. Those links are rendered
whether or not the caller holds the target screen; a caller who does not is stopped by that
screen's own guard rather than by a second, weaker check here.

<!-- SUB:F4-SCR-SEC-007:END -->

<!-- SUB:F4-SCR-SEC-008:START traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008 -->
### F4 · SCR-SEC-008 — سجل التدقيق / Audit log

### F4-SCREEN — SCR-SEC-008            traces=REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024
Routes       : base slug `audit-log`, under the module segment — `/security/audit-log` (search)
               only. No `new`, no `:id`, no `:id/edit`: audit rows are never created and never
               opened alone (SRS B3).
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_AUDIT_LOG_VIEW`, evaluated as `SEC_AUDIT_LOG` present in
               the menu response (ADR-SEC-005). Export shares that permission (SRS B4), so its
               affordance carries no separate guard.
Components   : `AuditLogPage` (route-level) · `AuditFilters`, `AuditResultTable`,
               `ExportButton` (presentational)
Mode         : VIEW only — read-only screen
Facade       : the SCR-SEC-008 facade of F2
Shared UI    : data table, filter bar, select, date-range field, secondary button, skeleton,
               empty state, localized message banner
Cross-module : none
The filter set is mirrored into the route's search params, so a filtered investigation is
shareable by URL even though the search itself is a POST (ADR-SEC-003). Export builds its four
query parameters from that same filter object and deliberately omits `page` and `size`, so it
exports the investigation rather than the visible page (AC-SEC-026).

<!-- SUB:F4-SCR-SEC-008:END -->

<!-- SUB:F4-SCR-SEC-009:START traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009 -->
### F4 · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management

### F4-SCREEN — SCR-SEC-009            traces=REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026
Routes       : base slug `sessions`, under the module segment — `/security/sessions` (search)
               only. No `new` and no `:id/edit`: there is no entry form (SRS B3), and the sole
               mutation is a per-row terminate that needs no route of its own.
Chunk        : one lazy chunk for this composite screen
Guard        : guarded by `PERM_SEC_SESSIONS_VIEW`, evaluated as `SEC_SESSIONS` present in the
               menu response (ADR-SEC-005). `PERM_SEC_SESSIONS_DELETE` is not readable from any
               published endpoint, so the terminate affordance renders and the server's 403 is
               the authority.
Components   : `ActiveSessionsPage` (route-level) · `SessionFilters`, `SessionResultTable`,
               `TerminateSessionConfirm` (presentational)
Mode         : VIEW only — read-only list with one action
Facade       : the SCR-SEC-009 facade of F2
Shared UI    : data table, filter bar, text field, destructive button, confirmation dialog,
               skeleton, empty state, localized message banner
Cross-module : none
Terminating confirms first and names the affected user (AC-SEC-028); on success the row leaves
the list through a re-read rather than a local removal, because the screen's contract is
"sessions that have not been terminated" and the server decides which those are.

<!-- SUB:F4-SCR-SEC-009:END -->

<!-- SUB:F4-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F4 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

### F4-SCREEN — SCR-SEC-010            traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027
Routes       : **none of its own** — this is the application shell's navigation component,
               rendered inside every authenticated route rather than matched by one. It is not
               a securable destination and has no page code (SRS B4).
Chunk        : none — it belongs to the shell bundle, not to a lazy chunk. A menu loaded lazily
               would leave the shell without navigation on first paint.
Guard        : the component itself requires only an authenticated caller, as its endpoint
               does. It **is** the guard source for every other screen: each route element in
               F4 above tests `holdsScreen(pageCode)` against this component's facade
               (ADR-SEC-005).
Components   : `AppShellNav` (shell-level) · `ModuleMenuGroup`, `ScreenMenuItem`
               (presentational). No "Page" suffix appears here, because none of these is a
               route-level page.
Mode         : not applicable — no route match, so no mode
Facade       : the SCR-SEC-010 facade of F2, which exposes the derived `holdsScreen(pageCode)`
               predicate the guards read
Shared UI    : navigation list, disclosure group, active-item indicator, skeleton, empty state
Cross-module : none — the entries are rows of SEC's own registry entities
A module the response omits is absent from the menu entirely (REQ-SEC-032) and its routes are
refused by their own guards (REQ-SEC-033); neither behaviour is the enforcement, which is the
server's on every request. When the menu fails to load the shell renders no entry and no route
becomes reachable — a failure narrows access, never widens it.

<!-- SUB:F4-SCR-SEC-010:END -->

<!-- PHASE:F4:END -->

<!-- PHASE:SEC-FE:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 5 — SEC-FE

The frontend half of the security model, per `SCR-*`: the navigation guard and the per-action
UI behaviour. Permission names are the backend registry's, read from the api-docs and never
redeclared. Two mechanisms exist in this module and each block states which one gates it:
the **menu gate** (`SEC_<PAGE>` present in the API-SEC-027 response) and the **server's 403**,
surfaced as the localized catalog message — the consequence of no endpoint publishing the
caller's action-level permissions (ADR-SEC-005). Never split — level-1 only.

### SEC-FE · SCR-SEC-001 — تسجيل الدخول / Login
Permissions      : public — no permission gates this screen (SRS Access summary: SEC_LOGIN)
Navigation guard : none. The inverse guard applies: a caller who already holds a session
is routed to their own landing screen rather than shown the form again.
Per action       : no `PERM_*` action exists for this screen. The rejected-credentials path is
a server decision (`SEC-401-INVALID-CREDENTIALS`) shown as the localized catalog message —
identical for a wrong password, an unknown username and a disabled one (AC-SEC-002), so the
screen reveals nothing about which of the three occurred.

### SEC-FE · SCR-SEC-002 — التسجيل الذاتي / Sign-up
Permissions      : public — no permission gates this screen (SRS Access summary: SEC_SIGNUP)
Navigation guard : none, as on SCR-SEC-001.
Per action       : no `PERM_*` action exists. A duplicate request is answered by the server as
`SEC-409-SIGNUP-DUP` after submit rather than by a client pre-check, so an anonymous caller
cannot probe the user directory (see F3).

### SEC-FE · SCR-SEC-003 — نسيت / إعادة تعيين كلمة المرور / Forgot / reset password
Permissions      : public — no permission gates this screen (SRS Access summary: SEC_PWD_RESET)
Navigation guard : none.
Per action       : no `PERM_*` action exists. Step 1 answers identically whether or not the
email is registered, and step 2's `SEC-409-RESET-TOKEN-INVALID` is shown as the localized
catalog message without distinguishing an expired token from an already-used one — both are
"invalid or expired" (AC-SEC-008).

### SEC-FE · SCR-SEC-004 — المستخدمون / Users
Permissions      : `PERM_SEC_USERS_VIEW`, `PERM_SEC_USERS_CREATE`, `PERM_SEC_USERS_UPDATE`
Navigation guard : `SEC_USERS` must be present in the API-SEC-027 menu response; a caller
without it is sent to the unauthorized destination, and every route of this screen — search,
pending, new, `:id`, `:id/edit` — carries the same guard.
Per action       : VIEW → the gate above, exact. CREATE (new user) and UPDATE (edit, assign
roles, activate, deactivate, approve/reject a sign-up) → the affordances render for a caller
who holds the screen, and `ACCESS_DENIED` from the server is shown as the localized forbidden
message (ADR-SEC-005). DELETE → no delete action exists on this screen: deactivation is an
UPDATE (REQ-SEC-011), and the SRS Access summary leaves SEC_USERS' DELETE column empty.
Permission names are the backend registry's, read from the api-docs, never redeclared here.

### SEC-FE · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions
Permissions      : `PERM_SEC_ROLES_VIEW`, `PERM_SEC_ROLES_CREATE`, `PERM_SEC_ROLES_UPDATE`
Navigation guard : `SEC_ROLES` must be present in the menu response; every route of this
screen carries it.
Per action       : VIEW → the gate above. CREATE (new role) and UPDATE (every grant-tree edit,
including the module revoke) → the affordances render and the server's `ACCESS_DENIED` is the
authority. DELETE → the SRS grants SEC_ROLES a DELETE for deactivating a role, but no endpoint
is published for it, so no affordance is drawn and nothing is gated (ADR-SEC-008).
The three grant refusals of this screen — `SEC-409-NO-MODULE-GRANT`, `SEC-409-NO-SCREEN-GRANT`,
`SEC-409-NO-VIEW-GRANT` — are authorization outcomes the administrator is *editing*, not
authorization failures of the administrator: they are shown as their own localized rule
messages beside the node (F3), never as the generic forbidden message.

### SEC-FE · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry
Permissions      : `PERM_SEC_MODULE_REGISTRY_VIEW`, `PERM_SEC_MODULE_REGISTRY_UPDATE`
Navigation guard : `SEC_MODULE_REGISTRY` must be present in the menu response; every
route of this screen carries it.
Per action       : VIEW → the gate above. UPDATE → the SRS grants it for deactivating a stale
row, but no endpoint is published, so no affordance is drawn and nothing is gated
(ADR-SEC-008). CREATE → registration is the registering module's own call, not an affordance of
this screen (ADR-SEC-009). DELETE → no such action on this screen.
The screen is read-only for every caller who reaches it.

### SEC-FE · SCR-SEC-007 — لوحة تحكم الأمان / Admin dashboard
Permissions      : `PERM_SEC_DASHBOARD_VIEW`, plus the VIEW of each summarized screen
Navigation guard : `SEC_DASHBOARD` must be present in the menu response.
Per action       : VIEW → the gate above. There is no CREATE, UPDATE or DELETE on this screen.
Per widget → **not gated on the client at all**: the server returns only the widgets the caller
may see, so a widget's absence from `DashboardResponse` is the permission decision
(REQ-SEC-023, ADR-SEC-005). The screen never tests a widget permission itself, because a
second test would be a weaker copy of the server's.
A widget's link to its source screen is rendered unconditionally; the target screen's own guard
stops a caller who does not hold it.

### SEC-FE · SCR-SEC-008 — سجل التدقيق / Audit log
Permissions      : `PERM_SEC_AUDIT_LOG_VIEW`
Navigation guard : `SEC_AUDIT_LOG` must be present in the menu response.
Per action       : VIEW → the gate above. Export shares the same permission and is not a
separate mutation (SRS B4), so its affordance is not separately gated and `ACCESS_DENIED` on it
would be the same denial as on the list. There is no CREATE, UPDATE or DELETE: audit entries
are append-only and immutable [POL-SEC-009].

### SEC-FE · SCR-SEC-009 — إدارة الجلسات النشطة / Active sessions management
Permissions      : `PERM_SEC_SESSIONS_VIEW`, `PERM_SEC_SESSIONS_DELETE`
Navigation guard : `SEC_SESSIONS` must be present in the menu response.
Per action       : VIEW → the gate above. DELETE (terminate) → the affordance renders for a
caller who holds the screen and `ACCESS_DENIED` is shown as the localized forbidden message
(ADR-SEC-005). There is no CREATE and no UPDATE on this screen.

### SEC-FE · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu
Permissions      : none of its own — the endpoint requires an authenticated caller only
Navigation guard : none — this component is not a destination (SRS B4). It is the guard
**source**: `holdsScreen(pageCode)`, derived from the API-SEC-027 response, is what every route
element above evaluates.
Per action       : no action exists on this component. A module the caller does not hold is
absent from the menu entirely (REQ-SEC-032), and a route reached directly without its grant is
refused by that route's guard here and by the server on every request (REQ-SEC-033) — the
server's check is the enforcement, the menu's omission is not.
A failure to load the menu renders no entry and grants no route; access narrows, never widens.

**Across every screen.** A forbidden response is shown as its localized catalog message, never
as a silent no-op and never as a generic failure. An unauthenticated response returns the
caller to `/login` and discards the server-state cache, so no data of the previous identity
survives into the next. No screen composes a permission name, and no screen holds a local copy
of the caller's grants beyond the menu response the SCR-SEC-010 facade already owns.

<!-- PHASE:SEC-FE:END -->

<!-- PHASE:ALIGN-FE:START traces=REQ-SEC-001,REQ-SEC-002,AC-SEC-001,AC-SEC-002,API-SEC-001,SCR-SEC-001,REQ-SEC-003,AC-SEC-003,API-SEC-002,SCR-SEC-002,REQ-SEC-006,REQ-SEC-007,REQ-SEC-008,REQ-SEC-029,AC-SEC-006,AC-SEC-007,AC-SEC-008,AC-SEC-029,API-SEC-003,API-SEC-004,SCR-SEC-003,REQ-SEC-004,REQ-SEC-005,REQ-SEC-009,REQ-SEC-010,REQ-SEC-011,REQ-SEC-031,AC-SEC-004,AC-SEC-005,AC-SEC-009,AC-SEC-010,AC-SEC-011,AC-SEC-031,API-SEC-005,API-SEC-006,API-SEC-007,API-SEC-008,API-SEC-009,API-SEC-010,API-SEC-011,SCR-SEC-004,REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005,REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006,REQ-SEC-022,REQ-SEC-023,AC-SEC-022,AC-SEC-023,API-SEC-022,SCR-SEC-007,REQ-SEC-024,REQ-SEC-025,REQ-SEC-026,AC-SEC-024,AC-SEC-025,AC-SEC-026,API-SEC-023,API-SEC-024,SCR-SEC-008,REQ-SEC-027,REQ-SEC-028,AC-SEC-027,AC-SEC-028,API-SEC-025,API-SEC-026,SCR-SEC-009,REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
## PHASE 6 — ALIGN-FE

The alignment self-check is this phase's content: see the section of the same name below,
whose verdict row is written by the orchestrator from the analyze report. Never split —
level-1 only.

<!-- PHASE:ALIGN-FE:END -->

---

## Alignment self-check (ALIGN-FE) — SEC v1

```
ALIGN-FE — SEC v1
SCREENS      10 SRS screen entries ↔ 10 SCR (1:1) │ every SCR has a block in F1, F2, F3 and
             F4 (40 SUB blocks) │ composite separation declared on every composite screen │
             container pattern set for all three entry screens (SCR-SEC-004 SIDE_DRAWER,
             SCR-SEC-005 and SCR-SEC-006 TREE_MASTER_DETAIL); the six screens with no entry
             sub-view carry FULL_PAGE and SCR-SEC-010 none, per ADR-SEC-007
API          27 of 27 documented endpoints have an RF2 block │ no endpoint is used that the
             api-docs lack │ every mutation declares its invalidation │ page and size sit
             inside the cache key's filter object on all five paged reads │ three documented
             endpoints (API-SEC-018/019/020) are bound but deliberately uncalled —
             ADR-SEC-009
LOOKUPS      3 keys, 3 shared hooks (USER_STATUS, SIGNUP_STATUS, AUDIT_EVENT_TYPE), each
             PENDING ADR-SEC-006 │ no enum is modelled anywhere │ no lookup validator binds
             a static list — the one LOOKUP_VALID (SCR-SEC-008's event-type filter) is left
             unwritten rather than hardcoded
VALIDATION   7 of 7 RULE-* accounted for: RULE-SEC-001/002/003/005/007 on SCR-SEC-005,
             RULE-SEC-005 also on SCR-SEC-004, RULE-SEC-006 on SCR-SEC-003, RULE-SEC-004
             recorded on SCR-SEC-006 as bound to an endpoint this frontend does not call │
             every message cites its catalog code │ no hard-coded message │ no
             frontend-only rule
ROUTES       every authenticated route guarded; the three public screens are guarded by
             nothing because the SRS marks them public │ tree routes registered before :id
             routes on SCR-SEC-005 and SCR-SEC-006, and the static `pending` / `new`
             segments before :id on SCR-SEC-004 │ pages use the facade, never a query │
             component naming matches the container pattern on every screen
UXD          0 minted and 0 cited — SEC is ROOT (SRS A8: no consumed entity), so no screen
             displays another module's data and no foreign-data field exists to need one
SECURITY     every SCR has an RF5 block in SEC-FE │ every permission name used
             (PERM_SEC_USERS_*, PERM_SEC_ROLES_*, PERM_SEC_MODULE_REGISTRY_*,
             PERM_SEC_DASHBOARD_VIEW, PERM_SEC_AUDIT_LOG_VIEW, PERM_SEC_SESSIONS_*) is one
             the api-docs attribute to a published endpoint
LANGUAGES    every label and every rule message carries ar + en; the audit details and the
             reset confirmations are rendered from the server's own ar/en pair
TRACES       every PHASE and every SUB carries traces= │ every target exists: REQ-SEC-001..
             033, their AC counterparts, API-SEC-001..027 and SCR-SEC-001..010
DECISIONS    ADR-SEC-003 (search shape) · ADR-SEC-004 (API id binding) · ADR-SEC-005
             (no action-level permission endpoint) · ADR-SEC-006 (no lookup endpoint) ·
             ADR-SEC-007 (container pattern for screens with no entry sub-view) ·
             ADR-SEC-008 (operations with no endpoint) · ADR-SEC-009 (documented endpoints
             this frontend does not call) · ADR-SEC-010 (SCR-SEC-004's form vs SRS B3's input
             list) · ADR-SEC-011 (SRS Part B's navigation grouping vs the two-tier menu) —
             all ACCEPTED, all non-breaking
RESULT       PASSED ✓ — 0 findings
```

### Operations coverage

| Operation | API | SCR action | Route | Status |
|---|---|---|---|---|
| login | API-SEC-001 | SCR-SEC-001 sign in | /login | ✓ |
| submit sign-up | API-SEC-002 | SCR-SEC-002 submit | /sign-up | ✓ |
| request password reset | API-SEC-003 | SCR-SEC-003 step 1 | /password-reset | ✓ |
| complete password reset | API-SEC-004 | SCR-SEC-003 step 2 | /password-reset/complete | ✓ |
| search users | API-SEC-005 | SCR-SEC-004 search | /security/users | ✓ |
| create user | API-SEC-006 | SCR-SEC-004 create | /security/users/new | ✓ |
| update user | API-SEC-007 | SCR-SEC-004 edit | /security/users/:id/edit | ✓ |
| assign roles | API-SEC-008 | SCR-SEC-004 assign roles | /security/users/:id/edit | ✓ |
| deactivate user | API-SEC-009 | SCR-SEC-004 deactivate | /security/users | ✓ |
| reactivate user | API-SEC-010 | SCR-SEC-004 reactivate | /security/users | ✓ |
| approve / reject sign-up | API-SEC-011 | SCR-SEC-004 decide | /security/users/pending | ✓ |
| search roles | API-SEC-012 | SCR-SEC-005 search | /security/roles | ✓ |
| create role | API-SEC-013 | SCR-SEC-005 create | /security/roles/new | ✓ |
| grant module | API-SEC-014 | SCR-SEC-005 grant module | /security/roles/:roleId | ✓ |
| revoke module (cascade) | API-SEC-015 | SCR-SEC-005 revoke module | /security/roles/:roleId | ✓ |
| grant screen | API-SEC-016 | SCR-SEC-005 grant screen | /security/roles/:roleId | ✓ |
| grant action | API-SEC-017 | SCR-SEC-005 grant action | /security/roles/:roleId | ✓ |
| register module | API-SEC-018 | — consuming module's own call | — (ADR-SEC-009) | ✗ |
| register screen | API-SEC-019 | — consuming module's own call | — (ADR-SEC-009) | ✗ |
| register action | API-SEC-020 | — consuming module's own call | — (ADR-SEC-009) | ✗ |
| search registry | API-SEC-021 | SCR-SEC-006 search; SCR-SEC-005 grant tree | /security/registry | ✓ |
| dashboard summary | API-SEC-022 | SCR-SEC-007 render | /security/dashboard | ✓ |
| search audit log | API-SEC-023 | SCR-SEC-008 search | /security/audit-log | ✓ |
| export audit log | API-SEC-024 | SCR-SEC-008 export | /security/audit-log | ✓ |
| list active sessions | API-SEC-025 | SCR-SEC-009 search | /security/sessions | ✓ |
| terminate session | API-SEC-026 | SCR-SEC-009 terminate | /security/sessions | ✓ |
| effective menu | API-SEC-027 | SCR-SEC-010 render + every guard | — (shell component) | ✓ |
| update role | — none published | SCR-SEC-005 — not drawn | — (ADR-SEC-008) | ✗ |
| deactivate role | — none published | SCR-SEC-005 — not drawn | — (ADR-SEC-008) | ✗ |
| revoke screen / action grant | — none published | SCR-SEC-005 — not drawn | — (ADR-SEC-008) | ✗ |
| deactivate registry row | — none published | SCR-SEC-006 — not drawn | — (ADR-SEC-008) | ✗ |
| read one user by id | — none published | SCR-SEC-004 — hydrated from cache | — (ADR-SEC-008) | ✗ |
| logout | — none published | — not drawn | — (ADR-SEC-008) | ✗ |

Twenty-four rows carry a route and a ✓; nine carry a ✗ with the ADR that explains it — three
endpoints published for a caller that is not this frontend, and six operations with no
endpoint at all. No row is a ✗ for want of a decision.

## Hand-off

The implementer reads the phases in profile order — F1 models, F2 hooks, F3 forms, F4 screens
and routes, SEC-FE guards — takes design intent from `ui-ux-spec-sec.md`, and takes every
request and response shape from `_inputs/api-docs-sec.md`. No route, component, permission or
field that is not traceable to an F-block above is invented: a gap is an ADR in
`erp/decisions/SEC/`, never an invention. The plan and its registry are split by the toolkit
into `packages/frontend-execution/` and delivered on the frontend delivery branch after the
`gate:pass-2` verdict, then tagged.

══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: registry-srs>>>
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

<<<INPUT: registry-db>>>
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

<<<INPUT: registry-exec-fe>>>
## REGISTRY — P3.2 — SEC v1
══════════════════════════════════════════════════════════════════

ID RANGES
UXD-SEC — none minted (see UXD INDEX) · SCR-SEC-001 .. SCR-SEC-010

SCR ids: SCR-SEC-001, SCR-SEC-002, SCR-SEC-003, SCR-SEC-004, SCR-SEC-005, SCR-SEC-006,
SCR-SEC-007, SCR-SEC-008, SCR-SEC-009, SCR-SEC-010

UXD ids: none — SEC is ROOT (SRS A8: no consumed entity, no external module read), so no
screen owned by this module displays data whose authoritative source is another module.
Last sequence per atom: SCR: 010 · UXD: 000 (sequence not opened)

SCREENS
| SCR | Name (ar / en) | Container pattern | Owning ENT | Permissions |
|---|---|---|---|---|
| SCR-SEC-001 | تسجيل الدخول / Login | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001, ENT-SEC-010 | public (SEC_LOGIN) |
| SCR-SEC-002 | التسجيل الذاتي / Sign-up | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-013 | public (SEC_SIGNUP) |
| SCR-SEC-003 | نسيت / إعادة تعيين كلمة المرور / Forgot / reset password | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-012, ENT-SEC-001 | public (SEC_PWD_RESET) |
| SCR-SEC-004 | المستخدمون / Users | SIDE_DRAWER | ENT-SEC-001 (+ ENT-SEC-003, ENT-SEC-013) | PERM_SEC_USERS_VIEW, PERM_SEC_USERS_CREATE, PERM_SEC_USERS_UPDATE |
| SCR-SEC-005 | الأدوار والصلاحيات / Roles & permissions | TREE_MASTER_DETAIL | ENT-SEC-002 (+ ENT-SEC-004..009) | PERM_SEC_ROLES_VIEW, PERM_SEC_ROLES_CREATE, PERM_SEC_ROLES_UPDATE |
| SCR-SEC-006 | سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry | TREE_MASTER_DETAIL | ENT-SEC-004, ENT-SEC-005, ENT-SEC-006 | PERM_SEC_MODULE_REGISTRY_VIEW, PERM_SEC_MODULE_REGISTRY_UPDATE (no surface — ADR-SEC-008) |
| SCR-SEC-007 | لوحة تحكم الأمان / Admin dashboard | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-001, ENT-SEC-002, ENT-SEC-010, ENT-SEC-011 | PERM_SEC_DASHBOARD_VIEW (+ each widget's source-screen VIEW, server-side) |
| SCR-SEC-008 | سجل التدقيق / Audit log | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-011 | PERM_SEC_AUDIT_LOG_VIEW (export shares it) |
| SCR-SEC-009 | إدارة الجلسات النشطة / Active sessions management | FULL_PAGE (no entry sub-view — ADR-SEC-007) | ENT-SEC-010 | PERM_SEC_SESSIONS_VIEW, PERM_SEC_SESSIONS_DELETE |
| SCR-SEC-010 | القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu | none — global shell component (ADR-SEC-007) | ENT-SEC-004, ENT-SEC-005 | none of its own — authenticated caller (SRS B4) |

UXD INDEX
| UXD | Screen | Field | Owner module · API used |
|---|---|---|---|
| — | — | — | none. SEC consumes no entity owned by another module (SRS A8, registry-srs "Consumed: none"), so no cross-module display dependency exists to mint. The registry rows of ENT-SEC-004/005/006 describe other modules but are owned by SEC, and reading a SEC-owned row is not a foreign-data field. |

API COVERAGE
| Status | Count | API ids |
|---|---|---|
| used by this frontend | 24 | API-SEC-001..017, API-SEC-021..027 |
| documented, deliberately uncalled | 3 | API-SEC-018, API-SEC-019, API-SEC-020 — the registration calls a consuming module makes for itself (SRS SCR-REQ-SEC-006 B3), bound and blocked out in F2 — ADR-SEC-009 |
| used but undocumented | 0 | — no endpoint is called that the api-docs lack |
| documented but unbound | 0 | all 27 registered API-SEC ids are bound by the API ID BINDING annex — ADR-SEC-004 |

Five of the bound reads carry a verb/path shape diff against the SRS B5 and the backend plan
(API-SEC-005, 012, 021, 023, 025 — GET planned, POST `…/search` published): ADR-SEC-003.

OPERATIONS WITHOUT AN ENDPOINT
role update · role deactivate · individual screen/action grant revoke · registry-row
deactivate · read-one-user-by-id · logout — named by SRS Part B or by an audit event type, but
required by no `REQ-*`; omitted from the frontend rather than faked (ADR-SEC-008).

LOOKUPS
| Key | Owner | Hook | Endpoint |
|---|---|---|---|
| USER_STATUS | SEC (SRS A6) | one shared hook | PENDING ADR-SEC-006 |
| SIGNUP_STATUS | SEC (SRS A6) | one shared hook | PENDING ADR-SEC-006 |
| AUDIT_EVENT_TYPE | SEC (SRS A6) | one shared hook | PENDING ADR-SEC-006 |
No lookup endpoint is published for any of the three; every lookup field stays a string holding
the code and no enum is modelled anywhere in the plan.

ALIGN-FE
PASSED ✓ · findings fixed: 0 (the verdict row inside the plan's ALIGN-FE block is written by
the orchestrator from the analyze report)

ADRs
erp/decisions/SEC/ADR-SEC-003.md (ACCEPTED, non-breaking — search endpoint shape) ·
erp/decisions/SEC/ADR-SEC-004.md (ACCEPTED, non-breaking — API id binding annex) ·
erp/decisions/SEC/ADR-SEC-005.md (ACCEPTED, non-breaking — no action-level permission endpoint) ·
erp/decisions/SEC/ADR-SEC-006.md (ACCEPTED, non-breaking — no lookup endpoint) ·
erp/decisions/SEC/ADR-SEC-007.md (ACCEPTED, non-breaking — container pattern for screens with no entry sub-view) ·
erp/decisions/SEC/ADR-SEC-008.md (ACCEPTED, non-breaking — operations with no published endpoint) ·
erp/decisions/SEC/ADR-SEC-009.md (ACCEPTED, non-breaking — documented endpoints this frontend does not call) ·
erp/decisions/SEC/ADR-SEC-010.md (ACCEPTED, non-breaking — SCR-SEC-004's form vs SRS B3's input list) ·
erp/decisions/SEC/ADR-SEC-011.md (ACCEPTED, non-breaking — SRS Part B's navigation grouping vs the two-tier menu)
Carried from earlier stages: ADR-SEC-001 (P2), ADR-SEC-002 (P3.1). No BLOCKED ADR.

TRACEABILITY
REQ covered by ≥1 SCR/F-block: 33/33 — REQ-SEC-001..033 each appear in the `traces=` of at
least one SUB block of every sub-bearing phase that owns its screen.
Orphan REQ: none.
AC covered: 33/33 (each AC accompanies its REQ in the same SUB traces).
SCR covered: 10/10 — every `SCR-*` carries a block in F1, F2, F3 and F4 (40 SUB blocks) and an
RF5 block in SEC-FE.
UXD cited by an F-block: 0 of 0 — none minted, none dangling.

Event
"P3.2 completed: SEC v1 — 10 screens, 0 UXD, 27/27 API bound (24 called), 4 sub-bearing phases
× 10 SUB blocks, ALIGN-FE PASSED, 9 ADRs"
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
