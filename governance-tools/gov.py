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
  status -m MOD
  publish [name] [--dry-run]                                           # factory publications → into each consumer repo
  structure/archive/split (toolkit) · render · lint [--profile ID]
  new-domain ID [--yes|--force] [--module CODE]   # resets stale project content, then starts ID

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

    Artifacts live in the shared repo now (`paths.external`), and that repo
    reaches this one as a submodule. `git add` run in the factory root over a
    submodule path stages the POINTER, not the content, and commits cleanly
    while saving nothing — the worst shape a failure can take. So the repo is
    derived from the declared checkouts rather than assumed to be this one, and
    innermost wins so a submodule beats the parent that contains it."""
    p = Path(path).resolve()
    roots = {CFG.root, *(CFG.repo_checkout(r) for r in CFG.repos)}
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
    _say(f"analyze stage:{stage.id} → {counts_line(c)}")
    for f in rep.findings[:25]:
        _say("  ", f)
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


def run_stage(stage_id: str, mod: str, version: int | None, complete: bool, no_commit: bool) -> int:
    stage = CFG.stage(stage_id)
    version = _version(mod, version)
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


def run_pass(pass_no: str, mod: str, version: int | None, new: bool, complete: bool, no_commit: bool, redo: bool = False) -> int:
    p = CFG.passes[str(pass_no)]
    if new:
        version = cmd_version(mod, True, quiet=True)
    version = _version(mod, version)
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
    record = CFG.version_root(mod, version) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": pass_no})
    if not complete:
        brief = _gate_brief(g, pass_no, mod, version, rep)
        _say(f"AWAITING REVIEW: gate brief → {rel(brief)} (lanes {', '.join(f'`{l}`' for l in g['lanes'])}, read-only reviewers)")
        _say(f"  when the review JSON exists: gov.py gate {pass_no} -m {mod} -v {version} --complete --result <file.json>")
        return AWAITING
    if not result or not Path(result).exists():
        _say("BLOCKED: --complete needs --result FILE.json (the reviewer's structured output)")
        return BLOCKED
    data = json.loads(Path(result).read_text(encoding="utf-8"))
    verdict, scores = data.get("verdict", "").upper(), data.get("scores", {})
    rv = CFG.review
    low = [k for k in rv["rubric"] if int(scores.get(k, 0)) < int(rv["pass_threshold"])]
    if verdict == "APPROVE" and low:
        verdict = "REVISE"
        _say(f"verdict downgraded to REVISE: attributes below threshold {low}")
    if verdict not in rv["verdicts"]:
        _say(f"BLOCKED: verdict must be one of {rv['verdicts']}")
        return BLOCKED
    lines = [CFG.data["lint"]["generated_marker"], f"# Gate record — {g['id']} — {mod.upper()} v{version}", "",
             f"Verdict: **{verdict}** · {now_iso()} · analyze {c}", "", "| Attribute | Score |", "|---|---|"]
    lines += [f"| {k} | {scores.get(k, '—')} |" for k in rv["rubric"]]
    if data.get("findings"):
        lines += ["", "| Severity | Artifact | Clause | Finding | Fix |", "|---|---|---|---|---|"]
        lines += [f"| {f.get('severity','')} | {f.get('artifact','')} | {f.get('clause','')} | {f.get('finding', f.get('message',''))} | {f.get('fix','')} |" for f in data["findings"]]
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(record.with_suffix(".json"), {"gate": g["id"], "pass": pass_no, "verdict": verdict, "scores": scores,
                                              "findings": data.get("findings", []), "at": now_iso()})
    _commit([CFG.version_root(mod, version)], CFG.commit_msg("gate", **{"pass": pass_no}, mod=mod, version=version, verdict=verdict), no_commit)
    _say(f"GATE {g['id']}: {verdict}")
    return OK if verdict == "APPROVE" else BLOCKED


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


def cmd_tag(mod: str, version: int) -> int:
    name = CFG.tag_name(mod, version)
    if _git("tag", "-l", name).stdout.strip():
        _say(f"tag {name} already exists")
        return OK
    _git("tag", "-a", name, "-m", f"{mod.upper()} v{version}")
    _say(f"tagged {name}")
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
    for name, spec in CFG.inputs.items():
        repo = spec["from_repo"]
        # WHO authors it and WHERE it lands are two questions. A producer that
        # publishes into the shared repo says so with `reads_from`; without it the
        # path resolves against the producer's own checkout, as before.
        host = CFG.repos[repo].get("reads_from", repo)
        checkout = CFG.repo_checkout(host)
        src = checkout / CFG.fmt(CFG.repos[repo]["publishes"][name], mod=mod)
        if pull and (checkout / ".git").exists():
            _git("pull", "--ff-only", cwd=checkout, check=False)
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
                continue
            dst.write_text(text, encoding="utf-8")
            n = len(sorted(src.glob(spec["merge"].get("include") or "**/*.md")))
            _say(f"fetched {name} ({n} files folded) → {rel(dst)}")
        else:
            shutil.copy2(src, dst)
            _say(f"fetched {name} → {rel(dst)}")
        companion = (spec.get("merge") or {}).get("keep_alongside")
        if companion:
            c = dst.parent / CFG.fmt(companion, mod=mod)
            if c.exists():
                _say(f"  kept {c.name} (written here, never fetched)")
    if missing:
        _say("GATE CLOSED — missing inputs:\n  " + "\n  ".join(missing))
        return BLOCKED
    return OK


def _shared_repo() -> str:
    return CFG.shared_repo()


def _partitions() -> dict[str, str]:
    return CFG.partitions()


def _per_module(part: str) -> bool:
    return CFG.partition_is_per_module(part)


def _shared_dir(part: str, mod: str | None = None) -> Path:
    return CFG.partition_dir(part, mod)


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
    host = _shared_repo()
    shared = CFG.repo_checkout(host)
    if not (shared / ".git").exists():
        _say(f"BLOCKED: shared checkout not found at {shared}\n"
             f"  clone it, or set {CFG.repos[host]['checkout_env']} — and if this is a\n"
             f"  fresh clone of a consumer, it is a submodule: `git submodule update --init`")
        return BLOCKED

    # Which submodule is the shared one is decided by its URL, not by a folder
    # name: each repo mounts it at a path of its own choosing, and matching on a
    # name would silently match nothing in the repo that chose a different one.
    url = (CFG.repos[host].get("url") or "").strip()
    stale = []
    for name in CFG.repos:
        if name == host:
            continue
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

    _say(f"shared @ {head}" + (f" · upstream {upstream} (behind {behind}, ahead {ahead})" if upstream else " · no upstream"))
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
        _say(f"  uncommitted in shared: {len(dirty)} path(s)")
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
        _say("dry-run" if dry_run else "nothing to push — shared is clean")
        return OK
    _git("add", "-A", cwd=shared)
    _git("commit", "-m", "sync from factory", cwd=shared)
    _git("push", cwd=shared)
    _say(f"pushed shared @ {_git('rev-parse', '--short', 'HEAD', cwd=shared).stdout.strip()}")
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
        if track not in _partitions():
            continue
        for m in ([mod.upper()] if mod else CFG.modules()):
            state = _shared_dir(track, m) / spec["file"]
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
    """Write every factory publication INTO each consumer repo that declares it.

    A consumer reads only paths inside its own checkout — no file above a repo root,
    no reach into a sibling repo's tree. The factory is the single writer; the consumer
    copies are read-only mirrors, byte-identical by construction rather than by hand.
    """
    names = [name] if name else list(CFG.publications)
    rc = OK
    for pub in names:
        targets = {r: CFG.repo_receives(r, pub) for r in CFG.repos}
        targets = {r: p for r, p in targets.items() if p}
        if not targets:
            _say(f"{pub}: no repo declares it under `receives` — nothing to publish")
            continue
        live = {r: p for r, p in targets.items() if CFG.repo_checkout(r).exists()}
        for r in targets.keys() - live.keys():
            _say(f"{pub}: SKIPPED {r} — checkout not found at {CFG.repo_checkout(r)} "
                 f"(set ${CFG.repos[r]['checkout_env']})")
            rc = BLOCKED
        payload = publications.payload(pub, [read_json(p, {}) or {} for p in live.values()])
        body = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        for r, path in live.items():
            before = path.read_text(encoding="utf-8") if path.exists() else None
            if before == body:
                _say(f"{pub} → {r}: unchanged")
                continue
            if dry_run:
                _say(f"{pub} → {r}: WOULD WRITE {path} ({'new' if before is None else 'changed'})")
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
            _say(f"{pub} → {r}: wrote {path} ({'new' if before is None else 'updated'})")
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
        tag = "tagged" if _git("tag", "-l", CFG.tag_name(mod, v)).stdout.strip() else "untagged"
        have = [s.id for s in CFG.stages if all(CFG.artifact_path(mod, s.id, a.artifact, v).exists() for a in s.produces if not a.optional and not a.dir) and any(not a.dir for a in s.produces)]
        inputs = [n for n, spec in CFG.inputs.items() if (CFG.inputs_dir(mod, v) / CFG.fmt(spec["file"], mod=mod)).exists()]
        gates = [p.stem for p in (CFG.state_dir(mod, v) / "approvals").glob("*.json")] if (CFG.state_dir(mod, v) / "approvals").exists() else []
        stale = an.stale_reason(mod, v, "all")
        pattern = CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": "*"}).replace(".md", ".json")
        gates += [p.stem for p in root.glob(pattern)]
        _say(f"  v{v}: stages {have} · inputs {inputs} · gates {gates} · {tag} · state {'fresh' if st.is_fresh(mod, v) else 'stale'}"
             f" · verdict {'current' if stale is None else 'STALE — ' + stale}")
    return OK


# ── domain scaffolding / reset ───────────────────────────────────────────────
# `new-domain ID` resets stale project content (prior profiles/modules/decisions/
# generated project docs), scaffolds profiles/ID.yaml, re-renders every doc
# derived from the (now new) active profile — README.md, engines/*/SKILL.md,
# standalone/*/SKILL.md, shared/START-HERE.md, any hand-written doc with a
# RENDER block — so none of them keep echoing the prior domain, then drops
# straight into the first stage of the pipeline — see
# PROMPT-ADD-RESET-AND-START-TO-NEW-DOMAIN.

@dataclass
class ResetPlan:
    profile_files: list[Path]
    profile_dirs: list[Path]
    module_dirs: list[Path]
    decision_entries: list[Path]
    project_files: list[Path]


def _protected_roots() -> list[Path]:
    return [CFG.dir("tools"), CFG.root / "_archive-v5", CFG.root / "history"]


def _under_any(path: Path, roots: list[Path]) -> bool:
    return any(root == path or root in path.parents for root in roots)


def _profile_files() -> list[Path]:
    d = CFG.profiles_dir()
    return sorted(p for p in d.glob("*.yaml") if p.name != "_schema.yaml") if d.exists() else []


def _profile_dirs() -> list[Path]:
    """Companion dirs of a profile (e.g. profiles/<id>/knowledge/ — schema §knowledge.files)."""
    d = CFG.profiles_dir()
    return sorted(p for p in d.iterdir() if p.is_dir()) if d.exists() else []


def _module_dirs() -> list[Path]:
    root = CFG.modules_root()
    return sorted(p for p in root.iterdir() if p.is_dir()) if root.exists() else []


def _decision_entries() -> list[Path]:
    root = CFG.dir("decisions")
    return sorted(root.iterdir()) if root.exists() else []


def _project_generated_files() -> list[Path]:
    """Every stage artifact with a bare `dir` (platform-level, e.g. domain-profile.md,
    project-registry.md) — read from the stage table, never a literal filename list."""
    seen: set[Path] = set()
    for s in CFG.all_stages():
        for a in s.produces:
            if a.dir:
                p = CFG.dir(a.dir) / a.filename("")
                if p.exists():
                    seen.add(p)
    return sorted(seen)


def _build_reset_plan() -> ResetPlan:
    plan = ResetPlan(_profile_files(), _profile_dirs(), _module_dirs(), _decision_entries(), _project_generated_files())
    protected = _protected_roots()
    for p in (*plan.profile_files, *plan.profile_dirs, *plan.module_dirs, *plan.decision_entries, *plan.project_files):
        if _under_any(p, protected):
            raise RuntimeError(f"refusing to reset: {p} is inside a protected path")
    return plan


def _reset_summary(plan: ResetPlan) -> str:
    proj_dirs = sorted({CFG.paths[a.dir] for s in CFG.all_stages() for a in s.produces if a.dir})
    proj_label = "/".join(proj_dirs) + "/" if proj_dirs else "(none)/"
    names = ", ".join(p.name for p in plan.project_files) if plan.project_files else "none"
    bar = "═" * 56
    return "\n".join([
        bar,
        "RESET — this will permanently delete:",
        f"  {CFG.paths['profiles']}/*.yaml                 ({len(plan.profile_files)} files)",
        f"  {CFG.paths['profiles']}/*/ (companion dirs)     ({len(plan.profile_dirs)} dirs)",
        f"  {CFG.paths['modules']}/*                       ({len(plan.module_dirs)} module folders)",
        f"  {CFG.paths['decisions']}/*                     ({len(plan.decision_entries)} entries)",
        f"  {proj_label} generated content ({names})",
        "Kept: governance-tools/, templates/, factory.yaml's own structure,",
        "      _archive-v5/, history/, tests",
        bar,
    ])


def _do_reset(plan: ResetPlan) -> None:
    for p in plan.profile_files:
        p.unlink(missing_ok=True)
    for d in plan.profile_dirs:
        shutil.rmtree(d, ignore_errors=True)
    for d in plan.module_dirs:
        shutil.rmtree(d, ignore_errors=True)
    for e in plan.decision_entries:
        if e.is_dir():
            shutil.rmtree(e, ignore_errors=True)
        else:
            e.unlink(missing_ok=True)
    for f in plan.project_files:
        f.unlink(missing_ok=True)
    # domain/platform/modules/decisions all nest under one folder named after the
    # (still-active, pre-reload) profile's own identity — once its contents are gone,
    # remove the now-empty folder too, so reset never leaves a stale <old-id>/ behind.
    project_root = CFG.dir("domain")
    if project_root.exists() and project_root != CFG.root:
        try:
            project_root.rmdir()
        except OSError:
            pass  # not empty (unexpected extra content) — leave it for the user to inspect


def _git_dirty() -> bool:
    r = _git("status", "--short", check=False)
    if r.returncode != 0:      # not a git repo (or git unavailable) — be conservative
        return True
    return bool(r.stdout.strip())


# -- factory.yaml instance-value reset (surgical text patch: factory.yaml is
#    hand-maintained prose with heavy comments; a yaml.safe_load/dump round-trip
#    would silently destroy all of it, so this only rewrites the value tokens) --

def _yaml_scalar(value: str) -> str:
    return value if re.fullmatch(r"[A-Za-z0-9_-]+", value) else json.dumps(value)


def _block_span(text: str, key: str, key_indent: str, child_indent: str) -> tuple[int, int]:
    """(start, end) of the indented body directly under a `{key_indent}{key}:` line."""
    m = re.search(rf"(?m)^{re.escape(key_indent)}{re.escape(key)}:[ \t]*\n", text)
    if not m:
        raise ValueError(f"{key!r} block not found")
    start = end = m.end()
    for lm in re.finditer(r"(?m)^(.*)\n", text[start:]):
        line = lm.group(1)
        if line.strip() == "" or line.startswith(child_indent):
            end = start + lm.end()
        else:
            break
    return start, end


def _repo_block_span(repos_block: str, repo_name: str) -> tuple[int, int]:
    return _block_span(repos_block, repo_name, "  ", "    ")


def _replace_scalar(block: str, key: str, new_value: str) -> str:
    pattern = re.compile(rf'(?m)^(\s*{re.escape(key)}:\s*)("[^"]*"|\S+)')
    new_block, n = pattern.subn(lambda m: m.group(1) + new_value, block, count=1)
    if n == 0:
        raise ValueError(f"key {key!r} not found")
    return new_block


def _reset_factory_yaml_instance_values(pid: str) -> None:
    """Clear repos.<name>.url/checkout_default to placeholders and point
    factory.active_profile at the new domain — everything else untouched."""
    path = CFG.root / "factory.yaml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(  active_profile:\s*)\S+", rf"\g<1>{_yaml_scalar(pid)}", text, count=1)
    repos_start, repos_end = _block_span(text, "repos", "", "  ")
    repos_block = text[repos_start:repos_end]
    for name in CFG.data["repos"]:
        start, end = _repo_block_span(repos_block, name)
        block = repos_block[start:end]
        block = _replace_scalar(block, "url", '""')
        block = _replace_scalar(block, "checkout_default", f'"../{name}"')
        repos_block = repos_block[:start] + block + repos_block[end:]
    text = text[:repos_start] + repos_block + text[repos_end:]
    path.write_text(text, encoding="utf-8")


def _sanitize_mod(pid: str) -> str:
    m = re.sub(r"[^A-Za-z0-9]", "", pid).upper()
    if not m or not m[0].isalpha():
        m = "M" + m
    return m


def _scaffold_profile(pid: str) -> Path:
    dst = CFG.profiles_dir() / f"{pid}.yaml"
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

    text = ["# profile scaffold generated by gov.py new-domain — fill every TODO, then gov.py lint --profile " + pid,
            f"schema_version: {schema.get('schema_version', CFG.data['schema_version'])}", *skel(schema)]
    text = [l.replace("id: TODO", f"id: {pid}") for l in text]
    dst.write_text("\n".join(text) + "\n", encoding="utf-8")
    return dst


def cmd_new_domain(pid: str, *, yes: bool = False, module: str | None = None) -> int:
    if _git_dirty():
        _say("BLOCKED: uncommitted changes present — commit or stash first (new-domain permanently deletes prior project content).")
        return BLOCKED
    plan = _build_reset_plan()
    _say(_reset_summary(plan))
    if not yes:
        try:
            ans = input("Proceed? [y/N] ")
        except EOFError:
            ans = ""
        if ans.strip().lower() != "y":
            _say("Aborted: no changes made.")
            return BLOCKED
    _do_reset(plan)
    _reset_factory_yaml_instance_values(pid)
    dst = _scaffold_profile(pid)
    CFG.reload()
    _say(f"scaffolded {rel(dst)} · factory.yaml active_profile → {pid}")
    rendered = rd.render_all()   # README.md, engines/*/SKILL.md, standalone/*/SKILL.md, shared/START-HERE.md
    _say(f"re-rendered {len(rendered)} profile-derived doc(s) — no stale reference to the prior domain")
    mod = module or _sanitize_mod(pid)
    stage = CFG.stages[0]                 # the pipeline's first stage, run-order (factory.yaml stages:)
    _say(f"continuing into `{stage.id}` for module {mod} …")
    return run_stage(stage.id, mod, None, False, False)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="gov.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def mv(p, version=True, module=True):
        p.add_argument("-m", "--module", required=module, default=None)
        if version:
            p.add_argument("-v", "--version", type=int)
        return p

    p = mv(sub.add_parser("run-stage")); p.add_argument("stage"); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true")
    p = sub.add_parser("run-standalone")   # -m/--modules/--scope: see run_standalone() — richer than mv() for test-gen's scopes
    p.add_argument("stage"); p.add_argument("-m", "--module"); p.add_argument("--modules")
    p.add_argument("--scope", choices=["module", "project"], default="module")
    p.add_argument("-v", "--version", type=int); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("run-pass")); p.add_argument("pass_no"); p.add_argument("--new", action="store_true"); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true"); p.add_argument("--redo", action="store_true", help="re-run stages that are already complete")
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
    p = mv(sub.add_parser("waive-feedback")); p.add_argument("--pass", dest="pass_no", required=True); p.add_argument("--by", required=True); p.add_argument("--why", required=True)
    p = sub.add_parser("sync"); p.add_argument("--push", action="store_true"); p.add_argument("--dry-run", action="store_true")
    p = mv(sub.add_parser("verify-split")); p.add_argument("--track", required=True); p.add_argument("--plan", default=None)
    mv(sub.add_parser("status"), version=False)
    p = mv(sub.add_parser("structure")); p.add_argument("--dry-run", action="store_true")
    p = mv(sub.add_parser("archive")); p.add_argument("--source", required=True); p.add_argument("--force", action="store_true"); p.add_argument("--dry-run", action="store_true")
    p = mv(sub.add_parser("split")); p.add_argument("--track", required=True); p.add_argument("--plan", default=None)
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--strict", action="store_true"); p.add_argument("--fix-safe", action="store_true")
    sub.add_parser("render")
    p = sub.add_parser("lint"); p.add_argument("--profile")
    p = sub.add_parser("new-domain"); p.add_argument("id")
    p.add_argument("--yes", "--force", dest="yes", action="store_true", help="skip the confirmation prompt (the uncommitted-changes check still applies)")
    p.add_argument("--module", "-m", default=None, help="initial module code for the domain-profile stage (default: derived from ID)")
    a = ap.parse_args(argv)

    if a.cmd == "run-stage":
        return run_stage(a.stage, a.module, a.version, a.complete, a.no_commit)
    if a.cmd == "run-standalone":
        return run_standalone(a.stage, a.module, a.modules, a.scope, a.version, a.complete, a.no_commit)
    if a.cmd == "run-pass":
        return run_pass(a.pass_no, a.module, a.version, a.new, a.complete, a.no_commit, a.redo)
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
    if a.cmd == "waive-feedback":
        return cmd_waive_feedback(a.module, a.version, a.pass_no, a.by, a.why)
    if a.cmd == "verify-split":
        return cmd_verify_split(a.track, a.module, _version(a.module, a.version), a.plan)
    if a.cmd == "status":
        return cmd_status(a.module)
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
        return OK
    if a.cmd == "lint":
        import lint
        fs = lint.run(profile_id=a.profile)
        for f in fs:
            _say(f)
        _say(counts_line(lint.counts(fs)))
        # the same blocking policy analyze gates on — one declaration, two readers
        return BLOCKED if blocks(fs) else OK
    if a.cmd == "new-domain":
        return cmd_new_domain(a.id, yes=a.yes, module=a.module)
    return OK


if __name__ == "__main__":
    sys.exit(main())
