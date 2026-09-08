"""Splitter (k, l): exec plan per phase, test plan flat, index, verification, idempotency."""
from __future__ import annotations

import json

from config import CFG
from toolkit import ensure_structure, load_manifest, split, verify
from toolkit.common import flat_plan, generated_marker, plan_key
from toolkit.markers import parse_structure
from toolkit.splitter import INDEX_FILE, SECTIONS_FILE, STATE_FILE, VERIFICATION_FILE, HEADER_SUFFIX

import planfx as fx


def _put_plan(mod, track, plan, text, version=1):
    ensure_structure(mod, version)
    p = CFG.plan_path(mod, track, plan, version)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _md(folder, recursive=False):
    it = folder.rglob("*.md") if recursive else folder.glob("*.md")
    return {f.name for f in it if f.name != INDEX_FILE}


# ── (k) exec plan → folders / files / headers / _SECTIONS / index / verification ──

def test_split_exec_plan_layout(factory_root, mod):
    _put_plan(mod, "backend", "exec", fx.exec_plan(mod))
    rep = split(mod, "backend", "exec", 1)
    assert rep.ok, (rep.errors, rep.findings, rep.verification)
    g = fx.grammar("backend", "exec")
    container = CFG.packages_dir(mod, "backend", "exec", 1)
    res = parse_structure(rep.source.read_text(encoding="utf-8"), "backend", "exec")
    for ph in g.phases:
        folder = container / ph.folder
        block = next(b for b in res.phases() if b.id == ph.key)
        subs = res.subs_of(block)
        if subs:
            assert _md(folder) == {f"{s.id}.md" for s in subs} | {f"{ph.key}{HEADER_SUFFIX}.md"}
            header = (folder / f"{ph.key}{HEADER_SUFFIX}.md").read_text(encoding="utf-8")
            assert "Phase-level strategy" in header and g.sub_kind + ":" not in header
        else:
            assert _md(folder) == {f"{ph.key}.md"}
            assert (folder / f"{ph.key}.md").read_text(encoding="utf-8").rstrip().endswith(f"<!-- {g.phase_kind}:{ph.key}:END -->")
        assert (folder / INDEX_FILE).read_text(encoding="utf-8").startswith(generated_marker())
    sections = container / SECTIONS_FILE
    assert sections.exists() and "Handoff Summary" in sections.read_text(encoding="utf-8")
    assert (container / INDEX_FILE).exists()
    v = json.loads((container / VERIFICATION_FILE).read_text(encoding="utf-8"))
    assert v["ok"] and v["verify"] == CFG.markers["rules"]["verify"]
    assert v["checked"] == len(res.atoms()) + sum(len(res.subs_of(p)) or 1 for p in res.phases())
    st = json.loads((container / STATE_FILE).read_text(encoding="utf-8"))
    assert st["markers_schema_version"] == CFG.markers["schema_version"] and st["verified"] is True
    assert set(st["files"]) == {str(p.relative_to(factory_root)) for p in rep.written}
    assert load_manifest(mod, 1)["status"]["split"][plan_key("backend", "exec")] is True


def test_sub_files_named_by_label_not_double_prefixed(factory_root, mod):
    _put_plan(mod, "backend", "exec", fx.exec_plan(mod))
    split(mod, "backend", "exec", 1)
    g = fx.grammar("backend", "exec")
    ph = fx.threshold_phase(g)
    names = _md(CFG.packages_dir(mod, "backend", "exec", 1) / ph.folder)
    label = ph.sub_labels[0]
    assert f"{ph.key}-{label}.md" in names and f"{ph.key}-{ph.key}-{label}.md" not in names


def test_unit_files_carry_traces_and_source_header(factory_root, mod):
    _put_plan(mod, "backend", "exec", fx.exec_plan(mod))
    split(mod, "backend", "exec", 1)
    g = fx.grammar("backend", "exec")
    ph = fx.threshold_phase(g)
    kind = fx.countable_kind(g, ph)
    f = CFG.packages_dir(mod, "backend", "exec", 1) / ph.folder / f"{ph.key}-{ph.sub_labels[0]}.md"
    lines = f.read_text(encoding="utf-8").splitlines()
    assert lines[0] == f"<!-- source: {g.phase_kind}:{ph.key} / {g.sub_kind}:{ph.key}-{ph.sub_labels[0]} -->"
    assert lines[1].startswith("<!-- context: ") and f"{ph.key}{HEADER_SUFFIX}.md" in lines[1]
    assert lines[2] == f"<!-- traces: {fx.trace_id(g, kind, mod)} -->"
    assert lines[3].startswith(f"<!-- {g.sub_kind}:{ph.key}-{ph.sub_labels[0]}:START")


def test_split_frontend_exec_plan_uses_frontend_phases(factory_root, mod):
    _put_plan(mod, "frontend", "exec", fx.exec_plan(mod, "frontend", "exec"))
    rep = split(mod, "frontend", "exec", 1)
    assert rep.ok, (rep.findings, rep.verification)
    container = CFG.packages_dir(mod, "frontend", "exec", 1)
    assert {p.name for p in container.iterdir() if p.is_dir()} == {p.folder for p in CFG.profile.phases("frontend", "exec")}
    sub_bearing = next(p for p in CFG.profile.phases("frontend", "exec") if p.sub_bearing)
    assert f"{sub_bearing.key}-UNIT-001.md" in _md(container / sub_bearing.folder)


# ── (l) test plan → flat ─────────────────────────────────────────────────────

def test_split_test_plan_is_flat(factory_root, mod):
    assert flat_plan("test")
    _put_plan(mod, "backend", "test", fx.test_plan(mod, over=True))
    rep = split(mod, "backend", "test", 1)
    assert rep.ok, (rep.findings, rep.verification)
    container = CFG.packages_dir(mod, "backend", "test", 1)
    ph = fx.grammar("backend", "test").phases[0]
    assert {p.name for p in container.iterdir() if p.is_dir()} == set()
    assert _md(container) == {f"{ph.sub_labels[0]}.md", f"{ph.sub_labels[1]}.md", f"{ph.key}{HEADER_SUFFIX}.md"}
    assert rep.verification["checked"] == int(ph.split_threshold["count"]) + 1 + 2


def test_split_test_plan_below_threshold_single_file(factory_root, mod):
    _put_plan(mod, "backend", "test", fx.test_plan(mod, over=False))
    rep = split(mod, "backend", "test", 1)
    ph = fx.grammar("backend", "test").phases[0]
    assert rep.ok and _md(CFG.packages_dir(mod, "backend", "test", 1)) == {f"{ph.key}.md"}


# ── blocking / strict / dry-run / fix-safe ──────────────────────────────────

def test_split_blocks_on_unknown_phase_and_writes_nothing(factory_root, mod):
    g = fx.grammar("backend", "exec")
    bogus = "NOT-" + g.phases[0].key
    _put_plan(mod, "backend", "exec", fx.marker(g.phase_kind, bogus, "START") + "x\n" + fx.marker(g.phase_kind, bogus, "END"))
    rep = split(mod, "backend", "exec", 1)
    assert rep.blocked and not rep.ok and rep.written == []
    assert any(f.rule == "phase-unknown" for f in rep.findings)
    assert _md(CFG.packages_dir(mod, "backend", "exec", 1), recursive=True) == set()


def test_split_over_threshold_advisory_then_strict_blocks(factory_root, mod):
    text, _ph = fx.over_threshold_no_sub(mod)
    _put_plan(mod, "backend", "exec", text)
    rep = split(mod, "backend", "exec", 1)
    assert rep.ok and any(f.rule == "split-threshold" and f.severity == "MINOR" for f in rep.findings)
    rep = split(mod, "backend", "exec", 1, strict=True)
    assert rep.blocked and any(f.rule == "split-threshold" and f.severity == "MAJOR" for f in rep.findings)


def test_split_dry_run_plans_but_writes_nothing(factory_root, mod):
    _put_plan(mod, "backend", "exec", fx.exec_plan(mod))
    rep = split(mod, "backend", "exec", 1, dry_run=True)
    assert rep.ok and rep.written and rep.verification == {}
    assert _md(CFG.packages_dir(mod, "backend", "exec", 1), recursive=True) == set()
    assert load_manifest(mod, 1)["status"]["split"][plan_key("backend", "exec")] is False
    rep2 = split(mod, "backend", "exec", 1, yes=False)
    assert rep2.dry_run and rep2.written == rep.written


def test_split_fix_safe_repairs_then_splits(factory_root, mod):
    g = fx.grammar("backend", "exec")
    ph = fx.threshold_phase(g)
    text = fx.exec_plan(mod).replace(f"{g.phase_kind}:{ph.key}:", f"{g.phase_kind}:{ph.key.replace('-', '_')}:")
    src = _put_plan(mod, "backend", "exec", text)
    assert split(mod, "backend", "exec", 1).blocked
    rep = split(mod, "backend", "exec", 1, fix_safe=True)
    assert rep.ok and rep.autofix.changed and src.with_name(src.name + ".orig").exists()


def test_split_missing_plan_is_an_error(factory_root, mod):
    ensure_structure(mod, 1)
    rep = split(mod, "backend", "exec", 1)
    assert not rep.ok and rep.errors and not rep.blocked


# ── idempotency / verification ──────────────────────────────────────────────

def test_rerun_is_identical_and_removes_stale_files(factory_root, mod):
    _put_plan(mod, "backend", "exec", fx.exec_plan(mod))
    container = CFG.packages_dir(mod, "backend", "exec", 1)
    split(mod, "backend", "exec", 1)
    snapshot = {f.relative_to(container): f.read_bytes() for f in container.rglob("*.md")}
    # change the plan: drop the trailing section → _SECTIONS.md must disappear on re-run
    CFG.plan_path(mod, "backend", "exec", 1).write_text(fx.exec_plan(mod, trailing=False), encoding="utf-8")
    rep = split(mod, "backend", "exec", 1)
    assert rep.ok and not (container / SECTIONS_FILE).exists()
    # restore the plan: output must be byte-identical to the first run
    CFG.plan_path(mod, "backend", "exec", 1).write_text(fx.exec_plan(mod), encoding="utf-8")
    split(mod, "backend", "exec", 1)
    assert {f.relative_to(container): f.read_bytes() for f in container.rglob("*.md")} == snapshot


def test_verify_detects_tampering(factory_root, mod):
    _put_plan(mod, "backend", "exec", fx.exec_plan(mod))
    split(mod, "backend", "exec", 1)
    assert verify(mod, "backend", "exec", 1)["ok"]
    g = fx.grammar("backend", "exec")
    ph = fx.threshold_phase(g)
    f = CFG.packages_dir(mod, "backend", "exec", 1) / ph.folder / f"{ph.key}-{ph.sub_labels[0]}.md"
    f.write_text(f.read_text(encoding="utf-8").replace("Body of", "TAMPERED"), encoding="utf-8")
    v = verify(mod, "backend", "exec", 1)
    assert not v["ok"] and v["mismatched"] and not v["missing"]
    f.unlink()
    v = verify(mod, "backend", "exec", 1)
    assert not v["ok"] and v["missing"]


def test_split_version_none_uses_current_version(factory_root, mod):
    ensure_structure(mod, 1)
    _put_plan(mod, "backend", "exec", fx.exec_plan(mod), version=2)
    rep = split(mod, "backend", "exec")
    assert rep.version == 2 and rep.ok
    assert CFG.packages_dir(mod, "backend", "exec", 2).is_relative_to(CFG.version_root(mod, 2))
    assert _md(CFG.packages_dir(mod, "backend", "exec", 1), recursive=True) == set()
