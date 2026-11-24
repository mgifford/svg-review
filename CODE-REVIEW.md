# Code review — SVG Review Lab

**Scope:** the four implementation files in this lab: `acquire.py`, `usage.py`,
`review.py`, `template.html`. This is a review of the *tool*, not a set of SVG
dispositions for Drupal MR !16166. Snapshots and implementation files were left
unchanged; the findings below are proposals, not applied fixes.

**Method:**

1. Read all four files and the historical evidence.
2. Ran the pinned-SHA fetch commands and extracted `core/themes/default_admin`
   at `29b0a0b...` and `fe4adb4...` into a temporary directory.
3. Ran `review.py` against (a) hand-built edge-case fixtures and (b) the real
   snapshots, then compared the result row-by-row with
   `evidence/svg-review-findings.json`.
4. Loaded `review.html` in Chromium via Playwright and exercised filtering,
   inspection, decisions, imports/exports, preview-size changes, blocked assets,
   and injected filenames/source.

**Bottom line:** the pipeline reproduces the historical baseline exactly
(194 before / 74 after / 204 rows; 77 unresolved, 63 relocated, 54 candidate
replacements, 10 unmatched — zero row differences), and its preview XSS
defences hold. The main weaknesses are in *attribution* (which references are
evidence for which asset), *provenance of automatic matches*, and *review-state
loss in the UI*. Those matter because this lab's output is used as evidence.

---

## Findings

### F1 — High — Reference suffix matching produces false `path` matches

`usage.py:20` treats a reference as an exact path when the reference string
merely ends with the asset path:

```python
resolved = (f.parent/token).resolve()
exact = [p for p in candidates
         if resolved == (root/p).resolve() or token.lstrip('/').endswith(p)]
```

Reproduction with a CSS file in the theme root:

* `url(../../other_theme/images/icons/a.svg)` is recorded as `match: "path"`
  for **this** theme's `images/icons/a.svg`.
* With both `images/icons/a.svg` and `x/images/icons/a.svg` present,
  `url(x/images/icons/a.svg)` is attributed to **both** assets.

Impact: shared basenames are common in Drupal themes (`checkmark.svg`,
`cog.svg`, `spinner.svg`). A cross-theme or nested reference can make a removed
icon look referenced, or inflate its reference count. This is exactly the kind
of claim the lab is supposed to prevent.

Suggested fix: only accept a resolved path against known roots (theme root,
Drupal root); remove the string-suffix fallback. If a suffix/relative-to-Drupal
form is needed, resolve it against the Drupal root and label it separately.
Add regression fixtures for `../`, `../../other_theme/`, and `x/images/...`.

### F2 — High — Automatic matches are exported as `selectedReplacement`

`review.py:67-73` picks `candidates[0]` automatically, and
`template.html:39` exports it as `selectedReplacement` with no indication that
no reviewer chose it. In the historical report:

* 127 before rows point at only 74 after targets.
* Seven different before assets each map to `images/icons/cog.svg`, and
  likewise for `hide`, `plus`, `show` and `trash`; `key` and `chevron-down`
  collect six each (colour variants collapsed by basename).
* The report has `chosen: {}`, so every one of those 54 "candidate
  replacements" is an automatic guess.

Impact: a consumer of the JSON can mistake an automatic proposal for a
confirmed mapping. It also silently merges many-to-one consolidations, which the
prompt asks to classify explicitly, without exposing that several assets share
one target.

Suggested fix: add fields such as `matchEvidence` (`hash` / `geometry` /
`basename` / `none`), `selectionSource` (`auto` / `reviewer`), and
`consolidatedFrom` (count or list) to each row. Do not label an automatic
target "selected"; keep `chosen` as the only reviewer-confirmed map and make the
UI show or filter unreviewed automatic matches.

### F3 — High — Unsaved decisions and notes are discarded on search or filter

`template.html:31` reloads the decision and notes from `localStorage` on every
`render()`. `template.html:32` wires `search` and `filter` input/change to
`nav()`, and `template.html:15` calls `render()` after every navigation.

Reproduced in Chromium: type `UNSAVED reviewer note`, choose
`Needs investigation`, then type one character in Search — the note and
decision become empty. The same happens when changing the replacement or
filtering. The saved record (if any) is keyed by the old pair, so changing the
replacement leaves an invisible orphan review.

Impact: silent loss of review work; a reviewer may believe a note was attached
to the row they are looking at.

Suggested fix: keep a dirty flag and do not overwrite unsaved edits when
navigating/filtering; at minimum prompt before discarding. On replacement
change, either migrate the review to the new key or tell the user that a new
row-level decision is starting and an earlier one is retained elsewhere.

### F4 — Medium — Rendering audit results go stale when preview size changes

`template.html:24` records results at the size current at audit start;
`template.html:32` changes size without invalidating them; the gallery continues
to show `Pass: Rendered nontransparent pixels at 64px` while previews render at
256px.

Reproduced: audit at 64 px, change Size to 256. Result text stays at 64 px,
`report().preview.size` is 256, `report().renderAudit.size` is 64, and the audit
still reports `completed`.

Impact: per-asset evidence and the visible preview can refer to different test
conditions, and the separate audit fields do not make that obvious enough for a
report reader.

Suggested fix: key cached results by `{hash, size, implementation, focus, palette}`
and mark the whole audit stale (or auto-rerun) when a test setting changes. The
report should state "results from size X; current preview size Y" explicitly.

### F5 — Medium — Blocked assets are not aggregated in the audit summary

`template.html:24` skips `z.blocked` assets. Per-asset reports do record
`rendering: {kind: 'not-tested', text: 'Blocked for safety'}`, but
`template.html:37-41` has no aggregate skipped count, and
`renderAudit.status` still says `completed`.

Real baseline: the two `003ecc/spinner*.svg` files are blocked because they use
`<style>` with an animation, so the audit covered 199 unique results across 268
asset entries (duplicates included) while presenting itself as completed. The
prompt explicitly says to inspect the blocked spinner styles rather than delete
them; the tool should make that omission countable, not just visible one asset
at a time.

Suggested fix: add `renderAudit.skipped = {blocked: n, hashes: [...]}` and a
sentence in the Markdown/JSON summary ("n assets not tested: blocked"). Keep
per-asset `not-tested` entries.

### F6 — Medium — `oldPathsInAfter` is dominated by basename noise

`review.py:90` calls `scan(roots[1], a)` to look for old paths in the after
tree. `usage.py:22` then records every same-basename asset when no exact match
exists.

Real baseline: all **157** hits for old paths are `basename candidate`; none is
an actual reference to a colour directory. 100 distinct removed variants appear
"referenced" only because the after CSS refers to the new base icon
(`../../images/icons/cog.svg`). Separately, the 16 entries in
`oldPathsInAfter.unmatchedImageReferences` are references to *new* after assets
(`check.svg`, `pretint/check-inverse.svg`, ...), not stale old paths.

Impact: a consumer can read `usage.json` as evidence that removed colour
variants are still referenced. The field name "unmatched image references"
makes the 16 new references look like problems.

Suggested fix: for old-path detection, accept only resolved exact hits; report
same-basename ambiguity in a separate field. Rename the unmatched list to
describe its actual scope (references with no before-side basename), or omit it
and compute "after references with no after-side asset" separately.

### F7 — Medium — Snapshot provenance is a ref name, not a content check

`review.py:84-87` reads `refs/heads/before|after` from `drupal.git` and puts them
in `provenance` as "export not independently verified". `acquire.py:15` checks
that the fetched commit equals the requested SHA, but nothing verifies that the
`before/`/`after/` trees currently on disk are the trees from those commits.

Impact: if a snapshot is edited, replaced, or left over from a different
checkout, the report still displays the pinned SHA. The honesty of the label
depends on a reader noticing it.

Suggested fix: at acquisition time write a manifest of `git ls-tree -r` paths,
modes and blob hashes; at review time compare the exported files with that
manifest (or recompute SHA-256 per file) and record `exportVerified: true/false`.
`git archive` already protects against transport corruption, but not against
later edits to the working directory.

### F8 — Medium — The historical evidence cannot be reproduced with the current tool

`evidence/svg-review-findings.json` is `schemaVersion: 4`, generated by Firefox
160, and contains no `usage` object; the current template emits `schemaVersion:
5` and embeds `usage`. `evidence/` has no `usage.json` or `inventory.json`,
although `AGENT-PROMPT.md` says to read `usage.json` and `README.md:40` tells
users to inspect it.

Impact: the baseline report and the current tool disagree on schema and on which
evidence exists, so a fresh run (which writes `usage.json`, `inventory.json`,
and a v5 report) is not directly comparable with the committed baseline. The
missing `usage.json` also means the source-reference step in the prompt has no
committed baseline to compare against.

Suggested fix: regenerate the evidence with the current code (including
`usage.json` and `inventory.json`), or record the generator version/schema in
the evidence README. Keep the schema version in the report and reject or
migrate unknown schemas on import.

### F9 — Medium — Reference scanning is theme-only, and unmatched detection is narrower still

`usage.py:6-24` scans only the `--before`/`--after` roots passed by
`review.py` (defaults: the two theme directories). Step 2 of the prompt requires
whole-Drupal-tree searches. `README.md:40` documents a manual `git grep`
substitute, but the generated `usage.json` does not mark itself as theme-scoped.

`usage.py:23` also reports unmatched references only when the token contains
`images/`. Reproduction: `url(img/missing.svg)` is silently ignored.

Impact: counts in the UI ("N source reference candidates") are not whole-core
counts, and broken references outside `images/` are invisible.

Suggested fix: add an explicit scan-root/scope option (Drupal root vs theme),
record the scope in `usage.json`, and report any unresolved `.svg` token that is
not `http(s)`/`data:` — with separate categories for "outside scanned roots".

### F10 — Low/Medium — Basename matching is case-insensitive even though Drupal on Linux is not

`usage.py:8` lowercases basenames. A reference to `images/icons/A.SVG` is
reported as a `basename candidate` for `images/icons/a.svg`. On a case-sensitive
server that reference is broken; on a case-insensitive local checkout it can
appear to resolve.

Suggested fix: match case-sensitively for path resolution; if a
case-insensitive match is found, report `caseMismatch` and do not present it as
ordinary usage. This also matters today because the lab is being run on macOS.

### F11 — Low — The geometry fingerprint is not a geometry check

`review.py:40` excludes `fill`, `stroke`, `color`, `stop-color`, `id` and
`class` from the hashed attributes, but includes the raw `style` attribute and
the whole attribute set. Reproductions:

* `fill="#000000"` vs `style="fill:#000000"` changes the fingerprint, producing
  "Geometry or non-paint attributes changed" even though paint is equivalent.
* Changing `id="a"` to `id="b"` does **not** change the fingerprint, so an ID
  rename (which can break `url(#...)` or author CSS) is unflagged.

Suggested fix: rename the finding to "serialized structure/non-paint attributes
changed", normalize `style` declarations into paint/geometry buckets, and
compare `id`/`class` separately where they are functionally relevant. Do not
describe the hash as geometry equivalence.

### F12 — Low — A deeply nested SVG crashes the whole run

`review.py:41` builds the fingerprint recursively; `review.py:59` catches only
`ET.ParseError` and `ValueError`. A 1,200-level `<g>` nest produced an unhandled
`RecursionError` and exit code 1.

Suggested fix: make the fingerprint traversal iterative (or impose and report a
depth limit), and catch unexpected per-asset exceptions so one pathological file
cannot abort the inventory.

### F13 — Low — Row findings duplicate side warnings in the report

`template.html:39` sets `findings: rowFlags(r)`, and `rowFlags` starts with
`assetFlags(before)` plus `assetFlags(after)`; `template.html:43` then prints
each side's warnings again. The historical Markdown shows repeated
"No viewBox" entries, and `warningRows` counts a row once while the prose lists
the same warning two or three times.

Suggested fix: keep `row.findings` for row-level findings only
(geometry/viewBox/replacement/missing), and keep side validation under
`before`/`after`; or de-duplicate by asset hash + message when rendering
Markdown.

### F14 — Low — No fallback if GitLab rejects a pinned-SHA fetch

`acquire.py:14` only runs
`git fetch --depth=1 URL <sha>:refs/heads/<label>`, with no fallback to a full
fetch or MR ref. I tested both pinned SHAs and they fetch successfully today, so
this is not a current failure; the prompt nevertheless anticipates servers that
reject unadvertised SHAs, and the script would then fail with no guidance.

Suggested fix: on fetch failure, fetch the MR ref (or full history) and then
verify `rev-parse` equals the requested SHA before archiving; fail with a
specific message if it does not.

### F15 — Low — Preview sizes and contrast coverage fall short of the prompt

`template.html:5` offers 16/24/32/64/128/256 px but not 12 px or actual
component sizes; the report's limitations correctly state that contrast,
geometry equivalence, and actual Drupal CSS are not checked. This is documented,
so it is listed as a coverage gap rather than a defect — but the prompt asks for
12/16/24 and component sizes, and for contrast of meaningful graphics.

Suggested fix: add 12 px and a free-form size input; when an asset's internal
`width`/`height` differs from the selected size, show it; add a documented
manual contrast checklist rather than implying automated coverage.

---

## What is solid

* **Reproduction is exact.** Fetching `29b0a0b...` and `fe4adb4...` from
  `git.drupalcode.org` succeeded, the extracted theme trees contain 194 and 74
  SVGs, and `review.py` produced 204 rows whose statuses (77 unresolved,
  63 relocated, 54 candidate replacements, 10 unmatched) and every row's
  before/after mapping match `evidence/svg-review-findings.json` exactly.
* **Preview injection is handled well.** `review.py:94` escapes `<` in the
  embedded JSON, and the template only uses `textContent`, `createElement`,
  and data URLs. A filename containing `<img src=x onerror=...>` and an SVG
  source containing `</script><script>...` did not execute, create a DOM image,
  or break the page in Chromium.
* **Unsafe SVG is blocked conservatively.** DTD/entity declarations, scripts,
  `<style>`, `foreignObject`, animation elements, event attributes, non-fragment
  `href`, and non-fragment `url()` values are flagged; duplicate/unresolved IDs,
  invalid/non-positive `viewBox`, negative dimensions, and empty title/desc are
  reported.
* **Deterministic and dependency-free.** No third-party packages; duplicate
  hashes are counted once in the audit; generated output ordering is stable.
* **Basic UI flow works.** The gallery, filters, inspect view, decision save,
  export, and rendering audit work in Chromium with no page errors (only the
  expected missing `favicon.ico` 404 from the test server).

## Maintainability observations

* **No automated tests.** The attribution bugs above were only visible because I
  built adversarial fixtures. A small stdlib `unittest` suite covering
  `usage.scan` (suffix, case, `../`, `images/` scope), `review.build`
  (many-to-one, relocation, added rows), the geometry fingerprint, and one
  malformed/deep SVG would prevent regressions cheaply.
* **The template is hard to review by construction.** Almost all CSS is on
  `template.html:2-5` and almost all JS on single very long lines (for example,
  `template.html:23` is over 2,000 characters). This is fine for an offline
  single-file tool, but it makes diffs and line-level review unreliable; keep a
  readable source and inline it into `review.html` at build time, or at least
  format it.
* **Outputs are written into the current working directory** (`usage.json`,
  `inventory.json`, `review.html`) with no `--out` option and no warning before
  overwriting. Running the lab twice from the same directory silently replaces
  earlier evidence; an output directory or an explicit overwrite flag would make
  runs safer.

## Not tested / unresolved

* This review did not make the 194 per-asset dispositions, run Drupal's CSS
  build/tests, render actual Drupal components, or test forced-colours/high
  contrast, focus, RTL, or reduced motion. Those remain the follow-up work in
  `AGENT-PROMPT.md`.
* The merge request itself was not inspected beyond the two pinned commits.
* Simulated palettes are not real forced-colours evidence; that limitation is
  already stated in the README and report.
* The exact W3C SVG conformance status of any asset was not assessed.

## Suggested minimal fix order

1. **Evidence correctness first:** F1, F2, F6 (scanner attribution and
   automatic-match provenance), with regression fixtures for each reproduction.
2. **Provenance and baseline:** F7, F8, F9 (content verification, schema/scope
   alignment in exported reports).
3. **Review-state correctness:** F3, F4, F5 (dirty state, audit cache key,
   skipped-asset accounting).
4. **Robustness/polish:** F11-F15 (fingerprint semantics, crash containment,
   report de-duplication, fetch fallback, preview sizes).

## Commands used (temporary directories, not the workspace)

```sh
# Pinned fetch and extraction
git init --bare /tmp/acqtest.git
git --git-dir=/tmp/acqtest.git fetch --depth=1 \
  https://git.drupalcode.org/project/drupal.git \
  29b0a0b2256eb5ed27df6ec5e4e4e33142a717e8:refs/heads/before
git --git-dir=/tmp/acqtest.git fetch --depth=1 \
  https://git.drupalcode.org/project/drupal.git \
  fe4adb4f942385912bb3244b570afa475cadf3bd:refs/heads/after
git --git-dir=/tmp/acqtest.git archive before core/themes/default_admin | tar -x -C before
git --git-dir=/tmp/acqtest.git archive after  core/themes/default_admin | tar -x -C after

# Real run
python3 review.py --before before/core/themes/default_admin \
                  --after  after/core/themes/default_admin

# Fixture runs for scanner, deep nesting, and geometry checks
python3 review.py --before before --after after
```

Browser tests used Chromium through Playwright at
`http://127.0.0.1:8766/review.html`; that temporary server was stopped after the
tests.
