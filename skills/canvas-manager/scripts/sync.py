#!/usr/bin/env python3
"""CanvasManager sync engine: diffs incoming Canvas objects against the manifest
and writes new/changed raw snapshots without duplicating unchanged ones."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest as manifest_mod  # noqa: E402
import snapshot as snapshot_mod  # noqa: E402


def run_sync(course_dir: Path, object_type: str, objects: list, now: datetime) -> dict:
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

        snapshot_path = snapshot_mod.write_snapshot(
            course_dir, object_type, obj, fetched_at_slug, fetched_at
        )
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

    return {
        "new": new_ids,
        "updated": updated_ids,
        "unchanged": unchanged_count,
        "missing": missing_ids,
    }


def main():
    parser = argparse.ArgumentParser(description="Sync one Canvas object type into a course's raw/ store.")
    parser.add_argument("--course-dir", required=True, type=Path)
    parser.add_argument("--object-type", required=True, help="e.g. assignments, announcements, pages, modules")
    parser.add_argument("--input", required=True, type=Path, help="JSON file: list of normalized Canvas objects")
    args = parser.parse_args()

    objects = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_sync(args.course_dir, args.object_type, objects, datetime.now())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
