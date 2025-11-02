# Implementation Plan: Gallery Banner, Title, and Subtitle

**Branch**: `009-gallery-banner` | **Date**: 2025-11-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-gallery-banner/spec.md`

**Note**: This plan has been extended to include subtitle functionality as a P3 priority feature.

## Summary

Add configurable banner image and title/subtitle display at the top of generated gallery pages. Banner spans full viewport width with CSS-based cropping. Title and optional subtitle overlay on banner with gradient for readability. All features are optional with graceful backward compatibility. Uses CSS object-fit for banner cropping, Pydantic validation for configuration, and Jinja2 conditional rendering for flexible display.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pydantic 2.0+ (data models), Jinja2 3.1+ (templates), Pillow 10.0+ (image metadata), PyYAML 6.0+ (config), Babel 2.13+ (i18n)
**Storage**: File-based (YAML configuration files, static image assets)
**Testing**: pytest with coverage, axe-core for accessibility testing
**Target Platform**: Static site generator (build-time tool), outputs HTML5/CSS3/vanilla JS for any web server
**Project Type**: Single project (static site generator with build tooling)
**Performance Goals**: HTML ≤30KB, CSS ≤25KB, JS ≤75KB initial load; banner images optimized <500KB; build time <5s for typical gallery
**Constraints**: Static-first (no backend runtime), no external dependencies in delivered assets, WCAG 2.1 AA accessibility, responsive 320px-4K viewports
**Scale/Scope**: Single feature adding 3 optional configuration fields, ~500 lines of new code (model validation, template logic, CSS), 6 user scenarios

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: Banner images copied as static assets, no backend runtime. CSS-only cropping.
2. ✅ **Performance budget accepted**: CSS additions ~2-3KB (within 25KB budget), HTML additions ~50-100 bytes (within 30KB budget), no JS changes.
3. ✅ **Accessibility commitment**: Semantic `<header>` + `<h1>`, descriptive alt text, WCAG 2.1 AA contrast (white text on gradient >7:1), axe tests planned.
4. ✅ **Content integrity**: Banner images copied with original filenames, reproducible builds maintained (deterministic file copy).
5. ✅ **Security/privacy**: No third-party scripts, banner images served from same origin, no CSP violations.
6. ✅ **Documentation**: README updated with banner config example, ADR for CSS cropping decision (vs server-side), quickstart guide complete.
7. ✅ **CI gates enumerated**: Asset budget checks (CSS ≤25KB), accessibility tests (axe), integration tests (banner rendering), build reproducibility maintained.

**Post-Design Re-Check (Phase 1 Complete)**: All gates remain satisfied. No constitution violations.
**Subtitle Extension**: Subtitle feature maintains all constitution compliance - no additional dependencies, performance impact minimal (<100 bytes HTML, <1KB CSS), accessibility maintained.

## Project Structure

### Documentation (this feature)

```text
specs/009-gallery-banner/
├── plan.md              # This file (extended for subtitle)
├── research.md          # Technical decisions (Q1-Q11)
├── data-model.md        # GalleryConfig + BannerData entities
├── quickstart.md        # Step-by-step implementation guide
├── spec.md              # Feature specification (6 user stories)
├── tasks.md             # Task breakdown
└── contracts/
    └── template-context.md  # Jinja2 template contract
```

### Source Code (repository root)

```text
src/
├── generator/
│   ├── model.py          # MODIFIED: GalleryConfig with banner_image, gallery_title, gallery_subtitle fields + validators
│   └── build_html.py     # MODIFIED: copy_banner_image(), prepare_banner_context(), template rendering
├── templates/
│   └── index.html.j2     # MODIFIED: <header> with conditional banner/title/subtitle rendering
└── static/
    └── css/
        └── gallery.css   # MODIFIED: .gallery-banner, .banner-image, .banner-title, .banner-subtitle styles

tests/
├── unit/
│   └── test_model.py     # NEW: GalleryConfig validation tests (banner_image, gallery_title, gallery_subtitle)
├── integration/
│   └── test_build.py     # NEW: Full build tests with banner/title/subtitle combinations
└── accessibility/
    └── test_a11y.py      # NEW: Banner accessibility tests (axe, contrast, alt text)
```

**Structure Decision**: Single project structure (static site generator). Changes are additions/modifications to existing files in established directories. No new top-level directories. Banner assets copied to `output_dir/images/banner/` at build time.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. This section intentionally left empty.
