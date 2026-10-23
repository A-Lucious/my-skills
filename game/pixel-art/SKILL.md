---
name: pixel-art
description: "Create, modify, and export pixel art assets and sprite animations via Blender MCP and Aseprite MCP. Use pre-light structural Sobel, protected SOFT.04, style palette mapping, and constrained Aseprite cleanup for original 3D assets; use Aseprite-only pure drawing for faithful 2D reference reproduction with measured SSIM/PSNR fidelity. Supports modular props, portraits, materials, and the create-style interview."
---

# Pixel Art

Determine the subject, purpose, and delivery goals from user requirements, assemble style, category node cards, and material cards into task inputs, choose the baseline, and execute it. User-specified styles, simplifications, and review modes take precedence over defaults.

## Built-in Command: create-style

When the user invokes `create-style` or asks to create/add a reusable pixel art style, follow [commands/create-style.md](commands/create-style.md). Interview for missing visual direction, palette and tonal steps, and reference examples, then write an independent style directory and register it in the library. This is a style-authoring workflow; enter the asset production pipeline only when a sample or calibration asset is also requested. A one-off change to an asset's appearance does not by itself create a reusable style.

## 1. Modular Card Injection Architecture

Assets are constructed by mounting three orthogonal layers of specifications:

### Category Node Cards (`cards/<category>/`)
Each asset category provides dedicated instruction cards tailored for every phase node of the baseline engine:

| Category | Description | Specification / Cards |
|---|---|---|
| **Props & Items** | Containers, equipment, potions, weapons, books | [cards/props/](cards/props/) (`3dac`, `lr`, `psap`, `ard`, `pcdt`, `fvc`) |
| **Portraits** | Dialog avatars, head-and-shoulders portraits, NPC busts | [cards/portraits/design.md](cards/portraits/design.md), then `cards/portraits/<phase-node>.md` (`3dac`, `lr`, `psap`, `ard`, `pcdt`, `fvc`) |
| **Characters & Creatures** | Full-body combat sprites, characters, creatures | [specs/characters.md](specs/characters.md) |
| **Scenes & Buildings** | Event illustrations, environments, architectural structures | [specs/scenes.md](specs/scenes.md), [specs/buildings.md](specs/buildings.md) |

For portraits, read the [design card](cards/portraits/design.md) before production and select its input route. Image generation is conditional on the user's prompt; the image-source route applies the smooth portrait Pixel Shader before Aseprite. Otherwise use the standard six-phase pipeline. Mount only the corresponding portrait card at each applicable phase.

### Material Cards (`cards/materials/`)
Mount applicable physical material rules to govern highlights, value transitions, and cluster patterns in Phase 5:
- [Wood](cards/materials/wood.md) | [Metal](cards/materials/metal.md) | [Skin](cards/materials/skin.md) | [Cloth & Leather](cards/materials/cloth_leather.md) | [Glass & Gems](cards/materials/glass_gem.md)

### Feature Cards (`cards/features/`)
Mount specialized pipeline modifiers when required:
- [Sprite Animation](cards/features/animation.md) | [Flat UI & Decorative Elements](cards/features/flat_ui.md)
- [Agent Pure-Draw Baseline](cards/features/pure_draw.md) — the second production baseline, see §2

### Global Style & Base Specifications
- Read [Common Specifications](specs/common.md) for fundamental pixel grid, staircasing, and cluster rules.
- Select style from [Style Library](styles/index.md) (defaults to `parchment-fantasy`). Read the selected style's `STYLE.md`, `palette.json`, and `reference-library/INDEX.md` in `styles/<style-id>/`.
- Read [Lighting Specification](specs/lighting.md), [Texture Specification](specs/texture.md), and [Production Specification](specs/production.md) for global execution constraints.

### Reusable Base Assets
For reusable UI components, borders, and small icons, consult the cross-style [source index](asset-library/INDEX.md). Follow the [on-demand usage and 50 MiB cache budget](asset-library/README.md). Put working copies and provenance in the target project's `Test Workspace/<task-id>/references/`, adapting them through Aseprite MCP. Most sources use CC0; Game-icons uses CC BY 3.0; see [license records](asset-library/THIRD_PARTY_LICENSES.md).

## 2. Baselines and Production Pipeline

This skill has **two baselines**. Read [Baseline Selection](specs/baselines.md) and pick one before
producing anything; the Agent decides, states the choice in one line, and records it in the task card.

| | What it does | Where |
|---|---|---|
| **A — Production** | Builds a new original asset from a described subject: 3D form → pre-light structural Sobel/masks → actual lighting → protected SOFT.04 → style palette quantization → constrained Aseprite source-color cleanup → refinement. Style-locked palette, transparent, native grid, animatable. | [workflow.md](workflow.md) |
| **B — Agent Pure-Draw** | Redraws a **supplied 2D image** faithfully at its own pixel size, Aseprite only, and reports measured fidelity (SSIM/PSNR/tolerance coverage). | [cards/features/pure_draw.md](cards/features/pure_draw.md) |

Pick **B** when the user supplies an image and wants it reproduced — 「画这个」「复刻」「按这张图」,
or a similarity/pixel-match target, or an existing screenshot, UI element or piece of art with no 3D
form to build. Pick **A** when the user describes a subject, or supplies an image as style/content
reference for a *new* asset that must fit the project's locked palette. Full decision matrix,
mixed cases, and the never-do list are in [Baseline Selection](specs/baselines.md).

The two baselines use different gates; never apply one baseline's gate to the other. `check_palette.py`
is a gate for A, not for B; a fidelity score is required for B, not for A.

Baseline A executes these six phases sequentially:
1. **3D & Camera (3dac):** Mount `cards/<category>/3dac.md`.
2. **Structure, Lighting & Render (lr):** Sample native alpha/normals/depth/IDs before lighting, detect structural edges and create protection masks through Aseprite MCP, then render actual lighting. Mount `cards/<category>/lr.md` and `specs/lighting.md`.
3. **Style Pixel Shader Preview (psap):** Apply SOFT.04 with the structural 1px protection band, then fixed palette quantization. Mount `cards/<category>/psap.md` and style shader.
4. **Aseprite Rough Draft (ard):** Import that exact base and write constrained neighboring source colors at approved structural candidates before refinement. Mount `cards/<category>/ard.md` and style palette.
5. **Pixel Clusters, Details & Texture (pcdt):** Mount `cards/<category>/pcdt.md`, `cards/materials/*.md`, and `specs/texture.md`.
6. **Final Visual Check (fvc):** Mount `cards/<category>/fvc.md` and `specs/production.md`.

Baseline B replaces all six phases with its own five stages (measure the reference → choose the
palette → emit the draw job → draw in tone bands → verify fidelity); the card is the authority.


For Parchment Fantasy's standard 3D route, use the sole [structural production baseline](styles/parchment-fantasy/PIXEL-SHADER.md), Shader `2.0.0`, native `64x64`, Palette `4.3`. Run `sample_structure` through Blender MCP, `scripts/structural_edges.py prepare` plus its real Aseprite mask job, then `render_preview` with mandatory guidance; after the preview, run `structural_edges.py cleanup` and its Aseprite job. There are no alternate Blender modes, unprotected dithering switches, or fallback entrypoints. The conditional portrait image route instead uses [the smooth portrait Shader](styles/parchment-fantasy/PORTRAIT-PIXEL-SHADER.md). Present the selected route's Shader preview before proceeding to Phase 4.

Except for the conditional portrait image route defined in the design card, phases may be omitted only when explicitly stated by user prompts; cite verbatim user text in the task card. Phase completion is validated through real artifacts, upstream comparisons, and visual self-checks. The portrait route is not a general waiver for other categories.

## 3. MCP Operations

- [Blender MCP](mcp/blender.md): 3D blockout, camera, lighting, guidance data, and direct native pixel base export.
- [Aseprite MCP](mcp/aseprite.md): Base import, followed by pixel creation, editing, scaling, color tuning, compositing, and formal exports, with workspace rooted in `Test Workspace/`.
- Scripts handle data/JSON orchestration, read-only analysis, byte-level saving, and copying; pixel writing and exports are performed via real MCP calls.

All generated files are centralized under `Test Workspace/` organized by task. The skill reference library is read-only by default. After delivery, clean up temporary intermediate files, retaining final assets, editable sources, and essential previews.

## 4. Public Distribution

Public cases retain only technical data and relative paths required for the task. Exclude personal identity, accounts, names, contact information, local absolute paths, and raw conversation text. See [NOTICE.md](NOTICE.md) for style provenance and third-party material boundaries.
