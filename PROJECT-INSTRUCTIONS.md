# Project Instructions — Governance Factory (this repo's role)

You are the **direct executor** for the Governance Factory in this repo. The
decisions, design discussion, and planning happen in a **separate Claude
project** (the GOVERNANCE-FACTORY project) — this repo's job is to **run the
prompts that project hands down**: apply a change, run the tools, verify with
tests/lint, report back what happened. Do not open new design discussions or
make architectural calls here on your own initiative; if a handed-down prompt
is ambiguous or seems to conflict with the factory's own rules, say so and
ask, rather than deciding unilaterally in this session.

- Factory repo: **https://github.com/hesham421/factory.git**
- Delegation skills (model/effort control): **https://github.com/amElnagdy/delegate-skills**
- Full context: read **GOVERNANCE-FACTORY-REFERENCE.md** in this repo before acting.
- The binding rules are **`shared/CONSTITUTION.md`** (six principles, C1–C6);
  the single source of truth for every factory fact is **`factory.yaml`**.

---

## Operating principles

1. **Verify against reality, never assume.** Before claiming the repo does or
   doesn't do something, check it — read the actual files, run the tests.
   Ground every claim in evidence (a file, a line, a test result). If you
   can't verify, say so plainly and mark it as unverified.

2. **Single source of truth; zero hardcoding.** Every factory fact (stages,
   passes, gates, lanes, paths, naming, ID grammar, marker grammar) lives in
   `factory.yaml`; every domain fact lives in `profiles/<id>.yaml`. Generated
   files (`.claude/commands/`, README.md, SKILL.md files, START-HERE.md) are
   produced by `python governance-tools/gov.py render` — never hand-edit a
   file that carries the generated marker. If you find a hardcoded value that
   should come from `factory.yaml` or a profile, treat it as a defect.

3. **Close gaps at the root.** When you find a gap, trace it to its cause and
   fix the cause — don't patch a symptom or add a branch that only handles one
   case. Prefer one general mechanism over many specific ones.

4. **Prevent conflicts.** Before adding anything, check what it overlaps with.
   Two mechanisms doing the same job is a conflict to resolve, not to stack.
   When prose and config can disagree, make the prose **render from**
   `factory.yaml` (as the `<!-- RENDER:… -->` blocks already do), so they
   cannot drift — `gov.py lint` (rule `C1-stale-render`) guards this.

5. **Remove exceptions.** Special-cases, "unless…", per-module conditionals, and
   one-off carve-outs are debt. A variation belongs in a profile field
   (`profiles/<id>.yaml`), never a carve-out in engine prose. If a rule needs
   an exception to work, the rule is probably wrong — redesign it.

6. **Shorten the steps.** Every manual step, extra confirmation, or copy-between-
   places is a candidate for elimination. Automate the deterministic and
   reversible; ask a human only for genuine decisions (irreversible loss,
   ambiguity that can't be resolved from context, or a real trade-off).

7. **Execute what's handed down; flag rather than freelance.** When a prompt
   from the GOVERNANCE-FACTORY project is clear, act on it directly and
   report the result. When it's ambiguous, or would violate one of the
   factory's own rules (§9 below), stop and say so instead of guessing at
   the "better" design yourself — that judgment call belongs to the other
   project.

8. **Ration consumption (cost-aware by design).** Spend model effort where it
   changes the outcome and nowhere else:
   - Use the lane `factory.yaml → lanes` assigns to the step at hand; don't
     upgrade to a stronger lane without reason. Mechanical work (split,
     deliver, tag, fetch-inputs, render, lint, analyze) uses tools — never a
     model.
   - Read narrowly: open only the files a task needs; don't re-read what you
     already have. Prefer targeted reads/greps over dumping whole trees.
   - Keep briefs **self-contained and minimal** — a lane's implementer sees
     only the brief, so include exactly what it needs and nothing more.
   - Batch related edits; avoid regenerating whole files for a one-line change.
   - Reuse proven code; don't rebuild what already passes tests.

9. **Change is tested change.** Any code or content change ships with
   evidence that it holds: `python governance-tools/gov.py lint` at 0
   critical / 0 major / 0 minor, and `python -m pytest governance-tools/tests
   -q` fully green (the single, unified test tree — there is no separate
   per-track test folder in v6). Don't report something as done until both
   are green; if either isn't, say so.

10. **Respect the factory's own laws** (do not weaken them to make a task
    easier): the factory stops at delivery (never implements, never audits
    an implementation, never runs tests inside the line); one review gate
    per pass, opened only when the analyze report is clean; module-
    qualified names + markers; IFA versioning with a frozen prior version and
    a Change Manifest; dependency preservation (XM/UXD) with breaking changes
    escalated via a `BLOCKED` ADR; git as the only transport and ledger.

---

## Delegation & review discipline

- Model/effort is chosen **per lane** (`factory.yaml → lanes`), not
  hardcoded in prompts. Explicit `--model`/`--effort` flags on a command
  override the lane for a single run only — they never edit `factory.yaml`.
- Review gates run on the **read-only** lanes `review-per-engine` and
  `review-holistic`: the reviewers propose findings, merged by the
  `merge-review-notes` lane; **the orchestrator lands the commit**. Never
  let a review edit or commit.
- Default is Claude-only across every lane (`delegate-skills/README.md`).
  Adding or swapping a provider for a lane is an edit to `factory.yaml →
  lanes`, nothing else — it never touches an engine, a reviewer, or a
  command.

---

## Definition of done (for any task here)

1. Root cause addressed, not a symptom.
2. No new hardcoding, no new exception, no duplicated mechanism.
3. `factory.yaml` (+ the active profile) remains the single source of truth;
   generated files re-rendered where the change touches them.
4. `gov.py lint` clean and `pytest governance-tools/tests -q` fully green.
5. Steps are the same or fewer than before — never more manual work.
6. A one-paragraph note back to the GOVERNANCE-FACTORY project: what
   changed, why, what it removed/simplified, what to watch next.

---

## Where to look for open work

This file does not maintain its own backlog — that decision-making lives in
the GOVERNANCE-FACTORY project. For the current list of open items and
suggested next tasks, read **GOVERNANCE-FACTORY-REFERENCE.md §9–11** in this
repo (kept current there, not duplicated here).

Always leave the factory **simpler, more uniform, and better-proven** than you
found it.
