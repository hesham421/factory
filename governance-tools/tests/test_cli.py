"""Standalone CLIs (`python -m toolkit.<module>`) — non-interactive, exit codes."""
from __future__ import annotations

import os
import subprocess
import sys

from config import CFG
from toolkit import ensure_structure
from toolkit.common import module_stages

import planfx as fx
from conftest import TOOLS_DIR


def _run(*args, root):
    env = dict(os.environ, GOV_FACTORY_ROOT=str(root))
    env.pop("GOV_PROFILE", None)
    return subprocess.run([sys.executable, "-m", *args], cwd=str(TOOLS_DIR), env=env,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)


def test_cli_validate_only_exit_codes(factory_root, tmp_path, mod):
    good = tmp_path / "good.md"
    good.write_text(fx.exec_plan(mod), encoding="utf-8")
    r = _run("toolkit.splitter", "--track", "backend", "--plan", "exec", "--validate-only", str(good), root=factory_root)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 blocking" in r.stdout
    bad, _ph = fx.over_threshold_no_sub(mod)
    p = tmp_path / "bad.md"
    p.write_text(bad, encoding="utf-8")
    r = _run("toolkit.splitter", "--track", "backend", "--plan", "exec", "--validate-only", str(p), root=factory_root)
    assert r.returncode == 0 and "split-threshold" in r.stdout
    r = _run("toolkit.splitter", "--track", "backend", "--plan", "exec", "--strict", "--validate-only", str(p), root=factory_root)
    assert r.returncode == 1


def test_cli_structure_archive_split_end_to_end(factory_root, tmp_path, mod):
    r = _run("toolkit.structure", "--module", mod, "--version", "1", "--dry-run", root=factory_root)
    assert r.returncode == 0 and "DRY RUN" in r.stdout and not CFG.module_root(mod).exists()
    r = _run("toolkit.structure", "--module", mod, "--version", "1", root=factory_root)
    assert r.returncode == 0 and CFG.module_root(mod).is_dir()
    src = tmp_path / "gen"
    src.mkdir()
    plan_artifact = next(a for s in module_stages() for a in s.produces if a.plan == "exec" and a.track == "backend")
    (src / plan_artifact.filename(mod)).write_text(fx.exec_plan(mod), encoding="utf-8")
    r = _run("toolkit.archive", "--module", mod, "--source", str(src), "--version", "1", root=factory_root)
    assert r.returncode == 0 and "copied" in r.stdout and "WARN" in r.stdout      # other artifacts missing → warnings
    r = _run("toolkit.archive", "--module", mod, "--source", str(src), "--version", "1", root=factory_root)
    assert r.returncode == 0 and "kept" in r.stdout
    r = _run("toolkit.splitter", "--module", mod, "--track", "backend", "--plan", "exec", "--version", "1", "--dry-run", root=factory_root)
    assert r.returncode == 0 and "plan " in r.stdout and "dry run" in r.stdout
    r = _run("toolkit.splitter", "--module", mod, "--track", "backend", "--plan", "exec", "--version", "1", root=factory_root)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ok=True" in r.stdout
    assert (CFG.packages_dir(mod, "backend", "exec", 1) / "verification.json").exists()


def test_cli_split_missing_plan_fails_cleanly(factory_root, mod):
    ensure_structure(mod, 1)
    r = _run("toolkit.splitter", "--module", mod, "--track", "backend", "--plan", "test", "--version", "1", root=factory_root)
    assert r.returncode == 1 and "not found" in r.stdout
