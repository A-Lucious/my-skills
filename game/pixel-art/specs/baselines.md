# Baseline Selection

This skill has **two production baselines**. They produce different things and are not
interchangeable; pick one per task, and record which one and why in the task card.

The Blender production route has one implementation: the [structural baseline](../styles/parchment-fantasy/PIXEL-SHADER.md). The A/B labels here distinguish original production from independent 2D reference reproduction; they are not Blender algorithm variants.

**The Agent selects the baseline.** Do not default silently to the six-phase engine because it is
the longer document, and do not default silently to pure-draw because the user attached an image.
Read the request, decide, state the decision in one line, then proceed.

| | **A — Production Baseline** | **B — Agent Pure-Draw Baseline** |
|---|---|---|
| Engine | [workflow.md](../workflow.md), six phases | [cards/features/pure_draw.md](../cards/features/pure_draw.md) |
| Tools | Blender pre-light structure/Sobel → protected SOFT.04 → style palette → constrained Aseprite cleanup | Aseprite MCP only |
| Input | A described subject (text, brief, design spec) | A supplied 2D image |
| Output | New original asset: chosen native grid, transparent background, style-locked palette, optional animation | The supplied image redrawn at its own pixel size |
| Optimizes | Style consistency, form, material, editability | Fidelity to the reference, measured |
| Palette | Locked to `styles/<style-id>/palette.json`; `check_palette.py` is a gate | The reference's own quantized colors; `check_palette.py` does not apply |
| Evidence | Q1–Q5 reviews on previews | Fidelity table (`ssim`, `psnr_db`, tolerance coverage) |

> Naming note: [cards/features/flat_ui.md](../cards/features/flat_ui.md) predates this split and calls
> its own 2D-blockout approach "Track B". That is a **sub-strategy inside Baseline A**, not Baseline B.
> When the two names could be confused, spell it "Baseline B (Agent Pure-Draw)" rather than "Track B".

## How to choose

Take **B (pure-draw)** when most of these hold:

- the user supplied an image and the request is to *reproduce* it: 「画这个」「照这个画」「复刻」
  「按这张图」「similarity / 相似度」, or a screenshot of an existing UI element or artwork;
- a number or a comparison is attached to the request ("99% similar", "pixel match", "same as the
  reference");
- there is no 3D form to reconstruct — flat painted strokes, paper strips, ribbons, UI panels,
  icons, gradients, existing game art;
- the output will be compared back to that image, so a measurable fidelity target makes sense;
- the reference size is meaningful (a fixed UI slot, a texture that must line up).

Take **A (production)** when most of these hold:

- the user describes a subject rather than supplying one: "a wooden chest icon", "a swamp scene",
  "a portrait with a scar";
- the image is a *reference for style or content*, and the deliverable is a new asset in that style —
  a supplied image does not by itself mean "reproduce it";
- the output must be a clean native-grid asset: transparent, small palette, hard edges, integer
  display scaling, layered source, animation;
- the asset is going into the project's UI and must match the locked style palette;
- the user asks for interpretation, variation, a new pose/angle, or a set of assets.

Mixed and edge cases:

- **Reference supplied + a style-adjusted asset wanted.** This is A, with the reference as visual
  guidance. Say so explicitly so nobody expects a fidelity score.
- **Reference supplied + exact reproduction *and* transparent/editable output wanted.** Run B first
  at reference size, then refine in Aseprite: cut the background, snap to the style palette, re-grid
  for the display scale. Record it as B → A handoff and keep the fidelity number for the B stage
  only; the A stage changes pixels deliberately.
- **A small flat icon that must match an existing set.** If the set already exists as pixels, B on
  one member and copy its conventions is faster and more faithful than A.
- **Both are plausible and it changes the deliverable.** Ask one short question instead of guessing:
  "要原样复刻（会对参考图算相似度），还是按参考做一张风格化的新素材？"

## Never

- Never mix the two baselines' gates. `check_palette.py` failing is not a defect under B; a fidelity
  score is not required under A.
- Never paste the source image into the sprite to satisfy B — `import_image`,
  `draw_image_base64`, `stamp_file`, `import_spritesheet` are excluded. If the delivered code path
  copies the file, the result is a copy, not a drawing; say so if the user explicitly wants a copy
  instead.
- Never claim "99% similar" without naming the metric. Bit-identical and SSIM are different targets
  and only one of them is achievable by a redraw.

## Recording

Task card first line, both baselines:

```markdown
Baseline: A Production — because <reason>
Baseline: B Agent Pure-Draw — because <reason>
```

Then follow the field template for that baseline in
[Production Specification](production.md#task-card-and-continuity-template).
