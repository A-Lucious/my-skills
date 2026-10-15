# Parchment Fantasy Pixel Shader

Fixed implementation: [pixel_shader.py](pixel_shader.py), version `1.3.0`, paired with [Parchment Fantasy Palette 4.3](palette.json). This is a screen-space compositing shader script inside Blender and does not rely on third-party plugins. Loaded via Blender MCP; render pixels are not processed in external Python scripts.

## Effects and Inputs

Pipeline: Active camera render -> native WxH grid -> 16-bit PNG via source scene AgX/Look/exposure in Blender -> Blender compositor nodes map actual display colors to the fixed palette -> 0/255 alpha. Preserves models, original materials, glass transmission, light sources, and source render engines; creates an isolated working scene without modifying upstream scenes. Tested on Blender 5.2.2 LTS / Cycles with sRGB display; compositor nodes use Blender 5.x API; verify other versions/engines before production.

Fixed rules: Source display colors are reverted to display-linear RGB, converted to Oklab in compositor nodes with distance `2×ΔL² + Δa² + Δb²` balancing perceptual lightness and chroma, without square-root brightening or contrast exaggeration. Native render uses filter=0.01, Pixelate Size=1, alpha>0.5. Source scene AgX/Look/exposure takes effect in `lighting-native.png`; final Standard/None (exposure 0, gamma 1, dither 0) encodes the palette only, without reapplying source color transforms. Oklab algorithm references the [author's implementation](https://bottosson.github.io/posts/oklab/). Rules are version-locked with the script.

In v1.1.0, HSV V represented the max RGB channel rather than perceptual lightness; brightening and tinting it exaggerated shadow boundaries. Comparing AgX source images directly to Standard outputs in older versions cannot justify claimed lighting preservation. Version 1.2.0 addressed this; inspect greyscale and representative bottle points rather than relying on palette compliance alone to verify lighting fidelity.

Resolution defaults to `size=(64, 64)`; tasks may explicitly specify `(W, H)`; declare `families` and `asset_type` on every run. Palette selection is restricted to declared families from the active palette, capped per asset purpose. Palette 4.3 allocates 18 shades to earth, 16 to blue, 40 to ruby (including low-saturation shades under glass, deep red tinted glass, and reflections), and 12 shades to remaining 3D materials, preserving all legacy values.

Version 1.3.0 supports declaring allowed color families per Blender material via `material_families`. The script executes real `scene.ray_cast` queries at native pixel centers to generate identity masks; compositor nodes restrict palette selection per region, preventing cork shadows from sampling potion ruby or bottle blue-grey. Lighting derives from the actual render without recomputing lighting from identity masks. Undeclared materials use all task-selected families. When colors bleed across materials, verify inputs and zoning before adjusting lights or contrast to mask mapping errors.

Identity masks detect first-hit surfaces; allowed families for transparent glass must include internal transmission colors. Tested on orthographic potion bottles; first-surface hits must not be conflated with full transmission path decomposition. Geometric normals and ray distances serve identity and structural checks, not replacing Cycles smooth-shaded normals, reflections, or transmission solves.

The script operates on the active camera; viewport angles must be aligned to a working camera via MCP and have their matrix saved. Pre-existing compositor setups in source scenes will reject overwrites; verify their purpose before planning compatibility. Native alpha boundaries use fixed thresholds; inspect glass outer contours, and maintain specialized implementations for semi-transparent visual effects.

## Direct Blender MCP Invocation

Pass the code below as `code` to `execute_blender_code`. When no running instance exists, use `execute_blender_code_for_cli` with `blend_file` pointing to the confirmed `.blend`. Replace `<skill-root>` and `<project-root>` with actual absolute paths; task output directories must be unique per iteration, as existing directories reject overwrites.

```python
from pathlib import Path
import bpy

shader = Path("<skill-root>/styles/parchment-fantasy/pixel_shader.py")
namespace = {"__file__": str(shader), "__name__": "parchment_pixel_shader"}
exec(compile(shader.read_text(), str(shader), "exec"), namespace)
result = namespace["render_preview"](
    bpy.context.scene,
    output_dir="<project-root>/Test Workspace/<task-id>/shader-v01",
    size=(64, 64),
    families=["ruby", "earth", "blue"],
    asset_type="prop_icon",
    # Optional: provide only when verified to exist and match asset purpose.
    material_families={
        "Mat_Cork": ["earth"],
        "Mat_Tie": ["earth"],
        "Mat_NeckGlass": ["blue"],
        "Mat_Glass": ["ruby"],
        "Mat_Liquid": ["ruby"],
    },
)
```

`render_preview` outputs inside Blender: same-camera smooth render `before-smooth.png`, native-size raw comparison `before-native.png`, source-transformed 16-bit lighting input `lighting-native.png`, native pixel base `pixel-base-v01.png`, working `.blend` preserving original scene and nodes `shader-preview.blend`, and `shader-manifest.json` containing script/palette hashes and arguments. Comparison images default to 4x scaling, while the native base remains WxH. The lighting input is packed into the `.blend`, with source display transforms applied exactly once.

Importing the module does not alter scenes; `create_pixel_scene` requires passing a pre-baked `lighting_image` of matching resolution. Image nodes in the active working scene correspond to recorded camera, frame, lights, and models; whenever these inputs change, re-run lighting renders and mapping rather than modifying scenes while reusing stale static inputs. Animation frames are baked per frame via MCP.

When declaring material zoning, the script additionally exports `surface-guidance.json` (hit objects, materials, world coordinates, geometric normals, ray distances) and `material-mask-N.png`; masks are packed into the `.blend`. Verify that exported colors in each material zone belong strictly to their declared families. Material names and family mappings must derive from the active source file without copying example identifiers blindly.

Import preview images via Aseprite MCP and display with integer nearest-neighbor scaling, preserving raw base bytes. Inspect current visual results and present to the user first, keeping Q3 as "pending review" until confirmed; Step 4 uses this exact native base without generating alternatives.

## Technical Baseline

The baseline for Shader `1.3.0` / Palette `4.3` derives from the in-house [Potion Bottle Base](../../references/cases/health-potion/case.md), native `64x64`, 25 actual colors, and 0 cross-family material zoning violations. The base preserves real display lighting and selects colors per material zone.

This case covers Step 3 Shader outputs only and does not represent completed Aseprite rough drafting, refinement, or final delivery; new subjects must generate, present, and review their own effects. Case files contain in-house props only, free of third-party game assets.
