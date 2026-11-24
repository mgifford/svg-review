# Forced-colours audit: status-report icons, chevron and tabledrag

**Scope:** the icons you flagged after reviewing the patch gallery under forced colours. Tested in Chromium forced-colours emulation and on the live Drupal 12 lab at `/admin/reports/status`. The live lab theme is restored exactly afterwards.

## Confirmed issue: status-report icons disappear

All five `.system-status-general-info__item-icon` items use a masked `::before` over:

```css
background-color: var(--admin-color-primary);
```

Under forced colours the author background is replaced with `Canvas`. The mask is then painted in the same colour as the page background:

| Mode | Page background | Icon `::before` background | Result |
|---|---|---|---|
| Forced light | `rgb(255,255,255)` Canvas | `rgb(255,255,255)` | **Invisible** |
| Forced dark | `rgb(0,0,0)` Canvas | `rgb(0,0,0)` | **Invisible** |

This affects **`images/logos/drupal.svg`** and the server, clock, PHP and database status icons. The SVG itself is fine; the problem is the background colour behind the mask.

**This is pre-existing in the before revision as well as MR head; it is not introduced by !16166.** It is still a real forced-colours defect worth fixing.

### Proposed fix

Add a system-colour override inside the icon block:

```css
@media (forced-colors: active) {
  .system-status-general-info__item-icon::before {
    background-color: CanvasText;
  }
}
```

Applied only in forced-colours mode; the normal `--admin-color-primary` circle remains unchanged.

* Patch: `proposed/interdiff-forced-colors-status-icons.patch` (2 files, 8 insertions)
* Test: `proposed/tests/forced_colors_status_icons.py` (3 tests, passing)
* Static component harness: `proposed/test/forced-status-after.html` / `forced-status-proposed.html`
* Actual Drupal screenshots:
  * before: `screens/live-status-forced-light-after.png`, `screens/live-status-forced-dark-after.png`
  * proposed: `screens/live-status-forced-light-proposed.png`, `screens/live-status-forced-dark-proposed.png`
* Component screenshots: `screens/forced-status-after-*.png` / `forced-status-proposed-*.png`

Measured after the fix: forced light `drupalBg = rgb(0,0,0)` on `rgb(255,255,255)`; forced dark `drupalBg = rgb(255,255,255)` on `rgb(0,0,0)`.

## Chevron-down

* The removed `images/icons/000f33/chevron-down.svg` has a hard-coded `#000f33` fill and is invisible on a forced-dark raw preview. It is **not used** by the MR.
* The after `images/icons/chevron-down.svg` is used as a select background. In forced colours the rule in `form--select.pcss.css` sets `background-image: none` and `appearance: revert`, so the browser draws the native select arrow.
* No forced-colours defect found; the dark-blue thumbnail is an original variant, not an after-side asset.

## Tabledrag handle

* The after `images/icons/tabledrag-handle.svg` is a mask. Under forced colours the handle computes `background-color: LinkText` (blue in forced light, yellow in forced dark) and is visible.
* The first two dark handles in the gallery card are original variants (`000f33/tabledrag-handle.svg` and `images/src/tabledrag-handle.svg`), not after assets. They are removed/unused; their raw previews are not evidence of an after-side forced-colours bug.

## Limitations

* Chromium forced-colours emulation, not native Windows High Contrast.
* The live Drupal test used the baseline Drupal 12 theme with only the proposed status CSS applied, then restored the theme exactly (directory diff clean).
* No full MR-theme live install; see the main evidence report for that limitation.
* No claim of full WCAG or SVG conformance.
