# Implementation Plan: High-Performance Image Preprocessing with WebP Thumbnails

**Branch**: `008-image-preprocessing` | **Date**: 2025-11-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-image-preprocessing/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add build-time image preprocessing to generate optimized WebP thumbnails for gallery display while preserving full-resolution originals for modal view. Thumbnails scale to 800px max dimension, achieving 90%+ file size reduction. Incremental builds detect changed images and skip regeneration. HTML templates serve WebP with JPEG fallback for browser compatibility.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Pillow 10.0+ (image processing), Pydantic 2.0+ (data models), Jinja2 3.1+ (HTML templating), PyYAML 6.0+ (config)
**Storage**: File-based (source images, generated thumbnails, build cache for incremental builds)
**Testing**: pytest 7.4+ (unit/integration), playwright (end-to-end), axe-playwright-python (accessibility)
**Target Platform**: Linux/macOS/Windows (build tooling), static file hosting (GitHub Pages, Netlify, any CDN)
**Project Type**: Static site generator (single project with CLI tool)
**Performance Goals**:
- Thumbnail generation: 100 images in <2 minutes on standard laptop
- Gallery page load: <3 seconds with 50 images on 10Mbps connection
- File size: 90%+ reduction for thumbnails vs originals, WebP 25-35% smaller than JPEG
**Constraints**:
- Static-first: no runtime server, all processing at build time
- Performance budget: thumbnails must fit existing HTML/CSS/JS limits (constitution compliance)
- Build must be reproducible and support incremental regeneration
**Scale/Scope**:
- Support galleries with 50-100+ images per category
- Handle source images up to 50MB, 20+ megapixels
- Multiple image formats: JPEG, PNG, GIF

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: All image preprocessing occurs at build time. Generated thumbnails are static assets committed to build output. No runtime server processing introduced.

2. ✅ **Performance budget accepted**: Thumbnails are designed to improve performance, not degrade it. HTML/CSS/JS payloads unchanged. Thumbnails reduce bandwidth by 85%+ compared to serving full-resolution images, directly supporting the <30KB HTML, <25KB CSS, <75KB JS limits by reducing page weight.

3. ✅ **Accessibility commitment**: Existing axe tests continue to cover generated HTML. Thumbnail implementation maintains semantic HTML (`<img>` tags with proper alt text). No accessibility regressions introduced.

4. ✅ **Content integrity**: Thumbnails are reproducible - same source image + settings = identical thumbnail hash. Thumbnail filenames include content hash for cache busting. Build cache tracks source image modification times for incremental regeneration. Source images remain in version control; thumbnails are build artifacts.

5. ✅ **Security/privacy**: No third-party scripts or services introduced. WebP conversion and resizing performed locally by Pillow. No external API calls. Existing CSP and header configuration in `docs/hosting.md` remains valid.

6. ✅ **Documentation**: README will document thumbnail generation in build process. Quickstart guide created in Phase 1. ADR for image preprocessing approach will be added to `docs/decisions/`.

7. ✅ **CI gates enumerated**: Existing gates (performance budget, accessibility, reproducibility checks, asset sizes) apply. Additional gate: verify thumbnail file sizes meet 90%+ reduction target. Verify WebP generation succeeds for all test images.

**Gate Status**: ✅ PASSED - All constitution requirements satisfied. No violations to justify.

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion (2025-11-02)*

1. ✅ **Static-first approach**: Design confirmed build-time processing only. No runtime server components. ThumbnailGenerator runs during `uv run exposure` build phase. Output is static HTML/CSS/JS + image files.

2. ✅ **Performance budget**: Design improves performance without increasing HTML/CSS/JS payload. Thumbnails reduce initial page load from 125MB to 15MB. HTML template changes minimal (<1KB). No new CSS/JS added.

3. ✅ **Accessibility**: Design maintains semantic HTML with `<picture>` elements. Alt text preserved from existing Image model. No JavaScript required for format selection (browser-native). Existing axe tests continue to validate accessibility.

4. ✅ **Content integrity**: Design includes content hashing (SHA-256) for thumbnail filenames. BuildCache tracks source mtimes for reproducibility. Same source + config = identical thumbnails. Cache stored in `build/.build-cache.json` (not tracked, regenerated).

5. ✅ **Security/privacy**: Design uses only local Pillow library. No external services or API calls. No third-party scripts. No tracking. All processing local to build machine. Existing CSP policy unaffected.

6. ✅ **Documentation**: Research.md, data-model.md, contracts/, and quickstart.md created. README update planned in implementation phase. ADR for image preprocessing approach will be added to `docs/decisions/008-image-preprocessing-approach.md`.

7. ✅ **CI gates**: Existing gates remain. Additional validations: thumbnail file size reduction test (verify 90%+ reduction), WebP format validation, incremental build cache test. Performance budget test updated to verify thumbnail serving improves load time.

**Final Gate Status**: ✅ PASSED - Design phase complete with full constitution compliance.

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
├── generator/
│   ├── __init__.py
│   ├── model.py           # Data models (Image, Category, GalleryConfig)
│   ├── scan.py            # Image discovery and validation
│   ├── build_html.py      # Main build orchestration
│   ├── assets.py          # Static asset copying
│   ├── i18n.py            # Internationalization
│   ├── yaml_sync.py       # YAML metadata sync
│   └── thumbnails.py      # NEW: Thumbnail generation module
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── index.html.j2      # MODIFIED: Serve thumbnails with WebP/fallback
    └── fullscreen.html.j2 # MODIFIED: Serve original full-res images

tests/
├── unit/
│   ├── test_model.py
│   ├── test_scan.py
│   ├── test_build_html.py
│   ├── test_i18n.py
│   ├── test_yaml_sync.py
│   └── test_thumbnails.py # NEW: Unit tests for thumbnail generation
├── integration/
│   ├── test_end_to_end.py # MODIFIED: Verify thumbnail generation in build
│   ├── test_asset_budgets.py
│   ├── test_fullscreen.py
│   └── test_reproducibility.py # MODIFIED: Verify thumbnail hashing
└── accessibility/
    └── test_axe_a11y.py

build/ (or dist/)          # Build output directory
├── images/
│   ├── originals/         # NEW: Original full-resolution images
│   └── thumbnails/        # NEW: Generated WebP + JPEG fallback thumbnails
├── index.html
├── gallery.*.css
└── gallery.*.js
```

**Structure Decision**: Single project structure (Option 1). This is a static site generator CLI tool written in Python. New `thumbnails.py` module handles image preprocessing. Existing modules modified to integrate thumbnail generation into build pipeline. Templates updated to serve thumbnails in gallery view and originals in modal view.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Constitution Check passed all requirements.
