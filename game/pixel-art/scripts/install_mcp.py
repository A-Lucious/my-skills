#!/usr/bin/env python3
"""Restore the pinned MCP checkout and write only this project's Codex entry."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from project_paths import ROOT, SKILL


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configure-only", action="store_true")
    opts = parser.parse_args()
    spec = json.loads((SKILL / "mcp/aseprite-mcp.lock.json").read_text())
    repo = ROOT / spec["directory"]
    if not opts.configure_only:
        if not shutil.which("git") or not shutil.which("uv"):
            raise RuntimeError("Install git and uv first.")
        if not repo.exists():
            repo.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "clone", spec["repository"], str(repo)], check=True)
            subprocess.run(["git", "checkout", "--detach", spec["commit"]], cwd=repo, check=True)
        if not (repo / ".git").exists():
            raise RuntimeError(f"Refusing to replace existing non-Git directory: {repo}")
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        if revision != spec["commit"]:
            raise RuntimeError(f"Checkout is {revision}, expected {spec['commit']}; left untouched.")
        subprocess.run(spec["dependency_install"], cwd=repo, check=True)
    if not (repo / ".venv/bin/python").is_file():
        raise RuntimeError("MCP environment missing; run installation without --configure-only.")
    config = ROOT / ".codex/config.toml"
    existing = config.read_text() if config.exists() else ""
    begin = "# BEGIN pixel-art (managed project-local MCP)"
    end = "# END pixel-art"
    launcher = SKILL / "scripts/start_mcp.sh"
    block = "\n".join([
        begin,
        "[mcp_servers.aseprite]",
        'command = "/bin/bash"',
        f"args = [{json.dumps(str(launcher), ensure_ascii=False)}]",
        f"cwd = {json.dumps(str(ROOT), ensure_ascii=False)}",
        "startup_timeout_sec = 30",
        "tool_timeout_sec = 180",
        "enabled = true",
        "[mcp_servers.aseprite.env]",
        f"PIXEL_PROJECT_ROOT = {json.dumps(str(ROOT), ensure_ascii=False)}",
        end,
    ])
    # Migrate the prior skill name without adding a second MCP registration.
    markers = [
        (begin, end),
        ("# BEGIN pixel-art-aseprite (managed project-local MCP)",
         "# END pixel-art-aseprite"),
    ]
    found = [(start, stop) for start, stop in markers if start in existing]
    if len(found) > 1:
        raise RuntimeError("Multiple managed aseprite blocks found; left untouched.")
    if found:
        start, stop = found[0]
        before, remainder = existing.split(start, 1)
        if stop not in remainder:
            raise RuntimeError("Managed config block has no end marker; left untouched.")
        _, after = remainder.split(stop, 1)
        updated = before + block + after
    else:
        if "[mcp_servers.aseprite]" in existing:
            raise RuntimeError("An unmanaged aseprite entry already exists; left untouched.")
        updated = existing.rstrip() + ("\n\n" if existing.strip() else "") + block + "\n"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(updated)
    for folder in ("source", "exports", "previews", "reports"):
        (ROOT / "Test Workspace" / folder).mkdir(parents=True, exist_ok=True)
    print(f"Configured {config}; workspace: {ROOT / 'Test Workspace'}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
