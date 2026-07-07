import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager-lite" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import sync_lite as sync_lite_mod  # noqa: E402


def make_obj(canvas_id, content, updated_at="2026-07-09T07:55:00"):
    return {
        "canvas_type": "page",
        "canvas_id": canvas_id,
        "course_id": 42,
        "title": f"Page {canvas_id}",
        "updated_at_canvas": updated_at,
        "source_url": f"https://school.instructure.com/courses/42/pages/{canvas_id}",
        "content": content,
    }


class TestSyncLiteText(unittest.TestCase):
    def test_first_sync_writes_latest_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            result = sync_lite_mod.run_text_sync(course_dir, "pages", [make_obj(1, "v1")], datetime(2026, 7, 6, 10, 30))
            self.assertEqual(result["new"], ["pages/1"])
            snapshot = course_dir / "raw" / "pages" / "1" / "latest.md"
            self.assertTrue(snapshot.exists())
            self.assertIn("v1", snapshot.read_text())

    def test_changed_content_overwrites_latest_no_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            sync_lite_mod.run_text_sync(course_dir, "pages", [make_obj(1, "v1")], datetime(2026, 7, 6, 10, 30))
            result = sync_lite_mod.run_text_sync(course_dir, "pages", [make_obj(1, "v2")], datetime(2026, 7, 9, 8, 0))
            self.assertEqual(result["updated"], ["pages/1"])
            page_dir = course_dir / "raw" / "pages" / "1"
            files = list(page_dir.glob("*.md"))
            self.assertEqual(len(files), 1)
            self.assertIn("v2", files[0].read_text())

    def test_unchanged_content_is_not_rewritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            sync_lite_mod.run_text_sync(course_dir, "pages", [make_obj(1, "v1")], datetime(2026, 7, 6, 10, 30))
            result = sync_lite_mod.run_text_sync(course_dir, "pages", [make_obj(1, "v1")], datetime(2026, 7, 9, 8, 0))
            self.assertEqual(result["new"], [])
            self.assertEqual(result["updated"], [])
            self.assertEqual(result["unchanged"], 1)


class TestSyncLiteFiles(unittest.TestCase):
    def test_new_file_is_registered_automatically(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            source = Path(tmp) / "syllabus.pdf"
            source.write_bytes(b"content-v1")
            manifest_path = course_dir / "raw" / "_manifest" / "canvas-objects.json"

            result = sync_lite_mod.run_file_sync(course_dir, [
                {"file_id": 101, "filename": "syllabus.pdf", "source_path": source}
            ])

            self.assertEqual(result["added"], ["files/101"])
            self.assertEqual(result["needs_confirmation"], [])
            self.assertTrue((course_dir / "raw" / "files" / "101" / "syllabus.pdf").exists())
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(manifest["files/101"]["filename"], "syllabus.pdf")

    def test_same_filename_new_id_flags_for_confirmation_without_registering(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            first_source = Path(tmp) / "v1.pdf"
            first_source.write_bytes(b"content-v1")
            sync_lite_mod.run_file_sync(course_dir, [
                {"file_id": 101, "filename": "syllabus.pdf", "source_path": first_source}
            ])

            second_source = Path(tmp) / "v2.pdf"
            second_source.write_bytes(b"content-v2")
            result = sync_lite_mod.run_file_sync(course_dir, [
                {"file_id": 202, "filename": "syllabus.pdf", "source_path": second_source}
            ])

            self.assertEqual(result["added"], [])
            self.assertEqual(result["needs_confirmation"], ["files/202"])
            self.assertFalse((course_dir / "raw" / "files" / "202").exists())
            self.assertTrue((course_dir / "raw" / "files" / "101" / "syllabus.pdf").exists())

    def test_confirmed_replacement_registers_without_deleting_old_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            first_source = Path(tmp) / "v1.pdf"
            first_source.write_bytes(b"content-v1")
            sync_lite_mod.run_file_sync(course_dir, [
                {"file_id": 101, "filename": "syllabus.pdf", "source_path": first_source}
            ])

            second_source = Path(tmp) / "v2.pdf"
            second_source.write_bytes(b"content-v2")
            result = sync_lite_mod.run_file_sync(
                course_dir,
                [{"file_id": 202, "filename": "syllabus.pdf", "source_path": second_source}],
                confirmed_replacement_ids={202},
            )

            self.assertEqual(result["added"], ["files/202"])
            self.assertEqual(result["needs_confirmation"], [])
            self.assertTrue((course_dir / "raw" / "files" / "101" / "syllabus.pdf").exists())
            self.assertTrue((course_dir / "raw" / "files" / "202" / "syllabus.pdf").exists())


if __name__ == "__main__":
    unittest.main()
