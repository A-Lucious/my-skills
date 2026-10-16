# Portraits: Aseprite Rough Draft (ard)

Focuses on bringing facial features to life: palette convergence, landmark placement, eyes, eyebrows, and expression.

## 1. Import & Palette Convergence
- Import the native PNG via Aseprite MCP, preserving the base reference layer and working on a duplicated draft layer.
- Map the skin tone gradient strictly to the 4–6 tone `skin` family in `palette.json`; map hair to `hair` or `neutral` ramps.

## 2. Facial Landmark Placement (The Soul of the Portrait)
In 64x64, facial features rely on precise, deliberate pixel placement rather than photographic rendering:
- **Eyes & Gaze:**
  - Locate the eye within the 3D-generated socket shadow well.
  - Place 1–2 pixels for sclera (off-white/cream, avoiding stark 255 pure white).
  - Place iris/pupil pixels matching the prompt description (e.g. gray-blue, hazel).
  - Add a single pure-white or pale-cream catchlight pixel on the key-light side of the iris to bring the eyes to life.
- **Eyebrows & Expression:**
  - Draw 1–2 pixel wide eyebrow arches tracking the brow ridge. Angle and arch determine personality: furrowed inward for intense/grim, arched for inquisitive/arrogant, straight for stoic.
- **Nose Structure:**
  - Simplify the 3D nose into a sharp 1–2 pixel highlight dot on the tip/bridge, paired with a dark pixel cluster for the under-nose shadow. Avoid drawing a harsh dark outline along the full bridge.
- **Lips & Mouth:**
  - Define mouth expression with a dark 2–4 pixel line for the lip fissure (neutral, smirking, or downturned). Add a soft illuminated pixel on the lower lip crest.
