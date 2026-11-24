#!/usr/bin/env python3
"""Regression checks for the checkmark contrast fix.

Scope: static CSS/SVG checks for the dark-mode disabled checkbox check.
This does not replace a Drupal interface test; it prevents the exact token and
asset regression from returning unnoticed. Run with:

    python3 proposed/tests/checkmark_regression.py
"""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

LAB = pathlib.Path(__file__).resolve().parents[2]
THEME = LAB / "proposed/core/themes/default_admin"
SVG_NS = "{http://www.w3.org/2000/svg}"


def luminance(rgb):
    channels = []
    for value in rgb:
        value = value / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(hex_a, hex_b):
    def to_rgb(value):
        value = value.lstrip("#")
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    light, dark = sorted((luminance(to_rgb(hex_a)), luminance(to_rgb(hex_b))), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class CheckmarkRegressionTest(unittest.TestCase):
    def test_new_pretint_exists_and_is_valid(self):
        path = THEME / "images/icons/pretint/check-disabled-inverse.svg"
        self.assertTrue(path.is_file(), path)
        root = ET.parse(path).getroot()
        self.assertEqual(root.tag, SVG_NS + "svg")
        self.assertEqual(root.get("viewBox"), "0 0 24 24")
        self.assertIsNone(root.get("width"))
        self.assertIsNone(root.get("height"))
        path_element = root.find(SVG_NS + "path")
        self.assertIsNotNone(path_element)
        self.assertEqual(path_element.get("fill"), "#adaeb3")

    def test_pretint_keeps_master_geometry(self):
        master = ET.parse(THEME / "images/icons/check.svg").getroot()
        pretint = ET.parse(THEME / "images/icons/pretint/check-disabled-inverse.svg").getroot()
        self.assertEqual(
            master.find(SVG_NS + "path").get("d"),
            pretint.find(SVG_NS + "path").get("d"),
        )

    def test_registry_declares_token_in_source_and_compiled_css(self):
        pcss = (THEME / "css/base/icons.pcss.css").read_text()
        css = (THEME / "css/base/icons.css").read_text()
        self.assertIn(
            '--admin-icon-checked-disabled-inverse: url("../../images/icons/pretint/check-disabled-inverse.svg")',
            pcss,
        )
        self.assertIn("--admin-icon-checked-disabled-inverse:", css)
        self.assertIn("check-disabled-inverse.svg  #adaeb3", pcss)
        self.assertIn("check-disabled-inverse.svg  #adaeb3", css)

    def test_compiled_data_uri_matches_source(self):
        css = (THEME / "css/base/icons.css").read_text()
        match = re.search(
            r'--admin-icon-checked-disabled-inverse:\s*url\("data:image/svg\+xml,([^"]+)"\)',
            css,
        )
        self.assertIsNotNone(match)
        from urllib.parse import unquote

        compiled = ET.fromstring(unquote(match.group(1)).encode())
        source = ET.parse(
            THEME / "images/icons/pretint/check-disabled-inverse.svg"
        ).getroot()
        self.assertEqual(compiled.get("viewBox"), source.get("viewBox"))
        self.assertEqual(
            compiled.find(SVG_NS + "path").get("d"),
            source.find(SVG_NS + "path").get("d"),
        )
        self.assertEqual(
            compiled.find(SVG_NS + "path").get("fill"),
            "#adaeb3",
        )

    def test_dark_mode_rule_uses_the_dark_pretint(self):
        for name in (
            "css/components/form--checkbox-radio.pcss.css",
            "css/components/form--checkbox-radio.css",
        ):
            css = (THEME / name).read_text()
            self.assertIn(
                ".dark-mode .form-boolean--type-checkbox[disabled]:checked",
                css,
                name,
            )
            self.assertIn(
                "background-image: var(--admin-icon-checked-disabled-inverse);",
                css,
                name,
            )
            # The light rule must remain unchanged.
            self.assertIn(
                "background-image: var(--admin-icon-checked-disabled);",
                css,
                name,
            )

    def test_dark_disabled_contrast_is_at_least_three_to_one(self):
        # Values from variables-color-primitive.css and
        # variables-color-semantic.css: gray-400 on the dark disabled surface.
        self.assertGreaterEqual(contrast("#adaeb3", "#313134"), 3.0)
        # The light-mode disabled check is unchanged and still passes.
        self.assertGreaterEqual(contrast("#767676", "#eaeaea"), 3.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
