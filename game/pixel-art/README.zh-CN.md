# Pixel Art

[English](README.md) | **简体中文**

通过 **Blender MCP + Aseprite MCP**，将素材需求转化为可编辑、可导出的像素美术。适用于道具与装备、角色与生物、场景与建筑、界面装饰及精灵动画。

技能将风格、配色、形体、光照和像素精修串成完整流程：先检查结构与视觉效果，再整理像素簇、材质和动画，最终交付原生 PNG、动画图集及可编辑的 Aseprite 源稿。

默认风格为 **羊皮纸奇幻（Parchment Fantasy）**，风格 ID 为 `parchment-fantasy`，也可按任务扩展独立风格。

## 制作流程

先确定对象、用途、尺寸和风格。Blender 提供形体与光照依据，Aseprite 完成像素整理、细化和正式导出。

```mermaid
flowchart LR
    A["3D 建模<br/>与相机"] --> B["光照<br/>与渲染"]
    B --> C["Pixel Shader<br/>效果预览"]
    C --> D["Aseprite<br/>像素粗稿"]
    D --> E["像素精修<br/>纹理与动画"]
    E --> F["效果检查<br/>与交付"]
```

各阶段展示实际预览并记录评审，Shader 效果在进入像素粗稿前展示。

人物画像先由[设计卡](cards/portraits/design.md)选择输入路线。用户明确说明上传图来自生图模型，或需要生图时，选定的二维图先经过[平滑人物 Pixel Shader](styles/parchment-fantasy/PORTRAIT-PIXEL-SHADER.md)，再进入 Aseprite 精修眼睛和表情。已有 AI 图够用时无需重新生成，普通参考图不自动触发生图模型调用。

## Tips

1. 请确保 Agent 环境已安装并接入 **Blender MCP** 和 **Aseprite MCP**。
2. 该技能的上下文较长，请确保 Agent 有足够的上下文容量来承载技能说明及当前任务。
3. 当前内置一种风格 `parchment-fantasy`。可调用技能内置的 [create-style](commands/create-style.md)，通过问答扩展独立风格，例如：`使用 $pixel-art create-style，帮我创建一个新风格。`

## 案例

### 道具、动画与材质案例

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

### 人物画像案例

<table>
  <tr>
    <td align="center" valign="middle">
      <img src="references/cases/portrait-smoothing-baseline/preview.png" alt="平滑 Shader 效果基准" width="180"><br/>
      <b>平滑 Shader 效果基准</b><br/>
      <sub>用户认可的平滑色块与观感基准</sub>
    </td>
    <td align="center" valign="middle">
      <img src="references/cases/cloaked-youth/preview.png" alt="兜帽青年画像" width="180"><br/>
      <b>兜帽青年</b><br/>
      <sub>头颈大占比特写构图（免精修）</sub>
    </td>
  </tr>
  <tr>
    <td align="center" valign="middle">
      <img src="references/cases/giant-goblin/preview.png" alt="巨型地精画像" width="180"><br/>
      <b>巨型地精</b><br/>
      <sub>宽颌厚颈与异质五官像素底稿</sub>
    </td>
    <td align="center" valign="middle">
      <img src="references/cases/ranger-failed-baseline/preview.png" alt="游侠失败基线案例" width="180"><br/>
      <b>游侠（失败基线案例）</b><br/>
      <sub>“无参考照片，无生图”下使用 Blender 建模的失败案例</sub>
    </td>
  </tr>
</table>

- [平滑 Shader 效果基准](references/cases/portrait-smoothing-baseline/case.md)：生图来源路线进入 Aseprite 之前的方向性平滑（Anisotropic Kuwahara）与 Oklab 色板映射基准，色块高度归并，光影层次明晰。
- [兜帽青年（头颈大占比特写）](references/cases/cloaked-youth/case.md)：原生 64×64，验证了特写构图规范（头部与颈部占据主要画面，底部仅保留少许斗篷领口，免躯干服饰挤占面部像素预算），比例已获认可。
- [巨型地精 / 哥布林](references/cases/giant-goblin/case.md)：原生 64×64，非人生物与怪物画像底稿，验证了宽颌、厚颈、尖耳与獠牙等特征的像素化与 Shader 处理。
- [骷髅画像（生图来源路线）](references/cases/skeleton-portrait-image-gen/case.md)：原生 64×64，验证了全身参考图转头颈特写、生图触发词分支与专属平滑 Shader 处理流程。
- [游侠（失败基线案例）](references/cases/ranger-failed-baseline/case.md)：**“无参考照片，无生图”下使用 Blender 建模的失败案例**。作为反面教材归档保留：由于在无真实参考下手工盲目建 3D 头部模型，导致面部骨骼体块僵硬、表情木讷疲惫；且半身像构图中服饰占据过多面积，严重挤占了五官神态的像素表现空间。确立了后续人物画像必须以“人脸特写构图”和“具备可靠造型来源”的约束规范。
- [人物画像生成说明与三次骷髅基线对比](docs/portrait-generation.md)：人物画像特写构图、3D 与 2D 生图双分支决策，以及三次骷髅画像基线对比深度指南。

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

[SKILL.md](SKILL.md) 是技能入口，负责风格与分类的选择；[workflow.md](workflow.md) 说明各阶段的执行与评审方式。

| 目录 | 内容 |
|---|---|
| `cards/` | 物品、人物画像、通用物理材质及特性扩展的模块化注入模板 |
| `styles/` | 通用规则、风格定义、固定色板与 Pixel Shader |
| `specs/` | 点阵基础规范、光照、纹理及交付规范 |
| `mcp/` | Blender 与 Aseprite 接入说明、固定版本清单 |
| `scripts/` | MCP 调用编排、诊断与只读技术检查 |
| `examples/` | 展示素材及其可编辑源稿、图集和帧数据 |
| `references/cases/` | 自制技术案例、适用范围与限制 |
| `asset-library/` | 跨风格素材来源网址、作者、协议记录与按需取用说明 |

## 通用基础素材

[素材来源索引](asset-library/README.zh-CN.md)只保存跨风格的来源网址、作者、协议和校验信息。先在[作者网站](asset-library/INDEX.md)浏览预览，需要时才下载选中的文件到项目工作区，遵守 50 MiB 缓存预算。多数来源为 CC0；Game-icons 以 CC BY 3.0 为主，使用时保留对应作者署名，详见[第三方协议说明](asset-library/THIRD_PARTY_LICENSES.md)。选中的工作副本通过 Aseprite MCP 改造为目标风格。

羊皮纸奇幻的历史视觉研究参考过 **Life in Adventure**，本技能与该游戏及其权利人无官方关联。公开包不附带该游戏的截图、裁切图、提取素材或临摹稿；来源与权属说明见 [NOTICE.md](NOTICE.md)。
