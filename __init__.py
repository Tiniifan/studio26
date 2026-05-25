import bpy
import sys
import importlib

bl_info = {
    "name": "Studio26",
    "category": "Import-Export",
    "description": "Support some Level 5 files for Blender",
    "author": "Tinifan",
    "version": (1, 0, 0),
    "blender": (3, 4, 0),
    "location": "File > Import-Export > Studio26",
    "support": "COMMUNITY",
}

modules_names = [
    "bridge.platform_env",
    "bridge.runner",
    "builders.mesh",
    "operators.xmpr.import_xmpr",
    "operators.xmpr.export_xmpr",
    "ui.panels",
    "ui.menus",
]

modules = []
classes = []

for name in modules_names:
    fullname = f"{__name__}.{name}"

    if fullname in sys.modules:
        module = importlib.reload(sys.modules[fullname])
    else:
        module = importlib.import_module(f".{name}", package=__name__)

    modules.append(module)

def register():

    # Register module-level register()
    for module in modules:
        if hasattr(module, "register"):
            module.register()

    # Register Blender classes automatically
    for module in modules:
        for obj_name in dir(module):
            obj = getattr(module, obj_name)

            if (
                isinstance(obj, type)
                and hasattr(obj, "bl_idname")
                and obj not in classes
            ):
                try:
                    bpy.utils.register_class(obj)
                    classes.append(obj)
                except Exception as e:
                    print(f"[Studio26] Failed to register {obj}: {e}")

    # Register PropertyGroup
    from .ui.panels import Level5MeshProperties

    bpy.utils.register_class(Level5MeshProperties)

    bpy.types.Mesh.level5_properties = bpy.props.PointerProperty(
        type=Level5MeshProperties
    )

def unregister():

    # Remove custom property
    if hasattr(bpy.types.Mesh, "level5_properties"):
        del bpy.types.Mesh.level5_properties

    try:
        from .ui.panels import Level5MeshProperties
        bpy.utils.unregister_class(Level5MeshProperties)
    except Exception as e:
        print(f"[Studio26] Failed to unregister Level5MeshProperties: {e}")

    # Unregister module-level unregister()
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()

    # Unregister classes in reverse order
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"[Studio26] Failed to unregister {cls}: {e}")

    classes.clear()

if __name__ == "__main__":
    register()