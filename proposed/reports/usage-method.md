# How “used” was determined — and what is still missing

There are three different questions, and they must not be conflated:

1. **Does a source file contain a literal reference to this SVG?**
2. **Is the SVG reachable through a CSS custom property or alias?**
3. **Does a rendered page actually paint it in a given state?**

The current “unused” label comes from questions 1 and 2, **not** question 3. That is why it is a cleanup candidate, not proof that no Drupal page can ever render the file.

## 1. Literal source scan (`usage.py`)

`usage.py` scans source files in the after-side theme (402 files in the current run):

- CSS, PCSS, Twig, PHP, JS/MJS/TS, YAML, HTML, JSON, theme/inc/module files.
- It looks for tokens matching:

```text
[\w./%+@~-]+\.svg(?:\?[^\s'\";)#]+)?
```

- It strips a query string such as `?v=123`.
- It resolves the token against the real path first.
- If that fails, it falls back to a **basename candidate** and records it as `basename candidate`.

It does **not** search for partial stems such as `files`, class names such as `.files`, or arbitrary strings. A reference must end in `.svg`.

Example that is found:

```css
background-image: url(../../images/icons/files.svg);
```

Example that is **not** found by this pass:

```css
background-image: var(--admin-icon-files);
```

or a path assembled at runtime.

Known limits, also recorded in `usage.json`:

- dynamic paths and generated code;
- aliases and CSS custom properties;
- references outside the scanned tree (contrib/custom modules/themes);
- SVG content inlined as a `data:image/svg+xml` URI (the filename disappears);
- runtime DOM changes.

Unmatched references are **not** treated as broken links; and a missing literal reference is **not** proof of non-use.

## 2. Alias/var analysis (separate from `usage.py`)

For the icon audit I separately parsed `--admin-icon-*` definitions and `var(--admin-icon-*)` usages, including aliases such as:

```css
--messages-icon: var(--admin-icon-info);
```

That produced the mode labels used in the gallery: `mask`, `background`, `mask,background`, `image` and unused. It is still **static source analysis**:

- a variable can be defined but never referenced;
- a reference can be inside a selector that never matches;
- the compiled CSS may inline a data URI, losing the filename;
- dynamic/JS-set variables are not captured.

The alias step is currently analysis code, not part of the committed `usage.py`. That should be added before “unused” is treated as authoritative.

## 3. What a rendered check requires

Run a browser against real Drupal pages and collect **computed styles plus DOM/resource evidence**, not source strings.

For every element and each of `::before`, `::after`, `::marker`:

- `background-image`
- `mask-image` / `-webkit-mask-image`
- `content` (it can contain a URL)
- `list-style-image`
- `border-image-source`
- `cursor`

Also collect:

- `<img src>`, `<object data>`, `<embed src>`
- `<use href>` and inline `<svg>`
- `performance.getEntriesByType('resource')`
- CSSOM rules as a secondary source (rules that exist but never match are not proof of rendering)
- decode `data:image/svg+xml` values and hash them against the known SVG content
- record the **page, state, element selector and CSS property** for each observation

States must be exercised explicitly:

- default, hover, focus-visible, active, checked, disabled
- light, dark, forced light, forced dark
- LTR and RTL
- open dialogs, autocomplete, media library, sticky form actions
- unauthenticated and authenticated pages, plus the permissions/roles that expose components

Chromium DevTools Protocol `CSS.forcePseudoState` can force `:hover`, `:focus`, `:active` and `:visited` for computed-style collection. Pseudo-element styles are visible through `getComputedStyle(element, '::after')`.

A minimal browser snippet:

```js
const found = new Set();

function urls(value) {
  for (const m of value.matchAll(/url\(["']?([^"')]+)["']?\)/g)) {
    found.add(m[1]);
  }
}

for (const el of document.querySelectorAll('*')) {
  for (const pseudo of [null, '::before', '::after', '::marker']) {
    const cs = getComputedStyle(el, pseudo);
    for (const prop of [
      'backgroundImage', 'maskImage', 'webkitMaskImage', 'content',
      'listStyleImage', 'borderImageSource', 'cursor',
    ]) {
      urls(cs[prop] || '');
    }
  }
}

for (const img of document.images) found.add(img.currentSrc || img.src);
for (const entry of performance.getEntriesByType('resource')) found.add(entry.name);
```

That output must then be mapped to theme paths, with data URIs hash-matched. Run it on a page/state manifest; a single page visit is not enough.

## What the labels should mean

| Label | Evidence |
|---|---|
| **Literal source reference** | Exact path or basename candidate found in source |
| **Alias source reference** | A used `var(--admin-icon-*)` resolves to the asset |
| **Rendered** | Observed in computed styles/DOM/network in a recorded state |
| **Not observed** | Not seen in the pages/states covered so far |
| **No source consumer found** | No literal or alias reference in scanned source; still not proof about unexercised UI |

This is why the current cleanup is **optional**. If we want to delete a file with confidence, the rendered check must cover the relevant components and states first.
