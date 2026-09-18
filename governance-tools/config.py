"""
Governance Factory — configuration LOADER (not a configuration file)
=====================================================================
Reads factory.yaml (factory facts) and profiles/<id>.yaml (domain facts) and
exposes them as typed objects + path/naming helpers. This module contains NO
factory or domain literal: no stage id, phase key, ID prefix, path, branch,
model name or vocabulary. If you find yourself typing one here, it belongs in
factory.yaml or in a profile (Constitution C1/C2).

Usage
-----
    from config import CFG            # lazily-loaded singleton
    CFG.stage(stage_id).produces      # typed access
    CFG.profile.tracks["backend"]     # active profile
    CFG.version_root("ORG", 2)        # path helpers (filesystem = version authority)
    CFG.fmt(CFG.naming["tag"], mod="org", version=2)

Environment overrides
---------------------
    GOV_FACTORY_ROOT        the tool's own root (tests / CI against an isolated checkout)
    GOV_PROJECT_CHECKOUT    the PROJECT repo (factory.yaml → project.checkout_env); everything
                            generated or project-variable lives there — switching projects is
                            pointing this at another checkout
    GOV_PROFILE             active profile id (default: the project's project.yaml → profile)
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Iterator

import yaml

_FACTORY_FILE = "factory.yaml"          # the one filename this loader must know
_PROFILE_SCHEMA = "_schema.yaml"        # and the schema's, inside paths.schema (a tool path)


# ── small helpers ────────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top level must be a mapping")
    return data


def stage_folder(stage_id: str) -> str:
    """Stage id → folder name, by RULE (naming.stage_folder): '.' and '-' → '_'."""
    return re.sub(r"[.\-]", "_", stage_id)


# ── typed views ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Artifact:
    artifact: str
    file: str
    dir: str | None = None          # None → stage folder inside the module version
    registry: bool = False
    plan: str | None = None         # 'exec' | 'test' → split-able
    track: str | None = None
    optional: bool = False

    def filename(self, mod: str) -> str:
        out = self.file.replace("{mod}", mod.lower()).replace("{MOD}", mod.upper())
        return out.replace("{profile}", CFG.profile_id)


@dataclass(frozen=True)
class Stage:
    id: str
    title: str
    pass_: str                      # 'pre' | 'bootstrap' | '1' | '2' | 'standalone'
    questions: str                  # 'allowed' | 'forbidden'
    lane: str
    inputs: tuple[str, ...]
    produces: tuple[Artifact, ...]
    owns_ids: tuple[str, ...]
    dialogue: bool = False
    track: str | None = None
    once_per: str | None = None
    next: str | None = None
    research: str | None = None
    requirement_format: str | None = None
    derives_from: str | None = None
    scoped: bool = False            # supports `run-standalone --module|--modules|--scope project`
    raw: dict = field(default_factory=dict, compare=False)

    @property
    def folder(self) -> str:
        return stage_folder(self.id)

    @property
    def standalone(self) -> bool:
        return self.pass_ == "standalone"

    def artifact(self, name: str) -> Artifact:
        for a in self.produces:
            if a.artifact == name:
                return a
        raise KeyError(f"stage {self.id} does not produce '{name}'")


@dataclass(frozen=True)
class Phase:
    key: str
    display: str
    folder: str
    never_split: bool = False
    split_threshold: dict | None = None
    sub_labels: tuple[str, ...] = ()
    sub_bearing: bool = False
    integration: bool = False
    binds_api: bool = False


class Profile:
    """Typed view over profiles/<id>.yaml (validated by lint, not here)."""

    def __init__(self, data: dict, path: Path):
        self.data = data
        self.path = path

    # generic access -----------------------------------------------------
    def get(self, dotted: str, default: Any = None) -> Any:
        cur: Any = self.data
        for part in dotted.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    @property
    def id(self) -> str:
        return self.data["identity"]["id"]

    @property
    def languages(self) -> dict:
        return self.data["languages"]

    @property
    def vocabulary(self) -> dict:
        return self.data["vocabulary"]

    @property
    def tracks(self) -> dict:
        return self.data["tracks"]

    @property
    def stack(self) -> dict:
        return self.data["stack"]

    @property
    def conventions(self) -> dict:
        return self.data.get("conventions") or {}

    SELF_CHECK = "self_check"       # the profile address of the self-check declaration

    @property
    def self_check(self) -> dict | None:
        """How this domain's artifacts state a verdict about themselves (block token,
        verdict label, pass/fail wording) — or None when the domain has no self-check.
        The one place the address is spelled; every reader goes through here or through
        a contract clause's own `spec` arg."""
        return self.data.get(self.SELF_CHECK) or None

    @property
    def knowledge_files(self) -> list[str]:
        return list((self.data.get("knowledge") or {}).get("files") or [])

    @property
    def extra_ids(self) -> dict:
        return dict(((self.data.get("ids") or {}).get("atoms")) or {})

    # phases ----------------------------------------------------------------
    def phases(self, track: str, plan: str) -> list[Phase]:
        rows = self.tracks[track]["plans"][plan]["phases"]
        out = []
        for r in rows:
            out.append(Phase(
                key=r["key"],
                display=r.get("display", r["key"]),
                folder=r.get("folder", r["key"]),
                never_split=bool(r.get("never_split", False)),
                split_threshold=r.get("split_threshold"),
                sub_labels=tuple(r.get("sub_labels", ()) or ()),
                sub_bearing=bool(r.get("sub_bearing", False)),
                integration=bool(r.get("integration", False)),
                binds_api=bool(r.get("binds_api", False)),
            ))
        return out

    def phase_keys(self, track: str, plan: str) -> list[str]:
        return [p.key for p in self.phases(track, plan)]

    def plans(self, track: str) -> list[str]:
        return list(self.tracks[track]["plans"].keys())


# ── the factory config ───────────────────────────────────────────────────────

class FactoryConfig:
    def __init__(self, root: Path | None = None, profile_id: str | None = None):
        self.root = Path(os.environ.get("GOV_FACTORY_ROOT") or root or self._discover_root()).resolve()
        self.data = _load_yaml(self.root / _FACTORY_FILE)
        self._profile_override = profile_id or os.environ.get("GOV_PROFILE")

    @staticmethod
    def _discover_root() -> Path:
        here = Path(__file__).resolve()
        for parent in [here.parent, *here.parents]:
            if (parent / _FACTORY_FILE).exists():
                return parent
        raise FileNotFoundError(f"{_FACTORY_FILE} not found above {here}")

    # raw sections ----------------------------------------------------------
    @property
    def factory(self) -> dict:      return self.data["factory"]
    @property
    def paths(self) -> dict:
        """Raw `paths:`. A value may still carry `{profile_id}`; it is resolved
        against the active profile only when present, so a project-less run
        (scaffolding a new project) never has to load a profile to name a path."""
        raw = self.data["paths"]
        if not any(isinstance(v, str) and "{profile_id}" in v for v in raw.values()):
            return dict(raw)
        pid = self.profile.id
        return {k: (v.replace("{profile_id}", pid) if isinstance(v, str) else v) for k, v in raw.items()}
    @property
    def naming(self) -> dict:       return self.data["naming"]
    @property
    def gates(self) -> list[dict]:  return self.data["gates"]
    @property
    def passes(self) -> dict:       return self.data["passes"]
    @property
    def ids(self) -> dict:          return self.data["ids"]
    @property
    def markers(self) -> dict:      return self.data["markers"]
    @property
    def tracks(self) -> dict:       return self.data["tracks"]
    @property
    def repos(self) -> dict:
        """The consumer repos of the ACTIVE PROJECT (`project.yaml → repos`) —
        per-project facts, never in factory.yaml."""
        return dict(self.project_data.get("repos") or {})
    @property
    def project(self) -> dict:      return self.data["project"]
    @property
    def lanes(self) -> dict:        return self.data["lanes"]
    @property
    def review(self) -> dict:       return self.data["review"]
    @property
    def analyze(self) -> dict:      return self.data["analyze"]
    @property
    def ambiguity(self) -> dict:    return self.data["ambiguity"]
    @property
    def dialogue(self) -> dict:     return self.data.get("dialogue", {})
    @property
    def runner(self) -> dict:       return self.data.get("runner", {})
    @property
    def versioning(self) -> dict:   return self.data["versioning"]
    @property
    def inputs(self) -> dict:       return self.data.get("inputs", {})
    @property
    def feedback(self) -> dict:     return self.data.get("feedback", {})
    @property
    def publications(self) -> dict: return self.data.get("publications", {})
    @property
    def commands(self) -> list[dict]: return self.data.get("commands", [])

    # project -----------------------------------------------------------------
    def project_checkout(self) -> Path:
        """The project repo: `$<project.checkout_env>`, else `project.checkout_default`
        relative to this tool's root. The content root for every external path key."""
        p = self.project
        return Path(os.environ.get(p["checkout_env"]) or (self.root / p["checkout_default"])).resolve()

    def project_file(self) -> Path:
        return self.project_checkout() / self.project["file"]

    @cached_property
    def project_data(self) -> dict:
        """`project.yaml` of the active project — user-edited, read here, never
        written by the factory. Empty when the checkout has none (a project being
        scaffolded, or the factory run without a project)."""
        f = self.project_file()
        return _load_yaml(f) if f.exists() else {}

    # profile -----------------------------------------------------------------
    @property
    def profile_id(self) -> str:
        pid = self._profile_override or self.project_data.get("profile")
        if not pid:
            raise FileNotFoundError(
                f"no active profile: {self.project_file()} names none (or does not exist) and "
                f"GOV_PROFILE is unset — point {self.project['checkout_env']} at a project repo, "
                f"or scaffold one with `gov.py new-project`")
        return str(pid)

    @cached_property
    def profile(self) -> Profile:
        return self.load_profile(self.profile_id)

    def profiles_dir(self) -> Path:
        """The project's profiles — an external path key, resolved on the project checkout."""
        return self.dir("profiles")

    def profile_schema(self) -> dict:
        # validation logic, not data: the schema stays in the tool (paths.schema)
        return _load_yaml(self.root / self.data["paths"]["schema"] / _PROFILE_SCHEMA)

    def load_profile(self, profile_id: str) -> Profile:
        path = self.profiles_dir() / f"{profile_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"profile '{profile_id}' not found: {path}")
        return Profile(_load_yaml(path), path)

    def list_profiles(self) -> list[str]:
        return sorted(p.stem for p in self.profiles_dir().glob("*.yaml") if not p.name.startswith("_"))

    # stages ------------------------------------------------------------------
    @staticmethod
    def _mk_stage(raw: dict, pass_override: str | None = None) -> Stage:
        produces = tuple(Artifact(
            artifact=a["artifact"], file=a["file"], dir=a.get("dir"),
            registry=bool(a.get("registry", False)), plan=a.get("plan"),
            track=a.get("track"), optional=bool(a.get("optional", False)),
        ) for a in raw.get("produces", []))
        return Stage(
            id=raw["id"], title=raw.get("title", raw["id"]),
            pass_=str(pass_override or raw.get("pass")),
            questions=raw.get("questions", "forbidden"),
            lane=raw["lane"],
            inputs=tuple(raw.get("inputs", [])),
            produces=produces,
            owns_ids=tuple(raw.get("owns_ids", [])),
            dialogue=bool(raw.get("dialogue", False)),
            track=raw.get("track"), once_per=raw.get("once_per"),
            next=raw.get("next"), research=raw.get("research"),
            requirement_format=raw.get("requirement_format"),
            derives_from=raw.get("derives_from"), scoped=bool(raw.get("scoped", False)), raw=raw,
        )

    @cached_property
    def stages(self) -> list[Stage]:
        return [self._mk_stage(s) for s in self.data["stages"]]

    @cached_property
    def standalone(self) -> list[Stage]:
        return [self._mk_stage(s, "standalone") for s in self.data.get("standalone", [])]

    def all_stages(self) -> Iterator[Stage]:
        yield from self.stages
        yield from self.standalone

    def stage(self, stage_id: str) -> Stage:
        for s in self.all_stages():
            if s.id == stage_id:
                return s
        raise KeyError(f"unknown stage '{stage_id}'")

    def pass_stages(self, pass_no: str | int) -> list[Stage]:
        return [self.stage(i) for i in self.passes[str(pass_no)]["stages"]]

    def stage_ids(self) -> list[str]:
        return [s.id for s in self.stages]

    def gate(self, gate_id: str) -> dict:
        for g in self.gates:
            if g["id"] == gate_id:
                return g
        raise KeyError(f"unknown gate '{gate_id}'")

    def gate_after(self, stage_id: str) -> dict | None:
        return next((g for g in self.gates if g["after"] == stage_id), None)

    def lane(self, lane_id: str) -> dict:
        return self.lanes[lane_id]

    # id grammar ---------------------------------------------------------------
    def id_atoms(self) -> dict:
        atoms = dict(self.ids["atoms"])
        atoms.update(self.profile.extra_ids)
        return atoms

    def id_regex(self, prefix: str | None = None) -> re.Pattern:
        w = int(self.ids["seq_width"])
        pfx = re.escape(prefix) if prefix else "|".join(re.escape(p) for p in sorted(self.id_atoms(), key=len, reverse=True))
        pat = self.ids["pattern"].replace("{prefix}", f"(?P<prefix>{pfx})") \
                                 .replace("{MOD}", r"(?P<mod>[A-Z][A-Z0-9]*)") \
                                 .replace("{seq}", rf"(?P<seq>\d{{{w},}})")
        return re.compile(pat)

    def make_id(self, prefix: str, mod: str, seq: int) -> str:
        w = int(self.ids["seq_width"])
        return self.ids["pattern"].replace("{prefix}", prefix).replace("{MOD}", mod.upper()).replace("{seq}", f"{seq:0{w}d}")

    # paths ---------------------------------------------------------------------
    @property
    def external(self) -> dict:
        """Which `paths` keys resolve against the PROJECT checkout (read raw — no
        profile is needed to answer this)."""
        return self.data["paths"].get("external") or {}

    def dir(self, key: str) -> Path:
        """Path for a declared key, against whichever repo owns it.

        Everything generated or project-variable lives in the project repo —
        the profile, the analysis, the decisions, the delivered packages — so
        every consumer reads the artifact where it was written. The factory's
        own machinery stays here. Which is which is declared in `paths.external`,
        never decided in this function."""
        ext = self.external
        base = self.project_checkout() if key in (ext.get("keys") or ()) else self.root
        rel = self.paths[key]
        if not isinstance(rel, str):
            raise KeyError(f"paths.{key} is not a path")
        return base / rel

    def modules_root(self) -> Path:
        return self.dir("modules")

    def module_root(self, mod: str) -> Path:
        return self.modules_root() / mod.upper()

    def modules(self) -> list[str]:
        """Every module the filesystem holds, in code order. The version authority is
        the filesystem (versioning.authority), so the module set is too — a sweep over
        "every module" never reads a list somebody has to remember to update."""
        root = self.modules_root()
        if not root.exists():
            return []
        return sorted(p.name for p in root.iterdir() if p.is_dir() and self.module_versions(p.name))

    def module_versions(self, mod: str) -> list[int]:
        """Filesystem is the version authority: base folder = v1 when it has any
        stage folder; vN subfolders = N. Non-stage service folders are ignored."""
        root = self.module_root(mod)
        if not root.exists():
            return []
        vf = self.naming["version_folder"]
        rx = re.compile("^" + re.escape(vf).replace(re.escape("{version}"), r"(\d+)") + "$")
        vs: set[int] = set()
        stage_folders = {s.folder for s in self.all_stages()}
        for child in root.iterdir():
            m = rx.match(child.name)
            if child.is_dir() and m:
                vs.add(int(m.group(1)))
            elif child.is_dir() and child.name in stage_folders:
                vs.add(1)
        return sorted(vs)

    def current_version(self, mod: str) -> int:
        vs = self.module_versions(mod)
        return max(vs) if vs else 1

    def next_version(self, mod: str) -> int:
        vs = self.module_versions(mod)
        return (max(vs) + 1) if vs else 1

    def version_root(self, mod: str, version: int | None = None) -> Path:
        version = self.current_version(mod) if version is None else int(version)
        if version == 1:
            return self.module_root(mod)
        return self.module_root(mod) / self.fmt(self.naming["version_folder"], version=version)

    def stage_dir(self, mod: str, stage_id: str, version: int | None = None) -> Path:
        st = self.stage(stage_id)
        return self.version_root(mod, version) / st.folder

    def artifact_path(self, mod: str, stage_id: str, artifact: str, version: int | None = None) -> Path:
        st = self.stage(stage_id)
        a = st.artifact(artifact)
        if a.dir:                                 # platform-level artifact (paths.domain, paths.platform)
            return self.dir(a.dir) / a.filename(mod)
        return self.stage_dir(mod, stage_id, version) / a.filename(mod)

    def plan_path(self, mod: str, track: str, plan: str, version: int | None = None) -> Path:
        for st in self.all_stages():
            for a in st.produces:
                if a.plan == plan and a.track == track:
                    return self.artifact_path(mod, st.id, a.artifact, version)
        raise KeyError(f"no plan '{plan}' for track '{track}'")

    def packages_dir(self, mod: str, track: str, plan: str, version: int | None = None) -> Path:
        """Where a track's split packages are DELIVERED: the track's delivery
        partition of the project repo (`tracks.<t>.delivery`), the version folder
        for a delta (v1 = the partition itself, as for the module base), then the
        package. The consumer reads it there; nothing is copied anywhere."""
        pkg = self.tracks[track]["packages"][plan]
        version = self.current_version(mod) if version is None else int(version)
        base = self.partition_dir(self.tracks[track]["delivery"], mod)
        if version > 1:
            base = base / self.fmt(self.naming["version_folder"], version=version)
        return base / pkg

    def state_dir(self, mod: str, version: int | None = None) -> Path:
        return self.version_root(mod, version) / self.paths["module"]["state_dir"]

    def inputs_dir(self, mod: str, version: int | None = None) -> Path:
        return self.version_root(mod, version) / self.paths["module"]["inputs_dir"]

    def decisions_dir(self, mod: str) -> Path:
        return self.dir("decisions") / mod.upper()

    def project_receives(self, publication: str) -> Path | None:
        """Where the project repo keeps a factory publication (`project.receives`)
        — inside the one checkout every consumer mounts. None when undeclared."""
        rel = (self.project.get("receives") or {}).get(publication)
        return (self.project_checkout() / rel) if rel else None

    def track_repo(self, track: str) -> str:
        """The consumer repo key for a track (`tracks.<t>.repo`, default `<t>`) —
        a key of the project's `repos`, named rather than inferred (F-12)."""
        return self.tracks[track].get("repo", track)

    def track_partition(self, track: str) -> str:
        """The partition a track WRITES (its execution state, its own outputs)."""
        return self.tracks[track]["partition"]

    def track_delivery(self, track: str) -> str:
        """The partition the factory delivers a track's packages into."""
        return self.tracks[track]["delivery"]

    # ── the project repo's partitions ─────────────────────────────────────
    FACTORY_WRITER = "factory"      # the one writer name that means "this tool"

    def _partition_specs(self) -> dict:
        return self.project.get("partitions", {})

    def partitions(self) -> dict:
        """Partition name → path template. GOVERNANCE-SHARED-DESIGN.md §3's
        ownership table in the form the tools address."""
        return {k: v["path"] for k, v in self._partition_specs().items()}

    def partition_readers(self, part: str) -> str | list[str]:
        """Who may READ it. Defaults to its writer — the narrow answer — so a
        partition that others must see has to say so."""
        return self._partition_specs()[part].get("readers", self.partition_writer(part))

    def partition_is_readable_by(self, part: str, who: str) -> bool:
        r = self.partition_readers(part)
        return r == "all" or who == r or (isinstance(r, list) and who in r)

    def partition_writer(self, part: str) -> str:
        """Who may write it. Read, not merely documented: it is what stops a
        factory regeneration from clearing a path a track wrote."""
        return self._partition_specs()[part]["writer"]

    def foreign_partitions(self, mod: str) -> list[Path]:
        """Every per-module partition this factory must not write or delete."""
        return [self.partition_dir(p, mod) for p in self._partition_specs()
                if self.partition_writer(p) != self.FACTORY_WRITER
                and self.partition_is_per_module(p)]

    def partition_is_per_module(self, part: str) -> bool:
        """Read off the template — an entry carrying `{MOD}` is per-module.
        Recognising a partition by its NAME would put the ownership table's
        vocabulary back into the code C1 keeps it out of."""
        return "{MOD}" in self.partitions()[part]

    def partition_dir(self, part: str, mod: str | None = None) -> Path:
        return self.project_checkout() / self.fmt(self.partitions()[part], **({"mod": mod} if mod else {}))

    def partition_of(self, path: Path, mod: str) -> str | None:
        """The partition a path falls in — the DEEPEST one, since a factory-written
        delivery partition sits inside a track's own partition (most specific
        wins, exactly as CODEOWNERS reads it). None outside every partition."""
        p = Path(path).resolve()
        best: tuple[int, str] | None = None
        for part in self._partition_specs():
            d = self.partition_dir(part, mod if self.partition_is_per_module(part) else None).resolve()
            if d == p or d in p.parents:
                if best is None or len(d.parts) > best[0]:
                    best = (len(d.parts), part)
        return best[1] if best else None

    def repo_checkout(self, repo: str) -> Path:
        """A CONSUMER checkout of the active project (`project.yaml → repos`):
        its env var, else its `checkout_default` relative to the project checkout."""
        r = self.repos[repo]
        return Path(os.environ.get(r["checkout_env"]) or (self.project_checkout() / r["checkout_default"])).resolve()

    # naming ---------------------------------------------------------------------
    def fmt(self, template: str, **kw: Any) -> str:
        """Fill a declared template. `{profile_id}` resolves from the active
        profile unless the caller overrides it — the same token `paths` carries,
        resolved in one place so any config value may use it. A config value
        that reached a filesystem path with `{profile_id}` still in it is how
        `fetch-inputs` reported a closed gate over a directory that was there."""
        out = template
        if "{profile_id}" in out and "profile_id" not in kw:
            kw = {**kw, "profile_id": self.profile.id}
        if "mod" in kw or "MOD" in kw:
            mod = str(kw.get("mod") or kw.get("MOD"))
            out = out.replace("{MOD}", mod.upper()).replace("{mod}", mod.lower())
        for k, v in kw.items():
            if k in ("mod", "MOD"):
                continue
            out = out.replace("{" + k + "}", str(v))
        # support {seq:03d}
        out = re.sub(r"\{seq:(\d+)d\}", lambda m: str(kw.get("seq", 0)).zfill(int(m.group(1))), out)
        return out

    def tag_name(self, mod: str, version: int) -> str:
        return self.fmt(self.naming["tag"], mod=mod, version=version)

    def commit_msg(self, kind: str, **kw: Any) -> str:
        return self.fmt(self.naming["commit"][kind], **kw)


# ── singleton ────────────────────────────────────────────────────────────────

class _Lazy:
    _inst: FactoryConfig | None = None

    def __getattr__(self, name: str) -> Any:
        if _Lazy._inst is None:
            _Lazy._inst = FactoryConfig()
        return getattr(_Lazy._inst, name)

    def reload(self, root: Path | None = None, profile_id: str | None = None) -> FactoryConfig:
        _Lazy._inst = FactoryConfig(root, profile_id)
        return _Lazy._inst


CFG = _Lazy()
