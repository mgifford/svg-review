# SVG property standard and matrix

**Scope:** the **74 after-side** SVGs in `after/core/themes/default_admin/images`, plus the **61** kept in the proposed tree. Before-side historical variants (194) are not part of this normalisation pass.

**Matrix:** [svg-properties.html](svg-properties.html) — filter by family, paint model, proposal status and flags. The raw data is in [svg-properties.json](svg-properties.json); rendered-pixel metrics are in [svg-visual-metrics.json](svg-visual-metrics.json).

## What the files look like now

| Property | After-side distribution | Proposed |
|---|---:|---|
| Files / bytes | 74 / 41,981 B | 61 / 32,119 B |
| 24×24 viewBox | 56 | 43 |
| 16×16 viewBox | 17 | 17 |
| `0 0 66 33.447` (PHP logo) | 1 | 1 |
| `currentColor` | 53 | 41 |
| Hardcoded colour | 21 | 20 |
| `aria-hidden`/`focusable` | 14 / 74 | **61 / 61** after normalisation |
| `title` / `desc` | 0 / 74 | 0 / 61 (decorative policy) |
| IDs | 0 | 0 |
| External refs / scripts / foreignObject | 0 | 0 |
| Stroke width 2.25 | 33 | 25 |
| Stroke width 3 | 11 | 10 |
| No stroke (filled) | 23 | 24 |
| Stroke width 0.5 / 0.8 / 2 | 3 / 1 / 1 | 3 / 1 / 1 |
| Path precision >4 decimals | 17 | 9 |

## Normalisation targets

### UI master on the 24 grid

- `viewBox="0 0 24 24"`
- no `width`/`height`
- `currentColor` paint
- `aria-hidden="true"` and `focusable="false"`
- no IDs, external refs, scripts, foreignObject
- 2.25 stroke is the **standard line weight**; 3 is the **bold class** (chevrons, grid/list, show/hide, trash)
- 0.5 is the **filled-icon edge-smoothing class** (bookmarks/files/media); do not change without a visual diff
- 2.25 with a `0` stroke on a filled accent is the **filled-accent class** (`fill-opacity=".15"`)

### UI on the 16 grid

- `viewBox="0 0 16 16"`, `width="16" height="16"`, `currentColor`, aria-hidden/focusable
- `key.svg`, `menu.svg`, `tabledrag-handle.svg`
- `tabledrag-handle.svg` was **17×17** with a 16×16 viewBox; normalised to **16×16** in the proposed tree

### Pretints

- same geometry as the master; hardcoded palette colour; 24 grid
- no `currentColor`; aria-hidden/focusable
- `check-inverse`, `chevron-down-*`, `remove-*`, etc. are intentionally white/grey/blue snapshots

### File types

- `viewBox="0 0 16 16"`, `width="16" height="16"`, hardcoded multicolour palette
- aria-hidden/focusable
- **Do not** convert to `currentColor` or force a 24 grid; these are multicolour file-type artwork

### Logos

- preserve intrinsic aspect and viewBox; the PHP logo is `0 0 66 33.447`
- `currentColor`, decorative aria-hidden/focusable
- do not crop or rescale to the 24 icon grid

## Applied metadata normalisation

[interdiff-svg-metadata-normalization.patch](../interdiff-svg-metadata-normalization.patch) adds `aria-hidden="true" focusable="false"` to the 47 proposed SVGs that lacked it and fixes `tabledrag-handle` to 16×16.

[svg_properties_test.py](../tests/svg_properties_test.py) asserts:

- every proposed SVG has a viewBox and is hidden from assistive technology
- no scripts, foreignObject, external/data URLs
- tabledrag dimensions match its 16×16 viewBox
- no external `href`s

All checks pass.

## Not normalised yet — needs visual decisions

1. **Optical padding.** The rendered matrix shows wide ranges: loader has 78.8% bottom padding, pager arrows 32.5% side padding, chevrons 26.9% cross-axis padding. Normalising these changes optical size, so each family needs a visual diff.
2. **Stroke-weight exceptions.** 2 and 3 are deliberate weight classes, not simply drift. Decide the class table before changing any icon.
3. **Fill accents.** Seven UI icons use `fill-opacity=".15"`; verify the accent is intentional across the family.
4. **Path precision.** 9 proposed files still have >4 decimal places. Optimise only with per-file pixel gates, as with the required/status pilot.
5. **Title/desc.** Do **not** add blanket titles. These assets are decorative; the containing control supplies the accessible name. `menu.svg` is inline inside a button labelled “Tabs display toggle”.

## Structural wins already in place

- every SVG has a viewBox
- no IDs, external references, scripts or foreignObject
- duplicate file-type pairs are still present; deduplication is deferred
- all proposed SVGs are hidden from assistive technology
- 14 unused assets removed (2 still pending); `tabledrag-handle` dimensions corrected
