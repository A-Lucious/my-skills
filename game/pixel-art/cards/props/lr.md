# Props: Lighting & Render Setup (lr)

For the standard 3D route, sample native geometry and run structural Sobel/mask preparation before the lighting bake. Use the sole [structural production baseline](../../styles/parchment-fantasy/PIXEL-SHADER.md).

Focuses on cast shadow projection, cavity depth, self-illumination, and material ID separation.

## 1. Key & Ambient Lighting Rig
- **Key Light:** Default to upper-left 45° elevation to create unmistakable primary illumination across top and front faces.
- **Ambient Fill:** Keep fill light soft and low-intensity, ensuring turned/shadow faces remain legible without flattening depth.

## 2. Occlusion & Cast Shadows
- **Internal Cavities:** The lid, opening rim, or stopper must cast a sharp, directional shadow into the interior cavity or neck, immediately conveying physical depth.
- **Overlapping Fixtures:** Metal bands, latches, straps, and guards must cast crisp contact shadows onto underlying wood, glass, or cloth surfaces.
- **Ground / Base Shadows:** Preserve receiving plane shadows underneath the object to ground it firmly; ensure full shadow contours stay within canvas margins.

## 3. Emissive & Translucent Elements
- For magic potions, glowing gems, or burning runes: add a localized secondary light source that casts subtle color bleeding onto adjacent rims and container inner walls.

## 4. Part & Material ID Mapping
- Assign distinct material pass indices or flat ID colors to separate components (e.g. wood body vs. brass metal bands vs. leather straps vs. glass/liquid) to prevent edge bleeding during shader quantization.
