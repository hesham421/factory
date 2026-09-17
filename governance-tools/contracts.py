"""
contracts — the contract document, read as data
===============================================
`shared/ARTIFACT-CONTRACTS.md` carries the contract set in its frontmatter: who
owns each interface, who consumes it, and the clauses `analyze` evaluates.

This lived in `render.py` because the contracts-index RENDER block needed it,
and everyone else followed it there — so `analyze` (the checker) and `dispatch`
(the brief builder) each imported the whole templating engine to reach two
functions, neither of them rendering anything. Reading a document is not
rendering one; the two concerns only shared a module.

Depends on `config` alone. `render` now depends on THIS, not the reverse.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from config import FactoryConfig

_CONTRACTS_FILE = "ARTIFACT-CONTRACTS.md"       # the one filename this module must know
_FRONTMATTER_RX = re.compile(r"^---\n(.*?)\n---\n", re.S)


def contracts_path(cfg: FactoryConfig) -> Path:
    """The contract document itself — addressed here so no second reader (analyze's
    provenance digest) has to spell the filename a second time."""
    return cfg.dir("shared") / _CONTRACTS_FILE


def contracts_from_doc(cfg: FactoryConfig) -> list[dict]:
    path = contracts_path(cfg)
    if not path.exists():
        return []
    m = _FRONTMATTER_RX.match(path.read_text(encoding="utf-8"))
    return (yaml.safe_load(m.group(1)) or {}).get("contracts", []) if m else []
