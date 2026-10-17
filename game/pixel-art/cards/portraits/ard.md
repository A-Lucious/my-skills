# Portraits: Aseprite Rough Draft (ard)

Mount the selected style's palette and [Common Specifications](../../specs/common.md). Establish readable identity and facial volume before micro-detail.

## 1. Import & Editable Structure

Import the exact Phase 3 native PNG through Aseprite MCP. Preserve an untouched, hidden-on-export `base-ref` layer and duplicate it into an active `draft`. Add editable layers for hair, skin, clothing, or details when they make revisions clearer; do not require empty layers merely to match a template.

For the conditional image-source route, this must be the smooth Shader output, not the raw generated image or a separately resized copy. Record its path/hash with the import. Preserve visible 2D planes and shadows; consult normals/depth only when actual 3D guidance exists.

Keep a same-scale base/draft comparison. Importing or resaving the image alone is not a rough-draft improvement.

## 2. Large Forms & Value Clusters

- Resolve face and hair silhouette, hairline, neck, collar, and material zones first.
- Consolidate render fragments into forehead, eye-socket, nose, cheek, jaw, and neck light/shadow masses. Preserve the guidance's turning planes and contact shadows.
- Retain character-specific feature spacing and pose. Moderately adjust landmarks for pixel readability without changing the specified face shape, age, or expression.
- Use useful tonal steps from the declared style families. Do not flatten facial volume to satisfy an arbitrary total-color count.

## 3. Rough-Draft Check

At 1x and in greyscale, verify that facial proportions, head direction, hair silhouette, and major volume hold without micro-detail. Place simple eye and mouth anchors when needed to judge expression; texture must not carry the likeness.

Rework silhouette or large value masses before detailing. Record deliberate changes from the Blender base and unresolved identity or feature losses (Q4).

Recheck exported pixel data after palette or color-mode conversions; ensure transparency-index behavior has not silently changed opaque pixels. Indexed conversion and RGB round-tripping are not required merely to demonstrate palette compliance.
