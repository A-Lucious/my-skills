# Props: 3D Modeling & Camera Setup (3dac)

Focuses on physical structure, assembly relationships, internal volume, and viewing angle clarity.

## 1. Geometric Assembly & Volume
- **Containers (Chests, Jars, Pouches):** Must model realistic wall thickness and internal cavities. For open containers, set the lid/opening angle between 25°–45°; avoid direct top-down views (which lose wall thickness) or strict horizontal views (which occlude the interior cavity).
- **Multi-Part Equipment:** Explicitly distinguish structural components:
  - *Chests:* Body, hinged lid, latch/clasp, reinforced corner metal bands.
  - *Potion Bottles:* Stopper (cork/crystal), neck rim/flange, bottle neck leather strap, glass body curvature, and fluid surface.
  - *Books/Scrolls:* Cover boards, spine, paper text block thickness, ribbon bookmarks, and corner clasps.
  - *Weapons/Tools:* Blade/head, guard/crossbar, handle grip, and pommel/counterweight; establish distinct connection axes or deliberate offsets.

## 2. Perspective & Camera
- **Angle Selection:** Prioritize 3/4 isometric or dimetric angles (e.g. 30°–45° tilt) so top, front, and side faces are visible simultaneously to communicate three-dimensional volume.
- **Focal Length:** Use orthographic or long-focus perspective (85mm–120mm equivalent) to eliminate perspective distortion and maintain legible component proportions.

## 3. Native Grid Silhouette Check
- Check silhouette negative space at target pixel resolution (e.g., 64x64 or 32x32).
- Ensure critical landmarks (latches, handles, bottle necks, blade tips) do not merge into single indistinguishable blobs; adjust component gaps or enlarge narrow parts in 3D when necessary.
