# Component coverage

Revision: MR `fe4adb4f942385912bb3244b570afa475cadf3bd` on upstream `0387fb948f786bc344a5cc54aa0d98b8f552e378`.

| Component | Route | States | Result |
|---|---|---|---|
| Permissions | `/admin/people/permissions` | ['light', 'dark', 'forced-light', 'forced-dark'] | verified |
| Autocomplete field | `/node/add/article` | ['light', 'dark', 'RTL light', 'RTL dark', 'forced-light', 'forced-dark', 'loading'] | verified |
| Sticky form actions | `/node/add/article` | ['light', 'dark', 'RTL light', 'RTL dark', 'reduced motion', 'forced-dark'] | verified with injected Drupal AJAX progress markup |
| Media library selected item | `/node/add/article media widget` | ['light', 'dark', 'hover', 'forced-light', 'forced-dark'] | verified; edit control inserted with theme markup because the fixture widget display omits it |
| Status report | `/admin/reports/status` | ['light', 'dark', 'forced-light', 'forced-dark'] | verified |
| Menu administration tabledrag | `/admin/structure/menu/manage/main` | ['light', 'dark', 'RTL', 'dragging'] | verified |
| Select controls | `/node/add/article` | ['light', 'dark', 'forced-light', 'forced-dark'] | verified with a synthetic disabled select in the real theme context; no disabled select exists in the fixture |

## Untested

- Sort indicators and pager controls on views administration
- File-type icons in managed file fields and attachment lists
- Required marker, password show/hide, sidebar toggles
- Local task hamburger under overflow and narrow viewport
- Messages, warnings and errors
- Native Windows High Contrast
- Firefox and WebKit pixel/forced-colors runs
- Full AJAX Save/Preview round trip (progress markup was injected; node Save is not an AJAX submit)

Axe checks on `/admin/people/permissions`, `/admin/reports/status` and `/node/add/article` reported no WCAG A/AA violations in the tested state. This is not a conformance claim.
