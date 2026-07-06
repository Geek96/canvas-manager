import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import manifest as manifest_mod  # noqa: E402


class TestManifest(unittest.TestCase):
    def test_load_manifest_missing_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = manifest_mod.load_manifest(Path(tmp) / "canvas-objects.json")
            self.assertEqual(result, {})

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest" / "canvas-objects.json"
            data = {"assignments/1": {"title": "Homework 1", "content_hash": "abc"}}
            manifest_mod.save_manifest(path, data)
            self.assertEqual(manifest_mod.load_manifest(path), data)

    def test_compute_content_hash_deterministic(self):
        h1 = manifest_mod.compute_content_hash("hello")
        h2 = manifest_mod.compute_content_hash("hello")
        self.assertEqual(h1, h2)

    def test_compute_content_hash_changes_with_content(self):
        h1 = manifest_mod.compute_content_hash("hello")
        h2 = manifest_mod.compute_content_hash("hello world")
        self.assertNotEqual(h1, h2)

    def test_diff_object_new_when_key_absent(self):
        self.assertEqual(manifest_mod.diff_object({}, "assignments/1", "abc"), "new")

    def test_diff_object_changed_when_hash_differs(self):
        state = {"assignments/1": {"content_hash": "old"}}
        self.assertEqual(manifest_mod.diff_object(state, "assignments/1", "new"), "changed")

    def test_diff_object_unchanged_when_hash_matches(self):
        state = {"assignments/1": {"content_hash": "same"}}
        self.assertEqual(manifest_mod.diff_object(state, "assignments/1", "same"), "unchanged")


if __name__ == "__main__":
    unittest.main()
