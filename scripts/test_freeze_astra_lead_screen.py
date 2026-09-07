"""Read-only destination regression tests; no model calls or package mutations."""
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from unittest.mock import Mock

from freeze_astra_lead_screen import REPO, resolve_destinations


class DestinationTests(unittest.TestCase):
    def setUp(self):
        suffix = uuid4().hex
        self.root = Path("/tmp") / ("astra-lead-screen-test-" + suffix)
        self.plan = REPO / "docs/experiments/astra-lead-harness" / ("unused-" + suffix)

    def test_new_exact_targets_are_allowed_without_creation(self):
        root, plan = resolve_destinations(self.root, self.plan)
        self.assertEqual(root, self.root.resolve())
        self.assertEqual(plan, self.plan.resolve())
        self.assertFalse(root.exists())
        self.assertFalse(plan.exists())

    def test_dotdot_escape_is_rejected_after_resolution(self):
        escaping = self.plan.parent / "../../../outside-" / self.plan.name
        self.assertTrue(escaping.is_relative_to(self.plan.parent))
        self.assertFalse(escaping.resolve().is_relative_to(self.plan.parent))
        with self.assertRaisesRegex(ValueError, "task evidence"):
            resolve_destinations(self.root, escaping)
        self.assertFalse(escaping.exists())
        self.assertFalse(self.root.exists())

    def test_existing_targets_and_broad_roots_are_rejected(self):
        for root, plan in ((Path("/tmp"), self.plan), (self.root, self.plan.parent)):
            with self.assertRaisesRegex(ValueError, "Fresh"):
                resolve_destinations(root, plan)

    def test_symlink_predicate_rejects_before_resolving_target(self):
        link = Mock(spec=Path)
        link.is_symlink.return_value = True
        with self.assertRaisesRegex(ValueError, "symlinks"):
            resolve_destinations(link, self.plan)
        link.resolve.assert_not_called()


if __name__ == "__main__":
    unittest.main()

