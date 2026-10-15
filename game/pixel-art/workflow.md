# Production Pipeline

This workflow describes how a pixel art asset progresses from requirements to final delivery: clarify what to depict, establish clear forms and lighting, generate and preview pixel bases using fixed style shaders, block out major color masses and material details in Aseprite, and finally verify overall visual coherence.

Choose styles and categories from the [Skill Entrypoint](SKILL.md); review methods, file naming, and delivery formats are defined in the [Production Specification](specs/production.md). Operations below follow chronological production order.

## Before Starting: Clarifying the Subject

1. **Understand the intended use.** Summarize the goal in one sentence, e.g., "Draw an opened treasure chest icon that fits in an inventory slot" or "Draw a young traveler portrait with clear facial expression." Confirm whether delivery is a static sprite, animation, or scene illustration, and where it will appear in-game.
2. **Inspect relevant references.** Review full images and detail crops, noting subject size, viewing angle, color zoning, value balance, and detail density. Record specific features to reference, such as chest lid angle, paper frame lightness, or facial proportions.
3. **List key features.** Clarify constituent parts, occlusion order, landmarks that must be instantly recognizable, and allowable simplifications. For chests, note opening angle and lid; for portraits, note orientation and expression; for scenes, note event focal points and depth layers.
4. **Determine canvas and production strategy.** Select native dimensions (the exact pixel dimensions of the PNG itself), viewing angle, materials, selected color families, and lighting plan. Record these in the task card to serve as a verifiable baseline during revisions.

The Blender track begins at Step 1 by default and executes all six phases; pure 2D tracks execute under Track B Strategy 1 as defined in the skill entrypoint. Phases may be omitted only when explicitly authorized in user prompts; cite verbatim user text and outline the omitted scope in the task card, recording "No phase omission authorized" otherwise. Asset category, flat style, small resolution, or simple subjects do not justify skipping phases.

Phases 1 and 2 must be executed via real Blender MCP calls, preserving `.blend` files, camera/light records, render previews, and guidance data; text-only lighting plans or 2D value calculations cannot substitute for these phases. If required upstream artifacts are missing or tool calls fail, the phase remains incomplete; fix issues or report blockers explicitly rather than unilaterally switching to pure 2D workflows.

## Phase Completion Criteria

After generating artifacts, open and inspect them, recording versions used, evidence paths, concrete observations, and unresolved issues. Complete internal production and self-checks before submitting for user phase reviews per the production specification; consolidated reviews do not waive self-checks in the table below.

| Phase | Mandatory Verification Before Proceeding |
|---|---|
| 1: 3D & Camera | Major proportions, key parts, joints, and gaps hold in target-size silhouette; establish structural baselines for pixel comparison. |
| 2: Lighting & Render | Actual render corresponds to part/material, normal, and depth data for the same scene and camera; sample data to verify semantic alignment with the image; configuration lists alone are insufficient. |
| 3: Style Shader Preview | Execute the style directory's fixed script via Blender MCP, saving native base, same-view comparison, script version/hash, and parameters; present current effect to user and record Q3 review before Step 4. |
| 4: Rough Draft | Import the confirmed Phase 3 native PNG directly via Aseprite MCP as base, then edit into a rough draft in Aseprite; compare 3D guidance, imported base, and rough draft on the same grid; major proportions, joints, apertures, and value masses must hold before detail work. |
| 5: Details & Texture | Structure remains consistent with structural baselines before and after detail passes; claimed features are legible at intended display sizes; details do not disrupt form or values. |
| 6: Final Check | Complete visual and technical checks on the final source version and exports; present candidates and log user reviews truthfully, maintaining "pending review" until confirmed. |

Pixel abstraction allows silhouette tuning and landmark enlargement; record deliberate deviations from 3D alongside their legibility rationale. Do not use "pixel style" or "simplification" to excuse lost major forms, misaligned joints, or altered identities. Structural errors return to Step 1 or Step 4; lighting errors return to Step 2; do not mask errors with added textures or specular highlights.

## Step 1: 3D Blockout and Camera Setup

This phase resolves: what the object looks like, and from which viewing angle it is most legible.

1. **Break down the subject into primary components.** Build major masses in Blender, such as chest body, lid, and latch; or head, torso, limbs, and gear. For scenes, block out terrain, buildings, and character placements first. Flat symbols, paper frames, and silhouettes may use flat or shallow extruded meshes to establish outlines, cutouts, and layering, preserving flat aesthetic requirements while completing camera and subsequent lighting phases.
2. **Adjust proportions and connections.** Verify relative component sizes, natural joints, and clear articulation or postures. Prioritize overall silhouette masses here; defer fine patterning to the pixel phase.
3. **Establish pose and spatial relationships.** For characters, set center of gravity, limb placement, and equipment layering; for buildings, set roofs, walls, and entrances; for scenes, set focal points and foreground, midground, and background planes.
4. **Adjust camera.** Test multiple viewing angles, comparing visibility across front, side, and top planes. For instance, a direct top-down view of a chest might obscure wall thickness, while an overly low angle obscures the interior opening; pick an angle that highlights key features.
5. **Inspect silhouette at target pixel resolution.** Examine outline and negative space alone, checking whether latches, limbs, or doorways crowd together. If features are too small or mutually occluding, adjust sizes, positions, or camera angle and re-evaluate.
6. **Save draft and preview.** Tag components and materials for downstream processing, distinguishing "chest lid" from "metal band." Record structural baselines on the target grid: major width/height ratios, component anchors, connection axes or design offsets, apertures, and key landmarks; for animations, record shared anchors across frames. Select items that definitively evaluate the current form rather than applying generic ratios.

**Review focus (Q1):** Is the subject instantly recognizable? Are key components intact? Are proportions, joints, pose, and viewing angle appropriate?

**Deliverables:** 3D source file, target-angle preview, target-size silhouette, camera and component records.

## Step 2: Lighting Setup and Value Definition

This phase resolves: how surfaces express volume, and where cast shadows fall.

1. **Position key light according to lighting plan.** Set light direction, elevation, and softness, adjusting ambient fill so both illuminated and shadow sides remain readable. Place secondary lights (fire, magic) at appropriate positions when required.
2. **Observe major value planes.** Confirm clear distinctions between illuminated, turned, and shadowed faces. For a chest, top, front, and side faces must communicate distinct surface orientations.
3. **Trace shadows along occlusion relationships.** Check "what blocks light, and where the shadow falls." Examples: hat brim shading forehead, roof eaves shading walls, chest lid shading interior cavity; verify contact shadows along seams and grounding lines.
4. **Inspect full composition.** Verify that main subject, ground shadows, and background elements remain unclipped. If shadows extend beyond the frame, adjust framing or extend canvas margins before rendering previews.
5. **Export guidance maps and data for drawing.** Save color render with alpha, alongside real part/material IDs, normals, and depth data; record lighting or occlusion data when shadow evaluation is needed. Use real render passes or Blender target-grid ray queries; formats and criteria are detailed in [Blender MCP](mcp/blender.md). Object names, pass_index values, light positions, and camera parameters are configuration metadata and cannot substitute for spatial data.
6. **Inspect exported data.** Cross-check render maps against exported data arrays to verify that they describe a unified form and lighting setup. Read data dimensions, coordinate definitions, and representative pixel samples to ensure sampling originates from the active model, documenting which fields Steps 3 and 4 actually consume. A single render may serve Steps 1 and 2, but reuse must be explicitly noted with separate form and lighting logs; differing filenames do not prove distinct steps occurred.

**Review focus (Q2):** Is light direction clear? Do major planes convey volume? Do cast shadows match actual occlusions? Are contact points and shadow boundaries complete?

**Deliverables:** Lighted preview, raw guidance data, light source parameters, and data dictionary. Export procedures are detailed in [Blender MCP](mcp/blender.md).

## Step 3: Fixed Style Pixel Shader and Advance Preview

This phase converts Step 2 renders into style-compliant pixel bases, giving users advance visibility of Shader outputs prior to Aseprite rough drafting.

1. **Lock camera and inputs.** Use confirmed models, active camera, lighting, frame, crop box, and native WxH; record chosen style and color families. If an interactive viewport is referenced, align that view to a working camera via Blender MCP and re-render; never switch views silently.
2. **Execute style script directly.** Load `styles/<style-id>/pixel_shader.py` and run inside Blender via Blender MCP. Each style uses its own script; algorithms, thresholds, and color rules are version-locked, taking canvas size, selected families, and asset purpose as task inputs. See [Pixel Shader](styles/parchment-fantasy/PIXEL-SHADER.md) for Parchment Fantasy invocations and compatibility. If missing, author and preview the script first; do not borrow from other styles or improvise temporary node graphs.
3. **Save real outputs.** Preserve original models and Step 2 guidance, exporting native pixel PNGs, editable `.blend` files, same-view before/after comparisons, and invocation manifests from the working copy. Manifests include script path, version/hash, palette version/hash, camera matrix, engine, target dimensions, and actual arguments. Upscaled presentations cannot replace native bases.
4. **Inspect and present in advance (Q3).** Review native, integer-upscaled, and before/after comparisons, verifying forms, apertures, material colors, and major values; present results and remaining issues to the user. Await user confirmation of this version before entering Step 4; agent self-checks cannot substitute for user sign-off. Explicit consolidated review authorizations apply, but Shader previews must still be presented prior to Step 4. Re-render and re-preview if scripts, palettes, angles, or parameters change.

**Deliverables:** Native pixel base, same-view before/after comparison, pixelated working `.blend`, Shader manifest, and Q3 status. Previews may be imported into Aseprite MCP and exported at integer scales for presentation, but Step 4 production refinement does not begin here.

## Step 4: Import Blender Pixel Base and Refine Rough Draft in Aseprite

This phase comprises two distinct actions: **directly import the confirmed Step 3 native output as base -> edit base in Aseprite into a rough draft**. As colors, outlines, landmarks, and values are organized, preserve upstream forms and component relationships; completing import or resaving alone leaves Step 4 unfinished.

1. **Verify inputs and pixel grid.** Use Step 3 previewed model, camera, lighting, framing, and target WxH, logging grid origin and component anchors aligned with the Shader manifest.
2. **Reuse previewed native base.** Use the exact Blender PNG from Step 3 without silently switching shaders, palettes, or regenerating alternative outputs before import. Return to Step 3 if inputs change; recheck Q2 if engine changes affect lighting.
3. **Inspect Blender base output.** Verify that PNG matches target WxH; inspect silhouettes, component proportions, joints, holes, and light/shadow planes; high-resolution mosaic screenshots are not native pixel bases. If fine details were obliterated by sampling or subjects distorted, adjust model, camera, or grid in Blender and regenerate in Step 3 rather than painting an alternative subject from scratch.
4. **Import Step 3 output as base.** Pass the confirmed native PNG to Aseprite MCP's `import_image`, creating an editable `.aseprite` file; verify actual canvas, frames, and layers to ensure dimensions and pixel coordinates remain intact. Preserve the raw PNG, keep an untouched base reference layer in the source file, and duplicate it into an active draft layer. Execute modifications 5–7 below on this working layer via Aseprite MCP, logging base version, actual edits, and before/after comparisons. If the user explicitly requests an alternative drafting method, cite verbatim instructions and scope in the task card; other phases follow their standard protocol.
5. **Consolidate materials and fixed palette.** Map base colors to selected fixed families and working ramps per part/material guidance, eliminating render interpolation artifacts, semi-transparent edges, and necessary localized outlines. All pixel writes, palette adjustments, and layer operations must route through Aseprite MCP; do not create ad-hoc production palettes to accommodate render colors. Re-check silhouettes and apertures after converging transparency and color families.
6. **Reinforce key landmarks.** On the base structure, refine eyes, nose, latches, doorways, handles, and other details that must be clearly legible. Check sizes, spacing, and depth relationships, enlarging slightly where necessary and recording deliberate adjustments relative to the direct base.
7. **Organize major value masses.** Preserve primary illuminated, shadow, cast shadow, and contact shadow areas from the direct base, consolidating continuous render gradients into coherent pixel clusters; cross-check adjustments against raw normals and occlusion guidance. Flat symbols and paper frames preserve flat color block layering as requested.
8. **Generate comparison and inspect.** Produce a unified-grid comparison of 3D guidance / Blender pixel base / current draft via Aseprite MCP, checking Step 1 structural baselines item by item. Inspect subject and features at native scale, staircasing and joints under integer zoom, and value masses in greyscale; record preserved items, deliberate adjustments, and unresolved issues. If major proportions, joints, or landmarks fail, rework and re-compare without proceeding to Step 5.

**Review focus (Q4):** Is the sprite legible at small sizes? Are parts and materials distinguishable? Do major values hold? Do overall proportions and pixel density align with the chosen style?

**Deliverables:** Step 3 native PNG and pixelation parameters, `.aseprite` retaining base reference layer and edited draft layer, unified-grid comparison of 3D guidance / imported base / modified draft, native/zoom/greyscale previews, and structural verification notes. MCP commands are detailed in [Aseprite MCP](mcp/aseprite.md).

## Step 5: Pixel Clusters, Material Details, Texture, and Value Re-Check

This phase refines the rough draft to make outlines natural and materials explicit, while preserving established structural masses.

1. **Clean edges.** Adjust staircasing along curves and diagonals, removing jagged stray pixels, cramped components, and illegible micro-gaps. Zoom in to evaluate pixel placement, then return to native scale to verify improvements.
2. **Build material structure.** Add details that convey material thickness: book page edges, metal bands, fabric folds, timber joints, and window frame bevels. Ensure details follow existing planar forms and component relationships.
3. **Incorporate textures where appropriate.** Place short lines, micro-patches, wear, or broken seams within relevant material zones. "Pixel clusters" are groups of pixels forming coherent micro-shapes. Wood grain follows board planes, fabric textures follow folds, and metals use minimal wear with narrower highlights; see [Texture Specification](specs/texture.md) for organization patterns.
4. **Compare before and after detail passes.** Toggle detail or texture layers, cross-checking Step 4 structural baselines to verify that materials are clearer and subjects, expressions, and key parts remain recognizable. Inspect planned landmarks item by item to verify they actually appear in the sprite; do not claim completion based on design names if features are missing or illegible at native scale. If an area appears noisy or cluttered, prune or merge clusters and re-evaluate.
5. **Execute final value re-check.** View color and greyscale previews, hunting for relationships broken by detail passes: do textures disrupt shadow edges? Are shadow planes raised too bright by highlights? Did crevices lose depth? Do specular highlights align with material and surface orientation? Apply localized corrections per [Lighting Specification](specs/lighting.md) and generate updated previews.
6. **Inspect source files.** Read canvas, layers, frame counts, durations, and animation tags to confirm alignment with task specifications. For animations, review frames and playback, verifying anchors, continuity, and frame-by-frame values.
7. **Export candidates and execute technical checks.** Generate native PNGs or spritesheets, verifying dimensions, crops, palette, and transparency; check frame rectangles and durations for animations. Fix source files upon encountering issues and re-export. Detailed check procedures are in the [Production Specification](specs/production.md).

**Review focus:** Did details add useful information? Are materials more distinct? Do major values remain coherent? Are source files and exports technically valid?

**Deliverables:** Layered candidate source, before/after detail and final value previews, candidate exports, and technical check logs. Record seeds and parameters for procedural textures alongside this version.

## Step 6: Visual Coherence, Confirmation, and Delivery

This phase evaluates the finished asset within its actual operational context to determine whether initial goals were met.

1. **Re-evaluate against requirements and references.** Check subject identity, major proportions, connections, pose/expression, key parts, materials, and style against the same final source and actual export; cross-check structural baselines and initial feature lists. If unresolved form or recognition problems remain, record "Rework Required" in visual self-checks; palette compliance, zero stray pixels, or tool success cannot override this, and do not claim "Requirements fully satisfied."
2. **Inspect at actual display size.** Simultaneously inspect native image, integer-upscaled preview, and expected UI scale. Verify whether icons are instantly recognizable, check portrait expressions, and verify scene focal points; inspect margins and framing.
3. **Review additional animation or study outputs.** For animations, check motion rhythm and looping at standard playback speeds; for studies, compare against original references item by item and review comparison reports. Log specific defects to corresponding assets or frames.
4. **Submit candidates for user review (Q5).** Present current previews and editable source files, explaining primary changes and remaining issues. Record technical checks, agent visual self-checks, and user acceptance separately; Q5 remains "pending review" without explicit user confirmation—agents must never mark "approved" on behalf of the user. Step 5 internal detail checks do not constitute Q5. When revisions are requested, return to the corresponding step per the table below.
5. **Package accepted version.** Save corresponding sources, formal exports, final previews, task logs, and verification outputs, ensuring all deliverables stem from the identical version.
6. **Fulfill delivery objectives.** If game integration is requested, update asset references and verify actual in-game rendering per the production specification; for asset-only tasks, deliver files and documentation.

**Deliverables:** User-accepted version, final files and previews, sign-off logs, and actual display verification results when integration was requested.

## Tracing Studies and Animation Pipelines

**Reference Studies & Tracing:** Before starting, observe grid size, origin, and colors for each subject; Step 1 models major forms and matches camera; Step 2 generates guidance based on visible lighting; Step 3 calls the style shader and previews in advance; Step 4 imports the identical base and refines outlines, materials, and values on the observation grid; Step 5 organizes pixels against visible details and occlusions; Step 6 compares actual exports against references per asset. Studies do not automatically omit 3D phases or base imports; when users explicitly request blank-canvas transcription, proceed according to their instructions as described in [Study Specification](styles/parchment-fantasy/REFERENCE-STUDY.md).

**Animation:** Before starting, determine motion, orientation, and anchors (e.g., aligning frames by feet position); Step 1 establishes key poses and component relationships; Step 2 sets shared lighting across poses; Step 3 renders bases with fixed style scripts, camera, palette, and grid, previewing shader effects on representative frames; Step 4 imports per-frame bases via Aseprite MCP and refines readable major forms; Step 5 harmonizes materials, details, and frame-by-frame values; Step 6 inspects rhythm, motion continuity, and loops at normal playback speeds. Pure 2D tracks execute per the skill entrypoint.

## Modifying Existing Assets and Troubleshooting

Open active sources and previews to confirm versions; create a working copy, listing parts to modify and elements to preserve. Verify sequentially across Steps 1 through 6; upstream sources and guidance consistent with current requirements may be reused, provided versions, paths, and conclusions are inspected and logged. Missing upstream artifacts must be completed, and artifacts affected by edits must be regenerated. The table below identifies rework entrypoints but does not authorize skipping intermediate phases.

| Observed Defect | Rework Entrypoint & Action |
|---|---|
| Chest lid proportions incorrect, unnatural arm joints, obstructed doorways, or poor viewing angle | Step 1: Adjust geometry, part placements, or camera, regenerating affected guidance and pixel drafts. |
| Inverted shadow direction, shadows on wrong surfaces, or lighting contradicts plane values | Step 2: Adjust light sources and occlusion baselines, then update pixel values. |
| Clear in 3D, but latches vanish, faces cramp, or light/shadow planes become unreadable in pixels | Step 4: Adjust pixel grid alignment, outlines, landmarks, or major value blocks. |
| Shader export loses features, maps colors to wrong materials, or pixel block size is off | Step 3: Correct inputs or maintain style Shader versions, regenerating and previewing effects first. |
| Surfaces too uniform, textures cluttered, edges noisy, or details break shadow boundaries | Step 5: Adjust detail or texture layers, followed by a value re-check. |
| Clear in preview, but blurry, clipped, color-distorted, or frame order scrambled in export/game | Check export settings, file metadata, and display scale, correcting before regenerating previews. |

For state recovery and resumption after tool call failures, see [Aseprite MCP](mcp/aseprite.md).
