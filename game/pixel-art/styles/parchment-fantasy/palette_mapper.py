"""Shared locked Oklab palette node builder for 3D and 2D inputs.

This utility has no production rendering entrypoint or scene sampling path.
"""
import bpy
VERSION = "1.0.0"
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

def build_compositor(scene, colours, lighting_image, material_masks, *, lightness_transform=None):
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
    if lightness_transform is not None:
        lab[0] = lightness_transform(tree, render, lab[0], math_node)

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
