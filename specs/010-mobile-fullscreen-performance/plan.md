# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Mobile users experience improved full-screen image viewing with true viewport-filling display, invisible navigation controls that auto-hide after 3 seconds, and instant perceived loading via ultra-low-resolution blur placeholders (20x20px, embedded as data URLs in HTML). Technical approach: extend existing Python build system (Pillow) to generate blur placeholders during thumbnail generation, enhance JavaScript fullscreen.js with Fullscreen API integration and control visibility state management, add CSS transitions for smooth progressive loading (blur → thumbnail → original).

## Technical Context

**Language/Version**: Python 3.11 (build tooling), HTML5/CSS3/Vanilla ES Modules JavaScript (frontend)
**Primary Dependencies**: Pillow 10.0+ (blur placeholder generation), Jinja2 3.1+ (HTML templating), Pydantic 2.0+ (data models), existing justified-layout.js vendor library
**Storage**: File-based (source images, generated thumbnails + blur placeholders, build cache JSON for incremental builds)
**Testing**: pytest (Python unit/integration), Playwright + axe-core (accessibility), manual mobile device testing (Chrome Mobile, Safari iOS)
**Target Platform**: Static site deployment (GitHub Pages, Netlify, any CDN), mobile browsers (iOS Safari 11.3+, Chrome Mobile 71+), desktop fallback
**Project Type**: Single web project (static site generator)
**Performance Goals**: Blur placeholders visible <50ms from page load, full-screen mode latency <100ms, control hide/show animations 300ms, each placeholder <1KB, total HTML size increase <30KB for 100 images
**Constraints**: HTML ≤30KB initial (constitution limit), CSS ≤25KB, JS ≤75KB, no external dependencies, Lighthouse Performance ≥90 on 3G throttle, WCAG 2.1 AA compliant
**Scale/Scope**: ~100-1000 images per gallery, blur placeholder generation adds ~2-5 seconds to build time, support mobile viewports 320px-768px width

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: No backend runtime introduced. Blur placeholders generated during build process (Python), all assets remain static files.

2. ⚠️ **Performance budget accepted (HTML ≤30KB, CSS ≤25KB, JS ≤75KB initial load)**:
   - HTML: Adding blur placeholders will increase HTML size. With ~100 images × ~800 bytes per data URL = ~80KB increase. **VIOLATION: Exceeds 30KB limit.**
   - CSS: New styles for blur placeholders, control visibility animations ~2KB. Within budget (current: ~18KB, after: ~20KB).
   - JS: Full-screen API + control visibility logic ~3-5KB. Within budget (current: ~45KB, after: ~50KB).

3. ✅ **Accessibility commitment**: axe tests already in place. Full-screen mode will maintain ARIA attributes, keyboard navigation, focus management. Control visibility doesn't affect accessibility (controls remain keyboard-accessible even when visually hidden).

4. ✅ **Content integrity**: Reproducible build maintained. Blur placeholders generated deterministically from source images. Build cache tracks blur placeholder hashes. No new versioning concerns.

5. ✅ **Security/privacy**: No third-party scripts added. Fullscreen API is native browser feature. Data URLs embedded inline (no external requests). CSP compliance maintained.

6. ✅ **Documentation**: Will update README with blur placeholder feature, mobile full-screen behavior. Will create ADR for blur placeholder approach and data URL size tradeoff.

7. ✅ **CI gates enumerated**: Existing performance budget checks will catch HTML size increase. Accessibility tests will validate full-screen keyboard navigation. Asset size limits require adjustment or alternative approach.

**GATE STATUS: CONDITIONAL PASS** - See Complexity Tracking for HTML size violation justification.

## Project Structure

### Documentation (this feature)

```text
specs/010-mobile-fullscreen-performance/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── blur-placeholder-generator.yaml    # Build-time API contract
│   ├── fullscreen-api.yaml                # Browser Fullscreen API usage
│   └── control-visibility-manager.yaml    # Frontend state management
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── generator/
│   ├── thumbnails.py          # MODIFIED: Add blur placeholder generation
│   ├── model.py               # MODIFIED: Add BlurPlaceholder data model
│   ├── build_html.py          # MODIFIED: Pass blur placeholders to templates
│   └── cache.py               # MODIFIED: Track blur placeholder in build cache
├── templates/
│   ├── index.html.j2          # MODIFIED: Embed blur placeholders as inline styles
│   └── fullscreen.html.j2     # MODIFIED: Add blur placeholder layer
└── static/
    ├── js/
    │   ├── fullscreen.js      # MODIFIED: Add Fullscreen API + control visibility
    │   └── gallery.js         # MODIFIED: Initialize blur placeholder loading
    └── css/
        └── [styles].css       # MODIFIED: Add blur placeholder + control visibility styles

tests/
├── unit/
│   ├── test_thumbnails.py     # MODIFIED: Add blur placeholder generation tests
│   └── test_model.py          # MODIFIED: Add BlurPlaceholder validation tests
├── integration/
│   ├── test_blur_placeholders.py  # NEW: End-to-end blur placeholder tests
│   └── test_asset_budgets.py     # MODIFIED: Update HTML size budget expectations
└── accessibility/
    └── test_fullscreen_a11y.py    # NEW: Full-screen keyboard navigation tests

docs/
└── decisions/
    └── 0012-blur-placeholder-strategy.md  # NEW: ADR for data URL vs external files
```

**Structure Decision**: Single project structure (static site generator). Python build tooling generates static assets (HTML/CSS/JS). Blur placeholder generation integrated into existing thumbnail pipeline. Frontend enhancements leverage existing vanilla JS modules.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| HTML size budget (30KB → ~110KB with data URLs) | Instant perceived load time critical for mobile UX. Blur placeholders eliminate "blank screen" experience and provide immediate visual feedback before any network requests complete. User research shows this dramatically improves perceived performance. | **External blur placeholder files**: Defeats purpose (requires network request, adds latency). **Larger thumbnails only**: Still requires network round-trip, ~200-500ms delay on 3G. **CSS background colors**: No visual preview of actual image content, poor UX. **Trade-off accepted**: 80KB HTML increase is one-time cost on initial page load, after which all images have instant previews. Progressive enhancement ensures functionality without placeholders. |

---

## Post-Design Constitution Re-Check

*Re-evaluation after Phase 1 design completion*

**Date**: December 8, 2025

### Constitution Compliance After Design

1. ✅ **Static-first approach**: Confirmed. All design artifacts (data models, contracts, quickstart) maintain static-first principle. No backend runtime introduced at any layer.

2. ⚠️ **Performance budget**: HTML size violation remains documented and justified in Complexity Tracking. Mitigation strategies identified:
   - Implement lazy blur placeholder loading (only embed for visible images)
   - Use CSS dominant color extraction as fallback for non-critical images
   - Add configuration toggle to disable blur placeholders entirely
   - **ADR required**: Document trade-off decision in `docs/decisions/0012-blur-placeholder-strategy.md`

3. ✅ **Accessibility commitment**: Design validates accessibility requirements:
   - Full-screen mode maintains keyboard navigation (Tab, ESC, Arrow keys)
   - Control visibility manager uses CSS `:focus-within` for keyboard accessibility
   - ARIA attributes preserved in fullscreen overlay
   - Screen reader announcements documented in contracts
   - Auto-hide behavior doesn't affect keyboard users

4. ✅ **Content integrity**: Build cache integration confirmed:
   - Blur placeholders tracked via SHA256 hashes
   - Cache invalidation strategy defined
   - Reproducible builds maintained (deterministic JPEG encoding)
   - Build cache version bump documented (1.0.0 → 2.0.0)

5. ✅ **Security/privacy**: Design review confirms no security concerns:
   - Data URLs are inline (no external requests, CSP compliant)
   - Fullscreen API is native browser feature (no third-party library)
   - No user data collection or tracking introduced
   - EXIF metadata privacy maintained (blur placeholders don't expose EXIF)

6. ✅ **Documentation**: Phase 1 artifacts complete:
   - ✅ `research.md` - Comprehensive research findings
   - ✅ `data-model.md` - Entity definitions and validation rules
   - ✅ `contracts/` - 3 API contracts (blur generator, fullscreen, control visibility)
   - ✅ `quickstart.md` - Developer setup guide
   - 🔲 ADR `0012-blur-placeholder-strategy.md` - To be created in implementation phase
   - 🔲 README update - To be done in implementation phase

7. ✅ **CI gates enumerated**: Testing strategy confirmed:
   - Unit tests: Blur placeholder generation, data model validation
   - Integration tests: End-to-end blur loading, asset budget checks
   - Accessibility tests: Full-screen keyboard navigation, screen reader compatibility
   - Performance tests: Lighthouse CI thresholds (FCP, LCP, CLS)
   - Manual tests: Mobile device testing (iOS Safari, Chrome Mobile)

### Final Gate Decision

**PASS WITH DOCUMENTED EXCEPTION**

The HTML size budget violation is accepted with the following conditions:

1. ✅ Justification documented in Complexity Tracking
2. ✅ Alternative approaches evaluated and rejected with rationale
3. ✅ Mitigation strategies identified (lazy loading, config toggle)
4. 🔲 ADR to be created documenting decision (implementation phase)
5. 🔲 Asset budget tests to be updated with new thresholds (implementation phase)
6. ✅ User-facing benefit clearly articulated (instant perceived performance)

**Ready to proceed to Phase 2 (Tasks)**: Use `/speckit.tasks` command to generate task breakdown.
