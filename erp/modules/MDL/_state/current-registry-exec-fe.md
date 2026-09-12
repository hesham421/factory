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

Two screens, and every `sub_bearing` phase splits per screen all the same: F1, F2, F3 and F4
carry one `SUB` per `SCR-*` — 8 SUB blocks — with every SUB id phase-qualified. The
`split_threshold` of `SCR >= 5` that these phases used to carry was removed from
`profiles/erp.yaml` on 2026-09-12, so a module's package shape no longer depends on how many
screens it happens to have.

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
split per screen (8 SUB), ALIGN-FE stamped by the orchestrator, 7 ADRs"
══════════════════════════════════════════════════════════════════
