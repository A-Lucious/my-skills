# Portraits: Style Pixel Shader & Advance Preview (psap)

First use [Portrait Design](design.md) to select the route. Use the character record's native dimensions, framing, and declared palette families.

## 1. Native Base Generation

### Standard 3D route

Mount the selected style's `PIXEL-SHADER.md` and fixed Shader, preserving the recorded camera and lighting.

- Execute the existing style Shader through Blender MCP; use `asset_type="portrait"` for Parchment Fantasy and the corresponding purpose code for another style.
- Apply material-to-family zoning so skin shadows, hair, clothing, and background cannot silently borrow unrelated ramps.
- Record the actual dimensions, style/palette versions, script identity, and inputs in the Shader manifest. Do not invent a portrait-specific quantizer or replace the base with a resampled concept image.

### Conditional image-source route

- Apply the [smooth portrait Pixel Shader](../../styles/parchment-fantasy/PORTRAIT-PIXEL-SHADER.md) to the selected generated/uploaded AI source through real Blender MCP before Aseprite production. For Parchment Fantasy use `portrait_pixel_shader.py`; it reuses the fixed style's Oklab palette mapper.
- Preserve the chosen face crop: area sampling to a working grid -> anisotropic Kuwahara smoothing -> area sampling to native size -> locked style palette -> binary alpha. Do not substitute plain nearest-neighbor reduction, a raw generated image, or an unfiltered face/eye restoration branch.
- Aim for the accepted smooth, coherent facial and hair clusters. Smoothing strength is a task parameter; the accepted screenshot did not establish an exact numeric preset. Do not keep increasing it after the desired effect is reached.
- The Shader reduces fragmented shading and downsampling noise. Eye shape, gaze, iris/pupil, catchlights, and expression remain Aseprite postprocessing in [pcdt.md](pcdt.md). Do not restore noisy raw eyes to “protect” features.
- Record source/hash, crop, working/native sizes, smoothing parameters, palette/script versions, and the exact native output path. Use only genuine 2D region masks when needed for palette ownership; do not label them as 3D guidance. For another style, retain this smoothing stage and use that style's declared palette mapper rather than imposing Parchment colors.

## 2. Structure & Value Retention

Inspect the native output, integer zoom, greyscale, and same-framing upstream comparison:
- Does the face retain its length, jaw shape, near/far relationships, and hair silhouette?
- Are eye sockets, nose planes, mouth region, and jaw-to-neck separation readable at the chosen grid?
- Are explicit features still representable, including anchors for marks to be drawn in Aseprite?
- Have quantization or material boundaries introduced foreign colors, black patches, merged facial planes, or cross-family bleeding?

If structure is lost, revisit the route's source, framing, native grid, and smoothing strength (or the model for the 3D route). If values or colors are lost, inspect palette ownership and color transforms before changing source illumination. Do not use a finer display export to imply recovery of missing detail.

## 3. Preview Handoff

Present the native pixel base and same-view comparison and record Q3 under the existing review rules. Phase 4 imports this exact base. Save the native PNG, essential previews, and Shader manifest.
