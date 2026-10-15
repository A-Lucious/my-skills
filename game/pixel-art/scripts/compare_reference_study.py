#!/usr/bin/env python3
"""Read-only subject comparisons between real MCP PNGs and the user screenshot.

Reports native-grid transcription fidelity separately from raw screenshot error.
Neither score proves original-art generalization. No image is written or changed.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

from reference_study import ROOT, ART, measured_asset, load_manifest, sample_cells


def compare_asset(reference, asset, path, grid=(180, 320)):
    sx, sy = reference.shape[1]/grid[0], reference.shape[0]/grid[1]
    phase = asset.get('pixel_phase_screenshot', [0, 0])
    cells, spreads, target_mask = measured_asset(reference, asset, sx, sy)
    evaluation_mask = target_mask.copy()
    if asset.get('flat_frame') or asset['id'] == 'nameplate':
        # Evaluate the paper frame perimeter. Serif name text is separate content.
        evaluation_mask[1:-1, 1:-1] = False
        raw_cells, _ = sample_cells(reference, asset['rect'], sx, sy, phase)
        frame = asset.get('flat_frame', {'color': [235, 232, 224]})
        visible_paper = np.max(np.abs(raw_cells.astype(int)-frame['color']), axis=2) <= frame.get('paper_tolerance', 16)
        evaluation_mask &= visible_paper
    with Image.open(path) as file:
        rgba = np.asarray(file.convert('RGBA'))
    h, w = cells.shape[:2]
    # Normalize only comparison coordinates; never resize/save a bitmap.
    iy = np.minimum(((np.arange(h) + .5) * rgba.shape[0]/h).astype(int), rgba.shape[0]-1)
    ix = np.minimum(((np.arange(w) + .5) * rgba.shape[1]/w).astype(int), rgba.shape[1]-1)
    actual = rgba[iy[:, None], ix[None, :]]
    actual_mask = actual[:, :, 3] > 127
    union, intersection = actual_mask | target_mask, actual_mask & target_mask
    iou = float(intersection.sum() / max(1, union.sum()))
    errors = np.max(np.abs(actual[:, :, :3].astype(int) - cells.astype(int)), axis=2)
    selected = evaluation_mask & target_mask
    strict_match = ((errors <= 3) & actual_mask)[selected]
    strict = float(strict_match.mean()) if selected.any() else 0
    mean_rgb_error = float(np.abs(actual[:, :, :3].astype(int) - cells.astype(int))[selected].mean())
    # Compare internal edge color changes, excluding exterior background pairs.
    edge_pass, edge_count = 0, 0
    for axis in [0, 1]:
        ref_edges = np.diff(cells.astype(int), axis=axis)
        candidate_edges = np.diff(actual[:, :, :3].astype(int), axis=axis)
        pair_mask = (selected[:-1, :] & selected[1:, :]) if axis == 0 else (selected[:, :-1] & selected[:, 1:])
        e = np.max(np.abs(ref_edges - candidate_edges), axis=2)
        edge_pass += int(((e <= 6) & pair_mask).sum())
        edge_count += int(pair_mask.sum())
    edge_score = edge_pass / max(1, edge_count)
    # Raw screenshot comparison keeps compression/interpolation error visible.
    x, y, ww, hh = asset['rect']
    xs = np.arange(max(0, int(round(x*sx+phase[0]))), min(reference.shape[1], int(round((x+ww)*sx+phase[0]))))
    ys = np.arange(max(0, int(round(y*sy+phase[1]))), min(reference.shape[0], int(round((y+hh)*sy+phase[1]))))
    # Match cell boundary rounding used by the phase study. Analysis only.
    xb = np.rint((x+np.arange(ww+1))*sx+phase[0]).astype(int)
    yb = np.rint((y+np.arange(hh+1))*sy+phase[1]).astype(int)
    cx = np.clip(np.searchsorted(xb, xs, side='right')-1, 0, ww-1)
    cy = np.clip(np.searchsorted(yb, ys, side='right')-1, 0, hh-1)
    raw_mask = selected[cy[:, None], cx[None, :]]
    raw = reference[ys[:, None], xs[None, :]]
    rebuilt = actual[cy[:, None], cx[None, :], :3]
    raw_errors = np.abs(rebuilt.astype(int)-raw.astype(int))
    raw_mae = float(raw_errors[raw_mask].mean()) if raw_mask.any() else None
    raw_strict = float((np.max(raw_errors, axis=2)[raw_mask] <= 3).mean()) if raw_mask.any() else None
    return {
        'id': asset['id'], 'file': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name,
        'native_size': [w, h], 'actual_png_size': [rgba.shape[1], rgba.shape[0]],
        'pixel_phase_screenshot': phase,
        'subject_cells': int(selected.sum()),
        'native_silhouette_iou_pct': round(iou*100, 4),
        'native_subject_rgb_within_3_pct': round(strict*100, 4),
        'native_internal_edge_within_6_pct': round(edge_score*100, 4),
        'native_subject_rgb_mean_absolute_error': round(mean_rgb_error, 4),
        'raw_screenshot_subject_rgb_mean_absolute_error': round(raw_mae, 4) if raw_mae is not None else None,
        'raw_screenshot_subject_rgb_within_3_pct': round(raw_strict*100, 4) if raw_strict is not None else None,
        'reference_cell_spread_mean': round(float(spreads[selected].mean()), 4),
        'native_99_gate': iou >= .99 and strict >= .99 and edge_score >= .99,
        'interpretation': 'Measured native-grid study fidelity; raw screenshot compression differs; not proof of general style mastery.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iteration', required=True)
    parser.add_argument('--candidate-dir', type=Path, help='Compare an explicit directory of candidate PNGs instead of the iteration output.')
    parser.add_argument('--manifest', type=Path, help='Defaults to the immutable iteration manifest, then current inventory.')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.iteration):
        parser.error('iteration must contain letters, digits or hyphens')
    manifest_path = args.manifest or ART/'reports'/f'reference-{args.iteration}-manifest.json'
    manifest = load_manifest(manifest_path)
    with Image.open(ROOT/manifest['reference']) as file:
        reference = np.asarray(file.convert('RGB'))
    results, missing = [], []
    for asset in manifest['assets']:
        directory = args.candidate_dir.resolve() if args.candidate_dir else ART/'exports/reference-study'/args.iteration
        path = directory/(asset['id']+'.png')
        if not path.exists():
            missing.append(asset['id'])
            continue
        results.append(compare_asset(reference, asset, path,
            (manifest['grid_estimate']['width'], manifest['grid_estimate']['height'])))
    report = {'iteration': args.iteration,
              'reference_sha256': manifest['reference_sha256'], 'scope': 'subjects, not whole-image backgrounds',
              'complete_inventory': len(manifest['assets']), 'evaluated': len(results), 'missing': missing,
              'native_99_all': not missing and len(results)==len(manifest['assets']) and all(r['native_99_gate'] for r in results),
              'results': results}
    output = ART/'reports'/('reference-' + args.iteration + '-comparison.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    for r in results:
        print(r['id'], 'IoU', r['native_silhouette_iou_pct'], 'RGB≤3', r['native_subject_rgb_within_3_pct'],
              'edges', r['native_internal_edge_within_6_pct'], 'raw MAE', r['raw_screenshot_subject_rgb_mean_absolute_error'],
              'native99', r['native_99_gate'])
    print('Native grid threshold passed for complete inventory:', report['native_99_all'], 'missing:', missing)


if __name__ == '__main__':
    main()
