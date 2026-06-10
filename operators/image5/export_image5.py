import os
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, EnumProperty

from ...bridge.runner import run_image_encode

from ...utils.platforms import PLATFORM_ITEMS
from ...utils.image_formats import FORMATS_BY_PLATFORM

# region Entry point

def export_image5_from_image(img: bpy.types.Image, filepath: str, platform: str, format_hex: str) -> None:
    """
    Encodes a Blender image to Image5 and writes it to disk.

    Args:
        img:        The Blender image to encode.
        filepath:   Destination path for the .Image5 file.
        platform:   Target platform name: "CTR" or "NX".
        format_hex: Pixel format hex string, e.g. "0x1B".
    """
    # Pack the image into a temporary PNG in memory
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Save the Blender image as a temporary PNG
        img.filepath_raw = tmp_path
        img.file_format  = "PNG"
        img.save()

        with open(tmp_path, "rb") as f:
            png_bytes = f.read()
    finally:
        os.remove(tmp_path)

    format_byte = int(format_hex, 16)
    version     = img.get("image5_version", 0)

    image5_bytes = run_image_encode(png_bytes, format_byte, platform, version)

    with open(filepath, "wb") as f:
        f.write(image5_bytes)

# endregion

# region Internal helpers

def _get_format_items(self, context):
    """Dynamic EnumProperty callback — returns formats for the selected platform."""
    return FORMATS_BY_PLATFORM.get(self.platform, [])


def _get_active_image5_image(context) -> bpy.types.Image | None:
    """Returns the image currently displayed in the active Image Editor, if any."""
    if context.area and context.area.type == 'IMAGE_EDITOR':
        return context.area.spaces.active.image
    for area in context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            return area.spaces.active.image
    return None

# endregion

# region Blender Operator

class STUDIO26_OT_export_image5(bpy.types.Operator, ExportHelper):
    bl_idname      = "studio26.export_image5"
    bl_label       = "Save XI (Level-5 Image)"
    bl_description = "Encode the current image and save it as a Level-5 (.xi) file"
    bl_options     = {'REGISTER'}

    # File browser filter
    filename_ext = ".xi"
    filter_glob: StringProperty(default="*.xi", options={'HIDDEN'})

    platform: EnumProperty(
        name        = "Platform",
        description = "Target platform",
        items       = PLATFORM_ITEMS,
        default     = "CTR",
    )

    format: EnumProperty(
        name        = "Pixel Format",
        description = "Pixel encoding format",
        items       = _get_format_items,
    )

    def execute(self, context):
        img = _get_active_image5_image(context)
        if img is None:
            self.report({'ERROR'}, "No image found in the active Image Editor.")
            return {'CANCELLED'}

        try:
            export_image5_from_image(img, self.filepath, self.platform, self.format)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, f"Image saved: {os.path.basename(self.filepath)}")
        return {'FINISHED'}

    def invoke(self, context, event):
        img = _get_active_image5_image(context)

        if img is not None:
            # Pre-fill platform and format from the custom properties stored at import
            image5_profile     = img.get("image5_profile",     "IMGC")
            image5_format_byte = img.get("image5_format_byte", 0)

            # Map profile name to platform key
            self.platform = "NX" if image5_profile == "IMGN" else "CTR"

            # Find the matching format hex string in the platform's list
            fmt_hex = f"0x{image5_format_byte:02X}"
            valid   = [item[0] for item in FORMATS_BY_PLATFORM.get(self.platform, [])]
            if fmt_hex in valid:
                self.format = fmt_hex

            # Suggest the original filename
            if img.name:
                self.filepath = img.name if img.name.endswith(".Image5") else img.name + ".Image5"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# endregion