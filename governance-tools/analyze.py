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
                            now_iso, sev as sev_at_rank, severities, severity_rank)


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
        self._texts: dict[str, str | None] = {}
        self._arts: dict[str, tuple[Stage, Artifact]] = {}
        for s in CFG.all_stages():
            for a in s.produces:
                self._arts[a.artifact] = (s, a)

    def artifact(self, name: str) -> tuple[Stage, Artifact] | None:
        return self._arts.get(name)

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
        defines its atom only inside an artifact of the atom's owning stage (else it is a reference)."""
        out = []
        for name, t in self.all_texts().items():
            if self.is_registry(name):
                continue
            stage = self.artifact(name)[0].id if self.artifact(name) else None
            for r in idmodel.by_prefix(idmodel.records(t), prefix):
                if r.via_marker and self.owner_of(prefix) not in (stage, "any"):
                    continue
                out.append(r)
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
            for rid in sorted({x for x in idmodel.find_ids(t) if idmodel.split_id(x)[0] == kind}):
                if rid not in defs:
                    out.append(Finding(sev, "", "traces", f"`{rid}` cited in `{frm}` is not defined in `{c['defined_in']}`", frm))
        return out
    # from = an ID kind — mode "all" (default): every listed kind needs its own ≥min;
    # mode "any": ≥min in at least one listed kind (e.g. a TC may trace to AC, XM or UXD)
    mode = c.get("mode", "all")
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
    in_art: set[str] = set()
    for n, art in texts.items():
        in_art |= {x for x in (idmodel.defined_ids(art) | idmodel.marker_ids(art) | (idmodel.referenced_ids(art) if n in CFG.inputs else set())) if idmodel.split_id(x)[0] in kinds}
    label = "+".join(names)
    c = dict(c, artifact=label)
    in_reg = {x for x in idmodel.referenced_ids(reg) if idmodel.split_id(x)[0] in kinds}
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


def _fmt_regex(fmt: str, mod: str) -> re.Pattern:
    """A declared code format → the regex its instances must match. Tokens:
    {MOD} module code · {http} HTTP status · {SLUG} SCREAMING-KEBAB · {seq} sequence;
    `[ … ]` wraps an optional half."""
    w = int(CFG.ids["seq_width"])
    tokens = {"{MOD}": re.escape(mod), "{http}": r"[1-5]\d{2}", "{SLUG}": r"[A-Z0-9]+(?:-[A-Z0-9]+)*", "{seq}": rf"\d{{{w}}}"}
    parts, i = [], 0
    while i < len(fmt):
        for tok, rx in tokens.items():
            if fmt.startswith(tok, i):
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
                if idrx.fullmatch(val) or not rx.match(val):
                    if idrx.fullmatch(val):
                        continue
                    out.append(Finding(sev, "", "code-format",
                                       f"`{val}` is not an instance of the declared format `{fmt}`", name, n))
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
}


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


def run(mod: str, version: int | None = None, scope: str = "all", write: bool = True) -> AnalyzeReport:
    version = CFG.current_version(mod) if version is None else int(version)
    if not st_mod.is_fresh(mod, version):
        st_mod.build_state(mod, version)
    ctx = Ctx(mod, version)
    rep = AnalyzeReport(mod.upper(), version, scope)
    for c in select_contracts(scope, ctx):
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
            try:
                fs = fn(ctx, args, cl["severity"])
            except Exception as e:  # a broken clause must be visible, never silent
                fs = [Finding(sev_at_rank(1), cl["id"], cl["check"], f"clause could not be evaluated: {e}")]
            for f in fs:
                f.clause = f.clause or cl["id"]
            rep.findings += fs
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
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (path.parent / f"analyze-{tag}.json").write_text(json.dumps(
        {"module": rep.mod, "version": rep.version, "scope": rep.scope, "counts": c, "clean": rep.clean,
         "findings": [f.__dict__ for f in rep.findings]}, indent=2), encoding="utf-8")
    return path
