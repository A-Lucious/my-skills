# Flame Sword / 火焰长剑

An accepted, original inventory prop demonstrating the complete Blender-to-Aseprite pixel-art pipeline: a slender flaming blade, a brown fabric-wrapped grip, a silver crossguard, and a round silver pommel.

已验收的原创物品案例：细长剑身缠绕火焰，棕色布条缠柄，银色护手与圆头剑首；展示 Blender 建模、固定像素 Shader、Aseprite 精修和正式导出的完整流程。

![Flame sword, exact 6× nearest-neighbor preview](preview.png)

## Artifacts / 文件

- [Native transparent PNG / 原生透明 PNG](native.png): 64×64.
- [Editable Aseprite / 分层源稿](source.aseprite): five layers, including an untouched, hidden, locked `base-ref`.
- [Inventory background comparison / 物品栏背景对比](backgrounds.png): 2× previews against dark, neutral, and parchment backgrounds.
- [Original Shader base / 原始 Shader 底稿](shader-base.png): the same 64×64 pixels imported into Aseprite, re-exported through MCP to omit machine-specific PNG metadata.
- [Technical manifest / 技术清单](manifest.json): parameters, checks, and artifact hashes.

## Pipeline

1. Build separate blade, crossguard, wrapped grip, round pommel, and layered flame meshes in Blender through MCP. Use a diamond-section blade, an orthographic camera, a 37° screen-space sword axis, and a slight depth tilt to expose material planes.
2. Render actual Cycles lighting with an upper-left key, a cool fill, and local orange fire bounce. Real native-grid ray casts provide material identities, world normals, positions, and distances. Material masks restrict palette families; normals and depth support structural inspection rather than replacing rendered lighting.
3. This historical asset used the then-current palette mapping at native 64×64. New production uses the sole [structural baseline](../../../styles/parchment-fantasy/PIXEL-SHADER.md).
4. Import that exact base through Aseprite MCP; preserve locked `base-ref` and duplicate it to `draft`. Consolidate ramps, strengthen flame contrast, and correct ambiguous palette assignments at flame boundaries.
5. Refine flame curls and bright cores, narrow blade and guard highlights, fabric fold clusters, and the rounded pommel on separate `fire-detail`, `metal-highlight`, and `cloth-fold` layers. Shift the visible composition −4 px horizontally and +2 px vertically to center it; the reference layer remains unshifted.
6. Inspect native, enlarged, greyscale, and inventory-background views. Export the native transparent PNG and exact 6× preview through Aseprite MCP, then verify palette, alpha, connected silhouette, source layers, and byte-identical archived copies.

## Palette and scope

- Style: `parchment-fantasy`; Palette 4.3; families `blue`, `earth`, `ember`.
- 22 visible colors, binary alpha 0/255, 575 visible pixels, one 4-connected silhouette component, and at least 7 px canvas margin.
- Native base, final PNG, and editable pixel source are retained. Geometry, packed shader scene, and raw spatial guidance are archived with the production project.
- This is a static inventory item; no flame animation or game integration is claimed.
- Thin diagonal highlights and selective outlines are intentional. Same-color singleton diagnostics are not a promise of zero texture noise or universal readability at every display scale.
- The final asset was accepted for archiving. Intermediate stages were executed and inspected, without claiming separate user approval at every stage.

This is an independent skill output, not an official asset from a third-party game. See [the provenance notice](../../../NOTICE.md).
