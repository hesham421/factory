"""
Governance Factory CLI — gov.py
================================
One entry point over the proven per-track toolsets + the factory's own
git-native mechanics. Nothing here spells a path/repo/branch: all from config.

  gov.py structure --track backend  --module ORG [--new-version] [--dry-run]
  gov.py archive   --track backend  --module ORG --source <dir> [--dry-run] [--force]
  gov.py split     --track backend  --module ORG [--stage N|--resume|--status|--dry-run]
        → dispatch to tracks/<track>/agent1|2|3 with their real flags.

  gov.py version   --module ORG [--new]        → current/next version, creates vN folder
  gov.py tag       --module ORG --version N    → git tag [mod]-vN on the factory repo
  gov.py fetch-inputs --module ORG --version N → pull api-docs/ui-shell from the linked
                                                 repos into modules/ORG/vN/_inputs/ (pass-2 gate)
  gov.py deliver   --track backend --module ORG --version N [--push]
        → copy this track's packages + execution-state into the consumer repo's
          checkout under deliver_to, commit on branch gov/<mod>-vN-<track>, optionally push.
  gov.py status    --module ORG                → versions, tags, inputs present, delivered?
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402


def _run(cmd, cwd=None, check=True, capture=False):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check,
                          capture_output=capture, text=True)


# ── dispatch to the proven track agents ─────────────────────────────────────

def dispatch(track: str, agent: str, argv: list[str]) -> int:
    t = C.TRACKS[track]
    script = t["tools_dir"] / {"structure": "agent1_create_structure.py",
                                "archive":   "agent2_archive.py",
                                "split":     "agent3_splitter.py"}[agent]
    env = dict(os.environ, GOV_FACTORY_ROOT=str(C.FACTORY_ROOT))
    return subprocess.call([sys.executable, str(script), *argv], cwd=str(t["tools_dir"]), env=env)


# ── versioning (git-native) ─────────────────────────────────────────────────

def _sync_backend_registry(mod: str, version: int) -> None:
    """The backend track versions by its registry; the factory versions by the
    filesystem. Keep them in lockstep so agent2/agent3 (backend) archive/split
    the SAME vN the factory created. Frontend is filesystem-based already."""
    os.environ["GOV_FACTORY_ROOT"] = str(C.FACTORY_ROOT)
    sys.path.insert(0, str(C.TRACKS["backend"]["tools_dir"]))
    import importlib, config as bcfg  # noqa
    importlib.reload(bcfg)
    reg = bcfg.load_modules_registry()
    entry = reg.setdefault("modules", {}).setdefault(mod.upper(), {
        "code": mod.upper(), "description": "", "versions": [], "current_version": None})
    if version not in entry.get("versions", []):
        entry.setdefault("versions", []).append(version)
    entry["current_version"] = version
    bcfg.save_modules_registry(reg)


def cmd_version(mod: str, new: bool) -> int:
    if new:
        v = C.next_version(mod)
        root = C.version_root(mod, v)
        root.mkdir(parents=True, exist_ok=True)
        (root / ".gitkeep").touch()
        _sync_backend_registry(mod, v)
        print(f"  {mod.upper()} → v{v} created at {root.relative_to(C.FACTORY_ROOT)}  (backend registry synced)")
    else:
        print(f"  {mod.upper()} current v{C.current_version(mod)}  versions={C.module_versions(mod) or 'none'}")
    return 0


def cmd_tag(mod: str, version: int) -> int:
    tag = C.tag_name(mod, version)
    r = _run(["git", "tag", tag], cwd=C.FACTORY_ROOT, check=False, capture=True)
    if r.returncode != 0:
        print(f"  ✗ tag {tag}: {r.stderr.strip()}"); return 1
    print(f"  ✓ tagged {tag}"); return 0


# ── pass-2 inputs from the linked repos ─────────────────────────────────────

def cmd_fetch_inputs(mod: str, version: int) -> int:
    dest = C.version_root(mod, version) / C.INPUTS_FOLDER
    dest.mkdir(parents=True, exist_ok=True)
    missing = []
    for key, repo_name in C.PASS2_REQUIRED_INPUTS.items():
        repo = C.REPOS[repo_name]
        checkout = Path(repo["checkout"])
        rel = C.fmt(repo["inputs"][key], mod)
        if repo["url"] and (checkout / ".git").exists():
            _run(["git", "pull", "--ff-only"], cwd=checkout, check=False)
        src = checkout / rel
        if src.exists():
            shutil.copy2(src, dest / src.name)
            print(f"  ✓ {key:9s} ← {repo_name}:{rel}")
        else:
            missing.append(f"{key} ({repo_name}:{rel})")
            print(f"  ✗ {key:9s} missing in {repo_name} at {rel}")
    if missing:
        print("\n  PASS-2 GATE CLOSED — waiting for: " + ", ".join(missing))
        return 1
    print(f"\n  PASS-2 GATE OPEN — inputs in {dest.relative_to(C.FACTORY_ROOT)}")
    return 0


# ── delivery: packages → consumer repo branch ───────────────────────────────

def cmd_deliver(track: str, mod: str, version: int, push: bool) -> int:
    t, repo = C.TRACKS[track], C.REPOS[track]
    checkout = Path(repo["checkout"])
    if not (checkout / ".git").exists():
        print(f"  ✗ {track} checkout not a git repo: {checkout} (set REPOS[{track!r}]['checkout'])"); return 1
    src_root = C.version_root(mod, version)
    branch = C.fmt(repo["branch"], mod, version)
    dest = checkout / C.fmt(repo["deliver_to"], mod)
    if version > 1:
        dest = dest / f"v{version}"
    # what we deliver: this track's packages + execution-state if present
    items = [src_root / "packages" / p for p in t["packages"]] + [src_root / "execution-state.json"]
    present = [i for i in items if i.exists()]
    if not present:
        print(f"  ✗ nothing to deliver for {track} {mod} v{version} under {src_root}"); return 1
    _run(["git", "checkout", "-B", branch], cwd=checkout)
    for i in present:
        target = dest / "packages" / i.name if i.is_dir() else dest / i.name
        if i.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(i, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(i, target)
        print(f"  → {i.relative_to(src_root)}  ⇒  {target.relative_to(checkout)}")
    _run(["git", "add", "-A"], cwd=checkout)
    msg = f"governance: deliver {mod.upper()} v{version} {track} packages ({C.tag_name(mod, version)})"
    r = _run(["git", "commit", "-m", msg], cwd=checkout, check=False, capture=True)
    if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
        print(r.stdout + r.stderr); return 1
    print(f"  ✓ committed on {branch}")
    if push:
        if not repo["url"]:
            print("  ⚠ no url configured for this repo — not pushed"); return 0
        _run(["git", "push", "-u", "origin", branch], cwd=checkout)
        print(f"  ✓ pushed {branch}")
    return 0


def cmd_status(mod: str) -> int:
    print(f"  module   : {mod.upper()}")
    print(f"  versions : {C.module_versions(mod) or 'none'}  (current v{C.current_version(mod)})")
    r = _run(["git", "tag", "--list", C.fmt(C.TAG_PATTERN, mod, None).replace("v", "v*")],
             cwd=C.FACTORY_ROOT, check=False, capture=True)
    print(f"  tags     : {r.stdout.split() or 'none'}")
    for v in C.module_versions(mod):
        inp = C.version_root(mod, v) / C.INPUTS_FOLDER
        have = sorted(p.name for p in inp.glob("*")) if inp.exists() else []
        print(f"  v{v} inputs: {have or 'none'}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Governance factory CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("structure", "archive", "split"):
        p = sub.add_parser(name); p.add_argument("--track", required=True, choices=list(C.TRACKS))
    p = sub.add_parser("version"); p.add_argument("--module", "-m", required=True); p.add_argument("--new", action="store_true")
    p = sub.add_parser("tag"); p.add_argument("--module", "-m", required=True); p.add_argument("--version", "-v", type=int, required=True)
    p = sub.add_parser("fetch-inputs"); p.add_argument("--module", "-m", required=True); p.add_argument("--version", "-v", type=int, required=True)
    p = sub.add_parser("deliver"); p.add_argument("--track", required=True, choices=list(C.TRACKS)); p.add_argument("--module", "-m", required=True); p.add_argument("--version", "-v", type=int, required=True); p.add_argument("--push", action="store_true")
    p = sub.add_parser("status"); p.add_argument("--module", "-m", required=True)

    args, rest = ap.parse_known_args()
    if args.cmd in ("structure", "archive", "split"):
        sys.exit(dispatch(args.track, args.cmd, rest))
    if args.cmd == "version":      sys.exit(cmd_version(args.module, args.new))
    if args.cmd == "tag":          sys.exit(cmd_tag(args.module, args.version))
    if args.cmd == "fetch-inputs": sys.exit(cmd_fetch_inputs(args.module, args.version))
    if args.cmd == "deliver":      sys.exit(cmd_deliver(args.track, args.module, args.version, args.push))
    if args.cmd == "status":       sys.exit(cmd_status(args.module))


if __name__ == "__main__":
    main()
