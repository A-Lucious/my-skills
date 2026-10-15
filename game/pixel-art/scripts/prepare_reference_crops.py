#!/usr/bin/env python3
"""Crop task references through real Aseprite MCP; keep outputs in the workspace."""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from project_paths import ROOT, SKILL


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True,
                        help='JSON list of {source, name, x, y, width, height}; source is relative to the project.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--overwrite', action='store_true')
    opts = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', opts.task_id):
        parser.error('task-id must contain lowercase letters, digits or hyphens')
    crops = json.loads(opts.manifest.read_text())
    if not isinstance(crops, list) or not crops:
        parser.error('manifest must contain a nonempty crop list')
    names = set()
    for crop in crops:
        name = crop['name']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
            parser.error('crop names must be unique lowercase names')
        names.add(name)
        if any(type(crop[k]) is not int for k in ('x', 'y', 'width', 'height')) or min(crop['x'], crop['y']) < 0 or min(crop['width'], crop['height']) < 1:
            parser.error('crop coordinates must be nonnegative integers and dimensions positive integers')
        source = (ROOT / crop['source']).resolve()
        source.relative_to(ROOT)
        if not source.is_file():
            parser.error(f'reference does not exist: {crop["source"]}')
    relative = f'{opts.task_id}/reference-crops'
    work = ROOT / 'Test Workspace' / relative
    if not opts.overwrite and any((work / f'{name}{suffix}').exists() for name in names for suffix in ('.png', '.aseprite', '-input.png')):
        parser.error('crop output exists; choose a new task-id or use --overwrite')
    work.mkdir(parents=True, exist_ok=True)
    steps = [{'tool': 'health_check', 'arguments': {}, 'expect': {'ok': True}}]
    for crop in crops:
        name = crop['name']
        shutil.copyfile(ROOT / crop['source'], work / f'{name}-input.png')
        sprite = f'{relative}/{name}.aseprite'
        steps.extend([
            {'tool': 'import_image', 'arguments': {'input_image': f'{relative}/{name}-input.png', 'output': sprite, 'overwrite': opts.overwrite}},
            {'tool': 'crop_sprite', 'arguments': {'filename': sprite, **{k: crop[k] for k in ('x', 'y', 'width', 'height')}}},
            {'tool': 'export_png', 'arguments': {'filename': sprite, 'output': f'{relative}/{name}.png', 'scale': 1, 'overwrite': opts.overwrite}},
        ])
    job = work / 'reference-crops.job.json'
    job.write_text(json.dumps({'steps': steps}, ensure_ascii=False, indent=2) + '\n')
    subprocess.run([sys.executable, str(SKILL / 'scripts/mcp_client.py'), 'run', str(job),
                    '--log-name', f'{opts.task_id}-reference-crops.mcp-log.json'], check=True)
    print(f'Saved {len(crops)} MCP reference crops to {work}')


if __name__ == '__main__':
    main()
