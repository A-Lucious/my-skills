"""Parchment Fantasy 2.0.0: pre-light structure -> protected SOFT.04 -> palette.

Run sampling/rendering via Blender MCP. Mask creation and final pixel edits use
Aseprite MCP between these stages. Importing this module has no scene effects.
"""
import bpy
import hashlib
import importlib.util
import json
import os
from array import array
from pathlib import Path

VERSION = "2.0.0"
STYLE_ID = "parchment-fantasy"
DEFAULT_SIZE = (64, 64)
FILTER_SIZE = 0.01
ALPHA_THRESHOLD = 0.5
LIGHTNESS_WEIGHT = 2.0
SCRIPT_PATH = Path(__file__).resolve()
PALETTE_PATH = SCRIPT_PATH.with_name("palette.json")
MAPPER_PATH = SCRIPT_PATH.with_name("palette_mapper.py")
_spec = importlib.util.spec_from_file_location("parchment_palette_mapper", MAPPER_PATH)
mapper = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mapper)
_node = mapper._node


def _workspace(path):
    project = Path(os.environ.get("PIXEL_PROJECT_ROOT", SCRIPT_PATH.parents[5]))
    workspace = (project / "Test Workspace").resolve()
    path = Path(path).resolve()
    if path == workspace or not path.is_relative_to(workspace):
        raise ValueError("Use a task directory inside Test Workspace.")
    return path


def _signature(scene):
    """Hash evaluated geometry, camera, frame and material slots."""
    digest = hashlib.sha256()
    state = {"frame": scene.frame_current, "camera": scene.camera.name,
             "camera_matrix": [list(r) for r in scene.camera.matrix_world],
             "camera_type": scene.camera.data.type, "ortho": scene.camera.data.ortho_scale,
             "lens": scene.camera.data.lens, "shift": [scene.camera.data.shift_x, scene.camera.data.shift_y]}
    digest.update(json.dumps(state, sort_keys=True).encode())
    with bpy.context.temp_override(scene=scene):
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for obj in sorted(scene.objects, key=lambda obj: obj.name):
            digest.update(json.dumps([obj.name, obj.type, obj.hide_render, [list(r) for r in obj.matrix_world],
                                      [slot.material.name if slot.material else None for slot in obj.material_slots]]).encode())
            if obj.type == 'MESH':
                evaluated = obj.evaluated_get(depsgraph)
                mesh = evaluated.to_mesh()
                try:
                    coords = array('f', [0.0]) * (len(mesh.vertices) * 3)
                    mesh.vertices.foreach_get('co', coords)
                    loops = array('i', [0]) * len(mesh.loops)
                    mesh.loops.foreach_get('vertex_index', loops)
                    mids = array('i', [0]) * len(mesh.polygons)
                    mesh.polygons.foreach_get('material_index', mids)
                    digest.update(coords.tobytes()); digest.update(loops.tobytes()); digest.update(mids.tobytes())
                finally:
                    evaluated.to_mesh_clear()
    return digest.hexdigest()


def _protected_lightness(tree, render, lightness, math_node, structural_mask):
    coordinate = _node(tree, "CompositorNodeImageCoordinates", "Native pixel centres", (-1300, -2000))
    tree.links.new(render.outputs["Image"], coordinate.inputs["Image"])
    repeat = _node(tree, "ShaderNodeVectorMath", "Repeat native cells", (-1100, -2000))
    repeat.operation = "MULTIPLY"
    repeat.inputs[1].default_value = (*render.image.size, 0.0)
    tree.links.new(coordinate.outputs["Normalized"], repeat.inputs[0])
    rotate = _node(tree, "ShaderNodeVectorRotate", "Screen angle 45 degrees", (-900, -2000))
    rotate.rotation_type = "Z_AXIS"
    rotate.inputs["Angle"].default_value = 0.785398
    tree.links.new(repeat.outputs["Vector"], rotate.inputs["Vector"])
    fraction = _node(tree, "ShaderNodeVectorMath", "Cell fraction", (-700, -2000))
    fraction.operation = "FRACTION"
    tree.links.new(rotate.outputs["Vector"], fraction.inputs[0])
    xy = _node(tree, "ShaderNodeSeparateXYZ", "Cell coordinates", (-500, -2000))
    tree.links.new(fraction.outputs["Vector"], xy.inputs[0])
    dx = math_node("ABSOLUTE", math_node("SUBTRACT", xy.outputs["X"], 0.5))
    dy = math_node("ABSOLUTE", math_node("SUBTRACT", xy.outputs["Y"], 0.5))
    pattern = math_node("MULTIPLY", math_node("MAXIMUM", dx, dy), 2.0)
    offset = math_node("MULTIPLY", math_node("SUBTRACT", pattern, 0.5), 0.04)
    mask_node = _node(tree, "CompositorNodeImage", "Structure protection: 0=edge / 1=interior", (-100, -2300))
    mask_node.image = structural_mask
    offset = math_node("MULTIPLY", offset, mask_node.outputs["Image"])
    return math_node("MINIMUM", math_node("MAXIMUM", math_node("ADD", lightness, offset), 0.0), 1.0)

def _material_masks(scene, size, families, material_families, output):
    """Query true Blender geometry; identity masks never substitute for lighting.

    One ray at each native pixel centre classifies the first visible surface.
    For transparent materials the caller must declare families for that front
    surface, including transmitted colours it wants to allow.
    """
    from mathutils import Vector

    palette = json.loads(PALETTE_PATH.read_text())
    for material, allowed in material_families.items():
        if material not in bpy.data.materials or not allowed or not set(allowed) <= set(families):
            raise ValueError(f"Invalid material family assignment: {material!r}.")
    groups = list(dict.fromkeys(tuple(allowed) for allowed in material_families.values()))
    width, height = size
    camera = scene.camera
    # Camera projection must use the target aspect, even if the source scene was
    # last previewed at a different resolution. Do not change the source scene.
    grid_scene = bpy.data.scenes.new('Structural sampling grid')
    try:
        grid_scene.render.resolution_x, grid_scene.render.resolution_y = size
        grid_scene.render.pixel_aspect_x = scene.render.pixel_aspect_x
        grid_scene.render.pixel_aspect_y = scene.render.pixel_aspect_y
        frame = camera.data.view_frame(scene=grid_scene)
    finally:
        bpy.data.scenes.remove(grid_scene)
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
                if material not in material_families:
                    raise ValueError(f'Visible material {material!r} requires an explicit family assignment.')
                allowed = material_families[material]
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


def _create_pixel_scene(source_scene, *, size, families, asset_type, lighting_image, material_masks, material_families, structural_mask, name=None):
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
    def transform(tree, render, lightness, math_node):
        return _protected_lightness(tree, render, lightness, math_node, structural_mask)
    mapper.build_compositor(scene, colours, lighting_image, material_masks, lightness_transform=transform)
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
        "material_families": material_families,
        "structural_mask": structural_mask.filepath,
        "dither": {"strength": 0.04, "space": "Oklab L", "rotation_radians": 0.785398, "frequency": list(size), "edge_multiplier": 0, "interior_multiplier": 1, "mean_corrected": False},
        "palette_mapper_version": mapper.VERSION,
        "palette_mapper_sha256": hashlib.sha256(MAPPER_PATH.read_bytes()).hexdigest(),
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


def sample_structure(source_scene, *, output_dir, size=DEFAULT_SIZE, families,
                     material_families, protected_materials=()):
    """Sample before lighting. Next run structural_edges.py prepare + its MCP job."""
    output = _workspace(output_dir)
    if source_scene.camera is None or source_scene.compositing_node_group is not None:
        raise ValueError("Use the confirmed camera scene without a compositor.")
    if len(size) != 2 or any(type(n) is not int or n < 1 for n in size):
        raise ValueError("size must be two positive integers.")
    if not families or not material_families:
        raise ValueError("Declare families and every visible material's allowed families.")
    guidance = output / 'guidance'
    if guidance.exists() and any(guidance.iterdir()):
        raise FileExistsError("Use a new task/version directory.")
    guidance.mkdir(parents=True, exist_ok=True)
    _material_masks(source_scene, size, families, material_families, guidance)
    signature = _signature(source_scene)
    manifest = {'version': VERSION, 'source_scene': source_scene.name,
                'source_signature': signature, 'source_file': bpy.data.filepath,
                'size': list(size), 'families': families,
                'material_families': material_families,
                'protected_materials': list(protected_materials),
                'sampled_before_lighting': True,
                'surface_sha256': hashlib.sha256((guidance/'surface-guidance.json').read_bytes()).hexdigest()}
    (guidance/'prelight-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def render_preview(source_scene, *, output_dir, guidance_dir, asset_type):
    """Render only the structural baseline; prelight data and MCP mask are mandatory."""
    output, guidance = _workspace(output_dir), _workspace(guidance_dir)
    config = json.loads((guidance/'prelight-manifest.json').read_text())
    structure = json.loads((guidance/'structure.json').read_text())
    if config['version'] != VERSION or config['source_signature'] != _signature(source_scene):
        raise ValueError("Geometry/camera/frame changed; resample structure in a new task.")
    if config['source_scene'] != source_scene.name:
        raise ValueError("Structure belongs to a different source scene.")
    surface_hash = hashlib.sha256((guidance/'surface-guidance.json').read_bytes()).hexdigest()
    if surface_hash != config['surface_sha256'] or surface_hash != structure['surface_sha256']:
        raise ValueError("Structure and surface guidance do not match.")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("Use a new empty Shader output directory.")
    size = tuple(config['size'])
    mask_path = guidance/'dither-mask.png'
    mask = bpy.data.images.load(str(mask_path), check_existing=False)
    if tuple(mask.size) != size:
        raise ValueError("Aseprite structure mask must match the native grid.")
    mask.colorspace_settings.name = 'Non-Color'
    values = list(mask.pixels)
    band = {tuple(xy) for xy in structure['band_xy']}
    for y in range(size[1]):
        for x in range(size[0]):
            index = ((size[1]-1-y)*size[0]+x)*4
            expected = 0.0 if (x,y) in band else 1.0
            if any(abs(values[index+c]-expected)>1e-6 for c in range(3)) or values[index+3]!=1.0:
                raise ValueError('Aseprite mask pixels do not match the structure protection band.')
    mask.pack()
    output.mkdir(parents=True, exist_ok=True)
    lighting_scene = source_scene.copy()
    lighting_scene.name = source_scene.name + '_Actual_Lighting'
    lighting_scene.use_fake_user = True
    lighting_scene.render.resolution_x, lighting_scene.render.resolution_y = size
    lighting_scene.render.resolution_percentage = 100
    lighting_scene.render.filter_size = FILTER_SIZE
    lighting_scene.render.dither_intensity = 0
    lighting_scene.render.use_compositing = False
    lighting_scene.render.use_sequencer = False
    lighting_scene.render.image_settings.media_type = 'IMAGE'
    lighting_scene.render.image_settings.file_format = 'PNG'
    lighting_scene.render.image_settings.color_mode = 'RGBA'
    lighting_scene.render.image_settings.color_depth = '16'
    lighting_scene.render.filepath = str(output/'lighting-native.png')
    bpy.ops.render.render(write_still=True, scene=lighting_scene.name)
    lighting = bpy.data.images.load(lighting_scene.render.filepath, check_existing=False)
    lighting.colorspace_settings.name = 'sRGB'; lighting.alpha_mode = 'STRAIGHT'; lighting.pack()
    palette = json.loads(PALETTE_PATH.read_text())
    groups = list(dict.fromkeys(tuple(f) for f in config['material_families'].values()))
    masks = []
    for index, group in enumerate(groups, 1):
        image = bpy.data.images.load(str(guidance/f'material-mask-{index}.png'), check_existing=False)
        image.colorspace_settings.name = 'Non-Color'; image.pack()
        masks.append({'families': list(group), 'image': image,
                      'colours': list(dict.fromkeys(c for f in group for c in palette['families'][f]['ramp']))})
    pixel_scene, manifest = _create_pixel_scene(
        source_scene, size=size, families=config['families'], asset_type=asset_type,
        lighting_image=lighting, material_masks=masks,
        material_families=config['material_families'], structural_mask=mask,
        name=f'{source_scene.name}_{output.parent.name}_Structural_Pixel')
    pixel_scene.render.filepath = str(output/'pixel-base-v01.png')
    bpy.ops.render.render(write_still=True, scene=pixel_scene.name)
    manifest.update({'guidance_dir': str(guidance), 'structure': structure['metrics'],
                     'surface_sha256': surface_hash,
                     'structural_mask_sha256': hashlib.sha256(mask_path.read_bytes()).hexdigest(),
                     'outputs': {'pixel': pixel_scene.render.filepath,
                                 'lighting': lighting_scene.render.filepath,
                                 'blend': str(output/'shader-preview.blend')}})
    pixel_scene['pixel_shader_manifest'] = json.dumps(manifest)
    bpy.data.libraries.write(str(output/'shader-preview.blend'),
                             {source_scene, lighting_scene, pixel_scene},
                             fake_user=True, compress=True)
    (output/'shader-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest
