"""`gov.py new-project` scaffolds a project repo — project.yaml, a profile
from the schema, the empty partitions, git — and `gov.py new-domain` adds a
second profile to the current one. Neither touches factory.yaml: the tool
carries no project fact, so nothing has to be reset between projects. The
same tool checkout then drives the new project the moment the variable
points at it, and its tool-side render is byte-identical under either."""
from __future__ import annotations

import json

import yaml

from config import CFG
import gov
from test_agnostic import TOY

OK, BLOCKED = gov.OK, gov.BLOCKED


def test_new_project_scaffolds_a_project_repo(factory_root, tmp_path, monkeypatch, capsys):
    target = tmp_path / "shop-governance"
    assert gov.cmd_new_project(target, "shop", "Shop Platform", None) == OK
    pj = yaml.safe_load((target / CFG.project["file"]).read_text(encoding="utf-8"))
    assert pj["project"]["id"] == "shop" and pj["profile"] == "shop"
    assert set(pj["repos"]) == {CFG.track_repo(t) for t in CFG.tracks}
    for repo, spec in pj["repos"].items():
        assert spec["checkout_env"] == CFG.fmt(CFG.project["consumer_env"], REPO=repo.upper())
    prof = target / CFG.paths["profiles"] / "shop.yaml"
    assert prof.exists() and "id: shop" in prof.read_text(encoding="utf-8") and "TODO" in prof.read_text(encoding="utf-8")
    for key in CFG.external["keys"]:
        rel = CFG.paths[key]
        if key != "profiles" and "." not in rel.split("/")[-1]:
            assert (target / rel).is_dir(), key
    for spec in CFG.project["partitions"].values():
        assert (target / spec["path"].split("{MOD}")[0].rstrip("/")).is_dir()
    assert (target / ".git").is_dir() and (target / "CODEOWNERS").exists() and (target / ".gitignore").exists()
    assert CFG.paths["module"]["state_dir"] in (target / ".gitignore").read_text(encoding="utf-8")
    out = capsys.readouterr().out
    assert CFG.project["checkout_env"] in out and "lint --profile shop" in out

    # drive it: the variable is the switch; an unfilled scaffold does not pass lint
    monkeypatch.setenv(CFG.project["checkout_env"], str(target))
    cfg = CFG.reload()
    assert cfg.profile_id == "shop" and cfg.project_checkout() == target.resolve()
    import lint
    fs = lint.validate_profile(cfg, cfg.load_profile("shop"))
    assert any(f.severity in ("CRITICAL", "MAJOR") for f in fs)


def test_new_project_refuses_an_existing_project_or_a_full_directory(factory_root, tmp_path):
    assert gov.cmd_new_project(CFG.project_checkout(), "again", None, None) == BLOCKED
    full = tmp_path / "full"
    full.mkdir()
    (full / "something.txt").write_text("x", encoding="utf-8")
    assert gov.cmd_new_project(full, "x", None, None) == BLOCKED
    assert gov.cmd_new_project(full, "x", None, None, yes=True) == OK


def test_new_domain_adds_a_profile_to_the_current_project(factory_root, capsys):
    before = (CFG.project_file()).read_text(encoding="utf-8")
    assert gov.cmd_new_domain("notes") == OK
    assert (CFG.profiles_dir() / "notes.yaml").exists()
    assert CFG.project_file().read_text(encoding="utf-8") == before, "the factory never writes project.yaml"
    assert "profile: notes" in capsys.readouterr().out
    assert gov.cmd_new_domain("notes") == BLOCKED       # exists


def test_the_same_tool_drives_two_projects_with_one_render(factory_root, tmp_path, monkeypatch):
    """Tool-rendered output is project-neutral: rendered under the fixture
    project and under a scaffolded toy project, every file in the tool tree is
    byte-identical; only the project's own overview differs."""
    import shutil
    import render
    from conftest import REAL_ROOT
    for d in ("shared", "engines", "standalone", "reviewers"):
        shutil.copytree(REAL_ROOT / d, factory_root / d)
    shutil.copytree(REAL_ROOT / "governance-tools" / "templates", factory_root / "governance-tools" / "templates")

    def tool_render():
        cfg = CFG.reload()
        files = render.generated_files(cfg)
        tool = {p: c for p, c in files.items() if p.is_relative_to(cfg.root)}
        overview = files[cfg.dir("overview")]
        return tool, overview

    first, first_overview = tool_render()
    toy_dir = tmp_path / "toy-governance"
    assert gov.cmd_new_project(toy_dir, "toy", "Clinic Suite", None) == OK
    (toy_dir / CFG.paths["profiles"] / "toy.yaml").write_text(yaml.safe_dump(TOY, sort_keys=False), encoding="utf-8")
    monkeypatch.setenv(CFG.project["checkout_env"], str(toy_dir))
    second, second_overview = tool_render()
    assert first == second, [str(p) for p in first if first[p] != second.get(p)]
    assert first_overview != second_overview
    assert TOY["identity"]["display"] in second_overview and TOY["identity"]["display"] not in first_overview
    assert not any(TOY["identity"]["id"] in c.split("`") for c in second.values())


def test_sanitize_mod_derives_a_valid_module_code():
    assert gov._sanitize_mod("acme-shop") == "ACMESHOP"
    assert gov._sanitize_mod("notes") == "NOTES"
    assert gov._sanitize_mod("123x") == "M123X"
