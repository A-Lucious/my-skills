# Feature Card: Agent Pure-Draw Baseline (Aseprite only)

Mount this card instead of the six-phase engine when the task is **to redraw a supplied 2D image
faithfully** — a screenshot, a piece of existing art, a cropped UI element — rather than to design
an original asset. Selection criteria and the comparison with the Production Baseline live in
[Baseline Selection](../../specs/baselines.md).

This baseline produces the image at the **reference's own pixel size**. It does not author a new
native grid, does not interpret the subject, and does not lock to `styles/<style-id>/palette.json`.
What it optimizes is fidelity to the supplied bitmap, measured and reported (Section 6).

No 3D, no Blender, no Pixel Shader, no image-generation model. Aseprite only, and every pixel is
written by an Aseprite MCP call — `import_image`, `draw_image_base64`, `stamp_file` and
`import_spritesheet` are **not** part of this baseline; using them turns the task into a copy, not
a drawing.

---

## 1. Read the reference before choosing a palette

Measure, do not assume:

```bash
tools/aseprite-mcp/.venv/bin/python -c "..."   # or any read-only inspection
```

Record in the task card:

- exact size in pixels; **this is the working size**, do not rescale the source and do not
  "improve" it to a round grid;
- number of distinct colors. A source that came from a screenshot or a resized render will carry
  far more colors than it appears to: anti-aliased edges plus compression noise. A flat two-tone
  drawing routinely measures 500–2000 distinct RGB values;
- the dominant dark tone and the dominant light tone, and roughly where the contour sits between
  them. These become the ground fill and the silhouette tone;
- any sub-shapes that must survive (folds, dry-brush marks, a drip, a soft shadow), because they
  set the palette size needed.

If the user also wants the subject turned into a *style-locked asset* (transparent background, small
palette, animation), this is the wrong baseline — use the Production Baseline, or run this one first
to establish the silhouette and then refine. Say which you are doing.

## 2. Palette: median cut, not most-frequent

Default **256 colors** (Aseprite's indexed ceiling), **median cut**.

Median cut beats "the 256 most frequent colors" on exactly the thing that matters here. The
anti-aliased rim is a tiny fraction of pixels, so frequency-based selection spends its whole budget
on the two big flat clusters and throws the rim away; the loss then shows up as banding along the
contour, the most visible place on the image. Measured on the calibration case in Section 7:
median cut gave SSIM 0.99962, most-frequent gave 0.99913, and the worst-case channel error dropped
from 21 to 14.

Use `--palette-mode frequency` only when the source already is a small flat palette and you want to
preserve its exact colors.

## 3. Emit the draw data

```bash
python3 .agents/skills/pixel-art/scripts/pure_draw.py analyze \
  --reference "<task>/references/<source>.png" \
  --task <task-id> --asset-id <asset-id> \
  --colors 256 --bands 8
```

This is analysis and JSON only — it writes no pixels. It produces:

- `Test Workspace/<task>/reports/pure-draw.job.json` — the whole drawing as a sequential list of
  real MCP calls;
- `Test Workspace/<task>/reports/pure-draw-manifest.json` — size, palette, ground tone, silhouette
  tone, per-band color and pixel counts, predicted fidelity, and the two commands to run next.

Outputs land under `Test Workspace/<task>/` (`source/`, `exports/`, `reports/`) to keep the task
self-contained, matching the host project's per-task workspace rule. Milestone previews are the one
exception: `mcp_client.py` only allows `save_image` under `Test Workspace/previews/`, so they are
written there as `<task>-step-NN-*.png`.

The script snaps every pixel to its nearest palette entry, sorts the palette by luminance, and cuts
it into 8 bands. Every pixel belongs to exactly one band, so the bands together cover 100% of the
canvas and the last pass completes the image.

`--bands` trades step count against fidelity: 8 is the default; 4 makes a coarser progression and
6–12 is the useful range. More bands never change the final image, only how many preview milestones
you get.

## 4. Draw, in this order

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py run \
  "Test Workspace/<task>/reports/pure-draw.job.json" \
  --log-name <task>-pure-draw.mcp.log.json
```

The job executes these steps; each one is a real call and each one is worth a line in the task
record:

| Phase | Call | What it does |
|---|---|---|
| **1. Canvas** | `create_sprite` | reference size, RGB |
| **2. Palette** | `set_palette` | the quantized working palette |
| **3. Layer** | `rename_layer` | `stroke` |
| **4. Ground** | `fill_layer` | whole frame, dominant dark tone |
| **5. Silhouette** | `draw_pixel_map` | subject blocked in as one flat tone — the form appears here |
| **6. Tone bands** | `draw_pixel_map` × bands | dark → light; background structure, then the anti-aliased rim, then the body and highlights |
| **7. Export** | `export_png` | scale 1, at reference size |

Milestone `render_preview` calls are interleaved so the task shows the image growing. They save to
`Test Workspace/previews/<task>-step-NN-*.png`.

Two things to keep honest in the task record:

- the tone-band order is a painting order, so between the silhouette pass and the last band the body
  is still dark and the image reads like a line drawing. That is expected, not a defect. If the user
  needs the body to appear first, reorder bands (`body → rim → ground`) in the manifest before
  running; the final image is identical.
- the palette is the source's own quantized colors, not the style palette. Do **not** run
  `check_palette.py` on this output as a pass/fail gate; run Section 6 instead. Note the deviation
  explicitly in the task card so nobody later mistakes it for a style regression.

## 5. Inspect at native scale and at integer zoom

- 1× — the size the image is actually used at;
- 2×–6× on the parts that carry the likeness: the outermost contour, any inner shadow, the fine
  texture marks, the smallest sub-shape;
- a side-by-side of reference and result at the same display scale;
- a difference map. Amplify it (×10–×20) or it will just look black when the result is good.

If the reference and result look different at 1×, stop and fix before exporting — no metric will
save an obviously wrong silhouette.

## 6. Verify against the reference, not against taste

```bash
python3 .agents/skills/pixel-art/scripts/pure_draw.py verify \
  --reference "<task>/references/<source>.png" \
  --result "<task>/exports/<asset-id>.png" \
  --task <task-id>
```

Writes `Test Workspace/<task>/reports/pure-draw-metrics.json` and exits non-zero when a gate fails.
Default gates: **SSIM ≥ 0.995**, **PSNR ≥ 40 dB**, **≥ 97% of pixels within 4/255 per channel**.

Report the whole table, not one number:

| Field | Meaning |
|---|---|
| `ssim` | structural similarity; the headline number |
| `psnr_db` | 40 dB ≈ imperceptible, 45+ dB is very close |
| `within_8_pct` / `within_4_pct` / `within_2_pct` | fraction of pixels within that per-channel error |
| `mae_per_channel` | average absolute error |
| `max_channel_diff` | worst single channel error |
| `identical_pixel_pct` | fraction of bit-identical pixels |

**`identical_pixel_pct` is not the fidelity number.** A reference that came from a screenshot has
noise of its own, so no redraw can be bit-identical there; only copying every source pixel would be.
Say this out loud in the delivery instead of letting the user discover it: state the SSIM/PSNR
figure, state that bit-identical is a different (and mutually exclusive) goal, and offer a
full-palette restoration pass if they actually need a bit-level match.

## 7. Calibration case

A 260×75 crop of a cream painted bar on a dark ground, reproduced from scratch: 1712 distinct source
colors, median-cut 256-color palette, 8 bands, 20 MCP steps including milestone previews. The working
directory was `Test Workspace/aseprite-redraw-20261018/`; workspace content is cleaned per project, so
the numbers below are the durable record, not that path.

Measured: **SSIM 0.999615, PSNR 48.90 dB, 99.70% of pixels within 8/255, 97.83% within 4/255,
mean error 0.28/255, worst channel error 14/255, bit-identical 77.88%.**

Use those numbers as the expectation for "a faithful pure-draw reproduction of a resampled
screenshot". A materially worse result means the palette mode, the band count or the reference size
is wrong — not that the reference was hard.

## 8. Task record fields

In `Test Workspace/reports/<id>.md`, in place of the 3D/lighting/Shader fields:

```markdown
Baseline: Agent Pure-Draw — reason chosen (verbatim user requirement + reference supplied)
Reference: path, sha256, size, distinct color count, dominant dark/light tones
Dimensions: reference WxH = canvas; display scale used by the consumer
Palette: mode (mediancut/frequency), size, ground tone, silhouette tone; style-palette deviation noted
Draw steps: job path, band count, per-band colors/pixels, milestone preview paths, MCP log path
Fidelity: the Section 6 table verbatim; gate pass/fail; what was deliberately not reproduced
Checks: 1× and integer-zoom previews, side-by-side path, difference map path
User review: pending / approved, with the quoted confirmation
```
