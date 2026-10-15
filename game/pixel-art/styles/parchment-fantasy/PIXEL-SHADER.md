# Parchment Fantasy Pixel Shader

固定实现：[pixel_shader.py](pixel_shader.py)，版本 `1.3.0`，配套 [Parchment Fantasy 4.3 色板](palette.json)。这是 Blender 内的屏幕空间合成着色脚本，不依赖同名第三方插件。通过 Blender MCP 加载，不在外部 Python 中处理渲染像素。

## 效果与输入

流程：当前活动相机的真实渲染 → 原生 W×H 网格 → 在 Blender 中以源场景的 AgX/Look/曝光输出 16-bit PNG → Blender 合成节点按实际显示颜色映射固定色板 → 0/255 alpha。保留模型、原材质、玻璃透射、光源和源引擎；创建独立工作场景，不修改上游源场景。当前实现经 Blender 5.2.2 LTS / Cycles、sRGB 显示实测；代码使用 Blender 5.x 合成 API，其他版本/引擎先实际验证。

固定规则：源显示颜色先还原为显示线性 RGB，经真实合成节点转换到 Oklab，距离为 `2×ΔL²+Δa²+Δb²`，兼顾感知亮度与色彩；没有额外平方根提亮或对比增强。原生渲染 filter=0.01，Pixelate Size=1，alpha>0.5。源场景的 AgX/Look/曝光在 `lighting-native.png` 中先实际生效；最终 Standard/None、曝光 0、gamma 1、dither 0 仅编码色板，不重复施加源色调转换。Oklab 算法依据见[作者实现](https://bottosson.github.io/posts/oklab/)。这些规则按脚本版本固定。

1.1.0 的 HSV V 是 RGB 最大通道，并不等于实际亮度；再对它提亮并强偏色相，会夸大阴影边界。旧版还将 AgX 原图与 Standard 输出直接比较，不能据此声称保留了原始光照。1.2.0 修复这一点；需实际对照灰度及瓶身代表点，不能仅以色板检查通过判断光影一致。

尺寸默认 `size=(64,64)`，任务可明确提供其他 `(W,H)`；每次声明 `families` 和 `asset_type`。颜色仅取当前锁定色板对应色系，按用途检查色系数量上限。4.3 的 earth 18 阶、blue 16 阶、ruby 40 阶（含玻璃覆盖下的低饱和色、红色着色玻璃的深红与反光），其余立体材质各 12 阶，保留全部旧色值。

1.3.0 可通过 `material_families` 给实际 Blender 材质声明允许色系。脚本在原生像素中心执行真实 `scene.ray_cast`，生成身份掩码；合成节点仅在对应区域按允许色系选色，防止木塞暗面被选成药液红灰或瓶口蓝灰。光影仍来自实际渲染，不使用身份掩码重算光照。未声明的材质继续使用任务所选的全部色系。材质混色时先核对输入和分区，不能用改灯或增加对比掩盖映射错误。

身份掩码识别第一命中的表面；透明玻璃的允许色系须包含其内部透射颜色。当前通过正交相机药水实测，不能把第一表面身份解释成完整的透射路径分解。几何法线与射线距离用于身份/结构核对，不代替 Cycles 的平滑着色法线、反射和透射求解。

脚本使用活动相机；自由视窗先经 MCP 对齐工作相机并保存其矩阵。已有合成器的源场景当前会拒绝覆盖，应先核对其用途再维护兼容路线。原生透明边缘采用固定阈值，玻璃外轮廓仍需查看，半透明特效须另行维护适用实现。

## Blender MCP 直接调用

将下列代码作为 `execute_blender_code` 的 `code`。无运行实例时可使用 `execute_blender_code_for_cli`，`blend_file` 指向本次已确认的 `.blend`，代码相同。将 `<skill-root>` 和 `<project-root>` 替换为当前技能和项目的实际绝对路径，任务输出目录每版独立；已有输出拒绝覆盖。

```python
from pathlib import Path
import bpy

shader = Path("<skill-root>/styles/parchment-fantasy/pixel_shader.py")
namespace = {"__file__": str(shader), "__name__": "parchment_pixel_shader"}
exec(compile(shader.read_text(), str(shader), "exec"), namespace)
result = namespace["render_preview"](
    bpy.context.scene,
    output_dir="<project-root>/Test Workspace/<task-id>/shader-v01",
    size=(64, 64),
    families=["ruby", "earth", "blue"],
    asset_type="prop_icon",
    # 可选：仅在实际查询确认这些材质存在且用途匹配时提供。
    material_families={
        "Mat_Cork": ["earth"],
        "Mat_Tie": ["earth"],
        "Mat_NeckGlass": ["blue"],
        "Mat_Glass": ["ruby"],
        "Mat_Liquid": ["ruby"],
    },
)
```

`render_preview` 在 Blender 内输出：同相机平滑渲染 `before-smooth.png`、同尺寸原始对照 `before-native.png`、经源显示转换的 16-bit 光照输入 `lighting-native.png`、原生底稿 `pixel-base-v01.png`、保留原场景和节点的 `shader-preview.blend`、含脚本/色板哈希与输入的 `shader-manifest.json`。默认对照为 4× 尺寸，原生底稿仍是 W×H。光照输入图打包进 `.blend`，源显示转换只生效一次。

加载模块本身不修改场景；`create_pixel_scene` 需传入实际烘焙的同尺寸 `lighting_image`。当前工作场景中的 Image 节点对应所记录的相机、帧、灯光与模型；这些输入变化后必须重新执行光照渲染及映射，不能直接改场景后用旧的静态输入图冒充新视角效果。动画逐帧通过 MCP 重新烘焙。

声明材质分区时，额外保存 `surface-guidance.json`（实际命中对象、材质、世界位置、几何法线、射线距离）与 `material-mask-N.png`；掩码同样打包进 `.blend`。检查材质区的实际导出颜色是否全部属于其声明色系。材质名称和通用色系表须取自本次源文件，不把示例名字硬套到别的对象。

通过 Aseprite MCP 导入预览图并以 nearest 整数倍展示，保留真实底稿字节。实际查看当前效果并先向用户展示，Q3 未确认时保持“待评审”；第四步使用该版原生底稿，不另做替代粗稿。

## 技术基准

Shader `1.3.0` / 色板 `4.3` 的基准来自自制的[药水瓶底稿](../../references/cases/health-potion/case.md)，原生 `64×64`，实际 25 色，材质分区违规像素为 0。底稿保留真实显示光影，并按实际材质分区选色。

该例只覆盖第三步 Shader，不代表已完成 Aseprite 粗稿、精修和最终交付；新对象仍须生成、展示并评审本次效果。案例文件仅包含自制道具，不包含第三方游戏素材。
