# Potion Bottle Shader Base

In-house red potion bottle showcasing Phase 3 output with Blender live lighting, fixed palette, and material zoning. This case represents a technical Shader base, not a finalized Aseprite-polished asset.

- Native size 64x64, Shader 1.3.0, Palette 4.3, 25 actual colors.
- Color families: `ruby/earth/blue`; cork and strap map to earth, neck rim maps to blue, bottle body and liquid map to ruby.
- Alpha is 0/255; cross-family bleed pixels in cork and neck regions count 0.
- Features red tinted glass, red liquid, and blue-grey neck; 512 samples and specific material settings are test parameters for this case, not defaults for other objects.

[Native PNG](native.png), [4x Preview](preview.png), [Technical Manifest](manifest.json). This case contains no third-party game screenshots, extracted assets, or tracing studies. Public cases do not bundle Blender project files containing local machine paths; for reproduction interfaces, see [Pixel Shader](../../../styles/parchment-fantasy/PIXEL-SHADER.md).
