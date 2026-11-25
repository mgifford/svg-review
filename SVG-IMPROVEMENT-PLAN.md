# SVG improvement plan for Drupal Core (Default Admin)

**Baseline:** before `29b0a0b2256eb5ed27df6ec5e4e4e33142a717e8`; MR !16166 head `fe4adb4f942385912bb3244b570afa475cadf3bd`.
**Scope:** the 203 SVG paths in the patch, the inline SVGs in the theme, and the components that consume them.
**Goal:** dark mode as a first-class mode, WCAG 2.2 AA where the icons carry meaning, and no regression to light mode or forced colours.

This is a work plan, not a claim of conformance. Each item names its evidence and acceptance test.

---

## 1. Are SVGs missing from Drupal Core?

**Short answer:** no SVG file is missing by reference — a whole-core pass over the after tree resolved **80 SVG references with 0 missing files**, and every after-side SVG has a `viewBox`, no XML errors and no blocked content. What is missing is narrower: **CSS variables and variants that components still expect**, plus a few **state-specific assets**.

- Add `search-muted.svg` and `search-muted-rtl.svg` (autocomplete).
- Add `pretint/edit-inverse.svg` (media library dark/forced dark).
- Consider a dark disabled chevron variant; the current dark rule can win over the disabled rule.
- Do **not** restore the 77 unresolved originals; 0 of their exact paths are still referenced in the after tree.

The rest of this document is the implementation backlog.

### 1.1 Missing assets / variants to add

| Priority | Missing item | Why it matters | Evidence | Acceptance |
|---|---|---|---|---|
| **P0** | `images/icons/search-muted.svg` and `search-muted-rtl.svg` (or equivalent pretints) | Autocomplete inputs lose the magnifier entirely. The CSS references undefined variables. | `autocomplete-loading.module.pcss.css:51,57`; compiled `.css:58,64`; old assets were `868686/magnifier.svg` and `magnifier-rtl.svg` | Align the input again in LTR/RTL; icon visible at 16px in light, dark and forced colours |
| **P0** | `images/icons/pretint/edit-inverse.svg` (white/light pencil) | Media library edit button has no glyph in dark mode and forced-colours dark. Remove already has `remove-inverse`; edit has no counterpart. | `media-library-item.pcss.css:289,338`; compiled `.css:296,345`; `--admin-icon-edit-inverse` is undefined | Edit button visible in dark and forced dark; forced-light unchanged |
| **P1** | `images/icons/pretint/chevron-down-disabled-inverse.svg` (or reordered selector) | In dark mode `.dark-mode &` overrides the disabled select glyph with the **enabled** white chevron, so the disabled arrow looks active. | `form--select.pcss.css:15-27`; both selectors have equal specificity and the dark override comes later | Disabled select has a muted chevron distinct from enabled in dark mode; checked by computed style and screenshot |
| **P1** | A documented dark/forced variant or explicit decision for each remaining pretint | Pretints are frozen colour snapshots. Their usability across modes cannot be inferred from the master. | `pretint/` contains check-inverse, check-disabled, chevron-down-default/inverse/disabled, remove-default/inverse | Every pretint has a state/mode table and a tested consumer; unused pretints removed |

### 1.1a Suggested minimal asset specs

| File | Suggested content | Wiring and test |
|---|---|---|
| `images/icons/search-muted.svg` and `search-muted-rtl.svg` | Reuse the old `before/.../images/icons/868686/magnifier.svg` / `magnifier-rtl.svg` artwork as pretints, or add a mask-based wrapper. For dark mode, use a lighter token snapshot (for example `#adaeb3`) rather than reusing `#868686`. | Define `--admin-icon-search-muted` / `-rtl`; add a `.dark-mode` override; test the autocomplete input in LTR and RTL |
| `images/icons/pretint/edit-inverse.svg` | Copy `images/icons/pencil.svg` and replace `currentColor` with `#ffffff`. | Register `--admin-icon-edit-inverse`; use it in the existing dark/forced-dark media library rule; test edit and remove buttons |
| `images/icons/pretint/chevron-down-disabled-inverse.svg` | Copy `chevron-down.svg` and replace `currentColor` with a muted dark-surface token (for example `#adaeb3`). | Define the token; add a dark-mode `[disabled]` selector; test enabled vs disabled in dark mode |
| `images/icons/pretint/check-disabled-inverse.svg` | Already proposed; `#adaeb3`. | `--admin-icon-checked-disabled-inverse`; tested in the live permission page |

Do not bulk-generate these from every colour variant. Add only the mode/state variants that have a real consumer and a regression test.

### 1.2 Not missing: do not restore the 77 unresolved originals

- **77 originals have no after-side target**, but **0 of those paths are still referenced exactly in the after tree**. Their references moved or the assets are unused.
- **36 of the 77** were referenced in the before tree. Examples: `000f33/sort--inactive.svg`, `003ecc/sort--asc.svg`, `868686/magnifier.svg`, `82828c/checkmark.svg`, `media-edit.svg`.
- Many are colour variants of a now-canonical master (`checkmark`, `ex`, `questionmark`, `circle`, `trash`, `cog`, `plus`, `show`, `hide`, `key`). Restoring them would recreate the duplication the MR correctly removes.
- Expected family outcomes:

| Family | Correct outcome |
|---|---|
| checkmark / checked | One currentColor master + light/dark/disabled pretints where native controls need them; **do not restore colour variants** |
| ex / remove / close | Canonical close/remove master; inverse pretint for dark; verify background-image uses |
| questionmark | Canonical help master or documented replacement; no colour variants |
| circle | Radio ring/dot is now CSS; **no circle asset needed** unless a non-radio consumer exists |
| sort indicators | New `sort.svg`, `sort-asc.svg`, `sort-desc.svg`; update the reconciliation mapping (names changed from `sort--asc`) |
| breadcrumb arrows | Separator is now `/` CSS text and the first link uses `back-to-site`; **no arrow-breadcrumb asset needed** |
| spinners | CSS border spinner and loader; do not restore the old blocked spinner SVGs merely because the lab blocked previews |
| tabledrag | `drag`, `drag-y` and inline indentation SVG; `tabledrag-handle` is the forced-colours mask |
| media edit/remove | `pencil`/`close` masters + `edit-inverse` (missing) and `remove-inverse` |
| module/navigation integrations | Several old toolbar/module icons are unused in core; removal is justified, not a missing icon |

### 1.3 Unused additions: cleanup status

**Removed in the proposed tree (14 assets / 11,068 bytes):** `appearance`, `blocks`, `bookmarks`, `content`, `files`, `media`, `nav-toggle-left`, `nav-toggle-top`, `people`, `reports`, `structure`, `user`, `pretint/chevron-down-default`, `pretint/remove-default`. Variable definitions and comment rows removed too.

**Kept pending (2):**
- `search.svg` — needed for the missing `search-muted` fix.
- `chevron-left.svg` — pending the RTL/breadcrumb decision.

`menu.svg` is used inline in `menu-local-task.html.twig` and is not unused.

- `search.svg` is unused because the muted search variants are missing; keep the master only once it has a consumer.
- `chevron-left.svg` is unused; use it for a real RTL/breadcrumb need or remove it.
- The rest are unused registry entries. Keeping them adds dark-mode and forced-colours surface with no component to test.
- The theme's own registry comment says “Only add a property when theme CSS uses it.” Bring the assets and variables back in line with that rule.

### 1.4 Inline SVGs that need attention

- `templates/navigation/menu-local-task.html.twig:30` includes `images/icons/menu.svg` inline inside a labelled button. Add `aria-hidden="true"` / `focusable="false"` to the SVG so the button's `aria-label` is the only announced name.
- `templates/admin/indentation.html.twig:13-35` contains an inline tabledrag tree SVG with hard-coded `stroke="#888"`. Use `currentColor` (or a documented token) and `aria-hidden="true"` / `focusable="false"`; verify light, dark and forced colours.

---

## 2. Dark mode as a first-class citizen

### 2.1 Policy

1. **Masters are monochrome and use `currentColor`** unless the artwork is intentionally multicolour (file-type/brand marks).
2. **Prefer CSS masks** for monochrome icons so `background-color`/`currentColor` determines the visible colour. Use background-image only where the component cannot host a mask (native `<select>`, `<input>`, `<input type=submit>`), and then use **pretints**.
3. **Never use a `currentColor` master as a background image** without a documented reason and a dark-mode override. `currentColor` in an external SVG resolves to black; the theme's own pretint comment already states this.
4. **Every pretint is state-and-mode-specific.** A single pretint may not serve light, dark and disabled states if its contrast differs.
5. **Forced colours uses system colours.** Use `CanvasText`, `LinkText`, `ButtonText`, `Highlight`, etc.; do not use a global `forced-color-adjust: none`.
6. **No hard-coded interface colours in inline SVG or masters.** Use `currentColor`/tokens; document exceptions (file-type artwork).
7. **Multicolour artwork stays multicolour.** Test it on dark surfaces; do not convert file-type icons to masks.

### 2.2 Audit findings to act on

| Priority | Finding | Where | Action |
|---|---|---|---|
| **P0** | `--admin-icon-edit-inverse` undefined | `media-library-item.pcss.css:289,338` | Add pretint; test dark/forced dark |
| **P0** | `--admin-icon-search-muted` / `-rtl` undefined | `autocomplete-loading.module.pcss.css:51,57` | Add muted LTR/RTL assets or a mask-based wrapper |
| **P1** | `--admin-icon-loader` used as background image while master is `currentColor` | `more-actions.pcss.css:66` | Measure on the sticky button background in dark mode; use a system/token colour or a pretint |
| **P1** | `--admin-icon-edit` used as background image in light mode | `media-library-item.pcss.css:105,282` | Verify black-on-light; pair with the new edit-inverse |
| **P1** | Status-report icons disappear in forced colours | `system-status-report-general-info.pcss.css:58-68` | **Proposed patch:** `background-color: CanvasText` under forced colours; verified on `/admin/reports/status` |
| **P1** | Intrinsic file-type icons have no dark adaptation | `file.pcss.css:30-69`; 14 `file-types/*.svg` | Test the file widget, media library and attachment lists on dark surfaces; add dark artwork only if the light artwork fails |
| **P2** | Disabled select glyph uses the enabled white inverse in dark mode | `form--select.pcss.css:15-27`; computed dark disabled select uses the `%23ffffff` chevron with `opacity: .7` and a disabled border | Add a muted dark disabled variant or reorder the rules; the state currently relies on opacity/border, not the glyph |
| **P2** | Checked+disabled checkbox in dark mode | `form--checkbox-radio.pcss.css:225` | **Proposed patch:** `check-disabled-inverse` (#adaeb3), measured 2.85:1 → 5.85:1 |
| **P2** | Tabledrag inline tree uses hard-coded `#888` | `indentation.html.twig:13-35` | `stroke="currentColor"`; verify dark/forced |

### 2.3 Dark-mode acceptance tests

- Every **meaningful** icon remains visible at its actual component size in light **and** dark.
- Relevant states remain distinguishable: checked, unchecked, selected, disabled, error, sort asc/desc, drag handle, focus, hover.
- Measured non-text contrast against the adjacent background is **≥3:1** for meaningful graphics. Disabled controls are exempt from SC 1.4.11, but states should still be discernible; do not use the exemption to hide a regression.
- No `background-image` with a `currentColor` master is unaccounted for.
- Every pretint appears in a state/mode table and is covered by a component test.
- Intrinsic multicolour icons are tested on the real dark surface; if they fail, supply dark artwork, not a mask silhouette.
- The test is performed in the actual Drupal component, not only in the standalone gallery.

---

## 3. Forced-colours plan

| Priority | Task | Acceptance |
|---|---|---|
| **P0** | Status-report icon masks: system-colour background (patch ready) | All five status icons visible in Chromium forced light and forced dark; actual `/admin/reports/status` screenshot |
| **P0** | Media library edit icon: add `edit-inverse` and verify the forced-dark rule | Edit and remove both visible in forced light/dark |
| **P0** | Autocomplete search: restore muted search glyph; test forced colours | Magnifier visible, or intentionally native/hidden |
| **P1** | Audit every `mask-image` + `background-color` pair for an author colour that forced colours will replace with Canvas | No icon disappears against Canvas/CanvasText; documented system colour per case |
| **P1** | Keep `forced-color-adjust: none` scoped to individual masks only, never globally | Grep check: no global opt-out |
| **P1** | Verify tabledrag `LinkText` fallback (visible in current Chromium tests) and select `appearance: revert` | No regression across forced light/dark |
| **P2** | Native Windows High Contrast verification | Required before claiming forced-colours readiness; Chromium emulation is not enough |

**Do not** treat a forced-colours simulation as native Windows evidence. Record which combinations are emulated and which are untested.

---

## 4. SVG quality policy

### 4.1 Required for every interface SVG

- Well-formed XML and correct SVG namespace.
- No scripts, event handlers, `foreignObject`, external `href` or external `url()`.
- Unique IDs within each document; all internal references resolve.
- A valid, non-zero `viewBox`; no negative dimensions.
- No unintended clipping; internal detail preserved.
- `currentColor` for monochrome artwork; no accidental hard-coded hex unless a pretint or multicolour artwork.
- Correct stroke/fill rules, line caps and joins preserved from the original.
- No bulk optimisation or reformatting mixed with functional change.
- Licence/provenance retained.
- Reasonable decimal precision; no arbitrary path rewriting.

### 4.2 Per-asset actions from this audit

| Asset / group | Finding | Action |
|---|---|---|
| **Masters** (33 mask-only assets) | Render through `mask-image`; colour comes from the component | Keep `currentColor`; test each consuming component in light/dark/forced |
| **Background-only assets** (20) | Intrinsic colours; `currentColor` renders black | Review the 20; convert to mask where a wrapper exists; otherwise add pretints/state variants |
| **Mixed assets** (4: `check`, `chevron-down`, `close`, `pencil`) | Used both as mask and background image | Document both consumers; do not judge them from one preview mode; test both code paths |
| **File-type icons** (14) | Intentionally multicolour; `aria-hidden`/`focusable` present | Test on dark surfaces; keep multicolour; do not mask |
| **Pretints** (7) | Frozen colours; several state combinations untested | Build the pretint state matrix; add `edit-inverse`; remove unused `chevron-down-default` and `remove-default` |
| **Status icons** (5) | Mask over author background disappears in forced colours | System-colour patch |
| **Inline menu SVG** | Included in a labelled button without `aria-hidden` | Add `aria-hidden="true"` and `focusable="false"` |
| **Inline indentation SVG** | Hard-coded `#888`; no ARIA hiding | Use `currentColor`; `aria-hidden="true"`; dark/forced test |
| **Unused additions** | 14 removed; 2 pending | `search` needs the muted-search fix; `chevron-left` awaits the RTL decision |

The after inventory has **0 structural errors** and **no missing viewBoxes**; the 21 paint-value warnings are the 14 multicolour file-type icons and 7 pretints, which are expected but require the dark/forced review above.

The usage counts follow custom-property aliases (for example `--messages-icon: var(--admin-icon-info)`) and inline template includes. A first-pass scanner that ignored aliases reported `info.svg` as unused; it is actually a mask in the messages component. `menu.svg` is used inline in `menu-local-task.html.twig`, not in CSS, and is counted as image-only.

---

### 4.3.1 High-use optimisation

The first family beyond required/status was selected by repeated UI use: hamburger/menu, chevrons, pager arrows, checks, close/plus, sort, loader and tabledrag. The supplied hamburger/logo files were validated, their lost viewBox/ARIA restored, and 4-decimal conversion applied only after pixel checks. **21 files saved 562 SVG bytes**; compiled `icons.css` dropped from **28,725 to 27,233 bytes** for that pass. The menu is pixel-identical at 16–512px; logos are exact at UI sizes with edge-pixel differences recorded at 192px+.

Report: [high-use-optimization.md](proposed/reports/high-use-optimization.md); patch: `proposed/interdiff-svg-high-use-optimization.patch`; tests: `compiled_icons_test.py` and `svg_optimization_status_family.py`.

### 4.4 `currentColor` in dark mode

`currentColor` only works when the SVG inherits a CSS colour. It does **not** work through an SVG used as a CSS `background-image`: the image is rasterised on its own and `currentColor` becomes black. This is why several after-side assets look black on a dark preview even when the asset itself is not used.

Rules:

1. **Mask or inline** currentColor icon: safe in dark mode; the CSS colour supplies the visible paint.
2. **Background image** currentColor icon: unsafe; use a mask/pseudo-element, an inline SVG, or a tested mode-specific pretint.
3. **Unused** currentColor icon: no dark-mode rendering exists. Remove it or attach it to a real component; do not treat its black `<img>` thumbnail as a component failure.

The unused after assets are recommended for removal; the proposed working tree removes them. This is optional cleanup, not an MR deletion. `menu.svg` is inline and inherits correctly. `loader.svg` was used as a `background-image` in the sticky form actions; the proposed fix draws it through a pseudo-element with `background-color: currentColor` and a mask, with a reduced-motion fallback. See `proposed/reports/dark-mode-currentcolor.md`, `proposed/interdiff-loader-currentcolor.patch` and `proposed/tests/loader_dark_test.py`.

### 4.3 SVG optimisation

Optimisation is a **separate, later phase**. Do not mix path rewriting with correctness fixes.

Baseline: **74 files / 41,981 bytes**. The measured opportunity is:

| Item | Bytes | Share | Risk |
|---|---:|---:|---|
| 14 unused after-side assets (recommended removal) | 11,068 | 26.4% | Optional cleanup; 2 remaining pending decisions |
| Two identical file-type pairs | 1,546 redundant | 3.7% | Deferred: compiled CSS inlines both data URIs; source deletion alone does not reduce served CSS |
| Whitespace/comments between tags | 1,411 | 3.4% | Deferred: low value and high review noise |
| SVGO 4-decimal path conversion, all 74 | 9,214 | 21.9% | Family pilot only: required + five status icons applied |
| SVGO 3-decimal path conversion | ~10,700 | ~25% | Reject: visible pixel differences at 24–192px in the pilot |

**Applied pilot:** `icons/required.svg`, SVGO 3.3.5 with `viewBox`, IDs, titles/descriptions, metadata, comments and `currentColor` preserved; no path merging/shape conversion; 4-decimal path data. Result: **1,130 → 920 bytes (18.6%)**, **0 differing pixels at 16/24/32/42/64/192px**. A 3-decimal version produced differences; it was rejected. `logos/drupal.svg` also produced a pixel-identical 4-decimal variant (1,610 → 1,222 bytes) but is not applied.

Rules:

1. Remove unused assets before optimising used ones.
2. Preserve `viewBox`, `currentColor`, IDs, titles/descriptions, licence/provenance and state variants.
3. Do not merge paths, convert shapes, remove `viewBox`, or strip metadata.
4. Use **4 decimals** as the batch floor; 3 decimals is not visually safe in the pilot.
5. Compare pixels at 16/24/32/42/64/192 and at the actual component size; test alpha, dark, forced colours and masks.
6. Test the real Drupal component before merging a family.
7. One asset or one family per commit; no bulk rewrite.
8. Do not optimise tiny files where the gain is negligible and review noise is high.
9. Do not optimise pretints until their mode/state table is final.

**Result so far:** after-side 74 files / 41,981 bytes → proposed 61 files / 31,557 bytes, a **24.8% reduction**; compiled `icons.css` 40,615 → 27,233 bytes, including the 14-file cleanup, the required/status pilots, and the new `check-disabled-inverse.svg`.

Reports: `proposed/reports/svg-optimization-pilot.md`.
Patches: `proposed/interdiff-svg-cleanup.patch`, `proposed/interdiff-svg-optimization-required.patch`, `proposed/interdiff-svg-optimization-status-family.patch`.
Tests: `proposed/tests/svg_cleanup_test.py`, `svg_optimization_pilot.py`, `svg_optimization_status_family.py`.

### 4.5 SVG property normalisation

The property matrix ([proposed/reports/svg-properties.html](proposed/reports/svg-properties.html)) audits all 74 after-side SVGs for viewBox, intrinsic dimensions, currentColor/hardcoded paint, stroke class, caps/joins, fill opacity, path/shape/group counts, IDs, aria/title metadata, external references, path precision and rendered padding/ink/centre metrics.

Applied metadata normalisation:

- all **61** proposed SVGs have `aria-hidden="true"` and `focusable="false"`;
- all have a viewBox; no IDs, external refs, scripts or foreignObject;
- `tabledrag-handle.svg` corrected from 17×17 to **16×16** to match its viewBox;
- the proposed images directory is now complete for regression tests.

The standard ([proposed/reports/svg-property-standard.md](proposed/reports/svg-property-standard.md)) keeps families separate: 24-grid UI masters, 16-grid UI, pretints, file types and logos. It does **not** force file types or logos into the 24 grid, and it does **not** flatten deliberate stroke-weight classes. Optical padding, fill accents, stroke exceptions and path precision remain family-by-family visual decisions.

Patch: `proposed/interdiff-svg-metadata-normalization.patch`. Test: `proposed/tests/svg_properties_test.py`.

## 5. WCAG 2.2 AA checklist for the icon work

These are the checks to run per affected component. They do not replace manual testing or testing with disabled people.

| Criterion | What to verify for icons | Evidence to record |
|---|---|---|
| **1.1.1 Non-text content** | Decorative background/mask icons are not announced; meaningful icon-only controls have a text alternative | `aria-hidden`/`focusable` on inline SVG; accessible name on buttons/links |
| **1.4.1 Use of colour** | Checked, selected, disabled, sort direction and error states are not conveyed by colour alone | Shape/position/state test, screenshots |
| **1.4.3 Contrast (minimum)** | Text labels and icon+text controls meet 4.5:1; large text 3:1 | Computed colours and contrast |
| **1.4.11 Non-text contrast** | Meaningful icon graphics, state indicators and focus indicators meet 3:1 against adjacent colours | Pixel measurement at component size |
| **1.4.10 Reflow** | Icons remain usable at 320px and at 200%/400% zoom | Browser reflow test |
| **2.4.7 Focus visible** | Icon-only controls and handles have a visible focus indicator in light, dark and forced colours | Keyboard screenshots/computed outline |
| **2.4.11 Focus not obscured** | Sticky headers/toolbars do not hide focus on icon controls | Scrolling/focus test |
| **2.5.8 Target size (minimum)** | Icon-only controls are at least 24×24 CSS px or have sufficient spacing | Measured target boxes |
| **3.2.3/3.2.4 Consistency** | The same icon/action looks and behaves consistently across admin pages | Component inventory |
| **4.1.2 Name, role, value** | Icon-only buttons expose their name and state | Accessibility tree |
| **2.2.2/2.3.1 Animation** | Spinners/throbbers respect reduced motion where required; no distracting uncontrolled motion | Reduced-motion emulation |
| **1.3.4/1.4.10 RTL** | Directional icons and search/magnifier variants are correct in RTL | RTL screenshots; no missing `-rtl` assets |

**Do not claim WCAG conformance from SVG inspection or axe alone.** Record manual and assistive-technology gaps separately. Disabled controls are exempt from 1.4.11, but that exemption must not be used to ignore a state-visibility regression.

---

## 6. Test matrix

| Component | Light | Dark | Forced light | Forced dark | Sizes | RTL | Reduced motion | Status |
|---|---|---|---|---|---|---|---|---|
| Checkbox checked / disabled / error | ✅ | ✅ | ✅ | ✅ | 21px actual; 12/16/24 preview | n/a | n/a | Check fix proposed; dark disabled 5.85:1 |
| Select chevron | ✅ | ✅ | ✅ native | ✅ native | actual | ✅ | n/a | Disabled-dark state still to verify |
| Autocomplete search | ❌ | ❌ | ❌ | ❌ | 16px | ❌ | n/a | **Missing asset** |
| Media library edit/remove | ✅ | ❌ edit | ✅ | ❌ edit | 24px | ✅ | n/a | **Missing `edit-inverse`** |
| Status-report icons | ✅ | ✅ | ❌ before / ✅ proposed | ❌ before / ✅ proposed | 42px | n/a | n/a | Forced-colours patch ready |
| Tabledrag handle | ✅ | ✅ | ✅ `LinkText` | ✅ `LinkText` | 16px | ✅ transform | n/a | Chromium verified |
| File-type icons | ✅ | ⚠️ open | ⚠️ open | ⚠️ open | 16px | n/a | n/a | Actual widget test needed |
| Action-link icons | ✅ | ✅ | ✅ | ✅ | 1em | n/a | n/a | Mask-rendered |
| Toggle checkbox | ✅ | ✅ | ✅ | ✅ | actual | ✅ transform | ✅ transition | Check states in dark/forced |
| Inline menu / indentation | ✅ | ⚠️ | ⚠️ | ⚠️ | actual | ✅ | n/a | Fix ARIA + currentColor |

Legend: ✅ tested, ❌ missing/broken, ⚠️ needs verification.

---

## 7. Ordered implementation plan

### Phase A — stop the confirmed breakage (P0)

1. Add `search-muted.svg` / `search-muted-rtl.svg` (or a mask wrapper), register them, and test autocomplete in LTR/RTL.
2. Add `pretint/edit-inverse.svg`, register it, and test media library edit in dark and forced dark.
3. Keep the proposed status-report forced-colours patch (5 status icons).
4. Keep the proposed check-disabled dark pretint fix.
5. Add a regression test that fails on any `var(--admin-icon-*)` reference without a definition.

### Phase B — dark-mode correctness (P1)

1. Resolve the loader background-image/currentColor case on the sticky buttons in dark mode.
2. Verify the disabled-select dark chevron state; add a muted variant or reorder the rules.
3. Review all 20 background-image assets against dark surfaces; convert to masks where a mask host exists.
4. Review the 14 multicolour file-type icons in real file/widget surfaces; do not mask them.
5. Fix inline menu/indentation SVG semantics and hard-coded colour.
6. Add a lint rule: no `background-image` pointing at a `currentColor` master unless allowlisted with a test.

### Phase C — forced colours and state coverage (P1/P2)

1. Add system-colour handling for every mask-over-author-background case.
2. Build a pretint state/mode table; test each entry at the component.
3. Scope `forced-color-adjust`; no global opt-out.
4. Verify select/checkbox native appearance in forced colours.
5. Request native Windows High Contrast verification.

### Phase D — cleanup and accessibility (P2)

1. Remove or justify the remaining unused assets. 14 are recommended for removal (11,068 bytes); `search` and `chevron-left` remain pending.
2. Add `aria-hidden`/`focusable` to inline decorative SVGs.
3. Test icon-only controls for names, focus, target size (24px) and state.
4. Add RTL and reduced-motion cases for directional spinners/toggles.
5. Reconcile the family mappings (sort names, breadcrumb, spinner, media) in `reconciliation.json`; do not restore colour variants.

### Phase E — reporting and lab tooling

1. Update the gallery to remain **Auto (actual use)** by default, with per-asset `mask`/`background`/`mixed`/`unused` badges and a forced-colours window.
2. Add a CSS-variable lint, missing-file lint, and background-image/currentColor lint to the lab.
3. Cache rendering results by asset hash + browser + size + mode; separate inherited warnings from after-side regressions.
4. Produce updated JSON/Markdown reports and a small interdiff per phase.
5. Stop after each phase for review; do not push or post upstream.

---

### Phase F — optimisation after correctness (P2)

1. Remove or justify the unused assets. 14 removed; `search` and `chevron-left` pending.
2. Decide whether the duplicate file-type pairs justify a shared CSS data URI (deferred: no runtime gain from source deletion alone).
3. Decide whether the 1,411-byte lossless minification is worth the review noise (currently deferred).
4. Pilot 4-decimal optimisation on one used family; required and the five status icons are applied, with 16–192px pixel checks and one 512px logo edge-pixel difference recorded.
5. Batch only after per-file visual and component tests pass; keep each family in its own commit.

## 8. Missing/unknown information

- **No native Windows High Contrast testing** yet; Chromium forced-colours emulation is not a substitute.
- **No full Drupal install with the complete MR theme**; the checkmark and status tests used the lab baseline theme with the relevant files/CSS applied surgically, then restored exactly.
- **Dynamic and third-party references** can still exist outside core; absence of a literal reference is evidence, not proof of non-use.
- **77 originals** have no after-side target, but **0 exact stale references** remain in the after tree. Their disposition still needs a family-by-family reconciliation.
- **No full WCAG 2.2 AA or SVG conformance claim.** Automated checks cover only part of the requirements; manual and assistive-technology testing remains outstanding.
- **No visual-regression baseline for every component**; the current screenshots cover checkboxes, status icons, tabledrag and selects only.

---

## 9. Reference evidence

- [reconciliation.md](reconciliation.md) / [reconciliation.json](reconciliation.json) — checkmark dispositions
- [checkmark-evidence.md](proposed/reports/checkmark-evidence.md) — checkmark fix and live Drupal measurements
- [forced-colors-status-icons.md](proposed/reports/forced-colors-status-icons.md) — status-icon forced-colours fix
- [svg-optimization-pilot.md](proposed/reports/svg-optimization-pilot.md) — optimisation audit, cleanup batch and family pilots
- [dark-mode-currentcolor.md](proposed/reports/dark-mode-currentcolor.md) — currentColor consumer audit and loader fix
- [svg-property-standard.md](proposed/reports/svg-property-standard.md) — property matrix, family targets and metadata normalisation
- [patch-gallery.html](http://127.0.0.1:8770/proposed/reports/patch-gallery.html) — full asset gallery with Auto/Image/Mask and forced-colours views
- `proposed/tests/checkmark_regression.py` — 6 tests
- `proposed/tests/forced_colors_status_icons.py` — 3 tests
- `proposed/interdiff-checkmark.patch` — checkmark dark disabled fix
- `proposed/interdiff-forced-colors-status-icons.patch` — status icon fix
- `proposed/reports/screens/` — live Drupal and component screenshots

**Not pushed. Not posted. Next step: Phase A, one small commit per missing variant, tested against the live lab.**
