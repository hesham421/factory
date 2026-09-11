"""
The "silent success" defect class (and its two enablers).

A frontend split once reported success while writing nothing: its toolkit was a
marker-grammar version and a filename convention behind factory.yaml, and every
"not found / nothing to parse / nothing to write" branch returned success. This
suite pins the factory-side toolkit against the same class:

  · nothing parsed / nothing written / nothing archived is NEVER a success
  · a module emitted with a NEWER marker grammar is refused before parsing,
    not mis-parsed into silence
  · a factory.yaml fact the tool has never seen flows through with ZERO tool
    code change (the no-hardcode guarantee, proven rather than asserted)

Nothing here spells a phase key, plan name, filename or ID prefix: every value
comes from factory.yaml / the active profile, exactly like the fixtures do.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from config import CFG
from toolkit import ensure_structure, load_manifest, split, verify
from toolkit.archive import archive
from toolkit.common import markers_schema_version, plan_key
from toolkit.structure import MarkerSchemaError, require_supported_marker_schema

import planfx as fx

TOOLS_DIR = Path(__file__).resolve().parent.parent


def _put_plan(mod, track, plan, text, version=1):
    ensure_structure(mod, version)
    p = CFG.plan_path(mod, track, plan, version)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _run(root, *argv):
    """Run a governance-tools CLI against an isolated factory root."""
    return subprocess.run([sys.executable, *argv], cwd=TOOLS_DIR, capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin", "GOV_FACTORY_ROOT": str(root),
                               "PYTHONPATH": str(TOOLS_DIR)})


def _first_track_plan():
    from toolkit.common import track_plans
    return track_plans()[0]


# ── nothing parsed is not a pass ────────────────────────────────────────────

def test_split_hard_fails_when_the_plan_carries_no_phase_marker(factory_root, mod):
    """The defect verbatim: an un-annotated plan must not 'split' into success."""
    track, plan = _first_track_plan()
    _put_plan(mod, track, plan, "# A plan nobody marked up\n\nProse only.\n")
    rep = split(mod, track, plan, 1)
    assert rep.ok is False
    assert rep.errors, "an unmarked plan must produce an explicit error"
    g = fx.grammar(track, plan)
    joined = " ".join(rep.errors)
    assert g.phase_kind in joined                      # names what was missing
    assert str(rep.source.name) in joined              # names the file
    assert "never injects markers" in joined           # states the boundary


def test_nothing_is_written_and_no_status_is_set_for_an_unmarked_plan(factory_root, mod):
    track, plan = _first_track_plan()
    _put_plan(mod, track, plan, "# Unmarked\n\nProse.\n")
    split(mod, track, plan, 1)
    container = CFG.packages_dir(mod, track, plan, 1)
    # (ensure_structure pre-creates the folders with .gitkeep — content is what counts)
    assert list(container.rglob("*.md")) == []
    man = load_manifest(mod, 1) or {}
    assert man["status"]["split"][plan_key(track, plan)] is False


def test_the_whole_unsplit_plan_is_never_emitted_as_one_sections_file(factory_root, mod):
    """Before the fix an unmarked plan landed whole in the sections file and
    was recorded as split — worse than writing nothing."""
    from toolkit.splitter import SECTIONS_FILE
    track, plan = _first_track_plan()
    _put_plan(mod, track, plan, "# Unmarked\n\nEvery word of the plan.\n")
    split(mod, track, plan, 1)
    assert not (CFG.packages_dir(mod, track, plan, 1) / SECTIONS_FILE).exists()


def test_verification_that_checked_nothing_is_not_ok(factory_root, mod):
    """`ok = not missing and not mismatched` was True over an empty set."""
    track, plan = _first_track_plan()
    _put_plan(mod, track, plan, "# Unmarked\n\nProse.\n")
    ensure_structure(mod, 1)
    CFG.packages_dir(mod, track, plan, 1).mkdir(parents=True, exist_ok=True)
    out = verify(mod, track, plan, 1)
    assert out["checked"] == 0
    assert out["ok"] is False
    assert out["missing"], "an empty verification must say why it failed"


def test_a_well_formed_plan_still_splits_and_verifies(factory_root, mod):
    """The hard-stops must not cost the happy path."""
    track, plan = _first_track_plan()
    _put_plan(mod, track, plan, fx.exec_plan(mod, track, plan))
    rep = split(mod, track, plan, 1)
    assert rep.ok, (rep.errors, rep.findings, rep.verification)
    assert rep.verification["checked"] > 0
    assert (load_manifest(mod, 1))["status"]["split"][plan_key(track, plan)] is True


# ── the newer-grammar guard (the durable protection) ───────────────────────

def test_a_newer_marker_schema_is_refused_before_parsing(factory_root, mod):
    ensure_structure(mod, 1)
    path = CFG.version_root(mod, 1) / CFG.paths["module"]["manifest_file"]
    man = json.loads(path.read_text(encoding="utf-8"))
    man["markers_schema_version"] = markers_schema_version() + 1
    path.write_text(json.dumps(man), encoding="utf-8")
    with pytest.raises(MarkerSchemaError) as exc:
        require_supported_marker_schema(mod, 1)
    assert "Refusing to parse" in str(exc.value)


def test_split_refuses_a_module_emitted_with_a_newer_grammar(factory_root, mod):
    track, plan = _first_track_plan()
    _put_plan(mod, track, plan, fx.exec_plan(mod, track, plan))
    path = CFG.version_root(mod, 1) / CFG.paths["module"]["manifest_file"]
    man = json.loads(path.read_text(encoding="utf-8"))
    man["markers_schema_version"] = markers_schema_version() + 7
    path.write_text(json.dumps(man), encoding="utf-8")
    rep = split(mod, track, plan, 1)
    assert rep.ok is False and any("Refusing to parse" in e for e in rep.errors)


def test_the_current_schema_and_a_stampless_module_are_accepted(factory_root, mod):
    ensure_structure(mod, 1)
    assert require_supported_marker_schema(mod, 1) == markers_schema_version()
    path = CFG.version_root(mod, 1) / CFG.paths["module"]["manifest_file"]
    man = json.loads(path.read_text(encoding="utf-8"))
    man.pop("markers_schema_version", None)
    path.write_text(json.dumps(man), encoding="utf-8")
    assert require_supported_marker_schema(mod, 1) == markers_schema_version()


# ── archiving nothing is not a pass ────────────────────────────────────────

def test_archive_of_a_source_holding_no_artifact_is_an_error(factory_root, mod, tmp_path):
    src = tmp_path / "empty"
    src.mkdir()
    rep = archive(mod, 1, src)
    assert rep.ok is False and rep.errors
    assert (load_manifest(mod, 1) or {}).get("status", {}).get("archived") is not True


# ── the CLIs exit non-zero too ─────────────────────────────────────────────

def test_validate_only_exits_nonzero_when_nothing_was_found(factory_root, mod, tmp_path):
    track, plan = _first_track_plan()
    f = tmp_path / "unmarked.md"
    f.write_text("# Nothing marked up here\n", encoding="utf-8")
    r = _run(factory_root, "-m", "toolkit.splitter", "--track", track, "--plan", plan,
             "--validate-only", str(f))
    assert r.returncode != 0, r.stdout
    assert "ERROR" in r.stdout


def test_gov_split_blocks_when_the_module_has_no_plan_at_all(factory_root, mod):
    track, _ = _first_track_plan()
    ensure_structure(mod, 1)
    r = _run(factory_root, "gov.py", "split", "--module", mod, "--track", track)
    assert r.returncode != 0, r.stdout
    assert "nothing was split" in r.stdout


# ── the no-hardcode guarantee, PROVEN ──────────────────────────────────────

def _add_phase_to_profile(root: Path, track: str, plan: str, key: str) -> None:
    """Declare a brand-new phase in the profile — a value no tool has seen."""
    pf = root / "profiles" / f"{CFG.profile_id}.yaml"
    data = yaml.safe_load(pf.read_text(encoding="utf-8"))
    data["tracks"][track]["plans"][plan]["phases"].append(
        {"key": key, "display": key, "never_split": True})
    pf.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    CFG.reload()


def test_a_phase_key_the_tool_has_never_seen_flows_through_untouched(factory_root, mod):
    """
    THE no-hardcode proof: declare a new phase in factory.yaml's profile and the
    splitter must recognise it, create its folder and split its block — with ZERO
    tool code change. If any tool spelled the phase vocabulary, this fails.
    """
    track, plan = _first_track_plan()
    new_key = "BRAND-NEW-PHASE"
    _add_phase_to_profile(factory_root, track, plan, new_key)

    g = fx.grammar(track, plan)
    assert new_key in g.phase_by_key, "the grammar must read the phase from the profile"

    # The fixture builds the plan from the profile, so the new phase appears in
    # it without a line of fixture code either — end to end, the only thing that
    # changed is factory.yaml's profile.
    _put_plan(mod, track, plan, fx.exec_plan(mod, track, plan))

    rep = split(mod, track, plan, 1)
    assert rep.ok, (rep.errors, rep.findings, rep.verification)
    written = {p.name for p in rep.written}
    assert any(new_key in n for n in written), f"new phase produced no file: {written}"
    spec = g.phase_by_key[new_key]
    container = CFG.packages_dir(mod, track, plan, 1)
    from toolkit.common import flat_plan
    folder = container if flat_plan(plan) else container / spec.folder
    assert folder.exists(), "the new phase's folder must be created from the profile"


def test_an_unknown_phase_is_still_refused_after_the_vocabulary_grows(factory_root, mod):
    """Reading the vocabulary from the profile must not weaken the refusal of a
    key the profile does NOT declare."""
    track, plan = _first_track_plan()
    _add_phase_to_profile(factory_root, track, plan, "BRAND-NEW-PHASE")
    g = fx.grammar(track, plan)
    body = (fx.marker(g.phase_kind, "NOT-DECLARED-ANYWHERE", fx.START)
            + "x\n" + fx.marker(g.phase_kind, "NOT-DECLARED-ANYWHERE", fx.END))
    _put_plan(mod, track, plan, body)
    rep = split(mod, track, plan, 1)
    assert rep.ok is False
