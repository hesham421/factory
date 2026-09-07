"""
ERP Governance Tools — Backend Configuration
==============================================
Single source of truth for the BACKEND toolset only.

This file has NO representation of "frontend" anywhere — not a
constant, not a path, not a conditional branch. The frontend has its
own completely separate copy of these five tools, in
frontend/governance/governance-tools/, which likewise has no
representation of "backend" beyond one sanctioned cross-repo read: the
published module registry (shared/modules-registry.json, written by
save_modules_registry below). Frontend does not read API Docs from
here either — those live in frontend's own modules/{MOD}/api-docs/.

There is no P4/P4_1 concept anywhere in this ecosystem — the
pre-implementation audit gate was removed entirely.

There is no --track flag anywhere in this toolset. Every tool here
does exactly one thing: backend.
"""

from pathlib import Path
import json
import re

# ─────────────────────────────────────────────
# REPO — Single root. Derived from this file's own location, not
# hardcoded, so the repo works regardless of which machine/user
# account it's checked out under.
# ─────────────────────────────────────────────

# Inside the governance FACTORY the modules tree lives at the factory root
# (GOV_FACTORY_ROOT, set by gov.py on dispatch); standalone, fall back to the
# classic layout (this file's grandparent).
import os as _os
REPO_BASE_PATH = Path(_os.environ["GOV_FACTORY_ROOT"]) if _os.environ.get("GOV_FACTORY_ROOT") \
    else Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# MODULES
# ─────────────────────────────────────────────

KNOWN_MODULES = [
    # Add modules here as they're registered
]

MODULES_REGISTRY_FILE = Path(__file__).resolve().parent / "modules-registry.json"   # track-owned, always

# Published, read-only copy of the registry for other tracks (frontend, etc.)
# to consume. Lives outside both backend/ and frontend/ trees so no other
# track ever needs a path that reaches into backend's internals directly.
SHARED_REGISTRY_FILE = REPO_BASE_PATH.parent.parent / "shared" / "modules-registry.json"


def load_modules_registry() -> dict:
    """Load the dynamic modules registry from disk."""
    if MODULES_REGISTRY_FILE.exists():
        with open(MODULES_REGISTRY_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"modules": {}}


def save_modules_registry(registry: dict):
    """Save the dynamic modules registry to disk, and publish a copy to
    SHARED_REGISTRY_FILE for other tracks to read — the only sanctioned
    way another track learns about registered modules."""
    MODULES_REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MODULES_REGISTRY_FILE, "w", encoding="utf-8") as fh:
        json.dump(registry, fh, indent=2, ensure_ascii=False)

    SHARED_REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SHARED_REGISTRY_FILE, "w", encoding="utf-8") as fh:
        json.dump(registry, fh, indent=2, ensure_ascii=False)


def register_module(mod: str, description: str = "") -> dict:
    """Register a new module or return its existing registration."""
    registry = load_modules_registry()
    if mod not in registry["modules"]:
        registry["modules"][mod] = {
            "code": mod,
            "description": description,
            "registered_at": __import__("datetime").datetime.now().isoformat(),
            "versions": [],
            "current_version": None,
        }
        save_modules_registry(registry)
    return registry["modules"][mod]


def get_module_version_path(mod: str, version: "int | None" = None) -> Path:
    """
    Path for a specific version of a module. Self-contained — never calls
    get_module_path (which now delegates here), so no mutual recursion.
    Version 1 = modules/[MODCODE]/ (no suffix), version 2 = modules/[MODCODE]/v2/, etc.
    mod is normalised to upper-case so v1 and v2 paths agree on casing.
    """
    mod = mod.upper()
    registry = load_modules_registry()
    mod_entry = registry.get("modules", {}).get(mod)

    if version is None:
        version = (mod_entry.get("current_version") if mod_entry else None) or 1

    if version == 1:
        return REPO_BASE_PATH / "modules" / mod
    return REPO_BASE_PATH / "modules" / mod / f"v{version}"

# ─────────────────────────────────────────────
# MODULE FOLDER STRUCTURE — backend stages only
# ─────────────────────────────────────────────

MODULE_STRUCTURE = {
    "P0":       "P0",        # Platform Inception outputs
    "P0_5":     "P0_5",      # PRD Engine: prd-{mod}.md
    "P1":       "P1",        # SRS outputs
    "P2":       "P2",        # DB Script outputs
    "P2_5":     "P2_5",      # UI/UX Design Engine text outputs:
                              # flow-diagram.md, ui-ux-spec.md
                              # (visual-mockups/ lives in the frontend repo)
    "P3_1":     "P3_1",      # Backend Execution Plan
    "P3_5_BE":  "P3_5_BE",   # Backend Test Plan + test-execution-manifest.md
    "packages": "packages",
}

BACKEND_STAGES = ("P0", "P0_5", "P1", "P2", "P2_5", "P3_1", "P3_5_BE")

# ─────────────────────────────────────────────
# ARTIFACT FILENAMES — exact names produced by the real governance
# engines (verified directly against PRD-ENGINE.md,
# PROJECT-1-SRS-GOVERNANCE-ENGINE.md, PROJECT-2-DATABASE-GOVERNANCE-
# ENGINE.md, UI-UX-DESIGN-ENGINE.md, PROJECT-3-BACKEND-ENGINE.md)
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# ARTIFACT FILENAMES — module-qualified (AMEND-PIPELINE-V5 §5).
# Every per-module artifact carries the module code as a SUFFIX
# ("srs-{mod}.md"), matching the registry-*-{mod}.md convention that
# already existed, so several modules' files can share one drop folder
# without colliding and without content-sniffing to find the module.
# The plan filenames below are defined ONCE as constants and referenced
# everywhere (ARTIFACT_FILES, PLAN_ARTIFACTS, agent3, tests) — there is
# no literal plan filename anywhere else in this toolset.
# ─────────────────────────────────────────────

EXEC_PLAN_FILE = "backend-execution-plan-{mod}.md"
TEST_PLAN_FILE = "backend-test-plan-{mod}.md"

ARTIFACT_FILES = {
    "P0": [
        "platform-summary.md",              # platform-level, not per-module
        "module-registry-{mod}.md",
        "business-policies-{mod}.md",
    ],
    "P0_5": [
        "prd-{mod}.md",
    ],
    "P1": [
        "srs-{mod}.md",
        "registry-srs-{mod}.md",            # inline registry step (§1D)
    ],
    "P2": [
        "db-script-{mod}.md",
        "registry-db-{mod}.md",             # inline registry step (§1D)
    ],
    "P2_5": [
        "flow-diagram-{mod}.md",
        "ui-ux-spec-{mod}.md",
        # visual-mockups/ is a directory, lives in the frontend repo
    ],
    "P3_1": [
        EXEC_PLAN_FILE,
        "registry-exec-be-{mod}.md",        # inline registry step (§1D)
    ],
    "P3_5_BE": [
        TEST_PLAN_FILE,                     # TestSprite-ready TC spec (§1D-3c)
        "registry-test-be-{mod}.md",        # inline registry step (§1D)
    ],
}

# The two split-able plans, keyed for agent3 — (stage, filename template).
# Derived from the SAME constants as ARTIFACT_FILES: single source of truth.
PLAN_ARTIFACTS = {
    "exec": ("P3_1",    EXEC_PLAN_FILE),
    "test": ("P3_5_BE", TEST_PLAN_FILE),
}


def plan_label(key: str, mod: str) -> str:
    """Resolved plan filename for display/logging (e.g. backend-execution-plan-org.md)."""
    return resolve_filename(PLAN_ARTIFACTS[key][1], mod)


def plan_file(base, mod: str, key: str):
    """Absolute path of a plan inside a module VERSION base — the only way
    agent3 locates a plan; it never spells the filename itself."""
    stage, tmpl = PLAN_ARTIFACTS[key]
    return base / MODULE_STRUCTURE[stage] / resolve_filename(tmpl, mod)


# Files archived once at the governance root rather than per-module.
# Empty since master-registry.md was removed — agent2_archive.py handles an
# empty list fine (it simply produces no SHARED operations).
SHARED_FILES: list[str] = []

# ─────────────────────────────────────────────
# PACKAGES STRUCTURE — backend-execution-plan.md / backend-test-plan.md splits
# ─────────────────────────────────────────────

# Each entry maps an artifact package to the set of sub-folders that are
# PRE-CREATED for it. Agent 3 writes into these folders.
#
#   backend-execution : one folder per canonical PHASE key. Agent 3 Stage 2
#                       writes each phase's package file(s) INTO its phase
#                       folder. These are the eight canonical backend
#                       execution phases (PROJECT-3-REGISTRY.md Section 2 /
#                       PROJECT-3-BACKEND-ENGINE.md) — no more, no less.
#                       (The old dead "SECTIONS" folder was removed —
#                       nothing ever wrote into it. Unmarked top-level
#                       content is now captured by Agent 3 as a flat
#                       _SECTIONS.md file instead — see agent3_splitter.py.)
#
#   backend-test      : NO pre-created sub-folders. backend-test-plan.md
#                       splits into flat files written DIRECTLY inside
#                       packages/backend-test/ (RULE-SCENARIOS.md,
#                       API-SCENARIOS.md, or one whole-phase file below
#                       threshold). Pre-creating RULE-SCENARIOS/ and
#                       API-SCENARIOS/ as *folders* while Agent 3 wrote
#                       them as *files* was FINDING-19 — the folders were
#                       always dead. The container packages/backend-test/
#                       itself is still created (see ensure_module_structure).
PACKAGES_STRUCTURE = {
    "backend-execution": [
        "CORE",
        "DATA-DOM",
        "SVC-API",
        "DOC",
        "INT-C",
        "INT-R",
        "SEC-BE",
        "ALIGN-BE",
    ],
    "backend-test": [],
}

# ─────────────────────────────────────────────
# CANONICAL PHASE KEYS — per artifact file identity. Used by the semantic
# validator (marker_parser.validate_semantics) to reject any PHASE marker
# whose key is not one of the file's canonical keys BEFORE splitting — so a
# typo like <!-- PHASE:SVC+API:START --> (+ instead of -) is caught as a
# blocking error instead of being silently skipped by Agent 3 Stage 2.
# Verified against PROJECT-3-REGISTRY.md Section 2 (Phase Ownership Index)
# and PROJECT-3-BACKEND-ENGINE.md.
# ─────────────────────────────────────────────

# Keyed by PLAN KEY ("exec" / "test"), never by a literal filename — the
# filename is module-qualified and resolved through PLAN_ARTIFACTS, so
# semantic rules stay attached to the artifact's identity, not its name.
CANONICAL_PHASE_KEYS = {
    "exec": [
        "CORE", "DATA-DOM", "SVC-API", "DOC",
        "INT-C", "INT-R", "SEC-BE", "ALIGN-BE",
    ],
    "test": [
        "TEST-PLAN-BE",
    ],
}

# Files whose SUB labels are EXEMPT from the phase-qualification rule
# (AMEND-P3-N). A test-plan file contains exactly one phase, so its two
# possible SUB labels (RULE-SCENARIOS / API-SCENARIOS) can never collide
# across phases and are deliberately left un-prefixed. Every OTHER file
# must phase-qualify every SUB: SUB:{PHASE-KEY}-{LABEL}.
SUB_QUALIFICATION_EXEMPT = {
    "test",
}


def classify_artifact(filename: str) -> str:
    """Return the PLAN KEY ("exec" / "test") for a path/name, or ''.

    File identity drives the semantic checks (canonical phase keys, SUB
    qualification). Matches the basename against each PLAN_ARTIFACTS
    template with "{mod}" as a wildcard, so a module-qualified name
    (backend-execution-plan-org.md) classifies correctly and the semantic
    checks can NEVER be skipped by a name the old exact-match missed.
    """
    name = Path(filename).name
    for key, (_stage, tmpl) in PLAN_ARTIFACTS.items():
        pattern = "^" + re.escape(tmpl).replace(re.escape("{mod}"), r"[a-z0-9_-]+") + "$"
        if re.match(pattern, name, flags=re.IGNORECASE):
            return key
    return ""


# ─────────────────────────────────────────────
# SPLIT THRESHOLDS — data-driven, AUTO-checked by the splitter.
#
# When a phase's countable element (an atomic marker kind) reaches its
# threshold, PROJECT-3-REGISTRY.md Section 5.7.4 expects the generating engine
# to have introduced SUB blocks. Agent 3 verifies this AUTOMATICALLY. The check
# is deliberately FLEXIBLE:
#   • advisory by default (a warning, never blocks) — because the split
#     decision is ultimately semantic, and a phase legitimately at the trigger
#     count with no meaningful sub-grouping is a judgment call, not an error;
#   • escalated to BLOCKING only when the caller passes --strict-thresholds;
#   • only phases whose trigger is countable FROM MARKERS are listed here.
#     DATA-DOM's "Entities ≥ 5" trigger is intentionally omitted: entities are
#     not a marker kind, so it cannot be counted structurally and is left to
#     the generating engine's own self-check. "Methods ≥ 6" for SVC-API is
#     likewise not marker-countable; API count is used as the structural proxy.
#
# To change a threshold, edit one row here — nothing else.
# Each rule: kind = atomic marker to count; count/op = the trigger comparison.
# ─────────────────────────────────────────────

PHASE_SPLIT_THRESHOLDS = {
    "SVC-API":      {"kind": "api", "count": 8,  "op": ">=", "grouping": "CRUD / SEARCH / INT"},
    "INT-C":        {"kind": "xm",  "count": 5,  "op": ">=", "grouping": "per target module"},
    "INT-R":        {"kind": "xm",  "count": 5,  "op": ">=", "grouping": "per target module"},
    "TEST-PLAN-BE": {"kind": "tc",  "count": 12, "op": ">",  "grouping": "RULE-SCENARIOS / API-SCENARIOS"},
}

# Phases that must never carry SUB blocks (Section 5.7.4 "Never splits"). If one
# does, it is flagged with the same advisory/flexible severity model.
NEVER_SPLIT_PHASES = {"CORE", "DOC", "SEC-BE", "ALIGN-BE"}

# ─────────────────────────────────────────────
# MARKER PATTERNS — neutral, no backend/frontend distinction in the
# syntax itself (see marker_parser.py)
# ─────────────────────────────────────────────

MARKERS = {
    "phase":  re.compile(r"<!--\s*PHASE:(\w[\w-]*):(START|END)\s*-->"),
    "sub":    re.compile(r"<!--\s*SUB:([\w-]+):(START|END)\s*-->"),
    "api":    re.compile(r"<!--\s*API:(API-[\w-]+):(START|END)\s*-->"),
    "xm":     re.compile(r"<!--\s*XM:(XM-[\w-]+):(START|END)\s*-->"),
    "tc":     re.compile(r"<!--\s*TC:(TC-[\w-]+):(START|END)\s*-->"),
}

ALLOWED_PARENTS = {
    "phase": [None],
    "sub":   ["phase"],
    "api":   ["phase", "sub"],
    "xm":    ["phase", "sub"],
    "tc":    ["phase", "sub"],
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_module_path(mod: str, version: "int | None" = None) -> Path:
    """
    Root path for a module. Auto-creates nothing — pure path resolution.
    version=None → the module's current_version from the registry (v1 when
    unregistered). This makes the whole path chain (stage/packages/ensure)
    version-aware while every existing call site (no version arg) keeps
    resolving to the current version, unchanged.
    """
    return get_module_version_path(mod.upper(), version)


def get_stage_path(mod: str, stage: str, version: "int | None" = None) -> Path:
    if stage not in MODULE_STRUCTURE:
        raise ValueError(f"Unknown backend stage: {stage}. Valid: {list(MODULE_STRUCTURE.keys())}")
    return get_module_path(mod, version) / MODULE_STRUCTURE[stage]


def get_packages_path(mod: str, artifact: str, sub: str = "", version: "int | None" = None) -> Path:
    base = get_module_path(mod, version) / "packages" / artifact
    return base / sub if sub else base


def resolve_filename(template: str, mod: str) -> str:
    return template.replace("{mod}", mod.lower())


def validate_module(mod: str, auto_register: bool = False, description: str = "") -> str:
    """
    Validate and normalize a module code.
    auto_register=True registers unknown modules automatically.
    """
    mod = mod.upper().strip()

    if mod in KNOWN_MODULES:
        return mod

    registry = load_modules_registry()
    if mod in registry.get("modules", {}):
        return mod

    if auto_register:
        register_module(mod, description)
        return mod

    raise ValueError(
        f"Module '{mod}' is not registered.\n"
        f"Static modules : {', '.join(KNOWN_MODULES) or '(none yet)'}\n"
        f"Use --auto-register to register it automatically, or add it "
        f"to KNOWN_MODULES in config.py."
    )


def ensure_module_structure(mod: str, version: "int | None" = None) -> list[Path]:
    """
    Create every backend stage folder + packages subfolder for a module
    VERSION if missing — idempotent, safe to call from any tool (agent1
    explicitly, or agent2 automatically when the structure doesn't
    exist yet). version=None → current version. Returns the list of
    paths that were newly created.
    """
    created = []
    for stage in BACKEND_STAGES:
        p = get_stage_path(mod, stage, version)
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            (p / ".gitkeep").touch()
            created.append(p)
    for artifact, subs in PACKAGES_STRUCTURE.items():
        # Always create the artifact container itself — even when it has no
        # pre-created sub-folders (backend-test), Agent 3 writes flat files
        # directly into this container.
        container = get_packages_path(mod, artifact, version=version)
        if not container.exists():
            container.mkdir(parents=True, exist_ok=True)
            (container / ".gitkeep").touch()
            created.append(container)
        for sub in subs:
            p = get_packages_path(mod, artifact, sub, version=version)
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                (p / ".gitkeep").touch()
                created.append(p)
    return created


# ─────────────────────────────────────────────
# MANIFEST SCHEMA
# ─────────────────────────────────────────────

def build_manifest(mod: str, version: int = 1) -> dict:
    base = get_module_version_path(mod, version)

    # Paths are stored relative to REPO_BASE_PATH, never absolute — an
    # absolute Path here would bake in the checking-out machine's home
    # directory and this repo's on-disk folder name at generation time,
    # both of which are guaranteed to differ across machines and to
    # drift the moment the repo/folder is renamed or moved.
    def rel(p: Path) -> str:
        return str(p.relative_to(REPO_BASE_PATH))

    return {
        "module":  mod,
        "version": version,
        "status": {
            "archived":  False,
            "split":     False,
            "backend_module_complete": False,  # gate for frontend readiness
            "ui_shell_complete": False,
        },
        "artifacts": {
            "p0":      rel(base / MODULE_STRUCTURE["P0"]),
            "p0_5":    rel(base / MODULE_STRUCTURE["P0_5"]),
            "p1":      rel(base / MODULE_STRUCTURE["P1"]),
            "p2":      rel(base / MODULE_STRUCTURE["P2"]),
            "p2_5":    rel(base / MODULE_STRUCTURE["P2_5"]),
            "p3_1":    rel(base / MODULE_STRUCTURE["P3_1"]),
            "p3_5_be": rel(base / MODULE_STRUCTURE["P3_5_BE"]),
        },
        "registries": {
            "srs":     rel(base / MODULE_STRUCTURE["P1"] / f"registry-srs-{mod.lower()}.md"),
            "db":      rel(base / MODULE_STRUCTURE["P2"] / f"registry-db-{mod.lower()}.md"),
            "exec_be": rel(base / MODULE_STRUCTURE["P3_1"] / f"registry-exec-be-{mod.lower()}.md"),
            "test_be": rel(base / MODULE_STRUCTURE["P3_5_BE"] / f"registry-test-be-{mod.lower()}.md"),
        },
        "packages": {
            "backend_execution": rel(base / "packages" / "backend-execution"),
            "backend_test":      rel(base / "packages" / "backend-test"),
        },
    }


def get_next_version(mod: str) -> int:
    registry = load_modules_registry()
    entry = registry.get("modules", {}).get(mod)
    if not entry or not entry.get("versions"):
        return 1
    return max(entry["versions"]) + 1


def set_current_version(mod: str, version: int):
    registry = load_modules_registry()
    if mod not in registry["modules"]:
        register_module(mod)
        registry = load_modules_registry()
    entry = registry["modules"][mod]
    if version not in entry["versions"]:
        entry["versions"].append(version)
    entry["current_version"] = version
    save_modules_registry(registry)


# ─────────────────────────────────────────────
# JOURNEY LEDGER (AMEND-PIPELINE-V5 §1D) — ONE file per module, all versions.
# Drive location: [LEDGER] = [CTX]/[Module]/journey-{mod}.json (GOVERNANCE-
# CONFIG §1B). Written by every engine's completion protocol (one row per
# artifact it uploaded) and by Stage-2 tooling (package receipts). Read by
# journey_loader.py to download a module+version in one pass.
# The schema lives HERE so engines, the loader, and tests share one truth.
# ─────────────────────────────────────────────

LEDGER_FILE = "journey-{mod}.json"

LEDGER_VERSION_STATUS = ("OPEN", "CLOSED")          # START … END of a version
LEDGER_ARTIFACT_STATUS = ("UPLOADED", "SUPERSEDED")

# Required keys of one artifact row. "drive_file_id" is what the loader hands
# to the Drive connector; "drive_url" is for humans.
LEDGER_ROW_KEYS = ("engine", "stage", "filename", "artifact",
                   "drive_file_id", "drive_url", "recorded_at", "status")

# A row records WHERE the file lives: Drive artifacts carry drive_file_id +
# drive_url; repo-resident package files (Stage-2 output, git-tracked, never
# uploaded) carry repo_path instead. Exactly one of the two is required.
LEDGER_LOCATION_KEYS = (("drive_file_id",), ("repo_path",))


def ledger_filename(mod: str) -> str:
    return resolve_filename(LEDGER_FILE, mod)


def new_ledger(mod: str) -> dict:
    """Empty ledger skeleton for a module (versions keyed by string int)."""
    return {"module": mod.upper(), "schema": "journey-ledger/1", "versions": {}}


def open_ledger_version(ledger: dict, version: int, engine: str, change_set: "str | None" = None,
                        started_at: "str | None" = None) -> dict:
    """START module <MOD> vN — creates the version section (idempotent)."""
    key = str(version)
    if key not in ledger["versions"]:
        ledger["versions"][key] = {
            "status": "OPEN", "started_at": started_at, "started_by_engine": engine,
            "ended_at": None, "change_set": change_set, "artifacts": [],
        }
    return ledger["versions"][key]


def close_ledger_version(ledger: dict, version: int, ended_at: "str | None" = None) -> dict:
    """END module <MOD> vN — freezes the version section."""
    sec = ledger["versions"][str(version)]
    sec["status"] = "CLOSED"
    sec["ended_at"] = ended_at
    return sec


def validate_ledger_row(row: dict) -> list[str]:
    """Return a list of problems (empty = valid). A row must carry a location:
    drive_file_id (+drive_url) for Drive artifacts, or repo_path for
    repo-resident package files written by Stage-2 tooling."""
    required = [k for k in LEDGER_ROW_KEYS if k not in ("drive_file_id", "drive_url")]
    problems = [f"missing key: {k}" for k in required if k not in row]
    has_drive = bool(row.get("drive_file_id"))
    has_repo = bool(row.get("repo_path"))
    if not (has_drive or has_repo):
        problems.append("no location: need drive_file_id (Drive) or repo_path (repo)")
    if row.get("status") not in LEDGER_ARTIFACT_STATUS:
        problems.append(f"bad status: {row.get('status')!r}")
    return problems


RECEIPT_FILE = "split-receipt-{mod}-v{version}.json"


def receipt_filename(mod: str, version: int) -> str:
    return RECEIPT_FILE.replace("{mod}", mod.lower()).replace("{version}", str(version))


# ─────────────────────────────────────────────
# DRIVE MIGRATION (AMEND-PIPELINE-V5) — maps a pre-V5 (un-qualified) filename
# to its V5 module-qualified name. Derived from ARTIFACT_FILES: every template
# ending in "-{mod}.md" whose un-qualified form is "<base>.md". Nothing listed
# by hand; if ARTIFACT_FILES changes, the migration map follows.
# ─────────────────────────────────────────────

def legacy_name_map(mod: str) -> dict:
    """{old un-qualified filename: new module-qualified filename} for MOD."""
    out = {}
    for _stage, templates in ARTIFACT_FILES.items():
        for t in templates:
            if t.endswith("-{mod}.md"):
                base = t[: -len("-{mod}.md")]
                # registry-*-{mod}.md / module-registry-{mod}.md were already
                # qualified before V5 — they have no legacy form to migrate.
                if base.startswith("registry-") or base in ("module-registry", "business-policies", "prd"):
                    continue
                out[base + ".md"] = resolve_filename(t, mod)
    return out


# ─────────────────────────────────────────────
# DRIVE LAYOUT (AMEND-PIPELINE-V5 §1E) — the SINGLE machine-readable source
# of where every artifact lives on Drive. GOVERNANCE-CONFIG §1E and each
# engine's PATHS block are RENDERED from this (never hand-typed), and
# drive_layout.py audits real Drive listings against it.
#
# ADDRESSING (multi-project · multi-module · multi-version):
#   [CTX] = [GOVERNANCE-ROOT]/[Project]/[Domain]/<slot>          (§1B)
#   module root   : [CTX]/[Module]/            for version 1
#                   [CTX]/[Module]/v{N}/       for version N ≥ 2   (mirrors the
#                   repo's modules/[MOD]/ vs modules/[MOD]/vN/ convention)
#   LAW           : a file lives ONLY inside its designated stage folder.
#                   [CTX] root and every module root hold FOLDERS ONLY.
# ─────────────────────────────────────────────

# stage key → (drive folder name, writer engine, reader engines)
# Folder names are canonical; writer = the ONE engine allowed to create files
# there; readers = engines that fetch from it (used for the §1E matrix).
DRIVE_LAYOUT = {
    "P0":      ("P0-Platform",       "P0",   ("P0.5", "P1", "P2", "P2.5", "P3.1", "P3.2")),
    "P0_5":    ("P0.5-PRD",          "P0.5", ("P1", "P2.5", "P3.5")),
    "P1":      ("P1-SRS",            "P1",   ("P2", "P2.5", "P3.1", "P3.2", "P3.5", "P4.1", "P4.2")),
    "P2":      ("P2-DB",             "P2",   ("P2.5", "P3.1", "P3.5", "P4.1")),
    "P2_5":    ("P2.5-UIUX",         "P2.5", ("P3.1", "P3.2", "P4.2")),
    "P3_1":    ("P3.1-Backend-Exec", "P3.1", ("P3.2", "P3.5", "P4.1")),
    "P3_5_BE": ("P3.5-Tests",        "P3.5", ("P4.1", "P5")),
}
# Frontend-track stage keys live in the SAME module tree (one Drive tree per
# module, both tracks) — folder names for stages the backend config does not
# archive itself:
DRIVE_LAYOUT_FRONTEND = {
    "P3_2":    ("P3.2-Frontend-Exec", "P3.2", ("P3.5", "P4.2")),
    "P3_5_FE": ("P3.5-Tests",         "P3.5", ("P4.2",)),
}
# REFERENCE folders — durable module inputs uploaded ONCE per version and
# read by any session that opens (AMEND-PIPELINE-V5 §1F): the real UI Shell
# manifest and the real API Docs. Written by P3.2's ingest step; read every
# session by P3.2 (and P3.5/P4.2). They live in the module VERSION tree, so a
# new IFA version gets its own copy and the prior one stays frozen.
DRIVE_LAYOUT_REFERENCE = {
    "REF_SHELL":   ("_ref/ui-shell",  "P3.2", ("P3.2", "P3.5", "P4.2")),
    "REF_APIDOCS": ("_ref/api-docs",  "P3.2", ("P3.1", "P3.2", "P3.5", "P4.1", "P4.2")),
}

# Optional-engine output folders (never read by the core pipeline):
DRIVE_LAYOUT_OPTIONAL = {
    "P4":      ("P4-Audit",          "P4.x", ()),
}
# Cross-version, per-module folder (outside any vN — the ledger spans versions):
DRIVE_JOURNEY_FOLDER = "_journey"                 # [CTX]/[Module]/_journey/journey-{mod}.json
# Platform-level (not per-module) folder under [CTX]:
DRIVE_PLATFORM_FOLDER = "_platform"               # [CTX]/_platform/platform-summary.md
PLATFORM_LEVEL_FILES = ("platform-summary.md",)   # the only files allowed there

# Frontend artifact templates the backend config must know ONLY for Drive
# placement/auditing (it never archives them). Mirrors frontend config.
REFERENCE_FILES = {
    "REF_SHELL":   ["ui-shell-manifest-{mod}.md"],
    "REF_APIDOCS": ["api-docs-{mod}.md"],
}

FRONTEND_ARTIFACT_FILES = {
    "P3_2":    ["frontend-execution-plan-{mod}.md", "registry-exec-fe-{mod}.md"],
    "P3_5_FE": ["frontend-test-plan-{mod}.md",      "registry-test-fe-{mod}.md"],
}


def all_drive_stages() -> dict:
    """stage key → (folder, writer, readers) across both tracks + references + optional."""
    return {**DRIVE_LAYOUT, **DRIVE_LAYOUT_FRONTEND, **DRIVE_LAYOUT_REFERENCE, **DRIVE_LAYOUT_OPTIONAL}


def drive_folder_for_file(filename: str, mod: str) -> "str | None":
    """Which canonical folder a (V5-named) file belongs to, or None if the
    name is not a known artifact. Derived from ARTIFACT_FILES +
    FRONTEND_ARTIFACT_FILES + the platform/journey rules — never a lookup
    table of filenames."""
    if filename in PLATFORM_LEVEL_FILES:
        return DRIVE_PLATFORM_FOLDER
    if filename == ledger_filename(mod):
        return DRIVE_JOURNEY_FOLDER
    for stage, templates in {**ARTIFACT_FILES, **FRONTEND_ARTIFACT_FILES, **REFERENCE_FILES}.items():
        for t in templates:
            if resolve_filename(t, mod) == filename and t not in PLATFORM_LEVEL_FILES:
                return all_drive_stages()[stage][0]
    return None


def drive_module_root(ctx: str, mod: str, version: int = 1) -> str:
    """[CTX]/[Module]/ (v1) or [CTX]/[Module]/v{N}/ — string path template."""
    base = f"{ctx.rstrip('/')}/{mod.upper()}"
    return base if version == 1 else f"{base}/v{version}"


def drive_expected_tree(ctx: str, mod: str, version: int = 1) -> list[str]:
    """Every folder that must exist for a module version (mkdir plan)."""
    root = drive_module_root(ctx, mod, version)
    folders = [f"{ctx.rstrip('/')}/{DRIVE_PLATFORM_FOLDER}",
               f"{ctx.rstrip('/')}/{mod.upper()}/{DRIVE_JOURNEY_FOLDER}"]
    seen = set()
    for _k, (folder, _w, _r) in all_drive_stages().items():
        if folder not in seen:
            seen.add(folder); folders.append(f"{root}/{folder}")
    return folders


# ─────────────────────────────────────────────
# REFERENCE INGEST (AMEND-PIPELINE-V5 §1F) — UI Shell + API Docs are uploaded
# ONCE per module VERSION and then read by every session. Rules the engine and
# tools share:
#   • location  : [CTX]/[Module][/vN]/_ref/{ui-shell|api-docs}/<file>  (§1E folder)
#   • one live copy per version: a re-upload REPLACES the old file in place
#     (same governed path) and SUPERSEDES its ledger row — never a second copy.
#   • a NEW IFA version (vN) starts empty _ref/: the engine copies the prior
#     version's references forward (carry_forward) unless a fresh one is
#     supplied, so vN is self-contained and vN-1 stays frozen.
# ─────────────────────────────────────────────

def reference_targets(mod: str, version: int, ctx: str = "[CTX]") -> dict:
    """{'REF_SHELL': (folder_path, filename), 'REF_APIDOCS': (…)} for a version."""
    root = drive_module_root(ctx, mod, version)
    out = {}
    for key, tmpls in REFERENCE_FILES.items():
        folder = f"{root}/{DRIVE_LAYOUT_REFERENCE[key][0]}"
        out[key] = (folder, resolve_filename(tmpls[0], mod))
    return out


def reference_ledger_row(engine: str, key: str, mod: str, drive_file_id: str,
                         drive_url: str = None, recorded_at: str = None) -> dict:
    """A §1D.3 row for a reference file (Drive-hosted, so drive_file_id)."""
    folder, filename = DRIVE_LAYOUT_REFERENCE[key][0], resolve_filename(REFERENCE_FILES[key][0], mod)
    return {"engine": engine, "stage": folder, "filename": filename,
            "artifact": f"reference/{key.lower()}", "drive_file_id": drive_file_id,
            "drive_url": drive_url, "recorded_at": recorded_at, "status": "UPLOADED"}
