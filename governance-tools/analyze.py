"""
gov.py analyze — mechanical cross-artifact consistency check (blueprint §6.4)
=============================================================================
Implements every clause of shared/ARTIFACT-CONTRACTS.md (front-matter
`contracts:`), against the module's generated current state (`_state/`).
Clause vocabulary (§13 of that file):
  exists · no-questions · languages · ids-owned · ids-continue · traces · orphans
  · ears · registry-agree · markers · manifest · gate-approved
  · value-agreement · code-format · data-source · xref-resolve · refs-exist · paths-resolve

The first group checks that a reference is SHAPED right; the second that it
RESOLVES — that two artifacts agree on a value, that a declared format describes
the values actually emitted, that a cited file exists, that an id of another
module is defined in that module, that a generated path points at something, and
that a rule has a source for the data it reads. A check that only ever passes is
worse than no check: it transfers false confidence to whoever reads the report.

A gate cannot open with a finding at a blocking severity (factory.yaml →
analyze.blocking — one declaration, read here and by gov.py). The report is written to
`paths.module.analyze_report` inside `_state/`, prose and JSON side by side, so a
pipeline can gate on the JSON instead of reading a paragraph.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from config import CFG, Artifact, Stage
import idmodel
import render
import state as st_mod
from toolkit import markers as mk
# `sev_at_rank(n)` — the severity at rank n of factory.yaml → analyze.severities
# (0 = most severe). Aliased because every clause function below takes the
# severity it is charged with in a parameter named `sev`.
from toolkit.common import (blocking_severities, blocks, counts_line, known_severity,
                            now_iso, read_json, sev as sev_at_rank, severities, severity_rank)


@dataclass
class Finding:
    severity: str
    clause: str
    check: str
    message: str
    artifact: str = ""
    line: int = 0

    def __str__(self) -> str:
        loc = f" {self.artifact}:{self.line}" if self.artifact and self.line else (f" {self.artifact}" if self.artifact else "")
        return f"[{self.severity}] {self.clause} ({self.check}){loc} — {self.message}"


@dataclass
class AnalyzeReport:
    mod: str
    version: int
    scope: str
    contracts: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)
    coverage: dict = field(default_factory=dict)     # clause id -> subjects examined
    clause_checks: dict = field(default_factory=dict)  # clause id -> check name

    def vacuous(self) -> list[str]:
        """Clauses that ran and examined NOTHING.

        A check reporting no finding over zero subjects is indistinguishable, in
        every output this tool produces, from one reporting no finding over five
        hundred. That is the shape behind every defect this file has had to grow a
        guard for: `verify` called an empty digest compare ok, a plan with no phase
        block split "successfully", and a DTO column resolved four wrong names by
        substring. Zero is not always wrong — a ROOT module really does own no
        cross-module id — but it is never something a reader should have to
        reconstruct. Listed, always; judged by the reader."""
        return sorted(k for k, v in self.coverage.items() if v == 0)

    def count(self, severity: str) -> int:
        return sum(1 for f in self.findings if f.severity == severity)

    @property
    def clean(self) -> bool:
        """No finding at a severity `factory.yaml → analyze.blocking` declares.
        The threshold is config, not code: a MAJOR that blocks nothing is how
        four findings naming a defect by line number were written down and shipped."""
        return not blocks(self.findings)

    def counts(self) -> dict:
        return {k: self.count(k) for k in severities()}


# ── context helpers ─────────────────────────────────────────────────────────

class Ctx:
    def __init__(self, mod: str, version: int):
        self.mod = mod.upper()
        self.version = version
        self._report: "AnalyzeReport | None" = None    # set by run(); read by deferred clauses
        self._examined = 0                             # subjects the running clause has looked at
        self._texts: dict[str, str | None] = {}
        self._arts: dict[str, tuple[Stage, Artifact]] = {}
        for s in CFG.all_stages():
            for a in s.produces:
                self._arts[a.artifact] = (s, a)

    def saw(self, n: int) -> None:
        """A check calls this with the number of subjects it actually examined.
        `_evaluate` reads it per clause; see AnalyzeReport.vacuous()."""
        self._examined += int(n)

    def artifact(self, name: str) -> tuple[Stage, Artifact] | None:
        return self._arts.get(name)

    def report_findings(self) -> list[Finding]:
        """What the run has produced SO FAR. Only a clause marked `reads_report`
        sees this, and run() evaluates those last — a clause that judges the run's
        own findings must not run before the clauses that produce them."""
        return list(self._report.findings) if self._report else []

    def known_names(self) -> list[str]:
        """Every name this context can resolve a text for — the stage artifacts, the
        fetched inputs and the change manifest. Derived from the config, so no list
        of artifact names is spelled anywhere."""
        return list(self._arts) + list(CFG.inputs) + [self.change_manifest_name()]

    def resolvable(self) -> list[str]:
        """The names that actually have content right now (forces the reads)."""
        return sorted(n for n in self.known_names() if self.text(n) is not None)

    def consumed(self) -> dict[str, str]:
        """Digest of every artifact this context has READ — derived from the cache,
        never from a list of names somebody has to keep in step with the contracts.
        A verdict is only about the bytes it was computed over."""
        return {n: _sha(t) for n, t in sorted(self._texts.items()) if t is not None}

    def digest_of(self, names) -> dict[str, str]:
        """Digest exactly these names, reading whatever has not been read yet."""
        for n in names:
            self.text(n)
        return {n: _sha(t) for n in names if (t := self._texts.get(n)) is not None}

    def text(self, name: str) -> str | None:
        if name not in self._texts:
            if name in CFG.inputs:
                self._texts[name] = self.input_text(name)
            elif name == self.change_manifest_name():
                p = CFG.version_root(self.mod, self.version) / CFG.paths["module"]["change_manifest"]
                self._texts[name] = p.read_text(encoding="utf-8") if p.exists() else None
            else:
                self._texts[name] = st_mod.state_text(self.mod, self.version, name)
        return self._texts[name]

    def input_text(self, name: str) -> str | None:
        spec = CFG.inputs[name]
        p = CFG.inputs_dir(self.mod, self.version) / CFG.fmt(spec["file"], mod=self.mod)
        return p.read_text(encoding="utf-8") if p.exists() else None

    @staticmethod
    def change_manifest_name() -> str:
        return Path(CFG.paths["module"]["change_manifest"]).stem

    def stage_texts(self, stage_id: str) -> dict[str, str]:
        s = CFG.stage(stage_id)
        return {a.artifact: t for a in s.produces if (t := self.text(a.artifact)) is not None}

    def all_texts(self) -> dict[str, str]:
        return {n: t for n in self._arts if (t := self.text(n)) is not None}

    def is_registry(self, name: str) -> bool:
        a = self.artifact(name)
        return bool(a and a[1].registry)

    def owner_of(self, prefix: str) -> str | None:
        return (CFG.id_atoms().get(prefix) or {}).get("owner")

    def records_of(self, prefix: str) -> list[idmodel.Record]:
        """Definitions of an atom across the module: registries never define; a marker block
        defines its atom only inside an artifact of the atom's owning stage (else it is a reference).

        Within ONE artifact every statement of an id is one record. An atom block is
        written as a marker START immediately followed by the heading that repeats
        the id, which parses as two definitions — the first ending where the second
        begins, so its body is the marker line and nothing else. Every check that
        reads a record's text (orphans, data-source, traces) then saw an empty
        block: a query cited inside an endpoint was invisible to the clause asking
        whether anything cited it. Across artifacts the first still wins — the
        upstream artifact governs, and a downstream restatement is a reference."""
        out = []
        for name, t in self.all_texts().items():
            if self.is_registry(name):
                continue
            stage = self.artifact(name)[0].id if self.artifact(name) else None
            per: dict[str, idmodel.Record] = {}
            for r in idmodel.by_prefix(idmodel.records(t), prefix):
                if r.via_marker and self.owner_of(prefix) not in (stage, "any"):
                    continue
                if r.id in per:
                    prev = per[r.id]
                    prev.text = prev.text + "\n" + r.text
                    prev.traces = list(dict.fromkeys(prev.traces + r.traces))
                else:
                    per[r.id] = r
            out += per.values()
        seen, uniq = set(), []
        for r in out:
            if r.id not in seen:
                seen.add(r.id); uniq.append(r)
        return uniq

    def when(self, expr: str | None) -> bool:
        if not expr:
            return True
        e = expr.strip()
        m = re.fullmatch(r"version\s*(>|>=|==|<)\s*(\d+)", e)
        if m:
            op, n = m.group(1), int(m.group(2))
            return {">": self.version > n, ">=": self.version >= n, "==": self.version == n, "<": self.version < n}[op]
        if e.startswith("profile."):
            return bool(CFG.profile.get(e[len("profile."):]))
        return True


# ── clause implementations ──────────────────────────────────────────────────

def _c_exists(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    a = c.get("artifact") or c.get("input")
    if not ctx.when(c.get("when")):
        return []
    t = ctx.text(a)
    if t is None or not t.strip():
        return [Finding(sev, "", "exists", f"`{a}` is missing or empty", a)]
    return []


def _targets(ctx: Ctx, c: dict) -> dict[str, str]:
    if c.get("stage"):
        return ctx.stage_texts(c["stage"])
    a = c.get("artifact")
    t = ctx.text(a)
    return {a: t} if t is not None else {}


def _c_no_questions(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    out = []
    for name, t in _targets(ctx, c).items():
        for ln in idmodel.questions(t):
            out.append(Finding(sev, "", "no-questions", "unresolved question / open dialogue marker", name, ln))
    return out


def _script_present(text: str, lang: str) -> bool:
    if lang == "en":
        return bool(re.search(r"[A-Za-z]{3,}", text))
    if lang == "ar":
        return bool(re.search(r"[؀-ۿ]{2,}", text))
    if lang in ("fr", "de", "es", "it", "pt", "nl", "tr"):
        return bool(re.search(r"[A-Za-z]{3,}", text))
    if lang in ("ru", "uk"):
        return bool(re.search(r"[Ѐ-ӿ]{2,}", text))
    if lang in ("zh", "ja"):
        return bool(re.search(r"[一-鿿]", text))
    return True   # unknown code: not checked


def _c_languages(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    langs = CFG.profile.languages
    if not langs.get("require_all"):
        return []
    out = []
    for name, t in _targets(ctx, c).items():
        for lang in langs["all"]:
            if not _script_present(t, lang):
                out.append(Finding(sev, "", "languages", f"language `{lang}` not present (profile requires all of {langs['all']})", name))
    return out


def _exempt_prefixes() -> set[str]:
    return {k for k, v in CFG.id_atoms().items() if v.get("owner") in ("any", "versioning")}


def _c_ids_owned(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    out = []
    if c.get("stage"):
        allowed = set(CFG.stage(c["stage"]).owns_ids)
        texts = ctx.stage_texts(c["stage"])
    else:
        allowed = set(c.get("defines") or [])
        t = ctx.text(c["artifact"])
        texts = {c["artifact"]: t} if t is not None else {}
    allowed |= _exempt_prefixes()
    for name, t in texts.items():
        if ctx.is_registry(name):
            continue
        for r in idmodel.records(t):
            if r.prefix in allowed:
                continue
            # restating an upstream ID (marker block or heading) is a REFERENCE; minting one that no owner defines is the violation
            if r.id in {x.id for x in ctx.records_of(r.prefix)}:
                continue
            out.append(Finding(sev, "", "ids-owned", f"`{r.id}` minted here but `{r.prefix}` is owned by `{ctx.owner_of(r.prefix)}` and that stage never defined it", name, r.line))
    return out


def _c_ids_continue(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    out = []
    prefixes = list(CFG.stage(c["stage"]).owns_ids) if c.get("stage") else [p for p in CFG.id_atoms() if p not in _exempt_prefixes()]
    for pfx in prefixes:
        recs = ctx.records_of(pfx)
        if not recs:
            continue
        seqs = sorted({r.seq for r in recs})
        expected = list(range(1, seqs[-1] + 1))
        if seqs != expected:
            missing = sorted(set(expected) - set(seqs))
            out.append(Finding(sev, "", "ids-continue", f"`{pfx}` sequence has gaps: missing {missing[:10]}", ""))
        dup = [r.id for r in recs]
        if len(dup) != len(set(dup)):
            out.append(Finding(sev, "", "ids-continue", f"`{pfx}` has duplicate definitions", ""))
    if ctx.version > 1:
        man = st_mod.read_change_manifest(ctx.mod, ctx.version)
        base_max: dict[str, int] = {}
        for v in range(1, ctx.version):
            for s in CFG.all_stages():
                for a in s.produces:
                    p = CFG.artifact_path(ctx.mod, s.id, a.artifact, v) if not a.dir else None
                    if p and p.exists():
                        for r in idmodel.records(p.read_text(encoding="utf-8")):
                            base_max[r.prefix] = max(base_max.get(r.prefix, 0), r.seq)
        modified = {i for art in man["artifacts"].values() for i in art.get("MODIFIED", [])}
        modified_all = {art for art, rows in man["artifacts"].items() if "all" in [x.lower() for x in rows.get("MODIFIED", [])]}
        for s in CFG.all_stages():
            for a in s.produces:
                if a.dir:
                    continue
                p = CFG.artifact_path(ctx.mod, s.id, a.artifact, ctx.version)
                if not p.exists() or a.registry or a.artifact in modified_all:
                    continue
                # baseline record texts (highest previous version that has the artifact)
                base_recs: dict[str, str] = {}
                for v in range(1, ctx.version):
                    bp = CFG.artifact_path(ctx.mod, s.id, a.artifact, v)
                    if bp.exists():
                        base_recs.update({r.id: r.text.strip() for r in idmodel.records(bp.read_text(encoding="utf-8"))})
                for r in idmodel.records(p.read_text(encoding="utf-8")):
                    if r.seq <= base_max.get(r.prefix, 0) and r.id not in modified and r.prefix not in _exempt_prefixes():
                        if base_recs.get(r.id) == r.text.strip():
                            continue      # identical restatement of an unchanged record — allowed
                        out.append(Finding(sev, "", "ids-continue", f"`{r.id}` re-defined with different content in v{ctx.version} but not listed as MODIFIED (sequences must continue after v{ctx.version-1})", a.artifact, r.line))
    return out


def _c_traces(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    out = []
    mn = int(c.get("min", 1))
    frm = c["from"]
    art = ctx.artifact(frm)
    if art and c.get("blocks"):                       # marker blocks of an artifact
        s, a = art
        t = ctx.text(frm)
        if t is None:
            return [Finding(sev, "", "traces", f"`{frm}` missing", frm)]
        res = mk.parse_structure(t, a.track, a.plan)
        ctx.saw(sum(1 for b in res.blocks() if b.kind in c["blocks"]))
        for b in res.blocks():
            if b.kind in c["blocks"] and len(b.traces) < mn:
                out.append(Finding(sev, "", "traces", f"block `{b.kind}:{b.id}` carries {len(b.traces)} trace(s), needs ≥{mn}", frm, b.start_line))
        return out
    if art and c.get("defined_in"):                    # every cited ID of kind `to` must be defined in that artifact/input
        t = ctx.text(frm) or ""
        defs = set()
        src = ctx.text(c["defined_in"])
        if src is not None:
            defs = idmodel.defined_ids(src) | idmodel.referenced_ids(src)
        for kind in c["to"]:
            cited = sorted({x for x in idmodel.find_ids(t) if idmodel.split_id(x)[0] == kind})
            ctx.saw(len(cited))
            for rid in cited:
                if rid not in defs:
                    out.append(Finding(sev, "", "traces", f"`{rid}` cited in `{frm}` is not defined in `{c['defined_in']}`", frm))
        return out
    # from = an ID kind — mode "all" (default): every listed kind needs its own ≥min;
    # mode "any": ≥min in at least one listed kind (e.g. a TC may trace to AC, XM or UXD)
    mode = c.get("mode", "all")
    ctx.saw(len(ctx.records_of(frm)))
    for r in ctx.records_of(frm):
        counts = {kind: sum(1 for x in r.traces if idmodel.split_id(x) and idmodel.split_id(x)[0] == kind) for kind in c.get("to", [])}
        if mode == "any":
            if counts and not any(n >= mn for n in counts.values()):
                out.append(Finding(sev, "", "traces", f"`{r.id}` traces to none of {list(counts)} (needs ≥{mn} in at least one)", "", r.line))
        else:
            for kind, n in counts.items():
                if n < mn:
                    out.append(Finding(sev, "", "traces", f"`{r.id}` traces to {n} `{kind}` id(s), needs ≥{mn}", "", r.line))
    return out


def _c_orphans(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    out = []
    mn = int(c.get("min", 1))
    kind = c["kind"]
    refby = c["referenced_by"]
    targets = ctx.records_of(kind)
    ctx.saw(len(targets))
    # collectors: records of the listed kinds (their traces + mentions) and texts of listed artifacts
    kind_recs = [r for k in refby if not ctx.artifact(k) and k not in CFG.inputs for r in ctx.records_of(k)]
    art_texts = [ctx.text(k) or "" for k in refby if ctx.artifact(k) or k in CFG.inputs]
    for t in targets:
        n = sum(1 for r in kind_recs if t.id in r.traces or t.id in r.text)
        n += sum(1 for at in art_texts if t.id in at)
        if n < mn:
            out.append(Finding(sev, "", "orphans", f"`{t.id}` is referenced by {n} of {refby}, needs ≥{mn}", "", t.line))
    return out


_STATEMENT = re.compile(r"^\s*\**Statement\**\s*:\s*(.+)$", re.I)


def _c_ears(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    pats = [re.compile(p) for p in CFG.ids["ears"]["patterns"].values()]
    out = []
    ctx.saw(len(ctx.records_of(c["kind"])))
    for r in ctx.records_of(c["kind"]):
        stmt = None
        for ln in r.text.splitlines():
            m = _STATEMENT.match(ln)
            if m:
                stmt = m.group(1).strip().strip("[]")
                break
        if stmt is None:
            first = r.text.splitlines()[0]
            stmt = re.sub(r"^.*?" + re.escape(r.id) + r"\s*(—|-|:)?\s*", "", first).strip()
        if not any(p.search(stmt) for p in pats):
            out.append(Finding(sev, "", "ears", f"`{r.id}` statement matches no EARS pattern: “{stmt[:80]}”", "", r.line))
    return out


def _categories() -> set[str]:
    doc = CFG.dir("shared") / "REGISTRY-SCHEMA.md"
    if not doc.exists():
        return set()
    return set(re.findall(r"\bCAT-\d+\b", doc.read_text(encoding="utf-8")))


def _c_registry_agree(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    out = []
    reg = ctx.text(c["registry"])
    if reg is None:
        return [Finding(sev, "", "registry-agree", f"registry `{c['registry']}` missing", c["registry"])]
    if c.get("categories") == "all":
        cats = _categories()
        ctx.saw(len(cats))       # this branch examines categories, not ids
        missing = sorted(x for x in cats if x not in reg)
        if missing:
            out.append(Finding(sev, "", "registry-agree", f"registry does not map categories {missing}", c["registry"]))
        return out
    names = c["artifact"] if isinstance(c["artifact"], list) else [c["artifact"]]
    texts = {n: ctx.text(n) for n in names}
    missing = [n for n, t in texts.items() if t is None]
    if missing:
        return [Finding(sev, "", "registry-agree", f"artifact `{n}` missing", n) for n in missing]
    kinds = set(c.get("kinds", []))

    def mine(x: str) -> bool:
        """This module's own id. A registry also records what the module CONSUMES —
        ids another module defines — and those are that module's to define, not this
        one's: resolving them here would demand every foreign entity be redefined
        locally. `xref-resolve` is what resolves them, against their owner."""
        parts = idmodel.split_id(x)
        return bool(parts) and parts[0] in kinds and parts[1] == ctx.mod

    in_art: set[str] = set()
    for n, art in texts.items():
        in_art |= {x for x in (idmodel.defined_ids(art) | idmodel.marker_ids(art) | (idmodel.referenced_ids(art) if n in CFG.inputs else set())) if mine(x)}
    label = "+".join(names)
    c = dict(c, artifact=label)
    in_reg = {x for x in idmodel.referenced_ids(reg) if mine(x)}
    ctx.saw(len(in_art | in_reg))
    direction = c.get("direction", "both")
    if direction in ("both", "artifact→registry"):
        for x in sorted(in_art - in_reg):
            out.append(Finding(sev, "", "registry-agree", f"`{x}` defined in `{c['artifact']}` but absent from `{c['registry']}`", c["artifact"]))
    if direction in ("both", "registry→artifact"):
        for x in sorted(in_reg - in_art):
            out.append(Finding(sev, "", "registry-agree", f"`{x}` registered in `{c['registry']}` but not defined in `{c['artifact']}`", c["registry"]))
    return out


def _c_markers(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    t = ctx.text(c["artifact"])
    if t is None:
        return [Finding(sev, "", "markers", f"`{c['artifact']}` missing", c["artifact"])]
    res = mk.parse(t, c["track"], c["plan"])
    out = []
    for f in res.findings:
        # the parser's own severity stands; one it does not declare is charged a
        # rank down from the top rather than silently dropped
        s = f.severity if known_severity(f.severity) else sev_at_rank(1)
        out.append(Finding(s, "", "markers", f"{f.rule}: {f.message}", c["artifact"], f.line))
    return out


def _c_manifest(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    if ctx.version <= 1:
        return []
    man = st_mod.read_change_manifest(ctx.mod, ctx.version)
    out = []
    if not man["path"].exists():
        return [Finding(sev, "", "manifest", "change manifest missing for a delta version", ctx.change_manifest_name())]
    if man["type"] not in ("ADDITIVE", "BREAKING"):
        out.append(Finding(sev, "", "manifest", "Change type must be ADDITIVE or BREAKING", ctx.change_manifest_name()))
    if not man["cs"]:
        out.append(Finding(sev_at_rank(1), "", "manifest", "no change-set id stamped in the manifest", ctx.change_manifest_name()))
    for art, rows in man["artifacts"].items():
        if not ctx.artifact(art):
            out.append(Finding(sev_at_rank(1), "", "manifest", f"manifest names unknown artifact `{art}`", ctx.change_manifest_name()))
            continue
        if rows.get("REMOVED") and man["type"] != "BREAKING":
            out.append(Finding(sev, "", "manifest", f"`{art}` lists REMOVED ids but change type is not BREAKING", ctx.change_manifest_name()))
        s, a = ctx.artifact(art)
        if not a.dir and (rows.get("ADDED") or rows.get("MODIFIED")) and not CFG.artifact_path(ctx.mod, s.id, art, ctx.version).exists():
            out.append(Finding(sev, "", "manifest", f"`{art}` is ADDED/MODIFIED in the manifest but not emitted in v{ctx.version}", art))
    return out


def approval_path(mod: str, version: int, gate: str) -> Path:
    return CFG.state_dir(mod, version) / "approvals" / f"{gate}.json"


def _c_gate_approved(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    p = approval_path(ctx.mod, ctx.version, c["gate"])
    if not p.exists():
        return [Finding(sev, "", "gate-approved", f"no approval record for gate `{c['gate']}` (gov.py approve {c['gate']})", "")]
    return []


# ── resolution checks — a reference is not "present", it RESOLVES ────────────
# Everything below answers a question the shape-only clauses above cannot:
# do two artifacts AGREE on a value, does a cited path/file EXIST, does an id of
# ANOTHER module resolve in that module's own registry, does a generated rule
# have a source for the data it reads. Nothing here spells a stage id, phase key
# or ID prefix — every one arrives through the clause's `args` (C1/C2).

# A physical identifier as the target dialects write one: lower snake_case with at
# least one separator (`granted_at`), never a property name (`grantedAt`), a type
# (`TIMESTAMPTZ`), a table (`SEC_USER`) or a bare word (`now`). Read from its whole
# dotted chain, so a table qualifier keeps its column (`SEC_USER.granted_at`) while a
# config address (`profile.conventions.entity_defaults.lookup`) yields nothing.
_CHAIN = re.compile(r"(?<![A-Za-z0-9_.])([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)")
_SNAKE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$")


def _physical_names(line: str) -> set[str]:
    out: set[str] = set()
    for m in _CHAIN.finditer(line):
        parts = m.group(1).split(".")
        if len(parts) == 1 and _SNAKE.match(parts[0]):
            out.add(parts[0])                                  # a bare column
        elif len(parts) == 2 and _SNAKE.match(parts[1]) and parts[0].upper() == parts[0]:
            out.add(parts[1])                                  # TABLE.column
    return out


def _binding_lines(text: str, prefix: str) -> dict[str, set[str]]:
    """id → every physical name that appears on a line binding exactly that one id.

    A line naming two ids of the kind (a `traces=` list, an API's DBF list) binds
    none of them and is skipped; a line with no physical name binds nothing.
    """
    rx = CFG.id_regex(prefix)
    out: dict[str, set[str]] = {}
    for ln in text.splitlines():
        ids = {m.group(0) for m in rx.finditer(ln)}
        if len(ids) != 1:
            continue
        names = _physical_names(ln)
        if names:
            out.setdefault(ids.pop(), set()).update(names)
    return out


def _c_value_agreement(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """Two artifacts that both name the physical object behind an id must name the
    SAME one. `binding` is the artifact that declares it; `against` the ones that
    must agree. A transcription slip in one of them is invisible to every
    shape-only check — this is the dictionary comparison that sees it."""
    prefix = c["kind"]
    truth_name = c["binding"]
    truth_text = ctx.text(truth_name)
    if truth_text is None:
        return [Finding(sev, "", "value-agreement", f"binding artifact `{truth_name}` missing", truth_name)]
    truth = _binding_lines(truth_text, prefix)
    out = []
    for name in (c["against"] if isinstance(c["against"], list) else [c["against"]]):
        t = ctx.text(name)
        if t is None:
            continue
        for rid, names in _binding_lines(t, prefix).items():
            declared = truth.get(rid)
            if not declared:
                if c.get("require_binding"):
                    out.append(Finding(sev_at_rank(1), "", "value-agreement",
                                       f"`{rid}` names {sorted(names)} here but `{truth_name}` binds it to no physical name", name))
                continue
            if not (names & declared):
                out.append(Finding(sev, "", "value-agreement",
                                   f"`{rid}` is {sorted(names)} in `{name}` but {sorted(declared)} in `{truth_name}` — one of them is a transcription slip",
                                   name))
    return out


_HTTP_TOKEN = "{http}"


def _fmt_regex(fmt: str, mod: str) -> re.Pattern:
    """A declared code format → the regex its instances must match. Tokens:
    {MOD} module code · {http} HTTP status · {SLUG} SCREAMING-KEBAB · {seq} sequence;
    `[ … ]` wraps an optional half.

    The FIRST `{http}` slot is captured by name, so the caller can ask the second
    question the shape alone cannot answer: is that status one the platform can
    actually produce? A code shaped perfectly and raised by nothing is a catalog
    row no code path can ever reach."""
    w = int(CFG.ids["seq_width"])
    tokens = {"{MOD}": re.escape(mod), _HTTP_TOKEN: r"[1-5]\d{2}", "{SLUG}": r"[A-Z0-9]+(?:-[A-Z0-9]+)*", "{seq}": rf"\d{{{w}}}"}
    parts, i, named = [], 0, False
    while i < len(fmt):
        for tok, rx in tokens.items():
            if fmt.startswith(tok, i):
                if tok == _HTTP_TOKEN and not named:
                    rx, named = f"(?P<http>{rx})", True
                parts.append(rx)
                i += len(tok)
                break
        else:
            parts.append({"[": "(?:", "]": ")?"}.get(fmt[i], re.escape(fmt[i])))
            i += 1
    return re.compile("^" + "".join(parts) + "$")


_BACKTICKED = re.compile(r"`([^`\n]{1,80})`")


def _c_code_format(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """The format an artifact DECLARES and the values it EMITS are one fact.
    A declared shape no emitted value obeys is a stale generalisation that a
    downstream verifier built from that sentence would reject every real value of."""
    fmt = CFG.profile.get(c["format"])
    if not fmt:
        return []
    # The set of statuses the platform can EMIT — an optional convention (C5): a
    # profile that declares none has the membership half skipped, and only the
    # shape is checked. `FIN-503` matched the declared shape perfectly and was
    # struck during implementation, because the platform's status enum has no 503
    # and no code path could ever have raised that catalog row.
    statuses = {str(s) for s in (CFG.profile.get(c["statuses"]) or [])} if c.get("statuses") else set()
    out, mod = [], ctx.mod
    declared = {fmt, fmt.replace("{MOD}", mod)}
    rx = _fmt_regex(fmt, mod)
    idrx = CFG.id_regex()
    value_rx = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(mod)}-\d[A-Z0-9-]*(?![A-Za-z0-9_-])")
    for name in (c["artifact"] if isinstance(c["artifact"], list) else [c["artifact"]]):
        t = ctx.text(name)
        if t is None:
            continue
        stated = False
        for n, ln in enumerate(t.splitlines(), 1):
            for m in _BACKTICKED.finditer(ln):
                lit = m.group(1)
                if lit in declared:
                    stated = True
                    continue
                # a declaration is a code-shaped literal carrying a placeholder
                if lit.startswith(mod + "-") and ("<" in lit or "{" in lit):
                    out.append(Finding(sev, "", "code-format",
                                       f"declares the code format `{lit}` but `{c['format']}` is `{fmt}` — "
                                       f"a format string maintained as free text drifts from the values it describes", name, n))
            for m in value_rx.finditer(ln):
                val = m.group(0)
                if idrx.fullmatch(val):
                    continue
                hit = rx.match(val)
                if not hit:
                    out.append(Finding(sev, "", "code-format",
                                       f"`{val}` is not an instance of the declared format `{fmt}`", name, n))
                    continue
                status = (hit.groupdict() or {}).get("http")
                if statuses and status and status not in statuses:
                    out.append(Finding(sev, "", "code-format",
                                       f"`{val}` carries status {status}, which `{c['statuses']}` "
                                       f"does not declare ({', '.join(sorted(statuses))}) — the platform "
                                       f"cannot emit it, so no code path can ever raise this row",
                                       name, n))
        if not stated and c.get("require_declaration", True):
            out.append(Finding(sev_at_rank(2), "", "code-format",
                               f"does not state the declared code format `{fmt}` (`{c['format']}`)", name))
    return out


def _c_data_source(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """A rule the plan turns into a runtime check must say where the data the
    check READS comes from. An error-catalog row and an enforcing endpoint prove
    nothing: without a declaration surface the guard compiles and never fires."""
    label = c["label"]
    label_rx = re.compile(r"^\s*[-*]?\s*\**\s*" + re.escape(label) + r"\s*\**\s*:\s*(.+)$", re.I)
    deferral = c.get("deferral")
    resolves = set(c.get("resolves_to") or [])
    bound_text = ctx.text(c["bound_in"]) if c.get("bound_in") else None
    out = []
    for r in ctx.records_of(c["kind"]):
        line = next((m.group(1).strip() for ln in r.text.splitlines() if (m := label_rx.match(ln))), None)
        if line is None:
            out.append(Finding(sev, "", "data-source",
                               f"`{r.id}` declares no `{label}` — the data its check reads has no stated origin", "", r.line))
            continue
        if deferral and deferral in line:
            continue
        cited = [x for x in idmodel.find_ids(line) if idmodel.split_id(x) and idmodel.split_id(x)[0] in resolves]
        if not cited:
            out.append(Finding(sev, "", "data-source",
                               f"`{r.id}` has `{label}: {line[:60]}` which resolves to no {sorted(resolves)} — "
                               f"state the declared field it reads, or mark it `{deferral}`", "", r.line))
            continue
        if bound_text is not None:
            for ref in re.findall(r"(" + "|".join(re.escape(x) for x in cited) + r")\.([A-Za-z_][A-Za-z0-9_]*)", line):
                qualified = f"{ref[0]}.{ref[1]}"
                if qualified not in bound_text:
                    out.append(Finding(sev, "", "data-source",
                                       f"`{r.id}` reads `{qualified}`, which `{c['bound_in']}` binds to no field — "
                                       f"the check can never fire", "", r.line))
    return out


def _module_ids(mod: str) -> set[str]:
    """Every id the module `mod` defines or registers, across its current version."""
    out: set[str] = set()
    try:
        version = CFG.current_version(mod)
    except Exception:
        return out
    for s in CFG.all_stages():
        for a in s.produces:
            if a.dir:
                continue
            p = CFG.artifact_path(mod, s.id, a.artifact, version)
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            out |= idmodel.defined_ids(text) | idmodel.marker_ids(text)
            if a.registry:
                out |= idmodel.referenced_ids(text)
    return out


def _c_xref_resolve(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """A plan that names another module's id is depending on that module's output.
    Each module's own analyze validates only its own artifacts, so a dependency on
    an endpoint the target never generates passes both — unless it is resolved here."""
    known = set(CFG.profile.vocabulary["module_prefixes"])
    kinds = set(c.get("kinds") or [])
    cache: dict[str, set[str]] = {}
    out, seen = [], set()
    for name in (c["artifact"] if isinstance(c["artifact"], list) else [c["artifact"]]):
        t = ctx.text(name)
        if t is None:
            continue
        for n, ln in enumerate(t.splitlines(), 1):
            for rid in idmodel.find_ids(ln):
                parts = idmodel.split_id(rid)
                if not parts:
                    continue
                prefix, fmod, _ = parts
                if fmod == ctx.mod or (kinds and prefix not in kinds) or (rid, name) in seen:
                    continue
                seen.add((rid, name))
                if fmod not in known:
                    out.append(Finding(sev, "", "xref-resolve",
                                       f"`{rid}` names module `{fmod}`, which the profile's module registry does not declare", name, n))
                    continue
                if fmod not in cache:
                    cache[fmod] = _module_ids(fmod)
                if not cache[fmod]:
                    out.append(Finding(sev_at_rank(1), "", "xref-resolve",
                                       f"`{rid}` is a contract with `{fmod}`, whose artifacts do not exist yet — "
                                       f"the dependency cannot be resolved", name, n))
                elif rid not in cache[fmod]:
                    out.append(Finding(sev, "", "xref-resolve",
                                       f"`{rid}` is cited here but `{fmod}` defines no such id — "
                                       f"this plan depends on something the target module never produced", name, n))
    return out


def _locator_rx(template: str, modules) -> re.Pattern:
    """A profile's surface locator template → the regex that finds an instance of it
    naming a module. `{module}` captures a declared module code; every other `{…}`
    slot matches one path segment. Nothing about the template's shape is assumed
    beyond that: it is whatever the profile declares.
    """
    codes = "|".join(re.escape(m) for m in sorted(modules, key=len, reverse=True))
    out, i = [], 0
    while i < len(template):
        m = re.compile(r"\{([a-zA-Z_]+)\}").match(template, i)
        if m:
            out.append(f"(?P<module>{codes})" if m.group(1).lower() == "module" else r"[^/\s?#`]+")
            i = m.end()
        else:
            out.append(re.escape(template[i]))
            i += 1
    return re.compile("".join(out), re.IGNORECASE)


def _prose_scopes(text: str):
    """(line number, line, the text the line's citations may come from).

    Prose wraps: a sentence naming another module's endpoint often carries the id
    on the NEXT line. So a citation anywhere in the same paragraph counts. A table
    is the exception — each row is its own statement, and an id in a neighbouring
    row says nothing about this one — so there the scope is the row itself.
    """
    lines = text.splitlines()
    start = 0
    for i in range(len(lines) + 1):
        if i < len(lines) and lines[i].strip():
            continue
        para = lines[start:i]
        is_table = any(l.lstrip().startswith("|") for l in para)
        joined = "\n".join(para)
        for k, l in enumerate(para):
            yield start + k + 1, l, (l if is_table else joined)
        start = i + 1


def _c_xref_surface(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """A reference to another module's SURFACE, written as prose, must resolve in
    that module's own artifacts.

    `xref-resolve` sees id-shaped citations only. A plan that says it will read data
    through another module's endpoint, without an id for it, is invisible to that
    check — and prose is exactly how a module encodes a dependency it has not been
    given an id for yet. Both modules then pass, because each validates only itself.

    The locator is the profile's own address template (`locator`), so this knows no
    path, no verb and no module name; the resolution runs across the module set.
    """
    template = CFG.profile.get(c["locator"])
    if not template:
        return []
    known = set(CFG.profile.vocabulary["module_prefixes"])
    kinds = set(c.get("kinds") or [])
    rx = _locator_rx(template, known)
    cache: dict[str, set[str]] = {}
    out, seen = [], set()
    for name in (c["artifact"] if isinstance(c["artifact"], list) else [c["artifact"]]):
        text = ctx.text(name)
        if text is None:
            continue
        for n, ln, scope_text in _prose_scopes(text):
            for m in rx.finditer(ln):
                fmod = (m.groupdict().get("module") or "").upper()
                if not fmod or fmod == ctx.mod or (fmod, name, m.group(0)) in seen:
                    continue
                seen.add((fmod, name, m.group(0)))
                if fmod not in cache:
                    cache[fmod] = _module_ids(fmod)
                cited = {rid for rid in idmodel.find_ids(scope_text)
                         if (parts := idmodel.split_id(rid)) and parts[1] == fmod
                         and (not kinds or parts[0] in kinds)}
                if cited & cache[fmod]:
                    continue                    # the prose names a surface the target really defines
                if not cache[fmod]:
                    out.append(Finding(sev, "", "xref-surface",
                                       f"`{m.group(0)}` consumes `{fmod}`'s surface, but `{fmod}` has no "
                                       f"artifacts yet — the dependency cannot be resolved, and neither "
                                       f"module's own checks can see it", name, n))
                elif cited:
                    out.append(Finding(sev, "", "xref-surface",
                                       f"`{m.group(0)}` consumes `{fmod}`'s surface citing {sorted(cited)}, "
                                       f"which `{fmod}` does not define", name, n))
                else:
                    out.append(Finding(sev, "", "xref-surface",
                                       f"`{m.group(0)}` consumes `{fmod}`'s surface in prose but cites no "
                                       f"{'/'.join(sorted(kinds)) or 'id'} of `{fmod}` — a dependency with no "
                                       f"id resolves nowhere, and `{fmod}`'s own checks never see it", name, n))
    return out


def _c_refs_exist(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """Every id of `kind` cited anywhere in the module must have the file it is
    cited as. A path repeated 30 times that resolves to nothing is not a reference."""
    prefix, out = c["kind"], []
    directory = CFG.dir(c["dir"]) / ctx.mod if c.get("per_module", True) else CFG.dir(c["dir"])
    pattern = CFG.naming[c["file_pattern"]]
    for name, t in ctx.all_texts().items():
        for rid in sorted({x for x in idmodel.find_ids(t) if idmodel.split_id(x) and idmodel.split_id(x)[0] == prefix}):
            _, mod, seq = idmodel.split_id(rid)
            if mod != ctx.mod:
                continue
            f = directory / CFG.fmt(pattern, mod=mod, seq=seq)
            if not f.exists():
                out.append(Finding(sev, "", "refs-exist",
                                   f"`{rid}` is cited in `{name}` but {f.relative_to(CFG.root)} does not exist", name))
    return sorted({(f.message, f.artifact): f for f in out}.values(), key=lambda f: f.message)


def _c_paths_resolve(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """Every path a generated index emits must resolve against the tree it is
    written into. A path that resolves in the factory and nowhere else is a
    dangling pointer for every consumer of the delivered tree."""
    from toolkit.common import read_json
    out = []
    base = CFG.version_root(ctx.mod, ctx.version)
    for fname in (c["files"] if isinstance(c["files"], list) else [c["files"]]):
        path = base / CFG.paths["module"][fname] if fname in CFG.paths["module"] else base / fname
        data = read_json(path)
        if data is None:
            if c.get("required", True):
                out.append(Finding(sev, "", "paths-resolve", f"{path.name} is missing", fname))
            continue
        for key, value in _walk_paths(data):
            if not (base / value).exists():
                out.append(Finding(sev, "", "paths-resolve",
                                   f"{path.name} → `{key}` = `{value}` resolves to nothing under {base.relative_to(CFG.root)}", fname))
    return out


# ── completeness — is the planned system complete enough to function? ────────
# Every clause above asks whether a reference is SHAPED right or whether it
# RESOLVES. None asks whether what was planned is COMPLETE: whether a declared
# total matches the rows beneath it, whether a required column has anything that
# writes it, whether a declared operation has an endpoint, whether the data that
# must exist before any of it works was planned at all. A whole delivered module
# passed twenty-two checks and could not serve its first request, because that
# dimension had no clause in it.


def _kind_ids(text: str, kind: str, mod: str) -> set[str]:
    """Every id of `kind` belonging to `mod` that the text names — the row set a
    declared total is a total OF."""
    return {x for x in idmodel.find_ids(text)
            if (p := idmodel.split_id(x)) and p[0] == kind and p[1] == mod}


def _c_count_agrees(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """A total an artifact DECLARES equals the rows it heads.

    `manifest` validates a manifest's shape and `registry-agree` compares two
    registries' membership; neither ever counts. One delivered plan asserted
    "147" on one line and "146" on another for the same set, and certified both.

    The label that introduces a total, the atom its rows are keyed by and the
    artifact those rows live in are all profile data (`spec`), so this knows no
    block name and no atom of its own. Where the same total is stated in more
    than one place every statement is compared against the same row set, so they
    also have to agree with each other."""
    rows = CFG.profile.get(c["spec"]) or []
    if not rows:
        return []                       # this profile declares no total worth counting
    out = []
    for row in rows:
        text = ctx.text(row["artifact"])
        source_name = row.get("rows_in") or row["artifact"]
        source = ctx.text(source_name)
        if text is None or source is None:
            continue
        actual = len(_kind_ids(source, row["kind"], ctx.mod))
        label_rx = re.compile(re.escape(row["label"]) + r"[^\d\n]*(\d+)", re.I)
        seen = 0
        for n, ln in enumerate(text.splitlines(), 1):
            m = label_rx.search(ln)
            if not m:
                continue
            seen += 1
            declared = int(m.group(1))
            if declared != actual:
                out.append(Finding(sev, "", "count-agrees",
                                   f"`{row['label']}` declares {declared} but `{source_name}` carries "
                                   f"{actual} `{row['kind']}` row(s) — a hand-counted total drifts from "
                                   f"the rows it heads the moment one row moves, and every reader "
                                   f"downstream takes the stated number for the real one",
                                   row["artifact"], n))
        ctx.saw(seen)
    return out


def _squash(name: str) -> str:
    """A physical/logical name reduced to what two spellings of it have in common:
    camelCase, snake_case and SCREAMING_SNAKE of one name collapse to one string. A
    profile declares its platform-filled fields in the language's spelling while the
    database holds the database's; comparing the raw strings exempts neither."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _template_rx(template: str) -> re.Pattern:
    """A profile's NAME template (`{entity}Pk`, `PERM_<PAGE>_<ACTION>`) → the regex
    matching an instance of it, over squashed names. Every `{…}`/`<…>` slot matches
    one word; nothing else about the template's shape is assumed."""
    out, i = [], 0
    while i < len(template):
        m = re.compile(r"\{[^}]*\}|<[^>]*>").match(template, i)
        if m:
            out.append(r"[a-z0-9]+")
            i = m.end()
        else:
            out.append(re.escape(_squash(template[i])))
            i += 1
    return re.compile("".join(out))


def _single_id_lines(text: str, kind: str, mod: str) -> dict[str, list[tuple[int, str]]]:
    """id → the lines that name exactly that one id of `kind` and no other.

    A line naming two ids of the kind (a traces list, a range) is a statement about
    neither, so it is skipped — the same rule `_binding_lines` already uses for the
    physical-name dictionary."""
    out: dict[str, list[tuple[int, str]]] = {}
    for n, ln in enumerate(text.splitlines(), 1):
        ids = {x for x in idmodel.find_ids(ln)
               if (p := idmodel.split_id(x)) and p[0] == kind and p[1] == mod}
        if len(ids) == 1:
            out.setdefault(ids.pop(), []).append((n, ln))
    return out


def _c_required_writer(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """Data the module REQUIRES must have something that writes it.

    Both halves were already in the plan — the structural artifact declares every
    column and marks which are required, and each endpoint block lists what its
    request carries — and nothing joined them. A column added as semantically
    required that no endpoint sets can never be satisfied on a fresh deployment, so
    the endpoint depending on it fails its first call; a flag no operation flips is
    the same defect wearing a different column name. Neither is visible to any
    shape check: every id resolves, every trace lands, every registry agrees.

    The exemptions are profile facts (`exempt_names`, `exempt_pattern` — addresses,
    not lists), because a system-assigned key or an audit column is written by the
    platform and naming either here would hardcode one profile's conventions."""
    src = ctx.text(c["declared_in"])
    plan = ctx.text(c["writer_in"])
    if src is None or plan is None:
        return []
    kind, mod = c["kind"], ctx.mod
    marker_rx = re.compile(r"(?<![A-Za-z])" + re.escape(c["required_marker"]) + r"(?![A-Za-z])", re.I)
    tokens = list(c.get("exclusions") or [])
    excl_rx = re.compile("|".join(re.escape(x) for x in tokens), re.I) if tokens else None
    exempt = {_squash(x) for x in (CFG.profile.get(c["exempt_names"]) or [])} if c.get("exempt_names") else set()
    pat = CFG.profile.get(c["exempt_pattern"]) if c.get("exempt_pattern") else None
    pk_rx = _template_rx(pat) if pat else None
    labels = c["writer_labels"] if isinstance(c.get("writer_labels"), list) else [c["writer_labels"]]
    label_rx = re.compile(r"^\s*[-*]?\s*\**\s*(?:" + "|".join(re.escape(l) for l in labels) +
                          r")\s*\**\s*:\s*(.+)$", re.I)
    # what the plan WRITES: every id cited on a writing line of an endpoint block
    written: set[str] = set()
    for r in idmodel.by_prefix(idmodel.records(plan), c["writer_kind"]):
        for ln in r.text.splitlines():
            if (m := label_rx.match(ln)):
                written |= set(idmodel.find_ids(m.group(1)))
    plan_lines = _single_id_lines(plan, kind, mod)
    out, seen = [], 0
    for rid, lines in sorted(_single_id_lines(src, kind, mod).items()):
        required = [(n, ln) for n, ln in lines if marker_rx.search(ln)]
        if not required:
            continue
        names = {_squash(x) for n, ln in required for x in _physical_names(ln)}
        if names & exempt or (pk_rx and any(pk_rx.fullmatch(x) for x in names)):
            continue                       # written by the platform, not by a caller
        if excl_rx and (any(excl_rx.search(ln) for _, ln in required)
                        or any(excl_rx.search(ln) for _, ln in plan_lines.get(rid, []))):
            continue                       # an explicit, stated reason — not a silent gap
        seen += 1
        if rid not in written:
            out.append(Finding(sev, "", "required-writer",
                               f"`{rid}` is {c['required_marker']} in `{c['declared_in']}` but no "
                               f"`{c['writer_kind']}` block names it on a `{'`/`'.join(labels)}` line — "
                               f"nothing in this module writes it, so every operation that depends on it "
                               f"fails on a fresh deployment. Either an endpoint writes it, or the row "
                               f"states why not ({', '.join(tokens) or 'an exclusion token'})",
                               c["declared_in"], required[0][0]))
    ctx.saw(seen)
    return out


def _name_template_rx(template: str, **binds: str) -> re.Pattern:
    """A profile's NAME template → the regex matching an instance of it, verbatim.
    Every `{…}`/`<…>` slot matches one identifier word, except a slot whose name is
    given in `binds`, which must hold exactly that value. Nothing about the
    template's shape is assumed beyond the slot syntax — the same rule
    `_locator_rx` uses for a surface address."""
    out, i = [], 0
    while i < len(template):
        m = re.compile(r"\{([^}]*)\}|<([^>]*)>").match(template, i)
        if m:
            key = (m.group(1) if m.group(1) is not None else m.group(2)).strip().lower()
            out.append(re.escape(binds[key]) if key in binds else r"[A-Za-z0-9_]+")
            i = m.end()
        else:
            out.append(re.escape(template[i]))
            i += 1
    return re.compile(r"(?<![A-Za-z0-9_])" + "".join(out) + r"(?![A-Za-z0-9_])")


def _table_rows(text: str):
    """(line number, headers, cells) for every data row of every markdown table."""
    headers = None
    for n, ln in enumerate(text.splitlines(), 1):
        cells = _cells(ln)
        if not cells:
            headers = None
            continue
        if headers is None:
            headers = cells
            continue
        if _is_separator(cells):
            continue
        yield n, headers, cells


def _word_rx(word: str) -> re.Pattern:
    return re.compile(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", re.I)


def _c_operation_resolves(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """Every operation the plan DECLARES resolves to an endpoint — in both directions.

    The existing clauses run plan → registry only. Nothing ran the other way, and
    nothing ran the subject → endpoint direction at all: two operations were
    specified for an entity and never built (nobody could deactivate one through
    the API), and the security matrix shipped cells marked present with no endpoint
    and no permission behind them. A ✓ that grants nothing and is enforced by
    nothing is worse than a blank: it reads as a decision that was implemented.

    The operation vocabulary is a profile address (`actions`), never a list here;
    the permission name is checked against the profile's own template with the
    action slot bound, so a cell claiming an action must carry the permission for
    THAT action, not merely some permission-shaped word."""
    text = ctx.text(c["artifact"])
    if text is None:
        return []
    actions = [str(a) for a in (CFG.profile.get(c["actions"]) or [])]
    if not actions:
        return []                       # this profile declares no operation vocabulary
    kind = c["resolves_to"]
    recs = idmodel.records(text)
    endpoints = idmodel.by_prefix(recs, kind)
    out, seen = [], 0

    d = c.get("declared")
    if d:
        label_rx = re.compile(r"^\s*[-*]?\s*\**\s*" + re.escape(d["label"]) + r"\s*\**\s*:?\s*(.+)$", re.I)
        for r in idmodel.by_prefix(recs, d["kind"]):
            stated = " ".join(m.group(1) for ln in r.text.splitlines() if (m := label_rx.match(ln)))
            for a in actions:
                if not _word_rx(a).search(stated):
                    continue
                seen += 1
                if not any(r.id in e.text and _word_rx(a).search(e.text) for e in endpoints):
                    out.append(Finding(sev, "", "operation-resolves",
                                       f"`{r.id}` declares the operation `{a}` on its `{d['label']}` line "
                                       f"but no `{kind}` block names both that operation and `{r.id}` — "
                                       f"the operation was specified and never built, and no shape check "
                                       f"can see the gap because every id in both halves resolves",
                                       c["artifact"], r.line))

    mx = c.get("matrix")
    if mx:
        pattern = CFG.profile.get(mx["permission"]) if mx.get("permission") else None
        for n, headers, cells in _table_rows(text):
            row = " ".join(cells)
            for h, cell in zip(headers, cells):
                a = next((x for x in actions if x.lower() == h.strip().lower()), None)
                if a is None or mx["present"] not in cell:
                    continue
                seen += 1
                missing = []
                if not [x for x in idmodel.find_ids(row)
                        if (parts := idmodel.split_id(x)) and parts[0] == kind]:
                    missing.append(f"no `{kind}` id")
                if pattern and not _name_template_rx(pattern, action=a).search(row):
                    missing.append(f"no name matching `{pattern}` for `{a}`")
                if missing:
                    out.append(Finding(sev, "", "operation-resolves",
                                       f"the `{a}` cell is marked `{mx['present']}` but the row carries "
                                       f"{' and '.join(missing)} — a matrix cell with nothing behind it "
                                       f"grants nothing and is enforced by nothing, while reading as a "
                                       f"decision that was implemented", c["artifact"], n))
    ctx.saw(seen)
    return out


_MD_HEADING = re.compile(r"^(#{1,6})\s")


def _section(text: str, token: str) -> str | None:
    """The block of text a named section covers: from the first line carrying
    `token` to the next heading that closes it — the next heading at or above the
    token line's own level when it is a heading, the next heading of any level
    otherwise. The token is found anywhere on a line, because how an engine frames
    its sections is the engine's business, not this checker's — the same rule
    `_verdict_line` already uses to locate a self-check block."""
    rx = _token_rx(token)
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if rx.search(ln)), None)
    if start is None:
        return None
    hm = _MD_HEADING.match(lines[start])
    level = len(hm.group(1)) if hm else 0
    for j in range(start + 1, len(lines)):
        h = _MD_HEADING.match(lines[j])
        if h and (not level or len(h.group(1)) <= level):
            return "\n".join(lines[start:j])
    return "\n".join(lines[start:])


def _c_bootstrap_complete(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """The data that must EXIST before any of the planned structure or behaviour
    can work is itself planned, and covers what the other registries declare.

    The largest hole the factory had. It plans structure and it plans behaviour,
    and it had no artifact section at all for the rows a fresh deployment needs:
    the lookup values a module's own keys resolve against live in another module's
    tables, so the seeding block that only covers tables THIS script creates was
    empty and nothing anywhere ever seeded them — the first create call of the
    delivered module failed validating a code against an empty table. Registering
    a permission is not granting it, and nothing named a grant target, so every
    endpoint answered forbidden to every caller including the administrator.

    Everything is profile data (`spec`): the section token, what each item
    enumerates (a name template, or a table column), where those names are
    declared, and the word that names the source. The checker knows no item."""
    spec = CFG.profile.get(c["spec"])
    if not spec:
        return []                       # this profile declares no bootstrap data
    text = ctx.text(c["artifact"])
    if text is None:
        return []
    section = _section(text, spec["section"])
    out, seen = [], 0
    for item in (spec.get("items") or []):
        src = ctx.text(item["declared_in"])
        if src is None:
            continue
        if item.get("names"):
            pattern = CFG.profile.get(item["names"])
            if not pattern:
                continue                # an optional convention this profile does not declare (C5)
            needed = set(_name_template_rx(pattern).findall(src))
        else:
            needed = {cell.strip("`*_ ") for _, cell in _column_cells(src, item["column"])} - _EMPTY
        seen += len(needed)
        if not needed:
            continue
        if section is None:
            out.append(Finding(sev, "", "bootstrap-complete",
                               f"`{item['declared_in']}` declares {len(needed)} {item['label']}(s) but "
                               f"`{c['artifact']}` carries no `{spec['section']}` section — the module "
                               f"plans its structure and its behaviour and nothing at all about the data "
                               f"that must exist before either can work", c["artifact"]))
            continue
        for name in sorted(needed):
            line = next((ln for ln in section.splitlines() if name in ln), None)
            if line is None:
                out.append(Finding(sev, "", "bootstrap-complete",
                                   f"the {item['label']} `{name}` has no row in `{spec['section']}` — "
                                   f"nothing anywhere in the pipeline creates it, so every operation "
                                   f"that reads it fails on a fresh deployment", c["artifact"]))
            elif item["source_label"].lower() not in line.lower():
                out.append(Finding(sev, "", "bootstrap-complete",
                                   f"the {item['label']} `{name}` is listed in `{spec['section']}` but "
                                   f"names no `{item['source_label']}` — a row that says a thing is "
                                   f"needed, and not who produces it, creates nothing", c["artifact"]))
    ctx.saw(seen)
    return out


# ── forward references — a fact a stage cannot verify at its own stage ───────
# A planning stage runs before any implementation exists, so a name it invents for
# an implementation artifact is a guess. In a table of facts a guess is
# indistinguishable from a decision, and the reader has no way to tell which columns
# were derived and which were imagined. A forward-referencing cell either carries the
# agreed proposed token, or holds a value that resolves in the artifact of the later
# stage that CAN resolve it. Which columns forward-reference is a profile fact; the
# token is a factory fact; this checker knows neither.

_ROW = re.compile(r"^\s*\|(.+)\|\s*$")


def _cells(line: str) -> list[str]:
    m = _ROW.match(line)
    return [c.strip() for c in m.group(1).split("|")] if m else []


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def _column_cells(text: str, column: str) -> list[tuple[int, str]]:
    """(line number, cell) for `column` in every markdown table that declares it."""
    out, idx = [], None
    lines = text.splitlines()
    for n, ln in enumerate(lines, 1):
        cells = _cells(ln)
        if not cells:
            idx = None
            continue
        if idx is None:
            idx = cells.index(column) if column in cells else None
            continue
        if _is_separator(cells):
            continue
        if idx < len(cells):
            out.append((n, cells[idx]))
    return out


_EMPTY = {"", "—", "-", "–", "n/a", "N/A", "none", "None"}


_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _names_in(value: str, source: str) -> bool:
    """Does `source` really name `value`, or does it merely contain its letters?

    A plain `value in source` passes on any substring, so a cell naming
    `RoleAssignmentRequest` resolved happily against an api-docs that defines only
    `UserRoleAssignmentRequest` — a different type, one the implementer cannot import.
    Four of SEC's twenty-seven rows were wrong that way and the column reported clean.

    Identifier-shaped values are matched on a whole-token boundary. Anything else —
    a prose cell like `paginated list of UserResponse`, or a wrapper notation — keeps
    substring semantics, because there is no token to anchor and a false negative there
    would be worse than the false positive it prevents.
    """
    value = value.strip()
    if not value:
        return True
    if _IDENTIFIER.fullmatch(value):
        return re.search(rf"(?<![A-Za-z0-9_]){re.escape(value)}(?![A-Za-z0-9_])", source) is not None
    return value in source


def _c_forward_refs(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    rows = CFG.profile.get(c["spec"]) or []
    if not rows:
        return []                            # this profile declares no forward-referencing column
    token = CFG.data["forward_reference"]["proposed_token"]
    out = []
    for row in rows:
        text = ctx.text(row["artifact"])
        if text is None:
            continue
        source = ctx.text(row["resolved_from"])
        unmarked = [(n, cell.strip("`*_ ")) for n, cell in _column_cells(text, row["column"])
                    if cell.strip("`*_ ") not in _EMPTY and token not in cell]
        if source is None:
            # nothing in this version can resolve the column, so every unmarked cell in
            # it is the same defect: ONE finding, not one per row. The count is the size
            # of the problem and the line numbers say where to start.
            if unmarked:
                where = ", ".join(str(n) for n, _ in unmarked[:5]) + (" …" if len(unmarked) > 5 else "")
                out.append(Finding(sev, "", "forward-refs",
                                   f"`{row['column']}` states {len(unmarked)} value(s) as fact "
                                   f"({', '.join(repr(v) for _, v in unmarked[:3])}…) but this stage cannot "
                                   f"resolve any of them: `{row['resolved_from']}` does not exist yet. Each "
                                   f"is a guess printed beside facts, which reads as a decision — mark them "
                                   f"`{token}` and let the stage that can resolve them fill them in. "
                                   f"Lines {where}", row["artifact"], unmarked[0][0]))
            continue
        ctx.saw(len(unmarked))
        for n, bare in unmarked:
            if not _names_in(bare.replace("\\", ""), source):
                out.append(Finding(sev, "", "forward-refs",
                                   f"`{row['column']}` names `{bare}`, which `{row['resolved_from']}` "
                                   f"does not define — either it is `{token}`, or the two disagree",
                                   row["artifact"], n))
    return out


# ── the artifact's own verdict about itself ──────────────────────────────────
# A model authors a verdict line inside the shipped artifact; the machine writes
# its own into `_state/`. Nothing compared them, and the shipped plan asserted
# zero findings over six real ones — the implementer reads the shipped plan.
#
# The preferred answer is to GENERATE the line (gov.py stamps it from the report,
# `stamp_verdict` below); this check is the guard for anything still authored by
# hand. It knows no block name, no label and no verdict wording: all five come
# from the profile address in its clause's `args`, so a profile that names its
# self-check differently — or declares none at all — is served unchanged.


def self_check_spec(address: str) -> dict | None:
    return CFG.profile.get(address) or None


def _token_rx(token: str) -> re.Pattern:
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])")


def _verdict_line(text: str, spec: dict) -> tuple[int, str] | None:
    """(line number, text) of the verdict line: the first line LABELLED
    `verdict_label` at or after the first line that names the self-check `block`.

    The block is located by its token appearing anywhere on a line — a heading, a
    fence header, a table caption — because how a profile's engine frames the block
    is the engine's business, not this checker's. The label must open its line, so a
    longer word starting with it is not mistaken for it."""
    block_rx, label_rx = _token_rx(spec["block"]), re.compile(rf"^{re.escape(spec['verdict_label'])}(\s|$)")
    seen = False
    for n, ln in enumerate(text.splitlines(), 1):
        if not seen:
            seen = bool(block_rx.search(ln))
            continue
        if label_rx.match(ln.strip()):
            return n, ln
    return None


def render_verdict(spec: dict, findings: int) -> str:
    """The verdict line's TEXT for a given finding count — one function, used both
    to write the line (gov.py) and to judge one that was written by hand."""
    token = spec["pass_token"] if findings == 0 else spec["fail_token"]
    return f"{token} — {findings} {spec['findings_noun']}"


def claimed_findings(line: str, spec: dict) -> int | None:
    """How many findings the line claims. A pass token with no number claims none;
    a line stating neither a number nor the pass token claims nothing knowable."""
    body = line.strip()[len(spec["verdict_label"]):]
    m = re.search(r"(\d+)", body)
    if m:
        return int(m.group(1))
    return 0 if spec["pass_token"].split()[0] in body else None


def _c_verdict_agrees(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """An artifact may not assert a verdict about itself that claims fewer findings
    than the machine produced for it."""
    spec = self_check_spec(c["spec"])
    if not spec:
        return []                       # this profile declares no self-check
    out = []
    for name in (c["artifact"] if isinstance(c["artifact"], list) else [c["artifact"]]):
        text = ctx.text(name)
        if text is None:
            continue
        found = _verdict_line(text, spec)
        if found is None:
            out.append(Finding(sev, "", "verdict-agrees",
                               f"`{name}` carries no `{spec['verdict_label']}` line inside its "
                               f"`{spec['block']}` block — the artifact states no verdict about itself", name))
            continue
        n, line = found
        machine = sum(1 for f in ctx.report_findings() if f.artifact == name and f.check != "verdict-agrees")
        claimed = claimed_findings(line, spec)
        if claimed is None:
            out.append(Finding(sev, "", "verdict-agrees",
                               f"the `{spec['verdict_label']}` line states no verdict this check can read "
                               f"(expected `{spec['pass_token']}`/`{spec['fail_token']}` and a count)", name, n))
        elif claimed < machine:
            out.append(Finding(sev, "", "verdict-agrees",
                               f"`{name}` claims {claimed} {spec['findings_noun']} but `gov.py analyze` "
                               f"produced {machine} for it — the artifact the implementer reads contradicts "
                               f"the report beside it. Correct line: `{render_verdict(spec, machine)}`", name, n))
    return out


_c_verdict_agrees.reads_report = True     # evaluated after every clause that PRODUCES findings


# ── a plan's endpoint assertions vs the surface that was actually published ──
# `forward-refs` guards the DTO columns of the same table and nothing guarded the
# verb or the path beside them, so a row could name the right request type on a
# verb that cannot carry one. SEC shipped five: `GET /users` with a
# `UserSearchRequest` body, against a surface that publishes `POST /users/search`.
# Self-contradictory at a glance, invisible to every clause.

_HTTP_VERB = re.compile(r"(?<![A-Za-z])(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)(?![A-Za-z])")
_URL_PATH = re.compile(r"/[A-Za-z0-9_{}][A-Za-z0-9_\-{}/.]*")
_BODYLESS = {"GET", "HEAD", "DELETE"}


def _published_endpoints(source: str) -> set[tuple[str, str]]:
    """(verb, path) of every endpoint the api-docs publish, from its own headings."""
    return {(m.group(1), m.group(2))
            for m in re.finditer(r"^#+\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/\S+)\s*$",
                                 source, re.M)}


def _c_endpoint_agrees(ctx: Ctx, c: dict, sev: str) -> list[Finding]:
    """Every (verb, path) an artifact asserts for an id of `kind` is one the
    published surface really serves.

    A path is matched by suffix, because a plan legitimately writes its paths
    relative to the module base while the api-docs write them absolute. The
    direction is one-way on purpose: the api-docs are the authority, and an
    endpoint the plan never mentions is `registry-agree`'s business, not this
    check's."""
    text = ctx.text(c["artifact"])
    source = ctx.text(c["source"])
    if text is None or source is None:
        return []                            # nothing published yet — forward-refs owns that case
    published = _published_endpoints(source)
    if not published:
        return []
    kind = c["kind"]
    out, seen = [], set()
    for n, line in enumerate(text.splitlines(), 1):
        # `parts[1] == ctx.mod` keeps this to the module whose api-docs these are:
        # a cited endpoint of ANOTHER module is that module's to publish, and
        # `xref-surface` is what resolves it against its owner.
        aids = {x for x in idmodel.find_ids(line)
                if (parts := idmodel.split_id(x)) and parts[0] == kind and parts[1] == ctx.mod}
        if len(aids) != 1:
            continue                         # a line citing several ids states no single endpoint
        aid = aids.pop()
        verbs = set(_HTTP_VERB.findall(line))
        if len(verbs) != 1:
            continue
        verb = verbs.pop()
        paths = [p for p in _URL_PATH.findall(line) if p.count("/") >= 1 and len(p) > 1]
        if not paths:
            continue
        path = max(paths, key=len)
        if (aid, verb, path) in seen:
            continue
        seen.add((aid, verb, path))
        ctx.saw(1)
        if any(v == verb and (q == path or q.endswith(path)) for v, q in published):
            continue
        served = sorted(f"{v} {q}" for v, q in published if q.endswith(path) or path.endswith(q.split("/")[-1]))
        hint = (f" — the published surface serves {', '.join('`' + s + '`' for s in served[:3])}"
                if served else " — no published endpoint matches that path at all")
        body = (" A body-carrying request type on a verb that sends no body is "
                "self-contradictory on its face." if verb in _BODYLESS and "Request" in line else "")
        out.append(Finding(sev, "", "endpoint-agrees",
                           f"`{aid}` is stated as `{verb} {path}`, which `{c['source']}` does not "
                           f"publish{hint}.{body} The published surface is the authority; correct the "
                           f"row, or record the divergence at the row rather than only in an ADR",
                           c["artifact"], n))
    return out


def _walk_paths(node, key: str = "") -> list[tuple[str, str]]:
    """Every string in a generated index that is shaped like a path."""
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out += _walk_paths(v, f"{key}.{k}" if key else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += _walk_paths(v, f"{key}[{i}]")
    elif isinstance(node, str) and node and ("/" in node or node.endswith(".md") or node.endswith(".json") or node == "."):
        out.append((key, node))
    return out


CHECKS = {
    "exists": _c_exists, "no-questions": _c_no_questions, "languages": _c_languages,
    "ids-owned": _c_ids_owned, "ids-continue": _c_ids_continue, "traces": _c_traces,
    "orphans": _c_orphans, "ears": _c_ears, "registry-agree": _c_registry_agree,
    "markers": _c_markers, "manifest": _c_manifest, "gate-approved": _c_gate_approved,
    "value-agreement": _c_value_agreement, "code-format": _c_code_format, "data-source": _c_data_source,
    "xref-resolve": _c_xref_resolve, "refs-exist": _c_refs_exist, "paths-resolve": _c_paths_resolve,
    "verdict-agrees": _c_verdict_agrees, "forward-refs": _c_forward_refs,
    "xref-surface": _c_xref_surface, "endpoint-agrees": _c_endpoint_agrees,
    "count-agrees": _c_count_agrees, "required-writer": _c_required_writer,
    "operation-resolves": _c_operation_resolves, "bootstrap-complete": _c_bootstrap_complete,
}

# Checks that report how many subjects they examined (ctx.saw). Only these appear
# in the report's coverage map: a check absent from it reported no count, which is
# different from having counted zero, and conflating the two would put noise in the
# one list that has to stay trustworthy.
for _fn in (_c_traces, _c_orphans, _c_registry_agree, _c_forward_refs,
            _c_endpoint_agrees, _c_ears, _c_count_agrees, _c_required_writer,
            _c_operation_resolves, _c_bootstrap_complete):
    _fn.counts_subjects = True


# ── provenance — a verdict is only valid under the rules that produced it ────
# A stored report used to be trusted for ever: strengthening a check invalidated
# no prior PASS, so every verdict in this factory was produced by a contract set
# that no longer exists. A report now records WHAT IT WAS PRODUCED BY, and a
# reader that finds a mismatch re-runs instead of trusting it. `analyze` is fast
# and pure, so when in doubt the safe answer is always: run it again.

def _sha(data: str | bytes) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes()) if path.exists() else ""


def rules_digest() -> dict:
    """The three things that decide a verdict independently of the artifacts:
    the contract set, the checker that implements it, and the blocking policy.
    Change any one and every stored verdict is about a rule set that is gone."""
    return {
        "contracts": _file_sha(render.contracts_path(CFG)),
        "checker": _file_sha(Path(__file__).resolve()),
        "policy": _sha(json.dumps(CFG.analyze, sort_keys=True)),
    }


def report_json_path(mod: str, version: int, scope: str) -> Path:
    tag = scope.replace(":", "-")
    md = CFG.version_root(mod, version) / CFG.fmt(CFG.paths["module"]["analyze_report"], stage=tag)
    return md.parent / f"analyze-{tag}.json"


def stale_reason(mod: str, version: int, scope: str) -> str | None:
    """Why the stored report for this scope may not be gated on — None when it may.

    Cheap first (the rules digests), then the artifacts: a stored verdict whose
    inputs have changed, or which never saw an artifact that now exists, is about
    a module that no longer exists either."""
    data = read_json(report_json_path(mod, version, scope))
    if data is None:
        return "no stored report"
    prov = data.get("provenance") or {}
    if not prov:
        return "stored report carries no provenance (produced before provenance existed)"
    now = rules_digest()
    changed = [k for k, v in now.items() if prov.get("rules", {}).get(k) != v]
    if changed:
        return f"the {', '.join(changed)} changed since the verdict was produced"
    if not st_mod.is_fresh(mod, version):
        # the module's own files moved after the state the verdict was computed over
        # was built — the digests below would compare a verdict against its own stale copy
        return "the module has changed since its current state was built"
    stored_inputs = prov.get("inputs") or {}
    ctx = Ctx(mod, version)
    live = ctx.digest_of(stored_inputs)
    differing = sorted(n for n, sha in stored_inputs.items() if live.get(n) != sha)
    if differing:
        return f"inputs changed since the verdict was produced: {differing}"
    appeared = sorted(set(ctx.resolvable()) - set(prov.get("resolvable") or []))
    if appeared:
        return f"artifacts exist now that the verdict never saw: {appeared}"
    gone = sorted(set(prov.get("resolvable") or []) - set(ctx.resolvable()))
    if gone:
        return f"artifacts the verdict was computed over are gone: {gone}"
    return None


def verdict(mod: str, version: int, scope: str, write: bool = True) -> tuple[AnalyzeReport, str | None]:
    """The report a gate may act on, plus why the stored one was refused (None when
    it was accepted). The default is always to re-run — trusting a stored verdict is
    the exception, and it has to earn it."""
    reason = stale_reason(mod, version, scope)
    if reason is None:
        return load_report(report_json_path(mod, version, scope)), None
    return run(mod, version, scope=scope, write=write), reason


def load_report(path: Path) -> AnalyzeReport:
    data = read_json(path) or {}
    rep = AnalyzeReport(data.get("module", ""), int(data.get("version", 1)), data.get("scope", ""))
    rep.contracts = list(data.get("contracts") or [])
    rep.skipped = list(data.get("skipped") or [])
    rep.provenance = data.get("provenance") or {}
    # a reloaded verdict must carry what it did NOT examine, or the signal survives
    # only until the first cache hit — which is where a silent pass would hide best.
    rep.coverage = dict(data.get("coverage") or {})
    rep.findings = [Finding(**{k: f[k] for k in ("severity", "clause", "check", "message", "artifact", "line") if k in f})
                    for f in (data.get("findings") or [])]
    return rep


# ── selection & run ─────────────────────────────────────────────────────────

def _owners(c: dict) -> list[str]:
    o = c["owner"]
    return o if isinstance(o, list) else [o]


def select_contracts(scope: str, ctx: "Ctx | None" = None) -> list[dict]:
    """scope: 'all' | 'stage:<id>' | 'pass:<n>' | 'gate:<id>'"""
    contracts = render.contracts_from_doc(CFG)
    standalone_ids = {s.id for s in CFG.standalone}
    if scope == "all":
        # the whole governed line; a standalone consumer's contract only once that stage has actually run
        def ran(sid: str) -> bool:
            if ctx is None:
                return True
            return any(ctx.text(a.artifact) for a in CFG.stage(sid).produces if not a.optional)
        return [c for c in contracts if c["consumer"] not in standalone_ids or ran(c["consumer"])]
    kind, _, val = scope.partition(":")
    if kind == "stage":
        order = {s.id: i for i, s in enumerate(CFG.all_stages())}
        standalone_ids = {s.id for s in CFG.standalone}
        out = []
        for c in contracts:
            owners = _owners(c)
            last_owner = max((o for o in owners if o in order), key=lambda o: order[o], default=None)
            is_owner_done = (val == last_owner) and c["consumer"] not in standalone_ids   # multi-owner: when the LAST owner completes
            is_standalone_consumer = (val in standalone_ids and c["consumer"] == val)
            if is_owner_done or is_standalone_consumer or c.get("owner") == "versioning":
                # a gate-approved clause belongs to the consumer's side: the owner completes BEFORE the human approves
                c2 = dict(c)
                c2["clauses"] = [cl for cl in c.get("clauses", []) if cl["check"] != "gate-approved" or c["consumer"] == val]
                out.append(c2)
        return out
    if kind in ("pass", "gate"):
        if kind == "gate":
            g = CFG.gate(val)
            val = next(k for k, p in CFG.passes.items() if g["after"] in p["stages"])
        done: list[str] = []
        for k in sorted(CFG.passes, key=int):
            if int(k) <= int(val):
                done += CFG.passes[k]["stages"]
        done += [s.id for s in CFG.stages if s.pass_ in ("pre", "bootstrap")]
        inputs = list(CFG.inputs) if int(val) >= 2 else []
        return [c for c in contracts if all(o in done or o in inputs or o == "versioning" for o in _owners(c))
                and c["consumer"] not in {s.id for s in CFG.standalone}]
    raise ValueError(f"unknown analyze scope '{scope}'")


def _evaluate(ctx: Ctx, fn, cl: dict, args: dict, rep: "AnalyzeReport | None" = None) -> list[Finding]:
    ctx._examined = 0
    try:
        fs = fn(ctx, args, cl["severity"])
    except Exception as e:  # a broken clause must be visible, never silent
        fs = [Finding(sev_at_rank(1), cl["id"], cl["check"], f"clause could not be evaluated: {e}")]
    else:
        if rep is not None:
            # only checks that report a count are tracked; one that reports none is
            # absent from coverage rather than shown as zero, so the list stays a
            # list of checks that really looked at nothing.
            if getattr(fn, "counts_subjects", False):
                rep.coverage[cl["id"]] = ctx._examined
                rep.clause_checks[cl["id"]] = cl["check"]
    for f in fs:
        f.clause = f.clause or cl["id"]
    return fs


def run(mod: str, version: int | None = None, scope: str = "all", write: bool = True) -> AnalyzeReport:
    version = CFG.current_version(mod) if version is None else int(version)
    if not st_mod.is_fresh(mod, version):
        st_mod.build_state(mod, version)
    ctx = Ctx(mod, version)
    rep = AnalyzeReport(mod.upper(), version, scope)
    ctx._report = rep
    # two passes: a clause whose check reads the run's own findings (a verdict
    # reconciliation) is evaluated after every clause that produces them. The
    # marker is an attribute on the check function, so no check name is spelled here.
    selected = select_contracts(scope, ctx)
    deferred: list[tuple[dict, dict]] = []
    for c in selected:
        rep.contracts.append(c["id"])
        for cl in c.get("clauses", []):
            fn = CHECKS.get(cl["check"])
            if fn is None:
                # a clause naming a check nobody implements would otherwise make the
                # contract look enforced while enforcing nothing — that is a finding.
                rep.skipped.append(f"{cl['id']}: unknown check {cl['check']}")
                rep.findings.append(Finding(sev_at_rank(1), cl["id"], cl["check"],
                                            f"contract clause names a check `gov.py analyze` does not implement — "
                                            f"this clause enforces nothing"))
                continue
            if not known_severity(cl["severity"]):
                # a clause charged at a severity the vocabulary does not declare is
                # charged at nothing: it can never reach `analyze.blocking`, so the
                # clause enforces nothing. Same defensive shape as the unknown check
                # above — the contract is wrong, and that is itself a top-rank finding.
                rep.skipped.append(f"{cl['id']}: unknown severity {cl['severity']}")
                rep.findings.append(Finding(sev_at_rank(0), cl["id"], cl["check"],
                                            f"contract clause declares severity `{cl['severity']}`, which "
                                            f"`factory.yaml → analyze.severities` {list(severities())} does not "
                                            f"declare — this clause can never block"))
                continue
            args = dict(cl.get("args") or {})
            if not ctx.when(args.pop("when", None)):
                continue
            if getattr(fn, "reads_report", False):
                deferred.append((cl, args))
                continue
            rep.findings += _evaluate(ctx, fn, cl, args, rep)
    for cl, args in deferred:
        rep.findings += _evaluate(ctx, CHECKS[cl["check"]], cl, args, rep)
    # the same defect reached through two clauses (an interface re-checked with a
    # stronger argument downstream) is ONE finding — reported under the first clause
    # that names it, so the count is a count of defects, not of clauses.
    seen: set[tuple] = set()
    unique = []
    for f in rep.findings:
        key = (f.severity, f.check, f.artifact, f.line, f.message)
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    rep.findings = unique
    rep.findings.sort(key=lambda f: (severity_rank(f.severity), f.clause, f.artifact, f.line))
    # `inputs` is what the clauses of THIS scope actually read (so a change to an
    # artifact this scope never looks at does not invalidate it); `resolvable` is the
    # whole set that existed, so an artifact appearing or vanishing is visible too.
    rep.provenance = {"rules": rules_digest(), "resolvable": ctx.resolvable(),
                      "inputs": ctx.consumed(), "at": now_iso()}
    if write:
        _write_report(rep)
    return rep


def _write_report(rep: AnalyzeReport) -> Path:
    tag = rep.scope.replace(":", "-")
    path = CFG.version_root(rep.mod, rep.version) / CFG.fmt(CFG.paths["module"]["analyze_report"], stage=tag)
    path.parent.mkdir(parents=True, exist_ok=True)
    c = rep.counts()
    lines = [CFG.data["lint"]["generated_marker"], f"# Analyze report — {rep.mod} v{rep.version} — scope `{rep.scope}`", "",
             f"Generated {now_iso()} · contracts {', '.join(rep.contracts) or '—'} · "
             f"**{counts_line(c)}** · blocking {sorted(blocking_severities())} · "
             f"verdict: {'CLEAN' if rep.clean else 'BLOCKED'}", ""]
    if rep.findings:
        lines += ["| Severity | Clause | Check | Artifact | Line | Finding |", "|---|---|---|---|---|---|"]
        for f in rep.findings:
            lines.append(f"| {f.severity} | {f.clause} | {f.check} | {f.artifact or '—'} | {f.line or '—'} | {f.message} |")
    else:
        lines.append("No findings.")
    if rep.skipped:
        lines += ["", "Skipped: " + "; ".join(rep.skipped)]
    if rep.coverage:
        # "no findings" over zero subjects and over five hundred printed the same
        # line until now. The count is the difference, so it is printed.
        vac = rep.vacuous()
        lines += ["", "## Coverage — subjects examined per clause", "",
                  "| Clause | Check | Examined |", "|---|---|---|"]
        by_clause = {cl: chk for cl, chk in rep.clause_checks.items()}
        for cl in sorted(rep.coverage):
            n = rep.coverage[cl]
            mark = " ⚠ nothing" if n == 0 else ""
            lines.append(f"| {cl} | {by_clause.get(cl, '—')} | {n}{mark} |")
        if vac:
            lines += ["", f"**{len(vac)} clause(s) examined nothing**: {', '.join(vac)}. "
                          "A clause with no subject is not by itself a defect — a ROOT module "
                          "really does own no cross-module id — but it enforced nothing on this "
                          "run, so its verdict is a statement about an empty set. Confirm each is "
                          "empty by nature and not because the check failed to find its subject."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # `skipped` used to reach the prose and stop there, so a programmatic reader
    # could not see that a clause never ran; `provenance` says what the verdict
    # was produced by, so a reader can tell whether it still applies (F2).
    (path.parent / f"analyze-{tag}.json").write_text(json.dumps(
        {"module": rep.mod, "version": rep.version, "scope": rep.scope, "counts": c, "clean": rep.clean,
         "blocking": sorted(blocking_severities()), "contracts": rep.contracts, "skipped": rep.skipped,
         "coverage": rep.coverage, "vacuous": rep.vacuous(),
         "findings": [f.__dict__ for f in rep.findings], "provenance": rep.provenance}, indent=2), encoding="utf-8")
    return path
