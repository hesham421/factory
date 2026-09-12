# PASS 2 — module FIN v1 — bundled session (1 stages, one commit per stage)

- `P3.2` Frontend — UX Design + Execution Plan — questions forbidden

==============================================================================
# BRIEF — stage `P3.2` (Frontend — UX Design + Execution Plan) · module FIN · v1 · profile `erp`

Lane `analysis` · implementer ['claude:opus'] · effort high · round 1

## Rules that bind this run
- Questions: **forbidden**. A `[QUESTION]` block is refused. Ambiguity → ADR in `erp/decisions/FIN/` (`ADR-{MOD}-{seq:03d}.md`): non-breaking → continue; breaking → status BLOCKED and stop.
- Owns IDs: UXD, SCR — ID grammar `{prefix}-{MOD}-{seq}` (seq width 3); never re-number, never restart a sequence.
- Read only what this brief contains (generated current state); never open version folders yourself.
- Write exactly these files (complete files; in a delta version only what changed, plus `change-manifest.md`):
- `erp/modules/FIN/P3_2/flow-diagram-fin.md`
- `erp/modules/FIN/P3_2/ui-ux-spec-fin.md`
- `erp/modules/FIN/P3_2/frontend-execution-plan-fin.md`
- `erp/modules/FIN/P3_2/registry-exec-fe-fin.md` (registry)
- Respond with one `<<<FILE: <repo-relative path>>>> … <<<END FILE>>>` block per file when running through a command runner; when running as the operator, write the files directly.

## Contracts checked by `gov.py analyze` after this stage
- **C8** real API docs (consumer repo input) → frontend: C8.1 exists {'input': 'api-docs'} [CRITICAL]; C8.2 registry-agree {'artifact': 'api-docs', 'registry': 'registry-exec-be', 'kinds': ['API'], 'direction': 'artifact→registry'} [MAJOR]; C8.3 registry-agree {'artifact': 'api-docs', 'registry': 'registry-exec-be', 'kinds': ['API'], 'direction': 'registry→artifact'} [MAJOR]; C8.4 endpoint-agrees {'artifact': 'backend-execution-plan', 'source': 'api-docs', 'kind': 'API'} [MAJOR]
- **C9** frontend design + execution plan → split / deliver: C9.1 markers {'artifact': 'frontend-execution-plan', 'track': 'frontend', 'plan': 'exec'} [CRITICAL]; C9.2 traces {'from': 'frontend-execution-plan', 'blocks': ['PHASE', 'SUB'], 'min': 1} [MAJOR]; C9.3 traces {'from': 'UXD', 'to': ['REQ', 'AC'], 'min': 1} [MAJOR]; C9.4 traces {'from': 'SCR', 'to': ['REQ', 'UXD'], 'min': 1, 'mode': 'any'} [MAJOR]; C9.5 traces {'from': 'frontend-execution-plan', 'to': ['API'], 'defined_in': 'api-docs'} [CRITICAL]; C9.6 orphans {'kind': 'UXD', 'referenced_by': ['frontend-execution-plan'], 'min': 1} [MAJOR]; C9.7 orphans {'kind': 'SCR', 'referenced_by': ['frontend-execution-plan'], 'min': 1} [MAJOR]; C9.8 registry-agree {'artifact': ['ui-ux-spec', 'frontend-execution-plan'], 'registry': 'registry-exec-fe', 'kinds': ['UXD', 'SCR']} [MAJOR]; C9.9 ids-owned {'stage': 'P3.2'} [CRITICAL]; C9.10 no-questions {'stage': 'P3.2'} [CRITICAL]; C9.11 ids-continue {'stage': 'P3.2'} [CRITICAL]; C9.13 xref-surface {'artifact': ['frontend-execution-plan'], 'locator': 'stack.backend.api.base_path', 'kinds': ['API']} [MAJOR]; C9.14 languages {'stage': 'P3.2'} [MAJOR]; C9.12 verdict-agrees {'artifact': ['frontend-execution-plan'], 'spec': 'self_check', 'when': 'profile.self_check'} [CRITICAL]

---
# ENGINE
```
ENGINE        : P3.2 — Frontend — UX Design + Execution Plan
PASS / TRACK  : pass 2 · track frontend · lane analysis · questions forbidden
MODULE        : FIN · v1 · profile erp (ERP Platform)
READS         : srs · prd · api-docs · registry-srs · registry-exec-be
                (_state/ for current state; _inputs/api-docs-fin.md for the real API surface)
PRODUCES      : flow-diagram-fin.md · ui-ux-spec-fin.md · frontend-execution-plan-fin.md · registry-exec-fe-fin.md   — ONE run, ONE input set
OWNS IDS      : UXD, SCR
NEXT          : gate:pass-2   (the orchestrator owns the completion protocol — shared/GOVERNANCE-CORE.md)
BOUNDARY      : analysis-only — design artifacts and specifications, never a build
```

# Frontend — UX Design + Execution Plan — engine reference

## 0. Position and authority

One engine, one run, two internal parts that share the same input set:

- **Part A — UX design** (§2): from the SRS (functional ceiling) and the PRD (priority and
  intent) it produces the flow diagram and the ui-ux-spec, minting `SCR-*` and `UXD-*`.
- **Part B — frontend execution plan** (§3): bound to the **real** API surface in
  `_inputs/api-docs-fin.md` (published by the backend repo after implementation —
  `factory.repos.backend.publishes`), organised by the profile's frontend phases, plus the
  registry.

Authority order: SRS `REQ/AC` are the functional ceiling; the api-docs are the only source
for endpoint shape; the PRD informs sequencing and priority; Part A's spec is strong design
intent for Part B — never a licence to add a field, rule or permission the SRS does not
have. A conflict is a finding (ADR — §7), never a silent resolution. The backend execution
plan's contract summary is **never** read as an API source (it may be opened for `DBF`/catalog
code lookup only).

Questions are `forbidden`. Ambiguity → `factory.yaml → ambiguity` (§7). No human
approval sits inside this engine: the human decision is the `gate:pass-2` gate.

Mockups are a **design artifact** (a per-screen mockup spec, optionally one generated image)
— never an implemented shell, never code, never a gate for anything.

**Delta versions** (v2+) emit only ADDED / MODIFIED / REMOVED blocks +
`change-manifest.md` against `_state/`; `SCR/UXD` sequences continue,
never renumbered. Rules: shared/VERSIONING.md.

## 1. Inputs and entry check

| Input | Read from | Use |
|---|---|---|
| `srs` | `_state/current-srs.md` | REQ/AC (EARS + Given/When/Then), ENT, RULE with messages, screen entries, permission matrix, lookup keys |
| `prd` | `_state/current-prd.md` | US-* priority, intent, navigation expectations |
| `api-docs` | `_inputs/api-docs-fin.md` | real endpoints, DTOs, paging + error envelope, runtime error codes |
| `registry-srs` | `_state/current-registry-srs.md` | ID ranges, screen entries, shared entities |
| `registry-exec-be` | `_state/current-registry-exec-be.md` | API-* ranges, catalog codes, XM status, permission names declared by the backend plan |

Entry: the orchestrator's `fetch-inputs` already refused the pass when
`factory.passes.2.required_inputs` are missing — this engine does not re-gate. It does
run one **reconciliation of api-docs against the SRS** (§3.0) before any F-content.

## 2. Part A — UX design (flow diagram + ui-ux-spec)

### A.0 Role

Translate the approved functional truth into navigation and component **intent**. Never
invent scope, business rules or permissions; never fix an SRS↔PRD contradiction by choosing
an interpretation (§7 decides). Final component names, code and routing are Part B's.

### A.1 Screens — `SCR-*`

Mint one `SCR-*` per screen the SRS declares (`SCR-FIN-{seq}`,
traces → REQ + UXD).
**Composite-screen rule** (`profile.conventions.composite_screen`): Search + Entry (or Master +
Detail, Wizard) are ONE screen with ONE `SCR-*`; the sub-views are UX sub-screens under it.
Each additional independent composite gets its own `SCR-*`.

### A.2 Flow diagram — `flow-diagram-fin.md`

One flow block per navigation path (identified by its starting `SCR-*` + a short name; flows
carry no atom of their own):
```
FLOW — <name>                                   traces=US-FIN-<seq>,REQ-FIN-<seq>,SCR-FIN-<seq>
Screens   : SCR-FIN-<seq> [, SCR-FIN-<seq> …]
Sequence  : <entry> → <screen A> → <screen B> → <exit>
Trigger   : <what gets the user here>
Priority  : <from the PRD, if stated>
```
Every flow cites a `US-*` **and** an `SCR-*`. A flow with no SRS-backed screen is inventing
navigation → ADR, not silently included.

### A.3 UI/UX spec — `ui-ux-spec-fin.md`

One block per `SCR-*`, fields and permissions copied from the SRS (no additions, no omissions):
```
## SCR-FIN-<seq> — <name>                 traces=REQ-FIN-<seq>,AC-FIN-<seq>[,UXD-FIN-<seq>]
UI pattern        : <from the SRS screen entry — do not change>
Container pattern : SIDE_DRAWER | FULL_PAGE | TREE_MASTER_DETAIL   (entry screens only — decided here, §A.4)
Sub-views         : Search · Entry (· Detail · Wizard) under this ONE SCR
Fields shown      : <every SRS field of the owning ENT — label per language (ar/en), read-only flags>
Permissions       : <SRS matrix rows for this screen — reference only> — names follow `PERM_<PAGE_CODE>_<ACTION>`, gateway `VIEW`
Cross-module data : <field → UXD-FIN-<seq> (owner module)> | none
States            : empty · loading · error (generic — catalog codes are Part B's) · offline (if the SRS says so)
Design intent     : <proposal, clearly marked PROPOSAL — never a rule>
Mockup            : <optional — see §A.6>
```

### A.4 Container pattern — decision order (stop at the first match)

1. hierarchical parent–child data (trees) → `TREE_MASTER_DETAIL` (two-pane, tree + permanently visible form);
2. header + repeating line items with a computed total (document-style) → `FULL_PAGE`;
3. otherwise (bounded field count, no repeating rows) → `SIDE_DRAWER`.

A screen that fits none is a signal to re-read the SRS field list, not to invent a fourth
pattern. The choice is authoritative input to Part B's screens/routes role.

### A.5 Cross-module display dependencies — `UXD-*`

`UXD-*` (`UXD-FIN-{seq}`, traces → REQ + AC)
names an application-layer need: a screen owned by **this** module displays data whose
authoritative source is another module's real API. It is minted the moment such a field is
drafted, keyed by the module owning the **screen**, recorded in the spec block and in the
registry. It is not a DB constraint, shares nothing with `XM-*`, and never appears in
backend artifacts.

Lifecycle: minted here → cited (never reassigned) by the F-blocks of Part B → verified at the
`gate:pass-2` gate by `gov.py analyze`: every `UXD-*` must be referenced by an F-block and
every referenced one must exist (unreferenced or dangling = MAJOR).

### A.6 Reconciliation self-check (SRS B1–B4 ↔ draft) — no human gate

Run before Part B, on the whole draft:
```
RECONCILIATION — FIN v1
B1 every US-* used in a flow has an SRS counterpart (REQ/AC/screen)   → none: ADR (no invented screen), flow excluded
B2 no RULE-* contradicts a flow/spec outcome                           → contradiction: both texts verbatim in an ADR (breaking → BLOCKED)
B3 every field/permission on a screen exists in the SRS               → extra: removed; missing: added
B4 every screen entry of the SRS has exactly one SCR-* block          → gap: block added
RESULT  reconciled <n> · reworked <n> (bounded to flagged blocks) · ADRs <list>
```

### A.7 Mockup spec (optional design artifact)

Per screen, a bounded brief: the A.3 block as the sole input, "render exactly these fields,
pattern and states — nothing more, nothing less; anything that seems missing is flagged back,
never added". Output = the spec (+ one generated image if the run produces one), verified
against B1–B4 (every SRS field present, none extra, permission-gated actions represented,
container pattern respected). It is never implemented, never a prerequisite for Part B.

## 3. Part B — frontend execution plan

### 3.0 Binding to the real API surface

Before writing any phase, extract from `_inputs/api-docs-fin.md` and bind:
```
API SURFACE — FIN v1   (source: api-docs-fin.md — the ONLY endpoint source)
ENDPOINTS   API-FIN-<seq> │ verb │ path │ request DTO (fields, types, required) │ response DTO │ paging (Page<T>) │ envelope (ApiResponse<T>)
ERRORS      runtime code (per LocalizedException → {code, messageAr, messageEn}) │ HTTP │ RULE-* │ message per language (ar, en)
LOOKUPS     endpoint per lookup key — rule: all LOV values runtime-loaded from the lookup module; no hardcoded enums in APIs or field specs
PERMISSIONS names the backend registry declares (`PERM_<PAGE_CODE>_<ACTION>`)
```
Reconcile once against the SRS: every REQ that needs an endpoint has one (missing/renamed
→ ADR — naming diffs continue, a missing core operation is breaking); every documented
endpoint maps to a REQ (unknown → ADR, never silently used). A value not in the api-docs is
never invented — mark `PENDING ADR-<id>`.

### 3.1 Markers, thresholds, traces

Grammar: `factory.markers` (schema v2, syntax `html-comment`) —
`<!-- KIND:ID:START [traces=…] -->` … `<!-- KIND:ID:END -->`. Kinds allowed in a `frontend` execution plan:

| Kind | Level | Allowed parents | Notes |
|---|---|---|---|
| `PHASE` | 1 | — (top level) | keys from `profile.tracks.<track>.plans.<plan>.phases` |
| `SUB` | 2 | PHASE | id = `{PHASE-KEY}-{SCR-ID}` — always phase-qualified |

- No atom kind is carried by this track: `API-*` and `XM-*` are backend-owned and only cited.
  The unit of addressing here is the **SUB per screen** in `sub_bearing` phases.
- `traces=` on **every** PHASE and SUB block: the
  `REQ/AC/API/UXD/SCR` IDs the block implements (grammar `{prefix}-{MOD}-{seq}`,
  3-digit seq). A PHASE traces to the union of its SUBs.
- The same screen legitimately appears under several phases; without the `{PHASE-KEY}-`
  prefix the SUB ids would collide — the prefix is mandatory, always.
- First line of a phase = its START marker; last = END. Threshold checked **while** writing.
  Unknown key → the toolkit refuses (`refuse`).
- Headings with the word PHASE use a profile key only; index, ALIGN table (unless a phase),
  registry and hand-off are trailing content after the last END. Protocol: shared/MARKER-PROTOCOL.md.

Phase table for `profile.tracks.frontend.plans.exec` (plan order):

| # | Key | Display | Split rule | Per-screen SUB |
|---|---|---|---|---|
| 1 | `F1` | F1 — Models & Types | SUB when SCR count >= 5 | yes — `SUB:F1-SCR-FIN-<seq>` |
| 2 | `F2` | F2 — Data Hooks | SUB when SCR count >= 5 | yes — `SUB:F2-SCR-FIN-<seq>` |
| 3 | `F3` | F3 — Forms & Validators | SUB when SCR count >= 5 | yes — `SUB:F3-SCR-FIN-<seq>` |
| 4 | `F4` | F4 — Screens & Routes | SUB when SCR count >= 5 | yes — `SUB:F4-SCR-FIN-<seq>` |
| 5 | `SEC-FE` | SEC-FE | never split | no |
| 6 | `ALIGN-FE` | ALIGN-FE | never split | no |


### 3.2 Content roles

The profile names the phases; the engine supplies content **by role**, matched on the words
in the phase display ("Models & Types", "Data Hooks", "Forms & Validators", "Screens & Routes",
security, alignment). A phase matching no role is filled as the profile describes it. Stack
facts come from `profile.stack.frontend`: framework `react-ts-vite`; libraries — routing: `react-router`, server-state: `tanstack-query`, forms: `react-hook-form`, validation: `zod`, state: `useState/useReducer + Context (no global store by default)`; lazy chunk per `composite-screen`.

**RF1 — Models & types.** Per `ENT-*` (from the response DTOs in the api-docs) and per `SCR-*`:
```
### <role>-MODEL — ENT-FIN-<seq> — <name>          (inside SUB:<phase>-SCR-… of the owning screen)
Source DTO   : <api-docs DTO>            fields: <property : type · read-only · system-only · lookup (code string, never enum) · deferred ⏸>
Read-only    : PK, business code, audit fields — never form input
### <role>-SCREEN — SCR-FIN-<seq>
Search model : filters (type, filter kind EXACT|LIKE|DATE_RANGE|SET) · paging + sort params (per Page<T>)
Form model   : fields (required/optional) · excluded system fields · read-only on edit
Container    : <from A.3>
```
Rules: lookup fields are strings holding the code (all LOV values runtime-loaded from the lookup module; no hardcoded enums in APIs or field specs); both names per language (ar, en); no internal/tenant identifiers in any model; nothing modelled that the api-docs do not return.

**RF2 — Data hooks.** Declares WHAT each screen needs from the API — not hook code:
```
### <role>-QUERY — API-FIN-<seq>            traces=API-…,REQ-…
Verb · path (exact from api-docs) · request shape · response shape · kind (read query | mutation)
Cache key    : [resource, filters] — every filter that changes the response is in the key
Errors       : catalog code → routing (field validation → inline · business rule → user message · unauthenticated → login · forbidden → unauthorized · server → generic)
Loading      : NONE | LOCAL | GLOBAL (GLOBAL only when the SRS says the call is slow → ADR)
Cache policy : defaults | <stale/gc values> (deviation → ADR)
Invalidation : keys refreshed on success (mutations MUST declare this)
### <role>-LOOKUP — <lookup key>     endpoint · key · options shape (code + label per language) · ONE hook per key, shared across screens · long-lived cache
### <role>-SCREEN-INIT — SCR-FIN-<seq>   permission read for the screen (VIEW/CREATE/UPDATE/DELETE) · lookups used · entity-by-id when editing
### <role>-FACADE — SCR-FIN-<seq>         composes the queries above · state it owns (list from query data, selection, filters incl. page/size, derived loading) · imperative operations (create/update/deactivate with usage check first)
```
State rule: page and page size live **inside** the filter object that forms the cache key —
never as independent state. Components use the facade only; the facade uses the declared
queries only (server-state library: `tanstack-query`).

**RF3 — Forms & validators.** One block per `RULE-*` enforced on a form:
```
### <role>-VALIDATION — RULE-FIN-<seq>      traces=REQ-…,AC-…
Statement · message per language (from the catalog code, never hard-coded) · scope (CREATE|UPDATE|ALL)
Field · kind (REQUIRED | LENGTH | PATTERN | LOOKUP_VALID | UNIQUE_CHECK | BUSINESS_RULE | DATE_RANGE) · when (change | blur | submit — declared once per form)
Validation shape : <what the schema must express — the implementer writes it with `zod` + `react-hook-form`>
UNIQUE_CHECK     : async, on blur, via API-…; current record excluded on edit
LOOKUP_VALID     : value ∈ runtime-loaded options — never a static list
```
Rules: no frontend-only validation the SRS does not state; business code displayed read-only,
never an input; locale from session → browser → `ar`; permission-driven field
behaviour (no edit permission → read-only form).

**RF4 — Screens & routes.** One block per `SCR-*`:
```
### <role>-SCREEN — SCR-FIN-<seq>            traces=REQ-…,UXD-…,API-…
Routes       : base slug (lower, plural, kebab) · new · :id · :id/edit · [tree — registered BEFORE :id routes]
Chunk        : one lazy chunk per composite-screen (routing: `react-router`)
Guard        : every route element guarded by its permission (`PERM_<PAGE_CODE>_<ACTION>` from the SRS matrix — never invented here)
Components   : route-level pages (suffix "Page") · presentational parts (no suffix) — named by container pattern:
               FULL_PAGE → SearchPage + EntryPage (separate routes)
               SIDE_DRAWER → SearchPage + FormDrawer (drawer toggled by a route param, never local-only state)
               TREE_MASTER_DETAIL → TreePage hosting tree + detail (node route param)
Mode         : CREATE | EDIT | VIEW resolved from the route match, never from a parent prop
Facade       : the RF2 facade of this screen · pages never call queries directly
Shared UI    : only the design-system components this screen renders
Cross-module : UXD-* cited for every foreign-data field (missing → ADR, never minted here)
```
Composite invariant: Search and Entry are always separate components under ONE `SCR-*`, one lazy chunk, linked by route params — never a second chunk for the sub-view.

**RF5 — Security (frontend half).** Per `SCR-*`: navigation guard (no `VIEW` → unauthorized redirect) and UI behaviour per action (no VIEW → its affordance hidden / read-only; no CREATE → its affordance hidden / read-only; no UPDATE → its affordance hidden / read-only; no DELETE → its affordance hidden / read-only); forbidden responses shown as the localized catalog message. Permission names are the backend registry's — never redeclared.

**RF6 — Alignment.** The ALIGN table (§4) as the alignment-role phase content (never
split); trailing content if the profile has no such phase.

### 3.3 Phase-by-phase

#### PHASE 1 — `F1` (F1 — Models & Types)
- `<!-- PHASE:F1:START traces=… -->` … `<!-- PHASE:F1:END -->`; content = the roles whose words appear in "F1 — Models & Types", else as the profile describes.
- Per-screen SUB: `<!-- SUB:F1-SCR-FIN-<seq>:START traces=… -->` for **every** `SCR-*` when the SCR count is >= 5; below that the screens may share the phase body, but the block heading still names the SCR.

#### PHASE 2 — `F2` (F2 — Data Hooks)
- `<!-- PHASE:F2:START traces=… -->` … `<!-- PHASE:F2:END -->`; content = the roles whose words appear in "F2 — Data Hooks", else as the profile describes.
- Per-screen SUB: `<!-- SUB:F2-SCR-FIN-<seq>:START traces=… -->` for **every** `SCR-*` when the SCR count is >= 5; below that the screens may share the phase body, but the block heading still names the SCR.

#### PHASE 3 — `F3` (F3 — Forms & Validators)
- `<!-- PHASE:F3:START traces=… -->` … `<!-- PHASE:F3:END -->`; content = the roles whose words appear in "F3 — Forms & Validators", else as the profile describes.
- Per-screen SUB: `<!-- SUB:F3-SCR-FIN-<seq>:START traces=… -->` for **every** `SCR-*` when the SCR count is >= 5; below that the screens may share the phase body, but the block heading still names the SCR.

#### PHASE 4 — `F4` (F4 — Screens & Routes)
- `<!-- PHASE:F4:START traces=… -->` … `<!-- PHASE:F4:END -->`; content = the roles whose words appear in "F4 — Screens & Routes", else as the profile describes.
- Per-screen SUB: `<!-- SUB:F4-SCR-FIN-<seq>:START traces=… -->` for **every** `SCR-*` when the SCR count is >= 5; below that the screens may share the phase body, but the block heading still names the SCR.

#### PHASE 5 — `SEC-FE` (SEC-FE)
- `<!-- PHASE:SEC-FE:START traces=… -->` … `<!-- PHASE:SEC-FE:END -->`; content = the roles whose words appear in "SEC-FE", else as the profile describes.
- Never split — level-1 only.

#### PHASE 6 — `ALIGN-FE` (ALIGN-FE)
- `<!-- PHASE:ALIGN-FE:START traces=… -->` … `<!-- PHASE:ALIGN-FE:END -->`; content = the roles whose words appear in "ALIGN-FE", else as the profile describes.
- Never split — level-1 only.

### 3.4 Mutual consistency rule

Every `SCR-*` in the ui-ux-spec has an F-block in **each** `sub_bearing` phase
(`F1`, `F2`, `F3`, `F4`) and every F-block names an
`SCR-*` that exists in the spec; every `UXD-*` in the spec is cited by an F-block. `gov.py
analyze` checks this at the gate — a mismatch is MAJOR.

## 4. ALIGN self-check

Against the plan itself, the api-docs and the SRS ceiling (cross-artifact = `gov.py analyze`).

**Every row names the check that backs it, and there are no other rows.** The block used to
assert screen coverage, validation, routing and security in prose no check could falsify, and a
sibling plan shipped four such rows false under a verdict that read `PASSED ✓`. A row
nothing can falsify manufactures confidence and is worse than no row, so every unbacked row was
**deleted** rather than softened — if a dimension matters and no check covers it, the fix is a
clause in `shared/ARTIFACT-CONTRACTS.md`, not a sentence here. Each mark is the analyze report's
result for that check, copied; a clause the report says examined nothing is written
`— examined nothing`, never ✓.

```
ALIGN — FIN v1
row           backing check   assertion
SCREENS       orphans         every SCR is referenced by a plan block
UXD           orphans         every UXD is cited by a plan block — this is where a UX decision closes
TRACES        traces          every PHASE/SUB carries traces=, every UXD traces to its REQ/AC, every SCR to its REQ/UXD
API           traces          every API this plan cites is defined in the fetched api-docs — never in the backend plan's contract draft
FOREIGN       xref-surface    every reference to another module's surface resolves in that module's own artifacts
REGISTRY      registry-agree  every UXD and SCR defined here is in the stage registry, and nothing else is
LANGUAGES     languages       labels and messages in ar + en
MARKERS       markers         the parser reports no structural or semantic error for this track and plan
DECISIONS     refs-exist      every ADR this plan cites exists on disk in erp/decisions/FIN/
COVERAGE      (the report)    the clauses the analyze report lists as having examined nothing — verbatim, or `none`
RESULT    (written by the orchestrator from the analyze report — leave it alone)
```
Operations coverage table (operation │ API │ SCR action │ route │ status) closes the section —
a row with an empty route is a ✗.

## 5. Registry update — `registry-exec-fe-fin.md`

```
REGISTRY — P3.2 — FIN v1
ID RANGES     UXD-FIN-<first>..<last> · SCR-FIN-<first>..<last>
SCREENS       SCR │ name │ container pattern │ owning ENT │ permissions
UXD INDEX     UXD │ screen │ field │ owner module · API used
API COVERAGE  documented endpoints used / unused (with ADR)
ALIGN      verdict as stamped · findings fixed
ADRs          decisions/FIN/ADR-FIN-<seq> … (status)
TRACEABILITY  REQ covered by ≥1 SCR/F-block: <n>/<total> · orphan REQ: <list — a gate blocker>
```

## 6. Structural self-check (toolkit)

```
[ ] every profile key has exactly one PHASE START/END pair, in profile order
[ ] every SUB id is {PHASE-KEY}-SCR-…; the same screen under different phases carries different prefixes
[ ] every PHASE/SUB carries traces=
[ ] no heading repeats; trailing content sits after the last PHASE END
[ ] §3.4 mutual consistency holds
```
Then (non-zero exit is blocking):
```
gov.py split --track frontend --module FIN --version 1 --dry-run
```
`gov.py analyze` runs before `gate:pass-2`; CRITICAL keeps the gate closed.

## 7. Ambiguity rule

`factory.yaml → ambiguity` (shared/GOVERNANCE-CORE.md): non-breaking → ADR
`erp/decisions/FIN/ADR-FIN-{seq:03d}.md` and
**continue**; breaking (contradicts a locked decision or a
REQ, including an SRS↔PRD contradiction) → ADR `BLOCKED`,
**stop**. Use `profile.knowledge.files` and `erp/` steering
for the best-practice choice. No question is raised at this stage.

## 8. Boundaries and hand-off

| Owns (mints) | References (read-only) | Never touches |
|---|---|---|
| `UXD-*`, `SCR-*`; flow diagram; ui-ux-spec; mockup spec; F-blocks; ALIGN; ADRs it raises | `REQ/AC/ENT/RULE` (P1), `API` (P3.1 — shape from the api-docs), catalog codes, permission names, `US` (P0.5) | `DBF/XM` (P2 — backend-only), `QR`, `TC` (test-gen), any code, any build |

Hand-off (the orchestrator prints it): plan + registry split by the toolkit into
`packages/frontend-execution/`, delivered on
`gov/{mod}-v{version}-{track}` after the `gate:pass-2` verdict, then tagged
`{mod}-v{version}`. The implementer reads the plan in profile-phase order, the spec for
intent, the api-docs for shapes, and never invents a route, component, permission or field
not traceable to an F-block (a gap → ADR, not an invention).


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

<<<INPUT: prd>>>
# PRD — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module          : FIN     Version : v1
Source artifacts: platform-summary, module-registry, business-policies
Stories         : 19   Policies covered : 20/20   Deferred : 0
Status          : DRAFT — awaiting prd-approval
══════════════════════════════════════════════════════════════════

## USER STORIES

US-FIN-001
  Title          : شجرة الحسابات / Chart of accounts
  Story          : As a finance administrator, I need a hierarchical chart of accounts where only leaf accounts accept direct posting, so that the account structure enforces its own integrity.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-002, POL-FIN-003
  Source         : general-accounting-system-plan-en.md §4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-002
  Title          : تعريف الأبعاد وقيمها / Define dimensions and their values
  Story          : As a finance administrator, I need to define dimensions and their values as data, so that account combinations can carry any segment (project, department, investor, ...) without code changes.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-011
  Source         : general-accounting-system-plan-en.md §4.2-§4.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-003
  Title          : إعداد محرك القواعد / Configure the rules engine
  Story          : As a finance administrator, I need to map each event type to a set of lines (account derivation, amount source, direction), so that new event types are added as data, never as code.
  Priority       : HIGH — plan names this "the core" (§6.1)
  Success metric : —
  Traces         : POL-FIN-005, POL-FIN-006, POL-FIN-014
  Source         : general-accounting-system-plan-en.md §6
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-004
  Title          : إنشاء قيد من حدث محاسبي / Build an entry from an accounting event
  Story          : As the accounting engine, I need to build a balanced entry from an incoming canonical event using its rule, so that event-sourced postings need no manual entry.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-001, POL-FIN-012, POL-FIN-014, POL-FIN-020
  Source         : general-accounting-system-plan-en.md §7.1
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-005
  Title          : إدخال يدوي / Manual journal entry
  Story          : As an accountant, I need to create a manual journal entry (adjustments, opening entries), so that postings with no source event follow the same validation and posting path.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-001, POL-FIN-018
  Source         : general-accounting-system-plan-en.md §7.2
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-006
  Title          : قوالب متكررة/عكسية / Recurring / reversing templates
  Story          : As an accountant, I need a template that recurs on a schedule or auto-reverses next period, so that I don't rebuild the same accrual entry by hand every period.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-018
  Source         : general-accounting-system-plan-en.md §7.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-007
  Title          : قواعد التوزيع / Allocation rules
  Story          : As an accountant, I need to distribute an accumulated account balance across several accounts or dimensions by data-defined rules, so that periodic allocations don't require manual, error-prone entries.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-006
  Source         : general-accounting-system-plan-en.md §7.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-008
  Title          : عرض قيود اليومية / View journal entries
  Story          : As an accountant, I need to view and search journal entries with their full status detail, so that I can review what has posted without altering it.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-013
  Source         : general-accounting-system-plan-en.md §8.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-009
  Title          : عكس/تصحيح قيد / Reverse / correct an entry
  Story          : As an accountant, I need to reverse a posted entry with one action, so that a mistake is corrected without ever editing or deleting the original.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-007
  Source         : general-accounting-system-plan-en.md §9
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-010
  Title          : إدارة السنوات والفترات المالية / Manage fiscal years and periods
  Story          : As a finance administrator, I need to open, soft-close and hard-close periods and run year-end close, so that the accounting calendar is fully under this module's own control.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-004, POL-FIN-010
  Source         : general-accounting-system-plan-en.md §10
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-011
  Title          : اعتماد إغلاق الفترة / Approve period close
  Story          : As a financial controller (distinct from any entry creator), I need to be the one who approves closing a period, so that the single human control point in the whole posting lifecycle is genuinely independent.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-016, POL-FIN-019
  Source         : general-accounting-system-plan-en.md §8.2, §10.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-012
  Title          : دفتر الحساب / Account ledger
  Story          : As an accountant, I need an account ledger derived live from posted lines, so that I always see a figure that matches reality, never a stale cached one.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-009, POL-FIN-011
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-013
  Title          : ميزان المراجعة / Trial balance
  Story          : As a financial controller, I need a trial balance that always balances by construction, so that I trust it as a control report, not just a listing.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-008, POL-FIN-009
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-014
  Title          : الميزانية العمومية / Balance sheet
  Story          : As a financial controller, I need a balance sheet derived from posted balances with correct opening-balance continuity, so that year-over-year figures are trustworthy.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-002, POL-FIN-010
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-015
  Title          : قائمة الدخل / Income statement
  Story          : As a financial controller, I need an income statement derived from posted balances that opens at zero every new year, so that period results are never contaminated by a prior year.
  Priority       : HIGH
  Success metric : —
  Traces         : POL-FIN-002, POL-FIN-010
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-016
  Title          : تقارير الأبعاد / Dimension reports
  Story          : As a financial controller, I need reports broken down by dimension without duplicating accounts, so that I can analyze results per project/department/investor without a parallel chart of accounts.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-011
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-017
  Title          : تسجيل FIN في وحدة الأمان / Register FIN into the Security module
  Story          : As FIN's own integrator, I need to register FIN's module, screens and actions into the Security module as data, so that FIN owns no security of its own.
  Priority       : HIGH — foundational, blocks every secured screen below
  Success metric : —
  Traces         : POL-FIN-015
  Source         : general-accounting-system-plan-en.md §2.2, §2.4
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-018
  Title          : تسجيل قوائم FIN المرجعية في MDL / Register FIN's lookup types into the Lookup module
  Story          : As FIN's own integrator, I need to register FIN's lookup types (payment methods, event types, account types, period states, journal types, ...) into the Lookup module as data, so that FIN keeps no lookup table of its own.
  Priority       : HIGH — foundational, blocks account/period/entry creation which cite these codes
  Success metric : —
  Traces         : POL-FIN-017
  Source         : general-accounting-system-plan-en.md §5.2, §5.3
  Status         : DRAFT → APPROVED (by the PRD approval gate)

US-FIN-019
  Title          : التتبع النازل من التقرير إلى الحدث / Drill-down from statement to source event
  Story          : As a financial controller, I need to drill down from a financial-statement line through the trial balance and account ledger to the original entry and its source event, so that any figure is explainable to its root cause.
  Priority       : MEDIUM
  Success metric : —
  Traces         : POL-FIN-013
  Source         : general-accounting-system-plan-en.md §11
  Status         : DRAFT → APPROVED (by the PRD approval gate)

## TRACEABILITY — story → policy
| US | Traces (POL) | Source |
|---|---|---|
| US-FIN-001 | POL-FIN-002, POL-FIN-003 | §4 |
| US-FIN-002 | POL-FIN-011 | §4.2-§4.3 |
| US-FIN-003 | POL-FIN-005, POL-FIN-006, POL-FIN-014 | §6 |
| US-FIN-004 | POL-FIN-001, POL-FIN-012, POL-FIN-014, POL-FIN-020 | §7.1 |
| US-FIN-005 | POL-FIN-001, POL-FIN-018 | §7.2 |
| US-FIN-006 | POL-FIN-018 | §7.3 |
| US-FIN-007 | POL-FIN-006 | §7.4 |
| US-FIN-008 | POL-FIN-013 | §8.4 |
| US-FIN-009 | POL-FIN-007 | §9 |
| US-FIN-010 | POL-FIN-004, POL-FIN-010 | §10 |
| US-FIN-011 | POL-FIN-016, POL-FIN-019 | §8.2, §10.3 |
| US-FIN-012 | POL-FIN-009, POL-FIN-011 | §11 |
| US-FIN-013 | POL-FIN-008, POL-FIN-009 | §11 |
| US-FIN-014 | POL-FIN-002, POL-FIN-010 | §11 |
| US-FIN-015 | POL-FIN-002, POL-FIN-010 | §11 |
| US-FIN-016 | POL-FIN-011 | §11 |
| US-FIN-017 | POL-FIN-015 | §2.2, §2.4 |
| US-FIN-018 | POL-FIN-017 | §5.2-§5.3 |
| US-FIN-019 | POL-FIN-013 | §11 |
Every policy POL-FIN-001 … POL-FIN-020 appears in at least one row above.

## RESOLVED DECISIONS (dialogue)
| # | Question | Recommended | Confirmed by user | Sources |
None — general-accounting-system-plan-en.md left no story's scope, priority or role
genuinely ambiguous; no dialogue question was required.

## DEFERRED
| US | Reason | Activation trigger |
None — every capability named in general-accounting-system-plan-en.md's in-scope sections
is represented by a story in this v1 PRD; the explicit exclusions (§15) are recorded as
SCOPE EXCEPTIONS in business-policies-fin.md, not as deferred stories.

## APPROVAL
Approved by : PENDING   Date : PENDING
Once approved, no stage may raise a question; P1 onward self-resolve
per the ambiguity rule (shared/GOVERNANCE-CORE.md).
══════════════════════════════════════════════════════════════════

<<<END INPUT>>>

<<<INPUT: api-docs>>>
<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN API Documentation

_OpenAPI definition_

API version: `v0`

## Servers

- http://localhost:7272


## Common Response Envelope

Schema: `ApiResponse<T>`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| success | boolean | No |  |  |
| data | object | No |  | Endpoint-specific payload — see each endpoint's Response section |
| error | ApiError | No |  | Present only when success=false |
| error.code | string | No |  |  |
| error.message | string | No |  |  |
| error.fieldErrors | array<FieldErrorItem> | No |  |  |
| error.fieldErrors[].field | string | No |  |  |
| error.fieldErrors[].message | string | No |  |  |
| timestamp | string (date-time) | No |  |  |

## Pagination Envelope

Schema: `Page<T>`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| totalPages | integer (int32) | No |  |  |
| totalElements | integer (int64) | No |  |  |
| first | boolean | No |  |  |
| last | boolean | No |  |  |
| numberOfElements | integer (int32) | No |  |  |
| pageable | Pageable | No |  |  |
| sort | Sort | No |  |  |
| size | integer (int32) | No |  |  |
| number | integer (int32) | No |  |  |
| empty | boolean | No |  |  |

## Pagination Constraints

Source: `com/erp/common/search/PageableBuilder.java`

| Constraint | Value |
|---|---|
| Default page | 0 |
| Default size | 20 |
| Maximum size | 200 |

## Known Error Codes

| Code | Value | Source | Status | HTTP Status |
|---|---|---|---|---|
| FIN_409_DIMVALUE_DUP | `FIN-409-DIMVALUE-DUP` | exception/FinErrorCodes.java | ALREADY_EXISTS | 409 CONFLICT |
| FIN_409_RULE_DUP | `FIN-409-RULE-DUP` | exception/FinErrorCodes.java | ALREADY_EXISTS | 409 CONFLICT |
| FIN_409_REMAINDER_COUNT | `FIN-409-REMAINDER-COUNT` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_409_PARENT_NOT_LEAF_ELIGIBLE | `FIN-409-PARENT-NOT-LEAF-ELIGIBLE` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_409_HAS_CHILDREN | `FIN-409-HAS-CHILDREN` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_409_NOT_POSTABLE_ACCOUNT | `FIN-409-NOT-POSTABLE-ACCOUNT` | exception/FinErrorCodes.java |  |  |
| FIN_409_NOT_REOPENABLE | `FIN-409-NOT-REOPENABLE` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_403_SOD_VIOLATION | `FIN-403-SOD-VIOLATION` | exception/FinErrorCodes.java |  |  |
| FIN_409_UNBALANCED | `FIN-409-UNBALANCED` | exception/FinErrorCodes.java |  |  |
| FIN_409_PERIOD_NOT_OPEN | `FIN-409-PERIOD-NOT-OPEN` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_409_INVALID_DIMENSION | `FIN-409-INVALID-DIMENSION` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_409_DUPLICATE_EVENT | `FIN-409-DUPLICATE-EVENT` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_409_NOT_POSTED | `FIN-409-NOT-POSTED` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_409_INVALID_TRANSITION | `FIN-409-INVALID-TRANSITION` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_404_ENTRY | `FIN-404-ENTRY` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_400_INVALID_LOOKUP | `FIN-400-INVALID-LOOKUP` | exception/FinErrorCodes.java | VALIDATION_ERROR | 400 BAD_REQUEST |
| FIN_409_ACCOUNT_DUP | `FIN-409-ACCOUNT-DUP` | exception/FinErrorCodes.java | ALREADY_EXISTS | 409 CONFLICT |
| FIN_404_ACCOUNT | `FIN-404-ACCOUNT` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_409_DIMENSION_DUP | `FIN-409-DIMENSION-DUP` | exception/FinErrorCodes.java | ALREADY_EXISTS | 409 CONFLICT |
| FIN_404_DIMENSION | `FIN-404-DIMENSION` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_404_DIMVALUE | `FIN-404-DIMVALUE` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_404_RULE | `FIN-404-RULE` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_400_MISSING_FREQUENCY | `FIN-400-MISSING-FREQUENCY` | exception/FinErrorCodes.java | VALIDATION_ERROR | 400 BAD_REQUEST |
| FIN_404_YEAR | `FIN-404-YEAR` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_404_PERIOD | `FIN-404-PERIOD` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_404_NO_ACTIVE_RULE | `FIN-404-NO-ACTIVE-RULE` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_404_ALLOCATION_RULE | `FIN-404-ALLOCATION-RULE` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_409_YEAR_DUP | `FIN-409-YEAR-DUP` | exception/FinErrorCodes.java | ALREADY_EXISTS | 409 CONFLICT |
| FIN_409_PERIODS_NOT_CLOSED | `FIN-409-PERIODS-NOT-CLOSED` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_422_MAPPING_UNSUPPORTED | `FIN-422-MAPPING-UNSUPPORTED` | exception/FinErrorCodes.java | BUSINESS_RULE_VIOLATION | 422 UNPROCESSABLE_CONTENT |
| FIN_404_TEMPLATE | `FIN-404-TEMPLATE` | exception/FinErrorCodes.java | NOT_FOUND | 404 NOT_FOUND |
| FIN_400_INVALID_SORT | `FIN-400-INVALID-SORT` | exception/FinErrorCodes.java | VALIDATION_ERROR | 400 BAD_REQUEST |
| FIN_409_ALREADY_REVERSED | `FIN-409-ALREADY-REVERSED` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |
| FIN_422_REMAINDER_MARKER | `FIN-422-REMAINDER-MARKER` | exception/FinErrorCodes.java | BUSINESS_RULE_VIOLATION | 422 UNPROCESSABLE_CONTENT |
| FIN_422_REMAINDER_NOT_POSITIVE | `FIN-422-REMAINDER-NOT-POSITIVE` | exception/FinErrorCodes.java | BUSINESS_RULE_VIOLATION | 422 UNPROCESSABLE_CONTENT |
| FIN_422_INVALID_PERCENTAGE_VALUE | `FIN-422-INVALID-PERCENTAGE-VALUE` | exception/FinErrorCodes.java | BUSINESS_RULE_VIOLATION | 422 UNPROCESSABLE_CONTENT |
| FIN_400_PERIOD_NOT_IN_YEAR | `FIN-400-PERIOD-NOT-IN-YEAR` | exception/FinErrorCodes.java | VALIDATION_ERROR | 400 BAD_REQUEST |
| FIN_400_DOCDATE_OUTSIDE_PERIOD | `FIN-400-DOCDATE-OUTSIDE-PERIOD` | exception/FinErrorCodes.java | VALIDATION_ERROR | 400 BAD_REQUEST |
| FIN_403_FORBIDDEN | `FIN-403-FORBIDDEN` | exception/FinErrorCodes.java | FORBIDDEN | 403 FORBIDDEN |
| FIN_409_NOT_ACTIVE | `FIN-409-NOT-ACTIVE` | exception/FinErrorCodes.java | CONFLICT | 409 CONFLICT |

## Status -> HTTP Status Reference

Shared, module-independent mapping every business error code's `Status` resolves through (see each error code's own Status column above, when known).

| Status | HTTP Status |
|---|---|
| ALREADY_EXISTS | 409 CONFLICT |
| BUSINESS_RULE_VIOLATION | 422 UNPROCESSABLE_CONTENT |
| CONFLICT | 409 CONFLICT |
| CREATED | 201 CREATED |
| FORBIDDEN | 403 FORBIDDEN |
| INTERNAL_ERROR | 500 INTERNAL_SERVER_ERROR |
| NOT_FOUND | 404 NOT_FOUND |
| PAYLOAD_TOO_LARGE | 413 CONTENT_TOO_LARGE |
| SUCCESS | 200 OK |
| UNAUTHORIZED | 401 UNAUTHORIZED |
| UNSUPPORTED_MEDIA_TYPE | 415 UNSUPPORTED_MEDIA_TYPE |
| UPDATED | 200 OK |
| VALIDATION_ERROR | 400 BAD_REQUEST |

## API Catalog

### FIN Recurring Template Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| PUT | `/api/v1/fin/recurring-templates/{id}/deactivate` | Deactivate recurring template | [deactivate](endpoints/fin-recurring-template-management.md#put-apiv1finrecurring-templatesiddeactivate) |
| POST | `/api/v1/fin/recurring-templates` | Create recurring template | [create](endpoints/fin-recurring-template-management.md#post-apiv1finrecurring-templates) |
| POST | `/api/v1/fin/recurring-templates/{id}/run` | Run a recurring template | [run](endpoints/fin-recurring-template-management.md#post-apiv1finrecurring-templatesidrun) |
| POST | `/api/v1/fin/recurring-templates/search` | Search recurring templates | [search](endpoints/fin-recurring-template-management.md#post-apiv1finrecurring-templatessearch) |

### FIN Event Rule Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| PUT | `/api/v1/fin/event-rules/{id}/deactivate` | Deactivate event-type rule | [deactivate_1](endpoints/fin-event-rule-management.md#put-apiv1finevent-rulesiddeactivate) |
| POST | `/api/v1/fin/event-rules` | Create event-type rule | [create_2](endpoints/fin-event-rule-management.md#post-apiv1finevent-rules) |
| POST | `/api/v1/fin/event-rules/{id}/lines` | Add rule line | [createRuleLine](endpoints/fin-event-rule-management.md#post-apiv1finevent-rulesidlines) |
| POST | `/api/v1/fin/event-rules/search` | Search event-type rules | [search_3](endpoints/fin-event-rule-management.md#post-apiv1finevent-rulessearch) |

### FIN Dimension Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| PUT | `/api/v1/fin/dimensions/values/{id}/deactivate` | Deactivate dimension value | [deactivateDimensionValue](endpoints/fin-dimension-management.md#put-apiv1findimensionsvaluesiddeactivate) |
| POST | `/api/v1/fin/dimensions` | Create dimension | [create_3](endpoints/fin-dimension-management.md#post-apiv1findimensions) |
| POST | `/api/v1/fin/dimensions/{id}/values` | Create dimension value | [createDimensionValue](endpoints/fin-dimension-management.md#post-apiv1findimensionsidvalues) |
| POST | `/api/v1/fin/dimensions/values/search` | Search dimension values | [searchDimensionValues](endpoints/fin-dimension-management.md#post-apiv1findimensionsvaluessearch) |
| POST | `/api/v1/fin/dimensions/search` | Search dimensions | [search_4](endpoints/fin-dimension-management.md#post-apiv1findimensionssearch) |

### FIN Allocation Rule Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| PUT | `/api/v1/fin/allocation-rules/{id}/deactivate` | Deactivate allocation rule | [deactivate_2](endpoints/fin-allocation-rule-management.md#put-apiv1finallocation-rulesiddeactivate) |
| POST | `/api/v1/fin/allocation-rules` | Create allocation rule | [create_4](endpoints/fin-allocation-rule-management.md#post-apiv1finallocation-rules) |
| POST | `/api/v1/fin/allocation-rules/{id}/run` | Run an allocation rule | [run_1](endpoints/fin-allocation-rule-management.md#post-apiv1finallocation-rulesidrun) |
| POST | `/api/v1/fin/allocation-rules/search` | Search allocation rules | [search_5](endpoints/fin-allocation-rule-management.md#post-apiv1finallocation-rulessearch) |

### FIN Account Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| PUT | `/api/v1/fin/accounts/{id}` | Update account | [update](endpoints/fin-account-management.md#put-apiv1finaccountsid) |
| PUT | `/api/v1/fin/accounts/{id}/deactivate` | Deactivate account | [deactivate_3](endpoints/fin-account-management.md#put-apiv1finaccountsiddeactivate) |
| POST | `/api/v1/fin/accounts` | Create account | [create_5](endpoints/fin-account-management.md#post-apiv1finaccounts) |
| POST | `/api/v1/fin/accounts/search` | Search accounts | [search_6](endpoints/fin-account-management.md#post-apiv1finaccountssearch) |

### FIN Journal Entry Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| POST | `/api/v1/fin/journal-entries` | Create manual journal entry | [createManual](endpoints/fin-journal-entry-management.md#post-apiv1finjournal-entries) |
| POST | `/api/v1/fin/journal-entries/{id}/reverse` | Reverse a posted journal entry | [reverse](endpoints/fin-journal-entry-management.md#post-apiv1finjournal-entriesidreverse) |
| POST | `/api/v1/fin/journal-entries/search` | Search journal entries | [search_1](endpoints/fin-journal-entry-management.md#post-apiv1finjournal-entriessearch) |
| POST | `/api/v1/fin/journal-entries/from-event` | Build and post a journal entry from an accounting event | [buildFromEvent](endpoints/fin-journal-entry-management.md#post-apiv1finjournal-entriesfrom-event) |
| GET | `/api/v1/fin/journal-entries/{id}` | Read a journal entry with its lines | [read](endpoints/fin-journal-entry-management.md#get-apiv1finjournal-entriesid) |

### FIN Fiscal Year Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| POST | `/api/v1/fin/fiscal-years` | Create fiscal year and generate its periods | [create_1](endpoints/fin-fiscal-year-management.md#post-apiv1finfiscal-years) |
| POST | `/api/v1/fin/fiscal-years/{id}/year-end-close` | Run year-end close | [yearEndClose](endpoints/fin-fiscal-year-management.md#post-apiv1finfiscal-yearsidyear-end-close) |

### FIN Fiscal Period Management

| Method | Path | Summary | Doc |
|---|---|---|---|
| POST | `/api/v1/fin/fiscal-periods/search` | Search fiscal periods | [search_2](endpoints/fin-fiscal-period-management.md#post-apiv1finfiscal-periodssearch) |
| PATCH | `/api/v1/fin/fiscal-periods/{id}/soft-close` | Soft-close a fiscal period | [softClose](endpoints/fin-fiscal-period-management.md#patch-apiv1finfiscal-periodsidsoft-close) |
| PATCH | `/api/v1/fin/fiscal-periods/{id}/open` | Open a fiscal period | [open](endpoints/fin-fiscal-period-management.md#patch-apiv1finfiscal-periodsidopen) |
| PATCH | `/api/v1/fin/fiscal-periods/{id}/hard-close` | Hard-close a fiscal period (approval) | [hardClose](endpoints/fin-fiscal-period-management.md#patch-apiv1finfiscal-periodsidhard-close) |

### FIN Financial Reports

| Method | Path | Summary | Doc |
|---|---|---|---|
| GET | `/api/v1/fin/reports/trial-balance` | Trial balance | [trialBalance](endpoints/fin-financial-reports.md#get-apiv1finreportstrial-balance) |
| GET | `/api/v1/fin/reports/income-statement` | Income statement | [incomeStatement](endpoints/fin-financial-reports.md#get-apiv1finreportsincome-statement) |
| GET | `/api/v1/fin/reports/dimension` | Dimension report | [dimensionReport](endpoints/fin-financial-reports.md#get-apiv1finreportsdimension) |
| GET | `/api/v1/fin/reports/balance-sheet` | Balance sheet | [balanceSheet](endpoints/fin-financial-reports.md#get-apiv1finreportsbalance-sheet) |
| GET | `/api/v1/fin/reports/account-ledger` | Account ledger | [accountLedger](endpoints/fin-financial-reports.md#get-apiv1finreportsaccount-ledger) |


---

<!-- from api-docs/endpoints/fin-account-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Account Management

**Endpoints in this file:**

- [PUT /api/v1/fin/accounts/{id}](#put-apiv1finaccountsid)
- [PUT /api/v1/fin/accounts/{id}/deactivate](#put-apiv1finaccountsiddeactivate)
- [POST /api/v1/fin/accounts](#post-apiv1finaccounts)
- [POST /api/v1/fin/accounts/search](#post-apiv1finaccountssearch)

## PUT /api/v1/fin/accounts/{id}

**Update account**

تعديل حساب

Operation ID: `update`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Request Body

Schema: `AccountUpdateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| nameAr | string | Yes | maxLength: 200 | Name (Arabic) - الاسم بالعربية | النقدية بالصندوق |
| nameEn | string | Yes | maxLength: 200 | Name (English) - الاسم بالإنجليزية | Cash on hand |
| isLeafFl | boolean | Yes |  | Accepts direct posting - يقبل الترحيل المباشر | true |

**Request Example**

```json
{
  "nameAr": "النقدية بالصندوق",
  "nameEn": "Cash on hand",
  "isLeafFl": true
}
```

### Response `200` — OK

Shape: `AccountResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| accountPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| code | string | No |  | Unique account code - رمز الحساب الفريد | 1101 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | النقدية بالصندوق |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Cash on hand |
| accountTypeCode | string | No |  | Account type code, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| parentAccountId | integer (int64) | No |  | Parent account id - معرّف الحساب الأب | 10 |
| isLeafFl | boolean | No |  | Accepts direct posting - يقبل الترحيل المباشر | true |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| isRetainedEarningsFl | boolean | No |  | Marks the single Retained Earnings account used by year-end close; read-only, never settable through the account APIs - يُحدِّد حساب الأرباح المُبقاة الوحيد المستخدم في إقفال نهاية السنة | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "accountPk": 1,
  "code": 1101,
  "nameAr": "النقدية بالصندوق",
  "nameEn": "Cash on hand",
  "accountTypeCode": "ASSET",
  "natureCode": "DEBIT",
  "parentAccountId": 10,
  "isLeafFl": true,
  "isActiveFl": true,
  "isRetainedEarningsFl": false
}
```

## PUT /api/v1/fin/accounts/{id}/deactivate

**Deactivate account**

إلغاء تفعيل حساب

Operation ID: `deactivate_3`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `AccountResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| accountPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| code | string | No |  | Unique account code - رمز الحساب الفريد | 1101 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | النقدية بالصندوق |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Cash on hand |
| accountTypeCode | string | No |  | Account type code, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| parentAccountId | integer (int64) | No |  | Parent account id - معرّف الحساب الأب | 10 |
| isLeafFl | boolean | No |  | Accepts direct posting - يقبل الترحيل المباشر | true |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| isRetainedEarningsFl | boolean | No |  | Marks the single Retained Earnings account used by year-end close; read-only, never settable through the account APIs - يُحدِّد حساب الأرباح المُبقاة الوحيد المستخدم في إقفال نهاية السنة | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "accountPk": 1,
  "code": 1101,
  "nameAr": "النقدية بالصندوق",
  "nameEn": "Cash on hand",
  "accountTypeCode": "ASSET",
  "natureCode": "DEBIT",
  "parentAccountId": 10,
  "isLeafFl": true,
  "isActiveFl": true,
  "isRetainedEarningsFl": false
}
```

## POST /api/v1/fin/accounts

**Create account**

إنشاء حساب في دليل الحسابات

Operation ID: `create_5`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `AccountCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| code | string | Yes | maxLength: 30 | Unique account code - رمز الحساب الفريد | 1101 |
| nameAr | string | Yes | maxLength: 200 | Name (Arabic) - الاسم بالعربية | النقدية بالصندوق |
| nameEn | string | Yes | maxLength: 200 | Name (English) - الاسم بالإنجليزية | Cash on hand |
| accountTypeCode | string | Yes | maxLength: 20 | Account type code, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| natureCode | string | Yes | maxLength: 10 | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| parentAccountId | integer (int64) | No |  | Parent account id, omitted for a root account - معرّف الحساب الأب | 10 |
| isLeafFl | boolean | No |  | Accepts direct posting - يقبل الترحيل المباشر | true |

**Request Example**

```json
{
  "code": 1101,
  "nameAr": "النقدية بالصندوق",
  "nameEn": "Cash on hand",
  "accountTypeCode": "ASSET",
  "natureCode": "DEBIT",
  "parentAccountId": 10,
  "isLeafFl": true
}
```

### Response `200` — OK

Shape: `AccountResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| accountPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| code | string | No |  | Unique account code - رمز الحساب الفريد | 1101 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | النقدية بالصندوق |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Cash on hand |
| accountTypeCode | string | No |  | Account type code, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| parentAccountId | integer (int64) | No |  | Parent account id - معرّف الحساب الأب | 10 |
| isLeafFl | boolean | No |  | Accepts direct posting - يقبل الترحيل المباشر | true |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| isRetainedEarningsFl | boolean | No |  | Marks the single Retained Earnings account used by year-end close; read-only, never settable through the account APIs - يُحدِّد حساب الأرباح المُبقاة الوحيد المستخدم في إقفال نهاية السنة | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "accountPk": 1,
  "code": 1101,
  "nameAr": "النقدية بالصندوق",
  "nameEn": "Cash on hand",
  "accountTypeCode": "ASSET",
  "natureCode": "DEBIT",
  "parentAccountId": 10,
  "isLeafFl": true,
  "isActiveFl": true,
  "isRetainedEarningsFl": false
}
```

## POST /api/v1/fin/accounts/search

**Search accounts**

بحث في دليل الحسابات

Operation ID: `search_6`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `AccountSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of AccountResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| accountPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| code | string | No |  | Unique account code - رمز الحساب الفريد | 1101 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | النقدية بالصندوق |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Cash on hand |
| accountTypeCode | string | No |  | Account type code, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| parentAccountId | integer (int64) | No |  | Parent account id - معرّف الحساب الأب | 10 |
| isLeafFl | boolean | No |  | Accepts direct posting - يقبل الترحيل المباشر | true |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| isRetainedEarningsFl | boolean | No |  | Marks the single Retained Earnings account used by year-end close; read-only, never settable through the account APIs - يُحدِّد حساب الأرباح المُبقاة الوحيد المستخدم في إقفال نهاية السنة | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "accountPk": 1,
  "code": 1101,
  "nameAr": "النقدية بالصندوق",
  "nameEn": "Cash on hand",
  "accountTypeCode": "ASSET",
  "natureCode": "DEBIT",
  "parentAccountId": 10,
  "isLeafFl": true,
  "isActiveFl": true,
  "isRetainedEarningsFl": false
}
```


---

<!-- from api-docs/endpoints/fin-allocation-rule-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Allocation Rule Management

**Endpoints in this file:**

- [PUT /api/v1/fin/allocation-rules/{id}/deactivate](#put-apiv1finallocation-rulesiddeactivate)
- [POST /api/v1/fin/allocation-rules](#post-apiv1finallocation-rules)
- [POST /api/v1/fin/allocation-rules/{id}/run](#post-apiv1finallocation-rulesidrun)
- [POST /api/v1/fin/allocation-rules/search](#post-apiv1finallocation-rulessearch)

## PUT /api/v1/fin/allocation-rules/{id}/deactivate

**Deactivate allocation rule**

إلغاء تفعيل قاعدة توزيع تكلفة

Operation ID: `deactivate_2`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `AllocationRuleResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| allocationRulePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | توزيع مصاريف الإدارة |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Administrative expense allocation |
| sourceAccountId | integer (int64) | No |  | Source account id - معرّف الحساب المصدر | 31 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| targetCount | integer (int32) | No |  | Number of allocation targets - عدد الأهداف | 3 |
| targets | array<AllocationTargetResponse> | No |  | Allocation targets - أهداف التوزيع |  |
| targets[].allocationTargetPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| targets[].allocationRuleId | integer (int64) | No |  | Parent allocation rule id - معرّف قاعدة التوزيع الأب | 1 |
| targets[].lineNo | integer (int32) | No |  | Target position within the rule - رقم السطر | 1 |
| targets[].targetAccountId | integer (int64) | No |  | Target account id - معرّف الحساب المستهدف | 21 |
| targets[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |
| targets[].distributionTypeCode | string | No |  | Distribution type, DISTRIBUTION_TYPE lookup - نوع التوزيع | PERCENTAGE |
| targets[].distributionValue | number | No |  | Distribution value - قيمة التوزيع | 25.0 |
| targets[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - هدف الباقي | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "allocationRulePk": 1,
  "nameAr": "توزيع مصاريف الإدارة",
  "nameEn": "Administrative expense allocation",
  "sourceAccountId": 31,
  "isActiveFl": true,
  "targetCount": 3,
  "targets": [
    {
      "allocationTargetPk": 1,
      "allocationRuleId": 1,
      "lineNo": 1,
      "targetAccountId": 21,
      "dimensionValueId": 5,
      "distributionTypeCode": "PERCENTAGE",
      "distributionValue": 25.0,
      "isRemainderFl": false
    }
  ]
}
```

## POST /api/v1/fin/allocation-rules

**Create allocation rule**

إنشاء قاعدة توزيع تكلفة

Operation ID: `create_4`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `AllocationRuleCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| nameAr | string | Yes | maxLength: 150 | Name (Arabic) - الاسم بالعربية | توزيع مصاريف الإدارة |
| nameEn | string | Yes | maxLength: 150 | Name (English) - الاسم بالإنجليزية | Administrative expense allocation |
| sourceAccountId | integer (int64) | Yes |  | Source account id - معرّف الحساب المصدر | 31 |
| targets | array<AllocationTargetCreateRequest> | Yes |  | Allocation targets — when any target uses PERCENTAGE the set must also carry exactly one REMAINDER target (ENT-FIN-014, RULE-FIN-003 reused) - أهداف التوزيع | [{"targetAccountId": 21, "dimensionValueId": 5, "distributionTypeCode": "PERCENTAGE", "distributionValue": 25.0, "isRemainderFl": false}, {"targetAccountId": 22, "distributionTypeCode": "REMAINDER", "isRemainderFl": true}] |
| targets[].targetAccountId | integer (int64) | Yes |  | Target account id - معرّف الحساب المستهدف | 21 |
| targets[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |
| targets[].distributionTypeCode | string | Yes | maxLength: 15 | Distribution type, DISTRIBUTION_TYPE lookup - نوع التوزيع | PERCENTAGE |
| targets[].distributionValue | number | No |  | Distribution value — the percentage or fixed amount; omitted for the remainder target - قيمة التوزيع | 25.0 |
| targets[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution — exactly one target per rule must set this true when any target is PERCENTAGE, and it must be the target whose distributionTypeCode is REMAINDER (ENT-FIN-014, RULE-FIN-003 reused) - هدف الباقي | false |

**Request Example**

```json
{
  "nameAr": "توزيع مصاريف الإدارة",
  "nameEn": "Administrative expense allocation",
  "sourceAccountId": 31,
  "targets": [
    {
      "targetAccountId": 21,
      "dimensionValueId": 5,
      "distributionTypeCode": "PERCENTAGE",
      "distributionValue": 25.0,
      "isRemainderFl": false
    }
  ]
}
```

### Response `200` — OK

Shape: `AllocationRuleResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| allocationRulePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | توزيع مصاريف الإدارة |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Administrative expense allocation |
| sourceAccountId | integer (int64) | No |  | Source account id - معرّف الحساب المصدر | 31 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| targetCount | integer (int32) | No |  | Number of allocation targets - عدد الأهداف | 3 |
| targets | array<AllocationTargetResponse> | No |  | Allocation targets - أهداف التوزيع |  |
| targets[].allocationTargetPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| targets[].allocationRuleId | integer (int64) | No |  | Parent allocation rule id - معرّف قاعدة التوزيع الأب | 1 |
| targets[].lineNo | integer (int32) | No |  | Target position within the rule - رقم السطر | 1 |
| targets[].targetAccountId | integer (int64) | No |  | Target account id - معرّف الحساب المستهدف | 21 |
| targets[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |
| targets[].distributionTypeCode | string | No |  | Distribution type, DISTRIBUTION_TYPE lookup - نوع التوزيع | PERCENTAGE |
| targets[].distributionValue | number | No |  | Distribution value - قيمة التوزيع | 25.0 |
| targets[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - هدف الباقي | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "allocationRulePk": 1,
  "nameAr": "توزيع مصاريف الإدارة",
  "nameEn": "Administrative expense allocation",
  "sourceAccountId": 31,
  "isActiveFl": true,
  "targetCount": 3,
  "targets": [
    {
      "allocationTargetPk": 1,
      "allocationRuleId": 1,
      "lineNo": 1,
      "targetAccountId": 21,
      "dimensionValueId": 5,
      "distributionTypeCode": "PERCENTAGE",
      "distributionValue": 25.0,
      "isRemainderFl": false
    }
  ]
}
```

## POST /api/v1/fin/allocation-rules/{id}/run

**Run an allocation rule**

تشغيل قاعدة توزيع تكلفة

Operation ID: `run_1`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `JournalEntryResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "journalEntryPk": 1,
  "docNo": "JV-2026-000123",
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "statusCode": "POSTED",
  "eventReference": "INV-2026-0001",
  "originalEntryId": 7,
  "reversalEntryId": 9,
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lineCount": 2,
  "lines": [
    {
      "journalLinePk": 1,
      "journalEntryId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "isRemainderFl": false,
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "journalLineDimensionPk": 1,
          "journalLineId": 1,
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```

## POST /api/v1/fin/allocation-rules/search

**Search allocation rules**

بحث في قواعد التوزيع

Operation ID: `search_5`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `AllocationRuleSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of AllocationRuleResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| allocationRulePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | توزيع مصاريف الإدارة |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Administrative expense allocation |
| sourceAccountId | integer (int64) | No |  | Source account id - معرّف الحساب المصدر | 31 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| targetCount | integer (int32) | No |  | Number of allocation targets - عدد الأهداف | 3 |
| targets | array<AllocationTargetResponse> | No |  | Allocation targets - أهداف التوزيع |  |
| targets[].allocationTargetPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| targets[].allocationRuleId | integer (int64) | No |  | Parent allocation rule id - معرّف قاعدة التوزيع الأب | 1 |
| targets[].lineNo | integer (int32) | No |  | Target position within the rule - رقم السطر | 1 |
| targets[].targetAccountId | integer (int64) | No |  | Target account id - معرّف الحساب المستهدف | 21 |
| targets[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |
| targets[].distributionTypeCode | string | No |  | Distribution type, DISTRIBUTION_TYPE lookup - نوع التوزيع | PERCENTAGE |
| targets[].distributionValue | number | No |  | Distribution value - قيمة التوزيع | 25.0 |
| targets[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - هدف الباقي | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "allocationRulePk": 1,
  "nameAr": "توزيع مصاريف الإدارة",
  "nameEn": "Administrative expense allocation",
  "sourceAccountId": 31,
  "isActiveFl": true,
  "targetCount": 3,
  "targets": [
    {
      "allocationTargetPk": 1,
      "allocationRuleId": 1,
      "lineNo": 1,
      "targetAccountId": 21,
      "dimensionValueId": 5,
      "distributionTypeCode": "PERCENTAGE",
      "distributionValue": 25.0,
      "isRemainderFl": false
    }
  ]
}
```


---

<!-- from api-docs/endpoints/fin-dimension-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Dimension Management

**Endpoints in this file:**

- [PUT /api/v1/fin/dimensions/values/{id}/deactivate](#put-apiv1findimensionsvaluesiddeactivate)
- [POST /api/v1/fin/dimensions](#post-apiv1findimensions)
- [POST /api/v1/fin/dimensions/{id}/values](#post-apiv1findimensionsidvalues)
- [POST /api/v1/fin/dimensions/values/search](#post-apiv1findimensionsvaluessearch)
- [POST /api/v1/fin/dimensions/search](#post-apiv1findimensionssearch)

## PUT /api/v1/fin/dimensions/values/{id}/deactivate

**Deactivate dimension value**

إلغاء تفعيل قيمة ضمن بُعد تحليلي

Operation ID: `deactivateDimensionValue`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `DimensionValueResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| dimensionValuePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| dimensionId | integer (int64) | No |  | Parent dimension id - معرّف البُعد الأب | 1 |
| code | string | No |  | Unique code within the parent dimension - الرمز الفريد ضمن البُعد | CC-100 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الإدارة المالية |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Finance department |
| sortOrder | integer (int32) | No |  | Display sort order - ترتيب العرض | 10 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "dimensionValuePk": 1,
  "dimensionId": 1,
  "code": "CC-100",
  "nameAr": "الإدارة المالية",
  "nameEn": "Finance department",
  "sortOrder": 10,
  "isActiveFl": true
}
```

## POST /api/v1/fin/dimensions

**Create dimension**

إنشاء بُعد تحليلي

Operation ID: `create_3`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `DimensionCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| code | string | Yes | maxLength: 30 | Unique dimension code - رمز البُعد الفريد | COST_CENTER |
| nameAr | string | Yes | maxLength: 150 | Name (Arabic) - الاسم بالعربية | مركز التكلفة |
| nameEn | string | Yes | maxLength: 150 | Name (English) - الاسم بالإنجليزية | Cost centre |

**Request Example**

```json
{
  "code": "COST_CENTER",
  "nameAr": "مركز التكلفة",
  "nameEn": "Cost centre"
}
```

### Response `200` — OK

Shape: `DimensionResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| dimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| code | string | No |  | Unique dimension code - رمز البُعد الفريد | COST_CENTER |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | مركز التكلفة |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Cost centre |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "dimensionPk": 1,
  "code": "COST_CENTER",
  "nameAr": "مركز التكلفة",
  "nameEn": "Cost centre",
  "isActiveFl": true
}
```

## POST /api/v1/fin/dimensions/{id}/values

**Create dimension value**

إنشاء قيمة ضمن بُعد تحليلي

Operation ID: `createDimensionValue`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Request Body

Schema: `DimensionValueCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| code | string | Yes | maxLength: 30 | Unique code within the parent dimension - الرمز الفريد ضمن البُعد | CC-100 |
| nameAr | string | Yes | maxLength: 150 | Name (Arabic) - الاسم بالعربية | الإدارة المالية |
| nameEn | string | Yes | maxLength: 150 | Name (English) - الاسم بالإنجليزية | Finance department |
| sortOrder | integer (int32) | Yes |  | Display sort order - ترتيب العرض | 10 |

**Request Example**

```json
{
  "code": "CC-100",
  "nameAr": "الإدارة المالية",
  "nameEn": "Finance department",
  "sortOrder": 10
}
```

### Response `200` — OK

Shape: `DimensionValueResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| dimensionValuePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| dimensionId | integer (int64) | No |  | Parent dimension id - معرّف البُعد الأب | 1 |
| code | string | No |  | Unique code within the parent dimension - الرمز الفريد ضمن البُعد | CC-100 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الإدارة المالية |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Finance department |
| sortOrder | integer (int32) | No |  | Display sort order - ترتيب العرض | 10 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "dimensionValuePk": 1,
  "dimensionId": 1,
  "code": "CC-100",
  "nameAr": "الإدارة المالية",
  "nameEn": "Finance department",
  "sortOrder": 10,
  "isActiveFl": true
}
```

## POST /api/v1/fin/dimensions/values/search

**Search dimension values**

بحث في قيم البُعد التحليلي — معرّف البُعد يُرسَل ضمن مرشِّحات الطلب

Operation ID: `searchDimensionValues`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `DimensionValueSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of DimensionValueResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| dimensionValuePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| dimensionId | integer (int64) | No |  | Parent dimension id - معرّف البُعد الأب | 1 |
| code | string | No |  | Unique code within the parent dimension - الرمز الفريد ضمن البُعد | CC-100 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الإدارة المالية |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Finance department |
| sortOrder | integer (int32) | No |  | Display sort order - ترتيب العرض | 10 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "dimensionValuePk": 1,
  "dimensionId": 1,
  "code": "CC-100",
  "nameAr": "الإدارة المالية",
  "nameEn": "Finance department",
  "sortOrder": 10,
  "isActiveFl": true
}
```

## POST /api/v1/fin/dimensions/search

**Search dimensions**

بحث في الأبعاد التحليلية

Operation ID: `search_4`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `DimensionSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of DimensionResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| dimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| code | string | No |  | Unique dimension code - رمز البُعد الفريد | COST_CENTER |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | مركز التكلفة |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Cost centre |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "dimensionPk": 1,
  "code": "COST_CENTER",
  "nameAr": "مركز التكلفة",
  "nameEn": "Cost centre",
  "isActiveFl": true
}
```


---

<!-- from api-docs/endpoints/fin-event-rule-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Event Rule Management

**Endpoints in this file:**

- [PUT /api/v1/fin/event-rules/{id}/deactivate](#put-apiv1finevent-rulesiddeactivate)
- [POST /api/v1/fin/event-rules](#post-apiv1finevent-rules)
- [POST /api/v1/fin/event-rules/{id}/lines](#post-apiv1finevent-rulesidlines)
- [POST /api/v1/fin/event-rules/search](#post-apiv1finevent-rulessearch)

## PUT /api/v1/fin/event-rules/{id}/deactivate

**Deactivate event-type rule**

إلغاء تفعيل قاعدة نوع حدث محاسبي

Operation ID: `deactivate_1`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `EventTypeRuleResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| eventTypeRulePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| eventTypeCode | string | No |  | Event type code, ACCOUNTING_EVENT_TYPE lookup - رمز نوع الحدث | SALES_INVOICE |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | فاتورة مبيعات |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Sales invoice |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "eventTypeRulePk": 1,
  "eventTypeCode": "SALES_INVOICE",
  "nameAr": "فاتورة مبيعات",
  "nameEn": "Sales invoice",
  "isActiveFl": true
}
```

## POST /api/v1/fin/event-rules

**Create event-type rule**

إنشاء قاعدة نوع حدث محاسبي

Operation ID: `create_2`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `EventTypeRuleCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| eventTypeCode | string | Yes | maxLength: 50 | Event type code, ACCOUNTING_EVENT_TYPE lookup - رمز نوع الحدث | SALES_INVOICE |
| nameAr | string | Yes | maxLength: 150 | Name (Arabic) - الاسم بالعربية | فاتورة مبيعات |
| nameEn | string | Yes | maxLength: 150 | Name (English) - الاسم بالإنجليزية | Sales invoice |

**Request Example**

```json
{
  "eventTypeCode": "SALES_INVOICE",
  "nameAr": "فاتورة مبيعات",
  "nameEn": "Sales invoice"
}
```

### Response `200` — OK

Shape: `EventTypeRuleResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| eventTypeRulePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| eventTypeCode | string | No |  | Event type code, ACCOUNTING_EVENT_TYPE lookup - رمز نوع الحدث | SALES_INVOICE |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | فاتورة مبيعات |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Sales invoice |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "eventTypeRulePk": 1,
  "eventTypeCode": "SALES_INVOICE",
  "nameAr": "فاتورة مبيعات",
  "nameEn": "Sales invoice",
  "isActiveFl": true
}
```

## POST /api/v1/fin/event-rules/{id}/lines

**Add rule line**

إضافة سطر إلى قاعدة نوع الحدث

Operation ID: `createRuleLine`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Request Body

Schema: `RuleLineCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| accountDerivationTypeCode | string | Yes | maxLength: 20 | Account derivation type, ACCOUNT_DERIVATION_TYPE lookup - نوع اشتقاق الحساب | CONSTANT |
| accountDerivationValue | string | Yes |  | Account derivation value - قيمة اشتقاق الحساب | 1101 |
| amountSourceTypeCode | string | Yes | maxLength: 20 | Amount source type, AMOUNT_SOURCE_TYPE lookup - نوع مصدر المبلغ | FIELD |
| amountSourceValue | string | No |  | Amount source value - قيمة مصدر المبلغ | netAmount |
| directionCode | string | Yes | maxLength: 10 | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| distributionTypeCode | string | Yes | maxLength: 15 | Distribution type, DISTRIBUTION_TYPE lookup - نوع التوزيع | FIXED |
| isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |

**Request Example**

```json
{
  "accountDerivationTypeCode": "CONSTANT",
  "accountDerivationValue": 1101,
  "amountSourceTypeCode": "FIELD",
  "amountSourceValue": "netAmount",
  "directionCode": "DEBIT",
  "distributionTypeCode": "FIXED",
  "isRemainderFl": false
}
```

### Response `200` — OK

Shape: `RuleLineResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| ruleLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| eventTypeRuleId | integer (int64) | No |  | Parent event-type rule id - معرّف القاعدة الأب | 1 |
| lineNo | integer (int32) | No |  | Line position within the rule - رقم السطر | 1 |
| accountDerivationTypeCode | string | No |  | Account derivation type, ACCOUNT_DERIVATION_TYPE lookup - نوع اشتقاق الحساب | CONSTANT |
| accountDerivationValue | string | No |  | Account derivation value - قيمة اشتقاق الحساب | 1101 |
| amountSourceTypeCode | string | No |  | Amount source type, AMOUNT_SOURCE_TYPE lookup - نوع مصدر المبلغ | FIELD |
| amountSourceValue | string | No |  | Amount source value - قيمة مصدر المبلغ | netAmount |
| directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| distributionTypeCode | string | No |  | Distribution type, DISTRIBUTION_TYPE lookup - نوع التوزيع | FIXED |
| isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "ruleLinePk": 1,
  "eventTypeRuleId": 1,
  "lineNo": 1,
  "accountDerivationTypeCode": "CONSTANT",
  "accountDerivationValue": 1101,
  "amountSourceTypeCode": "FIELD",
  "amountSourceValue": "netAmount",
  "directionCode": "DEBIT",
  "distributionTypeCode": "FIXED",
  "isRemainderFl": false
}
```

## POST /api/v1/fin/event-rules/search

**Search event-type rules**

بحث في قواعد أنواع الأحداث

Operation ID: `search_3`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `EventTypeRuleSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of EventTypeRuleResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| eventTypeRulePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| eventTypeCode | string | No |  | Event type code, ACCOUNTING_EVENT_TYPE lookup - رمز نوع الحدث | SALES_INVOICE |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | فاتورة مبيعات |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Sales invoice |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "eventTypeRulePk": 1,
  "eventTypeCode": "SALES_INVOICE",
  "nameAr": "فاتورة مبيعات",
  "nameEn": "Sales invoice",
  "isActiveFl": true
}
```


---

<!-- from api-docs/endpoints/fin-financial-reports.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Financial Reports

**Endpoints in this file:**

- [GET /api/v1/fin/reports/trial-balance](#get-apiv1finreportstrial-balance)
- [GET /api/v1/fin/reports/income-statement](#get-apiv1finreportsincome-statement)
- [GET /api/v1/fin/reports/dimension](#get-apiv1finreportsdimension)
- [GET /api/v1/fin/reports/balance-sheet](#get-apiv1finreportsbalance-sheet)
- [GET /api/v1/fin/reports/account-ledger](#get-apiv1finreportsaccount-ledger)

## GET /api/v1/fin/reports/trial-balance

**Trial balance**

ميزان المراجعة المُشتق حيًا

Operation ID: `trialBalance`

**Authentication**

Not determined from the OpenAPI document.

### Query Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| periodId | integer | No |  |
| accountTypeCode | string | No |  |

### Response `200` — OK

Shape: `TrialBalanceResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| periodId | integer (int64) | No |  | Fiscal period filter applied, null when unbounded - الفترة المُرشَّحة | 3 |
| accountTypeCode | string | No |  | Account-type filter applied, null when all types - النوع المُرشَّح | ASSET |
| rows | array<AccountBalanceRowResponse> | No |  | Account rows, ordered by account code - سطور الحسابات |  |
| rows[].accountId | integer (int64) | No |  | Account id, for drill-down (REQ-FIN-046) - معرّف الحساب | 5 |
| rows[].accountCode | string | No |  | Account code - رمز الحساب | 1101 |
| rows[].accountNameAr | string | No |  | Account name (Arabic) - اسم الحساب بالعربية | النقدية بالصندوق |
| rows[].accountNameEn | string | No |  | Account name (English) - اسم الحساب بالإنجليزية | Cash on hand |
| rows[].accountTypeCode | string | No |  | Account type, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| rows[].natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| rows[].debitTotal | number | No |  | Sum of DEBIT line amounts - إجمالي المدين | 5000.0 |
| rows[].creditTotal | number | No |  | Sum of CREDIT line amounts - إجمالي الدائن | 1800.0 |
| rows[].debitBalance | number | No |  | Balance shown on the debit column, zero otherwise (POL-FIN-002) - الرصيد المدين | 3200.0 |
| rows[].creditBalance | number | No |  | Balance shown on the credit column, zero otherwise (POL-FIN-002) - الرصيد الدائن | 0.0 |
| rows[].signedBalance | number | No |  | Net balance signed against the account's nature (POL-FIN-002) - الرصيد الصافي بإشارة طبيعة الحساب | 3200.0 |
| totalDebitBalance | number | No |  | Total of the debit-balance column - إجمالي الأرصدة المدينة | 12500.0 |
| totalCreditBalance | number | No |  | Total of the credit-balance column - إجمالي الأرصدة الدائنة | 12500.0 |
| balanced | boolean | No |  | Whether the two column totals match, an invariant by construction (POL-FIN-008) - هل يتوازن الميزان | true |

**Response Example**

```json
{
  "periodId": 3,
  "accountTypeCode": "ASSET",
  "rows": [
    {
      "accountId": 5,
      "accountCode": 1101,
      "accountNameAr": "النقدية بالصندوق",
      "accountNameEn": "Cash on hand",
      "accountTypeCode": "ASSET",
      "natureCode": "DEBIT",
      "debitTotal": 5000.0,
      "creditTotal": 1800.0,
      "debitBalance": 3200.0,
      "creditBalance": 0.0,
      "signedBalance": 3200.0
    }
  ],
  "totalDebitBalance": 12500.0,
  "totalCreditBalance": 12500.0,
  "balanced": true
}
```

## GET /api/v1/fin/reports/income-statement

**Income statement**

قائمة الدخل

Operation ID: `incomeStatement`

**Authentication**

Not determined from the OpenAPI document.

### Query Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| fiscalYearId | integer | Yes |  |
| fromPeriodId | integer | No |  |
| toPeriodId | integer | No |  |

### Response `200` — OK

Shape: `IncomeStatementResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| fiscalYearId | integer (int64) | No |  | Fiscal year the statement is scoped to - السنة المالية | 1 |
| fromPeriodId | integer (int64) | No |  | First period of the requested range, null when unbounded - أول فترة في المدى | 1 |
| toPeriodId | integer (int64) | No |  | Last period of the requested range, null when unbounded - آخر فترة في المدى | 6 |
| fromDate | string (date) | No |  | docDate lower bound derived from fromPeriodId - بداية المدى | 2026-01-01 |
| toDate | string (date) | No |  | docDate upper bound derived from toPeriodId - نهاية المدى | 2026-06-30 |
| groups | array<AccountBalanceGroupResponse> | No |  | Groups: REVENUE, EXPENSE - المجموعات |  |
| groups[].accountTypeCode | string | No |  | Account type, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| groups[].rows | array<AccountBalanceRowResponse> | No |  | Accounts in this group, ordered by code - حسابات المجموعة |  |
| groups[].rows[].accountId | integer (int64) | No |  | Account id, for drill-down (REQ-FIN-046) - معرّف الحساب | 5 |
| groups[].rows[].accountCode | string | No |  | Account code - رمز الحساب | 1101 |
| groups[].rows[].accountNameAr | string | No |  | Account name (Arabic) - اسم الحساب بالعربية | النقدية بالصندوق |
| groups[].rows[].accountNameEn | string | No |  | Account name (English) - اسم الحساب بالإنجليزية | Cash on hand |
| groups[].rows[].accountTypeCode | string | No |  | Account type, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| groups[].rows[].natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| groups[].rows[].debitTotal | number | No |  | Sum of DEBIT line amounts - إجمالي المدين | 5000.0 |
| groups[].rows[].creditTotal | number | No |  | Sum of CREDIT line amounts - إجمالي الدائن | 1800.0 |
| groups[].rows[].debitBalance | number | No |  | Balance shown on the debit column, zero otherwise (POL-FIN-002) - الرصيد المدين | 3200.0 |
| groups[].rows[].creditBalance | number | No |  | Balance shown on the credit column, zero otherwise (POL-FIN-002) - الرصيد الدائن | 0.0 |
| groups[].rows[].signedBalance | number | No |  | Net balance signed against the account's nature (POL-FIN-002) - الرصيد الصافي بإشارة طبيعة الحساب | 3200.0 |
| groups[].groupTotal | number | No |  | Sum of the group's signed balances (POL-FIN-002) - إجمالي المجموعة | 42000.0 |
| netResult | number | No |  | Revenue total less expense total, both signed per POL-FIN-002 - صافي النتيجة | 8400.0 |

**Response Example**

```json
{
  "fiscalYearId": 1,
  "fromPeriodId": 1,
  "toPeriodId": 6,
  "fromDate": "2026-01-01",
  "toDate": "2026-06-30",
  "groups": [
    {
      "accountTypeCode": "ASSET",
      "rows": [
        {
          "accountId": 5,
          "accountCode": 1101,
          "accountNameAr": "النقدية بالصندوق",
          "accountNameEn": "Cash on hand",
          "accountTypeCode": "ASSET",
          "natureCode": "DEBIT",
          "debitTotal": 5000.0,
          "creditTotal": 1800.0,
          "debitBalance": 3200.0,
          "creditBalance": 0.0,
          "signedBalance": 3200.0
        }
      ],
      "groupTotal": 42000.0
    }
  ],
  "netResult": 8400.0
}
```

## GET /api/v1/fin/reports/dimension

**Dimension report**

تقرير الأبعاد حسب تركيبة الحساب وقيمة البُعد

Operation ID: `dimensionReport`

**Authentication**

Not determined from the OpenAPI document.

### Query Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| dimensionId | integer | Yes |  |
| dimensionValueId | integer | No |  |
| periodId | integer | No |  |

### Response `200` — OK

Shape: `DimensionReportResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| dimensionId | integer (int64) | No |  | Dimension the report is grouped by - البُعد | 2 |
| dimensionValueId | integer (int64) | No |  | Dimension value filter applied, null when all values - قيمة البُعد المُرشَّحة | 7 |
| periodId | integer (int64) | No |  | Fiscal period filter applied, null when unbounded - الفترة المُرشَّحة | 3 |
| rows | array<DimensionReportRowResponse> | No |  | Rows, one per account and dimension value - السطور |  |
| rows[].accountId | integer (int64) | No |  | Account id - معرّف الحساب | 5 |
| rows[].accountCode | string | No |  | Account code - رمز الحساب | 5201 |
| rows[].accountNameAr | string | No |  | Account name (Arabic) - اسم الحساب بالعربية | مصروف إيجار |
| rows[].accountNameEn | string | No |  | Account name (English) - اسم الحساب بالإنجليزية | Rent expense |
| rows[].natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| rows[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 2 |
| rows[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 7 |
| rows[].dimensionValueCode | string | No |  | Dimension value code - رمز قيمة البُعد | PRJ-A |
| rows[].dimensionValueNameAr | string | No |  | Dimension value name (Arabic) - اسم قيمة البُعد بالعربية | مشروع أ |
| rows[].dimensionValueNameEn | string | No |  | Dimension value name (English) - اسم قيمة البُعد بالإنجليزية | Project A |
| rows[].debitTotal | number | No |  | Sum of DEBIT line amounts - إجمالي المدين | 5000.0 |
| rows[].creditTotal | number | No |  | Sum of CREDIT line amounts - إجمالي الدائن | 0.0 |
| rows[].signedBalance | number | No |  | Net balance signed against the account's nature (POL-FIN-002) - الرصيد الصافي | 5000.0 |

**Response Example**

```json
{
  "dimensionId": 2,
  "dimensionValueId": 7,
  "periodId": 3,
  "rows": [
    {
      "accountId": 5,
      "accountCode": 5201,
      "accountNameAr": "مصروف إيجار",
      "accountNameEn": "Rent expense",
      "natureCode": "DEBIT",
      "dimensionId": 2,
      "dimensionValueId": 7,
      "dimensionValueCode": "PRJ-A",
      "dimensionValueNameAr": "مشروع أ",
      "dimensionValueNameEn": "Project A",
      "debitTotal": 5000.0,
      "creditTotal": 0.0,
      "signedBalance": 5000.0
    }
  ]
}
```

## GET /api/v1/fin/reports/balance-sheet

**Balance sheet**

الميزانية العمومية

Operation ID: `balanceSheet`

**Authentication**

Not determined from the OpenAPI document.

### Query Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| fiscalYearId | integer | Yes |  |
| asOfDate | string | No |  |

### Response `200` — OK

Shape: `BalanceSheetResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| fiscalYearId | integer (int64) | No |  | Fiscal year the statement is scoped to - السنة المالية | 1 |
| asOfDate | string (date) | No |  | Cut-off applied to docDate, null when unbounded - تاريخ الإقفال | 2026-12-31 |
| groups | array<AccountBalanceGroupResponse> | No |  | Groups: ASSET, LIABILITY, EQUITY - المجموعات |  |
| groups[].accountTypeCode | string | No |  | Account type, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| groups[].rows | array<AccountBalanceRowResponse> | No |  | Accounts in this group, ordered by code - حسابات المجموعة |  |
| groups[].rows[].accountId | integer (int64) | No |  | Account id, for drill-down (REQ-FIN-046) - معرّف الحساب | 5 |
| groups[].rows[].accountCode | string | No |  | Account code - رمز الحساب | 1101 |
| groups[].rows[].accountNameAr | string | No |  | Account name (Arabic) - اسم الحساب بالعربية | النقدية بالصندوق |
| groups[].rows[].accountNameEn | string | No |  | Account name (English) - اسم الحساب بالإنجليزية | Cash on hand |
| groups[].rows[].accountTypeCode | string | No |  | Account type, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| groups[].rows[].natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| groups[].rows[].debitTotal | number | No |  | Sum of DEBIT line amounts - إجمالي المدين | 5000.0 |
| groups[].rows[].creditTotal | number | No |  | Sum of CREDIT line amounts - إجمالي الدائن | 1800.0 |
| groups[].rows[].debitBalance | number | No |  | Balance shown on the debit column, zero otherwise (POL-FIN-002) - الرصيد المدين | 3200.0 |
| groups[].rows[].creditBalance | number | No |  | Balance shown on the credit column, zero otherwise (POL-FIN-002) - الرصيد الدائن | 0.0 |
| groups[].rows[].signedBalance | number | No |  | Net balance signed against the account's nature (POL-FIN-002) - الرصيد الصافي بإشارة طبيعة الحساب | 3200.0 |
| groups[].groupTotal | number | No |  | Sum of the group's signed balances (POL-FIN-002) - إجمالي المجموعة | 42000.0 |

**Response Example**

```json
{
  "fiscalYearId": 1,
  "asOfDate": "2026-12-31",
  "groups": [
    {
      "accountTypeCode": "ASSET",
      "rows": [
        {
          "accountId": 5,
          "accountCode": 1101,
          "accountNameAr": "النقدية بالصندوق",
          "accountNameEn": "Cash on hand",
          "accountTypeCode": "ASSET",
          "natureCode": "DEBIT",
          "debitTotal": 5000.0,
          "creditTotal": 1800.0,
          "debitBalance": 3200.0,
          "creditBalance": 0.0,
          "signedBalance": 3200.0
        }
      ],
      "groupTotal": 42000.0
    }
  ]
}
```

## GET /api/v1/fin/reports/account-ledger

**Account ledger**

دفتر الحساب المُشتق حيًا من القيود المُرحَّلة

Operation ID: `accountLedger`

**Authentication**

Not determined from the OpenAPI document.

### Query Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| accountId | integer | Yes |  |
| fromDate | string | No |  |
| toDate | string | No |  |
| dimensionId | integer | No |  |
| dimensionValueId | integer | No |  |

### Response `200` — OK

Shape: `AccountLedgerResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| accountId | integer (int64) | No |  | Account id - معرّف الحساب | 5 |
| accountCode | string | No |  | Account code - رمز الحساب | 1101 |
| accountNameAr | string | No |  | Account name (Arabic) - اسم الحساب بالعربية | النقدية بالصندوق |
| accountNameEn | string | No |  | Account name (English) - اسم الحساب بالإنجليزية | Cash on hand |
| accountTypeCode | string | No |  | Account type, ACCOUNT_TYPE lookup - نوع الحساب | ASSET |
| natureCode | string | No |  | Normal balance side, DEBIT_CREDIT lookup - طبيعة الحساب | DEBIT |
| fromDate | string (date) | No |  | Range start applied to docDate, null when unbounded - بداية المدى | 2026-01-01 |
| toDate | string (date) | No |  | Range end applied to docDate, null when unbounded - نهاية المدى | 2026-01-31 |
| dimensionId | integer (int64) | No |  | Dimension filter applied, null when none - البُعد المُرشَّح | 2 |
| dimensionValueId | integer (int64) | No |  | Dimension-value filter applied, null when none - قيمة البُعد المُرشَّحة | 7 |
| debitTotal | number | No |  | Total of DEBIT lines in range - إجمالي المدين | 5000.0 |
| creditTotal | number | No |  | Total of CREDIT lines in range - إجمالي الدائن | 1800.0 |
| closingBalance | number | No |  | Closing balance, signed per POL-FIN-002 - الرصيد الختامي | 3200.0 |
| rows | array<AccountLedgerRowResponse> | No |  | Ledger rows, oldest first - سطور الدفتر |  |
| rows[].journalEntryId | integer (int64) | No |  | Originating journal entry id, for drill-down (REQ-FIN-046) - معرّف القيد المصدر | 12 |
| rows[].docNo | string | No |  | Journal entry document number - رقم مستند القيد | JV-2026-000123 |
| rows[].docDate | string (date) | No |  | Journal entry document date - تاريخ مستند القيد | 2026-01-31 |
| rows[].journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| rows[].eventReference | string | No |  | Source event reference, when the entry was event-built - مرجع الحدث | INV-2026-0001 |
| rows[].journalLineId | integer (int64) | No |  | Journal line id - معرّف سطر القيد | 44 |
| rows[].lineNo | integer (int32) | No |  | Line number inside the entry - رقم السطر داخل القيد | 1 |
| rows[].amount | number | No |  | Line amount, always positive (POL-FIN-005) - المبلغ | 1500.0 |
| rows[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| rows[].signedAmount | number | No |  | Amount signed against the account's nature (POL-FIN-002) - المبلغ بإشارة طبيعة الحساب | 1500.0 |
| rows[].runningBalance | number | No |  | Running balance after this line, signed per POL-FIN-002 - الرصيد الجاري بعد هذا السطر | 3200.0 |
| rows[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إيجار يناير |
| rows[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | January rent |

**Response Example**

```json
{
  "accountId": 5,
  "accountCode": 1101,
  "accountNameAr": "النقدية بالصندوق",
  "accountNameEn": "Cash on hand",
  "accountTypeCode": "ASSET",
  "natureCode": "DEBIT",
  "fromDate": "2026-01-01",
  "toDate": "2026-01-31",
  "dimensionId": 2,
  "dimensionValueId": 7,
  "debitTotal": 5000.0,
  "creditTotal": 1800.0,
  "closingBalance": 3200.0,
  "rows": [
    {
      "journalEntryId": 12,
      "docNo": "JV-2026-000123",
      "docDate": "2026-01-31",
      "journalTypeCode": "MANUAL",
      "eventReference": "INV-2026-0001",
      "journalLineId": 44,
      "lineNo": 1,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "signedAmount": 1500.0,
      "runningBalance": 3200.0,
      "descriptionAr": "إيجار يناير",
      "descriptionEn": "January rent"
    }
  ]
}
```


---

<!-- from api-docs/endpoints/fin-fiscal-period-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Fiscal Period Management

**Endpoints in this file:**

- [POST /api/v1/fin/fiscal-periods/search](#post-apiv1finfiscal-periodssearch)
- [PATCH /api/v1/fin/fiscal-periods/{id}/soft-close](#patch-apiv1finfiscal-periodsidsoft-close)
- [PATCH /api/v1/fin/fiscal-periods/{id}/open](#patch-apiv1finfiscal-periodsidopen)
- [PATCH /api/v1/fin/fiscal-periods/{id}/hard-close](#patch-apiv1finfiscal-periodsidhard-close)

## POST /api/v1/fin/fiscal-periods/search

**Search fiscal periods**

البحث في الفترات المحاسبية

Operation ID: `search_2`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `FiscalPeriodSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of FiscalPeriodResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| fiscalPeriodPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodNo | integer (int32) | No |  | Period number within the year - رقم الفترة | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الفترة 1 |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Period 1 |
| startDate | string (date) | No |  | First day of the period - أول أيام الفترة | 2026-01-01 |
| endDate | string (date) | No |  | Last day of the period - آخر أيام الفترة | 2026-01-31 |
| statusCode | string | No |  | Status, PERIOD_STATE lookup - حالة الفترة | OPEN |
| closedBy | string | No |  | Close-approval principal - معتمد الإغلاق | finance.approver |
| closedAt | string (date-time) | No |  | Close-approval moment - وقت اعتماد الإغلاق |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "fiscalPeriodPk": 1,
  "fiscalYearId": 1,
  "periodNo": 1,
  "nameAr": "الفترة 1",
  "nameEn": "Period 1",
  "startDate": "2026-01-01",
  "endDate": "2026-01-31",
  "statusCode": "OPEN",
  "closedBy": "finance.approver"
}
```

## PATCH /api/v1/fin/fiscal-periods/{id}/soft-close

**Soft-close a fiscal period**

إغلاق ناعم لفترة محاسبية

Operation ID: `softClose`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `FiscalPeriodResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| fiscalPeriodPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodNo | integer (int32) | No |  | Period number within the year - رقم الفترة | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الفترة 1 |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Period 1 |
| startDate | string (date) | No |  | First day of the period - أول أيام الفترة | 2026-01-01 |
| endDate | string (date) | No |  | Last day of the period - آخر أيام الفترة | 2026-01-31 |
| statusCode | string | No |  | Status, PERIOD_STATE lookup - حالة الفترة | OPEN |
| closedBy | string | No |  | Close-approval principal - معتمد الإغلاق | finance.approver |
| closedAt | string (date-time) | No |  | Close-approval moment - وقت اعتماد الإغلاق |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "fiscalPeriodPk": 1,
  "fiscalYearId": 1,
  "periodNo": 1,
  "nameAr": "الفترة 1",
  "nameEn": "Period 1",
  "startDate": "2026-01-01",
  "endDate": "2026-01-31",
  "statusCode": "OPEN",
  "closedBy": "finance.approver"
}
```

## PATCH /api/v1/fin/fiscal-periods/{id}/open

**Open a fiscal period**

فتح فترة محاسبية

Operation ID: `open`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `FiscalPeriodResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| fiscalPeriodPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodNo | integer (int32) | No |  | Period number within the year - رقم الفترة | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الفترة 1 |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Period 1 |
| startDate | string (date) | No |  | First day of the period - أول أيام الفترة | 2026-01-01 |
| endDate | string (date) | No |  | Last day of the period - آخر أيام الفترة | 2026-01-31 |
| statusCode | string | No |  | Status, PERIOD_STATE lookup - حالة الفترة | OPEN |
| closedBy | string | No |  | Close-approval principal - معتمد الإغلاق | finance.approver |
| closedAt | string (date-time) | No |  | Close-approval moment - وقت اعتماد الإغلاق |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "fiscalPeriodPk": 1,
  "fiscalYearId": 1,
  "periodNo": 1,
  "nameAr": "الفترة 1",
  "nameEn": "Period 1",
  "startDate": "2026-01-01",
  "endDate": "2026-01-31",
  "statusCode": "OPEN",
  "closedBy": "finance.approver"
}
```

## PATCH /api/v1/fin/fiscal-periods/{id}/hard-close

**Hard-close a fiscal period (approval)**

إغلاق صارم لفترة محاسبية باعتماد

Operation ID: `hardClose`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `FiscalPeriodResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| fiscalPeriodPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodNo | integer (int32) | No |  | Period number within the year - رقم الفترة | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الفترة 1 |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Period 1 |
| startDate | string (date) | No |  | First day of the period - أول أيام الفترة | 2026-01-01 |
| endDate | string (date) | No |  | Last day of the period - آخر أيام الفترة | 2026-01-31 |
| statusCode | string | No |  | Status, PERIOD_STATE lookup - حالة الفترة | OPEN |
| closedBy | string | No |  | Close-approval principal - معتمد الإغلاق | finance.approver |
| closedAt | string (date-time) | No |  | Close-approval moment - وقت اعتماد الإغلاق |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "fiscalPeriodPk": 1,
  "fiscalYearId": 1,
  "periodNo": 1,
  "nameAr": "الفترة 1",
  "nameEn": "Period 1",
  "startDate": "2026-01-01",
  "endDate": "2026-01-31",
  "statusCode": "OPEN",
  "closedBy": "finance.approver"
}
```


---

<!-- from api-docs/endpoints/fin-fiscal-year-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Fiscal Year Management

**Endpoints in this file:**

- [POST /api/v1/fin/fiscal-years](#post-apiv1finfiscal-years)
- [POST /api/v1/fin/fiscal-years/{id}/year-end-close](#post-apiv1finfiscal-yearsidyear-end-close)

## POST /api/v1/fin/fiscal-years

**Create fiscal year and generate its periods**

إنشاء سنة مالية وتوليد فتراتها

Operation ID: `create_1`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `FiscalYearCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| code | string | Yes | maxLength: 10 | Fiscal year code - رمز السنة المالية | 2026 |
| startDate | string (date) | Yes |  | First day of the fiscal year - أول أيام السنة المالية | 2026-01-01 |
| endDate | string (date) | Yes |  | Last day of the fiscal year - آخر أيام السنة المالية | 2026-12-31 |
| periodCount | integer (int32) | Yes |  | Number of periods to generate, each initially Open - عدد الفترات | 12 |

**Request Example**

```json
{
  "code": 2026,
  "startDate": "2026-01-01",
  "endDate": "2026-12-31",
  "periodCount": 12
}
```

### Response `200` — OK

Shape: `FiscalYearResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| fiscalYearPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| code | string | No |  | Fiscal year code - رمز السنة المالية | 2026 |
| startDate | string (date) | No |  | First day of the fiscal year - أول أيام السنة المالية | 2026-01-01 |
| endDate | string (date) | No |  | Last day of the fiscal year - آخر أيام السنة المالية | 2026-12-31 |
| statusCode | string | No |  | Status, FISCAL_YEAR_STATUS lookup - حالة السنة | OPEN |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| periodCount | integer (int32) | No |  | Number of periods - عدد الفترات | 12 |
| periods | array<FiscalPeriodResponse> | No |  | Generated periods - الفترات المولَّدة |  |
| periods[].fiscalPeriodPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| periods[].fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periods[].periodNo | integer (int32) | No |  | Period number within the year - رقم الفترة | 1 |
| periods[].nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | الفترة 1 |
| periods[].nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Period 1 |
| periods[].startDate | string (date) | No |  | First day of the period - أول أيام الفترة | 2026-01-01 |
| periods[].endDate | string (date) | No |  | Last day of the period - آخر أيام الفترة | 2026-01-31 |
| periods[].statusCode | string | No |  | Status, PERIOD_STATE lookup - حالة الفترة | OPEN |
| periods[].closedBy | string | No |  | Close-approval principal - معتمد الإغلاق | finance.approver |
| periods[].closedAt | string (date-time) | No |  | Close-approval moment - وقت اعتماد الإغلاق |  |
| periods[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| periods[].createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| periods[].updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| periods[].updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "fiscalYearPk": 1,
  "code": 2026,
  "startDate": "2026-01-01",
  "endDate": "2026-12-31",
  "statusCode": "OPEN",
  "isActiveFl": true,
  "periodCount": 12,
  "periods": [
    {
      "fiscalPeriodPk": 1,
      "fiscalYearId": 1,
      "periodNo": 1,
      "nameAr": "الفترة 1",
      "nameEn": "Period 1",
      "startDate": "2026-01-01",
      "endDate": "2026-01-31",
      "statusCode": "OPEN",
      "closedBy": "finance.approver"
    }
  ]
}
```

## POST /api/v1/fin/fiscal-years/{id}/year-end-close

**Run year-end close**

تشغيل إقفال نهاية السنة وتوليد قيدي الإقفال والافتتاح

Operation ID: `yearEndClose`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `YearEndCloseResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| closingEntry | JournalEntryResponse | No |  | Journal entry - قيد يومية |  |
| closingEntry.journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| closingEntry.docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| closingEntry.docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| closingEntry.fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| closingEntry.periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| closingEntry.journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| closingEntry.statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| closingEntry.eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| closingEntry.originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| closingEntry.reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| closingEntry.descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| closingEntry.descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| closingEntry.postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| closingEntry.lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| closingEntry.lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| closingEntry.lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| closingEntry.lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| closingEntry.lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| closingEntry.lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| closingEntry.lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| closingEntry.lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| closingEntry.lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| closingEntry.lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| closingEntry.lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| closingEntry.lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| closingEntry.lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| closingEntry.lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| closingEntry.lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| closingEntry.lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| closingEntry.lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| closingEntry.createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| closingEntry.createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| closingEntry.updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| closingEntry.updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |
| openingEntry | JournalEntryResponse | No |  | Journal entry - قيد يومية |  |
| openingEntry.journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| openingEntry.docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| openingEntry.docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| openingEntry.fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| openingEntry.periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| openingEntry.journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| openingEntry.statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| openingEntry.eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| openingEntry.originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| openingEntry.reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| openingEntry.descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| openingEntry.descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| openingEntry.postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| openingEntry.lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| openingEntry.lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| openingEntry.lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| openingEntry.lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| openingEntry.lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| openingEntry.lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| openingEntry.lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| openingEntry.lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| openingEntry.lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| openingEntry.lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| openingEntry.lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| openingEntry.lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| openingEntry.lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| openingEntry.lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| openingEntry.lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| openingEntry.lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| openingEntry.lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| openingEntry.createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| openingEntry.createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| openingEntry.updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| openingEntry.updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "closingEntry": {
    "journalEntryPk": 1,
    "docNo": "JV-2026-000123",
    "docDate": "2026-01-31",
    "fiscalYearId": 1,
    "periodId": 1,
    "journalTypeCode": "MANUAL",
    "statusCode": "POSTED",
    "eventReference": "INV-2026-0001",
    "originalEntryId": 7,
    "reversalEntryId": 9,
    "descriptionAr": "قيد إهلاك يناير",
    "descriptionEn": "January depreciation entry",
    "lineCount": 2,
    "lines": [
      {
        "journalLinePk": 1,
        "journalEntryId": 1,
        "lineNo": 1,
        "accountId": 12,
        "amount": 1500.0,
        "directionCode": "DEBIT",
        "isRemainderFl": false,
        "descriptionAr": "إهلاك",
        "descriptionEn": "Depreciation",
        "dimensions": [
          {
            "journalLineDimensionPk": 1,
            "journalLineId": 1,
            "dimensionId": 1,
            "dimensionValueId": 5
          }
        ]
      }
    ]
  },
  "openingEntry": {
    "journalEntryPk": 1,
    "docNo": "JV-2026-000123",
    "docDate": "2026-01-31",
    "fiscalYearId": 1,
    "periodId": 1,
    "journalTypeCode": "MANUAL",
    "statusCode": "POSTED",
    "eventReference": "INV-2026-0001",
    "originalEntryId": 7,
    "reversalEntryId": 9,
    "descriptionAr": "قيد إهلاك يناير",
    "descriptionEn": "January depreciation entry",
    "lineCount": 2,
    "lines": [
      {
        "journalLinePk": 1,
        "journalEntryId": 1,
        "lineNo": 1,
        "accountId": 12,
        "amount": 1500.0,
        "directionCode": "DEBIT",
        "isRemainderFl": false,
        "descriptionAr": "إهلاك",
        "descriptionEn": "Depreciation",
        "dimensions": [
          {
            "journalLineDimensionPk": 1,
            "journalLineId": 1,
            "dimensionId": 1,
            "dimensionValueId": 5
          }
        ]
      }
    ]
  }
}
```


---

<!-- from api-docs/endpoints/fin-journal-entry-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Journal Entry Management

**Endpoints in this file:**

- [POST /api/v1/fin/journal-entries](#post-apiv1finjournal-entries)
- [POST /api/v1/fin/journal-entries/{id}/reverse](#post-apiv1finjournal-entriesidreverse)
- [POST /api/v1/fin/journal-entries/search](#post-apiv1finjournal-entriessearch)
- [POST /api/v1/fin/journal-entries/from-event](#post-apiv1finjournal-entriesfrom-event)
- [GET /api/v1/fin/journal-entries/{id}](#get-apiv1finjournal-entriesid)

## POST /api/v1/fin/journal-entries

**Create manual journal entry**

إنشاء وترحيل قيد يومية يدوي

Operation ID: `createManual`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `JournalEntryCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| docDate | string (date) | Yes |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | Yes |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | Yes |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | Yes | maxLength: 20 | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| lines | array<JournalLineCreateRequest> | Yes |  | Entry lines - سطور القيد |  |
| lines[].accountId | integer (int64) | Yes |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | Yes |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | Yes | maxLength: 10 | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionCreateRequest> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].dimensionId | integer (int64) | Yes |  | Dimension id the value is claimed to belong to - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | Yes |  | Dimension value id - معرّف قيمة البُعد | 5 |

**Request Example**

```json
{
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lines": [
    {
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```

### Response `200` — OK

Shape: `JournalEntryResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "journalEntryPk": 1,
  "docNo": "JV-2026-000123",
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "statusCode": "POSTED",
  "eventReference": "INV-2026-0001",
  "originalEntryId": 7,
  "reversalEntryId": 9,
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lineCount": 2,
  "lines": [
    {
      "journalLinePk": 1,
      "journalEntryId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "isRemainderFl": false,
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "journalLineDimensionPk": 1,
          "journalLineId": 1,
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```

## POST /api/v1/fin/journal-entries/{id}/reverse

**Reverse a posted journal entry**

عكس قيد يومية مُرحَّل

Operation ID: `reverse`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `JournalEntryResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "journalEntryPk": 1,
  "docNo": "JV-2026-000123",
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "statusCode": "POSTED",
  "eventReference": "INV-2026-0001",
  "originalEntryId": 7,
  "reversalEntryId": 9,
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lineCount": 2,
  "lines": [
    {
      "journalLinePk": 1,
      "journalEntryId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "isRemainderFl": false,
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "journalLineDimensionPk": 1,
          "journalLineId": 1,
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```

## POST /api/v1/fin/journal-entries/search

**Search journal entries**

بحث في قيود اليومية

Operation ID: `search_1`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `JournalEntrySearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of JournalEntryResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "journalEntryPk": 1,
  "docNo": "JV-2026-000123",
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "statusCode": "POSTED",
  "eventReference": "INV-2026-0001",
  "originalEntryId": 7,
  "reversalEntryId": 9,
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lineCount": 2,
  "lines": [
    {
      "journalLinePk": 1,
      "journalEntryId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "isRemainderFl": false,
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "journalLineDimensionPk": 1,
          "journalLineId": 1,
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```

## POST /api/v1/fin/journal-entries/from-event

**Build and post a journal entry from an accounting event**

بناء وترحيل قيد يومية من حدث محاسبي

Operation ID: `buildFromEvent`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `EventEntryBuildRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| eventReference | string | Yes | maxLength: 100 | Event idempotency reference - المرجع الفريد للحدث | SALES-INV-2026-000811 |
| eventTypeCode | string | Yes | maxLength: 50 | Event type, ACCOUNTING_EVENT_TYPE lookup - نوع الحدث المحاسبي | SALES_INVOICE |
| docDate | string (date) | Yes |  | Document date; selects the target fiscal period - تاريخ المستند | 2026-01-31 |
| baseAmount | number | Yes |  | Event base amount the rule distributes - المبلغ الأساسي للحدث | 1000.0 |
| amounts | object | No |  | Named amount fields of the event - حقول المبالغ المسماة للحدث |  |
| fields | object | No |  | Named string fields of the event - حقول النصوص المسماة للحدث |  |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | فاتورة مبيعات |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | Sales invoice |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "eventReference": "SALES-INV-2026-000811",
  "eventTypeCode": "SALES_INVOICE",
  "docDate": "2026-01-31",
  "baseAmount": 1000.0,
  "descriptionAr": "فاتورة مبيعات",
  "descriptionEn": "Sales invoice"
}
```

### Response `200` — OK

Shape: `JournalEntryResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "journalEntryPk": 1,
  "docNo": "JV-2026-000123",
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "statusCode": "POSTED",
  "eventReference": "INV-2026-0001",
  "originalEntryId": 7,
  "reversalEntryId": 9,
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lineCount": 2,
  "lines": [
    {
      "journalLinePk": 1,
      "journalEntryId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "isRemainderFl": false,
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "journalLineDimensionPk": 1,
          "journalLineId": 1,
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```

## GET /api/v1/fin/journal-entries/{id}

**Read a journal entry with its lines**

عرض قيد يومية مع سطوره وأبعاده

Operation ID: `read`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `JournalEntryResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "journalEntryPk": 1,
  "docNo": "JV-2026-000123",
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "statusCode": "POSTED",
  "eventReference": "INV-2026-0001",
  "originalEntryId": 7,
  "reversalEntryId": 9,
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lineCount": 2,
  "lines": [
    {
      "journalLinePk": 1,
      "journalEntryId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "isRemainderFl": false,
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "journalLineDimensionPk": 1,
          "journalLineId": 1,
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```


---

<!-- from api-docs/endpoints/fin-recurring-template-management.md -->

<!-- AUTO-GENERATED by api-doc-generator — do not edit manually -->
# FIN Recurring Template Management

**Endpoints in this file:**

- [PUT /api/v1/fin/recurring-templates/{id}/deactivate](#put-apiv1finrecurring-templatesiddeactivate)
- [POST /api/v1/fin/recurring-templates](#post-apiv1finrecurring-templates)
- [POST /api/v1/fin/recurring-templates/{id}/run](#post-apiv1finrecurring-templatesidrun)
- [POST /api/v1/fin/recurring-templates/search](#post-apiv1finrecurring-templatessearch)

## PUT /api/v1/fin/recurring-templates/{id}/deactivate

**Deactivate recurring template**

إلغاء تفعيل قالب قيد متكرر

Operation ID: `deactivate`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `RecurringTemplateResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| recurringTemplatePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | إهلاك شهري |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Monthly depreciation |
| scheduleTypeCode | string | No |  | Schedule type, RECURRING_SCHEDULE_TYPE lookup - نوع الجدولة | RECURRING |
| frequencyCode | string | No |  | Frequency, RECURRING_FREQUENCY lookup - التكرار | MONTHLY |
| startDate | string (date) | No |  | First run date - تاريخ البداية | 2026-01-31 |
| nextRunDate | string (date) | No |  | Next scheduled run date - تاريخ التشغيل التالي | 2026-01-31 |
| endDate | string (date) | No |  | Last run date - تاريخ النهاية | 2026-12-31 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| lineCount | integer (int32) | No |  | Number of template lines - عدد السطور | 2 |
| lines | array<RecurringTemplateLineResponse> | No |  | Template lines - سطور القالب |  |
| lines[].recurringTemplateLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].recurringTemplateId | integer (int64) | No |  | Parent template id - معرّف القالب الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the template - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "recurringTemplatePk": 1,
  "nameAr": "إهلاك شهري",
  "nameEn": "Monthly depreciation",
  "scheduleTypeCode": "RECURRING",
  "frequencyCode": "MONTHLY",
  "startDate": "2026-01-31",
  "nextRunDate": "2026-01-31",
  "endDate": "2026-12-31",
  "isActiveFl": true,
  "lineCount": 2,
  "lines": [
    {
      "recurringTemplateLinePk": 1,
      "recurringTemplateId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "dimensionValueId": 5
    }
  ]
}
```

## POST /api/v1/fin/recurring-templates

**Create recurring template**

إنشاء قالب قيد متكرر

Operation ID: `create`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `RecurringTemplateCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| nameAr | string | Yes | maxLength: 150 | Name (Arabic) - الاسم بالعربية | إهلاك شهري |
| nameEn | string | Yes | maxLength: 150 | Name (English) - الاسم بالإنجليزية | Monthly depreciation |
| scheduleTypeCode | string | Yes | maxLength: 15 | Schedule type, RECURRING_SCHEDULE_TYPE lookup - نوع الجدولة | RECURRING |
| frequencyCode | string | No | maxLength: 15 | Frequency, RECURRING_FREQUENCY lookup; required unless the schedule type is REVERSING - التكرار | MONTHLY |
| startDate | string (date) | Yes |  | First run date - تاريخ البداية | 2026-01-31 |
| endDate | string (date) | No |  | Last run date, open-ended when omitted - تاريخ النهاية | 2026-12-31 |
| lines | array<RecurringTemplateLineCreateRequest> | Yes |  | Template lines - سطور القالب |  |
| lines[].accountId | integer (int64) | Yes |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | Yes |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | Yes | maxLength: 10 | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |

**Request Example**

```json
{
  "nameAr": "إهلاك شهري",
  "nameEn": "Monthly depreciation",
  "scheduleTypeCode": "RECURRING",
  "frequencyCode": "MONTHLY",
  "startDate": "2026-01-31",
  "endDate": "2026-12-31",
  "lines": [
    {
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "dimensionValueId": 5
    }
  ]
}
```

### Response `200` — OK

Shape: `RecurringTemplateResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| recurringTemplatePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | إهلاك شهري |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Monthly depreciation |
| scheduleTypeCode | string | No |  | Schedule type, RECURRING_SCHEDULE_TYPE lookup - نوع الجدولة | RECURRING |
| frequencyCode | string | No |  | Frequency, RECURRING_FREQUENCY lookup - التكرار | MONTHLY |
| startDate | string (date) | No |  | First run date - تاريخ البداية | 2026-01-31 |
| nextRunDate | string (date) | No |  | Next scheduled run date - تاريخ التشغيل التالي | 2026-01-31 |
| endDate | string (date) | No |  | Last run date - تاريخ النهاية | 2026-12-31 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| lineCount | integer (int32) | No |  | Number of template lines - عدد السطور | 2 |
| lines | array<RecurringTemplateLineResponse> | No |  | Template lines - سطور القالب |  |
| lines[].recurringTemplateLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].recurringTemplateId | integer (int64) | No |  | Parent template id - معرّف القالب الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the template - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "recurringTemplatePk": 1,
  "nameAr": "إهلاك شهري",
  "nameEn": "Monthly depreciation",
  "scheduleTypeCode": "RECURRING",
  "frequencyCode": "MONTHLY",
  "startDate": "2026-01-31",
  "nextRunDate": "2026-01-31",
  "endDate": "2026-12-31",
  "isActiveFl": true,
  "lineCount": 2,
  "lines": [
    {
      "recurringTemplateLinePk": 1,
      "recurringTemplateId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "dimensionValueId": 5
    }
  ]
}
```

## POST /api/v1/fin/recurring-templates/{id}/run

**Run a recurring template**

تشغيل قالب قيد متكرر

Operation ID: `run`

**Authentication**

Not determined from the OpenAPI document.

### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

### Response `200` — OK

Shape: `JournalEntryResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| journalEntryPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| docNo | string | No |  | System-generated document number - رقم المستند | JV-2026-000123 |
| docDate | string (date) | No |  | Document date - تاريخ المستند | 2026-01-31 |
| fiscalYearId | integer (int64) | No |  | Owning fiscal year id - معرّف السنة المالية | 1 |
| periodId | integer (int64) | No |  | Target fiscal period id - معرّف الفترة المالية | 1 |
| journalTypeCode | string | No |  | Journal type, JOURNAL_TYPE lookup - نوع اليومية | MANUAL |
| statusCode | string | No |  | Status, JOURNAL_STATUS lookup - الحالة | POSTED |
| eventReference | string | No |  | Source event reference, for event-built entries - مرجع الحدث | INV-2026-0001 |
| originalEntryId | integer (int64) | No |  | Original entry id, when this entry is a reversal - معرّف القيد الأصلي | 7 |
| reversalEntryId | integer (int64) | No |  | Reversal entry id, when this entry has been reversed - معرّف قيد العكس | 9 |
| descriptionAr | string | No |  | Entry description (Arabic) - وصف القيد بالعربية | قيد إهلاك يناير |
| descriptionEn | string | No |  | Entry description (English) - وصف القيد بالإنجليزية | January depreciation entry |
| postedAt | string (date-time) | No |  | Posting timestamp - تاريخ الترحيل |  |
| lineCount | integer (int32) | No |  | Number of entry lines - عدد السطور | 2 |
| lines | array<JournalLineResponse> | No |  | Entry lines - سطور القيد |  |
| lines[].journalLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].journalEntryId | integer (int64) | No |  | Parent journal entry id - معرّف القيد الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the entry - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].isRemainderFl | boolean | No |  | Carries the remainder of a percentage distribution - سطر الباقي | false |
| lines[].descriptionAr | string | No |  | Line description (Arabic) - وصف السطر بالعربية | إهلاك |
| lines[].descriptionEn | string | No |  | Line description (English) - وصف السطر بالإنجليزية | Depreciation |
| lines[].dimensions | array<JournalLineDimensionResponse> | No |  | Analysis dimension tags - الأبعاد التحليلية |  |
| lines[].dimensions[].journalLineDimensionPk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].dimensions[].journalLineId | integer (int64) | No |  | Parent journal line id - معرّف سطر القيد الأب | 1 |
| lines[].dimensions[].dimensionId | integer (int64) | No |  | Dimension id - معرّف البُعد | 1 |
| lines[].dimensions[].dimensionValueId | integer (int64) | No |  | Dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "journalEntryPk": 1,
  "docNo": "JV-2026-000123",
  "docDate": "2026-01-31",
  "fiscalYearId": 1,
  "periodId": 1,
  "journalTypeCode": "MANUAL",
  "statusCode": "POSTED",
  "eventReference": "INV-2026-0001",
  "originalEntryId": 7,
  "reversalEntryId": 9,
  "descriptionAr": "قيد إهلاك يناير",
  "descriptionEn": "January depreciation entry",
  "lineCount": 2,
  "lines": [
    {
      "journalLinePk": 1,
      "journalEntryId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "isRemainderFl": false,
      "descriptionAr": "إهلاك",
      "descriptionEn": "Depreciation",
      "dimensions": [
        {
          "journalLineDimensionPk": 1,
          "journalLineId": 1,
          "dimensionId": 1,
          "dimensionValueId": 5
        }
      ]
    }
  ]
}
```

## POST /api/v1/fin/recurring-templates/search

**Search recurring templates**

بحث في القوالب المتكررة

Operation ID: `search`

**Authentication**

Not determined from the OpenAPI document.

### Request Body

Schema: `RecurringTemplateSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| filters | array<SearchFilter> | No |  | Filter criteria - معايير التصفية |  |
| filters[].field | string | No |  |  |  |
| filters[].operator | string | No | enum: EQUALS, NOT_EQUALS, LIKE, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, IN |  |  |
| filters[].value | object | No |  |  |  |
| sortField | string | No |  | Sort field - حقل الترتيب |  |
| sortDirection | string | No | enum: ASC, DESC | Sort direction - اتجاه الترتيب |  |
| page | integer (int32) | No |  | Page number, zero-based - رقم الصفحة | 0 |
| size | integer (int32) | No |  | Page size - حجم الصفحة | 20 |

**Request Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "page": 0,
  "size": 20
}
```

### Response `200` — OK

Shape: `paginated list of RecurringTemplateResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| recurringTemplatePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| nameAr | string | No |  | Name (Arabic) - الاسم بالعربية | إهلاك شهري |
| nameEn | string | No |  | Name (English) - الاسم بالإنجليزية | Monthly depreciation |
| scheduleTypeCode | string | No |  | Schedule type, RECURRING_SCHEDULE_TYPE lookup - نوع الجدولة | RECURRING |
| frequencyCode | string | No |  | Frequency, RECURRING_FREQUENCY lookup - التكرار | MONTHLY |
| startDate | string (date) | No |  | First run date - تاريخ البداية | 2026-01-31 |
| nextRunDate | string (date) | No |  | Next scheduled run date - تاريخ التشغيل التالي | 2026-01-31 |
| endDate | string (date) | No |  | Last run date - تاريخ النهاية | 2026-12-31 |
| isActiveFl | boolean | No |  | Active status - حالة التفعيل | true |
| lineCount | integer (int32) | No |  | Number of template lines - عدد السطور | 2 |
| lines | array<RecurringTemplateLineResponse> | No |  | Template lines - سطور القالب |  |
| lines[].recurringTemplateLinePk | integer (int64) | No |  | Unique identifier - المعرف الفريد | 1 |
| lines[].recurringTemplateId | integer (int64) | No |  | Parent template id - معرّف القالب الأب | 1 |
| lines[].lineNo | integer (int32) | No |  | Line position within the template - رقم السطر | 1 |
| lines[].accountId | integer (int64) | No |  | Target account id - معرّف الحساب | 12 |
| lines[].amount | number | No |  | Line amount, always positive - المبلغ | 1500.0 |
| lines[].directionCode | string | No |  | Direction, DEBIT_CREDIT lookup - الاتجاه | DEBIT |
| lines[].dimensionValueId | integer (int64) | No |  | Optional dimension value id - معرّف قيمة البُعد | 5 |
| lines[].createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

_(partial — only fields with a documented example are shown)_

```json
{
  "recurringTemplatePk": 1,
  "nameAr": "إهلاك شهري",
  "nameEn": "Monthly depreciation",
  "scheduleTypeCode": "RECURRING",
  "frequencyCode": "MONTHLY",
  "startDate": "2026-01-31",
  "nextRunDate": "2026-01-31",
  "endDate": "2026-12-31",
  "isActiveFl": true,
  "lineCount": 2,
  "lines": [
    {
      "recurringTemplateLinePk": 1,
      "recurringTemplateId": 1,
      "lineNo": 1,
      "accountId": 12,
      "amount": 1500.0,
      "directionCode": "DEBIT",
      "dimensionValueId": 5
    }
  ]
}
```

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

<<<INPUT: registry-exec-be>>>
## REGISTRY — P3.1 — FIN v1
══════════════════════════════════════════════════════════════════

ID RANGES
API-FIN-001 .. API-FIN-032 · QR-FIN-001 .. QR-FIN-044

API ids: API-FIN-001, API-FIN-002, API-FIN-003, API-FIN-004, API-FIN-005, API-FIN-006,
API-FIN-007, API-FIN-008, API-FIN-009, API-FIN-010, API-FIN-011, API-FIN-012, API-FIN-013,
API-FIN-014, API-FIN-015, API-FIN-016, API-FIN-017, API-FIN-018, API-FIN-019, API-FIN-020,
API-FIN-021, API-FIN-022, API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026, API-FIN-027,
API-FIN-028, API-FIN-029, API-FIN-030, API-FIN-031, API-FIN-032

QR ids: QR-FIN-001, QR-FIN-002, QR-FIN-003, QR-FIN-004, QR-FIN-005, QR-FIN-006, QR-FIN-007,
QR-FIN-008, QR-FIN-009, QR-FIN-010, QR-FIN-011, QR-FIN-012, QR-FIN-013, QR-FIN-014,
QR-FIN-015, QR-FIN-016, QR-FIN-017, QR-FIN-018, QR-FIN-019, QR-FIN-020, QR-FIN-021,
QR-FIN-022, QR-FIN-023, QR-FIN-024, QR-FIN-025, QR-FIN-026, QR-FIN-027, QR-FIN-028,
QR-FIN-029, QR-FIN-030, QR-FIN-031, QR-FIN-032, QR-FIN-033, QR-FIN-034, QR-FIN-035,
QR-FIN-036, QR-FIN-037, QR-FIN-038, QR-FIN-039, QR-FIN-040, QR-FIN-041, QR-FIN-042,
QR-FIN-043, QR-FIN-044

ENTITIES / TABLES bound
All 14 ENT-FIN-001..014 bound to their db-script tables; lookups: 13 FIN-owned keys
registered into MDL (2 additional values, CLOSING/OPENING, added to JOURNAL_TYPE this
stage — data-only, non-breaking).

XM STATUS
open: none · deferred: none · active: XM-FIN-001 (SOFT-READ → MDL, target already gated).

CATALOG
31 error-catalog rows (29 module-specific/PLATFORM-STD + FIN-403-FORBIDDEN +
FIN-400-INVALID-SORT + FIN-500 generic set). Rules without a message: none — every
RULE-FIN-001..016 that produces a user-facing message has a full ar/en pair.

ALIGN
PASSED ✓ · 0 findings — including the explicit 14-point §12 coverage check (see
backend-execution-plan-fin.md → Alignment self-check → "ACCOUNTING §12" row).

ADRs
erp/decisions/FIN/ADR-FIN-001.md (ACCEPTED, carried from P2; no new ADR this stage).

TRACEABILITY
REQ covered by ≥1 API/DBF: 46/46 (every REQ-FIN-001..046 appears in ≥1 API block's
traces= or ≥1 DBF record's traces in db-script-fin.md). Orphan REQ: none.

Event
"P3.1 completed: FIN v1 — 32 API, 44 QR, ALIGN PASSED (14-point §12 coverage confirmed), 0 new ADRs"
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

