"""`_commit` writes into the repository that OWNS each path.

Governance artifacts live in the project repo (`paths.external`), a checkout
of its own beside the tool. Two ways that goes wrong silently, both guarded
here:

  * `git add` run in the wrong root stages nothing, or a pointer — it commits
    cleanly and saves nothing.
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
    """The tool checkout as a repo of its own, beside the project repo the
    conftest already initialised — the real layout."""
    import gov
    _init(factory_root)
    shared = CFG.project_checkout()
    return gov, factory_root, shared


def test_an_artifact_is_committed_in_the_repo_that_owns_it(two_repos, mod):
    gov, factory, shared = two_repos
    art = CFG.state_dir(mod)
    art.mkdir(parents=True, exist_ok=True)
    (art / "note.md").write_text("content\n", encoding="utf-8")
    before = _git("rev-parse", "HEAD", cwd=factory).stdout

    sha = gov._commit([art / "note.md"], "artifact")
    assert sha, "nothing was committed"

    # the CONTENT landed in the project repo; the tool repo did not move
    assert any("note.md" in f for f in _files_in_head(shared))
    assert CFG.paths["modules"] in " ".join(_files_in_head(shared))
    assert _git("rev-parse", "HEAD", cwd=factory).stdout == before


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
    """Every declared root is a candidate; the innermost containing the path
    wins, so a nested checkout beats the parent that contains it."""
    gov, factory, shared = two_repos
    assert gov._owning_checkout(CFG.module_root(mod)) == shared
    assert gov._owning_checkout(CFG.dir("engines")) == factory
    assert gov._owning_checkout(factory / "factory.yaml") == factory


def test_a_detached_project_checkout_refuses_the_write(two_repos, mod):
    """`git submodule update` leaves a checkout on a commit, not a branch. A
    commit made there is referenced by nothing and the next update walks away
    from it, while the push that should publish it succeeds publishing nothing.
    The failure is entirely silent, so this refuses rather than warns (F-28)."""
    gov, factory, shared = two_repos
    art = CFG.state_dir(mod)
    art.mkdir(parents=True, exist_ok=True)
    (art / "note.md").write_text("content\n", encoding="utf-8")

    head = _git("rev-parse", "HEAD", cwd=shared).stdout.strip()
    _git("checkout", "-q", "--detach", head, cwd=shared)
    with pytest.raises(SystemExit) as e:
        gov._commit([art / "note.md"], "artifact")
    assert "detached HEAD" in str(e.value) and "checkout" in str(e.value)

    # on a branch it goes through — the guard is about HEAD, not about writing
    _git("checkout", "-q", "-B", "main", cwd=shared)
    assert gov._commit([art / "note.md"], "artifact")


def test_the_factory_itself_is_never_blocked_by_it(two_repos):
    """The guard is for submodules. This repo's own HEAD is the operator's
    business, and refusing there would block a legitimate detached workflow."""
    gov, factory, shared = two_repos
    p = CFG.dir("engines") / "x.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("engine\n", encoding="utf-8")
    head = _git("rev-parse", "HEAD", cwd=factory).stdout.strip()
    _git("checkout", "-q", "--detach", head, cwd=factory)
    assert gov._commit([p], "engine")


# ── where a response may write (dispatch.ingest) ─────────────────────────────

def test_ingest_resolves_a_content_path_against_an_external_checkout(factory_root, tmp_path, monkeypatch, mod):
    """The content root does not have to nest inside this repo. Pointed anywhere
    else, a relative block path that names the content root's own top-level
    folder lands there, and an absolute path inside it is accepted — before,
    every such write was refused as an escape and every automated stage failed."""
    import dispatch as dp
    elsewhere = tmp_path / "elsewhere-project"
    elsewhere.mkdir()
    monkeypatch.setenv(CFG.project["checkout_env"], str(elsewhere))
    CFG.reload()
    assert dp.write_roots() == [CFG.root.resolve(), elsewhere.resolve()]

    target = CFG.state_dir(mod, 1) / "note.md"
    rel_path = target.relative_to(elsewhere).as_posix()
    resp = tmp_path / "resp.md"
    resp.write_text(f"<<<FILE: {rel_path}>>>\nrelative\n<<<END FILE>>>\n"
                    f"<<<FILE: {target.with_name('abs.md')}>>>\nabsolute\n<<<END FILE>>>\n"
                    f"<<<FILE: {CFG.paths['engines']}/x/ENGINE.md>>>\nfactory\n<<<END FILE>>>\n", encoding="utf-8")
    written = dp.ingest(resp)
    assert target in written and target.read_text(encoding="utf-8") == "relative\n"
    assert target.with_name("abs.md") in written
    assert (CFG.root / CFG.paths["engines"] / "x" / "ENGINE.md") in written


def test_ingest_still_refuses_a_path_outside_both_roots(factory_root, tmp_path):
    import dispatch as dp
    resp = tmp_path / "resp.md"
    resp.write_text(f"<<<FILE: {tmp_path / 'nowhere.md'}>>>\nx\n<<<END FILE>>>\n", encoding="utf-8")
    with pytest.raises(ValueError):
        dp.ingest(resp)
    resp.write_text("<<<FILE: ../../escape.md>>>\nx\n<<<END FILE>>>\n", encoding="utf-8")
    with pytest.raises(ValueError):
        dp.ingest(resp)


# ── what fetch-inputs records (the pin it read) ──────────────────────────────

def test_fetch_inputs_records_the_shared_commit_it_read(two_repos, mod, tmp_path):
    """The merged input said what it was folded from; nothing said at which
    commit. The sidecar and the module's execution state now carry the shared
    repo's HEAD, so a plan can prove which published surface it was built on."""
    import json
    gov, factory, shared = two_repos
    name, spec = next(iter(CFG.inputs.items()))
    host = CFG.partition_writer(spec["partition"])
    src = CFG.partition_dir(spec["partition"], mod)
    src.mkdir(parents=True, exist_ok=True)
    (src / "index.md").write_text("# published\n", encoding="utf-8")
    _git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A", cwd=shared)
    _git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "publish", cwd=shared)
    head = _git("rev-parse", "HEAD", cwd=shared).stdout.strip()

    CFG.module_root(mod).mkdir(parents=True, exist_ok=True)
    assert gov.cmd_fetch_inputs(mod, 1, pull=False) == gov.OK
    dst = CFG.inputs_dir(mod, 1) / CFG.fmt(spec["file"], mod=mod)
    meta = json.loads(dst.with_name(CFG.fmt(CFG.paths["module"]["input_meta"], file=dst.name)).read_text(encoding="utf-8"))
    assert meta["commit"] == head and meta["repo"] == host and len(meta["digest"]) == 64
    state = json.loads((CFG.module_root(mod) / CFG.paths["module"]["manifest_file"]).read_text(encoding="utf-8"))
    assert state["status"]["inputs"][name]["commit"] == head
    # a second fetch of the same surface is reported unchanged and keeps the record
    assert gov.cmd_fetch_inputs(mod, 1, pull=False) == gov.OK
    assert json.loads(dst.with_name(CFG.fmt(CFG.paths["module"]["input_meta"], file=dst.name)).read_text(encoding="utf-8"))["commit"] == head
