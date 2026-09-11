"""
Resolution checks — the half of `gov.py analyze` that asks whether a reference
RESOLVES, not whether it is shaped right.

Every defect these cover shipped past a plan whose own prose self-check reported
`PASSED ✓ — 0 findings`, because each of its assertions was true as literally
checked: the traces target existed, the DBF was cited, the RULE had an error code
and an API, the path was a string. None of them asked whether two artifacts AGREE
on a value, whether a cited file EXISTS, whether a cross-module dependency is on
something the target module really produces, or where the data a rule reads comes
from. These tests pin those questions.

Plus a golden-output regression over the rendered engine briefs: one assertion set
that fails the moment a profile value changes without everything downstream of it
following — the single cause behind the PK-strategy, error-format and path defects.
"""
from __future__ import annotations

import json

import pytest

from config import CFG
import analyze as an
import dispatch as dp
import gov
import orchfx as fx
from test_orchestrator import orch_root, _git   # noqa: F401  (fixture + helper)


# ── a module whose artifacts all resolve ────────────────────────────────────

@pytest.fixture
def module(orch_root, mod):
    """Every pass-1 artifact of one module, written and committed."""
    for s in ("domain-profile", "P-1", "P0", "P0.5"):
        fx.write_stage(s, mod)
    gov.approve("prd-approval", mod, 1, "tester", no_commit=True)
    for s in ("P1", "P2", "P3.1"):
        fx.write_stage(s, mod)
    from toolkit import structure as tk
    tk.ensure_structure(mod, 1)
    return mod


def _ctx(mod):
    import state as st
    st.build_state(mod, 1)
    return an.Ctx(mod, 1)


def _artifact(mod, stage, artifact):
    return CFG.artifact_path(mod, stage, artifact, 1)


def _rewrite(path, old, new):
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture does not contain {old!r}"
    path.write_text(text.replace(old, new), encoding="utf-8")


# ── value-agreement ─────────────────────────────────────────────────────────
# The acceptance case from the build report: reintroduce a one-character column
# typo in the plan and the check must fail.

def _column_args():
    """The C7 value-agreement clause, read from the contract rather than retyped."""
    import render
    for c in render.contracts_from_doc(CFG.reload()):
        for cl in c.get("clauses", []):
            if cl["check"] == "value-agreement":
                return cl["args"]
    pytest.skip("no value-agreement clause declared")


def test_a_column_both_artifacts_spell_the_same_way_is_clean(module):
    args = _column_args()
    assert an._c_value_agreement(_ctx(module), args, "CRITICAL") == []


def test_one_character_of_drift_in_a_column_name_is_a_finding(module):
    """55 columns agreeing and one diverging is a transcription bug — the exact
    class the plan is forbidden to guess at, and the one nothing caught."""
    args = _column_args()
    ctx = _ctx(module)
    binding = ctx.text(args["binding"])
    truth = next(iter(an._binding_lines(binding, args["kind"]).items()), None)
    assert truth, "fixture declares no bound physical name to diverge from"
    rid, names = truth
    column = sorted(names)[0]
    target = _artifact(module, CFG.id_atoms()[args["kind"]]["owner"], args["binding"])
    plan = _artifact(module, "P3.1", args["against"][0])
    plan.write_text(plan.read_text(encoding="utf-8") + f"\n| {rid} | prop | {column[:-1]} | type |\n", encoding="utf-8")

    fs = an._c_value_agreement(_ctx(module), args, "CRITICAL")
    assert len(fs) == 1 and rid in fs[0].message and column in fs[0].message
    assert target.exists()


def test_an_artifact_that_names_no_column_for_an_id_is_not_a_finding(module):
    """The plan index and the alignment manifest cite a DBF without naming its
    column. Silence is not disagreement."""
    args = _column_args()
    ctx = _ctx(module)
    rid = next(iter(an._binding_lines(ctx.text(args["binding"]), args["kind"])))
    plan = _artifact(module, "P3.1", args["against"][0])
    plan.write_text(plan.read_text(encoding="utf-8") + f"\n| {rid} | someProperty | Yes | —  |\n", encoding="utf-8")
    assert an._c_value_agreement(_ctx(module), args, "CRITICAL") == []


def test_a_config_address_is_not_a_column(module):
    """`profile.conventions.entity_defaults.lookup` on a DBF row is an address,
    not a physical name — reading it as one would flag every well-formed plan."""
    args = _column_args()
    ctx = _ctx(module)
    rid = next(iter(an._binding_lines(ctx.text(args["binding"]), args["kind"])))
    plan = _artifact(module, "P3.1", args["against"][0])
    plan.write_text(plan.read_text(encoding="utf-8")
                    + f"\n{rid} — matches `profile.conventions.entity_defaults.master` exactly\n", encoding="utf-8")
    assert an._c_value_agreement(_ctx(module), args, "CRITICAL") == []


# ── data-source ─────────────────────────────────────────────────────────────

_DS = {"kind": "RULE", "label": "Data source", "resolves_to": ["ENT"], "deferral": "DEFERRED"}


def test_a_rule_that_names_the_field_it_reads_is_clean(module):
    assert an._c_data_source(_ctx(module), _DS, "CRITICAL") == []


def test_a_rule_with_no_declared_input_is_a_finding(module):
    """A rule can have a trace, an error code and an enforcing endpoint and still
    be unenforceable: nothing in the module can record the value its check reads."""
    srs = _artifact(module, "P1", "srs")
    _rewrite(srs, f"  Data source: {fx.mid('ENT', module, 1)}.{fx.RULE_FIELD}", "  Note       : —")
    fs = an._c_data_source(_ctx(module), _DS, "CRITICAL")
    assert len(fs) == 1 and "no stated origin" in fs[0].message


def test_an_honest_deferral_passes(module):
    """`DEFERRED — no declaration surface in this version` is a truthful output
    and far more useful downstream than a silently unenforceable rule."""
    srs = _artifact(module, "P1", "srs")
    _rewrite(srs, f"  Data source: {fx.mid('ENT', module, 1)}.{fx.RULE_FIELD}",
             "  Data source: DEFERRED — no declaration surface in this version")
    assert an._c_data_source(_ctx(module), _DS, "CRITICAL") == []


def test_a_rule_reading_a_field_no_column_backs_is_a_finding(module):
    """The stronger downstream form: the field is named, but the db-script binds
    no column to it, so the check still can never fire."""
    args = dict(_DS, bound_in="db-script")
    srs = _artifact(module, "P1", "srs")
    _rewrite(srs, f"  Data source: {fx.mid('ENT', module, 1)}.{fx.RULE_FIELD}",
             f"  Data source: {fx.mid('ENT', module, 1)}.conflictingPair")
    fs = an._c_data_source(_ctx(module), args, "CRITICAL")
    assert len(fs) == 1 and "can never fire" in fs[0].message


# ── code-format ─────────────────────────────────────────────────────────────

_FMT = {"artifact": ["backend-execution-plan"], "format": "stack.backend.api.error_code_format"}


def test_a_declared_format_no_emitted_value_obeys_is_a_finding(module):
    """The declaration and the values are one fact. A format string maintained as
    free text is inherited by the next module as a convention no catalog obeys."""
    fmt = CFG.profile.get(_FMT["format"])
    if not fmt:
        pytest.skip("profile declares no error_code_format")
    plan = _artifact(module, "P3.1", "backend-execution-plan")
    plan.write_text(plan.read_text(encoding="utf-8")
                    + f"\nRuntime `code` format: `{module}-<3-digit-sequence>` (module-scoped).\n", encoding="utf-8")
    fs = an._c_code_format(_ctx(module), _FMT, "MAJOR")
    assert any("declares the code format" in f.message for f in fs)


def test_codes_that_are_instances_of_the_declared_format_are_clean(module):
    fmt = CFG.profile.get(_FMT["format"])
    if not fmt:
        pytest.skip("profile declares no error_code_format")
    plan = _artifact(module, "P3.1", "backend-execution-plan")
    plan.write_text(plan.read_text(encoding="utf-8")
                    + f"\nFormat `{fmt}`.\n| {module}-409-DUP | dup |\n| {module}-500 | server |\n", encoding="utf-8")
    fs = [f for f in an._c_code_format(_ctx(module), _FMT, "MAJOR") if f.severity != "MINOR"]
    assert fs == []


def test_a_section_reference_is_not_an_error_code(module):
    """`<MOD>-BE` is a heading address; only a module code followed by a digit is
    a candidate value."""
    plan = _artifact(module, "P3.1", "backend-execution-plan")
    plan.write_text(plan.read_text(encoding="utf-8") + f"\nSee §{module}-BE below.\n", encoding="utf-8")
    assert not any(f"{module}-BE" in f.message for f in an._c_code_format(_ctx(module), _FMT, "MAJOR"))


# ── xref-resolve ────────────────────────────────────────────────────────────

def test_an_endpoint_the_target_module_never_defined_is_a_finding(module):
    """Each module's analyze validates only its own artifacts, so a dependency on
    an API the target never generates passes both modules' checks — unless the
    contract is resolved across the module set."""
    other = next(m for m in CFG.profile.vocabulary["module_prefixes"] if m != module)
    from toolkit import structure as tk
    tk.ensure_structure(other, 1)
    fx.write_stage("P1", other)                       # the other module exists, but defines no API
    plan = _artifact(module, "P3.1", "backend-execution-plan")
    ghost = CFG.make_id("API", other, 99)
    plan.write_text(plan.read_text(encoding="utf-8")
                    + f"\nInterface: REST call — {ghost} on {other}\n", encoding="utf-8")
    fs = an._c_xref_resolve(_ctx(module), {"artifact": ["backend-execution-plan"]}, "CRITICAL")
    assert len(fs) == 1 and ghost in fs[0].message and "never produced" in fs[0].message


def test_an_id_of_an_undeclared_module_is_a_finding(module):
    plan = _artifact(module, "P3.1", "backend-execution-plan")
    ghost = CFG.make_id("API", "ZZZ", 1)
    plan.write_text(plan.read_text(encoding="utf-8") + f"\nCalls {ghost}.\n", encoding="utf-8")
    fs = an._c_xref_resolve(_ctx(module), {"artifact": ["backend-execution-plan"]}, "CRITICAL")
    assert len(fs) == 1 and "does not declare" in fs[0].message


def test_own_module_ids_are_never_cross_references(module):
    assert an._c_xref_resolve(_ctx(module), {"artifact": ["backend-execution-plan"]}, "CRITICAL") == []


# ── refs-exist ──────────────────────────────────────────────────────────────

_REFS = {"kind": "ADR", "dir": "decisions", "file_pattern": "adr_file"}


def test_an_adr_cited_by_path_but_never_written_is_a_finding(module):
    """Cited 30 times across two artifacts and present nowhere: the implementing
    agent could not read it and had to work from restatements."""
    plan = _artifact(module, "P3.1", "backend-execution-plan")
    adr = fx.mid("ADR", module, 7)
    plan.write_text(plan.read_text(encoding="utf-8") + f"\nDecision: {adr} (see decisions/{module}/).\n", encoding="utf-8")
    fs = an._c_refs_exist(_ctx(module), _REFS, "CRITICAL")
    assert len(fs) == 1 and adr in fs[0].message


def test_an_adr_that_exists_resolves(module):
    plan = _artifact(module, "P3.1", "backend-execution-plan")
    adr = fx.mid("ADR", module, 7)
    plan.write_text(plan.read_text(encoding="utf-8") + f"\nDecision: {adr}.\n", encoding="utf-8")
    d = CFG.decisions_dir(module)
    d.mkdir(parents=True, exist_ok=True)
    (d / CFG.fmt(CFG.naming["adr_file"], mod=module, seq=7)).write_text("# decision\n", encoding="utf-8")
    assert an._c_refs_exist(_ctx(module), _REFS, "CRITICAL") == []


# ── paths-resolve ───────────────────────────────────────────────────────────

_PATHS = {"files": ["manifest_file"]}


def test_a_freshly_written_manifest_fully_resolves(module):
    assert an._c_paths_resolve(_ctx(module), _PATHS, "CRITICAL") == []


def test_a_manifest_carrying_a_repo_prefix_does_not_resolve(module):
    """The regression itself: paths written with the producing repo's own prefix
    resolve in that repo and nowhere else."""
    path = CFG.version_root(module, 1) / CFG.paths["module"]["manifest_file"]
    data = json.loads(path.read_text(encoding="utf-8"))
    data["root"] = f"{CFG.profile.id}/modules/{module}"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    fs = an._c_paths_resolve(_ctx(module), _PATHS, "CRITICAL")
    assert len(fs) == 1 and "resolves to nothing" in fs[0].message


# ── golden output: the rendered briefs follow the profile ───────────────────
# Three of the shipped defects share one cause — a profile/template value changed
# for a newer generation without everything downstream of it following, and no
# test that would have noticed. These are that test.

def _brief(stage_id, mod):
    return dp.render_engine(CFG.stage(stage_id), mod, 1)


def test_the_db_engine_instructs_the_pk_strategy_the_profile_declares(orch_root, mod):
    """PK generation is a profile decision (`stack.db.pk_generation`), never a
    dialect default: one database cannot carry two PK strategies."""
    db = CFG.profile.stack["db"]
    strategy = db.get("pk_generation")
    assert strategy, "the profile must declare its PK strategy explicitly"
    brief = _brief("P2", mod)
    assert f"pk_generation = `{strategy}`" in brief
    identity = db["syntax_map"]["identity"][db["dialects"][0]]
    sequence = db["syntax_map"]["sequence"][db["dialects"][0]]
    if strategy == "sequence":
        assert sequence in brief and db["naming"]["sequence_pattern"] in brief
        assert f"`{identity}` must not appear anywhere in the script" in brief
        assert "MANDATORY: one per table" in brief
    else:
        assert identity in brief


def test_the_emitted_sequence_syntax_is_the_target_dialects_own(orch_root, mod):
    """`NO CACHE` is Oracle's spelling and fails on PostgreSQL — the syntax comes
    from the dialect's own syntax_map row, never from the other dialect's."""
    db = CFG.profile.stack["db"]
    target, *others = db["dialects"]
    brief = _brief("P2", mod)
    for other in others:
        foreign = db["syntax_map"]["sequence"][other]
        assert foreign not in brief, f"{other} sequence syntax leaked into the {target} brief"


def test_the_plan_engine_carries_the_generation_object_into_the_bindings(orch_root, mod):
    """The implementer reads the sequence name from the plan rather than deriving it."""
    strategy = CFG.profile.stack["db"].get("pk_generation")
    brief = _brief("P3.1", mod)
    assert f"PK generation `{strategy}`" in brief
    if strategy == "sequence":
        assert "sequence <exact name from the db-script BLOCK 1>" in brief


def test_the_plan_engine_derives_the_error_format_from_the_profile(orch_root, mod):
    fmt = CFG.profile.get("stack.backend.api.error_code_format")
    assert fmt, "the profile must declare the error-code format the plan states"
    brief = _brief("P3.1", mod)
    assert fmt in brief and "never from free text" in brief


def test_the_srs_engine_requires_a_source_for_every_rules_input(orch_root, mod):
    brief = _brief("P1", mod)
    assert "Data source" in brief and "DEFERRED — no declaration surface in this version" in brief


def test_every_check_the_contracts_name_is_implemented(orch_root):
    """A clause naming a check `analyze` does not implement is silently skipped —
    the failure mode that lets a contract look enforced while enforcing nothing."""
    import render
    cfg = CFG.reload()
    declared = {cl["check"] for c in render.contracts_from_doc(cfg) for cl in c.get("clauses", [])}
    assert declared <= set(an.CHECKS), f"unimplemented: {sorted(declared - set(an.CHECKS))}"


# ── delivery: the tree must index itself in the repo it lands in ────────────

def test_the_delivered_tree_resolves_in_the_consumer_repo(orch_root, mod, tmp_path, monkeypatch):
    """Packages, the manifest, the execution state and the cited decision records
    all land together, and every path either file emits resolves from where it sits."""
    from test_orchestrator import _consumer, _run_pass1
    backend = _consumer(tmp_path, monkeypatch, "backend")
    _run_pass1(orch_root, mod, tmp_path, monkeypatch)
    d = CFG.decisions_dir(mod)
    d.mkdir(parents=True, exist_ok=True)
    (d / CFG.fmt(CFG.naming["adr_file"], mod=mod, seq=1)).write_text("# a decision the plan cites\n", encoding="utf-8")

    assert gov.main(["split", "--track", "backend", "-m", mod, "-v", "1"]) == gov.OK
    assert gov.cmd_deliver("backend", mod, 1, push=False) == gov.OK

    dest = backend / CFG.fmt(CFG.repos["backend"]["deliver_to"], mod=mod)
    index = json.loads((dest / CFG.paths["module"]["manifest_file"]).read_text())
    state = json.loads((dest / CFG.delivery["execution_state"]["file"]).read_text())

    # no path in either file dangles — checked against the consumer repo, not the factory
    assert gov._dangling(index, dest, backend) == []
    assert gov._dangling(state["paths"], dest, backend) == []
    # and the two files cannot disagree: the state takes its paths from the index
    assert state["paths"]["plans"] == index["plans"]
    assert state["paths"]["packages"] == index["packages"]
    for ph in state["phases"]:
        assert (dest / ph["package"]).is_dir()
    # the decision records the plans cite travelled with them
    assert (dest / index["decisions_dir"] / CFG.fmt(CFG.naming["adr_file"], mod=mod, seq=1)).exists()
    # and the place the consumer is asked to publish its api-docs actually exists
    assert (backend / index["publishes"]["api-docs"]).is_dir()
