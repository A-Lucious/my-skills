# create-style

Create a reusable pixel art style through a short interview, then save it under `styles/<style-id>/` and add it to `styles/index.md`. Invoke with `Using $pixel-art create-style, help me create a new style`, or an equivalent request in the user's language. This is an agent-guided command within Pixel Art, not a shell executable or a separate installed skill.

## 1. Interview for the Missing Decisions

Reuse requirements, examples, and answers already present in the conversation. Ask in the user's language, in small batches of two or three questions; adapt follow-ups instead of presenting the entire checklist at once. Use the environment's user-input tool when available. When no answer has arrived, keep required questions pending; do not treat elapsed time as an answer.

Start with visual direction, color/tonal preferences, and examples. Cover the remaining topics only where they affect the resulting style:

| Topic | Decisions to Capture |
|---|---|
| Identity and direction | Display name, unique lowercase hyphenated ID, theme/mood, intended uses, distinctive features, and things to avoid. Suggest an ID from the name if none is supplied. |
| Color and tonal steps | Hue temperature, saturation/contrast, color families, shades per family (including exceptions), shadow/midtone/highlight organization, hue shifts, accent colors, and family budgets per asset type. Ask whether there is a fixed palette or the agent should propose HEX ramps. Distinguish number of families from total RGB colors. |
| Reference examples | Existing images, links, games/artists, or descriptive examples; what to adopt or avoid in each. Ask whether examples exist, but continue from verbal direction when none are available. Inspect supplied visuals before claiming observations; record uninspected named examples as such. |
| Shapes and pixels | Proportions, exaggeration, silhouette language, native sizes by category, cluster density, outlines (width/color/selective or continuous), texture density, dithering, and antialiasing. |
| Light and materials | Key light direction, shadow softness, value range, specular/glass/emissive treatment, material-to-family mappings, and transparency policy. |
| Scope and validation | Relevant asset categories, animation needs, and whether a calibration sample is wanted now. Style creation alone does not request an asset or authorize game integration. |

For example, an opening batch in Chinese can ask:

1. “这个风格大致是什么方向，主要用在哪类素材上？有偏好的名字吗？”
2. “配色倾向是什么？希望每个色族有多少级明暗？已有色板，还是让我提出一版？”
3. “有没有想参考的案例，以及特别想保留或避开的特点？没有案例也可以用文字描述。”

Users may delegate choices such as HEX values, native size, or ramp lengths. Make those choices, label them as agent proposals in the style summary, and continue within that delegation. Do not copy Parchment Fantasy's palette, 64x64 grid, or Shader parameters as unasked defaults for a new style. Resolve contradictions that materially change the style; optional missing examples do not block creation.

Summarize the resolved direction and distinguish user choices from agent proposals. If the requested decisions are supplied or delegated, proceed to writing without another approval round. If a necessary choice remains unresolved, ask a focused follow-up before committing that choice to the style.

## 2. Prepare the Style Directory

Read [COMMON.md](../styles/COMMON.md), the [style index](../styles/index.md), and the current [Parchment Fantasy directory](../styles/parchment-fantasy/STYLE.md) as a structural example. Read its other files only to understand relevant formats; its artistic choices and historical baselines are not a template for the new style's content. Check [check_palette.py](../scripts/check_palette.py) for the palette's enforced schema.

Use an ID matching `[a-z0-9]+(?:-[a-z0-9]+)*`, at most 63 characters. IDs are names, not paths. If the directory or library ID already exists, use a different name or clarify whether the user intends to update that style; do not overwrite it as a new style. Preserve the existing default and other style files.

Write this layout, using actual interview decisions rather than unresolved template tokens:

```text
styles/<style-id>/
├── STYLE.md
├── palette.json
├── PIXEL-SHADER.md
├── pixel_shader.py           # Independent implementation when supporting 3D
├── REFERENCE-STUDY.md
└── reference-library/
    └── INDEX.md
```

Create `pixel_shader.py` when implementing the shader as described below. If only specifications are being created and it is absent, state that explicitly in `STYLE.md`, `PIXEL-SHADER.md`, and the index entry; do not create a placeholder executable.

The request to create a style authorizes these skill-library edits. Keep interview working notes, temporary scripts, logs, source references, and calibration artifacts in `Test Workspace/create-style-<style-id>/`. Store reusable decisions in the style files, without private conversation transcripts or machine-specific paths.

## 3. Write the Style Files

### STYLE.md

Include display name and ID, specification/palette versions, readiness status, intended categories, visual language, shapes/proportions, native grids and cluster density, outlines, color-family budgets, lighting/materials, textures, transparency, and relevant animation rules. Link `../COMMON.md`, local palette, Shader notes, study rules, and reference index. Explain how style choices specialize COMMON; surface conflicts rather than silently changing shared production rules.

Record a compact rationale connecting the interview's defining preferences to usable drawing rules. Distinguish documented decisions, untested proposals, and observed calibration conclusions. A style without real calibration is a specification draft, even when all files are present.

### palette.json

Build a complete palette compatible with `check_palette.py`:

- `style_id`: the directory ID; `version`: an independent initial version such as `1.0.0`; `provenance`: the actual origin of the palette; `locked`: `true` once the interview choices or delegated proposal are written.
- `families`: named objects with `name`, positive `shade_count`, and `ramp` of that many unique six-digit HEX RGB colors in strictly increasing luminance. Define `shades_per_family` as the baseline and explicit per-family counts for exceptions.
- `family_count`: the number of families. `colors`: the deduplicated union of all family ramps. `color_count`: its actual length. Shared shades may belong to multiple declared families.
- `material_families`: each supported material mapped to an existing family. `ramps`: exactly the same material keys, each holding an ordered nonempty subset of its assigned family's colors.
- `asset_family_limits`: positive per-purpose limits no greater than `family_count`. Include the asset types in this style's scope and use these same keys in Shader inputs; do not introduce asset types absent from this map.
- `alpha_policy`: the agreed permitted integer alpha values, each between 0 and 255; `counting_rule` and `shade_count_policy`: explain the chosen budgets and tonal steps.

Calculate inventory counts and derived material ramps from the family data to avoid inconsistent duplicated fields. Color locking records a production contract, not a claim of visual validation; later palette revisions follow the skill's versioning rules. Do not describe guessed colors as sampled or official values.

### PIXEL-SHADER.md and pixel_shader.py

Document the style's 3D conversion contract: native grid, palette mapping, material zoning, alpha edges, outline/dithering behavior where relevant, supported Blender versions/engines, callable inputs/outputs, and implementation/validation status. Version implemented scripts independently and pair them with the local palette version.

When the requested scope includes Shader implementation, author a self-contained `pixel_shader.py` for this style's decisions, loading its sibling `palette.json`. Use the structural production contract: expose `sample_structure` for native-grid guidance before lighting, require the generated Aseprite protection mask in `render_preview`, apply protected SOFT.04 before the style palette, then constrain Aseprite source-color writes by surface identity. Document the style-specific inputs; do not add alternate Blender baselines. Importing the module must not render or alter the source scene. Preserve upstream data, record script/palette hashes and actual arguments in a manifest, and generate native base and same-view comparison outputs through Blender MCP. Use the existing [Blender integration rules](../mcp/blender.md); do not call or import another style's production Shader, rename its implementation unchanged, or substitute external pixel processing.

Writing specifications does not require launching Blender or Aseprite. If implementation or live calibration is outside the current request or the tools are unavailable, save the requested specification with the exact pending work and readiness limits. A script that has only passed syntax checks remains unvalidated. Before production, complete the independent implementation and actual Step 3 preview; do not label a missing or stubbed Shader ready.

### REFERENCE-STUDY.md

Define this style's observation and comparison method: provenance, target grid estimates, proportions, cluster/outline language, palette and value organization, lighting/material cues, and task-specific comparison criteria. Keep source observations separate from the production palette. Follow the shared workflow and do not inherit Parchment Fantasy's historical example coordinates, thresholds, asset lists, or calibration claims.

### reference-library/INDEX.md

List each actual reference or descriptive example, source/credit, permitted use and redistribution scope where known, inspection status, relevant observations, and limitations. Separate user-provided examples, agent suggestions, and the style's own technical cases. If no visual references were provided, say the style is based on verbal requirements and has no observed reference baseline. Do not invent sources, permissions, sample paths, or visual findings.

Keep third-party and private reference files in the task workspace under [NOTICE.md](../NOTICE.md)'s boundaries. Only add distributable style-owned reference assets when requested; do not bundle a named game's assets with the style.

## 4. Register, Validate, and Deliver

1. Add one row to `styles/index.md` with the unique ID, visual direction, links to the new files, and any draft/unvalidated scope. Retain existing rows and the default.
2. Run `python3 <skill-root>/scripts/check_palette.py --style <style-id>` and fix schema, ramp ordering, and budget failures. Check relative links and consistency among the directory ID, palette, style docs, and Shader metadata. If a Shader was written, syntax-check it without executing Blender-dependent code; keep any cache under the task workspace.
3. If a calibration sample was requested, read the applicable category and production specs and run the Blender/Aseprite pipeline. Show actual previews and record technical checks, agent review, and user acceptance separately. Save outputs in the task workspace and summarize observed conclusions in the style docs; a passing palette check alone does not validate appearance or a Shader. Missing tools block live calibration, not saving the agreed specifications.
4. Deliver links to the new style directory's main files, summarize its defining choices and readiness, and show a usage prompt such as `Using $pixel-art, create <asset> in the <style-id> style`. State remaining implementation/calibration work when applicable. Clean up disposable working files while retaining necessary calibration previews and editable sources.
