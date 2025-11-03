# Implementation Plan: Frontend Polish & Mobile Improvements

**Branch**: `011-frontend-polish` | **Date**: November 3, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-frontend-polish/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature enhances mobile user experience and visual polish for the static photo gallery through pure frontend improvements. Primary requirements include: (1) eliminating horizontal scrolling on mobile by fixing banner width calculations, (2) implementing touch swipe gestures for image navigation in the fullscreen overlay, (3) progressive image loading with immediate thumbnail display while original loads, (4) optimizing overlay layout to show larger images with better visual hierarchy, and (5) refining loading animations to be more subtle. Technical approach uses vanilla JavaScript touch event handlers (TouchEvent API) with horizontal gesture detection, CSS viewport unit adjustments for layout fixes, preloading strategy with smooth thumbnail-to-original transitions, and refined CSS animations. All changes maintain static-first architecture, accessibility (keyboard nav remains primary), and performance budgets (estimated +5KB JS, no new dependencies).

## Technical Context

**Language/Version**: Python 3.11 (build tooling), HTML5/CSS3/Vanilla ES Modules JavaScript (frontend)
**Primary Dependencies**: Jinja2 3.1+ (templating), Pillow 10.0+ (image processing), PyYAML 6.0+ (config), Pydantic 2.0+ (data models)
**Storage**: File-based (static HTML/CSS/JS generation, image assets, no database)
**Testing**: pytest 7.4+ (unit/integration), playwright 1.40+ (E2E), axe-playwright-python 0.1.4+ (accessibility)
**Target Platform**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+), mobile-first responsive design
**Project Type**: Static site generator (web) - Python build tool generates static frontend assets
**Performance Goals**:
  - Fullscreen overlay opens with thumbnail <100ms
  - Original image load cancellation on navigation <50ms
  - Swipe gesture recognition <16ms (60fps)
  - Layout reflow prevention (no horizontal scroll)
  - Lighthouse Performance ≥90, Accessibility ≥90
**Constraints**:
  - HTML ≤30KB, CSS ≤25KB, JS ≤75KB initial load (constitution)
  - Static assets only, no runtime backend
  - Must work offline after initial load (PWA considerations deferred)
  - Touch gesture detection without external libraries
  - Progressive image loading without framework dependencies
**Scale/Scope**:
  - Gallery with 60-100 images across 10-15 categories
  - 3 CSS files (~600 lines total), 4 JS modules (~800 lines total)
  - Desktop (1920x1080) to mobile (320px) responsive range
  - Single-page application behavior within static constraints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: All changes are pure frontend (CSS/JS modifications to existing static assets). No backend runtime introduced. Touch gesture detection implemented in vanilla JavaScript without external libraries.

2. ✅ **Performance budget accepted**:
   - Current CSS: ~600 lines across 3 files (estimated ~20KB gzipped)
   - Current JS: ~800 lines across 4 modules (estimated ~25KB gzipped)
   - Changes add ~150 lines JS (swipe detection, progressive loading) = ~5KB additional
   - Total remains well under limits: HTML ≤30KB, CSS ≤25KB, JS ≤30KB (well under 75KB)

3. ✅ **Accessibility commitment**:
   - Swipe gestures are supplementary to existing keyboard navigation (arrow keys)
   - Focus management remains unchanged (existing trapFocus implementation)
   - All interactive elements remain keyboard-accessible
   - Axe tests will verify no regressions in overlay accessibility
   - ARIA attributes preserved (aria-hidden, role="dialog" on modal)

4. ✅ **Content integrity**:
   - No changes to build process or asset generation
   - Static CSS/JS modifications only
   - Existing reproducible build strategy (hashing via build tool) unaffected
   - No new generated content or external resources

5. ✅ **Security/privacy**:
   - No third-party scripts added (vanilla JS implementation)
   - Touch event listeners use standard browser APIs (TouchEvent)
   - Progressive image loading uses existing image URLs (no external sources)
   - No analytics, tracking, or external requests introduced
   - CSP policy remains unchanged (no new script sources required)

6. ✅ **Documentation**:
   - README quickstart already exists and requires no updates
   - ADR will document touch gesture implementation approach (ADR-011-swipe-detection.md)
   - Quickstart.md will be generated for developer testing guidance
   - CHANGELOG entry will describe user-facing improvements

7. ✅ **CI gates enumerated**:
   - Existing Lighthouse CI will verify Performance ≥90, Accessibility ≥90
   - Existing axe-playwright tests will catch accessibility regressions
   - Existing asset budget tests will verify size constraints
   - New manual test: verify no horizontal scroll on 320px, 375px, 414px viewports
   - New manual test: verify swipe gestures work on iOS Safari, Android Chrome

**Status**: All constitution requirements satisfied. No violations. Ready for Phase 0 research.

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
│   │   ├── gallery.css       # Banner layout fixes, shimmer animation refinement
│   │   └── fullscreen.css    # Overlay layout optimization, category de-emphasis
│   └── js/
│       ├── fullscreen.js     # Touch swipe detection, progressive image loading
│       ├── layout.js         # Existing justified layout (unchanged)
│       ├── gallery.js        # Existing initialization (unchanged)
│       └── a11y.js           # Existing accessibility (unchanged)
├── templates/
│   └── gallery.html          # Jinja2 template (data attributes for original-src)
└── generator/
    └── build_html.py         # Build script (thumbnail generation already exists)

tests/
├── integration/
│   ├── test_asset_budgets.py          # Verify JS/CSS size limits
│   ├── test_accessibility.py          # Axe tests for overlay
│   └── test_responsive_layout.py      # NEW: Horizontal scroll checks
└── e2e/
    └── test_fullscreen_overlay.py     # NEW: Swipe gesture simulation
```

**Structure Decision**: Static site generator architecture (single project). Python build tooling generates static HTML/CSS/JS assets. All frontend improvements are pure client-side changes to existing CSS and JavaScript modules. No new dependencies, no backend changes, no template engine modifications beyond adding data attributes for progressive loading.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution requirements satisfied.

---

## Constitution Check Re-evaluation (Post Phase 1 Design)

*Re-checked after Phase 1 design artifacts (data-model.md, contracts/, quickstart.md) completed.*

**Date**: November 3, 2025

### Re-evaluation Results

1. ✅ **Static-first approach** - CONFIRMED
   - Design artifacts confirm vanilla JavaScript implementation
   - No frameworks or build-time dependencies added
   - All state management is client-side transient (TouchGestureState, ImageLoadingState, ModalState)
   - No server-side components or runtime backend introduced

2. ✅ **Performance budget** - CONFIRMED
   - Detailed code contracts show ~150 lines JS additions across fullscreen.js
   - CSS changes are minimal (<30 lines modifications to existing files)
   - Estimated final: HTML ≤30KB, CSS ~22KB, JS ~30KB (well within 75KB limit)
   - Progressive loading strategy minimizes perceived latency (<100ms thumbnail display)

3. ✅ **Accessibility** - CONFIRMED
   - Contracts document that touch gestures are supplementary to keyboard navigation
   - Focus management unchanged (trapFocus preserved)
   - Category label contrast verified (0.7 opacity = ~14:1 ratio, meets WCAG AA)
   - Quickstart includes axe test verification steps

4. ✅ **Content integrity** - CONFIRMED
   - Data model shows no changes to YAML schema or build process
   - Only DOM data attributes added (data-thumbnail-src, data-original-src)
   - Build reproducibility maintained (static HTML generation unchanged)

5. ✅ **Security/privacy** - CONFIRMED
   - Contracts show zero external dependencies or third-party scripts
   - Image() preloader uses existing static asset URLs
   - TouchEvent API is browser-native (no polyfills required)
   - CSP policy unchanged

6. ✅ **Documentation** - CONFIRMED
   - quickstart.md generated with comprehensive testing guide
   - research.md documents all technical decisions with rationale
   - contracts/javascript-interfaces.md defines public APIs and guarantees
   - ADR-011-swipe-detection.md pending (to be created during implementation)

7. ✅ **CI gates** - CONFIRMED
   - Quickstart documents manual and automated test procedures
   - Existing CI tests (Lighthouse, axe, asset budgets) will catch regressions
   - New test requirements documented: horizontal scroll checks, swipe gesture simulation

### Final Assessment

**PASS**: All constitution requirements remain satisfied after Phase 1 design. No violations introduced. No simpler alternatives would achieve the user requirements while maintaining constitution compliance. Ready to proceed to Phase 2 (task breakdown via /speckit.tasks command).

### Design Quality Validation

- ✅ Data model is minimal (client-side state only, no persistence)
- ✅ Contracts are well-defined (clear interfaces, performance guarantees)
- ✅ Quickstart is comprehensive (manual + automated testing procedures)
- ✅ Research decisions are justified (alternatives considered, rationale documented)
- ✅ No over-engineering detected (simplest approach for each requirement)

**Approved for implementation**.
