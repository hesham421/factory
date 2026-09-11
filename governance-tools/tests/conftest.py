"""
Shared pytest configuration for the governance-tools suite.

Every test runs against an ISOLATED factory root: a tmp copy of factory.yaml +
profiles/ with `GOV_FACTORY_ROOT` pointed at it and `CFG.reload()`ed, so the
toolkit never dirties the real repo. Vocabulary (module code, phase keys,
thresholds, package names) is read from the profile / factory.yaml — nothing
domain-specific is pinned by the tests.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent
REAL_ROOT = TOOLS_DIR.parent
for p in (str(TOOLS_DIR), str(Path(__file__).resolve().parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

from config import CFG  # noqa: E402


@pytest.fixture
def factory_root(tmp_path, monkeypatch):
    """Isolated factory root (factory.yaml + profiles/), active in CFG."""
    root = tmp_path / "factory"
    root.mkdir()
    shutil.copy2(REAL_ROOT / "factory.yaml", root / "factory.yaml")
    shutil.copytree(REAL_ROOT / "profiles", root / "profiles")
    monkeypatch.setenv("GOV_FACTORY_ROOT", str(root))
    monkeypatch.delenv("GOV_PROFILE", raising=False)
    CFG.reload()
    yield root
    monkeypatch.undo()
    CFG.reload()


@pytest.fixture
def cfg(factory_root):
    """The live FactoryConfig behind CFG (for lint helpers that take one)."""
    return CFG.reload()


@pytest.fixture
def mod(factory_root) -> str:
    """The first module code the active profile declares."""
    return next(iter(CFG.profile.vocabulary["module_prefixes"]))


@pytest.fixture
def endpoint_ctx():
    """A minimal analyze Ctx over two in-memory texts.

    `endpoint-agrees` reads exactly three things — the artifact's text, the
    source's text and the module code — so the fixture supplies those and
    nothing else: a check that needed more of a Ctx than it reads would be
    reaching past its own inputs.
    """
    class _Ctx:
        def __init__(self, artifact: str, source: str | None, mod: str):
            self._t = {"plan": artifact, "docs": source}
            self.mod = mod
            self._examined = 0

        def saw(self, n):
            self._examined += n

        def text(self, name):
            return self._t.get(name)

    def make(artifact_text: str, source_text: str | None, mod: str = "SEC"):
        return _Ctx(artifact_text, source_text, mod)

    return make
