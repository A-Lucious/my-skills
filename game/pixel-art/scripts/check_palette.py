#!/usr/bin/env python3
"""Read-only checks for color families, their shade ramps and production PNGs."""
import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in channels]
    return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def load_palette(path):
    palette = json.loads(path.read_text())
    if palette.get("locked") is not True or not palette.get("version"):
        raise ValueError("Palette must be locked and versioned.")
    colors = palette.get("colors")
    if not isinstance(colors, list) or not colors:
        raise ValueError("Palette needs a nonempty colors whitelist.")
    if any(not isinstance(c, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in colors):
        raise ValueError("Every palette color must be a six-digit HEX RGB value.")
    colors = [c.lower() for c in colors]
    if len(set(colors)) != len(colors):
        raise ValueError("Palette contains duplicate colors.")
    if type(palette.get("color_count")) is not int or palette["color_count"] != len(colors):
        raise ValueError("color_count must equal the unique whitelist length.")
    families = palette.get("families")
    if not isinstance(families, dict) or not families:
        raise ValueError("Palette needs named color families.")
    if type(palette.get("family_count")) is not int or palette["family_count"] != len(families):
        raise ValueError("family_count must equal the number of named families.")
    shades = palette.get("shades_per_family")
    if type(shades) is not int or shades < 1:
        raise ValueError("shades_per_family must declare the fixed shade count per family.")
    family_colors = set()
    for name, family in families.items():
        ramp = family.get("ramp") if isinstance(family, dict) else None
        family_shades = family.get("shade_count", shades) if isinstance(family, dict) else shades
        if type(family_shades) is not int or family_shades < 1:
            raise ValueError(f"Family {name} must declare a positive fixed shade_count.")
        if not isinstance(ramp, list) or len(ramp) != family_shades or any(
            not isinstance(c, str) or c.lower() not in colors for c in ramp
        ):
            raise ValueError(f"Family {name} must have {family_shades} shades from the whitelist.")
        ramp = [c.lower() for c in ramp]
        if len(set(ramp)) != len(ramp):
            raise ValueError(f"Family {name} has duplicate shades.")
        values = [luminance(c) for c in ramp]
        if any(a >= b for a, b in zip(values, values[1:])):
            raise ValueError(f"Family {name} must progress from dark to light.")
        family["ramp"] = ramp
        family_colors.update(ramp)
    if family_colors != set(colors):
        raise ValueError("colors must be exactly the union of declared family shades.")
    limits = palette.get("asset_family_limits")
    if not isinstance(limits, dict) or not limits or any(
        type(limit) is not int or not 1 <= limit <= len(families) for limit in limits.values()
    ):
        raise ValueError("Every asset family limit must be between 1 and family_count.")
    alpha = palette.get("alpha_policy")
    if not isinstance(alpha, list) or not alpha or any(
        type(a) is not int or not 0 <= a <= 255 for a in alpha
    ):
        raise ValueError("alpha_policy must list permitted integer alpha values.")
    ramps = palette.get("ramps")
    if not isinstance(ramps, dict) or not ramps:
        raise ValueError("Palette needs named material ramps.")
    materials = palette.get("material_families")
    if not isinstance(materials, dict) or set(materials) != set(ramps):
        raise ValueError("Every material ramp needs a material_families assignment.")
    for name, ramp in ramps.items():
        family = materials[name]
        if family not in families:
            raise ValueError(f"Material {name} refers to an unknown color family.")
        if not isinstance(ramp, list) or not ramp or any(
            not isinstance(c, str) or c.lower() not in families[family]["ramp"] for c in ramp
        ):
            raise ValueError(f"Ramp {name} includes a shade outside its assigned family.")
        values = [luminance(c.lower()) for c in ramp]
        if any(a > b for a, b in zip(values, values[1:])):
            raise ValueError(f"Ramp {name} is not ordered from dark to light.")
    palette["colors"] = colors
    return palette


def covering_families(palette, observed, selected=None):
    """Find a smallest family cover; a shared dark/light shade counts only once."""
    names = list(palette["families"]) if selected is None else selected
    if len(set(names)) != len(names) or any(name not in palette["families"] for name in names):
        raise ValueError("Selected families must be distinct declared family IDs.")
    groups = {name: set(palette["families"][name]["ramp"]) for name in names}
    available = set().union(*groups.values())
    target = observed & available
    for count in range(len(names) + 1):
        for chosen in combinations(names, count):
            if target <= set().union(*(groups[name] for name in chosen)):
                return list(chosen), sorted(observed - available)
    raise ValueError("Could not assign observed shades to color families.")


def check_exports(palette, asset_type, paths, selected=None):
    # Pillow is used only to read existing PNGs; this script never saves an image.
    from PIL import Image

    limits = palette["asset_family_limits"]
    if asset_type not in limits:
        raise ValueError(f"Unknown asset type {asset_type!r}; choose from {', '.join(limits)}.")
    observed = set()
    alphas = set()
    for path in paths:
        if path.suffix.lower() != ".png":
            raise ValueError("Use production PNGs or all-frame PNG sheets, not previews or GIFs.")
        with Image.open(path) as sprite:
            if sprite.format != "PNG":
                raise ValueError(f"Not a PNG: {path}")
            for frame in range(getattr(sprite, "n_frames", 1)):
                sprite.seek(frame)
                rgba = sprite.convert("RGBA")
                entries = rgba.getcolors(maxcolors=rgba.width * rgba.height)
                for _, (red, green, blue, alpha) in entries:
                    alphas.add(alpha)
                    if alpha:
                        observed.add(f"#{red:02x}{green:02x}{blue:02x}")
    outside = sorted(observed - set(palette["colors"]))
    invalid_alpha = sorted(alphas - set(palette["alpha_policy"]))
    families, outside_selected = covering_families(palette, observed, selected)
    declaration_ok = selected is None or len(selected) <= limits[asset_type]
    return {
        "ok": not outside and not outside_selected and not invalid_alpha
              and len(families) <= limits[asset_type] and declaration_ok,
        "asset_type": asset_type,
        "files": [str(path) for path in paths],
        "visible_color_count": len(observed),
        "required_family_count": len(families),
        "covering_families": families,
        "selected_families": selected,
        "family_limit": limits[asset_type],
        "outside_palette_count": len(outside),
        "outside_palette": outside[:32],
        "outside_selected_families": outside_selected[:32],
        "invalid_alpha": invalid_alpha,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", default="parchment-fantasy")
    parser.add_argument("--asset-type", help="Required with PNGs; see palette asset_family_limits.")
    parser.add_argument("--families", help="Comma-separated family IDs locked in the asset design.")
    parser.add_argument("pngs", type=Path, nargs="*")
    opts = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", opts.style):
        parser.error("--style must be a style ID, not a path.")
    if opts.pngs and not opts.asset_type:
        parser.error("--asset-type is required when checking PNGs.")
    if opts.families is not None and not opts.pngs:
        parser.error("--families is used with production PNGs.")
    try:
        palette = load_palette(SKILL / "styles" / opts.style / "palette.json")
        if palette.get("style_id") != opts.style:
            raise ValueError("Palette style_id does not match its directory.")
        result = {"ok": True, "style": opts.style, "palette_version": palette["version"],
                  "fixed_family_count": palette["family_count"],
                  "shades_per_family": palette["shades_per_family"],
                  "family_shade_counts": {name: family.get("shade_count", palette["shades_per_family"])
                                           for name, family in palette["families"].items()},
                  "available_shade_count": palette["color_count"]}
        if opts.pngs:
            selected = [name.strip() for name in opts.families.split(",")] if opts.families is not None else None
            result.update(check_exports(palette, opts.asset_type, opts.pngs, selected))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 1
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(f"Palette check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
