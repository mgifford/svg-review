# High-use SVG optimisation

The supplied `hamburger.svg`, `drupal.svg` and `php.svg` were a good starting point, but all three had lost structural metadata:

- hamburger: no `viewBox`
- PHP: no `viewBox`
- all three: no decorative `aria-hidden`/`focusable`

Those were restored before comparison. The hamburger is pixel-identical at **16–512px**. The Drupal and PHP logos are identical at **16–64px**; the Drupal logo has 8 edge pixels differing at 192px and 14 at 512px, and PHP has 1/2. Those differences are recorded, not hidden.

## High-use set applied

The same 4-decimal conversion was applied to the assets used repeatedly in admin controls:

| Asset | Before | After | Saving |
|---|---:|---:|---:|
| `menu.svg` (supplied hamburger) | 458 | 448 | 10 |
| `chevron-down` | 249 | 226 | 23 |
| `chevron-left` | 250 | 228 | 22 |
| `chevron-right` | 249 | 227 | 22 |
| `pager-first` | 322 | 285 | 37 |
| `pager-last` | 321 | 284 | 37 |
| `pager-next` | 269 | 240 | 29 |
| `pager-prev` | 270 | 241 | 29 |
| `check` | 254 | 221 | 33 |
| `close` | 275 | 256 | 19 |
| `plus` | 271 | 252 | 19 |
| `tabledrag-handle` | 811 | 811 | 0 |
| `loader` | 347 | 279 | 68 |
| `sort` | 296 | 271 | 25 |
| `sort-asc` | 279 | 257 | 22 |
| `sort-desc` | 280 | 258 | 22 |
| `pretint/check-disabled` | 249 | 216 | 33 |
| `pretint/check-inverse` | 249 | 216 | 33 |
| `pretint/check-disabled-inverse` | 249 | 216 | 33 |
| `logos/drupal` (supplied) | 1,260 | 1,235 | 25 |
| `logos/php` (supplied) | 1,229 | 1,208 | 21 |

**21 files / 562 bytes** saved before the compiled CSS pass. The subsequent over-300 pass reduces these files further.

Most importantly, the compiled `icons.css` inlines these as data URIs. It was regenerated from the source artwork and dropped from **28,725 to 27,233 bytes** (1,492 bytes) for this high-use pass. The after-side original compiled CSS was **40,615 bytes**; the current proposed one is **27,233 bytes** (33.0% smaller), including the earlier cleanup.

### Menu/hamburger: what “smaller” means

The supplied hamburger path **is** used for `images/icons/menu.svg`. The raw supplied file is 390 B, but it had no `viewBox`. Restoring the required `viewBox` and decorative ARIA makes it 438 B. The MR’s 421 B after-side file has no ARIA, so it is smaller as a standalone file.

The served CSS is different: the compiled hamburger data URI is **432 B** in the proposed CSS versus **451 B** in the after-side CSS. The gallery’s 421 B value is the MR after-side file, not the proposed optimised source. If raw file bytes were the only goal, dropping the legacy `focusable="false"` would make the proposed menu 419 B, but that would break the metadata consistency applied to the rest of the set.

## What changed

- supplied hamburger mapped to `icons/menu.svg`;
- supplied Drupal/PHP logos adopted with viewBox/ARIA restored;
- 4-decimal path conversion for chevrons, pager, checks, close/plus, sort, loader and tabledrag;
- compiled `icons.css` data URIs re-synced with the source SVGs so the bytes are actually in the served CSS.

## What did not change

- `tabledrag-handle` was already at the precision floor; no byte gain.
- No stroke-weight, optical-padding or geometry redesign was done here. Those remain family decisions in the property standard.
- This is not a blanket rewrite of all 61 assets; it targets repeated controls and the supplied files.

## Evidence

- Patch: `proposed/interdiff-svg-high-use-optimization.patch`.
- Pixel tests: `proposed/tests/svg_optimization_status_family.py` (status family), `proposed/tests/compiled_icons_test.py` (compiled/source artwork equivalence).
- Source/compiled sync test: `proposed/tests/compiled_icons_test.py`.
- Current totals after the over-300 pass: **28,661 SVG bytes** and **25,587 compiled icons.css bytes**.
