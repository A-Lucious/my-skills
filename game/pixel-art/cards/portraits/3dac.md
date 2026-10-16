# Portraits: 3D Modeling & Camera Setup (3dac)

Focuses on head planes, anatomical proportions, proxy hair/clothing volumes, and viewing angles.

## 1. Planes of the Head (Asaro Head Logic)
- **Extreme Low-Poly Mesh:** Use flat-shaded polygon planes (~150–300 triangles total). Do NOT use subdivision surface or smooth shading.
- **Key Anatomical Masses:**
  - *Forehead & Temples:* Distinct front plane and side temple planes.
  - *Eye Sockets:* Recessed polygon cavities to establish deep shadow wells.
  - *Nose Structure:* 3-plane prism (top ridge, side slopes, and underside).
  - *Cheekbones & Jaw:* Angular zygomatic arches and jawline tailored to character age/gender (broad jaw for rugged warriors, tapered chin for youthful characters).
- **STRICT PROHIBITION:** Do NOT model individual eyelashes, eyeball spheres, micro-nostrils, or lip contours in 3D. Micro-features downsample into muddy noise at low resolutions.

## 2. Hair, Hoods & Collar Proxy Volumes
- Model hair and headwear as simple geometric shell proxies (extruded cubes, simplified bevel curves, or smooth low-poly spheres).
- Shells must have solid physical depth to cast realistic occluding shadows onto the forehead, temples, and neck.

## 3. Framing & Camera
- Frame as a head-and-shoulders bust (typically leaving space for neck, collar, and shoulders).
- Use a slight 3/4 angle (15°–30° yaw) with a 85mm–100mm equivalent lens or orthographic camera to reveal both facial depth and profile contours without wide-angle distortion.
