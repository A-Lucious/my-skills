# Portraits: Pixel Clusters, Details & Texture (pcdt)

Focuses on fulfilling micro-prompt features, hair cluster flow, skin restraint, and value coherence.

## 1. Fulfilling Prompt Specifics
- **Scars & Marks:** Draw scars with a dark furrow pixel pair flanked by a light highlight pixel along the illuminated edge, conforming to facial curvature.
- **Moles & Freckles:** Single isolated dark brown skin pixels placed deliberately according to the prompt.
- **Beard & Stubble:** Use subtle dithered dots from the dark skin ramp or hair shadow ramp along the jaw and upper lip.

## 2. Hair Cluster Flow
- Break down the 3D proxy hair into directional pixel strands (clusters 2–3 pixels wide).
- Place specular highlights across the crown following hair flow; avoid noisy, single-pixel checkerboards.

## 3. Facial Contour Cleanup
- Smooth the jawline, chin silhouette, and neck transitions, ensuring single-pixel thickness along curves (eliminating doubles and staircasing jumps).
- Maintain soft, solid skin color planes; **strictly forbid heavy checkerboard dithering on facial cheeks** to keep skin youthful and readable.

## 4. Value Balance Re-Check
- Toggle to greyscale view. Ensure the added eyes, lips, and hair strands do not disrupt the overall head volume established in Step 2.
