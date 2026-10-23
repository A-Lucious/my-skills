# Ancient Marble Fountain / 远古大理石遗迹平台

A six-sided marble basin around a raised central plinth. Both tiers are shallowly recessed, with still water below their lips, masonry joints, mineral veins and sparse moss.

六边形大理石外池环绕抬高的中央石台，两层均向内浅凹并蓄水，带石块拼缝、大理石纹、裂缝和少量青苔。

**Gallery category / 案例分类:** Buildings / 建筑.

![Ancient Marble Fountain, transparent 6× nearest-neighbor preview](preview.png)

## Artifacts / 文件

- [Native transparent PNG / 原生透明 PNG](native.png): 64×64, binary alpha 0/255.
- [Transparent 6× preview / 透明放大预览](preview.png): 384×384, exact nearest-neighbor enlargement.
- [Editable Aseprite / 可编辑源稿](source.aseprite): 6 layers; untouched hidden and locked `base-ref`.
- [Background comparison / 背景对比](backgrounds.png): paper, gray and dark display backgrounds, explicitly opaque.
- [Technical manifest / 技术清单](manifest.json): palette, checks, artifact sizes and hashes.

README and case previews keep their original transparency. The separate background comparison deliberately adds backgrounds; use `native.png` for the transparent asset.

README 与案例预览均保留透明背景；背景对比图才带底色。需要透明素材时使用 `native.png`。

## Pipeline

1. Build a dedicated scene through Blender MCP. Model genuine hollow six-sided retaining walls in two courses, split each side into two blocks, and build the raised hollow central plinth separately. The center lip stands above the outer lip; both water planes remain below their rims.
2. Render physical upper-left lighting with Cycles. Real native-grid ray casts record object/material IDs, world normals, positions and distances. Material masks constrain palette mapping; normals and depth support structural inspection.
3. This historical asset used the then-current palette mapping at native 64×64. For new production, use the sole [structural baseline](../../../styles/parchment-fantasy/PIXEL-SHADER.md).
4. Import that exact base through Aseprite MCP. Preserve hidden locked `base-ref` and duplicate it into an editable `draft`.
5. Consolidate warm marble highlights and cool shadows. Add separate marble-vein, weathering, water and masonry-joint layers, with 36, 27, 16 and 16 detail pixels respectively. Place joints against actual block-identity guidance and clean 99 stray draft colors.
6. Inspect native, integer-enlarged, grayscale, silhouette and background views. Export native PNG and 6× transparent preview through Aseprite MCP; verify palette, alpha, editable layers and preservation of the Shader base.

## Palette and scope

- Style: `parchment-fantasy`; Palette 4.3; families `paper`, `blue`, `teal`, `green`.
- 23 visible colors, 1398 opaque pixels, binary alpha 0/255; zero colors outside declared families.
- Editable layers: `base-ref`, `draft`, `marble-veins`, `weathering`, `water-details`, `masonry-joints`.
- Gallery taxonomy groups vegetation with buildings; the recorded production palette purpose remains `scene`.
- Static asset; geometry, packed Shader scenes and raw spatial guidance stay in the production workspace. No game integration or animation is claimed.
- Original delivered skill output, added to the showcase on request. Separate stage-by-stage user approval is not inferred.
- Selective outlines, thin highlights, diagonals and small texture clusters are intentional; no zero-noise claim.

This is an original skill output, not an official third-party game asset. See [the provenance notice](../../../NOTICE.md).
