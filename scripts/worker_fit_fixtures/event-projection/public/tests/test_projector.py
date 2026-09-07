import unittest
from src.projector import project_accounts


class ProjectorTests(unittest.TestCase):
    def test_contiguous_delta(self):
        result = project_accounts([{'account_id': 'A', 'revision': 1, 'balance': 20}],
                                  [{'event_id': 'e2', 'account_id': 'A', 'revision': 2, 'delta': -3}], ['A'])
        self.assertEqual(result, {'accounts': [{'account_id': 'A', 'status': 'complete',
                         'revision': 2, 'balance': 17, 'first_missing_revision': None}], 'duplicates_ignored': 0})

    def test_no_snapshot(self):
        result = project_accounts([], [], ['Z'])
        self.assertEqual(result, {'accounts': [{'account_id': 'Z', 'status': 'missing',
                         'revision': None, 'balance': None, 'first_missing_revision': None}], 'duplicates_ignored': 0})


if __name__ == '__main__':
    unittest.main()
