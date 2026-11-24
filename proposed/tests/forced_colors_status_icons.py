#!/usr/bin/env python3
"""Regression checks for forced-colours visibility of status-report icons.

The status icons are masked ::before elements on an author background colour.
Forced colours replaces that background with Canvas unless a system colour is
set. These checks pin the system-colour override in both source and compiled
CSS. Run with: python3 proposed/tests/forced_colors_status_icons.py
"""
import pathlib
import re
import unittest

LAB = pathlib.Path(__file__).resolve().parents[2]
THEME = LAB / "proposed/core/themes/default_admin"
FILES = (
    "css/components/system-status-report-general-info.pcss.css",
    "css/components/system-status-report-general-info.css",
)


class ForcedColorsStatusIconsTest(unittest.TestCase):
    def test_status_icon_block_has_system_colour_override(self):
        for name in FILES:
            css = (THEME / name).read_text()
            # Locate the .system-status-general-info__item-icon block and its
            # ::before rule, then require CanvasText inside a forced-colors query.
            start = css.index(".system-status-general-info__item-icon {")
            block = css[start:start + 900]
            self.assertIn("@media (forced-colors: active)", block, name)
            self.assertIn("background-color: CanvasText;", block, name)

    def test_author_primary_background_remains_for_normal_modes(self):
        for name in FILES:
            css = (THEME / name).read_text()
            start = css.index(".system-status-general-info__item-icon {")
            block = css[start:start + 900]
            self.assertIn("background-color: var(--admin-color-primary);", block, name)

    def test_no_global_forced_color_adjust_opt_out(self):
        for name in FILES:
            css = (THEME / name).read_text()
            self.assertNotIn("forced-color-adjust: none", css, name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
