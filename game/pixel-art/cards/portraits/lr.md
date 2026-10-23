# Portraits: Lighting & Render Setup (lr)

For the standard 3D route, sample native geometry and run structural Sobel/mask preparation before the lighting bake. Use the sole [structural production baseline](../../styles/parchment-fantasy/PIXEL-SHADER.md).

Mount [Lighting Specification](../../specs/lighting.md) and use the structural baseline from [3D & Camera](3dac.md).

This card applies to the standard 3D route. The conditional image-source route preserves the selected image's visible lighting and proceeds to [Shader preprocessing](psap.md). Record the visible value structure, without inventing physical lights or geometry guidance.

## 1. Facial Volume & Light Direction

- Use the requested lighting, visible reference lighting, or selected style defaults. Record key direction, elevation, softness, and ambient fill.
- Establish readable light and shadow masses across the forehead, eye sockets, nose front and side, cheek planes, chin, jaw, and neck. Lighting should explain the chosen anatomy without erasing identity-critical features.
- Keep fill strong enough to preserve necessary shadow-side features while retaining facial volume. Distinguish local skin/hair color from the darkness caused by lighting.

## 2. Occlusion & Contact

Check relevant occluder/receiver pairs: fringe or headwear -> forehead, nose -> cheek, hair -> ear, jaw -> neck, and collar -> neck. Match each shadow to the real light direction and receiving surface; do not simulate depth with arbitrary dark outlines.

Separate skin, hair, cloth, and accessories in actual part/material guidance. Set material-family ownership from the selected palette, including dark facial details where applicable.

## 3. Value Check & Guidance

View the lighted head in greyscale without surface texture or tiny facial marks. The brow, nose, cheek, jaw, and neck should still describe a coherent face. Correct large value masses before adding detail.

Export the actual color render, alpha, IDs, normals, and depth through Blender MCP, with lighting parameters and guidance definitions. Preserve consistent camera and color management for the Shader comparison (Q2).
