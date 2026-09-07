"""
Shared pytest configuration for the governance-tools suite.

- Ensures the governance-tools directory (parent of tests/) is importable so
  `import config`, `import marker_parser`, etc. resolve the same way the tools
  do at runtime.
- `isolated_registry` redirects the modules registry (and its published shared
  copy) to a tmp path so tests never touch the real backend/governance tree.
"""
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))


@pytest.fixture
def isolated_registry(tmp_path, monkeypatch):
    """Redirect the registry AND the repo base into tmp, so tools that create
    folders / write manifests (e.g. a live agent1 run) never touch the real
    backend/governance tree."""
    import config
    repo = tmp_path / "repo"
    (repo / "modules").mkdir(parents=True, exist_ok=True)
    reg = repo / "modules-registry.json"
    shared = tmp_path / "shared" / "modules-registry.json"
    monkeypatch.setattr(config, "REPO_BASE_PATH", repo)
    monkeypatch.setattr(config, "MODULES_REGISTRY_FILE", reg)
    monkeypatch.setattr(config, "SHARED_REGISTRY_FILE", shared)
    return {"registry": reg, "shared": shared, "repo": repo}
