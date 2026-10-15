---
name: pixel-art
description: "制作、修改和导出像素素材与精灵动画。按分类和风格规范，以 Blender MCP 建模、打光，调用风格目录中的固定 Pixel Shader 并提前展示效果，再经 Aseprite MCP 导入、精修和导出。"
---

# Pixel Art

从用户需求确定对象、用途和交付目标，将风格与分类规范组成任务输入，再执行制作流程。用户明确指定的风格、简化和评审方式优先于默认值。

## 1. 风格与内容规范

先读 [通用规范](styles/COMMON.md)。默认风格为 `parchment-fantasy`，读取其 [STYLE.md](styles/parchment-fantasy/STYLE.md)、[palette.json](styles/parchment-fantasy/palette.json) 和[参考使用规则](styles/parchment-fantasy/reference-library/INDEX.md)。需要图像参照时，从当前任务提供且可使用的素材中选择，公开包不附第三方游戏图像。其他风格从[风格库](styles/index.md)选择。

按任务读取对应分类；复合素材以主要对象为入口，再补相关分类：

| 用户任务 | 分类规范 |
|---|---|
| 头像、全身角色、生物 | [人物画像](specs/characters.md) |
| 事件插图、环境、战斗画面 | [场景](specs/scenes.md) |
| 道具、装备、图标、纸框、装饰 | [物品](specs/props.md) |
| 房屋、遗迹、独立建筑 | [建筑](specs/buildings.md) |

所有任务读取[光照规范](specs/lighting.md)，需要表面纹理时补读[纹理规范](specs/texture.md)。所有任务按[交付规范](specs/production.md)建立任务卡；用户要求临摹或校准时，另读[参考研究规范](styles/parchment-fantasy/REFERENCE-STUDY.md)。

## 2. 制作流程

### 资产类型通道划分（工作流分流）

不要对所有素材搞“一刀切”，按资产特性划分通道：

- **A 轨（硬表面与空间资产）：** 建筑、机械、箱体、空间道具。继续严格走 3D 建模 → 真实射线/光照 → 底稿精修，充分利用 3D 的透视红利。
- **B 轨（有机与装饰类 UI 资产）：** 卷轴、羊皮纸框、丝带、植物花环、平面图标。这类素材的核心魅力在于“手绘夸张感”与“造型韵律”，允许两种执行策略：
  - **策略 1（纯 2D 手绘起稿通道）：** 允许直接在 Aseprite 中以 2D 剪影起稿（Silhouette Blockout），用经典的 2D 像素大色块切出非对称撕边、卷筒厚度和手绘弧度，直接规避 3D 的呆板。
  - **策略 2（若必须走 3D，必须是有机雕刻/曲面 3D）：** 禁止使用死板的立方体拼凑。

### 执行规则

创建、修改或导出素材时，A 轨或选择 B 轨策略 2 时必须依次执行 [workflow.md](workflow.md) 的六个阶段：**1：3D 与相机 → 2：光照渲染 → 3：风格 Pixel Shader 与效果预览 → 4：Aseprite 像素粗稿 → 5：像素簇、细节与纹理 → 6：最终效果检查**。B 轨选择策略 1 时，在任务卡注明采用纯 2D 手绘起稿通道，直接进入第四步的 Aseprite 剪影起稿，保留实际产物与检查记录。

Pixel Shader 按风格固定为 `styles/<style-id>/pixel_shader.py`，通过 Blender MCP 在 Blender 内直接加载执行；不逐任务另写算法，也不跨风格套用。Parchment Fantasy 实现与调用见 [Pixel Shader](styles/parchment-fantasy/PIXEL-SHADER.md)。先展示当前已确认视角下的 Shader 效果，完成该环节评审后再进入第四步。

羊皮纸奇幻当前技术基准为 Shader `1.3.0`、色板 `4.3`、原生 `64×64`：保留真实显示光影，支持实际材质到色系的分区，防止瓶口等部件串色。基准参数与阶段范围见 [Shader 基准](styles/parchment-fantasy/PIXEL-SHADER.md#技术基准)；新对象仍按第三步生成并展示本次效果。

仅当用户提示明确说明不需要某个阶段时，才可额外省略该阶段，并在任务卡引用用户原话、标明省略范围。除 B 轨明确策略外，不可擅自省略 3D 或光照。用户指定合并评审或一次试画只改变评审方式，不授权省略制作阶段。

阶段完成以实际产物、上游对照和视觉自检为依据，不能只凭文件存在或工具返回成功。A 轨 3D 指导须包含实际空间数据；第三步生成并展示 Blender 像素结果，第四步直接将第三步已确认的同一版原生 PNG 经 Aseprite MCP 导入作为底稿，再在 Aseprite 中修改底稿，形成像素粗稿。保留导入底稿与修改后粗稿的对照，单纯导入或另存不算粗稿制作完成。技术检查、Agent 视觉自检与用户验收分别记录，Agent 不得代填用户“通过”。

## 3. MCP 操作

- [Blender MCP](mcp/blender.md)：3D 草稿、相机、照明、指导数据及像素底稿直出。
- [Aseprite MCP](mcp/aseprite.md)：底稿导入，以及其后的像素创建、修改、缩放、调色、合成与正式导出，工作区为项目 `Test Workspace/`。
- 脚本负责数据/JSON 编排、只读分析、原字节保存与复制；像素写入和导出由真实 MCP 调用完成。

所有生成物（含 Blender 文件、任务卡、临时脚本、调用日志、阶段预览与备份）集中放在 `Test Workspace/`，按任务组织。技能参考库默认只读；仅用户明确要求维护参考库时写入。交付后清理不再需要的临时文件、旧迭代和备份，保留最终素材、可编辑源稿与必要预览；游戏接入按用户任务另行执行。

`references/` 保存自制技术案例：[木箱纹理](references/cases/wooden-chest/case.md)与[药水瓶 Shader 底稿](references/cases/health-potion/case.md)。第三方图像与其临摹稿不随技能分发；来源说明见 [NOTICE.md](NOTICE.md)。分类规范提供设计要点，具体尺寸、采样和纹理参数以本次任务及对应案例为依据。

## 4. 公开分发

公开案例只保留任务所需的技术信息与相对路径，不包含个人身份、账号、姓名、联系方式、本机绝对路径、生成日期、验收日期或私人对话原文。日期形种子不作为公开参数展示；技术版本号、动画时长可正常保留。本地任务卡可保留制作记录，发布案例时另行脱敏，不把日志和缓存打包。风格来源及第三方素材边界见 [NOTICE.md](NOTICE.md)。
