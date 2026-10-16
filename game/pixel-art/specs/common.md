# Common Pixel Specifications

Fundamental rules for all pixel art assets regardless of category or style.

## 1. Pixel Grid & Staircasing Discipline
- **Native Grid Integrity:** All assets must be authored and inspected on their true 1x native pixel grid. Pre-upscaling or fractional scaling during authoring is strictly prohibited.
- **Rhythmic Staircasing:** Curved and diagonal contours must follow intentional, consistent staircasing patterns (e.g. 1-1-2-2-3 or 3-2-2-1-1). Avoid erratic single-step jumps that create "jaggies".
- **Eliminate Artifacts:**
  - *Doubles / Banding:* Remove accidental 2-pixel thick corner clusters on single-pixel outlines.
  - *Stray Pixels:* Clean isolated, disconnected single pixels unless deliberately serving as catchlights or specular glints.
  - *Over-Dithering:* Forbid noisy checkerboard patterns on small surfaces; prioritize solid color masses and organized pixel clusters.

## 2. Forms, Landmarks & Negative Space
- Major forms and recognizable landmarks must hold at native resolution; fine details are always subordinate to primary masses.
- When abstracting 3D geometry into pixels, deliberate landmark exaggeration (e.g. enlarging weapon tips, eye catchlights, or buckles by 1 pixel) is permitted to ensure readability.
- Clear negative space between overlapping parts is mandatory.

## 3. Fixed Palette & Family Budgeting
- **Color Family Principle:** A set of tonal shades progressing from dark to light for a specific material constitutes one color family. Multiple materials may share a family.
- All pixel painting must stay within declared families defined in `palette.json`.
- Alpha policy: strict binary alpha (0 or 255) for all sprite outputs.
