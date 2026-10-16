# Parchment Fantasy

Production Palette 4.3. Structures fantasy themes through warm paper tones, low-saturation natural materials, and selective vibrant accents; tonal ramps preserve material reflections, transmittances, and shadow nuances. Historical visual research referenced visual observations of third-party games; see [NOTICE.md](../../NOTICE.md) for provenance and unofficial statements. This style does not bundle third-party game screenshots, crops, or tracing studies. Shares [COMMON](../COMMON.md); see [Reference Studies](REFERENCE-STUDY.md) for provenance and observational methodology.

Step 3 of the pipeline executes this style's fixed [Pixel Shader](PIXEL-SHADER.md), presenting advance previews under the active camera before proceeding to Step 4 Aseprite rough drafting. The implementation is housed in this style directory at [pixel_shader.py](pixel_shader.py); current technical baseline is `1.3.0`, Palette `4.3`, and native `64x64`.

## Visual Language

Parchment user interface and dark fantasy theme; scenes maintain low saturation, while attribute symbols and specific materials establish clear focal points. Characters employ semi-realistic proportions; outlines derive from adjacent material shadow planes or pale edges using selective outlining. Curves are expressed through stable staircasing, and details are organized in directional pixel clusters.

| Subject | Reference Characteristics |
|---|---|
| Symbols & Icons | Clear silhouettes and minimal color blocking communicate semantics; specific shapes designed per task |
| Gems & Metals | Faceted planes, narrow highlight rims, and contact shadows express material properties |
| Paper Frames & Trim | Warm paper surfaces, stepped corners, and margins; column dividing and decorative rhythm designed per content |
| Props & Travel Gear | Distinguish openings, seams, metal hardware, and surface curvatures; landmarks legible at native resolution |
| Portraits | Warm skin tones, dark brown hair; cohesive brow, nose side, jawline, neck, and collar; restrained facial proportions |
| Townships | Beams, stone/grey walls, tiles, doorways, streets, and character material blocks distinct; eaves shade walls, objects grounded |

## Grids and Information Density

Select production canvases based on content and display containers; do not confuse screenshot sizes or compressed grid estimates with native dimensions. Reference observations are logged per the [Study Specification](REFERENCE-STUDY.md).

Complex props and this style's Shader previews default to native **64x64**, preserving room for surface value gradients, seams, and material highlights; follow task requirements when users explicitly designate other dimensions. Portraits are sized by their display containers; symbols use smaller grids that clearly express semantics and cutouts. Each asset independently determines cluster scale and origin.

In-game rendering uses native PNGs scaled by UI display nodes; integer-factor nearest-neighbor scaling preserves the pixel grid (e.g., 64 -> 128/256). Pre-converting to vector graphics is unnecessary; non-integer scaling creates uneven pixel grid widths, while downsampling back to 32x32 discards newly introduced details. Always inspect live display proportions during integration.

## Materials and Palette

[palette.json](palette.json) locks 20 selectable color families and 236 inventory color values. `earth` features **18 shades**, `blue` features **16 shades**, `ruby` features **40 shades** (potions / tinted red glass and low-saturation reflections under glass), and other 3D materials feature **12 shades**; attribute symbols retain legacy 2–5 shades. Per-purpose family caps adhere to the JSON schema; adding tonal shades to an existing family does not increment family count, nor is an asset required to exhaust all available shades.

| Family | Common Uses |
|---|---|
| `earth`, `green`, `skin`, `hair` | Wood/stone, natural olive green, warm skin tones, and hair |
| `paper`, `parchment` | Pale paper, white symbols, book pages, and light fabric |
| `leather`, `gold`, `teal` | Warm leather, bright gold, teal-blue book covers |
| `ruby`, `jade`, `fuchsia` | Red/cyan-green status gems, magenta chest-interior gems |
| `red`, `sky`, `purple`, `heart_green`, `indigo` | Attribute-specific colors distinct from natural materials |
| `neutral`, `blue`, `ember` | Dark grey, cool metal/scales, flame |

Unless specified, original work defaults to top-left key lighting; reference studies adhere to visible lighting. Metal/gem highlights are narrow and sharp; leather/cloth highlights are broad and restrained. Current production uses alpha 0/255, normal blend mode, opacity 255, hard-edged ramps, and pixel clusters.

[palette-v3-legacy.json](palette-v3-legacy.json) interprets older outputs. Reference studies employ independent observation whitelists, recording compression variations per the [Study Specification](REFERENCE-STUDY.md).

## Empirical Baselines

- [Wooden Chest Texture v2](../../references/cases/wooden-chest/case.md): In-house single-object Blender -> Aseprite material and texture test case; earlier pipeline that predates the fixed Shader.
- [Potion Bottle Base](../../references/cases/health-potion/case.md): Fixed Shader material zoning and display lighting test case, covering Step 3 only.
