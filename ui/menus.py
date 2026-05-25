import bpy

class STUDIO26_MT_import_menu(bpy.types.Menu):
    bl_label = "Studio26 (.prm, .xc, ...)"
    bl_idname = "STUDIO26_MT_import_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("studio26.import_prm", text="Mesh (.prm)", icon="MESH_DATA")

def draw_import_menu(self, context):
    self.layout.menu(STUDIO26_MT_import_menu.bl_idname)

def register():
    bpy.types.TOPBAR_MT_file_import.append(draw_import_menu)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(draw_import_menu)