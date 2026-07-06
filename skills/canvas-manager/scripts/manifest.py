"""Manifest read/write/diff helpers for CanvasManager raw snapshots."""
import hashlib
import json
from pathlib import Path


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def save_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def compute_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def diff_object(manifest: dict, key: str, content_hash: str) -> str:
    entry = manifest.get(key)
    if entry is None:
        return "new"
    if entry.get("content_hash") != content_hash:
        return "changed"
    return "unchanged"
