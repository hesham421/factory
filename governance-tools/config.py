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
    GOV_FACTORY_ROOT   repo root (tests / CI against an isolated checkout)
    GOV_PROFILE        active profile id (default: factory.yaml → factory.active_profile)
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
_PROFILE_SCHEMA = "_schema.yaml"        # and the schema's, inside paths.profiles


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
        return self.file.replace("{mod}", mod.lower()).replace("{MOD}", mod.upper())


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
        self._profile_id = profile_id or os.environ.get("GOV_PROFILE") or self.data["factory"]["active_profile"]

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
    def paths(self) -> dict:        return self.data["paths"]
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
    def repos(self) -> dict:        return self.data["repos"]
    @property
    def delivery(self) -> dict:     return self.data["delivery"]
    @property
    def lanes(self) -> dict:        return self.data["lanes"]
    @property
    def review(self) -> dict:       return self.data["review"]
    @property
    def ambiguity(self) -> dict:    return self.data["ambiguity"]
    @property
    def versioning(self) -> dict:   return self.data["versioning"]
    @property
    def inputs(self) -> dict:       return self.data.get("inputs", {})
    @property
    def commands(self) -> list[dict]: return self.data.get("commands", [])

    # profile -----------------------------------------------------------------
    @property
    def profile_id(self) -> str:
        return self._profile_id

    @cached_property
    def profile(self) -> Profile:
        return self.load_profile(self._profile_id)

    def profiles_dir(self) -> Path:
        return self.root / self.paths["profiles"]

    def profile_schema(self) -> dict:
        return _load_yaml(self.profiles_dir() / _PROFILE_SCHEMA)

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
            derives_from=raw.get("derives_from"), raw=raw,
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
    def dir(self, key: str) -> Path:
        return self.root / self.paths[key]

    def modules_root(self) -> Path:
        return self.dir("modules")

    def module_root(self, mod: str) -> Path:
        return self.modules_root() / mod.upper()

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
        if a.dir:                                 # platform-level artifact (domain/, platform/)
            return self.dir(a.dir) / a.filename(mod)
        return self.stage_dir(mod, stage_id, version) / a.filename(mod)

    def plan_path(self, mod: str, track: str, plan: str, version: int | None = None) -> Path:
        for st in self.all_stages():
            for a in st.produces:
                if a.plan == plan and a.track == track:
                    return self.artifact_path(mod, st.id, a.artifact, version)
        raise KeyError(f"no plan '{plan}' for track '{track}'")

    def packages_dir(self, mod: str, track: str, plan: str, version: int | None = None) -> Path:
        pkg = self.tracks[track]["packages"][plan]
        return self.version_root(mod, version) / self.paths["module"]["packages_dir"] / pkg

    def state_dir(self, mod: str, version: int | None = None) -> Path:
        return self.version_root(mod, version) / self.paths["module"]["state_dir"]

    def inputs_dir(self, mod: str, version: int | None = None) -> Path:
        return self.version_root(mod, version) / self.paths["module"]["inputs_dir"]

    def decisions_dir(self, mod: str) -> Path:
        return self.dir("decisions") / mod.upper()

    def repo_checkout(self, repo: str) -> Path:
        r = self.repos[repo]
        return Path(os.environ.get(r["checkout_env"]) or (self.root / r["checkout_default"])).resolve()

    # naming ---------------------------------------------------------------------
    @staticmethod
    def fmt(template: str, **kw: Any) -> str:
        out = template
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

    def delivery_branch(self, mod: str, version: int, track: str) -> str:
        return self.fmt(self.naming["delivery_branch"], mod=mod, version=version, track=track)

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
