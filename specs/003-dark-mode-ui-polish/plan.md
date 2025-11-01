# Implementation Plan: Dark Mode and UI Polish

**Branch**: `003-dark-mode-ui-polish` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-dark-mode-ui-polish/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a modern dark theme for the static image gallery using CSS custom properties and `@media (prefers-color-scheme: dark)`. Primary requirements include WCAG 2.1 AA contrast ratios (4.5:1 minimum), smooth visual transitions, and enhanced typography/spacing. Technical approach uses pure vanilla CSS (no frameworks) to preserve performance budgets (CSS ≤25KB). Adds ~2KB for dark color palette, animation timing, and typography improvements. JS framework/library rejected to maintain static-first architecture and avoid budget breach.

## Technical Context

**Language/Version**: Python 3.11 (build tooling), HTML5/CSS3/ES Modules (delivery assets)
**Primary Dependencies**: PyYAML (YAML parsing), Pillow (image metadata), axe-core (accessibility testing)
**Storage**: Static file generation - no runtime storage
**Testing**: pytest (Python tests), playwright (integration), axe-playwright-python (accessibility)
**Target Platform**: Static web (served via GitHub Pages, Netlify, or any CDN)
**Project Type**: Single project - static site generator
**Performance Goals**: Lighthouse ≥90 Performance/Accessibility on 3G throttled; 60fps animations
**Constraints**: HTML ≤30KB, CSS ≤25KB, JS ≤75KB initial load; WCAG 2.1 AA; reproducible builds
**Scale/Scope**: Gallery sites with 10-1000s of images; CSS-only dark mode; no JS framework dependency

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ Static-first approach confirmed - CSS-only dark mode, no backend runtime introduced
2. ✅ Performance budget accepted - Current CSS ~4KB, target dark mode adds ~2KB via CSS variables
3. ✅ Accessibility commitment - axe tests exist, will verify contrast ratios (WCAG 2.1 AA 4.5:1)
4. ✅ Content integrity - Existing build pipeline with SHA256 asset hashing remains unchanged
5. ✅ Security/privacy - No third-party scripts added, existing CSP documented in docs/hosting.md
6. ✅ Documentation - Will update README with dark mode info, create ADR 0003 for styling approach
7. ✅ CI gates enumerated - Existing gates (axe, performance budgets, reproducibility) cover dark mode

**Decision**: Pure CSS approach (CSS custom properties + prefers-color-scheme media query). 
**Rationale**: JS framework/library rejected because:
- Tailwind CSS: ~10-15KB gzipped even with PurgeCSS, risks budget breach
- CSS-in-JS libraries: Require JS runtime, violate static-first principle
- Vanilla CSS: 2KB addition preserves budgets, no build complexity, browser-native dark mode detection

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── static/
│   ├── css/
│   │   ├── gallery.css         # Main gallery styles - ADD dark mode variables
│   │   └── fullscreen.css      # Fullscreen modal styles - ADD dark mode variables
│   └── js/
│       ├── gallery.js          # No changes needed (functionality complete)
│       ├── fullscreen.js       # No changes needed (functionality complete)
│       └── a11y.js             # No changes needed (accessibility helpers)
├── templates/
│   ├── index.html.tpl          # Main template - may add <meta name="color-scheme">
│   └── fullscreen.html.part    # No changes expected
└── generator/
    └── build_html.py           # No changes needed (asset hashing unchanged)

tests/
├── accessibility/
│   └── test_axe_a11y.py        # Will verify dark mode contrast ratios
├── integration/
│   ├── test_asset_budgets.py   # Will verify CSS budget (≤25KB after dark mode)
│   └── test_fullscreen.py      # May add dark mode visual checks
└── unit/
    └── test_build_html.py      # No changes expected

docs/
└── decisions/
    └── 0003-dark-mode-styling-approach.md  # NEW ADR documenting CSS-only decision

config/
└── gallery.yaml                # Example data - no changes
```

**Structure Decision**: Single project static generator. Dark mode implemented purely in CSS files (gallery.css, fullscreen.css) via CSS custom properties and `@media (prefers-color-scheme: dark)` queries. No JavaScript changes required. No new build tooling or dependencies.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Pure CSS approach maintains all constitutional requirements.
