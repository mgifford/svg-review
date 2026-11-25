# Optimisation of every proposed SVG over 300 bytes

**Scope:** all **39** proposed SVGs above 300 bytes. This is the broad pass; files at or below 300 bytes were not touched.

## Result

- 39 files: **26,048 → 23,152 bytes**
- **2,896 bytes saved** on the over-300 set
- **38 of 39** files adopted
- **1 skipped**: `icons/help.svg` — path rounding changed 3 pixels at 24px and 2 at 32px; not acceptable without a design review
- compiled `icons.css`: **27,233 → 25,587 bytes** (1,646 bytes) for this pass
- final proposed SVG total: **28,661 bytes**
- final compiled `icons.css`: **25,587 bytes**

## Applied, with pixel exceptions

| Asset | Before | After | Saving | Pixel result |
|---|---:|---:|---:|---|
| `toggle-unchecked` | 1,297 | 657 | 640 | identical 16–64; 2 edge pixels at 192 |
| `file-types/text-x-script` | 1,012 | 838 | 174 | identical 16–192 |
| `file-types/image-x-generic` | 951 | 827 | 124 | identical 16–192 |
| `file-types/application-pdf` | 838 | 716 | 122 | identical 16–64; 1 edge pixel at 192 |
| `file-types/text-plain` | 964 | 847 | 117 | identical 16–192 |
| `file-types/text-x-generic` | 964 | 847 | 117 | identical 16–192 |
| `file-types/package-x-generic` | 872 | 766 | 106 | identical 16–192 |
| `file-types/x-office-document` | 785 | 682 | 103 | identical 16–192 |
| `file-types/text-html` | 761 | 660 | 101 | identical 16–192 |
| `file-types/x-office-spreadsheet` | 792 | 694 | 98 | identical 16–192 |
| `icons/drag` | 519 | 430 | 89 | identical 16–192 |
| `file-types/x-office-presentation` | 751 | 662 | 89 | identical 16–192 |
| `file-types/video-x-generic` | 775 | 691 | 84 | identical 16–192 |
| `icons/back-to-site` | 375 | 324 | 51 | 5-decimal variant: identical 16–42; 14 edge pixels at 64 |
| `icons/cog` | 1,059 | 976 | 83 | identical 16/24/32/64/192; 1 pixel at 42 |
| `file-types/audio-x-generic` | 846 | 763 | 83 | identical 16–192 |
| `file-types/application-octet-stream` | 582 | 522 | 60 | identical 16–192 |
| `file-types/application-x-executable` | 582 | 522 | 60 | identical 16–192 |
| `icons/search` | 382 | 315 | 67 | identical 16–192 |
| `icons/trash` | 465 | 404 | 61 | identical 16–192 |
| `icons/grid` | 424 | 373 | 51 | identical 16–192 |
| `icons/sidebar` | 444 | 393 | 51 | identical 16–192 |
| `icons/drag-y` | 369 | 321 | 48 | identical 16–192 |
| `icons/warning` | 425 | 382 | 43 | identical 16–192 |
| `icons/hide` | 467 | 430 | 37 | identical 16–192 |
| `icons/status` | 333 | 299 | 34 | identical 16–192 |
| `icons/show` | 327 | 295 | 32 | identical 16–192 |
| `icons/error` | 324 | 293 | 31 | identical 16–192 |
| `icons/info` | 303 | 273 | 30 | identical 16–192 |
| `icons/key` | 517 | 498 | 19 | identical 16–192 |
| `icons/list` | 512 | 439 | 73 | identical 16–192 |
| `icons/menu` | 448 | 438 | 10 | identical 16–192 |
| `logos/drupal` | 1,235 | 1,230 | 5 | identical 16–192 |
| `logos/php` | 1,208 | 1,205 | 3 | identical 16–192 |
| `icons/database` | 343 | 343 | 0 | already at the precision floor |
| `icons/required` | 957 | 957 | 0 | already at the precision floor |
| `icons/server` | 401 | 401 | 0 | already at the precision floor |
| `icons/tabledrag-handle` | 811 | 811 | 0 | already at the precision floor |

`icons/help.svg` remains **628 bytes** and is deliberately not optimised.

## Method

- SVGO 3.3.5, 4-decimal path data, no path merging, no shape conversion, no viewBox removal, no ID cleanup, no title/description/metadata removal, no colour conversion.
- ARIA/viewBox restored after optimisation.
- Pixel comparison at 16, 24, 32, 42, 64 and 192px.
- Compiled `icons.css` data URIs re-synced from every source SVG; `compiled_icons_test.py` verifies source/compiled artwork equivalence.

Patch: `proposed/interdiff-svg-over-300-optimization.patch`.

This pass does not normalise stroke weight, optical padding or path geometry; those remain separate visual decisions.
