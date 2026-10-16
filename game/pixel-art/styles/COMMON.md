# Common Pixel Specifications

All styles share these specifications; themes, proportions, outline language, and material treatments are defined in the corresponding `STYLE.md`.

## Forms and Pixel Clusters

- The subject, action, and key landmarks must be recognizable at native resolution; details are subordinate to major forms, and textures are subordinate to materials.
- Preserve native grids, organizing curves and diagonals through consistent staircasing. Eliminate accidental stray pixels, edge banding, and meaningless noise; purposeful single pixels such as eye dots and gem glints may be retained.
- Outlines, material zoning, and major values must be established before adding details. Flat symbols prioritize semantic meaning and negative space; 3D objects prioritize planar transitions and occlusions.
- Identity IDs are sampled by category; normals and depth are interpreted per their data definitions. Pixel abstraction may adjust outlines and enlarge landmarks while preserving semantics and structural relationships.
- Previews use native scale, integer zoom, and greyscale; silhouettes diagnose outlines. Evaluate legibility from actual images, interpreting automated hints in context.

## Fixed Color Families and Budgets

**A set of tonal shades progressing from dark to light for a material constitutes one color family.** Multiple materials may share a single family, while independent families used for outlines and special effects count against the budget. Total RGB color count is statistical metadata, not an asset budget; for example, three 5-shade ramps still count as three families.

`palette.json` provides numerical criteria: `locked`, `family_count`, `families`, per-family `shade_count` (defaulting to `shades_per_family`), `material_families`, `asset_family_limits`, and `alpha_policy`. `colors` and `ramps` derive from these fixed families, and `color_count` represents inventory totals.

Record palette version, intended purpose, selected families, and material mappings before painting. Painting must be conducted within selected ramps; palette version bumps require explicit user instructions. Animations and all production PNGs for a single asset share a pooled family budget, with shared shades counted under declared ownership.

Tonal step counts adhere to style definitions; working subsets may be used. Tonal organization prioritizes adjusting block area and material grouping, preserving necessary shadow, illuminated, and specular tiers. When updating legacy assets to the current style, migrate them to the active palette.

## Specific Specifications

- [Common Base](../specs/common.md): Native grid, staircasing, and cluster rules.
- [Lighting](../specs/lighting.md): Illumination, occlusion, contact shadows, and post-detail value re-checks.
- [Texture](../specs/texture.md): Micro-cluster organization, density, and layer isolation.
- [Materials](../cards/materials/): Specific material behaviors for wood, metal, skin, cloth, and glass/gems.
- [Delivery](../specs/production.md): Source files, exports, technical checks, reviews, and logs.
