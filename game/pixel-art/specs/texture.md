# Pixel Clusters & Texture Specification

Defines general principles for micro-cluster organization, density control, and layer isolation. Specific material behaviors are defined in `cards/materials/`.

## 1. Pixel Clusters Principles
- **Subordination:** Textures must remain subordinate to primary silhouettes, material zoning, and major values. Never apply texture across light/shadow boundaries.
- **Micro-Cluster Organization:** Texture pixels must form coherent, non-uniform micro-shapes (2–4 pixels in length or small clusters). Eliminate uniform noise, grid-like hatching, and functionless single-pixel speckles.
- **Resting Space:** Protect resting zones; high-density texture over an entire surface creates visual fatigue. Keep overall texture pixel coverage typically between **5%–8%** of the material area.

## 2. Layer Isolation & Protected Zones
- Maintain isolated texture layers in `.aseprite` to enable quick toggling, inspection, and pruning.
- **Protected Zones:** Outer silhouettes, major landmark bevels, primary specular highlights, contact crevice shadows, and cast shadow boundaries must be kept free of texture interruptions.

## 3. Direction & Tonal Sampling
- Texture strokes must follow the planar perspective and contour curvature of the underlying geometry.
- Sample texture pixels strictly from adjacent tonal steps within the material's active palette ramp; never introduce high-contrast foreign colors for surface textures.

## 4. Inspection Checklist
- Check sprite at 1x native resolution, integer zoom (4x/8x), and in greyscale:
  - Textures enhance material identity without breaking form.
  - No accidental doubles or staircasing breaks along critical contour edges.
