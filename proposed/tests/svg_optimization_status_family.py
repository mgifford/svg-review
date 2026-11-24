#!/usr/bin/env python3
"""Checks for the 4-decimal optimisation of the five status-report icons."""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

LAB = pathlib.Path(__file__).resolve().parents[2]
AFTER = LAB / "after/core/themes/default_admin/images"
PROPOSED = LAB / "proposed/core/themes/default_admin/images"
ASSETS = [
    "icons/clock.svg",
    "icons/server.svg",
    "icons/database.svg",
    "logos/drupal.svg",
    "logos/php.svg",
]
NS = "{http://www.w3.org/2000/svg}"


class StatusFamilyOptimisationTest(unittest.TestCase):
    def test_each_file_is_smaller(self):
        for a in ASSETS:
            self.assertLess((PROPOSED / a).stat().st_size, (AFTER / a).stat().st_size, a)

    def test_structure_and_currentcolor_preserved(self):
        for a in ASSETS:
            root = ET.parse(PROPOSED / a).getroot()
            self.assertEqual(root.tag, NS + "svg", a)
            original = ET.parse(AFTER / a).getroot()
            self.assertEqual(root.get("viewBox"), original.get("viewBox"), a)
            self.assertIn("currentColor", (PROPOSED / a).read_text(), a)

    def test_precision_is_at_most_four_decimals(self):
        for a in ASSETS:
            text = (PROPOSED / a).read_text()
            for number in re.findall(r"-?\d+\.\d+", text):
                self.assertLessEqual(len(number.split(".")[1]), 4, f"{a}: {number}")

    def test_no_active_or_external_content(self):
        for a in ASSETS:
            text = (PROPOSED / a).read_text().replace("http://www.w3.org/2000/svg", "")
            for token in ("<script", "<foreignObject", "http://", "https://", "data:"):
                self.assertNotIn(token, text, a)


if __name__ == "__main__":
    unittest.main(verbosity=2)
