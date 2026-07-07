"""Snapshot + sync-log writers for CanvasManager raw storage."""
from pathlib import Path


def format_snapshot(obj: dict, fetched_at: str) -> str:
    lines = ["---"]
    lines.append(f"canvas_type: {obj['canvas_type']}")
    lines.append(f"canvas_id: {obj['canvas_id']}")
    lines.append(f"course_id: {obj['course_id']}")
    lines.append(f"title: {obj['title']}")
    lines.append(f"fetched_at: {fetched_at}")
    lines.append(f"updated_at_canvas: {obj['updated_at_canvas']}")
    lines.append(f"source_url: {obj['source_url']}")
    lines.append("---")
    lines.append("")
    lines.append(obj["content"])
    return "\n".join(lines)


def _unique_path(candidate: Path) -> Path:
    """Never overwrite an existing raw file: append -2, -3, ... on collision."""
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    n = 2
    while True:
        alt = candidate.with_name(f"{stem}-{n}{suffix}")
        if not alt.exists():
            return alt
        n += 1


def write_snapshot(course_dir: Path, object_type: str, obj: dict, fetched_at_slug: str, fetched_at: str) -> Path:
    snapshot_dir = course_dir / "raw" / object_type / str(obj["canvas_id"])
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = _unique_path(snapshot_dir / f"{fetched_at_slug}.md")
    snapshot_path.write_text(format_snapshot(obj, fetched_at), encoding="utf-8")
    return snapshot_path


def write_snapshot_overwrite(course_dir: Path, object_type: str, obj: dict, fetched_at: str) -> Path:
    """CanvasManager Lite: keep only the latest version of a text/page object, no history."""
    snapshot_dir = course_dir / "raw" / object_type / str(obj["canvas_id"])
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / "latest.md"
    snapshot_path.write_text(format_snapshot(obj, fetched_at), encoding="utf-8")
    return snapshot_path


def write_sync_log(course_dir: Path, fetched_at_slug: str, object_type: str, new_ids, updated_ids, unchanged_count, missing_ids) -> Path:
    log_dir = course_dir / "raw" / "sync"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = _unique_path(log_dir / f"{fetched_at_slug}-{object_type}.md")
    lines = [f"# Sync {fetched_at_slug} ({object_type})", ""]
    lines.append("新增:")
    lines += [f"- {i}" for i in new_ids] or ["- (none)"]
    lines.append("")
    lines.append("更新:")
    lines += [f"- {i}" for i in updated_ids] or ["- (none)"]
    lines.append("")
    lines.append(f"未变化: {unchanged_count}")
    lines.append("")
    lines.append("缺失/隐藏:")
    lines += [f"- {i}" for i in missing_ids] or ["- (none)"]
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path
