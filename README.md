# Drupal Default Admin SVG review

Independent review material for **Drupal core MR !16166** (`default_admin` SVG consolidation).

- MR: https://git.drupalcode.org/project/drupal/-/merge_requests/16166
- Issue: https://www.drupal.org/project/drupal/issues/3603162
- Baseline before: `29b0a0b2256eb5ed27df6ec5e4e4e33142a717e8`
- MR head reviewed: `fe4adb4f942385912bb3244b570afa475cadf3bd`

This is a **draft review lab**, not an official Drupal repository, not an upstream fork, and **not RTBC**. No claim of full SVG or WCAG conformance is made.

## What is here

| Path | Contents |
|---|---|
| `SVG-IMPROVEMENT-PLAN.md` | Prioritised plan for missing assets, dark mode, forced colours, WCAG 2.2 AA, testing and optimisation |
| `reconciliation.md` / `.json` | Checkmark-family dispositions and evidence |
| `CODE-REVIEW.md` | Review of the SVG Review Lab tooling |
| `evidence/` | Historical findings baseline (schema 4) |
| `lab/` | The static SVG Review Lab (`acquire.py`, `usage.py`, `review.py`, `template.html`) |
| `proposed/interdiff-*.patch` | Small proposed fixes/optimisations against the MR head |
| `proposed/tests/` | Regression checks for the fixes |
| `proposed/reports/` | Per-fix evidence, screenshots, validation, currentColor dark-mode audit, SVG property matrix and the self-contained asset gallery |
| `review.html` | Interactive SVG inventory generated from the pinned snapshots |
| `after/` / `proposed/` | **Test fixtures only** — not full Drupal themes; see below |

## Reading “after”, “proposed” and “removed”

- **After-side** — the MR !16166 tree: the files the patch actually adds or keeps.
- **Proposed** — our separate fixes/cleanup working copy, not upstream.
- **Unused — proposed removal** — the MR keeps the file, but we found no CSS, template or JS consumer in the after tree. Our cleanup recommends deleting it; this is **not** an MR deletion and the cleanup is optional.
- **No after asset** — an original file has no counterpart in the MR at all.

The 14 assets currently recommended for removal are `appearance`, `blocks`, `bookmarks`, `content`, `files`, `media`, `nav-toggle-left`, `nav-toggle-top`, `people`, `reports`, `structure`, `user`, `pretint/chevron-down-default` and `pretint/remove-default`. `search` and `chevron-left` are also unused but remain pending a decision.

## Quick start

### Static review

```sh
python3 -m http.server 8770 --bind 127.0.0.1
# open http://127.0.0.1:8770/proposed/reports/patch-gallery.html
```

`patch-gallery.html` embeds the SVGs, so the asset gallery works without the Drupal snapshots. The “Open real forced-colours tabs” button needs the local Playwright helper, which is not included in this simplified repo; use Chromium DevTools → Rendering → Emulate forced-colors instead.

`review.html` is the full generated inventory and also works offline.

### Reproduce the full lab

```sh
cd lab
python3 acquire.py        # fetches the pinned commits and extracts default_admin
python3 review.py         # writes usage.json, inventory.json, review.html
```

This requires Git and network access to `git.drupalcode.org`. Do not commit the acquired `before/`, `after/`, `drupal.git/`, `inventory.json` or `usage.json`.

### Apply the proposed patches

Apply in this order to a checkout at the MR head:

```sh
git apply -p1 proposed/interdiff-checkmark.patch
git apply -p1 proposed/interdiff-forced-colors-status-icons.patch
git apply -p1 proposed/interdiff-svg-optimization-required.patch
git apply -p1 proposed/interdiff-svg-cleanup.patch
git apply -p1 proposed/interdiff-svg-optimization-status-family.patch
git apply -p1 proposed/interdiff-loader-currentcolor.patch
git apply -p1 proposed/interdiff-svg-metadata-normalization.patch
```

Each patch is small and independently reviewable. Nothing here has been pushed upstream or posted to the issue/MR.

### Tests

```sh
python3 proposed/tests/checkmark_regression.py
python3 proposed/tests/forced_colors_status_icons.py
python3 proposed/tests/svg_cleanup_test.py
python3 proposed/tests/svg_optimization_pilot.py
python3 proposed/tests/svg_optimization_status_family.py
python3 proposed/tests/loader_dark_test.py
python3 proposed/tests/svg_properties_test.py
```

The repository includes only the **changed-file fixture subset** needed by these checks under `after/` and `proposed/`; it is not a full Drupal theme. The full-tree validation report in `proposed/reports/validation.json` was generated from the complete proposed theme.

## Headline findings

- The MR removes/relocates SVG assets but leaves **no broken SVG file references** (80 references resolved, 0 missing in the after tree).
- Missing variants: **`search-muted` / `search-muted-rtl`** (autocomplete) and **`pretint/edit-inverse`** (media-library dark mode). A dark disabled select chevron also needs a decision.
- **77 original assets have no after-side target**, but 0 of their exact paths are still referenced in the after tree. They are mostly intentional colour-variant/consolidation removals, not missing files.
- Confirmed fixes included here:
  - dark-mode disabled checkbox contrast (`2.85:1 → 5.85:1`)
  - status-report icons disappearing in forced colours
  - 14 unused assets recommended for removal (optional cleanup; also reflected in the proposed tree)
  - 4-decimal optimisation of `required.svg` and five status icons
- Optimisation result: after-side **74 files / 41,981 bytes → 61 files / 32,119 bytes**, a **23.5% reduction** (net of the new check-disabled-inverse pretint).
- CurrentColor audit: unused icons have no dark-mode rendering; `menu.svg` is inline and inherits, while the sticky loader was a real `background-image: currentColor` bug and now uses a currentColor mask.
- The asset gallery defaults to a checkerboard, outlines the AFTER thumbnail, and exposes per-asset byte sizes, zoom and uncompressed source diffs.
- The property matrix audits all 74 after-side SVGs for viewBox, dimensions, paint, stroke class, metadata, IDs, precision and rendered padding/ink; all 61 proposed SVGs now have consistent decorative ARIA metadata.
- `tabledrag-handle.svg` was corrected from 17×17 to 16×16; file types, pretints and logos are deliberately kept as separate families.

## Limits

- No full Drupal install with the complete MR theme was used. The live component tests used a local Drupal 12 baseline theme with relevant files/CSS applied surgically, then restored exactly.
- Forced-colours results are Chromium emulation, not native Windows High Contrast.
- File-type icons on dark surfaces, the autocomplete/media-library missing variants, and most of the 77 unresolved originals still need component-by-component review.
- Automated tests do not establish WCAG 2.2 AA conformance; manual and assistive-technology testing remains outstanding.

## Licence and provenance

Drupal is licensed under **GPL-2.0-or-later**. The patches, Drupal-derived SVGs, screenshots and evidence in this repository are derived from Drupal core and remain under that licence. See `LICENSE` and `NOTICE`.

This repository is not affiliated with or endorsed by the Drupal Association or the Drupal project.

## Not done

- No upstream push
- No issue/MR comment
- No full WCAG or SVG conformance claim
