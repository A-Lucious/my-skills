# Portraits: Final Visual Check & Delivery (fvc)

Focuses on prompt fidelity, emotional resonance, multi-scale readability, and technical validation.

## 1. Prompt Alignment Checklist
- Cross-check against the original text prompt item by item:
  - Apparent age and gender accurately reflected in facial structure?
  - Character expression/attitude (e.g. stoic, sarcastic, weary) clearly communicated?
  - Mandatory landmarks (scars, hair color, eye color) clearly distinct?

## 2. Multi-Scale UI Readability
- Inspect at native scale (1x) and common UI dialog scales (2x, 4x):
  - Does the face communicate character identity at an instant glance?
  - Are eyes and expressions sharp without blurriness?
  - Does the portrait frame sit harmoniously within character dialogue UI boxes?

## 3. Technical & Palette Compliance
- Verify palette compliance via the checker script:
  ```bash
  tools/aseprite-mcp/.venv/bin/python .agents/skills/pixel-art/scripts/check_palette.py \
    --style parchment-fantasy --asset-type portrait --families skin,hair,earth \
    "Test Workspace/exports/<id>-vNN.png"
  ```
- Confirm no orphan pixels, correct alpha (0 or 255), and clean edges against transparent or UI backgrounds.
