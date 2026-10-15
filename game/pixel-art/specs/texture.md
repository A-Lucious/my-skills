# Pixel Clusters and Material Textures

Textures build upon clear silhouettes, material zoning, and major values, applied only as demanded by the material.

## Zones and Tonal Ramps

- Use material/component zoning, surface orientations, lighting groups, and working ramps; replace 3D zoning with planned pixel regions only when users explicitly waive 3D phases.
- Maintain isolated texture layers for comparison and pruning. Protect silhouettes, key components, thin metal trim, specular highlights, deep crevices, and cast shadow boundaries.
- Sample texture shades from adjacent steps within the material's active ramp; reduce contrast on shadow planes and minimize details in deep recesses.

## Direction and Density

- Convey material properties through coherent, non-uniform micro-clusters, preserving resting areas. Randomness applies strictly to cluster position, length, thickness, spacing, and localized density.
- Wood grain follows board perspective, structured via short strokes, small knots, and broken seams; metals use less wear with narrower highlights; cloth and leather textures follow folds and anatomical forms.
- Meaningful single-pixel scuffs or specular dots may be retained; eliminate uniform noise, repetitive patterns, cross-material/cross-plane textures, and functionless pale spots.
- Record seeds, algorithm versions, and coverage definitions for procedural textures to facilitate reproduction and comparison.

## Inspection Checklist

Subject and materials remain readable at native scale, under zoom, and in greyscale; textures do not fragment shadow boundaries; hierarchy between illuminated and shadow planes remains clear. Evaluate isolated pixel diagnostics by inspecting specific coordinates; diagonal staircasing can be cross-checked via read-only Moore neighborhood (8-connectivity) checks.

See [Wooden Chest Case](../references/cases/wooden-chest/case.md) for small wooden object test parameters. Choose density and cluster scale for other materials, dimensions, and categories based on current observations.
