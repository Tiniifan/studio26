import bpy
import math

def build_prm_mesh(json_data: dict) -> bpy.types.Object:
    """Builds a Blender mesh from StudioEleven JSON data"""
    
    mesh_name = json_data.get("MeshName", "DefaultMesh")
    material_name = json_data.get("MaterialName", "DefaultMaterial")
    
    # Creating the Mesh and the Object
    mesh = bpy.data.meshes.new(name=mesh_name)
    obj = bpy.data.objects.new(name=mesh_name, object_data=mesh)
    bpy.context.collection.objects.link(obj)
    
    # Level 5 Custom Properties
    mesh.level5_properties.draw_priority = json_data.get("DrawPriority", 0)
    mesh.level5_properties.mesh_type = json_data.get("MeshType", 1)
    
    vertices_data = json_data.get("Vertices", [])
    indices = json_data.get("Indices", [])
    
    if not vertices_data or not indices:
        print("ATTENTION: Aucune donnée de vertex ou d'indice trouvée dans le JSON.")
        return obj

    # Extracting arrays for Blender
    positions = []
    normals = []
    uvs0 = []
    
    for v in vertices_data:
        pos = v.get("Position") or [0,0,0]
        norm = v.get("Normal") or [0,0,1]
        uv0 = v.get("UV0") or [0,0]
        
        positions.append(tuple(pos))
        normals.append(tuple(norm))
        uvs0.append(tuple(uv0))
        
    # Grouping the indices into triangles (in groups of 3)
    faces = [tuple(indices[i:i+3]) for i in range(0, len(indices), 3)]

    # Geometry generation
    mesh.from_pydata(positions, [], faces)
    mesh.update()

    # Applying Custom Normals
    mesh.use_auto_smooth = True
    mesh.normals_split_custom_set_from_vertices(normals)

    # Application of UVs
    if uvs0:
        uv_layer = mesh.uv_layers.new(name="UVMap0")
        for loop in mesh.loops:
            uv_layer.data[loop.index].uv = uvs0[loop.vertex_index]

    # Basic creation of the Material
    mat = bpy.data.materials.get(material_name)
    if not mat:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
    mesh.materials.append(mat)
    
    # Rotation (Level-5 Y-up to Blender Z-up)
    obj.rotation_euler = (math.radians(90), 0, 0)
    
    return obj