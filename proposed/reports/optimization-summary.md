# SVG optimization summary

## Counting correction

The `adopted` counts above mean “pixel-identical SVGO output”, not “smaller file”. The correct size accounting is:

- **41 existing SVGs are smaller**, saving **2,137 bytes**: 29 icons, 11 file-type icons and the PHP logo.
- **15 unused SVGs removed**, saving **11,281 bytes**.
- **5 new pretints added**, costing **1,226 bytes**.
- **2 adopted files are larger**: `icons/menu.svg` +16 bytes for ARIA metadata and `icons/tabledrag-handle.svg` +30 bytes from SVGO arc-flag spacing.
- Net SVG change: **12,146 bytes smaller**.

See [per-file SVG size changes](svg-size-changes.html).

Tool: SVGO 3.3.2, config `tools/svgo.config.mjs`, multipass with float precision 4.
Pixels were compared in Chromium at 12 sizes, DPR 1 and 2, on transparent, light and dark surfaces.

| Group | Assets | Adopted | Bytes before | Bytes after | Saved |
|---|---|---|---|---|---|
| Icons | 48 | 33 | 17715 | 14922 | 1104 |
| File types | 14 | 11 | 11475 | 10023 | 1052 |
| Logos | 2 | 1 | 2821 | 2413 | 20 |

Skipped because at least one tested combination changed: back-to-site.svg, check.svg, cog.svg, help.svg, key.svg, loader.svg, pretint/check-disabled-inverse.svg, pretint/check-disabled.svg, pretint/check-inverse.svg, pretint/loader-contrast.svg, pretint/loader-inverse.svg, required.svg, search.svg, show.svg, toggle-unchecked.svg, application-pdf.svg, text-html.svg, text-x-script.svg, drupal.svg.

## Theme totals

| Revision | SVGs | SVG bytes | icons.css bytes | icons.css gzip | icons.css brotli |
|---|---|---|---|---|---|
| MR head | 74 | 41981 | 40615 | 9669 | 8184 |
| Revised | 64 | 29835 | 26315 | 6246 | 5346 |

Compression: zlib level 9 and `brotli -q 11`. These are stylesheet-only measurements. They do not describe a delivered page, network transfer or carbon impact.

Limitations: Canvas rendering in Chromium only; no Firefox/WebKit pixel run. Not a visual equivalence proof.
