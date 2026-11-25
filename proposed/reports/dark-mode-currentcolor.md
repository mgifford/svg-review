# CurrentColor icons in dark mode — the 18 assets you flagged

**Scope:** `appearance`, `blocks`, `bookmarks`, `chevron-left`, `content`, `files`, `loader`, `media`, `menu`, `nav-toggle-left`, `nav-toggle-top`, `people`, `reports`, `search`, `structure`, `user`, `pretint/chevron-down-default`, `pretint/remove-default`.

This is a source/consumer audit, not a claim that every black thumbnail is a Drupal failure.

## Verdict summary

| Group | Assets | Dark-mode result | Verdict |
|---|---|---|---|
| Unused after assets | 14 | No Drupal consumer. As an `<img>`/`background-image`, `currentColor` resolves to black; as a mask/inline SVG it would inherit the text colour. | **Removed in the proposed cleanup**; not a component regression in the MR |
| Unused, still pending | `search`, `chevron-left` | Same as above; no consumer found in the after tree | **Not rendered anywhere**; remove or attach to a real component before treating them as supported icons |
| Inline currentColor | `menu.svg` | Included inline in `menu-local-task.html.twig`; `currentColor` inherits the surrounding text colour, so it is light in dark mode | **Not a bug**; the gallery’s Image mode shows it black, which is why it looked wrong |
| Background `currentColor` | `loader.svg` | Used as `background-image` in `more-actions.pcss.css`; `currentColor` cannot inherit through a background image and resolves to black | **Confirmed dark-mode bug**; needs a mask/pseudo-element or a mode-specific pretint |
| No after asset | `pretint/chevron-down-default`, `pretint/remove-default` | These originals have no after-side target; they are removed/renamed in the MR | No after image exists to compare |

## Why the gallery showed them as black

The gallery’s Image mode renders each SVG through an `<img>` element. An external SVG has no inherited `currentColor`, so the browser uses black. That is **not** how an inline SVG or a CSS mask behaves:

- **Mask:** the SVG shape is used as an alpha mask, and the CSS `background-color` supplies the visible colour.
- **Inline SVG:** `currentColor` inherits the text colour.
- **Background image:** the SVG is rasterised on its own; `currentColor` becomes black.

The gallery now labels this explicitly:

- **unused — no consumer**: shown on a light plate; no Drupal dark rendering exists.
- **inline currentColor — inherits**: `menu` is previewed as a mask.
- **background currentColor — black**: `loader` is marked as a real risk.

## The real loader problem

`after/core/themes/default_admin/css/components/more-actions.pcss.css:66`:

```css
background-image: var(--admin-icon-loader);
```

`loader.svg` uses `stroke="currentColor"`. A background image cannot inherit `currentColor`, so the sticky Save/Preview/Delete throbber is black. On a dark page, and on a transparent danger button, it disappears. The fix is to render the loader through a pseudo-element using `background-color: currentColor` plus a mask, or to provide a mode-specific pretinted loader.

![Sticky delete throbber in dark mode: the old background-image dot is invisible; the currentColor mask is visible on the danger button](screens/loader-dark-proposed.png)

The proposed pseudo-element is in `interdiff-loader-currentcolor.patch`. It keeps the button background intact, draws the loader with `background-color: currentColor` and a mask, preserves the throb animation through `mask-position`/`mask-size`, and disables the animation under `prefers-reduced-motion: reduce`.

Static harness: `proposed/test/loader-dark.html`. It uses the proposed compiled CSS and Drupal's real `body:has([data-drupal-selector="edit-delete"] + .ajax-progress)` selector.

## What to do

1. **Remove the 16 unused after assets** (`search` and `chevron-left` are the remaining two) or attach them to a component with a real mask/inline use.
2. **Keep `menu.svg` unchanged**; it is inline and inherits correctly.
3. **Fix `loader.svg` usage** with a currentColor mask/pseudo-element or a tested pretint.
4. Do not treat black `<img>` thumbnails of `currentColor` SVGs as evidence of a dark-mode failure; test the actual consumer.
