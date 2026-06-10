import os
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty

from ...bridge.runner import run_image_decode_raw, run_image_decode_raw_from_bytes
from ...builders.image import build_image5_image

#region Entry point

def import_image5_from_filepath(filepath: str, name: str | None = None) -> bpy.types.Image:
    """
    Loads a Image5 file from a disk path and returns the created bpy.types.Image.
    """
    name = name or os.path.splitext(os.path.basename(filepath))[0]
    json_data = run_image_decode_raw(filepath)
    return build_image5_image(json_data, name=name)


def import_image5_from_bytes(data: bytes, name: str = "image5_Image") -> bpy.types.Image:
    """
    Loads a Image5 file from bytes in memory (e.g., extracted from a .xc archive).
    """
    json_data = run_image_decode_raw_from_bytes(data)
    return build_image5_image(json_data, name=name)

#endregion

#region Internal helpers

def _show_image_in_editor(context, img: bpy.types.Image) -> None:
    """Assigns the image to the active Image Editor if one eImage5sts."""
    space = None

    # Priority: the active workspace if it is an Image Editor
    if context.area and context.area.type == 'IMAGE_EDITOR':
        space = context.area.spaces.active
    else:
        # Otherwise, look for the first Image Editor open in all screens.
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                space = area.spaces.active
                break

    if space is not None:
        space.image = img

#endregion

#region Operator Blender

class STUDIO26_OT_import_image5(bpy.types.Operator, ImportHelper):
    bl_idname  = "studio26.import_image5"
    bl_label   = "Open XI (Level-5 Image)"
    bl_description = "Open a Level-5 Image (.xi) image file in Blender"
    bl_options = {'REGISTER', 'UNDO'}

    # Filter displayed in the file browser
    filename_ext = ".xi"
    filter_glob: StringProperty(default="*.xi", options={'HIDDEN'})

    # Display the image in the active Image Editor after import
    show_in_editor: BoolProperty(
        name="Display in editor",
        description="Displays the imported image in the active Image Editor",
        default=True,
    )

    def execute(self, context):
        try:
            img = import_image5_from_filepath(self.filepath)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        # Automatic display in the active Image Editor (if requested)
        if self.show_in_editor:
            _show_image_in_editor(context, img)

        self.report({'INFO'}, f"Image importée : {img.name}  ({img.size[0]}×{img.size[1]})")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
#endregion