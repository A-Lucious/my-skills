# Aseprite MCP

Prioritize invoking the connected `aseprite` tool; when not loaded, use [mcp_client.py](../scripts/mcp_client.py) to connect to the same project server. The commands below assume the skill is copied to the project's `.agents/skills/pixel-art/` and executed from the project root. If located elsewhere, substitute the skill path and set `PIXEL_PROJECT_ROOT` to the absolute path of the target project; the installer writes this path into project MCP configurations.

## Startup and Diagnostics

Begin tasks with `health_check`, confirming `ok=true` and that the workspace is set to project `Test Workspace/`. If the currently connected server still targets an old directory, launch a new connection with `mcp_client.py` as shown below, verify the correct workspace, and only then proceed with writes; do not continue production in an outdated directory. For connection or execution issues, run:

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py doctor
```

`doctor` establishes a live MCP session, checking health, Lua functionality, and temporary source/PNG exports. For installation and project path migration, use:

```bash
python3 .agents/skills/pixel-art/scripts/install_mcp.py
python3 .agents/skills/pixel-art/scripts/install_mcp.py --configure-only
```

Installation restores the pinned commit from `mcp/aseprite-mcp.lock.json` within the skill and runs `uv sync --locked`; it aborts if an existing clone commit mismatches. Upgrades require explicitly updating the lock and verifying. `--configure-only` updates project configuration only.

[start_mcp.sh](../scripts/start_mcp.sh) launches the stdio server, keeping stdout reserved exclusively for protocol messages; it automatically locates the project virtual environment and local Aseprite executable. For custom installations, set `ASEPRITE_PATH` under `[mcp_servers.aseprite.env]` in `.codex/config.toml`. Server registration is read once the project is trusted and MCP is reloaded; upstream tool documentation is at `tools/aseprite-mcp/docs/TOOLS.md`.

## Schema and Writing Conventions

Structure arguments and batch operations according to live schemas:

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py tools
python3 .agents/skills/pixel-art/scripts/mcp_client.py tools draw_pixel_map
python3 .agents/skills/pixel-art/scripts/mcp_client.py tools apply_operations
```

- File paths are relative to `Test Workspace/`, e.g., `source/<id>-v01.aseprite`; paths must not include absolute paths, `Test Workspace/` prefixes, or `..`.
- Coordinates start at 0; frames and numeric layer indices start at 1. Explicitly designate `layer` and `frame` on every pixel write.
- `draw_pixel_map` rows must be equal in length, one character per pixel; `.` preserves the underlying pixel. Use `clear_layer` or selection tools for erasing; all-transparent maps are no-ops and should be skipped. The current version caps single calls at 65,536 drawn pixels; large sprites can be split into horizontal strips retaining the y offset.
  **Always `clear_layer` (or recreate with `create_sprite --overwrite`) before redrawing an existing source**: `.` preserves original pixels rather than clearing them. Successive repainting without clearing leaves leftover pixels outside new shapes while the tool still returns `ok`. The symptom is `drawn_pixels` in `assess_sprite` exceeding non-`.` characters in the map, with extraneous colors outside the legend. Verified test: a 32x32 gear repainted without clearing retained 64 obsolete pixels.
- `apply_operations` items take the form `{"op":"add_layer","args":{"name":"subject"}}`; test with `dry_run=true` first. Call `draw_pixel_map` independently.
- `set_palette` currently supports up to 256 colors; full observation whitelists for RGB tracing should be stored separately.
- `shade_region_by_light`, `shift_along_ramp`, and `outline_smart` operate on ordered ramps for a single material. For approximate shading, specify clear regions, `base_color`, and a small `tolerance`; check occlusion independently. `assess_sprite` verifies coverage against complete palette sets, and lightness order hints must be interpreted per material.
- Read `newFrame` and `renumbered_from` after frame insertion/duplication, updating subsequent frame indices accordingly.

## Single Calls and Previews

Phase 4 imports the confirmed Phase 3 native PNG directly as a base, then modifies it into a rough draft in Aseprite. Relative paths below are within `Test Workspace/`; `input_image` uses the actual file corresponding to `outputs.pixel` in Phase 3's `shader-manifest.json`. Verify dimensions and actual layers with `get_sprite_info`. Retain the untouched base as a reference layer, duplicate it into an active draft layer, and refine material colors, silhouettes, key landmarks, and major value masses via Aseprite MCP. Save the modified source along with base-to-draft comparison previews. Successful import completes base preparation only; completing the rough draft requires actual pixel edits and inspection logs.

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py call import_image \
  '{"input_image":"<task-id>/shader-v01/pixel-base-v01.png","output":"source/<id>-v01.aseprite"}'
```

Tuning colors uses the fixed families declared for the task. For global mapping, call `set_palette` with the target colors, then use `set_color_mode` with `palette_source="keep"` and `dithering="none"` to convert to indexed, converting back to RGB for detail work if needed; verify material zoning, alpha, and apertures before and after mapping. `quantize_palette` derives colors from images and cannot replace locked production palettes. For color bleed or ambiguity, apply localized MCP corrections per component/material region.

The `create_sprite`/`draw_pixel_map` examples below are for localized drafting or user-specified alternative blockout methods, not default entrypoints that bypass base import:

```bash
python3 .agents/skills/pixel-art/scripts/mcp_client.py call create_sprite \
  '{"filename":"source/torch-v01.aseprite","width":32,"height":48}'
python3 .agents/skills/pixel-art/scripts/mcp_client.py call draw_pixel_map \
  --args-file "Test Workspace/reports/torch-pixel-map.args.json"
python3 .agents/skills/pixel-art/scripts/mcp_client.py call render_preview \
  '{"filename":"source/torch-v01.aseprite","frame":1,"scale":6,"views":["color","value","silhouette","actual"]}' \
  --save-image previews/torch-review.png
```

Argument files are JSON objects; prefer files for complex arguments. Example pixel map:

```json
{
  "filename": "source/torch-v01.aseprite",
  "rows": ["..aa..", ".abba.", "abccba", ".abba.", "..aa.."],
  "legend": {"a":"#6d2e2a", "b":"#d5702f", "c":"#f4d886"},
  "x": 13, "y": 5, "layer": "Layer 1", "frame": 1
}
```

`--save-image` writes the server's returned PNG directly to `Test Workspace/previews/`, viewable via `view_image`.

## Sequential Jobs and Resumption

Job files use `tool/arguments`, distinct from `apply_operations`'s `op/args`:

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

The client validates schemas first, calls `tools/call` step-by-step, and halts at the first failure; logs are stored in `Test Workspace/reports/`. `expect` supports nested fields matched against actual results. Jobs are non-transactional; partial modifications may have been applied.

Following failures or interruptions, inspect logs, `get_sprite_info`, and actual previews to confirm source state, resuming only uncompleted steps. For transactional guarantees, use supported operations in `apply_operations`. If `extract_palette` exceeds `max_colors`, too many distinct colors are present; diagnose the source or compress subtle variations.

## Helper Scripts

| Script | When to Use |
|---|---|
| [prepare_reference_crops.py](../scripts/prepare_reference_crops.py) | Given `--manifest` and `--task-id`, copies original images to the workspace, generating localized crops via `import_image -> crop_sprite -> export_png`; never written to public skill repos; pass `--overwrite` to rebuild. |
| [make_style_sample.py](../scripts/make_style_sample.py) | Rebuilds the 4-frame lantern sample, generating jobs for MCP execution; uses historical colors; pass `--overwrite` to rebuild. |
| [reference_study.py](../scripts/reference_study.py) | Historical strict transcription tool that reads sources and manifests to generate jobs from scratch; run only when explicitly requested; cannot replace standard Blender base imports. |
| [compare_reference_study.py](../scripts/compare_reference_study.py) | Compares actual MCP exports against frozen iteration references, outputting per-asset reports. |

Example invocation for reference study (manifest definition in [Study Specification](../styles/parchment-fantasy/REFERENCE-STUDY.md)):

```bash
python3 .agents/skills/pixel-art/scripts/reference_study.py \
  --manifest <manifest.json> --iteration <new-id> --merge-threshold 1
python3 .agents/skills/pixel-art/scripts/mcp_client.py run \
  "Test Workspace/reports/reference-<new-id>-structure.job.json" --log-name reference-<new-id>-structure.mcp-log.json
python3 .agents/skills/pixel-art/scripts/compare_reference_study.py --iteration <new-id>
```

Execute study jobs by phases matching the [Production Pipeline](../workflow.md); `structure/light/export` jobs belong to the pixel phase and cannot replace Phases 1 and 2 (Blender modeling and lighting), which must be completed first unless explicitly waived by user prompt. Comparisons run post-export. `--assets` allows localized diagnosis, and `--candidate-dir` designates current task candidate PNG folders; save verification artifacts under a new ID for each round.
