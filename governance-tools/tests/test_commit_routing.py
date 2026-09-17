"""`_commit` writes into the repository that OWNS each path.

Governance artifacts live in the shared repo (`paths.external`), which reaches
the factory as a submodule. Two ways that goes wrong silently, both guarded here:

  * `git add` run in the factory root over a submodule path stages the POINTER,
    not the content — it commits cleanly and saves nothing.
  * `git commit` without a pathspec takes the whole index, so anything staged
    out of band rides along under this commit's message.
"""
from __future__ import annotations

import subprocess

import pytest

from config import CFG


def _git(*a, cwd):
    return subprocess.run(["git", *a], cwd=str(cwd), check=True, capture_output=True, text=True)


def _init(path):
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "-q", cwd=path)
    (path / ".gitkeep").write_text("", encoding="utf-8")
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=path)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init", cwd=path)
    return path


def _files_in_head(repo):
    return _git("show", "--name-only", "--format=", "HEAD", cwd=repo).stdout.split()


@pytest.fixture
def two_repos(factory_root, monkeypatch):
    """A factory checkout with the shared repo nested inside it, as in the real
    layout — the arrangement `dispatch.ingest()` depends on."""
    import gov
    _init(factory_root)
    shared = _init(factory_root / CFG.repos[CFG.external["repo"]]["checkout_default"])
    monkeypatch.setenv(CFG.repos[CFG.external["repo"]]["checkout_env"], str(shared))
    CFG.reload()
    return gov, factory_root, shared


def test_an_artifact_is_committed_in_the_repo_that_owns_it(two_repos, mod):
    gov, factory, shared = two_repos
    art = CFG.state_dir(mod)
    art.mkdir(parents=True, exist_ok=True)
    (art / "note.md").write_text("content\n", encoding="utf-8")

    sha = gov._commit([art / "note.md"], "artifact")
    assert sha, "nothing was committed"

    # the CONTENT landed in the shared repo, not a pointer in the factory
    assert "erp/modules" in " ".join(_files_in_head(shared)) or _files_in_head(shared)
    assert any("note.md" in f for f in _files_in_head(shared))
    # and the factory recorded WHICH shared commit it was
    assert _files_in_head(factory) == [shared.name]


def test_a_factory_owned_path_stays_in_the_factory(two_repos):
    gov, factory, shared = two_repos
    p = CFG.dir("engines") / "x.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("engine\n", encoding="utf-8")

    gov._commit([p], "engine")
    assert any("x.md" in f for f in _files_in_head(factory))
    assert _git("log", "--oneline", cwd=shared).stdout.count("\n") == 1   # untouched


def test_an_unrelated_staged_change_does_not_ride_along(two_repos, mod):
    gov, factory, shared = two_repos
    noise = shared / "noise.md"
    noise.write_text("staged out of band\n", encoding="utf-8")
    _git("add", "noise.md", cwd=shared)

    art = CFG.state_dir(mod)
    art.mkdir(parents=True, exist_ok=True)
    (art / "note.md").write_text("content\n", encoding="utf-8")
    gov._commit([art / "note.md"], "artifact only")

    files = _files_in_head(shared)
    assert any("note.md" in f for f in files)
    assert "noise.md" not in files, "an unrelated staged file was swept into the commit"


def test_owning_checkout_prefers_the_innermost_repo(two_repos, mod):
    """The shared repo sits INSIDE the factory root, so both contain the path.
    The submodule must win, or every artifact commit goes to the wrong repo."""
    gov, factory, shared = two_repos
    assert gov._owning_checkout(CFG.module_root(mod)) == shared
    assert gov._owning_checkout(CFG.dir("engines")) == factory
    assert gov._owning_checkout(factory / "factory.yaml") == factory
