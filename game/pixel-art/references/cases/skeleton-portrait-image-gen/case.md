# 骷髅人物画像（生图来源路线）

- 规格：原生 64×64 RGBA，parchment-fantasy 风格。
- 构图定位：头部与颈部特写构图，头颅占比大，深眼窝与三角鼻腔居中，无躯干与肩膀挤占像素。
- 流程路线：条件触发生图来源路线（提示词显式包含「用生图模型」）→ 专属人物平滑 Pixel Shader（Anisotropic Kuwahara 4.0 + 调色板映射）→ 像素底稿。
- 调色板：Palette 4.3 `earth` + `paper` 两族（28 色）。
- 状态：完成 Phase 3 Shader 像素底稿与 6× 放大检查。

[原生底稿 PNG](native.png) · [6× 预览图](preview.png) · [生成源图](reference.png)
