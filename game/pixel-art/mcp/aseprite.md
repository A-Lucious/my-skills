# Aseprite MCP

优先调用已连接的 `aseprite` 工具；未加载时用 [mcp_client.py](../scripts/mcp_client.py)连接同一项目服务器。以下命令以技能已复制到项目 `.agents/skills/pixel-art/` 为例，在项目根执行。若技能放在其他位置，替换命令中的技能路径并设置 `PIXEL_PROJECT_ROOT` 为目标项目绝对路径；安装器会将该路径写入项目 MCP 配置。

## 启动与诊断

开始作业先 `health_check`，确认 `ok=true` 和工作区为项目 `Test Workspace/`。若当前已连接服务仍使用旧目录，改用下述 `mcp_client.py` 启动新连接，确认工作区正确后再写入；不得在旧目录继续制作。连接或执行异常时运行：

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py doctor
```

`doctor` 建立真实 MCP session，检查 health、Lua 与临时源稿/PNG 导出。安装和项目路径迁移分别使用：

```bash
python3 .agents/skills/pixel-art/scripts/install_mcp.py
python3 .agents/skills/pixel-art/scripts/install_mcp.py --configure-only
```

安装从 技能内的 `mcp/aseprite-mcp.lock.json` 恢复固定提交并执行 `uv sync --locked`；已有 clone 提交不符时退出。升级需显式更新 lock 并验证。`--configure-only` 只更新项目配置。

[start_mcp.sh](../scripts/start_mcp.sh)启动 stdio 服务，stdout 专供协议；自动定位项目虚拟环境与本机 Aseprite。自定义安装位置在 `.codex/config.toml` 的 `[mcp_servers.aseprite.env]` 设置 `ASEPRITE_PATH` 为可执行文件路径。项目受信任并重载 MCP 后读取注册；上游工具说明位于 `tools/aseprite-mcp/docs/TOOLS.md`。

## Schema 与写入约定

按实时 schema 组织参数与批处理支持项：

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py tools
python3 .agents/skills/pixel-art/scripts/mcp_client.py tools draw_pixel_map
python3 .agents/skills/pixel-art/scripts/mcp_client.py tools apply_operations
```

- 文件参数相对 `Test Workspace/`，例如 `source/<id>-v01.aseprite`；路径不含绝对路径、`Test Workspace/` 前缀或 `..`。
- 坐标从 0 起，帧与数字层索引从 1 起；每次写像素明确 `layer` 和 `frame`。
- `draw_pixel_map` 的 rows 等长，每字一像素，`.` 保留原像素。擦除使用 `clear_layer` 或选择范围工具；全透明 map 是 no-op，跳过。现有版本单次上限 65,536 个实际绘制像素，大图可拆水平带并保留 y 偏移。
  **重绘已有源稿前必须先 `clear_layer`（或 `create_sprite --overwrite` 重建）**：`.` 是"保持原像素"而不是擦除，反复重绘会在新形状之外留下上一版的像素，且工具仍报 `ok`。症状是 `assess_sprite` 的 `drawn_pixels` 大于像素图里非 `.` 字符数，多出来的颜色不属于当前 legend。已实测：32×32 齿轮重绘后残留 64 个旧像素。
- `apply_operations` 的单项为 `{"op":"add_layer","args":{"name":"subject"}}`，先 `dry_run=true`。`draw_pixel_map` 独立调用。
- `set_palette` 现有版本最多 256 色；RGB 临摹的完整观察白名单另存。
- `shade_region_by_light`、`shift_along_ramp`、`outline_smart` 使用单个材料的有序 ramp。近似着色明确区域、`base_color` 与小 `tolerance`，遮挡关系另行检查。`assess_sprite` 可用素材完整色集检查覆盖，明度顺序提示按材料解释。
- 插帧/复制后读取 `newFrame`、`renumbered_from` 并更新后续帧编号。

## 单次调用与预览

第四步直接导入第三步已确认的原生 PNG 作为底稿，再在 Aseprite 中修改为粗稿。以下相对路径均位于 `Test Workspace/`；`input_image` 使用第三步 `shader-manifest.json` 中 `outputs.pixel` 对应的实际文件。通过 `get_sprite_info` 核对尺寸及实际图层，保留未修改的底稿参考层，复制为粗稿工作层后，通过 Aseprite MCP 整理材料颜色、轮廓、关键识别点和大明暗；保存修改后源稿及底稿/粗稿对照。导入成功仅完成底稿准备，粗稿完成还须有实际像素修改和检查记录。

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py call import_image \
  '{"input_image":"<task-id>/shader-v01/pixel-base-v01.png","output":"source/<id>-v01.aseprite"}'
```

调色使用任务声明的固定色系。需要整体映射时，可先 `set_palette` 指定选定颜色，再 `set_color_mode` 使用 `palette_source="keep"`、`dithering="none"` 转为 indexed，必要时转回 RGB 后细化；映射前后核对材料分区、alpha 和孔洞。`quantize_palette` 从图像推导颜色，不能代替锁定的生产色板。颜色混淆时按部件/材质区域通过 MCP 局部修正。

下面的 `create_sprite`/`draw_pixel_map` 示例用于局部绘制或用户明确指定的其他粗稿方式，不作为绕过底稿导入的默认入口：

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py call create_sprite \
  '{"filename":"source/torch-v01.aseprite","width":32,"height":48}'
python3 .agents/skills/pixel-art/scripts/mcp_client.py call draw_pixel_map \
  --args-file "Test Workspace/reports/torch-pixel-map.args.json"
python3 .agents/skills/pixel-art/scripts/mcp_client.py call render_preview \
  '{"filename":"source/torch-v01.aseprite","frame":1,"scale":6,"views":["color","value","silhouette","actual"]}' \
  --save-image previews/torch-review.png
```

参数文件为 JSON object，复杂参数优先用文件。像素 map 示例：

```json
{
  "filename": "source/torch-v01.aseprite",
  "rows": ["..aa..", ".abba.", "abccba", ".abba.", "..aa.."],
  "legend": {"a":"#6d2e2a", "b":"#d5702f", "c":"#f4d886"},
  "x": 13, "y": 5, "layer": "Layer 1", "frame": 1
}
```

`--save-image` 原样保存服务器返回 PNG 到 `Test Workspace/previews/`，随后用 `view_image` 查看。

## 顺序作业与续跑

作业文件使用 `tool/arguments`，与 `apply_operations` 的 `op/args` 分开：

```json
{
  "steps": [
    {"tool":"health_check", "arguments":{}, "expect":{"ok":true}},
    {"tool":"import_image", "arguments":{"input_image":"3d/demo/v01/pixel-base-v01.png","output":"source/demo-v01.aseprite"}},
    {"tool":"render_preview", "arguments":{"filename":"source/demo-v01.aseprite","scale":6}, "save_image":"previews/demo-structure.png"}
  ]
}
```

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py run "Test Workspace/reports/demo.job.json" \
  --log-name demo.mcp-log.json
```

客户端先校验 schema，逐项 `tools/call`，首个失败后停止；日志存 `Test Workspace/reports/`。`expect` 支持嵌套字段，字段取自实际结果。作业非事务，部分修改可能已生效。

失败或中断后先读日志、`get_sprite_info` 和实际预览，确认源稿状态，再仅续跑未完成步骤。需要事务时使用 `apply_operations` 的支持操作。`extract_palette` 超过 `max_colors` 表示精确颜色过多，可诊断来源或压缩微差。

## 辅助脚本

| 脚本 | 使用时机 |
|---|---|
| [prepare_reference_crops.py](../scripts/prepare_reference_crops.py) | 传入 `--manifest` 裁切清单与 `--task-id`，原图复制进工作区，经 `import_image → crop_sprite → export_png` 制作局部参考；不写入公开技能库；重建可传 `--overwrite` |
| [make_style_sample.py](../scripts/make_style_sample.py) | 重建已有四帧提灯演示，生成作业并交 MCP 执行；样例使用其历史配色，重建可传 `--overwrite` |
| [reference_study.py](../scripts/reference_study.py) | 历史严格转录工具，读取来源与 manifest 后从空白生成作业；仅用户明确要求此转录方式时使用，不能替代默认 Blender 底稿导入 |
| [compare_reference_study.py](../scripts/compare_reference_study.py) | 比较实际 MCP 导出与该轮冻结参照，输出逐对象报告 |

临摹工具示例，manifest 定义见[研究规范](../styles/parchment-fantasy/REFERENCE-STUDY.md)：

```bash
python3 .agents/skills/pixel-art/scripts/reference_study.py \
  --manifest <manifest.json> --iteration <new-id> --merge-threshold 1
python3 .agents/skills/pixel-art/scripts/mcp_client.py run \
  "Test Workspace/reports/reference-<new-id>-structure.job.json" --log-name reference-<new-id>-structure.mcp-log.json
python3 .agents/skills/pixel-art/scripts/compare_reference_study.py --iteration <new-id>
```

研究作业按[制作流程](../workflow.md)分阶段执行；这里的 `structure/light/export` 作业属于像素阶段，不能代替前两阶段的 Blender 建模与光照渲染，默认须先完成它们，除非用户提示明确授权省略。比对在导出后运行。`--assets` 用于局部诊断，`--candidate-dir` 可指定当前任务的候选 PNG 目录；每轮使用新 ID 保存证据。
