# Full-Body Characters: Final Visual Check & Delivery (fvc)

Focuses on silhouette recognition, grounded stance, animation readiness, and technical compliance.

## 1. Silhouette Readability at Distance
- Zoom out to native 1x scale and squint or view as pure black silhouette:
  - Is the class/archetype (e.g. heavy knight, agile rogue, robed wizard) recognizable from silhouette alone?
  - Are weapon poses and limb positions unmistakable?

## 2. Grounding & Anchoring
- Verify that feet have dark contact shadow pixels directly beneath them on the floor plane.
- The sprite should feel firmly grounded rather than floating in space.

## 3. Technical & Palette Compliance
- Verify palette compliance via the script:
  ```bash
  tools/aseprite-mcp/.venv/bin/python .agents/skills/pixel-art/scripts/check_palette.py \
    --style parchment-fantasy --asset-type battle_character --families <declared-families> \
    "Test Workspace/exports/<id>-vNN.png"
  ```
- Confirm canvas dimensions, transparent margins, and correct layer/tag packaging.
