# Lighting Specification

Defines core illumination physics, value hierarchies, occlusion relationships, and post-detail verification. Material-specific light reactions are defined in `cards/materials/`.

## 1. Core Lighting Setup
- **Lighting Rig:** The task card must record key light screen direction, elevation, softness/hardness, and ambient fill intensity. Defaults to top-left 45° key light unless task requirements specify otherwise.
- **Shared Light Coherence:** 3D guidance, shader renders, and pixel drafts must share identical light directions and coordinate frames.
- **Color Mapping Integrity:** Shader comparisons must maintain consistent AgX/Look/exposure settings; tonal quantization may group values but must not create unmotivated pitch-black voids or blown-out highlights.

## 2. Value Hierarchy & Shadow Classification

| Role | Success Criteria |
|---|---|
| **Illuminated Face (Highlight/Midtone)** | Broad planes indicating surface orientation toward the key light. Specular size follows material cards (`cards/materials/`). |
| **Form Shadow (Terminator)** | Shifts naturally as geometry turns away from light; follows surface curvature and anatomical turning edges. |
| **Cast Shadow** | Unambiguously traces occluder geometry, receiving surface, and light ray vector. |
| **Contact Shadow (Ambient Occlusion)** | Deep, narrow dark crevices along seams, joint intersections, and ground contacts. |

## 3. Grounding & Cast Shadow Margins
- Ground contact shadows require an unbroken receiving surface to ground the object.
- Design-critical cast shadows must remain unclipped within the canvas boundaries.

## 4. Final Value Re-Check
- After completing detail passes in Step 5, switch to greyscale view to verify:
  - Added textures and highlights have not disrupted major plane separation.
  - Shadow masses remain unified and legible.
  - Contact shadows retain depth without bleeding into illuminated planes.
