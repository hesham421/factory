"""
ERP Governance Tools — Frontend Configuration
================================================
Single source of truth for the FRONTEND toolset only.

This file has NO representation of "backend" anywhere except one
sanctioned cross-repo read, documented below. It has no --track flag,
no P4 concept, and no hardcoded module-name logic of any kind — no
denylist, no allowlist, no special case for any particular module.
Module identity is validated purely by looking the code up in the
published module registry; whatever is or isn't registered there is
whatever is or isn't reachable here. This file carries no historical
knowledge of any specific module — it is generic by construction.

Marker vocabulary (frontend, verified against PROJECT-3-FRONTEND-ENGINE.md
§ "no frontend phase carries atomic (API/XM/TC) markers" and
PROJECT-3-REGISTRY-2.md §5.7):
  frontend-execution-plan.md → PHASE + SUB only (no atomic markers).
  frontend-test-plan.md      → PHASE + SUB (UI-FLOWS/INT-FLOW) + TC.
The backend-owned API / XM atomic markers are intentionally NOT
recognized here: API-ID and XM-ID are referenced by the frontend only
as plain text, never re-marked. marker_parser.py flags any unrecognized
marker kind (an API/XM/MARK comment leaked from a backend pattern) as a
structural error rather than silently absorbing it — see its
_check_foreign_markers().

The one sanctioned cross-repo read:
  BACKEND_REGISTRY_FILE — read-only, to validate a module exists.
  This reads shared/modules-registry.json, a copy backend PUBLISHES on
  every registry write (see backend's save_modules_registry) — it is
  not a path inside backend/governance/ itself. Neither track reaches
  into the other's internal tree for this.

API Docs are NOT read from backend at all — they live under this
repo's own modules/{MOD}/api-docs/, placed there manually (or by
whatever process publishes them) after real implementation. This
track never reaches into backend/governance/modules/ for anything.
(Note: "API Docs" here are the real endpoint contract documents the
frontend consumes — unrelated to the backend-only API marker removed
from this toolset.)
"""

from pathlib import Path
import json
import re

# ─────────────────────────────────────────────
# REPO — Single root for this repo's own content. Derived from this
# file's own location, not hardcoded, so the repo works regardless of
# which machine/user account it's checked out under.
# ─────────────────────────────────────────────

REPO_BASE_PATH = Path(__file__).resolve().parent.parent

# The ONE sanctioned read into the published module registry —
# read-only, never written from this file. This repo maintains no
# module registry of its own; module identity truth lives entirely in
# backend, but this reads backend's PUBLISHED copy (a file backend
# writes specifically for other tracks to consume), not a path inside
# backend/governance/ itself — so neither track reaches into the
# other's internal directory tree. Derived relative to REPO_BASE_PATH
# so it stays correct on any machine.
BACKEND_REGISTRY_FILE = REPO_BASE_PATH.parent.parent / "shared" / "modules-registry.json"

# API Docs live inside this repo's own tree — modules/{MOD}/api-docs/
# — not inside backend's. Populated after real implementation; this
# track has no read path into backend/governance/modules/ at all.
API_DOCS_ROOT = REPO_BASE_PATH / "modules"


def get_api_docs_path(mod: str) -> Path:
    return API_DOCS_ROOT / mod.upper() / "api-docs"


# ─────────────────────────────────────────────
# MODULE VALIDATION — the only gate that can reject a module by
# identity. No denylist, no special-cased module name, anywhere.
# ─────────────────────────────────────────────

def load_backend_registry() -> dict:
    """
    Read-only load of backend's modules-registry.json. If it doesn't
    exist or isn't reachable, no module is valid — this repo has no
    fallback list of its own, by design.
    """
    if BACKEND_REGISTRY_FILE.exists():
        with open(BACKEND_REGISTRY_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"modules": {}}


def validate_module(mod: str) -> str:
    """
    Validate a module code against backend's registry — the ONLY
    source of truth for which modules exist. A module not found here
    is rejected with a generic "not registered" message; there is no
    module-specific rejection message anywhere in this codebase,
    because there is no module-specific logic to produce one.
    """
    mod = mod.upper().strip()
    registry = load_backend_registry()
    if mod in registry.get("modules", {}):
        return mod

    raise ValueError(
        f"Module '{mod}' is not registered in backend's modules-registry.json.\n"
        f"This repo never registers modules itself — registration happens "
        f"only in the backend toolset. If this module should exist, register "
        f"it there first."
    )


# ─────────────────────────────────────────────
# MODULE FOLDER STRUCTURE — frontend stages only
# ─────────────────────────────────────────────

MODULE_STRUCTURE = {
    "P3_2":     "P3_2",      # Frontend Execution Plan
    "P3_5_FE":  "P3_5_FE",   # Frontend Test Plan
}

FRONTEND_STAGES = ("P3_2", "P3_5_FE")

# ─────────────────────────────────────────────
# ARTIFACT FILENAMES — exact names produced by the real governance
# engines (verified against PROJECT-3-FRONTEND-ENGINE.md and
# PROJECT-REG-STATE-REGISTRY-EXTRACTOR.md §4.3b/§4.4b)
# ─────────────────────────────────────────────

# Module-qualified (AMEND-PIPELINE-V5 §5): the module code is a SUFFIX
# ("frontend-execution-plan-{mod}.md"), matching registry-*-{mod}.md, so
# several modules can share one drop folder without collisions or
# content-sniffing. Plan names are defined ONCE here and referenced
# everywhere (ARTIFACT_FILES, PLAN_ARTIFACTS, agent3, tests).

EXEC_PLAN_FILE = "frontend-execution-plan-{mod}.md"
TEST_PLAN_FILE = "frontend-test-plan-{mod}.md"

ARTIFACT_FILES = {
    "P3_2": [
        EXEC_PLAN_FILE,
        "registry-exec-fe-{mod}.md",   # inline registry step (§1D)
    ],
    "P3_5_FE": [
        TEST_PLAN_FILE,                # TestSprite-ready TC spec (§1D-3c)
        "registry-test-fe-{mod}.md",   # inline registry step (§1D)
    ],
}

# The two split-able plans, keyed for agent3 — (stage, filename template).
PLAN_ARTIFACTS = {
    "exec": ("P3_2",    EXEC_PLAN_FILE),
    "test": ("P3_5_FE", TEST_PLAN_FILE),
}


def plan_label(key: str, mod: str) -> str:
    """Resolved plan filename for display/logging."""
    return resolve_filename(PLAN_ARTIFACTS[key][1], mod)


def plan_file(base, mod: str, key: str):
    """Path of a plan inside a module VERSION base — the only way agent3
    locates a plan; it never spells the filename itself."""
    stage, tmpl = PLAN_ARTIFACTS[key]
    return base / MODULE_STRUCTURE[stage] / resolve_filename(tmpl, mod)


# ─────────────────────────────────────────────
# PACKAGES STRUCTURE — frontend-execution-plan.md / frontend-test-plan.md splits.
# This is the SINGLE source of truth for the frontend execution phase
# names; agent3 derives its phase→folder map from here rather than
# keeping a second copy.
# ─────────────────────────────────────────────

PACKAGES_STRUCTURE = {
    "frontend-execution": [
        "F1",
        "F2",
        "F3",
        "F4",
        "SEC-FE",
        "ALIGN-FE",
    ],
    "frontend-test": [
        "UI-FLOWS",
        "INT-FLOW",
    ],
}

# Frontend execution phases that carry per-screen SUB blocks (and thus
# require phase-qualified SUB labels, SUB:{PHASE}-{SCR-ID}). SEC-FE and
# ALIGN-FE never split — they carry no SUB. Used by agent3's --fix-safe
# to know which phases' bare SUB labels are auto-repairable.
SUB_BEARING_EXEC_PHASES = ("F1", "F2", "F3", "F4")

# The single phase key of the frontend test plan, and the TC threshold
# above which it is expected to carry UI-FLOWS / INT-FLOW SUBs
# (PROJECT-3-REGISTRY-2.md: "frontend-test-plan.md | TCs > 8").
TEST_PLAN_PHASE_KEY = "TEST-PLAN-FE"
TEST_PLAN_SUB_THRESHOLD = 8

# ─────────────────────────────────────────────
# MARKER PATTERNS — frontend vocabulary only: PHASE, SUB, TC.
# The backend-owned API / XM atomic markers are deliberately absent —
# they never appear in a frontend artifact. Any marker-shaped comment
# whose kind is not one of these is rejected by marker_parser as a
# foreign/unrecognized marker.
# ─────────────────────────────────────────────

MARKERS = {
    "phase":  re.compile(r"<!--\s*PHASE:(\w[\w-]*):(START|END)\s*-->"),
    "sub":    re.compile(r"<!--\s*SUB:([\w-]+):(START|END)\s*-->"),
    "tc":     re.compile(r"<!--\s*TC:(TC-[\w-]+):(START|END)\s*-->"),
}

# Generic marker shape — matches ANY "<!-- KIND:ID:START|END -->" comment
# regardless of KIND. Used to detect foreign markers (a kind not in
# MARKERS, e.g. an API/XM/MARK comment leaked from a backend pattern),
# which are a structural error in a frontend artifact.
GENERIC_MARKER = re.compile(r"<!--\s*([A-Za-z][\w-]*):([\w-]+):(START|END)\s*-->")

# Allowed nesting hierarchy — the SINGLE source of truth. marker_parser
# imports this rather than keeping its own copy.
#   PHASE  → top level only
#   SUB    → inside PHASE only
#   TC     → inside PHASE or SUB (frontend-test-plan.md only)
ALLOWED_PARENTS = {
    "phase": [None],
    "sub":   ["phase"],
    "tc":    ["phase", "sub"],
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_module_path(mod: str, version: "int | None" = None) -> Path:
    """Root path for a module VERSION in THIS repo. version=None → the
    current (highest existing) local version, v1 when the module is new.
    v1 = modules/[MOD]/ (no suffix); vN = modules/[MOD]/v{N}/.
    Pure path resolution — reads the filesystem, never the registry."""
    return get_module_version_path(mod, version)


def _module_root(mod: str) -> Path:
    """Raw un-versioned module root — internal, never leaks a version."""
    return REPO_BASE_PATH / "modules" / mod.upper()


def get_module_versions(mod: str) -> list[int]:
    """
    Existing LOCAL versions of a module, derived from the frontend's own
    folder tree (this repo owns its module tree; it never writes the
    backend-owned registry, so version truth for FE layout is the
    filesystem). v1 = the un-suffixed base folder holding real content;
    vN = a modules/[MOD]/v{N}/ subfolder.
    """
    root = _module_root(mod)
    if not root.exists():
        return []
    versions: set[int] = set()
    has_base_content = False
    for child in root.iterdir():
        m = re.fullmatch(r"v(\d+)", child.name)
        if child.is_dir() and m:
            versions.add(int(m.group(1)))
        else:
            # any non-vN child (P3_2/, packages/, manifest.json, …) means
            # the un-suffixed base folder is itself a real v1.
            has_base_content = True
    if has_base_content:
        versions.add(1)
    return sorted(versions)


def get_current_version(mod: str) -> int:
    """Highest existing local version — the one tools operate on by default."""
    vs = get_module_versions(mod)
    return max(vs) if vs else 1


def get_next_version(mod: str) -> int:
    """
    Next version to CREATE. First build is v1; once any version exists the
    next is max+1. The frontend never invents a version the way backend
    does via the registry — it just makes the next local folder alongside
    the frozen prior ones (agent1 --new-version).
    """
    vs = get_module_versions(mod)
    return (max(vs) + 1) if vs else 1


def get_module_version_path(mod: str, version: "int | None" = None) -> Path:
    """
    Path for a specific version of a module. Self-contained — no registry
    read. version=None → current local version.
    v1 = modules/[MOD]/ (no suffix); vN = modules/[MOD]/v{N}/.
    """
    mod = mod.upper()
    if version is None:
        version = get_current_version(mod)
    if version == 1:
        return _module_root(mod)
    return _module_root(mod) / f"v{version}"


def get_stage_path(mod: str, stage: str, version: "int | None" = None) -> Path:
    if stage not in MODULE_STRUCTURE:
        raise ValueError(f"Unknown frontend stage: {stage}. Valid: {list(MODULE_STRUCTURE.keys())}")
    return get_module_path(mod, version) / MODULE_STRUCTURE[stage]


def get_packages_path(mod: str, artifact: str, sub: str = "", version: "int | None" = None) -> Path:
    base = get_module_path(mod, version) / "packages" / artifact
    return base / sub if sub else base


def resolve_filename(template: str, mod: str) -> str:
    return template.replace("{mod}", mod.lower())


def ensure_module_structure(mod: str, version: "int | None" = None) -> list[Path]:
    """
    Create every frontend stage folder + packages subfolder for a module
    VERSION if missing — idempotent, safe to call from any tool. version=
    None → current local version. Never touches anything in
    backend/governance/ and never writes any registry.
    """
    created = []
    for stage in FRONTEND_STAGES:
        p = get_stage_path(mod, stage, version)
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            (p / ".gitkeep").touch()
            created.append(p)
    for artifact, subs in PACKAGES_STRUCTURE.items():
        for sub in subs:
            p = get_packages_path(mod, artifact, sub, version)
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                (p / ".gitkeep").touch()
                created.append(p)
    return created


def build_manifest(mod: str, version: "int | None" = None) -> dict:
    """
    This repo's own lightweight manifest — separate from backend's
    manifest.json for the same module (never merged, never synced).
    version=None → current local version.
    """
    base = get_module_path(mod, version)

    # Relative to REPO_BASE_PATH, never absolute — see the matching note
    # in backend's config.py. An absolute path here bakes in the
    # checking-out machine's home directory and this folder's name at
    # generation time, both of which differ across machines and drift
    # on any rename/move.
    def rel(p: Path) -> str:
        return str(p.relative_to(REPO_BASE_PATH))

    return {
        "module": mod,
        "status": {
            "archived": False,
            "split":    False,
        },
        "artifacts": {
            "p3_2":    rel(base / MODULE_STRUCTURE["P3_2"]),
            "p3_5_fe": rel(base / MODULE_STRUCTURE["P3_5_FE"]),
        },
        "registries": {
            "exec_fe": rel(base / MODULE_STRUCTURE["P3_2"] / f"registry-exec-fe-{mod.lower()}.md"),
            "test_fe": rel(base / MODULE_STRUCTURE["P3_5_FE"] / f"registry-test-fe-{mod.lower()}.md"),
        },
        "packages": {
            "frontend_execution": rel(base / "packages" / "frontend-execution"),
            "frontend_test":      rel(base / "packages" / "frontend-test"),
        },
    }


# ─────────────────────────────────────────────
# SPLIT RECEIPT (AMEND-PIPELINE-V5 §1D.8) — written by agent3 stage 5 with one
# journey-ledger row per package file (repo_path; packages are git-resident,
# never uploaded). The dual-track orchestrator appends it to the module's
# ledger via backend's journey_loader --append-receipts. Naming only — the
# ledger schema itself is owned by the backend toolset (single source).
# ─────────────────────────────────────────────
RECEIPT_FILE = "split-receipt-{mod}-v{version}.json"


def receipt_filename(mod: str, version: int) -> str:
    return RECEIPT_FILE.replace("{mod}", mod.lower()).replace("{version}", str(version))
