#!/usr/bin/env python3
"""
gov.py — the Governance Factory orchestrator (blueprint v6 §8)
==============================================================
Enforcement, not prose: every stage runs through the same protocol
(state → brief/dispatch → write → analyze → commit → gate). Nothing here
spells a stage id, phase key, path, branch or model — all from factory.yaml
and the active profile (`config.CFG`).

  run-stage <id> -m MOD [-v N] [--complete] [--no-commit]
  run-pass <1|2> -m MOD [-v N | --new] [--complete] [--no-commit]
  run-standalone <id> -m MOD [-v N] [--complete]                       # e.g. api-verify
  run-standalone test-gen --module MOD | --modules A,B,... | --scope project [-v N] [--complete]
  gate <1|2> -m MOD [-v N] [--complete --result FILE.json]
  approve <gate-id> -m MOD [-v N] [--by NAME]
  analyze -m MOD [-v N] [--scope all|stage:ID|pass:N|gate:ID]
  state -m MOD [-v N]
  version -m MOD [--new] · tag -m MOD -v N · fetch-inputs -m MOD -v N
  status -m MOD · next -m MOD [-v N] [--run]                           # the single next protocol step, printed or executed
  publish [name] [--dry-run]                                           # factory publications → into the project repo
  structure/archive/split (toolkit) · render · lint [--profile ID]
  new-project DIR --id ID [--name NAME] [--profile PID]                # scaffold a project repo (project.yaml, profile, partitions)
  new-domain ID                                                        # add a second profile to the current project

The factory is a pure tool: every path it writes is in the PROJECT repo named by
$GOV_PROJECT_CHECKOUT (factory.yaml → project); this checkout carries no project.

Exit codes: 0 ok · 1 blocked (findings / missing) · 2 awaiting the operator (manual runner)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import hashlib
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CFG                     # noqa: E402
import analyze as an                        # noqa: E402
import dispatch as dp                       # noqa: E402
import idmodel                              # noqa: E402
import publications                          # noqa: E402
import render as rd                         # noqa: E402
import state as st                          # noqa: E402
import toolkit.splitter as tk_split           # noqa: E402
import toolkit.structure as tk_struct         # noqa: E402
# The FUNCTION, by its own path: `toolkit.archive` resolves to the re-exported
# function, not the submodule, so `tk_archive.archive(...)` would raise
# AttributeError (see the caution in toolkit/__init__.py).
from toolkit.archive import archive as tk_archive   # noqa: E402
from toolkit.common import blocks, counts_line, now_iso, read_json, rel, write_json   # noqa: E402

OK, BLOCKED, AWAITING = 0, 1, 2


# ── git ─────────────────────────────────────────────────────────────────────

def _git(*args: str, cwd: Path | None = None, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd or CFG.root), check=check, capture_output=capture, text=True)


def _owning_checkout(path: Path) -> Path:
    """The checkout that owns a path — the innermost declared root containing it.

    Content lives in the project repo (`paths.external`); a tool doc lives
    here; a consumer's checkout is a third root. The repo is derived from the
    declared checkouts rather than assumed to be this one — `git add` in the
    wrong root stages nothing or a pointer and commits cleanly — and innermost
    wins so a nested checkout beats the parent that contains it."""
    p = Path(path).resolve()
    roots = {CFG.root, CFG.project_checkout(), *(CFG.repo_checkout(r) for r in CFG.repos)}
    inside = [r for r in roots if p == r or r in p.parents]
    return max(inside, key=lambda r: len(r.parts)) if inside else CFG.root


def _detached(root: Path) -> bool:
    """Whether a checkout is on a commit rather than a branch.

    `git submodule update` leaves the submodule on a detached HEAD. A commit
    made there is referenced by nothing, and the next `submodule update` walks
    away from it — the commit survives only in the reflog, and the push that
    was supposed to publish it is a silent no-op because HEAD has moved. It
    happened during this repo's own migration and cost a commit (F-28)."""
    return _git("symbolic-ref", "-q", "HEAD", cwd=root, check=False).returncode != 0


def _commit_in(root: Path, rels: list[str], message: str) -> str | None:
    """Commit exactly `rels` in `root` — nothing else the index happens to hold.

    Every git call here is pathspec-limited. Without that, `git commit` takes
    the WHOLE index, so anything staged out of band rides along under this
    message: a probe of this function swept 36 pending deletions into a commit
    that claimed to add one file. A stage commit must contain the stage's own
    output and nothing it did not write."""
    if root != CFG.root and _detached(root):
        raise SystemExit(
            f"BLOCKED: {root.name} is on a detached HEAD, so a commit here would be\n"
            f"  referenced by nothing and lost at the next `git submodule update`.\n"
            f"  Fix: git -C {root} checkout <branch>   (then re-run)\n"
            f"  This is not a warning: the failure is silent, and the push that should\n"
            f"  publish the commit succeeds while publishing nothing.")
    _git("add", "-A", "--", *rels, cwd=root)
    if _git("diff", "--cached", "--quiet", "--", *rels, check=False, cwd=root).returncode == 0:
        return None
    _git("-c", "user.email=factory@local", "-c", "user.name=governance-factory",
         "commit", "-q", "-m", message, "--", *rels, cwd=root)
    return _git("rev-parse", "--short", "HEAD", cwd=root).stdout.strip()


def _commit(paths: list[Path], message: str, no_commit: bool = False) -> str | None:
    """Commit each path in the repository that owns it.

    When a write lands in a submodule, the parent's pointer is advanced in the
    same operation: a factory commit that produced artifacts should record the
    shared commit it produced them AT, which is the whole reason the pointer is
    pinned. Leaving it unbumped would also leave this repo permanently dirty,
    which hides the changes that matter."""
    if no_commit:
        return None
    groups: dict[Path, list[str]] = {}
    for p in paths:
        if not Path(p).exists():
            continue
        root = _owning_checkout(p)
        groups.setdefault(root, []).append(str(Path(p).resolve().relative_to(root)))
    shas: list[str] = []
    for root, rels in sorted(groups.items(), key=lambda kv: len(kv[0].parts), reverse=True):
        sha = _commit_in(root, rels, message)
        if not sha:
            continue
        shas.append(sha if root == CFG.root else f"{root.name}@{sha}")
        if root != CFG.root and CFG.root in root.parents:      # submodule of this repo
            ptr = _commit_in(CFG.root, [str(root.relative_to(CFG.root))], message)
            if ptr:
                shas.append(ptr)
    return " · ".join(shas) or None


def _head_sha(checkout: Path) -> str | None:
    """The commit a checkout stands at — None when it is not inside a git tree."""
    r = _git("rev-parse", "HEAD", cwd=checkout, check=False)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _execution_state(mod: str, version: int, **fields) -> dict:
    """The factory's OWN execution facts for a module version — what it fetched
    and at which commit, what the last gate measured — kept in `manifest.json →
    status`, the index this factory writes anyway.

    Not in the track's `execution-state.json`: that file sits in a partition a
    track writes (`repos.shared.partitions.<track>`), and one writer per path is
    the rule the shared repo exists to keep (GOVERNANCE-SHARED-DESIGN.md §3).
    A dict value is merged key by key under `status.<field>`; anything else
    replaces `status.<field>` whole."""
    data: dict | None = None
    for key, value in fields.items():
        if isinstance(value, dict):
            for sub, v in value.items():
                data = tk_struct.set_status(mod, version, key, v, sub=sub)
        else:
            data = tk_struct.set_status(mod, version, key, value)
    return data if data is not None else (tk_struct.load_manifest(mod, version) or {})


def _version(mod: str, v: int | None) -> int:
    return CFG.current_version(mod) if v is None else int(v)


def _say(*a: object) -> None:
    print(*a, flush=True)


# ── stage protocol ──────────────────────────────────────────────────────────

def _prepare(mod: str, version: int) -> None:
    tk_struct.ensure_structure(mod, version)
    st.build_state(mod, version)


def _check_inputs(stage, mod: str, version: int) -> list[str]:
    missing = []
    for inp in stage.inputs:
        name, optional = inp.rstrip("?"), inp.endswith("?")
        if optional:
            continue
        if name in CFG.inputs:
            spec = CFG.inputs[name]
            if not (CFG.inputs_dir(mod, version) / CFG.fmt(spec["file"], mod=mod)).exists():
                missing.append(name)
        elif name not in ("raw-idea",) and st.state_text(mod, version, name) is None:
            missing.append(name)
    return missing


def _gate_blocking(stage, mod: str, version: int) -> str | None:
    """A human-approval gate that blocks this stage and holds no record."""
    for g in CFG.gates:
        if g["type"] == "human-approval" and stage.id in g.get("blocks", []):
            if not an.approval_path(mod, version, g["id"]).exists():
                return g["id"]
    return None


def _stamp_verdict(stage, mod: str, version: int, rep) -> list[Path]:
    """Write each produced artifact's own verdict line FROM the analyze report.

    A verdict a model authors drifts from its evidence — the shipped plan said
    "0 findings" over six. A verdict the orchestrator writes from the report cannot,
    which removes the defect class instead of detecting it. `verdict-agrees` stays as
    the guard for anything a model still authors by hand.

    Everything about the line's shape is a profile fact (`profile.self_check`); a
    profile that declares no self-check is stamped nothing, silently and correctly.
    """
    spec = CFG.profile.self_check
    if not spec:
        return []
    changed = []
    for a in stage.produces:
        if a.dir:
            continue
        path = CFG.artifact_path(mod, stage.id, a.artifact, version)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        found = an._verdict_line(text, spec)
        if found is None:
            continue
        n, line = found
        head = line[:len(line) - len(line.lstrip())] + spec["verdict_label"]
        rest = line[len(head):]
        pad = rest[:len(rest) - len(rest.lstrip())] or " "
        count = sum(1 for f in rep.findings if f.artifact == a.artifact and f.check != "verdict-agrees")
        new_line = head + pad + an.render_verdict(spec, count)
        if new_line == line:
            continue
        lines = text.splitlines(keepends=True)
        lines[n - 1] = new_line + ("\n" if lines[n - 1].endswith("\n") else "")
        path.write_text("".join(lines), encoding="utf-8")
        changed.append(path)
        _say(f"  verdict stamped in {a.artifact}: {an.render_verdict(spec, count)}")
    return changed


def _coverage_line(rep) -> str:
    """The report's traceability ratios, for the operator's one line."""
    if not rep.metrics:
        return ""
    return " · coverage " + " ".join(f"{m['id']}={'—' if m['pct'] is None else str(m['pct']) + '%'}" for m in rep.metrics)


def _record_coverage(mod: str, version: int, rep) -> None:
    """The ratios the report just measured, into the module's execution state —
    the same numbers the gate record will quote."""
    if rep.metrics:
        _execution_state(mod, version, coverage={m["id"]: m["pct"] for m in rep.metrics})


def _complete_stage(stage, mod: str, version: int, no_commit: bool) -> int:
    """After the artifacts exist: outputs → question policy → analyze → commit."""
    missing = [a.artifact for a in stage.produces if not a.optional and not CFG.artifact_path(mod, stage.id, a.artifact, version).exists()]
    if missing:
        _say(f"BLOCKED: stage {stage.id} did not produce {missing}")
        return BLOCKED
    q = dp.refused_questions(stage, mod, version)
    if q:
        _say(f"BLOCKED: stage {stage.id} raised questions but questions are forbidden here: {q[:5]} — apply the ambiguity rule (ADR) and re-run")
        return BLOCKED
    st.build_state(mod, version)
    rep = an.run(mod, version, scope=f"stage:{stage.id}")
    if _stamp_verdict(stage, mod, version, rep):
        # the artifacts changed, so the report just written is about the version
        # before the stamp (F2's own rule) — rebuild the state and re-derive it
        st.build_state(mod, version)
        rep = an.run(mod, version, scope=f"stage:{stage.id}")
    c = rep.counts()
    _say(f"analyze stage:{stage.id} → {counts_line(c)}" + _coverage_line(rep))
    for f in rep.findings[:25]:
        _say("  ", f)
    _record_coverage(mod, version, rep)
    if not rep.clean:
        return BLOCKED
    blocked = dp.blocked_adrs(mod, version)
    if blocked:
        _say(f"STOP: breaking ambiguity — BLOCKED ADR(s): {[p.name for p in blocked]} (surface at the next human decision point)")
        return BLOCKED
    paths = [CFG.version_root(mod, version), CFG.decisions_dir(mod)]
    for a in stage.produces:
        if a.dir:
            paths.append(CFG.artifact_path(mod, stage.id, a.artifact))
    sha = _commit(paths, CFG.commit_msg("stage", stage=stage.id, mod=mod, version=version, summary=stage.title), no_commit)
    _say(f"OK: {stage.id} {'committed ' + sha if sha else 'done (nothing new to commit)'}")
    return OK


# ── regeneration ────────────────────────────────────────────────────────────
# Re-running a stage over its own leftovers is not a clean run: a plan half
# rewritten reads as a whole one, and the analyze report beside it still
# describes the version that is gone. Deleting by hand works and has already
# gone wrong — 621 files in one commit whose message named one module. So the
# set is DERIVED from what the stage declares it produces, never typed, and
# every path is checked to be inside the factory's own partition before it goes.


def _factory_owned(p: Path, mod: str, version: int) -> bool:
    """A path this factory may delete: inside a partition the factory writes —
    the DEEPEST partition containing the path decides, so a delivery partition
    nested in a track's partition is the factory's while the track's own
    execution state beside it is not — or, outside every partition, inside the
    module's version root.

    The partition half is the one that matters: `api-docs/` and a track's
    execution state belong to the tracks; a regeneration that swept them would
    destroy work no factory stage can reproduce."""
    p = p.resolve()
    part = CFG.partition_of(p, mod)
    if part is not None:
        return CFG.partition_writer(part) == CFG.FACTORY_WRITER
    root = CFG.version_root(mod, version).resolve()
    return root == p or root in p.parents


def _stage_outputs(stage: Stage, mod: str, version: int) -> list[Path]:
    """Everything one stage owns — its artifacts, its folder, its analyze report,
    its briefs. Read off `stage.produces` and `paths.module.*`, so a stage that
    gains an artifact is covered without anyone remembering to add it here."""
    out: list[Path] = []
    for a in stage.produces:
        out.append(CFG.artifact_path(mod, stage.id, a.artifact, version))
    out.append(CFG.stage_dir(mod, stage.id, version))
    sd = CFG.state_dir(mod, version)
    rep = CFG.fmt(CFG.paths["module"]["analyze_report"], stage=stage.id).split("/")[-1]
    out += [sd / rep, (sd / rep).with_suffix(".json")]
    out += sorted((sd / "briefs").glob(f"{stage.id}*"))
    return out


def _pass_outputs(pass_no: str, mod: str, version: int) -> list[Path]:
    """A pass owns its stages' outputs, plus the gate record it earned and the
    packages split from its track. NOT the approvals: a human approval is not
    this factory's to delete, and a regeneration that wiped one would erase the
    record of a decision nobody re-made."""
    out: list[Path] = []
    spec = CFG.passes[str(pass_no)]
    for sid in spec["stages"]:
        out += _stage_outputs(CFG.stage(sid), mod, version)
    sd = CFG.state_dir(mod, version)
    rec = CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": pass_no}).split("/")[-1]
    out += [sd / rec, (sd / rec).with_suffix(".json")]
    out += sorted((sd / "briefs").glob(f"pass-{pass_no}*"))
    grep = CFG.fmt(CFG.paths["module"]["analyze_report"], stage=f"pass-{pass_no}").split("/")[-1]
    out += [sd / grep, (sd / grep).with_suffix(".json")]
    track = spec.get("track")
    if track:
        for plan in CFG.profile.plans(track):
            out.append(CFG.packages_dir(mod, track, plan, version))
    return out


def _regenerate(paths: list[Path], mod: str, version: int, what: str) -> int:
    """Delete, after proving every path is the factory's to delete."""
    import shutil
    present = [p for p in dict.fromkeys(paths) if p.exists()]
    foreign = [p for p in present if not _factory_owned(p, mod, version)]
    if foreign:
        _say(f"BLOCKED: {len(foreign)} path(s) are not this factory's to delete:")
        for p in foreign:
            _say(f"  {rel(p)}")
        return BLOCKED
    if not present:
        _say(f"regenerate {what}: nothing on disk to clear")
        return OK
    files = sum(1 for p in present if p.is_file()) + sum(
        len([x for x in p.rglob('*') if x.is_file()]) for p in present if p.is_dir())
    _say(f"regenerate {what}: clearing {len(present)} path(s), {files} file(s)")
    for p in present:
        _say(f"  - {rel(p)}")
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    return OK


def run_stage(stage_id: str, mod: str, version: int | None, complete: bool, no_commit: bool,
              regenerate: bool = False) -> int:
    stage = CFG.stage(stage_id)
    version = _version(mod, version)
    if regenerate:
        if complete:
            _say("BLOCKED: --regenerate clears this stage's output; it cannot be combined with --complete")
            return BLOCKED
        rc = _regenerate(_stage_outputs(stage, mod, version), mod, version, f"stage {stage.id}")
        if rc != OK:
            return rc
    _prepare(mod, version)
    if complete:
        return _complete_stage(stage, mod, version, no_commit)
    gate = _gate_blocking(stage, mod, version)
    if gate:
        _say(f"BLOCKED: stage {stage.id} waits for human approval of gate `{gate}` → gov.py approve {gate} -m {mod} -v {version}")
        return BLOCKED
    missing = _check_inputs(stage, mod, version)
    if missing:
        _say(f"BLOCKED: inputs missing for {stage.id}: {missing}")
        return BLOCKED
    res = dp.dispatch(stage, mod, version)
    if res.awaiting:
        _say(f"AWAITING OPERATOR: brief written → {rel(res.brief)}")
        _say(f"  lane `{res.lane}` implementers {CFG.lane(res.lane).get('implementers')} — execute the brief (delegate), write the files it lists, then:")
        _say(f"  gov.py run-stage {stage.id} -m {mod} -v {version} --complete")
        return AWAITING
    _say(f"dispatched {stage.id}: {res.rounds} round(s), converged={res.converged}, wrote {len(res.written)} file(s)")
    return _complete_stage(stage, mod, version, no_commit)


# ── standalone: multi-module / project scope (`stage.scoped` stages only —
#    additive, gated on the config flag, never on a stage-id literal, C2) ────
# `--module MOD` (the single-module case) always resolves to run_stage() above,
# byte-identical to before this scope model existed. `--modules A,B,...` and
# `--scope project` are new, additive paths that reuse _prepare()/_complete_stage()
# per module rather than rewriting the single-module protocol.

def _all_modules_with_versions() -> list[str]:
    root = CFG.modules_root()
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir() and CFG.module_versions(p.name))


def run_scoped_modules(stage_id: str, mods: list[str], version: int | None, complete: bool, no_commit: bool) -> int:
    stage = CFG.stage(stage_id)
    versions = {m: _version(m, version) for m in mods}
    for m in mods:
        _prepare(m, versions[m])
    if complete:
        rc = OK
        for m in mods:
            r = _complete_stage(stage, m, versions[m], no_commit)
            rc = r if r != OK else rc
        return rc
    missing = {m: miss for m in mods if (miss := _check_inputs(stage, m, versions[m]))}
    if missing:
        _say(f"BLOCKED: inputs missing for {stage.id}: {missing}")
        return BLOCKED
    res = dp.dispatch_scoped(stage, mods, versions, "modules")
    if res.awaiting:
        _say(f"AWAITING OPERATOR: brief written → {rel(res.brief)}")
        _say(f"  lane `{stage.lane}` implementers {CFG.lane(stage.lane).get('implementers')} — execute the brief (delegate), write the files it lists, then:")
        _say(f"  gov.py run-standalone {stage.id} --modules {','.join(mods)} --complete")
        return AWAITING
    _say(f"dispatched {stage.id} (modules {', '.join(mods)}): wrote {len(res.written)} file(s)")
    rc = OK
    for m in mods:
        r = _complete_stage(stage, m, versions[m], no_commit)
        rc = r if r != OK else rc
    return rc


def _complete_test_gen_project(stage, mods: list[str], versions: dict[str, int], no_commit: bool) -> int:
    sti_path = CFG.artifact_path(mods[0], stage.id, "system-test-index", versions[mods[0]])
    if not sti_path.exists() or not sti_path.read_text(encoding="utf-8").strip():
        _say(f"BLOCKED: {stage.id} (project scope) did not produce {rel(sti_path)}")
        return BLOCKED
    qlines = idmodel.questions(sti_path.read_text(encoding="utf-8"))
    if qlines:
        _say(f"BLOCKED: {stage.id} raised questions but questions are forbidden here: {qlines[:5]} — apply the ambiguity rule (ADR) and re-run")
        return BLOCKED
    sha = _commit([sti_path], f"{stage.id}: [ALL] project — system test index ({CFG.profile_id})", no_commit)
    _say(f"OK: {stage.id} project {'committed ' + sha if sha else 'done (nothing new to commit)'}")
    return OK


def run_scoped_project(stage_id: str, version: int | None, complete: bool, no_commit: bool) -> int:
    stage = CFG.stage(stage_id)
    mods = _all_modules_with_versions()
    if not mods:
        _say("BLOCKED: --scope project needs at least one module with a committed version")
        return BLOCKED
    versions = {m: _version(m, version) for m in mods}
    for m in mods:
        _prepare(m, versions[m])
    if complete:
        return _complete_test_gen_project(stage, mods, versions, no_commit)
    res = dp.dispatch_scoped(stage, mods, versions, "project")
    sti_path = CFG.artifact_path(mods[0], stage.id, "system-test-index", versions[mods[0]])
    if res.awaiting:
        _say(f"AWAITING OPERATOR: brief written → {rel(res.brief)}")
        _say(f"  lane `{stage.lane}` implementers {CFG.lane(stage.lane).get('implementers')} — execute the brief, write {rel(sti_path)}, then:")
        _say(f"  gov.py run-standalone {stage.id} --scope project --complete")
        return AWAITING
    _say(f"dispatched {stage.id} (project, {len(mods)} module(s)): wrote {len(res.written)} file(s)")
    return _complete_test_gen_project(stage, mods, versions, no_commit)


def run_standalone(stage_id: str, module: str | None, modules_csv: str | None, scope: str,
                    version: int | None, complete: bool, no_commit: bool) -> int:
    stage = CFG.stage(stage_id)
    if not stage.standalone:
        raise SystemExit(f"'{stage_id}' is not a standalone stage")
    if scope == "project":
        if not stage.scoped:
            _say(f"BLOCKED: --scope project is not supported by `{stage_id}` (factory.yaml → standalone.{stage_id}.scoped)")
            return BLOCKED
        return run_scoped_project(stage_id, version, complete, no_commit)
    mods = [m.strip().upper() for m in modules_csv.split(",") if m.strip()] if modules_csv else ([module.upper()] if module else [])
    if not mods:
        _say(f"BLOCKED: run-standalone {stage_id} needs -m/--module, --modules, or --scope project")
        return BLOCKED
    if len(mods) == 1:
        return run_stage(stage_id, mods[0], version, complete, no_commit)   # byte-identical single-module path
    if not stage.scoped:
        _say(f"BLOCKED: --modules (more than one) is not supported by `{stage_id}` (factory.yaml → standalone.{stage_id}.scoped)")
        return BLOCKED
    return run_scoped_modules(stage_id, mods, version, complete, no_commit)


def run_pass(pass_no: str, mod: str, version: int | None, new: bool, complete: bool, no_commit: bool,
             redo: bool = False, regenerate: bool = False) -> int:
    p = CFG.passes[str(pass_no)]
    if new:
        version = cmd_version(mod, True, quiet=True)
    version = _version(mod, version)
    if regenerate:
        if complete:
            _say("BLOCKED: --regenerate clears this pass's output; it cannot be combined with --complete")
            return BLOCKED
        if new:
            _say("BLOCKED: --new already starts an empty version; --regenerate would clear it")
            return BLOCKED
        rc = _regenerate(_pass_outputs(pass_no, mod, version), mod, version, f"pass {pass_no}")
        if rc != OK:
            return rc
    for inp in p.get("required_inputs", []):
        spec = CFG.inputs[inp]
        if not (CFG.inputs_dir(mod, version) / CFG.fmt(spec["file"], mod=mod)).exists():
            _say(f"GATE CLOSED: pass {pass_no} needs `{inp}` → gov.py fetch-inputs -m {mod} -v {version}")
            return BLOCKED
    _prepare(mod, version)
    if not complete and p.get("session") == "bundled" and dp.runner_kind() == "manual":
        # one bundled brief for the whole pass; per-stage commits happen on --complete
        stages = [CFG.stage(s) for s in p["stages"]]
        gate = next((g for s in stages if (g := _gate_blocking(s, mod, version))), None)
        parts = [f"# PASS {pass_no} — module {mod.upper()} v{version} — bundled session ({len(stages)} stages, one commit per stage)", ""]
        for s in stages:
            parts.append(f"- `{s.id}` {s.title} — questions {s.questions}" + (f" — **blocked until human approval of `{gate}`**" if s.id == (CFG.gate(gate)['blocks'][0] if gate else None) else ""))
        for s in stages:
            b = dp.build_brief(s, mod, version)
            parts += ["", "=" * 78, b.read_text(encoding="utf-8")]
        bundle = CFG.state_dir(mod, version) / "briefs" / f"pass-{pass_no}.md"
        bundle.write_text("\n".join(parts) + "\n", encoding="utf-8")
        _say(f"AWAITING OPERATOR: bundled brief → {rel(bundle)}")
        _say(f"  execute stage by stage (stop at a human-approval gate), then: gov.py run-pass {pass_no} -m {mod} -v {version} --complete")
        return AWAITING
    for sid in p["stages"]:
        # A pass RESUMES. Every pass that contains a human-approval gate is
        # designed to stop inside itself — `gates.prd-approval` blocks a stage
        # in the middle of this list — so re-invoking run-pass after the
        # approval is the documented way forward, not an edge case. It used to
        # re-dispatch from the first stage: the two dialogue stages ran again,
        # and the artifact the human had just approved was rewritten underneath
        # the approval record that binds its sha. Observed on this run — P0's
        # three artifacts were modified by the resume.
        # `run-stage <id>` stays unconditional: that is how a stage is redone.
        if not complete and not redo and _stage_is_done(sid, mod, version):
            _say(f"skipped {sid}: already produced {_produced_names(sid)} (gov.py run-stage {sid} -m {mod} -v {version} to redo)")
            continue
        rc = run_stage(sid, mod, version, complete, no_commit)
        if rc != OK:
            return rc
    _say(f"pass {pass_no} stages complete → gov.py gate {pass_no} -m {mod} -v {version}")
    return OK


def _produced_names(stage_id: str) -> str:
    return ", ".join(a.artifact for a in CFG.stage(stage_id).produces if not a.optional)


def _stage_is_done(stage_id: str, mod: str, version: int) -> bool:
    """Every non-optional artifact the stage declares is on disk and non-empty."""
    stage = CFG.stage(stage_id)
    produced = [a for a in stage.produces if not a.optional]
    if not produced:
        return False                      # nothing to judge by — always run it
    for a in produced:
        p = CFG.artifact_path(mod, stage.id, a.artifact, version)
        if not p.exists() or not p.read_text(encoding="utf-8").strip():
            return False
    return True


# ── gates ───────────────────────────────────────────────────────────────────

def _gate_for_pass(pass_no: str) -> dict:
    last = CFG.passes[str(pass_no)]["stages"][-1]
    g = CFG.gate_after(last)
    if not g:
        raise SystemExit(f"no gate after the last stage of pass {pass_no}")
    return g


def gate(pass_no: str, mod: str, version: int | None, complete: bool, result: Path | None, no_commit: bool) -> int:
    version = _version(mod, version)
    g = _gate_for_pass(pass_no)
    _prepare(mod, version)
    rep, stale = an.verdict(mod, version, f"gate:{g['id']}")
    if stale:
        _say(f"stored verdict refused, re-analyzed: {stale}")
    c = rep.counts()
    vac = rep.vacuous()
    # the gate is the one place a human signs off on "clean", so what the run did
    # NOT examine belongs on the same line as what it did.
    _say(f"analyze gate:{g['id']} → {counts_line(c)}"
         + (f" · {len(vac)} clause(s) examined nothing ({', '.join(vac)})" if vac else ""))
    if g.get("requires_analyze") == "clean" and not rep.clean:
        for f in rep.findings[:25]:
            _say("  ", f)
        _say("GATE CLOSED: analyze is not clean")
        return BLOCKED
    if g.get("requires_feedback") == "answered":
        blockers, waiver = _feedback_blockers(mod, version, pass_no)
        if waiver:
            _say(f"feedback waiver: {len(waiver.get('waived', []))} item(s) by {waiver.get('by')} — {waiver.get('why')}")
        if blockers:
            for r in blockers[:25]:
                _say(f"  [{r['status']:12s}] {r['track']:8s} {r['label']:12s} {r['id'][:90]}")
            _say(f"GATE CLOSED: {len(blockers)} consumer item(s) the factory has not answered.")
            _say("  These are what the implementation found that the plan did not say. Either")
            _say("  answer them in the plan, or decide not to and say so:")
            _say(f"    gov.py waive-feedback -m {mod} -v {version} --pass {pass_no} --by NAME --why '...'")
            return BLOCKED
    if complete:
        if not result or not Path(result).exists():
            _say("BLOCKED: --complete needs --result FILE.json (the reviewer's structured output)")
            return BLOCKED
        data = json.loads(Path(result).read_text(encoding="utf-8"))
        return _gate_complete(g, pass_no, mod, version, data, rep, no_commit)[0]
    brief = _gate_brief(g, pass_no, mod, version, rep)
    if dp.runner_kind() == "manual" or not CFG.lane(g["lane"]).get("implementers"):
        _say(f"AWAITING REVIEW: gate brief → {rel(brief)} (lane `{g['lane']}`, read-only reviewers)")
        _say(f"  when the review JSON exists: gov.py gate {pass_no} -m {mod} -v {version} --complete --result <file.json>")
        return AWAITING
    # Automated: the review lane reads the brief (a dialogue — two reviewers
    # converge on one scorecard), the verdict is recorded exactly as --complete
    # would, and a REVISE is applied by the on_revise lane, re-analyzed and
    # re-gated at most review.revise_max times before it ESCALATES to the human.
    revise_max = int(CFG.review.get("revise_max", 0))
    attempts = 0
    while True:
        data = _dispatch_review(g, pass_no, mod, version, brief)
        if data is None:
            return BLOCKED
        rc, verdict = _gate_complete(g, pass_no, mod, version, data, rep, no_commit)
        if verdict != "REVISE":
            return rc
        if attempts >= revise_max:
            _say(f"ESCALATE: gate {g['id']} returned REVISE {attempts + 1} time(s) — the limit is "
                 f"{revise_max} (review.revise_max); a human decides now")
            _gate_complete(g, pass_no, mod, version, dict(data, verdict="ESCALATE"), rep, no_commit)
            return BLOCKED
        attempts += 1
        _say(f"REVISE {attempts}/{revise_max}: applying the findings through lane `{g['on_revise']}`")
        rc = _auto_revise(g, pass_no, mod, version, data, no_commit)
        if rc != OK:
            return rc
        _prepare(mod, version)
        rep = an.run(mod, version, scope=f"gate:{g['id']}")
        _say(f"analyze gate:{g['id']} after revise → {counts_line(rep.counts())}")
        if g.get("requires_analyze") == "clean" and not rep.clean:
            for f in rep.findings[:25]:
                _say("  ", f)
            _say("GATE CLOSED: analyze is not clean after the revise")
            return BLOCKED
        c = rep.counts()
        brief = _gate_brief(g, pass_no, mod, version, rep)


def _dispatch_review(g: dict, pass_no: str, mod: str, version: int, brief: Path) -> dict | None:
    """The review lane over the gate brief → the scorecard it returned, or None.
    The extracted JSON is kept beside the brief (`<brief>.result.json`) — the
    record of what the verdict was read from — and every decision the
    reviewers settled between them becomes an ADR."""
    stage = CFG.stage(g["after"])
    res = dp.run_lane(brief, g["lane"], dialogue=True)
    if not res.responses:
        _say(f"BLOCKED: lane `{g['lane']}` returned no response for gate {g['id']}")
        return None
    final = res.responses[-1].read_text(encoding="utf-8")
    data = dp.extract_json(final)
    if data is None:
        _say(f"BLOCKED: the reviewer's final response ({rel(res.responses[-1])}) carries no JSON block — no verdict to record")
        return None
    write_json(brief.with_name(brief.stem + ".result.json"), data)
    adrs = dp.persist_decisions(stage, mod, version, res, lane_id=g["lane"])
    _say(f"reviewed gate {g['id']}: {res.rounds} round(s), converged={res.converged}, "
         f"verdict {str(data.get('verdict', '')).upper() or '?'}" + (f", {len(adrs)} decision(s) → ADR" if adrs else ""))
    return data


def _gate_complete(g: dict, pass_no: str, mod: str, version: int, data: dict, rep, no_commit: bool) -> tuple[int, str]:
    """Record a reviewer's scorecard as the gate's verdict: the record, its JSON
    twin, the coverage the analyze report measured, one commit. Returns the
    exit code and the verdict it settled on (a low score downgrades APPROVE)."""
    c = rep.counts()
    record = CFG.version_root(mod, version) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": pass_no})
    verdict, scores = str(data.get("verdict", "")).upper(), data.get("scores", {}) or {}
    rv = CFG.review
    low = [k for k in rv["rubric"] if int(scores.get(k) or 0) < int(rv["pass_threshold"])]
    if verdict == "APPROVE" and low:
        verdict = "REVISE"
        _say(f"verdict downgraded to REVISE: attributes below threshold {low}")
    if verdict not in rv["verdicts"]:
        _say(f"BLOCKED: verdict must be one of {rv['verdicts']}")
        return BLOCKED, verdict
    lines = [CFG.data["lint"]["generated_marker"], f"# Gate record — {g['id']} — {mod.upper()} v{version}", "",
             f"Verdict: **{verdict}** · {now_iso()} · analyze {c}", "", "| Attribute | Score |", "|---|---|"]
    lines += [f"| {k} | {scores.get(k, '—')} |" for k in rv["rubric"]]
    if data.get("findings"):
        lines += ["", "| Severity | Artifact | Clause | Finding | Fix |", "|---|---|---|---|---|"]
        lines += [f"| {f.get('severity','')} | {f.get('artifact','')} | {f.get('clause','')} | {f.get('finding', f.get('message',''))} | {f.get('fix','')} |" for f in data["findings"]]
    if rep.metrics:
        # the ratios analyze measured for THIS gate's scope — the record quotes the
        # report, and the module's execution state quotes the record
        lines += ["", "| Coverage | Covered | Total | % |", "|---|---|---|---|"]
        lines += [f"| {m['id']} (`{m['from']}` → {', '.join('`' + t + '`' for t in m['to'])}) | {m['covered']} | {m['total']} | "
                  f"{'—' if m['pct'] is None else m['pct']} |" for m in rep.metrics]
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(record.with_suffix(".json"), {"gate": g["id"], "pass": pass_no, "verdict": verdict, "scores": scores,
                                              "findings": data.get("findings", []), "coverage": rep.metrics, "at": now_iso()})
    _record_coverage(mod, version, rep)
    _commit([CFG.version_root(mod, version), CFG.decisions_dir(mod)],
            CFG.commit_msg("gate", **{"pass": pass_no}, mod=mod, version=version, verdict=verdict), no_commit)
    _say(f"GATE {g['id']}: {verdict}")
    return (OK if verdict == "APPROVE" else BLOCKED), verdict


def _revise_brief(g: dict, pass_no: str, mod: str, version: int, data: dict) -> Path:
    """The brief the on_revise lane gets: every finding of the review with its
    fix, the files it may rewrite (this pass's artifacts, complete files, as
    `<<<FILE:>>>` blocks), the rules that still bind, and the current state."""
    stages = [CFG.stage(s) for s in CFG.passes[str(pass_no)]["stages"]]
    lane = CFG.lane(g["on_revise"])
    outputs = []
    for s in stages:
        for a in s.produces:
            if not a.dir:
                outputs.append(f"- `{rel(CFG.artifact_path(mod, s.id, a.artifact, version))}` ({s.id}{' · registry' if a.registry else ''})")
    parts = [
        f"# REVISE BRIEF — gate `{g['id']}` · module {mod.upper()} · v{version} · profile `{CFG.profile_id}`",
        "",
        f"Lane `{g['on_revise']}` · implementers {lane.get('implementers')} · effort {lane.get('effort')}",
        "",
        "## What to do",
        f"The reviewers returned **{str(data.get('verdict', '')).upper()}**. Apply EVERY finding below in the artifact it names,",
        "with the fix it states. Where a fix needs a choice, take the best-practice one and record it as an ADR",
        f"(`{CFG.paths['decisions']}/{mod.upper()}/{CFG.naming['adr_file']}`, next sequence, status ACCEPTED). Never re-number an id,",
        "never restart a sequence, never raise a `[QUESTION]` — this pass's stages forbid questions.",
        "Respond with one `<<<FILE: <path>>>> … <<<END FILE>>>` block per file you change — the COMPLETE file — and nothing else",
        "for files you do not change. The files you may write:",
        *outputs,
        "",
        "## Findings to apply",
        "```json",
        json.dumps({k: data.get(k) for k in ("verdict", "scores", "findings", "extra_checks", "analyze_confirmed") if k in data},
                   indent=2, ensure_ascii=False),
        "```",
        "", "---", "# ARTIFACTS UNDER REVISION (generated current state — write the source file listed above, not this copy)",
    ]
    for p in sorted(CFG.state_dir(mod, version).glob("current-*")):
        parts += [f"\n<<<ARTIFACT: {p.name}>>>", p.read_text(encoding="utf-8"), "<<<END ARTIFACT>>>"]
    out = CFG.state_dir(mod, version) / "briefs" / f"revise-pass-{pass_no}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return out


def _auto_revise(g: dict, pass_no: str, mod: str, version: int, data: dict, no_commit: bool) -> int:
    """Apply a REVISE through the gate's on_revise lane: dispatch the findings,
    ingest what it wrote, re-run every stage's completion (analyze → stamp →
    commit) so the pass is judged again on what is on disk now."""
    brief = _revise_brief(g, pass_no, mod, version, data)
    res = dp.run_lane(brief, g["on_revise"])
    if res.awaiting or not res.responses:
        _say(f"BLOCKED: lane `{g['on_revise']}` returned no response to the revise brief")
        return BLOCKED
    written = [p for resp in res.responses for p in dp.ingest(resp)]
    if not written:
        _say(f"BLOCKED: lane `{g['on_revise']}` changed no file — the findings were not applied")
        return BLOCKED
    _say(f"revise: lane `{g['on_revise']}` rewrote {len(written)} file(s)")
    for s in [CFG.stage(x) for x in CFG.passes[str(pass_no)]["stages"]]:
        rc = _complete_stage(s, mod, version, no_commit)
        if rc != OK:
            _say(f"BLOCKED: stage {s.id} does not complete after the revise")
            return rc
    return OK


# ── the next protocol step, from what exists ────────────────────────────────

def _pass_plan_of(pass_no: str) -> str | None:
    """The plan this pass's track artifact carries (`produces[*].plan`), for the
    split the pass ends with — read off the stages, never spelled."""
    p = CFG.passes[str(pass_no)]
    for sid in p["stages"]:
        for a in CFG.stage(sid).produces:
            if a.plan and a.track == p.get("track"):
                return a.plan
    return None


def next_step(mod: str, version: int | None = None) -> tuple[str, list[str] | None]:
    """What the protocol says comes next for this module version, and the gov.py
    arguments that do it — None when the version is complete.

    Derived from factory.yaml (the stage order, each pass's `then` list, the
    gates) and the filesystem (which artifacts, records, packages and tags
    exist), so it never disagrees with what the commands themselves check."""
    mod = mod.upper()
    v = _version(mod, version)
    mv = ["-m", mod, "-v", str(v)]
    for s in CFG.stages:
        if s.pass_ in ("pre", "bootstrap") and not _stage_is_done(s.id, mod, v):
            return f"run `{s.id}` ({s.title})", ["run-stage", s.id, *mv]
    for k in sorted(CFG.passes, key=int):
        p = CFG.passes[k]
        for inp in p.get("required_inputs", []):
            if not (CFG.inputs_dir(mod, v) / CFG.fmt(CFG.inputs[inp]["file"], mod=mod)).exists():
                return f"fetch `{inp}` — pass {k} cannot start without it", ["fetch-inputs", *mv]
        for sid in p["stages"]:
            if _stage_is_done(sid, mod, v):
                continue
            gate = _gate_blocking(CFG.stage(sid), mod, v)
            if gate:
                return f"human approval `{gate}` before `{sid}` can run", ["approve", gate, *mv]
            return f"run pass {k} — next stage `{sid}` ({CFG.stage(sid).title})", ["run-pass", k, *mv]
        for step in p.get("then", []):
            if step.startswith("gate:"):
                gid = step.split(":", 1)[1]
                rec = read_json(CFG.version_root(mod, v) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": k}).replace(".md", ".json")) or {}
                if rec.get("verdict") != "APPROVE":
                    last = f" (last verdict {rec['verdict']})" if rec.get("verdict") else ""
                    return f"gate {k} (`{gid}`){last}", ["gate", k, *mv]
            elif step == "split":
                track, plan = p.get("track"), _pass_plan_of(k)
                if track and plan:
                    man = tk_struct.load_manifest(mod, v) or {}
                    if not ((man.get("status") or {}).get("split") or {}).get(f"{track}/{plan}"):
                        return f"split track `{track}` (pass {k}) into packages", ["split", "--track", track, *mv]
            elif step == "tag":
                if not _project_tag(mod, v):
                    return f"tag `{CFG.tag_name(mod, v)}` — freeze v{v}", ["tag", *mv]
    return f"v{v} is complete — `gov.py version -m {mod} --new` starts a delta", None


def cmd_next(mod: str, version: int | None, run: bool) -> int:
    what, argv = next_step(mod, version)
    _say(f"next: {what}")
    if argv is None:
        return OK
    _say("  gov.py " + " ".join(argv))
    if not run:
        return OK
    return main(argv)


def _gate_brief(g: dict, pass_no: str, mod: str, version: int, rep: an.AnalyzeReport) -> Path:
    import jinja2
    tpl = CFG.dir("reviewers") / "pass-review.md"
    env = jinja2.Environment(undefined=jinja2.ChainableUndefined, keep_trailing_newline=True)
    stage = CFG.stage(g["after"])
    ctx = dict(profile=CFG.profile.data, factory=CFG.data, stage=stage.raw | {"pass": stage.pass_}, mod=mod.upper(), version=version,
               gate=g, contracts=an.select_contracts(f"gate:{g['id']}"),
               analyze_report=(CFG.version_root(mod, version) / CFG.fmt(CFG.paths["module"]["analyze_report"], stage=f"gate-{g['id']}")).read_text(encoding="utf-8"),
               artifacts=[rel(p) for p in sorted(CFG.state_dir(mod, version).glob("current-*"))],
               previous_version=version - 1 if version > 1 else None)
    text = env.from_string(tpl.read_text(encoding="utf-8")).render(**ctx)
    parts = [text, "", "---", "# ARTIFACTS UNDER REVIEW (generated current state)"]
    for p in sorted(CFG.state_dir(mod, version).glob("current-*")):
        parts += [f"\n<<<ARTIFACT: {p.name}>>>", p.read_text(encoding="utf-8"), "<<<END ARTIFACT>>>"]
    d = CFG.decisions_dir(mod)
    if d.exists():
        for p in sorted(d.glob("*.md")):
            parts += [f"\n<<<ADR: {p.name}>>>", p.read_text(encoding="utf-8"), "<<<END ADR>>>"]
    out = CFG.state_dir(mod, version) / "briefs" / f"gate-pass-{pass_no}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return out


def approve(gate_id: str, mod: str, version: int | None, by: str, no_commit: bool) -> int:
    version = _version(mod, version)
    g = CFG.gate(gate_id)
    if g["type"] != "human-approval":
        _say(f"BLOCKED: `{gate_id}` is a {g['type']} gate; use gov.py gate")
        return BLOCKED
    # What this gate approves is the ARTIFACT, not the fact that a stage ran
    # (CONSTITUTION.md §2: "the user approves the PRD file itself"). An approval
    # whose subject is not on disk approves nothing, and `artifact_sha` — the
    # field that exists to bind the two — would record `{}` and say so to
    # nobody. Refuse instead: a gate that cannot see its subject does not open.
    shas = _artifact_shas(mod, version, g["after"])
    absent = [a.artifact for a in CFG.stage(g["after"]).produces if a.artifact not in shas]
    if absent:
        _say(f"BLOCKED: `{gate_id}` has nothing to approve — {g['after']} declares "
             f"{', '.join(absent)} and no such file exists for {mod.upper()} v{version}:\n  "
             + "\n  ".join(rel(CFG.artifact_path(mod, g["after"], a, version))
                            for a in absent))
        return BLOCKED
    p = an.approval_path(mod, version, gate_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    write_json(p, {"gate": gate_id, "module": mod.upper(), "version": version, "by": by, "at": now_iso(),
                   "after": g["after"], "artifact_sha": shas})
    _commit([CFG.version_root(mod, version)], CFG.commit_msg("gate", **{"pass": g["after"]}, mod=mod, version=version, verdict="APPROVED"), no_commit)
    _say(f"approved `{gate_id}` for {mod.upper()} v{version} by {by}")
    return OK


def _artifact_shas(mod: str, version: int, stage_id: str) -> dict:
    import hashlib
    out = {}
    for a in CFG.stage(stage_id).produces:
        p = CFG.artifact_path(mod, stage_id, a.artifact, version)
        if p.exists():
            out[a.artifact] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


# ── versioning / repos ──────────────────────────────────────────────────────

def cmd_version(mod: str, new: bool, quiet: bool = False) -> int:
    if not new:
        vs = CFG.module_versions(mod)
        _say(f"{mod.upper()}: versions {vs or '(none)'} · current v{CFG.current_version(mod)} · next v{CFG.next_version(mod)}")
        return CFG.current_version(mod)
    v = CFG.next_version(mod)
    tk_struct.ensure_structure(mod, v)
    if v > 1:
        cm = CFG.version_root(mod, v) / CFG.paths["module"]["change_manifest"]
        if not cm.exists():
            cm.write_text(f"# CHANGE MANIFEST — (stamp the change-set id here)\nModule       : {mod.upper()}      Version: v{v}      Baseline: v{v-1}\n"
                          "Change type  : ADDITIVE\nSummary      : \n\n## Per artifact\n", encoding="utf-8")
    _commit([CFG.version_root(mod, v)], CFG.commit_msg("version", mod=mod, version=v))
    if not quiet:
        _say(f"created {rel(CFG.version_root(mod, v))} (v{v})")
    return v


def _project_tag(mod: str, version: int) -> str:
    """The tag, if it exists — in the PROJECT repo. `{mod}-vN` is project
    content; the tool repo never carries a project's tags."""
    return _git("tag", "-l", CFG.tag_name(mod, version), cwd=CFG.project_checkout()).stdout.strip()


def cmd_tag(mod: str, version: int) -> int:
    name = CFG.tag_name(mod, version)
    if _project_tag(mod, version):
        _say(f"tag {name} already exists in {CFG.project_checkout().name}")
        return OK
    _git("tag", "-a", name, "-m", f"{mod.upper()} v{version}", cwd=CFG.project_checkout())
    _say(f"tagged {name} in {CFG.project_checkout().name}")
    return OK


def _merge_published(src: Path, spec: dict, mod: str) -> str:
    """Fold a published FOLDER into the one file a stage reads.

    A publication is whatever its producer finds natural — the backend's api-docs
    are an index plus a file per endpoint group. A stage reads one artifact. The
    gap between those two shapes used to be closed by hand, which is why the
    consolidated file carried a "concatenated for pass-2 input" note and a
    hand-written annex nothing could reproduce.

    The fold is a DERIVATION: same source, same bytes. Order is the profile's
    declared lead file first, then every other file by relative path, so a diff
    of the result shows a real change and never a reshuffle. The header records
    what it was folded from, and a digest of it, so a stale copy is provable
    rather than merely suspected."""
    m = spec["merge"]
    lead = m.get("lead")
    files = sorted(src.glob(m.get("include") or "**/*.md"), key=lambda f: f.relative_to(src).as_posix())
    if lead and (src / lead) in files:
        files = [src / lead] + [f for f in files if f != src / lead]
    parts, digest = [], hashlib.sha256()
    for f in files:
        rel = f.relative_to(src).as_posix()
        body = f.read_text(encoding="utf-8")
        digest.update(rel.encode() + b"\0" + body.encode())
        parts.append(f"<!-- fetched-from: {rel} -->\n{body.rstrip()}\n")
    head = (f"<!-- GENERATED by `gov.py fetch-inputs` — do not edit.\n"
            f"     source : {src.as_posix()}\n"
            f"     files  : {len(files)}\n"
            f"     digest : {digest.hexdigest()}\n"
            f"     Edits belong in the source; anything this factory adds belongs in\n"
            f"     the companion file, which this command never touches. -->\n\n")
    return head + "\n".join(parts)


def cmd_fetch_inputs(mod: str, version: int, pull: bool) -> int:
    missing = []
    checkout = CFG.project_checkout()
    if pull and (checkout / ".git").exists():
        _git("pull", "--ff-only", cwd=checkout, check=False)
    for name, spec in CFG.inputs.items():
        # the producing track publishes into a project partition (inputs.<name>.partition);
        # WHO writes it is that partition's `writer`, WHERE is the project repo
        host = CFG.partition_writer(spec["partition"])
        src = CFG.partition_dir(spec["partition"], mod)
        if not src.exists():
            missing.append(f"{name} ← {src}")
            continue
        dst = CFG.inputs_dir(mod, version) / CFG.fmt(spec["file"], mod=mod)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            if not spec.get("merge"):
                missing.append(f"{name} ← {src} is a folder and `inputs.{name}.merge` declares no fold")
                continue
            text = _merge_published(src, spec, mod)
            if dst.exists() and dst.read_text(encoding="utf-8") == text:
                _say(f"unchanged {name} → {rel(dst)}")
            else:
                dst.write_text(text, encoding="utf-8")
                n = len(sorted(src.glob(spec["merge"].get("include") or "**/*.md")))
                _say(f"fetched {name} ({n} files folded) → {rel(dst)}")
        else:
            shutil.copy2(src, dst)
            _say(f"fetched {name} → {rel(dst)}")
        _record_input(name, mod, version, host, checkout, src, dst)
        companion = (spec.get("merge") or {}).get("keep_alongside")
        if companion:
            c = dst.parent / CFG.fmt(companion, mod=mod)
            if c.exists():
                _say(f"  kept {c.name} (written here, never fetched)")
    if missing:
        _say("GATE CLOSED — missing inputs:\n  " + "\n  ".join(missing))
        return BLOCKED
    return OK


def _record_input(name: str, mod: str, version: int, host: str, checkout: Path, src: Path, dst: Path) -> dict:
    """WHICH published surface a fetched input is — the shared-repo commit it was
    read at, and a digest of what landed — written beside the input
    (`paths.module.input_meta`) and into the module's execution state.

    The merged file's header already says what it was folded from; nothing said
    at which commit. A pass-2 plan built against api-docs that the backend then
    republished was indistinguishable from one built against the current ones,
    and the pin every consumer keeps is only worth something if the factory can
    say which pin it read."""
    meta = {"input": name, "repo": host, "commit": _head_sha(checkout),
            "source": src.as_posix(), "file": dst.name,
            "digest": hashlib.sha256(dst.read_bytes()).hexdigest(), "fetched_at": now_iso()}
    write_json(dst.with_name(CFG.fmt(CFG.paths["module"]["input_meta"], file=dst.name)), meta)
    _execution_state(mod, version, inputs={name: {k: meta[k] for k in ("repo", "commit", "digest", "fetched_at")}})
    _say(f"  recorded {name} @ {host}" + (f" {meta['commit'][:12]}" if meta["commit"] else " (not a git checkout)"))
    return meta


def _partitions() -> dict[str, str]:
    return CFG.partitions()


def _per_module(part: str) -> bool:
    return CFG.partition_is_per_module(part)


def _shared_dir(part: str, mod: str | None = None) -> Path:
    return CFG.partition_dir(part, mod)


def _sparse_patterns(track: str) -> list[str]:
    """What one track may SEE of the shared repo.

    `CODEOWNERS` decides who may write; git decides who may read, and a
    submodule hands every consumer the whole repository. Sparse-checkout is the
    only lever that narrows the read, and this derives its patterns rather than
    listing them — from the same declarations everything else here reads:

      * a stage folder belongs to a track when the stage names that track, and
        to everyone when it names none (P0…P2 are shared analysis)
      * a package folder is `tracks.<t>.packages`
      * a partition is visible to its own `writer`, and api-docs to both,
        because the frontend builds against what the backend published

    Hiding is not isolation. The bytes are still in `.git`, and a consumer can
    widen its own checkout. What it buys is that the wrong tree is not in front
    of someone by accident — which is how a frontend session came to delete six
    modules' backend governance."""
    mods = f"{CFG.paths['modules']}/*"
    pats = [f"{CFG.partitions()[p]}/**" for p in CFG.partitions()
            if not CFG.partition_is_per_module(p) and CFG.partition_is_readable_by(p, track)]
    pats += [CFG.project["file"], f"{CFG.paths['domain']}/**", f"{CFG.paths['platform']}/**", f"{CFG.paths['decisions']}/**"]
    m = CFG.paths["module"]
    pats += [f"{mods}/{m['manifest_file']}", f"{mods}/{m['state_dir']}/**", f"{mods}/{m['inputs_dir']}/**"]
    for s in CFG.all_stages():
        if s.track in (None, track):
            pats.append(f"{mods}/{s.folder}/**")
    for part in CFG.partitions():
        if CFG.partition_is_per_module(part) and CFG.partition_is_readable_by(part, track):
            pats.append(CFG.fmt(CFG.partitions()[part], mod="*") + "/**")
    return sorted(dict.fromkeys(CFG.fmt(x) for x in pats))


def cmd_sparse(track: str, apply_to: str | None = None) -> int:
    """Print (or apply) the sparse-checkout patterns for one track."""
    if track not in CFG.tracks:
        _say(f"BLOCKED: `{track}` is not a track ({', '.join(CFG.tracks)})")
        return BLOCKED
    pats = _sparse_patterns(track)
    if not apply_to:
        for x in pats:
            _say(x)
        return OK
    root = Path(apply_to)
    if not (root / ".git").exists():
        _say(f"BLOCKED: not a checkout: {root}")
        return BLOCKED
    _git("sparse-checkout", "set", "--no-cone", *pats, cwd=root)
    _say(f"{track}: {len(pats)} pattern(s) applied to {root}")
    return OK


def cmd_sync(push: bool = False, dry_run: bool = False) -> int:
    """Report — and optionally close — the distance between this factory and the
    shared repo every consumer pins.

    Without this command the design it serves is a regression, not an advance.
    Each sync would otherwise be three commits and three submodule-pointer bumps
    done by hand; measured against the real rate (~3 syncs a week) that is more
    ceremony than the manual copying it replaces. The whole case for a shared
    repository rests on one command hiding that.

    It never rewrites what it does not own: the partitions are single-writer by
    design and this reports each one's state rather than reconciling them.
    """
    shared = CFG.project_checkout()
    if not (shared / ".git").exists():
        _say(f"BLOCKED: project checkout not found at {shared}\n"
             f"  clone it, or set {CFG.project['checkout_env']}")
        return BLOCKED

    # Which submodule is the project one is decided by its URL (project.yaml →
    # project.url), not by a folder name: each consumer mounts it at a path of
    # its own choosing, and matching on a name would silently match nothing.
    url = str((CFG.project_data.get("project") or {}).get("url") or "").strip()
    stale = []
    for name in CFG.repos:
        try:
            co = CFG.repo_checkout(name)
        except Exception:
            continue
        mods = co / ".gitmodules"
        if not (co.is_dir() and mods.exists()):
            continue
        if url and url.removesuffix(".git") not in mods.read_text(encoding="utf-8").replace(".git", ""):
            stale.append((name, "mounts the shared repo nowhere",
                          ".gitmodules does not name it"))
            continue
        for line in _git("submodule", "status", cwd=co, check=False).stdout.splitlines():
            if line.startswith(("-", "+")):
                # The leading character is git's own diagnosis and the only thing
                # that carries it: '-' is a submodule never initialised, '+' one
                # sitting on a commit other than the pinned one. Deriving this at
                # the print site made every non-git row read as '+'.
                kind = "not initialised" if line.startswith("-") else "differs from its pinned commit"
                stale.append((name, kind, line.strip()))

    _git("fetch", "--quiet", "origin", cwd=shared, check=False)
    head = _git("rev-parse", "--short", "HEAD", cwd=shared).stdout.strip()
    upstream = _git("rev-parse", "--short", "@{u}", cwd=shared, check=False).stdout.strip()
    behind = ahead = "0"
    if upstream:
        counts = _git("rev-list", "--left-right", "--count", "@{u}...HEAD", cwd=shared, check=False).stdout.split()
        if len(counts) == 2:
            behind, ahead = counts
    dirty = [l for l in _git("status", "--porcelain", cwd=shared).stdout.splitlines() if l.strip()]

    _say(f"project {shared.name} @ {head}" + (f" · upstream {upstream} (behind {behind}, ahead {ahead})" if upstream else " · no upstream"))
    known = CFG.modules()
    for part in _partitions():
        if not _per_module(part):
            _say(f"  {part:<9} {'present' if _shared_dir(part).exists() else 'ABSENT'}")
            continue
        present = [m for m in known if _shared_dir(part, m).exists()]
        missing = [m for m in known if m not in present]
        line = f"  {part:<9} {len(present)}/{len(known)}"
        if present:
            line += f"  {', '.join(present)}"
        if missing:
            line += f"   · no {part}: {', '.join(missing)}"
        _say(line)
    if dirty:
        _say(f"  uncommitted in the project: {len(dirty)} path(s)")
        for l in dirty[:8]:
            _say(f"    {l}")

    for name, kind, line in stale:
        _say(f"  {name}: submodule {kind} — {line}")

    if not push:
        if behind != "0":
            _say("BEHIND — a consumer pinning this commit is building on stale inputs; "
                 "`git -C %s pull --ff-only` before fetch-inputs" % shared)
        return OK

    if dry_run or not dirty:
        _say("dry-run" if dry_run else "nothing to push — the project checkout is clean")
        return OK
    _git("add", "-A", cwd=shared)
    _git("commit", "-m", "sync from factory", cwd=shared)
    _git("push", cwd=shared)
    _say(f"pushed {shared.name} @ {_git('rev-parse', '--short', 'HEAD', cwd=shared).stdout.strip()}")
    _say("now bump the submodule pointer in each consumer that should move")
    return OK


def _feedback_status(raw: str) -> tuple[str, str]:
    """Normalise a consumer's free-text resolution to a declared bucket.

    Only the FIRST word is read, stripped of punctuation and case: the field is
    prose written by an implementer, and it was already being written eleven
    ways ("RESOLVED", "RESOLVED.", "Resolved", "Implemented", "OPEN,"). A word
    in none of the declared lists comes back UNRECOGNISED rather than guessed
    into a bucket — a gap silently filed as closed is worse than one filed
    nowhere."""
    spec = CFG.feedback["status"]
    word = re.split(r"[\s,.;:]+", (raw or "").strip(), maxsplit=1)[0].upper()
    if not word:
        return "UNRECOGNISED", "(no resolution recorded)"
    for bucket in ("open", "closed", "human"):
        if word in [w.upper() for w in spec[bucket]]:
            return bucket.upper(), word
    return "UNRECOGNISED", word


def _feedback_rows(mod: str | None = None) -> list[dict]:
    """Every item every consumer has recorded for the factory, across tracks."""
    from toolkit.common import read_json
    spec = CFG.feedback
    rows: list[dict] = []
    for track in CFG.tracks:
        part = CFG.track_partition(track)
        if part not in _partitions():
            continue
        for m in ([mod.upper()] if mod else CFG.modules()):
            state = _shared_dir(part, m) / spec["file"]
            if not state.exists():
                continue
            data = read_json(state, {}) or {}
            for channel, cspec in spec["channels"].items():
                for item in data.get(channel) or []:
                    if not isinstance(item, dict):
                        continue
                    bucket, word = _feedback_status(item.get(spec["status"]["field"], ""))
                    rows.append({
                        "module": m, "track": track, "channel": channel,
                        "label": cspec["label"],
                        "id": str(item.get(cspec["key"]) or item.get("id") or "?"),
                        "type": item.get("type") or "",
                        "phase": item.get("phase") or "",
                        "detail": (item.get("detail") or "").replace("\n", " "),
                        "status": bucket, "word": word,
                    })
    return rows


UNANSWERED = ("OPEN", "HUMAN", "UNRECOGNISED")


def _feedback_key(row: dict) -> str:
    """A stable name for one recorded item, so a waiver can be pinned to it.

    A waiver that says only "feedback waived" covers whatever appears next, which
    is the opposite of a decision. This is the same shape `approve` uses when it
    binds an approval to `artifact_sha`: name the subject, or approve nothing."""
    return f"{row['track']}|{row['channel']}|{row['id']}"


def _waiver_path(mod: str, version: int, pass_no: str) -> Path:
    return an.approval_path(mod, version, f"feedback-pass-{pass_no}")


def cmd_waive_feedback(mod: str, version: int | None, pass_no: str, by: str, why: str) -> int:
    """Record a human decision to open a gate over consumer feedback it owes.

    Pinned to the exact items present now: a gap recorded afterwards is not
    covered, and the gate closes again. That is the point — a standing waiver
    is an off switch, and an off switch is what people reach for when a gate
    cannot be answered."""
    from toolkit.common import write_json
    version = _version(mod, version)
    rows = [r for r in _feedback_rows(mod) if r["status"] in UNANSWERED]
    if not rows:
        _say(f"nothing to waive for {mod.upper()} — no unanswered consumer feedback")
        return OK
    p = _waiver_path(mod, version, pass_no)
    p.parent.mkdir(parents=True, exist_ok=True)
    write_json(p, {"module": mod.upper(), "version": version, "pass": pass_no,
                   "by": by, "at": now_iso(), "why": why,
                   "waived": sorted({_feedback_key(r): r["status"] for r in rows}.items())})
    _say(f"waived {len(rows)} item(s) for {mod.upper()} v{version} gate pass-{pass_no}, by {by}")
    for r in rows:
        _say(f"  [{r['status']}] {r['label']} {r['id'][:90]}")
    _say(f"  reason: {why}")
    _say("A gap recorded after this is NOT covered — the gate closes again.")
    return OK


def _feedback_blockers(mod: str, version: int, pass_no: str) -> tuple[list[dict], dict]:
    """Unanswered consumer items this gate would open over, and the waiver (if any)."""
    from toolkit.common import read_json
    rows = [r for r in _feedback_rows(mod) if r["status"] in UNANSWERED]
    waiver = read_json(_waiver_path(mod, version, pass_no), {}) or {}
    covered = {k for k, _ in waiver.get("waived", [])}
    return [r for r in rows if _feedback_key(r) not in covered], waiver


def cmd_feedback(mod: str | None = None, verbose: bool = False) -> int:
    """What the consumers have discovered that the plan could not know.

    The factory writes the plan; the implementer finds out, while building it,
    what the plan got wrong or left out. Without this the discovery stays in the
    consumer's file and reaches nobody — which is how a requirement was added to
    SEC inside a delivered copy and never came back (F-23), and how the frontend
    ran into features with no endpoints far too late.

    Read-only, always: these paths belong to the tracks."""
    rows = _feedback_rows(mod)
    if not rows:
        scope = f" for {mod.upper()}" if mod else ""
        _say(f"no consumer feedback{scope} — nothing recorded, "
             f"or the shared checkout is behind (`gov.py sync`)")
        return OK

    order = {"OPEN": 0, "HUMAN": 1, "UNRECOGNISED": 2, "CLOSED": 3}
    by_mod: dict[str, list[dict]] = {}
    for r in sorted(rows, key=lambda r: (order.get(r["status"], 9), r["module"], r["phase"])):
        by_mod.setdefault(r["module"], []).append(r)

    owed = 0
    for m, items in by_mod.items():
        counts = {b: sum(1 for i in items if i["status"] == b) for b in order}
        _say(f"{m} — " + " · ".join(f"{n} {b.lower()}" for b, n in counts.items() if n))
        for i in items:
            if i["status"] == "CLOSED" and not verbose:
                continue
            owed += i["status"] in ("OPEN", "HUMAN", "UNRECOGNISED")
            head = f"  [{i['status']:12s}] {i['track']:8s} {i['label']:12s} {i['phase']:12s} {i['id']}"
            _say(head if len(head) < 150 else head[:147] + "...")
            if i["status"] == "UNRECOGNISED":
                _say(f"                 resolution `{i['word']}` is not a declared status "
                     f"(feedback.status) — the factory cannot tell whether this is still owed")
            if verbose and i["detail"]:
                _say(f"                 {i['detail'][:200]}")

    _say("")
    _say(f"{owed} item(s) the factory has not answered. "
         f"An OPEN gap is a plan the implementation disagrees with; "
         f"answer it in the plan, or record why not in an ADR.")
    return OK


def cmd_publish(name: str | None = None, dry_run: bool = False) -> int:
    """Write every factory publication INTO the project repo, where it declares
    a home (`project.receives`).

    Every consumer mounts the project repo and reads the one copy there — no
    file above a repo root, no reach into a sibling's tree, no copy to keep in
    step. The factory is the single writer; what it does not own in the file
    (`preserve`, `additive`) is carried over from the copy on disk.
    """
    names = [name] if name else list(CFG.publications)
    rc = OK
    if not CFG.project_checkout().exists():
        _say(f"BLOCKED: project checkout not found at {CFG.project_checkout()} (set ${CFG.project['checkout_env']})")
        return BLOCKED
    for pub in names:
        path = CFG.project_receives(pub)
        if path is None:
            _say(f"{pub}: the project declares no home for it under `project.receives` — nothing to publish")
            continue
        payload = publications.payload(pub, [read_json(path, {}) or {}])
        body = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        before = path.read_text(encoding="utf-8") if path.exists() else None
        if before == body:
            _say(f"{pub}: unchanged")
            continue
        if dry_run:
            _say(f"{pub}: WOULD WRITE {path} ({'new' if before is None else 'changed'})")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        _say(f"{pub}: wrote {path} ({'new' if before is None else 'updated'})")
    return rc


def cmd_verify_split(track: str, mod: str, version: int, plan: str | None) -> int:
    """Re-run the split verification, independently of a split.

    The digest comparison between a plan's blocks and their split copies already
    existed — it just ran ONCE, at split time. Every hand edit after that drifted
    silently, and did: the packages the implementer reads stopped being the plan
    the gate approved, and nothing said so. This runs the same comparison, on
    demand, over whatever is on disk now. No new mechanism, no new check."""
    plans = [plan] if plan else [pl for pl in CFG.tracks[track]["packages"] if pl in CFG.profile.plans(track)]
    if not plans:
        _say(f"BLOCKED: track {track} declares no plan that the active profile also declares.")
        return BLOCKED
    rc, checked_any = OK, False
    for pl in plans:
        v = tk_split.verify(mod, track, pl, version)
        if v.get("missing") == ["source plan or package container not found"]:
            _say(f"verify-split {track}/{pl}: skipped — no plan or no package container yet")
            if plan:
                rc = BLOCKED
            continue
        checked_any = True
        for m in v.get("missing", []):
            _say("  MISSING   ", m)
        for m in v.get("mismatched", []):
            # the whole point: the package copy no longer digests to the plan block
            _say("  DRIFTED   ", m, "— the package no longer matches the plan it was split from")
        _say(f"verify-split {track}/{pl} v{v['version']}: {v['checked']} block(s) checked, "
             f"{len(v.get('missing', []))} missing, {len(v.get('mismatched', []))} drifted — "
             f"{'OK' if v.get('ok') else 'BLOCKED'}")
        if not v.get("ok"):
            rc = BLOCKED
    if not checked_any and not plan:
        _say(f"BLOCKED: nothing verified for [{mod.upper()}] — no split output exists to compare against.")
        rc = BLOCKED
    return rc


def cmd_analyze_all(scope: str) -> int:
    """Re-analyze every module at its current version.

    The backlog a rules change creates is otherwise invisible and unbounded: the
    checks got stricter, no module was re-analyzed, and every stored PASS stayed a
    PASS. The module list comes from the filesystem (the version authority), so a
    sweep never reads a list somebody has to remember to extend."""
    mods = CFG.modules()
    if not mods:
        _say("no modules to analyze")
        return OK
    rc = OK
    for m in mods:
        v = CFG.current_version(m)
        stale = an.stale_reason(m, v, scope)
        rep = an.run(m, v, scope=scope)
        c = rep.counts()
        _say(f"{m} v{v} {scope} → {counts_line(c)} · {'CLEAN' if rep.clean else 'BLOCKED'}"
             f"{'   (previous verdict was stale: ' + stale + ')' if stale else ''}")
        for f in rep.findings:
            _say("  ", f)
        if not rep.clean:
            rc = BLOCKED
    return rc


def cmd_status(mod: str) -> int:
    vs = CFG.module_versions(mod)
    _say(f"{mod.upper()} · profile {CFG.profile_id} · versions {vs or '(none)'}")
    for v in vs:
        root = CFG.version_root(mod, v)
        tag = "tagged" if _project_tag(mod, v) else "untagged"
        have = [s.id for s in CFG.stages if all(CFG.artifact_path(mod, s.id, a.artifact, v).exists() for a in s.produces if not a.optional and not a.dir) and any(not a.dir for a in s.produces)]
        inputs = [n for n, spec in CFG.inputs.items() if (CFG.inputs_dir(mod, v) / CFG.fmt(spec["file"], mod=mod)).exists()]
        gates = [p.stem for p in (CFG.state_dir(mod, v) / "approvals").glob("*.json")] if (CFG.state_dir(mod, v) / "approvals").exists() else []
        stale = an.stale_reason(mod, v, "all")
        pattern = CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": "*"}).replace(".md", ".json")
        gates += [p.stem for p in root.glob(pattern)]
        _say(f"  v{v}: stages {have} · inputs {inputs} · gates {gates} · {tag} · state {'fresh' if st.is_fresh(mod, v) else 'stale'}"
             f" · verdict {'current' if stale is None else 'STALE — ' + stale}")
    return OK


# ── project scaffolding ──────────────────────────────────────────────────────
# A project is a repo of its own: `project.yaml` (its facts — user-edited), its
# profile(s), and the empty partitions the factory will fill. `new-project` lays
# one down in a target directory and initialises git there; `new-domain` adds a
# second profile to the current project. Neither touches factory.yaml: the tool
# carries no project fact, so nothing in it has to be reset between projects.


def _yaml_scalar(value: str) -> str:
    return value if re.fullmatch(r"[A-Za-z0-9_-]+", value) else json.dumps(value)


def _sanitize_mod(pid: str) -> str:
    m = re.sub(r"[^A-Za-z0-9]", "", pid).upper()
    if not m or not m[0].isalpha():
        m = "M" + m
    return m


def _scaffold_profile(pid: str, profiles: Path) -> Path:
    """`<profiles>/<pid>.yaml` from `profiles/_schema.yaml` — every value a TODO."""
    dst = profiles / f"{pid}.yaml"
    if dst.exists():
        raise FileExistsError(f"profile exists: {dst}")
    schema = CFG.profile_schema()

    def skel(node, indent=0):
        out = []
        for k, v in node.items():
            if k.startswith("$") or k == "schema_version":
                continue
            name, opt = k.rstrip("?"), k.endswith("?")
            pad = "  " * indent
            if isinstance(v, dict):
                out.append(f"{pad}{'# ' if opt else ''}{name}:")
                out += skel(v, indent + 1) if not opt else [("  " * (indent + 1)) + "# " + l.strip() for l in skel(v, indent + 1)]
            else:
                spec = str(v)
                placeholder = "[]" if spec.startswith("list[") else "{}" if spec.startswith("map[") else "false" if spec == "bool" else "0" if spec == "int" else "TODO"
                out.append(f"{pad}{'# ' if opt else ''}{name}: {placeholder if not opt else ''}   # TODO {v}")
        return out

    text = [f"# profile scaffold generated by gov.py new-project — fill every TODO, then gov.py lint --profile {pid}",
            f"schema_version: {schema.get('schema_version', CFG.data['schema_version'])}", *skel(schema)]
    text = [l.replace("id: TODO", f"id: {pid}") for l in text]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(text) + "\n", encoding="utf-8")
    return dst


def _project_yaml_text(pid: str, name: str, profile: str) -> str:
    """The project's own facts, with every consumer repo the tracks name."""
    p = CFG.project
    lines = [
        f"# {p['file']} — this project's facts. Edited by people; the factory READS it and never writes it.",
        "project:",
        f"  id: {_yaml_scalar(pid)}",
        f"  name: {_yaml_scalar(name)}",
        '  url: ""                          # this repo\'s own url — every consumer mounts it as a submodule and pins a commit',
        f"profile: {_yaml_scalar(profile)}                     # {CFG.paths['profiles']}/<profile>.yaml in this repo ($GOV_PROFILE overrides)",
        "repos:                             # the consumer repos, resolved relative to this checkout unless the env var is set",
    ]
    for track in CFG.tracks:
        repo = CFG.track_repo(track)
        env = CFG.fmt(p["consumer_env"], REPO=repo.upper())
        default = CFG.fmt(p["consumer_default"], repo=repo)
        lines.append(f'  {repo}: {{url: "", checkout_env: {env}, checkout_default: {json.dumps(default)}}}')
    return "\n".join(lines) + "\n"


def _project_gitignore_text() -> str:
    m = CFG.paths["module"]
    stem = CFG.fmt(CFG.naming["current_state_file"], artifact="")
    return "\n".join([
        "# macOS Finder metadata — never content", ".DS_Store", "",
        f"# Derived caches: `gov.py state` rewrites these from the vN/ sources on every run.",
        f"# Everything else under {m['state_dir']}/ IS tracked (approvals, gate and analyze records, briefs).",
        f"**/{m['state_dir']}/{stem}*.md", f"**/{m['state_dir']}/traceability.md", f"**/{m['state_dir']}/state.json", "",
        "# Implementer receipts — per-run, not governance", f"**/{CFG.paths['modules'].split('/')[-1]}/*/**/receipts/", "",
    ])


def _project_codeowners_text() -> str:
    """The one-writer table (project.partitions) in the form GitHub enforces —
    most specific wins, exactly as `CFG.partition_of` reads it."""
    lines = ["# One writer per path — derived from factory.yaml → project.partitions by gov.py new-project.",
             "# Most specific wins. Replace the placeholders with the maintainers of each writer.", "",
             "*                                   @factory-maintainers"]
    for part, spec in sorted(CFG.project["partitions"].items(), key=lambda kv: len(kv[1]["path"])):
        if spec["writer"] == CFG.FACTORY_WRITER and "{MOD}" not in spec["path"]:
            continue
        path = "/" + spec["path"].replace("{MOD}", "*") + "/"
        lines.append(f"{path:<36}@{spec['writer']}-maintainers")
    return "\n".join(lines) + "\n"


def cmd_new_project(target: Path, pid: str, name: str | None, profile: str | None, yes: bool = False) -> int:
    """Scaffold a project repo in `target`: project.yaml, profiles/<profile>.yaml
    from the schema, the empty partitions, .gitignore, CODEOWNERS, git init."""
    target = Path(target).resolve()
    profile = profile or pid
    name = name or pid
    if (target / CFG.project["file"]).exists():
        _say(f"BLOCKED: {target / CFG.project['file']} exists — this is already a project repo")
        return BLOCKED
    if target.exists() and any(target.iterdir()) and not yes:
        _say(f"BLOCKED: {target} is not empty — pass --yes to scaffold into it anyway")
        return BLOCKED
    target.mkdir(parents=True, exist_ok=True)
    (target / CFG.project["file"]).write_text(_project_yaml_text(pid, name, profile), encoding="utf-8")
    prof = _scaffold_profile(profile, target / CFG.paths["profiles"])
    (target / CFG.paths["profiles"] / profile / "knowledge").mkdir(parents=True, exist_ok=True)
    (target / CFG.paths["profiles"] / profile / "knowledge" / ".gitkeep").touch()
    created = []
    for key in CFG.external.get("keys") or ():
        sub = CFG.paths[key]
        if key == "profiles" or not isinstance(sub, str) or Path(sub).suffix:
            continue                      # a file key (the overview) is rendered, not scaffolded
        d = target / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch()
        created.append(sub)
    for part, spec in CFG.project["partitions"].items():
        sub = spec["path"].split("{MOD}")[0].rstrip("/")     # up to the per-module slot
        d = target / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch()
        created.append(sub)
    (target / ".gitignore").write_text(_project_gitignore_text(), encoding="utf-8")
    (target / "CODEOWNERS").write_text(_project_codeowners_text(), encoding="utf-8")
    (target / "README.md").write_text(
        f"# {name}\n\nThe governance project repo of `{pid}`: `{CFG.project['file']}` (its facts), "
        f"`{CFG.paths['profiles']}/` (its domain profile), and the partitions the governance factory "
        f"fills — one writer per path (CODEOWNERS). Every consumer mounts this repo as a submodule "
        f"and pins a commit.\n", encoding="utf-8")
    if not (target / ".git").exists():
        _git("init", "-q", cwd=target)
        _git("add", "-A", cwd=target)
        _git("-c", "user.email=factory@local", "-c", "user.name=governance-factory",
             "commit", "-q", "-m", f"new-project: {pid} — scaffolded by the governance factory", cwd=target)
    _say(f"scaffolded project `{pid}` at {target}")
    _say(f"  {CFG.project['file']} · {rel(prof)} · {', '.join(sorted(set(created)))} · .gitignore · CODEOWNERS · git")
    _say(f"next: fill every TODO in {prof.name}, then")
    _say(f"  {CFG.project['checkout_env']}={target} gov.py lint --profile {profile}")
    _say(f"  {CFG.project['checkout_env']}={target} gov.py run-stage {CFG.stages[0].id} -m {_sanitize_mod(pid)}")
    return OK


def cmd_new_domain(pid: str) -> int:
    """Add a second profile to the CURRENT project (scaffolded from the schema).
    Activating it is an edit to the project's project.yaml — the factory never
    writes that file."""
    if not CFG.project_file().exists():
        _say(f"BLOCKED: no project at {CFG.project_checkout()} — scaffold one with gov.py new-project, or set {CFG.project['checkout_env']}")
        return BLOCKED
    try:
        dst = _scaffold_profile(pid, CFG.profiles_dir())
    except FileExistsError as e:
        _say(f"BLOCKED: {e}")
        return BLOCKED
    _say(f"scaffolded {dst} in project `{CFG.project_data.get('project', {}).get('id', '?')}`")
    _say(f"next: fill every TODO, `gov.py lint --profile {pid}`, then set `profile: {pid}` in {CFG.project_file().name} to activate it")
    return OK


# ── CLI ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="gov.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def mv(p, version=True, module=True):
        p.add_argument("-m", "--module", required=module, default=None)
        if version:
            p.add_argument("-v", "--version", type=int)
        return p

    p = mv(sub.add_parser("run-stage")); p.add_argument("stage"); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true"); p.add_argument("--regenerate", action="store_true", help="clear this stage's own output first, then run it fresh")
    p = sub.add_parser("run-standalone")   # -m/--modules/--scope: see run_standalone() — richer than mv() for test-gen's scopes
    p.add_argument("stage"); p.add_argument("-m", "--module"); p.add_argument("--modules")
    p.add_argument("--scope", choices=["module", "project"], default="module")
    p.add_argument("-v", "--version", type=int); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("run-pass")); p.add_argument("pass_no"); p.add_argument("--new", action="store_true"); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true"); p.add_argument("--redo", action="store_true", help="re-run stages that are already complete"); p.add_argument("--regenerate", action="store_true", help="clear this pass's own output first, then run it fresh")
    p = mv(sub.add_parser("gate")); p.add_argument("pass_no"); p.add_argument("--complete", action="store_true"); p.add_argument("--result"); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("approve")); p.add_argument("gate"); p.add_argument("--by", default=os.environ.get("USER", "human")); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("analyze"), module=False); p.add_argument("--scope", default="all")
    p.add_argument("--all-modules", action="store_true", help="re-analyze every module at its current version")
    mv(sub.add_parser("state"))
    p = mv(sub.add_parser("version"), version=False); p.add_argument("--new", action="store_true")
    mv(sub.add_parser("tag"))
    p = mv(sub.add_parser("fetch-inputs")); p.add_argument("--pull", action="store_true")
    p = sub.add_parser("publish"); p.add_argument("name", nargs="?", default=None); p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("feedback"); p.add_argument("-m", "--module"); p.add_argument("-v", "--verbose", action="store_true")
    p = sub.add_parser("sparse"); p.add_argument("--track", required=True); p.add_argument("--apply-to", dest="apply_to")
    p = mv(sub.add_parser("waive-feedback")); p.add_argument("--pass", dest="pass_no", required=True); p.add_argument("--by", required=True); p.add_argument("--why", required=True)
    p = sub.add_parser("sync"); p.add_argument("--push", action="store_true"); p.add_argument("--dry-run", action="store_true")
    p = mv(sub.add_parser("verify-split")); p.add_argument("--track", required=True); p.add_argument("--plan", default=None)
    mv(sub.add_parser("status"), version=False)
    p = mv(sub.add_parser("next")); p.add_argument("--run", action="store_true", help="execute the step instead of printing it")
    p = mv(sub.add_parser("structure")); p.add_argument("--dry-run", action="store_true")
    p = mv(sub.add_parser("archive")); p.add_argument("--source", required=True); p.add_argument("--force", action="store_true"); p.add_argument("--dry-run", action="store_true")
    p = mv(sub.add_parser("split")); p.add_argument("--track", required=True); p.add_argument("--plan", default=None)
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--strict", action="store_true"); p.add_argument("--fix-safe", action="store_true")
    sub.add_parser("render")
    p = sub.add_parser("lint"); p.add_argument("--profile")
    p = sub.add_parser("new-project"); p.add_argument("dir"); p.add_argument("--id", required=True)
    p.add_argument("--name", default=None); p.add_argument("--profile", default=None, help="profile id (default: the project id)")
    p.add_argument("--yes", action="store_true", help="scaffold into a non-empty directory")
    p = sub.add_parser("new-domain"); p.add_argument("id")
    a = ap.parse_args(argv)

    if a.cmd == "run-stage":
        return run_stage(a.stage, a.module, a.version, a.complete, a.no_commit, a.regenerate)
    if a.cmd == "run-standalone":
        return run_standalone(a.stage, a.module, a.modules, a.scope, a.version, a.complete, a.no_commit)
    if a.cmd == "run-pass":
        return run_pass(a.pass_no, a.module, a.version, a.new, a.complete, a.no_commit, a.redo, a.regenerate)
    if a.cmd == "gate":
        return gate(a.pass_no, a.module, a.version, a.complete, Path(a.result) if a.result else None, a.no_commit)
    if a.cmd == "approve":
        return approve(a.gate, a.module, a.version, a.by, a.no_commit)
    if a.cmd == "analyze":
        if a.all_modules:
            return cmd_analyze_all(a.scope)
        if not a.module:
            _say("BLOCKED: analyze needs -m MOD (or --all-modules)")
            return BLOCKED
        rep = an.run(a.module, a.version, scope=a.scope)
        c = rep.counts()
        vac = rep.vacuous()
        # CLEAN over an empty set reads exactly like CLEAN over a full one, and
        # that is the shape every silent-success defect in this repo has had.
        tail = f" · {len(vac)} clause(s) examined nothing ({', '.join(vac)})" if vac else ""
        _say(f"analyze {a.scope} → {counts_line(c)} · {'CLEAN' if rep.clean else 'BLOCKED'}{tail}")
        for f in rep.findings:
            _say("  ", f)
        # a clause that could not run is not a clause that passed. It reached the
        # report and stopped there, where a reader gating on the terminal never saw it.
        for s in rep.skipped:
            _say("  SKIPPED   ", s)
        return OK if rep.clean else BLOCKED
    if a.cmd == "state":
        rep = st.build_state(a.module, a.version)
        _say(f"state {rep.mod} v{rep.version}: {len(rep.files)} file(s), missing {rep.missing or 'none'}")
        return OK
    if a.cmd == "version":
        cmd_version(a.module, a.new); return OK
    if a.cmd == "tag":
        return cmd_tag(a.module, _version(a.module, a.version))
    if a.cmd == "fetch-inputs":
        return cmd_fetch_inputs(a.module, _version(a.module, a.version), a.pull)
    if a.cmd == "sync":
        return cmd_sync(push=a.push, dry_run=a.dry_run)
    if a.cmd == "publish":
        return cmd_publish(a.name, a.dry_run)
    if a.cmd == "feedback":
        return cmd_feedback(a.module, a.verbose)
    if a.cmd == "sparse":
        return cmd_sparse(a.track, a.apply_to)
    if a.cmd == "waive-feedback":
        return cmd_waive_feedback(a.module, a.version, a.pass_no, a.by, a.why)
    if a.cmd == "verify-split":
        return cmd_verify_split(a.track, a.module, _version(a.module, a.version), a.plan)
    if a.cmd == "status":
        return cmd_status(a.module)
    if a.cmd == "next":
        return cmd_next(a.module, a.version, a.run)
    if a.cmd == "structure":
        created = tk_struct.ensure_structure(a.module, a.version, dry_run=a.dry_run)
        _say(f"structure: {len(created)} folder(s) {'would be ' if a.dry_run else ''}created"); return OK
    if a.cmd == "archive":
        rep = tk_archive(a.module, a.version, Path(a.source), force=a.force, dry_run=a.dry_run)
        _say(f"archive [{rep.module}] v{rep.version} ← {rep.source_dir}"
             f"{' [dry-run]' if rep.dry_run else ''}: {len(rep.copied)} copied, "
             f"{len(rep.overwritten)} overwritten, {len(rep.kept_existing)} kept, "
             f"{len(rep.skipped_missing)} missing")
        for w in rep.warnings:
            _say("  WARN", w)
        for e in rep.errors:
            _say("  ERROR", e)
        # The report's verdict IS the exit code. Returning OK unconditionally
        # reported a successful archive even when nothing was copied.
        return OK if rep.ok else BLOCKED
    if a.cmd == "split":
        plans = [a.plan] if a.plan else [pl for pl in CFG.tracks[a.track]["packages"] if pl in CFG.profile.plans(a.track)]
        rc = OK
        if not plans:
            _say(f"BLOCKED: track {a.track} declares no plan that the active profile also declares — nothing to split.")
            return BLOCKED
        # A plan the operator NAMED must exist; when iterating a whole track,
        # a plan the pipeline has not generated yet is a legitimate "not yet".
        # What is never legitimate is splitting NOTHING and reporting success —
        # that is how a split silently never happened.
        named = a.plan is not None
        split_any = False
        for pl in plans:
            src = CFG.plan_path(a.module, a.track, pl, a.version)
            if not src.exists():
                _say(f"split {a.track}/{pl}: skipped — plan not found at {rel(src)}"
                     + (" (generate it, then archive it into the module)." if named else " (not generated yet)."))
                if named:
                    rc = BLOCKED
                continue
            split_any = True
            rep = tk_split.split(a.module, a.track, pl, a.version, dry_run=a.dry_run, strict=a.strict, fix_safe=a.fix_safe)
            v = rep.verification or {}
            _say(f"split {a.track}/{pl} v{rep.version}: {len(rep.written)} file(s), {len(rep.findings)} finding(s), "
                 f"verify {'ok' if v.get('ok') else 'FAILED'} ({v.get('checked', 0)} checked){' [dry-run]' if a.dry_run else ''}")
            for f in rep.findings[:20]:
                _say("  ", f)
            for e in rep.errors:
                _say("  ERROR", e)
            if rep.blocked or rep.errors or (v and not v.get("ok", True)):
                rc = BLOCKED
        if not split_any:
            _say(f"BLOCKED: no plan of track {a.track} exists for [{a.module}] v"
                 f"{_version(a.module, a.version)} — nothing was split. Looked for: "
                 + ", ".join(rel(CFG.plan_path(a.module, a.track, pl, a.version)) for pl in plans))
            rc = BLOCKED
        return rc
    if a.cmd == "render":
        for pth in rd.render_all():
            _say("rendered", rel(pth))
        for pth in rd.unmanaged_commands(CFG):
            _say(f"KEPT {rel(pth)} — no generated marker, so not this render's to delete; "
                 f"declare it in factory.yaml → commands or remove it by hand (lint refuses it until then)")
        return OK
    if a.cmd == "lint":
        import lint
        fs = lint.run(profile_id=a.profile)
        for f in fs:
            _say(f)
        _say(counts_line(lint.counts(fs)))
        # the same blocking policy analyze gates on — one declaration, two readers
        return BLOCKED if blocks(fs) else OK
    if a.cmd == "new-project":
        return cmd_new_project(Path(a.dir), a.id, a.name, a.profile, yes=a.yes)
    if a.cmd == "new-domain":
        return cmd_new_domain(a.id)
    return OK


if __name__ == "__main__":
    sys.exit(main())
