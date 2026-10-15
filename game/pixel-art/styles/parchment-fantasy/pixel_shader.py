"""Parchment Fantasy Pixel Shader v1.3.0, executed inside Blender through Blender MCP.

Screen-space compositor: native grid -> nearest locked palette colour -> hard alpha.
Materials, geometry, active camera and lights are shared read-only with the source.
Loading this module does not change the scene or render anything.
"""

import hashlib
import json
from pathlib import Path

import bpy

VERSION = "1.3.0"
STYLE_ID = "parchment-fantasy"
DEFAULT_SIZE = (64, 64)
ALPHA_THRESHOLD = 0.5
FILTER_SIZE = 0.01
LIGHTNESS_WEIGHT = 2.0
RGB_TO_LMS = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)
LMS_TO_OKLAB = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)
SCRIPT_PATH = Path(__file__).resolve()
PALETTE_PATH = SCRIPT_PATH.with_name("palette.json")


def _linear(hex_colour):
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                 for c in rgb) + (1.0,)


def _node(tree, kind, label, location):
    node = tree.nodes.new(kind)
    node.label = label
    node.location = location
    return node


def _oklab(rgb):
    """Palette metadata only. Public-domain Oklab matrices by Bjorn Ottosson."""
    lms = [sum(a * b for a, b in zip(rgb, row)) ** (1 / 3) for row in RGB_TO_LMS]
    return tuple(sum(a * b for a, b in zip(lms, row)) for row in LMS_TO_OKLAB)


def _material_masks(scene, size, families, material_families, output):
    """Query true Blender geometry; identity masks never substitute for lighting.

    One ray at each native pixel centre classifies the first visible surface.
    For transparent materials the caller must declare families for that front
    surface, including transmitted colours it wants to allow.
    """
    if not material_families:
        return []
    from mathutils import Vector

    palette = json.loads(PALETTE_PATH.read_text())
    for material, allowed in material_families.items():
        if material not in bpy.data.materials or not allowed or not set(allowed) <= set(families):
            raise ValueError(f"Invalid material family assignment: {material!r}.")
    groups = list(dict.fromkeys(tuple(allowed) for allowed in material_families.values()))
    width, height = size
    camera = scene.camera
    frame = camera.data.view_frame(scene=scene)
    left, right = min(p.x for p in frame), max(p.x for p in frame)
    bottom, top = min(p.y for p in frame), max(p.y for p in frame)
    plane_z = frame[0].z
    matrix = camera.matrix_world
    rotation = matrix.to_3x3()
    with bpy.context.temp_override(scene=scene):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        records = []
        pixels = [[0.0] * (width * height) for _ in groups]
        for y in range(height):
            for x in range(width):
                point = Vector((left + (x + 0.5) * (right - left) / width,
                                top - (y + 0.5) * (top - bottom) / height, plane_z))
                if camera.data.type == 'ORTHO':
                    origin = matrix @ point
                    direction = (rotation @ Vector((0, 0, -1))).normalized()
                elif camera.data.type == 'PERSP':
                    origin = matrix.translation.copy()
                    direction = (rotation @ point).normalized()
                else:
                    raise ValueError("Material masks support perspective and orthographic cameras.")
                hit, position, normal, face, obj, _ = scene.ray_cast(
                    depsgraph, origin, direction, distance=camera.data.clip_end)
                if not hit:
                    continue
                evaluated = obj.evaluated_get(depsgraph)
                slot = evaluated.data.polygons[face].material_index
                material = evaluated.data.materials[slot].name if slot < len(evaluated.data.materials) else None
                allowed = material_families.get(material)
                if allowed:
                    group = groups.index(tuple(allowed))
                    pixels[group][(height - y - 1) * width + x] = 1.0
                records.append({'xy': [x, y], 'object': obj.name, 'material': material,
                                'families': allowed, 'position_world': list(position),
                                'normal_world': list(normal), 'ray_distance': (position - origin).length})
    masks = []
    for index, group in enumerate(groups):
        image = bpy.data.images.new(f"Parchment Fantasy material mask {index + 1}", width, height, alpha=False)
        image.colorspace_settings.name = 'Non-Color'
        image.pixels.foreach_set([channel for value in pixels[index] for channel in (value, value, value, 1.0)])
        image.filepath_raw = str(output / f"material-mask-{index + 1}.png")
        image.file_format = 'PNG'
        image.save()
        image.pack()
        colours = list(dict.fromkeys(c for family in group for c in palette['families'][family]['ramp']))
        masks.append({'families': list(group), 'colours': colours, 'image': image})
    (output / 'surface-guidance.json').write_text(json.dumps({
        'size': list(size), 'origin': 'top left; integer xy identify pixel centres',
        'normal_space': 'world', 'distance': 'world units from camera projection plane ray origin',
        'camera_matrix': [list(row) for row in matrix], 'records': records,
    }, ensure_ascii=False, indent=2) + '\n')
    return masks


def _compositor(scene, colours, lighting_image, material_masks):
    """Build real Blender nodes; do not read/write image pixels in Python."""
    tree = bpy.data.node_groups.new(f"Parchment Fantasy Pixel Shader {VERSION}", "CompositorNodeTree")
    tree["pixel_shader_version"] = VERSION
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    render = _node(tree, "CompositorNodeImage", "Actual lighting, source view transform baked", (-1000, 0))
    render.image = lighting_image
    pixel = _node(tree, "CompositorNodePixelate", "Native pixel grid (1 px)", (-600, 0))
    pixel.inputs["Size"].default_value = 1
    tree.links.new(render.outputs["Image"], pixel.inputs["Color"])

    # Render Layers are premultiplied; palette comparison needs straight RGB.
    straight = _node(tree, "CompositorNodePremulKey", "Straight RGB", (-400, 0))
    straight.inputs["Type"].default_value = "To Straight"
    tree.links.new(pixel.outputs["Color"], straight.inputs[0])
    source = straight.outputs[0]
    rgb = _node(tree, "CompositorNodeSeparateColor", "Display-linear RGB", (-200, 0))
    rgb.mode = "RGB"
    tree.links.new(source, rgb.inputs[0])

    def math_node(operation, a, b=None, *, location=(0, 0)):
        node = _node(tree, "ShaderNodeMath", operation, location)
        node.operation = operation
        for index, value in enumerate([a] if b is None else [a, b]):
            if isinstance(value, (int, float)):
                node.inputs[index].default_value = value
            else:
                tree.links.new(value, node.inputs[index])
        return node.outputs[0]

    def dot_nodes(components, coefficients, location):
        terms = [math_node("MULTIPLY", c, weight, location=(location[0], location[1] - i * 80))
                 for i, (c, weight) in enumerate(zip(components, coefficients))]
        partial = math_node("ADD", terms[0], terms[1], location=(location[0] + 140, location[1]))
        return math_node("ADD", partial, terms[2], location=(location[0] + 280, location[1]))

    lms = [dot_nodes(list(rgb.outputs)[:3], row, (-100, -300 - i * 300))
           for i, row in enumerate(RGB_TO_LMS)]
    roots = [math_node("POWER", math_node("MAXIMUM", c, 0.0, location=(400, -300 - i * 300)), 1 / 3,
                       location=(540, -300 - i * 300)) for i, c in enumerate(lms)]
    lab = [dot_nodes(roots, row, (600, -300 - i * 300)) for i, row in enumerate(LMS_TO_OKLAB)]
    def nearest_palette(subset, row=0):
        nearest = None
        minimum = None
        for index, colour in enumerate(subset):
            x, y = 1200 + index * 600, row - index * 240
            palette_lab = _oklab(_linear(colour)[:3])
            count = 0

            def step(operation, a, b=None):
                nonlocal count
                location = (x + (count % 4) * 140, y - (count // 4) * 100)
                count += 1
                return math_node(operation, a, b, location=location)

            differences = [step("SUBTRACT", component, target) for component, target in zip(lab, palette_lab)]
            squares = [step("MULTIPLY", d, d) for d in differences]
            lightness_distance = step("MULTIPLY", squares[0], LIGHTNESS_WEIGHT)
            distance = step("ADD", step("ADD", lightness_distance, squares[1]), squares[2])
            if nearest is None:
                constant = _node(tree, "ShaderNodeMixRGB", colour, (x, y + 100))
                constant.inputs[0].default_value = 0.0
                constant.inputs[1].default_value = _linear(colour)
                nearest = constant.outputs[0]
                minimum = distance
                continue
            closer = _node(tree, "ShaderNodeMath", "Closer palette entry?", (x + 100, y))
            closer.operation = "LESS_THAN"
            tree.links.new(distance, closer.inputs[0])
            tree.links.new(minimum, closer.inputs[1])
            choose = _node(tree, "ShaderNodeMixRGB", f"Choose {colour}", (x + 180, y + 100))
            choose.blend_type = "MIX"
            tree.links.new(closer.outputs[0], choose.inputs[0])
            tree.links.new(nearest, choose.inputs[1])
            choose.inputs[2].default_value = _linear(colour)
            nearest = choose.outputs[0]
            best = _node(tree, "ShaderNodeMath", "Minimum distance", (x + 180, y - 100))
            best.operation = "MINIMUM"
            tree.links.new(minimum, best.inputs[0])
            tree.links.new(distance, best.inputs[1])
            minimum = best.outputs[0]
        return nearest

    nearest = nearest_palette(colours)
    for group_index, mask in enumerate(material_masks):
        row = -18000 * (group_index + 1)
        masked_palette = nearest_palette(mask["colours"], row)
        mask_input = _node(tree, "CompositorNodeImage", "Actual material identity", (len(colours) * 600, row))
        mask_input.image = mask["image"]
        mix = _node(tree, "ShaderNodeMixRGB", " / ".join(mask["families"]), (len(colours) * 600 + 140, row))
        tree.links.new(mask_input.outputs["Image"], mix.inputs[0])
        tree.links.new(nearest, mix.inputs[1])
        tree.links.new(masked_palette, mix.inputs[2])
        nearest = mix.outputs[0]

    alpha = _node(tree, "ShaderNodeMath", "Hard alpha > 0.5", (len(colours) * 600, -200))
    alpha.operation = "GREATER_THAN"
    tree.links.new(render.outputs["Alpha"], alpha.inputs[0])
    alpha.inputs[1].default_value = ALPHA_THRESHOLD
    set_alpha = _node(tree, "CompositorNodeSetAlpha", "Binary transparency", (len(colours) * 600, 0))
    set_alpha.inputs["Type"].default_value = "Replace Alpha"
    tree.links.new(nearest, set_alpha.inputs["Image"])
    tree.links.new(alpha.outputs[0], set_alpha.inputs["Alpha"])
    output = _node(tree, "NodeGroupOutput", "Parchment Fantasy native pixel output", (len(colours) * 600 + 240, 0))
    tree.links.new(set_alpha.outputs[0], output.inputs["Image"])
    scene.compositing_node_group = tree
    scene.render.use_compositing = True
    return tree


def create_pixel_scene(source_scene, *, size=DEFAULT_SIZE, families, asset_type, lighting_image, material_masks=(), material_families=None, name=None):
    """Create a work scene for the source's active camera; never replace materials.

    Per-task inputs: target (W,H), declared palette families, asset usage, scene name.
    The algorithm, alpha threshold, colour management and filter are versioned constants.
    """
    if bpy.app.version < (5, 0, 0) or not hasattr(source_scene, "compositing_node_group"):
        raise RuntimeError(f"Parchment Fantasy Pixel Shader {VERSION} requires Blender 5.x compositor API.")
    if source_scene.camera is None:
        raise ValueError("An active camera matching the confirmed view is required.")
    if list(lighting_image.size) != list(size):
        raise ValueError("Bake actual lighting at the exact native size before creating the pixel scene.")
    if len(size) != 2 or any(type(n) is not int or n < 1 for n in size):
        raise ValueError("size must contain two positive integers.")
    if not families or len(set(families)) != len(families):
        raise ValueError("Declare a nonempty list of distinct palette families.")
    palette = json.loads(PALETTE_PATH.read_text())
    if palette["style_id"] != STYLE_ID or not palette["locked"]:
        raise ValueError("The locked Parchment Fantasy palette is required.")
    limit = palette["asset_family_limits"][asset_type]
    if len(families) > limit:
        raise ValueError(f"{asset_type} permits {limit} families, got {len(families)}.")
    colours = list(dict.fromkeys(colour for family in families
                                for colour in palette["families"][family]["ramp"]))
    scene_name = name or f"{source_scene.name}_Parchment Fantasy_Pixel"
    if scene_name in bpy.data.scenes:
        raise ValueError(f"Scene {scene_name!r} already exists; reuse it or choose a new name.")
    original_compositor = source_scene.compositing_node_group
    if original_compositor is not None:
        raise ValueError("Source has a compositor. Review/bake its output before applying this shader.")
    scene = source_scene.copy()
    scene.name = scene_name
    scene.use_fake_user = True
    scene["pixel_shader_version"] = VERSION
    scene["pixel_shader_source"] = source_scene.name
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.filter_size = FILTER_SIZE
    scene.render.dither_intensity = 0.0
    scene.render.use_sequencer = False
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.view_settings.use_curve_mapping = False
    scene.view_settings.use_white_balance = False
    # Temporal noise can change palette choices. Keep the source's sample count/seed.
    _compositor(scene, colours, lighting_image, material_masks)
    manifest = {
        "shader": STYLE_ID, "version": VERSION,
        "script": str(SCRIPT_PATH), "script_sha256": hashlib.sha256(SCRIPT_PATH.read_bytes()).hexdigest(),
        "palette_version": palette["version"],
        "palette_sha256": hashlib.sha256(PALETTE_PATH.read_bytes()).hexdigest(),
        "families": list(families), "colours": colours, "asset_type": asset_type,
        "source_file": bpy.data.filepath, "source_scene": source_scene.name, "pixel_scene": scene.name,
        "engine": scene.render.engine, "camera": scene.camera.name,
        "camera_matrix": [list(row) for row in scene.camera.matrix_world],
        "projection": scene.camera.data.type, "ortho_scale": scene.camera.data.ortho_scale,
        "size": list(size), "frame": scene.frame_current,
        "filter_size": FILTER_SIZE, "alpha_threshold": ALPHA_THRESHOLD,
        "colour_distance": "2 * delta Oklab L squared + delta a squared + delta b squared",
        "lightness_weight": LIGHTNESS_WEIGHT, "extra_brightness_curve": False,
        "material_families": material_families or {},
        "material_masks": [{"families": m["families"], "path": m["image"].filepath} for m in material_masks],
        "input_view_transform": source_scene.view_settings.view_transform,
        "input_look": source_scene.view_settings.look,
        "input_exposure": source_scene.view_settings.exposure,
        "input_gamma": source_scene.view_settings.gamma,
        "lighting_image": lighting_image.filepath,
        "view_transform": "Standard (source display transform already baked into input)",
        "lights": [{"name": o.name, "type": o.data.type, "energy": o.data.energy,
                    "colour": list(o.data.color), "matrix": [list(r) for r in o.matrix_world]}
                   for o in source_scene.objects if o.type == "LIGHT"],
        "blender": bpy.app.version_string, "user_review": "pending",
    }
    scene["pixel_shader_manifest"] = json.dumps(manifest, ensure_ascii=False)
    return scene, manifest


def render_preview(source_scene, *, output_dir, size=DEFAULT_SIZE, families, asset_type, comparison_scale=4, material_families=None):
    """Render A/B evidence and save both editable scenes through Blender itself.

    All output stays under the project's Test Workspace. No Aseprite production
    edits occur here; its MCP may import the images later to assemble review previews.
    """
    root = SCRIPT_PATH.parents[5] / "Test Workspace"
    output = Path(output_dir).resolve()
    if not output.is_relative_to(root.resolve()):
        raise ValueError("Shader preview output must stay inside Test Workspace.")
    if type(comparison_scale) is not int or comparison_scale < 1:
        raise ValueError("comparison_scale must be a positive integer.")
    paths = {key: output / filename for key, filename in {
        "smooth": "before-smooth.png", "raw_native": "before-native.png",
        "lighting": "lighting-native.png", "pixel": "pixel-base-v01.png",
        "blend": "shader-preview.blend", "manifest": "shader-manifest.json",
    }.items()}
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("Preview already exists. Choose a new task/version directory.")
    raw_scene = source_scene.copy()
    raw_scene.name = f"{source_scene.name}_Parchment Fantasy_Before"
    raw_scene.use_fake_user = True
    raw_scene.render.image_settings.media_type = "IMAGE"
    raw_scene.render.image_settings.file_format = "PNG"
    raw_scene.render.image_settings.color_mode = "RGBA"
    raw_scene.render.image_settings.color_depth = "8"
    raw_scene.render.resolution_percentage = 100
    raw_scene.render.use_sequencer = False
    raw_scene.render.use_compositing = False
    output.mkdir(parents=True, exist_ok=True)
    raw_scene.render.resolution_x, raw_scene.render.resolution_y = [n * comparison_scale for n in size]
    raw_scene.render.filepath = str(paths["smooth"])
    bpy.ops.render.render(write_still=True, scene=raw_scene.name)
    # Bake the source view transform through Blender, before palette quantization.
    # This preserves AgX/look/exposure rather than comparing scene-linear HSV V
    # against a display palette and then applying a different view transform.
    lighting_scene = raw_scene.copy()
    lighting_scene.name = f"{source_scene.name}_Parchment Fantasy_Lighting"
    lighting_scene.use_fake_user = True
    lighting_scene.render.resolution_x, lighting_scene.render.resolution_y = size
    lighting_scene.render.filter_size = FILTER_SIZE
    lighting_scene.render.dither_intensity = 0.0
    lighting_scene.render.image_settings.color_depth = "16"
    lighting_scene.render.filepath = str(paths["lighting"])
    bpy.ops.render.render(write_still=True, scene=lighting_scene.name)
    lighting_image = bpy.data.images.load(str(paths["lighting"]), check_existing=False)
    lighting_image.colorspace_settings.name = "sRGB"
    lighting_image.alpha_mode = "STRAIGHT"
    lighting_image.pack()
    masks = _material_masks(lighting_scene, size, families, material_families or {}, output)
    pixel_scene, manifest = create_pixel_scene(source_scene, size=size, families=families,
                                               asset_type=asset_type, lighting_image=lighting_image,
                                               material_masks=masks, material_families=material_families)
    raw_scene.render.resolution_x, raw_scene.render.resolution_y = size
    raw_scene.render.filepath = str(paths["raw_native"])
    bpy.ops.render.render(write_still=True, scene=raw_scene.name)
    pixel_scene.render.filepath = str(paths["pixel"])
    bpy.ops.render.render(write_still=True, scene=pixel_scene.name)
    manifest["outputs"] = {key: str(path) for key, path in paths.items()}
    manifest["comparison_scale"] = comparison_scale
    paths["manifest"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    bpy.context.window.scene = pixel_scene
    bpy.ops.wm.save_as_mainfile(filepath=str(paths["blend"]), copy=True)
    return manifest
