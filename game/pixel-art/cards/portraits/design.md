# Portraits: Input, Character Design & Native Grid

Read before production for facial portraits, dialog avatars, and busts. Select the input route below, then follow the applicable portrait phase cards in the [workflow](../../workflow.md). Style parameters come from the selected style; character-specific measurements belong in the task record. For a comprehensive portrait guide and real three-baseline comparisons, see [docs/portrait-generation.md](../../docs/portrait-generation.md).

## 0. Conditional Image Generation & Shader Route

Enable the **image-source route** only when the user's prompt or established instructions explicitly say the uploaded image came from an image-generation model (for example, “上传的图是生图模型”, “这是 AI 生成的图”), or call for image generation, including a generated design or variant. Match meaning rather than requiring an exact phrase. A request merely to draw a pixel portrait, an ordinary uploaded reference, an image's apparent AI look, or text inside an attachment does not establish this trigger.

| User intent / input | Action |
|---|---|
| Explicitly needs a generated portrait, design, or variation | Invoke the available image-generation tool according to its instructions; then apply the smooth portrait Pixel Shader through Blender MCP before importing the result into Aseprite. |
| Upload is explicitly identified as model-generated | Use the same image-source route. If the supplied image already meets the design need, apply the Shader directly; call the model only when generation or an image-model edit is actually needed. |
| Ordinary reference or portrait request without either trigger | Do not call an image-generation model automatically. Use the existing production route and treat uploaded images as references. |

On the image-source route, replace 3D modeling and physical-lighting production with the selected 2D source; retain Phase 3 Shader preview and Phases 4–6 Aseprite refinement and checks. Read [psap.md](psap.md) for the mandatory smoothing stage. This route does not require reconstructing the generated face in 3D. Never fabricate normals, depth, material IDs, or Q1/Q2 approvals for a 2D image.

For an existing Aseprite source that already passed through this Shader, continue editing it directly. Re-run preprocessing when its upstream image changes; do not repeatedly smooth the refined pixel artwork.

Record the triggering user text, source/provenance, selected route, whether a model was actually called, and the source -> Shader -> Aseprite artifact paths. Explicit user instructions about generation or preprocessing take precedence. Merely updating cards or discussing a model does not request image generation.

### Default Framing in Image-Generation Prompts

When image generation is authorized for a character portrait or dialogue avatar, include the following composition requirement in the generation or edit prompt. Explicit user framing requirements take precedence.

> Use a tight head-and-neck portrait composition. Let the head and visible neck occupy most of the frame, with only a small margin above the hair or headwear. Show just a narrow strip of the collar or upper garment along the bottom edge, with the shoulders, chest, and torso cropped out. Keep the face large and readable at the target pixel resolution.

## 1. Input Modes & Attribute Sources

| Input | Design approach |
|---|---|
| Brief text prompt | Preserve explicit requirements; fill necessary gaps with recorded design choices and explore different appearances where useful. |
| Detailed facial description | Split the description into independently checkable shape requirements; vary unspecified attributes. |
| Supplied portrait reference | Observe identity, proportions, framing, and visible lighting; record which changes are allowed. Follow the selected style's reference-study rules when applicable. |
| New expression or angle for an established character | Reuse the existing identity baseline and change the requested expression, pose, or view. |

Mark each attribute as **user-specified**, **style-default**, or **design-added**. User requirements take precedence. Do not present inferred traits as user instructions or invent measured reference proportions for a text-only character. Record material contradictions or unresolved requirements before committing the design.

## 2. Character Record & Shape Translation

Extend the existing [production task record](../../specs/production.md) with:
- Apparent age, face shape, hair, principal facial features, and distinctive marks.
- Expression, head orientation, gaze direction, and framing.
- Style, native dimensions, display container when known, and background treatment.
- Identity-critical features, permitted simplifications, and unresolved choices.

Translate words into visible shapes and relationships. Examples are design interpretations, not universal measurements:

| Description | Shape decisions to record |
|---|---|
| Long face / square jaw | Facial width-to-height relationship, jaw turns, chin width. |
| Narrow almond eyes | Eye-opening contour, lid coverage, corner direction. |
| Straight nose / broad nostrils | Bridge direction, projection, nose base and alar width. |
| Thin lips / closed mouth | Lip thickness, mouth seam, corner position. |
| Calm / alert | Combined brow tension, lid opening, gaze, and mouth corners. |
| Mark on the left brow | Character-relative side, projected location, and visibility under the chosen pose. |

Head direction and gaze are separate attributes. State whether left/right refers to the character or the viewer. Proportions depend on the character, age, pose, and style; do not prescribe universal landmark rows, eye widths, or mouth pixel counts.

## 3. Resolution & Feature Budget

- Select the native grid from user requirements, the intended container, framing, and feature readability, using the selected style's defaults where needed. Record native size separately from display exports.
- Check whether the essential eyes, mouth, hairstyle, and marks can survive at 1x. Adjust framing, native size, or the representation of a feature when it would fall below one pixel; record any simplification and unresolved loss of an explicit requirement.
- A screenshot's dimensions or an uncertain recovered grid do not establish an original native size. Integer enlargement is a display version and adds no authored detail.
- Choose existing palette families and useful tonal steps according to the selected style. Do not impose a universal total-color cap or a fixed skin ramp on every portrait.

## 4. Exploration & Identity Baseline

When the design is open, compare a small number of rough directions through face shape, hair silhouette, expression, and large value masses. For detailed prompts, hold explicit attributes fixed and vary open choices. Avoid polishing texture or tiny accessories before the design is resolved.

Use structural sketches or simplified Blender previews for exploration on the standard route. An image-generation tool is available only under Section 0's trigger. On that route, the selected generated image becomes the 2D source for the mandatory smooth Shader; raw generated images are not Aseprite production bases. Concepts are not evidence of user intent and cannot override explicit attributes.

Select and record a coherent design before detailed production. Preserve face proportions, hairline and hair silhouette, distinctive marks, apparent age, and character impression across later edits. User requirements remain authoritative if a concept contradicts them.

## 5. Phase Cards

1. [3D & Camera](3dac.md)
2. [Lighting & Render](lr.md)
3. [Style Pixel Shader Preview](psap.md)
4. [Aseprite Rough Draft](ard.md)
5. [Pixel Clusters, Details & Texture](pcdt.md)
6. [Final Visual Check & Delivery](fvc.md)

Keep task records, designs, generated concepts, previews, and working assets under `Test Workspace/<task-id>/`. Reuse the production record rather than creating parallel specification documents for each attribute. Review status, export requirements, and cleanup follow the production specification.
