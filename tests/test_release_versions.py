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

    def test_aliases_with_and_without_stable_releases(self):
        import tempfile
        from unittest.mock import patch

        for tags in ['v1.0.0', '']:
            with self.subTest(tags=tags):
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    for name in ['assets', '_includes', '_layouts']:
                        (root / name).mkdir()
                    (root / '_config.yaml').write_text('title: Models\n')
                    (root / 'index.md').write_text('---\nlayout: default\n---\n')

                    def fake_git(*args):
                        if args[0] == 'tag':
                            return tags
                        return 'main-commit' if args[1].startswith('origin/main') else 'release-commit'

                    def fake_run(command, **kwargs):
                        if command[1] == 'clone':
                            Path(command[-1]).mkdir()
                        elif 'checkout' in command:
                            snapshot = Path(command[2])
                            (snapshot / 'model.json').write_text(command[-1])

                    with patch.object(releases, 'ROOT', root), patch.object(releases, 'git', side_effect=fake_git), patch.object(releases.subprocess, 'run', side_effect=fake_run):
                        releases.main()
                    output = root / '_release_site'
                    self.assertEqual((output / 'model.json').read_text(), 'main-commit')
                    if tags:
                        self.assertEqual((output / 'stable/model.json').read_text(), 'release-commit')
                    else:
                        self.assertFalse((output / 'stable').exists())
                    self.assertEqual((output / 'latest/model.json').read_text(), 'main-commit')
                    self.assertIn('release: latest', (output / 'index.md').read_text())
