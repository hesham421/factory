# Factory defect analysis & fix plan

**Subject:** why the SEC/FIN/MDL analysis artifacts shipped with defects, and what to change so it cannot recur.
**Method:** forensic, against `/Users/ezzat/factory` and the delivered `backend` repo. Every claim below is reproducible with the command shown.
**Date:** 2026-09-11

---

## 1. Executive summary — the finding is the opposite of what it looked like

From inside the backend repo the SEC plan looked like the output of a weak generator: a wrong PK strategy, a wrong error-code format, a mis-transcribed column, dangling ADR paths, a rule with no data source, and a self-check that printed `PASSED ✓ — 0 findings` over all of it.

**None of that is true of the engine as it stands today.** The factory already contains:

- an engine spec (`engines/P3.1/references/ENGINE.md` §9) that *explicitly warns against* the exact failure that happened — "a self-check that always prints PASSED transfers false confidence downstream and is worse than no self-check";
- six mechanical checks — `value-agreement`, `code-format`, `data-source`, `xref-resolve`, `refs-exist`, `paths-resolve` — each of which targets one of the defects that shipped;
- all six **implemented** in `governance-tools/analyze.py` and **wired at `CRITICAL`** in `shared/ARTIFACT-CONTRACTS.md` (C7.10, C7.12, C7.13, C7.14, C5.12, C6.9);
- delivery code that copies ADRs into the consumer tree and emits repo-relative paths (`gov.py:_deliver_decisions`, `_delivered_index`).

The defects shipped anyway, for four reasons that have nothing to do with the engine's design and everything to do with **when checks run, what blocks, and what is never re-run.**

The single highest-value sentence in this report:

> **Running `gov.py analyze` on SEC's artifacts *right now* returns `CRITICAL: 1 · BLOCKED`. The verdict stored beside those same artifacts says `CRITICAL: 0 · CLEAN`. The pipeline gated on the stored verdict.**

---

## 2. Evidence

### 2.1 The stored verdict contradicts the code

```bash
cd /Users/ezzat/factory
.venv/bin/python -c "
import sys; sys.path.insert(0,'governance-tools')
import analyze as an
rep = an.run('SEC', 1, scope='stage:P3.1', write=False)
print(rep.counts(), 'clean:', rep.clean)"
```

| | `_state/analyze-stage-P3.1.json` (stored, gated on) | fresh run, same artifacts |
|---|---|---|
| CRITICAL | 0 | **1** |
| MAJOR | 4 | 4 |
| verdict | `CLEAN` | **`BLOCKED`** |

The missing CRITICAL is C7.10 `value-agreement`:
`DBF-SEC-064 is ['grant_at'] in backend-execution-plan but ['granted_at'] in db-script`.

The detector is not broken — verified directly:

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0,'governance-tools'); import analyze as an
p=open('erp/modules/SEC/P3_1/backend-execution-plan-sec.md').read()
d=open('erp/modules/SEC/P2/db-script-sec.md').read()
print(an._binding_lines(d,'DBF')['DBF-SEC-064'], an._binding_lines(p,'DBF')['DBF-SEC-064'])"
# {'granted_at'} {'grant_at'}
```

### 2.2 The checks postdate the modules

```bash
git show 6a1efef:shared/ARTIFACT-CONTRACTS.md | grep -c 'check:'   # 73  (SEC's P3.1 commit, 09-10 20:02)
grep -c 'check:' shared/ARTIFACT-CONTRACTS.md                      # 80  (today)
git show 6a1efef:shared/ARTIFACT-CONTRACTS.md | grep -c 'C7.10'    # 0
```

All three modules were generated inside a ~40-minute window (SEC 20:02, MDL 20:16, FIN 20:43 on 09-10). The six mechanical checks landed in `2be511f`, 09-11 00:33 — **after all three.** No module has been re-analyzed since.

**Consequence:** every `PASSED ✓ — 0 findings` in the FIN and MDL plans carries exactly as much evidence as SEC's did, which is none.

### 2.3 Detected-and-ignored

The stored SEC report *does* contain four `code-format` findings, at lines 410, 411, 1213, 1267 — the same lines found by hand weeks later, describing the same defect (`SEC-<3-digit>` declared, `SEC-409-USER-DUP` emitted). They were written to disk, classified `MAJOR`, and the run proceeded.

`governance-tools/analyze.py:66-68`:

```python
@property
def clean(self) -> bool:
    return self.count("CRITICAL") == 0
```

`gov.py:124` → `if not rep.clean: return BLOCKED`. A MAJOR finding therefore blocks nothing, ever. The defect was found, recorded, and shipped.

### 2.4 Delivery ran on older code

`backend/governance/modules/SEC/manifest.json` says `"root": "erp/modules/SEC"` with no `paths_relative_to` key. The current `gov.py:_delivered_index` emits `"root": "."` plus `"paths_relative_to": "the directory holding this file"`, and `_deliver_decisions` copies the ADR files into the delivered tree.

So the dangling `erp/decisions/SEC/ADR-SEC-001.md` citations that look like fabrications in the backend repo are **real files** (`erp/decisions/SEC/ADR-SEC-001.md` and `-002.md` both exist here) that an older delivery never copied. Fixed in code; never re-delivered.

### 2.5 The engine text was already right

`engines/P3.1/references/ENGINE.md:452-455` tells the author precisely what to do, and §9's table names all six mechanical checks and states "ALIGN is the *prose* half of the check and **it is not the authority**."

The authoring model printed `PASSED ✓ — 0 findings` regardless — because the mechanical half handed it `CLEAN`, and because nothing downstream ever compared the prose verdict against the machine verdict.

---

## 3. Root causes

| # | Root cause | Evidence | Blast radius |
|---|---|---|---|
| **RC1** | **Only `CRITICAL` blocks.** The blocking threshold is a literal in Python, in two places, and appears nowhere in `factory.yaml`. | `analyze.py:68`, `gov.py:943` | Every MAJOR finding ever produced, in every module, was advisory. Gap #1 shipped this way. |
| **RC2** | **No re-analysis after the rules change.** A stored verdict is trusted indefinitely; strengthening a check does not invalidate any prior PASS. | §2.1 + §2.2 | All three modules hold verdicts produced by a 73-check contract set now superseded by 80. |
| **RC3** | **Delivery is not idempotent and carries no provenance.** Artifacts delivered by an old toolchain are indistinguishable from ones delivered by the current toolchain. | §2.4 | Every path defect and every dangling ADR citation in the backend repo. |
| **RC4** | **The prose verdict is never reconciled with the machine verdict.** ALIGN's `RESULT` line is authored by a model and written into the shipped plan; `analyze`'s verdict lives in `_state/` and is read by nobody downstream. | §2.3 + §2.5 | The delivered plan asserts `PASSED ✓ — 0 findings` while the report beside it lists five findings. The consumer reads the plan. |

**Not a root cause** — worth stating plainly, because it was the initial hypothesis: the engines are not weak, the checks are not missing, and the model did not fabricate the ADRs.

---

## 4. Hardcoding — the one fact that is not in `factory.yaml`

`factory.yaml:4` states the design rule:

> `# Every factory fact lives here and ONLY here: stages, passes, gates, lanes, ...`

The codebase honours that almost completely. `gov.py`'s own header — "Nothing here spells a stage id, phase key, path, branch or model" — holds up under grep: no stage id, module code, or path literal appears in the orchestrator.

**The exception is the most consequential policy in the pipeline: what blocks a release.**

| Location | Hardcoded | Should be |
|---|---|---|
| `analyze.py:37` | `SEV = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}` | the severity vocabulary, from config |
| `analyze.py:68` | `return self.count("CRITICAL") == 0` | `blocking_severities` from config |
| `gov.py:943` | `BLOCKED if any(f.severity == "CRITICAL" ...)` | the same config value, read once |

Three literals, one policy, zero configurability — and the file that claims to hold every factory fact holds none of it. `grep -i "severity\|blocking\|threshold" factory.yaml` returns nothing relevant.

A second, minor instance: `render.py:155` hardcodes the track names `"backend"`/`"frontend"` in a display table, where `CFG.tracks` is available.

---

## 5. Fix plan

Ordered by leverage. F1 and F2 together would have stopped every defect in this report.

> **Every fix in this section is project-agnostic by construction.** The factory is a meta-tool:
> the ERP profile is one input, not the subject. A fix that encodes an ERP fact — a stack, a
> dialect, a naming convention, a module code — is itself a new instance of the defect this
> report is about. Each fix below is therefore stated as a **factory invariant**, with the ERP
> situation used only as the evidence that motivated it. Anything genuinely specific to the
> current project lives in §6, which is a remediation backlog, not an engine change.
>
> Two rules govern the whole section:
> 1. **No new literal.** If a fix needs a value, that value is declared in `factory.yaml` (a
>    factory fact) or in the profile (a project fact) — never in Python, never in an engine's
>    prose.
> 2. **No new assumption about a stack.** No fix may name a language, a database, a framework,
>    an ORM, a migration tool, or a naming convention. Those are profile territory.

### F1 — Make the blocking policy a config fact (closes RC1, closes the hardcoding gap)

Add to `factory.yaml`:

```yaml
analyze:
  severities: [CRITICAL, MAJOR, MINOR]   # ordered, most severe first
  blocking: [CRITICAL, MAJOR]            # a finding at or above this blocks the stage
  # per-stage or per-contract overrides may narrow this, never widen it
```

Then:
- `analyze.py:37` builds `SEV` from `CFG.data["analyze"]["severities"]`.
- `analyze.py:68` becomes `return not any(f.severity in CFG.blocking for f in self.findings)`.
- `gov.py:943` reads the same value — one source, two readers.
- Any severity string in a contract clause that is not in the configured vocabulary is itself a finding (the same defensive pattern `run()` already uses for an unknown check name — copy it).

**Decide deliberately whether `MAJOR` blocks.** It should: every defect in this report that was *detected* was detected as MAJOR. If some MAJOR clause is genuinely advisory, demote that clause to MINOR rather than keeping a blanket escape hatch.

### F2 — Invalidate a verdict when its inputs or its rules change (closes RC2)

A stored `analyze-*.json` must record what it was produced by, and be refused when that no longer matches:

```json
"provenance": {
  "contracts_sha": "<sha256 of shared/ARTIFACT-CONTRACTS.md>",
  "analyze_sha":   "<sha256 of analyze.py>",
  "inputs":        {"backend-execution-plan": "<sha256>", "db-script": "<sha256>"}
}
```

`gov.py` refuses to gate on a report whose `provenance` does not match the current state, and re-runs instead. This is cheap — `analyze` is fast and pure — and it turns "we strengthened the checks" into "every module is re-verified on its next touch", automatically.

Ship with a `gov.py analyze --all-modules` sweep so the backlog is one command.

### F3 — Reconcile the prose verdict with the machine verdict (closes RC4)

A model-authored verdict inside a shipped artifact is the only verdict the downstream implementer ever sees, and today nothing checks it.

**Invariant:** *no artifact may assert a verdict about itself that contradicts the machine verdict for the same scope.*

Add a check — `verdict-agrees` — that reads the self-check verdict out of an artifact and fails when it claims fewer findings than `analyze` produced for that stage. Severity from config (see F1).

**Keep it generic.** The check must not know the words `ALIGN` or `RESULT`, or any heading shape: another profile will name its self-check differently, or have none. Take both from the contract clause's own args, the way every other check already does:

```yaml
- {id: C7.15, check: verdict-agrees,
   args: {artifact: <artifact key>, block: <self_check.block_key>, line: <self_check.verdict_label>},
   severity: <from config>}
```

with the block/label values coming from the profile or the stage definition, not from the checker. A profile that declares no self-check simply carries no such clause, and the check never runs.

**Better still — generate the verdict instead of checking it.** Have `render` write the verdict line from the analyze report, and have the engine spec instruct the author to leave it alone. A generated verdict cannot drift from its own evidence, and this removes an entire class of defect rather than detecting it. Prefer this; keep `verdict-agrees` as the guard for artifacts a model still authors by hand.

This is the structural answer to "the model ignored the instruction": stop relying on the instruction.

### F4 — Stamp and verify delivery provenance (closes RC3)

- Write `toolchain_version` (a git describe / sha of the factory) into the delivered `manifest.json`.
- On `deliver`, if the destination already holds a manifest from an older toolchain, re-deliver the whole module rather than merging into it.
- Add a `gov.py verify-delivery --track backend -m MOD` that re-runs `paths-resolve` and `refs-exist` **against the delivered tree**, not the factory tree. Today both checks pass in the factory and fail in the consumer, which is the one place they matter. This is the check that would have caught the `erp/` prefix and the missing ADRs.

### F5 — Two engine-content invariants the checks cannot see

Both are genuine engine issues, independent of the four root causes. Both are stated as invariants; the ERP instance is only the evidence.

**F5a — A dialect default must never silently become a project decision.**

Where a stack choice has more than one valid answer, the profile must state which one, and the engine must emit the profile's answer rather than whatever the dialect's syntax map happens to yield. A default that no one chose is indistinguishable, downstream, from a decision that was made — and the implementer inherits it with no way to tell.

*Evidence:* `stack.db.syntax_map` for one dialect yielded an identity-column form for primary keys, and the engine restated it per entity as though it were a decision. The consuming repository had already been built on a different, equally valid strategy under applied migrations that cannot be rewritten — so the "default" was a breaking choice nobody recorded.

*Fix, generically:* audit `profiles/_schema.yaml` for every place a `syntax_map` or dialect table supplies a value that (a) has a real alternative and (b) is restated in a generated artifact. Promote each to an explicit, required profile key. Where a profile omits it, that is a lint finding, not a silent default. **Do not encode any particular answer in the engine** — the whole point is that the answer becomes a stated project fact.

**F5b — A value that is a config fact must be rendered, never restated by the author.**

If the engine asks a model to write out a value that the factory or the profile already knows, the two will drift. `C7.11` exists only because of this: a format sentence, maintained as free text, disagreed with the values it described.

*Fix, generically:* sweep every `ENGINE.md` for prose that restates a `factory.*` or `profile.*` value, and replace it with the template expression that renders it. The pattern is already used elsewhere in the same files, so this is consistency work, not new machinery. Each mechanical check that exists purely to detect such a drift then becomes a safety net rather than the only line of defence — and the corresponding class of finding stops being produced at all.

### F6 — Two things the current design cannot catch, and should

**F6a — An artifact must not state as fact what it cannot verify at its own stage.**

A planning stage runs before any implementation exists, so any name it invents for an implementation artifact is a guess. Stated in a table of facts, a guess is indistinguishable from a decision, and the downstream reader has no way to tell which columns were derived and which were imagined.

*Evidence:* 14 of 27 rows in one module's API-contract table named request/response types that never existed in any implementation. No upstream check could have caught it — the code did not exist yet.

*Fix, generically:* wherever a stage emits a column it cannot resolve at that stage, the engine marks that column **proposed** (a single agreed token, declared once in `factory.yaml`), and a later stage that *can* resolve it fills it from the built artifact. Add a lint rule: a column declared proposed-capable that is emitted without the marker, and without a resolvable source, is a finding. This generalises past DTO names to every forward-referencing column any profile may define.

**F6b — Cross-artifact references must resolve where they are consumed, not only where they are written.**

`xref-resolve` resolves `ID`-shaped citations against the owning module's registry — correct, but it only sees ids. A prose reference to another module's surface ("read X through Y's such-and-such API") is invisible to it, and a prose reference is exactly how one module encodes a dependency it has not yet been given an id for.

*Evidence:* one module's plan described obtaining data through another module's read API; the target module's registry defined no such endpoint. Both modules' checks passed, because each validated only its own artifacts.

*Fix, generically:* extend `xref-resolve` (or add a sibling) to resolve named references to another module's declared surface, not just id citations — and run the resolution **across the module set**, not per module. Pair it with F4's delivered-tree verification so the same reference is re-resolved in the consumer, where it actually has to hold.

---

## 6. Project-specific remediation — the current ERP run

> Everything above is a change to the factory and applies to any project it ever runs.
> **This section is the opposite**: a one-off backlog for the modules already generated under
> the ERP profile. Nothing here belongs in the engine, in `factory.yaml`, or in any check.

1. **Do not trust any of the three ALIGN verdicts.** All were produced under the 73-check contract set.
2. Run, in the factory, for each module: `gov.py analyze -m <MOD> --scope all`. Expect findings; SEC alone yields 1 CRITICAL + 4 MAJOR + 1 MINOR today.
3. Fix the findings **in the factory**, then re-`split` and re-`deliver`. The backend repo's copies have already been hand-corrected for SEC (error-code format, `granted_at`, the ALIGN RESULT line, five GET→POST endpoint reversals, the DOC DTO table, the INT-C cross-module statement); those corrections must be reproduced upstream or the next delivery will regress them. A diff of the delivered SEC tree against a fresh delivery is the fastest way to enumerate them.
4. FIN and MDL have not been implemented yet. Re-analyzing and re-delivering them **before** implementation starts is the cheapest this will ever be.

---

## 7. One-line summary

The factory's checks, contracts and engine text are sound; what failed is that **MAJOR findings never blocked, stored verdicts were never invalidated when the rules got stricter, deliveries carried no provenance, and a model-authored `PASSED ✓` was never reconciled against the machine's own report** — and the blocking policy that would have stopped all of it is the one fact hardcoded in Python instead of declared in `factory.yaml`.
