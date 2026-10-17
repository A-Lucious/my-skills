# Smooth 2D Portrait Pixel Shader

Use only on the conditional image-source route in [Portrait Design](../../cards/portraits/design.md). A generated portrait or an upload explicitly identified as model-generated receives this preprocessing before Aseprite. This document does not itself authorize a model call.

[portrait_pixel_shader.py](portrait_pixel_shader.py) runs inside Blender MCP. It preserves the selected image's framing and lighting, applies regular 4x4 footprint sampling to a 4x native working grid, anisotropic Kuwahara smoothing, and footprint sampling to native size. Palette mapping reuses [pixel_shader.py](pixel_shader.py)'s fixed Oklab implementation and Palette 4.3. No face or eye region bypasses smoothing; eye and expression refinement belongs in Aseprite.

## Invocation

Copy the selected source into `Test Workspace/<task-id>/references/` and establish the face crop through MCP. Input and native aspect ratios must agree. Pass this code to Blender MCP `execute_blender_code`, replacing the paths and task palette families:

```python
from pathlib import Path

shader = Path("<skill-root>/styles/parchment-fantasy/portrait_pixel_shader.py")
namespace = {"__file__": str(shader), "__name__": "portrait_smooth_shader"}
exec(compile(shader.read_text(), str(shader), "exec"), namespace)
result = namespace["render_preview"](
    "<project-root>/Test Workspace/<task-id>/references/selected-portrait.png",
    output_dir="<project-root>/Test Workspace/<task-id>/shader-v01",
    size=(64, 64),
    families=["skin", "earth", "green"],  # Select for this portrait.
    smoothing=4.0,
)
```

Use a new empty output directory per iteration. `smoothing` is the radius at the working grid (256x256 for native 64x64); 4.0 is a conservative starting point, not a numeric preset approved by the user. The tested prototype compared 4, 10, and 18 at that grid. Choose by the requested effect and preserve readable facial planes; stop increasing smoothing once that effect is reached.

Optional `palette_colours=["#…", ...]` selects useful shades strictly from the declared locked families. Optional `region_masks=[{"image": "<native-mask.png>", "families": ["green"]}]` restricts palette ownership with genuine native-size white-on-black 2D masks prepared through MCP. Overlapping masks apply in list order, with later masks winning. Masks only select palette families from the same filtered input; they never restore raw features. Do not copy one portrait's collar coordinates into another or fabricate geometry guidance.

## Output & Handoff

- `before-native.png`: area-sampled baseline with the same palette and masks, without Kuwahara smoothing.
- `pixel-base-v01.png`: smoothed native base for the exact Aseprite import.
- `before-native-input.png`, `smooth-native-input.png`: 16-bit inputs before palette mapping.
- `shader-preview.blend`: packed source, masks, intermediate inputs, and editable compositor scenes.
- `shader-manifest.json`: source/output hashes, dimensions, versions, filter settings, palette, and pending review status. Record route trigger and model-called yes/no in the production task record.

Inspect the same-crop comparison at 1x and integer zoom through Aseprite MCP. Preserve coherent face and hair clusters without changing identity or expression. Keep Q3 review separate from technical checks; the historical accepted appearance does not approve each new portrait. Import this exact `pixel-base-v01.png`, retain `base-ref`, then refine eye contours, iris/pupil, catchlights, and expression on editable Aseprite layers. Clean up unnecessary comparison intermediates after review while retaining source/editable evidence needed for the current task.
