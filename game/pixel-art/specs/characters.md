# Characters Specification

Applies to portraits, full-body characters, and creatures; the chosen style dictates proportions, exaggeration, and detail density.

## Task Inputs

Character identity, apparent age, expression or action, eye line and orientation, clothing/gear, and recognizable landmarks. Portraits specify head-and-shoulders framing; full-body characters specify grounding points and center of mass; creatures specify anatomical zoning and distinctive features.

## Design Principles

- **Portraits & Busts:** Establish continuous structural relationships across head orientation, brow, eye sockets, nose prism, jawline, neck, and collar before adding micro-details. Facial values convey anatomical volume (Asaro head planes). Never model individual eyelashes, eyeball spheres, or micro-nostrils in 3D; feature landmarks (iris, pupil, catchlight, scars, stubble) are placed in Aseprite.
- **Full-Body Characters:** Establish silhouette, center of mass, limb joints, and equipment occlusions first. Key landmarks like weapons, headwear, and wings must maintain legible shapes and negative space on the target grid. Radically simplify facial features in full-body sprites (omitting eyes and mouth).
- **3D Blockout:** Represents major anatomical masses, pose, and occlusion hierarchy; treat organic curves with appropriate anatomical volume. The pixel phase may moderately enlarge key landmarks like eyes, weapon tips, or hands for clarity.
- **Material Form & Occlusions:** Hair, cloth, skin, and metal follow their respective material rules in [cards/materials/](../cards/materials/). Critical occlusions include hair/hat brim -> forehead, nose -> cheek, jawline -> neck, and collar contacts.

## Inspection Checklist & References

Native resolution communicates identity, expression, or action; facial features and anatomical joints are structurally sound; apparent age, grounding, and gear layering are clear.

Select permissible references per [Reference Usage Rules](../styles/parchment-fantasy/reference-library/INDEX.md). For hooded portraits, check occlusion of the brim over the forehead and continuity of bridge-of-nose and cheek highlight blocks.
