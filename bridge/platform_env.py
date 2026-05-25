import os
import platform
import stat

def get_executable_path():
    """Detects the OS and architecture and returns the path to the StudioEleven executable"""
    # Move a folder up from 'bridge' to reach the root of the add-on
    addon_dir = os.path.dirname(os.path.dirname(__file__))
    bin_dir = os.path.join(addon_dir, "bin")
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    folder_name = ""
    exe_name = "StudioEleven"
    
    if system == "windows":
        folder_name = "win-x64"
        exe_name = "StudioEleven.exe"
    elif system == "darwin":
        folder_name = "osx-arm64" if machine in ("arm64", "aarch64") else "osx-x64"
    elif system == "linux":
        folder_name = "linux-arm64" if machine in ("arm64", "aarch64") else "linux-x64"
    else:
        raise Exception(f"Système d'exploitation non supporté : {system} {machine}")
        
    exe_path = os.path.join(bin_dir, folder_name, exe_name)
    
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Exécutable introuvable au chemin : {exe_path}")
        
    # Grant execution permissions on Mac/Linux
    if system in ("darwin", "linux"):
        st = os.stat(exe_path)
        os.chmod(exe_path, st.st_mode | stat.S_IEXEC)
        
    return exe_path