"""
Governance Factory — Unified Configuration
==========================================
The SINGLE source of truth for the analysis factory (repo `governance`).
Everything below is data; no tool spells a path, a repo, a branch name or a
filename on its own.

Design (approved blueprint, 2026-09-07):
  • The factory does ANALYSIS only: Domain → P0 → … → P3.1 (pass 1), then
    P3.2 (pass 2) once the repos have produced api-docs (backend) and the
    ui-shell manifest (frontend). It STOPS at delivery — never implements.
  • git-native: versions are `modules/[MOD]/vN/` folders mirrored by tags
    `[mod]-v[N]`; delivery is a branch pushed to each consumer repo; history
    is the ledger. No Drive.
  • Two tracks kept as proven toolsets under governance-tools/tracks/; the
    factory addresses them through `--track` via gov.py.
  • Consumer repos are declared HERE (REPOS) so linking backend/frontend to the
    factory is a config edit, not a code change.
"""

from pathlib import Path
import os
import re

# Roots derive from this file's location; GOV_* env vars override them (used
# by tests and by CI that runs the factory against an isolated checkout).
FACTORY_ROOT = Path(os.environ.get("GOV_FACTORY_ROOT") or Path(__file__).resolve().parent.parent)  # repo root
TOOLS_ROOT = Path(__file__).resolve().parent                    # governance-tools/
MODULES_ROOT = FACTORY_ROOT / "modules"
DOMAIN_ROOT = FACTORY_ROOT / "domain"
ENGINES_ROOT = FACTORY_ROOT / "engines"

# ─────────────────────────────────────────────
# TRACKS — each maps to a proven toolset (unchanged code, tested) and to the
# execution-plan / packages it owns. gov.py dispatches `--track` here.
# ─────────────────────────────────────────────
TRACKS = {
    "backend": {
        "tools_dir":   TOOLS_ROOT / "tracks" / "backend",
        "exec_stage":  "P3_1",
        "test_stage":  "P3_5_BE",
        "packages":    ["backend-execution", "backend-test"],
        "engine_pass": 1,                        # analysed in pass 1
    },
    "frontend": {
        "tools_dir":   TOOLS_ROOT / "tracks" / "frontend",
        "exec_stage":  "P3_2",
        "test_stage":  "P3_5_FE",
        "packages":    ["frontend-execution", "frontend-test"],
        "engine_pass": 2,                        # analysed in pass 2
    },
}

# ─────────────────────────────────────────────
# REPOS — consumer repositories linked to the factory (edit here to link).
#   url        : git remote (ssh/https). Empty → not linked yet.
#   checkout   : local working clone used for delivery + fetching inputs.
#   deliver_to : path INSIDE that repo where packages land.
#   inputs     : files the factory READS BACK from the repo for pass 2
#                (agreed paths; {mod} = lower-case module code).
#   branch     : delivery branch pattern.
# Linking later = fill url/checkout; nothing else changes.
# ─────────────────────────────────────────────
REPOS = {
    "backend": {
        "url":        "",                                     # e.g. git@github.com:org/backend.git
        "checkout":   Path(os.environ.get("GOV_BACKEND_CHECKOUT") or FACTORY_ROOT.parent / "backend"),
        "deliver_to": "governance/modules/{MOD}",              # packages + execution-state land here
        "inputs":     {"api_docs": "governance/api-docs/api-docs-{mod}.md"},
        "branch":     "gov/{mod}-v{version}-backend",
    },
    "frontend": {
        "url":        "",
        "checkout":   Path(os.environ.get("GOV_FRONTEND_CHECKOUT") or FACTORY_ROOT.parent / "frontend"),
        "deliver_to": "governance/modules/{MOD}",
        "inputs":     {"ui_shell": "governance/ui-shell/ui-shell-manifest-{mod}.md"},
        "branch":     "gov/{mod}-v{version}-frontend",
    },
}

# Pass-2 (P3.2) needs BOTH of these back from the repos before it may run.
PASS2_REQUIRED_INPUTS = {
    "api_docs": "backend",
    "ui_shell": "frontend",
}
INPUTS_FOLDER = "_inputs"          # modules/[MOD]/vN/_inputs/<file>

# ─────────────────────────────────────────────
# VERSIONING — git-native. Filesystem folders mirror tags.
# ─────────────────────────────────────────────
TAG_PATTERN = "{mod}-v{version}"                  # e.g. org-v2

def module_root(mod: str) -> Path:
    return MODULES_ROOT / mod.upper()

def module_versions(mod: str) -> list[int]:
    """Existing local versions: base folder = v1 when it has content; vN subfolders."""
    root = module_root(mod)
    if not root.exists():
        return []
    vs, base_content = set(), False
    for child in root.iterdir():
        m = re.fullmatch(r"v(\d+)", child.name)
        if child.is_dir() and m:
            vs.add(int(m.group(1)))
        else:
            base_content = True
    if base_content:
        vs.add(1)
    return sorted(vs)

def current_version(mod: str) -> int:
    vs = module_versions(mod)
    return max(vs) if vs else 1

def next_version(mod: str) -> int:
    vs = module_versions(mod)
    return (max(vs) + 1) if vs else 1

def version_root(mod: str, version: int | None = None) -> Path:
    if version is None:
        version = current_version(mod)
    return module_root(mod) if version == 1 else module_root(mod) / f"v{version}"

def tag_name(mod: str, version: int) -> str:
    return TAG_PATTERN.format(mod=mod.lower(), version=version)

def fmt(template: str, mod: str, version: int | None = None) -> str:
    return (template.replace("{MOD}", mod.upper()).replace("{mod}", mod.lower())
                    .replace("{version}", str(version) if version is not None else ""))

# ─────────────────────────────────────────────
# ANALYSIS PASSES — which engines run when, and where the factory stops.
# Engine ids match engines/<id>/SKILL.md.
# ─────────────────────────────────────────────
BOOTSTRAP = ["P-1"]                                     # once per platform: platform/project-registry.md
PASS_1 = ["domain-profile", "P0", "P0.5", "P1", "P2", "P2.5", "P3.1", "P3.5"]   # P3.5 = backend tests; stops here
PASS_2 = ["P3.2", "P3.5"]                                # P3.5 = frontend tests; needs PASS2_REQUIRED_INPUTS
OPTIONAL = ["optional/P4.1", "optional/P4.2", "optional/P5"]   # never a gate for the core
RETIRED = ["optional/P-REG"]
PLATFORM_DIR = FACTORY_ROOT / "platform"                # platform-level artifacts (P-1 + inline maintenance)

# Review gates (approved: 4 per-engine stations + 2 holistic).
PER_ENGINE_REVIEW_AT = ["P1", "P2", "P3.1", "P3.2"]
HOLISTIC_REVIEW_AT = {"after_pass_1": "backend", "after_pass_2": "frontend"}

# ─────────────────────────────────────────────
# DELEGATE LANES — model/effort control lives in the delegate brief per call
# (delegate-skills). These are the approved DEFAULTS; every command may
# override per run. implementer ∈ {"claude", "codex"}.
# ─────────────────────────────────────────────
LANES = {
    "analysis":          {"implementer": "claude", "model": "opus",   "effort": "high"},
    "merge-review-notes":{"implementer": "claude", "model": "sonnet", "effort": "low"},
    "review-per-engine": {"implementer": "claude", "model": "sonnet", "effort": "medium"},
    "review-holistic":   {"implementer": "codex",  "model": "default","effort": "high"},
    "split":             {"implementer": "tools",  "model": None,     "effort": None},   # no model
    "deliver":           {"implementer": "tools",  "model": None,     "effort": None},
}
