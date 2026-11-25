# SVG optimisation — audit and verified pilots

**Scope:** the 74 SVG files in `after/core/themes/default_admin/images/` (41,981 bytes total). This is a measurement plus two bounded pilots and a cleanup batch, not a bulk rewrite.

## Opportunity, in order of value

| Item | Bytes | Share of total | Risk |
|---|---:|---:|---|
| Unused after-side assets | **11,068 removed**; 558 pending | 26.4% removed | Delete rather than optimise |
| Two identical file-type pairs | **1,546** redundant | 3.7% | Low; deduplicate the CSS URL, not the artwork |
| Whitespace/comments between tags | **1,411** | 3.4% | Low; lossless |
| SVGO 4-decimal path conversion, all 74 | **9,214** | 21.9% | **Not yet validated per file**; geometry/path data changes |
| SVGO 3-decimal path conversion | ~10,700 | ~25% | **Rejected**: measured pixel differences at 24–192px |

Total SVG payload is small. Removing dead assets is a bigger, safer win than minifying used paths. Delivery compression and caching will matter more than a few hundred bytes for the used set.

## Pilot: `icons/required.svg`

Tool: SVGO 3.3.5, run only in `/tmp`, no repository dependency.

Config properties: `preset-default` with `removeViewBox: false`, `cleanupIds: false`, `removeTitle/Desc/Metadata/Comments: false`, `convertColors: false`, `mergePaths: false`, `convertShapeToPath: false`, `convertPathData` at 4 decimals, `multipass: false`.

| File | Before | After | Saving |
|---|---:|---:|---:|
| `icons/required.svg` | 1,130 B | **958 B** (920 B SVGO + shared ARIA) | **15.2%** |
| `icons/logos/drupal.svg` (pilot only, not applied) | 1,610 B | 1,222 B | 24.1% |

Pixel comparison (transparent canvas, RGBA, exact per-pixel diff):

| Asset | 16px | 24px | 32px | 42px | 64px | 192px |
|---|---|---|---|---|---|---|
| required, 4 decimals | 0 | 0 | 0 | 0 | 0 | 0 |
| drupal, 4 decimals | 0 | 0 | 0 | 0 | 0 | 0 |
| required, 3 decimals | 0 | 5 px (Δ64) | 2 px (Δ64) | 2 px (Δ64) | 4 px (Δ64) | 23 px (Δ64) |
| drupal, 3 decimals | 0 | 0 | 0 | 0 | 0 | 8 px (Δ64) |

4-decimal output was pixel-identical at all tested sizes for both pilot assets. 3-decimal output was rejected. The path data was rewritten to relative/shorthand commands; this is **not** byte-identical geometry, so pixel equality at tested sizes is evidence, not proof at every scale or renderer.

Pilot patch: `proposed/interdiff-svg-optimization-required.patch` (1 file; 920 bytes). Report: this file.

## Rules for a batch pass

1. **Remove unused assets first.** Do not spend optimisation effort on the 16 files with no consumer.
2. **Do not remove `viewBox`, `currentColor`, IDs, titles/descriptions, metadata or licence comments.**
3. **Do not merge paths or convert shapes** unless each file is separately reviewed; stroke order, fill rules and holes can change.
4. **4 decimals is the floor for a batch pilot.** 3 decimals produced visible antialias differences in the pilot.
5. **Per-file pixel comparison** at 16/24/32/42/64/192 plus the actual component size, in light/dark/forced colours where relevant.
6. **Actual Drupal component test** for each optimised asset family before merging; standalone raster equality is not enough.
7. **No bulk optimisation mixed with functional fixes.** One family or one asset per commit.
8. **Preserve provenance.** If an asset has a licence/title/description, keep it.
9. **No mass reformatting** of files that are already small (under ~300 bytes) — the gain is negligible and review noise is high.
10. **Do not optimise removed/pretint assets blindly.** Pretints are frozen colour snapshots; confirm their mode/state table first.

## Decision

The first pilot applied `required.svg`. The batch execution below adds the 14-file unused-asset cleanup and the five-icon status family; other assets remain unchanged. Actual full-MR-theme Drupal testing is still pending.

## Applied: unused-asset cleanup

Removed from `proposed` after confirming no consumer references:

`appearance`, `blocks`, `bookmarks`, `content`, `files`, `media`, `nav-toggle-left`, `nav-toggle-top`, `people`, `reports`, `structure`, `user`, `pretint/chevron-down-default`, `pretint/remove-default`.

- **14 files / 11,068 bytes removed.**
- The corresponding registry variables and comment-table rows were removed.
- `search.svg` is kept for the pending muted-search fix; `chevron-left.svg` is kept pending the RTL decision.
- Test: `proposed/tests/svg_cleanup_test.py` (3 tests, passing).
- Patch: `proposed/interdiff-svg-cleanup.patch`.

## Applied: status-icon family at 4 decimals

Five used assets, same SVGO settings as the required.svg pilot:

| Asset | Before | Proposed (incl. ARIA) | Saving | Pixel check |
|---|---:|---:|---:|---|
| `icons/clock.svg` | 279 | 281 | -0.7% (metadata overhead) | identical 16–192px |
| `icons/server.svg` | 415 | 401 | 3.4% | identical 16–192px |
| `icons/database.svg` | 349 | 343 | 1.7% | identical 16–192px |
| `logos/drupal.svg` | 1,610 | 1,230 | 23.6% | identical 16–192px |
| `logos/php.svg` | 1,211 | 1,205 | 0.5% | identical 16–192px |

Total: **3,864 → 3,460 bytes; 404 bytes saved (10.5%)**. The shared decorative ARIA attributes add bytes, so the savings are smaller than the raw SVGO delta. Tests: `proposed/tests/svg_optimization_status_family.py` (5 tests, passing). Patch: `proposed/interdiff-svg-optimization-status-family.patch`.

The one 512px edge-pixel difference for the Drupal logo is at a non-UI scale; it is recorded rather than hidden. The optimized family has not yet been installed into a full MR-theme Drupal site; the existing live status test used the pre-optimisation assets and the forced-colours CSS fix.

## Deferred with reasons

- **Duplicate file-type pairs**: the two pairs are identical, but the compiled CSS inlines each SVG as a separate data URI. Removing a source file does not reduce the served CSS without introducing a shared custom property, and the MIME-specific filenames are part of the theme's current mapping. Defer.
- **Whitespace/comment minification**: measured at only 1,411 bytes across all 74 files, and it would touch most files. Low value and high review noise; defer until a bulk-format policy is agreed.

## Result

After-side baseline: **74 files / 41,981 bytes**.
Proposed tree after cleanup, all optimisation pilots and the shared decorative metadata: **61 files / 28,661 bytes** — **13,320 bytes less (31.7%)**. The proposed tree also adds `pretint/check-disabled-inverse.svg`, so the reduction is net of that addition. The compiled `icons.css` went from **40,615 to 25,587 bytes**.
