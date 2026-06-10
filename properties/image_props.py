import bpy
from bpy.props import EnumProperty, IntProperty


# region Helpers

def _get_active_image(context):
    """Return the image currently displayed in the Image Editor, Image5 or not."""
    if context and context.area and context.area.type in ('IMAGE_EDITOR', 'UV'):
        return context.area.spaces.active.image
    return None

def _has_alpha(img):
    """Return True if the image has an alpha channel."""
    return img is not None and img.channels == 4

def _default_format_hex(img):
    """
    Return the default format hex string for a non-Image5 image:
    ETC1A4 (0x06) if the image has alpha, ETC1 (0x05) otherwise.
    Both are CTR formats (3DS default platform).
    """
    return "0x06" if _has_alpha(img) else "0x05"

def _ensure_image5_props(img):
    """
    Initialise Image5 custom properties on *img* if they are not already present.
    Default platform: CTR (3DS), default format: ETC1 or ETC1A4 based on alpha.
    """
    if img is None:
        return
    if "image5_profile" not in img:
        img["image5_profile"] = "IMGC"
    if "image5_version" not in img:
        img["image5_version"] = 0
    if "image5_format_byte" not in img:
        from ..utils.image_formats import FORMATS_BY_PLATFORM
        fmt_hex = _default_format_hex(img)
        items = FORMATS_BY_PLATFORM.get("CTR", [])
        for item in items:
            if item[0] == fmt_hex:
                img["image5_format_byte"] = int(item[0], 16)
                img["image5_format_name"] = item[1]
                break

# endregion


# region Platform

def _get_platform(self):
    img = _get_active_image(bpy.context)
    if img and "image5_profile" in img:
        from ..utils.platforms import PLATFORM_ITEMS
        profile = img.get("image5_profile", "IMGC")
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
    # Auto-init Image5 props if not present (user is opting in by changing the value)
    _ensure_image5_props(img)
    from ..utils.platforms import PLATFORM_ITEMS
    platform_key = PLATFORM_ITEMS[value][0]
    img["image5_profile"] = "IMGN" if platform_key == "NX" else "IMGC"
    # Reset format to first available for the new platform
    from ..utils.image_formats import FORMATS_BY_PLATFORM
    items = FORMATS_BY_PLATFORM.get(platform_key, [])
    if items:
        img["image5_format_byte"] = int(items[0][0], 16)
        img["image5_format_name"] = items[0][1]

# endregion


# region Format

def _get_format_items(self, context):
    from ..utils.image_formats import FORMATS_BY_PLATFORM
    img = _get_active_image(context)
    if img and "image5_profile" in img:
        profile = img.get("image5_profile", "IMGC")
        platform_key = "NX" if profile == "IMGN" else "CTR"
        return FORMATS_BY_PLATFORM.get(platform_key, [])
    # Default: CTR items (shown even without a Image5 image)
    return FORMATS_BY_PLATFORM.get("CTR", [])

def _get_format(self):
    from ..utils.image_formats import FORMATS_BY_PLATFORM
    img = _get_active_image(bpy.context)
    if img and "image5_format_byte" in img:
        profile = img.get("image5_profile", "IMGC")
        platform_key = "NX" if profile == "IMGN" else "CTR"
        fmt_hex = f"0x{img.get('image5_format_byte', 0):02X}"
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
    # Auto-init Image5 props if not present (user is opting in by changing the value)
    _ensure_image5_props(img)
    from ..utils.image_formats import FORMATS_BY_PLATFORM
    profile = img.get("image5_profile", "IMGC")
    platform_key = "NX" if profile == "IMGN" else "CTR"
    items = FORMATS_BY_PLATFORM.get(platform_key, [])
    if value < len(items):
        img["image5_format_byte"] = int(items[value][0], 16)
        img["image5_format_name"] = items[value][1]

# endregion


# region Version

def _get_version(self):
    img = _get_active_image(bpy.context)
    if img and "image5_version" in img:
        return img.get("image5_version", 0)
    return 0

def _set_version(self, value):
    img = _get_active_image(bpy.context)
    if img is None:
        return
    # Auto-init Image5 props if not present (user is opting in by changing the value)
    _ensure_image5_props(img)
    img["image5_version"] = value

# endregion


# region Register / Unregister

def register():
    from ..utils.platforms import PLATFORM_ITEMS
    bpy.types.Scene.image5_platform = EnumProperty(
        name="Platform",
        items=PLATFORM_ITEMS,
        get=_get_platform,
        set=_set_platform,
    )
    bpy.types.Scene.image5_format = EnumProperty(
        name="Pixel Format",
        items=_get_format_items,
        get=_get_format,
        set=_set_format,
    )
    bpy.types.Scene.image5_version = IntProperty(
        name="Version",
        description="Image5 header version",
        default=0,
        min=0,
        max=0,
        get=_get_version,
        set=_set_version,
    )

def unregister():
    if hasattr(bpy.types.Scene, "image5_platform"):
        del bpy.types.Scene.image5_platform
    if hasattr(bpy.types.Scene, "image5_format"):
        del bpy.types.Scene.image5_format
    if hasattr(bpy.types.Scene, "image5_version"):
        del bpy.types.Scene.image5_version

# endregion