# /orchestrate-module (BACKEND)

Master orchestration protocol for executing a BACKEND module's governance
execution pipeline in THIS backend repo. It runs from
`backend/governance/`, drives the module's own `execute-backend.md` per-phase
command, and adds a strict session/safety discipline on top of it. This command
knows ONLY the backend — there is no frontend concept, no `--track`, no
cross-repo reach into `frontend/`. (The frontend repo has its own separate
orchestrator; this one never touches it.) Every path below is relative to the
backend repo root unless said otherwise.

## Usage

```
/orchestrate-module [MODULE] [PHASE?] [--auto]
```

- `MODULE` (required): e.g. `ORG`, `SECURITY`, `MASTERDATA`. Must have a
  `governance/modules/{MODULE}/` folder with `execution-state.json`,
  `packages/backend-execution/`, and a per-module command
  `.claude/commands/{MODULE}/execute-backend.md`. If any of this is missing or
  shaped differently than expected, STOP and ask — never guess a module's
  structure.

  **VERSION (IFA-aware) — resolve the base BEFORE anything else.** A module
  that received an incremental feature (IFA) has `current_version` ≥ 2 and all
  of the above live under a version-suffixed base. Resolve it the way the tools
  do (`config.get_module_version_path`):

  ```bash
  python3 -c "import sys; sys.path.insert(0,'governance/governance-tools'); \
  import config; print(config.get_module_version_path('{MODULE}'))"
  ```

  - `current_version == 1` → base `governance/modules/{MODULE}/`      (no suffix)
  - `current_version == N` (N ≥ 2) → base `governance/modules/{MODULE}/v{N}/`

  Call it `{MBASE}`. Every `governance/modules/{MODULE}/…` and bare
  `packages/…` / `execution-state.json` path below resolves under `{MBASE}`,
  and the per-module command for a vN module is
  `.claude/commands/{MODULE}/v{N}/execute-backend.md`. By default orchestrate
  the CURRENT version; to drive an older frozen version, ask — never assume.
  Never orchestrate the un-suffixed v1 tree for a module whose current_version
  is ≥ 2.
- `PHASE` (optional): if omitted, resume from `execution-state.json`'s
  `current_phase`/`current_sub` — this command ALWAYS resumes from the last
  completed point, it never restarts a module from scratch.
- `--auto` (optional): AUTONOMOUS mode. Run every remaining phase to completion
  back-to-back WITHOUT pausing for the per-phase confirmation gate. Autonomy
  never weakens safety: subs still run strictly one at a time, the per-sub
  skill-compliance read + STEP 1.3 verification still happen, and the run STILL
  HALTS on any of — a sub error, a validation failure, a skill-compliance report
  that's silent or non-compliant, or a spec gap that STEP 2 cannot resolve from
  the module's own governance artifacts. `--auto` removes the human pause
  between clean phases; it removes no check and no stop. Without `--auto`, the
  per-phase gate applies (recommended for a module's first run or after any spec
  or skill change).

Backend execution phases, in order: `CORE → DATA-DOM → SVC-API → DOC → INT-C →
INT-R → SEC-BE → ALIGN-BE`. There is no P4/audit phase.

## Portability — never hardcode an absolute path

Keep this file working unchanged on any machine, for any user, with the repo
checked out anywhere. **Never write a specific machine's absolute path into this
file, into a dispatched agent's prompt, or into any config this command
touches.** At the start of every run derive the backend repo root at runtime —
`git rev-parse --show-toplevel`, or by walking up from this file's location —
never a remembered path from an earlier session or machine. Every path a
dispatched agent needs is resolved fresh, this run, on this machine.

---

## Role of the orchestrating session (this session, running this command)

**The orchestrating session never writes code, never edits governance specs,
and never touches the module's source files directly.** Its only jobs are:

1. Read state and spec files to brief each dispatch (read-only).
2. Dispatch exactly ONE Claude Code agent session (via the `Agent` tool) per
   **sub** — one addressable unit of work (e.g. one entity's slice, one API
   group). Never per individual task line, never a whole phase in one shot,
   regardless of what `execute-backend.md`'s weight table says. That file's
   weight-based chunking ("all LIGHT/MEDIUM → whole phase in one pass") is
   **overridden** by this standing rule: **one dispatched session per sub,
   always** — a deliberate context-safety and auditability choice.
3. Run execution **strictly sequentially**: dispatch sub N, wait for its agent
   to fully finish and report, do a lightweight verification pass, THEN dispatch
   sub N+1. Never dispatch two subs in parallel, even when they look
   independent — a later sub in a phase routinely depends on an earlier sub's
   output (a shared repository method, a common DTO/mapper, a cross-entity
   lookup).
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
   Never advance to the next phase without the user's explicit confirmation in
   this conversation, even if every sub completed cleanly. **Exception —
   `--auto`:** still PRINT each phase assessment (so the run stays auditable in
   the transcript), but do not wait — proceed automatically, and when the phase
   closes cleanly, on to the next. `--auto` only removes the pause between CLEAN
   phases; it never removes a stop on a sub error, a failed/omitted validation,
   a non-compliant skill report, or an unresolved spec gap.
5. Resolve any spec gap a dispatched agent reports (STEP 2) **before** letting
   the phase be considered done. A phase is not sound — and this command does
   not move on — until every gap opened during it is resolved or explicitly
   escalated to the user, not just recorded.
6. Communicate with dispatched agents in **English** (full technical detail).
   Communicate with the user in **Arabic**, concisely, to help them decide —
   not a narration of tool calls.

---

## STEP 0 — Locate module & resume point

1. Read `governance/modules/{MODULE}/execution-state.json`. Note
   `current_phase`, `current_sub`, and every phase's/sub's `status`.
2. If a `PHASE` argument was given, use it (but still resume from whatever subs
   in it are not yet `COMPLETE` — never re-run a `COMPLETE` sub). Otherwise use
   `current_phase`.
3. Read this module's own `.claude/commands/{MODULE}/execute-backend.md` for its
   phase list, weight map, and module-specific constraints (those substantive
   rules still apply — this command overrides only the *session-granularity and
   phase-gating* behavior above, not which files never get touched or how errors
   route).
4. **Skill & governance orientation — mandatory, once per run, before the first
   phase assessment.** Read, in full:
   - **The backend skill routing index** — `governance/GOVERNANCE-RULES.md` (its
     "Task → Skill Routing" and "Execution Order" tables). The backend skills
     themselves live at the repo root: `.claude/skills/<skill>/SKILL.md`, split
     into `build-*` (generate code) and `gov-*` (validate it). Do not assume
     "matching real code precedent" covers this — precedent tells you what the
     codebase currently does, not whether that pattern is the one the skills
     prescribe (precedent can itself be non-compliant; only reading the skill
     catches it).
   - **The repo-wide execution protocol / housekeeping rules** — the repo-root
     `CLAUDE.md` (file placement, comment style, the Legacy Module Path rules).
   - **The binding architecture reference.** On the backend there is NO
     standalone architecture doc and no `governance/.github/` tree — the
     architecture rules live INSIDE the skills (see `GOVERNANCE-RULES.md` →
     "Context Reference"): Domain-Layer ownership in `build-create-entity` +
     `gov-enforce-backend-contract` (LAYER 0); the API contract / response
     envelope / `Status`→HTTP mapping / error-code format in
     `gov-enforce-backend-contract` + `gov-enforce-error-handling`. Treat those
     skill sections as the binding reference; a skill outranks codebase
     precedent, never the reverse.
   This is a one-time read for the run — STEP 1.1 still requires identifying,
   per sub, exactly which skill files that sub's work triggers.
5. Print the phase assessment (format above) and wait for confirmation before
   dispatching anything. (In `--auto`, print it but do not wait — see the
   phase-gate rule.)

---

## STEP 1 — Per-sub dispatch protocol

For each `PENDING` sub in the confirmed phase, in the order listed in
`execution-state.json`:

### 1.1 — Orchestrator prep (read-only, in this session)

Before writing the dispatch prompt, read:
- **This command file itself, in full, again — before every single sub**, not
  just once at the start. Long multi-sub runs are exactly where instruction
  drift happens: a rule easy to follow at sub 1 silently stops applying by sub
  20 as your recall of "what this command says" degrades. This file on disk is
  authoritative over your memory of it; re-read it fresh every time.
- The phase's `[PHASE]-HEADER.md` (phase-level contracts/tables) and this sub's
  spec file, both under `packages/backend-execution/{PHASE}/`; and
  `packages/backend-execution/_SECTIONS.md` if present (plan-level content
  outside every phase — Plan Index, DB Alignment Manifest, Error Catalog, Agent
  Handoff Summary).
- **`db-script.md`** for this module (under its `P2` folder) — the authoritative
  source for table and column names, PK/FK/flag suffix conventions, and types.
  A spec block naming a field is a plan; `db-script.md` is schema ground truth.
  Never invent a column name.
- **The SRS** (under `P1`) for the business rules (RULE-IDs) this sub must
  implement — authoritative for behavior.
- **Skill compliance (mandatory — not satisfied by precedent-matching alone).**
  1. Cross-reference this sub's work type against the skills index from STEP 0.4
     and list, explicitly, every skill file this sub triggers before writing the
     dispatch — err toward more, not fewer. Backend triggers: ALWAYS
     `gov-enforce-backend-contract` first; a new/modified entity →
     `build-create-entity` (plus its Domain companion object for any business
     rule); repository → `build-create-repository`; DTOs → `build-create-dto`;
     mapper → `build-create-mapper`; service (incl. cross-module calls / domain
     events) → `build-create-service`; controller → `build-create-controller`;
     caching → `gov-enforce-caching-rules`; error handling →
     `gov-enforce-error-handling`; whole-feature validation →
     `gov-validate-backend-feature`.
  2. Read every listed skill file **in full** — not skimmed, not assumed from
     its name.
  3. Precedent-matching answers "what does the existing code look like"; this
     step answers "is that code — and the precedent you're about to copy —
     actually compliant." Both must be answered; neither substitutes for the
     other.
  4. If a skill's prescribed pattern conflicts with real precedent, do NOT
     silently pick a side — surface it to the user before/with the phase
     assessment. A consistent codebase-wide divergence from a skill is often the
     right call, but it's the user's to bless, not this orchestrator's to
     assume.
- **The real code precedent to mirror.** Before inventing any structure, find an
  already-`COMPLETE` analog and copy its exact shape: an earlier COMPLETE sub in
  this module (closest by entity shape — flat vs. self-referencing), or failing
  that an already-built sibling module's equivalent
  entity/repository/service/controller/mapper/DTO set. Real, consistent
  precedent in the checked-out code wins over an aspirational structure diagram
  when they disagree.
- Whether this sub needs something an **earlier sub in this phase** already built
  (a shared repository method, mapper, lookup, or cross-entity FK helper). If
  so, name the exact file/symbol to reuse and instruct the agent to import it,
  not duplicate it — and, if it doesn't exist yet, to ADD it there (additive
  only, one new method/export, nothing else in that file touched).

### 1.2 — Dispatch (Agent tool, one sub, `run_in_background: false`)

Write a fully self-contained English prompt — the dispatched agent has no memory
of this conversation. It MUST include:

- **Repo root**: the backend repo's absolute path (derived this run). It's a git
  repo, no worktree needed, work on the current checkout. The agent NEVER
  consults or touches the frontend repo — it does not exist for this work.
- **What NOT to touch**: every other module/phase/sub's output files; any file
  from an earlier sub in this phase (except the one specific additive change
  named in 1.1, if any — name that file and say "the ONLY change allowed here is
  X"); any controller/route/config not this phase's spec explicitly requires
  wiring into; any legacy module's files.
- **The exact files to read first, in full** (the ones identified in 1.1:
  HEADER, sub spec, db-script.md, SRS slice, the named skills, the precedent).
- **The "don't build a competing implementation" check**: before writing code,
  confirm whether the thing this sub needs already exists (an entity/repository/
  service/controller for this resource). If it exists: integrate/modify it,
  never create a competing new one. If genuinely absent, flag it in the report
  and implement it as a minimal explicit addition.
- **Contract ground-truth rule (backend)**: the authoritative sources are, in
  order, `db-script.md` (schema), the SRS (rules), and the sub's own spec block.
  The backend PRODUCES its API contract (api-docs are generated FROM the code
  after implementation) — the agent NEVER invents a contract detail the
  SRS/spec/db-script doesn't give, and NEVER consults the frontend. If a needed
  detail is confirmed absent or contradictory across those sources, it records
  ONE `api_doc_gaps[]` entry (shape below) and continues with everything else;
  it does NOT guess. Only the orchestrator (STEP 2) runs a gap to ground.
- **OQ-blocked items**: skip, note in the report, and write
  `// TODO: OQ-[ID] — pending resolution` only if the spec explicitly names that
  OQ ID for that exact field/behavior — never invent one.
- **XM-ID prohibition**: an XM-ID is a governance marker, not code — never write
  an XM-ID reference anywhere in the code. INT-C/INT-R cross-module dependencies
  are implemented via the established service/interface layer, not by emitting
  an XM-ID; if one seems needed in code, stop and flag it.
- **No parallel/competing mechanism for an owned responsibility** — use the
  established repository/service/mapper layering; no bypassing it with ad-hoc
  queries, no second HTTP/data path.
- **Skill compliance instruction**: name the exact skill file(s) from 1.1 by
  path, instruct the agent to read each in full before writing code, and to
  check its work against that skill's own "Verify before finishing" / violations
  list. A dispatch that never names a skill file means that step was skipped.
- **Validation step**: compile/build the module (`mvn -q -DskipTests compile` at
  minimum; the phase's own `gov-validate-*` skill where it applies) — run it and
  report the real result, never claim success without running it.
- **execution-state.json update, precisely scoped**: set only this sub's
  `status` to `"COMPLETE"`; advance `current_sub` only if it still equals this
  sub's id; if this is the LAST sub in the phase, also set the phase's `status`
  to `"COMPLETE"` and advance `current_phase`/`current_sub` to the next phase's
  first sub. If (and only if) a new gap was found, append ONE entry to the
  top-level `api_doc_gaps[]` in this exact canonical shape (identical to
  `generate-module-setup.md`'s, so generator and orchestrator never diverge):
  ```json
  {"type": "MISSING_IN_DOCS | NAMING_MISMATCH | MAPPING_GAP | ABSENT", "phase": "...", "sub": "...", "endpoint": "[METHOD] [path] or the field/contract in question", "detail": "what was missing/wrong", "resolution": "blocked pending spec clarification", "recorded_at": "[timestamp]"}
  ```
  Nothing else in that file may be touched. Append, never overwrite.
- **No `git commit`/`git push`** — leave changes in the working tree.
- **Required report-back format** (cap word count, keep it scannable): sub
  completed y/n; files created/changed (exact paths, plus an explicit "did NOT
  touch X" where ambiguity was possible); contract discrepancies vs. the spec
  and how resolved; any `api_doc_gaps` added; any OQ-blocked items; validation
  result; **skill compliance** (which skill file(s) checked, and for each:
  compliant or a named, justified deviation — not silence); and the exact scope
  of the `execution-state.json` edit.

### 1.3 — Orchestrator verification (after the agent reports, before the next sub)

Do this yourself, read-only, in this session:
- `git status --short` in the repo — confirm the changed-files list matches
  exactly what the agent claimed, nothing more.
- Re-run the validation command yourself if cheap (`mvn -q -DskipTests compile`),
  or at least read the agent's own run output critically.
- Re-read the relevant slice of `execution-state.json` to confirm the status
  update is scoped exactly as instructed (no other phase/sub/gap disturbed).
- Confirm the agent's report actually names the skill file(s) it checked and
  states compliant-or-deviation-with-reason for each — a report silent on this
  means the skill step was skipped, not that no skill applied; do not accept the
  sub as done on such a report. Send it back instead.
- If anything is off, send a follow-up to the same agent (by `agentId`, via
  `SendMessage`) to fix it in place — keep every code change attributable to a
  dispatched session, never patch it yourself.

---

## STEP 2 — Spec-gap resolution (same repo only — never reaches into frontend)

Trigger: a dispatched agent's report includes a new `api_doc_gaps` entry, or you
notice one still open from a prior sub. A gap must be run to ground before the
current phase is considered safe to build on — do not carry an unresolved gap
into the next phase.

Resolution stays entirely inside THIS backend repo — the backend is the source
of truth for its own contracts; there is nothing to ask the frontend. Work the
gap in this order:

1. **`db-script.md`** (this module's `P2`) — is the field/column actually
   defined, under a different real name or suffix? If so it's a NAMING_MISMATCH:
   correct this side's understanding (spec/comment wording) and proceed.
2. **The SRS** (`P1`) — does a RULE-ID specify the behavior the spec left
   implicit? If so it's MISSING_IN_DOCS resolved from the SRS; document it.
3. **A cross-module (INT-C/INT-R) dependency** — if the gap is a contract owned
   by ANOTHER backend module, read that module's own governance artifacts
   (`db-script.md`, SRS, generated `api-docs/`) in this same repo to confirm the
   real contract. This is a same-repo cross-module read, never a cross-repo one.
4. **Existing backend source** — an already-built sibling entity's
   entity/mapper/service may already implement the analogous field correctly;
   mirror it (record it as resolved via source).
5. **Genuinely absent / contradictory** — if none of the above resolves it, it's
   ABSENT: do NOT guess and do NOT invent a contract. Escalate to the USER with
   the exact gap and what you checked, and leave the `api_doc_gaps` entry open
   with `resolution` describing the state. In `--auto`, this is a HALT.

Whatever the outcome, update the gap's `resolution` in `execution-state.json`
from the placeholder to a factual note of what was found — keep the entry as a
historical record, never delete it — and sweep for any stale code comment that
still describes the field as an open gap. Only once every gap opened in the
current phase reads resolved (or is explicitly escalated) may the phase be
presented as done.

---

## STEP 3 — Phase closure and hand-back to the user

When the last sub in a phase completes and every gap is resolved:
1. Own final sweep: `git status --short`, a full compile/validation run,
   `execution-state.json` phase/sub statuses, and the `api_doc_gaps`
   resolutions.
2. Report to the user in Arabic, concisely: what got built, any corrections
   applied, any gaps found-and-fixed (with the real root cause, not just
   "resolved"), any non-blocking issues worth flagging for later — help them
   decide, don't just narrate.
3. Print the next phase's assessment and wait for explicit confirmation before
   dispatching anything in it. (In `--auto`, print it and proceed automatically
   — unless this phase closed on a halt condition, in which case wait regardless
   of `--auto`.)

---

## Constraints (non-negotiable, every sub, every phase)

- NEVER treat this as anything but a BACKEND command — no frontend concept, no
  cross-repo reach into `frontend/`, ever. The one sanctioned cross-repo
  artifact in the ecosystem (the published module registry) is the tooling's
  concern, not this orchestrator's.
- NEVER skip the phase-assessment gate, and never advance a phase without the
  user's explicit instruction — the ONLY exception is `--auto`, which
  auto-advances between CLEAN phases (still printing each assessment) and still
  HALTS on any sub error, validation failure, silent/non-compliant skill report,
  or unresolved gap, and never skips the per-sub skill read or STEP 1.3
  verification.
- NEVER dispatch more than one sub's agent at a time, even for LIGHT subs, even
  when they look independent.
- NEVER invent a route path, entity/field/column name, endpoint, error code, or
  permission code — trace every value to a real spec block, `db-script.md`, or
  SRS entry; raise a gap or an OQ instead of guessing.
- NEVER redesign an entity/repository/service/controller that already exists.
- NEVER write an XM-ID reference in code.
- NEVER dispatch a sub without first identifying (against the skills index from
  STEP 0.4) and reading, in full, every skill file that sub's work triggers.
  Matching real code precedent is necessary but not sufficient — precedent can
  itself be non-compliant, and only an actual skill read catches that. This
  discipline was learned the hard way on a frontend-side run of this same
  ecosystem (2026-08-29: 30 subs dispatched with zero skill files read,
  discovered only when the user asked — `create-forms`' RHF requirement and
  `enforce-permissions`' Layer-3 `can()` check were both silently violated
  module-wide). The incident was frontend, the discipline is identical here —
  don't wait for a backend repeat to take it seriously.
- ALWAYS update `execution-state.json` after every sub, scoped exactly as
  described — never let two subs' updates land in one dispatch.
- ALWAYS keep every code change attributable to a dispatched Claude Code
  session; this orchestrating session reads, briefs, verifies, and reports — it
  does not edit source itself.
- ALWAYS re-read this command file in full immediately before every sub's STEP
  1.1 prep — never rely on memory of it from earlier in the same conversation,
  no matter how many subs deep the run is.
