#!/usr/bin/env python3
"""Agent Pure-Draw Baseline: reproduce a supplied 2D image by drawing it in Aseprite.

Two subcommands, mirroring the split used by the other scripts in this skill:

  analyze  Read the reference image, quantize it to a working palette, split that
           palette into luminance bands, and emit
             Test Workspace/<task>/reports/pure-draw.job.json
             Test Workspace/<task>/reports/pure-draw-manifest.json
           A job is a plain list of real Aseprite MCP calls; run it with
             python3 .agents/skills/pixel-art/scripts/mcp_client.py run \\
               "Test Workspace/<task>/reports/pure-draw.job.json" \\
               --log-name <task>-pure-draw.mcp-log.json

  verify   Compare the exported PNG against the reference and write
           Test Workspace/<task>/reports/pure-draw-metrics.json.
           Exit code 1 when a gate fails.

Neither subcommand writes pixels or processes images for output: analyze only
derives draw call arguments, verify only measures. All drawing happens inside
Aseprite through the MCP server.

Method and rationale: cards/features/pure_draw.md.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

from project_paths import ROOT

CHARSET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
           "abcdefghijklmnopqrstuvwxyz"
           "0123456789"
           "!@#$%^&*()-_=+[]{};:,<>/?|~")
WORKSPACE = ROOT / "Test Workspace"


def rel_to_workspace(path):
    try:
        return path.resolve().relative_to(WORKSPACE.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def resolve_input(value):
    """Accept absolute, project-relative, or Test-Workspace-relative paths."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    if value.split("/")[0] == "Test Workspace":
        return ROOT / path
    candidate = WORKSPACE / path
    if candidate.exists():
        return candidate
    return ROOT / path


def luminance(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


# ---------------------------------------------------------------- metrics
def box_mean(arr, win):
    pad = win // 2
    padded = np.pad(arr, ((pad, win - 1 - pad), (pad, win - 1 - pad)), mode="edge")
    cs = np.pad(np.cumsum(np.cumsum(padded, axis=0), axis=1), ((1, 0), (1, 0)))
    total = (cs[win:, win:] - cs[:-win, win:] - cs[win:, :-win] + cs[:-win, :-win])
    return total / (win * win)


def ssim_gray(a, b, win=7):
    """Mean SSIM on luminance, uniform window. numpy only, no scipy needed."""
    la, lb = luminance(a), luminance(b)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu_a, mu_b = box_mean(la, win), box_mean(lb, win)
    var_a = box_mean(la * la, win) - mu_a ** 2
    var_b = box_mean(lb * lb, win) - mu_b ** 2
    cov = box_mean(la * lb, win) - mu_a * mu_b
    ssim = ((2 * mu_a * mu_b + c1) * (2 * cov + c2)) / \
           ((mu_a ** 2 + mu_b ** 2 + c1) * (var_a + var_b + c2))
    return float(ssim.mean())


def metrics(reference, result):
    if reference.shape != result.shape:
        raise SystemExit(
            f"Size mismatch: reference {reference.shape[1::-1]} vs result "
            f"{result.shape[1::-1]}. The pure-draw baseline redraws at the "
            f"reference's own pixel size; resize the source, not the result.")
    diff = np.abs(reference - result)
    worst = diff.max(axis=2)
    mse = float((diff ** 2).mean())
    return {
        "size": [int(reference.shape[1]), int(reference.shape[0])],
        "ssim": round(ssim_gray(reference, result), 6),
        "psnr_db": round(float(10 * np.log10(255 ** 2 / mse)), 3) if mse > 0 else 99.0,
        "mae_per_channel": round(float(diff.mean()), 4),
        "max_channel_diff": int(worst.max()),
        "identical_pixel_pct": round(100 * float((worst == 0).mean()), 3),
        "within_2_pct": round(100 * float((worst <= 2).mean()), 3),
        "within_4_pct": round(100 * float((worst <= 4).mean()), 3),
        "within_8_pct": round(100 * float((worst <= 8).mean()), 3),
    }


# ---------------------------------------------------------------- palettes
def quantize(img, colors, mode):
    """Return (palette list of [r,g,b], index map h x w)."""
    colors = max(2, min(colors, 256))  # Aseprite's indexed palette ceiling
    px = np.asarray(img, dtype=np.uint8).reshape(-1, 3)
    if mode == "mediancut":
        q = img.quantize(colors=colors, method=Image.MEDIANCUT)
        flat = q.getpalette()
        palette = [list(flat[i * 3:i * 3 + 3]) for i in range(colors)]
        index = np.asarray(q, dtype=np.int32)
        return palette, index.reshape(img.height, img.width)
    if mode == "frequency":
        counts = Counter(map(tuple, px.tolist()))
        palette = [list(c) for c, _ in counts.most_common(colors)]
    else:
        raise SystemExit(f"Unknown palette mode: {mode}")
    pal = np.array(palette, dtype=np.int32)
    index = np.empty(len(px), dtype=np.int32)
    for start in range(0, len(px), 2000):
        segment = px[start:start + 2000].astype(np.int32)
        dist = ((segment[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
        index[start:start + 2000] = dist.argmin(axis=1)
    return palette, index.reshape(img.height, img.width)


def dominant(colors, weights):
    order = sorted(range(len(colors)), key=lambda i: -weights[i])
    return order[0]


def split_bands(palette, bands):
    order = sorted(range(len(palette)), key=lambda i: luminance(np.array(palette[i])))
    band_of = {pi: min(bands - 1, rank * bands // len(order))
               for rank, pi in enumerate(order)}
    return order, band_of


# ---------------------------------------------------------------- analyze
def analyze(args):
    reference = resolve_input(args.reference)
    if not reference.is_file():
        raise SystemExit(f"Reference not found: {args.reference}")
    # keep the task self-contained: a reference from outside Test Workspace is
    # copied in verbatim (byte-level copy only, no image processing)
    task_dir = WORKSPACE / args.task
    if WORKSPACE.resolve() not in reference.resolve().parents:
        local = task_dir / "references" / reference.name
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(reference.read_bytes())
        reference = local
    img = Image.open(reference).convert("RGB")
    width, height = img.size
    array = np.asarray(img).astype(np.float64)

    palette, index = quantize(img, args.colors, args.palette_mode)
    pal = np.array(palette, dtype=np.float64)
    snapped = pal[index]

    # dominant dark ground / dominant light body, threshold between them
    counts = np.bincount(index.ravel(), minlength=len(palette))
    ground_i = dominant(palette, counts)
    lum = luminance(pal)
    light_i = max(range(len(palette)), key=lambda i: (lum[i], counts[i]))
    threshold = (lum[ground_i] + lum[light_i]) / 2
    shape_mask = luminance(snapped) > threshold
    shape_colour = palette[light_i]

    order, band_of = split_bands(palette, args.bands)
    hexc = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette]

    report_dir = task_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    sprite = f"{args.task}/source/{args.asset_id}.aseprite"

    steps = []
    steps.append({"tool": "create_sprite", "arguments": {
        "filename": sprite, "width": width, "height": height,
        "color_mode": "rgb", "overwrite": True},
        "expect": {"ok": True}})
    steps.append({"tool": "set_palette", "arguments": {
        "filename": sprite, "colors": hexc}, "expect": {"ok": True}})
    steps.append({"tool": "rename_layer", "arguments": {
        "filename": sprite, "layer": "Layer 1", "new_name": "stroke"},
        "expect": {"ok": True}})
    steps.append({"tool": "fill_layer", "arguments": {
        "filename": sprite, "color": hexc[ground_i], "layer": "stroke"},
        "expect": {"ok": True}})
    steps.append({"tool": "render_preview", "arguments": {
        "filename": sprite, "frame": 1, "scale": args.preview_scale},
        "save_image": f"previews/{args.task}-step-01-ground.png"})

    # silhouette pass: the subject blocked in as one flat tone
    rows = ["".join("X" if shape_mask[y, x] else "." for x in range(width))
            for y in range(height)]
    steps.append({"tool": "draw_pixel_map", "arguments": {
        "filename": sprite, "rows": rows,
        "legend": {"X": f"#{shape_colour[0]:02x}{shape_colour[1]:02x}{shape_colour[2]:02x}"},
        "x": 0, "y": 0, "layer": "stroke", "frame": 1},
        "expect": {"ok": True}})
    steps.append({"tool": "render_preview", "arguments": {
        "filename": sprite, "frame": 1, "scale": args.preview_scale},
        "save_image": f"previews/{args.task}-step-02-shape.png"})

    milestones = {1: "step-03", 3: "step-04", 5: "step-05", args.bands: "step-06"}
    bands = []
    for band in range(args.bands):
        colours = sorted((pi for pi in order if band_of[pi] == band),
                         key=lambda pi: lum[pi])
        legend, char_of, rows = {}, {}, []
        for y in range(height):
            out = []
            for x in range(width):
                pi = int(index[y, x])
                if band_of[pi] == band:
                    ch = char_of.get(hexc[pi])
                    if ch is None:
                        ch = CHARSET[len(char_of)]
                        char_of[hexc[pi]] = ch
                        legend[ch] = hexc[pi]
                    out.append(ch)
                else:
                    out.append(".")
            rows.append("".join(out))
        drawn = sum(1 for row in rows for ch in row if ch != ".")
        step = {"tool": "draw_pixel_map", "arguments": {
            "filename": sprite, "rows": rows, "legend": legend,
            "x": 0, "y": 0, "layer": "stroke", "frame": 1},
            "expect": {"ok": True}}
        if (band + 1) in milestones:
            step_index = len(steps) + 1
            steps.append(step)
            steps.append({"tool": "render_preview", "arguments": {
                "filename": sprite, "frame": 1, "scale": args.preview_scale},
                "save_image": f"previews/{args.task}-{milestones[band + 1]}-band-"
                              f"{band + 1:02d}.png"})
            steps[-1]["note"] = f"milestone after band {band + 1} (step {step_index})"
        else:
            steps.append(step)
        bands.append({"band": band + 1, "colours": len(legend), "drawn_pixels": drawn,
                      "luma_range": [round(float(lum[colours[0]]), 1),
                                     round(float(lum[colours[-1]]), 1)]})

    export = f"{args.task}/exports/{args.asset_id}.png"
    steps.append({"tool": "export_png", "arguments": {
        "filename": sprite, "output": export, "scale": 1, "overwrite": True},
        "expect": {"ok": True}})

    job = {"steps": steps}
    job_path = report_dir / "pure-draw.job.json"
    job_path.write_text(json.dumps(job, ensure_ascii=False) + "\n")

    predicted = metrics(array, snapped)
    manifest = {
        "baseline": "agent-pure-draw",
        "reference": rel_to_workspace(reference),
        "reference_sha256": __import__("hashlib").sha256(reference.read_bytes()).hexdigest(),
        "size": [width, height],
        "palette_mode": args.palette_mode,
        "palette_size": len(palette),
        "bands": args.bands,
        "ground": hexc[ground_i],
        "shape_tone": f"#{shape_colour[0]:02x}{shape_colour[1]:02x}{shape_colour[2]:02x}",
        "shape_threshold_luma": round(float(threshold), 1),
        "shape_pixels": int(shape_mask.sum()),
        "sprite": sprite,
        "export": export,
        "job": rel_to_workspace(job_path),
        "steps": len(steps),
        "band_stats": bands,
        "predicted_metrics": predicted,
        "run": (f"python3 .agents/skills/pixel-art/scripts/mcp_client.py run "
                f"\"{rel_to_workspace(job_path)}\" --log-name "
                f"{args.task}-pure-draw.mcp.log.json"),
        "verify": (f"python3 .agents/skills/pixel-art/scripts/pure_draw.py verify "
                   f"--reference \"{rel_to_workspace(reference)}\" "
                   f"--result \"{export}\" --task {args.task}"),
    }
    (report_dir / "pure-draw-manifest.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")

    print(json.dumps({k: manifest[k] for k in (
        "baseline", "size", "palette_mode", "palette_size", "bands",
        "ground", "shape_tone", "shape_pixels", "steps", "job",
        "predicted_metrics", "run", "verify")}, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- verify
def verify(args):
    reference = resolve_input(args.reference)
    result = resolve_input(args.result)
    ref = np.asarray(Image.open(reference).convert("RGB")).astype(np.float64)
    got = np.asarray(Image.open(result).convert("RGB")).astype(np.float64)
    measured = metrics(ref, got)

    gates = {
        "ssim": args.ssim_min,
        "psnr_db": args.psnr_min,
        "within_4_pct": args.within4_min,
    }
    failed = {k: {"actual": measured[k], "required": v}
              for k, v in gates.items()
              if measured[k] < v}
    report = {"gates": gates, "passed": not failed, "failed": failed,
              "metrics": measured, "reference": str(reference), "result": str(result)}
    if args.task:
        out = WORKSPACE / args.task / "reports" / "pure-draw-metrics.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
        report["report"] = rel_to_workspace(out)
    print(json.dumps(report, indent=1, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)

    a = sub.add_parser("analyze", help="Emit the pure-draw MCP job and manifest.")
    a.add_argument("--reference", required=True,
                   help="Reference image, project-relative or absolute.")
    a.add_argument("--task", required=True, help="Test Workspace/<task> id.")
    a.add_argument("--asset-id", default="redraw-v01")
    a.add_argument("--colors", type=int, default=256,
                   help="Working palette size. Aseprite's indexed ceiling is 256.")
    a.add_argument("--palette-mode", choices=["mediancut", "frequency"],
                   default="mediancut")
    a.add_argument("--bands", type=int, default=8,
                   help="Luminance bands, i.e. how many draw passes.")
    a.add_argument("--preview-scale", type=int, default=2)
    a.set_defaults(func=analyze)

    v = sub.add_parser("verify", help="Measure the export against the reference.")
    v.add_argument("--reference", required=True)
    v.add_argument("--result", required=True,
                   help="Exported PNG, project-relative, workspace-relative or absolute.")
    v.add_argument("--task", help="Write pure-draw-metrics.json into this task.")
    v.add_argument("--ssim-min", type=float, default=0.995)
    v.add_argument("--psnr-min", type=float, default=40.0)
    v.add_argument("--within4-min", type=float, default=97.0)
    v.set_defaults(func=verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
