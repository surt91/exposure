````markdown
# Implementation Plan: Flexible Aspect-Ratio Image Layout

**Branch**: `007-flexible-layout` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-flexible-layout/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

**Primary Requirement**: Display images at their original aspect ratios without cropping, while maintaining consistent visual sizing and minimizing whitespace.

**Technical Approach**: Implement client-side JavaScript layout algorithm that calculates optimal image positioning based on dimensions. Algorithm will arrange images in rows with consistent heights, balancing visual weight and space efficiency. Layout calculations occur before first paint to prevent layout shift (CLS=0.0). Will evaluate existing libraries (Masonry.js, Justified Layout, Flickr's algorithm) versus custom implementation based on performance and bundle size constraints.

## Technical Context

**Language/Version**: Python 3.11+ (build tooling), HTML5/CSS3/ES Modules (delivery assets)
**Primary Dependencies**: Pydantic v2 (data models), Jinja2 (templating), Pillow (image metadata), PyYAML (config), Babel (i18n)
**Storage**: File-based (YAML configuration, static assets, no database)
**Testing**: pytest (unit/integration), Playwright (E2E), axe-core (accessibility)
**Target Platform**: Static site generators - outputs to any web server/CDN (GitHub Pages, Netlify)
**Project Type**: Web (static site generator) - generates HTML/CSS/JS from Python build tool
**Performance Goals**: Initial layout ≤500ms for 100 images, zero layout shift (CLS=0.0), ≤75KB JS initial load
**Constraints**: Client-side layout (no server runtime), must preserve 4:3 aspect-ratio fallback during transition, responsive 320px-1920px viewports
**Scale/Scope**: Galleries with 1-500 images per category, mixed aspect ratios (1:4 to 4:1), multi-category support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed** - Layout calculation happens client-side via JavaScript; no backend runtime required. Outputs remain static HTML/CSS/JS.
2. ✅ **Performance budget accepted** - Current JS is ~15KB. Layout algorithm estimated +10-20KB (total ~35KB, well under 75KB limit). HTML/CSS unchanged.
3. ✅ **Accessibility commitment** - Will maintain existing semantic HTML structure, keyboard navigation, ARIA landmarks. Axe tests already in CI will verify.
4. ✅ **Content integrity** - No changes to build process. Existing asset fingerprinting continues. Layout algorithm deterministic (same images → same output).
5. ✅ **Security/privacy** - No third-party scripts introduced. Pure JavaScript layout algorithm. CSP compatibility maintained.
6. ✅ **Documentation** - Will add ADR for layout algorithm choice. README quickstart unchanged (user experience identical).
7. ✅ **CI gates enumerated** - Existing gates cover this feature: asset budget tests (JS size), accessibility tests (layout changes), E2E tests (visual verification).

**Gate Status**: ✅ PASSED - All constitution requirements satisfied. No violations or exceptions needed.

**Post-Phase 1 Re-evaluation (2025-11-02)**:

After completing research, data model, and contract design, all constitution requirements remain satisfied:

1. ✅ **Static-first** - Confirmed: Using flickr/justified-layout library (5KB) for client-side calculation. No backend runtime added.
2. ✅ **Performance budget** - Verified: Library adds 5KB + 2KB integration code = 7KB total. New total: ~22KB JS (well under 75KB).
3. ✅ **Accessibility** - Verified: Semantic HTML preserved, keyboard nav unchanged, alt text required, axe tests will catch regressions.
4. ✅ **Content integrity** - Verified: Dimension extraction deterministic (Pillow), layout algorithm deterministic (same inputs → same outputs).
5. ✅ **Security/privacy** - Verified: Library vendored locally at `src/static/js/vendor/justified-layout.js`. No external dependencies. No tracking/analytics. CSP compatible.
6. ✅ **Documentation** - Created: ADR 0007 outlined in quickstart, README update planned.
7. ✅ **CI gates** - Verified: Asset budget tests will catch JS size, accessibility tests run automatically, E2E tests verify layout.

**Final Gate Status**: ✅ PASSED - Design complete with no constitution violations.

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
├── generator/                    # Python build tooling (unchanged for this feature)
│   ├── model.py                 # Add width/height fields to Image model
│   ├── scan.py                  # Extract dimensions from image files
│   └── build_html.py            # Pass dimensions to template
├── static/
│   ├── css/
│   │   └── gallery.css          # Update grid layout styles
│   └── js/
│       ├── gallery.js           # Current lazy loading, keyboard nav
│       └── layout.js            # NEW: Flexible layout algorithm
└── templates/
    └── index.html.j2            # Add width/height data attributes

tests/
├── unit/
│   ├── test_scan.py             # Test dimension extraction
│   └── test_layout_algorithm.py # NEW: Test layout calculations
├── integration/
│   ├── test_end_to_end.py       # Verify layout in generated HTML
│   └── test_asset_budgets.py    # Verify JS size under 75KB
└── accessibility/
    └── test_axe_a11y.py         # Verify no regressions

docs/decisions/
└── 000X-layout-algorithm.md     # NEW: ADR documenting algorithm choice
```

**Structure Decision**: This is a static site generator (Option 1: Single project). All layout logic lives in client-side JavaScript. Python tooling extracts image dimensions during build and passes them to templates. No backend runtime or separate frontend/backend split needed.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - This feature fully complies with all constitution requirements.
