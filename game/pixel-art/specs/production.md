# 交付、检查与评审

## 文件与可编辑性

素材 ID 使用英文小写和连字符，版本用 `vNN`。制作期间保留已确认版本，修正在工作副本进行；同一源稿顺序修改。交付后清理不再需要的旧迭代、一次性作业、临时日志和备份，保留最终素材、可编辑源稿与必要预览。

| 位置（相对项目根） | 内容 |
|---|---|
| `Test Workspace/3d/<id>/<version>/` | `.blend`、原始指导及数据清单 |
| `Test Workspace/3d/<id>/<version>/pixel-base-vNN.png` | Blender 直出的原生像素底稿，供 Aseprite 导入及对照 |
| `Test Workspace/<task-id>/shader-manifest.json` | 第三步的风格 Shader 路径、版本/哈希、输入与预览评审状态；可与任务目录内 `.blend`、底稿及前后对照放在一起 |
| `Test Workspace/source/<id>-vNN.aseprite` | 可编辑像素源稿 |
| `Test Workspace/exports/` | 原生 PNG、动画图集及 JSON |
| `Test Workspace/previews/` | 阶段、对比与播放预览 |
| `Test Workspace/reports/` | 任务卡、作业、日志、检查及用户结论 |

按对象建立有用途的图层，保留分层源稿。场景可用 `sky/far/mid/ground/subject/fx`，角色可用 `shadow/body/gear/fx`。图层模式与透明度采用当前风格定义。

## 输出与技术检查

| 任务 | 交付 |
|---|---|
| 静态 | `.aseprite` + scale=1 PNG；透明或场景背景按设计 |
| 动画 | `.aseprite` + scale=1 spritesheet PNG + Aseprite JSON；另交播放 GIF 供观察 |

预览可用 4×/6×。固定格角色可选 horizontal/rows、padding=0；紧凑图集可用 packed、padding=1，并按 JSON frame rectangles 读取。

- 源稿：`get_sprite_info` 核对画布、图层、帧、时长与 tags；`assess_sprite` 查看色板覆盖和局部提示。
- PNG：检查尺寸、裁切、杂点和透明区域。原创输出运行[色板检查脚本](../scripts/check_palette.py)，按 [COMMON](../styles/COMMON.md)核对色阶、色系预算及 alpha；修正后重导出和检查。
- 动画：记录朝向、动作 tags、帧范围、时长及脚底/道具锚点。查看首/中/末帧与 GIF，用 `validate_loop` 检查循环、重复帧和停顿，按需用 `diff_sprites` 核对变化；检查 JSON 矩形边界、duration 与 tag 范围。循环停顿用时长表达。
- 临摹：按[研究规范](../styles/parchment-fantasy/REFERENCE-STUDY.md)进行来源、观察白名单和逐对象比对。

色板检查在项目根运行，传入任务卡中的用途、所选色系及全部生产 PNG。分类用于选择设计规范，`--asset-type` 使用当前色板定义的用途码；Parchment Fantasy 头像用 `portrait`、角色用 `battle_character`/`large_creature`、道具用 `prop`/`prop_icon`、符号用 `symbol`/`status`/`icon`，场景和建筑插图用 `scene`/`cover`，小建筑图标可用 `prop_icon`。

```bash
tools/aseprite-mcp/.venv/bin/python .agents/skills/pixel-art/scripts/check_palette.py \
  --style parchment-fantasy --asset-type portrait --families skin,earth,green \
  "Test Workspace/exports/portrait-v01.png"
```

只传 `--style` 时验证色板定义；省略 `--families` 的最小覆盖推断用于诊断，生产检查使用声明清单。

## 评审与状态

Q1 为 3D 形体、Q2 为光照指导、Q3 为第三步的风格 Pixel Shader 效果、Q4 为第四步像素粗稿、Q5 为第六阶段最终效果评审；第五阶段的内部细化检查不能当作 Q5。默认分阶段由用户确认；用户提示明确授权省略某阶段时，记录对应授权及省略状态。用户指定合并检查或一次试画时，仍完成全部未获省略授权的制作阶段及 Agent 自检，并按其方式评审；Shader 效果仍须在第四步制作之前展示。

逐项分开记录：阶段执行状态与产物、技术检查及结果、Agent 视觉自检（未检查/通过/需返工）、用户评审（待评审/通过/返工）。技术通过只说明所执行的技术项目合规，视觉自检不能代表用户验收；用户“通过”必须关联其明确确认的原话与预览版本，未确认保持待评审。沿用有效确认，修改后仅重开受影响的检查。

候选可先导出供评审；候选交付不等于用户验收或正式归档。未解决的问题随候选列出，不声明“全项通过”或“完全满足需求”。评审前保留本次判断所依赖的指导与对照证据；用户明确要求提前清理时记录已清理的证据范围。评审结束后按文件规范清理过程文件，保留最终源稿、必要预览和简要结论。

## 任务卡与续做记录

在 `Test Workspace/reports/<id>.md` 维护一份记录，条件字段按任务填写。流程、3D、光照及阶段产物记录不可因素材类别而省略；阶段被用户明确授权省略时，引用提示原文并记录范围，不得仅填 `N/A` 或“平涂符号”：

```markdown
# <asset-id>
需求：原创/临摹；分类与用途；style-id；交付目标；允许简化
流程：六个阶段的执行/复用/省略状态与证据路径；省略阶段及用户提示原文（未授权时写“无阶段省略授权”）
尺寸：原生 W×H；显示容器与比例；留白、裁框与锚点
参考：来源、原图/局部路径；实际观察到的形体与材料特点
配色：版本、用途上限、所选色系、材质→色系；研究稿记观察白名单
光照：主光/环境/额外光；主要遮挡物→受影面；渲染预览与原始指导数据路径；或用户明确授权省略的原话
3D：版本、.blend 路径、引擎、相机/网格、部件/材质 ID；通道定义与实际使用项；或用户明确授权省略的原话
结构基准：主要比例、部件锚点、连接轴线或设计偏置、孔洞及关键识别点；相应目标网格与版本
像素：源稿版本、层/帧；本轮问题、开放区与保护区
像素底稿：Blender PNG 路径与实际 W×H；shader/节点方案、引擎与色彩管理；Aseprite 导入源及工作层；或用户明确指定其他粗稿方式的原话
Shader：style-id、styles/<style-id>/pixel_shader.py、脚本版本/哈希、色板版本/哈希；输入尺寸/色系/用途、相机与渲染参数；原生/整数放大/着色前后预览路径；Q3 用户状态与确认原话
转译对照：3D 指导/Blender 像素底稿/Aseprite 粗稿对照路径；逐项保持、有意调整及其依据、未解决问题；实际使用的数据字段
纹理：材料/面、方向、疏密、种子/算法版本、覆盖率定义
检查：技术项目与结果；Agent 视觉自检及具体依据；Q1、Q2、Q3、Q4、Q5 的预览版本、用户状态与确认原话；剩余问题
产物：源稿、导出、预览、作业/日志；当前阶段与验收/接入状态
续做：保留关系、剩余问题、下一步
```

## 游戏接入

任务包含接入时，检查已验收预览和源文件，再将 PNG/图集及所需 JSON 原样复制到 `game/packages/<pack-id>/images/`，按既有包格式更新引用。延续项目的 nearest、关闭 mipmaps 和 lossless 设置；在真实窗口核对 keep-aspect 容器下的比例、留白与清晰度。Parchment Fantasy 复杂道具默认保留 64×64 原生文件，由节点按显示容器缩放；优先整数倍放大（如 128×128、256×256），无需为缩放改成 SVG。非整数缩放和缩小须在实际容器中检查像素格与细节，不以大预览代替显示检查。
