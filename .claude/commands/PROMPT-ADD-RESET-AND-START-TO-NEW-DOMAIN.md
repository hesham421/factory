# Execution prompt — make `new-domain` reset stale project content and immediately start the new project (paste into Claude Code, run on the standalone `hesham421/factory.git` repo, or its embedded copy)

**Run this with an agent/session that has full read/write/delete access to the whole repo** — this command is destructive by design (it deletes prior analysis content) and must never run through a read-only delegate lane or a sandboxed relay.

## Why

Every new project reuses the same factory template (per the "one repo per project" model already agreed). Right now, starting a genuinely new project after a prior one (or after any test run) requires manually remembering what to delete — which is exactly how the ERP/"simple note" mix-up happened (`DEMO`, nested in `profiles/erp.yaml`, leaked ERP framing into an unrelated test idea). The fix is to make the reset a real, built-in, repeatable step of the tool itself — not a habit to remember.

## Before changing anything

1. Read `factory.yaml → commands: → new-domain` and whatever `gov.py` function currently backs it — confirm its actual current behavior before extending it. Report what it does today.
2. Confirm the current live path-key names (`project` vs `domain`/`platform` — this may differ depending on whether the earlier restructuring prompt has been run on this checkout) and scope the reset accordingly, from what's actually on disk, not from memory of an earlier conversation.

## What to build

### 1. `new-domain` becomes reset-then-start, in one command

Extend the existing `new-domain` command (don't rename it, don't create a parallel command) so running it does, in order:

**Step A — Safety check.** Run `git status --short`. If there are uncommitted changes, STOP and tell the user to commit or stash first — never silently discard uncommitted work. This check cannot be skipped even with `--yes` (below).

**Step B — Print what will be deleted, and wait for confirmation** (unless `--yes`/`--force` is passed, for scripted/non-interactive use):
```
══════════════════════════════════════════════════════
RESET — this will permanently delete:
  profiles/*.yaml                (N files)
  modules/*                      (N module folders)
  decisions/*                    (N files)
  <project-path>/ generated content (domain-profile.md, project-registry.md, etc.)
Kept: governance-tools/, templates/, factory.yaml's own structure,
      _archive-v5/, history/, tests
══════════════════════════════════════════════════════
Proceed? [y/N]
```

**Step C — Delete**, exactly the scope confirmed in Step B. Nothing outside that explicit list — do not touch `_archive-v5/`, `history/`, `governance-tools/`, `templates/`, or the tests directory.

**Step D — Reset `factory.yaml`'s own instance-specific values** (not its structure): clear `repos.<name>.checkout_env`/`checkout_default` back to placeholder/empty values — a fresh project has no consumer repos linked yet. Leave `paths:`, `lanes:`, `commands:`, `stages:` untouched — those are the tool's own mechanism, not project data.

**Step E — Immediately continue into the domain-profile stage** (whatever currently starts that interactive interview — check how `bootstrap` currently kicks it off and reuse the same entry point) in the same run, so the user lands directly in the new project's first real question. Do not require a second manual command.

### 2. Explicit profile-selection safeguard

Separately, while reading through this code: confirm whether profile selection (which `profiles/*.yaml` file is "active" for a run) already requires an explicit choice, or silently defaults to whichever file exists. After Step C above, there will be zero `profiles/*.yaml` files left, so an explicit "which profile / create a new one named ___" prompt becomes unavoidable at the next `domain-profile` run regardless — confirm this is genuinely the case (no silent fallback path exists) and report if you find one.

## Constraints

- No hardcoding: the list of files to delete in Step B/C must be computed by scanning the actual directory structure at runtime (`profiles/*.yaml`, `modules/*`, `decisions/*`), never a literal list of today's filenames — this must keep working correctly as new profiles/modules get added over a project's life.
- Never touch `_archive-v5/`, `history/`, `governance-tools/`, `templates/`, or anything under the tests directory.
- The git-status safety check (Step A) is non-negotiable, including in `--yes`/non-interactive mode.
- Cover this with a real test in `governance-tools/tests/` (using a `tmp_path` fixture repo, per the existing test conventions) — simulate a populated project state, run the reset, assert the exact kept/deleted set, and assert it refuses to run over uncommitted changes.
- One commit.

## Acceptance criteria

- `python3 governance-tools/gov.py new-domain` on a populated project: prints the confirmation summary, refuses without explicit `y` (or `--yes`), deletes exactly the scoped content, leaves `governance-tools/`/`templates/`/`_archive-v5/`/`history/` untouched, resets `repos:` values, and proceeds directly into the domain-profile interview.
- `python3 governance-tools/gov.py new-domain` with uncommitted changes present: stops at Step A, makes no deletions.
- `python3 -m pytest governance-tools/tests -q` fully green, including the new reset test.
- `python3 governance-tools/gov.py lint` returns 0 critical / 0 major / 0 minor.
