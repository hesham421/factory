---
# Machine-readable contract list — `gov.py render` builds the index below from it,
# `gov.py analyze` implements every clause. Owner/consumer are stage ids from
# factory.yaml (or an input id from factory.inputs / a tool step); artifacts are
# artifact ids from stages[*].produces; kinds are ids.atoms prefixes.
# Clause `check` vocabulary (defined in §13 of this file, keep it small):
#   exists · no-questions · languages · ids-owned · ids-continue · traces · orphans
#   · ears · registry-agree · markers · manifest · gate-approved
#   · value-agreement · code-format · data-source · xref-resolve · refs-exist · paths-resolve
contracts:
  - id: C1
    title: domain profile → registry bootstrap
    owner: domain-profile
    consumer: P-1
    artifacts: [domain-profile]
    clauses:
      - {id: C1.1, check: exists,       args: {artifact: domain-profile},                       severity: CRITICAL}
      - {id: C1.2, check: no-questions, args: {artifact: domain-profile},                       severity: CRITICAL}
      - {id: C1.3, check: languages,    args: {artifact: domain-profile},                       severity: MAJOR}
  - id: C2
    title: project registry → inception
    owner: P-1
    consumer: P0
    artifacts: [project-registry]
    clauses:
      - {id: C2.1, check: exists,         args: {artifact: project-registry},                                        severity: CRITICAL}
      - {id: C2.2, check: registry-agree, args: {registry: project-registry, categories: all},                        severity: MAJOR}
      - {id: C2.3, check: ids-owned,      args: {artifact: project-registry, defines: []},                            severity: MAJOR}
  - id: C3
    title: inception → PRD
    owner: P0
    consumer: P0.5
    artifacts: [platform-summary, module-registry, business-policies]
    clauses:
      - {id: C3.1, check: exists,       args: {artifact: platform-summary},                     severity: CRITICAL}
      - {id: C3.2, check: exists,       args: {artifact: module-registry},                      severity: CRITICAL}
      - {id: C3.3, check: exists,       args: {artifact: business-policies},                    severity: CRITICAL}
      - {id: C3.4, check: ids-owned,    args: {stage: P0},                                      severity: CRITICAL}
      - {id: C3.5, check: no-questions, args: {stage: P0},                                      severity: CRITICAL}
      - {id: C3.6, check: languages,    args: {stage: P0},                                      severity: MAJOR}
      - {id: C3.7, check: registry-agree, args: {artifact: business-policies, registry: module-registry, kinds: [POL]}, severity: MAJOR}
  - id: C4
    title: PRD → SRS (human PRD approval in between)
    owner: P0.5
    consumer: P1
    artifacts: [prd]
    gate: prd-approval
    clauses:
      - {id: C4.1, check: exists,        args: {artifact: prd},                                  severity: CRITICAL}
      - {id: C4.2, check: gate-approved, args: {gate: prd-approval},                             severity: CRITICAL}
      - {id: C4.3, check: ids-owned,     args: {stage: P0.5},                                    severity: CRITICAL}
      - {id: C4.4, check: traces,        args: {from: US, to: [POL], min: 1},                    severity: MAJOR}
      - {id: C4.5, check: no-questions,  args: {stage: P0.5},                                    severity: CRITICAL}
      - {id: C4.6, check: languages,     args: {stage: P0.5},                                    severity: MAJOR}
  - id: C5
    title: SRS → database
    owner: P1
    consumer: P2
    artifacts: [srs, registry-srs]
    clauses:
      - {id: C5.1, check: exists,         args: {artifact: srs},                                                  severity: CRITICAL}
      - {id: C5.2, check: ears,           args: {kind: REQ, patterns: "factory.ids.ears.patterns"},               severity: CRITICAL}
      - {id: C5.3, check: traces,         args: {from: REQ, to: [US], min: 1},                                    severity: MAJOR}
      - {id: C5.4, check: orphans,        args: {kind: REQ, referenced_by: [AC], min: 1},                         severity: CRITICAL}
      - {id: C5.5, check: traces,         args: {from: AC, to: [REQ], min: 1},                                    severity: MAJOR}
      - {id: C5.6, check: traces,         args: {from: RULE, to: [REQ], min: 1},                                  severity: MAJOR}
      - {id: C5.7, check: ids-owned,      args: {stage: P1},                                                      severity: CRITICAL}
      - {id: C5.8, check: registry-agree, args: {artifact: srs, registry: registry-srs, kinds: [REQ, AC, ENT, RULE]}, severity: MAJOR}
      - {id: C5.9, check: no-questions,   args: {stage: P1},                                                      severity: CRITICAL}
      - {id: C5.10, check: languages,     args: {stage: P1},                                                      severity: MAJOR}
      - {id: C5.11, check: ids-continue,  args: {stage: P1},                                                      severity: CRITICAL}
      - {id: C5.12, check: data-source,   args: {kind: RULE, label: "Data source", resolves_to: [ENT], deferral: DEFERRED}, severity: CRITICAL}
  - id: C6
    title: SRS + database → backend execution plan
    owner: [P1, P2]
    consumer: P3.1
    artifacts: [srs, registry-srs, db-script, registry-db]
    clauses:
      - {id: C6.1, check: exists,         args: {artifact: db-script},                                            severity: CRITICAL}
      - {id: C6.2, check: traces,         args: {from: DBF, to: [REQ, ENT], min: 1},                               severity: MAJOR}
      - {id: C6.3, check: traces,         args: {from: XM, to: [REQ], min: 1},                                     severity: MAJOR}
      - {id: C6.4, check: ids-owned,      args: {stage: P2},                                                       severity: CRITICAL}
      - {id: C6.5, check: registry-agree, args: {artifact: db-script, registry: registry-db, kinds: [DBF, XM]},     severity: MAJOR}
      - {id: C6.6, check: orphans,        args: {kind: ENT, referenced_by: [DBF], min: 1},                          severity: MAJOR}
      - {id: C6.7, check: no-questions,   args: {stage: P2},                                                       severity: CRITICAL}
      - {id: C6.8, check: ids-continue,   args: {stage: P2},                                                       severity: CRITICAL}
      - {id: C6.9, check: data-source,    args: {kind: RULE, label: "Data source", resolves_to: [ENT], deferral: DEFERRED, bound_in: db-script}, severity: CRITICAL}
  - id: C7
    title: backend execution plan → split / deliver
    owner: P3.1
    consumer: split
    artifacts: [backend-execution-plan, registry-exec-be]
    clauses:
      - {id: C7.1, check: markers,        args: {artifact: backend-execution-plan, track: backend, plan: exec},                  severity: CRITICAL}
      - {id: C7.2, check: traces,         args: {from: backend-execution-plan, blocks: [PHASE, SUB, API, XM], min: 1},          severity: MAJOR}
      - {id: C7.3, check: traces,         args: {from: API, to: [REQ, DBF], min: 1},                                            severity: MAJOR}
      - {id: C7.4, check: registry-agree, args: {artifact: backend-execution-plan, registry: registry-exec-be, kinds: [API, QR]}, severity: MAJOR}
      - {id: C7.5, check: registry-agree, args: {artifact: backend-execution-plan, registry: registry-db, kinds: [XM]},           severity: MAJOR}
      - {id: C7.6, check: orphans,        args: {kind: REQ, referenced_by: [API, DBF], min: 1},                                 severity: MAJOR}
      - {id: C7.7, check: ids-owned,      args: {stage: P3.1},                                                                  severity: CRITICAL}
      - {id: C7.8, check: no-questions,   args: {stage: P3.1},                                                                  severity: CRITICAL}
      - {id: C7.9, check: ids-continue,   args: {stage: P3.1},                                                                  severity: CRITICAL}
      - {id: C7.10, check: value-agreement, args: {kind: DBF, binding: db-script, against: [backend-execution-plan]},              severity: CRITICAL}
      - {id: C7.11, check: code-format,   args: {artifact: [backend-execution-plan], format: stack.backend.api.error_code_format}, severity: MAJOR}
      - {id: C7.12, check: xref-resolve,  args: {artifact: [backend-execution-plan, registry-exec-be]},                            severity: CRITICAL}
      - {id: C7.13, check: refs-exist,    args: {kind: ADR, dir: decisions, file_pattern: adr_file},                               severity: CRITICAL}
      - {id: C7.14, check: paths-resolve, args: {files: [manifest_file]},                                                          severity: CRITICAL}
  - id: C8
    title: real API docs (consumer repo input) → frontend
    owner: api-docs
    consumer: P3.2
    artifacts: [api-docs]
    clauses:
      - {id: C8.1, check: exists,         args: {input: api-docs},                                                       severity: CRITICAL}
      - {id: C8.2, check: registry-agree, args: {artifact: api-docs, registry: registry-exec-be, kinds: [API], direction: artifact→registry}, severity: MAJOR}
      - {id: C8.3, check: registry-agree, args: {artifact: api-docs, registry: registry-exec-be, kinds: [API], direction: registry→artifact}, severity: MAJOR}
  - id: C9
    title: frontend design + execution plan → split / deliver
    owner: P3.2
    consumer: split
    artifacts: [flow-diagram, ui-ux-spec, frontend-execution-plan, registry-exec-fe]
    clauses:
      - {id: C9.1, check: markers,        args: {artifact: frontend-execution-plan, track: frontend, plan: exec},             severity: CRITICAL}
      - {id: C9.2, check: traces,         args: {from: frontend-execution-plan, blocks: [PHASE, SUB], min: 1},               severity: MAJOR}
      - {id: C9.3, check: traces,         args: {from: UXD, to: [REQ, AC], min: 1},                                          severity: MAJOR}
      - {id: C9.4, check: traces,         args: {from: SCR, to: [REQ, UXD], min: 1},                                         severity: MAJOR}
      - {id: C9.5, check: traces,         args: {from: frontend-execution-plan, to: [API], defined_in: api-docs},             severity: CRITICAL}
      - {id: C9.6, check: orphans,        args: {kind: UXD, referenced_by: [frontend-execution-plan], min: 1},               severity: MAJOR}
      - {id: C9.7, check: orphans,        args: {kind: SCR, referenced_by: [frontend-execution-plan], min: 1},               severity: MAJOR}
      - {id: C9.8, check: registry-agree, args: {artifact: [ui-ux-spec, frontend-execution-plan], registry: registry-exec-fe, kinds: [UXD, SCR]}, severity: MAJOR}
      - {id: C9.9, check: ids-owned,      args: {stage: P3.2},                                                               severity: CRITICAL}
      - {id: C9.10, check: no-questions,  args: {stage: P3.2},                                                               severity: CRITICAL}
      - {id: C9.11, check: ids-continue,  args: {stage: P3.2},                                                               severity: CRITICAL}
  - id: C10
    title: acceptance criteria → test generation (standalone)
    owner: P1
    consumer: test-gen
    artifacts: [srs, registry-srs, backend-execution-plan, frontend-execution-plan, registry-db, registry-exec-fe]
    clauses:
      - {id: C10.1, check: traces,   args: {from: TC, to: [AC, XM, UXD], min: 1, mode: any},                          severity: CRITICAL}
      - {id: C10.2, check: orphans,  args: {kind: AC, referenced_by: [TC], min: 1},                                   severity: MAJOR}
      - {id: C10.3, check: markers,  args: {artifact: backend-test-plan, track: backend, plan: test},                 severity: CRITICAL}
      - {id: C10.4, check: markers,  args: {artifact: frontend-test-plan, track: frontend, plan: test},               severity: CRITICAL}
      - {id: C10.5, check: ids-owned, args: {stage: test-gen},                                                        severity: CRITICAL}
      - {id: C10.6, check: exists,   args: {artifact: test-execution-manifest, when: "profile.stack.testing.manifest"}, severity: MINOR}
  - id: C11
    title: real API docs (+ manifest) → API verification (standalone)
    owner: api-docs
    consumer: api-verify
    artifacts: [api-docs, test-execution-manifest]
    clauses:
      - {id: C11.1, check: exists, args: {input: api-docs},                       severity: CRITICAL}
      - {id: C11.2, check: exists, args: {artifact: test-execution-manifest},     severity: MINOR}
      - {id: C11.3, check: exists, args: {artifact: api-verify-report},           severity: MAJOR}
  - id: C12
    title: delta version (change manifest) → every stage
    owner: versioning
    consumer: any
    artifacts: [change-manifest]
    clauses:
      - {id: C12.1, check: exists,       args: {artifact: change-manifest, when: "version > 1"},      severity: CRITICAL}
      - {id: C12.2, check: manifest,     args: {artifact: change-manifest},                            severity: CRITICAL}
      - {id: C12.3, check: ids-continue, args: {scope: version},                                       severity: CRITICAL}
---

# ARTIFACT CONTRACTS — what crosses each interface, and what `gov.py analyze` checks

```
Doc            : shared/ARTIFACT-CONTRACTS.md
Role           : one contract per interface between stages (and tool steps); every clause is machine-checkable
Loaded by      : every engine brief (its own owner/consumer contracts), reviewers/pass-review.md, gov.py analyze, gov.py render
Generated parts: RENDER:contracts-index (from the front-matter `contracts:` list)
Links          : GOVERNANCE-CORE.md · MARKER-PROTOCOL.md · REGISTRY-SCHEMA.md · VERSIONING.md · XM-PROTOCOL.md · QUALITY-RUBRIC.md
```

<!-- RENDER:contracts-index -->
| Contract | Interface | Owner | Consumer | Artifacts | Clauses |
|---|---|---|---|---|---|
| `C1` | domain profile → registry bootstrap | `domain-profile` | `P-1` | `domain-profile` | 3 |
| `C2` | project registry → inception | `P-1` | `P0` | `project-registry` | 3 |
| `C3` | inception → PRD | `P0` | `P0.5` | `platform-summary`, `module-registry`, `business-policies` | 7 |
| `C4` | PRD → SRS (human PRD approval in between) | `P0.5` | `P1` | `prd` | 6 |
| `C5` | SRS → database | `P1` | `P2` | `srs`, `registry-srs` | 12 |
| `C6` | SRS + database → backend execution plan | `P1+P2` | `P3.1` | `srs`, `registry-srs`, `db-script`, `registry-db` | 9 |
| `C7` | backend execution plan → split / deliver | `P3.1` | `split` | `backend-execution-plan`, `registry-exec-be` | 14 |
| `C8` | real API docs (consumer repo input) → frontend | `api-docs` | `P3.2` | `api-docs` | 3 |
| `C9` | frontend design + execution plan → split / deliver | `P3.2` | `split` | `flow-diagram`, `ui-ux-spec`, `frontend-execution-plan`, `registry-exec-fe` | 11 |
| `C10` | acceptance criteria → test generation (standalone) | `P1` | `test-gen` | `srs`, `registry-srs`, `backend-execution-plan`, `frontend-execution-plan`, `registry-db`, `registry-exec-fe` | 6 |
| `C11` | real API docs (+ manifest) → API verification (standalone) | `api-docs` | `api-verify` | `api-docs`, `test-execution-manifest` | 3 |
| `C12` | delta version (change manifest) → every stage | `versioning` | `any` | `change-manifest` | 3 |
<!-- /RENDER:contracts-index -->

**Reading a contract.** *Owner* produces, *Consumer* reads. *What crosses* is
the artifact plus the ID kinds and `traces` targets it must carry. *What does
not cross* is content the consumer derives by ID lookup and must never
restate (restating is a DUPLICATE finding, MAJOR). *Clauses* are the
front-matter rows in prose; `gov.py analyze` implements them (§13). *Violation*
gives the gate effect: CRITICAL closes the gate, MAJOR forces REVISE, MINOR is
recorded. Stage ids, artifact ids and ID kinds below are addresses into
`factory.yaml`, not restated values.

---

## C1 — domain profile → registry bootstrap

| | |
|---|---|
| Owner | `domain-profile` (conversational stage, `questions: allowed`, dialogue lane) |
| Consumer | `P-1` |
| What crosses | `domain-profile` file at `paths.domain`: the platform decisions, the **steering block** (confirmed `vocabulary` entries, bounded contexts, `profile.knowledge` references the later stages must cite), the researched recommendations with their closed questions |
| What does not cross | any module-level content (policies, stories, requirements); any ID (this stage owns none) |
| Clauses | C1.1 the file exists · C1.2 no open `[QUESTION]` remains (dialogue closed) · C1.3 every `profile.languages.all` language present when `require_all` |
| Violation | C1.1/C1.2 CRITICAL — `P-1` refuses to start; C1.3 MAJOR |

## C2 — project registry → inception

| | |
|---|---|
| Owner | `P-1` (once per platform) |
| Consumer | `P0` and, read-only, every later stage |
| What crosses | `project-registry` at `paths.platform` covering every category of [REGISTRY-SCHEMA.md](REGISTRY-SCHEMA.md) (module index, entity ownership, shared entity declarations, dependency indexes, status, event history) |
| What does not cross | module artifacts, policies, requirements, any ID other than registry rows (the registry defines no atom) |
| Clauses | C2.1 exists · C2.2 all registry categories present in substance (compliance map) · C2.3 defines no ID atom |
| Violation | C2.1 CRITICAL; C2.2/C2.3 MAJOR |

## C3 — inception → PRD

| | |
|---|---|
| Owner | `P0` (`questions: allowed`, dialogue lane) |
| Consumer | `P0.5` |
| What crosses | `platform-summary` (tiering, module map from `vocabulary.keyword_map`), `module-registry` (module scope, entity candidates, lookup candidates), `business-policies` with `POL` IDs |
| What does not cross | user stories, requirements, entity/rule/screen IDs, data structure, technology choices beyond `profile.stack` |
| Clauses | C3.1–C3.3 the three artifacts exist · C3.4 only `stages[P0].owns_ids` atoms are defined · C3.5 no open questions · C3.6 languages · C3.7 every `POL` in `business-policies` is registered in `module-registry` and vice versa |
| Violation | C3.1–C3.5 CRITICAL; C3.6/C3.7 MAJOR |

## C4 — PRD → SRS (human PRD approval in between)

| | |
|---|---|
| Owner | `P0.5` — the **last** stage where questions are allowed |
| Consumer | `P1`, blocked by gate `prd-approval` (`factory.gates`, `type: human-approval`) |
| What crosses | `prd` with `US` IDs; every `US` traces to ≥1 `POL`; priority and success metric per story (optional) |
| What does not cross | enforceable rules, requirements, entities, screens, APIs — a story is a NEED, not a specification; anything requirement-shaped in the PRD is a boundary violation |
| Clauses | C4.1 exists · C4.2 the approval is recorded for `prd-approval` · C4.3 only `US` defined · C4.4 `US` → `POL` ≥1 · C4.5 no open questions · C4.6 languages |
| Violation | C4.1/C4.2/C4.3/C4.5 CRITICAL — `P1` cannot start; C4.4/C4.6 MAJOR |

## C5 — SRS → database

| | |
|---|---|
| Owner | `P1` (`requirement_format: EARS`) |
| Consumer | `P2` (and every later stage: the SRS is the functional ceiling) |
| What crosses | `srs` + `registry-srs`: `REQ` (one EARS pattern each, `factory.ids.ears.patterns`) tracing to `US`; `AC` (Given / When / Then) tracing to `REQ`, ≥1 per `REQ`; `ENT` with kind from `vocabulary.entity_kinds`; `RULE` tracing to `REQ`; screen inventory |
| What does not cross | column names, types, DDL, endpoints, UX layout, technology — the SRS says *what*, never *how* |
| Clauses | C5.1 exists · C5.2 every `REQ` matches an EARS pattern · C5.3 `REQ` → `US` · C5.4 every `REQ` has ≥1 `AC` · C5.5 `AC` → `REQ` · C5.6 `RULE` → `REQ` · C5.7 only `stages[P1].owns_ids` defined · C5.8 srs ↔ registry-srs agree · C5.9 no questions · C5.10 languages · C5.11 sequences continue the previous version · C5.12 every `RULE` declares a `Data source` — the `ENT.field` values the check **reads**, or the explicit `DEFERRED` marker |
| Violation | C5.1/C5.2/C5.4/C5.7/C5.9/C5.11/C5.12 CRITICAL; the rest MAJOR |

`RULE` → `REQ` (C5.6) says the rule is *wanted*; C5.12 says it is *enforceable*. A rule
whose statement leans on data no entity declares ("a module-declared X", "a configured Y")
passes every shape check — it has a trace, it gets an error code, it gets an enforcing
endpoint — and can never fire, because nothing in the module can record the value it reads.
`DEFERRED — no declaration surface in this version` is a truthful output; a silently
unenforceable rule is not.

## C6 — SRS + database → backend execution plan

| | |
|---|---|
| Owner | `P1` + `P2` |
| Consumer | `P3.1` |
| What crosses | `db-script` + `registry-db`: `DBF` tracing to `REQ`/`ENT`; `XM` tracing to `REQ` with type and state per [XM-PROTOCOL.md](XM-PROTOCOL.md); shared-entity references by the owner's `ENT`; plus the SRS set of C5 |
| What does not cross | into the plan: column names, DB types, table names — the plan binds by `DBF` ID only; into `db-script`: business rules (cited by `RULE`), endpoints |
| Clauses | C6.1 exists · C6.2 `DBF` → `REQ`/`ENT` · C6.3 `XM` → `REQ` · C6.4 only `stages[P2].owns_ids` defined · C6.5 db-script ↔ registry-db agree · C6.6 every `ENT` has ≥1 `DBF` · C6.7 no questions · C6.8 sequences continue · C6.9 every `RULE`'s `Data source` field is bound to a column by the db-script (or is `DEFERRED`) |
| Violation | C6.1/C6.4/C6.7/C6.8/C6.9 CRITICAL; the rest MAJOR |

## C7 — backend execution plan → split / deliver

| | |
|---|---|
| Owner | `P3.1` (`track: backend`, `plan: exec`) |
| Consumer | `gov.py split` / `deliver` (tools lane); the pass-1 gate reads it first |
| What crosses | `backend-execution-plan` wrapped in markers per [MARKER-PROTOCOL.md](MARKER-PROTOCOL.md) — every `PHASE`/`SUB`/`API`/`XM` block carries `traces=`; `API` → `REQ` + `DBF`; `XM` blocks mirror `registry-db` entries with execution state; `registry-exec-be` with `API`/`QR` |
| What does not cross | DDL or column definitions (bound by `DBF`), test cases (standalone `test-gen`), any content for the frontend track |
| Clauses | C7.1 markers valid for `track: backend`, `plan: exec` (parser clean, phase keys canonical, split rules honoured) · C7.2 every block carries `traces` · C7.3 `API` → `REQ`+`DBF` · C7.4 plan ↔ registry-exec-be agree · C7.5 plan `XM` set == registry-db `XM` set · C7.6 every `REQ` is covered by ≥1 `API` or `DBF` · C7.7 only `stages[P3.1].owns_ids` defined · C7.8 no questions · C7.9 sequences continue · C7.10 every `DBF` names the same physical column here as in the db-script · C7.11 every emitted error code is an instance of the declared format, and no other format is declared · C7.12 every id of another module resolves in that module's own registry · C7.13 every cited `ADR` file exists · C7.14 every path the manifest emits resolves |
| Violation | C7.1/C7.7/C7.8/C7.9/C7.10/C7.12/C7.13/C7.14 CRITICAL; the rest MAJOR |

C7.1–C7.9 check that references are *shaped* right. C7.10–C7.14 check that they
**resolve**: that two artifacts agree on a value, that a declared format describes the
values actually emitted, that a cited file exists, that a cross-module dependency is on
something the target module really produces, and that a generated path points at something.
Every defect a shape-only pass has ever let through this interface was of the second kind,
and the plan's own prose self-check (`ALIGN`) reported PASSED for all of them — which is why
these are mechanical clauses here and not a checklist line there.

## C8 — real API docs (consumer-repo input) → frontend

| | |
|---|---|
| Owner | the backend repo (`factory.inputs.api-docs`, fetched by `gov.py fetch-inputs` into `paths.module.inputs_dir`) |
| Consumer | `P3.2` — pass 2 cannot start without it (`passes."2".required_inputs`) |
| What crosses | the implemented endpoint contracts keyed by `API` ID (method, path under `profile.stack.backend.api.base_path`, request/response shapes, error envelope) |
| What does not cross | the planned endpoint text of `backend-execution-plan` — the frontend never trusts a pre-implementation contract; nothing about UI |
| Clauses | C8.1 the input exists · C8.2 every `API` in api-docs is registered in `registry-exec-be` · C8.3 every `API` in `registry-exec-be` appears in api-docs (a missing one is listed for an ADR) |
| Violation | C8.1 CRITICAL — gate closed; C8.2/C8.3 MAJOR |

## C9 — frontend design + execution plan → split / deliver

| | |
|---|---|
| Owner | `P3.2` (`track: frontend`, `plan: exec`) |
| Consumer | `gov.py split` / `deliver`; the pass-2 gate reads it first |
| What crosses | `flow-diagram`, `ui-ux-spec` with `UXD` → `REQ`/`AC` and `SCR` → `REQ`/`UXD`; `frontend-execution-plan` whose phase blocks carry `traces` and cite only `API` IDs present in api-docs; `registry-exec-fe`. When `profile.conventions.composite_screen` is true a screen group is one `SCR` (scored via `profile.review.extra_checks`) |
| What does not cross | fields, rules or permissions not in the SRS; endpoints not in api-docs; backend content; a UI implementation of any kind (a mockup is a design artifact, never a build) |
| Clauses | C9.1 markers valid for `track: frontend`, `plan: exec` · C9.2 every `PHASE`/`SUB` block carries `traces` · C9.3 `UXD` → `REQ`/`AC` · C9.4 `SCR` → `REQ`/`UXD` · C9.5 every `API` cited by the plan is defined in api-docs · C9.6 every `UXD` is referenced by a plan block (this is where a UX decision closes) · C9.7 every `SCR` is referenced by a plan block · C9.8 plan ↔ registry-exec-fe agree · C9.9 only `stages[P3.2].owns_ids` defined · C9.10 no questions · C9.11 sequences continue |
| Violation | C9.1/C9.5/C9.9/C9.10/C9.11 CRITICAL; the rest MAJOR |

## C10 — acceptance criteria → test generation (standalone)

| | |
|---|---|
| Owner | `P1` (`AC`), `P2` (`XM`, via `registry-db`/`backend-execution-plan`), `P3.2` (`UXD`, via `registry-exec-fe`/`frontend-execution-plan`) |
| Consumer | `test-gen` (`factory.standalone`, `derives_from: AC`; integration scope also derives from `XM`/`UXD` — `ids.atoms.TC.traces_to`) |
| What crosses | every `AC` (Given / When / Then), its `REQ`, the exec plans' `API`/`SCR` blocks for placement; at `--modules`/`--scope project`: the `XM` blocks of each selected module's `backend-execution-plan` (+ `registry-db`) and the `UXD` references of each selected module's `frontend-execution-plan` (+ `registry-exec-fe`) — only atoms that actually link two *selected* modules are eligible; `profile.stack.testing` decides framework neutrality |
| What does not cross | implementation detail, framework code, gate status — test plans never gate the core; a fabricated integration flow with no backing `XM`/`UXD` |
| Clauses | C10.1 every `TC` → `AC`/`XM`/`UXD` (≥1) · C10.2 every `AC` has ≥1 `TC` · C10.3/C10.4 test plans' markers valid for `plan: test` per track · C10.5 only `TC` defined · C10.6 `test-execution-manifest` exists when `profile.stack.testing.manifest` |
| Violation | C10.1/C10.3/C10.4/C10.5 CRITICAL for the standalone run only; C10.2 MAJOR; C10.6 MINOR |

## C11 — real API docs (+ manifest) → API verification (standalone)

| | |
|---|---|
| Owner | the backend repo (api-docs) and `test-gen` (manifest, optional) |
| Consumer | `api-verify` (`factory.standalone`, post-implementation) |
| What crosses | api-docs as in C8; the manifest when produced (full tier); `profile.stack.backend.api` conventions for parsing envelope, paging and errors |
| What does not cross | any analysis artifact as a substitute for real docs; any verdict into the pass gates |
| Clauses | C11.1 api-docs exists · C11.2 manifest exists (absent → degraded tier, recorded) · C11.3 the report artifact is written |
| Violation | C11.1 CRITICAL for the standalone run; C11.3 MAJOR; C11.2 MINOR |

## C12 — delta version (change manifest) → every stage

| | |
|---|---|
| Owner | `gov.py version --new` creates the folder; the first stage of the delta writes `paths.module.change_manifest` |
| Consumer | every stage of the delta version, `gov.py state`, `gov.py split`, the gates |
| What crosses | the change set `CS` ID; per artifact: ADDED / MODIFIED / REMOVED IDs; change type ADDITIVE or BREAKING; the frozen previous version as read-only baseline (format in [VERSIONING.md](VERSIONING.md)) |
| What does not cross | any edit to the previous version's files; re-emitted unchanged artifacts (only deltas live in `vN/`) |
| Clauses | C12.1 the manifest exists for any version > 1 · C12.2 manifest consistency: ADDED IDs are new and continue sequences, MODIFIED IDs exist in the previous state, REMOVED only under BREAKING (which stops the pass with a BLOCKED ADR) · C12.3 every sequence continues the previous version |
| Violation | all CRITICAL |

---

## 13. Clause vocabulary — what `gov.py analyze` implements

| `check` | Meaning | `args` |
|---|---|---|
| `exists` | the artifact (`artifact`, resolved through `_state/`) or fetched input (`input`) is present and non-empty; `when` makes the clause conditional on a config expression | `artifact` \| `input`, `when?` |
| `no-questions` | no `[QUESTION]` block or unresolved dialogue marker remains in the stage's artifacts | `stage` \| `artifact` |
| `languages` | when `profile.languages.require_all`, every language of `profile.languages.all` is present in the artifact's headings and ID labels | `stage` \| `artifact` |
| `ids-owned` | the artifacts define IDs only of the atoms in `stages[stage].owns_ids` (`defines: []` = none); any other prefix defined = violation | `stage` \| `artifact`+`defines` |
| `ids-continue` | for every atom, the sequence has no gap and, for version > 1, starts after the previous version's highest ID | `stage` \| `scope: version` |
| `traces` | every ID of kind `from` (or every marker block of the listed `blocks` in the artifact `from`) carries `traces` to ≥`min` IDs of **each** kind in `to` (`mode: all`, the default); with `mode: any`, ≥`min` in **at least one** listed kind suffices (e.g. a `TC` may trace to `AC`, `XM` or `UXD`); with `defined_in`, every cited ID of kind `to` must be defined in that artifact | `from`, `to?`, `blocks?`, `min?`, `mode?`, `defined_in?` |
| `orphans` | every ID of `kind` is referenced by ≥`min` IDs/blocks of the kinds or artifacts in `referenced_by` | `kind`, `referenced_by`, `min` |
| `ears` | every ID of `kind` has a statement matching one of `patterns` | `kind`, `patterns` |
| `registry-agree` | the set of IDs of `kinds` defined in `artifact` equals the set registered in `registry` (`direction` restricts to one inclusion); with `categories: all`, every category of [REGISTRY-SCHEMA.md](REGISTRY-SCHEMA.md) is mapped in the registry's compliance map | `artifact`, `registry`, `kinds` \| `categories`, `direction?` |
| `markers` | the toolkit parser reports no structural or semantic error for the artifact under `track`/`plan` (`factory.markers` + `profile.tracks`) | `artifact`, `track`, `plan` |
| `manifest` | the change manifest is well-formed and consistent with the previous state (see C12.2) | `artifact` |
| `gate-approved` | the orchestrator holds an approval record for `gate` for this module version | `gate` |
| `value-agreement` | for every id of `kind`, the physical name (column / object) that `binding` declares for it and the one each artifact in `against` names for it are the same string; an artifact that names none for that id is skipped | `kind`, `binding`, `against`, `require_binding?` |
| `code-format` | every runtime code the artifact emits is an instance of the format at the profile address `format`, and the artifact declares no *other* format string for those codes (a declaration maintained as free text drifts from its values) | `artifact`, `format`, `require_declaration?` |
| `data-source` | every record of `kind` carries a `label:` line naming where the data its check **reads** comes from — ≥1 id of `resolves_to` (and, with `bound_in`, every `ID.field` it names is bound to a field there) — or the explicit `deferral` marker | `kind`, `label`, `resolves_to`, `deferral?`, `bound_in?` |
| `xref-resolve` | every id belonging to *another* module that the artifact cites is defined in that module's own artifacts; an unknown module code, or a module with no artifacts yet, is a finding of its own | `artifact`, `kinds?` |
| `refs-exist` | every id of `kind` cited anywhere in the module has the file it is cited as, at `dir`/`<MOD>`/`naming[file_pattern]` | `kind`, `dir`, `file_pattern`, `per_module?` |
| `paths-resolve` | every path-shaped string in each generated index (`files`, by `paths.module.*` key) resolves to something that exists, relative to the index's own directory | `files`, `required?` |

Severity semantics are `factory.review` + `factory.gates[*].requires_analyze`:
a gate opens only with zero CRITICAL; MAJOR findings return REVISE; MINOR
findings are recorded in the gate record. The report lives at
`paths.module.analyze_report`.
