# Pixel Art

通过 **Blender MCP + Aseprite MCP**，将素材需求转化为可编辑、可导出的像素美术。适用于道具与装备、角色与生物、场景与建筑、界面装饰及精灵动画。

技能将风格、配色、形体、光照和像素精修串成完整流程：先检查结构与视觉效果，再整理像素簇、材质和动画，最终交付原生 PNG、动画图集及可编辑的 Aseprite 源稿。

默认风格为 **羊皮纸奇幻（Parchment Fantasy）**，风格 ID 为 `parchment-fantasy`，也可按任务扩展独立风格。

## 制作流程

先确定对象、用途、尺寸和风格，再选择适合素材的制作通道。Blender 提供形体与光照依据，Aseprite 完成像素整理、细化和正式导出。

```mermaid
flowchart LR
    A["3D 建模<br/>与相机"] --> B["光照<br/>与渲染"]
    B --> C["Pixel Shader<br/>效果预览"]
    C --> D["Aseprite<br/>像素粗稿"]
    D --> E["像素精修<br/>纹理与动画"]
    E --> F["效果检查<br/>与交付"]
    G["纯 2D 通道<br/>有机与装饰类 UI"] --> D
```

硬表面与空间素材采用完整的 3D 通道；有机与装饰类 UI 可按任务选择纯 2D 起稿。各阶段展示实际预览并记录评审，Shader 效果在进入像素粗稿前展示。

## 案例

<table>
  <tr>
    <td align="center" valign="middle"><img src="examples/leather-backpack/preview.png" alt="多口袋皮革背包" width="192"></td>
    <td align="center" valign="middle"><img src="examples/d20-dice/preview.gif" alt="D20 掷骰动画" width="192"></td>
    <td align="center" valign="middle"><img src="examples/spiral-star/preview.gif" alt="螺旋星光动画" width="192"></td>
  </tr>
  <tr>
    <td align="center" valign="middle"><img src="examples/forest-campfire/preview.gif" alt="森林篝火动画" width="180"></td>
    <td align="center" valign="middle"><img src="references/cases/health-potion/preview.png" alt="药水瓶 Shader 底稿" width="192"></td>
    <td align="center" valign="middle"><img src="references/cases/wooden-chest/preview.png" alt="木箱纹理与投影" width="192"></td>
  </tr>
</table>

## 使用

准备可用的 Blender、Aseprite、Python 3.11+、Git、uv，以及相应 MCP 服务。将本文件夹复制到目标项目的 `.agents/skills/pixel-art/`，在项目根目录执行：

```bash
python3 .agents/skills/pixel-art/scripts/install_mcp.py
python3 .agents/skills/pixel-art/scripts/mcp_client.py doctor
```

安装器按固定版本安装 Aseprite MCP 并写入项目配置。Blender MCP 使用当前环境已注册的服务；详细接入方式见 [Blender MCP](mcp/blender.md) 与 [Aseprite MCP](mcp/aseprite.md)。Aseprite 安装在其他位置时，通过 `ASEPRITE_PATH` 指定可执行文件。

向支持该技能的 Agent 提出需求，例如：

```text
使用 $pixel-art，制作一个 64×64 的奇幻皮革药剂包。
采用 parchment-fantasy 风格，先展示 Blender 模型和 Shader 效果，
再进行像素精修，交付透明 PNG 和可编辑源稿。
```

若直接从技能仓库调用脚本，在目标项目根执行，并将 `PIXEL_PROJECT_ROOT` 环境变量设为目标项目的绝对路径。制作产物和临时文件统一保存在该项目的 `Test Workspace/`。

## 技能说明

[SKILL.md](SKILL.md) 是技能入口，负责风格、分类和制作通道的选择；[workflow.md](workflow.md) 说明各阶段的执行与评审方式。

| 目录 | 内容 |
|---|---|
| `styles/` | 通用规则、风格定义、固定色板与 Pixel Shader |
| `specs/` | 人物、场景、物品、建筑、光照、纹理及交付规范 |
| `mcp/` | Blender 与 Aseprite 接入说明、固定版本清单 |
| `scripts/` | MCP 调用编排、诊断与只读技术检查 |
| `examples/` | 展示素材及其可编辑源稿、图集和帧数据 |
| `references/cases/` | 自制技术案例、适用范围与限制 |

羊皮纸奇幻的历史视觉研究参考过 **Life in Adventure**，本技能与该游戏及其权利人无官方关联。公开包不附带该游戏的截图、裁切图、提取素材或临摹稿；来源与权属说明见 [NOTICE.md](NOTICE.md)。
