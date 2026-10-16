# Props: Final Visual Check & Delivery (fvc)

Focuses on slot legibility, canvas margins, palette validation, and export packaging.

## 1. Inventory & Slot Legibility
- Inspect the asset at native 1x scale and in-game container UI scales (2x, 4x):
  - Is the item instantly recognizable as its intended archetype (e.g. "opened chest", "health potion", "broadsword")?
  - Does the silhouette pop against dark, neutral, and paper-textured UI backgrounds?

## 2. Canvas Margins & Grounding
- Confirm safety margins of 2–4 pixels on all sides to prevent UI clipping.
- Ensure ground cast shadows taper smoothly within the bounds of the canvas rather than clipping bluntly at the bottom edge.

## 3. Technical & Palette Compliance
- Run the automated palette verification script:
  ```bash
  tools/aseprite-mcp/.venv/bin/python .agents/skills/pixel-art/scripts/check_palette.py \
    --style parchment-fantasy --asset-type prop --families <declared-families> \
    "Test Workspace/exports/<id>-vNN.png"
  ```
- Verify zero stray pixels, correct alpha (0 or 255), and that family counts adhere to the style budget.
