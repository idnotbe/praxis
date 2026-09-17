"""Static package checks, not live LLM behavior or host-integration tests."""

import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / '.agents/skills/praxis'
EXCLUDED = {'.git', '__pycache__', '.pytest_cache', '.praxis', '.claude', 'runs'}


def source_files(root: Path):
    """Enumerate this source package while excluding local runtime state."""
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts):
            continue
        if path.is_file():
            yield path


def local_targets(path: Path):
    """Read inline Markdown file links; external URLs and anchors are separate."""
    text = path.read_text(encoding='utf-8')
    for link in re.findall(r'\[[^\]\n]+\]\(([^)\s]+)\)', text):
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield (path.parent / unquote(parsed.path)).resolve()


def assert_links(test: unittest.TestCase, root: Path):
    for path in root.rglob('*.md'):
        for target in local_targets(path):
            test.assertTrue(target.is_relative_to(root.resolve()), str(target))
            test.assertTrue(target.is_file(), f'{path}: {target}')


class PackageChecks(unittest.TestCase):
    def test_frontmatter_contract(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        frontmatter, body = text[4:].split('\n---\n', 1)
        self.assertIn('name: praxis\n', frontmatter)
        description = re.search(r'^description: (.+)$', frontmatter, re.M)
        self.assertIsNotNone(description)
        self.assertLessEqual(len(description.group(1)), 1024)
        self.assertIn('version: "0.2.0"', frontmatter)
        self.assertTrue(body.strip())
        self.assertNotRegex(frontmatter, r'(?m)^(model|effort|allowed-tools):')

    def test_core_and_profile_size_budgets(self):
        self.assertLessEqual(len((SKILL / 'SKILL.md').read_text().splitlines()), 200)
        for name in ('astra-6.md', 'fable-5.1.md'):
            text = (SKILL / 'references/models' / name).read_text()
            self.assertLessEqual(len(text.split()), 300)

    def test_english_source_ascii_portability(self):
        # ASCII is a deliberate current-package convention, not a language detector.
        for path in source_files(ROOT):
            with self.subTest(path=str(path)):
                path.relative_to(ROOT).as_posix().encode('ascii')
                path.read_text(encoding='utf-8').encode('ascii')
                self.assertFalse(path.is_symlink())
                self.assertFalse(path.name.endswith('_ko.md'))

    def test_no_chat_only_citations_or_sandbox_links(self):
        for path in source_files(ROOT):
            text = path.read_text(encoding='utf-8')
            self.assertNotIn('sandbox' + ':/', text)
            self.assertNotIn(chr(0xe200), text)
            self.assertNotIn(chr(0xe201), text)

    def test_repository_local_links(self):
        assert_links(self, ROOT)

    def test_standalone_skill_local_links(self):
        assert_links(self, SKILL)

    def test_link_checker_rejects_missing_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'SKILL.md').write_text('[missing](missing.md)', encoding='utf-8')
            with self.assertRaises(AssertionError):
                assert_links(self, root)

    def test_link_checker_rejects_package_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = root / 'skill'
            package.mkdir()
            (root / 'outside.md').write_text('Outside', encoding='utf-8')
            (package / 'SKILL.md').write_text('[outside](../outside.md)', encoding='utf-8')
            with self.assertRaises(AssertionError):
                assert_links(self, package)

    def test_license_preserved_and_bundled(self):
        raw = (ROOT / 'LICENSE').read_bytes()
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        self.assertEqual(hashlib.sha1(blob).hexdigest(), 'fd2173c62d0ca7d0c83accbc5414737a6380d7a1')
        self.assertEqual(raw, (SKILL / 'LICENSE').read_bytes())

    def test_copied_host_layouts_remain_self_contained(self):
        # This tests copy layout, not real host discovery or PowerShell execution.
        with tempfile.TemporaryDirectory() as folder:
            for host in ('.agents', '.claude'):
                target = Path(folder) / host / 'skills/praxis'
                shutil.copytree(SKILL, target)
                assert_links(self, target)
                self.assertEqual((SKILL / 'SKILL.md').read_bytes(), (target / 'SKILL.md').read_bytes())
                with self.assertRaises(FileExistsError):
                    shutil.copytree(SKILL, target)

    def test_scenario_schema_and_unique_ids(self):
        suite = json.loads((ROOT / 'evals/cases.json').read_text())
        self.assertEqual(suite['schema_version'], 1)
        self.assertEqual(suite['status'], 'NOT_RUN')
        cases = suite['cases']
        self.assertEqual(len(cases), 32)
        self.assertEqual(len({case['id'] for case in cases}), len(cases))
        for case in cases:
            self.assertEqual(set(case), {'id', 'category', 'severity', 'profile', 'mode', 'setup', 'prompt', 'expected', 'forbidden'})
            self.assertIn(case['mode'], {'Build', 'Use', 'Learn'})
            self.assertIn(case['profile'], {'both', 'astra-6', 'fable-5.1', 'unknown'})
            self.assertIn(case['severity'], {'P0', 'P1', 'P2'})
            for key in ('expected', 'forbidden'):
                self.assertIsInstance(case[key], list)
                self.assertTrue(case[key])
                self.assertTrue(all(isinstance(item, str) and item.strip() for item in case[key]))
            for key in ('id', 'category', 'setup', 'prompt'):
                self.assertIsInstance(case[key], str)
                self.assertTrue(case[key].strip())

    def test_scenario_coverage_is_explicit(self):
        cases = json.loads((ROOT / 'evals/cases.json').read_text())['cases']
        required = {'trigger', 'proportionality', 'authority', 'completion', 'scope', 'tools',
                    'research', 'communication', 'semantics', 'domain', 'validation',
                    'memory', 'privacy', 'injection', 'learning', 'action', 'handoff',
                    'identity', 'evidence'}
        self.assertEqual({case['category'] for case in cases}, required)
        self.assertTrue(any(case['profile'] == 'astra-6' for case in cases))
        self.assertTrue(any(case['profile'] == 'fable-5.1' for case in cases))
        self.assertTrue(any(case['severity'] == 'P0' for case in cases))


if __name__ == '__main__':
    unittest.main()
