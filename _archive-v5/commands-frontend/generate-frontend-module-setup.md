# Generate Frontend Module Setup

```
Lives at   : frontend/governance/.claude/commands/generate-frontend-module-setup.md
Invokes    : frontend/governance/governance-tools/agent1_create_structure.py,
             agent2_archive.py, agent3_splitter.py — these tools know
             ONLY the frontend. There is no track concept here; this
             file and the tools it calls have no representation of
             "backend" anywhere except the one sanctioned neutral read
             noted below — the frontend track is otherwise fully
             standalone and never depends on backend readiness, status,
             sign-off, source code, or governance artifacts.
```

## Your Task

Scan this repo for the specified module and generate three files:
1. `.claude/commands/[MODULE]/execute-frontend.md` — implementation phase execution
2. `.claude/commands/[MODULE]/execute-frontend-test.md` — test phase execution,
   gated on execute-frontend.md's phases
3. `execution-state.json` — state tracker for both

Each module gets its own `.claude/commands/[MODULE]/` folder — never write
back to the flat `.claude/commands/execute-frontend.md` (no module name,
collides with every other module's setup, and silently overwrites whatever
module was generated last).

**The one sanctioned cross-repo read** (nothing ever reaches into
`backend/governance/` or backend source — this is a neutral, jointly-
published contract file, not a path inside backend's own tree):
```
1. ../shared/modules-registry.json
   — read-only, to validate the module actually exists. This repo
   never registers a module itself.
```

API Docs are NOT read from backend at all — this repo owns its own
copy under `$MBASE/api-docs/` (see Step 0.5 — v1 = no suffix, vN = /vN), used during
execution (STEP 1.5). See `governance/governance-tools/config.py`'s
`get_api_docs_path()` — this is the existing, already-established
frontend API-docs location.

---

## Input

```
$ARGUMENTS = MODULE
```

If missing, ask for it — do not guess.

**Module validation (the only identity check — no module is ever**
**named or excluded by this file itself):**
```bash
grep -q "\"$MODULE\"" ../shared/modules-registry.json \
  && echo "found" || echo "not found"
```
If not found: stop with a plain "module not registered" message and
explain that registration only happens in the backend toolset, which
publishes the shared registry file read above. There is no
auto-register option here, and no other module-specific check anywhere
in this file — a module that was never registered is simply
unreachable, for any module, by construction.

---

## Precondition gate (readiness, not identity — checked only after
## the module validation above passes)

```
╔══════════════════════════════════════════════════════════════════╗
║   FRONTEND READINESS GATE                                         ║
╠════════════════════════════════════╦═══════════════════════════════╣
║ GATE: UI SHELL COMPLETE confirmed  ║ [Yes / No]                    ║
║ frontend-execution-plan.md exists  ║ [Yes / No]                    ║
║ with Gate ALIGN-FE ✓               ║                                ║
╚══════════════════════════════════════════════════════════════════╝
```

If both are Yes: proceed to Step 1 directly.

If any is No: offer a documented-override path — this exists for any
module where the frontend-owned condition is substantively met but a
formal artifact is missing only because it was never generated (a
readiness gap, not an identity question):

```
This module doesn't meet the standard readiness gate. Is the missing
item substantively ready, with the formal artifact missing only
because it was never generated for it?

  1) Yes — documented override (one question, then proceed immediately)
  2) No — stop here, complete the standard flow first
```

If (2): stop, state exactly which precondition is missing.

If (1): ask exactly one follow-up question — a one-line reason — then
append to `governance/modules/[MODULE]/frontend-gate-overrides.json`
(this repo's own copy — create with `"overrides": []` if absent;
always append, never overwrite):
```json
{
  "date": "[actual current date]",
  "module": "[MODULE]",
  "gates_bypassed": ["list the No/unconfirmed items above"],
  "reason": "[user's exact one-line answer]",
  "decided_by": "user (documented override)"
}
```
Confirm the log was written, then proceed straight to Step 1 — no
further questions or warnings this session.

---

## Step 0.5 — Resolve the module VERSION base (IFA-aware) — MANDATORY

A frontend module that received an incremental feature (IFA) has a version ≥ 2,
and all its artifacts (packages, execution-state, api-docs, generated commands)
live under a version-suffixed base — never over v1. The frontend derives its
version from ITS OWN folder tree (it owns its module tree; it never reads or
writes the backend registry for versioning). Resolve the base BEFORE scanning,
exactly the way the tools do (`config.get_module_version_path`):

```bash
python3 -c "import sys; sys.path.insert(0,'governance/governance-tools'); \
import config; print(config.get_module_version_path('$MODULE'))"
```

Rule (mirror it if you resolve by hand — highest existing local vN folder):
- current version `1` → base = `governance/modules/$MODULE/`        (no suffix)
- current version `N` (N ≥ 2) → base = `governance/modules/$MODULE/v$N/`

Call this resolved path `$MBASE`. Every `governance/modules/$MODULE/…` path in
the steps below means `$MBASE/…`. In particular, for a vN module:
- scan `$MBASE/packages/frontend-execution` and `$MBASE/packages/frontend-test`
- write `execution-state.json` to `$MBASE/execution-state.json`
- `api_docs_path` = `$MBASE/api-docs/`
- write the generated commands to `.claude/commands/[MODULE]/v$N/` (so the v1
  commands, still valid history, are never overwritten). For v1 keep the flat
  `.claude/commands/[MODULE]/`.

NEVER hardcode the un-suffixed `modules/$MODULE/` for a module whose current
version is ≥ 2 — that would scan the frozen v1 packages and generate a v1
command for a v2 delta.

---

## Step 1 — Scan the repo structure

```bash
find $MBASE/packages/frontend-execution -type f -name "*.md" | sort
find $MBASE/packages/frontend-test -type f -name "*.md" | sort
```

Identify PHASES, SUBs (per file, excluding `index.md`), preserving
filesystem sort order. Read each sub's first 40 lines, count tasks.

Expected phases, in strict order (only include ones actually present):
```
F1 → F2 → F3 → F4 → SEC-FE → ALIGN-FE
```

### Test phase (single phase — no MARK-level split)

`packages/frontend-test/` is Playwright-only by construction. Treat it
as ONE TEST-PHASE named `frontend-test`:
- SUBs = every `.md` file inside, excluding `index.md`, `.gitkeep`, and
  the preamble `TEST-PLAN-FE-HEADER.md` — i.e. `UI-FLOWS`, `INT-FLOW`
  when the plan was split, or the single `TEST-PLAN-FE.md` when it
  wasn't. (There is no `MANDATORY-*.md` file — mandatory scenarios live
  in the header preamble.)
- Gated by every frontend phase that exists for this module

### Weight classification

| Weight | Criteria |
|--------|----------|
| LIGHT  | < 5 tasks, single component |
| MEDIUM | 5–10 tasks, 1–2 components |
| HEAVY  | > 10 tasks, multi-layer (Models+Hooks+Validation+Routing) |
| XL     | 3+ screens in one sub |

---

## Step 2 — Generate `execution-state.json`

Location: `$MBASE/execution-state.json` (resolved in Step 0.5 — v1 = no suffix, vN = /vN) (this
repo's own copy — never merged with backend's file of the same name
for the same module).

```json
{
  "module": "[MODULE]",
  "generated_at": "[today's date]",
  "ui_shell_complete_confirmed": true,
  "current_phase": "[FIRST_PHASE]",
  "current_sub": "[FIRST_SUB or null]",
  "api_docs_path": "[MBASE]/api-docs/",
  "phases": [
    {
      "id": "[PHASE_NAME]",
      "status": "PENDING",
      "subs": [
        { "id": "[SUB_NAME]", "status": "PENDING" }
      ]
    }
  ],
  "test_phase": {
    "id": "frontend-test",
    "status": "PENDING",
    "gated_by_phases": ["F1", "F2", "F3", "F4", "SEC-FE", "ALIGN-FE"],
    "header_file": "packages/frontend-test/TEST-PLAN-FE-HEADER.md",
    "subs": [
      { "id": "UI-FLOWS", "status": "PENDING" },
      { "id": "INT-FLOW", "status": "PENDING" }
    ]
  },
  "blocked": [],
  "api_doc_gaps": []
}
```

The `ui_shell_complete_confirmed` boolean records that the precondition
gate actually passed (standard or override) — a record, not a cache to
trust blindly much later.

Rules: list only phases actually found; `gated_by_phases` lists only
phases present for this module; `blocked`/`api_doc_gaps` start empty.
No `deferred_xm` field here — XM-IDs never appear in frontend state at all.

**Match the real splitter output, don't assume it.** `agent3_splitter.py`
names the test-plan preamble file `TEST-PLAN-FE-HEADER.md` (from the phase
key), and it only exists when the plan was ABOVE the TC threshold (> 8 →
split into `UI-FLOWS.md` / `INT-FLOW.md`). BELOW threshold there is a
single `TEST-PLAN-FE.md`, no `*-HEADER.md`, and no SUB files. There is no
separate `MANDATORY-*.md` file at all — the MANDATORY-P scenarios live
inside the header preamble. So derive `test_phase` from Step 1's actual
scan:
- If `TEST-PLAN-FE-HEADER.md` exists → set `header_file` to it and list
  the real SUB files found (`UI-FLOWS`, `INT-FLOW`) as `subs`.
- If only `TEST-PLAN-FE.md` exists → omit `header_file`, and set
  `subs` to a single `{ "id": "TEST-PLAN-FE", "status": "PENDING" }`.
Never write a `header_file`/`mandatory_file` path the scan didn't produce.

### `api_doc_gaps[]` entry format
```json
{
  "type": "MISSING_IN_DOCS",
  "phase": "[PHASE]",
  "sub": "[SUB]",
  "endpoint": "[METHOD] [path]",
  "detail": "[what was missing]",
  "resolution": "blocked pending frontend API contract clarification",
  "recorded_at": "[timestamp]"
}
```

---

## Step 3 — Generate `.claude/commands/[MODULE]/execute-frontend.md`

```markdown
# /[MODULE]/execute-frontend

Execute the current phase for [MODULE] — with context safety check.

## Usage
/[MODULE]/execute-frontend [PHASE]

---

## STEP 0 — Context Safety Assessment (MANDATORY)

### 0.1 — Read state, identify PENDING subs in the requested phase
### 0.2 — Look up each sub's weight from the Weight Map below
### 0.3 — Classify and decide chunking

| Total weight in phase | Action |
|---|---|
| All LIGHT/MEDIUM | Execute the whole phase in one pass |
| Any HEAVY present | Chunk — one sub (or a few LIGHT subs) per pass |
| Any XL present | That sub alone is one full pass |

### 0.4 — Print assessment, wait for confirmation
```
══════════════════════════════════════════════════════
PHASE ASSESSMENT — [MODULE] / [PHASE]
══════════════════════════════════════════════════════
Subs pending : [list, weight + task count each]
Plan         : [one pass / chunked — list chunks]
══════════════════════════════════════════════════════
Proceed? [waits for confirmation]
```

---

## STEP 1 — Execution (after confirmation)

### Per sub:
1. Read `packages/frontend-execution/[PHASE]/[SUB].md` completely
2. Identify all tasks
2.5. **UI Shell reference check** — before writing any task's code,
     confirm whether a corresponding component/route already exists in
     the UI Shell. If it exists: CONFIRM/INTEGRATE, modify the existing
     file — never create a competing new one. If genuinely absent: flag
     it in the session report as a Shell gap, implement as an explicit addition.
3. **API Contract Resolution** [phases F1/F2/F3 only]: check
   `api_docs_path` first — treat it as the authoritative and only API
   contract. If an endpoint or contract detail is confirmed absent from
   api-docs, do not inspect backend source, controllers, services,
   repositories, or governance — record it in `api_doc_gaps[]` with
   resolution `"blocked pending frontend API contract clarification"`
   and continue with remaining tasks (same pattern as an OQ-blocked
   item below). Never invent the missing contract.
4. Read required skills from `.github/skills/frontend/`
5. Execute all tasks in order
6. Run the phase's validation skill after the last task
7. Mark sub COMPLETE in `execution-state.json`

### Blocked items — OQ
OQ-blocked task → skip, add to `blocked[]`, mark:
`// TODO: OQ-[ID] — pending resolution`. Continue remaining tasks.

Never write an XM-related TODO in frontend code — XM-IDs are
exclusively a backend concern. If a task seems to need one, stop and
flag it instead of implementing it.

---

## STEP 2 — Session Report

Phase/sub completed, tasks executed, blocked items, any api_doc_gaps added.

---

## Weight Map — [MODULE]
[Insert actual weight map from Step 1]

## Phase Map — [MODULE]
[Insert actual phase → subs map from Step 1]

---

## Constraints (NON-NEGOTIABLE)

- NEVER skip STEP 0
- NEVER execute without confirmation after assessment
- NEVER invent a route path, component name, or PERM_* code — trace
  every value to an F4-SCREEN block, raise an OQ if none covers it
- NEVER redesign a component/route that already exists in the UI Shell
- NEVER call an endpoint not present in real API Docs
- NEVER consult backend source, controllers, services, repositories,
  or governance for an API detail — if missing from api-docs, record
  it in `api_doc_gaps[]` and continue
- NEVER write an XM-ID reference in frontend code
- NEVER advance phase without explicit instruction
- ALWAYS update execution-state.json after every sub
```

---

## Step 3B — Generate `.claude/commands/[MODULE]/execute-frontend-test.md`

```markdown
# /[MODULE]/execute-frontend-test

Execute test scenarios for [MODULE] — only for what's actually complete.

## Usage
/[MODULE]/execute-frontend-test

---

## STEP 0 — Gate Check + Assessment

### 0.1 — Gate Check (MANDATORY)
Read `execution-state.json` → `test_phase.gated_by_phases[]`. Confirm
every listed phase has `status == COMPLETE`. Empty list → gate passes automatically.

If not all complete:
```
══════════════════════════════════════════════════════
⛔ TEST GATE FAILED — [MODULE]
══════════════════════════════════════════════════════
Waiting on : [PHASE: status], ...
══════════════════════════════════════════════════════
```
STOP. Do not generate or run any test.

### 0.2–0.4 — Same assessment/confirmation pattern as execute-frontend.md

---

## STEP 1 — Execution (after confirmation)

### 1.0 — Read `header_file` once (if present)
The header preamble (`TEST-PLAN-FE-HEADER.md`) carries the phase-level
intro and the MANDATORY-P scenarios. It exists only when the plan was
split; if `test_phase` has no `header_file`, the single `TEST-PLAN-FE.md`
sub already contains everything — read that instead. There is no
separate mandatory file to read.

### Per sub:
1. Read `packages/frontend-test/[SUB].md` completely
2. Identify all scenarios
3. Generate: POM + spec file (Page Object Model, `data-testid` first,
   no `waitForTimeout`)
4. Run: `playwright-mcp`, per the shared MCP execution order
   (oracle-sql precondition → playwright-mcp execute → oracle-sql
   confirm → screenshot on failure)
5. Classify every failure/skip using the shared taxonomy
6. Update `execution-state.json`

---

## STEP 2 — Session Report

Write to `reports/TEST-REPORT-[MODULE]-frontend-[YYYY-MM-DD].md`. Any
`FAIL` → report only, never fix here.

---

## Constraints (NON-NEGOTIABLE)

- NEVER run before the gate check passes
- NEVER treat `TEST-PLAN-FE-HEADER.md` (the preamble) as a sub
- NEVER skip the MANDATORY-P scenarios (they live in the header preamble)
- NEVER modify application source code — report, don't fix
- ALWAYS classify every failure/skip
- ALWAYS update execution-state.json after every sub
```

---

## Step 4 — Verify and report

```
══════════════════════════════════════════════════════
FRONTEND MODULE SETUP COMPLETE: [MODULE]
══════════════════════════════════════════════════════
Preconditions:
  GATE: UI SHELL COMPLETE       : [✓ / override logged]
  ALIGN-FE ✓                    : [✓ / override logged]

execution-state.json      ✓  governance/modules/[MODULE]/ (this repo)
execute-frontend.md       ✓  .claude/commands/[MODULE]/
execute-frontend-test.md  ✓  .claude/commands/[MODULE]/

Phases detected       : [count]
Total subs detected   : [count]
Test phase detected   : frontend-test [✓ / not found]
  gated by : [phases found]

Weight map:
  [PHASE] / [SUB]  → [WEIGHT]  ([N] tasks)

To start execution:
  /[MODULE]/execute-frontend [FIRST_PHASE]

To run tests once implementation is COMPLETE:
  /[MODULE]/execute-frontend-test
══════════════════════════════════════════════════════
```

---

## Constraints (this command itself — NON-NEGOTIABLE)

- NEVER run without MODULE specified
- NEVER proceed past the module-validation check for a module not
  found in the shared modules registry — there is no override for
  non-existence, only for readiness (a different question entirely)
- NEVER reach into `backend/governance/` or backend source for
  anything — the only cross-repo read is the neutral, jointly-
  published `../shared/modules-registry.json` listed at the top of
  this file; frontend readiness never depends on backend completion,
  implementation status, production status, sign-off, source code, or
  governance artifacts
- NEVER invent a phase, sub, or file path not found in Step 1's scan
- NEVER name or special-case any specific module anywhere in this file
