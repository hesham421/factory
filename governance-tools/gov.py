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
  deliver --track T -m MOD -v N [--push] · status -m MOD
  structure/archive/split (toolkit) · render · lint [--profile ID]
  new-domain ID [--yes|--force] [--module CODE]   # resets stale project content, then starts ID

Exit codes: 0 ok · 1 blocked (findings / missing) · 2 awaiting the operator (manual runner)
"""
from __future__ import annotations

import argparse
import json
import os
import re
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
import render as rd                         # noqa: E402
import state as st                          # noqa: E402
from toolkit import archive as tk_archive, splitter as tk_split, structure as tk_struct   # noqa: E402
from toolkit.common import blocks, counts_line, now_iso, write_json   # noqa: E402

OK, BLOCKED, AWAITING = 0, 1, 2


# ── git ─────────────────────────────────────────────────────────────────────

def _git(*args: str, cwd: Path | None = None, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd or CFG.root), check=check, capture_output=capture, text=True)


def _commit(paths: list[Path], message: str, no_commit: bool = False) -> str | None:
    if no_commit:
        return None
    rels = [str(p.relative_to(CFG.root)) for p in paths if p.exists()]
    if not rels:
        return None
    _git("add", "-A", "--", *rels)
    if _git("diff", "--cached", "--quiet", check=False).returncode == 0:
        return None
    _git("-c", "user.email=factory@local", "-c", "user.name=governance-factory", "commit", "-q", "-m", message)
    return _git("rev-parse", "--short", "HEAD").stdout.strip()


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
        _say(f"AWAITING OPERATOR: brief written → {res.brief.relative_to(CFG.root)}")
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
        _say(f"AWAITING OPERATOR: brief written → {res.brief.relative_to(CFG.root)}")
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
        _say(f"BLOCKED: {stage.id} (project scope) did not produce {sti_path.relative_to(CFG.root)}")
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
        _say(f"AWAITING OPERATOR: brief written → {res.brief.relative_to(CFG.root)}")
        _say(f"  lane `{stage.lane}` implementers {CFG.lane(stage.lane).get('implementers')} — execute the brief, write {sti_path.relative_to(CFG.root)}, then:")
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


def run_pass(pass_no: str, mod: str, version: int | None, new: bool, complete: bool, no_commit: bool) -> int:
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
        _say(f"AWAITING OPERATOR: bundled brief → {bundle.relative_to(CFG.root)}")
        _say(f"  execute stage by stage (stop at a human-approval gate), then: gov.py run-pass {pass_no} -m {mod} -v {version} --complete")
        return AWAITING
    for sid in p["stages"]:
        rc = run_stage(sid, mod, version, complete, no_commit)
        if rc != OK:
            return rc
    _say(f"pass {pass_no} stages complete → gov.py gate {pass_no} -m {mod} -v {version}")
    return OK


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
    rep = an.run(mod, version, scope=f"gate:{g['id']}")
    c = rep.counts()
    _say(f"analyze gate:{g['id']} → {counts_line(c)}")
    if g.get("requires_analyze") == "clean" and not rep.clean:
        for f in rep.findings[:25]:
            _say("  ", f)
        _say("GATE CLOSED: analyze is not clean")
        return BLOCKED
    record = CFG.version_root(mod, version) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": pass_no})
    if not complete:
        brief = _gate_brief(g, pass_no, mod, version, rep)
        _say(f"AWAITING REVIEW: gate brief → {brief.relative_to(CFG.root)} (lanes {', '.join(f'`{l}`' for l in g['lanes'])}, read-only reviewers)")
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
               artifacts=[str(p.relative_to(CFG.root)) for p in sorted(CFG.state_dir(mod, version).glob("current-*"))],
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
    p = an.approval_path(mod, version, gate_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    write_json(p, {"gate": gate_id, "module": mod.upper(), "version": version, "by": by, "at": now_iso(),
                   "after": g["after"], "artifact_sha": _artifact_shas(mod, version, g["after"])})
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
        _say(f"created {CFG.version_root(mod, v).relative_to(CFG.root)} (v{v})")
    return v


def cmd_tag(mod: str, version: int) -> int:
    name = CFG.tag_name(mod, version)
    if _git("tag", "-l", name).stdout.strip():
        _say(f"tag {name} already exists")
        return OK
    _git("tag", "-a", name, "-m", f"{mod.upper()} v{version} delivered")
    _say(f"tagged {name}")
    return OK


def cmd_fetch_inputs(mod: str, version: int, pull: bool) -> int:
    missing = []
    for name, spec in CFG.inputs.items():
        repo = spec["from_repo"]
        checkout = CFG.repo_checkout(repo)
        src = checkout / CFG.fmt(CFG.repos[repo]["publishes"][name], mod=mod)
        if pull and (checkout / ".git").exists():
            _git("pull", "--ff-only", cwd=checkout, check=False)
        if not src.exists():
            missing.append(f"{name} ← {src}")
            continue
        dst = CFG.inputs_dir(mod, version) / CFG.fmt(spec["file"], mod=mod)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        _say(f"fetched {name} → {dst.relative_to(CFG.root)}")
    if missing:
        _say("GATE CLOSED — missing inputs:\n  " + "\n  ".join(missing))
        return BLOCKED
    return OK


def cmd_deliver(track: str, mod: str, version: int, push: bool) -> int:
    repo = CFG.repos[track]
    checkout = CFG.repo_checkout(track)
    if not (checkout / ".git").exists():
        _say(f"BLOCKED: consumer checkout not found for `{track}`: {checkout} (link it in factory.yaml → repos)")
        return BLOCKED
    branch = CFG.delivery_branch(mod, version, track)
    dest = checkout / CFG.fmt(repo["deliver_to"], mod=mod)
    if version > 1:
        dest = dest / CFG.fmt(CFG.naming["version_folder"], version=version)
    _git("checkout", "-B", branch, cwd=checkout)
    delivered = []
    for plan, pkg in CFG.tracks[track]["packages"].items():
        src = CFG.packages_dir(mod, track, plan, version)
        if src.exists() and any(f.is_file() and f.name != ".gitkeep" for f in src.rglob("*")):
            tgt = dest / CFG.paths["module"]["packages_dir"] / pkg
            if tgt.exists():
                shutil.rmtree(tgt)
            shutil.copytree(src, tgt)
            delivered.append(pkg)
    index = _delivered_index(track, mod, version, dest, checkout)
    write_json(dest / CFG.paths["module"]["manifest_file"], index)
    state_file = dest / CFG.delivery["execution_state"]["file"]
    state_file.parent.mkdir(parents=True, exist_ok=True)
    write_json(state_file, _execution_state(track, mod, version, delivered, index))
    _git("add", "-A", "--", str(dest.relative_to(checkout)), cwd=checkout)
    if _git("diff", "--cached", "--quiet", cwd=checkout, check=False).returncode != 0:
        _git("-c", "user.email=factory@local", "-c", "user.name=governance-factory", "commit", "-q", "-m",
             f"governance: {mod.upper()} v{version} {track} packages from the analysis factory", cwd=checkout)
    if push:
        _git("push", "-u", "origin", branch, cwd=checkout)
    _say(f"delivered {delivered} + {state_file.name} to {checkout.name}:{branch}")
    dangling = _dangling(index, dest, checkout)
    if dangling:
        _say("WARNING: the delivered index names paths that do not exist in the consumer repo:")
        for k, v in dangling:
            _say(f"  {k} = {v}")
        return BLOCKED
    return OK


def _deliver_decisions(mod: str, dest: Path) -> str | None:
    """Copy the module's decision records INTO the delivered tree.

    The plans cite them by path; a decisions folder that lives only in the factory
    makes every one of those citations dangle for the implementer who reads the
    delivered tree — the one reader they were written for.
    """
    src = CFG.decisions_dir(mod)
    files = sorted(p for p in src.glob("*.md")) if src.exists() else []
    if not files:
        return None
    name = Path(CFG.paths["decisions"]).name
    tgt = dest / name
    if tgt.exists():
        shutil.rmtree(tgt)
    tgt.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, tgt / f.name)
    return name


def _delivered_index(track: str, mod: str, version: int, dest: Path, checkout: Path) -> dict:
    """The delivered tree's own index — every path relative to `dest`, so it resolves
    in the consumer repo. `execution-state.json` takes its path fields from THIS dict
    rather than computing its own: two generated files cannot disagree about where a
    plan lives when only one of them decides.
    """
    pkg_root = CFG.paths["module"]["packages_dir"]
    packages, plans = {}, {}
    for plan, pkg in CFG.tracks[track]["packages"].items():
        tgt = dest / pkg_root / pkg
        if tgt.exists() and any(f.is_file() and f.name != ".gitkeep" for f in tgt.rglob("*")):
            key = f"{track}/{plan}"
            packages[key] = f"{pkg_root}/{pkg}"
            plans[key] = f"{pkg_root}/{pkg}"          # a delivered plan IS its split package
    index = {
        "module": mod.upper(), "version": version, "track": track, "profile": CFG.profile_id,
        "markers_schema_version": CFG.markers["schema_version"],
        "paths_relative_to": "the directory holding this file",
        "root": ".", "packages": packages, "plans": plans,
        "generated_at": now_iso(),
    }
    decisions = _deliver_decisions(mod, dest)
    if decisions:
        index["decisions_dir"] = decisions
    for name, spec in CFG.repos[track].get("publishes", {}).items():
        target = checkout / CFG.fmt(spec, mod=mod)
        target.parent.mkdir(parents=True, exist_ok=True)
        gk = target.parent / ".gitkeep"
        if not any(target.parent.iterdir()):
            gk.touch()
        index.setdefault("publishes", {})[name] = str(Path(CFG.fmt(spec, mod=mod)).parent).replace("\\", "/")
    return index


def _dangling(index: dict, dest: Path, checkout: Path) -> list[tuple[str, str]]:
    """Every path the delivered index emits must exist. `publishes` paths are
    relative to the consumer repo root (that is where the consumer writes them);
    everything else is relative to the delivered tree."""
    out = []
    for key, value in an._walk_paths(index):
        base = checkout if key.startswith("publishes") else dest
        if not (base / value).exists():
            out.append((key, value))
    return out


def _execution_state(track: str, mod: str, version: int, delivered: list[str], index: dict) -> dict:
    from toolkit import markers as mk
    phases = []
    covered: set[str] = set()
    for plan in CFG.tracks[track]["packages"]:
        p = CFG.plan_path(mod, track, plan, version) if plan in CFG.profile.plans(track) else None
        if p and p.exists():
            res = mk.parse_structure(p.read_text(encoding="utf-8"), track, plan)
            for ph in res.phases():
                phases.append({"key": ph.id, "plan": plan, "package": index["packages"].get(f"{track}/{plan}"),
                               "atoms": [b.id for b in ph.walk() if res.grammar.is_atom(b.kind)],
                               "traces": ph.all_traces()})
                covered |= set(ph.all_traces())
    analyze_json = CFG.state_dir(mod, version) / f"analyze-gate-{_gate_for_pass(CFG.tracks[track]['pass'])['id']}.json"
    gate_json = CFG.version_root(mod, version) / CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": CFG.tracks[track]["pass"]})
    gate_json = gate_json.with_suffix(".json")
    return {
        "module": mod.upper(), "version": version, "track": track, "profile": CFG.profile_id,
        "markers_schema_version": CFG.markers["schema_version"], "packages": delivered,
        # paths come from the delivered index, never computed a second time here
        "paths": {k: index[k] for k in ("paths_relative_to", "root", "packages", "plans") if k in index}
                 | {k: index[k] for k in ("decisions_dir", "publishes") if k in index},
        "phases": phases,
        "traceability": {"covered_ids": sorted(covered), "orphan_ids": []},
        "analyze": json.loads(analyze_json.read_text())["counts"] if analyze_json.exists() else None,
        "gate": json.loads(gate_json.read_text()) if gate_json.exists() else None,
        "generated_at": now_iso(),
    }


def cmd_status(mod: str) -> int:
    vs = CFG.module_versions(mod)
    _say(f"{mod.upper()} · profile {CFG.profile_id} · versions {vs or '(none)'}")
    for v in vs:
        root = CFG.version_root(mod, v)
        tag = "tagged" if _git("tag", "-l", CFG.tag_name(mod, v)).stdout.strip() else "untagged"
        have = [s.id for s in CFG.stages if all(CFG.artifact_path(mod, s.id, a.artifact, v).exists() for a in s.produces if not a.optional and not a.dir) and any(not a.dir for a in s.produces)]
        inputs = [n for n, spec in CFG.inputs.items() if (CFG.inputs_dir(mod, v) / CFG.fmt(spec["file"], mod=mod)).exists()]
        gates = [p.stem for p in (CFG.state_dir(mod, v) / "approvals").glob("*.json")] if (CFG.state_dir(mod, v) / "approvals").exists() else []
        pattern = CFG.fmt(CFG.paths["module"]["gate_record"], **{"pass": "*"}).replace(".md", ".json")
        gates += [p.stem for p in root.glob(pattern)]
        _say(f"  v{v}: stages {have} · inputs {inputs} · gates {gates} · {tag} · state {'fresh' if st.is_fresh(mod, v) else 'stale'}")
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
    _say(f"scaffolded {dst.relative_to(CFG.root)} · factory.yaml active_profile → {pid}")
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

    def mv(p, version=True):
        p.add_argument("-m", "--module", required=True)
        if version:
            p.add_argument("-v", "--version", type=int)
        return p

    p = mv(sub.add_parser("run-stage")); p.add_argument("stage"); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true")
    p = sub.add_parser("run-standalone")   # -m/--modules/--scope: see run_standalone() — richer than mv() for test-gen's scopes
    p.add_argument("stage"); p.add_argument("-m", "--module"); p.add_argument("--modules")
    p.add_argument("--scope", choices=["module", "project"], default="module")
    p.add_argument("-v", "--version", type=int); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("run-pass")); p.add_argument("pass_no"); p.add_argument("--new", action="store_true"); p.add_argument("--complete", action="store_true"); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("gate")); p.add_argument("pass_no"); p.add_argument("--complete", action="store_true"); p.add_argument("--result"); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("approve")); p.add_argument("gate"); p.add_argument("--by", default=os.environ.get("USER", "human")); p.add_argument("--no-commit", action="store_true")
    p = mv(sub.add_parser("analyze")); p.add_argument("--scope", default="all")
    mv(sub.add_parser("state"))
    p = mv(sub.add_parser("version"), version=False); p.add_argument("--new", action="store_true")
    mv(sub.add_parser("tag"))
    p = mv(sub.add_parser("fetch-inputs")); p.add_argument("--pull", action="store_true")
    p = mv(sub.add_parser("deliver")); p.add_argument("--track", required=True); p.add_argument("--push", action="store_true")
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
        return run_pass(a.pass_no, a.module, a.version, a.new, a.complete, a.no_commit)
    if a.cmd == "gate":
        return gate(a.pass_no, a.module, a.version, a.complete, Path(a.result) if a.result else None, a.no_commit)
    if a.cmd == "approve":
        return approve(a.gate, a.module, a.version, a.by, a.no_commit)
    if a.cmd == "analyze":
        rep = an.run(a.module, a.version, scope=a.scope)
        c = rep.counts()
        _say(f"analyze {a.scope} → {counts_line(c)} · {'CLEAN' if rep.clean else 'BLOCKED'}")
        for f in rep.findings:
            _say("  ", f)
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
    if a.cmd == "deliver":
        return cmd_deliver(a.track, a.module, _version(a.module, a.version), a.push)
    if a.cmd == "status":
        return cmd_status(a.module)
    if a.cmd == "structure":
        created = tk_struct.ensure_structure(a.module, a.version, dry_run=a.dry_run)
        _say(f"structure: {len(created)} folder(s) {'would be ' if a.dry_run else ''}created"); return OK
    if a.cmd == "archive":
        rep = tk_archive.archive(a.module, a.version, Path(a.source), force=a.force, dry_run=a.dry_run)
        _say(rep); return OK
    if a.cmd == "split":
        plans = [a.plan] if a.plan else [pl for pl in CFG.tracks[a.track]["packages"] if pl in CFG.profile.plans(a.track)]
        rc = OK
        for pl in plans:
            if not (CFG.plan_path(a.module, a.track, pl, a.version)).exists():
                continue
            rep = tk_split.split(a.module, a.track, pl, a.version, dry_run=a.dry_run, strict=a.strict, fix_safe=a.fix_safe)
            v = rep.verification or {}
            _say(f"split {a.track}/{pl} v{rep.version}: {len(rep.written)} file(s), {len(rep.findings)} finding(s), "
                 f"verify {'ok' if v.get('ok') else 'FAILED'} ({v.get('checked', 0)} checked){' [dry-run]' if a.dry_run else ''}")
            for f in rep.findings[:20]:
                _say("  ", f)
            if rep.blocked or rep.errors or (v and not v.get("ok", True)):
                rc = BLOCKED
        return rc
    if a.cmd == "render":
        for pth in rd.render_all():
            _say("rendered", pth.relative_to(CFG.root))
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
