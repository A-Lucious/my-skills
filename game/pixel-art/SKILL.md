---
name: pixel-art
description: "Create, modify, and export pixel art assets and sprite animations via Blender MCP and Aseprite MCP. Follow modular card injection templates for props, portraits, characters, and materials, preview fixed style Pixel Shaders, and refine editable sprites. Use the built-in create-style interview to define and save a new pixel art style."
---

# Pixel Art

Determine the subject, purpose, and delivery goals from user requirements, assemble style, category node cards, and material cards into task inputs, and execute the production pipeline. User-specified styles, simplifications, and review modes take precedence over defaults.

## Built-in Command: create-style

When the user invokes `create-style` or asks to create/add a reusable pixel art style, follow [commands/create-style.md](commands/create-style.md). Interview for missing visual direction, palette and tonal steps, and reference examples, then write an independent style directory and register it in the library. This is a style-authoring workflow; enter the asset production pipeline only when a sample or calibration asset is also requested. A one-off change to an asset's appearance does not by itself create a reusable style.

## 1. Modular Card Injection Architecture

Assets are constructed by mounting three orthogonal layers of specifications:

### Category Node Cards (`cards/<category>/`)
Each asset category provides dedicated instruction cards tailored for every phase node of the baseline engine:

| Category | Description | Node Cards Directory |
|---|---|---|
| **Props & Items** | Containers, equipment, potions, weapons, books | [cards/props/](cards/props/) (`3dac`, `lr`, `psap`, `ard`, `pcdt`, `fvc`) |
| **Portraits & Busts** | Dialog avatars, NPC busts, head planes, facial features | [cards/portraits/](cards/portraits/) (`3dac`, `lr`, `psap`, `ard`, `pcdt`, `fvc`) |
| **Full-Body Characters** | Combat sprites, monsters, poses, silhouette landmarks | [cards/characters/](cards/characters/) (`3dac`, `lr`, `psap`, `ard`, `pcdt`, `fvc`) |
| **Scenes & Buildings** | Event illustrations, environments, architectural structures | [specs/scenes.md](specs/scenes.md), [specs/buildings.md](specs/buildings.md) |

### Material Cards (`cards/materials/`)
Mount applicable physical material rules to govern highlights, value transitions, and cluster patterns in Phase 5:
- [Wood](cards/materials/wood.md) | [Metal](cards/materials/metal.md) | [Skin](cards/materials/skin.md) | [Cloth & Leather](cards/materials/cloth_leather.md) | [Glass & Gems](cards/materials/glass_gem.md)

### Feature Cards (`cards/features/`)
Mount specialized pipeline modifiers when required:
- [Sprite Animation](cards/features/animation.md) | [Flat UI & Decorative Elements](cards/features/flat_ui.md)

### Global Style & Base Specifications
- Read [Common Specifications](specs/common.md) for fundamental pixel grid, staircasing, and cluster rules.
- Select style from [Style Library](styles/index.md) (defaults to `parchment-fantasy`). Read the selected style's `STYLE.md`, `palette.json`, and `reference-library/INDEX.md` in `styles/<style-id>/`.
- Read [Lighting Specification](specs/lighting.md), [Texture Specification](specs/texture.md), and [Production Specification](specs/production.md) for global execution constraints.

### Reusable Base Assets
For reusable UI components, borders, and small icons, consult the cross-style [source index](asset-library/INDEX.md). Follow the [on-demand usage and 50 MiB cache budget](asset-library/README.md). Put working copies and provenance in the target project's `Test Workspace/<task-id>/references/`, adapting them through Aseprite MCP. Most sources use CC0; Game-icons uses CC BY 3.0; see [license records](asset-library/THIRD_PARTY_LICENSES.md).

## 2. Production Pipeline

Execute the six phases in [workflow.md](workflow.md) sequentially:
1. **3D & Camera (3dac):** Mount `cards/<category>/3dac.md`.
2. **Lighting & Render (lr):** Mount `cards/<category>/lr.md` and `specs/lighting.md`.
3. **Style Pixel Shader Preview (psap):** Mount `cards/<category>/psap.md` and style shader.
4. **Aseprite Rough Draft (ard):** Mount `cards/<category>/ard.md` and style palette.
5. **Pixel Clusters, Details & Texture (pcdt):** Mount `cards/<category>/pcdt.md`, `cards/materials/*.md`, and `specs/texture.md`.
6. **Final Visual Check (fvc):** Mount `cards/<category>/fvc.md` and `specs/production.md`.

For Parchment Fantasy, execute `styles/parchment-fantasy/pixel_shader.py` via Blender MCP at native `64x64`, Palette `4.3`. Present Shader previews under confirmed camera angles before proceeding to Phase 4.

Phases may be omitted only when explicitly stated by user prompts; cite verbatim user text in the task card. Do not omit 3D or lighting unilaterally. Phase completion is validated through real artifacts, upstream comparisons, and visual self-checks.

## 3. MCP Operations

- [Blender MCP](mcp/blender.md): 3D blockout, camera, lighting, guidance data, and direct native pixel base export.
- [Aseprite MCP](mcp/aseprite.md): Base import, followed by pixel creation, editing, scaling, color tuning, compositing, and formal exports, with workspace rooted in `Test Workspace/`.
- Scripts handle data/JSON orchestration, read-only analysis, byte-level saving, and copying; pixel writing and exports are performed via real MCP calls.

All generated files are centralized under `Test Workspace/` organized by task. The skill reference library is read-only by default. After delivery, clean up temporary intermediate files, retaining final assets, editable sources, and essential previews.

## 4. Public Distribution

Public cases retain only technical data and relative paths required for the task. Exclude personal identity, accounts, names, contact information, local absolute paths, and raw conversation text. See [NOTICE.md](NOTICE.md) for style provenance and third-party material boundaries.
