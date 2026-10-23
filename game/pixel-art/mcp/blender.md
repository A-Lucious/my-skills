# Blender MCP

Blender provides structural, camera, and lighting guidance. In Step 3, it executes the fixed style Pixel Shader and exports a native pixel base for Step 4 import. Prioritize registered Blender Lab `blender` tools.

## Connection and Startup

Begin by calling `get_blendfile_summary_datablocks` and `get_objects_summary` to inspect the active file, scene, mode, and selection. If dedicated tools are unavailable, use `execute_blender_code` to execute bpy, placing results in a JSON-serializable `result`; check `isError`, data `status`, and nested `result.status`.

Inspect existing Blender MCP registrations in the environment to verify server host, addon, and port; do not assume predetermined install paths or background auto-start status. If connection fails, check the Blender process, addon enablement, Online Access permissions, and configured port.

GUI sessions use the local Blender executable. When using the Blender Lab addon with command support, launch the background bridge with:

```bash
blender --background <file.blend> --command blender_mcp
```

Retain only one active server instance when interactive and background instances share a port. If tools are not loaded or standalone diagnostics are needed, run from the project root:

```bash
tools/aseprite-mcp/.venv/bin/python .agents/skills/pixel-art/scripts/check_blender_mcp.py
```

This script reads configurations, lists tools, and queries active scenes for connection verification only.

## Scenes and Files

Inspect existing scenes first; work within isolated scenes, files, or copies, preserving original models and objects. Use absolute paths for Blender file arguments; see [Production Specification](../specs/production.md) for directory and version layouts.

Assign stable identities to parts and materials; save camera matrices, projection, light sources, render engine, and resolution. Update dependent guidance data whenever models, poses, cameras, or meshes change.

## Guidance Passes and Definitions

Required guidance for Phase 2 comprises actual RGB/alpha, part/material IDs, normals, and depth for the active iteration. Guidance can be exported as render passes or sampled via real `scene.ray_cast` on target grids in Blender MCP, recording per-pixel hits, IDs, normals, and distances. The latter may be stored in JSON/NPZ arrays with grid origins, spacing, camera, and coordinate definitions. Do not substitute spatial samples with object lists, pass_index values, or light parameters; never forge sampling results outside Blender using mathematical ideal formulas.

| Signal | Storage & Interpretation |
|---|---|
| RGB/alpha | PNG for inspection; record color space and background |
| Part/Material ID | Category ID and mapping table; inspect categories individually |
| Normal | Raw float data and normal coordinate space |
| Depth | Distance definition, units, background values |
| Base color, direct/indirect light | Differentiate material albedo from lighting response; record color space |
| Specular, AO, occlusion/visibility | Save as needed; clarify implementation and meaning for each signal |

Retain raw float signals from render passes as EXR; store ray queries as raw numerical arrays, reading samples to confirm actual content. The guidance manifest records source versions, pass/array paths, dimensions, data semantics, and valid sample counts, distinguishing "actually used in Steps 3 & 4," "archived only," and "missing." Phase 2 remains incomplete if required guidance is missing; configuration metadata must not be labeled as "spatial guidance actually used in Steps 3 & 4." Direct diffuse accounts for incident light and material response; AO denotes localized ambient occlusion; independent light visibility is defined by its sampling method.

Query identities, world positions, normals, and ray distances at pixel centers of the target grid using `scene.ray_cast`; record grid origin, pixel pitch, and camera matrix. Keep world normals and world light sources in a unified coordinate frame. See [Wooden Chest Case](../references/cases/wooden-chest/case.md) for occlusion approximations and sampling parameters.

## Step 3: Style Pixel Shader and Direct Base Output

For the conditional [portrait image-source route](../cards/portraits/design.md), use the [smooth 2D portrait Shader](../styles/parchment-fantasy/PORTRAIT-PIXEL-SHADER.md) instead of the 3D-render instructions below. Its input is the selected 2D image; no physical-lighting or geometry passes are required. Preserve the real source and record its preprocessing parameters.

Load `styles/<style-id>/pixel_shader.py` directly through live Blender MCP to render native pixel PNGs inside Blender. Each style maintains its own fixed script; see [Pixel Shader](../styles/parchment-fantasy/PIXEL-SHADER.md) for Parchment Fantasy implementations, inputs, and executable calls. Bpy nodes and rendering are executed via real MCP; external scripts only orchestrate calls and must not read/write pixels to forge Shader outputs.

- **Verify implementation first.** Check the selected style script path, version, hash, and Blender/engine compatibility; use interfaces actually provided by that script. If missing or incompatible, maintain that style's script and preview results first; do not borrow from other styles, download external plugins with matching names, or assemble improvised node setups per task.
- **Preserve geometric and lighting baselines.** Use confirmed models, cameras, target grids, and lighting; place pixelated materials and compositing in working copies. Retain original normal, depth, and ID guidance separately from pixelated color maps; do not treat processed color as raw spatial signals.
- **Fixed style algorithm.** Parchment Fantasy 2.0.0 first samples geometry at native pixel centers, then uses `structural_edges.py prepare` and real Aseprite MCP to create the 1px structure protection band. Only after that does `render_preview` render actual lighting, apply protected SOFT.04 in Oklab L, and quantize to the fixed palette. Guidance is mandatory; the old guidance-free renderer is removed. Defaults to native 64x64 with 4.3 color ramps. Task inputs must declare every visible material-to-allowed family mapping; the script generates masks via real ray-casts inside Blender to restrict palette selection per region, while light and shadow derive from the actual render. Preserve original materials unless modification is requested. Algorithm updates require version bumps and regenerated previews; re-render inputs and masks whenever models, cameras, lights, frames, or source display transforms change, avoiding stale viewpoints.
- **Target grid and dimensions.** Final pixel bases must match task WxH; save upscaled images separately for preview. Parchment Fantasy renders directly at native low resolutions with `Pixelate` Size fixed to 1; do not masquerade high-res mosaics as native pixel bases for visual convenience. Structure arguments to match real-time node schemas.
- **Palette and edges.** Validate exported colors, alpha, apertures, and component joints; passing technical checks does not waive visual form verification. Aseprite must still organize materials and clusters against fixed color families in subsequent steps. If sampling loses critical landmarks, adjust the model or grid in Blender and re-render.
- **Showcase first, then import to production sources.** Save working `.blend` files, native bases, same-view before/after comparisons, and Shader manifests in `Test Workspace/`; present to the user and log Q3. Reuse this exact base in Step 4; return to this step if inputs or scripts change. Importing and upscaling previews in Aseprite at this stage is for demonstration only and does not mark the production rough draft as complete.

## Verified Interface Scope

Technical verification on Blender 5.2.2 LTS covers MCP modeling, orthographic cameras, area lights, Cycles, PNG/multi-layer EXR exports, and headless `.blend` reloads. Interfaces adhere to active bpy and tool schemas.

- Tested pass names: `Depth`, `Normal`, `Object Index`, `Material Index`, `Diffuse Color`, `Diffuse Direct`, `Diffuse Indirect`, `Glossy Direct`, `Ambient Occlusion`.
- In this version, multi-layer EXR requires setting `image_settings.media_type = 'MULTI_LAYER_IMAGE'` followed by `file_format = 'OPEN_EXR_MULTILAYER'`; PNG previews require `media_type = 'IMAGE'` and `file_format = 'PNG'`, restoring previous formats afterward. Earlier versions should use corresponding properties.
- The compositor interface in this version is `scene.compositing_node_group`.
