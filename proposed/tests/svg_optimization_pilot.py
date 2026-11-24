#!/usr/bin/env python3
"""Checks for the single required.svg optimisation pilot."""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

LAB = pathlib.Path(__file__).resolve().parents[2]
THEME = LAB / "proposed/core/themes/default_admin"
ORIGINAL = LAB / "after/core/themes/default_admin/images/icons/required.svg"
OPTIMISED = THEME / "images/icons/required.svg"
NS = "{http://www.w3.org/2000/svg}"


class SvgOptimisationPilotTest(unittest.TestCase):
    def test_file_is_smaller(self):
        self.assertLess(OPTIMISED.stat().st_size, ORIGINAL.stat().st_size)

    def test_structure_is_preserved(self):
        root = ET.parse(OPTIMISED).getroot()
        self.assertEqual(root.tag, NS + "svg")
        self.assertEqual(root.get("viewBox"), "0 0 24 24")
        path = root.find(NS + "path")
        self.assertIsNotNone(path)
        self.assertEqual(path.get("fill"), "currentColor")

    def test_no_active_or_external_content(self):
        source = OPTIMISED.read_text().replace("http://www.w3.org/2000/svg", "")
        for token in ("<script", "<foreignObject", "http://", "https://", "data:"):
            self.assertNotIn(token, source)

    def test_path_precision_is_at_most_four_decimals(self):
        root = ET.parse(OPTIMISED).getroot()
        d = root.find(NS + "path").get("d")
        for number in re.findall(r"-?\d+\.\d+", d):
            self.assertLessEqual(len(number.split(".")[1]), 4, number)


if __name__ == "__main__":
    unittest.main(verbosity=2)
