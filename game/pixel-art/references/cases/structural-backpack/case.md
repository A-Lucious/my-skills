# Structural Backpack Production Check

The current Blender production check uses [Shader 2.0.0](../../../styles/parchment-fantasy/PIXEL-SHADER.md), Palette 4.3, native 64×64, and leather/earth/gold/green families.

Real pre-light native-grid ray queries provide visibility, geometric world normals, ray distances, material and object IDs. Structural Sobel/NMS, thinning and redundant corner removal produce candidate and protection masks; Aseprite MCP writes the native mask. Actual Blender lighting then receives SOFT.04 only outside the 1px structure band, followed by fixed palette quantization. Aseprite MCP imports this exact base and applies constrained neighboring source colors before refinement.

- 1919 sampled surfaces, 1921 rendered opaque pixels; the 2px discrepancy receives no unassigned structural write.
- Protection band: 1321 samples (68.84%); 8 corner candidates, 1 protected small-part candidate, 1 safe source-color correction.
- Formal export: 34 visible colors, binary alpha, 0 material-family violations; exported pixels match the accepted structure-protected result exactly.
- Packed standalone Blender source reload, mandatory-guidance/stale-camera checks, 48×32 native-grid execution, and the independent 2D portrait palette-mapper regression were verified.

This is an algorithm and rough-draft cleanup check. The broad protection band reduces dither on this small, multipart object; new subjects still require visual inspection and artistic refinement.

[Native PNG](native.png) · [4× Preview](preview.png) · [Editable Aseprite Source](source.aseprite) · [Checks](manifest.json)
