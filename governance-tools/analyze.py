"""
gov.py analyze — mechanical cross-artifact consistency check (blueprint §6.4)
=============================================================================
Implements every clause of shared/ARTIFACT-CONTRACTS.md (front-matter
`contracts:`), against the module's generated current state (`_state/`).
Clause vocabulary (§13 of that file):
  exists · no-questions · languages · ids-owned · ids-continue · traces · orphans
  · ears · registry-agree · markers · manifest · gate-approved
A gate cannot open with a CRITICAL. The report is written to
`paths.module.analyze_report` inside `_state/`.
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
from toolkit.common import now_iso

SEV = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}


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

    def count(self, sev: str) -> int:
        return sum(1 for f in self.findings if f.severity == sev)

    @property
    def clean(self) -> bool:
        return self.count("CRITICAL") == 0

    def counts(self) -> dict:
        return {k: self.count(k) for k in SEV}


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
        s = f.severity if f.severity in SEV else "MAJOR"
        if SEV[s] > SEV[sev]:
            s = s  # keep the parser's own severity (never escalate above the parser)
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
        out.append(Finding("MAJOR", "", "manifest", "no change-set id stamped in the manifest", ctx.change_manifest_name()))
    for art, rows in man["artifacts"].items():
        if not ctx.artifact(art):
            out.append(Finding("MAJOR", "", "manifest", f"manifest names unknown artifact `{art}`", ctx.change_manifest_name()))
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


CHECKS = {
    "exists": _c_exists, "no-questions": _c_no_questions, "languages": _c_languages,
    "ids-owned": _c_ids_owned, "ids-continue": _c_ids_continue, "traces": _c_traces,
    "orphans": _c_orphans, "ears": _c_ears, "registry-agree": _c_registry_agree,
    "markers": _c_markers, "manifest": _c_manifest, "gate-approved": _c_gate_approved,
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
                rep.skipped.append(f"{cl['id']}: unknown check {cl['check']}")
                continue
            args = dict(cl.get("args") or {})
            if not ctx.when(args.pop("when", None)):
                continue
            try:
                fs = fn(ctx, args, cl["severity"])
            except Exception as e:  # a broken clause must be visible, never silent
                fs = [Finding("MAJOR", cl["id"], cl["check"], f"clause could not be evaluated: {e}")]
            for f in fs:
                f.clause = f.clause or cl["id"]
            rep.findings += fs
    rep.findings.sort(key=lambda f: (SEV[f.severity], f.clause, f.artifact, f.line))
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
             f"**{c['CRITICAL']} critical · {c['MAJOR']} major · {c['MINOR']} minor** · verdict: {'CLEAN' if rep.clean else 'BLOCKED'}", ""]
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
