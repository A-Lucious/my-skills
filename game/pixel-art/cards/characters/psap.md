# Full-Body Characters: Style Pixel Shader & Advance Preview (psap)

Focuses on sprite scale budgeting, limb connectivity, and weapon edge integrity.

## 1. Scale Budgeting
- **Combat Sprite / In-World Character:** Standard native canvas is **64x64** (or **48x48** for classic grids).
- **Large Boss / Creature:** Use **96x96** or **128x128**.

## 2. Integrity of Slender Elements
- **Limb Continuity:** Confirm that slender limbs (wrists, ankles, calves) retain at least 2 pixels thickness and do not break into discontinuous islands.
- **Weapon & Stave Shafts:** Check that spear shafts, bows, or sword blades do not disintegrate into dotted noise during shader quantization; thicken in 3D if needed before proceeding.
