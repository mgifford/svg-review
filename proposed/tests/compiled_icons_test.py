#!/usr/bin/env python3
"""Verify compiled icon data URIs still match their source SVG artwork."""
import pathlib
import re
import unittest
import urllib.parse
import xml.etree.ElementTree as ET

LAB = pathlib.Path(__file__).resolve().parents[2]
THEME = LAB / "proposed/core/themes/default_admin"
NS = "{http://www.w3.org/2000/svg}"


def sig(root):
    return [
        (child.tag, tuple(sorted(child.attrib.items())))
        for child in list(root)
    ]


class CompiledIconsTest(unittest.TestCase):
    def test_data_uris_match_source_artwork(self):
        pcss = (THEME / "css/base/icons.pcss.css").read_text()
        css = (THEME / "css/base/icons.css").read_text()
        direct = {}
        for m in re.finditer(r'--(admin-icon-[\w-]+):\s*url\("([^"]+)"\)', pcss):
            direct[m.group(1)] = (THEME / "css/base" / m.group(2)).resolve()
        aliases = {}
        for m in re.finditer(r'--(admin-icon-[\w-]+):\s*var\((--admin-icon-[\w-]+)\)', pcss):
            aliases[m.group(1)] = m.group(2).lstrip("-")

        def resolve(name, seen=None):
            seen = seen or set()
            if name in direct:
                return direct[name]
            if name in aliases and name not in seen:
                seen.add(name)
                return resolve(aliases[name], seen)
            return None

        checked = 0
        for var in list(direct) + list(aliases):
            source_path = resolve(var)
            if not source_path:
                continue
            m = re.search(
                r'--' + re.escape(var) + r':\s*url\("data:image/svg\+xml,([^"]+)"\)',
                css,
            )
            self.assertIsNotNone(m, var)
            compiled = ET.fromstring(urllib.parse.unquote(m.group(1)).encode())
            source = ET.parse(source_path).getroot()
            self.assertEqual(compiled.get("viewBox"), source.get("viewBox"), var)
            self.assertEqual(sig(compiled), sig(source), var)
            checked += 1
        self.assertGreater(checked, 45)


if __name__ == "__main__":
    unittest.main(verbosity=2)
