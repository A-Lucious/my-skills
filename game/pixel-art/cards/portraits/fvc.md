# Portraits: Final Visual Check & Delivery (fvc)

Mount [Production Specification](../../specs/production.md). Evaluate the actual exported candidate against the original request and the recorded design baseline.

## 1. Independent Check Categories

| Category | Evidence required |
|---|---|
| Requirement alignment | Specified face shape, features, marks, expression, head direction, gaze, and framing are visibly represented; unresolved losses are listed. |
| Identity continuity | Face proportions, hairline, hair silhouette, distinctive marks, and apparent age remain coherent with the selected design or reference. |
| Structure & lighting | Features share a plausible perspective; facial planes retain volume; occlusion and light direction agree; jaw, neck, and shoulders connect. |
| Pixel expression | The portrait reads at 1x; clusters and details have a visible purpose; edges and material treatment follow the style. |
| Technical delivery | Canvas, palette families, alpha, editable source, layer visibility, and exported versions satisfy the task. |
| Route fidelity | Any image-model call has the design card's user trigger; an image-source base passed through the smooth Pixel Shader before Aseprite; import path/hash matches that output. |

For text-only work, check explicit attributes individually with visible evidence: which brow carries the mark, where the eyes look, whether the lips are closed, and how the specified face shape is represented. Design-added traits must not become invented user requirements.

## 2. Visual Evidence & Metrics

- Inspect native 1x, integer zoom, greyscale, and the intended display container when known. Use matching framing and scale for reference or version comparisons.
- Compare the final portrait to the fixed design baseline, and use reference-image comparisons when an actual reference exists. A text-only task has no reference silhouette or ground-truth pixel map to score against.
- Silhouette overlap can diagnose outer shape; matching a shared construction guide proves execution consistency only. Histograms, regional means, color counts, or landmark coordinates alone do not establish identity, expression, or anatomical volume.
- Automated image-question answers and pixel diagnostics can guide inspection but cannot substitute for viewing the exported portrait.

## 3. Revisions & Completion

Prioritize the few defects most damaging to identity, structure, volume, or expression. On the 3D route, send shape/pose to Phase 1 and illumination to Phase 2. On the image-source route, revise the selected source/design when necessary and re-run its Shader; do not introduce a model call without the design card's trigger. Send mapping/smoothing to Phase 3 and cluster/detail placement to Phases 4–5. Preserve comparable before/after previews and reopen affected checks.

If the native grid cannot express a required feature, reassess framing, dimensions, or representation and record the limitation. If progress stalls, report the unresolved defect and the needed design/tool change; do not relabel the candidate as complete. Correct demonstrably faulty checks with evidence and re-evaluate affected versions rather than weakening criteria to fit one image.

Completion requires explicit requirements to be met, no unresolved major structure or lighting defects, native-size readability, and successful technical checks. Keep technical results, visual self-checks, and user acceptance separate under the existing production status rules. Deliver unresolved work as a candidate with its defects listed.

## 4. Source, Exports & Cleanup

- Run the existing palette validation script with the task's style, declared families, portrait purpose code, and all production PNGs. For Parchment Fantasy use `--asset-type portrait`; read family limits from its active palette rather than hardcoding a cap here.
- Verify the `.aseprite` canvas and editable content, hide reference/guide layers in exports, and check that the native PNG matches the source composition.
- Verify scale=1 native export, intended background/alpha, and any integer-scaled display version. When such a version is specified, confirm exact nearest-neighbor enlargement of the native; non-integer container scaling needs visual inspection.
- Retain the editable source, native PNG, required display/cutout versions, essential previews, and concise character/check record in `Test Workspace/`. Follow production cleanup and game-integration rules.
