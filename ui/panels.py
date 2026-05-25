import bpy
from bpy.props import IntProperty

class Level5MeshProperties(bpy.types.PropertyGroup):
    draw_priority: IntProperty(
        name="Draw Priority",
        description="Priority used for drawing the mesh",
        default=0,
        min=0,
        max=65535
    )

    mesh_type: IntProperty(
        name="Mesh Type",
        description="Type of the mesh",
        default=1,
        min=0,
        max=65535
    )

class STUDIO26_PT_level5_panel(bpy.types.Panel):
    bl_label = "Level 5 Properties"
    bl_idname = "STUDIO26_PT_level5_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.mesh is not None

    def draw(self, context):
        layout = self.layout
        mesh = context.mesh

        if hasattr(mesh, "level5_properties"):
            layout.prop(mesh.level5_properties, "draw_priority")
            layout.prop(mesh.level5_properties, "mesh_type")
        else:
            layout.label(text="No Level 5 properties found.")