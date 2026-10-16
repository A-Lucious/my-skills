---
name: pixel-art
description: "Create, modify, and export pixel art assets and sprite animations via Blender MCP and Aseprite MCP. Follow category and style specs, preview fixed style Pixel Shaders, and refine editable sprites. Use the built-in create-style interview to define and save a new pixel art style."
---

# Pixel Art

Determine the subject, purpose, and delivery goals from user requirements, assemble style and category specifications into task inputs, and execute the production pipeline. User-specified styles, simplifications, and review modes take precedence over defaults.

## Built-in Command: create-style

When the user invokes `create-style` or asks to create/add a reusable pixel art style, follow [commands/create-style.md](commands/create-style.md). Interview for missing visual direction, palette and tonal steps, and reference examples, then write an independent style directory and register it in the library. This is a style-authoring workflow; enter the asset production pipeline only when a sample or calibration asset is also requested. A one-off change to an asset's appearance does not by itself create a reusable style.

## 1. Style and Content Specifications

Read [Common Specifications](styles/COMMON.md) first. Select the requested style from the [Style Library](styles/index.md), defaulting to `parchment-fantasy` only when none is specified. Read the selected style's `STYLE.md`, `palette.json`, and `reference-library/INDEX.md` in `styles/<style-id>/`. When visual references are needed, use only permissible references provided for the current task; public packages exclude proprietary third-party game assets. Separately licensed base packs are described below. Parchment Fantasy examples and technical baselines apply only to that style; use the selected style's own documents for other styles.

Read the corresponding category specification for the task; for composite assets, start from the primary subject and supplement with related specs:

| User Task | Category Specification |
|---|---|
| Portraits, full-body characters, creatures | [Characters](specs/characters.md) |
| Event illustrations, environments, battle scenes | [Scenes](specs/scenes.md) |
| Props, equipment, icons, paper frames, decorations | [Props](specs/props.md) |
| Houses, ruins, standalone buildings | [Buildings](specs/buildings.md) |

All tasks read the [Lighting Specification](specs/lighting.md); read the [Texture Specification](specs/texture.md) when surface textures are needed. Establish a task card for every task following the [Production Specification](specs/production.md); when tracing or calibration is requested, also read the selected style's `REFERENCE-STUDY.md`.

### Reusable Base Assets

For reusable UI components, borders, and small icons, consult the cross-style [source index](asset-library/INDEX.md). This library stores metadata only. Browse upstream previews and verify the selected file's current license before downloading. Follow the [on-demand usage and 50 MiB cache budget](asset-library/README.md); obtain only selected files and their notices, without bulk or full-site downloads. Put working copies and provenance in the target project's `Test Workspace/<task-id>/references/`, then adapt them through Aseprite MCP to the selected style, native grid, and palette, following the asset-track routing below. Remove disposable downloads after delivery. Most sources use CC0; Game-icons primarily uses CC BY 3.0 and requires applicable author credit; see [license records](asset-library/THIRD_PARTY_LICENSES.md).

## 2. Production Pipeline

### Asset Type Track Routing (Workflow Branching)

Avoid a one-size-fits-all approach; route assets according to their inherent characteristics:

- **Track A (Hard-Surface & Spatial Assets):** Buildings, machinery, chests, spatial props. Strictly adhere to 3D modeling -> real ray/lighting -> base polish, taking full advantage of 3D perspective accuracy.
- **Track B (Organic & Decorative UI Assets):** Scrolls, parchment frames, ribbons, plant wreaths, flat icons. The core appeal of these assets lies in hand-drawn exaggeration and rhythmic shape appeal. Two execution strategies are permitted:
  - **Strategy 1 (Pure 2D Hand-drawn Blockout Track):** Block out silhouettes directly in 2D within Aseprite (Silhouette Blockout), cutting out asymmetric torn edges, scroll roll thickness, and hand-drawn curves using classic 2D pixel color blocks to avoid rigid 3D artifacts.
  - **Strategy 2 (Organic Sculpt / Curved 3D if 3D is required):** Rigid box-modeling is strictly prohibited.

### Execution Rules

When creating, modifying, or exporting assets in Track A or Track B Strategy 2, execute the six phases in [workflow.md](workflow.md) sequentially: **1: 3D & Camera -> 2: Lighting & Render -> 3: Style Pixel Shader & Advance Preview -> 4: Aseprite Rough Draft -> 5: Pixel Clusters, Details & Texture -> 6: Final Visual Check**. When Track B Strategy 1 is selected, record the pure 2D blockout track in the task card and proceed directly to Phase 4 for Aseprite silhouette blockout, retaining artifacts and check records.

The Pixel Shader is fixed per style as `styles/<style-id>/pixel_shader.py` and executed directly inside Blender via Blender MCP. Read that style's `PIXEL-SHADER.md` for implementation, invocation, and validation status. Do not invent per-task algorithms or cross-apply shaders between styles. For Parchment Fantasy implementation and invocation, see [Pixel Shader](styles/parchment-fantasy/PIXEL-SHADER.md). Draft styles require their missing implementation or calibration before entering 3D production; a 2D-only style does not waive Track A requirements. Present the Shader preview under the confirmed camera angle and complete review before proceeding to Phase 4.

The current technical baseline for Parchment Fantasy is Shader `1.3.0`, Palette `4.3`, and native `64x64`: preserves real display lighting, supports material-to-family partitioning, and prevents cross-color bleeding on parts such as bottle necks. See [Shader Baseline](styles/parchment-fantasy/PIXEL-SHADER.md#technical-baseline) for baseline parameters and ranges; generate and showcase the current effect for each new object in Phase 3.

Phases may be omitted only when explicitly stated by user prompts; cite verbatim user text and define the omitted scope in the task card. Except for the explicit Track B strategy, do not omit 3D or lighting unilaterally. Consolidated reviews or one-shot trials modify review methods only; they do not authorize skipping production phases.

Phase completion is validated through real artifacts, upstream comparisons, and visual self-checks, not mere file existence or tool return status. Track A 3D guidance must include real spatial data; Phase 3 generates and presents Blender pixel outputs, and Phase 4 imports the identical confirmed native PNG via Aseprite MCP as the base, modifying it in Aseprite into a rough draft. Maintain a side-by-side comparison between the imported base and the modified draft; importing or resaving alone does not constitute a completed rough draft. Technical checks, agent visual self-checks, and user acceptance are logged separately; agents must never fill in user "approved" on their behalf.

## 3. MCP Operations

- [Blender MCP](mcp/blender.md): 3D blockout, camera, lighting, guidance data, and direct native pixel base export.
- [Aseprite MCP](mcp/aseprite.md): Base import, followed by pixel creation, editing, scaling, color tuning, compositing, and formal exports, with the workspace rooted in project `Test Workspace/`.
- Scripts handle data/JSON orchestration, read-only analysis, byte-level saving, and copying; pixel writing and exports are performed via real MCP calls.

All generated files (including Blender files, task cards, temporary scripts, invocation logs, phase previews, and backups) are centralized under `Test Workspace/` organized by task. The skill reference library is read-only by default; write to it only upon explicit user instruction. After delivery, clean up intermediate files, obsolete iterations, and backups, retaining final assets, editable sources, and essential previews. Game integration proceeds as a separate step per user request.

`references/` houses in-house technical cases: [Wooden Chest Texture](references/cases/wooden-chest/case.md) and [Potion Bottle Shader Base](references/cases/health-potion/case.md). Third-party images and tracing studies are not distributed with the skill; see [NOTICE.md](NOTICE.md) for provenance notes. Category specifications provide design principles; specific dimensions, sampling, and texture parameters follow the current task and reference cases.

## 4. Public Distribution

Public cases retain only technical data and relative paths required for the task. They must exclude personal identity, accounts, names, contact information, local absolute paths, creation dates, sign-off timestamps, and raw private conversation text. Date-like seeds must not be displayed as public parameters; technical version numbers and animation durations may be retained. Local task cards may keep production records, which must be sanitized before publishing without bundling logs or caches. See [NOTICE.md](NOTICE.md) for style provenance and third-party material boundaries.
