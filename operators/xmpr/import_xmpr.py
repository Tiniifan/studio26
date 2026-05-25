import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ...bridge.runner import run_mesh_info
from ...builders.mesh import build_prm_mesh

class STUDIO26_OT_import_prm(bpy.types.Operator, ImportHelper):
    bl_idname = "studio26.import_prm"
    bl_label = "Import PRM/XMPR"
    bl_description = "Import a Level 5 PRM mesh file"
    bl_options = {'PRESET', 'UNDO'}
    
    filename_ext = ".prm"
    filter_glob: StringProperty(default="*.prm;*.xmpr", options={'HIDDEN'})
    
    def execute(self, context):
        try:
            # Use the executable to read the binary and generate the JSON
            json_data = run_mesh_info(self.filepath)
            
            # Use the Python constructor to create the 3D object
            obj = build_prm_mesh(json_data)
            
            # Select the imported object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            self.report({'INFO'}, f"Fichier importé avec succès : {obj.name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}