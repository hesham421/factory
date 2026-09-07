# /orchestrate-module (frontend)

Master orchestration protocol for executing ANY module's **frontend**
governance execution pipeline (`packages/frontend-execution/`,
`.claude/commands/{MODULE}/execute-frontend.md`) for any module under
`governance/modules/`. This command is module-agnostic and **frontend-only**
by construction — it has NO representation of "backend" anywhere, no
`--track`, and it never reaches into `backend/governance/`, backend source,
or any backend governance artifact. It wraps and adds a strict
session/safety discipline on top of that module's own per-module
`execute-frontend.md`, without duplicating that command's module-specific
phase/weight content. Run it from within the frontend repo; every path
below is relative to that repo's root unless said otherwise.

## Usage

```
/orchestrate-module [MODULE] [PHASE?]
```

- `MODULE` (required): e.g. `ORG`, `SECURITY`, `MASTERDATA`. Must have a
  `governance/modules/{MODULE}/` folder with `execution-state.json`,
  `packages/frontend-execution/`, `api-docs/`, and a per-module
  `.claude/commands/{MODULE}/execute-frontend.md`. If any of this is missing
  or shaped differently than expected, STOP and ask — never guess a module's
  structure.

  **VERSION (IFA-aware) — resolve the base BEFORE anything else.** A module
  that received an incremental feature (IFA) has a version ≥ 2 and all of the
  above live under a version-suffixed base. The frontend derives its version
  from ITS OWN folder tree (highest local `vN`) — it never reads or writes the
  backend registry for versioning. Resolve it the way the tools do
  (`config.get_module_version_path`):

  ```bash
  python3 -c "import sys; sys.path.insert(0,'governance/governance-tools'); \
  import config; print(config.get_module_version_path('{MODULE}'))"
  ```

  - current version `1` → base `governance/modules/{MODULE}/`      (no suffix)
  - current version `N` (N ≥ 2) → base `governance/modules/{MODULE}/v{N}/`

  Call it `{MBASE}`. Every `governance/modules/{MODULE}/…` and bare
  `packages/…` / `execution-state.json` path below resolves under `{MBASE}`,
  and the per-module command for a vN module is
  `.claude/commands/{MODULE}/v{N}/execute-frontend.md`. By default orchestrate
  the CURRENT version; to drive an older frozen version, ask — never assume.
  Never orchestrate the un-suffixed v1 tree for a module whose current version
  is ≥ 2.
- `PHASE` (optional): if omitted, resume from `execution-state.json`'s
  `current_phase`/`current_sub` — this command ALWAYS resumes from the last
  completed point, it never restarts a module from scratch.

## Portability — never hardcode an absolute path

This file must keep working unchanged on any machine, for any user, with the
repo checked out anywhere. **Never write a specific machine's absolute path
into this file, into a dispatched agent's prompt from memory, or into any
config this command touches.** At the start of every run:

- Derive the frontend repo root at runtime — e.g. `pwd` (if already inside
  it) or `git rev-parse --show-toplevel` — never assume a remembered path
  from an earlier session or a different machine.
- Every path a dispatched agent's prompt needs must be resolved fresh, this
  run, on this machine — never copy-pasted from a previous run's report or
  from this file's own examples.

There is no "other side" path to resolve — this orchestrator never dispatches
into, reads, or writes the backend repo. A frontend API-contract gap is
recorded and surfaced to the user (STEP 2), not investigated across repos.

---

## Role of the orchestrating session (this session, running this command)

**The orchestrating session never writes code, never edits governance specs,
and never touches the target project's source files directly.** Its only
jobs are:

1. Read state and spec files to brief each dispatch (read-only).
2. Dispatch exactly ONE Claude Code agent session (via the `Agent` tool) per
   **sub** (one screen/entity) — never per individual task line, and never a
   whole phase in one shot, REGARDLESS of what that module's own
   `execute-frontend.md` weight table says. That file's STEP 0 weight-based
   chunking ("all LIGHT/MEDIUM → whole phase in one pass") is **overridden**
   by this standing rule: **one dispatched session per sub, always.** This is
   a deliberate context-safety and auditability choice, not a reflection of
   the sub's actual complexity.
3. Run execution **strictly sequentially**: dispatch sub N, wait for its
   agent to fully finish and report, do a lightweight verification pass,
   THEN dispatch sub N+1. Never dispatch two subs' agents in parallel, even
   when they look independent — later subs in a phase routinely depend on an
   earlier sub's output files (a cross-entity options hook, a shared picker),
   and some phases (e.g. a routing phase with a single
   `renderCurrentScreen()`/`App.tsx` switch) have every sub touching the
   same shared file.
4. Gate every **phase** transition on the user's explicit go-ahead. Before
   dispatching the first sub of a phase, print a phase assessment and wait:
   ```
   ══════════════════════════════════════════════════════
   PHASE ASSESSMENT — {MODULE} / {PHASE}
   ══════════════════════════════════════════════════════
   Subs pending : [list, one line each]
   Plan         : N separate Claude Code sessions (one per sub), sequential
   ══════════════════════════════════════════════════════
   Proceed?
   ```
   Never advance to the next phase without the user's explicit confirmation
   in this conversation, even if every sub in the current phase completed
   cleanly.
5. Handle any `api_doc_gaps` a dispatched agent reports (see STEP 2)
   **before** letting the phase be considered done and before presenting the
   next phase's assessment. A phase is not "sound" — and this command does not
   move on — until every gap opened during it is resolved (fixed within
   frontend, or explicitly accepted by the user), not just recorded.
6. Communicate with dispatched agents in **English** (full technical detail).
   Communicate with the user in **Arabic**, concisely, in a way that helps
   them decide — not a narration of tool calls.

---

## STEP 0 — Locate module & resume point

1. Read `governance/modules/{MODULE}/execution-state.json`. Note
   `current_phase`, `current_sub`, and every phase's `status` and each sub's
   `status`.
2. If a `PHASE` argument was given, use it (but still resume from whatever
   subs in it are not yet `COMPLETE` — never re-run a `COMPLETE` sub).
   Otherwise use `current_phase`.
3. Read this module's own `governance/.claude/commands/{MODULE}/execute-frontend.md`
   for its phase list, weight map, and any module-specific constraints
   (module-specific rules there still apply — this command only overrides the
   *session-granularity and phase-gating* behavior described above, not the
   module's substantive rules like which files never get touched or how errors
   route).
4. **Skill & CLAUDE.md orientation — mandatory, once per run, before the
   first phase assessment.** Read, in full:
   - The frontend skills index: `governance/.github/skills/frontend/CLAUDE.md`
     — it names every `create-*`/`enforce-*` skill file that exists and when
     to use it. Do not proceed on the assumption that "matching real code
     precedent" already covers this — precedent tells you what the codebase
     currently does, not whether that pattern is the one the skills actually
     prescribe (precedent can itself be non-compliant; only reading the skill
     catches that).
   - `governance/CLAUDE.md` (repo-wide housekeeping rules — file placement,
     comment style, etc. — that apply regardless of which module/phase is
     being executed).
   - The binding architecture reference,
     `governance/.github/skills/frontend/references/architecture.md`, and
     `references/contract-rules.md` — `architecture.md` is the only thing
     that outranks a skill file when the two disagree; nothing else does, and
     a skill never yields to codebase precedent on its own say-so either (see
     STEP 1.1's skill-compliance bullet for what to do when they conflict).
   This is a one-time read for the run, not per-sub — STEP 1.1 below still
   requires identifying, per sub, exactly which of the indexed skill files
   that sub's specific work triggers.
5. Print the phase assessment (format above) and wait for confirmation
   before dispatching anything.

---

## STEP 1 — Per-sub dispatch protocol

For each `PENDING` sub in the confirmed phase, in the order listed in
`execution-state.json`:

### 1.1 — Orchestrator prep (read-only, in this session)

Before writing the dispatch prompt, read:
- **This command file itself (`governance/.claude/commands/
  orchestrate-module.md`), in full, again — before every single sub, not
  just once at the start of the run.** Long multi-sub, multi-phase runs are
  exactly where instruction drift happens: a rule added or sharpened mid-run
  (skill-compliance, a specific NEVER) is easy to keep following at sub 1 and
  silently stop applying by sub 20, without ever consciously deciding to skip
  it — your own memory of "what this command says" degrades over a long
  session even when nothing about the file itself changed. This file on disk
  is authoritative over your recollection of it; re-read it fresh every time.
- The phase's `TEST-PLAN-FE-HEADER.md` is a TEST artifact and is NOT read
  here — for execution, read the phase's own `*-HEADER.md` preamble (if the
  phase was split) and this sub's spec file under
  `packages/frontend-execution/{PHASE}/`.
- The relevant `api-docs/endpoints/*.md` file(s) for this sub's entity —
  this is the **only** authoritative API contract; a spec file's HTTP
  method/path/shape is a plan, api-docs is ground truth. The frontend never
  consults backend source to resolve a contract — if api-docs is silent or
  contradictory, that is an `api_doc_gaps` entry (STEP 2), not a reason to
  read backend code.
- **Skill compliance (mandatory — not satisfied by precedent-matching alone,
  and not skippable because "the pattern already exists in the codebase").**
  1. Cross-reference this sub's work type against the skills index read in
     STEP 0.4 and list, explicitly, in your own working notes, every skill
     file this sub triggers before writing the dispatch prompt — err toward
     listing more, not fewer. Non-exhaustive triggers: a facade-hook/query
     sub → `create-queries` + `create-api-client`; anything producing or
     touching a form → `create-forms`; anything touching a route, nav guard,
     or a permission-gated control (button, field, action) → `create-routing`
     + `enforce-permissions`; a new entity's types/schema → `create-models`;
     a new list/table/entry page → `create-components`; a delete/activate/
     deactivate handler → `create-confirm-actions`.
  2. Read every listed skill file **in full** — not skimmed, not assumed from
     its filename or one-line description.
  3. Precedent-matching (finding an already-COMPLETE sub or sibling module to
     mirror, per the next bullet) answers "what does the existing code look
     like"; this step answers "is that code — and the precedent you're about
     to copy — actually compliant." Both questions must be answered; neither
     substitutes for the other.
  4. If a skill's prescribed pattern conflicts with the real precedent you
     found, do NOT silently pick a side. Note the conflict and surface it to
     the user (alongside or before the phase assessment) rather than resolving
     it unilaterally — a real, consistent, codebase-wide divergence from a
     skill is common and often the right call, but it is the user's call to
     bless. The one exception: `references/architecture.md` outranks a skill
     file outright when the two disagree.
- **The real code precedent to mirror.** Before inventing any structure, find
  an already-implemented analog and copy its exact shape:
  - An earlier, already-`COMPLETE` sub in this same module (closest analog by
    container/structure pattern — e.g. flat SIDE_DRAWER vs. self-referencing
    TREE_MASTER_DETAIL).
  - Failing that, an already-built sibling module's equivalent feature —
    e.g. `src/roles/`, `src/permissions/`, `src/masterLookups/` are real,
    working implementations of this exact governance pipeline for a different
    module (same `hooks.ts`/`*Api.ts`/`*.schema.ts` shape, same query-key
    factory pattern, same facade-hook shape, same comment style referencing
    API-IDs).
  - Never assume a folder/file layout from the architecture doc's aspirational
    project-structure diagram alone if the *actual* codebase already diverges
    from it in a consistent way — real, consistent precedent in the
    checked-out code wins over the doc when they disagree.
- **Deferred wiring is a plan gap until a named phase owns it — never
  inherited precedent.** If this sub's spec, or the real precedent you're
  about to mirror, defers something structurally load-bearing (most commonly:
  a page never actually importing or calling the real facade hook this
  pipeline already built for it, staying on a mock/static/stub source
  instead) to "a later phase," or just leaves it unstated, do not accept that
  deferral only because an earlier sub already made the same call —
  repetition is not confirmation, it's the same unexamined gap propagating.
  Check, by name, against this module's own phase/weight map (STEP 0.3): is
  there a concrete phase/sub that will actually close this? If yes, cite it
  explicitly in your prep notes. If no such phase exists anywhere in the plan,
  this is a **plan gap** — surface it to the user directly, in this
  conversation, before dispatching this sub. Do not let a 3rd, 10th, or 30th
  sub cite the same absence as further evidence it was intentional. (Concrete
  incident, ORG module, 2026-08-29: F2 built a real TanStack Query facade hook
  per entity; every page kept using an old mock store instead; treated as an
  increasingly "established boundary" across F2→F3→F4→SEC-FE→ALIGN-FE — 30
  subs, never once re-examined — because no phase in the plan was ever going
  to wire it. TestSprite caught it after the fact. It should have been caught
  at F2 or F4.)
- Whether this sub needs something an **earlier sub in this phase** already
  built (a cross-entity FK "options" hook or shared type). If so, identify the
  exact file/symbol to reuse and instruct the dispatched agent to import it,
  not duplicate it — and, if it doesn't exist yet, to ADD it there (additive
  only, one new export, nothing else in that file touched) rather than
  reinventing it locally.

### 1.2 — Dispatch (Agent tool, one sub, `run_in_background: false`)

Write a fully self-contained English prompt — the dispatched agent has no
memory of this conversation. It MUST include:

- **Project root**: the frontend repo's absolute path (resolved this run).
  State it's a git repo, no worktree needed, work on the current checkout.
  Never give the agent a backend path — it has no reason to touch backend.
- **What NOT to touch**: every other module/phase/sub's output files, any
  file from an earlier sub in this same phase (except the one specific
  additive change identified in 1.1, if any — name that file explicitly and
  say "the ONLY change allowed to this file is X"), any page/component file
  unless this phase's own spec explicitly requires wiring into it, and any
  pre-existing legacy/mock-data files unless this phase explicitly targets
  them.
- **The exact files to read first**, in full, before writing anything (the
  ones identified in 1.1).
- **The "don't build a competing implementation" check**: before writing a
  task's code, confirm whether a corresponding component/route already exists
  in the UI Shell. If it exists: confirm/integrate, modify the existing file,
  never create a competing new one. If genuinely absent, flag it as a Shell
  gap in the report and implement it as an explicit, minimal addition.
- **API Contract Resolution rule**: `api-docs/` is authoritative and the ONLY
  source for wire contracts. The agent must NEVER consult backend source,
  controllers, services, repositories, or governance — if a detail is
  confirmed absent or contradictory in api-docs, it records an `api_doc_gaps[]`
  entry (shape below) with resolution `"blocked pending frontend API contract
  clarification"` and continues with everything else; it does NOT try to
  resolve the gap itself.
- **OQ-blocked items**: skip, note in the report, and only write
  `// TODO: OQ-[ID] — pending resolution` in code if the spec explicitly names
  that OQ ID for that exact field/behavior — never invent one.
- **XM-ID prohibition**: never write an XM-ID reference anywhere in frontend
  code; if one seems needed, stop and flag it instead.
- **No parallel/competing mechanism for an owned responsibility** — only
  whatever `architecture.md` (or, absent one, consistent real precedent) names
  as the one owner for each responsibility (e.g. TanStack Query + a single
  `http` client wrapper, no new state library, no axios/raw fetch).
- **Skill compliance instruction**: name the exact skill file(s) identified in
  1.1, by path, and instruct the agent to read each in full before writing any
  code, and to check its work against that skill's own "Verify before
  finishing"/violations list. A dispatch prompt that never names a skill file
  means that step was skipped, not that no skill applied.
- **Validation step**: whatever check actually verifies this phase's kind of
  change (typecheck at minimum; a build or the phase's own validation skill if
  one applies) — run it and report the result, don't claim success without
  running it.
- **execution-state.json update, precisely scoped**: set only this sub's
  `status` to `"COMPLETE"`; advance top-level `current_sub` only if it still
  equals this sub's id; if this is the LAST sub in the phase, also set the
  phase's own `status` to `"COMPLETE"` and advance `current_phase`/
  `current_sub` to the next phase's first sub. If (and only if) the agent
  found and needs to record a new gap, it may append ONE entry to the
  top-level `api_doc_gaps[]` array in this exact shape:
  ```json
  {"phase": "...", "sub": "...", "endpoint": "...", "detail": "...", "resolution": "blocked pending frontend API contract clarification"}
  ```
  Nothing else in that file may be touched. Append, never overwrite.
- **No `git commit`/`git push`** — leave changes in the working tree.
- **Required report-back format** (cap the word count so it stays scannable):
  sub completed y/n, files created/changed (exact paths, and an explicit
  confirmation of what was NOT touched if there was any risk of ambiguity),
  field/contract discrepancies found vs. the spec and how resolved, any Shell
  gaps flagged, any `api_doc_gaps` added, any OQ-blocked items, validation
  result, **skill compliance** (which skill file(s) it checked against, and
  for each: compliant, or a named, justified deviation — not silence), and
  exact scope of the `execution-state.json` edit.

### 1.3 — Orchestrator verification (after the agent reports, before
dispatching the next sub)

Do this yourself, directly, in this session (read-only inspection):
- `git status --short` in the frontend repo — confirm the changed-files list
  matches exactly what the agent claimed, nothing more.
- Re-run the validation command yourself (e.g. `tsc --noEmit`) if cheap
  enough, or at least read the agent's own run output critically.
- Re-read the relevant slice of `execution-state.json` to confirm the status
  update is scoped exactly as instructed (no other phase/sub/gap entry
  disturbed).
- Confirm the agent's report actually names the skill file(s) it checked
  against and states compliant-or-deviation-with-reason for each — a report
  silent on this means the skill step was skipped, not that no skill applied;
  send it back instead of accepting.
- If anything is off, send a follow-up message to the same agent (by its
  `agentId`, via `SendMessage`) to fix it in place rather than silently
  patching it yourself — keep every code change attributable to a dispatched
  Claude Code session.

---

## STEP 2 — API-contract gap handling (frontend-only — never reaches backend)

Trigger: a dispatched agent's report includes a new `api_doc_gaps` entry, or
you (the orchestrator) notice one still open from a prior sub.

This orchestrator does **not** investigate the backend. The frontend/backend
separation is absolute here: api-docs is the only contract source, and a gap
in it is resolved by clarifying api-docs — not by reading backend code.

1. **Confirm the gap is real** (read-only, frontend only): re-read the
   relevant `api-docs/endpoints/*.md` and the sub's spec. Decide which it is:
   - **(A) Already answered** — the contract detail IS in api-docs; the agent
     missed it. Correct the agent's understanding, no gap remains.
   - **(B) Genuinely missing/contradictory in api-docs** — the frontend
     contract this module needs is not documented, or documents conflict.
2. **Act on the finding**:
   - (A): dispatch a small follow-up to complete the sub against the real
     contract; clear the gap from `api_doc_gaps`.
   - (B): this is a real blocker the frontend cannot resolve on its own. Do
     NOT guess a contract and do NOT read backend source. Keep the
     `api_doc_gaps` entry with resolution `"blocked pending frontend API
     contract clarification"`, and **surface it to the user in this
     conversation** — state exactly what endpoint/field is undocumented and
     that it needs a real API-contract clarification (which is produced
     upstream and published into this repo's `api-docs/`, out of band, by
     whoever owns that contract). The user decides: pause the phase for the
     contract, or accept it as a documented, deliberate limitation.
3. **Close the loop on this side**: once a contract clarification lands in
   `api-docs/`, dispatch a small follow-up agent to complete the affected sub
   and change the gap's `resolution` field in `execution-state.json` from
   "blocked pending frontend API contract clarification" to a factual note of
   what was clarified — keep the entry as a historical record, never delete
   it. Sweep for any stale code comment that still describes the field as an
   open gap and update it too.
4. Only once every gap opened in the current phase reads as resolved (fixed,
   or user-accepted) may you present that phase as done and move to the next
   phase's STEP 0 assessment.

---

## STEP 3 — Phase closure and hand-back to the user

When the last sub in a phase completes and every gap is resolved:
1. Do your own final sweep: `git status --short`, full validation run,
   `execution-state.json` phase/sub statuses, and the `api_doc_gaps` array's
   resolutions.
2. Report to the user in Arabic, concisely: what got built, any corrections
   applied, any gaps found-and-fixed (with the real root cause, not just
   "resolved"), any non-blocking issues worth flagging for later (a stale UI
   filter, a deferred picker, etc.) — help them decide, don't just narrate.
3. Print the next phase's assessment and wait for explicit confirmation before
   dispatching anything in it.
4. **When the phase just closed is the module's LAST pre-test phase** — i.e.
   completing it makes every entry in `execution-state.json`'s
   `test_phase.gated_by_phases` list read `COMPLETE` (`ALIGN-FE`) — do one
   more mandatory pass before reporting the module "done":
   - **Data-Wiring Reality Check** (mechanical, cheap, read-only, do it
     yourself — inspection, not "execution"). For every SCR-ID this module
     built a real F2 facade hook for, grep the actual page/component file that
     is supposed to use it and confirm the import/call is really there — do
     not trust an F4 or routing-phase doc's "Facade Hook: useXFacade()" line
     as proof; that line documents the hook's existence, not that anything
     calls it (this is exactly how the ORG incident went undetected for 30
     subs). If the module built any structural stand-in (a mock store, a stub,
     a hardcoded dataset) that was supposed to be retired and no phase in the
     plan actually retired it, that is a blocking finding — report it to the
     user explicitly and by name, separately from and above any list of
     genuinely deliberate, spec-documented deferrals. Do not fold the two
     together into one "outstanding minor issues" list.
   - **Push `frontend-test` as the required next step, not an optional aside.**
     It is the one thing in this pipeline that exercises the built code
     end-to-end against something other than the plan's own self-consistency —
     which is all `ALIGN-FE` actually checks, despite its name (its own scope
     note says so: internal-plan consistency, not implementation correctness).
     The Data-Wiring Reality Check above is a cheap grep-level substitute for
     what a real test run would catch anyway, not a replacement for running it.
     Do not summarize the module as "complete" with the test phase framed as a
     separate, skippable track — frame it as the last remaining step before the
     module is actually verified to work, and recommend running it now.

---

## Constraints (non-negotiable, apply across every sub and every module)

- NEVER skip the phase-assessment confirmation gate, and never advance a phase
  without the user's explicit instruction in this conversation — regardless of
  how clean every sub's report looked.
- NEVER dispatch more than one sub's agent at a time, even for LIGHT subs,
  even when they look independent.
- NEVER reach into `backend/governance/`, backend source, or any backend
  artifact — this is a frontend-only orchestrator. A frontend API-contract gap
  is recorded and surfaced to the user (STEP 2), never investigated across
  repos. api-docs is the only contract source.
- NEVER invent a route path, component/entity name, field, endpoint, or
  permission code — trace every value to a real spec block or real api-docs
  entry; raise a gap or an OQ instead of guessing.
- NEVER redesign a component/route that already exists in the UI Shell.
- NEVER write an XM-ID reference in frontend code.
- NEVER dispatch a sub without first identifying (against the skills index
  read in STEP 0.4) and reading, in full, every skill file that sub's work
  type triggers. Matching real code precedent is necessary but not sufficient
  — precedent can itself be non-compliant with a skill, and only an actual
  skill read catches that. This was skipped for the entirety of a prior ORG
  run (2026-08-29): 30 subs dispatched across F1-ALIGN-FE with zero skill
  files read, discovered only when the user asked directly. Concretely found
  afterward: `create-forms` (R.8.1, "useState per field" is a listed rejection
  trigger) was violated by every one of the 7 entity forms — RHF+zodResolver
  was never wired, so the F3-built `*.schema.ts` files sat unused; and
  `enforce-permissions`' Layer-3 requirement (`can()` as the first statement
  inside a save/deactivate/activate handler, not just hiding the triggering
  button) was never implemented anywhere in the module. Do not repeat this.
- ALWAYS update `execution-state.json` after every sub, scoped exactly as
  described — never let two subs' status updates land in the same dispatch.
- ALWAYS keep every code change attributable to a dispatched Claude Code
  session; this orchestrating session reads, briefs, verifies, and reports —
  it does not edit source itself.
- ALWAYS re-read this command file itself, in full, immediately before every
  sub's STEP 1.1 prep — never rely on your memory of it from earlier in the
  same conversation, no matter how many subs deep the run is.
