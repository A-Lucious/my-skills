#!/usr/bin/env python3
"""Invoke the real Aseprite stdio MCP. This client never draws or edits images."""
import argparse
import asyncio
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from project_paths import ROOT, SKILL
VENV = ROOT / "tools/aseprite-mcp/.venv"
# Use the MCP SDK installed with the project, independent of the caller's Python.
if Path(sys.prefix).resolve() != VENV.resolve():
    python = VENV / "bin/python"
    if not python.is_file():
        raise SystemExit("Install the MCP first with scripts/install_mcp.py.")
    os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])

from jsonschema import Draft202012Validator  # noqa: E402
from mcp import ClientSession, StdioServerParameters, types  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402


def decoded(result, save_image=None):
    data = result.structured_content
    texts = []
    images = []
    for part in result.content:
        if part.type == "text":
            try:
                texts.append(json.loads(part.text))
            except ValueError:
                texts.append(part.text)
        elif part.type == "image":
            images.append(part)
    if data is None:
        data = texts[0] if len(texts) == 1 else {"content": texts}
    if images:
        data = {"result": data, "images": [{"mime_type": p.mime_type} for p in images]}
        if save_image:
            path = (ROOT / "Test Workspace" / save_image).resolve()
            path.relative_to((ROOT / "Test Workspace/previews").resolve())
            if len(images) != 1 or images[0].mime_type != "image/png":
                raise RuntimeError("--save-image supports exactly one MCP PNG preview.")
            path.parent.mkdir(parents=True, exist_ok=True)
            # Persist the bytes returned by MCP unchanged; no image processing here.
            path.write_bytes(base64.b64decode(images[0].data))
            data["saved_image"] = str(path)
    elif save_image:
        raise RuntimeError("Tool returned no image to save.")
    if result.is_error or (isinstance(data, dict) and data.get("ok") is False):
        raise RuntimeError(json.dumps(data, ensure_ascii=False))
    return data


def check_expectations(data, expectations):
    for key, expected in expectations.items():
        actual = data
        for part in key.split("."):
            actual = actual.get(part) if isinstance(actual, dict) else None
        if actual != expected:
            raise RuntimeError(f"Expected {key}={expected!r}, got {actual!r}")


async def run(opts):
    parameters = StdioServerParameters(
        command="/bin/bash", args=[str(SKILL / "scripts/start_mcp.sh")], cwd=ROOT,
        env={**os.environ, "ASEPRITE_MCP_TRANSPORT": "stdio"},
    )
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=180) as session:
            await session.initialize()
            registry = {}
            cursor = None
            while True:
                page = await session.list_tools(params=types.PaginatedRequestParams(cursor=cursor) if cursor else None)
                registry.update({tool.name: tool for tool in page.tools})
                cursor = page.next_cursor
                if not cursor:
                    break
            if opts.action == "tools":
                if opts.name:
                    if opts.name not in registry:
                        raise RuntimeError(f"Unknown MCP tool: {opts.name}")
                    print(registry[opts.name].model_dump_json(indent=2, exclude_none=True))
                else:
                    print(json.dumps({"count": len(registry), "tools": list(registry)}, indent=2))
                return
            if opts.action == "doctor":
                steps = [{"tool": "health_check", "arguments": {}, "expect": {"ok": True}}]
            elif opts.action == "call":
                arguments = json.loads(Path(opts.args_file).read_text()) if opts.args_file else json.loads(opts.arguments)
                steps = [{"tool": opts.name, "arguments": arguments, "save_image": opts.save_image}]
            else:
                job = json.loads(Path(opts.job).read_text())
                steps = job["steps"]
            if not isinstance(steps, list) or not steps:
                raise RuntimeError("Job needs a nonempty steps list.")
            # Validate all call shapes before the first mutating tool runs.
            for step in steps:
                name = step["tool"]
                if name not in registry:
                    raise RuntimeError(f"Unknown MCP tool: {name}")
                arguments = step.get("arguments", {})
                properties = registry[name].input_schema.get("properties", {})
                unknown = set(arguments) - set(properties)
                if unknown:
                    raise RuntimeError(f"Unknown arguments for {name}: {sorted(unknown)}")
                Draft202012Validator(registry[name].input_schema).validate(arguments)
                if step.get("save_image"):
                    (ROOT / "Test Workspace" / step["save_image"]).resolve().relative_to((ROOT / "Test Workspace/previews").resolve())
            log = {"started_utc": datetime.now(timezone.utc).isoformat(), "transport": "stdio", "calls": []}
            report = ROOT / "Test Workspace/reports" / (getattr(opts, "log_name", None) or "latest.mcp-log.json")
            report.resolve().relative_to((ROOT / "Test Workspace/reports").resolve())
            report.parent.mkdir(parents=True, exist_ok=True)
            try:
                for index, step in enumerate(steps, 1):
                    record = {"step": index, "tool": step["tool"], "arguments": step.get("arguments", {})}
                    log["calls"].append(record)
                    result = await session.call_tool(record["tool"], record["arguments"])
                    record["result"] = decoded(result, step.get("save_image"))
                    check_expectations(record["result"], step.get("expect", {}))
                    print(json.dumps(record, ensure_ascii=False), flush=True)
                log["ok"] = True
            except Exception as exc:
                log["ok"] = False
                log["error"] = str(exc)
                raise
            finally:
                report.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("doctor", help="Run the real MCP/Aseprite round trip.")
    tools = sub.add_parser("tools", help="List names or inspect one live input schema.")
    tools.add_argument("name", nargs="?")
    call = sub.add_parser("call", help="Call one MCP tool with JSON arguments.")
    call.add_argument("name")
    call.add_argument("arguments", nargs="?", default="{}")
    call.add_argument("--args-file")
    call.add_argument("--save-image", help="Save unchanged MCP PNG bytes as previews/<name>.png.")
    batch = sub.add_parser("run", help="Run a JSON MCP job sequentially; stop on first error.")
    batch.add_argument("job")
    batch.add_argument("--log-name", default="latest.mcp-log.json")
    opts = parser.parse_args()
    try:
        asyncio.run(run(opts))
    except (Exception, BaseExceptionGroup) as exc:
        def explain(error):
            if isinstance(error, BaseExceptionGroup):
                return "; ".join(explain(child) for child in error.exceptions)
            return f"{type(error).__name__}: {error}"
        print(f"MCP failed: {explain(exc)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
