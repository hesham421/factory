# Prompt — round 2: close the completeness blind spot

> Hand this to a session working **inside `/Users/ezzat/factory`**. It is self-contained:
> every claim below carries its own evidence, so there is no companion document to read first.
> The earlier round's prompt (`FACTORY-FIX-PROMPT.md`) and diagnosis
> (`FACTORY-DEFECT-ANALYSIS-AND-FIX-PLAN.md`) describe fixes that are **already applied** —
> read them only for the conventions they establish, not as outstanding work.

---

## Copy everything below this line into the session

---

You are working on the Governance Factory (`factory.yaml`, `profiles/`, `engines/`, `shared/`,
`governance-tools/`). Your job is a second round of root-cause fixes.

### Where this round came from

A consuming repository built one complete backend module end to end from factory-produced
documents — 14 entities, 32 endpoints, seven execution phases. The build surfaced a long list of
defects **that the factory's own generated self-check had certified as clean**: the plan literally
asserted `RESULT PASSED ✓ — 0 findings` before a line of code existed, and an audit at the end of
implementation found four of its rows demonstrably false.

The full defect record is 24 entries in that repo's
`governance/modules/FIN/execution-state.json` → `api_doc_gaps[]`. You do **not** need that repo to
do this work, and you must not modify it. The evidence you need is inline below.

### The finding that organises everything

The factory has 22 machine checks (`governance-tools/analyze.py`, `CHECKS` dict). Read them.
Every one of them checks **shape and reference integrity**: ids exist, traces resolve, markers
balance, registries agree, paths resolve.

**Not one checks whether the planned system is complete enough to function.** Nothing asks: does
this declared total match the rows beneath it? Can this declared HTTP status actually be produced?
Does this required column have anything that writes it? Does this declared operation have an
endpoint? Does this lookup key have a seed? Every blocking defect in that build fell into exactly
that blind spot.

So this round adds a **completeness** dimension to a factory that currently only has a
**consistency** dimension. Keep that framing: it is the reason these fixes generalise.

---

## The one rule that governs every change

`FACTORY-FIX-PROMPT.md` §"The one rule" states it and it is unchanged — read it there in full and
obey it exactly. In short: this factory is a meta-tool for **any** project, domain or stack. No new
literal, no new stack assumption, no new domain assumption, no check that knows one profile's
vocabulary. Values arrive from `factory.yaml` (factory facts) or a profile (project facts), and a
check's vocabulary arrives through its contract clause's `args`.

**The harness that proves it:** `governance-tools/tests/test_agnostic.py` drives the toolkit
through a toy profile from an unrelated domain (an outpatient clinic). For every fix below, extend
that toy profile so it exercises the new behaviour, and treat "passes under ERP but not under the
toy" as a literal in disguise. Passing `test_agnostic.py` is stronger evidence than any grep.

Also binding: `PROJECT-INSTRUCTIONS.md` §"Definition of done" — root cause not symptom, no new
hardcoding or duplicated mechanism, `gov.py lint` clean, `pytest governance-tools/tests -q` fully
green, and the steps a user takes must be the same or fewer than before.

### Scope boundary — read this twice

You may change: `engines/**`, `shared/**`, `profiles/**`, `governance-tools/**`, `factory.yaml`,
`reviewers/**`.

You may **not** change **any generated analysis artifact**. Concretely: nothing under
`erp/modules/**` — no SRS, no db-script, no execution plan, no `_state/`, no test plan, no
registry instance. Those are *output*. Editing an output to make a check pass is the precise
failure mode this round exists to prevent: it makes the artifact lie instead of making the
generator right. If a fix would require touching one, you have found a generator bug — fix the
generator and report that the existing artifacts are now stale, rather than patching them.

The same applies to the consuming repository at `/Users/ezzat/my project/backend`. Do not touch it
at all, for any reason.

---

## What already works — do not "fix" these

Four things were hypothesised as defects and then **refuted by evidence**. Re-investigating them is
wasted effort; actively "fixing" them would be damage.

1. **The authored-verdict reconciliation already exists and works.** `analyze.py`'s
   `_c_verdict_agrees` (marked `reads_report = True`, evaluated after every finding-producing
   clause), contract clause C7.15, and `profiles/erp.yaml`'s `self_check` block together stop a
   plan claiming fewer findings than the machine produced. The residual problem is **not** the
   verdict line — see G13, which is about the block's *rows*, not its verdict.

2. **XM extraction is not foreign-key-driven.** `engines/P2/references/ENGINE.md:219-222` sources
   XM rows from the SRS's consumed entities, from rules that join by code, **and from APIs that
   read another module's data**; `shared/XM-PROTOCOL.md:29` makes an untracked read a finding.
   Behavioural reads are already in scope. The real cause is structural and is G8.

3. **Split duplication already has a detector.** `governance-tools/toolkit/splitter.py:186-203`
   digests every plan block against its split copy (`_digest` at `:91`, the comparison and the
   `mismatched` list at `:202-203`) and reports mismatches, using the algorithm the profile names
   in `markers.rules.verify`. It simply runs once, at split time. That is G9 — make it re-runnable,
   do not design a new mechanism.

4. **Free choices in templates are nearly extinct.** Grepping `engines/`, `shared/` and `profiles/`
   for an A-or-B offer to the author returns exactly one remaining instance (G6). The pattern is
   not a broad template disease; do not go hunting for more than the one named.

Two further items were assessed and **deliberately dropped** — do not implement them:

- Detecting a cross-reference that cites the *wrong* sibling id (a QR row pointing at another QR).
  It is a semantic mis-citation; no mechanical check can distinguish it from a correct one.
- Mapping every state-machine transition to a rule owner. The defect it was meant to catch had a
  semantic root (a wrong transition was *chosen*), which a mapping check would have passed.

---

## The fixes, in descending expected value

Each is: **evidence → why nothing caught it → the layer → done when.**

Implement in this order. Each is independently shippable; do not batch them into one commit.

---

### G1 — `count-agrees`: a declared total must equal the rows beneath it

**Evidence.** `engines/P3.1/references/ENGINE.md:184-186` asks the author for `<n>` in four
separate places, and the plan's §4 and §7 carry hand-counted totals. In the delivered module one
file asserted both "147 DBF" and "Total: 146"; another line certified "12 columns note XM-FIN-001"
where the real number was 16. No check in the 22 counts anything.

**Why nothing caught it.** `manifest` validates a manifest's *shape*; `registry-agree` compares two
registries' *membership*. Neither ever counts.

**Layer.** New check in `analyze.py` + a clause per artifact in `shared/ARTIFACT-CONTRACTS.md`.

**Design notes.** The check must learn, from its clause `args`, how to find a declared total and
the row set it heads — a pattern for the total and the table or block it governs. It must not know
the word "DBF", "manifest" or any profile's block names. Where a total is stated in more than one
file, all of them must agree with the rows *and* with each other.

**Done when.** A toy-profile artifact with a deliberately wrong total fails; with a right one
passes; and the check names both numbers in its message.

---

### G2 — a declared HTTP status must be one the platform can produce

**Evidence.** The Error Catalog's format (`engines/P3.1/references/ENGINE.md:422`) has a free
`HTTP` column. `profiles/erp.yaml:120` declares `error_code_format: "{MOD}-{http}[-{SLUG}]"`, and
the `code-format` check validates the *code string's shape* — so `FIN-503` passed. The consuming
platform's status enum has no 503, so that catalog row could never be raised by any code; it was
struck during implementation.

**Why nothing caught it.** The profile declares a code *format* but never the *set* of statuses the
platform can emit, so there is nothing to check membership against.

**Layer.** Profile key (`stack.backend.api.http_statuses`, with `_schema.yaml` support) + extend
the existing `code-format` check — do not add a second check.

**Done when.** A catalog row whose `{http}` is outside the declared set is a finding; a profile that
declares no such set simply skips the membership half (an optional convention, per C5).

---

### G3 — required data must have a writer

**Evidence.** Two defects, one shape. A column was added as semantically required but **no endpoint
sets it**, so the endpoint depending on it could never succeed on a fresh deployment. Separately, a
soft-delete flag existed that **no operation flips**.

**Why nothing caught it.** The plan already carries both halves — the DB Alignment Manifest lists
every column, and each API block lists its request fields — but nothing joins them.

**Layer.** New check in `analyze.py` + contract clauses.

**Design notes.** For every column the manifest marks required and not system-assigned, there must
be at least one API whose request includes it, or an explicit exclusion token saying why not
(system-generated, derived, seeded). The audit-field and PK exclusions must come from profile keys
that already exist (`db.naming.audit_fields`, the PK convention), never from a hardcoded list.
This absorbs part of G5 — a marker column with no writer and no seed is the same defect twice.

**Done when.** The toy profile can express a required column with no writer and the check finds it.

---

### G4 — a declared operation must resolve to an endpoint

**Evidence.** `engines/P3.1/references/ENGINE.md:176` gives the ENTITY REGISTRY an `operations`
column, and P1's screen requirements carry their own `Operations:` list. The API REGISTRY is at
`:178`. Nothing compares them in either direction. Results in the delivered module: two operations
were specified and never built (nobody could deactivate a dimension through the API), and the
security matrix carried ✓ cells with no endpoint and no permission behind them.

**Why nothing caught it.** `profiles/erp.yaml:183`'s ERP-4 and the plan's own self-check both run
**plan → matrix** only. The reverse direction is unchecked, and the entity-registry direction is
unchecked entirely.

**Layer.** New check + contract clauses. One check, both directions.

**Design notes.** Every operation word declared for an entity or a screen resolves to an `API-*`
row, **and** every matrix cell marked present resolves to an API and a permission name. The
operation vocabulary comes from the profile (`vocabulary`, `conventions.security_model.actions`),
never from a literal list in Python. This subsumes the permission-matrix direction — do not write a
separate matrix check.

**Done when.** Both directions fail on a toy artifact seeded with each defect.

---

### G5 — plan the bootstrap data, then check it exists

**Evidence — the largest hole in the factory.** Three separate blocking defects, one root cause:

- `engines/P2/references/ENGINE.md:176-180` seeds lookup values **only into tables this module's
  own script creates**. Under `conventions.lookups` (`profiles/erp.yaml:154`) the lookup tables
  belong to a *different* module — the normal case — so that block is empty and **nothing, anywhere
  in the pipeline, ever seeds them**. The delivered module was unusable on a fresh database: its
  first create call failed validating a lookup code against an empty table.
- `engines/P3.1/references/ENGINE.md:399` seeds screen and permission rows but has **no concept of
  a grant**. `conventions.security_model` (`erp.yaml:147-151`) declares a page registry, a
  permission pattern and actions — but no grant target. Registration is not a grant: every endpoint
  answered 403 to every caller including the administrator.
- A marker column that must be set for an endpoint to work was planned with no seed and no writer
  (the G3 half).

Grep `engines/` and `shared/` for `grant`, `bootstrap` or `fresh deploy`: **zero module-level
hits.**

**Why nothing caught it.** The factory plans *structure* and *behaviour* and has no artifact
section for *the data that must exist before any of it works*.

**Layer.** ENGINE (a BOOTSTRAP DATA section — in P3.1's R7 security role and P2's seed block) +
profile (`security_model.grant_target`, or whatever the generic shape turns out to be) + a new
`bootstrap-complete` check.

**Design notes.** The section must state, per module: every lookup key the SRS declares this module
owns has a named seed source; every permission the matrix declares has a named grant target; every
required-but-unwritable column has a seed source. The check then asserts the section covers what
the other registries declare. Keep the profile key generic — "the thing a permission is granted to"
is a role in this profile but must not be named `role` in the engine if the schema can avoid it.

**Done when.** A toy module that owns a lookup key with no seed source fails `bootstrap-complete`;
one that declares a source passes; and `test_agnostic.py` exercises the toy's own grant vocabulary.

---

### G6 — remove the last free choice

**Evidence.** `engines/P3.1/references/ENGINE.md:377`: `Interface : DB foreign key | REST call`.
The delivered module's plan chose "REST call" for a platform that is a single deployable where
modules communicate by in-process interface injection. That single wrong word propagated into six
files, a planned HTTP client, and an error-catalog row for a network failure that cannot occur.

**Why nothing caught it.** Same mechanism as the domain-placement defect fixed in round 1: a
template that offers the author a menu gets an answer that contradicts the profile's own
architecture, and no check knows what the right answer was.

**Layer.** Profile key + `_schema.yaml` + render the declared value verbatim. **Follow the
`conventions.domain_behaviour_placement` fix exactly** — it is the reference implementation for
this pattern: an optional convention key, a guarded render with an else-branch for profiles that
declare nothing, a row in `shared/GOVERNANCE-CORE.md` §8, and a `review.extra_checks` entry.

**Done when.** The rendered line states the profile's declared mechanism and offers the author no
choice; a profile declaring nothing still renders a sensible instruction.

---

### G7 — every catalogued query must be referenced

**Evidence.** `engines/P3.1/references/ENGINE.md:479` reads, in full:

```
QRC (§5)  every API with a DB operation has a QR │ every QR carries the agent-reference warning │ no join for lookup labels │ exact generation object named
```

Four assertions, all pointing one way: API → QR, plus three about a QR's own wording. **None asserts
that a catalogued query is referenced by anything**, so a query nobody uses is invisible to the
self-check and to every machine check.

**Why nothing caught it.** One-directional by construction.

**Layer.** One clause in `shared/ARTIFACT-CONTRACTS.md` using the **existing** `orphans` check —
no new Python. Note the other half of this defect (dead repository methods in the delivered code)
is post-implementation and belongs to the consuming repo's own validation, not here.

**Done when.** An unreferenced catalogued query is a finding.

---

### G8 — let a later stage mint a cross-module row

**Evidence.** A real cross-module dependency — one module's business rule reading another module's
data through its published interface — was never registered, because the dependency is *introduced*
by P3.1's own security role, **after** P2 has frozen the cross-module register. Contract clause
C7.5 requires the plan's XM set to **equal** the registry's, so the plan could not legally add it.

**Why nothing caught it.** The check fired correctly; the contract forbade the right answer.

**Layer.** `shared/ARTIFACT-CONTRACTS.md` — relax C7.5 from equality to superset, and add a clause
that any row a later stage mints is back-registered into the owning registry.

**Done when.** A P3.1-minted row passes C7.5 and fails if it is not back-registered.

---

### G9 — make the split verification re-runnable

**Evidence.** `governance-tools/toolkit/splitter.py:196-212` already digests each plan block against
its split copy. It runs once, at split. Post-split hand edits then drift silently, and did.

**Layer.** Tooling only — expose the existing digest comparison as a command that can be re-run,
and require it where a consuming repo reconciles. No new concept, no new check.

**Done when.** The comparison can be invoked independently of a split and reports drift.

---

### G10 — ask about concurrency once, per mutating endpoint

**Evidence.** The only occurrence of "idempotency" in the whole factory is
`engines/P3.1/references/ENGINE.md:383`, inside the *cross-module* contract. The API block
(`:332-346`) and the query-catalog entry (`:216-230`) carry a `Transaction` field but nothing about
concurrency. Two races shipped: a unique document-number allocated from a read-then-write, and a
guard that two parallel requests could both pass.

**Layer.** ENGINE template only — a `Concurrency` line in the API block and a `Locking` field in
the query-catalog template, required for any endpoint that allocates a unique value or does a
read-then-write.

**Accept that this is not mechanically checkable.** It is a template prompt plus a reviewer row in
`reviewers/pass-review.md`. Do not invent a check that pretends to verify it.

**Done when.** The rendered API block asks the question, and the reviewer has a row for it.

---

### G11 — a channel for findings that belong to no module

**Evidence.** Three real defects found during the build were platform-wide, not module-scoped: a
forbidden-response envelope that never reaches the wire as the documented code, a shared audit
field whose declared length exceeds the physical column in every module, and a shared exception
type that cannot carry more than one error. Every module-scoped worker correctly said "not mine to
settle" — and nothing escalated them anywhere.

**Layer.** The project registry — a platform-findings category, so a module-scoped stage can record
a finding it must not fix.

**Done when.** A stage can record a platform finding without it being mistaken for a module gap,
and the reviewer sees it.

---

### G12 — a quotation carries its source

**Evidence.** A generated artifact quoted text as one module's requirement that exists only in a
*different* module's file — copied from a neighbour during generation. Because the artifact was
immutable by the time it was found, the false attribution is permanent.

**Layer.** `shared/GOVERNANCE-CORE.md` — a standing rule: a quotation carries its source id and
line, or it is written as a paraphrase. Cheap, and it makes the next occurrence self-evident.

---

### G13 — delete every self-check row no check backs

**Evidence.** `engines/P3.1/references/ENGINE.md:476-486` renders an alignment block whose rows
assert facts — traceability, binding, manifest integrity, coverage — that `analyze.py` never
verifies. The block then renders a verdict. In the delivered module four of those rows were false
and the verdict said `PASSED ✓ — 0 findings`.

**Why the verdict mechanism is not the problem.** See "What already works" §1: the verdict *is*
reconciled against the machine report. The rows are not, because nothing checks what they claim.

**Layer.** ENGINE — for each row, either bind it to a named check that actually runs (several will
be satisfied by G1, G3, G4, G7 once those exist) or **delete the row**. A self-check row that
nothing can falsify is worse than no row: it manufactures confidence.

**Done when.** Every remaining row names the check that backs it, and the block cannot assert a
clean result for a dimension no check examines.

---

## Constraints

- One fix per commit, in the order above. Each must leave `gov.py lint` clean and
  `pytest governance-tools/tests -q` fully green before the next begins.
- Extend `governance-tools/tests/test_agnostic.py` for every fix that adds a check or a profile key.
  A fix that only passes under the ERP profile is not done.
- Grep your own diff for a stack name, a domain word, a module code, or a literal that should have
  been a profile fact. A fix that hardcodes what it was written to prevent is worse than none.
- **Change no generated artifact**, in this repo (`erp/modules/**`) or the consuming one. If a fix
  implies existing artifacts are now stale, say so — do not edit them.
- If a fix cannot be made generic, stop and report what a profile key would have to express.

## Report back

For each of G1–G13: what you changed (file and line), how `test_agnostic.py` proves it is generic,
and the evidence it fires on a real defect and stays silent on a clean artifact.

Then, explicitly: which fixes you could **not** make generic and why; which existing generated
artifacts are now stale as a consequence of your changes; and anything in the evidence above you
found to be **wrong** — the analysis behind this round was itself produced by an agent, and a
refuted claim is a more valuable report than a compliant one.
