# Lighting Specification

## Lighting Setup

The task card must specify key light screen direction, elevation, softness/hardness, ambient fill, primary occluders, and shadow receivers. Use style defaults; if unspecified, choose a single key light that clarifies form and record it. Record secondary lights by position, range, and relative intensity. Flat or silhouette assets must also complete Blender lighting renders in the workflow while preserving target aesthetics; only when prompts explicitly waive lighting may "no volumetric lighting" be recorded with verbatim quotes.

3D guidance and pixel drafts must share identical light directions and coordinate frames. When normals and occlusion signals exist, structure major values accordingly; boundaries resulting from pixel discretization must still follow anatomical forms.

Shader preview comparisons must align with the source render's AgX/Look/exposure and output color space; do not compare raw AgX renders against pixel drafts subjected to differing display transforms or brightening curves while claiming value consistency. Inspect greyscale values and representative pixel samples across illuminated, shadow, and specular points; tonal quantization may merge continuous values but must not introduce pitch-black planes absent from the original or exaggerate contrast. Correct color mapping before modifying actual scene lights.

## Value Relationships

| Role | Success Criteria |
|---|---|
| Local Color (Albedo) | Communicates material identity, evaluated independently of illumination level. |
| Form Shadow | Shifts as surfaces turn away from light; boundaries trace geometric turning edges. |
| Cast Shadow | Clearly traces occluder, receiving surface, and light direction; shape conforms to receiver plane. |
| Contact Shadow | Concentrated along joints, seams, and tight occlusions; diminishes away from contact points. |
| Illuminated Face & Highlight | Broad illuminated planes indicate surface orientation; localized specular fits material reflectivity. |

Cloth and leather use broad, restrained illuminated planes; metals and gems use sharp, narrow highlights. Major planes for every material must express volume in greyscale, with light and dark masses serving clear semantic purposes. Ground shadows require visible receiving surfaces; canvas margins must preserve design-critical cast shadows in full.

## Final Value Re-Check

Major values established during the rough draft phase must be re-checked after detail passes across forms, cast shadows, contact shadows, and highlights, repairing areas fragmented or washed out by textures. Maintain valid relationships, log defects and corrections in task records, and inspect updated previews.

Re-evaluate affected lighting whenever silhouettes, poses, occluders, or light emitters change. Animation frames share world light sources, adapting shadows to poses; emissive objects must also be checked for localized illumination on neighboring surfaces. Flat assets verify readability of color blocks and occlusions.
