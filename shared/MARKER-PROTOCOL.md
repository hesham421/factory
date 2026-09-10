# MARKER PROTOCOL — addressability of plans, and how the toolkit splits them

```
Doc            : shared/MARKER-PROTOCOL.md
Role           : the canonical marker specification; the toolkit (paths.tools/toolkit) is its executable form
Loaded by      : plan-producing stages (stages/standalone with produces[*].plan), gov.py analyze (clause `markers`), gov.py split
Generated parts: RENDER:markers · RENDER:phases:backend:exec · RENDER:phases:backend:test · RENDER:phases:frontend:exec · RENDER:phases:frontend:test
Links          : GOVERNANCE-CORE.md · ARTIFACT-CONTRACTS.md · VERSIONING.md
```

**One executable spec.** The grammar is `factory.markers`; the phase
vocabulary is `profile.tracks.<track>.plans.<plan>.phases`; the parser,
validator, autofix, splitter and verifier are the single toolkit under
`paths.tools`. If this document and the toolkit disagree, the toolkit's tests
decide and this document is corrected.

## 1. Purpose

Markers are comments embedded when a plan is generated. They add
**addressability**, never structure: they change no content, add no phase,
affect no gate. They let an agent extract one phase, one sub-phase or one atom
without loading the file, and they let the splitter package a plan
deterministically with traces already attached.

## 2. Syntax and attributes

`markers.syntax` is HTML-comment:

```
<!-- <KIND>:<ID>:START [attr=value …] -->
…block content…
<!-- <KIND>:<ID>:END -->
```

- `<KIND>` is one of `markers.kinds`; `<ID>` is a phase key, a SUB label, or an
  atom ID matching `factory.ids.pattern`.
- Attributes are allowed on START only and limited to `markers.attributes`.
  `traces=` carries a comma-separated list (no spaces) of upstream IDs; it is
  how packages leave the splitter already traced and how the `traces` contract
  clauses read a plan ([ARTIFACT-CONTRACTS.md](ARTIFACT-CONTRACTS.md)).
- Whitespace inside the comment is tolerated; the kind is case-sensitive.
- Several markers may share a line; the tokeniser orders them by column.

## 3. Kinds, levels, nesting

<!-- RENDER:markers -->
Schema version **2**, syntax `html-comment`, attributes `traces`.

| Kind | Level | Allowed parents | Identity | Scope |
|---|---|---|---|---|
| `PHASE` | 1 | top level | keys from profile | all |
| `SUB` | 2 | `PHASE` | phase-qualified label | all |
| `API` | 3 | `PHASE`, `SUB` | atom `API` | tracks: backend |
| `XM` | 3 | `PHASE`, `SUB` | atom `XM` | tracks: backend |
| `TC` | 3 | `PHASE`, `SUB` | atom `TC` | plans: test |
<!-- /RENDER:markers -->

Level 1 wraps every phase, always. Level 2 (`SUB`) is conditional — present
only when the phase's `split_threshold` is met. Level 3 atoms are innermost,
never contain other markers, and exist only in the tracks/plans their kind
declares (`kinds.<KIND>.tracks` / `.plans`). No other level exists; IDs of
atoms not listed as kinds are read inside their containing phase, not
addressed individually.

## 4. Phase keys per track and plan

Keys are canonical (`[A-Z0-9-]+`); display names may differ (`display`),
package folders may differ (`folder`). An unknown key is **refused**
(`markers.rules.unknown_phase`), never skipped (C3).

Backend, execution plan:
<!-- RENDER:phases:backend:exec -->
| Key | Display | Folder | Split when | SUB labels |
|---|---|---|---|---|
| `CORE` | CORE | `CORE` | never | — |
| `DATA-DOM` | DATA+DOM | `DATA-DOM` | — | `MASTER`, `TRANSACTIONAL`, `LOOKUP` |
| `SVC-API` | SVC+API | `SVC-API` | API >= 8 (CRUD / SEARCH / INT) | `CRUD`, `SEARCH`, `INT` |
| `DOC` | DOC | `DOC` | never | — |
| `INT-C` | INT-C | `INT-C` | XM >= 5 (per target module) | — |
| `INT-R` | INT-R | `INT-R` | XM >= 5 (per target module) | — |
| `SEC-BE` | SEC-BE | `SEC-BE` | never | — |
| `ALIGN-BE` | ALIGN-BE | `ALIGN-BE` | never | — |
<!-- /RENDER:phases:backend:exec -->

Backend, test plan:
<!-- RENDER:phases:backend:test -->
| Key | Display | Folder | Split when | SUB labels |
|---|---|---|---|---|
| `TEST-PLAN-BE` | TEST-PLAN-BE | `TEST-PLAN-BE` | TC > 12 (RULE-SCENARIOS / API-SCENARIOS) | `RULE-SCENARIOS`, `API-SCENARIOS` |
| `INT-XM` | INT-XM _(integration — populated for `--modules`/`--scope project`)_ | `INT-XM` | TC > 8 (per target module) | — |
<!-- /RENDER:phases:backend:test -->

Frontend, execution plan:
<!-- RENDER:phases:frontend:exec -->
| Key | Display | Folder | Split when | SUB labels |
|---|---|---|---|---|
| `F1` | F1 — Models & Types | `F1` | SCR >= 5 | — |
| `F2` | F2 — Data Hooks | `F2` | SCR >= 5 | — |
| `F3` | F3 — Forms & Validators | `F3` | SCR >= 5 | — |
| `F4` | F4 — Screens & Routes | `F4` | SCR >= 5 | — |
| `SEC-FE` | SEC-FE | `SEC-FE` | never | — |
| `ALIGN-FE` | ALIGN-FE | `ALIGN-FE` | never | — |
<!-- /RENDER:phases:frontend:exec -->

Frontend, test plan:
<!-- RENDER:phases:frontend:test -->
| Key | Display | Folder | Split when | SUB labels |
|---|---|---|---|---|
| `TEST-PLAN-FE` | TEST-PLAN-FE | `TEST-PLAN-FE` | TC > 8 (UI-FLOWS / INT-FLOW) | `UI-FLOWS`, `INT-FLOW` |
| `INT-UXD` | INT-UXD _(integration — populated for `--modules`/`--scope project`)_ | `INT-UXD` | TC > 8 (per source module) | — |
<!-- /RENDER:phases:frontend:test -->

## 5. Rules (from `markers.rules`, non-negotiable)

1. Every START has a matching END in the same artifact; mismatched, unmatched
   or unclosed markers are structural errors (CRITICAL).
2. Nesting follows `allowed_parents` exactly: an atom or SUB outside a PHASE
   is forbidden.
3. Every ID in a marker is exact and comes from the stage's registry artifact
   (`registry-agree` clauses); one atom ID = one block, never grouped, never
   repeated (uniqueness per kind+ID across the file).
4. Markers are content-neutral: removing them must leave the plan unchanged.
5. A phase with `never_split: true` carries the level-1 marker only.
6. `unknown_phase: refuse` — the parser stops on a key that is not in the
   plan's phase list.

## 6. SUB qualification and thresholds

- A SUB label is **phase-qualified**: `<PHASE-KEY>-<LABEL>` — except in plans
  listed in `rules.sub_unqualified_exempt_plans`, where labels are bare.
- `<LABEL>` comes from the phase's `sub_labels` when declared; for
  `sub_bearing` phases the label is the screen ID the block serves; otherwise
  the grouping named in `split_threshold.grouping`.
- A SUB is added only when `split_threshold` is met (`kind`, `count`, `op`).
  Below the threshold, atoms sit directly under the PHASE. The split is
  semantic (by grouping), never by line count.
- Under a phase that has SUBs, an atom outside every SUB is an orphan (MAJOR).
- Thresholds in `split_threshold` are counted from atoms of that `kind`; a
  phase whose threshold counts something not marker-countable is an engine
  self-check, not a parser rule.

## 7. Split unit and packages

`rules.split_unit`: the physical unit is the **SUB** when present, otherwise
the **PHASE** — never an atom. The splitter writes, per plan, the package named
in `factory.tracks.<track>.packages.<plan>` under `paths.module.packages_dir`,
one folder per phase (`phase.folder`), one file per split unit, a phase
preamble when a phase has SUBs, a file for content outside every phase, an
index per folder, and `paths.module.manifest_file` listing every unit with its
traces. Packages inherit `traces=` verbatim.

## 8. Autofix (`markers.autofix`, deterministic and bounded)

| Flag | Effect | Refuses when |
|---|---|---|
| `phase_key_normalise` | separators (`+`, `_`, space, `--`) normalised to `-` | the result maps to zero or more than one canonical key |
| `qualify_bare_sub` | a bare SUB label under a non-exempt plan gets its phase prefix | the qualified label collides with an existing one |

Autofix keeps a backup of the original file, re-parses after each fix, restores
the original if the re-parse fails, and is bounded in iterations. It never
touches content, only marker lines.

## 9. Schema version and compatibility

`markers.schema_version` is recorded in every split manifest and in the
delivery state (`factory.delivery.execution_state.schema`). A plan split under
an older schema stays splittable: the toolkit selects the grammar by the
recorded version; a plan with no recorded version is treated as the current
one and reported.

## 10. Verification

After a split, `rules.verify` (content hash) is computed for every atom in the
source and in the packages; any mismatch fails the split. The manifest carries
the hashes; `gov.py deliver` refuses a package whose manifest does not verify.
