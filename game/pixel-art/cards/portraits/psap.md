# Portraits: Style Pixel Shader & Advance Preview (psap)

Focuses on portrait resolution standards, shader quantization, and facial value stability.

## 1. Portrait Resolution Standards
- **Standard Bust:** Default to **64x64** for character dialogues, party portraits, and status screens.
- **Detailed Avatar:** Use **96x96** for hero splash dialogs or major NPC portraits.
- **Compact Icon:** Use **48x48** for compact status bars (requires extra structural simplification in 3D).

## 2. Style Shader Output Inspection
- Run `pixel_shader.py` via Blender MCP and evaluate the resulting native PNG:
  - **Head Plane Stability:** Confirm that the forehead, nose ridge, cheekbones, and jawline retain distinct, contiguous value masses without dithering noise.
  - **Color Bleeding:** Ensure hair color does not bleed into forehead skin tones across the boundary line.
  - **Eye Wells:** The eye socket zones should appear as clean, unified shadow clusters ready for Aseprite feature placement.
