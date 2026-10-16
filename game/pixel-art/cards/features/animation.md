# Feature Card: Sprite Animation

Focuses on keyframe anchors, motion rhythm, shared lighting, and loop validation.

## 1. Multi-Pose 3D Alignment & Shared Lighting
- Establish key poses in 3D (idle, walk, strike) sharing identical world lighting and camera orientation.
- Lock anchor points (e.g. root bone / grounded foot coordinates) across all frames.

## 2. Base Rendering & Frame-by-Frame Import
- Render per-pose native bases via fixed style shader.
- Import into Aseprite as sequential frames with consistent canvas dimensions and layer structure.

## 3. Motion Rhythm & Pixel Continuity
- Maintain volume consistency: limbs and gear should not inflate or deflate between adjacent frames.
- Anchor stationary points (e.g. feet on ground during stance phases) to prevent ground sliding.
- Avoid erratic single-pixel jitter on high-frequency details.

## 4. Loop Verification
- Use Aseprite MCP tools:
  - `validate_loop` to confirm smooth, seamless playback without unintended duplicate frames or stutter.
  - `diff_sprites` to verify frame-by-frame deltas and ensure motion changes carry clear gameplay semantics.
