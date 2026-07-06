import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import sync as sync_mod  # noqa: E402

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "sample_course_objects.json"


class TestSmoke(unittest.TestCase):
    def test_full_course_sync_by_object_type_then_reruns_idempotently(self):
        objects = json.loads(FIXTURE_PATH.read_text())
        by_type = {}
        for obj in objects:
            by_type.setdefault(obj["canvas_type"] + "s", []).append(obj)

        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            first_pass = {}
            for object_type, objs in by_type.items():
                first_pass[object_type] = sync_mod.run_sync(course_dir, object_type, objs, datetime(2026, 7, 6, 6, 0, 0))

            for object_type, result in first_pass.items():
                self.assertEqual(result["unchanged"], 0)
                self.assertGreater(len(result["new"]), 0)

            second_pass = {}
            for object_type, objs in by_type.items():
                second_pass[object_type] = sync_mod.run_sync(course_dir, object_type, objs, datetime(2026, 7, 6, 18, 0, 0))

            for object_type, result in second_pass.items():
                self.assertEqual(result["new"], [])
                self.assertEqual(result["updated"], [])
                self.assertGreater(result["unchanged"], 0)

            manifest_path = course_dir / "raw" / "_manifest" / "canvas-objects.json"
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(len(manifest), len(objects))
            for entry in manifest.values():
                self.assertEqual(entry["status"], "active")


if __name__ == "__main__":
    unittest.main()
