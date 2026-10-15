#!/usr/bin/env python3
"""Read-only connection check through the configured Blender MCP stdio server."""
import asyncio
import json
import os
from pathlib import Path
import sys
import tomllib

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from project_paths import ROOT as PROJECT


def server_config():
    config_home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    config = {}
    for path in (config_home / 'config.toml', PROJECT / '.codex/config.toml'):
        if path.exists():
            config.update(tomllib.loads(path.read_text()).get('mcp_servers', {}).get('blender', {}))
    if config.get('enabled') is False or not config.get('command'):
        raise RuntimeError('No enabled blender stdio MCP configuration was found.')
    return config


def payload(reply):
    value = getattr(reply, 'structured_content', None)
    if value is None:
        value = getattr(reply, 'structuredContent', None)
    if value is None:
        for item in reply.content:
            if getattr(item, 'type', None) == 'text':
                try:
                    value = json.loads(item.text)
                    break
                except json.JSONDecodeError:
                    continue
    if getattr(reply, 'is_error', False) or getattr(reply, 'isError', False) or not isinstance(value, dict):
        raise RuntimeError('Blender MCP returned an error: ' + str(reply.content))
    if value.get('status') == 'error':
        raise RuntimeError(value.get('message', 'Blender execution failed.'))
    inner = value.get('result', value)
    if isinstance(inner, dict) and inner.get('status') == 'error':
        raise RuntimeError(inner.get('message', 'Blender execution failed.'))
    return inner


async def check():
    config = server_config()
    params = StdioServerParameters(
        command=config['command'], args=config.get('args', []),
        env={**os.environ, **config.get('env', {})},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            required = {'get_blendfile_summary_datablocks', 'execute_blender_code'}
            if not required <= names:
                raise RuntimeError('Missing Blender MCP tools: ' + ', '.join(sorted(required - names)))
            summary = payload(await session.call_tool('get_blendfile_summary_datablocks', {}))
            state = payload(await session.call_tool('execute_blender_code', {'code': (
                'import bpy\n'
                'result = {"version": bpy.app.version_string, "scene": bpy.context.scene.name, '
                '"file": bpy.data.filepath, "background": bpy.app.background, '
                '"cycles_built": bpy.app.build_options.cycles, '
                '"cycles_enabled": "cycles" in bpy.context.preferences.addons}\n'
            )}))
            return {'ok': True, 'tool_count': len(names), 'blender': state, 'scene_summary': summary}


def explain_error(exc):
    if isinstance(exc, BaseExceptionGroup):
        return '; '.join(explain_error(child) for child in exc.exceptions)
    return f'{type(exc).__name__}: {exc}'


def main():
    try:
        result = asyncio.run(asyncio.wait_for(check(), timeout=30))
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': explain_error(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
