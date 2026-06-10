import json
import base64
import subprocess
from .platform_env import get_executable_path

def run_mesh_info(filepath: str) -> dict:
    """Run StudioEleven to read a PRM and return the JSON in dictionary form."""
    exe_path = get_executable_path()
    
    try:
        result = subprocess.run(
            [exe_path, "mesh-info", filepath],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"StudioEleven error: {e.stderr}")
    except json.JSONDecodeError:
        raise Exception(f"Unable to read the JSON returned by StudioEleven.\nOutput: {result.stdout}")

def run_image_decode_raw(filepath: str) -> dict:
    """
    Sends a .xi file to StudioEleven via stdin (Base64) and retrieves
    a JSON dictionary containing: width, height, profile, version,
    format_name, format_byte, pixels (Base64 RGBA raw).
    """
    exe_path = get_executable_path()

    with open(filepath, "rb") as f:
        raw_bytes = f.read()

    return _decode_raw_from_bytes(exe_path, raw_bytes)

def run_image_decode_raw_from_bytes(data: bytes) -> dict:
    """
    A variant that accepts raw bytes directly (e.g., extracted from a .xc archive).
    Returns the same JSON dictionary as run_image_decode_raw.
    """
    exe_path = get_executable_path()
    return _decode_raw_from_bytes(exe_path, data)

def run_image_encode(png_bytes: bytes, format_byte: int, platform: str, version: int = 0) -> bytes:
    """
    Sends a PNG (as bytes) to StudioEleven via stdin (Base64) and retrieves
    the encoded .xi file as bytes.

    Args:
        png_bytes:   Raw PNG file bytes.
        format_byte: Pixel format key (e.g. 0x1B for ETC1).
        platform:    Target platform name: "CTR", "NX", etc.
        version:     Image5 header version (default 0).

    Returns:
        Raw .xi file bytes.
    """
    exe_path = get_executable_path()
    b64_input = base64.b64encode(png_bytes).decode("ascii")
    format_hex = f"0x{format_byte:02X}"

    try:
        result = subprocess.run(
            [exe_path, "image", "encode", format_hex, platform, str(version)],
            input=b64_input,
            capture_output=True,
            text=True,
            check=True
        )
        return base64.b64decode(result.stdout)

    except subprocess.CalledProcessError as e:
        raise Exception(f"StudioEleven error (encode): {e.stderr.strip()}")
    except Exception as e:
        raise Exception(f"Unexpected error during encode: {e}")

# region Internal helpers

def _decode_raw_from_bytes(exe_path: str, raw_bytes: bytes) -> dict:
    """Calls 'exe image decode-raw' with the provided bytes Base64 encoded on stdin."""
    b64_input = base64.b64encode(raw_bytes).decode("ascii")

    try:
        result = subprocess.run(
            [exe_path, "image", "decode-raw"],
            input=b64_input,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        raise Exception(f"StudioEleven error (decode-raw): {e.stderr.strip()}")
    except json.JSONDecodeError:
        raise Exception(
            f"Unable to read the JSON returned by decode-raw.\n"
            f"Raw output: {result.stdout[:200]}"
        )

# endregion