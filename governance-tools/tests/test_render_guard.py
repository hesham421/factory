"""`gov.py render` owns `paths.commands` — but only what it generated.

A stale GENERATED command (its entry left `factory.yaml → commands`) is the
renderer's own output and is removed. A file WITHOUT the generated marker was
written by a person; a render that deleted it would erase work it never
produced, silently, under a command that claims to regenerate. Such a file is
kept, reported, and refused by lint — so the tree still converges on
`factory.yaml → commands`, by a hand and not by a sweep.
"""
from __future__ import annotations

import shutil

from config import CFG
from conftest import REAL_ROOT


def _renderable(factory_root):
    shutil.copytree(REAL_ROOT / "governance-tools" / "templates", factory_root / "governance-tools" / "templates")
    for d in ("shared", "engines", "standalone", "reviewers"):
        shutil.copytree(REAL_ROOT / d, factory_root / d)
    return CFG.reload()


def test_render_removes_a_stale_generated_command_and_keeps_an_unmarked_file(factory_root):
    import render
    cfg = _renderable(factory_root)
    cmds = cfg.dir("commands")
    cmds.mkdir(parents=True, exist_ok=True)
    marker = cfg.data["lint"]["generated_marker"]
    stale = cmds / "retired-command.md"
    stale.write_text(marker + "\n# /retired-command — gone from factory.yaml\n", encoding="utf-8")
    handwritten = cmds / "my-own-note.md"
    handwritten.write_text("# a file someone wrote by hand\n", encoding="utf-8")

    changed = render.render_all(cfg, write=True)

    assert not stale.exists(), "a stale generated command is the renderer's own output and goes"
    assert stale in changed
    assert handwritten.exists() and handwritten.read_text(encoding="utf-8").startswith("# a file someone wrote")
    assert handwritten not in changed
    assert render.unmanaged_commands(cfg) == [handwritten]
    # and the tree now equals factory.yaml → commands, plus the one reported file
    expected = {f"{c['id']}.md" for c in cfg.commands}
    assert {p.name for p in cmds.glob("*.md")} == expected | {handwritten.name}


def test_lint_refuses_a_command_file_that_factory_yaml_does_not_declare(factory_root):
    import lint
    cfg = _renderable(factory_root)
    cmds = cfg.dir("commands")
    cmds.mkdir(parents=True, exist_ok=True)
    import render
    render.render_all(cfg, write=True)
    assert not [f for f in lint.scan_structure(cfg) if f.path.startswith(cfg.paths["commands"])]

    stray = cmds / "not-a-command.md"
    stray.write_text("# stray\n", encoding="utf-8")
    found = [f for f in lint.scan_structure(cfg) if f.path.startswith(cfg.paths["commands"])]
    assert len(found) == 1 and "not-a-command.md" in found[0].path and "never deletes" in found[0].message
    # a second render still does not remove it — lint is the enforcement, not deletion
    render.render_all(cfg, write=True)
    assert stray.exists()
