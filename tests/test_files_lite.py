import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager-lite" / "scripts"))

import files as files_mod  # noqa: E402


class TestFilesLite(unittest.TestCase):
    def test_classify_file_new_when_filename_unseen(self):
        self.assertEqual(files_mod.classify_file({}, file_id=101, filename="syllabus.pdf"), "new")

    def test_classify_file_unchanged_when_file_id_already_known(self):
        manifest = {"files/101": {"canvas_id": 101, "filename": "syllabus.pdf", "status": "active"}}
        self.assertEqual(files_mod.classify_file(manifest, file_id=101, filename="syllabus.pdf"), "unchanged")

    def test_classify_file_possible_replacement_when_same_filename_different_id(self):
        manifest = {"files/101": {"canvas_id": 101, "filename": "syllabus.pdf", "status": "active"}}
        self.assertEqual(files_mod.classify_file(manifest, file_id=202, filename="syllabus.pdf"), "possible_replacement")

    def test_register_file_copies_into_raw_files_and_updates_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            source = Path(tmp) / "downloaded.pdf"
            source.write_bytes(b"%PDF-fake-content")
            manifest = {}

            dest = files_mod.register_file(course_dir, manifest, file_id=101, filename="syllabus.pdf", source_path=source)

            self.assertEqual(dest, course_dir / "raw" / "files" / "101" / "syllabus.pdf")
            self.assertEqual(dest.read_bytes(), b"%PDF-fake-content")
            self.assertEqual(manifest["files/101"]["filename"], "syllabus.pdf")
            self.assertEqual(manifest["files/101"]["status"], "active")

    def test_register_file_does_not_delete_previous_version_on_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            old_source = Path(tmp) / "old.pdf"
            old_source.write_bytes(b"old")
            new_source = Path(tmp) / "new.pdf"
            new_source.write_bytes(b"new")
            manifest = {}

            files_mod.register_file(course_dir, manifest, file_id=101, filename="syllabus.pdf", source_path=old_source)
            files_mod.register_file(course_dir, manifest, file_id=202, filename="syllabus.pdf", source_path=new_source)

            old_path = course_dir / "raw" / "files" / "101" / "syllabus.pdf"
            new_path = course_dir / "raw" / "files" / "202" / "syllabus.pdf"
            self.assertTrue(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertEqual(old_path.read_bytes(), b"old")
            self.assertEqual(new_path.read_bytes(), b"new")


if __name__ == "__main__":
    unittest.main()
