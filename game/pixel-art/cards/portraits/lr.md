# Portraits: Lighting & Render Setup (lr)

Focuses on facial value distribution, directional shadows, anatomical cast shadows, and material ID passes.

## 1. Key Lighting & Value Hierarchy
- **Key Light:** Typically top-left (or top-right) 45° key light to establish clear facial values: illuminated forehead plane, nose ridge, and cheek crest.
- **Terminator Line:** Ensure the shadow line naturally tracks the turning edge of the cheekbone, temple, and jawline.
- **Ambient Fill:** Subtle fill light to keep the shadow-side eye socket and jaw edge readable against dark hair or background.

## 2. Critical Facial Cast Shadows
- **Brim/Hair -> Forehead:** Hair bangs or hood brims must cast a pronounced shadow band across the upper third of the forehead.
- **Nose -> Cheek & Philtrum:** The nose prism must cast a distinct triangular shadow on the turned cheek and upper lip zone.
- **Jaw -> Neck & Collar:** The jawline must cast a crisp shadow onto the neck and clothing collar, separating head and torso volumes.

## 3. Material & Part IDs
- Assign solid distinct base colors or material pass indices to:
  - Skin (face, ears, neck).
  - Hair / Headwear.
  - Clothing / Collar.
  - Background silhouette mask.
