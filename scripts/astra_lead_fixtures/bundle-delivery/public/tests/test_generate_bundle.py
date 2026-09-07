import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generate_bundle import build_bundle


class ExistingBundleTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "records.json"
        self.document = json.loads(path.read_text(encoding="utf-8"))

    def test_includes_a_positive_active_record(self):
        rows = build_bundle(self.document)["items"]
        self.assertEqual(next(row for row in rows if row["record_id"] == "row-a")["quantity"], 5)

    def test_excludes_archived_record(self):
        rows = build_bundle(self.document)["items"]
        self.assertNotIn("row-c", [row["record_id"] for row in rows])


if __name__ == "__main__":
    unittest.main()

