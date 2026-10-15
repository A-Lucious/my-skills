# Blender MCP

Blender 提供结构、视角与光照指导，在第三步调用固定风格 Pixel Shader 并直出像素底稿，供第四步导入。优先使用已注册的 Blender Lab `blender` 工具。

## 连接与启动

先调用 `get_blendfile_summary_datablocks` 和 `get_objects_summary`，读取当前文件、场景、模式和选择。无合适专用工具时用 `execute_blender_code` 执行 bpy，将结果放入可 JSON 序列化的 `result`；检查 `isError`、数据 `status` 及嵌套 `result.status`。

先读取当前环境已注册的 Blender MCP 配置，核对服务器、插件与端口；不假定特定安装目录或自动启动状态。连接失败检查 Blender 进程、插件、Online Access 和实际配置端口。

GUI 使用当前环境的 Blender 可执行文件；使用 Blender Lab 插件且支持该命令时，后台桥接可按以下方式启动：

```bash
blender --background <file.blend> --command blender_mcp
```

交互与后台实例使用同一端口时只保留一个服务实例。工具未加载或需要独立诊断，在项目根运行：

```bash
tools/aseprite-mcp/.venv/bin/python .agents/skills/pixel-art/scripts/check_blender_mcp.py
```

脚本读取配置、列工具并查询场景，仅做连接检查。

## 场景与文件

先查看已有场景，在独立场景、文件或副本中工作，保留原稿与既有对象。Blender 文件参数使用绝对路径；目录及版本布局见[交付规范](../specs/production.md)。

为部件、材料设置稳定身份，保存相机矩阵、投影、光源、渲染引擎与尺寸。模型、姿态、相机或网格变化后更新受影响的指导数据。

## 指导通道与定义

第二阶段的必需指导包含本轮实际 RGB/alpha、部件/材质 ID、法线和深度。可导出渲染通道，也可通过 Blender MCP 在目标网格执行真实 `scene.ray_cast`，保存逐像素命中、身份、法线与距离；后者可用 JSON/NPZ 数组，记录网格原点、间距、相机和坐标定义。不能用对象清单、pass_index 或光源参数代替空间样本，也不能在 Blender 外按理想形状公式伪造采样结果。

| 信号 | 保存与解释 |
|---|---|
| RGB/alpha | PNG 供观看，记录颜色空间与背景 |
| 部件/材料身份 | 分类 ID 及映射，单独读取类别 |
| Normal | 原始浮点数据及法线坐标空间 |
| Depth | 距离定义、单位、背景值 |
| 基础色、直接/间接照明 | 区分材质和照明响应，记录颜色空间 |
| 高光、AO、遮挡/可见性 | 按需保存，明确每个信号的实现与意义 |

渲染通道的原始浮点信号保留 EXR；射线查询保留原始数值数组，逐项读取确认实际内容。指导清单记录源文件版本、通道/数组路径、尺寸、数据含义与有效样本，并区分“第三、四步实际使用”“仅保存”和“缺失”。必需指导缺失时第二阶段未完成；配置元数据不能标为“第三、四步实际使用的空间指导”。直接漫反射包含受光及材质响应，AO 表示局部环境遮蔽；独立光源 visibility 按采样方式定义。

目标网格可用 `scene.ray_cast` 在像素中心查询身份、世界位置、法线与射线距离；记录网格原点、像素间距和相机矩阵。世界法线与世界光源保持同一坐标系。具体遮挡近似与采样参数见[箱体案例](../references/cases/wooden-chest/case.md)。

## 第三步：风格 Pixel Shader 与底稿直出

必须通过真实 Blender MCP 直接加载 `styles/<style-id>/pixel_shader.py`，在 Blender 内生成原生像素 PNG。每个风格维护自己的固定脚本；Parchment Fantasy 的实现、输入和可执行调用见 [Pixel Shader](../styles/parchment-fantasy/PIXEL-SHADER.md)。脚本内的 bpy 节点和渲染通过真实 MCP 执行，外部脚本只编排调用，不读写像素来伪造 Shader 结果。

- **先确认实现。** 核对所选风格的脚本路径、版本、哈希与 Blender/引擎兼容性；使用该脚本实际提供的接口。缺失或不兼容时维护对应风格实现并先展示效果，不自动借用其他风格、下载同名插件或逐任务拼一套替代节点。
- **保留几何与光照依据。** 使用确认过的模型、相机、目标网格与光照；像素化材质/合成放在工作副本。原始法线、深度及身份指导与像素化色彩图分别保存，不把加工后的颜色当作原始空间信号。
- **风格算法固定。** Parchment Fantasy v1.3.0 先以源场景的显示转换实际输出光照输入，再按 Oklab 映射固定色板；不额外提亮或增强对比。默认原生 64×64，配套 4.3 色阶。任务输入可声明真实材质→允许色系，脚本在 Blender 内按实际射线命中生成掩码，限制对应区域选色，光影仍来自原渲染。用户未要求修改材质时保留原材质。算法变更升级版本并重新预览；模型、相机、灯光、帧或源显示设置变化时重渲染光照输入和身份掩码，不能复用旧视角图。
- **目标网格与尺寸。** 最终底稿必须是任务中的 W×H，放大图另存作预览。Parchment Fantasy 直接原生低分辨率渲染，`Pixelate` 的 Size 固定为 1；不能为了截图好看而用大画布马赛克冒充原生底稿。接口按实时节点 schema 组织。
- **色板与边缘。** 实际检查导出色值、alpha、孔洞与部件连接；Shader 技术通过不能代替形体检查。Aseprite 后续仍需按固定色系整理材料和像素簇。采样丢失识别点时修正模型/网格并重出。
- **先展示，再导入生产源稿。** 在 `Test Workspace/` 保存工作 `.blend`、原生底稿、同视角原始/像素化对照与 Shader 清单，向用户展示并记录 Q3。第四步复用该版底稿；输入或脚本变更时回到本环节。评审预览的 Aseprite 导入/放大仅用于展示，不等于生产粗稿完成。

## 已验证接口范围

Blender 5.2.2 的技术验证覆盖 MCP 建模、正交相机、面积光、Cycles、PNG/多层 EXR 导出及后台重新读取 `.blend`。接口以当前 bpy 和 tool schema 为准。

- 实测通道名称：`Depth`、`Normal`、`Object Index`、`Material Index`、`Diffuse Color`、`Diffuse Direct`、`Diffuse Indirect`、`Glossy Direct`、`Ambient Occlusion`。
- 该版本多层 EXR 先设 `image_settings.media_type = 'MULTI_LAYER_IMAGE'`，再设 `file_format = 'OPEN_EXR_MULTILAYER'`；PNG 预览设 `media_type = 'IMAGE'`、`file_format = 'PNG'`，完成后恢复输出格式。旧版本按实际属性处理。
- 该版本 compositor 接口为 `scene.compositing_node_group`。
