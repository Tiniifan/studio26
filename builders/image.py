import bpy
import base64

def build_xi_image(json_data: dict, name: str = "XI_Image") -> bpy.types.Image:
    """
    Creates a Blender bpy.types.Image from the JSON produced by `decode-raw`.

    Expected json_data:
    {
        "width":       <int>,
        "height":      <int>,
        "profile":     "<string>",   // e.g. "IMGC" or "IMGN"
        "version":     <int>,
        "format_name": "<string>",   // e.g. "ETC1"
        "format_byte": <int>,        // e.g. 27 (0x1B)
        "pixels":      "<Base64 of raw RGBA bytes, 4 bytes/pixel, row-major top→bottom>"
    }

    Blender stores its pixels from bottom to top, so the image is flipped vertically.
    The profile, version and format are stored as custom properties on the image
    so the export operator can restore them automatically.
    """
    width  = json_data["width"]
    height = json_data["height"]
    raw    = base64.b64decode(json_data["pixels"])

    if len(raw) != width * height * 4:
        raise ValueError(
            f"Unexpected pixel size: {len(raw)} bytes "
            f"for a picture {width}×{height} ({width * height * 4} expected)."
        )

    # Convert to floats 0.0–1.0
    float_pixels = [b / 255.0 for b in raw]

    # Vertical flip (top→bottom → bottom→top for Blender)
    row_size = width * 4
    rows     = [float_pixels[i * row_size:(i + 1) * row_size] for i in range(height)]
    rows.reverse()
    flipped  = [v for row in rows for v in row]

    # Creating or replacing the image in bpy.data
    if name in bpy.data.images:
        img = bpy.data.images[name]
        img.scale(width, height)
    else:
        img = bpy.data.images.new(name, width=width, height=height, alpha=True)

    img.colorspace_settings.name = "sRGB"
    img.alpha_mode = "STRAIGHT"
    img.pixels[:] = flipped
    img.update()

    # Store XI metadata as custom properties for later export
    img["xi_profile"]     = json_data.get("profile",     "IMGC")
    img["xi_version"]     = json_data.get("version",     0)
    img["xi_format_name"] = json_data.get("format_name", "")
    img["xi_format_byte"] = json_data.get("format_byte", 0)

    return img