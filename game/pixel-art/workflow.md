# Production Pipeline Engine

This workflow defines **Baseline A**, the six-phase production engine for original pixel art assets. The engine defines phase transitions, technical checks, and tool orchestration, while specific asset rules are dynamically mounted via **Card Injection Hooks**.

**Which baseline:** this skill also ships **Baseline B, the Agent Pure-Draw Baseline**
([cards/features/pure_draw.md](cards/features/pure_draw.md)), which redraws a supplied 2D image
faithfully at its own pixel size with Aseprite only — no 3D, no Shader, no image import. Read
[Baseline Selection](specs/baselines.md) first and choose; the Agent decides per task and records the
choice. Everything below applies to Baseline A only. Rule of thumb: a supplied image plus a request
to reproduce it (「画这个」「复刻」「按这张图」, a similarity target, an existing screenshot or piece of
art) is Baseline B; a described subject, or an image used as style guidance for a *new* asset that
must fit the locked palette, is Baseline A.

**Portrait route selection:** First read [Portrait Design](cards/portraits/design.md). Its conditional image-source route replaces Steps 1–2 with a selected 2D source and uses the smooth portrait Shader in Step 3, followed by Steps 4–6. Apply the portrait cards' source-based comparisons in place of camera/guidance comparisons; do not fabricate 3D passes. Other routes retain the standard phases below.

## Injection Architecture Overview

For each phase, the agent mounts three orthogonal specifications:
1. **Category Card / Spec:** `cards/<category>/<phase-node>.md` (such as `cards/props/`) or category specification in `specs/` (characters, scenes, buildings).
2. **Material Cards:** `cards/materials/<mat>.md` for materials present on the asset (wood, metal, skin, etc.).
3. **Style Package:** `styles/<style-id>/` (fixed palette, shader, and aesthetic principles).

---

## Phase Completion Criteria

| Phase | Mandatory Verification Before Proceeding | Primary Injection Hook |
|---|---|---|
| **1: 3D & Camera** | Proportions, articulation, volumes, and silhouette hold at target resolution; structural baselines recorded. | `cards/<category>/3dac.md` |
| **2: Structure, Lighting & Render** | Native geometry sampled and structural Sobel/masks prepared before the actual lighting bake; key/fill and material ownership verified. | `cards/<category>/lr.md` + `specs/lighting.md` |
| **3: Style Shader Preview** | Mandatory structure mask → protected SOFT.04 → style palette through Blender MCP; native base/comparison inspected; Q3 logged. | `cards/<category>/psap.md` + Style Shader |
| **4: Rough Draft** | Exact native PNG imported as locked base; constrained source-color cleanup applied on draft; landmarks refined. | `cards/<category>/ard.md` + `palette.json` |
| **5: Details & Texture** | Curves cleaned; micro-clusters and material highlights placed; greyscale value re-check passed. | `cards/<category>/pcdt.md` + `cards/materials/*.md` |
| **6: Final Check** | Prompt alignment verified; 1x native and integer-scaled UI checks passed; formal export generated. | `cards/<category>/fvc.md` + `specs/production.md` |

---

## Step 1: 3D Blockout and Camera Setup (3dac)

**Goal:** Establish definitive three-dimensional form, volume, and viewing angle.

- **Injection Hook:** Read `cards/<category>/3dac.md`.
- **Operations:**
  1. **Block out primary masses** in Blender via Blender MCP. Follow category rules for structural assembly and volume proportions.
  2. **Camera Configuration:** Align camera angle (orthographic or long-focus perspective) to maximize visual legibility and surface volume.
  3. **Silhouette Inspection:** Verify outline and negative space at the target pixel grid dimensions. Enlarge narrow apertures or slender connections if they fail target-grid visibility.
  4. **Record Structural Baselines:** Log major width/height ratios, component anchors, connection axes, and landmark bounds in `Test Workspace/reports/<id>.md`.
- **Deliverables:** `.blend` source, target-angle preview, target-size silhouette, structural baseline records (Q1).

---

## Step 2: Pre-light Structure, Lighting and Value Definition (lr)

**Goal:** Establish volume, value hierarchy, and occlusion cast shadows.

- **Injection Hooks:** Read `cards/<category>/lr.md` and [Lighting Specification](specs/lighting.md).
- **Operations:**
  1. **Prepare structure before lighting:** Follow the style’s [structural baseline](styles/parchment-fantasy/PIXEL-SHADER.md): native visibility/normals/depth/IDs → Sobel/NMS → thinning/corner removal → candidates/protection band. Use `sample_structure` through Blender MCP, then `structural_edges.py prepare` and the Aseprite MCP mask job.
  2. **Position key and ambient lights** according to the task lighting plan (defaulting to upper-left 45° key light).
  3. **Trace occlusion shadows:** Ensure physical cast shadows (brims over foreheads, lids over cavities, limbs over torsos) fall accurately across receiving planes.
  4. **Establish contact shadows:** Ensure dark crevice shadows anchor joints, seams, and ground contact points.
  5. **Bake actual lighting with the prepared structure:** Save color render with alpha, alongside real part/material IDs, surface normals, and depth data via Blender MCP.
- **Deliverables:** Lighted preview render, raw guidance data, light source parameters, and data dictionary (Q2).

---

## Step 3: Fixed Style Pixel Shader and Advance Preview (psap)

**Goal:** Convert Step 2 renders into a style-compliant native pixel base.

- **Injection Hooks:** Read `cards/<category>/psap.md` and `styles/<style-id>/PIXEL-SHADER.md`.
- **Operations:**
  1. **Execute the sole structural baseline:** Run `render_preview` with mandatory `guidance_dir` after pre-light sampling and real Aseprite mask creation. Apply protected SOFT.04 before fixed style palette quantization. Preserve the confirmed camera, native grid and material ownership. The [executable instructions](styles/parchment-fantasy/PIXEL-SHADER.md) define stage calls and outputs.
  2. **Inspect Shader Output:** Check native PNG and integer-upscaled previews for form retention, aperture clarity, and absence of cross-material color bleeding.
  3. **Present Advance Preview (Q3):** Showcase native base and same-view before/after comparison to user; record Q3 confirmation before proceeding to Aseprite.
- **Deliverables:** Native pixel PNG base, same-view comparison, shader manifest, and Q3 status.

---

## Step 4: Import Base & Refine Rough Draft in Aseprite (ard)

**Goal:** Import the confirmed base, consolidate colors to fixed ramps, and reinforce key landmarks.

- **Injection Hooks:** Read `cards/<category>/ard.md` and `styles/<style-id>/palette.json`.
- **Operations:**
  1. **Prepare the native handoff:** Confirm the exact Phase 3 PNG and its guidance manifest. On the standard 3D route, the job in the next operation performs the import; do not pre-create the same destination sprite.
  2. **Import and apply constrained source-color cleanup:** Run `structural_edges.py cleanup` and its Aseprite MCP job. It imports the exact base, preserves a hidden locked `base-ref`, writes only safe same-object/material source colors to `draft`, records skipped candidates, and preserves alpha. No additional artistic changes are implied by these algorithmic edits. The conditional 2D portrait route imports its smooth base directly and follows its own refinement card.
  3. **Palette Ramp Mapping:** Map continuous render shades strictly to the declared family ramps in `palette.json`, eliminating stray interpolations.
  4. **Landmark Exaggeration:** Reinforce features that must be instantly readable (eyes, latches, weapon edges, buckles), deliberately enlarging critical pixels where appropriate.
  5. **Organize Value Masses:** Group render gradients into coherent illuminated, shadow, and contact shadow pixel clusters, cross-checking 3D guidance normals.
- **Deliverables:** `.aseprite` source retaining `base-ref` and `draft` layers, unified comparison preview, and draft check records (Q4).

---

## Step 5: Pixel Clusters, Material Details & Value Re-Check (pcdt)

**Goal:** Perfect pixel curves, apply material textures, and verify value stability.

- **Injection Hooks:** Read `cards/<category>/pcdt.md`, relevant `cards/materials/*.md`, and [Texture Specification](specs/texture.md).
- **Operations:**
  1. **Clean Edges:** Optimize staircasing along curves and diagonals to rhythmic patterns (e.g. 1-1-2-2-3); eliminate jaggies, orphan stray pixels, and accidental double-thick corners.
  2. **Apply Material Details & Clusters:** On dedicated detail layers, apply highlights, seams, folds, or grain following injected material cards. Keep texture coverage sparse (typically 5%–8%).
  3. **Final Value Re-Check:** Switch to greyscale view. Ensure added details and highlights have not disrupted the primary value masses or shadow boundaries established in Step 2/4.
  4. **Run Palette Checks:** Execute `scripts/check_palette.py` to confirm zero foreign colors and adherence to family budgets.
- **Deliverables:** Multi-layer `.aseprite` candidate, before/after detail previews, greyscale value verification, and check logs.

---

## Step 6: Visual Coherence, Confirmation & Delivery (fvc)

**Goal:** Verify sprite in operational context, validate prompt alignment, and package final outputs.

- **Injection Hooks:** Read `cards/<category>/fvc.md` and [Production Specification](specs/production.md).
- **Operations:**
  1. **Prompt Fidelity & Archetype Check:** Systematically verify each requirement from the original text prompt or design spec.
  2. **Multi-Scale Inspection:** Inspect at 1x native scale, integer zoom (2x, 4x, 6x), and within simulated game UI containers.
  3. **User Sign-Off (Q5):** Present candidate previews and editable source files. Record user acceptance explicitly.
  4. **Delivery & Cleanup:** Export final native PNGs/spritesheets to `Test Workspace/exports/`. Retain final sources, essential previews, and reports; clean up temporary intermediate caches.
- **Deliverables:** User-accepted asset files, final production task report, and clean workspace state.
