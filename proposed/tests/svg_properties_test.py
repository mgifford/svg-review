#!/usr/bin/env python3
"""Invariants for the normalised decorative SVG set."""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

LAB = pathlib.Path(__file__).resolve().parents[2]
ROOT = LAB / "proposed/core/themes/default_admin/images"
NS = "{http://www.w3.org/2000/svg}"


class SvgPropertiesTest(unittest.TestCase):
    def test_all_decoded_icons_have_a_viewbox_and_are_hidden(self):
        files = sorted(ROOT.rglob("*.svg"))
        self.assertTrue(files)
        for p in files:
            root = ET.parse(p).getroot()
            self.assertEqual(root.tag, NS + "svg", p)
            self.assertTrue(root.get("viewBox"), p)
            self.assertEqual(root.get("aria-hidden"), "true", p)
            self.assertEqual(root.get("focusable"), "false", p)

    def test_no_active_or_external_content(self):
        for p in ROOT.rglob("*.svg"):
            source = p.read_text()
            for token in ("<script", "<foreignObject", "http://", "https://", "data:"):
                if token == "http://":
                    source = source.replace("http://www.w3.org/2000/svg", "")
                self.assertNotIn(token, source, p)

    def test_16px_tabledrag_dimensions_match_viewbox(self):
        p = ROOT / "icons/tabledrag-handle.svg"
        root = ET.parse(p).getroot()
        self.assertEqual(root.get("viewBox"), "0 0 16 16")
        self.assertEqual(root.get("width"), "16")
        self.assertEqual(root.get("height"), "16")

    def test_no_external_hrefs(self):
        for p in ROOT.rglob("*.svg"):
            for m in re.finditer(r'(?:xlink:)?href="([^"]+)"', p.read_text()):
                self.assertTrue(m.group(1).startswith("#"), f"{p}: {m.group(1)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
