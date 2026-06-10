import bpy
import sys
import importlib
from bpy.props import EnumProperty, IntProperty

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
    "builders.image",
    "utils.image_formats",
    "utils.platforms",
    "operators.xmpr.import_xmpr",
    "operators.xmpr.export_xmpr",
    "operators.imgc.import_imgc",
    "operators.imgc.export_imgc",
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


# region Scene properties (xi_platform / xi_format / xi_version)
# Stored on bpy.types.Scene and read/written from the active image's custom properties.
# When no XI image is active, getters return safe defaults (CTR / ETC1 or ETC1A4 / 0).
# When the user changes platform or format on a non-XI image, XI properties are
# automatically initialised on that image (opt-in via interaction).

def _get_active_image(context):
    """Return the image currently displayed in the Image Editor, XI or not."""
    if context and context.area and context.area.type in ('IMAGE_EDITOR', 'UV'):
        return context.area.spaces.active.image
    return None

def _has_alpha(img):
    """Return True if the image has an alpha channel."""
    return img is not None and img.channels == 4

def _default_format_hex(img):
    """
    Return the default format hex string for a non-XI image:
    ETC1A4 (0x06) if the image has alpha, ETC1 (0x05) otherwise.
    Both are CTR formats (3DS default platform).
    """
    return "0x06" if _has_alpha(img) else "0x05"

def _ensure_xi_props(img):
    """
    Initialise XI custom properties on *img* if they are not already present.
    Default platform: CTR (3DS), default format: ETC1 or ETC1A4 based on alpha.
    """
    if img is None:
        return
    if "xi_profile" not in img:
        img["xi_profile"] = "IMGC"
    if "xi_version" not in img:
        img["xi_version"] = 0
    if "xi_format_byte" not in img:
        from .utils.image_formats import FORMATS_BY_PLATFORM
        fmt_hex = _default_format_hex(img)
        items = FORMATS_BY_PLATFORM.get("CTR", [])
        for item in items:
            if item[0] == fmt_hex:
                img["xi_format_byte"] = int(item[0], 16)
                img["xi_format_name"] = item[1]
                break


# --- Platform ---

def _get_platform(self):
    img = _get_active_image(bpy.context)
    if img and "xi_profile" in img:
        from .utils.platforms import PLATFORM_ITEMS
        profile = img.get("xi_profile", "IMGC")
        # Map profile name → platform key → index in PLATFORM_ITEMS
        platform_key = "NX" if profile == "IMGN" else "CTR"
        for i, item in enumerate(PLATFORM_ITEMS):
            if item[0] == platform_key:
                return i
    # Default: CTR (index 0)
    return 0

def _set_platform(self, value):
    img = _get_active_image(bpy.context)
    if img is None:
        return
    # Auto-init XI props if not present (user is opting in by changing the value)
    _ensure_xi_props(img)
    from .utils.platforms import PLATFORM_ITEMS
    platform_key = PLATFORM_ITEMS[value][0]
    img["xi_profile"] = "IMGN" if platform_key == "NX" else "IMGC"
    # Reset format to first available for the new platform
    from .utils.image_formats import FORMATS_BY_PLATFORM
    items = FORMATS_BY_PLATFORM.get(platform_key, [])
    if items:
        img["xi_format_byte"] = int(items[0][0], 16)
        img["xi_format_name"] = items[0][1]


# --- Format ---

def _get_format_items(self, context):
    from .utils.image_formats import FORMATS_BY_PLATFORM
    img = _get_active_image(context)
    if img and "xi_profile" in img:
        profile = img.get("xi_profile", "IMGC")
        platform_key = "NX" if profile == "IMGN" else "CTR"
        return FORMATS_BY_PLATFORM.get(platform_key, [])
    # Default: CTR items (shown even without a XI image)
    return FORMATS_BY_PLATFORM.get("CTR", [])

def _get_format(self):
    from .utils.image_formats import FORMATS_BY_PLATFORM
    img = _get_active_image(bpy.context)
    if img and "xi_format_byte" in img:
        profile = img.get("xi_profile", "IMGC")
        platform_key = "NX" if profile == "IMGN" else "CTR"
        fmt_hex = f"0x{img.get('xi_format_byte', 0):02X}"
        items = FORMATS_BY_PLATFORM.get(platform_key, [])
        for i, item in enumerate(items):
            if item[0] == fmt_hex:
                return i
    # Default: point to ETC1 or ETC1A4 depending on alpha
    if img is not None:
        fmt_hex = _default_format_hex(img)
        items = FORMATS_BY_PLATFORM.get("CTR", [])
        for i, item in enumerate(items):
            if item[0] == fmt_hex:
                return i
    return 0

def _set_format(self, value):
    img = _get_active_image(bpy.context)
    if img is None:
        return
    # Auto-init XI props if not present (user is opting in by changing the value)
    _ensure_xi_props(img)
    from .utils.image_formats import FORMATS_BY_PLATFORM
    profile = img.get("xi_profile", "IMGC")
    platform_key = "NX" if profile == "IMGN" else "CTR"
    items = FORMATS_BY_PLATFORM.get(platform_key, [])
    if value < len(items):
        img["xi_format_byte"] = int(items[value][0], 16)
        img["xi_format_name"] = items[value][1]


# --- Version ---

def _get_version(self):
    img = _get_active_image(bpy.context)
    if img and "xi_version" in img:
        return img.get("xi_version", 0)
    return 0

def _set_version(self, value):
    img = _get_active_image(bpy.context)
    if img is None:
        return
    # Auto-init XI props if not present (user is opting in by changing the value)
    _ensure_xi_props(img)
    img["xi_version"] = value


def _register_scene_props():
    from .utils.platforms import PLATFORM_ITEMS
    bpy.types.Scene.xi_platform = EnumProperty(
        name="Platform",
        items=PLATFORM_ITEMS,
        get=_get_platform,
        set=_set_platform,
    )
    bpy.types.Scene.xi_format = EnumProperty(
        name="Pixel Format",
        items=_get_format_items,
        get=_get_format,
        set=_set_format,
    )
    bpy.types.Scene.xi_version = IntProperty(
        name="Version",
        description="XI header version",
        default=0,
        min=0,
        max=0,
        get=_get_version,
        set=_set_version,
    )

def _unregister_scene_props():
    if hasattr(bpy.types.Scene, "xi_platform"):
        del bpy.types.Scene.xi_platform
    if hasattr(bpy.types.Scene, "xi_format"):
        del bpy.types.Scene.xi_format
    if hasattr(bpy.types.Scene, "xi_version"):
        del bpy.types.Scene.xi_version

# endregion


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

    # Register XI scene properties
    _register_scene_props()


def unregister():
    # Unregister XI scene properties
    _unregister_scene_props()

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