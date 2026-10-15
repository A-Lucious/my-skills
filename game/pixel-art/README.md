# Pixel Art

通过 Blender MCP 与 Aseprite MCP 制作像素道具、角色、场景及精灵动画。提供分类规范、固定色板、风格 Pixel Shader、分阶段预览和可编辑源稿交付流程。

默认风格为 **羊皮纸奇幻（Parchment Fantasy）**，ID：`parchment-fantasy`。风格来源、非官方关系及第三方素材边界见 [NOTICE.md](NOTICE.md)。

## 案例

以下展示本技能制作的独立素材。预览采用整数倍放大；技术阶段与局限单独标注，历史案例不代表现行六步流程的全部验证。案例仅保留技术信息，不包含个人身份、私人对话或生成日期。

### 多口袋皮革背包

<img src="examples/leather-backpack/preview.png" alt="多口袋皮革背包的四倍像素预览" width="256">

原生 64×64。展示立体口袋、扣带、皮革明暗与材质分区后的像素精修，当前为可审阅候选。

[原生 PNG](examples/leather-backpack/native.png) · [Aseprite 源稿](examples/leather-backpack/source.aseprite) · [技术清单](examples/leather-backpack/manifest.json)

### D20 掷骰动画

![D20 连续投掷演播](examples/d20-dice/preview.gif)

原生 32×32，预览为 192×192。支持 1–20 结果，每个结果包含 16 帧翻滚与定格，母源稿共 320 帧。此例使用早期动画流程。

[Aseprite 源稿](examples/d20-dice/source.aseprite) · [完整图集](examples/d20-dice/sheet.png) · [帧数据](examples/d20-dice/sheet.json) · [技术清单](examples/d20-dice/manifest.json)

### 螺旋星光动画

<img src="examples/spiral-star/preview.gif" alt="星光从四向星展开为圆环并回聚的动画" width="256">

原生 64×64，16 帧。展示星形、圆环与花瓣回聚之间的节奏和粒子运动。此例使用早期动画流程。

[Aseprite 源稿](examples/spiral-star/source.aseprite) · [图集](examples/spiral-star/sheet.png) · [帧数据](examples/spiral-star/sheet.json) · [技术清单](examples/spiral-star/manifest.json)

### 森林篝火动画

<img src="examples/forest-campfire/preview.gif" alt="森林小路中央的篝火、烟与余烬循环" width="360">

原生 180×320，16 帧。展示竖屏场景纵深、材料块、篝火和烟的循环；使用早期 Shader to RGB/Color Ramp 流程，当前为可审阅场景候选。

[Aseprite 源稿](examples/forest-campfire/source.aseprite) · [原生 PNG](examples/forest-campfire/native.png) · [图集](examples/forest-campfire/sheet.png) · [帧数据](examples/forest-campfire/sheet.json) · [技术清单](examples/forest-campfire/manifest.json)

### 药水瓶 Shader 底稿

<img src="references/cases/health-potion/preview.png" alt="红色药水瓶的 Shader 底稿" width="256">

原生 64×64。展示真实显示光影、固定色板和木塞/瓶口/瓶身的材质分区。**仅覆盖第三阶段 Shader，尚不是 Aseprite 精修成品。**

[案例说明](references/cases/health-potion/case.md) · [原生 PNG](references/cases/health-potion/native.png) · [技术清单](references/cases/health-potion/manifest.json)

### 木箱与投影

<img src="references/cases/wooden-chest/preview.png" alt="木箱纹理与完整地面投影" width="384">

主体 64×64，含完整投影的画布为 96×64。展示稀疏不规则木纹、材料分区与接触阴影。此例使用早期 Blender→Aseprite 流程，未使用当前固定 Shader；箱腔采用实心简化。

[案例说明](references/cases/wooden-chest/case.md) · [原生 PNG](references/cases/wooden-chest/native.png) · [Aseprite 源稿](references/cases/wooden-chest/source.aseprite) · [完整投影](references/cases/wooden-chest/with-shadow.png)

## 使用

技能入口为 [SKILL.md](SKILL.md)。需要可用的 Blender、Aseprite、Python 3.11+、Git、uv，以及相应 MCP 服务。Aseprite 可执行文件通过 `ASEPRITE_PATH` 指定，或由启动器查找常见安装位置。

将本文件夹复制到目标项目的 `.agents/skills/pixel-art/`。在目标项目根目录运行：

```bash
python3 .agents/skills/pixel-art/scripts/install_mcp.py
python3 .agents/skills/pixel-art/scripts/mcp_client.py doctor
```

安装器使用技能内的 [固定 MCP 版本清单](mcp/aseprite-mcp.lock.json)，将 Aseprite MCP 安装到目标项目 `tools/aseprite-mcp/` 并写入项目 `.codex/config.toml`。Blender MCP 使用当前环境已注册且可用的服务，连接方法见 [Blender MCP](mcp/blender.md)。

若直接从技能仓库调用而不复制技能，在目标项目根执行技能脚本，并将 `PIXEL_PROJECT_ROOT` 环境变量设置为该项目的绝对路径；技能文件本身不绑定个人目录。

示例请求：

```text
使用 $pixel-art，制作一个 64×64 的奇幻皮革药剂包。
采用 parchment-fantasy 风格，先展示 Blender 模型和 Shader 效果，
再经 Aseprite 粗稿、精修与检查，交付透明 PNG 和可编辑源稿。
```

## 流程与目录

硬表面及空间素材默认执行：3D 与相机 → 光照渲染 → 风格 Shader 预览 → Aseprite 粗稿 → 像素簇与纹理 → 最终检查。有机与装饰类 UI 可按技能规范选择纯 2D Aseprite 通道。详细步骤见 [workflow.md](workflow.md)。

| 目录 | 内容 |
|---|---|
| `styles/` | 通用规则、羊皮纸奇幻风格、色板和固定 Shader |
| `specs/` | 人物、场景、物品、建筑、光照、纹理及交付规范 |
| `mcp/` | Blender/Aseprite 接入说明及固定版本清单 |
| `scripts/` | MCP 调用编排、诊断和只读技术检查 |
| `examples/` | README 展示案例、源稿、图集与帧数据 |
| `references/cases/` | 自制技术案例与适用范围 |

任务产物与临时文件保存在目标项目的 `Test Workspace/`，不会默认写入技能参考库。公开包不附带第三方游戏截图、裁切图、提取精灵或临摹稿；相关来源声明见 [NOTICE.md](NOTICE.md)。
