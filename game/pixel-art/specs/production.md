# Delivery, Inspection, and Review

## Files and Editability

Asset IDs use lowercase English with hyphens; versions use `vNN`. Retain confirmed versions during production, conducting modifications in working copies; modify a single source sequentially. After delivery, purge obsolete iterations, one-off jobs, temporary logs, and backups, retaining final assets, editable sources, and essential previews.

| Location (Relative to Project Root) | Contents |
|---|---|
| `Test Workspace/3d/<id>/<version>/` | `.blend`, raw guidance, and data manifests |
| `Test Workspace/3d/<id>/<version>/pixel-base-vNN.png` | Native Blender pixel base for Aseprite import and comparison |
| `Test Workspace/<task-id>/shader-manifest.json` | Step 3 style Shader path, version/hash, inputs, and preview review status |
| `Test Workspace/source/<id>-vNN.aseprite` | Editable pixel source files |
| `Test Workspace/exports/` | Native PNGs, sprite sheets, and JSON |
| `Test Workspace/previews/` | Phase, comparison, and playback previews |
| `Test Workspace/reports/` | Task cards, jobs, logs, checks, and user conclusions |

Organize layers purposefully per object, preserving layered sources. Scenes may use `sky/far/mid/ground/subject/fx`; characters may use `shadow/body/gear/fx`. Layer blend modes and opacity follow current style definitions.

## Outputs and Technical Checks

| Task | Deliverables |
|---|---|
| Static | `.aseprite` + scale=1 PNG; transparent or scene background as designed |
| Animated | `.aseprite` + scale=1 spritesheet PNG + Aseprite JSON; accompanying preview GIF |

Previews use 4x or 6x integer scaling. Fixed-grid characters can use horizontal/rows with padding=0; compact sprite sheets can use packed with padding=1, parsed via JSON frame rectangles.

- Source files: `get_sprite_info` verifies canvas, layers, frames, durations, and tags; `assess_sprite` inspects palette coverage and localized suggestions.
- PNGs: Inspect dimensions, cropping, stray pixels, and transparent zones. Run [check_palette.py](../scripts/check_palette.py) on original outputs to verify ramps, family budgets, and alpha against [COMMON](../styles/COMMON.md); fix issues and re-export before re-checking.
- Animations: Record orientation, action tags, frame ranges, durations, and foot/prop anchors. Inspect first/mid/last frames and GIFs; use `validate_loop` to check loops, duplicated frames, and holds; use `diff_sprites` to verify frame deltas; check JSON rectangle bounds, durations, and tag ranges. Express loop holds through duration values.
- Tracing studies: Follow [Study Specification](../styles/parchment-fantasy/REFERENCE-STUDY.md) for provenance, observation whitelists, and per-asset comparisons.

Run palette checks from the project root, passing the asset purpose, selected families, and all production PNGs from the task card. Taxonomy selects design specs; `--asset-type` uses purpose codes defined in the current palette: Parchment Fantasy uses `portrait` for portraits, `battle_character`/`large_creature` for characters, `prop`/`prop_icon` for items, `symbol`/`status`/`icon` for symbols, `scene`/`cover` for scenes and buildings, and `prop_icon` for small architectural icons.

```bash
tools/aseprite-mcp/.venv/bin/python .agents/skills/pixel-art/scripts/check_palette.py \
  --style parchment-fantasy --asset-type portrait --families skin,earth,green \
  "Test Workspace/exports/portrait-v01.png"
```

Passing `--style` alone verifies palette schema definitions; omitting `--families` triggers minimal coverage inference for diagnostics; production checks require declared family lists.

## Reviews and Status

Q1 evaluates 3D form, Q2 evaluates lighting guidance, Q3 evaluates Step 3 style Pixel Shader output, Q4 evaluates Step 4 rough drafts, and Q5 evaluates Step 6 final visual results; Step 5 internal detail checks do not constitute Q5. Phases are confirmed by the user sequentially by default; when user prompts explicitly authorize omitting a phase, log the authorization and omitted status. When users request consolidated checks or single-trial runs, execute all non-waived production phases and agent self-checks, reviewing per user instructions; Shader previews must still be shown before Step 4 production.

Maintain separate records for: phase execution status and artifacts, technical checks and results, agent visual self-checks (Unchecked / Passed / Rework Required), and user reviews (Pending Review / Approved / Rework). Passing technical checks indicates only that technical criteria were met; visual self-checks cannot replace user sign-off. User "Approved" status requires verbatim quotes of explicit confirmation linked to specific preview versions, remaining pending review otherwise. Revisions re-open affected checks only.

Candidates may be exported for review; candidate delivery does not equal user acceptance or formal archiving. Unresolved issues must be listed alongside candidates without declaring "All checks passed" or "Requirements fully met." Retain guidance and comparison evidence supporting current decisions prior to review; if users explicitly request early cleanup, record the scope of cleaned evidence. After review, purge intermediate process files per file specs, retaining final sources, essential previews, and summary conclusions.

## Task Card and Continuity Template

Maintain a record in `Test Workspace/reports/<id>.md`, populating conditional fields per task. Workflow, 3D, lighting, and phase artifact records cannot be omitted due to asset category; when a phase is explicitly waived by the user, cite verbatim prompts and define the scope, avoiding `N/A` or "flat symbol":

```markdown
# <asset-id>
Requirements: Original / Study; taxonomy and purpose; style-id; delivery goals; allowable simplifications
Workflow: Execution / reuse / omission status and evidence paths across 6 phases; omitted phases and verbatim user prompts ("No phase omission authorized" if not waived)
Dimensions: Native WxH; display container and scaling ratio; margins, framing, and anchors
Reference: Source, full/crop paths; observed structural and material features
Palette: Version, purpose cap, selected families, material -> family mappings; observation whitelist for studies
Lighting: Key / ambient / secondary lights; primary occluders -> shadow receivers; render preview and raw guidance paths; or verbatim prompt waiving lighting
3D: Version, .blend path, engine, camera/grid, part/material IDs; pass definitions and consumed fields; or verbatim prompt waiving 3D
Structural Baseline: Major proportions, part anchors, joint axes or design offsets, apertures, and landmarks; target grid and version
Pixel: Source version, layers/frames; current defects, open zones, and protected zones
Pixel Base: Blender PNG path and actual WxH; shader/node setup, engine, and color management; Aseprite import source and draft layer; or verbatim prompt requesting alternative blockout
Shader: style-id, styles/<style-id>/pixel_shader.py, script version/hash, palette version/hash; input dimensions / families / purpose, camera, and render params; native / integer zoom / before-after preview paths; Q3 user status and confirmation quote
Comparison: Path to 3D guidance / Blender pixel base / Aseprite draft comparison; preserved items, deliberate adjustments with rationale, unresolved defects; consumed data fields
Texture: Material/plane, direction, density, seed/algorithm version, coverage definition
Checks: Technical criteria and results; agent visual self-check with concrete rationale; preview versions, user status, and verbatim quotes for Q1, Q2, Q3, Q4, Q5; remaining defects
Artifacts: Sources, exports, previews, jobs/logs; current phase and acceptance/integration status
Continuity: Preserved relationships, remaining issues, next steps
```

## Game Integration

When tasks include integration, inspect signed-off previews and source files, then copy PNGs/sheets and required JSON directly to `game/packages/<pack-id>/images/`, updating references per existing package formats. Inherit project nearest-neighbor, disabled mipmaps, and lossless settings; verify scaling, margins, and clarity under keep-aspect containers in live windows. Parchment Fantasy complex props retain native 64x64 files by default, scaled by display nodes; prefer integer-factor scaling (e.g., 128x128, 256x256) without converting to SVG. Non-integer scaling and downscaling require live container inspection of pixel grids and details, which cannot be substituted by large previews.
