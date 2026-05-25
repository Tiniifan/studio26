import json
import subprocess
from .platform_env import get_executable_path

def run_mesh_info(filepath: str) -> dict:
    """Lance StudioEleven pour lire un PRM et renvoie le JSON sous forme de dictionnaire."""
    exe_path = get_executable_path()
    
    try:
        # Run the command: exe mesh-info "path/to/file.prm"
        result = subprocess.run(
            [exe_path, "mesh-info", filepath],
            capture_output=True,
            text=True,
            check=True
        )
        # Outputs the standard output (stdout) as JSON
        return json.loads(result.stdout)
        
    except subprocess.CalledProcessError as e:
        # If the program returns an error (exit code 1)
        raise Exception(f"Erreur StudioEleven: {e.stderr}")
    except json.JSONDecodeError:
        raise Exception(f"Impossible de lire le JSON retourné par StudioEleven.\nSortie: {result.stdout}")