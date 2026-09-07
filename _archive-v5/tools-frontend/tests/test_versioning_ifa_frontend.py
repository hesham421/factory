"""
Frontend IFA / new-version coverage (previously ZERO tests touched versioning).

The frontend owns its module tree but NOT the registry (it reads backend's
published shared/modules-registry.json read-only, for identity only). So its
version model is FILESYSTEM-DERIVED — the current version is the highest local
vN folder, and `agent1 --new-version` makes the next one alongside a frozen
prior. This suite locks that contract end to end:

  agent1 --new-version → creates modules/[MOD]/v2/ (v1 untouched, no registry write)
  config path helpers  → default to the current local version, so agent2/agent3
                         archive/split the delta into v2 with no flags of their own
  v1                    → stays byte-identical (frozen) throughout
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import config
import agent1_create_structure as a1
import agent2_archive as a2


@pytest.fixture
def fe_repo(tmp_path, monkeypatch):
    """Point the frontend toolset's repo root + backend registry at tmp, and
    register one module so validate_module accepts it."""
    repo = tmp_path / "frontend" / "governance"
    (repo / "modules").mkdir(parents=True, exist_ok=True)
    shared = tmp_path / "shared" / "modules-registry.json"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text('{"modules": {"ORG": {"code": "ORG"}}}', encoding="utf-8")

    monkeypatch.setattr(config, "REPO_BASE_PATH", repo)
    monkeypatch.setattr(config, "BACKEND_REGISTRY_FILE", shared)
    monkeypatch.setattr(config, "API_DOCS_ROOT", repo / "modules")
    return {"repo": repo, "shared": shared}


def _run_a1(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    a1.main()


# ── filesystem-derived version resolution ───────────────────────────────────

def test_fresh_module_is_v1_no_suffix(fe_repo, monkeypatch):
    _run_a1(monkeypatch, ["agent1", "--module", "ORG"])
    assert config.get_current_version("ORG") == 1
    assert config.get_module_path("ORG").name == "ORG"          # no suffix
    assert config.get_stage_path("ORG", "P3_2").parent.name == "ORG"
    assert config.get_next_version("ORG") == 2


def test_new_version_creates_v2_alongside_frozen_v1(fe_repo, monkeypatch):
    _run_a1(monkeypatch, ["agent1", "--module", "ORG"])
    v1_root = config.get_module_path("ORG", 1)
    assert v1_root.exists() and v1_root.name == "ORG"

    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--new-version"])
    # current now follows the highest local folder → v2, resolved with no flags.
    assert config.get_current_version("ORG") == 2
    assert config.get_module_versions("ORG") == [1, 2]
    v2_root = config.get_module_path("ORG")
    assert v2_root.name == "v2" and v2_root.exists()
    # v1 tree still present and distinct — v2 is created ALONGSIDE, not over.
    assert v1_root.exists() and v1_root != v2_root
    # every helper (no explicit version) now resolves to v2, not v1.
    assert config.get_stage_path("ORG", "P3_2").parent.name == "v2"
    assert config.get_packages_path("ORG", "frontend-execution").parent.parent.name == "v2"
    # explicit version=1 still addresses the frozen v1 tree.
    assert config.get_stage_path("ORG", "P3_2", 1).parent.name == "ORG"


def test_frontend_never_writes_backend_registry(fe_repo, monkeypatch):
    before = fe_repo["shared"].read_text(encoding="utf-8")
    _run_a1(monkeypatch, ["agent1", "--module", "ORG"])
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--new-version"])
    # The frontend owns its folders, not the registry — the shared registry
    # backend publishes must be byte-identical after any frontend versioning.
    assert fe_repo["shared"].read_text(encoding="utf-8") == before


# ── the core end-to-end: agent2 archives the delta into v2, v1 frozen ───────

def test_agent2_archives_delta_into_v2_leaving_v1_frozen(fe_repo, monkeypatch):
    # 1) v1 built + a v1 frontend artifact archived.
    _run_a1(monkeypatch, ["agent1", "--module", "ORG"])
    src = fe_repo["repo"].parent.parent / "src_v1"
    src.mkdir()
    (src / config.plan_label("exec","ORG")).write_text("V1 FE plan — original", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["agent2", "--module", "ORG", "--source", str(src)])
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    a2.main()

    v1_plan = config.plan_file(config.get_module_path("ORG",1), "ORG", "exec")
    assert v1_plan.exists(), "v1 archive should land under modules/ORG/"
    v1_bytes = v1_plan.read_bytes()

    # 2) new frontend version, then archive a DELTA artifact.
    _run_a1(monkeypatch, ["agent1", "--module", "ORG", "--new-version"])
    src2 = fe_repo["repo"].parent.parent / "src_v2"
    src2.mkdir()
    (src2 / config.plan_label("exec","ORG")).write_text("V2 FE plan — delta feature", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["agent2", "--module", "ORG", "--source", str(src2)])
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    a2.main()

    # delta lands in v2 (agent2 has no version flag — it followed current) …
    v2_plan = config.plan_file(config.get_module_path("ORG",2), "ORG", "exec")
    assert v2_plan.exists(), "delta archive must land under modules/ORG/v2/"
    assert "delta feature" in v2_plan.read_text(encoding="utf-8")

    # … and v1 is byte-identical (frozen), never overwritten by the delta.
    assert v1_plan.read_bytes() == v1_bytes
    assert v1_plan.read_text(encoding="utf-8").startswith("V1 FE")
    assert v2_plan.resolve() != v1_plan.resolve()


# ── AMEND-PIPELINE-V5 §5: no literal plan filename in agent3 ─────────────────

def test_no_literal_plan_filename_in_fe_agent3_source():
    src = (Path(__file__).parent / "agent3_splitter.py").read_text(encoding="utf-8")
    body = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith("#") and '"""' not in l)
    assert '"frontend-execution-plan.md"' not in body
    assert '"frontend-test-plan.md"' not in body
    # and the resolvers produce module-qualified names
    assert config.plan_label("exec", "org") == "frontend-execution-plan-org.md"
    assert config.plan_label("test", "org") == "frontend-test-plan-org.md"
