# Prompt — apply the factory fix plan

> Hand this to a session working **inside `/Users/ezzat/factory`**. It is self-contained.
> The companion diagnosis, with the reproduction for every claim, is
> `FACTORY-DEFECT-ANALYSIS-AND-FIX-PLAN.md` in this same directory — **read it first, in full.**

---

## Copy everything below this line into the session

---

You are working on the Governance Factory (`gov.py`, `factory.yaml`, `profiles/`, `engines/`, `shared/ARTIFACT-CONTRACTS.md`). Your job is to apply a six-part fix plan that closes four root causes, each of which let a defect ship into a consuming repository.

**Read `FACTORY-DEFECT-ANALYSIS-AND-FIX-PLAN.md` in this directory before touching anything.** It carries the evidence for every claim below and the exact commands that reproduce it. Do not take my summary on trust — re-run at least §2.1 and §2.2 yourself, and say what you got.

---

## The one rule that governs every change you make

**This factory is a meta-tool. It generates governance artifacts for *any* project, domain or stack. The ERP profile currently loaded is one input, not the subject.**

Therefore:

1. **No new literal.** If a fix needs a value, it is declared in `factory.yaml` (a factory fact) or in a profile (a project fact). Never in Python. Never as prose inside an engine.
2. **No new assumption about a stack.** No change you make may name a language, database, dialect, framework, ORM, migration tool, API style, or naming convention. Those are profile territory, always.
3. **No new assumption about a domain.** No module code, entity name, or business concept from the current project may appear anywhere in the engine, the toolchain, or the contracts.
4. **A check must not know the vocabulary of one profile.** Any word a check needs — a block name, a label, a marker token — arrives through its contract clause's `args`, the way every existing check already does.
5. **If a fix cannot be made generic, do not make it.** Report it instead, with what a profile key would have to express.

Before you finish, grep your own diff for violations of rules 2 and 3. A fix that hardcodes the thing it was written to prevent is worse than no fix.

### The harness that proves it — use it, do not reinvent it

`governance-tools/tests/test_agnostic.py` already exists and is exactly the right tool. It writes a **toy profile from a different domain entirely** (an outpatient clinic: module prefixes `PAT`/`APT`/`BIL`, its own phase keys `FOUNDATION`/`RECORDS`/`ENDPOINTS`/`LINKS`/`WRAP-UP`, a single language, its own split thresholds) and drives the same toolkit through it, asserting the profile's vocabulary is live in `CFG` and that the parser and splitter follow the toy's phases rather than any built-in ones.

**This is the enforcement mechanism for the one rule above.** For every fix you make:

1. Extend `test_agnostic.py` so the toy profile exercises the new behaviour too — a toy `analyze` severity policy for F1, a toy self-check block name and verdict label for F3, a toy proposed-token for F6a, and so on.
2. A fix is not done until it passes **under the toy profile**, not merely under ERP. If it only works when the profile happens to be ERP-shaped, you have written a literal in disguise.
3. If extending the toy profile for your fix is awkward, that awkwardness is the signal: the value you are threading is not yet a proper profile fact. Fix that first.

Passing `test_agnostic.py` is stronger evidence than any grep. Do both, and report both.

---

## What already works — do not "fix" these

The instinct will be to assume the engine is weak. It is not. Verified:

- `engines/*/references/ENGINE.md` already specify the right behaviour, including an explicit warning against a self-check that always prints PASSED.
- All six mechanical checks (`value-agreement`, `code-format`, `data-source`, `xref-resolve`, `refs-exist`, `paths-resolve`) are implemented in `analyze.py` and wired in `shared/ARTIFACT-CONTRACTS.md`.
- `analyze.run()` already turns an unknown check name and a raised exception into findings rather than silence — **copy that defensive pattern** wherever you add something similar.
- `gov.py`'s orchestrator is already fully config-driven; its header rule ("nothing here spells a stage id, phase key, path, branch or model") holds under grep. Keep it holding.
- `gov.py:_deliver_decisions` / `_delivered_index` already do the right thing.

The defects shipped because of *when* checks run, *what* blocks, and *what is never re-run* — not because the checks are missing.

---

## F1 — Make the blocking policy a config fact

**Problem.** The blocking threshold is a literal in two places and appears nowhere in `factory.yaml`, whose own header claims every factory fact lives there and only there. MAJOR findings have therefore never blocked anything — including four findings that named, by line number, a defect that then shipped.

- `analyze.py:37` — `SEV = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}`
- `analyze.py:68` — `return self.count("CRITICAL") == 0`
- `gov.py:943` — `BLOCKED if any(f.severity == "CRITICAL" for f in fs) else OK`

**Do.**
1. Add a block to `factory.yaml` declaring the severity vocabulary (ordered, most severe first) and which severities block. Choose the key names to fit that file's existing style — read it first; do not impose a shape.
2. `analyze.py` builds its severity ordering from that config instead of the module-level dict.
3. `AnalyzeReport.clean` becomes "no finding at a blocking severity", read from config.
4. `gov.py` reads the same config value. **One source, two readers** — do not duplicate the predicate.
5. A severity string used in a contract clause that is not in the configured vocabulary is itself a finding, at the highest configured severity. Mirror the existing unknown-check pattern in `run()`.

**Decide deliberately whether MAJOR blocks, and say which way you went and why.** The evidence says it should: every defect that was *detected* was detected as MAJOR and ignored. If some clause is genuinely advisory, demote that clause to MINOR rather than keeping a blanket escape hatch — a policy with an exception for everything is not a policy.

Report the full before/after count: how many contract clauses currently sit at each severity, and how many stages would newly block under your chosen setting. If that number is large, say so — it is a real cost and the user should see it before it lands.

---

## F2 — Invalidate a verdict when its inputs or its rules change

**Problem.** A stored `_state/analyze-*.json` is trusted indefinitely. Strengthening a check does not invalidate any prior PASS. At generation time the contract set had 73 checks; it now has 80 — and no module has been re-analyzed. Every stored verdict in this factory was produced under a rule set that no longer exists.

**Do.**
1. Extend the analyze report with a provenance record: a digest of the contracts document, a digest of the checker implementation, and a digest of each input artifact the run actually read. Derive the artifact list from what the run consumed — do not hardcode a list of artifact names.
2. `gov.py` refuses to gate on a report whose provenance does not match current state, and re-runs instead of trusting it. `analyze` is fast and pure, so the safe default is: when in doubt, re-run.
3. Add a sweep command that re-analyzes every module at its current version, so clearing the backlog after a rules change is one command. Take the module list from state, never from a literal.
4. Make the report's `skipped` list survive into the JSON — today it is written to the Markdown and dropped from the JSON, so a programmatic consumer cannot see that a clause did not run.

Also fix, while you are here: the stored report's generated-at timestamp did not match its own commit time. Check whether `now_iso()` is producing a correct, timezone-honest value, and report what you find.

---

## F3 — Reconcile the authored verdict with the machine verdict

**Problem.** A model authors a verdict line inside the shipped artifact; the machine writes its own verdict into `_state/`. Nothing compares them. The shipped artifact asserted zero findings while the report beside it listed five. The consuming implementer reads the shipped artifact.

**Do — in this order of preference.**

1. **Preferred: generate the verdict.** Have the render path write the self-check verdict from the analyze report, and change the engine spec so the author is told to leave that line alone. A generated verdict cannot drift from its own evidence, and this removes the defect class instead of detecting it.
2. **Guard what is still hand-authored:** add a `verdict-agrees` check that reads the verdict out of an artifact and fails when it claims fewer findings than the machine produced for that scope.

**Generic-by-construction requirement for the check.** It must not know the block name, the label, or the heading shape of any profile's self-check — another profile will name it differently or have none. Those come from the clause's `args`, resolved from the profile or stage definition, exactly as every other check's args already work. A profile with no self-check carries no such clause and the check never runs. Severity from F1's config.

---

## F4 — Stamp and verify delivery

**Problem.** Artifacts delivered by an older toolchain are indistinguishable from ones delivered by the current toolchain. A delivered index in the consuming repo still carries factory-rooted paths and lacks keys the current code emits — so every path it names dangles for the one reader it was written for, and nothing detects that.

**Do.**
1. Record the toolchain identity in the delivered index (a git describe or sha of the factory).
2. On delivery, when the destination already holds an index from a different toolchain identity, re-deliver the module wholesale rather than merging into it.
3. Add a command that re-runs the path- and reference-resolution checks **against the delivered tree in the consumer**, not against the factory tree. This is the decisive one: both checks pass in the factory and fail in the consumer, and the consumer is the only place they matter.
4. Keep the consumer location resolution exactly as it is — `factory.yaml → repos` with env override. Do not introduce a path literal.

---

## F5 — Two engine-content invariants

**F5a — a dialect default must never silently become a project decision.**

Where a stack choice has more than one valid answer, the profile states which one and the engine emits the profile's answer — not whatever a syntax map happens to yield. A default nobody chose is indistinguishable downstream from a decision that was made.

*Do:* audit `profiles/_schema.yaml` and the dialect/syntax tables for every value that (a) has a real alternative and (b) gets restated in a generated artifact. Promote each to an explicit profile key. A profile that omits one is a lint finding, not a silent default. **Encode no particular answer in the engine** — the point is that the answer becomes a stated project fact. List every key you added and the alternatives each admits.

**F5b — a value that is a config fact must be rendered, never restated by an author.**

*Do:* sweep every `ENGINE.md` for prose that restates a `factory.*` or `profile.*` value, and replace it with the template expression that renders it. The same files already use that pattern elsewhere, so this is consistency work. Report each site you changed. Where a mechanical check exists only to detect that class of drift, note that it becomes a safety net rather than the sole defence — do not remove it.

---

## F6 — Two gaps the current design cannot see

**F6a — an artifact must not state as fact what it cannot verify at its own stage.**

A planning stage runs before any implementation exists, so a name it invents for an implementation artifact is a guess; printed in a table of facts it is indistinguishable from a decision. (Evidence: 14 of 27 rows in one module's contract table named types that never existed.)

*Do:* where a stage emits a column it cannot resolve at that stage, the engine marks it with an agreed *proposed* token declared once in `factory.yaml`; a later stage that can resolve it fills it from the built artifact. Add a lint rule for a proposed-capable column emitted without the marker and without a resolvable source. Keep it general — this must cover any forward-referencing column any profile defines, not one table in one profile.

**F6b — references must resolve where they are consumed.**

`xref-resolve` sees `ID`-shaped citations only. A prose reference to another module's surface is invisible to it — and prose is exactly how a module encodes a dependency it has no id for yet. (Evidence: one module's plan described obtaining data through another module's read API; the target defined no such endpoint. Both modules passed, because each validated only itself.)

*Do:* extend `xref-resolve` or add a sibling that resolves named references to another module's declared surface, run across the module set rather than per module. Pair with F4 so the same reference is re-resolved in the consumer.

---

## Constraints

- `governance-tools/tests/` exists and is the safety net for this work. **Run it before you start** to establish a baseline, and after every fix. A fix that breaks a test is not done. Add tests for each new behaviour — especially F1's config-driven threshold and F3's verdict comparison, both of which are pure functions and cheap to test.
- Do not change any artifact under `erp/` — that is generated project content, and §6 of the diagnosis handles it separately. Your scope is the engine, the toolchain, the contracts and the profile schema.
- Do not regenerate, re-split or re-deliver any module as part of this work. Applying the fixes and remediating the existing modules are two jobs; this is the first one.
- Commit per fix, with the F-number in the message, so any single fix can be reverted independently.

## Report back

1. Your own reproduction of §2.1 and §2.2 of the diagnosis — what you ran, what you got, and whether it matches.
2. Per fix F1–F6: what you changed, the files, and the config keys you added (with the value each admits).
3. **The MAJOR-blocks decision**: which way, why, and how many stages would newly block.
4. Test results: baseline before, and after each fix.
5. **Your self-audit against the one rule** — two pieces of evidence: (a) the grep you ran over your own diff for stack names, domain names and new literals, with its output; and (b) **what you added to `test_agnostic.py` per fix, and its passing output** — the toy non-ERP profile exercising every new behaviour is the real proof, the grep is only the backstop.
6. Anything you could not make generic, and what a profile key would have to express to make it so.
7. Anything in the diagnosis you found to be wrong. It was written from outside this repository; say so if it is.
