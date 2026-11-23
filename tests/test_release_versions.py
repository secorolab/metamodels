"""Release selection follows numeric stable versions, not push order."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('releases', Path(__file__).resolve().parents[1] / 'scripts/assemble_releases.py')
releases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(releases)


class ReleaseVersionsTest(unittest.TestCase):
    def test_stable_numeric_order(self):
        tags = ['v1.9.0', 'v2.0.0-rc1', 'v1.10.0', 'unrelated', 'v01.0.0', 'v1.8.5']
        self.assertEqual(releases.stable_versions(tags), ['v1.10.0', 'v1.9.0', 'v1.8.5'])

    def test_no_stable_tags(self):
        self.assertEqual(releases.stable_versions(['v1.0.0-beta']), [])
