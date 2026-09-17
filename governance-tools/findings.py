"""
findings — the one finding record every checker reports through
===============================================================
`Finding` is a value, not a checker: it names a severity (a rank in
factory.yaml → `analyze.severities`), the rule that fired, where, and why.

It lives on its own because two checkers need it and neither is the other's
parent. `lint` owns the Constitution rules; `render` owns the templating
engine and reports one rule of its own (`C1-stale-render`). Keeping the record
inside `lint` forced `render` to import `lint` for a ten-line dataclass while
`lint` imported `render` to run that check — a cycle, held open only by two
lazy imports that had to explain each other in comments.

Same cut as `contracts.py`: the shared value moves to a module with one
dependency, and `lint` re-exports it, so no caller changes.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    severity: str          # one of factory.yaml → analyze.severities
    rule: str
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        return f"[{self.severity}] {self.rule} {loc} — {self.message}"
