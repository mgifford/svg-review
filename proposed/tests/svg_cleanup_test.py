#!/usr/bin/env python3
"""Checks that the confirmed-unused icon assets and variables are gone."""
import pathlib
import re
import unittest

LAB = pathlib.Path(__file__).resolve().parents[2]
THEME = LAB / "proposed/core/themes/default_admin"
ASSETS = [
    "images/icons/appearance.svg",
    "images/icons/blocks.svg",
    "images/icons/bookmarks.svg",
    "images/icons/content.svg",
    "images/icons/files.svg",
    "images/icons/media.svg",
    "images/icons/nav-toggle-left.svg",
    "images/icons/nav-toggle-top.svg",
    "images/icons/people.svg",
    "images/icons/reports.svg",
    "images/icons/structure.svg",
    "images/icons/user.svg",
    "images/icons/pretint/chevron-down-default.svg",
    "images/icons/pretint/remove-default.svg",
]
VARS = [
    "appearance", "blocks", "bookmarks", "content", "files", "media",
    "nav-toggle-toleft", "nav-toggle-totop", "people", "reports",
    "structure", "user", "chevron-down-default", "remove-default",
]


class SvgCleanupTest(unittest.TestCase):
    def test_unused_assets_are_removed(self):
        for a in ASSETS:
            self.assertFalse((THEME / a).exists(), a)

    def test_unused_variables_are_removed(self):
        for name in ("css/base/icons.pcss.css", "css/base/icons.css"):
            css = (THEME / name).read_text()
            for v in VARS:
                self.assertIsNone(re.search(r"--admin-icon-" + re.escape(v) + r"\s*:", css), f"{name}: {v}")

    def test_no_dangling_references(self):
        for p in THEME.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in {".css", ".pcss", ".twig", ".php", ".js", ".yml", ".html"}:
                continue
            if "css/base/icons." in p.as_posix():
                continue
            text = p.read_text(errors="replace")
            for v in VARS:
                self.assertNotIn(f"var(--admin-icon-{v})", text, p.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
