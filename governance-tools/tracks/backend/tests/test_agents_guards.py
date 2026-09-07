"""Guard-rail tests for Agent 1 (dry-run registry) and Agent 2 (--force)."""
import sys
from pathlib import Path

import pytest

import config
import agent1_create_structure as a1
import agent2_archive as a2


# ── FINDING-22a — agent1 --dry-run must not mutate the registry ────────────

def test_dry_run_autoregister_writes_nothing(isolated_registry, monkeypatch, capsys):
    assert not isolated_registry["registry"].exists()
    monkeypatch.setattr(sys, "argv",
                        ["agent1", "--module", "NEWMOD", "--auto-register",
                         "--description", "x", "--dry-run"])
    a1.main()
    # The whole point of the fix: a dry run leaves the registry untouched.
    assert not isolated_registry["registry"].exists(), \
        "dry-run + auto-register must NOT write modules-registry.json"
    assert not isolated_registry["shared"].exists()
    out = capsys.readouterr().out
    assert "DRY RUN" in out


def test_live_autoregister_does_write(isolated_registry, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        ["agent1", "--module", "NEWMOD", "--auto-register", "--description", "x"])
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    a1.main()
    assert isolated_registry["registry"].exists(), \
        "a LIVE auto-register run SHOULD write the registry"


# ── M4 — agent2 --force actually controls overwrite ───────────────────────

def _op(src: Path, dst: Path):
    return {"found": src.exists(), "src": src, "dst": dst,
            "exists": dst.exists(), "stage": "P1", "filename": dst.name, "shared": False}


def test_existing_file_kept_without_force(tmp_path):
    src = tmp_path / "srs.md"; src.write_text("NEW", encoding="utf-8")
    dst = tmp_path / "out" / "srs.md"; dst.parent.mkdir(); dst.write_text("OLD", encoding="utf-8")
    a2.execute_archive("TST", [_op(src, dst)], dry_run=False, force=False)
    assert dst.read_text(encoding="utf-8") == "OLD", "must not overwrite without --force"


def test_existing_file_overwritten_with_force(tmp_path):
    src = tmp_path / "srs.md"; src.write_text("NEW", encoding="utf-8")
    dst = tmp_path / "out" / "srs.md"; dst.parent.mkdir(); dst.write_text("OLD", encoding="utf-8")
    a2.execute_archive("TST", [_op(src, dst)], dry_run=False, force=True)
    assert dst.read_text(encoding="utf-8") == "NEW", "--force must overwrite"


def test_new_file_always_copied(tmp_path):
    src = tmp_path / "srs.md"; src.write_text("NEW", encoding="utf-8")
    dst = tmp_path / "out" / "srs.md"; dst.parent.mkdir()
    a2.execute_archive("TST", [_op(src, dst)], dry_run=False, force=False)
    assert dst.read_text(encoding="utf-8") == "NEW"
