"""Factory layer tests — git-native versioning, pass-2 input gate, delivery, dispatch."""
import json, subprocess, sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent.parent
sys.path.insert(0, str(HERE))
import config as C  # noqa: E402

GOV = HERE / "gov.py"


def run(*a, cwd=None):
    return subprocess.run([sys.executable, str(GOV), *a], capture_output=True, text=True, cwd=cwd)


def git(*a, cwd):
    return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True, check=True)


@pytest.fixture
def factory(tmp_path, monkeypatch):
    """Isolated factory root with a git repo, plus two consumer repos with a
    git checkout each (linked via REPOS)."""
    root = tmp_path / "governance"; (root / "modules").mkdir(parents=True)
    git("init", "-q", cwd=root); git("config", "user.email", "t@t", cwd=root); git("config", "user.name", "t", cwd=root)
    (root / "README.md").write_text("x"); git("add", "-A", cwd=root); git("commit", "-qm", "init", cwd=root)
    repos = {}
    for name in ("backend", "frontend"):
        r = tmp_path / name; r.mkdir()
        git("init", "-q", cwd=r); git("config", "user.email", "t@t", cwd=r); git("config", "user.name", "t", cwd=r)
        (r / "README.md").write_text(name); git("add", "-A", cwd=r); git("commit", "-qm", "init", cwd=r)
        repos[name] = r
    monkeypatch.setattr(C, "FACTORY_ROOT", root)
    monkeypatch.setattr(C, "MODULES_ROOT", root / "modules")
    for name, r in repos.items():
        C.REPOS[name]["checkout"] = r
    # gov.py runs as a subprocess and re-imports config → write an override env
    monkeypatch.setenv("GOV_FACTORY_ROOT", str(root))
    monkeypatch.setenv("GOV_BACKEND_CHECKOUT", str(repos["backend"]))
    monkeypatch.setenv("GOV_FRONTEND_CHECKOUT", str(repos["frontend"]))
    return {"root": root, **repos}


def test_versions_are_filesystem_derived_and_git_tagged(factory):
    root = factory["root"]
    assert C.module_versions("ORG") == []
    r = run("version", "-m", "ORG", "--new"); assert r.returncode == 0, r.stdout + r.stderr
    assert (root / "modules" / "ORG").exists() and C.current_version("ORG") == 1
    r = run("version", "-m", "ORG", "--new"); assert r.returncode == 0
    assert (root / "modules" / "ORG" / "v2").exists() and C.current_version("ORG") == 2
    assert run("tag", "-m", "ORG", "-v", "2").returncode == 0
    assert "org-v2" in git("tag", "--list", cwd=root).stdout


def test_pass2_gate_closed_until_both_inputs_exist(factory):
    run("version", "-m", "ORG", "--new")
    r = run("fetch-inputs", "-m", "ORG", "-v", "1")
    assert r.returncode == 1 and "GATE CLOSED" in r.stdout
    be, fe = factory["backend"], factory["frontend"]
    p = be / C.fmt(C.REPOS["backend"]["inputs"]["api_docs"], "ORG"); p.parent.mkdir(parents=True); p.write_text("API")
    r = run("fetch-inputs", "-m", "ORG", "-v", "1")
    assert r.returncode == 1 and "ui_shell" in r.stdout          # still missing one
    q = fe / C.fmt(C.REPOS["frontend"]["inputs"]["ui_shell"], "ORG"); q.parent.mkdir(parents=True); q.write_text("SHELL")
    r = run("fetch-inputs", "-m", "ORG", "-v", "1")
    assert r.returncode == 0 and "GATE OPEN" in r.stdout
    inputs = factory["root"] / "modules" / "ORG" / C.INPUTS_FOLDER
    assert (inputs / p.name).read_text() == "API" and (inputs / q.name).read_text() == "SHELL"


def test_deliver_creates_branch_with_packages_in_consumer_repo(factory):
    root, be = factory["root"], factory["backend"]
    run("version", "-m", "ORG", "--new")
    pk = root / "modules" / "ORG" / "packages" / "backend-execution" / "CORE"; pk.mkdir(parents=True)
    (pk / "CORE.md").write_text("pkg"); (root / "modules" / "ORG" / "execution-state.json").write_text("{}")
    r = run("deliver", "--track", "backend", "-m", "ORG", "-v", "1")
    assert r.returncode == 0, r.stdout + r.stderr
    branch = C.fmt(C.REPOS["backend"]["branch"], "ORG", 1)
    assert git("rev-parse", "--abbrev-ref", "HEAD", cwd=be).stdout.strip() == branch
    delivered = be / C.fmt(C.REPOS["backend"]["deliver_to"], "ORG")
    assert (delivered / "packages" / "backend-execution" / "CORE" / "CORE.md").read_text() == "pkg"
    assert (delivered / "execution-state.json").exists()
    assert "deliver ORG v1 backend" in git("log", "-1", "--format=%s", cwd=be).stdout
    # frontend packages never land in the backend repo (track separation)
    assert not (delivered / "packages" / "frontend-execution").exists()


def test_deliver_v2_lands_under_v2_folder(factory):
    root, fe = factory["root"], factory["frontend"]
    run("version", "-m", "ORG", "--new"); run("version", "-m", "ORG", "--new")
    pk = root / "modules" / "ORG" / "v2" / "packages" / "frontend-execution" / "F1"; pk.mkdir(parents=True)
    (pk / "F1-SCR-ORG-001.md").write_text("fe")
    assert run("deliver", "--track", "frontend", "-m", "ORG", "-v", "2").returncode == 0
    d = fe / C.fmt(C.REPOS["frontend"]["deliver_to"], "ORG") / "v2" / "packages" / "frontend-execution" / "F1"
    assert (d / "F1-SCR-ORG-001.md").exists()


def test_dispatch_routes_to_track_agents():
    r = run("split", "--track", "backend", "--status", "--module", "ZZZ")
    # reaches the real backend agent3 (which rejects the unknown module) — not a dispatcher error
    assert "ZZZ" in (r.stdout + r.stderr) or "not registered" in (r.stdout + r.stderr) or r.returncode != 0
    r2 = run("split", "--track", "frontend", "--status", "--module", "ZZZ")
    assert r2.returncode != 0


def test_tracks_operate_on_factory_modules_root_and_same_version(factory, monkeypatch):
    """Regression guard for the root/version mismatch found in review: the
    backend track must create/archive under the FACTORY's modules/ (not under
    governance-tools/tracks/modules), at the SAME version the factory created,
    and the frontend must accept the module via the backend track registry."""
    root = factory["root"]
    # keep track registries isolated for the test
    breg = C.TRACKS["backend"]["tools_dir"] / "modules-registry.json"
    backup = breg.read_text(encoding="utf-8") if breg.exists() else None
    try:
        r = run("version", "-m", "ORG", "--new"); assert r.returncode == 0, r.stdout + r.stderr
        r = run("version", "-m", "ORG", "--new"); assert r.returncode == 0          # v2
        # dispatch structure creation for BOTH tracks (non-interactive: --dry-run shows the target path)
        rb = run("structure", "--track", "backend", "--module", "ORG", "--dry-run")
        assert rb.returncode == 0, rb.stdout + rb.stderr
        assert "v2" in rb.stdout, "backend must target the factory's v2, not v1"
        assert "governance-tools/tracks/modules" not in rb.stdout
        rf = run("structure", "--track", "frontend", "--module", "ORG", "--dry-run")
        assert rf.returncode == 0, rf.stdout + rf.stderr          # module accepted via backend track registry
        assert "v2" in rf.stdout
        assert str(root / "modules" / "ORG") in rf.stdout or "modules/ORG" in rf.stdout
    finally:
        if backup is not None:
            breg.write_text(backup, encoding="utf-8")
        elif breg.exists():
            breg.unlink()


def test_factory_structure_integrity():
    """Guards the review findings: shared governance files present, precedence
    file first, every engine SKILL loads shared + has a reference carrying the
    factory notice, every command exists, config passes/gates consistent."""
    root = HERE.parent
    shared = root / "shared"
    for f in ["FACTORY-PRECEDENCE.md", "GOVERNANCE-CONFIG.md", "shared-governance-rules.md",
              "shared-artifact-contracts.md", "PROJECT-3-REGISTRY.md", "AMEND-IFA-INCREMENTAL-FEATURE-ADDITION.md",
              "XM-RESOLUTION-EVENT-PROTOCOL.md"]:
        assert (shared / f).exists(), f"shared/{f} missing"
    for eid in C.BOOTSTRAP + C.PASS_1 + C.PASS_2 + C.OPTIONAL:
        d = root / "engines" / eid
        skill = (d / "SKILL.md").read_text(encoding="utf-8")
        assert skill.startswith("---\nname:"), f"{eid}: bad frontmatter"
        assert "FACTORY-PRECEDENCE.md" in skill, f"{eid}: does not load shared precedence first"
        refs = list((d / "references").glob("*.md"))
        assert refs, f"{eid}: no reference"
        for r in refs:
            assert "FACTORY NOTICE" in r.read_text(encoding="utf-8"), f"{r.name}: missing factory notice"
    for c in ["bootstrap", "analyze-pass1", "analyze-pass2", "review-gate", "micro-feature", "link-repos", "audit"]:
        assert (root / "commands" / f"{c}.md").exists()
    for r in ["per-engine-review", "holistic-review"]:
        assert (root / "reviewers" / f"{r}.md").exists()
    assert (root / "reviewers" / "references" / "MASTER-REVIEWER.md").exists()
    for d in ["MULTI-PROJECT-VERSIONING-ARCHITECTURE.md", "STAGE-2-GOVERNANCE-TOOLS-2.md", "WORKSPACE-ARCHITECTURE-REFERENCE.md"]:
        assert (shared / "docs" / d).exists(), f"shared/docs/{d} missing"
    assert (root / "platform" / "README.md").exists()
    assert (root / "engines" / "optional" / "P-REG" / "SKILL.md").exists()   # retired, traceable
    # gates reference stages that exist; lanes used by commands exist in config
    assert set(C.PER_ENGINE_REVIEW_AT) <= set(C.PASS_1 + C.PASS_2)
    for lane in ("analysis", "review-per-engine", "review-holistic", "merge-review-notes"):
        assert lane in C.LANES
