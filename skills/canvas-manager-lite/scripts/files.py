"""File (non-page) handling for CanvasManager Lite: new files are added
automatically; replacing an existing filename requires explicit user
confirmation before register_file() is called for it."""
import shutil
from pathlib import Path


def classify_file(manifest: dict, file_id: int, filename: str) -> str:
    key = f"files/{file_id}"
    if key in manifest:
        return "unchanged"
    for existing_key, entry in manifest.items():
        if existing_key.startswith("files/") and entry.get("filename") == filename:
            return "possible_replacement"
    return "new"


def register_file(course_dir: Path, manifest: dict, file_id: int, filename: str, source_path: Path) -> Path:
    """Copy source_path into raw/files/{file_id}/{filename} and record it in
    manifest. Never deletes a previous version already registered under a
    different file_id for the same filename."""
    dest_dir = course_dir / "raw" / "files" / str(file_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    shutil.copy(source_path, dest_path)
    manifest[f"files/{file_id}"] = {
        "canvas_id": file_id,
        "filename": filename,
        "status": "active",
    }
    return dest_path
