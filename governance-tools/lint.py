"""
gov.py lint — Constitution enforcement
=======================================
C1  single source of truth : generated files carry the generated marker and match a fresh render
C2  no hardcode            : profile vocabulary / stack / removed concepts never typed in engines, shared, tools
C3  no contradictions      : docs must not restate factory facts that differ from factory.yaml
                             (stage lists, phase keys, lanes) — checked via the render diff
C5  no exceptions          : every profile validates against profiles/_schema.yaml

Everything this module knows comes from factory.yaml (`lint:` section) and the
profile — it has no vocabulary of its own.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from config import CFG, FactoryConfig, Profile


@dataclass
class Finding:
    severity: str          # CRITICAL | MAJOR | MINOR
    rule: str
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        return f"[{self.severity}] {self.rule} {loc} — {self.message}"


# ═══════════════════════════════════════════════════════════════════════════
# Profile schema validation (C5)
# ═══════════════════════════════════════════════════════════════════════════

_ONE_OF = re.compile(r"^\((.+)\)$")
_LIST = re.compile(r"^list\[(.+)\]$")
_MAP = re.compile(r"^map\[(.+?),\s*(.+)\]$")


def _split_top(s: str, sep: str = ",") -> list[str]:
    """split on sep at bracket depth 0."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "[{(":
            depth += 1
        elif ch in "]})":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def _inline_obj(spec: str) -> dict[str, str] | None:
    """'{id: str, owns: list[str]}' → {'id': 'str', 'owns': 'list[str]'}"""
    spec = spec.strip()
    if not (spec.startswith("{") and spec.endswith("}")):
        return None
    body = spec[1:-1]
    out = {}
    for part in _split_top(body):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def _check_type(value: Any, spec: str, path: str, types: dict, out: list[Finding]) -> None:
    spec = spec.strip()
    if spec.startswith("$"):
        _check_obj(value, types[spec[1:]], path, types, out)
        return
    m = _ONE_OF.match(spec)
    if m and "|" in m.group(1) and not spec.startswith("{"):
        allowed = [a.strip() for a in m.group(1).split("|")]
        if str(value) not in allowed:
            out.append(Finding("MAJOR", "C5-profile", path, 0, f"must be one of {allowed}, got {value!r}"))
        return
    if spec == "str":
        if not isinstance(value, str):
            out.append(Finding("MAJOR", "C5-profile", path, 0, f"expected str, got {type(value).__name__}"))
        return
    if spec == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            out.append(Finding("MAJOR", "C5-profile", path, 0, f"expected int, got {type(value).__name__}"))
        return
    if spec == "bool":
        if not isinstance(value, bool):
            out.append(Finding("MAJOR", "C5-profile", path, 0, f"expected bool, got {type(value).__name__}"))
        return
    m = _LIST.match(spec)
    if m:
        if not isinstance(value, list):
            out.append(Finding("MAJOR", "C5-profile", path, 0, f"expected list, got {type(value).__name__}"))
            return
        for i, item in enumerate(value):
            _check_type(item, m.group(1), f"{path}[{i}]", types, out)
        return
    m = _MAP.match(spec)
    if m:
        if not isinstance(value, dict):
            out.append(Finding("MAJOR", "C5-profile", path, 0, f"expected map, got {type(value).__name__}"))
            return
        for k, v in value.items():
            _check_type(v, m.group(2), f"{path}.{k}", types, out)
        return
    obj = _inline_obj(spec)
    if obj is not None:
        _check_obj(value, obj, path, types, out)
        return
    # unknown spec → accept (schema author's responsibility)


def _check_obj(value: Any, schema: dict, path: str, types: dict, out: list[Finding]) -> None:
    if not isinstance(value, dict):
        out.append(Finding("MAJOR", "C5-profile", path, 0, f"expected mapping, got {type(value).__name__}"))
        return
    declared = {}
    for key, spec in schema.items():
        if key.startswith("$") or key == "schema_version":
            continue
        optional = key.endswith("?")
        name = key.rstrip("?")
        declared[name] = (optional, spec)
        if name not in value:
            if not optional:
                out.append(Finding("CRITICAL", "C5-profile", f"{path}.{name}", 0, "required key missing"))
            continue
        v = value[name]
        if isinstance(spec, dict):
            _check_obj(v, spec, f"{path}.{name}", types, out)
        else:
            _check_type(v, str(spec), f"{path}.{name}", types, out)
    for key in value:
        if key not in declared and key != "schema_version":
            out.append(Finding("MINOR", "C5-profile", f"{path}.{key}", 0, "key not declared in the schema"))


def validate_profile(cfg: FactoryConfig, profile: Profile) -> list[Finding]:
    schema = cfg.profile_schema()
    types = schema.get("$types", {})
    out: list[Finding] = []
    _check_obj(profile.data, schema, profile.id, types, out)
    # semantic checks that a type system cannot express
    langs = profile.languages
    if langs.get("primary") not in (langs.get("all") or []):
        out.append(Finding("MAJOR", "C5-profile", f"{profile.id}.languages.primary", 0, "primary must be in languages.all"))
    if profile.id != profile.path.stem:
        out.append(Finding("MAJOR", "C5-profile", f"{profile.id}.identity.id", 0, f"id must equal filename stem '{profile.path.stem}'"))
    try:
        _phase_checks(cfg, profile, out)
    except Exception as e:   # a malformed tracks block (e.g. an unfilled scaffold) is a finding, never a crash
        out.append(Finding("CRITICAL", "C5-profile", f"{profile.id}.tracks", 0, f"tracks block is not well-formed: {e}"))
    for f in profile.knowledge_files:
        if not (cfg.root / f).exists():
            out.append(Finding("MAJOR", "C5-profile", f, 0, "knowledge file does not exist"))
    core_atoms = set(cfg.ids["atoms"])
    for atom in profile.extra_ids:
        if atom in core_atoms:
            out.append(Finding("CRITICAL", "C5-profile", f"{profile.id}.ids.atoms.{atom}", 0, "profiles may ADD atoms, never redefine core atoms"))
    return out


def _phase_checks(cfg: FactoryConfig, profile: Profile, out: list[Finding]) -> None:
    for tr in profile.tracks:
        if tr not in cfg.tracks:
            out.append(Finding("MAJOR", "C5-profile", f"{profile.id}.tracks.{tr}", 0, "track not declared in factory.yaml"))
            continue
        for plan in profile.plans(tr):
            keys = profile.phase_keys(tr, plan)
            if len(keys) != len(set(keys)):
                out.append(Finding("CRITICAL", "C5-profile", f"{profile.id}.tracks.{tr}.plans.{plan}", 0, "duplicate phase keys"))
            for p in profile.phases(tr, plan):
                if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]*", p.key):
                    out.append(Finding("MAJOR", "C5-profile", f"{profile.id}.tracks.{tr}.plans.{plan}.{p.key}", 0, "phase key must match [A-Z0-9-]+"))
                if p.never_split and (p.split_threshold or p.sub_labels):
                    out.append(Finding("MAJOR", "C5-profile", f"{profile.id}.tracks.{tr}.plans.{plan}.{p.key}", 0, "never_split phase cannot declare split_threshold/sub_labels"))


# ═══════════════════════════════════════════════════════════════════════════
# Forbidden literals (C2) — removed concepts + profile vocabulary
# ═══════════════════════════════════════════════════════════════════════════

_TEXT_EXT = {".md", ".py", ".yaml", ".yml", ".txt", ".json"}


def _iter_files(cfg: FactoryConfig, roots: Iterable[str]) -> Iterable[Path]:
    exempt = set(cfg.data["lint"]["exempt_paths"])
    for r in roots:
        p = cfg.root / r
        if p.is_file():
            yield p
            continue
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if not f.is_file() or f.suffix not in _TEXT_EXT:
                continue
            rel = f.relative_to(cfg.root).parts
            if any(part in exempt for part in rel):
                continue
            yield f


def _profile_terms(cfg: FactoryConfig, profile: Profile) -> set[str]:
    terms: set[str] = set()

    def collect(v: Any) -> None:
        if isinstance(v, str):
            if len(v) >= 4 and not v.startswith("{"):
                terms.add(v)
        elif isinstance(v, list):
            for x in v:
                collect(x)
        elif isinstance(v, dict):
            for k, x in v.items():
                if isinstance(k, str) and len(k) >= 4 and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]+", k) and k[0].isupper() and any(c.islower() for c in k):
                    terms.add(k)   # camelCase/PascalCase field names declared by the profile
                collect(x)

    for dotted in cfg.data["lint"]["profile_term_sources"]:
        collect(profile.get(dotted))
    # only keep distinctive tokens: contains a digit, a hyphen, an underscore, or mixed case
    keep = set()
    for t in terms:
        tok = t.split()[0] if " " in t else t
        if len(tok) < 4:
            continue
        if any(c.isdigit() for c in tok) or "-" in tok or "_" in tok or (any(c.isupper() for c in tok) and any(c.islower() for c in tok)):
            keep.add(tok.strip("()"))
    return keep


def scan_literals(cfg: FactoryConfig, profile: Profile) -> list[Finding]:
    out: list[Finding] = []
    lint = cfg.data["lint"]
    gen_marker = lint["generated_marker"]
    forbidden = [t for t in lint["forbidden_terms"]]
    forb_rx = re.compile("|".join(re.escape(t) for t in forbidden))
    pterms = _profile_terms(cfg, profile)
    pterm_rx = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in sorted(pterms, key=len, reverse=True)) + r")(?![\w-])") if pterms else None
    profile_roots = set(lint["profile_terms_forbidden_in"])

    for f in _iter_files(cfg, lint["scan_paths"]):
        rel = f.relative_to(cfg.root)
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        is_generated = gen_marker in text
        in_profile_scope = any(str(rel).startswith(r) for r in profile_roots)
        for n, line in enumerate(text.splitlines(), 1):
            if forb_rx.search(line) and str(rel) != "factory.yaml":
                # allow the lint list itself and explicit "removed" notes in history-style lines
                if "removed" in line.lower() or "deleted" in line.lower() or "forbidden_terms" in line:
                    continue
                out.append(Finding("CRITICAL", "C2-removed-concept", str(rel), n, f"removed concept referenced: {forb_rx.search(line).group(0)!r}"))
            if pterm_rx and in_profile_scope and not is_generated:
                m = pterm_rx.search(line)
                if m and "{{" not in line:
                    out.append(Finding("MAJOR", "C2-profile-literal", str(rel), n, f"domain literal {m.group(1)!r} must come from the profile"))
    return out


def scan_code_literals(cfg: FactoryConfig, profile: Profile) -> list[Finding]:
    """Python under code_paths may not spell stage ids, phase keys or ID prefixes as string literals."""
    out: list[Finding] = []
    stage_ids = set(cfg.stage_ids()) | {s.id for s in cfg.standalone}
    phase_keys = {p.key for tr in profile.tracks for plan in profile.plans(tr) for p in profile.phases(tr, plan)}
    prefixes = set(cfg.id_atoms())
    literal_rx = re.compile(r"""(["'])([^"'\n]{1,40})\1""")
    for f in _iter_files(cfg, cfg.data["lint"]["code_paths"]):
        if f.suffix != ".py" or "tests" in f.parts or f.name == "lint.py":
            continue
        rel = str(f.relative_to(cfg.root))
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if s.startswith("#") or s.startswith('"""') or "noqa: lint" in line:
                continue
            for m in literal_rx.finditer(line):
                lit = m.group(2)
                if lit in stage_ids or lit in phase_keys:
                    out.append(Finding("MAJOR", "C2-code-literal", rel, n, f"{lit!r} must come from factory.yaml / profile"))
                elif lit in prefixes and len(lit) >= 2 and lit.isupper():
                    out.append(Finding("MAJOR", "C2-code-literal", rel, n, f"ID prefix {lit!r} must come from factory.yaml ids"))
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Duplicate command trees (C4) and generated freshness (C1) hooks
# ═══════════════════════════════════════════════════════════════════════════

def scan_structure(cfg: FactoryConfig) -> list[Finding]:
    out: list[Finding] = []
    legacy_cmds = cfg.root / "commands"
    if legacy_cmds.exists():
        out.append(Finding("CRITICAL", "C4-duplicate", "commands/", 0, f"second command tree; only {cfg.paths['commands']} may exist"))
    for st in cfg.stages:
        d = cfg.dir("engines") / st.id
        if not (d / "SKILL.md").exists():
            out.append(Finding("MAJOR", "C1-structure", f"engines/{st.id}/SKILL.md", 0, "missing (run gov.py render)"))
        if not (d / "references").exists():
            out.append(Finding("MAJOR", "C1-structure", f"engines/{st.id}/references", 0, "missing"))
    for st in cfg.standalone:
        d = cfg.dir("standalone") / st.id
        if not (d / "SKILL.md").exists():
            out.append(Finding("MAJOR", "C1-structure", f"standalone/{st.id}/SKILL.md", 0, "missing (run gov.py render)"))
    for extra in (cfg.dir("engines")).glob("*"):
        if extra.is_dir() and extra.name not in cfg.stage_ids():
            out.append(Finding("CRITICAL", "C1-structure", f"engines/{extra.name}", 0, "engine folder not declared in factory.yaml stages"))
    return out


def run(cfg: FactoryConfig | None = None, profile_id: str | None = None, render_check: bool = True) -> list[Finding]:
    cfg = cfg or CFG.reload()
    findings: list[Finding] = []
    profiles = [profile_id] if profile_id else cfg.list_profiles()
    for pid in profiles:
        prof = cfg.load_profile(pid)
        findings += validate_profile(cfg, prof)
    active = cfg.profile
    findings += scan_literals(cfg, active)
    findings += scan_code_literals(cfg, active)
    findings += scan_structure(cfg)
    if render_check:
        try:
            import render  # local module
            findings += render.check_fresh(cfg)
        except ImportError:
            pass
    order = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}
    findings.sort(key=lambda f: (order[f.severity], f.path, f.line))
    return findings


if __name__ == "__main__":  # pragma: no cover
    import sys
    fs = run(profile_id=sys.argv[1] if len(sys.argv) > 1 else None)
    for f in fs:
        print(f)
    print(f"\n{sum(f.severity=='CRITICAL' for f in fs)} critical · {sum(f.severity=='MAJOR' for f in fs)} major · {sum(f.severity=='MINOR' for f in fs)} minor")
    sys.exit(1 if any(f.severity == "CRITICAL" for f in fs) else 0)
