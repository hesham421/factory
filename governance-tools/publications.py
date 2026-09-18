"""
Cross-repo publications — what the factory DERIVES for every consumer to read.

Split out of gov.py because `lint` must check that every declared publication
names a builder that resolves, and importing gov to do it made `gov` and `lint`
import each other. A checker that cannot be loaded without the thing it checks
is not a checker.

A publication names its builder in factory.yaml; lint refuses a name that is not
registered here. Adding one with a NEW derivation is therefore new code, and
says so, instead of failing as a KeyError at the moment someone publishes.
"""
from __future__ import annotations

from config import CFG
from toolkit.common import now_iso, read_json


def module_manifest(mod: str) -> dict:
    """The module's own manifest — the factory-side place where a module states
    the facts a consumer's registry copy shows (when it was registered, what it
    is)."""
    return read_json(CFG.module_root(mod) / CFG.paths["module"]["manifest_file"], {}) or {}


def pub_profile_summary(spec: dict, existing: list[dict]) -> dict:
    """Every FACTORY fact a consumer needs to set a module up, derived wholly from
    the active profile.

    A consumer that cannot read the profile has to restate it, and both consumer
    generators did: the ordered phase list appeared twice in each, once as prose
    and once as `gated_by_phases`, which decides what must be COMPLETE before a
    test phase runs. A phase added to the profile was scanned into `phases` and
    absent from `gated_by_phases`, so the test phase ran without it (F-14). The
    profile id was typed too, in 29 places, which is why a second profile could
    not be started without editing them.

    Nothing here is a consumer's to keep, so there is no `preserve`: it is
    regenerated whole every time."""
    prof = CFG.profile
    tracks = {}
    for track in CFG.tracks:
        plans = {}
        for plan in prof.plans(track):
            plans[plan] = {
                "package": CFG.tracks[track]["packages"][plan],
                "phases": [{"key": ph.key, "display": ph.display, "folder": ph.folder,
                            "never_split": ph.never_split, "sub_bearing": ph.sub_bearing,
                            "integration": ph.integration, "binds_api": ph.binds_api,
                            **({"sub_labels": list(ph.sub_labels)} if ph.sub_labels else {}),
                            **({"split_threshold": ph.split_threshold} if ph.split_threshold else {})}
                           for ph in prof.phases(track, plan)],
            }
        tracks[track] = {
            "repo": CFG.track_repo(track),
            "exec_stage": CFG.tracks[track]["exec_stage"],
            "partition": CFG.partitions()[CFG.track_partition(track)],
            "delivery": CFG.partitions()[CFG.track_delivery(track)],
            "plans": plans,
        }
    return {
        "profile": prof.id,
        "project_file": CFG.project["file"],
        "paths": {k: CFG.paths[k] for k in (CFG.external.get("keys") or ()) if isinstance(CFG.paths[k], str)},
        "module_dirs": dict(CFG.paths["module"]),
        "tracks": tracks,
        "languages": prof.languages,
    }
    # No timestamp: the same profile must produce the same bytes, or every
    # publish reports a change and "unchanged" stops meaning anything. The
    # profile is the whole input; when it moves, this moves.


def pub_modules_registry(spec: dict, existing: list[dict]) -> dict:
    """The published module registry, derived from the ONE authority this factory
    recognises for the module set and its versions: the filesystem (versioning.authority).

    Two rules keep a derived file from destroying what it did not author:
      * `preserve` — fields the factory has no opinion about (a human-written description,
        the moment a module was first registered) are carried over from the copy already
        on disk instead of being regenerated. A rewrite that silently blanked descriptions
        would be indistinguishable from an intentional edit in the consumer's diff.
      * `additive` — a module that exists in a consumer's copy but not in this factory
        (registered by an earlier toolchain, or built before this factory existed) is KEPT
        exactly as it stands. Deriving is not a licence to forget.
    """
    preserve = spec.get("preserve", [])
    key = "modules"
    merged: dict = {}
    for prior in existing:                      # consumer copies first — oldest facts win for `preserve`
        for code, row in (prior.get(key) or {}).items():
            merged.setdefault(code, {}).update(row)
    for mod in CFG.modules():
        row = merged.setdefault(mod, {})
        man = module_manifest(mod)
        # `preserve` yields to the factory only where the factory actually states the field:
        # a manifest that carries a description is an authored fact, not a regenerated blank.
        keep = {f: row[f] for f in preserve if f in row and not man.get(f)}
        versions = CFG.module_versions(mod)
        row.update({"code": mod, "description": man.get("description", ""),
                    "registered_at": man.get("created_at") or now_iso(),
                    "versions": versions, "current_version": (max(versions) if versions else None)})
        row.update(keep)
    return {key: {c: merged[c] for c in sorted(merged, key=lambda c: merged[c].get("registered_at") or "")}}


# A publication names its builder in factory.yaml; lint refuses a name that does
# not resolve here. Adding a publication with a NEW derivation is new code, and
# says so, instead of failing as a KeyError at the moment someone publishes.
BUILDERS = {
    "modules_registry": pub_modules_registry,
    "profile_summary": pub_profile_summary,
}


def _publication_payload(name: str, existing: list[dict]) -> dict:
    spec = CFG.publications[name]
    return _PUBLICATION_BUILDERS[spec["builder"]](spec, existing)


def module_manifest(mod: str) -> dict:
    """The module's own manifest — the factory-side place where a module states the
    facts a consumer's registry copy shows (when it was registered, what it is)."""
    return read_json(CFG.module_root(mod) / CFG.paths["module"]["manifest_file"], {}) or {}




def payload(name: str, existing: list[dict]) -> dict:
    spec = CFG.publications[name]
    return BUILDERS[spec["builder"]](spec, existing)
