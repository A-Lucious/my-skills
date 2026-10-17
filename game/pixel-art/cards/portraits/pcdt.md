# Portraits: Pixel Clusters, Details & Texture (pcdt)

Mount [Skin](../materials/skin.md), other applicable material cards, and [Texture Specification](../../specs/texture.md), interpreted through the selected style. Work on editable detail layers above the established masses.

## 1. Facial Features & Expression

For the image-source route, eye cleanup happens here after the smooth Shader: simplify fragmented eye shading into deliberate lids, iris/pupil, and justified highlights on editable layers. Inspect gaze and expression at 1x. Do not paste the unfiltered source eyes back over the smoothed base.

- Eyes: coordinate lids, eye opening, pupil/iris, and any justified catchlight. Preserve intended gaze and the near/far relationship; do not force identical eyes or catchlights into every portrait.
- Nose: express bridge, side plane, tip, and nostril/alar cues through neighboring clusters. Avoid replacing the entire nose volume with a bright vertical stripe and a dark hook.
- Mouth: preserve lip thickness, seam shape, corner placement, and expression. Do not prescribe one horizontal pixel line for every mouth.
- Ears, scars, freckles, facial hair, and other marks: place according to the character record, pose, and native feature budget. Distinguish a requested mark from accidental noise.
- Hair: refine the silhouette and a few large directional locks before individual strands. Eyebrows, fringe, and face shading should remain distinguishable where the design requires it.

## 2. Cluster & Edge Refinement

Clean jaggies, accidental banding, broken contours, and meaningless stray pixels while respecting the intended shape. Curve rhythm follows the contour; avoid applying a universal run-length sequence to every facial feature.

Purposeful single pixels may serve pupils, marks, strand tips, or highlights when they visibly improve the portrait. Treat isolated-pixel and short-run detections as diagnostics requiring visual inspection. A coordinate declaration alone does not make a noisy pixel useful; automated cleanup must preserve intended facial marks.

## 3. Texture & Final Values

Use restrained material detail. Do not substitute skin noise, uniform dithering, repeated hair strokes, or cloth speckle for anatomical structure. Requested age cues or facial hair should have deliberate shape and density.

Toggle detail layers off and compare before/after color and greyscale views. Repair fragmented cheek planes, lost nose volume, weakened jaw/neck separation, or an expression changed by detail placement. Recheck the palette and affected lighting/structure after substantive edits.
