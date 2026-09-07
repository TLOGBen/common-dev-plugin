import unittest
from catalog import build_catalog
from search_index import build_index


class ExistingTests(unittest.TestCase):
    def setUp(self):
        self.document = {"release_id": "test", "records": [
            {"id": "one", "status": "active", "channel": "standard", "name": "One",
             "region": "north", "slots": 1, "tags": ["pump"]},
            {"id": "off", "status": "inactive", "channel": "standard", "name": "Off",
             "region": "south", "slots": 9, "tags": ["off"]},
        ]}

    def test_active_positive_record(self):
        self.assertEqual([row["id"] for row in build_catalog(self.document)["items"]], ["one"])

    def test_single_tag_lookup(self):
        index = build_index(build_catalog(self.document))
        self.assertEqual(index["terms"]["pump"], ["one"])


if __name__ == "__main__":
    unittest.main()
