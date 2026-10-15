# 参考临摹与校准规范

用于用户要求的复刻、临摹或风格校准。研究稿标明来源，采用独立观察白名单与逐对象比较；原创配色采用生产色板。

临摹与校准按 [workflow](../../workflow.md) 和技能入口选择通道；Blender 通道执行六个阶段，第三步调用固定风格 Shader 并提前展示效果，除非用户提示明确要求省略指定阶段。下述观察、转录与比较是流程内的专项操作，不代替 Blender 形体、光照指导和提前展示 Shader 效果。

## 来源与范围

公开技能不携带第三方游戏截图或临摹结果。需要研究时使用当前任务提供且可使用的参照，将原文件和冻结清单保存在 `Test Workspace/<task-id>/`，记录来源、使用范围和 SHA-256。研究稿与原创案例分别标注，私人参照不进入公开仓库。

文字与个人信息不属于可公开的图像案例；纸框、装饰等观察对象需与叠字、账号和时间标记分开。新参照建立自己的对象清单和网格估计，重复实例按模板对象计数。

## 观察格与颜色

- 估计每个对象的格大小、簇、边界及原点。显示缩放和局部半格偏移按来源记录，不沿用其他截图的网格参数。
- 格内中部颜色中位数用于观察颜色，压缩/插值边缘单独记录。颜色合并保留材料与结构；避免全局 hue 合并抹掉梁柱、墙面和五官。
- 纸框分离纸面与叠字/图标，内部重建为空白，颜色比较仅使用可见外沿。退格、转角和边框厚度按本次参照观察。
- 默认候选从 Blender 像素底稿经 Aseprite MCP 导入后整理；用户原图的 import/crop 文件用于观察，不直接充当候选。用户明确要求从空白逐格转录时，才使用历史转录方式，并记录原话；这不自动授权省略建模或光照。保留实际像素修改的层与前后预览，观察白名单随迭代冻结。

## Manifest

[reference_study.py](../../scripts/reference_study.py)是历史从空白逐格转录方式的辅助工具，仅用户明确要求该方式时运行；默认第四步按 workflow 导入 Blender 像素底稿。比较工具和观察清单可继续使用，调用方法见 [Aseprite MCP](../../mcp/aseprite.md)。原图路径相对项目根，MCP 文件路径相对 `Test Workspace/`。

```json
{
  "reference": "Test Workspace/studies/<task>/reference.png",
  "reference_sha256": "<actual-sha256>",
  "grid_estimate": {"width": 180, "height": 320},
  "composition_grid_multiplier": 2,
  "background": "#c8c0ae",
  "assets": [{
    "id": "example-prop", "class": "prop", "rect": [7,296,22,23],
    "pixel_phase_screenshot": [0,0],
    "mask_policy": {"mode":"exterior-background", "background":[200,192,174], "threshold":8}
  }]
}
```

`rect` 是观察格 x/y/w/h；`pixel_phase_screenshot` 是原截图像素偏移。`instances:[[x,y],…]` 表示重复模板。mask 支持 opaque、saturation（threshold 0–1）、exterior-background（RGB 通道差）；flat-frame 配置 color、paper_tolerance、transparent_cells，负索引用于声明的退格角。掩码结果需目视核对近色材料、背景与压缩边缘。

严格转录可从 `merge-threshold=1` 开始，按来源误差调整。范围、阈值、mask 与格估计是研究参数，随来源记录；2×合成格及裁框是观察表示，不是官方原稿尺寸。

## 比较指标

用实际 MCP PNG 对照未改动来源及该轮冻结 manifest。严格转录的可选观察格门槛为：主体轮廓 IoU、主体 RGB 通道差≤3 的比例、内部相邻格颜色变化差≤6 的比例，逐对象三项各≥99%。背景不作全图加权；纸面排除叠字和图标，退格轮廓结合原图目视核对。

另报告原截图主体 RGB MAE 与严格颜色比例，并说明网格估计、掩码、缩放和压缩误差。观察格通过仅表示该清单的转录结果；原截图逐像素相似度与新题材原创能力分别评价。截图微差可能产生高色数/孤立点提示，作为研究误差解释。
