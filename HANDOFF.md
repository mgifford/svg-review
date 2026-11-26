# Handoff — Drupal MR !16166 SVG review

**Status:** MR !17967 is open. This is an independent review lab, not an official Drupal repository, and **not RTBC**.

- Review site: https://mgifford.github.io/svg-review/
- Repository: https://github.com/mgifford/svg-review
- Baseline before: `29b0a0b2256eb5ed27df6ec5e4e4e33142a717e8`
- MR head reviewed: `fe4adb4f942385912bb3244b570afa475cadf3bd`
- MR: https://git.drupalcode.org/project/drupal/-/merge_requests/16166
- Issue: https://www.drupal.org/project/drupal/issues/3603162
- Release tag: `v0.1-review`

## 2026-11-25 revision

**Status: branch and MR published.** Issue-fork branch `3603162-svg-revision`; MR !17967 is open. No Drupal.org issue comment has been posted.

- MR head verified again: `fe4adb4f942385912bb3244b570afa475cadf3bd`.
- Upstream `main`: `0387fb948f786bc344a5cc54aa0d98b8f552e378`.
- Rebased revision tip: `172c07efd8243f678eaa8697c47596eb62b3a747`.
- Start with [the revision report](proposed/reports/revision-2026-11-25.html) and [component coverage](proposed/reports/component-coverage.html).

The revision restores the autocomplete and media-edit icons, fixes dark disabled checkbox and select states, keeps status masks visible in forced colours, replaces the invalid sticky-loader pseudo-element, and makes tabledrag tree strokes use `currentColor`. It removes 15 unused assets and 20 registry entries, and adopts 45 pixel-identical SVGO results; 41 existing SVGs are smaller, 2 are larger, and 2 are new pretints.

Executed: 64 SVGs validated with 0 errors; reference audit 0 undefined/missing/unused; 46 regression tests; 14 theme Unit/Kernel tests with 209 assertions; axe 0 violations on three pages; Stylelint, Twig lint and Core CSS build checks pass.

Not executed: 8 functional PHPUnit tests (no test web server), native Windows High Contrast, Firefox or WebKit. Full AJAX Save/Preview was not exercised; Drupal's real progress markup was injected. No WCAG 2.2 AA claim.

The sections below describe the earlier nine-patch proposal and are historical.

## Read this first

Start with the [proposed reports index](proposed/index.html) for the current revision and the full report list.

The repo contains **proposed fixes, cleanup and optimisation** built on top of the MR. It is not a mirror of the MR. “After-side” means the MR tree; “proposed” means this working tree. “Unused — optional removal” is a cleanup recommendation, not an MR deletion.

The `unused` conclusion comes from a **literal source + CSS-variable alias scan**, not a rendered-page audit. See [the usage method](proposed/reports/usage-method.html).

## What is verified

- The nine-patch sequence applies cleanly to the MR head and reproduces the proposed theme exactly.
- **8 test suites pass**:
  - `checkmark_regression.py`
  - `forced_colors_status_icons.py`
  - `loader_dark_test.py`
  - `svg_cleanup_test.py`
  - `svg_optimization_pilot.py`
  - `svg_optimization_status_family.py`
  - `svg_properties_test.py`
  - `compiled_icons_test.py`
- Checkmark contrast fix was measured in a live Drupal 12 baseline with the MR assets/CSS applied surgically:
  - MR head dark disabled: **2.85:1**
  - Proposed dark disabled: **5.85:1**
  - Light mode unchanged: **3.78:1**
- Status-report forced-colours fix was checked against the live Drupal status page with the proposed status CSS.
- Every proposed SVG has a `viewBox`, `aria-hidden="true"` and `focusable="false"`; no IDs, external references, scripts or `foreignObject`.
- All optimisation files used per-file pixel checks at 16/24/32/42/64/192px.
- The compiled `icons.css` data URIs were re-synced with the source SVGs; `compiled_icons_test.py` verifies equivalence.
- The public Pages site returns 200 for the gallery, property matrix, ledger and reports.

## What is NOT verified

- **A full MR-theme Drupal install.** Live checks used the baseline theme with selected MR files/CSS applied, then restored.
- **Native Windows High Contrast.** Forced-colours results are Chromium emulation.
- **RTL for the loader mask**, and the loader's forced-colour active/delete state.
- **A rendered page/state usage audit.** The “unused” decision is source-level only and does not cover dynamic paths, contrib/custom code, or unexercised states.
- **Missing variants**: `search-muted`, `search-muted-rtl`, and `edit-inverse` were identified but not implemented.
- **The loader fix in a real component.** It is verified in a static harness only.
- **`help.svg` optimisation** was skipped because rounding changed 3 pixels at 24px and 2 at 32px.
- **`back-to-site.svg` and `cog.svg`** have recorded high-zoom/edge-pixel exceptions.
- **WCAG 2.2 AA conformance** has not been established; this is not an audit report.

## Patch order

Apply in this order to a checkout at the MR head:

| # | Patch | Purpose |
|---:|---|---|
| 1 | `proposed/interdiff-checkmark.patch` | Dark disabled checkmark contrast |
| 2 | `proposed/interdiff-forced-colors-status-icons.patch` | Status icons in forced colours |
| 3 | `proposed/interdiff-svg-optimization-required.patch` | Required marker optimisation |
| 4 | `proposed/interdiff-svg-cleanup.patch` | Remove unused after-side assets |
| 5 | `proposed/interdiff-svg-optimization-status-family.patch` | Status family optimisation |
| 6 | `proposed/interdiff-loader-currentcolor.patch` | Sticky loader currentColor/mask |
| 7 | `proposed/interdiff-svg-metadata-normalization.patch` | Decorative ARIA/viewBox consistency |
| 8 | `proposed/interdiff-svg-high-use-optimization.patch` | Repeated controls |
| 9 | `proposed/interdiff-svg-over-300-optimization.patch` | **Latest:** every SVG over 300 B |

```sh
git apply -p1 proposed/interdiff-checkmark.patch
git apply -p1 proposed/interdiff-forced-colors-status-icons.patch
git apply -p1 proposed/interdiff-svg-optimization-required.patch
git apply -p1 proposed/interdiff-svg-cleanup.patch
git apply -p1 proposed/interdiff-svg-optimization-status-family.patch
git apply -p1 proposed/interdiff-loader-currentcolor.patch
git apply -p1 proposed/interdiff-svg-metadata-normalization.patch
git apply -p1 proposed/interdiff-svg-high-use-optimization.patch
git apply -p1 proposed/interdiff-svg-over-300-optimization.patch
```

Do not apply patch 7 independently of patches 1–6: it is generated against the preceding working tree.

## Current totals

| Measure | Before / after |
|---|---|
| SVG set | 41,981 → **28,661 bytes** (−31.7%) |
| Compiled `icons.css` | 40,615 → **25,587 bytes** (−37.0%) |
| Proposed SVG count | 74 after-side → **61** (14 optional removals + 1 new pretint) |
| Over-300 files | 39 attempted; **38 adopted**; `help.svg` skipped |
| High-use set | 21 files; 562 SVG bytes; 1,492 compiled CSS bytes |

`menu.svg` is an important nuance: the supplied hamburger path is used, but the proposed source is 438 B versus the MR's 421 B because it restores viewBox/ARIA. The **compiled hamburger data URI** is still smaller: 432 B proposed vs 451 B after-side.

## Recommended upstream subset

Do **not** submit all nine patches as one change. Proposed split:

1. **Confirmed accessibility fixes:** checkmark, forced-colours status icons.
2. **Confirmed currentColor fix:** loader, after a real component test.
3. **Structural metadata:** optional, if maintainers want it.
4. **Cleanup and optimisation:** separate decisions. The optional removals need a rendered-usage audit; optimisation needs maintainer agreement on scope/design.

## Files to read

- [File-by-file change ledger](proposed/reports/change-ledger.html)
- [SVG property matrix](proposed/reports/svg-properties.html)
- [Property standard](proposed/reports/svg-property-standard.html)
- [CurrentColor dark-mode audit](proposed/reports/dark-mode-currentcolor.html)
- [Usage method and rendered-audit gap](proposed/reports/usage-method.html)
- [High-use optimisation](proposed/reports/high-use-optimization.html)
- [Over-300 optimisation](proposed/reports/over-300-optimization.html)
- [Full asset gallery](proposed/reports/patch-gallery.html)
- [Improvement plan](SVG-IMPROVEMENT-PLAN.html)

## Release rule

This release is a **review artefact**. No upstream Drupal push, no MR comment, and no RTBC claim were made. Any upstream submission needs explicit authorization and a maintainer-scoped subset.
