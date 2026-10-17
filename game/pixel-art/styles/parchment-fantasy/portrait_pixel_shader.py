"""Smooth a 2D portrait inside Blender MCP, then reuse the fixed palette mapper.

No model invocation or Python raster writing. Importing this module has no scene
side effects. Derived from the tested area/Kuwahara portrait prototype 0.4.1.
"""
import hashlib
import json
import math
from pathlib import Path

import bpy

VERSION = "1.0.0"
SCRIPT = Path(__file__).resolve()
STYLE_SCRIPT = SCRIPT.with_name("pixel_shader.py")
PALETTE = SCRIPT.with_name("palette.json")


def _node(tree, kind, label):
    node = tree.nodes.new(kind)
    node.label = label
    return node


def _scale(tree, source, size):
    node = _node(tree, "CompositorNodeScale", f"Grid {size[0]}x{size[1]}")
    node.inputs["Type"].default_value = "Absolute"
    node.inputs["X"].default_value, node.inputs["Y"].default_value = size
    node.inputs["Interpolation"].default_value = "Bilinear"
    tree.links.new(source, node.inputs["Image"])
    return node.outputs["Image"]


def _colour_math(tree, operation, a, b):
    node = _node(tree, "ShaderNodeMixRGB", operation)
    node.blend_type = operation
    node.inputs[0].default_value = 1.0
    tree.links.new(a, node.inputs[1])
    if isinstance(b, tuple):
        node.inputs[2].default_value = b
    else:
        tree.links.new(b, node.inputs[2])
    return node.outputs[0]


def _area_sample(tree, source, input_size, target_size):
    """Regular 4x4 footprint approximation in linear RGB, using real nodes."""
    centered = _scale(tree, source, target_size)
    result = _colour_math(tree, "MULTIPLY", centered, (0, 0, 0, 1))
    for y in range(4):
        for x in range(4):
            move = _node(tree, "CompositorNodeTranslate", f"Footprint {x},{y}")
            move.inputs["X"].default_value = ((x + 0.5) / 4 - 0.5) * input_size[0] / target_size[0]
            move.inputs["Y"].default_value = ((y + 0.5) / 4 - 0.5) * input_size[1] / target_size[1]
            move.inputs["Interpolation"].default_value = "Bilinear"
            tree.links.new(source, move.inputs["Image"])
            result = _colour_math(tree, "ADD", result, _scale(tree, move.outputs["Image"], target_size))
    return _colour_math(tree, "MULTIPLY", result, (1 / 16, 1 / 16, 1 / 16, 1))


def _scene(name, size):
    scene = bpy.data.scenes.new(name)
    scene.use_fake_user = True
    camera_data = bpy.data.cameras.new(scene.name + "_CompositorOnlyCamera")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera  # Render trigger only; no portrait geometry or relighting.
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 1
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.filter_size = 0.01
    scene.render.dither_intensity = 0
    scene.render.use_sequencer = False
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "16"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.view_settings.use_curve_mapping = False
    scene.view_settings.use_white_balance = False
    return scene


def _image(path, *, mask=False):
    image = bpy.data.images.load(str(path), check_existing=False)
    image.colorspace_settings.name = "Non-Color" if mask else "sRGB"
    image.alpha_mode = "STRAIGHT"
    image.pack()
    return image


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_preview(input_image, *, output_dir, families, size=(64, 64),
                   smoothing=4.0, palette_colours=None, region_masks=()):
    """Export same-palette before/after, native base, packed .blend and manifest.

    smoothing is Kuwahara Size at the 4x working grid (4.0 is a conservative
    starting point, not a user-approved preset). region_masks optionally contains
    {image: path, families: [...]} for genuine native-size white-on-black 2D masks.
    palette_colours may select a subset of the declared locked family ramps.
    """
    if bpy.app.version < (5, 0, 0):
        raise RuntimeError("Requires Blender 5.x compositor API via Blender MCP.")
    if len(size) != 2 or any(type(n) is not int or n < 1 for n in size):
        raise ValueError("size must contain two positive integers.")
    if not isinstance(smoothing, (int, float)) or not math.isfinite(smoothing) or smoothing <= 0:
        raise ValueError("smoothing must be a positive finite working-grid radius.")
    palette = json.loads(PALETTE.read_text())
    if palette["style_id"] != "parchment-fantasy" or not palette["locked"]:
        raise ValueError("The locked Parchment Fantasy palette is required.")
    if (not families or len(set(families)) != len(families)
            or not set(families) <= set(palette["families"])
            or len(families) > palette["asset_family_limits"]["portrait"]):
        raise ValueError("Declare distinct portrait palette families within the style limit.")
    allowed = list(dict.fromkeys(c for f in families for c in palette["families"][f]["ramp"]))
    colours = list(dict.fromkeys(c.lower() for c in palette_colours)) if palette_colours is not None else allowed
    if not colours or not set(colours) <= set(allowed):
        raise ValueError("palette_colours must be a nonempty subset of the declared locked ramps.")
    source = Path(input_image).resolve(strict=True)
    output = Path(output_dir).resolve()
    workspace = (SCRIPT.parents[5] / "Test Workspace").resolve()
    if output == workspace or not output.is_relative_to(workspace):
        raise ValueError("Use a task/version output directory inside Test Workspace.")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("Choose a new empty task/version directory.")
    image = _image(source)
    if abs(image.size[0] / image.size[1] - size[0] / size[1]) > 0.001:
        raise ValueError("Prepare the intended matching-aspect crop via MCP first; do not stretch a face.")
    masks, mask_records = [], []
    for item in region_masks:
        path = Path(item["image"]).resolve(strict=True)
        group = item["families"]
        if not group or not set(group) <= set(families):
            raise ValueError("Each 2D mask must declare a subset of the active families.")
        mask_image = _image(path, mask=True)
        if tuple(mask_image.size) != tuple(size):
            raise ValueError("2D masks must match the native size.")
        ramp = {c for f in group for c in palette["families"][f]["ramp"]}
        subset = [c for c in colours if c in ramp]
        if not subset:
            raise ValueError("Each 2D mask needs at least one selected palette colour.")
        masks.append({"image": mask_image, "families": list(group), "colours": subset})
        mask_records.append({"source": str(path), "sha256": _sha(path), "families": list(group)})
    style = {"__file__": str(STYLE_SCRIPT), "__name__": "portrait_fixed_palette"}
    exec(compile(STYLE_SCRIPT.read_text(), str(STYLE_SCRIPT), "exec"), style)
    output.mkdir(parents=True, exist_ok=True)
    working = tuple(n * 4 for n in size)
    scenes, outputs = [], {}
    for smooth, stem in ((False, "before"), (True, "smooth")):
        scene = _scene(f"Portrait2D_{output.name}_{stem}", size)
        tree = bpy.data.node_groups.new(scene.name + "_Sampling", "CompositorNodeTree")
        tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        source_node = _node(tree, "CompositorNodeImage", "Selected 2D portrait; no relighting")
        source_node.image = image
        value = _area_sample(tree, source_node.outputs["Image"], tuple(image.size), working)
        if smooth:
            node = _node(tree, "CompositorNodeKuwahara", "Directional cluster smoothing")
            for key, val in {"Type": "Anisotropic", "Size": float(smoothing), "Uniformity": 4,
                             "Sharpness": 0.7, "Eccentricity": 1.0, "High Precision": True}.items():
                node.inputs[key].default_value = val
            tree.links.new(value, node.inputs["Image"])
            value = node.outputs["Image"]
        native = _area_sample(tree, value, working, size)
        end = _node(tree, "NodeGroupOutput", "Native input before locked palette")
        tree.links.new(native, end.inputs["Image"])
        scene.compositing_node_group = tree
        scene.render.use_compositing = True
        native_path = output / f"{stem}-native-input.png"
        scene.render.filepath = str(native_path)
        bpy.ops.render.render(write_still=True, scene=scene.name)
        mapped = _scene(scene.name + "_Palette", size)
        style["_compositor"](mapped, colours, _image(native_path), masks)
        mapped.render.image_settings.color_depth = "8"
        mapped_path = output / ("pixel-base-v01.png" if smooth else "before-native.png")
        mapped.render.filepath = str(mapped_path)
        bpy.ops.render.render(write_still=True, scene=mapped.name)
        scenes.extend([scene, mapped])
        outputs[stem + "_input"] = str(native_path)
        outputs["pixel" if smooth else "before"] = str(mapped_path)
    blend = output / "shader-preview.blend"
    bpy.data.libraries.write(str(blend), set(scenes), fake_user=True)
    outputs["blend"] = str(blend)
    manifest = {
        "shader": "parchment-fantasy-portrait-2d", "version": VERSION,
        "prototype_algorithm": "area/Kuwahara 0.4.1; no task-specific face or collar coordinates",
        "script_sha256": _sha(SCRIPT), "palette_mapper_version": style["VERSION"],
        "palette_mapper_sha256": _sha(STYLE_SCRIPT), "palette_version": palette["version"],
        "palette_sha256": _sha(PALETTE), "families": list(families), "colours": colours,
        "source": str(source), "source_sha256": _sha(source), "source_size": list(image.size),
        "input_type": "2D sRGB; lighting already in source", "size": list(size),
        "working_size": list(working), "samples_per_axis_per_stage": 4,
        "filter": {"type": "Anisotropic Kuwahara", "size_at_working_grid": smoothing,
                   "uniformity": 4, "sharpness": 0.7, "eccentricity": 1.0, "high_precision": True},
        "face_bypass": False, "eye_refinement": "Aseprite postprocessing",
        "region_masks_2d": mask_records, "alpha_threshold": 0.5,
        "blender": bpy.app.version_string, "outputs": outputs,
        "pixel_sha256": _sha(Path(outputs["pixel"])), "user_review": "pending",
    }
    manifest_path = output / "shader-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return {"status": "ok", "manifest": str(manifest_path), **outputs}
