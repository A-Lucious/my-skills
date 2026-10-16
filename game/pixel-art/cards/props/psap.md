# Props: Style Pixel Shader & Advance Preview (psap)

Focuses on resolution budgeting, shader execution, and cross-material bleed prevention.

## 1. Resolution Budgeting
- **Primary Grid:** Default to native **64x64** for complex inventory items, chest containers, and multi-part weapons to preserve face gradients, seams, and specular details.
- **Compact Grid:** Use **32x32** or **48x48** for hotbar icons, simple rings, or small flasks; simplify fine parts in 3D prior to execution to avoid pixel sampling noise.

## 2. Style Shader Execution
- Execute the style's fixed `pixel_shader.py` via Blender MCP.
- Use confirmed camera, lighting, and palette parameters; lock alpha to 0/255.

## 3. Sampling & Cross-Bleed Verification
- **Cross-Bleed Check:** Verify that small junctions (e.g. cork stopper touching bottle neck, metal latch meeting wood panel) exhibit 0 cross-family bleed pixels.
- **Component Retention:** Confirm that narrow components (latches, rim bands, handles) retain at least 1–2 contiguous pixels in width and are not dissolved into the background.
