#!/usr/bin/env python3
"""Read a user reference and serialize measured tracing maps for real MCP drawing.

This is a reference-study helper, not an original-art generator. No image is saved,
resized, painted, or imported as a candidate. All candidate pixels are written by
the generated Aseprite MCP jobs, starting from blank editable sprites.
"""
import argparse
import colorsys
import hashlib
import json
import re
from collections import Counter, deque
from pathlib import Path

import numpy as np
from PIL import Image

from project_paths import ROOT, SKILL
ART = ROOT / 'Test Workspace'


def hex_color(rgb):
    return '#%02x%02x%02x' % tuple(int(v) for v in rgb)


def sample_cells(image, rect, sx, sy, phase=(0, 0)):
    x, y, w, h = rect
    cells = np.zeros((h, w, 3), dtype=np.uint8)
    spreads = np.zeros((h, w), dtype=np.float64)
    for yy in range(h):
        for xx in range(w):
            # Only observe cell interiors: display interpolation at cell boundaries
            # and JPEG noise are recorded separately, never declared native colors.
            xs, xe = int((x + xx + .32) * sx + phase[0]), int((x + xx + .68) * sx + phase[0]) + 1
            ys, ye = int((y + yy + .32) * sy + phase[1]), int((y + yy + .68) * sy + phase[1]) + 1
            xs, xe = max(0, xs), min(image.shape[1], xe)
            ys, ye = max(0, ys), min(image.shape[0], ye)
            patch = image[ys:ye, xs:xe].reshape(-1, 3)
            if not len(patch):
                raise ValueError('Reference cell falls outside screenshot')
            cells[yy, xx] = np.median(patch, axis=0).astype(np.uint8)
            spreads[yy, xx] = np.max(np.std(patch, axis=0))
    return cells, spreads


def foreground(cells, asset):
    h, w, _ = cells.shape
    policy = asset.get('mask_policy', {})
    mode = policy.get('mode')
    if mode == 'opaque' or asset['id'] == 'portrait':
        return np.ones((h, w), dtype=bool)
    if mode == 'flat-frame' or asset['id'] == 'nameplate':
        # Text is not part of this paper-frame asset. Reconstruct its background
        # silhouette from the light paper region; letters must not enter the frame.
        return np.ones((h, w), dtype=bool)
    if mode == 'saturation' or asset['id'] in ['red-arm', 'blue-boot', 'purple-brain', 'gold-profile', 'green-heart', 'blue-ring']:
        mask = np.zeros((h, w), dtype=bool)
        for y in range(h):
            for x in range(w):
                _, sat, _ = colorsys.rgb_to_hsv(*(cells[y, x] / 255.0))
                mask[y, x] = sat > policy.get('threshold', .16)
        return mask
    paper = np.array(policy.get('background', [200, 192, 174]))
    near = np.max(np.abs(cells.astype(int) - paper), axis=2) <= policy.get('threshold', 8)
    # Clear exterior paper, retaining enclosed similarly colored material cells.
    exterior = np.zeros((h, w), dtype=bool)
    queue = deque((y, x) for y in range(h) for x in range(w)
                  if (y == 0 or y == h-1 or x == 0 or x == w-1) and near[y, x])
    while queue:
        y, x = queue.popleft()
        if exterior[y, x]:
            continue
        exterior[y, x] = True
        for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and near[yy, xx] and not exterior[yy, xx]:
                queue.append((yy, xx))
    return ~exterior


def reduce_noise(cells, mask, threshold):
    # Form a measured color whitelist, merging nearby screenshot noise. This
    # operates on observation data for JSON; it never writes an image.
    counts = Counter(tuple(int(v) for v in c) for c in cells[mask])
    groups, centers = [], []
    for color, count in counts.most_common():
        c = np.array(color, dtype=float)
        if centers:
            distances = np.max(np.abs(np.asarray(centers) - c), axis=1)
            index = int(np.argmin(distances))
        else:
            index = -1
        if index >= 0 and distances[index] <= threshold:
            groups[index].append((color, count))
        else:
            centers.append(c)
            groups.append([(color, count)])
    palette = []
    for group in groups:
        total = sum(n for _, n in group)
        palette.append(np.rint(sum(np.asarray(c, dtype=float) * n for c, n in group) / total).astype(int))
    palette = np.unique(np.asarray(palette), axis=0)
    result = cells.copy()
    for y, x in np.argwhere(mask):
        distances = np.sum((palette - cells[y, x].astype(int)) ** 2, axis=1)
        result[y, x] = palette[np.argmin(distances)]
    return result


def family(rgb):
    hue, sat, val = colorsys.rgb_to_hsv(*(np.asarray(rgb) / 255.0))
    if sat < .12:
        return 'paper' if val > .75 else 'stone'
    h = hue * 360
    if h < 18 or h >= 345:
        return 'rose'
    if h < 44:
        return 'leather'
    if h < 78:
        return 'gold'
    if h < 150:
        return 'green'
    if h < 215:
        return 'teal'
    if h < 275:
        return 'blue'
    return 'magenta'


def luminance(rgb):
    r, g, b = np.asarray(rgb) / 255.0
    return .2126*r + .7152*g + .0722*b


def encode(cells, mask):
    output = cells
    visible = sorted({tuple(int(v) for v in c) for c in output[mask]})
    symbols = {c: chr(0x100 + i) for i, c in enumerate(visible)}
    legend = {s: hex_color(c) for c, s in symbols.items()}
    rows = [''.join(symbols[tuple(int(v) for v in output[y, x])] if mask[y, x] else '.'
                    for x in range(mask.shape[1])) for y in range(mask.shape[0])]
    return rows, legend


def load_manifest(manifest_path):
    manifest = json.loads(manifest_path.read_text())
    reference = ROOT / manifest['reference']
    if hashlib.sha256(reference.read_bytes()).hexdigest() != manifest['reference_sha256']:
        raise ValueError('Reference SHA-256 does not match manifest')
    gw, gh = manifest['grid_estimate']['width'], manifest['grid_estimate']['height']
    if type(gw) is not int or type(gh) is not int or min(gw, gh) < 1:
        raise ValueError('Grid dimensions must be positive integers')
    ids = set()
    for a in manifest['assets']:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', a['id']) or a['id'] in ids:
            raise ValueError('Asset IDs must be unique lowercase names')
        ids.add(a['id'])
        x, y, w, h = a['rect']
        if any(type(v) is not int for v in a['rect']) or min(x, y) < 0 or min(w, h) < 1 or x+w > gw or y+h > gh:
            raise ValueError(f"Invalid grid rectangle: {a['id']}")
    return manifest


def measured_asset(image, asset, sx, sy):
    cells, spreads = sample_cells(image, asset['rect'], sx, sy, asset.get('pixel_phase_screenshot', [0, 0]))
    mask = foreground(cells, asset)
    frame = asset.get('flat_frame')
    if frame or asset['id'] == 'nameplate':
        frame = frame or {'color': [235, 232, 224], 'transparent_cells': [[-1, 0], [-1, -1]]}
        # Observe visible paper, replacing only letters/overlaid symbols. Do not
        # overwrite reference colors then compare against our own invented fill.
        visible_paper = np.max(np.abs(cells.astype(int)-frame['color']), axis=2) <= frame.get('paper_tolerance', 16)
        # UI content may leave near-paper antialiased fringes. Only observe the
        # visible perimeter; reconstruct the intentionally blank interior.
        perimeter = np.ones(mask.shape, dtype=bool)
        perimeter[1:-1, 1:-1] = False
        visible_paper &= perimeter
        cells[~visible_paper] = frame['color']
        for x, y in frame.get('transparent_cells', []):
            mask[y, x] = False
    return cells, spreads, mask


def map_steps(filename, rows, legend, layer, x=0, y=0):
    # Respect the server's 65,536 plotted-pixel limit without editing images.
    band_height = max(1, 65536 // len(rows[0]))
    return [{'tool': 'draw_pixel_map', 'arguments': {'filename': filename, 'layer': layer,
             'frame': 1, 'x': x, 'y': y+start, 'rows': rows[start:start+band_height], 'legend': legend}}
            for start in range(0, len(rows), band_height)
            if any(c != '.' for row in rows[start:start+band_height] for c in row)]


def make_jobs(iteration, threshold, selection=None, manifest_path=None):
    if manifest_path is None:
        raise ValueError('Provide the current task reference manifest')
    manifest = load_manifest(manifest_path)
    gw, gh = manifest['grid_estimate']['width'], manifest['grid_estimate']['height']
    board_scale = manifest.get('composition_grid_multiplier', 1)
    if type(board_scale) is not int or board_scale < 1:
        raise ValueError('composition_grid_multiplier must be a positive integer')
    if selection and not selection <= {a['id'] for a in manifest['assets']}:
        raise ValueError('Selection contains an unknown asset ID')
    reports = ART / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    if any((reports / f'reference-{iteration}-{p}.job.json').exists() for p in ['structure', 'light', 'export']):
        raise ValueError('Iteration exists; choose a new ID to preserve its evidence')
    with Image.open(ROOT / manifest['reference']) as source:
        image = np.asarray(source.convert('RGB'))
    sx, sy = image.shape[1] / gw, image.shape[0] / gh
    observations, base_steps, light_steps, export_steps = [], [], [], []
    for asset in manifest['assets']:
        if selection and asset['id'] not in selection:
            continue
        cells, spreads, mask = measured_asset(image, asset, sx, sy)
        if not mask.any():
            raise ValueError(f"No foreground cells: {asset['id']}; inspect mask policy")
        final = reduce_noise(cells, mask, threshold)
        # Keep different materials and structural color clusters. A global
        # hue-to-midtone collapse erased walls, beams and facial structure in
        # the first placement study; it is unsuitable for this reference.
        rough = reduce_noise(cells, mask, max(threshold * 2, 24))
        base_rows, base_legend = encode(rough, mask)
        final_rows, final_legend = encode(final, mask)
        light_rows = [''.join(f if f != '.' and (
            b == '.' or final_legend[f] != base_legend[b]) else '.'
            for f, b in zip(fr, br)) for fr, br in zip(final_rows, base_rows)]
        filename = f"source/reference-study/{iteration}/{asset['id']}.aseprite"
        _, _, w, h = asset['rect']
        palette = sorted(set(final_legend.values()) | set(base_legend.values()))
        # RGB canvases may contain more colors than palette slots. The complete
        # measured whitelist remains in observations, never silently truncated.
        base_steps += [
            {'tool': 'create_sprite', 'arguments': {'filename': filename, 'width': w, 'height': h}},
            {'tool': 'set_palette', 'arguments': {'filename': filename, 'colors': palette[:256]}},
            {'tool': 'add_layer', 'arguments': {'filename': filename, 'name': 'measured-structure'}},
        ]
        base_steps += map_steps(filename, base_rows, base_legend, 'measured-structure')
        base_steps.append({'tool': 'remove_layer', 'arguments': {'filename': filename, 'layer': 'Layer 1'}})
        if any(c != '.' for row in light_rows for c in row):
            light_steps += [
                {'tool': 'add_layer', 'arguments': {'filename': filename, 'name': 'observed-light-and-occlusion'}},
            ]
            light_steps += map_steps(filename, light_rows, final_legend, 'observed-light-and-occlusion')
        export_steps += [
            {'tool': 'get_sprite_info', 'arguments': {'filename': filename}},
            {'tool': 'export_png', 'arguments': {'filename': filename, 'output': f"exports/reference-study/{iteration}/{asset['id']}.png", 'scale': 1}},
        ]
        observations.append({'id': asset['id'], 'class': asset['class'], 'rect': asset['rect'],
            'pixel_phase_screenshot': asset.get('pixel_phase_screenshot', [0, 0]),
            'instances': asset.get('instances', [[asset['rect'][0], asset['rect'][1]]]),
            'mask': mask.astype(int).tolist(), 'measured_cells': cells.tolist(),
            'palette': palette, 'base_rows': base_rows, 'base_legend': base_legend,
            'final_rows': final_rows, 'final_legend': final_legend,
            'light_rows': light_rows,
            'cell_spread_mean': float(spreads[mask].mean()), 'merge_threshold': threshold})
    # The board is also drawn from blank through MCP; it never imports/copies a
    # screenshot raster. It shows pixel-art assets at the measured composition.
    board = f'source/reference-study/{iteration}/artboard.aseprite'
    base_steps += [
        {'tool': 'create_sprite', 'arguments': {'filename': board, 'width': gw*board_scale, 'height': gh*board_scale}},
        {'tool': 'add_layer', 'arguments': {'filename': board, 'name': 'study'}},
        {'tool': 'draw_rectangle', 'arguments': {'filename': board, 'layer': 'study', 'frame': 1, 'x': 0, 'y': 0, 'width': gw*board_scale, 'height': gh*board_scale, 'filled': True, 'color': manifest.get('background', '#c8c0ae')}},
        {'tool': 'remove_layer', 'arguments': {'filename': board, 'layer': 'Layer 1'}},
    ]
    for obs in observations:
        x, y, _, _ = obs['rect']
        dx, dy = obs['pixel_phase_screenshot']
        for xx, yy in obs['instances']:
            px, py = round((xx+dx/sx)*board_scale), round((yy+dy/sy)*board_scale)
            for steps, phase in [(base_steps, 'base'), (light_steps, 'final')]:
                rows = [ ''.join(c*board_scale for c in row)
                         for row in obs[f'{phase}_rows'] for _ in range(board_scale)]
                steps += map_steps(board, rows, obs[f'{phase}_legend'], 'study', px, py)
    for phase, steps in [('structure', base_steps), ('light', light_steps)]:
        steps.append({'tool': 'render_preview', 'arguments': {'filename': board, 'scale': max(1, 4//board_scale), 'views': ['color', 'value', 'actual']}, 'save_image': f'previews/reference-{iteration}-{phase}.png'})
    export_steps.append({'tool': 'export_png', 'arguments': {'filename': board, 'output': f'previews/reference-{iteration}-artboard-6x.png', 'scale': max(1, 6//board_scale)}})
    for phase, steps in [('structure', base_steps), ('light', light_steps), ('export', export_steps)]:
        (ART / f'reports/reference-{iteration}-{phase}.job.json').write_text(json.dumps({'steps': steps}, ensure_ascii=False, indent=2) + '\n')
    (ART / f'reports/reference-{iteration}-observations.json').write_text(json.dumps(observations, ensure_ascii=False, indent=2) + '\n')
    (ART / f'reports/reference-{iteration}-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(iteration, 'measured tracing assets', len(observations), 'merge threshold', threshold)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iteration', required=True)
    parser.add_argument('--merge-threshold', type=int, default=12)
    parser.add_argument('--assets', help='Comma-separated subset for an intermediate study; full goal inventory stays intact.')
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.iteration):
        parser.error('iteration must contain letters, digits or hyphens')
    if not 0 <= args.merge_threshold <= 255:
        parser.error('merge threshold must be between 0 and 255')
    make_jobs(args.iteration, args.merge_threshold, set(args.assets.split(',')) if args.assets else None, args.manifest)


if __name__ == '__main__':
    main()
