import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import snapshot as snapshot_mod  # noqa: E402


SAMPLE_OBJ = {
    "canvas_type": "assignment",
    "canvas_id": 12345,
    "course_id": 67890,
    "title": "Homework 4",
    "updated_at_canvas": "2026-07-09T07:55:00",
    "source_url": "https://school.instructure.com/courses/67890/assignments/12345",
    "content": "Due Friday.",
}


class TestSnapshot(unittest.TestCase):
    def test_format_snapshot_includes_frontmatter_fields(self):
        text = snapshot_mod.format_snapshot(SAMPLE_OBJ, "2026-07-06T10:30:00")
        self.assertIn("canvas_type: assignment", text)
        self.assertIn("canvas_id: 12345", text)
        self.assertIn("source_url: https://school.instructure.com/courses/67890/assignments/12345", text)
        self.assertIn("Due Friday.", text)

    def test_write_snapshot_creates_file_at_expected_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            path = snapshot_mod.write_snapshot(course_dir, "assignments", SAMPLE_OBJ, "2026-07-06-103000", "2026-07-06T10:30:00")
            self.assertEqual(path, course_dir / "raw" / "assignments" / "12345" / "2026-07-06-103000.md")
            self.assertTrue(path.exists())

    def test_write_snapshot_never_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            first = snapshot_mod.write_snapshot(course_dir, "assignments", SAMPLE_OBJ, "2026-07-06-103000", "2026-07-06T10:30:00")
            changed = dict(SAMPLE_OBJ, content="Due Monday now.")
            second = snapshot_mod.write_snapshot(course_dir, "assignments", changed, "2026-07-06-103000", "2026-07-06T10:30:00")
            self.assertNotEqual(first, second)
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
            self.assertIn("Due Friday.", first.read_text())
            self.assertIn("Due Monday now.", second.read_text())

    def test_write_snapshot_overwrite_creates_file_at_latest_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            path = snapshot_mod.write_snapshot_overwrite(course_dir, "pages", SAMPLE_OBJ, "2026-07-06T10:30:00")
            self.assertEqual(path, course_dir / "raw" / "pages" / "12345" / "latest.md")
            self.assertTrue(path.exists())
            self.assertIn("Due Friday.", path.read_text())

    def test_write_snapshot_overwrite_replaces_previous_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            snapshot_mod.write_snapshot_overwrite(course_dir, "pages", SAMPLE_OBJ, "2026-07-06T10:30:00")
            changed = dict(SAMPLE_OBJ, content="Due Monday now.")
            path = snapshot_mod.write_snapshot_overwrite(course_dir, "pages", changed, "2026-07-09T08:00:00")
            self.assertNotIn("Due Friday.", path.read_text())
            self.assertIn("Due Monday now.", path.read_text())
            all_files = list((course_dir / "raw" / "pages" / "12345").glob("*.md"))
            self.assertEqual(len(all_files), 1)

    def test_write_sync_log_lists_new_updated_unchanged_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            path = snapshot_mod.write_sync_log(
                course_dir, "2026-07-06-103000", "assignments",
                new_ids=["assignments/1"], updated_ids=["assignments/2"],
                unchanged_count=3, missing_ids=["assignments/4"],
            )
            text = path.read_text()
            self.assertIn("assignments/1", text)
            self.assertIn("assignments/2", text)
            self.assertIn("未变化: 3", text)
            self.assertIn("assignments/4", text)


if __name__ == "__main__":
    unittest.main()
