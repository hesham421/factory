"""
Orchestrator fixtures — a consistent, profile-driven set of module artifacts
that satisfies every contract of shared/ARTIFACT-CONTRACTS.md, generated from
CFG (module prefix, phases, atoms, languages) so nothing domain-specific is
pinned here. Used by test_orchestrator.py as the end-to-end dry run.
"""
from __future__ import annotations

import re
from pathlib import Path

from config import CFG

_AR = "نص عربي"     # any Arabic-script token — languages.require_all needs every script present
RULE_FIELD = "code"   # the ENT field the fixture's rule reads (and the db-script binds)
COLUMNS = {1: "main_code", 2: "created_at"}   # DBF seq → physical column, as the db-script declares it


def _lang_tag() -> str:
    langs = CFG.profile.languages
    return (" · " + _AR) if langs.get("require_all") and "ar" in langs["all"] else ""


def mid(prefix: str, mod: str, seq: int) -> str:
    return CFG.make_id(prefix, mod, seq)


def categories() -> list[str]:
    doc = CFG.dir("shared") / "REGISTRY-SCHEMA.md"
    return sorted(set(re.findall(r"\bCAT-\d+\b", doc.read_text(encoding="utf-8"))), key=lambda c: int(c.split("-")[1])) if doc.exists() else []


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip("\n") + "\n", encoding="utf-8")
    return path


# ── platform-level ──────────────────────────────────────────────────────────

def domain_profile() -> str:
    return f"""# Domain profile — {CFG.profile.data['identity']['display']}{_lang_tag()}
Scope: sample platform for the dry run{_lang_tag()}.
## Steering
Vocabulary: {', '.join(CFG.profile.vocabulary['module_prefixes'])}.
"""


def project_registry(mod: str) -> str:
    rows = "\n".join(f"| {c} | mapped |" for c in categories())
    return f"""# Project registry{_lang_tag()}
| Category | Status |
|---|---|
{rows}

Modules: {mod}
"""


# ── pass 1 ──────────────────────────────────────────────────────────────────

def platform_summary(mod: str) -> str:
    return f"# Platform summary{_lang_tag()}\n| Module | Tier |\n|---|---|\n| {mod} | 0 |\n"


def business_policies(mod: str, n: int = 2) -> str:
    out = [f"# Business policies — {mod}{_lang_tag()}", ""]
    for i in range(1, n + 1):
        out += [f"### {mid('POL', mod, i)} — policy {i}{_lang_tag()}",
                f"  Statement  : The system shall enforce policy {i} for every record.", ""]
    return "\n".join(out)


def module_registry(mod: str, n: int = 2) -> str:
    pols = ", ".join(mid("POL", mod, i) for i in range(1, n + 1))
    return f"# Module registry — {mod}{_lang_tag()}\nPolicies: {pols}\n"


def prd(mod: str, n: int = 2) -> str:
    out = [f"# PRD — {mod}{_lang_tag()}", ""]
    for i in range(1, n + 1):
        out += [f"### {mid('US', mod, i)} — story {i}{_lang_tag()}",
                f"  As a user I want feature {i}.",
                f"  Traces     : {mid('POL', mod, i)}", ""]
    return "\n".join(out)


def srs(mod: str, n_req: int = 2, start: int = 1) -> str:
    out = [f"# SRS — {mod}{_lang_tag()}", "", "## A4 — Functional requirements"]
    for i in range(start, start + n_req):
        us = mid("US", mod, min(i, 2))
        out += [f"### {mid('REQ', mod, i)} — requirement {i}{_lang_tag()}",
                "  Pattern    : event",
                f"  Statement  : When a user submits form {i}, the system shall validate and store the record.",
                f"  Traces     : {us}",
                f"  Entities   : {mid('ENT', mod, 1)}", "",
                f"#### {mid('AC', mod, i)} — [{mid('REQ', mod, i)}]",
                "  Given  : a valid form", "  When   : the user submits", f"  Then   : the record is stored{_lang_tag()}", ""]
    out += ["## A2 — Entities", f"### {mid('ENT', mod, 1)} — main entity{_lang_tag()}", "  Kind: master", ""]
    out += ["## A5 — Business rules", f"### {mid('RULE', mod, 1)} — rule 1{_lang_tag()}",
            "  Statement  : The system shall reject duplicates.", f"  Traces     : {mid('REQ', mod, 1)}",
            # every rule says where the data its check READS comes from (C5.12 / C6.9)
            f"  Data source: {mid('ENT', mod, 1)}.{RULE_FIELD}", ""]
    out += ["# PART B", f"## {mid('SCR-REQ', mod, 1)} — main screen{_lang_tag()}",
            f"  Entities     : {mid('ENT', mod, 1)}", f"  Traces       : {', '.join(mid('REQ', mod, i) for i in range(start, start + n_req))}", ""]
    return "\n".join(out)


def registry_list(title: str, ids: list[str]) -> str:
    return f"# {title}{_lang_tag()}\n" + "\n".join(f"- {i}" for i in ids) + "\n"


def registry_srs(mod: str, n_req: int = 2, end: int | None = None) -> str:
    end = end or n_req
    ids = [mid("REQ", mod, i) for i in range(1, end + 1)] + [mid("AC", mod, i) for i in range(1, end + 1)]
    ids += [mid("ENT", mod, 1), mid("RULE", mod, 1), mid("SCR-REQ", mod, 1)]
    return registry_list("registry-srs", ids)


def db_script(mod: str) -> str:
    """The structural truth, including the field registry and the column comments —
    the two places a DBF's physical name is declared (value-agreement reads them)."""
    table = f"{mod}_MAIN"
    return "\n".join([
        f"# DB script — {mod}{_lang_tag()}", "",
        "## Field registry", "| DBF id | Column | Type | Traces |", "|---|---|---|---|",
        f"| {mid('DBF', mod, 1)} | {COLUMNS[1]} | text | {mid('ENT', mod, 1)}.{RULE_FIELD} |",
        f"| {mid('DBF', mod, 2)} | {COLUMNS[2]} | timestamp | {mid('ENT', mod, 1)}.label |", "",
        f"### {mid('DBF', mod, 1)} — main table{_lang_tag()}",
        # the field RULE-1 reads, bound to a column here — what C6.9 resolves
        f"  Traces     : {mid('REQ', mod, 1)}, {mid('ENT', mod, 1)}.{RULE_FIELD}", "",
        f"### {mid('DBF', mod, 2)} — audit columns{_lang_tag()}",
        f"  Traces     : {mid('REQ', mod, 2)}, {mid('ENT', mod, 1)}", "",
        f"COMMENT ON COLUMN {table}.{COLUMNS[1]} IS '{mid('DBF', mod, 1)}';",
        f"COMMENT ON COLUMN {table}.{COLUMNS[2]} IS '{mid('DBF', mod, 2)}';", "",
        f"### {mid('XM', mod, 1)} — lookup dependency{_lang_tag()}",
        f"  Kind       : SOFT-READ", f"  Traces     : {mid('REQ', mod, 1)}", ""])


def registry_db(mod: str) -> str:
    return registry_list("registry-db", [mid("DBF", mod, 1), mid("DBF", mod, 2), mid("XM", mod, 1)])


def self_check_block() -> str:
    """The self-check block the active profile declares — written with the verdict the
    orchestrator will stamp over. A profile that declares none gets nothing (C7.15's
    `when: profile.self_check` means the clause never runs there either)."""
    spec = CFG.profile.self_check
    if not spec:
        return ""
    return (f"\n## Self-check ({spec['block']})\n\n```\n"
            f"{spec['verdict_label']}  {spec['pass_token']} — 0 {spec['findings_noun']}\n```\n")


def _phase_atom_kind(phase) -> str | None:
    t = phase.split_threshold
    return t["kind"] if t else None


def backend_plan(mod: str) -> str:
    """One PHASE block per profile phase, atoms placed in the phases whose threshold counts them."""
    req1, req2, dbf1, xm1 = mid("REQ", mod, 1), mid("REQ", mod, 2), mid("DBF", mod, 1), mid("XM", mod, 1)
    out = [f"# Backend execution plan — {mod}{_lang_tag()}", "", "Plan index and alignment manifest.", ""]
    api_done = xm_done = False
    for p in CFG.profile.phases("backend", "exec"):
        out.append(f"<!-- PHASE:{p.key}:START traces={req1} -->")
        out.append(f"## {p.display}{_lang_tag()}")
        kind = _phase_atom_kind(p)
        if kind == "API" and not api_done:
            out += [f"<!-- API:{mid('API', mod, 1)}:START traces={req1},{dbf1} -->", f"### {mid('API', mod, 1)} — create endpoint", "POST create.",
                    f"<!-- API:{mid('API', mod, 1)}:END -->",
                    f"<!-- API:{mid('API', mod, 2)}:START traces={req2},{dbf1} -->", f"### {mid('API', mod, 2)} — search endpoint", "GET search.",
                    f"<!-- API:{mid('API', mod, 2)}:END -->", f"### {mid('QR', mod, 1)} — search query", f"  Traces     : {req2}"]
            api_done = True
        elif kind == "XM" and not xm_done:
            out += [f"<!-- XM:{xm1}:START traces={req1} -->", f"### {xm1} — consume lookup", "Read-only lookup.", f"<!-- XM:{xm1}:END -->"]
            xm_done = True
        else:
            out.append(f"Work items for {p.key}.")
        out.append(f"<!-- PHASE:{p.key}:END -->")
        out.append("")
    out.append(self_check_block())
    return "\n".join(out)


def registry_exec_be(mod: str) -> str:
    return registry_list("registry-exec-be", [mid("API", mod, 1), mid("API", mod, 2), mid("QR", mod, 1), mid("XM", mod, 1)])


# ── inputs / pass 2 ─────────────────────────────────────────────────────────

def api_docs(mod: str) -> str:
    return f"# API docs — {mod}\n- {mid('API', mod, 1)} POST /x\n- {mid('API', mod, 2)} GET /x\n"


def flow_diagram(mod: str) -> str:
    return f"# Flow — {mod}{_lang_tag()}\n{mid('US', mod, 1)} → {mid('SCR', mod, 1)}\n"


def ui_ux_spec(mod: str) -> str:
    return "\n".join([
        f"# UI/UX spec — {mod}{_lang_tag()}", "",
        f"### {mid('UXD', mod, 1)} — composite screen pattern{_lang_tag()}",
        f"  Traces     : {mid('REQ', mod, 1)}, {mid('AC', mod, 1)}", "",
        f"### {mid('SCR', mod, 1)} — main screen{_lang_tag()}",
        f"  Traces     : {mid('REQ', mod, 1)}, {mid('UXD', mod, 1)}", ""])


def frontend_plan(mod: str) -> str:
    req1, ac1, api1, uxd1, scr1 = mid("REQ", mod, 1), mid("AC", mod, 1), mid("API", mod, 1), mid("UXD", mod, 1), mid("SCR", mod, 1)
    out = [f"# Frontend execution plan — {mod}{_lang_tag()}", ""]
    for p in CFG.profile.phases("frontend", "exec"):
        out.append(f"<!-- PHASE:{p.key}:START traces={req1},{uxd1} -->")
        out.append(f"## {p.display}{_lang_tag()}")
        if p.sub_bearing:
            out += [f"<!-- SUB:{p.key}-{scr1}:START traces={req1},{ac1},{api1},{scr1},{uxd1} -->",
                    f"### {scr1} in {p.key}", f"Uses {api1}.", f"<!-- SUB:{p.key}-{scr1}:END -->"]
        else:
            out.append(f"Work items for {p.key} referencing {scr1}.")
        out.append(f"<!-- PHASE:{p.key}:END -->")
        out.append("")
    out.append(self_check_block())
    return "\n".join(out)


def registry_exec_fe(mod: str) -> str:
    return registry_list("registry-exec-fe", [mid("UXD", mod, 1), mid("SCR", mod, 1)])


# ── standalone: test-gen ────────────────────────────────────────────────────

def _test_plan(mod: str, track: str, first_tc: int) -> str:
    out = [f"# {track} test plan — {mod}{_lang_tag()}", ""]
    n = first_tc
    for p in CFG.profile.phases(track, "test"):
        out.append(f"<!-- PHASE:{p.key}:START traces={mid('AC', mod, 1)} -->")
        out.append(f"## {p.display}{_lang_tag()}")
        for i in (1, 2):
            out += [f"<!-- TC:{mid('TC', mod, n)}:START traces={mid('AC', mod, i)} -->",
                    f"### {mid('TC', mod, n)} — derived from {mid('AC', mod, i)}", "Given/When/Then → steps.",
                    f"<!-- TC:{mid('TC', mod, n)}:END -->"]
            n += 1
        out.append(f"<!-- PHASE:{p.key}:END -->")
    return "\n".join(out)


def backend_test_plan(mod: str) -> str:  return _test_plan(mod, "backend", 1)
def frontend_test_plan(mod: str) -> str: return _test_plan(mod, "frontend", 3)
def test_manifest(mod: str) -> str:      return f"# Test execution manifest — {mod}\nTCs: {mid('TC', mod, 1)} … {mid('TC', mod, 4)}\n"


# ── writers keyed by stage ──────────────────────────────────────────────────

def write_stage(stage_id: str, mod: str, version: int = 1, **kw) -> list[Path]:
    """Write every artifact of a stage for the dry run (generator per artifact id)."""
    gens = {
        "domain-profile": lambda: domain_profile(),
        "project-registry": lambda: project_registry(mod),
        "platform-summary": lambda: platform_summary(mod),
        "module-registry": lambda: module_registry(mod),
        "business-policies": lambda: business_policies(mod),
        "prd": lambda: prd(mod),
        "srs": lambda: srs(mod, **kw), "registry-srs": lambda: registry_srs(mod, **kw),
        "db-script": lambda: db_script(mod), "registry-db": lambda: registry_db(mod),
        "backend-execution-plan": lambda: backend_plan(mod), "registry-exec-be": lambda: registry_exec_be(mod),
        "flow-diagram": lambda: flow_diagram(mod), "ui-ux-spec": lambda: ui_ux_spec(mod),
        "frontend-execution-plan": lambda: frontend_plan(mod), "registry-exec-fe": lambda: registry_exec_fe(mod),
        "backend-test-plan": lambda: backend_test_plan(mod), "frontend-test-plan": lambda: frontend_test_plan(mod),
        "test-execution-manifest": lambda: test_manifest(mod),
    }
    st = CFG.stage(stage_id)
    out = []
    for a in st.produces:
        if a.artifact in gens:
            out.append(write(CFG.artifact_path(mod, st.id, a.artifact, version), gens[a.artifact]()))
    return out


def write_input(name: str, mod: str, version: int = 1) -> Path:
    spec = CFG.inputs[name]
    return write(CFG.inputs_dir(mod, version) / CFG.fmt(spec["file"], mod=mod), api_docs(mod))
