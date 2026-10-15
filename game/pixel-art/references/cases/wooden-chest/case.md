# Wooden Chest Texture Case

In-house wooden chest with full cast shadow, demonstrating material zoning, value structure, and irregular wood grain. Main subject is 64x64, full-shadow canvas is 96x64, 11 actual colors, alpha is 0/255. The chest cavity uses solid interior simplification; this does not imply opening structures may be omitted in other tasks.

## Production and Verification

Simplified chest body, lid, latch, and metal bands -> Orthographic camera and Cycles -> Native-grid ray queries for components, world normals, and distances -> Value grouping by material and plane -> Aseprite rough draft and material refinement -> Sparse short clusters and broken seams -> Full cast shadow review.

Area light visibility represents the unoccluded ratio across the disc center and 8 peripheral points, constituting a 9-point geometric approximation. This case used an earlier Blender -> Aseprite pipeline without the current fixed Pixel Shader, and does not serve as a full verification of the active six-phase pipeline.

- Color families used: `leather/gold/hair/earth`; warm wood selects the leather working ramp.
- Wood grain consists mostly of 2–4 pixel short clusters, with occasional thicker clusters, small knots, and unequal-length seams.
- 66 texture pixels / 1117 wood pixels, yielding 5.91% coverage; seam substitutions are calculated separately, totaling 132 altered subject pixels.
- Outlines, latch, two metal bands, and ground shadow were protected during texture editing.

Dimensions, families, coverage, and sample counts are specific to this test case. Reusable techniques include zoning by material, applying sparse irregular clusters, protecting key landmarks, and re-checking values.

## Files

[Main Subject PNG](native.png), [Pixel Source](source.aseprite), [Full Shadow PNG](with-shadow.png), [Shadow Source](with-shadow.aseprite), [Zoom Preview](preview.png), [Technical Manifest](manifest.json). Public cases do not carry raw sessions or external project paths.
