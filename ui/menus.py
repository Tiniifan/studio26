import bpy

# region Menu File > Import

class STUDIO26_MT_import_menu(bpy.types.Menu):
    bl_label  = "Studio26 (.prm, .xi, .xc, ...)"
    bl_idname = "STUDIO26_MT_import_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("studio26.import_prm",  text="Mesh (.prm / .xmpr)", icon="MESH_DATA")
        layout.operator("studio26.import_imgc", text="Image (.xi)",          icon="IMAGE_DATA")

def draw_import_menu(self, context):
    self.layout.menu(STUDIO26_MT_import_menu.bl_idname)

# endregion

# region Menu Buttons in the Image Editor header

def draw_image_editor_header(self, context):
    """
    Adds 'Open .XI' and 'Save .XI' buttons to the right in the Image Editor header.
    """
    if context.area.type != 'IMAGE_EDITOR':
        return

    layout = self.layout
    layout.separator()

    layout.operator(
        "studio26.import_imgc",
        text="Open .XI",
        icon="IMAGE_DATA",
    )

    layout.operator(
        "studio26.export_imgc",
        text="Save .XI",
        icon="IMAGE_DATA",
    )

# endregion

# region XI Properties Panel (sidebar N)

class STUDIO26_PT_xi_properties(bpy.types.Panel):
    """
    Displays XI image metadata (profile, platform, pixel format, version) in the
    Image Editor sidebar (N panel), under the Studio26 tab.
    Changing platform or format on a non-XI image will automatically
    initialise XI properties on that image.
    """
    bl_label       = "XI Properties"
    bl_idname      = "STUDIO26_PT_xi_properties"
    bl_space_type  = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category    = "Studio26"

    def draw(self, context):
        layout = self.layout
        img    = context.area.spaces.active.image
        has_xi = img is not None and "xi_profile" in img

        col = layout.column(align=True)

        if has_xi:
            col.label(text=f"Profile: {img.get('xi_profile', '?')}", icon="IMAGE_DATA")
        else:
            col.label(text="No XI image loaded", icon="INFO")

        col.prop(context.scene, "xi_platform", text="Platform")
        col.prop(context.scene, "xi_format",   text="Format")
        col.prop(context.scene, "xi_version",  text="Version")

# endregion

# region Register / Unregister

def register():
    bpy.utils.register_class(STUDIO26_PT_xi_properties)
    bpy.types.TOPBAR_MT_file_import.append(draw_import_menu)
    bpy.types.IMAGE_HT_header.append(draw_image_editor_header)


def unregister():
    bpy.utils.unregister_class(STUDIO26_PT_xi_properties)
    bpy.types.TOPBAR_MT_file_import.remove(draw_import_menu)
    bpy.types.IMAGE_HT_header.remove(draw_image_editor_header)

# endregion