# Full-Body Characters: Lighting & Render Setup (lr)

Focuses on whole-body value consistency, equipment cast shadows, and ground shadow anchors.

## 1. Unified Light Direction
- Ensure light direction is consistent across all anatomy and gear (from helmet crest down to boots).
- Highlight plane hierarchy: upper shoulders, chestplate crest, and forward leg catch the strongest light.

## 2. Equipment Occlusions & Cast Shadows
- **Torso/Cloak -> Legs:** Large armor plates or cloaks must cast pronounced shadows across the underlying trousers and legs.
- **Weapons -> Body:** Two-handed weapons or shields must cast directional contact shadows onto the chest or arm.
- **Foot Contact Shadows:** Render small, dark contact patches underneath both boots to firmly anchor the character to the game world plane.

## 3. Material Pass Indexing
- Distinguish major material families: flesh/skin, plate armor/metal, cloth tunic, leather boots/straps, and weapon blades.
