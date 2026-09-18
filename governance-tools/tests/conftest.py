"""
Shared pytest configuration for the governance-tools suite.

Every test runs against an ISOLATED tool root (a tmp copy of factory.yaml + the
profile schema) AND an isolated PROJECT repo: a tmp copy of the tests' own
fixture project (`fixtures/project/` — project.yaml + a sample profile),
git-initialised, with `GOV_PROJECT_CHECKOUT` pointed at it and `CFG.reload()`ed.
No test depends on a committed project; the tool tree carries none. Vocabulary
(module code, phase keys, thresholds, package names) is read from the fixture
profile / factory.yaml — nothing domain-specific is pinned by the tests.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent
REAL_ROOT = TOOLS_DIR.parent
FIXTURE_PROJECT = Path(__file__).resolve().parent / "fixtures" / "project"
for p in (str(TOOLS_DIR), str(Path(__file__).resolve().parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

from config import CFG  # noqa: E402


def git_init(path: Path) -> Path:
    """A repo with one commit — the shape every content root has."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=str(path), check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A"], cwd=str(path), check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init"],
                   cwd=str(path), check=True)
    return path


def make_project(dest: Path) -> Path:
    """A fresh project repo from the fixture — copied, git-initialised."""
    shutil.copytree(FIXTURE_PROJECT, dest)
    return git_init(dest)


@pytest.fixture
def factory_root(tmp_path, monkeypatch):
    """Isolated tool root (factory.yaml + the schema) driving an isolated project repo."""
    root = tmp_path / "factory"
    root.mkdir()
    shutil.copy2(REAL_ROOT / "factory.yaml", root / "factory.yaml")
    (root / "profiles").mkdir()
    shutil.copy2(REAL_ROOT / "profiles" / "_schema.yaml", root / "profiles" / "_schema.yaml")
    project = make_project(tmp_path / "project")
    monkeypatch.setenv("GOV_FACTORY_ROOT", str(root))
    monkeypatch.setenv("GOV_PROJECT_CHECKOUT", str(project))
    monkeypatch.delenv("GOV_PROFILE", raising=False)
    CFG.reload()
    yield root
    monkeypatch.undo()
    CFG.reload()


@pytest.fixture
def project_root(factory_root) -> Path:
    """The temp project repo the active CFG drives."""
    return CFG.project_checkout()


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
