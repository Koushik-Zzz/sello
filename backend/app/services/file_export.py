import logging
import math
import os
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

import trimesh
import io

from app.models.product_state import ProductState

logger = logging.getLogger(__name__)

# Directory for storing exported files temporarily
EXPORT_DIR = Path(tempfile.gettempdir()) / "hw12_exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _download_glb(url: str) -> bytes:
    """Download GLB file from URL."""
    logger.info(f"[file-export] Downloading GLB from {url[:80]}...")
    with urllib.request.urlopen(url) as response:
        return response.read()


def _load_glb_mesh(glb_data: bytes) -> trimesh.Scene:
    """Load GLB data into trimesh Scene."""
    return trimesh.load(io.BytesIO(glb_data), file_type="glb")


def _export_stl(mesh: trimesh.Scene, output_path: Path) -> None:
    """Export mesh to STL format."""
    # Combine all meshes in the scene
    if isinstance(mesh, trimesh.Scene):
        # Dump returns a single mesh or list of meshes
        dumped = mesh.dump()
        if isinstance(dumped, list):
            combined = trimesh.util.concatenate(dumped)
        else:
            combined = dumped
    else:
        combined = mesh
        
    combined.export(str(output_path), file_type="stl")


def _export_obj(mesh: trimesh.Scene, output_path: Path) -> None:
    """Export mesh to OBJ format."""
    mesh.export(str(output_path), file_type="obj")


def export_product_files(state: ProductState) -> Dict[str, str]:
    """Generate product export files: stl, obj.
    
    Returns:
        Dict mapping file format (e.g. 'stl') to absolute file path
    """
    if not state.model_url:
        logger.warning("[file-export] No model URL in state, skipping product export")
        return {}

    logger.info(f"[file-export] Generating product exports for {state.model_url[:80]}")
    exports = {}

    try:
        # Download and load GLB inside a try block
        glb_data = _download_glb(state.model_url)

        # Save raw GLB as well
        glb_path = EXPORT_DIR / "product.glb"
        glb_path.write_bytes(glb_data)
        exports["glb"] = str(glb_path)

        # Trimesh exports could fail for some complex GLB files
        try:
            mesh = _load_glb_mesh(glb_data)
            stl_path = EXPORT_DIR / "product.stl"
            _export_stl(mesh, stl_path)
            exports["stl"] = str(stl_path)

            obj_path = EXPORT_DIR / "product.obj"
            _export_obj(mesh, obj_path)
            exports["obj"] = str(obj_path)
            logger.info(f"[file-export] Successfully generated: {list(exports.keys())}")
        except Exception as e:
            logger.error(f"[file-export] Failed to generate 3D exports from mesh: {e}")

    except Exception as e:
        logger.error(f"[file-export] Failed to download or convert GLB: {e}")

    return exports
