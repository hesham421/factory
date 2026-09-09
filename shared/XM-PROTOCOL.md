# XM PROTOCOL — cross-module dependency lifecycle

```
Doc            : shared/XM-PROTOCOL.md
Role           : how a dependency on another module is declared, typed, tracked, resolved and handed over
Loaded by      : the stages that own or reference the XM atom (ids.atoms.XM.owner and the backend exec stage), gov.py analyze, reviewers/pass-review.md
Generated parts: none (atoms via GOVERNANCE-CORE.md RENDER:ids; indexes via REGISTRY-SCHEMA.md)
Links          : GOVERNANCE-CORE.md · REGISTRY-SCHEMA.md · ARTIFACT-CONTRACTS.md (C6, C7, C12) · VERSIONING.md
```

## 1. What an XM is

An `XM` is a dependency of the **consuming** module on data owned by another
module. It is declared by the consuming module, in the artifact of the stage
that owns the atom (`factory.ids.atoms.XM`), citing the requirement that needs
it (`traces_to`). It is a backend concern only: the marker kind `XM` is limited
to the tracks in `markers.kinds.XM.tracks`. A frontend-visible cross-module
display of data is a **UXD** (owned by the frontend stage), a separate atom and
namespace that never merges with `XM` and closes when the frontend plan
references it (contract C9.6).

## 2. Declaration

Every `XM` block/row carries:

| Field | Value |
|---|---|
| id | `XM` atom per `factory.ids.pattern`, module part = the consuming module |
| type | `HARD-FK` — a physical constraint on the owner's table; `SOFT-READ` — an application-layer read without a constraint (governed exactly like a hard one; untracked reads are a finding) |
| target module | one of `profile.vocabulary.module_prefixes`, never the consuming module |
| target entity | the **owner's** `ENT` ID (and the owner's `DBF` when a column is named). A consumer never re-creates the entity, never assigns it a new ID, never adds fields to it |
| traces | ≥1 `REQ` of the consuming module (C6.3) |
| state | §4 |

Shared entities: an entity declared SHARED in the project registry
([REGISTRY-SCHEMA.md](REGISTRY-SCHEMA.md), shared-entity declarations) has
exactly one canonical owner; two modules owning the same entity is a CRITICAL
finding.

**Tier rule.** Whether module A may depend on module B follows the tiering in
`platform-summary` (a lower tier never depends on a higher one). When the
profile declares `profile.knowledge.files`, the tiering is derived from those
files; otherwise it follows `profile.vocabulary.bounded_contexts` and any
deviation is an ADR.

## 3. Where XMs are tracked

| Level | Where | Owner |
|---|---|---|
| structural detail (target, type, traces) | `db-script` XM register + `registry-db` | the DB stage of the consuming module |
| execution detail (state, blocked `API`s, workaround, unblock condition) | the `XM` marker block in `backend-execution-plan` | the backend exec stage; the block's ID set must equal the registry's (C7.5) |
| platform view (all modules) | project registry, cross-component dependency index | `gov.py` registry step |

The execution block never restates structural detail (table or column names);
it binds by ID (C6, "what does not cross").

## 4. States inside the factory

```
DECLARED ──► READY ─────────────────────► DELIVERED ──(consumer repo)──► CLOSED
    │           ▲                              ▲
    └──► DEFERRED ──(resolution event)─────────┘
              │
              └──► WAIVED  (terminal; a re-appearing need gets a new XM)
```

| State | Meaning | Set by |
|---|---|---|
| DECLARED | exists in the consuming module's `db-script` | DB stage |
| READY | the target entity exists in a committed `db-script` of the target module in this factory | DB stage or a resolution event |
| DEFERRED | the target is not yet available; the plan block carries a workaround and an unblock condition | backend exec stage |
| DELIVERED | the package containing the block was delivered (`gov.py deliver`, branch per `naming.delivery_branch`) — the **last state the factory sets** | tools lane |
| CLOSED | the dependency is physically applied in the implementation. Belongs to the **consumer repo**; the factory never sets it, never waits for it, never gates on it | consumer repo |
| WAIVED | a human decision (ADR) retired the dependency | ADR at a human decision point |

A pass gate may open with DEFERRED XMs as long as every one has a workaround
and an unblock condition; it may not open with a DECLARED XM that has no
execution block.

## 5. Resolution event

A resolution event is raised when a dependency **target changes version**:
the target module commits a `db-script` (new module or new version) that adds
or amends the target entity, or a SHARED entity's owner amends it. `gov.py
state`/`analyze` detect it from the project registry's dependency index and
the version folders ([VERSIONING.md](VERSIONING.md)); nothing is announced by
hand.

Event record (one per consuming module per triggering version, appended to
the project registry's event history and mirrored as an ADR in the consuming
module):

```
Trigger            : target committed <artifact> v<N> | shared entity amended
Initiating module  : <MOD> v<N>
Consuming module   : <MOD>
Affected XM IDs    : <list>
Change summary     : what became available / what changed (by ENT/DBF ID)
Required action    : re-evaluate each affected XM; DEFERRED → READY or record why not
Status             : OPEN → ACKNOWLEDGED → RESOLVED | WAIVED
```

Response, executed in the consuming module's next version (a delta version,
contract C12):
1. **acknowledge** — the DB stage reads the event; status ACKNOWLEDGED.
2. **evaluate** — per XM: available now → READY; still missing → stays
   DEFERRED with an updated unblock condition; amended entity → impact ADR
   (breaking → BLOCKED, the pass stops).
3. **update** — `registry-db` state, the plan's `XM` block, the registry
   index; the change manifest lists the XM as MODIFIED.
4. **resolve** — status RESOLVED in the event history.

An OPEN event that the consuming module's next gate has not acknowledged is a
MAJOR finding at that gate.

## 6. Waiver

A waiver needs a human decision at a decision point, recorded as an ADR
naming the XM, the reason (dependency no longer valid, target cancelled,
architectural decision) and the approver. The registry index moves the XM to
WAIVED; it is never re-activated.
