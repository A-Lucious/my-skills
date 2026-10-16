# Props: Pixel Clusters, Details & Texture (pcdt)

Focuses on edge staircasing cleanup, bevel/rim specular highlights, assembly seams, and material texture clusters.

## 1. Edge & Curve Staircasing Cleanup
- Inspect curved and diagonal contours (bottle round bottoms, cylindrical rims, sword edges) at 4x/8x zoom.
- Clean inconsistent jaggies into rhythmic staircasing (e.g. 1-1-2-2-3 or 2-2-1-1 patterns); eliminate stray orphan pixels and accidental double-thick corners (doubles/banding).

## 2. Bevel & Rim Specular Highlights
- Place 1-pixel wide specular highlights along the top-lit turning edges of metal bands, box lids, blade bevels, or glass shoulders.
- Use the lightest shade of the active material ramp (or paper/white accent); keep specular highlights narrow and sharp for metals/glass, restrained for leather/wood.

## 3. Structural Seams & Fasteners
- **Board Seams:** Draw wooden plank divisions using broken, discontinuous 1-pixel dark lines rather than solid continuous black bars.
- **Rivets & Screws:** Represent rivets on metal brackets as single-pixel accent dots paired with a dark shadow pixel underneath.
- **Stitching:** Represent leather seams with rhythmic 1-pixel dash patterns.

## 4. Texture Cluster Application
- Follow the injected `cards/materials/` rules for wood grain, metal scratches, and leather grain.
- Enforce strict texture coverage limits (typically 5%–8% of the material's surface area) to avoid visual noise.
