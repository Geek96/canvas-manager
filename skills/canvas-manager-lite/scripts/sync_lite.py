#!/usr/bin/env python3
"""CanvasManager Lite sync engine: same manifest-based diffing as the full
version, but text/page objects keep only their latest version (no history),
and files are only ever added or replaced with explicit user confirmation."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "canvas-manager" / "scripts"))
import manifest as manifest_mod  # noqa: E402
import snapshot as snapshot_mod  # noqa: E402
import files as files_mod  # noqa: E402


def run_text_sync(course_dir: Path, object_type: str, objects: list, now: datetime) -> dict:
    manifest_path = course_dir / "raw" / "_manifest" / "canvas-objects.json"
    state = manifest_mod.load_manifest(manifest_path)

    fetched_at = now.isoformat(timespec="seconds")
    fetched_at_slug = now.strftime("%Y-%m-%d-%H%M%S")

    new_ids, updated_ids, missing_ids = [], [], []
    unchanged_count = 0
    seen_keys = set()

    for obj in objects:
        key = f"{object_type}/{obj['canvas_id']}"
        seen_keys.add(key)
        content_hash = manifest_mod.compute_content_hash(obj["content"])
        status = manifest_mod.diff_object(state, key, content_hash)

        if status == "unchanged":
            unchanged_count += 1
            continue

        snapshot_path = snapshot_mod.write_snapshot_overwrite(course_dir, object_type, obj, fetched_at)
        state[key] = {
            "canvas_type": obj["canvas_type"],
            "canvas_id": obj["canvas_id"],
            "course_id": obj["course_id"],
            "title": obj["title"],
            "latest_snapshot": str(snapshot_path.relative_to(course_dir)),
            "last_canvas_updated_at": obj["updated_at_canvas"],
            "content_hash": content_hash,
            "status": "active",
        }
        (new_ids if status == "new" else updated_ids).append(key)

    for key, entry in state.items():
        if key.startswith(f"{object_type}/") and key not in seen_keys and entry.get("status") == "active":
            entry["status"] = "missing"
            missing_ids.append(key)

    manifest_mod.save_manifest(manifest_path, state)
    snapshot_mod.write_sync_log(course_dir, fetched_at_slug, object_type, new_ids, updated_ids, unchanged_count, missing_ids)

    return {"new": new_ids, "updated": updated_ids, "unchanged": unchanged_count, "missing": missing_ids}


def run_file_sync(course_dir: Path, file_entries: list, confirmed_replacement_ids: set = None) -> dict:
    confirmed_replacement_ids = confirmed_replacement_ids or set()
    manifest_path = course_dir / "raw" / "_manifest" / "canvas-objects.json"
    state = manifest_mod.load_manifest(manifest_path)

    added, needs_confirmation = [], []

    for entry in file_entries:
        file_id, filename, source_path = entry["file_id"], entry["filename"], entry["source_path"]
        classification = files_mod.classify_file(state, file_id, filename)

        if classification == "unchanged":
            continue
        if classification == "new" or file_id in confirmed_replacement_ids:
            files_mod.register_file(course_dir, state, file_id, filename, source_path)
            added.append(f"files/{file_id}")
        else:
            needs_confirmation.append(f"files/{file_id}")

    manifest_mod.save_manifest(manifest_path, state)
    return {"added": added, "needs_confirmation": needs_confirmation}


def main():
    parser = argparse.ArgumentParser(description="CanvasManager Lite: sync one Canvas object type via opencli-scraped input.")
    parser.add_argument("--course-dir", required=True, type=Path)
    parser.add_argument("--object-type", required=True, help="assignments, announcements, pages, modules, discussions, or files")
    parser.add_argument("--input", required=True, type=Path, help="JSON file: list of normalized objects (text types) or file entries")
    parser.add_argument("--confirm-replace", nargs="*", type=int, default=[], help="file_ids the user has explicitly confirmed replacing")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))

    if args.object_type == "files":
        for entry in data:
            entry["source_path"] = Path(entry["source_path"])
        result = run_file_sync(args.course_dir, data, confirmed_replacement_ids=set(args.confirm_replace))
    else:
        result = run_text_sync(args.course_dir, args.object_type, data, datetime.now())

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
