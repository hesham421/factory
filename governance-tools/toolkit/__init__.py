"""
governance-tools/toolkit — the ONE profile-driven toolkit (blueprint v6, C4)
============================================================================
Replaces the two duplicated per-track toolsets. Every name it uses comes
from factory.yaml (`CFG`) and the active profile:

    markers.parse / validate / safe_autofix   marker grammar + phase vocabulary
    structure.ensure_structure                stage + package folders, manifest.json
    archive.archive                           artifacts → stage folders
    splitter.split / verify                   plan → package files (+ index, digest check)

Standalone CLIs (run from governance-tools/):
    python -m toolkit.structure --module ORG [--version N] [--dry-run]
    python -m toolkit.archive   --module ORG --source DIR [--version N] [--dry-run] [--force]
    python -m toolkit.splitter  --module ORG --track backend --plan exec
                                [--version N] [--dry-run] [--strict] [--fix-safe] [--validate-only FILE]
"""
from __future__ import annotations

import sys
from pathlib import Path

# `config` lives one level up (governance-tools/); make it importable when the
# package is run as `python -m toolkit.<module>` from elsewhere.
_TOOLS_DIR = str(Path(__file__).resolve().parent.parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# CAUTION: `archive` is BOTH a submodule of this package and a function exported
# here, and the function wins — binding it on the package shadows the submodule,
# so even `import toolkit.archive as m` hands back the function and
# `m.archive(...)` raises AttributeError (gov.py fell into exactly that trap).
# Import the FUNCTION from its own path — `from toolkit.archive import archive` —
# and never assume `toolkit.archive` is the module. `split` / `verify` /
# `ensure_structure` are safe because their names differ from their submodules'.
from .archive import ArchiveReport, archive                                   # noqa: E402
from .markers import (AutofixReport, Block, Finding, Grammar, ParseResult,     # noqa: E402
                      parse, parse_structure, safe_autofix, validate)
from .splitter import SplitReport, split, verify                              # noqa: E402
from .structure import (build_manifest, ensure_structure, load_manifest,      # noqa: E402
                        planned_folders, set_status, write_manifest)

__all__ = [
    "ArchiveReport", "archive",
    "AutofixReport", "Block", "Finding", "Grammar", "ParseResult", "parse", "parse_structure", "safe_autofix", "validate",
    "SplitReport", "split", "verify",
    "build_manifest", "ensure_structure", "load_manifest", "planned_folders", "set_status", "write_manifest",
]
