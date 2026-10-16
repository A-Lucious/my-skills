# Reference Study and Calibration Specification

Applies to user-requested replications, tracing studies, or style calibrations. Studies document provenance, using independent observation whitelists and per-asset comparisons; original color schemes use the production palette.

Studies and calibrations follow the [Pipeline](../../workflow.md); execution covers all six phases, running the fixed style Shader in Step 3 with advance previews, unless prompts explicitly waive designated phases. The observations, transcriptions, and comparisons below are specialized operations within the pipeline and do not substitute for Blender modeling, lighting guidance, or advance Shader previews.

## Provenance and Scope

The public skill does not distribute third-party game screenshots or tracing outputs. When research is required, use permissible references provided for the active task, storing original files and frozen manifests in `Test Workspace/<task-id>/`, recording source, permitted scope, and SHA-256. Studies and original cases are labeled separately; private references must not enter public repositories.

Text and personal information are not public visual assets; inspect observation targets such as paper frames and decorations separately from overlaid text, accounts, and timestamps. New references establish their own asset lists and grid estimates, with repeated instances counted against template assets.

## Observation Grids and Colors

- Estimate per-asset grid dimensions, clusters, boundaries, and origin. Display scaling and localized half-cell offsets are recorded per source without assuming grid parameters from other screenshots.
- Use median cell-center colors to observe palette values, recording compression and interpolation edges separately. Color merging preserves materials and structures, avoiding global hue merges that obliterate beams, walls, or facial features.
- Paper frames separate paper texture from overlaid text/icons, reconstructing interiors as blank and restricting color comparisons to visible outer borders. Margin indents, corner steps, and border thicknesses are observed per reference.
- Default candidates are refined from Blender pixel bases imported via Aseprite MCP; imported/cropped files from user reference images serve observation only and must not act directly as candidates. Blank-canvas cell-by-cell transcription is used only when explicitly requested by users with verbatim prompt quotes; this does not automatically waive modeling or lighting. Retain active editing layers and before/after previews, freezing observation whitelists per iteration.

## Manifest

[reference_study.py](../../scripts/reference_study.py) is a helper tool for historical blank-canvas transcription, executed only upon explicit user request; Step 4 imports Blender pixel bases by default per workflow. Comparison tools and observation manifests remain active; invocation instructions are detailed in [Aseprite MCP](../../mcp/aseprite.md). Original image paths are relative to the project root; MCP paths are relative to `Test Workspace/`.

```json
{
  "reference": "Test Workspace/studies/<task>/reference.png",
  "reference_sha256": "<actual-sha256>",
  "grid_estimate": {"width": 180, "height": 320},
  "composition_grid_multiplier": 2,
  "background": "#c8c0ae",
  "assets": [{
    "id": "example-prop", "class": "prop", "rect": [7,296,22,23],
    "pixel_phase_screenshot": [0,0],
    "mask_policy": {"mode":"exterior-background", "background":[200,192,174], "threshold":8}
  }]
}
```

`rect` represents observation grid `[x, y, w, h]`; `pixel_phase_screenshot` represents pixel offset in the original screenshot. `instances:[[x, y], ...]` indicates repeated templates. Mask policies support `opaque`, `saturation` (threshold 0–1), and `exterior-background` (RGB channel delta); flat-frame configs include `color`, `paper_tolerance`, `transparent_cells`, with negative indices marking declared corner indents. Verify mask results visually against adjacent colors, backgrounds, and compression fringes.

Strict transcription may start with `merge-threshold=1`, adjusting for source error margins. Scopes, thresholds, masks, and grid estimates are research parameters logged with the source; 2x composite grids and crops represent analytical representations, not official source dimensions.

## Comparison Metrics

Compare actual MCP PNG outputs against unedited sources and the iteration's frozen manifest. Optional observation grid thresholds for strict transcription: subject silhouette IoU, proportion of subject pixels with RGB channel delta <= 3, and proportion of adjacent internal cell variation delta <= 6, all >= 99% per asset. Backgrounds are excluded from full-image weighting; paper faces exclude text and icons, cross-checking indented outlines visually against references.

Additionally report RGB MAE and strict color ratios against original screenshots, explaining grid estimation, mask, scaling, and compression errors. Passing observation grid checks confirms transcription accuracy for that manifest only; pixel-level similarity to source screenshots and original creative capability are evaluated separately. Minor screenshot compression artifacts may trigger high-color or stray-pixel warnings, which should be explained as study error margins.
