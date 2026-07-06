import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import sync as sync_mod  # noqa: E402


def make_obj(canvas_id, content, updated_at="2026-07-09T07:55:00"):
    return {
        "canvas_type": "assignment",
        "canvas_id": canvas_id,
        "course_id": 67890,
        "title": f"Homework {canvas_id}",
        "updated_at_canvas": updated_at,
        "source_url": f"https://school.instructure.com/courses/67890/assignments/{canvas_id}",
        "content": content,
    }


class TestSync(unittest.TestCase):
    def test_first_sync_writes_new_snapshots_for_all_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            objects = [make_obj(1, "Due Friday."), make_obj(2, "Due next Friday.")]
            result = sync_mod.run_sync(course_dir, "assignments", objects, datetime(2026, 7, 6, 10, 30, 0))
            self.assertEqual(sorted(result["new"]), ["assignments/1", "assignments/2"])
            self.assertEqual(result["updated"], [])
            self.assertEqual(result["unchanged"], 0)
            self.assertEqual(result["missing"], [])

    def test_second_sync_with_no_changes_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            objects = [make_obj(1, "Due Friday.")]
            sync_mod.run_sync(course_dir, "assignments", objects, datetime(2026, 7, 6, 10, 30, 0))
            result = sync_mod.run_sync(course_dir, "assignments", objects, datetime(2026, 7, 6, 18, 0, 0))
            self.assertEqual(result["new"], [])
            self.assertEqual(result["updated"], [])
            self.assertEqual(result["unchanged"], 1)
            snapshots = list((course_dir / "raw" / "assignments" / "1").glob("*.md"))
            self.assertEqual(len(snapshots), 1)

    def test_changed_object_appends_new_snapshot_and_keeps_old(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            sync_mod.run_sync(course_dir, "assignments", [make_obj(1, "Due Friday.")], datetime(2026, 7, 6, 10, 30, 0))
            result = sync_mod.run_sync(
                course_dir, "assignments",
                [make_obj(1, "Due Friday, extended to Monday.", updated_at="2026-07-11T07:55:00")],
                datetime(2026, 7, 6, 18, 0, 0),
            )
            self.assertEqual(result["updated"], ["assignments/1"])
            snapshots = sorted((course_dir / "raw" / "assignments" / "1").glob("*.md"))
            self.assertEqual(len(snapshots), 2)
            self.assertIn("Due Friday.", snapshots[0].read_text())
            self.assertIn("extended to Monday", snapshots[1].read_text())

    def test_object_missing_from_run_is_marked_missing_not_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            sync_mod.run_sync(course_dir, "assignments", [make_obj(1, "A"), make_obj(2, "B")], datetime(2026, 7, 6, 10, 30, 0))
            result = sync_mod.run_sync(course_dir, "assignments", [make_obj(1, "A")], datetime(2026, 7, 6, 18, 0, 0))
            self.assertEqual(result["missing"], ["assignments/2"])
            self.assertTrue((course_dir / "raw" / "assignments" / "2").exists())
            manifest = json.loads((course_dir / "raw" / "_manifest" / "canvas-objects.json").read_text())
            self.assertEqual(manifest["assignments/2"]["status"], "missing")


if __name__ == "__main__":
    unittest.main()
