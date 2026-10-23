# Armored Spider Portrait / 盔甲蜘蛛人物画像

An accepted, independently generated fantasy portrait demonstrating the complete image-source portrait route through Aseprite refinement. No third-party reference image was supplied.

已验收的奇幻蜘蛛画像，展示生图来源路线从人物设计、平滑 Shader 到 Aseprite 精修与正式导出的完整过程。

![Armored spider portrait, 6× nearest-neighbor preview](preview.png)

## Artifacts

- [Native PNG / 原生 PNG](native.png): 96×96, opaque parchment background.
- [Editable Aseprite / 可编辑源稿](source.aseprite): five layers, with the exact Shader base hidden and locked.
- [Refinement comparison / 精修前后对比](comparison.png): approved Shader base on the left, refined portrait on the right, both at 4×.
- [Technical manifest / 技术清单](manifest.json): parameters and artifact hashes.

## Pipeline

1. Generate one 1254×1254 head-and-neck design with the built-in image model: eight dark eyes, paired chelicerae and fangs, an open-faced steel helmet, and restrained brass trim.
2. Execute `portrait_pixel_shader.py` version 1.0.0 through Blender MCP. Regular footprint sampling and Anisotropic Kuwahara smoothing use a 384×384 working grid, then produce the 96×96 native base. Smoothing radius is 4.0; the fixed Oklab mapper is version 1.3.0 with Palette 4.3. No face or eye bypass is used.
3. Import that exact base through Aseprite MCP. Preserve hidden, locked `base-ref`; duplicate to `draft`. Rebuild eight eye contours and add separate `eyes-detail`, `fangs-detail`, and `armor-detail` layers for reflections, curved fangs, and narrow metal edges.
4. Run one protected stray-color cleanup pass on `draft`, replacing 988 isolated color pixels with neighboring existing colors. Retain intentional glints and dark contact shadows, then inspect native, enlarged, and greyscale views.
5. Export the native PNG and exact 6× nearest-neighbor preview through Aseprite MCP. Verify that `base-ref` remains pixel-identical to the Shader output.

## Palette and scope

- Style: `parchment-fantasy`; palette version 4.3.
- Families: `earth`, `blue`, `gold`; 36 visible colors in the native export.
- Binary alpha: all pixels opaque, alpha 255. Zero foreign colors or colors outside the three declared families.
- Framing: a tight nonhuman head-and-neck portrait; helmet meets the top edge and gorget meets the lower edge. This is a background-backed dialogue portrait, not a transparent full-body sprite.
- Lighting is inherited from the 2D source. This route does not claim 3D modeling, physical light measurements, normals, depth, or geometry-based material IDs.
- Residual isolated-color diagnostics include intentional glints, diagonals, and shaded material transitions; the cleanup does not claim zero texture noise.

The design retains spider anatomy and a restrained upper-left lighting impression. This case documents an original skill output; it is not an official asset from a third-party game. See [the provenance notice](../../../NOTICE.md).
