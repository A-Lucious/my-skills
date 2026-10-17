# Portraits: 3D Modeling & Camera Setup (3dac)

Read after [Portrait Design](design.md). Establish believable head structure and the chosen character's proportions at the target grid.

This card applies to the standard 3D route. For the design card's conditional image-source route, record the selected 2D source and framing, then proceed to [Shader preprocessing](psap.md); do not construct a replacement head or claim a 3D structural review.

## 1. Major Anatomical Masses

- Model the cranium, jaw and chin, brow and eye sockets, nose prism, cheek planes, ears, neck, and visible shoulders through Blender MCP. Let the required view and native grid determine geometric detail.
- Refine face length, jaw width, eye-opening shape and spacing, nose projection and base, and mouth-region volume according to the character record. A generic sphere-and-box blockout is an initial construction, not sufficient evidence that detailed facial requirements are satisfied.
- Model hair volume and hairline around the skull, separating large locks, headwear, and other identity-critical silhouettes.
- Keep iris, pupil, catchlight, scar marks, stubble, and other pixel-scale features for Aseprite. Avoid individual eyelashes, detailed eyeball spheres, and micro-nostril geometry; record placement anchors for later detail work.

## 2. Camera, Gaze & Framing

- Set the requested yaw, pitch, and roll, with a camera projection appropriate to the style and intended view. Do not force every portrait into the same three-quarter pose.
- Preserve the distinction between head direction and intended gaze. Record facial anchors needed to place the eyes later.
- Inspect the perspective of the brow, eyes, nose base, mouth, and ear together. Near and far features must agree with the same head orientation.
- Frame the head, neck, and shoulders for the delivery container. Preserve requested crops; do not automatically add margins or shrink the face.

## 3. Structural Check

Inspect the target-angle model and native-size silhouette. Verify face shape, anatomical continuity from jaw to neck and shoulders, hair volume, and visibility of important features. Record task-specific proportions, projected landmarks, and occlusions rather than copying coordinates from another portrait.

Correct structural problems here before lighting or micro-detail. Save the `.blend`, target-angle preview, native silhouette, and structural baseline through the existing workflow (Q1).
