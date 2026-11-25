#!/usr/bin/env python3
"""Checks that the sticky loader no longer uses a background-image currentColor."""
import pathlib
import unittest

LAB = pathlib.Path(__file__).resolve().parents[2]
THEME = LAB / "proposed/core/themes/default_admin/css/components"


class LoaderDarkTest(unittest.TestCase):
    def test_background_image_removed(self):
        for name in ("more-actions.pcss.css", "more-actions.css"):
            css = (THEME / name).read_text()
            self.assertNotIn("background-image: var(--admin-icon-loader)", css, name)

    def test_currentcolor_mask_present(self):
        for name in ("more-actions.pcss.css", "more-actions.css"):
            css = (THEME / name).read_text()
            self.assertIn("background-color: currentColor", css, name)
            self.assertIn("mask-image: var(--admin-icon-loader)", css, name)
            self.assertIn("pseudo-throbber-mask", css, name)

    def test_reduced_motion(self):
        css = (THEME / "more-actions.pcss.css").read_text()
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn("animation: none", css)


if __name__ == "__main__":
    unittest.main(verbosity=2)
